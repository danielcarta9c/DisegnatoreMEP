"""I testi del disegno: solo quelli che aggiungono informazione, e dove vanno.

D-052 divide i ruoli: la legenda dice **cosa** e' un simbolo, il tag dice
**quanto** o **quale**. Un tag che ripetesse la denominazione gia' presente in
legenda saturerebbe la tavola senza aggiungere nulla, quindi qui non si scrive
mai il nome di un componente — solo la sua sigla e i suoi valori.

D-075 dice **dove** si scrive, e ritira la riga di richiami a fondo tavola:
«un'etichetta e' una scritta piccola vicino al proprio componente, e basta».

**I testi sono l'ultima fase del disegno** (DRAW-003, I-025). Componenti e
rotte sono definitivi quando questo modulo entra in gioco, e niente di cio' che
decide qui puo' toccarli: un testo si posa, non sposta. E i testi hanno
**costo nullo rispetto alla geometria** (DRAW-003-R1): non entrano in nessuna
misura, candidato o funzione di costo della posa, e non bloccano mai
l'emissione della tavola. La posa e' quindi semplice e a buon fine, non un
ottimizzatore:

- ogni testo prova, in un **ordine fisso**, i posti adiacenti al proprio pezzo
  — la sigla sopra, poi sotto, a destra, a sinistra; i valori sotto per
  primi; l'indirizzo di verifica a destra per primo — prima nella fila che
  tocca il pezzo, poi in una seconda fila una riga piu' in la', e si ferma
  al primo libero da simboli, tubi, altri testi e margine, senza richiamo;
- le **sigle e i valori delle macchine** — i testi della tavola definitiva —
  se nessun posto adiacente e' libero provano un richiamo **corto** a 45
  gradi da uno spigolo del pezzo, l'unica giacitura che nessuna tubazione puo'
  avere (D-041, B1), e solo se non attraversa tubi, simboli, testi ne' altri
  richiami: un richiamo si disegna quando chiarisce, mai quando confonde;
- se nemmeno quello esiste, il testo **si omette**: la tavola esce lo stesso e
  il preflight lo dice come avviso;
- gli **indirizzi della modalita' verifica** sono un velo a buon fine, che
  serve al PO per indicare un pezzo: adiacenti se c'e' posto, altrimenti
  omessi, mai richiamati. Nessun obbligo di scriverli tutti.

La quota di terra non entra qui: non e' un ostacolo per i testi (D-121).

Tutto cio' che si legge e' in italiano (D-051): le sigle vengono dal modello,
le unita' da questa tabella.
"""

from dataclasses import dataclass, field
from math import ceil, sqrt

from disegnatore_mep.graphics.frame import Rect, SheetFrame
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

LEADER_MIN_LENGTH_MM = 5.0
"""Lunghezza minima della diagonale di richiamo.

Un segmento obliquo di due millimetri si legge come un errore di disegno, non
come un richiamo: la diagonale deve essere abbastanza lunga da dichiarare la
propria giacitura al primo sguardo (D2).
"""

LEADER_MAX_STEPS = 12
"""Quante volte la diagonale si allunga di un passo cercando un posto pulito.

Dodici passi sono poco piu' di trenta millimetri di corsa per asse: un richiamo
piu' lungo non chiarisce piu' di chi parla, e la regola (DRAW-003-R1) e' che
un richiamo si disegna solo quando chiarisce. **Taratura**, non norma: si
rivede sulle tavole reali.
"""

CHAR_WIDTH_RATIO = 0.6
"""Larghezza media di un carattere rispetto al corpo, per un sans-serif.

Stima: la tavola non incorpora metriche di font. Serve a capire se due testi si
sovrappongono, quindi un errore in eccesso e' innocuo.
"""

TOLERANCE_MM = 1e-6

SIDES_BY_ROLE: dict[str, tuple[str, ...]] = {
    "tag": ("above", "below", "right", "left"),
    "data": ("below", "above", "right", "left"),
    "address": ("right", "left", "above", "below"),
}
"""I lati che ogni ruolo prova, nell'ordine.

Il primo e' il posto preferito di D-075 e D-110 — la sigla sopra, i valori
sotto, l'indirizzo di fianco — e gli altri sono i ripieghi, sempre adiacenti:
un testo che cambia lato resta una scritta accanto al proprio pezzo, e non ha
bisogno di un richiamo per dire di chi parla (D1).
"""

ADJACENT_ROWS = 2
"""Quante file di testo si provano su ogni lato prima di rinunciare al lato.

La prima fila tocca il pezzo a meno dello stacco; la seconda sta una riga
piu' in la', oltre cio' che occupa la prima — di solito un tubo attaccato al
pezzo — e si legge ancora come la scritta di quel pezzo. Una terza fila
sarebbe gia' lontana: da li' in poi, richiamo o niente.
"""

LEADER_ROLES = frozenset({"tag", "data"})
"""I ruoli che possono portare un richiamo: i testi della tavola definitiva.

Gli indirizzi di verifica no: sono un velo a buon fine, e un groviglio di
richiami per identificare le valvole confonde piu' di quanto identifichi.
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

Segment = tuple[Point, Point]


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


def _line_segments(routes: list[RoutedTrunk] | None) -> list[Segment]:
    return [
        (before, after)
        for route in routes or []
        for segment in route.segments
        for before, after in zip(segment, segment[1:], strict=False)
    ]


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


def _turn(a: Point, b: Point, c: Point) -> float:
    return (b.x_mm - a.x_mm) * (c.y_mm - a.y_mm) - (b.y_mm - a.y_mm) * (c.x_mm - a.x_mm)


def segments_cross(first: Segment, second: Segment) -> bool:
    """Vero se i due segmenti si attraversano in un punto interno a entrambi.

    Toccarsi a un capo non e' attraversarsi: un richiamo che parte dallo
    spigolo di un simbolo tocca per forza il tubo che arriva a quell'attacco.
    """
    a, b = first
    c, d = second
    one = _turn(a, b, c) * _turn(a, b, d)
    two = _turn(c, d, a) * _turn(c, d, b)
    return one < -TOLERANCE_MM and two < -TOLERANCE_MM


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


def anchor_beside(
    item: PlacedSymbol,
    side: str,
    slot: int,
    width_mm: float,
    *,
    height_mm: float,
    step_mm: float,
) -> Point:
    """La base di un testo scritto su un lato del pezzo.

    Sopra e sotto il testo si centra sul riquadro restando su un nodo della
    griglia; di fianco sta in quota col centro del pezzo. Lo stacco dal
    riquadro vale un millimetro e mezzo perche' e' quanto deve valere: portarlo
    sul passo lo raddoppierebbe allontanando ogni scritta dal proprio pezzo,
    che e' il difetto che D-075 corregge. `slot` impila i testi dello stesso
    pezzo sullo stesso lato, uno per riga.
    """
    centred = (
        item.origin.x_mm + round((item.width_mm - width_mm) / 2 / step_mm) * step_mm
    )
    stack = slot * (height_mm + CALLOUT_LINE_GAP_MM)
    if side == "above":
        return Point(x_mm=centred, y_mm=item.origin.y_mm - TAG_GAP_MM - stack)
    if side == "below":
        return Point(
            x_mm=centred, y_mm=item.bottom_mm + VALUE_GAP_MM + height_mm + stack
        )
    middle = item.origin.y_mm + item.height_mm / 2 + height_mm / 2 + stack
    if side == "right":
        return Point(x_mm=item.right_mm + SIDE_GAP_MM, y_mm=middle)
    return Point(x_mm=item.origin.x_mm - SIDE_GAP_MM - width_mm, y_mm=middle)


def preferred_anchor(
    item: PlacedSymbol,
    role: str,
    slot: int,
    width_mm: float,
    *,
    height_mm: float,
    step_mm: float,
) -> Point:
    """La posizione preferita di un testo, secondo il suo ruolo: il primo dei
    lati di `SIDES_BY_ROLE`."""
    return anchor_beside(
        item, SIDES_BY_ROLE[role][0], slot, width_mm, height_mm=height_mm, step_mm=step_mm
    )


def _leader_corner(item: PlacedSymbol, way: tuple[int, int]) -> Point:
    """Lo spigolo da cui parte la diagonale: quello verso cui essa punta."""
    return Point(
        x_mm=item.right_mm if way[0] > 0 else item.origin.x_mm,
        y_mm=item.origin.y_mm if way[1] < 0 else item.bottom_mm,
    )


@dataclass
class _Canvas:
    """Cio' che e' gia' disegnato, e che un testo deve rispettare.

    Simboli, tubazioni e area di disegno sono definitivi; i testi e i richiami
    si aggiungono man mano che vengono posati, cosi' che chi arriva dopo veda
    chi e' arrivato prima.
    """

    area: Box
    symbols: list[Box]
    lines: list[Box]
    line_segments: list[Segment]
    texts: list[Box] = field(default_factory=list)
    leaders: list[Segment] = field(default_factory=list)

    def inside(self, box: Box) -> bool:
        return (
            box[0] >= self.area[0] - TOLERANCE_MM
            and box[1] >= self.area[1] - TOLERANCE_MM
            and box[2] <= self.area[2] + TOLERANCE_MM
            and box[3] <= self.area[3] + TOLERANCE_MM
        )

    def free(self, box: Box) -> bool:
        """Il posto e' dentro l'area e libero da simboli, tubi e altre scritte."""
        if not self.inside(box):
            return False
        return not any(
            _overlap(box, other) for other in (*self.symbols, *self.texts, *self.lines)
        )

    def leader_fits(self, start: Point, end: Point, box: Box) -> bool:
        """La diagonale non passa sopra simboli o testi — il proprio compreso —
        e non attraversa tubazioni ne' altri richiami. Un solo grado di rigore:
        un richiamo che attraversa qualcosa confonde, e allora non si disegna."""
        if _crosses(start, end, box):
            return False
        if any(_crosses(start, end, other) for other in (*self.symbols, *self.texts)):
            return False
        leader = (start, end)
        if any(segments_cross(leader, other) for other in self.line_segments):
            return False
        return not any(segments_cross(leader, other) for other in self.leaders)

    def take(self, box: Box, leader: Segment | None) -> None:
        self.texts.append(box)
        if leader is not None:
            self.leaders.append(leader)


def _leader(
    item: PlacedSymbol,
    width_mm: float,
    *,
    height_mm: float,
    step_mm: float,
    canvas: _Canvas,
) -> tuple[Point, Point] | None:
    """Il primo posto pulito raggiungibile con una diagonale corta a 45 gradi.

    La diagonale parte da uno spigolo del simbolo e finisce **sulla base del
    testo**: un solo segmento obliquo, nessuna piega. La codina orizzontale
    sotto la scritta — la «scaletta» del disegno a mano — si potrebbe
    aggiungere, e deliberatamente non c'e': porterebbe i due capi del richiamo a
    un angolo diverso da 45 gradi, e i due capi sono cio' che la geometria
    dichiara e che il preflight misura.

    Il posto si cerca allungando la diagonale di un passo per volta, quindi e'
    il piu' vicino fra i puliti; in ogni caso il testo sta dentro l'area, non
    copre niente e la diagonale non attraversa niente. Se entro la corsa
    massima non c'e' un posto cosi', non c'e' richiamo: `None`, e chi chiama
    omette il testo.
    """
    reach = ceil(LEADER_MIN_LENGTH_MM / sqrt(2) / step_mm) * step_mm
    for ring in range(LEADER_MAX_STEPS):
        span = reach + ring * step_mm
        for way in DIAGONALS:
            start = _leader_corner(item, way)
            anchor = Point(
                x_mm=start.x_mm + way[0] * span, y_mm=start.y_mm + way[1] * span
            )
            box = _text_box(anchor, width_mm, height_mm)
            if canvas.free(box) and canvas.leader_fits(start, anchor, box):
                return start, anchor
    return None


def _canvas(
    placed: list[PlacedSymbol],
    routes: list[RoutedTrunk] | None,
    standard: GraphicStandard,
    area: Rect | None,
) -> _Canvas:
    """L'area di disegno e' quella del formato, se chi chiama non la passa:
    il margine e' un conflitto come gli altri, e un testo non lo scavalca."""
    rect = area if area is not None else SheetFrame(standard=standard).drawing_rect_mm
    return _Canvas(
        area=(rect.x_mm, rect.y_mm, rect.right_mm, rect.bottom_mm),
        symbols=[_symbol_box(item) for item in placed],
        lines=_line_boxes(routes),
        line_segments=_line_segments(routes),
    )


def _settle(
    item: PlacedSymbol,
    label_id: str,
    text: str,
    role: str,
    slot: int,
    *,
    height_mm: float,
    step_mm: float,
    canvas: _Canvas,
) -> PlacedLabel | None:
    """Un testo sul primo lato libero, prima fila poi seconda; per le sigle
    delle macchine, poi, un richiamo corto e pulito; altrimenti niente."""
    width = text_width_mm(text, height_mm)
    for row in range(ADJACENT_ROWS):
        for side in SIDES_BY_ROLE[role]:
            spot = anchor_beside(
                item, side, slot + row, width, height_mm=height_mm, step_mm=step_mm
            )
            box = _text_box(spot, width, height_mm)
            if canvas.free(box):
                canvas.take(box, None)
                return PlacedLabel(id=label_id, text=text, role=role, anchor=spot)
    if role not in LEADER_ROLES:
        return None
    found = _leader(item, width, height_mm=height_mm, step_mm=step_mm, canvas=canvas)
    if found is None:
        return None
    start, spot = found
    canvas.take(_text_box(spot, width, height_mm), (start, spot))
    return PlacedLabel(id=label_id, text=text, role=role, anchor=spot, leader_from=start)


def place_addresses(
    placed: list[PlacedSymbol],
    addresses: dict[str, str],
    standard: GraphicStandard,
    *,
    routes: list[RoutedTrunk] | None = None,
    already: list[PlacedLabel] | None = None,
    floor_y_mm: float | None = None,
    area: Rect | None = None,
) -> list[PlacedLabel]:
    """L'indirizzo del nodo scritto accanto al proprio pezzo (D-110, D-111).

    E' la **terza specie di scritta** sulla tavola: la legenda dice *cosa* e' un
    simbolo, la sigla dice *quale*, l'indirizzo dice **dove** — cosi' il PO
    guarda il disegno, punta un pezzo, ne legge il codice e lo nomina.

    Si posa **dopo tutto il resto e non sposta niente**: e' un velo sopra una
    tavola gia' finita, e le due modalita' — verifica e consegna — danno percio'
    la stessa identica tavola, una con le etichette in piu'. Ed e' un velo **a
    buon fine** (DRAW-003-R1): l'indirizzo si scrive su un lato libero del
    pezzo, e se non ce n'e' uno si omette, senza richiamo e senza rilievo.
    Nessun obbligo di scriverli tutti.

    `floor_y_mm` e' accettato per la catena che ancora lo passa e non e' usato:
    la quota di terra non e' un ostacolo per i testi (D-121).
    """
    del floor_y_mm
    height = standard.text_small_mm
    step = standard.grid_mm
    canvas = _canvas(placed, routes, standard, area)
    for written in already or ():
        canvas.take(
            _text_box(written.anchor, text_width_mm(written.text, height), height),
            None if written.leader_from is None else (written.leader_from, written.anchor),
        )
    labels: list[PlacedLabel] = []
    for item in placed:
        text = addresses.get(item.component_id)
        if text is None:
            continue
        settled = _settle(
            item,
            f"address-{item.component_id}",
            text,
            "address",
            0,
            height_mm=height,
            step_mm=step,
            canvas=canvas,
        )
        if settled is not None:
            labels.append(settled)
    return labels


def place_labels(
    project: ProjectModel,
    placed: list[PlacedSymbol],
    standard: GraphicStandard,
    routes: list[RoutedTrunk] | None = None,
    floor_y_mm: float | None = None,
    *,
    area: Rect | None = None,
) -> list[PlacedLabel]:
    """Sigle e valori, scritti piccoli accanto al proprio componente (D-075).

    Sono i testi della tavola definitiva: la sigla sopra il riquadro, i valori
    sotto, e se quel lato e' occupato un altro lato adiacente, sempre senza
    richiamo (D1). Solo quando nessun lato e' libero la sigla prende un
    richiamo corto a 45 gradi che non attraversa niente (D2); se nemmeno
    quello esiste la sigla si omette, e niente di cio' che e' gia' disegnato si
    muove.

    `routes` porta le tubazioni gia' instradate: senza, un testo puo' cadere
    sopra una linea senza che nulla se ne accorga. Resta opzionale perche' i
    testi si posano anche quando le tratte non sono ancora instradate.
    `floor_y_mm` e' accettato per compatibilita' e non e' usato (D-121).

    Deterministico: l'ordine segue quello dei simboli posati, e a parita' di
    ingombro la ricerca percorre sempre gli stessi lati nello stesso ordine.
    """
    del floor_y_mm
    properties = {item.id: item.properties for item in project.components}
    height = standard.text_small_mm
    step = standard.grid_mm
    canvas = _canvas(placed, routes, standard, area)
    labels: list[PlacedLabel] = []
    for item in placed:
        slots = {"tag": 0, "data": 0}
        for label_id, text, role in _texts_of(item, properties):
            settled = _settle(
                item,
                label_id,
                text,
                role,
                slots[role],
                height_mm=height,
                step_mm=step,
                canvas=canvas,
            )
            slots[role] += 1
            if settled is not None:
                labels.append(settled)
    return labels
