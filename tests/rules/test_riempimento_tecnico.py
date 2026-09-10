"""Il blocco D di DRAW-006-R1: il riempimento e' un ponte fra due reti.

Il PM, sulla PR #24: «Il riempimento tecnico e' un ponte reale dall'acqua fredda
al ritorno comune del circuito tecnico. La variante Caleffi 553 include
riduttore, filtro, intercettazione e ritegno; il modello corrente a una sola
porta e' insufficiente.»

Cio' che il pacchetto chiede, punto per punto:

1. due reti e due porte: `cold_water` in ingresso → gruppo → `heating_water` in
   uscita;
2. collegato con un T a una sorgente di acqua fredda **gia' approvata** e al
   ritorno tecnico comune; senza sorgente, una domanda e nessun componente
   pendente;
3. riduttore di pressione, filtro, intercettazione e ritegno sono **interni** e
   non si duplicano fuori;
4. il verso e' acqua fredda → circuito tecnico.

Le prove sono generali: nessun identificativo di una tavola entra nelle attese,
e cio' che si cerca in catalogo si cerca per **mestiere e fluido**.
"""

from datetime import date
from functools import cache
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.model.project import (
    ComponentInstance,
    ConnectionModel,
    NetworkModel,
    PortRef,
    ProjectMetadata,
    ProjectModel,
)
from disegnatore_mep.model.types import PlantRegime, PortFlow
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.proposal import RuleGap
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"

COLD = "cold_water"
DHW = "domestic_hot_water"
HEATING = "heating_water"

FILLING = "filling"
BOUNDARY = "boundary"

INTEGRATE_DALLA_553 = ("pressure_control", "filtration", "isolation", "non_return")
"""Le funzioni che il PM dichiara **interne** alla variante Caleffi 553.

Sono nomi di mestieri, non di pezzi: quale voce di catalogo li porti su un dato
fluido lo dice il catalogo, e qui non se ne nomina nessuna.
"""


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


def filling_definition() -> ComponentDefinition:
    """Il gruppo di riempimento, cercato per **mestiere**, mai per nome."""
    found = [item for item in catalog().all() if FILLING in item.functions]
    assert len(found) == 1, f"gruppi di riempimento in catalogo: {found}"
    return found[0]


# ---------------------------------------------------------------------------
# Gli impianti di prova
# ---------------------------------------------------------------------------


def _pipe(
    pipe_id: str, network_id: str, a: tuple[str, str], b: tuple[str, str]
) -> ConnectionModel:
    return ConnectionModel(
        id=pipe_id,
        network_id=network_id,
        endpoint_a=PortRef(component_id=a[0], port_id=a[1]),
        endpoint_b=PortRef(component_id=b[0], port_id=b[1]),
    )


def _net(network_id: str, medium: str) -> NetworkModel:
    return NetworkModel(
        id=network_id, name=network_id, domain="hydronic", medium=medium
    )


def _metadata() -> ProjectMetadata:
    return ProjectMetadata(
        project_id="prova-riempimento",
        client="prova",
        project_name="prova",
        commission_code="PROVA",
        revision="00",
        issue_date=date(2026, 9, 10),
    )


def circuito_con_acqua_fredda() -> ProjectModel:
    """Un circuito chiuso e una linea di acqua fredda gia' approvata."""
    return ProjectModel(
        metadata=_metadata(),
        plant_regime=PlantRegime.UP_TO_35_KW,
        networks=[_net("anello", HEATING), _net("fredda", COLD), _net("sanitaria", DHW)],
        components=[
            ComponentInstance(id="generatore", definition_id="heat-pump-air-water"),
            ComponentInstance(id="terminale", definition_id="fan-coil"),
            ComponentInstance(id="riserva", definition_id="dhw-heat-pump"),
            ComponentInstance(id="acquedotto", definition_id="cold-water-inlet"),
            ComponentInstance(id="utenze", definition_id="dhw-draw-off"),
        ],
        connections=[
            _pipe("m", "anello", ("generatore", "water_supply"), ("terminale", "in")),
            _pipe("r", "anello", ("terminale", "out"), ("generatore", "water_return")),
            _pipe("f", "fredda", ("acquedotto", "a"), ("riserva", "cold_in")),
            _pipe("s", "sanitaria", ("riserva", "dhw_out"), ("utenze", "a")),
        ],
    )


def circuito_senza_acqua_fredda() -> ProjectModel:
    """Lo stesso circuito chiuso, e nessuna sorgente di acqua fredda."""
    base = circuito_con_acqua_fredda()
    tenuti = {"generatore", "terminale"}
    return base.model_copy(
        update={
            "networks": [item for item in base.networks if item.id == "anello"],
            "components": [item for item in base.components if item.id in tenuti],
            "connections": [
                item
                for item in base.connections
                if {item.endpoint_a.component_id, item.endpoint_b.component_id} <= tenuti
            ],
        }
    )


def completato(project: ProjectModel) -> tuple[ProjectModel, list[RuleGap]]:
    done, _, gaps = saturate(project, catalog(), rules())
    return done, gaps


def pezzi_con(model: ProjectModel, function: str) -> list[str]:
    return sorted(
        item.id
        for item in model.components
        if function in catalog().get(item.definition_id).functions
    )


def reti_di(model: ProjectModel, component_id: str) -> set[str]:
    return {
        pipe.network_id
        for pipe in model.connections
        for ref in (pipe.endpoint_a, pipe.endpoint_b)
        if ref.component_id == component_id
    }


def vicini_di(model: ProjectModel, component_id: str) -> dict[str, tuple[str, str]]:
    """Per ciascuna porta del pezzo, chi ci sta attaccato e su quale attacco."""
    found: dict[str, tuple[str, str]] = {}
    for pipe in model.connections:
        for mine, other in (
            (pipe.endpoint_a, pipe.endpoint_b),
            (pipe.endpoint_b, pipe.endpoint_a),
        ):
            if mine.component_id == component_id:
                found[mine.port_id] = (other.component_id, other.port_id)
    return found


# ---------------------------------------------------------------------------
# D.1 — due reti, due porte
# ---------------------------------------------------------------------------


def test_il_gruppo_di_riempimento_e_un_ponte_fra_due_reti() -> None:
    """Entra acqua fredda, esce acqua del circuito tecnico.

    Un pezzo con una porta sola non e' un ponte: non c'e' modo di dire da dove
    l'acqua arriva, e sulla tavola il gruppo resta appeso a un tubo che non
    porta l'acqua che ci passa.
    """
    group = filling_definition()
    media = {port.medium for port in group.ports}
    assert media == {COLD, HEATING}, (
        f"il gruppo di riempimento tocca {sorted(media)}: il ponte va "
        f"dall'acqua fredda all'acqua del circuito"
    )
    entrata = [port for port in group.ports if port.medium == COLD]
    uscita = [port for port in group.ports if port.medium == HEATING]
    assert len(entrata) == 1 and len(uscita) == 1
    assert entrata[0].flow is PortFlow.IN, (
        "l'attacco dell'acqua fredda non e' un ingresso: il verso e' AF → "
        "circuito, e il modello deve dirlo"
    )
    assert uscita[0].flow is PortFlow.OUT


def test_le_funzioni_interne_del_riempimento_sono_dichiarate() -> None:
    """Riduttore, filtro, intercettazione e ritegno stanno dentro il mantello.

    Il gruppo e' un composito, e un composito non dota di niente finche' non
    dichiara cosa ha dentro (DRAW-006, blocco B): l'elenco e' quello che il PM
    ha tradotto dalla serie 553.
    """
    group = filling_definition()
    assert group.composite
    mancanti = sorted(set(INTEGRATE_DALLA_553) - set(group.carries_on_board))
    assert not mancanti, (
        f"il gruppo non dichiara {mancanti}: le regole glieli aggiungerebbero "
        f"fuori, ed e' il duplicato che il PM ha tolto"
    )


# ---------------------------------------------------------------------------
# D.2 e D.4 — il ponte e' collegato davvero, e nel verso giusto
# ---------------------------------------------------------------------------


def test_il_riempimento_collega_l_acqua_fredda_e_il_ritorno_tecnico() -> None:
    """Due tubazioni, su due reti diverse: nessuna porta resta libera."""
    model, _ = completato(circuito_con_acqua_fredda())
    gruppi = pezzi_con(model, FILLING)
    assert len(gruppi) == 1, f"gruppi di riempimento sul modello: {gruppi}"
    gruppo = gruppi[0]
    media = {
        item.medium for item in model.networks if item.id in reti_di(model, gruppo)
    }
    assert media == {COLD, HEATING}, (
        f"il gruppo tocca {sorted(media)}: il ponte non e' collegato a tutte e "
        f"due le reti"
    )
    ports = vicini_di(model, gruppo)
    definition = filling_definition()
    assert set(ports) == definition.port_ids, (
        f"il gruppo ha attacchi liberi: {sorted(definition.port_ids - set(ports))}"
    )


def test_il_riempimento_pesca_dalla_sorgente_di_acqua_fredda_approvata() -> None:
    """L'acqua arriva dalla rete che il progettista ha gia' dichiarato.

    Non da una sorgente inventata dalla skill: la sorgente e' quella che porta
    il mestiere di confine sulla rete fredda, e il gruppo vi si innesta con una
    derivazione, senza interrompere l'adduzione di nessun altro.
    """
    model, _ = completato(circuito_con_acqua_fredda())
    gruppo = pezzi_con(model, FILLING)[0]
    definition = filling_definition()
    cold_port = next(port.id for port in definition.ports if port.medium == COLD)
    presa, _ = vicini_di(model, gruppo)[cold_port]
    fredde = {item.id for item in model.networks if item.medium == COLD}
    assert reti_di(model, presa) & fredde, (
        f"la presa del riempimento, {presa}, non sta sulla rete fredda"
    )
    assert catalog().get(
        next(item.definition_id for item in model.components if item.id == presa)
    ).is_a_fitting, (
        f"il riempimento e' attaccato a {presa}, che non e' una derivazione: il "
        f"gruppo si innesta con un T, non spezzando l'adduzione"
    )


def test_senza_sorgente_di_acqua_fredda_esce_una_domanda_e_nessun_pendente() -> None:
    """Mai un componente pendente: o il ponte e' completo, o si chiede."""
    model, gaps = completato(circuito_senza_acqua_fredda())
    assert not pezzi_con(model, FILLING), (
        "senza acqua fredda approvata il gruppo di riempimento e' stato posato "
        "lo stesso, con una porta che non porta da nessuna parte"
    )
    domande = [item for item in gaps if item.missing_function == FILLING]
    assert len(domande) == 1, (
        f"il riempimento non e' stato posato e nessuno lo ha chiesto: {gaps}"
    )


def test_il_verso_del_ponte_va_dall_acqua_fredda_al_circuito() -> None:
    """Sul modello, la tubazione fredda entra e quella tecnica esce."""
    model, _ = completato(circuito_con_acqua_fredda())
    gruppo = pezzi_con(model, FILLING)[0]
    definition = filling_definition()
    flows = {port.id: port.flow for port in definition.ports}
    for pipe in model.connections:
        for mine, is_a in (
            (pipe.endpoint_a, True),
            (pipe.endpoint_b, False),
        ):
            if mine.component_id != gruppo:
                continue
            # Una tubazione va sempre da una porta che esce a una che entra:
            # l'ingresso del gruppo deve percio' essere l'estremo B della
            # propria, e l'uscita l'estremo A.
            wanted = PortFlow.OUT if is_a else PortFlow.IN
            assert flows[mine.port_id] is wanted, (
                f"{pipe.id} tocca {mine.port_id} dalla parte sbagliata: il "
                f"verso del ponte e' acqua fredda → circuito"
            )


# ---------------------------------------------------------------------------
# D.3 — le funzioni interne non si duplicano
# ---------------------------------------------------------------------------


def test_nessun_organo_esterno_duplica_cio_che_il_gruppo_ha_dentro() -> None:
    """Attorno al gruppo non compare niente di cio' che dichiara di avere."""
    model, _ = completato(circuito_con_acqua_fredda())
    gruppo = pezzi_con(model, FILLING)[0]
    definitions = {item.id: catalog().get(item.definition_id) for item in model.components}
    attorno = {peer for peer, _ in vicini_di(model, gruppo).values()}
    # Il giro si allarga di un passo: fra il gruppo e la condotta ci puo'
    # stare la derivazione, e l'organo di troppo sarebbe subito oltre.
    for peer in list(attorno):
        attorno |= {other for other, _ in vicini_di(model, peer).values()}
    doppioni = sorted(
        item
        for item in attorno - {gruppo}
        if set(definitions[item].functions) & set(filling_definition().carries_on_board)
    )
    assert not doppioni, (
        f"attorno al gruppo di riempimento ci sono organi che il gruppo si "
        f"porta gia' dentro: {doppioni}"
    )
