"""Il rele' d'appoggio porta la sigla del circolatore che alimenta (I-267): KA-CIR-02."""

from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph.naming import Naming
from disegnatore_mep.graph.plant import read_plant
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project

ROOT = Path(__file__).resolve().parents[2]
VILLETTA = ROOT / "docs" / "collaudi" / "REL-015" / "pdc-regola" / "grafo-completo.json"


def test_ogni_rele_porta_la_sigla_del_suo_circolatore() -> None:
    catalogo = ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog", symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols")
    )
    modello = load_project(VILLETTA)
    sigle = read_plant(modello, catalogo.per_il_progetto(modello), Naming.from_directory(ROOT / "naming")).sigle
    rele = [c for c in modello.components if c.definition_id == "interface-relay"]
    assert len(rele) == 3
    for pezzo in rele:
        carico = next(
            (c.endpoint_b if c.endpoint_a.component_id == pezzo.id else c.endpoint_a).component_id
            for c in modello.connections
            if (pezzo.id, "b") in (
                (c.endpoint_a.component_id, c.endpoint_a.port_id),
                (c.endpoint_b.component_id, c.endpoint_b.port_id),
            )
        )
        assert sigle[pezzo.id] == f"KA-{sigle[carico]}", (pezzo.id, sigle[pezzo.id], sigle[carico])
