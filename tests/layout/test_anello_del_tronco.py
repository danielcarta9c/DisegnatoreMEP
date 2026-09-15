"""DRAW-010 §A: il tronco posa senza pezzi addosso, anche quando e' un anello.

La fase del tronco costruisce la forma invece di cercarla, e alla fine
**compatta**: due partecipanti che si trovano addosso si allontanano lungo
l'asse, mai di traverso, perche' di traverso si piegherebbe la tratta.

Fino a DRAW-009 quella mossa cercava il **sottoalbero** oltre la tratta che
porta al piu' lontano dei due. Su un albero quel sottoalbero e' un insieme che
si stacca; su un **anello** — e il tronco di un circuito chiuso e' un anello —
togliere una tratta non stacca niente: la camminata torna indietro dall'altro
capo e si porta dentro anche l'ancora. Le due candidate si scartavano tutte e
due, la posa usciva coi pezzi addosso, e da li' in poi la tavola usciva dal
ripiego di `compose_sheet` invece che dalla propria posa a fasi.

Qui si prova la regola nuova, su un anello costruito apposta:

- **la positiva**: su un tronco ad anello la separazione trova una mossa, e la
  posa che la fase consegna non ha nessuna coppia addosso;
- **la negativa**: la mossa piu' comoda — spostare il solo pezzo che sta
  addosso — piegherebbe la retta che lo tiene in asse, e la separazione non la
  prende: cio' che si muove e' sempre un insieme di **gruppi**, e un gruppo e'
  esattamente cio' che una retta tiene insieme su quell'asse.
"""

import json
from datetime import date
from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.canonical import canonical_json
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.geometry import PlacedSymbol
from disegnatore_mep.layout.partition import SheetPartition, partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.spine import _Spine
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


def _pipe(
    pipe_id: str, network_id: str, a: tuple[str, str], b: tuple[str, str]
) -> ConnectionModel:
    return ConnectionModel(
        id=pipe_id,
        network_id=network_id,
        endpoint_a=PortRef(component_id=a[0], port_id=a[1]),
        endpoint_b=PortRef(component_id=b[0], port_id=b[1]),
    )


@cache
def anello() -> ProjectModel:
    """Un tronco che si chiude: la deviatrice apre due vie e il raccordo le unisce.

    La macchina manda alla deviatrice, la deviatrice sceglie fra il volano e la
    serpentina del bollitore, i due ritornano sullo stesso raccordo e da li' si
    torna alla macchina. Fra la deviatrice e il raccordo il tronco e' un
    **anello**: togliere una qualunque delle sue tratte non lo divide in due.
    """
    project = ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-anello",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 14),
        ),
        plant_regime=PlantRegime.UP_TO_35_KW,
        networks=[
            NetworkModel(id=item, name=item, domain="hydronic", medium=medium)
            for item, medium in (
                ("primario", HEATING),
                ("secondario", HEATING),
                ("fredda", COLD),
                ("sanitaria", DHW),
            )
        ],
        components=[
            ComponentInstance(id=item, definition_id=definition, tag=tag)
            for item, definition, tag in (
                ("macchina", "heat-pump-air-water", "PDC-01"),
                ("deviatrice", "diverting-valve-3way", "VD-01"),
                ("volano", "buffer-four-port", "VOL-01"),
                ("bollitore", "dhw-cylinder", "BOL-01"),
                ("ritorno", "tee-junction", None),
                ("pompa", "pump-circulator", "CIR-01"),
                ("terminali", "fan-coil", "VC-01"),
                ("rete-idrica", "cold-water-inlet", "AF-01"),
                ("rubinetti", "dhw-draw-off", "ACS-01"),
            )
        ],
        connections=[
            _pipe("p1", "primario", ("macchina", "water_supply"), ("deviatrice", "in")),
            _pipe("p2", "primario", ("deviatrice", "out_a"), ("volano", "primary_in")),
            _pipe("p3", "primario", ("volano", "primary_out"), ("ritorno", "a")),
            _pipe("p4", "primario", ("deviatrice", "out_b"), ("bollitore", "coil_in")),
            _pipe("p5", "primario", ("bollitore", "coil_out"), ("ritorno", "c")),
            _pipe("p6", "primario", ("ritorno", "b"), ("macchina", "water_return")),
            _pipe("s1", "secondario", ("volano", "secondary_out"), ("pompa", "a")),
            _pipe("s2", "secondario", ("pompa", "b"), ("terminali", "in")),
            _pipe("s3", "secondario", ("terminali", "out"), ("volano", "secondary_in")),
            _pipe("w1", "fredda", ("rete-idrica", "a"), ("bollitore", "cold_in")),
            _pipe("w2", "sanitaria", ("bollitore", "dhw_out"), ("rubinetti", "a")),
        ],
        subsystems=[
            SubsystemModel(id=item, name=item, component_ids=members, network_ids=nets)
            for item, members, nets in (
                ("generazione", ["macchina", "deviatrice"], ["primario"]),
                (
                    "accumulo",
                    ["volano", "bollitore", "ritorno", "rete-idrica", "rubinetti"],
                    ["primario", "fredda", "sanitaria"],
                ),
                ("distribuzione", ["pompa", "terminali"], ["secondario"]),
            )
        ],
    )
    done, _, _ = saturate(project, catalog(), rules())
    return ProjectModel.model_validate(json.loads(canonical_json(done)))


def _partizione(project: ProjectModel) -> SheetPartition:
    inline = inline_component_ids(project, catalog())
    return partition_project(project, build_trunks(project, inline))[0]


def _spine(project: ProjectModel) -> _Spine:
    """Il costruttore del tronco, pronto ma non ancora eseguito."""
    registry = catalog()
    inline = inline_component_ids(project, registry)
    partition = _partizione(project)
    first = place_sheet(project, partition, registry, NOVE_C_A3, inline)
    return _Spine(project, partition, registry, NOVE_C_A3, first)


def _addosso(builder: _Spine) -> list[tuple[str, str]]:
    """Le coppie di partecipanti piu' vicine dello stacco, capi di una stessa
    tratta esclusi: sono esattamente quelle che `_relieve` deve separare."""
    joined = {
        frozenset({trunk.start.component_id, trunk.end.component_id})
        for trunk in builder.autostrade
    }
    items = list(builder.participants)
    return [
        (one, two)
        for index, one in enumerate(items)
        for two in items[index + 1 :]
        if frozenset({one, two}) not in joined
        and builder._overlaps(builder.laid[one], builder.laid[two])
    ]


def _e_un_anello(builder: _Spine) -> bool:
    """Vero se il grafo delle autostrade ha un ciclo: piu' tratte che nodi meno
    uno, cioe' togliendone una il tronco resta connesso."""
    nodes = {
        component_id
        for trunk in builder.autostrade
        for component_id in (trunk.start.component_id, trunk.end.component_id)
    }
    edges = {
        frozenset({trunk.start.component_id, trunk.end.component_id})
        for trunk in builder.autostrade
    }
    return len(edges) >= len(nodes)


def test_il_tronco_di_questo_impianto_e_un_anello() -> None:
    """La guardia: senza anello le due prove sotto non direbbero niente."""
    builder = _spine(anello())
    builder._lay_out(builder._root())
    assert _e_un_anello(builder), sorted(builder.participants)


def test_su_un_tronco_ad_anello_la_separazione_trova_una_mossa() -> None:
    """La positiva: la fase consegna una posa senza pezzi addosso.

    E si misura anche **perche'** prima non ci riusciva: la camminata che
    cercava il sottoalbero oltre una tratta, su un anello, si riporta dentro
    l'ancora da qualunque dei due capi si parta, e scartava tutte e due le
    candidate.
    """
    builder = _spine(anello())
    builder._lay_out(builder._root())
    clash = _addosso(builder)
    assert clash, "senza una coppia addosso questa prova non direbbe niente"

    one, two = clash[0]
    edges = builder._edges()

    def sottoalbero(origin: str, first: str) -> set[str]:
        """`_beyond` com'era: in ampiezza dal vicino, senza fermarsi mai."""
        seen = {origin, first}
        frontier = [first]
        while frontier:
            item = frontier.pop()
            for _, _, other, _ in edges.get(item, ()):
                if other in seen:
                    continue
                seen.add(other)
                frontier.append(other)
        return seen - {origin}

    for victim, anchor in ((two, one), (one, two)):
        edge = next(item for item in edges.get(victim, ()) if item[2] in builder.laid)
        assert anchor in sottoalbero(edge[2], victim), (
            f"su un anello il sottoalbero oltre {edge[2]} -> {victim} deve "
            f"contenere anche {anchor}: e' la ragione per cui la mossa di "
            f"DRAW-009 si scartava"
        )

    assert builder._push_apart(one, two), (one, two)
    assert not builder._overlaps(builder.laid[one], builder.laid[two])

    builder = _spine(anello())
    assert builder.build().symbols, "la fase del tronco non ha consegnato una posa"
    assert _addosso(builder) == []


def _rette_rotte(builder: _Spine, laid: dict[str, PlacedSymbol]) -> list[str]:
    """Le uguaglianze d'asse che una posa viola: sono le rette del tronco.

    Un vincolo `_Same` su un asse dice che due pezzi stanno sulla stessa retta
    dell'altro asse, a meno di uno scarto fisso; `_grouped` li raccoglie in
    gruppi e tiene lo scarto di ciascuno. Violarne uno vuol dire che quella
    tratta non e' piu' un rettilineo: e' la definizione di «piegare il tronco».
    """
    rotte: list[str] = []
    for axis in (0, 1):
        demands = builder.axes[axis]
        for item in builder.participants:
            head = demands.leader[item]
            mine, its = laid[item].origin, laid[head].origin
            voluto = demands.within[item] - demands.within[head]
            got = (mine.x_mm - its.x_mm) if axis == 0 else (mine.y_mm - its.y_mm)
            if abs(got - voluto) > TOLERANCE_MM:
                rotte.append(f"asse {'xy'[axis]}: {item} rispetto a {head}")
    return rotte


def test_una_separazione_che_piegherebbe_il_tronco_e_rifiutata() -> None:
    """La negativa: la mossa comoda — spostare il solo pezzo addosso — rompe una
    retta, e la separazione non la prende.

    Quello che si muove e' sempre un **insieme di gruppi**, e un gruppo e'
    esattamente cio' che una retta tiene insieme su quell'asse: il blocco che
    `_follow` restituisce non puo' spezzarne uno. La prova lo dice due volte —
    la mossa da sola romperebbe, quella vera no — cosi' che non regga per caso.
    """
    builder = _spine(anello())
    builder._lay_out(builder._root())
    clash = _addosso(builder)
    assert clash, "senza una coppia addosso questa prova non direbbe niente"
    one, two = clash[0]

    # La mossa comoda: sposta il solo pezzo addosso finche' esce, senza
    # portarsi dietro chi sta sulla sua stessa retta. Si guarda dove una retta
    # c'e' davvero: su un asse in cui il pezzo sta da solo nel proprio gruppo
    # non c'e' niente da rompere, e quel caso non direbbe nulla.
    provate = 0
    for victim, anchor in ((one, two), (two, one)):
        for axis in (0, 1):
            demands = builder.axes[axis]
            compagni = [
                item
                for item in builder.participants
                if item != victim
                and demands.leader[item] == demands.leader[victim]
            ]
            if not compagni:
                continue
            for sign in (1, -1):
                room = builder._clearance(victim, anchor, axis, sign)
                if room <= TOLERANCE_MM:
                    continue
                da_solo = dict(builder.laid)
                before = da_solo[victim]
                moved = (
                    {"x_mm": before.origin.x_mm + sign * room}
                    if axis == 0
                    else {"y_mm": before.origin.y_mm + sign * room}
                )
                da_solo[victim] = before.model_copy(
                    update={"origin": before.origin.model_copy(update=moved)}
                )
                assert _rette_rotte(builder, da_solo), (
                    f"spostare {victim} da solo sull'asse {'xy'[axis]} non "
                    f"rompe nessuna retta, e invece {compagni} ce lo tengono"
                )
                provate += 1
    assert provate, (
        "nessuna mossa comoda romperebbe una retta: la negativa non direbbe niente"
    )

    assert builder._push_apart(one, two), (one, two)
    assert _rette_rotte(builder, dict(builder.laid)) == []


@pytest.mark.parametrize("axis", (0, 1))
def test_il_blocco_che_si_muove_e_sempre_un_insieme_di_gruppi(axis: int) -> None:
    """La forma generale della negativa: nessun blocco spezza un gruppo.

    E' la proprieta' da cui discende che la separazione non puo' piegare il
    tronco, e vale per ogni partecipante e per tutti e due i versi.
    """
    builder = _spine(anello())
    builder._lay_out(builder._root())
    leader = builder.axes[axis].leader
    for victim in builder.participants:
        for sign in (1, -1):
            block = set(builder._follow(axis, sign, victim))
            capi = {leader[item] for item in block}
            interi = {
                item for item in builder.participants if leader[item] in capi
            }
            assert block == interi, (axis, sign, victim, sorted(block ^ interi))
