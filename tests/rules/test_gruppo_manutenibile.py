"""Le prove del grafo di DRAW-005, parte A, scritte prima del codice.

La matrice PM (`docs/pm/2026-09-05-audit-simboli-e-contenuto-tavola1.md`) cambia la
regola dell'intercettazione: non piu' «una valvola per ogni porta di ogni pezzo
manutenibile», ma «isolare il gruppo senza duplicare organi consecutivi che chiudono
lo stesso volume». Un **gruppo manutenibile** e' una macchina con gli accessori che
una regola per componente le ha posato sui suoi stessi attacchi — il filtro a Y sul
ritorno della pompa di calore — e si isola dall'esterno, mai fra i suoi membri.

Le prove sono generali: gli impianti sono costruiti qui, con il catalogo di prova,
e nessun identificativo o coordinata della tavola 1 entra nelle attese. Ogni prova
cammina il grafo attacco per attacco, senza contare totali (D-088).
"""

from collections.abc import Callable
from datetime import date
from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import (
    CLOSING_FUNCTIONS,
    ComponentDefinition,
    ComponentTrait,
)
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.canonical import canonical_json
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
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.proposal import GapReason, RuleGap, proposed_component_id
from disegnatore_mep.rules.registry import RuleRegistry
from disegnatore_mep.rules.schema import RuleCardinality, RuleDefinition

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"
PROVA_1 = ROOT / "examples" / "prova" / "prova-1-due-pdc-accumulo-combinato.json"

HEATING = "heating_water"
COLD = "cold_water"
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
) -> ProjectModel:
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-gruppo",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 7),
        ),
        plant_regime=PlantRegime.UP_TO_35_KW,
        networks=networks,
        components=[
            ComponentInstance(id=item, definition_id=definition)
            for item, definition in components
        ],
        connections=connections,
    )


# ---------------------------------------------------------------------------
# Gli impianti di prova, costruiti qui
# ---------------------------------------------------------------------------


def una_macchina_in_anello() -> ProjectModel:
    """Una pompa di calore e un terminale, e basta: il ritorno e' uno solo."""
    return _plant(
        [_net("anello", HEATING)],
        [("generatore", "heat-pump-air-water"), ("terminale", "fan-coil")],
        [
            _pipe("m", "anello", ("generatore", "water_supply"), ("terminale", "in")),
            _pipe("r", "anello", ("terminale", "out"), ("generatore", "water_return")),
        ],
    )


def due_macchine_in_parallelo() -> ProjectModel:
    """Due pompe di calore in parallelo su un volano a quattro attacchi."""
    return _plant(
        [_net("primo", HEATING), _net("secondo", HEATING)],
        [
            ("nord", "heat-pump-air-water"),
            ("sud", "heat-pump-air-water"),
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


def _con_accumulo_combinato(quante_macchine: int) -> ProjectModel:
    """Una o due pompe di calore su un accumulo combinato, con acqua fredda in
    ingresso al serpentino e acqua calda sanitaria in uscita alle utenze."""
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
        components.append(("generatore", "heat-pump-air-water"))
        pipes += [
            _pipe("p1", "primo", ("generatore", "water_supply"), ("serbatoio", "primary_in")),
            _pipe("p2", "primo", ("serbatoio", "primary_out"), ("generatore", "water_return")),
        ]
    else:
        components += [
            ("nord", "heat-pump-air-water"),
            ("sud", "heat-pump-air-water"),
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
    )


def una_macchina_con_accumulo_combinato() -> ProjectModel:
    return _con_accumulo_combinato(1)


def due_macchine_con_accumulo_combinato() -> ProjectModel:
    return _con_accumulo_combinato(2)


CASI: list[Callable[[], ProjectModel]] = [
    una_macchina_in_anello,
    due_macchine_in_parallelo,
    una_macchina_con_accumulo_combinato,
    due_macchine_con_accumulo_combinato,
]


# ---------------------------------------------------------------------------
# Come si cammina il grafo completato
# ---------------------------------------------------------------------------


class Walk:
    """Il modello completato letto lungo le tubazioni del percorso."""

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
        self.medium_of = {item.id: item.medium for item in model.networks}
        self.network_of = {item.id: item.network_id for item in model.connections}
        self.rules_by_id = {item.id: item for item in rules().all()}

    def functions(self, component_id: str) -> frozenset[str]:
        return frozenset(self.definitions[component_id].functions)

    def closes(self, component_id: str) -> bool:
        return bool(self.functions(component_id) & CLOSING_FUNCTIONS)

    def maintainable(self, component_id: str) -> bool:
        return self.definitions[component_id].has_trait(ComponentTrait.MAINTAINABLE)

    def run_ports(self, component_id: str) -> list[str]:
        return sorted(
            port_id
            for (owner, port_id) in self.at_port
            if owner == component_id and (owner, port_id) not in self.off_the_run
        )

    def rule_of(self, component_id: str) -> RuleDefinition | None:
        for item in self.model.components:
            if item.id != component_id:
                continue
            for evidence in item.evidence:
                if evidence.kind == "rule":
                    return self.rules_by_id.get(evidence.reference.split("@", 1)[0])
        return None

    def own_accessories(self, component_id: str) -> frozenset[str]:
        """Gli accessori che una regola **per componente** ha posato sugli
        attacchi di questo pezzo: sono suoi, e formano con lui il gruppo.

        Si riconoscono dai dati: l'identificativo derivato dall'attacco su cui
        la regola li ha posati, e la regola che li ha voluti, che li conta una
        volta per pezzo e non una per rete."""
        own: set[str] = set()
        for other in self.model.components:
            rule = self.rule_of(other.id)
            if rule is None or rule.cardinality is RuleCardinality.PER_NETWORK:
                continue
            if rule.then.placement.on_a_common_run:
                continue
            for port in self.definitions[component_id].ports:
                anchor = PortRef(component_id=component_id, port_id=port.id)
                if proposed_component_id(other.definition_id, anchor) == other.id:
                    own.add(other.id)
        return frozenset(own)

    def same_group(self, first: str, second: str) -> bool:
        return second in self.own_accessories(first) or first in self.own_accessories(second)

    def stretch_from(self, component_id: str, port_id: str) -> list[str]:
        """I pezzi incontrati dall'attacco in poi, fino al primo che ferma.

        Ferma un pezzo che non sta in linea, un pezzo manutenibile, o un
        raccordo da cui il percorso prosegue in piu' di una direzione. Il
        pezzo che ferma e' l'ultimo dell'elenco."""
        found: list[str] = []
        cursor = component_id
        connection = self.at_port.get((component_id, port_id))
        seen = {component_id}
        while connection is not None:
            peer = next(
                ref.component_id
                for ref in (connection.endpoint_a, connection.endpoint_b)
                if ref.component_id != cursor
            )
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

    def stops(self, component_id: str) -> bool:
        """Chi ferma una camminata: un nodo, un pezzo manutenibile, un raccordo
        da cui il percorso prosegue in piu' direzioni."""
        return (
            component_id not in self.inline
            or self.maintainable(component_id)
            or len(self.run_pipes_of.get(component_id, [])) > 2
        )

    def holder_of(self, hung: str, from_port: str | None = None) -> str:
        """Il pezzo del percorso da cui pende un accessorio: si risale lo
        stacco attraverso gli organi in fila fino a chi regge il braccio.

        `from_port` sceglie da quale attacco risalire, per chi ne ha piu' d'uno
        su stacchi diversi: il gruppo di riempimento e' un ponte, e i suoi due
        capi pendono da due tubazioni diverse (DRAW-006-R1, blocco D).
        """
        current = hung
        arrived_from: str | None = None
        while True:
            ports = [
                port.id
                for port in self.definitions[current].ports
                if (current, port.id) in self.at_port
                and self.at_port[(current, port.id)].id != arrived_from
                and (from_port is None or current != hung or port.id == from_port)
            ]
            connection = self.at_port[(current, ports[0])]
            peer = next(
                ref.component_id
                for ref in (connection.endpoint_a, connection.endpoint_b)
                if ref.component_id != current
            )
            if self.definitions[peer].is_a_fitting or peer not in self.inline:
                return peer
            current, arrived_from = peer, connection.id

    def machines_needing_a_filter(self) -> list[str]:
        return sorted(
            component_id
            for component_id, definition in self.definitions.items()
            if "heat_generation" in definition.functions
            and definition.has_trait(ComponentTrait.NEEDS_DEBRIS_PROTECTION)
        )

    def port_with_flow(self, component_id: str, flow: PortFlow) -> str:
        return next(
            port.id
            for port in self.definitions[component_id].ports
            if port.flow is flow and not port.off_the_run
        )


@cache
def _done(index: int) -> ProjectModel:
    done, _, gaps = saturate(CASI[index](), catalog(), rules())
    gaps = _senza_la_domanda_sull_acqua_di_riempimento(gaps)
    assert not gaps, [(gap.rule_id, gap.reason.value) for gap in gaps]
    return done


def _walk(index: int) -> Walk:
    return Walk(_done(index))


# ---------------------------------------------------------------------------
# A1 — il gruppo macchina + filtro si isola dall'esterno, mai fra i membri
# ---------------------------------------------------------------------------


def _senza_la_domanda_sull_acqua_di_riempimento(gaps: list[RuleGap]) -> list[RuleGap]:
    """I punti aperti diversi dalla domanda sulla sorgente di acqua fredda.

    Questi impianti di prova non dichiarano un acquedotto — non e' cio' che
    misurano — e da DRAW-006-R1 il gruppo di riempimento e' un **ponte fra due
    reti**: senza una sorgente fredda gia' approvata la regola chiede al
    progettista invece di appendere un pezzo al nulla. E' un punto aperto vero,
    e non riguarda la proprieta' provata qui.
    """
    return [item for item in gaps if item.reason is not GapReason.NO_SOURCE_NETWORK]


@pytest.mark.parametrize("index", range(len(CASI)))
def test_il_filtro_sta_contro_la_macchina_senza_valvola_in_mezzo(index: int) -> None:
    """Fra il filtro a Y sul ritorno e la propria macchina non c'e' niente di
    chiudibile: il primo pezzo che il ritorno incontra uscendo dalla macchina
    e' il filtro stesso."""
    walk = _walk(index)
    machines = walk.machines_needing_a_filter()
    assert machines, "nessuna macchina chiede un filtro: la prova non direbbe nulla"
    for machine in machines:
        inlet = walk.port_with_flow(machine, PortFlow.IN)
        pieces = walk.stretch_from(machine, inlet)
        assert pieces, (machine, inlet)
        assert "filtration" in walk.functions(pieces[0]), (machine, pieces)
        assert pieces[0] in walk.own_accessories(machine), (machine, pieces[0])


@pytest.mark.parametrize("index", range(len(CASI)))
def test_sul_ritorno_basta_una_valvola_lato_rete_oltre_il_filtro(index: int) -> None:
    """Oltre il filtro, verso la rete, un solo organo di chiusura prima del
    prossimo pezzo che ferma la camminata: una ripartizione, un altro pezzo
    manutenibile, un nodo."""
    walk = _walk(index)
    for machine in walk.machines_needing_a_filter():
        inlet = walk.port_with_flow(machine, PortFlow.IN)
        strainer = walk.stretch_from(machine, inlet)[0]
        away = next(
            port_id
            for port_id in walk.run_ports(strainer)
            if machine not in walk.stretch_from(strainer, port_id)[:1]
        )
        beyond = walk.stretch_from(strainer, away)
        closers = [item for item in beyond if walk.closes(item)]
        assert len(closers) == 1, (machine, beyond)
        assert walk.stops(beyond[-1]), beyond


@pytest.mark.parametrize("index", range(len(CASI)))
def test_la_mandata_della_macchina_ha_la_propria_intercettazione(index: int) -> None:
    """L'altro ramo del gruppo: la mandata esce dalla macchina e incontra un
    organo di chiusura, uno solo, prima del primo pezzo che ferma."""
    walk = _walk(index)
    for machine in walk.machines_needing_a_filter():
        outlet = walk.port_with_flow(machine, PortFlow.OUT)
        pieces = walk.stretch_from(machine, outlet)
        closers = [item for item in pieces if walk.closes(item)]
        assert len(closers) == 1, (machine, pieces)


@pytest.mark.parametrize("index", range(len(CASI)))
def test_nessun_organo_di_chiusura_ne_ha_un_altro_di_seguito(index: int) -> None:
    """«Senza duplicare organi consecutivi che chiudono lo stesso volume»:
    da un organo di chiusura, camminando da tutti e due i lati fino al primo
    pezzo che ferma, non se ne incontra un altro."""
    walk = _walk(index)
    closers = sorted(item for item in walk.definitions if walk.closes(item))
    assert closers
    for closer in closers:
        for port_id in walk.run_ports(closer):
            stretch = walk.stretch_from(closer, port_id)
            doubled = [item for item in stretch if walk.closes(item)]
            assert not doubled, (closer, port_id, stretch)


@pytest.mark.parametrize("index", range(len(CASI)))
def test_ogni_gruppo_manutenibile_si_isola_su_ogni_attacco_verso_l_esterno(index: int) -> None:
    """La proprieta' che sostituisce «una valvola per ogni porta»: da ogni
    attacco di ogni pezzo manutenibile si incontra un organo di chiusura
    prima di uscire dal gruppo, oppure si arriva a un membro dello stesso
    gruppo, che l'organo lo condivide.

    Chi l'organo lo **dichiara dentro il proprio mantello** e' isolato lo
    stesso, e non lo si vede sulla tubazione perche' non c'e' niente da
    disegnare: il gruppo di riempimento pubblicato incorpora la propria
    intercettazione (DRAW-006, blocco B), e pretendergliene una esterna
    sarebbe pretendere il pezzo ridondante che il PM ha tolto."""
    walk = _walk(index)
    serviceable = sorted(
        item
        for item in walk.definitions
        if walk.maintainable(item)
        and not CLOSING_FUNCTIONS & set(walk.definitions[item].carries_on_board)
    )
    assert serviceable
    uncovered: list[str] = []
    for component_id in serviceable:
        for port_id in walk.run_ports(component_id):
            stretch = walk.stretch_from(component_id, port_id)
            if any(walk.closes(item) for item in stretch):
                continue
            if stretch and walk.same_group(component_id, stretch[-1]):
                continue
            uncovered.append(f"{component_id}.{port_id} -> {stretch}")
    assert not uncovered, uncovered


@pytest.mark.parametrize("index", range(len(CASI)))
def test_fra_due_pezzi_manutenibili_estranei_c_e_una_valvola_sola(index: int) -> None:
    """Due pezzi manutenibili che non sono un gruppo — l'accumulo e il
    circolatore che ne parte — si separano con un organo, non due: uno solo
    basta a chiudere il volume fra i due, e il secondo chiuderebbe lo stesso."""
    walk = _walk(index)
    seen: set[frozenset[str]] = set()
    for component_id in sorted(item for item in walk.definitions if walk.maintainable(item)):
        for port_id in walk.run_ports(component_id):
            stretch = walk.stretch_from(component_id, port_id)
            if not stretch or not walk.maintainable(stretch[-1]):
                continue
            pair = frozenset({component_id, stretch[-1]})
            if pair in seen or walk.same_group(component_id, stretch[-1]):
                continue
            seen.add(pair)
            closers = [item for item in stretch[:-1] if walk.closes(item)]
            assert len(closers) == 1, (component_id, port_id, stretch)
    assert seen, "nessuna coppia di pezzi manutenibili estranei: la prova non direbbe nulla"


def test_le_sigle_e_le_permutazioni_non_muovono_una_valvola() -> None:
    """Lo stesso impianto scritto in un altro ordine da' lo stesso grafo: la
    regola del gruppo non puo' dipendere dall'ordine del file."""
    import random

    base = due_macchine_con_accumulo_combinato()
    done, _, _ = saturate(base, catalog(), rules())
    reference = canonical_json(done)
    for seed in (5, 23, 71):
        shuffled = random.Random(seed)
        permuted = base.model_copy(
            update={
                "connections": shuffled.sample(list(base.connections), len(base.connections)),
                "components": shuffled.sample(list(base.components), len(base.components)),
                "networks": shuffled.sample(list(base.networks), len(base.networks)),
            }
        )
        again, _, _ = saturate(permuted, catalog(), rules())
        assert {item.id for item in again.components} == {item.id for item in done.components}, seed
        assert {
            (c.endpoint_a.component_id, c.endpoint_a.port_id, c.endpoint_b.component_id, c.endpoint_b.port_id)
            for c in again.connections
        } == {
            (c.endpoint_a.component_id, c.endpoint_a.port_id, c.endpoint_b.component_id, c.endpoint_b.port_id)
            for c in done.connections
        }, seed
    assert canonical_json(done) == reference


# ---------------------------------------------------------------------------
# A2 — un solo gruppo di riempimento, sulla rete tecnica
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("index", (2, 3))
def test_il_riempimento_e_uno_solo_e_sta_sul_ritorno_dell_acqua_tecnica(index: int) -> None:
    walk = _walk(index)
    fillers = sorted(item for item in walk.definitions if "filling" in walk.functions(item))
    assert len(fillers) == 1, fillers
    filler = fillers[0]
    # Il gruppo e' un **ponte** (DRAW-006-R1, blocco D): l'attacco che guarda
    # il circuito tecnico e' quello sull'acqua di riscaldamento, e l'altro
    # pesca dall'acqua fredda. Si cerca per fluido, non per posizione.
    into = next(
        port.id
        for port in walk.definitions[filler].ports
        if port.medium == HEATING
    )
    stub = walk.at_port[(filler, into)]
    assert walk.medium_of[walk.network_of[stub.id]] == HEATING
    # Sta sul ritorno comune: partendo dall'uscita primaria dell'accumulo la
    # camminata incontra il raccordo che lo regge prima di fermarsi.
    tank = next(
        item for item in walk.definitions if walk.definitions[item].stored_medium == HEATING
        and {"cold_in", "dhw_out"} <= walk.definitions[item].port_ids
    )
    holder = walk.holder_of(filler, into)
    out_port = next(
        port.id
        for port in walk.definitions[tank].ports
        if port.medium == HEATING and port.flow is PortFlow.OUT and not port.off_the_run
        and port.id.startswith("primary")
    )
    assert holder in walk.stretch_from(tank, out_port), (holder, walk.stretch_from(tank, out_port))


@pytest.mark.parametrize("index", (2, 3))
def test_nessun_riempimento_sull_acqua_calda_sanitaria(index: int) -> None:
    """Il ponte pesca dalla fredda e sbocca sul tecnico, mai sulla sanitaria.

    Prima la prova escludeva anche l'acqua fredda, ed era giusto finche' il
    gruppo aveva un attacco solo: adesso e' un ponte, e l'acqua fredda e'
    proprio da dove pesca (DRAW-006-R1, blocco D). Cio' che resta escluso e'
    l'acqua calda sanitaria, che non riempie nessun circuito chiuso.
    """
    walk = _walk(index)
    for item in walk.definitions:
        if "filling" not in walk.functions(item):
            continue
        media = set()
        for port in walk.definitions[item].ports:
            connection = walk.at_port.get((item, port.id))
            if connection is None:
                continue
            media.add(walk.medium_of[walk.network_of[connection.id]])
        assert DHW not in media, item
        assert media == {COLD, HEATING}, (item, sorted(media))


# ---------------------------------------------------------------------------
# A3 — l'accumulo combinato: acqua fredda a `cold_in`, sanitaria da `dhw_out`
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("index", (2, 3))
def test_l_acqua_fredda_entra_nel_serpentino_e_la_calda_ne_esce_verso_le_utenze(index: int) -> None:
    walk = _walk(index)
    tank = next(
        item for item in walk.definitions if walk.definitions[item].stored_medium == HEATING
        and {"cold_in", "dhw_out"} <= walk.definitions[item].port_ids
    )
    cold_stretch = walk.stretch_from(tank, "cold_in")
    assert "boundary" in walk.functions(cold_stretch[-1]), cold_stretch
    assert walk.medium_of[walk.network_of[walk.at_port[(tank, "cold_in")].id]] == COLD
    assert all(item in walk.inline for item in cold_stretch[:-1]), cold_stretch
    hot_stretch = walk.stretch_from(tank, "dhw_out")
    assert walk.medium_of[walk.network_of[walk.at_port[(tank, "dhw_out")].id]] == DHW
    reached = hot_stretch
    # Il miscelatore e' manutenibile e ferma la camminata: oltre lui si prosegue.
    while reached and reached[-1] in walk.inline and "boundary" not in walk.functions(reached[-1]):
        last = reached[-1]
        away = next(
            port_id for port_id in walk.run_ports(last)
            if walk.stretch_from(last, port_id)[:1] != [reached[-2] if len(reached) > 1 else tank]
        )
        reached = reached + walk.stretch_from(last, away)
    assert "boundary" in walk.functions(reached[-1]), reached
    # Il volume tecnico alimenta primario e secondario, e sono reti di
    # riscaldamento diverse da quelle sanitarie.
    for port_id in ("primary_in", "primary_out", "secondary_in", "secondary_out"):
        medium = walk.medium_of[walk.network_of[walk.at_port[(tank, port_id)].id]]
        assert medium == HEATING, port_id
    assert walk.network_of[walk.at_port[(tank, "primary_in")].id] != walk.network_of[
        walk.at_port[(tank, "secondary_out")].id
    ]


def test_le_connessioni_sanitarie_della_tavola_1_sono_preservate_non_duplicate() -> None:
    """Sul modello dell'impianto 1 completato: una sola tubazione entra in
    `cold_in` dalla rete fredda, una sola esce da `dhw_out` verso le utenze."""
    done, _, _ = saturate(load_project(PROVA_1), catalog(), rules())
    walk = Walk(done)
    tanks = [
        item for item in walk.definitions if walk.definitions[item].stored_medium == HEATING
        and {"cold_in", "dhw_out"} <= walk.definitions[item].port_ids
    ]
    assert len(tanks) == 1
    tank = tanks[0]
    cold = [c for c in done.connections if PortRef(component_id=tank, port_id="cold_in") in (c.endpoint_a, c.endpoint_b)]
    hot = [c for c in done.connections if PortRef(component_id=tank, port_id="dhw_out") in (c.endpoint_a, c.endpoint_b)]
    assert len(cold) == 1 and len(hot) == 1
    assert walk.medium_of[cold[0].network_id] == COLD
    assert walk.medium_of[hot[0].network_id] == DHW
    boundaries = [item for item in walk.definitions if "boundary" in walk.functions(item)]
    assert len(boundaries) == 2


# ---------------------------------------------------------------------------
# A4 — puffer, bollitore e accumulo combinato sono tre definizioni diverse
# ---------------------------------------------------------------------------


def _reserves() -> dict[str, list[ComponentDefinition]]:
    """Le riserve del catalogo, classificate dai soli fluidi che dichiarano."""
    kinds: dict[str, list[ComponentDefinition]] = {"puffer": [], "bollitore": [], "combinato": []}
    for definition in catalog().all():
        if not definition.has_trait(ComponentTrait.HOLDS_ITS_OWN_VOLUME):
            continue
        flow_media = {port.medium for port in definition.ports if not port.off_the_run}
        if definition.stored_medium == HEATING and flow_media == {HEATING}:
            kinds["puffer"].append(definition)
        elif definition.stored_medium == DHW and HEATING in flow_media:
            kinds["bollitore"].append(definition)
        elif definition.stored_medium == HEATING and {COLD, DHW} <= flow_media:
            kinds["combinato"].append(definition)
    return kinds


def test_esistono_tutte_e_tre_le_riserve_e_non_condividono_il_simbolo() -> None:
    kinds = _reserves()
    for kind, found in kinds.items():
        assert found, f"nessuna riserva del tipo {kind} in catalogo"
    symbols = {kind: {item.symbol_id for item in found} for kind, found in kinds.items()}
    assert not (symbols["puffer"] & symbols["bollitore"])
    assert not (symbols["puffer"] & symbols["combinato"])
    assert not (symbols["bollitore"] & symbols["combinato"])


def test_le_porte_di_ogni_riserva_sono_coerenti_col_fluido_che_tiene_in_serbo() -> None:
    kinds = _reserves()
    for puffer in kinds["puffer"]:
        assert puffer.fills_from is None
        assert all(port.medium == HEATING for port in puffer.ports)
    for cylinder in kinds["bollitore"]:
        assert cylinder.fills_from is not None
        fill = next(port for port in cylinder.ports if port.id == cylinder.fills_from)
        assert fill.medium == COLD and fill.flow is PortFlow.IN
        coil = [port for port in cylinder.ports if port.medium == HEATING and not port.off_the_run]
        assert {port.flow for port in coil} == {PortFlow.IN, PortFlow.OUT}
        assert any(port.medium == DHW and port.flow is PortFlow.OUT for port in cylinder.ports)
    for combined in kinds["combinato"]:
        assert combined.fills_from is None, "il volume tecnico si riempie dal circuito"
        cold = [port for port in combined.ports if port.medium == COLD]
        hot = [port for port in combined.ports if port.medium == DHW]
        assert [port.flow for port in cold] == [PortFlow.IN]
        assert [port.flow for port in hot] == [PortFlow.OUT]
        technical = [port for port in combined.ports if port.medium == HEATING and not port.off_the_run]
        assert len(technical) == 4
        assert [port.flow for port in technical].count(PortFlow.IN) == 2


def test_una_riserva_tecnica_riceve_sicurezza_e_sfogo_sulla_rete_tecnica_e_non_il_corredo_sanitario() -> None:
    """Il combinato tocca l'acqua fredda senza riempirsene: niente ritegno,
    vaso o sicurezza sanitari; il bollitore invece li riceve."""
    walk = _walk(2)
    tank = next(
        item for item in walk.definitions if walk.definitions[item].stored_medium == HEATING
        and {"cold_in", "dhw_out"} <= walk.definitions[item].port_ids
    )
    cold_pieces = walk.stretch_from(tank, "cold_in")
    assert not any(walk.functions(item) & {"non_return", "expansion", "safety"} for item in cold_pieces), cold_pieces
