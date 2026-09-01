"""Le misure della tavola dell'impianto 1, prima e dopo (DRAW-001).

Non fa parte del nucleo deterministico: e' lo strumento con cui si guarda il
lavoro, come `scripts/rasterize.sh`. Legge un modello gia' completato dalle
regole, ricompone la tavola con la catena corrente e stampa in JSON le sette
misure che il pacchetto chiede, piu' l'impronta della geometria.

Uso:
    .venv/bin/python docs/collaudi/DRAW-001/metriche.py MODELLO.json > metriche.json
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
from disegnatore_mep.layout.compose import compose_on_ordinary_frame  # noqa: E402
from disegnatore_mep.layout.geometry import (  # noqa: E402
    box_of,
    ink_box,
    drawing_fingerprint,
    moves_of,
)
from disegnatore_mep.validation.geometry import validate_drawing_geometry  # noqa: E402
from disegnatore_mep.layout.partition import partition_project  # noqa: E402
from disegnatore_mep.layout.trunks import build_trunks  # noqa: E402
from disegnatore_mep.layout.compose import inline_component_ids  # noqa: E402
from disegnatore_mep.validation.preflight import (  # noqa: E402
    _fill_ratio,
    _ink_area_mm2,
    _quadrants,
    preflight_drawing,
)

TOLERANCE_MM = 1e-6


def _crosses_body(
    before: object, after: object, box: tuple[float, float, float, float]
) -> bool:
    """Vero se il tratto condivide superficie con il riquadro pieno del simbolo.

    E' la misura del criterio 1 del pacchetto, e non quella storica: un tratto
    **interamente** dentro il riquadro e' solo il caso estremo di attraversarlo.
    """
    left, top, right, bottom = box
    x_low, x_high = min(before.x_mm, after.x_mm), max(before.x_mm, after.x_mm)  # type: ignore[attr-defined]
    y_low, y_high = min(before.y_mm, after.y_mm), max(before.y_mm, after.y_mm)  # type: ignore[attr-defined]
    return (
        x_low < right - TOLERANCE_MM
        and left < x_high - TOLERANCE_MM
        and y_low < bottom - TOLERANCE_MM
        and top < y_high - TOLERANCE_MM
    )


def measure(project_path: Path) -> dict[str, object]:
    symbols = SymbolRegistry.from_directory(ROOT / "assets" / "symbols")
    catalog = ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog", symbols=symbols
    )
    project = load_project(project_path)
    frame, drawing = compose_on_ordinary_frame(project, catalog)
    area = frame.drawing_rect_mm
    line_mm = frame.standard.line_medium_mm

    inline_ids = inline_component_ids(project, catalog)
    isolators = {
        item.id
        for item in project.components
        if "isolation" in catalog.resolve(item.definition_id).definition.functions
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

        # Tubo dentro il corpo di un simbolo, contando anche l'attraversamento
        # parziale: il tratto che finisce su un attacco non conta, e si
        # riconosce dal capo della spezzata che cade sul riquadro.
        under: list[str] = []
        for symbol in sheet.symbols:
            box = box_of(symbol)
            for route in sheet.routes:
                for segment in route.segments:
                    ends_here = any(
                        box[0] - TOLERANCE_MM <= point.x_mm <= box[2] + TOLERANCE_MM
                        and box[1] - TOLERANCE_MM <= point.y_mm <= box[3] + TOLERANCE_MM
                        for point in (segment[0], segment[-1])
                    )
                    if ends_here:
                        continue
                    if any(
                        _crosses_body(before, after, box)
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
        partition = partitions.get(sheet.sheet_id)

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

        sheets.append(
            {
                "sheet_id": sheet.sheet_id,
                "ingombro_mm": [
                    round(item, 1)
                    for item in (ink_box(sheet.symbols, sheet.routes) or (0, 0, 0, 0))
                ],
                "riempimento_pct": round(_fill_ratio(sheet, area) * 100, 1),
                "quadranti_rapporto": (
                    round(max(ink) / min(ink), 2) if min(ink) > TOLERANCE_MM else None
                ),
                "quadranti_mm2": [round(item, 1) for item in ink],
                "incroci": crossings,
                "pieghe_totali": bends,
                "tratte_oltre_tre_pieghe": long_runs,
                "lunghezza_totale_mm": round(length_mm, 1),
                "tubo_sotto_simbolo": sorted(set(under)),
                "valvole_d120": gaps,
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
    print(json.dumps(measure(Path(sys.argv[1])), ensure_ascii=False, indent=2))
