"""La vista che una condizione puo' interrogare, e nulla di piu'.

E' qui che il vincolo «una regola non puo' nominare un componente» smette di
essere un'intenzione e diventa una proprieta': chi valuta una condizione riceve
questo oggetto, che risponde per **funzione**, per dominio e per fluido, e non
espone il modello. Gli identificativi escono solo dalla parte che costruisce la
proposta, che deve pur dire su cosa si ancora.
"""

from collections import defaultdict
from dataclasses import dataclass, field

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import PortDefinition
from disegnatore_mep.model.project import ConnectionModel, PortRef, ProjectModel


@dataclass(frozen=True)
class RuleContext:
    """Indici pronti su modello e catalogo. Costruita una volta per valutazione."""

    functions: dict[str, frozenset[str]]
    """Funzioni di catalogo di ciascun componente."""

    ports: dict[str, tuple[PortDefinition, ...]]
    networks_of: dict[str, frozenset[str]]
    """Reti che ciascun componente tocca."""

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
        ports: dict[str, tuple[PortDefinition, ...]] = {}
        inline: set[str] = set()
        for component in project.components:
            resolved = catalog.resolve(component.definition_id)
            functions[component.id] = frozenset(resolved.definition.functions)
            ports[component.id] = tuple(resolved.definition.ports)
            if resolved.is_inline:
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
            ports=ports,
            networks_of={key: frozenset(value) for key, value in touched.items()},
            connection_of_port=connection_of_port,
            network_of_connection=network_of_connection,
            inline=frozenset(inline),
            members={key: tuple(value) for key, value in members.items()},
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
        """Solo gli attacchi che una connessione tocca davvero.

        Un accessorio non si posa su un attacco libero: non c'e' tubazione su cui
        stare, e il modello non contiene coordinate con cui inventarne una.
        """
        return tuple(
            port
            for port in self.ports.get(component_id, ())
            if (component_id, port.id) in self.connection_of_port
        )


def endpoint_refs(connection: ConnectionModel) -> tuple[PortRef, PortRef]:
    return connection.endpoint_a, connection.endpoint_b


__all__ = ["RuleContext", "endpoint_refs"]
