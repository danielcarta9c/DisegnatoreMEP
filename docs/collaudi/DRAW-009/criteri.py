"""Le misure di DRAW-009 che `metriche.py` non dava, lette su una geometria.

`docs/collaudi/DRAW-008/metriche.py` resta lo strumento delle misure generali —
pieghe, incroci, lunghezza, gerarchia, catene, organi. Qui stanno le tre che
questo pacchetto ha aggiunto, e che servono a chiudere i criteri 3, 4 e 10:

- **i confini di rete**: per ciascuno, le pieghe della propria tratta e quante
  tratte di livello autostrada attraversa (criterio 3);
- **i nodi condivisi fra un'autostrada e un rango inferiore**, con la
  **ripartizione per rete** — che e' la misura del §A del pacchetto e il modo di
  vedere quanta parte ne portava l'acqua fredda (criterio 4);
- **le tratte di tronco che non possono essere rettilinee**, con le pieghe di
  ciascuna: una sola, o il criterio 10 non e' chiuso.

    python docs/collaudi/DRAW-009/criteri.py <modello-completo.json> <geometria.json>
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from disegnatore_mep.catalog.registry import ComponentRegistry  # noqa: E402
from disegnatore_mep.graphics.frame import NOVE_C_A3  # noqa: E402
from disegnatore_mep.graphics.registry import SymbolRegistry  # noqa: E402
from disegnatore_mep.io.project_json import load_project  # noqa: E402
from disegnatore_mep.layout.compose import inline_component_ids  # noqa: E402
from disegnatore_mep.layout.hierarchy import Level, hierarchy_of  # noqa: E402
from disegnatore_mep.layout.partition import partition_project  # noqa: E402
from disegnatore_mep.layout.place import place_sheet  # noqa: E402
from disegnatore_mep.layout.spine import lay_the_spine  # noqa: E402
from disegnatore_mep.layout.trunks import build_trunks  # noqa: E402

CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
STEP_MM = 2.5
BOUNDARY = "boundary"


def _nodes(route: dict[str, object]) -> set[tuple[float, float]]:
    touched: set[tuple[float, float]] = set()
    for segment in route["segments"]:  # type: ignore[index]
        for before, after in zip(segment, segment[1:], strict=False):
            steps = int(
                round(
                    (
                        abs(after["x_mm"] - before["x_mm"])
                        + abs(after["y_mm"] - before["y_mm"])
                    )
                    / STEP_MM
                )
            )
            for index in range(steps + 1):
                ratio = 0.0 if steps == 0 else index / steps
                touched.add(
                    (
                        round(before["x_mm"] + (after["x_mm"] - before["x_mm"]) * ratio, 3),
                        round(before["y_mm"] + (after["y_mm"] - before["y_mm"]) * ratio, 3),
                    )
                )
    return touched


def _bends(route: dict[str, object]) -> int:
    return sum(max(len(segment) - 2, 0) for segment in route["segments"])  # type: ignore[index]


def main(model_path: Path, geometry_path: Path) -> int:
    project = load_project(model_path)
    catalog = ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
    sheet = json.loads(geometry_path.read_text(encoding="utf-8"))["sheets"][0]
    routes = {tuple(item["connection_ids"]): item for item in sheet["routes"]}

    inline = inline_component_ids(project, catalog)
    partition = partition_project(project, build_trunks(project, inline))[0]
    trunks = list(partition.trunks)
    levels = hierarchy_of(project, catalog, trunks)
    first = place_sheet(project, partition, catalog, NOVE_C_A3, inline)
    spine = lay_the_spine(project, partition, catalog, NOVE_C_A3, first)
    names = {
        trunk.connection_ids: (
            f"{trunk.start.component_id}.{trunk.start.port_id}"
            f" -> {trunk.end.component_id}.{trunk.end.port_id}"
        )
        for trunk in trunks
    }
    network_of = {item.id: item for item in project.networks}

    inlets = {
        item.id
        for item in project.components
        if BOUNDARY in catalog.get(item.definition_id).functions
    }

    print("== confini di rete (criterio 3) ==")
    autostrade_nodes: set[tuple[float, float]] = set()
    for trunk in trunks:
        route = routes.get(tuple(trunk.connection_ids))
        if route is not None and levels[trunk.connection_ids] is Level.AUTOSTRADA:
            autostrade_nodes |= _nodes(route)
    for trunk in trunks:
        ends = {trunk.start.component_id, trunk.end.component_id}
        if not ends & inlets:
            continue
        route = routes.get(tuple(trunk.connection_ids))
        if route is None:
            print(f"   {names[trunk.connection_ids]}: nessuna tratta disegnata")
            continue
        crossing = _nodes(route) & autostrade_nodes
        print(
            f"   {names[trunk.connection_ids]:58s} pieghe={_bends(route)} "
            f"nodi_su_autostrada={len(crossing)}"
        )
    print()

    print("== nodi condivisi fra un'autostrada e un rango inferiore (criterio 4) ==")
    passaggi: dict[tuple[float, float], set[str]] = defaultdict(set)
    reti: dict[tuple[float, float], set[str]] = defaultdict(set)
    for trunk in trunks:
        route = routes.get(tuple(trunk.connection_ids))
        if route is None:
            continue
        rank = levels[trunk.connection_ids].name
        for node in _nodes(route):
            passaggi[node].add(rank)
            reti[node].add(str(route["network_id"]))
    condivisi = [
        node
        for node, ranks in passaggi.items()
        if "AUTOSTRADA" in ranks and len(ranks) > 1
    ]
    per_rete: dict[str, int] = defaultdict(int)
    for node in condivisi:
        for network_id in reti[node] - {"primario"}:
            per_rete[network_id] += 1
        if reti[node] <= {"primario"}:
            per_rete["primario"] += 1
    print(f"   totale: {len(condivisi)}")
    for network_id, count in sorted(per_rete.items()):
        medium = network_of[network_id].medium if network_id in network_of else "?"
        print(f"     rete {network_id} ({medium}): {count}")
    print()

    print("== tratte di tronco che non possono essere rettilinee (criterio 10) ==")
    impossibili = set(spine.impossible)
    for trunk in trunks:
        if trunk.connection_ids not in impossibili:
            continue
        route = routes.get(tuple(trunk.connection_ids))
        pieghe = "-" if route is None else _bends(route)
        print(f"   {names[trunk.connection_ids]:58s} pieghe={pieghe}")
    storte = [
        (names[trunk.connection_ids], _bends(routes[tuple(trunk.connection_ids)]))
        for trunk in trunks
        if levels[trunk.connection_ids] is Level.AUTOSTRADA
        and tuple(trunk.connection_ids) in routes
        and _bends(routes[tuple(trunk.connection_ids)])
    ]
    print(f"   autostrade con almeno una piega: {len(storte)}")
    for name, bends in storte:
        print(f"     {name:58s} pieghe={bends}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), Path(sys.argv[2])))
