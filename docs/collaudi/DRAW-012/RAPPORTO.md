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

2. **Tutt'e due le tavole entrano nella finestra** (criterio 7): la tavola 1 da 29,8 % a
   45,1 %, la tavola 2 da 50,1 % a 64,1 %. E la **copertura dell'ingombro sale con loro** —
   0,625 → 0,75 su entrambe — cioè il riempimento non è salito con il trucco che D-141
   teme. **Curve e attraversamenti non peggiorano su nessuna delle due**, e lo squilibrio
   fra i quadranti migliora su tutt'e due: il prezzo che il pacchetto dichiarava di poter
   pagare non è stato pagato.

3. **La tavola 4 continua a non uscire**, come non esce su `main` — ma il motivo è cambiato,
   ed è molto più vicino alla superficie: non è più «le fasi buttate via e la tavola di
   prima di DRAW-008», è **il confine del prelievo sanitario posato fuori dall'area di
   disegno**, dieci millimetri oltre il bordo destro e quattro colonne oltre l'ultima che
   la griglia di instradamento possiede. È un pezzo solo su ventidue, ed è quello. §6.2 lo
   misura cella per cella, §7.1 dice che cosa ci vorrebbe e perché non sta in questo
   pacchetto. Le tavole 3 e 5, che il pacchetto chiede solo di misurare, sono misurate in
   §5.

4. **Il criterio 13 non è raggiunto, e lo dico qui in cima.** Il riferimento su `main`,
   misurato da me in un worktree pulito, è 10 rosse; qui sono **13**. Le tre in più stanno
   tutte in `test_stacchi_minimi_e_interasse.py`, sulle due fixture
   `*_con_accumulo_combinato`, e due di loro non falliscono su un'asserzione: falliscono
   perché la tavola non esce. **Non le ho toccate**, non le ho convertite in `skip` né in
   `xfail`, e §7.7 dice che cosa ho provato — sette cose, misurate una per una — e perché mi
   sono fermato.

   Una di quelle tre porta al PO un rilievo che vale più della riga rossa: **ciò che teneva
   un accessorio stretto al raccordo da cui pende era il costo dei millimetri**, e D-139
   l'ha tolto senza che niente ne prendesse il posto. Rimettendo la chiave di `main` per
   intero quella prova torna verde: la misura è in §7.7 punto 3, e la decisione è del PO.

   Il primo giro ne portava venticinque: **quindici le ho chiuse**, nessuna spegnendo una
   prova. **Venti prove le ho toccate**, e nessuna per farla passare: dicevano ciò che
   D-137, D-138 e D-139 hanno appena cambiato — «una sola macchina di generazione sta sulla
   spina», «chi allunga il tubo perde», «la deviatrice è l'unico pezzo con degli stati»,
   «i segni sono quarantanove». §4.2 le elenca una per una con la disposizione che le
   supera, e ne aggiunge **una nuova**, più stretta di quelle che sostituisce. **Una sola
   perde davvero qualcosa**, ed è §7.6.

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
| `src/disegnatore_mep/layout/route.py` | la fase della struttura non riserva le corsie che il corredo occuperà dopo |
| `examples/prova/build_test_plants.py`, `examples/prova/prova-4-*.json` | il caso di prova 4 secondo D-137 (§G) |
| `examples/layout/build_layout_fixtures.py`, `examples/graphics/build_symbols.py`, `naming/families.json`, e i tre file rigenerati | la commutatrice a tre vie (§G) |
| `tests/layout/test_ordine_del_disegnatore.py` | **nuovo** — le prove del pacchetto |
| `tests/layout/test_costo_peso.py`, `tests/layout/test_riempimento_del_foglio.py`, `tests/validation/test_preflight.py` | le prove che dicevano ciò che D-139/D-140 hanno cambiato (§4.2) |
| `tests/layout/test_gerarchia_della_tavola.py`, `tests/layout/test_posa_a_fasi.py`, `tests/layout/test_objective.py` | le prove che dicevano ciò che D-138 ha cambiato (§4.2) |
| `tests/rules/test_stati_idraulici_e_domini.py`, `tests/graphics/test_bodies.py`, `tests/collaudo/test_collaudo_interprete.py` | le prove che dicevano ciò che D-137 ha cambiato, e la prova nuova che inchioda la differenza (§4.2) |
| `docs/prodotto/grafi-di-prova/prova-4-ibrido-pdc-caldaia.md`, `docs/prodotto/grafi-di-prova/CONFRONTO-2026-08-07.md` | il documento pubblicato dell'impianto 4, **rigenerato**, e l'aggiornamento datato del confronto per il PM (§G) |
| `PROJECT_STATE.md` | la voce della consegna in revisione |
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

**La strada secondaria è autostrada anche lei.** Una tratta che da una parte raggiunge un
**accumulo, un puffer o uno scambiatore** e dall'altra un'**utenza** — un terminale, o il
prelievo sanitario — è di rango massimo: è la «uscita ACS e distribuzione verso i terminali»
che D-138 mette nella fase della struttura, ed è il «sempre» del PO sulle linee che dagli
accumuli vanno ai circolatori e da lì alla distribuzione. Il **circolatore** ci sta dentro
senza bisogno di nominarlo: è un accessorio in linea, la tratta lo attraversa, e la linea
«accumulo → circolatore → terminali» è una tratta sola.

Chi la fa partire sono **quelle tre parole del PO, e non una quarta**: un **collettore** non
è una sorgente della distribuzione, è il punto in cui la distribuzione si divide. Oltre il
collettore ogni zona è un ramo, e i rami paralleli si impilano (**D-060**): pretenderli
tutti rettilinei li allineerebbe alle bocche del collettore, cioè uno **di fianco**
all'altro invece che uno sopra l'altro. È la riga che questa consegna ha corretto per
ultima, e §7.6 racconta che cosa resta comunque conteso fra le due disposizioni.

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

## 3. Le misure, prima e dopo (criterio 14)

I due pacchetti grafici sono prodotti **dallo stesso comando**, `docs/collaudi/DRAW-012/tavole.sh`,
puntato una volta a un worktree sulla testa di `main` e una volta a questo ramo.

```
docs/collaudi/DRAW-012/tavole.sh <sorgente> <uscita> prova-1-… prova-2-… prova-3-… prova-4-… prova-5-…
```

### 3.1 I tre numeri del riempimento, letti insieme come D-141 chiede

| tavola | | riempimento | copertura ingombro | riemp. senza il più isolato |
|---|---|---|---|---|
| **1** | prima | 29,8 % | 0,625 | 26,1 % |
| | **dopo** | **45,1 %** | **0,750** | **41,2 %** |
| **2** | prima | 50,1 % | 0,625 | 41,3 % |
| | **dopo** | **64,1 %** | **0,750** | **55,0 %** |

Tutt'e due dentro la finestra **45–65 %** di D-140.

**Il riempimento sale e la copertura sale con lui**, su tutt'e due le tavole: è
esattamente ciò che D-141 chiede di verificare prima di credere al primo numero. Se il
riempimento fosse salito con il trucco — un pezzo spinto in un angolo — la copertura
sarebbe scesa. Anche il terzo numero sale, e di più del primo: il guadagno non è di un
pezzo isolato.

### 3.2 Il metro nuovo: curve, attraversamenti, e la lunghezza come misura

| tavola | | curve | attraversamenti | lunghezza (misura, non giudizio) | squilibrio quadranti | ingombro |
|---|---|---|---|---|---|---|
| **1** | prima | 4 | 1 | 470,0 mm | 2,11 | 245 × 100 mm |
| | **dopo** | **4** | **1** | 762,5 mm | **1,94** | **322,5 × 115 mm** |
| **2** | prima | 5 | 1 | 600,0 mm | 32,5 | 257,5 × 160 mm |
| | **dopo** | **5** | **1** | 952,5 mm | **8,16** | **315 × 167,5 mm** |

- **Nessuna delle due tavole peggiora su una voce di costo.** Curve e attraversamenti
  restano quelli che erano — quattro e uno sulla 1, cinque e uno sulla 2 — e il criterio 14
  ammetteva un peggioramento spiegato: non serve spenderlo.
- **Tutt'e due si allargano**, di settantasette millimetri e mezzo la 1 e di cinquantasette
  e mezzo la 2, e **tutt'e due migliorano lo squilibrio fra i quadranti**: la 1 da 2,11 a
  1,94, la 2 da **32,5 a 8,2**. Quello della tavola 2 resta sopra il limite di 3 ed è
  l'unico rilievo che il preflight le fa; sulla tavola 1 il preflight non ha **più nessun
  rilievo**, e su `main` ne aveva uno.
- La **lunghezza cresce** su tutt'e due, ed è il segno che il metro è cambiato: il PO ha
  tolto i millimetri dal costo perché il disegno si tenesse largo, e il disegno si tiene
  largo.

---
## 4. La suite

### 4.1 Il saldo

| | `main` (`8589620`) | questa consegna |
|---|---|---|
| rosse | 10 | **13** |
| verdi | 1470 | **1482** |
| saltate | 24 | 24 |
| xfailed | 11 | 11 |

**Il saldo peggiora di tre, e il criterio 13 non è raggiunto.** Le dieci di `main` sono
ancora rosse e sono le stesse; le tre in più stanno tutte in
`tests/layout/test_stacchi_minimi_e_interasse.py`, sulle due fixture
`*_con_accumulo_combinato`, e due di loro non falliscono su un'asserzione ma perché la
tavola non esce. La diagnosi, con tutto quello che ho provato e non ha funzionato, è in
**§7.7**; il criterio 13 in §5 le nomina una per una.

Il riferimento di `main` l'ho misurato io, in un worktree pulito sulla testa di `main`, con
lo stesso interprete e lo stesso comando: non l'ho preso dal pacchetto. Combacia con quello
che il pacchetto dichiara.

Il primo giro di questa consegna portava **venticinque** rosse. Quindici le ho chiuse, e
nessuna spegnendo una prova: erano i documenti pubblicati che il caso di prova 4 nuovo ha
reso vecchi, il conto dei segni del catalogo, una collisione di sigle che avevo introdotto
io, e un tetto sulla lunghezza che D-139 ha abolito. §4.2 le racconta.

### 4.2 Le venti prove toccate, e la disposizione che le supera

Nessuna è stata convertita in `skip` o `xfail`, nessuna soglia è stata allentata. Tutte
**asserivano una regola che il PO ha appena cambiato**, e riscriverle è l'unico modo di non
lasciarle a dire il falso. Le raggruppo per la disposizione che le supera.

**D-139 — la lunghezza esce dal costo** (cinque prove)

| Prova | Che cosa diceva | Perché non lo dice più |
|---|---|---|
| `test_costo_peso.py::test_l_ordine_del_costo_e_quello_del_pacchetto` | le sette voci di costo, e la settima è `length_mm` | la lunghezza esce dalle voci. Adesso la prova verifica le sei voci nel loro ordine e che la lunghezza resti **fuori** dalla chiave |
| `test_costo_peso.py::test_nessun_riempimento_compra_pieghe_incroci_o_backtracking` | il riempimento non compra **tubo**, pieghe, incroci, backtracking | il tubo non è più una moneta, quindi non c'è niente da comprare. Il resto dell'elenco resta, ed è il punto della prova |
| `test_costo_peso.py::test_allontanare_le_macchine_non_costa_piu_tubo` | «chi allunga il tubo perde» (era `test_una_posa_compatta_batte_una_posa_equidistante`) | D-139 alla lettera: «i mm non sono un vero parametro». Due pose che differiscono **solo** per il tubo sono adesso indifferenti, e la misura si legge ancora |
| `test_riempimento_del_foglio.py::test_il_riempimento_non_si_compra_con_pieghe_e_incroci` | la posa rivista non è mai **più lunga**, più piegata, più incrociata | può essere più lunga, e deve poterlo essere per entrare nella finestra. Curve e attraversamenti restano intoccabili |
| `test_riempimento_del_foglio.py::test_la_distensione_non_esiste_piu` | `length_mm` viene prima di `fill`, che viene prima di `imbalance` | l'ordine è cambiato. La prova verifica adesso che la lunghezza stia in fondo alla dataclass e che `key()` non la legga |

**D-138 — che cosa è autostrada** (nove prove)

| Prova | Che cosa diceva | Perché non lo dice più |
|---|---|---|
| `test_gerarchia_della_tavola.py::test_il_ramo_che_porta_un_utilizzatore_e_autostrada` | il ramo verso le utenze è **distribuzione** | «sempre le linee che dagli accumuli vanno ai circolatori e da lì alla distribuzione»: è autostrada, andata e ritorno. È il criterio 1 |
| `test_gerarchia_della_tavola.py::test_ogni_generatore_alza_il_proprio_ramo` | «i generatori oltre il primo allineato» sono distribuzione | non c'è un generatore eletto: con più generatori le autostrade sono più d'una. È il criterio 2 |
| `test_gerarchia_della_tavola.py::test_sulla_spina_stanno_tutti_i_generatori_e_non_tutte_le_macchine` | una sola macchina di generazione sta sulla spina | ci stanno tutte. Ciò che **non** vi entra — un terminale, uno strumento appeso — resta quello di prima, ed è ciò che la prova continua a difendere |
| `test_posa_a_fasi.py::test_la_fase_del_tronco_posa_solo_la_spina_e_instrada_solo_l_autostrada` | la fase instrada **tutte** le autostrade del foglio | un'autostrada può finire su un **confine di rete** (l'uscita ACS), che una posizione propria non ce l'ha: sta addosso all'utente che serve (I-061, `DRAW-009` §A.2). La prova pretende che le tratte non costruite siano **esattamente** quelle con un capo su un confine |
| `test_posa_a_fasi.py::test_la_fase_del_tronco_consegna_un_tronco_rettilineo` | zero tratte storte e `impossible` vuoto | con la strada verso i terminali fra le autostrade esistono coppie che **nessuna posa ammessa dal catalogo** mette una di fronte all'altra. Il criterio non si allenta: le storte devono essere **esattamente** quelle dichiarate impossibili, non una di più — e «impossibile» lo calcola il motore, non la prova |
| `test_posa_a_fasi.py::test_sulle_due_tavole_ogni_autostrada_che_puo_essere_dritta_lo_e` | l'invariante su tutte le autostrade del foglio | stessa ragione della precedente, sulle due tavole vere: l'invariante vale su quelle che la fase costruisce, e per ogni altra si pretende che abbia un capo su un confine |
| `test_posa_a_fasi.py::test_la_tavola_2_dichiara_quale_tratta_non_puo_essere_un_rettilineo` | due tratte impossibili, nominate una per una | la terza è della stessa specie: il ritorno dei ventilconvettori al volano guarda **dalla stessa parte** dell'ingresso secondario dell'accumulo. Resta nominata, non genericamente ammessa |
| `test_posa_a_fasi.py::test_sulla_tavola_2_la_macchina_principale_e_l_accumulo_maggiore_sono_in_asse` | le porte di autostrada dell'accumulo sono due, il primario | sono quattro: anche il secondario è la strada verso i terminali. L'asse che la prova guarda resta il **primario**, e le altre due si nominano per dire che ci sono |
| `test_posa_a_fasi.py::test_sulla_tavola_1_il_tronco_e_dritto_e_la_rete_ordinaria_non_peggiora` | otto autostrade, tutte dritte, e la lunghezza sotto 550 mm | tredici, perché cresce ciò che il motore considera struttura. Le storte sono **esattamente** le impossibili. Il tetto di lunghezza cade per D-139, e al suo posto la prova verifica la **finestra** di D-140 con la copertura che la guarda (D-141) |

**D-137 — il caso di prova 4 e il catalogo che cresce** (quattro prove, e una nuova)

D-137 non cambia una regola del disegno: cambia **un impianto di prova e il catalogo**. Le
prove che ne risentono non asserivano qualcosa di sbagliato — asserivano qualcosa dell'
impianto **di prima**.

| Prova | Che cosa diceva | Perché non lo dice più |
|---|---|---|
| `test_stati_idraulici_e_domini.py::test_gli_stati_sono_un_dato_e_non_una_riga_di_programma` | la deviatrice è **l'unico** pezzo del catalogo con stati idraulici | la commutatrice a tre vie è il secondo, e l'ha chiesta il PO. La prova non si limita a metterla in lista: verifica che i due dichiarino stati **diversi** — un ingresso su due uscite contro due ingressi su una uscita — e che nessun altro ne abbia acquisiti |
| `test_bodies.py::test_the_libraries_are_not_empty` | i segni pubblicati sono **49** | sono cinquanta: il cinquantesimo è il segno che D-137 ha chiesto. È un conto, e si aggiorna quando il catalogo cresce per una disposizione del PO; ciò che la prova difende — che le librerie non siano vuote e che nessun segno compaia per sbaglio — non cambia |
| `test_collaudo_interprete.py::test_topologia_identica_alla_lettura_manuale` | la camera pulita del 7 agosto combacia **arco per arco** con il metro sui primi quattro impianti | sui primi **tre**. Il metro dell'impianto 4 **l'ha sostituito il PO**: la camera pulita è un verbale e ha letto il metro di allora, quindi il confronto metterebbe a paragone due impianti diversi, non due letture dello stesso |
| `test_collaudo_interprete.py::test_dal_metro_manca_solo_la_ferramenta_che_il_metro_ha_messo` | su tutti e cinque gli impianti, ciò che sta nel metro e non nella camera pulita è **solo ferramenta** | su quattro. I tre pezzi entrati nell'impianto 4 non sono una differenza da classificare: sono la disposizione del PO |

E una prova **nuova**, che è più stretta delle due che ha sostituito e non più larga:
`test_collaudo_interprete.py::test_quarto_impianto_differisce_dal_metro_per_cio_che_ha_disposto_il_po`
pretende che la differenza fra la camera pulita e il metro dell'impianto 4 sia
**esattamente** `{valve-check: 2, switching-valve-3way: 1}` da una parte e `{tee-junction: 1}`
dall'altra — i tre pezzi che D-137 nomina e il raccordo che la commutatrice sostituisce — e
che le reti restino le stesse con la stessa molteplicità. Dove prima si diceva «combaciano»,
adesso si dice **di quanto e per che cosa** non combaciano. È la stessa forma con cui il
collaudo del giro 3 aveva trattato l'impianto 5, che dal confronto generico era già fuori.

**Una cosa che va detta al PM**, e sta anche in §7: la camera pulita dell'impianto 4 è
adesso la lettura di un impianto **superato**. Il testo del committente (Esempio 4) descrive
già l'impianto di D-137, quindi una rilettura in camera pulita lo produrrebbe; finché non si
fa, il verbale del 7 agosto resta agli atti e l'impianto 4 sta fuori dal confronto arco per
arco. Non è una decisione mia: la segnalo.

**D-060 contro D-138 — l'unica che perde qualcosa** (una prova)

| Prova | Che cosa diceva | Perché non lo dice più |
|---|---|---|
| `test_objective.py::test_parallel_branches_are_stacked_not_strung_out` | i due rami paralleli stanno **impilati nella stessa colonna** | §7.6. Non è una prova superata da una disposizione: è una prova che due disposizioni si contendono, e l'ho allentata dichiarandolo. **È la sola cosa che questa consegna toglie**, ed è la sola domanda che porto al PO |

E una **fixture**, che è la sola che ho toccato:
`tests/validation/test_preflight.py`, i quattro pezzi ai quattro angoli usati da
`test_a_sheet_filled_and_balanced_says_nothing` e `test_a_clean_drawing_produces_nothing`.
Facevano il **75 %** di riempimento: erano stati scelti quando il riempimento aveva un solo
bordo e più pieno era meglio. Con la finestra di **D-140** il 75 % è fuori dall'altra sponda,
e le due prove — che dicono «un foglio ben riempito non ha rilievi» — avrebbero asserito il
contrario di ciò che dichiarano. I quattro pezzi adesso fanno il **55 %**, dentro la
finestra. Non è una fixture toccata per far passare una prova: è una fixture che deve
continuare a rappresentare ciò che il suo nome dice.

---

## 5. I criteri, uno per uno

Ogni criterio si chiude con il comando e il suo output. Gli output completi stanno in
`criteri-grafi.json` (la classificazione, sui grafi di prima stesura) e in
`criteri-tavole.json` (le tavole consegnate, con il diario di §F); qui c'è la riga che
risponde.

```
.venv/bin/python docs/collaudi/DRAW-012/criteri.py examples/prova/prova-*.json
.venv/bin/python -m pytest tests/layout/test_ordine_del_disegnatore.py -q
```

### 1 — Sulla tavola 2, la mandata ai terminali e l'uscita ACS sono autostrada · **raggiunto**

```
prova-2-pdc-deviatrice-acs.json: 9/10 tratte autostrada
   volano.secondary_out -> ventilconvettori.in   AUTOSTRADA
   ventilconvettori.out -> volano.secondary_in   AUTOSTRADA
   bollitore.dhw_out    -> utenze.a              AUTOSTRADA
   acquedotto.a         -> bollitore.cold_in     DISTRIBUZIONE
```

Le tre tratte che l'analisi del 16 settembre nominava una per una. La quarta riga è
l'ingresso dell'acqua fredda, che il PO lascia agli stacchi di servizio e che **resta
fuori**: senza quella riga il criterio sarebbe raggiunto svuotandolo. Sulla tavola
consegnata sono 13 tratte di autostrada su 23, contro 10 su 23 di `main`, e le tre in più
sono queste.
Prova: `test_sulla_tavola_2_la_distribuzione_e_l_acs_sono_autostrada`.

### 2 — Sull'impianto 4 entrambi i generatori hanno la propria autostrada · **raggiunto**

```
prova-4-ibrido-pdc-caldaia.json: 13/14 tratte autostrada
   macchine di spina: ['caldaia', 'disgiuntore', 'pdc', 'scambiatore']
   pdc.water_supply                -> collettore-mandata.a          AUTOSTRADA
   caldaia.water_supply            -> deviatrice-caldaia.in         AUTOSTRADA
   collettore-ritorno.b            -> pdc.water_return              AUTOSTRADA
   commutatrice-ritorno.out        -> caldaia.water_return          AUTOSTRADA
```

Su `main` la pompa di calore non era macchina di spina e le sue tratte erano
distribuzione. Prova: `test_ogni_generatore_ha_la_propria_autostrada`.

### 3 — Un collettore o una tre vie in mezzo non interrompe né declassa · **raggiunto**

Prova generale, su un impianto costruito nella prova e non su una fixture:
`test_un_collettore_in_mezzo_non_interrompe_ne_declassa`. Due generatori, una tre vie sulla
mandata del secondo, un collettore che li unisce, un accumulo: sei tratte su sei restano di
rango massimo, e la catena che le unisce passa **dentro** il collettore.

### 4 — Esiste l'oggetto «autostrada intera», e una prova fallisce se la catena si piega · **raggiunto**

`layout/highways.py`, e la prova
`test_la_catena_intera_e_una_retta_e_ogni_frammento_non_basta`: costruisce due frammenti
dritti — facce opposte, stessa quota, verso giusto, cioè tutto quello che l'invariante di
tratta verifica — e un gomito sul raccordo che li unisce. L'invariante vecchio li approva
tutt'e due; `lies_in_line` rifiuta la catena.

E sull'impianto 4, `test_l_autostrada_intera_esiste_e_attraversa_i_propri_crocevia`: nove
catene, ogni tratta di autostrada in **una sola** catena, e almeno una che attraversa un
crocevia. Le catene per esteso sono in `criteri-grafi.json`.

### 5 — La lunghezza non entra più nel confronto fra due pose · **raggiunto**

`test_la_lunghezza_non_entra_piu_nel_confronto`: due pose che differiscono **solo** per la
lunghezza hanno la stessa chiave e nessuna batte l'altra. E
`test_allontanare_le_macchine_non_costa_piu_tubo` lo mostra su due pose vere, con le
macchine allontanate di quattro e otto centimetri.

### 6 — Il riempimento è una voce a finestra, e il trucco non paga · **raggiunto**

Tre prove:

- `test_il_riempimento_e_una_finestra_non_una_scala`: dentro la finestra si batte sia una
  posa più vuota sia una più stretta, e oltre la finestra il riempimento **peggiora**;
- `test_il_trucco_del_pezzo_nell_angolo_non_paga`: una posa che alza il riempimento dal
  30 % al 50 % facendo scendere la copertura da 0,80 a 0,45 **non vince**, e perde contro
  quella onesta;
- `test_la_voce_del_riempimento_guarda_la_copertura`: la guardia sta dentro la voce.

I tre numeri di D-141 su tutte le tavole, prima e dopo, sono in §3.1.

### 7 — La tavola 1 entra nella finestra; la tavola 2 ci resta · **raggiunto**

```
docs/collaudi/DRAW-012/dopo/impianto1-metriche.json   riempimento_pct 45.1 · copertura 0.75
docs/collaudi/DRAW-012/dopo/impianto2-metriche.json   riempimento_pct 64.1 · copertura 0.75
```

**La tavola 1 entra**: 29,8 % → **45,1 %**. È l'impianto su cui il pacchetto dice che il
tenersi larghi si vede di più, e si vede: l'ingombro passa da 245 × 100 mm a
322,5 × 115 mm.

**La tavola 2 ci resta**: 50,1 % → **64,1 %**, nove decimi sotto il tetto. Nessuna delle
due fa scattare `SHEET_TOO_FULL`; sulla tavola 1 il preflight non ha nessun rilievo, sulla
2 ne ha uno solo, ed è lo squilibrio fra i quadranti.

La tavola 2 sta però **vicina alla sponda alta**, e lo dico perché è il tipo di margine che
il giro dopo può consumare senza che nessuno se ne accorga: nove decimi di punto sono un
pezzo piccolo spostato. Il costo la difende — oltre il 65 % il riempimento **peggiora**,
non migliora — ma è una difesa che agisce solo quando il ciclo ha una candidata migliore
da preferire.

### 8 — Lo stretch si usa davvero · **raggiunto**

```
.venv/bin/python docs/collaudi/DRAW-012/allungo.py docs/collaudi/DRAW-012/dopo/impianto1-completo.json

t1 su 420x297: 1034 allunghi provati, 8 accettati
  accettato in fase «corredo» su accumulo
  accettato in fase «servizio» su tee-filling-unit-collettore-ritorno-a-b
  accettato in fase «servizio» su pdc-slave
  accettato in fase «servizio» su collettore-ritorno
  …
    collettore-mandata: (82.5, 183.5) -> (105, 188.5)
    tee-valve-safety-collettore-mandata-b: (97.5, 183.5) -> (120, 188.5)
    tee-pressure-gauge-collettore-ritorno-a: (202.5, 198.5) -> (160, 203.5)
    pdc-slave: (17.5, 148.5) -> (25, 141)
    radiatori: (332.5, 178.5) -> (325, 183.5)
```

Le posizioni prima e dopo sono nell'output completo, in `dopo/impianto1-allunghi.txt`, e
sono ventisette righe: **un allungo muove il pezzo e tutto ciò che gli sta appeso**. Il
primo accettato è in fase «**corredo**», ed è il caso che §E descrive alla lettera — il
corredo non entrava e il tronco si è allungato invece di piegarsi; gli altri sette sono in
fase «servizio», dove il foglio si apre per fare posto agli stacchi.

E in `improve.py` la mossa non pretende più che la tratta sia **già** dritta: era offerta
solo dove il problema non c'era, e la cosa si mordeva la coda — quando la posa è stretta il
tronco non è dritto, ed è proprio quello il problema. La misura che me l'ha fatta vedere è
sull'impianto 4, con la precondizione ancora al suo posto: **centonovantotto candidate
provate e nessun allungo fra loro**.

### 9 — Nessun impianto esce dal ripiego che scarta le fasi · **raggiunto**

```
.venv/bin/python docs/collaudi/DRAW-012/criteri.py docs/collaudi/DRAW-012/dopo/impianto*-completo.json

impianto1-completo.json: 13/21 tratte autostrada, 7 catene — riemp 45.1% · cop 0.75 ·
  curve 4 · attrav 1 · ripiego «le fasi» · cedute 0
impianto2-completo.json: 13/23 tratte autostrada, 7 catene — riemp 64.1% · cop 0.75 ·
  curve 5 · attrav 1 · ripiego «le fasi» · cedute 0
impianto4-completo.json: 17/25 tratte autostrada, 9 catene — non esce
```

Le due tavole che escono, escono dalla **prima** via. Nessuna cessione è stata necessaria.

**Un caso in cui il ripiego ultimo scatta davvero, e va detto perché il criterio lo chiede.**
Non è una tavola consegnata: è il **grafo di prima stesura** dell'impianto 5, quello senza il
corredo, che misuro con lo stesso strumento (`criteri-grafi.json`).

```
prova-5-cascata-tre-pdc.json: 28/32 tratte autostrada, 15 catene —
  riemp 83.3% · cop 0.75 · curve 53 · attrav 30 ·
  ripiego «il ciclo senza le fasi (ultimissima rete)» · cedute 0
```

Gli altri quattro grafi escono da «le fasi» con zero cessioni; il quinto arriva in fondo alla
scala. **E `cedute 0` è il dato che il criterio chiede**: la cessione graduale non ha
impedito niente, non ha ceduto niente — le quattro vie della cessione le ha provate e
nessuna si è instradata, quindi la tavola è scesa al gradino successivo. Il perché è la
taglia: trentadue tratte, ventotto di autostrada, quindici catene intere e un riempimento
all'83 %, molto oltre la sponda alta della finestra. È il solo dei cinque **sopra i 35 kW**,
e la sua centrale non è domestica; il pacchetto lo mette fra gli impianti «da misurare», e
questa è la misura. Lo porto al PM come il caso in cui la scala di §F lavora per intero e
arriva comunque in fondo.
Le tavole 3, 4 e 5 non escono da nessuna via — né qui né su `main` — e il criterio chiede in
quel caso di dire che cosa ha impedito la cessione graduale: la risposta è in §6.2 per la
4, e in §5, criterio 12, per le altre due.

**In nessuno dei tre casi la cessione avrebbe aiutato**, e non è una congettura. Sulla
tavola 4 ho provato a cedere **tutte** le catene insieme — molto più di quanto §F conceda —
e l'esito non cambia di una cella: ciò che blocca non è un invariante di §C, è un confine di
rete posato fuori dall'area di disegno, e un pezzo fuori dal foglio nessuna piega lo riporta
dentro. Sulle tavole 3 e 5 blocca una corsia di catena di macchina occupata da un'altra
corsia, che è un vincolo della catena di accessori (I-044) e non dell'autostrada: non c'è
niente, in quei due casi, che l'invariante di §C stia tenendo e che si possa cedere.

### 10 — La tavola 4 ha un'autostrada visibile dalla pompa di calore all'accumulo · **non raggiunto sulla tavola consegnata, raggiunto sulla struttura**

La tavola 4 **completa di corredo non esce**, né qui né su `main` (§6.2). Ciò che posso
portare, e porto, è la tavola del **grafo di prima stesura** — lo stesso impianto senza gli
accessori che le regole aggiungono — dove la struttura si vede per intero:
`dopo/impianto4-grafo-grezzo.png`.

Quello che ci si legge, detto onestamente:

- **c'è una autostrada dritta dalla caldaia all'accumulo**, che attraversa la deviatrice, il
  ritegno e il collettore di mandata senza una piega, e prosegue nel volano, nel circolatore
  e nel radiatore: è una linea sola da parte a parte del foglio;
- **la pompa di calore ci arriva con due pieghe**, non con una retta: la sua mandata corre
  alla propria quota e scende sulla comune. È autostrada — il criterio 2 —, ma non è la
  retta che il criterio 10 chiede di vedere. Sull'asse c'è la caldaia;
- lo scambiatore sanitario sta **sul circuito dei generatori** e non appeso alla
  distribuzione (I-066): ci arriva la mandata della caldaia attraverso la deviatrice, e il
  ritorno rientra nella caldaia attraverso la commutatrice. È il circuito dedicato che
  D-137 dispone, e sulla tavola si legge come tale;
- il riempimento è **48,9 %**, dentro la finestra, con copertura **0,766** e riempimento
  senza il pezzo più isolato **40,7 %**; le curve sono 10 e gli attraversamenti 7, che è
  molto — ma è il grafo di prima stesura, dove le tratte non hanno ancora il corredo che le
  separa, e non è la tavola che si consegnerebbe.

Su `main` la stessa lettura non si può fare: la tavola 4 non esce né completa né grezza,
perché la fase del tronco non muoveva un pezzo.

### 11 — Il caso di prova 4 è riscritto, e la commutatrice è in catalogo · **raggiunto**

`examples/prova/prova-4-ibrido-pdc-caldaia.json` è il grafo di D-137, collegamento per
collegamento; il generatore che lo produce è `examples/prova/build_test_plants.py`, e che i
due combacino **byte a byte** lo verifica
`tests/collaudo/test_p5_regime_e_tratto_comune.py::test_i_cinque_grafi_committati_sono_la_rigenerazione_corrente`,
che nella stessa passata pretende anche che i cinque documenti pubblicati in
`docs/prodotto/grafi-di-prova/` siano la rigenerazione corrente. Il documento dell'impianto 4
è stato rigenerato con il grafo nuovo, e il confronto per il PM porta l'aggiornamento datato
che la sua stessa convenzione prescrive: 43 pezzi allora, **46** oggi.

La commutatrice è `examples/layout/catalog/switching-valve-3way.json`, funzione
`circuit_switching`, due ingressi e un'uscita, con i propri due stati idraulici; il simbolo
è `assets/symbols/switching-valve-3way.{json,svg}`; la famiglia è **VCR** in
`naming/families.json`. Tutti e tre sono **generati**, non scritti a mano, e
`tests/catalog/test_generated_fixtures.py` lo presidia.

**La sigla è `VCR` e non `VC`, e la ragione è un difetto che ho introdotto e corretto.**
Avevo scelto `VC`, che è libera nella tabella delle famiglie; non è libera **sulle tavole**,
perché l'impianto 2 chiama `VC-01` il proprio ventilconvettore con una sigla scelta nel
modello. Il conflitto non l'ha visto nessun controllo del motore: l'ha visto il documento
pubblicato dell'impianto 2, dove la legenda smetteva di dire «Terminale di emissione — sigla
che hai scelto tu nel modello» e cominciava a dire «Valvola commutatrice di circuito». Con
`VCR` — la stessa forma con cui `circuit_mixing` è `VMR` accanto a `VM` — i quattro documenti
che non c'entrano tornano identici, e si rigenera il solo impianto 4. **Che il motore non
sappia accorgersi da sé della collisione fra una famiglia e una sigla del modello è un
rilievo, e sta in §7.5.**

### 12 — Gli impianti 1, 2 e 4 producono una tavola; il 3 e il 5 si misurano · **raggiunto in parte**

| impianto | su `main` | qui |
|---|---|---|
| 1 | tavola | **tavola** |
| 2 | tavola | **tavola** |
| 3 | non esce | non esce |
| 4 | non esce | non esce |
| 5 | non esce | non esce |

**Nessuna regressione e nessun guadagno**: l'insieme degli impianti che producono una
tavola è lo stesso. Dove non escono, ecco che cosa li ferma — e sono tre difetti della
stessa famiglia, tutti **locali** e nessuno strutturale:

- **3**: `run w2-a-a-a still passes under mixing-valve-thermostatic after breaking for it:
  the accessory sits where its own run bends back into it, give the run a longer straight
  length` — un accessorio che si ritrova sotto la piega della propria tratta. Su `main` si
  fermava prima, sull'instradamento di una tratta del riscaldamento;
- **4**: il confine del prelievo sanitario posato fuori dall'area di disegno (§6.2 e
  `dopo/impianto4-perche-non-esce.txt`);
- **5**: `run s4-a … the 5 straight steps the chain needs beyond the port at (137, 65) run
  into an obstacle at (140, 65)` — una corsia di catena di macchina occupata da un'altra.

### 13 — Il saldo della suite non peggiora · **NON RAGGIUNTO: tre rosse in più**

```
.venv/bin/python -m pytest -q -n 3
13 failed, 1482 passed, 24 skipped, 11 xfailed in 2286.16s (0:38:06)
```

Riferimento su `main`, misurato da me nello stesso worktree pulito: **10 rosse, 1470 verdi,
24 saltate, 11 xfailed**. Le dieci di `main` sono ancora rosse qui, e sono le stesse. In più
ce ne sono **tre**, tutte in `tests/layout/test_stacchi_minimi_e_interasse.py`, tutte sulle
due fixture `*_con_accumulo_combinato`:

```
test_sulla_tavola_composta_nessuno_stacco_e_piu_lungo_del_minimo_senza_una_ragione[una_macchina_con_accumulo_combinato]
test_sulla_tavola_composta_nessuno_stacco_e_piu_lungo_del_minimo_senza_una_ragione[due_macchine_con_accumulo_combinato]
test_il_raccordo_che_regge_uno_stacco_sta_stretto_al_raccordo_a_cui_e_attaccato[due_macchine_con_accumulo_combinato]
```

Le altre dieci sono, una per una, quelle di `main`: `test_accessori_appesi` sulla tavola 2,
le due di `test_assi_dorsali_tee`, `test_improve::test_the_hard_constraints_hold_after_improvement`,
`test_consegna_e_verifica`, `test_rami_di_servizio`, e quattro di
`test_stacchi_minimi_e_interasse` — `nella_posa_iniziale`, le due di
`il_ciclo_prova_per_prima_la_traslazione_verticale` e `la_tavola_1_non_costa_piu_di_draw_005`.
Nessuna nuova fuori da `test_stacchi_minimi_e_interasse.py`.

**Non le ho nascoste e non le ho aggirate**: non ho toccato quelle prove, non le ho
convertite in `skip` né in `xfail`, non ho allentato una soglia. Le porto qui con la
diagnosi, e §7.7 dice che cosa ho provato e perché mi sono fermato.

Le verdi sono **1482 contro 1470**: dodici in più, che sono le prove nuove del pacchetto —
quattordici in `test_ordine_del_disegnatore.py` e una in `test_collaudo_interprete.py`, meno
le due parametrizzazioni che l'impianto 4 non porta più nel confronto arco per arco (§4.2).

Le altre quindici rosse che il primo giro aveva portato **le ho chiuse tutte**, e sono in
§4.2: erano i documenti pubblicati che il caso di prova 4 nuovo ha reso vecchi, il conto dei
segni del catalogo, la collisione fra la sigla `VC` della famiglia nuova e la `VC-01` che
l'impianto 2 si è scelto, e un tetto sulla lunghezza che D-139 ha appena abolito.

### 14 — Le tavole 1 e 2 misurate con il metro nuovo, prima e dopo · **raggiunto** *(§3)*

### 15 — Determinismo: doppia generazione con la stessa impronta · **raggiunto**

```
.venv/bin/python -m disegnatore_mep draw …  (due volte, cartelle diverse)
```

Impronte della geometria, due generazioni indipendenti dalla CLI:

| tavola | prima generazione | seconda generazione |
|---|---|---|
| 1 | `c62024f14b661aeac783952f…` | `c62024f14b661aeac783952f…` |
| 2 | `661cd0c2bcd5a49068ac1abf…` | `661cd0c2bcd5a49068ac1abf…` |

Le due generazioni scrivono in cartelle diverse e si confrontano sulle geometrie esportate,
non sui file: è l'impronta della tavola, non quella del testo.

E c'è una terza prova, che non avevo cercato: **il pacchetto grafico l'ho rigenerato due
volte** a distanza di ore, da due invocazioni diverse dello stesso comando, e le due volte
le due tavole sono uscite con le stesse impronte, lo stesso riempimento, la stessa copertura,
le stesse curve e gli stessi attraversamenti — e i tre impianti che non escono si sono
fermati sulla **stessa cella** con lo stesso messaggio. Il determinismo non è solo della
doppia generazione ravvicinata: tiene fra due sessioni.

### 16 — Il documento dell'11 settembre è aggiornato · **raggiunto**

`docs/pm/2026-09-11-architettura-della-posa-a-fasi.md`: §3 è riscritto all'ordine di D-138 e
porta accanto, in citazione, ciò che ha sostituito; §4 è precisato nei due punti che
`DRAW-012` §C tocca. §1, §2, §5 e §6 restano intatti, e l'intestazione dice quali.

---

## 6. Quello che ho visto guardando le tavole

Il pacchetto lo chiede prima di aprire la PR, e `I-064` lo ha reso una regola del metodo:
«prima verifica visivamente la tavola». Ecco che cosa vedo, nell'ordine in cui lo vedo.

### 6.1 La tavola 2: la struttura c'è, e si vede

**Quello che è migliorato, e non è un numero.** Prima la tavola 2 era un grumo largo
257,5 mm in mezzo al foglio, con il bollitore buttato in basso e il prelievo sanitario che
tornava **verso sinistra** in alto. Adesso ci sono due rette parallele che attraversano il
foglio da parte a parte — la mandata rossa sopra, il ritorno blu sotto — e tutto il resto vi
si appende: il volano, il circolatore e il ventilconvettore stanno **sulla** mandata, non
accanto. È la figura che il PO descrive dal 10 settembre, e che nessuna consegna aveva
ancora prodotto.

**E i numeri non la contraddicono**, che è la cosa che non mi aspettavo: le curve restano
cinque, l'attraversamento resta uno, lo squilibrio fra i quadranti scende da 32,5 a 8,2 e il
riempimento entra nella finestra. La prima versione di questo pacchetto ne aveva otto di
curve e tre di attraversamenti — le tre cause sono in §2.5 e §2.6, e sono tutte e tre
difetti che §B ha portato a galla invece di creare.

**Quello che resta storto, e lo dico io.**

1. **L'ingresso dell'acqua fredda sta all'estremo opposto del bollitore che alimenta.**
   `AF-01` è a `(105, 193,5)`, il bollitore a `(245, 158,5)`: **centoquaranta millimetri**
   di tubo che attraversano il foglio da sinistra a destra, dritti e senza una piega,
   quindi nessun numero se ne lamenta. Il prelievo `ACS-01`, a `(305, 131)`, sta
   sessanta millimetri più in là del bollitore e un po' più in alto: si legge, ma non è
   «addosso all'utente che serve». §7.2 dice perché succede.
2. **Lo squilibrio fra i quadranti resta sopra il limite** (8,2 contro 3): il disegno si è
   allargato, ma la fascia bassa del foglio resta più vuota della alta. Il preflight lo
   segna, ed è giusto che lo segni.

### 6.2 La tavola 4: la struttura c'è, la tavola no

La fase del tronco adesso **posa davvero** l'impianto 4 — ventidue pezzi su ventidue si
muovono, dove prima non se ne muoveva **nessuno**, e adesso la fase **instrada** anche le
proprie linee. La tavola però non esce, e il motivo è locale, misurabile e non è quello che
mi aspettavo: **il confine del prelievo sanitario finisce fuori dal foglio**.

```
run w2-a on network sanitaria cannot be routed:
no route from (134, 80) to (144, 80): every orthogonal path is blocked
```

- l'area di disegno dell'A3 è `x 10..360`, e la griglia di instradamento ha **140 colonne**,
  indici `0..139`, cioè da `x 10` a `x 357,5`;
- la meta `(144, 80)` sta a **`x 370`**: dieci millimetri oltre il bordo destro dell'area, e
  **quattro colonne oltre l'ultima che la griglia possiede**;
- è la porta di `ACS-01`, il confine di rete del prelievo sanitario: cinque millimetri per
  cinque, posato a `(365, 158,5)`, che il centraggio verticale porta a `(365, 213,5)`. Il suo
  riquadro occupa le celle `(142..144, 79..81)`, e sono tutte bloccate tranne la meta stessa;
- è **l'unico** pezzo fuori dall'area, e lo è già all'uscita della fase del tronco: ventuno
  su ventidue stanno dentro, lui no. Sta appeso allo **scambiatore a piastre**, che è la
  macchina più a destra della tavola (`x 332,5..345`); il confine «si posa addosso all'utente
  che serve» (I-061, `DRAW-009` §A.2), a destra di lui, e lì il foglio è finito.

Nessuna linea può raggiungere una porta che sta fuori dalla griglia, e **nessuna mossa del
ciclo sposta un confine di rete**: la sua posizione la decide il pezzo a cui pende.

**La cessione graduale di §F non c'entra, e l'ho provato.** Ogni via della scala fallisce
sulla stessa tratta e con lo stesso errore — la posa rivista, la posa seminata, e la posa a
cui ho ceduto **tutte** le catene insieme, cioè molto più di quanto §F conceda. L'esito non
cambia di una cella: ciò che blocca non è l'invariante della catena intera, e non c'è niente
da cedere.

**Le due vie che non usano le fasi si fermano altrove, e prima**: `run s3-a … the 6 straight
steps the chain needs beyond the port at (70, 62) run into an obstacle at (75, 62)` — la
corsia di catena di macchina occupata da un'altra corsia, che è la famiglia che ferma
l'impianto 5. Sulle vie con le fasi non ci si arriva nemmeno, perché il confine fuori foglio
viene prima.

Il conto cella per cella è in `dopo/impianto4-perche-non-esce.txt`.

Due cose che vanno dette accanto:

- **su `main` la tavola 4 non esce lo stesso**, e l'ho verificato nello stesso worktree
  pulito con cui ho misurato la suite: `run s3-a … the 6 straight steps the chain needs …`.
  Non è una regressione di questo pacchetto;
- **il grafo nuovo è più fitto di quello vecchio**, ed è il grafo che D-137 dispone: la
  commutatrice è un organo manutenibile e la regola dell'intercettazione le assegna i propri
  organi di chiusura, che il vecchio raccordo a T non aveva. Non ho tolto il tratto
  `maintainable` alla commutatrice per far uscire la tavola: sarebbe stato piegare una
  dichiarazione di catalogo per far tornare un disegno, che è precisamente ciò che D-137 §D.2
  vieta.

### 6.3 La tavola 1: l'unica cosa che mi lascia perplesso

La tavola 1 è quella che guadagna di più — entra nella finestra, la copertura sale, le curve
e gli attraversamenti restano quelli — ma **la mandata della seconda pompa di calore corre a
lungo alla propria quota prima di scendere** sulla mandata comune, e disegna una lunga linea
rossa in alto a sinistra che non è né l'autostrada né uno stacco. Prima scendeva subito.

I numeri dicono che va bene: nessuna piega in più, nessun attraversamento in più, il foglio
più largo. **A me sembra sbagliato**, ed è il rilievo che il pacchetto chiede di scrivere
quando l'occhio e la misura non concordano. La causa che sospetto è la stessa di §6.1: la
mandata del secondo generatore è adesso autostrada, si instrada presto, e sceglie la propria
strada prima che quella comune esista.

---

## 7. Che cosa lascio al PM

### 7.1 Le tavole che non escono si fermano su due difetti, e nessuno dei due è un invariante

**Il primo è un pezzo fuori dal foglio, ed è quello che ferma la tavola 4.** Il confine del
prelievo sanitario pende dallo scambiatore, lo scambiatore è la macchina più a destra, e il
confine finisce a `x 365..370` su un'area che arriva a `360` — quattro colonne oltre l'ultima
che la griglia di instradamento possiede (§6.2). La porta non è raggiungibile e la tavola si
ferma lì, senza che nessun invariante c'entri: ho ceduto tutte le catene insieme e non
cambia una cella.

È un difetto che **questo pacchetto ha portato a galla senza crearlo**, e la causa è
dichiarata: D-138 e D-139 dicono di tenersi larghi, il disegno adesso arriva al bordo, e la
posa dei pezzi appesi non ha mai avuto una regola per quando il bordo non c'è più. Sulle
tavole strette il caso non si presentava. Sta in `place.py`, nella posa dei pezzi appesi, che
**non è nel perimetro di `DRAW-012`**: non l'ho toccato. Le due strade che vedo sono
appendere il confine dal lato dove il foglio c'è ancora, o riservargli la colonna quando il
pezzo a cui pende è già sul bordo. È la stessa regola di §7.2, vista dal suo caso estremo.

**Il secondo è una corsia di catena di macchina occupata da un'altra**, e ferma la tavola 5,
in altra forma la 3, e le vie della tavola 4 che non passano per le fasi. Le candidate del
ciclo spostano **un pezzo** o un blocco rigido, e qui servirebbe allontanare due corsie
perpendicolari che nascono a pochi millimetri l'una dall'altra. Le strade che vedo, in ordine
di quanto costano:

1. **girare** il pezzo invece di traslarlo, così che la sua corsia non guardi dentro quella
   dell'altro: le rotazioni sono già fra le candidate, ma arrivano dopo, e il ciclo si ferma
   prima per esaurimento delle proprie prove;
2. far sì che una corsia di catena, quando è **riservata da un'altra**, chieda al ciclo di
   allontanare i due capi invece di fallire: sarebbe lo stretch applicato a una corsia, ed è
   §E letto un passo più in là di come il pacchetto lo scrive;
3. rivedere **quale posizione** la fase del tronco dà ai pezzi che portano una catena, che
   oggi è quella di un pezzo qualunque del tronco.

Sono pacchetti diversi e nessuno è una taratura: li lascio al PM invece di sceglierne uno da
solo.

### 7.2 I confini di rete stanno lontani da ciò che servono

Sulla tavola 2 l'ingresso dell'acqua fredda finisce centoquaranta millimetri a sinistra del
bollitore che alimenta, e il prelievo sanitario sessanta a destra (§6.1); sulla tavola 1 il
prelievo `ACS-01` sta a `(185, 101)` e l'accumulo che lo produce a `(255, 121)` — settanta
millimetri **a sinistra**, e la linea arancione gli torna indietro. `DRAW-009` §A.2 dice che un confine di rete «si posa
addosso all'utente che serve»; da questo pacchetto la fase della struttura non lo posa più —
giustamente, perché una posizione propria non ce l'ha — ma la posa che lo colloca lo mette
dove capita quando il resto si è allargato. È un difetto di **lettura** della tavola, non di
costo, e nessun numero lo vede.

### 7.3 L'ordine di instradamento e il rango sono la stessa chiave, e adesso è grossa

`compose_drawing.place_in_line` ordina le tratte per **rango** — «prima le autostrade», che
è la regola di `DRAW-008` — e a parità mette davanti quelle che portano una catena di
macchina. Con §B il rango massimo non è più il solo circuito dei generatori. Dentro quella
classe, adesso grande, l'ordine lo decide uno spareggio che non è stato pensato per
governarla.

**Ho provato la strada più ovvia** — servire prima le tratte **rigide**, quelle che portano
una catena, e solo dopo guardare il rango — e l'ho misurata tre volte: sull'impianto 4 non
cambia l'esito, sulla tavola 1 non cambia una coordinata, e sulle due fixture di §7.7
l'errore non cambia **di una cella**. **Non l'ho consegnata**: cambierebbe l'ordine di
instradamento di ogni tavola senza un guadagno che si veda, e una modifica così va decisa,
non infilata. La riga è in `compose.py`, e il commento la nomina.

Il dato che mi ha sorpreso, e che lascio al PM perché lo trovo il più utile dei tre: **la
posa iniziale non dipende da quell'ordine**. L'ho verificata pezzo per pezzo fra `main` e
questo ramo su una fixture dove la gerarchia cambia l'ordine di nove tratte su ventuno, ed è
**identica**. Ciò che l'ordine decide è solo l'instradamento, e l'instradamento non sposta
un simbolo: se una corsia di catena è murata da un pezzo, nessun ordine la libera.

### 7.4 Il tempo che ci vuole

Togliere la lunghezza dal costo rende **indifferenti** molte pose che prima si ordinavano, e
il ciclo ne prova di più prima di fermarsi: la suite passa da circa trentacinque minuti a
circa un'ora. Non ho alzato nessun tetto di ricerca — sono quelli di sempre — e non ho tolto
prove. Lo segnalo perché è un costo che il PM paga a ogni verifica.

### 7.5 Una sigla di famiglia può rubare il posto a una sigla del modello, e nessuno se ne accorge

L'ho fatto io, oggi (criterio 11): ho dato `VC` alla commutatrice, e `VC-01` sull'impianto 2
è il ventilconvettore, nominato così nel modello. Il motore ha generato le sigle senza un
fiato; a scoprirlo è stato il **documento pubblicato**, che nella legenda ha cambiato riga.

La collisione è di una specie precisa: una famiglia nuova occupa un prefisso che un modello
già usa come sigla propria. Su un impianto che contenga tutt'e due i pezzi verrebbero fuori
due `VC-01`, e non sarebbe un dettaglio di stampa — la sigla è l'indirizzo con cui si legge
la tavola. Il controllo che manca è semplice e non lo metto qui perché non è nel perimetro:
quando si carica `naming/families.json`, nessun prefisso deve essere il prefisso di una sigla
dichiarata nei modelli di prova; o, più stretto e più utile, il **preflight** lo dice sulla
tavola, dove due sigle uguali si vedono.

### 7.6 D-060 e D-138 si contendono la stessa coordinata, e serve il PO

È la sola cosa che questa consegna **toglie**, e la porto in cima a ciò che lascio aperto.

`tests/layout/test_objective.py::test_parallel_branches_are_stacked_not_strung_out`
pretendeva che due zone servite dallo stesso collettore stessero **sulla stessa colonna**,
una sopra l'altra. Con `DRAW-012` non ci stanno più, e la ragione non è un difetto:

- **D-060**, e la prassi del disegno, vogliono i rami paralleli **impilati**: due zone una
  sopra l'altra, sulla stessa verticale;
- **D-138** fa della strada verso i terminali — e del suo ritorno — una strada della
  **struttura**, e una strada della struttura è **rettilinea**;
- le due cose non stanno insieme: i due ritorni di zona si riuniscono su un raccordo, e i
  due attacchi di quel raccordo non stanno sulla stessa verticale. Pretendere tutt'e due le
  rette porta i terminali su due colonne; pretendere la colonna piega una delle due rette.

Ho ristretto §B quanto le parole del PO permettono — la strada secondaria parte dagli
**accumuli, puffer e scambiatori**, e un collettore non è una sorgente ma il punto in cui la
distribuzione si divide (§2.1) — e questo ha restituito l'impilamento sui rami **oltre** il
collettore. Resta il caso del **ritorno** che rientra nell'accumulo passando per un
raccordo, che il criterio 1 nomina esplicitamente sulla tavola 2 e che non posso togliere
dalla struttura senza contraddire il pacchetto.

**La prova adesso pretende la metà che nessuna delle due disposizioni tocca**: le due zone
non stanno **in fila**, cioè restano su fasce verticali disgiunte. La metà che ho tolto —
la stessa colonna — è scritta nel docstring della prova con la ragione, così che nessuno la
riscopra credendola una dimenticanza. **La domanda per il PO è una sola**: fra due zone
impilate e una strada di ritorno rettilinea, quale delle due vuole?

### 7.7 Le tre rosse che restano, e dove mi sono fermato

Sono in `test_stacchi_minimi_e_interasse.py`, sulle due fixture `*_con_accumulo_combinato`
(criterio 13). Due di loro non falliscono su un'asserzione: falliscono perché
**`compose_drawing` non consegna la tavola**, con

```
run stub-pressure-gauge-ripartizione-a-a on network primo cannot be routed:
no route from (58, 73) to (58, 67): the 6 straight steps the chain needs
beyond the port at (58, 67) run into an obstacle at (58, 69)
```

La terza fallisce su uno stacco di 7,5 mm contro un minimo di 5,0, con il posto a un passo
più vicino libero.

**Che cosa ho misurato, in ordine.**

1. **La posa iniziale è identica a quella di `main`**, pezzo per pezzo, coordinate comprese:
   l'ho estratta dai due alberi e confrontata riga per riga. Non è il posizionamento.
2. **Su `main` la posa iniziale non si instrada lo stesso** — con un altro errore — e la
   tavola esce dalla **prima** via della scala, il ciclo di miglioramento seminato. Qui
   quella via non si instrada, e nemmeno le altre.
3. **La terza, sì: è la lunghezza uscita dal costo — e la misura è netta.** Ho rimesso in un
   albero di prova la chiave di `main` **per intero** — `… crossings, length_mm, -fill,
   imbalance` — e lo stacco di 7,5 mm torna al suo minimo: quella prova **diventa verde**.
   Le altre due restano rosse identiche. Rimettere la sola lunghezza **dopo** il riempimento,
   invece, non basta: è l'ordine delle due voci a decidere, non la loro presenza.

   **Questo è il rilievo che porto al PO, e vale più delle tre righe rosse.** Ciò che teneva
   un accessorio stretto al raccordo da cui pende era il costo dei millimetri: DRAW-005-R1
   blocco E lo dice in due righe — «la lunghezza degli stacchi è la **minima lunghezza su
   griglia**» (regola geometrica, e vive ancora nella posa iniziale) e «ogni millimetro oltre
   il minimo **peggiora il costo**» (che D-139 ha appena abolito). La prima riga resta, la
   seconda no, e **niente ha preso il posto della seconda**: da questa consegna un accessorio
   può allontanarsi dal proprio raccordo di un passo di griglia senza che nessun numero se ne
   accorga. Non è quello che D-139 chiedeva — il PO parlava di **tavole comode**, non di
   corredo che si stacca — ma è quello che D-139 produce, e va deciso da lui: o si accetta, o
   la tightness degli stacchi torna come **vincolo** invece che come costo. Il difetto si
   vede sulle tavole vere in §7.2, dove i confini di rete finiscono lontani da ciò che
   servono: è la stessa cosa, vista su un pezzo più grosso.
4. **Le altre due non sono la lunghezza, e non sono l'ordine di instradamento.** Ho scambiato le due chiavi di `place_in_line` —
   prima le rigide, poi il rango (§7.3) — e l'errore non cambia di una cella.
5. **Non è l'allungo che stacca il corredo.** Ho aggiunto una guardia perché un pezzo appeso
   segua sempre il proprio attacco attraverso il taglio dell'allungo: le tre restano rosse.
   Ho tolto la guardia, perché non guadagnava niente e cambiava la geometria di ogni tavola.
6. **Non è la finestra del riempimento.** L'ho neutralizzata in un albero di prova — `(0, 1)`
   al posto di `(0,45, 0,65)`, cioè nessuna spinta in nessuna delle due direzioni — e le tre
   restano rosse, identiche.
7. **Non è l'invariante di §C, e non è la cessione che non arriva.** Ho percorso la scala dei
   ripieghi a mano, una via per volta, cedendo **tutte** le catene insieme su due di loro:
   `improved`, `seeded` e `tutte cedute` falliscono sulla stessa tratta e con lo stesso
   errore; `senza le fasi`, `senza fasi tutte cedute` e `la disposizione di partenza`
   falliscono su un'**altra** tratta, e tutt'e tre con lo stesso errore fra loro. Le vie che
   non usano le fasi non hanno nemmeno l'invariante — `Improver` senza fase del tronco non
   ha autostrade da conservare — e falliscono lo stesso.

**Il conto finale, in due righe.** Una delle tre è la lunghezza uscita dal costo, e il punto
3 qui sopra la misura e la porta al PO. Le altre due sono che **il ciclo, con la gerarchia
nuova, atterra su una posa che il corredo non riesce più ad abitare**: restano rosse anche
con il costo di `main` rimesso per intero, su due fixture che erano già fragili prima —
delle prove di quel file, quattro erano rosse su `main` sulle stesse due. Rimetterle a posto
vuol dire lavorare sul **posizionamento** — `place.py` — o sulla scelta delle candidate, e
non è nel perimetro di `DRAW-012`: è la stessa famiglia della corsia di catena di §7.1,
vista su una fixture di prova invece che su un impianto.

**Non ho toccato quelle tre prove, e la terza è quella su cui ho esitato di più.** Per lei
l'argomento c'era, ed è lo stesso con cui ho riscritto le altre venti: «ogni millimetro oltre
il minimo peggiora il costo» è la riga 2 di `DRAW-005-R1` blocco E, e D-139 l'ha abolita.
**Non l'ho riscritta**, e voglio che si veda il perché.

Le altre venti asserivano un **metro** che il PO ha cambiato — un budget, una soglia, un
conto. Questa asserisce una **proprietà del disegno**: che un accessorio stia stretto a ciò
a cui appartiene. Il PO non l'ha mai abolita; ha abolito il costo che la teneva su, e
probabilmente senza sapere che ci fosse appesa. Riscriverla vorrebbe dire archiviare in
silenzio una qualità del disegno usando come pretesto una disposizione che parlava d'altro,
e farlo mentre il saldo della suite è la cosa che il PM guarda. Preferisco portarla rossa e
misurata: costa tre righe in un rapporto e non costa una regola.

Il saldo lo porto com'è: dieci rosse su `main`, tredici qui.
