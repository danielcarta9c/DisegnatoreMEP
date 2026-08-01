from datetime import date

import pytest
from pydantic import ValidationError

from disegnatore_mep.model.project import (
    ComponentInstance,
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
            unsupported="value",
        )


def test_project_schema_version_is_fixed() -> None:
    project = ProjectModel(metadata=metadata())
    assert project.schema_version == "1.0.0"
