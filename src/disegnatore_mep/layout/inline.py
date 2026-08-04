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


def _straight_stretches(points: list[Point]) -> list[tuple[float, float]]:
    """Gli intervalli di lunghezza d'arco in cui la spezzata va dritta."""
    stretches: list[tuple[float, float]] = []
    travelled = 0.0
    for before, after in zip(points, points[1:], strict=False):
        length = abs(after.x_mm - before.x_mm) + abs(after.y_mm - before.y_mm)
        if length > 0:
            stretches.append((travelled, travelled + length))
        travelled += length
    return stretches


def _point_at(points: list[Point], distance_mm: float) -> Point:
    return _station_at(points, distance_mm).point


def _split(points: list[Point], low_mm: float, high_mm: float) -> list[list[Point]]:
    """Spezza la polilinea fra due distanze misurate lungo il proprio percorso.

    Il taglio si fa per **lunghezza d'arco**, non filtrando i vertici per
    coordinata: una spezzata a elle non e' monotona su nessuno dei due assi, e
    un filtro per coordinata la ricuciva in diagonale.
    """
    head: list[Point] = []
    tail: list[Point] = []
    travelled = 0.0
    for before, after in zip(points, points[1:], strict=False):
        length = abs(after.x_mm - before.x_mm) + abs(after.y_mm - before.y_mm)
        if travelled <= low_mm:
            head.append(before)
        if travelled >= high_mm:
            tail.append(before)
        travelled += length
    head.append(_point_at(points, low_mm))
    tail.insert(0, _point_at(points, high_mm))
    tail.append(points[-1])

    def tidy(part: list[Point]) -> list[Point]:
        out: list[Point] = []
        for item in part:
            if not out or (out[-1].x_mm, out[-1].y_mm) != (item.x_mm, item.y_mm):
                out.append(item)
        return out

    return [part for part in (tidy(head), tidy(tail)) if len(part) >= 2]


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

    # Un accessorio va posato al **centro di un tratto rettilineo** abbastanza
    # lungo da contenerlo, non a una frazione arbitraria della lunghezza: se la
    # rotta piega accanto a lui, il moncone che resta gli passa dentro il
    # riquadro, e la linea risulta disegnata sotto il simbolo.
    straights = _straight_stretches(points)
    if not straights:
        raise LayoutError(
            f"run {trunk.connection_ids[0]} has no straight stretch to sit an "
            f"accessory on"
        )

    placed: list[PlacedSymbol] = []
    cuts: list[tuple[float, float]] = []
    step = grid.step_mm
    free = list(straights)

    for index, component in enumerate(resolved):
        gap = component.symbol.manifest.inline_gap_mm or 0.0
        needed = gap + 2 * MIN_SPACING_MM
        candidates = [item for item in free if item[1] - item[0] >= needed]
        if not candidates:
            raise LayoutError(
                f"run {trunk.connection_ids[0]} has no straight stretch of "
                f"{needed:g}mm for {component.symbol.manifest.id}: symbols are never "
                f"shrunk to fit, give the run a longer straight length"
            )
        chosen = max(candidates, key=lambda item: item[1] - item[0])
        free.remove(chosen)
        low, high = chosen
        distance = round((low + high) / 2 / step) * step
        distance = min(max(distance, low + needed / 2), high - needed / 2)
        # I due spezzoni del rettilineo restano disponibili per altri accessori.
        free.extend(
            piece
            for piece in ((low, distance - gap / 2), (distance + gap / 2, high))
            if piece[1] - piece[0] > 0
        )
        station = _station_at(points, distance)
        centre = station.point
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
        cuts.append((distance - gap / 2, distance + gap / 2))

    segments = [points]
    for low, high in cuts:
        rebuilt: list[list[Point]] = []
        for part in segments:
            if _polyline_length(part) <= 0:
                continue
            offset = _offset_of(points, part[0])
            local_low, local_high = low - offset, high - offset
            if local_low < 0 or local_high > _polyline_length(part):
                rebuilt.append(part)
                continue
            rebuilt.extend(_split(part, local_low, local_high))
        segments = rebuilt

    return placed, routed.model_copy(update={"segments": segments})


def _offset_of(points: list[Point], start: Point) -> float:
    """Distanza dall'inizio della polilinea originale al punto dato."""
    travelled = 0.0
    for before, after in zip(points, points[1:], strict=False):
        length = abs(after.x_mm - before.x_mm) + abs(after.y_mm - before.y_mm)
        if abs(before.x_mm - start.x_mm) + abs(before.y_mm - start.y_mm) <= 1e-9:
            return travelled
        on_segment = (
            min(before.x_mm, after.x_mm) - 1e-9 <= start.x_mm <= max(before.x_mm, after.x_mm) + 1e-9
            and min(before.y_mm, after.y_mm) - 1e-9 <= start.y_mm <= max(before.y_mm, after.y_mm) + 1e-9
        )
        if on_segment:
            return travelled + abs(start.x_mm - before.x_mm) + abs(start.y_mm - before.y_mm)
        travelled += length
    return travelled
