"""Il confronto affiancato della M.02: il kit a sinistra, la skill a destra (REL-012, fase 2).

    python3 docs/collaudi/REL-012/fase-2/confronto.py

Scrive accanto a se':
- `confronto.png` — le due tavole intere, alla stessa altezza: il kit e' un A2 con le tabelle
  della distinta, la skill un A3 con la sola tabella delle apparecchiature e la legenda
  (REL-015, I-233: tratte, note e computo stanno nel PDF della distinta);
- `confronto-schema.png` — lo schema, alla **stessa scala** (150 dpi), lo stesso
  riquadro di 340 x 182 mm attorno al disegno.
Vuole pypdfium2 e Pillow.
"""

from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFont

QUI = Path(__file__).resolve().parent
RADICE = QUI.parents[3]
KIT = RADICE / "docs/input-pm/2026-10-29-kit-aria-aria/tavole/AA-01_M.02_Schema_funzionale_canalizzato_rev00.pdf"
SKILL = QUI / "tavola" / "caso-prova-aria-aria-t1.pdf"
PUNTI_PER_MM = 72 / 25.4
DPI = 150


def riquadro(pdf: Path, x0: float, y0: float, x1: float, y1: float, dpi: int = DPI) -> Image.Image:
    """Un riquadro della tavola, in millimetri dall'alto a sinistra."""
    pagina = pdfium.PdfDocument(str(pdf))[0]
    scala = dpi / 72
    intera = pagina.render(scale=scala).to_pil().convert("RGB")
    px = dpi / 25.4
    return intera.crop((round(x0 * px), round(y0 * px), round(x1 * px), round(y1 * px)))


def intera(pdf: Path, altezza: int) -> Image.Image:
    pagina = pdfium.PdfDocument(str(pdf))[0]
    immagine = pagina.render(scale=altezza / pagina.get_height()).to_pil().convert("RGB")
    return immagine


def affianca(sinistra: Image.Image, destra: Image.Image, titoli: tuple[str, str], percorso: Path) -> None:
    margine, testata = 20, 50
    altezza = max(sinistra.height, destra.height)
    tela = Image.new("RGB", (sinistra.width + destra.width + 3 * margine, altezza + testata + margine), "white")
    tela.paste(sinistra, (margine, testata))
    tela.paste(destra, (2 * margine + sinistra.width, testata))
    disegno = ImageDraw.Draw(tela)
    try:
        carattere = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
    except OSError:
        carattere = ImageFont.load_default()
    disegno.text((margine, 10), titoli[0], fill="black", font=carattere)
    disegno.text((2 * margine + sinistra.width, 10), titoli[1], fill="black", font=carattere)
    x = margine + sinistra.width + margine // 2
    disegno.line((x, 0, x, tela.height), fill="#c00000", width=3)
    tela.save(percorso, optimize=True)


def main() -> None:
    affianca(
        intera(KIT, 1400),
        intera(SKILL, 1400),
        ("Kit, M.02 (A2, tabelle a 7 pt)", "Skill, M.02 (A3, apparecchiature e legenda)"),
        QUI / "confronto.png",
    )
    affianca(
        riquadro(KIT, 35, 50, 375, 232),
        riquadro(SKILL, 33, 74, 373, 256),
        ("Kit — lo schema", "Skill — lo schema, stessa scala"),
        QUI / "confronto-schema.png",
    )


if __name__ == "__main__":
    main()
