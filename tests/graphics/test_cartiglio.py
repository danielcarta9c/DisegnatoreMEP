"""Il cartiglio Nove C sulla tavola (REL-002, I-130, D-091, D-025, D-186).

Le prove sono su **proprieta'** del cartiglio (D-092), non su una tavola:

- il modello viene dal file del PO, e il logo ne e' la copia esatta;
- un dato che il progetto non ha diventa «DA DEFINIRE», e la tavola una bozza;
- un testo resta nella sua casella, o la tavola lo dice;
- su ogni formato il cartiglio e' a misura, contro l'angolo in basso a destra;
- il disegno della tavola non cambia di un segno.
"""

import base64
import hashlib
import re
from datetime import date
from functools import cache
from pathlib import Path
from xml.etree import ElementTree

import pytest

from disegnatore_mep.cli import main
from disegnatore_mep.graphics import metriche
from disegnatore_mep.graphics.cartiglio import (
    BOZZA,
    DA_DEFINIRE,
    OBBLIGATORI,
    PT_MM,
    Campo,
    Cartiglio,
    CartiglioDellaTavola,
    ModelloDelCartiglio,
    disegna_cartiglio,
    impagina,
    larghezza_mm,
    rilievi_del_cartiglio,
    valori_del_cartiglio,
)
from disegnatore_mep.graphics.frame import NOVE_C_A1, NOVE_C_A2, NOVE_C_A3, NOVE_C_A4
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import DRAFT_MARK, render_sheet
from disegnatore_mep.layout.addresses import VERIFY_MARK
from disegnatore_mep.layout.geometry import PlacedSymbol, Point, RoutedTrunk, SheetGeometry
from disegnatore_mep.model.project import ProjectMetadata, ProjectModel, SheetIntentModel

ROOT = Path(__file__).resolve().parents[2]
CARTIGLI = ROOT / "assets" / "cartigli"
MODELLO = CARTIGLI / "Cartiglio_NoveC_A3.json"
FILE_DEL_PO = CARTIGLI / "Cartiglio_NoveC_A3.pdf"
SYMBOLS = ROOT / "assets" / "symbols"
SVG = "{http://www.w3.org/2000/svg}"


@cache
def cartiglio() -> Cartiglio:
    return Cartiglio.da_file(MODELLO)


def modello() -> ModelloDelCartiglio:
    return cartiglio().modello


def campo(nome: str) -> Campo:
    return next(item for item in modello().campi() if item.campo == nome)


def progetto(**campi: object) -> ProjectModel:
    dati: dict[str, object] = {
        "project_id": "prova-cartiglio",
        "client": "Condominio di prova",
        "project_name": "Riqualificazione della centrale termica",
        "commission_code": "PROVA-01",
        "revision": "00",
        "issue_date": date(2026, 9, 25),
        "address": "Via di Prova 1, 00000 Comune di Prova (XX)",
        "sheet_title": "Schema funzionale della centrale termica",
        "sheet_number": "T1",
    }
    dati.update(campi)
    return ProjectModel(metadata=ProjectMetadata.model_validate(dati))


def tavola(**campi: object) -> CartiglioDellaTavola:
    return CartiglioDellaTavola(
        cartiglio=cartiglio(), valori=valori_del_cartiglio(progetto(**campi), "t1")
    )


def foglio(title: str = "Prova") -> SheetGeometry:
    """Una tavola piccola fatta a mano: due simboli e una tratta."""
    return SheetGeometry(
        sheet_id="t1",
        title=title,
        symbols=[
            PlacedSymbol(
                component_id="valvola",
                symbol_id="valve-isolation",
                rotation_deg=0,
                origin=Point(x_mm=100.0, y_mm=100.0),
                width_mm=5.0,
                height_mm=5.0,
            )
        ],
        routes=[
            RoutedTrunk(
                network_id="riscaldamento",
                medium="heating_water",
                connection_ids=["c1"],
                segments=[[Point(x_mm=60.0, y_mm=102.5), Point(x_mm=100.0, y_mm=102.5)]],
            )
        ],
    )


@cache
def simboli() -> SymbolRegistry:
    return SymbolRegistry.from_directory(SYMBOLS)


# --- 1. Il modello viene dal file del PO ------------------------------------


def test_il_modello_dichiara_il_file_da_cui_viene() -> None:
    """Chi sostituisce il PDF senza rigenerare il modello lo scopre qui: il
    modello porta l'impronta del file che ha letto (I-130)."""
    assert modello().fonte.file == FILE_DEL_PO.name
    assert modello().fonte.sha256 == hashlib.sha256(FILE_DEL_PO.read_bytes()).hexdigest()
    assert modello().fonte.input == "I-130"


def test_il_logo_e_byte_per_byte_quello_del_file_del_po() -> None:
    """Il logo non si ricodifica: e' il JPEG che il PDF contiene, e questa prova
    lo ritrova nel file per conto suo, senza passare dal generatore."""
    dati = FILE_DEL_PO.read_bytes()
    flussi = re.findall(rb"/DCTDecode[^>]*>>\s*stream\r?\n(.*?)~>\s*endstream", dati, re.S)
    jpeg = [base64.a85decode(item, ignorechars=b" \t\r\n") for item in flussi]
    logo = (CARTIGLI / modello().logo().file).read_bytes()
    assert logo in jpeg
    assert logo.startswith(b"\xff\xd8")


def test_le_larghezze_dei_caratteri_sono_quelle_di_arial_nel_file() -> None:
    """La misura dei testi e' onesta: su ogni carattere che il file usa, le
    larghezze di `metriche` sono quelle dei caratteri Arial incorporati nel PDF
    del PO — Arial e Helvetica hanno le stesse larghezze."""
    tabelle = {"ArialMT": metriche.NORMALE, "Arial-BoldMT": metriche.GRASSETTO}
    larghezze = modello().larghezze_nel_file
    assert set(larghezze) == set(tabelle)
    for carattere_del_file, tabella in tabelle.items():
        diverse = {
            carattere: (misura, tabella[carattere])
            for carattere, misura in larghezze[carattere_del_file].items()
            if abs(tabella[carattere] - misura) > 1
        }
        assert diverse == {}, carattere_del_file
        assert len(larghezze[carattere_del_file]) >= 10


def test_ogni_dato_del_cartiglio_ha_il_suo_posto() -> None:
    """Gli undici segnaposto del file sono undici campi, e i tre nomi delle firme
    sono i soli posti che la sessione aggiunge."""
    campi = {item.campo: item for item in modello().campi()}
    assert set(campi) == {
        "intestazione", "dicitura", "committente", "indirizzo", "progetto",
        "titolo_tavola", "scala", "data", "revisione", "commessa", "numero_tavola",
        "approvato", "verificato", "disegnato",
    }
    aggiunti = sorted(nome for nome, item in campi.items() if item.origine == "sessione")
    assert aggiunti == ["approvato", "disegnato", "verificato"]
    assert "{commessa}" in (campi["intestazione"].modello or "")


# --- 2. I dati --------------------------------------------------------------


def test_i_valori_vengono_dal_progetto() -> None:
    valori = valori_del_cartiglio(progetto(), "t1")
    assert valori["committente"] == "Condominio di prova"
    assert valori["data"] == "25.09.2026"
    assert valori["revisione"] == "Rev. 00"
    assert valori["scala"] == "—"
    assert valori["numero_tavola"] == "T1"
    assert tavola().testo(campo("intestazione")) == (
        "NOVE C INGEGNERIA  |  Documento confidenziale  |  PROVA-01 – Elaborati Grafici"
    )


def test_un_dato_che_manca_si_scrive_da_definire_e_la_tavola_e_una_bozza() -> None:
    """D-025, D-087: il cartiglio non inventa. Un campo obbligatorio senza dato
    porta «DA DEFINIRE», e la tavola esce marcata in testata."""
    incompleta = tavola(address=None, sheet_title=None, sheet_number=None)
    assert incompleta.mancanti == ("indirizzo", "titolo_tavola", "numero_tavola")
    disegnato = disegna_cartiglio(incompleta, NOVE_C_A3)
    assert disegnato.bozza
    assert disegnato.svg.count(DA_DEFINIRE) == 3
    assert BOZZA in disegnato.svg
    rilievi = rilievi_del_cartiglio(incompleta, NOVE_C_A3)
    assert "INDIRIZZO, TITOLO TAVOLA, TAVOLA" in rilievi[0]


def test_nd_di_capire_e_un_dato_che_manca() -> None:
    """«Capire» scrive `ND` per il committente e la commessa che il progettista
    non ha dato: sul cartiglio non si stampa «ND», si stampa «DA DEFINIRE»."""
    incompleta = tavola(client="ND", commission_code="ND")
    assert incompleta.mancanti == ("committente", "commessa")
    assert DA_DEFINIRE in incompleta.testo(campo("intestazione"))


def test_firme_e_dicitura_non_sono_obbligatorie() -> None:
    completa = tavola()
    assert completa.mancanti == ()
    assert set(OBBLIGATORI).isdisjoint({"approvato", "verificato", "disegnato", "dicitura"})
    disegnato = disegna_cartiglio(completa, NOVE_C_A3)
    assert not disegnato.bozza
    assert BOZZA not in disegnato.svg
    assert DA_DEFINIRE not in disegnato.svg


def test_le_firme_si_scrivono_sulla_loro_riga() -> None:
    firmata = tavola(drawn_by="N. Cognome", checked_by="M. Rossi", approved_by="L. Verdi")
    svg = disegna_cartiglio(firmata, NOVE_C_A3).svg
    for nome in ("N. Cognome", "M. Rossi", "L. Verdi"):
        assert f">{nome}</text>" in svg


def test_una_tavola_dichiarata_porta_il_suo_titolo_e_il_suo_numero() -> None:
    modello_ = progetto().model_copy(
        update={"sheets": [SheetIntentModel(id="t2", title="Distribuzione", number="T7")]}
    )
    valori = valori_del_cartiglio(modello_, "t2")
    assert (valori["titolo_tavola"], valori["numero_tavola"]) == ("Distribuzione", "T7")


def test_i_campi_nuovi_sono_facoltativi_e_additivi() -> None:
    """Un documento 1.1.0 scritto prima di REL-002 resta valido cosi' com'e'."""
    vecchio = {
        "project_id": "vecchio",
        "client": "Nove C",
        "project_name": "Prova",
        "commission_code": "PROVA",
        "revision": "00",
        "issue_date": "2026-08-06",
    }
    meta = ProjectMetadata.model_validate(vecchio)
    assert (meta.address, meta.sheet_title, meta.sheet_number) == (None, None, None)
    richiesti = ProjectMetadata.model_json_schema()["required"]
    assert set(richiesti) == set(vecchio)


# --- 3. La misura dei testi -------------------------------------------------


def test_un_testo_che_entra_resta_al_suo_corpo() -> None:
    impaginato = impagina("Condominio", campo("committente"), modello().altezza_maiuscole_em)
    assert impaginato is not None
    assert impaginato.corpo_pt == campo("committente").corpo_pt
    assert impaginato.righe == ("Condominio",)


@pytest.mark.parametrize("nome", ["committente", "indirizzo", "progetto", "titolo_tavola"])
@pytest.mark.parametrize("parole", [4, 8, 12, 16, 24, 40])
def test_un_testo_resta_nella_sua_casella_o_non_si_impagina(nome: str, parole: int) -> None:
    """La proprieta' che conta: quello che si scrive non esce mai dalla casella.
    Scende di corpo fino al minimo, poi va su due righe; se non basta, non si
    impagina — e allora la tavola e' una bozza che lo dice."""
    posto = campo(nome)
    testo = " ".join(["Riqualificazione"] * parole)
    impaginato = impagina(testo, posto, modello().altezza_maiuscole_em)
    if impaginato is None:
        return
    assert posto.corpo_minimo_pt <= impaginato.corpo_pt <= posto.corpo_pt
    assert posto.larghezza_mm is not None
    for riga in impaginato.righe:
        assert larghezza_mm(riga, impaginato.corpo_pt, posto.grassetto) <= posto.larghezza_mm
    assert " ".join(impaginato.righe) == testo, "nessuna parola si perde"
    if len(impaginato.righe) == 2:
        corpo = impaginato.corpo_pt * PT_MM
        cima = posto.y_mm - 1.2 * corpo - modello().altezza_maiuscole_em * corpo
        assert posto.etichetta_y_mm is not None
        assert cima > posto.etichetta_y_mm, "la prima riga non tocca l'etichetta"


def test_un_testo_lungo_prima_scende_poi_va_a_capo() -> None:
    posto = campo("progetto")
    medio = "Riqualificazione della centrale termica condominiale – Conto Termico"
    lungo = medio + " con sconto in fattura e nuova distribuzione"
    primo = impagina(medio, posto, modello().altezza_maiuscole_em)
    secondo = impagina(lungo, posto, modello().altezza_maiuscole_em)
    assert primo is not None and secondo is not None
    assert len(primo.righe) == 1 and primo.corpo_pt < posto.corpo_pt
    assert len(secondo.righe) == 2 and secondo.corpo_pt == posto.corpo_minimo_pt


def test_un_testo_che_non_entra_nemmeno_su_due_righe_si_scrive_intero_e_fa_bozza() -> None:
    enorme = "Committente " * 40
    disegnato = disegna_cartiglio(tavola(client=enorme.strip()), NOVE_C_A3)
    assert disegnato.fuori_misura == ("committente",)
    assert disegnato.bozza
    assert enorme.strip().replace("  ", " ") in disegnato.svg


def test_i_doppi_spazi_della_testata_restano_due() -> None:
    """La testata del file ha due spazi attorno a ogni barra: un visualizzatore che
    compatta gli spazi li perderebbe, e lo spazio non separabile no."""
    svg = disegna_cartiglio(tavola(), NOVE_C_A3).svg
    assert "INGEGNERIA  |  Documento" in svg


# --- 4. Il foglio (D-186) ---------------------------------------------------


def _fascia(svg: str) -> tuple[float, float]:
    trovato = re.search(r'<g class="fascia" transform="translate\(([-\d.]+) ([-\d.]+)\)">', svg)
    assert trovato is not None
    return float(trovato.group(1)), float(trovato.group(2))


def test_sull_a3_il_cartiglio_sta_dove_sta_nel_file() -> None:
    svg = disegna_cartiglio(tavola(), NOVE_C_A3).svg
    assert _fascia(svg) == (0.0, 0.0)
    riquadro = modello().squadratura
    assert (
        f'<rect class="squadratura" x="10" y="10" width="400" height="277" fill="none" '
        f'stroke="{riquadro.colore}" stroke-width="{riquadro.spessore_mm:g}"/>'
    ) in svg


@pytest.mark.parametrize("telaio", [NOVE_C_A2, NOVE_C_A1], ids=["A2", "A1"])
def test_sugli_altri_formati_il_cartiglio_e_a_misura_in_basso_a_destra(telaio) -> None:  # type: ignore[no-untyped-def]
    """D-186: il cartiglio non si allarga e non si ridisegna. La fascia si sposta
    tutta insieme contro l'angolo in basso a destra della squadratura; la testata
    corre per tutta la squadratura."""
    svg = disegna_cartiglio(tavola(header_note=None), telaio).svg
    bordo = telaio.border_rect_mm
    fascia = modello().fascia.ingombro
    assert _fascia(svg) == (bordo.right_mm - fascia.destra_mm, bordo.bottom_mm - fascia.fondo_mm)
    assert f'x2="{bordo.right_mm - 4:g}" y2="16"' in svg, "il filetto della testata arriva al bordo"


def test_la_dicitura_si_tiene_al_bordo_destro() -> None:
    svg = disegna_cartiglio(tavola(header_note="Conto Termico con sconto in fattura"), NOVE_C_A2).svg
    bordo = NOVE_C_A2.border_rect_mm
    assert re.search(
        rf'<text x="{bordo.right_mm - 5:g}" y="14.5"[^>]*text-anchor="end">Conto Termico', svg
    )


def test_l_a4_non_contiene_il_cartiglio() -> None:
    with pytest.raises(ValueError, match="D-186"):
        disegna_cartiglio(tavola(), NOVE_C_A4)


# --- 5. La tavola -----------------------------------------------------------


def test_la_tavola_col_cartiglio_e_un_svg_valido_col_logo_dentro() -> None:
    svg = render_sheet(foglio(), NOVE_C_A3, simboli(), tavola())
    radice = ElementTree.fromstring(svg)
    immagini = radice.findall(f".//{SVG}image")
    assert len(immagini) == 1
    href = immagini[0].get("{http://www.w3.org/1999/xlink}href") or ""
    assert href.startswith("data:image/jpeg;base64,")
    assert base64.b64decode(href.split(",", 1)[1]) == cartiglio().logo_jpeg
    assert DRAFT_MARK not in svg


def _disegno(svg: str) -> list[str]:
    """I segni della tavola fuori da squadratura, testata e cartiglio."""
    radice = ElementTree.fromstring(svg)
    tenuti = []
    for figlio in radice:
        if figlio.get("class") == "cartiglio":
            continue
        tenuti.append(ElementTree.tostring(figlio, encoding="unicode"))
    return tenuti


def test_il_cartiglio_non_cambia_il_disegno() -> None:
    """Il cartiglio sta nella fascia e in testata: il resto della tavola e' lo
    stesso segno per segno, con o senza. Senza, i segni in piu' sono la vecchia
    riserva — la squadratura, il rettangolo del cartiglio, il titolo e la bozza."""
    senza = _disegno(render_sheet(foglio(), NOVE_C_A3, simboli()))
    con = _disegno(render_sheet(foglio(), NOVE_C_A3, simboli(), tavola()))
    vecchia_riserva = senza[:2] + senza[3:5]
    assert all(item.startswith(("<ns0:rect", "<ns0:text")) for item in vecchia_riserva)
    assert senza[2:3] + senza[5:] == con


def test_la_modalita_verifica_si_legge_in_testata() -> None:
    """D-110: la tavola di verifica si riconosce prima del disegno. Senza cartiglio
    il segno stava nel titolo; col cartiglio sta in testata, a destra."""
    svg = render_sheet(foglio(f"Prova · {VERIFY_MARK}"), NOVE_C_A3, simboli(), tavola())
    assert VERIFY_MARK in svg
    assert "Prova ·" not in svg


def test_il_comando_disegna_il_cartiglio(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`piano --cartiglio`: la tavola esce col cartiglio, e il comando dice che
    cosa manca — il grafo di prova non ha indirizzo, titolo e numero."""
    cartella = ROOT / "docs" / "collaudi" / "DRAW-018" / "prova-camera-pulita-2026-09-24"
    codice = main(
        [
            "piano", str(cartella / "grafo-completo-1.json"),
            "--piano", str(cartella / "piano-completo-1.json"),
            "--catalog", str(ROOT / "examples" / "layout" / "catalog"),
            "--symbols", str(SYMBOLS),
            "--naming", str(ROOT / "naming"),
            "--cartiglio", str(MODELLO),
            "--out", str(tmp_path),
        ]
    )
    detto = capsys.readouterr().out
    assert codice == 0
    assert "Cartiglio della tavola t1: campi da definire: INDIRIZZO, TITOLO TAVOLA, TAVOLA" in detto
    tavole = list(tmp_path.glob("*.svg"))
    assert len(tavole) == 1
    svg = tavole[0].read_text(encoding="utf-8")
    assert 'class="cartiglio"' in svg and BOZZA in svg


def test_un_dato_che_non_c_e_non_si_scrive_e_l_impronta_non_cambia() -> None:
    """L'aggiunta e' davvero additiva: un documento senza i dati del cartiglio si
    riscrive senza chiavi nuove — nemmeno `null` —, quindi `rules --apply-all`
    scrive gli stessi byte di prima e l'impronta del progetto non cambia. Con un
    dato, il dato si scrive."""
    from disegnatore_mep.io.canonical import canonical_json

    vecchio = progetto(address=None, sheet_title=None, sheet_number=None)
    scritto = vecchio.model_dump(mode="json")["metadata"]
    assert set(scritto) == {
        "project_id", "client", "project_name", "commission_code", "revision", "issue_date",
    }
    assert '"address"' not in vecchio.model_dump_json()
    assert '"address"' not in canonical_json(vecchio)
    nuovo = progetto(address="Via di Prova 1")
    assert nuovo.model_dump(mode="json")["metadata"]["address"] == "Via di Prova 1"
    assert canonical_json(nuovo) != canonical_json(vecchio)
    tavola_dichiarata = SheetIntentModel(id="t1", title="Distribuzione")
    assert "number" not in tavola_dichiarata.model_dump()
