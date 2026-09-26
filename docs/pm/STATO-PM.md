# STATO PM — il dossier di stato della sessione

**Aggiornato:** 2026-09-26 (`REL-003` fuso, tavola approvata — I-136; `REL-002` fuso, tavole approvate — I-132; i numeri delle due sessioni rinumerati alla fusione — I-133; **attivo `REL-004`, il DXF** — I-137)
**A chi serve:** alla sessione che subentra. Leggi questo e sei operativo: non ti serve un
prompt lungo, e chi te lo dà ti sta raccontando qualcosa che dovrebbe stare qui.
**Regola di questo file:** ogni sessione lo aggiorna prima di chiudere. Un file di stato
vecchio è peggio di nessun file di stato.

> **Il nome resta «STATO PM», il ruolo no.** Dal **19 settembre 2026** (**D-147**) **PM e
> DEV sono la stessa sessione**: non c'è più un agente che scrive i pacchetti e un altro che
> li giudica. Questo file smette di essere «l'ingresso del PM» e diventa **il dossier di
> stato**: quello che una sessione deve sapere prima di toccare qualcosa. Il percorso
> `docs/pm/` resta invariato, come `docs/input-pm/`, perché i verdetti che contiene sono
> agli atti e non si riscrivono.

---

## 1. Chi sei

**Un agente solo** (D-147): scrivi il pacchetto e i criteri, sviluppi, misuri, **mostri le
tavole al PO** e — solo dopo il suo sì — fondi, tramite PR. Nella stessa sessione scrivi
`HANDOFF.md` e il pacchetto successivo. Se il lavoro si divide in code che non si contendono
niente, puoi lanciare **agenti paralleli dentro la sessione** (D-152), con il perimetro
dichiarato prima; non consegnano, non fondono, non chiudono niente, e quello che riferiscono
**non è una misura finché non l'hai rieseguito**.

Le regole del mestiere stanno in `docs/governance/OPERATING_MODEL.md` §1.2.1, §1.2.2 e §3.
Le tre che si dimenticano per prime:

- **Non c'è più un secondo agente che verifica al posto tuo.** Il controllo è uno: **il PO
  guarda le tavole**. Ne segue che D-146 non è una buona pratica ma **la porta**.
- **Prima le misure, poi il racconto**, anche verso te stesso. Un criterio senza un comando
  e il suo output è **non raggiunto**.
- **Non decidi al posto del PO.** Dominio MEP, requisiti, convenzioni grafiche e «è questo
  che volevo» sono suoi. Tu proponi e aspetti.

> Lo sdoppiamento del PM in due soggetti è abolito da **D-130**; la separazione fra PM e DEV
> in due sessioni da **D-147**. Quel modello non torna qui.

**Come parlare col PO.** È un ingegnere MEP senior: giudica il **risultato**, non
l'implementazione. Mostragli la tavola, non i criteri numerati; niente nomi di file, di
funzioni o di prove. Se stai per scrivere «il criterio 8 è raggiunto in parte», fermati e
riscrivilo come lo diresti a un collega guardando il disegno.

**Vale anche per le sigle degli input.** Il 15 settembre gli ho portato le domande del
triage scritte come «`I-002` e `I-059` chiedono allo spessore due cose incompatibili», e me
le ha rimandate indietro: «per me non significano assolutamente nulla. O non le scrivi
proprio, oppure se mi chiedi qualcosa deve essere tradotta in termini che io possa capire».
Le sigle servono a noi per ritrovare la riga e restano di qua. La versione buona — la stessa
domanda detta guardando il disegno — sta in `2026-09-15-triage-input-aperti.md` §11, ed è il
modello da riusare.

## 2. Dove siamo, al 24 settembre 2026

| | |
|---|---|
| `main` | **la testa che leggi adesso.** Non si scrive uno SHA qui: questo file vive su `main` e ogni suo ritocco sposta la testa, quindi il numero nasce vecchio — è già successo due volte. La base si dice per contenuto: l'ultima fusione è la PR **#57**, che porta `DRAW-018` — una valvola di sicurezza per generatore (D-182) —, dopo la **#56** di `DRAW-017`. ✅ **Tutte e due fuse con le tavole approvate dal PO** (I-117, I-119) |
| Release dichiarata | **0.3 — generalizzazione**, e dal 24 settembre il lavoro va verso **la prima release** col perimetro del PO (D-183; `docs/plans/2026-09-03-release-plan.md`, sezione «La prima release») |
| Architettura del disegno | **cambiata il 20 settembre**: pianificatore → motore → revisore (**D-151**). `docs/ARCHITETTURA-DEL-PIANO.md` è il documento che vince su ogni contrasto |
| Pacchetto attivo | **`REL-004`** (`ACTIVE_WORK_PACKAGE.md`), **ATTIVO** dal 26 settembre 2026: il DXF (I-137 — prima i pezzi che mancano, la skill per ultima). **`REL-003`, i simboli nuovi, è fatto** (I-136, PR #60) e **`REL-002`, il cartiglio, è fatto** (I-132, PR #59). Poi il PDF senza browser, `REL-001` la skill, `REL-005` il pacchetto della release |
| Il criterio di un'autostrada | **non è un numero** (**D-164**): «un'autostrada per definizione ha poche curve e tratti rettilinei… un criterio **grafico non matematico**». Chi giudica è l'**occhio**. Trasformare un'osservazione in una soglia è **il solutore che rientra dalla finestra** |
| La convenzione grafica | **è quella sviluppata finora e non si tocca** (**D-165**). Le tavole di `input-pm/riferimenti-grafici/` sono riferimenti **sull'instradamento**, non una fonte di convenzione |
| Il metodo con cui si compone | **`D-159`, e viene prima delle regole**: la quota di un'autostrada **non si sceglie**, è quella della **porta** della macchina che la genera. Per intero in testa a `docs/regole-del-piano.md` |
| Le regole misurate | **nove** — A1, A4, B1, B3, B4, **B8** sali-scendi, **B9** corsie libere, **B10** mandata sopra ritorno sotto, **B11** la coppia corre insieme. Ciascuna con la propria **fonte** e il proprio **controllo** (**D-160**), tutte **dentro il punteggio** |
| L'occhio del revisore | **esiste** — `skill/rivedere/`, **D-162**, provato in camera pulita. Ha trovato **due difetti che nessun controllo poteva dare**. **Manca l'anello**: i vincoli sono un rapporto in italiano, non dati |
| Chi sviluppa, chi fonde | **un agente solo** (D-147), agenti paralleli dentro la sessione (D-152). **La fusione la approva il PO guardando le tavole** (D-146) |
| `DRAW-014` | **superato in corsa da D-151**, non chiuso come previsto. Ha fatto uscire le cinque tavole (D-148, D-150) ed è guardandole che il PO ha fermato la linea del solutore. **Quello che ne resta vivo è su `main`** |
| PR #41 (DRAW-012) | **verificata e respinta** il 18 settembre. Tredici criteri su sedici, nessuno barato, rapporto onesto — ma il PO ha guardato le tavole e ha detto «era meglio prima». Verdetto in `docs/pm/2026-09-18-review-pr41-draw012.md`. **Quella PR non è stata fusa.** ⚠ Ma il suo **contenuto** è su `main`: `DRAW-013` è ripartito da quel ramo ed è entrato con la **PR #44** (`a835006`), il commit dove compaiono `layout/highways.py` e `layout/dilate.py`. Non va rifatto |
| PR #32 (DRAW-010) | **verificata e respinta** il 15 settembre. Verdetto in `docs/pm/2026-09-15-review-pr32-draw010.md`. **Il suo lavoro non è su `main`**: la testa del ramo, `df66709`, non è antenata di `main` |
| Le tavole del pianificatore | i cinque impianti completi, composti **da solo** dal pianificatore (`skill/comporre/`) in camera pulita e **approvati dal PO** due volte: il 23 settembre (I-109, «hanno proprio l'aspetto di tavole professionali») e il 24 (I-117). I piani a mano di `docs/collaudi/PROVA-PIANO/` sono storia: materiale di collaudo del pezzo 3 (D-155) |
| Che cosa quelle tavole non dimostrano | **che la skill funzioni nella chat di lavoro.** Ogni tavola esce da un agente in camera pulita e dalla CLI, con la sessione che cuce i pezzi a mano. Il percorso intero — testo dell'ingegnere, grafo, domande, approvazione, piano, tavola — non è mai stato eseguito come lo userà l'ingegnere |
| I cinque impianti | **misurati il 24 settembre**, dalla sessione: formato · rilievi · incroci — 1: A3 · 1 · 1; 2: A3 · 1 · 1; 3: A3 · 1 · 2; 4: A3 · 2 · 2; 5: A2 · 1 · 5. Zero cedute, zero bloccanti. La suite: **46 rosse**, 1690 passate, tutte del percorso senza piano |
| Registro degli input | **103 righe, 32 aperte**, più le regole permanenti (il conto in testa a `docs/input-pm/REGISTRO.md`). **I-085 è aperta per dichiarazione del PO**: «le regole vanno solo aggiunte altre e migliorate» |
| Prodotto in chat | **mai eseguito nel suo ambiente finale.** È il rischio più vecchio |
| Export DXF | **non costruito.** `I-072` è aperta, e non esiste codice di export in `src/` |

> ⚠ **Una cosa che non torna, e va detta.** Il prezzo di D-151 — **via la riproducibilità
> bit-per-bit** (D-023) — e la sospensione del vincolo dell'A3 (D-148) sono stati accettati
> **perché** l'elaborato esce anche in DXF e il disegnatore lo rifinisce in AutoCAD (I-072).
> **Il DXF non esiste ancora**: `I-072` è aperta e in `src/` non c'è nulla che lo scriva. Il
> prezzo è già pagato, la contropartita no. Non è un errore di nessuno — è una sequenza da
> guardare, e la decisione su quando costruire il DXF è del PO.

Il verdetto completo su DRAW-009, con tutte le misure e i comandi, sta in
`docs/pm/2026-09-14-review-pr27-draw009.md`. È anche il modello di come si scrive un
verdetto, e resta valido adesso che a scriverlo è la stessa sessione che sviluppa.

## 3. Come si verifica una consegna, adesso che la scrivi tu

`DRAW-015` chiede dieci criteri. Il rito non cambia perché è sparito il secondo agente:
cambia che **non c'è nessuno a cui delegarlo**.

0. **Prima guardi la tavola, poi conti — e le tavole al PO per prime** (**D-146**, regola
   permanente). Le tavole prodotte gli arrivano prima di qualunque numero o criterio, e se
   non ne è uscita nessuna glielo dici per primo. Non aspetti che le chieda: su `DRAW-010`
   e su `DRAW-012` il giudizio che conta è arrivato dal suo occhio, e tutte e due le volte
   perché le ha chieste lui. Il PO: «altrimenti come PO non ho nulla da verificare e non
   posso contribuire. Rischiamo che prendiate qualche deriva.»
   La regola è nata il 15 settembre sulla consegna di `DRAW-010` (`I-064`): erano stati
   portati al PO pieghe, incroci e lunghezza senza aver letto il disegno, e i quattro
   difetti veri — il prelievo tornato al centro del foglio, lo stretch mai avvenuto, lo
   scarico che attraversa la mandata, la tavola 4 illeggibile — li ha visti lui. **Una
   misura dice se un numero peggiora; non dice se il disegno ha senso.** Si apre guardando,
   si chiude misurando.
1. **Misura la non-regressione prima di aprire la PR, non dopo.** Se un budget peggiora,
   non consegni: ti fermi e lo riferisci.
2. **Misura base e ramo nella stessa cartella**, passando con `git checkout`. Il pacchetto è
   installato *editable* e il `.pth` contiene il percorso assoluto di UNA cartella: un
   `git worktree` che riusa l'ambiente esegue le prove di prima **col codice di adesso**,
   senza nessun errore che te lo dica.
3. **La suite si riesegue per intero, sui due lati.** Mezz'ora l'una: avviale presto.
4. **Ogni criterio si chiude con un comando e il suo output.** Senza prova eseguibile è NON
   raggiunto, non «probabilmente».
5. **Misura anche ciò che il pacchetto dichiara fuori perimetro**, quando è una capacità che
   il prodotto aveva. È la regola nata dall'impianto 4, che si è perso proprio così.
6. **Se una tavola ti sembra sbagliata e i numeri dicono che va bene, scrivilo.** È il
   rilievo più utile che puoi portare, ed è due volte su due il modo in cui i difetti veri
   sono stati trovati in questo progetto.
7. **Quello che riferisce un agente parallelo non è una misura** finché non l'hai rieseguito
   tu (D-152).
8. **Il rapporto è scritto**, criterio per criterio, e vive nella cartella di collaudo del
   pacchetto; si pubblica anche come commento sulla PR.

Gli strumenti di misura esistono e non vanno riscritti: `docs/collaudi/DRAW-008/metriche.py`
(misure per livello di gerarchia), `docs/collaudi/DRAW-009/criteri.py`,
`le-due-sovrapposizioni.py`, `due-prove-senza-caso.py`,
`perche-la-strada-bassa-non-c-era.py`. **Attenzione a che cosa misurano**: alcuni sono nati
per giudicare il solutore, e le loro voci di costo non descrivono più il percorso vigente.

## 4. I fili aperti, al 21 settembre 2026

> **Nota del 24 settembre 2026.** Questo elenco è quello del 21 e resta com'era, perché dice
> come si ragionava. **I punti 0 e 1 sono chiusi nei fatti**: il pianificatore esiste, e le
> tavole che compone da solo il PO le ha approvate due volte (I-109, I-117). **I fili aperti di
> oggi** stanno in testa a `HANDOFF.md`, sezione «Da dove riparte»: la prima release (D-183) —
> `REL-001` la skill e il PDF, poi il cartiglio, i simboli nuovi, il DXF (I-072, I-125), il pacchetto
> della release —; e, come migliorie, l'anello, `passa-per`, i rilievi di A2, A3 e B5.

In ordine di quanto pesano. I rischi numerati stanno in `PROJECT_STATE.md`.

0. **Le tavole non assomigliano a un disegno vero, e l'ha detto il PO guardandole**
   (`I-082`). È il filo che comanda tutti gli altri, perché è il criterio del prodotto.
   Misurato: il disegno è una **fascia nella metà alta** del foglio — `DRAWING_ALL_ON_ONE_SIDE`,
   5,2 volte l'inchiostro fra quadrante pieno e vuoto sull'impianto 1 e **9,0** sul 5 — e
   l'impianto 5 ha **quattordici incroci**. È il **primo difetto aperto del pianificatore**
   (D3 in `docs/regole-del-piano.md`).
1. **Il pianificatore non esiste, e l'anello del revisore è aperto.** È il pacchetto
   attivo, `DRAW-016`, ed è il lavoro che il PO ha nominato chiudendo la sessione del 20
   settembre: «**l'agente che scrive il piano, l'agente che fa le verifiche che dà i
   suggerimenti precisi su dove passare**». Oggi il **piano lo scrive un umano** — l'agente in
   sessione, a mano — e le cinque tavole escono perché qualcuno ha scritto cinque file di
   coordinate: **la skill, da sola, non sa comporre** (D-155, D-156).
   — *~~Il revisore non c'è ancora (D-153)~~: **chiuso da `DRAW-015`** quanto alla metà
   deterministica — `piano/revisore.py` esegue, misura, si ferma e dice perché.*
   — *~~E il pezzo 5 misura ma non guarda~~: **chiuso il 20 settembre** — `skill/rivedere/`
   esiste ed è provato (D-162). **Quello che resta aperto è l'anello**: i vincoli che l'occhio
   scrive sono prosa, e devono diventare **dati** nella sezione `vincoli` del piano perché il
   pezzo 3 li riceva.*
1bis. **Il piano non può chiedere la forma di una spezzata** (**D-161**), e la leva che manca
   ha un nome: **`passa-per`**. Oggi l'unica mossa di chi compone è **togliere di mezzo chi
   occupa la strada** — e costa: sull'impianto 5 una linea faceva **3 pieghe invece di 1**
   perché il gruppo di riempimento stava nella colonna sotto la porta.
1ter. **Le autostrade del 4 e del 5 sono storte, e il PO le ha bocciate:** «la 4 e la 5 mi
   sembra che non hai minimamente risolto il problema». `HIGHWAY_IS_NOT_STRAIGHT` è acceso
   **5 volte sul 4 e 12 sul 5**. **Misurato dove sta il difetto**, e l'esperimento l'ha
   chiesto il PO: ridotti i due impianti a **sole macchine e collettori, senza una valvola**,
   restano **5 spezzate piegate sul 4 e 11 sul 5**. È la fase delle autostrade, non quella
   degli organi.
2. ~~**Nessun controllo sa che cos'è un'autostrada** (`I-068`).~~ **Chiuso da `DRAW-015`:**
   `layout/autostrade.py` porta la catena fino alla tavola instradata e B1 ha il proprio
   rilievo. Era il difetto che ha generato D-151. Dal 22 settembre (**D-171**) il bilancio
   della catena **non è più un numero**: `RUN_WITH_TOO_MANY_BENDS` non si accende su
   un'autostrada, e B1 confronta le pieghe con quelle che i **simboli impongono**.
3. ~~**Le quattro regole di D-154 non hanno ancora un controllo.**~~ **Chiuso da
   `DRAW-015`**, e sono **cinque**: A1, **A4**, B1, B3, B4 in `validation/regole.py`.
   **Quello che resta aperto è il censimento di D-158:** **A2, A3, B2, C1 e C3 non hanno un
   rilievo sulla tavola finita**, e **A3 oggi non è tenuta su da niente** — l'unico posto che
   la faceva valere era il solutore. **C3 è il buco peggiore**: è l'unico difetto di
   **contenuto** che nasce da una scelta **grafica**. Rapporto `DRAW-015` §4bis.
3bis. **A4 è misurata ma non è pulita.** Restano 4 rilievi sull'impianto 1 e 5 su ciascuno
   degli altri; il peggiore è **+50 mm** — l'acquedotto dell'impianto 3, che entra dal bordo
   sinistro invece che da accanto al bollitore. **Si chiudono componendo, non alzando la
   soglia**, ed è lavoro del pianificatore.
4. **«Un passo avanti e uno indietro»** (`I-067`, 16 settembre). Il PO l'ha detto e ha
   ragione: `DRAW-009` migliora la tavola 1 e perde l'impianto 4, `DRAW-010` riprende
   l'impianto 4 e perde due budget e quattro prove. **La causa non è del prodotto ma del
   modo in cui lo chiediamo**: i pacchetti chiedono «non peggiora» e nessuno chiede
   «migliora», quindi il miglior esito possibile è pari. Da `DRAW-011` §F ogni pacchetto
   chiede **almeno un budget che migliora**, e la non-regressione si misura **prima** di
   aprire la PR: se un budget peggiora non si consegna, ci si ferma e si riferisce.
5. **Il verso di mandata e ritorno lo decide la geometria** (`I-010`, aperto dal 9 agosto).
   Su circa un terzo delle tratte il colore di quel tubo è giusto per caso. **Il PO l'ha
   dichiarato fondamentale** — D-136. Nessuno strumento lo misura ancora: `supply` è un
   booleano già deciso quando arriva alla geometria esportata, quindi l'indecisione va
   misurata dentro la camminata sul grafo.
6. **Il prodotto non gira in una chat vera.** Il filo più vecchio e il meno toccato. La 0.3
   non si può dichiarare finita senza una prova verticale in una chat pulita.
7. **L'export DXF** (`I-072`, 17 settembre). **Non costruito**: in `src/` non c'è nulla che
   lo scriva. Fattibile e indipendente dal resto — legge la geometria già esportata, non
   tocca posa né instradamento, e la libreria è fatta quasi solo di rette, rettangoli e
   cerchi (sei archi e tre curve in tutto). **È anche la contropartita di due prezzi già
   pagati**: la riproducibilità (D-023, sospesa da D-151) e il vincolo dell'A3 (D-148) sono
   stati lasciati andare *perché* la tavola si rifinisce in CAD. Pacchetto a sé, **da aprire
   quando il PO lo vuole** — ed è una domanda che vale la pena fargli adesso.
8. **Lo spessore del tratto dice la gerarchia** (D-132): 0,50 mm autostrade, 0,25 mm
   servizio, due livelli e non tre. Oggi la tavola usa 0,18 / 0,35 / 0,50. Da assegnare, e
   porta con sé un nodo che D-132 lascia aperto — con due spessori in un nodo, il pallino di
   derivazione a quattro volte lo spessore va agganciato a uno dei due.
9. **L'audit della libreria dei simboli**, che il PO deve approvare prima della 0.3.
10. ~~**Le prove non dicono che cosa difendono.**~~ **Chiuso da `DRAW-015`:** i 36 file di
    `tests/layout/` portano dentro la propria riga `# categoria:` — 24 difendono il motore,
    10 difendevano il solutore, 4 difendono una regola del piano.
11. **L'ordine degli stacchi non ha un padrone.** Oggi vale per topologia sulle due tavole;
    diventa esigibile su un impianto che lo violi.
12. **Gli attacchi pari di un collettore**: la scambiabilità va dichiarata nel catalogo, non
    dedotta. Pacchetto a sé, da aprire se il PO lo vuole.

**Che cosa non è più un filo, e per quale decisione.**

- **«Il motore non ragiona nell'ordine del disegnatore»** (`I-069`, D-138) era il filo più
  pesante il 16 settembre ed è stato `DRAW-012`, il cui contenuto è su `main` con la PR #44.
  Da **D-151** la domanda si pone diversamente: l'ordine del disegnatore non si insegna a un
  solutore, **lo compone il pianificatore**. L'analisi in
  `2026-09-16-come-ragiona-il-motore-e-come-dovrebbe.md` resta utile per il motore; le sue
  parti sul solutore sono storia.
- **L'anello della fase del tronco** non è più un filo del percorso vigente: la fase del
  tronco **non decide più la posa** (D-151). Resta agli atti.
- **La tavola 1 sotto la finestra del riempimento** (D-140) è chiusa da **D-149**: il
  riempimento esce dagli obiettivi e torna una misura, e la dilatazione di D-142 è ritirata.
- **L'attuazione di D-126 sul prelievo**, che era la causa unica di quasi tutto ciò che la
  PR #32 rompeva, è storia di quel giro: la PR è stata respinta e il suo lavoro non è su
  `main`.

**Ed è tornato a essere un filo** lo **squilibrio fra quadranti**: non come numero da far
entrare in una finestra, ma come il difetto che si vede a colpo d'occhio sulle due tavole
composte del 20 settembre. È la voce 0.

## 5. Cold eye review del 15 settembre — che cosa non tornava, e com'è finita

Lettura dei registri del 15 settembre, non memoria. **Tutte chiuse in giornata**: quelle del
PM da sé, le altre con le sei disposizioni del PO della stessa sera.

| Che cosa non tornava | Come si è chiusa |
|---|---|
| Tre numeri di release in tre file (0.2, 0.3, `0.1.0`) | `HANDOFF.md` allineato a **0.3**. Resta noto e non allineato il numero di versione Python, che non ha mai seguito le release: è un asse diverso e cambiarlo è codice |
| `I-060` chiedeva il PM sdoppiato che D-130 ha abolito | Ritirata, superata da **D-130** |
| `I-014` chiedeva la regola che D-123 ha superato | Ritirata, superata da **D-123** |
| «Aperto» non distingueva più il lavoro dall'archivio: 60 righe su 63 | Triage in `2026-09-15-triage-input-aperti.md`, poi **D-131 … D-136**. Da 60 righe a **12 aperte più 4 regole** |
| La tavola 1 non risultava approvata da nessun atto, e D-116 ci poggiava sopra | **D-133**: le cinque tavole sono casi di prova, non elaborati da approvare. D-116 superata. La domanda era mal posta, e il PO l'ha corretta |
| `I-002` e `I-059` chiedevano allo spessore due cose incompatibili | **D-132**: lo spessore dice la gerarchia. Scostamento voluto dalla norma, dichiarato |
| `I-017` era soddisfatta da mesi senza che nessuno se ne fosse accorto | Chiusa con la misura sulla tavola 2: il prelievo sta 70 mm a destra e 85 mm sopra l'acquedotto |
| `DRAW-007` non ha cartella di collaudo | **Aperta.** Unico buco nella catena: `docs/collaudi/` porta DRAW-001…006-R1, 008 e 009. Va sistemata in un pacchetto |

### La correzione che il PO ha fatto al PM, e che vale più delle otto righe sopra

Gli ho portato queste stesse cose scritte con le sigle degli input, e me le ha rimandate
indietro: «per me non significano assolutamente nulla». Poi ha corretto la domanda sulla
tavola 1, che era mal posta alla radice: **non approviamo tavole, costruiamo un tool**; le
cinque tavole sono prove, un test passato può tornare a fallire, e non si generano tutte a
ogni giro perché lo stesso errore si paga cinque volte. È D-133, ed è la cosa che più cambia
il modo di lavorare da qui in avanti.

## 6. Igiene di git — censimento del 15 settembre 2026

> **Il censimento è di quella data e non è stato rifatto.** Dal 15 settembre sono state
> fuse le PR #34…#45, quindi il conto dei rami fusi è certamente cresciuto. Si rifà prima di
> usarlo.

**Stato al 15 settembre: 35 rami remoti oltre `main`.** Di questi **22 sono completamente
fusi** in `main` — il loro contenuto è tutto lì, cancellarli non perde niente — e **13
divergono**, cioè portano commit che su `main` non ci sono.

**La cancellazione non è eseguibile da una sessione Claude Code in questo ambiente:** il
proxy risponde **403** a `git push origin :ramo`, e il server GitHub MCP non espone un tool
che cancelli un ref. Va fatta dal PO, dall'interfaccia web di GitHub o da una copia locale.

I 22 fusi, sicuri da cancellare:

```
claude/disegnatoremep-interpreter-validation-6j9vk8   claude/draw-001-tavola1-qualita
claude/draw-004-assi-dorsali-tee                      claude/draw-005-contenuto-simboli-tavola1-r20hmg
claude/draw-005-r1-rifiniture-tavola1-3aad42          claude/draw-006-tavola2-semantica-v4n8o5
claude/draw-009-work-package-171cly                   claude/kind-wozniak-clrksw
claude/project-docs-first-pdf-obh471                  claude/ripresa-progetto-tavole-353zsb
claude/work-package-attivo-eijiol                     pm/close-draw005
pm/correct-draw005-r1                                 pm/draw-002-r1-costo-peso
pm/draw-002-routing-qualita                           pm/draw-003-terra-etichette
pm/draw-004-port-topology                             pm/generalize-draw005-r1
pm/register-pdc-port-spacing                          pm/register-po-input-draw004
pm/retro-roadmap-draw005                              pm/spec-draw005-r1
```

I 13 divergenti **non si cancellano senza deciderlo**, perché portano commit unici:
`archivio/fase-grafica-2026-08-03` (+72, è un archivio dichiarato: **si tiene**),
`claude/mep-pacchetto-e-collaudi-42itzv` (+214), `claude/disegnatoremep-main-resume-890881`
(+10), `claude/draw-002-routing-qualita-rhy6yu` (+4), `claude/gov-001-baseline-m6b0mn` (+3),
`claude/draw-003-terra-etichette` (+2), `pm/draw-001-active-work-package` (+2),
`pm/draw-006-component-semantics` (+5), `pm/draw-006-r1-revisione` (+5),
`pm/claude-entrypoint` (+1), `pm/draw-002-r2-riferimenti-visivi` (+1),
`pm/draw-002-r3-specifica-tecnica` (+1), `pm/draw-003-r1-priorita` (+1, l'unico il cui
titolo compare già su `main`).

Nota di governance: §3, obbligo 7, vuole un pacchetto esplicito per cancellare rami. Il PO
ha autorizzato la pulizia in sessione il 15 settembre; l'autorizzazione copre i 22 fusi.

## 7. Le trappole che costano tempo

Tre, ciascuna già pagata almeno una volta.

1. **Il `.pth` dell'installazione editable** (vedi §3.2). Ha già falsato un confronto.
2. **Uno SHA scritto dentro un file che vive su `main` nasce vecchio**, perché ogni ritocco
   al file sposta la testa. Vale per `ACTIVE_WORK_PACKAGE.md` — dove è già stato corretto — e
   **vale per questo file**: la riga `main` di §2 è stata trovata vecchia dal PM che è
   subentrato il 15 settembre, ed è stata trovata vecchia di nuovo un'ora dopo. Ora non porta
   più un numero. La base si dice per contenuto.
3. **Quali impianti producono una tavola è una misura, non un ricordo.** Fino al 18
   settembre gli impianti 3, 4 e 5 non ne producevano — 3 e 5 da prima di `DRAW-009`, il 4
   per una regressione vera. Poi **D-148** (A4→A1) e **D-150** (ripiego dichiarato) hanno
   cambiato le condizioni. **Si rimisura prima di scriverlo**: è il criterio 6 di
   `DRAW-015`, impianto per impianto, con formato e tratte cedute.
4. **Un documento che descrive un prodotto morto senza dichiararlo.** È la trappola per cui
   la ricerca del 4 agosto è rimasta inattuata per sei settimane, e la regola che la chiude
   è una: **o un documento è vigente, o dice in testa che è storia e quale decisione l'ha
   superato.** Il terzo stato è quello che fa danno.

## 8. Che cosa fa la sessione appena subentra

1. Legge `ACTIVE_WORK_PACKAGE.md`, `HANDOFF.md`, `docs/ARCHITETTURA-DEL-PIANO.md` e questo
   file — l'ordine sta in `CLAUDE.md`.
2. Esegue **soltanto** il pacchetto attivo, `DRAW-015`. Se il pacchetto è assente, già
   consegnato, ambiguo o incompatibile con lo stato del repository, **si ferma e chiede al
   PO**.
3. Prima di proporre la fusione: **guarda le tavole**, le mette accanto a quelle del
   disegnatore del PO (`docs/input-pm/riferimenti-grafici/`) e **le manda a lui per prime**
   (D-146). Se da un impianto non ne esce nessuna, lo dice per primo.
4. Quello che aspetta ancora solo il PO: la **lista dei rami da cancellare** (§6), il
   **formato definitivo** (D-148 è momentanea), la **riproducibilità** (D-023, sospesa), il
   **collettore di zona in verticale** (D-049 contro D-144), le **due autostrade storte
   della tavola 2**, e **quando aprire l'export DXF** (`I-072`). Il triage degli input del
   15 settembre è fatto: dossier in `docs/pm/2026-09-15-triage-input-aperti.md`, esito in
   D-131 … D-136.
5. Prima di chiudere la sessione, **aggiorna questo file**, `HANDOFF.md` e il pacchetto
   successivo.
