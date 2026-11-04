"""Le note di posa, in alto a destra della tabella (REL-011, D-231, D-232, I-263, I-264).

Che **escono solo nell'esecutivo-costruttivo** — nel definitivo, o senza livello, la
tavola e' quella di prima byte per byte —, che sono **al massimo cinque**, che
ciascuna **esce solo con il suo pezzo** sulla tavola, che il riquadro sta **a destra
della tabella e a sinistra della legenda**, che **il disegno non ci passa sopra** e
che il DXF lo porta uguale all'SVG. Le misure sulla tavola leggono il grafo e il piano
agli atti dell'impianto 1, con il solo livello cambiato.
"""

import html
import json
import re
from pathlib import Path

import ezdxf
import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition
from disegnatore_mep.graphics.dxf import ALTEZZA_MAIUSCOLE_EM, LAYER_TABELLA, write_dxf
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.note import (
    IN_CASCATA,
    LARGHEZZA_MINIMA_MM,
    MASSIMO_DELLE_NOTE,
    NOTA_ANTIGELO,
    NOTA_ISOLAMENTO,
    NOTA_SFIATI_E_SCARICHI,
    NOTA_SONDA_DEL_VOLANO,
    NOTA_VASO,
    TITOLO,
    impagina_le_note,
    note_di_posa,
    tratti_delle_note,
)
from disegnatore_mep.graphics.pdf import per_winansi
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import render_sheet
from disegnatore_mep.layout.compose import sgombra_la_tabella
from disegnatore_mep.layout.geometry import (
    STACCO_DALLA_TABELLA_MM,
    DrawingGeometry,
    PlacedSymbol,
    Point,
    RigaDellaTabella,
    SheetGeometry,
    TabellaDelleApparecchiature,
    zona_della_tabella,
)
from disegnatore_mep.layout.labels import text_width_mm
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

TAVOLE = [
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


def _modello(grafo: Path, livello: str | None) -> ProjectModel:
    documento = json.loads(grafo.read_text(encoding="utf-8"))
    if livello is not None:
        documento["metadata"]["livello"] = livello
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
def esecutivo_1(
    catalogo: ComponentRegistry, simboli: SymbolRegistry
) -> tuple[ProjectModel, EsitoDelPiano]:
    modello = _modello(APPROVATI / "grafo-completo-1.json", "esecutivo")
    return modello, _esegui(modello, APPROVATI / "piano-completo-1.json", catalogo, simboli)


def _tutto(modello: ProjectModel) -> tuple[list[str], list[str]]:
    return [item.id for item in modello.components], [item.id for item in modello.networks]


# --- che cosa dice ------------------------------------------------------------------


@pytest.mark.parametrize("livello", [None, "definitivo"])
def test_nel_definitivo_e_senza_livello_non_ci_sono_note(
    livello: str | None, catalogo: ComponentRegistry
) -> None:
    """D-232: «solo nel esecutivo-costruttivo». Assente vale definitivo."""
    modello = _modello(APPROVATI / "grafo-completo-1.json", livello)
    assert note_di_posa(modello, catalogo, *_tutto(modello)) == []


def test_nell_esecutivo_le_note_dei_pezzi_che_ci_sono_nell_ordine(
    catalogo: ComponentRegistry,
) -> None:
    """L'impianto 1: due pompe di calore, un accumulo, un vaso, nessuna valvola antigelo.
    Escono l'isolamento, sfiati e scarichi, il vaso e la sonda — con la cascata, perche'
    le pompe sono due. Non esce la nota delle valvole antigelo."""
    modello = _modello(APPROVATI / "grafo-completo-1.json", "esecutivo")
    assert note_di_posa(modello, catalogo, *_tutto(modello)) == [
        NOTA_ISOLAMENTO,
        NOTA_SFIATI_E_SCARICHI,
        NOTA_VASO,
        NOTA_SONDA_DEL_VOLANO + IN_CASCATA,
    ]


def test_ogni_nota_esce_solo_con_il_suo_pezzo(catalogo: ComponentRegistry) -> None:
    modello = _modello(APPROVATI / "grafo-completo-1.json", "esecutivo")
    pezzi, reti = _tutto(modello)

    def senza(*tolti: str) -> list[str]:
        return note_di_posa(modello, catalogo, [item for item in pezzi if item not in tolti], reti)

    vaso = "expansion-connection-collettore-ritorno-a"
    assert NOTA_VASO not in senza(vaso)
    # Senza le pompe di calore: niente sfiati e scarichi, e niente sonda del volano.
    assert senza("pdc-master", "pdc-slave") == [NOTA_ISOLAMENTO, NOTA_VASO]
    # Senza l'accumulo: niente sonda.
    assert not any(item.startswith(NOTA_SONDA_DEL_VOLANO) for item in senza("accumulo"))
    # Con una pompa sola la sonda c'e', senza la cascata.
    assert senza("pdc-slave")[-1] == NOTA_SONDA_DEL_VOLANO


def test_senza_tubazioni_d_acqua_dell_impianto_nessuna_nota(catalogo: ComponentRegistry) -> None:
    """La tavola dell'elettrico e del comando, una tavola dell'aria: le cinque note parlano
    del circuito dell'acqua, e su una tavola senza le sue tubazioni non escono."""
    modello = _modello(APPROVATI / "grafo-completo-1.json", "esecutivo")
    pezzi, _ = _tutto(modello)
    sanitarie = [item.id for item in modello.networks if item.medium != "heating_water"]
    assert sanitarie
    assert note_di_posa(modello, catalogo, pezzi, sanitarie) == []


def _con_la_valvola_antigelo(
    modello: ProjectModel,
) -> tuple[ProjectModel, ComponentRegistry]:
    """Un catalogo con una voce di prova che fa la protezione antigelo — la voce vera la
    porta un altro lavoro — e il grafo con un pezzo di quella voce."""
    definizioni = [
        ComponentDefinition.model_validate_json(path.read_text("utf-8"))
        for path in sorted(CATALOG.glob("*.json"))
    ]
    base = next(item for item in definizioni if item.id == "valve-isolation")
    antigelo = base.model_copy(update={"id": "valvola-antigelo-di-prova", "functions": ["frost_protection"]})
    pezzo = ComponentInstance(id="antigelo", definition_id="valvola-antigelo-di-prova")
    return (
        modello.model_copy(update={"components": [*modello.components, pezzo]}),
        ComponentRegistry([*definizioni, antigelo]),
    )


def test_con_la_valvola_antigelo_le_note_sono_cinque_e_non_di_piu() -> None:
    """La valvola antigelo porta la sua nota, la seconda (D-230, D-232): con tutti i pezzi
    le note sono cinque, il tetto di D-232."""
    modello, catalogo = _con_la_valvola_antigelo(
        _modello(APPROVATI / "grafo-completo-1.json", "esecutivo")
    )
    note = note_di_posa(modello, catalogo, *_tutto(modello))
    assert note == [
        NOTA_ISOLAMENTO,
        NOTA_ANTIGELO,
        NOTA_SFIATI_E_SCARICHI,
        NOTA_VASO,
        NOTA_SONDA_DEL_VOLANO + IN_CASCATA,
    ]
    assert len(note) == MASSIMO_DELLE_NOTE
    pezzi, reti = _tutto(modello)
    assert NOTA_ANTIGELO not in note_di_posa(
        modello, catalogo, [item for item in pezzi if item != "antigelo"], reti
    )
    riquadro = impagina_le_note(note, None, NOVE_C_A3)
    assert riquadro is not None and len(riquadro.note) == MASSIMO_DELLE_NOTE


# --- il posto sul foglio ---------------------------------------------------------------


def test_il_riquadro_sta_a_destra_della_tabella_e_a_sinistra_della_legenda(
    esecutivo_1: tuple[ProjectModel, EsitoDelPiano],
) -> None:
    esito = esecutivo_1[1]
    foglio = _foglio(esito)
    assert foglio.tabella is not None and foglio.note_di_posa is not None
    tabella, note = foglio.tabella.riquadro, foglio.note_di_posa.riquadro
    area = esito.frame.drawing_rect_mm
    assert note[1] == tabella[1] == area.y_mm
    assert note[0] == pytest.approx(tabella[2] + STACCO_DALLA_TABELLA_MM)
    assert note[2] <= esito.frame.legend_rect_mm.x_mm - 1e-9
    assert note[2] <= area.right_mm and note[3] <= area.bottom_mm
    # La riga del titolo e' alta quanto l'intestazione della tabella.
    assert foglio.note_di_posa.riga_mm == foglio.tabella.riga_mm


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
    return elenco


def _dentro(box: tuple[float, float, float, float], zona: tuple[float, float, float, float]) -> bool:
    return box[0] < zona[2] and zona[0] < box[2] and box[1] < zona[3] and zona[1] < box[3]


@pytest.mark.parametrize(("impianto", "grafo", "piano"), TAVOLE, ids=lambda item: str(item)[-25:])
def test_nell_esecutivo_il_disegno_non_passa_sulle_note(
    impianto: str,
    grafo: Path,
    piano: Path,
    catalogo: ComponentRegistry,
    simboli: SymbolRegistry,
) -> None:
    """Le sei tavole approvate, rifatte nell'esecutivo: nessun simbolo, tratto o scritta
    entra nelle note, nemmeno nello stacco che le circonda; il preflight non ha niente
    da dire, e la tavola esce senza bloccanti."""
    esito = _esegui(_modello(grafo, "esecutivo"), piano, catalogo, simboli)
    foglio = _foglio(esito)
    assert foglio.note_di_posa is not None, impianto
    zona = zona_della_tabella(foglio.note_di_posa.riquadro)
    corpo = esito.frame.standard.text_small_mm
    assert [nome for nome, box in _ingombri(foglio, corpo) if _dentro(box, zona)] == []
    assert not [
        item for item in esito.rilievi
        if item.code in {"DRAWING_OVER_THE_NOTES", "DRAWING_OVER_THE_EQUIPMENT_TABLE"}
    ]
    assert esito.bloccanti == []


def _tabella(colonne: list[float]) -> TabellaDelleApparecchiature:
    return TabellaDelleApparecchiature(
        x_mm=NOVE_C_A3.drawing_rect_mm.x_mm,
        y_mm=NOVE_C_A3.drawing_rect_mm.y_mm,
        colonne_mm=colonne,
        riga_mm=6.25,
        righe=[
            RigaDellaTabella(
                component_id="p1", codice="PDC-01", descrizione="Pompa di calore",
                caratteristiche=None, marca=None, modello=None,
            )
        ],
    )


def test_se_a_destra_della_tabella_non_c_e_posto_le_note_vanno_sotto() -> None:
    area = NOVE_C_A3.drawing_rect_mm
    stretta = _tabella([20.0, 40.0, 30.0, 20.0, 20.0])
    accanto = impagina_le_note([NOTA_ISOLAMENTO], stretta, NOVE_C_A3)
    assert accanto is not None and accanto.y_mm == area.y_mm
    larga = _tabella([20.0, 100.0, 80.0, 40.0, area.width_mm - 240.0 - LARGHEZZA_MINIMA_MM + 5.0])
    sotto = impagina_le_note([NOTA_ISOLAMENTO], larga, NOVE_C_A3)
    assert sotto is not None
    assert (sotto.x_mm, sotto.y_mm) == (area.x_mm, larga.riquadro[3] + STACCO_DALLA_TABELLA_MM)
    assert sotto.riquadro[2] <= NOVE_C_A3.legend_rect_mm.x_mm


def test_il_testo_va_a_capo_dentro_il_riquadro() -> None:
    riquadro = impagina_le_note(
        [NOTA_ISOLAMENTO, NOTA_SFIATI_E_SCARICHI], _tabella([20.0, 40.0, 30.0, 20.0, 20.0]), NOVE_C_A3
    )
    assert riquadro is not None
    tratti = tratti_delle_note(riquadro, NOVE_C_A3.standard)
    sinistra, alto, destra, basso = riquadro.riquadro
    corpo = tratti.corpo_mm
    for testo in tratti.testi:
        assert sinistra < testo.x_mm
        assert testo.x_mm + text_width_mm(testo.testo, corpo) < destra
        assert alto < testo.y_mm < basso
    assert tratti.testi[0].testo == TITOLO and tratti.testi[0].grassetto
    assert [item.testo for item in tratti.testi if re.fullmatch(r"\d\.", item.testo)] == ["1.", "2."]


def test_il_disegno_fa_spazio_anche_alle_note() -> None:
    """Un pezzo dentro le note, non nella tabella: il disegno si sposta tutto insieme fin
    fuori dalle due zone. Senza le note resta dov'e'."""
    tabella = _tabella([20.0, 40.0, 30.0, 20.0, 20.0])
    note = impagina_le_note([NOTA_ISOLAMENTO], tabella, NOVE_C_A3)
    assert note is not None
    pezzo = PlacedSymbol(
        component_id="a", symbol_id="probe", rotation_deg=0,
        origin=Point(x_mm=note.x_mm + 10, y_mm=note.y_mm + 5), width_mm=20.0, height_mm=10.0,
    )
    foglio = SheetGeometry(sheet_id="t1", title="prova", symbols=[pezzo])
    area = NOVE_C_A3.drawing_rect_mm
    assert sgombra_la_tabella(foglio, area, tabella.riquadro, 2.5, 10.0) is foglio
    spostato = sgombra_la_tabella(foglio, area, tabella.riquadro, 2.5, 10.0, [note.riquadro])
    mosso = spostato.symbols[0]
    box = (mosso.origin.x_mm, mosso.origin.y_mm, mosso.right_mm, mosso.bottom_mm)
    assert not _dentro(box, zona_della_tabella(note.riquadro))
    assert not _dentro(box, zona_della_tabella(tabella.riquadro))


def test_il_preflight_blocca_il_disegno_sulle_note() -> None:
    note = impagina_le_note([NOTA_ISOLAMENTO], None, NOVE_C_A3)
    assert note is not None
    sopra = PlacedSymbol(
        component_id="sopra", symbol_id="probe", rotation_deg=0,
        origin=Point(x_mm=note.x_mm + 5, y_mm=note.y_mm + 5), width_mm=10.0, height_mm=10.0,
    )
    foglio = SheetGeometry(sheet_id="t1", title="prova", symbols=[sopra], note_di_posa=note)
    rilievi = preflight.equipment_table(DrawingGeometry(project_id="p", sheets=[foglio]), NOVE_C_A3)
    assert [item.code for item in rilievi] == ["DRAWING_OVER_THE_NOTES"]
    assert rilievi[0].severity.value == "blocking"
    assert "sopra" in rilievi[0].entity_ids


# --- il definitivo resta com'era ------------------------------------------------------------


def test_nel_definitivo_la_tavola_e_quella_di_prima(
    catalogo: ComponentRegistry, simboli: SymbolRegistry, tmp_path: Path
) -> None:
    """Il livello «definitivo» dichiarato e il livello assente danno la stessa tavola, SVG e
    DXF, senza il riquadro e senza il campo nella geometria. Che sia anche quella di
    prima di REL-011 lo dicono le prove byte per byte sulle tavole agli atti."""
    uscite = []
    for livello in (None, "definitivo"):
        esito = _esegui(
            _modello(APPROVATI / "grafo-completo-1.json", livello),
            APPROVATI / "piano-completo-1.json",
            catalogo,
            simboli,
        )
        foglio = _foglio(esito)
        assert foglio.note_di_posa is None
        assert "note_di_posa" not in foglio.model_dump(mode="json")
        target = tmp_path / f"{livello}.dxf"
        write_dxf(foglio, esito.frame, simboli, target)
        svg = render_sheet(foglio, esito.frame, simboli)
        assert "note-di-posa" not in svg
        uscite.append((svg, foglio.model_dump_json()))
    assert uscite[0] == uscite[1]


# --- il disegno: SVG e DXF --------------------------------------------------------------


def test_nell_svg_ci_sono_le_note_numerate(
    esecutivo_1: tuple[ProjectModel, EsitoDelPiano], simboli: SymbolRegistry
) -> None:
    esito = esecutivo_1[1]
    svg = render_sheet(_foglio(esito), esito.frame, simboli)
    blocco = re.search(r'<g class="note-di-posa".*?</g>', svg)
    assert blocco is not None
    testi = [html.unescape(item) for item in re.findall(r">([^<]+)</text>", blocco.group(0))]
    assert testi[0] == TITOLO
    assert [item for item in testi if re.fullmatch(r"\d\.", item)] == ["1.", "2.", "3.", "4."]
    # Il testo e' quello che il PDF puo' scrivere: le sostituzioni dichiarate, prima.
    assert all(per_winansi(item) == item for item in testi)
    assert any("lambda <= 0,040 W/mK" in item for item in testi)


def test_nel_dxf_le_note_ci_sono_sul_layer_della_tabella_uguali_all_svg(
    esecutivo_1: tuple[ProjectModel, EsitoDelPiano], simboli: SymbolRegistry, tmp_path: Path
) -> None:
    esito = esecutivo_1[1]
    foglio = _foglio(esito)
    assert foglio.note_di_posa is not None
    target = tmp_path / "tavola.dxf"
    write_dxf(foglio, esito.frame, simboli, target)
    doc = ezdxf.readfile(target)
    assert doc.layers.get(LAYER_TABELLA).description == "Tabella delle apparecchiature, e note di posa"
    altezza = esito.frame.standard.sheet_height_mm
    tratti = tratti_delle_note(foglio.note_di_posa, esito.frame.standard)
    entita = [item for item in doc.modelspace() if item.dxf.layer == LAYER_TABELLA]
    testi = {
        (e.dxf.text, round(e.dxf.insert.x, 6), round(e.dxf.insert.y, 6), e.dxf.height, e.dxf.style)
        for e in entita if e.dxftype() == "TEXT"
    }
    attesi = {
        (
            t.testo, round(t.x_mm, 6), round(altezza - t.y_mm, 6),
            round(tratti.corpo_mm * ALTEZZA_MAIUSCOLE_EM, 4),
            "NOVEC_ARIAL_GRASSETTO" if t.grassetto else "NOVEC_ARIAL",
        )
        for t in tratti.testi
    }
    assert attesi <= testi
    linee = {
        (round(e.dxf.start.x, 6), round(e.dxf.start.y, 6), round(e.dxf.end.x, 6), round(e.dxf.end.y, 6))
        for e in entita if e.dxftype() == "LINE"
    }
    assert {
        (round(x1, 6), round(altezza - y1, 6), round(x2, 6), round(altezza - y2, 6))
        for x1, y1, x2, y2 in tratti.linee
    } <= linee
