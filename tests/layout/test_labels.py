from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.geometry import PlacedLabel, PlacedSymbol
from disegnatore_mep.layout.labels import CHAR_WIDTH_RATIO, format_value, place_labels
from disegnatore_mep.layout.partition import partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import ProjectModel

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"


def placed_case() -> tuple[ProjectModel, list[PlacedSymbol]]:
    project = load_project(PROJECT)
    registry = ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
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
    height = NOVE_C_A3.standard.text_small_mm
    boxes = [
        (item.origin.x_mm, item.origin.y_mm, item.right_mm, item.bottom_mm)
        for item in placed
    ]
    for label in labels():
        width = len(label.text) * height * CHAR_WIDTH_RATIO
        box = (
            label.anchor.x_mm,
            label.anchor.y_mm - height,
            label.anchor.x_mm + width,
            label.anchor.y_mm,
        )
        for other in boxes:
            apart = (
                box[2] <= other[0]
                or other[2] <= box[0]
                or box[3] <= other[1]
                or other[3] <= box[1]
            )
            assert apart, (label.text, other)
        boxes.append(box)


def test_the_labels_are_deterministic() -> None:
    first = [(item.id, item.anchor.x_mm, item.anchor.y_mm) for item in labels()]
    second = [(item.id, item.anchor.x_mm, item.anchor.y_mm) for item in labels()]
    assert first == second


def test_every_label_declares_its_role() -> None:
    assert {item.role for item in labels()} <= {"tag", "data"}
