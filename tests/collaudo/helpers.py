"""Attrezzi del collaudo indipendente della ripresa del 6 agosto 2026.

Scritti da zero dal collaudatore a contesto separato, non copiati dalle prove
esistenti. Adottati come regressione insieme alle correzioni dei difetti che
hanno trovato (C1, C3, C4 dell'appendice del piano)."""

from datetime import date
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graph.naming import Naming
from disegnatore_mep.graph.plant import PlantGraph, read_plant
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import (
    ComponentInstance,
    ConnectionModel,
    NetworkModel,
    PortRef,
    ProjectMetadata,
    ProjectModel,
)
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
CATALOG_DIR = ROOT / "examples" / "layout" / "catalog"
SYMBOLS_DIR = ROOT / "assets" / "symbols"
RULES_DIR = ROOT / "rules" / "hydronic"
NAMING_DIR = ROOT / "naming"
PROVE_DIR = ROOT / "examples" / "prova"


def symbols() -> SymbolRegistry:
    return SymbolRegistry.from_directory(SYMBOLS_DIR)


def catalog(directory: Path = CATALOG_DIR) -> ComponentRegistry:
    return ComponentRegistry.from_directory(directory, symbols=symbols())


def rules(directory: Path = RULES_DIR) -> RuleRegistry:
    return RuleRegistry.from_directory(directory)


def naming() -> Naming:
    return Naming.from_directory(NAMING_DIR)


def rules_map(registry: RuleRegistry) -> dict:
    return {item.id: item for item in registry.all()}


def load(name: str) -> ProjectModel:
    return load_project(PROVE_DIR / name)


def metadata() -> ProjectMetadata:
    return ProjectMetadata(
        project_id="collaudo",
        client="Collaudo",
        project_name="Collaudo indipendente",
        commission_code="COLL-01",
        revision="0",
        issue_date=date(2026, 8, 6),
    )


def project(
    networks: list[NetworkModel],
    components: list[ComponentInstance],
    connections: list[ConnectionModel],
) -> ProjectModel:
    return ProjectModel(
        metadata=metadata(),
        networks=networks,
        components=components,
        connections=connections,
    )


def net(nid: str, medium: str, name: str | None = None) -> NetworkModel:
    return NetworkModel(id=nid, name=name or nid, domain="hydronic", medium=medium)


def comp(cid: str, definition: str, tag: str | None = None) -> ComponentInstance:
    return ComponentInstance(id=cid, definition_id=definition, tag=tag)


def pipe(pid: str, nid: str, a: tuple[str, str], b: tuple[str, str]) -> ConnectionModel:
    return ConnectionModel(
        id=pid,
        network_id=nid,
        endpoint_a=PortRef(component_id=a[0], port_id=a[1]),
        endpoint_b=PortRef(component_id=b[0], port_id=b[1]),
    )


def graph_dump(graph: PlantGraph) -> dict:
    """Il dump completo del grafo, non le sole sigle: nodi coi bracci e le
    tubazioni di ciascun braccio, archi col verso, letture passo per passo."""
    return {
        "nodes": [
            {
                "id": node.component_id,
                "sigla": node.sigla,
                "family": node.family,
                "written": node.written_by_the_engineer,
                "arms": [
                    (arm.number, arm.port_id, arm.medium, arm.serves, tuple(arm.pipes))
                    for arm in node.arms
                ],
                "media": node.media,
                "stored": node.stored_medium,
            }
            for node in graph.nodes
        ],
        "pipes": sorted(
            (
                p.connection_id,
                p.network_id,
                p.medium,
                (p.leaves.component_id, p.leaves.port_id),
                (p.enters.component_id, p.enters.port_id),
            )
            for p in graph.pipes
        ),
        "readings": [
            {
                "start": r.start,
                "medium": r.medium,
                "kind": r.kind,
                "steps": [
                    (
                        s.number,
                        s.departs_from,
                        s.departs_arm,
                        s.arrives_at,
                        s.arrives_arm,
                        s.connection_id,
                        s.medium,
                        s.closes_the_ring,
                        s.rejoins,
                        s.onward_arms,
                    )
                    for s in r.steps
                ],
            }
            for r in graph.readings
        ],
        "unreached": graph.unreached,
        "unread": graph.unread_pipes,
    }


def read(model: ProjectModel, cat: ComponentRegistry) -> PlantGraph:
    return read_plant(model, cat, naming())


def permuted(model: ProjectModel, seed: int) -> ProjectModel:
    """Lo stesso impianto scritto in un altro ordine: tubazioni, pezzi e reti."""
    import random

    rng = random.Random(seed)
    connections = list(model.connections)
    components = list(model.components)
    networks = list(model.networks)
    rng.shuffle(connections)
    rng.shuffle(components)
    rng.shuffle(networks)
    return model.model_copy(
        update={
            "connections": connections,
            "components": components,
            "networks": networks,
        }
    )
