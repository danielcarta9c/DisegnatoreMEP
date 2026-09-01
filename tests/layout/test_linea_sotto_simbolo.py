"""Una tubazione non attraversa il corpo di un simbolo (D-027, I-018).

⛔ **Il difetto che queste prove inchiodano e' quello che teneva ferma la regola
di vicinanza del PM** (D-120): avvicinando la valvola all'attacco della macchina,
su un caso di prova una tubazione finiva **sotto** un simbolo invece di essere
interrotta da lui, e nessun controllo la segnalava.

La causa era la misura, non il disegno. «Linea sotto il simbolo» era scritta come
**contenimento**: il tratto valeva un rilievo solo se il riquadro lo conteneva
per intero. Ne discendevano due buchi che si sommavano:

- un tratto che entrava da un lato e usciva dall'altro passava per buono;
- una spezzata con un capo sul riquadro era per di piu' **esente** dal controllo
  di distanza — e' cosi' che si riconosce un attacco — quindi poteva
  attraversare il corpo indisturbata.

Il rimedio e' una misura sola, generale e senza eccezioni per l'esempio: un
tratto e' un rilievo quando percorre una lunghezza **dentro il corpo** del
riquadro, bordi esclusi. Chi termina su un attacco non entra — una porta sta sul
perimetro — quindi non serve nessuna deroga per lui, ed e' il motivo per cui le
due prove di guardia qui sotto continuano a passare.

⚠ **Queste prove sono scritte apposta con le sole funzioni che esistevano
prima della correzione**, cosi' che si possano eseguire sulla revisione
precedente e vederle fallire: e' la dimostrazione che il caso e' quello vero e
non uno costruito attorno al rimedio.
"""

from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.layout.geometry import (
    PlacedSymbol,
    Point,
    RoutedTrunk,
    SheetGeometry,
    run_intrudes_on,
)
from disegnatore_mep.validation.geometry import validate_sheet_geometry

BOX = (100.0, 100.0, 110.0, 110.0)
"""Un riquadro qualunque di dieci millimetri per lato."""


def _symbol() -> PlacedSymbol:
    return PlacedSymbol(
        component_id="accumulo",
        symbol_id="buffer-two-port",
        rotation_deg=0,
        origin=Point(x_mm=BOX[0], y_mm=BOX[1]),
        width_mm=BOX[2] - BOX[0],
        height_mm=BOX[3] - BOX[1],
    )


def _run(points: list[tuple[float, float]]) -> RoutedTrunk:
    return RoutedTrunk(
        network_id="cp",
        medium="heating_water",
        connection_ids=["c1"],
        segments=[[Point(x_mm=x, y_mm=y) for x, y in points]],
    )


def _codes(routes: list[RoutedTrunk]) -> set[str]:
    sheet = SheetGeometry(
        sheet_id="t1", title="prova", symbols=[_symbol()], routes=routes
    )
    return {item.code for item in validate_sheet_geometry(sheet, NOVE_C_A3)}


def test_una_spezzata_attaccata_al_simbolo_non_puo_attraversarlo() -> None:
    """⛔ Il caso di I-018, riprodotto: **falliva prima della correzione.**

    La spezzata ha un capo dentro il riquadro — e' un attacco — e poi ci passa
    attraverso, uscendo dall'altro lato. L'esenzione che riconosce l'attacco la
    copriva per intero, e il contenimento non la vedeva perche' nessun singolo
    tratto sta tutto dentro. E' esattamente la figura che compare quando la
    valvola si avvicina alla macchina: l'accessorio si siede dove un'altra
    tratta si attacca allo stesso pezzo.
    """
    crossing = _run([(105.0, 105.0), (105.0, 90.0), (130.0, 90.0)])
    assert run_intrudes_on(BOX, [crossing], NOVE_C_A3.standard.min_clearance_mm)


def test_il_controllo_di_correttezza_vede_chi_attraversa_da_parte_a_parte() -> None:
    """⛔ Lo stesso difetto al cancello, e **falliva prima della correzione.**

    Il tratto entra a sinistra ed esce a destra: non e' contenuto da nessuna
    parte, quindi la vecchia misura lo lasciava passare.
    """
    assert "LINE_UNDER_SYMBOL" in _codes([_run([(90.0, 105.0), (130.0, 105.0)])])


def test_il_controllo_di_correttezza_vede_ancora_chi_ci_sta_tutto_dentro() -> None:
    """Il caso che la vecchia misura vedeva resta visto: e' il caso estremo."""
    assert "LINE_UNDER_SYMBOL" in _codes([_run([(102.0, 105.0), (108.0, 105.0)])])


def test_la_tratta_che_si_ferma_sull_attacco_non_e_un_rilievo() -> None:
    """La guardia: chi arriva alla porta e si ferma non viene segnalato.

    E' il «salvo il tratto che termina esattamente su un attacco previsto», e
    non costa una deroga: una porta sta sul perimetro, quindi quel tratto tocca
    il bordo e nel corpo non entra.
    """
    assert "LINE_UNDER_SYMBOL" not in _codes([_run([(80.0, 105.0), (100.0, 105.0)])])


def test_la_tratta_che_costeggia_il_fianco_non_e_un_rilievo() -> None:
    """L'altra guardia: a filo del bordo la linea si legge, e non e' sotto niente."""
    assert "LINE_UNDER_SYMBOL" not in _codes([_run([(100.0, 90.0), (100.0, 120.0)])])


def test_un_accessorio_non_si_posa_dove_una_tratta_altrui_lo_attraversa() -> None:
    """La stessa misura vista da chi posa: la posizione si scarta, non si consegna.

    E' il predicato che il posatore e il ciclo di miglioramento interrogano per
    sapere «questa posizione la consegno o no?»: deve dare la stessa risposta
    del cancello, o si approva una tavola e se ne disegna un'altra.
    """
    across = _run([(105.0, 95.0), (105.0, 115.0)])
    assert run_intrudes_on(BOX, [across], NOVE_C_A3.standard.min_clearance_mm)
