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
3. gli attraversamenti e le tratte oltre le tre pieghe, che non devono crescere;
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

from collections.abc import Callable
from typing import NamedTuple

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import Rect, SheetFrame
from disegnatore_mep.graphics.symbol import PortFace, SymbolManifest
from disegnatore_mep.model.project import ProjectModel

from .composition import Standing, levels_of, standing_of
from .errors import LayoutError
from .geometry import (
    INK_COVERAGE_MIN,
    QUADRANT_IMBALANCE_MAX,
    PlacedSymbol,
    Point,
    RoutedTrunk,
    box_of,
    fill_ratio,
    ink_box,
    ink_coverage,
    ink_imbalance,
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
degli accessori. E' il tetto che tiene il costo limitato, non le passate.

**Alzarlo non serve**, ed e' misurato: portandolo a seicentocinquanta, sulla
tavola dell'impianto 1 non cambia una sola misura. Quando il ciclo si ferma con
un'andata e ritorno ancora in piedi non e' perche' ha finito le prove: e'
perche' nessuna delle mosse che conosce la toglie.
"""

NUDGE_STEPS = (1, 2, 4)
"""Le traslazioni provate, in passi di griglia: le vicine prima delle lontane."""

SPREAD_STEPS = (2, 4, 8, 16)
"""Gli allontanamenti dal centro provati dalla distensione, in passi di griglia.

Piu' lunghi delle traslazioni del ciclo che li precede, e per un motivo
diverso: quelle cercano di **togliere una piega**, e una piega si toglie
allineandosi a un vicino; questa cerca di **occupare il foglio**, e il foglio e'
grande. Sedici passi sono quaranta millimetri, un ottavo della larghezza utile
di una A3, e piu' in la' non si guadagna piu' niente: provare anche
ventiquattro passi non ha cambiato una misura, e ogni passo in piu' e' un
instradamento di prova speso.
"""

FILL_TARGET_RATIO = 0.60
"""Il riempimento oltre il quale la distensione si ferma (A1, D-111).

E' **lo stesso numero del preflight**, che avvisa quando la tavola e' piena
per meno di tre quinti: il collocatore non insegue un obiettivo proprio, insegue
quello gia' dichiarato. Fermarsi appena e' raggiunto e' la meta' che conta di
D-080 — «anche la lunghezza delle tratte costa, non facciamo che spargiamo le
macchine in giro»: la distensione compra riempimento pagando in lunghezza, e
smette appena il riempimento c'e'.
"""

MAX_SPREAD_TRIALS = 700
"""Tetto di instradamenti di prova per la sola distensione.

Separato da quello del ciclo che la precede, perche' le due fasi cercano cose
diverse e una non deve consumare il bilancio dell'altra. Come l'altro, scatta
in modo deterministico: stessi ingressi, stesse prove, stesso punto di arresto.

Il numero e' **misurato, non scelto**: sull'impianto 1 la distensione si
esaurisce da sola dopo poco piu' di cinquecento prove, quando nessuna mossa
migliora piu' nulla. Un tetto piu' basso la fermava prima del capolinea, e la
tavola usciva riempita a meta' — il tetto non deve essere il vincolo che decide
la tavola.
"""

_SNUG_STEPS = 2
"""Stacco fra la porta di chi si avvicina e quella del suo pari.

Due passi, come `place.CLEARANCE_STEPS`: e' la distanza a cui una linea si
stacca dal bordo del simbolo, quindi la minima a cui due porte affacciate si
collegano senza che la tratta sembri disegnata sul simbolo.
"""

BENDS_PER_RUN_MAX = 3
"""Pieghe oltre le quali una tratta e' un giro attorno a qualcosa (B4, D-060).

Lo stesso numero che il preflight usa per il proprio avviso: la distensione non
deve poter comprare una tratta che il controllo di qualita' segnalera'.
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

    long_runs: int = 0
    """Le tratte che cambiano direzione piu' di tre volte (B4, D-060).

    Contate a parte dal totale delle pieghe, perche' sono due difetti diversi:
    trenta pieghe sparse su venti tratte sono un disegno normale, quattro su una
    sola tratta sono un giro attorno a un ostacolo. La distensione non deve
    comprare ne' l'uno ne' l'altro.
    """

    bends: int = 0
    """Le pieghe, contate a parte dall'obiettivo.

    L'obiettivo le somma alla lunghezza, e alla distensione serve invece
    tenerle separate: li' la lunghezza **deve** poter crescere — allontanare due
    pezzi allunga il tubo che li unisce — mentre le pieghe non devono crescere
    di una.
    """

    fill: float = 0.0
    """Quanta area di disegno copre l'ingombro dell'inchiostro (A1, D-111)."""

    coverage: float = 1.0
    """Quante celle dell'ingombro portano inchiostro, sul totale.

    Serve a una cosa sola, e ce ne vuole una apposta: impedire che il
    riempimento si compri con una **propaggine**. Il riempimento misura il
    rettangolo che circonda il disegno, quindi basta spingere un pezzo leggero
    lontano da tutti — una valvola di sicurezza, uno sfiato, con il loro stelo —
    per allungare quel rettangolo di due centimetri di carta bianca. Misurato:
    su una prima versione di questo ciclo, dei tredici punti di riempimento
    guadagnati **nove venivano da un pezzo solo**.

    ⛔ **Il primo rimedio non rimediava niente**, e vale la pena scriverlo:
    misurare lo squilibrio fra i quattro quadranti dell'**ingombro** da'
    esattamente lo stesso numero che misurarlo sui quadranti dell'area centrata
    su di esso — stesse rette di divisione, stesso inchiostro — quindi la
    condizione in piu' era logicamente identica a quella che c'era gia'. Una
    propaggine sta **dentro** un quadrante e non lo svuota: la si vede solo
    guardando piu' fitto, ed e' quello che fa questa misura.
    """

    spread: float = 1.0
    """Squilibrio dell'inchiostro fra i quattro quadranti dell'area di disegno.

    E' la seconda misura che la carta chiede — «si copre meta' foglio con una
    mano: se una meta' e' quasi bianca e l'altra e' fitta, non va» — ed e' la
    stessa che il preflight pesa a tavola finita. Il riempimento da solo non la
    ottiene: un disegno puo' coprire i tre quarti del foglio e avere tutto
    l'inchiostro in una striscia.
    """


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


def _centred_on(
    box: tuple[float, float, float, float] | None,
    area: tuple[float, float, float, float],
) -> tuple[float, float, float, float]:
    """L'area di disegno **come la vedra' il blocco una volta centrato**.

    Il ciclo sceglie una posa, e dopo di lui la composizione porta il blocco al
    centro del foglio: misurare i quadranti dove i pezzi stanno adesso vuol dire
    misurare una tavola che non uscira'. Al posto di traslare la posa — che
    costa e non serve a nulla — si trasla il rettangolo: stessa misura, e
    invariante rispetto a dove il blocco si trova in questo momento.
    """
    if box is None:
        return area
    centre_x = (box[0] + box[2]) / 2.0
    centre_y = (box[1] + box[3]) / 2.0
    half_width = (area[2] - area[0]) / 2.0
    half_height = (area[3] - area[1]) / 2.0
    return (
        centre_x - half_width,
        centre_y - half_height,
        centre_x + half_width,
        centre_y + half_height,
    )


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
    # Il riempimento si misura sull'**area di disegno**, che e' il foglio meno
    # margini e fascia della legenda: la stessa che guarda il preflight.
    sheet_rect = (drawing.x_mm, drawing.y_mm, drawing.right_mm, drawing.bottom_mm)
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
            bends=sum(
                max(len(segment) - 2, 0)
                for route in settled.routes
                for segment in route.segments
            ),
            long_runs=sum(
                1
                for route in settled.routes
                if sum(max(len(segment) - 2, 0) for segment in route.segments)
                > BENDS_PER_RUN_MAX
            ),
            fill=fill_ratio(settled.symbols, settled.routes, sheet_rect),
            spread=ink_imbalance(
                settled.symbols,
                settled.routes,
                _centred_on(ink_box(settled.symbols, settled.routes), sheet_rect),
                frame.standard.line_medium_mm,
            ),
            coverage=ink_coverage(
                settled.symbols,
                settled.routes,
                ink_box(settled.symbols, settled.routes),
            ),
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

    exhausted = False
    for _ in range(MAX_PASSES):
        if exhausted:
            break
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
                    # Il tetto ferma **questo** ciclo, non la composizione: la
                    # distensione che segue ha il proprio bilancio e le proprie
                    # mosse, e finiva saltata per intero ogni volta che il
                    # foglio spendeva qui tutte le prove.
                    exhausted = True
                    break
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
                # Una tratta che smette di girare attorno a un ostacolo si
                # accetta anche a obiettivo fermo, come si accetta un'andata e
                # ritorno in meno: quattro pieghe su una tratta sola non sono
                # una tavola piu' cara, sono un giro (B4).
                shortened = (
                    same_fit
                    and len(found.turnbacks) == len(current_best.turnbacks)
                    and found.crossings <= current_best.crossings
                    and found.long_runs < current_best.long_runs
                )
                better = (
                    same_fit
                    and len(found.turnbacks) == len(current_best.turnbacks)
                    and found.crossings <= current_best.crossings
                    # Nemmeno una tratta in piu' oltre le tre pieghe: e' un
                    # rilievo di qualita' per se' (B4), e l'obiettivo totale non
                    # lo vede — trenta pieghe sparse su venti tratte le somma
                    # come quattro su una sola, che invece e' un giro attorno a
                    # un ostacolo. Senza questa voce il ciclo comprava una
                    # tratta lunga per risparmiare due pieghe altrove.
                    and found.long_runs <= current_best.long_runs
                    and found.objective < current_best.objective
                )
                if repaired or straightened or shortened or better:
                    best = trial
                    current_best = found
                    moved = True
                    break
            if exhausted:
                break
        if not moved:
            break

    # **Poi si distende**, ed e' la seconda meta' del lavoro (D-111, A1).
    #
    # Il ciclo qui sopra ottimizza pieghe, incroci e lunghezza, e le tre voci
    # tirano tutte dalla stessa parte: **stringere**. Il risultato e' corretto e
    # sta in un angolo — sull'impianto 1 il foglio finiva pieno al 29 %, contro
    # il 60 % che la carta chiede, con il quadrante piu' pieno che portava dodici
    # volte l'inchiostro del piu' vuoto. La misura c'era gia' nel preflight; a
    # mancare era che qualcuno la usasse **mentre** dispone, invece di scoprirla
    # alla fine con un avviso.
    #
    # La distensione allontana i pezzi dal centro del disegno e tiene la mossa
    # solo se il foglio si riempie o l'inchiostro si distribuisce meglio, **e**
    # se non costa niente di cio' che il PM ha messo prima: nessuna piega in
    # piu', nessun incrocio in piu', nessuna andata e ritorno in piu', nessuna
    # tratta che perde i propri accessori. Cresce solo la lunghezza, che e' il
    # prezzo dichiarato del riempimento, e cresce **finche' serve**: raggiunto
    # il riempimento richiesto la fase si ferma (D-080).
    return _spread_out(
        order=order,
        best=best,
        current_best=current_best,
        evaluate=evaluate,
        is_valid=is_valid,
        manifest_at=manifest_at,
        step=step,
    )


def _spread_out(
    *,
    order: list[str],
    best: dict[str, PlacedSymbol],
    current_best: _Outcome,
    evaluate: Callable[[dict[str, PlacedSymbol]], _Outcome | None],
    is_valid: Callable[[str, _Move], bool],
    manifest_at: Callable[[str, int], SymbolManifest],
    step: float,
) -> list[PlacedSymbol]:
    """Allontana i pezzi dal centro finche' il foglio si riempie (A1, D-111).

    Greedy e deterministico come il ciclo che la precede: i componenti si
    esaminano nell'ordine di posa, le mosse in ordine fisso, si accetta la prima
    che migliora, e un tetto di prove ferma la fase in un punto che non dipende
    da quanto tempo ha girato.

    Le mosse sono **allontanamenti dal centro dell'ingombro**: chi sta a destra
    va a destra, chi sta in alto va in alto. E' la mossa che apre il disegno
    senza rimescolarlo — l'ordine di processo da sinistra a destra e le colonne
    restano quelli che erano, perche' a difenderli e' lo stesso predicato di
    validita' del ciclo precedente.
    """
    trials = 0
    # Due passaggi con le stesse mosse e due criteri diversi, e in quest'ordine:
    # prima si **riempie** il foglio, poi si **distribuisce** l'inchiostro a
    # riempimento fermo. Sono le due misure che la carta chiede (A1, A3) e che
    # il preflight gia' pesava a tavola finita; un criterio solo non le ottiene
    # entrambe, perche' quasi ogni mossa cambia il riempimento di un pelo e il
    # bilanciamento non arriverebbe mai al proprio turno.
    # Due giri, non uno: la fase che distribuisce lascia dietro di se' un
    # margine — lo squilibrio scende sotto il limite — e quel margine e' spazio
    # in cui la fase che riempie puo' tornare a lavorare. Con un giro solo
    # restava inutilizzato.
    for filling in (False, True, False, True):
        moved = True
        while moved and (not filling or current_best.fill < FILL_TARGET_RATIO):
            moved = False
            box = ink_box([best[item] for item in order], current_best.routes)
            if box is None:
                break
            centre_x = (box[0] + box[2]) / 2.0
            centre_y = (box[1] + box[3]) / 2.0
            # ⚠ **Le due fasi guardano gli stessi pezzi e provano le stesse
            # mosse**, e conviene lasciarle cosi'. Restringere la fase che
            # distribuisce ai soli pezzi del quadrante piu' pieno, o mandarli
            # verso il piu' vuoto invece che via dal centro, sembra piu' mirato
            # e costa meno prove: misurato, porta il riempimento dal 42 al 37 %
            # e peggiora anche incroci e pieghe. Il motivo e' che questa fase
            # non serve solo a se stessa — rimescola la posa, e da quel
            # rimescolamento la fase che riempie riparte.
            for component_id in order:
                current = best[component_id]
                here_x = current.origin.x_mm + current.width_mm / 2
                here_y = current.origin.y_mm + current.height_mm / 2
                away_x = 1.0 if here_x >= centre_x else -1.0
                away_y = 1.0 if here_y >= centre_y else -1.0
                # **Il foglio lo allarga solo chi sta sul bordo dell'ingombro.**
                # Spostare un pezzo interno non sposta di un millimetro il
                # rettangolo che il riempimento misura, quindi in questa fase
                # non e' una candidata: e' una prova di instradamento buttata, e
                # le prove sono contate. Nella fase che distribuisce
                # l'inchiostro valgono invece tutti, perche' li' conta dove il
                # pezzo sta dentro il rettangolo, non quanto e' grande.
                on_edge_x = (
                    current.right_mm >= box[2] - step - _TOLERANCE_MM
                    if away_x > 0
                    else current.origin.x_mm <= box[0] + step + _TOLERANCE_MM
                )
                on_edge_y = (
                    current.bottom_mm >= box[3] - step - _TOLERANCE_MM
                    if away_y > 0
                    else current.origin.y_mm <= box[1] + step + _TOLERANCE_MM
                )
                candidates = [
                    _Move(
                        Point(
                            x_mm=current.origin.x_mm + away_x * count * step,
                            y_mm=current.origin.y_mm,
                        ),
                        current.rotation_deg,
                    )
                    for count in SPREAD_STEPS
                    if on_edge_x or not filling
                ] + [
                    _Move(
                        Point(
                            x_mm=current.origin.x_mm,
                            y_mm=current.origin.y_mm + away_y * count * step,
                        ),
                        current.rotation_deg,
                    )
                    for count in SPREAD_STEPS
                    if on_edge_y or not filling
                ] + [
                    # E in diagonale, che e' la mossa che apre davvero un
                    # angolo: chi sta in un vertice dell'ingombro lo allarga su
                    # tutti e due gli assi insieme, e una traslazione per volta
                    # non ci arriva mai perche' la prima da sola non guadagna
                    # niente e viene scartata.
                    _Move(
                        Point(
                            x_mm=current.origin.x_mm + away_x * count * step,
                            y_mm=current.origin.y_mm + away_y * count * step,
                        ),
                        current.rotation_deg,
                    )
                    for count in SPREAD_STEPS
                    if (on_edge_x and on_edge_y) or not filling
                ]
                for move in candidates:
                    if trials >= MAX_SPREAD_TRIALS:
                        return [best[item] for item in order]
                    if not is_valid(component_id, move):
                        continue
                    trials += 1
                    shape = manifest_at(component_id, move.rotation_deg)
                    trial = dict(best)
                    trial[component_id] = current.model_copy(
                        update={
                            "origin": move.origin,
                            "rotation_deg": move.rotation_deg,
                            "width_mm": shape.width_mm,
                            "height_mm": shape.height_mm,
                        }
                    )
                    found = evaluate(trial)
                    if found is None:
                        continue
                    # Niente di cio' che viene prima puo' peggiorare: la tavola
                    # che ospita i propri accessori, le andate e ritorno, gli
                    # incroci e le pieghe. La lunghezza si', ed e' il prezzo.
                    if (
                        len(found.unfit) > len(current_best.unfit)
                        or len(found.turnbacks) > len(current_best.turnbacks)
                        or found.crossings > current_best.crossings
                        or found.bends > current_best.bends
                        or found.long_runs > current_best.long_runs
                    ):
                        continue
                    # Le due misure si tengono per mano, e questo e' il punto.
                    # Riempire senza guardare la distribuzione non fa una
                    # tavola: basta portare un pezzo leggero in cima al foglio
                    # per far salire il riempimento — e' un rettangolo che si
                    # allunga — mentre l'inchiostro resta tutto in basso. Sulla
                    # prima prova il riempimento saliva dal 29 al 63 % e lo
                    # squilibrio fra quadranti da 12 a 32: un numero migliore e
                    # una tavola peggiore. Quindi: si riempie **a patto che la
                    # distribuzione non peggiori**, poi si distribuisce a
                    # riempimento fermo.
                    if filling:
                        # Riempire e' ammesso finche' l'inchiostro resta
                        # distribuito, e le due misure guardano due cose
                        # diverse: `spread` che la tavola non stia tutta da un
                        # lato, `coverage` che il rettangolo non si allunghi su
                        # una **propaggine** — un pezzo leggero spinto lontano
                        # da tutti, che allunga l'ingombro riempiendo una cella
                        # sola. La seconda e' l'unica che impedisce di comprare
                        # punti di riempimento con carta bianca.
                        gained = found.fill > current_best.fill + _TOLERANCE_MM and (
                            (
                                found.spread <= QUADRANT_IMBALANCE_MAX
                                or found.spread <= current_best.spread + _TOLERANCE_MM
                            )
                            and (
                                found.coverage >= INK_COVERAGE_MIN
                                or found.coverage
                                >= current_best.coverage - _TOLERANCE_MM
                            )
                        )
                    else:
                        gained = (
                            found.fill >= current_best.fill - _TOLERANCE_MM
                            and found.spread < current_best.spread - _TOLERANCE_MM
                        )
                    if not gained:
                        continue
                    best = trial
                    current_best = found
                    moved = True
                    break
    return [best[item] for item in order]


__all__ = [
    "MAX_PASSES",
    "MAX_TRIAL_ROUTINGS",
    "improve_sheet",
    "objective_of",
    "overshoots_the_goal",
]
