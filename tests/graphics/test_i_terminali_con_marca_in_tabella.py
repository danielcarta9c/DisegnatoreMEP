"""I terminali con marca o modello entrano nella tabella delle apparecchiature (REL-026 A-4).

Da una commessa (I-300): il ventilconvettore con marca e modello dati dal progettista non
compariva in tabella, perche' i terminali ne restavano fuori sempre (I-141). Adesso entra,
con potenza e portata; un terminale senza marca ne' modello resta fuori come prima.
"""

from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph.naming import Naming
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.tabella import dati_idronici, entra_in_tabella, righe_della_tabella
from disegnatore_mep.model.project import ProjectModel

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog", symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols")
    )


@pytest.mark.parametrize(
    ("proprieta", "entra"),
    [
        ({}, False),
        ({"power_kw": 3.5}, False),
        ({"marca": "Marca di prova"}, True),
        ({"modello": "PRV-FC-35"}, True),
        ({"marca": "  "}, False),
    ],
)
def test_un_terminale_entra_solo_con_marca_o_modello(proprieta: dict[str, object], entra: bool) -> None:
    assert entra_in_tabella(("emission",), proprieta) is entra  # type: ignore[arg-type]


def test_il_terminale_porta_potenza_e_portata() -> None:
    assert dati_idronici(("emission",), {"power_kw": 3.5, "flow_rate_m3h": 0.6, "delta_t_k": 5}) == [
        "3,5 kW",
        "0,6 m³/h",
    ]


def test_nella_tabella_il_ventilconvettore_con_marca_c_e_e_il_radiatore_senza_no(catalogo: ComponentRegistry) -> None:
    modello = ProjectModel.model_validate(
        {
            "schema_version": "1.1.0",
            "metadata": {
                "project_id": "prova-tabella",
                "client": "prova",
                "project_name": "prova",
                "commission_code": "PROVA",
                "revision": "00",
                "issue_date": "2026-11-13",
            },
            "plant_regime": "up_to_35_kw",
            "networks": [],
            "components": [
                {"id": "fc", "definition_id": "fan-coil-ducted-air",
                 "properties": {"marca": "Marca di prova", "modello": "PRV-FC-35", "power_kw": 3.5}},
                {"id": "rad", "definition_id": "radiator", "properties": {"power_kw": 1.2}},
                {"id": "fc2", "definition_id": "fan-coil", "properties": {"power_kw": 2}},
            ],
            "connections": [],
        }
    )
    righe = righe_della_tabella(
        modello,
        catalogo,
        Naming.from_directory(ROOT / "naming"),
        {"fc": "TE-01", "rad": "TE-02", "fc2": "TE-03"},
        sul_foglio=("fc", "rad", "fc2"),
    )
    assert [(r.codice, r.descrizione, r.caratteristiche, r.marca, r.modello) for r in righe] == [
        ("TE-01", "Ventilconvettore canalizzato", "3,5 kW", "Marca di prova", "PRV-FC-35")
    ]
