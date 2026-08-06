import json
import shutil
from pathlib import Path

from _pytest.capture import CaptureFixture

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.cli import main
from disegnatore_mep.graphics.registry import SymbolRegistry

FIXTURES = Path(__file__).resolve().parents[2] / "examples" / "foundation"


def test_valid_mixed_project_passes() -> None:
    assert (
        main(
            [
                "validate",
                str(FIXTURES / "valid-mixed-project.json"),
                "--catalog",
                str(FIXTURES / "catalog"),
            ]
        )
        == 0
    )


def test_cross_medium_project_fails_with_code_two(
    capsys: CaptureFixture[str],
) -> None:
    exit_code = main(
        [
            "validate",
            str(FIXTURES / "invalid-cross-medium.json"),
            "--catalog",
            str(FIXTURES / "catalog"),
        ]
    )
    captured = capsys.readouterr()
    report = json.loads(captured.out)
    assert exit_code == 2
    assert "PORT_MEDIUM_MISMATCH" in {item["code"] for item in report["issues"]}


def broken_catalog(tmp_path: Path) -> Path:
    """A copy of the foundation catalog with one symbol_id repointed at nothing.

    The catalog itself stays loadable and the project stays topologically
    valid: only the join to the symbol library is broken, which is exactly the
    failure the cross-check exists to catch.
    """
    catalog = tmp_path / "catalog"
    shutil.copytree(FIXTURES / "catalog", catalog)
    path = catalog / "gas-boiler.json"
    definition = json.loads(path.read_text(encoding="utf-8"))
    definition["symbol_id"] = "does-not-exist-anywhere"
    path.write_text(json.dumps(definition, ensure_ascii=False), encoding="utf-8")
    return catalog


def test_validate_with_symbols_accepts_a_matching_pair() -> None:
    assert (
        main(
            [
                "validate",
                str(FIXTURES / "valid-mixed-project.json"),
                "--catalog",
                str(FIXTURES / "catalog"),
                "--symbols",
                str(FIXTURES / "symbols"),
            ]
        )
        == 0
    )


def test_validate_with_symbols_rejects_an_unresolvable_symbol_id(
    tmp_path: Path, capsys: CaptureFixture[str]
) -> None:
    """Closes the gap the cross-check had from the shipped binary: no command
    ever passed a SymbolRegistry, so a catalog whose symbol_id resolves to
    nothing loaded clean through the CLI.
    """
    exit_code = main(
        [
            "validate",
            str(FIXTURES / "valid-mixed-project.json"),
            "--catalog",
            str(broken_catalog(tmp_path)),
            "--symbols",
            str(FIXTURES / "symbols"),
        ]
    )
    assert exit_code == 1
    assert "does-not-exist-anywhere" in capsys.readouterr().err


def test_validate_without_symbols_behaves_as_before(tmp_path: Path) -> None:
    """--symbols is optional and opt-in: omitting it leaves the cross-check
    unwired, exactly as today (D-024/P-3: symbols stay optional on
    ComponentRegistry).
    """
    assert (
        main(
            [
                "validate",
                str(FIXTURES / "valid-mixed-project.json"),
                "--catalog",
                str(broken_catalog(tmp_path)),
            ]
        )
        == 0
    )


def test_foundation_catalog_matches_its_symbols() -> None:
    """Closes the gap Task 3's review flagged: `--symbols` is optional on
    `validate`, so a caller who omits it never exercises ComponentRegistry's
    cross-check, and nothing would verify the shipped catalog against its own
    symbols.
    This proves it once, directly: a future edit that repoints a symbol_id at
    something that does not exist, or renames a port on only one side of the
    join, fails here instead of shipping silently.
    """
    symbols = SymbolRegistry.from_directory(FIXTURES / "symbols")
    catalog = ComponentRegistry.from_directory(FIXTURES / "catalog", symbols=symbols)
    assert [item.id for item in catalog.all()] == [
        "air-terminal",
        "boundary-gas-source",
        "boundary-hydronic-return",
        "boundary-hydronic-supply",
        "gas-boiler",
        "supply-fan",
        "vrv-indoor",
        "vrv-outdoor",
    ]
