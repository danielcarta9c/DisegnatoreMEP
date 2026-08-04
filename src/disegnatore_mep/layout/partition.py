"""Divisione dell'impianto in tavole, con rimandi accoppiati.

La partizione precede il layout (D-028, specifica §10.1): tagliare un disegno
gia' disposto spezzerebbe circuiti in modo arbitrario. Qui si esegue il piano
di impaginazione che il modello dichiara — quali sottosistemi su quale tavola —
e si generano i rimandi per le connessioni che attraversano un confine.

Quando il modello non dichiara tavole, l'impianto sta su una sola: la
partizione e' facoltativa (D-020).
"""

from dataclasses import dataclass

from disegnatore_mep.model.project import PortRef, ProjectModel

from .errors import LayoutError
from .trunks import Trunk

SINGLE_SHEET_ID = "t1"
"""Identificativo della tavola implicita, quando il modello non ne dichiara."""


@dataclass(frozen=True)
class SheetLink:
    """Meta' di un rimando: dove la connessione esce, e dove riprende.

    I due gemelli condividono `pair_id`, derivato dalla connessione, quindi
    stabile fra rigenerazioni.
    """

    id: str
    pair_id: str
    sheet_id: str
    peer_sheet_id: str
    connection_id: str
    network_id: str
    medium: str
    port: PortRef


@dataclass(frozen=True)
class SheetPartition:
    sheet_id: str
    title: str
    component_ids: tuple[str, ...]
    network_ids: tuple[str, ...]
    connection_ids: tuple[str, ...]
    trunks: tuple[Trunk, ...]
    links: tuple[SheetLink, ...]


def _sheet_of_component(project: ProjectModel) -> dict[str, str]:
    """Da componente a tavola, passando per il sottosistema che lo contiene."""
    subsystem_sheet: dict[str, str] = {}
    for sheet in project.sheets:
        for subsystem_id in sheet.subsystem_ids:
            subsystem_sheet[subsystem_id] = sheet.id

    placement: dict[str, str] = {}
    for subsystem in project.subsystems:
        sheet_id = subsystem_sheet.get(subsystem.id)
        if sheet_id is None:
            continue
        for component_id in subsystem.component_ids:
            existing = placement.get(component_id)
            if existing is not None and existing != sheet_id:
                raise LayoutError(
                    f"component {component_id} would be drawn on more than one sheet, "
                    f"{existing} and {sheet_id}: a component belongs to one tavola"
                )
            placement[component_id] = sheet_id

    missing = sorted(
        item.id for item in project.components if item.id not in placement
    )
    if missing:
        raise LayoutError(
            f"components belong to no sheet and would silently disappear from the "
            f"drawing: {missing}; every component needs a subsystem carried by a sheet"
        )
    return placement


def partition_project(
    project: ProjectModel, trunks: list[Trunk]
) -> list[SheetPartition]:
    """Esegue il piano di impaginazione. L'ordine segue quello del modello."""
    media = {item.id: item.medium for item in project.networks}

    if not project.sheets:
        return [
            SheetPartition(
                sheet_id=SINGLE_SHEET_ID,
                title=project.metadata.project_name,
                component_ids=tuple(item.id for item in project.components),
                network_ids=tuple(item.id for item in project.networks),
                connection_ids=tuple(item.id for item in project.connections),
                trunks=tuple(trunks),
                links=(),
            )
        ]

    placement = _sheet_of_component(project)
    components: dict[str, list[str]] = {sheet.id: [] for sheet in project.sheets}
    for component in project.components:
        components[placement[component.id]].append(component.id)

    empty = sorted(sheet_id for sheet_id, items in components.items() if not items)
    if empty:
        raise LayoutError(f"sheet {empty[0]} carries no component: an empty tavola")

    connections: dict[str, list[str]] = {sheet.id: [] for sheet in project.sheets}
    links: dict[str, list[SheetLink]] = {sheet.id: [] for sheet in project.sheets}
    networks: dict[str, set[str]] = {sheet.id: set() for sheet in project.sheets}

    for connection in project.connections:
        sheet_a = placement[connection.endpoint_a.component_id]
        sheet_b = placement[connection.endpoint_b.component_id]
        if sheet_a == sheet_b:
            connections[sheet_a].append(connection.id)
            networks[sheet_a].add(connection.network_id)
            continue
        # A cavallo di un confine: due meta' di rimando, una per tavola. La
        # connessione resta una sola nel modello; qui si dichiara solo dove
        # esce e dove riprende.
        for here, there in ((sheet_a, sheet_b), (sheet_b, sheet_a)):
            port = (
                connection.endpoint_a
                if placement[connection.endpoint_a.component_id] == here
                else connection.endpoint_b
            )
            networks[here].add(connection.network_id)
            links[here].append(
                SheetLink(
                    id=f"{connection.id}-{here}",
                    pair_id=connection.id,
                    sheet_id=here,
                    peer_sheet_id=there,
                    connection_id=connection.id,
                    network_id=connection.network_id,
                    medium=media.get(connection.network_id, ""),
                    port=port,
                )
            )

    trunk_of_sheet: dict[str, list[Trunk]] = {sheet.id: [] for sheet in project.sheets}
    for trunk in trunks:
        sheet_id = placement[trunk.start.component_id]
        if placement[trunk.end.component_id] == sheet_id:
            trunk_of_sheet[sheet_id].append(trunk)
            continue
        # Una tratta a cavallo di due tavole non viene instradata su nessuna
        # delle due: al suo posto compaiono i due rimandi. Ma un accessorio in
        # linea sta **su** una tratta, quindi resterebbe senza una linea su cui
        # posarsi, e sparirebbe dal disegno pur essendo nel modello.
        if trunk.inline_component_ids:
            raise LayoutError(
                f"the sheet boundary cuts run {trunk.connection_ids[0]}, which "
                f"carries the inline accessories {sorted(trunk.inline_component_ids)}: "
                f"an accessory sits on a run, so a run that crosses sheets must not "
                f"carry any. Move the accessory's subsystem onto the same sheet as "
                f"the rest of its run, or cut elsewhere"
            )

    return [
        SheetPartition(
            sheet_id=sheet.id,
            title=sheet.title,
            component_ids=tuple(components[sheet.id]),
            network_ids=tuple(sorted(networks[sheet.id])),
            connection_ids=tuple(connections[sheet.id]),
            trunks=tuple(trunk_of_sheet[sheet.id]),
            links=tuple(links[sheet.id]),
        )
        for sheet in project.sheets
    ]
