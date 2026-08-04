import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from disegnatore_mep.io.canonical import project_fingerprint
from disegnatore_mep.io.project_json import (
    SCHEMA_VERSION,
    SUPPORTED_SCHEMA_VERSIONS,
    load_project,
    migrate_project_document,
)
from disegnatore_mep.model.project import ProjectModel

METADATA = {
    "project_id": "migration",
    "client": "Nove C",
    "project_name": "Migrazione",
    "commission_code": "DEV-001",
    "revision": "00",
    "issue_date": "2026-08-04",
}


def document(version: str, **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": version,
        "metadata": METADATA,
        "subsystems": [{"id": "plant", "name": "Centrale"}],
        "sheets": [{"id": "t1", "title": "Centrale", "subsystem_ids": ["plant"]}],
    }
    payload.update(overrides)
    return payload


def test_the_build_writes_one_version_and_reads_more_than_one() -> None:
    assert SCHEMA_VERSION == "1.1.0"
    assert SCHEMA_VERSION in SUPPORTED_SCHEMA_VERSIONS
    assert "1.0.0" in SUPPORTED_SCHEMA_VERSIONS


def test_a_one_zero_document_is_lifted_and_gains_empty_band_assignments() -> None:
    migrated = migrate_project_document(document("1.0.0"))
    assert migrated["schema_version"] == SCHEMA_VERSION
    sheets = migrated["sheets"]
    assert isinstance(sheets, list)
    assert sheets[0]["band_assignments"] == []


def test_a_current_document_passes_through_unchanged() -> None:
    current = document(SCHEMA_VERSION)
    sheets = current["sheets"]
    assert isinstance(sheets, list)
    sheets[0]["band_assignments"] = [
        {"subsystem_id": "plant", "band": "generation", "order": 0}
    ]
    assert migrate_project_document(current) == current


def test_migration_is_idempotent() -> None:
    once = migrate_project_document(document("1.0.0"))
    assert migrate_project_document(dict(once)) == once


def test_an_unknown_version_is_refused_naming_what_is_supported() -> None:
    with pytest.raises(ValueError, match="unsupported schema version 2.0.0"):
        migrate_project_document(document("2.0.0"))


def test_a_missing_version_is_refused_instead_of_guessed() -> None:
    payload = document("1.0.0")
    del payload["schema_version"]
    with pytest.raises(ValueError, match="no schema_version"):
        migrate_project_document(payload)


def test_the_model_itself_speaks_only_the_current_version() -> None:
    """La migrazione avviene al confine: in memoria esiste una sola versione."""
    with pytest.raises(ValidationError):
        ProjectModel.model_validate(document("1.0.0"))


def test_a_migrated_document_and_a_native_one_have_the_same_fingerprint(
    tmp_path: Path,
) -> None:
    """La prova che conta: la migrazione non cambia il significato del progetto."""
    old = tmp_path / "old.json"
    new = tmp_path / "new.json"
    old.write_text(json.dumps(document("1.0.0")), encoding="utf-8")
    native = document(SCHEMA_VERSION)
    sheets = native["sheets"]
    assert isinstance(sheets, list)
    sheets[0]["band_assignments"] = []
    new.write_text(json.dumps(native), encoding="utf-8")
    assert project_fingerprint(load_project(old)) == project_fingerprint(load_project(new))


def test_loading_a_one_zero_file_from_disk_still_works(tmp_path: Path) -> None:
    path = tmp_path / "legacy.json"
    path.write_text(json.dumps(document("1.0.0")), encoding="utf-8")
    assert load_project(path).schema_version == SCHEMA_VERSION
