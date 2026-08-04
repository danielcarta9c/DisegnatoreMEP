"""Il formato si sceglie provando, non stimando (D-058).

A3 orizzontale, o A4 se il disegno e' proprio piccolo. Non esiste un criterio
di «piccolo» da valutare a priori: la prova **e'** il criterio, perche' il
posizionamento fallisce esattamente quando il contenuto non entra alla scala
fissa e ADR 0003 vieta di rimpicciolire i simboli per farceli stare.
"""

from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3, NOVE_C_A4
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import (
    compose_drawing,
    compose_on_ordinary_frame,
    fits_comfortably,
)
from disegnatore_mep.layout.errors import LayoutError

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def test_a_central_plant_lands_on_the_a3() -> None:
    """Il caso D-011 non e' un disegno piccolo: sull'A4 ci starebbe a filo."""
    frame, drawing = compose_on_ordinary_frame(load_project(PROJECT), catalog())
    assert frame == NOVE_C_A3
    assert drawing.sheets


def test_fitting_edge_to_edge_is_not_being_small() -> None:
    """Sull'A4 il caso entra, e occupa piu' del limite: quindi non lo prende."""
    on_a4 = compose_drawing(load_project(PROJECT), catalog(), NOVE_C_A4).sheets[0]
    assert not fits_comfortably(on_a4, NOVE_C_A4.drawing_rect_mm)
    assert fits_comfortably(
        compose_drawing(load_project(PROJECT), catalog(), NOVE_C_A3).sheets[0],
        NOVE_C_A3.drawing_rect_mm,
    )


def test_the_last_format_is_taken_even_if_the_drawing_fills_it() -> None:
    """L'A3 e' il formato ordinario: sopra non si sale, si divide (D-056)."""
    frame, _ = compose_on_ordinary_frame(load_project(PROJECT), catalog(), (NOVE_C_A4,))
    assert frame == NOVE_C_A4


def test_nothing_larger_than_the_a3_is_offered() -> None:
    """Niente A0, niente strisce: sopra l'A3 si divide in piu' tavole (D-056)."""
    with pytest.raises(LayoutError, match="does not fit on any ordinary sheet format"):
        compose_on_ordinary_frame(load_project(PROJECT), catalog(), ())
