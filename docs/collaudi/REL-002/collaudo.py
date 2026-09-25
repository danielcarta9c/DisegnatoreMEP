"""Le tavole di `REL-002`, e la misura che il disegno non si e' mosso.

Per ciascuno dei cinque impianti approvati — grafo e piano di `DRAW-018`, gli stessi
da cui sono uscite le tavole che il PO ha approvato (I-117, I-119):

1. il grafo con i **dati di prova** del cartiglio (`dati-di-prova.json`) aggiunti ai
   metadati — il disegno non li legge;
2. `disegnatore-mep piano … --cartiglio`: la tavola **col cartiglio**;
3. `disegnatore-mep piano …` senza cartiglio, dal grafo com'e' agli atti: la tavola
   **come usciva prima**;
4. tutt'e due in PDF con `scripts/to-pdf.sh`, rasterizzate con MuPDF, e confrontate
   pixel per pixel **fra la testata e il cartiglio**, lontano mezzo millimetro dalla
   squadratura: li' c'e' il disegno, e deve essere lo stesso.

Piu' **la tavola in bozza**: l'impianto 1 dal grafo agli atti, senza dati aggiunti —
indirizzo, titolo e numero mancano, e il cartiglio lo deve dire.

E' uno strumento di sessione: vuole PyMuPDF e numpy, che il pacchetto non ha, e il
browser per `to-pdf.sh`. Si lancia dalla radice del repository con un interprete che
abbia i tre e il pacchetto sul percorso:

    PYTHONPATH=src python3 docs/collaudi/REL-002/collaudo.py <cartella-di-lavoro>

Le tavole in PDF escono in `docs/collaudi/REL-002/tavole/`, il resto nella cartella
di lavoro.
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pymupdf

from disegnatore_mep.graphics.frame import ORDINARY_FRAMES

ROOT = Path(__file__).resolve().parents[3]
QUI = Path(__file__).resolve().parent
APPROVATI = ROOT / "docs" / "collaudi" / "DRAW-018" / "prova-camera-pulita-2026-09-24"
MODELLO = ROOT / "assets" / "cartigli" / "Cartiglio_NoveC_A3.json"
TAVOLE = QUI / "tavole"
DPI = 200
LARGHEZZE_MM = {"A3": 420.0, "A2": 594.0, "A1": 841.0}
SOGLIA = 64
STACCO_MM = 0.5


def piano(grafo: Path, piano_: Path, uscita: Path, cartiglio: bool) -> tuple[Path, str]:
    comando = [
        sys.executable, "-m", "disegnatore_mep", "piano", str(grafo),
        "--piano", str(piano_),
        "--catalog", str(ROOT / "examples" / "layout" / "catalog"),
        "--symbols", str(ROOT / "assets" / "symbols"),
        "--naming", str(ROOT / "naming"),
        "--out", str(uscita),
    ]
    if cartiglio:
        comando += ["--cartiglio", str(MODELLO)]
    fatto = subprocess.run(comando, capture_output=True, text=True, check=False)
    if fatto.returncode != 0:
        raise SystemExit(f"{grafo.name}: il piano non esce\n{fatto.stdout}\n{fatto.stderr}")
    svg = sorted(uscita.glob("*.svg"))
    if len(svg) != 1:
        raise SystemExit(f"{grafo.name}: {len(svg)} tavole invece di una")
    detto = [riga for riga in fatto.stdout.splitlines() if riga.startswith("Cartiglio")]
    return svg[0], "; ".join(detto)


def pdf(svg: Path, destinazione: Path) -> Path:
    subprocess.run(
        ["bash", str(ROOT / "scripts" / "to-pdf.sh"), str(svg), str(destinazione)],
        check=True, capture_output=True,
    )
    return destinazione


def raster(path: Path) -> np.ndarray:
    pagina = pymupdf.open(path)[0]
    pix = pagina.get_pixmap(dpi=DPI, alpha=False, colorspace=pymupdf.csRGB)
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)


def disegno_uguale(prima: Path, dopo: Path, larghezza_mm: float) -> tuple[int, int]:
    """Pixel diversi fra la testata e il cartiglio: (diversi, confrontati)."""
    telaio = next(item for item in ORDINARY_FRAMES if item.standard.sheet_width_mm == larghezza_mm)
    corpo = telaio.body_rect_mm
    a, b = raster(prima), raster(dopo)
    alto, largo = min(a.shape[0], b.shape[0]), min(a.shape[1], b.shape[1])
    px = DPI / 25.4
    y0, y1 = int((corpo.y_mm + STACCO_MM) * px), int((corpo.bottom_mm - STACCO_MM) * px)
    x0, x1 = int((corpo.x_mm + STACCO_MM) * px), int((corpo.right_mm - STACCO_MM) * px)
    zona_a = a[:alto, :largo][y0:y1, x0:x1].astype(int)
    zona_b = b[:alto, :largo][y0:y1, x0:x1].astype(int)
    diversi = (np.abs(zona_a - zona_b) > SOGLIA).any(axis=2)
    return int(diversi.sum()), int(diversi.size)


def main() -> None:
    lavoro = Path(sys.argv[1])
    lavoro.mkdir(parents=True, exist_ok=True)
    TAVOLE.mkdir(exist_ok=True)
    dati = json.loads((QUI / "dati-di-prova.json").read_text(encoding="utf-8"))
    print(f"{'tavola':12s} {'formato':7s} {'disegno: pixel diversi':>24s}  cartiglio")
    for numero in ("1", "2", "3", "4", "5"):
        grafo = APPROVATI / f"grafo-completo-{numero}.json"
        piano_ = APPROVATI / f"piano-completo-{numero}.json"
        documento = json.loads(grafo.read_text(encoding="utf-8"))
        documento["metadata"].update({**dati["tutti"], **dati["impianti"][numero]})
        compilato = lavoro / f"grafo-{numero}-con-i-dati.json"
        compilato.write_text(json.dumps(documento, ensure_ascii=False, indent=2), encoding="utf-8")

        con, detto = piano(compilato, piano_, lavoro / f"con-{numero}", cartiglio=True)
        senza, _ = piano(grafo, piano_, lavoro / f"senza-{numero}", cartiglio=False)
        dopo = pdf(con, TAVOLE / f"tavola-{numero}.pdf")
        prima = pdf(senza, lavoro / f"senza-{numero}.pdf")
        formato = json.loads(piano_.read_text(encoding="utf-8"))["formato"]
        diversi, confrontati = disegno_uguale(prima, dopo, LARGHEZZE_MM[formato])
        print(f"impianto-{numero:3s} {formato:7s} {diversi:>10d} su {confrontati:<11d}  {detto or 'completo'}")

    bozza, detto = piano(
        APPROVATI / "grafo-completo-1.json", APPROVATI / "piano-completo-1.json",
        lavoro / "bozza-1", cartiglio=True,
    )
    pdf(bozza, TAVOLE / "tavola-1-bozza.pdf")
    print(f"{'bozza-1':12s} {'A3':7s} {'':>24s}  {detto}")


if __name__ == "__main__":
    main()
