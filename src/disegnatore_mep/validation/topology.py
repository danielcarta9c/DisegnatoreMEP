from collections import Counter

from disegnatore_mep.catalog.registry import CatalogError, ComponentRegistry
from disegnatore_mep.catalog.schema import PortDefinition
from disegnatore_mep.domains.registry import DomainRegistry, default_domain_registry
from disegnatore_mep.model.project import ComponentInstance, PortRef, ProjectModel
from disegnatore_mep.model.types import IssueSeverity

from .issues import ValidationIssue, ValidationReport


def _issue(code: str, message: str, entity_ids: list[str]) -> ValidationIssue:
    return ValidationIssue(
        code=code,
        severity=IssueSeverity.BLOCKING,
        message=message,
        entity_ids=entity_ids,
    )


def _resolve_port(
    ref: PortRef,
    components: dict[str, ComponentInstance],
    catalog: ComponentRegistry,
    connection_id: str,
) -> tuple[PortDefinition | None, list[ValidationIssue]]:
    component = components.get(ref.component_id)
    if component is None:
        return None, [
            _issue(
                "UNKNOWN_COMPONENT",
                f"connection {connection_id}: unknown component {ref.component_id}",
                [connection_id, ref.component_id],
            )
        ]
    try:
        definition = catalog.get(component.definition_id)
    except CatalogError:
        return None, [
            _issue(
                "UNKNOWN_COMPONENT_DEFINITION",
                f"connection {connection_id}: unknown definition {component.definition_id}",
                [connection_id, component.id, component.definition_id],
            )
        ]
    port = next((item for item in definition.ports if item.id == ref.port_id), None)
    if port is None:
        return None, [
            _issue(
                "UNKNOWN_PORT",
                f"connection {connection_id}: unknown port {ref.port_id}",
                [connection_id, component.id, ref.port_id],
            )
        ]
    return port, []


def validate_project(
    project: ProjectModel,
    catalog: ComponentRegistry,
    domains: DomainRegistry | None = None,
) -> ValidationReport:
    domain_registry = domains or default_domain_registry()
    components = {item.id: item for item in project.components}
    networks = {item.id: item for item in project.networks}
    subsystems = {item.id: item for item in project.subsystems}
    usage: Counter[tuple[str, str]] = Counter()
    seen_edges: dict[tuple[str, tuple[str, str], tuple[str, str]], str] = {}
    issues: list[ValidationIssue] = []

    for component in project.components:
        if not catalog.contains(component.definition_id):
            issues.append(
                _issue(
                    "UNKNOWN_COMPONENT_DEFINITION",
                    f"unknown definition {component.definition_id}",
                    [component.id, component.definition_id],
                )
            )

    for subsystem in project.subsystems:
        for component_id in subsystem.component_ids:
            if component_id not in components:
                issues.append(
                    _issue(
                        "UNKNOWN_SUBSYSTEM_COMPONENT",
                        f"unknown component {component_id} in subsystem {subsystem.id}",
                        [subsystem.id, component_id],
                    )
                )
        for network_id in subsystem.network_ids:
            if network_id not in networks:
                issues.append(
                    _issue(
                        "UNKNOWN_SUBSYSTEM_NETWORK",
                        f"unknown network {network_id} in subsystem {subsystem.id}",
                        [subsystem.id, network_id],
                    )
                )

    for sheet in project.sheets:
        for subsystem_id in sheet.subsystem_ids:
            if subsystem_id not in subsystems:
                issues.append(
                    _issue(
                        "UNKNOWN_SHEET_SUBSYSTEM",
                        f"unknown subsystem {subsystem_id} in sheet {sheet.id}",
                        [sheet.id, subsystem_id],
                    )
                )
        assigned = {item.subsystem_id for item in sheet.band_assignments}
        for assignment in sheet.band_assignments:
            if assignment.subsystem_id not in subsystems:
                issues.append(
                    _issue(
                        "UNKNOWN_BAND_SUBSYSTEM",
                        f"sheet {sheet.id} assigns unknown subsystem "
                        f"{assignment.subsystem_id} to band {assignment.band.value}",
                        [sheet.id, assignment.subsystem_id],
                    )
                )
        # Un sottosistema dichiarato sulla tavola ma raccolto da nessuna fascia
        # non verrebbe disegnato: sparirebbe in silenzio dall'elaborato, che e'
        # peggio di un errore visibile.
        for subsystem_id in sheet.subsystem_ids:
            if sheet.band_assignments and subsystem_id not in assigned:
                issues.append(
                    _issue(
                        "UNASSIGNED_SUBSYSTEM",
                        f"sheet {sheet.id} carries subsystem {subsystem_id} but no "
                        f"band collects it, so it would not be drawn",
                        [sheet.id, subsystem_id],
                    )
                )

    for connection in project.connections:
        if connection.endpoint_a.component_id == connection.endpoint_b.component_id:
            issues.append(
                _issue(
                    "SELF_LOOP_CONNECTION",
                    f"connection {connection.id} joins component "
                    f"{connection.endpoint_a.component_id} to itself",
                    [connection.id, connection.endpoint_a.component_id],
                )
            )

        endpoint_a = (connection.endpoint_a.component_id, connection.endpoint_a.port_id)
        endpoint_b = (connection.endpoint_b.component_id, connection.endpoint_b.port_id)
        first_endpoint, second_endpoint = sorted((endpoint_a, endpoint_b))
        # `network_id` stays inside the edge key: two connections between the same
        # ports on different networks are legitimately distinct connections, not
        # duplicates. Same-network multiplicity is caught separately below by
        # PORT_CONNECTION_LIMIT.
        edge_key = (connection.network_id, first_endpoint, second_endpoint)
        first_id = seen_edges.get(edge_key)
        if first_id is None:
            seen_edges[edge_key] = connection.id
        else:
            # `entity_ids` stays sorted so the report is order-invariant, but the
            # message names the true first-declared connection as the original
            # and the current (later-declared) connection as the duplicate.
            pair = sorted([connection.id, first_id])
            issues.append(
                _issue(
                    "DUPLICATE_CONNECTION",
                    f"connection {connection.id} duplicates {first_id} on network {connection.network_id}",
                    pair,
                )
            )

        port_a, errors_a = _resolve_port(connection.endpoint_a, components, catalog, connection.id)
        port_b, errors_b = _resolve_port(connection.endpoint_b, components, catalog, connection.id)
        issues.extend(errors_a)
        issues.extend(errors_b)

        if port_a is not None:
            usage[endpoint_a] += 1
        if port_b is not None:
            usage[endpoint_b] += 1

        network = networks.get(connection.network_id)
        if network is None:
            issues.append(
                _issue(
                    "UNKNOWN_NETWORK",
                    f"unknown network {connection.network_id}",
                    [connection.id, connection.network_id],
                )
            )
            continue
        if port_a is None or port_b is None:
            continue
        for issue in domain_registry.get(network.domain).validate_pair(port_a, port_b, network):
            issues.append(
                issue.model_copy(update={"entity_ids": [connection.id, *issue.entity_ids]})
            )

    for component in project.components:
        if not catalog.contains(component.definition_id):
            continue
        definition = catalog.get(component.definition_id)
        for port in definition.ports:
            count = usage[(component.id, port.id)]
            if port.required and count == 0:
                issues.append(
                    _issue(
                        "REQUIRED_PORT_UNCONNECTED",
                        f"required port {port.id} is unconnected",
                        [component.id, port.id],
                    )
                )
            if count > port.max_connections:
                issues.append(
                    _issue(
                        "PORT_CONNECTION_LIMIT",
                        f"port {port.id} has {count} connections; maximum is {port.max_connections}",
                        [component.id, port.id],
                    )
                )

    unique = {
        (item.code, tuple(item.entity_ids), item.message): item
        for item in issues
    }
    ordered = sorted(unique.values(), key=lambda item: (item.code, item.entity_ids, item.message))
    return ValidationReport(issues=ordered)
