"""Il controllo a vista della base: la base ridisegnata sopra la planimetria d'origine (REL-026, C-3).

    mep.py base <planimetria.pdf|.jpg|.png> --out <cartella> [--pagina N] [--dpi D] [--zona x0,y0,x1,y1]
    mep.py base <pianta.json> --out <cartella> [--zona x0,y0,x1,y1]

**Leggere la planimetria e' il lavoro di un agente** (`skill/base/ISTRUZIONI.md`); questo
comando gli da' gli occhi e il righello, non legge niente al posto suo.

- **Con la planimetria** (un PDF, un JPEG, un PNG): la pagina come immagine, alla
  risoluzione detta, con una **griglia in pixel** e i numeri sui bordi. Sono i pixel della
  taratura: la barra dei 10 metri del catastale va da qui a qui, la quota del disegno a
  mano da qui a qui. `--zona` ingrandisce un riquadro, in pixel della pagina.
- **Con la pianta** (il JSON, con lo `sfondo` tarato): la **sovrapposizione** — la
  planimetria d'origine schiarita, la **griglia in metri** della pianta, e sopra la base
  trascritta a colori forti (muri rossi, finestre blu, porte verdi, stanze viola, balconi
  arancio) —, alla stessa scala; e in console i controlli che dicono se la taratura regge:
  le porte, gli spessori, le superfici. `--zona` ingrandisce un riquadro, in metri.

Le immagini le fa il PDF del motore, che incorpora JPEG e PNG; la pagina di un PDF la rende
quello che l'ambiente ha — PyMuPDF, pypdfium2 o pdftoppm, come l'anteprima —, e se non ha
niente il comando lo dice. Nessuna dipendenza nuova.
"""

from __future__ import annotations

import importlib
import math
import shutil
import subprocess
import zlib
from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from pathlib import Path

from disegnatore_mep.graphics.pdf import (
    FIRMA_DEL_PNG,
    leggi_il_png,
    misura_dell_immagine,
    svg_in_pdf,
)
from disegnatore_mep.graphics.standard import FAMIGLIA_DELLE_SCRITTE, PT_MM

from .base import aperture_della_base, dentro, locali_con_nome, muri_della_base, superficie
from .modello import DPI_DEL_PDF, Pianta, carica_pianta
from .tavola import Arco, Area, Linea, Primitiva, Scritta, _escape, _svg

Punto = tuple[float, float]

DPI_NOMINALE = 150
"""Per un'immagine (JPEG, PNG) un pixel e' un pixel: il foglio della sovrapposizione la
misura come se fosse a 150 dpi, e il PNG che ne esce ha gli stessi pixel."""

LATO_DELLO_ZOOM_PX = 2000
"""Il lato lungo di un ingrandimento: abbastanza per vedere un centimetro di muro."""

ROSSO_DEI_MURI = "#e3242b"
BLU_DELLE_FINESTRE = "#1565d8"
VERDE_DELLE_PORTE = "#13923a"
VIOLA_DELLE_STANZE = "#b0189a"
ARANCIO_DEI_BALCONI = "#e07800"
NERO_DEI_PEZZI = "#111111"
CIANO_DELLA_GRIGLIA = "#0aa5b8"
"""I colori della sovrapposizione: forti apposta, perche' si vedano sopra qualunque
planimetria. Non sono quelli della tavola: qui si controlla, non si consegna."""

OPACITA_DELL_ORIGINE = 0.55
"""L'origine schiarita, perche' la base trascritta si legga sopra."""


class ErroreDellaBase(ValueError):
    """La sovrapposizione non si fa: si dice perche', e che cosa serve."""


# --- dalla planimetria all'immagine ---------------------------------------------------------


def pagina_in_png(pdf: Path, pagina: int, dpi: int, destinazione: Path) -> str:
    """La pagina `pagina` (dalla prima) del PDF come PNG a `dpi`, con quello che l'ambiente ha.
    Dice con che cosa l'ha resa."""
    from disegnatore_mep.skill import _png

    try:
        fitz = importlib.import_module("fitz")
        documento = fitz.open(pdf)
        if not 1 <= pagina <= len(documento):
            raise ErroreDellaBase(f"{pdf.name} ha {len(documento)} pagine: la {pagina} non c'e'")
        documento[pagina - 1].get_pixmap(dpi=dpi, alpha=False).save(destinazione)
        return "PyMuPDF"
    except ImportError:
        pass
    try:
        pdfium = importlib.import_module("pypdfium2")
        documento = pdfium.PdfDocument(str(pdf))
        if not 1 <= pagina <= len(documento):
            raise ErroreDellaBase(f"{pdf.name} ha {len(documento)} pagine: la {pagina} non c'e'")
        resa = documento[pagina - 1].render(scale=dpi / 72, rev_byteorder=True)
        dati, passo, canali = bytes(resa.buffer), resa.stride, resa.n_channels
        righe = []
        for y in range(resa.height):
            riga = dati[y * passo : y * passo + resa.width * canali]
            if canali == 4:
                riga = bytes(b for i, b in enumerate(riga) if i % 4 != 3)
            elif canali == 1:
                riga = bytes(b for b in riga for _ in range(3))
            righe.append(riga)
        destinazione.write_bytes(_png(resa.width, resa.height, righe))
        return "pypdfium2"
    except ImportError:
        pass
    programma = shutil.which("pdftoppm")
    if programma:
        radice = destinazione.with_suffix("")
        subprocess.run(
            [programma, "-png", "-r", str(dpi), "-f", str(pagina), "-l", str(pagina), "-singlefile",
             str(pdf), str(radice)],
            check=True, capture_output=True,
        )
        return "pdftoppm"
    raise ErroreDellaBase(
        "per guardare un PDF serve un lettore: manca pypdfium2 (python3 -m pip install pypdfium2==5.13.0), "
        "PyMuPDF o pdftoppm. Senza, chiedi al progettista la planimetria come immagine (JPEG o PNG)"
    )


def _png_pieno(dati: bytes) -> bytes:
    """Un PNG con la trasparenza o interlacciato, rifatto pieno su fondo bianco: il PDF del
    motore incorpora solo PNG pieni e a righe. Con la sola libreria standard: e' lento su
    un'immagine grande, ma capita di rado (una planimetria arriva in JPEG o in PDF)."""
    from disegnatore_mep.skill import _png

    png = leggi_il_png(dati)
    if png.interlacciato:
        raise ErroreDellaBase("PNG interlacciato: salvalo non interlacciato, o come JPEG")
    if png.bit != 8 or png.colore not in (4, 6):
        raise ErroreDellaBase(f"PNG a {png.bit} bit di tipo {png.colore}: salvalo come JPEG")
    canali = 2 if png.colore == 4 else 4
    riga_byte = png.larghezza * canali
    grezzo = zlib.decompress(png.compressi)
    precedente = bytearray(riga_byte)
    righe: list[bytes] = []
    posto = 0
    for _ in range(png.altezza):
        filtro, riga = grezzo[posto], bytearray(grezzo[posto + 1 : posto + 1 + riga_byte])
        posto += 1 + riga_byte
        for i in range(riga_byte):
            a = riga[i - canali] if i >= canali else 0
            b = precedente[i]
            c = precedente[i - canali] if i >= canali else 0
            if filtro == 1:
                riga[i] = (riga[i] + a) & 0xFF
            elif filtro == 2:
                riga[i] = (riga[i] + b) & 0xFF
            elif filtro == 3:
                riga[i] = (riga[i] + (a + b) // 2) & 0xFF
            elif filtro == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                riga[i] = (riga[i] + (a if pa <= pb and pa <= pc else (b if pb <= pc else c))) & 0xFF
        precedente = riga
        rgb = bytearray()
        for x in range(png.larghezza):
            pixel = riga[x * canali : (x + 1) * canali]
            colore, alfa = (pixel[:1] * 3, pixel[1]) if canali == 2 else (pixel[:3], pixel[3])
            rgb += bytes((v * alfa + 255 * (255 - alfa)) // 255 for v in colore)
        righe.append(bytes(rgb))
    return _png(png.larghezza, png.altezza, righe)


@dataclass(frozen=True)
class Immagine:
    """L'immagine d'origine pronta per il foglio: il file accanto al foglio, i pixel, e quanti
    millimetri di foglio fa un pixel."""

    file: Path
    pixel: tuple[int, int]
    dpi: int
    lettore: str

    @property
    def mm_per_px(self) -> float:
        return 25.4 / self.dpi


def immagine_dell_origine(sorgente: Path, cartella: Path, pagina: int = 1, dpi: int = DPI_DEL_PDF) -> Immagine:
    """La planimetria come immagine, nella cartella del lavoro: un JPEG o un PNG si copiano
    (un PNG con la trasparenza si rifa' pieno), la pagina di un PDF si rende a `dpi`."""
    if not sorgente.exists():
        raise ErroreDellaBase(f"la planimetria {sorgente} non c'e'")
    cartella.mkdir(parents=True, exist_ok=True)
    suffisso = sorgente.suffix.lower()
    if suffisso == ".pdf":
        destinazione = cartella / f"{sorgente.stem}-p{pagina}-{dpi}dpi.png"
        lettore = pagina_in_png(sorgente, pagina, dpi, destinazione)
        return Immagine(destinazione, misura_dell_immagine(destinazione.read_bytes()), dpi, lettore)
    if suffisso in (".jpg", ".jpeg", ".png"):
        dati = sorgente.read_bytes()
        destinazione = cartella / sorgente.name
        if dati[:8] == FIRMA_DEL_PNG:
            png = leggi_il_png(dati)
            if png.colore in (4, 6) or png.interlacciato:
                destinazione = cartella / f"{sorgente.stem}-pieno.png"
                dati = _png_pieno(dati)
        if destinazione.resolve() != sorgente.resolve():
            destinazione.write_bytes(dati)
        return Immagine(destinazione, misura_dell_immagine(dati), DPI_NOMINALE, "immagine")
    raise ErroreDellaBase(
        f"{sorgente.name}: la planimetria va data come PDF, JPEG o PNG (una foto del telefono in HEIC si "
        "salva come JPEG)"
    )


# --- il foglio della sovrapposizione -----------------------------------------------------------


@dataclass
class Foglio:
    """Un foglio grande quanto l'immagine d'origine, in millimetri: un pixel e' `mm_per_px`."""

    immagine: Immagine
    opacita: float = 1.0
    primitive: list[Primitiva] = field(default_factory=list)

    @property
    def misura_mm(self) -> tuple[float, float]:
        return (self.immagine.pixel[0] * self.immagine.mm_per_px, self.immagine.pixel[1] * self.immagine.mm_per_px)

    def svg(self) -> str:
        w, h = (round(v, 4) for v in self.misura_mm)
        parti = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:g}mm" height="{h:g}mm" viewBox="0 0 {w:g} {h:g}" '
            f'font-family="{FAMIGLIA_DELLE_SCRITTE}">',
            f'<rect x="0" y="0" width="{w:g}" height="{h:g}" fill="#ffffff" stroke="none"/>',
            f'<image href="{_escape(self.immagine.file.name)}" x="0" y="0" width="{w:g}" height="{h:g}" '
            f'preserveAspectRatio="none" opacity="{self.opacita:g}"/>',
            *(_svg(p) for p in self.primitive),
            "</svg>",
        ]
        return "\n".join(parti) + "\n"

    def scrivi(self, pdf: Path) -> None:
        pdf.write_bytes(svg_in_pdf(self.svg(), self.immagine.file.parent, "Controllo a vista della base").dati)


def _corpo_pt(px: float, mm_per_px: float) -> float:
    """Il corpo, in punti, di una scritta alta `px` pixel sull'immagine."""
    return px * mm_per_px / PT_MM


def _passo(campo: float, desiderate: float = 12.0, passi: Sequence[float] = (1, 2, 5)) -> float:
    """Il passo tondo (1, 2, 5 per una potenza di dieci) che da' circa `desiderate` linee."""
    grezzo = campo / desiderate
    potenza = 10 ** math.floor(math.log10(grezzo)) if grezzo > 0 else 1
    return min((p * potenza for p in (*passi, 10)), key=lambda v: abs(v - grezzo))


def griglia_in_pixel(foglio: Foglio, zona: tuple[float, float, float, float] | None) -> None:
    """La griglia dei pixel della pagina, coi numeri sui bordi della zona guardata."""
    k = foglio.immagine.mm_per_px
    w, h = foglio.immagine.pixel
    x0, y0, x1, y1 = zona or (0.0, 0.0, float(w), float(h))
    passo = _passo(max(x1 - x0, y1 - y0), 14.0)
    alta = max(x1 - x0, y1 - y0) / 90  # una scritta alta circa un novantesimo della zona, in pixel
    corpo = _corpo_pt(alta, k)
    spessore = max(0.1, alta * k * 0.08)
    v = math.floor(x0 / passo) * passo
    while v <= x1:
        foglio.primitive.append(Linea(((v * k, y0 * k), (v * k, y1 * k)), CIANO_DELLA_GRIGLIA, spessore, "g"))
        foglio.primitive.append(Scritta(f"{v:g}", v * k + spessore, y0 * k + alta * k * 1.1, corpo, "g",
                                        colore=CIANO_DELLA_GRIGLIA))
        v += passo
    v = math.floor(y0 / passo) * passo
    while v <= y1:
        foglio.primitive.append(Linea(((x0 * k, v * k), (x1 * k, v * k)), CIANO_DELLA_GRIGLIA, spessore, "g"))
        foglio.primitive.append(Scritta(f"{v:g}", x0 * k + spessore * 2, v * k - spessore * 2, corpo, "g",
                                        colore=CIANO_DELLA_GRIGLIA))
        v += passo


def _estensione_della_base(pianta: Pianta) -> tuple[float, float, float, float] | None:
    xs: list[float] = []
    ys: list[float] = []
    for muro in pianta.muri:
        h = muro.spessore / 2
        xs += [muro.da[0] - h, muro.da[0] + h, muro.a[0] - h, muro.a[0] + h]
        ys += [muro.da[1] - h, muro.da[1] + h, muro.a[1] - h, muro.a[1] + h]
    for poligono in [*pianta.sagome_muri, *(s.poligono for s in pianta.stanze), *(b.poligono for b in pianta.balconi)]:
        xs += [p[0] for p in poligono]
        ys += [p[1] for p in poligono]
    for pezzo in pianta.pezzi:
        x0, y0, x1, y1 = pezzo.rettangolo
        xs += [x0, x1]
        ys += [y0, y1]
    if not xs:
        return None
    return min(xs), min(ys), max(xs), max(ys)


def griglia_in_metri(foglio: Foglio, pianta: Pianta, zona_m: tuple[float, float, float, float]) -> None:
    """La griglia della pianta, in metri, sulla zona guardata: girata come lo sfondo."""
    assert pianta.sfondo is not None
    sfondo, k = pianta.sfondo, foglio.immagine.mm_per_px

    def P(x: float, y: float) -> Punto:
        px, py = sfondo.in_pixel(x, y)
        return (round(px * k, 4), round(py * k, 4))

    x0, y0, x1, y1 = zona_m
    passo = _passo(max(x1 - x0, y1 - y0), 12.0)
    alta_mm = max(x1 - x0, y1 - y0) * sfondo.px_per_m * k / 100
    corpo = alta_mm / PT_MM
    spessore = max(0.1, alta_mm * 0.07)
    xs = [round(math.ceil(x0 / passo) * passo + i * passo, 6) for i in range(int((x1 - x0) / passo) + 2)]
    ys = [round(math.ceil(y0 / passo) * passo + j * passo, 6) for j in range(int((y1 - y0) / passo) + 2)]
    xs, ys = [v for v in xs if v <= x1 + 1e-9], [v for v in ys if v <= y1 + 1e-9]
    for v in xs:
        foglio.primitive.append(Linea((P(v, y0), P(v, y1)), CIANO_DELLA_GRIGLIA, spessore, "g", "2 1"))
    for v in ys:
        foglio.primitive.append(Linea((P(x0, v), P(x1, v)), CIANO_DELLA_GRIGLIA, spessore, "g", "2 1"))
    # I numeri: x= sulle verticali e y= sulle orizzontali, ripetuti ogni quattro maglie, perche'
    # dovunque si guardi ce ne sia uno vicino (e il bordo dell'immagine non li tagli tutti).
    for j, riga in enumerate(ys):
        for i, colonna in enumerate(xs):
            if j % 4 == 0:
                a = P(colonna, riga + passo * 0.12)
                foglio.primitive.append(Scritta(f"x={colonna:g}", a[0] + spessore * 2, a[1] + alta_mm, corpo, "g",
                                                colore=CIANO_DELLA_GRIGLIA))
            if i % 4 == 0:
                a = P(colonna + passo * 0.05, riga)
                foglio.primitive.append(Scritta(f"y={riga:g}", a[0], a[1] - spessore * 3, corpo, "g",
                                                colore=CIANO_DELLA_GRIGLIA))


def _ricolora(p: Primitiva, colore: str, spessore: float, riempimento_opacita: float = 0.18) -> Primitiva:
    if isinstance(p, Area):
        return replace(p, colore=colore, opacita=riempimento_opacita)
    if isinstance(p, (Linea, Arco)):
        return replace(p, colore=colore, spessore=spessore)
    return p


def base_sopra(foglio: Foglio, pianta: Pianta) -> None:
    """La base trascritta, a colori forti, nel posto in cui la taratura la mette."""
    assert pianta.sfondo is not None
    sfondo, k = pianta.sfondo, foglio.immagine.mm_per_px
    mm_per_m = sfondo.px_per_m * k

    def P(x: float, y: float) -> Punto:
        px, py = sfondo.in_pixel(x, y)
        return (round(px * k, 4), round(py * k, 4))

    tratto = max(0.12, min(0.5, 0.012 * mm_per_m))  # circa un centimetro e mezzo di muro, entro 0,12–0,5 mm
    colori = {"A-WALL": ROSSO_DEI_MURI, "A-GLAZ": BLU_DELLE_FINESTRE, "A-DOOR": VERDE_DELLE_PORTE,
              "A-FLOR-OTLN": ARANCIO_DEI_BALCONI}
    for p in muri_della_base(pianta, P):
        foglio.primitive.append(_ricolora(p, ROSSO_DEI_MURI, tratto))
    disegno, _ = aperture_della_base(pianta, P, mm_per_m)
    for p in disegno:
        colore = colori.get(getattr(p, "layer", ""), VERDE_DELLE_PORTE)
        foglio.primitive.append(_ricolora(p, colore, tratto * 1.3, 0.35))
    alta_mm = 0.22 * mm_per_m  # le scritte alte 22 cm di pianta
    for chi, parti, poligono in locali_con_nome(pianta):
        colore = ARANCIO_DEI_BALCONI if chi.startswith("balcone") else VIOLA_DELLE_STANZE
        foglio.primitive.append(Linea((*(P(*q) for q in poligono), P(*poligono[0])), colore, tratto, "s", "3 1.5"))
        cx = sum(x for x, _ in poligono) / len(poligono)
        cy = sum(y for _, y in poligono) / len(poligono)
        if not dentro((cx, cy), poligono):
            cx, cy = poligono[0][0] * 0.9 + poligono[2 % len(poligono)][0] * 0.1, poligono[0][1] * 0.9 + poligono[
                2 % len(poligono)][1] * 0.1
        x, y = P(cx, cy)
        foglio.primitive.append(Scritta(" · ".join(parti), x, y, alta_mm / PT_MM, "s", True, colore, "middle"))
    for pezzo in pianta.pezzi:
        x0, y0, x1, y1 = pezzo.rettangolo
        angoli = [P(x0, y0), P(x1, y0), P(x1, y1), P(x0, y1)]
        foglio.primitive.append(Linea((*angoli, angoli[0]), NERO_DEI_PEZZI, tratto, "p"))
        x, y = P(pezzo.x, pezzo.y)
        foglio.primitive.append(Scritta(pezzo.sigla, x, y + alta_mm * 0.35, alta_mm / PT_MM * 0.8, "p", True,
                                        NERO_DEI_PEZZI, "middle"))


def legenda(foglio: Foglio, voci: Sequence[tuple[str, str]], zona_mm: tuple[float, float, float, float]) -> None:
    """La legenda della sovrapposizione: una riga sola sul bordo basso della zona guardata, perche'
    copra il meno possibile della planimetria."""
    x0, _, x1, y1 = zona_mm
    alta = max(x1 - x0, zona_mm[3] - zona_mm[1]) / 110
    corpo = alta / PT_MM
    larghezza = sum(len(t) + 3 for t, _ in voci) * alta * 0.55 + alta
    y0 = y1 - alta * 1.6
    angoli = ((x0, y0), (x0 + larghezza, y0), (x0 + larghezza, y1), (x0, y1))
    foglio.primitive.append(Area(angoli, "#ffffff", "l", 0.8))
    x = x0 + alta * 0.5
    for i, (testo, colore) in enumerate(voci):
        foglio.primitive.append(Scritta(testo, x, y1 - alta * 0.45, corpo, "l", i == 0, colore))
        x += (len(testo) + 3) * alta * 0.55


# --- i controlli della taratura -------------------------------------------------------------


PORTA_DA_M, PORTA_A_M = 0.60, 1.20
"""Una porta interna sta fra 60 e 120 cm di luce (70–90 le piu'): fuori di li', o la porta e'
speciale, o la taratura e' sbagliata."""
PORTE_DI_SOLITO = (0.70, 0.95)
SPESSORI_M = {"perimetrale": (0.20, 0.70), "portante": (0.20, 0.70), "tramezza": (0.05, 0.20)}
STANZA_DA_M2, STANZA_A_M2 = 1.0, 80.0


def controlli_della_taratura(pianta: Pianta) -> list[str]:
    """Quello che dice se la taratura e la lettura reggono: le misure fuori dal plausibile.
    Sono indizi, non errori: una porta da 1,4 m esiste, ma se lo sono tutte la scala e' sbagliata."""
    righe: list[str] = []
    porte = sorted(a.larghezza for a in pianta.aperture if a.tipo == "porta")
    if porte:
        mediana = porte[len(porte) // 2]
        righe.append(f"Porte: {len(porte)}, luce mediana {mediana:.2f} m (di solito {PORTE_DI_SOLITO[0]:.2f}–"
                     f"{PORTE_DI_SOLITO[1]:.2f}).")
        if not PORTE_DI_SOLITO[0] - 0.05 <= mediana <= PORTE_DI_SOLITO[1] + 0.05:
            righe.append(f"DA GUARDARE: la luce mediana delle porte e' {mediana:.2f} m: se le porte sono "
                         "normali, la taratura e' sbagliata (rapporto "
                         f"{0.80 / mediana:.2f} rispetto a una porta da 80 cm).")
        strane = [f"{a.id} {a.larghezza:.2f} m" for a in pianta.aperture
                  if a.tipo == "porta" and not PORTA_DA_M <= a.larghezza <= PORTA_A_M]
        if strane:
            righe.append(f"DA GUARDARE: porte fuori da {PORTA_DA_M:.2f}–{PORTA_A_M:.2f} m: {'; '.join(strane)}.")
    for tipo, (da, a) in SPESSORI_M.items():
        fuori = [f"{m.id} {m.spessore:.2f} m" for m in pianta.muri if m.tipo == tipo and not da <= m.spessore <= a]
        if fuori:
            righe.append(f"DA GUARDARE: {tipo} fuori da {da:.2f}–{a:.2f} m: {'; '.join(fuori)}.")
    spessori = sorted({round(m.spessore, 2) for m in pianta.muri})
    if spessori:
        righe.append(f"Spessori dei muri: {', '.join(f'{s:.2f}' for s in spessori)} m.")
    totale = 0.0
    for stanza in pianta.stanze:
        mq = superficie(stanza.poligono)
        totale += mq
        if not STANZA_DA_M2 <= mq <= STANZA_A_M2:
            righe.append(f"DA GUARDARE: {stanza.nome} ({stanza.id}) misura {mq:.1f} m².")
    if pianta.stanze:
        elenco = "; ".join(f"{s.nome} {superficie(s.poligono):.1f}" for s in pianta.stanze)
        righe.append(f"Superfici: {elenco}; totale netto {totale:.1f} m².")
    if pianta.balconi:
        righe.append("Balconi: " + "; ".join(f"{b.nome} {superficie(b.poligono):.1f} m²" for b in pianta.balconi) + ".")
    return righe


# --- il comando ----------------------------------------------------------------------------------


def _un_metro(px_per_m: float, px_per_m_y: float | None) -> str:
    if px_per_m_y is None or px_per_m_y == px_per_m:
        return f"{px_per_m:g}"
    return f"{px_per_m:g} (x) / {px_per_m_y:g} (y)"


def _zona(testo: str | None) -> tuple[float, float, float, float] | None:
    if not testo:
        return None
    valori = [float(v) for v in testo.split(",")]
    if len(valori) != 4 or valori[0] >= valori[2] or valori[1] >= valori[3]:
        raise ErroreDellaBase(f"la zona {testo!r} vuole x0,y0,x1,y1 con x0 < x1 e y0 < y1")
    return valori[0], valori[1], valori[2], valori[3]


def _rendi(foglio: Foglio, pdf: Path, png: Path, zona_mm: tuple[float, float, float, float] | None,
           lato_px: int | None = None) -> tuple[str | None, int]:
    """Il PNG del foglio: intero ai pixel dell'origine, o la zona ingrandita."""
    from disegnatore_mep.skill import anteprima

    dpi = foglio.immagine.dpi
    if zona_mm is not None:
        lato_mm = max(zona_mm[2] - zona_mm[0], zona_mm[3] - zona_mm[1])
        dpi = max(dpi, min(600, round((lato_px or LATO_DELLO_ZOOM_PX) / (lato_mm / 25.4))))
    return anteprima(pdf, png, dpi, zona_mm), dpi


@dataclass
class EsitoDellaBase:
    file: list[Path]
    righe: list[str]


def guarda_la_planimetria(sorgente: Path, cartella: Path, pagina: int = 1, dpi: int = DPI_DEL_PDF,
                          zona_px: tuple[float, float, float, float] | None = None) -> EsitoDellaBase:
    """La pagina con la griglia dei pixel: per orientarsi e per la taratura."""
    immagine = immagine_dell_origine(sorgente, cartella, pagina, dpi)
    foglio = Foglio(immagine)
    w, h = immagine.pixel
    if zona_px is not None:
        zona_px = (max(0.0, zona_px[0]), max(0.0, zona_px[1]), min(float(w), zona_px[2]), min(float(h), zona_px[3]))
    griglia_in_pixel(foglio, zona_px)
    nome = immagine.file.stem if sorgente.suffix.lower() == ".pdf" else sorgente.stem
    coda = "" if zona_px is None else f"-zona-{'-'.join(str(round(v)) for v in zona_px)}"
    pdf, png = cartella / f"{nome}-pixel{coda}.pdf", cartella / f"{nome}-pixel{coda}.png"
    foglio.scrivi(pdf)
    k = immagine.mm_per_px
    zona_mm = None if zona_px is None else tuple(v * k for v in zona_px)
    lettore, resa = _rendi(foglio, pdf, png, zona_mm)  # type: ignore[arg-type]
    righe = [
        f"Planimetria: {sorgente.name}" + (f", pagina {pagina}" if sorgente.suffix.lower() == ".pdf" else ""),
        f"Immagine: {immagine.file.name}, {w} x {h} px"
        + (f" a {dpi} dpi (resa con {immagine.lettore}): un pixel e' {25.4 / dpi:.3f} mm di carta"
           if sorgente.suffix.lower() == ".pdf" else " (i pixel dell'immagine)"),
    ]
    if sorgente.suffix.lower() == ".pdf":
        righe.append(f"Pagina: {w * 25.4 / dpi:.0f} x {h * 25.4 / dpi:.0f} mm. Se il disegno e' in scala sulla "
                     "pagina, un metro fa: " + "; ".join(
                         f"1:{s} {dpi / 25.4 * 1000 / s:.2f} px" for s in (50, 100, 200)
                     ) + ". Verificalo con la barra della scala o con una quota: e' la taratura.")
    if lettore is None:
        righe.append("Il PNG non si e' potuto fare: manca un lettore di PDF (pypdfium2, PyMuPDF o pdftoppm).")
    else:
        righe.append(f"Griglia in pixel: {png}" + (f" (ingrandita a {resa} dpi)" if zona_px else ""))
    file = [immagine.file, pdf] + ([png] if lettore else [])
    return EsitoDellaBase(file, righe)


def controlla_a_vista(sorgente: Path, cartella: Path,
                      zona_m: tuple[float, float, float, float] | None = None) -> EsitoDellaBase:
    """La base trascritta sopra la planimetria d'origine, alla stessa scala, e i controlli."""
    pianta = carica_pianta(sorgente)
    if pianta.sfondo is None:
        raise ErroreDellaBase(
            f"{sorgente.name} non ha lo sfondo: la sovrapposizione vuole la planimetria d'origine con la sua "
            "taratura (\"sfondo\": file, px_per_m, origine_px; per un PDF anche pagina e dpi)"
        )
    sfondo = pianta.sfondo
    origine = sorgente.parent / sfondo.file
    immagine = immagine_dell_origine(origine, cartella, sfondo.pagina, sfondo.dpi)
    foglio = Foglio(immagine, OPACITA_DELL_ORIGINE)
    k = immagine.mm_per_px
    estesa = _estensione_della_base(pianta)
    if zona_m is None and estesa is not None:
        margine = 1.0
        zona_m = (estesa[0] - margine, estesa[1] - margine, estesa[2] + margine, estesa[3] + margine)
    if zona_m is None:
        w, h = immagine.pixel
        py_per_m = sfondo.px_per_m_y or sfondo.px_per_m
        zona_m = (-sfondo.origine_px[0] / sfondo.px_per_m, -sfondo.origine_px[1] / py_per_m,
                  (w - sfondo.origine_px[0]) / sfondo.px_per_m, (h - sfondo.origine_px[1]) / py_per_m)
    griglia_in_metri(foglio, pianta, zona_m)
    base_sopra(foglio, pianta)
    angoli = [sfondo.in_pixel(x, y) for x in (zona_m[0], zona_m[2]) for y in (zona_m[1], zona_m[3])]
    w_mm, h_mm = foglio.misura_mm
    zona_mm = (max(0.0, min(p[0] for p in angoli) * k), max(0.0, min(p[1] for p in angoli) * k),
               min(w_mm, max(p[0] for p in angoli) * k), min(h_mm, max(p[1] for p in angoli) * k))
    if zona_mm[0] >= zona_mm[2] or zona_mm[1] >= zona_mm[3]:
        raise ErroreDellaBase(
            "la base cade fuori dall'immagine d'origine: la taratura (px_per_m, origine_px) la porta altrove"
        )
    legenda(foglio, [
        ("Controllo a vista", "#000000"),
        ("muri", ROSSO_DEI_MURI),
        ("finestre", BLU_DELLE_FINESTRE),
        ("porte", VERDE_DELLE_PORTE),
        ("stanze", VIOLA_DELLE_STANZE),
        ("balconi", ARANCIO_DEI_BALCONI),
        (f"griglia in metri, 1 m = {_un_metro(sfondo.px_per_m, sfondo.px_per_m_y)} px", CIANO_DELLA_GRIGLIA),
    ], zona_mm)
    pdf, png = cartella / f"{sorgente.stem}-sovrapposizione.pdf", cartella / f"{sorgente.stem}-sovrapposizione.png"
    foglio.scrivi(pdf)
    lettore, resa = _rendi(foglio, pdf, png, zona_mm)
    righe = [
        f"Sovrapposizione: {png}" + (f" ({resa} dpi)" if lettore else " — il PNG non si e' potuto fare: manca un "
                                     "lettore di PDF (pypdfium2, PyMuPDF o pdftoppm); c'e' il PDF"),
        f"PDF della sovrapposizione (si ingrandisce): {pdf}",
        f"Origine: {origine.name}" + (f", pagina {sfondo.pagina} a {sfondo.dpi} dpi" if origine.suffix.lower() == ".pdf"
                                      else "") + f"; taratura 1 m = {_un_metro(sfondo.px_per_m, sfondo.px_per_m_y)} px, (0, 0) nel pixel "
        f"({sfondo.origine_px[0]:g}, {sfondo.origine_px[1]:g})" + (f", ruotata di {sfondo.rotazione:g} gradi"
                                                                    if sfondo.rotazione else ""),
        f"Zona guardata, in metri: {', '.join(f'{v:.2f}' for v in zona_m)} (--zona per ingrandire)",
        f"Base: {len(pianta.muri)} muri, {len(pianta.sagome_muri)} sagome, {len(pianta.aperture)} aperture, "
        f"{len(pianta.stanze)} stanze, {len(pianta.balconi)} balconi",
        *controlli_della_taratura(pianta),
        "Guarda la sovrapposizione: i muri rossi devono stare sui muri della planimetria, le porte e le "
        "finestre sui loro vani. Dove non combaciano, correggi la pianta, non la taratura di un muro solo.",
    ]
    file = [immagine.file, pdf] + ([png] if lettore else [])
    return EsitoDellaBase(file, righe)


def esegui(sorgente: Path, cartella: Path, pagina: int = 1, dpi: int = DPI_DEL_PDF, zona: str | None = None) -> int:
    """Il sottocomando `base`: con la planimetria la griglia dei pixel, con la pianta la sovrapposizione."""
    if sorgente.suffix.lower() == ".json":
        esito = controlla_a_vista(sorgente, cartella, _zona(zona))
    else:
        esito = guarda_la_planimetria(sorgente, cartella, pagina, dpi, _zona(zona))
    for riga in esito.righe:
        print(riga)
    return 0

