"""Le tratte e il loro ordine.

Una **tratta** e' la fila dei pezzi fra due punti fissi dell'impianto. Fissi
sono le macchine e tutto cio' che il progettista ha scritto: la skill non li
sposta. Riordinabile e' soltanto cio' che le regole hanno aggiunto, e ogni pezzo
aggiunto sa **a quale macchina si ancora** e **quali vincoli dichiara**.

Il verso in cui si conta e' quello che un termotecnico usa leggendo una
centrale: **dalla macchina verso l'impianto**. E' l'unico rispetto a cui frasi
come «io sto lato impianto rispetto all'intercettazione» significano qualcosa.
Una tratta ha due capi: i pezzi ancorati al primo si contano da li', quelli
ancorati al secondo dall'altro capo, e chi non e' ancorato a nessuno dei due sta
in mezzo.
"""

from collections import defaultdict
from dataclasses import dataclass

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.model.project import ConnectionModel, PortRef, ProjectModel
from disegnatore_mep.model.types import PortFlow
from disegnatore_mep.rules.schema import RuleDefinition


class AssemblyError(ValueError):
    """Due vincoli che non possono stare insieme, o una tratta che non si legge."""


@dataclass(frozen=True)
class Piece:
    """Un pezzo sulla tratta, con cio' che serve a metterlo in fila."""

    component_id: str
    functions: frozenset[str]
    anchor: str | None
    """La macchina a cui la regola lo ha ancorato. Vuoto per cio' che il
    progettista ha scritto: quello non si riordina."""

    against_the_anchor: bool = False
    """Sta attaccato alla macchina: fra lui e lei non ci va nessun altro pezzo."""

    before: tuple[str, ...] = ()
    """I mestieri che devono venire **dopo** di lui, verso l'impianto."""

    after: tuple[str, ...] = ()
    """I mestieri che devono venire **prima** di lui, verso l'impianto."""

    rule: str | None = None
    """La regola che lo ha voluto. Serve a nominarla se i vincoli litigano."""

    entry: str = ""
    exit: str = ""
    """I suoi due attacchi sul percorso, nel verso in cui il fluido lo attraversa."""


@dataclass(frozen=True)
class Run:
    """Una tratta: due capi fissi e la fila dei pezzi in mezzo."""

    head: PortRef
    tail: PortRef
    pieces: tuple[Piece, ...]
    pipes: tuple[str, ...]
    network_id: str

    @property
    def component_ids(self) -> tuple[str, ...]:
        return tuple(item.component_id for item in self.pieces)


def _rule_of(project: ProjectModel, component_id: str) -> str | None:
    for item in project.components:
        if item.id != component_id:
            continue
        for evidence in item.evidence:
            if evidence.kind == "rule":
                return evidence.reference.split("@", 1)[0]
    return None


class _Assembler:
    def __init__(
        self,
        project: ProjectModel,
        catalog: ComponentRegistry,
        rules: dict[str, RuleDefinition],
    ) -> None:
        self._project = project
        self._rules = rules
        self._definitions = {
            item.id: catalog.get(item.definition_id) for item in project.components
        }
        self._off_the_run: set[tuple[str, str]] = {
            (item.id, port.id)
            for item in project.components
            for port in self._definitions[item.id].ports
            if port.off_the_run
        }
        self._network_of = {
            item.id: item.network_id for item in project.connections
        }
        self._pipes_at: dict[tuple[str, str], list[ConnectionModel]] = defaultdict(list)
        for connection in project.connections:
            for ref in (connection.endpoint_a, connection.endpoint_b):
                if (ref.component_id, ref.port_id) not in self._off_the_run:
                    self._pipes_at[(ref.component_id, ref.port_id)].append(connection)
        self._by_id = {item.id: item for item in project.components}

    # --- chi si puo' spostare e chi no ---------------------------------------

    def run_ports(self, component_id: str) -> list[str]:
        """Gli attacchi sul percorso, nel verso in cui il fluido attraversa.

        Prima quello da cui si entra, poi quello da cui si esce: e' l'ordine con
        cui la tratta va ricucita, e sbagliarlo produce una tubazione fra due
        uscite che il validatore respinge — giustamente.
        """
        ports = [
            port
            for port in self._definitions[component_id].ports
            if not port.off_the_run
        ]
        rank = {PortFlow.IN: 0, PortFlow.BIDIRECTIONAL: 1, PortFlow.OUT: 2}
        return [port.id for port in sorted(ports, key=lambda item: rank[item.flow])]

    def movable(self, component_id: str) -> bool:
        """Solo cio' che una regola ha aggiunto, e che sta **in fila**, si sposta.

        Quello che il progettista ha scritto resta dove lo ha messo: la skill
        completa il suo impianto, non lo riscrive. E si sposta solo chi ha due
        attacchi sul percorso: una confluenza ne ha tre, e spostarla vorrebbe
        dire cambiare la topologia invece dell'ordine.
        """
        return (
            _rule_of(self._project, component_id) is not None
            and len(self.run_ports(component_id)) == 2
        )

    def anchor_of(self, component_id: str) -> str | None:
        """La macchina a cui quel pezzo e' stato ancorato.

        Si legge dall'identificativo che la proposta ha derivato dai dati — voce
        di catalogo, componente ancorante, attacco — che e' l'unico posto in cui
        l'ancoraggio sopravvive all'applicazione. Si riconosce **confrontando**
        con i componenti che esistono davvero, mai spezzando la stringa a naso.
        """
        candidates = [
            other
            for other in self._by_id
            if other != component_id
            and f"-{other.replace('_', '-')}-" in f"-{component_id}-"
        ]
        if not candidates:
            return None
        return max(candidates, key=len)

    # --- le tratte ------------------------------------------------------------

    def runs(self) -> list[Run]:
        found: list[Run] = []
        walked: set[str] = set()
        for connection in self._project.connections:
            if connection.id in walked or self._leaves_the_run(connection):
                continue
            run = self._run_through(connection)
            walked.update(run.pipes)
            if run.pieces:
                found.append(run)
        return found

    def _leaves_the_run(self, connection: ConnectionModel) -> bool:
        return any(
            (ref.component_id, ref.port_id) in self._off_the_run
            for ref in (connection.endpoint_a, connection.endpoint_b)
        )

    def _run_through(self, seed: ConnectionModel) -> Run:
        back, head, pipes_back = self._walk(seed, seed.endpoint_a)
        forward, tail, pipes_forward = self._walk(seed, seed.endpoint_b)
        pieces = [*reversed(back), *forward]
        return Run(
            head=head,
            tail=tail,
            pieces=tuple(self._piece(item) for item in pieces),
            pipes=tuple([*reversed(pipes_back), seed.id, *pipes_forward]),
            network_id=self._network_of[seed.id],
        )

    def _walk(
        self, seed: ConnectionModel, towards: PortRef
    ) -> tuple[list[str], PortRef, list[str]]:
        """Cammina da un capo finche' incontra qualcosa che non si sposta."""
        collected: list[str] = []
        pipes: list[str] = []
        current, edge = towards, seed
        while self.movable(current.component_id):
            # Se ci si arriva da uno stacco, quel pezzo e' il **piede** della
            # derivazione, non un pezzo della fila: la tratta finisce li'.
            if (current.component_id, current.port_id) in self._off_the_run:
                break
            collected.append(current.component_id)
            onward = [
                (candidate, ref)
                for port_id in self.run_ports(current.component_id)
                if port_id != current.port_id
                for candidate in self._pipes_at[(current.component_id, port_id)]
                if candidate.id != edge.id
                for ref in (candidate.endpoint_a, candidate.endpoint_b)
                if ref.component_id != current.component_id
            ]
            if len(onward) != 1:
                break
            edge, current = onward[0]
            pipes.append(edge.id)
        return collected, current, pipes

    def hanging_from(self, component_id: str) -> str | None:
        """Cio' che pende dallo stacco di quel pezzo, se ci pende qualcosa."""
        for owner, port_id in sorted(self._off_the_run):
            if owner != component_id:
                continue
            for connection in self._pipes_of(owner, port_id):
                for ref in (connection.endpoint_a, connection.endpoint_b):
                    if ref.component_id != component_id:
                        return ref.component_id
        return None

    def _pipes_of(self, component_id: str, port_id: str) -> list[ConnectionModel]:
        return [
            connection
            for connection in self._project.connections
            if PortRef(component_id=component_id, port_id=port_id)
            in (connection.endpoint_a, connection.endpoint_b)
        ]

    def _piece(self, component_id: str) -> Piece:
        # Una derivazione non e' un pezzo a se': e' il piede dello stacco. Dove
        # sta nella fila lo decide **cio' che ci pende**, e i vincoli sono quelli
        # di quell'accessorio. Trattarla per conto suo la lascerebbe dove capita
        # e porterebbe la sua valvola di sicurezza con se'.
        speaks_for = component_id
        if self._definitions[component_id].is_a_fitting:
            hung = self.hanging_from(component_id)
            if hung is not None:
                speaks_for = hung
        rule_id = _rule_of(self._project, speaks_for)
        rule = self._rules.get(rule_id or "")
        ports = self.run_ports(component_id)
        return Piece(
            component_id=component_id,
            functions=frozenset(self._definitions[speaks_for].functions),
            anchor=self.anchor_of(speaks_for),
            against_the_anchor=bool(rule and rule.ordering.against_the_anchor),
            before=tuple(rule.ordering.before) if rule else (),
            after=tuple(rule.ordering.after) if rule else (),
            rule=rule_id,
            entry=ports[0],
            exit=ports[-1],
        )


def runs_of(
    project: ProjectModel,
    catalog: ComponentRegistry,
    rules: dict[str, RuleDefinition],
) -> list[Run]:
    """Le tratte dell'impianto, cosi' come sono adesso."""
    return _Assembler(project, catalog, rules).runs()


def ordered(run: Run) -> tuple[Piece, ...]:
    """La fila dei pezzi di una tratta, messa in ordine dai vincoli dichiarati.

    Tre gruppi, e il verso di lettura e' quello: cio' che e' ancorato al capo di
    partenza si conta da li', cio' che e' ancorato al capo di arrivo si conta
    dall'altra parte, e cio' che non e' ancorato a nessuno dei due sta in mezzo.
    Dentro ogni gruppo decide l'ordinamento sui vincoli.
    """
    head, tail = run.head.component_id, run.tail.component_id
    blocks = _blocks(run)
    at_head = [block for block in blocks if block[0].anchor == head]
    at_tail = [block for block in blocks if block[0].anchor == tail]
    taken = {id(block) for block in (*at_head, *at_tail)}
    between = [block for block in blocks if id(block) not in taken]
    return (
        *_flatten(_sorted_blocks(at_head)),
        *_flatten(between),
        *_flatten(reversed(_sorted_blocks(at_tail))),
    )


def _blocks(run: Run) -> list[list[Piece]]:
    """I pezzi raggruppati con cio' che li serve.

    Un accessorio non viaggia da solo: le valvole che lo isolano sono ancorate a
    **lui**, non alla macchina, e stanno una per lato. Spostare l'accessorio
    lasciandole indietro le trasformerebbe in due valvole che non chiudono
    niente. Il blocco e' percio' l'unita' che si mette in fila, e dentro il
    blocco l'ordine resta quello che c'e' — che e' gia' quello giusto, perche'
    le valvole sono nate una per attacco.
    """
    order = {item.component_id: index for index, item in enumerate(run.pieces)}
    leader: dict[str, str] = {}
    for item in run.pieces:
        current = item
        while current.anchor in order:
            current = run.pieces[order[current.anchor]]
        leader[item.component_id] = current.component_id
    grouped: dict[str, list[Piece]] = {}
    for item in run.pieces:
        grouped.setdefault(leader[item.component_id], []).append(item)
    return [grouped[key] for key in dict.fromkeys(leader.values())]


def _flatten(blocks: object) -> list[Piece]:
    return [item for block in blocks for item in block]  # type: ignore[attr-defined]


def _sorted_blocks(blocks: list[list[Piece]]) -> list[list[Piece]]:
    """Mette in fila i blocchi guardando i vincoli del pezzo che li guida."""
    if len(blocks) < 2:
        return list(blocks)
    leaders = [block[0] for block in blocks]
    by_leader = {block[0].component_id: block for block in blocks}
    return [by_leader[item.component_id] for item in _sorted(leaders)]


def _sorted(pieces: list[Piece]) -> list[Piece]:
    """Ordinamento sui vincoli dichiarati, dal capo verso l'impianto.

    Un pezzo che dichiara «prima di cio' che chiude» precede ogni pezzo che
    chiude; uno che dichiara «dopo l'intercettazione» la segue. Dove i vincoli
    non dicono niente l'ordine e' libero, e si tiene stabile per identificativo:
    stabile non vuol dire significativo, e nessuno deve leggerci un ordine
    impiantistico che non c'e'.
    """
    if len(pieces) < 2:
        return list(pieces)
    # Chi sta attaccato alla macchina viene prima di tutto il resto: e' un
    # vincolo di sicurezza, non una preferenza, e non si contratta con gli altri.
    against = [item for item in pieces if item.against_the_anchor]
    if against and len(against) != len(pieces):
        return [*_sorted(against), *_sorted([item for item in pieces if item not in against])]
    needs: dict[str, set[str]] = {item.component_id: set() for item in pieces}
    for item in pieces:
        for other in pieces:
            if other.component_id == item.component_id:
                continue
            if other.functions & set(item.before):
                needs[other.component_id].add(item.component_id)
            if other.functions & set(item.after):
                needs[item.component_id].add(other.component_id)

    by_id = {item.component_id: item for item in pieces}
    placed: list[Piece] = []
    waiting = dict(needs)
    while waiting:
        free = sorted(key for key, before in waiting.items() if not (before & set(waiting)))
        if not free:
            stuck = sorted(waiting)
            rules = sorted({by_id[key].rule or key for key in stuck})
            raise AssemblyError(
                f"the declared constraints contradict each other on "
                f"{', '.join(stuck)}: {' and '.join(rules)} cannot both be "
                f"satisfied, so the file would be wrong whichever order came out"
            )
        for key in free:
            placed.append(by_id[key])
            del waiting[key]
    return placed


def assemble(
    project: ProjectModel,
    catalog: ComponentRegistry,
    rules: dict[str, RuleDefinition],
) -> ProjectModel:
    """Il grafo definitivo: gli stessi pezzi, nella fila che i vincoli impongono.

    Non aggiunge e non toglie niente. Riordina cio' che le regole hanno posato e
    ricollega le tubazioni di conseguenza: e' l'ultimo passo prima che il grafo
    vada in approvazione, e da qui in poi la tavola ne e' la rappresentazione.
    """
    assembler = _Assembler(project, catalog, rules)
    connections = {item.id: item for item in project.connections}
    for run in assembler.runs():
        wanted = ordered(run)
        if [item.component_id for item in wanted] == list(run.component_ids):
            continue
        for pipe in run.pipes:
            connections.pop(pipe, None)
        stops: list[PortRef] = [run.head]
        for item in wanted:
            stops.append(PortRef(component_id=item.component_id, port_id=item.entry))
            stops.append(PortRef(component_id=item.component_id, port_id=item.exit))
        stops.append(run.tail)
        for index in range(0, len(stops) - 1, 2):
            fresh = ConnectionModel(
                id=f"{run.pipes[0]}-{index // 2 + 1}",
                network_id=run.network_id,
                endpoint_a=stops[index],
                endpoint_b=stops[index + 1],
            )
            connections[fresh.id] = fresh
    return project.model_copy(update={"connections": list(connections.values())})


__all__ = ["AssemblyError", "Piece", "Run", "assemble", "ordered", "runs_of"]
