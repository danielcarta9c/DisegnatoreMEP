"""Le misure della tavola dell'impianto 1, prima e dopo (DRAW-005).

Non fa parte del nucleo deterministico: e' lo strumento con cui si guarda il
lavoro, come `scripts/rasterize.sh`. Legge un modello gia' completato dalle
regole e una geometria agli atti, e stampa in JSON le misure che il pacchetto
chiede, piu' l'impronta della geometria. E' lo strumento di DRAW-004 con tre
misure in piu', che sono quelle del contenuto e non del solo instradamento:

- **i rami di ciascuna macchina**, letti sul grafo: per ogni attacco del
  flusso la fila dei pezzi in linea fino al primo che ferma, con gli organi
  di chiusura e i filtri che vi stanno (criterio 3: nessun organo fra il
  filtro e la macchina, un organo lato rete per ramo di ritorno,
  l'intercettazione di mandata);
- **la valvola oltre un raccordo passante** (I-035): chi isola un pezzo
  attraverso un raccordo che non apre il percorso si misura contro il
  raccordo, che e' l'attacco a cui si stringe;
- **il tubo per collegamento**: la lunghezza di ciascuna tubazione del
  modello di partenza (`p1`… `w2`), con quanti accessori in linea porta e
  quanto rettilineo minimo essi pretendono, e a parte il tubo degli stacchi.
  E' cio' che permette di dire quanto tubo viene dal contenuto nuovo e quanto
  dal layout, invece di confrontare due grafi che non sono lo stesso grafo.

Uso:
    python3 docs/collaudi/DRAW-005/metriche.py MODELLO.json [GEOMETRIA.json] [--diario]

Con la geometria, la tavola si legge invece di ricomporla, e il foglio si
riconosce dal formato ordinario piu' piccolo che la contiene: e' il modo di
rimisurare con lo strumento di oggi una tavola prodotta ieri, anche quando i
simboli di oggi non ammettono piu' una rotazione di ieri — in quel caso le
misure che passano dai simboli lo dicono, invece di fermare tutto. Con
`--diario` si rifa' da capo la posa e il ciclo di miglioramento per stampare
**il diario delle candidate provate** (DRAW-004, criterio 4).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from disegnatore_mep.catalog.registry import ComponentRegistry  # noqa: E402
from disegnatore_mep.catalog.schema import CLOSING_FUNCTIONS, ComponentTrait  # noqa: E402
from disegnatore_mep.graphics.frame import ORDINARY_FRAMES  # noqa: E402
from disegnatore_mep.graphics.symbol import SymbolError  # noqa: E402
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
from disegnatore_mep.layout.inline import (  # noqa: E402
    ISOLATING_FUNCTIONS,
    MIN_SPACING_MM,
)
from disegnatore_mep.layout.labels import (  # noqa: E402
    LINE_CLEARANCE_MM,
    segments_cross,
    text_width_mm,
)
from disegnatore_mep.layout.partition import partition_project  # noqa: E402
from disegnatore_mep.layout.trunks import build_trunks  # noqa: E402
from disegnatore_mep.model.project import PortRef  # noqa: E402
from disegnatore_mep.rules.context import RuleContext  # noqa: E402
from disegnatore_mep.validation.geometry import validate_drawing_geometry  # noqa: E402
from disegnatore_mep.validation.preflight import (  # noqa: E402
    _fill_ratio,
    _ink_area_mm2,
    _leader_enters,
    _quadrants,
    preflight_drawing,
)

TOLERANCE_MM = 1e-6

OF_INTEREST = frozenset({*CLOSING_FUNCTIONS, "filtration", "sludge_separation"})
"""Le funzioni che contano nel leggere un ramo: chi chiude, chi filtra."""


def _logical_pipe(connection_id: str) -> str:
    """La tubazione del modello di partenza da cui un troncone deriva.

    Le regole spezzano `p3` in `p3-a` e `p3-b`, e poi ancora — il modello di
    DRAW-002 numerava i tronconi (`p4-a-a-1-3`): il nome di partenza e' quello
    senza i suffissi. Uno stacco (`stub-…`) non deriva da nessuna tubazione:
    e' un collegamento nuovo."""
    import re

    return re.sub(r"(-(?:[ab]|\d+))+$", "", connection_id)


def _frame_for(drawing: DrawingGeometry) -> object:
    """Il formato ordinario piu' piccolo che contiene tutto l'inchiostro."""
    for frame in ORDINARY_FRAMES:
        area = frame.drawing_rect_mm
        inside = True
        for sheet in drawing.sheets:
            box = ink_box(sheet.symbols, sheet.routes)
            if box is None:
                continue
            if not (
                area.x_mm - TOLERANCE_MM <= box[0]
                and area.y_mm - TOLERANCE_MM <= box[1]
                and box[2] <= area.right_mm + TOLERANCE_MM
                and box[3] <= area.bottom_mm + TOLERANCE_MM
            ):
                inside = False
        if inside:
            return frame
    return ORDINARY_FRAMES[-1]

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
    if geometry_path is not None:
        drawing = DrawingGeometry.model_validate_json(
            geometry_path.read_text(encoding="utf-8")
        )
        frame = _frame_for(drawing)  # type: ignore[assignment]
    else:
        frame, drawing = compose_on_ordinary_frame(project, catalog)
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

        all_trunks = list(partition.trunks) if partition is not None else []

        def serviced_beyond(ref: PortRef) -> str | None:
            """Il pezzo manutenibile che sta oltre questo capo, attraverso i
            soli raccordi passanti (I-035): la stessa camminata del posatore."""
            seen: set[str] = set()
            cursor = ref
            while cursor.component_id not in seen:
                seen.add(cursor.component_id)
                definition = catalog.get(definitions[cursor.component_id])
                if definition.has_trait(ComponentTrait.MAINTAINABLE):
                    return cursor.component_id
                if not definition.is_a_fitting:
                    return None
                onward = [
                    port.id
                    for port in definition.ports
                    if not port.off_the_run and port.id != cursor.port_id
                ]
                if len(onward) != 1:
                    return None
                beyond = PortRef(component_id=cursor.component_id, port_id=onward[0])
                following = [
                    item for item in all_trunks if beyond in (item.start, item.end)
                ]
                if len(following) != 1:
                    return None
                cursor = (
                    following[0].end if following[0].start == beyond else following[0].start
                )
            return None

        for trunk in all_trunks:
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
                # I casi della regola, nell'ordine in cui il posatore li
                # applica: contro l'estremo di partenza, contro quello di
                # arrivo — direttamente o oltre un raccordo passante (I-035) —
                # e la coppia in fila con un apparecchio manutenibile che sta
                # anch'esso sulla tubazione. Da DRAW-005 un organo solo puo'
                # chiudere un tratto che ha un pezzo manutenibile a ciascun
                # capo: si riporta il caso del capo **piu' vicino**, che e'
                # quello a cui il posatore lo ha stretto.
                candidates: list[tuple[float, str, str]] = []
                if position == 0 and "start" in ends:
                    host_id, x_mm, y_mm = ends["start"]
                    if host_id in maintainable:
                        candidates.append(
                            (gap_between(me, (x_mm, y_mm, x_mm, y_mm)), "primo", host_id)
                        )
                    else:
                        beyond = serviced_beyond(trunk.start)
                        if beyond is not None:
                            candidates.append(
                                (
                                    gap_between(me, (x_mm, y_mm, x_mm, y_mm)),
                                    "primo oltre il raccordo",
                                    beyond,
                                )
                            )
                if position == len(members) - 1 and "end" in ends:
                    host_id, x_mm, y_mm = ends["end"]
                    if host_id in maintainable:
                        candidates.append(
                            (gap_between(me, (x_mm, y_mm, x_mm, y_mm)), "ultimo", host_id)
                        )
                    else:
                        beyond = serviced_beyond(trunk.end)
                        if beyond is not None:
                            candidates.append(
                                (
                                    gap_between(me, (x_mm, y_mm, x_mm, y_mm)),
                                    "ultimo oltre il raccordo",
                                    beyond,
                                )
                            )
                for neighbour in (position - 1, position + 1):
                    if not 0 <= neighbour < len(members):
                        continue
                    other_id = members[neighbour]
                    if other_id not in maintainable or other_id not in by_id:
                        continue
                    candidates.append(
                        (gap_between(me, box_of(by_id[other_id])), "coppia", other_id)
                    )
                if not candidates:
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
                distance, case, target = min(candidates, key=lambda item: (item[0], item[1]))
                gaps[component_id] = {
                    "caso": case,
                    "isola": target,
                    "distanza_mm": round(distance, 3),
                }

        # Il tubo per collegamento del modello di partenza (DRAW-005): quanto
        # ne porta ciascuna tubazione `p1`… `w2`, quanti accessori in linea vi
        # stanno e quanto rettilineo minimo pretendono — il riquadro di ciascuno
        # piu' il passo — e, a parte, il tubo degli stacchi, che sono
        # collegamenti nuovi. Cosi' un confronto fra due grafi diversi dice
        # quanto viene dal contenuto e quanto dal layout.
        per_pipe: dict[str, dict[str, float | int]] = {}
        stubs_mm = 0.0
        stubs = 0
        for trunk in all_trunks:
            route = by_key.get(tuple(trunk.connection_ids))
            if route is None:
                continue
            mm = sum(
                abs(after.x_mm - before.x_mm) + abs(after.y_mm - before.y_mm)
                for segment in route.segments
                for before, after in moves_of(segment)
            )
            base = _logical_pipe(trunk.connection_ids[0])
            if base.startswith("stub-"):
                stubs_mm += mm
                stubs += 1
                continue
            row = per_pipe.setdefault(
                base, {"mm": 0.0, "accessori_in_linea": 0, "rettilineo_minimo_mm": 0.0}
            )
            row["mm"] = float(row["mm"]) + mm
            row["accessori_in_linea"] = int(row["accessori_in_linea"]) + len(members := list(trunk.inline_component_ids))
            for component_id in members:
                placed_item = by_component.get(component_id)
                if placed_item is None:
                    continue
                horizontal = all(
                    abs(after.y_mm - before.y_mm) <= TOLERANCE_MM
                    for segment in route.segments
                    for before, after in moves_of(segment)
                )
                extent = placed_item.width_mm if horizontal else placed_item.height_mm
                row["rettilineo_minimo_mm"] = float(row["rettilineo_minimo_mm"]) + extent + MIN_SPACING_MM
        for row in per_pipe.values():
            row["mm"] = round(float(row["mm"]), 1)
            row["rettilineo_minimo_mm"] = round(float(row["rettilineo_minimo_mm"]), 1)

        # Le etichette (DRAW-004): quante, quante richiamate, e se qualcuna
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
                "tubo_per_collegamento": dict(sorted(per_pipe.items())),
                "tubo_su_collegamenti_di_partenza_mm": round(
                    sum(float(row["mm"]) for row in per_pipe.values()), 1
                ),
                "tubo_su_stacchi_mm": round(stubs_mm, 1),
                "stacchi": stubs,
                "simboli": len(sheet.symbols),
                "tratte": len(sheet.routes),
            }
        )

    # I rami di ciascuna macchina, letti sul grafo (DRAW-005, criterio 3). Per
    # ogni attacco del flusso di un pezzo manutenibile che non sta in linea, la
    # fila dei pezzi in linea fino al primo che ferma — un pezzo non in linea, o
    # un raccordo da cui il percorso si apre — con le funzioni che contano.
    context = RuleContext.build(project, catalog)

    def peer_of(connection_id: str, component_id: str) -> str | None:
        for (holder, _), item in context.connection_of_port.items():
            if item == connection_id and holder != component_id:
                return holder
        return None

    def branch(ref: PortRef) -> list[str]:
        found: list[str] = []
        cursor = ref.component_id
        connection_id = context.connection_of_port.get((cursor, ref.port_id))
        seen = {cursor}
        while connection_id is not None:
            peer = peer_of(connection_id, cursor)
            if peer is None or peer in seen or peer not in context.inline:
                break
            seen.add(peer)
            found.append(peer)
            onward = [
                item
                for item in (*context.incoming.get(peer, ()), *context.outgoing.get(peer, ()))
                if item != connection_id
            ]
            if len(onward) != 1:
                break
            connection_id = onward[0]
            cursor = peer
        return found

    branches: dict[str, dict[str, object]] = {}
    for item in project.components:
        if item.id in inline_ids or item.id not in maintainable:
            continue
        for port in context.connected_ports(item.id):
            fila = branch(PortRef(component_id=item.id, port_id=port.id))
            roles = {
                piece: sorted(set(catalog.get(definitions[piece]).functions) & OF_INTEREST)
                for piece in fila
            }
            filters = [index for index, piece in enumerate(fila) if "filtration" in roles[piece]]
            closers = [
                index for index, piece in enumerate(fila) if CLOSING_FUNCTIONS & set(roles[piece])
            ]
            branches[f"{item.id}.{port.id}"] = {
                "verso": port.flow.value,
                "fila": [f"{piece} [{', '.join(roles[piece])}]" if roles[piece] else piece for piece in fila],
                "filtri": len(filters),
                "organi_di_chiusura": len(closers),
                "organi_fra_filtro_e_macchina": sum(
                    1 for index in closers if filters and index < min(filters)
                ),
                "organi_consecutivi": sum(
                    1
                    for first, second in zip(closers, closers[1:], strict=False)
                    if second == first + 1
                ),
            }

    try:
        quality = preflight_drawing(drawing, frame, catalog)
        quality_rows = [f"{item.severity.value}:{item.code}:{item.message}" for item in quality]
    except SymbolError as exc:
        quality_rows = [f"non misurabile con i simboli di oggi: {exc}"]
    try:
        correctness = validate_drawing_geometry(drawing, frame)
        correctness_rows = [f"{item.code}:{item.message}" for item in correctness.issues]
    except SymbolError as exc:
        correctness_rows = [f"non misurabile con i simboli di oggi: {exc}"]
    return {
        "formato": f"{frame.standard.sheet_width_mm:g}x{frame.standard.sheet_height_mm:g}",
        "area_disegno_mm": [round(area.width_mm, 1), round(area.height_mm, 1)],
        "impronta": drawing_fingerprint(drawing),
        "fogli": sheets,
        "rami": branches,
        "rilievi_qualita": quality_rows,
        "rilievi_correttezza": correctness_rows,
    }


def diario(project_path: Path) -> dict[str, object]:
    """Il diario del ciclo di miglioramento, rifatto da capo sul modello.

    Due fasi (DRAW-004): la posa di DRAW-002 e la rifinitura da disegnatore.
    Per la seconda si elencano, pezzo per pezzo, le specie di candidate
    misurate — dorsale, asse, tee, porta, colonna, e le altre — con quante
    sono state provate, il costo migliore fra loro e quale e' stata accettata:
    e' la risposta a «quali alternative di asse sono state provate e perche'
    quella finale ha vinto».
    """
    from collections import Counter, defaultdict

    from disegnatore_mep.layout.improve import Improver
    from disegnatore_mep.layout.partition import partition_project
    from disegnatore_mep.layout.place import place_sheet
    from disegnatore_mep.layout.trunks import build_trunks

    symbols = SymbolRegistry.from_directory(ROOT / "assets" / "symbols")
    catalog = ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog", symbols=symbols
    )
    project = load_project(project_path)
    inline = inline_component_ids(project, catalog)
    partition = partition_project(project, build_trunks(project, inline))[0]
    frame, _ = compose_on_ordinary_frame(project, catalog)
    placed = place_sheet(project, partition, catalog, frame, inline)
    improver = Improver(project, partition, catalog, frame, placed, inline)
    start = improver.measure(improver.best)
    improver.run()
    end = improver.measure(improver.best)

    names = (
        "violazioni", "tratte_con_backtracking", "backtracking_mm", "tratte_oltre_tre_pieghe",
        "pieghe", "incroci", "lunghezza_mm", "riempimento_negato", "squilibrio",
    )

    def named(key: tuple[object, ...] | None) -> dict[str, object] | None:
        return None if key is None else dict(zip(names[:7], key[:7], strict=False))

    placement = [entry for entry in improver.journal if entry.phase == "posa"]
    refinement = [entry for entry in improver.journal if entry.phase == "rifinitura"]
    settled = [entry for entry in placement if entry.accepted]

    per_piece: dict[str, dict[str, dict[str, object]]] = defaultdict(dict)
    for entry in refinement:
        row = per_piece[entry.leader].setdefault(
            entry.kind, {"provate": 0, "instradabili": 0, "migliore": None, "accettate": 0}
        )
        row["provate"] = int(row["provate"]) + 1
        if entry.cost is not None:
            row["instradabili"] = int(row["instradabili"]) + 1
            best = row["migliore"]
            if best is None or entry.cost < tuple(best):  # type: ignore[arg-type]
                row["migliore"] = list(entry.cost)
        if entry.accepted:
            row["accettate"] = int(row["accettate"]) + 1

    return {
        "costo_iniziale": named(None if start is None else start.cost.key()),
        "prove_posa": improver.trials - improver.axis_trials,
        "prove_rifinitura": improver.axis_trials,
        "costo_dopo_la_posa": named(settled[-1].cost)
        if settled
        else named(None if start is None else start.cost.key()),
        "costo_finale": named(None if end is None else end.cost.key()),
        "posa_specie_provate": dict(Counter(entry.kind for entry in placement)),
        "posa_accettate": [
            {"specie": entry.kind, "pezzo": entry.leader, "costo": named(entry.cost)}
            for entry in placement
            if entry.accepted
        ],
        "rifinitura_specie_provate": dict(Counter(entry.kind for entry in refinement)),
        "rifinitura_accettate": [
            {"specie": entry.kind, "pezzo": entry.leader, "costo": named(entry.cost)}
            for entry in refinement
            if entry.accepted
        ],
        "rifinitura_per_pezzo": {
            leader: {
                kind: {**row, "migliore": named(tuple(row["migliore"])) if row["migliore"] else None}  # type: ignore[arg-type]
                for kind, row in kinds.items()
            }
            for leader, kinds in per_piece.items()
        },
        "posa_finale": [
            {
                "pezzo": item.component_id,
                "x_mm": item.origin.x_mm,
                "y_mm": item.origin.y_mm,
                "rotazione": item.rotation_deg,
                "attacchi": item.port_map,
            }
            for item in improver.best.values()
        ],
    }


if __name__ == "__main__":
    arguments = [item for item in sys.argv[1:] if not item.startswith("--")]
    given = Path(arguments[1]) if len(arguments) > 1 else None
    if "--diario" in sys.argv:
        print(json.dumps(diario(Path(arguments[0])), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(measure(Path(arguments[0]), given), ensure_ascii=False, indent=2))
