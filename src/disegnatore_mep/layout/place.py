"""Dove va posato ciascun componente, che e' meta' della partita.

Il PM, guardando la prima tavola: «Sulle linee delle tubazioni e sulla
posizione delle apparecchiature si gioca la vera partita. La regola e'
minimizzare le curve disegnate, minimizzare gli attraversamenti tra linee e
minimizzare la lunghezza delle linee mantenendo pero' ordinamenti da sinistra a
destra.» E l'esempio: «Hai messo il circolatore in un punto e per far entrare la
linea hai fatto sali-scendi; bastava spostare tutte le apparecchiature a destra
e guadagnavi lo spazio che serviva.»

Le tre voci le paga l'instradamento, ma chi le rende pagabili e' il
posizionamento: una piega non si toglie instradando meglio, se i due attacchi
che collega stanno a quote diverse. Da qui tre regole.

**L'ordine da sinistra a destra e' quello del processo.** Le fasce funzionali
(D-041) lo danno all'ingrosso; dentro una fascia lo da' la profondita' lungo la
mandata, e i rami senza seguito precedono la dorsale che prosegue. Prima si
ordinava per profondita' topologica misurata da una sorgente qualsiasi, che in
un circuito chiuso non esiste: la valvola deviatrice finiva a sinistra della
pompa di calore che la alimenta.

**Dentro una fascia il cursore orizzontale e' uno solo.** Prima ce n'era uno per
livello, cosi' una valvola a mezz'aria poteva stare esattamente sopra la
macchina che la alimenta: geometricamente valido, e nessun ordine leggibile.

**Chi sta su una tubazione si allinea all'attacco che lo alimenta.** Portare il
proprio attacco d'ingresso sulla quota di chi lo serve toglie due pieghe per
componente, ed e' quello che un tecnico fa senza pensarci.

Gli accessori in linea **non** vengono posati qui: appartengono alla tratta su
cui stanno, e li posa `inline.py` dopo l'instradamento (D-027).
"""

from collections import defaultdict

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import Rect, SheetFrame
from disegnatore_mep.graphics.symbol import PortFace, SymbolManifest
from disegnatore_mep.model.project import PortRef, ProjectModel
from disegnatore_mep.model.types import BandRole

from .composition import Standing, levels_of, standing_of
from .errors import LayoutError
from .flow import orient_trunks
from .geometry import PlacedSymbol, Point
from .grid import GridSpace
from .inline import MIN_SPACING_MM
from .partition import SheetPartition

BAND_GUTTER_MM = 10.0
"""Distanza minima fra due fasce funzionali contigue."""

MAX_EXTRA_GUTTER_MM = 30.0
"""Quanto si allarga al massimo una gola quando sul foglio avanza spazio.

Lo spazio libero non si lascia tutto a destra: si distribuisce fra le fasce,
perche' e' li' che passano le tubazioni e stanno gli accessori in linea. E'
la mossa che il PM ha indicato — «bastava spostare tutte le apparecchiature a
destra e guadagnavi lo spazio che serviva» — resa sistematica. Il tetto evita
che un impianto di tre pezzi si stiri per mezza tavola.
"""

ROW_GAP_MM = 5.0
"""Distanza minima fra due componenti affiancati o sovrapposti."""

ROUTING_MARGIN_MM = 10.0
"""Corridoio libero fra il bordo dell'area di disegno e la prima fascia.

Senza, un simbolo appoggiato al bordo sinistro ha le proprie porte rivolte a
sinistra irraggiungibili: la rotta dovrebbe arrivare da fuori pagina. Quattro
passi di griglia su ciascun lato, cosi' l'area utile al posizionamento resta
un multiplo esatto del passo.
"""

_HORIZONTAL_FACES = (PortFace.LEFT, PortFace.RIGHT)


def _band_by_subsystem(project: ProjectModel, sheet_id: str) -> dict[str, BandRole]:
    for sheet in project.sheets:
        if sheet.id == sheet_id:
            return {item.subsystem_id: item.band for item in sheet.band_assignments}
    return {}


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
    # cui misurare una profondita' assoluta.
    if project.subsystems:
        for index, subsystem in enumerate(project.subsystems):
            role = roles[min(index, len(roles) - 1)]
            for component_id in subsystem.component_ids:
                bands[component_id] = role
        for component_id in placeable:
            bands.setdefault(component_id, roles[-1])
        return bands

    for component_id in placeable:
        bands[component_id] = roles[0]
    return bands


class _Process:
    """L'ordine del processo lungo la mandata: chi viene prima di chi.

    Si costruisce sulle tratte gia' orientate (D-059), quindi legge il verso
    reale del fluido e non la geometria di un disegno che ancora non esiste.
    """

    def __init__(
        self,
        project: ProjectModel,
        partition: SheetPartition,
        catalog: ComponentRegistry,
    ) -> None:
        trunks = list(partition.trunks)
        oriented = orient_trunks(project, catalog, trunks)
        self.feed: dict[str, tuple[PortRef, PortRef]] = {}
        successors: dict[str, list[str]] = defaultdict(list)
        members: set[str] = set()
        for trunk in trunks:
            members.update({trunk.start.component_id, trunk.end.component_id})
            if oriented.get(trunk.connection_ids) is not True:
                continue
            source, target = trunk.start.component_id, trunk.end.component_id
            if source == target:
                continue
            successors[source].append(target)
            self.feed.setdefault(target, (trunk.start, trunk.end))

        self.depth = dict.fromkeys(members, 0)
        # Rilassamento sul cammino piu' lungo. Il grafo di mandata e' aciclico
        # per costruzione — l'anello si chiude sui ritorni — ma il numero di
        # passate resta limitato, perche' un modello sbagliato non deve
        # bloccare il disegno.
        for _ in range(len(members)):
            changed = False
            for source in sorted(successors):
                for target in sorted(successors[source]):
                    if self.depth[target] <= self.depth[source]:
                        self.depth[target] = self.depth[source] + 1
                        changed = True
            if not changed:
                break

        self.downstream: dict[str, int] = {}
        for component_id in members:
            seen: set[str] = set()
            frontier = list(successors[component_id])
            while frontier:
                current = frontier.pop()
                if current in seen:
                    continue
                seen.add(current)
                frontier.extend(successors[current])
            self.downstream[component_id] = len(seen)

    def order_of(self, component_id: str) -> tuple[int, int, str]:
        """Piu' e' a valle piu' sta a destra; a pari profondita' prima i rami morti."""
        return (
            self.depth.get(component_id, 0),
            self.downstream.get(component_id, 0),
            component_id,
        )


def _port_of(manifest: SymbolManifest, port_id: str) -> tuple[float, float, PortFace]:
    for port in manifest.ports:
        if port.id == port_id:
            return port.x_mm, port.y_mm, port.face
    raise LayoutError(
        f"symbol {manifest.id} has no port {port_id}: the catalogue definition and "
        f"the symbol manifest disagree on the component's connections"
    )


def _outward(distance: int) -> tuple[int, ...]:
    """0, 1, -1, 2, -2, ...: la quota esatta, poi le piu' vicine."""
    return (0,) if distance == 0 else (distance, -distance)


def _slots(
    order: list[str],
    feeder_of: dict[str, str],
    stackable: dict[str, bool],
) -> list[list[str]]:
    """Raggruppa in colonne: i rami paralleli si impilano invece di affiancarsi.

    Due zone servite dallo stesso collettore sono lo stesso passo del processo,
    non due passi in fila: metterle una sopra l'altra e' come le disegna
    chiunque, accorcia la tavola e ne usa l'altezza, che altrimenti resta
    bianca. Vale solo per chi sta su una tubazione: due accumuli appoggiati a
    terra non si possono impilare, e restano affiancati.
    """
    slots: list[list[str]] = []
    for component_id in order:
        feeder = feeder_of.get(component_id)
        same_branch = (
            slots
            and stackable.get(component_id, False)
            and stackable.get(slots[-1][-1], False)
            and feeder is not None
            and feeder_of.get(slots[-1][-1]) == feeder
        )
        if same_branch:
            slots[-1].append(component_id)
        else:
            slots.append([component_id])
    return slots


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

    placeable = [
        item for item in partition.component_ids if item not in inline_component_ids
    ]
    if not placeable:
        raise LayoutError(
            f"sheet {partition.sheet_id} carries only inline accessories: an "
            f"accessory sits on a run, so there is nothing to draw it against"
        )

    bands = _assign_bands(project, partition, placeable)
    tags = {item.id: item.tag for item in project.components}
    process = _Process(project, partition, catalog)
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

    resolved = {
        item: catalog.resolve(
            next(c.definition_id for c in project.components if c.id == item)
        )
        for item in placeable
    }

    def rotation_for(component_id: str) -> int:
        allowed = resolved[component_id].symbol.manifest.allowed_rotations_deg
        return 0 if 0 in allowed else min(allowed)

    manifests = {
        item: resolved[item].symbol.manifest.rotated(rotation_for(item))
        for item in placeable
    }
    standings = {
        item: standing_of(
            manifests[item].height_mm,
            frozenset(resolved[item].definition.functions),
            resolved[item].is_inline,
        )
        for item in placeable
    }

    columns: dict[BandRole, list[str]] = defaultdict(list)
    for component_id in placeable:
        columns[bands[component_id]].append(component_id)
    for role in columns:
        columns[role].sort(
            key=lambda item: (
                order_hint.get(subsystem_of.get(item, ""), 0),
                *process.order_of(item),
            )
        )

    def snap_up(value_mm: float, origin_mm: float) -> float:
        """Il primo nodo di griglia non prima di `value_mm`.

        Misurato **dall'origine dell'area di disegno**, non dallo zero del
        foglio: l'area comincia a 16 mm dal bordo, che non e' un multiplo del
        passo, e snappare in assoluto porterebbe fuori griglia ogni simbolo.
        """
        offset = value_mm - origin_mm
        steps = int(offset / step) + (1 if offset % step > 1e-9 else 0)
        return origin_mm + step * steps

    def on_grid(value_mm: float, origin_mm: float) -> float:
        return origin_mm + round((value_mm - origin_mm) / step) * step

    used_roles = [role for role in BandRole if columns.get(role)]
    feeder_of = {
        component_id: feed[0].component_id
        for component_id, feed in process.feed.items()
    }
    stackable = {item: standings[item] is Standing.RAIL for item in placeable}
    slots = {role: _slots(columns[role], feeder_of, stackable) for role in used_roles}
    # Un solo cursore per fascia: la fascia e' larga quanto le sue colonne in
    # fila, qualunque quota occupino, e una colonna e' larga quanto il suo
    # pezzo piu' largo.
    widths = {
        role: snap_up(
            area.x_mm
            + sum(max(manifests[item].width_mm for item in slot) for slot in slots[role])
            + ROW_GAP_MM * (len(slots[role]) - 1),
            area.x_mm,
        )
        - area.x_mm
        for role in used_roles
    }

    # Una gola non e' larga soltanto per estetica: e' li' che corrono le tratte
    # fra una fascia e l'altra, e su quelle tratte stanno gli accessori in
    # linea. Se un circolatore vuole quindici millimetri di rettilineo, la gola
    # che la sua tratta attraversa deve poterglieli dare, altrimenti il foglio
    # fallisce dopo l'instradamento con l'accessorio senza posto.
    gutters = [BAND_GUTTER_MM] * max(len(used_roles) - 1, 0)
    position_of = {role: index for index, role in enumerate(used_roles)}
    for trunk in partition.trunks:
        if not trunk.inline_component_ids:
            continue
        edges = [
            position_of.get(bands.get(item.component_id, BandRole.GENERATION), -1)
            for item in (trunk.start, trunk.end)
        ]
        if -1 in edges or edges[0] == edges[1]:
            continue
        needed = sum(
            (catalog.resolve(item.definition_id).symbol.manifest.inline_gap_mm or 0.0)
            + 2 * MIN_SPACING_MM
            for item in project.components
            if item.id in trunk.inline_component_ids
        )
        for index in range(min(edges), max(edges)):
            gutters[index] = max(gutters[index], snap_up(needed, 0.0))

    total = sum(widths.values()) + sum(gutters)
    if total > area.width_mm + 1e-9:
        raise LayoutError(
            f"the {len(used_roles)} functional bands need {total:g}mm but the drawing "
            f"area is {area.width_mm:g}mm wide: symbols are never shrunk to fit, "
            f"split the plant across more sheets"
        )
    if gutters:
        spare = (area.width_mm - total) / len(gutters)
        extra = min(int(spare / step) * step, MAX_EXTRA_GUTTER_MM)
        gutters = [item + extra for item in gutters]

    # Le quote si misurano sull'**area di disegno**, non sul rettangolo ridotto
    # in cui si impaccano le fasce: il corridoio di instradamento restringe
    # dove si posa, non dove passa la linea di terra.
    levels = levels_of(drawing.y_mm, drawing.height_mm, step)
    placed: list[PlacedSymbol] = []
    boxes: list[tuple[float, float, float, float]] = []

    def free_of_symbols(left: float, top: float, width: float, height: float) -> bool:
        return not any(
            left < x1 + ROW_GAP_MM
            and x0 - ROW_GAP_MM < left + width
            and top < y1 + ROW_GAP_MM
            and y0 - ROW_GAP_MM < top + height
            for x0, y0, x1, y1 in boxes
        )

    def corridor_is_clear(from_x: float, to_x: float, row: float) -> bool:
        """Nessun simbolo gia' posato taglia il rettilineo che porta all'attacco.

        Il bordo del riquadro conta come dentro, perche' cosi' lo tratta
        l'instradamento: una corsia che passa esattamente sul filo di un
        simbolo per lui e' occupata, e la linea diritta che qui si credeva di
        aver trovato diventa un gomito in piu'.
        """
        low, high = min(from_x, to_x), max(from_x, to_x)
        return not any(
            y0 <= row <= y1 and x0 < high and low < x1 for x0, y0, x1, y1 in boxes
        )

    def aligned_top(component_id: str, left: float, floor: float) -> float | None:
        """La quota che porta l'attacco d'ingresso sulla linea che lo alimenta."""
        feed = process.feed.get(component_id)
        if feed is None:
            return None
        source, target = feed
        feeder = next(
            (item for item in placed if item.component_id == source.component_id), None
        )
        source_manifest = manifests.get(source.component_id)
        if feeder is None or source_manifest is None:
            return None
        source_x, source_y, source_face = _port_of(source_manifest, source.port_id)
        _, target_y, target_face = _port_of(manifests[component_id], target.port_id)
        if target_face not in _HORIZONTAL_FACES:
            return None
        exit_y = feeder.origin.y_mm + source_y
        if source_face is PortFace.BOTTOM:
            exit_y += step
        elif source_face is PortFace.TOP:
            exit_y -= step
        exit_x = feeder.origin.x_mm + source_x
        wanted = on_grid(max(exit_y - target_y, floor), area.y_mm)
        manifest = manifests[component_id]
        # Si prova la quota esatta, poi quelle sempre piu' lontane: se un altro
        # componente sta gia' li', o gli sta in mezzo, la linea diritta non c'e'
        # comunque, e tanto vale cercarla dove c'e' posto.
        for distance in range(int(area.height_mm / step)):
            for offset in _outward(distance):
                top = wanted + offset * step
                if top < area.y_mm - 1e-9 or top < floor - 1e-9:
                    continue
                if top + manifest.height_mm > levels.ground_mm + 1e-9:
                    continue
                if not free_of_symbols(left, top, manifest.width_mm, manifest.height_mm):
                    continue
                if not corridor_is_clear(exit_x, left, top + target_y):
                    continue
                return top
        return None

    x_mm = area.x_mm
    for role in used_roles:
        cursor = x_mm
        for slot in slots[role]:
            left = on_grid(cursor, area.x_mm)
            floor = area.y_mm
            for component_id in slot:
                manifest = manifests[component_id]
                if standings[component_id] is Standing.GROUND:
                    top = on_grid(levels.ground_mm - manifest.height_mm, area.y_mm)
                else:
                    found = aligned_top(component_id, left, floor)
                    if found is None:
                        fallback = (
                            levels.auxiliary_mm
                            if standings[component_id] is Standing.AUXILIARY
                            else levels.lower_supply_mm - manifest.height_mm / 2
                        )
                        found = on_grid(max(fallback, floor), area.y_mm)
                        while (
                            not free_of_symbols(
                                left, found, manifest.width_mm, manifest.height_mm
                            )
                            and found + manifest.height_mm < levels.ground_mm
                        ):
                            found += ROW_GAP_MM
                    top = found
                if (
                    top < area.y_mm - 1e-9
                    or top + manifest.height_mm > area.bottom_mm + 1e-9
                ):
                    raise LayoutError(
                        f"component {component_id} does not fit between the drawing "
                        f"area and the ground line: symbols are never shrunk to fit"
                    )
                placed.append(
                    PlacedSymbol(
                        component_id=component_id,
                        symbol_id=manifest.id,
                        rotation_deg=rotation_for(component_id),
                        origin=Point(x_mm=left, y_mm=top),
                        width_mm=manifest.width_mm,
                        height_mm=manifest.height_mm,
                        tag=tags.get(component_id),
                    )
                )
                boxes.append(
                    (left, top, left + manifest.width_mm, top + manifest.height_mm)
                )
                # Il prossimo della colonna sta sotto questo, non accanto.
                floor = top + manifest.height_mm + ROW_GAP_MM
            cursor = left + max(manifests[item].width_mm for item in slot) + ROW_GAP_MM
        x_mm += widths[role]
        if position_of[role] < len(gutters):
            x_mm += gutters[position_of[role]]

    return placed
