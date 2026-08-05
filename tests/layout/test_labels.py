from functools import cache
from math import hypot
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import compose_drawing
from disegnatore_mep.layout.geometry import (
    PlacedLabel,
    PlacedSymbol,
    Point,
    RoutedTrunk,
    SheetGeometry,
)
from disegnatore_mep.layout.labels import (
    CHAR_WIDTH_RATIO,
    LEADER_MIN_LENGTH_MM,
    LINE_CLEARANCE_MM,
    TAG_GAP_MM,
    VALUE_GAP_MM,
    format_value,
    place_labels,
    text_width_mm,
)
from disegnatore_mep.layout.partition import partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import ProjectModel

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"

HEIGHT_MM = NOVE_C_A3.standard.text_small_mm
Box = tuple[float, float, float, float]


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def placed_case() -> tuple[ProjectModel, list[PlacedSymbol]]:
    project = load_project(PROJECT)
    registry = catalog()
    inline = frozenset(
        item.id
        for item in project.components
        if registry.resolve(item.definition_id).is_inline
    )
    part = partition_project(project, build_trunks(project, inline))[0]
    return project, place_sheet(project, part, registry, NOVE_C_A3, inline)


def labels() -> list[PlacedLabel]:
    project, placed = placed_case()
    return place_labels(project, placed, NOVE_C_A3.standard)


@cache
def fixture_sheet() -> SheetGeometry:
    """Il caso di accettazione instradato, composto una volta per modulo.

    Serve per misurare le etichette **sulla tavola vera**, con le sue tubazioni:
    una prova su simboli soli non vedrebbe mai una collisione con una linea.
    """
    return compose_drawing(load_project(PROJECT), catalog(), NOVE_C_A3).sheets[0]


def fixture_labels() -> list[PlacedLabel]:
    sheet = fixture_sheet()
    return place_labels(
        load_project(PROJECT), sheet.symbols, NOVE_C_A3.standard, routes=sheet.routes
    )


def symbol(
    component_id: str,
    x_mm: float,
    y_mm: float,
    tag: str | None = None,
    width_mm: float = 10.0,
    height_mm: float = 10.0,
) -> PlacedSymbol:
    return PlacedSymbol(
        component_id=component_id,
        symbol_id="prova",
        rotation_deg=0,
        origin=Point(x_mm=x_mm, y_mm=y_mm),
        width_mm=width_mm,
        height_mm=height_mm,
        tag=tag,
    )


def run(*points: tuple[float, float]) -> RoutedTrunk:
    return RoutedTrunk(
        network_id="n1",
        medium="heating_water",
        segments=[[Point(x_mm=x, y_mm=y) for x, y in points]],
    )


def label_box(item: PlacedLabel) -> Box:
    width = text_width_mm(item.text, HEIGHT_MM)
    return (
        item.anchor.x_mm,
        item.anchor.y_mm - HEIGHT_MM,
        item.anchor.x_mm + width,
        item.anchor.y_mm,
    )


def symbol_box(item: PlacedSymbol) -> Box:
    return (item.origin.x_mm, item.origin.y_mm, item.right_mm, item.bottom_mm)


def line_boxes(routes: list[RoutedTrunk]) -> list[Box]:
    """I tratti come riquadri, con il franco che le etichette devono lasciare."""
    return [
        (
            min(before.x_mm, after.x_mm) - LINE_CLEARANCE_MM,
            min(before.y_mm, after.y_mm) - LINE_CLEARANCE_MM,
            max(before.x_mm, after.x_mm) + LINE_CLEARANCE_MM,
            max(before.y_mm, after.y_mm) + LINE_CLEARANCE_MM,
        )
        for route in routes
        for segment in route.segments
        for before, after in zip(segment, segment[1:], strict=False)
    ]


def apart(first: Box, second: Box) -> bool:
    return (
        first[2] <= second[0]
        or second[2] <= first[0]
        or first[3] <= second[1]
        or second[3] <= first[1]
    )


def test_a_component_with_a_tag_gets_one() -> None:
    texts = {item.text for item in labels()}
    assert "PDC-01" in texts
    assert "VOL-01" in texts


def test_a_component_without_a_tag_gets_none_invented() -> None:
    project, placed = placed_case()
    untagged = {item.id for item in project.components if item.tag is None}
    ids = {item.id for item in place_labels(project, placed, NOVE_C_A3.standard)}
    for component_id in untagged:
        assert f"{component_id}-tag" not in ids


def test_a_value_tag_carries_its_unit() -> None:
    """La legenda dira' cosa e' un volano, il tag dice quanti litri (D-052)."""
    texts = {item.text for item in labels()}
    assert "200 l" in texts
    assert "300 l" in texts


def test_a_property_without_a_known_unit_is_not_printed() -> None:
    assert format_value("colour", "red") is None
    assert format_value("volume_l", None) is None


def test_a_decimal_value_uses_the_italian_comma() -> None:
    assert format_value("flow_rate_m3h", 1.2) == "1,2 m³/h"


def test_a_diameter_reads_as_a_nominal_size() -> None:
    assert format_value("diameter_dn", 32) == "DN32"


def test_no_label_collides_with_a_symbol_or_another_label() -> None:
    _, placed = placed_case()
    boxes = [symbol_box(item) for item in placed]
    for label in labels():
        box = label_box(label)
        for other in boxes:
            assert apart(box, other), (label.text, other)
        boxes.append(box)


def test_the_width_estimate_is_the_declared_one() -> None:
    assert text_width_mm("PDC-01", HEIGHT_MM) == 6 * HEIGHT_MM * CHAR_WIDTH_RATIO


def test_the_labels_are_deterministic() -> None:
    first = [(item.id, item.anchor.x_mm, item.anchor.y_mm) for item in labels()]
    second = [(item.id, item.anchor.x_mm, item.anchor.y_mm) for item in labels()]
    assert first == second


def test_every_label_declares_its_role() -> None:
    assert {item.role for item in labels()} <= {"tag", "data"}
