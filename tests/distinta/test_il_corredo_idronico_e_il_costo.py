"""REL-020 e REL-021: il corredo idronico della distinta, e la distinta prezzata con il
listino della minuteria (I-284 … I-286, D-235)."""

import json
import re
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.distinta import RegoleDellaDistinta, componi_la_distinta
from disegnatore_mep.distinta.calcolo import prezzo_della_voce
from disegnatore_mep.distinta.costo import prezza_la_distinta
from disegnatore_mep.distinta.listino import ErroreDelListino, leggi_il_listino
from disegnatore_mep.skill import cartelle_del_repository, main

from .conftest import ROOT

LISTINO = ROOT / "skill" / "distinta" / "LISTINO-MINUTERIA.md"
CATALOGO = ROOT / "examples" / "layout" / "catalog"
SENZA_CORREDO = {"outdoor-temperature-probe", "plant-controller", "solar-collector"}
"""Le voci del catalogo che la distinta ancora non sa comprare: lo dice la sezione X."""


def _tubo(ident: str, rete: str, a: tuple[str, str], b: tuple[str, str], **dati: Any) -> dict[str, Any]:
    return {
        "id": ident, "network_id": rete,
        "endpoint_a": {"component_id": a[0], "port_id": a[1]},
        "endpoint_b": {"component_id": b[0], "port_id": b[1]},
        "properties": dati,
    }


def _centrale() -> dict[str, Any]:
    """Una pompa di calore, una valvola sulla mandata e una sul ritorno, un volano; la
    mandata e il ritorno all'esterno con la loro lunghezza, i tratti in centrale senza."""
    return {
        "schema_version": "1",
        "metadata": {"project_name": "Prova del costo"},
        "networks": [{"id": "primario", "name": "Circuito della pompa di calore", "domain": "hydronic",
                      "medium": "heating_water"}],
        "components": [
            {"id": "pdc", "definition_id": "heat-pump-air-water", "tag": "GT-01",
             "properties": {"marca": "Shenling", "modello": "ThermaX R290"}},
            {"id": "v1", "definition_id": "valve-isolation", "tag": "VI-01", "properties": {}},
            {"id": "v2", "definition_id": "valve-isolation", "tag": "VI-02", "properties": {}},
            {"id": "tee", "definition_id": "tee-branch", "tag": "DER-01", "properties": {}},
            {"id": "sfiato", "definition_id": "air-vent", "tag": "SF-01", "properties": {}},
            {"id": "vol", "definition_id": "buffer-two-port", "tag": "VOL-01",
             "properties": {"marca": "X", "modello": "Y"}},
        ],
        "connections": [
            _tubo("m1", "primario", ("pdc", "water_supply"), ("v1", "a"), lunghezza_m=10, sezione="MS 32×3"),
            _tubo("m2", "primario", ("v1", "b"), ("tee", "a"), sezione="MS 32×3"),
            _tubo("m3", "primario", ("tee", "b"), ("vol", "a"), lunghezza_m=1, sezione="MS 32×3"),
            _tubo("s1", "primario", ("tee", "branch"), ("sfiato", "a"), sezione="MS 32×3"),
            _tubo("r1", "primario", ("vol", "b"), ("v2", "a"), lunghezza_m=1, sezione="MS 32×3"),
            _tubo("r2", "primario", ("v2", "b"), ("pdc", "water_return"), lunghezza_m=10, sezione="MS 32×3"),
        ],
    }


@pytest.fixture(scope="module")
def listino() -> Any:
    return leggi_il_listino(LISTINO)


def test_ogni_voce_idronica_del_catalogo_ha_il_suo_corredo(regole: RegoleDellaDistinta) -> None:
    voci = {p.stem for p in CATALOGO.glob("*.json")}
    assert sorted(voci - set(regole.corredo) - SENZA_CORREDO) == []
    assert {"heating_water", "cold_water", "domestic_hot_water"} <= set(regole.fluidi)


def test_il_listino_si_legge_con_le_voci_del_banco_e_quelle_online(listino: Any) -> None:
    """Le 150 righe del rilievo al banco (§1) e i codici del riepilogo online (§2)."""
    del_banco = [v for v in listino.voci.values() if v.fonte.startswith("rilievo al banco")]
    online = [v for v in listino.voci.values() if v.fonte.startswith("riferimento online")]
    assert len(del_banco) == 150
    assert len(online) >= 60
    assert listino.get("I04").prezzo == pytest.approx(3.64) and listino.get("I04").um == "m"
    assert listino.get("E02").prezzo == pytest.approx(2.28)
    assert listino.revisione.startswith("03")


def test_un_codice_doppio_ferma_il_listino(tmp_path: Path) -> None:
    doppio = tmp_path / "listino.md"
    riga = "| I01 | Tubo | Tubo 16x2 | 1 | Segrate | 100 m | 69,10 | 0,69 | m | |"
    doppio.write_text(
        "# Listino\n\n| ID | Voce | Articolo | Codice | Negozio | Confezione | Netto conf. € | Netto/UM € | UM | Note |\n"
        f"|---|---|---|---|---|---|--:|--:|---|---|\n{riga}\n{riga}\n",
        encoding="utf-8",
    )
    with pytest.raises(ErroreDelListino, match="I01 ha due prezzi"):
        leggi_il_listino(doppio)


def test_ogni_codice_delle_regole_e_nel_listino(listino: Any) -> None:
    """Una regola che nomina un codice che il listino non ha farebbe un DA PREZZARE muto."""
    codici: set[str] = set()
    for nome in ("corredo.json", "fluidi.json"):
        testo = (ROOT / "rules" / "distinta" / nome).read_text(encoding="utf-8")
        codici |= set(re.findall(r'"codice": "([^"]+)"', testo))
    assert codici and sorted(codici - set(listino.voci)) == []


def test_il_prezzo_della_voce_sceglie_sul_dato() -> None:
    regola = {"prezzo": [{"per": "pollice", "scegli": [{"se": '^1"', "codice": "I32"}], "n": 1}]}
    assert prezzo_della_voce(regola, {"pollice": '1"'}).codici == (("I32", 1.0),)
    assert prezzo_della_voce(regola, {}).manca == "manca il dato «pollice»"
    assert "nessuna voce del listino" in prezzo_della_voce(regola, {"pollice": '½"'}).manca
    vaso = {"prezzo": [{"per": "volume_l", "scegli": [{"almeno": 18, "codice": "A"}, {"almeno": 25, "codice": "B"}]}]}
    assert prezzo_della_voce(vaso, {"volume_l": 24}).codici == (("B", 1.0),)
    assert prezzo_della_voce(vaso, {"volume_l": 30}).manca.startswith("nessuna voce del listino")
    rcbo = {"prezzo": [{"per": "{poli} C{in_a} {tipo}", "scegli": [{"se": "^2P C32 A$", "codice": "E17"}]}]}
    assert prezzo_della_voce(rcbo, {"poli": "2P", "in_a": 32, "tipo": "A"}).codici == (("E17", 1.0),)
    assert prezzo_della_voce(rcbo, {"poli": "2P", "in_a": 32, "tipo": "B"}).manca.startswith("nessuna voce")
    assert prezzo_della_voce({"prezzo": []}, {}).manca == "non e' nel listino"
    assert prezzo_della_voce({}, {}) is None


def test_la_centrale_ha_tubo_valvole_e_raccordi_del_suo_pollice(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    distinta = componi_la_distinta(_centrale(), regole, *nomi)
    sezione_i = {v.testo: v for v in distinta.voci_della_sezione("I")}
    assert sezione_i["Valvola a sfera a passaggio totale 1\" FF, con leva"].quantita == 2
    assert sezione_i["Raccordo diritto a pressare M 1\" × tubo multistrato MS 32×3"].quantita == 4
    assert sezione_i["Tee a pressare tubo multistrato MS 32×3"].quantita == 1
    # Le valvole sono passanti: GT-01 - VI-01 - DER-01 10 m × 1,15 = 11,5; DER-01 - VOL-01
    # 1 × 1,15 → 1,5; VOL-01 - VI-02 - GT-01 11 × 1,15 = 12,65 → 13 (l'acqua non aggiunge il
    # metro per tratto); DER-01 - SF-01 senza lunghezza, in centrale: 1 m (se_manca_m).
    tubo = sezione_i["Tubo multistrato MS 32×3, nudo"]
    assert tubo.quantita == pytest.approx(11.5 + 1.5 + 13 + 1)
    assert any("quotati senza maggiorazione" in a for a in distinta.avvisi)
    assert not distinta.voci_della_sezione("X")


def test_il_costo_e_la_somma_delle_voci_prezzate_e_dice_quelle_da_prezzare(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]], listino: Any
) -> None:
    distinta = componi_la_distinta(_centrale(), regole, *nomi)
    costo = prezza_la_distinta(distinta, listino)
    assert {r.sezione for r in costo.righe} <= {"S", "I", "E", "B", "C", "D", "X"}
    assert all(r.sezione != "A" for r in costo.righe), "le apparecchiature si comprano a parte"
    assert costo.totale == pytest.approx(sum(r.totale or 0 for r in costo.righe))
    tubo = next(r for r in costo.righe if r.testo == "Tubo multistrato MS 32×3, nudo")
    assert tubo.totale == pytest.approx(27.0 * listino.get("I04").prezzo)
    sfiato = next(r for r in costo.righe if r.testo.startswith("Valvola automatica di sfogo aria"))
    assert sfiato.totale == pytest.approx(listino.get("I43a").prezzo) and sfiato.nota
    valvole = next(r for r in costo.righe if r.testo.startswith("Valvola a sfera"))
    assert valvole.totale == pytest.approx(2 * listino.get("I32").prezzo)
    assert all(r.manca for r in costo.da_prezzare)


def test_il_comando_scrive_il_costo_accanto_alla_distinta(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    grafo = tmp_path / "grafo-completo.json"
    grafo.write_text(json.dumps(_centrale(), ensure_ascii=False), encoding="utf-8")
    main(
        ["distinta", str(grafo), "--out", str(tmp_path / "d"), "--costo", "--fornitura", "confermata"],
        cartelle_del_repository(ROOT),
    )
    stampa = capsys.readouterr().out
    assert "Costo della minuteria (uso interno, non va all'installatore)" in stampa
    md = (tmp_path / "d" / "costo-minuteria.md").read_text(encoding="utf-8")
    assert "Uso interno Nove C" in md and "Totale prezzato" in md
    dati = json.loads((tmp_path / "d" / "costo-minuteria.json").read_text(encoding="utf-8"))
    assert dati["totale_eur"] > 0 and dati["listino"]["revisione"].startswith("03")
    documento = next((tmp_path / "d").glob("Distinta_*.md")).read_text(encoding="utf-8")
    assert "€" not in documento, "il documento per l'installatore resta senza prezzi"
