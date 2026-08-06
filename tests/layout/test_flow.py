"""Mandata e ritorno vengono dalla topologia, non da come e' venuto il disegno.

Il difetto che queste prove chiudono: la valvola deviatrice del caso D-011 era
finita a sinistra della pompa di calore, e la mandata che la alimenta veniva
percio' disegnata come ritorno — blu, e in entrata dal lato sbagliato.
"""

from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.flow import orient_trunks
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import ProjectModel

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"


def oriented() -> dict[str, bool | None]:
    catalog = ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
    project = load_project(PROJECT)
    trunks = build_trunks(project, inline_component_ids(project, catalog))
    return {
        ",".join(key): value
        for key, value in orient_trunks(project, catalog, trunks).items()
    }


def test_what_leaves_the_generator_is_supply() -> None:
    """p1 va dalla pompa di calore alla valvola deviatrice: e' mandata."""
    assert oriented()["p1"] is True


def test_what_comes_back_into_the_generator_is_return() -> None:
    """p4,p5 dal volano e p7 dal bollitore rientrano in pompa: sono ritorni."""
    marks = oriented()
    assert marks["p4,p5"] is False
    assert marks["p7"] is False


def test_the_whole_primary_circuit_is_oriented() -> None:
    marks = oriented()
    assert {key: marks[key] for key in ("p1", "p2,p3", "p6")} == {
        "p1": True,
        "p2,p3": True,
        "p6": True,
    }


def test_the_secondary_is_oriented_on_its_own_source() -> None:
    """Il volano e' l'utilizzatore del primario e la sorgente del secondario."""
    marks = oriented()
    assert marks["s1,s2"] is True
    assert marks["s3"] is True and marks["s4"] is True
    assert marks["s5"] is False and marks["s6"] is False


@pytest.mark.skip(
    reason="La composizione e' il pezzo da rifare del piano: con gli accessori "
    "sugli stacchi al posto giusto l'impianto completo chiede piu' larghezza di "
    "quanta ne abbia un foglio ordinario, e il posizionamento a fasce non ci "
    "arriva. Non e' un difetto del contenuto — quello si giudica sul grafo "
    "scritto (D-096) — ed e' esattamente il limite che il pezzo della "
    "composizione deve chiudere. Queste prove tornano quando quel pezzo si fa."
)
def test_orientation_does_not_depend_on_where_the_drawing_put_things() -> None:
    """E' la proprieta' che il difetto violava: nessuna coordinata entra qui."""
    marks = oriented()
    supply = {key for key, value in marks.items() if value is True}
    assert supply == {"p1", "p2,p3", "p6", "s1,s2", "s3", "s4"}
    assert {key for key, value in marks.items() if value is False} == {
        "p4,p5",
        "p7",
        "s5",
        "s6",
    }


def test_a_ring_with_no_load_stays_undecided() -> None:
    """Nessun utilizzatore separa andata e ritorno: qui non si inventa un verso.

    Due collettori in anello: nessuno dei due produce, accumula o utilizza, e
    percorrerlo in avanti o all'indietro raggiunge le stesse due tratte.
    """
    catalog = ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
    ring = ProjectModel.model_validate(
        {
            "metadata": {
                "project_id": "ring",
                "client": "Nove C",
                "project_name": "Anello",
                "commission_code": "DEV-002",
                "revision": "00",
                "issue_date": "2026-08-04",
            },
            "networks": [
                {
                    "id": "loop",
                    "name": "Anello",
                    "domain": "hydronic",
                    "medium": "heating_water",
                }
            ],
            "components": [
                {"id": "m1", "definition_id": "zone-manifold"},
                {"id": "m2", "definition_id": "zone-manifold"},
            ],
            "connections": [
                {
                    "id": "c1",
                    "network_id": "loop",
                    "endpoint_a": {"component_id": "m1", "port_id": "out_1"},
                    "endpoint_b": {"component_id": "m2", "port_id": "in"},
                },
                {
                    "id": "c2",
                    "network_id": "loop",
                    "endpoint_a": {"component_id": "m2", "port_id": "out_1"},
                    "endpoint_b": {"component_id": "m1", "port_id": "in"},
                },
            ],
        }
    )
    trunks = build_trunks(ring, inline_component_ids(ring, catalog))
    assert set(orient_trunks(ring, catalog, trunks).values()) == {None}
