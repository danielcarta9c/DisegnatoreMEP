"""Il gate G1: le stesse regole su topologie diverse.

La roadmap master lo dichiara cosi': «le stesse regole producono risultati
motivati su varianti topologiche e non modificano il modello senza
approvazione». Tre impianti che non condividono un solo identificativo, e le
stesse regole devono capirli tutti e tre.
"""

from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph import Naming
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import IntegrationCategory
from disegnatore_mep.rules.engine import evaluate
from disegnatore_mep.rules.registry import RuleRegistry
from disegnatore_mep.rules.report import build_report

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"
NAMING = ROOT / "naming"

METADATA = {
    "project_id": "gate-g1",
    "client": "Nove C",
    "project_name": "Varianti topologiche",
    "commission_code": "DEV-003",
    "revision": "00",
    "issue_date": "2026-08-04",
}


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def plant(prefix: str, generator: str, terminal: str) -> ProjectModel:
    """Un impianto minimo: un generatore, un terminale, e il ritorno.

    Gli identificativi portano il prefisso, cosi' che due varianti non ne
    condividano nessuno: e' la condizione del gate.
    """
    return ProjectModel.model_validate(
        {
            "metadata": {**METADATA, "project_id": f"gate-{prefix}"},
            # Regime grande dichiarato (D-106): fra i testimoni del gate c'e'
            # la sicurezza per generatore, che parla solo sopra i 35 kW.
            "plant_regime": "over_35_kw",
            "subsystems": [
                {
                    "id": f"{prefix}-impianto",
                    "name": "Impianto",
                    "component_ids": [f"{prefix}-gen", f"{prefix}-term"],
                    "network_ids": [f"{prefix}-rete"],
                }
            ],
            "networks": [
                {
                    "id": f"{prefix}-rete",
                    "name": "Riscaldamento",
                    "domain": "hydronic",
                    "medium": "heating_water",
                }
            ],
            "components": [
                {"id": f"{prefix}-gen", "definition_id": generator},
                {"id": f"{prefix}-term", "definition_id": terminal},
            ],
            "connections": [
                {
                    "id": f"{prefix}-mandata",
                    "network_id": f"{prefix}-rete",
                    "endpoint_a": {"component_id": f"{prefix}-gen", "port_id": "water_supply"},
                    "endpoint_b": {"component_id": f"{prefix}-term", "port_id": "in"},
                },
                {
                    "id": f"{prefix}-ritorno",
                    "network_id": f"{prefix}-rete",
                    "endpoint_a": {"component_id": f"{prefix}-term", "port_id": "out"},
                    "endpoint_b": {"component_id": f"{prefix}-gen", "port_id": "water_return"},
                },
            ],
        }
    )


VARIANTS = {
    "alfa": plant("alfa", "heat-pump-air-water", "radiator"),
    "beta": plant("beta", "heat-pump-air-water", "underfloor-panel"),
}


def test_the_same_rules_understand_every_variant() -> None:
    registry = RuleRegistry.from_directory(RULES)
    for name, project in VARIANTS.items():
        found = evaluate(project, catalog(), registry).proposals
        fired = {item.rule_id for item in found}
        assert "expansion-on-closed-circuit" in fired, name
        assert "safety-relief-where-heat-enters-the-water" in fired, name
        assert "filling-unit-on-return" in fired, name
        assert "isolate-what-is-serviced" in fired, name


def test_no_variant_shares_an_identifier_with_another() -> None:
    ids = [
        {item.id for item in project.components}
        for project in VARIANTS.values()
    ]
    assert not ids[0] & ids[1]


def test_every_proposal_is_motivated_on_every_variant() -> None:
    registry = RuleRegistry.from_directory(RULES)
    for project in VARIANTS.values():
        for item in evaluate(project, catalog(), registry).proposals:
            assert item.rationale.strip()
            assert item.source.strip()


def test_the_engine_names_no_component_of_any_variant() -> None:
    """Il gate G0 lo dimostro' per il nucleo; qui vale per il motore delle regole."""
    sources = (ROOT / "src" / "disegnatore_mep" / "rules").glob("*.py")
    text = "\n".join(path.read_text(encoding="utf-8") for path in sources)
    for project in VARIANTS.values():
        for component in project.components:
            assert component.id not in text
            assert component.definition_id not in text


def water_service() -> ProjectModel:
    """Un impianto che non ha niente in comune col primo: sola acqua fredda.

    Serve a mostrare che le stesse regole capiscono un fluido diverso senza
    essere state scritte per lui: il riduttore dichiara di temere i residui e
    riceve il proprio filtro, sull'acqua fredda invece che sull'acqua di
    riscaldamento, perche' il pezzo lo sceglie il catalogo sul fluido della
    rete."""
    return ProjectModel.model_validate(
        {
            "metadata": {**METADATA, "project_id": "gate-acqua"},
            "subsystems": [
                {
                    "id": "acqua-impianto",
                    "name": "Allacciamento",
                    "component_ids": ["acqua-rete", "acqua-riduttore", "acqua-utenza"],
                    "network_ids": ["acqua-rete-fredda"],
                }
            ],
            "networks": [
                {
                    "id": "acqua-rete-fredda",
                    "name": "Acqua fredda",
                    "domain": "hydronic",
                    "medium": "cold_water",
                }
            ],
            "components": [
                {"id": "acqua-rete", "definition_id": "cold-water-inlet"},
                {"id": "acqua-riduttore", "definition_id": "pressure-reducer"},
                {"id": "acqua-utenza", "definition_id": "dhw-draw-off"},
            ],
            "connections": [
                {
                    "id": "acqua-monte",
                    "network_id": "acqua-rete-fredda",
                    "endpoint_a": {"component_id": "acqua-rete", "port_id": "a"},
                    "endpoint_b": {"component_id": "acqua-riduttore", "port_id": "a"},
                },
                {
                    "id": "acqua-valle",
                    "network_id": "acqua-rete-fredda",
                    "endpoint_a": {"component_id": "acqua-riduttore", "port_id": "b"},
                    "endpoint_b": {"component_id": "acqua-utenza", "port_id": "a"},
                },
            ],
        }
    )


def test_the_same_rules_serve_a_medium_they_were_not_written_for() -> None:
    """Una regola dichiara la funzione, il catalogo sceglie il pezzo sul fluido.

    La valvola che esce e' quella dell'acqua fredda, e nessuna regola la nomina."""
    registry = ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
    found = evaluate(water_service(), registry, RuleRegistry.from_directory(RULES))
    by_rule = {item.rule_id: item for item in found.proposals}
    guard = by_rule["isolate-what-is-serviced"]
    assert {
        port.medium for port in registry.get(guard.definition_id).ports
    } == {"cold_water"}
    assert "boundary-shutoff-at-the-edge-of-the-plant" in by_rule


def _two_separate_rings() -> ProjectModel:
    """Due generatori, ciascuno col proprio anello, sulla stessa rete.

    Nessuna tubazione porta tutta l'acqua che torna: il tratto comune del
    ritorno non esiste, e le regole che si posano li' devono dirlo invece di
    scegliere un anello a caso."""
    return ProjectModel.model_validate(
        {
            "metadata": {**METADATA, "project_id": "gate-anelli"},
            "subsystems": [
                {
                    "id": "anelli-impianto",
                    "name": "Impianto",
                    "component_ids": [
                        "anelli-gen-a",
                        "anelli-term-a",
                        "anelli-gen-b",
                        "anelli-term-b",
                    ],
                    "network_ids": ["anelli-rete"],
                }
            ],
            "networks": [
                {
                    "id": "anelli-rete",
                    "name": "Riscaldamento",
                    "domain": "hydronic",
                    "medium": "heating_water",
                }
            ],
            "components": [
                {"id": "anelli-gen-a", "definition_id": "heat-pump-air-water"},
                {"id": "anelli-term-a", "definition_id": "radiator"},
                {"id": "anelli-gen-b", "definition_id": "heat-pump-air-water"},
                {"id": "anelli-term-b", "definition_id": "radiator"},
            ],
            "connections": [
                {
                    "id": "anelli-mandata-a",
                    "network_id": "anelli-rete",
                    "endpoint_a": {"component_id": "anelli-gen-a", "port_id": "water_supply"},
                    "endpoint_b": {"component_id": "anelli-term-a", "port_id": "in"},
                },
                {
                    "id": "anelli-ritorno-a",
                    "network_id": "anelli-rete",
                    "endpoint_a": {"component_id": "anelli-term-a", "port_id": "out"},
                    "endpoint_b": {"component_id": "anelli-gen-a", "port_id": "water_return"},
                },
                {
                    "id": "anelli-mandata-b",
                    "network_id": "anelli-rete",
                    "endpoint_a": {"component_id": "anelli-gen-b", "port_id": "water_supply"},
                    "endpoint_b": {"component_id": "anelli-term-b", "port_id": "in"},
                },
                {
                    "id": "anelli-ritorno-b",
                    "network_id": "anelli-rete",
                    "endpoint_a": {"component_id": "anelli-term-b", "port_id": "out"},
                    "endpoint_b": {"component_id": "anelli-gen-b", "port_id": "water_return"},
                },
            ],
        }
    )


def test_a_rule_with_nothing_to_offer_says_so_instead_of_going_quiet() -> None:
    """Il difetto che ha fatto respingere P2: il silenzio scambiato per «non si
    applica».

    Su due anelli separati il defangatore **si applica** — i generatori ci
    sono — ma il ritorno generale su cui dovrebbe posarsi non esiste: nessuna
    tubazione porta tutta l'acqua. Sceglierne un anello sarebbe decidere al
    posto del progettista; tacere sarebbe il difetto di P2. Esce un punto
    aperto, con la sua categoria e il suo perche'."""
    registry = ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
    found = evaluate(
        _two_separate_rings(), registry, RuleRegistry.from_directory(RULES)
    )
    assert "dirt-separation-before-what-it-would-ruin" not in {
        item.rule_id for item in found.proposals
    }
    gap = next(
        item
        for item in found.gaps
        if item.rule_id == "dirt-separation-before-what-it-would-ruin"
    )
    assert gap.medium == "heating_water"
    assert gap.missing_function == "sludge_separation"
    assert gap.reason.value == "no_common_run"
    assert gap.rationale.strip() and gap.source.strip()

    report = build_report(found.proposals, found.gaps, Naming.from_directory(NAMING))
    assert not report.is_empty
    spoken = " ".join(point.what_is_missing for point in report.open_points)
    # In parole, non con le etichette interne: quel testo finisce nel dossier.
    assert "defangatore" in spoken and "tratto comune" in spoken


def test_a_lone_cylinder_is_told_that_its_drain_cannot_be_proposed() -> None:
    """Lo stesso, sul caso che il collaudo ha portato: un bollitore a se' stante.

    Se un giorno il catalogo perdesse lo scarico sanitario, il bollitore
    resterebbe senza — e la differenza fra «non serve» e «non ce l'ho» deve
    restare leggibile."""
    registry = ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
    without = ComponentRegistry(
        [item for item in registry.all() if item.id != "drain-connection-dhw"],
        symbols=SymbolRegistry.from_directory(SYMBOLS),
    )
    project = load_project(
        ROOT / "examples" / "rules" / "centrale-pdc-essenziale.json"
    )
    found = evaluate(project, without, RuleRegistry.from_directory(RULES))
    gap = next(
        item
        for item in found.gaps
        if item.rule_id == "let-what-holds-its-own-volume-empty"
    )
    assert gap.medium == "domestic_hot_water"
    assert gap.category is IntegrationCategory.RECOMMENDED
