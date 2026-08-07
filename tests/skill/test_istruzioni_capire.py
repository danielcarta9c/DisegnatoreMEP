"""Le istruzioni dell'interprete: due promesse che non devono decadere.

Le istruzioni sono un file di testo per un agente, non programma — ma due
cose che promettono si possono verificare, e sono le due su cui il collaudo
del 7 agosto le ha respinte:

1. **L'esempio del §3 carica.** Le istruzioni lo dichiarano «completo e
   caricabile», e un agente che lo copia come stampo deve ottenere un file
   valido. Se lo schema cambia e l'esempio no, la promessa diventa falsa.
2. **Gli esempi non contengono le risposte dei testi di prova.** Il collaudo
   ha trovato tre esempi che ricalcavano quasi parola per parola le
   assunzioni delle letture manuali dei cinque impianti del committente:
   finche' e' cosi', una prova in camera pulita su quei testi non misura le
   istruzioni, misura il ricordo dell'esempio.

Il conto della somiglianza e' grezzo di proposito: non serve un giudizio
fine, serve accorgersi se un esempio torna a essere la copia di una
soluzione.
"""

import difflib
import json
import re
import tempfile
from pathlib import Path

from disegnatore_mep.io.project_json import load_project

ROOT = Path(__file__).resolve().parents[2]
ISTRUZIONI = ROOT / "skill" / "capire" / "ISTRUZIONI.md"
PROVE = ROOT / "examples" / "prova"

SOMIGLIANZA_MASSIMA = 0.60
"""Oltre questa soglia un esempio e' la copia di una soluzione reale.

Il valore non e' tarato su una fixture: e' il punto oltre il quale due
frasi italiane condividono la struttura oltre al tema. Gli esempi attuali
stanno sotto il 50%, quelli respinti dal collaudo erano sopra il 90%."""


def istruzioni() -> str:
    return ISTRUZIONI.read_text(encoding="utf-8")


def test_l_esempio_delle_istruzioni_carica_davvero() -> None:
    """Il §3 promette «completo e caricabile»: qui la promessa si verifica."""
    block = re.search(r"```json\n(.*?)\n```", istruzioni(), re.S)
    assert block is not None, "le istruzioni non hanno piu' l'esempio di file"
    payload = block.group(1)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
        handle.write(payload)
        path = Path(handle.name)
    model = load_project(path)
    assert model.subsystems == []
    assert model.rule_applications == []
    assert model.sheets == []


def test_l_esempio_ricava_il_regime_dalla_potenza_che_dichiara() -> None:
    """L'esempio dichiara una potenza: allora deve mostrare anche il regime.

    Se l'esempio trascrivesse la potenza e lasciasse fuori il regime,
    contraddirebbe il §4.6 — e un agente segue l'esempio prima della regola."""
    block = re.search(r"```json\n(.*?)\n```", istruzioni(), re.S)
    assert block is not None
    payload = json.loads(block.group(1))
    potenze = [
        item["properties"]["potenza"]
        for item in payload["components"]
        if "potenza" in item.get("properties", {})
    ]
    assert potenze, "l'esempio non dichiara piu' nessuna potenza"
    assert payload.get("plant_regime") is not None, (
        "l'esempio dichiara una potenza e non il regime: contraddice il §4.6"
    )


def test_nessun_esempio_ricalca_una_soluzione_dei_testi_di_prova() -> None:
    """Il difetto per cui il collaudo ha respinto le istruzioni.

    Gli esempi di assunzione — le frasi fra virgolette basse in corsivo —
    non devono somigliare alle assunzioni delle letture manuali dei cinque
    impianti del committente: se le contengono, la prova in camera pulita su
    quei testi non misura piu' le istruzioni da sole."""
    reali = [
        voce["text"]
        for path in sorted(PROVE.glob("prova-*.json"))
        for voce in json.loads(path.read_text(encoding="utf-8"))["assumptions"]
    ]
    assert reali, "nessuna lettura manuale da confrontare"
    esempi = re.findall(r"\*«([^»]+)»\*", istruzioni())
    assert esempi, "le istruzioni non hanno piu' esempi di assunzione"
    troppo_simili = [
        (esempio, reale, ratio)
        for esempio in esempi
        for reale in reali
        if (ratio := difflib.SequenceMatcher(None, esempio.lower(), reale.lower()).ratio())
        > SOMIGLIANZA_MASSIMA
    ]
    assert not troppo_simili, [
        (f"{ratio:.0%}", esempio[:70], reale[:70])
        for esempio, reale, ratio in troppo_simili
    ]
