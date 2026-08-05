from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from disegnatore_mep.graphics.standard import A3_LANDSCAPE
from disegnatore_mep.graphics.symbol import SymbolManifest
from disegnatore_mep.model.project import SCHEMA_VERSION

ROOT = Path(__file__).parent
CATALOG = ROOT / "catalog"
SYMBOLS_DIR = ROOT / "symbols"


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


MAINTAINABLE = "maintainable"
NEEDS_DEBRIS_PROTECTION = "needs_debris_protection"
OUTGASSES = "outgasses"
NEEDS_RELIEF = "needs_relief"
SHUTOFF_ORDINARY = "shutoff_ordinary"
INLINE = "attachment_inline"

ORDINARY_INLINE = [SHUTOFF_ORDINARY, INLINE]
"""Le due dichiarazioni che nessun componente puo' tacere, nel caso ordinario:
lo isola una valvola comune e sta sul percorso del tubo. Non sono un default —
un componente che non le scrive non si carica affatto (P1)."""


def definition(
    component_id: str,
    name: str,
    functions: list[str],
    traits: list[str],
    ports: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "id": component_id,
        "version": "1.0.0",
        "name": name,
        "functions": functions,
        "traits": traits,
        "symbol_id": component_id,
        "composite": len(functions) > 1,
        "ports": ports,
        "sources": ["CONV-FOUNDATION"],
    }


DEFINITIONS = [
    definition("boundary-gas-source", "Confine gas", ["boundary"], ORDINARY_INLINE, [port("out", "gas", "natural_gas", "out")]),
    definition(
        "gas-boiler",
        "Caldaia gas",
        ["heat_generation", "gas_combustion"],
        [
            MAINTAINABLE,
            NEEDS_DEBRIS_PROTECTION,
            OUTGASSES,
            NEEDS_RELIEF,
            *ORDINARY_INLINE,
        ],
        [
            port("gas_in", "gas", "natural_gas", "in"),
            port("water_return", "hydronic", "heating_water", "in"),
            port("water_supply", "hydronic", "heating_water", "out"),
        ],
    ),
    definition("boundary-hydronic-return", "Confine ritorno", ["boundary"], ORDINARY_INLINE, [port("out", "hydronic", "heating_water", "out")]),
    definition("boundary-hydronic-supply", "Confine mandata", ["boundary"], ORDINARY_INLINE, [port("in", "hydronic", "heating_water", "in")]),
    definition("supply-fan", "Ventilatore", ["air_movement"], ORDINARY_INLINE, [port("out", "aeraulic", "supply_air", "out")]),
    definition("air-terminal", "Terminale aria", ["air_terminal"], ORDINARY_INLINE, [port("in", "aeraulic", "supply_air", "in")]),
    definition(
        "vrv-outdoor",
        "Unità esterna VRV",
        ["refrigerant_generation"],
        ORDINARY_INLINE,
        [
            port("liquid_out", "refrigerant", "refrigerant_liquid", "out"),
            port("gas_in", "refrigerant", "refrigerant_gas", "in"),
        ],
    ),
    definition(
        "vrv-indoor",
        "Unità interna VRV",
        ["direct_expansion_terminal"],
        ORDINARY_INLINE,
        [
            port("liquid_in", "refrigerant", "refrigerant_liquid", "in"),
            port("gas_out", "refrigerant", "refrigerant_gas", "out"),
        ],
    ),
]

# ---------------------------------------------------------------------------
# Simboli delle otto definizioni di fixture. Vivono in examples/foundation/symbols,
# non in assets/symbols: quella e' la libreria pubblicata dei dodici simboli del
# Task 6 e resta priva di artefatti di prova (P-2, progress.md). Queste otto forme
# esistono solo per far caricare il catalogo di fondazione insieme a un registro
# di simboli reale ed esercitare la verifica incrociata di ComponentRegistry (vedi
# tests/acceptance/test_foundation_cli.py); non sono pensate per essere disegnate
# in un progetto vero. Stesso spirito generativo di examples/graphics/build_symbols.py
# - dizionario di manifesto validato prima di scrivere, corpo SVG come frammento
# senza radice <svg> - ma proprieta' e ciclo di vita separati: le due librerie non
# condividono generatore.
# ---------------------------------------------------------------------------

SYMBOL_ROTATIONS_DEG = [0, 90, 180, 270]
SYMBOL_CLEARANCE_MM = A3_LANDSCAPE.min_clearance_mm
SYMBOL_SOURCE = "CONV-FOUNDATION"

_DEFINITION_NAMES = {item["id"]: item["name"] for item in DEFINITIONS}


def symbol_port(port_id: str, face: str, x_mm: float, y_mm: float) -> dict[str, Any]:
    return {"id": port_id, "face": face, "x_mm": x_mm, "y_mm": y_mm}


def symbol_keep_out(ports: list[dict[str, Any]]) -> dict[str, float]:
    """Area di rispetto sui lati che portano una porta, derivata dalle porte.

    Non da un elenco parallelo di nomi di lato passato da chi chiama: quello
    accettava in silenzio un refuso come "rigth" e spediva un simbolo con area
    di rispetto nulla.
    """
    faces = {item["face"] for item in ports}
    return {
        f"{side}_mm": SYMBOL_CLEARANCE_MM if side in faces else 0.0
        for side in ("left", "right", "top", "bottom")
    }


def symbol(
    symbol_id: str,
    width_mm: float,
    height_mm: float,
    ports: list[dict[str, Any]],
    body: str,
) -> tuple[dict[str, Any], str]:
    manifest: dict[str, Any] = {
        "id": symbol_id,
        "version": "1.0.0",
        "name": _DEFINITION_NAMES[symbol_id],
        "width_mm": width_mm,
        "height_mm": height_mm,
        "allowed_rotations_deg": SYMBOL_ROTATIONS_DEG,
        "ports": ports,
        "keep_out": symbol_keep_out(ports),
        "source": SYMBOL_SOURCE,
    }
    return manifest, body


SYMBOLS: list[tuple[dict[str, Any], str]] = [
    symbol(
        "boundary-gas-source",
        5.0,
        5.0,
        [symbol_port("out", "right", 5.0, 2.5)],
        '<circle cx="2.5" cy="2.5" r="1.6"/><line x1="4.1" y1="2.5" x2="5" y2="2.5"/>',
    ),
    symbol(
        "boundary-hydronic-return",
        5.0,
        5.0,
        [symbol_port("out", "right", 5.0, 2.5)],
        '<rect x="0.8" y="0.8" width="3.4" height="3.4"/><line x1="4.2" y1="2.5" x2="5" y2="2.5"/>',
    ),
    symbol(
        "boundary-hydronic-supply",
        5.0,
        5.0,
        [symbol_port("in", "left", 0.0, 2.5)],
        '<rect x="0.8" y="0.8" width="3.4" height="3.4"/><line x1="0" y1="2.5" x2="0.8" y2="2.5"/>',
    ),
    symbol(
        "gas-boiler",
        15.0,
        10.0,
        [
            symbol_port("gas_in", "bottom", 5.0, 10.0),
            symbol_port("water_return", "bottom", 10.0, 10.0),
            symbol_port("water_supply", "top", 7.5, 0.0),
        ],
        '<rect x="1" y="1" width="13" height="8"/>'
        '<line x1="5" y1="9" x2="5" y2="10"/>'
        '<line x1="10" y1="9" x2="10" y2="10"/>'
        '<line x1="7.5" y1="1" x2="7.5" y2="0"/>',
    ),
    symbol(
        "supply-fan",
        10.0,
        10.0,
        [symbol_port("out", "right", 10.0, 5.0)],
        '<circle cx="5" cy="5" r="3"/><line x1="8" y1="5" x2="10" y2="5"/>',
    ),
    symbol(
        "air-terminal",
        10.0,
        10.0,
        [symbol_port("in", "left", 0.0, 5.0)],
        '<rect x="2" y="1.5" width="7" height="7"/><line x1="0" y1="5" x2="2" y2="5"/>',
    ),
    symbol(
        "vrv-outdoor",
        10.0,
        10.0,
        [
            symbol_port("liquid_out", "right", 10.0, 2.5),
            symbol_port("gas_in", "right", 10.0, 7.5),
        ],
        '<rect x="1" y="1" width="8" height="8"/>'
        '<line x1="9" y1="2.5" x2="10" y2="2.5"/>'
        '<line x1="9" y1="7.5" x2="10" y2="7.5"/>',
    ),
    symbol(
        "vrv-indoor",
        10.0,
        10.0,
        [
            symbol_port("liquid_in", "left", 0.0, 2.5),
            symbol_port("gas_out", "left", 0.0, 7.5),
        ],
        '<rect x="1" y="1" width="8" height="8"/>'
        '<line x1="0" y1="2.5" x2="1" y2="2.5"/>'
        '<line x1="0" y1="7.5" x2="1" y2="7.5"/>',
    ),
]


def write_symbol(directory: Path, manifest: dict[str, Any], body: str) -> None:
    SymbolManifest.model_validate(manifest)  # fail fast, before anything is written
    write_json(directory / f"{manifest['id']}.json", manifest)
    (directory / f"{manifest['id']}.svg").write_text(body + "\n", encoding="utf-8")


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
        # Scritta nativamente alla versione corrente: un file che dichiarasse
        # ancora 1.0.0 verrebbe migrato al caricamento e mentirebbe sul disco.
        "schema_version": SCHEMA_VERSION,
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
    SYMBOLS_DIR.mkdir(parents=True, exist_ok=True)
    for item in DEFINITIONS:
        write_json(CATALOG / f"{item['id']}.json", item)
    for manifest, body in SYMBOLS:
        write_symbol(SYMBOLS_DIR, manifest, body)
    write_json(ROOT / "valid-mixed-project.json", project(CONNECTIONS))
    invalid_networks = [dict(item) for item in NETWORKS]
    invalid_networks[2] = dict(invalid_networks[2], medium="return_air")
    invalid_project = project(CONNECTIONS)
    invalid_project["networks"] = invalid_networks
    write_json(ROOT / "invalid-cross-medium.json", invalid_project)


if __name__ == "__main__":
    main()
