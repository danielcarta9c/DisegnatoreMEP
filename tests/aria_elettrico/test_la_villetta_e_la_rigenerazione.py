"""La villetta di riferimento (REL-015, pdc-regola) e' la rigenerazione corrente (REL-017).

Con la 1.9.0 il suo grafo completo agli atti era rimasto quello delle regole della 1.8, e il
piano idraulico non reggeva il corredo nuovo: nessuna prova se ne accorgeva. Lo stesso per la
sua variante con il vaso sanitario e le note del progettista (REL-017, I-271, I-272).

Dalla REL-018 il grafo completo e' quello che `completa` scrive, e non solo le regole: dopo
le regole, la riduzione all'attacco (D-233) e i dati elettrici della linea della Shenling
dal manuale e dalla specifica (`elettrico.costruttori`, I-278) — l'alimentazione, la
corrente massima e il cavo minimo della macchina, i dati dell'interruttore QF-01."""

from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.diametri.riduzioni import posa_le_riduzioni
from disegnatore_mep.elettrico.costruttori import scrivi_i_dati_del_manuale
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.canonical import canonical_json
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
VILLETTE = [
    ROOT / "docs" / "collaudi" / "REL-015" / "pdc-regola",
    ROOT / "docs" / "collaudi" / "REL-017" / "vaso-note",
]


@pytest.mark.parametrize("qui", VILLETTE, ids=lambda item: item.parent.name)
def test_il_grafo_completo_della_villetta_e_quello_che_le_regole_scrivono_oggi(qui: Path) -> None:
    catalogo = ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog", symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols")
    )
    grafo = load_project(qui / "grafo.json")
    catalogo = catalogo.per_il_progetto(grafo)
    completo, _, _ = saturate(grafo, catalogo, RuleRegistry.from_directory(ROOT / "rules" / "hydronic"))
    # Come `completa` (skill.py): la riduzione all'attacco e i dati elettrici del manuale.
    completo, _ = posa_le_riduzioni(completo, catalogo)
    completo, _ = scrivi_i_dati_del_manuale(completo, catalogo)
    assert canonical_json(completo) == (qui / "grafo-completo.json").read_text(encoding="utf-8")
