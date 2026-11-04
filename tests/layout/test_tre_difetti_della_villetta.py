"""Tre difetti grafici che il PO ha visto su una villetta reale (REL-017, 4 novembre 2026).

Sulla tavola di una commessa — pompa di calore Shenling da 12 kW, volano a quattro attacchi,
ACS su deviatrice — il PO ha segnato:

- **I-273** — lo scarico del volano disegnato rosso con la freccia. Lo scarico e' un ramo di
  servizio: acqua ferma, nessuna freccia (I-042); e in fondo al volano l'acqua e' quella che
  torna, il colore e' del ritorno (`layout.flow.OUTBOUND_FUNCTIONS`);
- **I-274** — la sigla VOL-01 lontana dal serbatoio: di fianco al pezzo cadeva a meta' del
  riquadro, subito sotto il tubo del secondario che esce da quella faccia e la sua valvola, e
  si leggeva come la loro (`layout.labels.quota_di_fianco`);
- **I-275** — in legenda i simboli dello sfiato, del volano e del bollitore si toccano: il
  simbolo si riduceva al campione di otto millimetri, e il passo e' di sette e mezzo
  (`layout.legend.scala_del_simbolo`).

Il banco e' la villetta di riferimento (`docs/collaudi/REL-015/pdc-regola/`), la stessa
configurazione della commessa, e le tavole della camera pulita di DRAW-018.
"""
# categoria: difende il motore

import re
from functools import cache
from itertools import combinations
from pathlib import Path
from xml.etree import ElementTree

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import render_sheet
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.geometry import (
    LegendEntry,
    PlacedSymbol,
    Point,
    RoutedTrunk,
    SheetGeometry,
)
from disegnatore_mep.layout.labels import SIDE_GAP_MM, riquadro_della_scritta
from disegnatore_mep.layout.legend import ROW_HEIGHT_MM, STACCO_FRA_I_SIMBOLI_MM, style_for
from disegnatore_mep.piano.esecutore import esegui_piano
from disegnatore_mep.piano.formato import carica_piano

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
NAMING = ROOT / "naming"
VILLETTA = ROOT / "docs" / "collaudi" / "REL-015" / "pdc-regola"
DRAW_018 = ROOT / "docs" / "collaudi" / "DRAW-018" / "prova-camera-pulita-2026-09-24"
CORPO_MM = NOVE_C_A3.standard.text_small_mm
TOLLERANZA_MM = 1e-6
ARROTONDAMENTO_SVG_MM = 1e-3
"""L'SVG scrive le misure a sei cifre significative."""

TAVOLE = {
    "villetta": (VILLETTA / "grafo-completo.json", VILLETTA / "piano-idraulica.json"),
    **{
        f"draw-018-{n}": (DRAW_018 / f"grafo-completo-{n}.json", DRAW_018 / f"piano-completo-{n}.json")
        for n in range(1, 6)
    },
}

Box = tuple[float, float, float, float]


@cache
def simboli() -> SymbolRegistry:
    return SymbolRegistry.from_directory(SYMBOLS)


@cache
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(CATALOG, symbols=simboli())


@cache
def foglio(nome: str) -> SheetGeometry:
    grafo, piano = TAVOLE[nome]
    esito = esegui_piano(load_project(grafo), carica_piano(piano), catalogo(), simboli(), NAMING)
    assert esito.disegno is not None, esito.errore
    return esito.disegno.sheets[0]


def _riquadro(item: PlacedSymbol) -> Box:
    return (item.origin.x_mm, item.origin.y_mm, item.right_mm, item.bottom_mm)


def _distanza(primo: Box, secondo: Box) -> float:
    dx = max(secondo[0] - primo[2], primo[0] - secondo[2], 0.0)
    dy = max(secondo[1] - primo[3], primo[1] - secondo[3], 0.0)
    return float((dx * dx + dy * dy) ** 0.5)


def _riquadri_dei_tubi(tratta: RoutedTrunk) -> list[Box]:
    return [
        (min(a.x_mm, b.x_mm), min(a.y_mm, b.y_mm), max(a.x_mm, b.x_mm), max(a.y_mm, b.y_mm))
        for segmento in tratta.segments
        for a, b in zip(segmento, segmento[1:], strict=False)
    ]


# --- I-273: lo scarico del volano ---------------------------------------------------------


def _sulla_tratta(x: float, y: float, tratta: RoutedTrunk) -> bool:
    return any(
        box[0] - 1e-3 <= x <= box[2] + 1e-3 and box[1] - 1e-3 <= y <= box[3] + 1e-3
        for box in _riquadri_dei_tubi(tratta)
    )


def _scarichi(nome: str) -> list[RoutedTrunk]:
    """Le tratte che arrivano a un pezzo che fa da scarico, lette sul modello."""
    modello = load_project(TAVOLE[nome][0])
    scarichi = {
        item.id for item in modello.components if "drain" in catalogo().get(item.definition_id).functions
    }
    connessioni = {
        item.id
        for item in modello.connections
        if {item.endpoint_a.component_id, item.endpoint_b.component_id} & scarichi
    }
    return [tratta for tratta in foglio(nome).routes if connessioni & set(tratta.connection_ids)]


def test_lo_scarico_del_volano_della_villetta_e_del_ritorno_e_senza_freccia() -> None:
    sheet = foglio("villetta")
    scarico = next(
        tratta
        for tratta in sheet.routes
        if "stub-drain-connection-volano-primary-in" in tratta.connection_ids
    )
    assert scarico.supply is False
    assert not scarico.flow_kind.porta_la_freccia
    radice = ElementTree.fromstring(render_sheet(sheet, NOVE_C_A3, simboli()))
    tratti = [
        item
        for item in radice.iter()
        if item.get("class") == "run"
        and all(
            _sulla_tratta(float(x), float(y), scarico)
            for x, y in (coppia.split(",") for coppia in item.get("points", "").split())
        )
    ]
    assert tratti, "la linea dello scarico non e' sulla tavola"
    assert {item.get("stroke") for item in tratti} == {style_for("heating_water", supply=False)[0]}
    for item in radice.iter():
        if item.get("class") != "flow-arrow":
            continue
        numeri = [float(valore) for valore in re.findall(r"-?\d+(?:\.\d+)?", item.get("d", ""))]
        assert not _sulla_tratta(numeri[0], numeri[1], scarico), numeri[:2]


@pytest.mark.parametrize("nome", sorted(TAVOLE))
def test_nessuno_scarico_porta_la_freccia(nome: str) -> None:
    scarichi = _scarichi(nome)
    assert scarichi, nome
    for tratta in scarichi:
        assert not tratta.flow_kind.porta_la_freccia, tratta.connection_ids


# --- I-274: la sigla del volano ------------------------------------------------------------


PEZZI_ALTI = {"villetta": "volano", "draw-018-1": "accumulo", "draw-018-2": "volano", "draw-018-4": "disgiuntore"}
"""I pezzi alti con la sigla di fianco: i volani e l'accumulo combinato."""


@pytest.mark.parametrize("nome", sorted(PEZZI_ALTI))
def test_la_sigla_del_volano_sta_accanto_al_serbatoio_e_lontano_da_tubi_e_valvole(nome: str) -> None:
    """La sigla tocca il suo pezzo — lo stacco di fianco, un millimetro e mezzo — e niente
    altro le sta vicino: nessun altro simbolo e nessun tubo a meno di due corpi. Prima di
    REL-017 VOL-01 della villetta stava a 2,1 mm dalla valvola del ritorno del secondario,
    sotto il tubo che esce dal volano (I-274)."""
    sheet = foglio(nome)
    pezzo = PEZZI_ALTI[nome]
    simbolo = next(item for item in sheet.symbols if item.component_id == pezzo)
    sigla = next(item for item in sheet.labels if item.id == f"{pezzo}-tag")
    assert sigla.richiamo is None
    box = riquadro_della_scritta(sigla, CORPO_MM)
    assert _distanza(box, _riquadro(simbolo)) <= SIDE_GAP_MM + TOLLERANZA_MM
    altri = [
        (_distanza(box, _riquadro(item)), item.component_id)
        for item in sheet.symbols
        if item.component_id != pezzo
    ]
    assert min(altri)[0] >= 2 * CORPO_MM, min(altri)
    tubi = [
        (_distanza(box, riquadro), tratta.connection_ids[0])
        for tratta in sheet.routes
        for riquadro in _riquadri_dei_tubi(tratta)
    ]
    assert min(tubi)[0] >= 2 * CORPO_MM, min(tubi)


def test_la_sigla_di_fianco_sta_lungo_il_tratto_libero_dai_tubi() -> None:
    """Sulla villetta i tubi escono dalla faccia destra del volano a 5 e a 20 mm: la sigla
    sta a meta' del tratto libero, da 20 a 45 mm, non a meta' del riquadro."""
    sheet = foglio("villetta")
    simbolo = next(item for item in sheet.symbols if item.component_id == "volano")
    sigla = next(item for item in sheet.labels if item.id == "volano-tag")
    box = riquadro_della_scritta(sigla, CORPO_MM)
    assert box[0] >= simbolo.right_mm
    centro = (box[1] + box[3]) / 2 - simbolo.origin.y_mm
    assert abs(centro - (20 + 45) / 2) <= TOLLERANZA_MM + 1e-3, centro


# --- I-275: i simboli della legenda ----------------------------------------------------------


def _riquadri_della_legenda(radice: ElementTree.Element) -> list[tuple[str, Box]]:
    trovati: list[tuple[str, Box]] = []
    for item in radice.iter():
        if item.get("class") != "legend-symbol":
            continue
        numeri = re.match(
            r"translate\(([-\d.e]+) ([-\d.e]+)\) scale\(([-\d.e]+)\)", item.get("transform", "")
        )
        assert numeri is not None, item.get("transform")
        x, y, scala = (float(valore) for valore in numeri.groups())
        manifesto = simboli().get(item.get("data-symbol-id", "")).manifest
        trovati.append(
            (manifesto.id, (x, y, x + manifesto.width_mm * scala, y + manifesto.height_mm * scala))
        )
    return trovati


def _si_toccano(primo: Box, secondo: Box) -> bool:
    return (
        primo[0] < secondo[2] + TOLLERANZA_MM
        and secondo[0] < primo[2] + TOLLERANZA_MM
        and primo[1] < secondo[3] + TOLLERANZA_MM
        and secondo[1] < primo[3] + TOLLERANZA_MM
    )


@pytest.mark.parametrize("nome", sorted(TAVOLE))
def test_nessun_simbolo_della_legenda_tocca_un_altro_ne_esce_dalla_fascia(nome: str) -> None:
    sheet = foglio(nome)
    radice = ElementTree.fromstring(render_sheet(sheet, NOVE_C_A3, simboli()))
    riquadri = _riquadri_della_legenda(radice)
    assert len(riquadri) == len(sheet.legend)
    for (primo, a), (secondo, b) in combinations(riquadri, 2):
        assert not _si_toccano(a, b), (primo, secondo, a, b)
        assert _distanza(a, b) >= STACCO_FRA_I_SIMBOLI_MM - ARROTONDAMENTO_SVG_MM, (primo, secondo)
    alto = min(entry.anchor.y_mm for entry in sheet.legend) - ROW_HEIGHT_MM
    assert all(box[1] >= alto - TOLLERANZA_MM for _, box in riquadri)


def test_tutti_i_simboli_della_libreria_stanno_nel_passo_della_legenda() -> None:
    """Una legenda con ogni simbolo della libreria, voce sotto voce al passo di sempre: nessun
    simbolo tocca quello sotto, qualunque sia la sua forma (I-275)."""
    tutti = sorted(simbolo.manifest.id for simbolo in simboli().all())
    voci = [
        LegendEntry(
            symbol_id=simbolo,
            name="x",
            anchor=Point(x_mm=10.0, y_mm=20.0 + ROW_HEIGHT_MM * (indice + 1)),
        )
        for indice, simbolo in enumerate(tutti)
    ]
    sheet = SheetGeometry(sheet_id="legenda", title="legenda", legend=voci)
    radice = ElementTree.fromstring(render_sheet(sheet, NOVE_C_A3, simboli()))
    riquadri = _riquadri_della_legenda(radice)
    assert len(riquadri) == len(tutti)
    for (primo, a), (secondo, b) in zip(riquadri, riquadri[1:], strict=False):
        assert b[1] - a[3] >= STACCO_FRA_I_SIMBOLI_MM - ARROTONDAMENTO_SVG_MM, (primo, secondo, a, b)
