"""Il modello geometrico derivato.

Il modello tecnico canonico resta la fonte di verita' e **non contiene
coordinate** (D-026, ADR 0002). Posizioni, spezzate, testi, legenda e rimandi
vivono qui, in un modello separato che si rigenera dal primo: correggere una
tavola significa correggere il modello tecnico o il piano di impaginazione,
mai queste coordinate.
"""

import hashlib
import json
import math

from pydantic import Field

from disegnatore_mep.model.base import FiniteFloat, StrictModel


class Point(StrictModel):
    x_mm: FiniteFloat
    y_mm: FiniteFloat


class PlacedSymbol(StrictModel):
    """Un simbolo posato: dove sta, come e' ruotato, quanto ingombra."""

    component_id: str
    symbol_id: str
    rotation_deg: int
    origin: Point
    width_mm: FiniteFloat = Field(gt=0)
    height_mm: FiniteFloat = Field(gt=0)
    tag: str | None = None

    @property
    def right_mm(self) -> float:
        return self.origin.x_mm + self.width_mm

    @property
    def bottom_mm(self) -> float:
        return self.origin.y_mm + self.height_mm


class RoutedTrunk(StrictModel):
    """Una tratta instradata: la spezzata ortogonale, con le sue interruzioni.

    `segments` e' l'elenco delle polilinee da disegnare: una sola quando la
    tratta non porta accessori in linea, piu' di una quando li porta, perche'
    ogni accessorio interrompe la linea invece di esservi sovrapposto (D-027).
    """

    network_id: str
    medium: str = ""
    """Il fluido, che decide colore e tratto: la rete da sola non basta."""
    supply: bool = True
    """Andata o ritorno. Su una tavola sono due linee distinte, non una."""
    connection_ids: list[str] = Field(default_factory=list)
    segments: list[list[Point]] = Field(default_factory=list)
    crossings: list[Point] = Field(default_factory=list)


class PlacedLabel(StrictModel):
    """Un testo sulla tavola: mai una denominazione, solo valore o sigla (D-052)."""

    id: str
    text: str
    role: str
    anchor: Point
    leader_from: Point | None = None
    """Da dove parte la linea di richiamo, quando il testo sta fuori dal corpo."""


class LegendEntry(StrictModel):
    symbol_id: str
    name: str
    anchor: Point


class NetworkKey(StrictModel):
    """Voce della sezione fluidi della legenda: colore e tratto di un fluido.

    Una per **fluido**, non per rete: primario e secondario portano la stessa
    acqua di riscaldamento e si disegnano uguali.
    """

    medium: str
    name: str
    colour: str
    dash: str
    anchor: Point


class CrossReference(StrictModel):
    id: str
    pair_id: str
    peer_sheet_id: str
    text: str
    anchor: Point


class SheetGeometry(StrictModel):
    sheet_id: str
    title: str
    symbols: list[PlacedSymbol] = Field(default_factory=list)
    routes: list[RoutedTrunk] = Field(default_factory=list)
    labels: list[PlacedLabel] = Field(default_factory=list)
    legend: list[LegendEntry] = Field(default_factory=list)
    network_keys: list[NetworkKey] = Field(default_factory=list)
    cross_references: list[CrossReference] = Field(default_factory=list)
    ground_line_y_mm: FiniteFloat | None = None
    """Quota della linea di terra: le macchine ci appoggiano sopra."""


class DrawingGeometry(StrictModel):
    project_id: str
    sheets: list[SheetGeometry] = Field(default_factory=list)


TOLERANCE_MM = 1e-6
"""Tolleranza delle misure sulla spezzata: la stessa del validatore."""


def _sign(value: float) -> int:
    if value > TOLERANCE_MM:
        return 1
    if value < -TOLERANCE_MM:
        return -1
    return 0


def moves_of(polyline: list[Point]) -> list[tuple[Point, Point]]:
    """I soli tratti che percorrono una distanza: un punto ripetuto non e' un tratto."""
    return [
        (before, after)
        for before, after in zip(polyline, polyline[1:], strict=False)
        if abs(after.x_mm - before.x_mm) > TOLERANCE_MM
        or abs(after.y_mm - before.y_mm) > TOLERANCE_MM
    ]


def _one_way_overshoot_mm(polyline: list[Point], step_mm: float) -> float:
    """Di quanto la spezzata, letta da un capo, supera l'altro e ci torna.

    L'ultimo tratto dice su quale asse si arriva — orizzontale o verticale — e i
    due capi dicono da che parte: la spezzata viaggia dal primo punto all'ultimo,
    e su quell'asse non deve mai andare oltre l'arrivo. Se i due capi hanno la
    stessa coordinata sull'asse di arrivo non c'e' un verso di viaggio da
    superare, e la misura e' zero: quello e' un aggiramento, non un'andata e
    ritorno.

    **Un passo non e' un giro.** Una porta si imbocca solo dal lato verso cui
    guarda, quindi quando guarda dalla parte opposta al verso di marcia della
    tratta l'ultimo tratto cade per forza oltre la porta, e il minimo che
    l'instradatore possa lasciare e' **un passo di griglia**: quello e'
    l'imbocco, non un superamento. Contarlo faceva segnalare come bloccante una
    figura che nessuna disposizione puo' evitare — una ricerca esaustiva sulle
    pose raggiungibili dei due terminali di zona del caso completo non ne trova
    nemmeno una che la eviti. Si concede quel passo e nulla di piu': chi gira
    due passi oltre la porta ha davvero allungato la linea per tornare indietro,
    e resta un rilievo.
    """
    moves = moves_of(polyline)
    if not moves:
        return 0.0
    source, goal = polyline[0], polyline[-1]
    before, after = moves[-1]
    if abs(after.y_mm - before.y_mm) <= TOLERANCE_MM:
        direction = _sign(goal.x_mm - source.x_mm)
        beyond = [(point.x_mm - goal.x_mm) * direction for point in polyline]
        approach = (before.x_mm - goal.x_mm) * direction
    else:
        direction = _sign(goal.y_mm - source.y_mm)
        beyond = [(point.y_mm - goal.y_mm) * direction for point in polyline]
        approach = (before.y_mm - goal.y_mm) * direction
    # Quando la porta guarda nel verso di marcia l'ultimo tratto arriva da
    # dietro, `approach` e' negativo e non si concede niente: la misura resta
    # quella di prima, tolleranza zero dalla porta.
    return max(beyond) - min(max(approach, 0.0), step_mm)


def overshoot_mm(polyline: list[Point], step_mm: float) -> float:
    """B12, D-078 — di quanto la spezzata supera una propria porta e ci torna.

    E' **la** misura dell'andata e ritorno, e vive qui perche' due moduli la
    devono leggere identica: il preflight di qualita', che blocca la tavola
    quando e' positiva, e il ciclo di miglioramento, che sceglie le mosse per
    annullarla. Finche' stavano su due formule diverse il ciclo poteva credere
    di aver chiuso un giro che il preflight vedeva ancora.

    Vale su **entrambi** i capi, perche' il verso in cui una spezzata e' scritta
    e' una convenzione dell'instradatore e il difetto non lo e'. Il passo di
    griglia serve a riconoscere l'imbocco obbligato di una porta, che non e' un
    superamento.
    """
    return max(
        _one_way_overshoot_mm(polyline, step_mm),
        _one_way_overshoot_mm(list(reversed(polyline)), step_mm),
    )


def distance_to_box(
    before: Point, after: Point, box: tuple[float, float, float, float]
) -> float:
    """Distanza fra un tratto ortogonale e un riquadro, zero se lo tocca."""
    left, top, right, bottom = box
    x_low, x_high = min(before.x_mm, after.x_mm), max(before.x_mm, after.x_mm)
    y_low, y_high = min(before.y_mm, after.y_mm), max(before.y_mm, after.y_mm)
    gap_x = max(left - x_high, x_low - right, 0.0)
    gap_y = max(top - y_high, y_low - bottom, 0.0)
    return math.hypot(gap_x, gap_y)


def attaches_to(polyline: list[Point], box: tuple[float, float, float, float]) -> bool:
    """Vero se un capo della spezzata cade sul riquadro: la tratta ci si attacca.

    La geometria non porta il legame fra tratta e componente — porta gli
    identificativi delle connessioni, che sono un altro spazio di nomi — quindi
    l'attacco si riconosce dove si vede: un capo di spezzata sul bordo o dentro
    il riquadro e' una porta.
    """
    left, top, right, bottom = box
    return any(
        left - TOLERANCE_MM <= point.x_mm <= right + TOLERANCE_MM
        and top - TOLERANCE_MM <= point.y_mm <= bottom + TOLERANCE_MM
        for point in (polyline[0], polyline[-1])
    )


def box_of(symbol: PlacedSymbol) -> tuple[float, float, float, float]:
    return (symbol.origin.x_mm, symbol.origin.y_mm, symbol.right_mm, symbol.bottom_mm)


def lies_inside(
    box: tuple[float, float, float, float], before: Point, after: Point
) -> bool:
    """Vero se il riquadro **contiene** il tratto, bordi compresi.

    E' la misura storica di D-027, tenuta parola per parola. Prende due cose
    che l'attraversamento non prende, e la seconda vale la pena dirla: il
    tratto tutto dentro il corpo, e il tratto che corre **a filo del bordo**
    per la lunghezza del riquadro. Il secondo caso non entra nel corpo — sulla
    carta la linea passa esattamente sul fianco del simbolo — ma si legge come
    se ci passasse sopra, e la freccia del flusso ci finisce dentro. E' il
    difetto che il commento di questa misura chiamava «esattamente il difetto
    peggiore», ed e' una convenzione di rappresentazione: **restringerla non e'
    del disegnatore** (D-124).
    """
    left, top, right, bottom = box
    return (
        left < min(before.x_mm, after.x_mm) + TOLERANCE_MM
        and max(before.x_mm, after.x_mm) < right + TOLERANCE_MM
        and top < min(before.y_mm, after.y_mm) + TOLERANCE_MM
        and max(before.y_mm, after.y_mm) < bottom + TOLERANCE_MM
    )


def enters_body(
    box: tuple[float, float, float, float], before: Point, after: Point
) -> bool:
    """Vero se il tratto entra nel **corpo pieno** del riquadro (D-027).

    Entrare vuol dire percorrere una lunghezza maggiore di zero dentro il
    riquadro **aperto**, cioe' bordi esclusi. Ne discendono le due cose che
    servono, senza bisogno di sapere quali tratte tocchino quale componente:

    - il tratto che **termina su un attacco** non entra. Una porta sta sul
      perimetro del simbolo e l'instradamento ci arriva da fuori: il tratto
      tocca il bordo e si ferma li', quindi la sua lunghezza dentro il corpo
      e' nulla. Vale anche per chi costeggia il fianco a filo;
    - il tratto che **attraversa** il simbolo entra, e non importa se ne esce
      dall'altra parte.

    ⛔ **Da sola questa misura non basta, e non sostituisce quella storica.**
    Prima si guardava il **contenimento** (`lies_inside`), che vedeva soltanto il
    caso estremo: un tratto che entrava da un lato e usciva dall'altro — o che
    sporgeva di un millimetro oltre il bordo — passava per buono, ed era una
    linea disegnata **sotto** un simbolo invece che interrotta da lui. E' il
    difetto che la regola di vicinanza del PM (D-120) ha fatto affiorare
    avvicinando le valvole agli attacchi: e' bastato che l'accessorio si sedesse
    dove un'altra tratta si attacca alla stessa macchina.

    Le due misure prendono cose diverse e si usano **insieme**
    (`intrudes_into`): questa vede chi attraversa, quella vede chi corre a filo
    del fianco. Sostituire la seconda con la prima avrebbe **allentato** un
    controllo di rappresentazione, che non e' del disegnatore.
    """
    left, top, right, bottom = box
    x_low, x_high = min(before.x_mm, after.x_mm), max(before.x_mm, after.x_mm)
    y_low, y_high = min(before.y_mm, after.y_mm), max(before.y_mm, after.y_mm)
    inside_x = min(x_high, right) - max(x_low, left)
    inside_y = min(y_high, bottom) - max(y_low, top)
    if inside_x < -TOLERANCE_MM or inside_y < -TOLERANCE_MM:
        return False
    # Un tratto ortogonale ha spessore nullo su un asse: li' basta che cada
    # **dentro** il riquadro, bordi esclusi, e sull'altro che percorra una
    # lunghezza vera.
    if abs(y_high - y_low) <= TOLERANCE_MM:
        return top + TOLERANCE_MM < y_low < bottom - TOLERANCE_MM and (
            inside_x > TOLERANCE_MM
        )
    if abs(x_high - x_low) <= TOLERANCE_MM:
        return left + TOLERANCE_MM < x_low < right - TOLERANCE_MM and (
            inside_y > TOLERANCE_MM
        )
    return inside_x > TOLERANCE_MM and inside_y > TOLERANCE_MM


def intrudes_into(
    box: tuple[float, float, float, float], before: Point, after: Point
) -> bool:
    """La misura completa di D-027: chi attraversa il corpo o chi ci corre dentro.

    E' l'unione delle due, e sta in un posto solo perche' i due consumatori — il
    cancello di correttezza e chi posa gli accessori — devono dare la stessa
    risposta: chi posa chiede «questa posizione la consegno o no?», e se le due
    misure divergono si approva una tavola e se ne disegna un'altra.
    """
    return enters_body(box, before, after) or lies_inside(box, before, after)


def run_intrudes_on(
    box: tuple[float, float, float, float],
    routes: list[RoutedTrunk],
    clearance_mm: float,
) -> bool:
    """Vero se una di queste tratte, contro questo riquadro, e' un rilievo bloccante.

    E' l'unione esatta di cio' che i due validatori bloccano, e non un
    millimetro di piu': chi posa un simbolo deve poter chiedere «questa
    posizione la consegno o no?» e ricevere la stessa risposta che daranno loro.

    - **B5**: un tratto passa a meno della distanza di rispetto dal riquadro.
      Le spezzate che finiscono dentro il riquadro non si misurano: e' il modo
      in cui il preflight riconosce un attacco, e vale anche qui.
    - **D-027**: un tratto entra nel corpo del riquadro **o gli corre dentro a
      filo del bordo**, e allora la linea passa **sotto** il simbolo invece di
      essere interrotta da lui. Questo si misura sempre, esenzione o no: una
      spezzata che si attacca al simbolo e' esente dalla distanza di rispetto —
      e' cosi' che si riconosce un attacco — ma non dall'attraversarlo.
    """
    for route in routes:
        for segment in route.segments:
            moves = moves_of(segment)
            if any(intrudes_into(box, before, after) for before, after in moves):
                return True
            if attaches_to(segment, box):
                continue
            if any(
                distance_to_box(before, after, box) < clearance_mm - TOLERANCE_MM
                for before, after in moves
            ):
                return True
    return False


SHEET_FILL_MIN_RATIO = 0.60
"""Quota dell'area di disegno che l'ingombro dell'inchiostro deve coprire (A1).

**Taratura**, non norma: la carta dice «il foglio e' pieno in modo uniforme» e
non da' un numero. Sotto tre quinti dell'area il disegno e' una fascia o un
angolo, non una tavola.

Vive accanto alla misura, e non fra i controlli, perche' da D-111 la leggono in
due: il **preflight**, che avvisa a tavola finita, e il **collocatore**, che la
insegue mentre dispone. Un numero solo, in un posto solo.
"""

QUADRANT_IMBALANCE_MAX = 3.0
"""Rapporto massimo fra il quadrante piu' pieno e il piu' vuoto (A1, A3).

**Taratura.** «Si copre meta' foglio con una mano: se una meta' e' quasi bianca
e l'altra e' fitta, non va», e «i quattro margini bianchi si somigliano». Tre
volte e' lo squilibrio oltre il quale la differenza si vede da due metri.
"""


def ink_box(
    symbols: list[PlacedSymbol], routes: list[RoutedTrunk]
) -> tuple[float, float, float, float] | None:
    """L'ingombro di cio' che e' disegnato: simboli e tubazioni.

    Legenda e fluidi vivono nella propria fascia, fuori dall'area di disegno per
    costruzione, e non entrano nel conto: il riempimento che la carta chiede e'
    quello del disegno, non quello del foglio.
    """
    xs: list[float] = []
    ys: list[float] = []
    for symbol in symbols:
        xs += [symbol.origin.x_mm, symbol.right_mm]
        ys += [symbol.origin.y_mm, symbol.bottom_mm]
    for route in routes:
        for segment in route.segments:
            xs += [point.x_mm for point in segment]
            ys += [point.y_mm for point in segment]
    if not xs or not ys:
        return None
    return (min(xs), min(ys), max(xs), max(ys))


def fill_ratio(
    symbols: list[PlacedSymbol],
    routes: list[RoutedTrunk],
    area: tuple[float, float, float, float],
) -> float:
    """Quanta parte dell'area di disegno copre l'ingombro dell'inchiostro (A1).

    Vive qui, e non fra i controlli, perche' due moduli la devono leggere
    identica: il **preflight**, che avvisa quando la tavola e' una fascia, e il
    **collocatore**, che da D-111 la usa come obiettivo mentre dispone invece di
    scoprirla alla fine. Finche' stavano su due formule diverse il collocatore
    poteva credere di aver riempito un foglio che il preflight vedeva vuoto.
    """
    box = ink_box(symbols, routes)
    if box is None:
        return 0.0
    width = max(box[2] - box[0], TOLERANCE_MM)
    height = max(box[3] - box[1], TOLERANCE_MM)
    span_x = max(area[2] - area[0], TOLERANCE_MM)
    span_y = max(area[3] - area[1], TOLERANCE_MM)
    return (width * height) / (span_x * span_y)


def quadrants_of(
    area: tuple[float, float, float, float],
) -> list[tuple[float, float, float, float]]:
    """I quattro quadranti di un rettangolo, in ordine di lettura."""
    half_width = (area[2] - area[0]) / 2.0
    half_height = (area[3] - area[1]) / 2.0
    return [
        (x_mm, y_mm, x_mm + half_width, y_mm + half_height)
        for y_mm in (area[1], area[1] + half_height)
        for x_mm in (area[0], area[0] + half_width)
    ]


def _clipped_length_mm(
    before: Point, after: Point, area: tuple[float, float, float, float]
) -> float:
    """Quanto di un tratto ortogonale cade dentro un rettangolo."""
    if abs(before.y_mm - after.y_mm) <= TOLERANCE_MM:
        if not area[1] - TOLERANCE_MM <= before.y_mm <= area[3] + TOLERANCE_MM:
            return 0.0
        low, high = min(before.x_mm, after.x_mm), max(before.x_mm, after.x_mm)
        return max(min(high, area[2]) - max(low, area[0]), 0.0)
    if abs(before.x_mm - after.x_mm) <= TOLERANCE_MM:
        if not area[0] - TOLERANCE_MM <= before.x_mm <= area[2] + TOLERANCE_MM:
            return 0.0
        low, high = min(before.y_mm, after.y_mm), max(before.y_mm, after.y_mm)
        return max(min(high, area[3]) - max(low, area[1]), 0.0)
    return 0.0


def ink_area_mm2(
    symbols: list[PlacedSymbol],
    routes: list[RoutedTrunk],
    area: tuple[float, float, float, float],
    line_mm: float,
) -> float:
    """L'inchiostro dentro un rettangolo: riquadri dei simboli piu' tratto delle linee."""
    total = 0.0
    for symbol in symbols:
        left, top, right, bottom = box_of(symbol)
        width = max(min(right, area[2]) - max(left, area[0]), 0.0)
        height = max(min(bottom, area[3]) - max(top, area[1]), 0.0)
        total += width * height
    for route in routes:
        for segment in route.segments:
            for before, after in moves_of(segment):
                total += _clipped_length_mm(before, after, area) * line_mm
    return total


def ink_imbalance(
    symbols: list[PlacedSymbol],
    routes: list[RoutedTrunk],
    area: tuple[float, float, float, float],
    line_mm: float,
) -> float:
    """Quanto il quadrante piu' pieno pesa piu' del piu' vuoto (A1, A3).

    Un quadrante senza inchiostro vale infinito: e' il caso del disegno tutto
    su un lato, che non e' uno squilibrio grande ma un difetto di specie diversa.
    """
    areas = [
        ink_area_mm2(symbols, routes, quadrant, line_mm)
        for quadrant in quadrants_of(area)
    ]
    if max(areas) <= TOLERANCE_MM:
        return 1.0
    if min(areas) <= TOLERANCE_MM:
        return math.inf
    return max(areas) / min(areas)


def drawing_fingerprint(drawing: DrawingGeometry) -> str:
    """Impronta riproducibile della geometria.

    Stesso modello e stesso piano di impaginazione devono dare la stessa
    tavola: questa e' la misura che lo dimostra, come `project_fingerprint`
    fa per il modello tecnico.
    """
    payload = json.dumps(
        drawing.model_dump(mode="json"),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
