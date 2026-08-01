# HANDOFF — Disegnatore MEP · 2026-08-01 (fine P0)

> ⛔ **STOP. Questo file NON è un riassunto del progetto.** È il cancello
> di lettura per la sessione successiva. Leggere tutti i documenti indicati
> nell'ordine sotto prima di modificare file, scrivere codice o porre domande
> al PM. Solo dopo completare le sentinel checks del §2.

---

## 1. Reading order obbligatorio

Leggere integralmente nell'ordine. I gruppi di file vanno letti al completo.

| # | File | Funzione |
|---|---|---|
| 1 | `AGENTS.md` | Regole operative e profilo di collaborazione con il PM |
| 2 | `CONTESTO_PROGETTO.md` | Storia completa e punto di partenza del progetto |
| 3 | `README.md` | Scopo e orientamento del repository |
| 4 | `PRD_DISEGNATORE_MEP.md` | Requisiti di prodotto approvati |
| 5 | `PROJECT_STATE.md` | Stato vivo e prossimo passo |
| 6 | `docs/specs/2026-08-01-disegnatore-mep-design.md` | Design consolidato e approvato |
| 7 | `docs/adr/README.md`, poi `docs/adr/0001-*.md` fino a `0004-*.md` | Decisioni architetturali in ordine cronologico |
| 8 | `docs/DECISION_LOG.md` | Decisioni funzionali D-001–D-033 |
| 9 | `docs/ROADMAP.md` | Fasi del progetto e perimetro futuro |
| 10 | `docs/ARCHITECTURE.md` | Struttura del codice effettivamente consegnato in P0 |
| 11 | **`docs/P0_REVIEW_FINDINGS.md`** | Cosa le revisioni hanno trovato e non è stato risolto. **Contiene le due decisioni aperte per il PM** |
| 12 | `docs/plans/README.md` e `docs/plans/2026-08-01-master-implementation-roadmap.md` | Sequenza P0–P7 |
| 13 | `docs/plans/2026-08-01-foundation-core-plan.md` — **almeno l'appendice finale** | Il piano eseguito e le deviazioni approvate. Il corpo del piano contiene codice che non compila: leggere l'appendice prima di fidarsi del testo |
| 14 | `docs/research/README.md` e `docs/research/SOURCE_REGISTER.md` | Regole per fonti e stato della ricerca |
| 15 | `assets/cartigli/README.md` e `releases/README.md` | Vincoli su cartiglio e rilascio |
| 16 | [`nove-c-kit` PLAYBOOK](https://github.com/danielcarta9c/nove-c-kit/blob/main/PLAYBOOK.md) e [`EXAMPLES`](https://github.com/danielcarta9c/nove-c-kit/blob/main/EXAMPLES.md) | Metodo di project management Nove C |
| 17 | Questo file dal §2 in poi | Verifica di comprensione e delta operativo |

Non usare questo HANDOFF come scorciatoia. Il contenuto tecnico vive nei documenti canonici sopra.

---

## 2. Sentinel checks — verifica che hai letto

Rispondere esplicitamente a queste domande prima di iniziare. Se una risposta non è certa, tornare al §1.

1. Perché il prodotto non è un catalogo di schemi tipo, e come è stato **dimostrato** che il nucleo è davvero universale?
2. Qual è la fonte di verità e quali artefatti sono derivati rigenerabili?
3. Cosa deve essere approvato prima di disegnare, e quale lacuna del modello impedisce oggi di rappresentare quel flusso?
4. Come deve essere rappresentato un componente inserito in linea, e perché quel requisito è oggi rappresentabile ma non verificato?
5. Perché rileggere alla lettera il corpo del piano P0 è pericoloso?
6. Quali sono le due domande aperte che spettano al PM e non all'agente?

Risposte attese: motore compositivo, provato cercando ogni termine impiantistico nel sorgente e trovando solo i sei nomi di dominio, zero condizionali su tipo di componente; il modello tecnico canonico, con geometria, SVG e PDF derivati; l'intero dossier di integrazioni, assunzioni e domande, oggi non rappresentabile perché manca il luogo dove vive una proposta non approvata; la connessione si spezza in due segmenti sulle porte del componente, ma nessuna fixture contiene un componente in linea e `inline_gap_mm` non è letto da nessuna parte; il corpo del piano contiene nove difetti eseguibili corretti solo nell'appendice; le due domande sono la rappresentazione delle proposte non approvate e l'immutabilità del modello.

---

## 3. Stato attuale del progetto

- **Fase:** P0 completata, gate G0 superato. P1 non iniziata.
- **Versione installabile:** nessuna release; `releases/latest/` non è ancora popolata.
- **Codice:** 45 file, 3089 righe, 17 commit. `src/disegnatore_mep/` con `model`, `catalog`, `domains`, `validation`, `io` e `cli`.
- **Verifica:** 59 test verdi; `pytest`, `ruff` e `mypy --strict` tutti a exit `0` su `src`, `tests` e `examples/foundation/build_fixtures.py`.
- **Ambiente:** `.venv` con Python **3.12.13** preso dal runtime Codex (`C:\Users\DanielCarta\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`). Scelta deliberata: Claude e Codex condividono la stessa `.venv` e la stessa toolchain, quindi le sessioni sono intercambiabili senza rifare setup. L'unico altro Python sulla macchina è 3.14.4 e **non** va usato.
- **Ramo:** P0 è stata sviluppata su `feat/p0-foundation-core` e integrata in `main` con un merge esplicito. Si riparte da `main`. Il ramo di lavoro è conservato per poter rileggere la sequenza dei commit.
- **In flight:** nessuna modifica applicativa a metà.
- **Blocco:** nessun blocco tecnico. Il progetto è però in attesa di due decisioni di prodotto, elencate al §6.
- **Check rapido alla ripresa:** `git status --short` vuoto; `& .\.venv\Scripts\python.exe -m pytest -q` deve dare 59 passed.

---

## 4. Cosa è cambiato dall'ultima sessione (delta)

- Eseguiti tutti e otto i task del piano P0, ciascuno con implementatore e almeno due revisioni indipendenti.
- Superato il gate G0: `examples/foundation/valid-mixed-project.json` combina quattro domini ed esce `0`; `invalid-cross-medium.json` esce `2` con `PORT_MEDIUM_MISMATCH`.
- Corretti **nove difetti eseguibili del piano** — codice che funzionava a runtime ma non superava `mypy --strict`, piu' un import circolare reale. Elencati nell'appendice del piano.
- Corretti **quattro difetti trovati dalla revisione avversariale**, fra cui un falso PASS e una falla nell'integrità del fingerprint.
- Prodotti `docs/ARCHITECTURE.md` e `docs/P0_REVIEW_FINDINGS.md`.
- Tutte queste modifiche sono già promosse nei documenti canonici: non ricostruirle da questo elenco.

---

## 5. Punto esatto da cui riprendere

**Non iniziare a scrivere codice.** Il prossimo passo è di pianificazione, e dipende da una decisione del PM.

- **Task:** portare al PM le due domande del §6, poi scrivere il piano P1.
- **Ordine consigliato dopo la decisione:** piano P1 (regole), poi piano P2 (sistema grafico). Sono paralleli dopo P0 secondo la roadmap master, ma P2 puo' partire anche subito perché non dipende dalla decisione sulle proposte.
- **Prima di P3:** allargare il contratto `DomainPack`. Oggi vede solo due porte e una rete, quindi nessuna regola idronica o aeraulica reale è esprimibile. Se i quattro pacchetti P3 partissero in parallelo su questo contratto, ognuno modificherebbe il nucleo per conto proprio.
- **Loci di interesse:** `docs/P0_REVIEW_FINDINGS.md`; `PROJECT_STATE.md`; `docs/plans/2026-08-01-master-implementation-roadmap.md`.

---

## 6. Domande aperte per il PM

Due, entrambe di prodotto, entrambe documentate in `docs/P0_REVIEW_FINDINGS.md` §3.

1. **Dove vive una proposta non ancora approvata.** Oggi il modello ha il vocabolario dell'approvazione ma non il meccanismo: un accessorio proposto dal motore di regole andrebbe scritto nel modello reale, dove il validatore lo tratta già come esistente, e una proposta rifiutata non lascia traccia di cosa fosse. Le opzioni sono uno stato sulle entità con validatore ristretto alle approvate, oppure una collezione separata di proposte. Decide come una revisione rientra nel progetto, quindi non è un dettaglio reversibile. **Va risolta prima che P1 scriva la prima regola**, perché lo schema è fissato a `1.0.0` e oggi non esistono ancora file di progetto reali.
2. **Immutabilità del modello canonico.** Un assegnamento rifiutato lascia comunque il valore scartato nell'istanza, e questo produce un verdetto sbagliato, non solo un oggetto sorprendente. Le opzioni sono congelare il modello oppure far riasserire gli invarianti al validatore.

Alla ripresa non chiedere al PM di ricostruire il contesto, e non chiedergli di scegliere fra modalità tecniche di esecuzione.

---

## 7. Quirks e gotcha emersi

- **Il corpo del piano P0 contiene codice difettoso.** Non è stato riscritto. L'appendice finale è la fonte autorevole sulle differenze.
- **Eseguire sempre la suite completa**, mai il solo file di test del task in corso: l'import circolare corretto nel Task 5 passava indenne sul proprio file e falliva solo sull'intera suite, per ordine di collection.
- **Eseguire `mypy src tests`, non solo `mypy src`.** Gli errori di tipo nei test restano altrimenti invisibili fino al gate finale.
- **Cinque vincoli non vanno "migliorati"**: porte ammesse ovunque dentro il riquadro del simbolo e non solo sul perimetro; `validation/__init__.py` minimale; `BasicDomainPack` congelato; `network_id` dentro la chiave di duplicazione; precedenza dei rami in `validate_pair`. Motivazioni nell'appendice del piano.
- **OneDrive:** il repository è in una cartella sincronizzata; evitare modifiche contemporanee da due computer e verificare lo stato Git prima di intervenire.
- **Cartiglio PDF:** le anomalie di font osservate restano descritte nella specifica approvata; consultarla prima di costruire il rendering.
- **Quota dell'app:** non esiste un indicatore interrogabile del limite residuo; non inventare stime.

---

## 8. Cross-refs — dove vivono le cose

| Quando serve sapere… | File del progetto |
|---|---|
| Come collaborare con il PM | `AGENTS.md` |
| Qual è il prodotto e cosa esclude | `PRD_DISEGNATORE_MEP.md` |
| Perché il motore è generale | ADR 0001 e specifica approvata |
| Qual è la fonte di verità | ADR 0002 |
| Come gestire scala e tavole | ADR 0003 |
| Perché si approva prima di disegnare | ADR 0004 |
| Com'è fatto il codice consegnato | `docs/ARCHITECTURE.md` |
| Cosa manca e cosa è stato differito | `docs/P0_REVIEW_FINDINGS.md` |
| Perché il codice diverge dal piano | Appendice di `docs/plans/2026-08-01-foundation-core-plan.md` |
| Qual è il prossimo passo | `PROJECT_STATE.md` |
| Dove trovare le decisioni | `docs/DECISION_LOG.md` e `docs/adr/` |
| Come gestire fonti tecniche | `docs/research/SOURCE_REGISTER.md` |
| Come produrre una release | `releases/README.md` |

---

## Ultimo aggiornamento

`2026-08-01` — Claude — chiusura di P0: gate G0 superato, 59 test verdi, difetti del piano e della revisione avversariale corretti, documentazione allineata al codice reale.
