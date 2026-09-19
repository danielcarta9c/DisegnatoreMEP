"""Le misure delle cinque tavole, da una geometria agli atti.

Legge i `*-geometria.json` prodotti da `scripts/tavole-dei-cinque.sh` e stampa
la tabella che il rapporto porta: formato, tratte cedute, curve,
attraversamenti, ingombro, margine dal bordo, riempimento.

Il riempimento c'e' come **misura** e non come giudizio (D-149): sta nella
tabella perche' il rapporto deve portarlo, non perche' qualcuno debba
riportarlo dentro una finestra.

    python docs/collaudi/DRAW-014/misure.py <cartella-con-le-geometrie>
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "src"))

from disegnatore_mep.graphics.frame import ORDINARY_FRAMES  # noqa: E402
from disegnatore_mep.layout.geometry import (  # noqa: E402
    DrawingGeometry,
    border_margin_mm,
    fill_ratio,
)


def _frame_of(larghezza: float) -> object:
    for item in ORDINARY_FRAMES:
        if abs(item.standard.sheet_width_mm - larghezza) < 1e-6:
            return item
    raise SystemExit(f"nessun formato ordinario largo {larghezza:g} mm")


def _formato(percorso: pathlib.Path) -> tuple[str, float]:
    """Il formato si legge dall'SVG accanto: la geometria non lo porta."""
    svg = next(percorso.parent.glob(percorso.name.replace("-geometria.json", "-t*.svg")), None)
    if svg is None:
        return "?", 0.0
    testa = svg.read_text(encoding="utf-8")[:400]
    import re

    trovato = re.search(r'width="([0-9.]+)mm" height="([0-9.]+)mm"', testa)
    if trovato is None:
        return "?", 0.0
    larghezza = float(trovato.group(1))
    nomi = {297.0: "A4", 420.0: "A3", 594.0: "A2", 841.0: "A1"}
    return nomi.get(larghezza, f"{larghezza:g}mm"), larghezza


def main() -> None:
    cartella = pathlib.Path(sys.argv[1])
    righe = []
    for percorso in sorted(cartella.glob("*-geometria.json")):
        dati = DrawingGeometry.model_validate_json(percorso.read_text(encoding="utf-8"))
        nome, larghezza = _formato(percorso)
        frame = _frame_of(larghezza) if larghezza else ORDINARY_FRAMES[1]
        area = frame.drawing_rect_mm  # type: ignore[attr-defined]
        for foglio in dati.sheets:
            tratte = foglio.routes
            cedute = [item for item in tratte if item.unresolved]
            pieghe = sum(
                max(len(segmento) - 2, 0)
                for item in tratte
                for segmento in item.segments
            )
            attraversamenti = sum(len(item.crossings) for item in tratte)
            rettangolo = (area.x_mm, area.y_mm, area.right_mm, area.bottom_mm)
            margine = border_margin_mm(foglio.symbols, foglio.routes, rettangolo)
            righe.append(
                (
                    percorso.name.replace("-geometria.json", "")[:34],
                    nome,
                    f"{len(cedute)}/{len(tratte)}",
                    str(pieghe),
                    str(attraversamenti),
                    "—" if margine is None else f"{margine:.1f}",
                    f"{fill_ratio(foglio.symbols, foglio.routes, rettangolo) * 100:.0f}%",
                )
            )

    intestazione = (
        "impianto",
        "formato",
        "cedute",
        "pieghe",
        "attrav.",
        "margine",
        "riemp.",
    )
    larghezze = [
        max(len(riga[i]) for riga in [intestazione, *righe]) for i in range(len(intestazione))
    ]
    for riga in [intestazione, tuple("-" * n for n in larghezze), *righe]:
        print("  ".join(voce.ljust(n) for voce, n in zip(riga, larghezze, strict=True)))


if __name__ == "__main__":
    main()
