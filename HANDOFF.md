# HANDOFF — Disegnatore MEP · 2026-08-05 (rilancio ordinato dal PM)

> ⚠️ **Prima di tutto:** il 5 agosto il PM ha registrato **otto difetti** sulla tavola
> completa, ha ordinato la riverifica da zero e ha imposto **il metodo dei tre ruoli**
> (D-083): uno decide, uno o più fanno, uno controlla — con collaudo indipendente e
> cancelli vincolanti. Il piano operativo è
> `docs/plans/2026-08-05-rilancio-qualita-tavola-plan.md`, **in attesa del suo via**.
> Le sezioni §3–§5 di questo file descrivono lo stato di fine layout (4 agosto) e vanno
> lette con questa correzione: il «prossimo passo P3A» è superato da D-084.

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
| 8 | `docs/DECISION_LOG.md` | Decisioni funzionali D-001–D-084. **Le D-072–D-084 sono gli otto difetti del PM e il metodo dei tre ruoli: leggerle per prime** |
| 8bis | **`docs/QUALITA_GRAFICA.md`** | **Le regole del colpo d'occhio** (D-076): lo standard contro cui si giudica ogni tavola, e il metro del collaudo |
| 8ter | **`docs/plans/2026-08-05-rilancio-qualita-tavola-plan.md`** | **Il piano operativo corrente**: riverifica input per input, metodo, sette pacchetti con criteri di accettazione |
| 9 | `docs/ROADMAP.md` | Fasi del progetto e perimetro futuro |
| 9bis | **`docs/DEFERRED.md`** | **Decisioni rimandate e note di sviluppo futuro.** Ogni «per ora no» del progetto sta qui col suo perché e con cosa lo sbloccherebbe. Leggerlo prima di proporre al PM qualcosa che è già stato rimandato |
| 10 | `docs/ARCHITECTURE.md` | Struttura del codice effettivamente consegnato |
| 11 | **`docs/GRAPHIC_STANDARD.md`** | **Lo standard grafico.** Grandezze in millimetri, regola perimetro-faccia, divisione fra geometria del simbolo e semantica del catalogo, compositi, rotazioni, come si aggiunge un simbolo, come si stampa il foglio |
| 12 | `docs/P0_REVIEW_FINDINGS.md` | Cosa le revisioni di P0 hanno trovato e non è stato risolto. **Il §3.1 fissa il flusso di lavoro reale della skill**: due revisori indipendenti erano partiti da una lettura sbagliata |
| 13 | `docs/plans/README.md` e `docs/plans/2026-08-01-master-implementation-roadmap.md` | Sequenza dei piani |
| 14 | `docs/plans/2026-08-01-foundation-core-plan.md` — **solo l'appendice finale** | Il piano P0 eseguito e le sue deviazioni. Il corpo contiene codice difettoso |
| 15 | **`docs/plans/2026-08-03-graphic-system-symbol-library-plan.md` — solo l'appendice finale** | Il piano grafico eseguito. **Sedici difetti corretti in esecuzione**, sei del piano e dieci trovati dalle revisioni. Anche qui il corpo non è stato riscritto |
| 15bis | **`docs/plans/2026-08-04-layout-routing-multitavola-plan.md` — §0, §2 e l'appendice** | Il piano di layout, **eseguito**. Il §0 porta le decisioni di prodotto e perché una quarta domanda era mal posta; il §2 le tre scoperte fatte prototipando; l'appendice i nove difetti trovati eseguendo. Il corpo dei task è stato scritto prima e non riscritto |
| 15ter | **`docs/plans/2026-08-04-rules-engine-plan.md` — §2, §3 e l'appendice** | Il motore delle regole, **eseguito**. Il §2 porta i due difetti di progetto trovati prototipando, il §3 i vincoli — a partire da «una regola non può nominare un componente» — e l'appendice i sette difetti trovati eseguendo |
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
7. Perché rileggere alla lettera il corpo dei piani P0 e grafico è pericoloso, e perché il piano di layout è diverso?
8. Perché una porta di simbolo deve cadere su un nodo di griglia?
9. Dove vivono le coordinate della tavola, e perché non nel modello tecnico?

Risposte attese: motore compositivo, provato cercando ogni termine impiantistico nel sorgente e trovando solo i nomi di dominio, zero condizionali su tipo di componente, e gate G0 su un progetto a quattro domini; il modello tecnico canonico, con geometria, SVG e PDF derivati; l'intero dossier di interpretazione, integrazioni, assunzioni e domande, confermato dentro la conversazione — se l'ingegnere rifiuta un'integrazione la skill semplicemente non la inserisce; la geometria nel manifesto del simbolo e la semantica nella definizione di catalogo, tenute allineate dalla verifica incrociata sugli identificativi di porta al caricamento (D-043); perché non sarebbe un punto a cui attaccare una tubazione, e ritira deliberatamente «le porte possono stare ovunque dentro il riquadro» (D-044); la generazione fallisce con una diagnostica che dice quanti simboli stanno, su entrambi gli assi, perché la scala di stampa è invariante (D-045); i primi due contengono codice che non funziona, corretto solo nelle rispettive appendici, mentre il piano di layout ha prototipato ed eseguito le proprie parti a rischio prima della stesura e marca **Verificato** ogni affermazione misurata; perché l'instradamento ortogonale cammina su nodi e una rotta può terminare solo su un nodo, quindi una porta fuori griglia è irraggiungibile (D-054); nel modello geometrico derivato, rigenerabile, perché il modello tecnico è la fonte di verità e non deve contenere coordinate (D-026, D-042).

---

## 3. Stato attuale del progetto

- **Fase:** fondazione canonica, sistema grafico, motore di layout e **motore delle regole** completati. Il nucleo disegna una tavola A3 del caso D-011. Rendering del cartiglio, PDF e distinta non ancora pianificati.
- **Versione installabile:** nessuna release; `releases/latest/` non è ancora popolata.
- **Verifica:** 461 test verdi; `pytest`, `ruff` e `mypy --strict` a exit `0` su `src`, `tests` ed `examples`.
- **Libreria:** trentuno simboli pubblicati in `assets/symbols/` più otto di fixture, tutti con riquadro e porte su nodi di griglia (D-054) e taglie che seguono la gerarchia dimensionale (D-055). Entrambe rigenerabili identiche.
- **Il gate G0 di P0 regge ancora.** Il fingerprint del progetto misto è `31a6198ee9697f07e2c10199e27781d10e70c058201fb59b95a9f5a94a4d96ac`: si è mosso una volta, al Task 3 del piano di layout, perché il documento dichiara ora `schema_version` `1.1.0`. Il valore precedente era `3347374e8b3f006c6f387c6228e0d9d2b885cbf57e65991937e985af32306573`.
- **Ambiente:** ricostruibile da zero con `bash scripts/setup-env.sh`. **Da eseguire come prima cosa in una sessione cloud**, che riparte sempre da un clone pulito.
- **Ramo:** layout e regole sono su `claude/layout-routing-multitable-plan-cbezrw`, **non ancora integrato in `main`**: le due fasi precedenti erano state chiuse con un merge esplicito, e questa attende il giudizio del PM.
- **In flight:** nessuna modifica applicativa a metà.
- **Blocco:** nessuno. La prova fisica di stampa è stata superata il 4 agosto 2026.
- **Check rapido alla ripresa:** `git status --short` vuoto; `.venv/bin/python -m pytest -q` deve dare 461 passed.

---

## 4. Cosa è cambiato dall'ultima sessione (delta)

- **P1 è fatto: il progetto ha il suo primo impianto che nessuno ha scritto a mano.** Da una topologia essenziale escono quindici integrazioni motivate — vaso di espansione, valvola di sicurezza, filtro, defangatore, separatore d'aria, riempimento, scarico, strumenti, e il gruppo sanitario del bollitore — ciascuna con categoria e fonte, e nessuna entra nel modello finché non viene applicata. Sette difetti trovati eseguendo, nell'appendice del piano.
- **Il PM ha giudicato la tavola, tre volte, e ogni giudizio è diventato una regola.** Il ritorno blu che entrava nella valvola a tre vie (D-059), i sali-scendi intorno al circolatore (D-060), le linee sovrapposte per il lungo (D-062). Tutte e tre erano difetti in codice consegnato, e tutte e tre erano misurabili: nessuna ha avuto bisogno di un giudizio soggettivo, una volta capita. È l'osservazione da cui nasce D-065.
- **Fatto il punto sullo stato reale del progetto**, perché ci si stava perdendo a tarare il disegno di un caso solo. Risultato: P0, P2 e P4 fatte; P1 (regole) e P3 (pacchetti di dominio) mai iniziate; P5 a metà, con l'SVG ma senza cartiglio, PDF, distinta né preflight; P6 e P7 mai iniziate. Il file di prova è scritto a mano e non è un impianto vero: è **questo** che tiene il foglio mezzo vuoto, non il layout.
- **Deciso come la skill verifica prima di consegnare** (D-063, D-064, D-065), e riscritta la §12 della specifica di conseguenza.
- **Scritto ed eseguito il piano di layout, instradamento e multi-tavola**: dodici task, dodici commit. Il progetto disegna la sua prima tavola.
- **Il metodo è cambiato**: le tre parti a rischio — rotazione, tratte, instradamento — sono state prototipate e messe sotto test **prima** di scrivere il piano. Nessuna delle tre ha prodotto difetti nel proprio nucleo; i nove difetti trovati stavano nel porting, nell'integrazione e nei task non prototipati.
- **Il cartiglio che il PM aveva fornito nel primo commit non era mai stato aperto.** La sua squadratura è a 10 mm sui quattro lati, mentre `A3_LANDSCAPE` ne dichiarava 20 citando ISO 5457, che il registro fonti elenca «da acquisire e valutare». Corretto con D-053, provenienza registrata come CONV-GRAFICA-003.
- **Nessuno dei venti simboli stava su un nodo di griglia**, quindi l'instradamento non avrebbe raggiunto un solo attacco. Risolto ridimensionando l'intera libreria sulla gerarchia di D-055, che chiude anche D-050.
- **Il fingerprint del progetto misto si è mosso una volta**, col primo cambiamento di modello dopo P0 (W2, `schema_version` a `1.1.0`).
- Tutte queste modifiche sono già promosse nei documenti canonici: non ricostruirle da questo elenco.

## 5. Punto esatto da cui riprendere

**Il progetto disegna.** Il caso D-011 — pompa di calore aria-acqua, ACS con valvola deviatrice, bollitore, volano a quattro attacchi, circolatore secondario, collettore a due zone con terminali misti — si dispone a fasce funzionali su una A3, si instrada in ortogonale, spezza la linea dove sta un accessorio, e porta a destra una legenda coi soli simboli usati. Passa tutti i controlli geometrici della §12.2 e ha un'impronta stabile fra processi.

- **Il PM ha giudicato la prima tavola: è fatta male.** E ha ricordato che la ricerca su come si disegna uno schema — rete, manuali dei produttori, Caleffi — era stata chiesta dall'inizio del progetto e non era mai stata fatta. È vero: il registro fonti porta quattro norme «da acquisire e valutare» dal primo commit, la fase grafica ha inventato `CONV-GRAFICA-001` proprio perché mancavano, e il layout ci è stato costruito sopra.
- **Prima acquisizione fatta**, in `docs/research/2026-08-04-come-si-disegna-uno-schema-funzionale.md`. La norma che mancava è **UNI 9511**. Leggerlo prima di toccare qualunque cosa di grafico: dice cosa regge (la meccanica) e cosa no (il linguaggio e la composizione).
- **Non trasformare un esempio in una legge.** È l'errore di metodo che il PM ha dovuto correggere due volte: dalla tavola di riferimento del 4 agosto erano state ricavate le corsie a quota fissa (rimosse, producevano sali-scendi) e la disposizione in fila dei componenti (D-073, sbagliata allo stesso modo). Un esempio mostra **una** soluzione ammissibile, non l'unica. Da un esempio si ricava un vincolo solo quando lo si riconosce anche altrove, o quando il PM lo dichiara tale.
- **La verifica della qualità grafica sta dentro la skill, prima della consegna, e ha tre livelli (D-063).** Il **preflight grafico deterministico** misura ciò che è misurabile — pieghe, attraversamenti, sovrapposizioni longitudinali, distanze — e classifica bloccante/da approvare/avviso; il **cold eye review**, agente terzo con contesto proprio, giudica ciò che non si misura e può respingere; il **controllo visivo umano** resta a ogni release. Non sono ridondanti: una sovrapposizione di 2,5 mm si trova misurandola, non guardandola, e «questa non sembra una tavola» non si misura. Oggi **non esiste nessuno dei tre**: le misure del preflight vivono in `tests/layout/test_objective.py`, cioè su una sola fixture e solo in fase di sviluppo. È il primo debito del layout.
- **Il ciclo di revisione cambia gli ingressi, mai il disegno (D-064).** Quando il cold eye review respinge, produce un **nuovo piano di impaginazione** e la pipeline rigenera da capo. Nessun agente tocca la geometria prodotta: se lo facesse, morirebbe la proprietà su cui è costruito il progetto — stesso modello e stesso piano, stesso identico file. Il piano è fatto di scelte discrete registrate nel modello proprio perché l'AI potesse sceglierle diversamente (D-042). Il ciclo è limitato nel numero di passate e monotono: si accetta una passata solo se le misure del preflight non peggiorano.
- **Ciò che il cold eye review respinge due volte diventa una soglia del preflight (D-065).** È come sono nate D-059, D-060 e D-062: quattro difetti che il PM ha visto a occhio sono diventati quattro regole misurate. Un giudice che non lascia dietro regole fa ricominciare ogni tavola da zero.
- **La regola su linee e posizioni è quella del PM, ed è implementata (D-060, D-062).** «Minimizzare le curve disegnate, minimizzare gli attraversamenti tra linee e minimizzare la lunghezza delle linee, mantenendo però ordinamenti da sinistra a destra», e «vietato sovrapporre longitudinalmente: sempre separate e ben distinte». Le prime tre sono pesi dell'instradamento; la quarta è un vincolo del posizionamento; la quinta è un **divieto**, non un costo — un costo si può sempre pagare, ed era quello che il motore faceva. Non trattarle come estetica: sono la specifica del disegno, e `tests/layout/test_objective.py` le misura.
- **Come la skill verifica prima di consegnare è deciso (D-063, D-064, D-065)**, ed è la risposta a una domanda che la specifica aveva lasciato a metà: §12.4 chiedeva un controllo visivo **di release, umano**, e nessuno aveva progettato la verifica dentro la skill. Ora c'è, a tre livelli, con il vincolo che il ciclo cambia gli ingressi e mai il disegno.
- **Il formato è deciso e non si riapre (D-058):** A3 orizzontale, A4 se il disegno è proprio piccolo. Niente A0, niente strisce. La proposta contraria, dedotta da due tavole pubbliche misurate in rete, è stata respinta dal PM ed è ritirata dal documento di ricerca. Non dedurre un vincolo di prodotto misurando esempi altrui.
- **Prossimo passo: P3A, il pacchetto di dominio idronico**, insieme all'allargamento del contratto `DomainPack` che va fatto **prima** che i quattro domini procedano in parallelo. Poi P5 col preflight grafico, poi P6 col cold eye review.
- **Una regola non può nominare un componente** (D-069), e una prova automatica lo presidia sull'intero pacchetto pubblicato. È il differenziale del prodotto: il motore delle regole è il posto da cui un catalogo di schemi tipo rientrerebbe dalla porta di servizio.
- **Sull'instradamento non si torna** finché non c'è un impianto completo da disegnare. Con un caso povero qualunque intervento è un'ipotesi, non una correzione.
- Resta aperta la domanda P5 del PM: acquistare UNI 9511.
- **Poi:** scrivere il piano di rendering, cartiglio e PDF. Deve chiudere anche i due limiti che il layout lascia aperti, elencati nel debito noto di `PROJECT_STATE.md`.
- **Da sapere prima di toccare il layout:** il modello tecnico **non contiene coordinate** e non deve acquistarne. Acquista il piano di impaginazione, che è fatto di scelte discrete (D-042). Se un task si trova a voler scrivere millimetri nel `ProjectModel`, ha sbagliato strada.
- **`render_symbol_sheet` resta il banco di prova della libreria**, non la tavola: la tavola è `graphics/sheet.py`.
- **La funzione obiettivo del disegno è quella che il PM ha dettato (D-060):** meno pieghe, meno attraversamenti, meno lunghezza, in quest'ordine, mantenendo l'ordinamento da sinistra a destra. I pesi stanno in `layout/route.py`; il vincolo lo garantisce `layout/place.py`. `tests/layout/test_objective.py` misura tutte e quattro le cose sul caso D-011: se un intervento le peggiora, quella suite lo dice.
- **L'incrocio resta più economico del giro**, e ora la disuguaglianza è scritta per quello che il giro costa davvero: due passi **e quattro pieghe**. La vecchia forma contava solo i passi e reggeva soltanto perché la piega costava quasi quanto un passo (D-041).
- **Mandata e ritorno non si leggono mai dalla geometria** ma dalla topologia del modello, che è orientata per costruzione (D-059). Il difetto che questo chiude era visibile a occhio: la mandata che alimenta la valvola deviatrice usciva blu.
- **Le corsie a quota fissa non esistono più.** Erano la causa dei sali-scendi: una tratta di dieci millimetri saliva a metà foglio e ne riscendeva subito. La corsia buona la trova la funzione di costo; non va dichiarata.
- **Le porte stanno sul perimetro (D-044) e sui nodi di griglia (D-054).** La seconda regola vive nel layout, non nel manifesto, perché `SymbolManifest` non conosce il `GraphicStandard`.

## 5bis. Come si parla col PM

Sta in `AGENTS.md`, ed è la cosa che il PM ha dovuto ripetere più volte. Non fargliela
ripetere ancora.

**Lui è il committente, l'agente è il PM senior dello sviluppo.** Il PM valuta se stiamo
costruendo il prodotto giusto; le sue correzioni non sono mai tecniche. «La tavola è fatta
male», «il ritorno blu entra nella valvola», «vietato sovrapporre le linee»: sono sintomi
di prodotto, e trovarne la causa tecnica è lavoro nostro, non suo.

**Zero verbosità, e deve capirlo un non sviluppatore.** Niente nomi di file, funzioni o
costanti in una risposta; niente codice; niente racconto di come ci si è arrivati. Il
dettaglio tecnico ha già due posti dove vivere — i documenti di progetto e i messaggi di
commit — e la conversazione non è uno di quelli.

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
| Cosa è stato rimandato, e perché | `docs/DEFERRED.md` |
| Dove trovare le decisioni | `docs/DECISION_LOG.md` e `docs/adr/` |
| Come gestire fonti tecniche | `docs/research/SOURCE_REGISTER.md` |
| Come produrre una release | `releases/README.md` |

---

## Stato del rilancio al 5 agosto 2026, sera

Ordine del PM: procedere fino a una tavola che **un agente terzo approverebbe**.
Piano: `docs/plans/2026-08-05-rilancio-qualita-tavola-plan.md`, appendice = registro
di esecuzione con i verdetti.

| Pacchetto | Stato |
|---|---|
| WP1 simboli dalle fonti | **APPROVATO** al ri-collaudo (respinto una volta, corretto) |
| WP2 regole per attacco + dossier PM | **APPROVATO** |
| WP3 disposizione al servizio delle linee | eseguito, in attesa di collaudo. Caso completo su **una sola A3**, pieghe 28→24, incroci 11→9 |
| WP3b mosse di rotazione | in sviluppo — chiude l'andata-e-ritorno sul prelievo ACS che il PM aveva cerchiato |
| WP4 etichette accanto al pezzo, richiami a 45°, scavalli e pallini | in sviluppo |
| WP5 preflight di qualità bloccante | eseguito, in attesa di collaudo. **Blocca la tavola oggi**, correttamente |
| WP6 cold eye review | protocollo e prompt scritti (`docs/COLD_EYE_REVIEW.md`, `docs/prompts/cold-eye-review.md`); ciclo non ancora eseguito |
| WP7 rigenerazione e consegna | non iniziato |

**Tre prove di accettazione sono rosse per progetto**: pretendono che il disegno esca
mentre il preflight lo blocca sui richiami non ancora corretti. Si chiudono con WP4.
Non ammorbidirle.

**Difetto nuovo trovato dal preflight, da chiudere (WP3c):** tre tratte passano a
distanza zero da accessori appartenenti ad altre tratte. Causa probabile: un accessorio
viene posato dopo che una tratta precedente è già stata instradata, quindi quella tratta
non poteva evitarlo. Il posizionamento degli accessori deve considerare anche le tratte
già instradate, non solo i simboli.

**Come si produce l'immagine per l'occhio terzo:**
`scripts/rasterize.sh tavola.svg tavola.png`.

## Ultimo aggiornamento

`2026-08-05` — Claude — **rilancio.** Otto difetti del PM registrati sulla tavola completa
(D-072–D-082: divisione col foglio vuoto, fila come legge, valvole per attacco, etichette
come tubi, disposizione che non serve le linee, scavallo mancante, lunghezza nel
bilancio, simboli senza fonte). Scritte le regole del colpo d'occhio
(`docs/QUALITA_GRAFICA.md`). Il PM ha ordinato riverifica da zero e metodo dei tre ruoli
(D-083); scritto il piano di rilancio con audit controverificato da collaudatore
indipendente (D-084), **in attesa del via del PM**. Nessun codice toccato: solo
registrazioni e piano, come da suo ordine.

`2026-08-04` — Claude — scritto il piano di layout, instradamento e multi-tavola, non eseguito. Rotazione, tratte e instradamento prototipati e messi sotto test prima della stesura; tre difetti trovati e registrati nel §2 del piano, fra cui il fatto che nessuno dei venti simboli sta sulla griglia. Il PM ha chiuso le tre decisioni di prodotto confermando le proposte; una quarta, sulla squadratura del foglio, e' stata ritirata perche' il cartiglio era gia' fra gli input del progetto.

`2026-08-04` — Claude — prova di stampa superata dal PM. Registrate D-051 (nomenclatura visibile in italiano) e D-052 (legenda a destra invece di didascalie ripetute nel disegno); il foglio di riscontro ora mostra il nome italiano del componente e l'identificativo solo come riferimento secondario.

`2026-08-03` — Claude — eseguito il piano del sistema grafico e della libreria dei simboli. Sette task, sedici difetti corretti, 144 test verdi, primo A3 stampabile a misura reale. Integrato in `main` con merge esplicito. Registrate le convenzioni grafiche interne nel registro fonti, che venti simboli citavano senza che fossero definite da nessuna parte. Resta al PM la sola prova fisica col righello.

`2026-08-03` — Claude — chiarito con il PM il flusso di lavoro reale della skill; ritirata D-036, chiusa D-037, aggiunta D-039 sulla tracciabilità.

`2026-08-03` — Claude — pubblicazione su GitHub in `danielcarta9c/DisegnatoreMEP`, repository pubblico con licenza MIT (D-038).

`2026-08-01` — Claude — chiusura di P0: gate G0 superato, 59 test verdi.
