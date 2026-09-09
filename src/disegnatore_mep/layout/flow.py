"""Mandata o ritorno: lo dice la topologia, non la geometria.

Finora il verso di una tratta si leggeva dal disegno gia' fatto — «chi va verso
destra e' mandata» — e bastava che un componente finisse a sinistra del suo
alimentatore perche' la mandata venisse disegnata blu. E' il difetto che il PM
ha visto per primo: «il ritorno blu va dentro la valvola a tre vie?». Ci andava
la mandata: la valvola sta a valle della pompa di calore, e la geometria la
aveva messa a sinistra.

Il verso e' una proprieta' del **modello**, che e' orientato: ogni connessione
va da una porta `out` a una porta `in`. Quello che manca al modello e' quale
componente sia la sorgente del circuito, e lo dicono le funzioni di catalogo.

La regola, che e' poi come si legge una centrale:

- ogni rete ha una **sorgente** — il generatore, o l'accumulo se generatori non
  ce ne sono;
- cio' che esce dalla sorgente e prosegue in avanti e' **mandata**, fino al
  primo utilizzatore;
- cio' che rientra nella sorgente, risalito all'indietro, e' **ritorno**, fino
  al primo utilizzatore.

Camminare si ferma sugli utilizzatori perche' e' li' che il fluido cambia
mestiere: quello che entra in un radiatore e' mandata, quello che ne esce e'
ritorno, e nessuna delle due camminate deve attraversarlo per non riscrivere
l'altra meta' del circuito.
"""

from collections import defaultdict
from typing import NamedTuple

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import PortDefinition
from disegnatore_mep.model.project import PortRef, ProjectModel
from disegnatore_mep.model.types import PortFlow

from .geometry import FlowKind
from .trunks import Trunk

TrunkKey = tuple[str, ...]
"""Identita' di una tratta: le connessioni che la compongono."""

INBOUND_FUNCTIONS = frozenset({"filling"})
"""I mestieri di chi, da uno stacco, **immette** acqua nel circuito.

Il gruppo di riempimento e' acqua di rete che entra nel ritorno tecnico: la
sua freccia punta dal gruppo verso il circuito (DRAW-005-R1, I-042). E' un
elenco di **funzioni** di catalogo, mai di pezzi (D-069)."""

OUTBOUND_FUNCTIONS = frozenset({"drain"})
"""I mestieri di chi, da uno stacco, **fa uscire** acqua dal circuito: lo
scarico esplicitamente modellato porta il verso uscente."""

GENERATOR_FUNCTIONS = frozenset(
    {
        "heat_generation",
        "cooling_generation",
        "refrigerant_generation",
        "gas_combustion",
    }
)
"""Chi produce il fluido caldo o freddo: e' la sorgente naturale di un circuito."""

STORE_FUNCTIONS = frozenset(
    {
        "thermal_storage",
        "dhw_storage",
        "hydraulic_separation",
    }
)
"""Chi lo accumula o lo separa: e' la sorgente del circuito che ne parte.

Un volano e' l'utilizzatore del primario e la sorgente del secondario. Le due
cose non sono in contraddizione: dipende da quale rete si sta guardando, ed e'
per questo che l'orientamento si calcola **una rete alla volta**.
"""

LOAD_FUNCTIONS = frozenset(
    {
        "emission",
        "air_terminal",
        "direct_expansion_terminal",
        "thermal_storage",
        "dhw_storage",
        "hydraulic_separation",
        "heat_exchange",
        "boundary",
    }
)
"""Dove il fluido cede o prende calore, e quindi cambia da mandata a ritorno.

Ci stanno dentro anche gli accumuli: rispetto al circuito che li alimenta un
volano e' un utilizzatore a tutti gli effetti, e la camminata deve fermarcisi.
"""


def _rank(functions: frozenset[str]) -> int:
    if functions & GENERATOR_FUNCTIONS:
        return 2
    if functions & STORE_FUNCTIONS:
        return 1
    return 0


def _sources(
    members: list[str],
    incoming: dict[str, list[Trunk]],
    functions_of: dict[str, frozenset[str]],
    position: dict[str, int],
) -> list[str]:
    """Da dove parte una rete. Due criteri, e il primo viene prima.

    **Chi immette e non riceve e' la sorgente, qualunque mestiere faccia.** Su
    una rete di acqua fredda la sorgente e' l'acquedotto: immette e basta. Il
    bollitore la riceve — e' l'ultimo posto dove il fluido va, non il primo da
    cui viene. Prima contava solo il mestiere, e il mestiere del bollitore
    (tenere una riserva) valeva piu' di quello di un confine di rete: cosi' la
    sorgente dell'acqua fredda risultava il bollitore, la camminata partiva da
    li' **all'indietro**, e **tutta l'adduzione veniva disegnata come un
    ritorno** — con il colore e il tratteggio del ritorno. Sui cinque impianti
    non esisteva una sola tratta di acqua fredda in andata, e l'acqua fredda un
    ritorno non ce l'ha.

    Dove nessuno immette senza ricevere — un circuito chiuso, che e' il caso del
    primario — la sorgente la dice il **mestiere**: prima chi genera, poi chi
    accumula.

    Resta **una sola** sorgente per rete, come prima. Partire da tutte quelle di
    pari mestiere — le due pompe di calore in parallelo — toglierebbe qualche
    tratta indecisa, ma cambia l'ordine con cui il collocatore legge il
    processo, e oggi la disposizione non regge il cambiamento: due impianti su
    tre smettono di entrare nel foglio. E' scritto fra le righe aperte del
    registro degli input del PM, e si fa quando la composizione compatta.
    """
    feeders = [item for item in members if not incoming.get(item)]
    candidates = feeders or members
    return [
        min(
            candidates,
            key=lambda item: (
                -_rank(functions_of.get(item, frozenset())),
                position.get(item, 0),
            ),
        )
    ]


def _walk(
    edges: dict[str, list[Trunk]],
    onward: str,
    source: str,
    functions_of: dict[str, frozenset[str]],
) -> set[TrunkKey]:
    """Le tratte raggiunte partendo dalla sorgente, fermandosi sugli utilizzatori."""
    reached: set[TrunkKey] = set()
    frontier = [source]
    visited = {source}
    while frontier:
        following: list[str] = []
        for component_id in frontier:
            for trunk in edges[component_id]:
                reached.add(trunk.connection_ids)
                beyond: str = getattr(trunk, onward).component_id
                if beyond in visited:
                    continue
                visited.add(beyond)
                if functions_of.get(beyond, frozenset()) & LOAD_FUNCTIONS:
                    continue
                following.append(beyond)
        frontier = following
    return reached


def orient_trunks(
    project: ProjectModel, catalog: ComponentRegistry, trunks: list[Trunk]
) -> dict[TrunkKey, bool | None]:
    """Per ciascuna tratta: `True` mandata, `False` ritorno, `None` indecidibile.

    `None` non e' un fallimento: e' un circuito in cui nessun utilizzatore
    separa l'andata dal ritorno — un anello di sola distribuzione, per esempio —
    e la sola cosa che resta e' guardare come e' venuto il disegno. Chi chiama
    decide come ripiegare; qui non si inventa un verso che il modello non ha.
    """
    functions_of = {
        item.id: frozenset(catalog.resolve(item.definition_id).definition.functions)
        for item in project.components
    }
    position = {item.id: index for index, item in enumerate(project.components)}

    by_network: dict[str, list[Trunk]] = defaultdict(list)
    for trunk in trunks:
        by_network[trunk.network_id].append(trunk)

    oriented: dict[TrunkKey, bool | None] = {}
    for group in by_network.values():
        outgoing: dict[str, list[Trunk]] = defaultdict(list)
        incoming: dict[str, list[Trunk]] = defaultdict(list)
        members: list[str] = []
        for trunk in group:
            outgoing[trunk.start.component_id].append(trunk)
            incoming[trunk.end.component_id].append(trunk)
            for component_id in (trunk.start.component_id, trunk.end.component_id):
                if component_id not in members:
                    members.append(component_id)
        if not members:
            continue

        supply: set[TrunkKey] = set()
        returns: set[TrunkKey] = set()
        for source in _sources(members, incoming, functions_of, position):
            supply |= _walk(outgoing, "end", source, functions_of)
            returns |= _walk(incoming, "start", source, functions_of)
        for trunk in group:
            key = trunk.connection_ids
            in_supply, in_return = key in supply, key in returns
            oriented[key] = None if in_supply == in_return else in_supply
    return oriented


class TrunkFlow(NamedTuple):
    """Cio' che il disegno deve sapere di una tratta prima di instradarla."""

    supply: bool | None
    """Andata o ritorno; `None` solo per una tratta del percorso che la
    topologia non decide. Uno stacco non e' mai indeciso: eredita."""

    kind: FlowKind
    """La specie: flusso ordinario, ramo statico, ingresso, scarico."""

    flow_from_start: bool
    """Il verso del flusso rispetto ai due capi della tratta: da `start` a
    `end`, oppure al contrario."""


def _branch_root(
    trunk: Trunk, ports_of: dict[str, tuple[PortDefinition, ...]]
) -> PortRef | None:
    """L'attacco fuori dal percorso da cui la tratta parte, se e' uno stacco.

    Uno stacco si riconosce dal **catalogo** (D-101): un suo capo sta su un
    attacco che il pezzo dichiara fuori dal percorso — il braccio di un
    raccordo, l'attacco di servizio di una macchina. Nessuna coordinata,
    nessun identificativo."""
    for ref in (trunk.start, trunk.end):
        if any(
            port.id == ref.port_id and port.off_the_run
            for port in ports_of.get(ref.component_id, ())
        ):
            return ref
    return None


def _forward_of(
    trunk: Trunk, ports_of: dict[str, tuple[PortDefinition, ...]]
) -> bool:
    """Il flusso ordinario va da `start` a `end`? Lo dicono le porte.

    Una connessione del modello va sempre da una porta che esce a una che
    entra; ma una tratta ricomposta dagli accessori in linea parte dal capo
    che il file elencava per primo, che puo' essere quello in cui il fluido
    **entra**. La freccia segue il catalogo, non l'ordine del file."""

    def flow_at(ref: PortRef) -> PortFlow | None:
        return next(
            (port.flow for port in ports_of.get(ref.component_id, ()) if port.id == ref.port_id),
            None,
        )

    at_start, at_end = flow_at(trunk.start), flow_at(trunk.end)
    if at_start is PortFlow.OUT or at_end is PortFlow.IN:
        return True
    return not (at_start is PortFlow.IN or at_end is PortFlow.OUT)


def _walk_edges(
    edges: dict[str, list[tuple[Trunk, str]]],
    source: str,
    functions_of: dict[str, frozenset[str]],
) -> set[TrunkKey]:
    """Come `_walk`, su archi gia' orientati: ogni arco porta il pezzo oltre."""
    reached: set[TrunkKey] = set()
    frontier = [source]
    visited = {source}
    while frontier:
        following: list[str] = []
        for component_id in frontier:
            for trunk, beyond in edges.get(component_id, ()):
                reached.add(trunk.connection_ids)
                if beyond in visited:
                    continue
                visited.add(beyond)
                if functions_of.get(beyond, frozenset()) & LOAD_FUNCTIONS:
                    continue
                following.append(beyond)
        frontier = following
    return reached


def _oriented_for_colour(
    project: ProjectModel, catalog: ComponentRegistry, trunks: list[Trunk]
) -> dict[TrunkKey, bool | None]:
    """Andata e ritorno **per il colore**, dal modello e da tutte le sorgenti.

    `orient_trunks` parte da una sorgente sola per rete e percorre le tratte
    nel verso in cui il file le ha scritte, e lo fa apposta: e' l'ordine con
    cui il collocatore legge il processo, e cambiarlo cambia la disposizione.
    Ma per il colore quella lettura non basta (I-042): con due macchine in
    parallelo la mandata e il ritorno della seconda restano indecisi, e una
    tratta che il file elenca dal capo che entra viene percorsa al contrario.
    Qui, e solo per il colore, si legge il modello com'e' orientato — ogni
    tratta nel verso in cui le sue porte dicono che il fluido la percorre — e
    si cammina da **ogni** sorgente della rete: una tratta raggiunta in avanti
    e' andata, una risalita e' ritorno, indecisa solo chi si raggiunge in
    entrambi i modi o in nessuno. La posa non legge questo.
    """
    functions_of = {
        item.id: frozenset(catalog.resolve(item.definition_id).definition.functions)
        for item in project.components
    }
    ports_of = {
        item.id: tuple(catalog.get(item.definition_id).ports) for item in project.components
    }
    position = {item.id: index for index, item in enumerate(project.components)}
    by_network: dict[str, list[Trunk]] = defaultdict(list)
    for trunk in trunks:
        by_network[trunk.network_id].append(trunk)

    oriented: dict[TrunkKey, bool | None] = {}
    for group in by_network.values():
        outgoing: dict[str, list[tuple[Trunk, str]]] = defaultdict(list)
        incoming: dict[str, list[tuple[Trunk, str]]] = defaultdict(list)
        members: list[str] = []
        for trunk in group:
            # Uno stacco non e' strada: chi cammina lungo il percorso non ci
            # entra, e un accessorio appeso non e' mai una sorgente.
            if _branch_root(trunk, ports_of) is not None:
                continue
            head, tail = (
                (trunk.start, trunk.end)
                if _forward_of(trunk, ports_of)
                else (trunk.end, trunk.start)
            )
            outgoing[head.component_id].append((trunk, tail.component_id))
            incoming[tail.component_id].append((trunk, head.component_id))
            for component_id in (head.component_id, tail.component_id):
                if component_id not in members:
                    members.append(component_id)
        if not members:
            continue
        # Le sorgenti: chi immette e non riceve; altrimenti tutti quelli del
        # mestiere piu' alto — i generatori, o gli accumuli — e non uno solo.
        feeders = [item for item in members if not incoming.get(item)]
        if feeders:
            sources = feeders
        else:
            top = max(_rank(functions_of.get(item, frozenset())) for item in members)
            sources = [item for item in members if _rank(functions_of.get(item, frozenset())) == top]
            if top == 0:
                sources = [min(sources, key=lambda item: position.get(item, 0))]
        supply: set[TrunkKey] = set()
        returns: set[TrunkKey] = set()
        for source in sources:
            supply |= _walk_edges(outgoing, source, functions_of)
            returns |= _walk_edges(incoming, source, functions_of)
        for trunk in group:
            key = trunk.connection_ids
            in_supply, in_return = key in supply, key in returns
            oriented[key] = None if in_supply == in_return else in_supply
    return oriented


def classify_trunks(
    project: ProjectModel, catalog: ComponentRegistry, trunks: list[Trunk]
) -> dict[TrunkKey, TrunkFlow]:
    """Servizio, specie e verso di ogni tratta, dal solo modello (I-042).

    Le tratte del percorso prendono andata o ritorno da `orient_trunks` e sono
    flusso ordinario. Uno **stacco** — una tratta che parte da un attacco fuori
    dal percorso — prende:

    - la **specie** dal mestiere di cio' che regge: chi immette (il
      riempimento) e' un ingresso, chi fa uscire (lo scarico) e' uno scarico,
      tutto il resto — misura, espansione, sfiato, sicurezza — e' statico;
    - il **servizio** dalla tratta che lo regge, quando pende da un raccordo:
      il manometro innestato sul ritorno tecnico e' del ritorno tecnico.
      Quando pende direttamente da un attacco di servizio di una macchina — lo
      sfiato in cima al serbatoio — non c'e' una tratta da cui ereditare: il
      volume della macchina non e' ne' andata ne' ritorno, e lo stacco prende
      il colore base del fluido;
    - il **verso**: l'ingresso guarda verso il tratto che lo regge, lo scarico
      se ne allontana, il ramo statico non ne ha.

    Nessuna geometria entra qui, ed e' il contratto: la firma lo dice.
    """
    oriented = _oriented_for_colour(project, catalog, trunks)
    definitions = {item.id: catalog.get(item.definition_id) for item in project.components}
    ports_of = {key: tuple(value.ports) for key, value in definitions.items()}
    result: dict[TrunkKey, TrunkFlow] = {}
    for trunk in trunks:
        key = trunk.connection_ids
        root = _branch_root(trunk, ports_of)
        if root is None:
            result[key] = TrunkFlow(
                supply=oriented.get(key),
                kind=FlowKind.ORDINARY,
                flow_from_start=_forward_of(trunk, ports_of),
            )
            continue
        far = trunk.end if root == trunk.start else trunk.start
        functions = frozenset(definitions[far.component_id].functions)
        if functions & INBOUND_FUNCTIONS:
            kind = FlowKind.INBOUND
        elif functions & OUTBOUND_FUNCTIONS:
            kind = FlowKind.OUTBOUND
        else:
            kind = FlowKind.STATIC
        root_at_start = root == trunk.start
        # Verso il capo radice per chi entra, via da esso per chi esce.
        flow_from_start = root_at_start if kind is FlowKind.OUTBOUND else not root_at_start
        supply: bool | None = True
        if definitions[root.component_id].is_a_fitting:
            hosts = {
                oriented.get(other.connection_ids)
                for other in trunks
                if other is not trunk
                and any(
                    ref.component_id == root.component_id
                    and _branch_root(other, ports_of) != ref
                    and not any(
                        port.id == ref.port_id and port.off_the_run
                        for port in ports_of[ref.component_id]
                    )
                    for ref in (other.start, other.end)
                )
            } - {None}
            supply = hosts.pop() if len(hosts) == 1 else True
        result[key] = TrunkFlow(supply=supply, kind=kind, flow_from_start=flow_from_start)
    return result


__all__ = [
    "INBOUND_FUNCTIONS",
    "OUTBOUND_FUNCTIONS",
    "TrunkFlow",
    "TrunkKey",
    "classify_trunks",
    "orient_trunks",
]
