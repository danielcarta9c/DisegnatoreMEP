from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent
CATALOG = ROOT / "catalog"


def port(
    port_id: str,
    domain: str,
    medium: str,
    flow: str,
) -> dict[str, Any]:
    return {
        "id": port_id,
        "domain": domain,
        "medium": medium,
        "flow": flow,
        "required": True,
        "max_connections": 1,
    }


def definition(
    component_id: str,
    name: str,
    functions: list[str],
    ports: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "id": component_id,
        "version": "1.0.0",
        "name": name,
        "functions": functions,
        "symbol_id": component_id,
        "composite": len(functions) > 1,
        "ports": ports,
        "sources": ["CONV-FOUNDATION"],
    }


DEFINITIONS = [
    definition("boundary-gas-source", "Confine gas", ["boundary"], [port("out", "gas", "natural_gas", "out")]),
    definition(
        "gas-boiler",
        "Caldaia gas",
        ["heat_generation", "gas_combustion"],
        [
            port("gas_in", "gas", "natural_gas", "in"),
            port("water_return", "hydronic", "heating_water", "in"),
            port("water_supply", "hydronic", "heating_water", "out"),
        ],
    ),
    definition("boundary-hydronic-return", "Confine ritorno", ["boundary"], [port("out", "hydronic", "heating_water", "out")]),
    definition("boundary-hydronic-supply", "Confine mandata", ["boundary"], [port("in", "hydronic", "heating_water", "in")]),
    definition("supply-fan", "Ventilatore", ["air_movement"], [port("out", "aeraulic", "supply_air", "out")]),
    definition("air-terminal", "Terminale aria", ["air_terminal"], [port("in", "aeraulic", "supply_air", "in")]),
    definition(
        "vrv-outdoor",
        "Unità esterna VRV",
        ["refrigerant_generation"],
        [
            port("liquid_out", "refrigerant", "refrigerant_liquid", "out"),
            port("gas_in", "refrigerant", "refrigerant_gas", "in"),
        ],
    ),
    definition(
        "vrv-indoor",
        "Unità interna VRV",
        ["direct_expansion_terminal"],
        [
            port("liquid_in", "refrigerant", "refrigerant_liquid", "in"),
            port("gas_out", "refrigerant", "refrigerant_gas", "out"),
        ],
    ),
]

COMPONENTS = [
    {"id": "gas-source", "definition_id": "boundary-gas-source", "tag": None, "properties": {}},
    {"id": "boiler", "definition_id": "gas-boiler", "tag": "CAL-01", "properties": {}},
    {"id": "return-boundary", "definition_id": "boundary-hydronic-return", "tag": None, "properties": {}},
    {"id": "supply-boundary", "definition_id": "boundary-hydronic-supply", "tag": None, "properties": {}},
    {"id": "fan", "definition_id": "supply-fan", "tag": "VEN-01", "properties": {}},
    {"id": "terminal", "definition_id": "air-terminal", "tag": "TER-01", "properties": {}},
    {"id": "vrv-outdoor", "definition_id": "vrv-outdoor", "tag": "UE-01", "properties": {}},
    {"id": "vrv-indoor", "definition_id": "vrv-indoor", "tag": "UI-01", "properties": {}},
]

NETWORKS = [
    {"id": "gas", "name": "Gas", "domain": "gas", "medium": "natural_gas"},
    {"id": "heating", "name": "Riscaldamento", "domain": "hydronic", "medium": "heating_water"},
    {"id": "supply-air", "name": "Aria mandata", "domain": "aeraulic", "medium": "supply_air"},
    {"id": "vrv-liquid", "name": "VRV liquido", "domain": "refrigerant", "medium": "refrigerant_liquid"},
    {"id": "vrv-gas", "name": "VRV gas", "domain": "refrigerant", "medium": "refrigerant_gas"},
]

CONNECTIONS = [
    {"id": "gas-1", "network_id": "gas", "endpoint_a": {"component_id": "gas-source", "port_id": "out"}, "endpoint_b": {"component_id": "boiler", "port_id": "gas_in"}, "properties": {}},
    {"id": "heat-return", "network_id": "heating", "endpoint_a": {"component_id": "return-boundary", "port_id": "out"}, "endpoint_b": {"component_id": "boiler", "port_id": "water_return"}, "properties": {}},
    {"id": "heat-supply", "network_id": "heating", "endpoint_a": {"component_id": "boiler", "port_id": "water_supply"}, "endpoint_b": {"component_id": "supply-boundary", "port_id": "in"}, "properties": {}},
    {"id": "air-1", "network_id": "supply-air", "endpoint_a": {"component_id": "fan", "port_id": "out"}, "endpoint_b": {"component_id": "terminal", "port_id": "in"}, "properties": {}},
    {"id": "vrv-liquid-1", "network_id": "vrv-liquid", "endpoint_a": {"component_id": "vrv-outdoor", "port_id": "liquid_out"}, "endpoint_b": {"component_id": "vrv-indoor", "port_id": "liquid_in"}, "properties": {}},
    {"id": "vrv-gas-1", "network_id": "vrv-gas", "endpoint_a": {"component_id": "vrv-indoor", "port_id": "gas_out"}, "endpoint_b": {"component_id": "vrv-outdoor", "port_id": "gas_in"}, "properties": {}},
]


def project(connections: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "metadata": {
            "project_id": "foundation-mixed",
            "client": "Nove C",
            "project_name": "Foundation mixed-domain fixture",
            "commission_code": "DEV-001",
            "revision": "00",
            "issue_date": "2026-08-01",
        },
        "networks": NETWORKS,
        "components": COMPONENTS,
        "connections": connections,
        "assumptions": [],
        "rule_applications": [],
        "sheets": [],
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    CATALOG.mkdir(parents=True, exist_ok=True)
    for item in DEFINITIONS:
        write_json(CATALOG / f"{item['id']}.json", item)
    write_json(ROOT / "valid-mixed-project.json", project(CONNECTIONS))
    invalid_networks = [dict(item) for item in NETWORKS]
    invalid_networks[2] = dict(invalid_networks[2], medium="return_air")
    invalid_project = project(CONNECTIONS)
    invalid_project["networks"] = invalid_networks
    write_json(ROOT / "invalid-cross-medium.json", invalid_project)


if __name__ == "__main__":
    main()
