"""Chi compone, e chi no (DRAW-010, criteri 7 e 16).

Due domande diverse, e si misurano tutte e due perche' la suite ne guarda una
sola:

- **`compose_drawing` su una A3 in un foglio solo** e' il contratto che la suite
  pretende (`COMPONIBILI` in `tests/layout/test_accessori_appesi.py`);
- **la CLI** — `compose_on_ordinary_frame`, il piu' piccolo formato ordinario su
  cui il disegno entra — e' la tavola che si consegna.

L'impianto 4 si e' perso fra le due: componeva per capacita' e non per
contratto, e quando ha smesso la suite e' rimasta verde. Questo strumento
esiste perche' non succeda una seconda volta.

    python docs/collaudi/DRAW-010/chi-compone.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from disegnatore_mep.catalog.registry import ComponentRegistry  # noqa: E402
from disegnatore_mep.graphics.frame import NOVE_C_A3  # noqa: E402
from disegnatore_mep.graphics.registry import SymbolRegistry  # noqa: E402
from disegnatore_mep.io.project_json import load_project  # noqa: E402
from disegnatore_mep.layout.compose import (  # noqa: E402
    compose_drawing,
    compose_on_ordinary_frame,
)
from disegnatore_mep.layout.errors import LayoutError  # noqa: E402
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


def _a3(model: ProjectModel) -> str:
    try:
        drawing = compose_drawing(model, catalog(), NOVE_C_A3)
    except LayoutError as error:
        return f"NO  ({error})"
    if len(drawing.sheets) != 1:
        return f"NO  (si divide in {len(drawing.sheets)} fogli)"
    return "SI"


def _cli(model: ProjectModel) -> str:
    try:
        frame, drawing = compose_on_ordinary_frame(model, catalog())
    except LayoutError as error:
        return f"NO  ({error})"
    return (
        f"SI  ({frame.standard.sheet_width_mm:g}x"
        f"{frame.standard.sheet_height_mm:g}, {len(drawing.sheets)} foglio/i)"
    )


def main(argv: list[str]) -> int:
    wanted = [int(item) for item in argv] or sorted(IMPIANTI)
    for number in wanted:
        name = IMPIANTI[number]
        model = completato(name)
        print(f"== impianto {number} — {name}")
        print(f"   compose_drawing su A3, un foglio solo : {_a3(model)}")
        print(f"   la CLI (formato ordinario piu' piccolo): {_cli(model)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
