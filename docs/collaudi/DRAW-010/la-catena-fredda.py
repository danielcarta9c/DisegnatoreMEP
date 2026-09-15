"""La fila degli accessori sull'acqua fredda del bollitore (DRAW-010 §D.3).

`let-what-holds-its-own-volume-empty` vuole lo scarico **dal lato del serbatoio
rispetto all'organo che lo chiude**. Il gruppo di sicurezza sanitario e' un
composito e porta a bordo l'intercettazione e il ritegno
(`carries_on_board: [isolation, non_return]`): e' lui l'organo che chiude, e lo
scarico gli deve stare dalla parte del bollitore.

Lo strumento stampa, per ogni impianto, le tratte dell'acqua fredda con la fila
dei loro pezzi nel verso in cui l'acqua le attraversa, e dice se lo scarico sta
dal lato giusto.

    python docs/collaudi/DRAW-010/la-catena-fredda.py
    python docs/collaudi/DRAW-010/la-catena-fredda.py 2
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from disegnatore_mep.assembly.runs import runs_of  # noqa: E402
from disegnatore_mep.catalog.registry import ComponentRegistry  # noqa: E402
from disegnatore_mep.graphics.registry import SymbolRegistry  # noqa: E402
from disegnatore_mep.io.project_json import load_project  # noqa: E402
from disegnatore_mep.model.project import ProjectModel  # noqa: E402
from disegnatore_mep.rules.apply import saturate  # noqa: E402
from disegnatore_mep.rules.registry import RuleRegistry  # noqa: E402

CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"
PROVA = ROOT / "examples" / "prova"

IMPIANTI = {
    1: "prova-1-due-pdc-accumulo-combinato.json",
    2: "prova-2-pdc-deviatrice-acs.json",
    3: "prova-3-pdc-diretta-pavimento.json",
    4: "prova-4-ibrido-pdc-caldaia.json",
    5: "prova-5-cascata-tre-pdc.json",
}

DRAIN = "drain"
CLOSING = frozenset({"isolation", "isolation_locked_open"})


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


def _report(number: int) -> None:
    name = IMPIANTI[number]
    print(f"== impianto {number} — {name}")
    model = completato(name)
    registry = catalog()
    rules = {item.id: item for item in RuleRegistry.from_directory(RULES).all()}
    mediums = {
        item.id: item.medium for item in model.networks
    }
    for run in runs_of(model, registry, rules):
        if mediums.get(run.network_id) != "cold_water":
            continue
        print(
            f"   {run.network_id}: {run.head.component_id}.{run.head.port_id}"
            f" -> {run.tail.component_id}.{run.tail.port_id}"
        )
        for piece in run.pieces:
            does = sorted(piece.functions | piece.on_board)
            bordo = sorted(piece.on_board)
            detto = f" (a bordo: {', '.join(bordo)})" if bordo else ""
            print(f"     {piece.component_id}  [{', '.join(does)}]{detto}")
        names = [item.component_id for item in run.pieces]
        drains = [
            index
            for index, item in enumerate(run.pieces)
            if DRAIN in (item.functions | item.on_board)
        ]
        closers = [
            index
            for index, item in enumerate(run.pieces)
            if CLOSING & (item.functions | item.on_board)
        ]
        if not drains or not closers:
            continue
        # La fila si legge dalla macchina verso l'impianto: il serbatoio e' il
        # capo di arrivo, quindi «dal lato del serbatoio» vuol dire piu' avanti
        # nella fila.
        ok = min(drains) > max(closers)
        print(
            f"     lo scarico sta dal lato del serbatoio: {ok}"
            f"   (scarico in posizione {drains}, organi che chiudono {closers},"
            f" fila {names})"
        )
    print()


def main(argv: list[str]) -> int:
    wanted = [int(item) for item in argv] or sorted(IMPIANTI)
    for number in wanted:
        _report(number)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
