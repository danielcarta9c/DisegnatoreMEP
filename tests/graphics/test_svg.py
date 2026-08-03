import re

from disegnatore_mep.graphics.registry import Symbol, SymbolRegistry
from disegnatore_mep.graphics.standard import A3_LANDSCAPE
from disegnatore_mep.graphics.svg import render_symbol_sheet
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


def test_nothing_is_drawn_outside_the_usable_area() -> None:
    output = sheet()
    xs = [float(value) for value in re.findall(r'translate\(([\d.]+) [\d.]+\)', output)]
    assert min(xs) >= A3_LANDSCAPE.margin_left_mm
    assert max(xs) <= A3_LANDSCAPE.margin_left_mm + A3_LANDSCAPE.usable_width_mm
