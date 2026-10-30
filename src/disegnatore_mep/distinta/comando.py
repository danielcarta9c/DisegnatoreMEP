"""`mep.py distinta <grafo-completo.json> --out <cartella> [--regole <cartella o fascio>]
[--sul-foglio tratte,computo,attivita,note] [--fornitura <scelte>|confermata]`.

Si lancia **prima** di `disegna`: le tabelle del foglio (`disegna --tabelle
<cartella>/tabelle-del-foglio.json`) le scrive lei. `--sul-foglio` sceglie quali tabelle
vanno nel file del foglio (di default tutte: il computo intero porta di solito la tavola
in A1). `--fornitura` conferma o cambia chi fornisce che cosa in questa offerta; senza,
la distinta usa le scelte predefinite di Nove C e le dichiara da confermare.

**Spenta di default** (proposta D-213): la distinta si fa solo con questo comando,
che il progettista chiede. Nessun altro comando la produce, e nessuno cambia per lei.

Codici di uscita come gli altri comandi della skill: `0` fatto; `2` fatto, ma ci sono
voci DA DEFINIRE e domande al progettista — la distinta non si consegna
all'installatore finche' non hanno risposta; `1` non si e' potuto fare.
"""

import json
import sys
from pathlib import Path

from .calcolo import componi_la_distinta
from .grafo import sigle_dello_schema
from .regole import ErroreDelleRegole, carica_regole, la_fornitura, regole_predefinite
from .uscite import TABELLE_DEL_FOGLIO, ha_openpyxl, scrivi_le_uscite, tabelle_scelte


def nomi_del_catalogo(cartella: Path) -> dict[str, str]:
    """Il nome in parole di ogni voce, letto dai JSON del catalogo senza caricarlo:
    alla distinta basta il nome, e una voce che il catalogo non ha ancora prende quello
    del corredo."""
    nomi: dict[str, str] = {}
    if not cartella.is_dir():
        return nomi
    for percorso in sorted(cartella.glob("*.json")):
        try:
            voce = json.loads(percorso.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(voce, dict) and isinstance(voce.get("id"), str) and isinstance(voce.get("name"), str):
            nomi[voce["id"]] = voce["name"]
    return nomi


def nomi_dei_fluidi(cartella_dei_nomi: Path) -> dict[str, str]:
    percorso = cartella_dei_nomi / "media.json"
    if not percorso.is_file():
        return {}
    dati = json.loads(percorso.read_text(encoding="utf-8"))
    return {str(m["medium"]): str(m["name"]) for m in dati.get("media", []) if "medium" in m and "name" in m}


def esegui(
    grafo: Path,
    uscita: Path,
    regole: Path | None,
    cartella_delle_regole: Path,
    cartella_del_catalogo: Path,
    cartella_dei_nomi: Path,
    sul_foglio: str | None = None,
    fornitura: str | None = None,
) -> int:
    tabelle = tabelle_scelte(sul_foglio)
    percorso_delle_regole = regole or regole_predefinite(cartella_delle_regole, cartella_dei_nomi)
    if percorso_delle_regole is None:
        raise ErroreDelleRegole(
            "le regole della distinta non ci sono accanto ai dati: indicale con --regole <cartella o fascio>"
        )
    try:
        dati = json.loads(grafo.read_text(encoding="utf-8"))
    except json.JSONDecodeError as errore:
        raise ValueError(f"{grafo}: non e' JSON valido ({errore})") from errore
    regole_caricate = carica_regole(percorso_delle_regole)
    distinta = componi_la_distinta(
        dati,
        regole_caricate,
        nomi_del_catalogo(cartella_del_catalogo),
        nomi_dei_fluidi(cartella_dei_nomi),
        sigle_dello_schema(dati, cartella_del_catalogo, cartella_dei_nomi),
        la_fornitura(regole_caricate, fornitura),
    )
    scritti = scrivi_le_uscite(distinta, uscita, tabelle)
    voci = len(distinta.voci)
    print(
        f"Distinta: {voci} voci in {len({v.sezione for v in distinta.voci})} sezioni, "
        f"{len(distinta.tratte_in_tabella)} tratte; regole {distinta.regole.impronta}."
    )
    for percorso in scritti:
        print(f"  {percorso}")
    if tabelle != TABELLE_DEL_FOGLIO:
        print(f"Sul foglio: {', '.join(tabelle)}; il resto e' nell'Excel.")
    if not ha_openpyxl():
        print(
            "Manca la libreria openpyxl: al posto dell'Excel c'e' distinta.csv (stesse voci, solo valori).",
            file=sys.stderr,
        )
    oltre = [e for e in distinta.verifica if e.esito == "oltre"]
    if oltre:
        print(f"Verifica — {len(oltre)} segnalazioni (la distinta non corregge):")
        for esito in oltre:
            print(f"  - {esito.dove}, {esito.controllo}: {esito.valore}, contro {esito.soglia}")
    gia_detti = {f"{e.dove}, {e.controllo}: {e.valore}, contro {e.soglia}." for e in oltre}
    avvisi = [a for a in distinta.avvisi if a not in gia_detti]
    if avvisi:
        print("Avvisi:")
        for avviso in avvisi:
            print(f"  - {avviso}")
    if distinta.da_confermare:
        print("Da confermare col progettista (poi --fornitura confermata, o le scelte sue):")
        for riga in distinta.da_confermare:
            print(f"  - {riga}")
    domande = distinta.domande
    if domande:
        print(f"DA DEFINIRE — {len(distinta.da_definire)} voci; le domande al progettista:")
        for domanda in domande:
            print(f"  - {domanda}")
        return 2
    print("Nessuna voce DA DEFINIRE.")
    return 0
