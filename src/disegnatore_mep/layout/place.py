"""Posizionamento a fasce funzionali sulla griglia.

D-041 fissa la convenzione: generatori a sinistra, distribuzione a destra,
verso di lettura imposto. Le fasce sono quelle di `BandRole`, dichiarate in
ordine di lettura; quale sottosistema vada su quale fascia lo dice il piano di
impaginazione registrato nel modello (D-042).

Gli accessori in linea **non** vengono posati qui: appartengono alla tratta su
cui stanno, e li posa `inline.py` dopo l'instradamento (D-027).
"""

from collections import defaultdict

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import Rect, SheetFrame
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.model.types import BandRole

from .errors import LayoutError
from .geometry import PlacedSymbol, Point
from .grid import GridSpace
from .partition import SheetPartition

BAND_GUTTER_MM = 10.0
"""Distanza fra due fasce funzionali contigue."""

ROW_GAP_MM = 5.0
"""Distanza verticale minima fra due componenti della stessa fascia."""

ROUTING_MARGIN_MM = 10.0
"""Corridoio libero fra il bordo dell'area di disegno e la prima fascia.

Senza, un simbolo appoggiato al bordo sinistro ha le proprie porte rivolte a
sinistra irraggiungibili: la rotta dovrebbe arrivare da fuori pagina. Quattro
passi di griglia su ciascun lato, cosi' l'area utile al posizionamento resta
un multiplo esatto del passo.
"""


def _band_by_subsystem(project: ProjectModel, sheet_id: str) -> dict[str, BandRole]:
    for sheet in project.sheets:
        if sheet.id == sheet_id:
            return {item.subsystem_id: item.band for item in sheet.band_assignments}
    return {}


def _depth_by_component(project: ProjectModel) -> dict[str, int]:
    """Profondita' topologica: quanti passi separano un componente da una sorgente.

    E' il ripiego quando il modello non dichiara un piano di impaginazione. Non
    sostituisce il piano — l'AI puo' sempre scegliere diversamente — ma da' un
    verso di lettura sensato invece di impilare tutto in una colonna.
    """
    outgoing: dict[str, list[str]] = defaultdict(list)
    incoming: dict[str, int] = {item.id: 0 for item in project.components}
    for connection in project.connections:
        source = connection.endpoint_a.component_id
        target = connection.endpoint_b.component_id
        outgoing[source].append(target)
        incoming[target] = incoming.get(target, 0) + 1

    depth = {item.id: 0 for item in project.components}
    frontier = sorted(item for item, count in incoming.items() if count == 0)
    if not frontier:  # tutto in ciclo: nessuna sorgente, si parte dal primo
        frontier = sorted(depth)[:1]
    seen: set[str] = set()
    while frontier:
        nxt: list[str] = []
        for component_id in frontier:
            if component_id in seen:
                continue
            seen.add(component_id)
            for target in sorted(outgoing[component_id]):
                if target in depth and depth[target] <= depth[component_id]:
                    depth[target] = depth[component_id] + 1
                    nxt.append(target)
        frontier = sorted(nxt)
    return depth


def _assign_bands(
    project: ProjectModel, partition: SheetPartition, placeable: list[str]
) -> dict[str, BandRole]:
    band_of_subsystem = _band_by_subsystem(project, partition.sheet_id)
    bands: dict[str, BandRole] = {}
    if band_of_subsystem:
        for subsystem in project.subsystems:
            band = band_of_subsystem.get(subsystem.id)
            if band is None:
                continue
            for component_id in subsystem.component_ids:
                bands[component_id] = band
        missing = sorted(set(placeable) - set(bands))
        if missing:
            raise LayoutError(
                f"the pagination plan of sheet {partition.sheet_id} assigns no band to "
                f"{missing}: every component needs a band, or it would not be drawn"
            )
        return bands

    roles = list(BandRole)
    # Senza piano dichiarato, i sottosistemi sono gia' un ordine di lettura:
    # l'i-esimo finisce sull'i-esima fascia. E' il ripiego migliore perche' un
    # impianto idronico e' un circuito chiuso e non ha sorgenti topologiche da
    # cui misurare una profondita'.
    if project.subsystems:
        for index, subsystem in enumerate(project.subsystems):
            role = roles[min(index, len(roles) - 1)]
            for component_id in subsystem.component_ids:
                bands[component_id] = role
        for component_id in placeable:
            bands.setdefault(component_id, roles[-1])
        return bands

    depth = _depth_by_component(project)
    for component_id in placeable:
        bands[component_id] = roles[min(depth.get(component_id, 0), len(roles) - 1)]
    return bands


def place_sheet(
    project: ProjectModel,
    partition: SheetPartition,
    catalog: ComponentRegistry,
    frame: SheetFrame,
    inline_component_ids: frozenset[str],
) -> list[PlacedSymbol]:
    """Dispone i componenti non in linea, a fasce, sulla griglia.

    Deterministico: stessa partizione e stesso piano danno la stessa geometria,
    e l'ordine di uscita segue le fasce da sinistra a destra.
    """
    drawing = frame.drawing_rect_mm
    # Il posizionamento lavora dentro un rettangolo piu' piccolo dell'area di
    # disegno: il bordo resta libero perche' l'instradamento possa raggiungere
    # le porte rivolte verso l'esterno.
    area = Rect(
        x_mm=drawing.x_mm + ROUTING_MARGIN_MM,
        y_mm=drawing.y_mm + ROUTING_MARGIN_MM,
        width_mm=drawing.width_mm - 2 * ROUTING_MARGIN_MM,
        height_mm=drawing.height_mm - 2 * ROUTING_MARGIN_MM,
    )
    grid = GridSpace(origin=area, standard=frame.standard)
    step = grid.step_mm

    placeable = [item for item in partition.component_ids if item not in inline_component_ids]
    if not placeable:
        raise LayoutError(
            f"sheet {partition.sheet_id} carries only inline accessories: an "
            f"accessory sits on a run, so there is nothing to draw it against"
        )

    bands = _assign_bands(project, partition, placeable)
    tags = {item.id: item.tag for item in project.components}
    depth = _depth_by_component(project)
    order_hint = {
        item.subsystem_id: item.order
        for sheet in project.sheets
        if sheet.id == partition.sheet_id
        for item in sheet.band_assignments
    }
    subsystem_of = {
        component_id: subsystem.id
        for subsystem in project.subsystems
        for component_id in subsystem.component_ids
    }

    columns: dict[BandRole, list[str]] = defaultdict(list)
    for component_id in placeable:
        columns[bands[component_id]].append(component_id)
    for role in columns:
        columns[role].sort(
            key=lambda item: (
                order_hint.get(subsystem_of.get(item, ""), 0),
                depth.get(item, 0),
                item,
            )
        )

    resolved = {
        item: catalog.resolve(
            next(c.definition_id for c in project.components if c.id == item)
        )
        for item in placeable
    }

    def rotation_for(component_id: str) -> int:
        allowed = resolved[component_id].symbol.manifest.allowed_rotations_deg
        return 0 if 0 in allowed else min(allowed)

    def snap_up(value_mm: float, origin_mm: float) -> float:
        """Il primo nodo di griglia non prima di `value_mm`.

        Misurato **dall'origine dell'area di disegno**, non dallo zero del
        foglio: l'area comincia a 16 mm dal bordo, che non e' un multiplo del
        passo, e snappare in assoluto porterebbe fuori griglia ogni simbolo.
        """
        offset = value_mm - origin_mm
        steps = int(offset / step) + (1 if offset % step > 1e-9 else 0)
        return origin_mm + step * steps

    used_roles = [role for role in BandRole if columns.get(role)]
    widths: dict[BandRole, float] = {}
    for role in used_roles:
        widest = max(
            resolved[item].symbol.manifest.rotated(rotation_for(item)).width_mm
            for item in columns[role]
        )
        widths[role] = snap_up(area.x_mm + widest, area.x_mm) - area.x_mm

    total = sum(widths.values()) + BAND_GUTTER_MM * (len(used_roles) - 1)
    if total > area.width_mm + 1e-9:
        raise LayoutError(
            f"the {len(used_roles)} functional bands need {total:g}mm but the drawing "
            f"area is {area.width_mm:g}mm wide: symbols are never shrunk to fit, "
            f"split the plant across more sheets"
        )

    placed: list[PlacedSymbol] = []
    x_mm = area.x_mm
    for role in used_roles:
        y_mm = area.y_mm
        for component_id in columns[role]:
            manifest = resolved[component_id].symbol.manifest.rotated(
                rotation_for(component_id)
            )
            if y_mm + manifest.height_mm > area.bottom_mm + 1e-9:
                fitting = len(
                    [item for item in placed if item.origin.x_mm == x_mm]
                )
                raise LayoutError(
                    f"band {role.value} does not fit the {area.height_mm:g}mm drawing "
                    f"height: {fitting} of its {len(columns[role])} components fit at "
                    f"fixed scale (symbols are never shrunk; split the plant across "
                    f"more sheets)"
                )
            placed.append(
                PlacedSymbol(
                    component_id=component_id,
                    symbol_id=manifest.id,
                    rotation_deg=rotation_for(component_id),
                    origin=Point(x_mm=x_mm, y_mm=y_mm),
                    width_mm=manifest.width_mm,
                    height_mm=manifest.height_mm,
                    tag=tags.get(component_id),
                )
            )
            y_mm = snap_up(y_mm + manifest.height_mm + ROW_GAP_MM, area.y_mm)
        x_mm += widths[role] + BAND_GUTTER_MM

    return placed
