"""Il renderer della tavola.

Come il foglio di riscontro della libreria, dichiara millimetri fisici e un
`viewBox` numericamente identico: una unita' utente e' un millimetro di carta,
senza fattori di scala nascosti.

`render_symbol_sheet` resta com'e': e' un banco di prova della libreria, non la
tavola, e generalizzarlo avrebbe mescolato due cose diverse.

Questo modulo **non compila il cartiglio**: ne disegna soltanto la riserva. Il
template vettoriale e il blocco della tavola finale incompleta sono del piano
di rendering; finche' non esistono, il foglio esce marcato come bozza (D-025).
"""

from disegnatore_mep.layout.geometry import SheetGeometry
from disegnatore_mep.layout.legend import style_for

from .frame import Rect, SheetFrame
from .registry import SymbolRegistry

DRAFT_MARK = "BOZZA — cartiglio non compilato"
"""Marcatura della bozza: una tavola finale richiede il cartiglio completo."""

LEGEND_SWATCH_MM = 8.0
"""Lunghezza del tratto campione accanto a una voce di legenda."""

LEGEND_TEXT_GAP_MM = 2.0
CROSS_REFERENCE_RADIUS_MM = 2.0


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _rect(rect: Rect, width_mm: float, dash: str = "none") -> str:
    dash_attribute = "" if dash == "none" else f' stroke-dasharray="{dash}"'
    return (
        f'<rect x="{rect.x_mm:g}" y="{rect.y_mm:g}" width="{rect.width_mm:g}" '
        f'height="{rect.height_mm:g}" fill="none" stroke="black" '
        f'stroke-width="{width_mm:g}"{dash_attribute}/>'
    )


def render_sheet(
    sheet: SheetGeometry, frame: SheetFrame, symbols: SymbolRegistry
) -> str:
    """Una tavola A3 a misura reale, deterministica byte per byte."""
    standard = frame.standard
    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{standard.sheet_width_mm:g}mm" height="{standard.sheet_height_mm:g}mm" '
        f'viewBox="0 0 {standard.sheet_width_mm:g} {standard.sheet_height_mm:g}">',
        _rect(frame.border_rect_mm, standard.line_medium_mm),
        _rect(frame.title_block_rect_mm, standard.line_thin_mm),
        _rect(frame.legend_rect_mm, standard.line_thin_mm),
    ]

    parts.append(
        f'<text x="{frame.header_rect_mm.x_mm + 2:g}" '
        f'y="{frame.header_rect_mm.bottom_mm - 1:g}" '
        f'font-size="{standard.text_small_mm:g}" fill="black">'
        f"{_escape(sheet.title)}</text>"
    )
    parts.append(
        f'<text x="{frame.title_block_rect_mm.x_mm + 2:g}" '
        f'y="{frame.title_block_rect_mm.y_mm + standard.text_normal_mm + 1:g}" '
        f'font-size="{standard.text_normal_mm:g}" fill="black">'
        f"{_escape(DRAFT_MARK)}</text>"
    )

    for route in sheet.routes:
        colour, dash = style_for(route.medium)
        dash_attribute = "" if dash == "none" else f' stroke-dasharray="{dash}"'
        for segment in route.segments:
            points = " ".join(f"{item.x_mm:g},{item.y_mm:g}" for item in segment)
            parts.append(
                f'<polyline class="run" points="{points}" fill="none" '
                f'stroke="{colour}" stroke-width="{standard.line_medium_mm:g}"'
                f"{dash_attribute}/>"
            )

    for placed in sheet.symbols:
        symbol = symbols.get(placed.symbol_id).rotated(placed.rotation_deg)
        parts.append(
            f'<g class="symbol" data-component-id="{_escape(placed.component_id)}" '
            f'data-symbol-id="{_escape(placed.symbol_id)}" '
            f'transform="translate({placed.origin.x_mm:g} {placed.origin.y_mm:g})" '
            f'stroke="black" stroke-width="{standard.line_medium_mm:g}" fill="none">'
            f"{symbol.body}</g>"
        )

    for label in sheet.labels:
        parts.append(
            f'<text class="label" data-role="{_escape(label.role)}" '
            f'x="{label.anchor.x_mm:g}" y="{label.anchor.y_mm:g}" '
            f'font-size="{standard.text_small_mm:g}" fill="black">'
            f"{_escape(label.text)}</text>"
        )

    for entry in sheet.legend:
        symbol = symbols.get(entry.symbol_id)
        scale = min(
            1.0,
            LEGEND_SWATCH_MM / symbol.manifest.width_mm,
            LEGEND_SWATCH_MM / symbol.manifest.height_mm,
        )
        parts.append(
            f'<g class="legend-symbol" data-symbol-id="{_escape(entry.symbol_id)}" '
            f'transform="translate({entry.anchor.x_mm:g} '
            f'{entry.anchor.y_mm - LEGEND_SWATCH_MM:g}) scale({scale:g})" '
            f'stroke="black" stroke-width="{standard.line_thin_mm / scale:g}" fill="none">'
            f"{symbol.body}</g>"
            f'<text class="legend-name" '
            f'x="{entry.anchor.x_mm + LEGEND_SWATCH_MM + LEGEND_TEXT_GAP_MM:g}" '
            f'y="{entry.anchor.y_mm:g}" font-size="{standard.text_small_mm:g}" '
            f'fill="black">{_escape(entry.name)}</text>'
        )

    for key in sheet.network_keys:
        dash_attribute = "" if key.dash == "none" else f' stroke-dasharray="{key.dash}"'
        parts.append(
            f'<line class="legend-network" x1="{key.anchor.x_mm:g}" '
            f'y1="{key.anchor.y_mm - 1:g}" '
            f'x2="{key.anchor.x_mm + LEGEND_SWATCH_MM:g}" y2="{key.anchor.y_mm - 1:g}" '
            f'stroke="{key.colour}" stroke-width="{standard.line_medium_mm:g}"'
            f"{dash_attribute}/>"
            f'<text class="legend-network-name" '
            f'x="{key.anchor.x_mm + LEGEND_SWATCH_MM + LEGEND_TEXT_GAP_MM:g}" '
            f'y="{key.anchor.y_mm:g}" font-size="{standard.text_small_mm:g}" '
            f'fill="black">{_escape(key.name)}</text>'
        )

    for reference in sheet.cross_references:
        parts.append(
            f'<g class="cross-reference" data-pair-id="{_escape(reference.pair_id)}">'
            f'<circle cx="{reference.anchor.x_mm:g}" cy="{reference.anchor.y_mm:g}" '
            f'r="{CROSS_REFERENCE_RADIUS_MM:g}" fill="none" stroke="black" '
            f'stroke-width="{standard.line_thin_mm:g}"/>'
            f'<text x="{reference.anchor.x_mm + CROSS_REFERENCE_RADIUS_MM + 1:g}" '
            f'y="{reference.anchor.y_mm:g}" font-size="{standard.text_small_mm:g}" '
            f'fill="black">{_escape(reference.text)}</text></g>'
        )

    parts.append("</svg>")
    return "".join(parts)
