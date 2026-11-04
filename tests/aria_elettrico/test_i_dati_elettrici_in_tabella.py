"""Sulla tavola dell'elettrico la tabella porta i dati elettrici, non quelli idronici (I-277).

Il PO, il 4 novembre 2026: «che senso ha mettere le caratteristiche idroniche della pdc e del
circolatore in una tabella nella tavola elettrica ci dovrebbero andare le info elettriche. pdc
Assorbimento ampere max? cavo minimo richiesto di sezione? alimentazione 230 o 400 ecc.».

Quattro dati del progettista, facoltativi — `alimentazione` (testo), `potenza_elettrica_kw`
(kW), `corrente_max_a` (A), `cavo_minimo` (testo) —, e la portata del `contatto` del relè e
del termostato a contatto. I numeri qui sotto sono **dati di prova**, scritti nel test: non
sono i dati di una macchina.
"""
# categoria: difende il motore

from functools import cache
from pathlib import Path

import pytest
from pydantic import ValidationError

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph import Naming, read_plant
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.tabella import dati_elettrici, righe_della_tabella
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ComponentInstance, ProjectModel
from disegnatore_mep.piano.esecutore import esegui_piano
from disegnatore_mep.piano.formato import carica_piano

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
NAMING = ROOT / "naming"
CASO = ROOT / "docs" / "collaudi" / "REL-017" / "termostato"

DATI_DI_PROVA = {
    "alimentazione": "230 V 1~",
    "potenza_elettrica_kw": 3.9,
    "corrente_max_a": 18,
    "cavo_minimo": "3G6",
}


@cache
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS))


def _con_i_dati_elettrici() -> ProjectModel:
    grafo = load_project(CASO / "grafo-completo.json")
    return grafo.model_copy(
        update={
            "components": [
                item.model_copy(update={"properties": {**item.properties, **DATI_DI_PROVA}})
                if item.id == "pdc"
                else item
                for item in grafo.components
            ]
        }
    )


def _righe(grafo: ProjectModel, ogni_pezzo: bool) -> dict[str, str | None]:
    catalogo_del_grafo = catalogo().per_il_progetto(grafo)
    naming = Naming.from_directory(NAMING)
    sigle = read_plant(grafo, catalogo_del_grafo, naming).sigle
    righe = righe_della_tabella(
        grafo, catalogo_del_grafo, naming, dict(sigle), (item.id for item in grafo.components), ogni_pezzo
    )
    return {riga.codice or "": riga.caratteristiche for riga in righe}


def test_la_pompa_di_calore_sulla_tavola_dell_elettrico_porta_i_dati_elettrici() -> None:
    esito = esegui_piano(
        _con_i_dati_elettrici(),
        carica_piano(CASO / "piano-elettrico.json"),
        catalogo(),
        SymbolRegistry.from_directory(SYMBOLS),
        NAMING,
    )
    assert esito.disegno is not None, esito.errore
    tabella = esito.disegno.sheets[0].tabella
    assert tabella is not None
    righe = {riga.codice: riga for riga in tabella.righe}
    # Nell'ordine: alimentazione, potenza elettrica, corrente massima, cavo minimo; la
    # virgola decimale e l'unita' come per i dati idronici. Niente «12 kW» termici.
    assert righe["GT-01"].caratteristiche == "230 V 1~ · 3,9 kW · 18 A · 3G6"
    assert righe["GT-01"].marca == "Shenling"
    # Il circolatore senza dati: il trattino, non la portata e la prevalenza.
    assert righe["CIR-01"].caratteristiche is None
    assert righe["TAC-01"].caratteristiche == "5(2) A 250 V"


def test_la_tabella_idraulica_non_cambia() -> None:
    """Gli stessi pezzi, coi dati elettrici scritti: la tabella dell'idraulica scrive la
    potenza termica come prima, e niente dei dati elettrici."""
    con = _righe(_con_i_dati_elettrici(), ogni_pezzo=False)
    senza = _righe(load_project(CASO / "grafo-completo.json"), ogni_pezzo=False)
    assert con == senza
    assert con["GT-01"] == "12 kW"


def test_i_dati_elettrici_si_scrivono_solo_se_dati() -> None:
    assert dati_elettrici(("heat_generation",), {"power_kw": 12, "volume_l": 50}) == []
    assert dati_elettrici(("heat_generation",), {"corrente_max_a": 25.5}) == ["25,5 A"]
    # La portata del contatto la scrivono solo il relè e il termostato a contatto.
    assert dati_elettrici(("power_switching",), {"contatto": "10 A 250 V"}) == ["10 A 250 V"]
    assert dati_elettrici(("circulation",), {"contatto": "10 A 250 V"}) == []


@pytest.mark.parametrize("chiave", ["corrente_max_a", "potenza_elettrica_kw"])
def test_i_numeri_elettrici_sono_numeri(chiave: str) -> None:
    with pytest.raises(ValidationError, match=chiave):
        ComponentInstance(id="pdc", definition_id="heat-pump-air-water", properties={chiave: "18 A"})
