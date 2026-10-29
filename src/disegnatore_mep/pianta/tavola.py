"""La tavola della pianta: un disegno, due scrittori.

La tavola si compone **una volta** in primitive — aree, linee, archi, cerchi,
scritte, l'immagine di sfondo — in millimetri di carta, e due scrittori le
traducono: l'SVG (da cui il PDF del motore, `graphics/pdf.py`) e il DXF (con
la presentazione, gli stili e il cartiglio di `graphics/dxf.py`). Cosi' il DXF
e' la stessa tavola dell'SVG, come per lo schema (REL-004).

Il foglio e' quello del motore: squadratura e cartiglio Nove C
(`graphics/cartiglio.py`), A3 o A2. A destra, al posto della fascia della
legenda dello schema, una colonna piu' larga con legenda, tabella delle tratte,
forature e note. Colori e tratteggi dei fluidi sono quelli dello schema
funzionale (`layout/legend.py`): chi passa dallo schema alla pianta riconosce
le linee.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Literal, cast

from disegnatore_mep.graphics.cartiglio import (
    Cartiglio,
    CartiglioDellaTavola,
    NomeCampo,
    disegna_cartiglio,
)
from disegnatore_mep.graphics.frame import SheetFrame
from disegnatore_mep.graphics.standard import (
    A1_LANDSCAPE,
    A2_LANDSCAPE,
    A3_LANDSCAPE,
    CORPO_DELLE_SCRITTE_PT,
    CORPO_MINIMO_PT,
    FAMIGLIA_DELLE_SCRITTE,
    PT_MM,
    GraphicStandard,
)
from disegnatore_mep.layout.legend import MEDIUM_NAMES, MEDIUM_STYLES, a_capo

from .instrada import ORDINE_DEI_FLUIDI, Percorso, chiave_della_tratta, ordine_di_instradamento
from .lunghezze import Lunghezza, Regola, la_regola, metri
from .modello import Foglio, Muro, Pianta
from .scritte import (
    RAGGIO_DEL_NUMERO_MM,
    Ingombri,
    Rettangolo,
    ScrittaPosata,
    Segmento,
    misura,
    posa_accanto,
    posa_dentro,
    posa_intorno,
    posa_nel_pezzo,
)

Punto = tuple[float, float]

SPESSORE_MM: dict[str, float] = {"supply_air": 0.70, "return_air": 0.70}
"""Il canale si legge piu' spesso del tubo, e il tubo piu' del cavo."""
SPESSORE_DEL_TUBO_MM = 0.45
SPESSORE_DEL_CAVO_MM = 0.30
FLUIDI_ELETTRICI = frozenset({"power_supply", "interconnection", "control_bus"})

TRATTO_CEDUTO = "2 1.5"
"""Il tratteggio fitto della tratta non risolta, come nello schema (D-150)."""

COLORE_FUORI = "#f4c27a"
"""La fascia sotto un tratto che corre in controsoffitto dove il controsoffitto
non c'e': si vede a colpo d'occhio, sotto qualunque tratteggio del fluido."""
LARGHEZZA_FUORI_MM = 2.4

COLONNA_MM = 130.0

STACCO_MM = 2.2
"""Il bianco fra due sezioni della colonna."""
"""La colonna di destra: legenda, tabella delle tratte, forature, note."""

MARGINE_MM = 6.0
"""Il bianco fra il disegno e il bordo della sua area."""

FASCIA_DELLA_SCALA_MM = 12.0
"""Sotto la pianta, la barra della scala."""

INTERRUZIONE_MM = 0.9
"""Dove due tracciati si sormontano, quello sotto si interrompe di tanto per
parte: si legge quale passa sopra."""

CORPO_SIGLE_PT = CORPO_DELLE_SCRITTE_PT
CORPO_STANZE_PT = CORPO_DELLE_SCRITTE_PT
CORPO_TRATTE_PT = CORPO_MINIMO_PT
CORPO_COLONNA_PT = CORPO_MINIMO_PT
CORPO_TITOLETTI_PT = CORPO_DELLE_SCRITTE_PT
CORPO_TITOLO_PT = 11.0

COLORE_STANZE = "#1c2e4a"
COLORE_MURI = {"perimetrale": "#8c8c8c", "portante": "#8c8c8c", "tramezza": "#b3b3b3"}
COLORE_APERTURE = "#555555"

FORMATI: dict[str, GraphicStandard] = {"A3": A3_LANDSCAPE, "A2": A2_LANDSCAPE, "A1": A1_LANDSCAPE}
SCALE = (50, 100)

LAYER_MURI = "A-WALL"
LAYER_APERTURE = "A-DOOR"
LAYER_STANZE = "A-AREA-IDEN"
LAYER_PEZZI = "M-EQPM"
LAYER_FORATURE = "A-WALL-HOLE"
LAYER_SIGLE = "M-ANNO-IDEN"
LAYER_TESTI = "M-ANNO-TEXT"
LAYER_COLONNA = "M-ANNO-LEGN"
LAYER_SCALA = "G-ANNO-SCAL"
LAYER_SFONDO = "A-PLAN-RAST"
LAYER_FUORI = "M-ANNO-NCSF"

DESCRIZIONE_DEI_LAYER: dict[str, str] = {
    LAYER_MURI: "Muri della planimetria",
    LAYER_APERTURE: "Porte, finestre, varchi e fori dichiarati",
    LAYER_STANZE: "Nomi delle stanze",
    LAYER_PEZZI: "Pezzi posati: ingombro in pianta",
    LAYER_FORATURE: "Forature da eseguire",
    LAYER_SIGLE: "Sigle, scritte dei tracciati e richiami",
    LAYER_TESTI: "Testi",
    LAYER_COLONNA: "Legenda, tabella delle tratte, forature e note",
    LAYER_SCALA: "Barra della scala",
    LAYER_SFONDO: "Planimetria raster di sfondo",
    LAYER_FUORI: "Tratti in controsoffitto dove il controsoffitto non c'e'",
}

LAYER_ELETTRICI = {
    "power_supply": "E-POWR-CIRC",
    "interconnection": "E-POWR-LINK",
    "control_bus": "E-CTRL-BUS",
}


def stile(fluido: str) -> tuple[str, str]:
    return MEDIUM_STYLES.get(fluido, ("#111111", "none"))


def nome_del_fluido(fluido: str) -> str:
    return MEDIUM_NAMES.get(fluido, fluido)


def spessore(fluido: str) -> float:
    if fluido in SPESSORE_MM:
        return SPESSORE_MM[fluido]
    return SPESSORE_DEL_CAVO_MM if fluido in FLUIDI_ELETTRICI else SPESSORE_DEL_TUBO_MM


def layer_del_fluido(fluido: str) -> str:
    if fluido in LAYER_ELETTRICI:
        return LAYER_ELETTRICI[fluido]
    from disegnatore_mep.graphics.dxf import layer_della_rete

    return layer_della_rete(fluido, True)


# --- le primitive ----------------------------------------------------------------


@dataclass(frozen=True)
class Area:
    punti: tuple[Punto, ...]
    colore: str
    layer: str
    opacita: float = 1.0


@dataclass(frozen=True)
class Linea:
    punti: tuple[Punto, ...]
    colore: str
    spessore: float
    layer: str
    tratto: str = "none"


@dataclass(frozen=True)
class Arco:
    centro: Punto
    raggio: float
    da: Punto
    a: Punto
    orario: bool
    """Sul foglio (y in basso): da `da` ad `a` in senso orario."""
    colore: str
    spessore: float
    layer: str


@dataclass(frozen=True)
class Cerchio:
    centro: Punto
    raggio: float
    colore: str
    spessore: float
    riempimento: str
    layer: str


@dataclass(frozen=True)
class Scritta:
    testo: str
    x: float
    y: float
    corpo_pt: float
    layer: str
    grassetto: bool = False
    colore: str = "#000000"
    ancora: Literal["start", "middle", "end"] = "start"


@dataclass(frozen=True)
class Immagine:
    file: str
    x: float
    y: float
    larghezza: float
    altezza: float
    opacita: float
    pixel: tuple[int, int]


Primitiva = Area | Linea | Arco | Cerchio | Scritta | Immagine


@dataclass(frozen=True)
class Foratura:
    numero: str
    muro: str
    tipo_del_muro: str
    tratte: tuple[str, ...]
    quota: str
    punto: Punto


@dataclass
class Tavola:
    frame: SheetFrame
    formato: str
    scala: int
    primitive: list[Primitiva]
    scritte: list[tuple[str, ScrittaPosata]]
    linee: list[tuple[str, Segmento]]
    rettangoli: list[tuple[str, Rettangolo]]
    cartiglio: CartiglioDellaTavola | None
    avvisi: list[str] = field(default_factory=list)
    ammessi: dict[str, set[str]] = field(default_factory=dict)
    """Per scritta, i rettangoli su cui puo' stare: il muro della foratura."""
    trasforma: tuple[float, float, float, float, float] = (0.0, 0.0, 0.0, 0.0, 1.0)
    """ox, oy, xmin, ymin, k: dalla carta ai metri, x_m = (x_mm - ox) / k + xmin."""

    def in_metri(self, r: Rettangolo) -> tuple[float, float, float, float]:
        ox, oy, xmin, ymin, k = self.trasforma
        return ((r[0] - ox) / k + xmin, (r[1] - oy) / k + ymin, (r[2] - ox) / k + xmin, (r[3] - oy) / k + ymin)


# --- la geometria della pianta -------------------------------------------------


def _asse(muro: Muro) -> tuple[float, float, float]:
    lunghezza = math.dist(muro.da, muro.a)
    return (muro.a[0] - muro.da[0]) / lunghezza, (muro.a[1] - muro.da[1]) / lunghezza, lunghezza


def _sull_asse(muro: Muro, s: float, d: float) -> Punto:
    ux, uy, _ = _asse(muro)
    return (muro.da[0] + ux * s - uy * d, muro.da[1] + uy * s + ux * d)


def pezzi_dei_muri(pianta: Pianta) -> list[tuple[Muro, float, float]]:
    """I tratti pieni di ogni muro: l'asse da s0 a s1, aperture tolte."""
    out: list[tuple[Muro, float, float]] = []
    for muro in pianta.muri:
        _, _, lunghezza = _asse(muro)
        mezzo = muro.spessore / 2
        tagli = []
        for apertura in pianta.aperture:
            if apertura.muro != muro.id:
                continue
            ux, uy, _ = _asse(muro)
            centro = (apertura.centro[0] - muro.da[0]) * ux + (apertura.centro[1] - muro.da[1]) * uy
            tagli.append((centro - apertura.larghezza / 2, centro + apertura.larghezza / 2))
        tratti = [(-mezzo, lunghezza + mezzo)]
        for t0, t1 in sorted(tagli):
            nuovi = []
            for s0, s1 in tratti:
                if t1 <= s0 or t0 >= s1:
                    nuovi.append((s0, s1))
                    continue
                if t0 > s0:
                    nuovi.append((s0, t0))
                if t1 < s1:
                    nuovi.append((t1, s1))
            tratti = nuovi
        out += [(muro, s0, s1) for s0, s1 in tratti if s1 - s0 > 1e-6]
    return out


def estensione(pianta: Pianta, percorsi: Sequence[Percorso]) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []
    for muro in pianta.muri:
        _, _, lunghezza = _asse(muro)
        h = muro.spessore / 2
        for s in (-h, lunghezza + h):
            for d in (-h, h):
                x, y = _sull_asse(muro, s, d)
                xs.append(x)
                ys.append(y)
    for pezzo in pianta.pezzi:
        x0, y0, x1, y1 = pezzo.rettangolo
        xs += [x0, x1]
        ys += [y0, y1]
    for stanza in pianta.stanze:
        xs += [p[0] for p in stanza.poligono]
        ys += [p[1] for p in stanza.poligono]
    for percorso in percorsi:
        xs += [p[0] for linea in percorso.linee for p in linea]
        ys += [p[1] for linea in percorso.linee for p in linea]
    return min(xs), min(ys), max(xs), max(ys)


# --- la colonna ---------------------------------------------------------------------


@dataclass
class _Colonna:
    larghezza: float
    primitive: list[Primitiva] = field(default_factory=list)
    y: float = 0.0

    def riga(self, testo: str, corpo: float = CORPO_COLONNA_PT, grassetto: bool = False,
             rientro: float = 0.0, colore: str = "#000000") -> None:
        corpo_mm = corpo * PT_MM
        for riga in a_capo(testo, self.larghezza - rientro, corpo_mm) or ("",):
            self.y += corpo_mm * 1.2
            self.primitive.append(Scritta(riga, rientro, self.y, corpo, LAYER_COLONNA, grassetto, colore))

    def stacco(self, mm: float) -> None:
        self.y += mm


def colonna(
    pianta: Pianta, percorsi: Sequence[Percorso], lunghe: Sequence[Lunghezza],
    forature: Sequence[Foratura], fori_dei_pezzi: Sequence[tuple[str, str]], scala: int, formato: str,
    regola: Regola | None = None, legenda: Sequence[str] = (), avvisi: Sequence[str] = (),
    ridotta: str | None = None,
) -> _Colonna:
    """La colonna della tavola. `ridotta` e' il nome della tavola intera: la
    colonna di un dettaglio porta legenda, scritte in legenda e note, e rimanda
    alla tavola intera per tratte, forature e avvisi."""
    c = _Colonna(larghezza=COLONNA_MM - 6.0)
    c.riga(pianta.titolo.upper(), CORPO_TITOLO_PT, True)
    c.riga(f"Scala 1:{scala} su {formato} · misure in metri", CORPO_COLONNA_PT)
    c.riga("Percorsi indicativi, da verificare in sopralluogo.", CORPO_COLONNA_PT, True)
    c.stacco(STACCO_MM)

    c.riga("LEGENDA", CORPO_TITOLETTI_PT, True)
    fluidi = sorted(
        {t.fluido for t in pianta.tracciati}, key=lambda f: (ORDINE_DEI_FLUIDI.get(f, 2), f)
    )
    corpo_mm = CORPO_COLONNA_PT * PT_MM
    # Le voci della legenda su due colonne: il segno a sinistra, il testo accanto.
    voci: list[tuple[Any, str]] = []

    def linea(colore: str, larghezza: float, tratto: str = "none") -> Any:
        return lambda x, y: [Linea(((x, y - corpo_mm * 0.3), (x + 10.0, y - corpo_mm * 0.3)), colore,
                                   larghezza, LAYER_COLONNA, tratto)]

    for fluido in fluidi:
        colore, tratto = stile(fluido)
        voci.append((linea(colore, spessore(fluido), tratto), nome_del_fluido(fluido)))
    voci.append((lambda x, y: _rettangolo_con_bordo((x + 1.0, y - corpo_mm * 0.75, x + 9.0, y + corpo_mm * 0.05),
                                                   LAYER_COLONNA), "Pezzo posato: ingombro e sigla"))
    if forature:
        voci.append((lambda x, y: [Cerchio((x + 5.0, y - corpo_mm * 0.35), 0.9, "#000000", 0.25, "#ffffff",
                                           LAYER_COLONNA)], "Foratura (F1, F2…: elenco sotto)"))
    if any(p.fuori for p in percorsi):
        voci.append((linea(COLORE_FUORI, LARGHEZZA_FUORI_MM), "Fuori dal controsoffitto: da verificare"))
    if legenda:
        voci.append((lambda x, y: _numero_cerchiato("1", x + 5.0, y - corpo_mm * 0.35, LAYER_COLONNA),
                     "Scritta in legenda (testo sotto)"))
    if any(p.ceduto for p in percorsi):
        voci.append((linea("#111111", 0.3, TRATTO_CEDUTO), "Tratta non instradata: da rivedere"))
    passo_della_voce = corpo_mm * 1.2 + 1.4
    mezza = c.larghezza / 2 + 1.0
    righe_della_legenda = (len(voci) + 1) // 2
    for indice, (segno, testo) in enumerate(voci):
        colonna_della_voce, riga_della_voce = divmod(indice, righe_della_legenda)
        x = colonna_della_voce * mezza
        y = c.y + (riga_della_voce + 1) * passo_della_voce
        c.primitive += segno(x, y)
        c.primitive.append(Scritta(testo, x + 13.0, y, CORPO_COLONNA_PT, LAYER_COLONNA))
    c.y += righe_della_legenda * passo_della_voce
    c.stacco(STACCO_MM)

    if ridotta is not None:
        c.riga(f"Tratte, lunghezze, forature e avvisi: tavola {ridotta}.", CORPO_COLONNA_PT, True)
        c.stacco(STACCO_MM)
    else:
        _tratte_e_avvisi(c, pianta, lunghe, forature, fori_dei_pezzi, regola, avvisi)
    if legenda:
        c.riga("SCRITTE IN LEGENDA", CORPO_TITOLETTI_PT, True)
        for numero, testo in enumerate(legenda, start=1):
            c.stacco(0.6)
            y = c.y + corpo_mm * 1.2
            c.primitive += _numero_cerchiato(str(numero), RAGGIO_DEL_NUMERO_MM + 0.2, y - corpo_mm * 0.35,
                                             LAYER_COLONNA)
            c.y = y - corpo_mm * 1.2
            c.riga(testo, rientro=6.0)
        c.stacco(STACCO_MM)

    c.riga("NOTE", CORPO_TITOLETTI_PT, True)
    note = [
        "Quote: canali, linee frigo e condensa in controsoffitto; cavi e bus in traccia, salvo dove la "
        "tabella dice altro. Salite e discese stanno nell'aggiunta della regola.",
        "Sigle e numeri di tratta come lo schema funzionale e la distinta.",
        *pianta.note,
    ]
    for numero, nota in enumerate(note, start=1):
        c.riga(f"{numero}. {nota}")
    return c


def _tratte_e_avvisi(
    c: _Colonna, pianta: Pianta, lunghe: Sequence[Lunghezza], forature: Sequence[Foratura],
    fori_dei_pezzi: Sequence[tuple[str, str]], regola: Regola | None, avvisi: Sequence[str],
) -> None:
    corpo_mm = CORPO_COLONNA_PT * PT_MM
    c.riga("TRATTE", CORPO_TITOLETTI_PT, True)
    colonne = (("Tratta", 0.0, "start"), ("Fluido", 11.0, "start"), ("Da", 38.0, "start"),
               ("A", 53.0, "start"), ("Dim.", 68.0, "start"), ("L prog.", 98.0, "end"),
               ("L mis.", 111.0, "end"), ("L quot.", 124.0, "end"))
    c.stacco(1.0)
    c.y += corpo_mm * 1.2
    for testo, x, ancora in colonne:
        c.primitive.append(Scritta(testo, x, c.y, CORPO_COLONNA_PT, LAYER_COLONNA, True,
                                   ancora=cast(Any, ancora)))
    c.primitive.append(Linea(((0.0, c.y + 1.0), (c.larghezza, c.y + 1.0)), "#000000", 0.18, LAYER_COLONNA))
    c.stacco(1.0)
    per_tratta = {lu.tratta: lu for lu in lunghe}
    corta = {
        "supply_air": "Aria di mandata", "return_air": "Aria di ripresa",
        "refrigerant_liquid": "Frigo, liquido", "refrigerant_gas": "Frigo, gas",
        "interconnection": "Cavo UI-UE", "power_supply": "Alimentazione", "control_bus": "Bus",
        "condensate": "Condensa",
    }
    for tracciato in sorted(pianta.tracciati, key=lambda t: chiave_della_tratta(t.tratta)):
        lu = per_tratta[tracciato.tratta]
        c.y += corpo_mm * 1.25
        valori = (
            tracciato.tratta, corta.get(tracciato.fluido, nome_del_fluido(tracciato.fluido)),
            tracciato.estremo_da.pezzo, tracciato.estremo_a.pezzo, tracciato.dimensione or "",
            "—" if lu.data_m is None else metri(lu.data_m),
            metri(lu.misurata_m) + ("!" if lu.oltre_lo_scarto else ""),
            metri(lu.da_quotare_m) + ("*" if lu.minimo_m else "") + ("°" if lu.dalla_misura else ""),
        )
        for testo, (_, x, ancora) in zip(valori, colonne, strict=True):
            c.primitive.append(Scritta(testo, x, c.y, CORPO_COLONNA_PT, LAYER_COLONNA,
                                       ancora=cast(Any, ancora)))
    c.stacco(1.0)
    in_linea = [f"{t.tratta} per {', '.join(t.passa_per)}" for t in pianta.tracciati if t.passa_per]
    regola = regola or la_regola(pianta.maggiorazione)
    numeri = regola.regola
    soglia = round(pianta.parametri.scarto_della_misura * 100)
    minimi = regola.minimi_del_testo()
    c.riga(
        ("Passano per organi in linea: " + "; ".join(in_linea) + ". " if in_linea else "")
        + "L prog. del progettista, si quota; L mis. sul disegno, un controllo "
        f"(! oltre il {soglia} %); L quot. = (L + {metri(float(numeri['aggiunta_m']), 2)} m) × "
        f"{metri(float(numeri['fattore']), 2)} per eccesso a {metri(float(numeri['passo_m']), 2)} m, "
        f"regola {regola.origine}; * minimo"
        + (f" ({', '.join(minimi)})" if minimi else "")
        + "; ° sulla misura, L prog. manca."
    )
    c.stacco(STACCO_MM)

    if avvisi:
        c.riga("AVVISI", CORPO_TITOLETTI_PT, True)
        for avviso in avvisi:
            c.riga(f"– {avviso}")
        c.stacco(STACCO_MM)

    if forature or fori_dei_pezzi:
        c.riga("FORATURE", CORPO_TITOLETTI_PT, True)
        for foratura in forature:
            c.riga(
                f"{foratura.numero} · {' '.join(foratura.tratte)} · {foratura.tipo_del_muro} "
                f"{foratura.muro} · {foratura.quota.replace('_', ' ')}"
            )
        if fori_dei_pezzi:
            per_muro: dict[str, list[str]] = {}
            for sigla, muro in fori_dei_pezzi:
                per_muro.setdefault(muro, []).append(sigla)
            elenco = "; ".join(f"{', '.join(s)} nel muro {m}" for m, s in per_muro.items())
            c.riga(f"Fori per i pezzi a parete: {elenco}.")
        c.stacco(STACCO_MM)


def _numero_cerchiato(testo: str, cx: float, cy: float, layer: str) -> list[Primitiva]:
    """Il numero di una scritta in legenda: un cerchio e la cifra al centro."""
    corpo = CORPO_TRATTE_PT if len(testo) < 2 else CORPO_TRATTE_PT - 1.5
    alto = corpo * PT_MM * 0.72
    return [
        Cerchio((round(cx, 4), round(cy, 4)), RAGGIO_DEL_NUMERO_MM, "#000000", 0.2, "#ffffff", layer),
        Scritta(testo, round(cx, 4), round(cy + alto / 2, 4), corpo, layer, True, ancora="middle"),
    ]


def _rettangolo_con_bordo(r: Rettangolo, layer: str, riempimento: str = "#ffffff") -> list[Primitiva]:
    x0, y0, x1, y1 = r
    angoli = ((x0, y0), (x1, y0), (x1, y1), (x0, y1))
    return [Area(angoli, riempimento, layer), Linea((*angoli, angoli[0]), "#1b2631", 0.25, layer)]


# --- la composizione ---------------------------------------------------------------


def scegli_il_foglio(
    pianta: Pianta, larghezza_m: float, altezza_m: float, altezza_colonna: float,
) -> tuple[str, int, SheetFrame, bool]:
    """Il formato piu' piccolo e la scala piu' grande su cui la pianta e la
    colonna entrano: prima 1:50 su A3, A2, A1, poi 1:100. Torna anche se entra."""
    formati = [pianta.foglio.formato] if pianta.foglio.formato else list(FORMATI)
    scale = [pianta.foglio.scala] if pianta.foglio.scala else list(SCALE)
    primo: tuple[str, int, SheetFrame] | None = None
    for scala in scale:
        for formato in formati:
            frame = SheetFrame(standard=FORMATI[formato], legend_width_mm=COLONNA_MM)
            area = frame.drawing_rect_mm
            k = 1000.0 / scala
            entra = (
                larghezza_m * k + 2 * MARGINE_MM <= area.width_mm
                and altezza_m * k + 2 * MARGINE_MM + FASCIA_DELLA_SCALA_MM <= area.height_mm
                and altezza_colonna + 6.0 <= frame.legend_rect_mm.height_mm
            )
            if primo is None:
                primo = (formato, scala, frame)
            if entra:
                return formato, scala, frame, True
    assert primo is not None
    formato, scala, frame = primo
    return formato, scala, frame, False


def componi(
    pianta: Pianta,
    percorsi: Sequence[Percorso],
    lunghe: Sequence[Lunghezza],
    forature: Sequence[Foratura],
    fori_dei_pezzi: Sequence[tuple[str, str]],
    cartiglio: Cartiglio | None,
    pixel_dello_sfondo: tuple[int, int] | None = None,
    regola: Regola | None = None,
    avvisi_della_colonna: Sequence[str] = (),
    zona: tuple[float, float, float, float] | None = None,
    rimandate: frozenset[str] = frozenset(),
    riquadri: Sequence[tuple[str, tuple[float, float, float, float], int]] = (),
    ridotta: str | None = None,
    nel_dettaglio: frozenset[str] = frozenset(),
) -> Tavola:
    """La tavola intera; con `zona` (in metri) solo quella zona, alla scala del
    foglio della pianta: e' il riquadro di dettaglio. `rimandate` sono le
    scritte che stanno nel dettaglio e qui non si posano; `riquadri` le zone
    dei dettagli, che la tavola intera incornicia e nomina. Nel dettaglio si
    scrivono le scritte `nel_dettaglio` (quelle rimandate dalla tavola intera)
    e quelle degli oggetti che stanno tutti dentro la zona: una tratta che la
    attraversa soltanto ha gia' la sua scritta sulla tavola intera."""
    xmin, ymin, xmax, ymax = zona or estensione(pianta, percorsi)
    prova = colonna(pianta, percorsi, lunghe, forature, fori_dei_pezzi, 50, "A3", regola, (),
                    avvisi_della_colonna, ridotta)
    formato, scala, frame, entra = scegli_il_foglio(pianta, xmax - xmin, ymax - ymin, prova.y)
    avvisi = [] if entra else [
        f"la pianta o la colonna non entrano in {formato} a 1:{scala}: la tavola esce lo stesso, "
        "e va vista"
    ]
    k = 1000.0 / scala
    area = frame.drawing_rect_mm
    larghezza, altezza = (xmax - xmin) * k, (ymax - ymin) * k
    libera_h = area.height_mm - FASCIA_DELLA_SCALA_MM
    ox = area.x_mm + max(MARGINE_MM, (area.width_mm - larghezza) / 2)
    oy = area.y_mm + max(MARGINE_MM, (libera_h - altezza) / 2)

    def P(x: float, y: float) -> Punto:
        return (round(ox + (x - xmin) * k, 4), round(oy + (y - ymin) * k, 4))

    primitive: list[Primitiva] = []
    ingombri = Ingombri(area=(area.x_mm, area.y_mm, area.right_mm, area.y_mm + libera_h))
    carta_della_zona: Rettangolo | None = None
    if zona is not None:
        a, b = P(zona[0], zona[1]), P(zona[2], zona[3])
        carta_della_zona = (a[0], a[1], b[0], b[1])
        ingombri.area = (max(a[0], area.x_mm), max(a[1], area.y_mm), min(b[0], area.right_mm),
                         min(b[1], area.y_mm + libera_h))
    linee: list[tuple[str, Segmento]] = []
    rettangoli: list[tuple[str, Rettangolo]] = []

    # Lo sfondo (non nel dettaglio: un'immagine non si ritaglia).
    if pianta.sfondo is not None and pixel_dello_sfondo is not None and zona is None:
        sf = pianta.sfondo
        x0, y0 = P(-sf.origine_px[0] / sf.px_per_m, -sf.origine_px[1] / sf.px_per_m)
        primitive.append(
            Immagine(Path(sf.file).name, x0, y0, pixel_dello_sfondo[0] / sf.px_per_m * k,
                     pixel_dello_sfondo[1] / sf.px_per_m * k, sf.opacita, pixel_dello_sfondo)
        )
    velo = 0.55 if pianta.sfondo is not None else 1.0

    # I muri.
    for muro, s0, s1 in pezzi_dei_muri(pianta):
        h = muro.spessore / 2
        angoli = tuple(P(*_sull_asse(muro, s, d)) for s, d in ((s0, -h), (s1, -h), (s1, h), (s0, h)))
        primitive.append(Area(angoli, COLORE_MURI[muro.tipo], LAYER_MURI, velo))
        r = (min(p[0] for p in angoli), min(p[1] for p in angoli),
             max(p[0] for p in angoli), max(p[1] for p in angoli))
        ingombri.metti_rettangolo(r, muro=True)
        rettangoli.append((f"muro {muro.id}", r))

    # Le aperture.
    muri = {m.id: m for m in pianta.muri}
    for apertura in pianta.aperture:
        muro = muri[apertura.muro]
        ux, uy, _ = _asse(muro)
        centro = (apertura.centro[0] - muro.da[0]) * ux + (apertura.centro[1] - muro.da[1]) * uy
        s0, s1 = centro - apertura.larghezza / 2, centro + apertura.larghezza / 2
        h = muro.spessore / 2
        if apertura.tipo == "finestra":
            for d in (-h, 0.0, h):
                a, b = P(*_sull_asse(muro, s0, d)), P(*_sull_asse(muro, s1, d))
                primitive.append(Linea((a, b), COLORE_APERTURE, 0.18, LAYER_APERTURE))
                segmento = (a[0], a[1], b[0], b[1], 0.09)
                ingombri.metti_segmento(segmento)
                linee.append((f"finestra {apertura.id}", segmento))
        elif apertura.tipo == "foro":
            angoli = tuple(P(*_sull_asse(muro, s, d)) for s, d in ((s0, -h), (s1, -h), (s1, h), (s0, h)))
            primitive.append(Linea((*angoli, angoli[0]), COLORE_APERTURE, 0.18, LAYER_APERTURE, "1 0.6"))
        elif apertura.tipo == "porta":
            verso = {"sopra": (0.0, -1.0), "sotto": (0.0, 1.0), "sinistra": (-1.0, 0.0), "destra": (1.0, 0.0)}
            normale = (-uy, ux)
            segno = 1.0
            if apertura.apre_verso is not None:
                v = verso[apertura.apre_verso]
                segno = 1.0 if normale[0] * v[0] + normale[1] * v[1] >= 0 else -1.0
            cerniera = _sull_asse(muro, s0, segno * h)
            anta = _sull_asse(muro, s0, segno * (h + apertura.larghezza))
            stipite = _sull_asse(muro, s1, segno * h)
            primitive.append(Linea((P(*cerniera), P(*anta)), COLORE_APERTURE, 0.18, LAYER_APERTURE))
            a_cerniera = math.atan2(anta[1] - cerniera[1], anta[0] - cerniera[0])
            a_stipite = math.atan2(stipite[1] - cerniera[1], stipite[0] - cerniera[0])
            orario = (a_stipite - a_cerniera) % (2 * math.pi) < math.pi
            primitive.append(Arco(P(*cerniera), apertura.larghezza * k, P(*anta), P(*stipite), orario,
                                  COLORE_APERTURE, 0.18, LAYER_APERTURE))
            # Anta e arco, per le scritte: l'arco come otto corde.
            centro_arco = P(*cerniera)
            raggio = apertura.larghezza * k
            passo_angolo = ((a_stipite - a_cerniera + math.pi) % (2 * math.pi) - math.pi) / 8
            corde = [
                (centro_arco[0] + raggio * math.cos(a_cerniera + i * passo_angolo),
                 centro_arco[1] + raggio * math.sin(a_cerniera + i * passo_angolo))
                for i in range(9)
            ]
            for a, b in [(P(*cerniera), P(*anta)), *zip(corde, corde[1:], strict=False)]:
                segmento = (a[0], a[1], b[0], b[1], 0.09)
                ingombri.metti_segmento(segmento)
                linee.append((f"porta {apertura.id}", segmento))

    # I tracciati: sotto quelli instradati dopo, interrotti dove passa sopra uno di prima.
    tracciati = {t.tratta: t for t in pianta.tracciati}
    priorita = {t.tratta: i for i, t in enumerate(ordine_di_instradamento(list(pianta.tracciati)))}
    carta = {p.tratta: [[P(*q) for q in linea] for linea in p.linee] for p in percorsi}
    carta_intera = carta
    if carta_della_zona is not None:
        carta = {t: ritaglia_le_linee(linee_t, carta_della_zona) for t, linee_t in carta.items()}
    ceduti = {p.tratta for p in percorsi if p.ceduto}
    # Sotto tutto, la fascia dei tratti in controsoffitto dove non c'e'.
    for percorso in percorsi:
        for tratto_fuori in percorso.fuori:
            punti_fuori = tuple(P(*q) for q in tratto_fuori)
            if len(punti_fuori) >= 2:
                primitive.append(Linea(punti_fuori, COLORE_FUORI, LARGHEZZA_FUORI_MM, LAYER_FUORI))
    for percorso in sorted(percorsi, key=lambda p: -priorita[p.tratta]):
        tracciato = tracciati[percorso.tratta]
        colore, tratto = stile(tracciato.fluido)
        mezzo = spessore(tracciato.fluido) / 2
        for punti in carta[percorso.tratta]:
            for a, b in zip(punti, punti[1:], strict=False):
                segmento = (a[0], a[1], b[0], b[1], mezzo)
                ingombri.metti_segmento(segmento)
                linee.append((f"tratta {percorso.tratta}", segmento))
        if percorso.ceduto:
            for punti in carta[percorso.tratta]:
                primitive.append(Linea(tuple(punti), colore, 0.3, layer_del_fluido(tracciato.fluido),
                                       TRATTO_CEDUTO))
            continue
        sopra = [
            linea for altro in percorsi
            if altro.tratta not in ceduti and priorita[altro.tratta] < priorita[percorso.tratta]
            for linea in carta[altro.tratta]
        ]
        for punti in carta[percorso.tratta]:
            for pezzo in _interrotta(punti, sopra):
                primitive.append(Linea(tuple(pezzo), colore, spessore(tracciato.fluido),
                                       layer_del_fluido(tracciato.fluido), tratto))

    # I pezzi.
    for pezzo in pianta.pezzi:
        x0, y0, x1, y1 = pezzo.rettangolo
        a, b = P(x0, y0), P(x1, y1)
        r = (a[0], a[1], b[0], b[1])
        primitive += _rettangolo_con_bordo(r, LAYER_PEZZI)
        ingombri.metti_rettangolo(r)
        rettangoli.append((f"pezzo {pezzo.sigla}", r))

    # Le forature.
    for foratura in forature:
        c = P(*foratura.punto)
        primitive.append(Cerchio(c, 0.9, "#000000", 0.25, "#ffffff", LAYER_FORATURE))
        ingombri.metti_rettangolo((c[0] - 0.9, c[1] - 0.9, c[0] + 0.9, c[1] + 0.9))

    # Le zone dei dettagli, sulla tavola intera: una cornice e il suo nome,
    # prima delle scritte, che non ci vanno sopra.
    for lettera, (zx0, zy0, zx1, zy1), scala_del_dettaglio in riquadri:
        a, b = P(zx0, zy0), P(zx1, zy1)
        angoli = ((a[0], a[1]), (b[0], a[1]), (b[0], b[1]), (a[0], b[1]), (a[0], a[1]))
        primitive.append(Linea(angoli, "#000000", 0.25, LAYER_SIGLE, "4 1 1 1"))
        for q0, q1 in zip(angoli, angoli[1:], strict=False):
            segmento = (q0[0], q0[1], q1[0], q1[1], 0.125)
            ingombri.metti_segmento(segmento)
            linee.append((f"dettaglio {lettera}", segmento))
        nome_del_riquadro = f"Dettaglio {lettera} 1:{scala_del_dettaglio}"
        larghezza_nome, salita_nome, discesa_nome = misura(nome_del_riquadro, CORPO_TRATTE_PT, True)
        candidati = [
            (b[0] - larghezza_nome, a[1] - 1.0 - discesa_nome), (a[0], a[1] - 1.0 - discesa_nome),
            (b[0] - larghezza_nome, b[1] + 1.0 + salita_nome), (a[0], b[1] + 1.0 + salita_nome),
        ]
        scelto = candidati[0]
        for x, y in candidati:
            riquadro = (x - 0.5, y - salita_nome - 0.5, x + larghezza_nome + 0.5, y + discesa_nome + 0.5)
            if ingombri.libero(riquadro):
                scelto = (x, y)
                break
        x, y = scelto
        riquadro = (x - 0.5, y - salita_nome - 0.5, x + larghezza_nome + 0.5, y + discesa_nome + 0.5)
        ingombri.metti_scritta(riquadro)
        primitive.append(Scritta(nome_del_riquadro, round(x, 4), round(y, 4), CORPO_TRATTE_PT, LAYER_SIGLE, True))

    # Le scritte: le sigle che stanno dentro il loro pezzo, poi tracciati, le
    # altre sigle, forature, stanze — in quest'ordine. Prima i tracciati delle
    # altre sigle, perche' una tratta corta ha pochi posti accanto a se', e una
    # sigla ne trova sempre uno intorno al suo pezzo; ma una sigla che sta
    # dentro il pezzo non toglie posto a nessuno.
    scritte: list[tuple[str, ScrittaPosata]] = []
    ammessi: dict[str, set[str]] = {}
    dentro_ai_pezzi: set[str] = set()
    def da_scrivere(chi: str, r: Rettangolo) -> bool:
        """Sulla tavola intera, tutte salvo le rimandate; nel dettaglio, le
        rimandate e quelle degli oggetti tutti dentro la zona."""
        if carta_della_zona is None:
            return chi not in rimandate
        z = carta_della_zona
        return chi in nel_dettaglio or (z[0] <= r[0] and z[1] <= r[1] and r[2] <= z[2] and r[3] <= z[3])

    def ingombro_della_tratta(tratte: Sequence[str]) -> Rettangolo:
        punti = [q for t in tratte for linea in carta_intera[t] for q in linea]
        return (min(q[0] for q in punti), min(q[1] for q in punti), max(q[0] for q in punti), max(q[1] for q in punti))

    for pezzo in pianta.pezzi:
        x0, y0, x1, y1 = pezzo.rettangolo
        a, b = P(x0, y0), P(x1, y1)
        if not da_scrivere(f"pezzo {pezzo.sigla}", (a[0], a[1], b[0], b[1])):
            continue
        posata_dentro = posa_nel_pezzo(pezzo.sigla, CORPO_SIGLE_PT, True, (a[0], a[1], b[0], b[1]), ingombri)
        if posata_dentro is not None:
            scritte.append((f"pezzo {pezzo.sigla}", posata_dentro))
            dentro_ai_pezzi.add(pezzo.sigla)
    lunghe_per_tratta = {lu.tratta: lu for lu in lunghe}
    for gruppo in _gruppi_delle_scritte(pianta, percorsi, priorita):
        primo = tracciati[gruppo[0]]
        if len(gruppo) == 1:
            testo = primo.etichetta or " · ".join(
                v for v in (
                    primo.tratta, primo.dimensione,
                    f"L {metri(lunghe_per_tratta[primo.tratta].da_quotare_m)} m",
                ) if v
            )
            guida = primo.tratta
            mezzo = spessore(primo.fluido) / 2
        else:
            # Un fascio fra gli stessi due pezzi ha una scritta sola, accanto al
            # tracciato di mezzo e lontana quanto il fascio e' largo: tre
            # scritte per tre linee a due millimetri l'una dall'altra non si
            # leggono. Le dimensioni di ciascuno stanno nella tabella; la
            # lunghezza e' la piu' lunga del fascio.
            membri = [tracciati[t] for t in gruppo]
            lunghezza = max(lunghe_per_tratta[t].da_quotare_m for t in gruppo)
            nomi = sorted((m.tratta for m in membri), key=chiave_della_tratta)
            numeri = [chiave_della_tratta(n) for n in nomi]
            di_fila = all(
                b[0] == a[0] and b[1] == a[1] + 1 for a, b in zip(numeri, numeri[1:], strict=False)
            )
            testo = (f"{nomi[0]}–{nomi[-1]}" if di_fila else "+".join(nomi)) + f" · L {metri(lunghezza)} m"
            guida = gruppo[len(gruppo) // 2]
            mezzo = (len(gruppo) - 1) / 2 * pianta.parametri.passo_fascio_m * k + max(
                spessore(m.fluido) for m in membri
            ) / 2
        chi = f"tratta {guida}" if len(gruppo) == 1 else f"fascio {' '.join(gruppo)}"
        if not carta[guida] or not da_scrivere(chi, ingombro_della_tratta(gruppo)):
            continue
        proprie = [s for di, s in linee if di.startswith("tratta ") and di[7:] in gruppo]
        posata = posa_accanto(testo, CORPO_TRATTE_PT, False, carta[guida], proprie, ingombri, mezzo)
        scritte.append((chi, posata))
    for pezzo in pianta.pezzi:
        if pezzo.sigla in dentro_ai_pezzi:
            continue
        x0, y0, x1, y1 = pezzo.rettangolo
        a, b = P(x0, y0), P(x1, y1)
        if not da_scrivere(f"pezzo {pezzo.sigla}", (a[0], a[1], b[0], b[1])):
            continue
        posata = posa_intorno(pezzo.sigla, CORPO_SIGLE_PT, True, (a[0], a[1], b[0], b[1]), ingombri,
                              dentro=True)
        scritte.append((f"pezzo {pezzo.sigla}", posata))
    for foratura in forature:
        c = P(*foratura.punto)
        if not da_scrivere(f"foratura {foratura.numero}", (c[0], c[1], c[0], c[1])):
            continue
        muro_del_foro = [
            r for di, r in rettangoli
            if di == f"muro {foratura.muro}" and r[0] - 1e-6 <= c[0] <= r[2] + 1e-6 and r[1] - 1e-6 <= c[1] <= r[3] + 1e-6
        ]
        posata = posa_intorno(foratura.numero, CORPO_TRATTE_PT, True,
                              (c[0] - 0.9, c[1] - 0.9, c[0] + 0.9, c[1] + 0.9), ingombri, sopra=muro_del_foro)
        ammessi[f"foratura {foratura.numero}"] = {f"muro {foratura.muro}"}
        scritte.append((f"foratura {foratura.numero}", posata))
    for stanza in pianta.stanze:
        superficie = _superficie(stanza.poligono)
        testo = " · ".join(
            v for v in (stanza.nome, stanza.zona, f"{metri(superficie)} m²") if v
        )
        posata_o_niente = posa_dentro(
            testo, CORPO_STANZE_PT, False,
            (P(*p) for p in _punti_dentro(stanza.poligono)), ingombri,
        )
        if posata_o_niente is not None:
            scritte.append((f"stanza {stanza.id}", posata_o_niente))

    for chi, posata in scritte:
        colore = COLORE_STANZE if chi.startswith("stanza") else "#000000"
        layer = LAYER_STANZE if chi.startswith("stanza") else LAYER_SIGLE
        if chi.startswith(("tratta", "fascio")):
            colore = stile(tracciati[chi.split()[1]].fluido)[0]
        if posata.numero is not None:
            primitive += _numero_cerchiato(posata.testo, posata.x + RAGGIO_DEL_NUMERO_MM, posata.y, layer)
        else:
            primitive.append(Scritta(posata.testo, posata.x, posata.y, posata.corpo_pt, layer,
                                     posata.grassetto, colore))
        if posata.richiamo is not None:
            x0, y0, x1, y1 = posata.richiamo
            primitive.append(Linea(((x0, y0), (x1, y1)), "#000000", 0.18, LAYER_SIGLE))
            primitive.append(Cerchio((x0, y0), 0.35, "#000000", 0.1, "#000000", LAYER_SIGLE))
            linee.append((f"richiamo:{chi}", (x0, y0, x1, y1, 0.09)))

    # Nel dettaglio, il disegno si ritaglia sulla zona.
    if carta_della_zona is not None:
        primitive = [q for p in primitive for q in ritaglia(p, carta_della_zona)]
        x0z, y0z, x1z, y1z = carta_della_zona
        primitive.append(Linea(((x0z, y0z), (x1z, y0z), (x1z, y1z), (x0z, y1z), (x0z, y0z)), "#000000", 0.25,
                               LAYER_SIGLE, "4 1 1 1"))

    # La scala.
    primitive += _barra_della_scala(area.x_mm + MARGINE_MM, area.y_mm + area.height_mm - 4.0, k, scala)

    # La colonna.
    c = colonna(pianta, percorsi, lunghe, forature, fori_dei_pezzi, scala, formato, regola,
                ingombri.legenda, avvisi_della_colonna, ridotta)
    if c.y + 6.0 > frame.legend_rect_mm.height_mm:
        # Le scritte in legenda e gli avvisi si sanno solo dopo la posa: se la
        # colonna non entra, si rifa' la tavola sul formato successivo.
        nomi = list(FORMATI)
        if pianta.foglio.formato is None and nomi.index(formato) + 1 < len(nomi):
            piu_grande = pianta.model_copy(
                update={"foglio": Foglio(formato=nomi[nomi.index(formato) + 1], scala=scala)}
            )
            tavola = componi(piu_grande, percorsi, lunghe, forature, fori_dei_pezzi, cartiglio,
                             pixel_dello_sfondo, regola, avvisi_della_colonna, zona, rimandate, riquadri,
                             ridotta, nel_dettaglio)
            return tavola
        avvisi.append("la colonna non entra nel foglio: la tavola esce lo stesso, e va vista")
    bx, by = frame.legend_rect_mm.x_mm + 3.0, frame.legend_rect_mm.y_mm + 2.0
    primitive += [_sposta(p, bx, by) for p in c.primitive]

    return Tavola(
        frame=frame, formato=formato, scala=scala, primitive=primitive, scritte=scritte,
        linee=linee, rettangoli=rettangoli, avvisi=avvisi, ammessi=ammessi,
        trasforma=(ox, oy, xmin, ymin, k),
        cartiglio=None if cartiglio is None else CartiglioDellaTavola(
            cartiglio=cartiglio, valori=valori_del_cartiglio(pianta, scala)
        ),
    )


def _sovrapposti_stretti(a: Rettangolo, b: Rettangolo) -> bool:
    return a[0] <= b[2] and b[0] <= a[2] and a[1] <= b[3] and b[1] <= a[3]


def _ritaglia_segmento(a: Punto, b: Punto, r: Rettangolo) -> tuple[Punto, Punto] | None:
    """Liang-Barsky: il pezzo del segmento dentro il rettangolo."""
    x0, y0, x1, y1 = r
    dx, dy = b[0] - a[0], b[1] - a[1]
    t0, t1 = 0.0, 1.0
    for p_, q_ in ((-dx, a[0] - x0), (dx, x1 - a[0]), (-dy, a[1] - y0), (dy, y1 - a[1])):
        if abs(p_) < 1e-12:
            if q_ < 0:
                return None
            continue
        t = q_ / p_
        if p_ < 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
        if t0 > t1:
            return None
    return ((round(a[0] + dx * t0, 4), round(a[1] + dy * t0, 4)), (round(a[0] + dx * t1, 4), round(a[1] + dy * t1, 4)))


def ritaglia_le_linee(linee: Sequence[Sequence[Punto]], r: Rettangolo) -> list[list[Punto]]:
    """Le spezzate ritagliate sul rettangolo: un pezzo per ogni tratto continuo dentro."""
    out: list[list[Punto]] = []
    for punti in linee:
        corrente: list[Punto] = []
        for a, b in zip(punti, punti[1:], strict=False):
            pezzo = _ritaglia_segmento(a, b, r)
            if pezzo is None or math.dist(*pezzo) < 1e-6:
                if len(corrente) >= 2:
                    out.append(corrente)
                corrente = []
                continue
            if corrente and math.dist(corrente[-1], pezzo[0]) < 1e-6:
                corrente.append(pezzo[1])
            else:
                if len(corrente) >= 2:
                    out.append(corrente)
                corrente = [pezzo[0], pezzo[1]]
            if math.dist(pezzo[1], b) > 1e-6:
                out.append(corrente)
                corrente = []
        if len(corrente) >= 2:
            out.append(corrente)
    return out


def _ritaglia_poligono(punti: Sequence[Punto], r: Rettangolo) -> list[Punto]:
    """Sutherland-Hodgman sul rettangolo."""
    x0, y0, x1, y1 = r
    lati = (
        (lambda p: p[0] >= x0, lambda a, b: (x0, a[1] + (b[1] - a[1]) * (x0 - a[0]) / (b[0] - a[0]))),
        (lambda p: p[0] <= x1, lambda a, b: (x1, a[1] + (b[1] - a[1]) * (x1 - a[0]) / (b[0] - a[0]))),
        (lambda p: p[1] >= y0, lambda a, b: (a[0] + (b[0] - a[0]) * (y0 - a[1]) / (b[1] - a[1]), y0)),
        (lambda p: p[1] <= y1, lambda a, b: (a[0] + (b[0] - a[0]) * (y1 - a[1]) / (b[1] - a[1]), y1)),
    )
    uscita = list(punti)
    for dentro, taglio in lati:
        entrata, uscita = uscita, []
        for i, corrente in enumerate(entrata):
            precedente = entrata[i - 1]
            if dentro(corrente):
                if not dentro(precedente):
                    uscita.append(taglio(precedente, corrente))
                uscita.append(corrente)
            elif dentro(precedente):
                uscita.append(taglio(precedente, corrente))
        if not uscita:
            return []
    return [(round(x, 4), round(y, 4)) for x, y in uscita]


def ritaglia(p: Primitiva, r: Rettangolo) -> list[Primitiva]:
    """Una primitiva del disegno, ritagliata sulla zona del dettaglio."""
    if isinstance(p, Linea):
        return [Linea(tuple(pezzo), p.colore, p.spessore, p.layer, p.tratto)
                for pezzo in ritaglia_le_linee([p.punti], r)]
    if isinstance(p, Area):
        punti = _ritaglia_poligono(p.punti, r)
        return [Area(tuple(punti), p.colore, p.layer, p.opacita)] if len(punti) >= 3 else []
    if isinstance(p, Arco):
        dentro = all(r[0] - 1e-6 <= q[0] <= r[2] + 1e-6 and r[1] - 1e-6 <= q[1] <= r[3] + 1e-6
                     for q in (p.centro, p.da, p.a))
        return [p] if dentro else []
    if isinstance(p, Cerchio):
        return [p] if r[0] <= p.centro[0] <= r[2] and r[1] <= p.centro[1] <= r[3] else []
    if isinstance(p, Scritta):
        return [p]
    return []


def _gruppi_delle_scritte(
    pianta: Pianta, percorsi: Sequence[Percorso], priorita: dict[str, int]
) -> list[list[str]]:
    """Le tratte che hanno una scritta in comune: i fasci fra gli stessi due
    pezzi, tutti instradati. Le altre, una per una."""
    instradate = {p.tratta for p in percorsi if not p.ceduto}
    gruppi: dict[tuple[str, ...], list[str]] = {}
    tutti: list[list[str]] = []
    for t in pianta.tracciati:
        if t.fascio and t.tratta in instradate and t.etichetta is None:
            capi = (t.fascio, *sorted((t.estremo_da.pezzo, t.estremo_a.pezzo)))
            gruppi.setdefault(capi, []).append(t.tratta)
        else:
            tutti.append([t.tratta])
    for gruppo in gruppi.values():
        if len(gruppo) == 1:
            tutti.append(gruppo)
        else:
            tutti.append(sorted(gruppo, key=lambda t: priorita[t]))
    return sorted(tutti, key=lambda g: priorita[g[0]])


def _sposta(p: Primitiva, dx: float, dy: float) -> Primitiva:
    def m(q: Punto) -> Punto:
        return (round(q[0] + dx, 4), round(q[1] + dy, 4))

    if isinstance(p, Scritta):
        return Scritta(p.testo, round(p.x + dx, 4), round(p.y + dy, 4), p.corpo_pt, p.layer,
                       p.grassetto, p.colore, p.ancora)
    if isinstance(p, Linea):
        return Linea(tuple(m(q) for q in p.punti), p.colore, p.spessore, p.layer, p.tratto)
    if isinstance(p, Area):
        return Area(tuple(m(q) for q in p.punti), p.colore, p.layer, p.opacita)
    if isinstance(p, Cerchio):
        return Cerchio(m(p.centro), p.raggio, p.colore, p.spessore, p.riempimento, p.layer)
    return p


def _barra_della_scala(x: float, y: float, k: float, scala: int) -> list[Primitiva]:
    metri_della_barra = 2 if scala <= 25 else (5 if scala <= 50 else 10)
    passo = 1 if scala <= 50 else 2
    out: list[Primitiva] = []
    for i in range(0, metri_della_barra, passo):
        x0, x1 = x + i * k, x + (i + passo) * k
        angoli = ((x0, y - 1.2), (x1, y - 1.2), (x1, y), (x0, y))
        colore = "#000000" if (i // passo) % 2 == 0 else "#ffffff"
        out.append(Area(angoli, colore, LAYER_SCALA))
        out.append(Linea((*angoli, angoli[0]), "#000000", 0.18, LAYER_SCALA))
    for i in range(0, metri_della_barra + 1, passo):
        testo = f"{i} m" if i == metri_della_barra else str(i)
        out.append(Scritta(testo, round(x + i * k, 4), round(y - 2.2, 4), CORPO_COLONNA_PT,
                           LAYER_SCALA, ancora="middle"))
    out.append(Scritta(f"Scala 1:{scala}", round(x + metri_della_barra * k + 6.0, 4), y,
                       CORPO_COLONNA_PT, LAYER_SCALA, True))
    return out


def _interrotta(punti: Sequence[Punto], sopra: Sequence[Sequence[Punto]]) -> list[list[Punto]]:
    """La spezzata, interrotta dove un tracciato di prima la attraversa."""
    tagli: list[tuple[int, float]] = []
    for altro in sopra:
        for indice, (a, b) in enumerate(zip(punti, punti[1:], strict=False)):
            for c, d in zip(altro, altro[1:], strict=False):
                punto = _incrocio_stretto((a, b), (c, d))
                if punto is not None:
                    t = math.dist(a, punto) / max(math.dist(a, b), 1e-9)
                    tagli.append((indice, t))
    if not tagli:
        return [list(punti)]
    pezzi: list[list[Punto]] = []
    corrente: list[Punto] = [punti[0]]
    for indice, (a, b) in enumerate(zip(punti, punti[1:], strict=False)):
        lunghezza = math.dist(a, b)
        for _, t in sorted(x for x in tagli if x[0] == indice):
            meno = max(0.0, t - INTERRUZIONE_MM / lunghezza)
            piu = min(1.0, t + INTERRUZIONE_MM / lunghezza)
            corrente.append((a[0] + (b[0] - a[0]) * meno, a[1] + (b[1] - a[1]) * meno))
            pezzi.append(corrente)
            corrente = [(a[0] + (b[0] - a[0]) * piu, a[1] + (b[1] - a[1]) * piu)]
        corrente.append(b)
    pezzi.append(corrente)
    return [[(round(x, 4), round(y, 4)) for x, y in p] for p in pezzi if len(p) >= 2]


def _incrocio_stretto(s: tuple[Punto, Punto], t: tuple[Punto, Punto]) -> Punto | None:
    (a, b), (c, d) = s, t
    s_or = abs(a[1] - b[1]) < 1e-6
    t_or = abs(c[1] - d[1]) < 1e-6
    if s_or == t_or:
        return None
    if s_or:
        x, y = c[0], a[1]
        dentro_s = min(a[0], b[0]) < x < max(a[0], b[0])
        dentro_t = min(c[1], d[1]) < y < max(c[1], d[1])
    else:
        x, y = a[0], c[1]
        dentro_s = min(a[1], b[1]) < y < max(a[1], b[1])
        dentro_t = min(c[0], d[0]) < x < max(c[0], d[0])
    return (x, y) if dentro_s and dentro_t else None


def _superficie(poligono: Sequence[Punto]) -> float:
    doppia = sum(
        a[0] * b[1] - b[0] * a[1]
        for a, b in zip(poligono, [*poligono[1:], poligono[0]], strict=True)
    )
    return abs(doppia) / 2


def _punti_dentro(poligono: Sequence[Punto]) -> list[Punto]:
    """Punti interni al poligono, dal baricentro dei vertici in fuori."""
    xs, ys = [p[0] for p in poligono], [p[1] for p in poligono]
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    out: list[Punto] = []
    passo = 0.2
    nx, ny = int((max(xs) - min(xs)) / passo) + 1, int((max(ys) - min(ys)) / passo) + 1
    for i in range(nx + 1):
        for j in range(ny + 1):
            p = (min(xs) + i * passo, min(ys) + j * passo)
            if _dentro(p, poligono):
                out.append(p)
    out.sort(key=lambda p: (round((p[0] - cx) ** 2 + (p[1] - cy) ** 2, 6), p))
    return out


def _dentro(p: Punto, poligono: Sequence[Punto]) -> bool:
    x, y = p
    dentro = False
    for a, b in zip(poligono, [*poligono[1:], poligono[0]], strict=True):
        if (a[1] > y) != (b[1] > y):
            xi = a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
            if x < xi:
                dentro = not dentro
    return dentro


# --- gli scrittori -------------------------------------------------------------------


def _n(v: float) -> str:
    return f"{round(v, 4):g}"


def _escape(testo: str) -> str:
    return testo.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def scrivi_svg(tavola: Tavola) -> str:
    standard = tavola.frame.standard
    w, h = standard.sheet_width_mm, standard.sheet_height_mm
    parti = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:g}mm" height="{h:g}mm" '
        f'viewBox="0 0 {w:g} {h:g}" font-family="{FAMIGLIA_DELLE_SCRITTE}">',
        f'<rect x="0" y="0" width="{w:g}" height="{h:g}" fill="#ffffff" stroke="none"/>',
    ]
    for p in tavola.primitive:
        parti.append(_svg(p))
    legenda = tavola.frame.legend_rect_mm
    parti.append(
        f'<rect x="{_n(legenda.x_mm)}" y="{_n(legenda.y_mm)}" width="{_n(legenda.width_mm)}" '
        f'height="{_n(legenda.height_mm)}" fill="none" stroke="#000000" stroke-width="{standard.line_thin_mm:g}"/>'
    )
    if tavola.cartiglio is not None:
        parti.append(disegna_cartiglio(tavola.cartiglio, tavola.frame).svg)
    else:
        bordo = tavola.frame.border_rect_mm
        parti.append(
            f'<rect x="{_n(bordo.x_mm)}" y="{_n(bordo.y_mm)}" width="{_n(bordo.width_mm)}" '
            f'height="{_n(bordo.height_mm)}" fill="none" stroke="#000000" '
            f'stroke-width="{standard.line_medium_mm:g}"/>'
        )
    parti.append("</svg>")
    return "\n".join(parti) + "\n"


def _svg(p: Primitiva) -> str:
    if isinstance(p, Area):
        punti = " ".join(f"{_n(x)},{_n(y)}" for x, y in p.punti)
        velo = "" if p.opacita == 1 else f' fill-opacity="{p.opacita:g}"'
        return f'<polygon points="{punti}" fill="{p.colore}"{velo} stroke="none"/>'
    if isinstance(p, Linea):
        punti = " ".join(f"{_n(x)},{_n(y)}" for x, y in p.punti)
        tratto = "" if p.tratto == "none" else f' stroke-dasharray="{p.tratto}"'
        return (
            f'<polyline points="{punti}" fill="none" stroke="{p.colore}" '
            f'stroke-width="{p.spessore:g}"{tratto}/>'
        )
    if isinstance(p, Arco):
        return (
            f'<path d="M{_n(p.da[0])} {_n(p.da[1])} A{_n(p.raggio)} {_n(p.raggio)} 0 0 '
            f'{1 if p.orario else 0} {_n(p.a[0])} {_n(p.a[1])}" fill="none" stroke="{p.colore}" '
            f'stroke-width="{p.spessore:g}"/>'
        )
    if isinstance(p, Cerchio):
        return (
            f'<circle cx="{_n(p.centro[0])}" cy="{_n(p.centro[1])}" r="{p.raggio:g}" '
            f'fill="{p.riempimento}" stroke="{p.colore}" stroke-width="{p.spessore:g}"/>'
        )
    if isinstance(p, Scritta):
        peso = ' font-weight="bold"' if p.grassetto else ""
        return (
            f'<text x="{_n(p.x)}" y="{_n(p.y)}" font-size="{round(p.corpo_pt * PT_MM, 4):g}"{peso} '
            f'fill="{p.colore}" text-anchor="{p.ancora}">{_escape(p.testo)}</text>'
        )
    return (
        f'<image href="{_escape(p.file)}" x="{_n(p.x)}" y="{_n(p.y)}" width="{_n(p.larghezza)}" '
        f'height="{_n(p.altezza)}" preserveAspectRatio="none" opacity="{p.opacita:g}"/>'
    )


def scrivi_dxf(tavola: Tavola, destinazione: Path, titolo: str) -> list[Path]:
    """La stessa tavola in DXF, con lo scrittore del motore: presentazione del
    formato, stili di testo, colori esatti e cartiglio in spazio carta."""
    from ezdxf import const
    from ezdxf.colors import RGB

    from disegnatore_mep.graphics.dxf import (
        LAYER_CARTIGLIO,
        LAYER_FINESTRA,
        _classi_in_ordine,
        _metadati_fissi,
        _Tavola,
        aci_vicino,
        colora,
        lineweight,
        rgb,
    )

    scritti = [destinazione]
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    foglio = SimpleNamespace(title=titolo, tabella=None, diametri=())
    with _metadati_fissi():
        t = _Tavola(cast(Any, foglio), tavola.frame, cast(Any, None))
        thin = t.standard.line_thin_mm
        for nome, descrizione in DESCRIZIONE_DEI_LAYER.items():
            t.layer(nome, descrizione, None, "none", thin)
        t.layer(LAYER_CARTIGLIO, "Squadratura e cartiglio", None, "none", thin)
        t.layer(LAYER_FINESTRA, "Finestra della presentazione (non si stampa)", None, "none", thin,
                stampa=False)
        if tavola.cartiglio is not None:
            logo = destinazione.parent / t.cartiglio(tavola.cartiglio)
            logo.write_bytes(tavola.cartiglio.cartiglio.logo_jpeg)
            scritti.append(logo)
        else:
            t.rettangolo(tavola.frame.border_rect_mm, LAYER_CARTIGLIO, t.standard.line_medium_mm,
                         dove=t.carta)
        msp = t.msp
        for p in tavola.primitive:
            if isinstance(p, Area):
                if p.layer not in t.doc.layers:
                    t.layer(p.layer, p.layer, None, "none", thin)
                campitura = msp.add_hatch(dxfattribs={"layer": p.layer})
                campitura.set_solid_fill(color=aci_vicino(rgb(p.colore)), rgb=RGB(*rgb(p.colore)))
                campitura.paths.add_polyline_path([t.p(*q) for q in p.punti], is_closed=True)
                if p.opacita < 1:
                    campitura.transparency = 1 - p.opacita
            elif isinstance(p, Linea):
                if p.layer not in t.doc.layers:
                    t.layer(p.layer, _descrizione_della_rete(p.layer), p.colore, p.tratto, p.spessore)
                polilinea = msp.add_lwpolyline(
                    [t.p(*q) for q in p.punti],
                    dxfattribs={"layer": p.layer, "lineweight": lineweight(p.spessore),
                                "linetype": t.tipo_di_linea(p.tratto)},
                )
                colora(polilinea, p.colore)
                polilinea.dxf.flags = polilinea.dxf.flags | const.LWPOLYLINE_PLINEGEN
            elif isinstance(p, Arco):
                centro = t.p(*p.centro)
                da, a = t.p(*p.da), t.p(*p.a)
                ang_da = math.degrees(math.atan2(da[1] - centro[1], da[0] - centro[0]))
                ang_a = math.degrees(math.atan2(a[1] - centro[1], a[0] - centro[0]))
                # Orario sul foglio e' antiorario nel DXF, che ha la y in alto.
                inizio, fine = (ang_da, ang_a) if p.orario else (ang_a, ang_da)
                arco = msp.add_arc(centro, p.raggio, inizio % 360, fine % 360,
                                   dxfattribs={"layer": p.layer, "lineweight": lineweight(p.spessore)})
                colora(arco, p.colore)
            elif isinstance(p, Cerchio):
                cerchio = msp.add_circle(t.p(*p.centro), p.raggio,
                                         dxfattribs={"layer": p.layer, "lineweight": lineweight(p.spessore)})
                colora(cerchio, p.colore)
                if p.riempimento != "#ffffff":
                    campitura = msp.add_hatch(dxfattribs={"layer": p.layer})
                    campitura.set_solid_fill(color=aci_vicino(rgb(p.riempimento)),
                                             rgb=RGB(*rgb(p.riempimento)))
                    cx, cy = t.p(*p.centro)
                    campitura.paths.add_polyline_path(
                        [(cx - p.raggio, cy, 1.0), (cx + p.raggio, cy, 1.0)], is_closed=True
                    )
            elif isinstance(p, Scritta):
                t.testo(p.testo, p.x, p.y, p.corpo_pt * PT_MM, p.layer, p.ancora, p.grassetto, p.colore)
            elif isinstance(p, Immagine):
                definizione = t.doc.add_image_def(p.file, p.pixel)
                msp.add_image(definizione, t.p(p.x, p.y + p.altezza), (p.larghezza, p.altezza),
                              dxfattribs={"layer": LAYER_SFONDO})
        _classi_in_ordine(t.doc)
        t.doc.saveas(destinazione)
    return scritti


def _descrizione_della_rete(layer: str) -> str:
    for fluido in ORDINE_DEI_FLUIDI:
        if layer_del_fluido(fluido) == layer:
            return f"Tracciati: {nome_del_fluido(fluido).lower()}"
    return "Tracciati"


def valori_del_cartiglio(pianta: Pianta, scala: int) -> dict[NomeCampo, str | None]:
    dati = pianta.cartiglio
    revisione = dati.get("revisione")
    valori: dict[str, str | None] = {
        "intestazione": None,
        "dicitura": dati.get("dicitura"),
        "committente": dati.get("committente"),
        "indirizzo": dati.get("indirizzo"),
        "progetto": dati.get("progetto"),
        "titolo_tavola": pianta.titolo,
        "scala": f"1:{scala}",
        "data": dati.get("data"),
        "revisione": None if revisione is None else (
            revisione if revisione.lower().startswith("rev") else f"Rev. {revisione}"
        ),
        "commessa": dati.get("commessa"),
        "numero_tavola": dati.get("numero_tavola"),
        "approvato": dati.get("approvato"),
        "verificato": dati.get("verificato"),
        "disegnato": dati.get("disegnato"),
    }
    return cast(dict[NomeCampo, str | None], valori)


def misura_della_scritta(testo: str, corpo_pt: float, grassetto: bool) -> float:
    return misura(testo, corpo_pt, grassetto)[0]
