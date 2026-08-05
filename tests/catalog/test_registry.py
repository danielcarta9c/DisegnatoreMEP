import json
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import CatalogError, ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry


def definition(component_id: str, ports: list[str] | None = None) -> dict[str, object]:
    return {
        "id": component_id,
        "version": "1.0.0",
        "name": "Valvola di intercettazione",
        "functions": ["isolation"],
        "traits": ["shutoff_ordinary", "attachment_inline"],
        "symbol_id": "valve-isolation",
        "composite": False,
        "ports": [
            {
                "id": port_id,
                "domain": "hydronic",
                "medium": "heating_water",
                "flow": "bidirectional",
                "required": True,
                "max_connections": 1,
            }
            for port_id in (ports or ["a", "b"])
        ],
        "sources": ["CONV-001"],
    }


def write_definition(path: Path, component_id: str) -> None:
    path.write_text(json.dumps(definition(component_id)), encoding="utf-8")


# Duplicated from tests/graphics/test_registry.py: pytest runs with
# --import-mode=importlib, so the test packages are not importable from
# one another.
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


def test_registry_loads_definition(tmp_path: Path) -> None:
    write_definition(tmp_path / "valve.json", "isolation-valve")
    registry = ComponentRegistry.from_directory(tmp_path)
    assert registry.get("isolation-valve").symbol_id == "valve-isolation"


def test_registry_rejects_duplicate_ids(tmp_path: Path) -> None:
    write_definition(tmp_path / "a.json", "isolation-valve")
    write_definition(tmp_path / "b.json", "isolation-valve")
    with pytest.raises(CatalogError, match="duplicate component definition"):
        ComponentRegistry.from_directory(tmp_path)


def test_registry_accepts_a_definition_matching_its_symbol(tmp_path: Path) -> None:
    catalog_dir = tmp_path / "catalog"
    symbol_dir = tmp_path / "symbols"
    catalog_dir.mkdir()
    symbol_dir.mkdir()
    write_symbol(symbol_dir, "valve-isolation")
    write_definition(catalog_dir / "valve.json", "isolation-valve")
    registry = ComponentRegistry.from_directory(
        catalog_dir, symbols=SymbolRegistry.from_directory(symbol_dir)
    )
    assert registry.get("isolation-valve").symbol_id == "valve-isolation"


def test_registry_rejects_unknown_symbol(tmp_path: Path) -> None:
    catalog_dir = tmp_path / "catalog"
    symbol_dir = tmp_path / "symbols"
    catalog_dir.mkdir()
    symbol_dir.mkdir()
    # A populated library that simply does not carry this symbol: an empty
    # directory is no longer a way to build an empty registry (SymbolRegistry
    # rejects a directory with no manifests), and the branch under test here is
    # the catalog's cross-check, not the library's own emptiness.
    write_symbol(symbol_dir, "valve-check")
    write_definition(catalog_dir / "valve.json", "isolation-valve")
    with pytest.raises(
        CatalogError, match="unknown symbol valve-isolation for isolation-valve"
    ):
        ComponentRegistry.from_directory(
            catalog_dir, symbols=SymbolRegistry.from_directory(symbol_dir)
        )


def test_registry_rejects_ports_the_symbol_does_not_have(tmp_path: Path) -> None:
    catalog_dir = tmp_path / "catalog"
    symbol_dir = tmp_path / "symbols"
    catalog_dir.mkdir()
    symbol_dir.mkdir()
    write_symbol(symbol_dir, "valve-isolation")
    (catalog_dir / "valve.json").write_text(
        json.dumps(definition("isolation-valve", ports=["a", "c"])), encoding="utf-8"
    )
    with pytest.raises(CatalogError, match="port ids do not match symbol valve-isolation"):
        ComponentRegistry.from_directory(
            catalog_dir, symbols=SymbolRegistry.from_directory(symbol_dir)
        )
