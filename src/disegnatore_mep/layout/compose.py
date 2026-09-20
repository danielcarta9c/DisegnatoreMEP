"""La catena completa, nell'ordine che la specifica §10.1 fissa.

    modello approvato
    -> validazione topologica          (validation/topology.py, fuori di qui)
    -> partizione funzionale in tavole
    -> assegnazione dei simboli
    -> layout per ciascuna tavola
    -> instradamento ortogonale
    -> accessori in linea sulla tratta
    -> testi e tag
    -> legenda e rimandi

La partizione precede il layout: tagliare un disegno gia' disposto spezzerebbe
circuiti in modo arbitrario (D-028).
"""

from collections.abc import Callable
from dataclasses import dataclass, field, replace

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import ORDINARY_FRAMES, Rect, SheetFrame
from disegnatore_mep.graphics.symbol import PortFace
from disegnatore_mep.model.order import structural_order
from disegnatore_mep.model.project import ProjectModel

from .chains import machine_chains
from .errors import LayoutError
from .geometry import (
    CrossReference,
    DrawingGeometry,
    PlacedSymbol,
    Point,
    RoutedTrunk,
    SheetGeometry,
)
from .grid import GridSpace
from .hierarchy import hierarchy_of
from .highways import highways, lies_in_line
from .inline import settle_sheet
from .labels import place_labels
from .legend import build_legend
from .partition import SheetLink, SheetPartition, partition_project
from .place import place_sheet
from .trunks import Trunk, build_trunks

CROSS_REFERENCE_GAP_MM = 2.5
"""Stacco fra la porta e il marcatore di rimando."""

TrunkKey = tuple[str, ...]

@dataclass
class ComposeNote:
    """Come e' uscita una tavola: con quale ripiego, e a che prezzo (§F.3).

    Esiste perche' il pacchetto lo chiede per iscritto: «la cessione e'
    **graduale e dichiarata**: si cede una piega per volta, sulla tratta che ne
    ha meno bisogno, e il rapporto dice dove e perche' per ciascun impianto che
    ha dovuto cedere», e «ogni volta che scatta [il ripiego che scarta le fasi]
    va scritto». Un ripiego silenzioso e' come la tavola 4 e' arrivata in
    revisione senza che nessuna misura se ne accorgesse.
    """

    sheet_id: str
    ripiego: str
    """Quale delle vie ha consegnato la tavola, in italiano e per esteso."""

    conceded: tuple[TrunkKey, ...] = ()
    """Le tratte delle catene a cui si e' concessa la piega, in ordine di resa."""

    crooked: tuple[TrunkKey, ...] = ()
    """Le catene che la tavola consegnata non ha dritte, cedute o no."""

    highways: int = 0
    """Quante autostrade intere ha questo foglio."""

    dilation: float = 1.0
    """Il fattore con cui il foglio e' stato allargato (**D-142**, §A).

    Uno vuol dire che la dilatazione non e' entrata in gioco: o il disegno non
    ci stava nemmeno cosi', o la griglia non ammetteva nessun altro fattore.
    Il rapporto di collaudo lo porta per ciascuna tavola, perche' il criterio 2
    chiede **con quale fattore** il riempimento e' entrato nella finestra."""


@dataclass
class ComposeJournal:
    """Il diario della composizione: una nota per foglio."""

    notes: list[ComposeNote] = field(default_factory=list)

    def clear(self) -> None:
        self.notes.clear()


def inline_component_ids(
    project: ProjectModel, catalog: ComponentRegistry
) -> frozenset[str]:
    """Chi spezza una linea lo dice la libreria, non un elenco nel motore."""
    return frozenset(
        item.id
        for item in project.components
        if catalog.resolve(item.definition_id).is_inline
    )


def _cross_references(
    partition: SheetPartition,
    placed_by_component: dict[str, PlacedSymbol],
    network_names: dict[str, str],
) -> list[CrossReference]:
    references: list[CrossReference] = []
    for link in partition.links:
        symbol = placed_by_component.get(link.port.component_id)
        if symbol is None:
            continue
        references.append(
            CrossReference(
                id=link.id,
                pair_id=link.pair_id,
                peer_sheet_id=link.peer_sheet_id,
                # Cio' che si legge e' in italiano (D-051): la sigla della
                # tavola di destinazione e il fluido che prosegue.
                text=f"→ {link.peer_sheet_id.upper()} · "
                f"{network_names.get(link.network_id, link.network_id)}",
                anchor=Point(
                    x_mm=symbol.right_mm + CROSS_REFERENCE_GAP_MM,
                    y_mm=symbol.origin.y_mm,
                ),
            )
        )
    return references


def _shifted(point: Point, delta_mm: float, across_mm: float = 0.0) -> Point:
    return Point(x_mm=point.x_mm + across_mm, y_mm=point.y_mm + delta_mm)


def centre_vertically(
    sheet: SheetGeometry, drawing: Rect, step_mm: float, text_mm: float = 0.0
) -> SheetGeometry:
    """Porta il blocco disegnato al centro dell'area di disegno.

    La composizione nasce appoggiata a una quota interna di posa, e un impianto
    basso lasciava vuoti i due terzi alti del foglio. Non si puo' rimediare
    ingrandendo i simboli — la scala di stampa e' invariante (ADR 0003) —
    quindi si sposta: il blocco resta quello che e' e si mette in mezzo.

    **Il blocco sono i simboli e le tubazioni, e nient'altro** (DRAW-003): la
    quota di terra non e' un elemento della tavola (D-121) e i testi si posano
    dopo, su una geometria gia' ferma. Se la centratura li contasse, la
    lunghezza di una sigla sposterebbe le macchine, e il contratto per cui le
    etichette non toccano posa e routing sarebbe falso. `text_mm` resta nella
    firma per chi la chiama ancora, e non e' usato.

    Lo spostamento e' un multiplo del passo, cosi' nulla esce dalla griglia.
    """
    del text_mm
    tops = [item.origin.y_mm for item in sheet.symbols]
    bottoms = [item.bottom_mm for item in sheet.symbols]
    for route in sheet.routes:
        for segment in route.segments:
            tops.extend(point.y_mm for point in segment)
            bottoms.extend(point.y_mm for point in segment)
    if not tops:
        return sheet

    top, bottom = min(tops), max(bottoms)
    wanted = drawing.y_mm + (drawing.height_mm - (bottom - top)) / 2
    delta = round((wanted - top) / step_mm) * step_mm
    delta = min(delta, drawing.bottom_mm - bottom)
    delta = max(delta, drawing.y_mm - top)
    delta = round(delta / step_mm) * step_mm

    # **E anche in orizzontale**, per la stessa ragione e con lo stesso limite.
    # L'ordine di processo va da sinistra a destra (D-060), ma non dice che il
    # disegno debba stare **appoggiato** al margine sinistro: appoggiato, un
    # impianto largo la meta' del foglio lasciava i due quadranti di destra
    # senza inchiostro, ed e' meta' dello squilibrio che la carta misura
    # (A1, A3). Spostare tutto in mezzo non cambia ne' l'ordine ne' una
    # distanza: cambia dove il blocco sta sulla carta.
    lefts = [item.origin.x_mm for item in sheet.symbols]
    rights = [item.right_mm for item in sheet.symbols]
    for route in sheet.routes:
        for segment in route.segments:
            lefts.extend(point.x_mm for point in segment)
            rights.extend(point.x_mm for point in segment)
    left, right = min(lefts), max(rights)
    wanted_x = drawing.x_mm + (drawing.width_mm - (right - left)) / 2
    across = round((wanted_x - left) / step_mm) * step_mm
    across = min(across, drawing.right_mm - right)
    across = max(across, drawing.x_mm - left)
    across = round(across / step_mm) * step_mm

    if delta == 0 and across == 0:
        return sheet

    return sheet.model_copy(
        update={
            "symbols": [
                item.model_copy(update={"origin": _shifted(item.origin, delta, across)})
                for item in sheet.symbols
            ],
            "routes": [
                item.model_copy(
                    update={
                        "segments": [
                            [_shifted(point, delta, across) for point in segment]
                            for segment in item.segments
                        ],
                        "crossings": [
                            _shifted(point, delta, across) for point in item.crossings
                        ],
                    }
                )
                for item in sheet.routes
            ],
            "labels": [
                item.model_copy(
                    update={
                        "anchor": _shifted(item.anchor, delta, across),
                        "leader_from": (
                            None
                            if item.leader_from is None
                            else _shifted(item.leader_from, delta, across)
                        ),
                    }
                )
                for item in sheet.labels
            ],
            "cross_references": [
                item.model_copy(update={"anchor": _shifted(item.anchor, delta, across)})
                for item in sheet.cross_references
            ],
        }
    )


def _reader_of(
    project: ProjectModel,
    catalog: ComponentRegistry,
    placed: list[PlacedSymbol],
) -> Callable[[str, str], tuple[Point, PortFace] | None]:
    """Dove sta ogni porta su questa tavola: la lettura che l'invariante chiede.

    E' la stessa di `Improver.port_at`, scritta qui perche' il diario la usa su
    una tavola gia' consegnata, dove un ciclo di miglioramento non serve piu'.
    """
    definitions = {item.id: item.definition_id for item in project.components}
    by_id = {item.component_id: item for item in placed}

    def at(component_id: str, port_id: str) -> tuple[Point, PortFace] | None:
        item = by_id.get(component_id)
        if item is None or component_id not in definitions:
            return None
        manifest = catalog.resolve(definitions[component_id]).symbol.manifest.rotated(
            item.rotation_deg
        )
        port = manifest.port(item.physical_port(port_id))
        return (
            Point(x_mm=item.origin.x_mm + port.x_mm, y_mm=item.origin.y_mm + port.y_mm),
            port.face,
        )

    return at


def compose_sheet(
    project: ProjectModel,
    partition: SheetPartition,
    catalog: ComponentRegistry,
    frame: SheetFrame,
    inline_ids: frozenset[str],
    journal: ComposeJournal | None = None,
    last_resort: bool = False,
) -> SheetGeometry:
    """La tavola di questo foglio, **senza nessuna ricerca** (D-151).

    Fino al 20 settembre 2026 qui giravano due cercatori: la **fase del tronco**
    di `spine.py`, che posava le autostrade per prime risolvendo un sistema di
    vincoli, e il **ciclo di miglioramento** di `improve.py`, che spostava i
    pezzi minimizzando una somma pesata. **D-151 li ha tolti tutt'e due dalla
    decisione della posa**, e questa funzione e' il posto in cui quella
    decisione si vede: restano la posa deterministica di `place_sheet`,
    l'instradamento, gli accessori in linea, la legenda, i testi.

    **Il difetto non era la taratura, era la forma della domanda**: una somma
    pesata non sa esprimere una gerarchia di giudizio, e nessun peso dice «un
    collettore e' **una** linea dritta». Il PO, guardando l'autostrada che si
    piegava mentre gli stacchetti restavano dritti: «abbiamo ottimizzato le
    curve e gli attraversamenti sugli attacchetti e abbiamo fatto sta curva
    senza senso».

    **Che cosa mette i pezzi, adesso.** Il **piano di composizione**
    (`disegnatore_mep.piano`), che lo compone un agente e lo esegue il motore.
    Questa via resta per l'impianto che un piano non ce l'ha: quello che ne
    esce e' **cio' che il motore sa fare da solo**, e i rilievi lo dicono.
    Misurato il 20 settembre sui cinque impianti di prova, ed e' scritto nel
    rapporto di `DRAW-015`: senza il solutore e senza un piano, tutti e cinque
    finiscono sul formato piu' grande col ripiego dichiarato. **Non e' un
    difetto nascosto: e' la ragione per cui i piani si scrivono.**

    Dove e' finito il lavoro di chi e' uscito: `layout/improve.py`,
    `layout/spine.py` (la fase del tronco) e `layout/dilate.py` lo dicono in
    testa, ciascuno con la data e la decisione.
    """
    grid = GridSpace(origin=frame.drawing_rect_mm, standard=frame.standard)
    first = place_sheet(project, partition, catalog, frame, inline_ids)

    def settled(
        base: list[PlacedSymbol], last_resort: bool = False
    ) -> tuple[list[PlacedSymbol], list[RoutedTrunk]]:
        """La tavola instradata con gli accessori posati: la stessa che valuta
        il ciclo di miglioramento, perche' e' la stessa funzione (D-078).

        Con `last_resort` niente fa piu' fallire il foglio (**D-150**): la
        tratta che non si instrada prende la spezzata di ripiego, quella che
        non ospita i propri accessori resta intera e li perde, e tutt'e due si
        marcano `unresolved`. **Le due cose non sono lo stesso difetto** — una
        linea sbagliata, un accessorio che non c'e' — ma hanno lo stesso
        contratto verso chi guarda: *qui la tavola non e' quella che dovrebbe
        essere, e il preflight ti dice dove*. Un accessorio perso in silenzio
        sarebbe un errore di contenuto; dichiarato, e' un rilievo.
        """
        sheet = settle_sheet(
            project,
            list(partition.trunks),
            base,
            catalog,
            grid,
            tolerant=last_resort,
            last_resort=last_resort,
        )
        routes = [
            item.model_copy(update={"unresolved": True}) if index in set(sheet.unfit) else item
            for index, item in enumerate(sheet.routes)
        ]
        return sheet.symbols, routes

    # **La scala dei ripieghi se ne va con il solutore** (D-151). Fino al 20
    # settembre qui c'era una scala di sei vie: le fasi, la posa seminata dal
    # tronco, quattro cessioni graduali di una catena per volta, il ciclo senza
    # le fasi, la disposizione di partenza. Cinque delle sei erano **modi di
    # richiamare il solutore con un vincolo in meno**, e senza il solutore non
    # vogliono dire piu' niente: quello che resta e' la posa deterministica,
    # che era gia' l'ultimo gradino della scala.
    #
    # Il ripiego di **D-150** resta intero, ed e' l'unico: se questa posa non
    # si instrada, la tratta persa si segna e la tavola esce lo stesso.
    laid = highways(project, catalog, list(partition.trunks))
    ways: list[tuple[str, tuple[TrunkKey, ...], Callable[[], list[PlacedSymbol]]]] = [
        ("la posa deterministica, senza ricerca (D-151)", (), lambda: first),
    ]

    found: tuple[list[PlacedSymbol], list[RoutedTrunk]] | None = None
    story: tuple[str, tuple[TrunkKey, ...]] = ("nessuna: la tavola non esce", ())
    for note, given, base in ways:
        try:
            found = settled(base())
        except LayoutError:
            continue
        story = (note, given)
        break
    if found is None:
        # **Nessuna via si instrada, e la tavola esce lo stesso** (D-150). Fino
        # a qui il motore rialzava l'errore della prima via e il foglio moriva:
        # il PO non vedeva niente, e su tre impianti di prova su cinque non ha
        # mai visto niente. Misurato il 19 settembre, tutt'e tre morivano per
        # **una** tratta su decine.
        #
        # Il ripiego arriva **qui e non prima** perche' l'errore, finche' le vie
        # restano, e' il segnale con cui il motore ne sceglie una migliore. Solo
        # adesso che sono finite, una tavola con le tratte perse segnate vale
        # piu' di nessuna tavola: il PO la guarda e la giudica, e il disegnatore
        # la chiude in CAD sul DXF (I-072).
        if not last_resort:
            # Senza l'interruttore la tavola muore come e' sempre morta, e
            # l'errore della prima via — quella che si voleva — arriva a chi
            # compone. **Serve che muoia**: e' cosi' che la scala dei formati
            # sa che su questo foglio non ci sta e deve provarne uno piu'
            # grande. Se il ripiego scattasse qui, ogni foglio riuscirebbe e
            # l'impianto finirebbe sull'A4.
            found = settled(first)
        else:
            found = settled(first, last_resort=True)
            story = ("il ripiego dichiarato: le tratte perse sono segnate", ())
    placed, broken = found
    if journal is not None:
        journal.notes.append(
            ComposeNote(
                sheet_id=partition.sheet_id,
                ripiego=story[0],
                conceded=story[1],
                crooked=tuple(
                    key
                    for item in laid
                    if not lies_in_line(item, _reader_of(project, catalog, placed))
                    for key in item.keys
                ),
                highways=len(laid),
            )
        )

    entries, keys = build_legend(
        project, placed, partition.network_ids, catalog, frame
    )
    # L'ordine e' un contratto (DRAW-003, I-025): prima la posa, poi
    # l'instradamento completo, poi la centratura del blocco — e **solo alla
    # fine** i testi, su simboli e rotte ormai definitivi. Le etichette non
    # entrano nella centratura ne' in nessuna misura della posa: cambiare una
    # sigla non muove un simbolo ne' un punto di una rotta. La quota di terra
    # non si esporta: non e' un elemento della tavola (D-121).
    # **La dilatazione e' ritirata** (D-149). D-142 l'aveva chiesta per rendere
    # la tavola comoda allargando tutto insieme, ed era la mossa giusta contro
    # quella sbagliata; ma misurata sulla consegna di `DRAW-013` ha spostato
    # **2,5 mm sulla tavola 1 e 10 mm sulla 2**, perche' la griglia quantizza:
    # a fattore 1,08 cresce solo un vuoto lungo almeno sette passi, e qui i
    # vuoti sono quasi tutti di uno o due. Il PO, guardando le tavole: «prima
    # il disegno era meglio».
    #
    # `layout/dilate.py` **resta agli atti**, non cancellato: il giorno in cui
    # una posa distribuira' davvero i pezzi, i vuoti saranno grandi e la
    # dilatazione avra' qualcosa da allargare. Oggi no.
    grown, factor = (
        SheetGeometry(
            sheet_id=partition.sheet_id,
            title=partition.title,
            symbols=placed,
            routes=broken,
            legend=entries,
            network_keys=keys,
            cross_references=_cross_references(
                partition,
                {item.component_id: item for item in placed},
                {item.id: item.name for item in project.networks},
            ),
        ),
        1.0,
    )
    if journal is not None and journal.notes:
        journal.notes[-1] = replace(journal.notes[-1], dilation=factor)
    composed = centre_vertically(grown, frame.drawing_rect_mm, grid.step_mm)
    return composed.model_copy(
        update={
            "labels": place_labels(
                project,
                composed.symbols,
                frame.standard,
                # Le sigle stanno accanto al proprio pezzo (D-075), e al primo
                # conflitto con un tubo, un simbolo, un'altra scritta o il
                # margine si sposta il solo testo con il richiamo obliquo.
                routes=composed.routes,
                area=frame.drawing_rect_mm,
            )
        }
    )


def compose_drawing(
    project: ProjectModel,
    catalog: ComponentRegistry,
    frame: SheetFrame,
    journal: ComposeJournal | None = None,
    last_resort: bool = False,
) -> DrawingGeometry:
    """Dal modello tecnico approvato alla geometria di tutte le tavole.

    `last_resort` lo accende soltanto `compose_on_ordinary_frame`, e soltanto
    quando **nessun** formato ha retto (**D-150**).
    """
    inline_ids = inline_component_ids(project, catalog)
    # Le tratte si instradano nell'ordine **strutturale** dei propri capi, non
    # in quello in cui il file elenca le tubazioni: l'instradamento e' seriale
    # — ogni tratta evita quelle gia' disegnate — quindi quell'ordine e' parte
    # della geometria, e non deve dipendere da come i pezzi si chiamano
    # (DRAW-006-R1, blocco A.2).
    rank = structural_order(project)

    all_trunks = build_trunks(project, inline_ids)
    levels = hierarchy_of(project, catalog, all_trunks)

    def place_in_line(
        trunk: Trunk,
    ) -> tuple[int, int, tuple[int, str], tuple[int, str]]:
        """L'ordine in cui le tratte si instradano.

        **Prima le autostrade** (DRAW-008, e il PO l'11 settembre: «prima devi
        disegnare le autostrade»). L'instradamento e' seriale — ogni tratta
        evita quelle gia' disegnate — quindi l'ordine e' il modo in cui la
        gerarchia arriva fino all'ultimo anello della catena: chi si instrada
        prima sceglie la propria strada, chi viene dopo gira attorno. Con le
        autostrade in coda erano loro a girare attorno agli stacchi.

        A parita' di rango, prima quelle che portano una **catena di
        macchina**: i loro accessori stanno a distanza fissa dalla porta e non
        scivolano (I-044), quindi o quel posto e' libero o la tavola non esce.
        Poi l'ordine strutturale dei capi, che i nomi non decidono.

        **Una riga che `DRAW-012` ha guardato e lasciato dov'era.** Da §B le
        autostrade non sono piu' il solo circuito dei generatori, e dentro lo
        stesso rango ci sono adesso decine di tratte: scambiare le due chiavi —
        prima le rigide, poi il rango — e' una strada che ho provato e misurato,
        e sull'impianto 4 non cambia l'esito. L'ho lasciata fuori dalla consegna
        perche' cambierebbe l'ordine di instradamento di **ogni** tavola senza
        un guadagno che si veda; resta agli atti nel rapporto come filo per il PM.
        """
        ends = sorted(
            (rank.get(ref.component_id, 0), ref.port_id)
            for ref in (trunk.start, trunk.end)
        )
        head, tail = machine_chains(project, catalog, trunk)
        return (
            -int(levels[trunk.connection_ids]),
            0 if head or tail else 1,
            ends[0],
            ends[1],
        )

    trunks = sorted(all_trunks, key=place_in_line)
    partitions = partition_project(project, trunks)
    return DrawingGeometry(
        project_id=project.metadata.project_id,
        sheets=[
            compose_sheet(
                project,
                partition,
                catalog,
                frame,
                inline_ids,
                journal,
                last_resort=last_resort,
            )
            for partition in partitions
        ],
    )


def compose_on_ordinary_frame(
    project: ProjectModel,
    catalog: ComponentRegistry,
    frames: tuple[SheetFrame, ...] = ORDINARY_FRAMES,
    journal: ComposeJournal | None = None,
) -> tuple[SheetFrame, DrawingGeometry]:
    """Il disegno sul piu' piccolo formato ordinario su cui entra (D-058).

    «Entrarci» non vuol dire starci a stento: le distanze minime — corridoio di
    instradamento, stacco fra due componenti, gola fra due fasce larga almeno
    quanto gli accessori che la attraversano — sono vincoli del posizionamento,
    non desideri. Se il contenuto le rispetta su una A4, allora quel disegno e'
    davvero piccolo; altrimenti il posizionamento fallisce e si passa all'A3.
    Non serve un secondo criterio a percentuale: sarebbe anche fuorviante,
    perche' lo spazio libero viene distribuito fra le fasce e un disegno riempie
    per costruzione il foglio su cui e' stato composto.
    """
    for frame in frames:
        try:
            # Il diario descrive **la tavola consegnata**: un formato provato e
            # scartato non lascia note dietro di se'.
            if journal is not None:
                journal.clear()
            return frame, compose_drawing(project, catalog, frame, journal)
        except LayoutError:
            continue
    if not frames:
        raise LayoutError(
            "the plant does not fit on any ordinary sheet format: "
            "no format was offered to try"
        )
    # **Nessun formato ha retto, e la tavola esce lo stesso** (D-150). Si
    # riprende il **piu' grande** — quello che lascia piu' spazio, quindi
    # quello su cui le tratte perse saranno meno — e lo si ricompone col
    # ripiego acceso: la tratta che non si instrada prende la spezzata
    # dichiarata, l'accessorio che non ci sta manca, e il preflight li nomina
    # uno per uno.
    #
    # **Il ripiego non anticipa mai la scala.** Un formato che regge davvero
    # vince sempre su uno piu' grande col ripiego, perche' questa riga si
    # legge soltanto dopo che il ciclo qui sopra e' finito a vuoto. Perche' la
    # tavola sia uscita cosi' non lo dice piu' un'eccezione che nessuno vedra':
    # lo dice il **preflight**, tratta per tratta, su quella che esce.
    if journal is not None:
        journal.clear()
    return frames[-1], compose_drawing(
        project, catalog, frames[-1], journal, last_resort=True
    )


__all__ = [
    "ComposeJournal",
    "ComposeNote",
    "SheetLink",
    "centre_vertically",
    "compose_drawing",
    "compose_on_ordinary_frame",
    "compose_sheet",
    "inline_component_ids",
]
