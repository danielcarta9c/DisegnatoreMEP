"""Instradamento ortogonale: l'incrocio costa poco, il giro lungo carissimo.

D-041 lo dice in una riga: «l'incrocio e' economico e il percorso lungo e'
carissimo». Un instradatore che tratti l'incrocio come vietato invece che come
costoso produce esattamente il difetto che quella decisione esiste per evitare:
una tubazione che gira intorno a mezzo disegno per non attraversarne un'altra.

La funzione di costo lo impone per costruzione: un incrocio costa meno del giro
minimo per evitarlo, che vale due passi. La disuguaglianza e' sotto test.
"""

import heapq
from collections.abc import Callable
from dataclasses import dataclass

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.symbol import PortFace
from disegnatore_mep.model.project import PortRef, ProjectModel

from .composition import AUXILIARY_FUNCTIONS, levels_of
from .errors import LayoutError
from .geometry import PlacedSymbol, Point, RoutedTrunk
from .grid import Cell, GridSpace
from .trunks import Trunk

STEP_COST = 10
"""Costo di un passo di griglia. La lunghezza e' la voce dominante."""

TURN_COST = 15
"""Costo di una piega: una tubazione che serpeggia si legge male."""

CROSS_COST = 5
"""Costo di una cella gia' percorsa da un'altra rete.

Attraversare ne tocca una sola, quindi costa meno del giro minimo per evitarla,
che vale due passi: l'instradatore non deviera' mai per schivare un incrocio
(D-041). Costeggiare la paga invece a ogni cella, e supera presto il costo di
una corsia libera accanto.
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
    max_expansions: int = MAX_EXPANSIONS,
) -> Route:
    """A* su stato `(cella, direzione di arrivo)`.

    La direzione entra nello stato perche' il costo di piega dipende da come ci
    si e' arrivati. L'euristica di Manhattan e' ammissibile: piega e incrocio
    possono solo aggiungere.

    `start_direction` e `goal_direction` sono le direzioni **uscenti** delle due
    porte, cioe' dove la porta guarda. Vanno derivate da `PortFace`, non passate
    a mano: al contrario l'instradatore non fallisce, costruisce un cappio che
    rientra dal lato sbagliato.
    """
    approach = (-goal_direction[0], -goal_direction[1])

    def heuristic(cell: Cell) -> int:
        return (abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])) * STEP_COST

    open_heap: list[tuple[int, int, Cell, Cell]] = [
        (heuristic(start), 0, start, start_direction)
    ]
    best: dict[tuple[Cell, Cell], int] = {(start, start_direction): 0}
    came: dict[tuple[Cell, Cell], tuple[Cell, Cell]] = {}
    expansions = 0

    while open_heap:
        _, cost, cell, direction = heapq.heappop(open_heap)
        if cost > best.get((cell, direction), cost):
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
            added = STEP_COST
            if step != direction:
                added += TURN_COST
            if nxt in occupied:
                # Penalita' per cella, non divieto. Attraversare costa un solo
                # CROSS_COST, meno del giro minimo; costeggiare lo paga a ogni
                # passo e diventa presto piu' caro di una corsia libera accanto.
                # Un divieto secco invece chiudeva il passaggio dove due corsie
                # corrono adiacenti, e la rotta non trovava piu' alcuna strada.
                added += CROSS_COST
            candidate = cost + added
            state = (nxt, step)
            if candidate < best.get(state, candidate + 1):
                best[state] = candidate
                came[state] = (cell, direction)
                heapq.heappush(open_heap, (candidate + heuristic(nxt), candidate, nxt, step))

    raise LayoutError(
        f"no route from {start} to {goal}: every orthogonal path is blocked"
    )


def _clear(path: list[Cell], blocked: frozenset[Cell], ends: tuple[Cell, Cell]) -> bool:
    return all(cell not in blocked or cell in ends for cell in path)


def _walk(a: Cell, b: Cell) -> list[Cell]:
    """Le celle da a a b, che devono stare sulla stessa riga o colonna."""
    if a[0] == b[0]:
        step = 1 if b[1] > a[1] else -1
        return [(a[0], y) for y in range(a[1], b[1] + step, step)]
    step = 1 if b[0] > a[0] else -1
    return [(x, a[1]) for x in range(a[0], b[0] + step, step)]


def _rail_path(
    start: Cell, start_direction: Cell, goal: Cell, goal_direction: Cell, rail_row: int
) -> list[Cell] | None:
    """Il percorso canonico di uno schema: esci, corri sulla corsia, entra.

    E' come e' disegnata una tavola vera: le tubazioni non serpeggiano fra i
    componenti, corrono su poche quote orizzontali e scendono dove serve. Un
    A* libero trova percorsi piu' corti e piu' brutti, pieni di gomiti, e
    lascia rettilinei troppo brevi per posarci sopra un accessorio.
    """
    if start_direction[1] != 0 or goal_direction[1] != 0:
        return None  # per ora solo porte laterali: le altre restano all'A*
    out_x = start[0] + start_direction[0]
    in_x = goal[0] + goal_direction[0]
    corners = [
        start,
        (out_x, start[1]),
        (out_x, rail_row),
        (in_x, rail_row),
        (in_x, goal[1]),
        goal,
    ]
    path: list[Cell] = [start]
    for before, after in zip(corners, corners[1:], strict=False):
        if before == after:
            continue
        if before[0] != after[0] and before[1] != after[1]:
            return None
        path.extend(_walk(before, after)[1:])
    return path


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
    routed: list[RoutedTrunk] = []
    # Le quote delle corsie, dall'alto: le prime sono preferite.
    levels = levels_of(grid.origin.y_mm, grid.origin.height_mm, grid.step_mm)
    supply_rails = [
        grid.to_cell(grid.origin.x_mm, y)[1]
        for y in (levels.upper_supply_mm, levels.lower_supply_mm)
    ]
    return_rails = [
        grid.to_cell(grid.origin.x_mm, y)[1]
        for y in (levels.upper_return_mm, levels.lower_return_mm)
    ]

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

    for trunk in trunks:
        start, start_direction = anchor(trunk.start)
        goal, goal_direction = anchor(trunk.end)

        # Prima le corsie: la mandata corre in alto, il ritorno in basso, e il
        # verso si legge dal disegno stesso — chi va verso destra e' mandata,
        # chi torna indietro e' ritorno.
        supply = goal[0] >= start[0]
        rails = supply_rails if supply else return_rails
        # Una tratta che porta ausiliari — filtro, vaso, riempimento — corre
        # bassa: su una tavola vera quei pezzi stanno vicino a terra, non a
        # mezz'aria fra i componenti.
        if any(
            frozenset(catalog.resolve(definitions[item]).definition.functions)
            & AUXILIARY_FUNCTIONS
            for item in trunk.inline_component_ids
        ):
            rails = list(reversed(rails))
        found_rail = None
        for rail_row in rails:
            candidate = _rail_path(start, start_direction, goal, goal_direction, rail_row)
            if candidate is None:
                continue
            if _clear(candidate, blocked, (start, goal)) and not any(
                cell in occupied for cell in candidate[1:-1]
            ):
                found_rail = candidate
                break
        if found_rail is not None:
            found = Route(cells=tuple(found_rail), cost=0, crossings=())
            occupied.update(found.cells)
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
                crossings=[],
            )
            routed.append(current)
            if on_routed is not None:
                blocked = blocked | _obstacle_cells(on_routed(trunk, current), grid)
            continue

        try:
            found = route(
                start,
                start_direction,
                goal,
                goal_direction,
                cols=grid.cols,
                rows=grid.rows,
                blocked=blocked - {start, goal},
                occupied=frozenset(occupied),
            )
        except LayoutError as exc:
            raise LayoutError(
                f"run {trunk.connection_ids[0]} on network {trunk.network_id} "
                f"cannot be routed: {exc}"
            ) from exc
        occupied.update(found.cells)
        current = RoutedTrunk(
                network_id=trunk.network_id,
                medium=media.get(trunk.network_id, ""),
                supply=goal[0] >= start[0],
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
            blocked = blocked | _obstacle_cells(on_routed(trunk, current), grid)
    return routed
