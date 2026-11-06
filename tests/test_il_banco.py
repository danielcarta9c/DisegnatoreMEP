"""Il banco delle tavole come prova (REL-024, fase 1, punto 3).

Ogni caso di `scripts/banco.py` si rifa' e si confronta con `tests/banco/impronte.json`.
Una tavola cambiata **non si fa tacere**: se la modifica e' voluta si rigenerano le impronte
con `python scripts/banco.py --registra`, e la tavola nuova si mostra al PO nella PR (D-146).
"""

# categoria: difende le tavole — la regressione che il PO giudica guardandole.

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

RADICE = Path(__file__).resolve().parent.parent


def _banco() -> ModuleType:
    spec = importlib.util.spec_from_file_location("banco", RADICE / "scripts" / "banco.py")
    assert spec is not None and spec.loader is not None
    modulo = importlib.util.module_from_spec(spec)
    sys.modules["banco"] = modulo  # le dataclass vogliono il modulo registrato
    spec.loader.exec_module(modulo)
    return modulo


BANCO = _banco()


def test_ogni_caso_ha_le_sue_impronte() -> None:
    nomi = {caso.nome for caso in BANCO.CASI}
    assert nomi == set(BANCO.registrate()), (
        "casi e impronte non coincidono: `python scripts/banco.py --registra` dopo aver aggiunto o tolto un caso"
    )


@pytest.mark.parametrize("caso", BANCO.CASI, ids=lambda caso: caso.nome)
def test_la_tavola_e_quella_registrata(caso: object, tmp_path: Path) -> None:
    attese = BANCO.registrate()[caso.nome]  # type: ignore[attr-defined]
    trovate = BANCO.rifai(caso, tmp_path)
    righe = BANCO.differenze(attese, trovate)
    assert not righe, (
        f"{caso.nome}: le uscite non sono quelle registrate.\n"  # type: ignore[attr-defined]
        + "\n".join(righe)
        + "\nSe il cambiamento e' voluto: `python scripts/banco.py --registra --uscita <cartella>`, "
        "e la tavola nuova va mostrata al PO nella PR (D-146). Se non e' voluto, e' una regressione."
    )
