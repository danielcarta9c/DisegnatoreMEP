"""Il defangatore sta fra i suoi due rubinetti, stretti a lui (REL-011, D-120, D-218).

Dal 4 novembre 2026 vaso, riempimento e manometro stanno sul ritorno comune fra le macchine e
il defangatore (D-218): il defangatore coi suoi rubinetti finisce fra il raccordo del manometro
e il volano. Il rubinetto verso il raccordo e' il primo organo della tratta, e la posa morbida
di I-035 — «l'organo che isola oltre un raccordo passante si stringe al raccordo» — lo
attaccava al raccordo, a 20 mm dal defangatore, mentre il defangatore si appoggiava al
rubinetto del volano. Sulla tavola D della prova del PO il defangatore aveva un rubinetto solo,
e l'altro sembrava dei raccordi. Rossa sul commit di partenza (`5046044` piu' i piani
ricomposti): 20 mm.
"""
# categoria: difende il motore — D-120, la coppia organo-apparecchio, contro la posa morbida di I-035

import contextlib
import io
import json
from pathlib import Path

from disegnatore_mep.layout.inline import END_CLEARANCE_MM, SNUG_CLEARANCE_MM
from disegnatore_mep.skill import cartelle_del_repository, main

ROOT = Path(__file__).resolve().parents[2]
PROVA = ROOT / "docs" / "collaudi" / "REL-005" / "prova-po-1"
TOLLERANZA = 1e-6


def _distanza(primo: dict[str, object], secondo: dict[str, object]) -> float:
    def riquadro(item: dict[str, object]) -> tuple[float, float, float, float]:
        origine = item["origin"]
        assert isinstance(origine, dict)
        x, y = float(origine["x_mm"]), float(origine["y_mm"])
        return x, y, x + float(item["width_mm"]), y + float(item["height_mm"])  # type: ignore[arg-type]

    a, b = riquadro(primo), riquadro(secondo)
    dx = max(a[0] - b[2], b[0] - a[2], 0.0)
    dy = max(a[1] - b[3], b[1] - a[3], 0.0)
    return float((dx**2 + dy**2) ** 0.5)


def test_sulla_tavola_d_il_defangatore_ha_un_rubinetto_per_parte_stretto_a_lui(tmp_path: Path) -> None:
    cartelle = cartelle_del_repository(ROOT)
    with contextlib.redirect_stdout(io.StringIO()):
        assert main(["completa", str(PROVA / "grafo-proposta-po.json"), "--out", str(tmp_path / "gc.json")], cartelle) == 0
        assert main(
            [
                "disegna", str(tmp_path / "gc.json"), "--piano", str(PROVA / "piano-D-volano-coricato.json"),
                "--out", str(tmp_path / "t"), "--geometria", str(tmp_path / "g.json"), "--senza-dxf",
            ],
            cartelle,
        ) == 0
    foglio = json.loads((tmp_path / "g.json").read_text(encoding="utf-8"))["sheets"][0]
    simboli = {item["component_id"]: item for item in foglio["symbols"]}
    defangatore = simboli["dirt-separator-pdc-water-return"]
    for rubinetto in ("valve-isolation-dirt-separator-pdc-water-return-b", "valve-isolation-volano-b"):
        distanza = _distanza(defangatore, simboli[rubinetto])
        assert SNUG_CLEARANCE_MM - TOLLERANZA <= distanza <= END_CLEARANCE_MM + TOLLERANZA, (rubinetto, distanza)
    # Da una parte e dall'altra, non tutti e due dallo stesso lato.
    centro = float(defangatore["origin"]["x_mm"]) + float(defangatore["width_mm"]) / 2
    lati = {
        float(simboli[rubinetto]["origin"]["x_mm"]) < centro
        for rubinetto in ("valve-isolation-dirt-separator-pdc-water-return-b", "valve-isolation-volano-b")
    }
    assert lati == {True, False}
