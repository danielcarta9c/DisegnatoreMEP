"""Quante volte scatta il ripiego di `compose_sheet` (DRAW-010, criterio 5).

`compose_sheet` prova quattro pose, in quest'ordine: quella del **ciclo sulle
fasi**, quella **seminata dalla fase del tronco**, quella del **ciclo senza le
fasi** — la tavola che sarebbe uscita prima di DRAW-008 — e infine la
**disposizione di partenza**. La prima che si instrada vince. Una tavola che
esce dal secondo, dal terzo o dal quarto tentativo e' una tavola che il ripiego
ha salvato, non la tavola che la catena a fasi voleva.

Lo strumento non rifa' quella catena — la rifarebbe diversa, prima o poi. Chiama
`compose_on_ordinary_frame`, cioe' esattamente cio' che chiama la CLI, e **conta
le chiamate** che ogni tavola fa a `settle_sheet`, che e' una per tentativo:
quanti falliscono prima del primo che riesce e' l'indice del ripiego che ha
lavorato, e il messaggio di ciascuno dice perche' quel tentativo e' caduto.

    python docs/collaudi/DRAW-010/il-ripiego.py
    python docs/collaudi/DRAW-010/il-ripiego.py 4
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from disegnatore_mep.catalog.registry import ComponentRegistry  # noqa: E402
from disegnatore_mep.graphics.registry import SymbolRegistry  # noqa: E402
from disegnatore_mep.io.project_json import load_project  # noqa: E402
from disegnatore_mep.layout import compose as compose_module  # noqa: E402
from disegnatore_mep.layout.compose import compose_on_ordinary_frame  # noqa: E402
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

TENTATIVI = (
    "il ciclo sulle fasi",
    "la posa seminata dalla fase del tronco",
    "il ciclo senza le fasi",
    "la disposizione di partenza",
)


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
    settle = compose_module.settle_sheet
    sheet = compose_module.compose_sheet
    diario: list[tuple[str, str, list[str]]] = []
    stato: dict[str, object] = {"frame": "", "esiti": []}

    def watched_settle(*args: object, **kwargs: object):  # type: ignore[no-untyped-def]
        esiti = stato["esiti"]
        assert isinstance(esiti, list)
        try:
            out = settle(*args, **kwargs)  # type: ignore[arg-type]
        except LayoutError as error:
            esiti.append(f"cade: {error}")
            raise
        esiti.append("si instrada")
        return out

    def watched_sheet(project, partition, cat, frame, inline):  # type: ignore[no-untyped-def]
        esiti: list[str] = []
        stato["esiti"] = esiti
        try:
            return sheet(project, partition, cat, frame, inline)
        finally:
            formato = f"{frame.standard.sheet_width_mm:g}x{frame.standard.sheet_height_mm:g}"
            diario.append((formato, partition.sheet_id, esiti))

    compose_module.settle_sheet = watched_settle  # type: ignore[assignment]
    compose_module.compose_sheet = watched_sheet  # type: ignore[assignment]
    try:
        frame, drawing = compose_on_ordinary_frame(model, registry)
        uscita = (
            f"la tavola esce su {frame.standard.sheet_width_mm:g}x"
            f"{frame.standard.sheet_height_mm:g}, {len(drawing.sheets)} foglio/i"
        )
    except LayoutError as error:
        uscita = f"la tavola NON esce: {error}"
    finally:
        compose_module.settle_sheet = settle  # type: ignore[assignment]
        compose_module.compose_sheet = sheet  # type: ignore[assignment]
    print(f"   {uscita}")
    for formato, sheet_id, esiti in diario:
        riusciti = [index for index, esito in enumerate(esiti) if esito == "si instrada"]
        scattato = riusciti[0] if riusciti else len(esiti)
        print(f"   {formato} / tavola {sheet_id}: il ripiego scatta {scattato} volte")
        for index, esito in enumerate(esiti):
            etichetta = TENTATIVI[index] if index < len(TENTATIVI) else "l'ultima prova"
            print(f"     {index}. {etichetta}: {esito}")
    print()


def main(argv: list[str]) -> int:
    wanted = [int(item) for item in argv] or sorted(IMPIANTI)
    for number in wanted:
        _report(number)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
