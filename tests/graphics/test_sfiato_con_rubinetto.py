"""Lo sfiato con il suo rubinetto, un simbolo solo, ovunque (I-210, I-211).

Il PO, con uno schizzo — lo sfiato sopra, il rubinetto sotto, sulla stessa asta —: «modificare il
simbolo dello sfiato, facendo sfiato e rubinetto insieme. cosi' riusciamo a disegnarlo piccolo e
il disegno si compatta e abbiamo meno sormonti e meno lunghezze»; e poi «ok si sostituiamo il
simbolo ovunque». Sul volano la valvola ci va: si cambia lo sfiato senza svuotare il serbatoio.

Il simbolo e' alto 7,5 e non 10: sul volano coricato sul ritorno di una pompa di calore (D-196) lo
sfiato sta addosso al cielo del volano, e la mandata gli passa sopra a 7,5 mm dal cielo.
"""

# categoria: difende il disegno — I-210, I-211, lo sfiato col rubinetto

import contextlib
import io
import json
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.skill import cartelle_del_repository, main

ROOT = Path(__file__).resolve().parents[2]
PROVA = ROOT / "docs" / "collaudi" / "REL-005" / "prova-po-1"


def _catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog",
        symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols"),
    )


def test_lo_sfiato_si_disegna_col_suo_rubinetto() -> None:
    catalogo = _catalogo()
    for voce in ("air-vent", "air-vent-solar"):
        simbolo = catalogo.resolve(voce).symbol.manifest
        assert simbolo.id == "air-vent-with-valve", voce
        assert (simbolo.width_mm, simbolo.height_mm) == (5.0, 7.5)
        assert [(porta.id, porta.face.value, porta.x_mm, porta.y_mm) for porta in simbolo.ports] == [
            ("a", "bottom", 2.5, 7.5)
        ]
    # Il segno: il tappo e il bulbo dello sfiato, e sotto i due triangoli della valvola.
    corpo = catalogo.resolve("air-vent").symbol.body
    assert corpo.count("<circle") == 1 and corpo.count("<path") == 2


def test_la_regola_propone_lo_sfiato_col_rubinetto_e_mai_la_variante() -> None:
    """La variante senza rubinetto fa lo stesso mestiere, e si sceglie solo quando il testo la
    nomina (D-188): la regola che vuole uno sfogo d'aria propone lo sfiato col rubinetto."""
    catalogo = _catalogo()
    assert catalogo.providing("air_release", "heating_water").id == "air-vent"
    semplice = catalogo.get("air-vent-plain")
    assert semplice.variant is not None and semplice.variant.of == "air-vent"
    assert catalogo.resolve("air-vent-plain").symbol.manifest.id == "air-vent"


def test_sul_volano_coricato_lo_sfiato_resta_sotto_la_mandata(tmp_path: Path) -> None:
    """La tavola D della prova del PO: il volano a due attacchi coricato sul ritorno della pompa
    di calore, con lo sfiato addosso al cielo. Il simbolo sta fra il cielo del volano e la
    mandata, e non la tocca."""
    cartelle = cartelle_del_repository(ROOT)
    with contextlib.redirect_stdout(io.StringIO()):
        assert main(["completa", str(PROVA / "grafo-proposta-po.json"), "--out", str(tmp_path / "gc.json")], cartelle) == 0
        main(
            [
                "disegna", str(tmp_path / "gc.json"), "--piano", str(PROVA / "piano-D-volano-coricato.json"),
                "--out", str(tmp_path / "t"), "--geometria", str(tmp_path / "g.json"),
            ],
            cartelle,
        )
    foglio = json.loads((tmp_path / "g.json").read_text(encoding="utf-8"))["sheets"][0]
    simboli = {item["component_id"]: item for item in foglio["symbols"]}
    sfiato, volano = simboli["air-vent-volano-b"], simboli["volano"]
    assert sfiato["symbol_id"] == "air-vent-with-valve"
    assert sfiato["origin"]["y_mm"] + 7.5 == volano["origin"]["y_mm"], "addosso al cielo del volano"
    alto, basso = sfiato["origin"]["y_mm"], sfiato["origin"]["y_mm"] + 7.5
    sinistra, destra = sfiato["origin"]["x_mm"], sfiato["origin"]["x_mm"] + 5
    sopra = []
    for rotta in foglio["routes"]:
        if rotta["supply"] is not True:
            continue
        for tratto in rotta["segments"]:
            for a, b in zip(tratto, tratto[1:], strict=False):
                if a["y_mm"] != b["y_mm"] or max(a["x_mm"], b["x_mm"]) < sinistra or min(a["x_mm"], b["x_mm"]) > destra:
                    continue
                assert not alto - 2.5 < a["y_mm"] < basso, f"una mandata a y={a['y_mm']} tocca lo sfiato"
                if a["y_mm"] <= alto:
                    sopra.append(a["y_mm"])
    assert sopra, "la mandata passa sopra lo sfiato"


def test_sul_caso_reale_lo_sfiato_pende_addosso_al_raccordo_e_non_scavalca(tmp_path: Path) -> None:
    """Il PO: «vorrei che fosse ridotto al minimo quel pezzetto di tubo in modo da non fare quel
    problema di scavallo» (I-212). Sul caso reale ricostruito ogni sfiato sta addosso al suo
    raccordo o al cielo del volano — tubo zero — e nessuno incrocia una linea: sul ritorno di una
    pompa di calore sta sotto la mandata, anche dove la mandata e' l'autostrada."""
    caso = ROOT / "docs" / "collaudi" / "REL-009" / "caso-reale-2"
    cartelle = cartelle_del_repository(ROOT)
    with contextlib.redirect_stdout(io.StringIO()):
        assert main(["completa", str(caso / "grafo-prima-stesura.json"), "--out", str(tmp_path / "gc.json")], cartelle) == 0
        main(
            [
                "disegna", str(tmp_path / "gc.json"), "--piano", str(caso / "piano.json"),
                "--out", str(tmp_path / "t"), "--geometria", str(tmp_path / "g.json"),
            ],
            cartelle,
        )
    grafo = json.loads((tmp_path / "gc.json").read_text(encoding="utf-8"))
    capi = {
        item["id"]: (item["endpoint_a"]["component_id"], item["endpoint_b"]["component_id"])
        for item in grafo["connections"]
    }
    foglio = json.loads((tmp_path / "g.json").read_text(encoding="utf-8"))["sheets"][0]
    stacchi = [
        rotta
        for rotta in foglio["routes"]
        if any(pezzo.startswith("sfiato-") for cid in rotta["connection_ids"] for pezzo in capi[cid])
        and not any(pezzo.startswith("giunto-") for cid in rotta["connection_ids"] for pezzo in capi[cid])
    ]
    assert len(stacchi) == 8, "sei pompe di calore e due volani"
    for rotta in stacchi:
        punti = [punto for tratto in rotta["segments"] for punto in tratto]
        assert {(punto["x_mm"], punto["y_mm"]) for punto in punti} == {(punti[0]["x_mm"], punti[0]["y_mm"])}, rotta
        assert rotta["crossings"] == [], rotta["connection_ids"]
