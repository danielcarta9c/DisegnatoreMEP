"""Le prove di DRAW-005-R1, blocco D, scritte prima del codice: la posa locale
della catena che appartiene alla macchina (I-044).

La traduzione PM (`docs/pm/2026-09-08-rilievi-po-draw005-r1.md`):

- ordine sul ritorno: porta della macchina -> filtro a Y -> valvola -> rete;
- filtro e valvola stanno sul **primo tratto rettilineo utile dalla porta**, prima
  della prima curva;
- due macchine uguali con la stessa catena hanno le stesse distanze locali fra
  porta, filtro e valvola, anche se una catena ruota;
- nessuna coordinata o eccezione per gli identificativi della tavola 1.

La catena di una macchina si legge dal catalogo, mai dal nome: da un attacco di un
pezzo che si manutiene, i pezzi in linea fino al primo organo di chiusura compreso.
E' un contratto duro: una posa che non lo rispetta non e' una candidata, e il costo
globale sceglie fra quelle che lo rispettano. Impianti costruiti qui.
"""

import math
from datetime import date
from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import CLOSING_FUNCTIONS, ComponentTrait
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.symbol import PortFace
from disegnatore_mep.layout.compose import compose_drawing, inline_component_ids
from disegnatore_mep.layout.errors import LayoutError
from disegnatore_mep.layout.geometry import (
    DrawingGeometry,
    PlacedSymbol,
    Point,
    RoutedTrunk,
    box_of,
    moves_of,
)
from disegnatore_mep.layout.grid import GridSpace
from disegnatore_mep.layout.inline import (
    CHAIN_PORT_GAP_MM,
    MIN_SPACING_MM,
    SNUG_CLEARANCE_MM,
    place_inline_accessories,
)
from disegnatore_mep.layout.trunks import Trunk, build_trunks
from disegnatore_mep.model.project import (
    ComponentInstance,
    ConnectionModel,
    NetworkModel,
    PortRef,
    ProjectMetadata,
    ProjectModel,
    SubsystemModel,
)
from disegnatore_mep.model.types import PlantRegime, PortFlow
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"

HEATING = "heating_water"
COLD = "cold_water"
DHW = "domestic_hot_water"
TOLERANCE_MM = 1e-6


@cache
def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


@cache
def rules() -> RuleRegistry:
    registry = RuleRegistry.from_directory(RULES)
    registry.cross_check(catalog())
    return registry


def grid() -> GridSpace:
    return GridSpace(origin=NOVE_C_A3.drawing_rect_mm, standard=NOVE_C_A3.standard)


def _pipe(pipe_id: str, network_id: str, a: tuple[str, str], b: tuple[str, str]) -> ConnectionModel:
    return ConnectionModel(
        id=pipe_id,
        network_id=network_id,
        endpoint_a=PortRef(component_id=a[0], port_id=a[1]),
        endpoint_b=PortRef(component_id=b[0], port_id=b[1]),
    )


def _plant(
    networks: list[tuple[str, str]],
    components: list[tuple[str, str, str | None]],
    connections: list[ConnectionModel],
    subsystems: list[tuple[str, list[str], list[str]]] | None = None,
) -> ProjectModel:
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-catena",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 8),
        ),
        plant_regime=PlantRegime.UP_TO_35_KW,
        networks=[
            NetworkModel(id=network_id, name=network_id, domain="hydronic", medium=medium)
            for network_id, medium in networks
        ],
        components=[
            ComponentInstance(id=item, definition_id=definition, tag=tag)
            for item, definition, tag in components
        ],
        connections=connections,
        subsystems=[
            SubsystemModel(id=item, name=item, component_ids=members, network_ids=nets)
            for item, members, nets in (subsystems or [])
        ],
    )


# ---------------------------------------------------------------------------
# La catena a mano: una tratta con i suoi pezzi, posata su una spezzata data
# ---------------------------------------------------------------------------


def _hand_plant(with_network_pieces: bool = False) -> ProjectModel:
    """Ripartizione -> [organi di rete] -> valvola -> filtro -> macchina, sul
    ritorno: i pezzi della macchina sono gli ultimi due, letti dal catalogo."""
    components: list[tuple[str, str, str | None]] = [
        ("ripartizione", "tee-split", None),
        ("valvola", "valve-isolation", None),
        ("filtro", "strainer", None),
        ("macchina", "heat-pump-air-water", "PDC-X"),
    ]
    pipes: list[ConnectionModel]
    if with_network_pieces:
        components = [
            components[0],
            ("valvola-rete", "valve-isolation", None),
            ("defangatore", "dirt-separator", None),
            *components[1:],
        ]
        pipes = [
            _pipe("r-1", "anello", ("ripartizione", "b"), ("valvola-rete", "a")),
            _pipe("r-2", "anello", ("valvola-rete", "b"), ("defangatore", "a")),
            _pipe("r-3", "anello", ("defangatore", "b"), ("valvola", "a")),
            _pipe("r-4", "anello", ("valvola", "b"), ("filtro", "a")),
            _pipe("r-5", "anello", ("filtro", "b"), ("macchina", "water_return")),
        ]
    else:
        pipes = [
            _pipe("r-1", "anello", ("ripartizione", "b"), ("valvola", "a")),
            _pipe("r-2", "anello", ("valvola", "b"), ("filtro", "a")),
            _pipe("r-3", "anello", ("filtro", "b"), ("macchina", "water_return")),
        ]
    return _plant([("anello", HEATING)], components, pipes)


def _hand_trunk(project: ProjectModel) -> Trunk:
    trunks = build_trunks(project, inline_component_ids(project, catalog()))
    assert len(trunks) == 1
    trunk = trunks[0]
    # La tratta si legge dalla ripartizione verso la macchina: e' la macchina
    # che sta al capo di arrivo.
    assert trunk.end.component_id == "macchina", trunk
    return trunk


def _routed(trunk: Trunk, points: list[tuple[float, float]]) -> RoutedTrunk:
    return RoutedTrunk(
        network_id=trunk.network_id,
        medium=HEATING,
        supply=False,
        connection_ids=list(trunk.connection_ids),
        segments=[[Point(x_mm=x, y_mm=y) for x, y in points]],
    )


def _along(origin: tuple[float, float], symbol: PlacedSymbol, axis: tuple[float, float]) -> float:
    """La distanza del centro del simbolo dal punto d'attacco, lungo l'asse."""
    centre = ((symbol.origin.x_mm + symbol.right_mm) / 2, (symbol.origin.y_mm + symbol.bottom_mm) / 2)
    return (centre[0] - origin[0]) * axis[0] + (centre[1] - origin[1]) * axis[1]


def _gap_to_point(symbol: PlacedSymbol, x_mm: float, y_mm: float) -> float:
    left, top, right, bottom = box_of(symbol)
    return math.hypot(max(left - x_mm, x_mm - right, 0.0), max(top - y_mm, y_mm - bottom, 0.0))


def _gap_between(first: PlacedSymbol, second: PlacedSymbol) -> float:
    a, b = box_of(first), box_of(second)
    return math.hypot(max(a[0] - b[2], b[0] - a[2], 0.0), max(a[1] - b[3], b[1] - a[3], 0.0))


def _arc_from_the_port(points: list[tuple[float, float]], symbol: PlacedSymbol) -> float:
    """La distanza del centro del simbolo dalla porta, misurata lungo la spezzata
    (che finisce sulla porta): l'ordine vero di una fila, anche oltre la curva."""
    centre = ((symbol.origin.x_mm + symbol.right_mm) / 2, (symbol.origin.y_mm + symbol.bottom_mm) / 2)
    travelled = 0.0
    for after, before in zip(reversed(points), list(reversed(points))[1:], strict=False):
        length = abs(after[0] - before[0]) + abs(after[1] - before[1])
        on_it = (
            min(before[0], after[0]) - 1e-6 <= centre[0] <= max(before[0], after[0]) + 1e-6
            and min(before[1], after[1]) - 1e-6 <= centre[1] <= max(before[1], after[1]) + 1e-6
        )
        if on_it:
            return travelled + abs(centre[0] - after[0]) + abs(centre[1] - after[1])
        travelled += length
    raise AssertionError(f"{symbol.component_id} non sta sulla spezzata")


# Le due giaciture: la stessa catena, una volta orizzontale e una verticale.
# La spezzata va dalla ripartizione alla macchina; l'ultimo tratto e' il primo
# rettilineo dalla porta della macchina.
GIACITURE: dict[str, tuple[list[tuple[float, float]], tuple[float, float]]] = {
    "orizzontale": ([(120.0, 160.0), (120.0, 120.0), (60.0, 120.0)], (1.0, 0.0)),
    "verticale": ([(60.0, 60.0), (100.0, 60.0), (100.0, 120.0)], (0.0, -1.0)),
}
"""Per ciascuna: i punti, e l'asse **uscente dalla porta** lungo il rettilineo."""


@pytest.mark.parametrize("giacitura", GIACITURE, ids=list(GIACITURE))
def test_la_catena_della_macchina_sta_sul_primo_rettilineo_dalla_porta_nell_ordine_giusto(
    giacitura: str,
) -> None:
    project = _hand_plant()
    trunk = _hand_trunk(project)
    points, axis = GIACITURE[giacitura]
    placed, broken = place_inline_accessories(
        project, trunk, _routed(trunk, points), catalog(), grid()
    )
    by_id = {item.component_id: item for item in placed}
    port = points[-1]
    filtro, valvola = by_id["filtro"], by_id["valvola"]
    # Sul rettilineo che parte dalla porta: i centri sull'asse, prima della curva.
    corner = points[-2]
    for item in (filtro, valvola):
        centre = ((item.origin.x_mm + item.right_mm) / 2, (item.origin.y_mm + item.bottom_mm) / 2)
        off_axis = abs((centre[0] - port[0]) * axis[1] - (centre[1] - port[1]) * axis[0])
        assert off_axis <= TOLERANCE_MM, (giacitura, item.component_id, centre)
        assert 0 < _along(port, item, axis) < _along(port, PlacedSymbol(
            component_id="curva", symbol_id="x", rotation_deg=0,
            origin=Point(x_mm=corner[0], y_mm=corner[1]), width_mm=1e-9, height_mm=1e-9,
        ), axis) + 1e-9, (giacitura, item.component_id)
    # Ordine: porta -> filtro -> valvola -> rete.
    assert _along(port, filtro, axis) < _along(port, valvola, axis)
    # Le distanze locali: la soglia dell'attacco piu' un passo dalla porta (D-120), un passo fra i due.
    assert abs(_gap_to_point(filtro, *port) - CHAIN_PORT_GAP_MM) <= TOLERANCE_MM
    assert abs(_gap_between(filtro, valvola) - MIN_SPACING_MM) <= TOLERANCE_MM
    # E la linea e' interrotta per entrambi, non coperta.
    assert len(broken.segments) == 3


def test_le_distanze_locali_non_cambiano_quando_la_catena_ruota() -> None:
    project = _hand_plant()
    trunk = _hand_trunk(project)
    offsets: dict[str, tuple[float, float]] = {}
    rotations: dict[str, tuple[int, int]] = {}
    for name, (points, axis) in GIACITURE.items():
        placed, _ = place_inline_accessories(
            project, trunk, _routed(trunk, points), catalog(), grid()
        )
        by_id = {item.component_id: item for item in placed}
        port = points[-1]
        offsets[name] = (
            round(_along(port, by_id["filtro"], axis), 6),
            round(_along(port, by_id["valvola"], axis), 6),
        )
        rotations[name] = (by_id["filtro"].rotation_deg, by_id["valvola"].rotation_deg)
    assert offsets["orizzontale"] == offsets["verticale"], offsets
    assert rotations["orizzontale"] != rotations["verticale"], rotations
    # E ogni centro sta su un nodo della griglia.
    for name in GIACITURE:
        for offset in offsets[name]:
            assert abs(offset / grid().step_mm - round(offset / grid().step_mm)) <= 1e-9, (name, offset)


def test_traslare_la_spezzata_trasla_la_catena_e_basta() -> None:
    project = _hand_plant()
    trunk = _hand_trunk(project)
    points, axis = GIACITURE["orizzontale"]
    shifted = [(x + 50.0, y + 25.0) for x, y in points]
    first, _ = place_inline_accessories(project, trunk, _routed(trunk, points), catalog(), grid())
    second, _ = place_inline_accessories(project, trunk, _routed(trunk, shifted), catalog(), grid())
    for one, two in zip(first, second, strict=True):
        assert one.component_id == two.component_id
        assert one.rotation_deg == two.rotation_deg
        assert abs(two.origin.x_mm - one.origin.x_mm - 50.0) <= TOLERANCE_MM
        assert abs(two.origin.y_mm - one.origin.y_mm - 25.0) <= TOLERANCE_MM


def test_i_pezzi_di_rete_non_entrano_nella_catena_e_le_restano_dietro() -> None:
    """Oltre l'organo di chiusura della macchina, verso la rete, gli altri pezzi
    si posano come sempre: dopo la catena, nell'ordine della tratta."""
    project = _hand_plant(with_network_pieces=True)
    trunk = _hand_trunk(project)
    points, axis = GIACITURE["orizzontale"]
    placed, _ = place_inline_accessories(project, trunk, _routed(trunk, points), catalog(), grid())
    by_id = {item.component_id: item for item in placed}
    port = points[-1]
    assert abs(_gap_to_point(by_id["filtro"], *port) - CHAIN_PORT_GAP_MM) <= TOLERANCE_MM
    assert abs(_gap_between(by_id["filtro"], by_id["valvola"]) - MIN_SPACING_MM) <= TOLERANCE_MM
    ordered = sorted(placed, key=lambda item: _arc_from_the_port(points, item))
    assert [item.component_id for item in ordered] == ["filtro", "valvola", "defangatore", "valvola-rete"]
    assert _gap_between(by_id["valvola"], by_id["defangatore"]) >= MIN_SPACING_MM - TOLERANCE_MM


def _hand_plant_from_the_machine() -> ProjectModel:
    """Macchina -> valvola -> defangatore -> ripartizione, sulla mandata: la
    catena sta al capo di **partenza** della tratta, e dietro di lei viene un
    pezzo che con la valvola fa coppia (D-120) e rinuncia al proprio passo."""
    components: list[tuple[str, str, str | None]] = [
        ("macchina", "heat-pump-air-water", "PDC-X"),
        ("valvola", "valve-isolation", None),
        ("defangatore", "dirt-separator", None),
        ("ripartizione", "tee-split", None),
    ]
    pipes = [
        _pipe("m-1", "anello", ("macchina", "water_supply"), ("valvola", "a")),
        _pipe("m-2", "anello", ("valvola", "b"), ("defangatore", "a")),
        _pipe("m-3", "anello", ("defangatore", "b"), ("ripartizione", "a")),
    ]
    return _plant([("anello", HEATING)], components, pipes)


def test_chi_segue_la_catena_di_testa_le_sta_a_un_passo_e_non_la_tocca() -> None:
    """La catena e' un pezzo posato come gli altri: chi viene dopo riparte dal
    suo riquadro **piu' il passo**, anche quando fa coppia con l'organo che
    chiude e rinuncia al proprio passo di testa. Toccarsi si legge come un
    pezzo solo."""
    project = _hand_plant_from_the_machine()
    trunks = build_trunks(project, inline_component_ids(project, catalog()))
    assert len(trunks) == 1
    trunk = trunks[0]
    assert trunk.start.component_id == "macchina", trunk
    points = [(60.0, 120.0), (120.0, 120.0), (120.0, 160.0)]
    placed, _ = place_inline_accessories(project, trunk, _routed(trunk, points), catalog(), grid())
    by_id = {item.component_id: item for item in placed}
    port = points[0]
    assert abs(_gap_to_point(by_id["valvola"], *port) - CHAIN_PORT_GAP_MM) <= TOLERANCE_MM
    gap = _gap_between(by_id["valvola"], by_id["defangatore"])
    assert gap >= MIN_SPACING_MM - TOLERANCE_MM, gap
    ordered = sorted(placed, key=lambda item: _arc_from_the_port(list(reversed(points)), item))
    assert [item.component_id for item in ordered] == ["valvola", "defangatore"]


def test_una_catena_che_non_sta_sul_primo_rettilineo_non_e_una_posa_valida() -> None:
    """Il contratto e' duro: se dalla porta alla prima curva non c'e' posto per
    filtro e valvola, la posa si rifiuta invece di spostare la catena oltre la
    curva."""
    project = _hand_plant()
    trunk = _hand_trunk(project)
    short = [(120.0, 160.0), (120.0, 120.0), (110.0, 120.0)]
    with pytest.raises(LayoutError, match="macchina"):
        place_inline_accessories(project, trunk, _routed(trunk, short), catalog(), grid())


def test_la_catena_si_legge_dal_catalogo_chi_chiude_e_chi_si_manutiene() -> None:
    assert CHAIN_PORT_GAP_MM == SNUG_CLEARANCE_MM + MIN_SPACING_MM
    project = _hand_plant()
    registry = catalog()
    definitions = {item.id: registry.get(item.definition_id) for item in project.components}
    assert definitions["macchina"].has_trait(ComponentTrait.MAINTAINABLE)
    assert CLOSING_FUNCTIONS & set(definitions["valvola"].functions)
    assert not (CLOSING_FUNCTIONS & set(definitions["filtro"].functions))
    assert definitions["ripartizione"].is_a_fitting


# ---------------------------------------------------------------------------
# Sulla tavola composta: due macchine uguali, due catene congruenti
# ---------------------------------------------------------------------------


def due_macchine_con_accumulo_combinato() -> ProjectModel:
    return _plant(
        [("primo", HEATING), ("secondo", HEATING), ("fredda", COLD), ("calda", DHW)],
        [
            ("nord", "heat-pump-air-water", "PDC-A"),
            ("sud", "heat-pump-air-water", "PDC-B"),
            ("unione", "tee-junction", None),
            ("ripartizione", "tee-split", None),
            ("serbatoio", "buffer-combined", "ACC-A"),
            ("pompa", "pump-circulator", "CIR-A"),
            ("corpo", "radiator", "RAD-A"),
            ("rete-idrica", "cold-water-inlet", "AF-A"),
            ("rubinetti", "dhw-draw-off", "ACS-A"),
        ],
        [
            _pipe("p1", "primo", ("nord", "water_supply"), ("unione", "a")),
            _pipe("p2", "primo", ("sud", "water_supply"), ("unione", "c")),
            _pipe("p3", "primo", ("unione", "b"), ("serbatoio", "primary_in")),
            _pipe("p4", "primo", ("serbatoio", "primary_out"), ("ripartizione", "a")),
            _pipe("p5", "primo", ("ripartizione", "b"), ("nord", "water_return")),
            _pipe("p6", "primo", ("ripartizione", "c"), ("sud", "water_return")),
            _pipe("s1", "secondo", ("serbatoio", "secondary_out"), ("pompa", "a")),
            _pipe("s2", "secondo", ("pompa", "b"), ("corpo", "in")),
            _pipe("s3", "secondo", ("corpo", "out"), ("serbatoio", "secondary_in")),
            _pipe("w1", "fredda", ("rete-idrica", "a"), ("serbatoio", "cold_in")),
            _pipe("w2", "calda", ("serbatoio", "dhw_out"), ("rubinetti", "a")),
        ],
        [
            ("generazione", ["nord", "sud", "unione", "ripartizione"], ["primo"]),
            ("accumulo", ["serbatoio", "rete-idrica", "rubinetti"], ["primo", "fredda", "calda"]),
            ("distribuzione", ["pompa", "corpo"], ["secondo"]),
        ],
    )


def due_macchine_in_parallelo_su_volano() -> ProjectModel:
    return _plant(
        [("primo", HEATING), ("secondo", HEATING)],
        [
            ("nord", "heat-pump-air-water", "PDC-A"),
            ("sud", "heat-pump-air-water", "PDC-B"),
            ("unione", "tee-junction", None),
            ("ripartizione", "tee-split", None),
            ("volano", "buffer-four-port", "VOL-A"),
            ("pompa", "pump-circulator", "CIR-A"),
            ("corpo", "radiator", "RAD-A"),
        ],
        [
            _pipe("p1", "primo", ("nord", "water_supply"), ("unione", "a")),
            _pipe("p2", "primo", ("sud", "water_supply"), ("unione", "c")),
            _pipe("p3", "primo", ("unione", "b"), ("volano", "primary_in")),
            _pipe("p4", "primo", ("volano", "primary_out"), ("ripartizione", "a")),
            _pipe("p5", "primo", ("ripartizione", "b"), ("nord", "water_return")),
            _pipe("p6", "primo", ("ripartizione", "c"), ("sud", "water_return")),
            _pipe("s1", "secondo", ("volano", "secondary_out"), ("pompa", "a")),
            _pipe("s2", "secondo", ("pompa", "b"), ("corpo", "in")),
            _pipe("s3", "secondo", ("corpo", "out"), ("volano", "secondary_in")),
        ],
        [
            ("generazione", ["nord", "sud", "unione", "ripartizione"], ["primo"]),
            ("accumulo", ["volano"], ["primo", "secondo"]),
            ("distribuzione", ["pompa", "corpo"], ["secondo"]),
        ],
    )


CASI = (due_macchine_con_accumulo_combinato, due_macchine_in_parallelo_su_volano)
CASI_IDS = [item.__name__ for item in CASI]


@cache
def _composed(index: int) -> tuple[ProjectModel, DrawingGeometry]:
    done, _, gaps = saturate(CASI[index](), catalog(), rules())
    assert not gaps
    return done, compose_drawing(done, catalog(), NOVE_C_A3)


class Chains:
    """Le catene di ritorno delle macchine, lette sulla tavola composta."""

    def __init__(self, project: ProjectModel, drawing: DrawingGeometry) -> None:
        self.project = project
        self.sheet = drawing.sheets[0]
        registry = catalog()
        self.definitions = {item.id: registry.get(item.definition_id) for item in project.components}
        self.manifests = {
            item.id: registry.resolve(item.definition_id).symbol.manifest
            for item in project.components
        }
        self.placed = {item.component_id: item for item in self.sheet.symbols}
        self.trunks = build_trunks(project, inline_component_ids(project, catalog()))
        self.routes = {tuple(route.connection_ids): route for route in self.sheet.routes}

    def generators(self) -> list[str]:
        return sorted(
            component_id
            for component_id, definition in self.definitions.items()
            if "heat_generation" in definition.functions
        )

    def return_trunk(self, generator: str) -> tuple[Trunk, bool]:
        """La tratta del ritorno, e se la macchina ne e' il capo di arrivo."""
        port = next(
            item.id
            for item in self.definitions[generator].ports
            if item.flow is PortFlow.IN and not item.off_the_run
        )
        ref = PortRef(component_id=generator, port_id=port)
        for trunk in self.trunks:
            if trunk.end == ref:
                return trunk, True
            if trunk.start == ref:
                return trunk, False
        raise AssertionError(generator)

    def port_point(self, ref: PortRef) -> tuple[tuple[float, float], PortFace]:
        symbol = self.placed[ref.component_id]
        turned = self.manifests[ref.component_id].rotated(symbol.rotation_deg)
        port = turned.port(symbol.physical_port(ref.port_id))
        return (symbol.origin.x_mm + port.x_mm, symbol.origin.y_mm + port.y_mm), port.face

    def first_straight(self, trunk: Trunk, from_end: bool) -> tuple[tuple[float, float], tuple[float, float]]:
        """Il rettilineo che parte dalla porta della macchina, sulla spezzata
        intera: dalla porta alla prima curva."""
        route = self.routes[trunk.connection_ids]
        points = [point for segment in route.segments for point in segment]
        whole: list[Point] = []
        for point in points:
            if not whole or (whole[-1].x_mm, whole[-1].y_mm) != (point.x_mm, point.y_mm):
                whole.append(point)
        ordered = list(reversed(whole)) if from_end else whole
        moves = moves_of(ordered)
        start = ordered[0]
        end = moves[0][1]
        for before, after in moves[1:]:
            same = (
                abs(after.x_mm - before.x_mm) <= TOLERANCE_MM
                and abs(end.x_mm - start.x_mm) <= TOLERANCE_MM
            ) or (
                abs(after.y_mm - before.y_mm) <= TOLERANCE_MM
                and abs(end.y_mm - start.y_mm) <= TOLERANCE_MM
            )
            if not same:
                break
            end = after
        return (start.x_mm, start.y_mm), (end.x_mm, end.y_mm)

    def chain_of(self, generator: str) -> list[str]:
        """Dalla porta della macchina: i pezzi in linea fino al primo organo di
        chiusura compreso, letti dal catalogo."""
        trunk, from_end = self.return_trunk(generator)
        members = list(trunk.inline_component_ids)
        ordered = list(reversed(members)) if from_end else members
        chain: list[str] = []
        for item in ordered:
            chain.append(item)
            if CLOSING_FUNCTIONS & set(self.definitions[item].functions):
                break
        return chain


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_le_catene_di_ritorno_delle_due_macchine_sono_congruenti(index: int) -> None:
    project, drawing = _composed(index)
    chains = Chains(project, drawing)
    generators = chains.generators()
    assert len(generators) == 2
    offsets: dict[str, list[float]] = {}
    for generator in generators:
        trunk, from_end = chains.return_trunk(generator)
        ref = trunk.end if from_end else trunk.start
        port, face = chains.port_point(ref)
        (start, end) = chains.first_straight(trunk, from_end)
        assert abs(start[0] - port[0]) <= TOLERANCE_MM and abs(start[1] - port[1]) <= TOLERANCE_MM
        length = abs(end[0] - start[0]) + abs(end[1] - start[1])
        axis = ((end[0] - start[0]) / length, (end[1] - start[1]) / length)
        chain = chains.chain_of(generator)
        assert [
            "filtration" in chains.definitions[item].functions for item in chain
        ] == [True, False], (generator, chain)
        assert CLOSING_FUNCTIONS & set(chains.definitions[chain[-1]].functions)
        # Sul primo rettilineo, prima della curva, nell'ordine porta -> filtro -> valvola.
        found: list[float] = []
        for item in chain:
            symbol = chains.placed[item]
            centre = ((symbol.origin.x_mm + symbol.right_mm) / 2, (symbol.origin.y_mm + symbol.bottom_mm) / 2)
            off_axis = abs((centre[0] - port[0]) * axis[1] - (centre[1] - port[1]) * axis[0])
            assert off_axis <= TOLERANCE_MM, (generator, item, centre, port, axis)
            along = (centre[0] - port[0]) * axis[0] + (centre[1] - port[1]) * axis[1]
            assert 0 < along < length + TOLERANCE_MM, (generator, item, along, length)
            found.append(round(along, 6))
        assert found == sorted(found), (generator, found)
        first, second = (chains.placed[item] for item in chain)
        assert abs(_gap_to_point(first, *port) - CHAIN_PORT_GAP_MM) <= TOLERANCE_MM, generator
        assert abs(_gap_between(first, second) - MIN_SPACING_MM) <= TOLERANCE_MM, generator
        offsets[generator] = found
    values = list(offsets.values())
    assert values[0] == values[1], offsets


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_nessun_tubo_passa_sotto_la_catena(index: int) -> None:
    from disegnatore_mep.layout.geometry import intrudes_into

    project, drawing = _composed(index)
    chains = Chains(project, drawing)
    for generator in chains.generators():
        for item in chains.chain_of(generator):
            box = box_of(chains.placed[item])
            for route in chains.sheet.routes:
                for segment in route.segments:
                    assert not any(
                        intrudes_into(box, before, after) for before, after in moves_of(segment)
                    ), (generator, item, route.connection_ids)
