"""Le porte di comando non si attraversano (REL-026 A-3, I-300).

Il difetto, trovato su una commessa: una pompa di calore con l'alimentazione (`power`) e una
sola uscita di comando collegata (`out_acs`) restava **senza portata sul primario**. Il
catalogo del progetto (`ComponentRegistry.per_il_progetto`) mette da parte le porte di comando
che il grafo non collega; con le due collegate la pompa di calore ha, sul fluido
`power_supply`, un'entrata e un'uscita sole, e il calcolo le contava come una seconda coppia
attraversata. Con due coppie non sa piu' da quale leggere la portata della macchina, e la
lascia senza.

Lo stesso col ventilconvettore canalizzato col lato aria, che ha un consenso in entrata e uno
in uscita sul bus.
"""

from datetime import date
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.diametri.calcolatore import portata_da_potenza
from disegnatore_mep.diametri.portate import portate_delle_tratte
from disegnatore_mep.layout.autostrade import tratte_del_progetto
from disegnatore_mep.model.project import (
    ComponentInstance,
    ConnectionModel,
    NetworkModel,
    PortRef,
    ProjectMetadata,
    ProjectModel,
    SubsystemModel,
)
from disegnatore_mep.model.types import PlantRegime

ROOT = Path(__file__).resolve().parents[2]


def _impianto(pezzi: dict[str, tuple[str, dict[str, object]]], tubi: list[tuple[str, str, str, str, str]]) -> ProjectModel:
    reti = {
        "primario": ("hydronic", "heating_water"),
        "linea": ("control", "power_supply"),
        "bus": ("control", "control_bus"),
    }
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-comando",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 11, 13),
        ),
        plant_regime=PlantRegime.UP_TO_35_KW,
        networks=[NetworkModel(id=k, name=k, domain=d, medium=m) for k, (d, m) in reti.items()],
        components=[
            ComponentInstance(id=item, definition_id=voce, properties=proprieta)  # type: ignore[arg-type]
            for item, (voce, proprieta) in pezzi.items()
        ],
        connections=[
            ConnectionModel(
                id=cid,
                network_id=rete,
                endpoint_a=PortRef(component_id=a.split(".")[0], port_id=a.split(".")[1]),
                endpoint_b=PortRef(component_id=b.split(".")[0], port_id=b.split(".")[1]),
            )
            for cid, rete, a, b, _ in tubi
        ],
        subsystems=[SubsystemModel(id="tutto", name="tutto", component_ids=list(pezzi), network_ids=list(reti))],
    )


def _portata_del_primario(modello: ProjectModel, catalogo: ComponentRegistry) -> tuple[float | None, set[str]]:
    del_progetto = catalogo.per_il_progetto(modello)
    tratte = tratte_del_progetto(modello, del_progetto)
    portate = portate_delle_tratte(modello, del_progetto, tratte)
    mandata = next(item for item in portate.tratte.values() if "m1" in item.chiave)
    return mandata.portata_m3h, set(portate.dati)


ACQUA = [
    ("m1", "primario", "pdc.water_supply", "pompa.a", ""),
    ("m2", "primario", "pompa.b", "fc.in", ""),
    ("r1", "primario", "fc.out", "pdc.water_return", ""),
]


def test_la_pompa_di_calore_con_l_uscita_acs_collegata_ha_la_portata_sul_primario(
    catalogo: ComponentRegistry,
) -> None:
    modello = _impianto(
        {
            "pdc": ("heat-pump-air-water", {"power_kw": 8, "delta_t_k": 5}),
            "pompa": ("pump-circulator", {}),
            "fc": ("fan-coil-ducted-air", {}),
            "quadro": ("electrical-panel", {}),
        },
        [
            *ACQUA,
            ("e1", "linea", "quadro.out_1", "pdc.power", ""),
            # L'uscita di comando dell'ACS: l'unica collegata, e il difetto.
            ("e2", "linea", "pdc.out_acs", "pompa.comando", ""),
        ],
    )
    portata, con_un_dato = _portata_del_primario(modello, catalogo)
    assert "pdc" in con_un_dato
    assert portata == pytest.approx(portata_da_potenza(8, 5))


def test_il_ventilconvettore_col_consenso_in_entrata_e_in_uscita_da_la_sua_portata(
    catalogo: ComponentRegistry,
) -> None:
    modello = _impianto(
        {
            "pdc": ("heat-pump-air-water", {}),
            "pompa": ("pump-circulator", {}),
            "fc": ("fan-coil-ducted-air", {"power_kw": 4, "delta_t_k": 5}),
            "tz": ("room-thermostat", {}),
        },
        [
            *ACQUA,
            ("b1", "bus", "tz.a", "fc.consenso_in", ""),
            ("b2", "bus", "fc.consenso", "pdc.termostato", ""),
        ],
    )
    portata, con_un_dato = _portata_del_primario(modello, catalogo)
    assert "fc" in con_un_dato
    assert portata == pytest.approx(portata_da_potenza(4, 5))
