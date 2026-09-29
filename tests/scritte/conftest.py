"""Le tavole approvate con le scritte a 9 punti (REL-008).

Gli stessi grafi, piani e dati di prova delle prove dei diametri (`tests/diametri`):
le tavole di `REL-008` sono quelle di `REL-007` con le scritte nuove, e la prova le
guarda nello stesso modo.
"""

import importlib.util
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.layout.geometry import SheetGeometry
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.piano.esecutore import EsitoDelPiano, esegui_piano
from disegnatore_mep.piano.formato import carica_piano


def _diametri() -> ModuleType:
    percorso = Path(__file__).resolve().parents[1] / "diametri" / "conftest.py"
    spec = importlib.util.spec_from_file_location("dati_delle_tavole_di_rel007", percorso)
    assert spec is not None and spec.loader is not None
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


DIAMETRI = _diametri()
ROOT: Path = DIAMETRI.ROOT
IMPIANTI: tuple[str, ...] = DIAMETRI.IMPIANTI


@dataclass(frozen=True)
class Tavola:
    modello: ProjectModel
    esito: EsitoDelPiano
    foglio: SheetGeometry


_TAVOLE: dict[str, Tavola] = {}


@pytest.fixture(scope="session")
def simboli() -> SymbolRegistry:
    return SymbolRegistry.from_directory(ROOT / "assets" / "symbols")


@pytest.fixture(scope="session")
def catalogo(simboli: SymbolRegistry) -> ComponentRegistry:
    return ComponentRegistry.from_directory(ROOT / "examples" / "layout" / "catalog", symbols=simboli)


@pytest.fixture
def tavola(catalogo: ComponentRegistry, simboli: SymbolRegistry) -> Callable[[str], Tavola]:
    """La tavola di un impianto con i dati di prova di `REL-007`, eseguita una volta."""

    def esegui(impianto: str) -> Tavola:
        if impianto not in _TAVOLE:
            _, piano = DIAMETRI.grafo_e_piano(impianto)
            modello = ProjectModel.model_validate(DIAMETRI.documento(impianto))
            esito = esegui_piano(modello, carica_piano(piano), catalogo, simboli, DIAMETRI.NAMING)
            assert esito.disegno is not None
            _TAVOLE[impianto] = Tavola(modello=modello, esito=esito, foglio=esito.disegno.sheets[0])
        return _TAVOLE[impianto]

    return esegui
