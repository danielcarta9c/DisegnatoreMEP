"""Le regole del piano, in forma di controllo.

Una regola e' un controllo che sa **nominare la propria violazione** (**D-153**):
se non si puo' misurare, il revisore non la puo' usare e resta un'intenzione. E'
la differenza fra «l'autostrada deve essere dritta» e «la tratta `s3` piega
quattro volte, e su un'autostrada le pieghe ammesse sono zero». Ogni messaggio
di questo modulo porta **i nomi veri e i numeri veri**: mai «violazione della
regola B1».

Quattro sono quelle che il PO ha dettato il 20 settembre 2026
(`docs/DECISION_LOG.md`, **D-154**); la quinta, **A4**, e' **D-145** e viene da
prima. Tutte vivono in `docs/regole-del-piano.md`:

| | regola | rilievo |
|---|---|---|
| **A1** | tre macro fasce verticali | `PIECE_OUTSIDE_ITS_BAND` |
| **A4** | un organo di servizio sta addosso al pezzo che serve | `SERVICE_STUB_LONGER_THAN_ITS_MINIMUM` |
| **B1** | prima le autostrade, e il piu' dritte possibile | `HIGHWAY_IS_NOT_STRAIGHT` |
| **B3** | piu' generatori o piu' terminali ⇒ collettore verticale | `PARALLEL_MACHINES_WITHOUT_A_COLLECTOR` |
| **B4** | un organo in linea non spezza il tratto | `INLINE_ORGAN_BREAKS_THE_RUN` |

⛔ **A4 e' qui per una ragione che vale per ogni riga futura.** Era gia' scritta
— **D-145**, 18 settembre — ma come **vincolo della posa del motore**, e da
**D-151** la posa non decide piu' dove stanno i pezzi: il piano scrive le
coordinate e le sovrascrive. Un vincolo che nessun rilievo misura **sulla tavola
finita** e' un vincolo che il piano rompe in silenzio, e questo l'ha rotto.

**Perche' tutte escono `WARNING`, e non bloccanti.** Una violazione di
regola e' un **difetto del piano**, e il piano lo corregge il revisore: e' il
suo mestiere, ed e' il motivo per cui questi controlli esistono
(`ARCHITETTURA-DEL-PIANO.md` §1). Il **cancello di consegna** resta quello del
preflight (**D-063**): li' sta cio' che rende una tavola inconsegnabile — una
tratta non risolta, un simbolo senza fonte, due linee sovrapposte. Far bloccare
una regola di composizione significherebbe rifiutare una tavola che il PO puo'
guardare e giudicare, e **una tavola segnata vale piu' di nessuna tavola**
(D-150).

**Lo stile e' quello del preflight**, e non per simmetria: ogni misura e' una
funzione pura che riceve la tavola e restituisce `ValidationIssue`, e ogni
soglia e' una costante nominata con la propria fonte accanto, dichiarata
**normata** o **tarata** (**D-083**: vietato inventare, e vietato far passare
una taratura per una norma).
"""

from collections.abc import Iterable
from math import ceil

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition
from disegnatore_mep.graphics.frame import SheetFrame
from disegnatore_mep.graphics.symbol import PortFace
from disegnatore_mep.layout.autostrade import (
    AutostradaInTavola,
    PorteInTavola,
    autostrade_del_progetto,
    pieghe_dell_autostrada,
    porte_in_tavola,
    tratte_del_progetto,
)
from disegnatore_mep.layout.flow import (
    BOUNDARY_FUNCTION,
    EXCHANGE_FUNCTIONS,
    GENERATOR_FUNCTIONS,
    STORE_FUNCTIONS,
)
from disegnatore_mep.layout.geometry import (
    DrawingGeometry,
    PlacedSymbol,
    Point,
    RoutedTrunk,
)
from disegnatore_mep.layout.hierarchy import (
    is_a_machine,
    ports_through,
    user_machines,
)
from disegnatore_mep.layout.partition import partition_project
from disegnatore_mep.layout.place import (
    ROW_GAP_MM,
    hanging_children,
    inline_room_mm,
    port_corridors,
    stub_minimum_mm,
)
from disegnatore_mep.layout.trunks import Trunk
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import IssueSeverity

from .issues import ValidationIssue

TOLLERANZA_MM = 1e-6
"""Quanto due coordinate possono differire ed essere ancora la stessa.

Confronto fra numeri in virgola mobile, non una soglia di disegno: non si tara.
"""

GENERAZIONE = "generazione"
ACCUMULI = "accumuli e scambiatori"
DISTRIBUZIONE = "distribuzione"

FASCE: tuple[str, ...] = (GENERAZIONE, ACCUMULI, DISTRIBUZIONE)
"""Le tre macro fasce verticali, **da sinistra a destra** (**D-154**, A1).

Le parole sono del PO, una per una: «tre macro fasce verticali di disegno:
generazione, accumuli e scambiatori, distribuzione». Precisano **D-041**, che
nominava due poli e non diceva che cosa sta in mezzo.
"""

ATTACCHI_DI_UN_ORGANO_IN_LINEA_MAX = 3
"""Quanti attacchi di percorso puo' avere un pezzo ed essere ancora un **organo**.

Non e' una taratura: e' la forma della valvola a tre vie che **D-154** nomina —
«ingresso e uscita allineati, il terzo attacco esce di lato» — e il numero e'
quello. Un pezzo con quattro o piu' attacchi sul percorso e' una **macchina**,
non un organo sulla linea: un accumulo ha cinque bocchettoni fisici su facce
diverse, e pretendere che due di essi siano allineati sarebbe pretendere che
l'accumulo sia un tubo.
"""

ATTACCHI_DI_UN_NODO_DI_COLLETTORE_MIN = 3
"""Da quanti attacchi di percorso un raccordo **unisce** invece di far passare.

Un raccordo con due soli attacchi sul percorso — il T di servizio che regge un
manometro o uno sfiato — non unisce niente: la linea gli passa attraverso. Un
raccordo con tre e' il punto in cui tre tratte si incontrano, ed e' di quelli
che una **catena di T** e' fatta (**B3**). La distinzione la dichiara il
catalogo con `off_the_run`, e non un elenco di nomi (D-069, D-093).
"""


def _rilievo(
    code: str, message: str, entity_ids: list[str]
) -> ValidationIssue:
    """Ogni rilievo di questo modulo e' un **avviso**: vedi il perche' in testa."""
    return ValidationIssue(
        code=code,
        severity=IssueSeverity.WARNING,
        message=message,
        entity_ids=entity_ids,
    )


def _definizioni(
    project: ProjectModel, catalog: ComponentRegistry
) -> dict[str, ComponentDefinition]:
    return {item.id: catalog.get(item.definition_id) for item in project.components}


def _attacchi_di_percorso(definition: ComponentDefinition) -> tuple[str, ...]:
    """Gli attacchi che stanno **sul percorso**: il catalogo esclude gli altri."""
    return tuple(port.id for port in definition.ports if not port.off_the_run)


def _scatola(symbol: PlacedSymbol) -> tuple[float, float]:
    return (symbol.origin.x_mm, symbol.right_mm)


def _centro_x(symbol: PlacedSymbol) -> float:
    return symbol.origin.x_mm + symbol.width_mm / 2


# --- A1 — tre macro fasce verticali -------------------------------------------


def fascia_del_pezzo(
    definition: ComponentDefinition, utenze: frozenset[str], component_id: str
) -> str | None:
    """In quale delle tre fasce sta questo pezzo, o `None` se non si sa.

    **La classificazione non si inventa** (D-069, D-093): si legge da cio' che
    il catalogo e `layout/flow.py` gia' dichiarano, e sono gli stessi insiemi
    che la gerarchia della tavola usa per decidere dove corrono le autostrade.

    - **generazione**: una macchina con un mestiere di `GENERATOR_FUNCTIONS`;
    - **accumuli e scambiatori**: una macchina con un mestiere di
      `STORE_FUNCTIONS | EXCHANGE_FUNCTIONS` — accumuli, puffer, separatori
      idraulici, scambiatori a piastre. Sono le parole del PO, e sono le stesse
      che `hierarchy.source_machines` legge;
    - **distribuzione**: una macchina di `hierarchy.user_machines` — i terminali
      che consegnano il calore all'ambiente.

    **Chi non ricade in nessuno dei tre non e' una violazione: si ignora.** Un
    raccordo e' un punto sulla tubazione, un organo in linea sta *sopra* una
    linea, un accessorio appeso segue il pezzo che serve, un collettore e' il
    punto in cui il fluido si divide e un confine che **immette** non e'
    un'utenza. Nessuno di questi ha una fascia propria nelle parole del PO, e
    metterlo in una sarebbe inventare una regola che non ha detto.

    ⛔ **E nemmeno un confine di rete**, benche' `user_machines` lo conti fra le
    utenze: il catalogo dichiara che un confine **non ha una posizione propria**
    e «va accanto all'utente che serve» (`flow.BOUNDARY_FUNCTION`, I-061,
    `DRAW-009` §A.2). Contarlo faceva partire la fascia della distribuzione dal
    punto in cui l'uscita ACS esce dall'accumulo — cioe' **dentro** l'accumulo —
    e il rilievo che ne usciva accusava l'accumulo di stare nella fascia
    sbagliata su una tavola in cui le tre fasce sono pulite (misurato sulla
    tavola di `docs/collaudi/DRAW-013/dopo`, guardandola). Un pezzo che non
    sceglie dove stare non puo' definire il confine di una fascia.

    *Fonte:* PO, 20 settembre 2026 (**D-154** punto 1), `regole-del-piano.md`
    §A1, che precisa **D-041**.
    """
    if not is_a_machine(definition):
        return None
    mestieri = frozenset(definition.functions)
    if mestieri & GENERATOR_FUNCTIONS:
        return GENERAZIONE
    if mestieri & (STORE_FUNCTIONS | EXCHANGE_FUNCTIONS):
        return ACCUMULI
    if component_id in utenze and BOUNDARY_FUNCTION not in mestieri:
        return DISTRIBUZIONE
    return None


def pezzi_fuori_fascia(
    drawing: DrawingGeometry, catalog: ComponentRegistry, project: ProjectModel
) -> list[ValidationIssue]:
    """**A1** — ogni pezzo sta nella fascia della propria categoria.

    *Fonte:* PO, 20 settembre 2026 (**D-154** punto 1), `regole-del-piano.md`
    §A1: «da sinistra a destra: generazione · accumuli e scambiatori ·
    distribuzione».

    **La misura.** Ogni fascia occupa l'intervallo orizzontale che va dal bordo
    sinistro del suo pezzo piu' a sinistra al bordo destro del suo pezzo piu' a
    destra. Le fasce non si devono **accavallare in orizzontale**: un pezzo che
    ricade dentro l'intervallo di una fascia che non e' la sua e' la violazione,
    e il rilievo nomina il pezzo, la sua fascia e la fascia in cui e' finito.

    **Nessuna soglia**, e quindi niente da tarare: la misura e' un confronto fra
    intervalli, e l'unica tolleranza e' quella dei numeri in virgola mobile.

    **Che cosa questa misura non vede, e va saputo:** tre fasce disgiunte ma in
    **ordine sbagliato** — generazione a destra della distribuzione senza che si
    tocchino — non danno nessun rilievo. L'ordine e' A3 in
    `regole-del-piano.md`, ed e' una riga `da scrivere` che non e' di questo
    pacchetto.
    """
    definizioni = _definizioni(project, catalog)
    utenze = user_machines(project, catalog)
    trovati: list[ValidationIssue] = []
    for sheet in drawing.sheets:
        fascia_di: dict[str, str] = {}
        for symbol in sheet.symbols:
            definition = definizioni.get(symbol.component_id)
            if definition is None:
                continue
            fascia = fascia_del_pezzo(definition, utenze, symbol.component_id)
            if fascia is not None:
                fascia_di[symbol.component_id] = fascia
        intervalli: dict[str, tuple[float, float]] = {}
        for symbol in sheet.symbols:
            fascia = fascia_di.get(symbol.component_id)
            if fascia is None:
                continue
            sinistra, destra = _scatola(symbol)
            presente = intervalli.get(fascia)
            intervalli[fascia] = (
                (sinistra, destra)
                if presente is None
                else (min(presente[0], sinistra), max(presente[1], destra))
            )
        for symbol in sorted(sheet.symbols, key=lambda item: item.component_id):
            mia = fascia_di.get(symbol.component_id)
            if mia is None:
                continue
            sinistra, destra = _scatola(symbol)
            for altra in FASCE:
                if altra == mia or altra not in intervalli:
                    continue
                inizio, fine = intervalli[altra]
                if destra <= inizio + TOLLERANZA_MM or sinistra >= fine - TOLLERANZA_MM:
                    continue
                trovati.append(
                    _rilievo(
                        "PIECE_OUTSIDE_ITS_BAND",
                        f"la tavola {sheet.sheet_id}: il pezzo {symbol.component_id} e' "
                        f"della fascia «{mia}» e sta fra x={sinistra:.1f} e x={destra:.1f}, "
                        f"cioe' dentro la fascia «{altra}», che va da x={inizio:.1f} a "
                        f"x={fine:.1f}. Le tre fasce verticali — generazione, accumuli e "
                        f"scambiatori, distribuzione — non si accavallano (A1, D-154)",
                        [sheet.sheet_id, symbol.component_id],
                    )
                )
    return trovati


# --- A4 — un organo di servizio sta addosso al pezzo che serve ----------------


def _organi_di_servizio(
    project: ProjectModel, catalog: ComponentRegistry
) -> list[tuple[str, str, Trunk]]:
    """Ogni **organo di servizio**, il pezzo che serve, e la tratta che lo porta.

    **La definizione non si inventa** (D-069, D-093): si legge da cio' che il
    catalogo e `layout/flow.py` gia' dichiarano, e sono due letture sole.

    - **chi pende da uno stacco**, che e' `place.hanging_children`: chi sta
      all'altro capo di un attacco che il catalogo mette **fuori dal percorso
      del fluido** (`PortDefinition.off_the_run`, D-101) e che non ha nessun
      altro attacco sul percorso. Sono gli scarichi, gli sfiati, i vasi, i
      manometri, le valvole di sicurezza e i gruppi di riempimento che **D-145**
      nomina uno per uno. Il criterio e' **lo stesso con cui il motore li
      posa**, e sta li' e non qui apposta: due letture separate darebbero prima
      o poi due elenchi diversi sullo stesso impianto.
    - **i confini di rete**, per mestiere: `flow.BOUNDARY_FUNCTION` dichiara
      gia' che quel pezzo «non ha una posizione propria» e «va accanto
      all'utente che serve» (**I-061**, `DRAW-009` §A.2). Vanno nominati a parte
      perche' la posa ne tiene dentro **solo gli ingressi**: un **prelievo** —
      l'acqua calda che se ne va verso le utenze — per il motore «e' l'ultimo
      passo della lettura e sta in fondo, come ogni utilizzatore»
      (`place._hanging_accessories`), quindi non pende da niente e **nessuno gli
      misura lo stacco**. E' esattamente il pezzo che sulle cinque tavole di
      `DRAW-015` finiva lontanissimo dall'accumulo che serve.

    La tratta che porta l'organo e' quella che ce l'ha a un capo, e ce n'e' una
    sola: un organo di servizio ha tutti gli attacchi su stacchi altrui, e un
    confine con un attacco solo ha una tratta sola per definizione.
    """
    trunks = tratte_del_progetto(project, catalog)
    appesi: dict[str, str] = {}
    for partizione in partition_project(project, trunks):
        for padre, figli in hanging_children(
            project, partizione, catalog, frozenset(partizione.component_ids)
        ).items():
            for figlio, _attacco in figli:
                appesi[figlio] = padre
    definizioni = _definizioni(project, catalog)
    trovati: list[tuple[str, str, Trunk]] = []
    for trunk in trunks:
        for mio, altro in ((trunk.start, trunk.end), (trunk.end, trunk.start)):
            definition = definizioni.get(mio.component_id)
            if definition is None:
                continue
            pende_di_qui = appesi.get(mio.component_id) == altro.component_id
            confine_non_appeso = (
                BOUNDARY_FUNCTION in definition.functions
                and mio.component_id not in appesi
            )
            if pende_di_qui or confine_non_appeso:
                trovati.append((mio.component_id, altro.component_id, trunk))
    return sorted(trovati, key=lambda item: item[0])


def _minimo_dello_stacco(
    project: ProjectModel,
    catalog: ComponentRegistry,
    trunk: Trunk,
    orizzontale: bool,
    passo_mm: float,
) -> float:
    """Quanto corto puo' essere questo stacco, secondo il motore.

    **Non e' una taratura di questo modulo e non e' una soglia**: sono tre
    misure del motore, ciascuna con la propria fonte, prese come il ciclo le
    prendeva finche' misurava il vincolo di **D-145**
    (`layout/improve.py::_hang_ceiling`).

    1. **`place.stub_minimum_mm`** — il minimo su griglia con cui la posa siede
       un appeso (**I-046**): due passi su uno stacco vuoto, una cella
       riservata davanti a ciascuno dei due attacchi (D-113); e, dove la tratta
       porta accessori in linea, quanto la **catena della macchina** pretende
       dalle due soglie (**I-044**, `chains.chain_room_mm`);
    2. **`place.inline_room_mm`** — il rettilineo che quegli stessi accessori
       pretenderanno **dopo l'instradamento**: l'interruzione di ciascuno piu'
       lo stacco dal vicino (`inline.py`). Su una tratta piu' corta il motore
       non riesce a sedercoli, e allungarla e' fattibilita', non estetica;
    3. **`place.ROW_GAP_MM`** — la distanza minima fra due simboli qualunque
       sul foglio (**D-062**): quattro passi, cioe' **tre corsie libere**, «e
       con cinque millimetri ne restava una sola». Uno stacco piu' corto
       metterebbe due simboli piu' vicini di quanto la posa li metta in
       qualunque altro punto della tavola.

    ⛔ **La lettura stretta — il solo punto 1 — l'ho scritta e misurata, e non
    regge**: sulle cinque tavole consegnate accendeva il rilievo 9, 10, 8, 7 e
    14 volte, e un terzo erano **due millimetri e mezzo**, cioe' un passo di
    griglia su uno stacco gia' addosso al proprio pezzo. Un rilievo che si
    accende su un termometro attaccato al proprio T non dice piu' niente su un
    prelievo che sta cinquecento millimetri piu' in la'. **La correzione non e'
    una soglia**: il minimo del motore non e' mai stato il solo punto 1.
    """
    return max(
        stub_minimum_mm(project, catalog, trunk, orizzontale, passo_mm),
        ceil(
            max(ROW_GAP_MM, inline_room_mm(project, catalog, trunk.inline_component_ids))
            / passo_mm
            - TOLLERANZA_MM
        )
        * passo_mm,
    )


def _verso_il_pezzo_che_serve(
    mio: Point, suo: Point, passo_mm: float
) -> tuple[float, float]:
    """Un passo di griglia **verso** il pezzo che l'organo serve.

    Lungo l'asse su cui lo stacco corre davvero: se il suo scarto maggiore e'
    in orizzontale lo stacco e' orizzontale, e viceversa. E' la stessa lettura
    di `tests/layout/test_stacchi_minimi_e_interasse.py`, che la fa sui
    riquadri; qui si fa sulle **porte**, che e' dove lo stacco comincia e
    finisce davvero.
    """
    dx, dy = suo.x_mm - mio.x_mm, suo.y_mm - mio.y_mm
    if abs(dx) >= abs(dy):
        return (passo_mm if dx >= 0 else -passo_mm, 0.0)
    return (0.0, passo_mm if dy >= 0 else -passo_mm)


def _il_posto_e_preso(
    posato: PlacedSymbol,
    verso: tuple[float, float],
    altri: Iterable[PlacedSymbol],
    corridoi: Iterable[tuple[float, float, float, float]],
    esclusi: frozenset[str],
    passo_mm: float,
) -> bool:
    """Vero se, **un passo piu' vicino**, l'organo non ci starebbe.

    E' il «**vincolo dichiarato**» di **D-145** punto 1 letto sulla tavola: uno
    stacco piu' lungo del minimo non e' una violazione se il posto al minimo e'
    **occupato**. Due modi di essere occupato, e sono quelli che il motore gia'
    conosce:

    - il riquadro dell'organo **toccherebbe un altro simbolo**, entro un passo
      di griglia — la distanza sotto la quale la posa non mette mai due pezzi;
    - il riquadro entrerebbe in un **corridoio di porta**
      (`place.port_corridors`): il rettilineo che la catena della macchina
      pretende davanti a un attacco (**I-044**), dove l'instradatore fara'
      uscire la tratta dritta e dove un simbolo la murerebbe.

    **Non e' una lettura nuova**: e' quella che
    `tests/layout/test_stacchi_minimi_e_interasse.py::_taken_one_step_closer`
    fa gia' sulla posa del motore, parola per parola — «un passo piu' vicino al
    raccordo il posto e' preso: lo stacco e' lungo per necessita', non per una
    costante». Sta qui perche' da **D-151** la posa non decide piu', e quella
    prova misura una tavola che il piano non compone piu'.
    """
    sinistra = posato.origin.x_mm + verso[0]
    alto = posato.origin.y_mm + verso[1]
    destra, basso = sinistra + posato.width_mm, alto + posato.height_mm
    if any(
        sinistra < x1 - TOLLERANZA_MM
        and x0 < destra - TOLLERANZA_MM
        and alto < y1 - TOLLERANZA_MM
        and y0 < basso - TOLLERANZA_MM
        for x0, y0, x1, y1 in corridoi
    ):
        return True
    return any(
        altro.component_id not in esclusi
        and sinistra < altro.right_mm + passo_mm
        and altro.origin.x_mm - passo_mm < destra
        and alto < altro.bottom_mm + passo_mm
        and altro.origin.y_mm - passo_mm < basso
        for altro in altri
    )


def _lunghezza_della_tratta(route: RoutedTrunk) -> float:
    """Quanto e' lunga la tratta sul foglio, **interruzioni comprese**.

    Si sommano i pezzi di spezzata **e** i salti sotto gli accessori in linea:
    sotto quel simbolo la tubazione c'e' lo stesso (D-027), e il minimo con cui
    questa lunghezza si confronta conta gli stessi accessori. Sommare il solo
    inchiostro darebbe uno stacco piu' corto del vero di tutta la fila, e un
    organo lontano passerebbe per vicino.
    """
    punti = [punto for segmento in route.segments for punto in segmento]
    return sum(
        abs(poi.x_mm - prima.x_mm) + abs(poi.y_mm - prima.y_mm)
        for prima, poi in zip(punti, punti[1:], strict=False)
    )


def organi_di_servizio_lontani(
    drawing: DrawingGeometry,
    frame: SheetFrame,
    catalog: ComponentRegistry,
    project: ProjectModel,
) -> list[ValidationIssue]:
    """**A4** — un organo di servizio sta addosso al pezzo che serve.

    *Fonte:* **D-145** (PO, I-076), `regole-del-piano.md` §A4: «valvole di
    intercettazione e di sicurezza, scarichi, sfiati, manometri, vasi, gruppi di
    riempimento, filtri e **confini di rete** si posano **addosso al pezzo che
    servono**: lo stacco che li porta e' **il proprio minimo su griglia**, e puo'
    allungarsi solo per un vincolo dichiarato». Per i confini di rete la fonte e'
    **I-061**, che `flow.BOUNDARY_FUNCTION` gia' cita: un confine «non ha una
    posizione propria e va accanto all'utente che serve». La ragione e' la
    **leggibilita'**: «una valvola in mezzo a una linea, lontana da tutto, e'
    equivoca».

    ⛔ **Perche' questo controllo esiste, ed e' il punto.** D-145 era un
    **vincolo della posa del motore**, e la posa dal **D-151** non decide piu'
    dove stanno i pezzi: il piano scrive le coordinate e le sovrascrive. Il
    vincolo non gira piu' su niente, e fino a qui **nessun rilievo lo misurava
    sulla tavola finita** — il piano poteva romperlo in silenzio, e l'ha rotto.

    **La misura.** Per ogni organo di servizio, la **lunghezza della tratta che
    lo porta** — la spezzata come il foglio la disegna, interruzioni comprese —
    contro **il suo minimo su griglia**. La violazione e' la tratta piu' lunga
    del proprio minimo, e il rilievo dice tutti e due i numeri.

    **Il minimo non e' una taratura di questo modulo, ed e' del motore**:
    `_minimo_dello_stacco` lo legge da `place.py`, dove la posa lo calcola, e il
    suo docstring dice da quale delle tre voci viene ogni millimetro.

    **I «vincoli dichiarati» di D-145 punto 1 sono due, e nessuno dei due e' un
    caso a parte scritto qui.** Il PO dice: «puo' allungarsi solo per un vincolo
    dichiarato — **per esempio** far posto a un altro accessorio in linea sulla
    stessa tratta». «Per esempio», non «soltanto»:

    1. **gli accessori sulla derivazione** stanno **dentro il minimo**
       (**I-044**): un organo lontano perche' sulla sua tratta c'e' una valvola
       ha un minimo piu' grande, e il controllo tace da solo;
    2. **il posto al minimo e' occupato** (`_il_posto_e_preso`): un passo piu'
       vicino, l'organo toccherebbe un altro simbolo o entrerebbe nel corridoio
       che una porta pretende. E' la stessa lettura che la posa difende in
       `tests/layout/test_stacchi_minimi_e_interasse.py`, portata sulla tavola.

    Se e' lontano e basta, il rilievo si accende.

    **Che cosa questa misura non vede, e va saputo.**

    - **Gli organi che stanno *sulla* linea** — la valvola di intercettazione e
      il filtro della catena della macchina — che D-145 nomina insieme agli
      altri: quelli non hanno uno stacco proprio, stanno **dentro** una tratta,
      e la loro vicinanza e' un contratto a parte (**I-044**, D-120), difeso da
      `tests/layout/test_vicinanza_valvole.py`. Qui si misura **lo stacco**, e
      un pezzo senza stacco non ha niente da misurare.
    - **Dove lo stacco punta**: uno stacco del proprio minimo esatto che parte
      dalla faccia sbagliata resta del proprio minimo, e passa. La regola dice
      «addosso», e addosso e' una distanza.
    - **Le tratte cedute** (`unresolved`, D-150): la loro spezzata e' un ripiego
      dichiarato, non una posa, e misurarla accuserebbe il piano di una cosa che
      il preflight nomina gia' come bloccante.
    - **Una tratta che il foglio non porta**: una catena spezzata fra due tavole
      non ha una lunghezza da leggere qui.
    - **Perche' il posto al minimo sia occupato**: il controllo vede che lo e',
      non **chi** l'ha occupato ne' se quel vicino potesse stare altrove. Un
      corredo composto stretto intorno a un raccordo passa; lo stesso corredo
      con un pezzo di troppo nel mezzo passa anche lui, e quello lo dice A2.
    """
    passo_mm = frame.standard.grid_mm
    trunks = tratte_del_progetto(project, catalog)
    organi = _organi_di_servizio(project, catalog)
    trovati: list[ValidationIssue] = []
    for sheet in drawing.sheets:
        porte = porte_in_tavola(sheet, project, catalog)
        posati = {item.component_id: item for item in sheet.symbols}
        corridoi = port_corridors(
            project, catalog, trunks, list(sheet.symbols), passo_mm
        )
        per_chiave = {tuple(route.connection_ids): route for route in sheet.routes}
        for organo, servito, trunk in organi:
            route = per_chiave.get(trunk.connection_ids)
            if route is None or route.unresolved:
                continue
            dritto = trunk.start.component_id == organo
            mio = trunk.start if dritto else trunk.end
            suo = trunk.end if dritto else trunk.start
            dove = porte.get((mio.component_id, mio.port_id))
            if dove is None:
                continue
            lungo_mm = _lunghezza_della_tratta(route)
            minimo_mm = _minimo_dello_stacco(
                project,
                catalog,
                trunk,
                dove[1] in (PortFace.LEFT, PortFace.RIGHT),
                passo_mm,
            )
            if lungo_mm <= minimo_mm + TOLLERANZA_MM:
                continue
            posato = posati.get(organo)
            altro = porte.get((servito, suo.port_id))
            if posato is not None and altro is not None and _il_posto_e_preso(
                posato,
                _verso_il_pezzo_che_serve(dove[0], altro[0], passo_mm),
                sheet.symbols,
                corridoi,
                frozenset({organo, servito}),
                passo_mm,
            ):
                continue
            perche = (
                f", che e' quanto pretendono gli accessori in linea "
                f"({', '.join(trunk.inline_component_ids)})"
                if trunk.inline_component_ids
                else ""
            )
            trovati.append(
                _rilievo(
                    "SERVICE_STUB_LONGER_THAN_ITS_MINIMUM",
                    f"la tavola {sheet.sheet_id}: lo stacco che porta {organo} da "
                    f"{servito} e' lungo {lungo_mm:.1f} mm e il suo minimo su griglia "
                    f"e' {minimo_mm:.1f}{perche}, cioe' {lungo_mm - minimo_mm:.1f} mm "
                    f"di tubo in piu': un organo di servizio sta addosso al pezzo che "
                    f"serve (A4, D-145)",
                    [sheet.sheet_id, organo, servito],
                )
            )
    return trovati

# --- B1 — prima le autostrade, e il piu' dritte possibile ----------------------


def autostrade_storte(
    drawing: DrawingGeometry, catalog: ComponentRegistry, project: ProjectModel
) -> list[ValidationIssue]:
    """**B1** — l'autostrada e' dritta, e le sue pieghe si contano sulla catena.

    *Fonte:* PO, 20 settembre 2026 (**D-154** punto 2), `regole-del-piano.md`
    §B1; il precedente e' del 19 (**D-151**): «abbiamo ottimizzato le curve e
    gli attraversamenti sugli attacchetti e abbiamo fatto sta curva senza
    senso».

    **La misura.** Per ogni autostrada in tavola si contano le pieghe della
    **catena intera** — quelle dentro ciascuna tratta e quelle **sui crocevia**
    che le uniscono — e si confrontano con `curve_ammesse`, cioe'
    `Highway.turns_allowed`: **zero** per la struttura fra le macchine di spina,
    **una** per la strada verso i terminali (**D-144**).

    **La soglia non sta qui e non e' tarata**: e' `Highway.turns_allowed`, e la
    sua fonte e' D-144 per la curva della distribuzione e `DRAW-012` §C per la
    retta della struttura (D-083).

    Il rilievo nomina **le tratte**, perche' e' li' che chi guarda la tavola
    mette il dito — «la tratta `s3` piega quattro volte, e su un'autostrada le
    pieghe ammesse sono zero» — e nomina la catena, perche' la piega puo' stare
    sul crocevia e non dentro nessuna delle due tratte che lo toccano.
    """
    autostrade = autostrade_del_progetto(project, catalog)
    trovati: list[ValidationIssue] = []
    for sheet in drawing.sheets:
        porte = porte_in_tavola(sheet, project, catalog)
        for autostrada in autostrade:
            pieghe = pieghe_dell_autostrada(autostrada, sheet.routes, porte)
            if pieghe is None or pieghe <= autostrada.curve_ammesse:
                continue
            trovati.append(
                _rilievo(
                    "HIGHWAY_IS_NOT_STRAIGHT",
                    f"la tavola {sheet.sheet_id}: {_tratte_nominate(autostrada)} "
                    f"{'piega' if autostrada.e_una_tratta_sola else 'piegano'} "
                    f"{pieghe} {'volta' if pieghe == 1 else 'volte'}, e su "
                    f"un'autostrada le pieghe ammesse sono "
                    f"{autostrada.curve_ammesse} — la catena e' {autostrada.nome} "
                    f"(B1, D-154)",
                    [sheet.sheet_id, *sorted(autostrada.connection_ids)],
                )
            )
    return trovati


def _tratte_nominate(autostrada: AutostradaInTavola) -> str:
    """Come si nominano le tratte di una catena in un rilievo."""
    nomi = [", ".join(chiave) for chiave in autostrada.catene]
    if len(nomi) == 1:
        return f"la tratta {nomi[0]}"
    return "le tratte " + " + ".join(nomi)


# --- B3 — piu' generatori o piu' terminali ⇒ collettore verticale --------------


def _macchine_in_parallelo(
    project: ProjectModel, catalog: ComponentRegistry
) -> dict[str, frozenset[str]]:
    """I due gruppi di macchine che il PO nomina: i generatori e i terminali.

    Nessun nome e nessun conteggio di posizione: il mestiere di catalogo per i
    generatori (`GENERATOR_FUNCTIONS`, la stessa lettura della gerarchia) e
    `hierarchy.user_machines` per i terminali e le utenze.
    """
    definizioni = _definizioni(project, catalog)
    generatori = frozenset(
        key
        for key, value in definizioni.items()
        if is_a_machine(value) and frozenset(value.functions) & GENERATOR_FUNCTIONS
    )
    return {"generatori": generatori, "terminali": user_machines(project, catalog)}


def _e_un_nodo_di_collettore(definition: ComponentDefinition) -> bool:
    return (
        definition.is_a_fitting
        and len(_attacchi_di_percorso(definition))
        >= ATTACCHI_DI_UN_NODO_DI_COLLETTORE_MIN
    )


def _tratte_per_attacco(
    trunks: Iterable[Trunk],
) -> dict[tuple[str, str], list[Trunk]]:
    per_attacco: dict[tuple[str, str], list[Trunk]] = {}
    for trunk in trunks:
        for ref in (trunk.start, trunk.end):
            per_attacco.setdefault((ref.component_id, ref.port_id), []).append(trunk)
    return per_attacco


def _cammina_fino_a_un_nodo(
    partenza: tuple[str, str],
    definizioni: dict[str, ComponentDefinition],
    per_attacco: dict[tuple[str, str], list[Trunk]],
) -> list[tuple[str, tuple[tuple[str, ...], ...]]]:
    """I nodi di collettore che si raggiungono da un attacco, e per quali tratte.

    Si cammina **per attacchi**, come fa `hierarchy.machines_beyond_of`: si
    attraversano solo i raccordi di passaggio — quelli che il catalogo dichiara
    con due soli attacchi sul percorso — e ci si ferma sul primo raccordo che
    **unisce** o sulla prima macchina. Un accessorio in linea non e' un
    ostacolo: sta **dentro** una tratta, e le tratte sono gia' ricomposte.
    """
    trovati: list[tuple[str, tuple[tuple[str, ...], ...]]] = []
    frontiera: list[tuple[tuple[str, str], tuple[tuple[str, ...], ...]]] = [
        (partenza, ())
    ]
    visti: set[tuple[str, str]] = {partenza}
    while frontiera:
        avanti: list[tuple[tuple[str, str], tuple[tuple[str, ...], ...]]] = []
        for attacco, percorse in frontiera:
            for trunk in per_attacco.get(attacco, ()):
                if trunk.connection_ids in percorse:
                    continue
                lontano = (
                    trunk.end
                    if (trunk.start.component_id, trunk.start.port_id) == attacco
                    else trunk.start
                )
                chiave = (lontano.component_id, lontano.port_id)
                if chiave in visti:
                    continue
                visti.add(chiave)
                fatte = (*percorse, trunk.connection_ids)
                definition = definizioni.get(lontano.component_id)
                if definition is None:
                    continue
                if _e_un_nodo_di_collettore(definition):
                    trovati.append((lontano.component_id, fatte))
                    continue
                for oltre in sorted(ports_through(definition, lontano.port_id)):
                    avanti.append(((lontano.component_id, oltre), fatte))
        frontiera = avanti
    return trovati


def _e_verticale(route: RoutedTrunk) -> bool:
    """Vero se ogni tratto della spezzata corre in verticale."""
    for segmento in route.segments:
        for prima, poi in zip(segmento, segmento[1:], strict=False):
            if abs(poi.x_mm - prima.x_mm) > TOLLERANZA_MM:
                return False
    return True


def macchine_in_parallelo_senza_collettore(
    drawing: DrawingGeometry,
    frame: SheetFrame,
    catalog: ComponentRegistry,
    project: ProjectModel,
) -> list[ValidationIssue]:
    """**B3** — le macchine in parallelo si attaccano a una catena di T verticale.

    *Fonte:* PO, 20 settembre 2026 (**D-154** punto 4), `regole-del-piano.md`
    §B3: «se ho piu' generatori o piu' terminali si fa un collettore
    verticale»; le macchine in parallelo si attaccano a una **catena di T
    verticale e allineata**, con uno stacco corto ciascuna, invece di tirare
    ognuna la propria tratta verso la destinazione.

    **La misura, in tre passi.**

    1. **I gruppi in parallelo**: i generatori e i terminali, letti dal mestiere
       di catalogo e da `hierarchy.user_machines`, mai da un nome.
    2. **Il collettore**: camminando da ciascuna macchina lungo le tratte e
       attraversando i raccordi di **passaggio**, il primo raccordo che
       **unisce** — tre attacchi sul percorso — e' un nodo di collettore. Due
       nodi che si raggiungono fra loro nello stesso modo sono lo stesso
       collettore. E' cosi' che il T di servizio del manometro resta fuori: ha
       due attacchi sul percorso e la linea gli passa attraverso.
    3. **La verifica**, solo dove il collettore serve **due o piu'** macchine
       dello stesso gruppo: i suoi nodi stanno tutti sulla stessa verticale, e
       le tratte che li uniscono sono verticali.

    La **tolleranza di allineamento** e' mezzo passo di griglia: su una griglia
    ortogonale due nodi o stanno sulla stessa colonna o distano almeno un passo
    intero, e mezzo passo e' il separatore che non ammette dubbi. **Non e' una
    taratura** — discende dal passo del foglio (D-083).

    **Che cosa questa misura non vede, e va saputo.** Due macchine in parallelo
    che si attaccano a **un raccordo solo** per lato — il caso ordinario con due
    generatori — danno un collettore di un nodo, e un nodo e' allineato per
    costruzione: la regola morde da **tre** macchine in su, dove la catena di T
    esiste davvero. E non si misura **se un collettore ci sia**: per dire «qui
    un collettore manca» servirebbe sapere quale lato del circuito un raccordo
    serve, e la mandata e il ritorno oggi sono due collettori distinti che
    servono le stesse macchine. Resta lavoro aperto, e va in
    `regole-del-piano.md` come tale.
    """
    definizioni = _definizioni(project, catalog)
    trunks = tratte_del_progetto(project, catalog)
    per_attacco = _tratte_per_attacco(trunks)
    gruppi = _macchine_in_parallelo(project, catalog)
    tolleranza_mm = frame.standard.grid_mm / 2

    # Chi serve ogni nodo, e con quali tratte lo raggiunge.
    serve: dict[str, set[str]] = {}
    for gruppo in gruppi.values():
        for macchina in sorted(gruppo):
            definition = definizioni.get(macchina)
            if definition is None:
                continue
            for porta in _attacchi_di_percorso(definition):
                for nodo, _ in _cammina_fino_a_un_nodo(
                    (macchina, porta), definizioni, per_attacco
                ):
                    serve.setdefault(nodo, set()).add(macchina)

    # I nodi che si raggiungono fra loro sono lo stesso collettore.
    vicini: dict[str, set[str]] = {nodo: set() for nodo in serve}
    fra_nodi: dict[tuple[str, str], tuple[tuple[str, ...], ...]] = {}
    for nodo in serve:
        for porta in _attacchi_di_percorso(definizioni[nodo]):
            for altro, percorse in _cammina_fino_a_un_nodo(
                (nodo, porta), definizioni, per_attacco
            ):
                if altro == nodo or altro not in serve:
                    continue
                vicini[nodo].add(altro)
                vicini.setdefault(altro, set()).add(nodo)
                coppia = (nodo, altro) if nodo < altro else (altro, nodo)
                fra_nodi.setdefault(coppia, percorse)

    collettori: list[list[str]] = []
    rimasti = set(serve)
    while rimasti:
        radice = min(rimasti)
        gruppo_nodi: list[str] = []
        frontiera = [radice]
        rimasti.discard(radice)
        while frontiera:
            nodo = frontiera.pop()
            gruppo_nodi.append(nodo)
            for altro in sorted(vicini.get(nodo, ())):
                if altro in rimasti:
                    rimasti.discard(altro)
                    frontiera.append(altro)
        collettori.append(sorted(gruppo_nodi))

    trovati: list[ValidationIssue] = []
    for sheet in drawing.sheets:
        posati = {item.component_id: item for item in sheet.symbols}
        per_chiave = {tuple(route.connection_ids): route for route in sheet.routes}
        for nodi in collettori:
            for nome_gruppo, gruppo in gruppi.items():
                macchine = sorted(
                    {
                        macchina
                        for nodo in nodi
                        for macchina in serve[nodo]
                        if macchina in gruppo
                    }
                )
                if len(macchine) < 2:
                    continue
                presenti = [nodo for nodo in nodi if nodo in posati]
                if not presenti:
                    continue
                ascisse = {nodo: _centro_x(posati[nodo]) for nodo in presenti}
                scarto = max(ascisse.values()) - min(ascisse.values())
                storte = sorted(
                    chiave
                    for coppia, percorse in fra_nodi.items()
                    if coppia[0] in ascisse and coppia[1] in ascisse
                    for chiave in percorse
                    if chiave in per_chiave and not _e_verticale(per_chiave[chiave])
                )
                if scarto <= tolleranza_mm and not storte:
                    continue
                dove = ", ".join(
                    f"{nodo} a x={ascisse[nodo]:.1f}" for nodo in sorted(ascisse)
                )
                motivo = (
                    f"non stanno sulla stessa verticale (scarto {scarto:.1f} mm, "
                    f"tolleranza {tolleranza_mm:.1f} mm)"
                    if scarto > tolleranza_mm
                    else "sono allineati, ma le tratte fra loro non sono verticali"
                )
                coda = (
                    f"; e le tratte {', '.join(', '.join(item) for item in storte)} "
                    f"non corrono in verticale"
                    if storte and scarto > tolleranza_mm
                    else ""
                )
                trovati.append(
                    _rilievo(
                        "PARALLEL_MACHINES_WITHOUT_A_COLLECTOR",
                        f"la tavola {sheet.sheet_id}: {len(macchine)} {nome_gruppo} in "
                        f"parallelo ({', '.join(macchine)}) si attaccano ai raccordi "
                        f"{dove}, che {motivo}{coda}. Piu' generatori o piu' terminali "
                        f"vogliono una catena di T verticale e allineata (B3, D-154)",
                        [sheet.sheet_id, *sorted(ascisse), *macchine],
                    )
                )
    return trovati


# --- B4 — un organo in linea non spezza il tratto ------------------------------


def _coppia_in_linea(
    symbol: PlacedSymbol,
    definition: ComponentDefinition,
    porte: PorteInTavola,
) -> tuple[str, str] | None:
    """Le due porte del pezzo che stanno su **facce opposte**, se ce ne sono.

    Si guardano le facce del **manifesto ruotato**, che e' come il pezzo sta
    davvero sulla tavola, e solo gli attacchi che il catalogo mette sul
    percorso. Piu' di una coppia non puo' esistere entro
    `ATTACCHI_DI_UN_ORGANO_IN_LINEA_MAX`: con tre attacchi il terzo sta per
    forza su una faccia perpendicolare, ed e' il «terzo attacco di lato» che
    **D-154** nomina.
    """
    attacchi = _attacchi_di_percorso(definition)
    if len(attacchi) > ATTACCHI_DI_UN_ORGANO_IN_LINEA_MAX:
        return None
    facce: dict[str, PortFace] = {}
    for porta in attacchi:
        dove = porte.get((symbol.component_id, porta))
        if dove is not None:
            facce[porta] = dove[1]
    for indice, prima in enumerate(attacchi):
        for poi in attacchi[indice + 1 :]:
            if prima in facce and poi in facce and facce[prima] is facce[poi].opposite:
                return (prima, poi)
    return None


def _tratto_alla_porta(
    dove: Point, routes: Iterable[RoutedTrunk]
) -> tuple[RoutedTrunk, Point, Point] | None:
    """Il tratto di spezzata che si attacca a questa porta.

    Solo i **capi** di un pezzo di spezzata contano: una linea che passa per il
    punto senza fermarcisi non e' attaccata alla porta, e' una linea che ci
    passa sopra — e quella la nomina gia' il preflight.
    """
    for route in routes:
        for segmento in route.segments:
            if len(segmento) < 2:
                continue
            for qui, la in ((segmento[0], segmento[1]), (segmento[-1], segmento[-2])):
                if (
                    abs(qui.x_mm - dove.x_mm) <= TOLLERANZA_MM
                    and abs(qui.y_mm - dove.y_mm) <= TOLLERANZA_MM
                ):
                    return (route, qui, la)
    return None


def _giacitura_del_tratto(qui: Point, la: Point) -> tuple[str, float] | None:
    if abs(qui.y_mm - la.y_mm) <= TOLLERANZA_MM:
        return ("orizzontale", qui.y_mm)
    if abs(qui.x_mm - la.x_mm) <= TOLLERANZA_MM:
        return ("verticale", qui.x_mm)
    return None


def organi_che_spezzano_il_tratto(
    drawing: DrawingGeometry, catalog: ComponentRegistry, project: ProjectModel
) -> list[ValidationIssue]:
    """**B4** — un organo in linea non spezza il tratto: la linea passa.

    *Fonte:* PO, 20 settembre 2026 (**D-154** punto 3), `regole-del-piano.md`
    §B4: «una valvola a tre vie si posa con ingresso e uscita allineati; il
    terzo attacco esce di lato. Vale per ogni organo che sta *sulla* linea: la
    linea passa, non si piega intorno a lui».

    **Il soggetto** si riconosce dal catalogo, non da un elenco di pezzi: un
    pezzo che **non e' un raccordo**, con al piu'
    `ATTACCHI_DI_UN_ORGANO_IN_LINEA_MAX` attacchi sul percorso, che ne ha due su
    **facce opposte** del manifesto **ruotato** e li usa tutti e due.

    **La violazione** e' che le due tratte attaccate a quelle due porte non
    stanno sulla stessa retta **al pezzo**: il tratto che esce da una e quello
    che esce dall'altra non hanno la stessa giacitura — stesso asse e stessa
    quota. Il rilievo dice il pezzo, le due porte, la loro quota e dove va
    invece ciascuna tratta.

    **Nessuna soglia**, e quindi niente da tarare: e' un confronto fra due
    giaciture, con la sola tolleranza dei numeri in virgola mobile.

    **Che cosa questa misura non vede:** una piega **lontana** dall'organo. La
    regola dice «al pezzo», e questo controllo misura li'; una tratta che si
    piega dieci millimetri piu' in la' la conta **B1** se e' un'autostrada, e
    `RUN_WITH_TOO_MANY_BENDS` altrimenti.
    """
    definizioni = _definizioni(project, catalog)
    trovati: list[ValidationIssue] = []
    for sheet in drawing.sheets:
        porte = porte_in_tavola(sheet, project, catalog)
        for symbol in sorted(sheet.symbols, key=lambda item: item.component_id):
            definition = definizioni.get(symbol.component_id)
            if definition is None or definition.is_a_fitting:
                continue
            coppia = _coppia_in_linea(symbol, definition, porte)
            if coppia is None:
                continue
            misure = []
            for porta in coppia:
                dove = porte[(symbol.component_id, porta)]
                attaccata = _tratto_alla_porta(dove[0], sheet.routes)
                if attaccata is None:
                    break
                giacitura = _giacitura_del_tratto(attaccata[1], attaccata[2])
                if giacitura is None:
                    break
                misure.append((porta, dove[0], attaccata[0], giacitura))
            if len(misure) != 2 or misure[0][3] == misure[1][3]:
                continue
            quota = _quota_della_coppia(misure[0][1], misure[1][1])
            racconto = " e ".join(
                f"il tratto che esce da {porta} corre {giacitura[0]} a "
                f"{'y' if giacitura[0] == 'orizzontale' else 'x'}={giacitura[1]:.1f}"
                for porta, _, _, giacitura in misure
            )
            sopra = sorted(
                {
                    ", ".join(route.connection_ids) or route.network_id
                    for _, _, route, _ in misure
                }
            )
            trovati.append(
                _rilievo(
                    "INLINE_ORGAN_BREAKS_THE_RUN",
                    f"la tavola {sheet.sheet_id}: {symbol.component_id} ha {misure[0][0]} "
                    f"e {misure[1][0]} su facce opposte, {quota}, ma {racconto} "
                    f"(tratta {' e '.join(sopra)}): l'organo sta sulla piega e spezza "
                    f"il tratto, invece di lasciarlo passare (B4, D-154)",
                    [
                        sheet.sheet_id,
                        symbol.component_id,
                        *[
                            connection_id
                            for _, _, route, _ in misure
                            for connection_id in route.connection_ids
                        ],
                    ],
                )
            )
    return trovati


def _quota_della_coppia(prima: Point, poi: Point) -> str:
    """La quota su cui le due porte si guardano, detta come si legge sul foglio."""
    if abs(prima.y_mm - poi.y_mm) <= TOLLERANZA_MM:
        return f"alla stessa quota y={prima.y_mm:.1f}"
    if abs(prima.x_mm - poi.x_mm) <= TOLLERANZA_MM:
        return f"alla stessa quota x={prima.x_mm:.1f}"
    return f"a quote diverse (y={prima.y_mm:.1f} e y={poi.y_mm:.1f})"


CODICE_DELLA_REGOLA: dict[str, str] = {
    "A1": "PIECE_OUTSIDE_ITS_BAND",
    "A4": "SERVICE_STUB_LONGER_THAN_ITS_MINIMUM",
    "B1": "HIGHWAY_IS_NOT_STRAIGHT",
    "B3": "PARALLEL_MACHINES_WITHOUT_A_COLLECTOR",
    "B4": "INLINE_ORGAN_BREAKS_THE_RUN",
}
"""Il rilievo di ciascuna regola misurata, **e non c'e' un secondo posto**.

Chi conta le violazioni entra da qui. E' nato da un difetto: quando `A4` e'
entrata fra le regole, l'elenco dei codici che il **punteggio** del revisore
conta era una lista **scritta a mano** in `piano/revisore.py`, e per un giorno il
rilievo di A4 e' finito fra gli **avvisi** — cioe' la voce che una piega in meno
si compra. **Un controllo che non entra nel punteggio non e' un controllo.**
"""

ORDINE_DELLE_REGOLE: tuple[str, ...] = tuple(CODICE_DELLA_REGOLA)
"""L'ordine in cui i controlli girano, e quindi quello dell'esito.

**Prima dove stanno i pezzi, poi come corrono le linee**: e' l'ordine in cui il
PO le ha dettate e l'ordine in cui `regole-del-piano.md` le elenca, ed e' anche
l'ordine in cui si correggono — una linea storta puo' essere la conseguenza di
un pezzo nella fascia sbagliata, mai il contrario. **A4 sta fra le due perche'
dice dove sta un pezzo**, non come corre una linea: e' la lettera che
`regole-del-piano.md` le da', ed e' anche l'ordine giusto per correggere —
spostare un organo addosso al proprio pezzo cambia la tratta che lo porta, mai
il contrario.
"""


def rilievi_delle_regole(
    drawing: DrawingGeometry,
    frame: SheetFrame,
    catalog: ComponentRegistry,
    project: ProjectModel,
) -> list[ValidationIssue]:
    """Tutte le regole misurabili del piano, nell'ordine di `ORDINE_DELLE_REGOLE`.

    Sono le quattro di **D-154** piu' **A4**, che e' **D-145** e viene da prima:
    era un **vincolo della posa del motore**, e da **D-151** la posa non decide
    piu' dove stanno i pezzi — il piano lo sovrascrive. Un vincolo che nessuno
    misura sulla tavola finita e' un vincolo che il piano rompe in silenzio.

    Non e' il preflight e non lo sostituisce: il preflight dice se la tavola e'
    **consegnabile** (D-063), questo dice se il **piano** e' fatto secondo le
    regole del PO. I due elenchi si leggono insieme e non si sommano.
    """
    return [
        *pezzi_fuori_fascia(drawing, catalog, project),
        *organi_di_servizio_lontani(drawing, frame, catalog, project),
        *autostrade_storte(drawing, catalog, project),
        *macchine_in_parallelo_senza_collettore(drawing, frame, catalog, project),
        *organi_che_spezzano_il_tratto(drawing, catalog, project),
    ]


__all__ = [
    "ACCUMULI",
    "CODICE_DELLA_REGOLA",
    "DISTRIBUZIONE",
    "FASCE",
    "GENERAZIONE",
    "ORDINE_DELLE_REGOLE",
    "autostrade_storte",
    "fascia_del_pezzo",
    "macchine_in_parallelo_senza_collettore",
    "organi_che_spezzano_il_tratto",
    "organi_di_servizio_lontani",
    "pezzi_fuori_fascia",
    "rilievi_delle_regole",
]
