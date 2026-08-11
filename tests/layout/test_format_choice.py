"""Il formato si sceglie provando, non stimando (D-058).

A3 orizzontale, o A4 se il disegno e' proprio piccolo. Non esiste un criterio
di «piccolo» da valutare a priori: la prova **e'** il criterio, perche' il
posizionamento fallisce esattamente quando il contenuto non entra alla scala
fissa e ADR 0003 vieta di rimpicciolire i simboli per farceli stare.
"""

from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3, NOVE_C_A4
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import compose_on_ordinary_frame
from disegnatore_mep.layout.errors import LayoutError

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def test_a_central_plant_lands_on_the_a3() -> None:
    """Il caso D-011 non e' un disegno piccolo: sull'A4 non ci sta."""
    frame, drawing = compose_on_ordinary_frame(load_project(PROJECT), catalog())
    assert frame == NOVE_C_A3
    assert drawing.sheets


def test_entering_means_respecting_the_minimum_distances() -> None:
    """«Entrare» non e' starci a stento.

    Corridoio di instradamento, stacco fra due componenti e gola larga almeno
    quanto gli accessori che la attraversano sono vincoli, non desideri: la A4
    viene rifiutata, e il rifiuto **nomina una misura** invece di dire soltanto
    che non ci sta.

    **Quale** misura non e' piu' fissato qui, ed e' un cambiamento vero: da
    quando i raccordi non si prendono una colonna a testa (D-120) questo
    impianto in larghezza sulla A4 ci starebbe, e a fermarlo e' una tratta che
    non si instrada. La prova continua a chiedere cio' per cui esiste — niente
    rimpicciolimenti, niente disegno fuori pagina, e un motivo misurabile
    scritto (ADR 0003, D-045) — e smette di chiedere **su quale dei due muri**
    l'impianto vada a sbattere, che non e' una promessa del prodotto.
    """
    with pytest.raises(LayoutError) as raised:
        compose_on_ordinary_frame(load_project(PROJECT), catalog(), (NOVE_C_A4,))
    # Non si rimpicciolisce per farcelo stare (ADR 0003): si dice quanto manca.
    assert "does not fit on any ordinary sheet format" in str(raised.value)
    assert any(
        measured in str(raised.value)
        for measured in ("functional bands need", "cannot be routed", "no straight")
    )


def test_nothing_larger_than_the_a3_is_offered() -> None:
    """Niente A0, niente strisce: sopra l'A3 si divide in piu' tavole (D-056)."""
    with pytest.raises(LayoutError, match="does not fit on any ordinary sheet format"):
        compose_on_ordinary_frame(load_project(PROJECT), catalog(), ())
