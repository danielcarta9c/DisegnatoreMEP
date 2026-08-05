"""Il preflight di qualita', misura per misura: il caso che cade e quello pulito.

Ogni geometria di prova e' costruita a mano, minima e leggibile. Nessuna passa
dalla catena di impaginazione e nessuna legge un esempio pubblicato: una misura
che si dimostra solo sul caso di accettazione smette di dimostrare qualcosa il
giorno in cui quel caso cambia, ed e' esattamente il giorno in cui serve.
"""

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition, PortDefinition
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import Symbol, SymbolRegistry
from disegnatore_mep.graphics.symbol import KeepOut, PortFace, SymbolManifest, SymbolPort
from disegnatore_mep.layout.geometry import (
    DrawingGeometry,
    PlacedLabel,
    PlacedSymbol,
    Point,
    RoutedTrunk,
    SheetGeometry,
)
from disegnatore_mep.model.types import Domain, IssueSeverity, PortFlow
from disegnatore_mep.validation import preflight
from disegnatore_mep.validation.issues import ValidationIssue

FRAME = NOVE_C_A3
GOOD_SOURCE = "UNI 9511 Tab. 3, tramite SRC-016"


# --- gli attrezzi per costruire una geometria a mano ---------------------------


def at(x_mm: float, y_mm: float) -> Point:
    return Point(x_mm=x_mm, y_mm=y_mm)


def run(name: str, *polylines: list[Point]) -> RoutedTrunk:
    return RoutedTrunk(
        network_id="probe",
        medium="heating-water",
        connection_ids=[name],
        segments=list(polylines),
    )


def placed(
    component_id: str,
    x_mm: float,
    y_mm: float,
    width_mm: float = 10.0,
    height_mm: float = 5.0,
    symbol_id: str = "probe_good",
) -> PlacedSymbol:
    return PlacedSymbol(
        component_id=component_id,
        symbol_id=symbol_id,
        rotation_deg=0,
        origin=at(x_mm, y_mm),
        width_mm=width_mm,
        height_mm=height_mm,
    )


def label(name: str, anchor: Point, leader_from: Point | None = None) -> PlacedLabel:
    return PlacedLabel(
        id=name, text="VAL-01", role="tag", anchor=anchor, leader_from=leader_from
    )


def sheet(
    sheet_id: str = "t1",
    symbols: list[PlacedSymbol] | None = None,
    routes: list[RoutedTrunk] | None = None,
    labels: list[PlacedLabel] | None = None,
) -> SheetGeometry:
    return SheetGeometry(
        sheet_id=sheet_id,
        title="Prova",
        symbols=symbols or [],
        routes=routes or [],
        labels=labels or [],
    )


def drawing(*sheets: SheetGeometry) -> DrawingGeometry:
    return DrawingGeometry(project_id="probe", sheets=list(sheets))


def _manifest(symbol_id: str, source: str) -> SymbolManifest:
    return SymbolManifest(
        id=symbol_id,
        version="1.0.0",
        name="Componente di prova",
        width_mm=10.0,
        height_mm=5.0,
        allowed_rotations_deg=[0],
        ports=[SymbolPort(id="a", face=PortFace.LEFT, x_mm=0.0, y_mm=2.5)],
        keep_out=KeepOut(left_mm=2.0),
        source=source,
    )


def _definition(symbol_id: str) -> ComponentDefinition:
    return ComponentDefinition(
        id=symbol_id,
        version="1.0.0",
        name="Componente di prova",
        functions=["prova"],
        symbol_id=symbol_id,
        ports=[
            PortDefinition(
                id="a", domain=Domain.HYDRONIC, medium="heating-water", flow=PortFlow.IN
            )
        ],
        sources=["SRC-016"],
    )


def catalog(**sources: str) -> ComponentRegistry:
    """Un catalogo minimo: un componente per simbolo, con la fonte dichiarata."""
    symbols = SymbolRegistry(
        [
            Symbol(manifest=_manifest(symbol_id, source), body="<rect/>")
            for symbol_id, source in sources.items()
        ]
    )
    return ComponentRegistry(
        [_definition(symbol_id) for symbol_id in sources], symbols=symbols
    )


def codes(findings: list[ValidationIssue]) -> list[str]:
    return [item.code for item in findings]


def only(findings: list[ValidationIssue], code: str) -> ValidationIssue:
    matching = [item for item in findings if item.code == code]
    assert len(matching) == 1, codes(findings)
    return matching[0]


# --- 1. pieghe per tratta (B4) -------------------------------------------------


def test_a_run_that_bends_too_often_is_a_warning_with_the_count() -> None:
    tangled = run(
        "b",
        [at(20, 20), at(40, 20), at(40, 40), at(60, 40), at(60, 60), at(80, 60)],
    )
    findings = preflight.bends_per_run(drawing(sheet(routes=[tangled])))
    assert codes(findings) == ["RUN_WITH_TOO_MANY_BENDS"]
    assert findings[0].severity is IssueSeverity.WARNING
    assert "4 volte" in findings[0].message
    assert findings[0].entity_ids == ["t1", "b"]


def test_a_run_within_its_bend_budget_says_nothing() -> None:
    tidy = run("b", [at(20, 20), at(40, 20), at(40, 40), at(60, 40)])
    assert preflight.bends_per_run(drawing(sheet(routes=[tidy]))) == []


# --- 2. incroci (B3) -----------------------------------------------------------


def crossed(legs: int) -> SheetGeometry:
    """Una dorsale orizzontale attraversata da `legs` montanti, uno per incrocio."""
    spine = run("h", [at(120, 100), at(200, 100)])
    verticals = [
        run(f"v{index}", [at(125 + index * 10, 80), at(125 + index * 10, 120)])
        for index in range(legs)
    ]
    return sheet(routes=[spine, *verticals])


def test_too_many_crossings_is_a_warning_with_the_count() -> None:
    findings = preflight.crossings(drawing(crossed(6)), FRAME)
    assert codes(findings) == ["TOO_MANY_CROSSINGS"]
    assert findings[0].severity is IssueSeverity.WARNING
    assert "6 nodi condivisi" in findings[0].message


def test_crossings_within_the_budget_say_nothing() -> None:
    assert preflight.crossings(drawing(crossed(3)), FRAME) == []


# --- 3. sovrapposizione longitudinale (B2, D-062) ------------------------------


def test_two_runs_on_the_same_stretch_are_blocking_with_the_length() -> None:
    first = run("o1", [at(220, 60), at(240, 60)])
    second = run("o2", [at(227.5, 60), at(235, 60)])
    findings = preflight.longitudinal_overlap(
        drawing(sheet(routes=[first, second])), FRAME
    )
    assert codes(findings) == ["RUNS_OVERLAP_LENGTHWISE"]
    assert findings[0].severity is IssueSeverity.BLOCKING
    assert "7.5 mm" in findings[0].message
    assert findings[0].entity_ids == ["o1", "o2", "t1"]


def test_a_derivation_on_a_shared_port_is_the_exception_d062_declares() -> None:
    """Un solo passo di griglia contro una porta capo di entrambe le tratte."""
    first = run("o1", [at(220, 60), at(240, 60)])
    joining = run("o2", [at(237.5, 70), at(237.5, 60), at(240, 60)])
    apart = run("o3", [at(220, 90), at(240, 90)])
    assert (
        preflight.longitudinal_overlap(
            drawing(sheet(routes=[first, joining, apart])), FRAME
        )
        == []
    )


# --- 4. distanze di rispetto (B5, B6) ------------------------------------------


def test_a_run_grazing_a_symbol_it_does_not_touch_is_blocking() -> None:
    near = placed("near", 50, 50)
    passing = run("c", [at(45, 56.5), at(80, 56.5)])
    findings = preflight.clearances(
        drawing(sheet(symbols=[near], routes=[passing])), FRAME
    )
    assert codes(findings) == ["RUN_TOO_CLOSE_TO_A_SYMBOL"]
    assert findings[0].severity is IssueSeverity.BLOCKING
    assert "1.5 mm" in findings[0].message


def test_a_run_exactly_on_the_minimum_clearance_is_a_warning() -> None:
    near = placed("near", 50, 50)
    passing = run("c", [at(45, 57), at(80, 57)])
    findings = preflight.clearances(
        drawing(sheet(symbols=[near], routes=[passing])), FRAME
    )
    assert only(findings, "RUN_TOO_CLOSE_TO_A_SYMBOL").severity is IssueSeverity.WARNING
    assert "2 mm" in findings[0].message


def test_two_runs_side_by_side_below_the_clearance_are_blocking() -> None:
    first = run("p1", [at(20, 50), at(60, 50)])
    second = run("p2", [at(30, 51.5), at(50, 51.5)])
    findings = preflight.clearances(drawing(sheet(routes=[first, second])), FRAME)
    assert codes(findings) == ["PARALLEL_RUNS_TOO_CLOSE"]
    assert findings[0].severity is IssueSeverity.BLOCKING
    assert "1.5 mm" in findings[0].message


def test_a_run_that_keeps_its_distance_says_nothing() -> None:
    near = placed("near", 50, 50)
    passing = run("c", [at(45, 65), at(80, 65)])
    alongside = run("d", [at(45, 75), at(80, 75)])
    assert (
        preflight.clearances(
            drawing(sheet(symbols=[near], routes=[passing, alongside])), FRAME
        )
        == []
    )


def test_a_run_attached_to_a_symbol_is_not_measured_against_it() -> None:
    """Il capo della spezzata cade sul riquadro: quello e' un attacco, non uno sfioro."""
    host = placed("host", 50, 50)
    attached = run("c", [at(50, 52.5), at(20, 52.5)])
    assert preflight.clearances(drawing(sheet(symbols=[host], routes=[attached])), FRAME) == []


# --- 5. andate e ritorno (B12, D-078) ------------------------------------------


def test_a_run_that_overshoots_its_port_and_returns_is_blocking() -> None:
    around = run("u", [at(20, 150), at(80, 150), at(80, 170), at(60, 170)])
    findings = preflight.u_turns(drawing(sheet(routes=[around])))
    assert codes(findings) == ["RUN_OVERSHOOTS_ITS_PORT"]
    assert findings[0].severity is IssueSeverity.BLOCKING
    assert "20 mm" in findings[0].message
    assert findings[0].entity_ids == ["t1", "u"]


def test_a_run_that_never_passes_its_port_says_nothing() -> None:
    straight = run("u", [at(20, 150), at(60, 150), at(60, 170)])
    assert preflight.u_turns(drawing(sheet(routes=[straight]))) == []


# --- 6. richiami di etichetta (D2, D3, D-075) ----------------------------------


def test_an_orthogonal_leader_is_blocking_with_its_angle() -> None:
    vertical = label("l1", anchor=at(300, 160), leader_from=at(300, 150))
    findings = preflight.orthogonality_of_leaders(drawing(sheet(labels=[vertical])))
    assert codes(findings) == ["ORTHOGONAL_LABEL_LEADER"]
    assert findings[0].severity is IssueSeverity.BLOCKING
    assert "90 gradi" in findings[0].message
    assert findings[0].entity_ids == ["t1", "l1"]


def test_a_leader_between_two_points_that_are_not_at_45_degrees_is_blocking() -> None:
    skewed = label("l2", anchor=at(320, 160), leader_from=at(300, 150))
    findings = preflight.orthogonality_of_leaders(drawing(sheet(labels=[skewed])))
    assert codes(findings) == ["LEADER_NOT_AT_45_DEGREES"]
    assert findings[0].severity is IssueSeverity.BLOCKING
    assert "27 gradi" in findings[0].message


def test_a_leader_at_45_degrees_and_a_label_without_one_say_nothing() -> None:
    oblique = label("l1", anchor=at(310, 160), leader_from=at(300, 150))
    beside = label("l2", anchor=at(120, 40))
    assert preflight.orthogonality_of_leaders(drawing(sheet(labels=[oblique, beside]))) == []


# --- 7. riempimento del foglio (A1, A3) ----------------------------------------


def test_a_sheet_filled_only_in_part_is_a_warning_with_the_percentage() -> None:
    """L'ingombro copre un quarto dell'area di disegno: una fascia, non una tavola."""
    band = run("f", [at(10, 16), at(185, 16), at(185, 133.5)])
    findings = preflight.sheet_fill(drawing(sheet(routes=[band])), FRAME)
    assert only(findings, "SHEET_BARELY_FILLED").severity is IssueSeverity.WARNING
    assert "pieno solo al 25%" in only(findings, "SHEET_BARELY_FILLED").message


def test_a_drawing_pushed_into_one_corner_is_a_warning_with_the_ratio() -> None:
    corner = placed("big", 20, 20, width_mm=100.0, height_mm=80.0)
    others = [
        placed("tr", 200, 20),
        placed("bl", 20, 150),
        placed("br", 200, 150),
    ]
    findings = preflight.sheet_fill(drawing(sheet(symbols=[corner, *others])), FRAME)
    leaning = only(findings, "DRAWING_ALL_ON_ONE_SIDE")
    assert leaning.severity is IssueSeverity.WARNING
    assert "160.0 volte" in leaning.message


def test_a_sheet_filled_and_balanced_says_nothing() -> None:
    quarters = [
        placed("tl", 30, 30, width_mm=60.0, height_mm=50.0),
        placed("tr", 250, 30, width_mm=60.0, height_mm=50.0),
        placed("bl", 30, 200, width_mm=60.0, height_mm=50.0),
        placed("br", 250, 200, width_mm=60.0, height_mm=50.0),
    ]
    assert preflight.sheet_fill(drawing(sheet(symbols=quarters)), FRAME) == []


# --- 8. riempimento delle tavole successive (A2, D-072) ------------------------


def test_a_continuation_sheet_that_is_nearly_empty_is_blocking() -> None:
    full = sheet("t1", symbols=[placed("a", 20, 20, width_mm=300.0, height_mm=200.0)])
    scrap = sheet("t2", symbols=[placed("b", 10, 16, width_mm=140.0, height_mm=117.5)])
    findings = preflight.next_sheet_fill(drawing(full, scrap), FRAME)
    assert codes(findings) == ["CONTINUATION_SHEET_TOO_EMPTY"]
    assert findings[0].severity is IssueSeverity.BLOCKING
    assert "la tavola t2 e' piena solo al 20%" in findings[0].message


def test_a_full_continuation_sheet_and_a_single_sheet_say_nothing() -> None:
    full = sheet("t1", symbols=[placed("a", 20, 20, width_mm=300.0, height_mm=200.0)])
    second = sheet("t2", symbols=[placed("b", 10, 16, width_mm=350.0, height_mm=117.5)])
    assert preflight.next_sheet_fill(drawing(full, second), FRAME) == []
    assert preflight.next_sheet_fill(drawing(full), FRAME) == []


# --- 9. fonti dei simboli (C8, D-081, D-083) -----------------------------------


def test_a_symbol_citing_the_internal_convention_is_blocking() -> None:
    registry = catalog(probe_good=GOOD_SOURCE, probe_bad=preflight.INVENTED_SOURCE)
    invented = [
        placed("one", 20, 20, symbol_id="probe_bad"),
        placed("two", 60, 20, symbol_id="probe_bad"),
    ]
    findings = preflight.symbol_sources(drawing(sheet(symbols=invented)), registry)
    assert codes(findings) == ["SYMBOL_FROM_AN_INVENTED_CONVENTION"]
    assert findings[0].severity is IssueSeverity.BLOCKING
    assert "usato da 2 componenti" in findings[0].message
    assert preflight.INVENTED_SOURCE in findings[0].message
    assert findings[0].entity_ids == ["probe_bad", "one", "two"]


def test_a_symbol_absent_from_the_catalog_cannot_be_vouched_for() -> None:
    registry = catalog(probe_good=GOOD_SOURCE)
    stranger = placed("one", 20, 20, symbol_id="probe_missing")
    findings = preflight.symbol_sources(drawing(sheet(symbols=[stranger])), registry)
    assert codes(findings) == ["SYMBOL_SOURCE_NOT_VERIFIABLE"]
    assert findings[0].severity is IssueSeverity.BLOCKING
    assert "usato da 1 componente" in findings[0].message


def test_a_symbol_with_a_real_source_says_nothing() -> None:
    registry = catalog(probe_good=GOOD_SOURCE, probe_bad=preflight.INVENTED_SOURCE)
    honest = placed("one", 20, 20, symbol_id="probe_good")
    assert preflight.symbol_sources(drawing(sheet(symbols=[honest])), registry) == []


# --- l'ordine delle misure -----------------------------------------------------


def everything_wrong() -> DrawingGeometry:
    """Una geometria che sbaglia tutto, una volta per misura."""
    first = sheet(
        "t1",
        symbols=[
            placed("good", 100, 40),
            placed("near", 250, 50),
            placed("invented", 300, 200, symbol_id="probe_bad"),
        ],
        routes=[
            run("b", [at(20, 20), at(40, 20), at(40, 40), at(60, 40), at(60, 60), at(80, 60)]),
            run("h", [at(120, 100), at(200, 100)]),
            *[
                run(f"v{index}", [at(125 + index * 10, 80), at(125 + index * 10, 120)])
                for index in range(6)
            ],
            run("o1", [at(220, 60), at(240, 60)]),
            run("o2", [at(227.5, 60), at(235, 60)]),
            run("c", [at(245, 56.5), at(280, 56.5)]),
            run("u", [at(20, 150), at(80, 150), at(80, 170), at(60, 170)]),
        ],
        labels=[label("l1", anchor=at(300, 160), leader_from=at(300, 150))],
    )
    scrap = sheet("t2", symbols=[placed("scrap", 20, 20)])
    return drawing(first, scrap)


def test_preflight_runs_every_measure_in_the_declared_order() -> None:
    broken = everything_wrong()
    registry = catalog(probe_good=GOOD_SOURCE, probe_bad=preflight.INVENTED_SOURCE)
    by_measure = [
        preflight.bends_per_run(broken),
        preflight.crossings(broken, FRAME),
        preflight.longitudinal_overlap(broken, FRAME),
        preflight.clearances(broken, FRAME),
        preflight.u_turns(broken),
        preflight.orthogonality_of_leaders(broken),
        preflight.sheet_fill(broken, FRAME),
        preflight.next_sheet_fill(broken, FRAME),
        preflight.symbol_sources(broken, registry),
    ]
    assert len(by_measure) == len(preflight.MEASURE_ORDER)
    assert all(found for found in by_measure), [
        name for name, found in zip(preflight.MEASURE_ORDER, by_measure, strict=True) if not found
    ]
    expected = [item for found in by_measure for item in found]
    assert preflight.preflight_drawing(broken, FRAME, registry) == expected


def test_every_declared_measure_is_a_function_of_this_module() -> None:
    for name in preflight.MEASURE_ORDER:
        assert callable(getattr(preflight, name)), name


def test_a_clean_drawing_produces_nothing() -> None:
    quarters = [
        placed("tl", 30, 30, width_mm=60.0, height_mm=50.0),
        placed("tr", 250, 30, width_mm=60.0, height_mm=50.0),
        placed("bl", 30, 200, width_mm=60.0, height_mm=50.0),
        placed("br", 250, 200, width_mm=60.0, height_mm=50.0),
    ]
    joining = run("s", [at(90, 55), at(250, 55)])
    tidy = sheet("t1", symbols=quarters, routes=[joining], labels=[label("l1", at(120, 40))])
    registry = catalog(probe_good=GOOD_SOURCE)
    assert preflight.preflight_drawing(drawing(tidy), FRAME, registry) == []
