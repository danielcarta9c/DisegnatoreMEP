"""Le prove del grafo di DRAW-005-R1, blocco A, scritte prima del codice.

Il PM traduce i rilievi PO I-043 (`docs/pm/2026-09-08-rilievi-po-draw005-r1.md`):

1. nessuna regola presume che una pompa di calore generica porti la sicurezza a
   bordo: la presenza a bordo e' un dato **esplicito** del catalogo della macchina;
2. ogni generatore che non la dichiara riceve una sicurezza esterna **sulla
   mandata**, il piu' vicino possibile alla macchina e **prima di qualunque organo
   di intercettazione**;
3. se la sicurezza e' dichiarata a bordo, nessun doppione esterno;
4. la sicurezza della riserva resta quella della riserva: non sostituisce quelle
   dei generatori e non ne viene sostituita;
5. lo sfogo aria non e' la sicurezza: resta sull'attacco alto della riserva, e non
   se ne aggiunge uno per generatore.

Le prove sono generali: gli impianti sono costruiti qui, su una e due macchine, con
e senza sicurezza integrata. La macchina «con sicurezza a bordo» e' la stessa voce
di catalogo della generica con un solo dato in piu' — cio' che dichiara di portare
dentro il mantello — cosi' che l'esito dipenda da quel dato e da nient'altro. Nessun
identificativo o coordinata della tavola 1 entra nelle attese.
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
from disegnatore_mep.rules.proposal import proposed_component_id
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
"""La stessa macchina della generica, che dichiara in piu' la sicurezza a bordo.

Vive solo in queste prove: non e' una voce del catalogo pubblicato, e' il modo di
provare che l'esito dipende dal **dato dichiarato** e non dal nome del pezzo."""


@cache
def catalog() -> ComponentRegistry:
    symbols = SymbolRegistry.from_directory(SYMBOLS)
    base = ComponentRegistry.from_directory(CATALOG, symbols=symbols)
    generic = base.get(GENERIC)
    assert SAFETY not in generic.carries_on_board, (
        "la macchina generica del catalogo non deve dichiarare la sicurezza a bordo: "
        "e' l'assunzione che il pacchetto toglie"
    )
    variant = generic.model_copy(
        update={
            "id": WITH_SAFETY,
            "name": f"{generic.name} con sicurezza a bordo",
            "carries_on_board": [*generic.carries_on_board, SAFETY],
        }
    )
    return ComponentRegistry([*base.all(), variant], symbols=symbols)


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
            project_id="prova-sicurezza",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 8),
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
# Gli impianti di prova: una e due macchine, con la macchina scelta dalla prova
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


CASI: list[Callable[[str], ProjectModel]] = [
    una_macchina_in_anello,
    due_macchine_in_parallelo,
    una_macchina_con_accumulo_combinato,
    due_macchine_con_accumulo_combinato,
]
MACCHINE = (GENERIC, WITH_SAFETY)


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
        """I pezzi del tratto che parte da quell'attacco, fino al primo organo di
        chiusura escluso: e' il volume che resta attaccato al pezzo quando lo
        si isola."""
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

    def safeties_on_the_outlet(self, generator: str) -> tuple[list[str], list[str]]:
        """Le sicurezze che pendono dal volume della mandata di un generatore —
        prima del primo organo di chiusura — e i pezzi di quel volume."""
        outlet = self.port_with_flow(generator, PortFlow.OUT)
        before_closer = self.before_the_first_closer(generator, outlet)
        return self.hung_before_the_first_closer(generator, outlet, SAFETY), before_closer


def _done(build: Callable[[str], ProjectModel], machine: str) -> ProjectModel:
    done, _, gaps = saturate(build(machine), catalog(), rules())
    assert not gaps, [(gap.rule_id, gap.reason.value) for gap in gaps]
    return done


def _walk(build: Callable[[str], ProjectModel], machine: str) -> Walk:
    return Walk(_done(build, machine))


CASI_IDS = [item.__name__ for item in CASI]


# ---------------------------------------------------------------------------
# A1 — la macchina generica non porta la sicurezza a bordo: la riceve, esterna
# ---------------------------------------------------------------------------


def test_la_macchina_generica_dichiara_a_bordo_solo_cio_che_il_catalogo_scrive() -> None:
    """Il bordo macchina e' un dato del catalogo, macchina per macchina: la
    generica dichiara il circolatore e nient'altro, e nessuna regola le
    attribuisce una sicurezza che non ha scritto."""
    generic = catalog().get(GENERIC)
    assert SAFETY not in generic.carries_on_board
    assert AIR_RELEASE not in generic.carries_on_board
    variant = catalog().get(WITH_SAFETY)
    assert SAFETY in variant.carries_on_board
    assert variant.functions == generic.functions
    assert variant.trait_set == generic.trait_set


@pytest.mark.parametrize("build", CASI, ids=CASI_IDS)
def test_ogni_generatore_senza_sicurezza_a_bordo_ne_riceve_una_sulla_mandata(
    build: Callable[[str], ProjectModel],
) -> None:
    """Una sicurezza per generatore, sulla tubazione che esce, e nessun'altra."""
    walk = _walk(build, GENERIC)
    generators = walk.generators()
    assert generators
    for generator in generators:
        hung, _ = walk.safeties_on_the_outlet(generator)
        assert len(hung) == 1, (generator, hung)
        assert walk.anchored_to(generator, SAFETY) == hung, generator
        # E sul ritorno niente: la sicurezza sta dove il calore esce.
        inlet = walk.port_with_flow(generator, PortFlow.IN)
        on_the_inlet = walk.hung_before_the_first_closer(generator, inlet, SAFETY)
        assert not on_the_inlet, (generator, on_the_inlet)


@pytest.mark.parametrize("build", CASI, ids=CASI_IDS)
def test_la_sicurezza_del_generatore_sta_prima_di_ogni_intercettazione_e_attaccata_alla_macchina(
    build: Callable[[str], ProjectModel],
) -> None:
    """Fra la macchina e la sua sicurezza non c'e' nessun pezzo; fra la
    sicurezza e la rete c'e' l'organo di chiusura, dopo."""
    walk = _walk(build, GENERIC)
    for generator in walk.generators():
        outlet = walk.port_with_flow(generator, PortFlow.OUT)
        stretch = walk.stretch_from(generator, outlet)
        hung, before_closer = walk.safeties_on_the_outlet(generator)
        holder = next(
            piece for piece in stretch if any(item in hung for item in walk.hanging_from(piece))
        )
        # Il primo pezzo che la mandata incontra e' cio' che regge la sicurezza.
        assert stretch[0] == holder, (generator, stretch)
        assert holder in before_closer, (generator, stretch, before_closer)
        closers = [item for item in stretch if walk.closes(item)]
        assert len(closers) == 1, (generator, stretch)
        assert stretch.index(holder) < stretch.index(closers[0]), (generator, stretch)
        # Nulla di chiudibile sullo stacco della sicurezza.
        assert not any(walk.closes(item) for item in walk.hanging_from(holder)), holder


# ---------------------------------------------------------------------------
# A2 — con la sicurezza a bordo, nessun doppione esterno
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("build", CASI, ids=CASI_IDS)
def test_con_la_sicurezza_a_bordo_nessuna_sicurezza_esterna_sul_generatore(
    build: Callable[[str], ProjectModel],
) -> None:
    walk = _walk(build, WITH_SAFETY)
    for generator in walk.generators():
        hung, _ = walk.safeties_on_the_outlet(generator)
        assert not hung, (generator, hung)
        assert not walk.anchored_to(generator, SAFETY), generator


@pytest.mark.parametrize("build", CASI, ids=CASI_IDS)
def test_il_bordo_macchina_e_l_unica_differenza_fra_i_due_esiti(
    build: Callable[[str], ProjectModel],
) -> None:
    """Stesse funzioni, stesse proprieta', un dato dichiarato in piu': i due
    grafi differiscono soltanto per le sicurezze dei generatori e per cio' che
    le regge."""
    generic = _walk(build, GENERIC)
    on_board = _walk(build, WITH_SAFETY)
    only_generic = set(generic.definitions) - set(on_board.definitions)
    only_on_board = set(on_board.definitions) - set(generic.definitions)
    assert not only_on_board, only_on_board
    expected = {
        item
        for generator in generic.generators()
        for item in generic.anchored_to(generator, SAFETY)
    }
    holders = {
        piece
        for generator in generic.generators()
        for piece in generic.stretch_from(generator, generic.port_with_flow(generator, PortFlow.OUT))
        if any(item in expected for item in generic.hanging_from(piece))
    }
    assert only_generic == expected | holders, (only_generic, expected, holders)


# ---------------------------------------------------------------------------
# A3 — la riserva tiene la propria sicurezza, una, e non la scambia con quelle
# dei generatori
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("build", CASI[1:], ids=CASI_IDS[1:])
@pytest.mark.parametrize("machine", MACCHINE)
def test_la_riserva_ha_una_sicurezza_sola_sull_ingresso_qualunque_cosa_facciano_i_generatori(
    build: Callable[[str], ProjectModel], machine: str
) -> None:
    walk = _walk(build, machine)
    reserves = [item for item in walk.reserves() if walk.definitions[item].stored_medium == HEATING]
    assert reserves
    for reserve in reserves:
        own = walk.anchored_to(reserve, SAFETY)
        assert len(own) == 1, (reserve, own)
        inlet = walk.port_with_flow(reserve, PortFlow.IN)
        stretch = walk.stretch_from(reserve, inlet)
        hung = walk.hung_before_the_first_closer(reserve, inlet, SAFETY)
        assert hung == own, (reserve, stretch, hung, own)
        # E il primo pezzo del tratto e' cio' che la regge: nulla di chiudibile
        # fra la riserva e la propria sicurezza.
        holder = next(
            piece for piece in stretch if any(item in own for item in walk.hanging_from(piece))
        )
        assert stretch[0] == holder, (reserve, stretch)


@pytest.mark.parametrize("machine", MACCHINE)
def test_le_sicurezze_dei_generatori_e_della_riserva_sono_pezzi_distinti(machine: str) -> None:
    walk = _walk(due_macchine_con_accumulo_combinato, machine)
    per_generator = {
        generator: walk.anchored_to(generator, SAFETY) for generator in walk.generators()
    }
    per_reserve = {reserve: walk.anchored_to(reserve, SAFETY) for reserve in walk.reserves()}
    everything = [item for items in (*per_generator.values(), *per_reserve.values()) for item in items]
    assert len(everything) == len(set(everything))
    assert set(walk.with_function(SAFETY)) == set(everything), (
        walk.with_function(SAFETY),
        everything,
    )
    expected_per_generator = 0 if machine == WITH_SAFETY else 1
    assert all(len(items) == expected_per_generator for items in per_generator.values())


# ---------------------------------------------------------------------------
# A4 — lo sfogo aria e' un'altra funzione: sull'attacco alto della riserva,
# nessuno per generatore
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("build", CASI[1:], ids=CASI_IDS[1:])
@pytest.mark.parametrize("machine", MACCHINE)
def test_lo_sfogo_aria_resta_sull_attacco_dedicato_della_riserva(
    build: Callable[[str], ProjectModel], machine: str
) -> None:
    walk = _walk(build, machine)
    vents = walk.with_function(AIR_RELEASE)
    reserves = [item for item in walk.reserves() if walk.definitions[item].stored_medium == HEATING]
    assert len(vents) == len(reserves), (vents, reserves)
    for reserve in reserves:
        port = next(
            item.id for item in walk.definitions[reserve].ports if item.serves == AIR_RELEASE
        )
        connection = walk.at_port.get((reserve, port))
        assert connection is not None, (reserve, port)
        hung = walk._peer(connection, reserve)
        assert AIR_RELEASE in walk.functions(hung), (reserve, hung)
        assert SAFETY not in walk.functions(hung)
    for generator in walk.generators():
        assert not walk.anchored_to(generator, AIR_RELEASE), generator


@pytest.mark.parametrize("build", CASI, ids=CASI_IDS)
def test_sfogo_e_sicurezza_non_condividono_mai_il_pezzo(
    build: Callable[[str], ProjectModel],
) -> None:
    walk = _walk(build, GENERIC)
    for item in walk.with_function(SAFETY):
        assert AIR_RELEASE not in walk.functions(item), item
    for item in walk.with_function(AIR_RELEASE):
        assert SAFETY not in walk.functions(item), item


# ---------------------------------------------------------------------------
# A5 — la catena e' stabile e non dipende dal regime ne' dall'ordine del file
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("build", CASI, ids=CASI_IDS)
@pytest.mark.parametrize("machine", MACCHINE)
def test_rieseguire_le_regole_sul_modello_completato_non_propone_niente(
    build: Callable[[str], ProjectModel], machine: str
) -> None:
    done = _done(build, machine)
    again = evaluate_in_phases(done, catalog(), rules())
    assert again.is_empty, [(item.rule_id, item.component_id) for item in again.proposals]
    twice, added, _ = saturate(done, catalog(), rules())
    assert not added
    assert [item.id for item in twice.components] == [item.id for item in done.components]


@pytest.mark.parametrize("regime", (PlantRegime.UP_TO_35_KW, PlantRegime.OVER_35_KW, None))
def test_la_sicurezza_del_generatore_vale_in_ogni_regime(regime: PlantRegime | None) -> None:
    """Il regime cambia il corredo di rete, non la protezione del generatore."""
    done, _, gaps = saturate(
        _con_accumulo_combinato(GENERIC, 2, regime), catalog(), rules()
    )
    assert not gaps
    walk = Walk(done)
    for generator in walk.generators():
        hung, _ = walk.safeties_on_the_outlet(generator)
        assert len(hung) == 1, (regime, generator, hung)


def test_permutare_componenti_e_connessioni_non_sposta_una_sicurezza() -> None:
    project = due_macchine_con_accumulo_combinato(GENERIC)
    permuted = project.model_copy(
        update={
            "components": list(reversed(project.components)),
            "connections": list(reversed(project.connections)),
        }
    )
    first = Walk(saturate(project, catalog(), rules())[0])
    second = Walk(saturate(permuted, catalog(), rules())[0])
    for walk in (first, second):
        for generator in walk.generators():
            assert len(walk.safeties_on_the_outlet(generator)[0]) == 1
    assert {
        (owner, tuple(first.anchored_to(owner, SAFETY)))
        for owner in (*first.generators(), *first.reserves())
    } == {
        (owner, tuple(second.anchored_to(owner, SAFETY)))
        for owner in (*second.generators(), *second.reserves())
    }


# ---------------------------------------------------------------------------
# A6 — la tavola 1, letta con le stesse camminate
# ---------------------------------------------------------------------------


def test_la_tavola_1_protegge_ciascuna_macchina_isolabile_prima_della_sua_intercettazione() -> None:
    """Il catalogo generico dichiara solo il circolatore: due sicurezze esterne,
    una per macchina, ciascuna prima della propria valvola di mandata; quella
    della riserva resta e non le sostituisce."""
    done, _, gaps = saturate(load_project(PROVA_1), catalog(), rules())
    assert not gaps
    walk = Walk(done)
    generators = walk.generators()
    assert len(generators) == 2
    for generator in generators:
        hung, before_closer = walk.safeties_on_the_outlet(generator)
        assert len(hung) == 1, (generator, hung)
        outlet = walk.port_with_flow(generator, PortFlow.OUT)
        stretch = walk.stretch_from(generator, outlet)
        assert before_closer and stretch[0] == before_closer[0]
    reserves = [item for item in walk.reserves() if walk.definitions[item].stored_medium == HEATING]
    assert len(reserves) == 1
    assert len(walk.anchored_to(reserves[0], SAFETY)) == 1
    assert len(walk.with_function(SAFETY)) == 3
    assert len(walk.with_function(AIR_RELEASE)) == 1
