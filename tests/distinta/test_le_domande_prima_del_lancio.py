"""Le domande della distinta si fanno al passo 2, prima del primo lancio (REL-016, D4).

Il collaudo indipendente della 1.7.0 ha chiesto la distinta di un canalizzato: al passo 2
la skill aveva fatto le domande del disegno — sezioni e lunghezze — e non quelle della
distinta, e il primo lancio e' uscito con «DA DEFINIRE — 12 voci»: refrigerante e
precarica, bocchette, attacco della condensa, protezioni. Si e' dovuto rifare il giro di
domande al progettista.

`mep.py distinta --domande` dice quelle domande prima del lancio, dal grafo completo e dalle
regole, senza scrivere niente. Le prove: sul trilocale del collaudo le domande coprono
**ogni** voce DA DEFINIRE; con le risposte nel grafo la distinta esce con le sole voci
che il progettista lascia aperte di proposito (marca e modello); le domande sono in parole,
senza codici interni; e `SKILL.md` le fa chiedere nello stesso giro del disegno.
"""
# categoria: difende il prodotto

import contextlib
import copy
import io
import json
import re
from pathlib import Path
from typing import Any

from disegnatore_mep.distinta import Distinta, RegoleDellaDistinta, componi_la_distinta
from disegnatore_mep.distinta.calcolo import SEGNAPOSTO
from disegnatore_mep.distinta.domande import DATI, domande_in_parole
from disegnatore_mep.skill import cartelle_del_repository, main

from .conftest import REGOLE, ROOT, pezzo, sigle, tubazione

D4 = ROOT / "docs" / "collaudi" / "REL-016" / "d4"
AL_PASSO_2 = D4 / "trilocale-al-passo-2.json"
"""Il trilocale del collaudo come lo scrive il passo 2 senza le domande della distinta."""
RISPOSTE = D4 / "risposte.json"
T2 = ROOT / "docs" / "collaudi" / "REL-012" / "collaudo-t2" / "grafo-completo.json"
"""Un idronico: la distinta non ne ha le regole, e le domande lo devono dire."""


def _lancia(argomenti: list[str]) -> tuple[int, str]:
    uscita = io.StringIO()
    with contextlib.redirect_stdout(uscita), contextlib.redirect_stderr(io.StringIO()):
        codice = main(argomenti, cartelle_del_repository(ROOT))
    return codice, uscita.getvalue()


def _completa(grafo: dict[str, Any], cartella: Path) -> Path:
    prima = cartella / "grafo.json"
    prima.write_text(json.dumps(grafo, ensure_ascii=False), encoding="utf-8")
    completo = cartella / "grafo-completo.json"
    codice, _ = _lancia(["completa", str(prima), "--out", str(completo)])
    assert codice == 0
    return completo


def _con_le_risposte() -> dict[str, Any]:
    grafo = json.loads(AL_PASSO_2.read_text(encoding="utf-8"))
    risposte = json.loads(RISPOSTE.read_text(encoding="utf-8"))
    for chiave in ("components", "connections"):
        for elemento in grafo[chiave]:
            elemento.setdefault("properties", {}).update(risposte[chiave].get(elemento["id"], {}))
    return grafo


def _distinta(completo: Path, regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]) -> Distinta:
    grafo = json.loads(completo.read_text(encoding="utf-8"))
    return componi_la_distinta(grafo, regole, *nomi, sigle(grafo))


def test_sul_trilocale_le_domande_coprono_ogni_voce_da_definire(
    tmp_path: Path, regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    """Il trilocale al passo 2 fa le dodici voci DA DEFINIRE del collaudo; ognuna ha i suoi
    dati mancanti, e `--domande` li chiede tutti — il dato in parole e il pezzo o il tratto
    a cui manca — prima del lancio."""
    completo = _completa(json.loads(AL_PASSO_2.read_text(encoding="utf-8")), tmp_path)
    distinta = _distinta(completo, regole, nomi)
    assert len(distinta.da_definire) == 12, [v.testo for v in distinta.da_definire]
    codice, stampa = _lancia(["distinta", str(completo), "--domande"])
    assert codice == 2
    domande = stampa.split("Per la verifica")[0]
    for voce in distinta.da_definire:
        assert voce.mancanti, f"{voce.testo}: DA DEFINIRE senza un dato da chiedere"
        for mancante in voce.mancanti:
            riga = next((r for r in domande.splitlines() if DATI[mancante.dato].domanda in r), "")
            assert mancante.chi in riga, f"{voce.testo}: «{mancante.dato}» di {mancante.chi} non e' chiesto"
    for dato in ("refrigerante", "precarica_fino_a_m", "carica_aggiuntiva_g_m", "attacco_condensa", "dimensione", "protezione"):
        assert DATI[dato].domanda in domande, dato
    verifica = stampa.split("Per la verifica")[1]
    assert DATI["portata_m3h"].domanda in verifica and DATI["lunghezza_max_m"].domanda in verifica
    assert "Da confermare" in stampa, "la fornitura si chiede nello stesso giro"


def test_con_le_risposte_restano_aperti_solo_marca_e_modello(
    tmp_path: Path, regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    """Le risposte scritte nei campi che `--domande` dice bastano: la distinta esce senza
    DA DEFINIRE, salvo marca e modello che il progettista lascia aperti di proposito."""
    completo = _completa(_con_le_risposte(), tmp_path)
    distinta = _distinta(completo, regole, nomi)
    assert distinta.da_definire and all(v.regola.endswith("/apparecchiatura") for v in distinta.da_definire), [
        v.testo for v in distinta.da_definire
    ]
    assert not [e for e in distinta.verifica if e.esito == "non verificabile"]
    _, stampa = _lancia(["distinta", str(completo), "--domande"])
    assert "Le domande della distinta — 1," in stampa and "1. Marca e modello" in stampa
    assert "Per la verifica" not in stampa


def test_le_domande_sono_in_parole_senza_codici_interni(tmp_path: Path) -> None:
    """Le domande vanno al progettista: niente decisioni o input del repository, niente id di
    regole o impronte, niente segnaposto lasciati nel testo. I campi del grafo si nominano
    fra caporali, perche' l'agente sappia dove scrivere la risposta."""
    completo = _completa(json.loads(AL_PASSO_2.read_text(encoding="utf-8")), tmp_path)
    for grafo in (completo, T2):
        _, stampa = _lancia(["distinta", str(grafo), "--domande"])
        assert stampa.strip()
        assert not re.findall(r"\b[DI]-\d{3}\b", stampa)
        assert not re.findall(r"\b[0-9a-f]{16}\b", stampa)
        assert not re.findall(r"\b(?:fluidi|corredo|attivita)/", stampa)
        assert "DA DEFINIRE (" not in stampa and "`" not in stampa
    assert "non ha regole nella distinta" in stampa, "l'idronico senza regole si dice"


def test_i_dati_di_macchina_si_chiedono_anche_senza_la_lunghezza(
    grafo_aa01: dict[str, Any], regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    """Le domande si fanno tutte in un giro: la riserva di refrigerante e la verifica della
    linea non aspettano la lunghezza per chiedere i dati della scheda della macchina."""
    for ident in ("r-liq", "r-gas"):
        del tubazione(grafo_aa01, ident)["properties"]["lunghezza_m"]
    for chiave in ("precarica_fino_a_m", "carica_aggiuntiva_g_m", "lunghezza_max_m"):
        del pezzo(grafo_aa01, "ue")["properties"][chiave]
    distinta = componi_la_distinta(grafo_aa01, regole, *nomi, sigle(grafo_aa01))
    chiesti = {(m.dato, m.chi) for m in [*distinta.mancanti, *distinta.mancanti_della_verifica]}
    assert {("precarica_fino_a_m", "UE-01"), ("carica_aggiuntiva_g_m", "UE-01"), ("lunghezza_max_m", "UE-01")} <= chiesti
    frigorifere = [t.num for t in distinta.tratte if t.fluido.startswith("refrigerant")]
    assert len(frigorifere) == 2 and {("lunghezza_m", n) for n in frigorifere} <= chiesti


def test_ogni_dato_dei_testi_delle_regole_ha_le_sue_parole() -> None:
    """Un dato nuovo nei testi delle regole della distinta ha la sua domanda in parole: se
    no, `--domande` lo direbbe col nome del campo e basta."""
    del_codice = {"rete", "sigla"}
    dati = set()
    for file in REGOLE.glob("*.json"):
        for trovato in SEGNAPOSTO.finditer(file.read_text(encoding="utf-8")):
            nome = trovato.group(1)
            if "." not in nome and nome not in del_codice and nome != "proprieta":
                dati.add(nome)
    assert dati and dati <= set(DATI), sorted(dati - set(DATI))


def test_le_domande_non_scrivono_niente_e_la_distinta_vuole_la_cartella(tmp_path: Path) -> None:
    grafo = tmp_path / "grafo-completo.json"
    grafo.write_text((ROOT / "examples" / "distinta" / "AA-01" / "grafo-completo.json").read_text(encoding="utf-8"))
    codice, stampa = _lancia(["distinta", str(grafo), "--domande"])
    assert codice == 0 and "nessuna" in stampa
    assert sorted(p.name for p in tmp_path.iterdir()) == ["grafo-completo.json"]
    assert _lancia(["distinta", str(grafo)])[0] == 1


def test_le_domande_della_distinta_si_fanno_al_passo_2() -> None:
    """`SKILL.md` fa lanciare `--domande` al passo 2 e portare le domande nello stesso
    messaggio; le istruzioni della distinta dicono lo stesso."""
    skill = (ROOT / "skill" / "SKILL.md").read_text(encoding="utf-8")
    passo_2 = skill.split("### 2. Le domande")[1].split("### 3.")[0]
    assert "distinta $L/grafo-completo.json --domande" in passo_2
    assert "stesso messaggio" in passo_2
    istruzioni = (ROOT / "skill" / "distinta" / "ISTRUZIONI.md").read_text(encoding="utf-8")
    assert "--domande" in istruzioni and "nello stesso giro" in istruzioni


def test_la_domanda_resta_uguale_se_il_grafo_e_lo_stesso(
    grafo_aa01: dict[str, Any], regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    """Deterministica: lo stesso grafo da' le stesse domande."""
    del pezzo(grafo_aa01, "bocchetta-b2")["properties"]["dimensione"]
    righe = [
        domande_in_parole(componi_la_distinta(copy.deepcopy(grafo_aa01), regole, *nomi, sigle(grafo_aa01)))
        for _ in range(2)
    ]
    assert righe[0] == righe[1]
    assert any("B2" in r and DATI["dimensione"].domanda in r for r in righe[0][0])
