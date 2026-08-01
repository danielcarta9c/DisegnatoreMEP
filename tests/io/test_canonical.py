from datetime import date
from pathlib import Path

from disegnatore_mep.io.canonical import canonical_json, project_fingerprint
from disegnatore_mep.io.project_json import dump_project, load_project
from disegnatore_mep.model.project import (
    ComponentInstance,
    NetworkModel,
    ProjectMetadata,
    ProjectModel,
)
from disegnatore_mep.model.types import Domain


def project(component_order: list[str]) -> ProjectModel:
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
            ComponentInstance(id=item, definition_id="boundary") for item in component_order
        ],
    )


def test_round_trip(tmp_path: Path) -> None:
    source = project(["b", "a"])
    path = tmp_path / "project.json"
    dump_project(source, path)
    assert load_project(path) == source


def test_fingerprint_ignores_collection_order() -> None:
    first = project(["a", "b"])
    second = project(["b", "a"])
    assert canonical_json(first) == canonical_json(second)
    assert project_fingerprint(first) == project_fingerprint(second)
