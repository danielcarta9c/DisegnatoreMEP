"""Le prove generali dei blocchi A e B di DRAW-006, scritte prima del codice.

Il Work Package e la traduzione PM del 2026-09-09:

A. la `P` cerchiata e' un **manometro**, e il suo organo di servizio e' un
   **rubinetto portamanometro a tre vie** sulla presa, non una valvola di
   intercettazione ordinaria. Il gruppo e' presa sulla tubazione → stacco
   statico minimo → rubinetto → manometro; il rubinetto vive sullo stacco e non
   interrompe la condotta, non e' un organo capace di dividere un dominio
   idraulico, e vale a qualunque diametro perche' la presa strumentale e' una
   derivazione propria. Un **pressostato** di sicurezza o di minima non riceve
   automaticamente ne' quel rubinetto ne' una valvola ordinaria.

B. il gruppo di riempimento pubblicato **incorpora la propria intercettazione**
   e non ne riceve una esterna. Cio' che un composito integra lo dichiara il
   catalogo, funzione per funzione: una funzione integrata dichiarata non viene
   duplicata, una non dichiarata continua a essere applicata dalle regole
   normali. Niente si deduce dal nome, dal disegno o dal solo `composite`.

Le prove sono **generali**. Gli impianti si costruiscono qui; le voci di
catalogo che servono a dimostrare una proprieta' e che nessun impianto usa
vivono qui e non nel catalogo pubblicato — cosi' la proprieta' si prova senza
che il prodotto dichiari la dotazione di prodotti che il PM non gli ha dato.
Nessun identificativo, nessuna coordinata e nessuna soglia di una tavola entra
nelle attese.
"""

from datetime import date
from functools import cache
from pathlib import Path

import pytest
from pydantic import ValidationError

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import (
    CLOSING_FUNCTIONS,
    SHUTOFF_REGIMES,
    ComponentDefinition,
    ComponentTrait,
    PortDefinition,
)
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
from disegnatore_mep.rules.context import RuleContext
from disegnatore_mep.rules.registry import RuleRegistry
from disegnatore_mep.rules.schema import RuleCondition

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"

HEATING = "heating_water"
DHW = "domestic_hot_water"

ISOLATION = "isolation"
INSTRUMENT_ISOLATION = "instrument_isolation"
"""Il mestiere dell'organo che sta sulla **presa strumentale**.

Non e' un mestiere di chiusura: chi cammina sulla rete per sapere se una
macchina puo' restare separata dalla propria sicurezza non lo conta come organo
capace di dividere un dominio.
"""

PRESSURE_SWITCHING = "pressure_switching"
"""Il mestiere di un pressostato: non mostra una misura, comanda.

Vive solo in questa prova: serve a dimostrare che il rubinetto della presa
segue il **regime di intercettazione dichiarato** e non la famiglia degli
strumenti.
"""

FITTING_FUNCTIONS = frozenset({"junction", "branch_off"})
FILLING = "filling"
DRAIN = "drain"
SAFETY = "safety"

CORREDO_DEL_GRUPPO_GENERICO = ("non_return", "filtration", "pressure_control")
"""Le dotazioni che al gruppo di riempimento **generico** non spettano.

Il PM: disconnettore, filtro, ritegno e riduzione di pressione appartengono
alle varianti che li dichiarano (serie 580, EN 1717, EN 12729, EN 806-5), non
al gruppo pubblicato. Sono nomi di **mestieri**, non di pezzi.
"""


# ---------------------------------------------------------------------------
# Il catalogo di prova: quello pubblicato, piu' le voci che vivono solo qui
# ---------------------------------------------------------------------------


def _port(port_id: str, flow: PortFlow, medium: str = HEATING) -> PortDefinition:
    return PortDefinition(
        id=port_id, domain="hydronic", medium=medium, flow=flow, required=True
    )


@cache
def symbols() -> SymbolRegistry:
    return SymbolRegistry.from_directory(SYMBOLS)


@cache
def published() -> ComponentRegistry:
    """Il catalogo come lo pubblica il prodotto."""
    return ComponentRegistry.from_directory(CATALOG, symbols=symbols())


def gauge_definition() -> ComponentDefinition:
    """Il manometro pubblicato: e' lui a dire come lo si intercetta."""
    return published().get("pressure-gauge")


def cock_definition() -> ComponentDefinition:
    """Il rubinetto portamanometro a tre vie pubblicato.

    Si cerca per **mestiere**, mai per identificativo: quale voce porti quella
    funzione lo decide il catalogo.
    """
    return next(item for item in published().all() if INSTRUMENT_ISOLATION in item.functions)


@cache
def catalog() -> ComponentRegistry:
    """Il catalogo pubblicato piu' le voci di prova.

    Le voci di prova dimostrano proprieta' **generali**: lo stesso strumento su
    un altro fluido con il proprio rubinetto, e un pressostato che non si
    intercetta. Non stanno nel catalogo pubblicato perche' nessun impianto le
    usa.
    """
    base = published()
    gauge, cock = gauge_definition(), cock_definition()
    extra = [
        gauge.model_copy(
            update={
                "id": "pressure-gauge-dhw",
                "name": f"{gauge.name} sull'acqua calda sanitaria",
                "ports": [_port("a", PortFlow.BIDIRECTIONAL, DHW)],
            }
        ),
        cock.model_copy(
            update={
                "id": f"{cock.id}-dhw",
                "name": f"{cock.name} sull'acqua calda sanitaria",
                "ports": [
                    _port("a", PortFlow.BIDIRECTIONAL, DHW),
                    _port("b", PortFlow.BIDIRECTIONAL, DHW),
                ],
            }
        ),
        ComponentDefinition(
            id="pressure-switch-safety",
            version="1.0.0",
            name="Pressostato di sicurezza",
            functions=[PRESSURE_SWITCHING],
            traits=[ComponentTrait.SHUTOFF_NEVER, ComponentTrait.ATTACHMENT_BRANCH],
            symbol_id=gauge.symbol_id,
            ports=[_port("a", PortFlow.BIDIRECTIONAL)],
            sources=["prova generale DRAW-006"],
        ),
    ]
    return ComponentRegistry([*base.all(), *extra], symbols=symbols())


def composite(definition_id: str, integrates: list[str]) -> ComponentDefinition:
    """Un gruppo che si manutiene e dichiara cosa si porta dentro.

    E' la forma generale del gruppo di riempimento: cambia solo l'elenco delle
    funzioni che il catalogo dichiara **interne**.
    """
    return ComponentDefinition(
        id=definition_id,
        version="1.0.0",
        name="Gruppo di prova",
        functions=[FILLING],
        traits=[
            ComponentTrait.MAINTAINABLE,
            ComponentTrait.SHUTOFF_ORDINARY,
            ComponentTrait.ATTACHMENT_BRANCH,
        ],
        carries_on_board=integrates,
        symbol_id="filling-unit",
        composite=True,
        ports=[_port("a", PortFlow.BIDIRECTIONAL)],
        sources=["prova generale DRAW-006"],
    )


def with_definitions(*extra: ComponentDefinition) -> ComponentRegistry:
    return ComponentRegistry([*catalog().all(), *extra], symbols=symbols())


@cache
def rules() -> RuleRegistry:
    registry = RuleRegistry.from_directory(RULES)
    registry.cross_check(catalog())
    return registry


# ---------------------------------------------------------------------------
# Gli impianti di prova
# ---------------------------------------------------------------------------


def _net(network_id: str, medium: str = HEATING) -> NetworkModel:
    return NetworkModel(id=network_id, name=network_id, domain="hydronic", medium=medium)


def _pipe(
    pipe_id: str, network_id: str, a: tuple[str, str], b: tuple[str, str]
) -> ConnectionModel:
    return ConnectionModel(
        id=pipe_id,
        network_id=network_id,
        endpoint_a=PortRef(component_id=a[0], port_id=a[1]),
        endpoint_b=PortRef(component_id=b[0], port_id=b[1]),
    )


def _plant(
    networks: list[NetworkModel],
    components: list[tuple[str, str]],
    connections: list[ConnectionModel],
) -> ProjectModel:
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-semantica",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 9),
        ),
        plant_regime=PlantRegime.UP_TO_35_KW,
        networks=networks,
        components=[
            ComponentInstance(id=item, definition_id=definition)
            for item, definition in components
        ],
        connections=connections,
    )


def anello_con(appeso: str, definition_id: str) -> ProjectModel:
    """Un generatore, un terminale e cio' che pende dalla presa sul ritorno.

    E' il piu' piccolo impianto che abbia un ritorno su cui appendere qualcosa:
    la prova guarda cosa le regole mettono **fra** la tubazione e l'appeso, e
    nient'altro.
    """
    return _plant(
        [_net("anello")],
        [
            ("generatore", "heat-pump-air-water"),
            ("terminale", "fan-coil"),
            ("derivazione", "tee-branch"),
            (appeso, definition_id),
        ],
        [
            _pipe("m", "anello", ("generatore", "water_supply"), ("terminale", "in")),
            _pipe("r1", "anello", ("terminale", "out"), ("derivazione", "a")),
            _pipe("r2", "anello", ("derivazione", "b"), ("generatore", "water_return")),
            _pipe("s", "anello", ("derivazione", "branch"), (appeso, "a")),
        ],
    )


def linea_sanitaria_con(appeso: str, definition_id: str) -> ProjectModel:
    """La stessa presa su un altro fluido: bollitore, derivazione, prelievo."""
    return _plant(
        [_net("sanitaria", DHW)],
        [
            ("bollitore", "dhw-cylinder"),
            ("derivazione", "tee-branch-dhw"),
            ("prelievo", "dhw-draw-off"),
            (appeso, definition_id),
        ],
        [
            _pipe("d1", "sanitaria", ("bollitore", "dhw_out"), ("derivazione", "a")),
            _pipe("d2", "sanitaria", ("derivazione", "b"), ("prelievo", "a")),
            _pipe("s", "sanitaria", ("derivazione", "branch"), (appeso, "a")),
        ],
    )


def completato(project: ProjectModel, registry: ComponentRegistry) -> ProjectModel:
    completed, _, _ = saturate(project, registry, rules())
    return completed


def funzioni_di(
    model: ProjectModel, registry: ComponentRegistry
) -> dict[str, frozenset[str]]:
    return {
        item.id: frozenset(registry.get(item.definition_id).functions)
        for item in model.components
    }


def pezzi_con(model: ProjectModel, registry: ComponentRegistry, function: str) -> list[str]:
    return sorted(
        item for item, jobs in funzioni_di(model, registry).items() if function in jobs
    )


def fila_dallo_stacco(
    model: ProjectModel, registry: ComponentRegistry, appeso: str
) -> list[str]:
    """I pezzi fra l'appeso e la condotta, in ordine, fino alla presa compresa.

    Si cammina **sul modello**, dall'appeso verso la tubazione: la fila esce
    dal disegno del grafo e non da un'attesa scritta a mano.
    """
    peers: dict[str, set[str]] = {item.id: set() for item in model.components}
    for pipe in model.connections:
        peers[pipe.endpoint_a.component_id].add(pipe.endpoint_b.component_id)
        peers[pipe.endpoint_b.component_id].add(pipe.endpoint_a.component_id)
    jobs = funzioni_di(model, registry)
    order, seen = [appeso], {appeso}
    while True:
        onward = sorted(peers[order[-1]] - seen)
        if len(onward) != 1:
            break
        order.append(onward[0])
        seen.add(onward[0])
        if jobs[onward[0]] & FITTING_FUNCTIONS:
            break
    return order


def organi_della_presa(
    model: ProjectModel, registry: ComponentRegistry, appeso: str
) -> list[frozenset[str]]:
    """I mestieri dei pezzi che stanno fra l'appeso e la presa."""
    jobs = funzioni_di(model, registry)
    return [jobs[item] for item in fila_dallo_stacco(model, registry, appeso)[1:-1]]


# ---------------------------------------------------------------------------
# A — manometro e rubinetto portamanometro a tre vie
# ---------------------------------------------------------------------------


def test_il_catalogo_distingue_il_rubinetto_dalla_valvola_ordinaria() -> None:
    """Sono due voci, due mestieri e due segni: non la stessa valvola.

    Il difetto che questa prova rende impossibile: risolvere «l'organo del
    manometro» con la valvola di linea, che sulla tavola si legge come un
    sezionamento della condotta.
    """
    cock, ordinary = cock_definition(), published().get("valve-isolation")
    assert cock.id != ordinary.id
    assert cock.symbol_id != ordinary.symbol_id, (
        "il rubinetto porta il segno della valvola di intercettazione: sulla "
        "tavola i due organi sarebbero indistinguibili"
    )
    assert INSTRUMENT_ISOLATION in cock.functions
    assert not CLOSING_FUNCTIONS & set(cock.functions)


def test_il_regime_della_presa_strumentale_e_un_regime_dichiarato() -> None:
    """E' uno dei modi in cui un componente si lascia chiudere, non una deroga.

    Un componente ne dichiara **uno solo**: se il regime della presa vivesse
    fuori da quell'elenco, un pezzo potrebbe dichiararlo insieme a quello
    ordinario e ricevere due organi.
    """
    assert ComponentTrait.SHUTOFF_INSTRUMENT_TAP in SHUTOFF_REGIMES
    payload = gauge_definition().model_dump(mode="json")
    payload["traits"] = [*payload["traits"], ComponentTrait.SHUTOFF_ORDINARY.value]
    with pytest.raises(ValidationError):
        ComponentDefinition.model_validate(payload)


def test_il_rubinetto_non_e_un_organo_capace_di_dividere_un_dominio() -> None:
    """Non chiude un dominio idraulico, e chi cammina sulla rete lo sa.

    E' il punto 4 del blocco A. Se comparisse fra i mestieri di chiusura, un
    generatore risulterebbe tagliato fuori dalla propria sicurezza per via di
    una presa manometrica.
    """
    assert INSTRUMENT_ISOLATION not in CLOSING_FUNCTIONS
    registry = catalog()
    model = completato(anello_con("manometro", "pressure-gauge"), registry)
    context = RuleContext.build(model, registry)
    organi = set(pezzi_con(model, registry, INSTRUMENT_ISOLATION))
    assert organi, "l'impianto di prova non ha nessun rubinetto: non prova niente"
    for generatore in pezzi_con(model, registry, "heat_generation"):
        assert not organi & context.own_closers(generatore), (
            "il rubinetto della presa e' finito fra gli organi propri del "
            "generatore: sarebbe un organo di linea, e non lo e'"
        )
        assert not context.cut_off_from(generatore, SAFETY, "anello"), (
            "il generatore risulta separato dalla propria sicurezza: qualcosa "
            "sta contando la presa strumentale come una chiusura"
        )


def test_il_manometro_riceve_il_rubinetto_e_mai_una_valvola_ordinaria() -> None:
    """L'organo del manometro esce dal **regime dichiarato**, non dal nome.

    La regola dell'intercettazione e' una sola e vale per tutto cio' che si
    smonta in esercizio: quale organo ciascuno pretenda lo dice il proprio
    regime, come per il vaso che vuole quello bloccabile aperto.
    """
    assert gauge_definition().shutoff_regime is ComponentTrait.SHUTOFF_INSTRUMENT_TAP
    registry = catalog()
    model = completato(anello_con("manometro", "pressure-gauge"), registry)
    organi = organi_della_presa(model, registry, "manometro")
    assert organi, "il manometro e' rimasto senza organo di servizio"
    for jobs in organi:
        assert INSTRUMENT_ISOLATION in jobs, (
            f"sulla presa del manometro c'e' {sorted(jobs)}: la presa vuole il "
            f"rubinetto a tre vie, non un organo di linea"
        )
        assert not jobs & CLOSING_FUNCTIONS


def test_il_gruppo_della_presa_e_presa_rubinetto_strumento() -> None:
    """Presa sulla tubazione → stacco → rubinetto → manometro, in quest'ordine.

    Il rubinetto vive **sullo stacco**: la condotta principale non lo incontra,
    e i suoi due capi restano quelli di prima.
    """
    registry = catalog()
    model = completato(anello_con("manometro", "pressure-gauge"), registry)
    fila = fila_dallo_stacco(model, registry, "manometro")
    jobs = funzioni_di(model, registry)
    assert INSTRUMENT_ISOLATION in jobs[fila[1]], (
        f"fra il manometro e la presa c'e' {fila[1:]}: il primo pezzo verso la "
        f"condotta dev'essere il rubinetto"
    )
    assert jobs[fila[-1]] & FITTING_FUNCTIONS, (
        f"la fila della presa finisce su {fila[-1]}, che non e' una presa sulla "
        f"tubazione"
    )
    presa, gruppo = fila[-1], set(fila[:-1])
    for pipe in model.connections:
        ends = {pipe.endpoint_a.component_id, pipe.endpoint_b.component_id}
        if not ends & gruppo:
            continue
        assert ends <= gruppo | {presa}, (
            f"{pipe.id} collega il gruppo della presa a {sorted(ends - gruppo)}: "
            f"il rubinetto sta sullo stacco, non sulla condotta"
        )
        for end in (pipe.endpoint_a, pipe.endpoint_b):
            if end.component_id == presa:
                assert end.port_id == "branch", (
                    "il gruppo della presa e' attaccato a un attacco del "
                    "percorso della presa: interromperebbe la condotta"
                )


def test_la_presa_strumentale_non_guarda_la_condotta_su_cui_nasce() -> None:
    """La presa e' una derivazione propria e corta, a qualunque diametro.

    Il modello non porta diametri, e nessuna regola puo' chiederli perche' non
    esiste un dato da chiedere: la prova lo verifica sul vocabolario delle
    condizioni e del catalogo, e poi mostra lo stesso gruppo su un altro fluido
    — l'unica dimensione lungo cui, in questo modello, la condotta cambia.
    """
    vocabolario = set(RuleCondition.model_fields) | set(ComponentDefinition.model_fields)
    assert not [item for item in vocabolario if "diameter" in item or "size" in item], (
        "il vocabolario delle regole o del catalogo ha acquisito una misura "
        "della condotta: la presa strumentale non la guarda"
    )
    registry = catalog()
    for progetto in (
        anello_con("manometro", "pressure-gauge"),
        linea_sanitaria_con("manometro", "pressure-gauge-dhw"),
    ):
        model = completato(progetto, registry)
        organi = organi_della_presa(model, registry, "manometro")
        assert organi and all(INSTRUMENT_ISOLATION in jobs for jobs in organi), (
            f"su {progetto.networks[0].medium} la presa del manometro non ha "
            f"ricevuto il rubinetto"
        )


def test_un_pressostato_non_riceve_ne_rubinetto_ne_valvola_ordinaria() -> None:
    """Il pressostato di sicurezza non e' un manometro (blocco A, punto 5).

    Fra un pressostato di sicurezza o di minima e cio' che comanda non ci va
    nulla di chiudibile: il suo regime dichiarato e' «non lo si chiude mai», e
    non si smonta a impianto in pressione. Una regola che desse il rubinetto
    «agli strumenti» gliene metterebbe uno addosso.
    """
    registry = catalog()
    switch = registry.get("pressure-switch-safety")
    assert switch.shutoff_regime is ComponentTrait.SHUTOFF_NEVER
    assert not switch.has_trait(ComponentTrait.MAINTAINABLE)
    model = completato(anello_con("pressostato", "pressure-switch-safety"), registry)
    for jobs in organi_della_presa(model, registry, "pressostato"):
        assert not jobs & (CLOSING_FUNCTIONS | {INSTRUMENT_ISOLATION}), (
            f"il pressostato ha ricevuto {sorted(jobs)} sulla propria presa: "
            f"fra lui e cio' che comanda non ci va nulla di chiudibile"
        )


# ---------------------------------------------------------------------------
# B — gruppi compositi e riempimento
# ---------------------------------------------------------------------------


def test_un_composito_dichiara_cosa_si_porta_dentro() -> None:
    """`composite` non e' una dotazione: e' l'obbligo di dichiararla.

    Il difetto che questa prova rende impossibile: un gruppo che «si sa» avere
    dentro le proprie valvole senza che il catalogo lo dica — e allora la stessa
    frase varrebbe per il disconnettore, il filtro e il ritegno.
    """
    with pytest.raises(ValidationError):
        composite("gruppo-muto", [])
    assert composite("gruppo-parlante", [ISOLATION]).on_board(ISOLATION).value == "present"


def test_il_gruppo_di_riempimento_pubblicato_incorpora_la_propria_intercettazione() -> None:
    """Il gruppo pubblicato dichiara l'intercettazione interna, e nient'altro.

    E' il punto 4 del blocco B: disconnettore, filtro, ritegno e riduzione di
    pressione appartengono alle varianti che li dichiarano, non al gruppo
    generico.
    """
    unit = published().get("filling-unit")
    assert unit.composite
    assert ISOLATION in unit.carries_on_board
    for job in CORREDO_DEL_GRUPPO_GENERICO:
        assert job not in unit.carries_on_board, (
            f"il gruppo generico dichiara di portare dentro {job}: quel corredo "
            f"appartiene alla variante che lo dichiara"
        )


def test_una_funzione_integrata_dichiarata_non_viene_duplicata() -> None:
    """Chi dichiara l'intercettazione interna non riceve la valvola esterna."""
    registry = with_definitions(composite("gruppo-con-organo", [ISOLATION]))
    model = completato(anello_con("riempimento", "gruppo-con-organo"), registry)
    for jobs in organi_della_presa(model, registry, "riempimento"):
        assert not jobs & CLOSING_FUNCTIONS, (
            f"al gruppo che dichiara l'intercettazione interna e' stato aggiunto "
            f"{sorted(jobs)}: e' l'organo che ha gia' dentro"
        )


def test_una_funzione_non_dichiarata_continua_a_essere_applicata() -> None:
    """L'altra meta' della regola: cio' che il composito non dichiara si posa.

    Il gruppo che integra solo lo scarico si manutiene ancora, e la valvola
    esterna gli spetta: `composite` da solo non toglie niente.
    """
    registry = with_definitions(composite("gruppo-senza-organo", [DRAIN]))
    model = completato(anello_con("riempimento", "gruppo-senza-organo"), registry)
    organi = organi_della_presa(model, registry, "riempimento")
    assert any(jobs & CLOSING_FUNCTIONS for jobs in organi), (
        "il gruppo che non dichiara l'intercettazione interna e' rimasto senza "
        "organo: una funzione non dichiarata si applica come sempre"
    )


def test_la_dotazione_non_si_deduce_dal_nome_ne_dal_disegno() -> None:
    """Due gruppi con lo stesso nome e lo stesso segno, dotazioni diverse.

    L'unico dato che cambia l'esito e' l'elenco delle funzioni integrate.
    """
    registry = with_definitions(
        composite("gruppo-gemello-con", [ISOLATION]),
        composite("gruppo-gemello-senza", [DRAIN]),
    )
    primo, secondo = (
        registry.get("gruppo-gemello-con"),
        registry.get("gruppo-gemello-senza"),
    )
    assert (primo.name, primo.symbol_id) == (secondo.name, secondo.symbol_id)
    esiti = [
        any(
            jobs & CLOSING_FUNCTIONS
            for jobs in organi_della_presa(
                completato(anello_con("riempimento", item), registry),
                registry,
                "riempimento",
            )
        )
        for item in ("gruppo-gemello-con", "gruppo-gemello-senza")
    ]
    assert esiti == [False, True], (
        "i due gruppi hanno avuto lo stesso esito: la dotazione sta seguendo "
        "qualcosa che non e' la dichiarazione del catalogo"
    )


def test_al_gruppo_generico_non_si_attribuisce_altro_corredo() -> None:
    """Niente disconnettore, filtro, ritegno o riduzione sul gruppo generico."""
    registry = catalog()
    model = completato(anello_con("riempimento", "filling-unit"), registry)
    for jobs in organi_della_presa(model, registry, "riempimento"):
        assert not jobs & set(CORREDO_DEL_GRUPPO_GENERICO), (
            f"sul gruppo di riempimento generico e' comparso {sorted(jobs)}: "
            f"quel corredo appartiene alla variante che lo dichiara"
        )


def test_il_riempimento_e_uno_solo_per_circuito_tecnico() -> None:
    """Un circuito chiuso si reintegra da un punto, e il punto e' uno."""
    registry = catalog()
    model = completato(anello_con("riempimento", "filling-unit"), registry)
    assert len(pezzi_con(model, registry, FILLING)) == 1


def test_il_bordo_di_un_composito_non_soddisfa_la_rete() -> None:
    """Cio' che un gruppo ha dentro serve **lui**, non l'impianto.

    Il difetto che questa prova rende impossibile: un organo interno che fa
    sparire in silenzio l'organo che un'altra macchina della stessa rete
    pretende, perche' «sulla rete quella funzione c'e' gia'».
    """
    registry = with_definitions(composite("gruppo-con-sicurezza", [SAFETY]))
    project = anello_con("riempimento", "gruppo-con-sicurezza")
    context = RuleContext.build(project, registry)
    assert context.carries("riempimento", SAFETY)
    assert not context.network_has("anello", SAFETY), (
        "il bordo di un gruppo sta soddisfacendo la rete: soddisfa chi lo porta"
    )
    model = completato(project, registry)
    assert pezzi_con(model, registry, SAFETY), (
        "la sicurezza del circuito e' sparita per via del bordo di un gruppo"
    )
