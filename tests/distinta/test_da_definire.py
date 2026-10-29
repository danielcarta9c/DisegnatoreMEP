"""Dove manca un dato, DA DEFINIRE e una domanda: mai un numero inventato.

E la distinta e' spenta di default: la fa solo il suo comando, e il grafo si legge
con i campi del tratto in testa alla tubazione (il modello di `REL-012`) come nelle
`properties` (prima che il modello li abbia).
"""

import json
import re
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.distinta import DA_DEFINIRE, Distinta, RegoleDellaDistinta, componi_la_distinta
from disegnatore_mep.distinta.uscite import distinta_in_json
from disegnatore_mep.skill import cartelle_del_repository, costruisci_il_parser, main

from .conftest import ROOT, pezzo, tubazione


def _distinta(grafo: dict[str, Any], regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]) -> Distinta:
    return componi_la_distinta(grafo, regole, *nomi)


def test_un_ramo_senza_lunghezza_lascia_da_definire_le_voci_a_metro(
    grafo_aa01: dict[str, Any], regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    del tubazione(grafo_aa01, "a-b3")["properties"]["lunghezza_m"]
    distinta = _distinta(grafo_aa01, regole, nomi)
    flessibile = next(v for v in distinta.voci if v.regola.endswith("flessibile-in-confezioni"))
    assert flessibile.quantita is None and flessibile.da_definire
    assert "manca la lunghezza di T03" in flessibile.calcolo
    sostegni = next(v for v in distinta.voci if v.regola.endswith("/sostegni"))
    assert sostegni.quantita is None
    fascette = next(v for v in distinta.voci if v.regola.endswith("/fascette"))
    assert fascette.quantita == 40, "le fascette si contano per ramo: il numero dei rami si sa"
    assert any("T03" in d and "quanto e' lungo" in d for d in distinta.domande)
    tratta = next(t for t in distinta.tratte if t.num == "T03")
    assert tratta.da_quotare_m is None


def test_una_linea_senza_protezione_chiede_la_protezione(
    grafo_aa01: dict[str, Any], regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    del tubazione(grafo_aa01, "e-3")["properties"]["protezione"]
    distinta = _distinta(grafo_aa01, regole, nomi)
    protezioni = [v for v in distinta.voci if v.regola.endswith("protezione-della-linea")]
    assert [v.da_definire for v in protezioni] == [False, True]
    assert protezioni[1].testo.startswith(f"{DA_DEFINIRE} (protezione)")
    assert "T11 (Alimentazione centrale Airzone): manca `protezione` sul tratto." in distinta.domande


def test_senza_i_dati_di_macchina_il_refrigerante_e_da_definire(
    grafo_aa01: dict[str, Any], regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    for chiave in ("precarica_fino_a_m", "carica_aggiuntiva_g_m", "refrigerante"):
        del pezzo(grafo_aa01, "ue")["properties"][chiave]
    distinta = _distinta(grafo_aa01, regole, nomi)
    carica = next(v for v in distinta.voci if v.regola.endswith("carica-aggiuntiva"))
    assert carica.quantita is None and carica.da_definire
    assert carica.testo == f"Refrigerante {DA_DEFINIRE} (refrigerante), riserva per carica aggiuntiva"
    assert any("precarica_fino_a_m" in d for d in carica.domande)


def test_un_dato_del_pezzo_che_manca_resta_nel_testo_come_da_definire(
    grafo_aa01: dict[str, Any], regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    del pezzo(grafo_aa01, "bocchetta-b2")["properties"]["dimensione"]
    distinta = _distinta(grafo_aa01, regole, nomi)
    plenum = [v for v in distinta.voci if v.regola.endswith("plenum-porta-bocchetta")]
    assert [(v.quantita, v.da_definire) for v in plenum] == [(4, False), (1, True)]
    assert f"per bocchetta {DA_DEFINIRE} (dimensione)" in plenum[1].testo
    assert "B2 (Bocchetta di mandata con plenum di raccordo): manca il dato «dimensione»" in plenum[1].domande[0]


def test_una_voce_senza_corredo_e_un_fluido_senza_regole_vanno_in_x(
    grafo_aa01: dict[str, Any], regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    """Un pezzo idronico in un grafo aria-aria: la distinta conta i pezzi (il numero
    si sa) e chiede il resto, invece di tacere."""
    grafo_aa01["networks"].append({"id": "acqua", "name": "Acqua di riscaldamento", "domain": "hydronic", "medium": "heating_water"})
    grafo_aa01["components"] += [
        {"id": "pdc", "definition_id": "heat-pump-air-water", "tag": "PDC-01", "properties": {}},
        {"id": "pompa", "definition_id": "pump-circulator", "tag": "P-01", "properties": {}},
    ]
    grafo_aa01["connections"].append(
        {
            "id": "w-1",
            "network_id": "acqua",
            "endpoint_a": {"component_id": "pdc", "port_id": "supply"},
            "endpoint_b": {"component_id": "pompa", "port_id": "a"},
            "properties": {"lunghezza_m": 3},
        }
    )
    distinta = _distinta(grafo_aa01, regole, nomi)
    x = distinta.voci_della_sezione("X")
    assert [(v.testo.split(" (")[0], v.quantita, v.fornitura) for v in x] == [
        ("Linea di acqua di riscaldamento DA DEFINIRE", 5.0, DA_DEFINIRE),
        ("Pompa di calore aria-acqua", 1.0, DA_DEFINIRE),
        ("Pompa di circolazione", 1.0, DA_DEFINIRE),
    ]
    assert all(v.da_definire and v.domande for v in x)


def test_un_grafo_senza_lunghezze_non_ha_numeri_inventati(
    grafo_aa01: dict[str, Any], regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    """Tolte tutte le lunghezze, nessuna voce che dipende da una lunghezza ha un numero."""
    for connessione in grafo_aa01["connections"]:
        if connessione["properties"].get("lunghezza_m"):
            del connessione["properties"]["lunghezza_m"]
    distinta = _distinta(grafo_aa01, regole, nomi)
    a_metro = {
        f"fluidi/{fluido}/{voce['id']}"
        for fluido, regola in regole.fluidi.items()
        for voce in regola["voci"]
        if voce["calcolo"]["tipo"] in ("lunghezza", "confezioni", "passo", "per_metro", "metri_arrotondati", "carica_refrigerante")
    }
    toccate = [v for v in distinta.voci if v.regola in a_metro]
    assert toccate and all(v.quantita is None and v.da_definire for v in toccate)
    assert all(t.da_quotare_m is None for t in distinta.tratte)


def test_il_comando_esce_con_2_se_resta_qualcosa_da_definire(
    grafo_aa01: dict[str, Any], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    del tubazione(grafo_aa01, "e-3")["properties"]["protezione"]
    grafo = tmp_path / "grafo.json"
    grafo.write_text(json.dumps(grafo_aa01, ensure_ascii=False), encoding="utf-8")
    assert main(["distinta", str(grafo), "--out", str(tmp_path / "d")], cartelle_del_repository(ROOT)) == 2
    uscita = capsys.readouterr().out
    assert "DA DEFINIRE — 1 voci; le domande al progettista:" in uscita
    scritta = json.loads((tmp_path / "d" / "distinta.json").read_text(encoding="utf-8"))
    assert scritta["domande"] == ["T11 (Alimentazione centrale Airzone): manca `protezione` sul tratto."]


def test_i_campi_del_tratto_in_testa_alla_tubazione_valgono_come_nelle_properties(
    grafo_aa01: dict[str, Any], regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    """Il contratto con `REL-012`: `sezione`, `lunghezza_m`, `scritta` sulla tubazione."""
    prima = distinta_in_json(_distinta(grafo_aa01, regole, nomi))
    for connessione in grafo_aa01["connections"]:
        for campo in ("sezione", "lunghezza_m", "scritta"):
            if campo in connessione["properties"]:
                connessione[campo] = connessione["properties"].pop(campo)
    assert distinta_in_json(_distinta(grafo_aa01, regole, nomi)) == prima


def test_gli_esistenti_non_si_forniscono(
    grafo_aa01: dict[str, Any], regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    pezzo(grafo_aa01, "madoka")["esistente"] = True
    distinta = _distinta(grafo_aa01, regole, nomi)
    assert not [v for v in distinta.voci if "Madoka" in v.testo]
    assert any("madoka" in a and "e-5" in a for a in distinta.avvisi)


# --- spenta di default -------------------------------------------------------------


def test_la_distinta_la_fa_solo_il_suo_comando() -> None:
    """Spenta di default (proposta D-213): nessun altro modulo del motore importa la
    distinta; il comando della skill la chiama da una funzione sua, e basta."""
    importano = []
    for percorso in sorted((ROOT / "src" / "disegnatore_mep").rglob("*.py")):
        if "distinta" in percorso.relative_to(ROOT / "src" / "disegnatore_mep").parts:
            continue
        testo = percorso.read_text(encoding="utf-8")
        if re.search(r"disegnatore_mep\.distinta|from \.+distinta", testo):
            importano.append(percorso.name)
    assert importano == ["skill.py"]
    testo = (ROOT / "src" / "disegnatore_mep" / "skill.py").read_text(encoding="utf-8")
    assert testo.count("disegnatore_mep.distinta") == 1, "un import solo, dentro la funzione del comando"
    comandi = costruisci_il_parser()._subparsers._group_actions[0].choices  # type: ignore[union-attr]
    assert "distinta" in comandi
