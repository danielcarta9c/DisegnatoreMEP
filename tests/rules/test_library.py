"""Il pacchetto delle regole, e la guardia che tiene il motore compositivo.

La prova che conta e' la seconda: **nessuna regola nomina un componente**. E' il
differenziale del prodotto, e il motore delle regole e' esattamente il posto da
cui un catalogo di schemi tipo rientrerebbe.

Da P2 la guardia scandisce la regola **intera** e non piu' le sole condizioni.
Prima non poteva: il campo che diceva *cosa* proporre portava un identificativo
di catalogo, ed era «l'unica eccezione». Ora una regola dichiara la **funzione**
che deve comparire e il catalogo risolve con quale pezzo si ottiene su quel
fluido, quindi l'eccezione non serve piu' e la guardia copre tutto.
"""

import json
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentTrait
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.types import IntegrationCategory
from disegnatore_mep.rules.errors import RuleError
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
RULES = ROOT / "rules" / "hydronic"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
ESSENTIAL = ROOT / "examples" / "rules" / "centrale-pdc-essenziale.json"


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def rules() -> RuleRegistry:
    return RuleRegistry.from_directory(RULES)


def probe(source: str, **changes: Any) -> dict[str, Any]:
    """Una regola vera, con i soli campi cambiati."""
    payload: dict[str, Any] = json.loads((RULES / source).read_text("utf-8"))
    payload.update(changes)
    return payload


def loading(tmp_path: Path, payload: dict[str, Any]) -> RuleRegistry:
    (tmp_path / "probe.json").write_text(json.dumps(payload), encoding="utf-8")
    return RuleRegistry.from_directory(tmp_path)


def test_the_package_loads_and_agrees_with_the_catalogue() -> None:
    registry = rules()
    assert registry.all()
    registry.cross_check(catalog())


def test_no_rule_names_a_component_or_a_definition_anywhere() -> None:
    """La guardia, su tutta la regola e non piu' sulle sole condizioni.

    Confronta valore per valore: un identificativo di progetto o di catalogo che
    comparisse come valore di un campo sarebbe un componente nominato, e la
    regola varrebbe per quel pezzo soltanto."""
    project = load_project(ESSENTIAL)
    forbidden = {item.id for item in project.components}
    forbidden |= {item.definition_id for item in project.components}
    forbidden |= {item.id for item in project.networks}
    forbidden |= {item.id for item in catalog().all()}
    assert forbidden
    for path in sorted(RULES.glob("*.json")):
        text = path.read_text(encoding="utf-8")
        named = sorted(item for item in forbidden if f'"{item}"' in text)
        assert not named, (path.name, named)


def test_the_guard_would_catch_a_component_put_back_into_a_rule() -> None:
    """La prova della prova: una guardia che non cattura piu' niente passa
    perche' non trova nulla, non perche' non c'e' nulla da trovare."""
    disguised = json.dumps({"when": {"anchor_is": "heat-pump-air-water"}})
    forbidden = {item.id for item in catalog().all()}
    assert [item for item in forbidden if f'"{item}"' in disguised]


def test_every_rule_declares_a_true_source_and_a_plant_reason() -> None:
    for rule in rules().all():
        assert rule.source.strip()
        assert rule.rationale.strip()
        # Se cita una norma, deve essere una di quelle davvero acquisite.
        if "UNI" in rule.source or "Raccolta" in rule.source:
            assert "SRC-" in rule.source, rule.id


def test_no_rationale_justifies_itself_with_the_example_or_with_the_sheet() -> None:
    """D-092: la tavola di prova serve a scoprire i difetti, mai a definire la
    correttezza. Una regola motivata dal foglio o dall'esempio e' una regola
    tarata su una fixture."""
    forbidden = (
        "esempio",
        "fixture",
        "tavola",
        "foglio",
        "a3",
        "a4",
        "formato",
        "millimetr",
        "ingombr",
        "disegn",
    )
    for rule in rules().all():
        text = rule.rationale.lower()
        assert not [word for word in forbidden if word in text], (rule.id, text)


def test_the_seven_families_are_all_represented() -> None:
    """Le famiglie si contano sulle **funzioni** proposte: da P2 una regola non
    nomina piu' il pezzo, e cosa esca su quale fluido lo decide il catalogo."""
    proposed = {
        function for rule in rules().all() for function in rule.then.functions()
    }
    assert {"expansion", "safety"} <= proposed  # sicurezza
    assert {"isolation", "isolation_locked_open"} <= proposed  # intercettazione
    assert {"filtration", "sludge_separation"} <= proposed  # protezione
    assert "air_release" in proposed  # aria
    assert {"filling", "drain"} <= proposed  # riempimento e scarico
    assert {"temperature_measurement", "pressure_measurement"} <= proposed  # misura
    assert {"non_return", "dhw_mixing"} <= proposed  # ACS


def test_the_isolation_rule_is_one() -> None:
    """L'accettazione di P2: le sei regole di intercettazione — una per macchina
    e per fluido — sono diventate una sola.

    Si conta cio' che le rende sei: quante regole partono dal fatto che un pezzo
    si smonta in esercizio. Una."""
    serviceable = [
        rule
        for rule in rules().all()
        if rule.when.anchor_has_trait is ComponentTrait.MAINTAINABLE
    ]
    assert len(serviceable) == 1, [rule.id for rule in serviceable]
    only = serviceable[0]
    assert only.when.network_medium is None, "un fluido dichiarato la rifarebbe per fluido"
    assert only.cardinality.value == "per_port"


def test_all_three_categories_are_used() -> None:
    used = {rule.category for rule in rules().all()}
    assert IntegrationCategory.NECESSARY in used
    assert IntegrationCategory.RECOMMENDED in used


def test_a_rule_that_proposes_an_unknown_function_is_refused(tmp_path: Path) -> None:
    payload = probe("expansion-on-closed-circuit.json")
    then = dict(payload["then"])
    then["provides_function"] = "funzione-che-non-esiste"
    with pytest.raises(RuleError, match="no catalogue definition provides"):
        loading(tmp_path, {**payload, "then": then}).cross_check(catalog())


def test_a_rule_whose_function_two_definitions_share_is_refused(tmp_path: Path) -> None:
    """Se due voci portano la stessa funzione sullo stesso fluido, quale delle
    due la regola intenda lo sceglierebbe il programma."""
    payload = probe("expansion-on-closed-circuit.json")
    then = dict(payload["then"])
    then["provides_function"] = "emission"  # radiatore e pannello, entrambi su acqua
    with pytest.raises(RuleError, match="definitions provide"):
        loading(tmp_path, {**payload, "then": then}).cross_check(catalog())


def test_a_rule_that_waits_for_an_unknown_function_is_refused(tmp_path: Path) -> None:
    payload = probe("flow-temperature-where-heat-enters-the-water.json")
    when = dict(payload["when"])
    when["anchor_has_function"] = "funzione-inventata"
    with pytest.raises(RuleError, match="never fires"):
        loading(tmp_path, {**payload, "when": when}).cross_check(catalog())


def test_a_rule_that_anchors_to_nothing_is_refused(tmp_path: Path) -> None:
    payload = probe("expansion-on-closed-circuit.json")
    when = {
        key: value
        for key, value in dict(payload["when"]).items()
        if key not in {"anchor_has_trait", "anchor_has_function"}
    }
    with pytest.raises(RuleError, match="what it anchors to"):
        loading(tmp_path, {**payload, "when": when})


def test_a_rule_that_anchors_to_an_unknown_property_is_refused(tmp_path: Path) -> None:
    """Il vocabolario delle proprieta' e' chiuso (P1): una proprieta' inventata
    non e' una regola generale, e' una regola che non parte mai."""
    payload = probe("expansion-on-closed-circuit.json")
    when = dict(payload["when"])
    when["anchor_has_trait"] = "si_smonta"
    with pytest.raises(RuleError, match="si_smonta"):
        loading(tmp_path, {**payload, "when": when})


def test_a_malformed_rule_names_its_file(tmp_path: Path) -> None:
    (tmp_path / "rotta.json").write_text('{"id": "x"}', encoding="utf-8")
    with pytest.raises(RuleError, match="rotta.json"):
        RuleRegistry.from_directory(tmp_path)


def test_a_rule_without_cardinality_is_refused(tmp_path: Path) -> None:
    """Il difetto trovato prototipando, reso impossibile dallo schema."""
    payload = {
        key: value
        for key, value in probe("expansion-on-closed-circuit.json").items()
        if key != "cardinality"
    }
    with pytest.raises(RuleError, match="cardinality"):
        loading(tmp_path, payload)


def test_a_rule_without_a_satisfaction_criterion_is_refused(tmp_path: Path) -> None:
    """Senza, rieseguire le regole su un modello completo ripropone tutto (D-070)."""
    with pytest.raises(RuleError, match="satisfied_by"):
        loading(tmp_path, probe("expansion-on-closed-circuit.json", satisfied_by={}))


def test_a_rule_cannot_name_an_organ_for_what_never_closes(tmp_path: Path) -> None:
    """Una regola che dicesse con quale valvola si chiude una sicurezza starebbe
    contraddicendo la proprieta' che quella sicurezza dichiara."""
    payload = probe("isolate-what-is-serviced.json")
    then = dict(payload["then"])
    then["provides_function_by_shutoff_regime"] = {"shutoff_never": "isolation"}
    with pytest.raises(RuleError, match="contradicting the property"):
        loading(tmp_path, {**payload, "then": then})
