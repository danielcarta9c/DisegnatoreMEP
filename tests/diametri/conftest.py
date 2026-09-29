"""Gli impianti approvati con i dati di prova dei diametri (REL-007).

Le prove leggono i grafi e i piani agli atti — i cinque impianti di `DRAW-018` e
l'impianto 6 di `REL-003` — con i dati della tabella di `REL-006` e quelli dei
diametri di `docs/collaudi/REL-007/dati-di-prova.json`: sono gli stessi da cui
escono le tavole che il PO guarda.
"""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.model.project import ProjectModel

ROOT = Path(__file__).resolve().parents[2]
APPROVATI = ROOT / "docs" / "collaudi" / "DRAW-018" / "prova-camera-pulita-2026-09-24"
IMPIANTO_6 = ROOT / "docs" / "collaudi" / "REL-003" / "impianto-6"
TABELLA = json.loads(
    (ROOT / "docs" / "collaudi" / "REL-006" / "dati-di-prova.json").read_text("utf-8")
)
DIAMETRI = json.loads(
    (ROOT / "docs" / "collaudi" / "REL-007" / "dati-di-prova.json").read_text("utf-8")
)
NAMING = ROOT / "naming"

IMPIANTI = ("1", "2", "3", "4", "5", "6")


def grafo_e_piano(impianto: str) -> tuple[Path, Path]:
    if impianto == "6":
        return IMPIANTO_6 / "grafo-completo-6.json", IMPIANTO_6 / "piano-6-a.json"
    return (
        APPROVATI / f"grafo-completo-{impianto}.json",
        APPROVATI / f"piano-completo-{impianto}.json",
    )


def documento(
    impianto: str,
    variante: str | None = None,
    con_la_richiesta: bool = True,
    con_i_dati: bool = True,
) -> dict[str, Any]:
    """Il grafo approvato con i dati di prova, come dizionario da ritoccare."""
    dati = DIAMETRI["varianti"][variante] if variante else DIAMETRI["impianti"][impianto]
    grafo, _ = grafo_e_piano(dati.get("impianto", impianto))
    testo: dict[str, Any] = json.loads(grafo.read_text(encoding="utf-8"))
    pezzi = {item["id"]: item for item in testo["components"]}
    for identificativo, proprieta in TABELLA["impianti"][impianto].items():
        pezzi[identificativo]["properties"].update(proprieta)
    if con_i_dati:
        for identificativo, proprieta in dati["pezzi"].items():
            pezzi[identificativo]["properties"].update(proprieta)
    esistenti = set(dati.get("esistenti", []))
    for rete in testo["networks"]:
        if rete["id"] in esistenti:
            rete["esistente"] = True
    if con_la_richiesta:
        reti = [item["id"] for item in testo["networks"]]
        chieste = reti if dati["reti"] == "tutte" else dati["reti"]
        testo["diametri"] = {"reti": [rete for rete in chieste if rete not in esistenti]}
    return testo


@pytest.fixture(scope="session")
def simboli() -> SymbolRegistry:
    return SymbolRegistry.from_directory(ROOT / "assets" / "symbols")


@pytest.fixture(scope="session")
def catalogo(simboli: SymbolRegistry) -> ComponentRegistry:
    return ComponentRegistry.from_directory(ROOT / "examples" / "layout" / "catalog", symbols=simboli)


@pytest.fixture
def modello() -> Callable[..., ProjectModel]:
    def costruisci(
        impianto: str,
        variante: str | None = None,
        con_la_richiesta: bool = True,
        con_i_dati: bool = True,
    ) -> ProjectModel:
        return ProjectModel.model_validate(
            documento(impianto, variante, con_la_richiesta, con_i_dati)
        )

    return costruisci
