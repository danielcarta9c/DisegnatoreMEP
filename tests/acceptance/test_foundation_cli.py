import json
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


def test_foundation_catalog_matches_its_symbols() -> None:
    """Closes the gap Task 3's review flagged: `validate` never passes a
    SymbolRegistry (symbols stay optional by design - D-024/P-3 in progress.md),
    so nothing exercised ComponentRegistry's cross-check against shipped data.
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
