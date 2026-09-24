"""Un ingresso per utente: le prove di DRAW-009 §A.1 (I-061).

Il PO, l'11 settembre 2026:

    «Non si deve fare una rete unica di af, non si fa cosi'; si fanno piu'
    ingressi.»

Il difetto che queste prove chiudono si vedeva sulla tavola 2: la rete `fredda`
era **una linea sola** che partiva dall'acquedotto, attraversava il foglio,
raccoglieva per strada il gruppo di riempimento del ritorno tecnico e finiva sul
`cold_in` del bollitore. Una linea cosi' non e' solo brutta: **inchioda i pezzi
che tocca**. Misurato sulla geometria consegnata da DRAW-008, il bollitore non
si spostava di cinque millimetri senza che `w1-a-a-4` smettesse di instradarsi.

La regola e' del contenuto, non del disegno: dove piu' utenti prendono acqua
fredda, il grafo completato porta **piu' confini di rete distinti**, uno per
utente, ciascuno con la propria rete. L'unione a T con un ingresso solo esiste —
serve a risparmiare sui piccoli componenti a servizio dell'ingresso — ma e'
**un'opzione che chiede il progettista**: non si deduce dal grafo e non la
sceglie il codice.
"""

from datetime import date
from functools import cache
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
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
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"
TAVOLA_2 = ROOT / "examples" / "prova" / "prova-2-pdc-deviatrice-acs.json"

BOUNDARY = "boundary"
COLD = "cold_water"
HEATING = "heating_water"
DHW = "domestic_hot_water"


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


def completato(project: ProjectModel) -> ProjectModel:
    done, _, _ = saturate(project, catalog(), rules())
    return done


def _pipe(
    pipe_id: str, network_id: str, a: tuple[str, str], b: tuple[str, str]
) -> ConnectionModel:
    return ConnectionModel(
        id=pipe_id,
        network_id=network_id,
        endpoint_a=PortRef(component_id=a[0], port_id=a[1]),
        endpoint_b=PortRef(component_id=b[0], port_id=b[1]),
    )


def due_utenti_di_acqua_fredda() -> ProjectModel:
    """Un impianto minimo con **due** utenti di acqua fredda.

    Il primo e' dichiarato dal progettista — l'acquedotto che alimenta il
    bollitore — il secondo nasce dal completamento: il circuito chiuso vuole un
    gruppo di riempimento, e il gruppo pesca dall'acqua fredda. Sono due utenti
    lontani, ed e' il caso che il PO ha in mente.

    **Da D-175 gli utenti che il completamento porta sono tre**: la riserva
    sanitaria vuole la miscelatrice termostatica, e la miscelatrice prende
    l'acqua fredda dal proprio terzo attacco. Il nome della prova resta quello
    dei due utenti che il PO aveva in mente l'11 settembre.
    """
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="due-utenti-af",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 13),
        ),
        plant_regime=PlantRegime.UP_TO_35_KW,
        networks=[
            NetworkModel(id="tecnico", name="tecnico", domain="hydronic", medium=HEATING),
            NetworkModel(id="fredda", name="fredda", domain="hydronic", medium=COLD),
            NetworkModel(id="calda", name="calda", domain="hydronic", medium=DHW),
        ],
        components=[
            ComponentInstance(id="generatore", definition_id="heat-pump-air-water", tag="PDC-01"),
            ComponentInstance(id="serbatoio", definition_id="buffer-combined", tag="ACC-01"),
            ComponentInstance(id="rete-idrica", definition_id="cold-water-inlet", tag="AF-01"),
            ComponentInstance(id="rubinetti", definition_id="dhw-draw-off", tag="ACS-01"),
        ],
        connections=[
            _pipe("p1", "tecnico", ("generatore", "water_supply"), ("serbatoio", "primary_in")),
            _pipe("p2", "tecnico", ("serbatoio", "primary_out"), ("generatore", "water_return")),
            _pipe("w1", "fredda", ("rete-idrica", "a"), ("serbatoio", "cold_in")),
            _pipe("w2", "calda", ("serbatoio", "dhw_out"), ("rubinetti", "a")),
        ],
        subsystems=[
            SubsystemModel(
                id="centrale",
                name="centrale",
                component_ids=["generatore", "serbatoio", "rete-idrica", "rubinetti"],
                network_ids=["tecnico", "fredda", "calda"],
            )
        ],
    )


def _inlets(project: ProjectModel, medium: str) -> list[ComponentInstance]:
    """I confini da cui quel fluido **entra**, letti dal catalogo."""
    found = []
    for item in project.components:
        definition = catalog().get(item.definition_id)
        if BOUNDARY not in definition.functions:
            continue
        ports = definition.ports
        if len(ports) == 1 and ports[0].medium == medium and ports[0].flow.value == "out":
            found.append(item)
    return found


def _users_of(project: ProjectModel, inlet_id: str) -> set[str]:
    """Chi quella rete serve davvero.

    Non chi la tocca. Un raccordo di derivazione e un organo in linea stanno
    **sulla** linea, non in fondo; e cio' che pende da uno stacco con un attacco
    solo — uno scarico, uno sfogo — e' corredo della linea, non un utente che la
    linea serve. L'utente e' cio' che resta: una macchina, o un ponte fra due
    reti come il gruppo di riempimento, che l'acqua fredda se la porta via.
    """
    definitions = {item.id: item.definition_id for item in project.components}
    networks = {
        connection.network_id
        for connection in project.connections
        if inlet_id in (connection.endpoint_a.component_id, connection.endpoint_b.component_id)
    }
    touched: set[str] = set()
    for connection in project.connections:
        if connection.network_id not in networks:
            continue
        for ref in (connection.endpoint_a, connection.endpoint_b):
            if ref.component_id == inlet_id:
                continue
            resolved = catalog().resolve(definitions[ref.component_id])
            if resolved.definition.is_a_fitting or resolved.is_inline:
                continue
            if resolved.definition.attaches_on_a_branch and len(resolved.definition.ports) == 1:
                continue
            touched.add(ref.component_id)
    return touched


def test_ogni_utente_di_acqua_fredda_ha_il_proprio_ingresso() -> None:
    """La prova generale del criterio 2.

    Dati piu' utenti di acqua fredda, il completamento produce **un ingresso per
    ciascuno** e non una rete che si dirama; ciascun ingresso sta su una rete
    propria. Gli utenti sono tre — il bollitore, il gruppo di riempimento e, da
    D-175, la miscelatrice termostatica — e gli ingressi tre.
    """
    completo = completato(due_utenti_di_acqua_fredda())
    inlets = _inlets(completo, COLD)
    assert len(inlets) == 3, [item.id for item in inlets]

    cold = [item for item in completo.networks if item.medium == COLD]
    assert len(cold) == 3, [item.id for item in cold]

    reti = {
        item.id: {
            connection.network_id
            for connection in completo.connections
            if item.id
            in (connection.endpoint_a.component_id, connection.endpoint_b.component_id)
        }
        for item in inlets
    }
    unite = [rete for rete in reti.values() if len(rete) != 1]
    assert not unite, reti
    assert len({next(iter(rete)) for rete in reti.values()}) == 3, reti


def test_nessuna_rete_di_acqua_fredda_serve_due_utenti_in_serie() -> None:
    """Il rovescio della stessa medaglia: **mai** una rete unica che si dirama.

    E' la forma misurabile del divieto del PO. Una rete di acqua fredda tocca
    un utente solo; gli altri pezzi che vi stanno sopra sono raccordi e organi
    in linea al servizio di quell'unico ingresso.
    """
    completo = completato(due_utenti_di_acqua_fredda())
    for inlet in _inlets(completo, COLD):
        users = _users_of(completo, inlet.id)
        assert len(users) == 1, (inlet.id, sorted(users))


def test_l_unione_a_t_non_compare_se_non_e_dichiarata() -> None:
    """L'unione a T e' un'opzione del progettista, non un esito del motore.

    Si misura su cio' che la si riconoscerebbe: un raccordo di derivazione
    sull'acqua fredda, cioe' il pezzo con cui una linea sola si sdoppierebbe
    per servire due utenti. Il completamento non ne mette nessuno, e finche' il
    progettista non dichiara l'unione gli ingressi restano separati.
    """
    completo = completato(due_utenti_di_acqua_fredda())
    cold = {item.id for item in completo.networks if item.medium == COLD}
    branches = [
        item.id
        for item in completo.components
        if catalog().get(item.definition_id).is_a_fitting
        and any(
            connection.network_id in cold
            and item.id
            in (connection.endpoint_a.component_id, connection.endpoint_b.component_id)
            for connection in completo.connections
        )
    ]
    derivazioni = [
        item
        for item in branches
        if sum(
            1
            for connection in completo.connections
            if item in (connection.endpoint_a.component_id, connection.endpoint_b.component_id)
        )
        > 2
    ]
    assert derivazioni == [], derivazioni


def test_sulla_tavola_2_la_rete_fredda_non_e_piu_una_linea_sola() -> None:
    """Il criterio 1, sull'impianto vero.

    Sulla tavola 2 il grafo completato porta un confine di rete per utente,
    ciascuno con la propria rete, e nessuna tratta di acqua fredda serve due
    utenti in serie. Prima ce n'era uno solo, e la sua linea attraversava il
    foglio. Gli utenti sono tre: il bollitore, il gruppo di riempimento e, da
    D-175, la miscelatrice termostatica.
    """
    completo = completato(load_project(TAVOLA_2))
    inlets = _inlets(completo, COLD)
    assert len(inlets) == 3, [item.id for item in inlets]
    assert len({item.tag for item in inlets}) == 3, [item.tag for item in inlets]
    assert len([item for item in completo.networks if item.medium == COLD]) == 3
    for inlet in inlets:
        assert len(_users_of(completo, inlet.id)) == 1, inlet.id
