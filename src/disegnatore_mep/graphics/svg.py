"""Emettitore SVG a misura reale.

Il foglio dichiara larghezza e altezza in millimetri e un `viewBox` numerico
identico, cosi' che una unita' utente corrisponda esattamente a un millimetro
di carta. Stampando senza adattamento, il righello deve confermare la barra di
scala.
"""

from .registry import SymbolRegistry
from .standard import A3_LANDSCAPE, GraphicStandard

SCALE_BAR_MM = 100.0
COLUMN_GAP_MM = 10.0
ROW_GAP_MM = 14.0


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _scale_bar(standard: GraphicStandard) -> str:
    x = standard.margin_left_mm
    y = standard.sheet_height_mm - standard.margin_bottom_mm
    return (
        f'<g id="scale-bar" stroke="black" stroke-width="{standard.line_medium_mm}">'
        f'<line x1="{x}" y1="{y}" x2="{x + SCALE_BAR_MM}" y2="{y}"/>'
        f'<line x1="{x}" y1="{y - 1.5}" x2="{x}" y2="{y + 1.5}"/>'
        f'<line x1="{x + SCALE_BAR_MM}" y1="{y - 1.5}" '
        f'x2="{x + SCALE_BAR_MM}" y2="{y + 1.5}"/>'
        f'<text x="{x + SCALE_BAR_MM / 2}" y="{y - 2}" '
        f'font-size="{standard.text_small_mm}" text-anchor="middle" '
        f'stroke="none" fill="black">100 mm</text>'
        f"</g>"
    )


def render_symbol_sheet(
    symbols: SymbolRegistry, standard: GraphicStandard = A3_LANDSCAPE
) -> str:
    column_width = max(
        (item.manifest.width_mm for item in symbols.all()), default=COLUMN_GAP_MM
    ) + COLUMN_GAP_MM
    row_height = max(
        (item.manifest.height_mm for item in symbols.all()), default=ROW_GAP_MM
    ) + ROW_GAP_MM
    columns = max(1, int(standard.usable_width_mm // column_width))

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{standard.sheet_width_mm:g}mm" height="{standard.sheet_height_mm:g}mm" '
        f'viewBox="0 0 {standard.sheet_width_mm:g} {standard.sheet_height_mm:g}">',
        f'<rect x="{standard.margin_left_mm}" y="{standard.margin_top_mm}" '
        f'width="{standard.usable_width_mm}" height="{standard.usable_height_mm}" '
        f'fill="none" stroke="black" stroke-width="{standard.line_thin_mm}"/>',
    ]

    for index, symbol in enumerate(symbols.all()):
        column, row = index % columns, index // columns
        x = standard.margin_left_mm + column * column_width
        y = standard.margin_top_mm + row * row_height
        markers = "".join(
            f'<circle class="port" cx="{port.x_mm}" cy="{port.y_mm}" r="0.6" '
            f'fill="black"/>'
            for port in symbol.manifest.ports
        )
        parts.append(
            f'<g class="symbol" data-symbol-id="{_escape(symbol.manifest.id)}" '
            f'transform="translate({x} {y})" '
            f'stroke="black" stroke-width="{standard.line_medium_mm}" fill="none">'
            f"{symbol.body}{markers}"
            f'<text x="0" y="{symbol.manifest.height_mm + standard.text_small_mm + 1}" '
            f'font-size="{standard.text_small_mm}" stroke="none" fill="black">'
            f"{_escape(symbol.manifest.id)}</text>"
            f"</g>"
        )

    parts.append(_scale_bar(standard))
    parts.append("</svg>")
    return "".join(parts)
