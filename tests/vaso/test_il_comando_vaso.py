"""Il comando `vaso` sul grafo completo (D-220, D-221, D-224)."""

from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.vaso.comando import applica

ROOT = Path(__file__).resolve().parents[2]
COMPLETO = ROOT / "examples" / "rules" / "centrale-pdc-completa.json"


@pytest.fixture(scope="module")
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog", symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols")
    )


def _con_livello(livello: str | None):  # type: ignore[no-untyped-def]
    modello = load_project(COMPLETO)
    return modello.model_copy(update={"metadata": modello.metadata.model_copy(update={"livello": livello})})


def test_nel_definitivo_solo_la_taglia(catalogo: ComponentRegistry) -> None:
    completo, vaso, _ = applica(_con_livello(None), catalogo, 200, 55, 6)
    vasi = [c for c in completo.components if c.definition_id == "expansion-connection"]
    assert [c.properties.get("volume_l") for c in vasi] == [vaso.taglia_l]
    assert "precarica_bar" not in vasi[0].properties
    assert not [c for c in completo.components if c.properties.get("etichetta")]


def test_nell_esecutivo_anche_precarica_tarature_e_carica(catalogo: ComponentRegistry) -> None:
    completo, vaso, scritto = applica(_con_livello("esecutivo"), catalogo, 200, 55, 6)
    vasi = [c for c in completo.components if c.definition_id == "expansion-connection"]
    assert vasi[0].properties["precarica_bar"] == vaso.precarica_bar
    etichette = {c.definition_id: c.properties["etichetta"] for c in completo.components if c.properties.get("etichetta")}
    assert etichette.get("valve-safety") == "3 bar"
    assert etichette.get("filling-unit", "").startswith("carica ")
    assert scritto


def test_due_vasi_si_dicono_uno_per_volta(catalogo: ComponentRegistry) -> None:
    """Il caso reale ha due primari, e due vasi d'impianto: il comando non sceglie."""
    from disegnatore_mep.rules.apply import saturate
    from disegnatore_mep.rules.registry import RuleRegistry

    regole = RuleRegistry.from_directory(ROOT / "rules" / "hydronic")
    caso = load_project(ROOT / "docs" / "collaudi" / "REL-009" / "caso-reale-2" / "grafo-prima-stesura.json")
    completo, _, _ = saturate(caso, catalogo, regole)
    with pytest.raises(ValueError, match="piu' vasi"):
        applica(completo, catalogo, 200, 55, 6)
    vasi = [c.id for c in completo.components if c.definition_id == "expansion-connection"]
    scritto, vaso, _ = applica(completo, catalogo, 1000, 55, 3, vaso_id=vasi[0])
    assert next(c for c in scritto.components if c.id == vasi[0]).properties["volume_l"] == vaso.taglia_l
