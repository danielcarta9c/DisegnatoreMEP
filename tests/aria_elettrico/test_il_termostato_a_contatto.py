"""Il termostato ambiente a contatto sulla linea del circolatore (I-269).

Il PO, da una commessa reale: la pompa di calore regola da se', e il circolatore del
secondario prende l'alimentazione dal quadro **attraverso il contatto del termostato
ambiente**. Il catalogo aveva solo il termostato di zona su bus, e il ripiego con una
`scritta` lasciava una linea che «attraversa un pezzo che non c'e'».

Tre cose:

1. **il grafo minimo** (`docs/collaudi/REL-017/termostato/`) — quadro, termostato a
   contatto, circolatore, e la pompa di calore col suo circuito — si valida, si completa e
   si disegna pulito sulla tavola dell'elettrico: TAC-01 in tabella e in legenda, nessun
   relè aggiunto, e sulla tavola idraulica il termostato non c'e';
2. **il vecchio termostato su un'alimentazione resta un errore** (`PORT_MEDIUM_MISMATCH`):
   la voce nuova non ha allargato quella di prima;
3. **le istruzioni** di Capire, Comporre e il corredo della distinta lo dicono.
"""
# categoria: difende il motore

import json
from functools import cache
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph import Naming, read_plant
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import Domain, IssueSeverity
from disegnatore_mep.piano.esecutore import EsitoDelPiano, esegui_piano
from disegnatore_mep.piano.formato import carica_piano
from disegnatore_mep.piano.vista import vista_del_grafo
from disegnatore_mep.validation.topology import validate_project

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
NAMING = ROOT / "naming"
CASO = ROOT / "docs" / "collaudi" / "REL-017" / "termostato"
CAPIRE = ROOT / "skill" / "capire" / "ISTRUZIONI.md"
COMPORRE = ROOT / "skill" / "comporre" / "ISTRUZIONI.md"
CORREDO = ROOT / "rules" / "distinta" / "corredo.json"
VOCE = "room-thermostat-contact"


@cache
def simboli() -> SymbolRegistry:
    return SymbolRegistry.from_directory(SYMBOLS)


@cache
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(CATALOG, symbols=simboli())


@cache
def tavola() -> EsitoDelPiano:
    esito = esegui_piano(
        load_project(CASO / "grafo-completo.json"),
        carica_piano(CASO / "piano-elettrico.json"),
        catalogo(),
        simboli(),
        NAMING,
    )
    assert esito.disegno is not None, esito.errore
    return esito


def _bloccanti(grafo: ProjectModel) -> list[tuple[str, str]]:
    rilievi = validate_project(grafo, catalogo().per_il_progetto(grafo))
    return [
        (item.code, item.message) for item in rilievi.issues if item.severity is IssueSeverity.BLOCKING
    ]


# --- la voce ---------------------------------------------------------------------------


def test_la_voce_e_un_passante_dell_alimentazione() -> None:
    """Due attacchi a 230 V, ingresso e uscita, come il sezionatore; il comando d'ambiente fra
    i mestieri, e **non** quello del relè: la lettura dell'impianto chiama KA-<carico> chi
    fa `power_switching` (I-267), e il termostato non e' un relè."""
    voce = ComponentRegistry.from_directory(CATALOG).get(VOCE)
    assert voce.name == "Termostato ambiente a contatto"
    assert "room_control" in voce.functions
    assert "power_switching" not in voce.functions
    porte = {porta.id: porta for porta in voce.ports}
    assert set(porte) == {"a", "b"}
    for nome, verso in (("a", "in"), ("b", "out")):
        assert porte[nome].domain is Domain.CONTROL
        assert (porte[nome].medium, porte[nome].flow.value) == ("power_supply", verso)
        assert porte[nome].required is True
    # In linea, come il sezionatore: il motore lo posa sul suo cavo.
    assert catalogo().resolve(VOCE).is_inline
    manifesto = simboli().get(VOCE).manifest
    assert {(porta.id, porta.face.value) for porta in manifesto.ports} == {("a", "left"), ("b", "right")}
    assert manifesto.allowed_rotations_deg == simboli().get("isolator-switch").manifest.allowed_rotations_deg


def test_la_sigla_e_tac_e_non_quella_del_termostato_di_zona() -> None:
    naming = Naming.from_directory(NAMING)
    voce = ComponentRegistry.from_directory(CATALOG).get(VOCE)
    assert naming.family_of(tuple(voce.functions), VOCE).prefix == "TAC"
    # Il termostato di zona resta TZ.
    vecchio = ComponentRegistry.from_directory(CATALOG).get("room-thermostat")
    assert naming.family_of(tuple(vecchio.functions), "room-thermostat").prefix == "TZ"


# --- 1. il grafo minimo -------------------------------------------------------------------


def test_il_grafo_minimo_si_valida_e_il_completo_e_la_rigenerazione() -> None:
    for nome in ("grafo.json", "grafo-completo.json"):
        assert _bloccanti(load_project(CASO / nome)) == [], nome
    grafo = load_project(CASO / "grafo-completo.json")
    voci = {item.id: item.definition_id for item in grafo.components}
    # Le regole non aggiungono un relè: il circolatore non e' comandato dalla pompa di calore.
    assert "interface-relay" not in voci.values()
    assert voci["termostato"] == VOCE
    cavi = {
        frozenset({(t.endpoint_a.component_id, t.endpoint_a.port_id), (t.endpoint_b.component_id, t.endpoint_b.port_id)})
        for t in grafo.connections
    }
    assert frozenset({("quadro", "out_3"), ("termostato", "a")}) in cavi
    assert frozenset({("termostato", "b"), ("circ", "power")}) in cavi
    assert not any(("circ", "comando") in cavo for cavo in cavi)
    # Una rete sola per la linea del circolatore.
    reti = {t.network_id for t in grafo.connections if "termostato" in {t.endpoint_a.component_id, t.endpoint_b.component_id}}
    assert len(reti) == 1


def test_la_sigla_del_termostato_e_tac_01() -> None:
    grafo = load_project(CASO / "grafo-completo.json")
    sigle = read_plant(grafo, catalogo().per_il_progetto(grafo), Naming.from_directory(NAMING)).sigle
    assert sigle["termostato"] == "TAC-01"
    assert not any(sigla.startswith("KA-") for sigla in sigle.values())


def test_la_tavola_dell_elettrico_esce_pulita_col_termostato_in_tabella_e_in_legenda() -> None:
    esito = tavola()
    bloccanti = [item.message for item in esito.rilievi if item.severity is IssueSeverity.BLOCKING]
    assert bloccanti == []
    assert not esito.cedute
    foglio = esito.disegno.sheets[0]  # type: ignore[union-attr]
    assert foglio.tabella is not None
    righe = {riga.codice: riga for riga in foglio.tabella.righe}
    assert righe["TAC-01"].descrizione == "Termostato ambiente a contatto"
    # La portata del contatto, come l'ha data il progettista: e' un dato elettrico (I-277).
    assert righe["TAC-01"].caratteristiche == "5(2) A 250 V"
    assert {"GT-01", "CIR-01", "QE-01", "TAC-01"} == set(righe)
    # I dati idronici non si scrivono sulla tavola dell'elettrico (I-277): i 12 kW termici
    # della pompa di calore restano sulla tavola idraulica, e senza dati elettrici la cella
    # ha il trattino.
    assert righe["GT-01"].caratteristiche is None
    assert (VOCE, "Termostato ambiente a contatto") in {(voce.symbol_id, voce.name) for voce in foglio.legend}
    testi = {label.text for label in foglio.labels}
    assert {"TAC-01", "soggiorno"} <= testi
    # Il termostato sta in linea sul cavo, posato dal motore.
    simbolo = next(item for item in foglio.symbols if item.component_id == "termostato")
    assert simbolo.symbol_id == VOCE


def test_sulla_tavola_idraulica_il_termostato_non_c_e() -> None:
    grafo = load_project(CASO / "grafo-completo.json")
    idraulica, _ = vista_del_grafo(grafo, "idraulica", catalogo(), NAMING)
    assert "termostato" not in {item.id for item in idraulica.components}
    elettrico, _ = vista_del_grafo(grafo, "elettrico", catalogo(), NAMING)
    assert "termostato" in {item.id for item in elettrico.components}


# --- 2. il vecchio termostato resta sul bus -------------------------------------------------


def _col_vecchio_termostato() -> ProjectModel:
    """Il ripiego di prima: il termostato di zona, che ha un attacco solo sul bus, in mezzo
    alla linea del circolatore."""
    grafo = json.loads((CASO / "grafo.json").read_text(encoding="utf-8"))
    for pezzo in grafo["components"]:
        if pezzo["id"] == "termostato":
            pezzo["definition_id"] = "room-thermostat"
            pezzo["properties"] = {}
    for tubazione in grafo["connections"]:
        for capo in ("endpoint_a", "endpoint_b"):
            if tubazione[capo]["component_id"] == "termostato":
                tubazione[capo]["port_id"] = "a"
    return ProjectModel.model_validate(grafo)


def test_il_termostato_di_zona_su_un_alimentazione_resta_un_errore() -> None:
    codici = {codice for codice, _ in _bloccanti(_col_vecchio_termostato())}
    assert "PORT_MEDIUM_MISMATCH" in codici


def test_il_termostato_di_zona_sul_comando_del_circolatore_resta_un_errore() -> None:
    """Il primo tentativo della commessa: il termostato sul `comando` del circolatore."""
    grafo = json.loads((CASO / "grafo.json").read_text(encoding="utf-8"))
    grafo["components"] = [p for p in grafo["components"] if p["id"] != "termostato"]
    grafo["components"].append({"id": "termostato", "definition_id": "room-thermostat", "tag": None, "properties": {}})
    grafo["connections"] = [
        t for t in grafo["connections"] if "termostato" not in {t["endpoint_a"]["component_id"], t["endpoint_b"]["component_id"]}
    ]
    grafo["connections"].append(
        {
            "id": "t9",
            "network_id": "el-circ",
            "endpoint_a": {"component_id": "termostato", "port_id": "a"},
            "endpoint_b": {"component_id": "circ", "port_id": "comando"},
            "properties": {},
        }
    )
    codici = {codice for codice, _ in _bloccanti(ProjectModel.model_validate(grafo))}
    assert "PORT_MEDIUM_MISMATCH" in codici


# --- 3. le istruzioni e il corredo -----------------------------------------------------------


def test_capire_dice_quando_si_usa_il_termostato_a_contatto() -> None:
    testo = CAPIRE.read_text(encoding="utf-8")
    for parola in (VOCE, "I-269", "Termostato ambiente a contatto", "`passante`", "PORT_MEDIUM_MISMATCH"):
        assert parola in testo, parola
    # Il relè resta per il circolatore comandato da un'uscita della pompa di calore.
    assert "Il relè è obbligatorio solo quando il circolatore è comandato da un'uscita della" in testo
    assert "domanda al progettista" in testo


def test_comporre_dice_dove_sta_il_termostato_sulla_tavola_dell_elettrico() -> None:
    testo = COMPORRE.read_text(encoding="utf-8")
    assert VOCE in testo
    assert "TAC-01" in testo
    assert "termostato ambiente a contatto" in testo.lower()


def test_il_corredo_ha_la_scatola_e_il_termostato_e_passante() -> None:
    corredo = json.loads(CORREDO.read_text(encoding="utf-8"))
    voce = corredo["voci"][VOCE]
    assert voce["passante"] is True
    assert "scatola-503" in {item["id"] for item in voce["voci"]}
    assert "andata e ritorno" in voce["perche"]
