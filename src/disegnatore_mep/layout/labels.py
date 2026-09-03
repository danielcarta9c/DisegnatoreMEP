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

**I testi sono l'ultima fase del disegno** (DRAW-003, I-025). Componenti e
rotte sono definitivi quando questo modulo entra in gioco, e niente di cio' che
decide qui puo' toccarli: un testo si posa, non sposta. La regola di posa e'
netta, ed e' quella del PM:

- ogni testo ha **una** posizione preferita accanto al proprio pezzo — la sigla
  sopra, i valori sotto, l'indirizzo di fianco;
- se e' libera, il testo resta li' senza richiamo;
- se collide con un tubo, un simbolo, un'altra etichetta o il margine
  dell'area di disegno, **non si muove nulla di cio' che e' gia' disegnato**:
  si cerca deterministicamente un posto libero per il solo testo e lo si lega
  al pezzo con un richiamo rettilineo obliquo. Niente peregrinazioni fra lati e
  distanze senza dichiarare graficamente il legame;
- il richiamo e' a 45 gradi, parte da uno spigolo del proprio pezzo, non passa
  sopra simboli o testi, e non attraversa tubazioni ne' altri richiami finche'
  esiste una diagonale libera equivalente.

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

LEADER_MAX_STEPS = 40
"""Quante volte la diagonale si allunga di un passo cercando spazio libero.

Quaranta passi sono cento millimetri di diagonale: oltre, il richiamo non
identifica piu' niente. Prima erano ventiquattro, e bastavano quando il
richiamo poteva attraversare le tubazioni; ora che le evita gli serve piu'
corsa, e la corsa la paga solo chi non trova posto prima.
"""

CHAR_WIDTH_RATIO = 0.6
"""Larghezza media di un carattere rispetto al corpo, per un sans-serif.

Stima: la tavola non incorpora metriche di font. Serve a capire se due testi si
sovrappongono, quindi un errore in eccesso e' innocuo.
"""

TOLERANCE_MM = 1e-6

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


def preferred_anchor(
    item: PlacedSymbol,
    role: str,
    slot: int,
    width_mm: float,
    *,
    height_mm: float,
    step_mm: float,
) -> Point:
    """La posizione preferita di un testo, secondo il suo ruolo.

    La sigla sta **sopra** il riquadro, i valori **sotto** — uno per riga, nel
    loro ordine — e l'indirizzo di verifica **a destra**, in quota col centro
    del pezzo. Sopra e sotto il testo si centra sul riquadro restando su un
    nodo della griglia; lo stacco dal riquadro vale invece un millimetro e
    mezzo perche' e' quanto deve valere: portarlo sul passo lo raddoppierebbe
    allontanando ogni scritta dal proprio pezzo, che e' il difetto che D-075
    corregge.
    """
    centred = (
        item.origin.x_mm + round((item.width_mm - width_mm) / 2 / step_mm) * step_mm
    )
    stack = slot * (height_mm + CALLOUT_LINE_GAP_MM)
    if role == "tag":
        return Point(x_mm=centred, y_mm=item.origin.y_mm - TAG_GAP_MM - stack)
    if role == "data":
        return Point(
            x_mm=centred, y_mm=item.bottom_mm + VALUE_GAP_MM + height_mm + stack
        )
    middle = item.origin.y_mm + item.height_mm / 2 + height_mm / 2 + stack
    return Point(x_mm=item.right_mm + SIDE_GAP_MM, y_mm=middle)


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

    def leader_fits(self, start: Point, end: Point, box: Box, *, rigour: int) -> bool:
        """La diagonale, a tre gradi di rigore.

        Al grado 2 non passa sopra simboli o testi, non attraversa tubazioni ne'
        altri richiami, e non passa sotto il proprio testo: e' la ricerca che si
        fa per prima. Al grado 1 puo' attraversare tubazioni e altri richiami —
        obliqua com'e' non la si scambia per un tubo (B1) — ma non simboli ne'
        testi. Al grado 0 puo' passare anche sopra un simbolo o sotto il
        proprio testo: e' l'ultima risorsa di un pezzo murato fra due macchine,
        e il preflight lo segnala; un testo mancante sarebbe peggio.
        """
        if _crosses(start, end, box) and rigour > 0:
            return False
        if rigour > 0 and any(
            _crosses(start, end, other) for other in (*self.symbols, *self.texts)
        ):
            return False
        if rigour < 2:
            return True
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
) -> tuple[Point, Point]:
    """Il primo posto raggiungibile con una diagonale a 45 gradi.

    La diagonale parte da uno spigolo del simbolo e finisce **sulla base del
    testo**: un solo segmento obliquo, nessuna piega. La codina orizzontale
    sotto la scritta — la «scaletta» del disegno a mano — si potrebbe
    aggiungere, e deliberatamente non c'e': porterebbe i due capi del richiamo a
    un angolo diverso da 45 gradi, e i due capi sono cio' che la geometria
    dichiara e che il preflight misura. Un richiamo che *si disegna* a 45 gradi
    ma *si misura* a 60 non e' verificabile.

    Il posto si cerca allungando la diagonale di un passo per volta, quindi e'
    il piu' vicino fra i liberi. Tre giri, dal piu' rigoroso al meno: nel primo
    la diagonale non attraversa niente; nel secondo puo' attraversare tubazioni
    e altri richiami — un richiamo che incrocia un tubo resta leggibile, perche'
    obliquo com'e' non lo si scambia per un tubo (B1); nel terzo puo' passare
    anche sopra un simbolo, che e' il caso del pezzo murato fra due macchine. In
    ogni giro il testo sta dentro l'area e non copre niente. Un testo mancante
    sarebbe peggio di un richiamo brutto, e il preflight dice dove e' brutto.
    """
    reach = ceil(LEADER_MIN_LENGTH_MM / sqrt(2) / step_mm) * step_mm

    def reached(way: tuple[int, int], span: float) -> tuple[Point, Point]:
        start = _leader_corner(item, way)
        return start, Point(
            x_mm=start.x_mm + way[0] * span, y_mm=start.y_mm + way[1] * span
        )

    for rigour in (2, 1, 0):
        for ring in range(LEADER_MAX_STEPS):
            span = reach + ring * step_mm
            for way in DIAGONALS:
                start, anchor = reached(way, span)
                box = _text_box(anchor, width_mm, height_mm)
                if not canvas.free(box):
                    continue
                if not canvas.leader_fits(start, anchor, box, rigour=rigour):
                    continue
                return start, anchor
    # Nemmeno una diagonale libera: si scrive comunque, sulla prima. Un testo
    # mancante e' un difetto peggiore di un testo affollato, e il preflight lo
    # misura (D5).
    return reached(DIAGONALS[0], reach)


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
) -> PlacedLabel:
    """Un testo al proprio posto preferito se e' libero, altrimenti richiamato."""
    width = text_width_mm(text, height_mm)
    spot = preferred_anchor(item, role, slot, width, height_mm=height_mm, step_mm=step_mm)
    start: Point | None = None
    if not canvas.free(_text_box(spot, width, height_mm)):
        start, spot = _leader(
            item, width, height_mm=height_mm, step_mm=step_mm, canvas=canvas
        )
    canvas.take(_text_box(spot, width, height_mm), None if start is None else (start, spot))
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
    simbolo, la sigla dice *quale*, l'indirizzo dice **dove** — cosi' il
    progettista guarda il disegno, punta un pezzo, ne legge il codice e va a
    cercarlo sul grafo.

    Si posa **dopo tutto il resto e non sposta niente**: e' un velo sopra una
    tavola gia' finita, e le due modalita' — verifica e consegna — danno percio'
    la stessa identica tavola, una con le etichette in piu'. Segue lo stesso
    ordine delle altre scritte (DRAW-003): posto preferito di fianco al pezzo
    se libero, altrimenti richiamo obliquo, e non finisce sopra un tubo.

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
        labels.append(
            _settle(
                item,
                f"address-{item.component_id}",
                text,
                "address",
                0,
                height_mm=height,
                step_mm=step,
                canvas=canvas,
            )
        )
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

    La sigla va **sopra** il riquadro, i valori **sotto**, senza alcuna linea di
    richiamo: il testo sta vicino a cio' che nomina, e non serve seguire niente
    per capire di chi parla (D1). Quel posto e' l'unico che si prova: se e'
    occupato da un simbolo, da una tubazione, da un'altra etichetta o dal
    margine, il testo si sposta con il richiamo obliquo (D2), e niente di cio'
    che e' gia' disegnato si muove.

    `routes` porta le tubazioni gia' instradate: senza, un testo puo' cadere
    sopra una linea senza che nulla se ne accorga. Resta opzionale perche' i
    testi si posano anche quando le tratte non sono ancora instradate.
    `floor_y_mm` e' accettato per compatibilita' e non e' usato (D-121).

    Deterministico: l'ordine segue quello dei simboli posati, e a parita' di
    ingombro la ricerca percorre sempre le stesse posizioni nello stesso ordine.
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
            labels.append(
                _settle(
                    item,
                    label_id,
                    text,
                    role,
                    slots[role],
                    height_mm=height,
                    step_mm=step,
                    canvas=canvas,
                )
            )
            slots[role] += 1
    return labels
