import pytest

from disegnatore_mep.graphics.composite import CompositeSpec, compile_composite
from disegnatore_mep.graphics.registry import Symbol, SymbolRegistry
from disegnatore_mep.graphics.symbol import SymbolManifest


def primitive(symbol_id: str) -> Symbol:
    manifest = SymbolManifest.model_validate(
        {
            "id": symbol_id,
            "version": "1.0.0",
            "name": symbol_id,
            "width_mm": 6.0,
            "height_mm": 6.0,
            "allowed_rotations_deg": [0],
            "inline_gap_mm": 6.0,
            "ports": [
                {"id": "a", "face": "left", "x_mm": 0.0, "y_mm": 3.0},
                {"id": "b", "face": "right", "x_mm": 6.0, "y_mm": 3.0},
            ],
            "source": "CONV-GRAFICA-001",
        }
    )
    return Symbol(manifest=manifest, body=f'<g id="{symbol_id}"/>')


def registry() -> SymbolRegistry:
    return SymbolRegistry([primitive("valve"), primitive("filter")])


def spec(**overrides: object) -> CompositeSpec:
    payload: dict[str, object] = {
        "id": "filling-group",
        "version": "1.0.0",
        "name": "Gruppo di riempimento",
        "width_mm": 16.0,
        "height_mm": 6.0,
        "allowed_rotations_deg": [0, 180],
        "source": "CONV-GRAFICA-002",
        "parts": [
            {"symbol_id": "valve", "offset_x_mm": 0.0, "offset_y_mm": 0.0},
            {"symbol_id": "filter", "offset_x_mm": 10.0, "offset_y_mm": 0.0},
        ],
        "exposed_ports": [
            {"part_index": 0, "port_id": "a", "as_id": "inlet"},
            {"part_index": 1, "port_id": "b", "as_id": "outlet"},
        ],
    }
    payload.update(overrides)
    return CompositeSpec.model_validate(payload)


def test_compiled_composite_is_a_single_symbol() -> None:
    symbol = compile_composite(spec(), registry())
    assert symbol.manifest.id == "filling-group"
    assert sorted(symbol.manifest.port_ids) == ["inlet", "outlet"]


def test_exposed_ports_carry_the_translated_position() -> None:
    symbol = compile_composite(spec(), registry())
    assert symbol.manifest.port("outlet").x_mm == 16.0
    assert symbol.manifest.port("inlet").x_mm == 0.0


def test_body_nests_each_part_with_its_offset() -> None:
    body = compile_composite(spec(), registry()).body
    assert 'translate(10.0 0.0)' in body
    assert body.count("<g") >= 2


def test_part_falling_outside_the_composite_box_is_rejected() -> None:
    with pytest.raises(ValueError, match="part 1 falls outside the composite box"):
        compile_composite(spec(width_mm=8.0), registry())


def test_unknown_primitive_is_rejected() -> None:
    invalid = spec(parts=[{"symbol_id": "nope", "offset_x_mm": 0.0, "offset_y_mm": 0.0}],
                   exposed_ports=[{"part_index": 0, "port_id": "a", "as_id": "inlet"}])
    with pytest.raises(ValueError, match="unknown symbol: nope"):
        compile_composite(invalid, registry())


def test_infinite_width_mm_is_rejected() -> None:
    with pytest.raises(ValueError, match="value must be a finite number"):
        spec(width_mm=float("inf"))


def test_bad_port_id_is_rejected() -> None:
    invalid = spec(exposed_ports=[{"part_index": 0, "port_id": "c", "as_id": "invalid"}])
    with pytest.raises(ValueError, match="part 0 has no port c"):
        compile_composite(invalid, registry())


def test_part_flush_with_box_passes_with_tolerance() -> None:
    """Float rounding causes 5.95 + 6.0 = 11.950000000000002 > 11.95 without tolerance.

    Using offset_x_mm = 0.05 * 119 produces 5.9500000000000017 due to float accumulation.
    With a 6.0-width part, this exceeds the 11.95 box boundary by ~2e-15, which triggers
    false rejection without tolerance but passes with it. The right port of the part
    (at offset + 6.0) lands exactly on the composite's right edge.
    """
    offset_value = 0.05 * 119
    flush_spec = spec(
        width_mm=11.95,
        height_mm=6.0,
        parts=[
            {"symbol_id": "valve", "offset_x_mm": offset_value, "offset_y_mm": 0.0},
        ],
        exposed_ports=[
            {"part_index": 0, "port_id": "b", "as_id": "outlet"},
        ],
    )
    # Should not raise with tolerance
    symbol = compile_composite(flush_spec, registry())
    assert symbol.manifest.port("outlet").x_mm == 11.95


def test_interior_port_is_rejected_by_perimeter_check() -> None:
    """A port from an interior-placed part is rejected by SymbolManifest perimeter validation.

    Even though the part fits within the box bounds, if its exposed port ends up at an
    interior point rather than on the composite's perimeter, SymbolManifest.geometry_is_coherent
    will reject the manifest construction.
    """
    interior_spec = spec(
        width_mm=20.0,
        height_mm=20.0,
        parts=[
            {"symbol_id": "valve", "offset_x_mm": 5.0, "offset_y_mm": 5.0},
        ],
        exposed_ports=[
            {"part_index": 0, "port_id": "a", "as_id": "interior_port"},
        ],
    )
    with pytest.raises(ValueError, match="is not on its left face"):
        compile_composite(interior_spec, registry())
