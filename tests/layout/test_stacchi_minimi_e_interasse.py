"""Le prove di DRAW-005-R1, blocco E nella correzione PM (I-046), scritte prima
del codice: gli stacchi sono lunghi il minimo, le macchine si spostano gratis.

Il Work Package:

1. la lunghezza degli stacchi di sicurezza, sfiato, misura, espansione e
   riempimento e' la **minima lunghezza su griglia** che evita il contatto fra
   tubo e ingombro del simbolo e conserva la leggibilita' di stampa; non e' una
   costante arbitraria;
2. ogni millimetro oltre il minimo peggiora il costo;
3. prima di introdurre curve, deviazioni o corridoi, il posatore prova la
   traslazione verticale delle macchine e dei gruppi collegati a passi di
   griglia: spostare le macchine costa zero;
4. i corridoi davanti alle porte sono locali e non possono impedire la posa
   degli altri impianti.

Impianti costruiti qui, salvo la regressione sulla fixture della tavola 1 in
coda: la rete a flusso ordinario non deve costare piu' di DRAW-005 — 4 curve,
1 incrocio, 525 mm — e quei tre numeri vivono **solo** in quella prova.
"""

import json
import math
from datetime import date
from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentTrait
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.canonical import canonical_json
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.chains import CHAIN_PORT_GAP_MM, MIN_SPACING_MM
from disegnatore_mep.layout.compose import compose_drawing, inline_component_ids
from disegnatore_mep.layout.geometry import (
    DrawingGeometry,
    FlowKind,
    PlacedSymbol,
    RoutedTrunk,
    SheetGeometry,
    moves_of,
)
from disegnatore_mep.layout.grid import GridSpace
from disegnatore_mep.layout.improve import LIFT_STEPS, Improver
from disegnatore_mep.layout.partition import partition_project
from disegnatore_mep.layout.place import (
    ROW_GAP_MM,
    place_sheet,
    port_corridors,
    stub_minimum_mm,
)
from disegnatore_mep.layout.trunks import Trunk, build_trunks
from disegnatore_mep.model.project import (
    ComponentInstance,
    ConnectionModel,
    NetworkModel,
    PortRef,
    ProjectMetadata,
    ProjectModel,
)
from disegnatore_mep.model.types import PlantRegime
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry
from disegnatore_mep.validation.geometry import validate_drawing_geometry
from disegnatore_mep.validation.preflight import preflight_drawing

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"
PROVA_1 = ROOT / "examples" / "prova" / "prova-1-due-pdc-accumulo-combinato.json"
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
) -> ProjectModel:
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-stacchi",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 9),
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
    )


def due_macchine_con_accumulo_combinato() -> ProjectModel:
    """Due pompe di calore in parallelo su un accumulo combinato, con
    riscaldamento e sanitario: la topologia della tavola 1, senza i suoi
    identificativi. Le regole la completano."""
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
    )


def una_macchina_con_accumulo_combinato() -> ProjectModel:
    return _plant(
        [("primo", HEATING), ("secondo", HEATING), ("fredda", COLD), ("calda", DHW)],
        [
            ("generatore", "heat-pump-air-water", "PDC-A"),
            ("serbatoio", "buffer-combined", "ACC-A"),
            ("pompa", "pump-circulator", "CIR-A"),
            ("corpo", "radiator", "RAD-A"),
            ("rete-idrica", "cold-water-inlet", "AF-A"),
            ("rubinetti", "dhw-draw-off", "ACS-A"),
        ],
        [
            _pipe("p1", "primo", ("generatore", "water_supply"), ("serbatoio", "primary_in")),
            _pipe("p2", "primo", ("serbatoio", "primary_out"), ("generatore", "water_return")),
            _pipe("s1", "secondo", ("serbatoio", "secondary_out"), ("pompa", "a")),
            _pipe("s2", "secondo", ("pompa", "b"), ("corpo", "in")),
            _pipe("s3", "secondo", ("corpo", "out"), ("serbatoio", "secondary_in")),
            _pipe("w1", "fredda", ("rete-idrica", "a"), ("serbatoio", "cold_in")),
            _pipe("w2", "calda", ("serbatoio", "dhw_out"), ("rubinetti", "a")),
        ],
    )


CASI = [una_macchina_con_accumulo_combinato, due_macchine_con_accumulo_combinato]
CASI_IDS = [item.__name__ for item in CASI]


@cache
def completato(index: int) -> ProjectModel:
    done, _, gaps = saturate(CASI[index](), catalog(), rules())
    assert not gaps, [(gap.rule_id, gap.reason.value) for gap in gaps]
    return done


@cache
def composto(index: int) -> DrawingGeometry:
    return compose_drawing(completato(index), catalog(), NOVE_C_A3)


def _trunks(project: ProjectModel) -> list[Trunk]:
    return build_trunks(project, inline_component_ids(project, catalog()))


def _stubs(project: ProjectModel) -> list[Trunk]:
    """Le tratte che pendono da uno stacco: un capo e' un attacco fuori dal
    percorso del fluido, secondo il catalogo."""
    definitions = {item.id: catalog().get(item.definition_id) for item in project.components}

    def off_the_run(ref: PortRef) -> bool:
        return any(
            port.id == ref.port_id and port.off_the_run
            for port in definitions[ref.component_id].ports
        )

    return [trunk for trunk in _trunks(project) if off_the_run(trunk.start) or off_the_run(trunk.end)]


def _length(route: RoutedTrunk) -> float:
    """Il tubo disegnato: i tratti, senza le interruzioni dei pezzi in linea."""
    return sum(
        abs(after.x_mm - before.x_mm) + abs(after.y_mm - before.y_mm)
        for segment in route.segments
        for before, after in moves_of(segment)
    )


def _span(route: RoutedTrunk) -> float:
    """Da porta a porta, pezzi in linea compresi: la lunghezza dello stacco."""
    first, last = route.segments[0][0], route.segments[-1][-1]
    return abs(last.x_mm - first.x_mm) + abs(last.y_mm - first.y_mm)


def _bends(route: RoutedTrunk) -> int:
    return sum(max(len(segment) - 2, 0) for segment in route.segments)


# ---------------------------------------------------------------------------
# E1 — il minimo dello stacco e' una funzione della tratta, non una costante
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_uno_stacco_vuoto_e_lungo_un_passo_e_uno_con_la_sua_catena_quanto_la_catena(
    index: int,
) -> None:
    project = completato(index)
    definitions = {item.id: catalog().get(item.definition_id) for item in project.components}
    step = grid().step_mm
    seen_empty = seen_chained = False
    for trunk in _stubs(project):
        minimum = stub_minimum_mm(project, catalog(), trunk, False, step)
        assert abs(minimum / step - round(minimum / step)) <= 1e-9, (trunk.connection_ids, minimum)
        if not trunk.inline_component_ids:
            # Due celle: la soglia dell'attacco del raccordo e quella
            # dell'attacco di chi pende (D-113), una per ciascuno.
            assert abs(minimum - 2 * step) <= TOLERANCE_MM, trunk.connection_ids
            seen_empty = True
        else:
            # La fila fra le due soglie: da ciascun attacco la soglia piu' un
            # passo (D-113, D-120), poi ogni pezzo con un passo dal vicino —
            # e niente altro.
            extents = [
                catalog().resolve(definitions[component_id].id).symbol.manifest.height_mm
                for component_id in trunk.inline_component_ids
            ]
            expected = 2 * CHAIN_PORT_GAP_MM + sum(extents) + MIN_SPACING_MM * (len(extents) - 1)
            assert abs(minimum - math.ceil(expected / step - 1e-9) * step) <= TOLERANCE_MM, (
                trunk.connection_ids,
                minimum,
                expected,
            )
            seen_chained = True
    assert seen_empty and seen_chained


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_nella_posa_iniziale_ogni_stacco_e_lungo_il_proprio_minimo(index: int) -> None:
    """Il posatore siede ogni appeso al minimo dal proprio raccordo; se e'
    piu' lontano e' perche' **il posto era preso** — da un simbolo, o dal
    rettilineo che una catena pretende davanti a una porta — e lo si deve
    vedere: un passo piu' vicino, l'appeso toccherebbe qualcuno."""
    project = completato(index)
    inline = inline_component_ids(project, catalog())
    partition = partition_project(project, build_trunks(project, inline))[0]
    laid = place_sheet(project, partition, catalog(), NOVE_C_A3, inline)
    placed = {item.component_id: item for item in laid}
    step = grid().step_mm
    corridors = port_corridors(project, catalog(), partition.trunks, laid, step)

    def taken(item: PlacedSymbol, dx: float, dy: float) -> bool:
        """Spostato di `(dx, dy)`, il riquadro tocca un altro simbolo — a meno
        di un passo — o un corridoio davanti a una porta."""
        left, top = item.origin.x_mm + dx, item.origin.y_mm + dy
        right, bottom = left + item.width_mm, top + item.height_mm
        if any(
            left < x1 - TOLERANCE_MM
            and x0 < right - TOLERANCE_MM
            and top < y1 - TOLERANCE_MM
            and y0 < bottom - TOLERANCE_MM
            for x0, y0, x1, y1 in corridors
        ):
            return True
        return any(
            other.component_id != item.component_id
            and left < other.origin.x_mm + other.width_mm + step
            and other.origin.x_mm - step < right
            and top < other.origin.y_mm + other.height_mm + step
            and other.origin.y_mm - step < bottom
            for other in laid
        )

    checked = 0
    for trunk in _stubs(project):
        parent, child = (
            (trunk.start, trunk.end) if trunk.end.component_id in placed and trunk.start.component_id in placed else (None, None)
        )
        if parent is None or child is None:
            continue
        holder, hung = placed[parent.component_id], placed[child.component_id]
        if len(catalog().get(next(item.definition_id for item in project.components if item.id == hung.component_id)).ports) != 1:
            holder, hung = hung, holder
            parent, child = child, parent
        stub = _port(project, holder, parent.port_id)
        own = _port(project, hung, child.port_id)
        gap = max(abs(own[0] - stub[0]), abs(own[1] - stub[1]))
        horizontal = abs(own[1] - stub[1]) <= TOLERANCE_MM
        minimum = stub_minimum_mm(project, catalog(), trunk, horizontal, step)
        assert gap >= minimum - TOLERANCE_MM, (child.component_id, gap, minimum)
        if gap > minimum + TOLERANCE_MM:
            # Un passo piu' vicino al raccordo il posto e' preso: lo stacco
            # e' lungo per necessita', non per una costante.
            towards = (
                (-step if own[0] > stub[0] else step, 0.0)
                if horizontal
                else (0.0, -step if own[1] > stub[1] else step)
            )
            assert taken(hung, *towards), (child.component_id, gap, minimum)
        checked += 1
    assert checked >= 4


def _port(project: ProjectModel, item: PlacedSymbol, port_id: str) -> tuple[float, float]:
    definition_id = next(
        component.definition_id for component in project.components if component.id == item.component_id
    )
    manifest = catalog().resolve(definition_id).symbol.manifest.rotated(item.rotation_deg)
    port = manifest.port(item.physical_port(port_id))
    return (item.origin.x_mm + port.x_mm, item.origin.y_mm + port.y_mm)


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_sulla_tavola_composta_nessuno_stacco_e_piu_lungo_del_minimo_senza_una_ragione(
    index: int,
) -> None:
    """Dopo il ciclo, uno stacco piu' lungo del minimo e' uno stacco che il
    ciclo ha allungato per liberare una riga, e lo si vede: e' una retta con
    una curva o un incrocio in meno altrove. Qui si pretende il minimo per
    ogni stacco dritto e senza incroci: allungarlo non avrebbe comprato
    niente."""
    project = completato(index)
    drawing = composto(index)
    sheet = drawing.sheets[0]
    by_key = {tuple(route.connection_ids): route for route in sheet.routes}
    step = grid().step_mm
    checked = 0
    for trunk in _stubs(project):
        route = by_key.get(tuple(trunk.connection_ids))
        if route is None:
            continue
        assert route.flow_kind is not FlowKind.ORDINARY, trunk.connection_ids
        minimum = stub_minimum_mm(
            project,
            catalog(),
            trunk,
            all(
                abs(after.y_mm - before.y_mm) <= TOLERANCE_MM
                for segment in route.segments
                for before, after in moves_of(segment)
            ),
            step,
        )
        if _bends(route) == 0 and not route.crossings:
            assert _span(route) >= minimum - TOLERANCE_MM, (
                trunk.connection_ids,
                _span(route),
                minimum,
            )
            if _span(route) > minimum + TOLERANCE_MM:
                # Piu' lungo del minimo solo se un passo piu' vicino il posto
                # e' preso: da un simbolo, o dal rettilineo che una catena
                # pretende davanti a una porta.
                assert _taken_one_step_closer(project, sheet, trunk, step), (
                    trunk.connection_ids,
                    _span(route),
                    minimum,
                )
            checked += 1
    assert checked >= 3


def _taken_one_step_closer(
    project: ProjectModel, sheet: SheetGeometry, trunk: Trunk, step: float
) -> bool:
    """Vero se, avvicinando di un passo al proprio raccordo l'accessorio che
    pende da questo stacco, il suo riquadro toccherebbe qualcuno o entrerebbe
    nel rettilineo che una catena pretende davanti a una porta."""
    definitions = {item.id: catalog().get(item.definition_id) for item in project.components}
    placed = {item.component_id: item for item in sheet.symbols}
    child_id = (
        trunk.end.component_id
        if len(definitions[trunk.start.component_id].ports) != 1
        else trunk.start.component_id
    )
    parent_id = (
        trunk.start.component_id if child_id == trunk.end.component_id else trunk.end.component_id
    )
    child, parent = placed[child_id], placed[parent_id]
    towards = (
        (step if parent.origin.x_mm > child.origin.x_mm else -step, 0.0)
        if abs(parent.origin.y_mm - child.origin.y_mm) <= TOLERANCE_MM
        else (0.0, step if parent.origin.y_mm > child.origin.y_mm else -step)
    )
    left, top = child.origin.x_mm + towards[0], child.origin.y_mm + towards[1]
    right, bottom = left + child.width_mm, top + child.height_mm
    corridors = port_corridors(
        project, catalog(), _trunks(project), list(sheet.symbols), step
    )
    if any(
        left < x1 - TOLERANCE_MM
        and x0 < right - TOLERANCE_MM
        and top < y1 - TOLERANCE_MM
        and y0 < bottom - TOLERANCE_MM
        for x0, y0, x1, y1 in corridors
    ):
        return True
    return any(
        other.component_id not in (child_id, parent_id)
        and left < other.origin.x_mm + other.width_mm + step
        and other.origin.x_mm - step < right
        and top < other.origin.y_mm + other.height_mm + step
        and other.origin.y_mm - step < bottom
        for other in sheet.symbols
    )


# ---------------------------------------------------------------------------
# E3, E4 — spostare le macchine costa zero, e si prova per primo
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_il_ciclo_prova_per_prima_la_traslazione_verticale_di_una_macchina(index: int) -> None:
    project = completato(index)
    inline = inline_component_ids(project, catalog())
    partition = partition_project(project, build_trunks(project, inline))[0]
    placed = place_sheet(project, partition, catalog(), NOVE_C_A3, inline)
    improver = Improver(project, partition, catalog(), NOVE_C_A3, placed, inline)
    generators = [
        item.id
        for item in project.components
        if "heat_generation" in catalog().get(item.definition_id).functions
    ]
    for generator in generators:
        kinds = improver.candidates_by_kind(generator)
        assert kinds, generator
        first_kind, first_move = kinds[0]
        assert first_kind == "interasse", first_kind
        before = improver.best[generator]
        after = first_move[generator]
        assert after.origin.x_mm == before.origin.x_mm
        assert abs(abs(after.origin.y_mm - before.origin.y_mm) - LIFT_STEPS[0] * grid().step_mm) <= TOLERANCE_MM
        # In tutte e due le direzioni, vicino prima che lontano, e tutte valide
        # finche' restano dentro l'area: la quota di chi sta a terra e' libera.
        lifts = [move for kind, move in kinds if kind == "interasse"]
        assert len(lifts) == 2 * len(LIFT_STEPS)
        inside = [
            move
            for move in lifts
            if move[generator].origin.y_mm >= NOVE_C_A3.drawing_rect_mm.y_mm
            and move[generator].bottom_mm <= improver.levels.ground_mm + TOLERANCE_MM
        ]
        assert inside
        assert all(improver.is_valid(move) for move in inside), generator


def test_traslare_una_macchina_non_cambia_il_suo_riquadro_ne_stacca_cio_che_le_pende() -> None:
    project = completato(0)
    inline = inline_component_ids(project, catalog())
    partition = partition_project(project, build_trunks(project, inline))[0]
    placed = place_sheet(project, partition, catalog(), NOVE_C_A3, inline)
    improver = Improver(project, partition, catalog(), NOVE_C_A3, placed, inline)
    reserve = next(
        item.id
        for item in project.components
        if catalog().get(item.definition_id).has_trait(ComponentTrait.HOLDS_ITS_OWN_VOLUME)
    )
    lifts = [move for kind, move in improver.candidates_by_kind(reserve) if kind == "interasse"]
    assert lifts
    for move in lifts:
        dy = move[reserve].origin.y_mm - improver.best[reserve].origin.y_mm
        assert move[reserve].width_mm == improver.best[reserve].width_mm
        assert move[reserve].height_mm == improver.best[reserve].height_mm
        for child, _port_id in improver.children.get(reserve, ()):
            assert child in move, child
            assert abs((move[child].origin.y_mm - improver.best[child].origin.y_mm) - dy) <= TOLERANCE_MM


# ---------------------------------------------------------------------------
# La tavola 1, letta come fixture di regressione: la rete ordinaria non costa
# piu' di DRAW-005 — i tre numeri vivono solo qui
# ---------------------------------------------------------------------------


def _ordinary_and_static(drawing: DrawingGeometry) -> tuple[dict[str, float], dict[str, float]]:
    sheet = drawing.sheets[0]
    stub_points = {
        (round(point.x_mm, 3), round(point.y_mm, 3))
        for route in sheet.routes
        if route.flow_kind is not FlowKind.ORDINARY
        for point in route.crossings
    }
    ordinary = {"curve": 0.0, "incroci": 0.0, "mm": 0.0}
    static = {"curve": 0.0, "incroci": 0.0, "mm": 0.0}
    for route in sheet.routes:
        is_stub = route.flow_kind is not FlowKind.ORDINARY
        bucket = static if is_stub else ordinary
        bucket["curve"] += _bends(route)
        bucket["mm"] += _length(route)
        bucket["incroci"] += sum(
            1
            for point in route.crossings
            if is_stub or (round(point.x_mm, 3), round(point.y_mm, 3)) not in stub_points
        )
    return ordinary, static


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_il_raccordo_che_regge_uno_stacco_sta_stretto_al_raccordo_a_cui_e_attaccato(
    index: int,
) -> None:
    """La sicurezza di circuito sta «vicino al gruppo» (I-046) perche' il suo
    raccordo sta stretto alla confluenza da cui la regola l'ha fatta pendere:
    lungo una retta la lunghezza totale del tubo non cambia spostandolo, e
    nessun costo lo terrebbe li'. Vale per ogni raccordo che regge soltanto
    uno stacco statico — il manometro, il riempimento, il vaso — attaccato a
    un altro raccordo da una tratta vuota: non c'e' niente da posare in
    mezzo, e ogni passo in piu' e' tubo che allontana l'accessorio da cio' a
    cui appartiene."""
    project = completato(index)
    drawing = composto(index)
    sheet = drawing.sheets[0]
    placed = {item.component_id: item for item in sheet.symbols}
    definitions = {item.id: catalog().get(item.definition_id) for item in project.components}
    # Chi regge uno stacco: il capo con piu' di un attacco, cioe' il raccordo
    # (o la macchina) da cui l'accessorio pende.
    holders = {
        trunk.end.component_id
        if len(definitions[trunk.start.component_id].ports) == 1
        else trunk.start.component_id
        for trunk in _stubs(project)
    }
    checked = 0
    for trunk in _trunks(project):
        head, tail = trunk.start.component_id, trunk.end.component_id
        if trunk.inline_component_ids or head not in placed or tail not in placed:
            continue
        if not (definitions[head].is_a_fitting and definitions[tail].is_a_fitting):
            continue
        if head not in holders and tail not in holders:
            continue
        stub = _port(project, placed[head], trunk.start.port_id)
        own = _port(project, placed[tail], trunk.end.port_id)
        span = abs(own[0] - stub[0]) + abs(own[1] - stub[1])
        assert span <= ROW_GAP_MM + TOLERANCE_MM, (trunk.connection_ids, span)
        checked += 1
    assert checked >= 1


def test_la_tavola_1_non_costa_piu_di_draw_005_sulla_rete_ordinaria() -> None:
    """Regressione sulla fixture della tavola 1 (DRAW-006, §E.4).

    La tavola 1 non si riconsegna piu' come elaborato: resta una **regressione
    automatica**, e le soglie sono quelle della consegna approvata di
    DRAW-005-R1, non piu' quelle piu' larghe di DRAW-005. Rete ordinaria: non
    oltre 4 curve, 1 incrocio e 425 mm. Stacchi statici: non oltre 0 curve,
    0 incroci e 45 mm. E le tre qualita' che non hanno numero — zero
    backtracking, zero tubo sotto un simbolo, nessuna tratta oltre tre curve —
    lette dai validatori invece che ricontate qui.
    """
    done, _, gaps = saturate(load_project(PROVA_1), catalog(), rules())
    assert not gaps
    # Il modello passa dal JSON canonico, come nella catena della CLI: la
    # geometria dipende ancora dall'ordine delle connessioni (fuori perimetro,
    # DRAW-005 §8), e la tavola che si giudica e' quella che la CLI scrive.
    canonical = ProjectModel.model_validate(json.loads(canonical_json(done)))
    drawing = compose_drawing(canonical, catalog(), NOVE_C_A3)
    ordinary, static = _ordinary_and_static(drawing)
    assert ordinary["curve"] <= 4, ordinary
    assert ordinary["incroci"] <= 1, ordinary
    assert ordinary["mm"] <= 425.0 + TOLERANCE_MM, ordinary
    assert static["curve"] <= 0, static
    assert static["incroci"] <= 0, static
    assert static["mm"] <= 45.0 + TOLERANCE_MM, static
    assert static["mm"] > 0
    # E gli stacchi sono tubo nuovo, contato a parte: nessuno oltre tre curve,
    # e nessuno che rientri su se stesso.
    for route in drawing.sheets[0].routes:
        if route.flow_kind is not FlowKind.ORDINARY:
            assert _bends(route) <= 3, route.connection_ids
    codes = {
        item.code
        for item in (
            *validate_drawing_geometry(drawing, NOVE_C_A3).issues,
            *preflight_drawing(drawing, NOVE_C_A3, catalog()),
        )
    }
    for code in ("LINE_UNDER_SYMBOL", "RUN_OVERSHOOTS_ITS_PORT", "RUN_WITH_TOO_MANY_BENDS"):
        assert code not in codes, sorted(codes)
