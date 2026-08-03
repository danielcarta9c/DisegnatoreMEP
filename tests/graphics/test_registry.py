import json
from pathlib import Path

import pytest

from disegnatore_mep.graphics.registry import SymbolError, SymbolRegistry


def manifest_payload(symbol_id: str) -> dict[str, object]:
    return {
        "id": symbol_id,
        "version": "1.0.0",
        "name": "Valvola di intercettazione",
        "width_mm": 6.0,
        "height_mm": 6.0,
        "allowed_rotations_deg": [0, 90, 180, 270],
        "inline_gap_mm": 6.0,
        "ports": [
            {"id": "a", "face": "left", "x_mm": 0.0, "y_mm": 3.0},
            {"id": "b", "face": "right", "x_mm": 6.0, "y_mm": 3.0},
        ],
        "keep_out": {"left_mm": 2.0, "right_mm": 2.0, "top_mm": 1.0, "bottom_mm": 1.0},
        "label_anchors": [{"id": "tag", "role": "tag", "x_mm": 3.0, "y_mm": -1.0}],
        "source": "CONV-GRAFICA-001",
    }


SVG_BODY = '<g><line x1="0" y1="3" x2="6" y2="3"/></g>'


def write_symbol(directory: Path, symbol_id: str, body: str = SVG_BODY) -> None:
    (directory / f"{symbol_id}.json").write_text(
        json.dumps(manifest_payload(symbol_id)), encoding="utf-8"
    )
    (directory / f"{symbol_id}.svg").write_text(body, encoding="utf-8")


def test_registry_loads_a_symbol(tmp_path: Path) -> None:
    write_symbol(tmp_path, "valve-isolation")
    registry = SymbolRegistry.from_directory(tmp_path)
    assert registry.get("valve-isolation").manifest.width_mm == 6.0
    assert "line" in registry.get("valve-isolation").body


def test_missing_directory_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(SymbolError, match="symbol directory not found"):
        SymbolRegistry.from_directory(tmp_path / "nope")


def test_manifest_without_body_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "valve-isolation.json").write_text(
        json.dumps(manifest_payload("valve-isolation")), encoding="utf-8"
    )
    with pytest.raises(SymbolError, match="missing svg body for valve-isolation"):
        SymbolRegistry.from_directory(tmp_path)


def test_filename_must_match_the_manifest_id(tmp_path: Path) -> None:
    (tmp_path / "wrong-name.json").write_text(
        json.dumps(manifest_payload("valve-isolation")), encoding="utf-8"
    )
    (tmp_path / "wrong-name.svg").write_text(SVG_BODY, encoding="utf-8")
    with pytest.raises(SymbolError, match="file name does not match symbol id"):
        SymbolRegistry.from_directory(tmp_path)


def test_body_carrying_its_own_svg_root_is_rejected(tmp_path: Path) -> None:
    write_symbol(tmp_path, "valve-isolation", body="<svg><g/></svg>")
    with pytest.raises(SymbolError, match="svg body must not contain an <svg> root"):
        SymbolRegistry.from_directory(tmp_path)


def test_unknown_symbol_lookup_is_rejected(tmp_path: Path) -> None:
    write_symbol(tmp_path, "valve-isolation")
    registry = SymbolRegistry.from_directory(tmp_path)
    with pytest.raises(SymbolError, match="unknown symbol: nope"):
        registry.get("nope")


def test_all_is_ordered_by_id(tmp_path: Path) -> None:
    write_symbol(tmp_path, "zzz-valve")
    write_symbol(tmp_path, "aaa-valve")
    registry = SymbolRegistry.from_directory(tmp_path)
    assert [item.manifest.id for item in registry.all()] == ["aaa-valve", "zzz-valve"]


def test_duplicate_symbol_is_rejected(tmp_path: Path) -> None:
    # Direct construction, not from_directory: Task 4's composite compiler
    # builds a SymbolRegistry straight from a list of Symbol objects, so
    # __init__'s own duplicate check needs its own test independent of the
    # filename/id coupling from_directory enforces.
    write_symbol(tmp_path, "valve-isolation")
    symbol = SymbolRegistry.from_directory(tmp_path).get("valve-isolation")
    with pytest.raises(SymbolError, match="duplicate symbol: valve-isolation"):
        SymbolRegistry([symbol, symbol])
