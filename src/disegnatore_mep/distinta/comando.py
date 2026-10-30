"""`mep.py distinta <grafo-completo.json> --out <cartella>|--domande [--report <skill nove-c-report>]
[--regole <cartella o fascio>] [--fornitura <scelte>|confermata] [--sul-foglio ...]`.

Scrive il **documento per l'installatore** (I-232: niente Excel): in PDF, con la copertina
e l'impaginazione dei report Nove C, se `--report` porta alla skill `nove-c-report`
installata accanto; altrimenti lo stesso contenuto in Markdown, e lo dice. Il nome e'
parlante dal cartiglio (commessa e titolo), o «distinta». Accanto: `distinta.json` (lo
legge la pianta), `distinta-calcoli.md` (ogni numero con il suo conto) e
`tabelle-del-foglio.json`, che il flusso della skill non posa piu' sulla tavola (I-233:
sulla tavola solo apparecchiature e legenda); `--sul-foglio` ne sceglie le tabelle.
`--fornitura` conferma o cambia chi fornisce che cosa in questa offerta; senza, la
distinta usa le scelte predefinite di Nove C e le dichiara da confermare.

Col PDF il comando fa il controllo finale dei report — `fill_report` e `qa_pdf` — e ne
stampa gli avvisi e le pagine in PNG, da guardare una per una.

**Spenta di default** (proposta D-213): la distinta si fa solo con questo comando,
che il progettista chiede. Nessun altro comando la produce, e nessuno cambia per lei.

Con `--domande` (REL-016, D4) il comando non scrive niente: compone la distinta in
memoria e stampa, in parole, i dati che il progettista deve dare perche' nessuna voce
esca DA DEFINIRE — da chiedere al passo 2, nello stesso giro delle domande del disegno.
Le domande vengono dagli stessi punti del calcolo che fanno le voci DA DEFINIRE
(`calcolo.Mancante`); `domande` le dice. Esce con `2` se ci sono domande, `0` se no.

Codici di uscita come gli altri comandi della skill: `0` fatto; `2` fatto, ma ci sono
voci DA DEFINIRE e domande al progettista — la distinta non si consegna
all'installatore finche' non hanno risposta; `1` non si e' potuto fare.
"""

import json
import sys
from pathlib import Path

from .calcolo import Distinta, componi_la_distinta
from .documento import documento_della_distinta
from .domande import domande_in_parole
from .grafo import sigle_dello_schema
from .impaginazione import scrivi_il_documento
from .regole import ErroreDelleRegole, carica_regole, la_fornitura, regole_predefinite
from .uscite import TABELLE_DEL_FOGLIO, scrivi_le_uscite, tabelle_scelte


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


def _componi(
    grafo: Path,
    regole: Path | None,
    cartella_delle_regole: Path,
    cartella_del_catalogo: Path,
    cartella_dei_nomi: Path,
    fornitura: str | None,
) -> Distinta:
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
    return componi_la_distinta(
        dati,
        regole_caricate,
        nomi_del_catalogo(cartella_del_catalogo),
        nomi_dei_fluidi(cartella_dei_nomi),
        sigle_dello_schema(dati, cartella_del_catalogo, cartella_dei_nomi),
        la_fornitura(regole_caricate, fornitura),
    )


def domande(
    grafo: Path,
    regole: Path | None,
    cartella_delle_regole: Path,
    cartella_del_catalogo: Path,
    cartella_dei_nomi: Path,
    fornitura: str | None = None,
) -> int:
    """`--domande`: i dati da chiedere prima del primo lancio, in parole; nessun file."""
    distinta = _componi(grafo, regole, cartella_delle_regole, cartella_del_catalogo, cartella_dei_nomi, fornitura)
    righe, quante = domande_in_parole(distinta)
    for riga in righe:
        print(riga)
    return 2 if quante else 0


def esegui(
    grafo: Path,
    uscita: Path,
    regole: Path | None,
    cartella_delle_regole: Path,
    cartella_del_catalogo: Path,
    cartella_dei_nomi: Path,
    sul_foglio: str | None = None,
    fornitura: str | None = None,
    report: Path | None = None,
) -> int:
    tabelle = tabelle_scelte(sul_foglio)
    distinta = _componi(grafo, regole, cartella_delle_regole, cartella_del_catalogo, cartella_dei_nomi, fornitura)
    scritti = scrivi_le_uscite(distinta, uscita, tabelle)
    documento, esito, perche = scrivi_il_documento(documento_della_distinta(distinta), uscita, report)
    print(
        f"Distinta: {len(distinta.voci)} voci in {len({v.sezione for v in distinta.voci})} sezioni, "
        f"{len(distinta.tratte_in_tabella)} tratte; regole {distinta.regole.impronta}."
    )
    for percorso in [documento, *scritti]:
        print(f"  {percorso}")
    if perche:
        print(
            f"Il PDF della distinta non c'e': {perche}. Il documento e' in Markdown, {documento.name}, "
            "con lo stesso contenuto.",
            file=sys.stderr,
        )
    if esito is not None:
        print(f"Il PDF coi report Nove C: {len(esito.pagine)} pagine, da guardare una per una:")
        for pagina in esito.pagine:
            print(f"  {pagina}")
        if esito.avvisi:
            print(f"Il controllo dei report — {len(esito.avvisi)} avvisi (si correggono, o si verificano a vista e si dicono):")
            for avviso in esito.avvisi:
                print(f"  - {avviso}")
        else:
            print("Il controllo dei report: nessun avviso.")
    if tabelle != TABELLE_DEL_FOGLIO:
        print(f"In tabelle-del-foglio.json: {', '.join(tabelle)}.")
    oltre = [e for e in distinta.verifica if e.esito == "oltre"]
    if oltre:
        print(f"Verifica — {len(oltre)} segnalazioni (la distinta non corregge):")
        for segnalata in oltre:
            print(f"  - {segnalata.dove}, {segnalata.controllo}: {segnalata.valore}, contro {segnalata.soglia}")
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
