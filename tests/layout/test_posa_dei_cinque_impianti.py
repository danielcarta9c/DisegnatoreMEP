"""I cinque impianti di prova arrivano **almeno alla posa** (DRAW-005-R1, I-046).

Il PM, respingendo la prima consegna: «Su `cc7ff93` l'impianto 5 arrivava alla
posa e falliva soltanto l'asserzione gia' marcata `xfail`; ora non si posa. Il
`try/except Exception -> pytest.skip` fa apparire la suite verde ma nasconde
una regressione». Qui non c'e' nessun `try`: se un impianto non si posa, la
prova e' rossa. La qualita' geometrica dell'impianto 5 resta la sua prova
rossa-apposta, altrove (`test_zone_dei_pezzi_grossi.py`); questa dice solo che
il posatore lo posa, come sulla base.
"""

from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.geometry import PlacedSymbol
from disegnatore_mep.layout.partition import partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
PLANTS = ROOT / "examples" / "prova"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"

IMPIANTI = sorted(item.name for item in PLANTS.glob("prova-*.json"))


@cache
def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


@cache
def completato(name: str) -> ProjectModel:
    rules = RuleRegistry.from_directory(RULES)
    rules.cross_check(catalog())
    completed, _, _ = saturate(load_project(PLANTS / name), catalog(), rules)
    return completed


@cache
def posa(name: str) -> tuple[PlacedSymbol, ...]:
    """La posa iniziale del foglio: senza `try`, senza `skip`."""
    project = completato(name)
    inline = inline_component_ids(project, catalog())
    partition = partition_project(project, build_trunks(project, inline))[0]
    return tuple(place_sheet(project, partition, catalog(), NOVE_C_A3, inline))


def test_i_cinque_impianti_sono_cinque() -> None:
    assert len(IMPIANTI) == 5, IMPIANTI


@pytest.mark.parametrize("name", IMPIANTI)
def test_l_impianto_arriva_alla_posa(name: str) -> None:
    """Ogni pezzo che non sta in linea ha un posto sul foglio."""
    project = completato(name)
    placed = posa(name)
    inline = inline_component_ids(project, catalog())
    expected = {item.id for item in project.components if item.id not in inline}
    assert {item.component_id for item in placed} == expected, name
