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

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import ORDINARY_FRAMES, Rect, SheetFrame
from disegnatore_mep.graphics.symbol import PortFace, SymbolManifest
from disegnatore_mep.model.project import PortRef, ProjectModel
from disegnatore_mep.model.types import BandRole

from .composition import Standing, standing_of
from .errors import LayoutError
from .flow import orient_trunks
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

ROW_GAP_MM = 15.0
"""Distanza minima fra due componenti affiancati o sovrapposti.

Sei passi di griglia, cioe' **cinque corsie libere** fra un pezzo e il
successivo. Con cinque millimetri ne restava una sola, e bastavano due tratte
che dovessero passare nello stesso varco — la mandata che scende in un
accumulo e il ritorno che ne risale — perche' una delle due dovesse
sovrapporsi all'altra. Sovrapporsi per il lungo e' vietato, quindi il varco
deve essere largo abbastanza da non costringerci.

**Da dieci a quindici l'8 agosto, e misurato.** Da quando la fascia si piega in
colonne, un pezzo ha vicini **anche sopra e sotto**, e nel varco fra due pezzi
impilati devono passare le tratte di entrambi. Con dieci millimetri nessuno dei
cinque impianti si instradava su una A3; con quindici l'ibrido esce. Non e' un
numero tondo: e' il primo che fa uscire una tavola, e si rivedra' sulle altre.
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

CLEARANCE_STEPS = 2
"""Passi di stacco fra una linea e il bordo del simbolo da cui esce.

Un attacco rivolto in basso scarica su una corsia che deve **staccarsi** dal
riquadro: a un passo solo la linea corre a due millimetri e mezzo dal bordo e
sulla carta sembra disegnata sul simbolo.
"""



# La grammatica di partenza di una centrale idronica (D-119). Il PM:
# «generatori a sinistra, impilati verticalmente se sono piu' di uno; volumi,
# separatori e scambiatori principali subito a destra, anch'essi organizzati
# verticalmente; distribuzione secondaria a destra dei volumi; circuiti
# secondari organizzati verticalmente».
#
# Si legge dal **mestiere che il catalogo dichiara**, mai dal nome di un
# componente (D-069, D-090): sono **posizioni iniziali preferite**, non
# coordinate, e cio' che viene dopo puo' deformarle liberamente.
GRAMMATICA: tuple[tuple[BandRole, frozenset[str]], ...] = (
    (BandRole.GENERATION, frozenset({"heat_generation"})),
    (
        BandRole.PRIMARY,
        frozenset(
            {"thermal_storage", "dhw_storage", "hydraulic_separation", "heat_exchange"}
        ),
    ),
    (
        BandRole.DISTRIBUTION,
        frozenset(
            {
                "circulation",
                "distribution",
                "diversion",
                "circuit_mixing",
                # La miscelatrice sanitaria sta coi circolatori, non coi
                # terminali: e' un organo di regolazione della centrale, non
                # un apparecchio dell'utenza. Detto dal PM l'8 agosto.
                "dhw_mixing",
            }
        ),
    ),
    (BandRole.TERMINAL, frozenset({"emission", "boundary"})),
)
"""Quale fascia chiede ciascun mestiere, da sinistra a destra.

Un componente che porta piu' mestieri prende la fascia **piu' a sinistra** fra
quelle che chiede: un bollitore che scambia e accumula e' un volume, non uno
scambiatore di distribuzione. Chi non porta nessuno di questi mestieri e' un
accessorio, e **segue il pezzo da cui pende**: la sua valvola sta dove sta la
sua macchina, sempre.
"""


def _band_by_subsystem(project: ProjectModel, sheet_id: str) -> dict[str, BandRole]:
    for sheet in project.sheets:
        if sheet.id == sheet_id:
            return {item.subsystem_id: item.band for item in sheet.band_assignments}
    return {}


def _assign_bands(
    project: ProjectModel,
    partition: SheetPartition,
    placeable: list[str],
    catalog: ComponentRegistry,
    definitions: dict[str, str] | None = None,
    anchors_of: dict[str, tuple[str, ...]] | None = None,
) -> dict[str, BandRole]:
    band_of_subsystem = _band_by_subsystem(project, partition.sheet_id)
    definitions = definitions or {item.id: item.definition_id for item in project.components}
    anchors_of = anchors_of or {}
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
    # Senza piano dichiarato, i sottosistemi sono gia' un ordine di lettura:
    # l'i-esimo finisce sull'i-esima fascia.
    if project.subsystems:
        for index, subsystem in enumerate(project.subsystems):
            role = roles[min(index, len(roles) - 1)]
            for component_id in subsystem.component_ids:
                bands[component_id] = role
        for component_id in placeable:
            bands.setdefault(component_id, roles[-1])
        return bands

    # Senza nemmeno i sottosistemi vale la **grammatica** (D-119): la fascia si
    # legge dal mestiere dichiarato in catalogo. Prima, in questo caso, tutti i
    # pezzi finivano nella prima fascia — e un impianto letto davvero
    # dall'interprete i sottosistemi non ce li ha, perche' le sue istruzioni gli
    # ordinano di lasciarli vuoti e nessun pezzo successivo li crea. Quarantacinque
    # pezzi in una fascia sola non sono una disposizione.
    for component_id in placeable:
        mestieri = frozenset(catalog.resolve(definitions[component_id]).definition.functions)
        scelta = next(
            (role for role, chiede in GRAMMATICA if mestieri & chiede), None
        )
        if scelta is not None:
            bands[component_id] = scelta
    # Gli accessori seguono il pezzo da cui pendono: la valvola sta dove sta la
    # sua macchina. Chi resta senza — non ha mestiere di grammatica e non tocca
    # nessuno che ce l'abbia — va con la distribuzione, che e' il mezzo.
    for component_id in placeable:
        if component_id in bands:
            continue
        vicini = [
            bands[other]
            for other in anchors_of.get(component_id, ())
            if other in bands
        ]
        bands[component_id] = min(vicini, key=lambda r: r.reading_order) if vicini else roles[2]
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

        # Chi sbocca dove: serve a riconoscere il **parallelo**. Due macchine
        # che alimentano la stessa cosa sono due rami dello stesso passo del
        # processo, non due passi in fila — e vanno in colonna.
        self.feeds_into: dict[str, str] = {
            source: targets[0]
            for source, targets in successors.items()
            if len(set(targets)) == 1
        }

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
    target_of: dict[str, str] | None = None,
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
    bianca.

    **Due pezzi sono paralleli in due modi, e contano tutti e due:** quando li
    alimenta la stessa cosa (`feeder_of`) e quando **sboccano nella stessa
    cosa** (`target_of`). Il secondo mancava, ed e' il caso piu' comune che
    esista: due generatori in parallelo non hanno nessuno che li alimenti — sono
    loro la sorgente — e si riconoscono solo dal fatto che mandano allo stesso
    raccordo. Senza, due pompe di calore in parallelo finivano affiancate
    qualunque cosa si facesse.

    **E si impila chiunque.** Prima valeva solo per chi sta su una tubazione,
    perche' «due accumuli appoggiati a terra non si possono impilare»: era una
    conseguenza della linea di terra, che e' stata ritirata (D-116). Il PM:
    «basta mettere le due pompe di calore una sopra e una sotto, e stessa cosa
    sui volumi».

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
        vicino = slots[-1][-1] if slots else None
        target = (target_of or {}).get(component_id)
        same_branch = bool(
            vicino
            and stackable.get(component_id, False)
            and stackable.get(vicino, False)
            and (
                (feeder is not None and feeder_of.get(vicino) == feeder)
                or (target is not None and (target_of or {}).get(vicino) == target)
            )
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


FOLD_QUOTAS: tuple[float, ...] = (0.22, 0.28, 0.34, 0.4, 0.45, 0.52, 0.6, 0.7, 0.8)
"""Le pieghe che si provano, dalla piu' bassa e larga alla piu' alta e stretta.

Non c'e' una quota giusta per tutti gli impianti, ed e' stato misurato: a 0,34
il quarto impianto esce e il primo non entra in larghezza; a 0,45 il primo
entra e non si instrada. Sceglierne una sola vuol dire far uscire un impianto e
fermarne un altro — per questo la sceglie **chi compone**, provandole e
tenendo la prima che arriva in fondo (input PM dell'8 agosto §6: «confrontare
poche alternative deterministiche e scegliere quella a costo minore»).
"""


def place_sheet(
    project: ProjectModel,
    partition: SheetPartition,
    catalog: ComponentRegistry,
    frame: SheetFrame,
    inline_component_ids: frozenset[str],
    fold_quota: float | None = None,
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

    # Chi tocca chi: serve alla grammatica per far seguire un accessorio al
    # pezzo da cui pende.
    tocca: dict[str, list[str]] = defaultdict(list)
    for trunk in partition.trunks:
        tocca[trunk.start.component_id].append(trunk.end.component_id)
        tocca[trunk.end.component_id].append(trunk.start.component_id)
    bands = _assign_bands(
        project,
        partition,
        placeable,
        catalog,
        {item.id: item.definition_id for item in project.components},
        {key: tuple(value) for key, value in tocca.items()},
    )
    tags = {item.id: item.tag for item in project.components}
    process = _Process(project, partition, catalog)
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

    def rotation_for(component_id: str) -> int:
        allowed = resolved[component_id].symbol.manifest.allowed_rotations_deg
        return 0 if 0 in allowed else min(allowed)

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
    for component_id in placeable:
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
    # Tutto si impila. Il vecchio «solo chi sta su una tubazione» discendeva
    # dalla linea di terra — chi ci appoggiava non poteva staccarsene — ed e'
    # caduto con lei (D-116).
    stackable = dict.fromkeys(placeable, True)
    linked = frozenset(
        (trunk.start.component_id, trunk.end.component_id)
        if trunk.start.component_id <= trunk.end.component_id
        else (trunk.end.component_id, trunk.start.component_id)
        for trunk in partition.trunks
    )
    heights = {item: manifests[item].height_mm for item in placeable}

    def fold(slot_list: list[list[str]], headroom_mm: float) -> list[list[str]]:
        """Piega una fascia in **colonne**: uno sotto l'altro finche' l'altezza
        basta, poi si va a destra.

        E' la regola del PM, detta con le sue parole: «le macchine si dispongono
        in maniera logica, non con un principio geometrico reale — esempio tutti
        i generatori a sinistra **in colonna**».

        Prima ogni fascia era **una riga sola**: un cursore che avanzava a
        destra e non sapeva che il foglio avesse un'altezza. Su un impianto
        ibrido faceva 538 mm di larghezza contro i 335 di una A3 — mentre i
        simboli coprivano il **sei per cento** del foglio — e costringeva le
        tubazioni a lunghezze senza senso, perche' due pezzi collegati
        finivano a quattrocento millimetri l'uno dall'altro. Lo stesso impianto
        in colonne sta in un terzo della larghezza.

        L'ordine del processo non si perde: le colonne si riempiono **in
        ordine**, quindi da sinistra a destra si continua a leggere il processo,
        e dentro una colonna si scende.
        """
        folded: list[list[str]] = []
        current: list[str] = []
        used = 0.0
        for slot in slot_list:
            tall = sum(heights[item] for item in slot) + ROW_GAP_MM * (len(slot) - 1)
            needed = tall if not current else used + ROW_GAP_MM + tall
            if current and needed > headroom_mm + 1e-9:
                folded.append(current)
                current, used = list(slot), tall
                continue
            current.extend(slot)
            used = needed
        if current:
            folded.append(current)
        return folded

    def pack(
        stacked_ground: frozenset[str],
        headroom_mm: float | None = None,
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

        Con `headroom_mm` le colonne si **piegano** su quell'altezza.
        """
        slots = {
            role: _slots(
                columns[role],
                feeder_of,
                stackable,
                process.feeds_into,
                ground=stacked_ground,
                heights=heights,
                linked=linked,
                headroom_mm=area.height_mm,
            )
            for role in used_roles
        }
        if headroom_mm is not None:
            slots = {
                role: fold(slots[role], headroom_mm) for role in used_roles
            }
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
                    max(manifests[item].width_mm for item in slot)
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
        return slots, gaps, widths, gutters, sum(widths.values()) + sum(gutters)

    slots, gaps, widths, gutters, total = pack(frozenset())
    if total > area.width_mm + 1e-9:
        # Non ci sta in fila: si piega in colonne, che e' come si dispone
        # davvero (D-116).
        #
        # **Si prende la piega piu' STRETTA che entra, non la prima.** Colonne
        # piu' alte fanno una fascia piu' stretta, e cio' che avanza in
        # larghezza sono le corsie in cui passano le tubazioni. Prendendo la
        # prima che entrava — la piu' bassa e larga — l'impianto 1 riempiva
        # tutti e 335 i millimetri utili di una A3 e all'instradatore non
        # restava un varco: «ogni percorso ortogonale e' bloccato».
        quote = (fold_quota,) if fold_quota is not None else FOLD_QUOTAS
        for quota in quote:
            piegate = pack(frozenset(), area.height_mm * quota)
            if piegate[4] <= area.width_mm + 1e-9:
                slots, gaps, widths, gutters, total = piegate
                break
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
                if top + manifest.height_mm > area.bottom_mm + 1e-9:
                    continue
                if not free_of_symbols(left, top, manifest.width_mm, manifest.height_mm):
                    continue
                if not corridor_is_clear(exit_x, left, top + target_y):
                    continue
                return top
        return None

    position_of = {role: index for index, role in enumerate(used_roles)}
    x_mm = area.x_mm
    for role in used_roles:
        cursor = x_mm
        for position, slot in enumerate(slots[role]):
            left = on_grid(cursor, area.x_mm)
            floor = area.y_mm
            for component_id in slot:
                manifest = manifests[component_id]
                # Nessun pezzo e' piu' inchiodato a una quota del foglio: la
                # linea di terra e' ritirata (D-116) e con lei il motivo per cui
                # un accumulo doveva stare **li'** e non altrove. Ogni pezzo
                # cerca la quota che gli toglie due pieghe — quella del proprio
                # alimentatore — e se non la trova scende sotto il precedente
                # della colonna.
                found = aligned_top(component_id, left, floor)
                if found is None:
                    found = on_grid(max(floor, area.y_mm), area.y_mm)
                    while (
                        not free_of_symbols(
                            left, found, manifest.width_mm, manifest.height_mm
                        )
                        and found + manifest.height_mm < area.bottom_mm
                    ):
                        found += ROW_GAP_MM
                if found + manifest.height_mm > area.bottom_mm + 1e-9:
                    # **La colonna e' piena: si apre quella dopo.** Prima il
                    # ripiego spingeva il pezzo in giu' finche' usciva dal
                    # foglio, e la tavola falliva su un foglio quasi vuoto —
                    # e' lo stesso ciclo che prima sfondava la linea di terra.
                    # Una colonna che finisce non e' un errore: e' il momento
                    # di andare a destra, che e' come si riempie un foglio.
                    left = on_grid(
                        left + max(manifests[item].width_mm for item in slot)
                        + ROW_GAP_MM,
                        area.x_mm,
                    )
                    floor = area.y_mm
                    found = aligned_top(component_id, left, floor)
                    if found is None:
                        found = on_grid(area.y_mm, area.y_mm)
                        while (
                            not free_of_symbols(
                                left, found, manifest.width_mm, manifest.height_mm
                            )
                            and found + manifest.height_mm < area.bottom_mm
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
                # **Non una colonna da riempire: un asse di allineamento.**
                # Il PM: «piu' che colonne, immaginiamola come una linea di
                # allineamento dei centri dei simboli». I pezzi di una colonna
                # hanno larghezze diverse — una pompa di calore 40 mm, la sua
                # valvola 5 — e allinearli a sinistra li faceva sembrare
                # appoggiati a un muro invece che infilati sullo stesso asse.
                asse = left + max(manifests[item].width_mm for item in slot) / 2
                centrato = on_grid(asse - manifest.width_mm / 2, area.x_mm)
                placed.append(
                    PlacedSymbol(
                        component_id=component_id,
                        symbol_id=manifest.id,
                        rotation_deg=rotation_for(component_id),
                        origin=Point(x_mm=centrato, y_mm=top),
                        width_mm=manifest.width_mm,
                        height_mm=manifest.height_mm,
                        tag=tags.get(component_id),
                    )
                )
                boxes.append(
                    (
                        centrato,
                        top,
                        centrato + manifest.width_mm,
                        top + manifest.height_mm,
                    )
                )
                # Il prossimo della colonna sta sotto questo, non accanto.
                floor = top + manifest.height_mm + ROW_GAP_MM
            widest = max(manifests[item].width_mm for item in slot)
            gap = gaps[role][position] if position < len(gaps[role]) else 0.0
            cursor = left + widest + gap
        x_mm += widths[role]
        if position_of[role] < len(gutters):
            x_mm += gutters[position_of[role]]

    return placed
