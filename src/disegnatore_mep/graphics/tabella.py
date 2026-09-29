"""La tabella delle apparecchiature, in alto a sinistra del foglio (REL-006).

Il PO, il 28 settembre 2026 (I-141): «Inserire una tabella in alto a sinistra del
foglio con codice, descrizione, caratteristiche, marca, modello. Esempio pdc.01
pompa di calore aria acqua nr 1 - 15 kw - Shenling - HPM150WR3. Mettiamo dentro
solo le apparecchiature principali, e vaso espansione, no valvole». E lo stesso
giorno (I-144): «marca e modello non deve essere nella skill, è qualcosa che
definisce il progettista […] quindi è un dato in ingresso».

Questo modulo fa tre cose, e il posto sul foglio non e' fra queste — lo decide
l'esecutore del piano, che fa spazio alla tabella (`layout/compose.py`):

- **che cosa dice** (`righe_della_tabella`): i pezzi che fanno un mestiere da
  apparecchiatura principale, la loro sigla, il nome della voce di catalogo, i
  dati tecnici **che il progettista ha dato**, con chiavi fisse. **Un dato che
  manca resta una cella vuota, con un trattino** (D-087): la tabella non ne
  inventa, e la skill non ha un elenco di marche e modelli;
- **quanto e' grande** (`impagina_la_tabella`): le colonne larghe quanto il
  loro testo piu' lungo, misurato con le larghezze di Helvetica del cartiglio;
- **come si disegna** (`tratti_della_tabella`): linee e testi, che l'SVG e il
  DXF scrivono **dalle stesse misure** — la tabella e' la stessa nei due.

Le scelte di contenuto e di grafica sono **proposte della sessione**, da
giudicare sulla tavola (D-146): quali mestieri entrano, le caratteristiche per
mestiere, il codice uguale alla sigla del disegno, «nr» quando le voci sono piu'
d'una, il trattino, il corpo e le righe della legenda.
"""

import re
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph.naming import Naming, NamingError
from disegnatore_mep.graph.plant import GraphError, read_plant
from disegnatore_mep.layout.geometry import (
    RigaDellaTabella,
    SheetGeometry,
    TabellaDelleApparecchiature,
)
from disegnatore_mep.model.project import (
    CHIAVI_DEI_DATI_NUMERICI,
    MARCA,
    MODELLO,
    ProjectModel,
)
from disegnatore_mep.model.types import JsonPrimitive

from .cartiglio import FAMIGLIA, PT_MM, SEPARATORE, larghezza_mm
from .frame import SheetFrame
from .standard import GraphicStandard

FUNZIONI_DELLA_TABELLA: tuple[str, ...] = (
    "heat_generation",
    "refrigerant_generation",
    "thermal_storage",
    "dhw_storage",
    "hydraulic_separation",
    "heat_exchange",
    "circulation",
    "expansion",
)
"""I mestieri delle apparecchiature principali, e il vaso di espansione (I-141).

Generatori, accumuli e bollitori, separatori idraulici, scambiatori,
circolatori — e i vasi. **Fuori** le valvole, come il PO ha detto, e con loro
filtri, strumenti, raccordi e attacchi. Fuori anche i **terminali** (radiatori,
ventilconvettori, pannelli): nello schema di centrale sono le utenze, non
macchine della centrale. *Proposta della sessione*, da giudicare sulla tavola.
Un pezzo entra se **uno qualunque** dei suoi mestieri e' in elenco."""

CARATTERISTICHE_PER_MESTIERE: dict[str, tuple[str, ...]] = {
    "heat_generation": ("power_kw",),
    "refrigerant_generation": ("power_kw",),
    "heat_exchange": ("power_kw",),
    "thermal_storage": ("volume_l",),
    "dhw_storage": ("volume_l",),
    "expansion": ("volume_l",),
    "circulation": ("flow_rate_m3h", "head_kpa", "head_m"),
}
"""Che cosa si scrive fra le caratteristiche, secondo il mestiere del pezzo.

La **potenza** dei generatori e degli scambiatori, il **volume** di accumuli,
bollitori e vasi, **portata e prevalenza** dei circolatori. Un pezzo che fa
piu' mestieri — il boiler in pompa di calore genera e accumula — le porta
tutte, nell'ordine delle chiavi di `CHIAVI_DEI_DATI_NUMERICI`. Il separatore
idraulico non ha una sua caratteristica: quando e' anche un accumulo, porta il
volume da accumulo."""

INTESTAZIONE: tuple[str, ...] = (
    "CODICE",
    "DESCRIZIONE",
    "CARATTERISTICHE",
    "MARCA",
    "MODELLO",
)
"""Le cinque colonne, nell'ordine in cui il PO le ha dette (I-141)."""

CELLA_VUOTA = "–"
"""Il segno di una cella senza dato: il progettista non l'ha dato, e sulla
tavola non compare (D-087). Un trattino e non il vuoto, perche' il vuoto si
legge come una dimenticanza del disegno."""

MARGINE_DELLA_RIGA_MM = 1.85
"""Lo spazio sopra e sotto le maiuscole di una riga: quello che la riga di 5 mm
di `REL-006` lasciava al testo di 1,8 mm (D-192, punto 8)."""

PASSO_DELLE_RIGHE_MM = 1.25
"""L'altezza di una riga si arrotonda a mezzo passo di griglia."""

RIENTRO_MM = 1.5
"""Lo spazio fra il testo e le linee della cella, a sinistra e a destra: lo
stesso stacco che un testo prende dal proprio pezzo (`labels.TAG_GAP_MM`)."""

MEZZE_MAIUSCOLE_EM = 0.35
"""Mezza altezza delle maiuscole, in corpi: serve a mettere il testo a meta'
della riga. Le maiuscole di Arial e di Helvetica sono alte 0,688–0,716 em
(`dxf.ALTEZZA_MAIUSCOLE_EM`, il cartiglio)."""


def altezza_della_riga_mm(corpo_mm: float) -> float:
    """L'altezza di una riga della tabella per il corpo dei suoi testi (REL-008): le
    maiuscole, alte 0,7 corpi, piu' lo stesso margine sopra e sotto, arrotondate a
    mezzo passo di griglia. A 1,8 mm fa i 5 mm di `REL-006`; a 9 punti 6,25."""
    grezza = 2 * MEZZE_MAIUSCOLE_EM * corpo_mm + 2 * MARGINE_DELLA_RIGA_MM
    return -(-round(grezza, 6) // PASSO_DELLE_RIGHE_MM) * PASSO_DELLE_RIGHE_MM


def formatta_il_dato(chiave: str, valore: JsonPrimitive) -> str | None:
    """Un dato numerico come si legge sulla tavola: «15 kW», «2,5 m³/h».

    La virgola e' quella decimale italiana. Un valore che non e' un numero non
    si scrive: e' il modello a rifiutarlo (`ComponentInstance`), e qui non si
    indovina che cosa volesse dire."""
    unita = CHIAVI_DEI_DATI_NUMERICI.get(chiave)
    if unita is None or isinstance(valore, bool) or not isinstance(valore, int | float):
        return None
    testo = str(valore) if isinstance(valore, int) else f"{valore:.3f}".rstrip("0").rstrip(".")
    return f"{testo.replace('.', ',')} {unita}"


def _testo(valore: JsonPrimitive) -> str | None:
    """Un dato di testo — marca, modello —, o `None` se non c'e'.

    «ND» e' come «Capire» scrive un dato non dato (`cartiglio.NON_DATO`): per la
    tabella e' una cella vuota come un dato che manca."""
    if not isinstance(valore, str) or not valore.strip() or valore.strip().upper() == "ND":
        return None
    return valore.strip()


def _in_ordine_di_sigla(codice: str | None) -> tuple[str, int, str]:
    """`PDC-02` prima di `PDC-10`: la famiglia, poi il numero come numero."""
    if codice is None:
        return ("~", 0, "")
    forma = re.fullmatch(r"([A-Za-z]+)[-.]?(\d+)", codice)
    if forma is None:
        return (codice, 0, codice)
    return (forma.group(1), int(forma.group(2)), codice)


def righe_della_tabella(
    modello: ProjectModel,
    catalogo: ComponentRegistry,
    naming: Naming,
    sigle: dict[str, str],
    sul_foglio: Iterable[str],
) -> list[RigaDellaTabella]:
    """Le apparecchiature della tavola, una riga per pezzo, in ordine.

    `sigle` sono quelle della lettura dell'impianto (`graph.plant`): la sigla
    che l'ingegnere ha scritto, e per gli altri quella della famiglia — la
    stessa che il disegno scrive accanto al pezzo (D-097, «la sigla è una sola
    per tutto il prodotto»). `sul_foglio` sono i pezzi disegnati su questa
    tavola.

    L'ordine e' quello delle famiglie in `naming/families.json` — prima chi il
    calore lo produce, poi accumuli, separatori, circolatori, scambiatori, vasi
    — e dentro una famiglia quello delle sigle."""
    disegnati = set(sul_foglio)
    scelti: list[tuple[tuple[int, tuple[str, int, str], str], RigaDellaTabella]] = []
    for pezzo in modello.components:
        if pezzo.id not in disegnati:
            continue
        voce = catalogo.get(pezzo.definition_id)
        mestieri = tuple(voce.functions)
        if not set(mestieri) & set(FUNZIONI_DELLA_TABELLA):
            continue
        try:
            famiglia = naming.families.index(naming.family_of(mestieri, pezzo.id))
        except NamingError:
            famiglia = len(naming.families)
        chiavi = [
            chiave
            for chiave in CHIAVI_DEI_DATI_NUMERICI
            if any(chiave in CARATTERISTICHE_PER_MESTIERE.get(item, ()) for item in mestieri)
        ]
        dati = [
            scritto
            for chiave in chiavi
            if (scritto := formatta_il_dato(chiave, pezzo.properties.get(chiave))) is not None
        ]
        codice = sigle.get(pezzo.id, pezzo.tag)
        riga = RigaDellaTabella(
            component_id=pezzo.id,
            codice=codice,
            descrizione=voce.name,
            caratteristiche=SEPARATORE.join(dati) if dati else None,
            marca=_testo(pezzo.properties.get(MARCA)),
            modello=_testo(pezzo.properties.get(MODELLO)),
        )
        scelti.append(((famiglia, _in_ordine_di_sigla(codice), pezzo.id), riga))
    righe = [riga for _, riga in sorted(scelti, key=lambda item: item[0])]

    # «nr 1», «nr 2» quando due apparecchiature hanno lo stesso nome (I-141): e'
    # quale delle due, nell'ordine delle sigle, non quante.
    quante = Counter(riga.descrizione for riga in righe)
    contate: Counter[str] = Counter()
    numerate: list[RigaDellaTabella] = []
    for riga in righe:
        if quante[riga.descrizione] < 2:
            numerate.append(riga)
            continue
        contate[riga.descrizione] += 1
        numerate.append(
            riga.model_copy(
                update={"descrizione": f"{riga.descrizione} nr {contate[riga.descrizione]}"}
            )
        )
    return numerate


def celle(riga: RigaDellaTabella) -> tuple[str, ...]:
    """Le cinque celle di una riga, come si scrivono: il trattino dove manca il dato."""
    return tuple(
        valore if valore else CELLA_VUOTA
        for valore in (riga.codice, riga.descrizione, riga.caratteristiche, riga.marca, riga.modello)
    )


def impagina_la_tabella(
    righe: list[RigaDellaTabella], frame: SheetFrame
) -> TabellaDelleApparecchiature | None:
    """La tabella misurata e messa **nell'angolo in alto a sinistra dell'area
    del disegno**, contro la squadratura e la testata come la legenda sta contro
    la squadratura a destra. `None` se la tavola non ha apparecchiature.

    Ogni colonna e' larga quanto il suo testo piu' lungo — intestazione
    compresa — piu' il rientro dai due lati, e si arrotonda al passo di griglia:
    le linee della tabella cadono sulla griglia del disegno."""
    if not righe:
        return None
    standard = frame.standard
    corpo_pt = standard.text_small_mm / PT_MM
    passo = standard.grid_mm
    colonne: list[float] = []
    for indice, titolo in enumerate(INTESTAZIONE):
        piu_lungo = max(
            [larghezza_mm(titolo, corpo_pt, True)]
            + [larghezza_mm(celle(riga)[indice], corpo_pt, False) for riga in righe]
        )
        colonne.append(-(-(piu_lungo + 2 * RIENTRO_MM) // passo) * passo)
    area = frame.drawing_rect_mm
    return TabellaDelleApparecchiature(
        x_mm=area.x_mm,
        y_mm=area.y_mm,
        colonne_mm=colonne,
        riga_mm=altezza_della_riga_mm(standard.text_small_mm),
        righe=righe,
    )


def tabella_della_tavola(
    modello: ProjectModel,
    catalogo: ComponentRegistry,
    cartella_dei_nomi: Path,
    sheet: SheetGeometry,
    frame: SheetFrame,
) -> TabellaDelleApparecchiature | None:
    """La tabella di una tavola: le righe dei pezzi disegnati, impaginate.

    Le sigle vengono dalla lettura dell'impianto (D-097, D-098). Se l'impianto
    non si legge — un pezzo che nessuna sorgente raggiunge — la tabella scrive
    le sigle che l'ingegnere ha dato, e il trattino dove non ce ne sono: la
    tavola esce lo stesso, e la lettura lo dice dove serve."""
    naming = Naming.from_directory(cartella_dei_nomi)
    try:
        sigle = read_plant(modello, catalogo, naming).sigle
    except (GraphError, NamingError):
        sigle = {}
    righe = righe_della_tabella(
        modello, catalogo, naming, sigle, (item.component_id for item in sheet.symbols)
    )
    return impagina_la_tabella(righe, frame)


@dataclass(frozen=True)
class TestoDellaTabella:
    testo: str
    x_mm: float
    y_mm: float
    """La linea di base."""
    grassetto: bool


@dataclass(frozen=True)
class TrattiDellaTabella:
    """La tabella come linee e testi: quello che l'SVG e il DXF scrivono."""

    linee: tuple[tuple[float, float, float, float], ...]
    testi: tuple[TestoDellaTabella, ...]
    corpo_mm: float
    spessore_mm: float


def tratti_della_tabella(
    tabella: TabellaDelleApparecchiature, standard: GraphicStandard
) -> TrattiDellaTabella:
    """Le linee — una griglia piena, al tratto sottile della legenda — e i testi:
    l'intestazione in neretto, le righe in chiaro, al corpo dei testi della
    tavola, allineati a sinistra e a meta' riga."""
    sinistra, alto, destra, basso = tabella.riquadro
    linee: list[tuple[float, float, float, float]] = []
    for indice in range(len(tabella.righe) + 2):
        y = round(alto + indice * tabella.riga_mm, 6)
        linee.append((sinistra, y, destra, y))
    x = sinistra
    bordi = [x]
    for larghezza in tabella.colonne_mm:
        x = round(x + larghezza, 6)
        bordi.append(x)
    linee.extend((item, alto, item, basso) for item in bordi)

    corpo = standard.text_small_mm
    testi: list[TestoDellaTabella] = []
    scritte = [INTESTAZIONE, *(celle(riga) for riga in tabella.righe)]
    for fila, valori in enumerate(scritte):
        base = round(
            alto + fila * tabella.riga_mm + tabella.riga_mm / 2 + corpo * MEZZE_MAIUSCOLE_EM, 6
        )
        for colonna, valore in enumerate(valori):
            testi.append(
                TestoDellaTabella(
                    testo=valore,
                    x_mm=round(bordi[colonna] + RIENTRO_MM, 6),
                    y_mm=base,
                    grassetto=fila == 0,
                )
            )
    return TrattiDellaTabella(
        linee=tuple(linee),
        testi=tuple(testi),
        corpo_mm=corpo,
        spessore_mm=standard.line_thin_mm,
    )


def _escape(testo: str) -> str:
    return (
        testo.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def svg_della_tabella(
    tabella: TabellaDelleApparecchiature, standard: GraphicStandard
) -> str:
    """La tabella nell'SVG della tavola: un gruppo, in nero come la legenda."""
    tratti = tratti_della_tabella(tabella, standard)
    parti = [
        f'<g class="tabella-apparecchiature" stroke="black" '
        f'stroke-width="{tratti.spessore_mm:g}" fill="none">'
    ]
    parti.extend(
        f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}"/>'
        for x1, y1, x2, y2 in tratti.linee
    )
    for item in tratti.testi:
        peso = ' font-weight="bold"' if item.grassetto else ""
        parti.append(
            f'<text x="{item.x_mm:g}" y="{item.y_mm:g}" font-family="{FAMIGLIA}" '
            f'font-size="{tratti.corpo_mm:g}"{peso} fill="black" stroke="none">'
            f"{_escape(item.testo)}</text>"
        )
    parti.append("</g>")
    return "".join(parti)


__all__ = [
    "CARATTERISTICHE_PER_MESTIERE",
    "CELLA_VUOTA",
    "FUNZIONI_DELLA_TABELLA",
    "INTESTAZIONE",
    "TestoDellaTabella",
    "TrattiDellaTabella",
    "celle",
    "formatta_il_dato",
    "impagina_la_tabella",
    "righe_della_tabella",
    "svg_della_tabella",
    "tabella_della_tavola",
    "tratti_della_tabella",
]
