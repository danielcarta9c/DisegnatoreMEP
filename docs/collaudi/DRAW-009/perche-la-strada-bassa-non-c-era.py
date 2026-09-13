"""Perche' `deviatrice.out_b -> bollitore.coil_in` girava attorno al ritorno.

E' la misura del **criterio 9** di DRAW-009, e la prima cosa che il pacchetto
chiede: «il rapporto dice **perche'** oggi la strada bassa non e' disponibile —
con la misura, non con un'ipotesi».

Lo strumento non ricompone la tavola: legge una geometria **agli atti** e
ricostruisce, su quella, lo stato con cui l'instradatore ha lavorato — celle
murate dai simboli, soglie degli attacchi, corsie riservate alle catene di
macchina — poi chiama l'instradatore vero, con i suoi pesi veri, e misura.
Cosi' la misura resta valida anche dopo che il codice e' cambiato: descrive la
tavola che sta nel file, non quella che uscirebbe oggi.

    python docs/collaudi/DRAW-009/perche-la-strada-bassa-non-c-era.py \\
        docs/collaudi/DRAW-008/dopo/impianto2-completo.json \\
        docs/collaudi/DRAW-008/dopo/geometria.json

Quattro misure, in quest'ordine:

1. **la strada a una piega esiste come forma**: la porta di partenza guarda in
   basso, quella di arrivo guarda a sinistra, quindi scendere e poi andare a
   destra e' l'unica spezzata con una piega sola. Se ne stampano le celle;
2. **quante di quelle celle sono murate, e da chi**: simbolo per simbolo, soglia
   per soglia;
3. **i pesi non c'entrano**: la stessa tratta, sullo stesso stato, con
   `TURN_COST` a 100, 800 e 2000. Se la spezzata non cambia, il numero di pieghe
   e' il minimo disponibile, non una scelta;
4. **la strada bassa con la corsia sgombra**: si tolgono dagli ostacoli le sole
   celle che la murano e si reinstrada. Se compare la spezzata a una piega, e
   costa meno di quella consegnata, allora la strada bassa **non era cara: non
   c'era**.
"""

import json
import sys
from math import ceil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

import disegnatore_mep.layout.route as router  # noqa: E402
from disegnatore_mep.catalog.registry import ComponentRegistry  # noqa: E402
from disegnatore_mep.graphics.frame import NOVE_C_A3  # noqa: E402
from disegnatore_mep.graphics.registry import SymbolRegistry  # noqa: E402
from disegnatore_mep.io.project_json import load_project  # noqa: E402
from disegnatore_mep.layout.chains import chain_room_mm, machine_chains  # noqa: E402
from disegnatore_mep.layout.compose import inline_component_ids  # noqa: E402
from disegnatore_mep.layout.geometry import PlacedSymbol  # noqa: E402
from disegnatore_mep.layout.grid import GridSpace  # noqa: E402
from disegnatore_mep.layout.partition import partition_project  # noqa: E402
from disegnatore_mep.layout.route import (  # noqa: E402
    CROSS_COST,
    TURN_COST,
    Cell,
    _obstacle_cells,
    _port_anchor,
    port_aprons,
    route,
)
from disegnatore_mep.layout.trunks import build_trunks  # noqa: E402

CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
TRATTA = ("deviatrice", "out_b", "bollitore", "coil_in")


def _pieghe(cells: tuple[Cell, ...]) -> int:
    """Le pieghe di una spezzata, senza contare le celle ripetute."""
    clean: list[Cell] = []
    for cell in cells:
        if not clean or cell != clean[-1]:
            clean.append(cell)
    return sum(
        1
        for index in range(1, len(clean) - 1)
        if (
            clean[index][0] - clean[index - 1][0],
            clean[index][1] - clean[index - 1][1],
        )
        != (
            clean[index + 1][0] - clean[index][0],
            clean[index + 1][1] - clean[index][1],
        )
    )


def main(model_path: Path, geometry_path: Path) -> int:
    project = load_project(model_path)
    catalog = ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
    sheet = json.loads(geometry_path.read_text(encoding="utf-8"))["sheets"][0]
    placed = [PlacedSymbol.model_validate(item) for item in sheet["symbols"]]
    by_component = {item.component_id: item for item in placed}
    definitions = {item.id: item.definition_id for item in project.components}
    grid = GridSpace(origin=NOVE_C_A3.drawing_rect_mm, standard=NOVE_C_A3.standard)
    step, origin = grid.step_mm, grid.origin

    inline = inline_component_ids(project, catalog)
    trunks = list(partition_project(project, build_trunks(project, inline))[0].trunks)
    # Gli accessori posati **sulle** tratte non entrano negli ostacoli: al
    # momento in cui questa tratta si instrada la maggior parte non c'e'
    # ancora. Chi mura la corsia bassa non e' uno di loro, e lo si vede.
    grossi = [item for item in placed if item.component_id not in inline]

    blocked = set(_obstacle_cells(grossi, grid))
    aprons = port_aprons(project, trunks, grossi, catalog, grid)
    corridors: dict[tuple[str, str], frozenset[Cell]] = {}
    for trunk in trunks:
        head, tail = machine_chains(project, catalog, trunk)
        for ref, chain in ((trunk.start, head), (trunk.end, tail)):
            if not chain or ref.component_id not in by_component:
                continue
            cell, direction = _port_anchor(
                by_component[ref.component_id],
                ref.port_id,
                catalog,
                definitions[ref.component_id],
                grid,
            )
            room = ceil(
                chain_room_mm(project, catalog, chain, direction[1] == 0) / step - 1e-9
            )
            corridors[ref.component_id, ref.port_id] = frozenset(
                (cell[0] + direction[0] * count, cell[1] + direction[1] * count)
                for count in range(1, room + 1)
            )

    start_id, start_port, goal_id, goal_port = TRATTA
    start, start_direction = _port_anchor(
        by_component[start_id], start_port, catalog, definitions[start_id], grid
    )
    goal, goal_direction = _port_anchor(
        by_component[goal_id], goal_port, catalog, definitions[goal_id], grid
    )
    mine = {(start_id, start_port), (goal_id, goal_port)}
    own = {aprons[key] for key in mine if key in aprons}
    elsewhere = {
        cell for key, cells in corridors.items() if key not in mine for cell in cells
    }
    reserved = set(aprons.values())
    field = (blocked | reserved | elsewhere) - {start, goal} - own

    trunk = next(
        item
        for item in trunks
        if (item.start.component_id, item.start.port_id) == (start_id, start_port)
    )
    head, tail = machine_chains(project, catalog, trunk)
    start_straight = ceil(
        chain_room_mm(project, catalog, head, start_direction[1] == 0) / step - 1e-9
    )
    goal_straight = ceil(
        chain_room_mm(project, catalog, tail, goal_direction[1] == 0) / step - 1e-9
    )

    consegnata = next(
        item
        for item in sheet["routes"]
        if item["connection_ids"][0].startswith(f"{trunk.connection_ids[0]}")
    )
    disegnata = [
        (point["x_mm"], point["y_mm"])
        for segment in consegnata["segments"]
        for point in segment
    ]

    def mm(cell: Cell) -> str:
        return f"({origin.x_mm + cell[0] * step:g}·{origin.y_mm + cell[1] * step:g})"

    print(f"tratta  {start_id}.{start_port} -> {goal_id}.{goal_port}")
    print(f"  partenza {mm(start)} guarda {start_direction}")
    print(f"  arrivo   {mm(goal)} guarda {goal_direction}")
    print(
        "  spezzata consegnata: "
        + " -> ".join(f"({x:g}·{y:g})" for x, y in dict.fromkeys(disegnata))
    )
    print()

    print("1. la strada a una piega, cella per cella")
    lane = [(start[0], y) for y in range(start[1], goal[1] + 1)]
    lane += [(x, goal[1]) for x in range(start[0] + 1, goal[0] + 1)]
    print(f"   {len(lane)} celle, da {mm(start)} a {mm(goal)}, con una piega sola")
    print()

    print("2. quante di quelle celle sono murate, e da chi")
    owner: dict[Cell, list[str]] = {}
    for item in grossi:
        for cell in _obstacle_cells([item], grid):
            owner.setdefault(cell, []).append(f"simbolo {item.component_id}")
    for key, cell in aprons.items():
        owner.setdefault(cell, []).append(f"soglia dell'attacco {key[0]}.{key[1]}")
    for key, cells in corridors.items():
        for cell in cells:
            owner.setdefault(cell, []).append(f"corsia della catena {key[0]}.{key[1]}")
    walls = [cell for cell in lane if cell in field]
    print(f"   murate: {len(walls)} su {len(lane)}")
    for cell in walls:
        print(f"     {mm(cell)}  <-  " + " | ".join(sorted(set(owner.get(cell, ())))))
    print()

    print("3. i pesi non c'entrano: la stessa tratta con pesi diversi")
    for turn in (TURN_COST, 800, 2000):
        router.TURN_COST = turn
        found = route(
            start,
            start_direction,
            goal,
            goal_direction,
            cols=grid.cols,
            rows=grid.rows,
            blocked=frozenset(field),
            occupied=frozenset(),
            start_straight=start_straight,
            goal_straight=goal_straight,
            prefer_high=True,
        )
        print(
            f"   TURN_COST={turn:5d} CROSS_COST={CROSS_COST}  "
            f"pieghe={_pieghe(found.cells)}  costo={found.cost}  "
            + " -> ".join(mm(cell) for cell in dict.fromkeys(found.vertices))
        )
    router.TURN_COST = TURN_COST
    print()

    print("4. la stessa tratta con la corsia bassa sgombra")
    sgombra = frozenset(field) - set(lane)
    found = route(
        start,
        start_direction,
        goal,
        goal_direction,
        cols=grid.cols,
        rows=grid.rows,
        blocked=sgombra,
        occupied=frozenset(),
        start_straight=start_straight,
        goal_straight=goal_straight,
        prefer_high=True,
    )
    print(
        f"   pieghe={_pieghe(found.cells)}  costo={found.cost}  "
        + " -> ".join(mm(cell) for cell in dict.fromkeys(found.vertices))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
