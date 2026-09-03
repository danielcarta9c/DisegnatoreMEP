"""La posa finale, decisa dal costo delle tubazioni (D-078, D-080, DRAW-002).

Il PO, sulla tavola di DRAW-001 (I-021): «bisogna spostare le macchine perche'
spostare le macchine costa zero; invece incroci, curve e lunghezze costano». E
prima ancora (D-078): «non devi mettere gli oggetti in tavola e poi fare le
linee — o meglio lo fai, ma poi gli oggetti si spostano per ottimizzare il
routing, non viceversa».

Qui `place.py` ha gia' dato una posa iniziale valida e ordinata per processo;
questo modulo decide la posa **finale** reinstradando l'intera tavola a ogni
prova. Tre regole, nell'ordine del pacchetto DRAW-002:

1. **Un solo confronto esplicito della tavola**, `SheetCost`, con precedenza
   lessicografica: violazioni bloccanti e tratte che non ospitano i propri
   accessori; tratte con andata e ritorno; millimetri di andata e ritorno;
   tratte oltre tre pieghe; pieghe; incroci; lunghezza; e solo come spareggio
   fra geometrie uguali su tutte e sette, riempimento e bilanciamento. Nessun
   peso: una voce successiva non compensa mai una precedente, e il movimento
   dei simboli non entra nel costo.
2. **Niente distensione.** Prima il ciclo, finite le linee, allontanava i
   pezzi dal centro per inseguire il 60 % di riempimento pagando in lunghezza
   di tubo: quel comportamento e' rimosso. `fill` e `imbalance` restano misure
   diagnostiche e spareggi, mai ragioni per aumentare tubo, curve, incroci o
   andate e ritorno.
3. **Le pose vengono dalla topologia, non da distanze prefissate.** I candidati
   si ricavano dalle coordinate delle porte e dei vicini collegati: la quota
   che allinea due porte, la distanza minima che lascia il rettilineo agli
   accessori in linea, la rotazione che rivolge una porta verso il proprio
   collegamento, la catena di raccordi rimessa in fila dalla porta del pezzo
   grosso, la traslazione di una pila o di una colonna come gruppo, lo
   spostamento di tutto cio' che sta oltre un pezzo verso il pezzo che lo
   precede. Possono valere anche molti passi di griglia.

Ogni candidato si misura **dopo `settle_sheet`**, accessori in linea posati e
tutte le tratte reinstradate: e' la stessa funzione con cui `compose_sheet`
disegna, quindi cio' che si misura e' cio' che esce. Nessuna approssimazione su
geometrie parziali.

Vincoli mai violabili, qualunque sia il guadagno:

- l'ordine di processo da sinistra a destra (D-060), letto sul verso del
  fluido: una tratta di mandata non porta la meta a sinistra della sorgente,
  una di ritorno non la porta a destra; dove il verso non e' deciso l'ordine
  disegnato non cambia. Una posa iniziale che gia' contraddice il verso puo'
  essere corretta, mai peggiorata;
- chi sta a terra resta alla propria quota: si scorre lungo la fascia;
- le distanze minime fra simboli, la griglia, l'area di disegno;
- una pila o una colonna non si sfila di un elemento: si trasla insieme;
- determinismo: candidati in ordine fisso, accettazione della prima mossa che
  batte la posa corrente sul confronto unico, tetto dichiarato di prove.

Il ciclo e' greedy e reversibile: ogni mossa accettata batte strettamente la
precedente, quindi termina; il tetto di instradamenti di prova lo ferma comunque
in un punto che dipende solo dagli ingressi.
"""

from collections.abc import Iterable
from typing import NamedTuple

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import Rect, SheetFrame
from disegnatore_mep.graphics.symbol import PortFace, SymbolManifest
from disegnatore_mep.model.project import ProjectModel

from .composition import Standing, levels_of, standing_of
from .errors import LayoutError
from .flow import orient_trunks
from .geometry import (
    PlacedSymbol,
    Point,
    RoutedTrunk,
    box_of,
    fill_ratio,
    ink_box,
    ink_imbalance,
    overshoot_mm,
    run_intrudes_on,
)
from .grid import GridSpace, is_on_grid
from .inline import SettledSheet, settle_sheet
from .partition import SheetPartition
from .place import (
    ROUTING_MARGIN_MM,
    ROW_GAP_MM,
    hanging_children,
    inline_room_mm,
    run_chains,
)
from .route import CROSS_COST, STEP_COST, TURN_COST
from .trunks import Trunk

MAX_PASSES = 12
"""Passate del ciclo: ognuna scorre tutti i pezzi una volta.

Una passata senza mosse accettate chiude il ciclo; dodici lo chiudono comunque.
Il numero e' un limite di sicurezza, non un obiettivo: il tetto che governa il
costo e' quello degli instradamenti di prova.
"""

MAX_TRIAL_ROUTINGS = 1500
"""Tetto di instradamenti di prova per foglio: il limite di ricerca dichiarato.

Raggiunto il tetto si restituisce la migliore posa trovata fin li'. Scatta in
modo deterministico — stessi ingressi, stesse prove, stesso punto di arresto —
quindi non costa la riproducibilita'. Ogni prova e' un `settle_sheet` completo,
e vale circa un decimo di secondo sull'impianto 1.
"""

NUDGE_STEPS = (1, 2, 4, 8)
"""Le traslazioni cieche, in passi di griglia: l'ultima risorsa, dopo le mosse
ricavate dalle porte. Servono a scansare un ostacolo che nessuna porta indica."""

SLACK_STEPS = (0, 2, 4)
"""Il gioco in piu' provato oltre la distanza minima, in passi di griglia.

La distanza minima e' quella che lascia il rettilineo agli accessori in linea;
qualche passo in piu' serve quando un altro pezzo o una tratta altrui occupano
proprio quel rettilineo.
"""

BENDS_PER_RUN_MAX = 3
"""Pieghe oltre le quali una tratta e' un giro attorno a qualcosa (B4, D-060).

Lo stesso numero che il preflight usa per il proprio avviso.
"""

_TOLERANCE_MM = 1e-6
_HORIZONTAL_FACES = (PortFace.LEFT, PortFace.RIGHT)
_DIRECTION: dict[PortFace, tuple[float, float]] = {
    PortFace.RIGHT: (1.0, 0.0),
    PortFace.BOTTOM: (0.0, 1.0),
    PortFace.LEFT: (-1.0, 0.0),
    PortFace.TOP: (0.0, -1.0),
}

Move = dict[str, PlacedSymbol]
"""Una candidata: i soli simboli che cambiano posa, gia' posati dove andrebbero."""


class SheetCost(NamedTuple):
    """Il valore confrontabile della geometria completa, nell'ordine del pacchetto.

    Si confronta con `beats`, che e' l'ordine lessicografico delle voci: la
    prima che differisce decide. Riempimento e bilanciamento chiudono la fila e
    contano solo a parita' di tutte le altre.
    """

    violations: int
    """Tratte che non ospitano i propri accessori, e accessori posati addosso a
    una tratta altrui o a un simbolo: cio' che il preflight blocca."""

    turnback_runs: int
    """Tratte con andata e ritorno (B12, D-078)."""

    turnback_mm: float
    """Millimetri complessivi di andata e ritorno."""

    long_runs: int
    """Tratte oltre le tre pieghe (B4)."""

    bends: int
    crossings: int
    length_mm: float

    fill: float
    """Riempimento dell'area di disegno: spareggio, piu' e' meglio."""

    imbalance: float
    """Squilibrio dell'inchiostro fra i quadranti: spareggio, meno e' meglio."""

    def key(self) -> tuple[int, int, float, int, int, int, float, float, float]:
        """La chiave d'ordine: le sette voci, poi i due spareggi."""
        return (
            self.violations,
            self.turnback_runs,
            round(self.turnback_mm, 3),
            self.long_runs,
            self.bends,
            self.crossings,
            round(self.length_mm, 3),
            round(-self.fill, 6),
            round(self.imbalance, 6),
        )

    def beats(self, other: "SheetCost") -> bool:
        """Vero se questa geometria e' strettamente migliore dell'altra."""
        return self.key() < other.key()


class Measured(NamedTuple):
    """Una posa misurata: il suo costo e la tavola instradata da cui viene."""

    cost: SheetCost
    settled: SettledSheet


def objective_of(routes: list[RoutedTrunk], step_mm: float) -> int:
    """L'obiettivo storico del PM, intero: pieghe, attraversamenti, lunghezza
    (D-060), con i pesi dell'instradatore. Resta come misura di confronto delle
    prove: il ciclo non lo usa piu' per decidere, decide `SheetCost`."""
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


def overshoot_beyond_goal_mm(route: RoutedTrunk, goal: Point) -> float:
    """Di quanto la tratta supera la porta di destinazione per poi tornarci (B12).

    Il corollario di D-078: «un componente non si raggiunge mai con un'andata
    e ritorno; se la linea lo supera e torna indietro, e' l'oggetto a essere
    nel posto sbagliato». Il confine e' la perpendicolare per la porta di
    arrivo: per un approccio orizzontale e' la verticale per la porta, per uno
    verticale l'orizzontale. Ogni punto della spezzata oltre quel confine, nel
    verso di arrivo, e' un'andata oltre la meta che la tratta deve disfare.

    Non e' la stessa cosa che misura `geometry.overshoot_mm`, che guarda la
    spezzata disegnata e vede se torna su se stessa; il ciclo le conta **tutte
    e due**, perche' sono due difetti e non due nomi dello stesso.
    """
    if not route.segments:
        return 0.0
    last = route.segments[-1]
    if len(last) < 2:
        return 0.0
    end, before = last[-1], last[-2]
    horizontal = abs(end.x_mm - before.x_mm) > abs(end.y_mm - before.y_mm)
    points = [point for segment in route.segments for point in segment]
    if horizontal:
        sign = 1.0 if end.x_mm > before.x_mm else -1.0
        overshoot = max((point.x_mm - goal.x_mm) * sign for point in points)
    else:
        sign = 1.0 if end.y_mm > before.y_mm else -1.0
        overshoot = max((point.y_mm - goal.y_mm) * sign for point in points)
    return max(overshoot, 0.0)


def overshoots_the_goal(route: RoutedTrunk, goal: Point) -> bool:
    """Vero se la tratta supera la porta di destinazione per poi tornarci (B12)."""
    return overshoot_beyond_goal_mm(route, goal) > _TOLERANCE_MM


def _relation(left: float, right: float) -> int:
    return (left > right) - (left < right)


def _centred_on(
    box: tuple[float, float, float, float] | None,
    area: tuple[float, float, float, float],
) -> tuple[float, float, float, float]:
    """L'area di disegno **come la vedra' il blocco una volta centrato**.

    Il ciclo sceglie una posa, e dopo di lui la composizione porta il blocco al
    centro del foglio: misurare i quadranti dove i pezzi stanno adesso vuol dire
    misurare una tavola che non uscira'. Si trasla il rettangolo, non la posa.
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


def _snap_up(value_mm: float, step_mm: float) -> float:
    """Il primo multiplo del passo non inferiore al valore."""
    steps = int(value_mm / step_mm)
    if value_mm - steps * step_mm > _TOLERANCE_MM:
        steps += 1
    return steps * step_mm


def _signature(layout: Move) -> tuple[tuple[str, float, float, int], ...]:
    return tuple(
        (item.component_id, item.origin.x_mm, item.origin.y_mm, item.rotation_deg)
        for item in layout.values()
    )


class Improver:
    """Il ciclo di miglioramento di un foglio, con le sue letture della posa.

    Si costruisce sulla posa iniziale e la migliora con `run`. I metodi
    `candidates`, `is_valid` e `measure` sono pubblici perche' le prove generali
    del pacchetto verificano **quali** mosse il ciclo sa generare, non solo
    dove arriva.
    """

    def __init__(
        self,
        project: ProjectModel,
        partition: SheetPartition,
        catalog: ComponentRegistry,
        frame: SheetFrame,
        placed: list[PlacedSymbol],
        inline_ids: frozenset[str],
    ) -> None:
        self.project = project
        self.partition = partition
        self.catalog = catalog
        self.frame = frame
        self.inline_ids = inline_ids
        self.trunks: list[Trunk] = list(partition.trunks)
        self.order = [item.component_id for item in placed]
        self.best: Move = {item.component_id: item for item in placed}
        # L'ordine di scansione e' quello della posa iniziale letta da sinistra
        # a destra e dall'alto in basso, mai quello dei nomi: due impianti
        # uguali con identificativi diversi devono dare la stessa tavola.
        self.scan = sorted(
            self.order,
            key=lambda item: (
                self.best[item].origin.x_mm,
                self.best[item].origin.y_mm,
                self.best[item].symbol_id,
            ),
        )

        drawing = frame.drawing_rect_mm
        # Lo stesso rettangolo ridotto dentro cui `place_sheet` posa: il
        # corridoio di instradamento lungo il bordo resta libero.
        self.area = Rect(
            x_mm=drawing.x_mm + ROUTING_MARGIN_MM,
            y_mm=drawing.y_mm + ROUTING_MARGIN_MM,
            width_mm=drawing.width_mm - 2 * ROUTING_MARGIN_MM,
            height_mm=drawing.height_mm - 2 * ROUTING_MARGIN_MM,
        )
        self.sheet_rect = (drawing.x_mm, drawing.y_mm, drawing.right_mm, drawing.bottom_mm)
        self.grid = GridSpace(origin=drawing, standard=frame.standard)
        self.step = self.grid.step_mm
        self.clearance = frame.standard.min_clearance_mm
        self.levels = levels_of(drawing.y_mm, drawing.height_mm, self.step)

        definitions = {item.id: item.definition_id for item in project.components}
        self.upright: dict[str, SymbolManifest] = {}
        self.features: dict[str, tuple[frozenset[str], bool]] = {}
        for item in placed:
            resolved = catalog.resolve(definitions[item.component_id])
            self.upright[item.component_id] = resolved.symbol.manifest
            self.features[item.component_id] = (
                frozenset(resolved.definition.functions),
                resolved.is_inline,
            )
        self._turned: dict[tuple[str, int], SymbolManifest] = {}
        self.standings = {
            item.component_id: self.standing_at(item.component_id, item.rotation_deg)
            for item in placed
        }

        # Il verso del fluido, che decide l'ordine di processo (D-059, D-060).
        self.flow = orient_trunks(project, catalog, self.trunks)

        # Le figure: chi pende da chi, e chi sta in fila su una tratta.
        placeable = frozenset(self.order)
        self.children: dict[str, tuple[tuple[str, str], ...]] = hanging_children(
            project, partition, catalog, placeable
        )
        self.parent_of: dict[str, tuple[str, str]] = {
            child: (parent, port_id)
            for parent, items in self.children.items()
            for child, port_id in items
        }
        self.chains = sorted(
            (
                chain
                for chain in run_chains(project, partition, catalog, placeable)
                if all(item in self.best for item in chain)
            ),
            key=lambda chain: min(self.scan.index(item) for item in chain),
        )
        self.room: dict[tuple[str, ...], float] = {
            trunk.connection_ids: inline_room_mm(project, catalog, trunk.inline_component_ids)
            for trunk in self.trunks
        }
        # Lo stacco di ogni appeso dal proprio attacco, misurato sulla posa
        # iniziale lungo l'asse dello stacco: si conserva quando il pezzo si
        # muove o si gira, perche' l'ha deciso il posizionamento.
        self.hang_gap: dict[str, float] = {}
        self._refresh_hang_gaps()

        self.owning_run = {
            component_id: index
            for index, trunk in enumerate(self.trunks)
            for component_id in trunk.inline_component_ids
        }
        self.trials = 0
        self._memo: dict[tuple[tuple[str, float, float, int], ...], Measured | None] = {}

    # -- letture del manifesto -------------------------------------------------

    def manifest_at(self, component_id: str, rotation_deg: int) -> SymbolManifest:
        """Il manifesto del componente girato di tanto, dal manifesto diritto."""
        found = self._turned.get((component_id, rotation_deg))
        if found is None:
            found = self.upright[component_id].rotated(rotation_deg)
            self._turned[component_id, rotation_deg] = found
        return found

    def standing_at(self, component_id: str, rotation_deg: int) -> Standing:
        functions, is_inline = self.features[component_id]
        return standing_of(
            self.manifest_at(component_id, rotation_deg).height_mm, functions, is_inline
        )

    def port_at(self, item: PlacedSymbol, port_id: str) -> tuple[Point, PortFace]:
        """Dove sta una porta di un simbolo posato, e dove guarda."""
        port = self.manifest_at(item.component_id, item.rotation_deg).port(port_id)
        return (
            Point(x_mm=item.origin.x_mm + port.x_mm, y_mm=item.origin.y_mm + port.y_mm),
            port.face,
        )

    def _placed(self, component_id: str, origin: Point, rotation_deg: int) -> PlacedSymbol:
        shape = self.manifest_at(component_id, rotation_deg)
        return self.best[component_id].model_copy(
            update={
                "origin": origin,
                "rotation_deg": rotation_deg,
                "width_mm": shape.width_mm,
                "height_mm": shape.height_mm,
            }
        )

    def leader_of(self, component_id: str) -> str:
        """Il pezzo che si muove: un appeso viaggia col pezzo che lo regge."""
        parent = self.parent_of.get(component_id)
        return component_id if parent is None else parent[0]

    def unit_of(self, component_id: str) -> tuple[str, ...]:
        leader = self.leader_of(component_id)
        return (leader, *(child for child, _ in self.children.get(leader, ())))

    # -- la misura ---------------------------------------------------------------

    def measure(self, layout: Iterable[PlacedSymbol] | Move) -> Measured | None:
        """Un instradamento di prova completo, contato contro il tetto.

        Completo vuol dire con gli accessori posati: `settle_sheet` e' la stessa
        funzione con cui la tavola si disegna. `None` e' una posa che non si
        lascia instradare: non e' una candidata.
        """
        table = layout if isinstance(layout, dict) else {
            item.component_id: item for item in layout
        }
        signature = _signature({item: table[item] for item in self.order})
        if signature in self._memo:
            return self._memo[signature]
        self.trials += 1
        symbols = [table[item] for item in self.order]
        try:
            settled = settle_sheet(
                self.project, self.trunks, symbols, self.catalog, self.grid, tolerant=True
            )
        except LayoutError:
            self._memo[signature] = None
            return None
        found = Measured(cost=self.cost_of(table, settled), settled=settled)
        self._memo[signature] = found
        return found

    def cost_of(self, table: Move, settled: SettledSheet) -> SheetCost:
        """Il confronto unico, letto sulla tavola instradata."""
        violations = len(settled.unfit) + self._accessories_out_of_place(settled)
        turnback_runs = 0
        turnback_mm = 0.0
        long_runs = 0
        bends = 0
        crossings = 0
        length_mm = 0.0
        for trunk, route in zip(self.trunks, settled.routes, strict=True):
            arrival = table[trunk.end.component_id]
            goal, _ = self.port_at(arrival, trunk.end.port_id)
            back = max(
                overshoot_beyond_goal_mm(route, goal),
                max(
                    (overshoot_mm(segment, self.step) for segment in route.segments),
                    default=0.0,
                ),
            )
            if back > _TOLERANCE_MM:
                turnback_runs += 1
                turnback_mm += back
            turns = sum(max(len(segment) - 2, 0) for segment in route.segments)
            bends += turns
            if turns > BENDS_PER_RUN_MAX:
                long_runs += 1
            crossings += len(route.crossings)
            length_mm += sum(
                abs(after.x_mm - before.x_mm) + abs(after.y_mm - before.y_mm)
                for segment in route.segments
                for before, after in zip(segment, segment[1:], strict=False)
            )
        box = ink_box(settled.symbols, settled.routes)
        return SheetCost(
            violations=violations,
            turnback_runs=turnback_runs,
            turnback_mm=turnback_mm,
            long_runs=long_runs,
            bends=bends,
            crossings=crossings,
            length_mm=length_mm,
            fill=fill_ratio(settled.symbols, settled.routes, self.sheet_rect),
            imbalance=ink_imbalance(
                settled.symbols,
                settled.routes,
                _centred_on(box, self.sheet_rect),
                self.frame.standard.line_medium_mm,
            ),
        )

    def _accessories_out_of_place(self, settled: SettledSheet) -> int:
        """Accessori addosso a una tratta altrui o a un simbolo (B5, D-027).

        E' la misura del preflight, letta prima che la tavola esista: un
        accessorio e' un simbolo, e una tratta che non e' la sua gli deve stare
        alla distanza di rispetto. Quale sia la sua lo dice la tratta che lo
        porta, non la geometria.
        """
        count = 0
        for accessory in settled.accessories:
            box = box_of(accessory)
            mine = self.owning_run.get(accessory.component_id)
            others = [
                route for index, route in enumerate(settled.routes) if index != mine
            ]
            if run_intrudes_on(box, others, self.clearance):
                count += 1
                continue
            for other in settled.symbols:
                if other is accessory:
                    continue
                if (
                    box[0] < other.right_mm - _TOLERANCE_MM
                    and other.origin.x_mm < box[2] - _TOLERANCE_MM
                    and box[1] < other.bottom_mm - _TOLERANCE_MM
                    and other.origin.y_mm < box[3] - _TOLERANCE_MM
                ):
                    count += 1
                    break
        return count

    # -- le figure -------------------------------------------------------------

    def _neighbours(self, component_id: str) -> frozenset[str]:
        """A cosa un pezzo e' attaccato, senza contare cio' che pende."""
        return frozenset(
            other
            for trunk in self.trunks
            for mine, other in (
                (trunk.start.component_id, trunk.end.component_id),
                (trunk.end.component_id, trunk.start.component_id),
            )
            if mine == component_id and other not in self.parent_of and other in self.best
        )

    def column_of(self, component_id: str) -> tuple[str, ...]:
        """La colonna o la pila a cui un pezzo appartiene, lui compreso.

        Due letture, che sono quelle del posizionamento: chi sta a terra e
        divide la colonna con un altro a terra (D-073), e chi ha lo stesso bordo
        sinistro di un pari — stessi vicini — sopra o sotto di lui (A3, D-119).
        La colonna e' una figura: si trasla insieme, non si sfila.
        """
        leader = self.leader_of(component_id)
        leaders = [item for item in self.scan if item not in self.parent_of]

        def stacked(first: str, second: str) -> bool:
            one, two = self.best[first], self.best[second]
            if (
                self.standings[first] is Standing.GROUND
                and self.standings[second] is Standing.GROUND
                and one.origin.x_mm < two.right_mm - _TOLERANCE_MM
                and two.origin.x_mm < one.right_mm - _TOLERANCE_MM
            ):
                return True
            if abs(one.origin.x_mm - two.origin.x_mm) > _TOLERANCE_MM:
                return False
            apart = (
                one.bottom_mm <= two.origin.y_mm + _TOLERANCE_MM
                or two.bottom_mm <= one.origin.y_mm + _TOLERANCE_MM
            )
            return apart and self._neighbours(first) == self._neighbours(second)

        column = {leader}
        frontier = [leader]
        while frontier:
            current = frontier.pop()
            for other in leaders:
                if other not in column and stacked(current, other):
                    column.add(other)
                    frontier.append(other)
        return tuple(item for item in leaders if item in column)

    # -- come si costruisce una candidata --------------------------------------

    def place_unit(self, leader: str, origin: Point, rotation_deg: int) -> Move:
        """Il pezzo posato la', con cio' che gli pende riappeso al proprio attacco."""
        parent = self._placed(leader, origin, rotation_deg)
        move: Move = {leader: parent}
        for child, port_id in self.children.get(leader, ()):
            move[child] = self._rehung(child, parent, port_id)
        return move

    def _rehung(
        self, child: str, parent: PlacedSymbol, port_id: str, gap_mm: float | None = None
    ) -> PlacedSymbol:
        """L'appeso rimesso dalla parte in cui lo stacco guarda, allo stacco di prima.

        Il figlio si gira, se il manifesto lo ammette, perche' il suo unico
        attacco guardi lo stacco; altrimenti tiene il verso che aveva. Con
        `gap_mm` lo stacco cambia lunghezza: e' la mossa che libera una riga a
        chi deve passarci.
        """
        stub, face = self.port_at(parent, port_id)
        direction = _DIRECTION[face]
        gap = self.hang_gap[child] if gap_mm is None else gap_mm
        current = self.best[child]
        own_port_id = self.upright[child].ports[0].id
        wanted = face.opposite
        rotations = sorted(
            self.upright[child].allowed_rotations_deg,
            key=lambda item: (item != current.rotation_deg, item),
        )
        chosen = current.rotation_deg
        for degrees in rotations:
            if self.manifest_at(child, degrees).port(own_port_id).face is wanted:
                chosen = degrees
                break
        port = self.manifest_at(child, chosen).port(own_port_id)
        origin = Point(
            x_mm=stub.x_mm + direction[0] * gap - port.x_mm,
            y_mm=stub.y_mm + direction[1] * gap - port.y_mm,
        )
        return self._placed(child, origin, chosen)

    def _translated(self, leaders: Iterable[str], dx_mm: float, dy_mm: float) -> Move:
        move: Move = {}
        for leader in leaders:
            here = self.best[leader]
            move.update(
                self.place_unit(
                    leader,
                    Point(x_mm=here.origin.x_mm + dx_mm, y_mm=here.origin.y_mm + dy_mm),
                    here.rotation_deg,
                )
            )
        return move

    def _need_mm(self, trunk: Trunk) -> float:
        """La distanza minima fra due porte affacciate su questa tratta.

        Il rettilineo che gli accessori pretendono, e mai meno dello stacco
        minimo fra due simboli (D-062).
        """
        return _snap_up(max(ROW_GAP_MM, self.room[trunk.connection_ids]), self.step)

    def _facing_rotations(self, component_id: str, port_id: str, wanted: PortFace) -> list[int]:
        """Le rotazioni ammesse che portano la porta a guardare da quella parte,
        prima quella attuale."""
        current = self.best[component_id].rotation_deg
        return [
            degrees
            for degrees in sorted(
                self.upright[component_id].allowed_rotations_deg,
                key=lambda item: (item != current, item),
            )
            if self.manifest_at(component_id, degrees).port(port_id).face is wanted
        ]

    def _trunks_of(self, leader: str) -> list[tuple[Trunk, str, str, str]]:
        """Le tratte fra questo pezzo e un pezzo di un'altra figura:
        `(tratta, porta mia, pezzo pari, porta del pari)`."""
        unit = set(self.unit_of(leader))
        found: list[tuple[Trunk, str, str, str]] = []
        for trunk in self.trunks:
            for mine, other in ((trunk.start, trunk.end), (trunk.end, trunk.start)):
                if mine.component_id != leader:
                    continue
                if other.component_id in unit or other.component_id not in self.best:
                    continue
                found.append((trunk, mine.port_id, other.component_id, other.port_id))
        return found

    def _port_moves(self, leader: str) -> list[Move]:
        """Le pose ricavate dalle porte dei vicini collegati.

        Per ogni tratta verso un pari gia' posato: la quota che allinea le due
        porte; la posa affacciata alla distanza minima che lascia il rettilineo
        agli accessori, dalla parte in cui la porta del pari guarda, con la
        rotazione che rivolge la propria porta verso di lui; e la stessa con
        qualche passo di gioco.
        """
        out: list[Move] = []
        me = self.best[leader]
        for trunk, my_port, peer_id, peer_port in self._trunks_of(leader):
            peer = self.best[peer_id]
            anchor, face = self.port_at(peer, peer_port)
            direction = _DIRECTION[face]
            need = self._need_mm(trunk)
            rotations = self._facing_rotations(leader, my_port, face.opposite)
            if me.rotation_deg not in rotations:
                rotations = [me.rotation_deg, *rotations]
            grounded = self.standings[leader] is Standing.GROUND
            for degrees in rotations:
                port = self.manifest_at(leader, degrees).port(my_port)
                # (a) allineamento: la porta sulla riga (o sulla colonna) della
                # porta del pari, senza muoversi lungo l'asse del collegamento.
                # Chi sta a terra non cambia quota: si allinea solo in ascissa.
                if face in _HORIZONTAL_FACES:
                    if grounded:
                        continue
                    aligned = Point(x_mm=me.origin.x_mm, y_mm=anchor.y_mm - port.y_mm)
                else:
                    aligned = Point(x_mm=anchor.x_mm - port.x_mm, y_mm=me.origin.y_mm)
                out.append(self.place_unit(leader, aligned, degrees))
            for degrees in rotations:
                port = self.manifest_at(leader, degrees).port(my_port)
                # (b) affacciato alla distanza minima, e con un po' di gioco.
                if port.face is not face.opposite:
                    continue
                for slack in SLACK_STEPS:
                    reach = need + slack * self.step
                    origin = Point(
                        x_mm=anchor.x_mm + direction[0] * reach - port.x_mm,
                        y_mm=me.origin.y_mm if grounded else anchor.y_mm + direction[1] * reach - port.y_mm,
                    )
                    out.append(self.place_unit(leader, origin, degrees))
        return out

    def _chain_moves(self, leader: str) -> list[Move]:
        """La catena di raccordi rimessa in fila dalla porta di un pezzo grosso.

        Dal capo attaccato all'ancora si cammina lungo la direzione in cui la
        porta dell'ancora guarda: ogni membro prende la rotazione che rivolge la
        propria porta d'ingresso all'indietro, si posa alla distanza minima che
        la tratta pretende, e se la sua porta d'uscita guarda altrove la fila
        gira con lei. E' la posa che un tecnico disegna a mano, e nessuna
        traslazione di un pezzo solo la raggiunge.
        """
        out: list[Move] = []
        for chain in self.chains:
            if leader not in chain:
                continue
            for members in (chain, tuple(reversed(chain))):
                head = members[0]
                for trunk, my_port, anchor_id, anchor_port in self._trunks_of(head):
                    if anchor_id in chain:
                        continue
                    for slack in SLACK_STEPS:
                        laid = self._lay(members, anchor_id, anchor_port, trunk, my_port, slack)
                        if laid is not None:
                            out.append(laid)
        return out

    def _lay(
        self,
        members: tuple[str, ...],
        anchor_id: str,
        anchor_port: str,
        first_trunk: Trunk,
        first_port: str,
        slack: int,
    ) -> Move | None:
        move: Move = {}
        anchor, face = self.port_at(self.best[anchor_id], anchor_port)
        trunk, entry_port = first_trunk, first_port
        for index, member in enumerate(members):
            direction = _DIRECTION[face]
            reach = self._need_mm(trunk) + slack * self.step
            rotations = self._facing_rotations(member, entry_port, face.opposite)
            degrees = rotations[0] if rotations else self.best[member].rotation_deg
            port = self.manifest_at(member, degrees).port(entry_port)
            origin = Point(
                x_mm=anchor.x_mm + direction[0] * reach - port.x_mm,
                y_mm=anchor.y_mm + direction[1] * reach - port.y_mm,
            )
            move.update(self.place_unit(member, origin, degrees))
            if index == len(members) - 1:
                break
            following = members[index + 1]
            link = next(
                (
                    (item, mine.port_id, other.port_id)
                    for item in self.trunks
                    for mine, other in ((item.start, item.end), (item.end, item.start))
                    if mine.component_id == member and other.component_id == following
                ),
                None,
            )
            if link is None:
                return None
            trunk, exit_port, entry_port = link
            anchor, face = self.port_at(move[member], exit_port)
        return move

    def _column_moves(self, leader: str) -> list[Move]:
        """La pila o la colonna traslata come gruppo, per gli stessi motivi per
        cui uno dei suoi membri si muoverebbe da solo."""
        column = self.column_of(leader)
        if len(column) < 2:
            return []
        grounded = any(self.standings[item] is Standing.GROUND for item in column)
        out: list[Move] = []
        seen: set[tuple[float, float]] = set()
        for member in column:
            here = self.best[member]
            for single in self._port_moves(member):
                target = single[member]
                if target.rotation_deg != here.rotation_deg:
                    continue
                dx = target.origin.x_mm - here.origin.x_mm
                dy = 0.0 if grounded else target.origin.y_mm - here.origin.y_mm
                if (dx, dy) == (0.0, 0.0) or (dx, dy) in seen:
                    continue
                seen.add((dx, dy))
                out.append(self._translated(column, dx, dy))
        return out

    def _shift_moves(self, leader: str) -> list[Move]:
        """Tutto cio' che sta oltre un pezzo si avvicina al pezzo che lo precede.

        E' l'avvicinamento di un gruppo funzionale al successivo: si sposta in
        blocco cio' che sta a destra del bordo sinistro del pezzo — lui compreso
        — di quanto serve a chiudere il varco con cio' che sta a sinistra, o di
        quanto una tratta che attraversa quel confine chiede per affacciare le
        proprie porte. E specularmente verso destra, per chi sta a sinistra.
        """
        out: list[Move] = []
        me = self.best[leader]
        leaders = [item for item in self.scan if item not in self.parent_of]
        for rightwards in (False, True):
            if rightwards:
                group = [
                    item for item in leaders if self.best[item].right_mm <= me.right_mm + _TOLERANCE_MM
                ]
                rest = [item for item in leaders if item not in group]
                if not rest:
                    continue
                gap = min(self.best[item].origin.x_mm for item in rest) - max(
                    self.best[item].right_mm for item in group
                )
                sign = 1.0
            else:
                group = [
                    item for item in leaders if self.best[item].origin.x_mm >= me.origin.x_mm - _TOLERANCE_MM
                ]
                rest = [item for item in leaders if item not in group]
                if not rest:
                    continue
                gap = min(self.best[item].origin.x_mm for item in group) - max(
                    self.best[item].right_mm for item in rest
                )
                sign = -1.0
            deltas: list[float] = []
            closing = gap - ROW_GAP_MM
            if closing > _TOLERANCE_MM:
                deltas.append(sign * (int(closing / self.step) * self.step))
            crossing = set(group)
            for trunk in self.trunks:
                one, two = trunk.start, trunk.end
                if (one.component_id in crossing) == (two.component_id in crossing):
                    continue
                if one.component_id not in self.best or two.component_id not in self.best:
                    continue
                first, _ = self.port_at(self.best[one.component_id], one.port_id)
                second, _ = self.port_at(self.best[two.component_id], two.port_id)
                inner = first if one.component_id in crossing else second
                outer = second if one.component_id in crossing else first
                span = abs(inner.x_mm - outer.x_mm) - self._need_mm(trunk)
                if span > _TOLERANCE_MM:
                    deltas.append(sign * (int(span / self.step) * self.step))
            seen: set[float] = set()
            for delta in deltas:
                if delta == 0.0 or delta in seen:
                    continue
                seen.add(delta)
                out.append(self._translated(group, delta, 0.0))
        return out

    def _collisions(self, move: Move) -> list[tuple[str, PlacedSymbol, PlacedSymbol]]:
        """Le figure ferme contro cui una candidata va a sbattere: `(capo, mio, suo)`."""
        after = dict(self.best)
        after.update(move)
        moved_units = {self.leader_of(item) for item in move}
        found: list[tuple[str, PlacedSymbol, PlacedSymbol]] = []
        for other_id in self.order:
            leader = self.leader_of(other_id)
            if leader in moved_units:
                continue
            other = after[other_id]
            for item in move:
                mine = after[item]
                if (
                    mine.origin.x_mm < other.right_mm + ROW_GAP_MM - _TOLERANCE_MM
                    and other.origin.x_mm - ROW_GAP_MM < mine.right_mm - _TOLERANCE_MM
                    and mine.origin.y_mm < other.bottom_mm + ROW_GAP_MM - _TOLERANCE_MM
                    and other.origin.y_mm - ROW_GAP_MM < mine.bottom_mm - _TOLERANCE_MM
                ):
                    found.append((leader, mine, other))
        return found

    def _with_room(self, move: Move, direction: tuple[float, float]) -> list[Move]:
        """La stessa candidata, con lo spazio che le manca aperto lungo il suo asse.

        Una posa ricavata dalle porte puo' finire addosso a chi sta gia' li':
        non e' una ragione per scartarla, e' una ragione per spostare anche gli
        altri, che costano zero (D-078). Tre varianti, tutte lungo l'asse della
        mossa: si **spinge** chi e' addosso nel verso della mossa, a cascata con
        chi gli sta oltre; lo si spinge nel verso **opposto**, quando e' il
        posto davanti a una porta a dover essere liberato da chi lo occupava;
        oppure si **arretra** la mossa con tutto cio' che le sta dietro, il
        pezzo grosso da cui e' partita compreso. Chi sta a terra si sposta solo
        in orizzontale: lungo un asse verticale la variante che lo toccherebbe
        non e' valida, e cade da sola.
        """
        collisions = self._collisions(move)
        if not collisions:
            return []
        horizontal = direction[0] != 0.0
        sign = direction[0] if horizontal else direction[1]
        out: list[Move] = []
        for push in (sign, -sign):
            pushed = self._pushed(move, horizontal, push)
            if pushed is not None:
                out.append(pushed)
        retreated = self._retreated(move, collisions, horizontal, sign)
        if retreated is not None:
            out.append(retreated)
        return out

    def _low(self, item: PlacedSymbol, horizontal: bool) -> float:
        return item.origin.x_mm if horizontal else item.origin.y_mm

    def _high(self, item: PlacedSymbol, horizontal: bool) -> float:
        return item.right_mm if horizontal else item.bottom_mm

    def _overlap(
        self, mine: PlacedSymbol, other: PlacedSymbol, horizontal: bool, sign: float
    ) -> float:
        """Di quanto l'altro va spostato nel verso dato per liberare lo stacco."""
        if sign > 0:
            return self._high(mine, horizontal) + ROW_GAP_MM - self._low(other, horizontal)
        return self._high(other, horizontal) + ROW_GAP_MM - self._low(mine, horizontal)

    def _shifted_units(self, items: Iterable[str], horizontal: bool, amount: float) -> Move:
        leaders = sorted({self.leader_of(item) for item in items}, key=self.scan.index)
        return self._translated(
            leaders, amount if horizontal else 0.0, 0.0 if horizontal else amount
        )

    def _pushed(self, move: Move, horizontal: bool, sign: float) -> Move | None:
        """Chi e' addosso alla mossa si sposta nel verso dato, e chi gli sta
        oltre lo segue di altrettanto, a cascata."""
        pushed = dict(move)
        for _ in range(len(self.order)):
            hits = self._collisions(pushed)
            if not hits:
                return pushed
            amount = _snap_up(
                max(self._overlap(mine, other, horizontal, sign) for _, mine, other in hits),
                self.step,
            )
            if amount <= 0.0:
                return None
            edge = (
                min(self._low(other, horizontal) for _, _, other in hits)
                if sign > 0
                else max(self._high(other, horizontal) for _, _, other in hits)
            )
            taken = {self.leader_of(key) for key in pushed}
            beyond = [
                item
                for item in self.order
                if self.leader_of(item) not in taken
                and (
                    self._low(self.best[item], horizontal) >= edge - _TOLERANCE_MM
                    if sign > 0
                    else self._high(self.best[item], horizontal) <= edge + _TOLERANCE_MM
                )
            ]
            for column_member in list(beyond):
                beyond.extend(
                    mate for mate in self.column_of(column_member) if mate not in beyond
                )
            pushed = {**self._shifted_units(beyond, horizontal, sign * amount), **pushed}
        return None

    def _retreated(
        self,
        move: Move,
        collisions: list[tuple[str, PlacedSymbol, PlacedSymbol]],
        horizontal: bool,
        sign: float,
    ) -> Move | None:
        """La mossa e tutto cio' che le sta alle spalle — chi non collide e sta
        dal lato da cui e' partita — indietreggiano di quanto serve; chi
        collideva resta dov'e'."""
        amount = _snap_up(
            max(self._overlap(mine, other, horizontal, sign) for _, mine, other in collisions),
            self.step,
        )
        colliding = {leader for leader, _, _ in collisions}
        moving = {self.leader_of(key) for key in move}
        front = (
            min(self._low(item, horizontal) for item in move.values())
            if sign > 0
            else max(self._high(item, horizontal) for item in move.values())
        )
        behind = [
            item
            for item in self.order
            if self.leader_of(item) not in colliding
            and self.leader_of(item) not in moving
            and (
                self._high(self.best[item], horizontal) <= front + _TOLERANCE_MM
                if sign > 0
                else self._low(self.best[item], horizontal) >= front - _TOLERANCE_MM
            )
        ]
        for column_member in list(behind):
            behind.extend(mate for mate in self.column_of(column_member) if mate not in behind)
        retreated: Move = {}
        for item, placed in move.items():
            retreated[item] = placed.model_copy(
                update={
                    "origin": Point(
                        x_mm=placed.origin.x_mm - (sign * amount if horizontal else 0.0),
                        y_mm=placed.origin.y_mm - (0.0 if horizontal else sign * amount),
                    )
                }
            )
        retreated.update(self._shifted_units(behind, horizontal, -sign * amount))
        if self._collisions(retreated):
            return None
        return retreated

    def _swap_moves(self, leader: str) -> list[Move]:
        """Due membri di una pila si scambiano di posto.

        Con due macchine impilate, quale sta sopra decide da che parte i
        raccordi le ricevono: un raccordo a T ha una mano sola, e la macchina
        che gli entra dall'alto non puo' essere quella che sta sotto.
        """
        column = self.column_of(leader)
        out: list[Move] = []
        me = self.best[leader]
        for mate in column:
            if mate == leader:
                continue
            other = self.best[mate]
            if abs(other.origin.x_mm - me.origin.x_mm) > _TOLERANCE_MM:
                continue
            # Ognuno prende l'origine dell'altro; chi e' piu' alto si allinea
            # in basso al posto che prende, come una macchina a terra.
            mine = Point(x_mm=other.origin.x_mm, y_mm=other.bottom_mm - me.height_mm)
            theirs = Point(x_mm=me.origin.x_mm, y_mm=me.bottom_mm - other.height_mm)
            move = self.place_unit(leader, mine, me.rotation_deg)
            move.update(self.place_unit(mate, theirs, other.rotation_deg))
            out.append(move)
            # Lo scambio da solo raramente paga: e' il raccordo che li serve a
            # doversi rimettere in fila dalla porta che ora gli sta davanti.
            # Le catene e le pose da porta dei vicini si ricavano **sulla pila
            # gia' scambiata**, e viaggiano nella stessa mossa.
            out.extend(self._composed_with(move, (leader, mate)))
        return out

    def _composed_with(self, move: Move, around: tuple[str, ...]) -> list[Move]:
        """Le mosse dei vicini, ricavate come se `move` fosse gia' stata fatta."""
        saved = self.best
        self.best = {**saved, **move}
        try:
            neighbours = [
                item
                for item in self.scan
                if item not in self.parent_of
                and item not in around
                and any(item in self._neighbours(member) for member in around)
            ]
            out: list[Move] = []
            for neighbour in neighbours:
                for extra in self._chain_moves(neighbour) + self._port_moves(neighbour):
                    out.append({**move, **extra})
            return out
        finally:
            self.best = saved

    def _hang_moves(self, leader: str) -> list[Move]:
        """Lo stacco di un appeso si allunga o si accorcia di qualche passo.

        Un appeso porta i propri organi sullo stacco, e quegli organi occupano
        una riga: la tratta di un altro pezzo che deve passarci trova la strada
        chiusa e gira. Spostare l'appeso di un passo la riapre, e costa zero.
        """
        out: list[Move] = []
        parent = self.best[leader]
        for child, port_id in self.children.get(leader, ()):
            for count in (1, 2, -1):
                gap = self.hang_gap[child] + count * self.step
                if gap < ROW_GAP_MM - _TOLERANCE_MM:
                    continue
                out.append({child: self._rehung(child, parent, port_id, gap)})
        return out

    def _refresh_hang_gaps(self) -> None:
        """Gli stacchi degli appesi, riletti dalla posa corrente."""
        for child, (parent, port_id) in self.parent_of.items():
            stub, _ = self.port_at(self.best[parent], port_id)
            own, _ = self.port_at(self.best[child], self.upright[child].ports[0].id)
            self.hang_gap[child] = max(abs(own.x_mm - stub.x_mm), abs(own.y_mm - stub.y_mm))

    def _rotation_moves(self, leader: str) -> list[Move]:
        me = self.best[leader]
        return [
            self.place_unit(leader, me.origin, degrees)
            for degrees in sorted(self.upright[leader].allowed_rotations_deg)
            if degrees != me.rotation_deg
        ]

    def _nudge_moves(self, leader: str) -> list[Move]:
        """Le traslazioni cieche: in alto prima che in basso, vicino prima che
        lontano; poi le orizzontali, che l'ordine di processo limita."""
        me = self.best[leader]
        column = self.column_of(leader)
        out: list[Move] = []
        for count in NUDGE_STEPS:
            for dy in (-count * self.step, count * self.step):
                out.append(self.place_unit(leader, Point(x_mm=me.origin.x_mm, y_mm=me.origin.y_mm + dy), me.rotation_deg))
        for count in NUDGE_STEPS:
            for dx in (-count * self.step, count * self.step):
                if len(column) > 1:
                    out.append(self._translated(column, dx, 0.0))
                else:
                    out.append(self.place_unit(leader, Point(x_mm=me.origin.x_mm + dx, y_mm=me.origin.y_mm), me.rotation_deg))
        return out

    def _axis_of(self, move: Move) -> tuple[float, float]:
        """Il verso di una candidata: dove il suo baricentro e' andato."""
        before_x = before_y = after_x = after_y = 0.0
        for item, placed in move.items():
            was = self.best[item]
            before_x += was.origin.x_mm
            before_y += was.origin.y_mm
            after_x += placed.origin.x_mm
            after_y += placed.origin.y_mm
        dx, dy = after_x - before_x, after_y - before_y
        if abs(dx) >= abs(dy):
            return (1.0, 0.0) if dx >= 0 else (-1.0, 0.0)
        return (0.0, 1.0) if dy > 0 else (0.0, -1.0)

    def candidates(self, component_id: str) -> list[Move]:
        """Le mosse alternative per un pezzo, in ordine fisso e senza doppioni.

        Prima le pose ricavate dalla topologia — catene, porte, colonne, gruppi
        — poi le rotazioni, infine le traslazioni cieche. Ogni mossa porta la
        posa nuova dei soli simboli che cambiano.
        """
        leader = self.leader_of(component_id)
        chained = self._chain_moves(leader)
        ported = self._port_moves(leader)
        roomy: list[Move] = []
        for move in chained + ported:
            roomy.extend(self._with_room(move, self._axis_of(move)))
        generated = (
            chained
            + ported
            + roomy
            + self._column_moves(leader)
            + self._shift_moves(leader)
            + self._swap_moves(leader)
            + self._hang_moves(leader)
            + self._rotation_moves(leader)
            + self._nudge_moves(leader)
        )
        # Chi divide una pila a terra con altri non se ne sfila: una mossa che
        # lo sposta in orizzontale porta con se' i compagni, dello stesso tanto.
        # Chi sta su una tubazione prova tutte e due le cose: da solo e in
        # colonna, e decide il costo.
        column = self.column_of(leader)
        if len(column) > 1:
            completed: list[Move] = []
            grounded = self.standings[leader] is Standing.GROUND
            for move in generated:
                if leader not in move:
                    completed.append(move)
                    continue
                dx = move[leader].origin.x_mm - self.best[leader].origin.x_mm
                mates = [item for item in column if item != leader and item not in move]
                if dx == 0.0 or not mates:
                    completed.append(move)
                    continue
                if not grounded:
                    completed.append(move)
                completed.append({**self._translated(mates, dx, 0.0), **move})
            generated = completed
        out: list[Move] = []
        seen: set[tuple[tuple[str, float, float, int], ...]] = set()
        for move in generated:
            changed = {
                item: placed
                for item, placed in move.items()
                if (placed.origin, placed.rotation_deg)
                != (self.best[item].origin, self.best[item].rotation_deg)
            }
            if not changed:
                continue
            key = _signature(dict(sorted(changed.items())))
            if key in seen:
                continue
            seen.add(key)
            out.append(changed)
        return out

    # -- la validita' --------------------------------------------------------

    def is_valid(self, move: Move) -> bool:
        """I vincoli che nessun guadagno compra: standing, terra, griglia, area,
        stacchi, colonne intere, ordine di processo."""
        after = dict(self.best)
        after.update(move)
        moved_leaders = {self.leader_of(item) for item in move}
        units = {item: self.leader_of(item) for item in self.order}
        for item, placed in move.items():
            before = self.best[item]
            if self.standing_at(item, placed.rotation_deg) is not self.standings[item]:
                return False
            if self.standings[item] is Standing.GROUND and item not in self.parent_of:
                if placed.height_mm != before.height_mm:
                    return False
                if placed.origin.y_mm != before.origin.y_mm and not self._swapped_in_column(
                    item, move
                ):
                    return False
            if not is_on_grid(placed.origin.x_mm - self.area.x_mm, self.step):
                return False
            if not is_on_grid(placed.origin.y_mm - self.area.y_mm, self.step):
                return False
            if placed.origin.x_mm < self.area.x_mm - _TOLERANCE_MM:
                return False
            if placed.origin.y_mm < self.area.y_mm - _TOLERANCE_MM:
                return False
            if placed.right_mm > self.area.right_mm + _TOLERANCE_MM:
                return False
            if placed.bottom_mm > self.levels.ground_mm + _TOLERANCE_MM:
                return False
            # Lo stesso stacco del posizionamento fra due simboli di figure
            # diverse (D-062); dentro la stessa figura basta non sovrapporsi.
            for other_id in self.order:
                if other_id == item:
                    continue
                other = after[other_id]
                gap = 0.0 if units[other_id] == units[item] else ROW_GAP_MM
                if (
                    placed.origin.x_mm < other.right_mm + gap - _TOLERANCE_MM
                    and other.origin.x_mm - gap < placed.right_mm - _TOLERANCE_MM
                    and placed.origin.y_mm < other.bottom_mm + gap - _TOLERANCE_MM
                    and other.origin.y_mm - gap < placed.bottom_mm - _TOLERANCE_MM
                ):
                    return False
        # Una pila a terra non si sfila di un elemento (D-073): chi la divide
        # con un altro si sposta in orizzontale solo insieme a lui. Chi sta su
        # una tubazione e divide la colonna con un pari puo' anche muoversi da
        # solo: la mossa di gruppo esiste comunque, e decide il costo.
        for leader in moved_leaders:
            if move.get(leader, self.best[leader]).origin.x_mm == self.best[leader].origin.x_mm:
                continue
            if self.standings[leader] is not Standing.GROUND:
                continue
            column = self.column_of(leader)
            dx = move[leader].origin.x_mm - self.best[leader].origin.x_mm
            for mate in column:
                if mate == leader:
                    continue
                if mate not in move or move[mate].origin.x_mm - self.best[mate].origin.x_mm != dx:
                    return False
        # L'ordine di processo e' un vincolo, non un costo (D-060), e si legge
        # sul verso del fluido: la mandata va a destra, il ritorno torna a
        # sinistra. Una posa che gia' contraddice il verso puo' essere corretta,
        # e nessuna puo' cominciare a contraddirlo; dove il verso non e' deciso
        # vale l'ordine gia' disegnato.
        for trunk in self.trunks:
            start_id, end_id = trunk.start.component_id, trunk.end.component_id
            if start_id == end_id or start_id not in self.best or end_id not in self.best:
                continue
            if units[start_id] == units[end_id]:
                continue
            if units[start_id] not in moved_leaders and units[end_id] not in moved_leaders:
                continue

            def centre(table: Move, item: str) -> float:
                return table[item].origin.x_mm + table[item].width_mm / 2

            was = _relation(centre(self.best, start_id), centre(self.best, end_id))
            now = _relation(centre(after, start_id), centre(after, end_id))
            if now == was:
                continue
            flow = self.flow.get(trunk.connection_ids)
            if flow is True and now <= 0:
                continue
            if flow is False and now >= 0:
                continue
            return False
        return True

    def _swapped_in_column(self, item: str, move: Move) -> bool:
        """Vero se la quota nuova e' quella che un compagno di pila lascia.

        Chi sta a terra non vola: le quote di una pila restano quelle che il
        posizionamento ha deciso, e i suoi membri possono solo scambiarsele.
        """
        column = [mate for mate in self.column_of(item) if self.standings[mate] is Standing.GROUND]
        if len(column) < 2:
            return False
        before = sorted(self.best[mate].bottom_mm for mate in column)
        after = sorted(move.get(mate, self.best[mate]).bottom_mm for mate in column)
        return before == after

    # -- il ciclo --------------------------------------------------------------

    def _offenders(self, current: Measured) -> list[str]:
        """I pezzi ai capi di una tratta che costa qualcosa, in ordine di posa."""
        guilty: set[str] = set()
        for index, (trunk, route) in enumerate(
            zip(self.trunks, current.settled.routes, strict=True)
        ):
            has_bends = any(len(segment) > 2 for segment in route.segments)
            arrival = self.best[trunk.end.component_id]
            goal, _ = self.port_at(arrival, trunk.end.port_id)
            turned_back = overshoot_beyond_goal_mm(route, goal) > _TOLERANCE_MM or any(
                overshoot_mm(segment, self.step) > _TOLERANCE_MM for segment in route.segments
            )
            far = sum(
                abs(after.x_mm - before.x_mm) + abs(after.y_mm - before.y_mm)
                for segment in route.segments
                for before, after in zip(segment, segment[1:], strict=False)
            ) > self._need_mm(trunk) + _TOLERANCE_MM
            if has_bends or route.crossings or index in current.settled.unfit or turned_back or far:
                guilty.add(self.leader_of(trunk.start.component_id))
                guilty.add(self.leader_of(trunk.end.component_id))
        return [item for item in self.scan if item in guilty]

    def run(self) -> list[PlacedSymbol]:
        """Greedy, lessicografico, limitato: la prima mossa che batte la posa
        corrente sul confronto unico si tiene; una passata senza mosse chiude."""
        current = self.measure(self.best)
        if current is None:
            return [self.best[item] for item in self.order]
        for _ in range(MAX_PASSES):
            moved = False
            for leader in self._offenders(current):
                for move in self.candidates(leader):
                    if self.trials >= MAX_TRIAL_ROUTINGS:
                        return [self.best[item] for item in self.order]
                    if not self.is_valid(move):
                        continue
                    trial = dict(self.best)
                    trial.update(move)
                    found = self.measure(trial)
                    if found is None or not found.cost.beats(current.cost):
                        continue
                    self.best = trial
                    self._refresh_hang_gaps()
                    current = found
                    moved = True
                    break
            if not moved:
                break
        return [self.best[item] for item in self.order]


def improve_sheet(
    project: ProjectModel,
    partition: SheetPartition,
    catalog: ComponentRegistry,
    frame: SheetFrame,
    placed: list[PlacedSymbol],
    inline_ids: frozenset[str],
) -> list[PlacedSymbol]:
    """Rivede la disposizione reinstradando: si tiene solo cio' che batte la
    posa corrente sul confronto unico della tavola (`SheetCost`)."""
    if not placed or not partition.trunks:
        return list(placed)
    return Improver(project, partition, catalog, frame, placed, inline_ids).run()


__all__ = [
    "MAX_PASSES",
    "MAX_TRIAL_ROUTINGS",
    "Improver",
    "Measured",
    "Move",
    "SheetCost",
    "improve_sheet",
    "objective_of",
    "overshoot_beyond_goal_mm",
    "overshoots_the_goal",
]
