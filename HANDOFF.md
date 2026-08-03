# HANDOFF — Disegnatore MEP · 2026-08-03 (fine fase grafica)

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
| 8 | `docs/DECISION_LOG.md` | Decisioni funzionali D-001–D-050 |
| 9 | `docs/ROADMAP.md` | Fasi del progetto e perimetro futuro |
| 10 | `docs/ARCHITECTURE.md` | Struttura del codice effettivamente consegnato |
| 11 | **`docs/GRAPHIC_STANDARD.md`** | **Lo standard grafico.** Grandezze in millimetri, regola perimetro-faccia, divisione fra geometria del simbolo e semantica del catalogo, compositi, rotazioni, come si aggiunge un simbolo, come si stampa il foglio |
| 12 | `docs/P0_REVIEW_FINDINGS.md` | Cosa le revisioni di P0 hanno trovato e non è stato risolto. **Il §3.1 fissa il flusso di lavoro reale della skill**: due revisori indipendenti erano partiti da una lettura sbagliata |
| 13 | `docs/plans/README.md` e `docs/plans/2026-08-01-master-implementation-roadmap.md` | Sequenza dei piani |
| 14 | `docs/plans/2026-08-01-foundation-core-plan.md` — **solo l'appendice finale** | Il piano P0 eseguito e le sue deviazioni. Il corpo contiene codice difettoso |
| 15 | **`docs/plans/2026-08-03-graphic-system-symbol-library-plan.md` — solo l'appendice finale** | Il piano grafico eseguito. **Sedici difetti corretti in esecuzione**, sei del piano e dieci trovati dalle revisioni. Anche qui il corpo non è stato riscritto |
| 16 | `docs/research/README.md` e `docs/research/SOURCE_REGISTER.md` | Regole per fonti e stato della ricerca |
| 17 | `assets/cartigli/README.md` e `releases/README.md` | Vincoli su cartiglio e rilascio |
| 18 | [`nove-c-kit` PLAYBOOK](https://github.com/danielcarta9c/nove-c-kit/blob/main/PLAYBOOK.md) e [`EXAMPLES`](https://github.com/danielcarta9c/nove-c-kit/blob/main/EXAMPLES.md) | Metodo di project management Nove C |
| 19 | Questo file dal §2 in poi | Verifica di comprensione e delta operativo |

Non usare questo HANDOFF come scorciatoia. Il contenuto tecnico vive nei documenti canonici sopra.

---

## 2. Sentinel checks — verifica che hai letto

Rispondere esplicitamente prima di iniziare. Se una risposta non è certa, tornare al §1.

1. Perché il prodotto non è un catalogo di schemi tipo, e come è stato **dimostrato**?
2. Qual è la fonte di verità e quali artefatti sono derivati rigenerabili?
3. Cosa deve essere approvato prima di disegnare, e perché quell'approvazione **non** richiede una macchina di stati dentro il modello?
4. Dove vive oggi la geometria di un componente, dove la sua semantica, e cosa le tiene allineate?
5. Perché una porta di simbolo non può stare al centro del riquadro, e quale vincolo P0 questo ha ritirato?
6. Cosa succede se la libreria dei simboli non entra nel foglio, e perché non viene rimpicciolita?
7. Perché rileggere alla lettera il corpo dei due piani è pericoloso?

Risposte attese: motore compositivo, provato cercando ogni termine impiantistico nel sorgente e trovando solo i nomi di dominio, zero condizionali su tipo di componente, e gate G0 su un progetto a quattro domini; il modello tecnico canonico, con geometria, SVG e PDF derivati; l'intero dossier di interpretazione, integrazioni, assunzioni e domande, confermato dentro la conversazione — se l'ingegnere rifiuta un'integrazione la skill semplicemente non la inserisce; la geometria nel manifesto del simbolo e la semantica nella definizione di catalogo, tenute allineate dalla verifica incrociata sugli identificativi di porta al caricamento (D-043); perché non sarebbe un punto a cui attaccare una tubazione, e ritira deliberatamente «le porte possono stare ovunque dentro il riquadro» (D-044); la generazione fallisce con una diagnostica che dice quanti simboli stanno, su entrambi gli assi, perché la scala di stampa è invariante (D-045); entrambi contengono codice che non funziona, corretto solo nelle rispettive appendici.

---

## 3. Stato attuale del progetto

- **Fase:** fondazione canonica e sistema grafico completati. Layout, instradamento e rendering non iniziati.
- **Versione installabile:** nessuna release; `releases/latest/` non è ancora popolata.
- **Verifica:** 144 test verdi; `pytest`, `ruff` e `mypy --strict` a exit `0` su `src`, `tests` ed `examples`.
- **Libreria:** dodici simboli pubblicati in `assets/symbols/` più otto di fixture in `examples/foundation/symbols/`, entrambe rigenerabili identiche dai rispettivi generatori.
- **Il gate G0 di P0 regge ancora** e il fingerprint del progetto misto non si è mosso: `3347374e8b3f006c6f387c6228e0d9d2b885cbf57e65991937e985af32306573`.
- **Ambiente:** ricostruibile da zero con `bash scripts/setup-env.sh`. **Da eseguire come prima cosa in una sessione cloud**, che riparte sempre da un clone pulito.
- **Ramo:** la fase grafica è stata sviluppata su `claude/graphic-symbol-library-setup-acgoka`.
- **In flight:** nessuna modifica applicativa a metà.
- **Check rapido alla ripresa:** `git status --short` vuoto; `.venv/bin/python -m pytest -q` deve dare 144 passed.

---

## 4. Cosa è cambiato dall'ultima sessione (delta)

- Eseguiti tutti e sette i task del piano grafico con `superpowers:subagent-driven-development`: implementatore fresco per task, revisione di conformità e di qualità, loop di correzione.
- **La geometria si è spostata dal catalogo al simbolo** e le porte stanno sul perimetro. Questo ritira un vincolo P0 esplicito: la motivazione è in `docs/GRAPHIC_STANDARD.md` §3.1.
- Prodotto il primo artefatto guardabile del progetto: un **A3 stampabile** dei simboli a misura reale. Rasterizzato a 10 px/mm la barra di scala misura 100,000 mm esatti.
- Corretti **sedici difetti**: sei nel codice letterale del piano, dieci trovati dalle revisioni. Elencati nell'appendice del piano grafico.
- Tutte queste modifiche sono già promosse nei documenti canonici: non ricostruirle da questo elenco.

---

## 5. Punto esatto da cui riprendere

- **Prossimo passo:** scrivere il piano di layout, instradamento e multi-tavola. È il punto 1 di `Next` in `PROJECT_STATE.md`.
- **Da progettare lì, al primo task:** la vista che unisce semantica e geometria. Il piano grafico la elencava fra i propri contratti come `ResolvedComponent` ma non l'ha costruita, perché non aveva consumatori. Oggi la verifica incrociata dimostra che i due insiemi di porte coincidono e poi **butta via l'accoppiamento**: non esiste modo supportato di passare da un componente alla sua geometria.
- **Da progettare lì, subito dopo:** la **trasformazione di rotazione**. `allowed_rotations_deg` dichiara gli orientamenti tecnicamente ammessi (D-049), ma nulla ruota un simbolo, scambia il riquadro a 90°/270°, ruota una `PortFace` o un lato di `KeepOut`. Se ogni consumatore se la scrive da sé, l'invariante perimetro-faccia diverge subito. Va messa in `symbol.py`, accanto al validatore che la impone.
- **`inline_gap_mm` non è ancora letto da nessuno.** D-027 e la regola non negoziabile di `AGENTS.md` sull'inserimento in linea non hanno ancora codice dietro. L'instradamento deve consumarlo, non riderivarlo.
- **`render_symbol_sheet` è un banco di prova, non la tavola.** Costruisce una griglia uniforme da due costanti di modulo. Non generalizza a una tavola con cartiglio e instradamento: va tenuto come riscontro, non esteso.
- **Attenzione al `keep_out`:** ora è imposto non nullo sulle facce con porta, quindi il layout può fidarsene. Prima non lo era.
- **`usable_height_mm` non è un multiplo del passo di griglia** (277 / 2,5 = 110,8), mentre la larghezza sì. È voluto, i margini seguono ISO 5457. Un layout che assuma entrambi gli assi allineati sbaglia in verticale di 0,8 di passo.

---

## 6. Domande aperte per il PM

**Nessuna.**

Una è stata chiusa in questa sessione: le rotazioni ammesse dichiarano gli orientamenti **tecnicamente** sensati, non quelli geometricamente possibili. Sfiato aria bloccato a `[0]`, vaso di espansione a `[0, 180]` (D-049).

Il PM ha anche registrato un input per la libreria vera: **la dimensione del simbolo comunica il peso del componente** nella tavola — valvole piccole, vasi più grandi, accumuli ancora di più. Le misure attuali (6×6, 8×8, 6×10) sono una convenzione di prova, non uno standard da ereditare (D-050).

Alla ripresa non chiedere al PM di ricostruire il contesto, e non chiedergli di scegliere fra modalità tecniche di esecuzione: il PM valida il prodotto, l'agente è il PM senior dello sviluppo.

---

## 7. Quirks e gotcha emersi

- **Il corpo di entrambi i piani contiene codice difettoso.** Le appendici finali sono le fonti autorevoli sulle differenze.
- **Eseguire sempre la suite completa** e `mypy src tests examples`, mai il solo file di test del task in corso: un import circolare di P0 passava sul proprio file e falliva solo sull'intera suite.
- **Mai `git checkout --` o `git stash` su un file con lavoro non committato.** In questa sessione un implementatore ha cancellato così una correzione appena scritta. Copiare il file da parte e ripristinare da lì.
- **Stampare e leggere i numeri che si riportano.** Un report ha citato valori in virgola mobile che Python non produce, e l'affermazione è caduta alla verifica. Un test costruito su quei numeri non dimostrava nulla.
- **Firma dei commit:** in questo container `commit.gpgsign` è attivo ma la chiave è un file vuoto di un altro utente, quindi i commit escono non firmati. Autore e committer sono corretti. Non risolvibile da dentro la sessione.
- **Quota dell'app:** non esiste un indicatore interrogabile del limite residuo; non inventare stime.

---

## 8. Cross-refs — dove vivono le cose

| Quando serve sapere… | File del progetto |
|---|---|
| Come collaborare con il PM | `AGENTS.md` |
| Qual è il prodotto e cosa esclude | `PRD_DISEGNATORE_MEP.md` |
| Com'è fatto lo standard grafico | `docs/GRAPHIC_STANDARD.md` |
| Com'è fatto il codice consegnato | `docs/ARCHITECTURE.md` |
| Perché il codice diverge dai piani | Le appendici dei due piani in `docs/plans/` |
| Qual è il prossimo passo e il debito noto | `PROJECT_STATE.md` |
| Dove trovare le decisioni | `docs/DECISION_LOG.md` e `docs/adr/` |
| Come gestire fonti tecniche | `docs/research/SOURCE_REGISTER.md` |
| Come produrre una release | `releases/README.md` |

---

## Ultimo aggiornamento

`2026-08-03` — Claude — eseguito il piano del sistema grafico e della libreria dei simboli. Sette task, sedici difetti corretti, 144 test verdi, primo A3 stampabile a misura reale. Resta al PM la sola prova fisica col righello.

`2026-08-03` — Claude — chiarito con il PM il flusso di lavoro reale della skill; ritirata D-036, chiusa D-037, aggiunta D-039 sulla tracciabilità.

`2026-08-03` — Claude — pubblicazione su GitHub in `danielcarta9c/DisegnatoreMEP`, repository pubblico con licenza MIT (D-038).

`2026-08-01` — Claude — chiusura di P0: gate G0 superato, 59 test verdi.
