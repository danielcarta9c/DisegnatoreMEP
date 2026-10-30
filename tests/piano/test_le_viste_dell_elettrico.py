"""Elettrico e comando nell'idronico (REL-012, fase 3, I-226, I-227).

Quattro cose, e sono quelle che il pacchetto chiede:

* **le porte di comando sono facoltative e non cambiano niente** finche' il grafo non
  le collega: il registro le tiene da parte, e una tavola disegnata col catalogo di
  oggi e' identica byte per byte a quella disegnata con un catalogo che non le ha
  mai avute;
* **le viste filtrano giusto**: l'idraulica senza cavi e senza i pezzi del solo
  comando, l'elettrico coi soli cavi e i pezzi che toccano;
* **le sigle sono le stesse** sulle due tavole;
* **le tavole di prova escono pulite**: zero rilievi bloccanti, zero tratte cedute.
"""
# categoria: difende il motore

from dataclasses import replace
from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.errors import CatalogError
from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph import Naming, read_plant
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.trunks import build_trunks, porte_di_comando_in_linea
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import Domain
from disegnatore_mep.piano.esecutore import esegui_piano
from disegnatore_mep.piano.formato import ErroreDelPiano, carica_piano
from disegnatore_mep.piano.vista import solo_comando, vista_del_grafo

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
NAMING = ROOT / "naming"
FASE_3 = ROOT / "docs" / "collaudi" / "REL-012" / "fase-3"
CENTRALE = FASE_3 / "centrale"
PICCOLO = FASE_3 / "piccolo"
IMPIANTO = ROOT / "docs" / "collaudi" / "DRAW-018" / "prova-camera-pulita-2026-09-24"

PORTE_DELLA_POMPA_DI_CALORE = {
    "power",
    "bus",
    "comando_a_filo",
    "sonda_acs",
    "sonda_accumulo",
    "sonda_zona_2",
    "termostato",
    "out_acs",
    "out_miscelatrice",
    "out_pompa_zona_1",
    "out_pompa_zona_2",
    "out_pompa_ricircolo",
    "out_ausiliario",
}
"""La pompa di calore con la regolazione a bordo (REL-015 punto 4, I-230): proposta."""

CON_LE_PORTE_DI_COMANDO = {
    "heat-pump-air-water": PORTE_DELLA_POMPA_DI_CALORE,
    "heat-pump-air-water-large": PORTE_DELLA_POMPA_DI_CALORE,
    "dhw-heat-pump": {"power", "bus"},
    "gas-boiler": {"power", "bus"},
    "gas-boiler-modular": {"power", "bus"},
    "pump-circulator": {"power", "comando"},
    "pump-circulator-dhw": {"power", "comando"},
    "pump-circulator-solar": {"power", "comando"},
    "diverting-valve-3way": {"comando"},
    "mixing-valve-3way": {"comando"},
    "switching-valve-3way": {"comando"},
    "fan-coil": {"power", "bus"},
    "fan-coil-ducted": {"power", "bus"},
}
"""Le voci con le porte elettriche e di comando: proposta della sessione."""


@cache
def simboli() -> SymbolRegistry:
    return SymbolRegistry.from_directory(SYMBOLS)


@cache
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(CATALOG, symbols=simboli())


@cache
def centrale() -> ProjectModel:
    return load_project(CENTRALE / "grafo-completo.json")


def senza_porte_di_comando() -> tuple[ComponentRegistry, SymbolRegistry]:
    """Il catalogo e la libreria come se le porte di comando non fossero mai esistite."""
    intere = ComponentRegistry.from_directory(CATALOG)
    libreria = SymbolRegistry(
        [
            replace(item, manifest=item.manifest.model_copy(update={"control_ports": []}))
            for item in simboli().all()
        ]
    )
    voci = [
        voce.model_copy(
            update={
                "ports": [
                    porta
                    for porta in voce.ports
                    if porta.id not in simboli().get(voce.symbol_id).manifest.control_port_ids
                ]
            }
        )
        for voce in intere.all()
    ]
    return ComponentRegistry(voci, libreria), libreria


# --- le porte di comando ----------------------------------------------------------


def test_le_voci_dell_idronico_hanno_le_porte_di_comando_facoltative() -> None:
    intere = ComponentRegistry.from_directory(CATALOG)
    for voce, attese in CON_LE_PORTE_DI_COMANDO.items():
        assert catalogo().porte_di_comando(voce) == attese, voce
        porte = {porta.id: porta for porta in intere.get(voce).ports}
        for porta in attese:
            assert porte[porta].domain is Domain.CONTROL, (voce, porta)
            assert porte[porta].required is False, (voce, porta)
        # Il registro coi simboli non le mostra: la voce e' quella di prima.
        assert not attese & catalogo().get(voce).port_ids, voce
        assert not attese & catalogo().resolve(voce).symbol.manifest.port_ids, voce


def test_un_circolatore_alimentato_resta_un_pezzo_in_linea() -> None:
    """La porta di comando sta fra le `control_ports`: il circolatore resta un pezzo a
    due porte opposte che spezza la sua tubazione, e chi cerca un pezzo per fluido lo
    trova anche col cavo collegato."""
    manifesto = simboli().get("pump-circulator").manifest
    assert manifesto.is_inline and len(manifesto.ports) == 2
    # L'alimentazione e, dal collaudo T2 di REL-012, il comando dal regolatore.
    assert manifesto.control_port_ids == {"power", "comando"}
    grafo = load_project(PICCOLO / "grafo-completo.json")
    del_grafo = catalogo().per_il_progetto(grafo)
    assert "power" in del_grafo.get("pump-circulator").port_ids
    assert del_grafo.resolve("pump-circulator").is_inline
    assert "pump-circulator" in {voce.id for voce in del_grafo.serving("circulation", "heating_water")}


def test_una_porta_di_comando_obbligatoria_non_si_carica() -> None:
    intere = ComponentRegistry.from_directory(CATALOG)
    pompa = intere.get("pump-circulator")
    guasta = pompa.model_copy(
        update={
            "ports": [
                porta.model_copy(update={"required": True}) if porta.id == "power" else porta
                for porta in pompa.ports
            ]
        }
    )
    with pytest.raises(CatalogError, match="facoltativa"):
        ComponentRegistry([guasta], simboli())


def test_senza_elettrico_il_catalogo_del_grafo_e_quello_di_sempre() -> None:
    grafo = load_project(IMPIANTO / "grafo-completo-1.json")
    assert catalogo().per_il_progetto(grafo) is catalogo()
    modello, del_grafo = vista_del_grafo(grafo, "tutto", catalogo())
    assert modello is grafo and del_grafo is catalogo()


@pytest.mark.parametrize("numero", [1, 4])
def test_le_porte_non_collegate_non_cambiano_la_tavola(numero: int) -> None:
    """La tavola dell'impianto col catalogo di oggi e' quella col catalogo di prima:
    la geometria intera, byte per byte. Il banco di REL-011 lo misura su 24 tavole;
    qui due, che girano a ogni prova."""
    grafo = load_project(IMPIANTO / f"grafo-completo-{numero}.json")
    piano = carica_piano(IMPIANTO / f"piano-completo-{numero}.json")
    oggi = esegui_piano(grafo, piano, catalogo(), simboli(), NAMING)
    vecchio_catalogo, vecchia_libreria = senza_porte_di_comando()
    prima = esegui_piano(grafo, piano, vecchio_catalogo, vecchia_libreria, NAMING)
    assert oggi.disegno is not None and prima.disegno is not None
    assert oggi.disegno.model_dump_json() == prima.disegno.model_dump_json()
    assert [item.message for item in oggi.rilievi] == [item.message for item in prima.rilievi]


def test_il_cavo_di_un_pezzo_in_linea_finisce_su_di_lui() -> None:
    """Il circolatore resta in linea sulla sua tubazione, con due tubi; il suo cavo e'
    una tratta che finisce sulla sua alimentazione."""
    grafo = load_project(PICCOLO / "grafo-completo.json")
    del_grafo = catalogo().per_il_progetto(grafo)
    fermate = porte_di_comando_in_linea(grafo, del_grafo)
    assert fermate == {("circolatore", "power")}
    tratte = build_trunks(grafo, inline_component_ids(grafo, del_grafo), fermate)
    cavo = next(item for item in tratte if "e2" in item.connection_ids)
    assert cavo.connection_ids == ("e2",)
    assert {(cavo.start.component_id, cavo.start.port_id), (cavo.end.component_id, cavo.end.port_id)} == {
        ("regolatore", "out_2"),
        ("circolatore", "power"),
    }
    acqua = next(item for item in tratte if "circolatore" in item.inline_component_ids)
    assert "e2" not in acqua.connection_ids


# --- le viste ---------------------------------------------------------------------


def test_la_vista_idraulica_non_ha_il_comando() -> None:
    grafo = centrale()
    vista, _ = vista_del_grafo(grafo, "idraulica", catalogo(), NAMING)
    domini = {item.id: item.domain for item in vista.networks}
    assert Domain.CONTROL not in domini.values()
    assert all(domini[item.network_id] is not Domain.CONTROL for item in vista.connections)
    pezzi = {item.id for item in vista.components}
    assert {"quadro", "regolatore", "sezionatore-pdc", "sonda-esterna"}.isdisjoint(pezzi)
    # La sonda a immersione resta sul suo tubo: il pozzetto e' un fatto idraulico.
    assert {"sonda-mandata", "sonda-ritorno"} <= pezzi
    assert pezzi == {item.id for item in grafo.components} - solo_comando(grafo, catalogo())
    assert vista.metadata.sheet_title == "Centrale termica — idraulica"
    assert vista.metadata.sheet_number == "P.04"


def test_la_vista_elettrica_ha_solo_il_comando() -> None:
    grafo = centrale()
    vista, del_grafo = vista_del_grafo(grafo, "elettrico", catalogo(), NAMING)
    domini = {item.id: item.domain for item in vista.networks}
    assert set(domini.values()) == {Domain.CONTROL}
    assert {item.id for item in vista.components} == {
        "pdc", "circolatore", "deviatrice", "quadro", "sezionatore-pdc", "regolatore",
        "sonda-mandata", "sonda-ritorno", "sonda-esterna",
    }
    # Il circolatore non ha il suo tubo: il piano lo posa come un pezzo.
    assert not del_grafo.resolve("pump-circulator").is_inline
    assert del_grafo.resolve("isolator-switch").is_inline
    assert vista.metadata.sheet_title == "Centrale termica — elettrico e comando"
    assert vista.metadata.sheet_number == "P.04-E"


def test_le_sigle_sono_le_stesse_sulle_due_tavole() -> None:
    """Senza sigle scritte: le scrive la vista, dalla lettura del grafo intero."""
    grafo = centrale()
    senza = grafo.model_copy(
        update={"components": [item.model_copy(update={"tag": None}) for item in grafo.components]}
    )
    attese = read_plant(senza, catalogo().per_il_progetto(senza), Naming.from_directory(NAMING)).sigle
    idraulica, _ = vista_del_grafo(senza, "idraulica", catalogo(), NAMING)
    elettrico, _ = vista_del_grafo(senza, "elettrico", catalogo(), NAMING)
    sigle_i = {item.id: item.tag for item in idraulica.components if item.tag}
    sigle_e = {item.id: item.tag for item in elettrico.components if item.tag}
    assert {"pdc", "circolatore"} <= set(sigle_e)
    for pezzo, sigla in sigle_e.items():
        assert sigle_i[pezzo] == sigla == attese[pezzo], pezzo


def test_una_vista_sconosciuta_non_si_legge(tmp_path: Path) -> None:
    piano = tmp_path / "piano.json"
    piano.write_text('{"formato": "A3", "vista": "luce", "pezzi": {}}', encoding="utf-8")
    with pytest.raises(ErroreDelPiano, match="vista"):
        carica_piano(piano)


# --- le tavole di prova -----------------------------------------------------------


@pytest.mark.parametrize(
    ("caso", "piano", "tratte"),
    [
        (PICCOLO, "piano.json", 16),
        (CENTRALE, "piano-idraulica.json", 29),
        (CENTRALE, "piano-elettrico.json", 8),
    ],
)
def test_le_tavole_di_prova_escono_pulite(caso: Path, piano: str, tratte: int) -> None:
    esito = esegui_piano(
        load_project(caso / "grafo-completo.json"),
        carica_piano(caso / piano),
        catalogo(),
        simboli(),
        NAMING,
    )
    assert esito.disegno is not None, esito.errore
    assert esito.bloccanti == []
    assert esito.cedute == ()
    assert sum(len(foglio.routes) for foglio in esito.disegno.sheets) == tratte


def test_le_due_tavole_si_rimandano() -> None:
    righe = {}
    for piano in ("piano-idraulica.json", "piano-elettrico.json"):
        esito = esegui_piano(centrale(), carica_piano(CENTRALE / piano), catalogo(), simboli(), NAMING)
        assert esito.disegno is not None
        righe[piano] = [" ".join(nota.righe) for nota in esito.disegno.sheets[0].note_della_legenda]
    assert any("P.04-E" in riga and "elettrico" in riga for riga in righe["piano-idraulica.json"])
    assert any("P.04 " in riga and "idraulica" in riga for riga in righe["piano-elettrico.json"])
