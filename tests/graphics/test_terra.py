"""La linea di terra non esiste piu' sulla tavola (D-121, I-024, DRAW-003).

Il PO: «non l'ho mai voluta e Claude continua a metterla». D-121 era stata
attuata solo sul routing: le tubazioni potevano attraversare la quota di terra,
ma il renderer continuava a disegnare una linea continua con il tratteggio del
pavimento. Qui si prova sul **risultato SVG** che nessun percorso di rendering
la reintroduca: ne' il gruppo dedicato, ne' una linea orizzontale che
attraversi l'area di disegno, ne' una fila di trattini.

La quota interna di posa puo' restare come riferimento di allineamento delle
macchine appoggiate; non e' una primitiva grafica.
"""

import re
from functools import cache
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3, SheetFrame
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import render_sheet
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import compose_drawing
from disegnatore_mep.layout.geometry import (
    PlacedSymbol,
    Point,
    RoutedTrunk,
    SheetGeometry,
)

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"

_LINE = re.compile(r"<line\b([^>]*)/?>")
_ATTRIBUTE = re.compile(r'(\w+)="([^"]*)"')


@cache
def symbols() -> SymbolRegistry:
    return SymbolRegistry.from_directory(SYMBOLS)


def _outside_symbols(svg: str) -> str:
    """L'SVG senza i corpi dei simboli: un segno corto di appoggio dentro un
    simbolo e' ammesso, e non deve confondere la misura."""
    return re.sub(r'<g class="symbol"[^>]*>.*?</g>', "", svg, flags=re.DOTALL)


def continuous_ground_lines(svg: str, frame: SheetFrame) -> list[str]:
    """Le linee orizzontali che attraversano l'area di disegno da parte a parte."""
    area = frame.drawing_rect_mm
    found: list[str] = []
    for match in _LINE.finditer(_outside_symbols(svg)):
        attributes = dict(_ATTRIBUTE.findall(match.group(1)))
        try:
            x1, y1 = float(attributes["x1"]), float(attributes["y1"])
            x2, y2 = float(attributes["x2"]), float(attributes["y2"])
        except (KeyError, ValueError):
            continue
        horizontal = abs(y1 - y2) <= 1e-6
        spans_the_area = abs(x2 - x1) >= area.width_mm * 0.9
        inside = area.y_mm <= y1 <= area.bottom_mm
        if horizontal and spans_the_area and inside:
            found.append(match.group(0))
    return found


def hatch_rows(svg: str) -> int:
    """Quante file di trattini obliqui uguali e ravvicinati: il pavimento."""
    slanted = [
        dict(_ATTRIBUTE.findall(match.group(1)))
        for match in _LINE.finditer(_outside_symbols(svg))
    ]
    rows: dict[float, int] = {}
    for item in slanted:
        try:
            x1, y1 = float(item["x1"]), float(item["y1"])
            x2, y2 = float(item["x2"]), float(item["y2"])
        except (KeyError, ValueError):
            continue
        if abs(x1 - x2) > 1e-6 and abs(y1 - y2) > 1e-6:
            rows[y1] = rows.get(y1, 0) + 1
    return sum(1 for count in rows.values() if count >= 10)


def _hand_made_sheet() -> SheetGeometry:
    """Una tavola costruita a mano che dichiara ancora una quota di terra.

    E' il caso che il rendering deve ignorare: una geometria vecchia, o
    un'altra strada della catena, puo' portare la quota; la tavola non la
    disegna comunque.
    """
    return SheetGeometry(
        sheet_id="t1",
        title="Prova",
        symbols=[
            PlacedSymbol(
                component_id="hp",
                symbol_id="heat-pump-air-water",
                rotation_deg=0,
                origin=Point(x_mm=50.0, y_mm=120.0),
                width_mm=40.0,
                height_mm=30.0,
            )
        ],
        routes=[
            RoutedTrunk(
                network_id="n",
                medium="heating_water",
                segments=[[Point(x_mm=90.0, y_mm=125.0), Point(x_mm=140.0, y_mm=125.0)]],
            )
        ],
        ground_line_y_mm=150.0,
    )


def test_nessuna_linea_continua_di_terra_nell_svg_di_una_tavola_a_mano() -> None:
    svg = render_sheet(_hand_made_sheet(), NOVE_C_A3, symbols())
    assert 'class="ground"' not in svg
    assert continuous_ground_lines(svg, NOVE_C_A3) == []
    assert hatch_rows(svg) == 0


def test_nessuna_linea_continua_di_terra_nella_tavola_composta() -> None:
    registry = ComponentRegistry.from_directory(CATALOG, symbols=symbols())
    drawn = compose_drawing(load_project(PROJECT), registry, NOVE_C_A3)
    svg = render_sheet(drawn.sheets[0], NOVE_C_A3, symbols())
    assert 'class="ground"' not in svg
    assert continuous_ground_lines(svg, NOVE_C_A3) == []
    assert hatch_rows(svg) == 0
    # La geometria consegnata non porta la quota come elemento della tavola.
    assert drawn.sheets[0].ground_line_y_mm is None


def test_la_squadratura_e_le_fasce_restano() -> None:
    """La misura non prende per terra la cornice del foglio: quella resta."""
    svg = render_sheet(_hand_made_sheet(), NOVE_C_A3, symbols())
    assert svg.count("<rect") >= 3
