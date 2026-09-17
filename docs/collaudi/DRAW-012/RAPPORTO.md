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
| | **dopo** | **45,4 %** | **0,734** | **41,6 %** |
| **2** | prima | 50,1 % | 0,625 | 41,3 % |
| | **dopo** | **66,7 %** | **0,719** | **57,8 %** |

**Il riempimento sale e la copertura sale con lui**, su tutt'e due le tavole: è
esattamente ciò che D-141 chiede di verificare prima di credere al primo numero. Se il
riempimento fosse salito con il trucco — un pezzo spinto in un angolo — la copertura
sarebbe scesa. Anche il terzo numero sale, e di più del primo: il guadagno non è di un
pezzo isolato.

### 3.2 Il metro nuovo: curve, attraversamenti, e la lunghezza come misura

| tavola | | curve | attraversamenti | lunghezza (misura, non giudizio) | squilibrio quadranti | ingombro |
|---|---|---|---|---|---|---|
| **1** | prima | 4 | 1 | 470,0 mm | 2,11 | 245 × 100 mm |
| | **dopo** | **4** | **1** | 782,5 mm | 2,43 | **325 × 115 mm** |
| **2** | prima | 5 | 1 | 600,0 mm | 32,5 | 257,5 × 160 mm |
| | **dopo** | **8** | **3** | 1132,5 mm | **5,04** | **337,5 × 162,5 mm** |

- **La tavola 1 non peggiora su nessuna voce di costo** e si allarga di ottanta millimetri.
- **La tavola 2 peggiora su curve e attraversamenti** (5 → 8, 1 → 3). Il criterio 14 lo
  ammette se il rapporto lo spiega con l'ordine nuovo, e la spiegazione è in §6.1: le tre
  linee che il criterio 1 nomina erano in ultima fase e adesso sono struttura, quindi si
  disegnano prima e si prendono la propria strada. Lo squilibrio fra i quadranti, che è la
  misura di «il disegno è tutto su un lato», passa da **32,5 a 5,0**.
- La **lunghezza cresce** su tutt'e due, ed è il segno che il metro è cambiato: il PO ha
  tolto i millimetri dal costo perché il disegno si tenesse largo, e il disegno si tiene
  largo.

---
## 4. La suite

### 4.1 Il saldo

| | `main` (`8589620`) | questa consegna |
|---|---|---|
| rosse | 10 | *(§5, criterio 13)* |
| verdi | 1470 | |
| saltate | 24 | |
| xfailed | 11 | |

Il riferimento di `main` l'ho misurato io, in un worktree pulito sulla testa di `main`, con
lo stesso interprete e lo stesso comando: non l'ho preso dal pacchetto. Combacia con quello
che il pacchetto dichiara.

### 4.2 Le cinque prove riscritte, e la disposizione che le supera

Nessuna è stata convertita in `skip` o `xfail`, nessuna soglia è stata allentata. Tutte e
cinque **asserivano una regola che il PO ha appena cambiato**, e riscriverle è l'unico modo
di non lasciarle a dire il falso.

| Prova | Che cosa diceva | Perché non lo dice più |
|---|---|---|
| `test_costo_peso.py::test_l_ordine_del_costo_e_quello_del_pacchetto` | le sette voci di costo, e la settima è `length_mm` | **D-139**: la lunghezza esce dalle voci. Adesso la prova verifica le sei voci e che la lunghezza resti **fuori** dalla chiave |
| `test_costo_peso.py::test_nessun_aumento_di_riempimento_compra_tubo_…` | il riempimento non compra **tubo**, pieghe, incroci, backtracking | **D-139**: il tubo non è più una moneta. Il resto dell'elenco resta, ed è il punto |
| `test_costo_peso.py::test_una_posa_compatta_batte_una_posa_equidistante` | «chi allunga il tubo perde» | **D-139**, alla lettera: «i mm non sono un vero parametro». Riscritta come `test_allontanare_le_macchine_non_costa_piu_tubo`: due pose che differiscono solo per il tubo sono **indifferenti**, e la misura si legge ancora |
| `test_riempimento_del_foglio.py::test_il_riempimento_non_si_compra_con_il_tubo` | la posa rivista non è mai **più lunga**, più piegata, più incrociata | **D-139**: può essere più lunga, e deve poterlo essere per entrare nella finestra. Curve e attraversamenti restano intoccabili |
| `test_riempimento_del_foglio.py::test_la_distensione_non_esiste_piu` | `length_mm` viene prima di `fill`, che viene prima di `imbalance` | **D-139**: l'ordine è cambiato. La prova verifica adesso che la lunghezza stia in fondo e che `key()` non la legga |

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

### 7 — La tavola 1 entra nella finestra; la tavola 2 ci resta · **raggiunto in parte**

**La tavola 1 entra**: 29,8 % → **45,4 %**, dentro la finestra, con la copertura salita a
0,734. È l'impianto su cui il pacchetto dice che il tenersi larghi si vede di più, e si
vede.

**La tavola 2 esce dall'altra parte**: 50,1 % → **66,7 %**, un punto e sette sopra il
tetto del 65 %. Non è un caso limite mascherato: il preflight la segna
(`SHEET_TOO_FULL`), e il rapporto la porta. §7.3 dice perché il costo non la riporta
dentro e che cosa lascio al PO.

### 8 — Lo stretch si usa davvero · **raggiunto**

```
.venv/bin/python docs/collaudi/DRAW-012/allungo.py docs/collaudi/DRAW-012/dopo/impianto1-completo.json

t1 su 420x297: 340 allunghi provati, 4 accettati
  accettato in fase «servizio» su tee-expansion-connection-collettore-ritorno-a
  accettato in fase «servizio» su tee-filling-unit-collettore-ritorno-a-b
  accettato in fase «servizio» su collettore-mandata
  …
    collettore-mandata: (82.5, 183.5) -> (177.5, 181)
    tee-valve-safety-collettore-mandata-b: (97.5, 183.5) -> (192.5, 181)
    pdc-master: (17.5, 181) -> (30, 178.5)
    pdc-slave: (17.5, 148.5) -> (30, 133.5)
    radiatori: (332.5, 178.5) -> (332.5, 176)
```

Le posizioni prima e dopo sono nell'output completo, in
`dopo/impianto1-allunghi.txt`: il collettore di mandata si sposta di novantacinque
millimetri lungo l'asse e si porta dietro il proprio corredo, e le macchine ai due capi si
allontanano. È il tronco che si allunga invece di piegarsi.

E in `improve.py` la mossa non pretende più che la tratta sia **già** dritta: era offerta
solo dove il problema non c'era. Misurato sul banco, l'impianto 4: centonovantotto
candidate provate e **nessun allungo fra loro**.

### 9 — Nessun impianto esce dal ripiego che scarta le fasi · **raggiunto**

```
impianto1-completo.json: … ripiego «le fasi» · cedute 0
impianto2-completo.json: … ripiego «le fasi» · cedute 0
```

Le due tavole che escono, escono dalla **prima** via. Nessuna cessione è stata necessaria.
Le tavole 3, 4 e 5 non escono da nessuna via — né qui né su `main` — e il criterio chiede in
quel caso di dire che cosa ha impedito la cessione graduale: la risposta è in §6.2 per la
4, e in §5, criterio 12, per le altre due. **In nessuno dei tre casi la cessione avrebbe
aiutato**, e non è una congettura: sull'impianto 4 ho provato a cedere **tutte** le catene
insieme, e l'esito non cambia — ciò che blocca non è un invariante di §C, è una corsia di
catena di macchina occupata da un'altra corsia.

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
- lo scambiatore sanitario sta **in centrale**, accanto al volano e non nella distribuzione
  (I-066);
- il riempimento è **48,9 %**, dentro la finestra, con copertura 0,766.

Su `main` la stessa lettura non si può fare: la tavola 4 non esce né completa né grezza,
perché la fase del tronco non muoveva un pezzo.

### 11 — Il caso di prova 4 è riscritto, e la commutatrice è in catalogo · **raggiunto**

`examples/prova/prova-4-ibrido-pdc-caldaia.json` è il grafo di D-137, collegamento per
collegamento; il generatore che lo produce è `examples/prova/build_test_plants.py`, e la
prova `tests/catalog/test_generated_fixtures.py` verifica che i due combacino.

La commutatrice è `examples/layout/catalog/switching-valve-3way.json`, funzione
`circuit_switching`, due ingressi e un'uscita, con i propri due stati idraulici; il simbolo
è `assets/symbols/switching-valve-3way.{json,svg}`; la famiglia è **VC** in
`naming/families.json`. Tutti e tre sono **generati**, non scritti a mano.

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

- **3**: `run stub-expansion-connection-pdc-water-return-a is 5mm long but its 1 inline
  accessories need 7.5mm` — uno stacco di servizio troppo corto per l'organo che porta.
  Su `main` si fermava prima, sull'instradamento di una tratta del riscaldamento;
- **4**: due corsie di catena di macchina che si incrociano (§6.2);
- **5**: `run s4-a … the 5 straight steps the chain needs beyond the port at (137, 65) run
  into an obstacle at (140, 65)` — la stessa specie del 4.

### 13 — Il saldo della suite non peggiora · *(§4.1)*

### 14 — Le tavole 1 e 2 misurate con il metro nuovo, prima e dopo · **raggiunto** *(§3)*

### 15 — Determinismo: doppia generazione con la stessa impronta · **raggiunto**

```
.venv/bin/python -m disegnatore_mep draw …  (due volte, cartelle diverse)
```

Impronte della geometria, due generazioni indipendenti dalla CLI:

| tavola | prima generazione | seconda generazione |
|---|---|---|
| 1 | `b4b8bdbfd156cea9f04aa248…` | `b4b8bdbfd156cea9f04aa248…` |
| 2 | `ea1012bd7f907aaa62695c2c…` | `ea1012bd7f907aaa62695c2c…` |

Le due generazioni scrivono in cartelle diverse e si confrontano sulle geometrie esportate,
non sui file: è l'impronta della tavola, non quella del testo.

### 16 — Il documento dell'11 settembre è aggiornato · **raggiunto**

`docs/pm/2026-09-11-architettura-della-posa-a-fasi.md`: §3 è riscritto all'ordine di D-138 e
porta accanto, in citazione, ciò che ha sostituito; §4 è precisato nei due punti che
`DRAW-012` §C tocca. §1, §2, §5 e §6 restano intatti, e l'intestazione dice quali.

---

## 6. Quello che ho visto guardando le tavole

Il pacchetto lo chiede prima di aprire la PR, e `I-064` lo ha reso una regola del metodo:
«prima verifica visivamente la tavola». Ecco che cosa vedo, nell'ordine in cui lo vedo.

### 6.1 La tavola 2: la struttura c'è, e si vede. Due difetti nuovi

**Quello che è migliorato, e non è un numero.** Prima la tavola 2 era un grumo largo
257,5 mm in mezzo al foglio, con il bollitore buttato in basso e il prelievo sanitario che
tornava **verso sinistra** in alto. Adesso ci sono due rette parallele che attraversano il
foglio da parte a parte — la mandata rossa sopra, il ritorno blu sotto — e tutto il resto vi
si appende: il volano, il circolatore, il ventilconvettore stanno **sulla** mandata, non
accanto. È la figura che il PO descrive dal 10 settembre, e che nessuna consegna aveva
ancora prodotto. Lo squilibrio fra i quadranti lo conferma senza che nessuno lo inseguisse:
**32,5 → 5,0**.

**Due difetti nuovi, e li dico io perché i numeri da soli non li direbbero.**

1. **L'uscita ACS attraversa la mandata.** Il prelievo sanitario sta in cima e la linea
   arancione che lo raggiunge taglia la mandata rossa poco prima del volano. Prima non
   attraversava. È uno dei tre attraversamenti nuovi, e il preflight lo segna anche come
   tratta con **quattro pieghe** (`RUN_WITH_TOO_MANY_BENDS`). La causa è §B: l'uscita ACS è
   adesso di rango massimo e si instrada **presto**, quando la mandata non c'è ancora, e
   quando la mandata arriva le passa sopra. Non è un difetto della classificazione — la
   classificazione è quella che il PO ha chiesto — è che l'ordine di instradamento e il
   rango sono la stessa chiave, e adesso quella chiave è più grossa. È il primo filo di §7.

2. **Curve e attraversamenti peggiorano** (5 → 8 e 1 → 3). Il pacchetto lo ammette
   esplicitamente al criterio 14 — «un peggioramento su curve o attraversamenti è ammesso
   se il rapporto lo spiega con l'ordine nuovo» — e la spiegazione è quella qui sopra: le
   tre linee che erano in ultima fase adesso sono struttura, e la struttura si disegna
   prima. Non lo presento come un buon numero: lo presento come il prezzo dichiarato.

### 6.2 La tavola 4: la struttura c'è, la tavola no

La fase del tronco adesso **posa davvero** l'impianto 4 — ventidue pezzi su ventidue si
muovono, dove prima non se ne muoveva **nessuno** — e la posa sta dentro il foglio. La
tavola però non esce, e il motivo è locale e misurabile: **due corsie di catena di macchina
si incrociano**.

- la deviatrice della caldaia è a `(130, 186)` e la sua uscita `out_a` è a `(140, 191)`: la
  catena che le sta davanti — il ritegno della caldaia e il proprio organo di chiusura —
  pretende cinque passi di rettilineo verso destra;
- la commutatrice del ritorno è a `(142.5, 196)`, girata di mezzo giro, e il suo secondo
  ingresso guarda in alto: la **sua** catena pretende il rettilineo verso l'alto, e passa
  per `(147.5, 191)`;
- quella cella è dentro tutt'e due i rettilinei, e un rettilineo di catena è **riservato**:
  chi ci passa sopra non fa fallire sé stesso, fa fallire l'altra catena.

Il ciclo non se ne tira fuori: esaurisce le proprie candidate — le ho contate, sono
centonovantotto sulla posa e nessuna le libera — perché **nessuna mossa di un pezzo solo**
allontana due corsie perpendicolari che si incrociano vicino all'origine di entrambe. Non è
un vincolo di §C: ho provato a cedere **tutte** le catene insieme, e l'esito non cambia.

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

### 7.1 L'ordine di instradamento e il rango sono la stessa chiave, e adesso è grossa

`compose_drawing.place_in_line` ordina le tratte per **rango** — «prima le autostrade», che
è la regola di `DRAW-008` — e a parità mette davanti quelle che portano una catena di
macchina. Con §B il rango massimo non è più il solo circuito dei generatori: ci finiscono la
distribuzione, l'uscita ACS e le linee di **ogni** generatore. Dentro quella classe, adesso
grande, l'ordine lo decide uno spareggio che non è stato pensato per governarla, e si vede
in tre posti: l'ACS che attraversa la mandata sulla tavola 2 (§6.1), la mandata del secondo
generatore che va per conto suo sulla tavola 1 (§6.3), e la corsia di catena occupata da
altri sulla tavola 4 (§6.2).

**Ho provato la strada più ovvia** — servire prima le tratte **rigide**, quelle che portano
una catena, e solo dopo guardare il rango — e l'ho misurata: sull'impianto 4 non cambia
l'esito, sulla tavola 1 non cambia una coordinata. **Non l'ho consegnata**: cambierebbe
l'ordine di instradamento di ogni tavola senza un guadagno che si veda, e una modifica così
va decisa, non infilata. La riga è `compose.py`, e il commento la nomina.

### 7.2 Due corsie di catena che si incrociano non le risolve nessuna mossa di un pezzo

È il blocco della tavola 4 (§6.2), ed è una specie di difetto che il ciclo non sa affrontare:
le candidate spostano **un pezzo** o un blocco rigido, e qui servirebbe allontanare due
corsie perpendicolari che nascono a sette millimetri e mezzo l'una dall'altra. Le strade che
vedo, in ordine di quanto costano:

1. **girare la commutatrice** invece di traslarla, così che il suo secondo ingresso non
   guardi dentro la corsia della deviatrice: le rotazioni sono già fra le candidate, ma
   arrivano dopo, e il ciclo si ferma prima per esaurimento delle proprie prove;
2. far sì che una corsia di catena, quando è **riservata da un'altra**, chieda al ciclo di
   allontanare i due capi invece di fallire: sarebbe lo stretch applicato a una corsia, ed è
   §E letto un passo più in là di come il pacchetto lo scrive;
3. rivedere **quale posizione** la fase del tronco dà alla commutatrice, che oggi è quella
   di un pezzo qualunque del tronco.

Sono tre pacchetti diversi e nessuno è una taratura: li lascio al PM invece di sceglierne
uno da solo.

### 7.3 La finestra e la tavola 2

La tavola 2 esce dalla finestra dall'alto (66,7 % contro 65 %). Il riempimento è l'ultima
voce di costo prima dello spareggio: sopra di lei stanno le curve e gli attraversamenti, e
riportare il disegno dentro la finestra vorrebbe dire stringerlo, cioè pagare in curve.
Il costo, correttamente, non lo fa. Due letture possibili, e la scelta è del PO:

- **la finestra è giusta e la tavola 2 va stretta**: allora serve una mossa che restringa
  senza piegare, che oggi non esiste (lo stretch sa solo allargare);
- **il tetto del 65 % è tarato su tavole più piccole**: la tavola 2 di oggi occupa 337,5 mm
  di larghezza contro i 257,5 di prima, ed è esattamente il «tenersi larghi» che D-138
  chiede. Un punto e sette sopra il tetto, con la copertura salita e lo squilibrio sceso da
  32,5 a 5,0, potrebbe voler dire che il tetto va guardato di nuovo sulle tavole nuove —
  che è quello che D-140 stessa dice di fare con una taratura.

Non propongo di cambiare il numero: è del PO, e l'ho lasciato dov'è.

### 7.4 Il tempo che ci vuole

Togliere la lunghezza dal costo rende **indifferenti** molte pose che prima si ordinavano, e
il ciclo ne prova di più prima di fermarsi: la suite passa da circa trentasei minuti a circa
cinquanta. Non ho alzato nessun tetto di ricerca — sono quelli di sempre — e non ho tolto
prove. Lo segnalo perché è un costo che il PM paga a ogni verifica.

