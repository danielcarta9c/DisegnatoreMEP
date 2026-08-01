import pytest
from pydantic import ValidationError

from disegnatore_mep.catalog.schema import ComponentDefinition


def geometry(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "width_mm": 10.0,
        "height_mm": 10.0,
        "clearance_mm": 2.0,
        "allowed_rotations_deg": [0, 90, 180, 270],
        "inline_gap_mm": 6.0,
    }
    base.update(overrides)
    return base


def port(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "id": "a",
        "domain": "hydronic",
        "medium": "heating_water",
        "flow": "bidirectional",
        "x_mm": 0.0,
        "y_mm": 5.0,
        "angle_deg": 180,
        "required": True,
        "max_connections": 1,
    }
    base.update(overrides)
    return base


def definition(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "id": "isolation-valve",
        "version": "1.0.0",
        "name": "Valvola di intercettazione",
        "functions": ["isolation"],
        "symbol_id": "valve-isolation",
        "composite": False,
        "geometry": geometry(),
        "ports": [port(id="a", x_mm=0.0), port(id="b", x_mm=10.0, angle_deg=0)],
        "sources": ["CONV-001"],
    }
    base.update(overrides)
    return base


def test_rejects_non_orthogonal_rotation() -> None:
    with pytest.raises(ValidationError, match="allowed rotations must be 0, 90, 180 or 270"):
        ComponentDefinition.model_validate(
            definition(geometry=geometry(allowed_rotations_deg=[181]))
        )


def test_rejects_duplicate_rotation() -> None:
    with pytest.raises(ValidationError, match="duplicate allowed rotation"):
        ComponentDefinition.model_validate(
            definition(geometry=geometry(allowed_rotations_deg=[0, 0]))
        )


def test_rejects_duplicate_port_id() -> None:
    with pytest.raises(ValidationError, match="duplicate port id"):
        ComponentDefinition.model_validate(
            definition(
                ports=[
                    port(id="a", x_mm=0.0),
                    port(id="a", x_mm=10.0, angle_deg=0),
                ]
            )
        )


def test_rejects_port_outside_symbol_width() -> None:
    with pytest.raises(ValidationError, match="port outside symbol width"):
        ComponentDefinition.model_validate(
            definition(ports=[port(id="a", x_mm=15.0)])
        )


def test_rejects_port_outside_symbol_height() -> None:
    with pytest.raises(ValidationError, match="port outside symbol height"):
        ComponentDefinition.model_validate(
            definition(ports=[port(id="a", y_mm=15.0)])
        )


def test_rejects_non_orthogonal_port_angle() -> None:
    with pytest.raises(ValidationError):
        ComponentDefinition.model_validate(
            definition(ports=[port(id="a", angle_deg=45)])
        )


def test_accepts_port_at_centre_of_symbol() -> None:
    parsed = ComponentDefinition.model_validate(
        definition(ports=[port(id="a", x_mm=5.0, y_mm=5.0, angle_deg=0)])
    )
    assert parsed.ports[0].x_mm == 5.0
    assert parsed.ports[0].y_mm == 5.0
