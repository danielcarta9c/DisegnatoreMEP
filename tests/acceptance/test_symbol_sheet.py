from pathlib import Path
from xml.etree import ElementTree

from disegnatore_mep.cli import main
from disegnatore_mep.graphics.registry import SymbolRegistry

SYMBOLS = Path(__file__).resolve().parents[2] / "assets" / "symbols"


def test_the_shipped_library_loads() -> None:
    assert len(SymbolRegistry.from_directory(SYMBOLS).all()) == 12


def test_symbols_sheet_command_writes_a_true_scale_sheet(tmp_path: Path) -> None:
    output = tmp_path / "symbols.svg"
    assert main(["symbols-sheet", str(output), "--symbols", str(SYMBOLS)]) == 0
    content = output.read_text(encoding="utf-8")
    assert 'width="420mm"' in content
    assert 'viewBox="0 0 420 297"' in content
    ElementTree.fromstring(content)


def test_every_shipped_symbol_appears_on_the_sheet(tmp_path: Path) -> None:
    output = tmp_path / "symbols.svg"
    main(["symbols-sheet", str(output), "--symbols", str(SYMBOLS)])
    content = output.read_text(encoding="utf-8")
    for symbol in SymbolRegistry.from_directory(SYMBOLS).all():
        assert f'data-symbol-id="{symbol.manifest.id}"' in content


def test_missing_symbol_directory_returns_one(tmp_path: Path) -> None:
    assert main(["symbols-sheet", str(tmp_path / "out.svg"), "--symbols", str(tmp_path / "nope")]) == 1


def test_existing_but_wrong_symbol_directory_returns_one(tmp_path: Path) -> None:
    """`--symbols assets` - a real directory one level above assets/symbols -
    used to exit 0 after writing an A3 containing no symbols at all.
    """
    output = tmp_path / "out.svg"
    assert main(["symbols-sheet", str(output), "--symbols", str(SYMBOLS.parent)]) == 1
    assert not output.exists()
