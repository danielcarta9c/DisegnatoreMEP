from pathlib import Path

import pytest

from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.standard import A3_LANDSCAPE
from disegnatore_mep.graphics.symbol import SymbolManifest
from disegnatore_mep.layout.errors import LayoutError
from disegnatore_mep.layout.grid import GridSpace, assert_symbol_is_aligned

ROOT = Path(__file__).resolve().parents[2]
PUBLISHED = ROOT / "assets" / "symbols"
FIXTURE_SYMBOLS = ROOT / "examples" / "foundation" / "symbols"


def space() -> GridSpace:
    return GridSpace(origin=NOVE_C_A3.drawing_rect_mm)


def test_the_drawing_area_is_a_whole_number_of_cells() -> None:
    assert (space().cols, space().rows) == (140, 94)


def test_millimetres_and_cells_are_each_other_inverse() -> None:
    grid = space()
    for cell in ((0, 0), (1, 3), (140, 94)):
        assert grid.to_cell(*grid.to_mm(cell)) == cell


def test_a_coordinate_between_two_nodes_is_refused() -> None:
    grid = space()
    origin = NOVE_C_A3.drawing_rect_mm
    with pytest.raises(LayoutError, match="not a multiple of the 2.5mm grid step"):
        grid.to_cell(origin.x_mm + 3.0, origin.y_mm)


def test_every_published_symbol_is_on_the_grid() -> None:
    """Senza questo, l'instradamento non raggiunge nessun attacco."""
    for symbol in SymbolRegistry.from_directory(PUBLISHED).all():
        assert_symbol_is_aligned(symbol.manifest)


def test_every_fixture_symbol_is_on_the_grid() -> None:
    for symbol in SymbolRegistry.from_directory(FIXTURE_SYMBOLS).all():
        assert_symbol_is_aligned(symbol.manifest)


def manifest(**overrides: object) -> SymbolManifest:
    payload: dict[str, object] = {
        "id": "probe",
        "version": "1.0.0",
        "name": "Sonda",
        "width_mm": 5.0,
        "height_mm": 5.0,
        "allowed_rotations_deg": [0],
        "ports": [{"id": "a", "face": "left", "x_mm": 0.0, "y_mm": 2.5}],
        "keep_out": {"left_mm": 2.0},
        "source": "CONV-GRAFICA-001",
    }
    payload.update(overrides)
    return SymbolManifest.model_validate(payload)


def test_a_box_off_the_grid_is_named() -> None:
    with pytest.raises(LayoutError, match="symbol probe: width 6mm is not a multiple"):
        assert_symbol_is_aligned(manifest(width_mm=6.0))


def test_a_port_off_the_grid_names_the_port_and_the_axis() -> None:
    off = manifest(
        height_mm=7.5, ports=[{"id": "inlet", "face": "left", "x_mm": 0.0, "y_mm": 3.75}]
    )
    with pytest.raises(LayoutError, match="port inlet: y=3.75mm is not a multiple"):
        assert_symbol_is_aligned(off)


def test_the_message_explains_the_even_step_rule() -> None:
    """Un lato dispari in passi non puo' portare una porta centrata."""
    off = manifest(
        height_mm=7.5, ports=[{"id": "inlet", "face": "left", "x_mm": 0.0, "y_mm": 3.75}]
    )
    with pytest.raises(LayoutError, match="even number of steps"):
        assert_symbol_is_aligned(off)


def test_an_odd_side_is_fine_when_no_port_is_centred_on_it() -> None:
    """7,5 x 5 e' legittimo: le porte stanno a sinistra e a destra, quindi
    centrate sull'altezza, che e' di due passi."""
    assert_symbol_is_aligned(
        manifest(
            width_mm=7.5,
            height_mm=5.0,
            ports=[
                {"id": "a", "face": "left", "x_mm": 0.0, "y_mm": 2.5},
                {"id": "b", "face": "right", "x_mm": 7.5, "y_mm": 2.5},
            ],
            keep_out={"left_mm": 2.0, "right_mm": 2.0},
        )
    )


def test_the_grid_step_comes_from_the_standard() -> None:
    assert space().step_mm == A3_LANDSCAPE.grid_mm
