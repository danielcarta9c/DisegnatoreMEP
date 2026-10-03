"""Il tempo del disegna sul caso reale: la catena di un attacco si conta una volta (REL-009, punto 7).

Il PO: «La skill gira in 30 minuti buoni, c'e' qualcosa che non va forse» (I-205). Misurato il 3
ottobre 2026 sul caso ricostruito (`docs/collaudi/REL-009/caso-reale-2/`), con la 1.4 prima della
correzione: `disegna` 107 secondi, e 269 dei 271 del profilo nella posa d'inventario — che del piano
non usa le coordinate. La posa, a ogni posto che prova per un pezzo, rifaceva i corridoi davanti a
tutti gli attacchi gia' posati, e per ogni attacco cercava la sua tratta rileggendole tutte: 460 mila
domande, 74 milioni di confronti. La catena di un attacco non cambia da una domanda all'altra.

Dopo: `disegna` 3,5 secondi, e le tavole agli atti identiche byte per byte. La prova conta le catene
che la posa chiede: prima della correzione erano 453 753.
"""

# categoria: difende la consegna — il tempo della skill (I-205, REL-009 punto 7)

import contextlib
import io
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout import place
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.partition import partition_project
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.piano.esecutore import _FOGLIO_DELL_INVENTARIO
from disegnatore_mep.skill import cartelle_del_repository, main

ROOT = Path(__file__).resolve().parents[2]
CASO = ROOT / "docs" / "collaudi" / "REL-009" / "caso-reale-2" / "grafo-prima-stesura.json"


def test_la_posa_d_inventario_chiede_la_catena_di_un_attacco_una_volta(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with contextlib.redirect_stdout(io.StringIO()):
        assert main(["completa", str(CASO), "--out", str(tmp_path / "gc.json")], cartelle_del_repository(ROOT)) == 0
    progetto = load_project(tmp_path / "gc.json")
    catalogo = ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog",
        symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols"),
    )
    in_linea = inline_component_ids(progetto, catalogo)
    partizione = partition_project(progetto, build_trunks(progetto, in_linea))[0]

    chieste = 0
    vera = place.machine_chains

    def contata(*argomenti, **chiavi):  # type: ignore[no-untyped-def]
        nonlocal chieste
        chieste += 1
        return vera(*argomenti, **chiavi)

    monkeypatch.setattr(place, "machine_chains", contata)
    posati = place.place_sheet(progetto, partizione, catalogo, _FOGLIO_DELL_INVENTARIO, in_linea)

    attacchi = sum(
        len(catalogo.resolve(item.definition_id).symbol.manifest.ports)
        for item in progetto.components
        if item.id in {pezzo.component_id for pezzo in posati}
    )
    # Al piu' una per attacco e per giacitura; prima della correzione, 453 753.
    assert chieste <= 2 * attacchi, (chieste, attacchi)
