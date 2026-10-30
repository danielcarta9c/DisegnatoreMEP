"""Le scritte dell'acqua si posano prima dei cavi, e lasciano loro la strada (REL-015, I-231).

Con l'acqua scritta per prima, sul canalizzato del collaudo T3 le scritte della condensa
andavano a destra dello scarico — il lato della convenzione, libero perche' i cavi non
c'erano ancora — e il bus fra la centrale di zona e l'unita' interna, che scende proprio
li', girava loro intorno e tornava indietro sulla propria porta (`RUN_OVERSHOOTS_ITS_PORT`,
bloccante). La scritta dello scarico si posava sopra la porta del comando a filo, e il cavo
non aveva piu' strada; e sulla M.02 la sigla del sifone, che cede e viene dopo, finiva sul
richiamo della scritta della condensa.

Tre correzioni, ciascuna con la sua prova:

- **il lato della scritta**: di fianco a un tubo dove arriva un cavo, prima il lato
  opposto (`layout.diametri._lati`, `_diagonali`);
- **la strada dei cavi diritti**: due porte una di fronte all'altra si uniscono dritte, e
  le scritte dell'acqua non ci si posano (`piano.esecutore.corridoi_dei_cavi_diritti`);
- **una sigla non si posa su un richiamo** (`layout.labels._Canvas.free`).

Rosse sul commit di partenza (la fusione del lavoro sul punto 3 di REL-015): la T3
rifatta si fermava, e le funzioni nuove non c'erano.
"""
# categoria: difende il motore

import contextlib
import io
import json
from pathlib import Path
from types import SimpleNamespace

from disegnatore_mep.layout.diametri import _diagonali, _lati, _Rettilineo
from disegnatore_mep.layout.geometry import Point
from disegnatore_mep.layout.labels import _Canvas

ROOT = Path(__file__).resolve().parents[2]
T3 = ROOT / "docs" / "collaudi" / "REL-012" / "collaudo-t3"


def _verticale(mandata: bool = True) -> _Rettilineo:
    """Uno scarico che scende a x = 200, da y = 100 a y = 130."""
    return _Rettilineo(route=SimpleNamespace(supply=mandata), orizzontale=False, fisso=200.0, da=100.0, a=130.0)  # type: ignore[arg-type]


def test_senza_cavi_i_lati_sono_quelli_della_convenzione() -> None:
    assert _lati(_verticale(), (), 0) == ("destra", "sinistra")
    assert _lati(_verticale(), (), 1) == ()


def test_un_cavo_a_destra_manda_la_scritta_prima_a_sinistra() -> None:
    cavo = (Point(x_mm=210.0, y_mm=95.0),)
    assert _lati(_verticale(), cavo, 0) == ("sinistra",)
    assert _lati(_verticale(), cavo, 1) == ("destra",)
    # Le diagonali del richiamo: prima quelle che vanno a sinistra.
    assert all(verso[0] == -1 for verso in _diagonali(_verticale(), cavo, 0))
    assert all(verso[0] == 1 for verso in _diagonali(_verticale(), cavo, 1))


def test_un_cavo_lontano_non_cambia_niente() -> None:
    lontano = (Point(x_mm=260.0, y_mm=110.0), Point(x_mm=205.0, y_mm=300.0))
    assert _lati(_verticale(), lontano, 0) == ("destra", "sinistra")


def test_una_sigla_non_si_posa_su_un_richiamo() -> None:
    tela = _Canvas(area=(0.0, 0.0, 100.0, 100.0), symbols=[], lines=[], line_segments=[])
    riquadro = (40.0, 40.0, 60.0, 44.0)
    assert tela.free(riquadro)
    tela.take((80.0, 80.0, 90.0, 84.0), (Point(x_mm=30.0, y_mm=30.0), Point(x_mm=70.0, y_mm=50.0)))
    assert not tela.free(riquadro)


def test_il_canalizzato_del_collaudo_t3_si_consegna_coi_cavi_diritti(tmp_path: Path) -> None:
    """Il canalizzato del collaudo T3 rifatto in A3: nessun bloccante, il bus della centrale
    e il cavo del comando a filo senza giri, e nessuna scritta sopra un cavo."""
    from disegnatore_mep.skill import cartelle_del_repository, main

    with contextlib.redirect_stdout(io.StringIO()):
        esito = main(
            [
                "disegna",
                str(T3 / "grafo-completo.json"),
                "--piano",
                str(T3 / "rifatto" / "piano.json"),
                "--out",
                str(tmp_path),
            ],
            cartelle_del_repository(ROOT),
        )
    rilievi = next(tmp_path.glob("*-rilievi.md")).read_text(encoding="utf-8")
    assert esito == 0, rilievi
    assert "rilievi bloccanti **0**" in rilievi
    for codice in ("RUN_OVERSHOOTS_ITS_PORT", "RUN_WITH_TOO_MANY_BENDS", "LABEL_ON_A_RUN", "RUN_LABEL_OMITTED"):
        assert codice not in rilievi, codice
    assert json.loads((T3 / "rifatto" / "piano.json").read_text(encoding="utf-8"))["formato"] == "A3"
