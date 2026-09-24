"""Le prove generali del blocco C di DRAW-006, scritte prima del codice.

**Aggiornate il 24 settembre 2026 per D-182** (la strada A, I-116): ogni
generatore del circuito chiuso ha la propria sicurezza, attaccata all'uscita e
prima di ogni organo, e non si chiede piu' il bordo macchina. I punti 4 e 6 qui
sotto sono la storia di I-046; restano provati gli stati idraulici del catalogo
(1, 2) e la capacita' del motore di dire chi una multivia puo' separare da una
sicurezza (3), su un impianto costruito a mano con una sicurezza sola.

Il Work Package e la traduzione PM del 2026-09-09:

1. il catalogo dichiara gli **stati idraulici ammessi** di un componente
   multivia. Per una deviatrice a tre vie: `in ↔ out_a` oppure `in ↔ out_b`;
   i due rami non comunicano insieme e `out_a ↔ out_b` non e' un passaggio
   autonomo;
2. nomenclatura delle linee e analisi della sicurezza leggono **lo stesso dato
   di catalogo**, senza elenchi di mestieri duplicati nei moduli;
3. un generatore e' protetto solo se raggiunge una sicurezza in **ogni** stato
   ammesso nel quale puo' funzionare, senza attraversare un organo che possa
   separarlo;
4. la cardinalita' della sicurezza e' per **dominio di protezione effettivo**,
   non per intera rete ne' per numero dei generatori;
5. una sicurezza valida per una parte della rete non si scarta perche' non
   protegge un altro generatore: ogni dominio si valuta separatamente;
6. per un generatore isolabile: dato di bordo ignoto → una domanda; presente →
   nessun pezzo; assente → sicurezza propria non intercettabile;
7. la fixture dell'impianto 4 verifica la logica senza produrre artefatti
   grafici.

Gli impianti sono costruiti qui, con una, due e tre macchine e con o senza
deviatrice. L'unica prova che legge una fixture e' l'ultima, che verifica il
comportamento sull'impianto 4 e non decide nulla.
"""

from datetime import date
from functools import cache
from pathlib import Path

import pytest
from pydantic import ValidationError

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition, HydraulicState
from disegnatore_mep.graph import LineNaming, Naming, read_lines, read_plant
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
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
from disegnatore_mep.rules.context import RuleContext
from disegnatore_mep.rules.proposal import GapReason, RuleGap
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"
NAMING = ROOT / "naming"
IBRIDO = ROOT / "examples" / "prova" / "prova-4-ibrido-pdc-caldaia.json"

HEATING = "heating_water"
SAFETY = "safety"
HEAT_GENERATION = "heat_generation"
DIVERTER = "diverting-valve-3way"
SWITCH = "switching-valve-3way"
"""La commutatrice a tre vie: il **secondo** multivia del catalogo (D-137 §D.2).

Due ingressi e un'uscita, funzione di commutazione: e' l'organo con cui la caldaia
sceglie da dove pesca — dal primario quando fa riscaldamento, dallo scambiatore
quando fa sanitario. Senza, mentre fa sanitario pesca da tutt'e due, ed e' il
«ritorno che torna ovunque» che il PO ha visto guardando la tavola 4. Gli stati
li ha chiesti il PO, e la riga qui sotto e' il posto in cui si dichiara."""
GENERIC = "heat-pump-air-water"
WITH_SAFETY = "heat-pump-air-water-sicurezza-a-bordo"
WITHOUT_SAFETY = "heat-pump-air-water-sicurezza-non-a-bordo"
"""Le tre macchine della prova: la generica, che della sicurezza non dice
nulla (dato **ignoto**); la stessa che la dichiara a bordo (**presente**); la
stessa che dichiara di non averla (**assente**)."""


@cache
def symbols() -> SymbolRegistry:
    return SymbolRegistry.from_directory(SYMBOLS)


@cache
def catalog() -> ComponentRegistry:
    base = ComponentRegistry.from_directory(CATALOG, symbols=symbols())
    generic = base.get(GENERIC)
    assert SAFETY not in generic.carries_on_board
    assert SAFETY not in generic.lacks_on_board, (
        "la macchina generica non deve dire nulla della sicurezza: il dato "
        "mancante e' cio' che il pacchetto tratta come ignoto"
    )
    present = generic.model_copy(
        update={
            "id": WITH_SAFETY,
            "name": f"{generic.name} con sicurezza a bordo",
            "carries_on_board": [*generic.carries_on_board, SAFETY],
        }
    )
    absent = generic.model_copy(
        update={
            "id": WITHOUT_SAFETY,
            "name": f"{generic.name} senza sicurezza a bordo",
            "lacks_on_board": [SAFETY],
        }
    )
    return ComponentRegistry([*base.all(), present, absent], symbols=symbols())


@cache
def rules() -> RuleRegistry:
    registry = RuleRegistry.from_directory(RULES)
    registry.cross_check(catalog())
    return registry


def diverter() -> ComponentDefinition:
    return catalog().get(DIVERTER)


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
            project_id="prova-stati",
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


def macchine_in_parallelo(machine: str, quante: int) -> ProjectModel:
    """N macchine su una confluenza e una ripartizione: **un** dominio solo."""
    lettere = ["a", "c", "d"][:quante]
    return _plant(
        [_net("rete")],
        [
            *((f"macchina-{index}", machine) for index in range(quante)),
            ("unione", "zone-manifold" if quante > 3 else "tee-junction"),
            ("ripartizione", "tee-split"),
            ("volano", "buffer-four-port"),
        ],
        [
            *(
                _pipe(
                    f"m{index}",
                    "rete",
                    (f"macchina-{index}", "water_supply"),
                    ("unione", lettere[index]),
                )
                for index in range(quante)
            ),
            _pipe("mc", "rete", ("unione", "b"), ("volano", "primary_in")),
            _pipe("rc", "rete", ("volano", "primary_out"), ("ripartizione", "a")),
            *(
                _pipe(
                    f"r{index}",
                    "rete",
                    ("ripartizione", ["b", "c", "d"][index]),
                    (f"macchina-{index}", "water_return"),
                )
                for index in range(quante)
            ),
        ],
    )


def due_domini_scollegati(machine: str) -> ProjectModel:
    """Due circuiti chiusi indipendenti, dichiarati sulla **stessa rete**.

    Non e' un caso di scuola: e' la forma minima in cui «una sicurezza per
    l'intera rete» e «una sicurezza per dominio» danno risposte diverse.
    """
    return _plant(
        [_net("rete")],
        [
            ("nord", machine),
            ("sud", machine),
            ("volano-nord", "buffer-two-port"),
            ("volano-sud", "buffer-two-port"),
        ],
        [
            _pipe("mn", "rete", ("nord", "water_supply"), ("volano-nord", "a")),
            _pipe("rn", "rete", ("volano-nord", "b"), ("nord", "water_return")),
            _pipe("ms", "rete", ("sud", "water_supply"), ("volano-sud", "a")),
            _pipe("rs", "rete", ("volano-sud", "b"), ("sud", "water_return")),
        ],
    )


def deviatrice_fra_due_macchine(machine: str) -> ProjectModel:
    """La forma dell'impianto ibrido, costruita qui.

    La prima macchina sta sul circuito tecnico; la seconda manda dentro una
    **deviatrice**, che in uno stato la porta sul circuito comune e nell'altro
    su uno scambiatore a se'. Nessun identificativo di una fixture entra qui.
    """
    return _plant(
        [_net("rete"), _net("sanitaria", "domestic_hot_water"), _net("fredda", "cold_water")],
        [
            ("sul-circuito", machine),
            ("dietro-la-deviatrice", machine),
            ("deviatrice", DIVERTER),
            ("unione", "tee-junction"),
            ("ripartizione", "tee-split"),
            ("volano", "buffer-four-port"),
            ("scambiatore", "plate-heat-exchanger"),
            ("rientro", "tee-junction"),
            ("acquedotto", "cold-water-inlet"),
            ("utenze", "dhw-draw-off"),
        ],
        [
            _pipe("p1", "rete", ("sul-circuito", "water_supply"), ("unione", "a")),
            _pipe("p2", "rete", ("dietro-la-deviatrice", "water_supply"), ("deviatrice", "in")),
            _pipe("p3", "rete", ("deviatrice", "out_a"), ("unione", "c")),
            _pipe("p4", "rete", ("unione", "b"), ("volano", "primary_in")),
            _pipe("p5", "rete", ("volano", "primary_out"), ("ripartizione", "a")),
            _pipe("p6", "rete", ("ripartizione", "b"), ("sul-circuito", "water_return")),
            _pipe("p7", "rete", ("deviatrice", "out_b"), ("scambiatore", "primary_in")),
            _pipe("p8", "rete", ("scambiatore", "primary_out"), ("rientro", "c")),
            _pipe("p9", "rete", ("ripartizione", "c"), ("rientro", "a")),
            _pipe("p10", "rete", ("rientro", "b"), ("dietro-la-deviatrice", "water_return")),
            _pipe("w1", "fredda", ("acquedotto", "a"), ("scambiatore", "secondary_in")),
            _pipe("w2", "sanitaria", ("scambiatore", "secondary_out"), ("utenze", "a")),
        ],
    )


SAFETY_RULES = ("safety-relief-where-heat-enters-the-water",)
"""La regola della sicurezza: una per generatore (D-182). Fino al 24 settembre
2026 erano due — quella del circuito e quella del generatore isolabile (I-046)."""


def completato(
    project: ProjectModel, registry: ComponentRegistry | None = None
) -> tuple[ProjectModel, list[RuleGap]]:
    """Il modello completato e i suoi punti aperti."""
    used = registry or catalog()
    model, _, gaps = saturate(project, used, rules())
    return model, gaps


def punti(gaps: list[RuleGap], reason: GapReason, rules_ids: tuple[str, ...] = SAFETY_RULES) -> list[str]:
    """I punti aperti di quel motivo, per quelle regole, letti come `motivo:pezzo`."""
    return sorted(
        f"{item.reason.value}:{item.anchor.component_id}"
        for item in gaps
        if item.reason is reason and item.rule_id in rules_ids
    )


def pezzi_con(
    model: ProjectModel, function: str, registry: ComponentRegistry | None = None
) -> list[str]:
    used = registry or catalog()
    return sorted(
        item.id
        for item in model.components
        if function in used.get(item.definition_id).functions
    )


# ---------------------------------------------------------------------------
# 1 — il catalogo dichiara gli stati ammessi
# ---------------------------------------------------------------------------


def test_la_deviatrice_dichiara_i_propri_stati_ammessi() -> None:
    """Due stati, e in ciascuno l'ingresso comunica con **un** ramo solo."""
    states = diverter().hydraulic_states
    assert len(states) == 2, (
        "una valvola multivia con configurazioni alternative ne dichiara almeno "
        "due: con una sola sarebbe un pezzo passante scritto in un altro modo"
    )
    collegamenti = {
        frozenset(group) for state in states for group in state.connects
    }
    assert collegamenti == {frozenset({"in", "out_a"}), frozenset({"in", "out_b"})}


def test_i_due_rami_non_sono_mai_comunicanti_fra_loro() -> None:
    """`out_a ↔ out_b` non e' un passaggio autonomo, in nessuno stato.

    E' la frase del PM: attraversare simultaneamente tutte le porte
    produrrebbe una comunicazione inesistente.
    """
    definition = diverter()
    for state in definition.hydraulic_states:
        assert not any(
            {"out_a", "out_b"} <= set(group) for group in state.connects
        ), f"lo stato {state.id} mette in comunicazione i due rami"
    assert "out_b" not in definition.linked_ports("out_a")
    assert "out_a" not in definition.linked_ports("out_b")


def test_uno_stato_dichiarato_male_non_si_carica() -> None:
    """Un catalogo che sbaglia gli stati si ferma al caricamento.

    Le tre forme che contano: una porta che non esiste, un gruppo con una porta
    sola — che non e' una comunicazione — e uno stato solo, che non e' una
    configurazione alternativa.
    """
    payload = diverter().model_dump(mode="json")
    for rotto in (
        [{"id": "x", "connects": [["in", "non-esiste"]]}, {"id": "y", "connects": [["in", "out_a"]]}],
        [{"id": "x", "connects": [["in"]]}, {"id": "y", "connects": [["in", "out_a"]]}],
        [{"id": "x", "connects": [["in", "out_a"]]}],
        [
            {"id": "x", "connects": [["in", "out_a"]]},
            {"id": "x", "connects": [["in", "out_b"]]},
        ],
    ):
        with pytest.raises(ValidationError):
            ComponentDefinition.model_validate(payload | {"hydraulic_states": rotto})


def test_uno_stato_non_puo_dichiarare_uno_stacco() -> None:
    """Gli stati parlano del **percorso**: uno stacco non e' una via."""
    tee = catalog().get("tee-branch")
    payload = tee.model_dump(mode="json")
    payload["hydraulic_states"] = [
        {"id": "x", "connects": [["a", "branch"]]},
        {"id": "y", "connects": [["a", "b"]]},
    ]
    with pytest.raises(ValidationError):
        ComponentDefinition.model_validate(payload)


# ---------------------------------------------------------------------------
# 2 — un dato solo, letto da chi nomina le linee e da chi guarda la sicurezza
# ---------------------------------------------------------------------------


def test_nessun_modulo_tiene_un_proprio_elenco_dei_mestieri_multivia() -> None:
    """La nomenclatura non ha una lista di funzioni sua.

    Il difetto che questa prova rende impossibile: due elenchi che divergono —
    uno nel modulo delle linee, uno nel motore — e una valvola nuova che passa
    da una parte e non dall'altra.
    """
    from disegnatore_mep.graph import lines as module

    multivia = {
        function
        for definition in catalog().all()
        if definition.hydraulic_states
        for function in definition.functions
    }
    assert multivia, "nessun componente dichiara stati: la prova non direbbe nulla"
    for name, value in vars(module).items():
        if isinstance(value, frozenset) and value & multivia:
            raise AssertionError(
                f"{module.__name__} tiene in {name} i mestieri {sorted(value & multivia)}: "
                f"quale pezzo si attraversa lo dice il catalogo, non il modulo"
            )


def test_la_nomenclatura_attraversa_chi_dichiara_gli_stati() -> None:
    """La linea attraversa una multivia perche' il **catalogo** lo dichiara.

    Si prova sul dato, e sul pezzo in cui la differenza si vede: una valvola che
    devia **e** ripartisce. Un pezzo che ripartisce chiude la linea — la linea
    ci finisce dentro e da ogni uscita ne riparte una nuova — a meno che non lo
    si attraversi. Con gli stati dichiarati la linea passa; togliendoli, il
    pezzo torna a chiuderla. Se la nomenclatura tenesse un proprio elenco di
    mestieri, l'esito non cambierebbe.
    """
    project = deviatrice_fra_due_macchine(GENERIC)
    naming, line_naming = Naming.from_directory(NAMING), LineNaming.from_directory(NAMING)

    def linee(registry: ComponentRegistry) -> tuple[str, ...]:
        graph = read_plant(project, registry, naming)
        return tuple(item.name for item in read_lines(project, registry, graph, line_naming).lines)

    def con(states: bool) -> ComponentRegistry:
        base = diverter()
        variante = base.model_copy(
            update={
                "functions": [*base.functions, "distribution"],
                "hydraulic_states": base.hydraulic_states if states else (),
            }
        )
        return ComponentRegistry(
            [item for item in catalog().all() if item.id != DIVERTER] + [variante],
            symbols=symbols(),
        )

    assert linee(con(True)) != linee(con(False)), (
        "togliere gli stati dichiarati non cambia la lettura delle linee: la "
        "nomenclatura non sta leggendo quel dato"
    )


# ---------------------------------------------------------------------------
# 3 — protetto in ogni stato ammesso
# ---------------------------------------------------------------------------


def _con_una_sicurezza_comune(project: ProjectModel) -> ProjectModel:
    """L'impianto con **una** sicurezza sulla mandata comune, messa a mano: un
    raccordo a stacco fra la confluenza e il volano, e la valvola sul suo stacco.

    Nessuna regola la mette piu' (D-182). Serve a provare cio' che il motore sa
    dire da se': chi una multivia puo' separare da una sicurezza. Si completa con
    tutte le regole tranne quella della sicurezza, perche' gli organi che separano
    sono quelli che le altre regole posano."""
    pipes = [item for item in project.connections if item.id != "p4"]
    return project.model_copy(
        update={
            "components": [
                *project.components,
                ComponentInstance(id="stacco", definition_id="tee-branch"),
                ComponentInstance(id="sicurezza", definition_id="valve-safety"),
            ],
            "connections": [
                *pipes,
                _pipe("p4a", "rete", ("unione", "b"), ("stacco", "a")),
                _pipe("p4b", "rete", ("stacco", "b"), ("volano", "primary_in")),
                _pipe("p4c", "rete", ("stacco", "branch"), ("sicurezza", "a")),
            ],
        }
    )


def test_un_generatore_e_protetto_solo_in_ogni_stato_ammesso() -> None:
    """Chi la deviatrice puo' separare dalla sicurezza e' un dominio a se'.

    Con una sicurezza sola sulla mandata comune, la macchina sul circuito
    tecnico la raggiunge comunque stia la deviatrice; quella dietro la
    deviatrice la raggiunge in uno stato solo, e in un solo stato non basta.
    """
    senza = RuleRegistry(rules=tuple(item for item in rules().all() if item.id not in SAFETY_RULES))
    project = _con_una_sicurezza_comune(deviatrice_fra_due_macchine(GENERIC))
    model, _, _ = saturate(project, catalog(), senza)
    context = RuleContext.build(model, catalog())
    assert pezzi_con(model, SAFETY) == ["sicurezza"]
    assert not context.cut_off_from("sul-circuito", SAFETY, "rete"), (
        "la macchina sul circuito tecnico risulta separata dalla sicurezza "
        "comune: la deviatrice non sta fra lei e il circuito"
    )
    assert context.cut_off_from("dietro-la-deviatrice", SAFETY, "rete"), (
        "la macchina dietro la deviatrice risulta protetta: in uno degli stati "
        "ammessi la deviatrice la manda dove la sicurezza non arriva"
    )


def test_con_d182_nessun_generatore_e_separato_dalla_propria_sicurezza() -> None:
    """Dopo D-182 la domanda sopra non si pone piu' sugli impianti completati:
    ogni generatore ha la sua sicurezza prima di ogni organo, anche quello che
    sta dietro la deviatrice."""
    model, gaps = completato(deviatrice_fra_due_macchine(GENERIC))
    context = RuleContext.build(model, catalog())
    assert len(pezzi_con(model, SAFETY)) == 2
    for generator in ("sul-circuito", "dietro-la-deviatrice"):
        assert not context.cut_off_from(generator, SAFETY, "rete"), generator
    assert not punti(gaps, GapReason.ON_BOARD_UNKNOWN)


def test_senza_deviatrice_le_due_macchine_sono_un_dominio_solo() -> None:
    """Il controllo dell'altro verso: senza organi che separino, si comunica."""
    model, _ = completato(macchine_in_parallelo(GENERIC, 2))
    context = RuleContext.build(model, catalog())
    for index in range(2):
        assert not context.cut_off_from(f"macchina-{index}", SAFETY, "rete")


# ---------------------------------------------------------------------------
# 4 e 5 — una sicurezza per dominio, e nessun dominio scartato
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("quante", [1, 2, 3])
def test_una_sicurezza_per_generatore_qualunque_sia_il_numero_delle_macchine(
    quante: int,
) -> None:
    """D-182: tante sicurezze quanti generatori — fino al 24 settembre era una
    per dominio, qualunque fosse il numero delle macchine (I-046)."""
    model, gaps = completato(macchine_in_parallelo(GENERIC, quante))
    assert len(pezzi_con(model, SAFETY)) == quante
    assert not punti(gaps, GapReason.NO_COMMON_RUN)


def test_due_domini_scollegati_ricevono_una_sicurezza_ciascuno() -> None:
    """Per **dominio**, non per rete: due circuiti chiusi, due sicurezze.

    E' il punto 4 del blocco C. Con la cardinalita' per rete il secondo
    circuito restava senza, e nessuno lo diceva.
    """
    model, gaps = completato(due_domini_scollegati(GENERIC))
    assert len(pezzi_con(model, SAFETY)) == 2, (
        f"le sicurezze posate sono {pezzi_con(model, SAFETY)}: due circuiti "
        f"chiusi indipendenti sono due domini, e ciascuno vuole la propria"
    )
    assert not punti(gaps, GapReason.NO_COMMON_RUN), (
        "la sicurezza e' stata negata a un dominio che il proprio tratto comune "
        "ce l'ha"
    )


def test_una_sicurezza_valida_per_un_dominio_non_viene_scartata() -> None:
    """Il difetto che il PM ha visto: nessun `NO_COMMON_RUN` globale.

    La macchina sul circuito tecnico ha un tratto comune e la sua protezione:
    non la si butta via perche' l'altra macchina non ci arriva in ogni stato.
    """
    model, gaps = completato(deviatrice_fra_due_macchine(GENERIC))
    assert not punti(gaps, GapReason.NO_COMMON_RUN), (
        f"la rete e' stata dichiarata senza tratto comune per la sicurezza: "
        f"{punti(gaps, GapReason.NO_COMMON_RUN)}"
    )
    assert pezzi_con(model, SAFETY), "il dominio che ha un tratto comune e' rimasto scoperto"
    context = RuleContext.build(model, catalog())
    assert not context.cut_off_from("sul-circuito", SAFETY, "rete")


# ---------------------------------------------------------------------------
# 6 — il generatore isolabile e il dato di bordo
# ---------------------------------------------------------------------------


def domande_di_bordo(gaps: list[RuleGap]) -> list[str]:
    return punti(gaps, GapReason.ON_BOARD_UNKNOWN)


def test_il_generatore_dietro_la_deviatrice_riceve_la_sua_senza_domande() -> None:
    """D-182: il dato ignoto non si chiede piu' — la sicurezza si mette comunque.
    Fino al 24 settembre era una domanda al progettista (I-046)."""
    model, gaps = completato(deviatrice_fra_due_macchine(GENERIC))
    assert domande_di_bordo(gaps) == []
    assert len(pezzi_con(model, SAFETY)) == 2


def test_il_generatore_con_la_sicurezza_a_bordo_riceve_la_sua_lo_stesso() -> None:
    """D-182: la sicurezza del generatore si mette anche quando il catalogo dice
    che la macchina ne porta una a bordo. Fino al 24 settembre il dato «presente»
    bastava (I-046)."""
    project = deviatrice_fra_due_macchine(GENERIC)
    project = project.model_copy(
        update={
            "components": [
                item.model_copy(update={"definition_id": WITH_SAFETY})
                if item.id == "dietro-la-deviatrice"
                else item
                for item in project.components
            ]
        }
    )
    model, gaps = completato(project)
    assert domande_di_bordo(gaps) == []
    assert len(pezzi_con(model, SAFETY)) == 2


def test_il_generatore_isolabile_senza_sicurezza_a_bordo_ne_riceve_una_propria() -> None:
    """Il dato c'e' e dice «assente»: sicurezza propria, e non intercettabile."""
    project = deviatrice_fra_due_macchine(GENERIC)
    project = project.model_copy(
        update={
            "components": [
                item.model_copy(update={"definition_id": WITHOUT_SAFETY})
                if item.id == "dietro-la-deviatrice"
                else item
                for item in project.components
            ]
        }
    )
    model, gaps = completato(project)
    assert domande_di_bordo(gaps) == []
    assert len(pezzi_con(model, SAFETY)) == 2, (
        f"le sicurezze sono {pezzi_con(model, SAFETY)}: al generatore che "
        f"dichiara di non averla a bordo ne spetta una propria"
    )
    context = RuleContext.build(model, catalog())
    assert not context.cut_off_from("dietro-la-deviatrice", SAFETY, "rete")


# ---------------------------------------------------------------------------
# 7 — la fixture dell'impianto 4, senza artefatti grafici
# ---------------------------------------------------------------------------


def test_l_impianto_4_non_produce_un_no_common_run_globale() -> None:
    """La fixture dell'ibrido: nessun tratto comune negato, nessun punto aperto,
    e dopo D-182 ogni generatore protetto dalla propria sicurezza — anche la
    caldaia, che la deviatrice manda allo scambiatore.

    E' l'unica prova di questo file che legge una fixture: verifica il
    comportamento e non decide nulla. Non produce artefatti grafici.
    """
    registry = ComponentRegistry.from_directory(CATALOG, symbols=symbols())
    model, _, gaps = saturate(load_project(IBRIDO), registry, rules())
    reasons = sorted(f"{item.reason.value}:{item.anchor.component_id}" for item in gaps)
    assert not reasons, f"restano punti aperti: {reasons}"
    context = RuleContext.build(model, registry)
    generatori = pezzi_con(model, HEAT_GENERATION, registry)
    assert len(generatori) == 2
    for item in generatori:
        assert not context.cut_off_from(item, SAFETY, "primario"), item
    assert len(pezzi_con(model, SAFETY, registry)) == 2


def test_gli_stati_sono_un_dato_e_non_una_riga_di_programma() -> None:
    """Chi non dichiara stati continua a comportarsi come sempre.

    Il contratto del dato nuovo: aggiungerlo non cambia nulla per i pezzi che
    non lo dichiarano — raccordi, valvole di linea, macchine.
    """
    for definition in catalog().all():
        if definition.id in (DIVERTER, SWITCH):
            continue
        assert definition.hydraulic_states == (), (
            f"{definition.id} ha acquisito stati idraulici senza che il PM li "
            f"abbia chiesti"
        )
    # E i due che li dichiarano li dichiarano davvero, ciascuno con i propri:
    # la deviatrice manda **un** ingresso su due uscite, la commutatrice porta
    # **due** ingressi su una uscita, e i due stati non comunicano mai fra loro.
    stati = {
        item.id: {tuple(sorted(pair)) for state in item.hydraulic_states for pair in state.connects}
        for item in catalog().all()
        if item.id in (DIVERTER, SWITCH)
    }
    assert stati[DIVERTER] == {("in", "out_a"), ("in", "out_b")}
    assert stati[SWITCH] == {("in_a", "out"), ("in_b", "out")}
    assert HydraulicState(id="solo", connects=[["in", "out_a"]]).connects
