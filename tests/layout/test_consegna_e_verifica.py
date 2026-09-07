"""Consegna, verifica e posa sul nuovo grafo (DRAW-005, B6 e C).

- la tavola di consegna porta le sigle delle macchine principali, sempre, e
  nessun indirizzo di nodo;
- gli indirizzi si attivano esplicitamente e sono un velo: simboli e tubazioni
  non cambiano di un punto, e nessuna modalita' tocca posa o routing;
- puffer, bollitore e accumulo combinato non vedono permutare nessuna porta
  dalla posa: ogni tubazione arriva sull'attacco che il manifesto le da';
- la valvola che isola un pezzo manutenibile oltre un raccordo passante si
  stringe al raccordo, cioe' sta vicina all'attacco che protegge.

Impianti costruiti qui, con il catalogo di prova: nessun identificativo o
coordinata della tavola 1.
"""

from datetime import date
from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import CLOSING_FUNCTIONS, ComponentTrait
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.layout.addresses import with_addresses
from disegnatore_mep.layout.compose import compose_drawing, inline_component_ids
from disegnatore_mep.layout.geometry import DrawingGeometry, PlacedSymbol, Point, box_of
from disegnatore_mep.layout.inline import END_CLEARANCE_MM, SNUG_CLEARANCE_MM
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

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"
NAMING = ROOT / "naming"

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
            project_id="prova-consegna",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 7),
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


def con_puffer() -> ProjectModel:
    return _plant(
        [("anello", HEATING)],
        [
            ("generatore", "heat-pump-air-water", "PDC-01"),
            ("volano", "buffer-two-port", "VOL-01"),
            ("corpo", "radiator", "RAD-01"),
        ],
        [
            _pipe("c1", "anello", ("generatore", "water_supply"), ("volano", "a")),
            _pipe("c2", "anello", ("volano", "b"), ("corpo", "in")),
            _pipe("c3", "anello", ("corpo", "out"), ("generatore", "water_return")),
        ],
    )


def con_bollitore() -> ProjectModel:
    return _plant(
        [("primo", HEATING), ("fredda", COLD), ("calda", DHW)],
        [
            ("generatore", "heat-pump-air-water", "PDC-01"),
            ("bollitore", "dhw-cylinder", "BOL-01"),
            ("rete-idrica", "cold-water-inlet", "AF-01"),
            ("rubinetti", "dhw-draw-off", "ACS-01"),
        ],
        [
            _pipe("p1", "primo", ("generatore", "water_supply"), ("bollitore", "coil_in")),
            _pipe("p2", "primo", ("bollitore", "coil_out"), ("generatore", "water_return")),
            _pipe("w1", "fredda", ("rete-idrica", "a"), ("bollitore", "cold_in")),
            _pipe("w2", "calda", ("bollitore", "dhw_out"), ("rubinetti", "a")),
        ],
    )


def con_accumulo_combinato() -> ProjectModel:
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
    )


def _shape(drawing: DrawingGeometry) -> tuple[object, ...]:
    sheet = drawing.sheets[0]
    return (
        tuple(item.model_dump(mode="json", exclude={"tag"}) for item in sheet.symbols),
        tuple(item.model_dump(mode="json") for item in sheet.routes),
    )


# ---------------------------------------------------------------------------
# B6 — consegna con le sigle, verifica con gli indirizzi, geometria intatta
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("build", (con_puffer, con_bollitore, con_accumulo_combinato))
def test_la_consegna_porta_le_sigle_delle_macchine_e_nessun_indirizzo(
    build: object,
) -> None:
    project = build()  # type: ignore[operator]
    assert isinstance(project, ProjectModel)
    drawing = compose_drawing(project, catalog(), NOVE_C_A3)
    sheet = drawing.sheets[0]
    assert {item.role for item in sheet.labels} <= {"tag", "data"}
    tagged = {item.id for item in project.components if item.tag}
    written = {item.id.rsplit("-", 1)[0] for item in sheet.labels if item.role == "tag"}
    assert written == tagged, (tagged - written, written - tagged)


@pytest.mark.parametrize("build", (con_puffer, con_accumulo_combinato))
def test_gli_indirizzi_si_attivano_esplicitamente_e_sono_un_velo(build: object) -> None:
    project = build()  # type: ignore[operator]
    assert isinstance(project, ProjectModel)
    frame = NOVE_C_A3
    delivered = compose_drawing(project, catalog(), frame)
    verified = with_addresses(delivered, project, catalog(), frame, NAMING)
    assert _shape(verified) == _shape(delivered)
    addresses = [item for item in verified.sheets[0].labels if item.role == "address"]
    assert addresses
    assert all(item.leader_from is None for item in addresses)
    tags_before = [item.model_dump() for item in delivered.sheets[0].labels]
    tags_after = [
        item.model_dump() for item in verified.sheets[0].labels if item.role != "address"
    ]
    assert tags_after == tags_before
    assert not [item for item in delivered.sheets[0].labels if item.role == "address"]


def test_cambiare_o_togliere_le_sigle_non_muove_simboli_ne_tubi() -> None:
    project = con_accumulo_combinato()
    plain = compose_drawing(project, catalog(), NOVE_C_A3)
    renamed = project.model_copy(deep=True)
    for item in renamed.components:
        item.tag = None if item.tag is None else f"{item.tag}-SIGLA-MOLTO-PIU-LUNGA"
    bare = project.model_copy(deep=True)
    for item in bare.components:
        item.tag = None
    assert _shape(compose_drawing(renamed, catalog(), NOVE_C_A3)) == _shape(plain)
    assert _shape(compose_drawing(bare, catalog(), NOVE_C_A3)) == _shape(plain)


# ---------------------------------------------------------------------------
# A4 — nessuna porta delle riserve viene permutata dalla posa
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("build", (con_puffer, con_bollitore, con_accumulo_combinato))
def test_ogni_tubazione_arriva_sull_attacco_che_il_manifesto_da_alla_riserva(
    build: object,
) -> None:
    project = build()  # type: ignore[operator]
    assert isinstance(project, ProjectModel)
    registry = catalog()
    drawing = compose_drawing(project, registry, NOVE_C_A3)
    sheet = drawing.sheets[0]
    placed = {item.component_id: item for item in sheet.symbols}
    definitions = {item.id: item.definition_id for item in project.components}
    reserves = [
        item.id
        for item in project.components
        if registry.get(item.definition_id).has_trait(ComponentTrait.HOLDS_ITS_OWN_VOLUME)
    ]
    assert reserves
    inline = inline_component_ids(project, registry)
    trunks = build_trunks(project, inline)
    for reserve in reserves:
        symbol = placed[reserve]
        assert symbol.port_map == {}, reserve
        assert symbol.rotation_deg == 0
        manifest = registry.resolve(definitions[reserve]).symbol.manifest
        for trunk in trunks:
            for ref in (trunk.start, trunk.end):
                if ref.component_id != reserve:
                    continue
                port = manifest.port(ref.port_id)
                expected = Point(
                    x_mm=symbol.origin.x_mm + port.x_mm, y_mm=symbol.origin.y_mm + port.y_mm
                )
                route = next(
                    item
                    for item in sheet.routes
                    if tuple(item.connection_ids) == trunk.connection_ids
                )
                ends = [route.segments[0][0], route.segments[-1][-1]]
                assert any(
                    abs(end.x_mm - expected.x_mm) <= TOLERANCE_MM
                    and abs(end.y_mm - expected.y_mm) <= TOLERANCE_MM
                    for end in ends
                ), (reserve, ref.port_id, ends, expected)


# ---------------------------------------------------------------------------
# C — la valvola che isola oltre un raccordo passante si stringe al raccordo
# ---------------------------------------------------------------------------


def _gap_to_point(symbol: PlacedSymbol, x_mm: float, y_mm: float) -> float:
    left, top, right, bottom = box_of(symbol)
    gap_x = max(left - x_mm, x_mm - right, 0.0)
    gap_y = max(top - y_mm, y_mm - bottom, 0.0)
    return (gap_x**2 + gap_y**2) ** 0.5


def _port_point(
    registry: ComponentRegistry, project: ProjectModel, symbol: PlacedSymbol, port_id: str
) -> tuple[float, float]:
    definition_id = next(item.definition_id for item in project.components if item.id == symbol.component_id)
    port = registry.resolve(definition_id).symbol.manifest.rotated(symbol.rotation_deg).port(
        symbol.physical_port(port_id)
    )
    return symbol.origin.x_mm + port.x_mm, symbol.origin.y_mm + port.y_mm


def _continues_to_a_serviced_piece(
    project: ProjectModel, registry: ComponentRegistry, trunk: Trunk, trunks: list[Trunk]
) -> bool:
    """Vero se oltre il capo d'arrivo — attraverso i soli raccordi passanti —
    si arriva a un pezzo manutenibile."""
    definitions = {item.id: item.definition_id for item in project.components}
    ref = trunk.end
    seen: set[str] = set()
    while ref.component_id not in seen:
        seen.add(ref.component_id)
        definition = registry.get(definitions[ref.component_id])
        if definition.has_trait(ComponentTrait.MAINTAINABLE):
            return True
        if not definition.is_a_fitting:
            return False
        onward = [
            port
            for port in definition.ports
            if not port.off_the_run and port.id != ref.port_id
        ]
        if len(onward) != 1:
            return False
        following = [
            item
            for item in trunks
            if item.start == PortRef(component_id=ref.component_id, port_id=onward[0].id)
            or item.end == PortRef(component_id=ref.component_id, port_id=onward[0].id)
        ]
        if len(following) != 1:
            return False
        ref = following[0].end if following[0].start.component_id == ref.component_id else following[0].start
    return False


def test_la_valvola_che_isola_oltre_un_raccordo_passante_si_stringe_al_raccordo() -> None:
    """La sicurezza dell'accumulo pende da un raccordo sulla sua mandata: la
    valvola che isola l'accumulo sta prima del raccordo, e il raccordo e'
    l'unico organo che per funzione resta fra lei e l'attacco. Si posa
    percio' contro il raccordo, non a mezza strada."""
    project, _, _ = saturate(con_puffer(), catalog(), rules())
    registry = catalog()
    drawing = compose_drawing(project, registry, NOVE_C_A3)
    sheet = drawing.sheets[0]
    placed = {item.component_id: item for item in sheet.symbols}
    definitions = {item.id: item.definition_id for item in project.components}
    inline = inline_component_ids(project, registry)
    trunks = build_trunks(project, inline)
    measured: list[tuple[str, float, float]] = []
    for trunk in trunks:
        if not trunk.inline_component_ids:
            continue
        end = registry.get(definitions[trunk.end.component_id])
        if not end.is_a_fitting or not _continues_to_a_serviced_piece(project, registry, trunk, trunks):
            continue
        last = trunk.inline_component_ids[-1]
        if not CLOSING_FUNCTIONS & set(registry.get(definitions[last]).functions):
            continue
        tee_x, tee_y = _port_point(registry, project, placed[trunk.end.component_id], trunk.end.port_id)
        start_x, start_y = _port_point(registry, project, placed[trunk.start.component_id], trunk.start.port_id)
        measured.append(
            (last, _gap_to_point(placed[last], tee_x, tee_y), _gap_to_point(placed[last], start_x, start_y))
        )
    assert measured, "nessuna valvola oltre un raccordo passante: la prova non direbbe nulla"
    for name, to_the_tee, to_the_start in measured:
        assert SNUG_CLEARANCE_MM - TOLERANCE_MM <= to_the_tee <= END_CLEARANCE_MM + TOLERANCE_MM, (name, to_the_tee)
        assert to_the_tee <= to_the_start + TOLERANCE_MM, (name, to_the_tee, to_the_start)
