"""Il gate G1: le stesse regole su topologie diverse.

La roadmap master lo dichiara cosi': «le stesse regole producono risultati
motivati su varianti topologiche e non modificano il modello senza
approvazione». Tre impianti che non condividono un solo identificativo, e le
stesse quindici regole devono capirli tutti e tre.
"""

from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.rules.engine import evaluate
from disegnatore_mep.rules.registry import RuleRegistry

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
        found = evaluate(project, catalog(), registry)
        fired = {item.rule_id for item in found}
        assert "expansion-on-closed-circuit" in fired, name
        assert "safety-valve-on-generator" in fired, name
        assert "filling-unit-on-return" in fired, name


def test_no_variant_shares_an_identifier_with_another() -> None:
    ids = [
        {item.id for item in project.components}
        for project in VARIANTS.values()
    ]
    assert not ids[0] & ids[1]


def test_every_proposal_is_motivated_on_every_variant() -> None:
    registry = RuleRegistry.from_directory(RULES)
    for project in VARIANTS.values():
        for item in evaluate(project, catalog(), registry):
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
