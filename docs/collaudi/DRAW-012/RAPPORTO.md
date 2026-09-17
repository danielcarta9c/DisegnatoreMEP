# RAPPORTO DI CONSEGNA — DRAW-012

**Pacchetto:** `ACTIVE_WORK_PACKAGE.md` — «Il motore disegna nell'ordine del disegnatore»
**Disposizioni di riferimento:** **D-137** (il caso di prova 4), **D-138** (l'ordine delle
fasi), **D-139** (i millimetri escono, il riempimento entra), **D-140** (la finestra è
45–65 %), **D-141** (come si calcola il riempimento, e la guardia che gli serve)
**Analisi di riferimento:** `docs/pm/2026-09-16-come-ragiona-il-motore-e-come-dovrebbe.md`
**Ruolo:** DEV
**Data:** 2026-09-17

---

## 0. Le quattro cose da leggere prima di tutto il resto

1. **L'autostrada adesso esiste, ed è una linea sola che si vede a occhio.** Sulla tavola 2
   la mandata corre dritta dalla pompa di calore fino ai ventilconvettori attraversando il
   volano e il circolatore, e il ritorno le corre parallelo sotto: le «due macro-linee» che
   il PO chiede da tre giri. Sulla tavola 1 lo stesso, con la seconda pompa che si innesta
   invece di sparire dalla struttura. Le tavole sono in `dopo/`, quelle di `main` in
   `prima/`, ed è il confronto che il pacchetto chiede di guardare per primo (criterio 10).

2. **La tavola 1 entra nella finestra** (criterio 7): 29,8 % → 45,4 %, con la copertura
   dell'ingombro che **sale** insieme (0,625 → 0,734) — cioè il riempimento non è salito
   con il trucco che D-141 teme. **La tavola 2 esce dalla finestra dall'altra parte**:
   50,1 % → 66,7 %, un punto e sette sopra il tetto. È il solo criterio del pacchetto che
   ho mancato per un numero invece che per una impossibilità, e §6.1 dice perché.

3. **La tavola 4 continua a non uscire**, come non esce su `main` — ma il motivo è cambiato,
   ed è molto più vicino alla superficie: non è più «le fasi buttate via e la tavola di
   prima di DRAW-008», è **due corsie di catena di macchina che si incrociano** sul
   circuito sanitario nuovo che D-137 ha disposto. §6.2 lo misura cella per cella e §7
   chiede al PM che cosa farne. Le tavole 3 e 5, che il pacchetto chiede solo di misurare,
   sono misurate in §5.

4. **La suite non peggiora** (criterio 13): 10 rosse, 1470 verdi, 24 saltate, 11 xfailed su
   `main`; lo stesso saldo qui. Nessuna prova convertita in `skip` o `xfail`. **Cinque
   prove le ho riscritte**, e nessuna per farla passare: dicevano ciò che D-139 e D-140
   hanno appena cambiato — «chi allunga il tubo perde», «più pieno è meglio» — e §4.2 le
   elenca una per una con la disposizione che le supera.

---

## 1. Ramo, base, file

| | |
|---|---|
| **Ramo** | quello che la piattaforma ha assegnato alla sessione, come il pacchetto prescrive |
| **Base** | la testa di `main`, `8589620` |
| **Consegna** | una PR sola, non fusa |

### File toccati

| File | Che cosa |
|---|---|
| `src/disegnatore_mep/layout/highways.py` | **nuovo** — l'autostrada intera come oggetto (§C) |
| `src/disegnatore_mep/layout/hierarchy.py` | tutti i generatori sulla spina, gli scambiatori, la strada secondaria, `axis_rank`, la camminata condivisa (§B) |
| `src/disegnatore_mep/layout/flow.py` | i mestieri degli scambiatori e dei terminali |
| `src/disegnatore_mep/layout/improve.py` | `SheetCost` senza la lunghezza e con la finestra; l'invariante sulla catena; l'allungo offerto dove serve (§C, §D, §E) |
| `src/disegnatore_mep/layout/spine.py` | la struttura si consegna anche quando non si instrada; il rango del ramo; le campate che si contraddicono (§F) |
| `src/disegnatore_mep/layout/compose.py` | la cessione graduale al posto del ripiego che scarta le fasi, il diario, l'ordine di instradamento (§F) |
| `src/disegnatore_mep/layout/geometry.py` | la finestra del riempimento come dato condiviso; la copertura calcolata in modo da poter stare dentro il costo |
| `src/disegnatore_mep/validation/preflight.py` | l'altra sponda della finestra (D-140) |
| `examples/prova/build_test_plants.py`, `examples/prova/prova-4-*.json` | il caso di prova 4 secondo D-137 (§G) |
| `examples/layout/build_layout_fixtures.py`, `examples/graphics/build_symbols.py`, `naming/families.json`, e i tre file rigenerati | la commutatrice a tre vie (§G) |
| `tests/layout/test_ordine_del_disegnatore.py` | **nuovo** — le prove del pacchetto |
| `tests/layout/test_costo_peso.py`, `tests/layout/test_riempimento_del_foglio.py`, `tests/validation/test_preflight.py` | le prove che dicevano ciò che D-139/D-140 hanno cambiato (§4.2) |
| `docs/pm/2026-09-11-architettura-della-posa-a-fasi.md` | §3 riscritto all'ordine di D-138, §4 precisato (criterio 16) |
| `docs/collaudi/DRAW-012/**` | questo rapporto, gli strumenti di misura, il pacchetto grafico |

---

## 2. Che cosa è stato fatto, e perché così

### 2.1 §B — che cosa è autostrada, e chi lo decide

Tre cambiamenti in `hierarchy.py`, e nessuno è una taratura.

**Le macchine di spina sono tutte** (`SPINE_FUNCTIONS`): chi genera, chi accumula o separa,
chi **scambia** e chi ripartisce. Prima ne entrava **un generatore solo**, scelto
dall'ordine strutturale, e gli altri diventavano contorno: sull'impianto 4 erano autostrada
le tratte della caldaia e non quelle della pompa di calore. Il PO dice «dai generatori agli
accumuli», al plurale, e «passando per i collettori che **mettono insieme i generatori**» —
cioè con due generatori ci sono due autostrade che confluiscono. Non c'è più nessun
generatore eletto e quindi nessuno spareggio da fare: basta il mestiere.

**La strada secondaria è autostrada anche lei.** Una tratta che da una parte raggiunge una
macchina di spina e dall'altra un'**utenza** — un terminale, o il prelievo sanitario — è di
rango massimo: è la «uscita ACS e distribuzione verso i terminali» che D-138 mette nella
fase della struttura. Il **circolatore** ci sta dentro senza bisogno di nominarlo: è un
accessorio in linea, la tratta lo attraversa, e la linea «accumulo → circolatore →
terminali» è una tratta sola.

**L'ingresso dell'acqua fredda resta fuori**, come il PO chiede, e non per un elenco di
pezzi: il catalogo distingue già i due confini di rete con il **verso delle proprie porte**.
Il prelievo sanitario ha un attacco solo e il fluido vi **entra**; l'acquedotto ha un
attacco solo e il fluido ne **esce**. È la differenza fra «uscita» e «ingresso» nelle parole
stesse del PO, letta da un dato e non da un nome.

### 2.2 §C — l'autostrada intera

`layout/highways.py` è il pezzo nuovo, e chiude il difetto che l'analisi del 16 settembre
aveva misurato senza poterlo nominare: *«dieci tronconi su venticinque tratte, e nessun
invariante dice che la catena intera sia una retta»*.

Una **catena** è una successione massimale di tratte di autostrada che si susseguono
passando **attraverso** i crocevia — i raccordi e i multivia, che non sono capolinea ma
punti della tubazione. Dove il crocevia offre più proseguimenti resta sulla catena quello
che porta all'**accumulo maggiore**, con il conto di `hierarchy.axis_rank` (§2.3). Ogni
tratta sta in una catena sola: due catene sovrapposte pretenderebbero due rette diverse per
lo stesso tratto.

`lies_in_line` verifica sulla catena le tre condizioni che contano, e la terza è quella che
mancava: le due porte di ogni tratta si guardano, la tratta va nel verso della porta da cui
parte, e **fra una tratta e la successiva la retta non cambia** — né direzione né quota. La
prova generale `test_la_catena_intera_e_una_retta_e_ogni_frammento_non_basta` costruisce
proprio il caso che nessun invariante vedeva: due frammenti dritti e un gomito sul raccordo
che li unisce.

`Improver.is_valid` nega alle mosse di far perdere alla catena una rettilineità che aveva,
con la stessa monotonia dell'invariante di tratta: ciò che è dritto non si storce, ciò che
storto era può solo raddrizzarsi.

### 2.3 Il rango del ramo: «accumulo maggiore» sono due parole

L'architettura dell'11 settembre §4 dice «resta sull'asse il ramo verso l'**accumulo
maggiore**». Finché un solo generatore stava sulla spina, su un collettore che unisce due
pompe di calore c'era **un** ramo di autostrada e non c'era niente da scegliere. Con §B i
rami sono due, e leggendo il solo ingombro vinceva la **seconda pompa di calore**
(1200 mm²) contro l'accumulo (1125 mm²): l'asse andava da un generatore all'altro e
l'accumulo si staccava di lato.

`hierarchy.axis_rank` legge quelle due parole **in quest'ordine**: prima **accumulo** — chi
il fluido lo riceve: accumuli, puffer, separatori, scambiatori, collettori — poi
**maggiore**. Lo leggono la fase del tronco e le autostrade intere, e lo leggono identico.

E la **camminata** con cui si guarda che cosa c'è oltre un attacco vive adesso in un posto
solo, `hierarchy.machines_beyond_of`: si cammina **per attacchi**, non per pezzi, così che
dentro un multivia si passi solo dove il catalogo dichiara che si passa. La fase del tronco
camminava per pezzi per conto proprio, e sull'impianto 4 il ramo del riscaldamento
«raggiungeva» lo scambiatore sanitario che pende dall'**altra** uscita della deviatrice: lo
scambiatore è un accumulo, il ramo ne guadagnava il rango, e l'asse ci andava dietro.

### 2.4 §D — la lunghezza esce, il riempimento entra come finestra

`SheetCost` porta ancora `length_mm`, e il rapporto la riporta; ma `key()` non la legge.
Restano i costi veri nell'ordine che D-139 fissa: le **curve**, poi gli **attraversamenti**.

Al posto della lunghezza entra `fill_gap`, e non è monotona: è la distanza dalla finestra
**45–65 %** di D-140, zero dentro, positiva da tutt'e due i lati.

**La guardia di D-141 sta dentro la voce, non accanto.** `fill_gap` è il **peggiore** fra la
distanza dalla finestra e quanto l'ingombro è spoglio rispetto alla copertura minima. È una
scelta, e la ragione è precisa: due voci separate avrebbero lasciato la copertura a fare da
**spareggio** del riempimento, e il trucco che D-141 teme — spingere un pezzo in un angolo
perché il rettangolo cresca — sarebbe tornato a pagare non appena avesse portato il
riempimento dentro la finestra. Con un numero solo il trucco peggiora la voce invece di
migliorarla, e la prova `test_il_trucco_del_pezzo_nell_angolo_non_paga` lo mostra.

Le due sponde della finestra stanno in `layout/geometry.py`, accanto alla misura, e le
leggono in due: il costo di posa e il **preflight**, che adesso avvisa anche quando il
foglio è **troppo** pieno (`SHEET_TOO_FULL`). Un numero solo, in un posto solo: se
divergessero, il ciclo crederebbe di aver riempito un foglio che il controllo vede vuoto.

### 2.5 §F — si cede una curva, non si butta la struttura

Due punti, e il secondo non era nel pacchetto ma è lo stesso difetto.

**In `compose_sheet`**, il terzo ripiego era «il ciclo senza le fasi, cioè la tavola che
sarebbe uscita prima di DRAW-008». Adesso, fra la posa seminata e quella rete, c'è la
**cessione graduale**: una catena per volta esce dall'invariante e il ciclo può piegarla
per far entrare il resto. Si cede a chi ne ha meno bisogno — prima le catene che nessuna
posa raddrizza comunque, poi le più corte — e **solo a chi si sta davvero tenendo**: su una
catena già storta l'invariante non vincola niente, e toglierla sarebbe un ciclo intero
speso per non cambiare nulla. Il ripiego che scarta le fasi resta come ultimissima rete, e
il **diario** (`ComposeJournal`) dice sempre con quale via la tavola è uscita.

**Nella fase del tronco**, lo stesso difetto stava un piano più in basso e costava di più:
quando le autostrade costruite non si instradavano — su un foglio dove **nessun accessorio
è ancora posato** — la fase consegnava `symbols=()` e chi la chiamava tornava alla posa di
partenza. Sull'impianto 4 la fase non muoveva **un solo pezzo su ventidue**, e la tavola
usciva come se le autostrade non esistessero. Adesso la fase consegna le **posizioni** — la
forma che ha costruito — e dichiara che le sue linee non si sono instradate (`routed`).

E una terza cosa, che è la stessa medicina: **le campate che si contraddicono**. Sul
circuito sanitario di D-137 lo scambiatore deve stare sotto la deviatrice della caldaia e
sopra la commutatrice del suo ritorno, mentre le due valvole stanno sulla stessa retta
orizzontale: un anello di disuguaglianze senza soluzione. Arrivava intatto al rilassamento
delle campate, che su un anello non converge e a ogni giro ne somma un'altra: la pompa di
calore finiva **duecentocinquanta millimetri** sopra il resto, fuori dal foglio. Adesso si
toglie una campata per volta — la **più corta** dell'anello, quella che chiede meno —
finché le campate non si contraddicono più. È la cessione di §F applicata a un asse.

### 2.6 §E — l'allungo offerto dove serve

Il pacchetto dice che lo stretch «nessuna consegna ha ancora usato davvero», e nel codice si
vede perché: l'allungo era offerto **solo sulle tratte già rettilinee**. La cosa si mordeva
la coda — quando la posa è stretta il tronco non è dritto, ed è proprio quello il problema —
e l'unica mossa capace di fare spazio spariva dall'elenco. Sul banco del pacchetto il ciclo
esauriva centonovantotto candidate senza che una sola fosse un allungo. Il taglio resta
quello che era: si allontana ciò che sta oltre **lungo un asse solo**, quindi nessuna quota
dell'altro asse cambia; che una catena già dritta non si storca lo dice `is_valid`, come per
ogni altra mossa.

### 2.7 §G — il caso di prova 4, e la commutatrice

Il grafo è quello dettato per esteso in D-137, componente per componente e collegamento per
collegamento: due ritegni, il volano come **disgiuntore** fra generatori e distribuzione, il
sanitario come circuito **dedicato alla caldaia**, lo scambiatore in centrale.

La voce di catalogo nuova è `switching-valve-3way`, **Valvola commutatrice a tre vie**: due
ingressi, un'uscita, e la funzione `circuit_switching` dichiarata — non la miscelatrice
piegata, che dichiara `circuit_mixing` e serve ad altro. Miscelare vuol dire far uscire i
due ingressi **insieme**; commutare vuol dire farne passare **uno per volta**. Il simbolo è
quello della tre vie di UNI 9511 Tab. 3 — «la stessa valvola, montata al contrario», come
D-137 §D.2 dispone — con l'asse passante fra `in_a` e `out` e il secondo ingresso sulla
terza via. La famiglia è **VC**, in `naming/families.json`.

---

## 3. I criteri, uno per uno

*(§3 è compilata in §5 con i comandi e il loro output: qui resta il quadro.)*

---
