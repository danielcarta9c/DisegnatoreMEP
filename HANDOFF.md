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
| 8 | `docs/DECISION_LOG.md` | Decisioni funzionali D-001–D-052 |
| 9 | `docs/ROADMAP.md` | Fasi del progetto e perimetro futuro |
| 10 | `docs/ARCHITECTURE.md` | Struttura del codice effettivamente consegnato |
| 11 | **`docs/GRAPHIC_STANDARD.md`** | **Lo standard grafico.** Grandezze in millimetri, regola perimetro-faccia, divisione fra geometria del simbolo e semantica del catalogo, compositi, rotazioni, come si aggiunge un simbolo, come si stampa il foglio |
| 12 | `docs/P0_REVIEW_FINDINGS.md` | Cosa le revisioni di P0 hanno trovato e non è stato risolto. **Il §3.1 fissa il flusso di lavoro reale della skill**: due revisori indipendenti erano partiti da una lettura sbagliata |
| 13 | `docs/plans/README.md` e `docs/plans/2026-08-01-master-implementation-roadmap.md` | Sequenza dei piani |
| 14 | `docs/plans/2026-08-01-foundation-core-plan.md` — **solo l'appendice finale** | Il piano P0 eseguito e le sue deviazioni. Il corpo contiene codice difettoso |
| 15 | **`docs/plans/2026-08-03-graphic-system-symbol-library-plan.md` — solo l'appendice finale** | Il piano grafico eseguito. **Sedici difetti corretti in esecuzione**, sei del piano e dieci trovati dalle revisioni. Anche qui il corpo non è stato riscritto |
| 15bis | **`docs/plans/2026-08-04-layout-routing-multitavola-plan.md` — per intero** | Il piano successivo, **scritto e non eseguito**. Qui il corpo si legge davvero: è il lavoro da fare. Il §0 raccoglie le tre decisioni di prodotto, tutte chiuse dal PM, e spiega perché una quarta è stata ritirata, il §2 le tre scoperte fatte prototipando |
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

- **Fase:** fondazione canonica e sistema grafico completati. Il piano di layout, instradamento e multi-tavola è **scritto e in attesa di approvazione**; nessun suo task è partito. Rendering, cartiglio e PDF non ancora pianificati.
- **Versione installabile:** nessuna release; `releases/latest/` non è ancora popolata.
- **Verifica:** 147 test verdi; `pytest`, `ruff` e `mypy --strict` a exit `0` su `src`, `tests` ed `examples`.
- **Libreria:** dodici simboli pubblicati in `assets/symbols/` più otto di fixture in `examples/foundation/symbols/`, entrambe rigenerabili identiche dai rispettivi generatori.
- **Il gate G0 di P0 regge ancora** e il fingerprint del progetto misto non si è mosso: `3347374e8b3f006c6f387c6228e0d9d2b885cbf57e65991937e985af32306573`.
- **Ambiente:** ricostruibile da zero con `bash scripts/setup-env.sh`. **Da eseguire come prima cosa in una sessione cloud**, che riparte sempre da un clone pulito.
- **Ramo:** la fase grafica è stata sviluppata su `claude/graphic-symbol-library-setup-acgoka` e **integrata in `main` con un merge esplicito** (`8e2b664`), come era stata chiusa P0. Si riparte da `main`. Il ramo di lavoro è conservato per poter rileggere la sequenza dei commit.
- **In flight:** nessuna modifica applicativa a metà.
- **Blocco:** nessuno. La prova fisica di stampa è stata superata il 4 agosto 2026.
- **Check rapido alla ripresa:** `git status --short` vuoto; `.venv/bin/python -m pytest -q` deve dare 147 passed.

---

## 4. Cosa è cambiato dall'ultima sessione (delta)

- Eseguiti tutti e sette i task del piano grafico con `superpowers:subagent-driven-development`: implementatore fresco per task, revisione di conformità e di qualità, loop di correzione.
- **La geometria si è spostata dal catalogo al simbolo** e le porte stanno sul perimetro. Questo ritira un vincolo P0 esplicito: la motivazione è in `docs/GRAPHIC_STANDARD.md` §3.1.
- Prodotto il primo artefatto guardabile del progetto: un **A3 stampabile** dei simboli a misura reale. Rasterizzato a 10 px/mm la barra di scala misura 100,000 mm esatti.
- Corretti **sedici difetti**: sei nel codice letterale del piano, dieci trovati dalle revisioni. Elencati nell'appendice del piano grafico.
- Tutte queste modifiche sono già promosse nei documenti canonici: non ricostruirle da questo elenco.

---

## 5. Punto esatto da cui riprendere

**La prova di stampa e' superata.** Il PM ha stampato l'A3 il 4 agosto 2026 e la barra di
scala misura 100 mm col righello: l'invarianza di scala e' dimostrata sulla carta, i dodici
simboli sono riconoscibili alla loro dimensione reale, e il gate grafico e' chiuso. Non
riproporre quella verifica.

Dalla stampa sono nate due convenzioni di prodotto che vincolano il piano di layout, e sono
la cosa piu' importante da portarsi dietro:

- **D-051, la nomenclatura visibile e' in italiano.** Il `name` di un manifesto e' la
  denominazione italiana; l'`id` e' codice e non compare su un elaborato. Il difetto trovato
  stava nel rendering, non nei dati: il foglio stampava l'identificativo interno mentre i
  nomi italiani erano gia' nei manifesti.
- **D-052, legenda invece di didascalie ripetute.** La tavola porta a destra una legenda con i
  soli simboli usati e il loro significato, una volta sola. Nel disegno il componente non si
  ri-spiega: solo i tag che aggiungono informazione che la legenda non da', per esempio i litri
  di un vaso di espansione. La legenda dice **cosa**, il tag dice **quanto** o **quale**, il
  disegno dice **dove** e **come e' collegato**. Conseguenze operative in
  `docs/GRAPHIC_STANDARD.md` §4bis: ripartire l'area utile fra corpo e fascia della legenda,
  costruire la legenda dai simboli effettivamente usati nel modello e non dall'intera libreria,
  e riservare gli `label_anchors` ai tag di valore.

**Il piano di layout è scritto.** Vive in `docs/plans/2026-08-04-layout-routing-multitavola-plan.md`: dodici task in TDD, dal `ResolvedComponent` mancante fino alla prima tavola A3 del caso D-011 disegnata e verificata geometricamente. **Non è stato eseguito**: il codice è quello di prima, 147 test verdi, fingerprint invariato.

- **Prossimo passo di sviluppo:** ottenere il via libera del PM a eseguire il piano. Le tre decisioni di prodotto sono già chiuse, quindi nessun task è in attesa: si parte dal Task 1.
- **Leggere il corpo di questo piano, non solo l'appendice.** È la differenza rispetto agli altri due: qui il corpo è il lavoro da fare, e le parti a rischio sono state prototipate ed eseguite prima della stesura — rotazione, tratte e instradamento hanno già le loro prove verdi.
- **Tre difetti trovati scrivendolo**, nessuno registrato altrove prima, tutti nel §2 del piano: nessuno dei venti simboli ha riquadro o porte su un nodo di griglia, quindi un instradatore su griglia non raggiunge nessun attacco; il telaio del foglio non segue il cartiglio che il PM aveva fornito nel primo commit, e i suoi margini sono attribuiti a ISO 5457, che il registro fonti dichiara non acquisita — lo stesso errore che D-047 ha corretto per i simboli; `inline_gap_mm` è confrontato con la larghezza invece che con l'asse che unisce le due porte opposte.
- **Gli input forniti dal PM vanno cercati e aperti prima di decidere.** Il cartiglio era sul disco dal 1 agosto e la fase grafica ha fissato la geometria della carta senza guardarlo, citando una norma mai ottenuta. Prima di dedurre una convenzione grafica, controllare `assets/`.
- **`render_symbol_sheet` è un banco di prova, non la tavola.** Costruisce una griglia uniforme da due costanti di modulo. Non generalizza a una tavola con cartiglio e instradamento: va tenuto come riscontro, non esteso.
- **Attenzione al `keep_out`:** ora è imposto non nullo sulle facce con porta, quindi il layout può fidarsene. Prima non lo era.
- **`usable_height_mm` non è un multiplo del passo di griglia** (277 / 2,5 = 110,8), mentre la larghezza sì. È voluto, i margini seguono ISO 5457. Un layout che assuma entrambi gli assi allineati sbaglia in verticale di 0,8 di passo. Il piano gira intorno al problema lavorando sull'area di disegno — 350 × 235 mm, che è allineata su entrambi gli assi — non sull'area utile del foglio.

---

## 6. Domande aperte per il PM

**Nessuna.**

Le tre decisioni di prodotto del piano di layout sono state chiuse dal PM il 4 agosto 2026, tutte confermando la proposta.

| # | Domanda | Decisione | Applicata da |
|---|---|---|---|
| P1 | Caso D-011 completo o dodici simboli attuali? | Caso completo, con la gerarchia dimensionale che chiude D-050 | Task 7 |
| P3 | Quando si spezza in più tavole? | Solo quando il contenuto non entra | Task 6 |
| P4 | Come si distinguono le reti? | Colore più tratto distinto, leggibile anche in bianco e nero | Task 11 |

**Una quarta era stata posta e ritirata**, e vale la pena sapere perché: chiedeva se il foglio dovesse usare la squadratura del cartiglio o la rilegatura ISO 5457. Il PM ha fatto notare che il cartiglio glielo aveva **già fornito** — è nel primo commit del progetto — quindi non c'era nulla da decidere. Non chiedere al PM ciò che il progetto ha già ricevuto: cercare fra gli input prima di aprire una domanda.

Chiusa nella sessione del 3 agosto: le rotazioni ammesse dichiarano gli orientamenti **tecnicamente** sensati, non quelli geometricamente possibili. Sfiato aria bloccato a `[0]`, vaso di espansione a `[0, 180]` (D-049).

Il PM aveva registrato un input per la libreria vera: **la dimensione del simbolo comunica il peso del componente** nella tavola — valvole piccole, vasi più grandi, accumuli ancora di più. Le misure attuali (6×6, 8×8, 6×10) sono una convenzione di prova, non uno standard da ereditare (D-050). È P1 a chiudere quell'input: il Task 7 del piano fissa una gerarchia in otto classi, tutte multiple del passo di griglia.

Alla ripresa non chiedere al PM di ricostruire il contesto, e non chiedergli di scegliere fra modalità tecniche di esecuzione: il PM valida il prodotto, l'agente è il PM senior dello sviluppo.

---

## 7. Quirks e gotcha emersi

- **Il corpo dei due piani *eseguiti* contiene codice difettoso.** Le loro appendici finali sono le fonti autorevoli sulle differenze. Non vale per il piano del 4 agosto, che non è stato eseguito e il cui corpo va letto per intero: le sue parti a rischio sono state prototipate ed eseguite prima della stesura, e ogni affermazione misurata è marcata **Verificato**.
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

`2026-08-04` — Claude — scritto il piano di layout, instradamento e multi-tavola, non eseguito. Rotazione, tratte e instradamento prototipati e messi sotto test prima della stesura; tre difetti trovati e registrati nel §2 del piano, fra cui il fatto che nessuno dei venti simboli sta sulla griglia. Il PM ha chiuso le tre decisioni di prodotto confermando le proposte; una quarta, sulla squadratura del foglio, e' stata ritirata perche' il cartiglio era gia' fra gli input del progetto.

`2026-08-04` — Claude — prova di stampa superata dal PM. Registrate D-051 (nomenclatura visibile in italiano) e D-052 (legenda a destra invece di didascalie ripetute nel disegno); il foglio di riscontro ora mostra il nome italiano del componente e l'identificativo solo come riferimento secondario.

`2026-08-03` — Claude — eseguito il piano del sistema grafico e della libreria dei simboli. Sette task, sedici difetti corretti, 144 test verdi, primo A3 stampabile a misura reale. Integrato in `main` con merge esplicito. Registrate le convenzioni grafiche interne nel registro fonti, che venti simboli citavano senza che fossero definite da nessuna parte. Resta al PM la sola prova fisica col righello.

`2026-08-03` — Claude — chiarito con il PM il flusso di lavoro reale della skill; ritirata D-036, chiusa D-037, aggiunta D-039 sulla tracciabilità.

`2026-08-03` — Claude — pubblicazione su GitHub in `danielcarta9c/DisegnatoreMEP`, repository pubblico con licenza MIT (D-038).

`2026-08-01` — Claude — chiusura di P0: gate G0 superato, 59 test verdi.
