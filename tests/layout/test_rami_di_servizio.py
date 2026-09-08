"""Le prove di DRAW-005-R1, blocco B, scritte prima del codice: medium, colore
e frecce dei rami di servizio (I-042).

La traduzione PM (`docs/pm/2026-09-08-rilievi-po-draw005-r1.md`):

- il colore deriva dalla **rete del tratto**, non dalla direzione grafica del ramo:
  lo stacco di manometro, vaso e riempimento innestato sul ritorno tecnico e' del
  ritorno tecnico, blu;
- la freccia compare solo quando esiste un flusso ordinario diretto;
- riempimento: flusso verso la rete tecnica, la freccia punta dal gruppo verso il
  circuito;
- misura, espansione, sfiato e sicurezza su stacco: nessuna freccia di circolazione;
- eventuale scarico esplicitamente modellato: freccia verso lo scarico;
- il componente `P` resta un manometro.

La semantica e' **generale**: tre specie di tratto — flusso ordinario, ramo statico,
scarico — piu' l'ingresso del riempimento, decise sul modello e sul catalogo, senza
coordinate, senza identificativi e senza colori scritti a mano nel renderer.
Impianti costruiti qui, con il catalogo di prova.
"""

import math
import re
from datetime import date
from functools import cache
from pathlib import Path
from xml.etree import ElementTree

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import ARROW_LENGTH_MM, render_sheet
from disegnatore_mep.layout import flow as flow_module
from disegnatore_mep.layout.compose import compose_drawing, inline_component_ids
from disegnatore_mep.layout.flow import classify_trunks
from disegnatore_mep.layout.geometry import (
    DrawingGeometry,
    FlowKind,
    Point,
    RoutedTrunk,
    SheetGeometry,
    moves_of,
)
from disegnatore_mep.layout.legend import style_for
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
Pt = tuple[float, float]


@cache
def symbols() -> SymbolRegistry:
    return SymbolRegistry.from_directory(SYMBOLS)


@cache
def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(CATALOG, symbols=symbols())


@cache
def rules() -> RuleRegistry:
    registry = RuleRegistry.from_directory(RULES)
    registry.cross_check(catalog())
    return registry


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
    subsystems: list[tuple[str, list[str], list[str]]],
) -> ProjectModel:
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-rami",
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
            for item, members, nets in subsystems
        ],
    )


def una_macchina_con_accumulo_combinato() -> ProjectModel:
    return _plant(
        [("primo", HEATING), ("secondo", HEATING), ("fredda", COLD), ("calda", DHW)],
        [
            ("generatore", "heat-pump-air-water", "PDC-01"),
            ("serbatoio", "buffer-combined", "ACC-01"),
            ("pompa", "pump-circulator", "CIR-01"),
            ("corpo", "radiator", "RAD-01"),
            ("rete-idrica", "cold-water-inlet", "AF-01"),
            ("rubinetti", "dhw-draw-off", "ACS-01"),
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
        [
            ("generazione", ["generatore"], ["primo"]),
            ("accumulo", ["serbatoio", "rete-idrica", "rubinetti"], ["primo", "fredda", "calda"]),
            ("distribuzione", ["pompa", "corpo"], ["secondo"]),
        ],
    )


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


CASI = (una_macchina_con_accumulo_combinato, due_macchine_con_accumulo_combinato)
CASI_IDS = [item.__name__ for item in CASI]


@cache
def _done(index: int) -> ProjectModel:
    done, _, gaps = saturate(CASI[index](), catalog(), rules())
    assert not gaps, [(gap.rule_id, gap.reason.value) for gap in gaps]
    return done


def _trunks(project: ProjectModel) -> list[Trunk]:
    return build_trunks(project, inline_component_ids(project, catalog()))


@cache
def _drawing(index: int) -> DrawingGeometry:
    return compose_drawing(_done(index), catalog(), NOVE_C_A3)


# ---------------------------------------------------------------------------
# Come si leggono gli stacchi sul modello, senza guardare la tavola
# ---------------------------------------------------------------------------


class Branches:
    """Gli stacchi di un modello completato: da chi pendono e cosa reggono."""

    def __init__(self, project: ProjectModel) -> None:
        self.project = project
        registry = catalog()
        self.definitions = {
            item.id: registry.get(item.definition_id) for item in project.components
        }
        self.trunks = _trunks(project)
        self.by_key = {trunk.connection_ids: trunk for trunk in self.trunks}

    def off_the_run(self, ref: PortRef) -> bool:
        return any(
            port.id == ref.port_id and port.off_the_run
            for port in self.definitions[ref.component_id].ports
        )

    def root_of(self, trunk: Trunk) -> PortRef | None:
        """L'attacco fuori dal percorso da cui lo stacco parte, se e' uno stacco."""
        for ref in (trunk.start, trunk.end):
            if self.off_the_run(ref):
                return ref
        return None

    def far_end_of(self, trunk: Trunk) -> str:
        root = self.root_of(trunk)
        assert root is not None
        return trunk.end.component_id if root == trunk.start else trunk.start.component_id

    def functions(self, component_id: str) -> frozenset[str]:
        return frozenset(self.definitions[component_id].functions)

    def branches_with(self, function: str) -> list[Trunk]:
        return [
            trunk
            for trunk in self.trunks
            if self.root_of(trunk) is not None
            and function in self.functions(self.far_end_of(trunk))
        ]

    def host_of(self, trunk: Trunk) -> list[Trunk]:
        """Le tratte del percorso che passano per chi regge lo stacco, se chi lo
        regge e' un raccordo; vuoto se e' una macchina."""
        root = self.root_of(trunk)
        assert root is not None
        if not self.definitions[root.component_id].is_a_fitting:
            return []
        return [
            other
            for other in self.trunks
            if other is not trunk
            and any(
                ref.component_id == root.component_id and not self.off_the_run(ref)
                for ref in (other.start, other.end)
            )
        ]


STATIC_FUNCTIONS = ("pressure_measurement", "expansion", "safety", "air_release")
"""Chi pende da uno stacco senza portare una circolazione ordinaria."""


# ---------------------------------------------------------------------------
# B1 — la specie del tratto si decide sul modello e sul catalogo
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_ogni_stacco_prende_la_specie_dalla_funzione_di_cio_che_regge(index: int) -> None:
    project = _done(index)
    branches = Branches(project)
    kinds = classify_trunks(project, catalog(), branches.trunks)
    seen: set[str] = set()
    for function in STATIC_FUNCTIONS:
        for trunk in branches.branches_with(function):
            assert kinds[trunk.connection_ids].kind is FlowKind.STATIC, (function, trunk)
            seen.add(function)
    for trunk in branches.branches_with("filling"):
        assert kinds[trunk.connection_ids].kind is FlowKind.INBOUND, trunk
        seen.add("filling")
    for trunk in branches.branches_with("drain"):
        assert kinds[trunk.connection_ids].kind is FlowKind.OUTBOUND, trunk
        seen.add("drain")
    assert {"pressure_measurement", "expansion", "safety", "air_release", "filling", "drain"} <= seen, seen
    for trunk in branches.trunks:
        if branches.root_of(trunk) is None:
            assert kinds[trunk.connection_ids].kind is FlowKind.ORDINARY, trunk


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_lo_stacco_su_un_raccordo_ha_il_servizio_della_tratta_che_lo_regge(index: int) -> None:
    """Manometro, vaso e riempimento pendono dal ritorno tecnico: sono ritorno.
    La sicurezza sulla mandata pende dalla mandata: e' mandata. Lo dice la
    tratta ospite, mai il verso in cui lo stacco e' disegnato."""
    project = _done(index)
    branches = Branches(project)
    kinds = classify_trunks(project, catalog(), branches.trunks)
    checked = 0
    for trunk in branches.trunks:
        if branches.root_of(trunk) is None:
            continue
        hosts = branches.host_of(trunk)
        if not hosts:
            continue
        host_services = {kinds[host.connection_ids].supply for host in hosts}
        assert len(host_services) == 1, (trunk, host_services)
        assert host_services != {None}, (trunk, "la tratta ospite deve essere decisa dalla topologia")
        assert kinds[trunk.connection_ids].supply == host_services.pop(), trunk
        checked += 1
    assert checked >= 4, checked


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_con_due_macchine_in_parallelo_nessuna_tratta_del_primario_resta_indecisa(index: int) -> None:
    """La seconda macchina in parallelo non si raggiunge dalla sorgente unica
    della posa: per il colore si cammina da ogni generatore, e mandata e
    ritorno di ciascuna macchina hanno il proprio servizio."""
    project = _done(index)
    trunks = _trunks(project)
    kinds = classify_trunks(project, catalog(), trunks)
    registry = catalog()
    definitions = {item.id: registry.get(item.definition_id) for item in project.components}
    generators = [
        item.id for item in project.components if "heat_generation" in definitions[item.id].functions
    ]
    for generator in generators:
        for trunk in trunks:
            for ref in (trunk.start, trunk.end):
                if ref.component_id != generator:
                    continue
                flow = next(port.flow for port in definitions[generator].ports if port.id == ref.port_id)
                expected = flow is PortFlow.OUT
                assert kinds[trunk.connection_ids].supply is expected, (generator, trunk)


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_riempimento_vaso_e_manometro_sono_ritorno_tecnico(index: int) -> None:
    project = _done(index)
    branches = Branches(project)
    kinds = classify_trunks(project, catalog(), branches.trunks)
    for function in ("filling", "expansion", "pressure_measurement"):
        found = branches.branches_with(function)
        assert found, function
        for trunk in found:
            assert kinds[trunk.connection_ids].supply is False, (function, trunk)
    for trunk in branches.branches_with("safety"):
        root = branches.root_of(trunk)
        assert root is not None
        if branches.definitions[root.component_id].is_a_fitting:
            assert kinds[trunk.connection_ids].supply is True, trunk


def test_la_classificazione_non_legge_nessuna_coordinata() -> None:
    """La firma della classificazione: modello, catalogo, tratte. Niente di
    posato, niente di instradato puo' entrarci."""
    import inspect

    parameters = list(inspect.signature(classify_trunks).parameters)
    assert parameters == ["project", "catalog", "trunks"], parameters


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_riordinare_il_file_non_cambia_specie_ne_servizio(index: int) -> None:
    project = _done(index)
    permuted = project.model_copy(
        update={
            "components": list(reversed(project.components)),
            "connections": list(reversed(project.connections)),
        }
    )
    first = {
        frozenset(key): (value.kind, value.supply)
        for key, value in classify_trunks(project, catalog(), _trunks(project)).items()
    }
    second = {
        frozenset(key): (value.kind, value.supply)
        for key, value in classify_trunks(permuted, catalog(), _trunks(permuted)).items()
    }
    assert first == second


def test_il_verso_del_flusso_ordinario_e_quello_del_modello_non_della_spezzata() -> None:
    """Una tratta che il file elenca dal capo che entra va disegnata al contrario:
    la freccia segue il verso out -> in del catalogo."""
    project = _done(0)
    trunks = _trunks(project)
    kinds = classify_trunks(project, catalog(), trunks)
    registry = catalog()
    definitions = {item.id: item.definition_id for item in project.components}
    for trunk in trunks:
        if kinds[trunk.connection_ids].kind is not FlowKind.ORDINARY:
            continue
        start = registry.get(definitions[trunk.start.component_id])
        flow = next(port.flow for port in start.ports if port.id == trunk.start.port_id)
        if flow is PortFlow.OUT:
            assert kinds[trunk.connection_ids].flow_from_start is True, trunk
        elif flow is PortFlow.IN:
            assert kinds[trunk.connection_ids].flow_from_start is False, trunk


# ---------------------------------------------------------------------------
# B2 — la tavola composta porta quella semantica, e il renderer la rispetta
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_ogni_tratta_instradata_porta_specie_e_servizio_della_classificazione(index: int) -> None:
    project = _done(index)
    kinds = classify_trunks(project, catalog(), _trunks(project))
    sheet = _drawing(index).sheets[0]
    assert sheet.routes
    for route in sheet.routes:
        expected = kinds[tuple(route.connection_ids)]
        assert route.flow_kind is expected.kind, route.connection_ids
        assert route.flow_from_start == expected.flow_from_start, route.connection_ids
        if expected.supply is not None:
            assert route.supply == expected.supply, route.connection_ids


def _arrows(root: ElementTree.Element) -> list[tuple[Pt, Pt]]:
    """Punta e base di ogni freccia di verso sulle tubazioni."""
    found: list[tuple[Pt, Pt]] = []
    for item in root.iter():
        if item.get("class") != "flow-arrow":
            continue
        numbers = [
            float(value)
            for value in item.get("d", "").replace("M", " ").replace("L", " ").replace("Z", " ").split()
        ]
        tip = (numbers[0], numbers[1])
        base = ((numbers[2] + numbers[4]) / 2, (numbers[3] + numbers[5]) / 2)
        found.append((tip, base))
    return found


def _on_route(point: Pt, route: RoutedTrunk) -> bool:
    for segment in route.segments:
        for before, after in moves_of(segment):
            cross = (after.x_mm - before.x_mm) * (point[1] - before.y_mm) - (
                after.y_mm - before.y_mm
            ) * (point[0] - before.x_mm)
            if abs(cross) > 1e-3:
                continue
            if (
                min(before.x_mm, after.x_mm) - 1e-3 <= point[0] <= max(before.x_mm, after.x_mm) + 1e-3
                and min(before.y_mm, after.y_mm) - 1e-3 <= point[1] <= max(before.y_mm, after.y_mm) + 1e-3
            ):
                return True
    return False


def _arrow_stations(route: RoutedTrunk) -> list[tuple[Pt, Pt]]:
    """Dove il renderer mette la freccia di ogni pezzo di spezzata — a meta'
    del tratto piu' lungo, se lungo abbastanza — e il verso di quel tratto
    letto da `start` a `end`. E' la stessa regola del renderer, rifatta qui
    perche' la prova sappia dove guardare senza fidarsi di lui."""
    found: list[tuple[Pt, Pt]] = []
    for segment in route.segments:
        moves = moves_of(segment)
        if not moves:
            continue
        before, after = max(
            moves, key=lambda pair: abs(pair[1].x_mm - pair[0].x_mm) + abs(pair[1].y_mm - pair[0].y_mm)
        )
        length = abs(after.x_mm - before.x_mm) + abs(after.y_mm - before.y_mm)
        if length < 2 * ARROW_LENGTH_MM:
            continue
        found.append(
            (
                ((before.x_mm + after.x_mm) / 2, (before.y_mm + after.y_mm) / 2),
                ((after.x_mm - before.x_mm) / length, (after.y_mm - before.y_mm) / length),
            )
        )
    return found


def _arrow_at(arrows: list[tuple[Pt, Pt]], point: Pt, along: Pt) -> list[float]:
    """Le frecce con la punta in quel punto e parallele a quel verso: il
    prodotto scalare fra la loro direzione e il verso del tratto."""
    found: list[float] = []
    for tip, base in arrows:
        if abs(tip[0] - point[0]) > 1e-3 or abs(tip[1] - point[1]) > 1e-3:
            continue
        heading = (tip[0] - base[0], tip[1] - base[1])
        norm = math.hypot(*heading)
        dot = (heading[0] * along[0] + heading[1] * along[1]) / norm
        if abs(dot) > 0.5:
            found.append(dot)
    return found


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_nessuna_freccia_sui_rami_statici_e_la_freccia_giusta_sugli_altri(index: int) -> None:
    """Sui rami statici nessuna freccia; su tutti gli altri una freccia per
    pezzo di spezzata, nel verso che la specie prescrive."""
    sheet = _drawing(index).sheets[0]
    root = ElementTree.fromstring(render_sheet(sheet, NOVE_C_A3, symbols()))
    arrows = _arrows(root)
    assert arrows
    static = [route for route in sheet.routes if route.flow_kind is FlowKind.STATIC]
    assert static
    for route in sheet.routes:
        stations = _arrow_stations(route)
        if route.flow_kind is FlowKind.STATIC:
            for point, along in stations:
                assert not _arrow_at(arrows, point, along), (route.connection_ids, point)
            continue
        assert stations, route.connection_ids
        for point, along in stations:
            dots = _arrow_at(arrows, point, along)
            assert len(dots) == 1, (route.connection_ids, point, dots)
            assert (dots[0] > 0) == route.flow_from_start, (route.connection_ids, route.flow_kind)


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_il_riempimento_punta_verso_il_circuito_e_lo_scarico_verso_fuori(index: int) -> None:
    """Letto sulla geometria: la freccia dell'ingresso va verso il capo che sta
    sul percorso, quella dello scarico se ne allontana."""
    project = _done(index)
    branches = Branches(project)
    sheet = _drawing(index).sheets[0]
    by_key = {tuple(route.connection_ids): route for route in sheet.routes}
    for function, towards_root in (("filling", True), ("drain", False)):
        found = branches.branches_with(function)
        assert found, function
        for trunk in found:
            route = by_key[trunk.connection_ids]
            root_at_start = branches.root_of(trunk) == trunk.start
            # La spezzata va da start a end: verso il capo radice vuol dire
            # contro la spezzata se la radice sta all'inizio.
            expected_from_start = (not root_at_start) if towards_root else root_at_start
            assert route.flow_from_start == expected_from_start, (function, trunk)


@pytest.mark.parametrize("index", range(len(CASI)), ids=CASI_IDS)
def test_il_colore_dello_stacco_e_quello_della_tratta_ospite(index: int) -> None:
    project = _done(index)
    branches = Branches(project)
    sheet = _drawing(index).sheets[0]
    root = ElementTree.fromstring(render_sheet(sheet, NOVE_C_A3, symbols()))
    by_key = {tuple(route.connection_ids): route for route in sheet.routes}
    polylines = [item for item in root.iter() if item.get("class") == "run"]

    def stroke_of(route: RoutedTrunk) -> set[str]:
        found: set[str] = set()
        for item in polylines:
            points = [
                tuple(float(value) for value in pair.split(","))
                for pair in item.get("points", "").split()
            ]
            if all(_on_route((x, y), route) for x, y in points):
                found.add(item.get("stroke", ""))
        return found

    checked = 0
    for trunk in branches.trunks:
        if branches.root_of(trunk) is None:
            continue
        hosts = branches.host_of(trunk)
        if not hosts:
            continue
        route = by_key[trunk.connection_ids]
        host = by_key[hosts[0].connection_ids]
        expected = style_for(host.medium, host.supply)[0]
        assert stroke_of(route) == {expected}, (trunk.connection_ids, stroke_of(route), expected)
        assert route.medium == host.medium
        checked += 1
    assert checked >= 4


def test_il_renderer_disegna_la_freccia_secondo_la_specie_e_non_secondo_la_geometria() -> None:
    """Quattro tratte identiche sulla carta, quattro specie: la freccia cambia
    solo per la specie dichiarata."""
    segment = [Point(x_mm=100.0, y_mm=100.0), Point(x_mm=140.0, y_mm=100.0)]
    routes = [
        RoutedTrunk(
            network_id="n",
            medium=HEATING,
            supply=False,
            connection_ids=[name],
            segments=[[point.model_copy(update={"y_mm": 100.0 + 20.0 * offset}) for point in segment]],
            flow_kind=kind,
            flow_from_start=from_start,
        )
        for offset, (name, kind, from_start) in enumerate(
            (
                ("ordinaria", FlowKind.ORDINARY, True),
                ("statica", FlowKind.STATIC, True),
                ("ingresso", FlowKind.INBOUND, False),
                ("scarico", FlowKind.OUTBOUND, True),
            )
        )
    ]
    sheet = SheetGeometry(sheet_id="t", title="prova", routes=routes)
    root = ElementTree.fromstring(render_sheet(sheet, NOVE_C_A3, symbols()))
    arrows = _arrows(root)
    assert len(arrows) == 3
    for route in routes:
        mine = [(tip, base) for tip, base in arrows if _on_route(tip, route)]
        if route.flow_kind is FlowKind.STATIC:
            assert not mine
            continue
        assert len(mine) == 1, route.connection_ids
        tip, base = mine[0]
        assert (tip[0] > base[0]) == route.flow_from_start, route.connection_ids


def test_una_geometria_agli_atti_senza_specie_si_legge_ancora_come_flusso_ordinario() -> None:
    route = RoutedTrunk.model_validate(
        {"network_id": "n", "medium": HEATING, "supply": True, "connection_ids": ["x"], "segments": []}
    )
    assert route.flow_kind is FlowKind.ORDINARY
    assert route.flow_from_start is True


# ---------------------------------------------------------------------------
# B3 — niente colori scritti a mano nel renderer, e il manometro resta tale
# ---------------------------------------------------------------------------


def test_il_renderer_non_conosce_ne_colori_ne_nomi_di_pezzi() -> None:
    from disegnatore_mep.graphics import sheet as sheet_module

    text = Path(sheet_module.__file__).read_text(encoding="utf-8")
    assert not re.search(r"#[0-9a-fA-F]{6}\b", text), "un colore scritto a mano nel renderer"
    for word in ("filling", "gauge", "manometro", "expansion", "strainer", "pdc"):
        assert word not in text.lower(), word
    flow_text = Path(flow_module.__file__).read_text(encoding="utf-8")
    for word in ("pdc-master", "pdc-slave", "collettore-mandata", "collettore-ritorno", "x_mm", "y_mm"):
        assert word not in flow_text, word


def test_il_pezzo_che_misura_la_pressione_e_un_manometro() -> None:
    definition = catalog().providing("pressure_measurement", HEATING)
    assert definition.name.strip().lower() == "manometro"
    manifest = symbols().get(definition.symbol_id).manifest
    assert manifest.name.strip().lower() == "manometro"
    for item in catalog().all():
        assert "pressostat" not in item.name.lower(), item.id
    for symbol in symbols().all():
        assert "pressostat" not in symbol.manifest.name.lower(), symbol.manifest.id
