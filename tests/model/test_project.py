from datetime import date

import pytest
from pydantic import ValidationError

from disegnatore_mep.model.project import (
    ComponentInstance,
    ConnectionModel,
    PortRef,
    ProjectMetadata,
    ProjectModel,
)


def metadata() -> ProjectMetadata:
    return ProjectMetadata(
        project_id="demo",
        client="Nove C",
        project_name="Impianto dimostrativo",
        commission_code="MI-001",
        revision="00",
        issue_date=date(2026, 8, 1),
    )


def test_project_rejects_duplicate_component_ids() -> None:
    component = ComponentInstance(
        id="boiler-1",
        definition_id="gas-boiler",
        tag="CAL-01",
    )
    with pytest.raises(ValidationError, match="duplicate component id: boiler-1"):
        ProjectModel(metadata=metadata(), components=[component, component])


def test_project_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ProjectMetadata(
            project_id="demo",
            client="Nove C",
            project_name="Impianto dimostrativo",
            commission_code="MI-001",
            revision="00",
            issue_date=date(2026, 8, 1),
            unsupported="value",  # type: ignore[call-arg]
        )


def test_project_schema_version_is_fixed() -> None:
    project = ProjectModel(metadata=metadata())
    assert project.schema_version == "1.0.0"


@pytest.mark.parametrize(
    "invalid_id",
    ["Boiler", "1boiler", "", "a b", "boiler-1\n", "-boiler", "boiler.1"],
)
def test_identifier_pattern_rejects_invalid_ids(invalid_id: str) -> None:
    with pytest.raises(ValidationError):
        ComponentInstance(id=invalid_id, definition_id="gas-boiler")


def test_connection_rejects_identical_endpoints() -> None:
    endpoint = PortRef(component_id="boiler-1", port_id="water-supply")
    with pytest.raises(ValidationError, match="connection endpoints must differ"):
        ConnectionModel(
            id="pipe-1",
            network_id="heating",
            endpoint_a=endpoint,
            endpoint_b=endpoint,
        )


def test_project_rejects_duplicate_component_tags() -> None:
    first = ComponentInstance(id="boiler-1", definition_id="gas-boiler", tag="CAL-01")
    second = ComponentInstance(id="boiler-2", definition_id="gas-boiler", tag="CAL-01")
    with pytest.raises(ValidationError, match="duplicate component tag: CAL-01"):
        ProjectModel(metadata=metadata(), components=[first, second])
