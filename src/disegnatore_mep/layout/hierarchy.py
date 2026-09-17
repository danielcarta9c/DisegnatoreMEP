"""La gerarchia della tavola: autostrada, distribuzione, servizio (DRAW-007, §A).

Il PO, il 10 settembre 2026:

    «Le tubazioni che vanno alle macchine principali sono l'autostrada, e su
    quelle i costi dovrebbero essere ancora maggiori. Oggi nel nostro router
    non abbiamo distinzione tra autostrada principale e strade secondarie:
    tutto e' principale ma non e' cosi'.»

Non e' una preferenza estetica: e' il modo in cui un progettista costruisce una
tavola. Allineate le porte della macchina principale con quelle dell'accumulo
principale nascono **due rette parallele** — mandata e ritorno — e tutto il
resto si appende a quelle. Chi disegna accetta volentieri dieci pieghe in piu'
sulle strade secondarie per tenere pulite le due macro-linee; un costo che le
pesa uguali fa il contrario, e lo fa **correttamente** secondo il criterio che
ha. Il criterio sbagliato e' il costo, non il ciclo che lo minimizza.

**La primitiva.** La prima stesura del pacchetto contava «quanta parte
dell'impianto dipende da questa tratta». Il prototipo l'ha smentita sulle due
tavole vere: su un circuito chiuso il cammino a valle rientra su se' stesso,
quindi ogni tratta dell'anello raggiunge ogni utilizzatore e ventuno tratte su
ventidue prendono lo stesso peso. Non e' una toppa mancante, e' la primitiva
sbagliata. Quella scelta dal PO e' il **tronco fra le macchine principali**, ed
e' quella che questo modulo calcola.

Il conto vive **qui e in nessun altro posto**: lo leggono il costo di posa e
l'obiettivo di allineamento, e con `DRAW-008` lo leggera' anche lo spessore del
tratto. Tre calcoli separati direbbero prima o poi tre cose diverse sulla stessa
tubazione.
"""

from collections.abc import Callable
from enum import IntEnum

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition
from disegnatore_mep.layout.flow import (
    BOUNDARY_FUNCTION,
    EXCHANGE_FUNCTIONS,
    GENERATOR_FUNCTIONS,
    STORE_FUNCTIONS,
    TERMINAL_FUNCTIONS,
    TrunkKey,
)
from disegnatore_mep.layout.trunks import Trunk
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import PortFlow

DISTRIBUTION_FUNCTIONS = frozenset({"distribution"})
"""Chi ripartisce il fluido fra piu' circuiti: il collettore.

Sta sulla spina insieme a chi genera e a chi accumula perche' e' il terzo capo
delle «due macro-linee»: il tronco non finisce sull'accumulo, arriva fin dove il
fluido si divide.
"""

ACCUMULATION_FUNCTIONS = (
    STORE_FUNCTIONS | EXCHANGE_FUNCTIONS | DISTRIBUTION_FUNCTIONS
)
"""Chi il fluido lo **riceve**: gli «accumuli» dell'architettura §4.

Accumuli, puffer, separatori, scambiatori e collettori. Sono le destinazioni
verso cui il PO fa correre l'autostrada — «dai generatori agli accumuli e agli
scambiatori» — e servono a decidere, su un crocevia, quale ramo resta sull'asse.
"""


def axis_rank(functions: frozenset[str], area_mm2: float) -> tuple[int, float]:
    """Quanto un ramo merita di restare sull'asse, guardando dove porta.

    L'architettura del **11 settembre** §4 lo dice cosi': «resta sull'asse il
    ramo verso l'**accumulo maggiore**». Sono due parole, e vengono in
    quest'ordine: prima **accumulo** — chi il fluido lo riceve, non un altro
    generatore — e poi **maggiore**, che e' l'ingombro dichiarato dal simbolo.

    ⛔ **L'ordine conta, e prima non c'era.** Finche' il tronco eleggeva un
    generatore solo, su un collettore che unisce due pompe di calore c'era un
    ramo di autostrada solo — l'altro era distribuzione — e non c'era niente da
    scegliere. Da `DRAW-012` i generatori sono tutti macchine di spina, e il
    collettore ne vede due: guardando il solo ingombro vinceva la **seconda
    pompa di calore** (1200 mm²) contro l'accumulo (1125 mm²), l'asse andava da
    un generatore all'altro e l'accumulo si staccava di lato. E' la prima cosa
    che il PO guarda — «dai generatori agli accumuli» — e adesso e' la prima
    chiave.

    Il criterio e' un **dato** — il mestiere di catalogo e l'ingombro del
    simbolo — mai un nome (D-093), e vive qui perche' lo leggono in due: la fase
    del tronco, che sceglie le pose, e le autostrade intere, che decidono dove
    la catena prosegue. Due conti separati direbbero prima o poi due cose
    diverse sulla stessa biforcazione.
    """
    return (0 if functions & ACCUMULATION_FUNCTIONS else 1, -area_mm2)


SPINE_FUNCTIONS = (
    GENERATOR_FUNCTIONS | STORE_FUNCTIONS | EXCHANGE_FUNCTIONS | DISTRIBUTION_FUNCTIONS
)
"""I mestieri delle macchine su cui la struttura si appoggia (**D-138**).

Il PO le nomina una per una quando detta dove corrono le autostrade: «dai
**generatori** agli **accumuli** e agli **scambiatori**, passando per le valvole
a tre vie e i **collettori** che mettono insieme i generatori». Sono quattro
mestieri, non quattro pezzi (D-069), e stanno qui in un elenco solo perche' la
spina e la gerarchia devono leggerli identici.
"""


class Level(IntEnum):
    """Il livello di una tratta. **Ordinato**, e non per comodita'.

    Il costo deve poterlo pesare come una grandezza — moltiplicare, confrontare,
    sommare — invece di aprire un elenco di casi. Un elenco di casi e' la strada
    piu' corta perche' il quarto livello, il giorno che serve, venga dimenticato
    in una funzione su tre.
    """

    SERVIZIO = 0
    """Non porta a nessuna macchina: stacchi ciechi e accessori appesi."""

    DISTRIBUZIONE = 1
    """Porta a una macchina che sulla spina non sta: un utilizzatore, un
    generatore oltre il principale, un confine di rete."""

    AUTOSTRADA = 2
    """Sta fra due macchine di spina. Su un circuito chiuso ci stanno **sia la
    mandata sia il ritorno**, che e' precisamente cio' che il PO chiama «le due
    macro-linee parallele»."""


_WEIGHT: dict["Level", int] = {}
"""Riempito sotto, dopo che `Level` esiste. Sta qui, e in nessun altro posto."""


def weight_of(level: Level) -> int:
    """Quanto pesa una piega, un incrocio o un millimetro su quel livello.

    La scala e' 1 / 4 / 16, e il numero che la fissa e' il PO:

        «Si accettano volentieri dieci pieghe in piu' sulle strade secondarie
        per tenere pulite le due macro-linee.»

    Sedici e' il primo gradino della scala che supera quel dieci: una piega
    sull'autostrada costa piu' di dieci pieghe di servizio, e il ciclo
    preferisce sempre spostarla fuori dal tronco. Non e' una costante arbitraria
    e non e' tarata su una fixture: e' la frase del PO tradotta in un numero, e
    se il PO la cambia questa e' l'unica riga da toccare.
    """
    return _WEIGHT[level]


def is_a_machine(definition: ComponentDefinition) -> bool:
    """Un apparecchio: non un raccordo, non un multivia, non un appeso.

    E' la distinzione che il catalogo dichiara gia'. Un raccordo lo si
    attraversa e basta. Un **multivia** lo si attraversa stato per stato — e'
    un organo sulla tubazione, non una destinazione: contarlo come macchina
    spezzava il tronco proprio dove il tronco passa, ed e' il difetto che il PO
    ha visto sulla tavola 2, dove la mandata dalla pompa di calore al puffer
    non risultava nemmeno autostrada perche' in mezzo c'e' una deviatrice. Un
    accessorio appeso e' un capolinea che non porta da nessuna parte. Cio' che
    resta e' una macchina, e sono le macchine che la gerarchia unisce.
    """
    return (
        not definition.is_a_fitting
        and not definition.attaches_on_a_branch
        and not definition.hydraulic_states
    )


def ports_through(definition: ComponentDefinition, port_id: str) -> frozenset[str]:
    """Le porte che comunicano con questa **dentro** il pezzo.

    Un multivia lo dice il catalogo, stato per stato: l'ingresso di una
    deviatrice comunica con un ramo oppure con l'altro, e i due rami non
    comunicano mai fra loro. Un raccordo si attraversa fra tutti i propri
    attacchi del percorso. Tutto il resto non si attraversa: una macchina e' il
    capolinea con cui ci si allinea, e un accessorio appeso resta un capolinea
    anche con due porte — il ponte del riempimento tocca due reti, e chi lo
    attraversasse leggerebbe come tronco una tubazione di servizio.
    """
    if definition.hydraulic_states:
        return definition.linked_ports(port_id)
    if definition.is_a_fitting:
        return frozenset(
            port.id
            for port in definition.ports
            if port.id != port_id and not port.off_the_run
        )
    return frozenset()


_WEIGHT.update(
    {
        Level.SERVIZIO: 1,
        Level.DISTRIBUZIONE: 4,
        Level.AUTOSTRADA: 16,
    }
)


def spine_machines(project: ProjectModel, catalog: ComponentRegistry) -> frozenset[str]:
    """Le macchine su cui la struttura si appoggia: **tutte**, generatori compresi.

    Chi accumula o separa idraulicamente, chi scambia calore fra due circuiti,
    ogni collettore e **ogni** macchina di generazione.

    ⛔ **Non piu' un generatore solo.** Fino a `DRAW-011` il tronco eleggeva un
    generatore — il primo dell'ordine strutturale — e gli altri diventavano
    contorno: sull'impianto 4 erano autostrada le tratte della caldaia e non
    quelle della pompa di calore, e sull'impianto 5, cascata di tre pompe, due
    su tre sparivano dalla struttura. Il PO (**D-138**): «dai generatori agli
    accumuli», al plurale, «passando per le valvole a tre vie e i collettori che
    **mettono insieme i generatori**» — cioe' con piu' generatori le autostrade
    sono piu' d'una, e ciascuno ha la propria fino al punto in cui confluiscono.
    Non c'e' nessun generatore eletto, e quindi nessuno spareggio da fare: il
    mestiere basta.
    """
    definitions = {item.id: catalog.get(item.definition_id) for item in project.components}
    return frozenset(
        key
        for key, value in definitions.items()
        if is_a_machine(value) and frozenset(value.functions) & SPINE_FUNCTIONS
    )


def _draws_from_the_plant(definition: ComponentDefinition) -> bool:
    """Un confine di rete che **riceve**: e' l'utenza a cui il fluido va.

    Il catalogo distingue gia' i due confini, e li distingue con il verso delle
    proprie porte: il prelievo sanitario ha un solo attacco e il fluido vi
    **entra**, l'acquedotto ha un solo attacco e il fluido ne **esce**. E' la
    differenza fra l'«uscita ACS», che D-138 mette nella fase della struttura, e
    l'«ingresso AF», che la stessa disposizione lascia agli stacchi di servizio
    della fase del corredo. Nessun nome, nessun fluido: il verso dichiarato.
    """
    if BOUNDARY_FUNCTION not in definition.functions:
        return False
    ports = [port for port in definition.ports if not port.off_the_run]
    return bool(ports) and all(port.flow is PortFlow.IN for port in ports)


def user_machines(project: ProjectModel, catalog: ComponentRegistry) -> frozenset[str]:
    """Chi usa il fluido: i terminali e le utenze.

    Sono il capolinea della **strada secondaria** che D-138 traccia nella fase
    della struttura insieme alle autostrade — «uscita ACS e distribuzione verso
    i terminali» — e servono alla gerarchia per riconoscerla.
    """
    definitions = {item.id: catalog.get(item.definition_id) for item in project.components}
    return frozenset(
        key
        for key, value in definitions.items()
        if is_a_machine(value)
        and (
            frozenset(value.functions) & TERMINAL_FUNCTIONS
            or _draws_from_the_plant(value)
        )
    )


Attacco = tuple[str, str]
"""Un attacco: il pezzo e la sua porta. E' l'unita' con cui si cammina."""

Beyond = Callable[[Attacco, TrunkKey], frozenset[str]]
"""Le macchine che si raggiungono entrando da un attacco, senza una tratta."""


def machines_beyond_of(
    project: ProjectModel, catalog: ComponentRegistry, trunks: list[Trunk]
) -> Beyond:
    """Chi c'e' **oltre** un attacco: la camminata, costruita una volta sola.

    Si cammina **per attacchi**, non per pezzi: dentro un multivia si passa solo
    dove il catalogo dichiara che si passa, e i due rami di una deviatrice non
    comunicano mai fra loro. Ci si ferma sulla prima macchina, perche' su un
    circuito chiuso un cammino che non si fermasse rientrerebbe su se' stesso e
    darebbe a ogni ramo la stessa risposta — la primitiva sbagliata che questo
    modulo ha gia' scartato una volta.

    La camminata vive **qui**, e la leggono in tre: la gerarchia, che ne ricava
    il livello di una tratta; la fase del tronco, che ne ricava quale ramo resta
    sull'asse; e le autostrade intere, che ne ricavano dove la catena prosegue.
    Camminare per pezzi invece che per attacchi — come la fase del tronco faceva
    per conto proprio — fa risultare raggiungibile dal ramo di una deviatrice
    cio' che sta sull'altro: sull'impianto 4 il ramo del riscaldamento
    «raggiungeva» lo scambiatore sanitario, e l'asse ci andava dietro.
    """
    definitions = {item.id: catalog.get(item.definition_id) for item in project.components}
    machines = {key for key, value in definitions.items() if is_a_machine(value)}
    edges: dict[Attacco, list[tuple[Attacco, TrunkKey]]] = {}
    for trunk in trunks:
        first = (trunk.start.component_id, trunk.start.port_id)
        second = (trunk.end.component_id, trunk.end.port_id)
        edges.setdefault(first, []).append((second, trunk.connection_ids))
        edges.setdefault(second, []).append((first, trunk.connection_ids))

    def machines_beyond(entry: Attacco, without: TrunkKey) -> frozenset[str]:
        if entry[0] in machines:
            return frozenset({entry[0]})
        if not ports_through(definitions[entry[0]], entry[1]):
            return frozenset()
        seen = {entry}
        found: set[str] = set()
        frontier = [entry]
        while frontier:
            onward: list[Attacco] = []
            for component_id, port_id in frontier:
                for inner in ports_through(definitions[component_id], port_id):
                    for other, key in edges.get((component_id, inner), ()):
                        if key == without or other in seen:
                            continue
                        seen.add(other)
                        if other[0] in machines:
                            found.add(other[0])
                            continue
                        if not ports_through(definitions[other[0]], other[1]):
                            continue
                        onward.append(other)
            frontier = onward
        return frozenset(found)

    return machines_beyond


def hierarchy_of(
    project: ProjectModel, catalog: ComponentRegistry, trunks: list[Trunk]
) -> dict[TrunkKey, Level]:
    """Il livello di ciascuna tratta.

    Si guarda che cosa c'e' **di qua e di la'** della tratta, camminando
    attraverso i raccordi e fermandosi sulla prima macchina. Poi, in ordine:

    1. da tutt'e due i lati una macchina di spina — la tratta e' **autostrada**:
       e' la regola di sempre, e da `DRAW-012` vale per **ogni** generatore e
       arriva anche sugli scambiatori (`SPINE_FUNCTIONS`);
    2. da un lato un **accumulo, un puffer o uno scambiatore** e dall'altro
       un'**utenza** — un terminale, o il prelievo sanitario — la tratta e'
       ancora **autostrada**:
       e' la «strada secondaria» che **D-138** traccia nella fase della
       struttura insieme alle autostrade, «uscita ACS e distribuzione verso i
       terminali», ed e' anche il «sempre» del PO sulle linee che dagli
       accumuli, dai puffer e dagli scambiatori vanno ai circolatori e da li'
       alla distribuzione — il circolatore sta **dentro** questa tratta, perche'
       e' un accessorio in linea e la tratta lo attraversa;
    3. da tutt'e due i lati una macchina — **distribuzione**. Ci resta
       l'ingresso dell'acqua fredda, che il PO lascia agli stacchi di servizio
       della fase del corredo: e' un confine che **immette** e non un'utenza che
       preleva;
    4. da un lato nessuna macchina — quel lato e' un capolinea, ed e'
       **servizio**.

    La simmetria della definizione e' il motivo per cui mandata e ritorno di un
    circuito chiuso finiscono **tutt'e due** in cima: nessuna delle due e' «la
    strada», sono le due corsie della stessa strada. Vale anche per la strada
    secondaria: la mandata ai ventilconvettori e il suo ritorno sono la stessa
    strada, e il criterio 1 del pacchetto le nomina tutt'e due.
    """
    spine = spine_machines(project, catalog)
    users = user_machines(project, catalog)
    definitions = {item.id: catalog.get(item.definition_id) for item in project.components}
    # Chi la strada secondaria la fa **partire**: gli accumuli, i puffer e gli
    # scambiatori, e nessun altro. Sono le tre parole del PO, e sono tre e non
    # quattro: un **collettore** non e' una sorgente della distribuzione, e' il
    # punto in cui la distribuzione si divide — «il tronco non finisce
    # sull'accumulo, arriva fin dove il fluido si divide». Oltre il collettore
    # ogni zona e' un ramo, e i rami paralleli si impilano (D-060): pretenderli
    # tutti rettilinei li allineerebbe alle bocche del collettore, cioe' uno di
    # fianco all'altro invece che uno sopra l'altro.
    sorgenti = frozenset(
        key
        for key, value in definitions.items()
        if key in spine
        and frozenset(value.functions) & (STORE_FUNCTIONS | EXCHANGE_FUNCTIONS)
    )
    machines_beyond = machines_beyond_of(project, catalog, trunks)

    levels: dict[TrunkKey, Level] = {}
    for trunk in trunks:
        here = machines_beyond(
            (trunk.start.component_id, trunk.start.port_id), trunk.connection_ids
        )
        there = machines_beyond(
            (trunk.end.component_id, trunk.end.port_id), trunk.connection_ids
        )
        joins_the_spine = bool(here & spine and there & spine)
        reaches_a_user = bool(
            (here & sorgenti and there & users) or (there & sorgenti and here & users)
        )
        if joins_the_spine or reaches_a_user:
            levels[trunk.connection_ids] = Level.AUTOSTRADA
        elif here and there:
            levels[trunk.connection_ids] = Level.DISTRIBUZIONE
        else:
            levels[trunk.connection_ids] = Level.SERVIZIO
    return levels


__all__ = [
    "ACCUMULATION_FUNCTIONS",
    "DISTRIBUTION_FUNCTIONS",
    "SPINE_FUNCTIONS",
    "Level",
    "axis_rank",
    "hierarchy_of",
    "machines_beyond_of",
    "is_a_machine",
    "ports_through",
    "spine_machines",
    "user_machines",
    "weight_of",
]
