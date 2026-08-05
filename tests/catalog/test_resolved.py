import json
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import CatalogError, ComponentRegistry
from disegnatore_mep.catalog.resolved import ResolvedComponent
from disegnatore_mep.catalog.schema import ComponentDefinition
from disegnatore_mep.graphics.registry import Symbol, SymbolRegistry
from disegnatore_mep.graphics.symbol import PortFace, SymbolManifest

FIXTURES = Path(__file__).resolve().parents[2] / "examples" / "foundation"


def foundation() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        FIXTURES / "catalog", symbols=SymbolRegistry.from_directory(FIXTURES / "symbols")
    )


# Duplicated from tests/catalog/test_registry.py: pytest runs with
# --import-mode=importlib, so the test packages are not importable from
# one another.
def definition_payload(ports: list[str] | None = None) -> dict[str, object]:
    return {
        "id": "isolation-valve",
        "version": "1.0.0",
        "name": "Valvola di intercettazione",
        "functions": ["isolation"],
        "traits": ["isolation_normal", "attachment_inline"],
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


def manifest_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": "valve-isolation",
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
        "keep_out": {"left_mm": 2.0, "right_mm": 2.0},
        "source": "CONV-GRAFICA-001",
    }
    payload.update(overrides)
    return payload


def a_symbol(**overrides: object) -> Symbol:
    return Symbol(
        manifest=SymbolManifest.model_validate(manifest_payload(**overrides)),
        body='<line x1="0" y1="3" x2="6" y2="3"/>',
    )


def write_pair(tmp_path: Path) -> tuple[Path, Path]:
    catalog_dir, symbol_dir = tmp_path / "catalog", tmp_path / "symbols"
    catalog_dir.mkdir()
    symbol_dir.mkdir()
    (catalog_dir / "valve.json").write_text(json.dumps(definition_payload()), "utf-8")
    (symbol_dir / "valve-isolation.json").write_text(json.dumps(manifest_payload()), "utf-8")
    (symbol_dir / "valve-isolation.svg").write_text(
        '<line x1="0" y1="3" x2="6" y2="3"/>', "utf-8"
    )
    return catalog_dir, symbol_dir


def test_resolve_joins_the_two_halves_of_a_component() -> None:
    resolved = foundation().resolve("gas-boiler")
    assert resolved.definition.id == "gas-boiler"
    assert resolved.symbol.manifest.id == "gas-boiler"
    assert resolved.port_ids == resolved.definition.port_ids
    assert resolved.port_ids == resolved.symbol.manifest.port_ids


def test_a_resolved_port_carries_semantics_and_geometry() -> None:
    """Il punto della vista: da una porta si arriva sia al verso sia alla faccia."""
    port = foundation().resolve("gas-boiler").port("water_supply")
    assert port.definition.flow.value == "out"
    assert port.definition.medium == "heating_water"
    assert isinstance(port.geometry.face, PortFace)
    assert port.geometry.outward_angle_deg == port.geometry.face.outward_angle_deg


def test_an_unknown_port_raises_the_catalog_error(tmp_path: Path) -> None:
    """R3 del piano grafico: un KeyError sfugge al pattern di cattura dei caricatori."""
    with pytest.raises(CatalogError, match="unknown port"):
        foundation().resolve("gas-boiler").port("does-not-exist")


def test_resolve_without_a_symbol_library_says_how_to_fix_it() -> None:
    registry = ComponentRegistry.from_directory(FIXTURES / "catalog")
    with pytest.raises(CatalogError, match="loaded without a symbol library"):
        registry.resolve("gas-boiler")


def test_is_inline_comes_from_the_symbol(tmp_path: Path) -> None:
    catalog_dir, symbol_dir = write_pair(tmp_path)
    registry = ComponentRegistry.from_directory(
        catalog_dir, symbols=SymbolRegistry.from_directory(symbol_dir)
    )
    assert registry.resolve("isolation-valve").is_inline is True
    assert foundation().resolve("gas-boiler").is_inline is False


def test_box_mm_comes_from_the_symbol(tmp_path: Path) -> None:
    catalog_dir, symbol_dir = write_pair(tmp_path)
    registry = ComponentRegistry.from_directory(
        catalog_dir, symbols=SymbolRegistry.from_directory(symbol_dir)
    )
    assert registry.resolve("isolation-valve").box_mm == (6.0, 6.0)


def test_every_foundation_definition_resolves() -> None:
    """La verifica incrociata dimostra che gli insiemi coincidono: qui si usa
    davvero l'accoppiamento che finora veniva buttato via."""
    registry = foundation()
    for definition in registry.all():
        resolved = registry.resolve(definition.id)
        assert resolved.definition is definition


def test_an_unknown_definition_raises_the_catalog_error() -> None:
    with pytest.raises(CatalogError, match="unknown component definition"):
        foundation().resolve("no-such-component")


def test_mismatched_port_sets_are_refused_by_the_view_itself() -> None:
    """Il validatore riasserisce l'invariante invece di fidarsi del costruttore
    (D-037): la vista non dipende dal fatto che il registro abbia controllato."""
    definition = ComponentDefinition.model_validate(definition_payload(ports=["a", "c"]))
    with pytest.raises(CatalogError, match="port ids do not match"):
        ResolvedComponent(definition=definition, symbol=a_symbol())
