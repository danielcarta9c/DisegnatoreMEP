"""Il PDF senza browser contro quello di `scripts/to-pdf.sh`, al pixel (REL-001, criterio 1).

Per ogni tavola SVG della cartella data:

1. il PDF del browser, con `scripts/to-pdf.sh`, e quello del modulo `graphics/pdf.py`;
2. **la misura della pagina** di tutt'e due, contro il foglio dell'SVG;
3. **la scala del disegno** dentro la pagina del browser: il browser non stampa a misura
   esatta (`REL-002` l'aveva misurato: −0,025 % in orizzontale, +0,043 % in verticale).
   Si misura qui, tavola per tavola, con la correlazione di fase su riquadri di 512 px:
   lo spostamento di ogni riquadro fra le due rese, e la retta che li spiega;
4. il confronto pixel per pixel, **due volte**: con la resa del browser com'e', e con la
   stessa resa riportata a misura esatta — la scala e lo scostamento del punto 3, tolti.
   **Un pixel e' diverso** se un canale cambia di piu' di `SOGLIA`; **una differenza sta
   nei caratteri** se cade dentro il riquadro di una scritta — preso dai due PDF,
   allargato di `MARGINE_PX` —; tutte le altre sono **differenze nel disegno**.

Scrive, per ogni tavola, un'immagine delle differenze nel disegno che restano: in rosso,
sopra la tavola schiarita, perche' si guardino.

E' uno strumento di sessione: vuole PyMuPDF, numpy e il browser, che il progetto non porta.

    python docs/collaudi/REL-001/confronto_pdf.py <cartella-degli-svg> <cartella-di-uscita>
"""

import subprocess
import sys
from pathlib import Path

import fitz  # PyMuPDF
import numpy

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from disegnatore_mep.graphics.pdf import scrivi_pdf  # noqa: E402

DPI = 200
"""Un pixel e' 0,127 mm: lo spessore sottile, 0,18 mm, e' largo un pixel e mezzo, e una
linea che si sposta di un decimo di millimetro cambia colore a una fila di pixel."""

SOGLIA = 96
"""Quanto deve cambiare un canale, su 255, perche' il pixel conti come diverso: sotto,
e' la sfumatura del bordo di una linea resa da due programmi diversi."""

MARGINE_PX = 3
"""Di quanto si allarga il riquadro di una scritta: il bordo sfumato dei glifi, e la
differenza fra i due caratteri — Liberation Sans nel browser, Helvetica qui."""

LATO_DEL_RIQUADRO_PX = 512
"""Il riquadro della correlazione di fase: abbastanza grande da contenere linee in tutte
e due le direzioni, abbastanza piccolo da darne una ventina per foglio."""

TOLLERANZA_PX = 1
"""Di quanto puo' spostarsi un bordo prima di contare: un pixel, 0,127 mm. Due programmi
che rendono la stessa linea a un decimo di pixel l'uno dall'altro sfumano il bordo in
modo diverso; il confronto guarda se il valore di un pixel c'e' **lì o accanto**
nell'altra resa, non se c'e' esattamente lì."""

MM_PER_PX = 25.4 / DPI

Matrice = numpy.ndarray


def resa(pdf: Path, matrice: fitz.Matrix | None = None) -> Matrice:
    pagina = fitz.open(pdf)[0]
    immagine = pagina.get_pixmap(matrix=matrice or fitz.Matrix(DPI / 72, DPI / 72), alpha=False)
    return (
        numpy.frombuffer(immagine.samples, dtype=numpy.uint8)
        .reshape(immagine.height, immagine.stride)[:, : 3 * immagine.width]
        .reshape(immagine.height, immagine.width, 3)
        .astype(numpy.int16)
    )


def riquadri_delle_scritte(pdf: Path) -> list[fitz.Rect]:
    riquadri = []
    for blocco in fitz.open(pdf)[0].get_text("dict")["blocks"]:
        for riga in blocco.get("lines", []):
            for pezzo in riga["spans"]:
                if pezzo["text"].strip():
                    riquadri.append(fitz.Rect(pezzo["bbox"]))
    return riquadri


def _spostamento(a: Matrice, b: Matrice) -> tuple[float, float]:
    """Di quanti pixel `b` e' spostata rispetto ad `a`, al decimo di pixel."""
    prodotto = numpy.fft.fft2(a) * numpy.conj(numpy.fft.fft2(b))
    prodotto /= numpy.abs(prodotto) + 1e-9
    correlazione = numpy.fft.ifft2(prodotto).real
    altezza, larghezza = correlazione.shape
    y, x = numpy.unravel_index(int(numpy.argmax(correlazione)), correlazione.shape)

    def fine(meno: float, centro: float, piu: float) -> float:
        curvatura = meno - 2 * centro + piu
        return 0.0 if curvatura == 0 else (meno - piu) / (2 * curvatura)

    dy = fine(correlazione[(y - 1) % altezza, x], correlazione[y, x], correlazione[(y + 1) % altezza, x])
    dx = fine(correlazione[y, (x - 1) % larghezza], correlazione[y, x], correlazione[y, (x + 1) % larghezza])
    y = y - altezza if y > altezza // 2 else y
    x = x - larghezza if x > larghezza // 2 else x
    return -(x + dx), -(y + dy)


def scala_del_browser(nuovo: Matrice, browser: Matrice) -> tuple[float, float, float, float]:
    """La scala e lo scostamento del disegno del browser rispetto a quello esatto:
    `posizione nel browser = posizione esatta · (1 + e) + o`, per asse, in pixel."""
    altezza = min(nuovo.shape[0], browser.shape[0])
    larghezza = min(nuovo.shape[1], browser.shape[1])
    a = 255 - nuovo[:altezza, :larghezza].mean(axis=2)
    b = 255 - browser[:altezza, :larghezza].mean(axis=2)
    lato = LATO_DEL_RIQUADRO_PX
    punti = []
    for y0 in range(0, altezza - lato, lato // 2):
        for x0 in range(0, larghezza - lato, lato // 2):
            ra, rb = a[y0 : y0 + lato, x0 : x0 + lato], b[y0 : y0 + lato, x0 : x0 + lato]
            if ra.sum() < 50_000 or rb.sum() < 50_000:
                continue  # un riquadro quasi bianco non dice dove sta niente
            dx, dy = _spostamento(ra, rb)
            punti.append((x0 + lato / 2, y0 + lato / 2, dx, dy))
    p = numpy.array(punti)
    ex, ox = numpy.polyfit(p[:, 0], p[:, 2], 1)
    ey, oy = numpy.polyfit(p[:, 1], p[:, 3], 1)
    return float(ex), float(ox), float(ey), float(oy)


def _intorno(immagine: Matrice) -> tuple[Matrice, Matrice]:
    """Il minimo e il massimo di ogni pixel sul suo intorno di `TOLLERANZA_PX`."""
    r = TOLLERANZA_PX
    bordato = numpy.pad(immagine, ((r, r), (r, r), (0, 0)), mode="edge")
    altezza, larghezza = immagine.shape[:2]
    finestre = [
        bordato[dy : dy + altezza, dx : dx + larghezza]
        for dy in range(2 * r + 1)
        for dx in range(2 * r + 1)
    ]
    return numpy.minimum.reduce(finestre), numpy.maximum.reduce(finestre)


def differenze(
    nuovo: Matrice, browser: Matrice, maschera: Matrice
) -> tuple[int, int, Matrice]:
    """Un pixel e' diverso se il suo valore, in una delle due rese, non c'e' nell'intorno
    dello stesso pixel dell'altra, a meno di `SOGLIA`."""
    altezza = min(nuovo.shape[0], browser.shape[0])
    larghezza = min(nuovo.shape[1], browser.shape[1])
    a, b = nuovo[:altezza, :larghezza], browser[:altezza, :larghezza]
    min_a, max_a = _intorno(a)
    min_b, max_b = _intorno(b)
    diversi = (
        (a < min_b - SOGLIA) | (a > max_b + SOGLIA) | (b < min_a - SOGLIA) | (b > max_a + SOGLIA)
    ).any(axis=2)
    nel_disegno = diversi & ~maschera[:altezza, :larghezza]
    return int((diversi & maschera[:altezza, :larghezza]).sum()), int(nel_disegno.sum()), nel_disegno


def maschera_delle_scritte(forma: tuple[int, ...], pdf: list[Path]) -> Matrice:
    maschera = numpy.zeros(forma[:2], dtype=bool)
    scala = DPI / 72
    for documento in pdf:
        for r in riquadri_delle_scritte(documento):
            maschera[
                max(0, int(r.y0 * scala) - MARGINE_PX) : int(r.y1 * scala) + MARGINE_PX + 1,
                max(0, int(r.x0 * scala) - MARGINE_PX) : int(r.x1 * scala) + MARGINE_PX + 1,
            ] = True
    return maschera


def immagine_delle_differenze(nuovo: Matrice, nel_disegno: Matrice, percorso: Path) -> None:
    altezza, larghezza = nel_disegno.shape
    fondo = (255 - (255 - nuovo[:altezza, :larghezza]) // 4).astype(numpy.uint8)
    fondo[nel_disegno] = (220, 0, 0)
    campioni = fitz.Pixmap(fitz.csRGB, larghezza, altezza, fondo.tobytes(), False)
    campioni.save(percorso)


def confronta(svg: Path, uscita: Path) -> dict[str, object]:
    browser = uscita / f"{svg.stem}-browser.pdf"
    nuovo = uscita / f"{svg.stem}.pdf"
    subprocess.run(
        ["bash", str(ROOT / "scripts" / "to-pdf.sh"), str(svg), str(browser)],
        check=True,
        capture_output=True,
    )
    esito = scrivi_pdf(svg, nuovo, svg.stem)
    misure = {
        nome: (p.rect.width * 25.4 / 72, p.rect.height * 25.4 / 72)
        for nome, p in (("browser", fitz.open(browser)[0]), ("nuovo", fitz.open(nuovo)[0]))
    }

    resa_nuova = resa(nuovo)
    resa_del_browser = resa(browser)
    maschera = maschera_delle_scritte(resa_nuova.shape, [nuovo, browser])
    caratteri_grezzo, disegno_grezzo, _ = differenze(resa_nuova, resa_del_browser, maschera)

    ex, ox, ey, oy = scala_del_browser(resa_nuova, resa_del_browser)
    k = DPI / 72
    riportata = resa(browser, fitz.Matrix(k / (1 + ex), 0, 0, k / (1 + ey), -ox / (1 + ex), -oy / (1 + ey)))
    caratteri, disegno, dove = differenze(resa_nuova, riportata, maschera)
    immagine_delle_differenze(resa_nuova, dove, uscita / f"{svg.stem}-differenze.png")
    ys, xs = numpy.nonzero(dove)
    return {
        "tavola": svg.stem,
        "foglio_mm": (esito.larghezza_mm, esito.altezza_mm),
        "pagina_browser_mm": misure["browser"],
        "pagina_nuova_mm": misure["nuovo"],
        "scala_del_browser": (ex, ey),
        "pixel": int(maschera.size),
        "grezzo": (caratteri_grezzo, disegno_grezzo),
        "riportato": (caratteri, disegno),
        "dove_mm": sorted({(round(x * MM_PER_PX), round(y * MM_PER_PX)) for x, y in zip(xs, ys, strict=True)})[:30],
        "sostituzioni": [(s.carattere, s.scritta) for s in esito.sostituzioni],
    }


def main() -> None:
    cartella, uscita = Path(sys.argv[1]), Path(sys.argv[2])
    uscita.mkdir(parents=True, exist_ok=True)
    for svg in sorted(cartella.glob("*.svg")):
        r = confronta(svg, uscita)
        fw, fh = r["foglio_mm"]  # type: ignore[misc]
        bw, bh = r["pagina_browser_mm"]  # type: ignore[misc]
        nw, nh = r["pagina_nuova_mm"]  # type: ignore[misc]
        ex, ey = r["scala_del_browser"]  # type: ignore[misc]
        print(f"{r['tavola']}")
        print(
            f"  pagina: foglio {fw:g}x{fh:g} mm · nuova {nw:.3f}x{nh:.3f} · browser {bw:.3f}x{bh:.3f} "
            f"({(bw / fw - 1) * 100:+.3f} %, {(bh / fh - 1) * 100:+.3f} %)"
        )
        print(f"  disegno del browser: scala {ex * 100:+.4f} % in orizzontale, {ey * 100:+.4f} % in verticale")
        print(
            f"  pixel diversi su {r['pixel']}: col browser com'e' — caratteri {r['grezzo'][0]}, "  # type: ignore[index]
            f"disegno {r['grezzo'][1]}; col browser a misura — caratteri {r['riportato'][0]}, "  # type: ignore[index]
            f"disegno {r['riportato'][1]}"  # type: ignore[index]
        )
        if r["dove_mm"]:
            print(f"  dove resta una differenza nel disegno (mm, arrotondati): {r['dove_mm']}")
        if r["sostituzioni"]:
            print(f"  caratteri sostituiti: {r['sostituzioni']}")


if __name__ == "__main__":
    main()
