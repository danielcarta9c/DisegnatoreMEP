"""Le prove di DRAW-005-R1, blocco C, scritte prima del codice: filtro a Y con
le barrette terminali e il tratto spesso, peso del tratto dichiarato nel
manifesto, serpentina morbida dell'accumulo combinato (I-041, I-045).

La traduzione PM (`docs/pm/2026-09-08-rilievi-po-draw005-r1.md`):

1. il filtro a Y ha le due **barrette terminali** perpendicolari all'asse passante;
   alla scala A3 il tratto medio e' troppo debole: il simbolo dichiara il tratto
   spesso da 0,50 mm, in tavola, in legenda e nel foglio di riscontro;
2. il peso del tratto e' una **proprieta' del manifesto** (`thin`, `medium`,
   `thick`), validata; nel renderer nessuna eccezione per identificativo;
3. il serpentino dell'accumulo combinato resta continuo da `cold_in` a `dhw_out` ma
   diventa una serpentina morbida e centrata, a curve raccordate; porte, riquadro,
   attacchi e grafo non cambiano.

Le prove leggono la libreria pubblicata e il catalogo di prova, e il generatore che
li scrive: nessun identificativo o coordinata della tavola 1 entra come eccezione.
"""

import re
from functools import cache
from pathlib import Path
from xml.etree import ElementTree

import pytest
from pydantic import ValidationError

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics import sheet as sheet_module
from disegnatore_mep.graphics import svg as svg_module
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import Symbol, SymbolRegistry
from disegnatore_mep.graphics.sheet import render_sheet
from disegnatore_mep.graphics.standard import A3_LANDSCAPE, A4_LANDSCAPE
from disegnatore_mep.graphics.svg import render_symbol_sheet
from disegnatore_mep.graphics.symbol import PortFace, StrokeWeight, SymbolManifest
from disegnatore_mep.layout import legend as legend_module
from disegnatore_mep.layout.geometry import LegendEntry, PlacedSymbol, Point, SheetGeometry

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"

HEATING = "heating_water"
TOLERANCE_MM = 1e-6
Pt = tuple[float, float]
Segment = tuple[Pt, Pt]


@cache
def library() -> SymbolRegistry:
    return SymbolRegistry.from_directory(SYMBOLS)


@cache
def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(CATALOG, symbols=library())


def _local(tag: str) -> str:
    return tag.rpartition("}")[2]


def parsed(body: str) -> ElementTree.Element:
    return ElementTree.fromstring(f"<g>{body}</g>")


def _numbers(text: str) -> list[float]:
    return [float(item) for item in re.findall(r"-?\d+(?:\.\d+)?", text)]


def path_commands(d: str) -> list[tuple[str, list[float]]]:
    return [
        (command, _numbers(arguments))
        for command, arguments in re.findall(r"([MLQCAZ])([^MLQCAZ]*)", d)
    ]


def path_vertices(d: str) -> list[Pt]:
    """I vertici di un tracciato assoluto: M, L e il punto d'arrivo di Q, C e A."""
    vertices: list[Pt] = []
    for command, numbers in path_commands(d):
        if command in ("M", "L"):
            vertices.extend(zip(numbers[0::2], numbers[1::2], strict=False))
        elif command in ("Q", "C", "A"):
            vertices.append((numbers[-2], numbers[-1]))
    return vertices


def segments_of(element: ElementTree.Element) -> list[Segment]:
    found: list[Segment] = []
    for item in element.iter():
        tag, get = _local(item.tag), item.get
        if tag == "line":
            found.append(
                (
                    (float(get("x1", "0")), float(get("y1", "0"))),
                    (float(get("x2", "0")), float(get("y2", "0"))),
                )
            )
        elif tag == "path":
            vertices = path_vertices(get("d", ""))
            found.extend(zip(vertices, vertices[1:], strict=False))
    return found


def manifest_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": "prova",
        "version": "1.0.0",
        "name": "Prova",
        "width_mm": 5.0,
        "height_mm": 5.0,
        "allowed_rotations_deg": [0, 90, 180, 270],
        "inline_gap_mm": 5.0,
        "ports": [
            {"id": "a", "face": "left", "x_mm": 0.0, "y_mm": 2.5},
            {"id": "b", "face": "right", "x_mm": 5.0, "y_mm": 2.5},
        ],
        "keep_out": {"left_mm": 2.0, "right_mm": 2.0},
        "source": "prova",
    }
    payload.update(overrides)
    return payload


# ---------------------------------------------------------------------------
# C1 — il peso del tratto e' un dato del manifesto, validato
# ---------------------------------------------------------------------------


def test_il_manifesto_dichiara_il_peso_del_tratto_e_il_valore_sottinteso_e_medio() -> None:
    manifest = SymbolManifest.model_validate(manifest_payload())
    assert manifest.stroke_weight is StrokeWeight.MEDIUM
    for weight in StrokeWeight:
        declared = SymbolManifest.model_validate(manifest_payload(stroke_weight=weight.value))
        assert declared.stroke_weight is weight


def test_un_peso_che_non_esiste_non_si_carica() -> None:
    with pytest.raises(ValidationError):
        SymbolManifest.model_validate(manifest_payload(stroke_weight="bold"))
    with pytest.raises(ValidationError):
        SymbolManifest.model_validate(manifest_payload(stroke_weight=0.5))


def test_il_peso_sopravvive_alla_rotazione() -> None:
    manifest = SymbolManifest.model_validate(manifest_payload(stroke_weight="thick"))
    for degrees in (90, 180, 270):
        assert manifest.rotated(degrees).stroke_weight is StrokeWeight.THICK


def test_lo_standard_traduce_il_peso_in_millimetri_e_il_thick_vale_mezzo_millimetro() -> None:
    for standard in (A3_LANDSCAPE, A4_LANDSCAPE):
        assert standard.line_mm(StrokeWeight.THIN) == standard.line_thin_mm
        assert standard.line_mm(StrokeWeight.MEDIUM) == standard.line_medium_mm
        assert standard.line_mm(StrokeWeight.THICK) == standard.line_thick_mm
    assert A3_LANDSCAPE.line_mm(StrokeWeight.THICK) == 0.50
    assert A3_LANDSCAPE.line_mm(StrokeWeight.MEDIUM) == 0.35


def test_ogni_manifesto_pubblicato_dichiara_il_proprio_peso() -> None:
    for path in sorted(SYMBOLS.glob("*.json")):
        payload = path.read_text(encoding="utf-8")
        assert '"stroke_weight"' in payload, path.name


# ---------------------------------------------------------------------------
# C2 — il filtro a Y: barrette terminali, tratto spesso ovunque
# ---------------------------------------------------------------------------


def _strainers() -> list[Symbol]:
    ids = sorted({item.symbol_id for item in catalog().all() if "filtration" in item.functions})
    assert ids
    return [library().get(symbol_id) for symbol_id in ids]


def _axis_of(symbol: Symbol) -> tuple[float, float, float]:
    """La quota dell'asse passante e le ascisse delle due porte."""
    first, second = symbol.manifest.ports
    assert abs(first.y_mm - second.y_mm) <= TOLERANCE_MM
    return first.y_mm, min(first.x_mm, second.x_mm), max(first.x_mm, second.x_mm)


def _bars(symbol: Symbol) -> list[Segment]:
    """I tratti perpendicolari all'asse che lo attraversano da parte a parte."""
    axis_y, _, _ = _axis_of(symbol)
    return [
        item
        for item in segments_of(parsed(symbol.body))
        if abs(item[0][0] - item[1][0]) <= TOLERANCE_MM
        and min(item[0][1], item[1][1]) < axis_y - TOLERANCE_MM
        and max(item[0][1], item[1][1]) > axis_y + TOLERANCE_MM
    ]


@pytest.mark.parametrize("symbol", _strainers(), ids=lambda item: item.manifest.id)
def test_il_filtro_ha_due_barrette_terminali_perpendicolari_all_asse(symbol: Symbol) -> None:
    axis_y, left, right = _axis_of(symbol)
    bars = _bars(symbol)
    assert len(bars) == 2, bars
    centre = (left + right) / 2
    xs = sorted(bar[0][0] for bar in bars)
    # Una per capo, simmetriche rispetto al centro, e ciascuna a cavallo dell'asse.
    assert xs[0] < centre < xs[1]
    assert abs((xs[0] + xs[1]) / 2 - centre) <= 1e-3
    assert xs[0] <= left + symbol.manifest.width_mm * 0.25 + TOLERANCE_MM
    assert xs[1] >= right - symbol.manifest.width_mm * 0.25 - TOLERANCE_MM
    for bar in bars:
        top, bottom = min(bar[0][1], bar[1][1]), max(bar[0][1], bar[1][1])
        assert abs((axis_y - top) - (bottom - axis_y)) <= 1e-3, bar
        assert top >= -TOLERANCE_MM and bottom <= symbol.manifest.height_mm + TOLERANCE_MM


@pytest.mark.parametrize("symbol", _strainers(), ids=lambda item: item.manifest.id)
def test_il_filtro_dichiara_il_tratto_spesso(symbol: Symbol) -> None:
    assert symbol.manifest.stroke_weight is StrokeWeight.THICK


def _valve() -> Symbol:
    definition = catalog().providing("isolation", HEATING)
    return library().get(definition.symbol_id)


def _placed(symbol: Symbol, component_id: str, x_mm: float) -> PlacedSymbol:
    return PlacedSymbol(
        component_id=component_id,
        symbol_id=symbol.manifest.id,
        rotation_deg=0,
        origin=Point(x_mm=x_mm, y_mm=100.0),
        width_mm=symbol.manifest.width_mm,
        height_mm=symbol.manifest.height_mm,
    )


def _group(root: ElementTree.Element, attribute: str, value: str, css: str) -> ElementTree.Element:
    return next(
        item
        for item in root.iter()
        if _local(item.tag) == "g" and item.get(attribute) == value and item.get("class") == css
    )


def test_in_tavola_il_tratto_di_ogni_simbolo_e_quello_dichiarato() -> None:
    strainer, valve = _strainers()[0], _valve()
    standard = NOVE_C_A3.standard
    sheet = SheetGeometry(
        sheet_id="t",
        title="prova",
        symbols=[_placed(strainer, "filtro", 100.0), _placed(valve, "valvola", 140.0)],
    )
    root = ElementTree.fromstring(render_sheet(sheet, NOVE_C_A3, library()))
    thick = _group(root, "data-component-id", "filtro", "symbol")
    medium = _group(root, "data-component-id", "valvola", "symbol")
    assert float(thick.get("stroke-width", "0")) == standard.line_mm(StrokeWeight.THICK)
    assert float(medium.get("stroke-width", "0")) == standard.line_mm(StrokeWeight.MEDIUM)
    assert float(thick.get("stroke-width", "0")) == 0.50


def test_in_legenda_il_filtro_conserva_il_tratto_spesso() -> None:
    strainer, valve = _strainers()[0], _valve()
    standard = NOVE_C_A3.standard
    band = NOVE_C_A3.legend_rect_mm
    sheet = SheetGeometry(
        sheet_id="t",
        title="prova",
        legend=[
            LegendEntry(
                symbol_id=strainer.manifest.id,
                name=strainer.manifest.name,
                anchor=Point(x_mm=band.x_mm + 2.5, y_mm=band.y_mm + 10.0),
            ),
            LegendEntry(
                symbol_id=valve.manifest.id,
                name=valve.manifest.name,
                anchor=Point(x_mm=band.x_mm + 2.5, y_mm=band.y_mm + 20.0),
            ),
        ],
    )
    root = ElementTree.fromstring(render_sheet(sheet, NOVE_C_A3, library()))
    thick = _group(root, "data-symbol-id", strainer.manifest.id, "legend-symbol")
    scale = float(re.search(r"scale\(([-\d.]+)\)", thick.get("transform", "")).group(1))  # type: ignore[union-attr]
    on_paper = float(thick.get("stroke-width", "0")) * scale
    assert abs(on_paper - standard.line_mm(StrokeWeight.THICK)) <= 1e-9
    ordinary = _group(root, "data-symbol-id", valve.manifest.id, "legend-symbol")
    scale = float(re.search(r"scale\(([-\d.]+)\)", ordinary.get("transform", "")).group(1))  # type: ignore[union-attr]
    assert float(ordinary.get("stroke-width", "0")) * scale < on_paper


def test_nel_foglio_di_riscontro_il_filtro_ha_il_tratto_spesso() -> None:
    """Il foglio di riscontro della libreria intera non entra piu' in una pagina
    (D-096): si riscontra un foglio con i due simboli che contano."""
    strainer, valve = _strainers()[0], _valve()
    root = ElementTree.fromstring(
        render_symbol_sheet(SymbolRegistry([strainer, valve]), A3_LANDSCAPE)
    )
    group = _group(root, "data-symbol-id", strainer.manifest.id, "symbol")
    assert float(group.get("stroke-width", "0")) == A3_LANDSCAPE.line_mm(StrokeWeight.THICK)
    ordinary = _group(root, "data-symbol-id", valve.manifest.id, "symbol")
    assert float(ordinary.get("stroke-width", "0")) == A3_LANDSCAPE.line_mm(StrokeWeight.MEDIUM)


def test_nessun_renderer_conosce_l_identificativo_del_filtro() -> None:
    """Il peso lo dichiara il manifesto: nel renderer non c'e' un'eccezione."""
    for module in (sheet_module, svg_module, legend_module):
        text = Path(module.__file__ or "").read_text(encoding="utf-8").lower()
        assert "strainer" not in text, module.__name__
        assert "filtro" not in text, module.__name__


# ---------------------------------------------------------------------------
# C3 — la serpentina dell'accumulo combinato
# ---------------------------------------------------------------------------


def _combined() -> tuple[Symbol, str, str]:
    """L'accumulo combinato e i due attacchi del serpentino: chi entra freddo e
    chi esce caldo, letti dal catalogo."""
    found = [
        item
        for item in catalog().all()
        if item.stored_medium == HEATING
        and {"cold_water", "domestic_hot_water"} <= {port.medium for port in item.ports}
    ]
    assert len(found) == 1, [item.id for item in found]
    definition = found[0]
    cold = next(port.id for port in definition.ports if port.medium == "cold_water")
    hot = next(port.id for port in definition.ports if port.medium == "domestic_hot_water")
    return library().get(definition.symbol_id), cold, hot


def _coil(symbol: Symbol) -> ElementTree.Element:
    coils = [item for item in parsed(symbol.body).iter() if item.get("class") == "coil"]
    assert len(coils) == 1
    return coils[0]


def _shell(symbol: Symbol) -> tuple[float, float, float, float]:
    rects = [
        tuple(float(item.get(key, "0")) for key in ("x", "y", "width", "height"))
        for item in parsed(symbol.body).iter()
        if _local(item.tag) == "rect"
    ]
    x, y, w, h = max(rects, key=lambda item: item[2] * item[3])
    return (x, y, x + w, y + h)


def test_la_serpentina_e_un_tracciato_solo_dal_freddo_al_caldo() -> None:
    symbol, cold, hot = _combined()
    coil = _coil(symbol)
    assert coil.get("data-from") == cold and coil.get("data-to") == hot
    vertices = path_vertices(coil.get("d", ""))
    first, last = symbol.manifest.port(cold), symbol.manifest.port(hot)
    assert abs(vertices[0][0] - first.x_mm) <= 1e-3 and abs(vertices[0][1] - first.y_mm) <= 1e-3
    assert abs(vertices[-1][0] - last.x_mm) <= 1e-3 and abs(vertices[-1][1] - last.y_mm) <= 1e-3
    commands = path_commands(coil.get("d", ""))
    assert commands[0][0] == "M" and sum(1 for command, _ in commands if command == "M") == 1


def test_la_serpentina_e_morbida_ogni_cambio_di_direzione_e_un_arco() -> None:
    """Nessuno spigolo: due tratti rettilinei consecutivi sono allineati, e fra
    due direzioni diverse c'e' sempre una curva."""
    symbol, _, _ = _combined()
    commands = path_commands(_coil(symbol).get("d", ""))
    arcs = [command for command, _ in commands if command in ("A", "C", "Q")]
    assert len(arcs) >= 5, len(arcs)
    cursor: Pt | None = None
    heading: Pt | None = None
    for command, numbers in commands:
        target = (numbers[-2], numbers[-1])
        if command == "L" and cursor is not None:
            step = (target[0] - cursor[0], target[1] - cursor[1])
            length = max(abs(step[0]), abs(step[1]))
            if length > TOLERANCE_MM:
                direction = (round(step[0] / length, 6), round(step[1] / length, 6))
                if heading is not None:
                    assert direction == heading, (cursor, target, heading)
                heading = direction
        elif command in ("A", "C", "Q"):
            heading = None
        cursor = target


def test_la_serpentina_sta_dentro_il_mantello_ed_e_centrata() -> None:
    symbol, _, _ = _combined()
    shell = _shell(symbol)
    commands = path_commands(_coil(symbol).get("d", ""))
    interior = [
        (numbers[-2], numbers[-1])
        for command, numbers in commands[1:-1]
        if command in ("L", "A", "C", "Q")
    ]
    for point in interior:
        assert shell[0] - 1e-6 <= point[0] <= shell[2] + 1e-6, point
        assert shell[1] - 1e-6 <= point[1] <= shell[3] + 1e-6, point
    turns = [(numbers[-2], numbers[-1]) for command, numbers in commands if command == "A"]
    assert len(turns) >= 4
    # L'ultimo arco e' il raccordo verso l'uscita, che sta dove sta l'attacco:
    # il corpo della serpentina sono le curve di inversione prima di quello.
    body = turns[:-1]
    xs = sorted(point[0] for point in body)
    centre = (shell[0] + shell[2]) / 2
    assert abs((xs[0] + xs[-1]) / 2 - centre) <= 1e-3, (xs, centre)


def test_la_serpentina_gira_abbastanza_da_leggersi_come_tale() -> None:
    symbol, _, _ = _combined()
    commands = path_commands(_coil(symbol).get("d", ""))
    rows = [numbers for command, numbers in commands if command == "L"]
    assert len(rows) >= 6, len(rows)


def test_porte_riquadro_e_attacchi_dell_accumulo_combinato_non_cambiano() -> None:
    """Il segno interno cambia, il contratto esterno no: le stesse nove porte,
    sulle stesse facce e alle stesse quote di DRAW-005."""
    symbol, _, _ = _combined()
    manifest = symbol.manifest
    assert (manifest.width_mm, manifest.height_mm) == (25.0, 45.0)
    assert manifest.allowed_rotations_deg == [0]
    ports = {port.id: (port.face, port.x_mm, port.y_mm) for port in manifest.ports}
    assert ports == {
        "primary_in": (PortFace.LEFT, 0.0, 5.0),
        "primary_out": (PortFace.LEFT, 0.0, 20.0),
        "secondary_out": (PortFace.RIGHT, 25.0, 5.0),
        "secondary_in": (PortFace.RIGHT, 25.0, 20.0),
        "dhw_out": (PortFace.TOP, 7.5, 0.0),
        "cold_in": (PortFace.LEFT, 0.0, 37.5),
        "vent": (PortFace.TOP, 17.5, 0.0),
        "drain": (PortFace.BOTTOM, 12.5, 45.0),
        "probe": (PortFace.RIGHT, 25.0, 32.5),
    }
    # Gli attacchi tecnici entrano ancora nel mantello.
    shell = _shell(symbol)
    segments = segments_of(parsed(symbol.body))
    for port_id in ("primary_in", "primary_out", "secondary_out", "secondary_in", "vent", "drain", "probe"):
        port = manifest.port(port_id)
        at = (port.x_mm, port.y_mm)
        stubs = [item for item in segments if any(abs(end[0] - at[0]) <= 1e-3 and abs(end[1] - at[1]) <= 1e-3 for end in item)]
        assert stubs, port_id
        inner = [item[1] if abs(item[0][0] - at[0]) <= 1e-3 and abs(item[0][1] - at[1]) <= 1e-3 else item[0] for item in stubs]
        assert any(
            shell[0] - 1e-6 <= point[0] <= shell[2] + 1e-6 and shell[1] - 1e-6 <= point[1] <= shell[3] + 1e-6
            for point in inner
        ), port_id
