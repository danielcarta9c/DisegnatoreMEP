"""Dove va posato ciascun componente, che e' meta' della partita.

Il PM, guardando la prima tavola: «Sulle linee delle tubazioni e sulla
posizione delle apparecchiature si gioca la vera partita. La regola e'
minimizzare le curve disegnate, minimizzare gli attraversamenti tra linee e
minimizzare la lunghezza delle linee mantenendo pero' ordinamenti da sinistra a
destra.» E l'esempio: «Hai messo il circolatore in un punto e per far entrare la
linea hai fatto sali-scendi; bastava spostare tutte le apparecchiature a destra
e guadagnavi lo spazio che serviva.»

Le tre voci le paga l'instradamento, ma chi le rende pagabili e' il
posizionamento: una piega non si toglie instradando meglio, se i due attacchi
che collega stanno a quote diverse. Da qui tre regole.

**L'ordine da sinistra a destra e' quello del processo.** Le fasce funzionali
(D-041) lo danno all'ingrosso; dentro una fascia lo da' la profondita' lungo la
mandata, e i rami senza seguito precedono la dorsale che prosegue. Prima si
ordinava per profondita' topologica misurata da una sorgente qualsiasi, che in
un circuito chiuso non esiste: la valvola deviatrice finiva a sinistra della
pompa di calore che la alimenta.

**Dentro una fascia il cursore orizzontale e' uno solo.** Prima ce n'era uno per
livello, cosi' una valvola a mezz'aria poteva stare esattamente sopra la
macchina che la alimenta: geometricamente valido, e nessun ordine leggibile.

**Chi sta su una tubazione si allinea all'attacco che lo alimenta.** Portare il
proprio attacco d'ingresso sulla quota di chi lo serve toglie due pieghe per
componente, ed e' quello che un tecnico fa senza pensarci.

Gli accessori in linea **non** vengono posati qui: appartengono alla tratta su
cui stanno, e li posa `inline.py` dopo l'instradamento (D-027).
"""

from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import ORDINARY_FRAMES, Rect, SheetFrame
from disegnatore_mep.graphics.symbol import PortFace, SymbolManifest
from disegnatore_mep.model.project import PortRef, ProjectModel
from disegnatore_mep.model.types import BandRole

from .composition import Standing, levels_of, standing_of
from .errors import LayoutError
from .flow import (
    GENERATOR_FUNCTIONS,
    LOAD_FUNCTIONS,
    STORE_FUNCTIONS,
    orient_trunks,
)
from .geometry import PlacedSymbol, Point
from .grid import GridSpace
from .inline import END_CLEARANCE_MM, MIN_SPACING_MM
from .partition import SheetPartition

BAND_GUTTER_MM = 10.0
"""Distanza minima fra due fasce funzionali contigue."""

MAX_EXTRA_GUTTER_MM = 30.0
"""Quanto si allarga al massimo una gola quando sul foglio avanza spazio.

Lo spazio libero non si lascia tutto a destra: si distribuisce fra le fasce,
perche' e' li' che passano le tubazioni e stanno gli accessori in linea. E'
la mossa che il PM ha indicato — «bastava spostare tutte le apparecchiature a
destra e guadagnavi lo spazio che serviva» — resa sistematica. Il tetto evita
che un impianto di tre pezzi si stiri per mezza tavola.
"""

ROW_GAP_MM = 10.0
"""Distanza minima fra due componenti affiancati o sovrapposti.

Quattro passi di griglia, cioe' **tre corsie libere** fra un pezzo e il
successivo. Con cinque millimetri ne restava una sola, e bastavano due tratte
che dovessero passare nello stesso varco — la mandata che scende in un
accumulo e il ritorno che ne risale — perche' una delle due dovesse
sovrapporsi all'altra. Sovrapporsi per il lungo e' vietato, quindi il varco
deve essere largo abbastanza da non costringerci.
"""

ROUTING_MARGIN_MM = 7.5
"""Corridoio libero fra il bordo dell'area di disegno e la prima fascia.

Senza, un simbolo appoggiato al bordo sinistro ha le proprie porte rivolte a
sinistra irraggiungibili: la rotta dovrebbe arrivare da fuori pagina.

**Tre** passi di griglia per lato, non quattro. Quattro era un numero tondo, non
una misura: il corridoio serve a far girare una rotta intorno a un simbolo di
bordo, e tre colonne bastano — una per scendere, una per passare, una di
rispetto. I cinque millimetri recuperati sui due lati sono quelli che fanno
entrare l'impianto completo su una A3 invece di dividerlo in due tavole, e
dividere e' un costo di lettura che si paga quando serve (D-056).
"""

_HORIZONTAL_FACES = (PortFace.LEFT, PortFace.RIGHT)

_OPPOSITE: dict[PortFace, PortFace] = {
    PortFace.BOTTOM: PortFace.TOP,
    PortFace.TOP: PortFace.BOTTOM,
    PortFace.LEFT: PortFace.RIGHT,
    PortFace.RIGHT: PortFace.LEFT,
}
"""Dove sta un pezzo rispetto al proprio attacco: dalla parte opposta a dove
l'attacco guarda. Uno sfogo che si imbocca da sotto sta **sopra** il punto in
cui si innesta."""

HANGING_CLEARANCE_MM = 5.0
"""Franco che si aggiunge alla lunghezza di uno stacco, oltre al conto dei pezzi.

Due passi di griglia. Il conto degli accessori dice quanto serve perche' ci
stiano in fila; questo dice quanto serve perche' ci stiano staccati da cio' che
corre di fianco, che e' l'altra meta' di cio' che `inline.py` pretende.
"""

CLEARANCE_STEPS = 2
"""Passi di stacco fra una linea e il bordo del simbolo da cui esce.

Un attacco rivolto in basso scarica su una corsia che deve **staccarsi** dal
riquadro: a un passo solo la linea corre a due millimetri e mezzo dal bordo e
sulla carta sembra disegnata sul simbolo.
"""

ZONED_FUNCTIONS = (
    GENERATOR_FUNCTIONS
    | STORE_FUNCTIONS
    | LOAD_FUNCTIONS
    | frozenset({"circulation", "distribution"})
)
"""Chi merita una zona, cioe' una colonna della fascia (D-120).

Il PM: «le zone servono solo per distribuire i **macro componenti**» —
generatori, accumuli, circolatori-collettori — e «le valvole che stanno in mezzo
possono finire dove vogliono, a cavallo fra le due zone o in una delle due».

Sono le **funzioni dichiarate dal catalogo**, mai un elenco di componenti
(D-090): chi genera, chi accumula o separa, chi utilizza, chi confina la rete,
chi spinge, chi ripartisce. Tutto il resto — raccordi, organi, strumenti — sta
sulla tratta a cui appartiene e non occupa un passo del processo.

**Il modo sbagliato di attuarlo e' gia' stato provato e buttato**, e vale la
pena non riprovarlo: far entrare la ferramenta *dentro* la colonna del proprio
pezzo grosso restringeva la tavola di centosessanta millimetri e faceva smettere
di uscire l'unica che usciva. La ferramenta non si comprime addosso a nessuno:
si toglie dalla fila e si posa dove la sua tratta passa.
"""


@dataclass(frozen=True)
class _Hanging:
    """Un accessorio che pende da uno stacco, e il pezzo da cui pende.

    Non e' un passo del processo e non merita una colonna sua: sta **accanto al
    proprio pezzo**, dalla parte in cui il suo unico attacco guarda. Prima
    veniva ordinato per profondita' come tutti gli altri, e finiva dove
    capitava: lo scarico del volano si e' ritrovato sessanta millimetri a
    sinistra del volano, con due macchine in mezzo, e la sua tratta non si e'
    piu' instradata su nessun formato, A0 compresa.
    """

    component_id: str
    parent_id: str
    parent_port_id: str
    room_mm: float
    """Il rettilineo che gli organi di chiusura dello stacco pretendono.

    Lo stacco e' corto per costruzione, ma non e' vuoto: la valvola che isola
    il vaso di espansione ci sta sopra, e se il pezzo si posa attaccato al
    proprio raccordo quella valvola non ha dove sedersi.
    """


def _file_order(project: ProjectModel) -> dict[str, int]:
    """La posizione di ogni componente nel modello: lo spareggio che non e' un nome.

    Dove due pezzi sono pari su ogni criterio strutturale si segue l'ordine in
    cui il progettista li ha elencati, mai l'ordine alfabetico dei loro
    identificativi (D-093): due impianti uguali con nomi diversi devono dare la
    stessa tavola.
    """
    return {item.id: index for index, item in enumerate(project.components)}


def _hanging_accessories(
    project: ProjectModel,
    partition: SheetPartition,
    catalog: ComponentRegistry,
    placeable: frozenset[str],
    room_of: Callable[[tuple[str, ...]], float],
) -> dict[str, list[_Hanging]]:
    """Chi pende da uno stacco, raccolto sotto il pezzo che lo regge.

    Il criterio non nomina nessun componente e non guarda le funzioni: legge il
    **catalogo**, che gia' dichiara quali attacchi stanno fuori dal percorso del
    fluido (`stub` o `serves`, D-101). Chi sta all'altro capo di uno di quegli
    attacchi, e ha un attacco solo, e' un accessorio appeso.
    """
    ports_of = {
        item.id: catalog.resolve(item.definition_id).definition.ports
        for item in project.components
        if item.id in placeable
    }

    def off_the_run(component_id: str, port_id: str) -> bool:
        return any(
            port.id == port_id and port.off_the_run
            for port in ports_of.get(component_id, [])
        )

    hanging: dict[str, list[_Hanging]] = defaultdict(list)
    claimed: set[str] = set()
    for trunk in partition.trunks:
        for parent, child in ((trunk.start, trunk.end), (trunk.end, trunk.start)):
            if parent.component_id == child.component_id:
                continue
            if child.component_id in claimed:
                continue
            if child.component_id not in placeable or parent.component_id not in placeable:
                continue
            if len(ports_of.get(child.component_id, [])) != 1:
                continue
            if not off_the_run(parent.component_id, parent.port_id):
                continue
            hanging[parent.component_id].append(
                _Hanging(
                    component_id=child.component_id,
                    parent_id=parent.component_id,
                    parent_port_id=parent.port_id,
                    room_mm=room_of(trunk.inline_component_ids),
                )
            )
            claimed.add(child.component_id)
            break

    # Un appeso che regge a sua volta un appeso tornerebbe a essere una colonna
    # senza che nessuno lo posi: la catena si ferma al primo livello, e chi
    # resta fuori riprende il proprio posto in fila.
    for parent_id in list(hanging):
        if parent_id in claimed:
            for item in hanging.pop(parent_id):
                claimed.discard(item.component_id)
    rank = _file_order(project)
    return {
        key: sorted(value, key=lambda item: rank.get(item.component_id, 0))
        for key, value in hanging.items()
    }


@dataclass(frozen=True)
class _RunChain:
    """Una catena di pezzi che stanno su una tratta, e i pezzi grossi che tocca."""

    members: tuple[str, ...]
    """In ordine di percorrenza, dal capo che tocca il primo estremo."""

    anchors: tuple[str, ...]
    """I pezzi grossi ai capi: possono essere piu' di due — una confluenza di
    due macchine su un accumulo ne tocca tre."""

    head_anchors: tuple[str, ...]
    """Quelli attaccati al primo della catena: dicono da che parte si comincia."""


def _ordered(
    chain: set[str], neighbours: dict[str, set[str]], rank: Callable[[str], int]
) -> tuple[str, ...]:
    """La catena in ordine di percorrenza, se e' un cammino semplice.

    Dove non lo e' — una catena che si biforca — non esiste un «lungo la
    tubazione», e l'ordine del modello basta a tenere il risultato ripetibile.
    """
    ends = sorted((item for item in chain if len(neighbours[item] & chain) <= 1), key=rank)
    if not ends:
        return tuple(sorted(chain, key=rank))
    order = [ends[0]]
    walked = {ends[0]}
    while True:
        forward = sorted((neighbours[order[-1]] & chain) - walked, key=rank)
        if len(forward) != 1:
            break
        order.append(forward[0])
        walked.add(forward[0])
    if len(order) != len(chain):
        return tuple(sorted(chain, key=rank))
    return tuple(order)


def _facing_edges(
    head: list[PlacedSymbol],
    tail: list[PlacedSymbol],
    *,
    horizontal: bool,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """I due bordi che si guardano fra due gruppi di pezzi gia' posati.

    Non i centri: fra due macchine affiancate il centro della piu' lontana sta
    **dietro** l'altra, e una catena che partisse da li' nascerebbe addosso alla
    macchina di mezzo. Si parte dal bordo piu' avanzato del gruppo che sta
    prima, e si arriva al bordo piu' arretrato del gruppo che sta dopo.
    """

    def centre(items: list[PlacedSymbol]) -> tuple[float, float]:
        return (
            sum((item.origin.x_mm + item.right_mm) / 2.0 for item in items) / len(items),
            sum((item.origin.y_mm + item.bottom_mm) / 2.0 for item in items) / len(items),
        )

    head_centre, tail_centre = centre(head), centre(tail)
    if horizontal:
        forward = tail_centre[0] >= head_centre[0]
        start = (
            max(item.right_mm for item in head)
            if forward
            else min(item.origin.x_mm for item in head)
        )
        finish = (
            min(item.origin.x_mm for item in tail)
            if forward
            else max(item.right_mm for item in tail)
        )
        return (start, head_centre[1]), (finish, tail_centre[1])
    forward = tail_centre[1] >= head_centre[1]
    start = (
        max(item.bottom_mm for item in head)
        if forward
        else min(item.origin.y_mm for item in head)
    )
    finish = (
        min(item.origin.y_mm for item in tail)
        if forward
        else max(item.bottom_mm for item in tail)
    )
    return (head_centre[0], start), (tail_centre[0], finish)


def _pieces_on_the_run(
    partition: SheetPartition,
    placeable: frozenset[str],
    hung: frozenset[str],
    is_zoned: Callable[[str], bool],
    rank: Callable[[str], int],
) -> list[_RunChain]:
    """Chi esce dalla fila delle colonne, e a quali pezzi e' legato (D-120).

    Un raccordo non e' un passo del processo: e' un punto della tubazione, e sta
    **fra i pezzi che unisce**. Finche' prendeva una colonna della fascia veniva
    letto come se fosse una macchina, e finiva dove lo mandava l'ordine del
    processo: sull'impianto 1 la confluenza dei due ritorni stava all'estrema
    sinistra del foglio, **prima delle due pompe di calore da cui quei ritorni
    arrivano**, e il ritorno attraversava la tavola due volte.

    Non si prova a metterlo «in mezzo a due estremi»: una confluenza di due
    macchine su un accumulo di estremi ne ha **tre**, e il posto giusto e' il
    baricentro di ciò a cui e' legato, qualunque sia il loro numero.

    Due condizioni, conservative apposta: il pezzo dev'essere legato ad
    **almeno due** altri — chi ne ha uno solo pende, e lo posa gia' `hang` — e
    la sua catena deve toccare **almeno un pezzo grosso**, o non ci sarebbe
    niente a cui appoggiarsi. Chi non le soddisfa tiene la propria colonna.
    """
    neighbours: dict[str, set[str]] = defaultdict(set)
    for trunk in partition.trunks:
        first, second = trunk.start.component_id, trunk.end.component_id
        if first == second or first not in placeable or second not in placeable:
            continue
        neighbours[first].add(second)
        neighbours[second].add(first)

    free = {
        item
        for item in placeable
        if item not in hung and not is_zoned(item) and len(neighbours[item]) > 1
    }
    seen: set[str] = set()
    result: list[_RunChain] = []
    for start in sorted(free, key=rank):
        if start in seen:
            continue
        chain: set[str] = set()
        stack = [start]
        while stack:
            current = stack.pop()
            if current in chain:
                continue
            chain.add(current)
            stack.extend((neighbours[current] & free) - chain)
        seen |= chain
        anchors = sorted(
            {
                other
                for item in chain
                for other in neighbours[item]
                if other not in chain and is_zoned(other) and other not in hung
            },
            key=rank,
        )
        if len(anchors) < 2:
            # Con un estremo solo non c'e' un «in mezzo»: la catena tiene le
            # proprie colonne, che e' il comportamento di prima.
            continue
        members = _ordered(chain, neighbours, rank)
        result.append(
            _RunChain(
                members=members,
                anchors=tuple(anchors),
                head_anchors=tuple(sorted(neighbours[members[0]] & set(anchors), key=rank)),
            )
        )
    return result


def _band_by_subsystem(project: ProjectModel, sheet_id: str) -> dict[str, BandRole]:
    for sheet in project.sheets:
        if sheet.id == sheet_id:
            return {item.subsystem_id: item.band for item in sheet.band_assignments}
    return {}


def _assign_bands(
    project: ProjectModel,
    partition: SheetPartition,
    placeable: list[str],
    depth_of: Callable[[str], int],
    _process_rank: Callable[[str], int],
) -> dict[str, BandRole]:
    band_of_subsystem = _band_by_subsystem(project, partition.sheet_id)
    bands: dict[str, BandRole] = {}
    if band_of_subsystem:
        for subsystem in project.subsystems:
            band = band_of_subsystem.get(subsystem.id)
            if band is None:
                continue
            for component_id in subsystem.component_ids:
                bands[component_id] = band
        missing = sorted(set(placeable) - set(bands))
        if missing:
            raise LayoutError(
                f"the pagination plan of sheet {partition.sheet_id} assigns no band to "
                f"{missing}: every component needs a band, or it would not be drawn"
            )
        return bands

    roles = list(BandRole)
    # Senza piano dichiarato, l'ordine delle fasce e' quello del **processo**:
    # chi genera sta a sinistra, poi chi accumula, poi chi utilizza. Lo dicono
    # le **funzioni dichiarate dal catalogo**, mai il nome di un sottosistema o
    # di un componente (D-090).
    #
    # Prima contava l'ordine in cui i sottosistemi comparivano nel file, che e'
    # quanto dire l'ordine alfabetico dei loro nomi: con `accumulo`,
    # `distribuzione`, `generazione` le due pompe di calore finivano
    # all'estrema destra e l'impianto si leggeva al contrario. Un ordine di
    # lettura deciso dal nome di un sottosistema non e' un ordine (D-093), e il
    # PM chiede l'opposto: le macchine principali a sinistra (D-111).
    if project.subsystems:
        ranked = sorted(
            project.subsystems,
            key=lambda item: (
                min(
                    (_process_rank(component_id) for component_id in item.component_ids),
                    default=len(roles),
                ),
                min(
                    (depth_of(component_id) for component_id in item.component_ids),
                    default=len(project.components),
                ),
                project.subsystems.index(item),
            ),
        )
        for index, subsystem in enumerate(ranked):
            role = roles[min(index, len(roles) - 1)]
            for component_id in subsystem.component_ids:
                bands[component_id] = role
        for component_id in placeable:
            bands.setdefault(component_id, roles[-1])
        return bands

    for component_id in placeable:
        bands[component_id] = roles[0]
    return bands


class _Process:
    """L'ordine del processo lungo la mandata: chi viene prima di chi.

    Si costruisce sulle tratte gia' orientate (D-059), quindi legge il verso
    reale del fluido e non la geometria di un disegno che ancora non esiste.
    """

    def __init__(
        self,
        project: ProjectModel,
        partition: SheetPartition,
        catalog: ComponentRegistry,
    ) -> None:
        trunks = list(partition.trunks)
        oriented = orient_trunks(project, catalog, trunks)
        self.feed: dict[str, tuple[PortRef, PortRef]] = {}
        self.position = _file_order(project)
        successors: dict[str, list[str]] = defaultdict(list)
        members: set[str] = set()
        for trunk in trunks:
            members.update({trunk.start.component_id, trunk.end.component_id})
            if oriented.get(trunk.connection_ids) is not True:
                continue
            source, target = trunk.start.component_id, trunk.end.component_id
            if source == target:
                continue
            successors[source].append(target)
            self.feed.setdefault(target, (trunk.start, trunk.end))

        self.depth = dict.fromkeys(members, 0)
        # Rilassamento sul cammino piu' lungo. Il grafo di mandata e' aciclico
        # per costruzione — l'anello si chiude sui ritorni — ma il numero di
        # passate resta limitato, perche' un modello sbagliato non deve
        # bloccare il disegno.
        for _ in range(len(members)):
            changed = False
            for source in sorted(successors):
                for target in sorted(successors[source]):
                    if self.depth[target] <= self.depth[source]:
                        self.depth[target] = self.depth[source] + 1
                        changed = True
            if not changed:
                break

        self.downstream: dict[str, int] = {}
        for component_id in members:
            seen: set[str] = set()
            frontier = list(successors[component_id])
            while frontier:
                current = frontier.pop()
                if current in seen:
                    continue
                seen.add(current)
                frontier.extend(successors[current])
            self.downstream[component_id] = len(seen)

    def order_of(self, component_id: str) -> tuple[int, int, int]:
        """Piu' e' a valle piu' sta a destra; a pari profondita' prima i rami morti.

        L'ultimo spareggio e' la posizione nel modello, non il nome (D-093).
        """
        return (
            self.depth.get(component_id, 0),
            self.downstream.get(component_id, 0),
            self.position.get(component_id, 0),
        )


def _port_of(manifest: SymbolManifest, port_id: str) -> tuple[float, float, PortFace]:
    for port in manifest.ports:
        if port.id == port_id:
            return port.x_mm, port.y_mm, port.face
    raise LayoutError(
        f"symbol {manifest.id} has no port {port_id}: the catalogue definition and "
        f"the symbol manifest disagree on the component's connections"
    )


def _outward(distance: int) -> tuple[int, ...]:
    """0, 1, -1, 2, -2, ...: la quota esatta, poi le piu' vicine."""
    return (0,) if distance == 0 else (distance, -distance)


def _slots(
    order: list[str],
    feeder_of: dict[str, str],
    stackable: dict[str, bool],
    *,
    ground: frozenset[str] = frozenset(),
    heights: dict[str, float] | None = None,
    linked: frozenset[tuple[str, str]] = frozenset(),
    headroom_mm: float = float("inf"),
) -> list[list[str]]:
    """Raggruppa in colonne: i rami paralleli si impilano invece di affiancarsi.

    Due zone servite dallo stesso collettore sono lo stesso passo del processo,
    non due passi in fila: metterle una sopra l'altra e' come le disegna
    chiunque, accorcia la tavola e ne usa l'altezza, che altrimenti resta
    bianca. Vale solo per chi sta su una tubazione: due accumuli appoggiati a
    terra non si possono impilare, e restano affiancati.

    `ground` e' il tentativo di recupero di D-072/D-073, e arriva popolato
    solo quando le fasce non entrano in larghezza: anche chi sta a terra puo'
    allora salire sopra un compagno di fascia — «il serbatoio ACS e il volano
    termico non in fila uno dopo l'altro ma uno sopra l'altro» — in coppie,
    il piu' basso sopra il piu' alto. Non si impila su chi e' collegato da una
    tratta (`linked`): l'ordine del processo resta leggibile in orizzontale.
    Chi sale scavalca le colonne fra la propria e quella ospite, quindi anche
    verso gli scavalcati non deve correre nessuna tratta.
    """
    slots: list[list[str]] = []
    for component_id in order:
        feeder = feeder_of.get(component_id)
        same_branch = (
            slots
            and stackable.get(component_id, False)
            and stackable.get(slots[-1][-1], False)
            and feeder is not None
            and feeder_of.get(slots[-1][-1]) == feeder
        )
        if same_branch:
            slots[-1].append(component_id)
        else:
            slots.append([component_id])
    if not ground:
        return slots

    tall = heights or {}
    merged: list[list[str]] = []
    open_indices: list[int] = []
    for slot in slots:
        if len(slot) != 1 or slot[0] not in ground:
            merged.append(slot)
            continue
        here = slot[0]

        def may_host(index: int, here: str = here) -> bool:
            mate = merged[index][0]
            if (
                tall.get(mate, 0.0) + ROW_GAP_MM + tall.get(here, 0.0)
                > headroom_mm + 1e-9
            ):
                return False
            jumped = [mate] + [
                item for others in merged[index + 1 :] for item in others
            ]
            return not any(
                tuple(sorted((item, here))) in linked for item in jumped
            )

        host = next((index for index in open_indices if may_host(index)), None)
        if host is None:
            merged.append(slot)
            open_indices.append(len(merged) - 1)
            continue
        mate = merged[host][0]
        # Il piu' alto resta a terra, il piu' basso gli sale sopra; a pari
        # altezza l'ordine di processo decide, e chi viene prima resta giu'.
        pair = [here, mate] if tall.get(here, 0.0) > tall.get(mate, 0.0) else [mate, here]
        merged[host] = pair
        open_indices.remove(host)
    return merged


def place_sheet(
    project: ProjectModel,
    partition: SheetPartition,
    catalog: ComponentRegistry,
    frame: SheetFrame,
    inline_component_ids: frozenset[str],
) -> list[PlacedSymbol]:
    """Dispone i componenti non in linea, a fasce, sulla griglia.

    Deterministico: stessa partizione e stesso piano danno la stessa geometria,
    e l'ordine di uscita segue le fasce da sinistra a destra.
    """
    drawing = frame.drawing_rect_mm
    # Il posizionamento lavora dentro un rettangolo piu' piccolo dell'area di
    # disegno: il bordo resta libero perche' l'instradamento possa raggiungere
    # le porte rivolte verso l'esterno.
    area = Rect(
        x_mm=drawing.x_mm + ROUTING_MARGIN_MM,
        y_mm=drawing.y_mm + ROUTING_MARGIN_MM,
        width_mm=drawing.width_mm - 2 * ROUTING_MARGIN_MM,
        height_mm=drawing.height_mm - 2 * ROUTING_MARGIN_MM,
    )
    grid = GridSpace(origin=area, standard=frame.standard)
    step = grid.step_mm

    placeable = [
        item for item in partition.component_ids if item not in inline_component_ids
    ]
    if not placeable:
        raise LayoutError(
            f"sheet {partition.sheet_id} carries only inline accessories: an "
            f"accessory sits on a run, so there is nothing to draw it against"
        )

    tags = {item.id: item.tag for item in project.components}
    process = _Process(project, partition, catalog)
    functions_of = {
        item.id: frozenset(catalog.resolve(item.definition_id).definition.functions)
        for item in project.components
    }

    def process_rank(component_id: str) -> int:
        """Che passo del processo e' un pezzo: genera, accumula, utilizza.

        Sono le stesse tre classi che gia' orientano le tratte (`flow.py`) e che
        danno il nome alle linee: qui decidono su quale fascia si posa un
        sottosistema, cioe' quanto a sinistra si legge.
        """
        functions = functions_of.get(component_id, frozenset())
        if functions & GENERATOR_FUNCTIONS:
            return 0
        if functions & STORE_FUNCTIONS:
            return 1
        if functions & LOAD_FUNCTIONS:
            return 2
        return 3

    bands = _assign_bands(
        project,
        partition,
        placeable,
        lambda item: process.depth.get(item, 0),
        process_rank,
    )
    order_hint = {
        item.subsystem_id: item.order
        for sheet in project.sheets
        if sheet.id == partition.sheet_id
        for item in sheet.band_assignments
    }
    subsystem_of = {
        component_id: subsystem.id
        for subsystem in project.subsystems
        for component_id in subsystem.component_ids
    }

    resolved = {
        item: catalog.resolve(
            next(c.definition_id for c in project.components if c.id == item)
        )
        for item in placeable
    }

    def _room_for(trunk_component_ids: tuple[str, ...]) -> float:
        """Il rettilineo che gli accessori di una tratta pretenderanno.

        E' lo stesso conto che `inline.py` fara' dopo l'instradamento: ogni
        accessorio vuole la propria interruzione piu' uno stacco dal vicino, e
        la fila intera vuole due stacchi dai componenti agli estremi.
        """
        accessories = [
            item for item in project.components if item.id in trunk_component_ids
        ]
        if not accessories:
            return 0.0
        return sum(
            (catalog.resolve(item.definition_id).symbol.manifest.inline_gap_mm or 0.0)
            + 2 * MIN_SPACING_MM
            for item in accessories
        ) + 2 * END_CLEARANCE_MM

    hanging = _hanging_accessories(
        project, partition, catalog, frozenset(placeable), _room_for
    )
    hung = {item.component_id for group in hanging.values() for item in group}

    def is_zoned(component_id: str) -> bool:
        return bool(functions_of.get(component_id, frozenset()) & ZONED_FUNCTIONS)

    chains = _pieces_on_the_run(
        partition,
        frozenset(placeable),
        frozenset(hung),
        is_zoned,
        lambda item: process.position.get(item, 0),
    )
    on_the_run = {item for chain in chains for item in chain.members}
    standing_columns = [
        item for item in placeable if item not in hung and item not in on_the_run
    ]
    if not standing_columns:
        # Un foglio di soli raccordi non esiste, ma se esistesse non avrebbe
        # nessun pezzo grosso a cui appoggiarli: si torna alla fila.
        chains, on_the_run = [], set()
        standing_columns = [item for item in placeable if item not in hung]

    def default_rotation(component_id: str) -> int:
        allowed = resolved[component_id].symbol.manifest.allowed_rotations_deg
        return 0 if 0 in allowed else min(allowed)

    def _sits_toward(component_id: str) -> PortFace:
        """Da che parte del proprio punto di attacco sta un accessorio appeso.

        Lo decide il **suo unico attacco**: chi ce l'ha in basso si posa sopra il
        punto in cui si innesta, chi ce l'ha in alto si posa sotto, e cosi' di
        fianco.
        """
        manifest = resolved[component_id].symbol.manifest.rotated(
            default_rotation(component_id)
        )
        return _OPPOSITE[manifest.ports[0].face]

    def rotation_for(component_id: str) -> int:
        """Come va girato un pezzo, e perche' non e' sempre come sta in libreria.

        Un raccordo con lo stacco rivolto in su e un vaso di espansione che si
        imbocca dall'alto non si possono unire con una linea diritta: il tubo
        dovrebbe uscire in su, scavalcare il raccordo e ridiscendere. Quattro
        pieghe per un pezzo che sta a cinque millimetri, e il primo corridoio
        stretto le rende impossibili — e' cosi' che il vaso e il gruppo di
        riempimento facevano fallire l'instradamento.

        La libreria dichiara le rotazioni ammesse: si prende quella che porta lo
        stacco **dalla parte in cui l'accessorio deve stare**, purche' i due capi
        del percorso restino orizzontali — un raccordo che tira su la strada
        invece che di lato non e' piu' un raccordo in linea.
        """
        manifest = resolved[component_id].symbol.manifest
        preferred = default_rotation(component_id)
        wanted = {
            item.parent_port_id: _sits_toward(item.component_id)
            for item in hanging.get(component_id, ())
        }
        if not wanted:
            return preferred
        for angle in sorted(
            manifest.allowed_rotations_deg, key=lambda item: (item != preferred, item)
        ):
            turned = manifest.rotated(angle)
            if any(
                turned.port(port_id).face is not face
                for port_id, face in wanted.items()
            ):
                continue
            if any(
                port.face not in _HORIZONTAL_FACES
                for port in turned.ports
                if port.id not in wanted
            ):
                continue
            return angle
        return preferred

    manifests = {
        item: resolved[item].symbol.manifest.rotated(rotation_for(item))
        for item in placeable
    }
    standings = {
        item: standing_of(
            manifests[item].height_mm,
            frozenset(resolved[item].definition.functions),
            resolved[item].is_inline,
        )
        for item in placeable
    }

    reading = {role: index for index, role in enumerate(BandRole)}

    def continues_rightwards(component_id: str) -> int:
        """Vero se questo pezzo e' legato a qualcosa di una fascia successiva.

        Chi prosegue va posato **per ultimo** nella propria fascia, qualunque sia
        la sua profondita': altrimenti fra lui e la fascia che alimenta si
        infilano i rami morti, e la tratta che li collega — con i suoi accessori
        — si ritrova senza rettilineo. E' capitato al volano, separato dal
        collettore dalle utenze sanitarie.
        """
        here = reading.get(bands.get(component_id, BandRole.GENERATION), 0)
        for trunk in partition.trunks:
            ends = {trunk.start.component_id, trunk.end.component_id}
            if component_id not in ends:
                continue
            for other in ends - {component_id}:
                if reading.get(bands.get(other, BandRole.GENERATION), 0) > here:
                    return 1
        return 0

    columns: dict[BandRole, list[str]] = defaultdict(list)
    for component_id in standing_columns:
        columns[bands[component_id]].append(component_id)
    for role in columns:
        columns[role].sort(
            key=lambda item: (
                order_hint.get(subsystem_of.get(item, ""), 0),
                continues_rightwards(item),
                *process.order_of(item),
            )
        )

    def snap_up(value_mm: float, origin_mm: float) -> float:
        """Il primo nodo di griglia non prima di `value_mm`.

        Misurato **dall'origine dell'area di disegno**, non dallo zero del
        foglio: l'area comincia a 16 mm dal bordo, che non e' un multiplo del
        passo, e snappare in assoluto porterebbe fuori griglia ogni simbolo.
        """
        offset = value_mm - origin_mm
        steps = int(offset / step) + (1 if offset % step > 1e-9 else 0)
        return origin_mm + step * steps

    def on_grid(value_mm: float, origin_mm: float) -> float:
        return origin_mm + round((value_mm - origin_mm) / step) * step

    def inline_room(here: set[str], there: set[str]) -> float:
        """Quanto rettilineo vogliono gli accessori delle tratte fra due colonne.

        Da quando le regole completano l'impianto, una tratta fra due componenti
        affiancati puo' ritrovarsi a portare tre accessori: fra la pompa di
        calore e la sua valvola deviatrice ci stanno termometro, separatore
        d'aria e valvola di sicurezza. Dieci millimetri non bastano, e a
        scoprirlo sarebbe `inline.py` dopo l'instradamento, quando spostare
        qualcosa non e' piu' possibile.

        Solo le tratte **fra queste due colonne**: quelle che vengono da lontano
        hanno gia' il proprio rettilineo lungo la strada.
        """
        return max(
            (
                _room_for(trunk.inline_component_ids)
                for trunk in partition.trunks
                if {trunk.start.component_id, trunk.end.component_id} & here
                and {trunk.start.component_id, trunk.end.component_id} & there
            ),
            default=0.0,
        )

    used_roles = [role for role in BandRole if columns.get(role)]
    feeder_of = {
        component_id: feed[0].component_id
        for component_id, feed in process.feed.items()
    }
    stackable = {item: standings[item] is Standing.RAIL for item in placeable}
    # Le quote si misurano sull'**area di disegno**, non sul rettangolo ridotto
    # in cui si impaccano le fasce: il corridoio di instradamento restringe
    # dove si posa, non dove passa la linea di terra.
    levels = levels_of(drawing.y_mm, drawing.height_mm, step)
    linked = frozenset(
        (trunk.start.component_id, trunk.end.component_id)
        if trunk.start.component_id <= trunk.end.component_id
        else (trunk.end.component_id, trunk.start.component_id)
        for trunk in partition.trunks
    )
    heights = {item: manifests[item].height_mm for item in placeable}

    def hangs_toward(component_id: str) -> PortFace:
        return _OPPOSITE[manifests[component_id].ports[0].face]

    def hanging_gap(item: _Hanging) -> float:
        """Quanto lo stacco deve essere lungo: almeno quanto cio' che ci sta sopra.

        Il conto degli accessori dice il **minimo** perche' ci stiano in fila; il
        franco in piu' serve perche' ci stiano **staccati** da cio' che passa
        accanto, che e' l'altra meta' della richiesta di `inline.py`. Senza, la
        valvola del gruppo di riempimento trovava i suoi dieci millimetri esatti
        e nessun respiro intorno.
        """
        return max(ROW_GAP_MM, snap_up(item.room_mm + HANGING_CLEARANCE_MM, 0.0))

    def sideways(component_id: str) -> tuple[float, float]:
        """Quanto un pezzo sporge a sinistra e a destra per cio' che gli pende."""
        left = right = 0.0
        for item in hanging.get(component_id, ()):
            side = hangs_toward(item.component_id)
            width = manifests[item.component_id].width_mm + hanging_gap(item)
            if side is PortFace.LEFT:
                left += width
            elif side is PortFace.RIGHT:
                right += width
        return left, right

    def overhang(component_id: str, side: PortFace) -> float:
        """Quanto un pezzo sporge, sopra o sotto, per cio' che gli pende.

        Non e' decorazione: fra il pezzo e cio' che gli pende passa il tubo che
        li unisce, e quel corridoio va **riservato**. Senza, impilare due colonne
        mette il pezzo di sotto proprio nel varco dello stacco di quello di
        sopra, e la tratta piu' corta della tavola non si instrada piu'.
        """
        return max(
            (
                hanging_gap(item) + manifests[item.component_id].height_mm
                for item in hanging.get(component_id, ())
                if hangs_toward(item.component_id) is side
            ),
            default=0.0,
        )

    def lift_above_ground(component_id: str) -> float:
        """Di quanto una macchina si stacca da terra per cio' che le pende sotto.

        Un serbatoio con lo scarico sul fondo appoggiato **esattamente** sulla
        linea di terra non ha dove metterlo: sotto la terra non si instrada, e
        l'unica cella libera sotto l'attacco e' gia' pavimento. Su una tavola
        vera il serbatoio sta su un basamento e lo scarico si disegna sotto di
        lui, sopra il pavimento. Qui e' la stessa cosa, misurata.
        """
        return overhang(component_id, PortFace.BOTTOM)

    def footprint_width(component_id: str) -> float:
        """La larghezza che un pezzo occupa **con cio' che gli pende accanto**.

        Chi pende sopra o sotto non allarga niente; chi pende di fianco si',
        e dimenticarlo farebbe sbordare la colonna dentro la successiva.
        """
        left, right = sideways(component_id)
        own = manifests[component_id].width_mm
        stacked = max(
            (
                manifests[item.component_id].width_mm
                for item in hanging.get(component_id, ())
                if hangs_toward(item.component_id) in (PortFace.TOP, PortFace.BOTTOM)
            ),
            default=0.0,
        )
        return left + max(own, stacked) + right

    def neighbours_of(component_id: str) -> frozenset[str]:
        """A cosa un pezzo e' attaccato, senza contare cio' che gli pende.

        Cio' che pende da uno stacco viaggia col proprio pezzo e non lo
        distingue da nessuno: contarlo direbbe che due pompe di calore identiche
        non sono in parallelo perche' una ha lo sfiato e l'altra no.
        """
        return frozenset(
            other
            for trunk in partition.trunks
            for ends in ({trunk.start.component_id, trunk.end.component_id},)
            if component_id in ends
            for other in ends - {component_id}
            if other not in hung
        )

    def column_height(slot: list[str]) -> float:
        """Quanto e' alta una colonna con i suoi pezzi uno sopra l'altro.

        Ogni pezzo porta con se' cio' che gli pende sopra e sotto, corridoio
        dello stacco compreso: dimenticarlo faceva entrare la colonna nei conti
        e non nel foglio.
        """
        return sum(
            overhang(item, PortFace.TOP) + heights[item] + overhang(item, PortFace.BOTTOM)
            for item in slot
        ) + ROW_GAP_MM * (len(slot) - 1)

    def may_stack(over: list[str], under: list[str]) -> bool:
        """Se due colonne contigue possono diventare una sola, impilate.

        Si impila **cio' che sta in parallelo, mai cio' che sta in fila.** Due
        zone servite dallo stesso collettore sono lo **stesso passo** del
        processo e una sopra l'altra si leggono come sono; due raccordi che si
        susseguono sulla stessa linea sono **due passi in fila**, e impilarli
        spezza la lettura da sinistra a destra che il PM ha chiesto — oltre a
        costringere la linea a scendere e risalire proprio nel varco dove passa
        lo stacco del primo.

        Il parallelo si riconosce da un fatto solo: **due cose sono in parallelo
        quando pendono dalle stesse cose.** Due pompe di calore attaccate allo
        stesso collettore di mandata e allo stesso collettore di ritorno hanno gli
        stessi vicini; due raccordi in fila sulla stessa linea no — il primo
        guarda il volume, il secondo guarda il collettore. La profondita' lungo
        la mandata non basta a dirlo: il ritorno non e' orientato, e tutto cio'
        che ci sta sopra risulterebbe alla stessa profondita'.

        E vale anche qui che chi appoggia a terra e chi pende da una tubazione
        stanno a due quote diverse e non si impilano l'uno sull'altro.
        """
        if any(
            tuple(sorted((first, second))) in linked
            for first in over
            for second in under
        ):
            return False
        if len({neighbours_of(item) for item in (*over, *under)}) != 1:
            return False
        if len({standings[item] for item in (*over, *under)}) != 1:
            return False
        return (
            column_height(over) + ROW_GAP_MM + column_height(under)
            <= levels.ground_mm - area.y_mm + 1e-9
        )

    def compress(
        slots: dict[BandRole, list[list[str]]], budget_mm: float
    ) -> dict[BandRole, list[list[str]]]:
        """Impila una colonna sulla precedente finche' la fila entra nel foglio.

        E' la mossa che D-111 chiede e che mancava: «serve che il collocatore
        possa mettere le cose anche **una sotto l'altra** e non solo una a fianco
        all'altra, e che sappia scegliere fra le disposizioni possibili». Il
        foglio e' un'area da ripartire, non una striscia.

        Si sceglie a ogni giro l'accoppiamento che **restringe di piu'**, e ci si
        ferma appena la fila entra: fra le disposizioni possibili si prende la
        prima che basta, non la piu' compressa, perche' comprimere oltre il
        bisogno accorcia la tavola e la impoverisce. A parita' di guadagno decide
        l'ordine delle fasce e poi quello delle colonne, quindi il risultato non
        dipende da come il file elenca i pezzi.
        """
        current = {role: [list(slot) for slot in slots[role]] for role in used_roles}

        def copy(
            plan: dict[BandRole, list[list[str]]],
        ) -> dict[BandRole, list[list[str]]]:
            return {role: [list(slot) for slot in plan[role]] for role in used_roles}

        def moves(
            plan: dict[BandRole, list[list[str]]],
        ) -> list[tuple[int, int, int, dict[BandRole, list[list[str]]]]]:
            """Le mosse possibili: impilare, oppure scambiare due colonne.

            Lo scambio e' la seconda mossa che D-112 chiede — «cambiare il loro
            ordine relativo quando la topologia lo consente» — e paga piu' di
            quanto sembri: due colonne che si toccano si portano dietro il
            rettilineo degli accessori della tratta che le unisce, e allontanarle
            lo fa pagare alla strada, che quel rettilineo ce l'ha gia'.
            Si scambiano solo colonne che **nessuna tratta collega**, o si
            invertirebbe il verso di lettura del processo.
            """
            found: list[tuple[int, int, int, dict[BandRole, list[list[str]]]]] = []
            for position, role in enumerate(used_roles):
                for index in range(1, len(plan[role])):
                    before, after = plan[role][index - 1], plan[role][index]
                    if may_stack(before, after):
                        trial = copy(plan)
                        trial[role][index - 1] = [*before, *after]
                        del trial[role][index]
                        found.append((0, position, index, trial))
                    joined = any(
                        tuple(sorted((first, second))) in linked
                        for first in before
                        for second in after
                    )
                    if not joined:
                        trial = copy(plan)
                        trial[role][index - 1], trial[role][index] = after, before
                        found.append((1, position, index, trial))
            return found

        while measure(current)[-1] > budget_mm + 1e-9:
            before_mm = measure(current)[-1]
            best: tuple[float, int, int, int] | None = None
            chosen: dict[BandRole, list[list[str]]] | None = None
            for kind, position, index, trial in moves(current):
                saved = before_mm - measure(trial)[-1]
                if saved <= 0:
                    continue
                key = (-saved, kind, position, index)
                if best is None or key < best:
                    best, chosen = key, trial
            if chosen is None:
                return current
            current = chosen
        return current

    def measure(
        slots: dict[BandRole, list[list[str]]],
    ) -> tuple[
        dict[BandRole, list[float]],
        dict[BandRole, float],
        list[float],
        float,
    ]:
        """Stacchi, larghezze, gole e larghezza totale di una disposizione."""
        gaps = {
            role: [
                max(
                    ROW_GAP_MM,
                    snap_up(
                        inline_room(
                            set(slots[role][index]), set(slots[role][index + 1])
                        ),
                        0.0,
                    ),
                )
                for index in range(len(slots[role]) - 1)
            ]
            for role in used_roles
        }
        widths = {
            role: snap_up(
                area.x_mm
                + sum(
                    max(footprint_width(item) for item in slot)
                    for slot in slots[role]
                )
                + sum(gaps[role]),
                area.x_mm,
            )
            - area.x_mm
            for role in used_roles
        }
        # Una gola non e' larga soltanto per estetica: e' li' che corrono le
        # tratte fra una fascia e l'altra. Vale lo stesso criterio degli
        # stacchi interni — si guarda alle **colonne che si toccano**, l'ultima
        # di una fascia e la prima della successiva. Provare a provvedere per
        # ogni tratta che attraversa il confine sovrastimava di ottanta
        # millimetri: una tratta fra componenti lontani viaggia a lungo e il
        # proprio rettilineo ce l'ha gia'.
        gutters = [
            max(
                BAND_GUTTER_MM,
                snap_up(
                    inline_room(
                        set(slots[used_roles[index]][-1]),
                        set(slots[used_roles[index + 1]][0]),
                    ),
                    0.0,
                ),
            )
            for index in range(len(used_roles) - 1)
        ]
        return gaps, widths, gutters, sum(widths.values()) + sum(gutters)

    def pack(
        stacked_ground: frozenset[str],
    ) -> tuple[
        dict[BandRole, list[list[str]]],
        dict[BandRole, list[float]],
        dict[BandRole, float],
        list[float],
        float,
    ]:
        """Colonne, stacchi, larghezze e gole per un dato insieme impilabile.

        Un solo cursore per fascia: la fascia e' larga quanto le sue colonne in
        fila, qualunque quota occupino, e una colonna e' larga quanto il suo
        pezzo piu' largo. Gli stacchi si calcolano **una volta sola** e si
        riusano nel posizionamento: calcolarli due volte con formule diverse
        faceva sbordare una fascia dentro la successiva.
        """
        slots = {
            role: _slots(
                columns[role],
                feeder_of,
                stackable,
                ground=stacked_ground,
                heights=heights,
                linked=linked,
                headroom_mm=levels.ground_mm - area.y_mm,
            )
            for role in used_roles
        }
        # **Cio' che sta in parallelo si impila, sempre — non solo quando manca
        # la larghezza** (D-119): «generatori a sinistra, impilati in verticale
        # se sono piu' di uno». Non e' una compressione, e' come si disegna una
        # centrale: due macchine in parallelo hanno gli stessi vicini, e messe
        # in fila costringono il collettore che le serve a stare da una parte
        # sola — di qua o di la' — con il ritorno della seconda che attraversa
        # la tavola per raggiungerlo. Prima capitava per caso: le due pompe si
        # impilavano solo perche' la fila non entrava nel foglio, e appena la
        # tavola si e' allargata si sono affiancate e il ritorno si e' rotto.
        for role in used_roles:
            index = 1
            while index < len(slots[role]):
                before, after = slots[role][index - 1], slots[role][index]
                if may_stack(before, after):
                    slots[role][index - 1] = [*before, *after]
                    del slots[role][index]
                    continue
                index += 1
        return slots, *measure(slots)

    slots, gaps, widths, gutters, total = pack(frozenset())
    if total > area.width_mm + 1e-9:
        # Prima di dividere si impila (D-072): il criterio di divisione non e'
        # «il contenuto non ci sta come l'ho disposto», ma «anche disponendolo
        # meglio non ci sta». Si riprova una volta lasciando salire anche chi
        # sta a terra (D-073); solo se nemmeno cosi' entra, l'errore e' quello
        # originale, con la larghezza misurata della disposizione in fila.
        # Il tentativo vale sul **formato piu' grande**, dove fallire vuol dire
        # dividere: sui formati minori fallire vuol dire salire di formato, e
        # impilare li' comprimerebbe su una A4 un disegno che D-058 manda in A3.
        overflow = LayoutError(
            f"the {len(used_roles)} functional bands need {total:g}mm but the drawing "
            f"area is {area.width_mm:g}mm wide: symbols are never shrunk to fit, "
            f"split the plant across more sheets"
        )
        largest = max(item.standard.usable_width_mm for item in ORDINARY_FRAMES)
        if frame.standard.usable_width_mm < largest - 1e-9:
            raise overflow
        ground_ids = frozenset(
            item for item in placeable if standings[item] is Standing.GROUND
        )
        slots, gaps, widths, gutters, total = pack(ground_ids)
        if total > area.width_mm + 1e-9:
            # Ultimo tentativo prima di arrendersi: il foglio ha anche
            # un'altezza, e finora nessuno la usava (D-111).
            slots = compress(slots, area.width_mm)
            gaps, widths, gutters, total = measure(slots)
        if total > area.width_mm + 1e-9:
            raise overflow
    if gutters:
        spare = (area.width_mm - total) / len(gutters)
        extra = min(int(spare / step) * step, MAX_EXTRA_GUTTER_MM)
        gutters = [item + extra for item in gutters]
    placed: list[PlacedSymbol] = []
    boxes: list[tuple[float, float, float, float]] = []

    def free_of_symbols(left: float, top: float, width: float, height: float) -> bool:
        return not any(
            left < x1 + ROW_GAP_MM
            and x0 - ROW_GAP_MM < left + width
            and top < y1 + ROW_GAP_MM
            and y0 - ROW_GAP_MM < top + height
            for x0, y0, x1, y1 in boxes
        )

    def corridor_is_clear(from_x: float, to_x: float, row: float) -> bool:
        """Nessun simbolo gia' posato taglia il rettilineo che porta all'attacco.

        Il bordo del riquadro conta come dentro, perche' cosi' lo tratta
        l'instradamento: una corsia che passa esattamente sul filo di un
        simbolo per lui e' occupata, e la linea diritta che qui si credeva di
        aver trovato diventa un gomito in piu'.
        """
        low, high = min(from_x, to_x), max(from_x, to_x)
        return not any(
            y0 <= row <= y1 and x0 < high and low < x1 for x0, y0, x1, y1 in boxes
        )

    def aligned_top(component_id: str, left: float, floor: float) -> float | None:
        """La quota che porta l'attacco d'ingresso sulla linea che lo alimenta."""
        feed = process.feed.get(component_id)
        if feed is None:
            return None
        source, target = feed
        feeder = next(
            (item for item in placed if item.component_id == source.component_id), None
        )
        source_manifest = manifests.get(source.component_id)
        if feeder is None or source_manifest is None:
            return None
        source_x, source_y, source_face = _port_of(source_manifest, source.port_id)
        _, target_y, target_face = _port_of(manifests[component_id], target.port_id)
        if target_face not in _HORIZONTAL_FACES:
            return None
        exit_y = feeder.origin.y_mm + source_y
        if source_face is PortFace.BOTTOM:
            exit_y += CLEARANCE_STEPS * step
        elif source_face is PortFace.TOP:
            exit_y -= CLEARANCE_STEPS * step
        exit_x = feeder.origin.x_mm + source_x
        wanted = on_grid(max(exit_y - target_y, floor), area.y_mm)
        manifest = manifests[component_id]
        # Si prova la quota esatta, poi quelle sempre piu' lontane: se un altro
        # componente sta gia' li', o gli sta in mezzo, la linea diritta non c'e'
        # comunque, e tanto vale cercarla dove c'e' posto.
        for distance in range(int(area.height_mm / step)):
            for offset in _outward(distance):
                top = wanted + offset * step
                if top < area.y_mm - 1e-9 or top < floor - 1e-9:
                    continue
                if top + manifest.height_mm > levels.ground_mm + 1e-9:
                    continue
                if not free_of_symbols(left, top, manifest.width_mm, manifest.height_mm):
                    continue
                if not corridor_is_clear(exit_x, left, top + target_y):
                    continue
                return top
        return None

    def clear_of_symbols(
        left: float,
        top: float,
        width: float,
        height: float,
        parent_left: float,
        parent_top: float,
        parent: SymbolManifest,
    ) -> bool:
        """Il riquadro non tocca nessun simbolo, tranne il proprio pezzo.

        Il proprio pezzo si esclude perche' e' quello a cui si appende: gli sta
        vicino per costruzione, e chiedergli lo stesso stacco degli estranei lo
        manderebbe a spasso.
        """
        own = (
            parent_left,
            parent_top,
            parent_left + parent.width_mm,
            parent_top + parent.height_mm,
        )
        return not any(
            box != own
            and left < box[2] + step
            and box[0] - step < left + width
            and top < box[3] + step
            and box[1] - step < top + height
            for box in boxes
        )

    def hang(parent_id: str, parent_left: float, parent_top: float) -> None:
        """Posa cio' che pende dal pezzo appena posato, accanto a lui.

        L'ancoraggio e' l'**attacco** da cui pende, non il centro del pezzo:
        uno scarico sul fondo di un accumulo scende dal punto in cui il fondo lo
        dichiara, e non dalla mezzeria del serbatoio.

        **Nulla scende sotto la linea di terra**: sotto c'e' il pavimento e la
        fascia dei richiami, e l'instradamento non ci passa. Chi dovrebbe finirci
        risale fin dove ci sta, e chi lo regge si e' gia' alzato quanto basta.
        """
        parent = manifests[parent_id]
        for item in hanging.get(parent_id, ()):
            child = manifests[item.component_id]
            stub_x, stub_y, _ = _port_of(parent, item.parent_port_id)
            port_x, port_y, _ = _port_of(child, child.ports[0].id)
            gap = hanging_gap(item)
            side = hangs_toward(item.component_id)
            if side is PortFace.TOP:
                child_left = parent_left + stub_x - port_x
                child_top = parent_top - gap - child.height_mm
            elif side is PortFace.BOTTOM:
                child_left = parent_left + stub_x - port_x
                child_top = min(
                    parent_top + parent.height_mm + gap,
                    levels.ground_mm - child.height_mm,
                )
            elif side is PortFace.RIGHT:
                child_left = parent_left + parent.width_mm + gap
                child_top = parent_top + stub_y - port_y
            else:
                child_left = parent_left - gap - child.width_mm
                child_top = parent_top + stub_y - port_y
            child_left = on_grid(child_left, area.x_mm)
            child_top = on_grid(child_top, area.y_mm)
            # Il foglio ha un bordo, e un accessorio appeso non lo scavalca: se
            # dalla parte del proprio attacco non c'e' spazio, si rientra. La
            # tratta ci arriva lo stesso, con una piega in piu'.
            child_left = min(
                max(child_left, area.x_mm), area.right_mm - child.width_mm
            )
            child_top = min(
                max(child_top, area.y_mm), levels.ground_mm - child.height_mm
            )
            # Il posto giusto e' quello, ma il foglio e' condiviso: se ci sta
            # gia' qualcun altro ci si allontana lungo lo stacco, un passo per
            # volta. Un accessorio appeso non ha diritto di posarsi addosso a
            # una macchina solo perche' il suo raccordo guarda da quella parte.
            reach = (
                area.bottom_mm - area.y_mm
                if side in (PortFace.TOP, PortFace.BOTTOM)
                else area.width_mm
            )
            away = {
                PortFace.TOP: (0.0, -step),
                PortFace.BOTTOM: (0.0, step),
                PortFace.RIGHT: (step, 0.0),
                PortFace.LEFT: (-step, 0.0),
            }[side]
            for _ in range(int(reach / step)):
                if clear_of_symbols(
                    child_left,
                    child_top,
                    child.width_mm,
                    child.height_mm,
                    parent_left,
                    parent_top,
                    parent,
                ):
                    break
                moved_left = child_left + away[0]
                moved_top = child_top + away[1]
                if (
                    moved_left < area.x_mm - 1e-9
                    or moved_left + child.width_mm > area.right_mm + 1e-9
                    or moved_top < area.y_mm - 1e-9
                    or moved_top + child.height_mm > levels.ground_mm + 1e-9
                ):
                    break
                child_left, child_top = moved_left, moved_top
            placed.append(
                PlacedSymbol(
                    component_id=item.component_id,
                    symbol_id=child.id,
                    rotation_deg=rotation_for(item.component_id),
                    origin=Point(x_mm=child_left, y_mm=child_top),
                    width_mm=child.width_mm,
                    height_mm=child.height_mm,
                    tag=tags.get(item.component_id),
                )
            )
            boxes.append(
                (
                    child_left,
                    child_top,
                    child_left + child.width_mm,
                    child_top + child.height_mm,
                )
            )

    position_of = {role: index for index, role in enumerate(used_roles)}
    x_mm = area.x_mm
    for role in used_roles:
        cursor = x_mm
        for position, slot in enumerate(slots[role]):
            left = on_grid(cursor + max(sideways(item)[0] for item in slot), area.x_mm)
            floor = area.y_mm
            ground_top: float | None = None
            for component_id in slot:
                manifest = manifests[component_id]
                if standings[component_id] is Standing.GROUND:
                    if ground_top is None:
                        top = on_grid(
                            levels.ground_mm
                            - manifest.height_mm
                            - lift_above_ground(component_id),
                            area.y_mm,
                        )
                    else:
                        # La coppia impilata del tentativo di recupero (D-073):
                        # il secondo lascia la terra e sale sopra il primo,
                        # allineato a sinistra, con lo stacco di fascia. Sopra
                        # il primo c'e' anche **cio' che gli pende sopra**: lo
                        # sfogo di un volano sta fuori dal suo riquadro, e chi
                        # gli saliva addosso ci finiva sopra.
                        top = on_grid(
                            ground_top - ROW_GAP_MM - manifest.height_mm, area.y_mm
                        )
                    ground_top = top - overhang(component_id, PortFace.TOP)
                else:
                    found = aligned_top(component_id, left, floor)
                    if found is None:
                        fallback = (
                            levels.auxiliary_mm
                            if standings[component_id] is Standing.AUXILIARY
                            else levels.lower_supply_mm - manifest.height_mm / 2
                        )
                        found = on_grid(max(fallback, floor), area.y_mm)
                        while (
                            not free_of_symbols(
                                left, found, manifest.width_mm, manifest.height_mm
                            )
                            and found + manifest.height_mm < levels.ground_mm
                        ):
                            found += ROW_GAP_MM
                    top = found
                if (
                    top < area.y_mm - 1e-9
                    or top + manifest.height_mm > area.bottom_mm + 1e-9
                ):
                    raise LayoutError(
                        f"component {component_id} does not fit between the drawing "
                        f"area and the ground line: symbols are never shrunk to fit"
                    )
                placed.append(
                    PlacedSymbol(
                        component_id=component_id,
                        symbol_id=manifest.id,
                        rotation_deg=rotation_for(component_id),
                        origin=Point(x_mm=left, y_mm=top),
                        width_mm=manifest.width_mm,
                        height_mm=manifest.height_mm,
                        tag=tags.get(component_id),
                    )
                )
                boxes.append(
                    (left, top, left + manifest.width_mm, top + manifest.height_mm)
                )
                hang(component_id, left, top)
                # Il prossimo della colonna sta sotto questo, non accanto — e
                # sotto anche a cio' che gli pende, corridoio compreso.
                floor = (
                    top
                    + manifest.height_mm
                    + overhang(component_id, PortFace.BOTTOM)
                    + ROW_GAP_MM
                )
            widest = max(footprint_width(item) for item in slot)
            gap = gaps[role][position] if position < len(gaps[role]) else 0.0
            cursor = on_grid(cursor, area.x_mm) + widest + gap
        x_mm += widths[role]
        if position_of[role] < len(gutters):
            x_mm += gutters[position_of[role]]

    # Chi sta sulla tratta si posa **alla fine**, fra i due pezzi grossi che
    # quella tratta unisce (D-120): non ha una colonna, quindi non allarga la
    # fascia, e non ha un posto nel processo, quindi non sposta nessuno. Puo'
    # benissimo trovarsi a cavallo di due zone — e' proprio cio' che il PM
    # chiede.
    settled = {item.component_id: item for item in placed}

    def room_between(first_id: str, second_id: str) -> float:
        """Il rettilineo che vuole la tratta fra due pezzi, se ne esiste una."""
        return max(
            (
                _room_for(trunk.inline_component_ids)
                for trunk in partition.trunks
                if {trunk.start.component_id, trunk.end.component_id}
                == {first_id, second_id}
            ),
            default=0.0,
        )

    def centre_of(component_id: str) -> tuple[float, float] | None:
        item = settled.get(component_id)
        if item is None:
            return None
        return (
            (item.origin.x_mm + item.right_mm) / 2.0,
            (item.origin.y_mm + item.bottom_mm) / 2.0,
        )

    def settle_on_the_run(
        component_id: str,
        centre_x: float,
        centre_y: float,
        along: tuple[float, float],
        forward: int,
    ) -> PlacedSymbol:
        manifest = manifests[component_id]
        left = on_grid(centre_x - manifest.width_mm / 2.0, area.x_mm)
        top = on_grid(centre_y - manifest.height_mm / 2.0, area.y_mm)
        left = min(max(left, area.x_mm), area.right_mm - manifest.width_mm)
        top = min(max(top, area.y_mm), levels.ground_mm - manifest.height_mm)
        # Il posto giusto e' quello; se ci sta gia' qualcuno ci si allontana
        # **in avanti lungo la tubazione**, mai all'indietro: tornare indietro
        # scavalcherebbe il pezzo precedente della catena, e la fila si
        # leggerebbe al contrario. E' successo: cercando il primo posto libero,
        # un raccordo e' finito trenta millimetri **prima** della confluenza che
        # lo precede.
        # Chi sta su una tubazione si allinea **all'attacco che lo alimenta**:
        # e' la regola che toglie due pieghe per pezzo, e vale per un raccordo
        # quanto per una macchina. Solo se quella quota non esiste si tiene
        # quella interpolata lungo la campata.
        aligned = aligned_top(component_id, left, area.y_mm)
        if aligned is not None:
            top = aligned
        base_left, base_top = left, top
        # Avanti lungo la tubazione, che tiene l'ordine della fila; e se avanti
        # non c'e' posto, indietro — **due simboli non si sovrappongono mai**,
        # e un ordine invertito e' un difetto minore di due pezzi disegnati uno
        # sull'altro.
        seated = False
        for direction in (forward, -forward):
            if seated:
                break
            for distance in range(int(max(area.width_mm, area.height_mm) / step)):
                moved_left = base_left + along[0] * distance * direction
                moved_top = base_top + along[1] * distance * direction
                if (
                    moved_left < area.x_mm - 1e-9
                    or moved_left + manifest.width_mm > area.right_mm + 1e-9
                    or moved_top < area.y_mm - 1e-9
                    or moved_top + manifest.height_mm > levels.ground_mm + 1e-9
                ):
                    break
                if free_of_symbols(
                    moved_left, moved_top, manifest.width_mm, manifest.height_mm
                ):
                    left, top, seated = moved_left, moved_top, True
                    break
        if not seated:
            raise LayoutError(
                f"component {component_id} sits on a run and finds no free spot "
                f"along it: symbols are never shrunk to fit, give the run room"
            )
        placed.append(
            PlacedSymbol(
                component_id=component_id,
                symbol_id=manifest.id,
                rotation_deg=rotation_for(component_id),
                origin=Point(x_mm=left, y_mm=top),
                width_mm=manifest.width_mm,
                height_mm=manifest.height_mm,
                tag=tags.get(component_id),
            )
        )
        boxes.append((left, top, left + manifest.width_mm, top + manifest.height_mm))
        settled[component_id] = placed[-1]
        hang(component_id, left, top)
        return placed[-1]

    def chain_rank(item: str) -> int:
        return process.position.get(item, 0)

    for chain in chains:
        ends = [
            place for place in (centre_of(item) for item in chain.anchors)
            if place is not None
        ]
        if len(ends) < 2:
            raise LayoutError(
                f"the run pieces {chain.members} sit between {chain.anchors}, "
                f"which were never placed: a junction needs the pieces it joins"
            )
        # I capi della campata sono i due estremi **piu' lontani**: se una
        # confluenza unisce due macchine affiancate a un accumulo, la campata e'
        # quella che va dalle macchine all'accumulo, non quella fra le due
        # macchine.
        first = min(ends, key=lambda place: (place[0], place[1]))
        last = max(ends, key=lambda place: (place[0], place[1]))
        horizontal = abs(last[0] - first[0]) >= abs(last[1] - first[1])
        along = (step, 0.0) if horizontal else (0.0, step)
        # La catena si percorre dal capo attaccato all'estremo da cui parte la
        # campata, o la fila si legge al contrario.
        members = chain.members
        head_ids = set(chain.head_anchors)
        head = [
            place
            for place in (centre_of(item) for item in sorted(head_ids, key=chain_rank))
            if place is not None
        ]
        if head and min(
            abs(place[0] - first[0]) + abs(place[1] - first[1]) for place in head
        ) > (abs(last[0] - first[0]) + abs(last[1] - first[1])) / 2.0:
            members = tuple(reversed(members))
            head_ids = {
                item for item in chain.anchors if item not in chain.head_anchors
            } or head_ids
        # **La campata si misura sui bordi, non sui centri.** Fra due pompe di
        # calore affiancate il centro della piu' lontana sta dietro l'altra, e
        # la catena partiva da li': il primo raccordo si ritrovava a dieci
        # millimetri dalla macchina, e la valvola di intercettazione della sua
        # tratta non aveva dove sedersi.
        tail_ids = {item for item in chain.anchors if item not in head_ids} or head_ids
        head_placed = [
            settled[item] for item in sorted(head_ids, key=chain_rank) if item in settled
        ]
        tail_placed = [
            settled[item] for item in sorted(tail_ids, key=chain_rank) if item in settled
        ]
        if head_placed and tail_placed:
            first, last = _facing_edges(
                head_placed, tail_placed, horizontal=horizontal
            )
        span_x, span_y = last[0] - first[0], last[1] - first[1]
        # Lo spazio non si divide in parti uguali: si divide **secondo il
        # bisogno**. Ogni tratta della catena porta i propri accessori in linea
        # e vuole il proprio rettilineo; una tratta vuota non vuole niente.
        # Dividere a passi uguali dava dieci millimetri a chi ne chiedeva
        # quindici e quindici a chi non ne chiedeva nessuno, e l'accessorio non
        # trovava dove sedersi.
        sizes = [
            manifests[item].width_mm if horizontal else manifests[item].height_mm
            for item in members
        ]
        stops = (chain.head_anchors, *((item,) for item in members))
        needs = [
            max(
                (room_between(item, other) for item in stops[index] for other in group),
                default=0.0,
            )
            for index, group in enumerate(
                (*((item,) for item in members), tuple(chain.anchors))
            )
        ]
        span_mm = abs(span_x) if horizontal else abs(span_y)
        wanted = sum(sizes) + sum(needs)
        scale = min(1.0, span_mm / wanted) if wanted > 0 else 1.0
        spare = max(0.0, span_mm - wanted) / (len(needs) or 1)
        forward = 1 if (span_x if horizontal else span_y) >= 0 else -1
        cursor = 0.0
        for index, component_id in enumerate(members):
            cursor += needs[index] * scale + spare
            share = (cursor + sizes[index] / 2.0) / span_mm if span_mm else 0.5
            item = settle_on_the_run(
                component_id,
                first[0] + span_x * share,
                first[1] + span_y * share,
                along,
                forward,
            )
            # Il cursore riparte da **dove il pezzo e' finito davvero**, non da
            # dove lo si voleva: se ha dovuto scansare qualcuno, chi viene dopo
            # ne tiene conto invece di ripetere lo scarto.
            reached = (
                (item.right_mm if forward > 0 else -item.origin.x_mm) - first[0] * forward
                if horizontal
                else (item.bottom_mm if forward > 0 else -item.origin.y_mm)
                - first[1] * forward
            )
            cursor = max(cursor + sizes[index] * scale, reached)

    return placed


# ---------------------------------------------------------------------------
# Cio' che il miglioratore legge della posa (DRAW-002)
#
# Il ciclo che rivede la disposizione muove **figure**, non pezzi: chi pende da
# uno stacco viaggia col proprio pezzo, e una catena di raccordi sulla tratta si
# rimette in fila tutta insieme. Le tre letture che gli servono sono le stesse
# con cui questo modulo posa, esposte qui perche' non vengano riscritte in due
# modi diversi.
# ---------------------------------------------------------------------------


def inline_room_mm(
    project: ProjectModel, catalog: ComponentRegistry, inline_ids: tuple[str, ...]
) -> float:
    """Il rettilineo che gli accessori in linea di una tratta pretendono.

    E' lo stesso conto che `inline.py` fara' dopo l'instradamento: ogni
    accessorio vuole la propria interruzione piu' uno stacco dal vicino, e la
    fila intera vuole due stacchi dai componenti agli estremi. Una tratta senza
    accessori non pretende niente.
    """
    accessories = [item for item in project.components if item.id in inline_ids]
    if not accessories:
        return 0.0
    return sum(
        (catalog.resolve(item.definition_id).symbol.manifest.inline_gap_mm or 0.0)
        + 2 * MIN_SPACING_MM
        for item in accessories
    ) + 2 * END_CLEARANCE_MM


def hanging_children(
    project: ProjectModel,
    partition: SheetPartition,
    catalog: ComponentRegistry,
    placeable: frozenset[str],
) -> dict[str, tuple[tuple[str, str], ...]]:
    """Chi pende da uno stacco, per pezzo che lo regge: `(figlio, attacco)`.

    Lo stesso criterio della posa (D-101): chi sta all'altro capo di un attacco
    fuori dal percorso del fluido, e ha un attacco solo, e' un accessorio appeso
    e si muove col proprio pezzo.
    """
    found = _hanging_accessories(
        project, partition, catalog, placeable, lambda _ids: 0.0
    )
    return {
        parent: tuple((item.component_id, item.parent_port_id) for item in items)
        for parent, items in found.items()
    }


def run_chains(
    project: ProjectModel,
    partition: SheetPartition,
    catalog: ComponentRegistry,
    placeable: frozenset[str],
) -> list[tuple[str, ...]]:
    """Le catene di pezzi che stanno sulla tratta fra due pezzi grossi (D-120).

    In ordine di percorrenza, come la posa le legge: un raccordo non e' un passo
    del processo e si rimette in fila con i suoi compagni di tratta.
    """
    functions_of = {
        item.id: frozenset(catalog.resolve(item.definition_id).definition.functions)
        for item in project.components
    }
    hung = frozenset(
        child
        for items in hanging_children(project, partition, catalog, placeable).values()
        for child, _ in items
    )
    rank = _file_order(project)
    chains = _pieces_on_the_run(
        partition,
        placeable,
        hung,
        lambda item: bool(functions_of.get(item, frozenset()) & ZONED_FUNCTIONS),
        lambda item: rank.get(item, 0),
    )
    return [chain.members for chain in chains]
