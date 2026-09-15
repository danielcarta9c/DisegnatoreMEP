"""Le coppie addosso nella posa che la fase del tronco consegna (criterio 1).

Misura la posa che `lay_the_spine` + `carry_the_rest` consegnano — non la
tavola finita — e conta due cose, per impianto:

- le coppie di simboli che **si sovrappongono davvero**, riquadro contro
  riquadro;
- le coppie **piu' vicine dello stacco che la posa impone fra figure diverse**,
  che e' la regola con cui `Improver.is_valid` giudica una candidata
  (`ROW_GAP_MM`); dentro la stessa figura basta non sovrapporsi (D-062). Le
  sovrapposte sono comprese in questo conto, come nella regola.

Usa solo funzioni pubbliche, cosi' che lo stesso file misuri la base e il ramo.
Per misurare la base, con il codice della base:

    cd <worktree della base>
    PYTHONPATH="$PWD/src" python docs/collaudi/DRAW-010/le-coppie-addosso.py

    python docs/collaudi/DRAW-010/le-coppie-addosso.py
    python docs/collaudi/DRAW-010/le-coppie-addosso.py 2
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from disegnatore_mep.catalog.registry import ComponentRegistry  # noqa: E402
from disegnatore_mep.graphics.frame import NOVE_C_A3  # noqa: E402
from disegnatore_mep.graphics.registry import SymbolRegistry  # noqa: E402
from disegnatore_mep.io.project_json import load_project  # noqa: E402
from disegnatore_mep.layout.compose import inline_component_ids  # noqa: E402
from disegnatore_mep.layout.geometry import PlacedSymbol  # noqa: E402
from disegnatore_mep.layout.partition import partition_project  # noqa: E402
from disegnatore_mep.layout.place import (  # noqa: E402
    ROW_GAP_MM,
    hanging_children,
    place_sheet,
)
from disegnatore_mep.layout.spine import carry_the_rest, lay_the_spine  # noqa: E402
from disegnatore_mep.layout.trunks import build_trunks  # noqa: E402
from disegnatore_mep.model.project import ProjectModel  # noqa: E402
from disegnatore_mep.rules.apply import saturate  # noqa: E402
from disegnatore_mep.rules.registry import RuleRegistry  # noqa: E402

CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"
PROVA = ROOT / "examples" / "prova"

TOLERANCE_MM = 1e-6

IMPIANTI = {
    1: "prova-1-due-pdc-accumulo-combinato.json",
    2: "prova-2-pdc-deviatrice-acs.json",
    3: "prova-3-pdc-diretta-pavimento.json",
    4: "prova-4-ibrido-pdc-caldaia.json",
    5: "prova-5-cascata-tre-pdc.json",
}


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def completato(name: str) -> ProjectModel:
    registry = catalog()
    rules = RuleRegistry.from_directory(RULES)
    rules.cross_check(registry)
    done, _, _ = saturate(load_project(PROVA / name), registry, rules)
    return done


def _too_close(one: PlacedSymbol, two: PlacedSymbol, gap_mm: float) -> bool:
    return (
        one.origin.x_mm < two.right_mm + gap_mm - TOLERANCE_MM
        and two.origin.x_mm - gap_mm < one.right_mm - TOLERANCE_MM
        and one.origin.y_mm < two.bottom_mm + gap_mm - TOLERANCE_MM
        and two.origin.y_mm - gap_mm < one.bottom_mm - TOLERANCE_MM
    )


def _report(number: int) -> None:
    name = IMPIANTI[number]
    model = completato(name)
    registry = catalog()
    inline = inline_component_ids(model, registry)
    partition = partition_project(model, build_trunks(model, inline))[0]
    first = place_sheet(model, partition, registry, NOVE_C_A3, inline)
    spine = lay_the_spine(model, partition, registry, NOVE_C_A3, first)
    seeded = carry_the_rest(model, partition, registry, first, spine, NOVE_C_A3)

    known = frozenset(item.component_id for item in seeded)
    children = hanging_children(model, partition, registry, known)
    parent = {child: father for father, items in children.items() for child, _ in items}
    leader: dict[str, str] = {}
    for item in known:
        head, seen = item, {item}
        while head in parent and parent[head] not in seen:
            head = parent[head]
            seen.add(head)
        leader[item] = head

    where = {item.component_id: item for item in seeded}
    ids = sorted(where)
    sovrapposte: list[tuple[str, str]] = []
    vicine: list[tuple[str, str]] = []
    for index, one in enumerate(ids):
        for two in ids[index + 1 :]:
            gap = 0.0 if leader[one] == leader[two] else ROW_GAP_MM
            if _too_close(where[one], where[two], 0.0):
                sovrapposte.append((one, two))
            if _too_close(where[one], where[two], gap):
                vicine.append((one, two))
    print(f"== impianto {number} — {name}")
    print(f"   la fase del tronco ha consegnato una posa: {bool(spine.symbols)}")
    print(f"   coppie che si sovrappongono davvero     : {len(sovrapposte)}")
    for one, two in sovrapposte:
        print(f"       {one} <-> {two}")
    print(f"   coppie piu' vicine dello stacco ammesso : {len(vicine)}")
    for one, two in vicine:
        print(f"       {one} <-> {two}")
    print()


def main(argv: list[str]) -> int:
    wanted = [int(item) for item in argv] or sorted(IMPIANTI)
    for number in wanted:
        _report(number)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
