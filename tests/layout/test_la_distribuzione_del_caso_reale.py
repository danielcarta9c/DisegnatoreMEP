"""La distribuzione del primo caso reale, dopo I-202 … I-205 (REL-009, punto 6).

Il PO, sulla tavola fatta con la 1.3.0: le pompe di zona una in verticale e una in
orizzontale (I-204); i colori sbagliati nella distribuzione (I-202); il collettore con
ritorno che si raccorda ai terminali con «un sacco di curve inutili» (I-205).

- **Le pompe in parallelo**: la fila di una pompa che ha una sorella sullo stesso raccordo
  si posa sul primo orizzontale che la contiene, anche se la tratta parte in verticale.
- **I colori**: il ritorno che esce dal collettore con ritorno e' ritorno — la camminata
  non attraversa il collettore dalla mandata al ritorno —; e la mandata della pompa di
  carico del bollitore e' mandata — il bollitore, sulla sua serpentina, non e' una sorgente.
- **Il collettore**: le coppie mandata-ritorno a 10 mm, come gli attacchi dei terminali.
"""

# categoria: difende il disegno — I-202, I-204, I-205, il primo caso reale

import contextlib
import io
from datetime import date
from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import inline_component_ids
from disegnatore_mep.layout.flow import classify_trunks
from disegnatore_mep.layout.geometry import Point, RoutedTrunk
from disegnatore_mep.layout.grid import GridSpace
from disegnatore_mep.layout.inline import place_inline_accessories
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import (
    ComponentInstance,
    ConnectionModel,
    NetworkModel,
    PortRef,
    ProjectMetadata,
    ProjectModel,
)
from disegnatore_mep.model.types import PlantRegime
from disegnatore_mep.skill import cartelle_del_repository, main

ROOT = Path(__file__).resolve().parents[2]
CASO = ROOT / "docs" / "collaudi" / "REL-009" / "caso-reale-2" / "grafo-prima-stesura.json"


@cache
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog",
        symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols"),
    )


# --- le pompe in parallelo (I-204) --------------------------------------------


def _due_pompe() -> ProjectModel:
    def tubo(ident: str, a: str, b: str) -> ConnectionModel:
        (pa, porta_a), (pb, porta_b) = a.split("."), b.split(".")
        return ConnectionModel(
            id=ident,
            network_id="sec",
            endpoint_a=PortRef(component_id=pa, port_id=porta_a),
            endpoint_b=PortRef(component_id=pb, port_id=porta_b),
        )

    pezzi = [("divide", "tee-split"), ("zona-1", "fan-coil"), ("zona-2", "fan-coil")]
    for n in (1, 2):
        pezzi += [(f"v{n}a", "valve-isolation"), (f"pompa-{n}", "pump-circulator"), (f"v{n}b", "valve-isolation")]
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="pompe", client="prova", project_name="prova",
            commission_code="PROVA", revision="00", issue_date=date(2026, 10, 3),
        ),
        plant_regime=PlantRegime.UP_TO_35_KW,
        networks=[NetworkModel(id="sec", name="sec", domain="hydronic", medium="heating_water")],
        components=[ComponentInstance(id=ident, definition_id=voce) for ident, voce in pezzi],
        connections=[
            tubo(f"m{n}{k}", a, b)
            for n, porta in ((1, "b"), (2, "c"))
            for k, (a, b) in enumerate(
                [
                    (f"divide.{porta}", f"v{n}a.a"),
                    (f"v{n}a.b", f"pompa-{n}.a"),
                    (f"pompa-{n}.b", f"v{n}b.a"),
                    (f"v{n}b.b", f"zona-{n}.in"),
                ]
            )
        ],
    )


def test_la_fila_di_una_pompa_in_parallelo_va_sull_orizzontale() -> None:
    """La tratta parte con 40 mm di verticale, che conterrebbero valvola, pompa e valvola:
    fino a I-204 la fila ci si posava, e la pompa usciva in verticale accanto alla sorella
    orizzontale."""
    project = _due_pompe()
    registry = catalogo()
    trunks = build_trunks(project, inline_component_ids(project, registry))
    tratta = next(item for item in trunks if "pompa-2" in item.inline_component_ids)
    area = NOVE_C_A3.drawing_rect_mm
    x0, y0 = area.x_mm + 50, area.y_mm + 50
    instradata = RoutedTrunk(
        network_id="sec",
        medium="heating_water",
        connection_ids=list(tratta.connection_ids),
        segments=[[Point(x_mm=x0, y_mm=y0), Point(x_mm=x0, y_mm=y0 + 40), Point(x_mm=x0 + 80, y_mm=y0 + 40)]],
    )
    griglia = GridSpace(origin=area, standard=NOVE_C_A3.standard)
    posati, _ = place_inline_accessories(project, tratta, instradata, registry, griglia, trunks=trunks)
    rotazioni = {item.component_id: item.rotation_deg % 180 for item in posati}
    assert rotazioni == {"v2a": 0, "pompa-2": 0, "v2b": 0}, rotazioni


# --- i colori (I-202) ---------------------------------------------------------


@pytest.fixture(scope="module")
def colori(tmp_path_factory: pytest.TempPathFactory) -> dict[tuple[str, str], bool | None]:
    """Mandata o ritorno di ogni tratta del caso, per i suoi due capi."""
    cartella = tmp_path_factory.mktemp("caso-reale-2")
    with contextlib.redirect_stdout(io.StringIO()):
        assert main(["completa", str(CASO), "--out", str(cartella / "gc.json")], cartelle_del_repository(ROOT)) == 0
    project = load_project(cartella / "gc.json")
    registry = catalogo()
    trunks = build_trunks(project, inline_component_ids(project, registry))
    flussi = classify_trunks(project, registry, trunks)
    return {
        (item.start.component_id, item.end.component_id): flussi[item.connection_ids].supply
        for item in trunks
    }


def _ruolo(colori: dict[tuple[str, str], bool | None], da: str, a: str) -> bool | None:
    return colori.get((da, a), colori.get((a, da)))


def test_il_ritorno_che_esce_dal_collettore_con_ritorno_e_ritorno(colori: dict[tuple[str, str], bool | None]) -> None:
    assert _ruolo(colori, "coll-mz1-1", "tj-mz1-1") is False
    assert _ruolo(colori, "tj-mz1-1", "tj-mz") is False
    assert _ruolo(colori, "ts-mz1-1", "coll-mz1-1") is True
    assert _ruolo(colori, "coll-mz1-1", "fc-mz1-1") is True
    assert _ruolo(colori, "fc-mz1-1", "coll-mz1-1") is False


def test_la_mandata_della_pompa_di_carico_del_bollitore_e_mandata(colori: dict[tuple[str, str], bool | None]) -> None:
    assert _ruolo(colori, "volano-acs", "bollitore") is True


# --- il collettore (I-205) ----------------------------------------------------


def test_le_coppie_del_collettore_hanno_l_interasse_dei_terminali() -> None:
    simboli = SymbolRegistry.from_directory(ROOT / "assets" / "symbols")
    collettore = {porta.id: porta.x_mm for porta in simboli.get("zone-manifold-pair").manifest.ports}
    for terminale in ("fan-coil", "underfloor-panel"):
        girato = {porta.id: porta.x_mm for porta in simboli.get(terminale).manifest.rotated(270, True).ports}
        interasse = girato["out"] - girato["in"]
        assert interasse == 10
        for k in (1, 2):
            assert collettore[f"ret_{k}"] - collettore[f"out_{k}"] == interasse
    assert collettore["out_2"] - collettore["ret_1"] >= 10, "fra due terminali larghi 15 restano 5 mm"
