"""La disposizione al servizio delle linee (D-078, D-080).

Il PM, cerchiando il giro attorno al prelievo ACS sulla tavola completa:
«potevi spostarlo, metterlo in linea, e non fare quel giretto li'. Abbiamo
detto che le curve costano, invece spostare gli oggetti sulla tavola e'
gratis. Non devi mettere gli oggetti in tavola e poi fare le linee — o meglio
lo fai, ma poi gli oggetti si spostano per ottimizzare il routing, non
viceversa.» E subito dopo, la correzione preventiva (D-080): «ricordati che
anche la lunghezza delle tratte costa, non facciamo che spargiamo le macchine
in giro, dobbiamo bilanciare tutto.»

Qui la disposizione di `place.py` smette di essere l'ultima parola. Dopo un
instradamento di prova si generano mosse discrete dei componenti — traslazioni
**e rotazioni** fra quelle che il manifesto ammette; per ciascuna si reinstrada
l'**intero foglio** e la mossa si tiene solo se l'obiettivo totale — pieghe,
attraversamenti e lunghezza, con i pesi di D-060 — scende davvero. Mai una voce
sola a spese delle altre.

La rotazione serve un difetto che nessuna traslazione chiude: un terminale con
una porta sola — il confine di rete dell'ACS — la tiene rivolta a destra mentre
l'alimentazione gli arriva da sinistra, e la linea deve superarlo e tornare
indietro. Spostarlo non cambia da che parte guarda: girarlo si'.

**Il confronto e' lessicografico**, e la prima voce non e' l'obiettivo ma
l'andata e ritorno. Nell'ordine:

1. le tratte che non ospitano i propri accessori in linea (D-027): una mossa
   che ne recupera una vale qualunque obiettivo;
2. le **andate e ritorno** (B12): una tratta che supera la propria meta e torna
   indietro non e' un disegno caro, e' un disegno sbagliato. Una mossa che ne
   toglie una si accetta anche a obiettivo invariato; una che ne aggiunge una
   non si accetta mai, per nessun guadagno;
3. gli attraversamenti, che non devono crescere;
4. l'obiettivo totale, che deve scendere strettamente.

Vincoli mai violabili, qualunque sia il guadagno:

- l'ordine di processo da sinistra a destra (D-060): nessuno spostamento
  altera l'ordine orizzontale dei centri di due estremi collegati;
- le distanze minime fra simboli, con lo stesso predicato del posizionamento;
- chi sta a terra resta alla propria quota: si scorre lungo la fascia, non si
  vola. La quota di un componente a terra la decide il posizionamento —
  compreso l'impilamento di D-073 — non questo ciclo;
- tutto sulla griglia e dentro l'area di disegno; i simboli non si toccano;
- nessun accessorio in linea a meno della distanza di rispetto da una tratta
  che non e' la sua, e nessuno sovrapposto a un simbolo: il preflight lo tratta
  come bloccante, quindi qui non e' un costo da pagare ma una posa da scartare;
- determinismo: candidati in ordine fisso, accettazione greedy della prima
  mossa che migliora, tetto fisso di instradamenti di prova.

L'instradamento di prova e' quello **completo**, accessori in linea compresi:
`settle_sheet`, la stessa funzione con cui `compose_sheet` disegna. Prima era
quello senza, e il ragionamento sembrava solido — gli accessori si posano sulla
tratta gia' instradata (D-027), quindi non possono cambiare il segno di un
confronto. Non e' vero, e la tavola del caso completo lo ha dimostrato in due
modi: un accessorio posato dopo che una **altra** tratta era gia' passata di li'
le finiva addosso a 0 mm — tre rilievi bloccanti — e un'andata e ritorno che il
ciclo credeva di aver tolto restava nel disegno consegnato, perche' la
geometria misurata non era quella disegnata. Il ciclo deve ottimizzare cio' che
esce, non un'approssimazione piu' comoda: costa di piu' per prova, e si paga
abbassando il tetto delle prove, non guardando la tavola sbagliata.
"""

from typing import NamedTuple

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import Rect, SheetFrame
from disegnatore_mep.graphics.symbol import PortFace, SymbolManifest
from disegnatore_mep.model.project import ProjectModel

from .composition import Standing, levels_of, standing_of
from .errors import LayoutError
from .geometry import (
    PlacedSymbol,
    Point,
    RoutedTrunk,
    box_of,
    overshoot_mm,
    run_intrudes_on,
)
from .grid import GridSpace, is_on_grid
from .inline import SettledSheet, settle_sheet
from .partition import SheetPartition
from .place import ROUTING_MARGIN_MM, ROW_GAP_MM
from .route import CROSS_COST, STEP_COST, TURN_COST

MAX_PASSES = 8
"""Passate del ciclo di miglioramento: limitato e monotono (D-078).

Erano tre, e tre bastavano finche' il ciclo valutava un instradamento senza
accessori. Da quando valuta quello vero le prime passate le spende a togliere
le tratte che non ospitano i propri accessori — la voce che comanda il
confronto — e chiudevano il ciclo con un giro attorno a un oggetto ancora li'.
Alla quarta passata quel giro se ne va; dall'ottava il guadagno per passata e'
ormai qualche millimetro di lunghezza, e il tempo lo si paga tutto.
"""

MAX_TRIAL_ROUTINGS = 400
"""Tetto di instradamenti di prova per foglio.

Raggiunto il tetto si restituisce la migliore disposizione trovata fin li'.
Il tetto scatta in modo deterministico — stessi ingressi, stesse prove, stesso
punto di arresto — quindi non costa la riproducibilita' bit-a-bit.

Il numero segue le passate e il costo di una prova, che ora comprende la posa
degli accessori: la tavola completa ne spende poco piu' di 260 e disegna in una
ventina di secondi. E' il tetto che tiene il costo limitato, non le passate.
"""

NUDGE_STEPS = (1, 2, 4)
"""Le traslazioni provate, in passi di griglia: le vicine prima delle lontane."""

_SNUG_STEPS = 2
"""Stacco fra la porta di chi si avvicina e quella del suo pari.

Due passi, come `place.CLEARANCE_STEPS`: e' la distanza a cui una linea si
stacca dal bordo del simbolo, quindi la minima a cui due porte affacciate si
collegano senza che la tratta sembri disegnata sul simbolo.
"""

_TOLERANCE_MM = 1e-6


class _Move(NamedTuple):
    """Una candidata: dove va l'origine del riquadro e come e' girato.

    Traslazione e rotazione sono la stessa cosa per il ciclo — una posa
    alternativa da provare instradando — e viaggiano insieme perche' la
    validita' di un riquadro dipende da entrambe: a 90 e 270 gradi il
    manifesto scambia larghezza e altezza, e il riquadro da verificare contro
    l'area, la terra e i vicini non e' piu' quello di prima.
    """

    origin: Point
    rotation_deg: int


class _Outcome(NamedTuple):
    """Cio' che una prova di instradamento dice della disposizione provata."""

    unfit: tuple[int, ...]
    """Indici delle tratte che non ospitano i propri accessori in linea."""

    turnbacks: tuple[int, ...]
    """Indici delle tratte che fanno un'andata e ritorno (B12)."""

    objective: int
    crossings: int
    routes: list[RoutedTrunk]


_HORIZONTAL_FACES = (PortFace.LEFT, PortFace.RIGHT)
"""Le facce per cui l'allineamento in quota ha senso.

Due porte affacciate su fianchi si collegano con una linea orizzontale quando
stanno sulla stessa riga: e' la mossa che toglie pieghe. Una porta sul fondo o
sul cielo scarica in verticale, e portarla «sulla riga» dell'altra non produce
nessuna linea diritta: produce l'uncino che poi l'instradamento paga.
"""


def objective_of(routes: list[RoutedTrunk], step_mm: float) -> int:
    """L'obiettivo del PM, intero: pieghe, attraversamenti, lunghezza (D-060).

    Stessi pesi dell'instradatore — `TURN_COST`, `CROSS_COST`, `STEP_COST` —
    perche' e' la stessa regola: qui si sommano sulle tratte gia' instradate
    invece che sui passi di un percorso da scegliere.
    """
    total = 0
    for route in routes:
        for segment in route.segments:
            total += TURN_COST * max(len(segment) - 2, 0)
            length = sum(
                abs(after.x_mm - before.x_mm) + abs(after.y_mm - before.y_mm)
                for before, after in zip(segment, segment[1:], strict=False)
            )
            total += STEP_COST * round(length / step_mm)
        total += CROSS_COST * len(route.crossings)
    return total


def overshoots_the_goal(route: RoutedTrunk, goal: Point) -> bool:
    """Vero se la tratta supera la porta di destinazione per poi tornarci (B12).

    Il corollario di D-078: «un componente non si raggiunge mai con un'andata
    e ritorno; se la linea lo supera e torna indietro, e' l'oggetto a essere
    nel posto sbagliato». Il confine e' la perpendicolare per la porta di
    arrivo: per un approccio orizzontale e' la verticale per la porta, per uno
    verticale l'orizzontale. Ogni punto della spezzata oltre quel confine, nel
    verso di arrivo, e' un'andata oltre la meta che la tratta deve disfare.

    E' il **giro attorno all'oggetto**, quello che il PM ha cerchiato: la porta
    guarda da una parte e la linea arriva dall'altra, quindi la tratta scavalca
    il pezzo per rientrargli dal lato giusto. Non e' la stessa cosa che misura
    `geometry.overshoot_mm`, che guarda la spezzata disegnata e vede se torna
    su se stessa; il ciclo le conta **tutte e due**, perche' sono due difetti e
    non due nomi dello stesso.
    """
    if not route.segments:
        return False
    last = route.segments[-1]
    if len(last) < 2:
        return False
    end, before = last[-1], last[-2]
    horizontal = abs(end.x_mm - before.x_mm) > abs(end.y_mm - before.y_mm)
    points = [point for segment in route.segments for point in segment]
    if horizontal:
        sign = 1.0 if end.x_mm > before.x_mm else -1.0
        overshoot = max((point.x_mm - goal.x_mm) * sign for point in points)
    else:
        sign = 1.0 if end.y_mm > before.y_mm else -1.0
        overshoot = max((point.y_mm - goal.y_mm) * sign for point in points)
    return overshoot > _TOLERANCE_MM


def _relation(left: float, right: float) -> int:
    return (left > right) - (left < right)


def improve_sheet(
    project: ProjectModel,
    partition: SheetPartition,
    catalog: ComponentRegistry,
    frame: SheetFrame,
    placed: list[PlacedSymbol],
    inline_ids: frozenset[str],
) -> list[PlacedSymbol]:
    """Rivede la disposizione reinstradando: si tiene solo cio' che migliora.

    Greedy e deterministico: i componenti colpevoli — estremi di tratte con
    pieghe, attraversamenti o andate e ritorno — si esaminano nell'ordine di
    posa; per ciascuno si prova una lista fissa di mosse alternative —
    traslazioni e rotazioni ammesse dal manifesto — e si accetta la prima che
    migliora nell'ordine lessicografico del modulo. Una passata senza mosse
    chiude il ciclo; tre passate lo chiudono comunque.

    `inline_ids` non entra nel ciclo: gli accessori in linea non sono ancora
    posati, e l'instradamento di prova gira apposta senza di loro.
    """
    trunks = list(partition.trunks)
    if not placed or not trunks:
        return list(placed)

    drawing = frame.drawing_rect_mm
    # Lo stesso rettangolo ridotto dentro cui `place_sheet` posa: il corridoio
    # di instradamento lungo il bordo resta libero anche quando ci si sposta.
    area = Rect(
        x_mm=drawing.x_mm + ROUTING_MARGIN_MM,
        y_mm=drawing.y_mm + ROUTING_MARGIN_MM,
        width_mm=drawing.width_mm - 2 * ROUTING_MARGIN_MM,
        height_mm=drawing.height_mm - 2 * ROUTING_MARGIN_MM,
    )
    grid = GridSpace(origin=drawing, standard=frame.standard)
    step = grid.step_mm
    clearance = frame.standard.min_clearance_mm
    levels = levels_of(drawing.y_mm, drawing.height_mm, step)

    definitions = {item.id: item.definition_id for item in project.components}
    upright: dict[str, SymbolManifest] = {}
    features: dict[str, tuple[frozenset[str], bool]] = {}
    for item in placed:
        resolved = catalog.resolve(definitions[item.component_id])
        upright[item.component_id] = resolved.symbol.manifest
        features[item.component_id] = (
            frozenset(resolved.definition.functions),
            resolved.is_inline,
        )

    turned: dict[tuple[str, int], SymbolManifest] = {}

    def manifest_at(component_id: str, rotation_deg: int) -> SymbolManifest:
        """Il manifesto del componente girato di tanto, calcolato una volta.

        Si parte sempre dal manifesto **diritto** del catalogo: ruotare un
        manifesto gia' ruotato rimappa le rotazioni ammesse, e chiedergli
        quelle originali darebbe la risposta sbagliata.
        """
        found = turned.get((component_id, rotation_deg))
        if found is None:
            found = upright[component_id].rotated(rotation_deg)
            turned[component_id, rotation_deg] = found
        return found

    def manifest_of(item: PlacedSymbol) -> SymbolManifest:
        return manifest_at(item.component_id, item.rotation_deg)

    def standing_at(component_id: str, rotation_deg: int) -> Standing:
        functions, is_inline = features[component_id]
        return standing_of(
            manifest_at(component_id, rotation_deg).height_mm, functions, is_inline
        )

    standings = {
        item.component_id: standing_at(item.component_id, item.rotation_deg)
        for item in placed
    }

    order = [item.component_id for item in placed]
    best = {item.component_id: item for item in placed}
    trials = 0

    owning_run = {
        component_id: index
        for index, trunk in enumerate(trunks)
        for component_id in trunk.inline_component_ids
    }

    def accessories_are_clear(settled: SettledSheet) -> bool:
        """Nessun accessorio addosso a una tratta altrui o a un simbolo (B5).

        E' la misura del preflight, letta qui prima che la tavola esista: un
        accessorio e' un simbolo, e una tratta che non e' la sua gli deve stare
        alla distanza di rispetto. Quale sia la sua non si indovina dalla
        geometria come fa il preflight: lo dice la tratta che lo porta.
        """
        for accessory in settled.accessories:
            box = box_of(accessory)
            mine = owning_run.get(accessory.component_id)
            others = [
                route
                for index, route in enumerate(settled.routes)
                if index != mine
            ]
            if run_intrudes_on(box, others, clearance):
                return False
            for other in settled.symbols:
                if other is accessory:
                    continue
                if (
                    box[0] < other.right_mm - _TOLERANCE_MM
                    and other.origin.x_mm < box[2] - _TOLERANCE_MM
                    and box[1] < other.bottom_mm - _TOLERANCE_MM
                    and other.origin.y_mm < box[3] - _TOLERANCE_MM
                ):
                    return False
        return True

    def evaluate(layout: dict[str, PlacedSymbol]) -> _Outcome | None:
        """Un instradamento di prova completo, contato contro il tetto.

        Completo vuol dire **con gli accessori posati**: `settle_sheet` e' la
        stessa funzione con cui la tavola si disegna, quindi cio' che si misura
        qui e' cio' che uscira'. Oltre all'obiettivo restituisce quali tratte
        non riescono a ospitare i propri accessori in linea (D-027) —
        avvicinare e' gratis solo finche' gli accessori trovano il proprio
        rettilineo, e una disposizione che glielo toglie costerebbe l'intera
        tavola, non una piega — e quali fanno un'andata e ritorno (B12), che e'
        la voce che comanda il confronto.

        Due esiti non sono candidature e valgono `None`: una posa che non si
        lascia instradare, e una che ci riesce mettendo un accessorio addosso a
        una tratta che non e' la sua. La seconda e' un rilievo bloccante del
        preflight: pagarla con qualche piega in meno sarebbe comprare una
        tavola che non si consegna.
        """
        nonlocal trials
        trials += 1
        symbols = [layout[item] for item in order]
        try:
            settled = settle_sheet(
                project, trunks, list(symbols), catalog, grid, tolerant=True
            )
        except LayoutError:
            return None
        if not accessories_are_clear(settled):
            return None
        # Le due andate e ritorno, contate insieme e sulle spezzate
        # **disegnate**: il giro attorno all'oggetto, che guarda la porta di
        # arrivo, e il ritorno su se stessa, che e' la misura del preflight e
        # legge entrambi i capi. Prima il ciclo contava solo la prima, e sulla
        # geometria senza accessori: cosi' non vedeva ne' il giro sulla porta di
        # **partenza** ne' l'effetto delle interruzioni sulle spezzate.
        turnbacks: list[int] = []
        for index, (trunk, route) in enumerate(
            zip(trunks, settled.routes, strict=True)
        ):
            arrival = layout[trunk.end.component_id]
            port = manifest_of(arrival).port(trunk.end.port_id)
            goal = Point(
                x_mm=arrival.origin.x_mm + port.x_mm,
                y_mm=arrival.origin.y_mm + port.y_mm,
            )
            if overshoots_the_goal(route, goal) or any(
                overshoot_mm(segment, step) > _TOLERANCE_MM
                for segment in route.segments
            ):
                turnbacks.append(index)
        return _Outcome(
            unfit=settled.unfit,
            turnbacks=tuple(turnbacks),
            objective=objective_of(settled.routes, step),
            crossings=sum(len(route.crossings) for route in settled.routes),
            routes=settled.routes,
        )

    def candidates_of(component_id: str) -> list[_Move]:
        """Le mosse alternative, in ordine fisso: prima gli allineamenti di
        porta, poi le rotazioni, poi le traslazioni verticali, poi le
        orizzontali.

        Le rotazioni stanno **dopo gli allineamenti e prima delle
        traslazioni** perche' costano meno di tutte: girare un simbolo non lo
        muove di un millimetro, quindi non tocca ne' l'ordine di processo ne'
        lo spazio dei vicini, e nella catena greedy conviene provarla prima di
        mettersi a far scorrere l'oggetto per la tavola. E' anche l'unica
        mossa che possa pagare un'andata e ritorno dovuta al verso di una
        porta, che nessuna traslazione toglie.
        """
        me = best[component_id]
        manifest = manifest_of(me)
        here = me.rotation_deg
        out: list[_Move] = []
        # (a) La quota che porta la propria porta sulla riga della porta del
        # pari, per ogni tratta che li collega: e' la mossa che rende
        # possibile la linea diritta. E la stessa quota con l'ascissa appena
        # oltre la porta del pari, per chi puo' avvicinarsi.
        for trunk in trunks:
            for mine, other in (
                (trunk.start, trunk.end),
                (trunk.end, trunk.start),
            ):
                if mine.component_id != component_id:
                    continue
                peer = best.get(other.component_id)
                if peer is None:
                    continue
                own_port = manifest.port(mine.port_id)
                peer_port = manifest_of(peer).port(other.port_id)
                if (
                    own_port.face not in _HORIZONTAL_FACES
                    or peer_port.face not in _HORIZONTAL_FACES
                ):
                    continue
                aligned_y = peer.origin.y_mm + peer_port.y_mm - own_port.y_mm
                out.append(_Move(Point(x_mm=me.origin.x_mm, y_mm=aligned_y), here))
                snug_x = (
                    peer.origin.x_mm
                    + peer_port.x_mm
                    + _SNUG_STEPS * step
                    - own_port.x_mm
                )
                out.append(_Move(Point(x_mm=snug_x, y_mm=aligned_y), here))
        # (b) Rotazioni: quelle che il manifesto ammette, in gradi crescenti,
        # con l'origine ferma. Il riquadro pero' cambia — a 90 e 270 gradi
        # larghezza e altezza si scambiano — e lo rivaluta il predicato di
        # validita' come per qualunque altra mossa.
        for degrees in sorted(upright[component_id].allowed_rotations_deg):
            if degrees != here:
                out.append(_Move(me.origin, degrees))
        # (c) Traslazioni verticali: in alto prima che in basso, vicino prima
        # che lontano.
        for count in NUDGE_STEPS:
            out.append(
                _Move(Point(x_mm=me.origin.x_mm, y_mm=me.origin.y_mm - count * step), here)
            )
            out.append(
                _Move(Point(x_mm=me.origin.x_mm, y_mm=me.origin.y_mm + count * step), here)
            )
        # (d) Traslazioni orizzontali: l'ordine di processo le limita, e a
        # controllarlo e' il predicato di validita'.
        for count in NUDGE_STEPS:
            out.append(
                _Move(Point(x_mm=me.origin.x_mm - count * step, y_mm=me.origin.y_mm), here)
            )
            out.append(
                _Move(Point(x_mm=me.origin.x_mm + count * step, y_mm=me.origin.y_mm), here)
            )
        return out

    def in_a_ground_column(component_id: str) -> bool:
        """Vero se il componente a terra divide la colonna con un altro.

        E' la coppia impilata di D-073: si muove insieme o non si muove, e
        questo ciclo non ha mosse di coppia. Sfilare orizzontalmente uno dei
        due trasformerebbe la pila in una scala.
        """
        me = best[component_id]
        for other_id in order:
            if other_id == component_id or standings[other_id] is not Standing.GROUND:
                continue
            other = best[other_id]
            if me.origin.x_mm < other.right_mm and other.origin.x_mm < me.right_mm:
                return True
        return False

    def heads_a_column_with_another(component_id: str) -> bool:
        """Vero se un altro componente ha lo stesso bordo sinistro, sopra o sotto.

        E' la stessa ragione di `in_a_ground_column`, estesa a chi a terra non
        sta: i rami paralleli che il posizionamento incolonna — le due zone
        servite dallo stesso collettore — stanno una sopra l'altra e allineate a
        sinistra, e quell'allineamento e' cio' che le fa leggere come due rami
        della stessa derivazione invece che come due pezzi sparsi (A3, D-073).
        Il ciclo non ha mosse di coppia: sfilarne uno in orizzontale non sposta
        una colonna, la trasforma in una scala. Le mosse verticali restano
        libere, perche' non toccano l'allineamento.
        """
        me = best[component_id]
        for other_id in order:
            if other_id == component_id:
                continue
            other = best[other_id]
            if abs(other.origin.x_mm - me.origin.x_mm) > _TOLERANCE_MM:
                continue
            if (
                other.bottom_mm <= me.origin.y_mm + _TOLERANCE_MM
                or me.bottom_mm <= other.origin.y_mm + _TOLERANCE_MM
            ):
                return True
        return False

    def is_valid(component_id: str, move: _Move) -> bool:
        me = best[component_id]
        target = move.origin
        manifest = manifest_at(component_id, move.rotation_deg)
        # Girare un simbolo non puo' cambiare che cosa e' sulla tavola: se la
        # rotazione lo fa scendere sotto la soglia delle macchine, o salirci,
        # non e' piu' lo stesso pezzo e la sua quota la deve decidere il
        # posizionamento, non questo ciclo.
        if standing_at(component_id, move.rotation_deg) is not standings[component_id]:
            return False
        # Chi sta a terra scorre lungo la fascia: la quota non si tocca. Vale
        # anche per chi la terra l'ha lasciata impilandosi (D-073): quella
        # quota l'ha decisa il posizionamento, non questo ciclo. E non si gira
        # in modo da cambiare altezza, che e' lo stesso che sollevarlo.
        if standings[component_id] is Standing.GROUND:
            if target.y_mm != me.origin.y_mm:
                return False
            if manifest.height_mm != me.height_mm:
                return False
            if target.x_mm != me.origin.x_mm and in_a_ground_column(component_id):
                return False
        # E chi divide la colonna con un altro non ci si sfila da solo, a terra
        # o no: la colonna e' una figura, e questo ciclo muove un pezzo per volta.
        if target.x_mm != me.origin.x_mm and heads_a_column_with_another(component_id):
            return False
        # Sulla griglia, misurata dall'origine dell'area come nel posizionamento.
        if not is_on_grid(target.x_mm - area.x_mm, step):
            return False
        if not is_on_grid(target.y_mm - area.y_mm, step):
            return False
        # Dentro l'area di posa, e mai sotto la linea di terra.
        if target.x_mm < area.x_mm - _TOLERANCE_MM:
            return False
        if target.y_mm < area.y_mm - _TOLERANCE_MM:
            return False
        if target.x_mm + manifest.width_mm > area.right_mm + _TOLERANCE_MM:
            return False
        if target.y_mm + manifest.height_mm > levels.ground_mm + _TOLERANCE_MM:
            return False
        # Lo stesso stacco del posizionamento fra due simboli (D-062).
        for other_id in order:
            if other_id == component_id:
                continue
            other = best[other_id]
            if (
                target.x_mm < other.right_mm + ROW_GAP_MM
                and other.origin.x_mm - ROW_GAP_MM < target.x_mm + manifest.width_mm
                and target.y_mm < other.bottom_mm + ROW_GAP_MM
                and other.origin.y_mm - ROW_GAP_MM < target.y_mm + manifest.height_mm
            ):
                return False
        # L'ordine di processo e' un vincolo, non un costo (D-060): l'ordine
        # orizzontale dei centri dei due estremi di **ogni** tratta resta
        # quello della disposizione corrente. Per le tratte orientate e' il
        # verso del fluido; per quelle che la topologia non decide vale
        # l'ordine gia' disegnato, che da quel verso discende.
        old_centre = me.origin.x_mm + me.width_mm / 2
        new_centre = target.x_mm + manifest.width_mm / 2
        for trunk in trunks:
            start_id = trunk.start.component_id
            end_id = trunk.end.component_id
            if component_id not in (start_id, end_id) or start_id == end_id:
                continue
            other_id = end_id if start_id == component_id else start_id
            peer = best.get(other_id)
            if peer is None:
                continue
            other_centre = peer.origin.x_mm + peer.width_mm / 2
            if start_id == component_id:
                before = _relation(old_centre, other_centre)
                after = _relation(new_centre, other_centre)
            else:
                before = _relation(other_centre, old_centre)
                after = _relation(other_centre, new_centre)
            if after != before:
                return False
        return True

    current_best = evaluate(best)
    if current_best is None:
        return list(placed)

    for _ in range(MAX_PASSES):
        moved = False
        offending: set[str] = set()
        for index, (trunk, route) in enumerate(
            zip(trunks, current_best.routes, strict=True)
        ):
            has_bends = any(len(segment) > 2 for segment in route.segments)
            if (
                has_bends
                or route.crossings
                or index in current_best.unfit
                or index in current_best.turnbacks
            ):
                offending.add(trunk.start.component_id)
                offending.add(trunk.end.component_id)
        for component_id in (item for item in order if item in offending):
            current = best[component_id]
            seen: set[tuple[float, float, int]] = set()
            for move in candidates_of(component_id):
                key = (move.origin.x_mm, move.origin.y_mm, move.rotation_deg)
                if key in seen or key == (
                    current.origin.x_mm,
                    current.origin.y_mm,
                    current.rotation_deg,
                ):
                    continue
                seen.add(key)
                if not is_valid(component_id, move):
                    continue
                if trials >= MAX_TRIAL_ROUTINGS:
                    return [best[item] for item in order]
                box = manifest_at(component_id, move.rotation_deg)
                trial = dict(best)
                trial[component_id] = current.model_copy(
                    update={
                        "origin": move.origin,
                        "rotation_deg": move.rotation_deg,
                        "width_mm": box.width_mm,
                        "height_mm": box.height_mm,
                    }
                )
                found = evaluate(trial)
                if found is None:
                    continue
                # Il confronto lessicografico del modulo, nell'ordine.
                # Prima di tutto viene la tavola intera: una mossa che fa
                # entrare gli accessori di una tratta che non li ospitava vale
                # qualunque obiettivo. Poi l'andata e ritorno, che non e' un
                # costo ma un errore: toglierne una si accetta anche a
                # obiettivo fermo, aggiungerne una non si accetta mai. Solo a
                # parita' di entrambe si guarda al disegno: gli
                # attraversamenti non devono crescere — non si comprano
                # nemmeno pagando in pieghe e lunghezza, perche' sono la voce
                # che l'occhio paga per prima dopo le pieghe (D-060) — e
                # l'obiettivo **totale** deve scendere, mai una voce a spese
                # del totale (D-080).
                same_fit = len(found.unfit) == len(current_best.unfit)
                repaired = len(found.unfit) < len(current_best.unfit)
                straightened = same_fit and len(found.turnbacks) < len(
                    current_best.turnbacks
                )
                better = (
                    same_fit
                    and len(found.turnbacks) == len(current_best.turnbacks)
                    and found.crossings <= current_best.crossings
                    and found.objective < current_best.objective
                )
                if repaired or straightened or better:
                    best = trial
                    current_best = found
                    moved = True
                    break
        if not moved:
            break
    return [best[item] for item in order]


__all__ = [
    "MAX_PASSES",
    "MAX_TRIAL_ROUTINGS",
    "improve_sheet",
    "objective_of",
    "overshoots_the_goal",
]
