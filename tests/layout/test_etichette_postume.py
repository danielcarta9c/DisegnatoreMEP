"""Le etichette sono l'ultima fase del disegno, e non spostano niente (DRAW-003).

Il PO (I-025): i testi non condizionano posa o tubazioni. La sequenza
posa → tubazioni → centratura → testi esiste gia' nella catena, e qui e' un
**contratto provato**: cambiare contenuto, lunghezza, presenza o modalita' delle
etichette non cambia una coordinata dei simboli ne' un punto delle rotte.

La revisione del PM (DRAW-003-R1) ha corretto la regola di posa: le etichette
hanno costo nullo rispetto alla geometria, e la loro posa e' **semplice e a
buon fine**, non un ottimizzatore. Ogni testo prova, in un ordine fisso, i
posti adiacenti al proprio pezzo — sopra, sotto, a destra, a sinistra — e si
ferma al primo libero, senza richiamo. Le sigle delle macchine, se nessun
posto adiacente e' libero, provano un richiamo corto a 45 gradi che non
attraversa niente; se nemmeno quello esiste, la sigla si omette e la tavola
esce lo stesso. Gli indirizzi della modalita' verifica sono un velo a buon
fine: adiacenti o omessi, mai richiamati.

Scritte prima del codice applicativo, come il pacchetto chiede.
"""

from functools import cache
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import compose_drawing, compose_on_ordinary_frame
from disegnatore_mep.layout.geometry import (
    DrawingGeometry,
    PlacedLabel,
    PlacedSymbol,
    Point,
    RoutedTrunk,
    drawing_fingerprint,
)
from disegnatore_mep.layout.labels import (
    CALLOUT_LINE_GAP_MM,
    LINE_CLEARANCE_MM,
    SIDE_GAP_MM,
    TAG_GAP_MM,
    VALUE_GAP_MM,
    place_addresses,
    place_labels,
    text_width_mm,
)
from disegnatore_mep.model.project import ProjectModel

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
PROVA_1 = ROOT / "examples" / "prova" / "prova-1-due-pdc-accumulo-combinato.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"
NAMING = ROOT / "naming"

HEIGHT_MM = NOVE_C_A3.standard.text_small_mm
Box = tuple[float, float, float, float]


@cache
def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def symbol(
    component_id: str,
    x_mm: float,
    y_mm: float,
    tag: str | None = None,
    width_mm: float = 10.0,
    height_mm: float = 10.0,
) -> PlacedSymbol:
    return PlacedSymbol(
        component_id=component_id,
        symbol_id="prova",
        rotation_deg=0,
        origin=Point(x_mm=x_mm, y_mm=y_mm),
        width_mm=width_mm,
        height_mm=height_mm,
        tag=tag,
    )


def run(*points: tuple[float, float]) -> RoutedTrunk:
    return RoutedTrunk(
        network_id="n1",
        medium="heating_water",
        segments=[[Point(x_mm=x, y_mm=y) for x, y in points]],
    )


def label_box(item: PlacedLabel) -> Box:
    width = text_width_mm(item.text, HEIGHT_MM)
    return (
        item.anchor.x_mm,
        item.anchor.y_mm - HEIGHT_MM,
        item.anchor.x_mm + width,
        item.anchor.y_mm,
    )


def symbol_box(item: PlacedSymbol) -> Box:
    return (item.origin.x_mm, item.origin.y_mm, item.right_mm, item.bottom_mm)


def line_boxes(routes: list[RoutedTrunk]) -> list[Box]:
    return [
        (
            min(before.x_mm, after.x_mm) - LINE_CLEARANCE_MM,
            min(before.y_mm, after.y_mm) - LINE_CLEARANCE_MM,
            max(before.x_mm, after.x_mm) + LINE_CLEARANCE_MM,
            max(before.y_mm, after.y_mm) + LINE_CLEARANCE_MM,
        )
        for route in routes
        for segment in route.segments
        for before, after in zip(segment, segment[1:], strict=False)
    ]


def apart(first: Box, second: Box) -> bool:
    return (
        first[2] <= second[0] + 1e-9
        or second[2] <= first[0] + 1e-9
        or first[3] <= second[1] + 1e-9
        or second[3] <= first[1] + 1e-9
    )


def adjacent(item: PlacedLabel, owner: PlacedSymbol) -> bool:
    """Il testo sta accanto al proprio pezzo: nella fila che lo tocca a meno
    dello stacco, o nella seconda fila, una riga piu' in la'."""
    box, own = label_box(item), symbol_box(owner)
    gap_x = max(own[0] - box[2], box[0] - own[2], 0.0)
    gap_y = max(own[1] - box[3], box[1] - own[3], 0.0)
    reach = max(TAG_GAP_MM, VALUE_GAP_MM, SIDE_GAP_MM) + HEIGHT_MM + CALLOUT_LINE_GAP_MM
    return max(gap_x, gap_y) <= reach + 1e-9


def _orientation(a: Point, b: Point, c: Point) -> float:
    return (b.x_mm - a.x_mm) * (c.y_mm - a.y_mm) - (b.y_mm - a.y_mm) * (c.x_mm - a.x_mm)


def segments_cross(a: Point, b: Point, c: Point, d: Point) -> bool:
    """Vero se i due segmenti si attraversano in un punto interno a entrambi."""
    first = _orientation(a, b, c) * _orientation(a, b, d)
    second = _orientation(c, d, a) * _orientation(c, d, b)
    return first < -1e-9 and second < -1e-9


def leader_is_oblique(item: PlacedLabel) -> bool:
    assert item.leader_from is not None
    span_x = abs(item.anchor.x_mm - item.leader_from.x_mm)
    span_y = abs(item.anchor.y_mm - item.leader_from.y_mm)
    return span_x > 0 and span_y > 0 and abs(span_x - span_y) <= 1e-9


def leader_crosses_nothing(
    item: PlacedLabel,
    symbols: list[PlacedSymbol],
    routes: list[RoutedTrunk],
    others: list[PlacedLabel],
) -> bool:
    """Il richiamo non attraversa tubi, simboli, testi ne' altri richiami."""
    assert item.leader_from is not None
    start, end = item.leader_from, item.anchor
    for route in routes:
        for segment in route.segments:
            for first, second in zip(segment, segment[1:], strict=False):
                if segments_cross(start, end, first, second):
                    return False
    for other in others:
        if other is item or other.leader_from is None:
            continue
        if segments_cross(start, end, other.leader_from, other.anchor):
            return False
    boxes = [symbol_box(one) for one in symbols] + [
        label_box(one) for one in others if one is not item
    ]
    return not any(_enters(start, end, box) for box in boxes)


def _enters(before: Point, after: Point, box: Box) -> bool:
    origin = (before.x_mm, before.y_mm)
    delta = (after.x_mm - before.x_mm, after.y_mm - before.y_mm)
    low, high = 0.0, 1.0
    for axis, (lower, upper) in enumerate(((box[0], box[2]), (box[1], box[3]))):
        if abs(delta[axis]) <= 1e-9:
            if not lower + 1e-9 < origin[axis] < upper - 1e-9:
                return False
            continue
        first = (lower - origin[axis]) / delta[axis]
        second = (upper - origin[axis]) / delta[axis]
        low = max(low, min(first, second))
        high = min(high, max(first, second))
    return low < high - 1e-9


def shape(drawing: DrawingGeometry) -> tuple[object, ...]:
    """Simboli e rotte, senza i testi: cio' che le etichette non devono toccare."""
    sheet = drawing.sheets[0]
    return (
        tuple(
            item.model_dump(mode="json", exclude={"tag"}) for item in sheet.symbols
        ),
        tuple(item.model_dump(mode="json") for item in sheet.routes),
    )


def hugging(item: PlacedSymbol) -> list[RoutedTrunk]:
    """Due tubi a un passo e a due passi dal pezzo su ogni lato, lunghi quanto
    il pezzo.

    Ogni posto adiacente — prima e seconda fila — e' occupato, ma dagli
    spigoli partono diagonali che non attraversano niente: e' il caso in cui
    un richiamo corto chiarisce.
    """
    box = symbol_box(item)
    routes: list[RoutedTrunk] = []
    for k in (2.5, 5.0):
        routes.append(run((box[0], box[1] - k), (box[2], box[1] - k)))
        routes.append(run((box[0], box[3] + k), (box[2], box[3] + k)))
        routes.append(run((box[0] - k, box[1]), (box[0] - k, box[3])))
        routes.append(run((box[2] + k, box[1]), (box[2] + k, box[3])))
    return routes


def walled(item: PlacedSymbol) -> list[RoutedTrunk]:
    """Un reticolo fitto di tubi tutt'intorno, ben oltre il pezzo: nessun
    posto adiacente e nessuna diagonale pulita."""
    box = symbol_box(item)
    routes: list[RoutedTrunk] = []
    for k in range(1, 10):
        routes.append(run((box[0] - 25.0, box[1] - 2.5 * k), (box[2] + 25.0, box[1] - 2.5 * k)))
        routes.append(run((box[0] - 25.0, box[3] + 2.5 * k), (box[2] + 25.0, box[3] + 2.5 * k)))
        routes.append(run((box[0] - 2.5 * k, box[1] - 25.0), (box[0] - 2.5 * k, box[3] + 25.0)))
        routes.append(run((box[2] + 2.5 * k, box[1] - 25.0), (box[2] + 2.5 * k, box[3] + 25.0)))
    return routes


# --- posti adiacenti in ordine fisso, senza richiamo -------------------------


def test_un_etichetta_con_il_posto_libero_resta_adiacente_e_senza_richiamo() -> None:
    """La sigla sopra il proprio pezzo, e basta (D1)."""
    project = load_project(PROJECT)
    placed = [symbol("x", 100.0, 100.0, tag="X-01")]
    written = place_labels(project, placed, NOVE_C_A3.standard, routes=[])
    assert len(written) == 1
    tag = written[0]
    assert tag.leader_from is None
    assert tag.anchor.y_mm == 100.0 - TAG_GAP_MM
    assert 100.0 <= tag.anchor.x_mm <= 110.0


def test_un_etichetta_sulla_tubazione_prende_un_altro_lato_e_il_tubo_resta_identico() -> None:
    """Il posto sopra e' occupato da un tubo: la sigla va sotto, senza richiamo,
    e la tubazione non si muove di un punto."""
    project = load_project(PROJECT)
    placed = [symbol("x", 100.0, 100.0, tag="X-01")]
    crossing = [run((80.0, 100.0 - TAG_GAP_MM - HEIGHT_MM / 2), (130.0, 100.0 - TAG_GAP_MM - HEIGHT_MM / 2))]
    before = [route.model_dump(mode="json") for route in crossing]

    written = place_labels(project, placed, NOVE_C_A3.standard, routes=crossing)

    assert [route.model_dump(mode="json") for route in crossing] == before
    assert len(written) == 1
    tag = written[0]
    assert tag.leader_from is None, "un posto adiacente libero non chiede richiamo"
    assert adjacent(tag, placed[0])
    box = label_box(tag)
    assert all(apart(box, other) for other in line_boxes(crossing))
    assert apart(box, symbol_box(placed[0]))


def test_i_lati_si_provano_in_ordine_fisso_e_il_primo_libero_vince() -> None:
    """Sopra, sotto, destra, sinistra, nella fila che tocca il pezzo: chiuso il
    sopra si va sotto; chiusi sopra e sotto si va a destra. La seconda fila
    viene solo dopo tutti i lati."""
    project = load_project(PROJECT)
    placed = [symbol("x", 100.0, 100.0, tag="X-01")]
    above = run((80.0, 97.5), (130.0, 97.5))
    below = run((80.0, 112.5), (130.0, 112.5))

    under = place_labels(project, placed, NOVE_C_A3.standard, routes=[above])[0]
    assert under.leader_from is None
    assert under.anchor.y_mm == 110.0 + VALUE_GAP_MM + HEIGHT_MM

    beside = place_labels(project, placed, NOVE_C_A3.standard, routes=[above, below])[0]
    assert beside.leader_from is None
    assert beside.anchor.x_mm == 110.0 + SIDE_GAP_MM

    sides = [run((112.5, 90.0), (112.5, 120.0)), run((97.5, 90.0), (97.5, 120.0))]
    second_row = place_labels(
        project, placed, NOVE_C_A3.standard, routes=[above, below, *sides]
    )[0]
    assert second_row.leader_from is None
    assert second_row.anchor.y_mm == 100.0 - TAG_GAP_MM - HEIGHT_MM - CALLOUT_LINE_GAP_MM
    assert adjacent(second_row, placed[0])


def test_due_etichette_in_conflitto_la_seconda_prende_un_altro_lato() -> None:
    """Chi arriva dopo trova il posto preferito occupato e ne prende un altro
    adiacente; nessuna sovrapposizione finale, nessun richiamo."""
    project = load_project(PROJECT)
    placed = [
        symbol("primo", 100.0, 100.0, tag="PRIMO-0001"),
        symbol("secondo", 110.0, 100.0, tag="SECONDO-01"),
    ]
    written = place_labels(project, placed, NOVE_C_A3.standard, routes=[])
    assert [item.id for item in written] == ["primo-tag", "secondo-tag"]
    first, second = written
    assert first.leader_from is None and second.leader_from is None
    assert adjacent(second, placed[1])
    assert apart(label_box(first), label_box(second))
    for item in written:
        for other in placed:
            assert apart(label_box(item), symbol_box(other))


def test_un_etichetta_non_esce_dall_area_di_disegno() -> None:
    """Il margine e' un conflitto come gli altri: il testo prende un lato
    che sta dentro l'area."""
    area = NOVE_C_A3.drawing_rect_mm
    project = load_project(PROJECT)
    placed = [symbol("x", area.right_mm - 10.0, area.y_mm, tag="X-01-LUNGHISSIMA")]
    written = place_labels(project, placed, NOVE_C_A3.standard, routes=[])
    assert len(written) == 1
    box = label_box(written[0])
    assert box[0] >= area.x_mm - 1e-9 and box[2] <= area.right_mm + 1e-9
    assert box[1] >= area.y_mm - 1e-9 and box[3] <= area.bottom_mm + 1e-9
    assert written[0].leader_from is None
    assert adjacent(written[0], placed[0])


# --- il richiamo: corto, pulito, solo per le sigle delle macchine -------------


def test_una_sigla_murata_prende_un_richiamo_corto_che_non_attraversa_niente() -> None:
    project = load_project(PROJECT)
    placed = [symbol("x", 100.0, 100.0, tag="X-01")]
    routes = hugging(placed[0])
    written = place_labels(project, placed, NOVE_C_A3.standard, routes=routes)
    assert len(written) == 1
    tag = written[0]
    assert tag.leader_from is not None, "nessun posto adiacente: serve il richiamo"
    assert leader_is_oblique(tag)
    assert leader_crosses_nothing(tag, placed, routes, written)
    corners = {(100.0, 100.0), (110.0, 100.0), (100.0, 110.0), (110.0, 110.0)}
    assert (tag.leader_from.x_mm, tag.leader_from.y_mm) in corners
    boxes = [symbol_box(placed[0])] + line_boxes(routes)
    assert all(apart(label_box(tag), other) for other in boxes)
    # Corto: il primo posto libero lungo la diagonale.
    assert abs(tag.anchor.x_mm - tag.leader_from.x_mm) <= 10.0


def test_una_sigla_senza_nessun_posto_pulito_si_omette_e_la_tavola_esce() -> None:
    """Niente richiamo che attraversa tubi o simboli, niente testo sopra
    qualcosa: la sigla manca, e chi legge il preflight lo sa."""
    project = load_project(PROJECT)
    placed = [symbol("x", 100.0, 100.0, tag="X-01")]
    routes = walled(placed[0])
    written = place_labels(project, placed, NOVE_C_A3.standard, routes=routes)
    assert written == []


def test_un_richiamo_non_attraversa_un_altro_richiamo_ne_un_altra_sigla() -> None:
    """Due pezzi murati vicini: il secondo richiamo evita il primo, o non c'e'."""
    project = load_project(PROJECT)
    placed = [
        symbol("uno", 100.0, 100.0, tag="UNO-01"),
        symbol("due", 120.0, 100.0, tag="DUE-01"),
    ]
    routes = hugging(placed[0]) + hugging(placed[1])
    written = place_labels(project, placed, NOVE_C_A3.standard, routes=routes)
    boxes = [symbol_box(item) for item in placed] + line_boxes(routes)
    for item in written:
        assert all(apart(label_box(item), other) for other in boxes), item.id
        boxes.append(label_box(item))
        if item.leader_from is not None:
            assert leader_is_oblique(item)
            assert leader_crosses_nothing(item, placed, routes, written), item.id


# --- gli indirizzi di verifica: velo a buon fine, mai richiamati -------------


def test_un_indirizzo_prende_un_lato_libero_o_si_omette() -> None:
    placed = [symbol("x", 100.0, 100.0)]
    free = place_addresses(placed, {"x": "CP.01.N.01"}, NOVE_C_A3.standard, routes=[])
    assert len(free) == 1 and free[0].leader_from is None
    assert free[0].anchor.x_mm == 110.0 + SIDE_GAP_MM

    # Un tubo verticale dove l'indirizzo vorrebbe stare: si va a sinistra.
    blocking = [run((115.0, 80.0), (115.0, 130.0))]
    moved = place_addresses(placed, {"x": "CP.01.N.01"}, NOVE_C_A3.standard, routes=blocking)
    assert len(moved) == 1 and moved[0].leader_from is None
    assert adjacent(moved[0], placed[0])
    assert all(apart(label_box(moved[0]), other) for other in line_boxes(blocking))

    # Nessun lato libero: l'indirizzo non si scrive, e non si richiama.
    omitted = place_addresses(
        placed, {"x": "CP.01.N.01"}, NOVE_C_A3.standard, routes=hugging(placed[0])
    )
    assert omitted == []


def test_un_indirizzo_non_porta_mai_il_richiamo() -> None:
    placed = [symbol(f"v{index}", 100.0 + 15.0 * index, 100.0, width_mm=5.0, height_mm=5.0) for index in range(4)]
    routes = [run((90.0, 102.5), (170.0, 102.5))]
    routes += [route for item in placed for route in hugging(item)]
    written = place_addresses(
        placed, {item.component_id: "CP.01.N.01" for item in placed}, NOVE_C_A3.standard, routes=routes
    )
    assert all(item.leader_from is None for item in written)


# --- il contratto: i testi non toccano simboli e rotte -----------------------


def _with_long_tag(project: ProjectModel, text: str) -> ProjectModel:
    twin = project.model_copy(deep=True)
    tagged = next(item for item in twin.components if item.tag)
    tagged.tag = text
    return twin


def test_una_sigla_molto_piu_lunga_non_cambia_simboli_ne_rotte() -> None:
    project = load_project(PROJECT)
    plain = compose_drawing(project, catalog(), NOVE_C_A3)
    long = compose_drawing(
        _with_long_tag(project, "SIGLA-LUNGHISSIMA-CHE-NON-DEVE-SPOSTARE-NIENTE-01"),
        catalog(),
        NOVE_C_A3,
    )
    assert shape(plain) == shape(long)
    assert {item.text for item in long.sheets[0].labels} != {
        item.text for item in plain.sheets[0].labels
    }


def test_senza_nessuna_sigla_simboli_e_rotte_restano_gli_stessi() -> None:
    project = load_project(PROJECT)
    bare = project.model_copy(deep=True)
    for item in bare.components:
        item.tag = None
        item.properties = {}
    assert shape(compose_drawing(project, catalog(), NOVE_C_A3)) == shape(
        compose_drawing(bare, catalog(), NOVE_C_A3)
    )


@cache
def _tavola_1() -> tuple[ProjectModel, DrawingGeometry, object]:
    from disegnatore_mep.rules.apply import saturate
    from disegnatore_mep.rules.registry import RuleRegistry

    rules = RuleRegistry.from_directory(RULES)
    rules.cross_check(catalog())
    completed, _, _ = saturate(load_project(PROVA_1), catalog(), rules)
    frame, drawn = compose_on_ordinary_frame(completed, catalog())
    return completed, drawn, frame


def test_gli_indirizzi_di_verifica_non_cambiano_simboli_ne_rotte() -> None:
    """La modalita' verifica e' un velo sopra la tavola di consegna."""
    from disegnatore_mep.cli import _with_addresses
    from disegnatore_mep.graphics.frame import SheetFrame

    completed, delivered, frame = _tavola_1()
    assert isinstance(frame, SheetFrame)
    verified = _with_addresses(delivered, completed, catalog(), frame, NAMING)
    assert shape(verified) == shape(delivered)
    addresses = [item for item in verified.sheets[0].labels if item.role == "address"]
    assert addresses
    assert all(item.leader_from is None for item in addresses)
    others = [item for item in verified.sheets[0].labels if item.role != "address"]
    assert [item.model_dump() for item in others] == [
        item.model_dump() for item in delivered.sheets[0].labels
    ]
    sheet = verified.sheets[0]
    boxes = [symbol_box(item) for item in sheet.symbols] + line_boxes(sheet.routes)
    for item in sheet.labels:
        assert all(apart(label_box(item), other) for other in boxes), item.id
        boxes.append(label_box(item))


def test_la_tavola_di_consegna_porta_solo_le_sigle_delle_macchine() -> None:
    """Criterio 5: nessun indirizzo della rete nella tavola definitiva."""
    _, drawn, _ = _tavola_1()
    sheet = drawn.sheets[0]
    assert {item.role for item in sheet.labels} <= {"tag", "data"}
    tagged = {item.component_id for item in sheet.symbols if item.tag}
    assert {item.id.rsplit("-", 1)[0] for item in sheet.labels} <= tagged
    placed = {item.component_id: item for item in sheet.symbols}
    for item in sheet.labels:
        if item.leader_from is None:
            assert adjacent(item, placed[item.id.rsplit("-", 1)[0]]), item.id
        else:
            assert leader_is_oblique(item), item.id
            assert leader_crosses_nothing(item, sheet.symbols, sheet.routes, sheet.labels), item.id


def test_due_generazioni_consecutive_danno_lo_stesso_output() -> None:
    project = load_project(PROJECT)
    once = compose_drawing(project, catalog(), NOVE_C_A3)
    twice = compose_drawing(project, catalog(), NOVE_C_A3)
    assert drawing_fingerprint(once) == drawing_fingerprint(twice)
    assert [item.model_dump() for item in once.sheets[0].labels] == [
        item.model_dump() for item in twice.sheets[0].labels
    ]
