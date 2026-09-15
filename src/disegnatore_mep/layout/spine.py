"""La fase del tronco: prima le autostrade, e dritte (DRAW-008 §A).

Il PO, l'11 settembre 2026:

    «Il sistema di instradatura deve prima disegnare le autostrade e farle piu'
    dritte possibile, come ho fatto io a colori. Poi si mettono dentro tutte le
    altre valvole e pezzi, e se non ci stanno le autostrade le puoi allungare,
    stretchare, spostando le macchine principali — sempre pero' mantenendo le
    autostrade dritte.»

**Perche' questo modulo non e' un altro ciclo di costo.** Il ciclo di
`improve.py` e' un greedy globale su un costo lessicografico: ogni proprieta'
del disegno vi e' una voce che si compra e si vende, e la rettilineita' del
tronco vi si trovava o vi si mancava a seconda di dove il greedy partiva
(`docs/pm/2026-09-11-architettura-della-posa-a-fasi.md` §1). Qui il tronco non
si cerca: **si costruisce**. Si cammina lungo l'autostrada da una macchina di
spina e si posa ogni pezzo dove la retta lo vuole — stesso asse della porta di
partenza, distanza pari a quel che il corredo pretende. Non c'e' niente da
ottimizzare perche' non c'e' nessuna alternativa da confrontare: la forma e'
l'esito, non il vincitore.

**Che cosa partecipa.** Le macchine di spina (`hierarchy.spine_machines`) e i
pezzi che stanno **sull'**autostrada, cioe' i capi delle tratte di livello
`Level.AUTOSTRADA` — un raccordo a T, una deviatrice. Tutto il resto — gli
utilizzatori, i generatori oltre il primo, gli appesi, gli stacchi — non
partecipa: lo dispone la posa che viene dopo, attorno a un tronco gia' fermo.

**Che cosa «dritto» vuol dire.** Ogni **tratta** del tronco e' un rettilineo, e
non l'intero tronco una retta sola: dove il tronco si biforca uno dei due rami
resta sull'asse e l'altro se ne stacca, restando a sua volta rettilineo
(architettura §4). Resta sull'asse il ramo che esce dalla porta allineata con
quella d'ingresso del pezzo che biforca; a parita', quello che porta
all'accumulo maggiore.

**Il limite che il catalogo impone, e che qui si dichiara.** Una tratta e'
rettilinea soltanto se le sue due porte si guardano: facce opposte, stesso
asse. La posa di un pezzo pero' serve **tutte** le sue porte insieme: l'uscita
secondaria di una deviatrice non puo' voltarsi senza che si volti anche quella
principale, e se la principale tiene l'asse verso l'accumulo maggiore — come
l'architettura §4 dispone — la secondaria resta dov'e'. Quando in quella
situazione la porta dall'altra parte non ammette nessuna posa che la guardi in
faccia — la serpentina di un bollitore che si imbocca da sinistra, e il
bollitore non si gira — la tratta **non puo'** essere rettilinea, e non e' un
difetto della posa. `unstraightenable_runs` calcola quelle tratte e le nomina,
cosi' che la misura sappia distinguere «non e' dritta» da «non poteva esserlo».
"""

from collections import deque
from dataclasses import dataclass
from itertools import permutations

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import FITTING_FUNCTIONS
from disegnatore_mep.graphics.frame import Rect, SheetFrame
from disegnatore_mep.graphics.symbol import PortFace, SymbolManifest
from disegnatore_mep.model.order import structural_order
from disegnatore_mep.model.project import ProjectModel

from .errors import LayoutError
from .flow import STORE_FUNCTIONS, TrunkKey
from .geometry import PlacedSymbol, Point, RoutedTrunk
from .grid import GridSpace
from .hierarchy import Level, hierarchy_of, spine_machines
from .partition import SheetPartition
from .place import (
    ROUTING_MARGIN_MM,
    ROW_GAP_MM,
    boundary_faces_the_plant,
    chain_room_of_port_mm,
    hanging_children,
    hanging_ports,
    inline_room_mm,
)
from .route import route_sheet
from .trunks import Trunk

_TOLERANCE_MM = 1e-6

_RELIEF_STEPS = 40
"""Passi di griglia concessi per allontanare due pezzi sovrapposti.

Un tetto, non un obiettivo: la compattazione si ferma qui e dichiara cio' che
non ha risolto, invece di camminare fuori dal foglio.
"""

_RELIEF_ROUNDS = 200
"""Quante coppie la compattazione prova a separare, in tutto.

Ogni giro chiude una coppia o la mette da parte come irriducibile, e una mossa
puo' avvicinarne un'altra: il tetto e' generoso perche' il lavoro e' finito
quando non resta niente da separare, non dopo un numero di giri deciso a
tavolino. Serve solo perche' un ciclo che si rincorre finisca.
"""

_HORIZONTAL_FACES = (PortFace.LEFT, PortFace.RIGHT)

_DIRECTION: dict[PortFace, tuple[float, float]] = {
    PortFace.RIGHT: (1.0, 0.0),
    PortFace.BOTTOM: (0.0, 1.0),
    PortFace.LEFT: (-1.0, 0.0),
    PortFace.TOP: (0.0, -1.0),
}

PortMap = dict[str, str]
Pose = tuple[int, tuple[tuple[str, str], ...]]
"""Una rotazione e una permutazione degli attacchi, come chiave ordinabile."""


@dataclass(frozen=True)
class SpineRun:
    """Una tratta dell'autostrada, com'e' uscita dalla fase del tronco."""

    key: TrunkKey
    horizontal: bool
    """Giacitura della retta che unisce le due porte."""

    straight: bool
    """Vero se la tratta e' un rettilineo: una spezzata sola, senza pieghe."""

    possible: bool
    """Vero se le due porte si guardano nelle pose che la fase ha scelto.

    Falso vuol dire che, **dato il resto del tronco**, nessuna posa ammessa del
    pezzo a valle mette la sua porta di fronte a quella da cui si arriva: la
    tratta sara' un gomito, e non per un difetto della posa.
    """


@dataclass(frozen=True)
class SpineLayout:
    """L'esito della fase del tronco: la forma, e chi vi ha partecipato.

    `symbols` porta **soltanto** i partecipanti e `routes` **soltanto** le
    autostrade: e' la geometria della fase, non della tavola. Chi la riceve la
    usa come vincolo, non come disegno.
    """

    machines: frozenset[str]
    participants: tuple[str, ...]
    trunks: tuple[Trunk, ...]
    symbols: tuple[PlacedSymbol, ...]
    routes: tuple[RoutedTrunk, ...]
    runs: tuple[SpineRun, ...]

    @property
    def crooked(self) -> tuple[TrunkKey, ...]:
        """Le autostrade che sono uscite con almeno una piega."""
        return tuple(run.key for run in self.runs if not run.straight)

    @property
    def impossible(self) -> tuple[TrunkKey, ...]:
        """Le autostrade che, dato il resto del tronco, nessuna posa raddrizza."""
        return tuple(run.key for run in self.runs if not run.possible)

    @property
    def is_straight(self) -> bool:
        """Vero se ogni autostrada che poteva essere rettilinea lo e'."""
        return all(run.straight or not run.possible for run in self.runs)


def autostrada_trunks(
    project: ProjectModel, catalog: ComponentRegistry, trunks: list[Trunk]
) -> list[Trunk]:
    """Le sole tratte di livello autostrada, nell'ordine della partizione."""
    levels = hierarchy_of(project, catalog, trunks)
    return [item for item in trunks if levels[item.connection_ids] is Level.AUTOSTRADA]


def spine_participants(
    project: ProjectModel, catalog: ComponentRegistry, trunks: list[Trunk]
) -> frozenset[str]:
    """Chi partecipa alla fase del tronco.

    Le macchine di spina **e** i capi delle autostrade: un raccordo a T o una
    deviatrice non sono macchine, ma stanno sul tronco e la sua forma passa da
    loro. Cio' che non compare qui non partecipa: si posa dopo, attorno a un
    tronco fermo.
    """
    machines = spine_machines(project, catalog)
    ends = {
        ref.component_id
        for trunk in autostrada_trunks(project, catalog, trunks)
        for ref in (trunk.start, trunk.end)
    }
    return frozenset(machines | ends)


def _faces_of(manifest: SymbolManifest, port_map: PortMap, port_id: str) -> PortFace:
    return manifest.port(port_map.get(port_id, port_id)).face


def _admitted_poses(
    catalog: ComponentRegistry, definition_id: str, upright: SymbolManifest
) -> list[Pose]:
    """Le pose che il catalogo e il simbolo ammettono per un pezzo del tronco.

    Le rotazioni sono quelle del manifesto. Le permutazioni degli attacchi
    esistono solo per un **raccordo** — lo dice la funzione dichiarata dal
    catalogo (D-069) — con almeno tre attacchi tutti dello stesso dominio e
    fluido: un raccordo si disegna come un punto e ogni suo attacco vale
    l'altro. In una deviatrice, in una miscelatrice o in un collettore ogni
    porta ha un ruolo e scambiarle cambierebbe l'impianto, non il disegno.
    """
    definition = catalog.get(definition_id)
    maps: list[PortMap] = [{}]
    ports = [(port.id, f"{port.domain}:{port.medium}") for port in definition.ports]
    ids = [port_id for port_id, _ in ports]
    if (
        frozenset(definition.functions) & FITTING_FUNCTIONS
        and len(ids) >= 3
        and len({kind for _, kind in ports}) == 1
        and all(port_id in upright.port_ids for port_id in ids)
    ):
        for order in permutations(ids):
            mapping = {
                mine: physical
                for mine, physical in zip(ids, order, strict=True)
                if mine != physical
            }
            if mapping:
                maps.append(mapping)
    out: list[Pose] = []
    seen: set[tuple[tuple[str, PortFace], ...]] = set()
    for degrees in sorted(upright.allowed_rotations_deg):
        shape = upright.rotated(degrees)
        for port_map in maps:
            signature = tuple(
                (port.id, _faces_of(shape, port_map, port.id)) for port in upright.ports
            )
            if signature in seen:
                continue
            seen.add(signature)
            out.append((degrees, tuple(sorted(port_map.items()))))
    return out


@dataclass(frozen=True)
class _Same:
    """Due pezzi che una retta obbliga alla stessa coordinata, a meno di uno
    scarto fisso: e' la retta stessa, scritta come vincolo."""

    here: str
    there: str
    delta: float


@dataclass(frozen=True)
class _Apart:
    """Una campata: `high` sta almeno `gap` oltre `low` su quell'asse."""

    low: str
    high: str
    gap: float


@dataclass(frozen=True)
class _AxisDemands:
    """Quel che un asse pretende, tenuto da parte dopo averlo risolto.

    `leader` dice, per ogni pezzo, il gruppo che una retta gli impone: chi sta
    sulla stessa retta dell'altro asse ha lo stesso capo e su questo asse non
    puo' muoversi da solo senza piegarla. `within` e' lo scarto di ciascuno
    dentro il proprio gruppo, e `apart` sono le campate.
    """

    leader: dict[str, str]
    within: dict[str, float]
    apart: tuple["_Apart", ...]


def _apart(
    here: str, there: str, face: PortFace, mine: float, its: float, span: float
) -> _Apart:
    """La campata che una tratta chiede lungo il proprio asse.

    Il verso lo dice la faccia della porta di partenza: chi esce a destra o in
    basso vuole il proprio pari **oltre**, chi esce a sinistra o in alto lo
    vuole prima. Lo scarto delle due porte dall'origine dei rispettivi simboli
    entra nel conto, perche' la campata si misura fra le porte e la coordinata
    che si risolve e' quella dell'origine.
    """
    direction = _DIRECTION[face]
    if direction[0] + direction[1] > 0:
        return _Apart(low=here, high=there, gap=span + mine - its)
    return _Apart(low=there, high=here, gap=span + its - mine)


class _Spine:
    """Il costruttore del tronco: legge il catalogo, cammina, posa.

    Vive il tempo di una chiamata a `lay_the_spine`. Sta in una classe e non in
    una funzione sola perche' la camminata ha bisogno di tre letture — il
    manifesto girato, la porta posata, la campata che il corredo pretende — e
    passarsele come argomenti renderebbe illeggibile il cuore, che e' breve.
    """

    def __init__(
        self,
        project: ProjectModel,
        partition: SheetPartition,
        catalog: ComponentRegistry,
        frame: SheetFrame,
        placed: list[PlacedSymbol],
    ) -> None:
        self.project = project
        self.catalog = catalog
        self.partition = partition
        self.trunks = list(partition.trunks)
        self.levels = hierarchy_of(project, catalog, self.trunks)
        self.autostrade = [
            item
            for item in self.trunks
            if self.levels[item.connection_ids] is Level.AUTOSTRADA
        ]
        self.machines = spine_machines(project, catalog)
        self.start: dict[str, PlacedSymbol] = {
            item.component_id: item for item in placed
        }
        self.participants = tuple(
            item.component_id
            for item in placed
            if item.component_id
            in spine_participants(project, catalog, self.trunks)
        )
        self.definitions = {
            item.id: item.definition_id for item in project.components
        }
        drawing = frame.drawing_rect_mm
        self.area = Rect(
            x_mm=drawing.x_mm + ROUTING_MARGIN_MM,
            y_mm=drawing.y_mm + ROUTING_MARGIN_MM,
            width_mm=drawing.width_mm - 2 * ROUTING_MARGIN_MM,
            height_mm=drawing.height_mm - 2 * ROUTING_MARGIN_MM,
        )
        self.grid = GridSpace(origin=drawing, standard=frame.standard)
        self.step = self.grid.step_mm
        self.upright = {
            item: catalog.resolve(self.definitions[item]).symbol.manifest
            for item in self.participants
        }
        self.poses = {
            item: _admitted_poses(catalog, self.definitions[item], self.upright[item])
            for item in self.participants
        }
        self.room = {
            trunk.connection_ids: inline_room_mm(
                project, catalog, trunk.inline_component_ids
            )
            for trunk in self.autostrade
        }
        # Quanto il disegno intero occupa nella prima ipotesi di posa, sui due
        # assi, e quanto la compattazione l'ha gia' allargato. Non sono i soli
        # partecipanti: chi li segue esce dal foglio con loro, e la tratta di
        # un utilizzatore finito oltre il bordo non si instrada. Serve a
        # scegliere **da che parte** allargare: la tavola 2 ha 335 mm di
        # larghezza occupata su 350 e settantacinque millimetri di altezza su
        # 235, quindi lo stesso stacco costa il foglio in orizzontale e non
        # costa niente in verticale.
        self.spread = (
            max(item.right_mm for item in placed)
            - min(item.origin.x_mm for item in placed),
            max(item.bottom_mm for item in placed)
            - min(item.origin.y_mm for item in placed),
        ) if placed else (0.0, 0.0)
        self.grown = [0.0, 0.0]
        self.order = structural_order(project)
        self._turned: dict[tuple[str, int], SymbolManifest] = {}
        self.pose: dict[str, Pose] = {}
        self.laid: dict[str, PlacedSymbol] = {}
        # Per ogni autostrada, se le sue due porte si guardano nelle pose che
        # la camminata ha scelto. E' la domanda che separa «questa tratta e'
        # venuta storta» da «questa tratta non poteva venire dritta»: la posa
        # di un pezzo serve **tutte** le sue porte, e l'uscita secondaria di
        # una deviatrice non puo' voltarsi senza che si volti anche quella
        # principale.
        self.facing: dict[TrunkKey, bool] = {}
        # Da che parte se n'e' staccato il ramo a cui un pezzo appartiene.
        # Lo decide la **biforcazione**: se la seconda uscita della deviatrice
        # guarda in basso, il bollitore e tutto cio' che gli sta dietro stanno
        # in basso, e il raccordo di ritorno deve aspettarseli da li'. Senza
        # questa memoria il ritorno del bollitore rientrava dall'alto e la
        # tavola 2 chiedeva due pieghe per tornare indietro.
        self.side: dict[str, PortFace] = {}
        # Da che parte sta «fuori dal tronco» per ciascun pezzo. Lo decide la
        # macchina di spina da cui la corsia parte: fra le sue porte di
        # autostrada, la mandata e il ritorno stanno una sopra l'altra, e per
        # chi sta sulla corsia bassa il fuori e' in basso. Serve agli **stacchi
        # di servizio**: un manometro appeso a un raccordo del ritorno che si
        # alza attraversa la mandata, e la mandata e' un'autostrada. Ai rami di
        # distribuzione no: quelli vanno dove sta la loro macchina.
        self.away: dict[str, PortFace] = {}

    # -- letture -------------------------------------------------------------

    def manifest(self, component_id: str, rotation_deg: int) -> SymbolManifest:
        found = self._turned.get((component_id, rotation_deg))
        if found is None:
            found = self.upright[component_id].rotated(rotation_deg)
            self._turned[component_id, rotation_deg] = found
        return found

    def face(self, component_id: str, pose: Pose, port_id: str) -> PortFace:
        degrees, port_map = pose
        return _faces_of(self.manifest(component_id, degrees), dict(port_map), port_id)

    def offset(self, component_id: str, pose: Pose, port_id: str) -> tuple[float, float]:
        """Dove sta la porta rispetto all'origine del simbolo, in quella posa."""
        degrees, port_map = pose
        port = self.manifest(component_id, degrees).port(
            dict(port_map).get(port_id, port_id)
        )
        return (port.x_mm, port.y_mm)

    def port_at(self, item: PlacedSymbol, port_id: str) -> tuple[Point, PortFace]:
        port = self.manifest(item.component_id, item.rotation_deg).port(
            item.physical_port(port_id)
        )
        return (
            Point(x_mm=item.origin.x_mm + port.x_mm, y_mm=item.origin.y_mm + port.y_mm),
            port.face,
        )

    def span_mm(self, trunk: Trunk, horizontal: bool = True) -> float:
        """La campata che questa tratta pretende fra le due porte.

        Tre cose la decidono, e si prende la piu' grande: il rettilineo che i
        suoi accessori in linea occuperanno, lo stacco minimo fra due simboli
        (D-062), e **il rettilineo che la catena di macchina pretende davanti a
        ciascuna delle due porte** (I-044). L'ultimo non e' un dettaglio: e'
        quello che l'instradatore imporra' uscendo dalla porta, e una campata
        che non lo conta consegna una posa in cui la tratta non si instrada —
        con una diagnostica che parla di un ostacolo, non di una campata corta.

        E' anche il numero che la fase del corredo allunghera' se il conto
        risultera' stretto: il tronco si allunga, non si piega (§B.2).
        """
        catene = max(
            chain_room_of_port_mm(
                self.project, self.catalog, self.trunks, ref, horizontal
            )
            for ref in (trunk.start, trunk.end)
        )
        if catene > 0:
            # La cella in cui la tratta gira e il bordo del vicino che conta
            # come cella occupata: due passi in piu', come nella posa.
            catene += 2 * self.step
        want = max(ROW_GAP_MM, self.room.get(trunk.connection_ids, 0.0), catene)
        steps = int(want / self.step)
        if want - steps * self.step > _TOLERANCE_MM:
            steps += 1
        return steps * self.step

    def placed(self, component_id: str, origin: Point, pose: Pose) -> PlacedSymbol:
        degrees, port_map = pose
        shape = self.manifest(component_id, degrees)
        return self.start[component_id].model_copy(
            update={
                "origin": origin,
                "rotation_deg": degrees,
                "width_mm": shape.width_mm,
                "height_mm": shape.height_mm,
                "port_map": dict(port_map),
            }
        )

    # -- la camminata --------------------------------------------------------

    def _edges(self) -> dict[str, list[tuple[Trunk, str, str, str]]]:
        """Da ogni partecipante, le autostrade che ne escono."""
        out: dict[str, list[tuple[Trunk, str, str, str]]] = {}
        for trunk in self.autostrade:
            for mine, other in ((trunk.start, trunk.end), (trunk.end, trunk.start)):
                if mine.component_id == other.component_id:
                    continue
                out.setdefault(mine.component_id, []).append(
                    (trunk, mine.port_id, other.component_id, other.port_id)
                )
        return out

    def _all_edges(self) -> dict[str, list[tuple[TrunkKey, str, str]]]:
        """Da ogni partecipante, **tutte** le tratte che ne escono: anche quelle
        che il tronco non e', perche' e' dove vanno i loro stacchi che decide se
        una tubazione di servizio attraversera' un'autostrada."""
        out: dict[str, list[tuple[TrunkKey, str, str]]] = {}
        for trunk in self.trunks:
            for mine, other in ((trunk.start, trunk.end), (trunk.end, trunk.start)):
                if mine.component_id not in self.start:
                    continue
                out.setdefault(mine.component_id, []).append(
                    (trunk.connection_ids, mine.port_id, other.component_id)
                )
        return out

    def _root(self) -> str:
        """Da dove si comincia a camminare: la macchina che genera.

        E' il capo dell'asse principale — «la macchina principale» del PO — e
        quando non ce n'e' una sulla spina si parte dall'accumulo maggiore. A
        parita' decide lo spareggio strutturale, mai l'identificativo.
        """
        machines = [item for item in self.participants if item in self.machines]
        if not machines:
            return self.participants[0]
        stores = frozenset(STORE_FUNCTIONS)
        generators = [
            item
            for item in machines
            if not frozenset(self.catalog.get(self.definitions[item]).functions) & stores
        ]
        pool = generators or machines
        return min(pool, key=lambda item: (self.order.get(item, 0), item))

    def _size_of(self, component_id: str) -> float:
        manifest = self.upright[component_id]
        return manifest.width_mm * manifest.height_mm

    def _rank_of_branch(
        self, edges: dict[str, list[tuple[Trunk, str, str, str]]], origin: str, first: str
    ) -> tuple[float, int]:
        """Quanto «pesa» il ramo che si imbocca: l'accumulo maggiore che porta.

        Si cammina oltre il primo pezzo e **ci si ferma sulla prima macchina**,
        come fa la gerarchia: su un circuito chiuso il cammino a valle rientra
        su se' stesso, e un conto che non si fermasse darebbe a ogni ramo lo
        stesso peso — e' la primitiva sbagliata che `hierarchy.py` ha gia'
        scartato una volta. Fra le macchine che si incontrano vince la piu'
        grande, e l'ingombro lo dichiara il simbolo: e' la traduzione di «resta
        sull'asse il ramo verso l'accumulo maggiore» (architettura §4), e il
        criterio e' un dato, mai un nome.
        """
        seen = {origin, first}
        frontier = [first]
        biggest = 0.0
        while frontier:
            onward: list[str] = []
            for item in frontier:
                if item in self.machines:
                    biggest = max(biggest, self._size_of(item))
                    continue
                for _, _, other, _ in edges.get(item, ()):
                    if other in seen:
                        continue
                    seen.add(other)
                    onward.append(other)
            frontier = onward
        return (-biggest, self.order.get(first, 0))

    def _walk(self, root: str) -> None:
        """Prima passata: sceglie le pose e decide su che retta sta ogni tratta.

        L'ordine e' una visita in ampiezza, e a ogni biforcazione si serve
        **prima** il ramo che resta sull'asse: quello la cui porta d'uscita e'
        allineata con la porta d'ingresso del pezzo che biforca, e a parita'
        quello che porta all'accumulo maggiore (architettura §4). Cosi' il ramo
        che se ne stacca trova l'asse gia' deciso e ci si appende, invece di
        contenderselo.

        Qui non si fissa nessuna coordinata: si sceglie per ogni pezzo la posa
        che gli fa **guardare in faccia** la porta da cui si arriva — quella
        attuale se gia' va bene, cosi' che la fase non giri i pezzi senza
        motivo — e si annota la tratta come orizzontale, verticale o a gomito.
        Le coordinate le decide la seconda passata, che e' l'unica a sapere
        quanto lungo dev'essere l'insieme.
        """
        edges = self._edges()
        self.pose[root] = self._pose_of(root)
        arrived: dict[str, str] = {}
        queue: deque[str] = deque([root])
        seen = {root}
        while queue:
            here = queue.popleft()
            outgoing = sorted(
                edges.get(here, ()),
                key=lambda edge: (
                    not self._on_the_axis(here, edge[1], arrived.get(here)),
                    self._rank_of_branch(edges, here, edge[2]),
                    self.order.get(edge[2], 0),
                ),
            )
            for _trunk, my_port, other, other_port in outgoing:
                if other in seen:
                    continue
                seen.add(other)
                if self._on_the_axis(here, my_port, arrived.get(here)):
                    inherited = self.side.get(here)
                    if inherited is not None:
                        self.side[other] = inherited
                else:
                    self.side[other] = self.face(here, self.pose[here], my_port)
                outward = self._outward_of(here, my_port) or self.away.get(here)
                if outward is not None:
                    self.away[other] = outward
                self.pose[other] = self._pose_facing(here, my_port, other, other_port)
                arrived[other] = other_port
                queue.append(other)
        for item in self.participants:
            if item not in self.pose:
                # Un partecipante che l'autostrada non raggiunge: tiene la posa
                # che la prima ipotesi gli aveva dato.
                self.pose[item] = self._pose_of(item)

    def _on_the_axis(self, component_id: str, port_id: str, arrival: str | None) -> bool:
        """Vero se questa porta prosegue la retta con cui si e' arrivati."""
        if arrival is None:
            return True
        pose = self.pose[component_id]
        here = self.offset(component_id, pose, port_id)
        there = self.offset(component_id, pose, arrival)
        face = self.face(component_id, pose, arrival)
        if face in _HORIZONTAL_FACES:
            return abs(here[1] - there[1]) <= _TOLERANCE_MM
        return abs(here[0] - there[0]) <= _TOLERANCE_MM

    def _pose_of(self, component_id: str) -> Pose:
        current = self.start[component_id]
        return (current.rotation_deg, tuple(sorted(current.port_map.items())))

    def _outward_of(self, here: str, port_id: str) -> PortFace | None:
        """Da che parte sta «fuori dal tronco», guardando questa porta.

        Fra le porte di autostrada dello stesso pezzo che escono sullo stesso
        asse, chi sta piu' in la' sulla trasversale ha il fuori dalla propria
        parte: sulla pompa di calore la mandata esce in alto e il ritorno in
        basso, quindi per la corsia del ritorno il fuori e' in basso. Dove il
        pezzo ha una porta di autostrada sola non c'e' niente da dire, e la
        risposta e' `None`: la decide chi sta a monte.
        """
        pose = self.pose[here]
        face = self.face(here, pose, port_id)
        across = 1 if face in _HORIZONTAL_FACES else 0
        mine = self.offset(here, pose, port_id)[across]
        others = [
            self.offset(here, pose, edge[1])[across]
            for edge in self._edges().get(here, ())
            if edge[1] != port_id
            and self.face(here, pose, edge[1]) in (face, face.opposite)
        ]
        if not others:
            return None
        if all(mine > item + _TOLERANCE_MM for item in others):
            return PortFace.BOTTOM if across == 1 else PortFace.RIGHT
        if all(mine < item - _TOLERANCE_MM for item in others):
            return PortFace.TOP if across == 1 else PortFace.LEFT
        return None

    def _pose_facing(self, here: str, my_port: str, other: str, other_port: str) -> Pose:
        """La posa che fa guardare in faccia la porta da cui si arriva.

        Fra quelle che ci riescono vince chi **prosegue diritto**: un raccordo
        del tronco riceve da una parte e riparte dall'altra, e il ramo che se
        ne stacca prende cio' che resta. Senza questa preferenza il raccordo di
        ritorno della tavola 2 metteva l'uscita verso la pompa di calore sulla
        faccia superiore e mandava la corsia principale a girare: una posa che
        soddisfa la tratta da cui si arriva e rovina le due che ne escono.

        L'ordine dei rami e' quello dell'architettura §4 — prima quello che
        porta all'accumulo maggiore — e a parita' si tiene la posa attuale,
        cosi' che la fase non giri i pezzi senza bisogno. Se nessuna posa
        ammessa guarda in faccia la porta di arrivo, la coppia non ammette un
        rettilineo: si tiene la posa attuale e `SpineRun.possible` lo dira'.
        """
        edges = self._edges()
        wanted = self.face(here, self.pose[here], my_port).opposite
        current = self._pose_of(other)
        onward = sorted(
            (item for item in edges.get(other, ()) if item[1] != other_port),
            key=lambda edge: (
                self._rank_of_branch(edges, other, edge[2]),
                self.order.get(edge[2], 0),
            ),
        )

        outward = self.away.get(other)
        stubs = [
            edge[1]
            for edge in sorted(self._all_edges().get(other, ()))
            if self.levels.get(edge[0]) is Level.SERVIZIO
        ]

        def score(pose: Pose) -> tuple[bool, tuple[bool, ...], int, bool]:
            arrival = self.face(other, pose, other_port)
            return (
                arrival is not wanted,
                tuple(
                    self.face(other, pose, edge[1])
                    is not (self.side.get(edge[2]) or arrival.opposite)
                    for edge in onward
                ),
                0
                if outward is None
                else sum(
                    self.face(other, pose, port) is not outward for port in stubs
                ),
                pose != current,
            )

        best = min(self.poses[other], key=score)
        return best if self.face(other, best, other_port) is wanted else current

    # -- la seconda passata: le rette, risolte insieme ------------------------

    def _demands(self) -> tuple[list["_Same"], list["_Apart"], list["_Same"], list["_Apart"]]:
        """Cosa ogni tratta pretende dai due assi, letto sulle pose scelte.

        Una tratta orizzontale chiede **la stessa quota** ai suoi due capi — e'
        la retta — e chiede all'asse x una **distanza minima**, che e' la
        campata del corredo. Una verticale chiede le due cose scambiate. Una
        tratta a gomito, che nessuna posa raddrizza, non chiede nessuna
        uguaglianza e chiede una distanza minima su tutti e due gli assi: e'
        una elle, e le due mete stanno l'una oltre l'altra su tutti e due i
        versi.
        """
        same_x: list[_Same] = []
        same_y: list[_Same] = []
        apart_x: list[_Apart] = []
        apart_y: list[_Apart] = []

        def demand(item: "_Apart", index: int) -> None:
            (apart_x if index == 0 else apart_y).append(item)

        for trunk in self.autostrade:
            here, there = trunk.start.component_id, trunk.end.component_id
            if here == there:
                continue
            my_pose, its_pose = self.pose[here], self.pose[there]
            my_face = self.face(here, my_pose, trunk.start.port_id)
            its_face = self.face(there, its_pose, trunk.end.port_id)
            mine = self.offset(here, my_pose, trunk.start.port_id)
            its = self.offset(there, its_pose, trunk.end.port_id)
            along = 0 if my_face in _HORIZONTAL_FACES else 1
            across = 1 - along
            span = self.span_mm(trunk, along == 0)
            self.facing[trunk.connection_ids] = its_face is my_face.opposite
            if its_face is my_face.opposite:
                same = _Same(here, there, mine[across] - its[across])
                (same_y if along == 0 else same_x).append(same)
                demand(_apart(here, there, my_face, mine[along], its[along], span), along)
                continue
            theirs = 0 if its_face in _HORIZONTAL_FACES else 1
            if theirs == along:
                # Due porte che guardano dalla **stessa** parte: la spezzata
                # esce, gira due volte e rientra. Sul loro asse non c'e' niente
                # da imporre — qualunque ordine va bene — e sull'altro serve
                # invece che non stiano sulla stessa riga, o le due corsie si
                # sovrapporrebbero per il lungo. L'ordine di traverso e' quello
                # che la prima ipotesi di posa gia' aveva.
                low, high = here, there
                if self._starts_after(here, there, across):
                    low, high = there, here
                demand(_Apart(low=low, high=high, gap=span), across)
                continue
            # Il gomito: una distanza minima lungo il mio asse e una lungo il
            # suo, cosi' che la spezzata giri una volta sola e poi entri dritta.
            # Ciascuna chiede la campata **del proprio asse**: il rettilineo che
            # una catena di macchina pretende non e' lo stesso in orizzontale e
            # in verticale, e chiederlo una volta sola per tutt'e due avrebbe
            # dato a una delle due meno di quel che l'instradatore le imporra'.
            demand(_apart(here, there, my_face, mine[along], its[along], span), along)
            demand(
                _apart(
                    there,
                    here,
                    its_face,
                    its[theirs],
                    mine[theirs],
                    self.span_mm(trunk, theirs == 0),
                ),
                theirs,
            )
        return (same_x, apart_x, same_y, apart_y)

    def _starts_after(self, here: str, there: str, index: int) -> bool:
        """Vero se nella prima ipotesi di posa `here` sta oltre `there`."""
        mine = self.start[here].origin
        its = self.start[there].origin
        return (mine.x_mm, mine.y_mm)[index] > (its.x_mm, its.y_mm)[index]

    def _fits_the_sheet(self, values: dict[str, float], index: int) -> bool:
        """Vero se, con quelle coordinate, il disegno intero sta nel foglio.

        Intero vuol dire **anche chi non partecipa**: il tronco si sposta e il
        resto lo segue, e a uscire dal bordo e' quasi sempre chi sta in fondo a
        una fila, non una macchina di spina. Il conto rifa' la stessa lettura di
        `carry_the_rest` — chi tocca un partecipante prende la sua traslazione —
        sulla prima ipotesi di posa.
        """
        root = self._root()
        base = self.start[root].origin
        anchor = values[root]
        start = (base.x_mm, base.y_mm)[index]
        delta: dict[str, tuple[float, float]] = {}
        for item in self.participants:
            here = self.start[item].origin
            shift = start + values[item] - anchor - (here.x_mm, here.y_mm)[index]
            delta[item] = (shift, 0.0) if index == 0 else (0.0, shift)
        following = _followers(self.partition, frozenset(self.start), delta)
        low: float | None = None
        high: float | None = None
        for item, placed in self.start.items():
            move = delta.get(item) or following.get(item) or (0.0, 0.0)
            shift = move[index]
            near = (placed.origin.x_mm, placed.origin.y_mm)[index] + shift
            far = (placed.right_mm, placed.bottom_mm)[index] + shift
            low = near if low is None else min(low, near)
            high = far if high is None else max(high, far)
        if low is None or high is None:
            return True
        size = (self.area.width_mm, self.area.height_mm)[index]
        return high - low <= size + _TOLERANCE_MM

    def _solve_axis(
        self,
        same: list["_Same"],
        apart: list["_Apart"],
        index: int,
        compact: bool = False,
    ) -> dict[str, float]:
        """Le coordinate di un asse, risolte tutte insieme.

        Le uguaglianze — le rette dell'altro asse — legano i pezzi in **gruppi**
        che si muovono insieme: un pezzo non puo' scendere senza portarsi dietro
        chi sta sulla sua stessa retta orizzontale. Le disuguaglianze sono le
        campate, e si risolvono come un cammino piu' lungo sul grafo dei gruppi:
        e' cosi' che la mandata e il ritorno, che uniscono le stesse due
        macchine passando per un numero diverso di raccordi, si accordano sulla
        distanza **senza** che nessuno dei due si pieghi. La piu' lunga delle due
        file decide, e l'altra resta larga: e' lo stretch, prima ancora che una
        mossa lo chieda.

        Fra tutte le soluzioni che rispettano i vincoli si sceglie **quella piu'
        vicina alla prima ipotesi di posa**. Non e' un dettaglio: la fase deve
        raddrizzare il tronco, non riscrivere la tavola, e una soluzione «tutto
        a sinistra» sposterebbe di mezzo foglio pezzi che stavano bene dov'erano
        — portandosi dietro il corredo, gli stacchi e le zone.
        """
        leader, within = self._grouped(same)

        def root(item: str) -> str:
            return leader[item]

        groups: dict[str, list[str]] = {}
        for item in self.participants:
            groups.setdefault(root(item), []).append(item)
        edges = [
            (root(link.low), root(link.high), link.gap + within[link.low] - within[link.high])
            for link in apart
            if root(link.low) != root(link.high)
        ]
        earliest = self._earliest(groups, edges)
        order = None if compact else self._ordered(groups, edges)
        if order is None:
            return {item: earliest[root(item)] + within[item] for item in self.participants}
        wanted = {
            name: sum(
                (self.start[item].origin.x_mm, self.start[item].origin.y_mm)[index]
                - within[item]
                for item in members
            )
            / len(members)
            for name, members in groups.items()
        }
        # L'orizzonte comprende **anche** dove i pezzi vorrebbero stare: un
        # orizzonte fissato sulla sola soluzione compatta incollerebbe l'ultimo
        # gruppo al proprio minimo, e con lui mezza tavola.
        horizon = max(
            max(earliest.values(), default=0.0), max(wanted.values(), default=0.0)
        )
        latest = self._latest(groups, edges, horizon)
        position: dict[str, float] = {}
        outgoing: dict[str, list[tuple[str, float]]] = {}
        for low, high, gap in edges:
            outgoing.setdefault(high, []).append((low, gap))
        for name in order:
            floor = max(
                (position[low] + gap for low, gap in outgoing.get(name, ())),
                default=earliest[name],
            )
            ceiling = max(latest[name], floor)
            position[name] = min(max(self._snapped(wanted[name]), floor), ceiling)
        return {item: position[root(item)] + within[item] for item in self.participants}

    def _grouped(self, same: list["_Same"]) -> tuple[dict[str, str], dict[str, float]]:
        """I pezzi legati dalle rette dell'altro asse, e lo scarto di ciascuno."""
        offset: dict[str, float] = {item: 0.0 for item in self.participants}
        parent: dict[str, str] = {item: item for item in self.participants}

        def find(item: str) -> tuple[str, float]:
            shift = 0.0
            while parent[item] != item:
                shift += offset[item]
                item = parent[item]
            return item, shift

        for link in same:
            one, shift_one = find(link.here)
            two, shift_two = find(link.there)
            if one == two:
                continue
            parent[two] = one
            offset[two] = shift_one + link.delta - shift_two
        leader = {item: find(item)[0] for item in self.participants}
        within = {item: find(item)[1] for item in self.participants}
        return (leader, within)

    def _earliest(
        self, groups: dict[str, list[str]], edges: list[tuple[str, str, float]]
    ) -> dict[str, float]:
        """La soluzione piu' compatta: ogni gruppo il piu' indietro possibile."""
        position = dict.fromkeys(groups, 0.0)
        for _ in range(len(groups) + 1):
            moved = False
            for low, high, gap in edges:
                if position[high] < position[low] + gap - _TOLERANCE_MM:
                    position[high] = position[low] + gap
                    moved = True
            if not moved:
                break
        return position

    def _latest(
        self,
        groups: dict[str, list[str]],
        edges: list[tuple[str, str, float]],
        horizon: float,
    ) -> dict[str, float]:
        """Fin dove ciascun gruppo puo' arrivare senza spingere gli altri."""
        position = dict.fromkeys(groups, horizon)
        for _ in range(len(groups) + 1):
            moved = False
            for low, high, gap in edges:
                if position[low] > position[high] - gap + _TOLERANCE_MM:
                    position[low] = position[high] - gap
                    moved = True
            if not moved:
                break
        return position

    def _ordered(
        self, groups: dict[str, list[str]], edges: list[tuple[str, str, float]]
    ) -> list[str] | None:
        """I gruppi in ordine di dipendenza, o `None` se le campate si mordono
        la coda: un anello di disuguaglianze non ha soluzione e la fase lo
        dichiara invece di consegnare una posa che non le rispetta."""
        waiting = dict.fromkeys(groups, 0)
        after: dict[str, list[str]] = {}
        for low, high, _ in edges:
            waiting[high] += 1
            after.setdefault(low, []).append(high)
        ready = sorted(name for name, count in waiting.items() if count == 0)
        out: list[str] = []
        while ready:
            name = ready.pop(0)
            out.append(name)
            for other in sorted(after.get(name, ())):
                waiting[other] -= 1
                if waiting[other] == 0:
                    ready.append(other)
            ready.sort()
        return out if len(out) == len(groups) else None

    def _snapped(self, value: float) -> float:
        return round(value / self.step) * self.step

    def _lay_out(self, root: str) -> None:
        """Le due passate, e la posa che ne esce."""
        self._walk(root)
        same_x, apart_x, same_y, apart_y = self._demands()
        # I due assi si conservano: la compattazione che viene dopo non
        # improvvisa una propria idea di «che cosa si muove insieme», la legge
        # da qui. Un gruppo e' cio' che una retta tiene insieme su quell'asse, e
        # una campata e' l'ordine che due gruppi si devono.
        self.axes = (
            _AxisDemands(*self._grouped(same_x), tuple(apart_x)),
            _AxisDemands(*self._grouped(same_y), tuple(apart_y)),
        )
        xs = self._solve_axis(same_x, apart_x, 0)
        ys = self._solve_axis(same_y, apart_y, 1)
        # **Il foglio viene prima della prima ipotesi.** Fra tutte le soluzioni
        # che rispettano le campate, `_solve_axis` sceglie quella piu' vicina
        # alla posa di partenza, che e' la scelta giusta finche' ci sta: la fase
        # deve raddrizzare il tronco, non riscrivere la tavola. Quando pero'
        # quella soluzione porta il disegno **oltre il bordo**, non e' una
        # soluzione: chi segue il tronco esce dal foglio con lui, e una tratta
        # oltre il bordo non si instrada — sulla tavola 2 erano i
        # ventilconvettori, trentacinque millimetri fuori. Allora si prende
        # quella compatta, che rispetta le stesse campate e occupa il minimo.
        if not self._fits_the_sheet(xs, 0):
            xs = self._solve_axis(same_x, apart_x, 0, compact=True)
        if not self._fits_the_sheet(ys, 1):
            ys = self._solve_axis(same_y, apart_y, 1, compact=True)
        base = self.start[root].origin
        anchor_x, anchor_y = xs[root], ys[root]
        for item in self.participants:
            origin = Point(
                x_mm=base.x_mm + xs[item] - anchor_x,
                y_mm=base.y_mm + ys[item] - anchor_y,
            )
            self.laid[item] = self.placed(
                item, self._on_grid(origin), self.pose[item]
            )

    def _on_grid(self, origin: Point) -> Point:
        """L'origine riportata sul nodo di griglia piu' vicino dell'area."""

        def snap(value: float, base: float) -> float:
            return base + round((value - base) / self.step) * self.step

        return Point(
            x_mm=snap(origin.x_mm, self.area.x_mm),
            y_mm=snap(origin.y_mm, self.area.y_mm),
        )

    # -- la compattazione ----------------------------------------------------

    def _overlaps(self, one: PlacedSymbol, two: PlacedSymbol) -> bool:
        return (
            one.origin.x_mm < two.right_mm + ROW_GAP_MM - _TOLERANCE_MM
            and two.origin.x_mm - ROW_GAP_MM < one.right_mm - _TOLERANCE_MM
            and one.origin.y_mm < two.bottom_mm + ROW_GAP_MM - _TOLERANCE_MM
            and two.origin.y_mm - ROW_GAP_MM < one.bottom_mm - _TOLERANCE_MM
        )

    def _relieve(self) -> None:
        """Allontana lungo l'asse cio' che si sovrappone, mai di traverso.

        Muovere un pezzo **lungo la retta** della propria tratta ne allunga la
        campata e non tocca nessun allineamento: e' la stessa mossa che la fase
        del corredo chiamera' stretch. Muoverlo di traverso, invece, piegherebbe
        la tratta — ed e' esattamente cio' che questa fase non fa.

        **Una coppia che non si separa non ferma le altre.** Prima di DRAW-010
        la prima coppia irriducibile chiudeva la compattazione, e sulla tavola 2
        era la prima in ordine: il resto non veniva nemmeno guardato.
        """
        stuck: set[frozenset[str]] = set()
        for _ in range(_RELIEF_ROUNDS):
            clash = self._first_clash(stuck)
            if clash is None:
                return
            if not self._push_apart(*clash):
                stuck.add(frozenset(clash))

    def _first_clash(self, stuck: set[frozenset[str]]) -> tuple[str, str] | None:
        """Due partecipanti troppo vicini, escluse le coppie che una tratta unisce.

        Chi sta ai due capi della stessa autostrada e' gia' alla distanza che
        la campata gli assegna: chiedergli anche lo stacco di fascia lo
        allontanerebbe dal proprio raccordo senza motivo.
        """
        joined = {
            frozenset({trunk.start.component_id, trunk.end.component_id})
            for trunk in self.autostrade
        }
        items = list(self.participants)
        for index, one in enumerate(items):
            for two in items[index + 1 :]:
                pair = frozenset({one, two})
                if pair in joined or pair in stuck:
                    continue
                if self._overlaps(self.laid[one], self.laid[two]):
                    return (one, two)
        return None

    def _push_apart(self, one: str, two: str) -> bool:
        """Allontana i due lungo un asse, portandosi dietro chi li segue.

        **Perche' non basta il sottoalbero oltre una tratta.** Fino a DRAW-009
        la mossa cercava il sottoalbero al di la' della tratta che porta al piu'
        lontano dei due. Su un albero quel sottoalbero e' un insieme che si
        stacca; su un **anello** — e il tronco di un circuito chiuso e' un
        anello — togliere una tratta non stacca niente: si cammina fino in fondo
        e si torna indietro dall'altro capo, con dentro anche l'ancora. Le due
        candidate si scartavano tutte e due e la posa usciva coi pezzi addosso
        (`docs/collaudi/DRAW-010/perche-l-anello-non-separava.py`).

        **Cio' che si muove insieme lo dicono i vincoli, non la topologia.** Su
        un asse, una retta dell'altro asse tiene insieme un **gruppo**: chi vi
        appartiene non si muove da solo senza piegarla. Fra gruppi valgono le
        campate, che sono disuguaglianze con un verso. Spostare in avanti un
        gruppo **con tutti quelli che gli stanno oltre** — o all'indietro un
        gruppo con tutti quelli che gli stanno prima — allunga le campate al
        confine e non ne accorcia nessuna: nessuna retta si piega, nessuna
        tratta che era rettilinea diventa storta, e ogni tratta conserva almeno
        il rettilineo che pretende. E' lo stretch del PO, applicato a un anello.
        """
        best: (
            tuple[tuple[int, float, int, int, int, str], list[str], int, float] | None
        ) = None
        for axis in (0, 1):
            for victim, anchor in ((one, two), (two, one)):
                for sign in (1, -1):
                    block = self._follow(axis, sign, victim)
                    if anchor in block:
                        # L'ancora si muove con la vittima: la coppia resta
                        # com'e'. E' il caso dell'anello.
                        continue
                    room = self._clearance(victim, anchor, axis, sign)
                    if room <= _TOLERANCE_MM or room > _RELIEF_STEPS * self.step:
                        continue
                    # **Prima cio' che ci sta nel foglio, poi cio' che costa
                    # meno.** Allargare di venti millimetri dalla parte in cui
                    # il disegno e' gia' al bordo porta fuori foglio chi segue
                    # il tronco — un utilizzatore oltre il bordo non si
                    # instrada — mentre trenta dalla parte libera non costano
                    # niente: spostare macchine e accessori non costa, e la
                    # misura della posa dice da che parte c'e' spazio.
                    room_left = (
                        self.area.width_mm if axis == 0 else self.area.height_mm
                    )
                    fuori = (
                        0
                        if self.spread[axis] + self.grown[axis] + room
                        <= room_left + _TOLERANCE_MM
                        else 1
                    )
                    key = (fuori, room, len(block), axis, 0 if sign > 0 else 1, victim)
                    if best is None or key < best[0]:
                        best = (key, block, axis, sign * room)
        if best is None:
            return False
        _, block, axis, shift = best
        self._shift(block, axis, shift)
        self.grown[axis] += abs(shift)
        return True

    def _follow(self, axis: int, sign: int, victim: str) -> list[str]:
        """Chi si sposta insieme al `victim`, su quell'asse e in quel verso.

        Il suo gruppo, e a ruota tutti i gruppi che le campate obbligano a
        stargli oltre — o a stargli prima, se il verso e' all'indietro.
        """
        demands = self.axes[axis]
        leader = demands.leader
        onward: dict[str, list[str]] = {}
        for link in demands.apart:
            low, high = leader[link.low], leader[link.high]
            if low == high:
                continue
            first, then = (low, high) if sign > 0 else (high, low)
            onward.setdefault(first, []).append(then)
        seen = {leader[victim]}
        frontier = [leader[victim]]
        while frontier:
            name = frontier.pop()
            for other in onward.get(name, ()):
                if other in seen:
                    continue
                seen.add(other)
                frontier.append(other)
        return [item for item in self.participants if leader[item] in seen]

    def _clearance(self, victim: str, anchor: str, axis: int, sign: int) -> float:
        """Di quanto il `victim` deve scorrere per uscire da sotto l'`anchor`.

        Il conto e' sull'asse e nel verso dati, riportato in su al passo di
        griglia: la posa resta sui nodi della griglia come la fase l'ha fatta.
        """
        here, there = self.laid[victim], self.laid[anchor]
        if axis == 0:
            mine = (here.origin.x_mm, here.right_mm)
            its = (there.origin.x_mm, there.right_mm)
        else:
            mine = (here.origin.y_mm, here.bottom_mm)
            its = (there.origin.y_mm, there.bottom_mm)
        want = (
            its[1] + ROW_GAP_MM - mine[0]
            if sign > 0
            else mine[1] - (its[0] - ROW_GAP_MM)
        )
        return self._steps_up(want) if want > _TOLERANCE_MM else 0.0

    def _shift(self, block: list[str], axis: int, shift: float) -> None:
        for item in block:
            here = self.laid[item]
            self.laid[item] = here.model_copy(
                update={
                    "origin": Point(
                        x_mm=here.origin.x_mm + (shift if axis == 0 else 0.0),
                        y_mm=here.origin.y_mm + (0.0 if axis == 0 else shift),
                    )
                }
            )

    def _into_the_area(self) -> None:
        """Porta il tronco dentro l'area di disegno, senza cambiarne la forma."""
        lefts = [self.laid[item].origin.x_mm for item in self.participants]
        tops = [self.laid[item].origin.y_mm for item in self.participants]
        rights = [self.laid[item].right_mm for item in self.participants]
        bottoms = [self.laid[item].bottom_mm for item in self.participants]
        dx = self._slide(min(lefts), max(rights), self.area.x_mm, self.area.right_mm)
        dy = self._slide(min(tops), max(bottoms), self.area.y_mm, self.area.bottom_mm)
        if dx == 0.0 and dy == 0.0:
            return
        for item in self.participants:
            here = self.laid[item]
            self.laid[item] = here.model_copy(
                update={
                    "origin": Point(
                        x_mm=here.origin.x_mm + dx, y_mm=here.origin.y_mm + dy
                    )
                }
            )

    def _slide(self, low: float, high: float, floor: float, ceiling: float) -> float:
        """Di quanto traslare un intervallo perche' stia dentro un altro."""
        steps = 0.0
        if low < floor - _TOLERANCE_MM:
            steps = self._steps_up(floor - low)
        elif high > ceiling + _TOLERANCE_MM:
            steps = -self._steps_up(high - ceiling)
        return steps

    def _steps_up(self, amount: float) -> float:
        steps = int(amount / self.step)
        if amount - steps * self.step > _TOLERANCE_MM:
            steps += 1
        return steps * self.step

    # -- la misura della forma ------------------------------------------------

    def build(self) -> SpineLayout:
        if not self.participants or not self.autostrade:
            return SpineLayout(
                machines=self.machines,
                participants=self.participants,
                trunks=tuple(self.autostrade),
                symbols=(),
                routes=(),
                runs=(),
            )
        self._lay_out(self._root())
        self._relieve()
        self._into_the_area()
        symbols = [self.laid[item] for item in self.participants]
        try:
            routes = route_sheet(
                self.project, list(self.autostrade), symbols, self.catalog, self.grid
            )
        except LayoutError:
            # Il tronco costruito non si instrada: la fase non ha una forma da
            # consegnare e lo dice, invece di consegnarne una falsa. Chi la
            # chiama torna alla posa di partenza e il rapporto lo dichiara.
            return SpineLayout(
                machines=self.machines,
                participants=self.participants,
                trunks=tuple(self.autostrade),
                symbols=(),
                routes=(),
                runs=tuple(
                    SpineRun(
                        key=trunk.connection_ids,
                        horizontal=self._is_horizontal(trunk),
                        straight=False,
                        possible=self._can_be_straight(trunk),
                    )
                    for trunk in self.autostrade
                ),
            )
        runs = tuple(
            SpineRun(
                key=trunk.connection_ids,
                horizontal=self._is_horizontal(trunk),
                straight=_is_a_straight_route(route),
                possible=self._can_be_straight(trunk),
            )
            for trunk, route in zip(self.autostrade, routes, strict=True)
        )
        return SpineLayout(
            machines=self.machines,
            participants=self.participants,
            trunks=tuple(self.autostrade),
            symbols=tuple(symbols),
            routes=tuple(routes),
            runs=runs,
        )

    def _is_horizontal(self, trunk: Trunk) -> bool:
        _, face = self.port_at(self.laid[trunk.start.component_id], trunk.start.port_id)
        return face in _HORIZONTAL_FACES

    def _can_be_straight(self, trunk: Trunk) -> bool:
        return self.facing.get(trunk.connection_ids, False)


def can_be_straight(here: frozenset[PortFace], there: frozenset[PortFace]) -> bool:
    """Vero se fra le facce che le due porte possono prendere ce n'e' una coppia
    opposta: e' la condizione perche' una retta le unisca.

    Prende **insiemi di facce**, non pezzi: chi la chiama decide quali facce
    siano davvero disponibili. Su un pezzo libero sono quelle di tutte le sue
    pose ammesse; su un pezzo che il resto del tronco ha gia' fermato — la
    deviatrice che tiene l'asse verso l'accumulo maggiore — e' una sola. Con una
    faccia sola da una parte e una sola dall'altra, la risposta e' un fatto del
    catalogo e nessuna posa lo cambia.
    """
    return any(face.opposite in there for face in here)


def _is_a_straight_route(route: RoutedTrunk) -> bool:
    """Vero se la spezzata e' una retta: un tratto solo, due punti."""
    return len(route.segments) == 1 and len(route.segments[0]) == 2


def unstraightenable_runs(
    project: ProjectModel,
    partition: SheetPartition,
    catalog: ComponentRegistry,
    frame: SheetFrame,
    placed: list[PlacedSymbol],
) -> tuple[TrunkKey, ...]:
    """Le autostrade che, dato il resto del tronco, nessuna posa raddrizza."""
    return _Spine(project, partition, catalog, frame, placed).build().impossible


def lay_the_spine(
    project: ProjectModel,
    partition: SheetPartition,
    catalog: ComponentRegistry,
    frame: SheetFrame,
    placed: list[PlacedSymbol],
) -> SpineLayout:
    """La fase del tronco: posa le macchine di spina, instrada l'autostrada.

    Restituisce **soltanto** la geometria della fase — i partecipanti e le
    autostrade — perche' e' quella che le fasi successive devono rispettare. Il
    resto dell'impianto non partecipa e non compare.
    """
    return _Spine(project, partition, catalog, frame, placed).build()


def carry_the_rest(
    project: ProjectModel,
    partition: SheetPartition,
    catalog: ComponentRegistry,
    placed: list[PlacedSymbol],
    layout: SpineLayout,
    frame: SheetFrame | None = None,
) -> list[PlacedSymbol]:
    """La posa del resto che parte dal tronco (architettura §5).

    Chi non ha partecipato alla fase del tronco non resta dov'era: **segue per
    il grafo** il partecipante da cui dipende, della stessa traslazione. Non
    per vicinanza sul foglio — l'utilizzatore che sta a due centimetri da un
    raccordo non e' per questo attaccato a lui — ma per come l'impianto e'
    fatto: dal partecipante si cammina lungo le tubazioni e si porta con se'
    tutto quel che si incontra.

    E chi **pende** da un partecipante che la fase ha girato non si trasla: si
    riappende. Un manometro appeso al raccordo del ritorno, quando il raccordo
    gira il proprio stacco verso il basso, va sotto — e restarsene sopra
    significherebbe consegnare una figura spezzata.

    Con `frame`, una figura riappesa che finirebbe **fuori dall'area di disegno**
    accorcia il proprio stacco finche' ci rientra, fino al minimo di un passo.
    Il tronco si sposta guardando i soli partecipanti (`_into_the_area`), e
    quando scende porta con se' cio' che gli pende: una figura profonda — dal
    raccordo il gruppo di riempimento, dal gruppo il proprio ingresso — arriva
    piu' in basso di chi la regge, ed e' uscita dal foglio. Fuori dal foglio una
    tratta non si instrada, e la fase consegnava una posa che non si poteva
    nemmeno misurare.

    E' una prima ipotesi, non una posa finale: a sistemarla sono le fasi del
    corredo e delle strade di servizio.
    """
    if not layout.symbols:
        return list(placed)
    moved = {item.component_id: item for item in layout.symbols}
    before = {item.component_id: item for item in placed}
    delta = {
        component_id: (
            item.origin.x_mm - before[component_id].origin.x_mm,
            item.origin.y_mm - before[component_id].origin.y_mm,
        )
        for component_id, item in moved.items()
        if component_id in before
    }
    if not delta:
        return list(placed)
    children = hanging_children(project, partition, catalog, frozenset(before))
    hung = {
        child: (parent, port_id)
        for parent, items in children.items()
        for child, port_id in items
    }
    own_ports = hanging_ports(project, partition, catalog, frozenset(before))
    following = _followers(partition, frozenset(before), delta)
    definitions = {item.id: item.definition_id for item in project.components}

    def carried(item: PlacedSymbol) -> PlacedSymbol:
        step = following.get(item.component_id)
        if step is None:
            return item
        dx, dy = step
        return item.model_copy(
            update={
                "origin": Point(x_mm=item.origin.x_mm + dx, y_mm=item.origin.y_mm + dy)
            }
        )

    settled: dict[str, PlacedSymbol] = {}
    for item in placed:
        component_id = item.component_id
        if component_id in moved:
            settled[component_id] = moved[component_id]
        elif component_id not in hung:
            settled[component_id] = carried(item)
    # **La figura si riappende tutta, dall'alto in basso.** Una figura puo'
    # essere profonda — dal raccordo pende il gruppo di riempimento e dal gruppo
    # pende il proprio ingresso — e fermarsi al primo livello lasciava il nipote
    # a seguire il grafo per conto suo: padre e figlio prendevano due
    # traslazioni diverse e la figura si spezzava, senza che nessun vincolo se
    # ne accorgesse.
    changed = True
    while changed:
        changed = False
        for item in placed:
            component_id = item.component_id
            if component_id in settled:
                continue
            link = hung.get(component_id)
            if link is None or link[0] not in settled:
                continue
            hung_now = _rehung(
                item,
                settled[link[0]],
                link[1],
                before[link[0]],
                catalog,
                definitions,
                own_ports.get(component_id),
            )
            settled[component_id] = _inside(
                hung_now,
                settled[link[0]],
                link[1],
                catalog,
                definitions,
                own_ports.get(component_id),
                frame,
            )
            changed = True
    for item in placed:
        settled.setdefault(item.component_id, carried(item))
    _spread_the_hung(settled, placed, hung, catalog, definitions, frame)
    return [settled[item.component_id] for item in placed]


def _spread_the_hung(
    settled: dict[str, PlacedSymbol],
    placed: list[PlacedSymbol],
    hung: dict[str, tuple[str, str]],
    catalog: ComponentRegistry,
    definitions: dict[str, str],
    frame: SheetFrame | None,
) -> None:
    """Allontana lungo il proprio stacco una figura appesa finita addosso a un'altra.

    **Perche' serve, e perche' proprio qui.** Chi posa per la prima volta gia' lo
    fa: `place.hanging_place` cerca il posto preferito dell'appeso e, se e'
    occupato, si allontana lungo lo stacco un passo per volta. Poi pero' la fase
    del tronco sposta il tronco, e `carry_the_rest` riappende le figure a un
    pezzo che sta altrove: il posto che era libero puo' non esserlo piu', e
    nessuno lo guardava. E' cosi' che sulla tavola 2 lo scarico del volano
    finiva dentro il bollitore e il prelievo dentro il volano.

    La regola e' quella della posa, applicata alla posa nuova: si scorre lungo
    lo stacco — nel verso in cui l'appeso si sporge, cioe' l'opposto della faccia
    del proprio attacco — finche' la figura non tocca piu' nessuno, e non si esce
    dall'area di disegno. Lo stacco si allunga; niente si piega, e il tronco non
    si tocca. Chi non trova posto resta dov'e' e la posa lo dichiara com'e'.
    """
    if frame is None:
        return
    area = frame.drawing_rect_mm
    step = frame.standard.grid_mm
    leader: dict[str, str] = {}
    for item in placed:
        head, seen = item.component_id, {item.component_id}
        while head in hung and hung[head][0] not in seen:
            head = hung[head][0]
            seen.add(head)
        leader[item.component_id] = head
    below: dict[str, list[str]] = {}
    for child, (parent, _port) in hung.items():
        below.setdefault(parent, []).append(child)

    def figure(head: str) -> list[str]:
        out, frontier = [head], [head]
        while frontier:
            here = frontier.pop()
            for child in below.get(here, ()):
                out.append(child)
                frontier.append(child)
        return out

    def clear(moving: list[str], shift: tuple[float, float]) -> bool:
        block = set(moving)
        for name in moving:
            here = _moved(settled[name], shift)
            if (
                here.origin.x_mm < area.x_mm - _TOLERANCE_MM
                or here.origin.y_mm < area.y_mm - _TOLERANCE_MM
                or here.right_mm > area.right_mm + _TOLERANCE_MM
                or here.bottom_mm > area.bottom_mm + _TOLERANCE_MM
            ):
                return False
            for other in settled:
                if other in block:
                    continue
                gap = 0.0 if leader[other] == leader[name] else ROW_GAP_MM
                if _touching(here, settled[other], gap):
                    return False
        return True

    # Dall'alto in basso: una figura profonda si sposta tutta insieme, e il
    # nipote non si muove da solo prima del padre.
    order = sorted(hung, key=lambda item: len(figure(item)), reverse=True)
    for component_id in order:
        moving = figure(component_id)
        if clear(moving, (0.0, 0.0)):
            continue
        upright = catalog.resolve(definitions[component_id]).symbol.manifest
        here = settled[component_id]
        mine = upright.rotated(here.rotation_deg).port(
            here.physical_port(hung[component_id][1])
            if hung[component_id][1] in here.port_map
            else upright.ports[0].id
        )
        # Prima lungo lo stacco, che e' la regola della posa e non piega
        # niente; poi, se lungo lo stacco non c'e' posto — capita quando il
        # tronco ha impilato due macchine e la figura di una e' finita dentro
        # l'altra — **di traverso**, che allo stacco costa una piega. Una piega
        # su uno stacco di servizio e' cio' che il PO ha detto di accettare
        # («quelle si', accettiamo qualche curva in piu'»); un pezzo dentro un
        # altro no.
        lungo = _DIRECTION[mine.face.opposite]
        di_traverso = (
            (0.0, 1.0) if lungo[0] else (1.0, 0.0),
            (0.0, -1.0) if lungo[0] else (-1.0, 0.0),
        )
        for direction in (lungo, *di_traverso):
            found = False
            for count in range(1, _RELIEF_STEPS + 1):
                shift = (direction[0] * step * count, direction[1] * step * count)
                if clear(moving, shift):
                    for name in moving:
                        settled[name] = _moved(settled[name], shift)
                    found = True
                    break
            if found:
                break


def _moved(item: PlacedSymbol, shift: tuple[float, float]) -> PlacedSymbol:
    return item.model_copy(
        update={
            "origin": Point(
                x_mm=item.origin.x_mm + shift[0], y_mm=item.origin.y_mm + shift[1]
            )
        }
    )


def _touching(one: PlacedSymbol, two: PlacedSymbol, gap_mm: float) -> bool:
    return (
        one.origin.x_mm < two.right_mm + gap_mm - _TOLERANCE_MM
        and two.origin.x_mm - gap_mm < one.right_mm - _TOLERANCE_MM
        and one.origin.y_mm < two.bottom_mm + gap_mm - _TOLERANCE_MM
        and two.origin.y_mm - gap_mm < one.bottom_mm - _TOLERANCE_MM
    )


def _inside(
    child: PlacedSymbol,
    parent: PlacedSymbol,
    port_id: str,
    catalog: ComponentRegistry,
    definitions: dict[str, str],
    own_port_id: str | None,
    frame: SheetFrame | None,
) -> PlacedSymbol:
    """L'appeso riportato dentro l'area, accorciando il proprio stacco.

    Si accorcia un passo per volta, e non si scende sotto un passo: uno stacco
    lungo zero metterebbe due simboli a contatto. Se nemmeno cosi' ci sta, si
    lascia dov'e' e la posa si giudica come sempre — cattiva, ma misurabile.
    """
    if frame is None:
        return child
    area = frame.drawing_rect_mm
    step = frame.standard.grid_mm

    def fits(item: PlacedSymbol) -> bool:
        return (
            item.origin.x_mm >= area.x_mm - _TOLERANCE_MM
            and item.origin.y_mm >= area.y_mm - _TOLERANCE_MM
            and item.right_mm <= area.right_mm + _TOLERANCE_MM
            and item.bottom_mm <= area.bottom_mm + _TOLERANCE_MM
        )

    if fits(child):
        return child
    upright = catalog.resolve(definitions[child.component_id]).symbol.manifest
    shape = catalog.resolve(definitions[parent.component_id]).symbol.manifest
    port = shape.rotated(parent.rotation_deg).port(parent.physical_port(port_id))
    mine_id = own_port_id or upright.ports[0].id
    stub = Point(
        x_mm=parent.origin.x_mm + port.x_mm, y_mm=parent.origin.y_mm + port.y_mm
    )
    direction = _DIRECTION[port.face]
    mine = upright.rotated(child.rotation_deg).port(mine_id)
    here = Point(x_mm=child.origin.x_mm + mine.x_mm, y_mm=child.origin.y_mm + mine.y_mm)
    gap = abs(here.x_mm - stub.x_mm) + abs(here.y_mm - stub.y_mm)
    shorter = child
    while gap > step + _TOLERANCE_MM:
        gap -= step
        shorter = child.model_copy(
            update={
                "origin": Point(
                    x_mm=stub.x_mm + direction[0] * gap - mine.x_mm,
                    y_mm=stub.y_mm + direction[1] * gap - mine.y_mm,
                )
            }
        )
        if fits(shorter):
            return shorter
    return shorter


def _followers(
    partition: SheetPartition,
    placeable: frozenset[str],
    delta: dict[str, tuple[float, float]],
) -> dict[str, tuple[float, float]]:
    """Di quanto si sposta chi non ha partecipato alla fase del tronco.

    Si guarda a chi e' **attaccato**: un pezzo collegato a un solo
    partecipante lo segue, perche' e' di quel partecipante che fa parte. Un
    pezzo collegato a due partecipanti che si sono spostati in modo diverso non
    segue nessuno dei due e resta dov'e': non c'e' una risposta giusta, e
    sceglierne una a caso rompe la figura — e' successo alla seconda pompa di
    calore di un impianto in cascata, tirata via dalla propria compagna di
    colonna dietro un raccordo che si era spostato.

    Chi non tocca nessun partecipante eredita dal vicino che lo fa, camminando
    in ampiezza: cosi' un utilizzatore in fondo a una fila segue l'accumulo da
    cui la fila parte.
    """
    edges: dict[str, list[str]] = {}
    for trunk in partition.trunks:
        here, there = trunk.start.component_id, trunk.end.component_id
        if here not in placeable or there not in placeable or here == there:
            continue
        edges.setdefault(here, []).append(there)
        edges.setdefault(there, []).append(here)
    found: dict[str, tuple[float, float]] = {}
    for item in sorted(placeable - frozenset(delta)):
        touched = {
            delta[other] for other in edges.get(item, ()) if other in delta
        }
        if len(touched) == 1:
            found[item] = touched.pop()
    seen = set(delta) | set(found)
    frontier = sorted(found)
    while frontier:
        onward: list[str] = []
        for item in sorted(frontier):
            for other in sorted(edges.get(item, ())):
                if other in seen:
                    continue
                seen.add(other)
                found[other] = found[item]
                onward.append(other)
        frontier = onward
    return found


def _rehung(
    child: PlacedSymbol,
    parent: PlacedSymbol,
    port_id: str,
    was: PlacedSymbol,
    catalog: ComponentRegistry,
    definitions: dict[str, str],
    own_port_id: str | None = None,
) -> PlacedSymbol:
    """L'appeso rimesso dalla parte in cui lo stacco guarda adesso, allo stacco
    di prima: e' la stessa regola con cui il ciclo lo riappende quando gira il
    pezzo che lo regge.

    `own_port_id` e' **il suo** attacco su quello stacco. Non e' sempre il primo
    del manifesto: un ponte fra due reti ne ha due, e riappenderlo per l'altro
    lo manda dalla parte opposta del proprio stacco — con il nipote che gli
    pende addosso a finire in mezzo alla tubazione (DRAW-006-R1, blocco D).
    """
    resolved = catalog.resolve(definitions[child.component_id])
    upright = resolved.symbol.manifest
    shape = catalog.resolve(definitions[parent.component_id]).symbol.manifest
    port = shape.rotated(parent.rotation_deg).port(parent.physical_port(port_id))
    old = shape.rotated(was.rotation_deg).port(was.physical_port(port_id))
    stub = Point(
        x_mm=parent.origin.x_mm + port.x_mm, y_mm=parent.origin.y_mm + port.y_mm
    )
    if boundary_faces_the_plant(resolved.definition) is not None:
        # **Un confine di rete non si rigira dietro lo stacco** (DRAW-010 §D.1).
        # La sua giacitura non la decide il pezzo che lo regge: la decide la
        # lettura, da sinistra a destra, e la posa l'ha gia' scelta. Riappenderlo
        # come gli altri lo rimetterebbe con l'attacco rivolto verso lo stacco —
        # sul bollitore, la cui uscita ACS sta sulla faccia superiore, con la
        # bocchetta verso il basso e la linea che deve risalirci dentro, cioe'
        # proprio la curva che il PO ha chiesto di togliere. Segue percio' il
        # proprio stacco di pura traslazione, e la piega che resta e' quella
        # voluta: il gomito che tiene il flusso di lettura da sinistra a destra.
        return child.model_copy(
            update={
                "origin": Point(
                    x_mm=child.origin.x_mm
                    + (port.x_mm - old.x_mm)
                    + (parent.origin.x_mm - was.origin.x_mm),
                    y_mm=child.origin.y_mm
                    + (port.y_mm - old.y_mm)
                    + (parent.origin.y_mm - was.origin.y_mm),
                )
            }
        )
    mine_id = own_port_id or upright.ports[0].id
    own = upright.rotated(child.rotation_deg).port(mine_id)
    gap = abs(
        (was.origin.x_mm + old.x_mm) - (child.origin.x_mm + own.x_mm)
    ) + abs((was.origin.y_mm + old.y_mm) - (child.origin.y_mm + own.y_mm))
    direction = _DIRECTION[port.face]
    wanted = port.face.opposite
    chosen = child.rotation_deg
    for degrees in sorted(
        upright.allowed_rotations_deg,
        key=lambda item: (item != child.rotation_deg, item),
    ):
        if upright.rotated(degrees).port(mine_id).face is wanted:
            chosen = degrees
            break
    turned = upright.rotated(chosen)
    mine = turned.port(mine_id)
    return child.model_copy(
        update={
            "origin": Point(
                x_mm=stub.x_mm + direction[0] * gap - mine.x_mm,
                y_mm=stub.y_mm + direction[1] * gap - mine.y_mm,
            ),
            "rotation_deg": chosen,
            "width_mm": turned.width_mm,
            "height_mm": turned.height_mm,
        }
    )


def straight_runs_of(
    trunks: list[Trunk], routes: list[RoutedTrunk], levels: dict[TrunkKey, Level]
) -> dict[TrunkKey, bool]:
    """Per ogni autostrada, se la sua spezzata e' un rettilineo.

    E' la lettura che il collaudo usa sulla tavola consegnata: si guarda la
    geometria, non l'intenzione.
    """
    return {
        trunk.connection_ids: _is_a_straight_route(route)
        for trunk, route in zip(trunks, routes, strict=True)
        if levels.get(trunk.connection_ids) is Level.AUTOSTRADA
    }


__all__ = [
    "SpineLayout",
    "SpineRun",
    "autostrada_trunks",
    "can_be_straight",
    "carry_the_rest",
    "lay_the_spine",
    "spine_participants",
    "straight_runs_of",
    "unstraightenable_runs",
]
