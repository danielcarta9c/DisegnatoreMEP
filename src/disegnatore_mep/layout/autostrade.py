"""L'autostrada sulla tavola: il ponte fra la catena del modello e la spezzata disegnata.

**Il difetto che questo modulo chiude.** `highways.py` sa gia' che cos'e'
un'autostrada, ma lavora sui `Trunk` del **modello**: sa quali connessioni
formano una catena e quante curve quella catena ha diritto di fare. Il
preflight, invece, misura `RoutedTrunk` — la **spezzata della tavola** — e non
sa niente di catene: `RUN_WITH_TOO_MANY_BENDS` conta una piega della dorsale
come una piega di uno stacchetto. E' il difetto che il PO ha visto il 20
settembre — «abbiamo ottimizzato le curve e gli attraversamenti sugli
attacchetti e abbiamo fatto sta curva senza senso» — ed e' quello che ha
generato **D-151**.

Fra i due mondi c'e' un aggancio solo, e non e' una coordinata:
`RoutedTrunk.connection_ids` e `Trunk.connection_ids` sono **la stessa chiave**,
perche' una tratta instradata e' l'immagine di una tratta del modello. Tutto
questo modulo sta su quella chiave.

**Che cosa questo modulo non decide.** Non decide che cos'e' un'autostrada —
lo decide `hierarchy.hierarchy_of` — ne' quante curve le spettano: quello e'
`Highway.turns_allowed`, cioe' zero per la struttura fra le macchine di spina e
**una** per la strada che porta ai terminali (**D-144**). Qui si traduce, e
basta.
"""

from collections.abc import Iterable
from dataclasses import dataclass

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.symbol import PortFace
from disegnatore_mep.model.project import PortRef, ProjectModel

from .geometry import TOLERANCE_MM, Point, RoutedTrunk, SheetGeometry, moves_of
from .highways import highways
from .trunks import Trunk, build_trunks

_TOLLERANZA_MM = TOLERANCE_MM
"""Quanto due coordinate possono differire ed essere ancora la stessa.

E' la tolleranza di confronto fra numeri in virgola mobile del modello
geometrico, la stessa che `moves_of` usa per scartare un tratto degenere: non
e' una soglia di disegno e non si tara.
"""


@dataclass(frozen=True)
class AutostradaInTavola:
    """Un'autostrada come la tavola la porta: le sue tratte, e il suo bilancio.

    `connection_ids` e' l'insieme di **tutte** le connessioni della catena: e'
    con quello che si riconosce una tratta instradata. `catene` e `passi` la
    percorrono nell'ordine giusto — quello della catena, non quello in cui il
    file ha scritto le connessioni — e servono a misurare le pieghe **sui
    crocevia**, dove la catena si piega senza che nessuna delle sue tratte se
    ne accorga.
    """

    connection_ids: frozenset[str]
    curve_ammesse: int
    """Quante curve la catena puo' fare restando nella propria forma.

    E' `Highway.turns_allowed` tale e quale: **zero** per l'autostrada fra le
    macchine di spina, **una** per la strada verso i terminali (**D-144**).
    Non e' una taratura e non si rivede qui: si rivede dove e' scritta.
    """
    pezzi: tuple[str, ...]
    nome: str
    """Come l'autostrada si nomina in un rilievo: i pezzi che tocca, in fila.

    Un rilievo deve **nominare la propria violazione** (**D-153**), e un nome
    deve poterlo leggere chi guarda la tavola: «pdc-master -> collettore-mandata
    -> accumulo» si ritrova sul foglio, una chiave no.
    """
    catene: tuple[tuple[str, ...], ...]
    """Le chiavi delle tratte, **nell'ordine della catena**."""
    passi: tuple[tuple[PortRef, PortRef], ...]
    """Per ogni tratta, la porta da cui vi si entra e quella da cui se ne esce,
    nello stesso ordine di `catene`."""

    @property
    def e_una_tratta_sola(self) -> bool:
        """Vero se la catena e' una tratta sola: allora non ci sono crocevia, e
        le sue pieghe sono quelle della sua spezzata."""
        return len(self.catene) == 1


def _pezzi_in_linea(project: ProjectModel, catalog: ComponentRegistry) -> frozenset[str]:
    """Chi spezza una linea lo dice la libreria, non un elenco scritto qui.

    E' la stessa lettura di `compose.inline_component_ids`, ripetuta qui in una
    riga per non trascinare l'intero modulo di composizione — e il solutore che
    quello importa — dentro il preflight.
    """
    return frozenset(
        item.id
        for item in project.components
        if catalog.resolve(item.definition_id).is_inline
    )


def autostrade_in_tavola(
    project: ProjectModel, catalog: ComponentRegistry, trunks: Iterable[Trunk]
) -> tuple[AutostradaInTavola, ...]:
    """Le autostrade dell'impianto, nella forma in cui la tavola le riconosce.

    Non aggiunge niente a `highways.highways`: ne traduce l'esito in una chiave
    che `RoutedTrunk` sa confrontare, e in un nome che un umano sa leggere.
    """
    trovate: list[AutostradaInTavola] = []
    for catena in highways(project, catalog, trunks):
        pezzi = catena.component_ids
        trovate.append(
            AutostradaInTavola(
                connection_ids=frozenset(
                    connection_id for chiave in catena.keys for connection_id in chiave
                ),
                curve_ammesse=catena.turns_allowed,
                pezzi=pezzi,
                nome=" -> ".join(pezzi),
                catene=catena.keys,
                passi=catena.steps,
            )
        )
    return tuple(trovate)


def tratte_del_progetto(
    project: ProjectModel, catalog: ComponentRegistry
) -> list[Trunk]:
    """Le tratte del modello, ricomposte dal solo modello e dalla libreria.

    E' la porta d'ingresso per chi ha in mano il progetto e la tavola ma non la
    partizione — il preflight e i controlli delle regole. Sta qui, e in nessun
    altro posto, perche' due ricostruzioni separate darebbero prima o poi due
    insiemi di tratte diversi sullo stesso impianto.
    """
    return build_trunks(project, _pezzi_in_linea(project, catalog))


def autostrade_del_progetto(
    project: ProjectModel, catalog: ComponentRegistry
) -> tuple[AutostradaInTavola, ...]:
    """Le autostrade di un progetto, ricostruendo le tratte per conto proprio."""
    return autostrade_in_tavola(
        project, catalog, tratte_del_progetto(project, catalog)
    )


def e_autostrada(
    route: RoutedTrunk, autostrade: Iterable[AutostradaInTavola]
) -> AutostradaInTavola | None:
    """L'autostrada di cui questa tratta instradata fa parte, se ce n'e' una.

    Il confronto e' sulle connessioni, non sui nomi e non sulle coordinate: una
    tratta instradata appartiene alla catena che contiene le sue connessioni.
    Una tratta senza connessioni — non ne esistono nelle tavole vigenti, ma il
    modello geometrico lo consente — non appartiene a nessuna.
    """
    if not route.connection_ids:
        return None
    volute = set(route.connection_ids)
    for autostrada in autostrade:
        if volute <= autostrada.connection_ids:
            return autostrada
    return None


def tratte_dell_autostrada(
    autostrada: AutostradaInTavola, routes: Iterable[RoutedTrunk]
) -> tuple[RoutedTrunk | None, ...]:
    """Le tratte instradate della catena, **nell'ordine della catena**.

    `None` al posto di una tratta che questo foglio non porta: una catena puo'
    essere spezzata fra due tavole, e chi misura deve poterlo vedere invece di
    misurare una catena mutilata credendola intera.
    """
    per_chiave = {tuple(route.connection_ids): route for route in routes}
    return tuple(per_chiave.get(chiave) for chiave in autostrada.catene)


def _giacitura(prima: Point, poi: Point) -> tuple[str, float] | None:
    """Su quale retta sta questo tratto: l'asse e la quota.

    `None` per un tratto degenere o obliquo: non ha una giacitura da
    confrontare. Un tratto obliquo lo nomina gia' il validatore di correttezza,
    e non e' compito di questa misura ripeterlo.
    """
    orizzontale = abs(poi.y_mm - prima.y_mm) <= _TOLLERANZA_MM
    verticale = abs(poi.x_mm - prima.x_mm) <= _TOLLERANZA_MM
    if orizzontale and verticale:
        return None
    if orizzontale:
        return ("orizzontale", prima.y_mm)
    if verticale:
        return ("verticale", prima.x_mm)
    return None


def _verso(valore: float) -> int:
    if valore > _TOLLERANZA_MM:
        return 1
    if valore < -_TOLLERANZA_MM:
        return -1
    return 0


def pieghe_della_tratta(route: RoutedTrunk) -> int:
    """Quante volte la spezzata di questa tratta cambia direzione.

    Si conta per **tratta**, non per spezzata: una tratta interrotta dai propri
    accessori in linea resta una tratta sola, e le pieghe dei suoi pezzi si
    sommano. E' il conto che il preflight ha sempre fatto, riga per riga, e sta
    qui perche' adesso lo leggono in due — `bends_per_run` e il controllo di
    **B1** — e due conti separati direbbero prima o poi due cose diverse sulla
    stessa tratta.

    **L'interruzione sotto un accessorio in linea non e' una piega di questa
    misura**: i due pezzi di spezzata non si toccano, e un cambio di giacitura
    fra l'uno e l'altro e' un organo che **spezza il tratto** — cioe' **B4**,
    che lo nomina per conto proprio.
    """
    pieghe = 0
    for segmento in route.segments:
        passi = [
            (_verso(poi.x_mm - prima.x_mm), _verso(poi.y_mm - prima.y_mm))
            for prima, poi in moves_of(segmento)
        ]
        pieghe += sum(
            1 for prima, poi in zip(passi, passi[1:], strict=False) if prima != poi
        )
    return pieghe


def _punti(route: RoutedTrunk) -> list[Point]:
    """Tutti i punti della tratta, di seguito: i pezzi di spezzata sono gia'
    nell'ordine in cui la tratta li percorre."""
    return [punto for segmento in route.segments for punto in segmento]


def _capo_iniziale(route: RoutedTrunk, verso: Point | None) -> bool:
    """La tratta si percorre nel verso in cui e' scritta?

    Lo dice la porta da cui la catena vi entra: il capo della spezzata che le
    sta piu' vicino e' il primo. Senza quella porta — una posa che non colloca
    il pezzo — si tiene il verso in cui la tratta e' scritta, che e' quello in
    cui il motore l'ha instradata.
    """
    punti = _punti(route)
    if verso is None or len(punti) < 2:
        return True
    testa = abs(punti[0].x_mm - verso.x_mm) + abs(punti[0].y_mm - verso.y_mm)
    coda = abs(punti[-1].x_mm - verso.x_mm) + abs(punti[-1].y_mm - verso.y_mm)
    return testa <= coda


def _giaciture_ai_capi(
    route: RoutedTrunk, dritta: bool
) -> tuple[tuple[str, float] | None, tuple[str, float] | None]:
    """La giacitura del primo e dell'ultimo tratto, nel verso di percorrenza."""
    punti = _punti(route)
    if not dritta:
        punti = list(reversed(punti))
    giaciture = [
        giacitura
        for giacitura in (_giacitura(prima, poi) for prima, poi in moves_of(punti))
        if giacitura is not None
    ]
    if not giaciture:
        return (None, None)
    return (giaciture[0], giaciture[-1])


PorteInTavola = dict[tuple[str, str], tuple[Point, PortFace]]
"""Dove sta ogni porta sulla tavola, e su che faccia guarda."""


def porte_in_tavola(
    sheet: SheetGeometry, project: ProjectModel, catalog: ComponentRegistry
) -> PorteInTavola:
    """Le porte di tutti i pezzi posati su questo foglio.

    La posizione si legge come la legge il motore: il manifesto **ruotato** del
    simbolo, l'attacco che `PlacedSymbol.port_map` dichiara per quella porta del
    modello, e l'origine del pezzo. Nessuna coordinata nuova viene inventata
    qui: si rilegge quella che la tavola ha gia'.
    """
    definizioni = {item.id: item.definition_id for item in project.components}
    trovate: PorteInTavola = {}
    for posato in sheet.symbols:
        definition_id = definizioni.get(posato.component_id)
        if definition_id is None:
            continue
        manifesto = catalog.resolve(definition_id).symbol.manifest.rotated(
            posato.rotation_deg, posato.specchiato
        )
        attacchi = {attacco.id: attacco for attacco in manifesto.ports}
        for porta in catalog.get(definition_id).ports:
            attacco = attacchi.get(posato.physical_port(porta.id))
            if attacco is None:
                continue
            trovate[(posato.component_id, porta.id)] = (
                Point(
                    x_mm=posato.origin.x_mm + attacco.x_mm,
                    y_mm=posato.origin.y_mm + attacco.y_mm,
                ),
                attacco.face,
            )
    return trovate


def pieghe_dell_autostrada(
    autostrada: AutostradaInTavola,
    routes: Iterable[RoutedTrunk],
    porte: PorteInTavola,
) -> int | None:
    """Quante volte la catena intera si piega, su questa tavola.

    Due addendi, e il secondo e' quello che mancava:

    1. le **pieghe di ciascuna tratta**, contate sulla sua spezzata — lo stesso
       conto del preflight;
    2. le **pieghe sui crocevia**, cioe' i cambi di giacitura fra l'ultimo
       tratto di una tratta e il primo della successiva. Sono le pieghe che
       nessuna tratta vede: ogni frammento resta dritto e la catena fa un
       gomito sul raccordo che li unisce. E' il difetto che `DRAW-012` §C ha
       gia' nominato sul modello e che sulla tavola non era misurato.

    `None` quando il foglio non porta tutte le tratte della catena: una catena
    mutilata non ha un numero di pieghe da dare, e chi chiama non deve leggerne
    uno.
    """
    tratte = tratte_dell_autostrada(autostrada, routes)
    if any(tratta is None for tratta in tratte):
        return None
    pieghe = 0
    uscente: tuple[str, float] | None = None
    for indice, tratta in enumerate(tratte):
        assert tratta is not None
        entrata, _ = autostrada.passi[indice]
        dove = porte.get((entrata.component_id, entrata.port_id))
        dritta = _capo_iniziale(tratta, dove[0] if dove is not None else None)
        prima, poi = _giaciture_ai_capi(tratta, dritta)
        pieghe += pieghe_della_tratta(tratta)
        if uscente is not None and prima is not None and uscente != prima:
            pieghe += 1
        if poi is not None:
            uscente = poi
    return pieghe


__all__ = [
    "AutostradaInTavola",
    "PorteInTavola",
    "autostrade_del_progetto",
    "autostrade_in_tavola",
    "e_autostrada",
    "pieghe_della_tratta",
    "pieghe_dell_autostrada",
    "porte_in_tavola",
    "tratte_del_progetto",
    "tratte_dell_autostrada",
]
