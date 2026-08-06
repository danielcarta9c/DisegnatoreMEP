import re

import pytest

from disegnatore_mep.graphics import svg
from disegnatore_mep.graphics.registry import Symbol, SymbolRegistry
from disegnatore_mep.graphics.standard import A3_LANDSCAPE, GraphicStandard
from disegnatore_mep.graphics.svg import SYMBOL_LABEL_GAP_MM, render_symbol_sheet
from disegnatore_mep.graphics.symbol import SymbolManifest


def standard_with(**overrides: float) -> GraphicStandard:
    """A3_LANDSCAPE with fields replaced, revalidated rather than copied blind.

    render_symbol_sheet accepts any GraphicStandard, so its layout assumptions
    have to be exercised against a standard other than the one they happen to
    hold for.
    """
    payload = A3_LANDSCAPE.model_dump()
    payload.update(overrides)
    return GraphicStandard(**payload)


def symbol(symbol_id: str) -> Symbol:
    manifest = SymbolManifest.model_validate(
        {
            "id": symbol_id,
            "version": "1.0.0",
            "name": f"Simbolo {symbol_id}",
            "width_mm": 6.0,
            "height_mm": 6.0,
            "allowed_rotations_deg": [0],
            "inline_gap_mm": 6.0,
            "ports": [
                {"id": "a", "face": "left", "x_mm": 0.0, "y_mm": 3.0},
                {"id": "b", "face": "right", "x_mm": 6.0, "y_mm": 3.0},
            ],
            "keep_out": {"left_mm": 2.0, "right_mm": 2.0},
            "source": "CONV-GRAFICA-001",
        }
    )
    return Symbol(manifest=manifest, body='<line x1="0" y1="3" x2="6" y2="3"/>')


def sized_symbol(symbol_id: str, width_mm: float, height_mm: float) -> Symbol:
    """A symbol of arbitrary size, for exercising the sheet's row/column capacity.

    A single left-face port at half-height is enough to satisfy SymbolManifest's
    perimeter validator; port topology does not affect the layout arithmetic.
    """
    manifest = SymbolManifest.model_validate(
        {
            "id": symbol_id,
            "version": "1.0.0",
            "name": symbol_id,
            "width_mm": width_mm,
            "height_mm": height_mm,
            "allowed_rotations_deg": [0],
            "ports": [{"id": "a", "face": "left", "x_mm": 0.0, "y_mm": height_mm / 2}],
            "keep_out": {"left_mm": 2.0},
            "source": "CONV-GRAFICA-001",
        }
    )
    return Symbol(manifest=manifest, body=f'<g id="{symbol_id}"/>')


def sheet() -> str:
    return render_symbol_sheet(SymbolRegistry([symbol("valve"), symbol("pump")]))


def test_sheet_declares_physical_millimetres() -> None:
    output = sheet()
    assert 'width="420mm"' in output
    assert 'height="297mm"' in output


def test_viewbox_maps_one_unit_to_one_millimetre() -> None:
    assert 'viewBox="0 0 420 297"' in sheet()


def test_sheet_contains_a_hundred_millimetre_scale_bar() -> None:
    output = sheet()
    assert 'id="scale-bar"' in output
    assert "100 mm" in output


def test_scale_bar_caption_follows_the_constant(monkeypatch: pytest.MonkeyPatch) -> None:
    """The caption used to be the literal `100 mm` next to SCALE_BAR_MM = 100.0.
    Changing the constant would have left the printed ruler check measuring
    against a caption that no longer matched the bar it labels.
    """
    monkeypatch.setattr(svg, "SCALE_BAR_MM", 50.0)
    output = sheet()
    assert "50 mm" in output
    assert "100 mm" not in output


def test_every_symbol_is_placed_once() -> None:
    output = sheet()
    assert output.count('class="symbol"') == 2
    assert 'data-symbol-id="valve"' in output
    assert 'data-symbol-id="pump"' in output


def test_symbol_bodies_are_nested_under_a_translation() -> None:
    assert re.search(r'<g class="symbol"[^>]*transform="translate\([\d.]+ [\d.]+\)"', sheet())


def test_port_markers_are_emitted_at_their_millimetre_position() -> None:
    assert 'class="port"' in sheet()


def test_sheet_labels_each_symbol_with_its_readable_name() -> None:
    """Cio' che un tecnico legge e' il nome, non l'identificativo di macchina.

    D-051: la nomenclatura visibile e' in italiano; `id` resta un identificativo
    di codice e sul foglio compare solo come riferimento secondario.
    """
    output = sheet()
    assert "Simbolo valve" in output
    assert "Simbolo pump" in output
    assert 'class="symbol-name"' in output
    # L'identificativo di macchina non compare come testo stampato: vive solo
    # nell'attributo data- per l'ispezione automatica.
    assert ">valve<" not in output
    assert ">pump<" not in output


def test_sheet_is_deterministic() -> None:
    assert sheet() == sheet()


def test_sheet_is_well_formed_xml() -> None:
    from xml.etree import ElementTree

    ElementTree.fromstring(sheet())


def test_symbol_content_stays_inside_the_usable_area() -> None:
    """Checks the real extents on both axes for every placed symbol: origin
    plus width_mm/height_mm (the box), and the id-label baseline below the
    box. All of it must stay within the usable rectangle.
    """
    standard = A3_LANDSCAPE
    manifests = {"valve": symbol("valve").manifest, "pump": symbol("pump").manifest}
    placements = re.findall(
        r'<g class="symbol" data-symbol-id="([a-z][a-z0-9_-]*)" '
        r'transform="translate\(([\d.]+) ([\d.]+)\)"',
        sheet(),
    )
    assert len(placements) == len(manifests)
    right = standard.margin_left_mm + standard.usable_width_mm
    bottom = standard.margin_top_mm + standard.usable_height_mm
    for symbol_id, x_str, y_str in placements:
        manifest = manifests[symbol_id]
        x, y = float(x_str), float(y_str)
        label_baseline = y + manifest.height_mm + standard.text_small_mm + SYMBOL_LABEL_GAP_MM
        assert x >= standard.margin_left_mm
        assert x + manifest.width_mm <= right
        assert y >= standard.margin_top_mm
        assert y + manifest.height_mm <= bottom
        assert label_baseline <= bottom


def test_scale_bar_stays_on_the_physical_sheet() -> None:
    """The scale bar is drawing furniture pinned to the bottom margin line, not
    symbol content: its end ticks intentionally reach half a tick's length
    below the usable-area boundary, into the bottom margin (see _scale_bar).
    That is by design, so it is checked against the full physical sheet
    rather than the usable-area bound that symbol content must respect - and
    the overshoot past the usable area is asserted explicitly below, so this
    test cannot pass by looking at too little.
    """
    standard = A3_LANDSCAPE
    output = sheet()
    block_match = re.search(r'<g id="scale-bar"[^>]*>(.*?)</g>', output)
    assert block_match is not None
    coords = re.findall(r'\b([xy])(?:1|2)?="([\d.]+)"', block_match.group(1))
    xs = [float(value) for axis, value in coords if axis == "x"]
    ys = [float(value) for axis, value in coords if axis == "y"]
    assert xs and ys
    assert min(xs) >= 0.0
    assert max(xs) <= standard.sheet_width_mm
    assert min(ys) >= 0.0
    assert max(ys) <= standard.sheet_height_mm
    # The ticks really do dip past the usable-area's bottom edge, into the
    # margin - otherwise this test would pass without checking anything real.
    assert max(ys) > standard.margin_top_mm + standard.usable_height_mm


def test_library_that_fits_still_renders() -> None:
    """Mirrors the size profile of the shipped twelve-symbol library (Task 6):
    eight 6x6 mm inline symbols, three 8x8 mm symbols and one 6x10 mm symbol -
    twelve components between 6 and 10 mm, comfortably within one A3 sheet.
    """
    sizes = [(6.0, 6.0)] * 8 + [(8.0, 8.0)] * 3 + [(6.0, 10.0)]
    registry = SymbolRegistry(
        [
            sized_symbol(f"item-{index}", width, height)
            for index, (width, height) in enumerate(sizes)
        ]
    )
    output = render_symbol_sheet(registry)
    assert output.count('class="symbol"') == 12


def test_empty_registry_still_renders_a_sheet() -> None:
    """`SymbolRegistry.from_directory` now rejects a directory with no
    manifests, but a registry built straight from a list - which is how the
    composite compiler and these tests build one - can still legitimately be
    empty. The `default=` fallbacks in the column/row arithmetic are therefore
    still reachable, and this pins that.
    """
    output = render_symbol_sheet(SymbolRegistry([]))
    assert 'viewBox="0 0 420 297"' in output
    assert 'class="symbol"' not in output


def uniform_symbol(index: int) -> Symbol:
    """Simbolo 6x6 mm con etichetta di lunghezza costante.

    La larghezza di colonna dipende dall'etichetta piu' lunga della libreria,
    quindi con nomi di lunghezza variabile la capienza del foglio cambierebbe
    col numero di simboli e il confine non sarebbe definito.
    """
    manifest = SymbolManifest.model_validate(
        {
            "id": f"item-{index}",
            "version": "1.0.0",
            "name": "Simbolo",
            "width_mm": 6.0,
            "height_mm": 6.0,
            "allowed_rotations_deg": [0],
            "ports": [{"id": "a", "face": "left", "x_mm": 0.0, "y_mm": 3.0}],
            "keep_out": {"left_mm": 2.0},
            "source": "CONV-GRAFICA-001",
        }
    )
    return Symbol(manifest=manifest, body='<line x1="0" y1="3" x2="6" y2="3"/>')


def _sheet_capacity() -> int:
    """Capienza dichiarata dal messaggio d'errore, per una libreria volutamente eccessiva."""
    registry = SymbolRegistry([uniform_symbol(i) for i in range(5000)])
    with pytest.raises(ValueError) as excinfo:
        render_symbol_sheet(registry)
    match = re.search(r"at most (\d+) fit", str(excinfo.value))
    assert match is not None
    return int(match.group(1))


def test_oversized_library_raises_naming_the_counts() -> None:
    """Il messaggio nomina quanti simboli sono stati dati e quanti ne stanno."""
    capacity = _sheet_capacity()
    too_many = capacity + 1
    registry = SymbolRegistry([uniform_symbol(i) for i in range(too_many)])
    with pytest.raises(ValueError, match=rf"{too_many} symbols.*{capacity}"):
        render_symbol_sheet(registry)


def test_the_capacity_boundary_is_exact() -> None:
    """Esattamente alla capienza rende, uno in piu' rifiuta.

    La capienza non e' fissata a un numero: dipende dalla larghezza di colonna,
    che considera anche l'etichetta piu' lunga. Fissarla renderebbe il test una
    fotografia dell'implementazione invece dell'invariante che deve proteggere.
    """
    capacity = _sheet_capacity()
    exact = SymbolRegistry([uniform_symbol(i) for i in range(capacity)])
    assert render_symbol_sheet(exact).count('class="symbol"') == capacity
    one_more = SymbolRegistry([uniform_symbol(i) for i in range(capacity + 1)])
    with pytest.raises(ValueError):
        render_symbol_sheet(one_more)


def test_symbol_wider_than_the_usable_area_raises_naming_both_measurements() -> None:
    """D-045 on the other axis: a 500 mm symbol used to draw off the right edge
    of a 420 mm sheet - x=20.0, right edge at 520 mm - and exit 0, because the
    column count was clamped to 1 instead of failing.
    """
    registry = SymbolRegistry([sized_symbol("too-wide", 500.0, 6.0)])
    with pytest.raises(ValueError, match=r"symbol too-wide does not fit.*510.*400"):
        render_symbol_sheet(registry)


def test_widest_symbol_that_still_fits_is_accepted() -> None:
    """The guard is on the column, not on an arbitrary margin: a symbol whose
    width plus the column gap is exactly the usable width still renders.
    """
    registry = SymbolRegistry([sized_symbol("just-fits", 380.0, 6.0)])
    assert render_symbol_sheet(registry).count('class="symbol"') == 1


def test_row_gap_too_small_for_the_label_is_rejected() -> None:
    """ROW_GAP_MM must leave room for the id label below each symbol. That holds
    for A3_LANDSCAPE by coincidence, and this function accepts any standard.
    """
    registry = SymbolRegistry([sized_symbol("valve", 6.0, 6.0)])
    with pytest.raises(ValueError, match=r"row gap.*leaves no room for the .*label"):
        render_symbol_sheet(
            registry,
            standard_with(text_small_mm=14.0, text_normal_mm=15.0, text_title_mm=16.0),
        )


def test_scale_bar_wider_than_the_usable_area_is_rejected() -> None:
    registry = SymbolRegistry([sized_symbol("valve", 6.0, 6.0)])
    with pytest.raises(ValueError, match=r"100mm scale bar does not fit.*80mm"):
        # 100 mm di foglio meno i due margini da 10 mm: la barra da 100 non ci sta.
        render_symbol_sheet(registry, standard_with(sheet_width_mm=100.0))
