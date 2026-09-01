"""Il foglio pieno e l'inchiostro distribuito sono obiettivi, non avvisi (D-111).

Le due misure esistevano gia' — il preflight avvisa quando il foglio e' pieno
per meno di tre quinti e quando il quadrante piu' pieno pesa piu' di tre volte
il piu' vuoto — ma **nessuno le guardava mentre disponeva**: il collocatore le
scopriva alla fine, sotto forma di rilievo, quando non c'era piu' niente da
fare. Il ciclo che rivede la disposizione tira in una direzione sola, stringere,
perche' pieghe, incroci e lunghezza si pagano tutti accorciando: il risultato
era corretto e stava in un angolo del foglio.

Qui si prova che il collocatore, dopo aver ottimizzato le linee, **distende** —
e che lo fa senza vendere niente di cio' che viene prima: nessuna piega in piu',
nessun incrocio in piu', nessuna tratta che perde i propri accessori.
"""

from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout import improve
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.geometry import (
    PlacedSymbol,
    RoutedTrunk,
    fill_ratio,
    ink_imbalance,
)
from disegnatore_mep.layout.grid import GridSpace
from disegnatore_mep.layout.inline import settle_sheet
from disegnatore_mep.layout.partition import SheetPartition, partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import ProjectModel

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"

AREA = (
    NOVE_C_A3.drawing_rect_mm.x_mm,
    NOVE_C_A3.drawing_rect_mm.y_mm,
    NOVE_C_A3.drawing_rect_mm.right_mm,
    NOVE_C_A3.drawing_rect_mm.bottom_mm,
)


def _registry() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def _case() -> tuple[ProjectModel, SheetPartition, frozenset[str]]:
    project = load_project(PROJECT)
    inline = inline_component_ids(project, _registry())
    partition = partition_project(project, build_trunks(project, inline))[0]
    return project, partition, inline


def _drawn(
    project: ProjectModel, partition: SheetPartition, placed: list[PlacedSymbol]
) -> tuple[list[PlacedSymbol], list[RoutedTrunk]]:
    grid = GridSpace(origin=NOVE_C_A3.drawing_rect_mm, standard=NOVE_C_A3.standard)
    settled = settle_sheet(
        project, list(partition.trunks), placed, _registry(), grid, tolerant=True
    )
    return settled.symbols, settled.routes


def _bends(routes: list[RoutedTrunk]) -> int:
    return sum(
        max(len(segment) - 2, 0) for route in routes for segment in route.segments
    )


def test_la_distensione_riempie_il_foglio_senza_vendere_le_linee(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """La stessa disposizione, con e senza distensione: quella distesa riempie.

    Il confronto e' fra le due uscite dello **stesso** ciclo, non fra la posa di
    partenza e quella rivista: il ciclo che ottimizza le linee stringe — e' il
    suo mestiere — e la distensione lavora dopo di lui, su cio' che lui lascia.
    Metterle sulla stessa bilancia direbbe soltanto quale delle due tira piu'
    forte.

    Le voci del PM restano davanti a tutto (D-060): quello che la distensione
    puo' spendere e' **solo** lunghezza di tubazione, che e' il prezzo dichiarato
    del riempimento.
    """
    project, partition, inline = _case()
    first = place_sheet(project, partition, _registry(), NOVE_C_A3, inline)

    monkeypatch.setattr(improve, "MAX_SPREAD_TRIALS", 0)
    tight = improve.improve_sheet(
        project, partition, _registry(), NOVE_C_A3, list(first), inline
    )
    monkeypatch.undo()
    spread = improve.improve_sheet(
        project, partition, _registry(), NOVE_C_A3, list(first), inline
    )

    tight_symbols, tight_routes = _drawn(project, partition, tight)
    spread_symbols, spread_routes = _drawn(project, partition, spread)

    assert fill_ratio(spread_symbols, spread_routes, AREA) > fill_ratio(
        tight_symbols, tight_routes, AREA
    )
    assert _bends(spread_routes) <= _bends(tight_routes)
    assert sum(len(route.crossings) for route in spread_routes) <= sum(
        len(route.crossings) for route in tight_routes
    )
    line_mm = NOVE_C_A3.standard.line_medium_mm
    assert ink_imbalance(
        spread_symbols, spread_routes, AREA, line_mm
    ) <= ink_imbalance(tight_symbols, tight_routes, AREA, line_mm)


def test_la_disposizione_rivista_e_sempre_la_stessa() -> None:
    """Determinismo: mosse in ordine fisso, accettazione greedy, tetto fisso."""
    project, partition, inline = _case()
    first = place_sheet(project, partition, _registry(), NOVE_C_A3, inline)
    once = improve.improve_sheet(
        project, partition, _registry(), NOVE_C_A3, list(first), inline
    )
    twice = improve.improve_sheet(
        project, partition, _registry(), NOVE_C_A3, list(first), inline
    )
    assert [item.model_dump() for item in once] == [
        item.model_dump() for item in twice
    ]
