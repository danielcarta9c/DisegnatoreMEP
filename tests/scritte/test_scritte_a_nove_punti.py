"""Le scritte della tavola a 9 punti, mai sotto 8, in Arial (REL-008, I-159).

Il PO: «Adesso mi sembra che sta a circa 5, dovrebbe essere almeno 8 o meglio 9».
Qui si misura sulle tavole approvate che nessuna scritta del disegno, della legenda e
della tabella scenda sotto gli 8 punti, che quelle al corpo di sempre siano a 9, che
la legenda e la tabella le contengano, e che il DN che a 9 non entra scenda a 8 e lo
dica.
"""

import math
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
    # L'SVG scrive il corpo con sei cifre significative: 8 punti sono 2,82222 mm.
    assert min(corpi) >= CORPO_MINIMO_PT - 1e-4
    nove = {round(c, 3) for c in corpi if c < 9.5}
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


# --- quello che a 9 punti non entra accanto (I-160, I-161, I-162) --------------------


@pytest.mark.parametrize("impianto", IMPIANTI)
def test_la_sigla_di_un_apparecchiatura_in_tabella_c_e_sempre(
    impianto: str, tavola: Callable[[str], Tavola]
) -> None:
    """I-160: la sigla di un pezzo che sta in tabella non si omette. Sulle tavole 5 e
    6 il circolatore non ha 5,2 mm sopra di se', e la sigla scende a 8 punti."""
    t = tavola(impianto)
    assert t.foglio.tabella is not None
    scritte = {label.id for label in t.foglio.labels}
    for riga in t.foglio.tabella.righe:
        simbolo = next(s for s in t.foglio.symbols if s.component_id == riga.component_id)
        if simbolo.tag:
            assert f"{riga.component_id}-tag" in scritte, simbolo.tag
    codici = {r.code for r in t.esito.rilievi}
    assert not codici & {"TAG_OMITTED", "TABLE_EQUIPMENT_TAG_OMITTED"}
    if impianto in ("5", "6"):
        scese = [label for label in t.foglio.labels if label.corpo_mm is not None]
        assert scese and all(label.corpo_mm == pytest.approx(CORPO_MINIMO_PT * PT_MM) for label in scese)


def test_il_preflight_blocca_se_manca_la_sigla_di_un_apparecchiatura_in_tabella(
    tavola: Callable[[str], Tavola]
) -> None:
    from disegnatore_mep.layout.geometry import DrawingGeometry
    from disegnatore_mep.model.types import IssueSeverity
    from disegnatore_mep.validation.preflight import omitted_tags

    t = tavola("5")
    assert t.foglio.tabella is not None
    in_tabella = {riga.component_id for riga in t.foglio.tabella.righe}
    della_tabella = next(label for label in t.foglio.labels if label.id.removesuffix("-tag") in in_tabella)
    fuori = next(
        (s for s in t.foglio.symbols if s.tag and s.component_id not in in_tabella),
        None,
    )
    via = {della_tabella.id} | ({f"{fuori.component_id}-tag"} if fuori is not None else set())
    foglio = t.foglio.model_copy(update={"labels": [x for x in t.foglio.labels if x.id not in via]})
    rilievi = omitted_tags(DrawingGeometry(project_id="p", sheets=[foglio]))
    bloccanti = [r for r in rilievi if r.code == "TABLE_EQUIPMENT_TAG_OMITTED"]
    assert len(bloccanti) == 1 and bloccanti[0].severity is IssueSeverity.BLOCKING
    if fuori is not None:
        assert [r.severity for r in rilievi if r.code == "TAG_OMITTED"] == [IssueSeverity.WARNING]


@pytest.mark.parametrize("impianto", ("1", "4", "6"))
def test_il_dn_di_una_strada_principale_senza_posto_va_staccato_con_freccia(
    impianto: str, tavola: Callable[[str], Tavola], simboli: SymbolRegistry, tmp_path: Path
) -> None:
    """I-162: la freccia tocca una linea del proprio tratto, e il richiamo e' una sola
    diagonale a 45 gradi fino alla base della scritta (D-075); la scritta e'
    orizzontale e non tocca niente. SVG e DXF disegnano linea e freccia."""
    t = tavola(impianto)
    staccate = [e for e in t.foglio.diametri if e.richiamo_da is not None]
    assert staccate
    for etichetta in staccate:
        assert etichetta.richiamo_da is not None and not etichetta.verticale
        dx = abs(etichetta.ancora.x_mm - etichetta.richiamo_da.x_mm)
        dy = abs(etichetta.ancora.y_mm - etichetta.richiamo_da.y_mm)
        assert dx == pytest.approx(dy) and dx >= 3.5
        punta = etichetta.richiamo_da
        proprie = [r for r in t.foglio.routes if set(r.connection_ids) <= set(etichetta.connection_ids)]
        assert any(
            min(a.x_mm, b.x_mm) - 1e-6 <= punta.x_mm <= max(a.x_mm, b.x_mm) + 1e-6
            and min(a.y_mm, b.y_mm) - 1e-6 <= punta.y_mm <= max(a.y_mm, b.y_mm) + 1e-6
            for r in proprie
            for segmento in r.segments
            for a, b in zip(segmento, segmento[1:], strict=False)
        ), etichetta.testo
    svg = render_sheet(t.foglio, t.esito.frame, simboli)
    radice = ET.fromstring(svg)
    classi = [e.get("class") for e in radice.iter()]
    assert classi.count("diameter-leader") == len(staccate)
    assert classi.count("diameter-leader-arrow") == len(staccate)
    assert not [r.code for r in t.esito.rilievi if r.code.startswith(("DIAMETER_", "LEADER", "ORTHOGONAL"))]


def test_il_dn_di_una_strada_secondaria_si_sacrifica_senza_rilievo(tavola: Callable[[str], Tavola]) -> None:
    """I-161: sulla tavola 5 tre DN di strade secondarie non trovano posto accanto
    alla linea. Mancano, non hanno richiamo, e il preflight non lo segnala."""
    t = tavola("5")
    from disegnatore_mep.diametri.tratti import tratti_da_etichettare

    tratti = tratti_da_etichettare(t.modello, _catalogo_della_tavola())
    posati = {frozenset(e.connection_ids) for e in t.foglio.diametri}
    sacrificati = [item for item in tratti if item.connection_ids not in posati]
    assert sacrificati and all(not item.strada_principale for item in sacrificati)
    assert all(e.richiamo_da is None for e in t.foglio.diametri)
    assert "DIAMETER_TAG_MISSING" not in {r.code for r in t.esito.rilievi}


def _catalogo_della_tavola():  # type: ignore[no-untyped-def]
    from disegnatore_mep.catalog.registry import ComponentRegistry
    from disegnatore_mep.graphics.registry import SymbolRegistry

    simboli = SymbolRegistry.from_directory(DIAMETRI.ROOT / "assets" / "symbols")
    return ComponentRegistry.from_directory(DIAMETRI.ROOT / "examples" / "layout" / "catalog", symbols=simboli)


def test_la_freccia_del_richiamo_e_stretta_e_punta_sul_pezzo() -> None:
    from disegnatore_mep.graphics.sheet import (
        FRECCIA_DEL_RICHIAMO_MM,
        MEZZA_FRECCIA_DEL_RICHIAMO_MM,
        freccia_del_richiamo,
    )

    punta, b, c = freccia_del_richiamo(Point(x_mm=10, y_mm=10), Point(x_mm=20, y_mm=0))
    assert punta == Point(x_mm=10, y_mm=10)
    base = ((b.x_mm + c.x_mm) / 2, (b.y_mm + c.y_mm) / 2)
    assert math.hypot(base[0] - 10, base[1] - 10) == pytest.approx(FRECCIA_DEL_RICHIAMO_MM, abs=1e-3)
    assert math.hypot(b.x_mm - c.x_mm, b.y_mm - c.y_mm) == pytest.approx(2 * MEZZA_FRECCIA_DEL_RICHIAMO_MM, abs=1e-3)
    assert base[0] > 10 and base[1] < 10, "la base sta verso l'altro capo del richiamo"
