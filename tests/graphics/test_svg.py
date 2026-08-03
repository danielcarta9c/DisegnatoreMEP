import re

import pytest

from disegnatore_mep.graphics.registry import Symbol, SymbolRegistry
from disegnatore_mep.graphics.standard import A3_LANDSCAPE
from disegnatore_mep.graphics.svg import SYMBOL_LABEL_GAP_MM, render_symbol_sheet
from disegnatore_mep.graphics.symbol import SymbolManifest


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


def test_every_symbol_is_placed_once() -> None:
    output = sheet()
    assert output.count('class="symbol"') == 2
    assert 'data-symbol-id="valve"' in output
    assert 'data-symbol-id="pump"' in output


def test_symbol_bodies_are_nested_under_a_translation() -> None:
    assert re.search(r'<g class="symbol"[^>]*transform="translate\([\d.]+ [\d.]+\)"', sheet())


def test_port_markers_are_emitted_at_their_millimetre_position() -> None:
    assert 'class="port"' in sheet()


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


def test_oversized_library_raises_naming_the_counts() -> None:
    """313 uniform 6x6 mm symbols exceed the 312-symbol capacity of one A3
    sheet (24 columns x 13 rows at the fixed COLUMN_GAP_MM/ROW_GAP_MM gaps).
    """
    registry = SymbolRegistry([sized_symbol(f"item-{index}", 6.0, 6.0) for index in range(313)])
    with pytest.raises(ValueError, match=r"313 symbols.*312"):
        render_symbol_sheet(registry)
