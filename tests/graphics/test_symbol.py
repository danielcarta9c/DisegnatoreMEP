import pytest
from pydantic import ValidationError

from disegnatore_mep.graphics.symbol import (
    KeepOut,
    LabelAnchor,
    PortFace,
    SymbolManifest,
    SymbolPort,
)


def manifest(**overrides: object) -> SymbolManifest:
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
        "keep_out": {"left_mm": 2.0, "right_mm": 2.0, "top_mm": 1.0, "bottom_mm": 1.0},
        "label_anchors": [{"id": "tag", "role": "tag", "x_mm": 3.0, "y_mm": -1.0}],
        "source": "CONV-GRAFICA-001",
    }
    payload.update(overrides)
    return SymbolManifest.model_validate(payload)


def test_manifest_accepts_ports_on_the_perimeter() -> None:
    assert manifest().port("a").outward_angle_deg == 180


def test_outward_angle_is_derived_from_the_face() -> None:
    assert PortFace.RIGHT.outward_angle_deg == 0
    assert PortFace.BOTTOM.outward_angle_deg == 90
    assert PortFace.LEFT.outward_angle_deg == 180
    assert PortFace.TOP.outward_angle_deg == 270


def test_port_off_its_declared_face_is_rejected() -> None:
    with pytest.raises(ValidationError, match="port a is not on its left face"):
        manifest(ports=[{"id": "a", "face": "left", "x_mm": 3.0, "y_mm": 3.0}])


def test_port_in_the_interior_is_rejected() -> None:
    with pytest.raises(ValidationError, match="port a is not on its top face"):
        manifest(ports=[{"id": "a", "face": "top", "x_mm": 3.0, "y_mm": 3.0}])


def test_port_outside_the_box_is_rejected() -> None:
    with pytest.raises(ValidationError, match="port a falls outside the symbol box"):
        manifest(ports=[{"id": "a", "face": "left", "x_mm": 0.0, "y_mm": 99.0}])


def test_duplicate_port_ids_are_rejected() -> None:
    with pytest.raises(ValidationError, match="duplicate port id: a"):
        manifest(
            ports=[
                {"id": "a", "face": "left", "x_mm": 0.0, "y_mm": 3.0},
                {"id": "a", "face": "right", "x_mm": 6.0, "y_mm": 3.0},
            ]
        )


def test_inline_symbol_needs_two_opposed_ports() -> None:
    with pytest.raises(ValidationError, match="an inline symbol needs two opposed ports"):
        manifest(
            inline_gap_mm=6.0,
            ports=[
                {"id": "a", "face": "left", "x_mm": 0.0, "y_mm": 3.0},
                {"id": "b", "face": "top", "x_mm": 3.0, "y_mm": 0.0},
            ],
        )


def test_non_inline_symbol_may_have_any_arrangement() -> None:
    assert (
        manifest(
            inline_gap_mm=None,
            ports=[
                {"id": "a", "face": "left", "x_mm": 0.0, "y_mm": 3.0},
                {"id": "b", "face": "top", "x_mm": 3.0, "y_mm": 0.0},
            ],
        ).inline_gap_mm
        is None
    )


def test_inline_gap_cannot_exceed_the_symbol_width() -> None:
    with pytest.raises(ValidationError, match="inline gap cannot exceed the symbol width"):
        manifest(inline_gap_mm=99.0)


def test_duplicate_label_anchor_ids_are_rejected() -> None:
    with pytest.raises(ValidationError, match="duplicate label anchor id: tag"):
        manifest(
            label_anchors=[
                {"id": "tag", "role": "tag", "x_mm": 3.0, "y_mm": -1.0},
                {"id": "tag", "role": "description", "x_mm": 3.0, "y_mm": 8.0},
            ]
        )


def test_keep_out_defaults_to_zero() -> None:
    assert KeepOut().left_mm == 0.0


def test_keep_out_must_be_non_zero_on_a_face_that_carries_a_port() -> None:
    """The rule was documented and enforced nowhere: KeepOut defaults every side
    to zero and both generators built the dict by membership test over the four
    side names, so a typo shipped a symbol with no clearance in silence.

    The manifest cannot know the paper's min_clearance_mm - it has no
    GraphicStandard - so the invariant that belongs here is "greater than zero".
    """
    with pytest.raises(
        ValidationError,
        match="keep_out.left_mm must be greater than zero: the left face carries a port",
    ):
        manifest(keep_out={"left_mm": 0.0, "right_mm": 2.0, "top_mm": 1.0, "bottom_mm": 1.0})


def test_keep_out_stays_zero_on_a_face_without_a_port() -> None:
    accepted = manifest(keep_out={"left_mm": 2.0, "right_mm": 2.0})
    assert accepted.keep_out.top_mm == 0.0
    assert accepted.keep_out.bottom_mm == 0.0


def test_a_default_keep_out_no_longer_passes_with_ports() -> None:
    """A manifest that simply omits keep_out is now rejected rather than
    shipping a symbol a router would butt a pipe against.
    """
    with pytest.raises(ValidationError, match="must be greater than zero"):
        manifest(keep_out={})


def test_label_anchor_may_sit_outside_the_box() -> None:
    anchor = LabelAnchor(id="tag", role="tag", x_mm=3.0, y_mm=-1.0)
    assert anchor.y_mm == -1.0


def test_symbol_port_is_immutable() -> None:
    port = SymbolPort(id="a", face=PortFace.LEFT, x_mm=0.0, y_mm=3.0)
    with pytest.raises(ValidationError):
        port.x_mm = 1.0  # type: ignore[misc]


def test_infinite_width_is_rejected() -> None:
    with pytest.raises(ValidationError, match="value must be a finite number"):
        manifest(width_mm=float("inf"))


def test_invalid_rotation_is_rejected() -> None:
    with pytest.raises(ValidationError, match="allowed rotations must be 0, 90, 180 or 270"):
        manifest(allowed_rotations_deg=[181])


def test_duplicate_rotation_is_rejected() -> None:
    with pytest.raises(ValidationError, match="duplicate allowed rotation"):
        manifest(allowed_rotations_deg=[0, 0])


def test_unknown_port_lookup_is_rejected() -> None:
    with pytest.raises(KeyError, match="unknown symbol port: nope"):
        manifest().port("nope")
