import pytest
from pydantic import ValidationError

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.model.project import ProjectModel, SheetIntentModel
from disegnatore_mep.model.types import BandRole
from disegnatore_mep.validation.topology import validate_project

METADATA = {
    "project_id": "pagination",
    "client": "Nove C",
    "project_name": "Piano di impaginazione",
    "commission_code": "DEV-001",
    "revision": "00",
    "issue_date": "2026-08-04",
}


def sheet(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": "t1",
        "title": "Centrale",
        "subsystem_ids": ["plant"],
        "band_assignments": [
            {"subsystem_id": "plant", "band": "generation", "order": 0}
        ],
    }
    payload.update(overrides)
    return payload


def project(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "metadata": METADATA,
        "subsystems": [{"id": "plant", "name": "Centrale"}],
        "sheets": [sheet()],
    }
    payload.update(overrides)
    return payload


def test_a_sheet_carries_its_band_assignments() -> None:
    model = ProjectModel.model_validate(project())
    assignment = model.sheets[0].band_assignments[0]
    assert assignment.band is BandRole.GENERATION
    assert assignment.subsystem_id == "plant"


def test_bands_read_left_to_right() -> None:
    order = [role.reading_order for role in BandRole]
    assert order == sorted(order)
    assert BandRole.GENERATION.reading_order < BandRole.TERMINAL.reading_order


def test_a_subsystem_cannot_be_assigned_twice_on_one_sheet() -> None:
    with pytest.raises(ValidationError, match="assigned to more than one band"):
        SheetIntentModel.model_validate(
            sheet(
                band_assignments=[
                    {"subsystem_id": "plant", "band": "generation", "order": 0},
                    {"subsystem_id": "plant", "band": "distribution", "order": 1},
                ]
            )
        )


def test_a_band_cannot_assign_a_subsystem_the_sheet_does_not_carry() -> None:
    with pytest.raises(ValidationError, match="not listed on sheet"):
        SheetIntentModel.model_validate(
            sheet(
                band_assignments=[
                    {"subsystem_id": "zones", "band": "terminal", "order": 0}
                ]
            )
        )


def test_an_unknown_band_is_rejected() -> None:
    with pytest.raises(ValidationError):
        SheetIntentModel.model_validate(
            sheet(band_assignments=[{"subsystem_id": "plant", "band": "middle", "order": 0}])
        )


def test_a_negative_order_is_rejected() -> None:
    with pytest.raises(ValidationError):
        SheetIntentModel.model_validate(
            sheet(
                band_assignments=[
                    {"subsystem_id": "plant", "band": "generation", "order": -1}
                ]
            )
        )


def empty_catalog() -> ComponentRegistry:
    return ComponentRegistry([])


def test_the_validator_reports_a_band_pointing_at_a_missing_subsystem() -> None:
    model = ProjectModel.model_validate(
        project(
            subsystems=[{"id": "plant", "name": "Centrale"}, {"id": "zones", "name": "Zone"}],
            sheets=[
                sheet(
                    subsystem_ids=["plant", "zones"],
                    band_assignments=[
                        {"subsystem_id": "plant", "band": "generation", "order": 0},
                        {"subsystem_id": "zones", "band": "terminal", "order": 0},
                    ],
                )
            ],
        )
    )
    model.subsystems = [item for item in model.subsystems if item.id == "plant"]
    report = validate_project(model, empty_catalog())
    assert "UNKNOWN_BAND_SUBSYSTEM" in {issue.code for issue in report.issues}


def test_the_validator_reports_a_subsystem_no_band_collects() -> None:
    """Un sottosistema che non finisce su nessuna fascia sparisce dal disegno:
    un'omissione silenziosa e' peggio di un errore visibile."""
    model = ProjectModel.model_validate(
        project(
            subsystems=[{"id": "plant", "name": "Centrale"}, {"id": "zones", "name": "Zone"}],
            sheets=[sheet(subsystem_ids=["plant", "zones"])],
        )
    )
    report = validate_project(model, empty_catalog())
    issues = {issue.code: issue for issue in report.issues}
    assert "UNASSIGNED_SUBSYSTEM" in issues
    assert "zones" in issues["UNASSIGNED_SUBSYSTEM"].entity_ids


def test_a_fully_assigned_sheet_validates_clean() -> None:
    model = ProjectModel.model_validate(project())
    report = validate_project(model, empty_catalog())
    assert report.ok


def test_a_project_without_sheets_stays_valid() -> None:
    """La partizione e' facoltativa (D-020): un impianto semplice sta su una
    sola tavola e non dichiara nulla."""
    model = ProjectModel.model_validate(
        {"metadata": METADATA, "subsystems": [{"id": "plant", "name": "Centrale"}]}
    )
    assert validate_project(model, empty_catalog()).ok
