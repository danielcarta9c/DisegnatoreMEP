"""Le uscite della distinta: il JSON, le tabelle per il foglio, l'Excel, il foglio dei calcoli.

- `distinta.json` — tutto: le voci con la regola, la fonte, il perche' e il conto; le
  tratte con la loro lunghezza maggiorata; la verifica; le domande;
- `tabelle-del-foglio.json` — **i dati** delle tabelle da disegnare sulla tavola
  (tratte, computo, attivita', note), gia' scritti come testo: chi disegna non conta
  niente. La forma e' in `tabelle_del_foglio`;
- `distinta.xlsx` — per l'installatore: **solo valori, nessuna formula**, prezzo a
  corpo, sopralluogo obbligatorio, sezione H vuota, varianti V. Senza openpyxl
  nell'ambiente, `distinta.csv` al suo posto, e il comando lo dice;
- `distinta-calcoli.md` — il foglio dei calcoli, accanto alla tavola (come per i
  diametri, D-191): ogni numero con il suo conto e la sua regola.

**Niente codici interni nell'Excel e nelle tabelle del foglio** (collaudo REL-012 t1,
§2.4.5-6): i pezzi si dicono con le sigle dello schema, le fonti con le parole di
`fonte_in_parole`. Gli id delle regole restano nel JSON e nel foglio dei calcoli, che
sono la traccia del conto. Dove il cartiglio non ha un dato, l'intestazione dice
«DA DEFINIRE», come il cartiglio della tavola (§2.2.9).
"""

import csv
import importlib
import importlib.util
import io
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .calcolo import DA_DEFINIRE, Distinta, Voce
from .lunghezze import in_parole

FORMATO_DELLA_DISTINTA = "disegnatore-mep/distinta"
FORMATO_DELLE_TABELLE = "disegnatore-mep/tabelle-del-foglio"
VERSIONE_DEL_FORMATO = 1

LETTERE_DI_ATTIVITA = ("G", "H", "V")

TABELLE_DEL_FOGLIO = ("tratte", "computo", "attivita", "note")
"""Le tabelle che la distinta scrive per il foglio, nell'ordine in cui le scrive. Il
computo intero porta di solito la tavola in A1: con `--sul-foglio tratte,note` il
foglio porta solo tratte e note, e il computo resta nell'Excel."""


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
                "materiale": t.dato("materiale") or distinta.regole.fluidi.get(t.fluido, {}).get("materiale"),
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


def _numero_o_vuoto(valore: float | None, cifre: int = 2) -> str:
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
                        per_il_foglio(str(t.dato("materiale") or regole.fluidi.get(t.fluido, {}).get("materiale") or "")),
                        _numero_o_vuoto(t.dato("portata_m3h") if isinstance(t.dato("portata_m3h"), int | float) else None),
                        _velocita(distinta, t.num),
                        "" if t.diretta else _numero_o_vuoto(t.lunghezza_m),
                        "" if t.diretta else (_numero_o_vuoto(t.da_quotare_m) or DA_DEFINIRE),
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
        "verificare in sopralluogo (varianti e voci aggiunte: file Excel)",
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
                        _numero_o_vuoto(v.quantita) or DA_DEFINIRE,
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


# --- l'Excel ---------------------------------------------------------------------


def ha_openpyxl() -> bool:
    return importlib.util.find_spec("openpyxl") is not None


def _cella(foglio: Any, riga: int, colonna: int, valore: Any) -> Any:
    """Una cella con un valore, mai una formula: un testo che comincia con «=»
    openpyxl lo prenderebbe per formula, e qui resta testo."""
    cella = foglio.cell(riga, colonna, valore)
    if isinstance(valore, str) and valore.startswith("="):
        cella.data_type = "s"
    return cella


def scrivi_excel(distinta: Distinta, percorso: Path) -> None:
    openpyxl = importlib.import_module("openpyxl")
    stili = importlib.import_module("openpyxl.styles")
    utili = importlib.import_module("openpyxl.utils")
    Font, PatternFill, Side, Border, Alignment = (
        stili.Font,
        stili.PatternFill,
        stili.Side,
        stili.Border,
        stili.Alignment,
    )
    carattere = "Arial"
    normale = Font(name=carattere, size=9)
    grassetto = Font(name=carattere, size=9, bold=True)
    titolo = Font(name=carattere, size=12, bold=True, color="1C2E4A")
    sottotitolo = Font(name=carattere, size=9, italic=True, color="555555")
    avviso = Font(name=carattere, size=9, bold=True, color="0000FF")
    da_compilare = Font(name=carattere, size=9, color="0000FF")
    testata = Font(name=carattere, size=9, bold=True, color="FFFFFF")
    grigio = Font(name=carattere, size=8, italic=True, color="7F7F7F")
    rosso = Font(name=carattere, size=9, bold=True, color="C00000")
    sfondo_testata = PatternFill("solid", fgColor="1C2E4A")
    sfondo_gruppo = PatternFill("solid", fgColor="E6E9EF")
    giallo = PatternFill("solid", fgColor="FFFF00")
    sfondo_grigio = PatternFill("solid", fgColor="F2F2F2")
    arancio = PatternFill("solid", fgColor="FCE4D6")
    filo = Side(style="thin", color="BFBFBF")
    riquadro = Border(left=filo, right=filo, top=filo, bottom=filo)
    a_capo = Alignment(wrap_text=True, vertical="top")
    euro = '#,##0.00 "€"'
    regole = distinta.regole
    progetto = distinta.progetto
    installatore = str(regole.distinta.get("fornitura_installatore", "installatore"))

    libro = openpyxl.Workbook()
    foglio = libro.active
    foglio.title = "Computo"
    foglio.sheet_view.showGridLines = False
    intestazione = [
        (
            f"{dato_o_da_definire(progetto, 'commission_code')} — {dato_o_da_definire(progetto, 'project_name')} — "
            "Distinta materiali per l'installatore",
            titolo,
        ),
        (
            f"Committente: {dato_o_da_definire(progetto, 'client')}. Indirizzo: "
            f"{dato_o_da_definire(progetto, 'address')}. Allegata alla tavola "
            f"{dato_o_da_definire(progetto, 'sheet_number')}, rev. {dato_o_da_definire(progetto, 'revision')} del "
            f"{data_del_cartiglio(progetto)}. Regole della distinta {regole.impronta}. Quantità indicative.",
            sottotitolo,
        ),
        *((riga, avviso) for riga in regole.distinta.get("intestazione", [])),
    ]
    for indice, (testo, carattere_della_riga) in enumerate(intestazione, start=1):
        _cella(foglio, indice, 1, testo).font = carattere_della_riga
        foglio.merge_cells(start_row=indice, start_column=1, end_row=indice, end_column=8)
        foglio.cell(indice, 1).alignment = a_capo
        if indice > 2:
            foglio.row_dimensions[indice].height = 28
    colonne = [
        ("Rif.", 7),
        ("Voce", 72),
        ("UM", 9),
        ("Q.tà", 11),
        ("Fornitura", 13),
        ("Note", 40),
        ("Prezzo unitario €", 14),
        ("Importo €", 14),
    ]
    prima = len(intestazione) + 2
    for colonna, (nome, larghezza) in enumerate(colonne, start=1):
        cella = _cella(foglio, prima, colonna, nome)
        cella.font, cella.fill, cella.border = testata, sfondo_testata, riquadro
        cella.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        foglio.column_dimensions[utili.get_column_letter(colonna)].width = larghezza
    riga = prima + 1

    def gruppo(testo: str) -> None:
        nonlocal riga
        _cella(foglio, riga, 1, testo).font = grassetto
        foglio.merge_cells(start_row=riga, start_column=1, end_row=riga, end_column=8)
        for colonna in range(1, 9):
            foglio.cell(riga, colonna).border = riquadro
            foglio.cell(riga, colonna).fill = sfondo_gruppo
        riga += 1

    def scrivi(valori: Sequence[Any], modo: str, motivo: str = "") -> None:
        """`modo`: «quota» (prezzo unitario e importo), «corpo» (solo importo),
        «variante» (solo prezzo unitario), «no» (non si quota)."""
        nonlocal riga
        for colonna, valore in enumerate(valori, start=1):
            cella = _cella(foglio, riga, colonna, valore)
            cella.font, cella.border, cella.alignment = normale, riquadro, a_capo
        foglio.cell(riga, 4).alignment = Alignment(horizontal="right", vertical="top")
        if valori[3] == DA_DEFINIRE:
            foglio.cell(riga, 4).font, foglio.cell(riga, 4).fill = rosso, arancio
        unitario, importo = foglio.cell(riga, 7), foglio.cell(riga, 8)
        unitario.border = importo.border = riquadro
        unitario.number_format = importo.number_format = euro
        if modo == "no":
            unitario.fill = importo.fill = sfondo_grigio
            importo.value, importo.font = motivo, grigio
        elif modo == "corpo":
            unitario.fill = sfondo_grigio
            importo.fill, importo.font = giallo, da_compilare
        elif modo == "variante":
            unitario.fill, unitario.font = giallo, da_compilare
            importo.fill = sfondo_grigio
            importo.value, importo.font = "variante, fuori totale", grigio
        else:
            unitario.fill, unitario.font = giallo, da_compilare
            importo.fill, importo.font = giallo, da_compilare
        riga += 1

    def quantita(voce: Voce) -> Any:
        if voce.quantita is None:
            return "" if voce.sezione == "V" else DA_DEFINIRE
        return _q(voce.quantita)

    for lettera in regole.lettere:
        if lettera in LETTERE_DI_ATTIVITA:
            continue
        voci = distinta.voci_della_sezione(lettera)
        if not voci:
            continue
        gruppo(f"{lettera}. {regole.titolo(lettera)}")
        for voce in voci:
            valori = [voce.rif, voce.testo, voce.um, quantita(voce), voce.fornitura, voce.note]
            if voce.fornitura == installatore:
                scrivi(valori, "quota")
            elif voce.fornitura == DA_DEFINIRE:
                scrivi(valori, "no", "da definire")
            elif voce.fornitura == "committente":
                scrivi(valori, "no", "escluso")
            else:
                scrivi(valori, "no", f"fornitura {voce.fornitura}")
    gruppo(f"G. {regole.titolo('G')}")
    for voce in distinta.voci_della_sezione("G"):
        scrivi([voce.rif, voce.testo, voce.um, quantita(voce), voce.fornitura, voce.note], "corpo")
    gruppo(f"H. {regole.titolo('H')}")
    for indice in range(1, int(regole.distinta.get("righe_h", 6)) + 1):
        scrivi([f"H.{indice}", "", "", "", installatore, ""], "quota")
    riga += 1
    _cella(foglio, riga, 6, "TOTALE A CORPO, oltre IVA (somma degli importi B-H)").font = grassetto
    foglio.cell(riga, 6).alignment = Alignment(horizontal="right", wrap_text=True)
    totale = foglio.cell(riga, 8)
    totale.fill, totale.border, totale.number_format = giallo, riquadro, euro
    totale.font = Font(name=carattere, size=9, bold=True, color="0000FF")
    riga += 2
    gruppo(f"V. {regole.titolo('V')}")
    for voce in distinta.voci_della_sezione("V"):
        scrivi([voce.rif, voce.testo, voce.um, quantita(voce), voce.fornitura, voce.note], "variante")
    riga += 1
    _cella(foglio, riga, 1, str(regole.distinta.get("chiusura", ""))).font = grassetto
    foglio.merge_cells(start_row=riga, start_column=1, end_row=riga, end_column=8)
    riga += 1
    for colonna in range(1, 9):
        foglio.cell(riga, colonna).border = riquadro
        foglio.cell(riga, colonna).fill = giallo
    foglio.merge_cells(start_row=riga, start_column=1, end_row=riga, end_column=8)
    foglio.row_dimensions[riga].height = 40
    foglio.freeze_panes = foglio.cell(prima + 1, 1)
    foglio.print_title_rows = f"{prima}:{prima}"
    foglio.page_setup.orientation = "landscape"
    foglio.page_setup.fitToWidth = 1
    foglio.page_setup.fitToHeight = 0
    foglio.sheet_properties.pageSetUpPr.fitToPage = True

    def tabella(nome: str, testo_del_titolo: str, testate: Sequence[tuple[str, int]], righe: Sequence[Sequence[Any]]) -> None:
        altro = libro.create_sheet(nome)
        altro.sheet_view.showGridLines = False
        _cella(altro, 1, 1, testo_del_titolo).font = titolo
        for colonna, (nome_della_colonna, larghezza) in enumerate(testate, start=1):
            cella = _cella(altro, 3, colonna, nome_della_colonna)
            cella.font, cella.fill, cella.border = testata, sfondo_testata, riquadro
            cella.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            altro.column_dimensions[utili.get_column_letter(colonna)].width = larghezza
        for indice, valori in enumerate(righe, start=4):
            for colonna, valore in enumerate(valori, start=1):
                cella = _cella(altro, indice, colonna, valore)
                cella.font, cella.border, cella.alignment = normale, riquadro, a_capo
        altro.freeze_panes = "A4"

    tabella(
        "Tratte",
        "Tabella delle tratte — sezioni e lunghezze per la quotazione",
        [("Tratto", 8), ("Rete", 24), ("Da - a", 26), ("Ø / sezione / cavo", 18), ("Materiale", 30),
         ("Portata m³/h", 11), ("Velocità m/s", 11), ("L stimata m", 11), ("L da quotare m", 13), ("Conto", 50)],
        [
            [
                t.num,
                t.rete.nome,
                distinta.da_a(t),
                t.sezione or "",
                str(t.dato("materiale") or regole.fluidi.get(t.fluido, {}).get("materiale") or ""),
                _q(t.dato("portata_m3h")) if isinstance(t.dato("portata_m3h"), int | float) else None,
                float(_velocita(distinta, t.num).replace(",", ".")) if _velocita(distinta, t.num) else None,
                None if t.diretta else _q(t.lunghezza_m),
                None if t.diretta else (_q(t.da_quotare_m) if t.da_quotare_m is not None else DA_DEFINIRE),
                "raccordo diretto" if t.diretta else t.calcolo_della_lunghezza,
            ]
            for t in distinta.tratte_in_tabella
        ],
    )
    tabella(
        "Verifica",
        "Verifica dell'aria e delle linee — segnala, non corregge",
        [("Dove", 10), ("Controllo", 28), ("Valore", 40), ("Soglia", 26), ("Esito", 16), ("Fonte", 70)],
        [[e.dove, e.controllo, e.valore, e.soglia, e.esito, e.fonte] for e in distinta.verifica],
    )
    tabella(
        "Regole",
        "Da dove viene ogni quantità — la voce, il conto, la fonte, il perché",
        [("Rif.", 7), ("Voce", 40), ("Conto", 60), ("Fonte", 40), ("Perché", 70)],
        [[v.rif, v.testo, v.calcolo, v.fonte, v.perche] for v in distinta.voci],
    )
    tabella(
        "Note e domande",
        "Note, cose da confermare, domande al progettista e avvisi",
        [("", 14), ("", 130)],
        [
            *(["Nota", n] for n in distinta.note if n not in distinta.da_confermare),
            *(["Da confermare", c] for c in distinta.da_confermare),
            *(["DA DEFINIRE", d] for d in distinta.domande),
            *(["Avviso", a] for a in distinta.avvisi),
        ],
    )
    libro.save(percorso)


def scrivi_csv(distinta: Distinta, percorso: Path) -> None:
    """Il computo in CSV (separatore «;», come lo apre un Excel italiano): solo se
    l'ambiente non ha openpyxl."""
    uscita = io.StringIO()
    scrittore = csv.writer(uscita, delimiter=";", lineterminator="\n")
    scrittore.writerow(["Rif.", "Voce", "UM", "Q.tà", "Fornitura", "Note", "Conto", "Fonte"])
    for intestazione in distinta.regole.distinta.get("intestazione", []):
        scrittore.writerow(["", intestazione])
    for voce in distinta.voci:
        quantita = _q(voce.quantita)
        scrittore.writerow(
            [
                voce.rif,
                voce.testo,
                voce.um,
                "" if quantita is None and voce.sezione == "V" else (DA_DEFINIRE if quantita is None else str(quantita).replace(".", ",")),
                voce.fornitura,
                voce.note,
                voce.calcolo,
                voce.fonte,
            ]
        )
    for indice in range(1, int(distinta.regole.distinta.get("righe_h", 6)) + 1):
        scrittore.writerow([f"H.{indice}", "", "", "", distinta.regole.distinta.get("fornitura_installatore", ""), "", "", ""])
    percorso.write_text(uscita.getvalue(), encoding="utf-8-sig")


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
            f"{'' if t.diretta else _numero_o_vuoto(t.lunghezza_m)} | "
            f"{'' if t.diretta else (_numero_o_vuoto(t.da_quotare_m) or DA_DEFINIRE)} | "
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
    """Scrive le uscite nella cartella, e le restituisce nell'ordine in cui le scrive.
    `sul_foglio` sono le tabelle di `tabelle-del-foglio.json` (`--sul-foglio`)."""
    cartella.mkdir(parents=True, exist_ok=True)
    scritti = []
    for nome, testo in (
        ("distinta.json", _json(distinta_in_json(distinta))),
        ("tabelle-del-foglio.json", _json(tabelle_del_foglio(distinta, sul_foglio))),
        ("distinta-calcoli.md", foglio_dei_calcoli(distinta)),
    ):
        (cartella / nome).write_text(testo, encoding="utf-8")
        scritti.append(cartella / nome)
    if ha_openpyxl():
        scrivi_excel(distinta, cartella / "distinta.xlsx")
        scritti.append(cartella / "distinta.xlsx")
    else:
        scrivi_csv(distinta, cartella / "distinta.csv")
        scritti.append(cartella / "distinta.csv")
    return scritti
