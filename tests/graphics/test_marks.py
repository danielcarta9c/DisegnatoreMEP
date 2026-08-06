"""I segni sui punti notevoli: lo scavallo sull'incrocio, il pallino sul nodo.

D-079: «un incrocio fra due linee che non si collegano si disegna con il proprio
scavallo, e scavalca la linea verticale; un collegamento porta il pallino pieno
di diametro quattro volte lo spessore del tratto». Prima i due punti avevano lo
stesso identico segno, cioe' nessuno, e chi legge non poteva distinguerli.
"""

from xml.etree import ElementTree

from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import (
    CROSSING_ARC_RADIUS_MM,
    JUNCTION_DOT_WIDTHS,
    render_sheet,
    sheet_marks,
)
from disegnatore_mep.layout.geometry import Point, RoutedTrunk, SheetGeometry

LINE_MM = NOVE_C_A3.standard.line_medium_mm


def at(x_mm: float, y_mm: float) -> Point:
    return Point(x_mm=x_mm, y_mm=y_mm)


def run(
    name: str,
    *points: tuple[float, float],
    crossings: tuple[tuple[float, float], ...] = (),
) -> RoutedTrunk:
    return RoutedTrunk(
        network_id=name,
        medium="heating_water",
        connection_ids=[name],
        segments=[[at(x, y) for x, y in points]],
        crossings=[at(x, y) for x, y in crossings],
    )


def sheet(*routes: RoutedTrunk) -> SheetGeometry:
    return SheetGeometry(sheet_id="t1", title="prova", routes=list(routes))


def drawn(*routes: RoutedTrunk) -> ElementTree.Element:
    return ElementTree.fromstring(
        render_sheet(sheet(*routes), NOVE_C_A3, SymbolRegistry([]))
    )


def marked(root: ElementTree.Element, name: str) -> list[ElementTree.Element]:
    return [item for item in root.iter() if item.get("class") == name]


def polylines(root: ElementTree.Element) -> list[str]:
    return [item.get("points", "") for item in marked(root, "run")]


# Una verticale che attraversa un'orizzontale. L'incrocio lo registra
# l'instradamento sulla tratta che passa per ultima: qui la verticale.
VERTICAL = run("v", (120.0, 90.0), (120.0, 110.0), crossings=((120.0, 100.0),))
HORIZONTAL = run("h", (100.0, 100.0), (140.0, 100.0))


def test_a_crossing_on_a_vertical_run_gets_its_arc() -> None:
    marks = sheet_marks(sheet(HORIZONTAL, VERTICAL))
    assert len(marks.hops) == 1
    assert marks.hops[0].at == at(120.0, 100.0)
    assert sheet(HORIZONTAL, VERTICAL).routes[marks.hops[0].route_index].network_id == "v"
    assert len(marked(drawn(HORIZONTAL, VERTICAL), "crossing-hop")) == 1


def test_the_horizontal_run_of_the_same_crossing_stays_whole() -> None:
    """La convenzione: scavalca la verticale, l'orizzontale prosegue intera."""
    root = drawn(HORIZONTAL, VERTICAL)
    assert "100,100 140,100" in polylines(root)


def test_the_arc_hops_the_point_with_the_declared_radius() -> None:
    path = marked(drawn(HORIZONTAL, VERTICAL), "crossing-hop")[0]
    assert path.get("d") == (
        f"M120 {100 - CROSSING_ARC_RADIUS_MM:g} "
        f"A{CROSSING_ARC_RADIUS_MM:g} {CROSSING_ARC_RADIUS_MM:g} 0 0 1 "
        f"120 {100 + CROSSING_ARC_RADIUS_MM:g}"
    )
    assert path.get("stroke-width") == f"{LINE_MM:g}"


def test_the_hopping_run_is_interrupted_under_its_own_arc() -> None:
    """Un archetto sopra la linea intera e' un semicerchio con la sua corda."""
    lines = polylines(drawn(HORIZONTAL, VERTICAL))
    assert f"120,90 120,{100 - CROSSING_ARC_RADIUS_MM:g}" in lines
    assert f"120,{100 + CROSSING_ARC_RADIUS_MM:g} 120,110" in lines


def test_the_arc_goes_on_the_vertical_run_whoever_recorded_the_crossing() -> None:
    """L'instradamento registra l'incrocio sulla tratta che passa per ultima,
    che puo' benissimo essere l'orizzontale: e' la giacitura a decidere, non
    l'ordine di calcolo."""
    horizontal = run("h", (100.0, 100.0), (140.0, 100.0), crossings=((120.0, 100.0),))
    vertical = run("v", (120.0, 90.0), (120.0, 110.0))
    marks = sheet_marks(sheet(horizontal, vertical))
    assert len(marks.hops) == 1
    assert marks.hops[0].route_index == 1
    root = drawn(horizontal, vertical)
    assert len(marked(root, "crossing-hop")) == 1
    assert "100,100 140,100" in polylines(root)


def test_a_crossing_that_falls_on_a_bend_gets_no_arc() -> None:
    """D-079: «un archetto su un angolo non si legge»."""
    straight = run("h", (90.0, 100.0), (130.0, 100.0))
    bent = run("b", (120.0, 80.0), (120.0, 100.0), (130.0, 100.0),
               crossings=((120.0, 100.0),))
    marks = sheet_marks(sheet(straight, bent))
    assert marks.hops == ()
    assert marks.skipped_on_bends == 1
    assert marked(drawn(straight, bent), "crossing-hop") == []


def test_a_crossing_too_close_to_a_bend_gets_no_arc() -> None:
    """Il raggio non ci sta: l'archetto uscirebbe dall'angolo."""
    horizontal = run("h", (100.0, 91.0), (140.0, 91.0))
    vertical = run("v", (120.0, 90.0), (120.0, 110.0), (140.0, 110.0),
                   crossings=((120.0, 91.0),))
    marks = sheet_marks(sheet(horizontal, vertical))
    assert marks.hops == ()
    assert marks.skipped_on_bends == 1


# --- il pallino ---------------------------------------------------------------


def test_two_runs_that_end_on_the_same_port_get_a_junction_dot() -> None:
    first = run("a", (100.0, 100.0), (120.0, 100.0))
    second = run("b", (120.0, 100.0), (120.0, 120.0))
    marks = sheet_marks(sheet(first, second))
    assert [mark.at for mark in marks.junctions] == [at(120.0, 100.0)]
    dots = marked(drawn(first, second), "junction")
    assert len(dots) == 1
    assert (dots[0].get("cx"), dots[0].get("cy")) == ("120", "100")


def test_the_junction_dot_is_four_line_widths_across() -> None:
    """UNI 9511 Tab. 1, tramite SRC-016."""
    first = run("a", (100.0, 100.0), (120.0, 100.0))
    second = run("b", (120.0, 100.0), (120.0, 120.0))
    dot = marked(drawn(first, second), "junction")[0]
    assert float(dot.get("r", "0")) * 2 == JUNCTION_DOT_WIDTHS * LINE_MM
    assert dot.get("fill") not in (None, "none")


def test_a_run_that_ends_on_another_run_is_a_junction_not_a_crossing() -> None:
    """Una derivazione a T: un capo cade in mezzo all'altra tratta."""
    through = run("a", (100.0, 100.0), (140.0, 100.0))
    branch = run("b", (120.0, 100.0), (120.0, 120.0), crossings=((120.0, 100.0),))
    marks = sheet_marks(sheet(through, branch))
    assert marks.hops == ()
    assert marks.skipped_as_junctions == 1
    assert [mark.at for mark in marks.junctions] == [at(120.0, 100.0)]
    root = drawn(through, branch)
    assert marked(root, "crossing-hop") == []
    assert len(marked(root, "junction")) == 1


def test_two_runs_that_only_share_a_stretch_get_neither_sign() -> None:
    """L'ultimo tratto contro un attacco condiviso e' una derivazione, non un
    incrocio: la si riconosce perche' li' nessuna delle due e' verticale."""
    first = run("a", (100.0, 100.0), (130.0, 100.0))
    second = run("b", (110.0, 90.0), (110.0, 100.0), (130.0, 100.0),
                 crossings=((125.0, 100.0),))
    marks = sheet_marks(sheet(first, second))
    assert marks.hops == ()
    assert marks.skipped_without_a_crossed_line == 1


def test_nothing_is_drawn_when_nothing_crosses() -> None:
    root = drawn(run("a", (100.0, 100.0), (140.0, 100.0)))
    assert marked(root, "crossing-hop") == []
    assert marked(root, "junction") == []
    assert polylines(root) == ["100,100 140,100"]


def test_the_marks_are_deterministic() -> None:
    first = sheet_marks(sheet(HORIZONTAL, VERTICAL))
    second = sheet_marks(sheet(HORIZONTAL, VERTICAL))
    assert first == second
