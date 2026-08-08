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
from dataclasses import dataclass, field

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import (
    SHUTOFF_REGIMES,
    ComponentTrait,
    PortDefinition,
)
from disegnatore_mep.model.project import ConnectionModel, PortRef, ProjectModel


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

    members: dict[str, tuple[str, ...]] = field(default_factory=dict)
    """Componenti di ciascuna rete, in ordine di modello."""

    @classmethod
    def build(cls, project: ProjectModel, catalog: ComponentRegistry) -> "RuleContext":
        functions: dict[str, frozenset[str]] = {}
        traits: dict[str, frozenset[ComponentTrait]] = {}
        carried: dict[str, frozenset[str]] = {}
        stored_media: dict[str, str] = {}
        fill_ports: dict[str, str] = {}
        ports: dict[str, tuple[PortDefinition, ...]] = {}
        inline: set[str] = set()
        service_ports: dict[tuple[str, str], str] = {}
        for component in project.components:
            resolved = catalog.resolve(component.definition_id)
            functions[component.id] = frozenset(resolved.definition.functions)
            traits[component.id] = resolved.definition.trait_set
            carried[component.id] = frozenset(resolved.definition.carries_on_board)
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
            # In ordine di nome, mai nell'ordine in cui il file elenca le
            # tubazioni: una regola che serve «il primo» della rete deve
            # servire lo stesso pezzo comunque l'impianto sia stato scritto.
            # Il collaudo ha visto il gruppo di riempimento migrare da una
            # pompa di calore all'altra permutando il file: si chiude qui.
            members={key: tuple(sorted(value)) for key, value in members.items()},
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
        self,
        connection_id: str,
        *,
        upstream: bool,
        network_id: str,
        without: frozenset[str] = frozenset(),
    ) -> tuple[str, ...]:
        """Tutte le tubazioni da cui questa puo' essere alimentata, in ordine.

        Risalendo il fluido (`upstream`) si va verso chi lo manda; seguendolo
        si va verso chi lo riceve. La camminata attraversa raccordi e accessori
        in linea e **si apre sui rami**: dove due tubazioni confluiscono, si
        risalgono tutte e due, perche' l'acqua di questo ritorno puo' venire
        da entrambe. Si ferma su cio' che non e' in linea — una macchina, un
        serbatoio — e dove non c'e' piu' niente.

        L'ordine e' quello della scoperta, dal piu' vicino al piu' lontano.
        **Serve a dire quali tubazioni stanno dal lato giusto** — sul ritorno
        per una regola del ritorno, sulla mandata per una della mandata — non
        a scegliere il tratto comune: quale sia il tratto comune lo decide
        `carries_all_the_water_of`, che guarda la struttura e non l'ordine di
        scoperta. Prima lo decideva questa camminata, prendendo la prima
        tubazione condivisa da tutte le risalite, e su un anello «la prima che
        incontro» dipendeva da quale macchina partiva per prima.

        `without` toglie tubazioni dal percorso: serve a misurare quanta rete
        resta fra le macchine e un tratto candidato, cioe' a scegliere quello
        piu' vicino.
        """
        if connection_id not in self.pipe_ends or connection_id in without:
            return ()
        chain = [connection_id]
        seen = {connection_id}
        frontier = [connection_id]
        while frontier:
            current = frontier.pop(0)
            leaves, enters = self.pipe_ends[current]
            component_id = (leaves if upstream else enters).component_id
            if component_id not in self.inline:
                continue
            for item in sorted(
                (self.incoming if upstream else self.outgoing).get(component_id, ())
            ):
                if (
                    item in seen
                    or item in without
                    or self.network_of_connection.get(item) != network_id
                ):
                    continue
                seen.add(item)
                chain.append(item)
                frontier.append(item)
        return tuple(chain)

    def carries_all_the_water_of(
        self, connection_id: str, *, network_id: str, component_ids: tuple[str, ...]
    ) -> bool:
        """Se per quella tubazione passa **tutta** l'acqua di quelle macchine.

        E' la proprieta' che la regola del defangatore dichiara per iscritto —
        «li' passa tutta l'acqua che torna, quindi un pezzo solo protegge ogni
        generatore» — presa alla lettera e resa misurabile: si toglie la
        tubazione e si guarda se il circuito di ciascuna macchina **si chiude
        ancora**. Se si chiude, quell'acqua per di li' non passava.

        Il giro si fa **attraversando anche le macchine**, perche' l'acqua ci
        passa dentro: fermarsi sulle macchine e' comodo per camminare, non e'
        vero per l'acqua.

        Sostituisce il vecchio criterio — «da questo tratto si risale a tutti i
        generatori» — che non e' la stessa cosa e su due grafi su sette dava
        una risposta diversa: un ramo che rientra **a valle** e' risalibile da
        entrambe le macchine e non porta l'acqua di nessuna delle due.
        """
        pipes = {
            pipe
            for pipe, network in self.network_of_connection.items()
            if network == network_id and pipe in self.pipe_ends
        }
        if connection_id not in pipes:
            return False
        onward = {
            pipe: [
                item
                for item in self.outgoing.get(self.pipe_ends[pipe][1].component_id, ())
                if item in pipes
            ]
            for pipe in pipes
        }
        for component_id in component_ids:
            leaving = [
                pipe
                for pipe in pipes
                if self.pipe_ends[pipe][0].component_id == component_id
            ]
            arriving = {
                pipe
                for pipe in pipes
                if self.pipe_ends[pipe][1].component_id == component_id
            }
            if not leaving or not arriving:
                # Una macchina che su questa rete non ha sia una partenza sia
                # un arrivo non ha un circuito da tagliare, e non ha voce.
                continue
            seen: set[str] = set()
            stack = [pipe for pipe in leaving if pipe != connection_id]
            while stack:
                current = stack.pop()
                if current in seen:
                    continue
                seen.add(current)
                stack.extend(
                    item
                    for item in onward[current]
                    if item != connection_id and item not in seen
                )
            if seen & arriving:
                return False
        return True

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
        for candidate, holder in self.connection_of_port.items():
            if holder == connection_id and candidate[0] != component_id:
                return candidate[0]
        return None

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
