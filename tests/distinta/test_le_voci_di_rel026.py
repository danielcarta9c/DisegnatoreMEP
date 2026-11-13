"""La distinta con le voci di REL-026 (A-6, I-300): il ventilconvettore canalizzato col lato
aria e il plenum di mandata da due a sei uscite.

Il loro corredo di posa — chi li fornisce, se il ventilconvettore e' un'apparecchiatura di Nove
C, con che sospensioni e raccordi — e' contenuto MEP che il PO non ha deciso: la distinta non lo
inventa. I pezzi escono nella sezione X, «fornitura e corredo di posa DA DEFINIRE», con la
colonna Fornitura DA DEFINIRE e la domanda al progettista, come ogni voce senza regola. Quello
che e' gia' deciso vale anche per loro: le linee d'aria e di condensa hanno le loro regole, e
l'attacco d'acqua del ventilconvettore e' un confine come quello del ventilconvettore
canalizzato (vuole il tubo, non un nipplo). Col plenum motorizzato di zona, che c'e' gia', il
plenum e la sua centrale escono come nell'aria-aria.
"""

import json
from typing import Any

import pytest

from disegnatore_mep.distinta import RegoleDellaDistinta, componi_la_distinta

from .conftest import ROOT

CASI = ROOT / "docs" / "collaudi" / "REL-026" / "blocco-a"
IN_LETTERE = {2: "due", 3: "tre", 4: "quattro", 5: "cinque", 6: "sei"}


def _grafo(caso: str) -> dict[str, Any]:
    return json.loads((CASI / caso / "grafo-completo.json").read_text(encoding="utf-8"))


def _da_definire(distinta: Any) -> dict[str, Any]:
    return {v.testo: v for v in distinta.voci_della_sezione("X")}


def test_ventilconvettori_e_plenum_di_mandata_sono_da_definire_e_si_chiedono(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    distinta = componi_la_distinta(_grafo("plenum-di-mandata"), regole, *nomi)
    x = _da_definire(distinta)
    attese = {
        "Ventilconvettore canalizzato: fornitura e corredo di posa DA DEFINIRE": 3,
        "Plenum di mandata a due uscite: fornitura e corredo di posa DA DEFINIRE": 1,
        "Plenum di mandata a tre uscite: fornitura e corredo di posa DA DEFINIRE": 1,
        "Plenum di mandata a sei uscite: fornitura e corredo di posa DA DEFINIRE": 1,
    }
    assert {testo: x[testo].quantita for testo in attese} == attese
    assert {x[testo].fornitura for testo in attese} == {"DA DEFINIRE"}
    assert all(x[testo].da_definire for testo in attese)
    domande = " ".join(distinta.domande)
    assert "«Ventilconvettore canalizzato»" in domande and "«Plenum di mandata a sei uscite»" in domande
    # Non sono apparecchiature di Nove C finche' il PO non lo dice: la sezione A non li porta.
    assert not [v for v in distinta.voci_della_sezione("A") if "entilconvettore" in v.testo or "Plenum" in v.testo]


def test_il_lato_aria_e_la_condensa_hanno_le_loro_regole(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    """Le undici bocchette col loro plenum porta-bocchetta, i flessibili, i tre sifoni."""
    distinta = componi_la_distinta(_grafo("plenum-di-mandata"), regole, *nomi)
    aria = {v.testo: v for v in distinta.voci_della_sezione("B")}
    porta_bocchetta = next(v for t, v in aria.items() if t.startswith("Plenum porta-bocchetta"))
    assert porta_bocchetta.quantita == 11
    assert any(t.startswith("Condotto flessibile coibentato Ø160") for t in aria)
    condensa = {v.testo: v for v in distinta.voci_della_sezione("D")}
    assert condensa["Sifone ispezionabile per condensa"].quantita == 3


def test_l_attacco_d_acqua_del_ventilconvettore_e_un_confine(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    """Come il ventilconvettore canalizzato (REL-023, I-291): fra la valvola e il terminale il
    tubo, con il suo raccordo a pressare; nessun nipplo da ½" fra le sei valvole e i tre
    ventilconvettori."""
    assert "fan-coil-ducted-air" in regole.giunzioni["confini"]
    distinta = componi_la_distinta(_grafo("plenum-di-mandata"), regole, *nomi)
    idronico = distinta.voci_della_sezione("I")
    # Senza i diametri (li calcola il comando) i pollici restano DA DEFINIRE: si contano le voci.
    nippli = sum(v.quantita or 0 for v in idronico if v.testo.startswith("Nipplo"))
    all_attacco = sum(v.quantita or 0 for v in idronico if v.testo.endswith("all'attacco"))
    # I due nippli sono quelli della pompa di calore; prima di REL-026 ce n'erano altri sei.
    assert (nippli, all_attacco) == (2, 6)


@pytest.mark.parametrize("uscite", sorted(IN_LETTERE))
def test_ogni_taglia_del_plenum_di_mandata_esce_da_definire(
    uscite: int, regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    grafo = _grafo("plenum-motorizzato")
    # Lo stesso ventilconvettore col plenum di mandata della taglia, al posto di quello di zona.
    tolti = {"plz-1", "centrale"}
    grafo["components"] = [c for c in grafo["components"] if c["id"] not in tolti and not c["id"].startswith("b-")]
    grafo["connections"] = [
        c for c in grafo["connections"]
        if not {c["endpoint_a"]["component_id"], c["endpoint_b"]["component_id"]} & tolti
        and not c["id"].startswith("ma-")
    ]
    grafo["components"].append({"id": "pl", "definition_id": f"supply-plenum-{uscite}", "properties": {}})
    grafo["connections"].append({
        "id": "ma-0", "network_id": "mandata-aria-1", "endpoint_a": {"component_id": "fc-1", "port_id": "supply"},
        "endpoint_b": {"component_id": "pl", "port_id": "in"}, "properties": {},
    })
    for k in range(1, uscite + 1):
        grafo["components"].append({"id": f"b-{k}", "definition_id": "air-supply-terminal",
                                    "properties": {"etichetta": f"Locale {k}", "dimensione": "300×150"}})
        grafo["connections"].append({
            "id": f"ma-{k}", "network_id": "mandata-aria-1", "sezione": "Ø160", "lunghezza_m": 3.0,
            "endpoint_a": {"component_id": "pl", "port_id": f"out_{k}"},
            "endpoint_b": {"component_id": f"b-{k}", "port_id": "a"}, "properties": {},
        })
    distinta = componi_la_distinta(grafo, regole, *nomi)
    voce = _da_definire(distinta)[f"Plenum di mandata a {IN_LETTERE[uscite]} uscite: fornitura e corredo di posa DA DEFINIRE"]
    assert (voce.quantita, voce.fornitura) == (1, "DA DEFINIRE")
    porta_bocchetta = next(v for v in distinta.voci_della_sezione("B") if v.testo.startswith("Plenum porta-bocchetta"))
    assert porta_bocchetta.quantita == uscite


def test_col_plenum_motorizzato_il_plenum_e_la_centrale_escono_come_nell_aria_aria(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    """La richiesta del PO del 13 novembre 2026: il ventilconvettore idronico col plenum di zona
    che c'e' gia'. Il plenum e' un'apparecchiatura di Nove C col suo corredo, la centrale e'
    compresa nel plenum; il ventilconvettore resta da definire."""
    distinta = componi_la_distinta(_grafo("plenum-motorizzato"), regole, *nomi)
    apparecchiature = [v for v in distinta.voci_della_sezione("A")]
    plenum = next(v for v in apparecchiature if v.testo.startswith("Plenum motorizzato di zona a quattro serrande"))
    assert plenum.fornitura == "Nove C" and "comprende Centrale di zona" in (plenum.note or "")
    assert not [v for v in apparecchiature if v.testo.startswith("Centrale di zona")]
    assert "Ventilconvettore canalizzato: fornitura e corredo di posa DA DEFINIRE" in _da_definire(distinta)
