"""La dilatazione proporzionale della posa (**D-142**, `DRAW-013` §A).

Il PO, guardando le tavole della PR #41: «se devo rendere comoda la tavola
**allargo tutte le linee di un X per cento**, non che allungo solo un tratto per
prendere piu' spazio, e' proprio brutto cosi'». Qui sta quella mossa, ed e'
l'**unica** che insegue il riempimento: lo stiramento del singolo tratto
(`improve._stretch_moves`) resta, ma solo per far entrare il corredo dove non ci
sta, e il riempimento non lo puo' piu' comprare.

**Che cosa fa.** Su ciascun asse si costruisce una funzione monotona a tratti:
**pendenza 1** dove c'e' un simbolo — cosi' i simboli restano della loro
misura — e **pendenza pari al fattore** nel vuoto fra un simbolo e l'altro. Il
disegno cresce conservando la propria forma:

* nessun pezzo si sposta **rispetto agli altri**: chi stava sopra resta sopra,
  chi stava in colonna resta in colonna;
* un tratto orizzontale resta orizzontale e uno verticale resta verticale,
  perche' le due funzioni lavorano su un asse per volta: **nessuna piega nasce
  e nessuna sparisce**;
* gli attraversamenti sono gli stessi punti, portati avanti dalla stessa
  funzione: non se ne aggiunge uno.

**Perche' le fasce rigide si fondono.** Se due simboli si sovrappongono sulla
proiezione di un asse, la pendenza 1 vale per tutt'e due e quindi per tutto
l'intervallo che coprono insieme: una funzione sola dell'ascissa e' cio' che
tiene in colonna i pezzi incolonnati, e una funzione sola dell'ordinata e' cio'
che tiene in quota i pezzi allineati. E' anche il limite della mossa: dove le
proiezioni sono fitte il disegno **non puo'** crescere su quell'asse senza che
un pezzo si sposti rispetto a un altro, che e' proprio cio' che D-142 vieta.

**La griglia.** Il risultato resta sui nodi, e ci resta **per costruzione**:
i vuoti si misurano in passi, si moltiplicano per il fattore e si riportano al
passo piu' vicino. Un fattore esatto su ogni vuoto non esiste — un vuoto di
`m` passi resta intero solo se il fattore e' `t/q` con `q` divisore del massimo
comun divisore di **tutti** i vuoti, e su queste tavole quel divisore e' 1,
quindi sarebbero ammessi i soli fattori interi e nessun intero ci sta nel
foglio. Il PO, richiesto: «stretchare tutto di un X per cento finche' ci sta
spazio senza uscire dalla tavola; se c'e' spazio stretchi altrimenti no». Il
fattore percio' resta **uno solo per foglio** e lo scarto e' quello della
griglia: meno di mezzo passo per vuoto, cioe' meno di 1,25 mm, e la tavola
resta instradabile. Lo scarto massimo si misura e il rapporto lo porta.
"""

from collections.abc import Callable, Iterable

from disegnatore_mep.graphics.frame import Rect

from .geometry import (
    SHEET_FILL_MAX_RATIO,
    TOLERANCE_MM,
    PlacedSymbol,
    Point,
    RoutedTrunk,
    SheetGeometry,
    ink_box,
    margin_allowed_mm,
    moves_of,
)

MAX_FACTOR = 4.0
"""Fin dove si cerca il fattore, e non e' una taratura del disegno.

E' il tetto della ricerca: oltre il quadruplo nessun disegno di questa
famiglia entrerebbe piu' nel foglio, e la scala serve solo a non enumerare
all'infinito una successione che non converge da sola.
"""


def _rigid_spans(
    symbols: Iterable[PlacedSymbol], horizontal: bool
) -> list[tuple[float, float]]:
    """Le fasce che la dilatazione **non** allarga: i simboli, fusi.

    Un simbolo conserva la propria misura (ADR 0003: la scala di stampa e'
    invariante), quindi la funzione dell'asse ha pendenza 1 su tutta la sua
    proiezione. Due proiezioni che si toccano diventano una fascia sola:
    altrimenti la funzione non sarebbe una funzione.
    """
    raw = sorted(
        (item.origin.x_mm, item.right_mm)
        if horizontal
        else (item.origin.y_mm, item.bottom_mm)
        for item in symbols
    )
    merged: list[tuple[float, float]] = []
    for low, high in raw:
        if merged and low <= merged[-1][1] + TOLERANCE_MM:
            merged[-1] = (merged[-1][0], max(merged[-1][1], high))
        else:
            merged.append((low, high))
    return merged


def _gaps(spans: list[tuple[float, float]], low: float, high: float) -> list[float]:
    """I vuoti che la dilatazione allarga, da un capo all'altro del disegno.

    Contano anche i due estremi: il tubo che esce dall'ultimo simbolo e corre
    verso il bordo e' vuoto quanto quello che passa fra due simboli, e la
    funzione dell'asse lo allarga allo stesso modo. Dimenticarlo qui darebbe
    un ingombro previsto piu' corto di quello vero, e la scelta del fattore
    sceglierebbe su una misura sbagliata.
    """
    out: list[float] = []
    cursor = low
    for start, end in spans:
        if start > cursor + TOLERANCE_MM:
            out.append(start - cursor)
        cursor = max(cursor, end)
    if high > cursor + TOLERANCE_MM:
        out.append(high - cursor)
    return out


def _mapper(
    spans: list[tuple[float, float]],
    low: float,
    high: float,
    factor: float,
    step_mm: float,
) -> Callable[[float], float]:
    """La funzione dell'asse: pendenza 1 sulle fasce rigide, il vuoto allargato.

    I vuoti crescono tutti del **medesimo** fattore e si posano sul passo, cosi'
    ogni nodo della griglia va in un nodo della griglia. Dentro un vuoto la
    pendenza e' quella che porta il suo capo al posto nuovo: un punto della
    tubazione in mezzo al vuoto si sposta in proporzione, come il vuoto.
    """
    gaps = _gaps(spans, low, high)
    grown = iter(_stretched_gaps(gaps, factor, step_mm))
    pieces: list[tuple[float, float, float]] = []
    cursor = low
    moved = low
    for start, end in spans:
        if start > cursor + TOLERANCE_MM:
            width = next(grown)
            pieces.append((cursor, moved, width / (start - cursor)))
            moved += width
            cursor = start
        if end > cursor + TOLERANCE_MM:
            pieces.append((cursor, moved, 1.0))
            moved += end - cursor
            cursor = end
    tail = next(grown, None)
    slope = 1.0 if tail is None or high <= cursor + TOLERANCE_MM else tail / (high - cursor)
    pieces.append((cursor, moved, slope))

    def at(value: float) -> float:
        chosen = pieces[0]
        for piece in pieces:
            if value >= piece[0] - TOLERANCE_MM:
                chosen = piece
            else:
                break
        return chosen[1] + (value - chosen[0]) * chosen[2]

    return at


def _stretched_gaps(
    gaps: list[float], factor: float, step_mm: float
) -> list[float]:
    """I vuoti allargati del fattore, riportati al passo.

    Il fattore e' **uno solo**: ogni vuoto lo riceve uguale, e cio' che la
    griglia non rappresenta si perde nello stesso modo per tutti. Un vuoto non
    si accorcia mai — il fattore non scende sotto 1 e l'arrotondamento non lo
    porta sotto il suo passo.
    """
    out: list[float] = []
    for gap in gaps:
        steps = gap / step_mm
        out.append(max(round(steps * factor), round(steps)) * step_mm)
    return out


def factor_error(sheet: SheetGeometry, factor: float, step_mm: float) -> float:
    """Di quanto il fattore realizzato si scosta da quello nominale, al peggio.

    E' la misura che il rapporto porta: zero vuol dire che il fattore e' esatto
    su ogni vuoto, e il resto dice quanto la griglia ha limato. Si legge sul
    vuoto, non sul disegno intero: e' li' che lo scarto e' piu' visibile.
    """
    box = ink_box(sheet.symbols, sheet.routes)
    if box is None:
        return 0.0
    worst = 0.0
    for horizontal, low, high in ((True, box[0], box[2]), (False, box[1], box[3])):
        gaps = _gaps(_rigid_spans(sheet.symbols, horizontal), low, high)
        for gap, grown in zip(gaps, _stretched_gaps(gaps, factor, step_mm), strict=True):
            if gap <= TOLERANCE_MM:
                continue
            worst = max(worst, abs(grown / gap - factor))
    return worst


def dilate_sheet(sheet: SheetGeometry, factor: float, step_mm: float) -> SheetGeometry:
    """La tavola dilatata del fattore dato. Fattore 1: la tavola com'e'."""
    if abs(factor - 1.0) <= TOLERANCE_MM:
        return sheet
    box = ink_box(sheet.symbols, sheet.routes)
    if box is None:
        return sheet
    across = _mapper(_rigid_spans(sheet.symbols, True), box[0], box[2], factor, step_mm)
    along = _mapper(_rigid_spans(sheet.symbols, False), box[1], box[3], factor, step_mm)

    def moved(point: Point) -> Point:
        return Point(x_mm=across(point.x_mm), y_mm=along(point.y_mm))

    return sheet.model_copy(
        update={
            "symbols": [
                item.model_copy(update={"origin": moved(item.origin)})
                for item in sheet.symbols
            ],
            "routes": [
                item.model_copy(
                    update={
                        "segments": [
                            [moved(point) for point in segment]
                            for segment in item.segments
                        ],
                        "crossings": [moved(point) for point in item.crossings],
                    }
                )
                for item in sheet.routes
            ],
            "labels": [
                item.model_copy(
                    update={
                        "anchor": moved(item.anchor),
                        "leader_from": (
                            None if item.leader_from is None else moved(item.leader_from)
                        ),
                    }
                )
                for item in sheet.labels
            ],
            "cross_references": [
                item.model_copy(update={"anchor": moved(item.anchor)})
                for item in sheet.cross_references
            ],
        }
    )


def dilated_span_mm(
    symbols: list[PlacedSymbol],
    routes: list[RoutedTrunk],
    factor: float,
    step_mm: float,
) -> tuple[float, float]:
    """Quanto misurerebbe l'ingombro, in larghezza e altezza, a quel fattore.

    Si legge dalla struttura — fasce rigide piu' vuoti allargati — senza
    costruire la tavola dilatata: scegliere il fattore e' una ricerca, e la
    ricerca prova molti fattori.
    """
    box = ink_box(symbols, routes)
    if box is None:
        return (0.0, 0.0)
    out: list[float] = []
    for horizontal, low, high in ((True, box[0], box[2]), (False, box[1], box[3])):
        gaps = _gaps(_rigid_spans(symbols, horizontal), low, high)
        rigid = (high - low) - sum(gaps)
        out.append(rigid + sum(_stretched_gaps(gaps, factor, step_mm)))
    return (out[0], out[1])


def _bends_and_crossings(routes: list[RoutedTrunk]) -> tuple[int, int]:
    """Pieghe e attraversamenti contati sulla geometria, come il collaudo."""
    bends = 0
    for route in routes:
        for segment in route.segments:
            bends += max(len(moves_of(segment)) - 1, 0)
    return (bends, sum(len(route.crossings) for route in routes))


def dilated_to_fit(
    sheet: SheetGeometry, area: Rect, step_mm: float
) -> tuple[SheetGeometry, float]:
    """La tavola allargata quanto il foglio permette, e il fattore usato (§A.2).

    **Uno solo per foglio**, e scelto dopo che il disegno e' risolto: il piu'
    grande che tiene l'ingombro dentro il margine di D-143 e non spinge il
    riempimento oltre la sponda alta della finestra di D-140. Il PO:
    «stretchare tutto di un X per cento finche' ci sta spazio senza uscire
    dalla tavola. Se c'e' spazio stretchi altrimenti no».

    Il margine e' quello che il disegno **a fattore 1** puo' permettersi: si
    stringe per far entrare un disegno, mai per far salire un numero, quindi
    dilatare non lo puo' mai stringere di piu'.

    ⛔ **Non e' mai una contrazione**: il fattore parte da 1 e non scende. Un
    disegno che non ci sta nemmeno cosi' resta quello che e', e il preflight lo
    dice.

    L'ultima parola e' della misura, ed e' la guardia di §E — **il riempimento
    e' salito per dilatazione e non per altro**: la tavola dilatata si tiene
    solo se pieghe e attraversamenti non peggiorano. Per come la funzione
    dell'asse e' fatta non possono, e proprio per questo il controllo costa poco
    e vale la pena di averlo.

    ⚠️ **La copertura dell'ingombro non entra in questa guardia, e il pacchetto
    dava per scontato che entrasse** (§A.1: «la copertura dell'ingombro non puo'
    scendere»). Il ragionamento e' giusto e la misura no: la dilatazione non
    sposta **nessun** pezzo rispetto agli altri, quindi non crea la propaggine
    che D-141 teme; ma `ink_coverage` divide l'ingombro in sessantaquattro celle
    **relative all'ingombro stesso**, e quando l'ingombro cresce le celle
    crescono con lui, cosi' una tavola scarica puo' perderne una o due senza che
    un solo pezzo si sia mosso. Misurato su una tavola di prova: 0,3125 →
    0,2500 a fattore 1,5. Tenerla nella guardia avrebbe bocciato la dilatazione
    proprio dove serve — sulle tavole scariche — e il rapporto di collaudo porta
    la variazione misurata tavola per tavola.
    """
    rect = (area.x_mm, area.y_mm, area.right_mm, area.bottom_mm)
    box = ink_box(sheet.symbols, sheet.routes)
    if box is None:
        return (sheet, 1.0)
    margin = margin_allowed_mm(sheet.symbols, sheet.routes, rect, step_mm)
    room_x = (rect[2] - rect[0]) - 2 * margin
    room_y = (rect[3] - rect[1]) - 2 * margin
    ceiling = SHEET_FILL_MAX_RATIO * (rect[2] - rect[0]) * (rect[3] - rect[1])

    # La scala dei fattori e' fitta un centesimo: piu' fitta di cosi' due
    # fattori vicini danno la **stessa** tavola, perche' i vuoti si posano
    # comunque sul passo. Si sale finche' si sta dentro, e si tiene l'ultimo
    # che ci sta: la ricerca e' deterministica e non dipende da dove comincia.
    chosen = 1.0
    steps = int(round((MAX_FACTOR - 1.0) * 100))
    for index in range(1, steps + 1):
        factor = 1.0 + index / 100.0
        width, height = dilated_span_mm(sheet.symbols, sheet.routes, factor, step_mm)
        if width > room_x + TOLERANCE_MM or height > room_y + TOLERANCE_MM:
            break
        if width * height > ceiling + TOLERANCE_MM:
            break
        chosen = factor
    if chosen <= 1.0 + TOLERANCE_MM:
        return (sheet, 1.0)

    grown = dilate_sheet(sheet, chosen, step_mm)
    if _bends_and_crossings(grown.routes) > _bends_and_crossings(sheet.routes):
        return (sheet, 1.0)
    return (grown, chosen)
