"""Le scritte della tavola a 9 punti, mai sotto 8, in Arial (REL-008, I-159).

Il PO: «Adesso mi sembra che sta a circa 5, dovrebbe essere almeno 8 o meglio 9».
Qui si misura sulle tavole approvate che nessuna scritta del disegno, della legenda e
della tabella scenda sotto gli 8 punti, che quelle al corpo di sempre siano a 9, che
la legenda e la tabella le contengano, e che il DN che a 9 non entra scenda a 8 e lo
dica.
"""

import xml.etree.ElementTree as ET
from collections.abc import Callable
from pathlib import Path

import ezdxf
import pytest

from disegnatore_mep.graphics.cartiglio import larghezza_mm
from disegnatore_mep.graphics.dxf import ALTEZZA_MAIUSCOLE_EM, write_dxf
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import render_sheet
from disegnatore_mep.graphics.standard import (
    A2_LANDSCAPE,
    A3_LANDSCAPE,
    A4_LANDSCAPE,
    CORPO_DELLE_SCRITTE_PT,
    CORPO_MINIMO_PT,
    FAMIGLIA_DELLE_SCRITTE,
    PT_MM,
)
from disegnatore_mep.graphics.tabella import altezza_della_riga_mm
from disegnatore_mep.layout import diametri
from disegnatore_mep.layout.geometry import DiametroSullaTavola, Point
from disegnatore_mep.layout.legend import (
    INSET_MM,
    INTERLINEA_EM,
    RIENTRO_DEL_NOME_MM,
    a_capo,
    larghezza_del_nome_mm,
    righe_del_nome,
)
from disegnatore_mep.piano.esecutore import esegui_piano
from disegnatore_mep.piano.formato import carica_piano

from .conftest import DIAMETRI, IMPIANTI, Tavola

SVG = "{http://www.w3.org/2000/svg}"


def _testi(svg: str) -> list[ET.Element]:
    return [elemento for elemento in ET.fromstring(svg).iter(f"{SVG}text")]


def test_il_corpo_e_nove_punti_in_un_posto_solo() -> None:
    """Tutti i formati hanno lo stesso corpo, 9 punti (3,175 mm), e il minimo e' 8."""
    for standard in (A4_LANDSCAPE, A3_LANDSCAPE, A2_LANDSCAPE):
        assert standard.text_small_mm == pytest.approx(9 * 25.4 / 72)
        assert standard.text_small_mm < standard.text_normal_mm < standard.text_title_mm
    assert CORPO_DELLE_SCRITTE_PT == 9.0
    assert CORPO_MINIMO_PT == 8.0


@pytest.mark.parametrize("impianto", IMPIANTI)
def test_nessuna_scritta_sotto_otto_punti_ne_nell_svg_ne_nel_dxf(
    impianto: str, tavola: Callable[[str], Tavola], simboli: SymbolRegistry, tmp_path: Path
) -> None:
    """Sigle, dati, DN, legenda, nota, tabella, intestazione: nell'SVG il corpo, nel
    DXF l'altezza delle maiuscole. Le scritte al corpo di sempre sono a 9 punti."""
    t = tavola(impianto)
    frame = t.esito.frame
    corpi = [float(testo.get("font-size", "0")) / PT_MM for testo in _testi(render_sheet(t.foglio, frame, simboli))]
    assert corpi
    assert min(corpi) >= CORPO_MINIMO_PT - 1e-6
    nove = {round(c, 6) for c in corpi if c < 9.5}
    assert nove <= {9.0, 8.0}, nove
    dxf = tmp_path / "tavola.dxf"
    write_dxf(t.foglio, frame, simboli, dxf)
    altezze = [e.dxf.height for e in ezdxf.readfile(dxf).modelspace().query("TEXT")]
    assert altezze
    assert min(altezze) >= round(CORPO_MINIMO_PT * PT_MM * ALTEZZA_MAIUSCOLE_EM, 4) - 1e-6


@pytest.mark.parametrize("impianto", ("1", "5"))
def test_ogni_scritta_e_in_arial(
    impianto: str, tavola: Callable[[str], Tavola], simboli: SymbolRegistry
) -> None:
    """La radice dell'SVG dichiara Arial, e nessuna scritta ne dichiara un altro:
    sigle e legenda non escono piu' con le grazie (I-122)."""
    t = tavola(impianto)
    svg = render_sheet(t.foglio, t.esito.frame, simboli)
    radice = ET.fromstring(svg)
    assert radice.get("font-family") == FAMIGLIA_DELLE_SCRITTE
    for testo in radice.iter(f"{SVG}text"):
        famiglia = testo.get("font-family")
        assert famiglia is None or "Arial" in famiglia, famiglia


@pytest.mark.parametrize("impianto", IMPIANTI)
def test_la_legenda_sta_nella_sua_fascia(impianto: str, tavola: Callable[[str], Tavola]) -> None:
    """Ogni riga di ogni nome entra nella fascia di 50 mm, e le righe di due voci
    vicine non si toccano."""
    t = tavola(impianto)
    frame = t.esito.frame
    corpo = frame.standard.text_small_mm
    fascia = frame.legend_rect_mm
    larghezza = larghezza_del_nome_mm(frame)
    assert larghezza == pytest.approx(fascia.width_mm - INSET_MM - RIENTRO_DEL_NOME_MM - 1.0)
    blocchi = []
    for nome, base in [(e.name, e.anchor.y_mm - 8.0 + 4.0 + corpo / 2) for e in t.foglio.legend] + [
        (k.name, k.anchor.y_mm) for k in t.foglio.network_keys
    ]:
        righe = righe_del_nome(nome, frame)
        assert all(larghezza_mm(riga, corpo / PT_MM, False) <= larghezza + 1e-6 for riga in righe), righe
        passo = INTERLINEA_EM * corpo
        alto = base - (len(righe) - 1) * passo / 2 - 0.716 * corpo
        basso = base + (len(righe) - 1) * passo / 2
        blocchi.append((alto, basso, nome))
    blocchi.sort()
    for (_, basso, primo), (alto, _, secondo) in zip(blocchi, blocchi[1:], strict=False):
        assert basso < alto, (primo, secondo)


def test_l_a_capo_e_bilanciato_e_la_lineetta_non_apre_una_riga() -> None:
    corpo = 9 * PT_MM
    assert a_capo("Valvola deviatrice a tre vie", 36.5, corpo) == ("Valvola deviatrice", "a tre vie")
    assert a_capo("Acqua di riscaldamento — ritorno", 36.5, corpo) == ("Acqua di", "riscaldamento — ritorno")
    assert a_capo("Valvola di sfiato aria", 36.5, corpo) == ("Valvola di sfiato aria",)
    assert all(not riga.startswith("—") for riga in a_capo("Acqua fredda sanitaria — andata", 20, corpo))


@pytest.mark.parametrize("impianto", ("1", "6"))
def test_la_nota_della_legenda_ha_l_interlinea_del_corpo(
    impianto: str, tavola: Callable[[str], Tavola], simboli: SymbolRegistry
) -> None:
    """A 9 punti il passo di griglia, 2,5 mm, farebbe sovrapporre le righe della nota:
    il passo e' 1,15 corpi."""
    t = tavola(impianto)
    frame = t.esito.frame
    (nota,) = t.foglio.note_della_legenda
    assert len(nota.righe) > 1
    righe = [e for e in _testi(render_sheet(t.foglio, frame, simboli)) if e.get("class") == "legend-note"]
    basi = [float(e.get("y", "0")) for e in righe]
    passo = INTERLINEA_EM * frame.standard.text_small_mm
    # L'SVG scrive le coordinate con sei cifre significative: un millesimo di mm.
    assert all(b - a == pytest.approx(passo, abs=2e-3) for a, b in zip(basi, basi[1:], strict=False))


def test_la_riga_della_tabella_segue_il_corpo(tavola: Callable[[str], Tavola]) -> None:
    """Cinque millimetri a 1,8 mm, come in `REL-006`; 6,25 mm a 9 punti."""
    assert altezza_della_riga_mm(1.8) == 5.0
    assert altezza_della_riga_mm(9 * PT_MM) == 6.25
    tabella = tavola("1").foglio.tabella
    assert tabella is not None and tabella.riga_mm == 6.25


def test_un_dn_che_a_nove_punti_non_entra_scende_a_otto(
    tavola: Callable[[str], Tavola], simboli: SymbolRegistry, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Con lo spazio ai capi di prima, 1,5 mm, un DN della tavola 1 entra solo a 8
    punti: si posa a 8, lo dice, e SVG e DXF lo scrivono a 8."""
    monkeypatch.setattr(diametri, "RIENTRO_DAI_CAPI_MM", 1.5)
    t = tavola("1")
    _, piano = DIAMETRI.grafo_e_piano("1")
    esito = esegui_piano(t.modello, carica_piano(piano), _catalogo(simboli), simboli, DIAMETRI.NAMING)
    assert esito.disegno is not None
    foglio = esito.disegno.sheets[0]
    scese = [e for e in foglio.diametri if e.corpo_mm is not None]
    assert scese
    otto = CORPO_MINIMO_PT * PT_MM
    assert all(e.corpo_mm == pytest.approx(otto) for e in scese)
    svg = [e for e in _testi(render_sheet(foglio, esito.frame, simboli)) if e.get("class") == "diameter"]
    corpi = sorted({round(float(e.get("font-size", "0")) / PT_MM, 4) for e in svg})
    assert corpi == [8.0, 9.0]
    dxf = tmp_path / "tavola.dxf"
    write_dxf(foglio, esito.frame, simboli, dxf)
    altezze = {round(e.dxf.height, 4) for e in ezdxf.readfile(dxf).modelspace().query("TEXT") if e.dxf.layer == "M-ANNO-DIAM"}
    assert round(otto * ALTEZZA_MAIUSCOLE_EM, 4) in altezze


def _catalogo(simboli: SymbolRegistry):  # type: ignore[no-untyped-def]
    from disegnatore_mep.catalog.registry import ComponentRegistry

    return ComponentRegistry.from_directory(DIAMETRI.ROOT / "examples" / "layout" / "catalog", symbols=simboli)


def test_il_corpo_di_sempre_non_si_scrive_nella_geometria() -> None:
    """Un DN al corpo delle scritte non porta `corpo_mm`: le geometrie di `REL-007`
    restano identiche byte per byte."""
    sempre = DiametroSullaTavola(testo="Øi 32", ancora=Point(x_mm=1, y_mm=2), connection_ids=["a"])
    assert "corpo_mm" not in sempre.model_dump(mode="json")
    sceso = sempre.model_copy(update={"corpo_mm": 8 * PT_MM})
    assert sceso.model_dump(mode="json")["corpo_mm"] == pytest.approx(8 * PT_MM)
