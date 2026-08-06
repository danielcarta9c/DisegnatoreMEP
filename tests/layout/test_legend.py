from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.errors import LayoutError
from disegnatore_mep.layout.geometry import LegendEntry, NetworkKey, PlacedSymbol
from disegnatore_mep.layout.inline import place_inline_accessories
from disegnatore_mep.layout.labels import place_labels
from disegnatore_mep.layout.legend import build_legend, style_for
from disegnatore_mep.layout.partition import partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.route import route_sheet
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import ProjectModel

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def drawn() -> tuple[ProjectModel, list[PlacedSymbol], tuple[str, ...]]:
    from disegnatore_mep.layout.grid import GridSpace

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
    grid = GridSpace(origin=NOVE_C_A3.drawing_rect_mm, standard=NOVE_C_A3.standard)
    routes = route_sheet(project, list(part.trunks), placed, registry, grid)
    for trunk, routed in zip(part.trunks, routes, strict=True):
        extra, _ = place_inline_accessories(project, trunk, routed, registry, grid)
        placed.extend(extra)
    return project, placed, part.network_ids


def legend() -> tuple[list[LegendEntry], list[NetworkKey]]:
    project, placed, networks = drawn()
    return build_legend(project, placed, networks, catalog(), NOVE_C_A3)


def test_the_legend_lists_only_the_symbols_actually_used() -> None:
    entries, _ = legend()
    library = {item.manifest.id for item in SymbolRegistry.from_directory(SYMBOLS).all()}
    listed = {item.symbol_id for item in entries}
    assert listed < library
    assert "air-diffuser" not in listed
    assert "heat-pump-air-water" in listed


def test_a_symbol_used_many_times_appears_once() -> None:
    entries, _ = legend()
    ids = [item.symbol_id for item in entries]
    assert len(ids) == len(set(ids))


def test_the_legend_speaks_italian() -> None:
    """D-051: sulla tavola si legge la denominazione, mai l'identificativo."""
    entries, _ = legend()
    names = {item.name for item in entries}
    assert "Pompa di calore aria-acqua" in names
    assert "Volano termico a quattro attacchi" in names
    for item in entries:
        assert item.name != item.symbol_id


def test_no_label_in_the_drawing_repeats_a_legend_entry() -> None:
    """La prova che rende vera la divisione dei ruoli di D-052."""
    project, placed, _ = drawn()
    entries, _ = legend()
    denominations = {item.name for item in entries}
    for label in place_labels(project, placed, NOVE_C_A3.standard):
        assert label.text not in denominations


def test_the_legend_sits_inside_its_own_band() -> None:
    band = NOVE_C_A3.legend_rect_mm
    entries, keys = legend()
    anchors = [item.anchor for item in entries] + [item.anchor for item in keys]
    for anchor in anchors:
        assert band.x_mm <= anchor.x_mm <= band.right_mm
        assert band.y_mm <= anchor.y_mm <= band.bottom_mm


def test_the_fluid_section_carries_colour_and_dash() -> None:
    """D-057: colore e tratto, cosi' la tavola regge la fotocopia."""
    _, keys = legend()
    assert keys
    for item in keys:
        assert item.colour.startswith("#")
        assert item.dash


def test_two_hydronic_media_are_told_apart() -> None:
    """La chiave e' il fluido, non il dominio: caldo e freddo sono entrambi
    idronici e devono distinguersi."""
    assert style_for("heating_water") != style_for("chilled_water")


def test_supply_and_return_of_one_fluid_are_told_apart() -> None:
    assert style_for("heating_water", supply=True) != style_for(
        "heating_water", supply=False
    )


def test_an_unknown_medium_falls_back_to_black() -> None:
    assert style_for("something_new") == ("#111111", "none")
    assert style_for("something_new", supply=False)[0] == "#5d6d7e"


def test_the_order_is_stable() -> None:
    first, _ = legend()
    second, _ = legend()
    assert [item.symbol_id for item in first] == [item.symbol_id for item in second]


def test_a_legend_taller_than_its_band_fails_with_a_diagnostic() -> None:
    """Il testo non si rimpicciolisce per farlo stare (ADR 0003)."""
    project, placed, networks = drawn()
    narrow = NOVE_C_A3.model_copy(update={"title_block_height_mm": 200.0})
    with pytest.raises(LayoutError, match="never shrunk|legend needs"):
        build_legend(project, placed, networks, catalog(), narrow)


def test_a_fluid_gets_one_row_for_supply_and_one_for_return() -> None:
    """Su una tavola vera mandata e ritorno sono due linee: la legenda tubazioni
    le elenca separate. Primario e secondario, che portano lo stesso fluido,
    condividono invece la stessa coppia di righe."""
    _, keys = legend()
    assert [item.medium for item in keys] == ["heating_water", "heating_water"]
    assert [item.name for item in keys] == [
        "Acqua di riscaldamento — andata",
        "Acqua di riscaldamento — ritorno",
    ]
    assert keys[0].colour != keys[1].colour


def test_the_fluid_row_speaks_italian_or_falls_back_to_the_network_name() -> None:
    from disegnatore_mep.layout.legend import MEDIUM_NAMES

    assert MEDIUM_NAMES["chilled_water"] == "Acqua refrigerata"
    assert "something_new" not in MEDIUM_NAMES
