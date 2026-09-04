"""Le regole di composizione, misurate su una tavola di riferimento.

Il PM ha fornito uno schema reale — pompa di calore monoblocco con ACS,
compensatore e circolatore — e ha detto che quello e' il livello di ordine e
disposizione atteso. Queste prove fissano cio' che ne e' stato ricavato, cosi'
che il motore non possa tornare a impilare i componenti in colonne.
"""

from functools import cache
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import compose_drawing
from disegnatore_mep.layout.composition import (
    AUXILIARY_BAND,
    CALLOUT_BAND,
    GROUND_LINE,
    Standing,
    standing_of,
)
from disegnatore_mep.layout.geometry import SheetGeometry

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"


@cache
def sheet() -> SheetGeometry:
    """Composta una volta per modulo: il ciclo di miglioramento reinstrada
    decine di volte, e ogni prova la leggerebbe identica."""
    registry = ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
    return compose_drawing(load_project(PROJECT), registry, NOVE_C_A3).sheets[0]


def area_y(fraction: float) -> float:
    rect = NOVE_C_A3.drawing_rect_mm
    step = NOVE_C_A3.standard.grid_mm
    return rect.y_mm + round(rect.height_mm * fraction / step) * step


def test_the_ground_line_is_not_on_the_sheet() -> None:
    """La quota di terra e' un riferimento interno della posa, non un elemento
    della tavola (D-121, DRAW-003): la geometria non la esporta."""
    drawn = sheet()
    assert drawn.ground_line_y_mm is None


def test_the_drawn_block_is_centred_in_the_drawing_area() -> None:
    """Un impianto basso non lascia vuoti i due terzi alti del foglio.

    Non si rimedia ingrandendo — la scala di stampa e' invariante (ADR 0003) —
    quindi il blocco resta quello che e' e si mette in mezzo.
    """
    drawn = sheet()
    area = NOVE_C_A3.drawing_rect_mm
    # Il blocco che si centra sono simboli e tratte: i testi si posano dopo e
    # non entrano nella centratura (DRAW-003). Misurare il fondo sui soli testi valeva finche' i richiami stavano
    # in una riga sotto il disegno, e D-075 quella riga l'ha ritirata.
    tops = [item.origin.y_mm for item in drawn.symbols]
    bottoms = [item.bottom_mm for item in drawn.symbols]
    for route in drawn.routes:
        for segment in route.segments:
            tops.extend(point.y_mm for point in segment)
            bottoms.extend(point.y_mm for point in segment)
    above = min(tops) - area.y_mm
    below = area.bottom_mm - max(bottoms)
    assert abs(above - below) <= 10.0, (above, below)


def test_machines_and_storage_stand_on_the_ground() -> None:
    """Appoggiati, non appesi: e' la prima cosa che si vede in una tavola vera.

    La **posa** li allinea in basso fra loro. Da DRAW-004 la quota di terra e'
    un suggerimento di posa, non un vincolo: la rifinitura puo' alzare una
    macchina per mettere le porte in asse, se il modello non dichiara un
    vincolo fisico, e nessuna scende sotto la quota di posa. Sulla tavola
    composta, quindi, nessuna macchina sta piu' in basso della piu' bassa
    posata, e la piu' bassa e' ancora appoggiata.
    """
    from disegnatore_mep.layout.compose import inline_component_ids
    from disegnatore_mep.layout.partition import partition_project
    from disegnatore_mep.layout.place import place_sheet
    from disegnatore_mep.layout.trunks import build_trunks

    project = load_project(PROJECT)
    registry = ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )
    inline = inline_component_ids(project, registry)
    partition = partition_project(project, build_trunks(project, inline))[0]
    placed = {
        item.component_id: item
        for item in place_sheet(project, partition, registry, NOVE_C_A3, inline)
    }
    machines = ("hp", "cylinder", "buffer")
    assert len({placed[component_id].bottom_mm for component_id in machines}) == 1

    # Sulla tavola composta la centratura trasla tutto il blocco insieme:
    # si confrontano le distanze fra le macchine, non le quote assolute. Chi
    # e' salito lo ha fatto di passi interi, e nessuna e' scesa sotto la
    # quota di posa comune.
    drawn = {item.component_id: item for item in sheet().symbols}
    step = NOVE_C_A3.standard.grid_mm
    lowest = max(drawn[component_id].bottom_mm for component_id in machines)
    placed_ground = placed["hp"].bottom_mm
    for component_id in machines:
        lifted = lowest - drawn[component_id].bottom_mm
        assert lifted >= 0.0
        assert lifted % step == 0.0, (component_id, lifted)
        assert placed[component_id].bottom_mm == placed_ground


def test_an_inline_accessory_rides_its_own_run() -> None:
    """Un filtro sta **su** una tratta e non puo' lasciarla.

    Prima si pretendeva anche che la sua tratta corresse bassa, come sul
    riferimento dove filtro e riempimento stanno vicino a terra, e per ottenerlo
    l'instradamento provava le corsie basse per prime. Quella preferenza e'
    stata tolta: comprava pieghe per soddisfare una convenzione, e il PM ha
    messo le pieghe al primo posto. Cio' che resta garantito e' che
    l'accessorio stia sopra la linea di terra e sul proprio percorso — nella
    giacitura del tratto su cui cade (D-027): da quando gli accessori seguono
    l'ordine della catena, un filtro puo' legittimamente stare sul tratto
    verticale subito a valle della propria valvola.
    """
    drawn = sheet()
    strainer = next(item for item in drawn.symbols if item.component_id == "strainer")
    floor = max(item.bottom_mm for item in drawn.symbols if item.component_id == "hp")
    assert strainer.bottom_mm <= floor + 1e-9
    centre_x = (strainer.origin.x_mm + strainer.right_mm) / 2
    centre_y = (strainer.origin.y_mm + strainer.bottom_mm) / 2
    # Il simbolo sta **dentro l'interruzione** che ha aperto, quindi non tocca
    # nessun tratto disegnato: quello che deve valere e' che i due monconi lo
    # prendano in mezzo, allineati con lui, qualunque sia la giacitura.
    run = next(item for item in drawn.routes if "p2" in item.connection_ids)
    ends = [segment[-1] for segment in run.segments] + [
        segment[0] for segment in run.segments
    ]
    on_row = [item for item in ends if abs(item.y_mm - centre_y) <= 1e-9]
    on_column = [item for item in ends if abs(item.x_mm - centre_x) <= 1e-9]
    rides_horizontally = any(item.x_mm < centre_x for item in on_row) and any(
        item.x_mm > centre_x for item in on_row
    )
    rides_vertically = any(item.y_mm < centre_y for item in on_column) and any(
        item.y_mm > centre_y for item in on_column
    )
    assert rides_horizontally or rides_vertically, ends


def test_the_size_hierarchy_reads_like_the_reference() -> None:
    """Sul riferimento una macchina sta a una valvola come 5,3 a 1 in misura
    lineare. La gerarchia precedente le teneva a 2,7 e non si distinguevano."""
    registry = SymbolRegistry.from_directory(SYMBOLS)
    machine = registry.get("heat-pump-air-water").manifest
    valve = registry.get("valve-isolation").manifest
    assert machine.height_mm / valve.height_mm >= 5.0
    storage = registry.get("dhw-cylinder").manifest
    assert storage.height_mm > machine.height_mm


def test_supply_attachments_sit_above_return_attachments() -> None:
    """Mandata sopra, ritorno sotto: la convenzione sta **nei simboli**.

    E' li' che decide davvero, perche' la tubazione arriva dove l'attacco la
    chiama. Sulla corsia la convenzione non si puo' pretendere: dove due tratte
    devono scavalcare lo stesso ostacolo, la prima prende la quota piu' vicina e
    la seconda quella sopra, e chi sia la prima lo decide l'ordine del modello.
    Imporlo costerebbe pieghe, che il PM ha messo al primo posto; la mandata e
    il ritorno restano distinti da colore e tratto (D-057).
    """
    from disegnatore_mep.graphics.registry import SymbolRegistry

    registry = SymbolRegistry.from_directory(SYMBOLS)

    def port_y(symbol_id: str, port_id: str) -> float:
        manifest = registry.get(symbol_id).manifest
        return next(item.y_mm for item in manifest.ports if item.id == port_id)

    assert port_y("heat-pump-air-water", "water_supply") < port_y(
        "heat-pump-air-water", "water_return"
    )
    assert port_y("buffer-four-port", "primary_in") < port_y(
        "buffer-four-port", "primary_out"
    )
    assert port_y("buffer-four-port", "secondary_out") < port_y(
        "buffer-four-port", "secondary_in"
    )
    assert port_y("dhw-cylinder", "coil_in") < port_y("dhw-cylinder", "coil_out")


def test_supply_and_return_runs_are_both_drawn() -> None:
    routes = sheet().routes
    assert any(item.supply for item in routes)
    assert any(not item.supply for item in routes)


def test_supply_and_return_are_different_lines() -> None:
    from disegnatore_mep.layout.legend import style_for

    routes = sheet().routes
    styles = {(style_for(item.medium, item.supply)) for item in routes}
    assert len(styles) >= 2


def test_labels_sit_beside_their_component_without_a_leader() -> None:
    """D-075: una sigla e' una scritta piccola accanto al proprio pezzo.

    La riga di richiami a fondo tavola e' ritirata: era ortogonale e sottile
    come una tubazione, quindi indistinguibile da una. Il richiamo esiste solo
    quando il testo non ci sta, ed e' obliquo a 45 gradi.
    """
    drawn = sheet()
    assert drawn.labels
    placed = {item.component_id: item for item in drawn.symbols}
    for label in drawn.labels:
        # La scritta puo' scendere anche sotto la quota di terra (D-121): li'
        # non c'e' nessun pavimento, e il divieto non era mai stato deciso da
        # nessuno. Cio' che si chiede resta che stia **accanto al proprio
        # pezzo**, ed e' la riga qui sotto.
        if label.leader_from is not None:
            continue
        symbol = placed.get(label.id.rsplit("-", 1)[0])
        if symbol is None:
            continue
        near_x = symbol.origin.x_mm - 25.0 <= label.anchor.x_mm <= symbol.right_mm + 25.0
        near_y = symbol.origin.y_mm - 25.0 <= label.anchor.y_mm <= symbol.bottom_mm + 25.0
        assert near_x and near_y, label.id


def test_a_leader_starts_on_the_component_it_names() -> None:
    drawn = sheet()
    placed = {item.component_id: item for item in drawn.symbols}
    for label in drawn.labels:
        if label.leader_from is None:
            continue
        component_id = label.id.rsplit("-", 1)[0]
        symbol = placed.get(component_id)
        if symbol is None:
            continue
        # Da uno spigolo del proprio pezzo, quello verso cui la diagonale punta.
        assert label.leader_from.x_mm in (symbol.origin.x_mm, symbol.right_mm)
        assert label.leader_from.y_mm in (symbol.origin.y_mm, symbol.bottom_mm)


def test_standing_is_decided_by_size_and_function_not_by_name() -> None:
    assert standing_of(45.0, frozenset({"dhw_storage"}), False) is Standing.GROUND
    assert standing_of(5.0, frozenset({"isolation"}), True) is Standing.RAIL
    assert standing_of(15.0, frozenset({"expansion"}), False) is Standing.AUXILIARY
    # Un filtro e' in linea, ma la sua funzione lo porta comunque in basso.
    assert standing_of(5.0, frozenset({"filtration"}), True) is Standing.AUXILIARY


def test_the_reference_proportions_are_ordered() -> None:
    assert CALLOUT_BAND > GROUND_LINE > AUXILIARY_BAND
