"""Gli accessori in linea, posati sulla tratta che hanno spezzato.

D-027: un componente in linea non viene sovrapposto a una linea continua. Nel
modello topologico spezza la connessione in due; qui spezza anche il disegno,
interrompendo la spezzata per la propria `inline_gap_mm`. E' il consumatore che
a quel campo mancava (W4).

Qui vive anche `settle_sheet`, l'instradamento **come esce sulla tavola**:
tratte instradate una dopo l'altra e accessori posati appena la propria tratta
e' pronta. E' una funzione sola perche' i suoi due chiamanti devono vedere la
stessa geometria — `compose_sheet`, che la disegna, e il ciclo di
miglioramento, che sceglie le mosse. Finche' il ciclo valutava un
instradamento **senza** accessori sceglieva su una tavola che non esisteva:
approvava una posa e ne consegnava un'altra.
"""

from dataclasses import dataclass
from math import ceil
from typing import NamedTuple

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.model.project import ProjectModel

from .errors import LayoutError
from .geometry import PlacedSymbol, Point, RoutedTrunk, run_intrudes_on
from .grid import GridSpace
from .route import route_sheet
from .trunks import Trunk

MIN_SPACING_MM = 2.5
"""Distanza minima fra due accessori sulla stessa tratta: un passo di griglia."""

END_CLEARANCE_MM = 5.0
"""Stacco fra un accessorio e il componente all'estremo della propria tratta.

Due passi, il doppio della distanza fra due accessori, e per un motivo diverso.
Fra due accessori basta che si distinguano; contro un componente serve invece
che resti **una colonna libera**, perche' e' da li' che passano le tubazioni che
raggiungono i suoi altri attacchi. Con un passo solo la valvola di sicurezza
della pompa di calore le si e' appoggiata al fianco e ha chiuso il corridoio del
ritorno del primario: l'instradamento e' fallito con una diagnostica che parlava
di tutt'altro.
"""


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
    obstacles: list[PlacedSymbol] | None = None,
    runs: list[RoutedTrunk] | None = None,
) -> tuple[list[PlacedSymbol], RoutedTrunk]:
    """Posa gli accessori della tratta e restituisce la spezzata interrotta.

    Gli accessori si distribuiscono lungo la tratta nell'ordine in cui la
    percorrono; ciascuno prende il verso del tratto su cui cade.

    `obstacles` sono i simboli gia' posati sul foglio: una rotta puo'
    costeggiare un serbatoio a un passo di distanza, e li' la linea si legge,
    ma il riquadro di un accessorio alto sporge oltre la linea e finirebbe
    dentro il serbatoio. Le posizioni il cui riquadro tocca un simbolo posato
    si saltano, avanzando lungo la tratta.

    `runs` sono le tratte **gia' disegnate**, e vanno tenute a distanza di
    rispetto come qualunque altro simbolo (B5): un accessorio e' un simbolo, e
    posarlo a filo della tubazione di un'altra tratta si legge come disegnarcelo
    sopra. Senza questo vincolo la valvola di intercettazione del ritorno
    pompa di calore e i due accessori del freddo sanitario finivano a 0 mm da
    una tratta instradata prima di loro, ed erano tre rilievi bloccanti sulla
    tavola consegnata. Le stazioni che non rispettano lo stacco si saltano,
    esattamente come quelle che cascano su un simbolo.
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
    straights = [
        (max(low, END_CLEARANCE_MM), min(high, total - END_CLEARANCE_MM))
        for low, high in _straight_stretches(points)
    ]
    straights = [item for item in straights if item[1] > item[0]]
    if not straights:
        raise LayoutError(
            f"run {trunk.connection_ids[0]} has no straight stretch to sit an "
            f"accessory on"
        )

    placed: list[PlacedSymbol] = []
    cuts: list[tuple[float, float]] = []
    step = grid.step_mm
    # Gli accessori si posano **nell'ordine della catena**, avanzando lungo la
    # tratta: sulla tavola compaiono nell'ordine topologico in cui il fluido
    # li attraversa, che e' l'unico ordine vero. Prima ciascuno prendeva il
    # centro del rettilineo piu' lungo: l'ordine ne usciva rimescolato, e ogni
    # taglio dimezzava la capacita' del rettilineo — su una tratta da quattro
    # accessori di dieci millimetri il quarto non entrava piu' (D-074 ne mette
    # quattro in fila davvero, e li vuole in fila davvero).
    cursor = 0.0

    clearance = grid.standard.min_clearance_mm
    others = list(runs or [])

    def clear_of_symbols(origin: Point, width: float, height: float) -> bool:
        """Il riquadro non si sovrappone a nessun simbolo posato.

        Lo stesso predicato — stretto, con tolleranza — del controllo di
        correttezza: toccarsi sul filo e' ammesso, condividere superficie no.
        """
        return not any(
            origin.x_mm < item.right_mm - 1e-6
            and item.origin.x_mm < origin.x_mm + width - 1e-6
            and origin.y_mm < item.bottom_mm - 1e-6
            and item.origin.y_mm < origin.y_mm + height - 1e-6
            for item in (obstacles or [])
        )

    def clear_of_other_runs(origin: Point, width: float, height: float) -> bool:
        """Nessuna tratta gia' disegnata gli passa addosso o a filo (B5, D-027)."""
        if not others:
            return True
        box = (origin.x_mm, origin.y_mm, origin.x_mm + width, origin.y_mm + height)
        return not run_intrudes_on(box, others, clearance)

    for index, component in enumerate(resolved):
        manifest = component.symbol.manifest
        gap = manifest.inline_gap_mm or 0.0
        needed = gap + 2 * MIN_SPACING_MM
        found: _Station | None = None
        turned = manifest
        rotation = 0
        distance = 0.0
        for low, high in straights:
            # Il primo nodo di griglia da cui l'accessorio sta nel rettilineo,
            # oltre l'accessorio precedente: avanzare invece di spezzare tiene
            # l'ordine e non spreca nemmeno un passo. Se il riquadro casca su
            # un simbolo posato, si avanza di un passo e si riprova.
            wanted = max(low, cursor) + needed / 2
            snapped = ceil((wanted - 1e-9) / step) * step
            while snapped + needed / 2 <= high + 1e-9:
                station = _station_at(points, snapped)
                rotation = 0 if station.horizontal else 90
                if rotation not in manifest.allowed_rotations_deg:
                    raise LayoutError(
                        f"inline accessory {manifest.id} cannot be drawn rotated by "
                        f"{rotation} degrees, which the run it sits on requires: "
                        f"allowed {sorted(manifest.allowed_rotations_deg)}"
                    )
                turned = manifest.rotated(rotation)
                origin = Point(
                    x_mm=station.point.x_mm - turned.width_mm / 2,
                    y_mm=station.point.y_mm - turned.height_mm / 2,
                )
                if clear_of_symbols(
                    origin, turned.width_mm, turned.height_mm
                ) and clear_of_other_runs(origin, turned.width_mm, turned.height_mm):
                    found, distance = station, snapped
                    break
                snapped += step
            if found is not None:
                break
        if found is None:
            raise LayoutError(
                f"run {trunk.connection_ids[0]} has no straight stretch of "
                f"{needed:g}mm for {component.symbol.manifest.id} that keeps "
                f"{clearance:g}mm clear of the other symbols and runs: symbols are "
                f"never shrunk to fit, give the run a longer straight length"
            )
        cursor = distance + needed / 2
        component_id = trunk.inline_component_ids[index]
        placed.append(
            PlacedSymbol(
                component_id=component_id,
                symbol_id=turned.id,
                rotation_deg=rotation,
                origin=Point(
                    x_mm=found.point.x_mm - turned.width_mm / 2,
                    y_mm=found.point.y_mm - turned.height_mm / 2,
                ),
                width_mm=turned.width_mm,
                height_mm=turned.height_mm,
                tag=tags.get(component_id),
            )
        )
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


class SettledSheet(NamedTuple):
    """La tavola instradata **come si disegna**: linee interrotte e accessori."""

    symbols: list[PlacedSymbol]
    """I simboli posati piu' gli accessori, nell'ordine in cui sono comparsi."""

    accessories: list[PlacedSymbol]
    """I soli accessori in linea, quelli che questa posa ha aggiunto."""

    routes: list[RoutedTrunk]
    """Le tratte con la spezzata gia' interrotta, una per tratta e nel suo ordine."""

    unfit: tuple[int, ...]
    """Indici delle tratte che non hanno ospitato i propri accessori.

    Sempre vuoto quando si instrada per disegnare: li' una tratta che non
    ospita i propri accessori e' un errore e solleva. Si riempie solo in
    lettura tollerante, dove serve **contare** i difetti di una posa invece che
    rifiutarla, perche' quel conto e' la prima voce del confronto fra pose.
    """


def settle_sheet(
    project: ProjectModel,
    trunks: list[Trunk],
    placed: list[PlacedSymbol],
    catalog: ComponentRegistry,
    grid: GridSpace,
    tolerant: bool = False,
) -> SettledSheet:
    """Instrada il foglio posando gli accessori appena instradata la loro tratta.

    Restituire gli accessori dentro la callback li rende ostacoli per le tratte
    successive: posati tutti alla fine erano invisibili all'instradamento, che
    ci passava sopra. E passarli come `runs` a chi li posa li tiene lontani
    dalle tratte gia' disegnate, che a loro volta erano invisibili a lui.

    Con `tolerant` una tratta che non riesce a ospitare i propri accessori non
    fa fallire il foglio: si annota fra le `unfit` e resta con la spezzata
    intera. Serve al ciclo di miglioramento, che deve poter **misurare** una
    posa cattiva per preferirle una buona; chi disegna la lascia sollevare.
    """
    symbols = list(placed)
    accessories: list[PlacedSymbol] = []
    drawn: list[RoutedTrunk] = []
    unfit: list[int] = []

    def settle(trunk: Trunk, route: RoutedTrunk) -> list[PlacedSymbol]:
        try:
            found, pieces = place_inline_accessories(
                project, trunk, route, catalog, grid, symbols, drawn
            )
        except LayoutError:
            if not tolerant:
                raise
            unfit.append(len(drawn))
            drawn.append(route)
            return []
        symbols.extend(found)
        accessories.extend(found)
        drawn.append(pieces)
        return found

    route_sheet(project, list(trunks), symbols, catalog, grid, settle)
    return SettledSheet(
        symbols=symbols, accessories=accessories, routes=drawn, unfit=tuple(unfit)
    )
