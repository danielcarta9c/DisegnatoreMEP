import json
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import CatalogError, ComponentRegistry


def definition(component_id: str) -> dict[str, object]:
    return {
        "id": component_id,
        "version": "1.0.0",
        "name": "Valvola di intercettazione",
        "functions": ["isolation"],
        "symbol_id": "valve-isolation",
        "composite": False,
        "geometry": {
            "width_mm": 6.0,
            "height_mm": 6.0,
            "clearance_mm": 2.0,
            "allowed_rotations_deg": [0, 90, 180, 270],
            "inline_gap_mm": 6.0,
        },
        "ports": [
            {
                "id": "a",
                "domain": "hydronic",
                "medium": "heating_water",
                "flow": "bidirectional",
                "x_mm": 0.0,
                "y_mm": 3.0,
                "angle_deg": 180,
                "required": True,
                "max_connections": 1,
            },
            {
                "id": "b",
                "domain": "hydronic",
                "medium": "heating_water",
                "flow": "bidirectional",
                "x_mm": 6.0,
                "y_mm": 3.0,
                "angle_deg": 0,
                "required": True,
                "max_connections": 1,
            },
        ],
        "sources": ["CONV-001"],
    }


def write_definition(path: Path, component_id: str) -> None:
    path.write_text(json.dumps(definition(component_id)), encoding="utf-8")


def test_registry_loads_definition(tmp_path: Path) -> None:
    write_definition(tmp_path / "valve.json", "isolation-valve")
    registry = ComponentRegistry.from_directory(tmp_path)
    assert registry.get("isolation-valve").geometry.inline_gap_mm == 6.0


def test_registry_rejects_duplicate_ids(tmp_path: Path) -> None:
    write_definition(tmp_path / "a.json", "isolation-valve")
    write_definition(tmp_path / "b.json", "isolation-valve")
    with pytest.raises(CatalogError, match="duplicate component definition"):
        ComponentRegistry.from_directory(tmp_path)
