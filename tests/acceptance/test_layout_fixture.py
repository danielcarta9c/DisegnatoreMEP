"""Il caso D-011 come dato, prima ancora di disegnarlo.

Il progetto e' un file di dati come qualunque altro: nessun ramo del codice lo
riconosce. Queste prove verificano che sia coerente — catalogo, simboli,
topologia, tratte, piano di impaginazione — cosi' che quando il layout
fallira' si sappia che la colpa e' del layout.
"""

from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.cli import main
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.grid import assert_symbol_is_aligned
from disegnatore_mep.layout.partition import partition_project
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.types import BandRole
from disegnatore_mep.validation.topology import validate_project

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def test_the_case_validates_through_the_cli() -> None:
    assert (
        main(
            [
                "validate",
                str(PROJECT),
                "--catalog",
                str(CATALOG),
                "--symbols",
                str(SYMBOLS),
            ]
        )
        == 0
    )


def test_the_case_is_topologically_clean() -> None:
    assert validate_project(load_project(PROJECT), catalog()).ok


def test_the_case_carries_what_d011_describes() -> None:
    """PDC, ACS con deviatrice, bollitore, volano a quattro attacchi,
    circolatore secondario, collettore a due zone e terminali misti."""
    definitions = {
        item.definition_id for item in load_project(PROJECT).components
    }
    assert definitions >= {
        "heat-pump-air-water",
        "diverting-valve-3way",
        "dhw-cylinder",
        "buffer-four-port",
        "pump-circulator",
        "zone-manifold",
        "radiator",
        "underfloor-panel",
    }


def test_every_component_resolves_to_a_symbol() -> None:
    registry = catalog()
    for component in load_project(PROJECT).components:
        resolved = registry.resolve(component.definition_id)
        assert_symbol_is_aligned(resolved.symbol.manifest)


def test_the_inline_accessories_are_the_ones_the_library_says() -> None:
    registry = catalog()
    project = load_project(PROJECT)
    inline = {
        component.id
        for component in project.components
        if registry.resolve(component.definition_id).is_inline
    }
    assert inline == {"strainer", "shutoff", "pump-secondary"}


def test_the_runs_reassemble_and_cover_every_connection() -> None:
    registry = catalog()
    project = load_project(PROJECT)
    inline = frozenset(
        component.id
        for component in project.components
        if registry.resolve(component.definition_id).is_inline
    )
    trunks = build_trunks(project, inline)
    covered = [cid for trunk in trunks for cid in trunk.connection_ids]
    assert sorted(covered) == sorted(item.id for item in project.connections)
    assert len(covered) == len(set(covered))


def test_the_case_fits_one_sheet_and_uses_all_four_bands() -> None:
    project = load_project(PROJECT)
    assert len(project.sheets) == 1
    bands = {item.band for item in project.sheets[0].band_assignments}
    assert bands == set(BandRole)


def test_the_partition_is_a_single_sheet_with_no_cross_references() -> None:
    registry = catalog()
    project = load_project(PROJECT)
    inline = frozenset(
        component.id
        for component in project.components
        if registry.resolve(component.definition_id).is_inline
    )
    parts = partition_project(project, build_trunks(project, inline))
    assert len(parts) == 1
    assert parts[0].links == ()
    assert len(parts[0].component_ids) == len(project.components)


def test_value_tags_exist_for_the_components_that_carry_one() -> None:
    """La legenda dira' cosa e' un volano; il tag dira' quanti litri (D-052)."""
    properties = {
        item.id: item.properties for item in load_project(PROJECT).components
    }
    assert properties["buffer"]["volume_l"] == 200
    assert properties["cylinder"]["volume_l"] == 300
