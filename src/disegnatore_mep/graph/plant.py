"""L'impianto letto come un grafo: nodi con la propria sigla, archi, incroci.

Il modello dell'impianto **e' gia'** un grafo — i pezzi sono nodi, le tubazioni
sono archi — ma finora non si poteva ne' leggere ne' citare ne' contare: i pezzi
non avevano un nome con cui indicarli. Questo modulo e' quel nome, e la lettura
che ne discende (D-097).

**Dove vivono le sigle, e perche' qui.** La sigla non e' una proprieta' del
catalogo: il catalogo conosce i *tipi* di pezzo, non i pezzi di questo impianto,
e due volani dello stesso tipo hanno sigle diverse. Non e' nemmeno un campo del
modello: il modello porta la sigla che l'ingegnere ha scritto a mano, e le altre
si **derivano** — riscriverle dentro il modello vorrebbe dire tenerne due copie
che possono divergere. La sigla vive quindi qui, in una lettura del modello che
si ricalcola sempre uguale, e chiunque la mostri — la tavola, la distinta, il
documento per il committente — la chiede a `PlantGraph` invece di inventarsene
una (D-097: una sigla sola per tutto il prodotto).

**Da dove si comincia a contare** (D-098). Non dall'ordine in cui il file elenca
i pezzi o le tubazioni, che e' un fatto del file e non dell'impianto: si parte
dalle **sorgenti dichiarate** — chi il calore lo produce, e il confine da cui il
fluido entra nell'edificio — e si segue il fluido. La prima valvola che si
incontra uscendo dal generatore e' la numero uno della sua famiglia. Quali
famiglie siano sorgenti lo dice una tabella di dati, mai un elenco di nomi:
un impianto con una caldaia al posto della pompa di calore comincia allo stesso
modo.

**Il verso non lo inventa questo modulo.** Una connessione del modello va sempre
dalla porta da cui il fluido **esce** a quella in cui **entra**: e' la stessa
origine da cui il progetto ricava mandata e ritorno (`layout/flow.py`) e
l'ordine di lettura della tavola. Qui la si riusa, non se ne apre una seconda.

**Un circuito e' un anello, non un albero.** Quando la lettura torna su un pezzo
gia' incontrato non si ferma e non riparte: dice che li' il giro si richiude. Un
albero si spezzerebbe sul primo ritorno.

**Cio' che non si sa dire non si tace.** Un attacco su cui non arriva nessuna
tubazione, un pezzo che nessuna sorgente raggiunge, una tubazione che nessuna
lettura attraversa: sono i silenzi che questo progetto continua a riscoprire, e
qui diventano dati che il documento e' obbligato a mostrare.
"""

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Literal

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition
from disegnatore_mep.model.project import PortRef, ProjectModel
from disegnatore_mep.model.types import PortFlow

from .naming import FamilyEntry, Naming

WRITTEN_TAG = re.compile(r"^([A-Z]+)-(\d+)$")
"""Come e' fatta una sigla: famiglia, trattino, numero.

Una sigla scritta a mano che non abbia questa forma si rispetta lo stesso, ma
non prenota nessun numero: non si saprebbe quale.
"""

StartKind = Literal["source", "store", "onward", "unreached"]
"""Perche' una lettura comincia da li'.

`source` — e' una sorgente dichiarata: chi produce il fluido, o il confine da
cui entra. `store` — nessuna sorgente produce quel fluido, ma quel pezzo lo
tiene in serbo, e quindi e' li' che nasce. `onward` — il giro prosegue da un
pezzo gia' incontrato, con un fluido che cambia nome attraversandolo. `unreached`
— nessuna sorgente arriva fin li': non e' un modo di leggere, e' una cosa da
dire.
"""


class GraphError(ValueError):
    """Il grafo non si lascia leggere, e dice perche'."""


@dataclass(frozen=True)
class Pipe:
    """Un arco: la tubazione fra due pezzi, col proprio fluido."""

    connection_id: str
    network_id: str
    medium: str
    leaves: PortRef
    """Il pezzo, e l'attacco, da cui il fluido esce."""

    enters: PortRef
    """Il pezzo, e l'attacco, in cui il fluido entra."""

    def other_end(self, component_id: str, port_id: str) -> PortRef:
        near = PortRef(component_id=component_id, port_id=port_id)
        return self.enters if self.leaves == near else self.leaves


@dataclass(frozen=True)
class Arm:
    """Un attacco di un pezzo, numerato come il braccio di un incrocio (D-097)."""

    number: int
    port_id: str
    medium: str
    flow: PortFlow
    pipes: tuple[str, ...]
    """Le tubazioni che convergono qui, in ordine di lettura."""

    @property
    def is_a_crossing(self) -> bool:
        """Piu' di una tubazione su un attacco solo: e' un incrocio."""
        return len(self.pipes) > 1

    @property
    def carries_nothing(self) -> bool:
        """Un attacco su cui non arriva nessuna tubazione."""
        return not self.pipes


@dataclass(frozen=True)
class Node:
    """Un pezzo dell'impianto, con la sua sigla e i suoi bracci."""

    component_id: str
    sigla: str
    name: str
    prefix: str
    family: str
    written_by_the_engineer: bool
    arms: tuple[Arm, ...]
    media: tuple[str, ...]
    stored_medium: str | None

    @property
    def crossings(self) -> tuple[Arm, ...]:
        return tuple(arm for arm in self.arms if arm.is_a_crossing)

    @property
    def free_arms(self) -> tuple[Arm, ...]:
        return tuple(arm for arm in self.arms if arm.carries_nothing)


@dataclass(frozen=True)
class Step:
    """Un passo della passeggiata: da un pezzo al successivo, lungo una tubazione."""

    number: int
    departs_from: str
    departs_arm: int
    arrives_at: str
    arrives_arm: int
    connection_id: str
    network_id: str
    medium: str
    closes_the_ring: bool
    """Si e' tornati su un pezzo gia' incontrato **seguendo lo stesso giro**: e'
    li' che il circuito si chiude su se' stesso, e la lettura lo dice invece di
    fermarsi come se mancasse un pezzo."""

    rejoins: bool
    """Si e' arrivati su un pezzo gia' letto, ma da un giro diverso: l'acqua
    fredda che arriva al bollitore non chiude nessun anello, ci si innesta."""

    onward_arms: tuple[int, ...]
    """I bracci del pezzo d'arrivo da cui la lettura prosegue, oltre a quello
    da cui si e' arrivati. Piu' d'uno vuol dire che li' l'impianto si dirama."""


@dataclass(frozen=True)
class Reading:
    """Una passeggiata: da dove comincia, su che fluido, e i passi che fa."""

    start: str
    medium: str
    kind: StartKind
    departing_arms: tuple[int, ...]
    steps: tuple[Step, ...]


@dataclass(frozen=True)
class PlantGraph:
    """L'impianto letto come grafo. Si costruisce con `read_plant`."""

    nodes: tuple[Node, ...]
    """I pezzi, nell'ordine in cui la lettura li incontra: e' anche l'ordine
    in cui sono stati numerati."""

    pipes: tuple[Pipe, ...]
    readings: tuple[Reading, ...]
    unreached: tuple[str, ...]
    """I pezzi a cui nessuna sorgente arriva."""

    unread_pipes: tuple[str, ...]
    """Le tubazioni che nessuna lettura attraversa."""

    def node(self, component_id: str) -> Node:
        for item in self.nodes:
            if item.component_id == component_id:
                return item
        raise GraphError(f"nessun nodo per {component_id}")

    def pipe(self, connection_id: str) -> Pipe:
        for item in self.pipes:
            if item.connection_id == connection_id:
                return item
        raise GraphError(f"nessuna tubazione per {connection_id}")

    @property
    def sigle(self) -> dict[str, str]:
        """La sigla di ogni pezzo. E' cio' che tavola e distinta devono mostrare."""
        return {item.component_id: item.sigla for item in self.nodes}

    @property
    def crossings(self) -> tuple[tuple[Node, Arm], ...]:
        return tuple(
            (node, arm) for node in self.nodes for arm in node.crossings
        )

    @property
    def free_arms(self) -> tuple[tuple[Node, Arm], ...]:
        return tuple(
            (node, arm) for node in self.nodes for arm in node.free_arms
        )


def read_plant(
    project: ProjectModel, catalog: ComponentRegistry, naming: Naming
) -> PlantGraph:
    """Legge l'impianto come grafo e ne assegna le sigle.

    Il risultato non dipende dall'ordine in cui il file elenca le tubazioni ne'
    da quello in cui elenca i pezzi: ogni scelta fra due strade si decide su
    cio' che l'impianto dichiara — il verso del fluido, il numero del braccio —
    e, quando davvero due strade sono indistinguibili, su un criterio fisso che
    non ha niente a che vedere con l'ordine del file.
    """
    return _Reader(project, catalog, naming).read()


class _Reader:
    def __init__(
        self, project: ProjectModel, catalog: ComponentRegistry, naming: Naming
    ) -> None:
        self._project = project
        self._naming = naming
        self._definitions: dict[str, ComponentDefinition] = {}
        self._families: dict[str, FamilyEntry] = {}
        for component in project.components:
            definition = catalog.get(component.definition_id)
            self._definitions[component.id] = definition
            self._families[component.id] = naming.family_of(
                tuple(definition.functions), component.id
            )
        self._media_order = {entry.medium: index for index, entry in enumerate(naming.media)}
        self._pipes = self._read_pipes()
        self._by_id = {pipe.connection_id: pipe for pipe in self._pipes}
        self._at_arm = self._index_pipes()
        self._arms = self._number_arms()
        self._met: list[str] = []
        self._traversed: set[str] = set()
        self._from_source: set[str] = set()
        self._scopes: list[set[str]] = []
        """Per ogni lettura, i pezzi del giro di cui fa parte."""

        self._scope_of: dict[str, int] = {}
        """In quale giro ogni pezzo e' stato incontrato la prima volta."""

    # --- gli archi ------------------------------------------------------------

    def _read_pipes(self) -> tuple[Pipe, ...]:
        media = {network.id: network.medium for network in self._project.networks}
        pipes: list[Pipe] = []
        for connection in self._project.connections:
            medium = media.get(connection.network_id)
            if medium is None:
                raise GraphError(
                    f"la tubazione {connection.id} dice di appartenere a "
                    f"{connection.network_id}, che il modello non dichiara: non se "
                    f"ne saprebbe dire il fluido"
                )
            self._check_direction(connection.endpoint_a, PortFlow.IN, connection.id)
            self._check_direction(connection.endpoint_b, PortFlow.OUT, connection.id)
            pipes.append(
                Pipe(
                    connection_id=connection.id,
                    network_id=connection.network_id,
                    medium=medium,
                    leaves=connection.endpoint_a,
                    enters=connection.endpoint_b,
                )
            )
        return tuple(pipes)

    def _check_direction(self, ref: PortRef, forbidden: PortFlow, pipe: str) -> None:
        """Il verso e' quello del modello, e il modello non deve contraddirsi.

        Una connessione va da una porta che **esce** a una che **entra**: se il
        primo estremo fosse un ingresso, la lettura seguirebbe il fluido al
        contrario e non se ne accorgerebbe nessuno.
        """
        definition = self._definitions.get(ref.component_id)
        if definition is None:
            raise GraphError(
                f"la tubazione {pipe} tocca {ref.component_id}, che il modello non "
                f"elenca fra i pezzi"
            )
        port = next((item for item in definition.ports if item.id == ref.port_id), None)
        if port is None:
            raise GraphError(
                f"la tubazione {pipe} tocca un attacco che {ref.component_id} non ha"
            )
        if port.flow is forbidden:
            raise GraphError(
                f"la tubazione {pipe} e' scritta al contrario: il fluido non puo' "
                f"uscire da un ingresso ne' entrare in un'uscita"
            )

    def _index_pipes(self) -> dict[tuple[str, str], list[str]]:
        """Tutte le tubazioni di ogni attacco: mai una sola.

        E' il punto in cui questo modulo si smarca dal difetto che rendeva
        diverso lo stesso impianto scritto in un altro ordine: tenere **una**
        tubazione per attacco vuol dire che l'ultima o la prima del file decide
        cosa si legge. Qui l'attacco le tiene tutte, e l'ordine fra loro non
        viene dal file.
        """
        found: dict[tuple[str, str], list[str]] = defaultdict(list)
        for pipe in self._pipes:
            for ref in (pipe.leaves, pipe.enters):
                found[(ref.component_id, ref.port_id)].append(pipe.connection_id)
        for key, ids in found.items():
            ids.sort(key=lambda item: self._pipe_order(key[0], key[1], item))
        return dict(found)

    def _pipe_order(self, component_id: str, port_id: str, connection_id: str) -> tuple[str, str]:
        """Fra due tubazioni sullo stesso attacco si sceglie sempre allo stesso modo.

        Il criterio e' arbitrario ma fisso, e soprattutto **non e' l'ordine del
        file**: due tubazioni che convergono sullo stesso attacco sono
        indistinguibili per l'impianto, e l'unica cosa che conta e' che la
        scelta non cambi riscrivendo lo stesso impianto in un altro ordine.
        """
        peer = self._by_id[connection_id].other_end(component_id, port_id)
        return (peer.component_id, connection_id)

    # --- i bracci -------------------------------------------------------------

    def _number_arms(self) -> dict[str, tuple[Arm, ...]]:
        numbered: dict[str, tuple[Arm, ...]] = {}
        for component in self._project.components:
            definition = self._definitions[component.id]
            numbered[component.id] = tuple(
                Arm(
                    number=index + 1,
                    port_id=port.id,
                    medium=port.medium,
                    flow=port.flow,
                    pipes=tuple(self._at_arm.get((component.id, port.id), ())),
                )
                for index, port in enumerate(definition.ports)
            )
        return numbered

    # --- la passeggiata -------------------------------------------------------

    def _departures(
        self, component_id: str, medium: str
    ) -> list[tuple[int, int, str, str]]:
        """Le tubazioni da cui la lettura puo' proseguire, in ordine.

        Prima quelle su cui il fluido **esce**, poi quelle da cui arriva: si
        segue l'acqua, e solo dopo la si risale. A parita' di verso, i bracci
        nell'ordine in cui il pezzo li dichiara.
        """
        found: list[tuple[int, int, str, str]] = []
        for arm in self._arms[component_id]:
            for connection_id in arm.pipes:
                pipe = self._by_id[connection_id]
                if pipe.medium != medium:
                    continue
                near = PortRef(component_id=component_id, port_id=arm.port_id)
                leaves = pipe.leaves == near
                peer = pipe.other_end(component_id, arm.port_id)
                found.append(
                    (0 if leaves else 1, arm.number, peer.component_id, connection_id)
                )
        return sorted(found)

    def _onward_arms(self, component_id: str, medium: str, arrived_on: int) -> tuple[int, ...]:
        return tuple(
            arm.number
            for arm in self._arms[component_id]
            if arm.number != arrived_on
            and any(self._by_id[item].medium == medium for item in arm.pipes)
        )

    def _arm_of(self, ref: PortRef) -> int:
        for arm in self._arms[ref.component_id]:
            if arm.port_id == ref.port_id:
                return arm.number
        raise GraphError(f"{ref.component_id} non ha l'attacco {ref.port_id}")

    def _reading_from(
        self, start: str, medium: str, kind: StartKind, reachable: bool
    ) -> Reading:
        """Una passeggiata, e il **giro** di cui fa parte.

        Il giro conta per una cosa sola: distinguere un anello che si richiude
        da un innesto. Una lettura che riparte da un pezzo gia' incontrato —
        perche' li' il fluido cambia nome, o perche' li' viene tenuto in serbo —
        prosegue lo stesso giro e ne eredita la memoria; una lettura che parte
        da un'altra sorgente comincia un giro suo, e arrivare su un pezzo gia'
        letto non e' un anello ma un innesto.
        """
        inherited = self._scope_of.get(start)
        scope = set(self._scopes[inherited]) if inherited is not None else set()
        self._scopes.append(scope)
        here = len(self._scopes) - 1
        self._meet(start, here, reachable)
        steps: list[Step] = []
        self._explore(start, medium, steps, reachable, here)
        return Reading(
            start=start,
            medium=medium,
            kind=kind,
            departing_arms=self._onward_arms(start, medium, 0),
            steps=tuple(steps),
        )

    def _meet(self, component_id: str, scope: int, reachable: bool) -> None:
        if component_id not in self._met:
            self._met.append(component_id)
        self._scopes[scope].add(component_id)
        self._scope_of.setdefault(component_id, scope)
        if reachable:
            self._from_source.add(component_id)

    def _explore(
        self,
        component_id: str,
        medium: str,
        steps: list[Step],
        reachable: bool,
        scope: int,
    ) -> None:
        for _, arm_number, _, connection_id in self._departures(component_id, medium):
            if connection_id in self._traversed:
                continue
            self._traversed.add(connection_id)
            pipe = self._by_id[connection_id]
            near_port = next(
                arm.port_id for arm in self._arms[component_id] if arm.number == arm_number
            )
            far = pipe.other_end(component_id, near_port)
            closes = far.component_id in self._scopes[scope]
            rejoins = not closes and far.component_id in self._met
            arrives_arm = self._arm_of(far)
            steps.append(
                Step(
                    number=len(steps) + 1,
                    departs_from=component_id,
                    departs_arm=arm_number,
                    arrives_at=far.component_id,
                    arrives_arm=arrives_arm,
                    connection_id=connection_id,
                    network_id=pipe.network_id,
                    medium=pipe.medium,
                    closes_the_ring=closes,
                    rejoins=rejoins,
                    onward_arms=()
                    if closes or rejoins
                    else self._onward_arms(far.component_id, medium, arrives_arm),
                )
            )
            if closes or rejoins:
                continue
            self._meet(far.component_id, scope, reachable)
            self._explore(far.component_id, medium, steps, reachable, scope)

    # --- da dove si comincia --------------------------------------------------

    def _in_reading_order(self) -> list[str]:
        """I pezzi in un ordine che non dipende da come il file li elenca."""
        return sorted(
            (item.id for item in self._project.components),
            key=lambda item: (self._naming.order_of(self._families[item]), item),
        )

    def _media_leaving(self, component_id: str) -> list[str]:
        found = {
            pipe.medium
            for pipe in self._pipes
            if pipe.leaves.component_id == component_id
        }
        return sorted(found, key=lambda item: (self._media_order.get(item, len(self._media_order)), item))

    def _media_touching(self, component_id: str) -> list[str]:
        found = {
            pipe.medium
            for pipe in self._pipes
            for ref in (pipe.leaves, pipe.enters)
            if ref.component_id == component_id
        }
        return sorted(found, key=lambda item: (self._media_order.get(item, len(self._media_order)), item))

    def _walk_everything(self) -> list[Reading]:
        readings: list[Reading] = []
        ordered = self._in_reading_order()

        # Le sorgenti dichiarate: chi il fluido lo produce, e il confine da cui
        # entra. Un confine da cui il fluido esce e' una partenza; un prelievo,
        # dove il fluido se ne va, non lo e'.
        for component_id in ordered:
            if not self._families[component_id].starts_the_reading:
                continue
            for medium in self._media_leaving(component_id):
                readings.append(
                    self._reading_from(component_id, medium, "source", reachable=True)
                )

        # Chi tiene un fluido in serbo e' la sorgente di quel fluido: l'acqua
        # calda sanitaria nasce dentro il bollitore, non all'acquedotto.
        for component_id in ordered:
            stored = self._definitions[component_id].stored_medium
            if stored is None or not self._untraversed_at(component_id, stored):
                continue
            readings.append(
                self._reading_from(
                    component_id, stored, "store", component_id in self._from_source
                )
            )

        # Dove un fluido cambia mestiere, il giro prosegue con un altro nome:
        # cio' che entra liquido esce gassoso, e la lettura del primo non tocca
        # il secondo. Si riparte dal pezzo — gia' incontrato — da cui quel
        # fluido esce, nell'ordine in cui la lettura lo ha incontrato.
        # Poi cio' che nessuna sorgente raggiunge, che si legge lo stesso
        # perche' sparire e' il silenzio che questo progetto continua a
        # riscoprire, ma dichiarato per quello che e'.
        while True:
            found = self._seed_onward() or self._seed_island(ordered)
            if found is None:
                break
            readings.append(found)
        return readings

    def _seed_onward(self) -> Reading | None:
        for component_id in list(self._met):
            for medium in self._media_leaving(component_id):
                if self._untraversed_leaving(component_id, medium):
                    return self._reading_from(
                        component_id, medium, "onward", component_id in self._from_source
                    )
        return None

    def _seed_island(self, ordered: list[str]) -> Reading | None:
        for component_id in ordered:
            if component_id in self._met:
                continue
            media = self._media_touching(component_id)
            return self._reading_from(
                component_id, media[0] if media else "", "unreached", reachable=False
            )
        return None

    def _untraversed_at(self, component_id: str, medium: str) -> bool:
        return any(
            pipe.medium == medium
            and pipe.connection_id not in self._traversed
            and component_id in (pipe.leaves.component_id, pipe.enters.component_id)
            for pipe in self._pipes
        )

    def _untraversed_leaving(self, component_id: str, medium: str) -> bool:
        return any(
            pipe.medium == medium
            and pipe.connection_id not in self._traversed
            and pipe.leaves.component_id == component_id
            for pipe in self._pipes
        )

    # --- le sigle -------------------------------------------------------------

    def _assign_sigle(self) -> dict[str, str]:
        written = {
            item.id: item.tag for item in self._project.components if item.tag is not None
        }
        used: dict[str, int] = {}
        for tag in written.values():
            shaped = WRITTEN_TAG.match(tag)
            if shaped is not None:
                prefix, number = shaped.group(1), int(shaped.group(2))
                used[prefix] = max(used.get(prefix, 0), number)

        sigle: dict[str, str] = {}
        for component_id in self._met:
            if component_id in written:
                sigle[component_id] = written[component_id]
                continue
            prefix = self._families[component_id].prefix
            used[prefix] = used.get(prefix, 0) + 1
            sigle[component_id] = f"{prefix}-{used[prefix]:02d}"
        counted = Counter(sigle.values())
        repeated = sorted(item for item, times in counted.items() if times > 1)
        if repeated:
            raise GraphError(
                f"due pezzi porterebbero la stessa sigla: {', '.join(repeated)}. "
                f"Una sigla ripetuta non identifica niente"
            )
        return sigle

    # --- il risultato ---------------------------------------------------------

    def read(self) -> PlantGraph:
        readings = self._walk_everything()
        missing = [
            item.id for item in self._project.components if item.id not in self._met
        ]
        if missing:
            raise GraphError(
                f"la lettura non ha incontrato {', '.join(sorted(missing))}: un "
                f"pezzo che nessuna lettura tocca resterebbe senza sigla"
            )
        sigle = self._assign_sigle()
        nodes = tuple(
            Node(
                component_id=component_id,
                sigla=sigle[component_id],
                name=self._definitions[component_id].name,
                prefix=self._families[component_id].prefix,
                family=self._families[component_id].name,
                written_by_the_engineer=any(
                    item.id == component_id and item.tag is not None
                    for item in self._project.components
                ),
                arms=self._arms[component_id],
                media=tuple(self._media_touching(component_id)),
                stored_medium=self._definitions[component_id].stored_medium,
            )
            for component_id in self._met
        )
        return PlantGraph(
            nodes=nodes,
            pipes=self._pipes,
            readings=tuple(readings),
            unreached=tuple(
                component_id
                for component_id in self._met
                if component_id not in self._from_source
            ),
            unread_pipes=tuple(
                pipe.connection_id
                for pipe in self._pipes
                if pipe.connection_id not in self._traversed
            ),
        )


__all__ = [
    "Arm",
    "GraphError",
    "Node",
    "Pipe",
    "PlantGraph",
    "Reading",
    "StartKind",
    "Step",
    "read_plant",
]
