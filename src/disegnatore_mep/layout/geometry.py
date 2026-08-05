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


def _covers(box: tuple[float, float, float, float], before: Point, after: Point) -> bool:
    """Vero se il riquadro contiene per intero il tratto: la linea gli passa sotto."""
    left, top, right, bottom = box
    return (
        left < min(before.x_mm, after.x_mm) + TOLERANCE_MM
        and max(before.x_mm, after.x_mm) < right + TOLERANCE_MM
        and top < min(before.y_mm, after.y_mm) + TOLERANCE_MM
        and max(before.y_mm, after.y_mm) < bottom + TOLERANCE_MM
    )


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
    - **D-027**: un tratto sta dentro il riquadro per intero, e allora la linea
      passa **sotto** il simbolo invece di essere interrotta da lui. Questo si
      misura sempre, esenzione o no: una linea che corre lungo il bordo del
      riquadro ha i capi sul riquadro e sembrerebbe un attacco, mentre e'
      esattamente il difetto peggiore.
    """
    for route in routes:
        for segment in route.segments:
            moves = moves_of(segment)
            if any(_covers(box, before, after) for before, after in moves):
                return True
            if attaches_to(segment, box):
                continue
            if any(
                distance_to_box(before, after, box) < clearance_mm - TOLERANCE_MM
                for before, after in moves
            ):
                return True
    return False


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
