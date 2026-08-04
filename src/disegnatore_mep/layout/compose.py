"""La catena completa, nell'ordine che la specifica §10.1 fissa.

    modello approvato
    -> validazione topologica          (validation/topology.py, fuori di qui)
    -> partizione funzionale in tavole
    -> assegnazione dei simboli
    -> layout per ciascuna tavola
    -> instradamento ortogonale
    -> accessori in linea sulla tratta
    -> testi e tag
    -> legenda e rimandi

La partizione precede il layout: tagliare un disegno gia' disposto spezzerebbe
circuiti in modo arbitrario (D-028).
"""

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import ORDINARY_FRAMES, Rect, SheetFrame
from disegnatore_mep.model.project import ProjectModel

from .composition import CALLOUT_GAP_MM, levels_of
from .errors import LayoutError
from .geometry import (
    CrossReference,
    DrawingGeometry,
    PlacedSymbol,
    Point,
    RoutedTrunk,
    SheetGeometry,
)
from .grid import GridSpace
from .inline import place_inline_accessories
from .labels import place_labels
from .legend import build_legend
from .partition import SheetLink, SheetPartition, partition_project
from .place import place_sheet
from .route import route_sheet
from .trunks import Trunk, build_trunks

CROSS_REFERENCE_GAP_MM = 2.5
"""Stacco fra la porta e il marcatore di rimando."""


def inline_component_ids(
    project: ProjectModel, catalog: ComponentRegistry
) -> frozenset[str]:
    """Chi spezza una linea lo dice la libreria, non un elenco nel motore."""
    return frozenset(
        item.id
        for item in project.components
        if catalog.resolve(item.definition_id).is_inline
    )


def _cross_references(
    partition: SheetPartition, placed_by_component: dict[str, PlacedSymbol]
) -> list[CrossReference]:
    references: list[CrossReference] = []
    for link in partition.links:
        symbol = placed_by_component.get(link.port.component_id)
        if symbol is None:
            continue
        references.append(
            CrossReference(
                id=link.id,
                pair_id=link.pair_id,
                peer_sheet_id=link.peer_sheet_id,
                # Cio' che si legge e' in italiano (D-051): la sigla della
                # tavola di destinazione e il fluido che prosegue.
                text=f"→ {link.peer_sheet_id.upper()} · {link.medium}",
                anchor=Point(
                    x_mm=symbol.right_mm + CROSS_REFERENCE_GAP_MM,
                    y_mm=symbol.origin.y_mm,
                ),
            )
        )
    return references


def _shifted(point: Point, delta_mm: float) -> Point:
    return Point(x_mm=point.x_mm, y_mm=point.y_mm + delta_mm)


def centre_vertically(
    sheet: SheetGeometry, drawing: Rect, step_mm: float, text_mm: float
) -> SheetGeometry:
    """Porta il blocco disegnato al centro verticale dell'area.

    La composizione nasce appoggiata a una linea di terra a quota fissa, e un
    impianto basso lasciava vuoti i due terzi alti del foglio. Non si puo'
    rimediare ingrandendo i simboli — la scala di stampa e' invariante
    (ADR 0003) — quindi si sposta: il blocco resta quello che e' e si mette in
    mezzo, richiami e linea di terra compresi.

    Lo spostamento e' un multiplo del passo, cosi' nulla esce dalla griglia.
    """
    tops = [item.origin.y_mm for item in sheet.symbols]
    bottoms = [item.bottom_mm for item in sheet.symbols]
    for route in sheet.routes:
        for segment in route.segments:
            tops.extend(point.y_mm for point in segment)
            bottoms.extend(point.y_mm for point in segment)
    # I richiami sono la riga piu' bassa: il testo scende sotto la propria base.
    bottoms.extend(item.anchor.y_mm + text_mm for item in sheet.labels)
    if sheet.ground_line_y_mm is not None:
        bottoms.append(sheet.ground_line_y_mm)
    if not tops:
        return sheet

    top, bottom = min(tops), max(bottoms)
    wanted = drawing.y_mm + (drawing.height_mm - (bottom - top)) / 2
    delta = round((wanted - top) / step_mm) * step_mm
    delta = min(delta, drawing.bottom_mm - bottom)
    delta = max(delta, drawing.y_mm - top)
    delta = round(delta / step_mm) * step_mm
    if delta == 0:
        return sheet

    return sheet.model_copy(
        update={
            "symbols": [
                item.model_copy(update={"origin": _shifted(item.origin, delta)})
                for item in sheet.symbols
            ],
            "routes": [
                item.model_copy(
                    update={
                        "segments": [
                            [_shifted(point, delta) for point in segment]
                            for segment in item.segments
                        ],
                        "crossings": [
                            _shifted(point, delta) for point in item.crossings
                        ],
                    }
                )
                for item in sheet.routes
            ],
            "labels": [
                item.model_copy(
                    update={
                        "anchor": _shifted(item.anchor, delta),
                        "leader_from": (
                            None
                            if item.leader_from is None
                            else _shifted(item.leader_from, delta)
                        ),
                    }
                )
                for item in sheet.labels
            ],
            "cross_references": [
                item.model_copy(update={"anchor": _shifted(item.anchor, delta)})
                for item in sheet.cross_references
            ],
            "ground_line_y_mm": (
                None
                if sheet.ground_line_y_mm is None
                else sheet.ground_line_y_mm + delta
            ),
        }
    )


def compose_sheet(
    project: ProjectModel,
    partition: SheetPartition,
    catalog: ComponentRegistry,
    frame: SheetFrame,
    inline_ids: frozenset[str],
) -> SheetGeometry:
    grid = GridSpace(origin=frame.drawing_rect_mm, standard=frame.standard)
    levels = levels_of(
        frame.drawing_rect_mm.y_mm, frame.drawing_rect_mm.height_mm, grid.step_mm
    )
    placed = place_sheet(project, partition, catalog, frame, inline_ids)
    broken: list[RoutedTrunk] = []

    def settle(trunk: Trunk, route: RoutedTrunk) -> list[PlacedSymbol]:
        """Posa gli accessori appena la loro tratta e' instradata.

        Restituirli qui li rende ostacoli per le tratte successive: posati tutti
        alla fine erano invisibili all'instradamento, che ci passava sopra.
        """
        accessories, pieces = place_inline_accessories(
            project, trunk, route, catalog, grid
        )
        placed.extend(accessories)
        broken.append(pieces)
        return accessories

    route_sheet(project, list(partition.trunks), placed, catalog, grid, settle)

    entries, keys = build_legend(
        project, placed, partition.network_ids, catalog, frame
    )
    composed = SheetGeometry(
        sheet_id=partition.sheet_id,
        title=partition.title,
        symbols=placed,
        routes=broken,
        labels=place_labels(
            project,
            placed,
            frame.standard,
            callout_y_mm=levels.ground_mm + CALLOUT_GAP_MM,
        ),
        legend=entries,
        network_keys=keys,
        ground_line_y_mm=levels.ground_mm,
        cross_references=_cross_references(
            partition, {item.component_id: item for item in placed}
        ),
    )
    return centre_vertically(
        composed, frame.drawing_rect_mm, grid.step_mm, frame.standard.text_small_mm
    )


def compose_drawing(
    project: ProjectModel, catalog: ComponentRegistry, frame: SheetFrame
) -> DrawingGeometry:
    """Dal modello tecnico approvato alla geometria di tutte le tavole."""
    inline_ids = inline_component_ids(project, catalog)
    trunks = build_trunks(project, inline_ids)
    partitions = partition_project(project, trunks)
    return DrawingGeometry(
        project_id=project.metadata.project_id,
        sheets=[
            compose_sheet(project, partition, catalog, frame, inline_ids)
            for partition in partitions
        ],
    )


def compose_on_ordinary_frame(
    project: ProjectModel,
    catalog: ComponentRegistry,
    frames: tuple[SheetFrame, ...] = ORDINARY_FRAMES,
) -> tuple[SheetFrame, DrawingGeometry]:
    """Il disegno sul piu' piccolo formato ordinario su cui entra (D-058).

    «Entrarci» non vuol dire starci a stento: le distanze minime — corridoio di
    instradamento, stacco fra due componenti, gola fra due fasce larga almeno
    quanto gli accessori che la attraversano — sono vincoli del posizionamento,
    non desideri. Se il contenuto le rispetta su una A4, allora quel disegno e'
    davvero piccolo; altrimenti il posizionamento fallisce e si passa all'A3.
    Non serve un secondo criterio a percentuale: sarebbe anche fuorviante,
    perche' lo spazio libero viene distribuito fra le fasce e un disegno riempie
    per costruzione il foglio su cui e' stato composto.
    """
    last: LayoutError | None = None
    for frame in frames:
        try:
            return frame, compose_drawing(project, catalog, frame)
        except LayoutError as exc:
            last = exc
    reason = str(last) if last is not None else "no format was offered to try"
    raise LayoutError(
        f"the plant does not fit on any ordinary sheet format: {reason}"
    ) from last


__all__ = [
    "SheetLink",
    "centre_vertically",
    "compose_drawing",
    "compose_on_ordinary_frame",
    "compose_sheet",
    "inline_component_ids",
]
