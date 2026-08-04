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
from disegnatore_mep.layout.compose import compose_on_ordinary_frame
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
    """Il caso D-011 non e' un disegno piccolo: l'A4 non lo regge."""
    frame, drawing = compose_on_ordinary_frame(load_project(PROJECT), catalog())
    assert frame == NOVE_C_A3
    assert drawing.sheets


def test_the_smaller_format_is_tried_first() -> None:
    with pytest.raises(LayoutError):
        compose_on_ordinary_frame(load_project(PROJECT), catalog(), (NOVE_C_A4,))


def test_nothing_larger_than_the_a3_is_offered() -> None:
    """Niente A0, niente strisce: sopra l'A3 si divide in piu' tavole (D-056)."""
    with pytest.raises(LayoutError, match="does not fit on any ordinary sheet format"):
        compose_on_ordinary_frame(load_project(PROJECT), catalog(), ())
