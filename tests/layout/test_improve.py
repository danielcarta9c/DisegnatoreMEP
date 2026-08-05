"""WP3 — la disposizione al servizio delle linee (D-078, D-080), collaudata.

«Spostare un oggetto e' gratis, piegare una linea costa»: dopo la prima posa i
componenti si spostano, si reinstrada, e la mossa si tiene solo se l'obiettivo
totale scende senza che gli attraversamenti crescano. Il criterio di
accettazione del pacchetto, rivisto dall'orchestratore sulla scorta della
ricerca esaustiva (600 disposizioni: sotto i 9 nodi condivisi si va solo
pagando 27 pieghe), e': nessuna voce peggiore del pre-miglioramento, almeno
una strettamente migliore, obiettivo totale strettamente migliore, lunghezza
entro il +10%. I vincoli rigidi — ordine di processo, distanze, griglia,
terra — non si negoziano per nessun guadagno.

WP3b aggiunge le due cose che chiudono il residuo dichiarato — l'andata e
ritorno sul prelievo ACS del caso di accettazione: le **rotazioni** fra le
mosse candidate, perche' nessuna traslazione cambia da che parte guarda una
porta, e l'**andata e ritorno** come prima voce del confronto, perche' non e'
un disegno caro ma un disegno sbagliato e va pagata prima dell'obiettivo.
"""

from functools import cache
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.symbol import PortFace
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import (
    compose_drawing,
    compose_on_ordinary_frame,
    inline_component_ids,
)
from disegnatore_mep.layout.composition import Standing, levels_of, standing_of
from disegnatore_mep.layout.geometry import (
    PlacedSymbol,
    Point,
    SheetGeometry,
    drawing_fingerprint,
)
from disegnatore_mep.layout.grid import GridSpace
from disegnatore_mep.layout.improve import (
    improve_sheet,
    objective_of,
    overshoots_the_goal,
)
from disegnatore_mep.layout.partition import SheetPartition, partition_project
from disegnatore_mep.layout.place import ROW_GAP_MM, place_sheet
from disegnatore_mep.layout.route import route_sheet
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.validation.geometry import validate_drawing_geometry

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
COMPLETE = ROOT / "examples" / "rules" / "centrale-pdc-completa.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"


@cache
def registry() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


@cache
def case_of(path: Path) -> tuple[ProjectModel, SheetPartition, frozenset[str]]:
    project = load_project(path)
    inline = inline_component_ids(project, registry())
    partition = partition_project(project, build_trunks(project, inline))[0]
    return project, partition, inline


def case() -> tuple[ProjectModel, SheetPartition, frozenset[str]]:
    return case_of(PROJECT)


@cache
def before_and_after_of(path: Path) -> tuple[list[PlacedSymbol], list[PlacedSymbol]]:
    project, partition, inline = case_of(path)
    first = place_sheet(project, partition, registry(), NOVE_C_A3, inline)
    improved = improve_sheet(
        project, partition, registry(), NOVE_C_A3, list(first), inline
    )
    return first, improved


def before_and_after() -> tuple[list[PlacedSymbol], list[PlacedSymbol]]:
    return before_and_after_of(PROJECT)


def measured(
    placed: list[PlacedSymbol], path: Path = PROJECT
) -> tuple[int, int, int, float]:
    """(obiettivo, pieghe, attraversamenti, lunghezza) della prova di rotta."""
    project, partition, _ = case_of(path)
    grid = GridSpace(origin=NOVE_C_A3.drawing_rect_mm, standard=NOVE_C_A3.standard)
    routes = route_sheet(
        project, list(partition.trunks), list(placed), registry(), grid, None
    )
    bends = sum(
        max(len(segment) - 2, 0) for route in routes for segment in route.segments
    )
    crossings = sum(len(route.crossings) for route in routes)
    length = sum(
        abs(after.x_mm - before.x_mm) + abs(after.y_mm - before.y_mm)
        for route in routes
        for segment in route.segments
        for before, after in zip(segment, segment[1:], strict=False)
    )
    return objective_of(routes, grid.step_mm), bends, crossings, length


def test_the_improvement_is_deterministic() -> None:
    """Stessi ingressi, geometria bit-identica: nessun caso, nessun ordine di
    dizionario, nessuna dipendenza dal seme di hash."""
    project, partition, inline = case()
    first = place_sheet(project, partition, registry(), NOVE_C_A3, inline)
    again = improve_sheet(
        project, partition, registry(), NOVE_C_A3, list(first), inline
    )
    assert [item.model_dump() for item in again] == [
        item.model_dump() for item in before_and_after()[1]
    ]


def test_the_total_objective_strictly_improves_and_no_term_worsens() -> None:
    """Il criterio rivisto di WP3: obiettivo totale strettamente giu';
    pieghe e attraversamenti mai peggiori, almeno uno strettamente meglio;
    lunghezza entro il +10% del pre-miglioramento (qui scende)."""
    before, after = before_and_after()
    objective0, bends0, crossings0, length0 = measured(before)
    objective1, bends1, crossings1, length1 = measured(after)
    assert objective1 < objective0
    assert bends1 <= bends0
    assert crossings1 <= crossings0
    assert bends1 < bends0 or crossings1 < crossings0
    assert length1 <= length0 * 1.10


def test_the_hard_constraints_hold_after_improvement() -> None:
    """Cio' che non si negozia per nessun guadagno: distanze fra simboli,
    ordine di processo, terra, griglia (D-060, D-062)."""
    before, after = before_and_after()
    project, partition, _ = case()

    # Nessuna sovrapposizione, e nemmeno sotto lo stacco minimo di fascia.
    for index, first in enumerate(after):
        for second in after[index + 1 :]:
            apart = (
                first.right_mm <= second.origin.x_mm + 1e-9
                or second.right_mm <= first.origin.x_mm + 1e-9
                or first.bottom_mm <= second.origin.y_mm + 1e-9
                or second.bottom_mm <= first.origin.y_mm + 1e-9
            )
            assert apart, (first.component_id, second.component_id)

    # L'ordine orizzontale dei centri di ogni tratta e' quello di partenza.
    def centre_x(placed: list[PlacedSymbol], component_id: str) -> float:
        item = next(entry for entry in placed if entry.component_id == component_id)
        return item.origin.x_mm + item.width_mm / 2

    for trunk in partition.trunks:
        start_id, end_id = trunk.start.component_id, trunk.end.component_id
        if start_id == end_id:
            continue
        was_left = centre_x(before, start_id) < centre_x(before, end_id)
        is_left = centre_x(after, start_id) < centre_x(after, end_id)
        assert was_left == is_left, trunk.connection_ids

    # Chi sta a terra per costruzione ci sta ancora, esattamente sulla linea.
    # (Non chi la sfiorava per caso: un terminale su tubazione puo' alzarsi.)
    drawing = NOVE_C_A3.drawing_rect_mm
    grid = GridSpace(origin=drawing, standard=NOVE_C_A3.standard)
    ground = levels_of(drawing.y_mm, drawing.height_mm, grid.step_mm).ground_mm
    definitions = {item.id: item.definition_id for item in project.components}

    def stands_on_the_ground(item: PlacedSymbol) -> bool:
        resolved = registry().resolve(definitions[item.component_id])
        manifest = resolved.symbol.manifest.rotated(item.rotation_deg)
        return (
            standing_of(
                manifest.height_mm,
                frozenset(resolved.definition.functions),
                resolved.is_inline,
            )
            is Standing.GROUND
        )

    grounded = [item for item in after if stands_on_the_ground(item)]
    assert grounded, "il caso ha macchine a terra"
    for item in grounded:
        assert item.bottom_mm == ground, item.component_id
    # E tutto resta sulla griglia: una coordinata fuori passo solleva.
    for item in after:
        grid.to_cell(item.origin.x_mm, item.origin.y_mm)


@cache
def composed_of(path: Path) -> SheetGeometry:
    return compose_drawing(load_project(path), registry(), NOVE_C_A3).sheets[0]


def composed() -> SheetGeometry:
    return composed_of(PROJECT)


def andata_e_ritorno(path: Path) -> list[tuple[str, ...]]:
    """Le tratte della tavola composta che superano la meta e ci tornano."""
    project, partition, _ = case_of(path)
    drawn = composed_of(path)
    placed = {item.component_id: item for item in drawn.symbols}
    definitions = {item.id: item.definition_id for item in project.components}
    by_key = {tuple(route.connection_ids): route for route in drawn.routes}
    overshooting: list[tuple[str, ...]] = []
    for trunk in partition.trunks:
        route = by_key[tuple(trunk.connection_ids)]
        symbol = placed[trunk.end.component_id]
        manifest = (
            registry()
            .resolve(definitions[trunk.end.component_id])
            .symbol.manifest.rotated(symbol.rotation_deg)
        )
        port = manifest.port(trunk.end.port_id)
        goal = Point(
            x_mm=symbol.origin.x_mm + port.x_mm,
            y_mm=symbol.origin.y_mm + port.y_mm,
        )
        if overshoots_the_goal(route, goal):
            overshooting.append(tuple(trunk.connection_ids))
    return overshooting


def test_no_route_makes_an_andata_e_ritorno() -> None:
    """B12, corollario di D-078: nessuna tratta supera la perpendicolare per
    la porta di destinazione per poi tornarci. Se serve, si sposta l'oggetto."""
    assert andata_e_ritorno(PROJECT) == []


def test_no_route_makes_an_andata_e_ritorno_on_the_complete_case() -> None:
    """Lo stesso, sul caso di accettazione: e' il giro che il PM ha cerchiato.

    Il prelievo ACS e' un confine di rete, un simbolo con una porta sola
    rivolta a destra, e la sua alimentazione gli arriva da sinistra: la linea
    lo superava e tornava indietro. Nessuna traslazione lo chiude — spostarlo
    non cambia da che parte guarda — e infatti WP3 lo lasciava aperto. Lo
    chiude la rotazione (WP3b).
    """
    assert andata_e_ritorno(COMPLETE) == []


def test_the_improvement_turns_a_single_port_terminal_towards_its_feed() -> None:
    """La mossa di rotazione esiste, e' ammessa e viene accettata.

    Il posizionamento posa il confine di rete diritto, perche' non sa da che
    parte gli arrivera' la linea; il ciclo lo gira di 180 gradi, ed e' la sola
    mossa che toglie l'andata e ritorno — una traslazione non cambia da che
    parte guarda una porta. Le passate successive possono poi anche
    spostarlo, ma il verso resta quello scelto qui.
    """
    first, improved = before_and_after_of(COMPLETE)
    was = next(item for item in first if item.component_id == "draw-off")
    now = next(item for item in improved if item.component_id == "draw-off")
    assert was.rotation_deg == 0
    assert now.rotation_deg == 180
    # La rotazione e' fra quelle che il manifesto ammette (D-049), e il
    # riquadro dichiarato resta quello del manifesto ruotato (ADR 0003).
    upright = registry().resolve("dhw-draw-off").symbol.manifest
    assert 180 in upright.allowed_rotations_deg
    turned = upright.rotated(180)
    assert (now.width_mm, now.height_mm) == (turned.width_mm, turned.height_mm)
    # E la porta ora guarda dalla parte da cui arriva l'alimentazione.
    assert upright.port("a").face is PortFace.RIGHT
    assert turned.port("a").face is PortFace.LEFT


def turnbacks(placed: list[PlacedSymbol], path: Path) -> list[tuple[str, ...]]:
    """Le andate e ritorno della prova di rotta, come le conta il ciclo."""
    project, partition, _ = case_of(path)
    grid = GridSpace(origin=NOVE_C_A3.drawing_rect_mm, standard=NOVE_C_A3.standard)
    routes = route_sheet(
        project, list(partition.trunks), list(placed), registry(), grid, None
    )
    definitions = {item.id: item.definition_id for item in project.components}
    by_component = {item.component_id: item for item in placed}
    found: list[tuple[str, ...]] = []
    for trunk, route in zip(partition.trunks, routes, strict=True):
        symbol = by_component[trunk.end.component_id]
        manifest = (
            registry()
            .resolve(definitions[trunk.end.component_id])
            .symbol.manifest.rotated(symbol.rotation_deg)
        )
        port = manifest.port(trunk.end.port_id)
        goal = Point(
            x_mm=symbol.origin.x_mm + port.x_mm, y_mm=symbol.origin.y_mm + port.y_mm
        )
        if overshoots_the_goal(route, goal):
            found.append(tuple(trunk.connection_ids))
    return found


def test_the_improvement_removes_a_turnback_and_never_adds_one() -> None:
    """La voce che comanda il confronto lessicografico (WP3b).

    Sul caso completo l'andata e ritorno del prelievo ACS c'e' prima e non
    c'e' dopo. Sul caso di layout non ce n'erano e non ce ne sono: il ciclo
    non ne compra una nemmeno quando l'obiettivo scenderebbe — senza questa
    voce, con le sole rotazioni fra i candidati, il caso di layout chiudeva a
    obiettivo 6190 **con** un'andata e ritorno invece che a 6200 senza.
    """
    before, after = before_and_after_of(COMPLETE)
    assert turnbacks(before, COMPLETE) == [("w2-a-a", "w2-a-b", "w2-b")]
    assert turnbacks(after, COMPLETE) == []
    before, after = before_and_after_of(PROJECT)
    assert turnbacks(before, PROJECT) == []
    assert turnbacks(after, PROJECT) == []


def test_the_complete_case_improvement_is_deterministic() -> None:
    """Due esecuzioni, geometria bit-identica: la rotazione non introduce
    nessun ordine di dizionario ne' dipendenza dal seme di hash."""
    project, partition, inline = case_of(COMPLETE)
    first = place_sheet(project, partition, registry(), NOVE_C_A3, inline)
    again = improve_sheet(
        project, partition, registry(), NOVE_C_A3, list(first), inline
    )
    assert [item.model_dump() for item in again] == [
        item.model_dump() for item in before_and_after_of(COMPLETE)[1]
    ]
    twice = compose_drawing(load_project(COMPLETE), registry(), NOVE_C_A3)
    assert drawing_fingerprint(twice) == drawing_fingerprint(
        compose_drawing(load_project(COMPLETE), registry(), NOVE_C_A3)
    )


def test_the_complete_case_pays_nothing_for_the_straightened_run() -> None:
    """La rotazione non compra l'andata e ritorno con un disegno peggiore.

    Sulla prova di rotta del caso completo: pieghe da 28 a 22, attraversamenti
    da 11 a 9, lunghezza da 1332,5 a 1195 mm, obiettivo da 8460 a 7250. Prima
    di WP3b il ciclo si fermava a 24 pieghe, 9 attraversamenti, 1207,5 mm e
    obiettivo 7500 — con il giro ancora li'.
    """
    before, after = before_and_after_of(COMPLETE)
    objective0, bends0, crossings0, length0 = measured(before, COMPLETE)
    objective1, bends1, crossings1, length1 = measured(after, COMPLETE)
    assert (objective0, bends0, crossings0, length0) == (8460, 28, 11, 1332.5)
    assert objective1 <= 7250
    assert bends1 <= 22
    assert crossings1 <= 9
    assert length1 <= 1195.0


def test_the_complete_case_fits_one_a3_with_a_stacked_pair() -> None:
    """D-072 e D-073 sul caso di accettazione: prima di dividere si impila.

    «Avresti potuto mettere il serbatoio ACS e il volano termico non in fila
    uno dopo l'altro ma uno sopra l'altro»: con le intercettazioni per attacco
    di WP2 le quattro fasce in fila chiedono 395 mm su 335 disponibili, e il
    tentativo di recupero impila bollitore e volano nella stessa colonna —
    il piano di impaginazione torna a una tavola sola, piena a criterio.
    """
    frame, drawn = compose_on_ordinary_frame(load_project(COMPLETE), registry())
    assert frame == NOVE_C_A3
    assert len(drawn.sheets) == 1
    assert validate_drawing_geometry(drawn, frame).ok
    placed = {item.component_id: item for item in drawn.sheets[0].symbols}
    tank, buffer = placed["cylinder"], placed["buffer"]
    # Colonna condivisa: allineati a sinistra, il volano sopra il bollitore,
    # con lo stacco di fascia; chi resta a terra ci appoggia esattamente.
    assert tank.origin.x_mm == buffer.origin.x_mm
    assert buffer.bottom_mm + ROW_GAP_MM == tank.origin.y_mm
    ground = drawn.sheets[0].ground_line_y_mm
    assert ground is not None
    assert tank.bottom_mm == ground
    assert buffer.bottom_mm < tank.origin.y_mm
