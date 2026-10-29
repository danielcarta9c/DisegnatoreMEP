"""Il vaso che le macchine non possono perdere (REL-011, proposta 3).

Il manuale Shenling ThermaX R290 6-15 kW, p. 52, letto e ricontrollato in sessione
(`docs/collaudi/REL-010/RAPPORTO.md` par. 2): il vaso non e' a bordo. La skill lo mette sempre, sul
ritorno generale del primario. Ma il progettista puo' spostarlo («altrove», REL-009), e sul caso
rifatto lo ha spostato sul ritorno del secondario, oltre il volano e i suoi rubinetti (T5): il PO,
sulla tavola, «ho anche un dubbio sul vaso di espansione» (I-220).

La regola non sposta il vaso e non ne aggiunge: se il circuito dei generatori resta senza vaso,
**chiede** al progettista. Usa la domanda della proposta 2.

**La regola e' proposta, non attiva**: sta in `docs/collaudi/REL-011/proposta-3/regola/` e si
carica qui accanto a quelle del prodotto.
"""

# categoria: difende il contenuto — REL-011 proposta 3, il vaso sul circuito dei generatori

import json
from functools import cache
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.rules.apply import saturation
from disegnatore_mep.rules.proposal import GapReason, RuleGap
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
RULES = ROOT / "rules" / "hydronic"
PROPOSTA = ROOT / "docs" / "collaudi" / "REL-011" / "proposta-3" / "regola"
REGOLA = "expansion-on-the-generators-own-circuit"
REL009 = ROOT / "docs" / "collaudi" / "REL-009"
RIFATTO = REL009 / "caso-reale-2" / "grafo-prima-stesura.json"
SENZA_SCELTE = REL009 / "caso-reale-1" / "grafo-prima-stesura.json"


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


def _domande(model: ProjectModel) -> list[RuleGap]:
    return [item for item in saturation(model, catalog(), rules()).gaps if item.rule_id == REGOLA]


def test_il_vaso_spostato_oltre_il_volano_e_una_domanda() -> None:
    """La prova rossa sul commit di partenza: sul caso rifatto i due vasi dei primari stanno
    sul ritorno dei secondari, e nessuno lo dice."""
    domande = _domande(load_project(RIFATTO))
    assert sorted(item.network_id for item in domande) == ["primario-acs", "primario-risc"]
    assert all(item.reason is GapReason.DESIGNER_QUESTION for item in domande)
    assert all(item.question and "vaso" in item.question for item in domande)


def test_il_vaso_dove_lo_mette_la_skill_non_chiede_niente() -> None:
    """Lo stesso impianto senza le scelte del progettista: il vaso sta sul ritorno generale
    del primario, e la regola tace."""
    assert _domande(load_project(SENZA_SCELTE)) == []


@pytest.mark.parametrize(
    "caso", sorted((ROOT / "examples" / "prova").glob("prova-*.json")), ids=lambda item: item.stem
)
def test_sugli_impianti_di_prova_tace(caso: Path) -> None:
    assert _domande(load_project(caso)) == []


def test_la_risposta_del_progettista_toglie_la_domanda_del_suo_circuito() -> None:
    payload: dict[str, Any] = json.loads(RIFATTO.read_text(encoding="utf-8"))
    for item in payload["components"]:
        if item["id"] == "pdc-r1":
            item["properties"] = {**item.get("properties", {}), "vaso_separabile": "accettato"}
    domande = _domande(ProjectModel.model_validate(payload))
    assert [item.network_id for item in domande] == ["primario-acs"]


def test_la_regola_non_sposta_e_non_aggiunge() -> None:
    """Il vaso resta dove il progettista lo ha voluto: la regola chiede e basta."""
    con = saturation(load_project(RIFATTO), catalog(), rules())
    senza = saturation(
        load_project(RIFATTO), catalog(), RuleRegistry.from_directory(RULES)
    )
    assert [item.id for item in con.model.components] == [
        item.id for item in senza.model.components
    ]
