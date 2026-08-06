"""Il motore delle regole, provato sul caso di accettazione.

Le prove che contano sono tre, e nascono tutte da difetti visti prototipando
prima che ci fosse del codice da correggere: la cardinalita', l'idempotenza e il
fatto che il motore non tocchi il modello.
"""

from pathlib import Path

import pytest

from disegnatore_mep.assembly import assemble
from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.canonical import canonical_json
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.types import IntegrationCategory
from disegnatore_mep.rules import apply as apply_module
from disegnatore_mep.rules.apply import apply_proposals, saturate
from disegnatore_mep.rules.engine import evaluate
from disegnatore_mep.rules.errors import RuleError
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
    return evaluate(load_project(ESSENTIAL), catalog(), rules()).proposals


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
    vaso di espansione usciva due volte.

    «Una per rete» vuol dire una per rete, non una in tutto: un impianto con un
    circuito di riscaldamento e uno sanitario vuole due vasi, uno per circuito,
    e ciascuno esce una volta sola."""
    vessels = [
        item
        for item in proposals()
        if item.rule_id == "expansion-on-closed-circuit"
    ]
    assert len(vessels) == len({item.network_id for item in vessels}), vessels


def test_the_engine_is_idempotent() -> None:
    """Rieseguire su un modello gia' completato non ripropone nulla."""
    project = load_project(ESSENTIAL)
    completed, _, _ = saturate(project, catalog(), rules())
    assert evaluate(completed, catalog(), rules()).proposals == []


def test_completing_takes_more_than_one_pass_and_then_stops() -> None:
    """Le regole valgono anche su cio' che le regole aggiungono (D-090).

    Un accessorio proposto e' a sua volta un pezzo che si smonta in esercizio, e
    vuole i propri organi di chiusura: una passata sola lascerebbe scoperto
    proprio cio' che ha appena aggiunto. Il ciclo si spegne perche' un organo di
    chiusura non chiede a sua volta di essere intercettato."""
    project = load_project(ESSENTIAL)
    passes = 0
    current = project
    while True:
        found = evaluate(current, catalog(), rules())
        if found.is_empty:
            break
        # Come fa la catena: applicare e **rimettere in fila**, perche'
        # riordinare puo' scoprire un attacco che era coperto per caso.
        current = assemble(
            apply_proposals(current, found.proposals, catalog()),
            catalog(),
            {item.id: item for item in rules().all()},
        )
        passes += 1
    assert passes > 1
    completed, applied, _ = saturate(project, catalog(), rules())
    assert canonical_json(completed) == canonical_json(current)
    assert len(applied) > len(evaluate(project, catalog(), rules()).proposals)


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
    completed, _, _ = saturate(project, catalog(), rules())
    assert validate_project(completed, catalog()).ok


def test_applying_nothing_changes_nothing() -> None:
    project = load_project(ESSENTIAL)
    assert canonical_json(apply_proposals(project, [], catalog())) == canonical_json(project)


def test_applying_leaves_the_traceability_behind() -> None:
    """D-039: `RuleApplicationModel` esisteva senza che nessuno lo scrivesse."""
    project = load_project(ESSENTIAL)
    completed, found, _ = saturate(project, catalog(), rules())
    assert len(completed.rule_applications) == len(found)
    versions = {rule.id: rule.version for rule in rules().all()}
    for applied in completed.rule_applications:
        assert applied.rule_version == versions[applied.rule_id]
        assert applied.entity_ids


def test_the_limit_counts_productive_passes_and_not_the_one_that_finds_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """L'errore che il collaudo ha trovato: un modello **arrivato** che falliva.

    Le passate produttive del caso di accettazione sono due. Col limite fissato
    a due deve concludere, non fermarsi: la valutazione che scopre che non c'e'
    piu' niente da fare non e' un giro in piu' del ciclo, e contarla nel limite
    faceva respingere un modello gia' completo.
    """
    project = load_project(ESSENTIAL)
    productive = 0
    current = project
    while True:
        found = evaluate(current, catalog(), rules())
        if found.is_empty:
            break
        # Come fa la catena: applicare e **rimettere in fila**, perche'
        # riordinare puo' scoprire un attacco che era coperto per caso.
        current = assemble(
            apply_proposals(current, found.proposals, catalog()),
            catalog(),
            {item.id: item for item in rules().all()},
        )
        productive += 1

    monkeypatch.setattr(apply_module, "ROUNDS", productive)
    completed, applied, _ = saturate(project, catalog(), rules())
    assert canonical_json(completed) == canonical_json(current)
    assert applied


def test_a_ceiling_too_low_stops_and_names_the_rules_still_asking(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """E quando si ferma davvero, deve dire chi stava ancora chiedendo.

    Il messaggio precedente costruiva l'elenco da una valutazione nuova, che a
    quel punto poteva essere vuota, e usciva la frase «the last round asked
    for .» — un errore che non dice niente a nessuno."""
    monkeypatch.setattr(apply_module, "ROUNDS", 1)
    with pytest.raises(RuleError) as raised:
        saturate(load_project(ESSENTIAL), catalog(), rules())
    message = str(raised.value)
    assert "asked for " in message
    named = message.split("asked for ", 1)[1]
    assert named.strip(" .")
    assert any(rule.id in message for rule in rules().all())
