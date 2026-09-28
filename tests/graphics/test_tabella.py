"""La tabella delle apparecchiature, in alto a sinistra (REL-006, I-141, I-144).

Che cosa dice — i pezzi che fanno un mestiere da apparecchiatura principale, e i vasi,
con la loro sigla —, che **non inventa niente** — un dato che il grafo non ha e' una
cella vuota —, che **il disegno non ci passa sopra**, e che il DXF la porta uguale
all'SVG. Le misure sulle tavole approvate leggono i grafi e i piani agli atti, come le
altre prove dell'esecutore.
"""

import json
import re
from pathlib import Path

import ezdxf
import pytest
from pydantic import ValidationError

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph.naming import Naming
from disegnatore_mep.graph.plant import read_plant
from disegnatore_mep.graphics.dxf import ALTEZZA_MAIUSCOLE_EM, LAYER_TABELLA, write_dxf
from disegnatore_mep.graphics.frame import NOVE_C_A2, NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import render_sheet
from disegnatore_mep.graphics.tabella import (
    CELLA_VUOTA,
    FUNZIONI_DELLA_TABELLA,
    INTESTAZIONE,
    celle,
    formatta_il_dato,
    impagina_la_tabella,
    righe_della_tabella,
    tratti_della_tabella,
)
from disegnatore_mep.layout.compose import sgombra_la_tabella
from disegnatore_mep.layout.geometry import (
    DrawingGeometry,
    PlacedSymbol,
    Point,
    RigaDellaTabella,
    RoutedTrunk,
    SheetGeometry,
    TabellaDelleApparecchiature,
    zona_della_tabella,
)
from disegnatore_mep.layout.labels import place_labels, text_width_mm
from disegnatore_mep.model.project import ComponentInstance, ProjectModel
from disegnatore_mep.piano.esecutore import EsitoDelPiano, esegui_piano
from disegnatore_mep.piano.formato import carica_piano
from disegnatore_mep.validation import preflight

ROOT = Path(__file__).resolve().parents[2]
SYMBOLS = ROOT / "assets" / "symbols"
CATALOG = ROOT / "examples" / "layout" / "catalog"
NAMING = ROOT / "naming"
APPROVATI = ROOT / "docs" / "collaudi" / "DRAW-018" / "prova-camera-pulita-2026-09-24"
IMPIANTO_6 = ROOT / "docs" / "collaudi" / "REL-003" / "impianto-6"
DATI_DELLA_TABELLA = ROOT / "docs" / "collaudi" / "REL-006" / "dati-di-prova.json"

TAVOLE_APPROVATE = [
    *(
        (n, APPROVATI / f"grafo-completo-{n}.json", APPROVATI / f"piano-completo-{n}.json")
        for n in ("1", "2", "3", "4", "5")
    ),
    ("6", IMPIANTO_6 / "grafo-completo-6.json", IMPIANTO_6 / "piano-6-a.json"),
]


@pytest.fixture(scope="module")
def simboli() -> SymbolRegistry:
    return SymbolRegistry.from_directory(SYMBOLS)


@pytest.fixture(scope="module")
def catalogo(simboli: SymbolRegistry) -> ComponentRegistry:
    return ComponentRegistry.from_directory(CATALOG, symbols=simboli)


def _modello(grafo: Path, impianto: str | None = None) -> ProjectModel:
    """Il grafo agli atti; con `impianto`, piu' i dati di prova della tabella."""
    documento = json.loads(grafo.read_text(encoding="utf-8"))
    if impianto is not None:
        dati = json.loads(DATI_DELLA_TABELLA.read_text(encoding="utf-8"))["impianti"][impianto]
        pezzi = {item["id"]: item for item in documento["components"]}
        for identificativo, proprieta in dati.items():
            pezzi[identificativo]["properties"].update(proprieta)
    return ProjectModel.model_validate(documento)


def _esegui(
    modello: ProjectModel, piano: Path, catalogo: ComponentRegistry, simboli: SymbolRegistry
) -> EsitoDelPiano:
    esito = esegui_piano(modello, carica_piano(piano), catalogo, simboli, NAMING)
    assert esito.disegno is not None, esito.errore
    return esito


def _foglio(esito: EsitoDelPiano) -> SheetGeometry:
    assert esito.disegno is not None
    (foglio,) = esito.disegno.sheets
    return foglio


@pytest.fixture(scope="module")
def tavola_1(catalogo: ComponentRegistry, simboli: SymbolRegistry) -> tuple[ProjectModel, EsitoDelPiano]:
    """L'impianto 1 com'e' agli atti: nessun dato tecnico nel grafo."""
    modello = _modello(APPROVATI / "grafo-completo-1.json")
    return modello, _esegui(modello, APPROVATI / "piano-completo-1.json", catalogo, simboli)


@pytest.fixture(scope="module")
def tavola_1_coi_dati(
    catalogo: ComponentRegistry, simboli: SymbolRegistry
) -> tuple[ProjectModel, EsitoDelPiano]:
    modello = _modello(APPROVATI / "grafo-completo-1.json", "1")
    return modello, _esegui(modello, APPROVATI / "piano-completo-1.json", catalogo, simboli)


# --- che cosa dice --------------------------------------------------------------------


def test_le_righe_sono_le_apparecchiature_principali_e_i_vasi_e_niente_valvole(
    tavola_1: tuple[ProjectModel, EsitoDelPiano], catalogo: ComponentRegistry
) -> None:
    """I-141: «solo le apparecchiature principali, e vaso espansione, no valvole». Nella
    tabella c'e' **ogni** pezzo disegnato che fa uno di quei mestieri, e nessun altro:
    ne' valvole ne' filtri, strumenti, raccordi, confini — ne' i radiatori, che sono le
    utenze (proposta da giudicare sulla tavola)."""
    modello, esito = tavola_1
    tabella = _foglio(esito).tabella
    assert tabella is not None
    attesi = {
        item.id
        for item in modello.components
        if set(catalogo.get(item.definition_id).functions) & set(FUNZIONI_DELLA_TABELLA)
    }
    assert {riga.component_id for riga in tabella.righe} == attesi
    assert attesi == {"pdc-master", "pdc-slave", "accumulo", "circolatore",
                      "expansion-connection-collettore-ritorno-a"}
    for riga in tabella.righe:
        mestieri = catalogo.get(
            next(item for item in modello.components if item.id == riga.component_id).definition_id
        ).functions
        assert not any("valve" in item or item in {"isolation", "non_return", "safety"} for item in mestieri)


def test_il_codice_e_la_sigla_che_il_disegno_scrive_accanto_al_pezzo(
    tavola_1: tuple[ProjectModel, EsitoDelPiano], catalogo: ComponentRegistry
) -> None:
    """Una numerazione sola (D-097): il codice della tabella e' la sigla della lettura
    dell'impianto — quella dell'ingegnere, o quella della famiglia —, e la stessa sigla
    e' scritta sul disegno accanto al pezzo. Il vaso dell'impianto 1 non aveva sigla sul
    disegno: adesso porta VE-01, come nella tabella."""
    modello, esito = tavola_1
    foglio = _foglio(esito)
    assert foglio.tabella is not None
    sigle = read_plant(modello, catalogo, Naming.from_directory(NAMING)).sigle
    scritte = {label.id: label.text for label in foglio.labels if label.role == "tag"}
    for riga in foglio.tabella.righe:
        assert riga.codice == sigle[riga.component_id]
        assert scritte.get(f"{riga.component_id}-tag") == riga.codice, riga.component_id
    assert scritte["expansion-connection-collettore-ritorno-a-tag"] == "VE-01"


def test_nr_distingue_due_apparecchiature_con_lo_stesso_nome(
    tavola_1: tuple[ProjectModel, EsitoDelPiano],
) -> None:
    """«pompa di calore aria acqua nr 1» (I-141): «nr» quando le voci sono piu' d'una,
    nell'ordine delle sigle; una voce sola non lo porta."""
    tabella = _foglio(tavola_1[1]).tabella
    assert tabella is not None
    descrizioni = {riga.codice: riga.descrizione for riga in tabella.righe}
    assert descrizioni["PDC-01"] == "Pompa di calore aria-acqua nr 1"
    assert descrizioni["PDC-02"] == "Pompa di calore aria-acqua nr 2"
    assert descrizioni["ACC-01"] == "Accumulo combinato"
    assert [riga.codice for riga in tabella.righe] == ["PDC-01", "PDC-02", "ACC-01", "CIR-01", "VE-01"]


def test_una_cella_senza_dato_nel_grafo_resta_vuota(
    tavola_1: tuple[ProjectModel, EsitoDelPiano], simboli: SymbolRegistry
) -> None:
    """**Criterio 2 di REL-006**: niente dati inventati. Il grafo dell'impianto 1 non ha
    ne' potenze ne' volumi ne' marche: caratteristiche, marca e modello sono vuoti su ogni
    riga, e la tavola scrive un trattino — non un numero, non un nome."""
    modello, esito = tavola_1
    foglio = _foglio(esito)
    assert foglio.tabella is not None
    for riga in foglio.tabella.righe:
        assert (riga.caratteristiche, riga.marca, riga.modello) == (None, None, None)
        assert celle(riga)[2:] == (CELLA_VUOTA, CELLA_VUOTA, CELLA_VUOTA)
    svg = render_sheet(foglio, esito.frame, simboli)
    blocco = re.search(r'<g class="tabella-apparecchiature".*?</g>', svg)
    assert blocco is not None
    testi = re.findall(r">([^<]+)</text>", blocco.group(0))
    assert testi.count(CELLA_VUOTA) == 3 * len(foglio.tabella.righe)
    assert not any(re.search(r"\d\s*(kW|l|m³/h|kPa)\b", testo) for testo in testi)


def test_un_dato_scritto_a_parole_non_entra_nella_tabella(
    catalogo: ComponentRegistry, simboli: SymbolRegistry
) -> None:
    """L'impianto 6 porta nel grafo «potenza»: «120 kW» come testo libero, com'era
    scritto prima delle chiavi fisse. La tabella legge solo le chiavi fisse e non prova
    a indovinare un numero da un testo: la cella resta vuota."""
    modello = _modello(IMPIANTO_6 / "grafo-completo-6.json")
    pdc = next(item for item in modello.components if item.id == "pdc")
    assert pdc.properties["potenza"] == "120 kW"
    tabella = _foglio(_esegui(modello, IMPIANTO_6 / "piano-6-a.json", catalogo, simboli)).tabella
    assert tabella is not None
    riga = next(item for item in tabella.righe if item.component_id == "pdc")
    assert riga.caratteristiche is None


def test_le_caratteristiche_dipendono_dal_mestiere(
    tavola_1_coi_dati: tuple[ProjectModel, EsitoDelPiano],
) -> None:
    """La potenza dei generatori, il volume di accumuli e vasi, portata e prevalenza dei
    circolatori; marca e modello come il progettista li ha scritti."""
    tabella = _foglio(tavola_1_coi_dati[1]).tabella
    assert tabella is not None
    per_codice = {riga.codice: riga for riga in tabella.righe}
    assert per_codice["PDC-01"].caratteristiche == "15 kW"
    assert per_codice["ACC-01"].caratteristiche == "800 l"
    assert per_codice["CIR-01"].caratteristiche == "2,5 m³/h · 60 kPa"
    assert per_codice["VE-01"].caratteristiche == "24 l"
    assert (per_codice["PDC-02"].marca, per_codice["PDC-02"].modello) == ("Marca di prova", "PRV-PDC-15")


def test_i_numeri_si_scrivono_all_italiana_con_la_loro_unita() -> None:
    assert formatta_il_dato("power_kw", 15) == "15 kW"
    assert formatta_il_dato("power_kw", 1.9) == "1,9 kW"
    assert formatta_il_dato("flow_rate_m3h", 2.5) == "2,5 m³/h"
    assert formatta_il_dato("head_m", 6) == "6 m c.a."
    assert formatta_il_dato("volume_l", 1500) == "1500 l"
    assert formatta_il_dato("potenza", 15) is None
    assert formatta_il_dato("power_kw", True) is None


def test_un_pezzo_che_genera_e_accumula_porta_potenza_e_volume(
    catalogo: ComponentRegistry,
) -> None:
    """Il boiler in pompa di calore genera e accumula (impianto 3): le due caratteristiche,
    nell'ordine delle chiavi."""
    modello = _modello(APPROVATI / "grafo-completo-3.json", "3")
    righe = righe_della_tabella(
        modello, catalogo, Naming.from_directory(NAMING), {}, (item.id for item in modello.components)
    )
    boiler = next(riga for riga in righe if riga.component_id == "boiler")
    assert boiler.caratteristiche == "1,9 kW · 200 l"


def test_i_dati_della_tabella_non_si_ripetono_accanto_al_pezzo(
    tavola_1_coi_dati: tuple[ProjectModel, EsitoDelPiano],
) -> None:
    """Il pezzo della tabella porta sul disegno la sola sigla: «15 kW» accanto alla pompa
    di calore ripeterebbe la tabella, e il testo accanto a un pezzo si scrive solo se
    aggiunge informazione (D-052)."""
    foglio = _foglio(tavola_1_coi_dati[1])
    assert foglio.tabella is not None
    in_tabella = {riga.component_id for riga in foglio.tabella.righe}
    valori = [label for label in foglio.labels if label.role == "data"]
    assert not any(label.id.rsplit("-", 1)[0] in in_tabella for label in valori)
    assert not any(label.text.endswith((" kW", " l", " kPa")) for label in foglio.labels)


# --- il modello ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "proprieta",
    [
        {"power_kw": "15 kW"},
        {"power_kw": 0},
        {"volume_l": -5},
        {"head_kpa": True},
        {"marca": ""},
        {"modello": 12},
    ],
)
def test_un_dato_con_nome_fisso_ha_la_forma_che_il_nome_promette(proprieta: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        ComponentInstance.model_validate(
            {"id": "pdc", "definition_id": "heat-pump-air-water", "properties": proprieta}
        )


def test_le_altre_proprieta_restano_libere() -> None:
    pezzo = ComponentInstance.model_validate(
        {
            "id": "pdc",
            "definition_id": "heat-pump-air-water",
            "properties": {"potenza": "15 kW", "tipo": "aria-acqua", "power_kw": 15, "marca": "X"},
        }
    )
    assert pezzo.properties["potenza"] == "15 kW"


# --- il posto sul foglio ---------------------------------------------------------------


def _ingombri(foglio: SheetGeometry, corpo: float) -> list[tuple[str, tuple[float, float, float, float]]]:
    elenco: list[tuple[str, tuple[float, float, float, float]]] = [
        (item.component_id, (item.origin.x_mm, item.origin.y_mm, item.right_mm, item.bottom_mm))
        for item in foglio.symbols
    ]
    for route in foglio.routes:
        for segment in route.segments:
            for a, b in zip(segment, segment[1:], strict=False):
                elenco.append(
                    (route.network_id, (min(a.x_mm, b.x_mm), min(a.y_mm, b.y_mm), max(a.x_mm, b.x_mm), max(a.y_mm, b.y_mm)))
                )
    for label in foglio.labels:
        elenco.append(
            (label.id, (label.anchor.x_mm, label.anchor.y_mm - corpo,
                        label.anchor.x_mm + text_width_mm(label.text, corpo), label.anchor.y_mm))
        )
        if label.leader_from is not None:
            a, b = label.leader_from, label.anchor
            elenco.append((label.id, (min(a.x_mm, b.x_mm), min(a.y_mm, b.y_mm), max(a.x_mm, b.x_mm), max(a.y_mm, b.y_mm))))
    return elenco


def _dentro(box: tuple[float, float, float, float], zona: tuple[float, float, float, float]) -> bool:
    return box[0] < zona[2] and zona[0] < box[2] and box[1] < zona[3] and zona[1] < box[3]


@pytest.mark.parametrize(("impianto", "grafo", "piano"), TAVOLE_APPROVATE, ids=lambda item: str(item)[-25:])
def test_sulle_sei_tavole_approvate_il_disegno_non_passa_sulla_tabella(
    impianto: str,
    grafo: Path,
    piano: Path,
    catalogo: ComponentRegistry,
    simboli: SymbolRegistry,
) -> None:
    """**Criterio 3 di REL-006**: su ciascuna delle sei tavole approvate, coi dati di
    prova, nessun simbolo, tratto di tubazione, sigla o richiamo entra nella tabella —
    e nemmeno nello stacco che la circonda. Il preflight non ha niente da dire, e la
    tavola esce senza bloccanti."""
    esito = _esegui(_modello(grafo, impianto), piano, catalogo, simboli)
    foglio = _foglio(esito)
    assert foglio.tabella is not None
    zona = zona_della_tabella(foglio.tabella.riquadro)
    dentro = [nome for nome, box in _ingombri(foglio, esito.frame.standard.text_small_mm) if _dentro(box, zona)]
    assert dentro == []
    assert not [item for item in esito.rilievi if item.code == "DRAWING_OVER_THE_EQUIPMENT_TABLE"]
    assert esito.bloccanti == []


def test_la_tabella_sta_nell_angolo_in_alto_a_sinistra_dell_area_del_disegno(
    tavola_1: tuple[ProjectModel, EsitoDelPiano],
) -> None:
    esito = tavola_1[1]
    tabella = _foglio(esito).tabella
    assert tabella is not None
    area = esito.frame.drawing_rect_mm
    assert (tabella.x_mm, tabella.y_mm) == (area.x_mm, area.y_mm)
    assert tabella.altezza_mm == tabella.riga_mm * (len(tabella.righe) + 1)
    passo = esito.frame.standard.grid_mm
    assert all(abs(item / passo - round(item / passo)) < 1e-9 for item in tabella.colonne_mm)


def _tabella_di_prova(righe: int = 4) -> TabellaDelleApparecchiature:
    return TabellaDelleApparecchiature(
        x_mm=10,
        y_mm=16,
        colonne_mm=[12.5, 30.0, 20.0, 15.0, 15.0],
        riga_mm=5.0,
        righe=[
            RigaDellaTabella(
                component_id=f"p{indice}",
                codice=f"GT-0{indice}",
                descrizione="Generatore di prova",
                caratteristiche=None,
                marca=None,
                modello=None,
            )
            for indice in range(1, righe + 1)
        ],
    )


def _pezzo(nome: str, x: float, y: float, larghezza: float = 20.0, altezza: float = 10.0) -> PlacedSymbol:
    return PlacedSymbol(
        component_id=nome, symbol_id="probe", rotation_deg=0,
        origin=Point(x_mm=x, y_mm=y), width_mm=larghezza, height_mm=altezza,
    )


def test_il_disegno_che_entrerebbe_nella_tabella_si_sposta_il_meno_possibile() -> None:
    """Un pezzo nell'angolo in alto a sinistra: il disegno si sposta **tutto insieme**, di
    passi di griglia, fino a lasciare lo stacco, e non oltre."""
    tabella = _tabella_di_prova()
    area = NOVE_C_A3.drawing_rect_mm
    foglio = SheetGeometry(
        sheet_id="t1",
        title="prova",
        symbols=[_pezzo("a", 40, 30), _pezzo("b", 150, 120)],
        routes=[
            RoutedTrunk(network_id="n", segments=[[Point(x_mm=60, y_mm=35), Point(x_mm=150, y_mm=35)]])
        ],
    )
    spostato = sgombra_la_tabella(foglio, area, tabella.riquadro, 2.5, 10.0)
    assert spostato != foglio
    zona = zona_della_tabella(tabella.riquadro)
    assert not any(_dentro(box, zona) for _, box in _ingombri(spostato, 1.8))
    dx = spostato.symbols[0].origin.x_mm - foglio.symbols[0].origin.x_mm
    dy = spostato.symbols[0].origin.y_mm - foglio.symbols[0].origin.y_mm
    assert (dx, dy) == (
        spostato.symbols[1].origin.x_mm - 150,
        spostato.symbols[1].origin.y_mm - 120,
    )
    # Il minimo: un passo in meno, in una qualunque direzione, rientrerebbe.
    for meno_x, meno_y in ((2.5, 0.0), (0.0, 2.5)):
        if dx - meno_x < 0 or dy - meno_y < 0:
            continue
        indietro = (40 + dx - meno_x, 30 + dy - meno_y, 60 + dx - meno_x, 40 + dy - meno_y)
        linea = (60 + dx - meno_x, 35 + dy - meno_y, 150 + dx - meno_x, 35 + dy - meno_y)
        assert _dentro(indietro, zona) or _dentro(linea, zona)


def test_un_disegno_che_gia_non_la_tocca_resta_dov_e() -> None:
    tabella = _tabella_di_prova()
    foglio = SheetGeometry(sheet_id="t1", title="prova", symbols=[_pezzo("a", 150, 120)])
    assert sgombra_la_tabella(foglio, NOVE_C_A3.drawing_rect_mm, tabella.riquadro, 2.5, 10.0) is foglio


def test_se_il_foglio_e_troppo_piccolo_il_disegno_resta_e_il_preflight_lo_blocca() -> None:
    """Un disegno che riempie l'area da un bordo all'altro non ha dove spostarsi: resta
    dov'e', la tabella si disegna lo stesso, e il preflight dice che il foglio e' troppo
    piccolo — un bloccante, perche' la tabella non si legge."""
    tabella = _tabella_di_prova()
    area = NOVE_C_A3.drawing_rect_mm
    foglio = SheetGeometry(
        sheet_id="t1",
        title="prova",
        symbols=[_pezzo("pieno", area.x_mm, area.y_mm, area.width_mm, area.height_mm)],
    )
    fermo = sgombra_la_tabella(foglio, area, tabella.riquadro, 2.5, 10.0)
    assert fermo is foglio
    rilievi = preflight.equipment_table(
        DrawingGeometry(project_id="p", sheets=[fermo.model_copy(update={"tabella": tabella})]),
        NOVE_C_A3,
    )
    assert [item.code for item in rilievi] == ["DRAWING_OVER_THE_EQUIPMENT_TABLE"]
    assert rilievi[0].severity.value == "blocking"
    assert "pieno" in rilievi[0].entity_ids


def test_le_sigle_non_entrano_nella_tabella(
    tavola_1: tuple[ProjectModel, EsitoDelPiano],
) -> None:
    """Un pezzo appena sotto la tabella: la sua sigla, che starebbe sopra di lui, dentro la
    tabella, va su un altro lato."""
    modello, esito = tavola_1
    tabella = _tabella_di_prova()
    zona = zona_della_tabella(tabella.riquadro)
    pdc = next(item for item in _foglio(esito).symbols if item.component_id == "pdc-master")
    sotto = pdc.model_copy(update={"origin": Point(x_mm=20.0, y_mm=zona[3] + 1.0)})
    senza = place_labels(modello, [sotto], NOVE_C_A3.standard, area=NOVE_C_A3.drawing_rect_mm)
    con = place_labels(
        modello, [sotto], NOVE_C_A3.standard, area=NOVE_C_A3.drawing_rect_mm, ostacoli=(zona,)
    )
    corpo = NOVE_C_A3.standard.text_small_mm

    def box(label: object) -> tuple[float, float, float, float]:
        assert hasattr(label, "anchor") and hasattr(label, "text")
        return (label.anchor.x_mm, label.anchor.y_mm - corpo,
                label.anchor.x_mm + text_width_mm(label.text, corpo), label.anchor.y_mm)

    assert any(_dentro(box(item), zona) for item in senza)
    assert con and not any(_dentro(box(item), zona) for item in con)


def test_una_tabella_senza_righe_non_c_e() -> None:
    assert impagina_la_tabella([], NOVE_C_A3) is None


def test_una_tavola_senza_tabella_non_scrive_il_campo() -> None:
    """Additiva: le geometrie scritte prima di REL-006 restano identiche byte per byte."""
    foglio = SheetGeometry(sheet_id="t1", title="prova")
    assert "tabella" not in foglio.model_dump(mode="json")
    assert "tabella" in foglio.model_copy(update={"tabella": _tabella_di_prova()}).model_dump(mode="json")


# --- il disegno: SVG e DXF --------------------------------------------------------------


def test_nell_svg_c_e_la_tabella_con_la_sua_intestazione(
    tavola_1_coi_dati: tuple[ProjectModel, EsitoDelPiano], simboli: SymbolRegistry
) -> None:
    esito = tavola_1_coi_dati[1]
    foglio = _foglio(esito)
    svg = render_sheet(foglio, esito.frame, simboli)
    blocco = re.search(r'<g class="tabella-apparecchiature".*?</g>', svg)
    assert blocco is not None
    testi = re.findall(r">([^<]+)</text>", blocco.group(0))
    assert tuple(testi[: len(INTESTAZIONE)]) == INTESTAZIONE
    assert "PDC-01" in testi and "Pompa di calore aria-acqua nr 1" in testi and "15 kW" in testi


def test_nel_dxf_la_tabella_c_e_sul_suo_layer_uguale_all_svg(
    tavola_1_coi_dati: tuple[ProjectModel, EsitoDelPiano], simboli: SymbolRegistry, tmp_path: Path
) -> None:
    """**Criterio 4 di REL-006**: ogni linea e ogni testo della tabella, riletti dal DXF
    sul layer della tabella, sono quelli che l'SVG disegna — stesse misure, stessi
    testi, l'intestazione in neretto."""
    esito = tavola_1_coi_dati[1]
    foglio = _foglio(esito)
    assert foglio.tabella is not None
    target = tmp_path / "tavola.dxf"
    write_dxf(foglio, esito.frame, simboli, target)
    doc = ezdxf.readfile(target)
    assert LAYER_TABELLA in doc.layers
    assert doc.layers.get(LAYER_TABELLA).description == "Tabella delle apparecchiature"
    entita = [item for item in doc.modelspace() if item.dxf.layer == LAYER_TABELLA]
    altezza = esito.frame.standard.sheet_height_mm
    tratti = tratti_della_tabella(foglio.tabella, esito.frame.standard)
    linee = sorted(
        (round(e.dxf.start.x, 6), round(e.dxf.start.y, 6), round(e.dxf.end.x, 6), round(e.dxf.end.y, 6))
        for e in entita if e.dxftype() == "LINE"
    )
    assert linee == sorted(
        (round(x1, 6), round(altezza - y1, 6), round(x2, 6), round(altezza - y2, 6))
        for x1, y1, x2, y2 in tratti.linee
    )
    testi = sorted(
        (e.dxf.text, round(e.dxf.insert.x, 6), round(e.dxf.insert.y, 6), e.dxf.height, e.dxf.style)
        for e in entita if e.dxftype() == "TEXT"
    )
    assert testi == sorted(
        (
            t.testo, round(t.x_mm, 6), round(altezza - t.y_mm, 6),
            round(tratti.corpo_mm * ALTEZZA_MAIUSCOLE_EM, 4),
            "NOVEC_ARIAL_GRASSETTO" if t.grassetto else "NOVEC_ARIAL",
        )
        for t in tratti.testi
    )
    assert {item.dxftype() for item in entita} == {"LINE", "TEXT"}


def test_senza_tabella_il_dxf_non_ha_il_suo_layer(simboli: SymbolRegistry, tmp_path: Path) -> None:
    foglio = SheetGeometry(sheet_id="t1", title="prova")
    target = tmp_path / "vuota.dxf"
    write_dxf(foglio, NOVE_C_A2, simboli, target)
    assert LAYER_TABELLA not in ezdxf.readfile(target).layers


def test_lo_stesso_piano_da_la_stessa_tavola_svg_e_dxf(
    catalogo: ComponentRegistry, simboli: SymbolRegistry, tmp_path: Path
) -> None:
    """**Criterio 5 di REL-006**: deterministico, SVG e DXF, byte per byte."""
    uscite = []
    for giro in ("uno", "due"):
        modello = _modello(IMPIANTO_6 / "grafo-completo-6.json", "6")
        esito = _esegui(modello, IMPIANTO_6 / "piano-6-a.json", catalogo, simboli)
        foglio = _foglio(esito)
        target = tmp_path / f"{giro}.dxf"
        write_dxf(foglio, esito.frame, simboli, target)
        uscite.append((render_sheet(foglio, esito.frame, simboli), target.read_bytes()))
    assert uscite[0] == uscite[1]


def test_la_riga_della_tabella_non_ha_campi_in_piu() -> None:
    """Le cinque colonne del PO, e nient'altro (I-141)."""
    assert INTESTAZIONE == ("CODICE", "DESCRIZIONE", "CARATTERISTICHE", "MARCA", "MODELLO")
    assert set(RigaDellaTabella.model_fields) == {
        "component_id", "codice", "descrizione", "caratteristiche", "marca", "modello"
    }


def _tabella_alta(righe: int) -> TabellaDelleApparecchiature:
    return _tabella_di_prova(righe).model_copy(update={"colonne_mm": [12.5, 37.5, 20.0, 15.0, 5.0]})


def test_il_foglio_piu_piccolo_deve_contenere_anche_la_tabella() -> None:
    """`SHEET_LARGER_THAN_NEEDED` dice «ci stava su un A3» solo se sull'A3 ci sta il disegno
    **e** la tabella: sotto di lei o alla sua destra, con lo stacco e il margine. Un
    disegno di 300 x 200 mm su un A2 ci starebbe da solo, ma con una tabella di 90 x 60
    no; uno di 100 x 100 si'."""
    tabella = _tabella_alta(11)
    assert (tabella.larghezza_mm, tabella.altezza_mm) == (90.0, 60.0)

    def codici(larghezza: float, altezza: float, con_la_tabella: bool) -> list[str]:
        foglio = SheetGeometry(
            sheet_id="t1",
            title="prova",
            symbols=[_pezzo("grande", 150, 120, larghezza, altezza)],
            tabella=tabella if con_la_tabella else None,
        )
        return [
            item.code
            for item in preflight.sheet_fill(DrawingGeometry(project_id="p", sheets=[foglio]), NOVE_C_A2)
        ]

    assert "SHEET_LARGER_THAN_NEEDED" in codici(300, 200, con_la_tabella=False)
    assert "SHEET_LARGER_THAN_NEEDED" not in codici(300, 200, con_la_tabella=True)
    assert "SHEET_LARGER_THAN_NEEDED" in codici(100, 100, con_la_tabella=True)
