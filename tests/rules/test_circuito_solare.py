"""Sul circuito solare le regole non aggiungono niente (D-187, punto 3).

Il PO, 26 settembre 2026: il gruppo di circolazione solare lo descrive il
progettista e lo trascrive chi legge il testo; le regole non ci mettono niente,
e in particolare nessun gruppo di riempimento dall'acquedotto — il circuito si
riempie di fluido antigelo. Il motore lo fa valere nel punto in cui decide di
quali reti una regola parla, e queste prove lo tengono su da due lati: sulla rete
solare non nasce niente, sulla rete di riscaldamento dello stesso impianto le
regole lavorano come prima — anche sul bollitore a due serpentini, che sta su
tutt'e due.
"""

from datetime import date
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.model.project import (
    ComponentInstance,
    ConnectionModel,
    NetworkModel,
    PortRef,
    ProjectMetadata,
    ProjectModel,
)
from disegnatore_mep.model.types import PlantRegime
from disegnatore_mep.rules import engine
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"


def _pipe(pipe_id: str, network_id: str, a: tuple[str, str], b: tuple[str, str]) -> ConnectionModel:
    return ConnectionModel(
        id=pipe_id,
        network_id=network_id,
        endpoint_a=PortRef(component_id=a[0], port_id=a[1]),
        endpoint_b=PortRef(component_id=b[0], port_id=b[1]),
    )


def impianto() -> ProjectModel:
    """Una caldaia modulare sul serpentino alto del bollitore, il collettore
    solare su quello basso, con il circolatore del solare: il minimo che mette
    un pezzo su due reti, una delle quali e' solare."""
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-solare",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 26),
        ),
        plant_regime=PlantRegime.OVER_35_KW,
        networks=[
            NetworkModel(id="riscaldamento", name="riscaldamento", domain="hydronic", medium="heating_water"),
            NetworkModel(id="solare", name="solare", domain="hydronic", medium="solar_fluid"),
        ],
        components=[
            ComponentInstance(id="caldaia", definition_id="gas-boiler-modular"),
            ComponentInstance(id="bollitore", definition_id="dhw-cylinder-twin-coil"),
            ComponentInstance(id="collettore", definition_id="solar-collector"),
            ComponentInstance(id="pompa-solare", definition_id="pump-circulator-solar"),
        ],
        connections=[
            _pipe("r1", "riscaldamento", ("caldaia", "water_supply"), ("bollitore", "coil_in")),
            _pipe("r2", "riscaldamento", ("bollitore", "coil_out"), ("caldaia", "water_return")),
            _pipe("s1", "solare", ("collettore", "supply"), ("bollitore", "solar_coil_in")),
            _pipe("s2", "solare", ("bollitore", "solar_coil_out"), ("pompa-solare", "a")),
            _pipe("s3", "solare", ("pompa-solare", "b"), ("collettore", "return")),
        ],
    )


@pytest.fixture(scope="module")
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


@pytest.fixture(scope="module")
def regole(catalogo: ComponentRegistry) -> RuleRegistry:
    registry = RuleRegistry.from_directory(RULES)
    registry.cross_check(catalogo)
    return registry


def test_sulla_rete_solare_non_nasce_niente(
    catalogo: ComponentRegistry, regole: RuleRegistry
) -> None:
    esito = engine.evaluate(impianto(), catalogo, regole)
    sul_solare = [item.rule_id for item in esito.proposals if item.network_id == "solare"]
    assert sul_solare == []
    # Neanche un punto aperto: il catalogo non ha, per esempio, un filtro sul
    # fluido solare, e senza l'esclusione la regola lo segnalerebbe come pezzo
    # che manca. Sul solare non manca niente, perche' niente si aggiunge.
    assert [item for item in esito.gaps if item.network_id == "solare"] == []


def test_sulla_rete_di_riscaldamento_le_regole_lavorano_come_prima(
    catalogo: ComponentRegistry, regole: RuleRegistry
) -> None:
    """Il bollitore sta su tutt'e due le reti: il serpentino di integrazione
    riceve le sue intercettazioni, quello solare no."""
    esito = engine.evaluate(impianto(), catalogo, regole)
    sul_riscaldamento = [item for item in esito.proposals if item.network_id == "riscaldamento"]
    assert sul_riscaldamento, "le regole devono ancora lavorare sul riscaldamento"
    attacchi_del_bollitore = {
        item.anchor.port_id for item in sul_riscaldamento if item.anchor.component_id == "bollitore"
    }
    assert attacchi_del_bollitore <= {"coil_in", "coil_out"}
    assert attacchi_del_bollitore, "il serpentino di integrazione si intercetta come sempre"


def test_e_l_esclusione_a_tenere_fuori_il_solare(
    catalogo: ComponentRegistry, regole: RuleRegistry, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Senza l'esclusione le regole che non guardano il fluido — intercettare
    cio' che si manutiene, il termometro sull'uscita del generatore sopra i 35
    kW, il separatore d'aria... — porterebbero pezzi sul circuito solare. E'
    quello che D-187 vieta, e la ragione per cui l'esclusione esiste."""
    monkeypatch.setattr(engine, "MEDIA_WITHOUT_ACCESSORIES", frozenset())
    esito = engine.evaluate(impianto(), catalogo, regole)
    sul_solare = {item.rule_id for item in esito.proposals if item.network_id == "solare"}
    sul_solare |= {item.rule_id for item in esito.gaps if item.network_id == "solare"}
    assert sul_solare, "senza l'esclusione qualche regola parlerebbe della rete solare"
