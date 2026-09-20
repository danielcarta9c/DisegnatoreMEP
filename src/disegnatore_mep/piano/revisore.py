"""Il revisore: legge i rilievi, **corregge il piano**, e rifa' girare.

⚠ **META' DI QUESTO MODULO E' SUPERATA DA D-157, E VA SOSTITUITA.**

**Che cosa e' superato:** le **cure** (`CURE`, `_cura_a1`, `_cura_b1`, `_cura_b3`,
`_cura_b4`, `_cura_pieghe`) e tutto cio' che **sposta** un pezzo. D-157 dispone
che il revisore **non sposti niente**: dichiara **vincoli** su nodi nominati —
«questi nodi alla stessa quota», «questi T sulla stessa verticale», «questa
tratta passa per questo punto» — e il **pianificatore** ricompone rispettandoli.

**Perche', ed e' una misura, non un'opinione.** Sui cinque impianti di prova la
prima correzione di questo revisore **ha peggiorato la tavola su quattro su
cinque**: ogni mossa e' cieca a quello che le altre regole stavano tenendo — la
cura di A1 spostava il radiatore e piegava un'autostrada, quella di B1 spostava
l'accumulo e rompeva le due primarie, che erano due rette. **Un revisore a mosse
e' un solutore in miniatura**, e sbaglia per la stessa ragione per cui e'
fallito il solutore (D-151).

**Che cosa invece resta, ed e' giusto che sia deterministico:** la **misura**
(`misura`, `Punteggio`), le **condizioni d'arresto**, la guardia che **non
peggiora in silenzio**, e la traccia dei giri. Sono l'occhio che non si stanca,
sotto quello che guarda.

**Dove va il resto:** l'occhio e' un **agente AI** e vive nella skill, nella
stessa forma del pezzo «Capire» — `skill/rivedere/ISTRUZIONI.md`. Non esiste
ancora, ed e' il pacchetto `DRAW-016`. Fino a quel giorno le cure restano qui e
girano, perche' un revisore che non corregge niente non chiude nessun anello: ma
**non sono il modello da seguire**, e chi ne aggiunge una sta allungando la vita
a un pezzo che deve morire.

Architettura: `docs/ARCHITETTURA-DEL-PIANO.md` §5.

---

E' il terzo pezzo della catena di **D-151** — pianificatore, motore, revisore —
ed e' **D-114** scritta il 9 agosto e mai costruita: «il validatore AI smette di
essere un cancello a valle e diventa supervisore in anello chiuso».

**Si costruisce subito** (D-153), e non e' il premio a valle: e' l'attrezzo con
cui si scrivono le regole, una tavola alla volta. Un giro lascia la propria
traccia — piano, rilievi, piano — ed e' quella traccia che diventa una riga
nuova in `docs/regole-del-piano.md`.

## Che cosa entra, che cosa esce

Entra un **piano**; escono **i giri**, ciascuno con la propria tavola, i propri
rilievi e le proprie correzioni. **Ogni correzione porta il nome della regola
che la motiva**: una correzione senza regola non si fa, perche' sarebbe il
solutore travestito — uno spostamento che migliora un numero e non sa dire
perche'.

## Le cure che conosce, e quelle che non conosce

Cura le **quattro regole che il PO ha dettato il 20 settembre** (**D-154**), che
sono le quattro per cui esiste un controllo che sa nominare la propria
violazione:

| rilievo | regola | che cosa muove |
|---|---|---|
| `PIECE_OUTSIDE_ITS_BAND` | **A1** | il pezzo, in orizzontale, fuori dalla fascia di un altro |
| `HIGHWAY_IS_NOT_STRAIGHT` | **B1** | i pezzi della catena, sulla quota che la catena ha gia' |
| `RUN_WITH_TOO_MANY_BENDS` (su un'autostrada) | **B1** | gli stessi |
| `PARALLEL_MACHINES_WITHOUT_A_COLLECTOR` | **B3** | i raccordi del collettore, sulla stessa verticale |
| `INLINE_ORGAN_BREAKS_THE_RUN` | **B4** | l'organo, sulla quota delle due tratte che unisce |

**Quello che non cura, e non per dimenticanza.**

* `DRAWING_ALL_ON_ONE_SIDE` (**D3**) e' il primo difetto aperto del
  pianificatore, e la cura ovvia — allargare il disegno per distribuirlo — e'
  **la mossa che il PO ha gia' bocciato**: «ha poco senso questo stretch fatto
  cosi' per il gusto di riempire la tavola… era meglio prima» (D-142 ritirata da
  **D-149**). Un revisore che la rifacesse da solo rifarebbe l'errore piu' caro
  di questo progetto. Si nomina e si lascia a chi compone.
* `TOO_MANY_CROSSINGS` non e' il difetto di un pezzo: e' l'esito dell'intera
  composizione, e nessuno spostamento singolo lo chiude.
* `SHEET_BARELY_FILLED` e `SHEET_TOO_FULL` sono **misure**, non difetti da
  chiudere (**D-149**).

Un rilievo senza cura non sparisce e non si abbassa di grado: finisce in
`Revisione.non_curati`, con il proprio codice, ed e' lavoro per chi compone.

## L'occhio che il codice non ha

D-153 punto 3 dice che il metro del revisore **non e' solo numerico**: guarda la
tavola, con accanto quelle del disegnatore del PO. Questo modulo **non guarda
niente**: chiude l'anello sui rilievi misurabili e consegna, per ogni giro, la
tavola che ne e' uscita. Lo sguardo lo mette l'agente che lo governa, ed e' il
punto in cui nascono le righe nuove del foglio delle regole. Dirlo e' meglio che
lasciarlo credere.
"""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import SheetFrame
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.symbol import PortFace
from disegnatore_mep.layout.autostrade import (
    AutostradaInTavola,
    autostrade_del_progetto,
    pieghe_della_tratta,
    porte_in_tavola,
)
from disegnatore_mep.layout.geometry import (
    DrawingGeometry,
    PlacedSymbol,
    SheetGeometry,
)
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import IssueSeverity
from disegnatore_mep.validation.issues import ValidationIssue
from disegnatore_mep.validation.regole import (
    FASCE,
    fascia_del_pezzo,
    rilievi_delle_regole,
)

from .esecutore import EsitoDelPiano, esegui_piano
from .formato import PezzoNelPiano, PianoDiComposizione

TETTO_DEI_GIRI = 6
"""Quanti giri, al piu', prima di fermarsi e dirlo.

Un tetto dichiarato, non una taratura sulla qualita': serve a garantire che
l'anello **finisca**, non a dire quanti giri bastano. I cinque giri di
correzione a mano della prova del 20 settembre sono il precedente
(`docs/collaudi/PROVA-PIANO/README.md`); sei lascia un margine di uno.
"""

CODICI_DELLE_REGOLE = frozenset(
    {
        "PIECE_OUTSIDE_ITS_BAND",
        "HIGHWAY_IS_NOT_STRAIGHT",
        "PARALLEL_MACHINES_WITHOUT_A_COLLECTOR",
        "INLINE_ORGAN_BREAKS_THE_RUN",
    }
)
"""I quattro rilievi che `validation/regole.py` misura, e **solo quelli**.

Sono le violazioni vere e proprie: le conta il punteggio, e sono quelle che
decidono se la revisione e' chiusa. `RUN_WITH_TOO_MANY_BENDS` non sta qui —
resta un avviso del preflight — perche' su un'autostrada dice la stessa cosa di
`HIGHWAY_IS_NOT_STRAIGHT` e contarli tutt'e due sarebbe contare due volte."""

REGOLA_DEL_RILIEVO: dict[str, str] = {
    "PIECE_OUTSIDE_ITS_BAND": "A1",
    "HIGHWAY_IS_NOT_STRAIGHT": "B1",
    "RUN_WITH_TOO_MANY_BENDS": "B1",
    "PARALLEL_MACHINES_WITHOUT_A_COLLECTOR": "B3",
    "INLINE_ORGAN_BREAKS_THE_RUN": "B4",
}
"""Quale regola di `docs/regole-del-piano.md` motiva la cura di quale rilievo.

E' la tabella che rende vero il criterio «**ogni correzione porta il nome della
regola**»: una cura si scrive **entrando da qui**, e un rilievo che non e' in
questa mappa non si cura — si nomina.
"""


@dataclass(frozen=True)
class Punteggio:
    """Le sei misure con cui un giro si confronta col precedente.

    L'ordine delle voci **e'** la gerarchia di giudizio, e per questo e' un
    ordine lessicografico e non una somma pesata: una somma si compra sempre —
    e' il difetto che ha ucciso il solutore (**D-151**) — mentre qui una tratta
    ceduta non si compra con dieci pieghe in meno.
    """

    bloccanti: int
    cedute: int
    violazioni: int
    avvisi: int
    pieghe: int
    incroci: int

    VOCI = ("bloccanti", "cedute", "violazioni", "avvisi", "pieghe", "incroci")

    @property
    def ordine(self) -> tuple[int, ...]:
        return tuple(getattr(self, voce) for voce in self.VOCI)

    @property
    def chiuso(self) -> bool:
        """Vero quando non resta niente da correggere: nessun rilievo
        bloccante, nessuna tratta ceduta, nessuna regola violata."""
        return self.bloccanti == 0 and self.cedute == 0 and self.violazioni == 0

    def peggiorate(self, prima: "Punteggio") -> tuple[str, ...]:
        """Le voci che questo giro ha peggiorato rispetto al precedente."""
        return tuple(
            voce
            for voce in self.VOCI
            if getattr(self, voce) > getattr(prima, voce)
        )

    def migliorate(self, prima: "Punteggio") -> tuple[str, ...]:
        return tuple(
            voce
            for voce in self.VOCI
            if getattr(self, voce) < getattr(prima, voce)
        )

    def racconto(self) -> str:
        return ", ".join(
            f"{voce} {getattr(self, voce)}" for voce in self.VOCI
        )


@dataclass(frozen=True)
class Correzione:
    """Uno spostamento, e **la regola che lo motiva**.

    `regola` non e' decorativa e non ha un valore di comodo: una correzione che
    non sa dire quale regola la vuole non si fa (criterio 2 di `DRAW-015`).
    """

    pezzo: str
    da: tuple[float, float]
    a: tuple[float, float]
    regola: str
    rilievo: str
    perche: str
    aggiunto: bool = False
    """Vero quando il pezzo **non era nel piano** e il revisore ce l'ha messo.

    Succede per i pezzi che la semina trascina dietro al proprio: finche' stanno
    dove devono non hanno bisogno di una riga nel piano, ma nel momento in cui
    vanno spostati quella riga serve, ed e' del pianificatore."""

    def racconto(self) -> str:
        return (
            f"{self.pezzo}: ({self.da[0]:.1f}, {self.da[1]:.1f}) -> "
            f"({self.a[0]:.1f}, {self.a[1]:.1f}) — regola {self.regola} "
            f"[{self.rilievo}]{' (messo nel piano adesso)' if self.aggiunto else ''}"
        )


@dataclass(frozen=True)
class Giro:
    """Un giro dell'anello: il piano che e' entrato, e che cosa ne e' uscito."""

    numero: int
    piano: PianoDiComposizione
    esito: EsitoDelPiano
    rilievi: tuple[ValidationIssue, ...]
    punteggio: Punteggio
    correzioni: tuple[Correzione, ...] = ()
    scambio: tuple[str, ...] = ()
    """Le misure peggiorate mentre l'ordine nel complesso migliorava.

    **Il revisore non peggiora in silenzio**: quando chiude un difetto grave al
    prezzo di uno lieve, il prezzo si scrive qui invece di sparire nel saldo."""


@dataclass(frozen=True)
class Revisione:
    """L'anello intero: i giri, quello che consegna, e perche' si e' fermato."""

    giri: tuple[Giro, ...]
    migliore: int
    perche_si_e_fermato: str
    non_curati: tuple[str, ...] = ()

    @property
    def giro_migliore(self) -> Giro:
        return self.giri[self.migliore]

    @property
    def piano_finale(self) -> PianoDiComposizione:
        return self.giro_migliore.piano

    @property
    def ha_migliorato(self) -> bool:
        return (
            len(self.giri) > 1
            and self.giro_migliore.punteggio.ordine < self.giri[0].punteggio.ordine
        )

    @property
    def giri_serviti(self) -> int:
        """Quanti giri sono serviti per arrivare alla tavola che consegna.

        Il primo giro e' la tavola del piano cosi' com'e': se consegna quello,
        i giri di revisione sono **zero**."""
        return self.migliore


# --- la misura di un giro -----------------------------------------------------


def _incroci(disegno: DrawingGeometry) -> int:
    return len(
        {
            (punto.x_mm, punto.y_mm)
            for foglio in disegno.sheets
            for route in foglio.routes
            for punto in route.crossings
        }
    )


def _pieghe(disegno: DrawingGeometry) -> int:
    """Le pieghe di tutta la tavola, contate come le conta il preflight.

    Si chiama `layout.autostrade.pieghe_della_tratta`, che e' la stessa funzione
    che `bends_per_run` usa: due conti diversi della stessa cosa sarebbero due
    verita' diverse sulla stessa tavola.
    """
    return sum(
        pieghe_della_tratta(route)
        for foglio in disegno.sheets
        for route in foglio.routes
    )


def misura(
    esito: EsitoDelPiano, rilievi: Sequence[ValidationIssue]
) -> Punteggio:
    """Le sei misure di questa tavola.

    Un piano che **non si instrada** non ha una tavola da misurare: prende il
    punteggio piu' alto che esista su tutte le voci, cosi' l'ordine lo mette
    sotto a qualunque tavola uscita, per brutta che sia. Una tavola c'e' o non
    c'e': non e' una differenza di grado.
    """
    if esito.disegno is None:
        grande = 10**6
        return Punteggio(grande, grande, grande, grande, grande, grande)
    # **Una violazione si conta una volta sola.** `RUN_WITH_TOO_MANY_BENDS`, da
    # quando il preflight sa che cos'e' un'autostrada, dice **la stessa cosa**
    # che dice B1 su una catena di una tratta sola: contarli tutt'e due
    # gonfierebbe il punteggio e farebbe sembrare peggiore una tavola che ha un
    # difetto solo. Le violazioni sono quelle che `regole.py` misura; la piega
    # dello stacchetto resta fra gli avvisi, dove e' sempre stata.
    violazioni = sum(1 for item in rilievi if item.code in CODICI_DELLE_REGOLE)
    return Punteggio(
        bloccanti=sum(
            1 for item in rilievi if item.severity is IssueSeverity.BLOCKING
        ),
        cedute=sum(
            1
            for foglio in esito.disegno.sheets
            for route in foglio.routes
            if route.unresolved
        ),
        violazioni=violazioni,
        avvisi=sum(
            1 for item in rilievi if item.severity is IssueSeverity.WARNING
        ),
        pieghe=_pieghe(esito.disegno),
        incroci=_incroci(esito.disegno),
    )


# --- dalla tavola al piano ----------------------------------------------------


def _scarto_di_centratura(esito: EsitoDelPiano) -> tuple[float, float]:
    """Di quanto la tavola consegnata e' traslata rispetto alla posa.

    `compose.centre_vertically` sposta il blocco dopo l'instradamento: le
    coordinate che i rilievi nominano **non sono** quelle del piano, e una cura
    che le scrivesse tali e quali sposterebbe i pezzi due volte. Lo scarto e' lo
    stesso per tutti i pezzi, quindi basta leggerlo da uno.
    """
    if esito.disegno is None or not esito.disegno.sheets:
        return (0.0, 0.0)
    dove = {item.component_id: item for item in esito.posa}
    for posato in esito.disegno.sheets[0].symbols:
        prima = dove.get(posato.component_id)
        if prima is not None:
            return (
                posato.origin.x_mm - prima.origin.x_mm,
                posato.origin.y_mm - prima.origin.y_mm,
            )
    return (0.0, 0.0)


@dataclass(frozen=True)
class _Tavolo:
    """Tutto cio' che una cura ha bisogno di leggere, raccolto una volta sola."""

    modello: ProjectModel
    catalogo: ComponentRegistry
    piano: PianoDiComposizione
    esito: EsitoDelPiano
    foglio: SheetGeometry
    frame: SheetFrame
    scarto: tuple[float, float]

    @property
    def passo_mm(self) -> float:
        return self.frame.standard.grid_mm

    def posato(self, component_id: str) -> PlacedSymbol | None:
        for item in self.foglio.symbols:
            if item.component_id == component_id:
                return item
        return None

    def nel_piano(self, component_id: str) -> tuple[float, float] | None:
        """Dove il piano mette questo pezzo, tolta la centratura."""
        posato = self.posato(component_id)
        if posato is None:
            return None
        return (
            posato.origin.x_mm - self.scarto[0],
            posato.origin.y_mm - self.scarto[1],
        )

    def in_griglia(self, valore: float, base: float) -> float:
        return base + round((valore - base) / self.passo_mm) * self.passo_mm

    def e_un_raccordo(self, component_id: str) -> bool:
        for item in self.modello.components:
            if item.id == component_id:
                return bool(self.catalogo.get(item.definition_id).is_a_fitting)
        return False


def _sposta(
    tavolo: _Tavolo,
    component_id: str,
    dx_mm: float,
    dy_mm: float,
    regola: str,
    rilievo: ValidationIssue,
) -> Correzione | None:
    """Uno spostamento, in griglia, con la propria regola accanto."""
    dove = tavolo.nel_piano(component_id)
    if dove is None:
        return None
    area = tavolo.frame.drawing_rect_mm
    nuovo = (
        tavolo.in_griglia(dove[0] + dx_mm, area.x_mm),
        tavolo.in_griglia(dove[1] + dy_mm, area.y_mm),
    )
    if abs(nuovo[0] - dove[0]) < 1e-9 and abs(nuovo[1] - dove[1]) < 1e-9:
        return None
    return Correzione(
        pezzo=component_id,
        da=dove,
        a=nuovo,
        regola=regola,
        rilievo=rilievo.code,
        perche=rilievo.message,
        aggiunto=component_id not in tavolo.piano.pezzi,
    )


def _frequente(valori: Iterable[float]) -> float | None:
    """Il valore piu' frequente, e a parita' quello di mezzo.

    Si prende il **piu' frequente** e non la media perche' la cura deve muovere
    **il meno possibile**: chi sta gia' dove va, ci resta. La media sposterebbe
    tutti.
    """
    elenco = sorted(round(valore, 3) for valore in valori)
    if not elenco:
        return None
    quanti: dict[float, int] = {}
    for valore in elenco:
        quanti[valore] = quanti.get(valore, 0) + 1
    massimo = max(quanti.values())
    candidati = [valore for valore, conto in quanti.items() if conto == massimo]
    return candidati[len(candidati) // 2]


# --- le cure, una per regola --------------------------------------------------


def _cura_a1(tavolo: _Tavolo, rilievo: ValidationIssue) -> list[Correzione]:
    """**A1** — il pezzo torna nella propria fascia, in orizzontale.

    Le tre fasce stanno da sinistra a destra nell'ordine di `FASCE`: il pezzo si
    porta nella striscia libera fra la fascia che lo precede e quella che lo
    segue. Se quella striscia non esiste — le altre due si toccano — non si
    inventa spazio: la cura non si applica e il rilievo resta nominato.

    **Si sposta sempre verso destra, e mai il pezzo a monte.** Un accavallamento
    fra due fasce lo nominano due rilievi, uno per pezzo: se si curassero
    tutt'e due, i due pezzi si allontanerebbero l'uno dall'altro e il disegno si
    allargherebbe da solo. Si cura **quello della fascia piu' a valle**, e lo si
    porta a destra dell'altra; l'altro rilievo non trova niente da fare e si
    spegne con lui. La ragione non e' di comodo: **l'ordine del processo si
    legge da sinistra a destra** (D-060, `regole-del-piano.md` §A3), quindi chi
    e' a valle e' quello che sta nel posto sbagliato.

    Misurato il 20 settembre sull'impianto 1: curando invece il pezzo a monte,
    l'accumulo si spostava di 22,5 mm a sinistra e **il piano non si instradava
    piu'**. Il revisore lo diceva e si fermava — cioe' faceva il suo mestiere —
    ma la cura era quella sbagliata.
    """
    if len(rilievo.entity_ids) < 2:
        return []
    component_id = rilievo.entity_ids[1]
    posato = tavolo.posato(component_id)
    if posato is None:
        return []
    definizioni = {item.id: item.definition_id for item in tavolo.modello.components}
    from disegnatore_mep.layout.hierarchy import user_machines

    utenze = user_machines(tavolo.modello, tavolo.catalogo)
    fascia_di: dict[str, str] = {}
    for item in tavolo.foglio.symbols:
        definition_id = definizioni.get(item.component_id)
        if definition_id is None:
            continue
        fascia = fascia_del_pezzo(
            tavolo.catalogo.get(definition_id), utenze, item.component_id
        )
        if fascia is not None:
            fascia_di[item.component_id] = fascia
    mia = fascia_di.get(component_id)
    if mia is None:
        return []

    def bordi(fascia: str) -> tuple[float, float] | None:
        pezzi = [
            item
            for item in tavolo.foglio.symbols
            if fascia_di.get(item.component_id) == fascia
            and item.component_id != component_id
        ]
        if not pezzi:
            return None
        return (
            min(item.origin.x_mm for item in pezzi),
            max(item.origin.x_mm + item.width_mm for item in pezzi),
        )

    area = tavolo.frame.drawing_rect_mm
    indice = FASCE.index(mia)
    sinistra = area.x_mm
    accavallata_a_monte = False
    for altra in FASCE[:indice]:
        confine = bordi(altra)
        if confine is None:
            continue
        if posato.origin.x_mm < confine[1] - 1e-9:
            accavallata_a_monte = True
        sinistra = max(sinistra, confine[1] + tavolo.passo_mm)
    if not accavallata_a_monte:
        # L'accavallamento c'e', ma con una fascia **a valle**: il pezzo nel
        # posto sbagliato e' l'altro, e sara' il suo rilievo a muoverlo.
        return []
    destra = area.x_mm + area.width_mm - posato.width_mm
    if sinistra > destra:
        return []
    voluto = min(max(posato.origin.x_mm, sinistra), destra)
    corretta = _sposta(
        tavolo, component_id, voluto - posato.origin.x_mm, 0.0, "A1", rilievo
    )
    return [corretta] if corretta else []


def _autostrada_del_rilievo(
    tavolo: _Tavolo, rilievo: ValidationIssue
) -> AutostradaInTavola | None:
    """Quale catena nomina questo rilievo, fra quelle dell'impianto."""
    nominate = set(rilievo.entity_ids)
    migliore: tuple[int, AutostradaInTavola] | None = None
    for autostrada in autostrade_del_progetto(tavolo.modello, tavolo.catalogo):
        comuni = len(autostrada.connection_ids & nominate)
        if comuni and (migliore is None or comuni > migliore[0]):
            migliore = (comuni, autostrada)
    return migliore[1] if migliore else None


def _catene_a_posto(tavolo: _Tavolo, rilievi: Sequence[ValidationIssue]) -> frozenset[str]:
    """I pezzi che stanno su un'autostrada **gia' nella propria forma**.

    Sono intoccabili, ed e' la regola piu' importante di tutto il revisore:
    **non si smonta cio' che e' a posto per aggiustare altro.** Senza questa
    guardia, misurato il 20 settembre sull'impianto 1, la cura di B1 sulla
    tratta `radiatori -> accumulo` spostava l'accumulo di 15 mm e piegava **le
    due primarie**, che erano due rette: il saldo peggiorava e il disegno pure
    — lo squilibrio fra i quadranti passava da 5,2 a 11,5 volte.
    """
    storte = {
        connection_id
        for item in rilievi
        if item.code == "HIGHWAY_IS_NOT_STRAIGHT"
        for connection_id in item.entity_ids
    }
    intoccabili: set[str] = set()
    for autostrada in autostrade_del_progetto(tavolo.modello, tavolo.catalogo):
        if not (autostrada.connection_ids & storte):
            intoccabili.update(autostrada.pezzi)
    return frozenset(intoccabili)


def _cura_b1(tavolo: _Tavolo, rilievo: ValidationIssue) -> list[Correzione]:
    """**B1** — la catena si rimette su **una** quota.

    Si prende la quota che la catena gia' ha piu' spesso e ci si portano sopra i
    pezzi che ne sono fuori: chi e' gia' in linea non si muove. Un pezzo che
    porta **due** porte della catena a quote diverse non si puo' allineare
    spostandolo — l'allineamento glielo dovrebbe dare una rotazione, che e'
    un'altra decisione — e si lascia dov'e'.
    """
    autostrada = _autostrada_del_rilievo(tavolo, rilievo)
    if autostrada is None:
        return []
    porte = porte_in_tavola(tavolo.foglio, tavolo.modello, tavolo.catalogo)
    quote: dict[str, list[tuple[float, float]]] = {}
    orizzontale = 0.0
    verticale = 0.0
    for entrata, uscita in autostrada.passi:
        qui = porte.get((entrata.component_id, entrata.port_id))
        la = porte.get((uscita.component_id, uscita.port_id))
        if qui is None or la is None:
            continue
        orizzontale += abs(qui[0].x_mm - la[0].x_mm)
        verticale += abs(qui[0].y_mm - la[0].y_mm)
    lungo_x = orizzontale >= verticale
    for componente, porta in [
        (ref.component_id, ref.port_id)
        for passo in autostrada.passi
        for ref in passo
    ]:
        dove = porte.get((componente, porta))
        if dove is None:
            continue
        quote.setdefault(componente, []).append((dove[0].x_mm, dove[0].y_mm))
    tutte = [
        (coppia[1] if lungo_x else coppia[0])
        for coppie in quote.values()
        for coppia in coppie
    ]
    voluta = _frequente(tutte)
    if voluta is None:
        return []
    corrette: list[Correzione] = []
    for componente, coppie in sorted(quote.items()):
        misure = {round(coppia[1] if lungo_x else coppia[0], 3) for coppia in coppie}
        if len(misure) > 1:
            # Due porte della catena a quote diverse sullo stesso pezzo: non e'
            # una posizione da correggere, e' una forma del simbolo.
            continue
        sua = next(iter(misure))
        if abs(sua - voluta) < 1e-9:
            continue
        corretta = _sposta(
            tavolo,
            componente,
            0.0 if lungo_x else voluta - sua,
            voluta - sua if lungo_x else 0.0,
            "B1",
            rilievo,
        )
        if corretta:
            corrette.append(corretta)
    return corrette


def _cura_b3(tavolo: _Tavolo, rilievo: ValidationIssue) -> list[Correzione]:
    """**B3** — i raccordi del collettore tornano sulla stessa verticale.

    Si muovono **solo i raccordi** nominati dal rilievo, mai le macchine: un
    collettore e' una catena di T, e raddrizzarlo non deve spostare le pompe che
    ci pendono. La verticale e' quella su cui gia' stanno di piu'.
    """
    raccordi = [
        component_id
        for component_id in rilievo.entity_ids[1:]
        if tavolo.e_un_raccordo(component_id)
    ]
    posati = [
        item for item in tavolo.foglio.symbols if item.component_id in set(raccordi)
    ]
    if len(posati) < 2:
        return []
    centri = {
        item.component_id: item.origin.x_mm + item.width_mm / 2 for item in posati
    }
    voluta = _frequente(centri.values())
    if voluta is None:
        return []
    corrette: list[Correzione] = []
    for component_id, centro in sorted(centri.items()):
        if abs(centro - voluta) < 1e-9:
            continue
        corretta = _sposta(
            tavolo, component_id, voluta - centro, 0.0, "B3", rilievo
        )
        if corretta:
            corrette.append(corretta)
    return corrette


def _cura_b4(tavolo: _Tavolo, rilievo: ValidationIssue) -> list[Correzione]:
    """**B4** — l'organo in linea si mette sulla quota del tratto che regge.

    Le sue due porte in linea stanno su una quota sola per costruzione: quello
    che non torna e' **dove** sta quella quota. Si porta l'organo sulla quota
    che le due tratte hanno all'altro capo, cosi' la linea gli passa dentro
    invece di piegarsi intorno a lui.
    """
    if len(rilievo.entity_ids) < 2:
        return []
    component_id = rilievo.entity_ids[1]
    posato = tavolo.posato(component_id)
    if posato is None:
        return []
    porte = porte_in_tavola(tavolo.foglio, tavolo.modello, tavolo.catalogo)
    mie = [
        (chiave[1], valore)
        for chiave, valore in porte.items()
        if chiave[0] == component_id
    ]
    orizzontali = [
        valore for _, valore in mie if valore[1] in (PortFace.LEFT, PortFace.RIGHT)
    ]
    verticali = [
        valore for _, valore in mie if valore[1] in (PortFace.TOP, PortFace.BOTTOM)
    ]
    lungo_x = len(orizzontali) >= 2
    if not lungo_x and len(verticali) < 2:
        return []
    coppia = orizzontali if lungo_x else verticali
    sua = coppia[0][0].y_mm if lungo_x else coppia[0][0].x_mm

    # La quota che le due tratte chiedono: dove va a finire il loro **altro**
    # capo, quello che non sta su questo pezzo.
    volute: list[float] = []
    connessioni = set(rilievo.entity_ids[2:])
    for route in tavolo.foglio.routes:
        if not connessioni & set(route.connection_ids):
            continue
        for segmento in route.segments:
            if len(segmento) < 2:
                continue
            for punto in (segmento[0], segmento[-1]):
                distante = abs(
                    (punto.y_mm if lungo_x else punto.x_mm) - sua
                )
                if distante > 1e-9:
                    volute.append(punto.y_mm if lungo_x else punto.x_mm)
    voluta = _frequente(volute)
    if voluta is None:
        return []
    corretta = _sposta(
        tavolo,
        component_id,
        0.0 if lungo_x else voluta - sua,
        voluta - sua if lungo_x else 0.0,
        "B4",
        rilievo,
    )
    return [corretta] if corretta else []


def _cura_pieghe(tavolo: _Tavolo, rilievo: ValidationIssue) -> list[Correzione]:
    """`RUN_WITH_TOO_MANY_BENDS`, **ma solo su un'autostrada** (B1).

    Su uno stacchetto la stessa piega non e' la stessa cosa — e' esattamente il
    difetto che ha generato **D-151**, «abbiamo ottimizzato le curve sugli
    attacchetti e abbiamo fatto sta curva senza senso» — e li' il revisore non
    tocca niente.
    """
    if _autostrada_del_rilievo(tavolo, rilievo) is None:
        return []
    return _cura_b1(tavolo, rilievo)


CURE = {
    "PIECE_OUTSIDE_ITS_BAND": _cura_a1,
    "HIGHWAY_IS_NOT_STRAIGHT": _cura_b1,
    "RUN_WITH_TOO_MANY_BENDS": _cura_pieghe,
    "PARALLEL_MACHINES_WITHOUT_A_COLLECTOR": _cura_b3,
    "INLINE_ORGAN_BREAKS_THE_RUN": _cura_b4,
}


# --- l'anello -----------------------------------------------------------------


def _rilievi_di(
    esito: EsitoDelPiano, modello: ProjectModel, catalogo: ComponentRegistry
) -> tuple[ValidationIssue, ...]:
    """I rilievi del preflight e quelli delle regole, in un elenco solo."""
    if esito.disegno is None:
        return ()
    return (
        *esito.rilievi,
        *rilievi_delle_regole(esito.disegno, esito.frame, catalogo, modello),
    )


def _correggi(
    tavolo: _Tavolo, rilievi: Sequence[ValidationIssue]
) -> tuple[list[Correzione], list[str]]:
    """Le correzioni che i rilievi motivano, e i codici che nessuna cura copre.

    Si corregge **un rilievo per giro**, il primo nell'ordine delle regole: una
    cura cambia la tavola, e le cure successive leggerebbero una tavola che non
    esiste piu'. E' lo stesso motivo per cui l'anello gira invece di risolvere.
    """
    non_curati: list[str] = []
    intoccabili = _catene_a_posto(tavolo, rilievi)
    gia_detto = {
        connection_id
        for item in rilievi
        if item.code == "HIGHWAY_IS_NOT_STRAIGHT"
        for connection_id in item.entity_ids
    }
    for rilievo in rilievi:
        # **Lo stesso difetto non si cura due volte.** Su un'autostrada
        # `RUN_WITH_TOO_MANY_BENDS` e `HIGHWAY_IS_NOT_STRAIGHT` nominano la
        # stessa piega: la cura la fa B1, che vede la catena intera.
        if rilievo.code == "RUN_WITH_TOO_MANY_BENDS" and (
            gia_detto & set(rilievo.entity_ids)
        ):
            continue
        cura = CURE.get(rilievo.code)
        if cura is None:
            if rilievo.code not in non_curati:
                non_curati.append(rilievo.code)
            continue
        # **La guardia vale verso il basso, non verso l'alto.** Una catena gia'
        # dritta non si smonta per raddrizzarne un'altra (stesso grado) ne' per
        # allineare un organo (grado piu' basso); ma **A1 viene prima di B1**
        # (`ORDINE_DELLE_REGOLE`: prima dove stanno i pezzi, poi come corrono le
        # linee), e un pezzo nella fascia sbagliata si sposta anche se una
        # catena ne soffre — poi sara' B1 a dire quanto.
        regola = REGOLA_DEL_RILIEVO[rilievo.code]
        protetti = frozenset() if regola == "A1" else intoccabili
        corrette = [
            item for item in cura(tavolo, rilievo) if item.pezzo not in protetti
        ]
        if corrette:
            return corrette, non_curati
        if rilievo.code not in non_curati:
            non_curati.append(rilievo.code)
    return [], non_curati


def _ordina(rilievi: Sequence[ValidationIssue]) -> list[ValidationIssue]:
    """Prima cio' che blocca, poi le regole nel loro ordine, poi il resto.

    **Prima dove stanno i pezzi, poi come corrono le linee**: una linea storta
    puo' essere la conseguenza di un pezzo nella fascia sbagliata, mai il
    contrario.
    """
    peso = {"A1": 1, "B1": 2, "B3": 3, "B4": 4}

    def chiave(item: ValidationIssue) -> tuple[int, int, str]:
        return (
            0 if item.severity is IssueSeverity.BLOCKING else 1,
            peso.get(REGOLA_DEL_RILIEVO.get(item.code, ""), 9),
            item.code,
        )

    return sorted(rilievi, key=chiave)


def _applica(
    piano: PianoDiComposizione, correzioni: Sequence[Correzione]
) -> PianoDiComposizione:
    """Il piano corretto: le stesse note, i pezzi spostati, la regola accanto."""
    pezzi = dict(piano.pezzi)
    for correzione in correzioni:
        vecchio = pezzi.get(correzione.pezzo)
        pezzi[correzione.pezzo] = PezzoNelPiano(
            x=correzione.a[0],
            y=correzione.a[1],
            rotazione=vecchio.rotazione if vecchio is not None else None,
            regola=correzione.regola,
        )
    return piano.model_copy(update={"pezzi": pezzi})


def revisiona(
    modello: ProjectModel,
    piano: PianoDiComposizione,
    catalogo: ComponentRegistry,
    simboli: SymbolRegistry,
    naming: Path,
    tetto: int = TETTO_DEI_GIRI,
) -> Revisione:
    """L'anello chiuso: esegui, misura, correggi il piano, rifai girare.

    Si ferma per uno di **quattro** motivi, e in tutti e quattro lo dice
    (criterio del pacchetto: «in tutti e tre i casi dice perche' si e'
    fermato»):

    1. **non resta niente da correggere** — nessun bloccante, nessuna ceduta,
       nessuna regola violata;
    2. **un giro non migliora** — l'ordine lessicografico non scende, oppure
       nessuna cura si applica ai rilievi che restano;
    3. **un giro peggiora** — e allora si consegna il giro **precedente**, e le
       misure peggiorate si nominano;
    4. **il tetto dei giri**.

    Quando l'ordine migliora ma una misura singola peggiora, non ci si ferma:
    si scrive lo **scambio** nel giro, perche' un prezzo pagato in silenzio e'
    un peggioramento in silenzio.
    """
    giri: list[Giro] = []
    non_curati: list[str] = []
    corrente = piano
    perche = f"il tetto dei giri ({tetto})"
    migliore = 0

    for numero in range(tetto + 1):
        esito = esegui_piano(modello, corrente, catalogo, simboli, naming)
        rilievi = _ordina(_rilievi_di(esito, modello, catalogo))
        punteggio = misura(esito, rilievi)
        scambio: tuple[str, ...] = ()
        if giri:
            prima = giri[-1].punteggio
            if punteggio.ordine > prima.ordine:
                giri.append(
                    Giro(
                        numero=numero,
                        piano=corrente,
                        esito=esito,
                        rilievi=tuple(rilievi),
                        punteggio=punteggio,
                        scambio=punteggio.peggiorate(prima),
                    )
                )
                migliore = len(giri) - 2
                perche = (
                    "la correzione ha tolto la tavola: il piano corretto non si "
                    f"instrada piu' ({esito.errore}). Si consegna il giro precedente"
                    if esito.disegno is None
                    else "un giro ha peggiorato la tavola su "
                    + ", ".join(punteggio.peggiorate(prima))
                    + f" ({prima.racconto()} -> {punteggio.racconto()}): "
                    "si consegna il giro precedente"
                )
                break
            scambio = punteggio.peggiorate(prima)

        giri.append(
            Giro(
                numero=numero,
                piano=corrente,
                esito=esito,
                rilievi=tuple(rilievi),
                punteggio=punteggio,
                scambio=scambio,
            )
        )
        migliore = len(giri) - 1

        if punteggio.chiuso:
            perche = "non resta nessun rilievo da correggere"
            break
        if esito.disegno is None:
            perche = (
                "il piano non si instrada, e il revisore non lo ricompone: "
                f"{esito.errore}"
            )
            break
        if len(giri) > 1 and punteggio.ordine >= giri[-2].punteggio.ordine:
            perche = "un giro non migliora la tavola"
            break
        if numero == tetto:
            break

        tavolo = _Tavolo(
            modello=modello,
            catalogo=catalogo,
            piano=corrente,
            esito=esito,
            foglio=esito.disegno.sheets[0],
            frame=esito.frame,
            scarto=_scarto_di_centratura(esito),
        )
        correzioni, scoperti = _correggi(tavolo, rilievi)
        for codice in scoperti:
            if codice not in non_curati:
                non_curati.append(codice)
        if not correzioni:
            perche = (
                "nessuna cura si applica ai rilievi che restano ("
                + ", ".join(sorted(set(scoperti)))
                + ")"
            )
            break
        giri[-1] = replace(giri[-1], correzioni=tuple(correzioni))
        corrente = _applica(corrente, correzioni)

    return Revisione(
        giri=tuple(giri),
        migliore=migliore,
        perche_si_e_fermato=perche,
        non_curati=tuple(non_curati),
    )


__all__ = [
    "CURE",
    "REGOLA_DEL_RILIEVO",
    "TETTO_DEI_GIRI",
    "Correzione",
    "Giro",
    "Punteggio",
    "Revisione",
    "misura",
    "revisiona",
]
