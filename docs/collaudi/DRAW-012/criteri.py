"""I criteri di DRAW-012, misurati uno per uno sul motore corrente.

Non fa parte del nucleo deterministico: e' lo strumento con cui il DEV chiude il
rapporto e con cui il PM lo rilegge, come `docs/collaudi/DRAW-002/metriche.py`.
Ogni voce che stampa risponde a un criterio del pacchetto, e lo dice.

Uso:
    .venv/bin/python docs/collaudi/DRAW-012/criteri.py                 # tutti e cinque
    .venv/bin/python docs/collaudi/DRAW-012/criteri.py MODELLO.json    # uno solo

Con un modello **completato dalle regole** (`prova-N-completo.json`) si misura
la tavola vera; con un grafo di prima stesura si misura la sola classificazione,
che non dipende dal corredo.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from disegnatore_mep.catalog.registry import ComponentRegistry  # noqa: E402
from disegnatore_mep.graphics.registry import SymbolRegistry  # noqa: E402
from disegnatore_mep.io.project_json import load_project  # noqa: E402
from disegnatore_mep.layout.compose import (  # noqa: E402
    ComposeJournal,
    compose_on_ordinary_frame,
    inline_component_ids,
)
from disegnatore_mep.layout.errors import LayoutError  # noqa: E402
from disegnatore_mep.layout.geometry import (  # noqa: E402
    drawing_fingerprint,
    fill_ratio,
    ink_box,
    ink_coverage,
)
from disegnatore_mep.layout.hierarchy import (  # noqa: E402
    Level,
    hierarchy_of,
    spine_machines,
    user_machines,
)
from disegnatore_mep.layout.highways import highways  # noqa: E402
from disegnatore_mep.layout.trunks import build_trunks  # noqa: E402

PROVE = ROOT / "examples" / "prova"


def _catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog",
        symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols"),
    )


def measure(path: Path) -> dict[str, object]:
    catalog = _catalog()
    project = load_project(path)
    runs = build_trunks(project, inline_component_ids(project, catalog))
    levels = hierarchy_of(project, catalog, runs)
    catene = highways(project, catalog, runs)

    found: dict[str, object] = {
        "modello": path.name,
        # §B — che cosa e' autostrada, e chi lo decide
        "macchine_di_spina": sorted(spine_machines(project, catalog)),
        "utenze": sorted(user_machines(project, catalog)),
        "tratte": {
            f"{item.start.component_id}.{item.start.port_id}"
            f" -> {item.end.component_id}.{item.end.port_id}": levels[
                item.connection_ids
            ].name
            for item in runs
        },
        # §C — l'autostrada intera
        "autostrade_intere": [
            {
                "tratte": [list(key) for key in item.keys],
                "percorso": " · ".join(
                    f"{entry.component_id}.{entry.port_id}"
                    f"→{exit_.component_id}.{exit_.port_id}"
                    for entry, exit_ in item.steps
                ),
            }
            for item in catene
        ],
    }

    started = time.time()
    journal = ComposeJournal()
    try:
        frame, drawing = compose_on_ordinary_frame(project, catalog, journal=journal)
    except LayoutError as exc:
        found["tavola"] = f"non esce: {exc}"
        found["secondi"] = round(time.time() - started, 1)
        return found

    area = frame.drawing_rect_mm
    rect = (area.x_mm, area.y_mm, area.right_mm, area.bottom_mm)
    fogli: list[dict[str, object]] = []
    for sheet, note in zip(drawing.sheets, journal.notes, strict=False):
        box = ink_box(sheet.symbols, sheet.routes)
        fogli.append(
            {
                "foglio": sheet.sheet_id,
                # §D — i tre numeri che D-141 vuole letti insieme
                "riempimento_pct": round(
                    fill_ratio(sheet.symbols, sheet.routes, rect) * 100, 1
                ),
                "copertura_ingombro": round(
                    ink_coverage(sheet.symbols, sheet.routes, box), 3
                ),
                "curve": sum(
                    max(len(segment) - 2, 0)
                    for route in sheet.routes
                    for segment in route.segments
                ),
                "attraversamenti": sum(len(route.crossings) for route in sheet.routes),
                "ingombro_mm": [round(value, 1) for value in (box or (0, 0, 0, 0))],
                # §F — con quale via e' uscita, e che cosa ha ceduto
                "ripiego": note.ripiego,
                "autostrade_intere": note.highways,
                "tratte_cedute": [list(key) for key in note.conceded],
                "catene_storte": [list(key) for key in note.crooked],
            }
        )
    found["formato"] = f"{frame.standard.sheet_width_mm:g}x{frame.standard.sheet_height_mm:g}"
    found["fogli"] = fogli
    found["impronta"] = drawing_fingerprint(drawing)
    found["secondi"] = round(time.time() - started, 1)
    return found


def _sunto(found: dict[str, object]) -> str:
    """Una riga per impianto: cio' che il rapporto porta in tabella."""
    levels = found.get("tratte", {})
    assert isinstance(levels, dict)
    autostrade = sum(1 for value in levels.values() if value == Level.AUTOSTRADA.name)
    head = (
        f"{found['modello']}: {autostrade}/{len(levels)} tratte autostrada, "
        f"{len(found.get('autostrade_intere', []))} catene"  # type: ignore[arg-type]
    )
    fogli = found.get("fogli")
    if not isinstance(fogli, list):
        return f"{head} — {found.get('tavola')}"
    parts = [
        f"riemp {item['riempimento_pct']}% · cop {item['copertura_ingombro']} · "
        f"curve {item['curve']} · attrav {item['attraversamenti']} · "
        f"ripiego «{item['ripiego']}» · cedute {len(item['tratte_cedute'])}"  # type: ignore[arg-type]
        for item in fogli
    ]
    return head + " — " + " | ".join(parts)


def main() -> None:
    paths = (
        [Path(item) for item in sys.argv[1:]]
        if len(sys.argv) > 1
        else sorted(PROVE.glob("prova-*.json"))
    )
    found = [measure(path) for path in paths]
    print(json.dumps(found, ensure_ascii=False, indent=2))
    print("\n--- sunto ---", file=sys.stderr)
    for item in found:
        print(_sunto(item), file=sys.stderr)


if __name__ == "__main__":
    main()
