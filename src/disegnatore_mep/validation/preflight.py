"""Il preflight di qualita': non «questa tavola sta in piedi?» ma «e' disegnata bene?».

`geometry.py` misura la **correttezza** — simboli sovrapposti, testi addosso ai
pezzi, segmenti obliqui, oggetti fuori area, rimandi spaiati — e blocca. Questo
modulo misura la **qualita'**: le righe che `docs/QUALITA_GRAFICA.md` marca «da
misurare», cioe' il livello 1 della verifica a tre livelli di D-063, il
preflight deterministico che gira dentro la pipeline e non nei test.

Ogni misura e' una funzione pura che riceve la geometria e restituisce
`ValidationIssue`, lo stesso tipo e la stessa scala di severita' del validatore
di correttezza: un difetto e' un difetto, e chi legge il rapporto non deve
imparare due lessici. `preflight_drawing` le esegue nell'ordine dichiarato da
`MEASURE_ORDER`, e l'ordine dell'esito e' quello.

Le soglie sono costanti nominate con la propria fonte accanto. Dove la fonte e'
una regola scritta — la carta del colpo d'occhio, una decisione del registro —
il commento la cita; dove il numero e' una **taratura**, il commento lo dichiara
tale, perche' un valore tarato si rivede sulle tavole reali e un valore normato
no (D-083: vietato inventare, e vietato far passare una taratura per una norma).
"""

import math

from disegnatore_mep.catalog.errors import CatalogError
from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import Rect, SheetFrame
from disegnatore_mep.layout.geometry import (
    QUADRANT_IMBALANCE_MAX,
    SHEET_FILL_MIN_RATIO,
    DrawingGeometry,
    PlacedLabel,
    Point,
    RoutedTrunk,
    SheetGeometry,
    attaches_to,
    box_of,
    distance_to_box,
    fill_ratio,
    ink_area_mm2,
    moves_of,
    overshoot_mm,
    quadrants_of,
)
from disegnatore_mep.layout.labels import (
    LINE_CLEARANCE_MM,
    segments_cross,
    text_width_mm,
)
from disegnatore_mep.model.types import IssueSeverity

from .geometry import TOLERANCE_MM
from .issues import ValidationIssue

BENDS_PER_RUN_MAX = 3
"""Cambi di direzione ammessi su una tratta prima dell'avviso (B4, D-060).

Il numero viene dalla geometria, non da una taratura: per unire due porte su
una griglia ortogonale servono zero pieghe se sono allineate, una per una elle,
due per uno scarto, tre per la graffa fra due porte sulla stessa faccia. Oltre
la terza la piega non la chiede il collegamento: la chiede un ostacolo, cioe'
una posizione da correggere (D-078).
"""

CROSSINGS_MAX = 5
"""Nodi condivisi fra tratte diverse ammessi su una tavola (B3).

«Su una centrale semplice devono stare sulle dita di una mano»: cinque. La
misura e' quella della prova permanente `tests/layout/test_objective.py` — i
nodi di griglia toccati da due tratte diverse.
"""

SHARED_EDGES_MAX = 0
"""Spigoli di griglia percorsi da due tratte diverse: divieto, non costo (D-062).

«Vietato sovrapporre longitudinalmente le linee, sempre separate e ben
distinte.» Due linee sullo stesso tratto sono una linea sola: non e' una
penalita' da pagare, e' un esito bloccante.
"""

SHARED_EDGES_AT_A_SHARED_PORT = 1
"""L'unica eccezione che D-062 dichiara, trascritta alla lettera.

«Unica eccezione: l'ultimo tratto contro una porta condivisa da due tratte, che
sulla tavola e' una derivazione ed e' lungo un passo di griglia.» Vale solo se
lo spigolo condiviso e' uno e tocca una porta che e' capo di **entrambe** le
tratte: fuori da questa condizione la sovrapposizione resta bloccante.
"""

U_TURN_OVERSHOOT_MAX_MM = 0.0
"""Quanto una tratta puo' superare la propria porta di arrivo: niente (B12, D-078).

«La linea supera l'oggetto, scende e torna indietro a prenderlo. Va spostato
l'oggetto, non allungata la linea.» Tolleranza zero per costruzione.
"""

# Le due tarature del riempimento vivono accanto alla misura, in
# `layout.geometry`, perche' da D-111 le legge anche il collocatore: qui si
# guarda la tavola finita, li' si dispone per ottenerla, e il numero deve
# essere lo stesso. Il valore si rivede sulle tavole reali (carta, §«Come
# cresce questa carta», terza sorgente); l'esito resta un avviso proprio per
# questo.

NEXT_SHEET_FILL_MIN_RATIO = 0.40
"""Riempimento minimo di una tavola successiva alla prima (D-072, A2).

**Taratura**, ed e' il «riempimento minimo dichiarato» che D-072 chiede senza
fissarlo: «non ha senso separare in due fogli con il secondo completamente
vuoto». Sotto questa quota la seconda tavola sembra un ritaglio e doveva stare
sulla prima: esito bloccante, perche' D-072 e' un divieto di divisione, non un
consiglio.
"""

LEADER_ANGLE_DEG = 45
"""L'unica giacitura ammessa per un richiamo di etichetta (D-075, D2).

«Quando il testo non ci sta o interferisce, e solo allora, si allontana con un
richiamo **in diagonale a 45 gradi**.» Non e' una taratura: e' l'angolo che
nessuna tubazione puo' avere, ed e' per questo che e' stato scelto.
"""

INVENTED_SOURCE = "CONV-GRAFICA-001"
"""La convenzione grafica interna: una fonte inventata, non una fonte (D-081, D-083).

Un simbolo che la cita non ha una fonte vera: nessuna tavola normata, nessuno
schema di produttore, nessuna decisione del PM. E' esattamente il difetto che
WP1 ha chiuso, e questa misura impedisce che rientri.
"""

GRID_ROUNDING_DIGITS = 3
"""Cifre decimali con cui si arrotondano i nodi di griglia prima di confrontarli.

Serve a far coincidere due percorsi calcolati per strade diverse: senza, due
tratte sullo stesso spigolo non risultano sullo stesso spigolo per un errore in
fondo alla mantissa.
"""

QUADRANT_NAMES: tuple[str, ...] = (
    "in alto a sinistra",
    "in alto a destra",
    "in basso a sinistra",
    "in basso a destra",
)
"""I quattro quadranti dell'area di disegno, in ordine di lettura."""

MEASURE_ORDER: tuple[str, ...] = (
    "bends_per_run",
    "crossings",
    "longitudinal_overlap",
    "clearances",
    "u_turns",
    "orthogonality_of_leaders",
    "labels_on_runs",
    "leader_crossings",
    "omitted_tags",
    "sheet_fill",
    "next_sheet_fill",
    "symbol_sources",
)
"""L'ordine in cui `preflight_drawing` esegue le misure, e quindi l'ordine
dell'esito: prima le linee, poi i testi, poi il foglio, infine le fonti.
Dichiararlo qui rende l'ordine una scelta leggibile invece di un effetto della
sequenza delle chiamate.
"""


def _finding(
    code: str, severity: IssueSeverity, message: str, entity_ids: list[str]
) -> ValidationIssue:
    return ValidationIssue(
        code=code, severity=severity, message=message, entity_ids=entity_ids
    )


def _stretches(polyline: list[Point]) -> list[tuple[Point, Point]]:
    """Le coppie di punti consecutivi, degeneri comprese."""
    return list(zip(polyline, polyline[1:], strict=False))


def _sign(value: float) -> int:
    if value > TOLERANCE_MM:
        return 1
    if value < -TOLERANCE_MM:
        return -1
    return 0


def _bends(polyline: list[Point]) -> int:
    """Quante volte la spezzata cambia direzione."""
    steps = [
        (_sign(after.x_mm - before.x_mm), _sign(after.y_mm - before.y_mm))
        for before, after in moves_of(polyline)
    ]
    return sum(1 for before, after in zip(steps, steps[1:], strict=False) if before != after)


def _walk(before: Point, after: Point, ratio: float) -> tuple[float, float]:
    return (
        round(before.x_mm + (after.x_mm - before.x_mm) * ratio, GRID_ROUNDING_DIGITS),
        round(before.y_mm + (after.y_mm - before.y_mm) * ratio, GRID_ROUNDING_DIGITS),
    )


def _steps(before: Point, after: Point, grid_mm: float) -> int:
    span = abs(after.x_mm - before.x_mm) + abs(after.y_mm - before.y_mm)
    return int(round(span / grid_mm))


def _cells(polyline: list[Point], grid_mm: float) -> set[tuple[float, float]]:
    """I nodi di griglia toccati dalla spezzata."""
    walked: set[tuple[float, float]] = set()
    for before, after in _stretches(polyline):
        steps = _steps(before, after, grid_mm)
        for index in range(steps + 1):
            walked.add(_walk(before, after, index / steps if steps else 0.0))
    return walked


def _edges(
    polyline: list[Point], grid_mm: float
) -> set[tuple[tuple[float, float], tuple[float, float]]]:
    """Gli spigoli di griglia **percorsi**, non i nodi toccati.

    E' la distinzione fra un incrocio e una sovrapposizione: due tratte che si
    tagliano condividono un nodo, due tratte che corrono insieme condividono
    degli spigoli.
    """
    walked: set[tuple[tuple[float, float], tuple[float, float]]] = set()
    for before, after in _stretches(polyline):
        steps = _steps(before, after, grid_mm)
        for index in range(steps):
            first = _walk(before, after, index / steps)
            second = _walk(before, after, (index + 1) / steps)
            walked.add((first, second) if first <= second else (second, first))
    return walked


def _run_polylines(sheet: SheetGeometry) -> list[tuple[int, RoutedTrunk, list[Point]]]:
    """Ogni spezzata con la tratta cui appartiene, in ordine di dichiarazione."""
    return [
        (index, route, segment)
        for index, route in enumerate(sheet.routes)
        for segment in route.segments
    ]


def _run_name(route: RoutedTrunk) -> str:
    return ", ".join(route.connection_ids) if route.connection_ids else route.network_id


def _run_ids(sheet: SheetGeometry, route: RoutedTrunk) -> list[str]:
    return [sheet.sheet_id, *route.connection_ids]


def _clearance_severity(distance_mm: float, minimum_mm: float) -> IssueSeverity | None:
    """Sotto la distanza minima si blocca, esattamente sulla soglia si avvisa."""
    if distance_mm < minimum_mm - TOLERANCE_MM:
        return IssueSeverity.BLOCKING
    if distance_mm <= minimum_mm + TOLERANCE_MM:
        return IssueSeverity.WARNING
    return None


def _parallel_distance(
    first: tuple[Point, Point], second: tuple[Point, Point]
) -> float | None:
    """Distanza fra due tratti paralleli che corrono affiancati, altrimenti niente.

    Due tratti sono affiancati se hanno la stessa giacitura e le loro proiezioni
    sull'asse comune si sovrappongono per un tratto vero: due tubi allineati che
    si toccano in un punto non corrono affiancati, si incontrano.
    """
    horizontal = (
        abs(first[0].y_mm - first[1].y_mm) <= TOLERANCE_MM
        and abs(second[0].y_mm - second[1].y_mm) <= TOLERANCE_MM
    )
    vertical = (
        abs(first[0].x_mm - first[1].x_mm) <= TOLERANCE_MM
        and abs(second[0].x_mm - second[1].x_mm) <= TOLERANCE_MM
    )
    if horizontal:
        along = (first[0].x_mm, first[1].x_mm, second[0].x_mm, second[1].x_mm)
        across = abs(first[0].y_mm - second[0].y_mm)
    elif vertical:
        along = (first[0].y_mm, first[1].y_mm, second[0].y_mm, second[1].y_mm)
        across = abs(first[0].x_mm - second[0].x_mm)
    else:
        return None
    shared = min(max(along[0], along[1]), max(along[2], along[3])) - max(
        min(along[0], along[1]), min(along[2], along[3])
    )
    if shared <= TOLERANCE_MM:
        return None
    return across


def _rect(area: Rect) -> tuple[float, float, float, float]:
    """Il rettangolo come quaterna, che e' la forma che le misure condivise usano."""
    return (area.x_mm, area.y_mm, area.right_mm, area.bottom_mm)


def _fill_ratio(sheet: SheetGeometry, area: Rect) -> float:
    """Il riempimento della tavola, con la formula condivisa col collocatore.

    La misura vive in `layout.geometry` perche' da D-111 il collocatore la usa
    come **obiettivo** mentre dispone, e non basta che le due somiglino: devono
    essere la stessa (e' la lezione dell'andata e ritorno, misurata due volte
    con due formule diverse).
    """
    return fill_ratio(sheet.symbols, sheet.routes, _rect(area))


def _quadrants(area: Rect) -> list[Rect]:
    return [
        Rect(x_mm=item[0], y_mm=item[1], width_mm=item[2] - item[0], height_mm=item[3] - item[1])
        for item in quadrants_of(_rect(area))
    ]


def _ink_area_mm2(sheet: SheetGeometry, area: Rect, line_mm: float) -> float:
    return ink_area_mm2(sheet.symbols, sheet.routes, _rect(area), line_mm)


def bends_per_run(drawing: DrawingGeometry) -> list[ValidationIssue]:
    """B4 — una linea cambia direzione solo per una ragione.

    Si conta per **tratta**, non per spezzata: una tratta interrotta dai propri
    accessori in linea resta una tratta sola, e le sue pieghe si sommano.
    """
    findings: list[ValidationIssue] = []
    for sheet in drawing.sheets:
        for route in sheet.routes:
            total = sum(_bends(segment) for segment in route.segments)
            if total <= BENDS_PER_RUN_MAX:
                continue
            findings.append(
                _finding(
                    "RUN_WITH_TOO_MANY_BENDS",
                    IssueSeverity.WARNING,
                    f"la tratta {_run_name(route)} cambia direzione {total} volte, "
                    f"oltre le {BENDS_PER_RUN_MAX} pieghe che bastano a unire due "
                    f"porte: la piega in piu' la chiede un ostacolo, e l'ostacolo si "
                    f"sposta (B4, D-078)",
                    _run_ids(sheet, route),
                )
            )
    return findings


def crossings(drawing: DrawingGeometry, frame: SheetFrame) -> list[ValidationIssue]:
    """B3 — gli incroci sono pochi: si contano i nodi condivisi da tratte diverse."""
    findings: list[ValidationIssue] = []
    for sheet in drawing.sheets:
        walked = [
            (index, _cells(segment, frame.standard.grid_mm))
            for index, _, segment in _run_polylines(sheet)
        ]
        total = sum(
            len(walked[first][1] & walked[second][1])
            for first in range(len(walked))
            for second in range(first + 1, len(walked))
            if walked[first][0] != walked[second][0]
        )
        if total <= CROSSINGS_MAX:
            continue
        findings.append(
            _finding(
                "TOO_MANY_CROSSINGS",
                IssueSeverity.WARNING,
                f"la tavola {sheet.sheet_id} porta {total} nodi condivisi fra tratte "
                f"diverse: su una centrale semplice gli incroci stanno sulle dita di "
                f"una mano, cioe' {CROSSINGS_MAX} (B3, D-060)",
                [sheet.sheet_id],
            )
        )
    return findings


def longitudinal_overlap(
    drawing: DrawingGeometry, frame: SheetFrame
) -> list[ValidationIssue]:
    """B2, D-062 — vietato sovrapporre longitudinalmente: divieto, non costo.

    Si misurano gli **spigoli** percorsi in comune, non i nodi toccati: due
    tratte che si tagliano condividono un nodo e non si sovrappongono. L'unica
    eccezione ammessa e' quella che D-062 dichiara — un solo passo di griglia
    contro una porta condivisa dalle due tratte, che sulla tavola e' una
    derivazione.
    """
    findings: list[ValidationIssue] = []
    grid_mm = frame.standard.grid_mm
    for sheet in drawing.sheets:
        walked = [
            (index, route, segment, _edges(segment, grid_mm))
            for index, route, segment in _run_polylines(sheet)
        ]
        for first in range(len(walked)):
            for second in range(first + 1, len(walked)):
                one, other = walked[first], walked[second]
                if one[0] == other[0]:
                    continue
                shared = one[3] & other[3]
                if len(shared) <= SHARED_EDGES_MAX:
                    continue
                if len(shared) <= SHARED_EDGES_AT_A_SHARED_PORT and _at_a_shared_port(
                    one[2], other[2], shared
                ):
                    continue
                findings.append(
                    _finding(
                        "RUNS_OVERLAP_LENGTHWISE",
                        IssueSeverity.BLOCKING,
                        f"le tratte {_run_name(one[1])} e {_run_name(other[1])} corrono "
                        f"sovrapposte per {len(shared) * grid_mm:g} mm: due linee sullo "
                        f"stesso tratto sono una linea sola (B2, D-062)",
                        sorted({*_run_ids(sheet, one[1]), *_run_ids(sheet, other[1])}),
                    )
                )
    return findings


def _at_a_shared_port(
    first: list[Point],
    second: list[Point],
    shared: set[tuple[tuple[float, float], tuple[float, float]]],
) -> bool:
    """L'eccezione di D-062: lo spigolo comune tocca una porta capo di entrambe."""
    ends = {
        (round(point.x_mm, GRID_ROUNDING_DIGITS), round(point.y_mm, GRID_ROUNDING_DIGITS))
        for point in (first[0], first[-1])
    } & {
        (round(point.x_mm, GRID_ROUNDING_DIGITS), round(point.y_mm, GRID_ROUNDING_DIGITS))
        for point in (second[0], second[-1])
    }
    return any(edge[0] in ends or edge[1] in ends for edge in shared)


def clearances(drawing: DrawingGeometry, frame: SheetFrame) -> list[ValidationIssue]:
    """B5, B6 — le linee non sfiorano i simboli e non si affiancano troppo.

    Sotto la distanza minima dello standard grafico si blocca; esattamente sulla
    soglia si avvisa, perche' un valore che tocca il limite lo supera al primo
    ritocco. La distanza zero fra due paralleli non si conta qui: quella e' una
    sovrapposizione, e la misura sua e' `longitudinal_overlap`.
    """
    findings: list[ValidationIssue] = []
    minimum = frame.standard.min_clearance_mm
    for sheet in drawing.sheets:
        findings.extend(_symbol_clearances(sheet, minimum))
        findings.extend(_parallel_clearances(sheet, minimum))
    return findings


def _symbol_clearances(sheet: SheetGeometry, minimum: float) -> list[ValidationIssue]:
    """B5 — le linee non sfiorano i simboli cui non si attaccano."""
    findings: list[ValidationIssue] = []
    for _, route, segment in _run_polylines(sheet):
        moves = moves_of(segment)
        if not moves:
            continue
        for symbol in sheet.symbols:
            box = box_of(symbol)
            if attaches_to(segment, box):
                continue
            gap = min(distance_to_box(before, after, box) for before, after in moves)
            severity = _clearance_severity(gap, minimum)
            if severity is None:
                continue
            findings.append(
                _finding(
                    "RUN_TOO_CLOSE_TO_A_SYMBOL",
                    severity,
                    f"la tratta {_run_name(route)} passa a {gap:g} mm dal simbolo "
                    f"{symbol.component_id}, cui non si attacca: la distanza di "
                    f"rispetto e' {minimum:g} mm (B5)",
                    sorted({*_run_ids(sheet, route), symbol.component_id}),
                )
            )
    return findings


def _parallel_clearances(sheet: SheetGeometry, minimum: float) -> list[ValidationIssue]:
    """B6 — due linee affiancate corrono a distanza dichiarata, non a filo."""
    findings: list[ValidationIssue] = []
    alongside = [
        (index, route, move)
        for index, route, segment in _run_polylines(sheet)
        for move in moves_of(segment)
    ]
    for first in range(len(alongside)):
        for second in range(first + 1, len(alongside)):
            one, other = alongside[first], alongside[second]
            if one[0] == other[0]:
                continue
            gap = _parallel_distance(one[2], other[2])
            if gap is None or gap <= TOLERANCE_MM:
                continue
            severity = _clearance_severity(gap, minimum)
            if severity is None:
                continue
            findings.append(
                _finding(
                    "PARALLEL_RUNS_TOO_CLOSE",
                    severity,
                    f"le tratte {_run_name(one[1])} e {_run_name(other[1])} corrono "
                    f"affiancate a {gap:g} mm: la distanza di rispetto e' "
                    f"{minimum:g} mm (B6)",
                    sorted({*_run_ids(sheet, one[1]), *_run_ids(sheet, other[1])}),
                )
            )
    return findings


def u_turns(drawing: DrawingGeometry, frame: SheetFrame) -> list[ValidationIssue]:
    """B12, D-078 — nessuna andata e ritorno per raggiungere un pezzo.

    Il capo di una spezzata e' una porta, e l'ultimo tratto dice da che parte le
    si arriva. Se la spezzata era gia' stata **oltre** quella porta lungo l'asse
    di arrivo, l'ha superata e ci e' tornata indietro: si sposta l'oggetto, non
    si allunga la linea. La misura vale su entrambi i capi, perche' il verso in
    cui una spezzata e' scritta e' una convenzione dell'instradatore e il
    difetto non lo e'.

    Il passo di griglia entra nella misura perche' l'imbocco di una porta rivolta
    all'indietro cade per forza un passo oltre la porta: quello e' l'attacco, non
    un giro, e `geometry.overshoot_mm` lo distingue.
    """
    findings: list[ValidationIssue] = []
    for sheet in drawing.sheets:
        for _, route, segment in _run_polylines(sheet):
            overshoot = overshoot_mm(segment, frame.standard.grid_mm)
            if overshoot <= U_TURN_OVERSHOOT_MAX_MM + TOLERANCE_MM:
                continue
            findings.append(
                _finding(
                    "RUN_OVERSHOOTS_ITS_PORT",
                    IssueSeverity.BLOCKING,
                    f"la tratta {_run_name(route)} supera di {overshoot:g} mm la "
                    f"propria porta di arrivo e ci torna indietro: si sposta "
                    f"l'oggetto, non si allunga la linea (B12, D-078)",
                    _run_ids(sheet, route),
                )
            )
    return findings


def _label_box(
    label: PlacedLabel, height_mm: float
) -> tuple[float, float, float, float]:
    width = text_width_mm(label.text, height_mm)
    return (
        label.anchor.x_mm,
        label.anchor.y_mm - height_mm,
        label.anchor.x_mm + width,
        label.anchor.y_mm,
    )


def _boxes_overlap(
    first: tuple[float, float, float, float], second: tuple[float, float, float, float]
) -> bool:
    return (
        first[0] < second[2] - TOLERANCE_MM
        and second[0] < first[2] - TOLERANCE_MM
        and first[1] < second[3] - TOLERANCE_MM
        and second[1] < first[3] - TOLERANCE_MM
    )


def labels_on_runs(drawing: DrawingGeometry, frame: SheetFrame) -> list[ValidationIssue]:
    """D5, DRAW-003 — un testo non copre una tubazione.

    Le etichette sono l'ultima fase del disegno e non hanno costo rispetto
    alla geometria (DRAW-003-R1): il disegnatore scrive un testo solo su un
    posto libero, e se non ce n'e' uno lo omette. Un testo sopra una linea — o
    a meno del franco che i testi tengono dalle linee — e' quindi una tavola
    che non esce dal disegnatore, o una regressione; e' un **avviso**, perche'
    nessun rilievo sui testi blocca l'emissione della tavola.
    """
    findings: list[ValidationIssue] = []
    height = frame.standard.text_small_mm
    for sheet in drawing.sheets:
        stretches = [
            (
                route,
                (
                    min(before.x_mm, after.x_mm) - LINE_CLEARANCE_MM,
                    min(before.y_mm, after.y_mm) - LINE_CLEARANCE_MM,
                    max(before.x_mm, after.x_mm) + LINE_CLEARANCE_MM,
                    max(before.y_mm, after.y_mm) + LINE_CLEARANCE_MM,
                ),
            )
            for _, route, segment in _run_polylines(sheet)
            for before, after in moves_of(segment)
        ]
        for label in sheet.labels:
            box = _label_box(label, height)
            hit = next((route for route, other in stretches if _boxes_overlap(box, other)), None)
            if hit is None:
                continue
            findings.append(
                _finding(
                    "LABEL_ON_A_RUN",
                    IssueSeverity.WARNING,
                    f"l'etichetta {label.id} copre la tratta {_run_name(hit)}: un testo "
                    f"si scrive su un posto libero o si omette (D5, D-075, DRAW-003-R1)",
                    sorted({sheet.sheet_id, label.id, *hit.connection_ids}),
                )
            )
    return findings


def omitted_tags(drawing: DrawingGeometry) -> list[ValidationIssue]:
    """DRAW-003-R1 — una sigla di macchina che non ha trovato posto.

    Il disegnatore scrive la sigla su un lato libero del pezzo o con un
    richiamo corto che non attraversa niente; se nemmeno quello esiste la
    omette, e la tavola esce lo stesso. Chi legge il preflight deve pero'
    saperlo: e' un avviso, mai un blocco, perche' l'impossibilita' di
    collocare un testo non ferma l'emissione della tavola.
    """
    findings: list[ValidationIssue] = []
    for sheet in drawing.sheets:
        written = {label.id for label in sheet.labels if label.role == "tag"}
        for symbol in sheet.symbols:
            if not symbol.tag or f"{symbol.component_id}-tag" in written:
                continue
            findings.append(
                _finding(
                    "TAG_OMITTED",
                    IssueSeverity.WARNING,
                    f"la sigla {symbol.tag} di {symbol.component_id} non e' scritta: "
                    f"nessun lato libero e nessun richiamo pulito (DRAW-003-R1)",
                    [sheet.sheet_id, symbol.component_id],
                )
            )
    return findings


def _leader_enters(
    leader: tuple[Point, Point], box: tuple[float, float, float, float]
) -> bool:
    """Vero se il richiamo percorre l'interno del riquadro (Liang-Barsky)."""
    before, after = leader
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


def leader_crossings(drawing: DrawingGeometry) -> list[ValidationIssue]:
    """DRAW-003 — i richiami non si incrociano fra loro, non attraversano tubi
    e non passano sopra simboli.

    Il disegnatore non produce un richiamo cosi' (DRAW-003-R1): quando nessuna
    diagonale pulita esiste il testo si omette. Un richiamo che attraversa
    qualcosa e' percio' una geometria scritta a mano o una regressione, ed e'
    un avviso: nessun rilievo sui testi blocca la tavola.
    """
    findings: list[ValidationIssue] = []
    for sheet in drawing.sheets:
        leaders = [
            (label, (label.leader_from, label.anchor))
            for label in sheet.labels
            if label.leader_from is not None
        ]
        runs = [
            (route, (before, after))
            for _, route, segment in _run_polylines(sheet)
            for before, after in moves_of(segment)
        ]
        for index, (label, leader) in enumerate(leaders):
            for other, other_leader in leaders[index + 1 :]:
                if segments_cross(leader, other_leader):
                    findings.append(
                        _finding(
                            "LEADERS_CROSS",
                            IssueSeverity.WARNING,
                            f"i richiami delle etichette {label.id} e {other.id} si "
                            f"incrociano: due richiami che si attraversano non dicono "
                            f"piu' chi parla di chi (D2, DRAW-003)",
                            sorted({sheet.sheet_id, label.id, other.id}),
                        )
                    )
            covered = next(
                (
                    symbol
                    for symbol in sheet.symbols
                    if _leader_enters(leader, box_of(symbol))
                ),
                None,
            )
            if covered is not None:
                findings.append(
                    _finding(
                        "LEADER_CROSSES_A_SYMBOL",
                        IssueSeverity.WARNING,
                        f"il richiamo dell'etichetta {label.id} passa sopra il simbolo "
                        f"{covered.component_id}: un richiamo che confonde non si "
                        f"disegna, il testo si omette (D2, DRAW-003-R1)",
                        sorted({sheet.sheet_id, label.id, covered.component_id}),
                    )
                )
            crossed = next((route for route, run in runs if segments_cross(leader, run)), None)
            if crossed is not None:
                findings.append(
                    _finding(
                        "LEADER_CROSSES_A_RUN",
                        IssueSeverity.WARNING,
                        f"il richiamo dell'etichetta {label.id} attraversa la tratta "
                        f"{_run_name(crossed)}: un richiamo che confonde non si "
                        f"disegna, il testo si omette (D2, DRAW-003-R1)",
                        sorted({sheet.sheet_id, label.id, *crossed.connection_ids}),
                    )
                )
    return findings


def orthogonality_of_leaders(drawing: DrawingGeometry) -> list[ValidationIssue]:
    """D2, D3, D-075 — un richiamo e' obliquo a 45 gradi, mai ortogonale.

    Le tubazioni sono sempre ortogonali (D-041, B1): un richiamo ortogonale ha
    la stessa forma e la stessa giacitura di un tubo, e si legge come un tubo.
    La diagonale risolve alla radice, perche' nessuna tubazione e' mai obliqua.

    La geometria dichiara del richiamo i **due capi**, non la spezzata: la
    misura sta quindi sui due capi, ed e' la sola che valga qualunque cosa
    faccia il renderer. Un richiamo si puo' disegnare come D-075 lo vuole — una
    sola diagonale a 45 gradi — se e solo se i due capi stanno a 45 gradi l'uno
    dall'altro. Se non ci stanno, chi disegna deve piegare, e una piega ad
    angolo retto e' esattamente il tubo finto che D-075 vieta.

    Un'etichetta senza richiamo non e' misurata: e' il caso giusto, la scritta
    piccola accanto al proprio pezzo (D1).
    """
    findings: list[ValidationIssue] = []
    for sheet in drawing.sheets:
        for label in sheet.labels:
            if label.leader_from is None:
                continue
            span_x = abs(label.anchor.x_mm - label.leader_from.x_mm)
            span_y = abs(label.anchor.y_mm - label.leader_from.y_mm)
            if span_x <= TOLERANCE_MM and span_y <= TOLERANCE_MM:
                continue
            if abs(span_x - span_y) <= TOLERANCE_MM:
                continue
            angle = math.degrees(math.atan2(span_y, span_x))
            if span_x <= TOLERANCE_MM or span_y <= TOLERANCE_MM:
                code = "ORTHOGONAL_LABEL_LEADER"
                message = (
                    f"il richiamo dell'etichetta {label.id} e' ortogonale "
                    f"({angle:.0f} gradi): ha la giacitura di una tubazione e si legge "
                    f"come un altro tubo, mentre un richiamo si disegna obliquo a "
                    f"{LEADER_ANGLE_DEG} gradi (D2, D3, D-075)"
                )
            else:
                code = "LEADER_NOT_AT_45_DEGREES"
                message = (
                    f"il richiamo dell'etichetta {label.id} unisce due capi a "
                    f"{angle:.0f} gradi invece che a {LEADER_ANGLE_DEG}: fra quei due "
                    f"punti una sola diagonale non ci sta e chi disegna deve piegare ad "
                    f"angolo retto, cioe' disegnare un altro tubo (D2, D3, D-075)"
                )
            findings.append(
                _finding(code, IssueSeverity.BLOCKING, message, [sheet.sheet_id, label.id])
            )
    return findings


def sheet_fill(drawing: DrawingGeometry, frame: SheetFrame) -> list[ValidationIssue]:
    """A1, A3 — il foglio e' pieno in modo uniforme, il disegno non sta su un lato.

    Due numeri: quanto l'ingombro dell'inchiostro copre dell'area di disegno, e
    quanto il quadrante piu' pieno pesa piu' del piu' vuoto. Il primo dice se la
    tavola e' una fascia; il secondo se e' appoggiata a un bordo.
    """
    findings: list[ValidationIssue] = []
    area = frame.drawing_rect_mm
    line_mm = frame.standard.line_medium_mm
    for sheet in drawing.sheets:
        ratio = _fill_ratio(sheet, area)
        if ratio < SHEET_FILL_MIN_RATIO:
            findings.append(
                _finding(
                    "SHEET_BARELY_FILLED",
                    IssueSeverity.WARNING,
                    f"la tavola {sheet.sheet_id}: il foglio e' pieno solo al "
                    f"{ratio * 100:.0f}%, sotto il {SHEET_FILL_MIN_RATIO * 100:.0f}% "
                    f"dichiarato: il disegno e' una fascia, non una tavola (A1)",
                    [sheet.sheet_id],
                )
            )
        areas = [
            _ink_area_mm2(sheet, quadrant, line_mm) for quadrant in _quadrants(area)
        ]
        if max(areas) <= TOLERANCE_MM:
            continue
        empty = [
            name for name, value in zip(QUADRANT_NAMES, areas, strict=True)
            if value <= TOLERANCE_MM
        ]
        if empty:
            findings.append(
                _finding(
                    "DRAWING_ALL_ON_ONE_SIDE",
                    IssueSeverity.WARNING,
                    f"la tavola {sheet.sheet_id}: il disegno e' tutto su un lato, "
                    f"{len(empty)} quadranti su 4 non portano inchiostro "
                    f"({', '.join(empty)}) (A1, A3)",
                    [sheet.sheet_id],
                )
            )
            continue
        imbalance = max(areas) / min(areas)
        if imbalance > QUADRANT_IMBALANCE_MAX:
            findings.append(
                _finding(
                    "DRAWING_ALL_ON_ONE_SIDE",
                    IssueSeverity.WARNING,
                    f"la tavola {sheet.sheet_id}: il disegno e' tutto su un lato, il "
                    f"quadrante piu' pieno porta {imbalance:.1f} volte l'inchiostro "
                    f"del piu' vuoto, oltre il limite di {QUADRANT_IMBALANCE_MAX:g} "
                    f"(A1, A3)",
                    [sheet.sheet_id],
                )
            )
    return findings


def next_sheet_fill(
    drawing: DrawingGeometry, frame: SheetFrame
) -> list[ValidationIssue]:
    """A2, D-072 — una tavola successiva esiste solo se porta contenuto vero.

    «Non ha senso separare in due fogli con il secondo completamente vuoto.» La
    prima tavola non e' misurata qui: una tavola sola non e' una divisione, e il
    suo riempimento lo dice `sheet_fill` come avviso.
    """
    findings: list[ValidationIssue] = []
    area = frame.drawing_rect_mm
    for sheet in drawing.sheets[1:]:
        ratio = _fill_ratio(sheet, area)
        if ratio >= NEXT_SHEET_FILL_MIN_RATIO:
            continue
        findings.append(
            _finding(
                "CONTINUATION_SHEET_TOO_EMPTY",
                IssueSeverity.BLOCKING,
                f"la tavola {sheet.sheet_id} e' piena solo al {ratio * 100:.0f}%, sotto "
                f"il {NEXT_SHEET_FILL_MIN_RATIO * 100:.0f}% dichiarato: si divide solo "
                f"se la tavola successiva e' abbastanza piena, altrimenti si ottimizza "
                f"quella che c'e' (A2, D-072)",
                [sheet.sheet_id],
            )
        )
    return findings


def symbol_sources(
    drawing: DrawingGeometry, catalog: ComponentRegistry
) -> list[ValidationIssue]:
    """C8, D-081, D-083 — nessun simbolo senza una fonte vera.

    La convenzione grafica interna non e' una fonte: e' il nome che si da' a un
    simbolo inventato. Un simbolo che la cita torna a essere una domanda aperta
    al PM, non un elaborato da consegnare.
    """
    used: dict[str, set[str]] = {}
    for sheet in drawing.sheets:
        for symbol in sheet.symbols:
            used.setdefault(symbol.symbol_id, set()).add(symbol.component_id)
    by_symbol = {item.symbol_id: item for item in catalog.all()}

    findings: list[ValidationIssue] = []
    for symbol_id in sorted(used):
        components = sorted(used[symbol_id])
        entities = [symbol_id, *components]
        subject = f"il simbolo {symbol_id}, {_how_many_components(len(components))},"
        definition = by_symbol.get(symbol_id)
        if definition is None:
            findings.append(
                _finding(
                    "SYMBOL_SOURCE_NOT_VERIFIABLE",
                    IssueSeverity.BLOCKING,
                    f"{subject} non si trova nel catalogo: la sua fonte non e' "
                    f"verificabile (D-083)",
                    entities,
                )
            )
            continue
        try:
            source = catalog.resolve(definition.id).symbol.manifest.source
        except CatalogError as exc:
            findings.append(
                _finding(
                    "SYMBOL_SOURCE_NOT_VERIFIABLE",
                    IssueSeverity.BLOCKING,
                    f"{subject} non si risolve sulla libreria dei simboli: {exc} (D-083)",
                    entities,
                )
            )
            continue
        if not source.strip():
            findings.append(
                _finding(
                    "SYMBOL_WITHOUT_A_DECLARED_SOURCE",
                    IssueSeverity.BLOCKING,
                    f"{subject} non dichiara nessuna fonte: la mancanza di fonte e' una "
                    f"domanda al PM, non una licenza (D-083)",
                    entities,
                )
            )
        elif source.strip() == INVENTED_SOURCE:
            findings.append(
                _finding(
                    "SYMBOL_FROM_AN_INVENTED_CONVENTION",
                    IssueSeverity.BLOCKING,
                    f"{subject} cita {INVENTED_SOURCE}: la convenzione interna non e' "
                    f"una fonte, e' il nome di un simbolo inventato (C8, D-081, D-083)",
                    entities,
                )
            )
    return findings


def _how_many_components(count: int) -> str:
    return f"usato da {count} componente" if count == 1 else f"usato da {count} componenti"


def preflight_drawing(
    drawing: DrawingGeometry, frame: SheetFrame, catalog: ComponentRegistry
) -> list[ValidationIssue]:
    """Tutte le misure di qualita', nell'ordine dichiarato da `MEASURE_ORDER`.

    L'ordine e' parte dell'esito: chi legge il rapporto trova prima le linee,
    poi i testi, poi il foglio, infine le fonti — e lo trova sempre nello stesso
    posto, quale che sia la tavola.
    """
    return [
        *bends_per_run(drawing),
        *crossings(drawing, frame),
        *longitudinal_overlap(drawing, frame),
        *clearances(drawing, frame),
        *u_turns(drawing, frame),
        *orthogonality_of_leaders(drawing),
        *labels_on_runs(drawing, frame),
        *leader_crossings(drawing),
        *omitted_tags(drawing),
        *sheet_fill(drawing, frame),
        *next_sheet_fill(drawing, frame),
        *symbol_sources(drawing, catalog),
    ]
