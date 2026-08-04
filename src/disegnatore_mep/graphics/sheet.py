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

from disegnatore_mep.layout.geometry import Point, SheetGeometry
from disegnatore_mep.layout.legend import style_for

from .frame import Rect, SheetFrame
from .registry import SymbolRegistry

DRAFT_MARK = "BOZZA — cartiglio non compilato"
"""Marcatura della bozza: una tavola finale richiede il cartiglio completo."""

GROUND_HATCH_PITCH_MM = 4.0
"""Passo del tratteggio della linea di terra."""

GROUND_HATCH_DEPTH_MM = 2.5
"""Profondita' dei trattini sotto la linea di terra."""

ARROW_LENGTH_MM = 2.0
"""Lunghezza della freccia di verso sulle tubazioni."""

ARROW_HALF_WIDTH_MM = 1.0

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


def _frange(start: float, stop: float, step: float) -> list[float]:
    values: list[float] = []
    current = start
    while current < stop:
        values.append(current)
        current += step
    return values


def _flow_arrow(segment: list[Point], colour: str) -> str:
    """Una freccia a meta' del tratto piu' lungo: il verso si legge dal disegno."""
    if len(segment) < 2:
        return ""
    best = max(
        zip(segment, segment[1:], strict=False),
        key=lambda pair: abs(pair[1].x_mm - pair[0].x_mm)
        + abs(pair[1].y_mm - pair[0].y_mm),
    )
    before, after = best
    length = abs(after.x_mm - before.x_mm) + abs(after.y_mm - before.y_mm)
    if length < 2 * ARROW_LENGTH_MM:
        return ""
    dx = (after.x_mm - before.x_mm) / length
    dy = (after.y_mm - before.y_mm) / length
    tip_x = before.x_mm + dx * length / 2
    tip_y = before.y_mm + dy * length / 2
    back_x, back_y = tip_x - dx * ARROW_LENGTH_MM, tip_y - dy * ARROW_LENGTH_MM
    left_x, left_y = back_x - dy * ARROW_HALF_WIDTH_MM, back_y + dx * ARROW_HALF_WIDTH_MM
    right_x, right_y = back_x + dy * ARROW_HALF_WIDTH_MM, back_y - dx * ARROW_HALF_WIDTH_MM
    return (
        f'<path class="flow-arrow" d="M{tip_x:g} {tip_y:g} L{left_x:g} {left_y:g} '
        f'L{right_x:g} {right_y:g} Z" fill="{colour}" stroke="none"/>'
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

    # La linea di terra: le macchine ci appoggiano sopra, e senza di essa il
    # disegno sembra sospeso nel vuoto.
    ground = sheet.ground_line_y_mm
    if ground is not None:
        body = frame.drawing_rect_mm
        hatches = "".join(
            f'<line x1="{x:g}" y1="{ground:g}" x2="{x - GROUND_HATCH_DEPTH_MM:g}" '
            f'y2="{ground + GROUND_HATCH_DEPTH_MM:g}"/>'
            for x in _frange(body.x_mm + GROUND_HATCH_PITCH_MM, body.right_mm, GROUND_HATCH_PITCH_MM)
        )
        parts.append(
            f'<g class="ground" stroke="black" stroke-width="{standard.line_thin_mm:g}">'
            f'<line x1="{body.x_mm:g}" y1="{ground:g}" x2="{body.right_mm:g}" '
            f'y2="{ground:g}" stroke-width="{standard.line_medium_mm:g}"/>'
            f"{hatches}</g>"
        )

    for route in sheet.routes:
        colour, dash = style_for(route.medium, route.supply)
        dash_attribute = "" if dash == "none" else f' stroke-dasharray="{dash}"'
        for segment in route.segments:
            points = " ".join(f"{item.x_mm:g},{item.y_mm:g}" for item in segment)
            parts.append(
                f'<polyline class="run" points="{points}" fill="none" '
                f'stroke="{colour}" stroke-width="{standard.line_medium_mm:g}"'
                f"{dash_attribute}/>"
            )
            parts.append(_flow_arrow(segment, colour))

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
        if label.leader_from is not None:
            parts.append(
                f'<polyline class="leader" points="'
                f"{label.leader_from.x_mm:g},{label.leader_from.y_mm:g} "
                f"{label.leader_from.x_mm:g},{label.anchor.y_mm:g} "
                f'{label.anchor.x_mm:g},{label.anchor.y_mm:g}" fill="none" '
                f'stroke="black" stroke-width="{standard.line_thin_mm:g}"/>'
            )
        parts.append(
            f'<text class="label" data-role="{_escape(label.role)}" '
            f'x="{label.anchor.x_mm:g}" y="{label.anchor.y_mm:g}" '
            f'font-size="{standard.text_small_mm:g}" fill="black">'
            f"{_escape(label.text)}</text>"
        )

    # Simbolo e denominazione si centrano l'uno sull'altra dentro il riquadro
    # campione. Prima il simbolo pendeva in alto a sinistra e il testo appoggiava
    # sul fondo: un collettore, largo otto volte la propria altezza, finiva un
    # riquadro sopra il proprio nome.
    for entry in sheet.legend:
        symbol = symbols.get(entry.symbol_id)
        scale = min(
            1.0,
            LEGEND_SWATCH_MM / symbol.manifest.width_mm,
            LEGEND_SWATCH_MM / symbol.manifest.height_mm,
        )
        top = entry.anchor.y_mm - LEGEND_SWATCH_MM
        left = entry.anchor.x_mm + (LEGEND_SWATCH_MM - symbol.manifest.width_mm * scale) / 2
        middle = top + (LEGEND_SWATCH_MM - symbol.manifest.height_mm * scale) / 2
        parts.append(
            f'<g class="legend-symbol" data-symbol-id="{_escape(entry.symbol_id)}" '
            f'transform="translate({left:g} {middle:g}) scale({scale:g})" '
            f'stroke="black" stroke-width="{standard.line_thin_mm / scale:g}" fill="none">'
            f"{symbol.body}</g>"
            f'<text class="legend-name" '
            f'x="{entry.anchor.x_mm + LEGEND_SWATCH_MM + LEGEND_TEXT_GAP_MM:g}" '
            f'y="{top + LEGEND_SWATCH_MM / 2 + standard.text_small_mm / 2:g}" '
            f'font-size="{standard.text_small_mm:g}" '
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
