"""I grafi dei cinque impianti di prova, dalla catena corrente.

Fa girare, su ciascuno dei cinque impianti che il committente ha consegnato, la
prima parte della skill: le **regole** aggiungono cio' che manca, l'**assemblatore**
mette i pezzi in fila, e il grafo si scrive.

Non c'e' nessun disegno: il contenuto si giudica sul grafo scritto (D-096).

    python examples/prova/build_test_graphs.py
"""

import importlib.util
import sys
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph import Naming
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry

REPO_ROOT = Path(__file__).resolve().parents[2]
PLANTS = REPO_ROOT / "examples" / "prova"
CATALOG = REPO_ROOT / "examples" / "layout" / "catalog"
SYMBOLS = REPO_ROOT / "assets" / "symbols"
NAMING = REPO_ROOT / "naming"
RULES = REPO_ROOT / "rules" / "hydronic"
OUT = REPO_ROOT / "docs" / "prodotto" / "grafi-di-prova"


def generator() -> object:
    """Il generatore del grafo, riusato tale e quale: uno solo scrive i grafi."""
    path = REPO_ROOT / "examples" / "graph" / "build_plant_graph.py"
    spec = importlib.util.spec_from_file_location("build_plant_graph", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    symbols = SymbolRegistry.from_directory(SYMBOLS)
    catalog = ComponentRegistry.from_directory(CATALOG, symbols=symbols)
    naming = Naming.from_directory(NAMING)
    rules = RuleRegistry.from_directory(RULES)
    rules.cross_check(catalog)
    build = generator().build  # type: ignore[attr-defined]

    OUT.mkdir(parents=True, exist_ok=True)
    for path in sorted(PLANTS.glob("prova-*.json")):
        project = load_project(path)
        completed, _, gaps = saturate(project, catalog, rules)
        target = OUT / f"{path.stem}.md"
        target.write_text(build(completed, catalog, naming, gaps), encoding="utf-8")
        print(f"scritto {target.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
