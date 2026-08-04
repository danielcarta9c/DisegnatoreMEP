"""Gli accessori in linea, posati sulla tratta che hanno spezzato.

D-027: un componente in linea non viene sovrapposto a una linea continua. Nel
modello topologico spezza la connessione in due; qui spezza anche il disegno,
interrompendo la spezzata per la propria `inline_gap_mm`. E' il consumatore che
a quel campo mancava (W4).
"""

from dataclasses import dataclass

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.model.project import ProjectModel

from .errors import LayoutError
from .geometry import PlacedSymbol, Point, RoutedTrunk
from .grid import GridSpace
from .trunks import Trunk

MIN_SPACING_MM = 2.5
"""Distanza minima fra due accessori sulla stessa tratta: un passo di griglia."""


@dataclass(frozen=True)
class _Station:
    point: Point
    horizontal: bool


def _polyline_length(points: list[Point]) -> float:
    return sum(
        abs(after.x_mm - before.x_mm) + abs(after.y_mm - before.y_mm)
        for before, after in zip(points, points[1:], strict=False)
    )


def _station_at(points: list[Point], distance_mm: float) -> _Station:
    """Punto e giacitura del segmento a una distanza data dall'inizio."""
    travelled = 0.0
    for before, after in zip(points, points[1:], strict=False):
        length = abs(after.x_mm - before.x_mm) + abs(after.y_mm - before.y_mm)
        if length <= 0:
            continue
        if travelled + length >= distance_mm:
            ratio = (distance_mm - travelled) / length
            return _Station(
                point=Point(
                    x_mm=before.x_mm + (after.x_mm - before.x_mm) * ratio,
                    y_mm=before.y_mm + (after.y_mm - before.y_mm) * ratio,
                ),
                horizontal=before.y_mm == after.y_mm,
            )
        travelled += length
    last, previous = points[-1], points[-2]
    return _Station(point=last, horizontal=previous.y_mm == last.y_mm)


def _cut(points: list[Point], centre: Point, horizontal: bool, gap_mm: float) -> list[list[Point]]:
    """Spezza la polilinea attorno al centro, per `gap_mm` lungo la sua giacitura."""
    half = gap_mm / 2
    if horizontal:
        low = Point(x_mm=centre.x_mm - half, y_mm=centre.y_mm)
        high = Point(x_mm=centre.x_mm + half, y_mm=centre.y_mm)
    else:
        low = Point(x_mm=centre.x_mm, y_mm=centre.y_mm - half)
        high = Point(x_mm=centre.x_mm, y_mm=centre.y_mm + half)

    def before_cut(point: Point) -> bool:
        return (point.x_mm < low.x_mm) if horizontal else (point.y_mm < low.y_mm)

    def after_cut(point: Point) -> bool:
        return (point.x_mm > high.x_mm) if horizontal else (point.y_mm > high.y_mm)

    head = [item for item in points if before_cut(item)] + [low]
    tail = [high] + [item for item in points if after_cut(item)]
    return [part for part in (head, tail) if len(part) >= 2]


def place_inline_accessories(
    project: ProjectModel,
    trunk: Trunk,
    routed: RoutedTrunk,
    catalog: ComponentRegistry,
    grid: GridSpace,
) -> tuple[list[PlacedSymbol], RoutedTrunk]:
    """Posa gli accessori della tratta e restituisce la spezzata interrotta.

    Gli accessori si distribuiscono lungo la tratta nell'ordine in cui la
    percorrono; ciascuno prende il verso del tratto su cui cade.
    """
    if not trunk.inline_component_ids:
        return [], routed

    definitions = {item.id: item.definition_id for item in project.components}
    tags = {item.id: item.tag for item in project.components}
    points = routed.segments[0]
    total = _polyline_length(points)

    resolved = [
        catalog.resolve(definitions[component_id])
        for component_id in trunk.inline_component_ids
    ]
    needed = sum(
        (item.symbol.manifest.inline_gap_mm or 0.0) + MIN_SPACING_MM for item in resolved
    )
    if needed > total:
        raise LayoutError(
            f"run {trunk.connection_ids[0]} is {total:g}mm long but its "
            f"{len(resolved)} inline accessories need {needed:g}mm: symbols are "
            f"never shrunk to fit, give the run more room"
        )

    placed: list[PlacedSymbol] = []
    segments = [points]
    step = grid.step_mm
    count = len(resolved)

    for index, component in enumerate(resolved):
        distance = total * (index + 1) / (count + 1)
        station = _station_at(points, distance)
        # Il centro cade su un nodo, cosi' le porte dell'accessorio ci cadono
        # anche loro e l'instradamento le raggiunge.
        centre = Point(
            x_mm=grid.origin.x_mm + round((station.point.x_mm - grid.origin.x_mm) / step) * step,
            y_mm=grid.origin.y_mm + round((station.point.y_mm - grid.origin.y_mm) / step) * step,
        )
        rotation = 0 if station.horizontal else 90
        manifest = component.symbol.manifest
        if rotation not in manifest.allowed_rotations_deg:
            raise LayoutError(
                f"inline accessory {manifest.id} cannot be drawn rotated by "
                f"{rotation} degrees, which the run it sits on requires: "
                f"allowed {sorted(manifest.allowed_rotations_deg)}"
            )
        turned = manifest.rotated(rotation)
        component_id = trunk.inline_component_ids[index]
        placed.append(
            PlacedSymbol(
                component_id=component_id,
                symbol_id=turned.id,
                rotation_deg=rotation,
                origin=Point(
                    x_mm=centre.x_mm - turned.width_mm / 2,
                    y_mm=centre.y_mm - turned.height_mm / 2,
                ),
                width_mm=turned.width_mm,
                height_mm=turned.height_mm,
                tag=tags.get(component_id),
            )
        )
        gap = manifest.inline_gap_mm or 0.0
        segments = [
            piece
            for part in segments
            for piece in _cut(part, centre, station.horizontal, gap)
        ]

    return placed, routed.model_copy(update={"segments": segments})
