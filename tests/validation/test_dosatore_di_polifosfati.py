"""Il dosatore di polifosfati sta solo sull'acqua fredda che entra nell'accumulo dell'ACS
(REL-009, I-198, D-204).

Il PO: «va installato esclusivamente sulla linea di ingresso dell'acqua fredda sanitaria
che alimenta il boiler di accumulo dell'ACS. Non deve assolutamente essere inserito
nell'acqua tecnica (circuito chiuso di riscaldamento)». Gli attacchi del dosatore sono di
acqua fredda; la validazione guarda dove va l'acqua dopo di lui.
"""

# categoria: difende il contenuto — I-198, i polifosfati non vanno nell'acqua tecnica

import json
from functools import cache
from pathlib import Path
from typing import Any

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.validation.topology import validate_project

ROOT = Path(__file__).resolve().parents[2]
PROVA = ROOT / "docs" / "collaudi" / "REL-009" / "simboli-nuovi" / "grafo.json"


@cache
def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog",
        symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols"),
    )


def _codici(grafo: dict[str, Any]) -> list[str]:
    return [item.code for item in validate_project(ProjectModel.model_validate(grafo), catalog()).issues]


def _tubo(grafo: dict[str, Any], ident: str) -> dict[str, Any]:
    return next(item for item in grafo["connections"] if item["id"] == ident)


def test_sull_acqua_fredda_che_entra_nell_accumulo_dell_acs_il_dosatore_regge() -> None:
    codici = _codici(json.loads(PROVA.read_text(encoding="utf-8")))
    assert "DOSER_NOT_ON_THE_DHW_FEED" not in codici
    assert "DOSER_FEEDS_THE_TECHNICAL_WATER" not in codici


def test_il_dosatore_che_alimenta_un_riempimento_non_regge() -> None:
    """I polifosfati andrebbero nell'acqua tecnica: il riempimento la carica."""
    grafo = json.loads(PROVA.read_text(encoding="utf-8"))
    grafo["components"].append({"id": "riempimento", "definition_id": "filling-unit", "tag": None, "properties": {}})
    _tubo(grafo, "f2")["endpoint_b"] = {"component_id": "riempimento", "port_id": "a"}
    codici = _codici(grafo)
    assert "DOSER_FEEDS_THE_TECHNICAL_WATER" in codici
    assert "DOSER_NOT_ON_THE_DHW_FEED" in codici


def test_il_dosatore_che_non_alimenta_un_accumulo_non_regge() -> None:
    """La miscelatrice prende acqua fredda, ma non e' un accumulo: l'acqua che la
    attraversa non si scalda e non deposita calcare."""
    grafo = json.loads(PROVA.read_text(encoding="utf-8"))
    grafo["components"].append(
        {"id": "miscelatrice", "definition_id": "mixing-valve-thermostatic", "tag": None, "properties": {}}
    )
    _tubo(grafo, "f2")["endpoint_b"] = {"component_id": "miscelatrice", "port_id": "cold_in"}
    assert "DOSER_NOT_ON_THE_DHW_FEED" in _codici(grafo)


def test_il_verso_in_cui_il_grafo_scrive_il_tubo_non_conta() -> None:
    """Il grafo non dice da che capo del tubo va l'acqua: si parte dall'attacco d'uscita
    del dosatore. E la validazione non pretende la libreria dei simboli."""
    grafo = json.loads(PROVA.read_text(encoding="utf-8"))
    for ident in ("f1", "f2"):
        tubo = _tubo(grafo, ident)
        tubo["endpoint_a"], tubo["endpoint_b"] = tubo["endpoint_b"], tubo["endpoint_a"]
    solo_catalogo = ComponentRegistry.from_directory(ROOT / "examples" / "layout" / "catalog")
    codici = [item.code for item in validate_project(ProjectModel.model_validate(grafo), solo_catalogo).issues]
    assert "DOSER_NOT_ON_THE_DHW_FEED" not in codici
    assert "DOSER_FEEDS_THE_TECHNICAL_WATER" not in codici
