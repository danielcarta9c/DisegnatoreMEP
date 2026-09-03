"""Le etichette sono l'ultima fase del disegno, e non spostano niente (DRAW-003).

Il PO (I-025): «se il testo collide con tubi o altre etichette, si muove il solo
testo e si aggiunge un richiamo; il routing resta invariato». La sequenza
posa → tubazioni → testi esiste gia' nella catena, ma qui diventa un
**contratto provato**: cambiare contenuto, lunghezza, presenza o modalita' delle
etichette non cambia una coordinata dei simboli ne' un punto delle rotte.

E la posa dei testi e' netta (D-075, D-110, D-111): ogni testo ha una posizione
preferita accanto al proprio pezzo; se e' libera resta li' senza richiamo; al
primo conflitto — tubo, simbolo, altra etichetta, margine — si sposta il solo
testo e lo si lega con un richiamo obliquo a 45 gradi, che non attraversa
tubazioni ne' altri richiami quando esiste un'alternativa libera.

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
    LINE_CLEARANCE_MM,
    TAG_GAP_MM,
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


def shape(drawing: DrawingGeometry) -> tuple[object, ...]:
    """Simboli e rotte, senza i testi: cio' che le etichette non devono toccare."""
    sheet = drawing.sheets[0]
    return (
        tuple(
            item.model_dump(mode="json", exclude={"tag"}) for item in sheet.symbols
        ),
        tuple(item.model_dump(mode="json") for item in sheet.routes),
    )


# --- la posizione preferita, e il richiamo al primo conflitto ------------------


def test_un_etichetta_con_il_posto_libero_resta_adiacente_e_senza_richiamo() -> None:
    """Prova 4: la sigla sopra il proprio pezzo, e basta (D1)."""
    project = load_project(PROJECT)
    placed = [symbol("x", 100.0, 100.0, tag="X-01")]
    written = place_labels(project, placed, NOVE_C_A3.standard, routes=[])
    assert len(written) == 1
    tag = written[0]
    assert tag.leader_from is None
    assert tag.anchor.y_mm == 100.0 - TAG_GAP_MM
    assert 100.0 <= tag.anchor.x_mm <= 110.0


def test_un_etichetta_sulla_tubazione_si_sposta_con_richiamo_e_il_tubo_resta_identico() -> None:
    """Prova 5: al primo conflitto si muove il solo testo, con la diagonale."""
    project = load_project(PROJECT)
    placed = [symbol("x", 100.0, 100.0, tag="X-01")]
    # Una tubazione che corre esattamente dove la sigla vorrebbe stare.
    crossing = [run((80.0, 100.0 - TAG_GAP_MM - HEIGHT_MM / 2), (130.0, 100.0 - TAG_GAP_MM - HEIGHT_MM / 2))]
    before = [route.model_dump(mode="json") for route in crossing]

    written = place_labels(project, placed, NOVE_C_A3.standard, routes=crossing)

    assert [route.model_dump(mode="json") for route in crossing] == before
    assert len(written) == 1
    tag = written[0]
    assert tag.leader_from is not None, "la sigla spostata porta il richiamo"
    assert leader_is_oblique(tag)
    box = label_box(tag)
    assert all(apart(box, other) for other in line_boxes(crossing))
    assert apart(box, symbol_box(placed[0]))
    # Il richiamo parte dal proprio pezzo e non attraversa la tubazione: qui lo
    # spazio libero c'e' da tutte le parti, quindi l'alternativa esiste.
    start = tag.leader_from
    corners = {(100.0, 100.0), (110.0, 100.0), (100.0, 110.0), (110.0, 110.0)}
    assert (start.x_mm, start.y_mm) in corners
    for route in crossing:
        for segment in route.segments:
            for first, second in zip(segment, segment[1:], strict=False):
                assert not segments_cross(start, tag.anchor, first, second)


def test_due_etichette_in_conflitto_la_seconda_prende_il_richiamo() -> None:
    """Prova 6: chi arriva dopo si sposta; nessuna sovrapposizione finale."""
    project = load_project(PROJECT)
    # Due pezzi affiancati e due sigle piu' larghe dei pezzi: la seconda sigla,
    # al proprio posto preferito, finirebbe sopra la prima.
    placed = [
        symbol("primo", 100.0, 100.0, tag="PRIMO-0001"),
        symbol("secondo", 110.0, 100.0, tag="SECONDO-01"),
    ]
    written = place_labels(project, placed, NOVE_C_A3.standard, routes=[])
    assert [item.id for item in written] == ["primo-tag", "secondo-tag"]
    first, second = written
    assert first.leader_from is None
    assert second.leader_from is not None
    assert leader_is_oblique(second)
    assert apart(label_box(first), label_box(second))
    for item in written:
        for other in placed:
            assert apart(label_box(item), symbol_box(other))


def test_un_indirizzo_in_conflitto_segue_lo_stesso_ordine() -> None:
    """Gli indirizzi della modalita' verifica: preferito di fianco, poi richiamo."""
    placed = [symbol("x", 100.0, 100.0)]
    free = place_addresses(placed, {"x": "CP.01.N.01"}, NOVE_C_A3.standard, routes=[])
    assert len(free) == 1 and free[0].leader_from is None
    assert free[0].anchor.x_mm > 110.0

    # Una tubazione verticale che passa proprio dove l'indirizzo vorrebbe stare.
    blocking = [run((115.0, 80.0), (115.0, 130.0)), run((80.0, 111.0), (130.0, 111.0))]
    moved = place_addresses(placed, {"x": "CP.01.N.01"}, NOVE_C_A3.standard, routes=blocking)
    assert len(moved) == 1
    assert moved[0].leader_from is not None
    assert leader_is_oblique(moved[0])
    assert all(apart(label_box(moved[0]), other) for other in line_boxes(blocking))


def test_un_etichetta_non_esce_dall_area_di_disegno() -> None:
    """Il margine e' un conflitto come gli altri: si sposta il testo."""
    area = NOVE_C_A3.drawing_rect_mm
    project = load_project(PROJECT)
    placed = [symbol("x", area.right_mm - 10.0, area.y_mm, tag="X-01-LUNGHISSIMA")]
    written = place_labels(project, placed, NOVE_C_A3.standard, routes=[])
    assert len(written) == 1
    box = label_box(written[0])
    assert box[0] >= area.x_mm - 1e-9 and box[2] <= area.right_mm + 1e-9
    assert box[1] >= area.y_mm - 1e-9 and box[3] <= area.bottom_mm + 1e-9
    assert written[0].leader_from is not None


def test_i_richiami_non_si_incrociano_quando_esiste_un_alternativa() -> None:
    """Due testi richiamati dallo stesso angolo trovano diagonali che non si
    attraversano, finche' ce n'e' una libera."""
    project = load_project(PROJECT)
    # Un reticolo di tubi sopra e sotto due pezzi affiancati: nessun posto
    # preferito e' libero, e i richiami devono cercare da soli.
    placed = [
        symbol("uno", 100.0, 100.0, tag="UNO-01"),
        symbol("due", 120.0, 100.0, tag="DUE-01"),
    ]
    routes = [run((80.0, 100.0 - 2.5 * k), (150.0, 100.0 - 2.5 * k)) for k in range(1, 4)]
    routes += [run((80.0, 110.0 + 2.5 * k), (150.0, 110.0 + 2.5 * k)) for k in range(1, 4)]
    written = place_labels(project, placed, NOVE_C_A3.standard, routes=routes)
    leaders = [(item.leader_from, item.anchor) for item in written if item.leader_from is not None]
    assert leaders, "il reticolo obbliga al richiamo"
    for index, (start, end) in enumerate(leaders):
        for other_start, other_end in leaders[index + 1 :]:
            assert not segments_cross(start, end, other_start, other_end)
    boxes = [symbol_box(item) for item in placed] + line_boxes(routes)
    for item in written:
        assert all(apart(label_box(item), other) for other in boxes)
        boxes.append(label_box(item))


# --- il contratto: i testi non toccano simboli e rotte -----------------------


def _with_long_tag(project: ProjectModel, text: str) -> ProjectModel:
    twin = project.model_copy(deep=True)
    tagged = next(item for item in twin.components if item.tag)
    tagged.tag = text
    return twin


def test_una_sigla_molto_piu_lunga_non_cambia_simboli_ne_rotte() -> None:
    """Prova 3: la lunghezza di un testo non muove niente di cio' che e' disegnato."""
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
    """La presenza stessa dei testi non entra nella posa ne' nella centratura."""
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
    """Prova 2: la modalita' verifica e' un velo sopra la tavola di consegna."""
    from disegnatore_mep.cli import _with_addresses
    from disegnatore_mep.graphics.frame import SheetFrame

    completed, delivered, frame = _tavola_1()
    assert isinstance(frame, SheetFrame)
    verified = _with_addresses(delivered, completed, catalog(), frame, NAMING)
    assert shape(verified) == shape(delivered)
    # Il velo esiste davvero: le etichette di indirizzo ci sono, e le altre
    # sono quelle di consegna, identiche.
    addresses = [item for item in verified.sheets[0].labels if item.role == "address"]
    assert addresses
    others = [item for item in verified.sheets[0].labels if item.role != "address"]
    assert [item.model_dump() for item in others] == [
        item.model_dump() for item in delivered.sheets[0].labels
    ]
    # E nessuna scritta finisce sopra un tubo, un simbolo o un'altra scritta.
    sheet = verified.sheets[0]
    boxes = [symbol_box(item) for item in sheet.symbols] + line_boxes(sheet.routes)
    for item in sheet.labels:
        assert all(apart(label_box(item), other) for other in boxes), item.id
        boxes.append(label_box(item))


def test_ogni_etichetta_della_tavola_1_e_libera_o_richiamata_obliqua() -> None:
    """Criteri 4 e 5 sulla tavola vera: nessuna collisione, richiami a 45 gradi."""
    _, drawn, _ = _tavola_1()
    sheet = drawn.sheets[0]
    boxes = [symbol_box(item) for item in sheet.symbols] + line_boxes(sheet.routes)
    for item in sheet.labels:
        assert all(apart(label_box(item), other) for other in boxes), item.id
        boxes.append(label_box(item))
        if item.leader_from is not None:
            assert leader_is_oblique(item), item.id


def test_due_generazioni_consecutive_danno_lo_stesso_output() -> None:
    """Prova 7: etichette comprese."""
    project = load_project(PROJECT)
    once = compose_drawing(project, catalog(), NOVE_C_A3)
    twice = compose_drawing(project, catalog(), NOVE_C_A3)
    assert drawing_fingerprint(once) == drawing_fingerprint(twice)
    assert [item.model_dump() for item in once.sheets[0].labels] == [
        item.model_dump() for item in twice.sheets[0].labels
    ]
