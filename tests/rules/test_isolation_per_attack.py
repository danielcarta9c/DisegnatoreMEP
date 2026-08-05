"""WP2 — una valvola di intercettazione per ogni attacco di macchina (D-074).

Il collaudo automatico del pacchetto, sul caso di accettazione rigenerato:
pompa di calore due valvole, circolatore due, volano quattro, bollitore
quattro — «ogni macchina, ogni tubo che entra o esce». Una valvola gia'
presente nel modello essenziale soddisfa il proprio attacco e non viene
duplicata. Il file completo pubblicato negli esempi deve essere esattamente
la rigenerazione corrente: un artefatto vecchio mostrato come attuale e' il
difetto da cui nasce il piano di rilancio.
"""

from collections import defaultdict
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.canonical import canonical_json
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ConnectionModel, ProjectModel
from disegnatore_mep.rules.apply import apply_proposals
from disegnatore_mep.rules.engine import evaluate
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
ESSENTIAL = ROOT / "examples" / "rules" / "centrale-pdc-essenziale.json"
COMPLETE = ROOT / "examples" / "rules" / "centrale-pdc-completa.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"

MACHINE_FUNCTIONS = frozenset(
    {"heat_generation", "circulation", "thermal_storage", "dhw_storage"}
)


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def complete() -> ProjectModel:
    return load_project(COMPLETE)


def _functions_and_inline(
    project: ProjectModel, registry: ComponentRegistry
) -> tuple[dict[str, frozenset[str]], frozenset[str]]:
    functions: dict[str, frozenset[str]] = {}
    inline: set[str] = set()
    for component in project.components:
        resolved = registry.resolve(component.definition_id)
        functions[component.id] = frozenset(resolved.definition.functions)
        if resolved.is_inline:
            inline.add(component.id)
    return functions, frozenset(inline)


def _touching(project: ProjectModel) -> dict[tuple[str, str], list[ConnectionModel]]:
    touching: dict[tuple[str, str], list[ConnectionModel]] = defaultdict(list)
    for connection in project.connections:
        for ref in (connection.endpoint_a, connection.endpoint_b):
            touching[(ref.component_id, ref.port_id)].append(connection)
    return touching


def _walk(
    project: ProjectModel,
    inline: frozenset[str],
    start: str,
    connection: ConnectionModel,
) -> list[str]:
    """La fila degli accessori in linea da un attacco fino al primo nodo."""
    chain: list[str] = []
    cursor = start
    seen = {cursor}
    current: ConnectionModel | None = connection
    while current is not None:
        peers = [
            ref.component_id
            for ref in (current.endpoint_a, current.endpoint_b)
            if ref.component_id != cursor
        ]
        if not peers or peers[0] in seen:
            break
        peer = peers[0]
        chain.append(peer)
        if peer not in inline:
            break
        seen.add(peer)
        following: ConnectionModel | None = None
        for candidate in project.connections:
            if candidate.id == current.id:
                continue
            if peer in (
                candidate.endpoint_a.component_id,
                candidate.endpoint_b.component_id,
            ):
                following = candidate
                break
        cursor = peer
        current = following
    return chain


def _isolation_serving(
    project: ProjectModel, registry: ComponentRegistry
) -> dict[str, dict[str, set[str]]]:
    """Per ogni macchina, per ogni attacco: le intercettazioni sulla sua fila."""
    functions, inline = _functions_and_inline(project, registry)
    touching = _touching(project)
    served: dict[str, dict[str, set[str]]] = {}
    for component in project.components:
        if not functions[component.id] & MACHINE_FUNCTIONS:
            continue
        ports: dict[str, set[str]] = {}
        for (owner, port_id), connections in touching.items():
            if owner != component.id:
                continue
            found: set[str] = set()
            for connection in connections:
                for item in _walk(project, inline, component.id, connection):
                    if item in inline and "isolation" in functions[item]:
                        found.add(item)
                        break
            ports[port_id] = found
        served[component.id] = ports
    return served


def test_every_connected_machine_port_is_isolated() -> None:
    """«Ogni macchina, ogni tubo che entra o esce» — nessun attacco scoperto."""
    served = _isolation_serving(complete(), catalog())
    assert served, "nessuna macchina trovata nel caso di accettazione"
    uncovered = [
        f"{machine}.{port}"
        for machine, ports in served.items()
        for port, valves in ports.items()
        if not valves
    ]
    assert not uncovered, uncovered


def test_the_counts_are_those_of_d074() -> None:
    """PdC 2, circolatore 2, volano 4 (una e' lo shutoff gia' presente), bollitore 4."""
    project = complete()
    ids = {item.id for item in project.components}
    assert {
        "valve-isolation-hp-water-supply",
        "valve-isolation-hp-water-return",
    } <= ids
    assert {
        "valve-isolation-pump-secondary-a",
        "valve-isolation-pump-secondary-b",
    } <= ids
    assert {
        "valve-isolation-buffer-primary-in",
        "valve-isolation-buffer-secondary-out",
        "valve-isolation-buffer-secondary-in",
    } <= ids
    assert {
        "valve-isolation-cylinder-coil-in",
        "valve-isolation-cylinder-coil-out",
        "valve-isolation-dhw-cylinder-cold-in",
        "valve-isolation-dhw-hot-cylinder-dhw-out",
    } <= ids

    served = _isolation_serving(project, catalog())
    distinct = {machine: set().union(*ports.values()) for machine, ports in served.items()}
    assert len(distinct["hp"] & {f"valve-isolation-hp-water-{side}" for side in ("supply", "return")}) == 2
    assert len(distinct["pump-secondary"]) == 2
    assert len(distinct["buffer"]) == 4
    assert len(distinct["cylinder"]) == 4


def test_a_hand_authored_valve_satisfies_its_attack() -> None:
    """Lo shutoff sul primario del volano conta come valvola di quell'attacco."""
    project = complete()
    ids = {item.id for item in project.components}
    assert "shutoff" in ids
    assert "valve-isolation-buffer-primary-out" not in ids
    served = _isolation_serving(project, catalog())
    assert "shutoff" in served["buffer"]["primary_out"]


def test_the_stored_complete_case_is_the_current_regeneration() -> None:
    """Mai piu' un artefatto vecchio mostrato come attuale: il file pubblicato
    e' esattamente cio' che il pacchetto corrente rigenera dall'essenziale."""
    essential = load_project(ESSENTIAL)
    registry = catalog()
    rules = RuleRegistry.from_directory(RULES)
    regenerated = apply_proposals(essential, evaluate(essential, registry, rules))
    assert canonical_json(regenerated) == COMPLETE.read_text(encoding="utf-8")


def test_rerunning_the_rules_on_the_complete_case_proposes_nothing() -> None:
    """Idempotenza sul file pubblicato, non solo sul modello in memoria."""
    assert evaluate(complete(), catalog(), RuleRegistry.from_directory(RULES)) == []
