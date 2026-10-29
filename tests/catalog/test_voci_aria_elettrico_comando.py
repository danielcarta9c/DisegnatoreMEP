"""Le voci di `REL-012`: l'aria-aria del kit del PO e il comando nell'idronico.

Dodici voci vengono dal kit (`docs/input-pm/2026-10-29-kit-aria-aria/`,
`RAPPORTO.md` §5.2, I-224), cinque sono proposte della sessione per l'elettrico
e il comando nell'idronico (I-226). Tutte si approvano sulla tavola; queste prove
dicono soltanto che il catalogo le porta come il kit le ha pensate — col loro
simbolo, la loro sigla, i domini giusti — e che non disturbano cio' che c'era.
"""

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

SIGLE: dict[str, str] = {
    # Il kit (I-224): le sigle che la tavola M.02 scrive accanto ai pezzi.
    "split-outdoor-unit": "UE",
    "ducted-indoor-unit": "UI",
    "zoning-plenum-5": "PLZ",
    "zone-controller": "CZ",
    "air-supply-terminal": "TA",
    "return-air-terminal": "RA",
    "condensate-trap": "SIF",
    "condensate-outlet": "AL",
    "electrical-panel": "QE",
    "isolator-switch": "SZ",
    "room-thermostat": "TZ",
    "wired-remote": "CF",
    # La fase 3 (I-226): sigle proposte dalla sessione, da approvare dal PO.
    "temperature-probe": "SO",
    "temperature-probe-dhw": "SO",
    "temperature-probe-solar": "SO",
    "outdoor-temperature-probe": "SE",
    "plant-controller": "RG",
}
"""Le diciassette voci nuove, con la sigla di famiglia che il loro mestiere porta."""

DOMINIO_DEL_FLUIDO: dict[str, Domain] = {
    "supply_air": Domain.AERAULIC,
    "return_air": Domain.AERAULIC,
    "refrigerant_liquid": Domain.REFRIGERANT,
    "refrigerant_gas": Domain.REFRIGERANT,
    "condensate": Domain.CONDENSATE,
    "power_supply": Domain.CONTROL,
    "interconnection": Domain.CONTROL,
    "control_bus": Domain.CONTROL,
}
"""Il dominio di ogni fluido fuori dall'acqua: un cavo e' comando, mai aria."""


def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS))


@pytest.mark.parametrize("voce", sorted(SIGLE))
def test_ogni_voce_nuova_carica_col_suo_simbolo_e_si_risolve(voce: str) -> None:
    """Il registro confronta le porte della voce con quelle del simbolo: una
    porta in piu' o in meno da una parte sola ferma il caricamento."""
    risolta = catalogo().resolve(voce)
    assert {porta.id for porta in risolta.ports()} == set(risolta.symbol.manifest.port_ids)


@pytest.mark.parametrize("voce", sorted(SIGLE))
def test_ogni_voce_nuova_prende_la_sigla_della_sua_famiglia(voce: str) -> None:
    definizione = catalogo().get(voce)
    famiglia = Naming.from_directory(NAMING).family_of(tuple(definizione.functions), voce)
    assert famiglia.prefix == SIGLE[voce]


def test_nessuna_voce_nuova_si_dichiara_manutenibile() -> None:
    """`RAPPORTO.md` §5.2: «manutenibile» farebbe scattare la regola
    dell'intercettazione, che cercherebbe una valvola sul refrigerante, sull'aria
    o su un cavo — e il catalogo non ne ha. Vale anche per la sonda, che pende
    dall'acqua ma si toglie dal suo pozzetto senza chiudere niente."""
    for voce in SIGLE:
        assert not catalogo().get(voce).has_trait(ComponentTrait.MAINTAINABLE), voce


def test_ogni_porta_fuori_dall_acqua_sta_nel_dominio_del_suo_fluido() -> None:
    for voce in SIGLE:
        for porta in catalogo().get(voce).ports:
            if porta.domain is Domain.HYDRONIC:
                continue
            assert DOMINIO_DEL_FLUIDO[porta.medium] is porta.domain, (voce, porta.id)


def test_la_sonda_pende_dall_acqua_e_manda_il_segnale_sul_bus() -> None:
    """La sonda e' l'unico pezzo con un piede nell'acqua e uno nel comando: pende
    dal tubo — o dal pozzetto dell'accumulo — e il segnale, facoltativo, esce sul
    bus. Una voce per fluido, come il termometro."""
    for voce, fluido in (
        ("temperature-probe", "heating_water"),
        ("temperature-probe-dhw", "domestic_hot_water"),
        ("temperature-probe-solar", "solar_fluid"),
    ):
        definizione = catalogo().get(voce)
        porte = {porta.id: porta for porta in definizione.ports}
        assert definizione.attachment is ComponentTrait.ATTACHMENT_BRANCH
        assert (porte["a"].domain, porte["a"].medium) == (Domain.HYDRONIC, fluido)
        assert (porte["signal"].domain, porte["signal"].medium) == (Domain.CONTROL, "control_bus")
        assert porte["signal"].required is False


def test_la_sonda_non_prende_il_posto_del_termometro() -> None:
    """La regola che vuole un termometro chiede «misura di temperatura»
    sull'acqua: la sonda fa un altro mestiere, e la risposta resta il termometro."""
    assert catalogo().providing("temperature_measurement", "heating_water").id == "thermometer"
    assert catalogo().providing("temperature_measurement", "solar_fluid").id == "thermometer-solar"


def test_il_regolatore_ha_alimentazione_bus_comandi_e_sonde() -> None:
    porte = {porta.id: porta for porta in catalogo().get("plant-controller").ports}
    assert porte["power"].medium == "power_supply" and porte["power"].required
    assert porte["bus"].medium == "control_bus"
    assert {porte[f"out_{i}"].medium for i in range(1, 5)} == {"power_supply"}
    assert {porte[f"probe_{i}"].medium for i in range(1, 4)} == {"control_bus"}
    assert [nome for nome, porta in porte.items() if porta.required] == ["power"]


def test_la_bocchetta_di_mandata_ha_il_nome_del_kit_in_legenda() -> None:
    """Il simbolo `air-diffuser` cambia nome, non segno (I-224)."""
    simbolo = SymbolRegistry.from_directory(SYMBOLS).get("air-diffuser").manifest
    assert simbolo.name == "Bocchetta di mandata con plenum di raccordo"
    assert simbolo.version == "1.0.0"
