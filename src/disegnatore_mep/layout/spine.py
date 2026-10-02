"""La semina: chi non e' nel piano segue il pezzo a cui e' appeso.

`carry_the_rest` porta dietro a ogni pezzo posato cio' che gli e' appeso — gli
organi di servizio, gli stacchi — e la usa ogni giorno
`disegnatore_mep.piano.esecutore`. `SpineLayout` e `SpineRun` sono le strutture
che la semina riceve: l'esecutore gliene passa una costruita dal piano.

**Che cosa c'era, e non c'e' piu'.** Questo modulo ospitava la **fase del
tronco**, `lay_the_spine`: cercava la posa delle autostrade risolvendo un
sistema di vincoli. **D-151** (20 settembre 2026) l'ha tolta dalla decisione —
il disegno lo compone un agente, e le autostrade le tira dritte il piano, con il
controllo **B1** (`validation/regole.py::autostrade_storte`) a verificarle — e il
2 ottobre 2026, col via libera del PO (I-180), il codice e' stato tolto insieme a
`layout/improve.py` e `layout/dilate.py`. Resta nella storia di git.
"""

from dataclasses import dataclass

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import SheetFrame
from disegnatore_mep.graphics.symbol import PortFace
from disegnatore_mep.model.project import ProjectModel

from .flow import TrunkKey
from .geometry import PlacedSymbol, Point, RoutedTrunk
from .partition import SheetPartition
from .place import (
    hanging_children,
    hanging_ports,
)
from .trunks import Trunk

_TOLERANCE_MM = 1e-6


_HORIZONTAL_FACES = (PortFace.LEFT, PortFace.RIGHT)

_DIRECTION: dict[PortFace, tuple[float, float]] = {
    PortFace.RIGHT: (1.0, 0.0),
    PortFace.BOTTOM: (0.0, 1.0),
    PortFace.LEFT: (-1.0, 0.0),
    PortFace.TOP: (0.0, -1.0),
}


@dataclass(frozen=True)
class SpineRun:
    """Una tratta dell'autostrada, com'e' uscita dalla fase del tronco."""

    key: TrunkKey
    horizontal: bool
    """Giacitura della retta che unisce le due porte."""

    straight: bool
    """Vero se la tratta e' un rettilineo: una spezzata sola, senza pieghe."""

    possible: bool
    """Vero se le due porte si guardano nelle pose che la fase ha scelto.

    Falso vuol dire che, **dato il resto del tronco**, nessuna posa ammessa del
    pezzo a valle mette la sua porta di fronte a quella da cui si arriva: la
    tratta sara' un gomito, e non per un difetto della posa.
    """


@dataclass(frozen=True)
class SpineLayout:
    """L'esito della fase del tronco: la forma, e chi vi ha partecipato.

    `symbols` porta **soltanto** i partecipanti e `routes` **soltanto** le
    autostrade: e' la geometria della fase, non della tavola. Chi la riceve la
    usa come vincolo, non come disegno.
    """

    machines: frozenset[str]
    participants: tuple[str, ...]
    trunks: tuple[Trunk, ...]
    symbols: tuple[PlacedSymbol, ...]
    routes: tuple[RoutedTrunk, ...]
    runs: tuple[SpineRun, ...]
    routed: bool = True
    """Vero se le autostrade della fase si sono lasciate disegnare.

    Falso vuol dire che la forma c'e' — `symbols` la porta — ma le sue linee
    non si sono instradate su un foglio ancora privo di corredo. Non e' una
    ragione per buttare la fase (§F): e' una ragione per dichiararlo.
    """

    @property
    def crooked(self) -> tuple[TrunkKey, ...]:
        """Le autostrade che sono uscite con almeno una piega."""
        return tuple(run.key for run in self.runs if not run.straight)

    @property
    def impossible(self) -> tuple[TrunkKey, ...]:
        """Le autostrade che, dato il resto del tronco, nessuna posa raddrizza."""
        return tuple(run.key for run in self.runs if not run.possible)

    @property
    def is_straight(self) -> bool:
        """Vero se ogni autostrada che poteva essere rettilinea lo e'."""
        return all(run.straight or not run.possible for run in self.runs)


def carry_the_rest(
    project: ProjectModel,
    partition: SheetPartition,
    catalog: ComponentRegistry,
    placed: list[PlacedSymbol],
    layout: SpineLayout,
    frame: SheetFrame | None = None,
) -> list[PlacedSymbol]:
    """La posa del resto che parte dal tronco (architettura §5).

    Chi non ha partecipato alla fase del tronco non resta dov'era: **segue per
    il grafo** il partecipante da cui dipende, della stessa traslazione. Non
    per vicinanza sul foglio — l'utilizzatore che sta a due centimetri da un
    raccordo non e' per questo attaccato a lui — ma per come l'impianto e'
    fatto: dal partecipante si cammina lungo le tubazioni e si porta con se'
    tutto quel che si incontra.

    E chi **pende** da un partecipante che la fase ha girato non si trasla: si
    riappende. Un manometro appeso al raccordo del ritorno, quando il raccordo
    gira il proprio stacco verso il basso, va sotto — e restarsene sopra
    significherebbe consegnare una figura spezzata.

    Con `frame`, una figura riappesa che finirebbe **fuori dall'area di disegno**
    accorcia il proprio stacco finche' ci rientra, fino al minimo di un passo.
    Il tronco si sposta guardando i soli partecipanti (`_into_the_area`), e
    quando scende porta con se' cio' che gli pende: una figura profonda — dal
    raccordo il gruppo di riempimento, dal gruppo il proprio ingresso — arriva
    piu' in basso di chi la regge, ed e' uscita dal foglio. Fuori dal foglio una
    tratta non si instrada, e la fase consegnava una posa che non si poteva
    nemmeno misurare.

    E' una prima ipotesi, non una posa finale: a sistemarla sono le fasi del
    corredo e delle strade di servizio.
    """
    if not layout.symbols:
        return list(placed)
    moved = {item.component_id: item for item in layout.symbols}
    before = {item.component_id: item for item in placed}
    delta = {
        component_id: (
            item.origin.x_mm - before[component_id].origin.x_mm,
            item.origin.y_mm - before[component_id].origin.y_mm,
        )
        for component_id, item in moved.items()
        if component_id in before
    }
    if not delta:
        return list(placed)
    children = hanging_children(project, partition, catalog, frozenset(before))
    hung = {
        child: (parent, port_id)
        for parent, items in children.items()
        for child, port_id in items
    }
    own_ports = hanging_ports(project, partition, catalog, frozenset(before))
    following = _followers(partition, frozenset(before), delta)
    definitions = {item.id: item.definition_id for item in project.components}

    def carried(item: PlacedSymbol) -> PlacedSymbol:
        step = following.get(item.component_id)
        if step is None:
            return item
        dx, dy = step
        return item.model_copy(
            update={
                "origin": Point(x_mm=item.origin.x_mm + dx, y_mm=item.origin.y_mm + dy)
            }
        )

    settled: dict[str, PlacedSymbol] = {}
    for item in placed:
        component_id = item.component_id
        if component_id in moved:
            settled[component_id] = moved[component_id]
        elif component_id not in hung:
            settled[component_id] = carried(item)
    # **La figura si riappende tutta, dall'alto in basso.** Una figura puo'
    # essere profonda — dal raccordo pende il gruppo di riempimento e dal gruppo
    # pende il proprio ingresso — e fermarsi al primo livello lasciava il nipote
    # a seguire il grafo per conto suo: padre e figlio prendevano due
    # traslazioni diverse e la figura si spezzava, senza che nessun vincolo se
    # ne accorgesse.
    changed = True
    while changed:
        changed = False
        for item in placed:
            component_id = item.component_id
            if component_id in settled:
                continue
            link = hung.get(component_id)
            if link is None or link[0] not in settled:
                continue
            hung_now = _rehung(
                item,
                settled[link[0]],
                link[1],
                before[link[0]],
                catalog,
                definitions,
                own_ports.get(component_id),
            )
            settled[component_id] = _inside(
                hung_now,
                settled[link[0]],
                link[1],
                catalog,
                definitions,
                own_ports.get(component_id),
                frame,
            )
            changed = True
    for item in placed:
        settled.setdefault(item.component_id, carried(item))
    return [settled[item.component_id] for item in placed]


def _inside(
    child: PlacedSymbol,
    parent: PlacedSymbol,
    port_id: str,
    catalog: ComponentRegistry,
    definitions: dict[str, str],
    own_port_id: str | None,
    frame: SheetFrame | None,
) -> PlacedSymbol:
    """L'appeso riportato dentro l'area, accorciando il proprio stacco.

    Si accorcia un passo per volta, e non si scende sotto un passo: uno stacco
    lungo zero metterebbe due simboli a contatto. Se nemmeno cosi' ci sta, si
    lascia dov'e' e la posa si giudica come sempre — cattiva, ma misurabile.
    """
    if frame is None:
        return child
    area = frame.drawing_rect_mm
    step = frame.standard.grid_mm

    def fits(item: PlacedSymbol) -> bool:
        return (
            item.origin.x_mm >= area.x_mm - _TOLERANCE_MM
            and item.origin.y_mm >= area.y_mm - _TOLERANCE_MM
            and item.right_mm <= area.right_mm + _TOLERANCE_MM
            and item.bottom_mm <= area.bottom_mm + _TOLERANCE_MM
        )

    if fits(child):
        return child
    upright = catalog.resolve(definitions[child.component_id]).symbol.manifest
    shape = catalog.resolve(definitions[parent.component_id]).symbol.manifest
    port = shape.rotated(parent.rotation_deg).port(parent.physical_port(port_id))
    mine_id = own_port_id or upright.ports[0].id
    stub = Point(
        x_mm=parent.origin.x_mm + port.x_mm, y_mm=parent.origin.y_mm + port.y_mm
    )
    direction = _DIRECTION[port.face]
    mine = upright.rotated(child.rotation_deg).port(mine_id)
    here = Point(x_mm=child.origin.x_mm + mine.x_mm, y_mm=child.origin.y_mm + mine.y_mm)
    gap = abs(here.x_mm - stub.x_mm) + abs(here.y_mm - stub.y_mm)
    shorter = child
    while gap > step + _TOLERANCE_MM:
        gap -= step
        shorter = child.model_copy(
            update={
                "origin": Point(
                    x_mm=stub.x_mm + direction[0] * gap - mine.x_mm,
                    y_mm=stub.y_mm + direction[1] * gap - mine.y_mm,
                )
            }
        )
        if fits(shorter):
            return shorter
    return shorter


def _followers(
    partition: SheetPartition,
    placeable: frozenset[str],
    delta: dict[str, tuple[float, float]],
) -> dict[str, tuple[float, float]]:
    """Di quanto si sposta chi non ha partecipato alla fase del tronco.

    Si guarda a chi e' **attaccato**: un pezzo collegato a un solo
    partecipante lo segue, perche' e' di quel partecipante che fa parte. Un
    pezzo collegato a due partecipanti che si sono spostati in modo diverso non
    segue nessuno dei due e resta dov'e': non c'e' una risposta giusta, e
    sceglierne una a caso rompe la figura — e' successo alla seconda pompa di
    calore di un impianto in cascata, tirata via dalla propria compagna di
    colonna dietro un raccordo che si era spostato.

    Chi non tocca nessun partecipante eredita dal vicino che lo fa, camminando
    in ampiezza: cosi' un utilizzatore in fondo a una fila segue l'accumulo da
    cui la fila parte.
    """
    edges: dict[str, list[str]] = {}
    for trunk in partition.trunks:
        here, there = trunk.start.component_id, trunk.end.component_id
        if here not in placeable or there not in placeable or here == there:
            continue
        edges.setdefault(here, []).append(there)
        edges.setdefault(there, []).append(here)
    found: dict[str, tuple[float, float]] = {}
    for item in sorted(placeable - frozenset(delta)):
        touched = {
            delta[other] for other in edges.get(item, ()) if other in delta
        }
        if len(touched) == 1:
            found[item] = touched.pop()
    seen = set(delta) | set(found)
    frontier = sorted(found)
    while frontier:
        onward: list[str] = []
        for item in sorted(frontier):
            for other in sorted(edges.get(item, ())):
                if other in seen:
                    continue
                seen.add(other)
                found[other] = found[item]
                onward.append(other)
        frontier = onward
    return found


def _rehung(
    child: PlacedSymbol,
    parent: PlacedSymbol,
    port_id: str,
    was: PlacedSymbol,
    catalog: ComponentRegistry,
    definitions: dict[str, str],
    own_port_id: str | None = None,
) -> PlacedSymbol:
    """L'appeso rimesso dalla parte in cui lo stacco guarda adesso, allo stacco
    di prima: e' la stessa regola con cui il ciclo lo riappende quando gira il
    pezzo che lo regge.

    `own_port_id` e' **il suo** attacco su quello stacco. Non e' sempre il primo
    del manifesto: un ponte fra due reti ne ha due, e riappenderlo per l'altro
    lo manda dalla parte opposta del proprio stacco — con il nipote che gli
    pende addosso a finire in mezzo alla tubazione (DRAW-006-R1, blocco D).
    """
    upright = catalog.resolve(definitions[child.component_id]).symbol.manifest
    shape = catalog.resolve(definitions[parent.component_id]).symbol.manifest
    port = shape.rotated(parent.rotation_deg).port(parent.physical_port(port_id))
    old = shape.rotated(was.rotation_deg).port(was.physical_port(port_id))
    stub = Point(
        x_mm=parent.origin.x_mm + port.x_mm, y_mm=parent.origin.y_mm + port.y_mm
    )
    mine_id = own_port_id or upright.ports[0].id
    own = upright.rotated(child.rotation_deg).port(mine_id)
    gap = abs(
        (was.origin.x_mm + old.x_mm) - (child.origin.x_mm + own.x_mm)
    ) + abs((was.origin.y_mm + old.y_mm) - (child.origin.y_mm + own.y_mm))
    direction = _DIRECTION[port.face]
    wanted = port.face.opposite
    chosen = child.rotation_deg
    for degrees in sorted(
        upright.allowed_rotations_deg,
        key=lambda item: (item != child.rotation_deg, item),
    ):
        if upright.rotated(degrees).port(mine_id).face is wanted:
            chosen = degrees
            break
    turned = upright.rotated(chosen)
    mine = turned.port(mine_id)
    return child.model_copy(
        update={
            "origin": Point(
                x_mm=stub.x_mm + direction[0] * gap - mine.x_mm,
                y_mm=stub.y_mm + direction[1] * gap - mine.y_mm,
            ),
            "rotation_deg": chosen,
            "width_mm": turned.width_mm,
            "height_mm": turned.height_mm,
        }
    )


__all__ = [
    "SpineLayout",
    "SpineRun",
    "carry_the_rest",
]
