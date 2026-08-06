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

    stored_media: dict[str, str]
    """Il fluido che ciascun componente tiene in serbo, per chi ne tiene uno."""

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
    inline: frozenset[str] = frozenset()
    """Chi sta **su** una tubazione invece di essere un nodo del disegno."""

    members: dict[str, tuple[str, ...]] = field(default_factory=dict)
    """Componenti di ciascuna rete, in ordine di modello."""

    @classmethod
    def build(cls, project: ProjectModel, catalog: ComponentRegistry) -> "RuleContext":
        functions: dict[str, frozenset[str]] = {}
        traits: dict[str, frozenset[ComponentTrait]] = {}
        stored_media: dict[str, str] = {}
        ports: dict[str, tuple[PortDefinition, ...]] = {}
        inline: set[str] = set()
        service_ports: dict[tuple[str, str], str] = {}
        for component in project.components:
            resolved = catalog.resolve(component.definition_id)
            functions[component.id] = frozenset(resolved.definition.functions)
            traits[component.id] = resolved.definition.trait_set
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
        for connection in project.connections:
            network_of_connection[connection.id] = connection.network_id
            for ref in (connection.endpoint_a, connection.endpoint_b):
                touched[ref.component_id].add(connection.network_id)
                connection_of_port[(ref.component_id, ref.port_id)] = connection.id
                if ref.component_id not in members[connection.network_id]:
                    members[connection.network_id].append(ref.component_id)

        return cls(
            functions=functions,
            traits=traits,
            stored_media=stored_media,
            ports=ports,
            networks_of={key: frozenset(value) for key, value in touched.items()},
            service_ports=service_ports,
            connection_of_port=connection_of_port,
            network_of_connection=network_of_connection,
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
        return any(
            function in self.functions.get(component_id, frozenset())
            for component_id in self.members.get(network_id, ())
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
            connection_id = self._other_connection(peer, connection_id)
            cursor = peer
        return False

    def _peer(self, connection_id: str, component_id: str) -> str | None:
        for candidate, holder in self.connection_of_port.items():
            if holder == connection_id and candidate[0] != component_id:
                return candidate[0]
        return None

    def _other_connection(self, component_id: str, connection_id: str) -> str | None:
        return next(
            (
                holder
                for (owner, _), holder in self.connection_of_port.items()
                if owner == component_id and holder != connection_id
            ),
            None,
        )

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
