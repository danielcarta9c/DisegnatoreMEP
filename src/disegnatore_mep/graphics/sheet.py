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

from dataclasses import dataclass

from disegnatore_mep.layout.geometry import Point, RoutedTrunk, SheetGeometry
from disegnatore_mep.layout.legend import style_for

from .frame import Rect, SheetFrame
from .registry import SymbolRegistry

DRAFT_MARK = "BOZZA — cartiglio non compilato"
"""Marcatura della bozza: una tavola finale richiede il cartiglio completo."""

ARROW_LENGTH_MM = 2.0
"""Lunghezza della freccia di verso sulle tubazioni."""

ARROW_HALF_WIDTH_MM = 1.0

LEGEND_SWATCH_MM = 8.0
"""Lunghezza del tratto campione accanto a una voce di legenda."""

LEGEND_TEXT_GAP_MM = 2.0
CROSS_REFERENCE_RADIUS_MM = 2.0

CROSSING_ARC_RADIUS_MM = 1.25
"""Raggio dello scavallo: mezzo passo di griglia (D-079, CONV-GRAFICA-004).

Grande abbastanza da leggersi come un archetto e non come un ispessimento,
piccolo abbastanza da non toccare la corsia accanto, che dista un passo.
"""

JUNCTION_DOT_WIDTHS = 4.0
"""Diametro del pallino di collegamento, in spessori di tratto.

UNI 9511 Tab. 1, tramite SRC-016: un incrocio **con** connessione e una
derivazione portano un cerchio pieno di diametro quattro volte lo spessore
della linea; l'incrocio senza connessione porta invece lo scavallo (D-079).
Insieme, i due segni non lasciano ambiguita'.
"""

MARK_ROUNDING_DIGITS = 3
"""Cifre con cui si confrontano due punti prima di dirli lo stesso punto.

Due tratte arrivano allo stesso nodo per strade diverse: senza arrotondamento
un errore in fondo alla mantissa le farebbe risultare in due punti distinti.
"""

TOLERANCE_MM = 1e-6


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


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


def _key(point: Point) -> tuple[float, float]:
    return (
        round(point.x_mm, MARK_ROUNDING_DIGITS),
        round(point.y_mm, MARK_ROUNDING_DIGITS),
    )


def _on_stretch(before: Point, after: Point, point: Point) -> bool:
    """Vero se il punto cade sul tratto, estremi compresi."""
    if abs(before.x_mm - after.x_mm) <= TOLERANCE_MM:
        return (
            abs(point.x_mm - before.x_mm) <= TOLERANCE_MM
            and min(before.y_mm, after.y_mm) - TOLERANCE_MM
            <= point.y_mm
            <= max(before.y_mm, after.y_mm) + TOLERANCE_MM
        )
    if abs(before.y_mm - after.y_mm) <= TOLERANCE_MM:
        return (
            abs(point.y_mm - before.y_mm) <= TOLERANCE_MM
            and min(before.x_mm, after.x_mm) - TOLERANCE_MM
            <= point.x_mm
            <= max(before.x_mm, after.x_mm) + TOLERANCE_MM
        )
    return False


def _hoppable(before: Point, after: Point, point: Point) -> bool:
    """Vero se su questo tratto **verticale** l'archetto ci sta per intero.

    «Un incrocio che cade su una piega non si scavalca — un archetto su un
    angolo non si legge» (D-079). Vale anche per un capo di spezzata: da un
    lato l'archetto non avrebbe linea da scavalcare.
    """
    if abs(before.x_mm - after.x_mm) > TOLERANCE_MM:
        return False
    if not _on_stretch(before, after, point):
        return False
    low, high = min(before.y_mm, after.y_mm), max(before.y_mm, after.y_mm)
    return (
        point.y_mm - low >= CROSSING_ARC_RADIUS_MM - TOLERANCE_MM
        and high - point.y_mm >= CROSSING_ARC_RADIUS_MM - TOLERANCE_MM
    )


def _local(route: RoutedTrunk, point: Point) -> str | None:
    """Come la tratta passa per quel punto: verticale, orizzontale, o su una piega.

    E' la domanda che decide chi scavalca: la convenzione dice che **la linea
    verticale scavalca e l'orizzontale prosegue intera**, quindi serve sapere
    la giacitura del tratto che contiene il punto **in quella tratta**, non in
    generale. `None` se la tratta li' non passa — puo' succedere: un accessorio
    in linea ne interrompe la spezzata.
    """
    seen: set[str] = set()
    room = False
    for segment in route.segments:
        for before, after in zip(segment, segment[1:], strict=False):
            if not _on_stretch(before, after, point):
                continue
            if abs(before.x_mm - after.x_mm) <= TOLERANCE_MM:
                seen.add("vertical")
                room = room or _hoppable(before, after, point)
            else:
                seen.add("horizontal")
    if not seen:
        return None
    if len(seen) > 1:
        return "corner"
    if "horizontal" in seen:
        return "horizontal"
    return "vertical" if room else "corner"


@dataclass(frozen=True)
class Mark:
    """Un segno su un punto notevole, con la tratta che gli da' il colore."""

    route_index: int
    at: Point


@dataclass(frozen=True)
class SheetMarks:
    """Scavalli e pallini di una tavola, con il conto di cio' che si e' saltato."""

    hops: tuple[Mark, ...]
    junctions: tuple[Mark, ...]
    skipped_on_bends: int
    """Incroci che cadono su una piega: non si scavallano (D-079)."""
    skipped_as_junctions: int
    """Incroci che sono invece collegamenti: portano il pallino, non l'archetto."""
    skipped_without_a_crossed_line: int
    """Incroci in cui non c'e' piu' una linea da scavalcare, o due tratte che
    non si incrociano affatto — l'ultimo tratto condiviso contro un attacco
    comune, che sulla tavola e' una derivazione (D-062)."""


def sheet_marks(sheet: SheetGeometry) -> SheetMarks:
    """I segni sui punti notevoli, ricavati dalla sola geometria instradata.

    Due punti si somigliano e vogliono segni opposti (D-079):

    - un **incrocio** e' un punto in cui due tratte si attraversano e non si
      collegano: prende lo **scavallo**, e a scavallare e' la verticale;
    - un **collegamento** e' un punto in cui due tratte si toccano davvero,
      cioe' almeno una delle due **finisce** li', sullo stesso attacco: prende
      il **pallino** pieno.

    La distinzione si ricava qui perche' la geometria la porta gia': un capo di
    spezzata e' un attacco. Serve davvero: l'instradamento registra come
    incrocio ogni nodo gia' percorso da un'altra tratta, compresi gli attacchi
    condivisi, che incroci non sono.
    """
    junctions: list[Mark] = []
    marked: set[tuple[float, float]] = set()
    for index, route in enumerate(sheet.routes):
        if not route.segments:
            continue
        for point in (route.segments[0][0], route.segments[-1][-1]):
            key = _key(point)
            if key in marked:
                continue
            meets = any(
                other != index and _local(sheet.routes[other], point) is not None
                for other in range(len(sheet.routes))
            )
            if meets:
                marked.add(key)
                junctions.append(Mark(route_index=index, at=point))

    hops: list[Mark] = []
    on_bends = 0
    as_junctions = 0
    without_a_line = 0
    seen: set[tuple[float, float]] = set()
    for route in sheet.routes:
        for point in route.crossings:
            key = _key(point)
            if key in seen:
                continue
            seen.add(key)
            if key in marked:
                as_junctions += 1
                continue
            kinds = [_local(item, point) for item in sheet.routes]
            vertical = [index for index, kind in enumerate(kinds) if kind == "vertical"]
            horizontal = any(kind == "horizontal" for kind in kinds)
            if vertical and horizontal:
                hops.append(Mark(route_index=vertical[0], at=point))
            elif any(kind == "corner" for kind in kinds):
                on_bends += 1
            else:
                without_a_line += 1

    return SheetMarks(
        hops=tuple(hops),
        junctions=tuple(junctions),
        skipped_on_bends=on_bends,
        skipped_as_junctions=as_junctions,
        skipped_without_a_crossed_line=without_a_line,
    )


def _interrupted(polyline: list[Point], hops: list[Point]) -> list[list[Point]]:
    """La spezzata interrotta a ogni scavallo: l'archetto prende il posto del tratto.

    Un archetto disegnato **sopra** una linea intera non e' uno scavallo: e' un
    semicerchio con la propria corda. La linea si spezza davvero, e i due
    monconi si fermano a un raggio dal punto.
    """
    pieces: list[list[Point]] = []
    current: list[Point] = [polyline[0]]
    for before, after in zip(polyline, polyline[1:], strict=False):
        here = [point for point in hops if _hoppable(before, after, point)]
        way = 1.0 if after.y_mm >= before.y_mm else -1.0
        here.sort(key=lambda point: point.y_mm * way)
        for point in here:
            current.append(
                Point(x_mm=point.x_mm, y_mm=point.y_mm - CROSSING_ARC_RADIUS_MM * way)
            )
            pieces.append(current)
            current = [
                Point(x_mm=point.x_mm, y_mm=point.y_mm + CROSSING_ARC_RADIUS_MM * way)
            ]
        current.append(after)
    pieces.append(current)
    return [piece for piece in pieces if len(piece) >= 2]


def _hop_arc(point: Point, colour: str, width_mm: float) -> str:
    """L'archetto che scavalca, sempre sulla verticale e sempre verso destra.

    Il verso della gobba e' una convenzione, e come tale e' fissa: due scavalli
    che si gonfiano da parti diverse sulla stessa tavola si leggono come due
    segni diversi. Il tratteggio del fluido non si applica — un archetto lungo
    due millimetri e mezzo, tratteggiato, sparisce.
    """
    return (
        f'<path class="crossing-hop" '
        f'd="M{point.x_mm:g} {point.y_mm - CROSSING_ARC_RADIUS_MM:g} '
        f"A{CROSSING_ARC_RADIUS_MM:g} {CROSSING_ARC_RADIUS_MM:g} 0 0 1 "
        f'{point.x_mm:g} {point.y_mm + CROSSING_ARC_RADIUS_MM:g}" '
        f'fill="none" stroke="{colour}" stroke-width="{width_mm:g}"/>'
    )


def _junction_dot(point: Point, colour: str, width_mm: float) -> str:
    """Il pallino pieno del collegamento: diametro quattro volte il tratto."""
    return (
        f'<circle class="junction" cx="{point.x_mm:g}" cy="{point.y_mm:g}" '
        f'r="{JUNCTION_DOT_WIDTHS * width_mm / 2:g}" fill="{colour}" stroke="none"/>'
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

    # Qui si stendeva la **linea di terra**, tratteggiata da un bordo all'altro
    # del foglio. Non si disegna piu' (D-116). Il PM: «il disegno di centrale
    # non ha una linea di terra».
    #
    # Cio' che al suo posto puo' esserci — «una linea sotto il serbatoio,
    # **circoscritta al serbatoio**, per indicare che e' appoggiato e non
    # appeso» — e' un segno del **simbolo**, non una quota del foglio, e non si
    # scrive qui finche' non e' definito: quali macchine lo portano, quanto
    # sporge, se e' tratteggiato. Inventarlo adesso rifarebbe l'errore che
    # D-116 corregge — dedurre una regola grafica invece di riceverla.

    # Incroci e collegamenti hanno segni opposti e vanno decisi insieme, prima
    # di disegnare: lo scavallo interrompe la linea che lo porta (D-079).
    marks = sheet_marks(sheet)
    for index, route in enumerate(sheet.routes):
        colour, dash = style_for(route.medium, route.supply)
        dash_attribute = "" if dash == "none" else f' stroke-dasharray="{dash}"'
        hops = [mark.at for mark in marks.hops if mark.route_index == index]
        for segment in route.segments:
            for piece in _interrupted(segment, hops):
                points = " ".join(f"{item.x_mm:g},{item.y_mm:g}" for item in piece)
                parts.append(
                    f'<polyline class="run" points="{points}" fill="none" '
                    f'stroke="{colour}" stroke-width="{standard.line_medium_mm:g}"'
                    f"{dash_attribute}/>"
                )
            parts.extend(
                _hop_arc(point, colour, standard.line_medium_mm)
                for point in hops
                if any(
                    _hoppable(before, after, point)
                    for before, after in zip(segment, segment[1:], strict=False)
                )
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

    # Il pallino del collegamento sta **sopra** i simboli: cade su un attacco, e
    # sotto il bocchello non si vedrebbe.
    for mark in marks.junctions:
        route = sheet.routes[mark.route_index]
        parts.append(
            _junction_dot(
                mark.at, style_for(route.medium, route.supply)[0], standard.line_medium_mm
            )
        )

    for label in sheet.labels:
        if label.leader_from is not None:
            # Il richiamo e' **quello che il layout ha deciso**: i due capi si
            # uniscono come stanno. Prima il renderer ci ricavava una spezzata
            # verticale-poi-orizzontale, cioe' rimetteva sulla tavola l'angolo
            # retto che D-075 vieta, qualunque cosa il layout avesse deciso.
            parts.append(
                f'<polyline class="leader" points="'
                f"{label.leader_from.x_mm:g},{label.leader_from.y_mm:g} "
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
