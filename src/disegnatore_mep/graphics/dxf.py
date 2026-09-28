"""La tavola in DXF, per il disegnatore che la apre in AutoCAD (REL-004).

**Il DXF e' la stessa tavola dell'SVG**, non un disegno parallelo: legge la
stessa geometria (`SheetGeometry`), usa le stesse funzioni che decidono dove
stanno scavalli, pallini e frecce (`sheet.py`), e il cartiglio lo rilegge dal
frammento che `cartiglio.py` disegna. Quello che aggiunge e' quello che l'SVG
non sa dire e AutoCAD si', con le scelte del PO (I-138, I-139) e delle fonti
(`docs/fonti/ricerche/`):

- **i blocchi**: ogni simbolo e' definito una volta e inserito dove serve,
  ruotato e specchiato come nella tavola. Dentro il blocco la geometria sta sul
  layer 0 con colore e spessore **DaBlocco**, cosi' l'inserimento comanda
  l'aspetto (Autodesk, *Block Object Properties Reference*). Le lettere degli
  strumenti che la tavola tiene diritte (I-033) sono un blocco a parte,
  inserito diritto;
- **i layer**: una rete per fluido e per verso, con il colore **RGB esatto**
  della tavola (I-139), il tratteggio e lo spessore; poi simboli, sigle,
  testi, legenda, cartiglio. I nomi seguono le linee guida americane dei layer
  (US National CAD Standard) e portano la **descrizione in italiano**;
- **le frecce del verso** sono un blocco, inserito sulla linea e ruotato, sul
  layer della sua rete (I-138);
- **i tratteggi** sono definiti nel file in millimetri, e le polilinee li
  generano di continuo sui vertici (PLINEGEN): si vedono giusti appena aperto.

Lo schema sta nello **spazio modello, a 1:1 in millimetri di carta**, con
l'origine nell'angolo in basso a sinistra del foglio; squadratura e cartiglio
stanno nello **spazio carta** della **presentazione** del formato, che ha una
finestra 1:1 bloccata ed e' pronta per la stampa. Il file si apre su quella.
I colori RGB portano accanto un colore d'indice di ripiego, per chi il colore
esatto non lo legge.
Il formato e' **AutoCAD 2013** (AC1027): lo apre ogni AutoCAD e AutoCAD LT dal
2013 in poi, e lo studio ha il 2020 (I-139).

Il logo del cartiglio **non entra nel DXF**: il formato le immagini le
collega, non le contiene (ezdxf, *Image tutorial*). Si scrive accanto al DXF,
e il DXF lo nomina senza percorso: AutoCAD lo cerca nella cartella del disegno.
"""

import contextlib
import math
import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING
from xml.etree import ElementTree

from disegnatore_mep.layout.geometry import FlowKind, Point, RoutedTrunk, SheetGeometry
from disegnatore_mep.layout.legend import MEDIUM_NAMES, RETURN_NAMES, style_for
from disegnatore_mep.model.types import PortFlow

from .cartiglio import CartiglioDellaTavola, disegna_cartiglio
from .frame import Rect, SheetFrame
from .glyphs import _DIRECTION
from .registry import Symbol, SymbolRegistry
from .sheet import (
    ARROW_HALF_WIDTH_MM,
    ARROW_LENGTH_MM,
    CROSS_REFERENCE_RADIUS_MM,
    CROSSING_ARC_RADIUS_MM,
    DRAFT_MARK,
    JUNCTION_DOT_WIDTHS,
    LEGEND_SWATCH_MM,
    LEGEND_TEXT_GAP_MM,
    UNRESOLVED_RUN_DASH,
    _hoppable,
    _interrupted,
    flow_arrow_at,
    sheet_marks,
    stati_della_tavola,
)
from .symbol import FlowGlyph, PortFace, StrokeWeight

if TYPE_CHECKING:
    from ezdxf.document import Drawing
    from ezdxf.entities.dxfgfx import DXFGraphic
    from ezdxf.entities.layer import Layer
    from ezdxf.layouts.base import BaseLayout
    from ezdxf.layouts.layout import Paperspace

DXF_VERSION = "R2013"
"""AutoCAD 2013 (AC1027): lo aprono AutoCAD e AutoCAD LT dal 2013 al 2027
(Autodesk, *AutoCAD drawing file format*), e ha tutto quello che serve —
spessori, colori RGB, testo UTF-8, presentazioni e immagini (ezdxf)."""

ALTEZZA_MAIUSCOLE_EM = 0.688
"""Quanto e' alta una maiuscola, in corpi, nel carattere della tavola.

AutoCAD misura l'altezza di un testo **sulle maiuscole**, l'SVG sul corpo
(`font-size`): scrivere nel DXF il corpo darebbe testi del 45 % piu' grandi
della tavola. La misura e' quella di Liberation Sans, che ha le larghezze di
Arial e di Helvetica (`cartiglio.py`): 1409 unita' su 2048 (fontTools, sul file
del sistema; `docs/fonti/ricerche/research_notes/DXF per AutoCAD/layer-spessori-testi.md`,
§4.4). Cosi' un testo occupa nel DXF lo spazio che occupa nella tavola."""

STILE_TESTO = "NOVEC_ARIAL"
STILE_TESTO_GRASSETTO = "NOVEC_ARIAL_GRASSETTO"

LAYER_SIMBOLI = "M-DIAG-EQPM"
LAYER_SIGLE = "M-ANNO-IDEN"
LAYER_TESTI = "M-ANNO-TEXT"
LAYER_LEGENDA = "M-ANNO-LEGN"
LAYER_CARTIGLIO = "G-ANNO-TTLB"
LAYER_FINESTRA = "G-ANNO-NPLT"

BLOCCO_FRECCIA = "NoveC_FlowArrow"
BLOCCO_PALLINO = "NoveC_JunctionDot"

LINEWEIGHTS = (0, 5, 9, 13, 15, 18, 20, 25, 30, 35, 40, 50, 53, 60, 70, 80, 90, 100,
               106, 120, 140, 158, 200, 211)
"""Gli spessori che il DXF ammette, in centesimi di millimetro (codice 370)."""

NERO = 7
"""Il colore d'indice che AutoCAD disegna nero su fondo bianco e bianco su nero."""

_RETI: dict[tuple[str, bool], str] = {
    ("heating_water", True): "M-HWTR-SPLY",
    ("heating_water", False): "M-HWTR-RETN",
    ("chilled_water", True): "M-CWTR-SPLY",
    ("chilled_water", False): "M-CWTR-RETN",
    ("cold_water", True): "P-DOMW-CPIP",
    ("cold_water", False): "P-DOMW-CPIP",
    ("domestic_hot_water", True): "P-DOMW-HPIP",
    ("domestic_hot_water", False): "P-DOMW-RPIP",
    ("solar_fluid", True): "M-SOLR-SPLY",
    ("solar_fluid", False): "M-SOLR-RETN",
    ("natural_gas", True): "M-NGAS-PIPE",
    ("natural_gas", False): "M-NGAS-PIPE",
    ("refrigerant_liquid", True): "M-REFG-LIQD",
    ("refrigerant_liquid", False): "M-REFG-LIQD",
    ("refrigerant_gas", True): "M-REFG-GASS",
    ("refrigerant_gas", False): "M-REFG-GASS",
    ("supply_air", True): "M-HVAC-SPLY",
    ("supply_air", False): "M-HVAC-SPLY",
    ("return_air", True): "M-HVAC-RETN",
    ("return_air", False): "M-HVAC-RETN",
    ("condensate", True): "M-CNDS-PIPE",
    ("condensate", False): "M-CNDS-PIPE",
}
"""Il layer di ogni rete: il fluido e il verso.

I nomi seguono le linee guida dei layer del US National CAD Standard (AIA CAD
Layer Guidelines): disciplina, gruppo, sottogruppo. Dove il gruppo e' scritto
nelle linee guida si usa quello (`HWTR`, `DOMW`, `CPIP`, `HPIP`, `RPIP`…);
`SOLR` per il solare e' un codice del progetto. **Le linee guida si leggono
come fonte, non come norma**: ISO 13567 fissa la struttura dei nomi ma non i
codici degli impianti."""

LAYER_ALTRA_RETE = "M-PIPE-OTHR"


def nome_del_blocco(symbol_id: str) -> str:
    """Il nome del blocco di un simbolo: `NoveC_` e l'identificativo in CamelCase.

    Solo lettere, cifre e il trattino basso: nessun carattere che AutoCAD
    rifiuti, e nessuno spazio o accento (BS 8541-1, opzione `Source_Type`). Al
    piu' 31 caratteri, anche per le lettere diritte (`NoveC_Thermometer_Lettera`):
    e' il limite di AutoCAD con i nomi estesi spenti (`EXTNAMES = 0`)."""
    return "NoveC_" + "".join(parte.capitalize() for parte in symbol_id.split("-"))


def layer_della_rete(medium: str, supply: bool) -> str:
    return _RETI.get((medium, supply), LAYER_ALTRA_RETE)


def lineweight(mm: float) -> int:
    """Lo spessore ammesso dal DXF piu' vicino a quello della tavola."""
    centesimi = mm * 100
    return min(LINEWEIGHTS, key=lambda valore: (abs(valore - centesimi), valore))


def rgb(colore: str) -> tuple[int, int, int]:
    esadecimale = colore.lstrip("#")
    return (
        int(esadecimale[0:2], 16),
        int(esadecimale[2:4], 16),
        int(esadecimale[4:6], 16),
    )


def aci_vicino(colore: tuple[int, int, int]) -> int:
    """Il colore d'indice (ACI) piu' vicino a un RGB, per distanza nello spazio
    RGB sulla tavolozza con cui ezdxf descrive i colori d'indice di AutoCAD.

    Accanto al colore esatto (codice 420) il DXF scrive un ACI di ripiego
    (codice 62) per chi il 420 non lo legge. AutoCAD tiene il colore esatto,
    che vince (ezdxf, *True Color*): il ripiego non si vede e non si stampa.
    Anche l'ODA File Converter, quando riscrive il file, mette un ripiego
    accanto al colore esatto; il suo criterio non e' documentato e a volte
    sceglie un indice diverso da questo (misurato, `docs/collaudi/REL-004/`).
    Il 7 non e' un candidato: non e' un colore, e' nero su fondo bianco e
    bianco su fondo nero."""
    from ezdxf.colors import DXF_DEFAULT_COLORS, int2rgb

    rosso, verde, blu = colore

    def distanza(indice: int) -> int:
        candidato = int2rgb(DXF_DEFAULT_COLORS[indice])
        return (candidato.r - rosso) ** 2 + (candidato.g - verde) ** 2 + (candidato.b - blu) ** 2

    return min((i for i in range(1, 256) if i != NERO), key=lambda i: (distanza(i), i))


def colora(oggetto: "DXFGraphic | Layer", colore: str) -> None:
    """Il colore esatto della tavola, con il suo ACI di ripiego."""
    valore = rgb(colore)
    oggetto.rgb = valore
    oggetto.dxf.color = aci_vicino(valore)


def _testo(testo: str) -> str:
    """Un testo come lo scrive un TEXT: `%%` apre i codici di controllo di
    AutoCAD, e un segno di percento si scrive `%%%`. Gli spazi non separabili
    del cartiglio tornano spazi: AutoCAD non compatta gli spazi di fila."""
    return testo.replace("%", "%%%").replace(" ", " ")


# --- la geometria dei corpi SVG ---------------------------------------------------

Vertice = tuple[float, float, float]
"""Un vertice di polilinea nel sistema del DXF, y in alto: x, y e la curvatura
(bulge) del tratto che parte da li'."""


@dataclass(frozen=True)
class Polilinea:
    vertici: tuple[Vertice, ...]
    chiusa: bool


@dataclass(frozen=True)
class Segmento:
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass(frozen=True)
class Cerchio:
    cx: float
    cy: float
    r: float
    pieno: bool


@dataclass(frozen=True)
class Riempimento:
    """Una campitura piena: i suoi contorni, ciascuno chiuso."""

    contorni: tuple[tuple[Vertice, ...], ...]


Primitiva = Polilinea | Segmento | Cerchio | Riempimento


@dataclass
class Corpo:
    """Il corpo di un simbolo, nel sistema del DXF: il segno e le lettere diritte."""

    primitive: list[Primitiva] = field(default_factory=list)
    glifi: dict[str, list[Primitiva]] = field(default_factory=dict)


_NUMERO = r"-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
_TOKEN = re.compile(rf"([MLHVAQZmlhvaqz])|({_NUMERO})")
_PIENO = {"black", "currentColor"}
_PASSI_DI_CURVA = 12
"""In quanti tratti si spezza una curva che il DXF non ha: la quadratica di
Bézier e l'arco d'ellisse. A pochi millimetri di corda non si distinguono."""


def _y(y: float) -> float:
    """Da y verso il basso (SVG) a y verso l'alto (DXF)."""
    return 0.0 if y == 0 else -y


def _arco(
    x0: float, y0: float, rx: float, ry: float, phi: float,
    grande: bool, orario: bool, x1: float, y1: float,
) -> list[tuple[float, float, float]]:
    """Un arco SVG in un sistema con y in alto, come vertici con curvatura.

    `orario` dice il verso **a vederlo**, che il ribaltamento dell'asse y non
    cambia: la bandiera SVG 1 — angoli crescenti con y in basso — e' un arco
    orario a vederlo, e nel sistema con y in alto e' orario anche per gli angoli.
    Un arco di cerchio e' un tratto solo, con la sua curvatura (positiva se
    antioraria, come vuole il DXF); un arco d'ellisse si spezza in tratti."""
    if (x0, y0) == (x1, y1):
        return []
    if rx == 0 or ry == 0:
        return [(x0, y0, 0.0)]
    rx, ry = abs(rx), abs(ry)
    cos_p, sin_p = math.cos(math.radians(phi)), math.sin(math.radians(phi))
    dx2, dy2 = (x0 - x1) / 2, (y0 - y1) / 2
    x1p = cos_p * dx2 + sin_p * dy2
    y1p = -sin_p * dx2 + cos_p * dy2
    lam = (x1p / rx) ** 2 + (y1p / ry) ** 2
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    coef = math.sqrt(max(0.0, num / den)) if den else 0.0
    antiorario = not orario
    if grande == antiorario:
        coef = -coef
    cxp, cyp = coef * rx * y1p / ry, -coef * ry * x1p / rx
    cx = cos_p * cxp - sin_p * cyp + (x0 + x1) / 2
    cy = sin_p * cxp + cos_p * cyp + (y0 + y1) / 2

    def angolo(ux: float, uy: float, vx: float, vy: float) -> float:
        return math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)

    t1 = angolo(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = angolo((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if antiorario and dt < 0:
        dt += 2 * math.pi
    elif not antiorario and dt > 0:
        dt -= 2 * math.pi
    if math.isclose(rx, ry, rel_tol=1e-9):
        return [(x0, y0, math.tan(dt / 4))]
    punti: list[tuple[float, float, float]] = []
    for passo in range(_PASSI_DI_CURVA):
        t = t1 + dt * passo / _PASSI_DI_CURVA
        ex, ey = rx * math.cos(t), ry * math.sin(t)
        punti.append((cos_p * ex - sin_p * ey + cx, sin_p * ex + cos_p * ey + cy, 0.0))
    return punti


def _percorso(d: str) -> list[tuple[list[Vertice], bool]]:
    """I sottopercorsi di un `d` SVG, nel sistema del DXF: vertici e chiusura."""
    token = [(c or n) for c, n in _TOKEN.findall(d)]
    sotto: list[tuple[list[Vertice], bool]] = []
    vertici: list[Vertice] = []
    x = y = 0.0
    inizio = (0.0, 0.0)
    comando = ""
    i = 0

    def numeri(quanti: int) -> list[float]:
        nonlocal i
        valori = [float(item) for item in token[i : i + quanti]]
        if len(valori) != quanti:
            raise ValueError(f"percorso SVG troncato: {d!r}")
        i += quanti
        return valori

    def chiudi(chiuso: bool) -> None:
        """Il sottopercorso finisce nel punto corrente; chiuso, torna al primo
        vertice, che non si ripete."""
        nonlocal vertici
        if vertici:
            vertici.append((x, _y(y), 0.0))
            if chiuso and len(vertici) > 1 and vertici[-1][:2] == vertici[0][:2]:
                vertici.pop()
            sotto.append((vertici, chiuso))
        vertici = []

    while i < len(token):
        if re.fullmatch(r"[A-Za-z]", token[i]):
            comando = token[i]
            i += 1
        relativo = comando.islower()
        base_x, base_y = (x, y) if relativo else (0.0, 0.0)
        maiuscolo = comando.upper()
        if maiuscolo == "M":
            chiudi(False)
            px, py = numeri(2)
            x, y = base_x + px, base_y + py
            inizio = (x, y)
            comando = "l" if relativo else "L"
        elif maiuscolo == "L":
            px, py = numeri(2)
            vertici.append((x, _y(y), 0.0))
            x, y = base_x + px, base_y + py
        elif maiuscolo == "H":
            (px,) = numeri(1)
            vertici.append((x, _y(y), 0.0))
            x = base_x + px
        elif maiuscolo == "V":
            (py,) = numeri(1)
            vertici.append((x, _y(y), 0.0))
            y = base_y + py
        elif maiuscolo == "A":
            rx, ry, phi, grande, verso, px, py = numeri(7)
            nx, ny = base_x + px, base_y + py
            vertici.extend(
                _arco(x, _y(y), rx, ry, -phi, bool(grande), bool(verso), nx, _y(ny))
            )
            x, y = nx, ny
        elif maiuscolo == "Q":
            qx, qy, px, py = numeri(4)
            cx, cy = base_x + qx, base_y + qy
            nx, ny = base_x + px, base_y + py
            for passo in range(_PASSI_DI_CURVA):
                t = passo / _PASSI_DI_CURVA
                bx = (1 - t) ** 2 * x + 2 * (1 - t) * t * cx + t * t * nx
                by = (1 - t) ** 2 * y + 2 * (1 - t) * t * cy + t * t * ny
                vertici.append((bx, _y(by), 0.0))
            x, y = nx, ny
        elif maiuscolo == "Z":
            chiudi(True)
            x, y = inizio
        else:
            raise ValueError(f"comando SVG che il DXF non sa scrivere: {comando!r} in {d!r}")
    chiudi(False)
    return [(item, chiuso) for item, chiuso in sotto if len(item) >= 2 or chiuso]


def _rettangolo(elemento: ElementTree.Element) -> str:
    x = float(elemento.get("x", 0))
    y = float(elemento.get("y", 0))
    w = float(elemento.get("width", 0))
    h = float(elemento.get("height", 0))
    r = min(float(elemento.get("rx", 0) or 0), w / 2, h / 2)
    if r <= 0:
        return f"M{x} {y} L{x + w} {y} L{x + w} {y + h} L{x} {y + h} Z"
    return (
        f"M{x + r} {y} L{x + w - r} {y} A{r} {r} 0 0 1 {x + w} {y + r} "
        f"L{x + w} {y + h - r} A{r} {r} 0 0 1 {x + w - r} {y + h} "
        f"L{x + r} {y + h} A{r} {r} 0 0 1 {x} {y + h - r} "
        f"L{x} {y + r} A{r} {r} 0 0 1 {x + r} {y} Z"
    )


def _elemento(elemento: ElementTree.Element, dove: list[Primitiva]) -> None:
    """Un elemento del corpo come primitive: la linea, il cerchio, il percorso
    e il rettangolo, che e' un percorso con gli angoli eventualmente tondi."""
    tag = elemento.tag.rpartition("}")[2]
    pieno = elemento.get("fill") in _PIENO
    if tag == "line":
        dove.append(
            Segmento(
                float(elemento.get("x1", 0)), _y(float(elemento.get("y1", 0))),
                float(elemento.get("x2", 0)), _y(float(elemento.get("y2", 0))),
            )
        )
    elif tag == "circle":
        dove.append(
            Cerchio(
                float(elemento.get("cx", 0)), _y(float(elemento.get("cy", 0))),
                float(elemento.get("r", 0)), pieno,
            )
        )
    elif tag in ("path", "rect"):
        d = elemento.get("d", "") if tag == "path" else _rettangolo(elemento)
        sotto = _percorso(d)
        if pieno:
            dove.append(Riempimento(tuple(tuple(item) for item, _ in sotto)))
        dove.extend(Polilinea(tuple(item), chiuso) for item, chiuso in sotto)
    elif tag == "g":
        if elemento.get("transform"):
            raise ValueError("un gruppo trasformato nel corpo di un simbolo")
        for figlio in elemento:
            _elemento(figlio, dove)
    else:
        raise ValueError(f"elemento SVG che il DXF non sa scrivere: <{tag}>")


def corpo_del_simbolo(body: str) -> Corpo:
    """Il corpo SVG di un simbolo, com'e' nella libreria, nel sistema del DXF.

    I gruppi `data-glyph` — le lettere che la tavola tiene diritte — escono a
    parte, ciascuno con le sue primitive: diventano un blocco inserito diritto."""
    radice = ElementTree.fromstring(f'<g xmlns="http://www.w3.org/2000/svg">{body}</g>')
    corpo = Corpo()
    for elemento in radice:
        glifo = elemento.get("data-glyph")
        if glifo is None:
            _elemento(elemento, corpo.primitive)
            continue
        dove = corpo.glifi.setdefault(glifo, [])
        for figlio in elemento:
            _elemento(figlio, dove)
    return corpo


def _spostate(primitive: Sequence[Primitiva], dx: float, dy: float) -> list[Primitiva]:
    """Le primitive traslate: serve a centrare una lettera sul suo punto."""

    def v(vertici: Sequence[Vertice]) -> tuple[Vertice, ...]:
        return tuple((x + dx, y + dy, b) for x, y, b in vertici)

    spostate: list[Primitiva] = []
    for item in primitive:
        if isinstance(item, Segmento):
            spostate.append(Segmento(item.x1 + dx, item.y1 + dy, item.x2 + dx, item.y2 + dy))
        elif isinstance(item, Cerchio):
            spostate.append(Cerchio(item.cx + dx, item.cy + dy, item.r, item.pieno))
        elif isinstance(item, Polilinea):
            spostate.append(Polilinea(v(item.vertici), item.chiusa))
        else:
            spostate.append(Riempimento(tuple(v(contorno) for contorno in item.contorni)))
    return spostate


# --- la trasformazione di un inserimento ---------------------------------------------


@dataclass(frozen=True)
class Inserimento:
    """Dove e come si inserisce un blocco: punto, rotazione antioraria, specchio."""

    x: float
    y: float
    rotazione: float
    specchiato: bool


def _giro(
    x: float, y: float, gradi: int, specchiato: bool, larghezza: float, altezza: float
) -> tuple[float, float]:
    """Un punto del corpo diritto, nel corpo girato: la stessa matrice di
    `Symbol.rotated` — lo specchio prima, attorno alla verticale del riquadro,
    poi la rotazione oraria con y in basso."""
    if specchiato:
        x = larghezza - x
    if gradi == 90:
        return altezza - y, x
    if gradi == 180:
        return larghezza - x, altezza - y
    if gradi == 270:
        return y, larghezza - x
    return x, y


def inserimento_del_simbolo(
    origine: Point, gradi: int, specchiato: bool, larghezza: float, altezza: float,
    altezza_foglio: float,
) -> Inserimento:
    """L'inserimento che porta il blocco dove la tavola porta il simbolo.

    Il blocco ha il corpo diritto con y in alto (`x`, `-y` del corpo SVG); la
    tavola lo mette girato e specchiato, con l'angolo in alto a sinistra del
    riquadro girato in `origine`. Si legge la trasformazione su tre punti e se
    ne ricavano punto, rotazione e specchio: niente casi da tenere allineati a
    mano con `Symbol.rotated`."""

    def nel_foglio(bx: float, by: float) -> tuple[float, float]:
        rx, ry = _giro(bx, -by, gradi, specchiato, larghezza, altezza)
        return origine.x_mm + rx, altezza_foglio - (origine.y_mm + ry)

    x0, y0 = nel_foglio(0, 0)
    x1, y1 = nel_foglio(1, 0)
    x2, y2 = nel_foglio(0, 1)
    ax, ay = x1 - x0, y1 - y0
    bx, by = x2 - x0, y2 - y0
    specchio = ax * by - ay * bx < 0
    if specchio:
        ax, ay = -ax, -ay
    rotazione = round(math.degrees(math.atan2(ay, ax))) % 360
    return Inserimento(x0, y0, float(rotazione), specchio)


# --- lo scrittore ----------------------------------------------------------------------


@contextlib.contextmanager
def _metadati_fissi() -> Iterator[None]:
    """Il DXF esce uguale byte per byte, come l'SVG: senza, ezdxf scrive la data
    e due identificativi casuali a ogni salvataggio. Con l'opzione le date sono
    quelle fisse di ezdxf (1 gennaio 2000): AutoCAD le mostra solo nelle
    proprieta' del disegno."""
    from ezdxf._options import options

    prima = options.write_fixed_meta_data_for_testing
    options.write_fixed_meta_data_for_testing = True
    try:
        yield
    finally:
        options.write_fixed_meta_data_for_testing = prima


def _classi_in_ordine(doc: "Drawing") -> None:
    """Le classi del file (sezione CLASSES) in ordine di nome.

    ezdxf le registra scorrendo un insieme dei tipi in uso, e l'ordine di un
    insieme di stringhe cambia da un processo all'altro (`PYTHONHASHSEED`):
    senza riordinarle, lo stesso piano dava due file diversi in due esecuzioni
    (misurato, `docs/collaudi/REL-004/`). Si registrano tutte prima di salvare
    — al salvataggio ezdxf non ne aggiunge altre — e si mettono in fila. Il
    DXF le nomina per nome, non per posizione: l'ordine non cambia il disegno."""
    doc.commit_pending_changes()
    doc.classes.add_required_classes(doc.dxfversion)
    ordinate = sorted(doc.classes.classes.items())
    doc.classes.classes.clear()
    doc.classes.classes.update(ordinate)


def _nome_del_tipo_di_linea(tratto: str) -> str:
    return "NOVEC_TRATTO_" + "_".join(
        parte.replace(".", "P") for parte in re.split(r"[ ,]+", tratto.strip())
    )


class _Tavola:
    def __init__(
        self, sheet: SheetGeometry, frame: SheetFrame, symbols: SymbolRegistry
    ) -> None:
        from ezdxf import units
        from ezdxf.filemanagement import new

        self.sheet = sheet
        self.frame = frame
        self.standard = frame.standard
        self.symbols = symbols
        self.larghezza = self.standard.sheet_width_mm
        self.altezza = self.standard.sheet_height_mm
        self.doc = new(DXF_VERSION, setup=False, units=units.MM)
        self.msp = self.doc.modelspace()
        self.blocchi: set[str] = set()
        self._intestazione()
        self._stili()
        self.carta = self._presentazione()

    # -- impianto del documento --

    def _intestazione(self) -> None:
        header = self.doc.header
        header["$MEASUREMENT"] = 1
        header["$LTSCALE"] = 1.0
        header["$PSLTSCALE"] = 1
        header["$CELTSCALE"] = 1.0
        header["$LWDISPLAY"] = 1

    def _stili(self) -> None:
        normale = self.doc.styles.add(STILE_TESTO, font="arial.ttf")
        normale.set_extended_font_data("Arial", italic=False, bold=False)
        grassetto = self.doc.styles.add(STILE_TESTO_GRASSETTO, font="arialbd.ttf")
        grassetto.set_extended_font_data("Arial", italic=False, bold=True)
        self.doc.header["$TEXTSTYLE"] = STILE_TESTO

    def p(self, x: float, y: float) -> tuple[float, float]:
        """Un punto della tavola (y in basso) nello spazio modello (y in alto)."""
        return x, self.altezza - y

    def tipo_di_linea(self, tratto: str) -> str:
        if tratto == "none":
            return "Continuous"
        nome = _nome_del_tipo_di_linea(tratto)
        if nome not in self.doc.linetypes:
            valori = [float(item) for item in re.split(r"[ ,]+", tratto.strip())]
            motivo = [v if indice % 2 == 0 else -v for indice, v in enumerate(valori)]
            self.doc.linetypes.add(
                nome,
                pattern=[sum(valori), *motivo],
                description="Tratteggio della tavola: " + " / ".join(f"{v:g}" for v in valori)
                + " mm",
            )
        return nome

    def layer(
        self, nome: str, descrizione: str, colore: str | None = None,
        tratto: str = "none", spessore_mm: float | None = None, stampa: bool = True,
    ) -> str:
        if nome in self.doc.layers:
            return nome
        layer = self.doc.layers.add(nome)
        if colore is None:
            layer.color = NERO
        else:
            colora(layer, colore)
        layer.dxf.linetype = self.tipo_di_linea(tratto)
        layer.dxf.lineweight = lineweight(
            self.standard.line_thin_mm if spessore_mm is None else spessore_mm
        )
        if not stampa:
            layer.dxf.plot = 0
        layer.description = descrizione
        return nome

    def layer_della_rete(self, route: RoutedTrunk) -> str:
        colore, tratto = style_for(route.medium, route.supply)
        nome = layer_della_rete(route.medium, route.supply)
        fluido = MEDIUM_NAMES.get(route.medium, route.medium)
        verso = "andata" if route.supply else RETURN_NAMES.get(route.medium, "ritorno")
        return self.layer(
            nome, f"{fluido} — {verso}", colore, tratto, self.standard.line_medium_mm
        )

    def layer_di_servizio(self) -> None:
        thin, medium = self.standard.line_thin_mm, self.standard.line_medium_mm
        self.layer(LAYER_SIMBOLI, "Simboli dei componenti", None, "none", medium)
        self.layer(LAYER_SIGLE, "Sigle e richiami", None, "none", thin)
        self.layer(LAYER_TESTI, "Testi e rimandi", None, "none", thin)
        self.layer(LAYER_LEGENDA, "Legenda", None, "none", thin)
        self.layer(LAYER_CARTIGLIO, "Squadratura e cartiglio", None, "none", thin)
        self.layer(
            LAYER_FINESTRA, "Finestra della presentazione (non si stampa)", None, "none",
            thin, stampa=False,
        )

    # -- i blocchi --

    def _primitive_nel_blocco(self, blocco: "BaseLayout", primitive: Sequence[Primitiva]) -> None:
        """Le primitive dentro un blocco: layer 0, colore e spessore DaBlocco,
        tipo di linea continuo esplicito — un simbolo su una rete tratteggiata
        resta pieno."""
        from ezdxf import const

        attributi = {
            "layer": "0",
            "color": const.BYBLOCK,
            "lineweight": const.LINEWEIGHT_BYBLOCK,
            "linetype": "Continuous",
        }
        for item in primitive:
            if isinstance(item, Segmento):
                blocco.add_line((item.x1, item.y1), (item.x2, item.y2), dxfattribs=attributi)
            elif isinstance(item, Cerchio):
                if item.pieno:
                    self._disco(blocco, item.cx, item.cy, item.r, attributi)
                blocco.add_circle((item.cx, item.cy), item.r, dxfattribs=attributi)
            elif isinstance(item, Polilinea):
                blocco.add_lwpolyline(
                    [(x, y, 0, 0, b) for x, y, b in item.vertici],
                    format="xyseb", close=item.chiusa, dxfattribs=attributi,
                )
            else:
                campitura = blocco.add_hatch(dxfattribs=attributi)
                campitura.set_solid_fill(color=const.BYBLOCK)
                for contorno in item.contorni:
                    campitura.paths.add_polyline_path(
                        [(x, y, b) for x, y, b in contorno], is_closed=True
                    )

    @staticmethod
    def _disco(
        blocco: "BaseLayout", cx: float, cy: float, r: float, attributi: dict[str, object]
    ) -> None:
        from ezdxf import const

        campitura = blocco.add_hatch(dxfattribs=attributi)
        campitura.set_solid_fill(color=const.BYBLOCK)
        campitura.paths.add_polyline_path(
            [(cx - r, cy, 1.0), (cx + r, cy, 1.0)], is_closed=True
        )

    def blocco_del_simbolo(self, symbol_id: str) -> str:
        nome = nome_del_blocco(symbol_id)
        if nome in self.blocchi:
            return nome
        simbolo = self.symbols.get(symbol_id)
        corpo = corpo_del_simbolo(simbolo.body)
        blocco = self.doc.blocks.new(nome, dxfattribs={"description": simbolo.manifest.name})
        self._primitive_nel_blocco(blocco, corpo.primitive)
        for glifo in simbolo.manifest.upright_glyphs:
            nome_glifo = f"{nome}_{glifo.id.capitalize()}"
            lettera = self.doc.blocks.new(
                nome_glifo,
                dxfattribs={"description": f"{simbolo.manifest.name}: lettera, sempre diritta"},
            )
            self._primitive_nel_blocco(
                lettera, _spostate(corpo.glifi.get(glifo.id, []), -glifo.x_mm, glifo.y_mm)
            )
            self.blocchi.add(nome_glifo)
        self.blocchi.add(nome)
        return nome

    def blocco_della_freccia(self) -> str:
        if BLOCCO_FRECCIA not in self.blocchi:
            from ezdxf import const

            blocco = self.doc.blocks.new(
                BLOCCO_FRECCIA, dxfattribs={"description": "Freccia del verso del flusso"}
            )
            campitura = blocco.add_hatch(
                dxfattribs={"layer": "0", "color": const.BYBLOCK}
            )
            campitura.set_solid_fill(color=const.BYBLOCK)
            campitura.paths.add_polyline_path(
                [(0, 0), (-ARROW_LENGTH_MM, ARROW_HALF_WIDTH_MM),
                 (-ARROW_LENGTH_MM, -ARROW_HALF_WIDTH_MM)],
                is_closed=True,
            )
            self.blocchi.add(BLOCCO_FRECCIA)
        return BLOCCO_FRECCIA

    def blocco_del_pallino(self) -> str:
        if BLOCCO_PALLINO not in self.blocchi:
            from ezdxf import const

            raggio = JUNCTION_DOT_WIDTHS * self.standard.line_medium_mm / 2
            blocco = self.doc.blocks.new(
                BLOCCO_PALLINO, dxfattribs={"description": "Pallino di collegamento"}
            )
            self._disco(blocco, 0.0, 0.0, raggio, {"layer": "0", "color": const.BYBLOCK})
            self.blocchi.add(BLOCCO_PALLINO)
        return BLOCCO_PALLINO

    # -- lo spazio modello --

    def testo(
        self, testo: str, x: float, y: float, corpo_mm: float, layer: str,
        allineamento: str = "start", grassetto: bool = False, colore: str | None = None,
        opacita: float = 1.0, dove: "BaseLayout | None" = None,
    ) -> None:
        from ezdxf.enums import TextEntityAlignment

        if not testo:
            return
        attributi: dict[str, object] = {
            "layer": layer,
            "height": round(corpo_mm * ALTEZZA_MAIUSCOLE_EM, 4),
            "style": STILE_TESTO_GRASSETTO if grassetto else STILE_TESTO,
        }
        spazio = self.msp if dove is None else dove
        entita = spazio.add_text(_testo(testo), dxfattribs=attributi)
        if colore is not None:
            colora(entita, colore)
        if opacita < 1:
            entita.transparency = 1 - opacita
        allinea = {
            "start": TextEntityAlignment.LEFT,
            "middle": TextEntityAlignment.CENTER,
            "end": TextEntityAlignment.RIGHT,
        }[allineamento]
        entita.set_placement(self.p(x, y), align=allinea)

    def rettangolo(
        self, rect: Rect, layer: str, spessore_mm: float | None = None,
        colore: str | None = None, dove: "BaseLayout | None" = None,
    ) -> None:
        x0, y0 = self.p(rect.x_mm, rect.y_mm)
        x1, y1 = self.p(rect.right_mm, rect.bottom_mm)
        attributi: dict[str, object] = {"layer": layer}
        if spessore_mm is not None:
            attributi["lineweight"] = lineweight(spessore_mm)
        spazio = self.msp if dove is None else dove
        entita = spazio.add_lwpolyline(
            [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs=attributi
        )
        if colore is not None:
            colora(entita, colore)

    def reti(self) -> None:
        from ezdxf import const

        marks = sheet_marks(self.sheet)
        for index, route in enumerate(self.sheet.routes):
            layer = self.layer_della_rete(route)
            attributi: dict[str, object] = {"layer": layer}
            if route.unresolved:
                attributi["linetype"] = self.tipo_di_linea(UNRESOLVED_RUN_DASH)
            hops = [mark.at for mark in marks.hops if mark.route_index == index]
            for segment in route.segments:
                for piece in _interrupted(segment, hops):
                    polilinea = self.msp.add_lwpolyline(
                        [self.p(item.x_mm, item.y_mm) for item in piece],
                        dxfattribs=attributi,
                    )
                    # Il tratteggio prosegue sui vertici (PLINEGEN): senza,
                    # AutoCAD lo ricomincia a ogni piega.
                    polilinea.dxf.flags = polilinea.dxf.flags | const.LWPOLYLINE_PLINEGEN
                for point in hops:
                    if any(
                        _hoppable(before, after, point)
                        for before, after in zip(segment, segment[1:], strict=False)
                    ):
                        # L'archetto e' sempre pieno: tratteggiato, due
                        # millimetri e mezzo spariscono (come nell'SVG).
                        centro = self.p(point.x_mm, point.y_mm)
                        self.msp.add_arc(
                            centro, CROSSING_ARC_RADIUS_MM, 270, 90,
                            dxfattribs={"layer": layer, "linetype": "Continuous"},
                        )
                if route.flow_kind is not FlowKind.STATIC:
                    freccia = flow_arrow_at(segment, route.flow_from_start)
                    if freccia is not None:
                        tip_x, tip_y, dx, dy = freccia
                        self.msp.add_blockref(
                            self.blocco_della_freccia(), self.p(tip_x, tip_y),
                            dxfattribs={
                                "layer": layer,
                                "rotation": math.degrees(math.atan2(-dy, dx)) % 360,
                            },
                        )

    def _freccia_del_glifo(
        self, glyph: FlowGlyph, face: PortFace, flow: str | None, ox: float, oy: float,
        scala: float = 1.0,
    ) -> None:
        """La freccia di verso di una porta: la stessa di `glyphs.flow_glyph_path`,
        con il blocco della freccia scalato sulla sua misura."""
        if flow == PortFlow.BIDIRECTIONAL.value:
            return
        outward = _DIRECTION[face]
        sign = -1.0 if flow == PortFlow.IN.value else 1.0
        along = (outward[0] * sign, outward[1] * sign)
        half = glyph.length_mm / 2
        tip = (ox + (glyph.x_mm + along[0] * half) * scala, oy + (glyph.y_mm + along[1] * half) * scala)
        self.msp.add_blockref(
            self.blocco_della_freccia(), self.p(*tip),
            dxfattribs={
                "layer": LAYER_SIMBOLI,
                "rotation": math.degrees(math.atan2(-along[1], along[0])) % 360,
                "xscale": glyph.length_mm / ARROW_LENGTH_MM * scala,
                "yscale": glyph.half_width_mm / ARROW_HALF_WIDTH_MM * scala,
            },
        )

    def simboli(self) -> None:
        for placed in self.sheet.symbols:
            diritto = self.symbols.get(placed.symbol_id)
            girato: Symbol = diritto.rotated(placed.rotation_deg, placed.specchiato)
            nome = self.blocco_del_simbolo(placed.symbol_id)
            dove = inserimento_del_simbolo(
                placed.origin, placed.rotation_deg, placed.specchiato,
                diritto.manifest.width_mm, diritto.manifest.height_mm, self.altezza,
            )
            attributi: dict[str, object] = {
                "layer": LAYER_SIMBOLI,
                "rotation": dove.rotazione,
                "xscale": -1.0 if dove.specchiato else 1.0,
            }
            if diritto.manifest.stroke_weight is not StrokeWeight.MEDIUM:
                attributi["lineweight"] = lineweight(
                    self.standard.line_mm(diritto.manifest.stroke_weight)
                )
            self.msp.add_blockref(nome, (dove.x, dove.y), dxfattribs=attributi)
            for glifo in girato.manifest.upright_glyphs:
                self.msp.add_blockref(
                    f"{nome}_{glifo.id.capitalize()}",
                    self.p(placed.origin.x_mm + glifo.x_mm, placed.origin.y_mm + glifo.y_mm),
                    dxfattribs={"layer": LAYER_SIMBOLI},
                )
            for glyph in girato.manifest.flow_glyphs:
                self._freccia_del_glifo(
                    glyph, girato.manifest.port(glyph.port).face,
                    placed.port_flows.get(glyph.port), placed.origin.x_mm, placed.origin.y_mm,
                )

    def pallini(self) -> None:
        for mark in sheet_marks(self.sheet).junctions:
            route = self.sheet.routes[mark.route_index]
            self.msp.add_blockref(
                self.blocco_del_pallino(), self.p(mark.at.x_mm, mark.at.y_mm),
                dxfattribs={"layer": self.layer_della_rete(route)},
            )

    def sigle(self) -> None:
        for label in self.sheet.labels:
            if label.leader_from is not None:
                self.msp.add_line(
                    self.p(label.leader_from.x_mm, label.leader_from.y_mm),
                    self.p(label.anchor.x_mm, label.anchor.y_mm),
                    dxfattribs={"layer": LAYER_SIGLE},
                )
            self.testo(
                label.text, label.anchor.x_mm, label.anchor.y_mm,
                self.standard.text_small_mm, LAYER_SIGLE,
            )

    def legenda(self) -> None:
        self.rettangolo(self.frame.legend_rect_mm, LAYER_LEGENDA)
        for entry in self.sheet.legend:
            simbolo = self.symbols.get(entry.symbol_id)
            manifest = simbolo.manifest
            scala = min(1.0, LEGEND_SWATCH_MM / manifest.width_mm, LEGEND_SWATCH_MM / manifest.height_mm)
            top = entry.anchor.y_mm - LEGEND_SWATCH_MM
            left = entry.anchor.x_mm + (LEGEND_SWATCH_MM - manifest.width_mm * scala) / 2
            middle = top + (LEGEND_SWATCH_MM - manifest.height_mm * scala) / 2
            nome = self.blocco_del_simbolo(entry.symbol_id)
            self.msp.add_blockref(
                nome, self.p(left, middle),
                dxfattribs={
                    "layer": LAYER_LEGENDA,
                    "xscale": scala,
                    "yscale": scala,
                    "lineweight": lineweight(self.standard.legend_line_mm(manifest.stroke_weight)),
                },
            )
            for glifo in manifest.upright_glyphs:
                self.msp.add_blockref(
                    f"{nome}_{glifo.id.capitalize()}",
                    self.p(left + glifo.x_mm * scala, middle + glifo.y_mm * scala),
                    dxfattribs={
                        "layer": LAYER_LEGENDA,
                        "xscale": scala,
                        "yscale": scala,
                        "lineweight": lineweight(self.standard.legend_line_mm(manifest.stroke_weight)),
                    },
                )
            for glyph in manifest.flow_glyphs:
                self._freccia_del_glifo(
                    glyph, manifest.port(glyph.port).face, None, left, middle, scala
                )
            self.testo(
                entry.name,
                entry.anchor.x_mm + LEGEND_SWATCH_MM + LEGEND_TEXT_GAP_MM,
                top + LEGEND_SWATCH_MM / 2 + self.standard.text_small_mm / 2,
                self.standard.text_small_mm, LAYER_LEGENDA,
            )
        for key in self.sheet.network_keys:
            # Il campione porta colore, tratteggio e spessore sull'oggetto: la
            # legenda resta intera anche con il layer della rete spento.
            linea = self.msp.add_line(
                self.p(key.anchor.x_mm, key.anchor.y_mm - 1),
                self.p(key.anchor.x_mm + LEGEND_SWATCH_MM, key.anchor.y_mm - 1),
                dxfattribs={
                    "layer": LAYER_LEGENDA,
                    "linetype": self.tipo_di_linea(key.dash),
                    "lineweight": lineweight(self.standard.line_medium_mm),
                },
            )
            colora(linea, key.colour)
            self.testo(
                key.name, key.anchor.x_mm + LEGEND_SWATCH_MM + LEGEND_TEXT_GAP_MM,
                key.anchor.y_mm, self.standard.text_small_mm, LAYER_LEGENDA,
            )

    def rimandi(self) -> None:
        for reference in self.sheet.cross_references:
            self.msp.add_circle(
                self.p(reference.anchor.x_mm, reference.anchor.y_mm),
                CROSS_REFERENCE_RADIUS_MM, dxfattribs={"layer": LAYER_TESTI},
            )
            self.testo(
                reference.text, reference.anchor.x_mm + CROSS_REFERENCE_RADIUS_MM + 1,
                reference.anchor.y_mm, self.standard.text_small_mm, LAYER_TESTI,
            )

    def riserva_senza_cartiglio(self) -> None:
        """La squadratura e la riserva del cartiglio, in spazio carta come il
        cartiglio."""
        self.rettangolo(
            self.frame.border_rect_mm, LAYER_CARTIGLIO, self.standard.line_medium_mm,
            dove=self.carta,
        )
        self.rettangolo(self.frame.title_block_rect_mm, LAYER_CARTIGLIO, dove=self.carta)
        self.testo(
            self.sheet.title, self.frame.header_rect_mm.x_mm + 2,
            self.frame.header_rect_mm.bottom_mm - 1, self.standard.text_small_mm,
            LAYER_CARTIGLIO, dove=self.carta,
        )
        self.testo(
            DRAFT_MARK, self.frame.title_block_rect_mm.x_mm + 2,
            self.frame.title_block_rect_mm.y_mm + self.standard.text_normal_mm + 1,
            self.standard.text_normal_mm, LAYER_CARTIGLIO, dove=self.carta,
        )

    def cartiglio(self, tavola: CartiglioDellaTavola) -> str:
        """Il cartiglio, riletto dal frammento SVG che `cartiglio.py` disegna:
        cosi' e' lo stesso della tavola, misurato e impaginato una volta sola.
        Sta in **spazio carta**, con la squadratura: nello spazio modello resta
        lo schema, che si copia in un altro disegno senza portarsi dietro il
        cartiglio. Torna il nome del file del logo, che va scritto accanto al
        DXF."""
        from ezdxf.colors import RGB

        disegnato = disegna_cartiglio(tavola, self.frame, stati_della_tavola(self.sheet))
        radice = ElementTree.fromstring(
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink">{disegnato.svg}</svg>'
        )
        logo = tavola.cartiglio.modello.logo()

        def visita(nodo: ElementTree.Element, dx: float, dy: float) -> None:
            for elemento in nodo:
                tag = elemento.tag.rpartition("}")[2]
                if tag == "g":
                    mossa = re.fullmatch(
                        rf"translate\(({_NUMERO})[ ,]+({_NUMERO})\)",
                        (elemento.get("transform") or "translate(0 0)").strip(),
                    )
                    if mossa is None:
                        raise ValueError("un gruppo del cartiglio con una trasformazione ignota")
                    visita(elemento, dx + float(mossa.group(1)), dy + float(mossa.group(2)))
                elif tag == "rect":
                    rect = Rect(
                        x_mm=float(elemento.get("x", 0)) + dx,
                        y_mm=float(elemento.get("y", 0)) + dy,
                        width_mm=float(elemento.get("width", 0)),
                        height_mm=float(elemento.get("height", 0)),
                    )
                    riempimento = elemento.get("fill", "none")
                    if riempimento != "none":
                        x0, y0 = self.p(rect.x_mm, rect.y_mm)
                        x1, y1 = self.p(rect.right_mm, rect.bottom_mm)
                        campitura = self.carta.add_hatch(dxfattribs={"layer": LAYER_CARTIGLIO})
                        campitura.set_solid_fill(
                            color=aci_vicino(rgb(riempimento)), rgb=RGB(*rgb(riempimento))
                        )
                        campitura.paths.add_polyline_path(
                            [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], is_closed=True
                        )
                        opacita = float(elemento.get("fill-opacity", 1))
                        if opacita < 1:
                            campitura.transparency = 1 - opacita
                    if elemento.get("stroke", "none") != "none":
                        self.rettangolo(
                            rect, LAYER_CARTIGLIO, float(elemento.get("stroke-width", 0)),
                            elemento.get("stroke"), dove=self.carta,
                        )
                elif tag == "line":
                    linea = self.carta.add_line(
                        self.p(float(elemento.get("x1", 0)) + dx, float(elemento.get("y1", 0)) + dy),
                        self.p(float(elemento.get("x2", 0)) + dx, float(elemento.get("y2", 0)) + dy),
                        dxfattribs={
                            "layer": LAYER_CARTIGLIO,
                            "lineweight": lineweight(float(elemento.get("stroke-width", 0))),
                        },
                    )
                    colora(linea, elemento.get("stroke", "#000000"))
                elif tag == "text":
                    self.testo(
                        elemento.text or "",
                        float(elemento.get("x", 0)) + dx, float(elemento.get("y", 0)) + dy,
                        float(elemento.get("font-size", 0)), LAYER_CARTIGLIO,
                        elemento.get("text-anchor", "start"),
                        elemento.get("font-weight") == "bold",
                        elemento.get("fill"), float(elemento.get("fill-opacity", 1)),
                        dove=self.carta,
                    )
                elif tag == "image":
                    x = float(elemento.get("x", 0)) + dx
                    y = float(elemento.get("y", 0)) + dy
                    larghezza = float(elemento.get("width", 0))
                    altezza = float(elemento.get("height", 0))
                    definizione = self.doc.add_image_def(
                        logo.file, (logo.pixel_larghezza, logo.pixel_altezza)
                    )
                    self.carta.add_image(
                        definizione, self.p(x, y + altezza), (larghezza, altezza),
                        dxfattribs={"layer": LAYER_CARTIGLIO},
                    )
                else:
                    raise ValueError(f"elemento del cartiglio che il DXF non sa scrivere: <{tag}>")

        visita(radice, 0.0, 0.0)
        self.doc.set_raster_variables(frame=0, quality=1, units="mm")
        return logo.file

    # -- la presentazione --

    def _presentazione(self) -> "Paperspace":
        """Il foglio pronto per la stampa: la presentazione del formato, a
        margini zero, 1:1, con una finestra bloccata su tutto il foglio e il
        suo bordo su un layer che non si stampa (Autodesk: «create all viewport
        objects on a separate layer»). Il file **si apre su questa**
        (`$TILEMODE` a 0): si vede la tavola come nel PDF.

        La finestra principale — quella che ogni presentazione ha, e che non si
        vede — ezdxf la mette su un layer `VIEWPORTS` che non definisce: sta
        sul layer 0, come la rimette l'ODA File Converter."""
        formato = _formato(self.larghezza, self.altezza)
        layout = self.doc.layouts.new(formato)
        layout.page_setup(
            size=(self.larghezza, self.altezza), margins=(0, 0, 0, 0), units="mm",
            scale=16, name=f"ISO_full_bleed_{formato}", device="DWG To PDF.pc3",
        )
        principale = layout.main_viewport()
        if principale is not None:
            principale.dxf.layer = "0"
        finestra = layout.add_viewport(
            center=(self.larghezza / 2, self.altezza / 2),
            size=(self.larghezza, self.altezza),
            view_center_point=(self.larghezza / 2, self.altezza / 2),
            view_height=self.altezza,
            dxfattribs={"layer": LAYER_FINESTRA},
        )
        finestra.dxf.flags = finestra.dxf.flags | 16384
        if "Layout1" in self.doc.layouts.names():
            self.doc.layouts.delete("Layout1")
        self.doc.layouts.set_active_layout(formato)
        self.doc.header["$TILEMODE"] = 0
        self.doc.set_modelspace_vport(
            height=self.altezza, center=(self.larghezza / 2, self.altezza / 2)
        )
        return layout


def _formato(larghezza: float, altezza: float) -> str:
    formati = {(420.0, 297.0): "A3", (594.0, 420.0): "A2", (841.0, 594.0): "A1",
               (297.0, 210.0): "A4"}
    return formati.get((larghezza, altezza), f"{larghezza:g}x{altezza:g}")


def write_dxf(
    sheet: SheetGeometry,
    frame: SheetFrame,
    symbols: SymbolRegistry,
    target: Path,
    cartiglio: CartiglioDellaTavola | None = None,
) -> tuple[Path, ...]:
    """Scrive la tavola in DXF e, con il cartiglio, il logo accanto.

    Torna i file scritti. **Deterministico**: la stessa geometria da' lo stesso
    file, byte per byte."""
    target.parent.mkdir(parents=True, exist_ok=True)
    scritti = [target]
    # Dalla creazione al salvataggio: ezdxf scrive la sua firma con l'ora gia'
    # quando crea il documento, non solo quando lo salva.
    with _metadati_fissi():
        tavola = _Tavola(sheet, frame, symbols)
        tavola.layer_di_servizio()
        if cartiglio is None:
            tavola.riserva_senza_cartiglio()
        else:
            logo = target.parent / tavola.cartiglio(cartiglio)
            logo.write_bytes(cartiglio.cartiglio.logo_jpeg)
            scritti.append(logo)
        tavola.reti()
        tavola.simboli()
        tavola.pallini()
        tavola.sigle()
        tavola.legenda()
        tavola.rimandi()
        _classi_in_ordine(tavola.doc)
        tavola.doc.saveas(target)
    return tuple(scritti)


__all__ = [
    "ALTEZZA_MAIUSCOLE_EM",
    "DXF_VERSION",
    "Inserimento",
    "aci_vicino",
    "corpo_del_simbolo",
    "inserimento_del_simbolo",
    "layer_della_rete",
    "lineweight",
    "nome_del_blocco",
    "write_dxf",
]
