from datetime import date

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import (
    ComponentDefinition,
    PortDefinition,
    SymbolGeometry,
)
from disegnatore_mep.domains.builtin import BasicDomainPack
from disegnatore_mep.domains.registry import DomainRegistry
from disegnatore_mep.model.project import (
    ComponentInstance,
    ConnectionModel,
    NetworkModel,
    PortRef,
    ProjectMetadata,
    ProjectModel,
    SubsystemModel,
)
from disegnatore_mep.model.types import Domain, PortFlow
from disegnatore_mep.validation.topology import validate_project


def component_definition(component_id: str, flow: PortFlow) -> ComponentDefinition:
    return ComponentDefinition(
        id=component_id,
        version="1.0.0",
        name=component_id,
        functions=["boundary"],
        symbol_id=component_id,
        composite=False,
        geometry=SymbolGeometry(
            width_mm=10,
            height_mm=10,
            clearance_mm=2,
            allowed_rotations_deg=[0],
        ),
        ports=[
            PortDefinition(
                id="port",
                domain=Domain.HYDRONIC,
                medium="heating_water",
                flow=flow,
                x_mm=5,
                y_mm=5,
                angle_deg=0,
            )
        ],
        sources=["CONV-001"],
    )


def project() -> ProjectModel:
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="demo",
            client="Nove C",
            project_name="Demo",
            commission_code="MI-001",
            revision="00",
            issue_date=date(2026, 8, 1),
        ),
        networks=[
            NetworkModel(
                id="heating",
                name="Riscaldamento",
                domain=Domain.HYDRONIC,
                medium="heating_water",
            )
        ],
        components=[
            ComponentInstance(id="source", definition_id="source-def"),
            ComponentInstance(id="sink", definition_id="sink-def"),
        ],
        connections=[
            ConnectionModel(
                id="pipe-1",
                network_id="heating",
                endpoint_a=PortRef(component_id="source", port_id="port"),
                endpoint_b=PortRef(component_id="sink", port_id="port"),
            )
        ],
    )


def test_valid_project_has_no_issues() -> None:
    catalog = ComponentRegistry(
        [
            component_definition("source-def", PortFlow.OUT),
            component_definition("sink-def", PortFlow.IN),
        ]
    )
    report = validate_project(project(), catalog)
    assert report.ok is True
    assert report.issues == []


def test_unknown_definition_is_blocking() -> None:
    catalog = ComponentRegistry([component_definition("source-def", PortFlow.OUT)])
    report = validate_project(project(), catalog)
    assert report.ok is False
    assert "UNKNOWN_COMPONENT_DEFINITION" in {issue.code for issue in report.issues}


def test_required_unconnected_port_is_blocking() -> None:
    disconnected = project().model_copy(update={"connections": []})
    catalog = ComponentRegistry(
        [
            component_definition("source-def", PortFlow.OUT),
            component_definition("sink-def", PortFlow.IN),
        ]
    )
    report = validate_project(disconnected, catalog)
    assert report.ok is False
    assert [issue.code for issue in report.issues].count("REQUIRED_PORT_UNCONNECTED") == 2


def test_unknown_subsystem_member_is_blocking() -> None:
    invalid = project().model_copy(
        update={
            "subsystems": [
                SubsystemModel(
                    id="plant",
                    name="Centrale",
                    component_ids=["missing-component"],
                )
            ]
        }
    )
    catalog = ComponentRegistry(
        [
            component_definition("source-def", PortFlow.OUT),
            component_definition("sink-def", PortFlow.IN),
        ]
    )
    report = validate_project(invalid, catalog)
    assert "UNKNOWN_SUBSYSTEM_COMPONENT" in {issue.code for issue in report.issues}


def test_duplicate_connection_is_blocking() -> None:
    base = project()
    duplicate = base.connections[0].model_copy(update={"id": "pipe-2"})
    invalid = base.model_copy(update={"connections": [base.connections[0], duplicate]})
    catalog = ComponentRegistry(
        [
            component_definition("source-def", PortFlow.OUT),
            component_definition("sink-def", PortFlow.IN),
        ]
    )
    report = validate_project(invalid, catalog)
    assert "DUPLICATE_CONNECTION" in {issue.code for issue in report.issues}


def test_domain_pack_faults_on_shared_definition_are_not_deduplicated() -> None:
    # Domain packs only ever see PortDefinition/NetworkModel, so two components
    # sharing a single catalog definition produce byte-identical pack diagnostics
    # unless the core prefixes the connection id before deduplicating. This test
    # exercises the public `domains=` seam directly.
    shared_definition = component_definition("shared-def", PortFlow.OUT)
    catalog = ComponentRegistry([shared_definition])
    domain_registry = DomainRegistry([BasicDomainPack(Domain.HYDRONIC)])
    faulty = project().model_copy(
        update={
            "components": [
                ComponentInstance(id="c1", definition_id="shared-def"),
                ComponentInstance(id="c2", definition_id="shared-def"),
                ComponentInstance(id="c3", definition_id="shared-def"),
                ComponentInstance(id="c4", definition_id="shared-def"),
            ],
            "connections": [
                ConnectionModel(
                    id="conn-1",
                    network_id="heating",
                    endpoint_a=PortRef(component_id="c1", port_id="port"),
                    endpoint_b=PortRef(component_id="c2", port_id="port"),
                ),
                ConnectionModel(
                    id="conn-2",
                    network_id="heating",
                    endpoint_a=PortRef(component_id="c3", port_id="port"),
                    endpoint_b=PortRef(component_id="c4", port_id="port"),
                ),
            ],
        }
    )
    report = validate_project(faulty, catalog, domains=domain_registry)
    mismatches = [issue for issue in report.issues if issue.code == "PORT_FLOW_MISMATCH"]
    assert len(mismatches) == 2
    connection_ids = {issue.entity_ids[0] for issue in mismatches}
    assert connection_ids == {"conn-1", "conn-2"}


def test_bad_endpoint_does_not_falsely_flag_valid_neighbour() -> None:
    catalog = ComponentRegistry(
        [
            component_definition("source-def", PortFlow.OUT),
            component_definition("sink-def", PortFlow.IN),
        ]
    )
    broken = project().model_copy(
        update={
            "connections": [
                ConnectionModel(
                    id="pipe-1",
                    network_id="heating",
                    endpoint_a=PortRef(component_id="source", port_id="port"),
                    endpoint_b=PortRef(component_id="sink", port_id="missing-port"),
                )
            ]
        }
    )
    report = validate_project(broken, catalog)
    codes = [issue.code for issue in report.issues]
    assert "UNKNOWN_PORT" in codes
    for issue in report.issues:
        if issue.code == "REQUIRED_PORT_UNCONNECTED":
            assert "source" not in issue.entity_ids


def test_unknown_network_still_surfaces_endpoint_faults() -> None:
    catalog = ComponentRegistry(
        [
            component_definition("source-def", PortFlow.OUT),
            component_definition("sink-def", PortFlow.IN),
        ]
    )
    broken = project().model_copy(
        update={
            "connections": [
                ConnectionModel(
                    id="pipe-1",
                    network_id="missing-network",
                    endpoint_a=PortRef(component_id="source", port_id="port"),
                    endpoint_b=PortRef(component_id="sink", port_id="missing-port"),
                )
            ]
        }
    )
    report = validate_project(broken, catalog)
    codes = {issue.code for issue in report.issues}
    assert "UNKNOWN_NETWORK" in codes
    assert "UNKNOWN_PORT" in codes


def test_duplicate_connection_names_both_ids_and_is_order_invariant() -> None:
    catalog = ComponentRegistry(
        [
            component_definition("source-def", PortFlow.OUT),
            component_definition("sink-def", PortFlow.IN),
        ]
    )
    base = project()
    duplicate = base.connections[0].model_copy(update={"id": "pipe-2"})
    forward = base.model_copy(update={"connections": [base.connections[0], duplicate]})
    backward = base.model_copy(update={"connections": [duplicate, base.connections[0]]})

    report_forward = validate_project(forward, catalog)
    report_backward = validate_project(backward, catalog)

    assert report_forward == report_backward

    duplicate_issues = [issue for issue in report_forward.issues if issue.code == "DUPLICATE_CONNECTION"]
    assert len(duplicate_issues) == 1
    message = duplicate_issues[0].message
    assert "pipe-1" in message
    assert "pipe-2" in message
    assert duplicate_issues[0].entity_ids == sorted(["pipe-1", "pipe-2"])


def test_port_connection_limit_is_blocking() -> None:
    catalog = ComponentRegistry(
        [
            component_definition("source-def", PortFlow.OUT),
            component_definition("hub-def", PortFlow.IN),
        ]
    )
    hub_project = ProjectModel(
        metadata=ProjectMetadata(
            project_id="demo",
            client="Nove C",
            project_name="Demo",
            commission_code="MI-001",
            revision="00",
            issue_date=date(2026, 8, 1),
        ),
        networks=[
            NetworkModel(
                id="heating",
                name="Riscaldamento",
                domain=Domain.HYDRONIC,
                medium="heating_water",
            )
        ],
        components=[
            ComponentInstance(id="src1", definition_id="source-def"),
            ComponentInstance(id="src2", definition_id="source-def"),
            ComponentInstance(id="hub", definition_id="hub-def"),
        ],
        connections=[
            ConnectionModel(
                id="conn-1",
                network_id="heating",
                endpoint_a=PortRef(component_id="src1", port_id="port"),
                endpoint_b=PortRef(component_id="hub", port_id="port"),
            ),
            ConnectionModel(
                id="conn-2",
                network_id="heating",
                endpoint_a=PortRef(component_id="src2", port_id="port"),
                endpoint_b=PortRef(component_id="hub", port_id="port"),
            ),
        ],
    )
    report = validate_project(hub_project, catalog)
    limit_issues = [issue for issue in report.issues if issue.code == "PORT_CONNECTION_LIMIT"]
    assert len(limit_issues) == 1
    assert limit_issues[0].entity_ids == ["hub", "port"]
    assert "2 connections" in limit_issues[0].message
    assert "maximum is 1" in limit_issues[0].message


def test_unknown_component_message_includes_id() -> None:
    catalog = ComponentRegistry(
        [
            component_definition("source-def", PortFlow.OUT),
            component_definition("sink-def", PortFlow.IN),
        ]
    )
    broken = project().model_copy(
        update={
            "connections": [
                ConnectionModel(
                    id="pipe-1",
                    network_id="heating",
                    endpoint_a=PortRef(component_id="missing-component", port_id="port"),
                    endpoint_b=PortRef(component_id="sink", port_id="port"),
                )
            ]
        }
    )
    report = validate_project(broken, catalog)
    unknown_component_issues = [issue for issue in report.issues if issue.code == "UNKNOWN_COMPONENT"]
    assert len(unknown_component_issues) == 1
    assert unknown_component_issues[0].message == "unknown component missing-component"
    assert unknown_component_issues[0].entity_ids == ["missing-component"]
