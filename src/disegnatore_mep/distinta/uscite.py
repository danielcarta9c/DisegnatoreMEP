"""Le uscite della distinta: il JSON, le tabelle per il foglio, il foglio dei calcoli.

- `distinta.json` — tutto: le voci con la regola, la fonte, il perche' e il conto; le
  tratte con la loro lunghezza maggiorata; la verifica; le domande;
- `tabelle-del-foglio.json` — **i dati** delle tabelle che il motore sa posare sulla
  tavola (`disegna --tabelle`), gia' scritti come testo. **Il flusso della skill non le
  posa piu'** (I-233: sulla tavola solo la tabella delle apparecchiature e la legenda);
  il file resta, con la capacita' del motore;
- `distinta-calcoli.md` — il foglio dei calcoli, accanto alla tavola (come per i
  diametri, D-191): ogni numero con il suo conto e la sua regola.

Il documento per l'installatore — la copertina e i capitoli, in PDF coi report Nove C o
in Markdown — e' in `documento` e `impaginazione` (I-232: niente Excel).

**Niente codici interni nel documento e nelle tabelle del foglio** (collaudo REL-012 t1,
§2.4.5-6): i pezzi si dicono con le sigle dello schema, le fonti con le parole di
`fonte_in_parole`. Gli id delle regole restano nel JSON e nel foglio dei calcoli, che
sono la traccia del conto. Dove il cartiglio non ha un dato, l'intestazione dice
«DA DEFINIRE», come il cartiglio della tavola (§2.2.9).
"""

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .calcolo import DA_DEFINIRE, Distinta, Voce
from .lunghezze import in_parole

FORMATO_DELLA_DISTINTA = "disegnatore-mep/distinta"
FORMATO_DELLE_TABELLE = "disegnatore-mep/tabelle-del-foglio"
VERSIONE_DEL_FORMATO = 1

TABELLE_DEL_FOGLIO = ("tratte", "computo", "attivita", "note")
"""Le tabelle che la distinta scrive in `tabelle-del-foglio.json`, nell'ordine in cui le
scrive; `--sul-foglio` ne sceglie alcune. Il flusso della skill non le posa sulla tavola
(I-233): tratte, computo, attivita' e note stanno nel documento della distinta."""


def tabelle_scelte(testo: str | None) -> tuple[str, ...]:
    """Le tabelle dell'opzione `--sul-foglio` («tratte,note»), nell'ordine di sempre.
    Un nome che non c'e' e' un errore che dice quali ci sono."""
    if testo is None:
        return TABELLE_DEL_FOGLIO
    scelte = [parte.strip().replace("à", "a") for parte in testo.split(",") if parte.strip()]
    ignote = [s for s in scelte if s not in TABELLE_DEL_FOGLIO]
    if ignote or not scelte:
        raise ValueError(
            f"--sul-foglio: {', '.join(ignote) or 'nessuna tabella'}; le tabelle sono {', '.join(TABELLE_DEL_FOGLIO)}"
        )
    return tuple(nome for nome in TABELLE_DEL_FOGLIO if nome in scelte)


def dato_o_da_definire(progetto: Mapping[str, Any], chiave: str) -> str:
    """Un campo del cartiglio, o «DA DEFINIRE» come lo scrive la tavola (§2.2.9)."""
    valore = progetto.get(chiave)
    return str(valore) if valore else DA_DEFINIRE


def data_del_cartiglio(progetto: Mapping[str, Any]) -> str:
    """La data come la scrive il cartiglio: 29.10.2026."""
    valore = str(progetto.get("issue_date") or "")
    parti = valore.split("-")
    if len(parti) == 3 and all(p.isdigit() for p in parti):
        return f"{parti[2]}.{parti[1]}.{parti[0]}"
    return valore or DA_DEFINIRE

PER_IL_FOGLIO = (("≥ ", "min. "), ("≤ ", "max. "), ("≥", "min."), ("≤", "max."), ("→", "-"))
"""Il writer PDF del motore e' WinAnsi: «≥», «≤», «→» diventerebbero «?» (kit AA-01,
RAPPORTO §6 punto 5). Sul foglio si scrivono come li scriveva il kit."""


def _q(valore: float | None) -> int | float | None:
    if valore is None:
        return None
    return int(valore) if float(valore).is_integer() else round(valore, 3)


def per_il_foglio(testo: str) -> str:
    for prima, dopo in PER_IL_FOGLIO:
        testo = testo.replace(prima, dopo)
    return testo


def _voce_in_json(voce: Voce) -> dict[str, Any]:
    return {
        "rif": voce.rif,
        "testo": voce.testo,
        "um": voce.um,
        "quantita": _q(voce.quantita),
        "fornitura": voce.fornitura,
        "note": voce.note,
        "da_definire": voce.da_definire,
        "domande": list(voce.domande),
        "regola": voce.regola,
        "calcolo": voce.calcolo,
        "fonte": voce.fonte,
        "perche": voce.perche,
    }


def distinta_in_json(distinta: Distinta) -> dict[str, Any]:
    regole = distinta.regole
    sezioni = []
    for lettera in regole.lettere:
        voci = distinta.voci_della_sezione(lettera)
        if lettera == "H":
            sezioni.append(
                {"lettera": "H", "titolo": regole.titolo("H"), "righe_vuote": int(regole.distinta.get("righe_h", 6)), "voci": []}
            )
        elif voci:
            sezioni.append({"lettera": lettera, "titolo": regole.titolo(lettera), "voci": [_voce_in_json(v) for v in voci]})
    return {
        "formato": FORMATO_DELLA_DISTINTA,
        "versione": VERSIONE_DEL_FORMATO,
        "stato": regole.distinta.get("stato", ""),
        "progetto": dict(distinta.progetto),
        "regole": {"versioni": dict(regole.versioni), "impronta": regole.impronta},
        "intestazione": list(regole.distinta.get("intestazione", [])),
        "sezioni": sezioni,
        "tratte": [
            {
                "num": t.num,
                "rete": t.rete.nome,
                "fluido": t.fluido,
                "da_a": distinta.da_a(t),
                "tubazioni": [tubazione.id for tubazione in t.tubazioni],
                "sezione": t.sezione,
                "materiale": distinta.materiale(t) or None,
                "portata_m3h": _q(t.dato("portata_m3h") if isinstance(t.dato("portata_m3h"), int | float) else None),
                "lunghezza_stimata_m": _q(t.lunghezza_m),
                "lunghezza_da_quotare_m": _q(t.da_quotare_m),
                "calcolo": t.calcolo_della_lunghezza,
                "raccordo_diretto": t.diretta,
            }
            for t in distinta.tratte_in_tabella
        ],
        "verifica": [
            {
                "dove": e.dove,
                "controllo": e.controllo,
                "valore": e.valore,
                "soglia": e.soglia,
                "esito": e.esito,
                "fonte": e.fonte,
            }
            for e in distinta.verifica
        ],
        "note": list(distinta.note),
        "avvisi": list(distinta.avvisi),
        "domande": distinta.domande,
        "da_confermare": list(distinta.da_confermare),
    }


# --- le tabelle per il foglio ----------------------------------------------------


def _colonne(*colonne: tuple[str, str, str, float]) -> list[dict[str, Any]]:
    return [{"id": i, "titolo": t, "allinea": a, "peso": p} for i, t, a, p in colonne]


def numero_o_vuoto(valore: float | None, cifre: int = 2) -> str:
    return "" if valore is None else in_parole(valore, cifre)


def _velocita(distinta: Distinta, num: str) -> str:
    for esito in distinta.verifica:
        if esito.dove == num and esito.misura is not None:
            return in_parole(esito.misura, 1)
    return ""


def tabelle_del_foglio(distinta: Distinta, sul_foglio: Sequence[str] = TABELLE_DEL_FOGLIO) -> dict[str, Any]:
    """I dati delle tabelle per la tavola, come le disegnava il kit AA-01 sulla M.02.

    Forma: `{"formato", "versione", "tabelle": [tabella, ...]}`; ogni tabella e'
    `{"id", "titolo", "colonne": [{"id", "titolo", "allinea": "sinistra"|"destra",
    "peso"}], "sezioni": [{"titolo": testo o null, "righe": [[cella, ...], ...]}]}`.
    Le celle sono testo gia' scritto (virgola decimale, niente «≥»: il writer PDF e'
    WinAnsi); `peso` e' la larghezza relativa della colonna. Le tabelle sono al piu'
    quattro: `tratte`, `computo` (le sezioni del foglio, da `sezioni_sul_foglio`),
    `attivita` (G), `note`; `sul_foglio` dice quali (`--sul-foglio`)."""
    regole = distinta.regole
    tratte = {
        "id": "tratte",
        "titolo": "TABELLA DELLE TRATTE — diametri e lunghezze per la quotazione",
        "colonne": _colonne(
            ("tratto", "Tratto", "sinistra", 0.6),
            ("da_a", "Da - a", "sinistra", 2.4),
            ("sezione", "Ø / sezione", "sinistra", 1.4),
            ("materiale", "Materiale", "sinistra", 1.9),
            ("portata", "Q m³/h", "destra", 0.6),
            ("velocita", "v m/s", "destra", 0.5),
            ("l_stimata", "L stim. m", "destra", 0.6),
            ("l_quotare", "L quot. m", "destra", 0.6),
        ),
        "sezioni": [
            {
                "titolo": None,
                "righe": [
                    [
                        t.num,
                        distinta.da_a(t),
                        t.sezione or "-",
                        per_il_foglio(distinta.materiale(t)),
                        numero_o_vuoto(t.dato("portata_m3h") if isinstance(t.dato("portata_m3h"), int | float) else None),
                        _velocita(distinta, t.num),
                        "" if t.diretta else numero_o_vuoto(t.lunghezza_m),
                        "" if t.diretta else (numero_o_vuoto(t.da_quotare_m) or DA_DEFINIRE),
                    ]
                    for t in distinta.tratte_in_tabella
                ],
            }
        ],
    }
    sezioni_del_foglio = [str(lettera) for lettera in regole.distinta.get("sezioni_sul_foglio", [])]
    computo = {
        "id": "computo",
        "titolo": "COMPUTO DELLE QUANTITÀ E DEI PEZZI SPECIALI — quantità indicative per il prezzo a corpo, da "
        "verificare in sopralluogo (varianti e voci aggiunte: documento della distinta)",
        "colonne": _colonne(
            ("rif", "Rif.", "sinistra", 0.5),
            ("voce", "Voce", "sinistra", 6.0),
            ("um", "UM", "sinistra", 0.7),
            ("quantita", "Q.tà", "destra", 0.6),
            ("fornitura", "Fornitura", "sinistra", 1.0),
            ("note", "Note", "sinistra", 2.6),
        ),
        "sezioni": [
            {
                "titolo": f"{lettera}. {regole.titolo(lettera)}",
                "righe": [
                    [
                        v.rif,
                        per_il_foglio(v.testo),
                        v.um,
                        numero_o_vuoto(v.quantita) or DA_DEFINIRE,
                        v.fornitura,
                        per_il_foglio(v.note),
                    ]
                    for v in distinta.voci_della_sezione(lettera)
                ],
            }
            for lettera in sezioni_del_foglio
            if distinta.voci_della_sezione(lettera)
        ],
    }
    attivita = {
        "id": "attivita",
        "titolo": f"G. {regole.titolo('G').upper()}",
        "colonne": _colonne(("rif", "Rif.", "sinistra", 0.5), ("voce", "Attività", "sinistra", 9.5)),
        "sezioni": [{"titolo": None, "righe": [[v.rif, per_il_foglio(v.testo)] for v in distinta.voci_della_sezione("G")]}],
    }
    note = {
        "id": "note",
        "titolo": "NOTE DELLA DISTINTA",
        "colonne": _colonne(("n", "", "destra", 0.3), ("nota", "", "sinistra", 9.7)),
        "sezioni": [{"titolo": None, "righe": [[f"{i}.", per_il_foglio(n)] for i, n in enumerate(distinta.note, start=1)]}],
    }
    return {
        "formato": FORMATO_DELLE_TABELLE,
        "versione": VERSIONE_DEL_FORMATO,
        "tabelle": [t for t in (tratte, computo, attivita, note) if t["id"] in sul_foglio],
    }


# --- il foglio dei calcoli -------------------------------------------------------


def foglio_dei_calcoli(distinta: Distinta) -> str:
    progetto = distinta.progetto
    righe = [
        f"# Distinta materiali — foglio dei calcoli ({dato_o_da_definire(progetto, 'commission_code')}, tavola "
        f"{dato_o_da_definire(progetto, 'sheet_number')} rev. {dato_o_da_definire(progetto, 'revision')})",
        "",
        f"Committente: {dato_o_da_definire(progetto, 'client')} · Progetto: "
        f"{dato_o_da_definire(progetto, 'project_name')} · Data: {data_del_cartiglio(progetto)}",
        "",
        f"> {distinta.regole.distinta.get('stato', '')}. Regole `{distinta.regole.impronta}` "
        f"({', '.join(f'{n} {v}' for n, v in distinta.regole.versioni.items())}).",
        "",
    ]
    if distinta.domande:
        righe += ["## DA DEFINIRE — le domande al progettista", ""]
        righe += [f"- {d}" for d in distinta.domande]
        righe.append("")
    if distinta.da_confermare:
        righe += ["## Da confermare per questa offerta", ""]
        righe += [f"- {c}" for c in distinta.da_confermare]
        righe.append("")
    righe += [
        "## Le tratte",
        "",
        "| tratto | rete | da - a | sezione | L stimata | L da quotare | conto |",
        "|---|---|---|---|---|---|---|",
    ]
    for t in distinta.tratte_in_tabella:
        righe.append(
            f"| {t.num} | {t.rete.nome} | {distinta.da_a(t)} | {t.sezione or '—'} | "
            f"{'' if t.diretta else numero_o_vuoto(t.lunghezza_m)} | "
            f"{'' if t.diretta else (numero_o_vuoto(t.da_quotare_m) or DA_DEFINIRE)} | "
            f"{'raccordo diretto' if t.diretta else t.calcolo_della_lunghezza} |"
        )
    righe += ["", "## La verifica (segnala, non corregge)", "", "| dove | controllo | valore | soglia | esito |", "|---|---|---|---|---|"]
    righe += [f"| {e.dove} | {e.controllo} | {e.valore} | {e.soglia} | {e.esito} |" for e in distinta.verifica]
    righe += ["", "## Le voci, con la regola e il conto", "", "| rif | voce | q.tà | um | conto | regola |", "|---|---|---|---|---|---|"]
    for voce in distinta.voci:
        quantita = _q(voce.quantita)
        mostrata = "" if quantita is None and voce.sezione == "V" else (DA_DEFINIRE if quantita is None else in_parole(float(quantita)))
        righe.append(
            f"| {voce.rif} | {voce.testo.replace('|', '/')} | {mostrata} | {voce.um} | "
            f"{voce.calcolo.replace('|', '/')} | `{voce.regola}` |"
        )
    if distinta.avvisi:
        righe += ["", "## Avvisi", ""]
        righe += [f"- {a}" for a in distinta.avvisi]
    righe += ["", "## Note", ""]
    righe += [f"{i}. {n}" for i, n in enumerate(distinta.note, start=1)]
    return "\n".join(righe) + "\n"


def _json(dati: Mapping[str, Any]) -> str:
    return json.dumps(dati, ensure_ascii=False, indent=1) + "\n"


def scrivi_le_uscite(
    distinta: Distinta, cartella: Path, sul_foglio: Sequence[str] = TABELLE_DEL_FOGLIO
) -> list[Path]:
    """Scrive il JSON, le tabelle del foglio e il foglio dei calcoli nella cartella, e li
    restituisce nell'ordine in cui li scrive. `sul_foglio` sono le tabelle di
    `tabelle-del-foglio.json` (`--sul-foglio`). Il documento per l'installatore lo scrive
    `impaginazione.scrivi_il_documento`."""
    cartella.mkdir(parents=True, exist_ok=True)
    scritti = []
    for nome, testo in (
        ("distinta.json", _json(distinta_in_json(distinta))),
        ("tabelle-del-foglio.json", _json(tabelle_del_foglio(distinta, sul_foglio))),
        ("distinta-calcoli.md", foglio_dei_calcoli(distinta)),
    ):
        (cartella / nome).write_text(testo, encoding="utf-8")
        scritti.append(cartella / nome)
    return scritti
