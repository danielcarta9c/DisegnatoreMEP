"""Il blocco C di DRAW-006-R1: l'adduzione fredda di un accumulo sanitario.

La traduzione impiantistica del PM, vincolante: «Per l'accumulo sanitario
pressurizzato non si eliminano tutte le protezioni: si usa un gruppo composito
conforme EN 1487 sull'ingresso freddo, evitando i duplicati separati. Il vaso
sanitario e' condizionale al progetto/catalogo; senza dato resta una domanda o
raccomandazione. Lo sfiato automatico ACS non e' predefinito. Lo scarico usa la
porta dedicata del serbatoio se il catalogo la dichiara.»

Le prove sono **generali**: gli accumuli si costruiscono qui — uno con la porta
di scarico e uno senza, uno che dichiara di non avere il vaso a bordo e uno che
tace — e nessun identificativo di una tavola entra nelle attese. Le voci di
catalogo che servono solo a dimostrare una proprieta' vivono qui e non nel
catalogo pubblicato.
"""

from datetime import date
from functools import cache
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import CLOSING_FUNCTIONS, ComponentDefinition
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
from disegnatore_mep.rules.proposal import GapReason, RuleGap
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"

COLD = "cold_water"
DHW = "domestic_hot_water"
HEATING = "heating_water"

SAFETY = "safety"
NON_RETURN = "non_return"
EXPANSION = "expansion"
AIR_RELEASE = "air_release"
DRAIN = "drain"

EN_1487 = "EN 1487"
"""La norma che il PM cita per il gruppo di sicurezza dell'accumulo sanitario.

Non e' un identificativo di componente: e' cio' che la **fonte** della voce di
catalogo deve dichiarare, ed e' l'unico modo di provare che quel pezzo e' li'
per quella ragione e non per somiglianza di nome.
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


def with_definitions(*extra: ComponentDefinition) -> ComponentRegistry:
    return ComponentRegistry([*catalog().all(), *extra], symbols=symbols())


def cylinder_definition() -> ComponentDefinition:
    """L'accumulo sanitario pubblicato: quello che le fixture usano davvero."""
    return next(
        item
        for item in catalog().all()
        if "dhw_storage" in item.functions and "heat_generation" not in item.functions
    )


def safety_group_definition() -> ComponentDefinition:
    """Il gruppo di sicurezza sanitario, cercato per **mestiere e fluido**."""
    return catalog().providing(SAFETY, COLD)


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


def accumulo_sanitario(definition_id: str) -> ProjectModel:
    """Acquedotto, riserva sanitaria, prelievo: l'adduzione fredda e basta.

    Nessun circuito di riscaldamento: cosi' cio' che compare sull'ingresso
    freddo viene dalle regole dell'accumulo e da nessun'altra.
    """
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-acs",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 10),
        ),
        plant_regime=PlantRegime.UP_TO_35_KW,
        networks=[_net("fredda", COLD), _net("sanitaria", DHW)],
        components=[
            ComponentInstance(id="acquedotto", definition_id="cold-water-inlet"),
            ComponentInstance(id="riserva", definition_id=definition_id),
            ComponentInstance(id="utenze", definition_id="dhw-draw-off"),
        ],
        connections=[
            _pipe("f", "fredda", ("acquedotto", "a"), ("riserva", "cold_in")),
            _pipe("s", "sanitaria", ("riserva", "dhw_out"), ("utenze", "a")),
        ],
    )


def completato(
    project: ProjectModel, registry: ComponentRegistry | None = None
) -> tuple[ProjectModel, list[RuleGap]]:
    done, _, gaps = saturate(project, registry or catalog(), rules())
    return done, gaps


def funzioni_di(
    model: ProjectModel, registry: ComponentRegistry
) -> dict[str, frozenset[str]]:
    return {
        item.id: frozenset(registry.get(item.definition_id).functions)
        for item in model.components
    }


def sulla_rete(
    model: ProjectModel, registry: ComponentRegistry, network_id: str, function: str
) -> list[str]:
    """I pezzi con quel mestiere che stanno su quella rete."""
    members = {
        ref.component_id
        for pipe in model.connections
        if pipe.network_id == network_id
        for ref in (pipe.endpoint_a, pipe.endpoint_b)
    }
    jobs = funzioni_di(model, registry)
    return sorted(item for item in members if function in jobs[item])


# ---------------------------------------------------------------------------
# C.1 — un solo gruppo composito EN 1487
# ---------------------------------------------------------------------------


def test_il_gruppo_di_sicurezza_sanitario_e_un_composito_dichiarato() -> None:
    """Un gruppo, e il catalogo dice cosa si porta dentro.

    Le tre funzioni sono quelle che il PM ha nominato: intercettazione, ritegno
    controllabile e sicurezza. La sicurezza e' il **mestiere** del pezzo; le
    altre due sono dichiarate interne, e per questo non vanno duplicate.
    """
    group = safety_group_definition()
    assert group.composite, (
        "il pezzo che porta la sicurezza sull'acqua fredda non e' un gruppo: "
        "senza `composite` non dichiara niente di cio' che ha dentro"
    )
    assert SAFETY in group.functions
    assert NON_RETURN in group.carries_on_board, (
        "il gruppo non dichiara il ritegno controllabile: le regole gliene "
        "aggiungerebbero uno esterno, che e' il duplicato che il PM ha tolto"
    )
    assert set(CLOSING_FUNCTIONS) & set(group.carries_on_board), (
        "il gruppo non dichiara la propria intercettazione"
    )
    assert any(EN_1487 in item for item in group.sources), (
        f"la voce non cita {EN_1487}: la ragione per cui questo gruppo sta "
        f"sull'ingresso freddo e' quella norma, e va scritta nella fonte"
    )


def test_l_ingresso_freddo_riceve_un_solo_gruppo_e_nessun_duplicato() -> None:
    """Una sola sicurezza, un solo ritegno, e il ritegno e' quello del gruppo."""
    model, _ = completato(accumulo_sanitario(cylinder_definition().id))
    registry = catalog()
    sicurezze = sulla_rete(model, registry, "fredda", SAFETY)
    assert len(sicurezze) == 1, (
        f"sull'ingresso freddo ci sono {len(sicurezze)} sicurezze: {sicurezze}"
    )
    ritegni = sulla_rete(model, registry, "fredda", NON_RETURN)
    assert not ritegni, (
        f"il ritegno del gruppo e' stato duplicato all'esterno: {ritegni}"
    )
    jobs = funzioni_di(model, registry)
    organi = [
        item
        for item in sulla_rete(model, registry, "fredda", "isolation")
        if not jobs[item] & {SAFETY}
    ]
    # L'organo del confine dell'impianto resta: e' un'altra regola, e chiude la
    # rete verso l'acquedotto, non il gruppo.
    assert len(organi) <= 1, (
        f"sull'ingresso freddo ci sono {len(organi)} organi di chiusura oltre a "
        f"quelli del gruppo: {organi}"
    )


# ---------------------------------------------------------------------------
# C.2 — il vaso sanitario e' condizionale al dato
# ---------------------------------------------------------------------------


def test_senza_il_dato_il_vaso_sanitario_non_nasce_ma_si_chiede() -> None:
    """Dato ignoto: nessun pezzo, e una domanda al progettista (I-046)."""
    riserva = cylinder_definition()
    assert EXPANSION not in riserva.carries_on_board
    assert EXPANSION not in riserva.lacks_on_board, (
        "l'accumulo pubblicato dichiara il dato del vaso: questa prova vuole "
        "proprio il caso in cui il dato manca"
    )
    model, gaps = completato(accumulo_sanitario(riserva.id))
    assert not sulla_rete(model, catalog(), "fredda", EXPANSION), (
        "il vaso sanitario e' stato aggiunto senza che nessun dato dicesse che "
        "manca a bordo"
    )
    domande = [
        item
        for item in gaps
        if item.missing_function == EXPANSION
        and item.reason is GapReason.ON_BOARD_UNKNOWN
    ]
    assert len(domande) == 1, (
        f"il vaso non e' stato aggiunto e nessuno lo ha chiesto: {gaps}"
    )


def test_col_dato_che_dice_di_no_il_vaso_sanitario_si_applica() -> None:
    """Dato presente e negativo: il pezzo si propone, come sempre."""
    riserva = cylinder_definition().model_copy(
        update={
            "id": "riserva-senza-vaso-a-bordo",
            "lacks_on_board": [EXPANSION],
        }
    )
    registry = with_definitions(riserva)
    model, gaps = completato(accumulo_sanitario(riserva.id), registry)
    assert sulla_rete(model, registry, "fredda", EXPANSION), (
        "l'accumulo dichiara di non avere il vaso a bordo e il vaso non e' "
        "stato aggiunto"
    )
    assert not [
        item
        for item in gaps
        if item.missing_function == EXPANSION
        and item.reason is GapReason.ON_BOARD_UNKNOWN
    ]


def test_col_dato_che_dice_di_si_il_vaso_sanitario_non_si_aggiunge() -> None:
    """Dato presente e positivo: il pezzo c'e' gia' dentro il mantello."""
    riserva = cylinder_definition().model_copy(
        update={"id": "riserva-col-vaso-a-bordo", "carries_on_board": [EXPANSION]}
    )
    registry = with_definitions(riserva)
    model, gaps = completato(accumulo_sanitario(riserva.id), registry)
    assert not sulla_rete(model, registry, "fredda", EXPANSION)
    assert not [item for item in gaps if item.missing_function == EXPANSION]


# ---------------------------------------------------------------------------
# C.3 — nessuno sfiato automatico predefinito
# ---------------------------------------------------------------------------


def test_nessuno_sfiato_automatico_sull_accumulo_sanitario() -> None:
    """Il riempimento sanitario ordinario si sfoga da un'utenza aperta.

    Vale su tutte e due le reti che toccano la riserva: nessuna delle due
    riceve uno sfogo d'aria, e nessuna regola ne chiede uno che il catalogo non
    possa dare.
    """
    model, gaps = completato(accumulo_sanitario(cylinder_definition().id))
    for network_id in ("fredda", "sanitaria"):
        assert not sulla_rete(model, catalog(), network_id, AIR_RELEASE), (
            f"sulla rete {network_id} e' comparso uno sfogo d'aria che nessuna "
            f"fonte chiede"
        )
    assert not [item for item in gaps if item.missing_function == AIR_RELEASE]


# ---------------------------------------------------------------------------
# C.4 e C.5 — lo scarico preferisce la porta dedicata
# ---------------------------------------------------------------------------


def _drain_port(definition: ComponentDefinition) -> str | None:
    return next(
        (port.id for port in definition.ports if port.serves == DRAIN), None
    )


def _attaccato_a(model: ProjectModel, component_id: str) -> set[tuple[str, str]]:
    """Gli attacchi, di chiunque, a cui quel pezzo e' collegato."""
    found: set[tuple[str, str]] = set()
    for pipe in model.connections:
        for mine, other in (
            (pipe.endpoint_a, pipe.endpoint_b),
            (pipe.endpoint_b, pipe.endpoint_a),
        ):
            if mine.component_id == component_id:
                found.add((other.component_id, other.port_id))
    return found


def accumulo_tecnico(definition_id: str, ports: tuple[str, str]) -> ProjectModel:
    """Un circuito chiuso con una riserva tecnica in mezzo.

    Serve al caso opposto del bollitore: un serbatoio che la **porta di
    scarico** ce l'ha, dichiarata dal proprio catalogo.
    """
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-accumulo",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 10),
        ),
        plant_regime=PlantRegime.UP_TO_35_KW,
        networks=[_net("anello", HEATING)],
        components=[
            ComponentInstance(id="generatore", definition_id="heat-pump-air-water"),
            ComponentInstance(id="riserva", definition_id=definition_id),
        ],
        connections=[
            _pipe("m", "anello", ("generatore", "water_supply"), ("riserva", ports[0])),
            _pipe("r", "anello", ("riserva", ports[1]), ("generatore", "water_return")),
        ],
    )


def test_lo_scarico_usa_la_porta_dedicata_quando_il_serbatoio_la_dichiara() -> None:
    """Se il catalogo dichiara l'attacco di scarico, lo scarico va li'.

    Il serbatoio si sceglie **per proprieta'** — tiene un volume proprio e
    dichiara una porta che serve lo scarico — non per identificativo: se un
    giorno il catalogo ne pubblicasse un altro, la prova userebbe il primo che
    trova, senza cambiare una riga.
    """
    riserva = next(
        item
        for item in catalog().all()
        if _drain_port(item) is not None
        and len([port for port in item.ports if not port.off_the_run]) == 2
    )
    porta = _drain_port(riserva)
    assert porta is not None
    ingressi = [port.id for port in riserva.ports if port.flow is PortFlow.IN]
    uscite = [port.id for port in riserva.ports if port.flow is PortFlow.OUT]
    model, _ = completato(accumulo_tecnico(riserva.id, (ingressi[0], uscite[0])))
    scarichi = sulla_rete(model, catalog(), "anello", DRAIN)
    assert len(scarichi) == 1, f"scarichi trovati: {scarichi}"
    assert ("riserva", porta) in _attaccato_a(model, scarichi[0]), (
        f"lo scarico e' appeso a {sorted(_attaccato_a(model, scarichi[0]))} "
        f"invece che alla porta che il serbatoio gli dedica"
    )


def test_senza_porta_dedicata_lo_scarico_ripiega_sulla_linea_di_riempimento() -> None:
    """Dove la porta non c'e', la riserva si svuota da dove si riempie."""
    riserva = cylinder_definition()
    assert _drain_port(riserva) is None, (
        "l'accumulo sanitario pubblicato ha una porta di scarico: questa prova "
        "vuole proprio il caso in cui non ce l'ha"
    )
    model, _ = completato(accumulo_sanitario(riserva.id))
    scarichi = sulla_rete(model, catalog(), "fredda", DRAIN)
    assert len(scarichi) == 1, f"scarichi trovati: {scarichi}"
    vicini = {item for item, _ in _attaccato_a(model, scarichi[0])}
    assert "riserva" not in vicini, (
        "senza porta dedicata lo scarico si e' appeso lo stesso al serbatoio"
    )
