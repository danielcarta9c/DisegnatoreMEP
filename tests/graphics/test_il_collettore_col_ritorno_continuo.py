"""Il collettore di zona col ritorno continuo (REL-015, I-231).

Il PO, sulla 1.6.0: «Un collettore aveva una forma strana le tubazioni». Il collaudo T2
di REL-012, §3.6: «il collettore di ritorno e' disegnato come tre barrette staccate (una
per `out`, una per `ret_1`, una per `ret_2`): sembrano tre pezzi distinti, non un
collettore». Il difetto stava nel corpo del simbolo `zone-manifold-pair`: la barra del
ritorno si interrompeva dove una discesa di mandata la attraversava.

Adesso le due barre sono continue, e si interrompe la **discesa della mandata**, che
passa dietro la barra del ritorno. Le porte non cambiano. Rossa sul commit di partenza.
"""
# categoria: difende il simbolo

import re
from pathlib import Path

from disegnatore_mep.graphics.registry import SymbolRegistry

ROOT = Path(__file__).resolve().parents[2]
SYMBOLS = ROOT / "assets" / "symbols"


def _rettangoli(corpo: str) -> list[tuple[float, float, float, float]]:
    return [
        tuple(float(valore) for valore in item)  # type: ignore[misc]
        for item in re.findall(
            r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"/>', corpo
        )
    ]


def _linee(corpo: str) -> list[tuple[float, float, float, float]]:
    return [
        tuple(float(valore) for valore in item)  # type: ignore[misc]
        for item in re.findall(
            r'<line x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)"/>', corpo
        )
    ]


def test_mandata_e_ritorno_sono_due_barre_continue() -> None:
    corpo = (SYMBOLS / "zone-manifold-pair.svg").read_text(encoding="utf-8")
    barre = _rettangoli(corpo)
    # Due barre sole, lunghe tutto il collettore: niente barrette.
    assert len(barre) == 2, barre
    for x, _, larghezza, _ in barre:
        assert x == 2.0 and x + larghezza == 40.0


def test_la_discesa_di_mandata_passa_dietro_il_ritorno_senza_toccarlo() -> None:
    corpo = (SYMBOLS / "zone-manifold-pair.svg").read_text(encoding="utf-8")
    ritorno = next(barra for barra in _rettangoli(corpo) if barra[1] > 5)
    alto, basso = ritorno[1], ritorno[1] + ritorno[3]
    manifesto = SymbolRegistry.from_directory(SYMBOLS).get("zone-manifold-pair").manifest
    for porta in ("out_1", "out_2"):
        x = manifesto.port(porta).x_mm
        tratti = sorted((min(y1, y2), max(y1, y2)) for x1, y1, x2, y2 in _linee(corpo) if x1 == x2 == x)
        # Due tratti: dalla barra della mandata fino a prima del ritorno, e da dopo il
        # ritorno fino alla porta. Nessuno dei due tocca la barra del ritorno.
        assert len(tratti) == 2, (porta, tratti)
        assert tratti[0][1] < alto and tratti[1][0] > basso
        assert tratti[1][1] == manifesto.height_mm


def test_le_porte_non_cambiano() -> None:
    """Il segno cambia, la posa no: le tavole che lo usano cambiano solo nel corpo."""
    manifesto = SymbolRegistry.from_directory(SYMBOLS).get("zone-manifold-pair").manifest
    assert {(porta.id, porta.x_mm, porta.y_mm, porta.face.value) for porta in manifesto.ports} == {
        ("in", 0.0, 2.5, "left"),
        ("out", 0.0, 12.5, "left"),
        ("out_1", 7.5, 15.0, "bottom"),
        ("out_2", 27.5, 15.0, "bottom"),
        ("ret_1", 17.5, 15.0, "bottom"),
        ("ret_2", 37.5, 15.0, "bottom"),
    }
    assert manifesto.version == "1.1.0"
