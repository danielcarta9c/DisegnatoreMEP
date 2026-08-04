from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.errors import LayoutError
from disegnatore_mep.layout.geometry import PlacedSymbol, Point, RoutedTrunk
from disegnatore_mep.layout.grid import GridSpace
from disegnatore_mep.layout.inline import place_inline_accessories
from disegnatore_mep.layout.partition import partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.route import route_sheet
from disegnatore_mep.layout.trunks import Trunk, build_trunks
from disegnatore_mep.model.project import ProjectModel

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def grid() -> GridSpace:
    return GridSpace(origin=NOVE_C_A3.drawing_rect_mm, standard=NOVE_C_A3.standard)


def routed_case() -> tuple[ProjectModel, list[Trunk], list[RoutedTrunk], list[PlacedSymbol]]:
    project = load_project(PROJECT)
    registry = catalog()
    inline = frozenset(
        item.id
        for item in project.components
        if registry.resolve(item.definition_id).is_inline
    )
    trunks = build_trunks(project, inline)
    part = partition_project(project, trunks)[0]
    placed = place_sheet(project, part, registry, NOVE_C_A3, inline)
    routes = route_sheet(project, list(part.trunks), placed, registry, grid())
    return project, list(part.trunks), routes, placed


def with_accessories() -> list[tuple[Trunk, list[list[Point]], list[PlacedSymbol]]]:
    project, trunks, routes, _ = routed_case()
    registry, space = catalog(), grid()
    out = []
    for trunk, routed in zip(trunks, routes, strict=True):
        if not trunk.inline_component_ids:
            continue
        accessories, broken = place_inline_accessories(
            project, trunk, routed, registry, space
        )
        out.append((trunk, broken.segments, accessories))
    return out


def test_every_inline_accessory_of_the_case_is_placed() -> None:
    placed = {
        item.component_id for _, _, items in with_accessories() for item in items
    }
    assert placed == {"strainer", "shutoff", "pump-secondary"}


def test_an_accessory_sits_on_its_own_run() -> None:
    for trunk, broken, accessories in with_accessories():
        for accessory in accessories:
            centre = Point(
                x_mm=accessory.origin.x_mm + accessory.width_mm / 2,
                y_mm=accessory.origin.y_mm + accessory.height_mm / 2,
            )
            ends = [point for segment in broken for point in (segment[0], segment[-1])]
            assert any(
                abs(point.x_mm - centre.x_mm) + abs(point.y_mm - centre.y_mm)
                <= accessory.width_mm / 2 + accessory.height_mm / 2 + 1e-9
                for point in ends
            ), trunk.connection_ids


def test_the_line_is_broken_not_covered() -> None:
    """D-027: nessuna linea continua passa sotto un componente in linea."""
    for _, broken, accessories in with_accessories():
        assert len(broken) == len(accessories) + 1
        for accessory in accessories:
            for segment in broken:
                for before, after in zip(segment, segment[1:], strict=False):
                    crosses_x = (
                        accessory.origin.x_mm < min(before.x_mm, after.x_mm)
                        and max(before.x_mm, after.x_mm) < accessory.right_mm
                    )
                    crosses_y = (
                        accessory.origin.y_mm < min(before.y_mm, after.y_mm)
                        and max(before.y_mm, after.y_mm) < accessory.bottom_mm
                    )
                    assert not (crosses_x and crosses_y)


def test_the_break_is_as_long_as_the_declared_gap() -> None:
    registry = catalog()
    project, trunks, routes, _ = routed_case()
    definitions = {item.id: item.definition_id for item in project.components}
    for trunk, routed in zip(trunks, routes, strict=True):
        if len(trunk.inline_component_ids) != 1:
            continue
        gap = registry.resolve(
            definitions[trunk.inline_component_ids[0]]
        ).symbol.manifest.inline_gap_mm
        assert gap is not None
        _, broken = place_inline_accessories(project, trunk, routed, registry, grid())
        head, tail = broken.segments[0][-1], broken.segments[1][0]
        measured = abs(tail.x_mm - head.x_mm) + abs(tail.y_mm - head.y_mm)
        assert measured == pytest.approx(gap)


def test_the_rotation_follows_the_run_and_is_allowed() -> None:
    registry = catalog()
    project, _, _, _ = routed_case()
    definitions = {item.id: item.definition_id for item in project.components}
    for _, _, accessories in with_accessories():
        for accessory in accessories:
            manifest = registry.resolve(
                definitions[accessory.component_id]
            ).symbol.manifest
            assert accessory.rotation_deg in manifest.allowed_rotations_deg
            assert accessory.rotation_deg in (0, 90)


def test_an_accessory_centre_lands_on_a_grid_node() -> None:
    space = grid()
    for _, _, accessories in with_accessories():
        for accessory in accessories:
            space.to_cell(
                accessory.origin.x_mm + accessory.width_mm / 2,
                accessory.origin.y_mm + accessory.height_mm / 2,
            )


def test_a_run_too_short_for_its_accessories_fails_with_a_diagnostic() -> None:
    project, trunks, routes, _ = routed_case()
    trunk = next(item for item in trunks if item.inline_component_ids)
    routed = RoutedTrunk(
        network_id=trunk.network_id,
        connection_ids=list(trunk.connection_ids),
        segments=[[Point(x_mm=10.0, y_mm=20.0), Point(x_mm=12.0, y_mm=20.0)]],
    )
    with pytest.raises(LayoutError, match="never shrunk|need"):
        place_inline_accessories(project, trunk, routed, catalog(), grid())


def test_a_run_without_accessories_is_returned_untouched() -> None:
    project, trunks, routes, _ = routed_case()
    for trunk, routed in zip(trunks, routes, strict=True):
        if trunk.inline_component_ids:
            continue
        accessories, unchanged = place_inline_accessories(
            project, trunk, routed, catalog(), grid()
        )
        assert accessories == []
        assert unchanged is routed


def test_the_accessory_keeps_its_tag() -> None:
    tags = {
        item.component_id: item.tag
        for _, _, items in with_accessories()
        for item in items
    }
    assert tags["strainer"] == "FIL-01"
    assert tags["pump-secondary"] == "CIR-02"
