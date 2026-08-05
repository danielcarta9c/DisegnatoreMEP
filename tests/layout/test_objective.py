"""La regola che il PM ha dettato, misurata sul caso D-011.

«La regola e' minimizzare le curve disegnate, minimizzare gli attraversamenti
tra linee e minimizzare la lunghezza delle linee, mantenendo pero' ordinamenti
da sinistra a destra.»

Sono tre numeri e un vincolo, quindi si misurano. Le soglie sono quelle
raggiunte: servono a impedire che una modifica futura peggiori la tavola senza
che nessuno se ne accorga, non a descrivere un ottimo teorico.

Da quando la disposizione serve le linee (D-078, `improve.py`), le soglie sono
quelle **dopo** il ciclo di miglioramento: pieghe scese da 25 a 23 e lunghezza
da 975 a 887,5 mm, nodi condivisi fermi a 9. Il criterio rivisto del
pacchetto WP3 e' «nessuna voce peggiore, almeno una strettamente migliore»:
una ricerca esaustiva su seicento disposizioni per traslazione ha mostrato
che sotto i 9 nodi condivisi si scende solo pagando 27 pieghe — 4 dei 9 sono
le derivazioni obbligate sulle due porte condivise, gli altri 5 incroci
topologicamente forzati da quest'ordine di fasce.
"""

from functools import cache
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import compose_drawing
from disegnatore_mep.layout.geometry import SheetGeometry

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"

STEP_MM = 2.5


@cache
def sheet() -> SheetGeometry:
    """Composta una volta per modulo: il ciclo di miglioramento reinstrada
    decine di volte, e ogni prova la leggerebbe identica."""
    registry = ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
    return compose_drawing(load_project(PROJECT), registry, NOVE_C_A3).sheets[0]


def polylines(drawn: SheetGeometry) -> list[list[tuple[float, float]]]:
    return [
        [(point.x_mm, point.y_mm) for point in segment]
        for route in drawn.routes
        for segment in route.segments
    ]


def bends(drawn: SheetGeometry) -> int:
    return sum(max(len(line) - 2, 0) for line in polylines(drawn))


def length_mm(drawn: SheetGeometry) -> float:
    return sum(
        abs(after[0] - before[0]) + abs(after[1] - before[1])
        for line in polylines(drawn)
        for before, after in zip(line, line[1:], strict=False)
    )


def edges(line: list[tuple[float, float]]) -> set[tuple[tuple[float, float], ...]]:
    """I singoli tratti di griglia percorsi, non i nodi toccati."""
    walked: set[tuple[tuple[float, float], ...]] = set()
    for before, after in zip(line, line[1:], strict=False):
        steps = int(
            round((abs(after[0] - before[0]) + abs(after[1] - before[1])) / STEP_MM)
        )
        for index in range(steps):
            walked.add(
                tuple(
                    sorted(
                        (
                            (
                                round(before[0] + (after[0] - before[0]) * index / steps, 3),
                                round(before[1] + (after[1] - before[1]) * index / steps, 3),
                            ),
                            (
                                round(before[0] + (after[0] - before[0]) * (index + 1) / steps, 3),
                                round(before[1] + (after[1] - before[1]) * (index + 1) / steps, 3),
                            ),
                        )
                    )
                )
            )
    return walked


def cells(line: list[tuple[float, float]]) -> set[tuple[float, float]]:
    walked: set[tuple[float, float]] = set()
    for before, after in zip(line, line[1:], strict=False):
        steps = int(
            round((abs(after[0] - before[0]) + abs(after[1] - before[1])) / STEP_MM)
        )
        for index in range(steps + 1):
            ratio = index / steps if steps else 0.0
            walked.add(
                (
                    round(before[0] + (after[0] - before[0]) * ratio, 3),
                    round(before[1] + (after[1] - before[1]) * ratio, 3),
                )
            )
    return walked


def shared_cells(drawn: SheetGeometry) -> int:
    walked = [cells(line) for line in polylines(drawn)]
    return sum(
        len(walked[first] & walked[second])
        for first in range(len(walked))
        for second in range(first + 1, len(walked))
    )


def test_no_two_runs_are_drawn_on_top_of_each_other() -> None:
    """Vietato sovrapporre longitudinalmente: sempre separate e ben distinte.

    L'unica sovrapposizione ammessa e' l'ultimo tratto contro una porta che due
    tratte condividono — due ritorni di zona su un solo attacco del volano — che
    sulla tavola e' una derivazione ed e' lungo un passo di griglia.
    """
    drawn = sheet()
    walked = [(line, edges(line)) for line in polylines(drawn)]
    for first in range(len(walked)):
        for second in range(first + 1, len(walked)):
            shared = walked[first][1] & walked[second][1]
            assert len(shared) <= 1, (
                len(shared) * STEP_MM,
                walked[first][0],
                walked[second][0],
            )


def test_the_drawing_stays_within_its_bend_budget() -> None:
    """Prima erano 31 su tredici tratte, con sali-scendi intorno a ogni pezzo;
    25 col posizionamento a fasce; 23 da quando i componenti si spostano per
    servire le linee (D-078). Strettamente sotto il valore pre-miglioramento."""
    assert bends(sheet()) <= 23


def test_the_drawing_stays_within_its_crossing_budget() -> None:
    """Prima erano ventiquattro nodi condivisi fra tratte diverse; 9 col
    posizionamento a fasce, e 9 restano dopo il miglioramento: 4 sono le
    derivazioni obbligate sulle due porte condivise, 5 gli incroci forzati
    dalla topologia con quest'ordine di fasce. Il ciclo di miglioramento non
    puo' accettare mosse che li aumentino (regola di accettazione di WP3)."""
    assert shared_cells(sheet()) <= 9


def test_the_drawing_stays_within_its_length_budget() -> None:
    """Il criterio di WP3 ammetteva fino al +10% sul valore pre-miglioramento
    (975 mm, quindi 1072,5); il ciclo l'ha invece **accorciata** a 887,5 mm,
    e la soglia si fissa sul raggiunto."""
    assert length_mm(sheet()) <= 887.5


def test_a_component_stands_to_the_right_of_what_feeds_it() -> None:
    """Il vincolo della regola: l'ordine da sinistra a destra.

    La valvola deviatrice e' alimentata dalla pompa di calore, quindi le sta a
    destra. Prima ci finiva sopra, e la mandata doveva girarle intorno.
    """
    placed = {item.component_id: item for item in sheet().symbols}
    order = ["hp", "dv", "buffer", "manifold", "radiators"]
    for before, after in zip(order, order[1:], strict=False):
        assert placed[before].origin.x_mm < placed[after].origin.x_mm, (before, after)


def test_a_run_between_aligned_ports_is_a_straight_line() -> None:
    """Zero pieghe: e' il caso in cui il posizionamento ha fatto il suo lavoro."""
    drawn = sheet()
    straight = {
        ",".join(route.connection_ids)
        for route in drawn.routes
        for segment in route.segments
        if len(segment) == 2
    }
    assert "p1" in straight, straight  # pompa di calore -> valvola deviatrice
    assert "s1,s2" in straight, straight  # volano -> circolatore -> collettore


def test_parallel_branches_are_stacked_not_strung_out() -> None:
    """Due zone servite dallo stesso collettore stanno una sopra l'altra."""
    placed = {item.component_id: item for item in sheet().symbols}
    radiators, underfloor = placed["radiators"], placed["underfloor"]
    assert radiators.origin.x_mm == underfloor.origin.x_mm
    assert radiators.bottom_mm < underfloor.origin.y_mm


def test_no_run_climbs_above_the_plant_without_a_reason() -> None:
    """L'anti sali-scendi: nessuna tratta sale piu' in alto di quanto le serva.

    Il difetto che si chiude qui: una corsia dichiarata a meta' foglio si
    prendeva anche i collegamenti di dieci millimetri, che ci salivano e ne
    riscendevano subito.
    """
    drawn = sheet()
    highest_symbol = min(item.origin.y_mm for item in drawn.symbols)
    for route in drawn.routes:
        for segment in route.segments:
            top = min(point.y_mm for point in segment)
            assert top >= highest_symbol - 10.0, (route.connection_ids, top)
