"""Le prove della distinta materiali (REL-013, proposta D-213)."""

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.distinta import RegoleDellaDistinta, carica_regole
from disegnatore_mep.distinta.comando import nomi_dei_fluidi, nomi_del_catalogo
from disegnatore_mep.distinta.grafo import sigle_dello_schema

ROOT = Path(__file__).resolve().parents[2]
REGOLE = ROOT / "rules" / "distinta"
AA01 = ROOT / "examples" / "distinta" / "AA-01" / "grafo-completo.json"


@pytest.fixture(scope="session")
def regole() -> RegoleDellaDistinta:
    return carica_regole(REGOLE)


@pytest.fixture(scope="session")
def nomi() -> tuple[dict[str, str], dict[str, str]]:
    return nomi_del_catalogo(ROOT / "examples" / "layout" / "catalog"), nomi_dei_fluidi(ROOT / "naming")


CATALOGO = ROOT / "examples" / "layout" / "catalog"
NOMI = ROOT / "naming"
COLLAUDO_T1 = Path(__file__).resolve().parent / "collaudo-t1" / "grafo-completo.json"
"""Il grafo del primo collaudo indipendente (REL-012, `docs/collaudi/REL-012/collaudo-t1/`):
un canalizzato Mitsubishi con zonizzazione Airzone, com'e' uscito dalla skill."""


def sigle(grafo: dict[str, Any]) -> dict[str, str]:
    """Le sigle dello schema, come le calcola il comando."""
    return sigle_dello_schema(grafo, CATALOGO, NOMI)


@pytest.fixture
def grafo_aa01() -> dict[str, Any]:
    """Una copia fresca del grafo del caso AA-01, da guastare a piacere."""
    return copy.deepcopy(json.loads(AA01.read_text(encoding="utf-8")))


def tubazione(grafo: dict[str, Any], ident: str) -> dict[str, Any]:
    return next(c for c in grafo["connections"] if c["id"] == ident)


def pezzo(grafo: dict[str, Any], ident: str) -> dict[str, Any]:
    return next(c for c in grafo["components"] if c["id"] == ident)
