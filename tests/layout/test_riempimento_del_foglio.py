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


def test_il_riempimento_non_si_compra_con_pieghe_e_incroci() -> None:
    """La posa rivista non e' mai piu' piegata ne' piu' incrociata di quella di
    partenza: il riempimento puo' salire, **le curve no**.

    **Riscritta il 17 settembre 2026 da `DRAW-012` §D.** Fino a `DRAW-011`
    questa prova chiedeva anche che la posa rivista non fosse **piu' lunga**:
    era il rovescio della vecchia distensione, e con D-139 non e' piu' vero —
    la lunghezza non e' un costo, e il riempimento puo' comprarne quanto gliene
    serve per entrare nella propria finestra. Cio' che non puo' comprare resta
    scritto qui, ed e' quanto il PO chiama il costo vero: le curve, e poi gli
    attraversamenti.
    """
    project, partition, inline, first = _posa()
    improver = Improver(project, partition, _registry(), NOVE_C_A3, first, inline)
    before = improver.measure(first)
    after = improver.measure(
        improve.improve_sheet(project, partition, _registry(), NOVE_C_A3, list(first), inline)
    )
    assert before is not None and after is not None
    assert not before.cost.beats(after.cost)
    assert after.cost.bends <= before.cost.bends
    assert after.cost.crossings <= before.cost.crossings


def test_la_distensione_non_esiste_piu() -> None:
    """Nessun obiettivo minimo di riempimento dentro il collocatore (§2).

    Resta vero con D-139, e per la ragione che D-139 stessa dichiara: una
    **finestra** non e' un traguardo. Cio' che D-134 rifiutava — inseguire una
    percentuale sempre piu' alta — resta rifiutato, e la prova che il
    riempimento non sia monotono sta in `test_ordine_del_disegnatore.py`.
    """
    for name in ("FILL_TARGET_RATIO", "SPREAD_STEPS", "MAX_SPREAD_TRIALS"):
        assert not hasattr(improve, name), name
    # E la lunghezza non e' piu' una voce del confronto: sta nella tupla come
    # misura, dopo gli spareggi, e `key()` non la legge (DRAW-012 §D.1).
    fields = improve.SheetCost._fields
    assert fields.index("fill") < fields.index("imbalance") < fields.index("length_mm")
    corta = improve.SheetCost(
        violations=0, turnback_runs=0, turnback_mm=0.0, long_runs=0, bends=2,
        crossings=0, fill=0.55, coverage=0.8, imbalance=1.0, length_mm=10.0,
    )
    assert corta.key() == corta._replace(length_mm=10_000.0).key()


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
