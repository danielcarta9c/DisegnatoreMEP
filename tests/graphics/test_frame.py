import pytest
from pydantic import ValidationError

from disegnatore_mep.graphics.frame import (
    LEGEND_WIDTH_MM,
    NOVE_C_A3,
    SheetFrame,
)
from disegnatore_mep.graphics.standard import A3_LANDSCAPE


def areas() -> dict[str, object]:
    return {
        "intestazione": NOVE_C_A3.header_rect_mm,
        "corpo": NOVE_C_A3.body_rect_mm,
        "cartiglio": NOVE_C_A3.title_block_rect_mm,
    }


def test_the_border_matches_the_supplied_title_block() -> None:
    """Misurato su assets/cartigli/Cartiglio_NoveC_A3.pdf: 10 mm sui quattro lati."""
    border = NOVE_C_A3.border_rect_mm
    assert (border.x_mm, border.y_mm) == (10.0, 10.0)
    assert (border.width_mm, border.height_mm) == (400.0, 277.0)


def test_the_body_sits_between_the_header_and_the_title_block() -> None:
    body = NOVE_C_A3.body_rect_mm
    assert (body.width_mm, body.height_mm) == (400.0, 235.0)
    assert body.y_mm == NOVE_C_A3.header_rect_mm.bottom_mm
    assert body.bottom_mm == NOVE_C_A3.title_block_rect_mm.y_mm


def test_the_legend_band_is_on_the_right_and_as_tall_as_the_body() -> None:
    """D-052: la legenda sta sul lato destro, una volta sola per tavola."""
    legend, body = NOVE_C_A3.legend_rect_mm, NOVE_C_A3.body_rect_mm
    assert legend.width_mm == LEGEND_WIDTH_MM
    assert legend.right_mm == body.right_mm
    assert (legend.y_mm, legend.height_mm) == (body.y_mm, body.height_mm)


def test_the_drawing_area_is_the_body_minus_the_legend() -> None:
    drawing = NOVE_C_A3.drawing_rect_mm
    assert (drawing.width_mm, drawing.height_mm) == (350.0, 235.0)
    assert drawing.x_mm == NOVE_C_A3.body_rect_mm.x_mm
    assert drawing.right_mm == NOVE_C_A3.legend_rect_mm.x_mm


def test_both_axes_of_the_drawing_area_are_whole_grid_steps() -> None:
    """E' cio' da cui dipende l'instradamento: una rotta puo' finire solo su un
    nodo, quindi l'area su cui si instrada deve esserne un multiplo esatto."""
    grid = A3_LANDSCAPE.grid_mm
    drawing = NOVE_C_A3.drawing_rect_mm
    assert drawing.width_mm / grid == 140
    assert drawing.height_mm / grid == 94


def test_the_title_block_reserve_matches_the_measured_band() -> None:
    block = NOVE_C_A3.title_block_rect_mm
    assert block.height_mm == 36.0
    assert block.width_mm == NOVE_C_A3.border_rect_mm.width_mm
    assert block.bottom_mm == NOVE_C_A3.border_rect_mm.bottom_mm


def test_the_four_areas_do_not_overlap_and_stay_inside_the_border() -> None:
    regions = [
        NOVE_C_A3.header_rect_mm,
        NOVE_C_A3.drawing_rect_mm,
        NOVE_C_A3.legend_rect_mm,
        NOVE_C_A3.title_block_rect_mm,
    ]
    for region in regions:
        assert NOVE_C_A3.border_rect_mm.contains(region), region
    for index, first in enumerate(regions):
        for second in regions[index + 1 :]:
            assert not first.overlaps(second), (first, second)


def test_a_frame_whose_bands_do_not_fit_is_refused() -> None:
    with pytest.raises(ValidationError, match="leave no drawing area"):
        SheetFrame(
            standard=A3_LANDSCAPE,
            header_height_mm=150.0,
            title_block_height_mm=150.0,
            legend_width_mm=50.0,
        )


def test_a_legend_wider_than_the_body_is_refused() -> None:
    with pytest.raises(ValidationError, match="legend band"):
        SheetFrame(
            standard=A3_LANDSCAPE,
            header_height_mm=6.0,
            title_block_height_mm=36.0,
            legend_width_mm=500.0,
        )


def test_the_frame_derives_the_paper_from_the_standard() -> None:
    """Il telaio non ridichiara le grandezze della carta: le legge da
    GraphicStandard, che resta l'unica autorita' (D-046)."""
    assert NOVE_C_A3.standard is A3_LANDSCAPE
    assert NOVE_C_A3.border_rect_mm.width_mm == A3_LANDSCAPE.usable_width_mm
    assert NOVE_C_A3.border_rect_mm.height_mm == A3_LANDSCAPE.usable_height_mm


def test_a_rect_knows_its_own_edges() -> None:
    from disegnatore_mep.graphics.frame import Rect

    rect = Rect(x_mm=10.0, y_mm=20.0, width_mm=30.0, height_mm=40.0)
    assert (rect.right_mm, rect.bottom_mm) == (40.0, 60.0)
    assert rect.contains(Rect(x_mm=10.0, y_mm=20.0, width_mm=1.0, height_mm=1.0))
    assert not rect.contains(Rect(x_mm=9.0, y_mm=20.0, width_mm=1.0, height_mm=1.0))
    assert rect.overlaps(Rect(x_mm=39.0, y_mm=59.0, width_mm=5.0, height_mm=5.0))
    # Due rettangoli che si toccano sul bordo non si sovrappongono: e' il caso
    # del corpo e del cartiglio, contigui per costruzione.
    assert not rect.overlaps(Rect(x_mm=40.0, y_mm=20.0, width_mm=5.0, height_mm=5.0))
