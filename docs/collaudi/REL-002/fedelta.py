"""Il cartiglio disegnato dalla skill contro il file del PO — criterio 1 di `REL-002`.

Disegna il cartiglio **com'e' nel file**, cioe' con i segnaposto del file al posto
dei valori, su un A3 vuoto; rasterizza quell'SVG e il file del PO con lo stesso
motore — MuPDF — alla stessa risoluzione, e li confronta pixel per pixel.

**Perche' non passa dal browser.** `scripts/to-pdf.sh` stampa l'SVG con Chromium, e
Chromium arrotonda: nel PDF che ne esce 410 mm diventano 409,896 e 287 diventano
287,122 (-0,025 % in orizzontale, +0,043 % in verticale), e il confronto vedrebbe
spostato di un pixel ogni bordo lontano dall'angolo in alto a sinistra. E' un
difetto dello strumento, non del cartiglio, ed e' misurato qui con `--browser`.

Il criterio e' «differisce solo nei caratteri». Si misura cosi': si toglie dal
confronto il riquadro di ogni testo — l'etichetta o il valore, allargato di mezzo
millimetro — e si contano i pixel che restano diversi. **Fuori dai testi devono
essere zero**; dentro ci sono le differenze fra i caratteri: nel file del PO i
valori ritoccati sono Arial incorporato, qui Helvetica.

E' uno strumento di sessione, come `to-pdf.sh`: vuole PyMuPDF e numpy, che il
pacchetto non ha.

Uso: python docs/collaudi/REL-002/fedelta.py <cartella-di-uscita> [dpi] [--browser]
"""

import subprocess
import sys
from pathlib import Path

import numpy as np
import pymupdf

from disegnatore_mep.graphics.cartiglio import (
    PT_MM,
    Campo,
    Cartiglio,
    CartiglioDellaTavola,
    Testo,
    disegna_cartiglio,
    larghezza_mm,
)
from disegnatore_mep.graphics.frame import NOVE_C_A3

ROOT = Path(__file__).resolve().parents[3]
MODEL = ROOT / "assets" / "cartigli" / "Cartiglio_NoveC_A3.json"
SOURCE = ROOT / "assets" / "cartigli" / "Cartiglio_NoveC_A3.pdf"
SOGLIA = 64
"""Un pixel e' diverso se un canale scarta di piu' di un quarto della scala:
sotto, e' la sfumatura del bordo di una linea, non un segno diverso."""
MARGINE_MM = 0.5


def raster(document: pymupdf.Document, dpi: int) -> np.ndarray:
    pix = document[0].get_pixmap(dpi=dpi, alpha=False, colorspace=pymupdf.csRGB)
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)


def riquadri(cartiglio: Cartiglio) -> list[tuple[float, float, float, float]]:
    """Il riquadro di ogni testo del cartiglio, in millimetri."""
    boxes = []
    tavola = CartiglioDellaTavola.del_file(cartiglio)
    for zona in (cartiglio.modello.testata, cartiglio.modello.fascia):
        for item in zona.elementi:
            if isinstance(item, Testo):
                testo = item.testo
            elif isinstance(item, Campo):
                testo = tavola.testo(item)
            else:
                continue
            if not testo:
                continue
            larghezza = larghezza_mm(testo, item.corpo_pt, item.grassetto)
            x0 = {
                "sinistra": item.x_mm,
                "centro": item.x_mm - larghezza / 2,
                "destra": item.x_mm - larghezza,
            }[item.allineamento]
            corpo = item.corpo_pt * PT_MM
            boxes.append((x0, item.y_mm - corpo, x0 + larghezza, item.y_mm + 0.25 * corpo))
    return boxes


def confronta(nostro: np.ndarray, suo: np.ndarray, cartiglio: Cartiglio, dpi: int, out: Path) -> None:
    alto, largo = min(nostro.shape[0], suo.shape[0]), min(nostro.shape[1], suo.shape[1])
    nostro, suo = nostro[:alto, :largo], suo[:alto, :largo]
    diversi = (np.abs(nostro.astype(int) - suo.astype(int)) > SOGLIA).any(axis=2)
    fuori = diversi.copy()
    px = dpi / 25.4
    for x0, y0, x1, y1 in riquadri(cartiglio):
        a, b = int((y0 - MARGINE_MM) * px), int((y1 + MARGINE_MM) * px) + 1
        c, d = int((x0 - MARGINE_MM) * px), int((x1 + MARGINE_MM) * px) + 1
        fuori[max(a, 0) : b, max(c, 0) : d] = False

    immagine = np.full_like(nostro, 255)
    immagine[diversi] = (190, 190, 190)
    immagine[fuori] = (220, 0, 0)
    pymupdf.Pixmap(
        pymupdf.csRGB, immagine.shape[1], immagine.shape[0], immagine.tobytes(), False
    ).save(out)
    print(f"  pixel diversi (soglia {SOGLIA}/255): {int(diversi.sum())} su {diversi.size} "
          f"({100 * diversi.sum() / diversi.size:.3f} %)")
    print(f"  pixel diversi fuori dai riquadri dei testi: {int(fuori.sum())}")
    if fuori.any():
        ys, xs = np.nonzero(fuori)
        print(f"    dove: x {xs.min() / px:.1f}–{xs.max() / px:.1f} mm, "
              f"y {ys.min() / px:.1f}–{ys.max() / px:.1f} mm")
    print(f"  mappa: {out} (grigio dentro i testi, rosso fuori)")


def main() -> None:
    out = Path(sys.argv[1])
    dpi = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 300
    out.mkdir(parents=True, exist_ok=True)
    cartiglio = Cartiglio.da_file(MODEL)
    disegno = disegna_cartiglio(CartiglioDellaTavola.del_file(cartiglio), NOVE_C_A3)
    svg = out / "cartiglio-come-nel-file.svg"
    svg.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" '
        f'viewBox="0 0 420 297">{disegno.svg}</svg>',
        encoding="utf-8",
    )
    suo = raster(pymupdf.open(SOURCE), dpi)
    print(f"risoluzione: {dpi} dpi")
    print("l'SVG della skill, reso da MuPDF, contro il file del PO:")
    confronta(raster(pymupdf.open(svg), dpi), suo, cartiglio, dpi, out / "differenze.png")
    if "--browser" in sys.argv:
        pdf = out / "cartiglio-come-nel-file.pdf"
        subprocess.run(["bash", str(ROOT / "scripts" / "to-pdf.sh"), str(svg), str(pdf)], check=True)
        print("lo stesso SVG passato da scripts/to-pdf.sh (Chromium), contro il file del PO:")
        confronta(raster(pymupdf.open(pdf), dpi), suo, cartiglio, dpi, out / "differenze-browser.png")


if __name__ == "__main__":
    main()
