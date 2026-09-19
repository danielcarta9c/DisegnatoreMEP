"""L'autostrada intera: non una catena di frammenti, ma un oggetto (DRAW-012 §C).

**Il difetto che questo modulo chiude.** Fino a `DRAW-011` un'autostrada non
esisteva come oggetto: esistevano le sue **tratte**, e ogni raccordo o multivia
incontrato ne apriva una nuova. Sull'impianto 4 erano dieci tronconi lunghi
cinque o dieci millimetri, e l'invariante «ogni tratta del tronco e' un
rettilineo» veniva verificato su **ciascun troncone**, dove e' vero per
costruzione: un frammento di 5 mm e' dritto sempre. **Nessun invariante diceva
che la catena intera fosse una retta**, ed e' il motivo per cui il difetto non
si vedeva: i numeri erano verdi e la tavola era storta.

**Che cos'e' una catena.** Una successione massimale di tratte di livello
autostrada che si susseguono passando **attraverso** i crocevia — i raccordi e i
multivia, che non sono capolinea ma punti della tubazione — e che comincia e
finisce su una macchina, o dove la retta non prosegue.

**Dove la retta prosegue lo dice il simbolo, non la geometria.** Arrivati su un
crocevia da una porta, la catena continua sulla porta che il manifesto dichiara
sulla **faccia opposta**: e' la sola che possa stare sulla stessa retta, e la
relazione sopravvive a qualunque rotazione perche' ruotare il simbolo ruota
tutt'e due le facce. Su un raccordo a T — `a` a sinistra, `b` a destra, `c` in
cima — la catena passa fra `a` e `b` e il braccio `c` se ne stacca: e'
esattamente «uno dei due rami resta sull'asse e l'altro se ne stacca»
(`2026-09-11-architettura-della-posa-a-fasi.md` §4). Con due generatori che
confluiscono su un collettore le catene sono **due**, ciascuna fino al punto in
cui confluiscono, che e' cio' che **D-138** dispone.

Poiche' «di fronte» e' una relazione simmetrica e **una porta porta una sola
tubazione** (D-100), l'accoppiamento sui crocevia e' un abbinamento perfetto: le
catene sono le componenti connesse di quell'abbinamento e non dipendono
dall'ordine in cui si costruiscono. Non c'e' nessuno spareggio da fare, e quindi
nessun nome puo' entrarci.
"""

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition
from disegnatore_mep.graphics.symbol import PortFace
from disegnatore_mep.model.order import structural_order
from disegnatore_mep.model.project import PortRef, ProjectModel

from .geometry import Point
from .hierarchy import (
    Level,
    axis_rank,
    hierarchy_of,
    is_a_machine,
    machines_beyond_of,
    ports_through,
    source_machines,
    user_machines,
)
from .trunks import Trunk

TrunkKey = tuple[str, ...]

_TOLERANCE_MM = 1e-6

_HORIZONTAL_FACES = frozenset({PortFace.LEFT, PortFace.RIGHT})

_DIRECTION: dict[PortFace, tuple[float, float]] = {
    PortFace.RIGHT: (1.0, 0.0),
    PortFace.BOTTOM: (0.0, 1.0),
    PortFace.LEFT: (-1.0, 0.0),
    PortFace.TOP: (0.0, -1.0),
}

PortAt = Callable[[str, str], tuple[Point, PortFace] | None]
"""Dove sta una porta sulla tavola, e su che faccia guarda.

La firma e' quella che hanno gia' `improve.Improver.port_at` e
`spine._Spine.port_at`: chi chiama passa la propria, perche' l'invariante si
deve poter verificare **sulla stessa geometria** che il ciclo sta valutando.
`None` per un pezzo che questa posa non colloca.
"""


@dataclass(frozen=True)
class Highway:
    """Un'autostrada intera, dall'inizio alla fine.

    `steps` la percorre: ogni passo e' una tratta, con la porta da cui vi si
    entra e quella da cui se ne esce, **nell'ordine della catena** e non in
    quello in cui il file ha scritto le connessioni. Fra un passo e il
    successivo c'e' un crocevia, e la catena vi passa attraverso.
    """

    keys: tuple[TrunkKey, ...]
    steps: tuple[tuple[PortRef, PortRef], ...]
    turns_allowed: int = 0
    """Quante curve la catena puo' fare restando **nella sua forma** (**D-144**).

    Zero per l'autostrada fra le macchine di spina: quella e' una retta da un
    capo all'altro, e resta cio' che `DRAW-012` §C ha costruito.

    **Uno** per la strada che porta ai terminali, ed e' la forma che il PO ha
    dettato come best practice il 18 settembre: «serbatoio, pompa, tratto
    dritto, curva, e giu' attacchi i terminali. Si fa sempre cosi'». Dal
    circolatore esce una **gamba rettilinea**, poi c'e' **una** curva, e dopo la
    curva la **dorsale** su cui i terminali si attaccano a pettine. La curva e'
    dichiarata: non e' una cessione di `compose._order_of_surrender` e non va
    contata fra le catene cedute."""

    @property
    def head(self) -> PortRef:
        """Il capo da cui la catena comincia."""
        return self.steps[0][0]

    @property
    def tail(self) -> PortRef:
        """Il capo su cui finisce."""
        return self.steps[-1][1]

    @property
    def component_ids(self) -> tuple[str, ...]:
        """I pezzi che la catena tocca, nell'ordine in cui li incontra."""
        found: list[str] = []
        for entry, exit_ in self.steps:
            for ref in (entry, exit_):
                if ref.component_id not in found:
                    found.append(ref.component_id)
        return tuple(found)

    @property
    def is_a_single_run(self) -> bool:
        """Vero se la catena e' una tratta sola: allora l'invariante nuovo non
        aggiunge niente a quello di sempre, ed e' giusto che sia cosi'."""
        return len(self.steps) == 1


def highways(
    project: ProjectModel, catalog: ComponentRegistry, trunks: Iterable[Trunk]
) -> tuple[Highway, ...]:
    """Le autostrade intere dell'impianto, ciascuna con le proprie tratte.

    Ogni tratta di livello autostrada sta in **una sola** catena: le catene non
    si sovrappongono, altrimenti pretendere che due catene incidenti siano
    tutt'e due rette imporrebbe al disegno una condizione che nessuna posa puo'
    soddisfare — due rette diverse per lo stesso tratto.
    """
    runs = list(trunks)
    levels = hierarchy_of(project, catalog, runs)
    autostrade = [
        item for item in runs if levels[item.connection_ids] is Level.AUTOSTRADA
    ]
    definitions: dict[str, ComponentDefinition] = {
        item.id: catalog.get(item.definition_id) for item in project.components
    }
    sizes = {
        item.id: (
            catalog.resolve(item.definition_id).symbol.manifest.width_mm
            * catalog.resolve(item.definition_id).symbol.manifest.height_mm
        )
        for item in project.components
    }
    order = structural_order(project)
    machines = {key for key, value in definitions.items() if is_a_machine(value)}
    sorgenti = source_machines(project, catalog)
    users = user_machines(project, catalog)

    at_port: dict[tuple[str, str], Trunk] = {}
    for trunk in autostrade:
        for ref in (trunk.start, trunk.end):
            at_port[(ref.component_id, ref.port_id)] = trunk
    beyond = machines_beyond_of(project, catalog, runs)

    def rank_of(here: str, port_id: str) -> tuple[int, float, int]:
        """Quanto pesa il ramo che parte da questa porta: dove porta, e quanto
        e' grande cio' a cui porta.

        Stessa camminata e stesso conto della fase del tronco — la prima sta in
        `hierarchy.machines_beyond_of`, il secondo in `hierarchy.axis_rank` —
        perche' la catena deve proseguire dove il tronco tiene l'asse: due
        criteri diversi misurerebbero una forma che il motore non sta
        costruendo.
        """
        trunk = at_port[(here, port_id)]
        far = trunk.end if trunk.start.component_id == here else trunk.start
        found = beyond((far.component_id, far.port_id), trunk.connection_ids)
        if not found:
            return (2, 0.0, 0)
        return min(
            (
                *axis_rank(frozenset(definitions[item].functions), sizes[item]),
                order.get(item, 0),
            )
            for item in found
        )

    def onward(ref: PortRef, taken: set[TrunkKey]) -> PortRef | None:
        """La porta da cui la catena prosegue. `None` se finisce qui.

        Finisce su una **macchina**, che e' un capolinea e non un punto della
        tubazione; e finisce dove nessuna delle porte comunicanti porta una
        tratta di autostrada ancora libera.
        """
        definition = definitions[ref.component_id]
        if is_a_machine(definition):
            return None
        free = [
            port_id
            for port_id in sorted(ports_through(definition, ref.port_id))
            if (ref.component_id, port_id) in at_port
            and at_port[(ref.component_id, port_id)].connection_ids not in taken
        ]
        if not free:
            return None
        chosen = min(free, key=lambda port_id: (rank_of(ref.component_id, port_id), port_id))
        return PortRef(component_id=ref.component_id, port_id=chosen)

    def step_from(trunk: Trunk, entry: PortRef) -> tuple[PortRef, PortRef]:
        return (entry, trunk.end if entry == trunk.start else trunk.start)

    # **Le catene cominciano dalle macchine**, e nell'ordine strutturale: e' lo
    # stesso capo da cui la fase del tronco comincia a camminare, cosi' che
    # l'asse che quella costruisce sia l'asse su cui questa misura. Le tratte
    # che nessuna macchina tocca formano poi le proprie catene, nell'ordine in
    # cui la partizione le elenca.
    def seed_key(pair: tuple[Trunk, PortRef | None]) -> tuple[int, int, str]:
        trunk, anchor = pair
        if anchor is None:
            return (1, 0, trunk.connection_ids[0])
        return (0, order.get(anchor.component_id, 0), anchor.port_id)

    seeds: list[tuple[Trunk, PortRef | None]] = []
    for trunk in autostrade:
        anchors = [
            ref
            for ref in (trunk.start, trunk.end)
            if ref.component_id in machines
        ]
        seeds.append((trunk, anchors[0] if anchors else None))
    seeds.sort(key=seed_key)

    taken: set[TrunkKey] = set()
    found: list[Highway] = []
    for trunk, anchor in seeds:
        if trunk.connection_ids in taken:
            continue
        taken.add(trunk.connection_ids)
        entry = anchor if anchor is not None else trunk.start
        chain: list[tuple[PortRef, PortRef]] = [step_from(trunk, entry)]
        keys: list[TrunkKey] = [trunk.connection_ids]

        # Avanti, poi indietro: la catena cresce dai due capi finche' il
        # crocevia offre un proseguimento che nessun'altra catena ha preso.
        for forward in (True, False):
            cursor = chain[-1][1] if forward else chain[0][0]
            while True:
                across = onward(cursor, taken)
                if across is None:
                    break
                following = at_port[(across.component_id, across.port_id)]
                taken.add(following.connection_ids)
                piece = step_from(following, across)
                if forward:
                    chain.append(piece)
                    keys.append(following.connection_ids)
                else:
                    chain.insert(0, (piece[1], piece[0]))
                    keys.insert(0, following.connection_ids)
                cursor = piece[1]
        head, tail = chain[0][0].component_id, chain[-1][1].component_id
        # **La strada verso i terminali ha diritto a una curva** (D-144): e'
        # quella che va da un accumulo, un puffer o uno scambiatore a
        # un'utenza, cioe' esattamente la «strada secondaria» che la gerarchia
        # riconosce. Dal circolatore esce la gamba dritta, poi la curva, poi la
        # dorsale. L'autostrada fra le macchine di spina non ne ha diritto: li'
        # la forma e' la retta intera, e resta quella.
        found.append(
            Highway(
                keys=tuple(keys),
                steps=tuple(chain),
                turns_allowed=int(
                    (head in sorgenti and tail in users)
                    or (tail in sorgenti and head in users)
                ),
            )
        )
    return tuple(found)


def turns_of(highway: Highway, port_at: PortAt) -> int | None:
    """Quante curve fa la catena con questa posa, o `None` se non si misura.

    Ogni tratta deve restare un rettilineo: le due porte si guardano in faccia e
    la tratta va nel verso della porta da cui parte. Fra una tratta e la
    successiva la retta puo' **cambiare**, e ogni cambio — di direzione o di
    quota — e' una curva. Zero curve e' la retta di `DRAW-012` §C; una curva e'
    la forma che **D-144** chiede alla distribuzione.

    `None` quando la posa non colloca un pezzo, o quando una tratta non e' un
    rettilineo: non c'e' un numero di curve da dare, e chi chiama lo tratta come
    una catena che non sta nella propria forma.
    """
    heading: tuple[float, float] | None = None
    axis: float | None = None
    turns = 0
    for entry, exit_ in highway.steps:
        here = port_at(entry.component_id, entry.port_id)
        there = port_at(exit_.component_id, exit_.port_id)
        if here is None or there is None:
            return None
        (source, face), (goal, other) = here, there
        if other is not face.opposite:
            return None
        direction = _DIRECTION[face]
        if face in _HORIZONTAL_FACES:
            if abs(source.y_mm - goal.y_mm) > _TOLERANCE_MM:
                return None
            if (goal.x_mm - source.x_mm) * direction[0] <= _TOLERANCE_MM:
                return None
            quota = source.y_mm
        else:
            if abs(source.x_mm - goal.x_mm) > _TOLERANCE_MM:
                return None
            if (goal.y_mm - source.y_mm) * direction[1] <= _TOLERANCE_MM:
                return None
            quota = source.x_mm
        if heading is not None and (
            heading != direction or abs((axis or 0.0) - quota) > _TOLERANCE_MM
        ):
            turns += 1
        heading, axis = direction, quota
    if heading is None:
        return None
    return turns


def lies_in_line(highway: Highway, port_at: PortAt) -> bool:
    """Vero se la catena sta **nella propria forma**, con questa posa.

    Per l'autostrada fra le macchine di spina la forma e' la retta intera, ed e'
    l'invariante che `DRAW-012` §C ha costruito: le due porte di ogni tratta si
    guardano in faccia, la tratta va nel verso della porta da cui parte, e fra
    una tratta e la successiva **la retta non cambia**. E' la condizione che
    fallisce quando ogni frammento e' dritto e la catena fa un gomito sul
    raccordo che li unisce.

    Per la strada verso i terminali la forma e' quella di **D-144**: gamba
    rettilinea, **una** curva, dorsale. L'invariante non si applica piu' da un
    capo all'altro — si applica **a tratti**, con una curva dichiarata fra le
    due — e quella curva non e' una cessione: e' la forma giusta.

    Una posa che non colloca uno dei pezzi non e' una catena storta: e' una
    catena che non si puo' ancora misurare, e la risposta e' `False` senza
    giudizio — chi chiama usa l'invariante in modo monotono, «cio' che e' dritto
    non si storce», e su una catena non misurabile non c'e' niente da
    conservare.
    """
    turns = turns_of(highway, port_at)
    return turns is not None and turns <= highway.turns_allowed


def crooked_highways(
    laid: Iterable[Highway], port_at: PortAt
) -> tuple[Highway, ...]:
    """Le catene che con questa posa non sono una retta."""
    return tuple(item for item in laid if not lies_in_line(item, port_at))


__all__ = [
    "Highway",
    "PortAt",
    "crooked_highways",
    "highways",
    "lies_in_line",
    "turns_of",
]
