"""La valvola di ritegno e' la N di UNI 9511, non la z (I-115, D-181).

Il PO, il 24 settembre 2026, sulle tavole di `DRAW-017`: «noi lo stiamo
disegnando come una "Z" invece è come una "N"». La tavola della norma pubblicata
da Oppo (SRC-016), misurata sui vettori, ha due barre **di traverso al tubo**,
unite dalla diagonale che scende dall'alto della prima al basso della seconda,
il tubo che arriva nel **punto medio** delle barre e la freccia **sopra**, lunga
quanto il segno. La z di D-122 aveva le barre parallele al tubo, e i monconi
che non toccavano il segno.

Le prove leggono la libreria pubblicata: il ritegno da solo e quello dentro il
gruppo di sicurezza sanitario, che porta lo stesso organo.
"""

import re
from pathlib import Path

import pytest

from disegnatore_mep.graphics.registry import Symbol, SymbolRegistry

ROOT = Path(__file__).resolve().parents[2]
SYMBOLS = ROOT / "assets" / "symbols"
TOLERANCE_MM = 1e-6

Segment = tuple[float, float, float, float]

LINE = re.compile(r'<line x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)"/>')


def _symbol(symbol_id: str) -> Symbol:
    return SymbolRegistry.from_directory(SYMBOLS).get(symbol_id)


def _lines(symbol: Symbol) -> list[Segment]:
    return [
        (float(x1), float(y1), float(x2), float(y2)) for x1, y1, x2, y2 in LINE.findall(symbol.body)
    ]


def _bars_across(symbol: Symbol) -> list[Segment]:
    """Le barre della N: tratti di traverso al tubo, a cavallo dell'asse."""
    axis = symbol.manifest.height_mm / 2
    return sorted(
        (
            line
            for line in _lines(symbol)
            if abs(line[0] - line[2]) < TOLERANCE_MM
            and min(line[1], line[3]) < axis < max(line[1], line[3])
        ),
        key=lambda line: line[0],
    )


def _the_n(symbol: Symbol) -> tuple[Segment, Segment, Segment]:
    """Le due barre e la diagonale che le unisce."""
    bars = _bars_across(symbol)
    assert len(bars) == 2, f"{symbol.manifest.id}: le barre di traverso al tubo sono {len(bars)}, non due"
    left, right = bars
    top = min(left[1], left[3])
    bottom = max(right[1], right[3])
    diagonals = [
        line
        for line in _lines(symbol)
        if {(line[0], line[1]), (line[2], line[3])} == {(left[0], top), (right[0], bottom)}
    ]
    assert diagonals, (
        f"{symbol.manifest.id}: nessuna diagonale dall'alto della barra di sinistra "
        "al basso di quella di destra"
    )
    return left, right, diagonals[0]


@pytest.mark.parametrize("symbol_id", ["valve-check", "dhw-safety-group"])
def test_le_barre_stanno_di_traverso_al_tubo_con_il_tubo_nel_punto_medio(symbol_id: str) -> None:
    symbol = _symbol(symbol_id)
    axis = symbol.manifest.height_mm / 2
    left, right, _ = _the_n(symbol)
    for bar in (left, right):
        assert abs((bar[1] + bar[3]) / 2 - axis) < TOLERANCE_MM, (
            f"{symbol_id}: la barra a x={bar[0]} non ha il tubo nel punto medio"
        )
        assert abs(abs(bar[3] - bar[1]) - abs(right[3] - right[1])) < TOLERANCE_MM


@pytest.mark.parametrize("symbol_id", ["valve-check", "dhw-safety-group"])
def test_il_tubo_arriva_alle_barre_e_non_passa_fra_loro(symbol_id: str) -> None:
    symbol = _symbol(symbol_id)
    axis = symbol.manifest.height_mm / 2
    left, right, _ = _the_n(symbol)
    on_axis = [
        (min(line[0], line[2]), max(line[0], line[2]))
        for line in _lines(symbol)
        if abs(line[1] - axis) < TOLERANCE_MM and abs(line[3] - axis) < TOLERANCE_MM
    ]
    assert any(abs(end - left[0]) < TOLERANCE_MM for _, end in on_axis), (
        f"{symbol_id}: il tubo non raggiunge la barra di sinistra"
    )
    assert any(abs(start - right[0]) < TOLERANCE_MM for start, _ in on_axis), (
        f"{symbol_id}: il tubo non riparte dalla barra di destra"
    )
    assert not any(
        start < right[0] - TOLERANCE_MM and end > left[0] + TOLERANCE_MM for start, end in on_axis
    ), f"{symbol_id}: un tratto del tubo passa dentro la N"


def test_il_ritegno_non_ha_barre_parallele_al_tubo_dentro_il_segno() -> None:
    """E' la z di D-122 che non deve tornare: nessun tratto orizzontale fra le
    barre, salvo la freccia che sta sopra."""
    symbol = _symbol("valve-check")
    left, right, _ = _the_n(symbol)
    top = min(left[1], left[3])
    inside = [
        line
        for line in _lines(symbol)
        if abs(line[1] - line[3]) < TOLERANCE_MM
        and line[1] >= top - TOLERANCE_MM
        and min(line[0], line[2]) < right[0] - TOLERANCE_MM
        and max(line[0], line[2]) > left[0] + TOLERANCE_MM
    ]
    assert inside == []


def test_la_freccia_sta_sopra_lunga_quanto_il_segno_e_punta_all_uscita() -> None:
    symbol = _symbol("valve-check")
    left, right, _ = _the_n(symbol)
    top = min(left[1], left[3])
    ports = {port.id: port for port in symbol.manifest.ports}
    shafts = [
        line
        for line in _lines(symbol)
        if abs(line[1] - line[3]) < TOLERANCE_MM and line[1] < top - TOLERANCE_MM
    ]
    assert len(shafts) == 1, "la freccia sopra il segno e' una sola asta"
    shaft = shafts[0]
    assert abs(min(shaft[0], shaft[2]) - left[0]) < TOLERANCE_MM
    assert abs(max(shaft[0], shaft[2]) - right[0]) < TOLERANCE_MM
    tip_x = right[0] if ports["b"].x_mm > ports["a"].x_mm else left[0]
    barbs = [
        line
        for line in _lines(symbol)
        if abs(line[0] - tip_x) < TOLERANCE_MM
        and abs(line[1] - shaft[1]) < TOLERANCE_MM
        and abs(line[3] - shaft[1]) > TOLERANCE_MM
    ]
    assert len(barbs) == 2, "la punta della freccia sta dalla parte dell'uscita, la porta b"
    assert all((line[2] - tip_x) * (ports["b"].x_mm - ports["a"].x_mm) < 0 for line in barbs)


def test_le_proporzioni_sono_quelle_della_tavola_della_norma() -> None:
    """Barre alte circa sei decimi della distanza fra loro: 0,57 nella tavola
    Oppo e in Caleffi, misurato sui vettori. Una N schiacciata o una N alta
    quanto larga non e' il segno della norma."""
    left, right, _ = _the_n(_symbol("valve-check"))
    ratio = abs(left[3] - left[1]) / (right[0] - left[0])
    assert 0.5 <= ratio <= 0.7, ratio
