"""I testi del disegno: solo quelli che aggiungono informazione, e dove vanno.

D-052 divide i ruoli: la legenda dice **cosa** e' un simbolo, il tag dice
**quanto** o **quale**. Un tag che ripetesse la denominazione gia' presente in
legenda saturerebbe la tavola senza aggiungere nulla, quindi qui non si scrive
mai il nome di un componente — solo la sua sigla e i suoi valori.

D-075 dice **dove** si scrive, e ritira la riga di richiami a fondo tavola:
«un'etichetta e' una scritta piccola vicino al proprio componente, e basta».
Il motivo e' preciso: le tubazioni sono sempre ortogonali (D-041, B1), quindi
un richiamo disegnato verticale-poi-orizzontale ha la forma **e la giacitura**
di un tubo, e sulla tavola si legge come un tubo in piu'. Quando accanto al
pezzo non c'e' posto — e solo allora — il testo si allontana con una diagonale
a **45 gradi**, l'unica giacitura che nessuna tubazione puo' avere.

Tutto cio' che si legge e' in italiano (D-051): le sigle vengono dal modello,
le unita' da questa tabella.
"""

from math import ceil, sqrt

from disegnatore_mep.graphics.standard import GraphicStandard
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import JsonPrimitive

from .geometry import PlacedLabel, PlacedSymbol, Point, RoutedTrunk

TAG_GAP_MM = 1.5
"""Stacco fra il riquadro del simbolo e la sigla scritta sopra."""

VALUE_GAP_MM = 1.5
"""Stacco fra il riquadro e il valore scritto sotto."""

SIDE_GAP_MM = 1.5
"""Stacco fra il riquadro e un testo scritto di fianco.

Stessa misura dei due precedenti: la distanza fra un pezzo e la propria scritta
non cambia con il lato su cui la scritta finisce, o le etichette della tavola
sembrano appoggiate a caso.
"""

CALLOUT_LINE_GAP_MM = 0.5
"""Interlinea fra due testi dello stesso componente."""

LINE_CLEARANCE_MM = 0.5
"""Franco fra un testo e una tubazione.

Un testo che tocca una linea si legge come se la linea gli passasse dentro
(D5). Il franco e' piccolo perche' deve solo staccarli: allargarlo spingerebbe
le etichette lontano dal proprio pezzo, che e' il difetto che D-075 corregge.
"""

ADJACENT_MAX_STEPS = 8
"""Quanti passi di griglia un testo si allontana dal proprio pezzo prima di
rinunciare al posto adiacente e passare al richiamo obliquo.

Otto passi sono venti millimetri: oltre, la scritta non e' piu' «vicina al
proprio componente» e il richiamo che la lega diventa necessario per capire di
chi parla.
"""

LEADER_MIN_LENGTH_MM = 5.0
"""Lunghezza minima della diagonale di richiamo.

Un segmento obliquo di due millimetri si legge come un errore di disegno, non
come un richiamo: la diagonale deve essere abbastanza lunga da dichiarare la
propria giacitura al primo sguardo (D2).
"""

LEADER_MAX_STEPS = 24
"""Quante volte la diagonale si allunga di un passo cercando spazio libero."""

CHAR_WIDTH_RATIO = 0.6
"""Larghezza media di un carattere rispetto al corpo, per un sans-serif.

Stima: la tavola non incorpora metriche di font. Serve a capire se due testi si
sovrappongono, quindi un errore in eccesso e' innocuo.
"""

TOLERANCE_MM = 1e-6

SIDES: tuple[str, ...] = ("above", "below", "right", "left")
"""L'ordine in cui si cerca un posto adiacente: sopra, sotto, destra, sinistra.

Fisso, quindi deterministico. Il lato **proprio** del testo — sopra per la
sigla, sotto per i valori — viene provato per primo, e questo e' l'ordine dei
rimanenti.
"""

DIAGONALS: tuple[tuple[int, int], ...] = ((1, -1), (1, 1), (-1, -1), (-1, 1))
"""Le quattro diagonali del richiamo: alto-destra, basso-destra, alto-sinistra,
basso-sinistra. La prima e' quella che si legge meglio su una tavola scritta da
sinistra a destra, e le altre servono quando quella e' occupata."""

UNITS: dict[str, str] = {
    "volume_l": "l",
    "flow_rate_m3h": "m³/h",
    "power_kw": "kW",
    "head_kpa": "kPa",
    "diameter_dn": "DN",
    "temperature_c": "°C",
}
"""Unita' delle proprieta' che si scrivono in tavola.

Una proprieta' che non compare qui non viene stampata: meglio non dirlo che
dirlo senza unita', e la distinta la riportera' comunque per intero.
"""

Box = tuple[float, float, float, float]
"""Un riquadro come `(sinistra, alto, destra, basso)`, in millimetri di carta."""


def format_value(key: str, value: JsonPrimitive) -> str | None:
    unit = UNITS.get(key)
    if unit is None or value is None or isinstance(value, bool):
        return None
    if key == "diameter_dn":
        return f"{unit}{value:g}" if isinstance(value, int | float) else f"{unit}{value}"
    if isinstance(value, float):
        return f"{value:g}".replace(".", ",") + f" {unit}"
    return f"{value} {unit}"


def text_width_mm(text: str, height_mm: float) -> float:
    return len(text) * height_mm * CHAR_WIDTH_RATIO


def _overlap(first: Box, second: Box) -> bool:
    """Vero se i due riquadri condividono superficie: toccarsi sul filo non conta."""
    return (
        first[0] < second[2] - TOLERANCE_MM
        and second[0] < first[2] - TOLERANCE_MM
        and first[1] < second[3] - TOLERANCE_MM
        and second[1] < first[3] - TOLERANCE_MM
    )


def _symbol_box(item: PlacedSymbol) -> Box:
    return (item.origin.x_mm, item.origin.y_mm, item.right_mm, item.bottom_mm)


def _text_box(anchor: Point, width_mm: float, height_mm: float) -> Box:
    """Il riquadro di un testo, dalla propria base: l'ancoraggio e' la base a
    sinistra, come l'`x`/`y` di un `<text>` SVG."""
    return (
        anchor.x_mm,
        anchor.y_mm - height_mm,
        anchor.x_mm + width_mm,
        anchor.y_mm,
    )


def _line_boxes(routes: list[RoutedTrunk] | None) -> list[Box]:
    """Ogni tratto delle tubazioni come riquadro, gia' allargato del franco.

    I tratti sono ortogonali (B1), quindi il riquadro che li contiene **e'** il
    tratto: non serve una intersezione segmento-riquadro, basta confrontare due
    riquadri come si fa con i simboli.
    """
    boxes: list[Box] = []
    for route in routes or []:
        for segment in route.segments:
            for before, after in zip(segment, segment[1:], strict=False):
                boxes.append(
                    (
                        min(before.x_mm, after.x_mm) - LINE_CLEARANCE_MM,
                        min(before.y_mm, after.y_mm) - LINE_CLEARANCE_MM,
                        max(before.x_mm, after.x_mm) + LINE_CLEARANCE_MM,
                        max(before.y_mm, after.y_mm) + LINE_CLEARANCE_MM,
                    )
                )
    return boxes


def _crosses(before: Point, after: Point, box: Box) -> bool:
    """Vero se il segmento attraversa l'interno del riquadro.

    Serve per il richiamo, che e' obliquo: il suo riquadro d'ingombro coprirebbe
    mezzo foglio e direbbe che passa dappertutto. Ritaglio parametrico del
    segmento contro le due fasce del riquadro (Liang-Barsky).
    """
    origin = (before.x_mm, before.y_mm)
    delta = (after.x_mm - before.x_mm, after.y_mm - before.y_mm)
    low, high = 0.0, 1.0
    for axis, (lower, upper) in enumerate(((box[0], box[2]), (box[1], box[3]))):
        if abs(delta[axis]) <= TOLERANCE_MM:
            if not lower + TOLERANCE_MM < origin[axis] < upper - TOLERANCE_MM:
                return False
            continue
        first = (lower - origin[axis]) / delta[axis]
        second = (upper - origin[axis]) / delta[axis]
        low = max(low, min(first, second))
        high = min(high, max(first, second))
    return low < high - TOLERANCE_MM


def _texts_of(
    item: PlacedSymbol, properties: dict[str, dict[str, JsonPrimitive]]
) -> list[tuple[str, str, str]]:
    """Sigla e valori di un componente, nell'ordine in cui si scrivono."""
    texts: list[tuple[str, str, str]] = []
    if item.tag:
        texts.append((f"{item.component_id}-tag", item.tag, "tag"))
    for key in sorted(properties.get(item.component_id, {})):
        value = format_value(key, properties[item.component_id][key])
        if value is not None:
            texts.append((f"{item.component_id}-{key}", value, "data"))
    return texts


def place_labels(
    project: ProjectModel,
    placed: list[PlacedSymbol],
    standard: GraphicStandard,
    callout_y_mm: float | None = None,
    routes: list[RoutedTrunk] | None = None,
) -> list[PlacedLabel]:
    """Sigle e valori, scritti piccoli accanto al proprio componente (D-075).

    La sigla va **sopra** il riquadro, i valori **sotto**, senza alcuna linea di
    richiamo: il testo sta vicino a cio' che nomina, e non serve seguire niente
    per capire di chi parla (D1).

    Il posto si cerca in ordine fisso — sopra, sotto, destra, sinistra, poi un
    passo di griglia piu' lontano, fino a `ADJACENT_MAX_STEPS` — e si scarta
    ogni posizione che si sovrapponga a un simbolo, a un'altra etichetta o a una
    tubazione. `routes` porta proprio quest'ultima: senza, un testo puo' cadere
    sopra una linea senza che nulla se ne accorga. Resta opzionale perche' i
    testi si posano anche quando le tratte non sono ancora instradate.

    Solo quando nessun posto adiacente e' libero il testo si allontana, e allora
    il richiamo e' **una diagonale a 45 gradi** lunga almeno
    `LEADER_MIN_LENGTH_MM`, mai una spezzata ortogonale (D2, D3).

    `callout_y_mm` e' il vecchio meccanismo della riga di richiami a fondo
    tavola, che D-075 **ritira**: resta soltanto perche' la catena lo passa
    ancora, e passandolo si ottiene il comportamento vecchio. Il comportamento
    di D-075 e' quello predefinito.

    Deterministico: l'ordine segue quello dei simboli posati, e a parita' di
    ingombro la ricerca percorre sempre le stesse posizioni nello stesso ordine.
    """
    properties = {item.id: item.properties for item in project.components}
    height = standard.text_small_mm
    step = standard.grid_mm
    taken: list[Box] = [_symbol_box(item) for item in placed]
    lines = _line_boxes(routes)
    labels: list[PlacedLabel] = []

    def free(box: Box) -> bool:
        return not any(_overlap(box, other) for other in (*taken, *lines))

    def free_slot(x_mm: float, y_mm: float, text: str, upward: bool) -> Point:
        """Il primo posto libero, cercato **allontanandosi** dal simbolo.

        Serve al solo meccanismo ritirato dei richiami a fondo tavola.
        """
        width = text_width_mm(text, height)
        stride = -height if upward else height
        candidate_y = y_mm
        for _ in range(24):
            box = (x_mm, candidate_y - height, x_mm + width, candidate_y)
            if free(box):
                taken.append(box)
                return Point(x_mm=x_mm, y_mm=candidate_y)
            candidate_y += stride
        taken.append((x_mm, candidate_y - height, x_mm + width, candidate_y))
        return Point(x_mm=x_mm, y_mm=candidate_y)

    def anchor_at(
        item: PlacedSymbol, side: str, slot: int, ring: int, width_mm: float
    ) -> Point:
        """L'ancoraggio di un testo su un lato del simbolo.

        `slot` conta i testi gia' posati su quel lato — e' l'interlinea — e
        `ring` di quanti passi di griglia ci si e' allontanati. Sopra e sotto il
        testo si centra sul riquadro, restando su un nodo della griglia; di
        fianco si centra in quota.
        """
        centred = item.origin.x_mm + round((item.width_mm - width_mm) / 2 / step) * step
        stack = slot * (height + CALLOUT_LINE_GAP_MM)
        away = ring * step
        if side == "above":
            return Point(
                x_mm=centred, y_mm=item.origin.y_mm - TAG_GAP_MM - stack - away
            )
        if side == "below":
            return Point(
                x_mm=centred,
                y_mm=item.bottom_mm + VALUE_GAP_MM + height + stack + away,
            )
        middle = item.origin.y_mm + item.height_mm / 2 + height / 2 + stack
        if side == "right":
            return Point(x_mm=item.right_mm + SIDE_GAP_MM + away, y_mm=middle)
        return Point(
            x_mm=item.origin.x_mm - SIDE_GAP_MM - width_mm - away, y_mm=middle
        )

    def leader_corner(item: PlacedSymbol, way: tuple[int, int]) -> Point:
        """Lo spigolo da cui parte la diagonale: quello verso cui essa punta."""
        return Point(
            x_mm=item.right_mm if way[0] > 0 else item.origin.x_mm,
            y_mm=item.origin.y_mm if way[1] < 0 else item.bottom_mm,
        )

    def ladder(
        item: PlacedSymbol, width_mm: float
    ) -> tuple[Point, Point]:
        """Il primo posto raggiungibile con una diagonale a 45 gradi.

        La diagonale parte da uno spigolo del simbolo e finisce sulla base del
        testo: un solo segmento obliquo, nessuna piega ad angolo retto. Si
        allunga di un passo per volta, quindi il posto scelto e' il piu' vicino
        fra quelli liberi.
        """
        reach = ceil(LEADER_MIN_LENGTH_MM / sqrt(2) / step) * step

        def reached(way: tuple[int, int], span: float) -> tuple[Point, Point]:
            start = leader_corner(item, way)
            return start, Point(
                x_mm=start.x_mm + way[0] * span, y_mm=start.y_mm + way[1] * span
            )

        for ring in range(LEADER_MAX_STEPS):
            span = reach + ring * step
            for way in DIAGONALS:
                start, anchor = reached(way, span)
                box = _text_box(anchor, width_mm, height)
                if not free(box):
                    continue
                if any(_crosses(start, anchor, other) for other in taken):
                    continue
                if _crosses(start, anchor, box):
                    continue
                return start, anchor
        # Nemmeno una diagonale libera: si scrive comunque, sulla prima. Un
        # testo mancante e' un difetto peggiore di un testo affollato, e il
        # preflight lo misura (D5).
        return reached(DIAGONALS[0], reach)

    for item in placed:
        texts = _texts_of(item, properties)
        if not texts:
            continue

        if callout_y_mm is not None:
            # Il meccanismo ritirato da D-075: fuori dal corpo, in fondo alla
            # tavola. Resta finche' la catena lo chiede esplicitamente.
            attach = Point(
                x_mm=item.origin.x_mm + item.width_mm / 2, y_mm=item.bottom_mm
            )
            for offset, (label_id, text, role) in enumerate(texts):
                anchor = free_slot(
                    item.origin.x_mm,
                    callout_y_mm + offset * (height + CALLOUT_LINE_GAP_MM),
                    text,
                    upward=False,
                )
                labels.append(
                    PlacedLabel(
                        id=label_id,
                        text=text,
                        role=role,
                        anchor=anchor,
                        leader_from=attach if offset == 0 else None,
                    )
                )
            continue

        slots = dict.fromkeys(SIDES, 0)
        for label_id, text, role in texts:
            width = text_width_mm(text, height)
            own = "above" if role == "tag" else "below"
            order = (own, *(side for side in SIDES if side != own))
            spot: Point | None = None
            start: Point | None = None
            for ring in range(ADJACENT_MAX_STEPS + 1):
                for side in order:
                    candidate = anchor_at(item, side, slots[side], ring, width)
                    if free(_text_box(candidate, width, height)):
                        spot = candidate
                        slots[side] += 1
                        break
                if spot is not None:
                    break
            if spot is None:
                start, spot = ladder(item, width)
            taken.append(_text_box(spot, width, height))
            labels.append(
                PlacedLabel(
                    id=label_id,
                    text=text,
                    role=role,
                    anchor=spot,
                    leader_from=start,
                )
            )
    return labels
