"""Il ripiego dichiarato di **D-150**, e i due confini che lo tengono onesto.

Una tratta che non si instrada non uccide piu' la tavola. Ma il ripiego e'
pericoloso in due modi precisi, e sono questi due che le prove difendono:

1. **non deve anticipare la scala dei formati** — se scattasse prima, ogni
   foglio riuscirebbe e l'impianto finirebbe sul piu' piccolo, degradato,
   invece che sul primo che lo regge davvero;
2. **non deve entrare nel ciclo di miglioramento** — il ciclo usa l'errore per
   scegliere una posa migliore, e se gliela si togliesse accetterebbe come
   buone proprio le pose da scartare.

Insieme dicono una cosa sola: **il ripiego e' l'ultima riga, non una
scorciatoia.**
"""

import inspect
from typing import cast

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import (
    NOVE_C_A1,
    NOVE_C_A2,
    NOVE_C_A3,
    NOVE_C_A4,
    ORDINARY_FRAMES,
    SheetFrame,
)
from disegnatore_mep.layout import compose as compose_module
from disegnatore_mep.layout.compose import compose_on_ordinary_frame
from disegnatore_mep.layout.errors import LayoutError
from disegnatore_mep.layout.route import _last_resort
from disegnatore_mep.model.project import ProjectModel

# Il doppio di `compose_drawing` non guarda ne' il modello ne' il catalogo:
# qui si prova **l'ordine delle decisioni** di chi sceglie il foglio, non
# che cosa ci finisce sopra. Due segnaposto bastano, e il `cast` dice a
# `mypy` che la cosa e' voluta invece di costruire due oggetti veri.
NESSUN_MODELLO = cast(ProjectModel, object())
NESSUN_CATALOGO = cast(ComponentRegistry, object())

# ---------------------------------------------------------------------------
# La spezzata di ripiego
# ---------------------------------------------------------------------------


def test_la_spezzata_di_ripiego_esce_dritta_dalle_due_porte() -> None:
    """E' l'unica cosa che resta giusta di una tratta ceduta: nasce e muore
    **dritta sull'attacco**, perche' li' il verso lo impone la porta."""
    cells = _last_resort((10, 10), (1, 0), (30, 30), (-1, 0), cols=100, rows=100)

    assert cells[0] == (10, 10)
    assert cells[-1] == (30, 30)
    # Un passo fuori da ciascuna porta, nella direzione che la porta impone.
    assert cells[1] == (11, 10)
    assert cells[-2] == (29, 30)
    # Ortogonale a ogni passo: nessun tratto obliquo finisce su una tavola.
    for before, after in zip(cells, cells[1:], strict=False):
        assert before[0] == after[0] or before[1] == after[1]


def test_la_spezzata_di_ripiego_resta_dentro_la_griglia() -> None:
    """Una porta sul bordo che guarda in fuori non manda la linea fuori foglio."""
    cells = _last_resort((0, 0), (-1, 0), (9, 9), (0, 1), cols=10, rows=10)

    for x, y in cells:
        assert 0 <= x < 10
        assert 0 <= y < 10


def test_la_spezzata_di_ripiego_non_ripete_una_cella() -> None:
    """Due porte che si guardano da un passo non producono una spezzata
    degenere: la geometria agli atti non porta punti doppi."""
    cells = _last_resort((10, 10), (1, 0), (11, 10), (-1, 0), cols=100, rows=100)

    assert len(cells) == len(set(cells))


# ---------------------------------------------------------------------------
# §1 — il ripiego non anticipa la scala dei formati
# ---------------------------------------------------------------------------


class _Falsa:
    """Un finto `compose_drawing` che sa su quali formati il disegno entra.

    Serve a provare **l'ordine delle decisioni** di `compose_on_ordinary_frame`
    senza pagare una composizione vera: qui interessa quale foglio viene scelto
    e con quale interruttore, non che cosa ci finisce sopra.
    """

    def __init__(self, entra_da_mm: float) -> None:
        self.entra_da_mm = entra_da_mm
        self.chiamate: list[tuple[float, bool]] = []

    def __call__(
        self,
        project: object,
        catalog: object,
        frame: SheetFrame,
        journal: object = None,
        last_resort: bool = False,
    ) -> str:
        larghezza = frame.standard.sheet_width_mm
        self.chiamate.append((larghezza, last_resort))
        if last_resort or larghezza >= self.entra_da_mm:
            return f"disegno su {larghezza:g}"
        raise LayoutError(f"non entra su {larghezza:g}")


@pytest.fixture
def falsa(monkeypatch: pytest.MonkeyPatch):  # type: ignore[no-untyped-def]
    def installa(entra_da_mm: float) -> _Falsa:
        doppio = _Falsa(entra_da_mm)
        monkeypatch.setattr(compose_module, "compose_drawing", doppio)
        return doppio

    return installa


def test_un_impianto_che_entra_esce_sul_primo_foglio_che_lo_regge(falsa) -> None:  # type: ignore[no-untyped-def]
    """Il criterio 3: il ripiego **non anticipa la scala**.

    L'impianto entra su A2. Deve uscire su A2, non su A4 col ripiego — e il
    ripiego non deve essere nemmeno provato.
    """
    doppio = falsa(entra_da_mm=594.0)

    frame, _ = compose_on_ordinary_frame(NESSUN_MODELLO, NESSUN_CATALOGO)

    assert frame is NOVE_C_A2
    assert doppio.chiamate == [(297.0, False), (420.0, False), (594.0, False)]
    assert not any(ripiego for _, ripiego in doppio.chiamate)


def test_il_ripiego_scatta_solo_a_formati_finiti_e_sul_piu_grande(falsa) -> None:  # type: ignore[no-untyped-def]
    """Quando nessun foglio regge, si riprende **il piu' grande** — quello che
    lascia piu' spazio, quindi quello su cui le tratte perse saranno meno."""
    doppio = falsa(entra_da_mm=10_000.0)

    frame, _ = compose_on_ordinary_frame(NESSUN_MODELLO, NESSUN_CATALOGO)

    assert frame is NOVE_C_A1
    # Tutti i formati provati sul serio, in ordine, e **poi** il ripiego.
    assert doppio.chiamate == [
        (297.0, False),
        (420.0, False),
        (594.0, False),
        (841.0, False),
        (841.0, True),
    ]


def test_senza_nessun_formato_da_provare_si_alza_le_mani(falsa) -> None:  # type: ignore[no-untyped-def]
    """Il ripiego ha bisogno di un foglio su cui posarsi: senza, e' un errore."""
    falsa(entra_da_mm=10_000.0)

    with pytest.raises(LayoutError, match="no format was offered to try"):
        compose_on_ordinary_frame(NESSUN_MODELLO, NESSUN_CATALOGO, frames=())


def test_la_scala_dei_formati_arriva_all_a1(falsa) -> None:  # type: ignore[no-untyped-def]
    """D-148, letto da chi sceglie: quattro formati, dal piu' piccolo in su."""
    assert ORDINARY_FRAMES == (NOVE_C_A4, NOVE_C_A3, NOVE_C_A2, NOVE_C_A1)


# ---------------------------------------------------------------------------
# §2 — il ripiego non entra nel ciclo di miglioramento
# ---------------------------------------------------------------------------


def test_i_due_interruttori_restano_separati() -> None:
    """Il criterio 4, ed e' la ragione per cui non sono un parametro solo.

    `tolerant` lo accende il **ciclo di miglioramento** a ogni posa che misura:
    gli serve per poter *misurare* una posa in cui il corredo non entra, invece
    di vederla sparire. `last_resort` lo accende **solo chi compone**, e solo a
    vie finite.

    Se fossero lo stesso interruttore, il ciclo accetterebbe come valide le
    pose che non si instradano — cioe' sceglierebbe proprio quelle da
    scartare, e la tavola uscirebbe degradata anche dove una posa buona c'era.
    """
    from disegnatore_mep.layout.inline import settle_sheet

    parametri = inspect.signature(settle_sheet).parameters
    assert parametri["tolerant"].default is False
    assert parametri["last_resort"].default is False


def test_il_ciclo_di_miglioramento_non_accende_il_ripiego() -> None:
    """Chi misura una posa non deve poterla vedere riuscire per finta."""
    import ast
    import pathlib

    sorgente = pathlib.Path(
        compose_module.__file__
    ).parent.joinpath("improve.py").read_text(encoding="utf-8")
    albero = ast.parse(sorgente)
    chiamate = [
        nodo
        for nodo in ast.walk(albero)
        if isinstance(nodo, ast.Call)
        and isinstance(nodo.func, ast.Name)
        and nodo.func.id == "settle_sheet"
    ]
    assert chiamate, "il ciclo non chiama piu' settle_sheet: questa prova va riscritta"
    for chiamata in chiamate:
        passati = {parola.arg for parola in chiamata.keywords}
        assert "last_resort" not in passati, (
            "il ciclo di miglioramento accende il ripiego: cosi' accetta come "
            "buona una posa che non si instrada (D-150)"
        )


def test_il_motore_ordinario_non_tollera_una_tratta_persa() -> None:
    """`route_sheet` senza interruttore fallisce come ha sempre fatto: e' quel
    fallimento che fa salire di formato e cambiare posa."""
    from disegnatore_mep.layout.route import route_sheet

    assert inspect.signature(route_sheet).parameters["tolerant"].default is False
