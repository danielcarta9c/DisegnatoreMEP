"""Prima l'idraulica e l'aeraulica, poi l'elettrico (REL-015, I-231).

Il PO, il 30 ottobre 2026: «Non vorrei che le linee elettriche facciano spostare le
linee idrauliche. [...] Ricordiamoci che prima si disegna idronico - areaulico e poi
si aggiunge elettrico e comando.»

**La regola, resa misurabile**: sulla tavola unica (`vista: tutto`) la parte
dell'acqua e dell'aria — tubazioni, pezzi, e le sigle, le etichette e le scritte dei
pezzi e dei tratti — e' **la stessa** della vista `idraulica` dello stesso grafo, col
piano senza i pezzi del solo comando; al decimo di millimetro, a meno della
traslazione del disegno nel foglio (`validation.parte_idraulica`).

Sui tre casi del pacchetto: la tavola unica piccola di `REL-012/fase-3/piccolo`
(acqua), la tavola di prova di `REL-012/fase-1` (aria-aria con l'elettrico: la vista
che toglie i cavi), e la M.02 del kit rifatta in `REL-012/fase-2` (aria, refrigerante,
condensa). Rossa sul commit di partenza (`c99b192`): le sigle VMR-01, CIR-01 e SO-01
della tavola piccola cambiano posto col cavo che arriva al pezzo.
"""
# categoria: difende il motore

import contextlib
import importlib.util
import io
import json
from functools import cache
from pathlib import Path
from types import ModuleType

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import render_sheet
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.piano.esecutore import esegui_piano
from disegnatore_mep.piano.formato import PianoDiComposizione
from disegnatore_mep.validation.parte_idraulica import (
    il_comando_del_grafo,
    parte_idraulica,
    pezzi_da_togliere,
    piano_della_vista_idraulica,
)

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
NAMING = ROOT / "naming"
REL012 = ROOT / "docs" / "collaudi" / "REL-012"


@cache
def simboli() -> SymbolRegistry:
    return SymbolRegistry.from_directory(SYMBOLS)


@cache
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(CATALOG, symbols=simboli())


@pytest.fixture(scope="module")
def tavola_di_prova() -> ModuleType:
    """La tavola di prova della fase 1 (`examples/aria_elettrico/tavola_di_prova.py`)."""
    spec = importlib.util.spec_from_file_location(
        "tavola_di_prova", ROOT / "examples" / "aria_elettrico" / "tavola_di_prova.py"
    )
    assert spec is not None and spec.loader is not None
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@pytest.fixture(scope="module")
def registri_aria(
    tmp_path_factory: pytest.TempPathFactory, tavola_di_prova: ModuleType
) -> tuple[SymbolRegistry, ComponentRegistry]:
    """Simboli e catalogo della tavola di prova: quelli di oggi, col kit accanto."""
    cartella_simboli, cartella_catalogo = tavola_di_prova.cartelle_di_prova(tmp_path_factory.mktemp("aria"))
    libreria = SymbolRegistry.from_directory(cartella_simboli)
    return libreria, ComponentRegistry.from_directory(cartella_catalogo, symbols=libreria)


def _svg(
    modello: ProjectModel,
    piano: dict,
    catalogo: ComponentRegistry,
    simboli: SymbolRegistry,
) -> str:
    esito = esegui_piano(modello, PianoDiComposizione.model_validate(piano), catalogo, simboli, NAMING)
    assert esito.disegno is not None, esito.errore
    return render_sheet(esito.disegno.sheets[0], esito.frame, simboli)


def _le_due_viste(
    modello: ProjectModel, piano: dict, catalogo: ComponentRegistry, simboli: SymbolRegistry
) -> list[str]:
    """Le differenze fra la parte dell'acqua della tavola unica e quella della vista
    idraulica: vuote, se la regola tiene."""
    assert piano.get("vista", "tutto") == "tutto"
    comando = il_comando_del_grafo(modello, catalogo, simboli, NAMING)
    assert comando.colori, "il caso deve avere l'elettrico"
    idraulica = piano_della_vista_idraulica(piano, pezzi_da_togliere(modello, catalogo))
    tutto = parte_idraulica(_svg(modello, piano, catalogo, simboli), comando)
    sola = parte_idraulica(_svg(modello, idraulica, catalogo, simboli), comando)
    assert sola.simboli and sola.tracciati and sola.testi
    return tutto.differenze(sola)


def test_la_tavola_unica_piccola_ha_l_idraulica_della_vista_idraulica() -> None:
    """La distribuzione di zona con miscelatrice, regolatore e quadro (fase 3)."""
    cartella = REL012 / "fase-3" / "piccolo"
    modello = load_project(cartella / "grafo-completo.json")
    piano = json.loads((cartella / "piano.json").read_text(encoding="utf-8"))
    assert _le_due_viste(modello, piano, catalogo(), simboli()) == []


def test_la_centrale_su_tavola_unica_ha_l_idraulica_della_vista_idraulica() -> None:
    """La centrale della fase 3 composta sulla tavola unica (`piano-tutto.json`, il
    confronto agli atti): qui i cavi orizzontali incrociano i tubi verticali, e sul
    commit di partenza erano i tubi a spezzarsi con l'archetto. Adesso scavalca il
    cavo, e il tubo resta intero."""
    cartella = REL012 / "fase-3" / "centrale"
    modello = load_project(cartella / "grafo-completo.json")
    piano = json.loads((cartella / "piano-tutto.json").read_text(encoding="utf-8"))
    assert _le_due_viste(modello, piano, catalogo(), simboli()) == []


def test_la_tavola_di_prova_dell_aria_ha_l_aria_della_vista_senza_cavi(
    tavola_di_prova: ModuleType, registri_aria: tuple[SymbolRegistry, ComponentRegistry]
) -> None:
    """L'unita' esterna e la canalizzata con quadro, sezionatore e comando (fase 1)."""
    modello = load_project(tavola_di_prova.GRAFO)
    piano = json.loads(Path(tavola_di_prova.PIANO).read_text(encoding="utf-8"))
    simboli_aria, catalogo_aria = registri_aria
    assert _le_due_viste(modello, piano, catalogo_aria, simboli_aria) == []


def test_la_m02_del_kit_ha_l_aria_della_vista_senza_cavi(tmp_path: Path) -> None:
    """La M.02 del kit aria-aria, rifatta dalla skill (fase 2): aria, refrigerante e
    condensa."""
    from disegnatore_mep.skill import cartelle_del_repository, main

    cartella = REL012 / "fase-2"
    completo = tmp_path / "grafo-completo.json"
    with contextlib.redirect_stdout(io.StringIO()):
        assert main(["completa", str(cartella / "grafo.json"), "--out", str(completo)], cartelle_del_repository(ROOT)) == 0
    modello = load_project(completo)
    piano = json.loads((cartella / "piano.json").read_text(encoding="utf-8"))
    assert _le_due_viste(modello, piano, catalogo(), simboli()) == []


@pytest.mark.parametrize("vista", ["tutto", "idraulica"])
def test_la_parte_idraulica_toglie_il_comando_e_tiene_l_acqua(vista: str) -> None:
    """La misura stessa: sulla tavola piccola toglie i cavi, il regolatore, il quadro,
    la sonda esterna e le loro scritte, e tiene la miscelatrice, il collettore, le
    sigle dei pezzi d'acqua e i loro tracciati."""
    cartella = REL012 / "fase-3" / "piccolo"
    modello = load_project(cartella / "grafo-completo.json")
    piano = json.loads((cartella / "piano.json").read_text(encoding="utf-8"))
    if vista == "idraulica":
        piano = piano_della_vista_idraulica(piano, pezzi_da_togliere(modello, catalogo()))
    comando = il_comando_del_grafo(modello, catalogo(), simboli(), NAMING)
    assert {"regolatore", "quadro", "sonda-esterna"} <= comando.pezzi
    parte = parte_idraulica(_svg(modello, piano, catalogo(), simboli()), comando)
    pezzi = {voce.split()[0] for voce in parte.simboli}
    assert {"miscelatrice", "collettore", "circolatore", "sonda-mandata"} <= pezzi
    assert not pezzi & {"regolatore", "quadro", "sonda-esterna"}
    scritte = " ".join(parte.testi)
    for sigla in ("VMR-01", "CIR-01", "SO-01", "COL-01", "«mandata»"):
        assert sigla in scritte
    for del_comando in ("RG-01", "QE-01", "SE-01", "4G1", "2x0,75"):
        assert del_comando not in scritte
    assert not any("#784212" in voce or "#2020e0" in voce for voce in parte.tracciati)
