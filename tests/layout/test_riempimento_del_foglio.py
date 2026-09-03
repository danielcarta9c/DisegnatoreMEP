"""Il riempimento del foglio non e' piu' un obiettivo del collocatore (DRAW-002).

Con DRAW-001 il ciclo, finite le linee, **distendeva**: allontanava i pezzi dal
centro per inseguire il 60 % di riempimento che il preflight dichiara, e lo
pagava in lunghezza di tubo. Il PO ha respinto quella tavola (I-021, I-022):
«bisogna spostare le macchine perche' spostare le macchine costa zero; invece
incroci, curve e lunghezze costano», e nessuna distanza va introdotta per
riempire il foglio.

Da DRAW-002 riempimento e bilanciamento restano **misure diagnostiche e
spareggi**: contano solo fra due geometrie uguali su violazioni, andate e
ritorno, pieghe, incroci e lunghezza. Qui si prova che il ciclo non compra piu'
carta con tubo, e che resta deterministico.
"""

from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout import improve
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.geometry import PlacedSymbol
from disegnatore_mep.layout.improve import Improver
from disegnatore_mep.layout.partition import SheetPartition, partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import ProjectModel

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"


def _registry() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def _case() -> tuple[ProjectModel, SheetPartition, frozenset[str]]:
    project = load_project(PROJECT)
    inline = inline_component_ids(project, _registry())
    partition = partition_project(project, build_trunks(project, inline))[0]
    return project, partition, inline


def _posa() -> tuple[ProjectModel, SheetPartition, frozenset[str], list[PlacedSymbol]]:
    project, partition, inline = _case()
    return project, partition, inline, place_sheet(
        project, partition, _registry(), NOVE_C_A3, inline
    )


def test_il_riempimento_non_si_compra_con_il_tubo() -> None:
    """La posa rivista non e' mai piu' lunga, piu' piegata o piu' incrociata
    della posa di partenza: il riempimento puo' solo salire a costo fermo.

    E' il rovescio della vecchia distensione, che accettava tubo in piu' in
    cambio di carta coperta. Ora il confronto unico della tavola la vieta.
    """
    project, partition, inline, first = _posa()
    improver = Improver(project, partition, _registry(), NOVE_C_A3, first, inline)
    before = improver.measure(first)
    after = improver.measure(
        improve.improve_sheet(project, partition, _registry(), NOVE_C_A3, list(first), inline)
    )
    assert before is not None and after is not None
    assert not before.cost.beats(after.cost)
    assert after.cost.length_mm <= before.cost.length_mm
    assert after.cost.bends <= before.cost.bends
    assert after.cost.crossings <= before.cost.crossings


def test_la_distensione_non_esiste_piu() -> None:
    """Nessun obiettivo minimo di riempimento dentro il collocatore (§2)."""
    for name in ("FILL_TARGET_RATIO", "SPREAD_STEPS", "MAX_SPREAD_TRIALS"):
        assert not hasattr(improve, name), name
    # Le voci di spareggio stanno in coda al costo, dopo la lunghezza.
    fields = improve.SheetCost._fields
    assert fields.index("length_mm") < fields.index("fill") < fields.index("imbalance")


def test_la_disposizione_rivista_e_sempre_la_stessa() -> None:
    """Determinismo: mosse in ordine fisso, accettazione greedy, tetto fisso."""
    project, partition, inline, first = _posa()
    once = improve.improve_sheet(
        project, partition, _registry(), NOVE_C_A3, list(first), inline
    )
    twice = improve.improve_sheet(
        project, partition, _registry(), NOVE_C_A3, list(first), inline
    )
    assert [item.model_dump() for item in once] == [
        item.model_dump() for item in twice
    ]
