"""I difetti della distinta trovati dal primo collaudo indipendente (REL-012, caso t1).

Il rapporto e' `docs/collaudi/REL-012/collaudo-t1/RAPPORTO.md`, §2.2 e §2.4; il grafo e'
quello che il collaudo ha fatto con la skill (`collaudo-t1/grafo-completo.json`): un
canalizzato Mitsubishi con zonizzazione Airzone, quattro bocchette (piu' l'uscita tappata
del ripiego del §2.1), il cartiglio con committente e commessa «ND».
"""

import copy
import json
import re
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.distinta import DA_DEFINIRE, Distinta, RegoleDellaDistinta, componi_la_distinta
from disegnatore_mep.distinta.regole import ErroreDelleRegole, la_fornitura
from disegnatore_mep.skill import cartelle_del_repository, main

from .conftest import COLLAUDO_T1, ROOT, pezzo, sigle

Nomi = tuple[dict[str, str], dict[str, str]]


@pytest.fixture
def grafo_t1() -> dict[str, Any]:
    return copy.deepcopy(json.loads(COLLAUDO_T1.read_text(encoding="utf-8")))


def _distinta(grafo: dict[str, Any], regole: RegoleDellaDistinta, nomi: Nomi, fornitura: str | None = None) -> Distinta:
    return componi_la_distinta(grafo, regole, *nomi, sigle(grafo), la_fornitura(regole, fornitura))


# --- §2.4.1 una lunghezza che manca non cancella quelle date -------------------------


def test_il_bus_senza_una_lunghezza_tiene_i_metri_noti(
    grafo_t1: dict[str, Any], regole: RegoleDellaDistinta, nomi: Nomi
) -> None:
    """I tre bus ai termostati (7 + 5 + 9 m) e il collegamento centrale-UI, senza lunghezza:
    prima la voce intera era DA DEFINIRE e i 28 m noti sparivano."""
    distinta = _distinta(grafo_t1, regole, nomi)
    cavo = [v for v in distinta.voci if v.regola.endswith("/cavo-di-bus")]
    # 28 m noti (DA DEFINIRE solo la sezione del cavo, che il grafo non da'), poi T15, poi il comando a filo.
    # T15 e' CZ-01 - UI-01: nell'ordine delle sigle viene prima di UI-01 - CF-01 (collaudo T3).
    assert [v.quantita for v in cavo] == [28, None, 8.5]
    assert cavo[0].calcolo == "T12 9,5 + T13 7 + T14 11,5 = 28 m"
    assert "Bus ai termostati di zona" in cavo[0].testo and "Collegamento centrale" not in cavo[0].testo
    assert "manca la lunghezza di T15" in cavo[1].calcolo and "Collegamento centrale di zona" in cavo[1].testo
    corrugato = [v for v in distinta.voci if v.regola.endswith("/corrugato-di-bus")]
    assert [v.quantita for v in corrugato] == [40, None]
    assert any("T15" in d and "quanto e' lungo" in d for d in distinta.domande)


# --- §2.4.2 griglie di transito per locale ------------------------------------------


def _griglie(distinta: Distinta) -> list[Any]:
    return [v for v in distinta.voci if v.regola.endswith("griglia-di-transito")]


def test_due_bocchette_nello_stesso_locale_vogliono_una_griglia(
    grafo_t1: dict[str, Any], regole: RegoleDellaDistinta, nomi: Nomi
) -> None:
    """Il soggiorno ha due bocchette («Z3 Soggiorno (sopra il varco)», «Z3 Soggiorno
    (veletta)»): conta uno. Il collaudo ne contava 5, una per bocchetta."""
    [griglia] = _griglie(_distinta(grafo_t1, regole, nomi))
    assert griglia.quantita == 4
    assert griglia.note.count("Z3 Soggiorno") == 1
    assert "4 locali serviti" in griglia.calcolo


def test_un_locale_con_un_varco_non_vuole_la_griglia(
    grafo_t1: dict[str, Any], regole: RegoleDellaDistinta, nomi: Nomi
) -> None:
    pezzo(grafo_t1, "bocchetta-soggiorno-1")["properties"]["varco"] = "varco di 1,5 m verso il disimpegno"
    distinta = _distinta(grafo_t1, regole, nomi)
    [griglia] = _griglie(distinta)
    assert griglia.quantita == 3 and "Z3 Soggiorno" not in griglia.note
    assert "nessuna dove il locale ha un varco: Z3 Soggiorno" in griglia.calcolo
    varco = [e for e in distinta.verifica if e.dove == "Z3 Soggiorno"]
    assert [(e.controllo, e.soglia) for e in varco] == [("varco verso la ripresa", "Aeff ≥ 0,112 m²")]


def test_il_locale_si_scrive_col_suo_dato(
    grafo_t1: dict[str, Any], regole: RegoleDellaDistinta, nomi: Nomi
) -> None:
    for ident in ("bocchetta-matrimoniale", "bocchetta-singola"):
        pezzo(grafo_t1, ident)["properties"]["locale"] = "Zona notte"
    [griglia] = _griglie(_distinta(grafo_t1, regole, nomi))
    assert griglia.quantita == 3 and "Zona notte" in griglia.note


def test_una_bocchetta_senza_locale_e_una_domanda(
    grafo_t1: dict[str, Any], regole: RegoleDellaDistinta, nomi: Nomi
) -> None:
    del pezzo(grafo_t1, "bocchetta-singola")["properties"]["etichetta"]
    distinta = _distinta(grafo_t1, regole, nomi)
    [griglia] = _griglie(distinta)
    assert griglia.quantita == 4 and griglia.da_definire
    assert any("TA-02" in d and "che locale serve?" in d for d in distinta.domande)


# --- §2.4.3 il refrigerante dato non si chiede ----------------------------------------


def test_il_refrigerante_dato_non_si_chiede(grafo_t1: dict[str, Any], regole: RegoleDellaDistinta, nomi: Nomi) -> None:
    distinta = _distinta(grafo_t1, regole, nomi)
    [carica] = [v for v in distinta.voci if v.regola.endswith("carica-aggiuntiva")]
    assert carica.testo.startswith("Refrigerante R32,") and carica.quantita is None
    [domanda] = carica.domande
    assert "`precarica_fino_a_m` e `carica_aggiuntiva_g_m`" in domanda
    assert "refrigerante`" not in domanda


# --- §2.4.4 le scelte commerciali sono dati ---------------------------------------------


def test_la_fornitura_predefinita_si_dichiara_da_confermare(
    grafo_t1: dict[str, Any], regole: RegoleDellaDistinta, nomi: Nomi
) -> None:
    distinta = _distinta(grafo_t1, regole, nomi)
    [riga] = distinta.da_confermare
    assert riga.startswith("Fornitura: apparecchiature fornite da Nove C; bocchette e griglie del Committente;")
    assert riga.endswith("come da regole predefinite di Nove C; confermare per questa offerta.")
    assert (
        "Fornitura da confermare: apparecchiature fornite da Nove C; bocchette e griglie, opere edili del "
        "Committente; messa in servizio con Nove C."
    ) in distinta.note, "sul foglio, in una riga"
    assert all(v.fornitura == "Nove C" for v in distinta.voci_della_sezione("A"))


def test_la_fornitura_si_cambia_per_l_offerta(
    grafo_t1: dict[str, Any], regole: RegoleDellaDistinta, nomi: Nomi
) -> None:
    distinta = _distinta(
        grafo_t1, regole, nomi, "apparecchiature=installatore, bocchette_e_griglie=installatore, messa_in_servizio=installatore"
    )
    assert not distinta.da_confermare
    assert (
        "Fornitura: apparecchiature fornite dall'installatore; bocchette e griglie dell'installatore; opere edili "
        "del Committente; messa in servizio a cura dell'installatore."
    ) in distinta.note
    assert {v.fornitura for v in distinta.voci_della_sezione("A")} == {"installatore"}
    bocchette = [v for v in distinta.voci if v.regola.endswith("bocchetta-di-mandata")]
    assert bocchette and all(v.sezione == "B" and v.fornitura == "installatore" for v in bocchette)
    assert not [v for v in distinta.voci_della_sezione("Z") if "Bocchetta" in v.testo or "Griglia" in v.testo]
    assert [v for v in distinta.voci_della_sezione("Z") if "Botola" in v.testo], "le opere edili restano del Committente"
    testi = " ".join(v.testo for v in distinta.voci_della_sezione("G"))
    assert "con Nove C" not in testi and "fornite da Nove C" not in testi


def test_una_fornitura_che_non_c_e_e_un_errore(regole: RegoleDellaDistinta) -> None:
    with pytest.raises(ErroreDelleRegole, match="le scelte sono apparecchiature="):
        la_fornitura(regole, "caldaie=installatore")
    with pytest.raises(ErroreDelleRegole, match="bocchette_e_griglie vale committente, installatore"):
        la_fornitura(regole, "bocchette_e_griglie=Nove C")
    assert la_fornitura(regole, "confermata").confermata
    assert la_fornitura(regole, "apparecchiature=nove-c").valori["apparecchiature"] == "Nove C"


# --- §2.4.5-6 niente codici interni, §2.2.9 il cartiglio ---------------------------------

FONTI_DI_SVILUPPO = re.compile(
    r"lavoro/|\.py\b|\.md\b|RAPPORTO|REVISIONE|rilievo \d|kit AA-01|rules/|sessione di sviluppo|D-\d{3}"
)
SIGLE = re.compile(r"[A-Z]{1,4}-\d{2}( - [A-Z]{1,4}-\d{2})*")


def _celle_dell_excel(percorso: Path) -> list[str]:
    openpyxl = pytest.importorskip("openpyxl")
    libro = openpyxl.load_workbook(percorso)
    return [str(c) for f in libro for r in f.iter_rows(values_only=True) for c in r if c is not None]


def _celle_delle_tabelle(percorso: Path) -> list[str]:
    dati = json.loads(percorso.read_text(encoding="utf-8"))
    celle = [str(t["titolo"]) for t in dati["tabelle"]]
    for tabella in dati["tabelle"]:
        for sezione in tabella["sezioni"]:
            celle += [str(sezione["titolo"] or "")] + [str(c) for riga in sezione["righe"] for c in riga]
    return celle


@pytest.fixture(scope="module")
def uscite_t1(tmp_path_factory: pytest.TempPathFactory) -> Path:
    cartella = tmp_path_factory.mktemp("t1")
    assert main(["distinta", str(COLLAUDO_T1), "--out", str(cartella)], cartelle_del_repository(ROOT)) == 2
    return cartella


def test_nelle_uscite_per_l_installatore_niente_id_del_grafo(uscite_t1: Path) -> None:
    grafo = json.loads(COLLAUDO_T1.read_text(encoding="utf-8"))
    ids = [c["id"] for c in grafo["components"] if "-" in c["id"]] + [c["id"] for c in grafo["connections"]]
    ids += [n["id"] for n in grafo["networks"] if "-" in n["id"]]
    for celle in (_celle_delle_tabelle(uscite_t1 / "tabelle-del-foglio.json"), _celle_dell_excel(uscite_t1 / "distinta.xlsx")):
        testo = "\n".join(celle)
        trovati = [i for i in ids if re.search(rf"(?<![\w-]){re.escape(i)}(?![\w-])", testo)]
        assert trovati == []
    tratte = json.loads((uscite_t1 / "tabelle-del-foglio.json").read_text(encoding="utf-8"))["tabelle"][0]
    da_a = [riga[1] for riga in tratte["sezioni"][0]["righe"]]
    assert da_a[0] == "PLZ-01 - TA-01"
    assert all(SIGLE.fullmatch(cella) for cella in da_a), da_a


def test_nelle_uscite_per_l_installatore_niente_fonti_di_sviluppo(uscite_t1: Path) -> None:
    for celle in (_celle_delle_tabelle(uscite_t1 / "tabelle-del-foglio.json"), _celle_dell_excel(uscite_t1 / "distinta.xlsx")):
        trovate = sorted({m.group(0) for c in celle for m in [FONTI_DI_SVILUPPO.search(c)] if m})
        assert trovate == []


def test_il_cartiglio_che_manca_e_da_definire_come_sulla_tavola(uscite_t1: Path) -> None:
    celle = _celle_dell_excel(uscite_t1 / "distinta.xlsx")
    assert celle[0].startswith(f"{DA_DEFINIRE} — Canalizzato aria-aria")
    assert f"Committente: {DA_DEFINIRE}." in celle[1] and f"Allegata alla tavola {DA_DEFINIRE}, rev. 00" in celle[1]
    assert not [c for c in celle[:2] if re.search(r"\bND\b|tavola -", c)]
    calcoli = (uscite_t1 / "distinta-calcoli.md").read_text(encoding="utf-8")
    assert calcoli.startswith(f"# Distinta materiali — foglio dei calcoli ({DA_DEFINIRE}, tavola {DA_DEFINIRE} rev. 00)")
    assert "(ND" not in calcoli and f"Committente: {DA_DEFINIRE}" in calcoli


# --- §2.2.3 e la tavola in A1: quali tabelle vanno sul foglio -----------------------------


def test_sul_foglio_vanno_le_tabelle_scelte(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cartelle = cartelle_del_repository(ROOT)
    argomenti = ["distinta", str(COLLAUDO_T1), "--out", str(tmp_path), "--sul-foglio", "note,tratte"]
    assert main(argomenti, cartelle) == 2
    tabelle = json.loads((tmp_path / "tabelle-del-foglio.json").read_text(encoding="utf-8"))["tabelle"]
    assert [t["id"] for t in tabelle] == ["tratte", "note"]
    assert "Sul foglio: tratte, note; il resto e' nell'Excel." in capsys.readouterr().out
    assert main([*argomenti[:-1], "tratte,legenda"], cartelle) == 1
    assert "--sul-foglio: legenda; le tabelle sono tratte, computo, attivita, note" in capsys.readouterr().err


def test_il_comando_prende_la_fornitura(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cartelle = cartelle_del_repository(ROOT)
    assert main(["distinta", str(COLLAUDO_T1), "--out", str(tmp_path / "a")], cartelle) == 2
    assert "Da confermare col progettista" in capsys.readouterr().out
    argomenti = ["distinta", str(COLLAUDO_T1), "--out", str(tmp_path / "b"), "--fornitura", "confermata"]
    assert main(argomenti, cartelle) == 2
    assert "Da confermare" not in capsys.readouterr().out
    scritta = json.loads((tmp_path / "b" / "distinta.json").read_text(encoding="utf-8"))
    assert scritta["da_confermare"] == []
    assert main([*argomenti[:-1], "apparecchiature=boh"], cartelle) == 1


# --- le istruzioni della distinta (§2.2.2, §2.2.3, §2.2.11) -------------------------------


def test_le_istruzioni_della_distinta() -> None:
    testo = (ROOT / "skill" / "distinta" / "ISTRUZIONI.md").read_text(encoding="utf-8")
    assert "non sono nella skill" not in testo
    assert "**prima** di `disegna`" in testo
    assert "disegna --tabelle <cartella>/tabelle-del-foglio.json" in testo
    assert "--sul-foglio tratte,note" in testo and "--fornitura" in testo
    assert "basta su **una** tubazione del tratto" in testo
    assert "`locale`" in testo and "`varco`" in testo
