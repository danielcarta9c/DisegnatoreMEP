"""Le linee idrauliche e l'indirizzo dei nodi, come i civici di una strada (D-105).

Le sigle dicono **che cosa** e' un pezzo e mai **dove** sta: per sapere dov'era
`VI-03` bisognava risalire un elenco, e una passeggiata che era una sola mandata
sembrava una sequenza di salti. Questo modulo da' il nome che mancava: ogni
**linea idraulica** ha una sigla di famiglia e un numero (`CP.01`), ogni pezzo
che ci sta sopra e' un **nodo numerato lungo di lei** (`CP.01.N.02`), e cio' che
pende da uno stacco e' un **civico del nodo** (`CP.01.N.02.1`).

Come per le sigle, l'indirizzo e' una **lettura** del modello, mai un campo
scritto dentro: si ricalcola sempre uguale, e chi lo mostra lo chiede a
`PlantLines` invece di inventarsene uno.

Le regole della strada, come il PM le ha date:

- **dove due linee si incontrano, la principale tira dritto e la secondaria
  muore** su quel nodo: con due generatori, la linea del primo prosegue e quella
  del secondo finisce sul nodo di innesto;
- **dove una linea si sdoppia, la principale tiene il nome nudo e i rami
  prendono una lettera** (`RP.01a`): cosi' il nome del ramo dice da chi
  discende, e il nome della principale non cambia mai per qualcosa successo
  altrove;
- in tutti e due i casi **la principale e' quella che va verso la prima
  sorgente**, nell'ordine gia' fissato da D-098. Dove nessun ramo porta a una
  sorgente — la deviatrice in mandata, la presa di un ricircolo — decide
  l'ordine dei bracci dichiarati dal pezzo, che e' lo stesso ordine in cui la
  passeggiata li percorre.

**La famiglia di una linea e' un dato, non una riga di programma**: vive in
`naming/lines.json` e si legge dal fluido della rete, dal mestiere della
sorgente da cui la rete parte e dal verso — mandata o ritorno — mai dal nome di
una rete o di un componente. Una linea che la tabella non sa nominare ferma la
generazione nominando il colpevole, come ogni altra cosa che non si sa dire.
"""

import sys
from collections import defaultdict
from dataclasses import dataclass
from typing import Literal

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition
from disegnatore_mep.layout.flow import GENERATOR_FUNCTIONS, LOAD_FUNCTIONS, STORE_FUNCTIONS
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import Domain

from .naming import LineNaming
from .plant import GraphError, Pipe, PlantGraph

Direction = Literal["supply", "return"]
"""Mandata o ritorno. In tabella e nel documento si dice in italiano."""


def _far_side(pipe: Pipe, component_id: str) -> str:
    """Il pezzo all'altro capo della tubazione, qualunque sia il verso."""
    if pipe.leaves.component_id == component_id:
        return pipe.enters.component_id
    return pipe.leaves.component_id

DISTRIBUTION_FUNCTIONS = frozenset({"distribution"})
"""Chi distribuisce su piu' circuiti: un collettore. La linea ci finisce
dentro, e da ogni sua uscita ne parte una nuova col proprio numero — il PM
parla di «tre circuiti secondari», non di tre rami di uno stesso nome."""

PASS_THROUGH_FUNCTIONS = frozenset({"diversion"})
"""Chi sdoppia il flusso senza essere un raccordo: la valvola deviatrice.
La linea la attraversa come attraversa un T, e il ramo deviato prende la
lettera. I raccordi veri si riconoscono gia' da `is_a_fitting`."""


@dataclass(frozen=True)
class HydraulicLine:
    """Una linea idraulica: la strada, con i suoi nodi in fila."""

    name: str
    """La sigla della linea: `CP.01`, oppure `RP.01a` per una diramazione."""

    family_prefix: str
    family_name: str
    """Come si chiama in italiano quel genere di linea: «mandata primaria»."""

    network_id: str
    direction: Direction
    branch_of: str | None
    """Il nome della linea da cui questa si e' staccata, se e' un ramo."""

    node_ids: tuple[str, ...]
    """I pezzi lungo la linea, dal capo alla fine, compresi i capi che
    appartengono ad altre linee: quelli si citano con l'indirizzo che hanno."""


@dataclass(frozen=True)
class PlantLines:
    """Le linee dell'impianto e l'indirizzo di ogni pezzo. Da `read_lines`."""

    lines: tuple[HydraulicLine, ...]
    owner: dict[str, str]
    """Per ogni pezzo, la linea che gli ha dato l'indirizzo: la prima che lo
    ha incontrato, nell'ordine della passeggiata."""

    addresses: dict[str, str]
    """L'indirizzo di ogni pezzo — nodo (`CP.01.N.02`) o civico
    (`CP.01.N.02.1`). Uno solo per pezzo, sempre."""

    hanging: dict[str, tuple[str, ...]]
    """Per ogni nodo, i pezzi appesi ai suoi stacchi, nell'ordine dei civici."""

    run_pipes: dict[str, tuple[str, ...]]
    """Per ogni rete idraulica, le tubazioni del percorso: le strade, senza le
    tubazioni dei civici. Serve a chi legge per dire se una linea che finisce
    su un nodo di un'altra chiude un anello o vi si innesta."""

    def line(self, name: str) -> HydraulicLine:
        for item in self.lines:
            if item.name == name:
                return item
        raise GraphError(f"nessuna linea di nome {name}")

    def address_of(self, component_id: str) -> str:
        found = self.addresses.get(component_id)
        if found is None:
            raise GraphError(f"nessun indirizzo per {component_id}")
        return found


def read_lines(
    project: ProjectModel,
    catalog: ComponentRegistry,
    graph: PlantGraph,
    naming: LineNaming,
) -> PlantLines:
    """Battezza le linee e numera i nodi, camminando dalle sorgenti (D-098).

    Il risultato non dipende dall'ordine del file di ingresso: ogni scelta si
    decide sull'ordine in cui la lettura del grafo ha incontrato i pezzi, che
    e' gia' invariante, e sull'ordine dei bracci che ogni pezzo dichiara.
    """
    return _Liner(project, catalog, graph, naming).read()


class _Liner:
    def __init__(
        self,
        project: ProjectModel,
        catalog: ComponentRegistry,
        graph: PlantGraph,
        naming: LineNaming,
    ) -> None:
        self._project = project
        self._graph = graph
        self._naming = naming
        self._definitions: dict[str, ComponentDefinition] = {
            item.id: catalog.get(item.definition_id) for item in project.components
        }
        self._rank = {node.component_id: index for index, node in enumerate(graph.nodes)}
        self._medium_of_network = {item.id: item.medium for item in project.networks}
        self._by_id = {pipe.connection_id: pipe for pipe in graph.pipes}

        self._hanging, hang_pipes = self._read_hangs()
        self._run_pipes = self._read_run_pipes(hang_pipes)

        self._assigned: set[str] = set()
        """Le tubazioni gia' date a una linea."""

        self._owner: dict[str, str] = {}
        self._lines: list[HydraulicLine] = []
        self._numbers: dict[str, int] = defaultdict(int)
        self._letters: dict[str, int] = defaultdict(int)

    # --- gli stacchi, prima di tutto -------------------------------------------

    def _read_hangs(self) -> tuple[dict[str, tuple[str, ...]], set[str]]:
        """Cio' che pende da ogni nodo, e le tubazioni con cui pende.

        Un civico non e' un pezzo della strada: le sue tubazioni vanno tolte
        dal percorso prima di camminare, altrimenti la catena appesa a un vaso
        sembrerebbe una linea.
        """
        hanging: dict[str, tuple[str, ...]] = {}
        pipes: set[str] = set()
        for component in self._project.components:
            found: list[str] = []
            for port in self._definitions[component.id].ports:
                if not port.off_the_run:
                    continue
                for pipe in self._pipes_at(component.id, port.id):
                    pipes.add(pipe.connection_id)
                    found.extend(self._chain_from(component.id, pipe, pipes))
            if found:
                hanging[component.id] = tuple(found)
        return hanging, pipes

    def _chain_from(self, owner: str, first: Pipe, pipes: set[str]) -> list[str]:
        """La catena appesa a uno stacco, un pezzo alla volta."""
        chain: list[str] = []
        previous, current = owner, _far_side(first, owner)
        edge = first
        while current not in chain:
            chain.append(current)
            onward = [
                pipe
                for arm in self._graph.node(current).arms
                for connection_id in arm.pipes
                if (pipe := self._by_id[connection_id]).connection_id != edge.connection_id
                and previous
                not in (pipe.leaves.component_id, pipe.enters.component_id)
            ]
            if len(onward) != 1:
                break
            edge = onward[0]
            pipes.add(edge.connection_id)
            previous, current = current, _far_side(edge, current)
        return chain

    def _pipes_at(self, component_id: str, port_id: str) -> list[Pipe]:
        return [
            self._by_id[connection_id]
            for arm in self._graph.node(component_id).arms
            if arm.port_id == port_id
            for connection_id in arm.pipes
        ]

    def _read_run_pipes(self, hang_pipes: set[str]) -> dict[str, list[Pipe]]:
        """Le tubazioni del percorso, rete per rete: le strade, senza i civici.

        Le linee di D-105 sono **idrauliche**: le reti che non portano acqua —
        canali d'aria, linee frigorifere, gas — restano fuori, e i loro pezzi
        si citano con la sola sigla.
        """
        hydronic = {
            item.id for item in self._project.networks if item.domain is Domain.HYDRONIC
        }
        found: dict[str, list[Pipe]] = defaultdict(list)
        for pipe in self._graph.pipes:
            if pipe.connection_id in hang_pipes or pipe.network_id not in hydronic:
                continue
            found[pipe.network_id].append(pipe)
        return dict(found)

    # --- che cosa e' ogni pezzo, sulla propria rete -----------------------------

    def _functions(self, component_id: str) -> frozenset[str]:
        return frozenset(self._definitions[component_id].functions)

    def _passes_through(self, component_id: str) -> bool:
        """Un raccordo o una deviatrice: la linea principale li attraversa."""
        return (
            self._definitions[component_id].is_a_fitting
            or bool(self._functions(component_id) & PASS_THROUGH_FUNCTIONS)
        )

    def _ends_the_line(self, component_id: str) -> bool:
        """Una macchina: sorgente, utilizzatore, riserva, confine, collettore.

        La linea ci finisce dentro. Tutto il resto — valvole, filtri, pompe,
        raccordi — la lascia passare.
        """
        if self._passes_through(component_id):
            return False
        functions = self._functions(component_id)
        return bool(
            functions & (GENERATOR_FUNCTIONS | LOAD_FUNCTIONS | DISTRIBUTION_FUNCTIONS)
        )

    def _leaving(self, component_id: str, network_id: str) -> list[Pipe]:
        """Le tubazioni che escono dal pezzo su quella rete, in ordine di braccio."""
        return [
            pipe
            for arm in self._graph.node(component_id).arms
            for connection_id in arm.pipes
            if (pipe := self._by_id[connection_id]).network_id == network_id
            and pipe.leaves.component_id == component_id
            and pipe.leaves.port_id == arm.port_id
            and pipe in self._run_pipes.get(network_id, [])
        ]

    # --- il verso: mandata o ritorno -------------------------------------------

    def _source_of(self, network_id: str) -> str:
        """Da dove la rete parte: il pezzo di rango piu' basso con una
        tubazione in uscita. Il rango e' l'ordine della passeggiata (D-098),
        quindi su un circuito di generazione e' il primo generatore, su un
        secondario e' la riserva da cui il giro comincia."""
        candidates = {
            pipe.leaves.component_id for pipe in self._run_pipes.get(network_id, [])
        }
        if not candidates:
            raise GraphError(
                f"la rete {network_id} non ha tubazioni sul percorso: non c'e' "
                f"nessuna linea da battezzare"
            )
        return min(candidates, key=lambda item: self._rank[item])

    def _directions(self, network_id: str) -> dict[str, Direction]:
        """Il verso di ogni tubazione della rete, camminando dalla sorgente.

        Prima di attraversare un utilizzatore l'acqua e' mandata; dopo, e'
        ritorno. Un generatore azzera il conto: quello che esce da lui e' di
        nuovo mandata, anche se e' il secondo di una cascata e la lettura lo
        raggiunge dal ritorno comune.
        """
        source = self._source_of(network_id)
        directions: dict[str, Direction] = {}
        left: dict[str, bool] = {}
        frontier: list[tuple[int, str, bool]] = [(self._rank[source], source, False)]
        while frontier:
            frontier.sort()
            _, current, crossed = frontier.pop(0)
            if current in left:
                continue
            left[current] = crossed
            if self._functions(current) & GENERATOR_FUNCTIONS:
                crossed = False
            for pipe in self._leaving(current, network_id):
                directions.setdefault(
                    pipe.connection_id, "return" if crossed else "supply"
                )
                target = pipe.enters.component_id
                onward = crossed or bool(self._functions(target) & LOAD_FUNCTIONS)
                frontier.append((self._rank[target], target, onward))
        # Una tubazione che la camminata dal fluido non raggiunge e' gia'
        # denunciata dal grafo fra i silenzi: qui prende il verso di mandata
        # per non restare senza nome, e la si vede comunque.
        for pipe in self._run_pipes.get(network_id, []):
            directions.setdefault(pipe.connection_id, "supply")
        return directions

    # --- la costruzione delle linee ---------------------------------------------

    def read(self) -> PlantLines:
        # A parita' di sorgente — l'accumulo genera sia il secondario sia il
        # sanitario — decide il nome della rete, che e' un dato del modello e
        # non cambia riscrivendo lo stesso impianto in un altro ordine.
        networks = sorted(
            self._run_pipes,
            key=lambda item: (self._rank[self._source_of(item)], item),
        )
        for network_id in networks:
            self._read_network(network_id)
        addresses = self._assign_addresses()
        return PlantLines(
            lines=tuple(self._lines),
            owner=dict(self._owner),
            addresses=addresses,
            hanging=dict(self._hanging),
            run_pipes={
                network_id: tuple(pipe.connection_id for pipe in pipes)
                for network_id, pipes in self._run_pipes.items()
            },
        )

    def _read_network(self, network_id: str) -> None:
        directions = self._directions(network_id)
        enders = sorted(
            {
                ref.component_id
                for pipe in self._run_pipes[network_id]
                for ref in (pipe.leaves, pipe.enters)
                if self._ends_the_line(ref.component_id)
            },
            key=lambda item: self._rank[item],
        )
        queue: list[tuple[str, Pipe]] = []
        for ender in enders:
            for pipe in self._leaving(ender, network_id):
                if pipe.connection_id in self._assigned:
                    continue
                self._build_line(network_id, ender, pipe, directions, None, queue)
                while queue:
                    parent, branch = queue.pop(0)
                    if branch.connection_id in self._assigned:
                        continue
                    self._build_line(
                        network_id,
                        branch.leaves.component_id,
                        branch,
                        directions,
                        parent,
                        queue,
                    )
        # Un giro senza nessuna macchina — solo valvole e raccordi — non ha un
        # capo da cui partire: si parte dal pezzo di rango piu' basso, cosi'
        # nemmeno un anello degenere resta senza nome.
        while True:
            leftover = [
                pipe
                for pipe in self._run_pipes[network_id]
                if pipe.connection_id not in self._assigned
            ]
            if not leftover:
                break
            first = min(
                leftover,
                key=lambda item: (self._rank[item.leaves.component_id], item.connection_id),
            )
            self._build_line(
                network_id, first.leaves.component_id, first, directions, None, queue
            )
            while queue:
                parent, branch = queue.pop(0)
                if branch.connection_id not in self._assigned:
                    self._build_line(
                        network_id,
                        branch.leaves.component_id,
                        branch,
                        directions,
                        parent,
                        queue,
                    )

    def _build_line(
        self,
        network_id: str,
        head: str,
        first: Pipe,
        directions: dict[str, Direction],
        branch_of: str | None,
        queue: list[tuple[str, Pipe]],
    ) -> None:
        direction = directions[first.connection_id]
        name = self._baptise(network_id, direction, branch_of)
        nodes: list[str] = [head]
        if head not in self._owner:
            self._owner[head] = name
        pipe = first
        self._assigned.add(pipe.connection_id)
        current = pipe.enters.component_id
        while True:
            nodes.append(current)
            if current in self._owner and self._owner[current] != name:
                # La strada finisce su un nodo di un'altra linea: e' l'innesto,
                # o il punto dove il giro si richiude. La secondaria muore qui.
                break
            if current not in self._owner:
                self._owner[current] = name
            if self._ends_the_line(current):
                break
            onward = [
                item
                for item in self._leaving(current, network_id)
                if item.connection_id not in self._assigned
            ]
            if not onward:
                break
            main = min(
                onward,
                key=lambda item: (
                    self._nearest_ender_rank(network_id, item, {current}, name),
                    self._arm_number(current, item),
                ),
            )
            for item in onward:
                if item is not main:
                    # Le lettere restano piatte sul nome base: la diramazione
                    # di una diramazione e' la lettera successiva della stessa
                    # strada, come la bis e la ter di una statale.
                    queue.append((branch_of or name, item))
            pipe = main
            self._assigned.add(pipe.connection_id)
            current = pipe.enters.component_id
        entry = self._naming.family_for(
            medium=self._medium_of_network[network_id],
            fed_by=self._fed_by(network_id),
            direction=direction,
        )
        self._lines.append(
            HydraulicLine(
                name=name,
                family_prefix=entry.prefix,
                family_name=entry.name,
                network_id=network_id,
                direction=direction,
                branch_of=branch_of,
                node_ids=tuple(nodes),
            )
        )

    def _baptise(self, network_id: str, direction: Direction, branch_of: str | None) -> str:
        if branch_of is not None:
            self._letters[branch_of] += 1
            letter = chr(ord("a") + self._letters[branch_of] - 1)
            return f"{branch_of}{letter}"
        entry = self._naming.family_for(
            medium=self._medium_of_network[network_id],
            fed_by=self._fed_by(network_id),
            direction=direction,
        )
        self._numbers[entry.prefix] += 1
        return f"{entry.prefix}.{self._numbers[entry.prefix]:02d}"

    def _fed_by(self, network_id: str) -> str:
        """Il mestiere della sorgente della rete, per la tabella delle famiglie."""
        functions = self._functions(self._source_of(network_id))
        if functions & GENERATOR_FUNCTIONS:
            return "generator"
        if functions & STORE_FUNCTIONS:
            return "store"
        if "boundary" in functions:
            return "boundary"
        return "other"

    def _arm_number(self, component_id: str, pipe: Pipe) -> int:
        for arm in self._graph.node(component_id).arms:
            if pipe.connection_id in arm.pipes:
                return arm.number
        raise GraphError(
            f"la tubazione {pipe.connection_id} non tocca nessun braccio di {component_id}"
        )

    def _nearest_ender_rank(
        self, network_id: str, pipe: Pipe, seen: set[str], line_name: str
    ) -> int:
        """Il rango del primo capolinea che quel ramo raggiunge seguendo l'acqua.

        E' il criterio della principale: fra due rami vince chi arriva al
        capolinea incontrato prima dalla passeggiata — sul ritorno comune di
        due macchine, quello che va alla prima (D-105). Un ramo che rientra
        sulla **stessa** linea che si sta costruendo non va verso nessuna
        sorgente: e' un anello — il ricircolo — e non vince mai.
        """
        current = pipe.enters.component_id
        walked = set(seen)
        while True:
            owned_by_another = (
                current in self._owner and self._owner[current] != line_name
            )
            if self._ends_the_line(current) or owned_by_another:
                return self._rank[current]
            if current in walked:
                return sys.maxsize
            walked.add(current)
            onward = self._leaving(current, network_id)
            candidates = [
                item for item in onward if item.enters.component_id not in walked
            ]
            if not candidates:
                return sys.maxsize
            if len(candidates) == 1:
                current = candidates[0].enters.component_id
                continue
            return min(
                self._nearest_ender_rank(network_id, item, walked, line_name)
                for item in candidates
            )

    # --- gli indirizzi ----------------------------------------------------------

    def _assign_addresses(self) -> dict[str, str]:
        addresses: dict[str, str] = {}
        for line in self._lines:
            position = 0
            for component_id in line.node_ids:
                if self._owner.get(component_id) != line.name:
                    continue
                if component_id in addresses:
                    continue
                position += 1
                addresses[component_id] = f"{line.name}.N.{position:02d}"
        for node_id, chain in self._hanging.items():
            root = addresses.get(node_id)
            if root is None:
                # Un pezzo con uno stacco che nessuna linea tocca: il grafo lo
                # denuncia gia' fra i silenzi, e un civico senza strada non
                # significherebbe niente.
                continue
            for index, hung in enumerate(chain, start=1):
                addresses[hung] = f"{root}.{index}"
        return addresses


__all__ = [
    "Direction",
    "HydraulicLine",
    "PlantLines",
    "read_lines",
]
