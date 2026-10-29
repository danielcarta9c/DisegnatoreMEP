"""I tre comportamenti del motore del §6 del rapporto del kit (REL-012, fase 1, punto 6).

Ciascuno ha la sua prova, **rossa sul commit di partenza** (`6e04487`), e la causa
misurata prima della correzione:

1. **«Le sigle tutte o niente»** non e' quello che sembra. Le sigle automatiche non
   spariscono perche' qualche pezzo ha la sua: spariscono — tutte, e in silenzio, con
   il trattino nella tabella — quando **la lettura dell'impianto si rompe**
   (`graph.plant`), e la tabella ripiega sulle sole sigle dell'ingegnere. Sul caso del
   kit la lettura si rompeva perche' due tubazioni dell'alimentazione erano scritte al
   contrario: `ue.power -> sezionatore.b` e `sezionatore.a -> quadro.out_1`, cioe'
   dall'ingresso all'uscita. E le aveva scritte cosi' **per aggirare il terzo
   comportamento**. La validazione non lo diceva: adesso lo dice, e ferma.
2. **Il pezzo in tabella perde la sua scritta libera, e il preflight la pretende.** Un
   pezzo della tabella delle apparecchiature porta accanto la sola sigla: i suoi dati
   stanno in tabella (D-192, punto 7). Ma l'`etichetta` non e' un dato della tabella,
   e' una scritta del progettista (I-194), e restava fuori dalla tavola mentre
   `FREE_LABEL_OMITTED` la pretendeva: la tavola non usciva. Succede anche
   sull'idronico.
3. **Il lato dell'organo in linea dipendeva dall'ordine delle tubazioni.** Un organo
   che non e' della catena di una macchina si posa dal capo da cui la tratta comincia,
   e la tratta comincia dalla prima tubazione del modello. Il sezionatore di
   prossimita' deve stare accanto alla macchina che alimenta **per mestiere**
   (`power_isolation`), non per come si chiamano le tubazioni.
"""

import json
from collections.abc import Callable
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph.naming import Naming
from disegnatore_mep.graph.plant import read_plant
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.tabella import tabella_della_tavola
from disegnatore_mep.layout.geometry import SheetGeometry
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.piano.esecutore import esegui_piano
from disegnatore_mep.piano.formato import PianoDiComposizione, carica_piano
from disegnatore_mep.validation.topology import validate_project

ROOT = Path(__file__).resolve().parents[2]
APPROVATI = ROOT / "docs" / "collaudi" / "DRAW-018" / "prova-camera-pulita-2026-09-24"
TABELLA = json.loads((ROOT / "docs" / "collaudi" / "REL-006" / "dati-di-prova.json").read_text("utf-8"))
NAMING = ROOT / "naming"

RETI_ELETTRICHE = {
    "liquido": ("refrigerant", "refrigerant_liquid"),
    "gas": ("refrigerant", "refrigerant_gas"),
    "collegamento": ("control", "interconnection"),
    "alimentazione": ("control", "power_supply"),
}


def _impianto_1(**ritocchi: dict[str, object]) -> ProjectModel:
    """L'impianto 1 approvato, con i dati della tabella di REL-006 e qualche ritocco."""
    grafo = json.loads((APPROVATI / "grafo-completo-1.json").read_text(encoding="utf-8"))
    pezzi = {item["id"]: item for item in grafo["components"]}
    for ident, proprieta in TABELLA["impianti"]["1"].items():
        pezzi[ident]["properties"].update(proprieta)
    for ident, proprieta in ritocchi.items():
        pezzi[ident]["properties"].update(proprieta)
    return ProjectModel.model_validate(grafo)


# --- 1. le sigle -------------------------------------------------------------------


def _alimentazione(progetto: Callable[..., ProjectModel], tubi: list[tuple[str, ...]], sigle: bool) -> ProjectModel:
    return progetto(
        RETI_ELETTRICHE,
        {
            "ue": ("split-outdoor-unit", {}, "UE-01" if sigle else None),
            "ui": ("ducted-indoor-unit", {}, None),
            "quadro": ("electrical-panel", {}, "QE-01"),
            "sezionatore": "isolator-switch",
        },
        [
            ("r-liq", "liquido", "ue.liquid", "ui.liquid"),
            ("r-gas", "gas", "ue.gas", "ui.gas"),
            ("e-link", "collegamento", "ue.link", "ui.link"),
            *tubi,
        ],
    )


def test_una_tubazione_scritta_al_contrario_si_ferma_alla_validazione(
    catalogo_aria: ComponentRegistry, progetto: Callable[..., ProjectModel]
) -> None:
    """Il caso del kit: l'alimentazione scritta dall'ingresso della macchina verso il
    quadro. La lettura dell'impianto la rifiuta (`graph.plant`), la tabella ripiega
    sulle sole sigle date e mette il trattino agli altri; la validazione la lasciava
    passare. **Rossa sul commit di partenza**: nessun rilievo."""
    al_contrario = _alimentazione(
        progetto,
        [
            ("e-1a", "alimentazione", "ue.power", "sezionatore.b"),
            ("e-1b", "alimentazione", "sezionatore.a", "quadro.out_1"),
        ],
        sigle=True,
    )
    esito = validate_project(al_contrario, catalogo_aria)
    contrari = [item for item in esito.issues if item.code == "CONNECTION_WRITTEN_BACKWARDS"]
    assert {item.entity_ids[0] for item in contrari} == {"e-1a", "e-1b"}, esito.issues
    assert all(item.severity.value == "blocking" for item in contrari)
    assert "al contrario" in contrari[0].message


def test_l_idronico_scritto_al_contrario_si_ferma_anche_lui(catalogo_aria: ComponentRegistry) -> None:
    """La stessa cosa sull'impianto 1 approvato: la mandata della pompa di calore
    capovolta. Prima nessun rilievo, e la tabella perdeva le sigle che non sono
    dell'ingegnere. **Rossa sul commit di partenza.**"""
    grafo = json.loads((APPROVATI / "grafo-completo-1.json").read_text(encoding="utf-8"))
    tubo = next(item for item in grafo["connections"] if item["id"] == "p1-a-a-1")
    tubo["endpoint_a"], tubo["endpoint_b"] = tubo["endpoint_b"], tubo["endpoint_a"]
    esito = validate_project(ProjectModel.model_validate(grafo), catalogo_aria)
    assert [item.entity_ids[0] for item in esito.issues if item.code == "CONNECTION_WRITTEN_BACKWARDS"] == [
        "p1-a-a-1"
    ]


def test_le_sigle_automatiche_non_sono_tutte_o_niente(
    catalogo_aria: ComponentRegistry, progetto: Callable[..., ProjectModel]
) -> None:
    """Con l'alimentazione scritta nel verso del fluido, i pezzi senza sigla prendono
    quella della famiglia accanto a quelli che l'hanno: e' la regola di sempre (D-097,
    D-098), e sul commit di partenza vale gia'. E' la prova che il §6.1 del kit era la
    lettura rotta, non le sigle."""
    dritto = _alimentazione(
        progetto,
        [
            ("e-1a", "alimentazione", "quadro.out_1", "sezionatore.a"),
            ("e-1b", "alimentazione", "sezionatore.b", "ue.power"),
        ],
        sigle=False,
    )
    # La UI qui non ha aria, condensa e comando: mancano i suoi attacchi obbligatori, e
    # la validazione lo dice. Di versi sbagliati, nessuno.
    codici = {item.code for item in validate_project(dritto, catalogo_aria).issues}
    assert codici == {"REQUIRED_PORT_UNCONNECTED"}, codici
    sigle = read_plant(dritto, catalogo_aria, Naming.from_directory(NAMING)).sigle
    assert sigle["quadro"] == "QE-01"
    assert sigle["ue"] == "UE-01" and sigle["ui"] == "UI-01" and sigle["sezionatore"] == "SZ-01"


def test_la_tabella_dell_impianto_1_ha_tutti_i_codici(
    catalogo_aria: ComponentRegistry, simboli_aria: SymbolRegistry
) -> None:
    """Sull'impianto 1 le sigle sono in parte dell'ingegnere e in parte della famiglia:
    la tabella le ha tutte. E' il riferimento della prova qui sopra."""
    modello = _impianto_1()
    piano = carica_piano(APPROVATI / "piano-completo-1.json")
    esito = esegui_piano(modello, piano, catalogo_aria, simboli_aria, NAMING)
    assert esito.disegno is not None
    foglio = esito.disegno.sheets[0]
    assert foglio.tabella is not None
    assert all(riga.codice for riga in foglio.tabella.righe), foglio.tabella.righe
    scritte = {item.tag for item in modello.components}
    assert any(riga.codice not in scritte for riga in foglio.tabella.righe), "ce n'e' una della famiglia"
    tabella = tabella_della_tavola(modello, catalogo_aria, NAMING, foglio, esito.frame)
    assert tabella is not None and tabella.righe == foglio.tabella.righe


# --- 2. la scritta libera di un pezzo che sta in tabella ---------------------------


def test_il_pezzo_in_tabella_porta_la_sua_scritta_libera(
    catalogo_aria: ComponentRegistry, simboli_aria: SymbolRegistry
) -> None:
    """La pompa di calore dell'impianto 1 sta nella tabella, e il progettista le da'
    una scritta: «sul tetto». **Rossa sul commit di partenza**: la scritta non si
    scriveva, e il preflight fermava la tavola con `FREE_LABEL_OMITTED`. I dati della
    tabella — potenza, marca, modello — restano solo in tabella (D-192, punto 7)."""
    modello = _impianto_1(**{"pdc-master": {"etichetta": "sul tetto"}})
    esito = esegui_piano(
        modello, carica_piano(APPROVATI / "piano-completo-1.json"), catalogo_aria, simboli_aria, NAMING
    )
    assert esito.disegno is not None
    foglio = esito.disegno.sheets[0]
    assert foglio.tabella is not None and "pdc-master" in {riga.component_id for riga in foglio.tabella.righe}
    scritte = {label.id: label.text for label in foglio.labels}
    assert scritte.get("pdc-master-etichetta") == "sul tetto"
    assert "pdc-master-power_kw" not in scritte and "pdc-master-marca" not in scritte
    assert not [item.code for item in esito.rilievi if item.code == "FREE_LABEL_OMITTED"]


# --- 3. il lato del sezionatore ----------------------------------------------------

PIANO_DEL_SEZIONATORE = PianoDiComposizione.model_validate(
    {
        "formato": "A3",
        "pezzi": {
            "ue": {"x": 60, "y": 60, "rotazione": 0},
            "ui": {"x": 170, "y": 60, "rotazione": 0},
            "quadro": {"x": 62.5, "y": 200, "rotazione": 0},
        },
    }
)


def _dove_sta_il_sezionatore(
    progetto: Callable[..., ProjectModel],
    catalogo: ComponentRegistry,
    simboli: SymbolRegistry,
    tubi: list[tuple[str, ...]],
) -> tuple[float, float]:
    """Le distanze del centro del sezionatore dall'attacco della macchina e da quello
    del quadro, lungo la verticale che li unisce."""
    modello = _alimentazione(progetto, tubi, sigle=True)
    esito = esegui_piano(modello, PIANO_DEL_SEZIONATORE, catalogo, simboli, NAMING)
    assert esito.disegno is not None, esito.errore
    foglio: SheetGeometry = esito.disegno.sheets[0]
    posati = {item.component_id: item for item in foglio.symbols}
    sez, ue, quadro = posati["sezionatore"], posati["ue"], posati["quadro"]
    centro = sez.origin.y_mm + sez.height_mm / 2
    return centro - ue.bottom_mm, quadro.origin.y_mm - centro


def test_il_sezionatore_sta_dalla_parte_della_macchina_comunque_si_chiamino_i_tubi(
    progetto: Callable[..., ProjectModel], catalogo_aria: ComponentRegistry, simboli_aria: SymbolRegistry
) -> None:
    """Le stesse due tubazioni, nei due ordini. **Rossa sul commit di partenza**: col
    tubo del quadro per primo il sezionatore finiva accanto al quadro, a 125 mm dalla
    macchina; con quello della macchina per primo, accanto alla macchina."""
    dal_quadro = [
        ("e-1a", "alimentazione", "quadro.out_1", "sezionatore.a"),
        ("e-1b", "alimentazione", "sezionatore.b", "ue.power"),
    ]
    dalla_macchina = [dal_quadro[1], dal_quadro[0]]
    for tubi in (dal_quadro, dalla_macchina):
        dalla_ue, dal_quadro_mm = _dove_sta_il_sezionatore(progetto, catalogo_aria, simboli_aria, tubi)
        assert dalla_ue < dal_quadro_mm, (tubi[0][0], dalla_ue, dal_quadro_mm)
        assert dalla_ue <= 10.0, (tubi[0][0], dalla_ue)
