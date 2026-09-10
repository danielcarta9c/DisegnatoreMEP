"""Le prove di DRAW-007, blocco A, scritte prima del codice: la tavola ha una
gerarchia, e la gerarchia si calcola sul grafo.

Il PO, il 10 settembre 2026:

    «Le tubazioni che vanno alle macchine principali sono l'autostrada, e su
    quelle i costi dovrebbero essere ancora maggiori. Oggi nel nostro router
    non abbiamo distinzione tra autostrada principale e strade secondarie:
    tutto e' principale ma non e' cosi'.»

La primitiva e' quella che il PO ha scelto fra tre (`ACTIVE_WORK_PACKAGE.md`
§A.1), dopo che la prima — «quanta parte dell'impianto dipende da questa
tratta» — e' collassata sul prototipo: su un circuito chiuso il cammino a
valle rientra su se' stesso, e ventuno tratte su ventidue prendevano lo
stesso peso.

Il **tronco fra le macchine principali**:

- **macchine di spina**: la macchina di generazione principale, ogni macchina
  che accumula o separa idraulicamente, ogni collettore o ripartitore;
- **autostrada**: la tratta sta su un percorso fra due macchine di spina che
  non attraversa ne' un'altra macchina di spina ne' una macchina qualsiasi.
  Su un circuito chiuso ci stanno **sia la mandata sia il ritorno**, che e'
  precisamente cio' che il PO chiama «le due macro-linee parallele»;
- **distribuzione**: il percorso porta a una macchina che di spina non e' —
  un utilizzatore, un generatore oltre il principale, un confine di rete;
- **servizio**: il percorso non porta a nessuna macchina. Stacchi ciechi.

Nessuna prova qui fissa quante tratte ci siano per livello: quel numero e'
della fixture, non della regola.
"""

import ast
import inspect
from datetime import date
from pathlib import Path
from types import ModuleType

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.layout import hierarchy as hierarchy_module
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.hierarchy import Level, hierarchy_of, spine_machines
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import (
    ComponentInstance,
    ConnectionModel,
    NetworkModel,
    PortRef,
    ProjectMetadata,
    ProjectModel,
    SubsystemModel,
)
from disegnatore_mep.model.types import PlantRegime

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
HEATING = "heating_water"


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def _pipe(
    identifier: str, network: str, a: tuple[str, str], b: tuple[str, str]
) -> ConnectionModel:
    return ConnectionModel(
        id=identifier,
        network_id=network,
        endpoint_a=PortRef(component_id=a[0], port_id=a[1]),
        endpoint_b=PortRef(component_id=b[0], port_id=b[1]),
    )


def _plant(
    components: list[tuple[str, str]],
    connections: list[ConnectionModel],
    networks: list[tuple[str, str]] | None = None,
) -> ProjectModel:
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-gerarchia",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 10),
        ),
        plant_regime=PlantRegime.UP_TO_35_KW,
        networks=[
            NetworkModel(id=key, name=key, domain="hydronic", medium=medium)
            for key, medium in (networks or [("primo", HEATING), ("secondo", HEATING)])
        ],
        components=[
            ComponentInstance(id=item, definition_id=definition)
            for item, definition in components
        ],
        connections=connections,
        subsystems=[
            SubsystemModel(
                id="tutto",
                name="tutto",
                component_ids=[item for item, _ in components],
                network_ids=[key for key, _ in (networks or [("primo", ""), ("secondo", "")])],
            )
        ],
    )


def cascata_con_utenza() -> ProjectModel:
    """Due generatori in parallelo su un volano, un'utenza sul secondario, e
    uno stacco cieco. Ci sono tutti e tre i livelli, e una sola volta."""
    return _plant(
        [
            ("nord", "heat-pump-air-water"),
            ("sud", "heat-pump-air-water"),
            ("unione", "tee-junction"),
            ("ripartizione", "tee-split"),
            ("volano", "buffer-four-port"),
            ("corpo", "radiator"),
            ("presa", "tee-branch"),
            ("manometro", "pressure-gauge"),
        ],
        [
            _pipe("p1", "primo", ("nord", "water_supply"), ("unione", "a")),
            _pipe("p2", "primo", ("sud", "water_supply"), ("unione", "c")),
            _pipe("p3", "primo", ("unione", "b"), ("volano", "primary_in")),
            _pipe("p4", "primo", ("volano", "primary_out"), ("ripartizione", "a")),
            _pipe("p5", "primo", ("ripartizione", "b"), ("nord", "water_return")),
            _pipe("p6", "primo", ("ripartizione", "c"), ("sud", "water_return")),
            _pipe("s1", "secondo", ("volano", "secondary_out"), ("presa", "a")),
            _pipe("s2", "secondo", ("presa", "b"), ("corpo", "in")),
            _pipe("s3", "secondo", ("corpo", "out"), ("volano", "secondary_in")),
            _pipe("st", "secondo", ("presa", "branch"), ("manometro", "a")),
        ],
    )


def riempimento_fra_due_reti() -> ProjectModel:
    """Il ponte del §D di DRAW-006-R1: un accessorio appeso con **due porte**,
    che pesca dall'acquedotto e sbocca sul ritorno tecnico."""
    return _plant(
        [
            ("nord", "heat-pump-air-water"),
            ("volano", "buffer-four-port"),
            ("presa-tecnica", "tee-branch"),
            ("riempimento", "filling-unit"),
            ("presa-fredda", "tee-branch-cold"),
            ("acquedotto", "cold-water-inlet"),
            ("riserva", "dhw-cylinder"),
        ],
        [
            _pipe("p1", "primo", ("nord", "water_supply"), ("volano", "primary_in")),
            _pipe("p2", "primo", ("volano", "primary_out"), ("presa-tecnica", "a")),
            _pipe("p3", "primo", ("presa-tecnica", "b"), ("nord", "water_return")),
            _pipe("w1", "fredda", ("acquedotto", "a"), ("presa-fredda", "a")),
            _pipe("w2", "fredda", ("presa-fredda", "b"), ("riserva", "cold_in")),
            _pipe("sf", "fredda", ("presa-fredda", "branch"), ("riempimento", "a")),
            _pipe("st", "primo", ("riempimento", "b"), ("presa-tecnica", "branch")),
        ],
        networks=[("primo", HEATING), ("fredda", "cold_water")],
    )


def _levels(project: ProjectModel) -> dict[tuple[str, ...], Level]:
    registry = catalog()
    trunks = build_trunks(project, inline_component_ids(project, registry))
    return hierarchy_of(project, registry, trunks)


def _by_definition(project: ProjectModel) -> frozenset[tuple[int, str, str]]:
    """La classificazione letta **per struttura**: livello e voci di catalogo ai
    due capi, mai identificativi. E' cio' che deve restare uguale quando i
    nomi cambiano."""
    registry = catalog()
    trunks = build_trunks(project, inline_component_ids(project, registry))
    levels = hierarchy_of(project, registry, trunks)
    definitions = {item.id: item.definition_id for item in project.components}
    letta: set[tuple[int, str, str]] = set()
    for trunk in trunks:
        primo, secondo = sorted(
            (definitions[trunk.start.component_id], definitions[trunk.end.component_id])
        )
        letta.add((int(levels[trunk.connection_ids]), primo, secondo))
    return frozenset(letta)


def _renamed(project: ProjectModel) -> ProjectModel:
    """Gli stessi pezzi con altri nomi, e in ordine inverso."""
    names = {item.id: f"z{index:02d}" for index, item in enumerate(project.components)}
    return project.model_copy(
        update={
            "components": [
                item.model_copy(update={"id": names[item.id]})
                for item in reversed(project.components)
            ],
            "connections": [
                item.model_copy(
                    update={
                        "endpoint_a": item.endpoint_a.model_copy(
                            update={"component_id": names[item.endpoint_a.component_id]}
                        ),
                        "endpoint_b": item.endpoint_b.model_copy(
                            update={"component_id": names[item.endpoint_b.component_id]}
                        ),
                    }
                )
                for item in project.connections
            ],
            "subsystems": [
                item.model_copy(
                    update={"component_ids": [names[key] for key in item.component_ids]}
                )
                for item in project.subsystems
            ],
        }
    )


# ---------------------------------------------------------------------------
# A.4 — la gerarchia non dipende dai nomi
# ---------------------------------------------------------------------------


def test_la_gerarchia_non_cambia_rinominando_gli_identificativi() -> None:
    """Criterio 1. Rinominare tutto e invertire l'ordine dei pezzi non sposta
    una tratta di livello: la classificazione si legge per struttura."""
    assert _by_definition(cascata_con_utenza()) == _by_definition(
        _renamed(cascata_con_utenza())
    )


def test_la_gerarchia_non_cambia_mescolando_le_connessioni() -> None:
    """Criterio 1, l'altro verso: l'ordine con cui il file elenca le tubazioni
    non e' un dato dell'impianto."""
    project = cascata_con_utenza()
    mixed = project.model_copy(update={"connections": list(reversed(project.connections))})
    assert _by_definition(project) == _by_definition(mixed)


def _stringhe_del_codice(module: ModuleType) -> list[str]:
    """Le stringhe che il modulo **usa**, senza le sue spiegazioni.

    La differenza conta: D-069 vieta di ramificare sul nome di un pezzo, non di
    dire in italiano che cosa fa un collettore. Una prova che vietasse anche la
    prosa spingerebbe a scrivere codice muto, che e' il contrario di cio' che
    questo repository chiede.
    """
    tree = ast.parse(inspect.getsource(module))
    docstrings = {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef)
        and node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
        and isinstance(node.body[0].value.value, str)
    }
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstrings
    ]


def test_il_modulo_della_gerarchia_non_nomina_nessun_pezzo() -> None:
    """Criterio 1, D-069: il codice che classifica non conosce il catalogo per
    nome. Nessuna voce di catalogo e nessun identificativo di impianto puo'
    comparire fra le stringhe che il modulo usa — le spiegazioni restano
    libere, il codice no."""
    usate = _stringhe_del_codice(hierarchy_module)
    voci = {definition.id for definition in catalog().all()}
    for stringa in usate:
        assert stringa not in voci, stringa
    for pezzo in cascata_con_utenza().components:
        assert pezzo.id not in usate, pezzo.id


# ---------------------------------------------------------------------------
# A.1 — i tre livelli, sulla forma che li contiene tutti
# ---------------------------------------------------------------------------


def test_la_mandata_e_il_ritorno_di_un_circuito_chiuso_sono_tutt_e_due_autostrada() -> None:
    """Le «due macro-linee parallele» del PO. E' il caso su cui la prima
    primitiva era collassata: qui si pretende che **entrambe** siano in cima,
    non una sola."""
    levels = _levels(cascata_con_utenza())
    andata = levels[("p1",)], levels[("p3",)]
    ritorno = levels[("p4",)], levels[("p5",)]
    assert set(andata) == {Level.AUTOSTRADA}, andata
    assert set(ritorno) == {Level.AUTOSTRADA}, ritorno


def test_il_ramo_che_porta_un_utilizzatore_e_distribuzione() -> None:
    """Il collettore verso le utenze: porta a una macchina che di spina non e'."""
    levels = _levels(cascata_con_utenza())
    assert levels[("s2",)] is Level.DISTRIBUZIONE
    assert levels[("s3",)] is Level.DISTRIBUZIONE


def test_una_macchina_oltre_la_principale_non_alza_il_proprio_ramo() -> None:
    """«I generatori oltre il primo allineato» sono distribuzione: una sola
    macchina di generazione sta sulla spina, le altre ci si innestano."""
    levels = _levels(cascata_con_utenza())
    rami = {levels[("p2",)], levels[("p6",)]}
    assert rami == {Level.DISTRIBUZIONE}, rami


def test_un_accessorio_appeso_non_si_attraversa_nemmeno_con_due_porte() -> None:
    """Il ponte del riempimento ha due porte e tocca due reti, ma resta uno
    stacco: chi lo attraversasse leggerebbe come tronco fra due macchine di
    spina — la riserva di qua, il volano di la' — una tubazione di servizio, e
    per giunta unirebbe due reti che sulla tavola non si toccano.

    E' il difetto che questa prova presidia: senza il capolinea, sulla tavola 1
    e sulla tavola 2 lo stacco del riempimento finiva in autostrada."""
    levels = _levels(riempimento_fra_due_reti())
    assert levels[("sf",)] is Level.SERVIZIO, levels
    assert levels[("st",)] is Level.SERVIZIO, levels


def test_uno_stacco_cieco_e_servizio() -> None:
    """Il manometro non porta da nessuna parte: e' l'ultimo livello."""
    assert _levels(cascata_con_utenza())[("st",)] is Level.SERVIZIO


def test_una_sola_macchina_di_generazione_sta_sulla_spina() -> None:
    """La spina non e' «tutte le macchine»: la generazione ne mette una sola,
    e a parita' di mestiere lo spareggio e' strutturale, mai un nome."""
    project = cascata_con_utenza()
    spina = spine_machines(project, catalog())
    generatori = {"nord", "sud"} & spina
    assert len(generatori) == 1, spina
    assert "volano" in spina
    assert "corpo" not in spina
    assert "manometro" not in spina


# ---------------------------------------------------------------------------
# Criterio 2 — l'ordine fra i livelli, come proprieta' e non come numero
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("plant", [cascata_con_utenza], ids=lambda item: item.__name__)
def test_ogni_tratta_di_autostrada_pesa_piu_di_ogni_tratta_di_servizio(plant) -> None:  # type: ignore[no-untyped-def]
    """Criterio 2. Non si fissa quante siano: si pretende l'ordine."""
    levels = _levels(plant())
    autostrade = [key for key, value in levels.items() if value is Level.AUTOSTRADA]
    servizi = [key for key, value in levels.items() if value is Level.SERVIZIO]
    assert autostrade and servizi, levels
    for alta in autostrade:
        for bassa in servizi:
            assert levels[alta] > levels[bassa], (alta, bassa)


def test_il_livello_e_confrontabile_e_ordinato() -> None:
    """Il livello e' una grandezza ordinata, cosi' il costo puo' pesarlo senza
    tradurlo in un elenco di casi."""
    assert Level.AUTOSTRADA > Level.DISTRIBUZIONE > Level.SERVIZIO
