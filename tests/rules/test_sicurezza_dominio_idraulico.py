"""Le prove del grafo di DRAW-005-R1, blocco A nella correzione PM (I-046),
scritte prima del codice.

Il PM (`docs/pm/2026-09-08-rilievi-po-draw005-r1.md`, correzione dopo il
collaudo) e il Work Package:

1. il numero delle sicurezze non si deduce dal numero dei generatori;
2. si protegge ogni **dominio** pressurizzato: una sicurezza comune serve piu'
   macchine finche' resta comunicante con loro nelle configurazioni ammesse —
   cioe' finche' fra la macchina in esercizio e la sicurezza non c'e' un organo
   di chiusura che non sia quello della macchina stessa;
3. la presenza a bordo e' un dato **tri-stato** del catalogo: presente, assente,
   ignoto. Un campo mancante e' ignoto, non assente, e non autorizza ad
   aggiungere dispositivi;
4. protezioni ulteriori compaiono solo con un dato di catalogo (assente) o con
   domini autonomi modellati; nel caso indeterminato (ignoto) il motore genera
   una **domanda aperta**, non un pezzo;
5. lo sfogo aria non e' la sicurezza: uno, sull'attacco alto della riserva.

Le prove sono generali: gli impianti sono costruiti qui, con una, due e tre
macchine; la macchina «con sicurezza a bordo» e quella «che dichiara di non
averla» sono la stessa voce della generica con un dato in piu'. Nessun
identificativo o coordinata della tavola 1 entra nelle attese, salvo nella
prova di regressione in coda, che legge la fixture e non decide nulla.
"""

from collections.abc import Callable
from datetime import date
from functools import cache
from pathlib import Path

import pytest
from pydantic import ValidationError

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import (
    CLOSING_FUNCTIONS,
    ComponentDefinition,
    ComponentTrait,
    OnBoard,
)
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
from disegnatore_mep.model.types import PlantRegime, PortFlow
from disegnatore_mep.rules.apply import evaluate_in_phases, saturate
from disegnatore_mep.rules.proposal import GapReason, RuleGap, proposed_component_id
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"
PROVA_1 = ROOT / "examples" / "prova" / "prova-1-due-pdc-accumulo-combinato.json"

HEATING = "heating_water"
COLD = "cold_water"
DHW = "domestic_hot_water"
SAFETY = "safety"
AIR_RELEASE = "air_release"
GENERIC = "heat-pump-air-water"
WITH_SAFETY = "heat-pump-air-water-sicurezza-a-bordo"
WITHOUT_SAFETY = "heat-pump-air-water-sicurezza-non-a-bordo"
"""Le tre macchine della prova: la generica, che del bordo dice solo il
circolatore (sicurezza **ignota**); la stessa che dichiara la sicurezza a bordo
(**presente**); la stessa che dichiara di non averla (**assente**). Vivono solo
qui: sono il modo di provare che l'esito dipende dal dato dichiarato."""


@cache
def catalog() -> ComponentRegistry:
    symbols = SymbolRegistry.from_directory(SYMBOLS)
    base = ComponentRegistry.from_directory(CATALOG, symbols=symbols)
    generic = base.get(GENERIC)
    assert SAFETY not in generic.carries_on_board
    assert SAFETY not in generic.lacks_on_board, (
        "la macchina generica del catalogo non deve dire nulla della sicurezza: "
        "il dato mancante e' cio' che il pacchetto tratta come ignoto"
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
    return ComponentRegistry([*base.all(), present, absent], symbols=symbols)


@cache
def rules() -> RuleRegistry:
    registry = RuleRegistry.from_directory(RULES)
    registry.cross_check(catalog())
    return registry


def _net(network_id: str, medium: str) -> NetworkModel:
    return NetworkModel(id=network_id, name=network_id, domain="hydronic", medium=medium)


def _pipe(pipe_id: str, network_id: str, a: tuple[str, str], b: tuple[str, str]) -> ConnectionModel:
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
    regime: PlantRegime | None = PlantRegime.UP_TO_35_KW,
) -> ProjectModel:
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-dominio",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 9),
        ),
        plant_regime=regime,
        networks=networks,
        components=[
            ComponentInstance(id=item, definition_id=definition)
            for item, definition in components
        ],
        connections=connections,
    )


# ---------------------------------------------------------------------------
# Gli impianti di prova
# ---------------------------------------------------------------------------


def una_macchina_in_anello(machine: str) -> ProjectModel:
    return _plant(
        [_net("anello", HEATING)],
        [("generatore", machine), ("terminale", "fan-coil")],
        [
            _pipe("m", "anello", ("generatore", "water_supply"), ("terminale", "in")),
            _pipe("r", "anello", ("terminale", "out"), ("generatore", "water_return")),
        ],
    )


def due_macchine_in_parallelo(machine: str) -> ProjectModel:
    return _plant(
        [_net("primo", HEATING), _net("secondo", HEATING)],
        [
            ("nord", machine),
            ("sud", machine),
            ("unione", "tee-junction"),
            ("ripartizione", "tee-split"),
            ("volano", "buffer-four-port"),
            ("pompa", "pump-circulator"),
            ("corpo", "radiator"),
        ],
        [
            _pipe("p1", "primo", ("nord", "water_supply"), ("unione", "a")),
            _pipe("p2", "primo", ("sud", "water_supply"), ("unione", "c")),
            _pipe("p3", "primo", ("unione", "b"), ("volano", "primary_in")),
            _pipe("p4", "primo", ("volano", "primary_out"), ("ripartizione", "a")),
            _pipe("p5", "primo", ("ripartizione", "b"), ("nord", "water_return")),
            _pipe("p6", "primo", ("ripartizione", "c"), ("sud", "water_return")),
            _pipe("s1", "secondo", ("volano", "secondary_out"), ("pompa", "a")),
            _pipe("s2", "secondo", ("pompa", "b"), ("corpo", "in")),
            _pipe("s3", "secondo", ("corpo", "out"), ("volano", "secondary_in")),
        ],
    )


def _con_accumulo_combinato(
    machine: str, quante_macchine: int, regime: PlantRegime | None = PlantRegime.UP_TO_35_KW
) -> ProjectModel:
    components = [
        ("serbatoio", "buffer-combined"),
        ("pompa", "pump-circulator"),
        ("corpo", "radiator"),
        ("rete-idrica", "cold-water-inlet"),
        ("rubinetti", "dhw-draw-off"),
    ]
    pipes = [
        _pipe("s1", "secondo", ("serbatoio", "secondary_out"), ("pompa", "a")),
        _pipe("s2", "secondo", ("pompa", "b"), ("corpo", "in")),
        _pipe("s3", "secondo", ("corpo", "out"), ("serbatoio", "secondary_in")),
        _pipe("w1", "fredda", ("rete-idrica", "a"), ("serbatoio", "cold_in")),
        _pipe("w2", "calda", ("serbatoio", "dhw_out"), ("rubinetti", "a")),
    ]
    if quante_macchine == 1:
        components.append(("generatore", machine))
        pipes += [
            _pipe("p1", "primo", ("generatore", "water_supply"), ("serbatoio", "primary_in")),
            _pipe("p2", "primo", ("serbatoio", "primary_out"), ("generatore", "water_return")),
        ]
    else:
        components += [
            ("nord", machine),
            ("sud", machine),
            ("unione", "tee-junction"),
            ("ripartizione", "tee-split"),
        ]
        pipes += [
            _pipe("p1", "primo", ("nord", "water_supply"), ("unione", "a")),
            _pipe("p2", "primo", ("sud", "water_supply"), ("unione", "c")),
            _pipe("p3", "primo", ("unione", "b"), ("serbatoio", "primary_in")),
            _pipe("p4", "primo", ("serbatoio", "primary_out"), ("ripartizione", "a")),
            _pipe("p5", "primo", ("ripartizione", "b"), ("nord", "water_return")),
            _pipe("p6", "primo", ("ripartizione", "c"), ("sud", "water_return")),
        ]
    return _plant(
        [_net("primo", HEATING), _net("secondo", HEATING), _net("fredda", COLD), _net("calda", DHW)],
        components,
        pipes,
        regime,
    )


def una_macchina_con_accumulo_combinato(machine: str) -> ProjectModel:
    return _con_accumulo_combinato(machine, 1)


def due_macchine_con_accumulo_combinato(machine: str) -> ProjectModel:
    return _con_accumulo_combinato(machine, 2)


def tre_macchine_con_un_organo_di_rete(machine: str) -> ProjectModel:
    """Tre macchine in cascata: le prime due confluiscono, poi **un organo di
    rete scritto dal progettista** chiude quel tratto, poi confluisce la terza.
    L'ultima confluenza e' dopo l'organo: la sicurezza di circuito, che sta li',
    resta raggiungibile dalla terza macchina e non dalle prime due, che
    l'organo di rete — non loro — puo' separare da lei. Sono un dominio
    isolabile."""
    return _plant(
        [_net("primo", HEATING), _net("secondo", HEATING)],
        [
            ("nord", machine),
            ("centro", machine),
            ("sud", machine),
            ("unione-1", "tee-junction"),
            ("organo-di-rete", "valve-isolation"),
            ("unione-2", "tee-junction"),
            ("volano", "buffer-four-port"),
            ("ripartizione-1", "tee-split"),
            ("ripartizione-2", "tee-split"),
            ("pompa", "pump-circulator"),
            ("corpo", "radiator"),
        ],
        [
            _pipe("p1", "primo", ("nord", "water_supply"), ("unione-1", "a")),
            _pipe("p2", "primo", ("centro", "water_supply"), ("unione-1", "c")),
            _pipe("p3", "primo", ("unione-1", "b"), ("organo-di-rete", "a")),
            _pipe("p4", "primo", ("organo-di-rete", "b"), ("unione-2", "a")),
            _pipe("p5", "primo", ("sud", "water_supply"), ("unione-2", "c")),
            _pipe("p6", "primo", ("unione-2", "b"), ("volano", "primary_in")),
            _pipe("p7", "primo", ("volano", "primary_out"), ("ripartizione-1", "a")),
            _pipe("p8", "primo", ("ripartizione-1", "b"), ("sud", "water_return")),
            _pipe("p9", "primo", ("ripartizione-1", "c"), ("ripartizione-2", "a")),
            _pipe("p10", "primo", ("ripartizione-2", "b"), ("nord", "water_return")),
            _pipe("p11", "primo", ("ripartizione-2", "c"), ("centro", "water_return")),
            _pipe("s1", "secondo", ("volano", "secondary_out"), ("pompa", "a")),
            _pipe("s2", "secondo", ("pompa", "b"), ("corpo", "in")),
            _pipe("s3", "secondo", ("corpo", "out"), ("volano", "secondary_in")),
        ],
    )


def due_reti_con_una_macchina_ciascuna(machine: str) -> ProjectModel:
    """Due domini autonomi modellati come due reti: ciascuna con il proprio
    generatore e il proprio anello."""
    return _plant(
        [_net("est", HEATING), _net("ovest", HEATING)],
        [
            ("gen-est", machine),
            ("term-est", "fan-coil"),
            ("gen-ovest", machine),
            ("term-ovest", "fan-coil"),
        ],
        [
            _pipe("e1", "est", ("gen-est", "water_supply"), ("term-est", "in")),
            _pipe("e2", "est", ("term-est", "out"), ("gen-est", "water_return")),
            _pipe("o1", "ovest", ("gen-ovest", "water_supply"), ("term-ovest", "in")),
            _pipe("o2", "ovest", ("term-ovest", "out"), ("gen-ovest", "water_return")),
        ],
    )


DOMINIO_UNICO: list[Callable[[str], ProjectModel]] = [
    una_macchina_in_anello,
    due_macchine_in_parallelo,
    una_macchina_con_accumulo_combinato,
    due_macchine_con_accumulo_combinato,
]
DOMINIO_UNICO_IDS = [item.__name__ for item in DOMINIO_UNICO]
MACCHINE = (GENERIC, WITH_SAFETY, WITHOUT_SAFETY)


# ---------------------------------------------------------------------------
# Come si cammina il grafo completato
# ---------------------------------------------------------------------------


class Walk:
    """Il modello completato letto lungo le tubazioni del percorso, con cio' che
    pende dagli stacchi."""

    def __init__(self, model: ProjectModel) -> None:
        self.model = model
        registry = catalog()
        self.definitions: dict[str, ComponentDefinition] = {
            item.id: registry.get(item.definition_id) for item in model.components
        }
        self.inline = frozenset(
            item.id
            for item in model.components
            if registry.resolve(item.definition_id).is_inline
            or registry.get(item.definition_id).is_a_fitting
        )
        self.off_the_run = {
            (item.id, port.id)
            for item in model.components
            for port in self.definitions[item.id].ports
            if port.off_the_run
        }
        self.at_port: dict[tuple[str, str], ConnectionModel] = {}
        self.run_pipes_of: dict[str, list[ConnectionModel]] = {}
        for connection in model.connections:
            for ref in (connection.endpoint_a, connection.endpoint_b):
                self.at_port[(ref.component_id, ref.port_id)] = connection
            if any(
                (ref.component_id, ref.port_id) in self.off_the_run
                for ref in (connection.endpoint_a, connection.endpoint_b)
            ):
                continue
            for ref in (connection.endpoint_a, connection.endpoint_b):
                self.run_pipes_of.setdefault(ref.component_id, []).append(connection)

    def functions(self, component_id: str) -> frozenset[str]:
        return frozenset(self.definitions[component_id].functions)

    def closes(self, component_id: str) -> bool:
        return bool(self.functions(component_id) & CLOSING_FUNCTIONS)

    def maintainable(self, component_id: str) -> bool:
        return self.definitions[component_id].has_trait(ComponentTrait.MAINTAINABLE)

    def generators(self) -> list[str]:
        return sorted(
            component_id
            for component_id, definition in self.definitions.items()
            if "heat_generation" in definition.functions
        )

    def reserves(self) -> list[str]:
        return sorted(
            component_id
            for component_id, definition in self.definitions.items()
            if definition.has_trait(ComponentTrait.HOLDS_ITS_OWN_VOLUME)
        )

    def port_with_flow(self, component_id: str, flow: PortFlow) -> str:
        return next(
            port.id
            for port in self.definitions[component_id].ports
            if port.flow is flow and not port.off_the_run
        )

    def _peer(self, connection: ConnectionModel, component_id: str) -> str:
        return next(
            ref.component_id
            for ref in (connection.endpoint_a, connection.endpoint_b)
            if ref.component_id != component_id
        )

    def stretch_from(self, component_id: str, port_id: str) -> list[str]:
        """I pezzi incontrati dall'attacco in poi, fino al primo che ferma: un
        nodo, un pezzo manutenibile, un raccordo da cui si va in piu' direzioni."""
        found: list[str] = []
        cursor = component_id
        connection = self.at_port.get((component_id, port_id))
        seen = {component_id}
        while connection is not None:
            peer = self._peer(connection, cursor)
            if peer in seen:
                break
            found.append(peer)
            seen.add(peer)
            if peer not in self.inline or self.maintainable(peer):
                break
            onward = [
                item for item in self.run_pipes_of.get(peer, []) if item.id != connection.id
            ]
            if len(onward) != 1:
                break
            connection, cursor = onward[0], peer
        return found

    def hanging_from(self, component_id: str) -> list[str]:
        """Gli accessori che pendono dagli stacchi di un pezzo, attraverso gli
        organi in fila sullo stacco, fino al pezzo che regge lo stacco."""
        found: list[str] = []
        for owner, port_id in sorted(self.off_the_run):
            if owner != component_id:
                continue
            connection = self.at_port.get((owner, port_id))
            cursor = owner
            seen = {owner}
            while connection is not None:
                peer = self._peer(connection, cursor)
                if peer in seen:
                    break
                found.append(peer)
                seen.add(peer)
                onward = [
                    item
                    for (holder, _), item in self.at_port.items()
                    if holder == peer and item.id != connection.id
                ]
                if len(onward) != 1:
                    break
                connection, cursor = onward[0], peer
        return found

    def with_function(self, function: str) -> list[str]:
        return sorted(
            component_id
            for component_id in self.definitions
            if function in self.functions(component_id)
        )

    def holder_of(self, component_id: str) -> str | None:
        """Il pezzo del percorso da cui un accessorio appeso pende."""
        for owner, _ in sorted(self.off_the_run):
            if component_id in self.hanging_from(owner):
                return owner
        return None

    def anchored_to(self, component_id: str, function: str) -> list[str]:
        """I pezzi con quella funzione che una regola ha posato su un attacco di
        questo componente: letti dall'identificativo derivato dall'attacco."""
        found: list[str] = []
        for other in self.model.components:
            if function not in self.functions(other.id):
                continue
            for port in self.definitions[component_id].ports:
                anchor = PortRef(component_id=component_id, port_id=port.id)
                if proposed_component_id(other.definition_id, anchor) == other.id:
                    found.append(other.id)
        return sorted(found)

    def before_the_first_closer(self, component_id: str, port_id: str) -> list[str]:
        found: list[str] = []
        for item in self.stretch_from(component_id, port_id):
            if self.closes(item):
                break
            found.append(item)
        return found

    def hung_before_the_first_closer(
        self, component_id: str, port_id: str, function: str
    ) -> list[str]:
        return [
            item
            for piece in self.before_the_first_closer(component_id, port_id)
            for item in self.hanging_from(piece)
            if function in self.functions(item)
        ]

    def own_closers(self, component_id: str) -> set[str]:
        """Gli organi propri di una macchina: il primo che chiude su ciascuno dei
        suoi attacchi del percorso, attraverso i pezzi in linea."""
        found: set[str] = set()
        for port in self.definitions[component_id].ports:
            if port.off_the_run or (component_id, port.id) not in self.at_port:
                continue
            for item in self.stretch_through_inline(component_id, port.id):
                if self.closes(item):
                    found.add(item)
                    break
        return found

    def stretch_through_inline(self, component_id: str, port_id: str) -> list[str]:
        """Come `stretch_from`, ma non si ferma sui pezzi manutenibili in linea —
        il filtro della macchina e' della macchina, e la valvola oltre il filtro
        e' la sua — e attraversa le confluenze **seguendo il fluido**: da un
        raccordo prosegue per l'unica tubazione che ne esce."""
        found: list[str] = []
        cursor = component_id
        connection = self.at_port.get((component_id, port_id))
        seen = {component_id}
        while connection is not None:
            peer = self._peer(connection, cursor)
            if peer in seen:
                break
            found.append(peer)
            seen.add(peer)
            if peer not in self.inline:
                break
            onward = [
                item for item in self.run_pipes_of.get(peer, []) if item.id != connection.id
            ]
            if len(onward) != 1:
                leaving = [
                    item
                    for item in onward
                    if any(
                        ref.component_id == peer
                        and next(
                            port.flow for port in self.definitions[peer].ports if port.id == ref.port_id
                        )
                        is PortFlow.OUT
                        for ref in (item.endpoint_a, item.endpoint_b)
                    )
                ]
                if len(leaving) != 1:
                    break
                onward = leaving
            connection, cursor = onward[0], peer
        return found

    def rule_of(self, component_id: str) -> str | None:
        """La regola che ha posato un pezzo, letta dalla sua evidenza."""
        component = next(item for item in self.model.components if item.id == component_id)
        return next(
            (
                evidence.reference.split("@", 1)[0]
                for evidence in component.evidence
                if evidence.kind == "rule"
            ),
            None,
        )

    def reaches(self, component_id: str, function: str, network_id: str) -> bool:
        """Dalla macchina, attraverso i soli organi propri, si arriva a un pezzo
        con quella funzione — in linea o appeso a uno stacco."""
        own = self.own_closers(component_id)
        frontier = [
            self.at_port[(component_id, port.id)]
            for port in self.definitions[component_id].ports
            if not port.off_the_run
            and (component_id, port.id) in self.at_port
            and self.at_port[(component_id, port.id)].network_id == network_id
        ]
        seen_pieces = {component_id}
        seen_pipes = {item.id for item in frontier}
        cursor_of = {item.id: component_id for item in frontier}
        while frontier:
            pipe = frontier.pop(0)
            peer = self._peer(pipe, cursor_of[pipe.id])
            if peer in seen_pieces:
                continue
            seen_pieces.add(peer)
            if function in self.functions(peer) or any(
                function in self.functions(item) for item in self.hanging_from(peer)
            ):
                return True
            if self.closes(peer) and peer not in own:
                continue
            for onward in self.run_pipes_of.get(peer, []):
                if onward.id in seen_pipes or onward.network_id != network_id:
                    continue
                seen_pipes.add(onward.id)
                cursor_of[onward.id] = peer
                frontier.append(onward)
        return False


def _saturated(model: ProjectModel) -> tuple[Walk, list[RuleGap]]:
    done, _, gaps = saturate(model, catalog(), rules())
    return Walk(done), gaps


def _walk(build: Callable[[str], ProjectModel], machine: str) -> Walk:
    walk, gaps = _saturated(build(machine))
    assert not gaps, [(gap.rule_id, gap.reason.value, gap.anchor) for gap in gaps]
    return walk


def _safeties_on(walk: Walk, network_id: str) -> list[str]:
    return sorted(
        item
        for item in walk.with_function(SAFETY)
        if walk.at_port[(item, walk.definitions[item].ports[0].id)].network_id == network_id
        or any(
            connection.network_id == network_id
            for (holder, _), connection in walk.at_port.items()
            if holder == item
        )
    )


def _heating_networks(model: ProjectModel) -> list[str]:
    return sorted(item.id for item in model.networks if item.medium == HEATING)


# ---------------------------------------------------------------------------
# A3 — il bordo macchina e' tri-stato, e il dato mancante e' ignoto
# ---------------------------------------------------------------------------


def test_il_bordo_macchina_e_tri_stato_e_il_dato_mancante_e_ignoto() -> None:
    generic = catalog().get(GENERIC)
    assert generic.on_board("circulation") is OnBoard.PRESENT
    assert generic.on_board(SAFETY) is OnBoard.UNKNOWN
    assert catalog().get(WITH_SAFETY).on_board(SAFETY) is OnBoard.PRESENT
    assert catalog().get(WITHOUT_SAFETY).on_board(SAFETY) is OnBoard.ABSENT
    # Le tre macchine differiscono solo per quel dato.
    for variant in (WITH_SAFETY, WITHOUT_SAFETY):
        assert catalog().get(variant).functions == generic.functions
        assert catalog().get(variant).trait_set == generic.trait_set


def test_una_funzione_non_puo_essere_dichiarata_insieme_presente_e_assente() -> None:
    generic = catalog().get(GENERIC)
    with pytest.raises(ValidationError, match="sia a bordo sia non a bordo"):
        ComponentDefinition.model_validate(
            {
                **generic.model_dump(mode="json"),
                "id": "contraddittoria",
                "carries_on_board": [*generic.carries_on_board, SAFETY],
                "lacks_on_board": [SAFETY],
            }
        )


# ---------------------------------------------------------------------------
# A1, A2, A4 — un dominio: una sicurezza di circuito, sulla mandata comune
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("build", DOMINIO_UNICO, ids=DOMINIO_UNICO_IDS)
@pytest.mark.parametrize("machine", (GENERIC, WITHOUT_SAFETY))
def test_un_dominio_riceve_una_sicurezza_sola_qualunque_sia_il_numero_delle_macchine(
    build: Callable[[str], ProjectModel], machine: str
) -> None:
    """Una per dominio, non una per generatore: con una o due macchine che non
    dichiarano la sicurezza a bordo (ignota o assente) la rete di
    riscaldamento ne ha esattamente una."""
    walk = _walk(build, machine)
    for network_id in _heating_networks(walk.model):
        found = _safeties_on(walk, network_id)
        expected = 1 if any(
            walk.at_port.get((generator, walk.port_with_flow(generator, PortFlow.OUT)))
            and walk.at_port[(generator, walk.port_with_flow(generator, PortFlow.OUT))].network_id
            == network_id
            for generator in walk.generators()
        ) else 0
        assert len(found) == expected, (network_id, found)


@pytest.mark.parametrize("build", DOMINIO_UNICO, ids=DOMINIO_UNICO_IDS)
@pytest.mark.parametrize("machine", (GENERIC, WITHOUT_SAFETY))
def test_la_sicurezza_di_circuito_sta_sulla_mandata_comune_vicino_al_gruppo_e_prima_di_ogni_organo(
    build: Callable[[str], ProjectModel], machine: str
) -> None:
    """Sul tratto in cui le mandate sono gia' una, attaccata a cio' che le
    unisce — o alla macchina, se e' una sola — e prima di qualunque organo di
    chiusura di quel tratto."""
    walk = _walk(build, machine)
    generators = walk.generators()
    for safety in walk.with_function(SAFETY):
        holder = walk.holder_of(safety)
        assert holder is not None, safety
        # Chi regge la sicurezza sta sul tratto della mandata comune: dalla
        # mandata di ogni generatore, seguendo il fluido attraverso i soli
        # pezzi in linea, lo si incontra.
        for generator in generators:
            outlet = walk.port_with_flow(generator, PortFlow.OUT)
            downstream = walk.stretch_through_inline(generator, outlet)
            assert holder in downstream, (generator, holder, downstream)
            # E prima di qualunque organo di chiusura sul tratto comune: fra
            # l'ultima confluenza e la sicurezza non c'e' nulla che chiuda.
            joins = [
                item
                for item in downstream
                if item in walk.inline and len(walk.run_pipes_of.get(item, [])) > 2
            ]
            start = downstream.index(joins[-1]) + 1 if joins else 0
            between = downstream[start : downstream.index(holder)]
            assert not any(walk.closes(item) for item in between), (generator, between)
        # Attaccata a cio' che unisce le mandate, o alla macchina sola.
        if len(generators) == 1:
            outlet = walk.port_with_flow(generators[0], PortFlow.OUT)
            assert walk.stretch_from(generators[0], outlet)[0] == holder, holder
        else:
            outlet = walk.port_with_flow(generators[0], PortFlow.OUT)
            downstream = walk.stretch_through_inline(generators[0], outlet)
            join = downstream[downstream.index(holder) - 1]
            assert len(walk.run_pipes_of.get(join, [])) > 2, (holder, join)
        # E l'ha posata la regola del circuito, non quella per macchina.
        assert walk.rule_of(safety) == "safety-relief-on-the-closed-circuit", safety


@pytest.mark.parametrize("build", DOMINIO_UNICO, ids=DOMINIO_UNICO_IDS)
@pytest.mark.parametrize("machine", MACCHINE)
def test_nessuna_sicurezza_per_macchina_ne_sulla_riserva_in_un_dominio_unico(
    build: Callable[[str], ProjectModel], machine: str
) -> None:
    """Nessuna sicurezza ancorata a un generatore o alla riserva: la sola
    protezione e' quella del circuito, qualunque cosa dica il bordo macchina."""
    walk = _walk(build, machine)
    for safety in walk.with_function(SAFETY):
        assert walk.rule_of(safety) == "safety-relief-on-the-closed-circuit", safety
    for reserve in walk.reserves():
        assert not walk.anchored_to(reserve, SAFETY), reserve


@pytest.mark.parametrize("build", DOMINIO_UNICO, ids=DOMINIO_UNICO_IDS)
@pytest.mark.parametrize("machine", (GENERIC, WITHOUT_SAFETY))
def test_ogni_generatore_resta_comunicante_con_la_sicurezza_attraverso_i_soli_organi_propri(
    build: Callable[[str], ProjectModel], machine: str
) -> None:
    """La configurazione ammessa: la macchina in esercizio ha i propri organi
    aperti, e da li' raggiunge la sicurezza senza attraversare organi altrui."""
    walk = _walk(build, machine)
    for generator in walk.generators():
        outlet = walk.port_with_flow(generator, PortFlow.OUT)
        network_id = walk.at_port[(generator, outlet)].network_id
        assert walk.reaches(generator, SAFETY, network_id), generator


@pytest.mark.parametrize("build", DOMINIO_UNICO, ids=DOMINIO_UNICO_IDS)
def test_con_la_sicurezza_a_bordo_di_ogni_macchina_il_circuito_non_ne_riceve_una_esterna(
    build: Callable[[str], ProjectModel],
) -> None:
    walk = _walk(build, WITH_SAFETY)
    for network_id in _heating_networks(walk.model):
        assert not _safeties_on(walk, network_id), network_id


def test_con_la_sicurezza_a_bordo_di_una_macchina_sola_il_circuito_la_vuole_lo_stesso() -> None:
    """Il bordo di un membro non protegge l'altro: la sicurezza di circuito
    resta, una, sulla mandata comune."""
    model = due_macchine_con_accumulo_combinato(GENERIC)
    model = model.model_copy(
        update={
            "components": [
                item.model_copy(update={"definition_id": WITH_SAFETY})
                if item.id == "nord"
                else item
                for item in model.components
            ]
        }
    )
    walk, gaps = _saturated(model)
    assert not gaps
    assert len(_safeties_on(walk, "primo")) == 1
    assert not walk.anchored_to("nord", SAFETY)
    assert not walk.anchored_to("sud", SAFETY)


# ---------------------------------------------------------------------------
# A2, A5 — un dominio isolabile: dato di catalogo, o domanda aperta
# ---------------------------------------------------------------------------


def test_nel_dominio_isolabile_la_sicurezza_di_circuito_sta_dopo_l_ultima_confluenza() -> None:
    """La terza macchina, che confluisce dopo l'organo di rete, raggiunge la
    sicurezza di circuito attraverso i soli organi propri; le prime due no, e
    per loro parla il dato di catalogo (prove sotto)."""
    walk, gaps = _saturated(tre_macchine_con_un_organo_di_rete(GENERIC))
    assert walk.reaches("sud", SAFETY, "primo")
    assert not walk.reaches("nord", SAFETY, "primo")
    assert not walk.reaches("centro", SAFETY, "primo")
    circuit = [item for item in walk.with_function(SAFETY)]
    assert len(circuit) == 1, circuit
    holder = walk.holder_of(circuit[0])
    downstream = walk.stretch_through_inline("sud", walk.port_with_flow("sud", PortFlow.OUT))
    assert holder in downstream and "organo-di-rete" not in downstream[downstream.index(holder) :]
    del gaps


def test_con_il_dato_assente_ogni_macchina_isolabile_riceve_la_propria_sicurezza() -> None:
    """Il catalogo dice che la macchina non porta la sicurezza a bordo, e un
    organo non suo puo' separarla da quella di circuito: la riceve, sulla
    mandata, attaccata a lei e prima del proprio organo."""
    walk, gaps = _saturated(tre_macchine_con_un_organo_di_rete(WITHOUT_SAFETY))
    assert not gaps, gaps
    for generator in ("nord", "centro"):
        own = walk.anchored_to(generator, SAFETY)
        assert len(own) == 1, (generator, own)
        outlet = walk.port_with_flow(generator, PortFlow.OUT)
        hung = walk.hung_before_the_first_closer(generator, outlet, SAFETY)
        assert hung == own, (generator, hung, own)
        assert walk.reaches(generator, SAFETY, "primo")
    assert not walk.anchored_to("sud", SAFETY)
    # E la sicurezza di circuito resta, una, oltre l'organo di rete.
    circuit = [
        item
        for item in walk.with_function(SAFETY)
        if not any(item in walk.anchored_to(generator, SAFETY) for generator in walk.generators())
    ]
    assert len(circuit) == 1, circuit


def test_con_il_dato_ignoto_la_macchina_isolabile_e_una_domanda_aperta_non_un_pezzo() -> None:
    """Il campo mancante e' ignoto, non assente: il motore non aggiunge, chiede."""
    walk, gaps = _saturated(tre_macchine_con_un_organo_di_rete(GENERIC))
    for generator in walk.generators():
        assert not walk.anchored_to(generator, SAFETY), generator
    asked = sorted(
        gap.anchor.component_id for gap in gaps if gap.reason is GapReason.ON_BOARD_UNKNOWN
    )
    assert asked == ["centro", "nord"], [(gap.rule_id, gap.reason.value, gap.anchor) for gap in gaps]
    for gap in gaps:
        assert gap.missing_function == SAFETY
        assert gap.network_id == "primo"
    # Nessun altro punto aperto: la sicurezza di circuito c'e'.
    assert all(gap.reason is GapReason.ON_BOARD_UNKNOWN for gap in gaps), gaps
    assert len([item for item in walk.with_function(SAFETY)]) == 1


def test_con_il_dato_presente_la_macchina_isolabile_non_chiede_e_non_riceve() -> None:
    walk, gaps = _saturated(tre_macchine_con_un_organo_di_rete(WITH_SAFETY))
    assert not gaps, gaps
    for generator in walk.generators():
        assert not walk.anchored_to(generator, SAFETY), generator
    # E la sicurezza di circuito non serve: ogni macchina la porta a bordo.
    assert not walk.with_function(SAFETY)


def test_la_domanda_aperta_si_conta_per_macchina_e_dice_di_che_dato_si_tratta() -> None:
    _, gaps = _saturated(tre_macchine_con_un_organo_di_rete(GENERIC))
    keys = {gap.key for gap in gaps}
    assert len(keys) == len(gaps) == 2
    for gap in gaps:
        assert gap.reason is GapReason.ON_BOARD_UNKNOWN
        assert gap.anchor.component_id in {"nord", "centro"}


def test_due_reti_sono_due_domini_e_ogni_dominio_ha_la_propria_sicurezza() -> None:
    walk = _walk(due_reti_con_una_macchina_ciascuna, GENERIC)
    assert len(_safeties_on(walk, "est")) == 1
    assert len(_safeties_on(walk, "ovest")) == 1
    # Ciascuna e' la sicurezza del proprio circuito — che con una macchina sola
    # comincia sulla sua mandata — non una protezione per macchina.
    for safety in walk.with_function(SAFETY):
        assert walk.rule_of(safety) == "safety-relief-on-the-closed-circuit", safety


# ---------------------------------------------------------------------------
# Sopra i 35 kW — la Raccolta R vuole i dispositivi su ogni generatore
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("machine", (GENERIC, WITHOUT_SAFETY))
def test_sopra_i_35_kw_ogni_generatore_ha_la_propria_sicurezza_e_nessuna_in_piu(
    machine: str,
) -> None:
    walk, gaps = _saturated(_con_accumulo_combinato(machine, 2, PlantRegime.OVER_35_KW))
    assert not gaps, gaps
    for generator in walk.generators():
        own = walk.anchored_to(generator, SAFETY)
        assert len(own) == 1, (generator, own)
    assert len(_safeties_on(walk, "primo")) == len(walk.generators())


# ---------------------------------------------------------------------------
# A6 — lo sfogo aria resta uno, sull'attacco alto della riserva
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("build", DOMINIO_UNICO[2:], ids=DOMINIO_UNICO_IDS[2:])
@pytest.mark.parametrize("machine", MACCHINE)
def test_lo_sfogo_aria_resta_uno_sull_attacco_dedicato_della_riserva(
    build: Callable[[str], ProjectModel], machine: str
) -> None:
    walk = _walk(build, machine)
    vents = walk.with_function(AIR_RELEASE)
    assert len(vents) == 1, vents
    reserve = walk.reserves()[0]
    assert walk.anchored_to(reserve, AIR_RELEASE) == vents
    for generator in walk.generators():
        assert not walk.anchored_to(generator, AIR_RELEASE), generator


# ---------------------------------------------------------------------------
# Stabilita': rieseguire non propone, permutare non sposta
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("build", [*DOMINIO_UNICO, tre_macchine_con_un_organo_di_rete])
@pytest.mark.parametrize("machine", MACCHINE)
def test_rieseguire_le_regole_sul_modello_completato_non_propone_niente(
    build: Callable[[str], ProjectModel], machine: str
) -> None:
    done, _, gaps = saturate(build(machine), catalog(), rules())
    again = evaluate_in_phases(done, catalog(), rules())
    assert not again.proposals, [item.component_id for item in again.proposals]
    # I punti aperti sono gli stessi, non di piu'.
    assert {gap.key for gap in again.gaps} <= {gap.key for gap in gaps}


def test_permutare_componenti_e_connessioni_non_sposta_la_sicurezza() -> None:
    base = due_macchine_con_accumulo_combinato(GENERIC)
    permuted = base.model_copy(
        update={
            "components": list(reversed(base.components)),
            "connections": list(reversed(base.connections)),
        }
    )
    first = Walk(saturate(base, catalog(), rules())[0])
    second = Walk(saturate(permuted, catalog(), rules())[0])
    assert first.with_function(SAFETY) == second.with_function(SAFETY)
    for safety in first.with_function(SAFETY):
        assert first.holder_of(safety) == second.holder_of(safety)


# ---------------------------------------------------------------------------
# La tavola 1, letta come fixture di regressione
# ---------------------------------------------------------------------------


def test_la_tavola_1_ha_una_sola_sicurezza_di_circuito_sulla_mandata_vicino_al_gruppo() -> None:
    """Regressione sulla fixture: una sola sicurezza sulla rete di
    riscaldamento, appesa al raccordo attaccato alla confluenza delle mandate e
    prima della valvola della riserva; niente sulla riserva, niente per
    macchina; uno sfogo aria; nessuna domanda aperta."""
    done, _, gaps = saturate(load_project(PROVA_1), catalog(), rules())
    assert not gaps, [(gap.rule_id, gap.reason.value) for gap in gaps]
    walk = Walk(done)
    heating = [item.id for item in done.networks if item.medium == HEATING]
    safeties = sorted(
        {item for network_id in heating for item in _safeties_on(walk, network_id)}
    )
    assert len(safeties) == 1, safeties
    assert walk.rule_of(safeties[0]) == "safety-relief-on-the-closed-circuit"
    for generator in walk.generators():
        assert not walk.anchored_to(generator, SAFETY), generator
        outlet = walk.port_with_flow(generator, PortFlow.OUT)
        assert walk.reaches(generator, SAFETY, walk.at_port[(generator, outlet)].network_id)
    for reserve in walk.reserves():
        assert not walk.anchored_to(reserve, SAFETY), reserve
    holder = walk.holder_of(safeties[0])
    assert holder is not None
    outlet = walk.port_with_flow(walk.generators()[0], PortFlow.OUT)
    downstream = walk.stretch_through_inline(walk.generators()[0], outlet)
    join = downstream[downstream.index(holder) - 1]
    assert len(walk.run_pipes_of.get(join, [])) > 2, (holder, join)
    assert len(walk.with_function(AIR_RELEASE)) == 1
