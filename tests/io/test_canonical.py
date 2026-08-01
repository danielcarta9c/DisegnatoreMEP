from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

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


def test_fingerprint_discriminates_different_content() -> None:
    first = project(["a", "b"])
    second = project(["a", "b", "c"])
    assert canonical_json(first) != canonical_json(second)
    assert project_fingerprint(first) != project_fingerprint(second)


@pytest.mark.parametrize("bad_value", [float("inf"), float("-inf"), float("nan")])
def test_non_finite_property_is_rejected_at_the_model_boundary(bad_value: float) -> None:
    # D2(a) regression: a non-finite float can never round-trip through JSON
    # (canonical_json refuses to emit it, and dump/load would otherwise
    # silently turn it into null), so it must be rejected as soon as it
    # reaches a JsonPrimitive field rather than corrupting the canonical form
    # or the fingerprint later.
    with pytest.raises(ValidationError):
        ComponentInstance(id="c1", definition_id="boundary", properties={"x": bad_value})


def test_canonical_json_never_emits_non_finite_literals() -> None:
    # D2(b) regression: defence in depth. Even for an ordinary, fully valid
    # project, canonical_json must produce output a conformant JSON parser
    # can read - `NaN` / `Infinity` / `-Infinity` are not valid JSON tokens.
    source = project(["a", "b"])
    text = canonical_json(source)
    assert "NaN" not in text
    assert "Infinity" not in text
