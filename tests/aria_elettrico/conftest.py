"""I dati delle prove di REL-012, fase 1: la parte comune del motore per l'aria, il
refrigerante, l'elettrico e il comando.

**I simboli e le voci di catalogo dell'aria-aria non sono ancora nella libreria**: li
porta la fase 2, nel generatore (`examples/graphics/build_symbols.py`), e li fa un
altro lavoro. Qui si leggono **dal kit del PO** com'e' agli atti
(`docs/input-pm/2026-10-29-kit-aria-aria/per-il-repo/`), accanto alla libreria di
oggi, in una cartella temporanea: le prove del motore non aspettano la libreria, e la
libreria non si tocca da qui.
"""

import json
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.model.project import ProjectModel

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "docs" / "input-pm" / "2026-10-29-kit-aria-aria" / "per-il-repo"
DATI = Path(__file__).resolve().parent / "dati"
NAMING = ROOT / "naming"


@pytest.fixture(scope="session")
def cartelle_aria(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path]:
    """Simboli e catalogo di oggi, con quelli del kit accanto."""
    base = tmp_path_factory.mktemp("aria-elettrico")
    simboli, catalogo = base / "simboli", base / "catalogo"
    shutil.copytree(ROOT / "assets" / "symbols", simboli)
    shutil.copytree(ROOT / "examples" / "layout" / "catalog", catalogo)
    for sorgente, destinazione in (
        (KIT / "assets" / "symbols", simboli),
        (KIT / "examples" / "layout" / "catalog", catalogo),
    ):
        for file in sorted(sorgente.iterdir()):
            if not (destinazione / file.name).exists():
                shutil.copy(file, destinazione / file.name)
    return simboli, catalogo


@pytest.fixture(scope="session")
def simboli_aria(cartelle_aria: tuple[Path, Path]) -> SymbolRegistry:
    return SymbolRegistry.from_directory(cartelle_aria[0])


@pytest.fixture(scope="session")
def catalogo_aria(cartelle_aria: tuple[Path, Path], simboli_aria: SymbolRegistry) -> ComponentRegistry:
    return ComponentRegistry.from_directory(cartelle_aria[1], symbols=simboli_aria)


METADATI: dict[str, Any] = {
    "project_id": "prova-rel012",
    "client": "Prova",
    "project_name": "Prova del motore, REL-012 fase 1",
    "commission_code": "REL-012",
    "revision": "00",
    "issue_date": "2026-10-29",
}


@pytest.fixture(scope="session")
def progetto() -> Callable[..., ProjectModel]:
    """Un grafo piccolo scritto in poche righe: reti, pezzi e tubazioni.

    `pezzi` va da identificativo a voce di catalogo (o a `(voce, proprieta', sigla)`);
    `tubi` sono `(id, rete, "pezzo.attacco", "pezzo.attacco")` piu', facoltativi, i
    campi della tubazione."""

    def costruisci(
        reti: dict[str, tuple[str, str]],
        pezzi: dict[str, Any],
        tubi: list[tuple[Any, ...]],
    ) -> ProjectModel:
        componenti = []
        for ident, voce in pezzi.items():
            definizione, proprieta, sigla = (voce, {}, None) if isinstance(voce, str) else voce
            componenti.append(
                {"id": ident, "definition_id": definizione, "tag": sigla, "properties": proprieta}
            )
        connessioni = []
        for tubo in tubi:
            ident, rete, a, b, *altro = tubo
            pa, qa = a.split(".")
            pb, qb = b.split(".")
            connessioni.append(
                {
                    "id": ident,
                    "network_id": rete,
                    "endpoint_a": {"component_id": pa, "port_id": qa},
                    "endpoint_b": {"component_id": pb, "port_id": qb},
                    **(altro[0] if altro else {}),
                }
            )
        return ProjectModel.model_validate(
            {
                "schema_version": "1.1.0",
                "metadata": METADATI,
                "networks": [
                    {"id": ident, "name": ident, "domain": dominio, "medium": fluido}
                    for ident, (dominio, fluido) in reti.items()
                ],
                "components": componenti,
                "connections": connessioni,
            }
        )

    return costruisci


def grafo_di_prova() -> dict[str, Any]:
    return json.loads((DATI / "grafo-di-prova.json").read_text(encoding="utf-8"))
