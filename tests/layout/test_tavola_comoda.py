"""Le prove di DRAW-013: la tavola si allarga tutta insieme e non tocca il bordo.

Il PO, il 18 settembre 2026, guardando le tavole della PR #41:

    «Ha poco senso questo stretch fatto cosi' per il gusto di riempire la
    tavola. Se devo rendere comoda la tavola **allargo tutte le linee di un X
    per cento**, non che allungo solo un tratto per prendere piu' spazio, e'
    proprio brutto cosi'. Era meglio prima.»

    «Non si mettono gli oggetti cosi' vicini al bordo del foglio a meno che non
    ci sia un disegno molto molto pieno.»

    «Serbatoio, pompa, tratto dritto, curva, e giu' attacchi i terminali. Si fa
    sempre cosi', puoi prenderla come best practice.»

Qui si prova che sono **queste** le regole, e non una taratura migliorata:

- **§A / D-142**: la dilatazione proporzionale allarga tutti i vuoti dello
  stesso fattore, non cambia ne' pieghe ne' attraversamenti, e non e' mai una
  contrazione;
- **§B / D-143**: il margine parte da venticinque millimetri e si stringe solo
  per far entrare un disegno, e il preflight lo dice nei due versi;
- **§C / D-144**: la distribuzione ha la forma dettata — gamba dritta, **una**
  curva, dorsale, terminali a pettine — e quella curva non e' una cessione;
- **§E / D-141**: la guardia del riempimento e' un divieto e non una soglia, e
  il caso lieve non vince;
- **§G / D-145**: un organo di servizio sta addosso al pezzo che serve, ed e'
  un vincolo che nessun costo compra.
"""

from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.symbol import PortFace
from disegnatore_mep.layout.dilate import (
    _gaps,
    _rigid_spans,
    dilate_sheet,
    dilated_to_fit,
    factor_error,
)
from disegnatore_mep.layout.geometry import (
    SHEET_MARGIN_MIN_MM,
    SHEET_MARGIN_MM,
    DrawingGeometry,
    PlacedSymbol,
    Point,
    RoutedTrunk,
    SheetGeometry,
    border_margin_mm,
    ink_box,
    ink_coverage,
    margin_allowed_mm,
    moves_of,
)
from disegnatore_mep.layout.highways import (
    Highway,
    PortAt,
    lies_in_line,
    turns_of,
)
from disegnatore_mep.layout.improve import SheetCost
from disegnatore_mep.model.project import PortRef
from disegnatore_mep.validation.preflight import preflight_drawing

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"

STEP_MM = 2.5
TOLERANCE_MM = 1e-6
AREA = NOVE_C_A3.drawing_rect_mm
RECT = (AREA.x_mm, AREA.y_mm, AREA.right_mm, AREA.bottom_mm)


@cache
def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def _symbol(component_id: str, x_mm: float, y_mm: float, w: float, h: float) -> PlacedSymbol:
    return PlacedSymbol(
        component_id=component_id,
        symbol_id=component_id,
        rotation_deg=0,
        origin=Point(x_mm=x_mm, y_mm=y_mm),
        width_mm=w,
        height_mm=h,
    )


def _route(network_id: str, *points: tuple[float, float]) -> RoutedTrunk:
    return RoutedTrunk(
        network_id=network_id,
        connection_ids=[network_id],
        segments=[[Point(x_mm=x, y_mm=y) for x, y in points]],
    )


def una_tavola_da_allargare() -> SheetGeometry:
    """Una tavola finta con vuoti di misura diversa, su griglia.

    Non e' un impianto: e' la **struttura** su cui la dilatazione lavora — fasce
    rigide e vuoti — e serve perche' una regola provata su una sola tavola vera
    e' una coincidenza. I vuoti sono di venti, dieci e quaranta passi, cosi' che
    il fattore resti esatto su tutti e tre e la prova misuri la regola invece
    dell'arrotondamento della griglia.
    """
    return SheetGeometry(
        sheet_id="t1",
        title="prova",
        symbols=[
            _symbol("a", 60.0, 66.0, 20.0, 20.0),
            _symbol("b", 130.0, 66.0, 10.0, 10.0),
            _symbol("c", 165.0, 66.0, 20.0, 20.0),
            _symbol("d", 130.0, 186.0, 10.0, 10.0),
        ],
        routes=[
            _route("mandata", (80.0, 71.0), (130.0, 71.0)),
            _route("seguito", (140.0, 71.0), (165.0, 71.0)),
            _route("discesa", (135.0, 76.0), (135.0, 186.0)),
        ],
    )


def _gap_list(sheet: SheetGeometry) -> tuple[list[float], list[float]]:
    box = ink_box(sheet.symbols, sheet.routes)
    assert box is not None
    return (
        _gaps(_rigid_spans(sheet.symbols, True), box[0], box[2]),
        _gaps(_rigid_spans(sheet.symbols, False), box[1], box[3]),
    )


def _bends(sheet: SheetGeometry) -> int:
    return sum(
        max(len(moves_of(segment)) - 1, 0)
        for route in sheet.routes
        for segment in route.segments
    )


def _crossings(sheet: SheetGeometry) -> int:
    return sum(len(route.crossings) for route in sheet.routes)


# ---------------------------------------------------------------------------
# §A — la tavola comoda si ottiene dilatando tutto (D-142)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("factor", [1.5, 2.0, 2.5])
def test_la_dilatazione_allarga_tutti_i_vuoti_della_stessa_percentuale(
    factor: float,
) -> None:
    """Il criterio 1, per intero: tutte le distanze fra i pezzi crescono della
    stessa percentuale, e **niente altro cambia**.

    E' la differenza fra questa mossa e lo stiramento del singolo tratto che il
    PO ha bocciato: li' una tratta si allungava e le altre no, qui crescono
    tutte insieme. I simboli restano della loro misura — la scala di stampa e'
    invariante (ADR 0003) — quindi il disegno cresce **conservando la propria
    forma**.
    """
    sheet = una_tavola_da_allargare()
    grown = dilate_sheet(sheet, factor, STEP_MM)

    assert factor_error(sheet, factor, STEP_MM) <= TOLERANCE_MM

    before_x, before_y = _gap_list(sheet)
    after_x, after_y = _gap_list(grown)
    assert len(before_x) == len(after_x) and len(before_y) == len(after_y)
    for was, now in zip(before_x + before_y, after_x + after_y, strict=True):
        assert abs(now - was * factor) <= TOLERANCE_MM, (was, now, factor)

    # I simboli: stessa misura, e nessuno si e' scavalcato.
    sizes = {item.component_id: (item.width_mm, item.height_mm) for item in sheet.symbols}
    for item in grown.symbols:
        assert (item.width_mm, item.height_mm) == sizes[item.component_id]
    order = [item.component_id for item in sorted(sheet.symbols, key=lambda s: s.origin.x_mm)]
    after = [item.component_id for item in sorted(grown.symbols, key=lambda s: s.origin.x_mm)]
    assert order == after

    # Pieghe e attraversamenti: gli stessi. La funzione dell'asse lavora su un
    # asse per volta, quindi un tratto orizzontale resta orizzontale e nessuna
    # piega nasce; gli attraversamenti sono gli stessi punti, portati avanti.
    assert _bends(grown) == _bends(sheet)
    assert _crossings(grown) == _crossings(sheet)


def test_la_dilatazione_non_crea_la_propaggine_che_la_copertura_cerca() -> None:
    """La copertura dell'ingombro **si misura**, e il pacchetto la dava per
    invariante: non lo e', e il rapporto lo porta.

    `ink_coverage` divide l'ingombro in sessantaquattro celle relative
    all'ingombro stesso: quando l'ingombro cresce le celle crescono con lui, e
    una tavola scarica puo' perderne una senza che un pezzo si sia mosso. Cio'
    che D-141 cerca davvero — **un pezzo spinto in un angolo** — la dilatazione
    non lo puo' fare, e questo si prova sulla struttura invece che sul numero:
    i vuoti crescono tutti uguali, quindi nessun pezzo si allontana dagli altri
    piu' degli altri.
    """
    sheet = una_tavola_da_allargare()
    grown = dilate_sheet(sheet, 1.5, STEP_MM)
    prima = ink_coverage(sheet.symbols, sheet.routes, ink_box(sheet.symbols, sheet.routes))
    dopo = ink_coverage(grown.symbols, grown.routes, ink_box(grown.symbols, grown.routes))
    assert dopo < prima  # la misura si muove, ed e' un fatto della misura
    before_x, before_y = _gap_list(sheet)
    after_x, after_y = _gap_list(grown)
    fattori = {
        round(now / was, 6)
        for was, now in zip(before_x + before_y, after_x + after_y, strict=True)
        if was > TOLERANCE_MM
    }
    assert fattori == {1.5}  # nessun vuoto e' cresciuto piu' degli altri


def test_la_dilatazione_conserva_le_colonne_e_le_quote() -> None:
    """Chi stava in colonna resta in colonna, chi stava in quota resta in quota.

    E' la ragione per cui la funzione e' **una sola per asse**: due pezzi con la
    stessa ascissa la ricevono uguale anche dopo. Senza questo la dorsale di
    D-144 si sfilaccerebbe alla prima dilatazione.
    """
    sheet = una_tavola_da_allargare()
    grown = dilate_sheet(sheet, 2.0, STEP_MM)
    was = {item.component_id: item.origin for item in sheet.symbols}
    now = {item.component_id: item.origin for item in grown.symbols}
    for first in was:
        for second in was:
            if abs(was[first].x_mm - was[second].x_mm) <= TOLERANCE_MM:
                assert abs(now[first].x_mm - now[second].x_mm) <= TOLERANCE_MM
            if abs(was[first].y_mm - was[second].y_mm) <= TOLERANCE_MM:
                assert abs(now[first].y_mm - now[second].y_mm) <= TOLERANCE_MM


def test_la_dilatazione_non_e_mai_una_contrazione() -> None:
    """§A.4: se il disegno non ci sta nemmeno al fattore 1, il foglio resta
    quello. La dilatazione allarga o non fa niente; non stringe mai."""
    sheet = una_tavola_da_allargare()
    largo = dilate_sheet(sheet, 3.0, STEP_MM)
    grown, factor = dilated_to_fit(largo, AREA, STEP_MM)
    assert factor == 1.0
    assert grown is largo

    box = ink_box(sheet.symbols, sheet.routes)
    comodo, used = dilated_to_fit(sheet, AREA, STEP_MM)
    assert used >= 1.0
    after = ink_box(comodo.symbols, comodo.routes)
    assert after is not None and box is not None
    assert after[2] - after[0] >= box[2] - box[0] - TOLERANCE_MM
    assert after[3] - after[1] >= box[3] - box[1] - TOLERANCE_MM


def test_la_dilatazione_si_ferma_al_margine_e_non_lo_stringe() -> None:
    """§A.2 con §B: il fattore e' il piu' grande che tiene il disegno dentro il
    margine, e il margine non si stringe per far salire un numero."""
    sheet = una_tavola_da_allargare()
    grown, factor = dilated_to_fit(sheet, AREA, STEP_MM)
    assert factor > 1.0
    margine = border_margin_mm(grown.symbols, grown.routes, RECT)
    assert margine is not None
    ammesso = margin_allowed_mm(sheet.symbols, sheet.routes, RECT, STEP_MM)
    box = ink_box(grown.symbols, grown.routes)
    assert box is not None
    assert box[2] - box[0] <= (RECT[2] - RECT[0]) - 2 * ammesso + TOLERANCE_MM
    assert box[3] - box[1] <= (RECT[3] - RECT[1]) - 2 * ammesso + TOLERANCE_MM


# ---------------------------------------------------------------------------
# §B — il margine dal bordo, e non e' fisso (D-143)
# ---------------------------------------------------------------------------


def test_il_margine_parte_da_venticinque_e_si_stringe_solo_per_far_entrare() -> None:
    """D-143: venticinque millimetri sul disegno che ci sta, meno solo su quello
    che altrimenti non ci starebbe, e mai sotto dieci."""
    piccolo = [_symbol("a", 100.0, 100.0, 20.0, 20.0)]
    assert margin_allowed_mm(piccolo, [], RECT, STEP_MM) == SHEET_MARGIN_MM

    largo = [_symbol("a", 20.0, 100.0, 320.0, 20.0)]
    stretto = margin_allowed_mm(largo, [], RECT, STEP_MM)
    assert SHEET_MARGIN_MIN_MM <= stretto < SHEET_MARGIN_MM
    assert abs(stretto / STEP_MM - round(stretto / STEP_MM)) <= TOLERANCE_MM

    enorme = [_symbol("a", 10.0, 100.0, 350.0, 20.0)]
    assert margin_allowed_mm(enorme, [], RECT, STEP_MM) == SHEET_MARGIN_MIN_MM


def _sheet_with(symbols: list[PlacedSymbol]) -> SheetGeometry:
    return SheetGeometry(sheet_id="t1", title="prova", symbols=symbols)


def _border_findings(sheet: SheetGeometry) -> list[str]:
    found = preflight_drawing(
        DrawingGeometry(project_id="p", sheets=[sheet]), NOVE_C_A3, catalog()
    )
    return [item.code for item in found if item.code == "DRAWING_TOUCHES_THE_BORDER"]


def test_il_preflight_segnala_il_disegno_che_tocca_il_bordo_senza_autorizzazione() -> None:
    """Il criterio 5, **nei due versi**.

    Un disegno piccolo spinto contro il bordo e' un rilievo: poteva starne
    lontano e non ci sta. Un disegno largo quanto il foglio no: piu' dentro non
    ci stava, e il margine si e' stretto per farlo entrare, che e' l'unica
    ragione per cui D-143 lo permette.
    """
    contro_il_bordo = _sheet_with([_symbol("a", AREA.x_mm, 100.0, 20.0, 20.0)])
    assert _border_findings(contro_il_bordo) == ["DRAWING_TOUCHES_THE_BORDER"]

    comodo = _sheet_with([_symbol("a", 160.0, 120.0, 20.0, 20.0)])
    assert _border_findings(comodo) == []

    pieno = _sheet_with([_symbol("a", AREA.x_mm + 10.0, 100.0, 330.0, 20.0)])
    assert _border_findings(pieno) == []


# ---------------------------------------------------------------------------
# §C — la forma della distribuzione (D-144)
# ---------------------------------------------------------------------------


def _chain(*steps: tuple[str, str, str, str], turns: int) -> Highway:
    return Highway(
        keys=tuple((f"p{index}",) for index in range(len(steps))),
        steps=tuple(
            (
                PortRef(component_id=here, port_id=my_port),
                PortRef(component_id=there, port_id=peer_port),
            )
            for here, my_port, there, peer_port in steps
        ),
        turns_allowed=turns,
    )


def _reader(
    places: dict[tuple[str, str], tuple[float, float, str]],
) -> PortAt:
    faces = {
        "left": PortFace.LEFT,
        "right": PortFace.RIGHT,
        "top": PortFace.TOP,
        "bottom": PortFace.BOTTOM,
    }

    def at(component_id: str, port_id: str) -> tuple[Point, PortFace] | None:
        found = places.get((component_id, port_id))
        if found is None:
            return None
        x_mm, y_mm, face = found
        return (Point(x_mm=x_mm, y_mm=y_mm), faces[face])

    return at


def test_la_distribuzione_fa_una_curva_e_una_sola() -> None:
    """Il criterio 8 sulla forma: gamba dritta, **una** curva, dorsale.

    La prova fallisce se la gamba si piega — cioe' se la catena curva dove non
    deve — e se le curve sono due. L'autostrada fra le macchine di spina non ha
    diritto a nessuna curva, e la stessa posa che va bene alla distribuzione la
    fa cadere: e' la differenza che D-144 introduce.
    """
    gamba_curva_dorsale = _reader(
        {
            ("circolatore", "b"): (100.0, 100.0, "right"),
            ("gomito", "a"): (160.0, 100.0, "left"),
            ("gomito", "c"): (160.0, 100.0, "bottom"),
            ("terminali", "in"): (160.0, 160.0, "top"),
        }
    )
    forma = (
        ("circolatore", "b", "gomito", "a"),
        ("gomito", "c", "terminali", "in"),
    )
    assert turns_of(_chain(*forma, turns=1), gamba_curva_dorsale) == 1
    assert lies_in_line(_chain(*forma, turns=1), gamba_curva_dorsale)
    # La stessa catena, senza il diritto alla curva, non sta nella propria forma.
    assert not lies_in_line(_chain(*forma, turns=0), gamba_curva_dorsale)

    due_curve = _reader(
        {
            ("circolatore", "b"): (100.0, 100.0, "right"),
            ("gomito", "a"): (160.0, 100.0, "left"),
            ("gomito", "c"): (160.0, 100.0, "bottom"),
            ("secondo", "c"): (160.0, 160.0, "top"),
            ("secondo", "b"): (160.0, 160.0, "right"),
            ("terminali", "in"): (220.0, 160.0, "left"),
        }
    )
    storta = (
        ("circolatore", "b", "gomito", "a"),
        ("gomito", "c", "secondo", "c"),
        ("secondo", "b", "terminali", "in"),
    )
    assert turns_of(_chain(*storta, turns=1), due_curve) == 2
    assert not lies_in_line(_chain(*storta, turns=1), due_curve)


def test_una_catena_che_non_si_misura_non_e_una_catena_storta() -> None:
    """Una posa che non colloca un pezzo non da' un numero di curve: chi chiama
    la tratta come non conservabile, non come piegata."""
    parziale = _reader({("circolatore", "b"): (100.0, 100.0, "right")})
    catena = _chain(("circolatore", "b", "gomito", "a"), turns=1)
    assert turns_of(catena, parziale) is None
    assert not lies_in_line(catena, parziale)


# ---------------------------------------------------------------------------
# §E — la guardia del riempimento e' un divieto, non una soglia (D-141)
# ---------------------------------------------------------------------------


def _cost(fill: float, coverage: float, **extra: float) -> SheetCost:
    base = {
        "violations": 0,
        "turnback_runs": 0,
        "turnback_mm": 0.0,
        "long_runs": 0,
        "bends": 0,
        "crossings": 0,
        "margin_gap": 0.0,
        "fill": fill,
        "coverage": coverage,
        "imbalance": 1.0,
        "length_mm": 0.0,
    }
    base.update(extra)
    return SheetCost(**base)  # type: ignore[arg-type]


def test_la_guardia_del_riempimento_boccia_anche_il_caso_lieve() -> None:
    """Il criterio 7, ed e' il rilievo §5.1 del verdetto sulla PR #41.

    La guardia di `DRAW-012` era una **soglia**: finche' la copertura restava
    sopra 0,75 una posa che alzava il riempimento e **abbassava** la copertura
    vinceva lo stesso. Il PM l'ha misurato — riempimento 30 % con copertura 0,80
    perdeva contro riempimento 50 % con copertura 0,70 — e D-141 dice l'opposto
    senza soglie. Qui il caso **lieve** costa quanto il caso grosso.
    """
    onesta = _cost(fill=0.30, coverage=0.80)
    lieve = _cost(fill=0.50, coverage=0.70)
    forte = _cost(fill=0.50, coverage=0.45)

    assert not lieve.beats(onesta)
    assert not forte.beats(onesta)
    # E la guardia non punisce chi migliora **tutt'e due**: quella e' la posa
    # buona, e deve continuare a vincere.
    buona = _cost(fill=0.50, coverage=0.85)
    assert buona.beats(onesta)


def test_il_riempimento_non_compra_un_allungo() -> None:
    """§A.3: lo stiramento del singolo tratto resta ammesso **solo** per far
    entrare il corredo. Con `on_fill=False` il riempimento non conta, e un
    allungo che si giustificasse con lui non passa; uno che fa entrare un
    accessorio passa lo stesso, perche' vince su una voce che viene prima."""
    prima = _cost(fill=0.30, coverage=0.80)
    solo_riempimento = _cost(fill=0.50, coverage=0.80)
    assert solo_riempimento.beats(prima)
    assert not solo_riempimento.beats(prima, on_fill=False)

    fa_entrare = _cost(fill=0.30, coverage=0.80, violations=0)
    con_violazione = _cost(fill=0.50, coverage=0.80, violations=1)
    assert fa_entrare.beats(con_violazione, on_fill=False)


def test_il_margine_viene_prima_del_riempimento() -> None:
    """§B con D-140: un disegno che rinuncia al margine per far salire una
    percentuale perde. Lo spazio comodo si prende **dopo**, dilatando."""
    comoda = _cost(fill=0.30, coverage=0.80, margin_gap=0.0)
    fino_al_bordo = _cost(fill=0.55, coverage=0.80, margin_gap=15.0)
    assert comoda.beats(fino_al_bordo)
    assert not fino_al_bordo.beats(comoda)
