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
    return {key: sorted(value, key=lambda item: item.component_id) for key, value in hanging.items()}


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
                item.id,
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

    def order_of(self, component_id: str) -> tuple[int, int, str]:
        """Piu' e' a valle piu' sta a destra; a pari profondita' prima i rami morti."""
        return (
            self.depth.get(component_id, 0),
            self.downstream.get(component_id, 0),
            component_id,
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
                        ground_top = top
                    else:
                        # La coppia impilata del tentativo di recupero (D-073):
                        # il secondo lascia la terra e sale sopra il primo,
                        # allineato a sinistra, con lo stacco di fascia.
                        top = on_grid(
                            ground_top - ROW_GAP_MM - manifest.height_mm, area.y_mm
                        )
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

    return placed
