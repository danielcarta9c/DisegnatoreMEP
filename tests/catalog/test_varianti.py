"""Le varianti del catalogo si scelgono per un dato che non e' il nome (D-187).

La pompa di calore di alta potenza, la caldaia modulare e il ventilconvettore
canalizzato fanno quello che fa il loro fratello e hanno gli stessi attacchi.
Chi legge il testo dell'ingegnere — «Capire» — sceglie per mestiere e per
attacchi, mai per somiglianza di nome: fra due voci cosi' non avrebbe niente con
cui decidere. Il PO ha deciso come si decide: **la variante si sceglie solo
quando il testo la nomina**, con le sue parole, e mai per potenza. Queste prove
tengono su il dato che lo rende possibile, e i due fatti che D-187 aggiunge:
il circolatore a bordo e il circuito solare con i suoi pezzi.
"""

import copy
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import CatalogError, ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition
from disegnatore_mep.graphics.registry import SymbolRegistry

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"

VARIANTI = {
    # voce: (voce base, le parole del PO)
    "heat-pump-air-water-large": ("heat-pump-air-water", {"alta potenza", "grande taglia"}),
    "gas-boiler-modular": ("gas-boiler", {"modulare", "a moduli"}),
    "fan-coil-ducted": ("fan-coil", {"canalizzato", "canalizzabile"}),
}


@pytest.fixture(scope="module")
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def _porte(definition: ComponentDefinition) -> set[tuple[str, str, str, str]]:
    return {(p.id, p.domain.value, p.medium, p.flow.value) for p in definition.ports}


@pytest.mark.parametrize("voce", sorted(VARIANTI))
def test_la_variante_e_la_stessa_macchina_con_un_altro_simbolo(
    catalogo: ComponentRegistry, voce: str
) -> None:
    base_id, parole = VARIANTI[voce]
    variante, base = catalogo.get(voce), catalogo.get(base_id)
    assert variante.variant is not None and variante.variant.of == base_id
    assert set(variante.variant.named_as) == parole
    # Mestieri e attacchi non le distinguono: e' per questo che serve il dato.
    assert set(variante.functions) == set(base.functions)
    assert _porte(variante) == _porte(base)
    assert variante.symbol_id != base.symbol_id
    # La voce base e' quella che si sceglie quando il testo non dice niente.
    assert base.variant is None


def test_le_varianti_sono_tutte_e_sole_quelle_di_d187(catalogo: ComponentRegistry) -> None:
    dichiarate = {item.id for item in catalogo.all() if item.variant is not None}
    assert dichiarate == set(VARIANTI)


@pytest.mark.parametrize("voce", ["heat-pump-air-water-large", "gas-boiler-modular"])
def test_la_macchina_grande_porta_il_circolatore_a_bordo(
    catalogo: ComponentRegistry, voce: str
) -> None:
    """D-187: la pompa di calore grande come la domestica, e la caldaia modulare
    per correzione del PO — «anche loro le danno sempre con circolatore
    integrato». La caldaia murale, che e' la sua voce base, non dichiara niente."""
    assert "circulation" in catalogo.get(voce).carries_on_board
    assert "circulation" not in catalogo.get("gas-boiler").carries_on_board


def test_il_bollitore_a_due_serpentini_si_sceglie_dagli_attacchi(
    catalogo: ComponentRegistry,
) -> None:
    """Non e' una variante: e' l'unico accumulo sanitario con gli attacchi del
    serpentino solare, ed e' da quelli che «Capire» lo sceglie."""
    con_il_solare = [
        item.id
        for item in catalogo.all()
        if "dhw_storage" in item.functions
        and any(port.medium == "solar_fluid" for port in item.ports)
    ]
    assert con_il_solare == ["dhw-cylinder-twin-coil"]
    assert catalogo.get("dhw-cylinder-twin-coil").variant is None


def test_il_collettore_e_un_generatore_sul_fluido_solare(catalogo: ComponentRegistry) -> None:
    collettore = catalogo.get("solar-collector")
    assert collettore.functions == ["heat_generation"]
    assert {port.medium for port in collettore.ports} == {"solar_fluid"}


@pytest.mark.parametrize(
    "mestiere",
    [
        "circulation",
        "non_return",
        "isolation",
        "safety",
        "expansion",
        "pressure_measurement",
        "temperature_measurement",
        "air_release",
        "drain",
        "junction",
        "branch_off",
    ],
)
def test_il_gruppo_solare_ha_i_suoi_pezzi(catalogo: ComponentRegistry, mestiere: str) -> None:
    """Il gruppo di circolazione solare lo descrive il progettista e «Capire» lo
    trascrive con i pezzi della libreria (D-184, D-187): per ogni pezzo serve una
    voce i cui attacchi portino il fluido solare, come per l'acqua sanitaria."""
    assert any(
        mestiere in item.functions
        and all(port.medium == "solar_fluid" for port in item.ports)
        for item in catalogo.all()
    ), mestiere


# --- il registro rifiuta una variante che non e' la stessa macchina ----------


def _voci(catalogo: ComponentRegistry) -> dict[str, ComponentDefinition]:
    return {item.id: item for item in catalogo.all()}


def _con(voci: dict[str, ComponentDefinition], voce: str, **campi: object) -> list[ComponentDefinition]:
    cambiata = voci[voce].model_copy(update=campi)
    return [cambiata if item.id == voce else item for item in voci.values()]


def test_una_variante_di_una_voce_che_non_ce_si_rifiuta(catalogo: ComponentRegistry) -> None:
    voci = _voci(catalogo)
    variante = voci["fan-coil-ducted"].variant
    assert variante is not None
    storta = variante.model_copy(update={"of": "fan-coil-che-non-esiste"})
    with pytest.raises(CatalogError, match="non e' nel catalogo"):
        ComponentRegistry(_con(voci, "fan-coil-ducted", variant=storta))


def test_una_variante_con_altri_attacchi_si_rifiuta(catalogo: ComponentRegistry) -> None:
    voci = _voci(catalogo)
    porte = copy.deepcopy(voci["fan-coil-ducted"].ports)
    porte[0] = porte[0].model_copy(update={"medium": "chilled_water"})
    with pytest.raises(CatalogError, match="non ha gli stessi attacchi"):
        ComponentRegistry(_con(voci, "fan-coil-ducted", ports=porte))


def test_una_variante_con_altri_mestieri_si_rifiuta(catalogo: ComponentRegistry) -> None:
    voci = _voci(catalogo)
    with pytest.raises(CatalogError, match="non fa gli stessi mestieri"):
        ComponentRegistry(_con(voci, "fan-coil-ducted", functions=["emission", "air_movement"]))


def test_una_variante_con_lo_stesso_simbolo_si_rifiuta(catalogo: ComponentRegistry) -> None:
    voci = _voci(catalogo)
    with pytest.raises(CatalogError, match="con lo stesso simbolo"):
        ComponentRegistry(_con(voci, "fan-coil-ducted", symbol_id="fan-coil"))


def test_la_variante_di_una_variante_si_rifiuta(catalogo: ComponentRegistry) -> None:
    voci = _voci(catalogo)
    base = voci["fan-coil-ducted"].variant
    assert base is not None
    a_cascata = voci["fan-coil"].model_copy(
        update={"variant": base.model_copy(update={"of": "radiator"})}
    )
    elenco = [a_cascata if item.id == "fan-coil" else item for item in voci.values()]
    with pytest.raises(CatalogError, match="a sua volta una variante"):
        ComponentRegistry(elenco)
