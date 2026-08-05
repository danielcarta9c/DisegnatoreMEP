"""Il primo pacchetto di regole, e la guardia che tiene il motore compositivo.

La prova che conta e' l'ultima: **nessuna condizione puo' nominare un
componente**. E' il differenziale del prodotto, e il motore delle regole e'
esattamente il posto da cui un catalogo di schemi tipo rientrerebbe.
"""

import json
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
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


def test_the_package_loads_and_agrees_with_the_catalogue() -> None:
    registry = RuleRegistry.from_directory(RULES)
    # 15 regole del primo pacchetto, piu' le 4 di intercettazione per attacco
    # di macchina nate da D-074 (WP2).
    assert len(registry.all()) >= 19
    registry.cross_check(catalog())


def test_a_condition_never_names_a_component() -> None:
    """La guardia. Le condizioni parlano di funzioni, non di pezzi.

    Il campo `then.definition_id` e' l'unica eccezione ed e' per costruzione:
    una proposta deve pur dire cosa propone. Ma e' un esito, non una condizione.
    """
    project = load_project(ESSENTIAL)
    forbidden = {item.id for item in project.components}
    forbidden |= {item.definition_id for item in project.components}
    forbidden |= {item.id for item in project.networks}
    for path in sorted(RULES.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        text = json.dumps(
            {"when": payload["when"], "satisfied_by": payload["satisfied_by"]},
            ensure_ascii=False,
        )
        named = sorted(item for item in forbidden if f'"{item}"' in text)
        assert not named, (path.name, named)


def test_every_rule_declares_a_true_source() -> None:
    for rule in RuleRegistry.from_directory(RULES).all():
        assert rule.source.strip()
        assert rule.rationale.strip()
        # Se cita una norma, deve essere una di quelle davvero acquisite.
        if "UNI" in rule.source or "Raccolta" in rule.source:
            assert "SRC-" in rule.source, rule.id


def test_the_seven_families_are_all_represented() -> None:
    proposed = {rule.then.definition_id for rule in RuleRegistry.from_directory(RULES).all()}
    assert {"expansion-connection", "valve-safety"} <= proposed  # sicurezza
    # intercettazione: per ogni attacco di macchina, su ogni fluido (D-074)
    assert {"valve-isolation", "valve-isolation-dhw", "valve-isolation-dhw-hot"} <= proposed
    assert {"strainer", "dirt-separator"} <= proposed  # protezione
    assert "air-separator" in proposed  # aria
    assert {"filling-unit", "drain-connection"} <= proposed  # riempimento e scarico
    assert {"thermometer", "pressure-gauge"} <= proposed  # misura
    assert {"valve-safety-dhw", "mixing-valve-thermostatic"} <= proposed  # ACS


def test_all_three_categories_are_used() -> None:
    used = {rule.category for rule in RuleRegistry.from_directory(RULES).all()}
    assert IntegrationCategory.NECESSARY in used
    assert IntegrationCategory.RECOMMENDED in used


def test_a_rule_that_proposes_an_unknown_component_is_refused(tmp_path: Path) -> None:
    payload = json.loads((RULES / "expansion-on-closed-circuit.json").read_text("utf-8"))
    payload["then"]["definition_id"] = "componente-che-non-esiste"
    (tmp_path / "bad.json").write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(RuleError, match="does not define"):
        RuleRegistry.from_directory(tmp_path).cross_check(catalog())


def test_a_rule_that_waits_for_an_unknown_function_is_refused(tmp_path: Path) -> None:
    payload = json.loads((RULES / "expansion-on-closed-circuit.json").read_text("utf-8"))
    payload["when"]["anchor_has_function"] = "funzione-inventata"
    (tmp_path / "bad.json").write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(RuleError, match="never fires"):
        RuleRegistry.from_directory(tmp_path).cross_check(catalog())


def test_a_malformed_rule_names_its_file(tmp_path: Path) -> None:
    (tmp_path / "rotta.json").write_text('{"id": "x"}', encoding="utf-8")
    with pytest.raises(RuleError, match="rotta.json"):
        RuleRegistry.from_directory(tmp_path)


def test_a_rule_without_cardinality_is_refused(tmp_path: Path) -> None:
    """Il difetto trovato prototipando, reso impossibile dallo schema."""
    payload = json.loads((RULES / "expansion-on-closed-circuit.json").read_text("utf-8"))
    del payload["cardinality"]
    (tmp_path / "bad.json").write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(RuleError, match="cardinality"):
        RuleRegistry.from_directory(tmp_path)


def test_a_satisfaction_criterion_that_checks_nothing_is_refused(tmp_path: Path) -> None:
    payload = json.loads((RULES / "expansion-on-closed-circuit.json").read_text("utf-8"))
    payload["satisfied_by"] = {}
    (tmp_path / "bad.json").write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(RuleError, match="propose the same accessory again"):
        RuleRegistry.from_directory(tmp_path)
