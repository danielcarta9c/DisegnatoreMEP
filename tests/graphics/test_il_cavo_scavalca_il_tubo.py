"""A un incrocio fra un cavo e un tubo scavalca il cavo (REL-015, I-231).

«Non vorrei che le linee elettriche facciano spostare le linee idrauliche.» La
convenzione di D-079 vuole che a scavallare sia la verticale: un tubo verticale
incrociato da un cavo orizzontale si spezzava con l'archetto, e sulla tavola unica la
tubazione aveva un'interruzione che sulla tavola idraulica non c'era. Adesso il tubo
resta intero e scavalca il cavo, in orizzontale. Fra due tubi, la regola di sempre.
Rossa sul commit di partenza.
"""
# categoria: difende il disegno

from disegnatore_mep.graphics.sheet import sheet_marks
from disegnatore_mep.layout.geometry import Point, RoutedTrunk, SheetGeometry


def _tratta(medium: str, *punti: tuple[float, float], incroci: tuple[tuple[float, float], ...] = ()) -> RoutedTrunk:
    return RoutedTrunk(
        network_id=medium,
        medium=medium,
        segments=[[Point(x_mm=x, y_mm=y) for x, y in punti]],
        crossings=[Point(x_mm=x, y_mm=y) for x, y in incroci],
    )


def _foglio(*tratte: RoutedTrunk) -> SheetGeometry:
    return SheetGeometry(sheet_id="t1", title="prova", routes=list(tratte))


def test_il_cavo_orizzontale_scavalca_il_tubo_verticale() -> None:
    tubo = _tratta("heating_water", (50, 0), (50, 100))
    cavo = _tratta("power_supply", (0, 50), (100, 50), incroci=((50, 50),))
    segni = sheet_marks(_foglio(tubo, cavo))
    assert [(mark.route_index, mark.at.x_mm, mark.at.y_mm) for mark in segni.hops] == [(1, 50, 50)]


def test_il_cavo_verticale_scavalca_il_tubo_orizzontale() -> None:
    tubo = _tratta("heating_water", (0, 50), (100, 50))
    cavo = _tratta("control_bus", (50, 0), (50, 100), incroci=((50, 50),))
    assert [mark.route_index for mark in sheet_marks(_foglio(tubo, cavo)).hops] == [1]


def test_fra_due_tubi_scavalca_la_verticale_come_sempre() -> None:
    verticale = _tratta("heating_water", (50, 0), (50, 100))
    orizzontale = _tratta("cold_water", (0, 50), (100, 50), incroci=((50, 50),))
    assert [mark.route_index for mark in sheet_marks(_foglio(verticale, orizzontale)).hops] == [0]


def test_l_archetto_del_cavo_e_orizzontale_e_il_tubo_resta_intero() -> None:
    from disegnatore_mep.graphics.frame import ORDINARY_FRAMES
    from disegnatore_mep.graphics.registry import SymbolRegistry
    from disegnatore_mep.graphics.sheet import render_sheet

    tubo = _tratta("heating_water", (100, 60), (100, 160))
    cavo = _tratta("power_supply", (50, 110), (150, 110), incroci=((100, 110),))
    svg = render_sheet(_foglio(tubo, cavo), ORDINARY_FRAMES[0], SymbolRegistry([]))
    assert 'points="100,60 100,160"' in svg
    assert 'd="M98.75 110 A1.25 1.25 0 0 1 101.25 110"' in svg
