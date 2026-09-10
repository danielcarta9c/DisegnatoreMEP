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
from disegnatore_mep.catalog.schema import SERVICE_ORGAN_FUNCTIONS, ComponentTrait
from disegnatore_mep.graphics.symbol import SymbolManifest
from disegnatore_mep.model.project import PortRef, ProjectModel

from .chains import CHAIN_PORT_GAP_MM as CHAIN_PORT_GAP_MM
from .chains import MIN_SPACING_MM as MIN_SPACING_MM
from .chains import SNUG_CLEARANCE_MM as SNUG_CLEARANCE_MM
from .chains import machine_chains
from .errors import LayoutError
from .geometry import (
    PlacedSymbol,
    Point,
    RoutedTrunk,
    intrudes_into,
    moves_of,
    run_intrudes_on,
)
from .grid import Cell, GridSpace
from .route import port_aprons, route_sheet
from .trunks import Trunk

END_CLEARANCE_MM = 5.0
"""Stacco fra un accessorio e il componente all'estremo della propria tratta.

Due passi, il doppio della distanza fra due accessori, e per un motivo diverso.
Fra due accessori basta che si distinguano; contro un componente serve invece
che resti **una colonna libera**, perche' e' da li' che passano le tubazioni che
raggiungono i suoi altri attacchi. Con un passo solo la valvola di sicurezza
della pompa di calore le si e' appoggiata al fianco e ha chiuso il corridoio del
ritorno del primario: l'instradamento e' fallito con una diagnostica che parlava
di tutt'altro.

⚠ **Il PM ha chiesto di abbassarlo** (I-018), e abbassarlo per tutti fu provato
e ritirato: portando questa costante a un passo, sull'impianto 1 i rilievi di
qualita' salivano da sei a nove e gli incroci da 13 a 15. La causa era che una
costante sola non distingue **la valvola che isola una macchina** — quella che
il PM sta guardando — da un accessorio qualunque in mezzo a una tratta.

**Questo stacco resta quello ordinario**; chi isola l'apparecchio che si
manutiene usa invece `SNUG_CLEARANCE_MM` (D-120).
"""

ISOLATING_FUNCTIONS = SERVICE_ORGAN_FUNCTIONS
"""Chi isola, secondo il catalogo e mai secondo il nome (D-090, D-120).

Sono i mestieri che la regola dell'intercettazione assegna: quello comune,
quello bloccabile aperto e il rubinetto della presa strumentale. Un componente
che li dichiara e' li' per fermare l'acqua attorno a un pezzo che si smonta, ed
e' quello che va disegnato **sul suo attacco**. Alla posa non interessa se
quell'organo separi anche un dominio idraulico — quella e' un'altra domanda, e
la fa chi cammina sulla rete: interessa che l'organo appartenga a un pezzo, e
percio' gli stia stretto. L'elenco vive nel catalogo, con chi lo legge per
proporre e per saturare: qui se ne tiene il nome che la posa usa da D-120.
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
    reserved: frozenset[Cell] = frozenset(),
    trunks: list[Trunk] | None = None,
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

    `trunks` sono tutte le tratte del foglio: servono a guardare **oltre un
    raccordo passante** per sapere se al capo di questa tratta, attraverso il
    raccordo, sta un pezzo che si manutiene (DRAW-005, I-035). Senza, la valvola
    che isola l'accumulo restava a mezza strada, perche' la sua tratta finiva
    sul raccordo della sicurezza e non sull'accumulo.
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

    # **Chi isola una macchina si disegna sul suo attacco** (D-120), e da
    # DRAW-005-R1 con lui tutta la **catena della macchina** (I-044). Lo dice il
    # catalogo da due lati e mai il nome del pezzo: la funzione di chi ferma
    # l'acqua, e la proprieta' `maintainable` di cio' che si smonta in
    # esercizio — la stessa che la regola dell'intercettazione legge per
    # chiedere quella valvola. La catena e' la fila dei pezzi in linea che
    # parte dalla porta del pezzo che si manutiene fino al primo organo di
    # chiusura compreso: il filtro a Y e la sua valvola sul ritorno della pompa
    # di calore, o la sola valvola dove non c'e' altro. Si posa a **distanze
    # fisse** dalla porta, sul **primo rettilineo** che ne parte, prima della
    # prima curva: due macchine uguali con la stessa catena hanno la stessa
    # geometria locale, anche se una catena ruota, e una posa in cui la catena
    # non ci sta non e' una candidata.
    isolates = [
        bool(ISOLATING_FUNCTIONS & set(item.definition.functions)) for item in resolved
    ]
    serviced = [
        item.definition.has_trait(ComponentTrait.MAINTAINABLE) for item in resolved
    ]

    def services(ref: PortRef) -> bool:
        """Al di la' di questo capo c'e' un pezzo che si manutiene.

        Si guarda **attraverso i raccordi passanti** (I-035): la sicurezza
        dell'accumulo pende da un raccordo sulla sua mandata, e la tratta della
        valvola finisce sul raccordo, non sull'accumulo. Il raccordo e' l'unico
        organo che per funzione resta fra la valvola e l'attacco: la valvola si
        stringe a lui, cioe' all'attacco. La camminata attraversa un raccordo
        solo se il percorso vi prosegue in una direzione sola; una ripartizione
        la ferma, perche' oltre di lei i volumi sono due.
        """
        seen: set[str] = set()
        cursor = ref
        while cursor.component_id not in seen:
            seen.add(cursor.component_id)
            definition_id = definitions.get(cursor.component_id)
            if definition_id is None:
                return False
            definition = catalog.resolve(definition_id).definition
            if definition.has_trait(ComponentTrait.MAINTAINABLE):
                return True
            if not definition.is_a_fitting or trunks is None:
                return False
            onward = [
                port.id
                for port in definition.ports
                if not port.off_the_run and port.id != cursor.port_id
            ]
            if len(onward) != 1:
                return False
            beyond = PortRef(component_id=cursor.component_id, port_id=onward[0])
            following = [
                item for item in trunks if beyond in (item.start, item.end)
            ]
            if len(following) != 1:
                return False
            cursor = following[0].end if following[0].start == beyond else following[0].start
        return False

    last = len(resolved) - 1

    # La catena della macchina la legge `chains.py`, lo stesso modulo da cui
    # l'instradatore ha letto quanto rettilineo lasciarle dalla porta: i due
    # devono vedere la stessa catena. Dove il capo e' un raccordo passante
    # (I-035) vale invece la posa morbida: il solo organo, stretto al raccordo.
    head_ids, tail_ids = machine_chains(project, catalog, trunk)
    position = {component_id: index for index, component_id in enumerate(trunk.inline_component_ids)}
    strict_head, strict_tail = bool(head_ids), bool(tail_ids)
    head_chain = [position[item] for item in head_ids]
    tail_chain = [position[item] for item in tail_ids]
    if not strict_head and isolates[0] and services(trunk.start):
        head_chain = [0]
    if not strict_tail and isolates[last] and services(trunk.end):
        tail_chain = [last]
    if set(head_chain) & set(tail_chain):
        head_chain = []
    chained = set(head_chain) | set(tail_chain)

    # Lo stacco che ciascun accessorio pretende **prima di se'**. Vale un passo
    # fra due accessori qualunque; scende a zero — e resta allora il solo passo
    # che chi lo precede si tiene dietro — fra chi isola e l'apparecchio in
    # linea che isola. Dopo di se' lo stacco e' sempre un passo, e non c'e' un
    # secondo elenco: uno solo dei due margini varia, e tenerne due darebbe una
    # simmetria apparente.
    leads = [MIN_SPACING_MM] * len(resolved)
    for index in range(1, len(resolved)):
        pair = (isolates[index] and serviced[index - 1]) or (
            serviced[index] and isolates[index - 1]
        )
        if pair:
            leads[index] = 0.0

    # Un accessorio va posato al **centro di un tratto rettilineo** abbastanza
    # lungo da contenerlo, non a una frazione arbitraria della lunghezza: se la
    # rotta piega accanto a lui, il moncone che resta gli passa dentro il
    # riquadro, e la linea risulta disegnata sotto il simbolo.
    raw_straights = _straight_stretches(points)
    moves = moves_of(points)
    if not moves:
        raise LayoutError(
            f"run {trunk.connection_ids[0]} has no straight stretch to sit an "
            f"accessory on"
        )

    def stretches(head_mm: float, tail_mm: float) -> list[tuple[float, float]]:
        """I rettilinei disponibili, tenendo i due capi liberi di quanto detto."""
        found = [
            (max(low, head_mm), min(high, total - tail_mm))
            for low, high in raw_straights
        ]
        return [item for item in found if item[1] > item[0]]

    placed: list[PlacedSymbol] = []
    cuts: list[tuple[float, float]] = []
    step = grid.step_mm

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

    def clear_of_port_thresholds(origin: Point, width: float, height: float) -> bool:
        """Non si siede sulla soglia di un attacco (D-113).

        Davanti a ogni attacco c'e' una cella sola, la sua unica uscita.
        Occuparla lo mura, e la tratta che ci arriva non si instrada piu' — ne'
        su questo foglio ne' su uno piu' grande, perche' non e' una questione di
        spazio. E' successo sul collettore del pavimento radiante: la valvola
        della prima zona si e' seduta sotto l'attacco della seconda.
        """
        if not reserved:
            return True
        low = grid.to_cell(origin.x_mm, origin.y_mm)
        high = grid.to_cell(origin.x_mm + width, origin.y_mm + height)
        return not any(
            (col, row) in reserved
            for col in range(low[0], high[0] + 1)
            for row in range(low[1], high[1] + 1)
        )

    def clear_of_other_runs(origin: Point, width: float, height: float) -> bool:
        """Nessuna tratta gia' disegnata gli passa addosso o a filo (B5, D-027)."""
        if not others:
            return True
        box = (origin.x_mm, origin.y_mm, origin.x_mm + width, origin.y_mm + height)
        return not run_intrudes_on(box, others, clearance)

    def turned_for(
        manifest: SymbolManifest, horizontal: bool
    ) -> tuple[int, SymbolManifest]:
        """La giacitura la da' il tratto; fra le due rotazioni che la danno si
        prende la prima che il simbolo ammette. Un filtro a Y ammette solo
        quelle in cui il gambo non punta in su (I-031): su una verticale gira
        di 270 gradi, non di 90."""
        wanted = (0, 180) if horizontal else (90, 270)
        allowed = [item for item in wanted if item in manifest.allowed_rotations_deg]
        if not allowed:
            raise LayoutError(
                f"inline accessory {manifest.id} cannot be drawn rotated by "
                f"{wanted[0]} or {wanted[1]} degrees, which the run it sits on "
                f"requires: allowed {sorted(manifest.allowed_rotations_deg)}"
            )
        rotation = allowed[0]
        return rotation, manifest.rotated(rotation)

    def seat(
        index: int, station: _Station, distance: float, rotation: int, turned: SymbolManifest
    ) -> None:
        component_id = trunk.inline_component_ids[index]
        gap = turned.inline_gap_mm or 0.0
        placed.append(
            PlacedSymbol(
                component_id=component_id,
                symbol_id=turned.id,
                rotation_deg=rotation,
                origin=Point(
                    x_mm=station.point.x_mm - turned.width_mm / 2,
                    y_mm=station.point.y_mm - turned.height_mm / 2,
                ),
                width_mm=turned.width_mm,
                height_mm=turned.height_mm,
                tag=tags.get(component_id),
                port_flows=resolved[index].glyph_flows,
            )
        )
        cuts.append((distance - gap / 2, distance + gap / 2))

    def place_softly(index: int, from_end: bool) -> float:
        """L'organo che isola oltre un raccordo passante (I-035): stretto al
        raccordo, al primo nodo di griglia libero dal suo capo, anche oltre una
        curva — come si posava in DRAW-005. Restituisce fin dove arriva."""
        manifest = resolved[index].symbol.manifest
        gap = manifest.inline_gap_mm or 0.0
        lead, trail = MIN_SPACING_MM, MIN_SPACING_MM
        window = (
            list(reversed(stretches(END_CLEARANCE_MM, SNUG_CLEARANCE_MM)))
            if from_end
            else stretches(SNUG_CLEARANCE_MM, END_CLEARANCE_MM)
        )
        for low, high in window:
            first = ceil((low + lead + gap / 2 - 1e-9) / step) * step
            stop = high - trail - gap / 2
            nodes: list[float] = []
            here = first
            while here <= stop + 1e-9:
                nodes.append(here)
                here += step
            for snapped in reversed(nodes) if from_end else nodes:
                station = _station_at(points, snapped)
                rotation, turned = turned_for(manifest, station.horizontal)
                origin = Point(
                    x_mm=station.point.x_mm - turned.width_mm / 2,
                    y_mm=station.point.y_mm - turned.height_mm / 2,
                )
                if (
                    clear_of_symbols(origin, turned.width_mm, turned.height_mm)
                    and clear_of_other_runs(origin, turned.width_mm, turned.height_mm)
                    and clear_of_port_thresholds(origin, turned.width_mm, turned.height_mm)
                ):
                    seat(index, station, snapped, rotation, turned)
                    extent = turned.width_mm if station.horizontal else turned.height_mm
                    edge = snapped + max(gap, extent) / 2
                    return (total - (snapped - max(gap, extent) / 2)) if from_end else edge
        raise LayoutError(
            f"run {trunk.connection_ids[0]} has no straight stretch for "
            f"{manifest.id} against the fitting it isolates through: symbols are "
            f"never shrunk to fit, give the run a longer straight length"
        )

    def place_chain(indices: list[int], from_end: bool, strict: bool) -> float | None:
        """La catena della macchina, a distanze fisse dalla porta, sul primo
        rettilineo che ne parte (I-044). Restituisce fin dove arriva dalla
        porta — il fianco lontano dell'ultimo pezzo — o niente senza catena.

        Il primo pezzo lascia libera la soglia dell'attacco e un passo, come la
        valvola di D-120; ogni pezzo successivo sta a un passo dal precedente.
        Le distanze non dipendono dalla tratta: solo dai pezzi, nell'ordine in
        cui la catena li elenca dalla porta. Se il rettilineo dalla porta alla
        prima curva non li contiene, o il posto fisso e' occupato, la posa non
        e' valida: la catena non si sposta oltre la curva. Senza `strict` — il
        capo e' un raccordo passante — vale la posa morbida di I-035.
        """
        if not indices:
            return None
        if not strict:
            return place_softly(indices[0], from_end)
        low, high = raw_straights[-1] if from_end else raw_straights[0]
        before, after = moves[-1] if from_end else moves[0]
        horizontal = abs(after.y_mm - before.y_mm) <= 1e-9
        owner = (trunk.end if from_end else trunk.start).component_id
        reach = CHAIN_PORT_GAP_MM
        for index in indices:
            manifest = resolved[index].symbol.manifest
            rotation, turned = turned_for(manifest, horizontal)
            extent = turned.width_mm if horizontal else turned.height_mm
            centre = reach + extent / 2
            distance = total - centre if from_end else centre
            if distance - extent / 2 < low - 1e-9 or distance + extent / 2 > high + 1e-9:
                raise LayoutError(
                    f"run {trunk.connection_ids[0]} bends before the chain of {owner} "
                    f"fits on the first straight from its port: {manifest.id} needs the "
                    f"straight to reach {reach + extent:g}mm, it is {high - low:g}mm long"
                )
            if abs(distance / step - round(distance / step)) > 1e-9:
                raise LayoutError(
                    f"run {trunk.connection_ids[0]}: the chain of {owner} would sit "
                    f"off the grid at {distance:g}mm along the run"
                )
            station = _station_at(points, distance)
            origin = Point(
                x_mm=station.point.x_mm - turned.width_mm / 2,
                y_mm=station.point.y_mm - turned.height_mm / 2,
            )
            blocked = [
                what
                for what, free in (
                    ("un simbolo", clear_of_symbols(origin, turned.width_mm, turned.height_mm)),
                    ("una tratta", clear_of_other_runs(origin, turned.width_mm, turned.height_mm)),
                    (
                        "la soglia di un attacco",
                        clear_of_port_thresholds(origin, turned.width_mm, turned.height_mm),
                    ),
                )
                if not free
            ]
            if blocked:
                raise LayoutError(
                    f"run {trunk.connection_ids[0]}: the fixed place of {manifest.id} in "
                    f"the chain of {owner}, at ({origin.x_mm:g}, {origin.y_mm:g}), is "
                    f"taken by {' e '.join(blocked)}, and a chain does not slide: "
                    f"give the machine room on its port"
                )
            seat(index, station, distance, rotation, turned)
            reach += extent + MIN_SPACING_MM
        return reach - MIN_SPACING_MM

    head_reach = place_chain(head_chain, from_end=False, strict=strict_head)
    tail_reach = place_chain(tail_chain, from_end=True, strict=strict_tail)

    # Il resto della fila si posa come sempre, avanzando dal cursore: dopo la
    # catena di testa, e prima di quella di coda, a un passo da ciascuna.
    head_mm = head_reach if head_reach is not None else END_CLEARANCE_MM
    tail_mm = tail_reach if tail_reach is not None else END_CLEARANCE_MM
    remaining = [index for index in range(len(resolved)) if index not in chained]
    if remaining and not stretches(head_mm, tail_mm):
        raise LayoutError(
            f"run {trunk.connection_ids[0]} has no straight stretch to sit an "
            f"accessory on"
        )

    # Gli accessori si posano **nell'ordine della catena**, avanzando lungo la
    # tratta: sulla tavola compaiono nell'ordine topologico in cui il fluido
    # li attraversa, che e' l'unico ordine vero. Prima ciascuno prendeva il
    # centro del rettilineo piu' lungo: l'ordine ne usciva rimescolato, e ogni
    # taglio dimezzava la capacita' del rettilineo — su una tratta da quattro
    # accessori di dieci millimetri il quarto non entrava piu' (D-074 ne mette
    # quattro in fila davvero, e li vuole in fila davvero).
    # Il cursore e' **il riquadro piu' il passo**: e' cosi' che riparte dopo
    # ogni pezzo posato, e la catena di testa e' un pezzo posato come gli
    # altri. Senza il passo la coppia di D-120, che rinuncia al proprio
    # passo di testa, si appoggiava al fianco dell'organo della catena.
    cursor = head_reach + MIN_SPACING_MM if head_reach is not None else 0.0

    for index in remaining:
        component = resolved[index]
        manifest = component.symbol.manifest
        gap = manifest.inline_gap_mm or 0.0
        lead, trail = leads[index], MIN_SPACING_MM
        needed = gap + lead + trail
        window = stretches(head_mm, tail_mm)
        found: _Station | None = None
        turned = manifest
        rotation = 0
        distance = 0.0

        for low, high in window:
            # Il primo nodo di griglia da cui l'accessorio sta nel rettilineo,
            # oltre l'accessorio precedente: avanzare invece di spezzare tiene
            # l'ordine e non spreca nemmeno un passo. Se il riquadro casca su
            # un simbolo posato, si avanza di un passo e si riprova.
            first = ceil((max(low, cursor) + lead + gap / 2 - 1e-9) / step) * step
            stop = high - trail - gap / 2
            nodes: list[float] = []
            here = first
            while here <= stop + 1e-9:
                nodes.append(here)
                here += step
            for snapped in nodes:
                station = _station_at(points, snapped)
                rotation, turned = turned_for(manifest, station.horizontal)
                origin = Point(
                    x_mm=station.point.x_mm - turned.width_mm / 2,
                    y_mm=station.point.y_mm - turned.height_mm / 2,
                )
                # **Lo stacco si misura sul riquadro.** La stazione si sceglie
                # sulla lunghezza del taglio, ma il simbolo e' largo il proprio
                # riquadro, che puo' sporgere oltre il taglio da tutt'e due i
                # lati: chi arriva dopo si ritrovava appoggiato al fianco di
                # chi lo precede, e con la coppia di D-120 — che rinuncia al
                # proprio passo di testa — i due arrivavano a toccarsi. Si
                # guarda dove il **riquadro** comincia, non dove comincia
                # l'interruzione.
                extent_here = turned.width_mm if station.horizontal else turned.height_mm
                if snapped - extent_here / 2 < cursor + lead - 1e-9:
                    continue
                if (
                    clear_of_symbols(origin, turned.width_mm, turned.height_mm)
                    and clear_of_other_runs(origin, turned.width_mm, turned.height_mm)
                    and clear_of_port_thresholds(
                        origin, turned.width_mm, turned.height_mm
                    )
                ):
                    found, distance = station, snapped
                    break
            if found is not None:
                break
        if found is None:
            raise LayoutError(
                f"run {trunk.connection_ids[0]} has no straight stretch of "
                f"{needed:g}mm for {component.symbol.manifest.id} that keeps "
                f"{clearance:g}mm clear of the other symbols and runs: symbols are "
                f"never shrunk to fit, give the run a longer straight length"
            )
        # Il cursore riparte dal **riquadro**, non dall'interruzione: un
        # simbolo piu' largo del proprio taglio sporge oltre di esso, e chi
        # viene dopo gli si appoggiava al fianco. Con la coppia di D-120, che
        # chiede un passo secco, i due si toccavano e sulla carta si leggevano
        # come un pezzo solo.
        extent = turned.width_mm if found.horizontal else turned.height_mm
        cursor = distance + max(gap, extent) / 2 + trail
        seat(index, found, distance, rotation, turned)

    # I simboli escono nell'ordine della tratta, comunque siano stati posati.
    order = {component_id: index for index, component_id in enumerate(trunk.inline_component_ids)}
    placed.sort(key=lambda item: order[item.component_id])
    cuts.sort()

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

    # **E la propria tratta non deve rientrare nel riquadro di un accessorio.**
    # Il taglio toglie il pezzo di linea che passa **per** il simbolo, ma una
    # spezzata che piega li' accanto puo' rientrare nel riquadro da un altro
    # lato, e allora la linea e' disegnata sotto il simbolo esattamente come se
    # non fosse stata interrotta. Si guarda **dopo** il taglio, perche' prima
    # ogni posizione sarebbe intrusa dalla linea che il simbolo sta per
    # interrompere; e si guarda con la stessa misura del cancello, o si
    # approverebbe una posa che la tavola poi rifiuta.
    trimmed = routed.model_copy(update={"segments": segments})
    for item in placed:
        box = (item.origin.x_mm, item.origin.y_mm, item.right_mm, item.bottom_mm)
        for part in segments:
            if any(
                intrudes_into(box, before, after) for before, after in moves_of(part)
            ):
                raise LayoutError(
                    f"run {trunk.connection_ids[0]} still passes under "
                    f"{item.symbol_id} after breaking for it: the accessory sits "
                    f"where its own run bends back into it, give the run a longer "
                    f"straight length"
                )
    return placed, trimmed


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

    reserved = frozenset(
        port_aprons(project, list(trunks), placed, catalog, grid).values()
    )

    def settle(trunk: Trunk, route: RoutedTrunk) -> list[PlacedSymbol]:
        try:
            found, pieces = place_inline_accessories(
                project, trunk, route, catalog, grid, symbols, drawn, reserved, list(trunks)
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
