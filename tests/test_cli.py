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


ROOT = Path(__file__).resolve().parents[1]
ESSENTIAL = ROOT / "examples" / "rules" / "centrale-pdc-essenziale.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"
NAMING = ROOT / "naming"


def test_rules_prints_what_the_catalogue_cannot_offer(
    tmp_path: Path, capsys: CaptureFixture[str]
) -> None:
    """Il difetto per cui P2 e' stato respinto, sul comando che l'ingegnere usa.

    Si toglie dal catalogo lo scarico sanitario e si chiede l'elenco delle
    integrazioni: il bollitore non puo' piu' svuotare la propria riserva, e la
    cosa deve **comparire**. Prima l'ancoraggio veniva scartato in silenzio e
    l'elenco sembrava completo.
    """
    thinned = tmp_path / "catalogo"
    thinned.mkdir()
    for source in sorted(CATALOG.glob("*.json")):
        if source.name == "drain-connection-dhw.json":
            continue
        (thinned / source.name).write_text(source.read_text("utf-8"), encoding="utf-8")

    exit_code = main(
        [
            "rules",
            str(ESSENTIAL),
            "--catalog",
            str(thinned),
            "--symbols",
            str(SYMBOLS),
            "--rules",
            str(RULES),
            "--naming",
            str(NAMING),
        ]
    )
    printed = capsys.readouterr().out
    assert exit_code == 0
    assert "Punti aperti" in printed
    assert "acqua calda sanitaria" in printed
    assert "Attacco di scarico" in printed


def test_rules_on_a_complete_model_says_so_and_opens_no_point(
    capsys: CaptureFixture[str],
) -> None:
    """L'altro verso: senza lacune, il messaggio di completezza dice il vero."""
    exit_code = main(
        [
            "rules",
            str(ROOT / "examples" / "rules" / "centrale-pdc-completa.json"),
            "--catalog",
            str(CATALOG),
            "--symbols",
            str(SYMBOLS),
            "--rules",
            str(RULES),
            "--naming",
            str(NAMING),
        ]
    )
    printed = capsys.readouterr().out
    assert exit_code == 0
    assert "Punti aperti" not in printed
    assert "il modello e' gia' completo" in printed
