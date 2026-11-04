"""La villetta di riferimento (REL-015, pdc-regola) e' la rigenerazione corrente (REL-017).

Con la 1.9.0 il suo grafo completo agli atti era rimasto quello delle regole della 1.8, e il
piano idraulico non reggeva il corredo nuovo: nessuna prova se ne accorgeva."""

from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.canonical import canonical_json
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
QUI = ROOT / "docs" / "collaudi" / "REL-015" / "pdc-regola"


def test_il_grafo_completo_della_villetta_e_quello_che_le_regole_scrivono_oggi() -> None:
    catalogo = ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog", symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols")
    )
    grafo = load_project(QUI / "grafo.json")
    catalogo = catalogo.per_il_progetto(grafo)
    completo, _, _ = saturate(grafo, catalogo, RuleRegistry.from_directory(ROOT / "rules" / "hydronic"))
    assert canonical_json(completo) == (QUI / "grafo-completo.json").read_text(encoding="utf-8")
