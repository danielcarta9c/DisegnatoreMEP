"""Il motore delle regole, provato sul caso di accettazione.

Le prove che contano sono tre, e nascono tutte da difetti visti prototipando
prima che ci fosse del codice da correggere: la cardinalita', l'idempotenza e il
fatto che il motore non tocchi il modello.
"""

from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.canonical import canonical_json
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.types import IntegrationCategory
from disegnatore_mep.rules.apply import apply_proposals
from disegnatore_mep.rules.engine import evaluate
from disegnatore_mep.rules.proposal import RuleProposal
from disegnatore_mep.rules.registry import RuleRegistry
from disegnatore_mep.validation.topology import validate_project

ROOT = Path(__file__).resolve().parents[2]
ESSENTIAL = ROOT / "examples" / "rules" / "centrale-pdc-essenziale.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def rules() -> RuleRegistry:
    return RuleRegistry.from_directory(RULES)


def proposals() -> list[RuleProposal]:
    return evaluate(load_project(ESSENTIAL), catalog(), rules())


def test_the_engine_proposes_the_missing_accessories() -> None:
    found = proposals()
    assert found
    assert {item.definition_id for item in found} >= {
        "expansion-connection",
        "valve-safety",
        "filling-unit",
        "strainer",
    }


def test_a_rule_proposes_once_per_declared_cardinality() -> None:
    """Il difetto trovato prototipando: la pompa di calore ha due ritorni, e il
    vaso di espansione usciva due volte."""
    vessels = [
        item
        for item in proposals()
        if item.rule_id == "expansion-on-closed-circuit"
    ]
    assert len(vessels) == 1, vessels


def test_the_engine_is_idempotent() -> None:
    """Rieseguire su un modello gia' completato non ripropone nulla."""
    project = load_project(ESSENTIAL)
    completed = apply_proposals(project, evaluate(project, catalog(), rules()))
    assert evaluate(completed, catalog(), rules()) == []


def test_the_engine_does_not_touch_the_model() -> None:
    """§9.2: il motore non trasforma una proposta in progetto approvato."""
    project = load_project(ESSENTIAL)
    before = canonical_json(project)
    evaluate(project, catalog(), rules())
    assert canonical_json(project) == before


def test_the_same_input_gives_the_same_proposals() -> None:
    assert [item.component_id for item in proposals()] == [
        item.component_id for item in proposals()
    ]


def test_every_proposal_carries_its_reason_and_source() -> None:
    for item in proposals():
        assert item.rationale.strip()
        assert item.source.strip()
        assert item.category in set(IntegrationCategory)


def test_the_completed_model_is_valid() -> None:
    project = load_project(ESSENTIAL)
    completed = apply_proposals(project, evaluate(project, catalog(), rules()))
    assert validate_project(completed, catalog()).ok


def test_applying_nothing_changes_nothing() -> None:
    project = load_project(ESSENTIAL)
    assert canonical_json(apply_proposals(project, [])) == canonical_json(project)


def test_applying_leaves_the_traceability_behind() -> None:
    """D-039: `RuleApplicationModel` esisteva senza che nessuno lo scrivesse."""
    project = load_project(ESSENTIAL)
    found = evaluate(project, catalog(), rules())
    completed = apply_proposals(project, found)
    assert len(completed.rule_applications) == len(found)
    versions = {rule.id: rule.version for rule in rules().all()}
    for applied in completed.rule_applications:
        assert applied.rule_version == versions[applied.rule_id]
        assert applied.entity_ids
