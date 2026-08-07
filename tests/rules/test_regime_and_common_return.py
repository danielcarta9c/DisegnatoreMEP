"""Il pacchetto E: il regime della centrale e il tratto comune (D-106).

Tre meccanismi nuovi, e le proprieta' che devono valere su qualunque impianto:

- il **regime** e' un dato dichiarato dal progettista, mai calcolato: le regole
  dell'altro regime non parlano, e senza dichiarazione vale il corredo minimo;
- il **ritorno generale** si trova sulla struttura — il tratto che tutte le
  camminate dai generatori condividono — e non dipende dall'ordine del file;
- cio' che una macchina **porta a bordo** lo dichiara il suo catalogo, e una
  regola non aggiunge cio' che la macchina dichiara di avere.
"""

import random
from pathlib import Path

import pytest
from pydantic import ValidationError

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.canonical import canonical_json
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import PlantRegime
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.engine import evaluate
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"
PROVA = ROOT / "examples" / "prova"

LARGE_ONLY = {
    "safety-relief-where-heat-enters-the-water",
    "flow-temperature-where-heat-enters-the-water",
    "air-release-where-the-water-is-hottest",
}
SMALL_ONLY = {
    "air-vent-on-the-stored-volume",
    "safety-relief-on-the-stored-volume",
}


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def rules() -> RuleRegistry:
    return RuleRegistry.from_directory(RULES)


def with_regime(model: ProjectModel, regime: PlantRegime | None) -> ProjectModel:
    return model.model_copy(update={"plant_regime": regime})


# ---------------------------------------------------------------------------
# Il regime: dichiarato, mai calcolato
# ---------------------------------------------------------------------------


def test_without_a_declaration_the_minimal_kit_applies() -> None:
    """Il default di D-106: nessuna dichiarazione, corredo minimo.

    L'impianto 1 nomina due macchine da 12 kW, ma la somma non la fa la
    skill: senza dichiarazione parlano le regole del regime piccolo e
    tacciono quelle del grande."""
    model = with_regime(
        load_project(PROVA / "prova-1-due-pdc-accumulo-combinato.json"), None
    )
    assert model.plant_regime is None
    _, applied, _ = saturate(model, catalog(), rules())
    fired = {item.rule_id for item in applied}
    assert not fired & LARGE_ONLY
    assert fired >= SMALL_ONLY


def test_declaring_the_large_regime_swaps_the_kit() -> None:
    model = with_regime(
        load_project(PROVA / "prova-1-due-pdc-accumulo-combinato.json"),
        PlantRegime.OVER_35_KW,
    )
    _, applied, _ = saturate(model, catalog(), rules())
    fired = {item.rule_id for item in applied}
    assert fired >= LARGE_ONLY
    assert not fired & SMALL_ONLY


def test_the_two_regimes_never_speak_together() -> None:
    """I due regimi non si mescolano sullo stesso impianto (D-106)."""
    for regime in (None, PlantRegime.UP_TO_35_KW, PlantRegime.OVER_35_KW):
        model = with_regime(
            load_project(PROVA / "prova-2-pdc-deviatrice-acs.json"), regime
        )
        _, applied, _ = saturate(model, catalog(), rules())
        fired = {item.rule_id for item in applied}
        assert not (fired & LARGE_ONLY and fired & SMALL_ONLY)


# ---------------------------------------------------------------------------
# Il ritorno generale: strutturale, mai dall'ordine del file
# ---------------------------------------------------------------------------


def test_the_kit_lands_on_the_common_return_upstream_of_the_split() -> None:
    """Con due macchine in parallelo il corredo sta a monte della ripartizione.

    E' la correzione del PM: vaso, riempimento, manometro e defangatore non
    pendono piu' dal ramo della prima macchina."""
    model = load_project(PROVA / "prova-1-due-pdc-accumulo-combinato.json")
    _, applied, _ = saturate(model, catalog(), rules())
    kit = {
        item.rule_id: item.anchor
        for item in applied
        if item.rule_id
        in {
            "expansion-on-closed-circuit",
            "filling-unit-on-return",
            "gauge-where-the-plant-is-charged",
            "dirt-separation-before-what-it-would-ruin",
        }
    }
    assert set(kit) == {
        "expansion-on-closed-circuit",
        "filling-unit-on-return",
        "gauge-where-the-plant-is-charged",
        "dirt-separation-before-what-it-would-ruin",
    }
    for rule_id, anchor in kit.items():
        assert anchor.component_id == "collettore-ritorno", (rule_id, anchor)
        assert anchor.port_id == "a", (rule_id, anchor)


def test_the_completed_plant_does_not_depend_on_the_file_order() -> None:
    """Stesso impianto, connessioni e pezzi in ordine diverso: stesso grafo.

    E' la proprieta' che il collaudo C1 ha imposto, estesa al tratto comune:
    permutare l'ingresso non muove il corredo e non cambia una valvola."""
    base = load_project(PROVA / "prova-1-due-pdc-accumulo-combinato.json")
    done, _, _ = saturate(base, catalog(), rules())
    reference = canonical_json(done)
    for seed in (3, 17, 41):
        shuffled = random.Random(seed)
        permuted = base.model_copy(
            update={
                "connections": shuffled.sample(
                    list(base.connections), len(base.connections)
                ),
                "components": shuffled.sample(
                    list(base.components), len(base.components)
                ),
            }
        )
        again, _, _ = saturate(permuted, catalog(), rules())
        assert {c.id for c in again.components} == {c.id for c in done.components}, seed
        # Le connessioni portano l'ordine del file nel nome dei tronconi, ma i
        # pezzi, gli attacchi che occupano e le file devono coincidere.
        assert {
            (c.endpoint_a.component_id, c.endpoint_a.port_id,
             c.endpoint_b.component_id, c.endpoint_b.port_id)
            for c in again.connections
        } == {
            (c.endpoint_a.component_id, c.endpoint_a.port_id,
             c.endpoint_b.component_id, c.endpoint_b.port_id)
            for c in done.connections
        }, seed
    assert canonical_json(done) == reference


def test_the_vent_lands_on_the_service_port_of_the_store() -> None:
    """Lo sfogo sta sull'attacco che il serbatoio gli dedica (D-101 + D-106)."""
    model = load_project(PROVA / "prova-1-due-pdc-accumulo-combinato.json")
    _, applied, _ = saturate(model, catalog(), rules())
    vent = next(
        item for item in applied if item.rule_id == "air-vent-on-the-stored-volume"
    )
    assert vent.service_port == "vent"
    assert vent.anchor.component_id == "accumulo"


# ---------------------------------------------------------------------------
# Cio' che sta a bordo non si aggiunge
# ---------------------------------------------------------------------------


def _entry(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "id": "macchina-di-prova",
        "version": "1.0.0",
        "name": "Macchina di prova",
        "functions": ["heat_generation"],
        "traits": ["maintainable", "shutoff_ordinary", "attachment_inline"],
        "symbol_id": "heat-pump-air-water",
        "ports": [
            {
                "id": "water_supply",
                "domain": "hydronic",
                "medium": "heating_water",
                "flow": "out",
                "required": True,
            },
            {
                "id": "water_return",
                "domain": "hydronic",
                "medium": "heating_water",
                "flow": "in",
                "required": True,
            },
        ],
        "sources": ["CONV-FOUNDATION"],
    }
    base.update(overrides)
    return base


def test_a_function_cannot_be_both_a_job_and_on_board() -> None:
    with pytest.raises(ValidationError, match="mestiere"):
        ComponentDefinition.model_validate(
            _entry(carries_on_board=["heat_generation"])
        )


def test_on_board_functions_are_not_declared_twice() -> None:
    with pytest.raises(ValidationError, match="due volte"):
        ComponentDefinition.model_validate(
            _entry(carries_on_board=["circulation", "circulation"])
        )


def test_a_rule_does_not_add_what_the_machine_carries_on_board() -> None:
    """Una macchina che dichiara il vaso a bordo non ne riceve uno esterno.

    E' la frase esatta del contratto (§3bis-E, criterio 4), provata dai dati:
    si dichiara l'integrazione sulla voce di catalogo e la regola tace."""
    registry = catalog()
    definitions = []
    for item in registry.all():
        if item.id == "heat-pump-air-water":
            item = item.model_copy(
                update={
                    "carries_on_board": [*item.carries_on_board, "expansion"]
                }
            )
        definitions.append(item)
    doctored = ComponentRegistry(
        definitions, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
    model = load_project(PROVA / "prova-2-pdc-deviatrice-acs.json")
    found = evaluate(model, doctored, rules())
    assert "expansion-on-closed-circuit" not in {
        item.rule_id for item in found.proposals
    }
    # Sul catalogo vero, che dichiara solo il circolatore, il vaso esce.
    found_true = evaluate(model, registry, rules())
    assert "expansion-on-closed-circuit" in {
        item.rule_id for item in found_true.proposals
    }
