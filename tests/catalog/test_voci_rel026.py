"""Le voci di `REL-026` (I-300): il ventilconvettore canalizzato col lato aria e il plenum
di mandata non motorizzato da due a sei uscite.

Vengono da una copia della skill usata su una commessa
(`docs/input-pm/2026-11-13-rilievi-bd-rm-260/estendi_catalogo.py`), rifatte nel catalogo
generato. Forma e sigla sono **proposte** che il PO giudica sulla tavola; queste prove
dicono che il catalogo le porta coerenti — simbolo, sigla, domini, quote — e che il
plenum di mandata resta il fratello del plenum di zona, che non si tocca.
"""

import json
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentTrait
from disegnatore_mep.graph import Naming
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.model.types import Domain

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
NAMING = ROOT / "naming"
USCITE = range(2, 7)
PASSO_DI_GRIGLIA_MM = 2.5

SIGLE: dict[str, str] = {
    "fan-coil-ducted-air": "TE",
    **{f"supply-plenum-{n}": "PL" for n in USCITE},
}


@pytest.fixture(scope="module")
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS))


@pytest.mark.parametrize("voce", sorted(SIGLE))
def test_ogni_voce_nuova_carica_col_suo_simbolo_e_si_risolve(catalogo: ComponentRegistry, voce: str) -> None:
    risolta = catalogo.resolve(voce)
    assert {porta.id for porta in risolta.ports()} == set(risolta.symbol.manifest.port_ids)


@pytest.mark.parametrize("voce", sorted(SIGLE))
def test_ogni_voce_nuova_prende_la_sigla_della_sua_famiglia(catalogo: ComponentRegistry, voce: str) -> None:
    definizione = catalogo.get(voce)
    famiglia = Naming.from_directory(NAMING).family_of(tuple(definizione.functions), voce)
    assert famiglia.prefix == SIGLE[voce]


def test_la_famiglia_del_plenum_di_mandata_sta_dopo_quella_del_plenum_di_zona() -> None:
    famiglie = json.loads((NAMING / "families.json").read_text(encoding="utf-8"))["families"]
    mestieri = [item["function"] for item in famiglie]
    assert mestieri.index("air_distribution") == mestieri.index("air_zoning") + 1
    voce = famiglie[mestieri.index("air_distribution")]
    assert (voce["prefix"], voce["name"]) == ("PL", "Plenum di mandata")


def test_il_plenum_di_zona_resta_plz(catalogo: ComponentRegistry) -> None:
    naming = Naming.from_directory(NAMING)
    for n in USCITE:
        definizione = catalogo.get(f"zoning-plenum-{n}")
        assert naming.family_of(tuple(definizione.functions), definizione.id).prefix == "PLZ"


@pytest.mark.parametrize("n", USCITE)
def test_il_plenum_di_mandata_e_il_plenum_di_zona_senza_motori(catalogo: ComponentRegistry, n: int) -> None:
    """Stesso riquadro, stesse uscite alle stesse quote; nessuna porta di comando."""
    mandata = catalogo.resolve(f"supply-plenum-{n}")
    zona = catalogo.resolve(f"zoning-plenum-{n}")
    assert mandata.box_mm == zona.box_mm
    uscite = {p.id: (p.face, p.y_mm) for p in mandata.symbol.manifest.ports if p.id.startswith("out_")}
    assert uscite == {p.id: (p.face, p.y_mm) for p in zona.symbol.manifest.ports if p.id.startswith("out_")}
    assert len(uscite) == n
    assert {p.domain for p in mandata.definition.ports} == {Domain.AERAULIC}
    assert all(p.required for p in mandata.definition.ports)
    assert mandata.definition.functions == ["air_distribution"]


@pytest.mark.parametrize("n", USCITE)
def test_l_ingresso_del_plenum_di_mandata_sta_al_centro_delle_uscite(catalogo: ComponentRegistry, n: int) -> None:
    """Il PO, 13 novembre 2026 (I-300): il plenum non e' una tre vie, e l'ingresso sta al
    centro. Con le uscite dispari e' in asse con quella di mezzo; con le pari il centro cade
    a mezzo passo, e l'ingresso va sulla quota di griglia piu' vicina, che e' il centro del
    riquadro."""
    manifesto = catalogo.resolve(f"supply-plenum-{n}").symbol.manifest
    ingresso = manifesto.port("in")
    uscite = sorted(p.y_mm for p in manifesto.ports if p.id.startswith("out_"))
    centro = (uscite[0] + uscite[-1]) / 2
    assert ingresso.face.value == "left"
    assert abs(ingresso.y_mm / PASSO_DI_GRIGLIA_MM - round(ingresso.y_mm / PASSO_DI_GRIGLIA_MM)) < 1e-9
    assert abs(ingresso.y_mm - centro) <= PASSO_DI_GRIGLIA_MM / 2 + 1e-9
    if n % 2:
        assert ingresso.y_mm == uscite[n // 2]
    else:
        assert ingresso.y_mm == manifesto.height_mm / 2
        assert ingresso.y_mm not in uscite


def test_il_ventilconvettore_col_lato_aria(catalogo: ComponentRegistry) -> None:
    """Un terminale d'acqua come il ventilconvettore canalizzato, con l'aria e la condensa
    dell'unita' interna canalizzata: si manutiene sull'acqua, e aria e condensa sono
    facoltative."""
    risolto = catalogo.resolve("fan-coil-ducted-air")
    definizione = risolto.definition
    porte = {p.id: p for p in definizione.ports}
    assert definizione.functions == ["emission"]
    assert definizione.has_trait(ComponentTrait.MAINTAINABLE)
    assert (porte["in"].domain, porte["out"].domain) == (Domain.HYDRONIC, Domain.HYDRONIC)
    assert porte["in"].required and porte["out"].required
    assert (porte["supply"].medium, porte["return"].medium, porte["drain"].medium) == (
        "supply_air", "return_air", "condensate"
    )
    assert not any(porte[p].required for p in ("supply", "return", "drain"))
    # Le porte di comando sono quelle del simbolo, messe da parte finche' il grafo non le collega.
    assert catalogo.porte_di_comando("fan-coil-ducted-air") == {"power", "bus", "consenso_in", "consenso"}
    assert set(porte) == {"in", "out", "supply", "return", "drain"}
    # Le quote dell'unita' interna canalizzata: mandata dell'aria a 12,5, ripresa in alto.
    unita = catalogo.resolve("ducted-indoor-unit").symbol.manifest
    for porta in ("supply", "return", "drain"):
        assert risolto.symbol.manifest.port(porta) == unita.port(porta)
    assert risolto.box_mm == catalogo.resolve("ducted-indoor-unit").box_mm
