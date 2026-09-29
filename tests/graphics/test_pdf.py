"""La tavola in PDF senza browser (REL-001, I-122): l'SVG tradotto, a misura reale.

Il confronto al pixel col PDF del browser sta nel collaudo
(`docs/collaudi/REL-001/confronto_pdf.py`), perche' vuole il browser e MuPDF, che il
progetto non porta. Queste prove tengono su quello che si misura con la sola libreria
standard:

- la pagina e' il foglio, al centesimo di punto;
- lo stesso SVG da' gli stessi byte, e il file e' ben formato;
- ogni simbolo della libreria e la tavola intera, col cartiglio e il logo, si traducono;
- le scritte si allineano con le larghezze di Arial, e gli spazi si fondono come nell'SVG;
- un carattere che WinAnsi non ha si sostituisce e si dice;
- quello che il modulo non sa tradurre lo ferma, e lo nomina.
"""

import json
import math
import re
import zlib
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.cli import main
from disegnatore_mep.graphics.cartiglio import Cartiglio, CartiglioDellaTavola, valori_del_cartiglio
from disegnatore_mep.graphics.metriche import NORMALE
from disegnatore_mep.graphics.pdf import (
    PUNTI_PER_MM,
    ErroreDelPdf,
    larghezza_della_scritta,
    svg_in_pdf,
)
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import render_sheet
from disegnatore_mep.graphics.svg import render_symbol_sheet
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.piano.esecutore import esegui_piano
from disegnatore_mep.piano.formato import carica_piano

ROOT = Path(__file__).resolve().parents[2]
SYMBOLS = ROOT / "assets" / "symbols"
CATALOG = ROOT / "examples" / "layout" / "catalog"
IMPIANTO_6 = ROOT / "docs" / "collaudi" / "REL-003" / "impianto-6"
DATI_DI_PROVA = ROOT / "docs" / "collaudi" / "REL-002" / "dati-di-prova.json"
MODELLO_CARTIGLIO = ROOT / "assets" / "cartigli" / "Cartiglio_NoveC_A3.json"
LOGO = ROOT / "assets" / "cartigli" / "Cartiglio_NoveC_A3-logo.jpg"


def _svg(corpo: str, w: float = 420, h: float = 297) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:g}mm" height="{h:g}mm" '
        f'viewBox="0 0 {w:g} {h:g}" font-family="Arial, Helvetica, sans-serif">{corpo}</svg>'
    )


def _contenuto(dati: bytes) -> str:
    """Il contenuto della pagina, decompresso."""
    trovato = re.search(rb"/Filter /FlateDecode >>\nstream\n(.*?)\nendstream", dati, re.S)
    assert trovato is not None
    return zlib.decompress(trovato.group(1)).decode("latin-1")


@pytest.fixture(scope="module")
def simboli() -> SymbolRegistry:
    return SymbolRegistry.from_directory(SYMBOLS)


@pytest.fixture(scope="module")
def tavola_6(simboli: SymbolRegistry) -> str:
    """La tavola di prova di REL-003, approvata (I-136), col cartiglio compilato."""
    documento = json.loads((IMPIANTO_6 / "grafo-completo-6.json").read_text(encoding="utf-8"))
    dati = json.loads(DATI_DI_PROVA.read_text(encoding="utf-8"))
    documento["metadata"].update({**dati["tutti"], "sheet_number": "T6"})
    modello = ProjectModel.model_validate(documento)
    catalogo = ComponentRegistry.from_directory(CATALOG, symbols=simboli)
    esito = esegui_piano(modello, carica_piano(IMPIANTO_6 / "piano-6-a.json"), catalogo, simboli, ROOT / "naming")
    assert esito.disegno is not None
    (foglio,) = esito.disegno.sheets
    cartiglio = Cartiglio.da_file(MODELLO_CARTIGLIO)
    tavola = CartiglioDellaTavola(cartiglio=cartiglio, valori=valori_del_cartiglio(modello, foglio.sheet_id))
    return render_sheet(foglio, esito.frame, simboli, tavola)


@pytest.mark.parametrize(("w", "h"), [(420, 297), (594, 420), (841, 594)])
def test_la_pagina_e_il_foglio(w: float, h: float) -> None:
    """ADR 0003: un simbolo stampato misura quello che il modello dice. La pagina e' il
    foglio, senza margini e senza arrotondamenti — il browser sbagliava di mezzo millimetro."""
    esito = svg_in_pdf(_svg('<line x1="0" y1="0" x2="10" y2="10" stroke="black"/>', w, h))
    trovato = re.search(rb"/MediaBox \[0 0 ([0-9.]+) ([0-9.]+)\]", esito.dati)
    assert trovato is not None
    assert float(trovato.group(1)) == pytest.approx(w * PUNTI_PER_MM, abs=1e-3)
    assert float(trovato.group(2)) == pytest.approx(h * PUNTI_PER_MM, abs=1e-3)
    assert (esito.larghezza_mm, esito.altezza_mm) == (w, h)


def test_un_unita_utente_e_un_millimetro() -> None:
    """Il contenuto parte dalla scala che porta il millimetro nel punto, e capovolge la y:
    l'SVG scende, il PDF sale."""
    contenuto = _contenuto(svg_in_pdf(_svg("")).dati)
    k = f"{PUNTI_PER_MM:.4f}".rstrip("0")
    assert contenuto.startswith(f"{k} 0 0 -{k} 0 {297 * PUNTI_PER_MM:.4f}".rstrip("0"))


def test_un_viewbox_che_non_e_il_foglio_si_ferma() -> None:
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 840 594"/>'
    with pytest.raises(ErroreDelPdf, match="viewBox"):
        svg_in_pdf(svg)


def test_lo_stesso_svg_da_gli_stessi_byte_e_il_file_e_ben_formato(tavola_6: str) -> None:
    primo, secondo = svg_in_pdf(tavola_6).dati, svg_in_pdf(tavola_6).dati
    assert primo == secondo
    assert primo.startswith(b"%PDF-1.4\n") and primo.endswith(b"%%EOF\n")
    inizio_xref = int(re.search(rb"startxref\n(\d+)\n", primo).group(1))  # type: ignore[union-attr]
    assert primo[inizio_xref : inizio_xref + 4] == b"xref"
    righe = primo[inizio_xref:].split(b"\n")
    quanti = int(righe[1].split()[1])
    for numero, riga in enumerate(righe[3 : 2 + quanti], start=1):
        posizione = int(riga[:10])
        assert primo[posizione:].startswith(f"{numero} 0 obj\n".encode()), numero
    assert f"/Size {quanti}".encode() in primo


def test_la_tavola_col_cartiglio_si_traduce_e_il_logo_entra_byte_per_byte(tavola_6: str) -> None:
    esito = svg_in_pdf(tavola_6)
    assert esito.sostituzioni == []
    logo = LOGO.read_bytes()
    assert logo in esito.dati
    assert b"/Subtype /Image" in esito.dati and b"/Filter /DCTDecode" in esito.dati
    contenuto = _contenuto(esito.dati)
    assert contenuto.count("BT ") > 100
    assert "/Im1 Do" in contenuto
    assert b"/BaseFont /Helvetica " in esito.dati and b"/BaseFont /Helvetica-Bold " in esito.dati


def test_ogni_simbolo_della_libreria_si_traduce(simboli: SymbolRegistry) -> None:
    """Tutti i simboli su un foglio, come li mette la tavola: se uno usasse qualcosa che il
    PDF non sa scrivere, la traduzione si fermerebbe qui e non sulla tavola di un
    progettista. Il foglio di riscontro A3 ne porta sedici: si traduce anche lui."""
    corpi = "".join(
        f'<g class="symbol" transform="translate({10 + 70 * (i % 12)} {10 + 70 * (i // 12)})" '
        f'stroke="black" stroke-width="0.35" fill="none">{item.body}</g>'
        for i, item in enumerate(simboli.all())
    )
    esito = svg_in_pdf(_svg(corpi, 841, 594))
    contenuto = _contenuto(esito.dati)
    assert contenuto.count(" c\n") > 0, "archi e cerchi diventano curve di Bezier"
    assert esito.sostituzioni == []
    assert len(simboli.all()) == 47


def test_il_foglio_di_riscontro_si_traduce(simboli: SymbolRegistry) -> None:
    sedici = SymbolRegistry(list(simboli.all())[:16])
    assert svg_in_pdf(render_symbol_sheet(sedici)).sostituzioni == []


@pytest.mark.parametrize(("ancora", "spostamento"), [("start", 0.0), ("middle", 0.5), ("end", 1.0)])
def test_la_scritta_si_allinea_con_le_larghezze_di_arial(ancora: str, spostamento: float) -> None:
    testo, corpo = "PDC-01 Øi 32", 3.175
    contenuto = _contenuto(
        svg_in_pdf(_svg(f'<text x="100" y="50" font-size="{corpo}" text-anchor="{ancora}">{testo}</text>')).dati
    )
    x = float(re.search(r"1 0 0 -1 ([-0-9.]+) 50 Tm", contenuto).group(1))  # type: ignore[union-attr]
    larghezza = sum(NORMALE[c] for c in testo) * corpo / 1000
    assert larghezza_della_scritta(testo, corpo) == pytest.approx(larghezza)
    assert x == pytest.approx(100 - spostamento * larghezza, abs=1e-4)


def test_il_grassetto_e_helvetica_bold() -> None:
    contenuto = _contenuto(svg_in_pdf(_svg('<text x="1" y="2" font-weight="bold">T1</text>')).dati)
    assert "/F2 16 Tf" in contenuto


def test_gli_spazi_si_fondono_come_nell_svg() -> None:
    """Senza `xml:space` l'SVG fonde gli spazi in fila (SVG 1.1 §10.15): il cartiglio
    scrive «NOVE C INGEGNERIA  |  Documento…» e il browser ne mostra uno solo."""
    contenuto = _contenuto(svg_in_pdf(_svg('<text x="1" y="2">A  |  B  C</text>')).dati)
    assert r"(A | B\240\240C) Tj" in contenuto


def test_un_carattere_fuori_da_winansi_si_sostituisce_e_si_dice() -> None:
    esito = svg_in_pdf(_svg('<text x="1" y="2">Δt 5 K</text>'))
    assert [(s.carattere, s.scritta) for s in esito.sostituzioni] == [("Δ", "Δt 5 K")]
    assert "(?t 5 K) Tj" in _contenuto(esito.dati)


def test_l_arco_arriva_dove_l_svg_lo_manda_e_resta_sul_cerchio() -> None:
    """Il mezzo cerchio di raggio 10 da (0,0) a (20,0): la curva finisce nel punto
    d'arrivo, e il suo punto di mezzo sta sul cerchio, a meno dell'errore di Bezier."""
    contenuto = _contenuto(svg_in_pdf(_svg('<path d="M0 0 A10 10 0 0 1 20 0" stroke="black" fill="none"/>')).dati)
    curve = re.findall(r"^([-0-9. ]+) c$", contenuto, re.M)
    assert len(curve) == 2
    x0, y0 = 0.0, 0.0
    for curva in curve:
        x1, y1, x2, y2, x3, y3 = (float(v) for v in curva.split())
        mx = (x0 + 3 * x1 + 3 * x2 + x3) / 8
        my = (y0 + 3 * y1 + 3 * y2 + y3) / 8
        assert math.hypot(mx - 10, my) == pytest.approx(10, rel=3e-4)
        x0, y0 = x3, y3
    assert (x0, y0) == (20, 0)
    assert float(curve[0].split()[5]) == pytest.approx(-10, abs=1e-4), (
        "sweep 1 nell'SVG: l'arco gira in senso orario sullo schermo, e passa per (10, -10)"
    )


def test_il_tratteggio_e_quello_dell_svg() -> None:
    contenuto = _contenuto(svg_in_pdf(_svg('<line x1="0" y1="0" x2="50" y2="0" stroke="blue" stroke-dasharray="3 2"/>')).dati)
    assert "[3 2] 0 d" in contenuto
    assert "0 0 1 RG" in contenuto


def test_il_colore_corrente_e_il_nero() -> None:
    """`currentColor` — il pallino dei raccordi a T — senza un `color` dichiarato e' nero."""
    contenuto = _contenuto(svg_in_pdf(_svg('<circle cx="1" cy="1" r="0.7" fill="currentColor"/>')).dati)
    assert "0 0 0 rg" in contenuto


@pytest.mark.parametrize(
    ("corpo", "detto"),
    [
        ('<use href="#a"/>', "<use>"),
        ('<rect x="0" y="0" width="1" height="1" style="fill:red"/>', "style"),
        ('<g clip-path="url(#c)"/>', "clip-path"),
        ('<text x="0" y="0"><tspan>a</tspan></text>', "tspan"),
        ('<text x="0" y="0" font-family="Times New Roman">a</text>', "Times New Roman"),
        ('<rect x="0" y="0" width="1" height="1" fill="hsl(0,0%,0%)"/>', "hsl"),
    ],
)
def test_quello_che_il_pdf_non_sa_scrivere_si_ferma_e_si_nomina(corpo: str, detto: str) -> None:
    with pytest.raises(ErroreDelPdf, match=re.escape(detto)):
        svg_in_pdf(_svg(corpo))


def test_il_comando_scrive_il_pdf_accanto_all_svg(tmp_path: Path) -> None:
    """`piano … --pdf`: la tavola esce anche in PDF, della misura del foglio, senza browser."""
    codice = main(
        [
            "piano", str(IMPIANTO_6 / "grafo-completo-6.json"),
            "--piano", str(IMPIANTO_6 / "piano-6-a.json"),
            "--catalog", str(CATALOG), "--symbols", str(SYMBOLS), "--naming", str(ROOT / "naming"),
            "--out", str(tmp_path), "--pdf",
        ]
    )
    assert codice == 0
    (svg,) = tmp_path.glob("*.svg")
    pdf = svg.with_suffix(".pdf").read_bytes()
    atteso = svg_in_pdf(svg.read_text(encoding="utf-8"), svg.parent)
    assert _contenuto(pdf) == _contenuto(atteso.dati)
    assert re.search(rb"/MediaBox \[0 0 ([0-9.]+) ([0-9.]+)\]", pdf).groups() == re.search(  # type: ignore[union-attr]
        rb"/MediaBox \[0 0 ([0-9.]+) ([0-9.]+)\]", atteso.dati
    ).groups()
