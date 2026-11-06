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
from disegnatore_mep.skill import cartelle_del_repository, consegna, main

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
    """Una pompa di calore, una valvola sulla mandata e una sul ritorno, un volano; i
    metri del tubo li dice il progettista per la rete, nel blocco «distinta» (I-288):
    le lunghezze sui tratti del grafo non contano per l'acqua."""
    return {
        "schema_version": "1",
        "metadata": {"project_name": "Prova del costo"},
        "distinta": {"tubi": [{"rete": "primario", "tubo": "MS 32×3", "metri": 24, "isolamento": "guaina 19 mm"}]},
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
    """Le 150 righe del rilievo al banco (§1), i 4 nippli delle fatture dell'installatore
    (§2ter, REL-023) e i codici del riepilogo online (§2)."""
    del_banco = [v for v in listino.voci.values() if v.fonte.startswith("rilievo al banco")]
    online = [v for v in listino.voci.values() if v.fonte.startswith("riferimento online")]
    assert len(del_banco) == 154
    assert listino.get("I83c").prezzo == pytest.approx(2.13) and "Bricoman" in listino.get("I83c").fonte
    assert len(online) >= 60
    assert listino.get("I04").prezzo == pytest.approx(3.64) and listino.get("I04").um == "m"
    assert listino.get("E02").prezzo == pytest.approx(2.28)
    assert listino.revisione.startswith("05")


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
    # REL-023 (I-291): VI-01 ha il tubo da tutte e due le parti (il tratto esterno e il tee),
    # VI-02 dal lato della macchina; sull'attacco del volano VI-02 si avvita con un nipplo.
    assert sezione_i["Raccordo diritto a pressare M 1\" × tubo multistrato MS 32×3"].quantita == 3
    assert sezione_i["Nipplo 1\" M × M"].quantita == 1
    assert sezione_i["Raccordo diritto a pressare M × tubo multistrato MS 32×3, all'attacco"].quantita == 3
    assert sezione_i["Tee a pressare tubo multistrato MS 32×3"].quantita == 1
    # I 24 m del progettista × 1,15 = 27,6 → 28 m; le lunghezze dei tratti non contano.
    tubo = sezione_i["Tubo multistrato MS 32×3, nudo"]
    assert tubo.quantita == pytest.approx(28)
    assert sezione_i["Guaina isolante elastomerica per tubo multistrato MS 32×3 (guaina 19 mm)"].quantita == 28
    assert sezione_i["Gomito 90° a pressare tubo multistrato MS 32×3, a corpo"].quantita == 20
    assert not distinta.voci_della_sezione("X")
    assert not [t for t in distinta.tratte_in_tabella if t.fluido == "heating_water"]
    assert not any("quanto e' lungo" in d for d in distinta.domande), "l'acqua non chiede lunghezze di tratto"
    staffe = [v for v in distinta.voci_della_sezione("S")]
    assert [v.testo for v in staffe] == ["Basamento a terra per l'unità esterna con supporti antivibranti"]


def test_il_costo_e_la_somma_delle_voci_prezzate_e_dice_quelle_da_prezzare(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]], listino: Any
) -> None:
    distinta = componi_la_distinta(_centrale(), regole, *nomi)
    costo = prezza_la_distinta(distinta, listino)
    assert {r.sezione for r in costo.righe} <= {"S", "I", "E", "B", "C", "D", "X"}
    assert all(r.sezione != "A" for r in costo.righe), "le apparecchiature si comprano a parte"
    assert costo.totale == pytest.approx(sum(r.totale or 0 for r in costo.righe))
    tubo = next(r for r in costo.righe if r.testo == "Tubo multistrato MS 32×3, nudo")
    assert tubo.totale == pytest.approx(28.0 * listino.get("I04").prezzo)
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
    md = (tmp_path / "d" / "interno" / "costo-minuteria.md").read_text(encoding="utf-8")
    assert "Uso interno Nove C" in md and "Totale prezzato" in md
    dati = json.loads((tmp_path / "d" / "interno" / "costo-minuteria.json").read_text(encoding="utf-8"))
    assert dati["totale_eur"] > 0 and dati["listino"]["revisione"].startswith("05")
    documento = next((tmp_path / "d").glob("Distinta_*.md")).read_text(encoding="utf-8")
    assert "€" not in documento, "il documento per l'installatore resta senza prezzi"
    consegnati = consegna(tmp_path / "d", tmp_path / "consegna")
    assert consegnati and not [p for p in consegnati if p.name.startswith("costo-minuteria")], "il costo non si consegna"


def test_senza_i_tubi_della_chat_la_rete_e_da_definire_e_si_chiede(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    grafo = _centrale()
    del grafo["distinta"]
    distinta = componi_la_distinta(grafo, regole, *nomi)
    voce = next(v for v in distinta.voci if v.testo.startswith("Tubo della rete"))
    assert voce.quantita is None and voce.da_definire
    assert any("quanti metri di tubo, di che diametro e come isolato" in d for d in distinta.domande)


def test_il_tubo_preisolato_non_ha_guaina_e_le_staffe_solo_se_chieste(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    grafo = _centrale()
    grafo["distinta"] = {"tubi": [{"rete": "primario", "tubo": "MS 32×3", "metri": 10, "isolamento": "preisolato"}],
                         "gomiti": 12}
    grafo["components"][0]["properties"]["posa"] = "su staffe a muro"
    distinta = componi_la_distinta(grafo, regole, *nomi)
    testi = {v.testo: v for v in distinta.voci}
    assert "Tubo multistrato MS 32×3 preisolato" in testi
    assert not [t for t in testi if t.startswith("Guaina") or t.endswith(", nudo")]
    assert testi["Gomito 90° a pressare tubo multistrato MS 32×3, a corpo"].quantita == 12
    assert [v.testo for v in distinta.voci_della_sezione("S")] == [
        "Staffe a muro per l'unità esterna, portata 160 kg, con gommini antivibranti (coppia)"
    ]


def test_completa_conserva_i_dati_della_chat(tmp_path: Path) -> None:
    """I tubi d'acqua del progettista stanno nel blocco «distinta» del grafo: un nuovo
    `completa` non li cancella (collaudi T1, T2 e T4 di REL-021: le risposte si perdevano)."""
    grafo = json.loads((ROOT / "docs" / "collaudi" / "REL-017" / "diametri" / "grafo.json").read_text(encoding="utf-8"))
    blocco = {"tubi": [{"rete": "primario", "tubo": "MS 32×3", "metri": 30, "isolamento": "preisolato"}], "gomiti": 18}
    grafo["distinta"] = blocco
    prima = tmp_path / "grafo.json"
    prima.write_text(json.dumps(grafo, ensure_ascii=False), encoding="utf-8")
    dopo = tmp_path / "grafo-completo.json"
    assert main(["completa", str(prima), "--out", str(dopo)], cartelle_del_repository(ROOT)) == 0
    letto = json.loads(dopo.read_text(encoding="utf-8"))["distinta"]
    assert letto["gomiti"] == 18 and letto["tubi"][0]["metri"] == 30 and letto["tubi"][0]["isolamento"] == "preisolato"


def test_i_gomiti_sono_un_ipotesi_che_si_chiede(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    """I-288: i gomiti a corpo si chiedono in chat come i metri; senza risposta la voce
    porta l'ipotesi di 20 e resta da confermare."""
    distinta = componi_la_distinta(_centrale(), regole, *nomi)
    gomiti = next(v for v in distinta.voci if v.testo.startswith("Gomito 90°"))
    assert gomiti.quantita == 20 and gomiti.da_definire
    assert any("Quanti gomiti a corpo" in d for d in distinta.domande)


def _con_filtro_e_pozzetto(compreso: bool) -> dict[str, Any]:
    """La centrale con un filtro a Y sul ritorno e una sonda nel suo pozzetto; con
    `compreso`, tutti e due nella fornitura della pompa di calore."""
    grafo = _centrale()
    dato = {"compreso_in": "GT-01"} if compreso else {}
    grafo["components"] += [
        {"id": "fy", "definition_id": "strainer", "tag": "FY-01", "properties": dict(dato)},
        {"id": "so", "definition_id": "temperature-probe", "tag": "SO-01", "properties": dict(dato)},
    ]
    grafo["connections"] = [c for c in grafo["connections"] if c["id"] != "r2"] + [
        _tubo("r2", "primario", ("v2", "b"), ("fy", "a"), sezione="MS 32×3"),
        _tubo("r3", "primario", ("fy", "b"), ("pdc", "water_return"), lunghezza_m=10, sezione="MS 32×3"),
    ]
    return grafo


def test_compreso_nella_pompa_di_calore_non_si_compra_due_volte(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    """I-297, dal progetto reale: «la dicitura “compreso con la PdC” non toglie dalla distinta
    gli accessori di corredo (filtro a Y, pozzetti)». `compreso_in` toglieva solo la riga della
    macchina in sezione A; un accessorio compreso resta nella sua tavola e nelle giunzioni,
    ma non si compra: lo dice la riga della pompa di calore («comprende …»)."""
    senza = componi_la_distinta(_con_filtro_e_pozzetto(False), regole, *nomi)
    con = componi_la_distinta(_con_filtro_e_pozzetto(True), regole, *nomi)

    def contributi(distinta: Any, sigla: str) -> list[str]:
        return [v.testo for v in distinta.voci if any(chi == sigla for chi, _ in v.contributi)]

    assert contributi(senza, "FY-01") and contributi(senza, "SO-01"), "il caso non prova niente"
    assert contributi(con, "FY-01") == [] and contributi(con, "SO-01") == []
    pdc = next(v for v in con.voci_della_sezione("A") if "GT-01" in v.note)
    assert "comprende FY-01" in pdc.note and "comprende SO-01" in pdc.note
