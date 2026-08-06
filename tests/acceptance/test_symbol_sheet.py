from pathlib import Path
from xml.etree import ElementTree

from disegnatore_mep.cli import main
from disegnatore_mep.graphics.registry import SymbolRegistry

SYMBOLS = Path(__file__).resolve().parents[2] / "assets" / "symbols"


def test_the_shipped_library_loads() -> None:
    assert len(SymbolRegistry.from_directory(SYMBOLS).all()) == 32


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


def test_every_shipped_symbol_shows_its_italian_name(tmp_path: Path) -> None:
    """D-051: la tavola e' in italiano. Il foglio mostra il nome del componente,
    non l'identificativo interno, che resta un riferimento di codice."""
    output = tmp_path / "symbols.svg"
    main(["symbols-sheet", str(output), "--symbols", str(SYMBOLS)])
    content = output.read_text(encoding="utf-8")
    for symbol in SymbolRegistry.from_directory(SYMBOLS).all():
        assert symbol.manifest.name in content


def test_restricted_symbols_declare_only_their_technical_orientations() -> None:
    """allowed_rotations_deg is a technical constraint, not a geometric one:
    all four rotations are always geometrically possible, but an automatic air
    vent discharges upward and a membrane expansion vessel is drawn upright.
    Ruled by the project owner (a thermal engineer); see
    docs/GRAPHIC_STANDARD.md §3.2.
    """
    registry = SymbolRegistry.from_directory(SYMBOLS)
    assert registry.get("air-vent").manifest.allowed_rotations_deg == [0]
    assert registry.get("expansion-connection").manifest.allowed_rotations_deg == [0, 180]


def test_upright_symbols_declare_only_their_own_orientation() -> None:
    """Accumuli, macchine e collettori si disegnano nel proprio verso: una
    pompa di calore coricata o un bollitore di traverso non aiutano a leggere
    la tavola, e D-049 riguarda proprio il senso impiantistico."""
    registry = SymbolRegistry.from_directory(SYMBOLS)
    for symbol_id in ("heat-pump-air-water", "dhw-cylinder", "buffer-four-port", "zone-manifold"):
        assert registry.get(symbol_id).manifest.allowed_rotations_deg == [0]


def test_every_other_shipped_symbol_admits_all_four_rotations() -> None:
    restricted = {
        "air-vent",
        "expansion-connection",
        "heat-pump-air-water",
        "dhw-cylinder",
        "buffer-four-port",
        "zone-manifold",
    }
    for symbol in SymbolRegistry.from_directory(SYMBOLS).all():
        if symbol.manifest.id not in restricted:
            assert symbol.manifest.allowed_rotations_deg == [0, 90, 180, 270]


def test_missing_symbol_directory_returns_one(tmp_path: Path) -> None:
    assert main(["symbols-sheet", str(tmp_path / "out.svg"), "--symbols", str(tmp_path / "nope")]) == 1


def test_existing_but_wrong_symbol_directory_returns_one(tmp_path: Path) -> None:
    """`--symbols assets` - a real directory one level above assets/symbols -
    used to exit 0 after writing an A3 containing no symbols at all.
    """
    output = tmp_path / "out.svg"
    assert main(["symbols-sheet", str(output), "--symbols", str(SYMBOLS.parent)]) == 1
    assert not output.exists()
