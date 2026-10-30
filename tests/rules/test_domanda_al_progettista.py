"""La regola che chiede invece di posare, e il volume minimo (REL-011, proposta 2).

Il manuale Shenling ThermaX R290 6-15 kW, p. 52, letto e ricontrollato in sessione
(`docs/collaudi/REL-010/RAPPORTO.md` par. 2): il volume dell'impianto, esclusa la macchina, almeno
40 l, anche a valvole chiuse. Un volume non e' un pezzo, e la skill non dimensiona (D-002): la
regola riconosce il caso in cui il dubbio c'e' — un generatore senza serbatoio sul proprio
circuito — e lo **chiede** al progettista. Non mette un volano: quale, e dove, e' del progettista.

**La regola e' proposta, non attiva**: sta in `docs/collaudi/REL-011/proposta-2/regola/` e si
carica qui accanto a quelle del prodotto. Il motore che la legge e' nel prodotto, inerte finche'
nessuna regola dichiara una domanda.
"""

# categoria: difende il contenuto — REL-011 proposta 2, il volume minimo come domanda al progettista

import json
from functools import cache
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph import Naming
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.rules.apply import saturation
from disegnatore_mep.rules.errors import RuleError
from disegnatore_mep.rules.proposal import GapReason
from disegnatore_mep.rules.registry import RuleRegistry
from disegnatore_mep.rules.report import build_report
from disegnatore_mep.rules.schema import RuleProposalTemplate

ROOT = Path(__file__).resolve().parents[2]
PROVA = ROOT / "examples" / "prova"
RULES = ROOT / "rules" / "hydronic"
PROPOSTA = ROOT / "docs" / "collaudi" / "REL-011" / "proposta-2" / "regola"
REGOLA = "minimum-volume-where-the-generator-has-no-storage"
DIRETTA = PROVA / "prova-3-pdc-diretta-pavimento.json"


@cache
def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog",
        symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols"),
    )


@cache
def rules() -> RuleRegistry:
    """Le regole del prodotto, con quella proposta."""
    registry = RuleRegistry(
        rules=(
            *RuleRegistry.from_directory(RULES).all(),
            *RuleRegistry.from_directory(PROPOSTA).all(),
        )
    )
    registry.cross_check(catalog())
    return registry


def _senza_volano(**proprieta_della_pompa: str) -> ProjectModel:
    """L'impianto 3 con la pompa diretta sui pannelli: il volano tolto e i suoi due tubi
    riuniti in uno. E' la centrale piccola su cui il manuale chiede i 40 litri."""
    payload: dict[str, Any] = json.loads(DIRETTA.read_text(encoding="utf-8"))
    payload["components"] = [item for item in payload["components"] if item["id"] != "volano"]
    for gruppo in payload["subsystems"]:
        gruppo["component_ids"] = [item for item in gruppo["component_ids"] if item != "volano"]
    toccano = [
        item
        for item in payload["connections"]
        if "volano" in (item["endpoint_a"]["component_id"], item["endpoint_b"]["component_id"])
    ]
    assert len(toccano) == 2, toccano
    entra = next(item for item in toccano if item["endpoint_b"]["component_id"] == "volano")
    esce = next(item for item in toccano if item["endpoint_a"]["component_id"] == "volano")
    payload["connections"] = [item for item in payload["connections"] if item not in toccano]
    payload["connections"].append(
        {
            "id": "senza-volano",
            "network_id": entra["network_id"],
            "endpoint_a": entra["endpoint_a"],
            "endpoint_b": esce["endpoint_b"],
            "properties": {},
        }
    )
    for item in payload["components"]:
        if item["id"] == "pdc":
            item["properties"] = {**item.get("properties", {}), **proprieta_della_pompa}
    return ProjectModel.model_validate(payload)


def _domande(model: ProjectModel) -> list[Any]:
    return [item for item in saturation(model, catalog(), rules()).gaps if item.rule_id == REGOLA]


def test_senza_serbatoio_la_regola_chiede() -> None:
    """La prova rossa sul commit di partenza: la pompa diretta sui pannelli, nessuna domanda."""
    risultato = saturation(_senza_volano(), catalog(), rules())
    domande = [item for item in risultato.gaps if item.rule_id == REGOLA]
    assert len(domande) == 1, risultato.gaps
    domanda = domande[0]
    assert domanda.reason is GapReason.DESIGNER_QUESTION
    assert domanda.anchor.component_id == "pdc"
    assert domanda.question and "volume" in domanda.question
    # chiede, e non posa niente: nessun volano messo per prudenza
    assert not [item for item in risultato.applied if item.rule_id == REGOLA]
    assert not [
        item
        for item in risultato.model.components
        if "thermal_storage" in catalog().get(item.definition_id).functions
    ]


def test_la_domanda_arriva_al_progettista_con_le_sue_parole() -> None:
    risultato = saturation(_senza_volano(), catalog(), rules())
    rapporto = build_report(
        risultato.applied, risultato.gaps, Naming.from_directory(ROOT / "naming")
    )
    punto = next(item for item in rapporto.open_points if "Volume minimo" in item.name)
    assert punto.what_is_missing.startswith("una domanda al progettista: ")
    assert "costruttore" in punto.what_is_missing


def test_con_il_volano_non_si_chiede() -> None:
    assert _domande(load_project(DIRETTA)) == []


def test_la_risposta_del_progettista_toglie_la_domanda() -> None:
    assert _domande(_senza_volano(volume_minimo=" Verificato ")) == []


@pytest.mark.parametrize(
    "caso",
    [
        *sorted(PROVA.glob("prova-*.json")),
        ROOT / "docs" / "collaudi" / "REL-009" / "caso-reale-2" / "grafo-prima-stesura.json",
    ],
    ids=lambda item: item.stem,
)
def test_sugli_impianti_che_hanno_un_serbatoio_non_cambia_niente(caso: Path) -> None:
    """Tutti gli impianti di prova hanno un volano o un accumulo sul circuito della macchina:
    la regola tace, e il grafo completo e' quello di prima."""
    assert _domande(load_project(caso)) == []


def test_una_domanda_non_sceglie_un_pezzo() -> None:
    """Il volano, sull'acqua di riscaldamento, lo portano tre voci di catalogo: una regola che
    posasse dovrebbe sceglierne una. Una che chiede no, e il registro la accetta."""
    assert len(catalog().serving("thermal_storage", "heating_water")) > 1
    rules()  # cross_check gia' fatto: non solleva


def test_chi_chiede_non_posa(tmp_path: Path) -> None:
    payload: dict[str, Any] = json.loads((PROPOSTA / f"{REGOLA}.json").read_text("utf-8"))
    with pytest.raises(ValidationError, match="proposes no piece"):
        RuleProposalTemplate.model_validate(
            {**payload["then"], "bridges_from_medium": "cold_water"}
        )
    storta = {**payload, "then": {**payload["then"], "provides_function": "funzione-inventata"}}
    (tmp_path / "storta.json").write_text(json.dumps(storta), encoding="utf-8")
    with pytest.raises(RuleError, match="asks about"):
        RuleRegistry.from_directory(tmp_path).cross_check(catalog())
