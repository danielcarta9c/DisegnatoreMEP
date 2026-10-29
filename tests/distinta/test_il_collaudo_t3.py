"""Le riserve sulla distinta del terzo collaudo indipendente (REL-012, caso t3).

Il rapporto e' `docs/collaudi/REL-012/collaudo-t3/RAPPORTO.md`, §3; il grafo e' quello che
il collaudo ha fatto con la skill (`collaudo-t3/grafo-completo.json`): un canalizzato in
appartamento, plenum di zona con quattro bocchette TA-01…TA-04, centrale Airzone e tre
termostati, la ripresa montata sulla macchina.
"""

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.distinta import Distinta, RegoleDellaDistinta, componi_la_distinta
from disegnatore_mep.distinta.regole import la_fornitura
from disegnatore_mep.distinta.uscite import tabelle_del_foglio

from .conftest import sigle

Nomi = tuple[dict[str, str], dict[str, str]]

COLLAUDO_T3 = Path(__file__).resolve().parent / "collaudo-t3" / "grafo-completo.json"


@pytest.fixture
def grafo_t3() -> dict[str, Any]:
    return copy.deepcopy(json.loads(COLLAUDO_T3.read_text(encoding="utf-8")))


def _distinta(grafo: dict[str, Any], regole: RegoleDellaDistinta, nomi: Nomi) -> Distinta:
    return componi_la_distinta(grafo, regole, *nomi, sigle(grafo), la_fornitura(regole, "confermata"))


# --- §3 i numeri di tratta seguono le sigle ---------------------------------------------


def test_t0n_va_a_ta_0n(grafo_t3: dict[str, Any], regole: RegoleDellaDistinta, nomi: Nomi) -> None:
    """Prima T03 andava a TA-04 e T04 a TA-03: il grafo nomina prima la bocchetta TA-04.
    Dentro il fluido le tratte vanno nell'ordine delle sigle che collegano."""
    distinta = _distinta(grafo_t3, regole, nomi)
    mandata = [(t.num, distinta.da_a(t)) for t in distinta.tratte_in_tabella if t.fluido == "supply_air"]
    assert mandata == [
        ("T01", "PLZ-01 - TA-01"),
        ("T02", "PLZ-01 - TA-02"),
        ("T03", "PLZ-01 - TA-03"),
        ("T04", "PLZ-01 - TA-04"),
    ]
    # I bus: i tre termostati in fila, poi i due collegamenti dell'unita' interna.
    bus = [distinta.da_a(t) for t in distinta.tratte_in_tabella if t.fluido == "control_bus"]
    assert bus == ["CZ-01 - TZ-01", "CZ-01 - TZ-02", "CZ-01 - TZ-03", "CZ-01 - UI-01", "UI-01 - CF-01"]


def test_l_ordine_non_dipende_da_come_il_grafo_elenca_le_tubazioni(
    grafo_t3: dict[str, Any], regole: RegoleDellaDistinta, nomi: Nomi
) -> None:
    prima = _distinta(grafo_t3, regole, nomi)
    grafo_t3["connections"].reverse()
    dopo = _distinta(grafo_t3, regole, nomi)
    assert [(t.num, dopo.da_a(t)) for t in dopo.tratte_in_tabella] == [
        (t.num, prima.da_a(t)) for t in prima.tratte_in_tabella
    ]


def test_dieci_bocchette_si_contano_come_si_leggono(
    grafo_t3: dict[str, Any], regole: RegoleDellaDistinta, nomi: Nomi
) -> None:
    """TA-2 prima di TA-10: le cifre si leggono come numeri, non come lettere."""
    sigle_date = {
        "bocchetta-matrimoniale": "TA-10",
        "bocchetta-singola": "TA-2",
        "bocchetta-soggiorno-parete": "TA-9",
        "bocchetta-soggiorno-varco": "TA-1",
    }
    for pezzo in grafo_t3["components"]:
        if pezzo["id"] in sigle_date:
            pezzo["tag"] = sigle_date[pezzo["id"]]
    distinta = _distinta(grafo_t3, regole, nomi)
    mandata = [distinta.da_a(t) for t in distinta.tratte_in_tabella if t.fluido == "supply_air"]
    assert mandata == ["PLZ-01 - TA-1", "PLZ-01 - TA-2", "PLZ-01 - TA-9", "PLZ-01 - TA-10"]


# --- §3 la ripresa con un nome solo -------------------------------------------------------


def test_la_ripresa_sulla_macchina_ha_un_nome_solo(
    grafo_t3: dict[str, Any], regole: RegoleDellaDistinta, nomi: Nomi
) -> None:
    """Il raccordo diretto RA-01 - UI-01 (lunghezza 0) era «canale di ripresa coibentato» nella
    tabella delle tratte e «plenum di ripresa» nell'Excel: adesso e' il plenum di ripresa
    del corredo, nella tabella del foglio, nel foglio «Tratte» e nella voce B."""
    distinta = _distinta(grafo_t3, regole, nomi)
    ripresa = next(t for t in distinta.tratte_in_tabella if t.fluido == "return_air")
    assert ripresa.diretta
    assert distinta.materiale(ripresa) == "plenum di ripresa coibentato"
    righe = tabelle_del_foglio(distinta)["tabelle"][0]["sezioni"][0]["righe"]
    riga = next(r for r in righe if r[0] == ripresa.num)
    assert "plenum di ripresa" in riga[3] and "canale" not in riga[3]
    voci = [v.testo for v in distinta.voci]
    assert any(v.startswith("Plenum di ripresa") for v in voci)
    assert not any("anale di ripresa" in v for v in voci)


def test_un_canale_di_ripresa_vero_resta_un_canale(
    grafo_t3: dict[str, Any], regole: RegoleDellaDistinta, nomi: Nomi
) -> None:
    """Se il progettista porta la ripresa lontano dalla macchina, e' un canale e si quota."""
    for tubazione in grafo_t3["connections"]:
        if tubazione["network_id"] == "ripresa-aria":
            tubazione["lunghezza_m"] = 3.0
    distinta = _distinta(grafo_t3, regole, nomi)
    ripresa = next(t for t in distinta.tratte_in_tabella if t.fluido == "return_air")
    assert distinta.materiale(ripresa) == "canale di ripresa coibentato"
    assert any(v.testo.startswith("Canale di ripresa coibentato 800×300") for v in distinta.voci)
