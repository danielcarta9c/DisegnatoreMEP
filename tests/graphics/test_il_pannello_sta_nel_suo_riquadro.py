"""La serpentina del pannello radiante sta dentro il proprio riquadro (I-217).

Sulla tavola della prova pulita C, ingrandita, il pannello radiante aveva la
serpentina che usciva dal riquadro e correva sotto il suo lato: l'ultima ansa
cominciava a 0,92 della larghezza e ne prendeva altri 0,14. Nessun controllo
della tavola guarda dentro un simbolo, e il difetto stava su ogni pannello di
ogni tavola dal 21 settembre 2026. L'ha visto l'occhio, non un numero.

La prova legge la libreria pubblicata: ogni punto della serpentina sta nel
rettangolo che il simbolo disegna.
"""

import re
from pathlib import Path

from disegnatore_mep.graphics.registry import SymbolRegistry

ROOT = Path(__file__).resolve().parents[2]
SYMBOLS = ROOT / "assets" / "symbols"

RECT = re.compile(r'<rect x="([-\d.]+)" y="([-\d.]+)" width="([-\d.]+)" height="([-\d.]+)"/>')
PATH = re.compile(r'<path d="([^"]+)"/>')
POINT = re.compile(r"[ML]([-\d.]+) ([-\d.]+)")


def test_la_serpentina_non_esce_dal_riquadro() -> None:
    body = SymbolRegistry.from_directory(SYMBOLS).get("underfloor-panel").body
    rect = RECT.search(body)
    path = PATH.search(body)
    assert rect is not None and path is not None, "il pannello non disegna piu' riquadro e serpentina"
    x, y, width, height = (float(value) for value in rect.groups())
    punti = [(float(px), float(py)) for px, py in POINT.findall(path.group(1))]
    assert punti, "la serpentina non ha punti"
    fuori = [
        (px, py)
        for px, py in punti
        if not (x <= px <= x + width and y <= py <= y + height)
    ]
    assert not fuori, (
        f"la serpentina esce dal riquadro ({x:g}, {y:g}) – ({x + width:g}, {y + height:g}) "
        f"nei punti {fuori}"
    )
