import pytest

from disegnatore_mep.graphics.composite import CompositeSpec, compile_composite
from disegnatore_mep.graphics.registry import Symbol, SymbolRegistry
from disegnatore_mep.graphics.symbol import KeepOut, SymbolManifest


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
            "keep_out": {"left_mm": 2.0, "right_mm": 2.0},
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
        "keep_out": {"left_mm": 2.0, "right_mm": 2.0},
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
    """Float rounding causes 4.0 + 4.03 = 8.030000000000001 > 8.03 without tolerance.

    This tests the critical case where a part placed at offset 4.0 with width 4.03
    should fit exactly in a composite of width 8.03, but due to float arithmetic,
    the sum is 8.030000000000001 which is > 8.03 without tolerance. Without the
    TOLERANCE_MM adjustment, this valid composite would be falsely rejected.
    """
    narrow_primitive = Symbol(
        manifest=SymbolManifest.model_validate({
            "id": "narrow-valve",
            "version": "1.0.0",
            "name": "narrow-valve",
            "width_mm": 4.03,
            "height_mm": 6.0,
            "allowed_rotations_deg": [0],
            "ports": [
                {"id": "a", "face": "left", "x_mm": 0.0, "y_mm": 3.0},
                {"id": "b", "face": "right", "x_mm": 4.03, "y_mm": 3.0},
            ],
            "keep_out": {"left_mm": 2.0, "right_mm": 2.0},
            "source": "CONV-GRAFICA-003",
        }),
        body='<g id="narrow-valve"/>'
    )
    flush_registry = SymbolRegistry([narrow_primitive])
    flush_spec = CompositeSpec.model_validate({
        "id": "flush-composite",
        "version": "1.0.0",
        "name": "Flush Composite",
        "width_mm": 8.03,
        "height_mm": 6.0,
        "allowed_rotations_deg": [0],
        "keep_out": {"right_mm": 2.0},
        "source": "TEST",
        "parts": [
            {"symbol_id": "narrow-valve", "offset_x_mm": 4.0, "offset_y_mm": 0.0},
        ],
        "exposed_ports": [
            {"part_index": 0, "port_id": "b", "as_id": "outlet"},
        ],
    })
    # Should not raise with tolerance
    symbol = compile_composite(flush_spec, flush_registry)
    assert symbol.manifest.port("outlet").x_mm == 8.030000000000001


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


def test_compiled_composite_carries_the_supplied_keep_out() -> None:
    """keep_out is authored on the spec, never inferred from the parts.

    Both parts here declare their own 2 mm clearance, but part 0's right side
    sits at x=6 - deep inside the 16 mm composite - so its clearance says
    nothing about the composite's outer envelope. Only the spec knows.
    """
    supplied = {"left_mm": 3.0, "right_mm": 2.0, "bottom_mm": 1.5}
    symbol = compile_composite(spec(keep_out=supplied), registry())
    assert symbol.manifest.keep_out.left_mm == 3.0
    # No port on the bottom face, so nothing could have derived this: it is
    # authored on the spec and carried through verbatim.
    assert symbol.manifest.keep_out.bottom_mm == 1.5
    assert symbol.manifest.keep_out.top_mm == 0.0


def test_composite_assembled_from_inline_parts_is_inline_when_declared() -> None:
    """D-027: an in-line component breaks the connection into two segments.

    A composite built from in-line primitives is itself in-line, and the router
    can only know that from `inline_gap_mm` on the compiled manifest.
    """
    symbol = compile_composite(spec(inline_gap_mm=16.0), registry())
    assert symbol.manifest.is_inline
    assert symbol.manifest.inline_gap_mm == 16.0


def test_composite_without_an_inline_gap_is_not_inline() -> None:
    assert not compile_composite(spec(), registry()).manifest.is_inline


def test_compiled_composite_carries_its_label_anchors() -> None:
    anchors = [
        {"id": "tag", "role": "tag", "x_mm": 8.0, "y_mm": -1.0},
        {"id": "note", "role": "description", "x_mm": 8.0, "y_mm": 8.0},
    ]
    symbol = compile_composite(spec(label_anchors=anchors), registry())
    assert [item.id for item in symbol.manifest.label_anchors] == ["tag", "note"]
    assert symbol.manifest.label_anchors[0].role == "tag"


def test_inline_composite_must_satisfy_the_two_opposed_ports_rule() -> None:
    """The compiled manifest is validated like any other: an in-line symbol
    exposing a single port is rejected, not quietly published.
    """
    single_port = spec(
        inline_gap_mm=16.0,
        exposed_ports=[{"part_index": 0, "port_id": "a", "as_id": "inlet"}],
    )
    with pytest.raises(ValueError, match="an inline symbol needs two opposed ports"):
        compile_composite(single_port, registry())


def test_inline_gap_wider_than_the_composite_box_is_rejected() -> None:
    with pytest.raises(ValueError, match="inline gap cannot exceed the symbol width"):
        compile_composite(spec(inline_gap_mm=99.0), registry())


def test_spec_defaults_match_the_manifest_defaults() -> None:
    """A composite is authored exactly like a hand-written symbol: same three
    optional fields, same defaults.
    """
    bare = CompositeSpec.model_validate(
        {
            "id": "bare",
            "version": "1.0.0",
            "name": "Bare",
            "width_mm": 16.0,
            "height_mm": 6.0,
            "allowed_rotations_deg": [0],
            "source": "TEST",
            "parts": [{"symbol_id": "valve", "offset_x_mm": 0.0, "offset_y_mm": 0.0}],
            "exposed_ports": [{"part_index": 0, "port_id": "a", "as_id": "inlet"}],
        }
    )
    assert bare.keep_out == KeepOut()
    assert bare.inline_gap_mm is None
    assert bare.label_anchors == []
