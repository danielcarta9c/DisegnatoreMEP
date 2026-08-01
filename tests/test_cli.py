import json
from pathlib import Path

from _pytest.capture import CaptureFixture

from disegnatore_mep.cli import main
from disegnatore_mep.model.project import ProjectModel


def test_export_schema(tmp_path: Path) -> None:
    output = tmp_path / "schema.json"
    exit_code = main(["export-schema", str(output)])
    assert exit_code == 0
    schema = json.loads(output.read_text(encoding="utf-8"))
    assert schema["title"] == "ProjectModel"


def test_fingerprint(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    project = ProjectModel.model_validate(
        {
            "metadata": {
                "project_id": "demo",
                "client": "Nove C",
                "project_name": "Demo",
                "commission_code": "MI-001",
                "revision": "00",
                "issue_date": "2026-08-01",
            }
        }
    )
    path = tmp_path / "project.json"
    path.write_text(project.model_dump_json(), encoding="utf-8")
    exit_code = main(["fingerprint", str(path)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert len(captured.out.strip()) == 64


def test_validate_load_error_returns_one(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    assert main(["validate", str(missing), "--catalog", str(catalog)]) == 1
