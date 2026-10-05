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
# categoria: difende il motore — lo stacco lungo il proprio minimo su griglia e i corridoi davanti alle porte (I-046); due prove difendevano il solutore: elencate nel rapporto

import math
from datetime import date
from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.layout.chains import CHAIN_PORT_GAP_MM, MIN_SPACING_MM
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.geometry import (
    DrawingGeometry,
    PlacedSymbol,
)
from disegnatore_mep.layout.grid import GridSpace
from disegnatore_mep.layout.place import (
    ROW_GAP_MM,
    pende_addosso,
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
from disegnatore_mep.piano.esecutore import esegui_piano
from disegnatore_mep.piano.formato import carica_piano
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry
from disegnatore_mep.validation.regole import organi_di_servizio_lontani

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"
NAMING = ROOT / "naming"
PIANI = Path(__file__).resolve().parent / "piani"
HEATING = "heating_water"
COLD = "cold_water"
DHW = "domestic_hot_water"
TOLERANCE_MM = 1e-6


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
    """La tavola **dal piano**, come la compone la skill (D-151): il piano
    dell'impianto di prova 1 tradotto sui nomi della configurazione (`piani/`,
    I-180). Fino al 2 ottobre 2026 si componeva senza piano, e da D-167 quella
    via non instradava piu' il ritorno del radiatore."""
    esito = esegui_piano(
        completato(index),
        carica_piano(PIANI / f"{CASI[index].__name__}.json"),
        catalog(),
        symbols(),
        NAMING,
    )
    assert esito.disegno is not None, esito.errore
    return esito.disegno


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
        if pende_addosso(project, catalog(), trunk):
            # Lo sfiato col suo rubinetto pende addosso al raccordo, senza tubo in
            # mezzo: il suo simbolo lo stelo lo disegna da se' (I-212).
            assert minimum == 0.0, trunk.connection_ids
        elif not trunk.inline_component_ids:
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
    """Sulla tavola dal piano ogni organo di servizio sta **addosso** al pezzo che
    serve: lo misura il controllo **A4** del motore (`organi_di_servizio_lontani`,
    D-145), con il minimo vigente — dieci millimetri per uno stacco vuoto (D-062).

    Fino al 2 ottobre 2026 questa prova misurava a mano il minimo di I-046, due
    passi, e pretendeva che il **ciclo di miglioramento** non allungasse uno
    stacco senza comprare niente. Il ciclo non c'e' piu' (I-180); il minimo di
    due passi l'ha superato D-145; la misura sulla tavola finita e' A4, e la
    prova chiede quella. Perche' non passi a vuoto, conta gli organi misurati.
    """
    project = completato(index)
    drawing = composto(index)
    assert organi_di_servizio_lontani(drawing, NOVE_C_A3, catalog(), project) == []
    misurati = [
        trunk
        for trunk in _stubs(project)
        if tuple(trunk.connection_ids)
        in {tuple(route.connection_ids) for route in drawing.sheets[0].routes}
    ]
    assert len(misurati) >= 5, [trunk.connection_ids for trunk in misurati]




# ---------------------------------------------------------------------------
# E3, E4 — spostare le macchine costa zero, e si prova per primo
# ---------------------------------------------------------------------------






# ---------------------------------------------------------------------------
# La tavola 1, letta come fixture di regressione: la rete ordinaria non costa
# piu' di DRAW-005 — i tre numeri vivono solo qui
# ---------------------------------------------------------------------------






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


