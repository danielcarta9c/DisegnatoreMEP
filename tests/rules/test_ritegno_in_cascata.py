"""Il ritegno sulla mandata di ogni generatore in parallelo (REL-011, proposta 1).

Il manuale Shenling ThermaX R290 6-15 kW, p. 40, letto e ricontrollato in sessione
(`docs/collaudi/REL-010/RAPPORTO.md` par. 2): in cascata una valvola di non ritorno
sull'uscita di ogni unita'. Fino a `REL-011` nessuna regola la metteva: c'era solo dove il
progettista la scriveva (il caso reale, I-193) o dove il grafo di prova la portava gia'
(l'ibrido, D-137).

**La regola e' proposta, non attiva.** Sta in `docs/collaudi/REL-011/proposta-1/regola/`, non in
`rules/hydronic/`: cambia tre impianti di prova su cui poggiano altre prove e documenti agli atti,
e quei cambiamenti li approva il PO guardando le tavole (D-146). Qui si carica accanto alle regole
del prodotto; il motore che la legge, invece, e' gia' nel prodotto, inerte finche' nessuna regola
dichiara la condizione.

Le prove, come la regola:

- **due pompe in parallelo**: ciascuna ha il ritegno sulla propria mandata, prima che le
  mandate diventino una, e dopo i propri rubinetti;
- **una pompa sola**: nessun ritegno, nessuno le spinge contro;
- **il ritegno gia' scritto dal progettista** (il caso reale): non se ne aggiunge un secondo.
"""

# categoria: difende il contenuto — REL-011 proposta 1, il ritegno sull'uscita di ogni unita' in cascata

import json
from functools import cache
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.errors import RuleError
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
PROVA = ROOT / "examples" / "prova"
CASO = ROOT / "docs" / "collaudi" / "REL-009" / "caso-reale-2" / "grafo-prima-stesura.json"
RULES = ROOT / "rules" / "hydronic"
PROPOSTA = ROOT / "docs" / "collaudi" / "REL-011" / "proposta-1" / "regola"
REGOLA = "non-return-where-generators-run-in-parallel"


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


def _funzioni(model: ProjectModel, component_id: str) -> frozenset[str]:
    definition = catalog().get(
        next(item.definition_id for item in model.components if item.id == component_id)
    )
    return frozenset((*definition.functions, *definition.carries_on_board))


def _sulla_mandata(model: ProjectModel, generatore: str, attacco: str) -> list[str]:
    """I mestieri dei pezzi in fila sulla mandata, dalla macchina al primo raccordo che
    unisce: e' il tratto che appartiene a quella macchina sola."""
    fila: list[str] = []
    capo = (generatore, attacco)
    for _ in range(50):
        tubo = next(
            item
            for item in model.connections
            if capo
            in (
                (item.endpoint_a.component_id, item.endpoint_a.port_id),
                (item.endpoint_b.component_id, item.endpoint_b.port_id),
            )
        )
        arrivo = (
            tubo.endpoint_b
            if (tubo.endpoint_a.component_id, tubo.endpoint_a.port_id) == capo
            else tubo.endpoint_a
        )
        funzioni = _funzioni(model, arrivo.component_id)
        if "junction" in funzioni:
            return fila
        if "branch_off" in funzioni:
            # cio' che pende dallo stacco sta in fila al punto dello stacco
            funzioni = frozenset().union(
                *(
                    _funzioni(model, ref.component_id)
                    for item in model.connections
                    for ref, altro in (
                        (item.endpoint_a, item.endpoint_b),
                        (item.endpoint_b, item.endpoint_a),
                    )
                    if (altro.component_id, altro.port_id) == (arrivo.component_id, "branch")
                )
            )
        fila.extend(sorted(funzioni))
        capo = (arrivo.component_id, "b")
    raise AssertionError(f"la mandata di {generatore} non arriva a nessun collettore")


def test_due_pompe_in_parallelo_hanno_ciascuna_il_proprio_ritegno() -> None:
    """La prova rossa sul commit di partenza: l'impianto 1 ha due pompe di calore sullo
    stesso collettore, e nessun ritegno."""
    modello = load_project(PROVA / "prova-1-due-pdc-accumulo-combinato.json")
    fatto, applicate, _ = saturate(modello, catalog(), rules())
    for pompa in ("pdc-master", "pdc-slave"):
        fila = _sulla_mandata(fatto, pompa, "water_supply")
        assert "non_return" in fila, (pompa, fila)
        # dopo i rubinetti della macchina, lato impianto, come sul caso reale (I-193)
        assert fila.index("non_return") > fila.index("isolation"), (pompa, fila)
        # e dopo la sicurezza, che sta attaccata alla macchina (D-182)
        assert fila.index("non_return") > fila.index("safety"), (pompa, fila)
    assert sorted(item.anchor.component_id for item in applicate if item.rule_id == REGOLA) == [
        "pdc-master",
        "pdc-slave",
    ]


def test_una_pompa_sola_non_ha_ritegno() -> None:
    modello = load_project(PROVA / "prova-2-pdc-deviatrice-acs.json")
    _, applicate, _ = saturate(modello, catalog(), rules())
    assert not [item for item in applicate if item.rule_id == REGOLA]


def test_il_ritegno_del_progettista_non_si_raddoppia() -> None:
    """Sul caso reale i sei ritegni li ha scritti il progettista (I-193): la regola li
    riconosce e non ne aggiunge."""
    modello = load_project(CASO)
    _, applicate, _ = saturate(modello, catalog(), rules())
    assert not [item for item in applicate if item.rule_id == REGOLA]


def test_il_ritegno_dopo_la_deviatrice_e_gia_quello_della_caldaia() -> None:
    """Nell'ibrido il ritegno della caldaia sta dopo la sua deviatrice, sul ramo verso il
    collettore (D-137): e' il suo, anche se non sta sull'attacco. Guardare il solo attacco
    ne aggiungeva un secondo prima della deviatrice."""
    modello = load_project(PROVA / "prova-4-ibrido-pdc-caldaia.json")
    _, applicate, _ = saturate(modello, catalog(), rules())
    assert not [item for item in applicate if item.rule_id == REGOLA]


def test_la_condizione_non_si_dichiara_sul_tratto_comune(tmp_path: Path) -> None:
    """Il tratto comune e' di tutti: «in parallelo» parla dell'attacco di ciascuno."""
    payload: dict[str, Any] = json.loads((PROPOSTA / f"{REGOLA}.json").read_text("utf-8"))
    payload["cardinality"] = "per_network"
    payload["then"] = {**payload["then"], "placement": "on_the_common_supply"}
    (tmp_path / "probe.json").write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(RuleError, match="lavori in parallelo"):
        RuleRegistry.from_directory(tmp_path)
