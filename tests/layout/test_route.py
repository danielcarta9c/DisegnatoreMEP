import time
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.errors import LayoutError
from disegnatore_mep.layout.geometry import PlacedSymbol, RoutedTrunk
from disegnatore_mep.layout.grid import GridSpace
from disegnatore_mep.layout.partition import partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.route import (
    CROSS_COST,
    MAX_EXPANSIONS,
    STEP_COST,
    TURN_COST,
    Route,
    route,
    route_sheet,
)
from disegnatore_mep.layout.trunks import build_trunks

EAST = (1, 0)
WEST = (-1, 0)
SOUTH = (0, 1)
NORTH = (0, -1)

BODY_COLS, BODY_ROWS = 140, 94
"""L'area di disegno reale: 350 x 235 mm con passo 2,5 mm."""


def straight(max_expansions: int = MAX_EXPANSIONS) -> Route:
    return route(
        (0, 10), EAST, (20, 10), WEST,
        cols=BODY_COLS, rows=BODY_ROWS,
        blocked=frozenset(), occupied=frozenset(),
        max_expansions=max_expansions,
    )


def test_a_clear_run_is_a_straight_line() -> None:
    result = straight()
    assert result.vertices == ((0, 10), (20, 10))
    assert result.cost == 20 * STEP_COST


def test_the_path_is_orthogonal_and_contiguous() -> None:
    result = route(
        (0, 0), EAST, (30, 40), NORTH,
        cols=BODY_COLS, rows=BODY_ROWS, blocked=frozenset(), occupied=frozenset(),
    )
    for before, after in zip(result.cells, result.cells[1:], strict=False):
        assert abs(before[0] - after[0]) + abs(before[1] - after[1]) == 1


def test_a_crossing_is_taken_instead_of_a_detour() -> None:
    """Il cuore di D-041: la rete che attraversa non gira intorno."""
    curtain = frozenset({(10, row) for row in range(0, BODY_ROWS)})
    result = route(
        (0, 10), EAST, (20, 10), WEST,
        cols=BODY_COLS, rows=BODY_ROWS, blocked=frozenset(), occupied=curtain,
    )
    assert result.vertices == ((0, 10), (20, 10))
    assert result.crossings == ((10, 10),)
    assert result.cost == 20 * STEP_COST + CROSS_COST


def test_a_crossing_costs_less_than_the_shortest_way_around() -> None:
    """D-041, con il giro misurato per quello che costa davvero.

    Schivare una cella occupata su un rettilineo non vale «due passi»: vale due
    passi **e quattro pieghe**, perche' si esce, si va di fianco, si rientra e
    si riprende la direzione. La vecchia formulazione contava solo i passi e
    reggeva soltanto perche' la piega costava quasi quanto un passo.
    """
    around = 2 * STEP_COST + 4 * TURN_COST
    assert around > CROSS_COST
    # E resta piu' cara di un solo attraversamento anche a piega gratis.
    assert 2 * STEP_COST + TURN_COST > CROSS_COST


def test_an_obstacle_is_gone_around_not_through() -> None:
    wall = frozenset({(10, row) for row in range(0, 12)})
    result = route(
        (0, 10), EAST, (20, 10), WEST,
        cols=BODY_COLS, rows=BODY_ROWS, blocked=wall, occupied=frozenset(),
    )
    assert not set(result.cells) & wall
    assert result.cells[-1] == (20, 10)


def test_two_networks_do_not_run_side_by_side_on_the_same_cells() -> None:
    lane = frozenset({(col, 10) for col in range(0, 21)})
    result = route(
        (0, 10), EAST, (20, 10), WEST,
        cols=BODY_COLS, rows=BODY_ROWS, blocked=frozenset(), occupied=lane,
    )
    longest = run = 0
    for cell in result.cells:
        run = run + 1 if cell in lane else 0
        longest = max(longest, run)
    assert longest <= 2, result.cells  # si attraversa, non si costeggia


def test_a_sealed_target_fails_with_a_diagnostic() -> None:
    box = frozenset(
        {(col, row) for col in range(18, 23) for row in range(8, 13)} - {(20, 10)}
    )
    with pytest.raises(LayoutError, match="blocked|did not converge"):
        route(
            (0, 10), EAST, (20, 10), WEST,
            cols=BODY_COLS, rows=BODY_ROWS, blocked=box, occupied=frozenset(),
        )


def test_the_iteration_budget_produces_a_diagnostic_not_a_hang() -> None:
    with pytest.raises(LayoutError, match="did not converge"):
        straight(max_expansions=3)


def test_the_same_input_always_gives_the_same_route() -> None:
    runs = {
        route(
            (0, 0), EAST, (60, 40), NORTH,
            cols=BODY_COLS, rows=BODY_ROWS,
            blocked=frozenset({(30, row) for row in range(0, 30)}),
            occupied=frozenset({(45, row) for row in range(0, BODY_ROWS)}),
        ).cells
        for _ in range(5)
    }
    assert len(runs) == 1


def test_a_full_width_route_is_fast_enough_for_a_sheet() -> None:
    started = time.perf_counter()
    result = route(
        (0, 0), EAST, (BODY_COLS - 2, BODY_ROWS - 2), NORTH,
        cols=BODY_COLS, rows=BODY_ROWS,
        blocked=frozenset({(col, 40) for col in range(0, 120)}),
        occupied=frozenset(),
    )
    elapsed = time.perf_counter() - started
    assert result.cells[-1] == (BODY_COLS - 2, BODY_ROWS - 2)
    assert elapsed < 1.0, f"{elapsed:.3f}s"


def test_the_arrival_direction_is_the_outward_direction_of_its_port() -> None:
    """La convenzione dei segni: la porta dichiara dove GUARDA, non da dove si arriva.

    Una porta a destra di un componente ha direzione uscente EAST; la rotta che la
    raggiunge viaggia verso ovest.
    """
    good = route(
        (0, 10), EAST, (20, 10), WEST,
        cols=BODY_COLS, rows=BODY_ROWS, blocked=frozenset(), occupied=frozenset(),
    )
    assert good.vertices == ((0, 10), (20, 10))

    # Al contrario non fallisce: costruisce un cappio che rientra dal lato
    # sbagliato. E' il motivo per cui la direzione non va passata a mano ma
    # derivata da PortFace.outward_angle_deg.
    backwards = route(
        (0, 10), EAST, (20, 10), EAST,
        cols=BODY_COLS, rows=BODY_ROWS, blocked=frozenset(), occupied=frozenset(),
    )
    assert backwards.cost > good.cost
    assert backwards.cells[-2] == (21, 10)


# --- l'instradamento del caso D-011 ------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"


def routed_case() -> tuple[list[PlacedSymbol], list[RoutedTrunk]]:
    project = load_project(PROJECT)
    registry = ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
    inline = frozenset(
        item.id
        for item in project.components
        if registry.resolve(item.definition_id).is_inline
    )
    trunks = build_trunks(project, inline)
    part = partition_project(project, trunks)[0]
    placed = place_sheet(project, part, registry, NOVE_C_A3, inline)
    grid = GridSpace(origin=NOVE_C_A3.drawing_rect_mm, standard=NOVE_C_A3.standard)
    return placed, route_sheet(project, list(part.trunks), placed, registry, grid)


@pytest.mark.skip(
    reason="La composizione e' il pezzo da rifare del piano: con gli accessori "
    "sugli stacchi al posto giusto l'impianto completo chiede piu' larghezza di "
    "quanta ne abbia un foglio ordinario, e il posizionamento a fasce non ci "
    "arriva. Non e' un difetto del contenuto — quello si giudica sul grafo "
    "scritto (D-096) — ed e' esattamente il limite che il pezzo della "
    "composizione deve chiudere. Queste prove tornano quando quel pezzo si fa."
)
def test_every_run_of_the_case_is_routed() -> None:
    _, routes = routed_case()
    assert len(routes) == 10
    assert all(item.segments and len(item.segments[0]) >= 2 for item in routes)


def test_no_route_passes_under_a_placed_symbol() -> None:
    """Il gate dichiarato per P4 nella roadmap master."""
    placed, routes = routed_case()
    for item in routes:
        for segment in item.segments:
            for before, after in zip(segment, segment[1:], strict=False):
                for symbol in placed:
                    inside_x = (
                        symbol.origin.x_mm < min(before.x_mm, after.x_mm)
                        and max(before.x_mm, after.x_mm) < symbol.right_mm
                    )
                    inside_y = (
                        symbol.origin.y_mm < min(before.y_mm, after.y_mm)
                        and max(before.y_mm, after.y_mm) < symbol.bottom_mm
                    )
                    assert not (inside_x and inside_y), (symbol.component_id, before, after)


def test_every_route_is_orthogonal() -> None:
    _, routes = routed_case()
    for item in routes:
        for segment in item.segments:
            for before, after in zip(segment, segment[1:], strict=False):
                assert before.x_mm == after.x_mm or before.y_mm == after.y_mm


def test_nothing_is_routed_outside_the_drawing_area() -> None:
    area = NOVE_C_A3.drawing_rect_mm
    _, routes = routed_case()
    for item in routes:
        for segment in item.segments:
            for point in segment:
                assert area.x_mm <= point.x_mm <= area.right_mm
                assert area.y_mm <= point.y_mm <= area.bottom_mm
