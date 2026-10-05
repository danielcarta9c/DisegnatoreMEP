"""Prima le autostrade, e disegnata l'autostrada non si tocca (REL-009, I-201, I-203).

Sulla tavola del caso reale fatta con la 1.3.0 la mandata delle pompe di calore saliva e
riscendeva per scavalcare la valvola dello sfiato dichiarato sul ritorno. Il motore instradava
le tratte nell'ordine dei nomi delle tubazioni: lo stacco dello sfiato, passato prima, aveva
posato la sua valvola sulla quota della mandata. Il PO: «vale il principio che disegnata
l'autostrada non andrebbe toccata».

La prova e' la riproduzione misurata il 3 ottobre 2026: la tavola D della prova del PO con uno
sfiato e la sua valvola sul ritorno della pompa di calore, lo stesso grafo e lo stesso piano, e
le due tubazioni dello stacco con due nomi diversi — uno che viene dopo quelli della mandata,
uno che viene prima. Con l'ordine dei nomi la seconda tavola aveva 23 pieghe invece di 19.
"""

# categoria: difende il disegno — I-201, I-203, la regola delle autostrade (D-171)

import contextlib
import io
import json
import re
from collections import Counter
from pathlib import Path

from disegnatore_mep.skill import cartelle_del_repository, main

ROOT = Path(__file__).resolve().parents[2]
PROVA = ROOT / "docs" / "collaudi" / "REL-005" / "prova-po-1"


def _linea(ident: str, a: str, b: str) -> dict[str, object]:
    (pa, porta_a), (pb, porta_b) = a.split("."), b.split(".")
    return {
        "id": ident,
        "endpoint_a": {"component_id": pa, "port_id": porta_a},
        "endpoint_b": {"component_id": pb, "port_id": porta_b},
        "network_id": "primario",
    }


def _tavola(cartella: Path, nomi_dello_stacco: tuple[str, str]) -> tuple[str, str]:
    """La tavola D con lo sfiato sul ritorno: l'SVG e la riga dei numeri."""
    grafo = json.loads((PROVA / "grafo-proposta-po.json").read_text(encoding="utf-8"))
    grafo["components"] += [
        {"id": "tee-sfiato", "definition_id": "tee-branch", "tag": None, "properties": {}},
        {"id": "valvola-sfiato", "definition_id": "valve-isolation", "tag": None, "properties": {}},
        # Lo sfiato senza rubinetto con la valvola sullo stacco: dal 5 ottobre 2026 lo
        # sfiato di norma porta il suo rubinetto (I-211), ma qui serve uno stacco con un
        # organo in mezzo, ed e' la stessa geometria della prova del 3 ottobre.
        {"id": "sfiato-pdc", "definition_id": "air-vent-plain", "tag": None, "properties": {}},
    ]
    grafo["connections"] = [item for item in grafo["connections"] if item["id"] != "p7"] + [
        _linea("p7a", "volano.b", "tee-sfiato.a"),
        _linea("p7b", "tee-sfiato.b", "pdc.water_return"),
        _linea(nomi_dello_stacco[0], "tee-sfiato.branch", "valvola-sfiato.a"),
        _linea(nomi_dello_stacco[1], "valvola-sfiato.b", "sfiato-pdc.a"),
    ]
    piano = json.loads((PROVA / "piano-D-volano-coricato.json").read_text(encoding="utf-8"))
    piano["pezzi"].pop("air-vent-volano-b")
    piano["pezzi"]["tee-sfiato"] = {"x": 80, "y": 177.5}
    piano["pezzi"]["sfiato-pdc"] = {"x": 80, "y": 140}
    cartella.mkdir()
    (cartella / "grafo.json").write_text(json.dumps(grafo), encoding="utf-8")
    (cartella / "piano.json").write_text(json.dumps(piano), encoding="utf-8")

    cartelle = cartelle_del_repository(ROOT)
    with contextlib.redirect_stdout(io.StringIO()):
        assert main(["completa", str(cartella / "grafo.json"), "--out", str(cartella / "gc.json")], cartelle) == 0
    uscita = io.StringIO()
    with contextlib.redirect_stdout(uscita):
        main(["disegna", str(cartella / "gc.json"), "--piano", str(cartella / "piano.json"), "--out", str(cartella / "t")], cartelle)
    numeri = next(riga for riga in uscita.getvalue().splitlines() if riga.startswith("Formato"))
    svg = next((cartella / "t").glob("*.svg")).read_text(encoding="utf-8")
    return svg, numeri


def test_la_tavola_non_dipende_dal_nome_delle_tubazioni_di_uno_stacco(tmp_path: Path) -> None:
    dopo, numeri_dopo = _tavola(tmp_path / "dopo", ("s1", "s2"))
    prima, numeri_prima = _tavola(tmp_path / "prima", ("a-sfiato-1", "a-sfiato-2"))
    assert "pieghe 19" in numeri_dopo
    assert numeri_prima == numeri_dopo, "lo stacco che passa prima per nome non sposta l'autostrada"
    elementi = re.compile(r"<[^>]+>")
    assert Counter(elementi.findall(prima)) == Counter(elementi.findall(dopo))
