"""La tavola in PDF, a misura reale e senza browser (REL-001, I-122).

**Il PDF si scrive dall'SVG della tavola**, che resta l'unico disegno: questo
modulo non ridisegna niente, traduce. `render_sheet` e `render_symbol_sheet`
scrivono un SVG in cui un'unita' utente e' un millimetro di carta; qui ogni
elemento diventa l'operatore PDF che dipinge la stessa cosa, e la pagina e'
**il foglio**, della sua misura esatta (ADR 0003). Prima lo faceva
`scripts/to-pdf.sh` col browser, che nell'ambiente di una skill non c'e', e
che non stampa a misura esatta (−0,025 % / +0,043 %, `REL-002`).

**Solo libreria standard**: la skill gira dove non si puo' installare niente.

**Le scritte sono in Helvetica**, uno dei quattordici caratteri che ogni
lettore PDF ha di suo, e non si incorporano: Arial ha le larghezze di
Helvetica, e le larghezze con cui si allinea una scritta sono quelle di
`metriche.py`, lette da Liberation Sans, che ha le larghezze di Arial. Sul
lettore del progettista la scritta esce in Arial o nel suo gemello; il
carattere puo' cambiare di un soffio, il posto no. La codifica e' WinAnsi: un
carattere che non ci sta si sostituisce e **si dice**, non sparisce.

**Quello che l'SVG usa e questo modulo non conosce, lo ferma**: un elemento o
un attributo che cambierebbe il disegno e che qui non si traduce e' un errore
che lo nomina, non un pezzo di tavola che manca in silenzio.
"""

import base64
import math
import re
import zlib
from collections.abc import Iterator
from dataclasses import dataclass, field, replace
from pathlib import Path
from xml.etree import ElementTree

from .metriche import GRASSETTO, NORMALE

SVG_NS = "{http://www.w3.org/2000/svg}"
XLINK_HREF = "{http://www.w3.org/1999/xlink}href"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"

PUNTI_PER_MM = 72 / 25.4
"""Il punto tipografico del PDF e' 1/72 di pollice; il pollice e' 25,4 mm."""

MITER_LIMIT_SVG = 4.0
"""Il limite dello spigolo vivo che l'SVG usa se non si dice (SVG 1.1 §11.4).
Il PDF ne ha un altro, 10: senza dirlo, gli spigoli acuti uscirebbero diversi."""

KAPPA = 4 * (math.sqrt(2) - 1) / 3
"""La distanza dei punti di controllo della curva di Bezier che approssima un
quarto di cerchio di raggio 1: l'errore massimo e' sotto il 3 per diecimila."""

CIFRE = 4
"""Decimali dei numeri nel contenuto della pagina, in millimetri: un decimo di
micron, cento volte sotto il punto di una stampante a 2400 dpi."""

CARATTERE_SOSTITUTO = "?"

FAMIGLIE_SENZA_GRAZIE = ("arial", "helvetica", "liberation sans", "sans-serif")
"""Le famiglie che la tavola dichiara (REL-008): tutte si scrivono in Helvetica."""

GRASSETTI = {"bold", "bolder", "600", "700", "800", "900"}

COLORI_CON_NOME: dict[str, tuple[float, float, float]] = {
    "black": (0.0, 0.0, 0.0),
    "white": (1.0, 1.0, 1.0),
    "red": (1.0, 0.0, 0.0),
    "green": (0.0, 128 / 255, 0.0),
    "blue": (0.0, 0.0, 1.0),
    "gray": (128 / 255, 128 / 255, 128 / 255),
    "grey": (128 / 255, 128 / 255, 128 / 255),
    "magenta": (1.0, 0.0, 1.0),
    "fuchsia": (1.0, 0.0, 1.0),
    "cyan": (0.0, 1.0, 1.0),
    "aqua": (0.0, 1.0, 1.0),
    "yellow": (1.0, 1.0, 0.0),
    "orange": (1.0, 165 / 255, 0.0),
    "purple": (128 / 255, 0.0, 128 / 255),
    "maroon": (128 / 255, 0.0, 0.0),
    "navy": (0.0, 0.0, 128 / 255),
    "teal": (0.0, 128 / 255, 128 / 255),
    "olive": (128 / 255, 128 / 255, 0.0),
    "lime": (0.0, 1.0, 0.0),
    "silver": (192 / 255, 192 / 255, 192 / 255),
}
"""I colori con nome dei quattro formati di base del CSS, piu' l'arancio."""

ATTRIBUTI_MUTI = {"class", "id", "xmlns", "viewBox", "width", "height"}
"""Attributi che non dipingono niente, o che l'elemento legge per conto suo."""

ATTRIBUTI_EREDITATI = {
    "fill",
    "stroke",
    "stroke-width",
    "stroke-dasharray",
    "stroke-dashoffset",
    "stroke-linecap",
    "stroke-linejoin",
    "stroke-miterlimit",
    "fill-opacity",
    "stroke-opacity",
    "fill-rule",
    "font-family",
    "font-size",
    "font-weight",
    "text-anchor",
    "color",
    "visibility",
}

GEOMETRIA: dict[str, set[str]] = {
    "svg": set(),
    "g": set(),
    "line": {"x1", "y1", "x2", "y2"},
    "rect": {"x", "y", "width", "height", "rx", "ry"},
    "circle": {"cx", "cy", "r"},
    "ellipse": {"cx", "cy", "rx", "ry"},
    "polyline": {"points"},
    "polygon": {"points"},
    "path": {"d"},
    "text": {"x", "y"},
    "image": {"x", "y", "width", "height", "preserveAspectRatio", "href", XLINK_HREF},
}
"""Gli elementi che la tavola usa, ciascuno con gli attributi che ne danno la forma."""

ALTRI_ATTRIBUTI = {"transform", "display", "opacity", XML_SPACE}


class ErroreDelPdf(ValueError):
    """L'SVG usa qualcosa che questo modulo non traduce: si dice che cosa."""


@dataclass(frozen=True)
class Stile:
    """Le proprieta' che un elemento eredita da chi lo contiene, coi valori
    iniziali dell'SVG (SVG 1.1 §11, §10)."""

    fill: str = "black"
    stroke: str = "none"
    stroke_width: float = 1.0
    stroke_dasharray: str = "none"
    stroke_dashoffset: float = 0.0
    stroke_linecap: str = "butt"
    stroke_linejoin: str = "miter"
    stroke_miterlimit: float = MITER_LIMIT_SVG
    fill_opacity: float = 1.0
    stroke_opacity: float = 1.0
    fill_rule: str = "nonzero"
    font_family: str = "sans-serif"
    font_size: float = 16.0
    font_weight: str = "normal"
    text_anchor: str = "start"
    color: str = "black"
    visibility: str = "visible"


@dataclass
class Sostituzione:
    """Un carattere che WinAnsi non ha, e la scritta in cui stava."""

    carattere: str
    scritta: str


@dataclass
class _Risorse:
    trasparenze: dict[tuple[float, float], str] = field(default_factory=dict)
    immagini: list[tuple[str, bytes, int, int, int]] = field(default_factory=list)
    caratteri_usati: set[str] = field(default_factory=set)

    def trasparenza(self, riempimento: float, tratto: float) -> str:
        chiave = (round(riempimento, 4), round(tratto, 4))
        if chiave not in self.trasparenze:
            self.trasparenze[chiave] = f"GS{len(self.trasparenze) + 1}"
        return self.trasparenze[chiave]


def _n(valore: float) -> str:
    testo = f"{valore:.{CIFRE}f}".rstrip("0").rstrip(".")
    return "0" if testo in ("-0", "") else testo


def _lunghezza(testo: str | None, predefinito: float = 0.0) -> float:
    if testo is None:
        return predefinito
    valore = testo.strip()
    if valore.endswith("px"):
        valore = valore[:-2]
    try:
        return float(valore)
    except ValueError:
        raise ErroreDelPdf(f"lunghezza che il PDF non sa leggere: {testo!r}") from None


def _numeri(testo: str) -> list[float]:
    return [float(x) for x in re.findall(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", testo)]


def _colore(testo: str, stile: Stile) -> tuple[float, float, float] | None:
    valore = testo.strip().lower()
    if valore == "none":
        return None
    if valore == "currentcolor":
        return _colore(stile.color, replace(stile, color="black"))
    if valore in COLORI_CON_NOME:
        return COLORI_CON_NOME[valore]
    if re.fullmatch(r"#[0-9a-f]{6}", valore):
        return tuple(int(valore[i : i + 2], 16) / 255 for i in (1, 3, 5))  # type: ignore[return-value]
    if re.fullmatch(r"#[0-9a-f]{3}", valore):
        return tuple(int(c * 2, 16) / 255 for c in valore[1:])  # type: ignore[return-value]
    trovato = re.fullmatch(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", valore)
    if trovato:
        return tuple(int(g) / 255 for g in trovato.groups())  # type: ignore[return-value]
    raise ErroreDelPdf(f"colore che il PDF non sa leggere: {testo!r}")


def _stile_di(elemento: ElementTree.Element, genitore: Stile) -> Stile:
    cambi: dict[str, object] = {}
    for nome in ATTRIBUTI_EREDITATI:
        valore = elemento.get(nome)
        if valore is None or valore.strip() == "inherit":
            continue
        campo = nome.replace("-", "_")
        if nome in ("stroke-width", "font-size", "stroke-dashoffset"):
            cambi[campo] = _lunghezza(valore)
        elif nome in ("fill-opacity", "stroke-opacity", "stroke-miterlimit"):
            cambi[campo] = float(valore)
        else:
            cambi[campo] = valore.strip()
    return replace(genitore, **cambi) if cambi else genitore  # type: ignore[arg-type]


def _trasformazioni(testo: str) -> Iterator[tuple[float, float, float, float, float, float]]:
    """Le matrici di una lista `transform`, nell'ordine in cui si scrivono: emesse
    una dopo l'altra con `cm`, il punto le attraversa da destra a sinistra come
    nell'SVG."""
    for nome, argomenti in re.findall(r"([a-zA-Z]+)\s*\(([^)]*)\)", testo):
        valori = _numeri(argomenti)
        if nome == "matrix" and len(valori) == 6:
            a, b, c, d, e, f = valori
            yield (a, b, c, d, e, f)
        elif nome == "translate" and len(valori) in (1, 2):
            yield (1, 0, 0, 1, valori[0], valori[1] if len(valori) == 2 else 0.0)
        elif nome == "scale" and len(valori) in (1, 2):
            sx = valori[0]
            yield (sx, 0, 0, valori[1] if len(valori) == 2 else sx, 0, 0)
        elif nome == "rotate" and len(valori) in (1, 3):
            angolo = math.radians(valori[0])
            coseno, seno = math.cos(angolo), math.sin(angolo)
            if len(valori) == 3:
                yield (1, 0, 0, 1, valori[1], valori[2])
            yield (coseno, seno, -seno, coseno, 0, 0)
            if len(valori) == 3:
                yield (1, 0, 0, 1, -valori[1], -valori[2])
        elif nome == "skewX" and len(valori) == 1:
            yield (1, 0, math.tan(math.radians(valori[0])), 1, 0, 0)
        elif nome == "skewY" and len(valori) == 1:
            yield (1, math.tan(math.radians(valori[0])), 0, 1, 0, 0)
        else:
            raise ErroreDelPdf(f"trasformazione che il PDF non sa leggere: {nome}({argomenti})")


# --- Le forme, come percorsi -------------------------------------------------

Punto = tuple[float, float]


class _Percorso:
    """Un percorso PDF in costruzione: `m`, `l`, `c`, `h`."""

    def __init__(self) -> None:
        self.operatori: list[str] = []

    def muovi(self, p: Punto) -> None:
        self.operatori.append(f"{_n(p[0])} {_n(p[1])} m")

    def linea(self, p: Punto) -> None:
        self.operatori.append(f"{_n(p[0])} {_n(p[1])} l")

    def curva(self, c1: Punto, c2: Punto, p: Punto) -> None:
        self.operatori.append(
            f"{_n(c1[0])} {_n(c1[1])} {_n(c2[0])} {_n(c2[1])} {_n(p[0])} {_n(p[1])} c"
        )

    def chiudi(self) -> None:
        self.operatori.append("h")


def _ellisse(percorso: _Percorso, cx: float, cy: float, rx: float, ry: float) -> None:
    kx, ky = rx * KAPPA, ry * KAPPA
    percorso.muovi((cx + rx, cy))
    percorso.curva((cx + rx, cy + ky), (cx + kx, cy + ry), (cx, cy + ry))
    percorso.curva((cx - kx, cy + ry), (cx - rx, cy + ky), (cx - rx, cy))
    percorso.curva((cx - rx, cy - ky), (cx - kx, cy - ry), (cx, cy - ry))
    percorso.curva((cx + kx, cy - ry), (cx + rx, cy - ky), (cx + rx, cy))
    percorso.chiudi()


def _rettangolo(percorso: _Percorso, x: float, y: float, w: float, h: float,
                rx: float, ry: float) -> None:
    if rx <= 0 or ry <= 0:
        percorso.muovi((x, y))
        percorso.linea((x + w, y))
        percorso.linea((x + w, y + h))
        percorso.linea((x, y + h))
        percorso.chiudi()
        return
    rx, ry = min(rx, w / 2), min(ry, h / 2)
    kx, ky = rx * KAPPA, ry * KAPPA
    percorso.muovi((x + rx, y))
    percorso.linea((x + w - rx, y))
    percorso.curva((x + w - rx + kx, y), (x + w, y + ry - ky), (x + w, y + ry))
    percorso.linea((x + w, y + h - ry))
    percorso.curva((x + w, y + h - ry + ky), (x + w - rx + kx, y + h), (x + w - rx, y + h))
    percorso.linea((x + rx, y + h))
    percorso.curva((x + rx - kx, y + h), (x, y + h - ry + ky), (x, y + h - ry))
    percorso.linea((x, y + ry))
    percorso.curva((x, y + ry - ky), (x + rx - kx, y), (x + rx, y))
    percorso.chiudi()


def _arco(percorso: _Percorso, da: Punto, rx: float, ry: float, rotazione: float,
          grande: bool, orario: bool, a: Punto) -> None:
    """L'arco ellittico dell'SVG in curve di Bezier (SVG 1.1 §F.6.5-F.6.6)."""
    if da == a:
        return
    if rx == 0 or ry == 0:
        percorso.linea(a)
        return
    rx, ry = abs(rx), abs(ry)
    fi = math.radians(rotazione % 360)
    cos_fi, sin_fi = math.cos(fi), math.sin(fi)
    dx, dy = (da[0] - a[0]) / 2, (da[1] - a[1]) / 2
    x1 = cos_fi * dx + sin_fi * dy
    y1 = -sin_fi * dx + cos_fi * dy
    lam = (x1 * x1) / (rx * rx) + (y1 * y1) / (ry * ry)
    if lam > 1:
        radice = math.sqrt(lam)
        rx, ry = rx * radice, ry * radice
    numeratore = rx * rx * ry * ry - rx * rx * y1 * y1 - ry * ry * x1 * x1
    denominatore = rx * rx * y1 * y1 + ry * ry * x1 * x1
    coeff = math.sqrt(max(0.0, numeratore / denominatore))
    if grande == orario:
        coeff = -coeff
    cx1, cy1 = coeff * rx * y1 / ry, -coeff * ry * x1 / rx
    cx = cos_fi * cx1 - sin_fi * cy1 + (da[0] + a[0]) / 2
    cy = sin_fi * cx1 + cos_fi * cy1 + (da[1] + a[1]) / 2

    def angolo(ux: float, uy: float, vx: float, vy: float) -> float:
        return math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)

    inizio = angolo(1, 0, (x1 - cx1) / rx, (y1 - cy1) / ry)
    ampiezza = angolo((x1 - cx1) / rx, (y1 - cy1) / ry, (-x1 - cx1) / rx, (-y1 - cy1) / ry)
    if not orario and ampiezza > 0:
        ampiezza -= 2 * math.pi
    elif orario and ampiezza < 0:
        ampiezza += 2 * math.pi
    pezzi = max(1, math.ceil(abs(ampiezza) / (math.pi / 2) - 1e-9))
    passo = ampiezza / pezzi
    alfa = 4 / 3 * math.tan(passo / 4)

    def sull_ellisse(t: float) -> tuple[Punto, Punto]:
        cos_t, sin_t = math.cos(t), math.sin(t)
        punto = (cx + rx * cos_t * cos_fi - ry * sin_t * sin_fi,
                 cy + rx * cos_t * sin_fi + ry * sin_t * cos_fi)
        tangente = (-rx * sin_t * cos_fi - ry * cos_t * sin_fi,
                    -rx * sin_t * sin_fi + ry * cos_t * cos_fi)
        return punto, tangente

    t = inizio
    p0, d0 = sull_ellisse(t)
    for indice in range(pezzi):
        t += passo
        p1, d1 = sull_ellisse(t)
        if indice == pezzi - 1:
            p1 = a
        percorso.curva((p0[0] + alfa * d0[0], p0[1] + alfa * d0[1]),
                       (p1[0] - alfa * d1[0], p1[1] - alfa * d1[1]), p1)
        p0, d0 = p1, d1


def _percorso_svg(d: str) -> _Percorso:
    """Il linguaggio dei percorsi dell'SVG per intero (SVG 1.1 §8.3)."""
    percorso = _Percorso()
    simboli = re.findall(r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", d)
    corrente: Punto = (0.0, 0.0)
    inizio: Punto = (0.0, 0.0)
    controllo_c: Punto | None = None
    controllo_q: Punto | None = None
    comando = ""
    i = 0

    def numero() -> float:
        nonlocal i
        if i >= len(simboli) or simboli[i].isalpha():
            raise ErroreDelPdf(f"percorso incompleto dopo il comando {comando!r}: {d[:60]!r}")
        valore = float(simboli[i])
        i += 1
        return valore

    def bandiera() -> bool:
        nonlocal i
        testo = simboli[i] if i < len(simboli) else ""
        if testo in ("0", "1"):
            i += 1
            return testo == "1"
        if testo[:1] in ("0", "1") and not testo[1:2].isalpha():
            # Bandiere scritte attaccate al numero dopo, «11.5»: una cifra sola.
            simboli[i] = testo[1:]
            return testo[0] == "1"
        raise ErroreDelPdf(f"bandiera d'arco illeggibile in {d[:60]!r}")

    while i < len(simboli):
        if simboli[i].isalpha():
            comando = simboli[i]
            i += 1
        elif not comando:
            raise ErroreDelPdf(f"percorso senza comando iniziale: {d[:60]!r}")
        relativo = comando.islower()
        ox, oy = corrente if relativo else (0.0, 0.0)
        tipo = comando.upper()
        if tipo == "Z":
            percorso.chiudi()
            corrente = inizio
            controllo_c = controllo_q = None
            continue
        if tipo == "M":
            corrente = (ox + numero(), oy + numero())
            inizio = corrente
            percorso.muovi(corrente)
            comando = "l" if relativo else "L"
            controllo_c = controllo_q = None
        elif tipo == "L":
            corrente = (ox + numero(), oy + numero())
            percorso.linea(corrente)
            controllo_c = controllo_q = None
        elif tipo == "H":
            corrente = (ox + numero(), corrente[1])
            percorso.linea(corrente)
            controllo_c = controllo_q = None
        elif tipo == "V":
            corrente = (corrente[0], oy + numero())
            percorso.linea(corrente)
            controllo_c = controllo_q = None
        elif tipo in ("C", "S"):
            if tipo == "C":
                c1 = (ox + numero(), oy + numero())
            else:
                c1 = (2 * corrente[0] - controllo_c[0], 2 * corrente[1] - controllo_c[1]) \
                    if controllo_c else corrente
            c2 = (ox + numero(), oy + numero())
            fine = (ox + numero(), oy + numero())
            percorso.curva(c1, c2, fine)
            controllo_c, controllo_q, corrente = c2, None, fine
        elif tipo in ("Q", "T"):
            if tipo == "Q":
                q = (ox + numero(), oy + numero())
            else:
                q = (2 * corrente[0] - controllo_q[0], 2 * corrente[1] - controllo_q[1]) \
                    if controllo_q else corrente
            fine = (ox + numero(), oy + numero())
            c1 = (corrente[0] + 2 / 3 * (q[0] - corrente[0]), corrente[1] + 2 / 3 * (q[1] - corrente[1]))
            c2 = (fine[0] + 2 / 3 * (q[0] - fine[0]), fine[1] + 2 / 3 * (q[1] - fine[1]))
            percorso.curva(c1, c2, fine)
            controllo_q, controllo_c, corrente = q, None, fine
        elif tipo == "A":
            rx, ry, rotazione = numero(), numero(), numero()
            grande, orario = bandiera(), bandiera()
            fine = (ox + numero(), oy + numero())
            _arco(percorso, corrente, rx, ry, rotazione, grande, orario, fine)
            corrente = fine
            controllo_c = controllo_q = None
    return percorso


def _punti(testo: str) -> list[Punto]:
    valori = _numeri(testo)
    if len(valori) % 2:
        raise ErroreDelPdf(f"lista di punti dispari: {testo[:60]!r}")
    return list(zip(valori[0::2], valori[1::2], strict=True))


# --- Le scritte ---------------------------------------------------------------


def _testo_dell_elemento(elemento: ElementTree.Element) -> str:
    """Il testo di una scritta come lo mostra l'SVG: senza `xml:space`, gli a capo
    spariscono, le tabulazioni diventano spazi, e gli spazi in fila si fondono in
    uno (SVG 1.1 §10.15). Lo spazio indivisibile resta com'e'."""
    for figlio in elemento:
        raise ErroreDelPdf(f"una scritta con dentro <{figlio.tag.replace(SVG_NS, '')}>: il PDF la sa scrivere solo piana")
    testo = elemento.text or ""
    if elemento.get(XML_SPACE) == "preserve":
        return testo.replace("\n", " ").replace("\t", " ")
    testo = testo.replace("\n", "").replace("\t", " ")
    return re.sub(r" {2,}", " ", testo).strip(" ")


def larghezza_della_scritta(testo: str, corpo_mm: float, grassetto: bool = False) -> float:
    """La larghezza di una scritta in millimetri, con le larghezze di Arial."""
    tabella = GRASSETTO if grassetto else NORMALE
    return sum(tabella.get(c, tabella[CARATTERE_SOSTITUTO]) for c in testo) * corpo_mm / 1000


def _winansi(testo: str, sostituzioni: list[Sostituzione]) -> bytes:
    uscita = bytearray()
    for carattere in testo:
        try:
            uscita += carattere.encode("cp1252")
        except UnicodeEncodeError:
            sostituzioni.append(Sostituzione(carattere=carattere, scritta=testo))
            uscita += CARATTERE_SOSTITUTO.encode("cp1252")
    return bytes(uscita)


def _stringa_pdf(dati: bytes) -> str:
    uscita = []
    for byte in dati:
        carattere = chr(byte)
        if carattere in "\\()":
            uscita.append("\\" + carattere)
        elif byte < 32 or byte > 126:
            uscita.append(f"\\{byte:03o}")
        else:
            uscita.append(carattere)
    return "(" + "".join(uscita) + ")"


# --- Le immagini ----------------------------------------------------------------


def _jpeg(dati: bytes) -> tuple[int, int, int]:
    """Larghezza, altezza e componenti di un JPEG, dal suo segmento SOF."""
    if dati[:2] != b"\xff\xd8":
        raise ErroreDelPdf("l'immagine non e' un JPEG")
    i = 2
    while i + 4 <= len(dati):
        if dati[i] != 0xFF:
            i += 1
            continue
        marcatore = dati[i + 1]
        if marcatore in (0xD8, 0x01) or 0xD0 <= marcatore <= 0xD7:
            i += 2
            continue
        lunghezza = int.from_bytes(dati[i + 2 : i + 4], "big")
        if 0xC0 <= marcatore <= 0xCF and marcatore not in (0xC4, 0xC8, 0xCC):
            altezza = int.from_bytes(dati[i + 5 : i + 7], "big")
            larghezza = int.from_bytes(dati[i + 7 : i + 9], "big")
            return larghezza, altezza, dati[i + 9]
        i += 2 + lunghezza
    raise ErroreDelPdf("JPEG senza segmento SOF")


def _dati_dell_immagine(href: str, cartella: Path | None) -> bytes:
    if href.startswith("data:"):
        intestazione, _, contenuto = href.partition(",")
        if "image/jpeg" not in intestazione or ";base64" not in intestazione:
            raise ErroreDelPdf(f"immagine che il PDF non sa incorporare: {intestazione}")
        return base64.b64decode(contenuto)
    if cartella is None:
        raise ErroreDelPdf(f"immagine collegata senza la cartella dell'SVG: {href}")
    percorso = cartella / href
    if percorso.suffix.lower() not in (".jpg", ".jpeg"):
        raise ErroreDelPdf(f"immagine che il PDF non sa incorporare: {href}")
    return percorso.read_bytes()


# --- La pagina ----------------------------------------------------------------


class _Pagina:
    def __init__(self, cartella: Path | None) -> None:
        self.cartella = cartella
        self.operatori: list[str] = []
        self.risorse = _Risorse()
        self.sostituzioni: list[Sostituzione] = []
        self._opacita = 1.0

    def elemento(self, elemento: ElementTree.Element, stile_del_genitore: Stile) -> None:
        tag = elemento.tag.replace(SVG_NS, "")
        if tag not in GEOMETRIA:
            raise ErroreDelPdf(f"elemento SVG che il PDF non sa scrivere: <{tag}>")
        for nome in elemento.attrib:
            if (
                nome in ATTRIBUTI_MUTI
                or nome in ATTRIBUTI_EREDITATI
                or nome in GEOMETRIA[tag]
                or nome in ALTRI_ATTRIBUTI
                or nome.startswith("data-")
                or nome.startswith("{http://www.w3.org/2000/xmlns/}")
            ):
                continue
            raise ErroreDelPdf(f"attributo che il PDF non sa scrivere: <{tag} {nome}=...>")
        if elemento.get("display", "").strip() == "none":
            return
        opacita = elemento.get("opacity")
        if opacita is not None and float(opacita) != 1 and tag in ("g", "svg"):
            raise ErroreDelPdf("l'opacita' di un gruppo non si traduce: va messa sugli elementi")
        stile = _stile_di(elemento, stile_del_genitore)
        if opacita is not None:
            stile = replace(stile, fill_opacity=stile.fill_opacity * float(opacita),
                            stroke_opacity=stile.stroke_opacity * float(opacita))
        trasformazione = elemento.get("transform")
        self.operatori.append("q")
        if trasformazione:
            for matrice in _trasformazioni(trasformazione):
                self.operatori.append(" ".join(_n(v) for v in matrice) + " cm")
        if tag in ("svg", "g"):
            for figlio in elemento:
                self.elemento(figlio, stile)
        elif stile.visibility != "hidden":
            # Un'immagine non ha riempimento: la sua trasparenza e' solo la propria.
            self._opacita = float(opacita) if opacita is not None else 1.0
            getattr(self, f"_{tag}")(elemento, stile)
        self.operatori.append("Q")

    def _dipingi(self, percorso: _Percorso, stile: Stile, riempibile: bool = True) -> None:
        riempimento = _colore(stile.fill, stile) if riempibile else None
        tratto = _colore(stile.stroke, stile) if stile.stroke_width > 0 else None
        if riempimento is None and tratto is None:
            return
        self._trasparenza(stile.fill_opacity if riempimento else 1.0,
                          stile.stroke_opacity if tratto else 1.0)
        if riempimento is not None:
            self.operatori.append(" ".join(_n(c) for c in riempimento) + " rg")
        if tratto is not None:
            self._tratto(tratto, stile)
        self.operatori.extend(percorso.operatori)
        pari_dispari = stile.fill_rule == "evenodd"
        if riempimento is not None and tratto is not None:
            self.operatori.append("B*" if pari_dispari else "B")
        elif riempimento is not None:
            self.operatori.append("f*" if pari_dispari else "f")
        else:
            self.operatori.append("S")

    def _trasparenza(self, riempimento: float, tratto: float) -> None:
        if riempimento < 1 or tratto < 1:
            nome = self.risorse.trasparenza(riempimento, tratto)
            self.operatori.append(f"/{nome} gs")

    def _tratto(self, colore: tuple[float, float, float], stile: Stile) -> None:
        self.operatori.append(" ".join(_n(c) for c in colore) + " RG")
        self.operatori.append(f"{_n(stile.stroke_width)} w")
        cap = {"butt": 0, "round": 1, "square": 2}.get(stile.stroke_linecap)
        join = {"miter": 0, "round": 1, "bevel": 2}.get(stile.stroke_linejoin)
        if cap is None or join is None:
            raise ErroreDelPdf(f"estremi o spigoli che il PDF non sa scrivere: {stile.stroke_linecap}, {stile.stroke_linejoin}")
        if cap:
            self.operatori.append(f"{cap} J")
        if join:
            self.operatori.append(f"{join} j")
        if stile.stroke_miterlimit != MITER_LIMIT_SVG:
            self.operatori.append(f"{_n(stile.stroke_miterlimit)} M")
        if stile.stroke_dasharray.strip() not in ("none", ""):
            trattini = _numeri(stile.stroke_dasharray)
            if len(trattini) % 2:
                trattini *= 2
            if any(t < 0 for t in trattini):
                raise ErroreDelPdf(f"tratteggio negativo: {stile.stroke_dasharray!r}")
            if sum(trattini) > 0:
                self.operatori.append(
                    "[" + " ".join(_n(t) for t in trattini) + f"] {_n(stile.stroke_dashoffset)} d"
                )

    def _line(self, e: ElementTree.Element, stile: Stile) -> None:
        percorso = _Percorso()
        percorso.muovi((_lunghezza(e.get("x1")), _lunghezza(e.get("y1"))))
        percorso.linea((_lunghezza(e.get("x2")), _lunghezza(e.get("y2"))))
        self._dipingi(percorso, stile, riempibile=False)

    def _polyline(self, e: ElementTree.Element, stile: Stile, chiusa: bool = False) -> None:
        punti = _punti(e.get("points", ""))
        if not punti:
            return
        percorso = _Percorso()
        percorso.muovi(punti[0])
        for punto in punti[1:]:
            percorso.linea(punto)
        if chiusa:
            percorso.chiudi()
        self._dipingi(percorso, stile)

    def _polygon(self, e: ElementTree.Element, stile: Stile) -> None:
        self._polyline(e, stile, chiusa=True)

    def _rect(self, e: ElementTree.Element, stile: Stile) -> None:
        larghezza, altezza = _lunghezza(e.get("width")), _lunghezza(e.get("height"))
        if larghezza <= 0 or altezza <= 0:
            return
        rx, ry = e.get("rx"), e.get("ry")
        raggio_x = _lunghezza(rx if rx is not None else ry)
        raggio_y = _lunghezza(ry if ry is not None else rx)
        percorso = _Percorso()
        _rettangolo(percorso, _lunghezza(e.get("x")), _lunghezza(e.get("y")), larghezza,
                    altezza, raggio_x, raggio_y)
        self._dipingi(percorso, stile)

    def _circle(self, e: ElementTree.Element, stile: Stile) -> None:
        raggio = _lunghezza(e.get("r"))
        if raggio <= 0:
            return
        percorso = _Percorso()
        _ellisse(percorso, _lunghezza(e.get("cx")), _lunghezza(e.get("cy")), raggio, raggio)
        self._dipingi(percorso, stile)

    def _ellipse(self, e: ElementTree.Element, stile: Stile) -> None:
        rx, ry = _lunghezza(e.get("rx")), _lunghezza(e.get("ry"))
        if rx <= 0 or ry <= 0:
            return
        percorso = _Percorso()
        _ellisse(percorso, _lunghezza(e.get("cx")), _lunghezza(e.get("cy")), rx, ry)
        self._dipingi(percorso, stile)

    def _path(self, e: ElementTree.Element, stile: Stile) -> None:
        self._dipingi(_percorso_svg(e.get("d", "")), stile)

    def _text(self, e: ElementTree.Element, stile: Stile) -> None:
        testo = _testo_dell_elemento(e)
        if not testo:
            return
        famiglia = stile.font_family.lower()
        if not any(nome in famiglia for nome in FAMIGLIE_SENZA_GRAZIE):
            raise ErroreDelPdf(f"carattere che la tavola non usa: {stile.font_family!r}")
        riempimento = _colore(stile.fill, stile)
        tratto = _colore(stile.stroke, stile) if stile.stroke_width > 0 else None
        if riempimento is None and tratto is None:
            return
        grassetto = stile.font_weight.strip().lower() in GRASSETTI
        corpo = stile.font_size
        x, y = _lunghezza(e.get("x")), _lunghezza(e.get("y"))
        larghezza = larghezza_della_scritta(testo, corpo, grassetto)
        if stile.text_anchor == "middle":
            x -= larghezza / 2
        elif stile.text_anchor == "end":
            x -= larghezza
        elif stile.text_anchor != "start":
            raise ErroreDelPdf(f"allineamento che il PDF non sa scrivere: {stile.text_anchor!r}")
        self._trasparenza(stile.fill_opacity if riempimento else 1.0,
                          stile.stroke_opacity if tratto else 1.0)
        if riempimento is not None:
            self.operatori.append(" ".join(_n(c) for c in riempimento) + " rg")
        if tratto is not None:
            self._tratto(tratto, stile)
        modo = 2 if riempimento and tratto else (1 if tratto else 0)
        carattere = "F2" if grassetto else "F1"
        self.risorse.caratteri_usati.add(carattere)
        dati = _winansi(testo, self.sostituzioni)
        self.operatori.append(
            f"BT /{carattere} {_n(corpo)} Tf {modo} Tr 1 0 0 -1 {_n(x)} {_n(y)} Tm "
            f"{_stringa_pdf(dati)} Tj ET"
        )

    def _image(self, e: ElementTree.Element, stile: Stile) -> None:
        href = e.get("href") or e.get(XLINK_HREF)
        if not href:
            return
        dati = _dati_dell_immagine(href, self.cartella)
        larghezza_px, altezza_px, componenti = _jpeg(dati)
        if componenti not in (1, 3):
            raise ErroreDelPdf(f"JPEG a {componenti} componenti: il PDF vuole grigi o RGB")
        x, y = _lunghezza(e.get("x")), _lunghezza(e.get("y"))
        w, h = _lunghezza(e.get("width")), _lunghezza(e.get("height"))
        if w <= 0 or h <= 0:
            return
        allineamento = (e.get("preserveAspectRatio") or "xMidYMid meet").split()
        if allineamento[0] != "none":
            scala_x, scala_y = w / larghezza_px, h / altezza_px
            taglia = len(allineamento) > 1 and allineamento[1] == "slice"
            scala = max(scala_x, scala_y) if taglia else min(scala_x, scala_y)
            iw, ih = larghezza_px * scala, altezza_px * scala
            dove = allineamento[0]
            ix = x + {"xMin": 0.0, "xMid": (w - iw) / 2, "xMax": w - iw}[dove[:4]]
            iy = y + {"YMin": 0.0, "YMid": (h - ih) / 2, "YMax": h - ih}[dove[4:]]
            if taglia:
                self.operatori.append(f"{_n(x)} {_n(y)} {_n(w)} {_n(h)} re W n")
            x, y, w, h = ix, iy, iw, ih
        nome = f"Im{len(self.risorse.immagini) + 1}"
        self.risorse.immagini.append((nome, dati, larghezza_px, altezza_px, componenti))
        self._trasparenza(self._opacita, 1.0)
        self.operatori.append(f"{_n(w)} 0 0 {_n(-h)} {_n(x)} {_n(y + h)} cm /{nome} Do")


# --- Il file ------------------------------------------------------------------


@dataclass
class PdfDellaTavola:
    """Il PDF scritto, e i caratteri che WinAnsi non aveva."""

    dati: bytes
    larghezza_mm: float
    altezza_mm: float
    sostituzioni: list[Sostituzione]


def _misura_del_foglio(radice: ElementTree.Element) -> tuple[float, float]:
    larghezza, altezza = radice.get("width", ""), radice.get("height", "")
    if not (larghezza.endswith("mm") and altezza.endswith("mm")):
        raise ErroreDelPdf("l'SVG non dichiara larghezza e altezza in millimetri")
    w, h = float(larghezza[:-2]), float(altezza[:-2])
    vista = _numeri(radice.get("viewBox", ""))
    if vista != [0.0, 0.0, w, h]:
        raise ErroreDelPdf(
            f"il viewBox {radice.get('viewBox')!r} non e' il foglio di {w:g}x{h:g} mm: "
            "un'unita' utente deve essere un millimetro di carta"
        )
    return w, h


def _carattere_pdf(nome_base: str) -> bytes:
    return (
        f"<< /Type /Font /Subtype /Type1 /BaseFont /{nome_base} "
        "/Encoding /WinAnsiEncoding >>"
    ).encode("ascii")


def svg_in_pdf(svg: str, cartella: Path | None = None, titolo: str | None = None) -> PdfDellaTavola:
    """Il PDF di un foglio SVG a misura reale: una pagina, della misura del foglio.

    `cartella` e' dove l'SVG sta, per le immagini collegate e non incorporate.
    Lo stesso SVG da' sempre gli stessi byte: niente date, niente identificativi
    casuali."""
    radice = ElementTree.fromstring(svg)
    if radice.tag != f"{SVG_NS}svg":
        raise ErroreDelPdf("il documento non e' un SVG")
    larghezza_mm, altezza_mm = _misura_del_foglio(radice)
    pagina = _Pagina(cartella)
    k = PUNTI_PER_MM
    pagina.operatori.append(f"{_n(k)} 0 0 {_n(-k)} 0 {_n(altezza_mm * k)} cm")
    pagina.operatori.append(f"{_n(MITER_LIMIT_SVG)} M")
    pagina.elemento(radice, Stile())

    oggetti: list[bytes] = []

    def aggiungi(corpo: bytes) -> int:
        oggetti.append(corpo)
        return len(oggetti)

    contenuto = zlib.compress("\n".join(pagina.operatori).encode("latin-1"), 9)
    n_contenuto = aggiungi(
        f"<< /Length {len(contenuto)} /Filter /FlateDecode >>\nstream\n".encode("ascii")
        + contenuto
        + b"\nendstream"
    )
    caratteri = {
        nome: aggiungi(_carattere_pdf(base))
        for nome, base in (("F1", "Helvetica"), ("F2", "Helvetica-Bold"))
        if nome in pagina.risorse.caratteri_usati
    }
    immagini = {}
    for nome, dati, larghezza_px, altezza_px, componenti in pagina.risorse.immagini:
        spazio = "/DeviceRGB" if componenti == 3 else "/DeviceGray"
        immagini[nome] = aggiungi(
            (
                f"<< /Type /XObject /Subtype /Image /Width {larghezza_px} /Height {altezza_px} "
                f"/ColorSpace {spazio} /BitsPerComponent 8 /Filter /DCTDecode "
                f"/Length {len(dati)} >>\nstream\n"
            ).encode("ascii")
            + dati
            + b"\nendstream"
        )
    risorse = ["/ProcSet [/PDF /Text /ImageC /ImageB]"]
    if caratteri:
        risorse.append(
            "/Font << " + " ".join(f"/{n} {o} 0 R" for n, o in caratteri.items()) + " >>"
        )
    if pagina.risorse.trasparenze:
        risorse.append(
            "/ExtGState << "
            + " ".join(
                f"/{nome} << /Type /ExtGState /ca {_n(ca)} /CA {_n(cs)} >>"
                for (ca, cs), nome in pagina.risorse.trasparenze.items()
            )
            + " >>"
        )
    if immagini:
        risorse.append(
            "/XObject << " + " ".join(f"/{n} {o} 0 R" for n, o in immagini.items()) + " >>"
        )
    n_pagine = len(oggetti) + 2
    n_pagina = aggiungi(
        (
            f"<< /Type /Page /Parent {n_pagine} 0 R "
            f"/MediaBox [0 0 {_n(larghezza_mm * k)} {_n(altezza_mm * k)}] "
            f"/Resources << {' '.join(risorse)} >> /Contents {n_contenuto} 0 R >>"
        ).encode("ascii")
    )
    aggiungi(f"<< /Type /Pages /Kids [{n_pagina} 0 R] /Count 1 >>".encode("ascii"))
    n_catalogo = aggiungi(f"<< /Type /Catalog /Pages {n_pagine} 0 R >>".encode("ascii"))
    informazioni = "<< /Producer (disegnatore-mep)"
    if titolo:
        informazioni += f" /Title {_stringa_pdf(_winansi(titolo, []))}"
    n_info = aggiungi((informazioni + " >>").encode("latin-1"))

    uscita = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    posizioni = []
    for numero, corpo in enumerate(oggetti, start=1):
        posizioni.append(len(uscita))
        uscita += f"{numero} 0 obj\n".encode("ascii") + corpo + b"\nendobj\n"
    inizio_xref = len(uscita)
    uscita += f"xref\n0 {len(oggetti) + 1}\n0000000000 65535 f \n".encode("ascii")
    for posizione in posizioni:
        uscita += f"{posizione:010d} 00000 n \n".encode("ascii")
    uscita += (
        f"trailer\n<< /Size {len(oggetti) + 1} /Root {n_catalogo} 0 R /Info {n_info} 0 R >>\n"
        f"startxref\n{inizio_xref}\n%%EOF\n"
    ).encode("ascii")
    return PdfDellaTavola(
        dati=bytes(uscita),
        larghezza_mm=larghezza_mm,
        altezza_mm=altezza_mm,
        sostituzioni=pagina.sostituzioni,
    )


def scrivi_pdf(svg: Path, pdf: Path | None = None, titolo: str | None = None) -> PdfDellaTavola:
    """Scrive accanto all'SVG — o dove si dice — il PDF della tavola."""
    esito = svg_in_pdf(svg.read_text(encoding="utf-8"), svg.parent, titolo)
    destinazione = pdf if pdf is not None else svg.with_suffix(".pdf")
    destinazione.write_bytes(esito.dati)
    return esito
