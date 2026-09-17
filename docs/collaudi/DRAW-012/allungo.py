"""Lo stretch usato davvero: dove il corredo non entrava e il tronco si e' allungato.

Criterio 8 di `DRAW-012`. Non fa parte del nucleo deterministico: legge il
**diario** del ciclo di miglioramento — che registra ogni candidata provata, la
sua specie e se e' stata accettata — e ne estrae le sole mosse di specie
`allungo`, con le posizioni prima e dopo dei pezzi che hanno mosso.

Uso:
    .venv/bin/python docs/collaudi/DRAW-012/allungo.py MODELLO-completo.json
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from disegnatore_mep.catalog.registry import ComponentRegistry  # noqa: E402
from disegnatore_mep.graphics.registry import SymbolRegistry  # noqa: E402
from disegnatore_mep.io.project_json import load_project  # noqa: E402
from disegnatore_mep.layout.chains import machine_chains  # noqa: E402
from disegnatore_mep.layout.compose import (  # noqa: E402
    compose_on_ordinary_frame,
    inline_component_ids,
)
from disegnatore_mep.layout.errors import LayoutError  # noqa: E402
from disegnatore_mep.layout.hierarchy import hierarchy_of  # noqa: E402
from disegnatore_mep.layout.improve import Improver  # noqa: E402
from disegnatore_mep.layout.partition import partition_project  # noqa: E402
from disegnatore_mep.layout.place import place_sheet  # noqa: E402
from disegnatore_mep.layout.spine import carry_the_rest, lay_the_spine  # noqa: E402
from disegnatore_mep.layout.trunks import build_trunks  # noqa: E402
from disegnatore_mep.model.order import structural_order  # noqa: E402


def main() -> None:
    symbols = SymbolRegistry.from_directory(ROOT / "assets" / "symbols")
    catalog = ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog", symbols=symbols
    )
    project = load_project(Path(sys.argv[1]))
    inline = inline_component_ids(project, catalog)
    runs = build_trunks(project, inline)
    levels = hierarchy_of(project, catalog, runs)
    rank = structural_order(project)

    def in_line(trunk: object) -> tuple[int, int, tuple[int, str], tuple[int, str]]:
        ends = sorted(
            (rank.get(ref.component_id, 0), ref.port_id)
            for ref in (trunk.start, trunk.end)  # type: ignore[attr-defined]
        )
        head, tail = machine_chains(project, catalog, trunk)  # type: ignore[arg-type]
        return (
            0 if head or tail else 1,
            -int(levels[trunk.connection_ids]),  # type: ignore[attr-defined]
            ends[0],
            ends[1],
        )

    ordered = sorted(runs, key=in_line)  # type: ignore[arg-type]
    # Il formato e' quello su cui la tavola **esce davvero**, non il primo su
    # cui la sola posa iniziale riesce: la catena completa e' l'unica che sa
    # dirlo, e il diario dell'allungo deve descrivere la tavola consegnata.
    chosen, _ = compose_on_ordinary_frame(project, catalog)
    for frame in (chosen,):
        for partition in partition_project(project, ordered):
            try:
                first = place_sheet(project, partition, catalog, frame, inline)
            except LayoutError:
                break
            spine = lay_the_spine(project, partition, catalog, frame, first)
            seeded = carry_the_rest(project, partition, catalog, first, spine, frame)
            improver = Improver(
                project, partition, catalog, frame, seeded, inline, spine
            )
            before = {item.component_id: item for item in seeded}
            improver.run()
            stretched = [
                item for item in improver.journal if item.kind == "allungo"
            ]
            taken = [item for item in stretched if item.accepted]
            print(
                f"{partition.sheet_id} su "
                f"{frame.standard.sheet_width_mm:g}x{frame.standard.sheet_height_mm:g}: "
                f"{len(stretched)} allunghi provati, {len(taken)} accettati"
            )
            for item in taken:
                print(f"  accettato in fase «{item.phase}» su {item.leader}")
            if taken:
                for name, was in before.items():
                    now = improver.best[name]
                    if now.origin != was.origin:
                        print(
                            f"    {name}: ({was.origin.x_mm:g}, {was.origin.y_mm:g})"
                            f" -> ({now.origin.x_mm:g}, {now.origin.y_mm:g})"
                        )
        else:
            return


if __name__ == "__main__":
    main()
