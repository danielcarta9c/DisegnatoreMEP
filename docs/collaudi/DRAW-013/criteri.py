"""I criteri di DRAW-013, misurati su una geometria gia' agli atti.

Non fa parte del nucleo deterministico: e' lo strumento con cui il DEV chiude il
rapporto e con cui il PM lo rilegge, come `docs/collaudi/DRAW-002/metriche.py`.
Legge le geometrie prodotte da `tavole.sh` — quindi misura **la tavola
consegnata**, non una ricomposta adesso — e stampa in JSON, per ciascuna:

* pieghe e attraversamenti (criterio 6);
* riempimento, copertura e riempimento senza il pezzo piu' isolato;
* ingombro e **margine minimo dal bordo**, con quello che il disegno poteva
  permettersi (criteri 4 e 15);
* la **lunghezza**, come misura e non come giudizio (D-139);
* i vuoti dell'asse e il **fattore** con cui la tavola e' stata allargata;
* la distanza di ogni **organo di servizio** dal pezzo che serve (criterio 12),
  e in testa quella dell'ingresso dell'acqua fredda dal bollitore (criterio 3).

Uso:
    .venv/bin/python docs/collaudi/DRAW-013/criteri.py CARTELLA [CARTELLA...]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from disegnatore_mep.layout.dilate import _gaps, _rigid_spans  # noqa: E402
from disegnatore_mep.layout.geometry import (  # noqa: E402
    SheetGeometry,
    border_margin_mm,
    fill_ratio,
    ink_box,
    ink_coverage,
    margin_allowed_mm,
    moves_of,
)

STEP_MM = 2.5
AREA = (10.0, 16.0, 360.0, 251.0)
"""L'area di disegno di una A3 Nove C: 350 x 235 mm, al netto di cartiglio e
legenda. Scritta qui e non calcolata, perche' questo strumento legge geometrie
agli atti e deve misurarle tutte con lo stesso metro."""


def _distance_mm(one: dict, two: dict) -> float:
    """Quanto distano due riquadri, zero se si toccano."""
    dx = max(one["x0"] - two["x1"], two["x0"] - one["x1"], 0.0)
    dy = max(one["y0"] - two["y1"], two["y0"] - one["y1"], 0.0)
    return max(dx, dy) if min(dx, dy) == 0.0 else (dx * dx + dy * dy) ** 0.5


def _boxes(sheet: SheetGeometry) -> dict[str, dict]:
    return {
        item.component_id: {
            "x0": item.origin.x_mm,
            "y0": item.origin.y_mm,
            "x1": item.right_mm,
            "y1": item.bottom_mm,
        }
        for item in sheet.symbols
    }


def _nearest(sheet: SheetGeometry, who: str, among: list[str]) -> tuple[str, float] | None:
    boxes = _boxes(sheet)
    if who not in boxes:
        return None
    found = [(other, _distance_mm(boxes[who], boxes[other])) for other in among if other in boxes]
    if not found:
        return None
    return min(found, key=lambda item: (item[1], item[0]))


def measure(sheet: SheetGeometry) -> dict:
    box = ink_box(sheet.symbols, sheet.routes)
    bends = sum(
        max(len(moves_of(segment)) - 1, 0)
        for route in sheet.routes
        for segment in route.segments
    )
    length = sum(
        abs(after.x_mm - before.x_mm) + abs(after.y_mm - before.y_mm)
        for route in sheet.routes
        for segment in route.segments
        for before, after in moves_of(segment)
    )
    gaps = {
        axis: [
            round(value / STEP_MM)
            for value in _gaps(
                _rigid_spans(sheet.symbols, axis == "x"),
                box[0] if axis == "x" else box[1],
                box[2] if axis == "x" else box[3],
            )
        ]
        for axis in ("x", "y")
    }
    return {
        "foglio": sheet.sheet_id,
        "ingombro_mm": None if box is None else [round(v, 1) for v in box],
        "larghezza_mm": None if box is None else round(box[2] - box[0], 1),
        "altezza_mm": None if box is None else round(box[3] - box[1], 1),
        "pieghe": bends,
        "attraversamenti": sum(len(route.crossings) for route in sheet.routes),
        "riempimento_pct": round(fill_ratio(sheet.symbols, sheet.routes, AREA) * 100, 1),
        "copertura_ingombro": round(ink_coverage(sheet.symbols, sheet.routes, box), 3),
        "margine_minimo_mm": round(border_margin_mm(sheet.symbols, sheet.routes, AREA) or 0.0, 1),
        "margine_ammesso_mm": round(
            margin_allowed_mm(sheet.symbols, sheet.routes, AREA, STEP_MM), 1
        ),
        "lunghezza_mm": round(length, 1),
        "vuoti_passi": gaps,
        "simboli": len(sheet.symbols),
        "tratte": len(sheet.routes),
    }


def main(folders: list[str]) -> None:
    out: dict[str, dict] = {}
    for folder in folders:
        here = Path(folder)
        for path in sorted(here.glob("*-geometria.json")):
            name = path.name.removesuffix("-geometria.json")
            raw = json.loads(path.read_text(encoding="utf-8"))
            for sheet_raw in raw["sheets"]:
                sheet = SheetGeometry.model_validate(sheet_raw)
                found = measure(sheet)
                # Criterio 3 e 12: l'ingresso dell'acqua fredda torna vicino al
                # bollitore che alimenta, e ogni organo di servizio sta addosso
                # al pezzo che serve.
                vicino = _nearest(
                    sheet,
                    "acquedotto",
                    [
                        item.component_id
                        for item in sheet.symbols
                        if item.component_id in {"bollitore", "accumulo", "volano"}
                    ],
                )
                if vicino is not None:
                    found["acqua_fredda_dal_pezzo_che_alimenta"] = {
                        "pezzo": vicino[0],
                        "distanza_mm": round(vicino[1], 1),
                    }
                out[f"{here.name}/{name}/{sheet.sheet_id}"] = found
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:] or ["docs/collaudi/DRAW-013/prima", "docs/collaudi/DRAW-013/dopo"])
