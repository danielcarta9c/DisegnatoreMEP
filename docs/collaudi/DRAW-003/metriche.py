"""Le misure della tavola dell'impianto 1, prima e dopo (DRAW-003).

Non fa parte del nucleo deterministico: e' lo strumento con cui si guarda il
lavoro, come `scripts/rasterize.sh`. Legge un modello gia' completato dalle
regole, ricompone la tavola con la catena corrente e stampa in JSON le
misure che il pacchetto chiede, piu' l'impronta della geometria.

Uso:
    .venv/bin/python docs/collaudi/DRAW-003/metriche.py MODELLO.json [GEOMETRIA.json]

Con la geometria, la tavola si legge invece di ricomporla: e' il modo di
rimisurare con lo strumento di oggi una tavola prodotta ieri.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from disegnatore_mep.catalog.registry import ComponentRegistry  # noqa: E402
from disegnatore_mep.catalog.schema import ComponentTrait  # noqa: E402
from disegnatore_mep.graphics.registry import SymbolRegistry  # noqa: E402
from disegnatore_mep.io.project_json import load_project  # noqa: E402
from disegnatore_mep.layout.compose import (  # noqa: E402
    compose_on_ordinary_frame,
    inline_component_ids,
)
from disegnatore_mep.layout.geometry import (  # noqa: E402
    DrawingGeometry,
    Point,
    box_of,
    drawing_fingerprint,
    fill_ratio,
    ink_box,
    ink_coverage,
    intrudes_into,
    moves_of,
    overshoot_mm,
)
from disegnatore_mep.layout.improve import overshoot_beyond_goal_mm  # noqa: E402
from disegnatore_mep.layout.inline import ISOLATING_FUNCTIONS  # noqa: E402
from disegnatore_mep.layout.labels import (  # noqa: E402
    LINE_CLEARANCE_MM,
    segments_cross,
    text_width_mm,
)
from disegnatore_mep.layout.partition import partition_project  # noqa: E402
from disegnatore_mep.layout.trunks import build_trunks  # noqa: E402
from disegnatore_mep.validation.geometry import validate_drawing_geometry  # noqa: E402
from disegnatore_mep.validation.preflight import (  # noqa: E402
    _fill_ratio,
    _ink_area_mm2,
    _leader_enters,
    _quadrants,
    preflight_drawing,
)

TOLERANCE_MM = 1e-6

def _fill_without_the_loneliest(sheet: object, area: object) -> float:
    """Il riempimento tolto il pezzo piu' lontano dal resto dell'inchiostro.

    E' la misura che smaschera una **propaggine**: se togliendo un simbolo solo
    — e la tratta che lo raggiunge — il riempimento crolla, quel numero non era
    del disegno, era di quel pezzo. Il collaudo indipendente l'ha usata per
    respingere due consegne, e da allora sta qui accanto all'altra.
    """
    symbols = list(sheet.symbols)  # type: ignore[attr-defined]
    routes = list(sheet.routes)  # type: ignore[attr-defined]
    rect = (area.x_mm, area.y_mm, area.right_mm, area.bottom_mm)  # type: ignore[attr-defined]
    base = fill_ratio(symbols, routes, rect)
    worst = base
    for index, symbol in enumerate(symbols):
        kept = symbols[:index] + symbols[index + 1 :]
        # Anche la tratta che lo raggiunge se ne va: un pezzo isolato porta con
        # se' il proprio stelo, ed e' lo stelo a disegnare il vuoto.
        box = (symbol.origin.x_mm, symbol.origin.y_mm, symbol.right_mm, symbol.bottom_mm)
        others = [
            route
            for route in routes
            if not any(
                box[0] - 5.0 <= point.x_mm <= box[2] + 5.0
                and box[1] - 5.0 <= point.y_mm <= box[3] + 5.0
                for segment in route.segments
                for point in segment
            )
        ]
        worst = min(worst, fill_ratio(kept, others, rect))
    return worst


def measure(
    project_path: Path, geometry_path: Path | None = None
) -> dict[str, object]:
    """Le misure della tavola di questo modello.

    Con `geometry_path` la geometria si **legge** invece di ricomporla: serve a
    rimisurare una tavola gia' agli atti con lo strumento di oggi, cosi' che le
    due colonne di un confronto siano calcolate con la stessa definizione. Senza,
    la tavola si ricompone dalla catena corrente.
    """
    symbols = SymbolRegistry.from_directory(ROOT / "assets" / "symbols")
    catalog = ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog", symbols=symbols
    )
    project = load_project(project_path)
    frame, drawing = compose_on_ordinary_frame(project, catalog)
    if geometry_path is not None:
        drawing = DrawingGeometry.model_validate_json(
            geometry_path.read_text(encoding="utf-8")
        )
    area = frame.drawing_rect_mm
    line_mm = frame.standard.line_medium_mm

    inline_ids = inline_component_ids(project, catalog)
    # Chi isola si riconosce con **la stessa definizione della regola**: se la
    # misura e la regola non concordano su chi sia una valvola, il numero che
    # certifica la regola non certifica niente.
    isolators = {
        item.id
        for item in project.components
        if ISOLATING_FUNCTIONS
        & set(catalog.resolve(item.definition_id).definition.functions)
    }
    definitions = {item.id: item.definition_id for item in project.components}
    maintainable = {
        item.id
        for item in project.components
        if catalog.resolve(item.definition_id).definition.has_trait(
            ComponentTrait.MAINTAINABLE
        )
    }
    partitions = {
        item.sheet_id: item
        for item in partition_project(project, build_trunks(project, inline_ids))
    }

    sheets: list[dict[str, object]] = []
    for sheet in drawing.sheets:
        ink = [
            _ink_area_mm2(sheet, quadrant, line_mm) for quadrant in _quadrants(area)
        ]
        bends = 0
        long_runs = 0
        length_mm = 0.0
        crossings = 0
        # L'andata e ritorno, con le due misure che il ciclo di posa conta
        # (DRAW-002): il giro attorno alla porta di arrivo e il ritorno della
        # spezzata su se stessa. Tratte e millimetri complessivi.
        by_key = {tuple(route.connection_ids): route for route in sheet.routes}
        by_component = {item.component_id: item for item in sheet.symbols}
        turnback_runs = 0
        turnback_mm = 0.0
        step_mm = frame.standard.grid_mm
        partition = partitions.get(sheet.sheet_id)
        for trunk in partition.trunks if partition is not None else []:
            route = by_key.get(tuple(trunk.connection_ids))
            arrival = by_component.get(trunk.end.component_id)
            if route is None or arrival is None:
                continue
            port = catalog.resolve(
                definitions[trunk.end.component_id]
            ).symbol.manifest.rotated(arrival.rotation_deg).port(trunk.end.port_id)
            goal = Point(
                x_mm=arrival.origin.x_mm + port.x_mm, y_mm=arrival.origin.y_mm + port.y_mm
            )
            back = max(
                overshoot_beyond_goal_mm(route, goal),
                max((overshoot_mm(segment, step_mm) for segment in route.segments), default=0.0),
            )
            if back > TOLERANCE_MM:
                turnback_runs += 1
                turnback_mm += back
        for route in sheet.routes:
            turns = 0
            for segment in route.segments:
                turns += max(len(segment) - 2, 0)
                for before, after in moves_of(segment):
                    length_mm += abs(after.x_mm - before.x_mm) + abs(
                        after.y_mm - before.y_mm
                    )
            bends += turns
            if turns > 3:
                long_runs += 1
            crossings += len(route.crossings)

        # Tubo dentro il corpo di un simbolo, **senza nessuna esenzione**: la
        # stessa misura del cancello di correttezza, che conta l'attraversamento
        # e il tratto che corre a filo dentro il riquadro. Chi termina su un
        # attacco non compare per costruzione — una porta sta sul perimetro — e
        # non serve saltarne la spezzata: saltarla reintrodurrebbe proprio
        # l'esenzione che era meta' del difetto.
        under: list[str] = []
        for symbol in sheet.symbols:
            box = box_of(symbol)
            for route in sheet.routes:
                for segment in route.segments:
                    if any(
                        intrudes_into(box, before, after)
                        for before, after in moves_of(segment)
                    ):
                        under.append(f"{symbol.component_id}<-{route.connection_ids}")

        # Quanto dista chi isola da cio' che isola (D-120), e per quale dei
        # tre casi della regola: il primo accessorio contro l'estremo di
        # partenza, l'ultimo contro quello di arrivo, la coppia in fila con un
        # apparecchio che sta esso stesso sulla tubazione. Chi non ricade in
        # nessuno dei tre non e' interessato dalla regola e si riporta a parte.
        gaps: dict[str, dict[str, object]] = {}
        by_id = {item.component_id: item for item in sheet.symbols}

        def gap_between(
            first: tuple[float, float, float, float],
            second: tuple[float, float, float, float],
        ) -> float:
            gap_x = max(first[0] - second[2], second[0] - first[2], 0.0)
            gap_y = max(first[1] - second[3], second[1] - first[3], 0.0)
            return (gap_x**2 + gap_y**2) ** 0.5

        for trunk in partition.trunks if partition is not None else []:
            members = list(trunk.inline_component_ids)
            ends = {}
            for side, ref in (("start", trunk.start), ("end", trunk.end)):
                host = by_id.get(ref.component_id)
                if host is None:
                    continue
                manifest = catalog.resolve(
                    definitions[ref.component_id]
                ).symbol.manifest.rotated(host.rotation_deg)
                port = manifest.port(ref.port_id)
                ends[side] = (
                    ref.component_id,
                    host.origin.x_mm + port.x_mm,
                    host.origin.y_mm + port.y_mm,
                )
            for position, component_id in enumerate(members):
                if component_id not in isolators or component_id not in by_id:
                    continue
                me = box_of(by_id[component_id])
                case = None
                distance = None
                target = None
                # I tre casi della regola, nell'ordine in cui il posatore li
                # applica: contro l'estremo di partenza, contro quello di
                # arrivo, e infine la coppia in fila con un apparecchio
                # manutenibile che sta anch'esso sulla tubazione.
                if position == 0 and "start" in ends:
                    host_id, x_mm, y_mm = ends["start"]
                    if host_id in maintainable:
                        case, target = "primo", host_id
                        distance = gap_between(me, (x_mm, y_mm, x_mm, y_mm))
                if case is None and position == len(members) - 1 and "end" in ends:
                    host_id, x_mm, y_mm = ends["end"]
                    if host_id in maintainable:
                        case, target = "ultimo", host_id
                        distance = gap_between(me, (x_mm, y_mm, x_mm, y_mm))
                if case is None:
                    for neighbour in (position - 1, position + 1):
                        if not 0 <= neighbour < len(members):
                            continue
                        other_id = members[neighbour]
                        if other_id not in maintainable or other_id not in by_id:
                            continue
                        case, target = "coppia", other_id
                        distance = gap_between(me, box_of(by_id[other_id]))
                        break
                if case is None:
                    nearest = min(
                        (
                            gap_between(me, (x_mm, y_mm, x_mm, y_mm))
                            for _, x_mm, y_mm in ends.values()
                        ),
                        default=None,
                    )
                    gaps[component_id] = {
                        "caso": "fuori regola",
                        "distanza_mm": None if nearest is None else round(nearest, 3),
                    }
                    continue
                gaps[component_id] = {
                    "caso": case,
                    "isola": target,
                    "distanza_mm": round(distance or 0.0, 3),
                }

        # Le etichette (DRAW-003): quante, quante richiamate, e se qualcuna
        # copre un tubo, un simbolo o un'altra scritta; i richiami che
        # attraversano tubi, simboli o altri richiami.
        height = frame.standard.text_small_mm
        text_boxes: list[tuple[float, float, float, float]] = []
        stretches = [
            (
                min(a.x_mm, b.x_mm) - LINE_CLEARANCE_MM,
                min(a.y_mm, b.y_mm) - LINE_CLEARANCE_MM,
                max(a.x_mm, b.x_mm) + LINE_CLEARANCE_MM,
                max(a.y_mm, b.y_mm) + LINE_CLEARANCE_MM,
            )
            for route in sheet.routes
            for segment in route.segments
            for a, b in moves_of(segment)
        ]
        segments = [
            (a, b)
            for route in sheet.routes
            for segment in route.segments
            for a, b in moves_of(segment)
        ]

        def overlaps(one: tuple[float, float, float, float], two: tuple[float, float, float, float]) -> bool:
            return one[0] < two[2] - TOLERANCE_MM and two[0] < one[2] - TOLERANCE_MM and one[1] < two[3] - TOLERANCE_MM and two[1] < one[3] - TOLERANCE_MM

        label_on_run = label_on_symbol = label_on_label = 0
        leaders = [(item.leader_from, item.anchor) for item in sheet.labels if item.leader_from is not None]
        leader_on_run = sum(1 for lead in leaders if any(segments_cross(lead, seg) for seg in segments))
        leader_on_symbol = sum(
            1
            for lead in leaders
            if any(_leader_enters(lead, box_of(symbol)) for symbol in sheet.symbols)
        )
        leaders_crossing = sum(
            1
            for i, lead in enumerate(leaders)
            for other in leaders[i + 1 :]
            if segments_cross(lead, other)
        )
        for item in sheet.labels:
            box = (item.anchor.x_mm, item.anchor.y_mm - height, item.anchor.x_mm + text_width_mm(item.text, height), item.anchor.y_mm)
            if any(overlaps(box, other) for other in stretches):
                label_on_run += 1
            if any(overlaps(box, box_of(symbol)) for symbol in sheet.symbols):
                label_on_symbol += 1
            if any(overlaps(box, other) for other in text_boxes):
                label_on_label += 1
            text_boxes.append(box)

        sheets.append(
            {
                "sheet_id": sheet.sheet_id,
                "linea_di_terra_esportata": sheet.ground_line_y_mm is not None,
                "etichette": len(sheet.labels),
                "sigle": sum(1 for item in sheet.labels if item.role == "tag"),
                "sigle_omesse": sum(
                    1
                    for symbol in sheet.symbols
                    if symbol.tag
                    and f"{symbol.component_id}-tag" not in {item.id for item in sheet.labels}
                ),
                "indirizzi": sum(1 for item in sheet.labels if item.role == "address"),
                "etichette_con_richiamo": len(leaders),
                "etichette_su_tubo": label_on_run,
                "etichette_su_simbolo": label_on_symbol,
                "etichette_su_etichetta": label_on_label,
                "richiami_su_tubo": leader_on_run,
                "richiami_su_simbolo": leader_on_symbol,
                "richiami_incrociati": leaders_crossing,
                "ingombro_mm": [
                    round(item, 1)
                    for item in (ink_box(sheet.symbols, sheet.routes) or (0, 0, 0, 0))
                ],
                "riempimento_pct": round(_fill_ratio(sheet, area) * 100, 1),
                "riempimento_senza_il_piu_isolato_pct": round(
                    _fill_without_the_loneliest(sheet, area) * 100, 1
                ),
                "copertura_ingombro": round(
                    ink_coverage(sheet.symbols, sheet.routes, ink_box(sheet.symbols, sheet.routes)),
                    3,
                ),
                "quadranti_rapporto": (
                    round(max(ink) / min(ink), 2) if min(ink) > TOLERANCE_MM else None
                ),
                "quadranti_mm2": [round(item, 1) for item in ink],
                "backtracking_tratte": turnback_runs,
                "backtracking_mm": round(turnback_mm, 1),
                "incroci": crossings,
                "pieghe_totali": bends,
                "tratte_oltre_tre_pieghe": long_runs,
                "lunghezza_totale_mm": round(length_mm, 1),
                "tubo_sotto_simbolo": sorted(set(under)),
                "valvole_d120": gaps,
                # Le valvole che la regola governa — chi isola un pezzo
                # manutenibile, nei tre casi di D-120 — e quante stanno a
                # 2,5-5 mm dall'attacco. Le altre sono «fuori regola» e si
                # riportano a parte, con la loro distanza.
                "valvole_d120_entro_2_5_5_mm": sum(
                    1
                    for item in gaps.values()
                    if item.get("caso") != "fuori regola"
                    and item.get("distanza_mm") is not None
                    and 2.5 - TOLERANCE_MM <= float(str(item["distanza_mm"])) <= 5.0 + TOLERANCE_MM
                ),
                "valvole_d120_totali": sum(
                    1 for item in gaps.values() if item.get("caso") != "fuori regola"
                ),
                "simboli": len(sheet.symbols),
                "tratte": len(sheet.routes),
            }
        )

    quality = preflight_drawing(drawing, frame, catalog)
    correctness = validate_drawing_geometry(drawing, frame)
    return {
        "formato": f"{frame.standard.sheet_width_mm:g}x{frame.standard.sheet_height_mm:g}",
        "area_disegno_mm": [round(area.width_mm, 1), round(area.height_mm, 1)],
        "impronta": drawing_fingerprint(drawing),
        "fogli": sheets,
        "rilievi_qualita": [
            f"{item.severity.value}:{item.code}:{item.message}" for item in quality
        ],
        "rilievi_correttezza": [
            f"{item.code}:{item.message}" for item in correctness.issues
        ],
    }


if __name__ == "__main__":
    given = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    print(json.dumps(measure(Path(sys.argv[1]), given), ensure_ascii=False, indent=2))
