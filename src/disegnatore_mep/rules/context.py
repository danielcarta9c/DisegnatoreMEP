"""La vista che una condizione puo' interrogare, e nulla di piu'.

E' qui che il vincolo «una regola non puo' nominare un componente» smette di
essere un'intenzione e diventa una proprieta': chi valuta una condizione riceve
questo oggetto, che risponde per **proprieta' dichiarata** (P1), per funzione,
per dominio e per fluido, e non espone il modello. Gli identificativi escono
solo dalla parte che costruisce la proposta, che deve pur dire su cosa si
ancora.

Le proprieta' sono la novita' di P2, e sono il motivo per cui P1 veniva prima:
«tutto cio' che si smonta in esercizio» non e' una domanda che si possa fare a
un indice di funzioni.
"""

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass, field
from itertools import product

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import (
    CLOSING_FUNCTIONS,
    SHUTOFF_REGIMES,
    ComponentTrait,
    HydraulicState,
    OnBoard,
    PortDefinition,
)
from disegnatore_mep.model.project import ConnectionModel, PortRef, ProjectModel

from .proposal import anchor_of_proposed
from .schema import RuleCardinality, RuleDefinition


@dataclass(frozen=True)
class RuleContext:
    """Indici pronti su modello e catalogo. Costruita una volta per valutazione."""

    functions: dict[str, frozenset[str]]
    """Funzioni di catalogo di ciascun componente."""

    traits: dict[str, frozenset[ComponentTrait]]
    """Le proprieta' che ciascun componente dichiara di se' (P1)."""

    carried: dict[str, frozenset[str]]
    """Le funzioni che ciascun componente porta a bordo di fabbrica (D-106).

    Una regola non aggiunge cio' che **la macchina** dichiara di avere: il
    bordo soddisfa i bisogni ancorati a chi lo porta — il filtro integrato E'
    il filtro di quella macchina — e, per una regola di rete, vale solo se
    **ogni** ancoraggio della regola lo porta. Il bordo di un altro membro
    non conta mai: la sicurezza integrata della pompa di calore non e' la
    sicurezza del serbatoio, e un pezzo di sicurezza che sparisse per il
    bordo altrui sparirebbe in silenzio."""

    stored_media: dict[str, str]
    """Il fluido che ciascun componente tiene in serbo, per chi ne tiene uno."""

    fill_ports: dict[str, str]
    """L'attacco da cui la riserva di ciascun componente si riempie (C2).

    Solo per chi lo dichiara: un bollitore si riempie dall'ingresso freddo, un
    volano tecnico dal circuito e non dichiara niente."""

    ports: dict[str, tuple[PortDefinition, ...]]
    networks_of: dict[str, frozenset[str]]
    """Reti che ciascun componente tocca."""

    service_ports: dict[tuple[str, str], str]
    """L'attacco di servizio di un componente per una data funzione (D-101).

    Un volano dichiara lo scarico, lo sfiato e la sede della sonda; un bollitore
    la sola sonda. Chi ce l'ha riceve l'accessorio **li'**, invece che dentro la
    tubazione principale."""

    connection_of_port: dict[tuple[str, str], str]
    """Quale connessione tocca un dato attacco."""

    network_of_connection: dict[str, str]
    pipe_ends: dict[str, tuple[PortRef, PortRef]] = field(default_factory=dict)
    """Da dove esce e dove entra ciascuna tubazione **del percorso**.

    Il verso e' quello del modello: una connessione va sempre dalla porta da
    cui il fluido esce a quella in cui entra. Le tubazioni corte che reggono
    cio' che pende da uno stacco non stanno qui: il percorso non ci passa."""

    incoming: dict[str, tuple[str, ...]] = field(default_factory=dict)
    """Le tubazioni del percorso che **entrano** in ciascun componente."""

    outgoing: dict[str, tuple[str, ...]] = field(default_factory=dict)
    """Le tubazioni del percorso che **escono** da ciascun componente."""

    inline: frozenset[str] = frozenset()
    """Chi sta **su** una tubazione invece di essere un nodo del disegno."""

    states: dict[str, tuple[HydraulicState, ...]] = field(default_factory=dict)
    """Le configurazioni idrauliche ammesse di ciascun **multivia** (DRAW-006).

    Solo per chi le dichiara. E' l'unico dato su cui si decide se una porta
    comunica con un'altra dentro un pezzo che non e' un raccordo: chi cammina
    sulla rete lo legge da qui, e nessun modulo tiene un proprio elenco dei
    mestieri che si attraversano."""

    members: dict[str, tuple[str, ...]] = field(default_factory=dict)
    """Componenti di ciascuna rete, in ordine di modello."""

    own: dict[str, frozenset[str]] = field(default_factory=dict)
    lacking: dict[str, frozenset[str]] = field(default_factory=dict)
    """Le funzioni che ogni componente dichiara di **non** portare a bordo
    (I-046): l'altra meta' di `carried`. Cio' che non sta in nessuno dei due
    e' ignoto."""
    """Gli accessori **di ciascun pezzo**: quelli che una regola per componente
    gli ha posato sui suoi stessi attacchi (DRAW-005, I-034).

    Il filtro a Y sul ritorno della pompa di calore e' della pompa di calore:
    la regola che lo vuole parte da una proprieta' della macchina, lo conta una
    volta per macchina e lo posa sul suo attacco. Insieme formano il **gruppo
    manutenibile**, che si isola dall'esterno e mai fra i membri. Non entrano
    nel gruppo il corredo di rete — che si posa sul tratto comune e si conta
    una volta per rete, anche quando quel tratto comincia sull'attacco della
    macchina — ne' cio' che il progettista ha scritto, che non deriva da
    nessuna regola. Si legge dai dati: la regola in calce al pezzo e
    l'identificativo derivato dall'attacco, mai dal nome del pezzo."""

    @classmethod
    def build(
        cls,
        project: ProjectModel,
        catalog: ComponentRegistry,
        rules: Mapping[str, RuleDefinition] | None = None,
    ) -> "RuleContext":
        functions: dict[str, frozenset[str]] = {}
        traits: dict[str, frozenset[ComponentTrait]] = {}
        states: dict[str, tuple[HydraulicState, ...]] = {}
        carried: dict[str, frozenset[str]] = {}
        lacking: dict[str, frozenset[str]] = {}
        stored_media: dict[str, str] = {}
        fill_ports: dict[str, str] = {}
        ports: dict[str, tuple[PortDefinition, ...]] = {}
        inline: set[str] = set()
        service_ports: dict[tuple[str, str], str] = {}
        for component in project.components:
            resolved = catalog.resolve(component.definition_id)
            functions[component.id] = frozenset(resolved.definition.functions)
            traits[component.id] = resolved.definition.trait_set
            if resolved.definition.hydraulic_states:
                states[component.id] = resolved.definition.hydraulic_states
            carried[component.id] = frozenset(resolved.definition.carries_on_board)
            lacking[component.id] = frozenset(resolved.definition.lacks_on_board)
            if resolved.definition.fills_from is not None:
                fill_ports[component.id] = resolved.definition.fills_from
            if resolved.definition.stored_medium is not None:
                stored_media[component.id] = resolved.definition.stored_medium
            ports[component.id] = tuple(resolved.definition.ports)
            for port in resolved.definition.ports:
                if port.serves is not None:
                    service_ports[(component.id, port.serves)] = port.id
            # In linea per il disegno, oppure raccordo: in tutti e due i casi
            # la corsa ci passa attraverso e la camminata non si ferma.
            if resolved.is_inline or resolved.definition.is_a_fitting:
                inline.add(component.id)

        touched: dict[str, set[str]] = defaultdict(set)
        members: dict[str, list[str]] = defaultdict(list)
        connection_of_port: dict[tuple[str, str], str] = {}
        network_of_connection: dict[str, str] = {}
        pipe_ends: dict[str, tuple[PortRef, PortRef]] = {}
        incoming: dict[str, list[str]] = defaultdict(list)
        outgoing: dict[str, list[str]] = defaultdict(list)

        def off_the_run(ref: PortRef) -> bool:
            port = next(
                (item for item in ports.get(ref.component_id, ()) if item.id == ref.port_id),
                None,
            )
            return port is not None and port.off_the_run

        for connection in project.connections:
            network_of_connection[connection.id] = connection.network_id
            for ref in (connection.endpoint_a, connection.endpoint_b):
                touched[ref.component_id].add(connection.network_id)
                connection_of_port[(ref.component_id, ref.port_id)] = connection.id
                if ref.component_id not in members[connection.network_id]:
                    members[connection.network_id].append(ref.component_id)
            # Il percorso e' fatto delle sole tubazioni fra attacchi del
            # flusso: cio' che pende da uno stacco — attacco di servizio o
            # braccio di un raccordo — non e' strada, e chi cammina lungo la
            # rete non ci entra (D-101).
            if off_the_run(connection.endpoint_a) or off_the_run(connection.endpoint_b):
                continue
            pipe_ends[connection.id] = (connection.endpoint_a, connection.endpoint_b)
            outgoing[connection.endpoint_a.component_id].append(connection.id)
            incoming[connection.endpoint_b.component_id].append(connection.id)

        own: dict[str, set[str]] = defaultdict(set)
        if rules:
            attachments = [
                (item.id, port.id) for item in project.components for port in ports[item.id]
            ]
            for component in project.components:
                rule = next(
                    (
                        rules.get(evidence.reference.split("@", 1)[0])
                        for evidence in component.evidence
                        if evidence.kind == "rule"
                    ),
                    None,
                )
                if rule is None or rule.cardinality is RuleCardinality.PER_NETWORK:
                    continue
                if rule.then.placement.on_a_common_run:
                    continue
                anchor = anchor_of_proposed(component.id, component.definition_id, attachments)
                if anchor is not None and anchor.component_id != component.id:
                    own[anchor.component_id].add(component.id)

        return cls(
            functions=functions,
            traits=traits,
            carried=carried,
            stored_media=stored_media,
            fill_ports=fill_ports,
            ports=ports,
            networks_of={key: frozenset(value) for key, value in touched.items()},
            service_ports=service_ports,
            connection_of_port=connection_of_port,
            network_of_connection=network_of_connection,
            pipe_ends=pipe_ends,
            incoming={key: tuple(value) for key, value in incoming.items()},
            outgoing={key: tuple(value) for key, value in outgoing.items()},
            inline=frozenset(inline),
            states=states,
            # In ordine di nome, mai nell'ordine in cui il file elenca le
            # tubazioni: una regola che serve «il primo» della rete deve
            # servire lo stesso pezzo comunque l'impianto sia stato scritto.
            # Il collaudo ha visto il gruppo di riempimento migrare da una
            # pompa di calore all'altra permutando il file: si chiude qui.
            members={key: tuple(sorted(value)) for key, value in members.items()},
            own={key: frozenset(value) for key, value in own.items()},
            lacking=lacking,
        )

    # --- cio' che una condizione puo' chiedere ------------------------------

    def network_has(self, network_id: str, function: str) -> bool:
        """La funzione c'e' su quella rete, come **pezzo** dell'impianto.

        Il bordo macchina non entra qui: cio' che una macchina integra
        soddisfa i bisogni ancorati a lei (`carries`), non quelli della rete
        intera — contarlo qui faceva sparire in silenzio la sicurezza del
        serbatoio quando la pompa di calore dichiarava la propria.
        """
        return any(
            function in self.functions.get(component_id, frozenset())
            for component_id in self.members.get(network_id, ())
        )

    def carries(self, component_id: str, function: str) -> bool:
        """Quel componente porta quella funzione a bordo, di fabbrica."""
        return function in self.carried.get(component_id, frozenset())

    def on_board(self, component_id: str, function: str) -> OnBoard:
        """Cosa il catalogo dice di quella funzione dentro il mantello di quel
        pezzo: presente, assente, o ignoto — e ignoto non e' assente (I-046)."""
        if function in self.carried.get(component_id, frozenset()):
            return OnBoard.PRESENT
        if function in self.lacking.get(component_id, frozenset()):
            return OnBoard.ABSENT
        return OnBoard.UNKNOWN

    # --- chi comunica con chi, dentro un pezzo (DRAW-006, blocco C) ---------

    def admitted_states(self, component_id: str) -> tuple[HydraulicState | None, ...]:
        """Le configurazioni ammesse di un pezzo, o l'unica implicita.

        Chi non dichiara stati ne ha uno solo, che non ha nome: e' il modo in
        cui il pezzo e' sempre stato — un raccordo o un accessorio in linea si
        attraversa, una macchina no.
        """
        return self.states.get(component_id) or (None,)

    def linked_ports(
        self, component_id: str, port_id: str, state: HydraulicState | None = None
    ) -> frozenset[str]:
        """Gli attacchi del percorso che comunicano con questo, dentro il pezzo.

        Per un **multivia** lo dice il catalogo, stato per stato: l'ingresso di
        una deviatrice comunica con un ramo oppure con l'altro, e i due rami
        non comunicano mai fra loro. Per tutti gli altri vale la regola di
        sempre: chi sta in linea — o e' un raccordo — lascia passare la corsa
        fra tutti i suoi attacchi del percorso; una macchina la ferma.
        """
        declared = self.states.get(component_id)
        if declared:
            if state is not None:
                return state.linked(port_id)
            found: set[str] = set()
            for item in declared:
                found |= item.linked(port_id)
            return frozenset(found)
        if component_id not in self.inline:
            return frozenset()
        return frozenset(
            port.id
            for port in self.ports.get(component_id, ())
            if port.id != port_id and not port.off_the_run
        )

    def _stateful_on(self, network_id: str) -> tuple[str, ...]:
        """I multivia della rete, in ordine: su di loro si enumerano gli stati."""
        return tuple(
            component_id
            for component_id in self.members.get(network_id, ())
            if component_id in self.states
        )

    def _assignments(
        self, network_id: str
    ) -> tuple[dict[str, HydraulicState], ...]:
        """Le configurazioni ammesse della rete: una per ogni combinazione.

        Il prodotto degli stati dei multivia che la rete contiene. Senza
        multivia c'e' una configurazione sola, quella di sempre, e il costo e'
        quello di prima.
        """
        stateful = self._stateful_on(network_id)
        if not stateful:
            return ({},)
        return tuple(
            dict(zip(stateful, combination, strict=True))
            for combination in product(*(self.states[item] for item in stateful))
        )

    def own_closers(self, component_id: str) -> frozenset[str]:
        """Gli organi **propri** di un pezzo: su ciascuno dei suoi attacchi del
        percorso, il primo che chiude, letto attraverso i pezzi in linea —
        anche quelli che si manutengono, perche' il filtro della macchina e'
        della macchina e la valvola oltre il filtro isola tutti e due (I-034).
        Sono gli organi che la macchina chiude per essere manutenuta: nella
        configurazione ammessa, quando lei e' in esercizio, sono aperti."""
        found: set[str] = set()
        for port in self.connected_ports(component_id):
            cursor = component_id
            connection_id = self.connection_of_port.get((component_id, port.id))
            seen = {cursor}
            while connection_id is not None:
                peer = self._peer(connection_id, cursor)
                if peer is None or peer in seen:
                    break
                seen.add(peer)
                if CLOSING_FUNCTIONS & self.functions.get(peer, frozenset()):
                    found.add(peer)
                    break
                if peer not in self.inline:
                    break
                onward = [
                    item
                    for item in (*self.incoming.get(peer, ()), *self.outgoing.get(peer, ()))
                    if item != connection_id
                ]
                if len(onward) != 1:
                    break
                connection_id = onward[0]
                cursor = peer
        return frozenset(found)

    def cut_off_from(self, component_id: str, function: str, network_id: str) -> bool:
        """Il pezzo puo' restare **separato** da ogni pezzo con quella funzione
        sulla sua rete (I-046): il dominio di protezione, letto dalla
        connettivita', dalle intercettazioni e dalle configurazioni ammesse.

        Si cammina dagli attacchi del pezzo lungo le tubazioni della rete,
        in tutte e due le direzioni, attraverso tutto cio' che comunica —
        raccordi, accessori, macchine, serbatoi: l'acqua dentro e' una — e si
        guarda anche cio' che pende dagli stacchi. Un organo di chiusura si
        attraversa solo se e' **proprio** del pezzo: quelli sono aperti quando
        la macchina e' in esercizio; un organo altrui puo' essere chiuso mentre
        lei scalda, e oltre quello la protezione non conta.

        Dentro un **multivia** si passa solo per una comunicazione che lo stato
        ammette (DRAW-006, blocco C): l'ingresso di una deviatrice va su un ramo
        o sull'altro, mai su tutti e due, e i due rami non comunicano fra loro.
        La camminata si rifa' percio' in **ogni configurazione ammessa** della
        rete: e' protetto chi raggiunge la funzione in tutte; basta una
        configurazione in cui non la raggiunge perche' il pezzo sia un dominio
        a se'. Vero se esiste una configurazione in cui nessuna strada arriva
        alla funzione cercata.
        """
        return any(
            not self._reaches(component_id, function, network_id, assignment)
            for assignment in self._assignments(network_id)
        )

    def _reaches(
        self,
        component_id: str,
        function: str,
        network_id: str,
        assignment: Mapping[str, HydraulicState],
    ) -> bool:
        """La camminata di `cut_off_from`, in **una** configurazione della rete."""
        own = self.own_closers(component_id)
        frontier: list[tuple[str, str]] = []
        seen_pipes: set[str] = set()
        for port in self.connected_ports(component_id):
            connection_id = self.connection_of_port[(component_id, port.id)]
            if self.network_of_connection.get(connection_id) != network_id:
                continue
            seen_pipes.add(connection_id)
            frontier.append((connection_id, component_id))
        seen_pieces = {component_id}
        while frontier:
            connection_id, cursor = frontier.pop(0)
            arrival = self._peer_ref(connection_id, cursor)
            if arrival is None or arrival.component_id in seen_pieces:
                continue
            peer = arrival.component_id
            seen_pieces.add(peer)
            if function in self.functions.get(peer, frozenset()) or function in self.hanging_functions(peer):
                return True
            if CLOSING_FUNCTIONS & self.functions.get(peer, frozenset()) and peer not in own:
                continue
            for onward in sorted(self._onward(arrival, assignment)):
                if onward in seen_pipes or self.network_of_connection.get(onward) != network_id:
                    continue
                seen_pipes.add(onward)
                frontier.append((onward, peer))
        return False

    def _onward(
        self, arrival: PortRef, assignment: Mapping[str, HydraulicState]
    ) -> tuple[str, ...]:
        """Le tubazioni per cui la camminata prosegue oltre un pezzo raggiunto.

        Per un **multivia** sono quelle degli attacchi che lo stato assegnato
        mette in comunicazione con l'attacco da cui si e' arrivati; per tutti
        gli altri sono tutte quelle del percorso, come e' sempre stato — dentro
        una macchina o un serbatoio l'acqua e' una sola.
        """
        state = assignment.get(arrival.component_id)
        if state is None:
            return (
                *self.incoming.get(arrival.component_id, ()),
                *self.outgoing.get(arrival.component_id, ()),
            )
        return tuple(
            connection_id
            for port_id in sorted(
                self.linked_ports(arrival.component_id, arrival.port_id, state)
            )
            if (
                connection_id := self.connection_of_port.get(
                    (arrival.component_id, port_id)
                )
            )
            is not None
        )

    def run_holds(self, pipes: frozenset[str], function: str) -> bool:
        """Quella funzione e' gia' su uno di quei tratti, o vi pende.

        E' la soddisfazione di una regola che si posa su un **tratto comune**:
        l'ambito non e' la rete intera ma il dominio che quel tratto serve. Con
        l'ambito di rete, un secondo circuito chiuso restava senza il proprio
        corredo perche' il primo ce l'aveva gia' — ed e' il difetto che il PM
        ha visto sulla sicurezza (DRAW-006, blocco C, punti 4 e 5).
        """
        pieces = {
            ref.component_id
            for pipe in pipes
            if pipe in self.pipe_ends
            for ref in self.pipe_ends[pipe]
        }
        return any(
            function in self.functions.get(item, frozenset())
            or function in self.hanging_functions(item)
            for item in pieces
        )

    def components_with(self, network_id: str, function: str) -> tuple[str, ...]:
        return tuple(
            component_id
            for component_id in self.members.get(network_id, ())
            if function in self.functions.get(component_id, frozenset())
        )

    def anchors_of(
        self, network_id: str, function: str | None, trait: ComponentTrait | None
    ) -> tuple[str, ...]:
        """I componenti della rete che l'ancoraggio di una regola descrive.

        Proprieta' e funzione si sommano quando ci sono entrambe: la regola le
        ha dichiarate tutte e due perche' le vuole tutte e due.
        """
        return tuple(
            component_id
            for component_id in self.members.get(network_id, ())
            if (function is None or function in self.functions.get(component_id, frozenset()))
            and (trait is None or trait in self.traits.get(component_id, frozenset()))
        )

    def shutoff_regime_of(self, component_id: str) -> ComponentTrait:
        """Come quel componente si lascia chiudere.

        Esiste sempre per chi sta in catalogo: lo garantisce la validazione di
        P1. Un componente che il catalogo non conosce non arriva fin qui,
        perche' costruire questa vista lo avrebbe gia' fatto fallire.
        """
        return next(iter(self.traits[component_id] & SHUTOFF_REGIMES))

    def has_trait(self, component_id: str, trait: ComponentTrait) -> bool:
        return trait in self.traits.get(component_id, frozenset())

    def stores(self, component_id: str, medium: str) -> bool:
        """Quel componente tiene **in serbo** proprio quel fluido.

        Falso per chi non tiene niente in serbo: cosi' una regola che si occupa
        della riserva non si applica a chi non ne ha una."""
        return self.stored_media.get(component_id) == medium

    def fills_on(self, component_id: str, network_id: str) -> bool:
        """La riserva di quel componente si riempie da questa rete (C2).

        Vero solo per chi dichiara il proprio punto di riempimento e ce l'ha
        collegato: un attacco dichiarato ma libero non riempie niente."""
        port_id = self.fill_ports.get(component_id)
        if port_id is None:
            return False
        connection_id = self.connection_of_port.get((component_id, port_id))
        return (
            connection_id is not None
            and self.network_of_connection.get(connection_id) == network_id
        )

    def fill_port_of(self, component_id: str) -> str | None:
        """L'attacco da cui la riserva si riempie, se dichiarato."""
        return self.fill_ports.get(component_id)

    def run_from(
        self, connection_id: str, *, upstream: bool, network_id: str
    ) -> tuple[str, ...]:
        """Tutte le tubazioni da cui questa puo' essere alimentata, in ordine.

        Risalendo il fluido (`upstream`) si va verso chi lo manda; seguendolo
        si va verso chi lo riceve. La camminata attraversa raccordi e accessori
        in linea e **si apre sui rami**: dove due tubazioni confluiscono, si
        risalgono tutte e due, perche' l'acqua di questo ritorno puo' venire
        da entrambe. Si ferma su cio' che non e' in linea — una macchina, un
        serbatoio — e dove non c'e' piu' niente.

        L'ordine e' quello della scoperta, dal piu' vicino al piu' lontano: e'
        cosi' che il tratto comune si sceglie a monte della **prima**
        ripartizione e non piu' su. Fra rami pari si guarda l'identificativo
        della tubazione, mai l'ordine del file.

        **Perche' si apre sui rami.** Fermarsi alla prima confluenza faceva
        sparire il ritorno generale di un impianto ibrido: risalendo dalla
        caldaia si incontrava subito il punto in cui rientra il ramo del
        sanitario, la camminata si fermava li', e il tratto che porta tutta
        l'acqua di ritorno — quello fra il volume tecnico e la ripartizione
        verso le macchine — non veniva mai raggiunto. Il corredo del circuito
        diventava un punto aperto su un impianto che il punto lo aveva.
        """
        if connection_id not in self.pipe_ends:
            return ()
        chain = [connection_id]
        seen = {connection_id}
        frontier = [connection_id]
        while frontier:
            current = frontier.pop(0)
            leaves, enters = self.pipe_ends[current]
            ref = leaves if upstream else enters
            here = (self.incoming if upstream else self.outgoing).get(
                ref.component_id, ()
            )
            # Dentro un multivia si prosegue solo per una comunicazione che
            # **qualche** stato ammette: il tratto comune e' un fatto di
            # topologia — dove le mandate possono diventare una — e chi lo
            # raggiunga davvero, in ogni configurazione, lo dice il dominio di
            # protezione, che e' un'altra lettura (DRAW-006, blocco C).
            reachable = {
                self.connection_of_port.get((ref.component_id, port_id))
                for port_id in self.linked_ports(ref.component_id, ref.port_id)
            }
            for item in sorted(set(here) & {item for item in reachable if item}):
                if item in seen or self.network_of_connection.get(item) != network_id:
                    continue
                seen.add(item)
                chain.append(item)
                frontier.append(item)
        return tuple(chain)

    def service_port_for(self, component_id: str, function: str) -> str | None:
        """L'attacco che quel componente dedica a quella funzione, se ce l'ha."""
        return self.service_ports.get((component_id, function))

    def service_port_is_taken(self, component_id: str, function: str) -> bool:
        """Quell'attacco di servizio ha gia' qualcosa attaccato.

        Va guardato a parte: l'accessorio posato su uno stacco non sta sulla
        tubazione principale, quindi camminando lungo quella non lo si trova e
        lo si riproporrebbe a ogni passata.
        """
        port_id = self.service_ports.get((component_id, function))
        return port_id is not None and (component_id, port_id) in self.connection_of_port

    def port_carries(self, ref: PortRef, function: str) -> bool:
        """Un accessorio con quella funzione e' gia' sulla tubazione di questo attacco.

        Cammina lungo la fila degli accessori in linea, non si ferma al primo:
        dopo due o tre applicazioni una tubazione ne porta parecchi, e guardare
        solo il vicino faceva riproporre uno scarico che era gia' li', due
        accessori piu' in la'.

        La strada si sceglie **sulla struttura**, mai sull'ordine del file: da
        un pezzo in linea si prosegue per l'unica altra tubazione del percorso;
        da un raccordo con piu' strade — una diramazione, una confluenza, il
        piede di uno stacco — non si prosegue affatto, perche' un organo oltre
        la diramazione non chiude questo attacco. Prima la prossima tubazione
        la decideva l'ordine delle connessioni nel modello, e lo stesso
        impianto scritto in un altro ordine dava una risposta diversa.
        """
        cursor = ref.component_id
        connection_id = self.connection_of_port.get((ref.component_id, ref.port_id))
        seen = {cursor}
        while connection_id is not None:
            peer = self._peer(connection_id, cursor)
            if peer is None or peer in seen:
                return False
            if function in self.functions.get(peer, frozenset()):
                return True
            # Cio' che pende da uno stacco del pezzo sta **su questa
            # tubazione** (DRAW-005-R1, I-043): la sicurezza appesa al
            # raccordo di derivazione e' la sicurezza di quell'attacco, e una
            # camminata che passasse oltre il raccordo senza guardarci sopra
            # la riproporrebbe a ogni passata.
            if function in self.hanging_functions(peer):
                return True
            if peer not in self.inline:
                return False
            seen.add(peer)
            onward = [
                item
                for item in (
                    *self.incoming.get(peer, ()),
                    *self.outgoing.get(peer, ()),
                )
                if item != connection_id
            ]
            if len(onward) != 1:
                return False
            connection_id = onward[0]
            cursor = peer
        return False

    def _peer(self, connection_id: str, component_id: str) -> str | None:
        found = self._peer_ref(connection_id, component_id)
        return None if found is None else found.component_id

    def _peer_ref(self, connection_id: str, component_id: str) -> PortRef | None:
        """L'altro capo di una tubazione, **con l'attacco su cui arriva**.

        L'attacco serve a chi deve sapere se dentro il pezzo si prosegue: in un
        multivia dipende da quale porta si e' entrati, e la sola identita' del
        pezzo non basta piu' a dirlo.
        """
        for candidate, holder in self.connection_of_port.items():
            if holder == connection_id and candidate[0] != component_id:
                return PortRef(component_id=candidate[0], port_id=candidate[1])
        return None

    def hanging_functions(self, component_id: str) -> frozenset[str]:
        """Le funzioni di cio' che pende dagli stacchi di un pezzo.

        Si risale ogni attacco fuori dal percorso — il braccio di un raccordo,
        l'attacco di servizio di una macchina — attraverso gli organi in fila
        sullo stacco, fino all'accessorio che vi pende. Lo stacco non e' strada
        (`pipe_ends` non lo porta), quindi lo si percorre qui, a parte.
        """
        found: set[str] = set()
        for port in self.ports.get(component_id, ()):
            if not port.off_the_run:
                continue
            connection_id = self.connection_of_port.get((component_id, port.id))
            cursor = component_id
            seen = {cursor}
            while connection_id is not None:
                peer = self._peer(connection_id, cursor)
                if peer is None or peer in seen:
                    break
                found |= self.functions.get(peer, frozenset())
                seen.add(peer)
                onward = [
                    holder
                    for (owner, _), holder in self.connection_of_port.items()
                    if owner == peer and holder != connection_id
                ]
                if len(onward) != 1:
                    break
                connection_id, cursor = onward[0], peer
        return frozenset(found)

    # --- il gruppo manutenibile (DRAW-005, I-034) ---------------------------

    def same_group(self, first: str, second: str) -> bool:
        """I due pezzi sono un gruppo: uno e' un accessorio dell'altro."""
        return second in self.own.get(first, frozenset()) or first in self.own.get(
            second, frozenset()
        )

    def along(self, ref: PortRef) -> tuple[tuple[str, ...], tuple[str, ...]]:
        """Il tratto che parte da un attacco: i pezzi incontrati e le tubazioni
        percorse, fino al primo pezzo che **ferma**.

        Ferma un pezzo che non sta in linea, un pezzo che si manutiene — perche'
        il volume fra due pezzi manutenibili e' uno, e un organo oltre il
        secondo non chiude il primo — o un raccordo da cui il percorso prosegue
        in piu' direzioni. Il pezzo che ferma e' l'ultimo dell'elenco; una
        tubazione che finisce nel vuoto lascia l'elenco com'e'. La strada si
        sceglie sulla struttura, come `port_carries`, mai sull'ordine del file.
        """
        pieces: list[str] = []
        pipes: list[str] = []
        cursor = ref.component_id
        connection_id = self.connection_of_port.get((ref.component_id, ref.port_id))
        seen = {cursor}
        while connection_id is not None:
            pipes.append(connection_id)
            peer = self._peer(connection_id, cursor)
            if peer is None or peer in seen:
                break
            pieces.append(peer)
            seen.add(peer)
            if peer not in self.inline or self.has_trait(peer, ComponentTrait.MAINTAINABLE):
                break
            onward = [
                item
                for item in (*self.incoming.get(peer, ()), *self.outgoing.get(peer, ()))
                if item != connection_id
            ]
            if len(onward) != 1:
                break
            connection_id = onward[0]
            cursor = peer
        return tuple(pieces), tuple(pipes)

    def stretch_from(self, ref: PortRef) -> frozenset[str]:
        """Le tubazioni del tratto che parte da quell'attacco: la sua identita'.

        Due attacchi affacciati sullo stesso tratto danno lo stesso insieme,
        percorso dai due capi: e' cosi' che due proposte dello stesso organo
        sullo stesso volume si riconoscono come una."""
        _, pipes = self.along(ref)
        return frozenset(pipes)

    def group_holds(self, ref: PortRef, function: str) -> bool:
        """Il gruppo di quell'attacco e' gia' chiuso da quel lato.

        Vero se sul tratto c'e' gia' un pezzo con quella funzione, oppure se il
        tratto finisce su un membro dello stesso gruppo: fra i due non ci va
        nessun organo, e il volume lo chiudono gli organi ai bordi del gruppo.
        """
        pieces, _ = self.along(ref)
        if any(function in self.functions.get(item, frozenset()) for item in pieces):
            return True
        return bool(pieces) and self.same_group(ref.component_id, pieces[-1])

    def connected_ports(self, component_id: str) -> tuple[PortDefinition, ...]:
        """Gli attacchi **del flusso** che una connessione tocca davvero.

        Un accessorio non si posa su un attacco libero: non c'e' tubazione su cui
        stare, e il modello non contiene coordinate con cui inventarne una.

        Gli attacchi di servizio restano fuori. Sono lo stacco di **un altro**
        accessorio, non un pezzo del percorso: senza questa esclusione la regola
        dell'intercettazione, appena lo scarico di un volano veniva collegato,
        pretendeva una valvola anche sul suo stacco — e uno scarico e' gia' un
        rubinetto.
        """
        return tuple(
            port
            for port in self.ports.get(component_id, ())
            if not port.is_service
            and (component_id, port.id) in self.connection_of_port
        )


def endpoint_refs(connection: ConnectionModel) -> tuple[PortRef, PortRef]:
    return connection.endpoint_a, connection.endpoint_b


__all__ = ["RuleContext", "endpoint_refs"]
