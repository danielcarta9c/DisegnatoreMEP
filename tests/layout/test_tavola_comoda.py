"""Le prove di DRAW-013: la tavola si allarga tutta insieme e non tocca il bordo.

> **Dal 2 ottobre 2026 (I-180) il solutore non c'e' piu'**, e con lui le prove che lo
> difendevano. Restano qui le prove del margine dal bordo (D-143), del preflight che lo segnala e della misura della catena storta (B1, D-171). Il resto di questa intestazione e' la storia del
> file, e si legge come tale.


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
# categoria: difende regole del piano — il margine dal bordo (D-143), il preflight del bordo, la catena storta di B1 (D-171)

from functools import cache
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.symbol import PortFace
from disegnatore_mep.layout.geometry import (
    SHEET_MARGIN_MIN_MM,
    SHEET_MARGIN_MM,
    DrawingGeometry,
    PlacedSymbol,
    Point,
    SheetGeometry,
    margin_allowed_mm,
)
from disegnatore_mep.layout.highways import (
    Highway,
    PortAt,
    lies_in_line,
    turns_forced,
    turns_of,
)
from disegnatore_mep.model.project import (
    PortRef,
)
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












# ---------------------------------------------------------------------------
# §A — la tavola comoda si ottiene dilatando tutto (D-142)
# ---------------------------------------------------------------------------












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


def _chain(*steps: tuple[str, str, str, str]) -> Highway:
    return Highway(
        keys=tuple((f"p{index}",) for index in range(len(steps))),
        steps=tuple(
            (
                PortRef(component_id=here, port_id=my_port),
                PortRef(component_id=there, port_id=peer_port),
            )
            for here, my_port, there, peer_port in steps
        ),
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


def test_la_curva_che_un_raccordo_impone_non_storce_la_catena() -> None:
    """La forma e' quella che **le facce dei pezzi consentono** (**D-171**).

    Fino al 22 settembre 2026 il confronto era `Highway.turns_allowed`: zero fra
    le macchine di spina, **una** verso i terminali. Il PO ha tolto il massimo —
    «piu' dritte possibili, meno curve possibili… non c'e' un numero massimo;
    dicevo una curva nel caso del generatore singolo e due accumuli, ma era per
    far capire il concetto» — e al suo posto c'e' un **pavimento**: quante
    pieghe i simboli attraversati impongono.

    Il gomito ha `a` a sinistra e `c` sotto, due facce **perpendicolari**: la
    sua curva non e' una cessione, e' la sua forma. Nessuna posa la toglie.
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
    assert turns_of(_chain(*forma), gamba_curva_dorsale) == 1
    assert turns_forced(_chain(*forma), gamba_curva_dorsale) == 1
    assert lies_in_line(_chain(*forma), gamba_curva_dorsale)

    # **Due gomiti impongono due curve**, e la scala che ne esce non e' un
    # difetto di chi ha posato: e' l'impianto che ha due gomiti. Che due siano
    # piu' di una lo dice la voce `pieghe` del punteggio, non un rilievo.
    due_gomiti = _reader(
        {
            ("circolatore", "b"): (100.0, 100.0, "right"),
            ("gomito", "a"): (160.0, 100.0, "left"),
            ("gomito", "c"): (160.0, 100.0, "bottom"),
            ("secondo", "c"): (160.0, 160.0, "top"),
            ("secondo", "b"): (160.0, 160.0, "right"),
            ("terminali", "in"): (220.0, 160.0, "left"),
        }
    )
    scala = (
        ("circolatore", "b", "gomito", "a"),
        ("gomito", "c", "secondo", "c"),
        ("secondo", "b", "terminali", "in"),
    )
    assert turns_of(_chain(*scala), due_gomiti) == 2
    assert turns_forced(_chain(*scala), due_gomiti) == 2
    assert lies_in_line(_chain(*scala), due_gomiti)


def test_una_piega_che_nessun_simbolo_impone_storce_la_catena() -> None:
    """Il difetto di **D-151**: ogni frammento e' dritto e la catena fa un gomito.

    Il raccordo di mezzo ha `a` a sinistra e `b` a destra — facce **opposte**,
    pavimento **zero**: passarci attraverso non costa nessuna piega. Se la
    catena ne fa una lo stesso, e' perche' le due tratte corrono su **due quote
    diverse**, e quella e' una scelta di chi ha posato — si toglie spostando un
    pezzo, non piegando il tubo.
    """
    due_quote = _reader(
        {
            ("circolatore", "b"): (100.0, 100.0, "right"),
            ("dritto", "a"): (160.0, 100.0, "left"),
            ("dritto", "b"): (160.0, 140.0, "right"),
            ("terminali", "in"): (220.0, 140.0, "left"),
        }
    )
    catena = _chain(
        ("circolatore", "b", "dritto", "a"),
        ("dritto", "b", "terminali", "in"),
    )
    assert turns_of(catena, due_quote) == 1
    assert turns_forced(catena, due_quote) == 0
    assert not lies_in_line(catena, due_quote)


def test_una_catena_che_non_si_misura_non_e_una_catena_storta() -> None:
    """Una posa che non colloca un pezzo non da' un numero di curve: chi chiama
    la tratta come non conservabile, non come piegata."""
    parziale = _reader({("circolatore", "b"): (100.0, 100.0, "right")})
    catena = _chain(("circolatore", "b", "gomito", "a"))
    assert turns_of(catena, parziale) is None
    assert not lies_in_line(catena, parziale)
    # Anche una catena di una tratta sola ha un pavimento: le due porte fra cui
    # corre possono stare su assi perpendicolari, ed e' la L fra due pezzi che
    # la tavola 5 approvata dal PO porta sette volte (I-108). Senza la porta del
    # gomito quel pavimento non si conosce, e il numero e' un'incognita — fino
    # al 22 settembre 2026 qui si leggeva **zero**, perche' il pavimento
    # contava i soli crocevia.
    assert turns_forced(catena, parziale) is None

    # Il pavimento diventa un'incognita quando manca la porta di un crocevia.
    lunga = _chain(
        ("circolatore", "b", "gomito", "a"),
        ("gomito", "c", "terminali", "in"),
    )
    assert turns_forced(lunga, parziale) is None
    assert not lies_in_line(lunga, parziale)


# ---------------------------------------------------------------------------
# §E — la guardia del riempimento e' un divieto, non una soglia (D-141)
# ---------------------------------------------------------------------------










# ---------------------------------------------------------------------------
# §G — gli organi di servizio addosso al pezzo che servono (D-145)
# ---------------------------------------------------------------------------








