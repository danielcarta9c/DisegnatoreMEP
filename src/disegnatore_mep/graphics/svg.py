"""Emettitore SVG a misura reale.

Il foglio dichiara larghezza e altezza in millimetri e un `viewBox` numerico
identico, cosi' che una unita' utente corrisponda esattamente a un millimetro
di carta. Stampando senza adattamento, il righello deve confermare la barra di
scala.
"""

import math

from .registry import SymbolRegistry
from .standard import A3_LANDSCAPE, GraphicStandard

SCALE_BAR_MM = 100.0
COLUMN_GAP_MM = 10.0
ROW_GAP_MM = 14.0
SCALE_BAR_TICK_HALF_MM = 1.5
SCALE_BAR_LABEL_GAP_MM = 2.0
SYMBOL_LABEL_GAP_MM = 1.0
LABEL_LINES = 1
"""Righe di etichetta sotto ogni simbolo: la sola denominazione italiana (D-051)."""
LABEL_CHAR_WIDTH_RATIO = 0.6
"""Larghezza media di un carattere rispetto al corpo, per un sans-serif.

Stima: il foglio non incorpora metriche di font. Serve a dimensionare la colonna
perche' un nome lungo non si sovrapponga al simbolo accanto, quindi una stima
prudente e' sufficiente e un errore in eccesso e' innocuo.
"""
PORT_MARKER_RADIUS_MM = 0.6


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
        f'<line x1="{x}" y1="{y - SCALE_BAR_TICK_HALF_MM}" '
        f'x2="{x}" y2="{y + SCALE_BAR_TICK_HALF_MM}"/>'
        f'<line x1="{x + SCALE_BAR_MM}" y1="{y - SCALE_BAR_TICK_HALF_MM}" '
        f'x2="{x + SCALE_BAR_MM}" y2="{y + SCALE_BAR_TICK_HALF_MM}"/>'
        f'<text x="{x + SCALE_BAR_MM / 2}" y="{y - SCALE_BAR_LABEL_GAP_MM}" '
        f'font-size="{standard.text_small_mm}" text-anchor="middle" '
        # La didascalia e' derivata dalla costante: scritta a mano, cambiare
        # SCALE_BAR_MM avrebbe fatto misurare col righello contro un numero falso.
        f'stroke="none" fill="black">{SCALE_BAR_MM:g} mm</text>'
        f"</g>"
    )


def render_symbol_sheet(
    symbols: SymbolRegistry, standard: GraphicStandard = A3_LANDSCAPE
) -> str:
    # This function accepts any GraphicStandard, so the two assumptions its
    # layout makes about the paper are checked instead of assumed. Both hold for
    # A3_LANDSCAPE, but only by coincidence.
    # Una riga di etichetta per simbolo: la denominazione italiana che un
    # tecnico legge (D-051). L'identificativo di macchina non si stampa.
    label_block_mm = LABEL_LINES * (standard.text_small_mm + SYMBOL_LABEL_GAP_MM)
    if label_block_mm > ROW_GAP_MM:
        raise ValueError(
            f"the {ROW_GAP_MM:g}mm row gap leaves no room for the "
            f"{LABEL_LINES} label lines of {standard.text_small_mm:g}mm each "
            f"plus their {SYMBOL_LABEL_GAP_MM:g}mm gaps"
        )
    if standard.usable_width_mm < SCALE_BAR_MM:
        raise ValueError(
            f"the {SCALE_BAR_MM:g}mm scale bar does not fit the "
            f"{standard.usable_width_mm:g}mm usable width"
        )

    all_symbols = symbols.all()
    # La colonna deve contenere il piu' largo fra il simbolo e la sua etichetta:
    # le denominazioni italiane sono piu' lunghe degli identificativi che
    # stavano qui prima, e dimensionare sul solo simbolo le faceva collidere.
    widest_symbol = max(
        (item.manifest.width_mm for item in all_symbols), default=COLUMN_GAP_MM
    )
    widest_label = max(
        (
            len(item.manifest.name) * standard.text_small_mm * LABEL_CHAR_WIDTH_RATIO
            for item in all_symbols
        ),
        default=0.0,
    )
    column_width = max(widest_symbol, widest_label) + COLUMN_GAP_MM
    row_height = max(
        (item.manifest.height_mm for item in all_symbols), default=ROW_GAP_MM
    ) + ROW_GAP_MM

    # D-045 on the width axis: without this, `columns` is clamped to 1 and a
    # symbol wider than the usable area is drawn off the right edge in silence.
    for item in all_symbols:
        if item.manifest.width_mm + COLUMN_GAP_MM > standard.usable_width_mm:
            raise ValueError(
                f"symbol {item.manifest.id} does not fit the sheet width: its "
                f"{item.manifest.width_mm + COLUMN_GAP_MM:g}mm column "
                f"({item.manifest.width_mm:g}mm wide plus the {COLUMN_GAP_MM:g}mm "
                f"column gap) exceeds the {standard.usable_width_mm:g}mm usable width "
                f"(symbols are never shrunk to fit; use a larger sheet)"
            )
    columns = max(1, int(standard.usable_width_mm // column_width))

    total = len(all_symbols)
    rows_needed = math.ceil(total / columns)
    if rows_needed * row_height > standard.usable_height_mm:
        capacity = columns * int(standard.usable_height_mm // row_height)
        raise ValueError(
            f"{total} symbols do not fit on one sheet: at most {capacity} fit at "
            f"fixed scale on a {standard.sheet_width_mm:g}x{standard.sheet_height_mm:g}mm "
            f"sheet (symbols are never shrunk to fit; split the library across "
            f"additional sheets)"
        )

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{standard.sheet_width_mm:g}mm" height="{standard.sheet_height_mm:g}mm" '
        f'viewBox="0 0 {standard.sheet_width_mm:g} {standard.sheet_height_mm:g}">',
        f'<rect x="{standard.margin_left_mm}" y="{standard.margin_top_mm}" '
        f'width="{standard.usable_width_mm}" height="{standard.usable_height_mm}" '
        f'fill="none" stroke="black" stroke-width="{standard.line_thin_mm}"/>',
    ]

    for index, symbol in enumerate(all_symbols):
        column, row = index % columns, index // columns
        x = standard.margin_left_mm + column * column_width
        y = standard.margin_top_mm + row * row_height
        markers = "".join(
            f'<circle class="port" cx="{port.x_mm}" cy="{port.y_mm}" '
            f'r="{PORT_MARKER_RADIUS_MM}" fill="black"/>'
            for port in symbol.manifest.ports
        )
        parts.append(
            f'<g class="symbol" data-symbol-id="{_escape(symbol.manifest.id)}" '
            f'transform="translate({x} {y})" '
            f'stroke="black" stroke-width="{standard.line_medium_mm}" fill="none">'
            f"{symbol.body}{markers}"
            f'<text class="symbol-name" x="0" '
            f'y="{symbol.manifest.height_mm + standard.text_small_mm + SYMBOL_LABEL_GAP_MM}" '
            f'font-size="{standard.text_small_mm}" stroke="none" fill="black">'
            f"{_escape(symbol.manifest.name)}</text>"
            f"</g>"
        )

    parts.append(_scale_bar(standard))
    parts.append("</svg>")
    return "".join(parts)
