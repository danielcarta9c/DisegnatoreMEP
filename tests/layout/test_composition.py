"""Le regole di composizione, misurate su una tavola di riferimento.

Il PM ha fornito uno schema reale — pompa di calore monoblocco con ACS,
compensatore e circolatore — e ha detto che quello e' il livello di ordine e
disposizione atteso. Queste prove fissano cio' che ne e' stato ricavato, cosi'
che il motore non possa tornare a impilare i componenti in colonne.
"""

from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import compose_drawing
from disegnatore_mep.layout.composition import (
    AUXILIARY_BAND,
    CALLOUT_BAND,
    GROUND_LINE,
    Standing,
    standing_of,
)
from disegnatore_mep.layout.geometry import RoutedTrunk, SheetGeometry

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"


def sheet() -> SheetGeometry:
    registry = ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
    return compose_drawing(load_project(PROJECT), registry, NOVE_C_A3).sheets[0]


def area_y(fraction: float) -> float:
    rect = NOVE_C_A3.drawing_rect_mm
    step = NOVE_C_A3.standard.grid_mm
    return rect.y_mm + round(rect.height_mm * fraction / step) * step


def test_the_ground_line_is_recorded_on_the_sheet() -> None:
    assert sheet().ground_line_y_mm == area_y(GROUND_LINE)


def test_machines_and_storage_stand_on_the_ground() -> None:
    """Appoggiati, non appesi: e' la prima cosa che si vede in una tavola vera."""
    ground = area_y(GROUND_LINE)
    placed = {item.component_id: item for item in sheet().symbols}
    for component_id in ("hp", "cylinder", "buffer"):
        assert placed[component_id].bottom_mm == ground, component_id


def test_an_inline_auxiliary_rides_the_lowest_rail() -> None:
    """Un filtro sta **su** una tratta e non puo' lasciarla: quello che si puo'
    chiedere e' che la sua tratta corra bassa, come sul riferimento, dove
    filtro e riempimento stanno vicino a terra."""
    drawn = sheet()
    placed = {item.component_id: item for item in drawn.symbols}
    strainer = placed["strainer"]
    others = [
        item
        for item in drawn.symbols
        if item.component_id not in {"strainer", "shutoff", "pump-secondary"}
        and item.height_mm < 20.0
    ]
    assert strainer.origin.y_mm >= min(item.origin.y_mm for item in others) - 1e-9
    assert strainer.bottom_mm <= area_y(GROUND_LINE) + 1e-9


def test_the_size_hierarchy_reads_like_the_reference() -> None:
    """Sul riferimento una macchina sta a una valvola come 5,3 a 1 in misura
    lineare. La gerarchia precedente le teneva a 2,7 e non si distinguevano."""
    registry = SymbolRegistry.from_directory(SYMBOLS)
    machine = registry.get("heat-pump-air-water").manifest
    valve = registry.get("valve-isolation").manifest
    assert machine.height_mm / valve.height_mm >= 5.0
    storage = registry.get("dhw-cylinder").manifest
    assert storage.height_mm > machine.height_mm


def test_supply_runs_sit_above_return_runs() -> None:
    """Mandata sopra, ritorno sotto: la convenzione del riferimento."""
    supply = [item for item in sheet().routes if item.supply]
    returns = [item for item in sheet().routes if not item.supply]
    assert supply and returns

    def rail_of(route: RoutedTrunk) -> float:
        return min(
            point.y_mm for segment in route.segments for point in segment
        )

    assert min(rail_of(item) for item in supply) <= min(rail_of(item) for item in returns)


def test_supply_and_return_are_different_lines() -> None:
    from disegnatore_mep.layout.legend import style_for

    routes = sheet().routes
    styles = {(style_for(item.medium, item.supply)) for item in routes}
    assert len(styles) >= 2


def test_labels_are_callouts_below_the_ground_line() -> None:
    """I testi escono dal corpo e una linea sottile li riporta al pezzo: sopra
    il simbolo non ci sta nulla appena il disegno si infittisce."""
    drawn = sheet()
    assert drawn.labels
    for label in drawn.labels:
        assert label.anchor.y_mm >= area_y(CALLOUT_BAND) - 1e-9
    assert any(label.leader_from is not None for label in drawn.labels)


def test_a_leader_starts_on_the_component_it_names() -> None:
    drawn = sheet()
    placed = {item.component_id: item for item in drawn.symbols}
    for label in drawn.labels:
        if label.leader_from is None:
            continue
        component_id = label.id.rsplit("-", 1)[0]
        symbol = placed.get(component_id)
        if symbol is None:
            continue
        assert symbol.origin.x_mm <= label.leader_from.x_mm <= symbol.right_mm
        assert label.leader_from.y_mm == symbol.bottom_mm


def test_standing_is_decided_by_size_and_function_not_by_name() -> None:
    assert standing_of(45.0, frozenset({"dhw_storage"}), False) is Standing.GROUND
    assert standing_of(5.0, frozenset({"isolation"}), True) is Standing.RAIL
    assert standing_of(15.0, frozenset({"expansion"}), False) is Standing.AUXILIARY
    # Un filtro e' in linea, ma la sua funzione lo porta comunque in basso.
    assert standing_of(5.0, frozenset({"filtration"}), True) is Standing.AUXILIARY


def test_the_reference_proportions_are_ordered() -> None:
    assert CALLOUT_BAND > GROUND_LINE > AUXILIARY_BAND
