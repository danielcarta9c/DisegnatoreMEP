"""Le zone per le tabelle come opzione del piano, e le tabelle che il motore disegna
(REL-012, fase 1, punti 4 e 7).

- `zone_tabelle` nel piano restringe l'area del disegno: non e' un formato in piu', e
  i controlli del motore lavorano sull'area che resta;
- `graphics.tabelle` posa nelle zone le tabelle che un altro modulo gli passa —
  titolo, colonne con la larghezza, testo che va a capo, righe di sezione, la tabella
  che continua nella colonna accanto — e SVG, PDF e DXF le scrivono uguali;
- il PDF e' WinAnsi: «≥», «≤», «→» passano per una sostituzione dichiarata, non per
  un «?»;
- la tabella delle apparecchiature porta l'unita' interna, il plenum, la centrale di
  zona e il comando a filo.
"""

from pathlib import Path
from typing import Any

import ezdxf
import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph.naming import Naming
from disegnatore_mep.graphics.frame import NOVE_C_A2, NOVE_C_A3
from disegnatore_mep.graphics.pdf import svg_in_pdf
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import render_sheet
from disegnatore_mep.graphics.tabella import righe_della_tabella
from disegnatore_mep.graphics.tabelle import (
    RIGHE_MINIME_IN_CONTINUAZIONE,
    posa_le_tabelle,
    riquadro_della_tabella_posata,
    tratti_della_tabella_posata,
)
from disegnatore_mep.layout.errors import LayoutError
from disegnatore_mep.layout.geometry import (
    ColonnaDellaTabella,
    RigaDellaTabellaLibera,
    SheetGeometry,
    TabellaNelleZone,
)
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.piano.formato import ErroreDelPiano, PianoDiComposizione, carica_piano
from disegnatore_mep.validation.preflight import equipment_table

ROOT = Path(__file__).resolve().parents[2]
NAMING = ROOT / "naming"
VUOTO = SheetGeometry(sheet_id="t1", title="prova")


def _tabella(righe: int, zona: str = "basso", titolo: str | None = "PROVA", sezioni: bool = False) -> TabellaNelleZone:
    elenco: list[RigaDellaTabellaLibera] = []
    for n in range(1, righe + 1):
        if sezioni and n % 5 == 1:
            elenco.append(RigaDellaTabellaLibera(sezione=f"Sezione {n}"))
        elenco.append(RigaDellaTabellaLibera(celle=[f"{n}", f"voce {n}", f"{n * 2}"]))
    return TabellaNelleZone(
        titolo=titolo,
        colonne=[
            ColonnaDellaTabella(intestazione="N.", larghezza_mm=12),
            ColonnaDellaTabella(intestazione="Voce", larghezza_mm=60),
            ColonnaDellaTabella(intestazione="Q.tà", larghezza_mm=16, a_destra=True),
        ],
        righe=elenco,
        zona=zona,  # type: ignore[arg-type]
    )


# --- le zone ---------------------------------------------------------------------


def test_le_zone_restringono_l_area_del_disegno_e_non_toccano_il_resto() -> None:
    con = NOVE_C_A2.con_le_zone(175, 135)
    assert con.standard == NOVE_C_A2.standard
    assert con.legend_rect_mm == NOVE_C_A2.legend_rect_mm
    assert con.title_block_rect_mm == NOVE_C_A2.title_block_rect_mm
    area, prima = con.drawing_rect_mm, NOVE_C_A2.drawing_rect_mm
    assert (area.x_mm, area.y_mm) == (prima.x_mm, prima.y_mm)
    assert area.width_mm == prima.width_mm - 175 and area.height_mm == prima.height_mm - 135
    destra, basso = con.zona_destra_mm, con.zona_basso_mm
    assert destra is not None and basso is not None
    assert destra.x_mm == area.right_mm and destra.right_mm == con.legend_rect_mm.x_mm
    assert basso.y_mm == area.bottom_mm and basso.bottom_mm == con.title_block_rect_mm.y_mm
    assert not destra.overlaps(area) and not basso.overlaps(area) and not destra.overlaps(basso)
    assert NOVE_C_A2.zona_destra_mm is None and NOVE_C_A2.zona_basso_mm is None


def test_zone_che_non_lasciano_il_disegno_sono_un_errore() -> None:
    with pytest.raises(ValueError, match="senza larghezza"):
        NOVE_C_A3.con_le_zone(400, 0)
    with pytest.raises(ValueError, match="senza altezza"):
        NOVE_C_A3.con_le_zone(0, 260)


def test_il_piano_dichiara_le_zone(tmp_path: Path) -> None:
    piano = PianoDiComposizione.model_validate(
        {"formato": "A2", "pezzi": {}, "zone_tabelle": {"destra_mm": 175, "basso_mm": 135}}
    )
    assert piano.zone_tabelle is not None and piano.zone_tabelle.destra_mm == 175
    assert PianoDiComposizione.model_validate({"pezzi": {}}).zone_tabelle is None
    rotto = tmp_path / "piano.json"
    rotto.write_text('{"pezzi": {}, "zone_tabelle": {"destra_mm": -5}}', encoding="utf-8")
    with pytest.raises(ErroreDelPiano, match="zone_tabelle"):
        carica_piano(rotto)
    rotto.write_text('{"pezzi": {}, "zone_tabelle": {"sinistra_mm": 5}}', encoding="utf-8")
    with pytest.raises(ErroreDelPiano, match="zone_tabelle"):
        carica_piano(rotto)


def test_la_tavola_di_prova_sta_nell_area_ristretta(tavola: tuple[ProjectModel, Any]) -> None:
    """Il piano chiede 175 mm a destra e 135 in basso: l'esecutore lavora sull'area che
    resta, e niente del disegno entra nelle zone. Zero rilievi."""
    _, esito = tavola
    area = esito.frame.drawing_rect_mm
    assert esito.frame.riserva_destra_mm == 175 and esito.frame.riserva_basso_mm == 135
    foglio = esito.disegno.sheets[0]
    for simbolo in foglio.symbols:
        assert area.x_mm <= simbolo.origin.x_mm and simbolo.right_mm <= area.right_mm, simbolo.component_id
        assert area.y_mm <= simbolo.origin.y_mm and simbolo.bottom_mm <= area.bottom_mm, simbolo.component_id
    for route in foglio.routes:
        for polilinea in route.segments:
            assert all(area.x_mm <= p.x_mm <= area.right_mm and area.y_mm <= p.y_mm <= area.bottom_mm for p in polilinea)
    assert esito.rilievi == []


def test_il_foglio_piu_piccolo_si_misura_con_le_stesse_zone(tavola: tuple[ProjectModel, Any]) -> None:
    """Senza zone il disegno di prova starebbe in un A3, e il rilievo lo direbbe; con le
    zone l'A3 lascia al disegno 175 x 100 mm e non lo contiene: il rilievo tace. Prima
    di questa correzione il rilievo avrebbe confrontato l'area ristretta dell'A2 con
    l'A3 intero."""
    from disegnatore_mep.validation.preflight import sheet_fill

    _, esito = tavola
    assert not sheet_fill(esito.disegno, esito.frame)
    senza = NOVE_C_A2
    assert [item.code for item in sheet_fill(esito.disegno, senza)] == ["SHEET_LARGER_THAN_NEEDED"]


# --- le tabelle ------------------------------------------------------------------


def test_le_tabelle_si_posano_nelle_loro_zone_una_sotto_l_altra() -> None:
    frame = NOVE_C_A2.con_le_zone(175, 135)
    foglio = posa_le_tabelle(VUOTO, frame, [_tabella(3, "destra"), _tabella(4, "destra", "SECONDA"), _tabella(2)])
    destra, basso = frame.zona_destra_mm, frame.zona_basso_mm
    assert destra is not None and basso is not None
    prima, seconda, terza = foglio.tabelle
    assert (prima.x_mm, prima.y_mm) == (destra.x_mm + 2.5, destra.y_mm + 2.5)
    assert seconda.x_mm == prima.x_mm
    assert seconda.y_mm >= riquadro_della_tabella_posata(prima, frame.standard)[3] + 5 - 1e-6
    assert (terza.x_mm, terza.y_mm) == (basso.x_mm + 2.5, basso.y_mm + 2.5)
    assert equipment_table(_disegno(foglio), frame) == []


def _disegno(foglio: SheetGeometry) -> Any:
    from disegnatore_mep.layout.geometry import DrawingGeometry

    return DrawingGeometry(project_id="p", sheets=[foglio])


def test_una_tabella_lunga_continua_nella_colonna_accanto_con_l_intestazione() -> None:
    frame = NOVE_C_A2.con_le_zone(175, 135)
    tabella = _tabella(30, sezioni=True)
    foglio = posa_le_tabelle(VUOTO, frame, [tabella])
    assert len(foglio.tabelle) == 2, "trenta righe non stanno in 130 mm"
    prima, seconda = foglio.tabelle
    assert prima.titolo == "PROVA" and seconda.titolo is None
    assert seconda.y_mm == prima.y_mm and seconda.x_mm == prima.x_mm + 88 + 5
    assert prima.righe + seconda.righe == tabella.righe, "nessuna riga persa, nessuna doppia"
    assert prima.righe[-1].sezione is None, "una riga di sezione non resta in fondo da sola"
    for pezzo in foglio.tabelle:
        sinistra, alto, destra, basso = riquadro_della_tabella_posata(pezzo, frame.standard)
        zona = frame.zona_basso_mm
        assert zona is not None and basso <= zona.bottom_mm and destra <= zona.right_mm
        intestazione = [t.testo for t in tratti_della_tabella_posata(pezzo, frame.standard).testi if t.grassetto]
        assert {"N.", "Voce", "Q.tà"} <= set(intestazione), "l'intestazione si ripete"


def _quante_in_una_colonna(frame: Any) -> int:
    """Quante righe di `_tabella` stanno in una colonna della zona in basso, col titolo."""
    return len(posa_le_tabelle(VUOTO, frame, [_tabella(40)]).tabelle[0].righe)


def test_una_continuazione_di_una_riga_sola_non_fa_una_colonna_vedova() -> None:
    """Collaudo T3 di REL-012: la tabella delle tratte andava su due colonne e la seconda
    portava la sola T16, con l'intestazione ripetuta. Una riga in piu' di quante ne
    entrano: le righe si dividono a meta' fra le due colonne."""
    frame = NOVE_C_A2.con_le_zone(175, 135)
    capienza = _quante_in_una_colonna(frame)
    for in_piu in (1, 2):
        tabella = _tabella(capienza + in_piu)
        prima, seconda = posa_le_tabelle(VUOTO, frame, [tabella]).tabelle
        assert prima.righe + seconda.righe == tabella.righe, "nessuna riga persa, nessuna doppia"
        assert len(seconda.righe) >= RIGHE_MINIME_IN_CONTINUAZIONE
        assert abs(len(prima.righe) - len(seconda.righe)) <= 1, "le due colonne si bilanciano"
    # Con tre righe nella colonna accanto, la continuazione resta com'era.
    prima, seconda = posa_le_tabelle(VUOTO, frame, [_tabella(capienza + 3)]).tabelle
    assert (len(prima.righe), len(seconda.righe)) == (capienza, 3)


def test_una_tabella_che_lascerebbe_una_colonna_vedova_passa_intera_nella_colonna_accanto() -> None:
    """Sotto un'altra tabella, una tabella che lascerebbe meno di tre righe nella colonna
    accanto ci va intera, se li' entra tutta."""
    frame = NOVE_C_A2.con_le_zone(175, 135)
    capienza = _quante_in_una_colonna(frame)
    sopra = _tabella(4, titolo="SOPRA")
    (posata_sopra,) = posa_le_tabelle(VUOTO, frame, [sopra]).tabelle
    # Quante righe di una seconda tabella entrano sotto la prima.
    sotto_entrano = len(posa_le_tabelle(VUOTO, frame, [sopra, _tabella(40)]).tabelle[1].righe)
    assert sotto_entrano + 1 <= capienza
    seconda = _tabella(sotto_entrano + 1, titolo="SOTTO")
    prima, intera = posa_le_tabelle(VUOTO, frame, [sopra, seconda]).tabelle
    assert prima.titolo == "SOPRA" and intera.titolo == "SOTTO"
    assert intera.righe == seconda.righe and intera.y_mm == posata_sopra.y_mm
    assert intera.x_mm == posata_sopra.x_mm + 88 + 5


def test_il_testo_va_a_capo_e_la_riga_si_alza() -> None:
    frame = NOVE_C_A2.con_le_zone(175, 135)
    lunga = TabellaNelleZone(
        colonne=[ColonnaDellaTabella(intestazione="Nota", larghezza_mm=40)],
        righe=[
            RigaDellaTabellaLibera(celle=["corta"]),
            RigaDellaTabellaLibera(celle=["una nota lunga che non entra in quaranta millimetri e va a capo"]),
        ],
        zona="destra",
    )
    (posata,) = posa_le_tabelle(VUOTO, frame, [lunga]).tabelle
    tratti = tratti_della_tabella_posata(posata, frame.standard)
    orizzontali = sorted({y1 for x1, y1, x2, y2 in tratti.linee if y1 == y2})
    altezze = [round(b - a, 3) for a, b in zip(orizzontali, orizzontali[1:], strict=False)]
    assert altezze[0] == altezze[1] < altezze[2], altezze
    assert len([t for t in tratti.testi if not t.grassetto]) >= 3


def test_una_tabella_che_non_entra_lo_dice() -> None:
    frame = NOVE_C_A2.con_le_zone(175, 135)
    larga = TabellaNelleZone(colonne=[ColonnaDellaTabella(intestazione="x", larghezza_mm=200)], zona="destra")
    with pytest.raises(LayoutError, match="non entra"):
        posa_le_tabelle(VUOTO, frame, [larga])
    parola = TabellaNelleZone(
        colonne=[ColonnaDellaTabella(intestazione="x", larghezza_mm=10)],
        righe=[RigaDellaTabellaLibera(celle=["precipitevolissimevolmente"])],
    )
    with pytest.raises(LayoutError, match="non entra nella colonna"):
        posa_le_tabelle(VUOTO, frame, [parola])
    with pytest.raises(LayoutError, match="zone_tabelle"):
        posa_le_tabelle(VUOTO, NOVE_C_A2, [_tabella(2)])
    with pytest.raises(LayoutError, match="non entra nella zona"):
        posa_le_tabelle(VUOTO, NOVE_C_A2.con_le_zone(0, 20), [_tabella(2)])


def test_una_riga_ha_le_celle_giuste() -> None:
    with pytest.raises(ValueError, match="celle"):
        TabellaNelleZone(colonne=[ColonnaDellaTabella(intestazione="x", larghezza_mm=10)],
                         righe=[RigaDellaTabellaLibera(celle=["a", "b"])])
    with pytest.raises(ValueError):
        RigaDellaTabellaLibera(celle=["a"], sezione="b")
    with pytest.raises(ValueError):
        RigaDellaTabellaLibera()


def test_il_preflight_ferma_una_tabella_fuori_dalla_sua_zona() -> None:
    frame = NOVE_C_A2.con_le_zone(175, 135)
    foglio = posa_le_tabelle(VUOTO, frame, [_tabella(2, "destra")])
    spostata = foglio.tabelle[0].model_copy(update={"x_mm": 100.0})
    rilievi = equipment_table(_disegno(foglio.model_copy(update={"tabelle": [spostata]})), frame)
    assert [item.code for item in rilievi] == ["ZONE_TABLE_OUT_OF_ITS_ZONE"]
    assert equipment_table(_disegno(foglio), frame) == []


def test_svg_pdf_e_dxf_scrivono_le_tabelle_e_il_pdf_non_ha_punti_di_domanda(
    tavola: tuple[ProjectModel, Any], simboli_aria: SymbolRegistry, tmp_path: Path
) -> None:
    """Le note della tavola di prova portano «≥» e «→»: nell'SVG, nel DXF e nel PDF
    sono «>=» e «->», e il PDF non sostituisce niente con «?»."""
    from disegnatore_mep.graphics.dxf import LAYER_TABELLA, write_dxf

    _, esito = tavola
    foglio = esito.disegno.sheets[0]
    assert len(foglio.tabelle) == 4, "tratte; note; computo in due colonne"
    svg = render_sheet(foglio, esito.frame, simboli_aria)
    assert svg.count('class="tabella-nelle-zone"') == 4
    assert "&gt;= 1 %" in svg and "Quadro -&gt; sezionatore" in svg
    assert "≥" not in svg and "→" not in svg
    pdf = svg_in_pdf(svg)
    assert pdf.sostituzioni == []
    assert b">= 1 %" in _testi_del_pdf(pdf.dati)
    write_dxf(foglio, esito.frame, simboli_aria, tmp_path / "t.dxf")
    testi = {
        item.dxf.text for item in ezdxf.readfile(tmp_path / "t.dxf").modelspace().query("TEXT")
        if item.dxf.layer == LAYER_TABELLA
    }
    # Nel TEXT del DXF il segno di percento si scrive «%%%» (`dxf._testo`).
    attesi = {
        t.testo.replace("%", "%%%")
        for pezzo in foglio.tabelle
        for t in tratti_della_tabella_posata(pezzo, esito.frame.standard).testi
    }
    assert attesi <= testi
    assert "TABELLA DELLE TRATTE — dati del progettista" in testi


def _testi_del_pdf(dati: bytes) -> bytes:
    import zlib

    uscita = b""
    for pezzo in dati.split(b"stream\n")[1:]:
        corpo = pezzo.split(b"\nendstream")[0]
        try:
            uscita += zlib.decompress(corpo)
        except zlib.error:
            continue
    return uscita


def test_il_pdf_sostituisce_i_caratteri_che_winansi_non_ha_e_lo_dice() -> None:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="50mm" viewBox="0 0 100 50" '
        'font-family="Arial"><text x="10" y="10" font-size="3">pendenza ≥ 1 % → scarico ⊕</text></svg>'
    )
    pdf = svg_in_pdf(svg)
    assert [(item.carattere, item.con) for item in pdf.sostituzioni] == [("≥", ">="), ("→", "->"), ("⊕", "?")]
    assert b"pendenza >= 1 % -> scarico ?" in _testi_del_pdf(pdf.dati)


# --- la tabella delle apparecchiature (punto 7) ----------------------------------


def test_la_tabella_delle_apparecchiature_porta_le_macchine_dell_aria(
    catalogo_aria: ComponentRegistry, progetto: Any
) -> None:
    modello = progetto(
        {"liquido": ("refrigerant", "refrigerant_liquid")},
        {
            "ui": ("ducted-indoor-unit", {"power_kw": 5.7, "flow_rate_m3h": 1080, "marca": "M", "modello": "X"}, None),
            "plenum": "zoning-plenum-5",
            "centrale": "zone-controller",
            "comando": "wired-remote",
            "termostato": "room-thermostat",
            "bocchetta": "air-supply-terminal",
            "quadro": "electrical-panel",
        },
        [],
    )
    righe = righe_della_tabella(
        modello, catalogo_aria, Naming.from_directory(NAMING), {}, [item.id for item in modello.components]
    )
    per_pezzo = {riga.component_id: riga for riga in righe}
    assert set(per_pezzo) == {"ui", "plenum", "centrale", "comando"}
    assert per_pezzo["ui"].caratteristiche == "5,7 kW · 1080 m³/h"


def test_un_termostato_con_marca_o_modello_sta_in_tabella(catalogo_aria: ComponentRegistry, progetto: Any) -> None:
    """Collaudo T3 di REL-012, §2: il progettista aveva dato «Airzone Think a filo» per i
    termostati, e sulla tavola non comparivano. Con marca o modello dichiarati entrano;
    senza, restano fuori come prima."""
    modello = progetto(
        {"liquido": ("refrigerant", "refrigerant_liquid")},
        {
            "centrale": "zone-controller",
            "con-marca": ("room-thermostat", {"marca": "Airzone", "modello": "Think a filo"}, None),
            "solo-modello": ("room-thermostat", {"modello": "Think a filo"}, None),
            "senza": ("room-thermostat", {"etichetta": "Soggiorno"}, None),
            "nd": ("room-thermostat", {"marca": "ND"}, None),
        },
        [],
    )
    righe = righe_della_tabella(
        modello, catalogo_aria, Naming.from_directory(NAMING), {}, [item.id for item in modello.components]
    )
    per_pezzo = {riga.component_id: riga for riga in righe}
    assert set(per_pezzo) == {"centrale", "con-marca", "solo-modello"}
    assert (per_pezzo["con-marca"].marca, per_pezzo["con-marca"].modello) == ("Airzone", "Think a filo")


def test_la_tavola_di_prova_ha_le_sigle_e_la_scritta_del_comando(tavola: tuple[ProjectModel, Any]) -> None:
    """Il comando a filo sta in tabella e porta la sua scritta accanto (§6.2); nessuna
    sigla e' scritta dall'ingegnere, e la tabella le ha tutte (§6.1)."""
    _, esito = tavola
    foglio = esito.disegno.sheets[0]
    assert foglio.tabella is not None
    assert [(r.component_id, r.codice) for r in foglio.tabella.righe] == [
        ("ue", "UE-01"), ("ui", "UI-01"), ("comando", "CF-01")
    ]
    scritte = {label.id: label.text for label in foglio.labels}
    assert scritte["comando-etichetta"] == "in soggiorno" and scritte["comando-tag"] == "CF-01"
