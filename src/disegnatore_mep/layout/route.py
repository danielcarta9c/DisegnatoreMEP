"""Instradamento ortogonale, con la funzione di costo che il PM ha dettato.

«La regola e' minimizzare le curve disegnate, minimizzare gli attraversamenti
fra linee e minimizzare la lunghezza delle linee, mantenendo pero' ordinamenti
da sinistra a destra.» Le tre voci sono in ordine di peso, e la funzione di
costo le riporta in quell'ordine: una piega costa dieci passi, un
attraversamento tre, un passo uno. L'ordinamento da sinistra a destra non e'
una voce di costo: e' un vincolo, e lo garantisce il posizionamento.

Prima queste tre voci stavano quasi alla pari — piega 15 contro passo 10 — e il
risultato era un instradatore che serpeggiava per accorciare di due millimetri.
Le tubazioni che ne uscivano salivano e scendevano intorno ai componenti senza
motivo, ed e' il secondo difetto che il PM ha visto sulla tavola.

D-041 resta valida e diventa piu' forte: l'incrocio e' economico e il giro
lungo e' carissimo. Attraversare costa un `CROSS_COST`; il giro minimo per
schivare una cella occupata su un rettilineo vale due passi **e quattro
pieghe**, che e' quello che costa davvero e che la vecchia formulazione
tralasciava.
"""

import heapq
from collections.abc import Callable
from dataclasses import dataclass

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.symbol import PortFace
from disegnatore_mep.model.project import PortRef, ProjectModel

from .composition import levels_of
from .errors import LayoutError
from .flow import orient_trunks
from .geometry import PlacedSymbol, Point, RoutedTrunk
from .grid import Cell, GridSpace
from .trunks import Trunk

STEP_COST = 10
"""Costo di un passo di griglia: la lunghezza della linea, terza voce."""

TURN_COST = 100
"""Costo di una piega: dieci passi, cioe' 25 mm di tubazione.

E' la voce dominante perche' e' la prima della regola. Con un valore vicino a
quello del passo l'instradatore compra pieghe per risparmiare lunghezza, e la
tavola si riempie di sali-scendi.
"""

CROSS_COST = 30
"""Costo di una cella gia' percorsa da un'altra rete.

Sta fra la piega e il passo, come nella regola. Attraversare ne tocca una sola
e costa 30; schivarla su un rettilineo costa due passi e quattro pieghe, cioe'
420: l'instradatore non deviera' mai per evitare un incrocio (D-041).
Costeggiare la paga invece a ogni cella e supera presto il costo di scostarsi
di una corsia, che sono due passi e quattro pieghe una volta sola.
"""

HUG_COST = 4
"""Costo di una cella a un passo da un ostacolo o da un'altra tubazione.

Una linea che corre a due millimetri e mezzo dal bordo di un simbolo, o
affiancata a un'altra linea, sulla carta si legge come se ci passasse sopra.
Costa poco — meno di mezzo passo — perche' non deve mai far girare una rotta:
deve solo farle scegliere la corsia libera quando ce n'e' una.
"""

MAX_EXPANSIONS = 400_000
"""Limite di iterazioni: oltre, si restituisce una diagnostica, non si continua."""

DIRECTIONS: tuple[Cell, ...] = ((1, 0), (0, 1), (-1, 0), (0, -1))
"""Ordine fisso dei vicini: da esso dipende il determinismo a parita' di costo."""


_FACE_DIRECTION: dict[PortFace, Cell] = {
    PortFace.RIGHT: (1, 0),
    PortFace.BOTTOM: (0, 1),
    PortFace.LEFT: (-1, 0),
    PortFace.TOP: (0, -1),
}


@dataclass(frozen=True)
class Route:
    cells: tuple[Cell, ...]
    cost: int
    crossings: tuple[Cell, ...]

    @property
    def vertices(self) -> tuple[Cell, ...]:
        """Solo i vertici della spezzata: dove cambia direzione."""
        if len(self.cells) < 3:
            return self.cells
        out = [self.cells[0]]
        for before, here, after in zip(self.cells, self.cells[1:], self.cells[2:], strict=False):
            if (here[0] - before[0], here[1] - before[1]) != (
                after[0] - here[0],
                after[1] - here[1],
            ):
                out.append(here)
        out.append(self.cells[-1])
        return tuple(out)


def route(
    start: Cell,
    start_direction: Cell,
    goal: Cell,
    goal_direction: Cell,
    *,
    cols: int,
    rows: int,
    blocked: frozenset[Cell],
    occupied: frozenset[Cell],
    taken: frozenset[tuple[Cell, Cell]] = frozenset(),
    crowded: frozenset[Cell] = frozenset(),
    prefer_high: bool | None = None,
    max_expansions: int = MAX_EXPANSIONS,
) -> Route:
    """A* su stato `(cella, direzione di arrivo)`.

    La direzione entra nello stato perche' il costo di piega dipende da come ci
    si e' arrivati.

    `start_direction` e `goal_direction` sono le direzioni **uscenti** delle due
    porte, cioe' dove la porta guarda. Vanno derivate da `PortFace`, non passate
    a mano: al contrario l'instradatore non fallisce, costruisce un cappio che
    rientra dal lato sbagliato.

    `taken` sono i **tratti** gia' percorsi da altre tubazioni, e sono vietati:
    due linee sovrapposte per il lungo si leggono come una sola. `occupied` sono
    invece i **nodi**, che si possono attraversare pagando: attraversare e'
    trasversale, sovrapporsi e' longitudinale, e le due cose non vanno confuse.
    `crowded` sono i nodi a un passo da un ostacolo o da un'altra linea.

    `prefer_high` non cambia il costo: sceglie **fra percorsi di pari costo**
    quello che corre piu' in alto (`True`) o piu' in basso (`False`). E' cosi'
    che la mandata finisce sopra il ritorno senza pagarlo in pieghe: su una
    griglia i percorsi ottimi sono quasi sempre molti, e uno vale l'altro
    finche' non lo si sceglie.
    """
    approach = (-goal_direction[0], -goal_direction[1])

    def heuristic(cell: Cell, direction: Cell) -> int:
        dx, dy = goal[0] - cell[0], goal[1] - cell[1]
        distance = (abs(dx) + abs(dy)) * STEP_COST
        # Ammissibile e piu' stretta della sola Manhattan: se la meta' non e'
        # allineata serve almeno una piega, e se si sta andando dalla parte
        # opposta ne servono almeno due. Senza, con TURN_COST dominante, l'A*
        # degenera in Dijkstra ed esplora l'intero foglio.
        turns = 0
        if dx != 0 and dy != 0:
            turns = 1
        if (dx != 0 and dx * direction[0] < 0) or (dy != 0 and dy * direction[1] < 0):
            turns = 2
        return distance + turns * TURN_COST

    def lean(cell: Cell) -> int:
        if prefer_high is None:
            return 0
        return cell[1] if prefer_high else rows - cell[1]

    open_heap: list[tuple[int, int, int, Cell, Cell]] = [
        (heuristic(start, start_direction), lean(start), 0, start, start_direction)
    ]
    best: dict[tuple[Cell, Cell], tuple[int, int]] = {
        (start, start_direction): (0, lean(start))
    }
    came: dict[tuple[Cell, Cell], tuple[Cell, Cell]] = {}
    expansions = 0

    while open_heap:
        _, bias, cost, cell, direction = heapq.heappop(open_heap)
        if (cost, bias) > best.get((cell, direction), (cost, bias)):
            continue
        if cell == goal and direction == approach:
            cells = [cell]
            state = (cell, direction)
            while state in came:
                state = came[state]
                cells.append(state[0])
            cells.reverse()
            return Route(
                cells=tuple(cells),
                cost=cost,
                crossings=tuple(item for item in cells if item in occupied),
            )

        expansions += 1
        if expansions > max_expansions:
            raise LayoutError(
                f"no route from {start} to {goal} within {max_expansions} expansions: "
                f"the layout did not converge, try a different partition"
            )

        for step in DIRECTIONS:
            nxt = (cell[0] + step[0], cell[1] + step[1])
            if not (0 <= nxt[0] < cols and 0 <= nxt[1] < rows):
                continue
            if nxt in blocked and nxt != goal:
                continue
            # Percorrere un tratto gia' percorso da un'altra tubazione e'
            # **vietato**, non caro: due linee sovrapposte per il lungo sono una
            # linea sola, e un circuito sparisce dalla tavola.
            if (cell, nxt) in taken or (nxt, cell) in taken:
                continue
            added = STEP_COST
            if step != direction:
                added += TURN_COST
            if nxt in occupied:
                # Qui invece si tratta di un **incrocio**: si tocca un nodo e si
                # prosegue trasversalmente. E' una penalita' per cella, non un
                # divieto, perche' l'incrocio deve restare piu' economico del
                # giro per evitarlo (D-041).
                added += CROSS_COST
            if nxt in crowded:
                # Costeggiare un simbolo o un'altra tubazione a un passo di
                # distanza si legge come toccarli. Costa poco, ma basta a far
                # scegliere la corsia libera quando c'e'.
                added += HUG_COST
            candidate = (cost + added, bias + lean(nxt))
            state = (nxt, step)
            if candidate < best.get(state, (candidate[0] + 1, 0)):
                best[state] = candidate
                came[state] = (cell, direction)
                heapq.heappush(
                    open_heap,
                    (
                        candidate[0] + heuristic(nxt, step),
                        candidate[1],
                        candidate[0],
                        nxt,
                        step,
                    ),
                )

    raise LayoutError(
        f"no route from {start} to {goal}: every orthogonal path is blocked"
    )



def _obstacle_cells(placed: list[PlacedSymbol], grid: GridSpace) -> frozenset[Cell]:
    """I riquadri dei simboli posati, arrotondati verso l'esterno.

    L'area di rispetto non viene aggiunta qui: e' gia' garantita dalla
    spaziatura del posizionamento, e gonfiare gli ostacoli chiuderebbe i
    corridoi che portano alle porte.
    """
    cells: set[Cell] = set()
    step = grid.step_mm
    for item in placed:
        x0 = int((item.origin.x_mm - grid.origin.x_mm) / step)
        y0 = int((item.origin.y_mm - grid.origin.y_mm) / step)
        x1 = int(-(-(item.right_mm - grid.origin.x_mm) // step))
        y1 = int(-(-(item.bottom_mm - grid.origin.y_mm) // step))
        for col in range(x0, x1 + 1):
            for row in range(y0, y1 + 1):
                cells.add((col, row))
    return frozenset(cells)


def _port_anchor(
    placed: PlacedSymbol,
    port_id: str,
    catalog: ComponentRegistry,
    definition_id: str,
    grid: GridSpace,
) -> tuple[Cell, Cell]:
    """Nodo e direzione uscente di una porta, sul simbolo gia' posato e ruotato."""
    manifest = catalog.resolve(definition_id).symbol.manifest.rotated(placed.rotation_deg)
    port = manifest.port(port_id)
    cell = grid.to_cell(
        placed.origin.x_mm + port.x_mm, placed.origin.y_mm + port.y_mm
    )
    return cell, _FACE_DIRECTION[port.face]



def port_aprons(
    project: ProjectModel,
    trunks: list[Trunk],
    placed: list[PlacedSymbol],
    catalog: ComponentRegistry,
    grid: GridSpace,
) -> dict[tuple[str, str], Cell]:
    """La cella davanti a ogni attacco in uso: la sua soglia.

    Un attacco ha **una sola uscita**, quella verso cui guarda: le altre tre
    celle intorno stanno dentro il proprio simbolo. Chi occupa quella cella —
    un'altra tratta, o peggio un accessorio, che e' un ostacolo pieno — mura
    l'attacco, e la sua tratta non si instrada piu' su nessun formato.
    """
    by_component = {item.component_id: item for item in placed}
    definitions = {item.id: item.definition_id for item in project.components}
    aprons: dict[tuple[str, str], Cell] = {}
    for trunk in trunks:
        for ref in (trunk.start, trunk.end):
            symbol = by_component.get(ref.component_id)
            if symbol is None:
                continue
            cell, direction = _port_anchor(
                symbol, ref.port_id, catalog, definitions[ref.component_id], grid
            )
            aprons[(ref.component_id, ref.port_id)] = (
                cell[0] + direction[0],
                cell[1] + direction[1],
            )
    return aprons


def route_sheet(
    project: ProjectModel,
    trunks: list[Trunk],
    placed: list[PlacedSymbol],
    catalog: ComponentRegistry,
    grid: GridSpace,
    on_routed: Callable[[Trunk, RoutedTrunk], list[PlacedSymbol]] | None = None,
) -> list[RoutedTrunk]:
    """Instrada le tratte una dopo l'altra, accumulando le celle occupate.

    L'ordine e' quello delle tratte, quindi deterministico. Una tratta che non
    converge fa fallire l'intero foglio con una diagnostica che la nomina: la
    specifica §10.2 vuole una partizione diversa o un errore, non un disegno
    approssimato.

    `on_routed` viene chiamato appena una tratta e' instradata e restituisce i
    simboli che vi sono stati posati sopra. Quei simboli diventano **ostacoli
    per le tratte successive**: posarli tutti alla fine li rendeva invisibili
    all'instradamento, che ci passava attraverso.
    """
    by_component = {item.component_id: item for item in placed}
    definitions = {item.id: item.definition_id for item in project.components}
    media = {item.id: item.medium for item in project.networks}
    blocked = _obstacle_cells(placed, grid)
    # Niente tubazioni sotto la linea di terra: sotto c'e' il pavimento, e la
    # fascia dei richiami. Una rotta che ci finiva sembrava interrata.
    ground_row = grid.to_cell(grid.origin.x_mm, levels_of(
        grid.origin.y_mm, grid.origin.height_mm, grid.step_mm
    ).ground_mm)[1]
    blocked = blocked | frozenset(
        (col, row)
        for col in range(grid.cols + 1)
        for row in range(ground_row + 1, grid.rows + 1)
    )
    occupied: set[Cell] = set()
    # I **tratti** gia' percorsi, non i nodi: ripercorrerne uno e' sovrapporsi
    # per il lungo, ed e' vietato. L'unica eccezione e' l'ultimo tratto contro
    # una porta condivisa da due tratte — due ritorni di zona su un solo attacco
    # del volano — che sulla tavola e' una derivazione, non due linee.
    taken: dict[tuple[Cell, Cell], set[Cell]] = {}
    routed: list[RoutedTrunk] = []
    # L'insieme dei nodi affollati si mantiene **incrementalmente**: e' identico
    # a `_crowded(blocked | occupied)`, ma ricalcolarlo da zero a ogni tratta
    # dominava il costo dell'intero instradamento — e da quando la disposizione
    # si rivede reinstradando (D-078), l'instradamento si paga molte volte.
    cols, rows = grid.cols, grid.rows
    union: set[Cell] = set()
    crowded: set[Cell] = set()

    def absorb(cells: frozenset[Cell] | tuple[Cell, ...]) -> None:
        """Registra nuove celle occupate e aggiorna i loro dintorni."""
        for cell in cells:
            union.add(cell)
            crowded.discard(cell)
        for col, row in cells:
            for step in DIRECTIONS:
                neighbour = (col + step[0], row + step[1])
                if (
                    0 <= neighbour[0] <= cols
                    and 0 <= neighbour[1] <= rows
                    and neighbour not in union
                ):
                    crowded.add(neighbour)

    absorb(blocked)
    # Mandata o ritorno lo dice il modello, che e' orientato, e non la geometria:
    # un componente che finisce a sinistra del proprio alimentatore non per
    # questo lo alimenta di ritorno (D-059).
    orientation = orient_trunks(project, catalog, trunks)

    def anchor(ref: PortRef) -> tuple[Cell, Cell]:
        symbol = by_component.get(ref.component_id)
        if symbol is None:
            raise LayoutError(
                f"connection endpoint {ref.component_id}.{ref.port_id} has no placed "
                f"symbol on this sheet: an inline accessory cannot be a run endpoint"
            )
        return _port_anchor(
            symbol, ref.port_id, catalog, definitions[ref.component_id], grid
        )

    # La cella davanti a ogni attacco in uso e' **riservata al suo attacco**.
    #
    # Un attacco ha una sola uscita, quella verso cui guarda: le altre tre
    # celle intorno stanno dentro il proprio simbolo. Se un'altra tratta ci
    # passa sopra — o peggio, se ci si siede un accessorio, che e' un ostacolo
    # pieno — quell'attacco resta murato e la sua tratta non si instrada piu',
    # su nessun formato. E' successo sul collettore del pavimento radiante: la
    # valvola della prima zona si e' seduta esattamente sotto l'attacco della
    # seconda, a sei celle di distanza, e la seconda zona e' diventata
    # irraggiungibile su A3, su A2 e su A1.
    #
    # Riservare una cella per attacco costa pochissimo e toglie una specie
    # intera di fallimento.
    aprons = port_aprons(project, trunks, placed, catalog, grid)
    reserved = frozenset(aprons.values())

    for trunk in trunks:
        start, start_direction = anchor(trunk.start)
        goal, goal_direction = anchor(trunk.end)

        # Il ripiego geometrico vale solo quando la topologia non decide: e' il
        # caso di un anello in cui nessun utilizzatore separa andata e ritorno.
        declared = orientation.get(trunk.connection_ids)
        supply = declared if declared is not None else goal[0] >= start[0]
        ends = {start, goal}
        # Le proprie soglie servono a questa tratta, e le altre le deve lasciare
        # stare: e' l'unico modo perche' la riserva protegga senza impedire.
        own = {
            aprons[(ref.component_id, ref.port_id)]
            for ref in (trunk.start, trunk.end)
            if (ref.component_id, ref.port_id) in aprons
        }
        try:
            found = route(
                start,
                start_direction,
                goal,
                goal_direction,
                cols=grid.cols,
                rows=grid.rows,
                blocked=(blocked | reserved) - ends - own,
                occupied=frozenset(occupied),
                # Vietati tutti i tratti gia' percorsi, tranne quelli che
                # toccano un attacco condiviso con questa tratta: li' due linee
                # sono una derivazione, e sono lunghi un passo.
                taken=frozenset(
                    edge
                    for edge, anchors in taken.items()
                    if not (anchors & ends & set(edge))
                ),
                crowded=frozenset(crowded - ends),
                # Mandata sopra, ritorno sotto: a parita' di costo, e senza
                # comprare nemmeno una piega per ottenerlo.
                prefer_high=supply,
            )
        except LayoutError as exc:
            raise LayoutError(
                f"run {trunk.connection_ids[0]} on network {trunk.network_id} "
                f"cannot be routed: {exc}"
            ) from exc
        occupied.update(found.cells)
        absorb(found.cells)
        for before, after in zip(found.cells, found.cells[1:], strict=False):
            taken.setdefault((before, after), set()).update(ends)
        current = RoutedTrunk(
                network_id=trunk.network_id,
                medium=media.get(trunk.network_id, ""),
                supply=supply,
                connection_ids=list(trunk.connection_ids),
                segments=[
                    [
                        Point(x_mm=grid.to_mm(cell)[0], y_mm=grid.to_mm(cell)[1])
                        for cell in found.vertices
                    ]
                ],
                crossings=[
                    Point(x_mm=grid.to_mm(cell)[0], y_mm=grid.to_mm(cell)[1])
                    for cell in found.crossings
                ],
        )
        routed.append(current)
        if on_routed is not None:
            settled = _obstacle_cells(on_routed(trunk, current), grid)
            blocked = blocked | settled
            absorb(settled)
    return routed
