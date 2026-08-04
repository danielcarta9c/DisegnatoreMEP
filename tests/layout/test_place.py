import os
import subprocess
import sys
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.errors import LayoutError
from disegnatore_mep.layout.geometry import PlacedSymbol
from disegnatore_mep.layout.grid import GridSpace
from disegnatore_mep.layout.partition import partition_project
from disegnatore_mep.layout.place import place_sheet
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


def inline_ids(project: ProjectModel, registry: ComponentRegistry) -> frozenset[str]:
    return frozenset(
        item.id
        for item in project.components
        if registry.resolve(item.definition_id).is_inline
    )


def placed_case() -> list[PlacedSymbol]:
    project = load_project(PROJECT)
    registry = catalog()
    inline = inline_ids(project, registry)
    part = partition_project(project, build_trunks(project, inline))[0]
    return place_sheet(project, part, registry, NOVE_C_A3, inline)


def test_generation_is_left_and_terminals_are_right() -> None:
    """D-041: i generatori a sinistra, la distribuzione a destra."""
    placed = {item.component_id: item for item in placed_case()}
    assert placed["hp"].origin.x_mm < placed["buffer"].origin.x_mm
    assert placed["buffer"].origin.x_mm < placed["manifold"].origin.x_mm
    assert placed["manifold"].origin.x_mm < placed["radiators"].origin.x_mm


def test_every_symbol_lands_on_a_grid_node() -> None:
    grid = GridSpace(origin=NOVE_C_A3.drawing_rect_mm)
    for item in placed_case():
        grid.to_cell(item.origin.x_mm, item.origin.y_mm)  # solleva se fuori griglia


def test_nothing_leaves_the_drawing_area() -> None:
    """Niente entra nella legenda, nell'intestazione o nel cartiglio."""
    area = NOVE_C_A3.drawing_rect_mm
    for item in placed_case():
        assert item.origin.x_mm >= area.x_mm
        assert item.origin.y_mm >= area.y_mm
        assert item.right_mm <= area.right_mm + 1e-9
        assert item.bottom_mm <= area.bottom_mm + 1e-9


def test_no_two_symbols_overlap() -> None:
    items = placed_case()
    for index, first in enumerate(items):
        for second in items[index + 1 :]:
            apart = (
                first.right_mm <= second.origin.x_mm + 1e-9
                or second.right_mm <= first.origin.x_mm + 1e-9
                or first.bottom_mm <= second.origin.y_mm + 1e-9
                or second.bottom_mm <= first.origin.y_mm + 1e-9
            )
            assert apart, (first.component_id, second.component_id)


def test_inline_accessories_are_not_placed_here() -> None:
    """Un accessorio in linea sta sulla tratta, non e' un nodo del disegno."""
    placed = {item.component_id for item in placed_case()}
    assert "strainer" not in placed
    assert "shutoff" not in placed
    assert "pump-secondary" not in placed


def test_every_rotation_is_one_the_symbol_allows() -> None:
    registry = catalog()
    project = load_project(PROJECT)
    definitions = {item.id: item.definition_id for item in project.components}
    for item in placed_case():
        manifest = registry.resolve(definitions[item.component_id]).symbol.manifest
        assert item.rotation_deg in manifest.allowed_rotations_deg


def test_the_tag_travels_with_the_symbol() -> None:
    placed = {item.component_id: item for item in placed_case()}
    assert placed["hp"].tag == "PDC-01"
    assert placed["buffer"].tag == "VOL-01"


def test_the_pagination_plan_decides_the_bands() -> None:
    """Stesso modello, piano diverso, tavola diversa: e' cio' che rende utile
    registrare il piano invece di lasciarlo al motore (D-042)."""
    project = load_project(PROJECT)
    registry = catalog()
    inline = inline_ids(project, registry)
    part = partition_project(project, build_trunks(project, inline))[0]
    first = place_sheet(project, part, registry, NOVE_C_A3, inline)

    moved = project.model_copy(deep=True)
    for assignment in moved.sheets[0].band_assignments:
        if assignment.subsystem_id == "zones":
            assignment.band = moved.sheets[0].band_assignments[0].band
    second = place_sheet(moved, part, registry, NOVE_C_A3, inline)
    assert [item.origin.x_mm for item in first] != [item.origin.x_mm for item in second]


def test_a_plan_that_forgets_a_component_is_refused() -> None:
    project = load_project(PROJECT)
    registry = catalog()
    inline = inline_ids(project, registry)
    part = partition_project(project, build_trunks(project, inline))[0]
    stripped = project.model_copy(deep=True)
    stripped.sheets[0].band_assignments = [
        item for item in stripped.sheets[0].band_assignments if item.subsystem_id != "zones"
    ]
    with pytest.raises(LayoutError, match="assigns no band"):
        place_sheet(stripped, part, registry, NOVE_C_A3, inline)


def test_a_project_without_a_plan_still_reads_left_to_right() -> None:
    """Senza piano di impaginazione la fascia si ricava dalla profondita'
    topologica: un verso di lettura sensato invece di una colonna sola."""
    project = load_project(PROJECT)
    registry = catalog()
    inline = inline_ids(project, registry)
    bare = project.model_copy(deep=True)
    bare.sheets = []
    part = partition_project(bare, build_trunks(bare, inline))[0]
    placed = {item.component_id: item for item in place_sheet(bare, part, registry, NOVE_C_A3, inline)}
    assert placed["hp"].origin.x_mm < placed["radiators"].origin.x_mm


def test_a_plant_that_does_not_fit_fails_with_a_diagnostic() -> None:
    """Mai un rimpicciolimento, mai un disegno fuori pagina (D-045)."""
    project = load_project(PROJECT)
    registry = catalog()
    inline = inline_ids(project, registry)
    crowded = project.model_copy(deep=True)
    extra = [
        item.model_copy(update={"id": f"{item.id}-{index}", "tag": f"X{index}-{item.id[:3]}"})
        for index in range(1, 6)
        for item in project.components
        if item.id in {"buffer", "cylinder"}
    ]
    crowded.components = [*crowded.components, *extra]
    crowded.subsystems[1].component_ids = [
        *crowded.subsystems[1].component_ids,
        *[item.id for item in extra],
    ]
    part = partition_project(crowded, build_trunks(project, inline))[0]
    with pytest.raises(LayoutError, match="does not fit|never shrunk"):
        place_sheet(crowded, part, registry, NOVE_C_A3, inline)


def test_the_placement_is_deterministic_across_processes() -> None:
    """Fra processi separati e con PYTHONHASHSEED variabile."""
    script = (
        "import json;from pathlib import Path;"
        "from disegnatore_mep.catalog.registry import ComponentRegistry;"
        "from disegnatore_mep.graphics.frame import NOVE_C_A3;"
        "from disegnatore_mep.graphics.registry import SymbolRegistry;"
        "from disegnatore_mep.io.project_json import load_project;"
        "from disegnatore_mep.layout.partition import partition_project;"
        "from disegnatore_mep.layout.place import place_sheet;"
        "from disegnatore_mep.layout.trunks import build_trunks;"
        f"p=load_project(Path({str(PROJECT)!r}));"
        f"r=ComponentRegistry.from_directory(Path({str(CATALOG)!r}),"
        f" symbols=SymbolRegistry.from_directory(Path({str(SYMBOLS)!r})));"
        "i=frozenset(c.id for c in p.components if r.resolve(c.definition_id).is_inline);"
        "part=partition_project(p, build_trunks(p, i))[0];"
        "print(json.dumps([s.model_dump(mode='json') for s in "
        "place_sheet(p, part, r, NOVE_C_A3, i)], sort_keys=True))"
    )
    outputs = set()
    for seed in ("0", "1", "12345"):
        environment = {**os.environ, "PYTHONHASHSEED": seed}
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            check=True,
            env=environment,
            cwd=ROOT,
        )
        outputs.add(result.stdout)
    assert len(outputs) == 1
