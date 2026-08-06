import pytest
from pydantic import ValidationError

from disegnatore_mep.graphics.standard import A3_LANDSCAPE, GraphicStandard


def test_a3_landscape_has_iso_dimensions() -> None:
    assert (A3_LANDSCAPE.sheet_width_mm, A3_LANDSCAPE.sheet_height_mm) == (420.0, 297.0)


def test_usable_area_is_derived_from_margins() -> None:
    expected_width = 420.0 - A3_LANDSCAPE.margin_left_mm - A3_LANDSCAPE.margin_right_mm
    expected_height = 297.0 - A3_LANDSCAPE.margin_top_mm - A3_LANDSCAPE.margin_bottom_mm
    assert A3_LANDSCAPE.usable_width_mm == expected_width
    assert A3_LANDSCAPE.usable_height_mm == expected_height


def test_usable_width_is_a_whole_number_of_grid_steps() -> None:
    steps = A3_LANDSCAPE.usable_width_mm / A3_LANDSCAPE.grid_mm
    assert steps == int(steps)


def test_usable_height_is_not_grid_aligned_because_margins_follow_iso_5457() -> None:
    steps = A3_LANDSCAPE.usable_height_mm / A3_LANDSCAPE.grid_mm
    assert steps != int(steps)


def test_margins_cannot_exceed_the_sheet() -> None:
    with pytest.raises(ValidationError, match="margins leave no usable area"):
        GraphicStandard(
            sheet_width_mm=420,
            sheet_height_mm=297,
            margin_left_mm=250,
            margin_right_mm=250,
            margin_top_mm=10,
            margin_bottom_mm=10,
            grid_mm=2.5,
            line_thin_mm=0.18,
            line_medium_mm=0.35,
            line_thick_mm=0.5,
            text_small_mm=1.8,
            text_normal_mm=2.5,
            text_title_mm=3.5,
            min_clearance_mm=2.0,
        )


def test_line_weights_are_ordered() -> None:
    assert A3_LANDSCAPE.line_thin_mm < A3_LANDSCAPE.line_medium_mm < A3_LANDSCAPE.line_thick_mm


def test_text_heights_are_ordered() -> None:
    assert A3_LANDSCAPE.text_small_mm < A3_LANDSCAPE.text_normal_mm < A3_LANDSCAPE.text_title_mm


def standard(**overrides: float) -> GraphicStandard:
    """A3_LANDSCAPE's values with fields replaced, revalidated.

    The two ordering assertions above only read A3_LANDSCAPE, which satisfies
    both branches: nothing exercised the validator's failing path.
    """
    payload: dict[str, float] = {
        "sheet_width_mm": 420.0,
        "sheet_height_mm": 297.0,
        "margin_left_mm": 20.0,
        "margin_right_mm": 10.0,
        "margin_top_mm": 10.0,
        "margin_bottom_mm": 10.0,
        "grid_mm": 2.5,
        "line_thin_mm": 0.18,
        "line_medium_mm": 0.35,
        "line_thick_mm": 0.5,
        "text_small_mm": 1.8,
        "text_normal_mm": 2.5,
        "text_title_mm": 3.5,
        "min_clearance_mm": 2.0,
    }
    payload.update(overrides)
    return GraphicStandard(**payload)


def test_line_weights_out_of_order_are_rejected() -> None:
    with pytest.raises(ValidationError, match="line weights must increase from thin to thick"):
        standard(line_thin_mm=0.5, line_thick_mm=0.18)


def test_text_heights_out_of_order_are_rejected() -> None:
    with pytest.raises(ValidationError, match="text heights must increase from small to title"):
        standard(text_small_mm=3.5, text_title_mm=1.8)


def test_infinite_dimensions_are_rejected() -> None:
    with pytest.raises(ValidationError, match="value must be a finite number"):
        GraphicStandard(
            sheet_width_mm=float("inf"),
            sheet_height_mm=297.0,
            margin_left_mm=20.0,
            margin_right_mm=10.0,
            margin_top_mm=10.0,
            margin_bottom_mm=10.0,
            grid_mm=2.5,
            line_thin_mm=0.18,
            line_medium_mm=0.35,
            line_thick_mm=0.5,
            text_small_mm=1.8,
            text_normal_mm=2.5,
            text_title_mm=3.5,
            min_clearance_mm=2.0,
        )
