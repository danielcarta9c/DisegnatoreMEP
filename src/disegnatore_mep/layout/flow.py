"""Mandata o ritorno: lo dice la topologia, non la geometria.

Finora il verso di una tratta si leggeva dal disegno gia' fatto — «chi va verso
destra e' mandata» — e bastava che un componente finisse a sinistra del suo
alimentatore perche' la mandata venisse disegnata blu. E' il difetto che il PM
ha visto per primo: «il ritorno blu va dentro la valvola a tre vie?». Ci andava
la mandata: la valvola sta a valle della pompa di calore, e la geometria la
aveva messa a sinistra.

Il verso e' una proprieta' del **modello**, che e' orientato: ogni connessione
va da una porta `out` a una porta `in`. Quello che manca al modello e' quale
componente sia la sorgente del circuito, e lo dicono le funzioni di catalogo.

La regola, che e' poi come si legge una centrale:

- ogni rete ha una **sorgente** — il generatore, o l'accumulo se generatori non
  ce ne sono;
- cio' che esce dalla sorgente e prosegue in avanti e' **mandata**, fino al
  primo utilizzatore;
- cio' che rientra nella sorgente, risalito all'indietro, e' **ritorno**, fino
  al primo utilizzatore.

Camminare si ferma sugli utilizzatori perche' e' li' che il fluido cambia
mestiere: quello che entra in un radiatore e' mandata, quello che ne esce e'
ritorno, e nessuna delle due camminate deve attraversarlo per non riscrivere
l'altra meta' del circuito.
"""

from collections import defaultdict

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.model.project import ProjectModel

from .trunks import Trunk

TrunkKey = tuple[str, ...]
"""Identita' di una tratta: le connessioni che la compongono."""

GENERATOR_FUNCTIONS = frozenset(
    {
        "heat_generation",
        "cooling_generation",
        "refrigerant_generation",
        "gas_combustion",
    }
)
"""Chi produce il fluido caldo o freddo: e' la sorgente naturale di un circuito."""

STORE_FUNCTIONS = frozenset(
    {
        "thermal_storage",
        "dhw_storage",
        "hydraulic_separation",
    }
)
"""Chi lo accumula o lo separa: e' la sorgente del circuito che ne parte.

Un volano e' l'utilizzatore del primario e la sorgente del secondario. Le due
cose non sono in contraddizione: dipende da quale rete si sta guardando, ed e'
per questo che l'orientamento si calcola **una rete alla volta**.
"""

LOAD_FUNCTIONS = frozenset(
    {
        "emission",
        "air_terminal",
        "direct_expansion_terminal",
        "thermal_storage",
        "dhw_storage",
        "hydraulic_separation",
        "heat_exchange",
        "boundary",
    }
)
"""Dove il fluido cede o prende calore, e quindi cambia da mandata a ritorno.

Ci stanno dentro anche gli accumuli: rispetto al circuito che li alimenta un
volano e' un utilizzatore a tutti gli effetti, e la camminata deve fermarcisi.
"""


def _rank(functions: frozenset[str]) -> int:
    if functions & GENERATOR_FUNCTIONS:
        return 2
    if functions & STORE_FUNCTIONS:
        return 1
    return 0


def _walk(
    edges: dict[str, list[Trunk]],
    onward: str,
    source: str,
    functions_of: dict[str, frozenset[str]],
) -> set[TrunkKey]:
    """Le tratte raggiunte partendo dalla sorgente, fermandosi sugli utilizzatori."""
    reached: set[TrunkKey] = set()
    frontier = [source]
    visited = {source}
    while frontier:
        following: list[str] = []
        for component_id in frontier:
            for trunk in edges[component_id]:
                reached.add(trunk.connection_ids)
                beyond: str = getattr(trunk, onward).component_id
                if beyond in visited:
                    continue
                visited.add(beyond)
                if functions_of.get(beyond, frozenset()) & LOAD_FUNCTIONS:
                    continue
                following.append(beyond)
        frontier = following
    return reached


def orient_trunks(
    project: ProjectModel, catalog: ComponentRegistry, trunks: list[Trunk]
) -> dict[TrunkKey, bool | None]:
    """Per ciascuna tratta: `True` mandata, `False` ritorno, `None` indecidibile.

    `None` non e' un fallimento: e' un circuito in cui nessun utilizzatore
    separa l'andata dal ritorno — un anello di sola distribuzione, per esempio —
    e la sola cosa che resta e' guardare come e' venuto il disegno. Chi chiama
    decide come ripiegare; qui non si inventa un verso che il modello non ha.
    """
    functions_of = {
        item.id: frozenset(catalog.resolve(item.definition_id).definition.functions)
        for item in project.components
    }
    position = {item.id: index for index, item in enumerate(project.components)}

    by_network: dict[str, list[Trunk]] = defaultdict(list)
    for trunk in trunks:
        by_network[trunk.network_id].append(trunk)

    oriented: dict[TrunkKey, bool | None] = {}
    for group in by_network.values():
        outgoing: dict[str, list[Trunk]] = defaultdict(list)
        incoming: dict[str, list[Trunk]] = defaultdict(list)
        members: list[str] = []
        for trunk in group:
            outgoing[trunk.start.component_id].append(trunk)
            incoming[trunk.end.component_id].append(trunk)
            for component_id in (trunk.start.component_id, trunk.end.component_id):
                if component_id not in members:
                    members.append(component_id)
        if not members:
            continue

        source = min(
            members,
            key=lambda item: (
                -_rank(functions_of.get(item, frozenset())),
                position.get(item, 0),
            ),
        )
        supply = _walk(outgoing, "end", source, functions_of)
        returns = _walk(incoming, "start", source, functions_of)
        for trunk in group:
            key = trunk.connection_ids
            in_supply, in_return = key in supply, key in returns
            oriented[key] = None if in_supply == in_return else in_supply
    return oriented


__all__ = ["TrunkKey", "orient_trunks"]
