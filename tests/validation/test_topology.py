from datetime import date

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import (
    ComponentDefinition,
    PortDefinition,
    SymbolGeometry,
)
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
