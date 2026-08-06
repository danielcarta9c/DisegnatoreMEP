"""Il gate G1: le stesse regole su topologie diverse.

La roadmap master lo dichiara cosi': «le stesse regole producono risultati
motivati su varianti topologiche e non modificano il modello senza
approvazione». Tre impianti che non condividono un solo identificativo, e le
stesse quindici regole devono capirli tutti e tre.
"""

from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
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

    Il filtro che esce e' quello dell'acqua fredda, e nessuna regola lo nomina."""
    registry = ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
    found = evaluate(water_service(), registry, RuleRegistry.from_directory(RULES))
    by_rule = {item.rule_id: item for item in found.proposals}
    guard = by_rule["debris-guard-before-what-it-would-ruin"]
    assert "cold_water" in {
        port.medium for port in registry.get(guard.definition_id).ports
    }
    assert "isolate-what-is-serviced" in by_rule


def test_a_rule_with_nothing_to_offer_says_so_instead_of_going_quiet() -> None:
    """Il difetto che ha fatto respingere P2: il silenzio scambiato per «non si
    applica».

    Sul riduttore il defangatore **si applica** — il pezzo dichiara di temere i
    residui — ma il catalogo non ha nessun separatore di fanghi sull'acqua
    fredda. Prima l'ancoraggio veniva scartato senza dire niente, e chi leggeva
    l'elenco delle integrazioni credeva che non mancasse nulla. Adesso esce un
    punto aperto, con la sua categoria e il suo perche'."""
    registry = ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
    found = evaluate(water_service(), registry, RuleRegistry.from_directory(RULES))
    assert "dirt-separation-before-what-it-would-ruin" not in {
        item.rule_id for item in found.proposals
    }
    gap = next(
        item
        for item in found.gaps
        if item.rule_id == "dirt-separation-before-what-it-would-ruin"
    )
    assert gap.medium == "cold_water"
    assert gap.missing_function == "sludge_separation"
    assert gap.anchor.component_id == "acqua-riduttore"
    assert gap.rationale.strip() and gap.source.strip()

    report = build_report(found.proposals, found.gaps)
    assert not report.is_empty
    spoken = " ".join(point.what_is_missing for point in report.open_points)
    assert "sludge_separation" in spoken and "cold_water" in spoken


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
