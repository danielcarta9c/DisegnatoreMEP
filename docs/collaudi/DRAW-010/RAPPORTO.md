# RAPPORTO DI CONSEGNA — DRAW-010

**Pacchetto:** `ACTIVE_WORK_PACKAGE.md` — «Il tronco posa senza pezzi addosso, e
l'impianto 4 torna a uscire»
**Ramo:** `claude/adoring-albattani-lpghbr` — quello che la piattaforma ha
assegnato alla sessione; il pacchetto non ne prescrive uno
**Commit di partenza:** `af6fad8`, testa di `main` all'apertura della sessione
(`DRAW-010: il commit di partenza è la testa di main, senza SHA`, PR #30)
**Ambiente:** ricostruito con `scripts/setup-env.sh`; Python 3.11.15

---

## 0. Le sei cose da leggere prima di tutto il resto

1. **L'impianto 4 torna a uscire, e l'impianto 2 continua a uscire dalla propria
   posa a fasi.** Sono i criteri 4 e 5, e sono chiusi. Gli impianti che si
   compongono passano da due a tre.
2. **La causa dell'anello è misurata, non ipotizzata**, e la cura non è la mossa
   che separa ma **che cosa le si dà da spostare**: non il sottoalbero oltre una
   tratta — su un anello non ne esiste uno — ma il **gruppo** che i vincoli
   d'asse tengono insieme, con tutto ciò che le campate gli obbligano dietro.
   §2.1 e criterio 2.
3. **La posa che la fase del tronco consegna è pulita su tutt'e tre le tavole
   che escono**: zero coppie sovrapposte e zero coppie più vicine dello stacco
   ammesso, dove la tavola 2 ne aveva 1 e 8. Criterio 1.
4. **Una premessa del pacchetto non si riscontra sulla base**, e va detto
   subito: §B.2 dà per assodato che «oggi la tavola 2 esce dal terzo ripiego di
   `compose_sheet`». Misurato sul commit di partenza, il ripiego **non scatta
   affatto**: la tavola 2 esce dal primo tentativo, quello della catena a fasi
   (§3.5). Il criterio 5 era quindi già soddisfatto alla partenza, e la consegna
   lo mantiene.
5. **Tre criteri non sono raggiunti, e sono dichiarati con la misura**: il 13 (la
   tavola 2 peggiora su incroci e lunghezza), il 15 (il saldo della suite
   peggiora: otto rosse nuove contro quattro chiuse) e la seconda metà dell'8
   (`utenze` resta posato con la bocchetta verso il basso, mentre la sua tratta
   passa da una piega a **zero**). §6 li porta uno per uno con il numero che li
   prova, e §7 mette al PM le due decisioni che ne discendono.
6. **Nessuna prova è stata convertita in `skip` o `xfail`, nessuna soglia è stata
   allentata, nessuna fixture è stata toccata per far passare una prova.** I
   quattro artefatti rigenerati (§5) sono documenti che la catena **riscrive**
   da sé e che una prova pretende identici alla rigenerazione: non toccarli
   avrebbe voluto dire consegnare un documento vecchio spacciato per attuale.

---

## 1. Ramo, commit, file

| | |
|---|---|
| **Ramo** | `claude/adoring-albattani-lpghbr` |
| **Base** | `af6fad8` (testa di `main`) |
| **Altri rami con lavoro non riportato** | nessuno: `git branch -a` elenca `main` e questo ramo soltanto |

### File del motore

| file | che cosa cambia |
|---|---|
| `src/disegnatore_mep/layout/spine.py` | §A: la compattazione del tronco — che cosa si muove, quanto, e in che verso; la posa non esce più dal foglio; una figura appesa finita addosso a un'altra si allontana lungo il proprio stacco; un confine di rete non si rigira dietro lo stacco |
| `src/disegnatore_mep/layout/place.py` | §D.1: la giacitura di un confine di rete e la gamba del suo gomito; lo stacco che porta **due** accessori in linea conta anche il franco di estremità |
| `src/disegnatore_mep/layout/improve.py` | §E: `is_valid` torna stretta |
| `src/disegnatore_mep/assembly/runs.py` | §D.3: chi ordina gli accessori conta anche ciò che un composito si porta a bordo, e «attaccato alla macchina» cede a un vincolo dichiarato |

### Prove

| file | che cosa |
|---|---|
| `tests/layout/test_anello_del_tronco.py` | **nuovo**: la positiva e la negativa del criterio 3, su un anello costruito apposta |
| `tests/rules/test_ordine_semantico.py` | **aggiunta**: la prova generale del criterio 10 |
| `tests/layout/test_rami_di_servizio.py` | §D.2: la regola della freccia sotto la lunghezza minima |
| `tests/layout/test_accessori_appesi.py` | §C: `COMPONIBILI` e `NON_COMPONGONO` |

### Documenti rigenerati dalla catena (§5)

`docs/prodotto/GRAFO_IMPIANTO.md`, `docs/prodotto/grafi-di-prova/prova-2`, `-3`,
`-5`, `examples/rules/centrale-pdc-completa.json`.

### Strumenti di misura consegnati

Tutti in `docs/collaudi/DRAW-010/`, con l'uscita grezza in `misure/`:

- `le-coppie-addosso.py` — le coppie addosso nella posa che la fase consegna
  (criterio 1). Usa solo funzioni pubbliche, così misura **base e ramo con lo
  stesso file**;
- `perche-l-anello-non-separava.py` — il diario di `_relieve`: la mossa di prima,
  le candidate di adesso, e perché ciascuna si scarta (criterio 2);
- `il-ripiego.py` — quante volte scatta il ripiego di `compose_sheet`, impianto
  per impianto e formato per formato (criterio 5);
- `chi-compone.py` — chi compone, sul contratto della suite e dalla CLI
  (criteri 7 e 16);
- `la-catena-fredda.py` — la fila degli accessori sull'acqua fredda, e da che
  parte sta lo scarico (criterio 10);
- `il-prelievo-acs.py` — la giacitura di ogni confine di rete e le pieghe della
  sua tratta (criterio 8).

---

## 2. Che cosa è stato fatto, e perché così

### 2.1 §A — l'anello non dà un sottoalbero, e il sottoalbero non serve

La compattazione della fase del tronco allontana due partecipanti che si trovano
addosso spostandone uno lungo l'asse, mai di traverso. Fino a DRAW-009 quello
che si spostava era il **sottoalbero oltre la tratta** che porta al più lontano
dei due: su un albero è un insieme che si stacca, su un anello no. `_beyond`
camminava in ampiezza dal vicino e senza fermarsi mai, tornava indietro
dall'altro capo e si portava dentro anche l'ancora; la guardia «l'ancora sta nel
blocco» scartava allora **tutte e due** le candidate, `_push_apart` tornava
`False` alla prima coppia, e `_relieve` si fermava lì.

Due cose sono cambiate, e nessuna è una soglia:

1. **Che cosa si muove lo dicono i vincoli, non la topologia.** Su un asse, una
   retta dell'altro asse tiene insieme un **gruppo** — è la stessa lettura che
   `_solve_axis` usa per risolvere l'asse — e fra gruppi valgono le campate, che
   sono disuguaglianze con un verso. Spostare in avanti un gruppo **con tutti
   quelli che gli stanno oltre**, o all'indietro un gruppo con tutti quelli che
   gli stanno prima, allunga le campate al confine e non ne accorcia nessuna:
   nessuna retta si piega, nessuna tratta che era rettilinea diventa storta, e
   ogni tratta conserva almeno il rettilineo che pretende. È lo stretch del PO,
   applicato a un anello.
2. **Una coppia che non si separa non ferma le altre.** Prima la prima coppia
   irriducibile chiudeva la compattazione, e sulla tavola 2 era la prima in
   ordine: il resto non veniva nemmeno guardato.

Due cose si sono aggiunte strada facendo, tutt'e due misurate:

3. **Il foglio viene prima della prima ipotesi.** `_solve_axis` sceglie, fra le
   soluzioni che rispettano le campate, quella più vicina alla posa di partenza.
   È la scelta giusta finché ci sta; quando porta il disegno **oltre il bordo**
   non è una soluzione, perché chi segue il tronco esce dal foglio con lui e una
   tratta oltre il bordo non si instrada — sulla tavola 2 erano i
   ventilconvettori, trentacinque millimetri fuori. Allora si prende la
   soluzione compatta, che rispetta le stesse campate.
4. **Chi pende si allontana lungo il proprio stacco.** `place.hanging_place` lo
   fa già quando posa per la prima volta; poi però la fase del tronco sposta il
   tronco e `carry_the_rest` riappende le figure a un pezzo che sta altrove, e
   nessuno guardava se il posto fosse ancora libero. Così lo scarico del volano
   finiva dentro il bollitore e il prelievo dentro il volano. La regola è quella
   della posa, applicata alla posa nuova. Dove lungo lo stacco non c'è posto —
   capita quando il tronco ha impilato due macchine e la figura dell'una è finita
   dentro l'altra — si scorre **di traverso**, che a uno stacco di servizio costa
   una piega: è ciò che il PO ha detto di accettare («quelle sì, accettiamo
   qualche curva in più»), e un pezzo dentro un altro no.

### 2.2 §D.1 — un confine di rete non ha una giacitura propria, ce l'ha la lettura

Il prelievo si posa come un ingresso: pende dal pezzo che serve, e la sua
giacitura non la decide il pezzo che lo regge ma la **lettura**, che va da
sinistra a destra. L'impianto sta a destra di un ingresso e a sinistra di un
prelievo, e l'attacco del confine guarda l'impianto: a destra per l'ingresso, a
sinistra per il prelievo. Non è un elenco di nomi: è la funzione dichiarata dal
catalogo (`boundary`) e il verso del suo unico attacco.

Ne discendono due cose:

- **il gomito vuole la propria gamba**: dove l'attacco dell'appeso non guarda in
  faccia lo stacco — il prelievo sta di lato, il bollitore manda la linea in su
  dalla faccia superiore — la tratta gira una volta, ed è il gomito che il PO ha
  detto di tenere; sedersi alla quota dello stacco lo lascerebbe senza gamba e
  il rettilineo che la catena pretende appena fuori dalla porta non ci starebbe;
- **un confine non si rigira dietro lo stacco** quando `carry_the_rest` lo
  riappende: segue il proprio stacco di pura traslazione.

Il ciclo di miglioramento, invece, **lo rigira**: §6.3 lo misura, e il conto di
impedirglielo è lì.

### 2.3 §D.3 — «a bordo» conta, e il posto attaccato alla macchina cede a un vincolo dichiarato

La cura che il PM ha prescritto è che chi ordina gli accessori conti anche ciò
che un composito si porta dentro il mantello. È stata scritta così: `Piece` porta
un campo `on_board` letto da `carries_on_board`, e `_sorted` confronta
`functions | on_board` contro i `before`/`after` dichiarati.

**Del pezzo stesso, non di ciò che gli pende.** Il piede di uno stacco parla per
l'accessorio che ci pende e ne prende il mestiere — è il servizio che lo stacco
offre alla tratta — ma gli organi che quell'accessorio ha **dentro** restano
sullo stacco e non chiudono niente sulla tratta. Contarli spostava il corredo del
ritorno dietro al piede del riempimento, e la prima stesura lo faceva: è stato
trovato dalla suite e corretto.

**E una seconda riga, che la cura rende necessaria.** Con `carries_on_board`
contato, `let-what-holds-its-own-volume-empty` e
`safety-group-on-the-stored-volume` si contendono lo stesso posto: la prima vuole
lo scarico dal lato del serbatoio rispetto all'organo che chiude, la seconda
dichiara `against_the_anchor`, cioè «fra me e la macchina non ci va nessun altro
pezzo». La contraddizione era nascosta: `_sorted` dava il posto all'ancorato
**prima** di guardare i vincoli, e il conflitto non si vedeva. Adesso
`against_the_anchor` resta la preferenza più forte fra i pezzi liberi
dell'ordinamento, ma **cede a un vincolo dichiarato** invece di scavalcarlo in
silenzio. Dove nessun vincolo lo contende — le tre valvole di sicurezza — il
posto attaccato alla macchina resta suo; il piede di uno stacco non chiude
niente, quindi la via di sfogo che quel vincolo difende resta aperta.

**Questa seconda riga non è nel testo di §D.3.** È la conseguenza necessaria
della cura che §D.3 prescrive, senza la quale il criterio 10 non si chiude: con
il solo `carries_on_board` l'ordine non cambia di una riga, misurato. La
segnalo qui e in §7.1 perché il PM la veda come una scelta e non come un
dettaglio.

### 2.4 Lo stacco che porta due accessori, e il franco che nessuno contava

`stub_minimum_mm` calcolava la lunghezza di uno stacco come la fila dei suoi
accessori più la soglia delle due porte. Chi poi li siede — `inline.py` — non li
mette mai a ridosso del capo della tratta: vuole il proprio franco di estremità.
Finché uno stacco portava **un** accessorio solo la differenza non si vedeva,
perché al pezzo restava tutto il tratto per scorrere; con **due** la fila è
rigida, e uno stacco lungo esattamente quanto la fila è uno stacco su cui la fila
non ci sta.

Si è visto perché §D.3 mette l'intercettazione e il gruppo di sicurezza
sanitario sulla **stessa** tratta: lo stacco dell'acquedotto chiedeva 27,5 mm e
`inline.py` ne voleva 32,5, e la tavola 2 non usciva. Da due accessori in su lo
stacco conta anche quel franco. È un difetto antecedente che §D.3 ha scoperto, e
sta qui perché il PM lo veda: §7.2.

### 2.5 §E — il cancello torna stretto, e non costa niente

Fatto §A, la regola monotona non serve più. La riga è tornata quella che era:
nessuna candidata lascia due pezzi addosso. Il conto è stato fatto con lo
strumento che il pacchetto nomina, e dice due cose (§4.6): la prova di DRAW-007
torna verde, e sul banco della traslazione di blocco **la regola stretta e quella
monotona danno la stessa classifica** — quindi §E non costa niente. Ciò che
cambia il banco è §A, che gli toglie due delle tre coppie sovrapposte da cui
partiva.

---

## 3. I sedici criteri, uno per uno

Ogni criterio porta il comando e la sua uscita. Le uscite lunghe stanno per
intero in `docs/collaudi/DRAW-010/misure/`, e qui se ne riporta la parte che
chiude il criterio.

### 3.1 Criterio 1 — la posa della fase del tronco non ha coppie addosso — **RAGGIUNTO**

```
$ .venv/bin/python docs/collaudi/DRAW-010/le-coppie-addosso.py 2
```

| tavola 2 | base `af6fad8` | ramo |
|---|---|---|
| coppie che si sovrappongono davvero | **1** (`bollitore` ↔ `volano`) | **0** |
| coppie più vicine dello stacco ammesso | **8** | **0** |

Uscita del ramo:

```
== impianto 2 — prova-2-pdc-deviatrice-acs.json
   la fase del tronco ha consegnato una posa: True
   coppie che si sovrappongono davvero     : 0
   coppie piu' vicine dello stacco ammesso : 0
```

Uscita della base (stesso file, eseguito nel worktree della base con
`PYTHONPATH="$PWD/src"`, come la nota di metodo prescrive):

```
== impianto 2 — prova-2-pdc-deviatrice-acs.json
   la fase del tronco ha consegnato una posa: True
   coppie che si sovrappongono davvero     : 1
       bollitore <-> volano
   coppie piu' vicine dello stacco ammesso : 8
       acquedotto <-> tee-pressure-gauge-pdc-water-return
       bollitore <-> drain-connection-volano-primary-in
       bollitore <-> volano
       deviatrice <-> tee-expansion-connection-pdc-water-return
       drain-connection-cold-bollitore-cold-in <-> ritorno
       drain-connection-cold-bollitore-cold-in <-> tee-pressure-gauge-pdc-water-return
       ritorno <-> tee-drain-connection-cold-bollitore-cold-in
       tee-drain-connection-cold-bollitore-cold-in <-> tee-pressure-gauge-pdc-water-return
```

Il numero della base coincide con quello che il pacchetto dichiara (1 e 8) e con
la misura del PM sul verdetto della PR #27.

Le altre tavole, dalla stessa esecuzione (`misure/coppie-prima.txt` e
`misure/coppie-dopo.txt`):

| impianto | base sovrapposte / vicine | ramo sovrapposte / vicine |
|---|---|---|
| 1 | 0 / 0 | **0 / 0** |
| 2 | 1 / 8 | **0 / 0** |
| 3 | 0 / 2 (la fase non consegna una posa) | 0 / 2 (idem) |
| 4 | 0 / 5 | **0 / 0** |
| 5 | 4 / 21 | la posa iniziale non arriva più alla fase (§6.4) |

### 3.2 Criterio 2 — perché l'anello impediva la separazione — **RAGGIUNTO**

```
$ .venv/bin/python docs/collaudi/DRAW-010/perche-l-anello-non-separava.py 2
```

Uscita, sulla coppia che la tavola 2 presenta (`misure/anello-dopo.txt` per
intero):

```
   coppia addosso: bollitore <-> volano
     la mossa di prima (DRAW-009):
       candidata «sposta volano»: allunga la campata deviatrice.out_a -> volano, verso right
         sottoalbero di _beyond (8): volano, ritorno, bollitore, tee-pressure-gauge-pdc-water-return,
           tee-filling-unit-pdc-water-return-b, tee-expansion-connection-pdc-water-return, pdc,
           tee-valve-safety-pdc-water-supply
         SCARTATA — l'ancora bollitore sta nel sottoalbero: l'anello lo riporta dentro, e spostarlo
           porta dietro tutti e due senza separarli
       candidata «sposta bollitore»: allunga la campata deviatrice.out_b -> bollitore, verso bottom
         sottoalbero di _beyond (8): bollitore, ritorno, volano, tee-pressure-gauge-pdc-water-return,
           tee-filling-unit-pdc-water-return-b, tee-expansion-connection-pdc-water-return, pdc,
           tee-valve-safety-pdc-water-supply
         SCARTATA — l'ancora volano sta nel sottoalbero: l'anello lo riporta dentro, e spostarlo
           porta dietro tutti e due senza separarli
     la mossa di adesso (DRAW-010):
       x avanti    «sposta bollitore»: AMMESSA — scorre 60 mm, blocco (1): bollitore
       x indietro  «sposta bollitore»: AMMESSA — scorre 10 mm, blocco (8): pdc, bollitore, ...
       x avanti    «sposta volano»: AMMESSA — scorre 10 mm, blocco (1): volano
       x indietro  «sposta volano»: AMMESSA — scorre 60 mm, blocco (8): pdc, volano, ...
       y avanti    «sposta bollitore»: AMMESSA — scorre 30 mm, blocco (1): bollitore
       y indietro  «sposta bollitore»: SCARTATA — l'ancora volano e' nel blocco (9 pezzi)
       y avanti    «sposta volano»: SCARTATA — l'ancora bollitore e' nel blocco (9 pezzi)
       y indietro  «sposta volano»: AMMESSA — scorre 30 mm, blocco (8): pdc, volano, ...
     esito: separati — bollitore (+0, +30)
```

Si legge tutto lì dentro:

- **le due candidate che `_relieve` generava**, e per ciascuna il sottoalbero che
  `_beyond` calcolava: **otto pezzi su nove**, cioè tutto il tronco meno il
  pezzo da cui si parte. Su un anello la camminata rientra dall'altro capo;
- **perché ciascuna si scartava**: l'ancora è dentro il blocco, quindi spostarlo
  porta dietro tutti e due e non li separa. Vale da qualunque dei due capi si
  parta, ed è il motivo per cui non ne restava nessuna;
- **le otto candidate di adesso**, con il blocco e lo scorrimento di ciascuna.
  Due si scartano per la stessa ragione — sull'asse y i due stanno nello stesso
  gruppo o uno tira l'altro — e sei sono ammesse;
- **quale vince e perché**: `bollitore (+0, +30)`. Non è la più corta — sull'asse
  x ce n'erano due da 10 mm — ma è l'unica che non allarga il disegno oltre il
  bordo del foglio: la tavola 2 occupa 335 mm su 350 in larghezza e settantacinque
  su 235 in altezza.

### 3.3 Criterio 3 — la prova generale e la negativa — **RAGGIUNTO**

`tests/layout/test_anello_del_tronco.py`, cinque prove su un anello costruito
apposta (deviatrice → volano/bollitore → raccordo di ritorno → macchina).

```
$ .venv/bin/python -m pytest tests/layout/test_anello_del_tronco.py -q
.....                                                                    [100%]
5 passed in 2.70s
```

- `test_il_tronco_di_questo_impianto_e_un_anello` — la guardia: senza anello le
  altre non direbbero niente;
- `test_su_un_tronco_ad_anello_la_separazione_trova_una_mossa` — **la positiva**.
  Verifica anche, rifacendo il calcolo di `_beyond`, che su quell'anello il
  sottoalbero contenesse l'ancora da tutti e due i capi: la prova non dice solo
  che adesso funziona, dice **perché prima no**;
- `test_una_separazione_che_piegherebbe_il_tronco_e_rifiutata` — **la negativa**.
  Costruisce la mossa comoda — spostare il solo pezzo addosso, dove una retta lo
  tiene insieme ad altri — mostra che romperebbe quella retta, e mostra che la
  separazione vera non ne rompe nessuna;
- `test_il_blocco_che_si_muove_e_sempre_un_insieme_di_gruppi[0,1]` — la forma
  generale della negativa: nessun blocco spezza mai un gruppo, su tutti e due gli
  assi, per ogni partecipante e per tutti e due i versi. È la proprietà da cui
  discende che la separazione non può piegare il tronco.

### 3.4 Criterio 4 — l'impianto 4 produce una tavola — **RAGGIUNTO**

Stessa riga di comando con cui oggi fallisce, cioè quella di
`scripts/tavole-di-verifica.sh`:

```
$ bash scripts/tavole-di-verifica.sh docs/collaudi/DRAW-010/dopo
...
== prova-4-ibrido-pdc-caldaia
docs/collaudi/DRAW-010/dopo/prova-4-ibrido-pdc-caldaia-t1.pdf (420x297 mm)
docs/collaudi/DRAW-010/dopo/prova-4-ibrido-pdc-caldaia-t1.png (3176x2248 px, 420x297 mm)
```

Sulla base, con lo stesso comando:

```
== prova-4-ibrido-pdc-caldaia
   la tavola non esce: the plant does not fit on any ordinary sheet format: run s3-a on
   network secondario cannot be routed: no route from (147, 70) to (116, 76): the 6 straight
   steps the chain needs beyond the port at (116, 76) run into an obstacle at (118, 76)
```

La tavola è in `docs/collaudi/DRAW-010/dopo/prova-4-ibrido-pdc-caldaia-t1.pdf`
(e `.svg`, `.png`), con la geometria e le misure accanto. Il pacchetto grafico
`prima/` porta, per lo stesso impianto, il solo `-preflight.txt` con l'errore: là
la tavola non esiste.

### 3.5 Criterio 5 — la tavola 2 esce dalla propria posa a fasi — **RAGGIUNTO, e una premessa da correggere**

```
$ .venv/bin/python docs/collaudi/DRAW-010/il-ripiego.py
```

| impianto | ripiego, base | ripiego, ramo |
|---|---|---|
| 1 | 0 (A3) | **0** (A3) |
| 2 | 0 (A3) | **0** (A3) |
| 3 | 5, la tavola non esce | 5, la tavola non esce |
| 4 | 5, la tavola non esce | **2**, la tavola esce |
| 5 | 5, la tavola non esce | 0 chiamate: la posa si ferma prima (§6.4) |

Uscita del ramo per la tavola 2:

```
== impianto 2 — prova-2-pdc-deviatrice-acs.json
   la tavola esce su 420x297, 1 foglio/i
   297x210 / tavola t1: il ripiego scatta 0 volte
   420x297 / tavola t1: il ripiego scatta 0 volte
     0. il ciclo sulle fasi: si instrada
```

**La premessa di §B.2 non si riscontra.** Il pacchetto scrive «Oggi esce dal
terzo ripiego di `compose_sheet` (rischio 16)». Misurato sul commit di partenza
con lo stesso strumento, il ripiego **non scatta**: la tavola 2 esce dal primo
tentativo, quello della catena a fasi. Era vero al tempo di DRAW-009 (§6.4 di
quel rapporto), e sulla testa di `main` non lo è più. Il criterio resta chiuso —
la tavola 2 esce dalla propria posa a fasi — ma non c'era niente da riparare, e
il PM deve saperlo perché il rischio 16 va riletto (§7.4).

Sull'impianto 4 il ripiego lavora ancora due volte: la catena a fasi e la posa
seminata cadono tutt'e due su `s3-a`, e la tavola esce dal ciclo senza le fasi.
È una tavola che il ripiego salva, ed è dichiarato.

### 3.6 Criterio 6 — l'impianto 3 è misurato — **MISURATO, non esce**

```
$ .venv/bin/python docs/collaudi/DRAW-010/il-ripiego.py 3
== impianto 3 — prova-3-pdc-diretta-pavimento.json
   la tavola NON esce: the plant does not fit on any ordinary sheet format: run p6-a on
   network riscaldamento cannot be routed: no route from (85, 66) to (3, 56): the 6 straight
   steps the chain needs beyond the port at (3, 56) run into an obstacle at (-1, 56)
   420x297 / tavola t1: il ripiego scatta 5 volte
     0. il ciclo sulle fasi: cade: run p6-a ...
     1. la posa seminata dalla fase del tronco: cade: run p6-a ...
     2. il ciclo senza le fasi: cade: run p6-a ...
     3. la disposizione di partenza: cade: run p6-a ...
     4. l'ultima prova: cade: run p6-a ...
```

**Dove si ferma, e perché.** Sulla tratta `p6-a` — il ritorno del pavimento
radiante — la catena di macchina pretende **sei passi dritti oltre la porta** a
`(3, 56)`, e l'ostacolo che trova è a `(-1, 56)`: una coordinata **negativa**,
cioè fuori dall'area di disegno. La porta sta a tre celle dal bordo sinistro e il
rettilineo che la sua catena esige non ci sta fisicamente. Non è una questione di
pesi né di instradatore: è il pezzo che sta troppo vicino al bordo.

Tutti e quattro i tentativi di `compose_sheet` cadono sullo stesso punto, il che
dice che non è una posa sfortunata ma la disposizione di partenza. §A non lo
tocca, perché per l'impianto 3 la fase del tronco **non consegna nemmeno una
posa** (`le-coppie-addosso.py 3`: «la fase del tronco ha consegnato una posa:
False»), sia sulla base sia sul ramo.

L'errore è identico, carattere per carattere, a quello della base — salvo le
coordinate del capo di partenza, che si spostano con la posa. La linea di
partenza non è cambiata.

### 3.7 Criterio 7 — `COMPONIBILI` elenca tutti quelli che compongono — **RAGGIUNTO**

```
$ .venv/bin/python docs/collaudi/DRAW-010/chi-compone.py
== impianto 1 — prova-1-due-pdc-accumulo-combinato.json
   compose_drawing su A3, un foglio solo : SI
   la CLI (formato ordinario piu' piccolo): SI  (420x297, 1 foglio/i)
== impianto 2 — prova-2-pdc-deviatrice-acs.json
   compose_drawing su A3, un foglio solo : SI
   la CLI (formato ordinario piu' piccolo): SI  (420x297, 1 foglio/i)
== impianto 3 — prova-3-pdc-diretta-pavimento.json
   compose_drawing su A3, un foglio solo : NO  (run p6-a ... cannot be routed ...)
   la CLI (formato ordinario piu' piccolo): NO  (...)
== impianto 4 — prova-4-ibrido-pdc-caldaia.json
   compose_drawing su A3, un foglio solo : SI
   la CLI (formato ordinario piu' piccolo): SI  (420x297, 1 foglio/i)
== impianto 5 — prova-5-cascata-tre-pdc.json
   compose_drawing su A3, un foglio solo : NO  (the 4 functional bands need 447.5mm ...)
   la CLI (formato ordinario piu' piccolo): NO  (...)
```

`tests/layout/test_accessori_appesi.py` porta di conseguenza

```python
COMPONIBILI = (
    "prova-1-due-pdc-accumulo-combinato.json",
    "prova-2-pdc-deviatrice-acs.json",
    "prova-4-ibrido-pdc-caldaia.json",
)
NON_COMPONGONO = (
    ("prova-3-pdc-diretta-pavimento.json", "il ritorno del pavimento radiante non si instrada ..."),
    ("prova-5-cascata-tre-pdc.json", "le quattro fasce funzionali chiedono piu' larghezza ..."),
)
```

I due elenchi coprono tutti e cinque gli impianti. `TORNATO_A_COMPORRE` è sparito:
era un terzo elenco che diceva la stessa cosa del primo, e l'impianto che
conteneva non compone.

**Il rischio 22 è incassato.** L'`xfail(strict=True)`
`test_tornano_a_comporre_quando_la_composizione_compatta[prova-2]` era rosso sulla
testa di partenza — falliva perché l'impianto 2 **compone**, e la prova pretendeva
il contrario. L'impianto 2 è passato fra i componibili e quella prova non esiste
più; al suo posto c'è
`test_chi_non_compone_non_compone_per_la_ragione_scritta`, che serve nei due
versi: se un impianto smette di comporre lo dice il parametrizzato di
`COMPONIBILI`, se uno **ricomincia** e nessuno lo sposta lo dice questa.

```
$ .venv/bin/python -m pytest tests/layout/test_accessori_appesi.py -q
.................                                                        [100%]
17 passed in 1199.33s (0:19:59)
```

### 3.8 Criterio 8 — la tratta del prelievo ACS e la giacitura di `utenze` — **RAGGIUNTO IN PARTE**

```
$ .venv/bin/python docs/collaudi/DRAW-010/il-prelievo-acs.py \
    docs/collaudi/DRAW-010/<lato>/prova-2-pdc-deviatrice-acs-completo.json \
    docs/collaudi/DRAW-010/<lato>/prova-2-pdc-deviatrice-acs-geometria.json
```

base:

```
   utenze (prelievo): rotazione 90, attacco sulla faccia bottom
      tratta w2-a-a-a: pieghe=1  [[(225.0, 151.0), (225.0, 146.0)], [(225.0, 141.0), (225.0, 133.5)],
        [(230.0, 133.5), (232.5, 133.5)], [(237.5, 133.5), (260.0, 133.5), (260.0, 128.5)]]
```

ramo:

```
   utenze (prelievo): rotazione 90, attacco sulla faccia bottom
      tratta w2-a-a-a: pieghe=0  [[(215.0, 151.0), (215.0, 146.0)], [(215.0, 141.0), (215.0, 138.5)],
        [(215.0, 133.5), (215.0, 131.0)], [(215.0, 126.0), (215.0, 101.0)]]
```

**La prima metà è raggiunta, e oltre.** La tratta del prelievo passa da **una
piega a zero**: la spezzata è una sola verticale dalla faccia superiore del
bollitore fino a `utenze`. La curva che il PO chiamava inutile — quella con cui
la linea usciva a destra e poi risaliva dentro la bocchetta — non c'è più.

**La seconda metà non è raggiunta: `utenze` è ancora posato con la bocchetta
verso il basso.** La posa gliela dà giusta — attacco a sinistra, rotazione 180,
seduto a destra del bollitore, misurato su `place_sheet` e sulla posa che la fase
del tronco consegna — ed è il **ciclo di miglioramento** che lo rigira: `_rehung`
rimette ogni appeso con l'attacco rivolto allo stacco da cui pende, e su un
bollitore quello stacco guarda in su.

Impedirglielo è una riga, ed è stata scritta e misurata. Il conto:

| tavola 2 | pieghe | incroci | lunghezza |
|---|---|---|---|
| giacitura lasciata al ciclo (**consegnato**) | 4 | 4 | 645,0 mm |
| giacitura tenuta anche dal ciclo | **25** | 4 | **1127,5 mm** |

Venticinque pieghe contro quattro, e mezzo metro di tubo in più. Non l'ho
consegnata, e non ho ammorbidito il criterio: lo dichiaro non raggiunto nella
sua seconda metà, con la misura, e metto al PM la decisione (§7.3). La ragione
che il PO ha dato per il criterio — «pagando così una curva inutile» — nella
tavola consegnata non esiste più, perché quella tratta non paga nessuna curva.

Le altre due clausole del criterio:

- **`dhw_out` è ancora sulla faccia superiore**: `git diff af6fad8 -- assets/symbols`
  non stampa niente;
- **la libreria dei simboli è identica al commit di partenza**: stesso comando.

```
$ git diff --stat af6fad8 -- assets/symbols
$
```

### 3.9 Criterio 9 — nessuna tratta più corta di una freccia ne pretende una — **RAGGIUNTO**

La regola sta nella prova, sulla misura della tratta, non nel suo esito:

```python
def _the_longest_stretch_mm(route: RoutedTrunk) -> float:
    """Il tratto rettilineo piu' lungo della spezzata, in millimetri. ..."""

...
        if _the_longest_stretch_mm(route) < 2 * ARROW_LENGTH_MM:
            assert not stations, route.connection_ids
            assert not [tip for tip, _ in arrows if _on_route(tip, route)], (
                route.connection_ids
            )
            continue
        assert stations, route.connection_ids
```

Una tratta il cui tratto rettilineo più lungo non arriva a `2 × ARROW_LENGTH_MM`
non porta nessuna freccia, e la prova lo **verifica**: non che la freccia manchi
soltanto dove il renderer non la mette, ma che sulla spezzata non ci sia
**nessuna punta di freccia**.

```
$ .venv/bin/python -m pytest tests/layout/test_rami_di_servizio.py -q
........................                                                 [100%]
24 passed in 48.23s
```

Sulla base lo stesso file dava `1 failed, 23 passed`, con
`AssertionError: ['inlet-filling-unit-generatore-water-return-a'] assert []` —
la tratta lunga un passo di DRAW-009 §6.7.

### 3.10 Criterio 10 — lo scarico del bollitore, e la prova generale — **RAGGIUNTO**

```
$ .venv/bin/python docs/collaudi/DRAW-010/la-catena-fredda.py 2
```

base:

```
   fredda: acquedotto.a -> bollitore.cold_in
     valve-isolation-dhw-acquedotto-a  [isolation]
     tee-drain-connection-cold-bollitore-cold-in  [drain]
     dhw-safety-group-bollitore-cold-in  [isolation, non_return, safety] (a bordo: isolation, non_return)
     lo scarico sta dal lato del serbatoio: False   (scarico in posizione [1], organi che chiudono [0, 2])
```

ramo:

```
   fredda: acquedotto.a -> bollitore.cold_in
     valve-isolation-dhw-acquedotto-a  [isolation]
     dhw-safety-group-bollitore-cold-in  [isolation, non_return, safety] (a bordo: isolation, non_return)
     tee-drain-connection-cold-bollitore-cold-in  [drain]
     lo scarico sta dal lato del serbatoio: True   (scarico in posizione [2], organi che chiudono [0, 1])
```

La fila si legge dalla macchina verso l'impianto: il bollitore è il capo di
arrivo, quindi «dal lato del serbatoio» vuol dire più avanti nella fila. Lo
scarico è adesso **fra il gruppo di sicurezza e il serbatoio**, e aprendo quel
rubinetto il bollitore si svuota.

Vale anche sugli altri due impianti che hanno un accumulo sanitario:
`misure/catena-fredda-dopo.txt` dà `True` per il 2, il 3 e il 5 (era `False` su
tutti e tre).

**La prova generale** è
`tests/rules/test_ordine_semantico.py::test_un_organo_a_bordo_di_un_composito_conta_come_organo_che_chiude`.
Non nomina nessun pezzo: cerca nel modello completato una coppia in cui il
mestiere che uno pretende «dopo di sé» esiste **solo** a bordo dell'altro — e lo
verifica, `assert not wanted & set(definition.functions)` — poi misura da che
parte stanno. Una guardia finale (`assert misurate`) impedisce che passi a vuoto.

```
$ .venv/bin/python -m pytest tests/rules/test_ordine_semantico.py -q
.......                                                                  [100%]
7 passed in 9.60s
```

Che la prova misuri davvero la cura si controlla togliendola: rimettendo
`does = other.functions` al posto di `does = other.functions | other.on_board`,

```
E                           assert 2 < 1
FAILED tests/rules/test_ordine_semantico.py::test_un_organo_a_bordo_di_un_composito_conta_come_organo_che_chiude
```

### 3.11 Criterio 11 — `is_valid` è tornata stretta — **RAGGIUNTO**

```
$ .venv/bin/python -m pytest tests/layout/test_assi_dorsali_tee.py -q
1 failed, 10 passed in 17.00s
FAILED tests/layout/test_assi_dorsali_tee.py::test_una_macchina_a_terra_puo_partecipare_a_un_candidato_verticale
```

`test_l_allineamento_non_si_accetta_quando_rende_la_tavola_peggiore` è **verde**:
era rosso sulla testa di partenza ed è una delle quattro chiuse. L'unica rossa
rimasta in quel file è `test_una_macchina_a_terra_puo_partecipare_a_un_candidato_verticale`,
che è rossa anche sulla base e difende il pavimento invisibile abolito dal PO
(rischio 21, fuori perimetro).

La misura con lo strumento che il pacchetto nomina:

```
$ .venv/bin/python docs/collaudi/DRAW-009/le-due-sovrapposizioni.py
1. la posa da cui la prova di DRAW-007 parte
   ...
   is_valid con la regola consegnata: False
2. che cosa di quella prova regge lo stesso
   A. la mossa che si allinea da sola e' rifiutata .... True   <- l'unica che cade
   B. il ciclo non peggiora mai la tavola ............. True
   C. la tavola finisce senza violazioni ............. True   (0)
   D. ogni mossa accettata batte la precedente ....... True   (4 accettate)
3. il banco della traslazione di blocco
   coppie gia' sovrapposte nella posa che la fase del tronco consegna:
     bollitore <-> ritorno  compenetrazione = (2.5, 15.0) mm
   con la regola consegnata (non crea):
     asse+spazio      (0, 0, 0.0, 0, 32, 32, 4405.0, ...)  batte la partenza
     blocco           (0, 0, 0.0, 0, 32, 32, 4485.0, ...)  batte la partenza
   con la regola piu' stretta (ne' crea ne' approfondisce):
     asse+spazio      (0, 0, 0.0, 0, 32, 32, 4405.0, ...)  batte la partenza
     blocco           (0, 0, 0.0, 0, 32, 32, 4485.0, ...)  batte la partenza
```

Tre cose, e sono le tre che servono:

1. la mossa che la prova di DRAW-007 vuole rifiutata **è rifiutata**;
2. le coppie già sovrapposte sul banco scendono da **tre a una**: è §A;
3. **la regola stretta e quella monotona danno la stessa classifica**, quindi §E
   non costa niente. Ciò che cambia è che su quel banco `asse+spazio`
   (4405,0 mm) adesso batte `blocco` (4485,0 mm): è la ragione della rossa nuova
   di §6.2, e viene da §A, non da §E.

### 3.12 Criterio 12 — la tavola 1 non peggiora — **RAGGIUNTO**

```
$ .venv/bin/python docs/collaudi/DRAW-002/metriche.py <completo> <geometria>
```

| tavola 1 | base | ramo | |
|---|---|---|---|
| pieghe | 4 | **4** | invariata |
| incroci | 1 | **1** | invariata |
| lunghezza | 470,0 mm | **452,5 mm** | −17,5 mm |
| backtracking | 0 | 0 | invariato |
| organi D-120 | 14 su 15 | 14 su 15 | invariato |

E le tratte di autostrada:

```
$ .venv/bin/python docs/collaudi/DRAW-009/criteri.py <completo> <geometria>
== tratte di tronco che non possono essere rettilinee (criterio 10) ==
   autostrade con almeno una piega: 0
```

Identico sui due lati (`misure/criteri-prima-1.txt` e `misure/criteri-dopo-1.txt`
non differiscono di un carattere): **nessuna tratta di autostrada prende una
piega**, né prima né dopo.

### 3.13 Criterio 13 — la tavola 2 non peggiora — **NON RAGGIUNTO**

| tavola 2 | base | ramo | |
|---|---|---|---|
| pieghe | 5 | **4** | −1, migliora |
| incroci | 1 | **4** | +3, **peggiora** |
| lunghezza | 600,0 mm | **645,0 mm** | +45 mm, **peggiora** |
| nodi condivisi col tronco | 0 | **2** | **peggiora** |
| organi D-120 | 11 su 14 | 10 su 14 | **peggiora di uno** |
| riempimento | 50,1 % | 39,5 % | |
| squilibrio fra quadranti | 32,50 | **14,03** | migliora |

*(Il riferimento del criterio dice «organi D-120 14 su 15»: sulla tavola 2 gli
organi governati da D-120 sono **quattordici**, non quindici, e sulla base ne
stanno vicini undici. Quindici è il totale della tavola 1. Riporto i numeri
misurati sui due lati con lo stesso strumento.)*

**Perché peggiora, misurato.** La causa è §D.1, la disposizione del PO sul
prelievo. Il conto, sulla stessa testa del ramo con la sola riga di §D.1
disattivata:

| tavola 2 | pieghe | incroci | lunghezza |
|---|---|---|---|
| base `af6fad8` | 5 | 1 | 600,0 mm |
| ramo, **consegnato** (il prelievo pende dal bollitore) | **4** | **4** | **645,0 mm** |
| ramo, senza §D.1 (il prelievo resta una colonna) | 8 | 1 | 620,0 mm |
| ramo, senza §D.3 (l'ordine degli accessori di prima) | 21 | 7 | 1082,5 mm |

Si legge così: **§D.3 fa guadagnare molto** — senza di essa la tavola 2 avrebbe
21 pieghe — e **§D.1 scambia pieghe con incroci e lunghezza**. Nessuna delle due
configurazioni di §D.1 chiude il criterio: quella consegnata peggiora incroci e
lunghezza, quella senza §D.1 peggiora pieghe e lunghezza. Il budget della
lunghezza peggiora in tutt'e due, e la lunghezza è la voce su cui la tavola 2
paga la fila più lunga dell'acqua fredda: il gruppo di sicurezza e
l'intercettazione stanno adesso sulla **stessa** tratta, che è quindi più lunga
del suo stacco di prima.

Il criterio non è raggiunto, non è stato ammorbidito, e la decisione fra le due
configurazioni è del PM: §7.3.

### 3.14 Criterio 14 — determinismo — **RAGGIUNTO**

Doppia generazione dalla CLI, stesso modello, cartelle diverse:

```
$ for n in 1 2 4; do for giro in a b; do
    .venv/bin/python -m disegnatore_mep draw docs/collaudi/DRAW-010/dopo/prova-$n-*-completo.json \
      --catalog examples/layout/catalog --symbols assets/symbols --naming naming \
      --verifica --geometry $D/$n-$giro/geom.json --out $D/$n-$giro
  done; done
$ for n in 1 2 4; do diff -q $D/$n-a/geom.json $D/$n-b/geom.json && \
    sha256sum $D/$n-a/*.svg $D/$n-b/*.svg; done

impianto 1: geometria identica; svg b757d587a6c266a9 vs b757d587a6c266a9
impianto 2: geometria identica; svg 96474dac3c377abb vs 96474dac3c377abb
impianto 4: geometria identica; svg b9b98f94815642ae vs b9b98f94815642ae
```

Le impronte che la CLI stampa coincidono a coppie
(`misure/determinismo.txt`).

**Forma invariante alla ridenominazione**, dalle due prove che la misurano:

```
$ .venv/bin/python -m pytest tests/rules/test_ordine_semantico.py -q -k rinomin
..                                                                       [100%]
2 passed, 5 deselected in 8.38s
```

`test_l_ordine_funzionale_non_cambia_rinominando_gli_identificativi` e
`test_il_costo_della_tavola_non_cambia_rinominando_gli_identificativi`: stesso
impianto con identificativi rinominati e ordinamento invertito, stessa fila di
mestieri e stesso costo (pieghe, incroci, millimetri).

### 3.15 Criterio 15 — il saldo della suite — **NON RAGGIUNTO**

```
$ .venv/bin/python -m pytest -q -rA
```

| | base `af6fad8` | ramo |
|---|---|---|
| rosse | **10** | **14** |
| verdi | 1470 | 1483 |
| saltate | 24 | 24 |
| xfailed | 11 | 10 |

```
base : 10 failed, 1470 passed, 24 skipped, 11 xfailed in 2152.20s (0:35:52)
ramo : 14 failed, 1483 passed, 24 skipped, 10 xfailed in 2453.05s (0:40:53)
```

**Quattro rosse si chiudono:**

```
tests/layout/test_accessori_appesi.py::test_tornano_a_comporre_quando_la_composizione_compatta[prova-2-pdc-deviatrice-acs.json]
tests/layout/test_assi_dorsali_tee.py::test_l_allineamento_non_si_accetta_quando_rende_la_tavola_peggiore
tests/layout/test_rami_di_servizio.py::test_nessuna_freccia_sui_rami_statici_e_la_freccia_giusta_sugli_altri[una_macchina_con_accumulo_combinato]
tests/layout/test_stacchi_minimi_e_interasse.py::test_la_tavola_1_non_costa_piu_di_draw_005_sulla_rete_ordinaria
```

**Otto sono nuove**, e ciascuna ha la propria causa misurata in §6.2. Non ne ho
convertita nessuna in `skip` o `xfail`, non ho allentato nessuna soglia e non ho
toccato nessuna fixture per farle passare.

L'`xfail` in meno è `test_chi_e_tornato_a_comporre_compone_in_un_foglio_solo`,
che §C ha sostituito insieme all'elenco `TORNATO_A_COMPORRE` su cui girava.

### 3.16 Criterio 16 — nessun impianto che componeva smette — **RAGGIUNTO**

```
$ .venv/bin/python docs/collaudi/DRAW-010/chi-compone.py
```

| impianto | base | ramo | |
|---|---|---|---|
| 1 | SI | **SI** | |
| 2 | SI | **SI** | |
| 3 | NO | NO | stessa diagnostica |
| 4 | NO | **SI** | **guadagnato** |
| 5 | NO | NO | diagnostica diversa, §6.4 |

Nessuno smette, uno comincia. La misura è fatta nei due modi che contano: il
contratto della suite (`compose_drawing` su A3, un foglio solo) e la CLI
(`compose_on_ordinary_frame`, il più piccolo formato ordinario su cui il disegno
entra). Lo stesso file misura la base e il ramo, ed è per questo che esiste: è la
prova che l'impianto 4 non si perda una seconda volta.

---

## 4. Le misure

### 4.1 La posa della fase del tronco

§3.1. Uscite in `misure/coppie-prima.txt` e `misure/coppie-dopo.txt`.

### 4.2 Le due tavole

§3.12 e §3.13. Pacchetti grafici completi in `docs/collaudi/DRAW-010/prima/` e
`docs/collaudi/DRAW-010/dopo/`: per ogni impianto il modello completato, la
geometria, la tavola in SVG/PDF/PNG, il preflight e le misure.

### 4.3 L'impianto 4

§3.4. La tavola non esisteva; adesso esiste e sta in `dopo/`.

### 4.4 Il ripiego

§3.5. Uscite in `misure/ripiego-prima.txt` e `misure/ripiego-dopo.txt`.

### 4.5 La catena dell'acqua fredda

§3.10. Uscite in `misure/catena-fredda-prima.txt` e `misure/catena-fredda-dopo.txt`.

### 4.6 Le due regole di `is_valid`

§3.11.

### 4.7 `ruff` e `mypy`

```
$ .venv/bin/python -m ruff check src tests docs/collaudi/DRAW-010
All checks passed!
$ .venv/bin/python -m mypy src
Success: no issues found in 69 source files
$ .venv/bin/python -m mypy src tests
tests/layout/test_posa_a_fasi.py:515: error: Incompatible return value type
  (got "dict[str, PlacedSymbol]", expected "dict[str, object]")  [return-value]
tests/layout/test_posa_a_fasi.py:531: error: Unpacked dict entry 1 has incompatible type
  "dict[str, object]"; expected "SupportsKeysAndGetItem[str, PlacedSymbol]"  [dict-item]
Found 2 errors in 1 file (checked 160 source files)
```

Le due segnalazioni su `tests/layout/test_posa_a_fasi.py` sono **antecedenti**:
lo stesso comando sulla base le dà identiche (`Found 2 errors in 1 file (checked
159 source files)`). `mypy` sul solo `src`, che è quello che
`scripts/setup-env.sh` verifica, è pulito sui due lati.

---

## 5. Il perimetro

**Toccato, e dentro il perimetro dichiarato:** la posa consegnata dalla fase del
tronco e il meccanismo che separa i pezzi (§A); gli impianti 4, 3 e 2 come banco
(§B); gli elenchi di copertura della suite (§C); la posa del prelievo (§D.1); la
freccia sotto la lunghezza minima (§D.2); l'ordine degli accessori rispetto agli
organi dichiarati a bordo di un composito (§D.3); `is_valid` (§E); le misure e il
rapporto.

**Toccato oltre la lettera del perimetro, e dichiarato:**

1. **`_sorted` e `against_the_anchor`** (§2.3). Senza, la cura di §D.3 non cambia
   l'ordine di una riga e il criterio 10 non si chiude. §7.1.
2. **`stub_minimum_mm`** (§2.4). Senza, la tavola 2 non esce più: è §D.3 che
   scopre un difetto antecedente del conto dello stacco. §7.2.
3. **Quattro documenti rigenerati**: `docs/prodotto/GRAFO_IMPIANTO.md`, i grafi
   di prova 2, 3 e 5, `examples/rules/centrale-pdc-completa.json`. Non sono
   fixture toccate per far passare una prova: sono artefatti che la catena
   riscrive da sé, e che quattro prove pretendono **identici alla rigenerazione
   corrente**. §D.3 cambia il grafo, quindi cambia loro; lasciarli com'erano
   avrebbe voluto dire pubblicare un documento vecchio come attuale.

**Non toccato:** la libreria dei simboli (`git diff af6fad8 -- assets/symbols`
non stampa niente); l'ordine degli stacchi lungo il tronco (rischio 17); le due
prove che difendono il pavimento invisibile (rischio 21); il ripiego di
`compose_sheet`, che §B.4 dice di non togliere; gli attacchi pari di un
collettore; l'impianto 5 oltre la misura.

---

## 6. Difetti noti

### 6.1 La tavola 2 peggiora su incroci e lunghezza

§3.13, con il conto delle configurazioni. È il criterio 13, e non è raggiunto.

### 6.2 Otto rosse nuove, con la causa di ciascuna

| prova | causa misurata |
|---|---|
| `test_posa_a_fasi::test_l_allungo_non_sposta_nessuno_di_traverso[macchina_e_accumulo]` | §D.1. Il prelievo si siede **fuori dall'asse** dello stacco (la gamba del gomito), e il ciclo lo riappende sull'asse: la mossa di allungo lo sposta allora su tutt'e due le coordinate. La prova pretende che ogni pezzo di un allungo si muova su una sola. Lo **stiramento** non muove nessuno di traverso; a muoversi di traverso è il **riappendimento** che lo accompagna, che è un'altra operazione. |
| `test_posa_a_fasi::test_l_allungo_non_sposta_nessuno_di_traverso[due_macchine_e_accumulo]` | la stessa |
| `test_stacchi_minimi_e_interasse::test_traslare_una_macchina_non_cambia_il_suo_riquadro_ne_stacca_cio_che_le_pende` | la stessa: `rubinetti` passa da rotazione 180 a 90 e da una quota all'altra quando la macchina trasla |
| `test_posa_a_fasi::test_ogni_impianto_di_prova_arriva_alla_fase_del_tronco[prova-5]` | §D.1. Con il prelievo appeso al bollitore la fascia che li contiene si allarga, e le quattro fasce dell'impianto 5 chiedono 447,5 mm contro i 335 dell'area di disegno: la posa si ferma prima della fase del tronco. Sulla base ne chiedevano meno e la posa arrivava in fondo, pur senza produrre una tavola. |
| `test_posa_dei_cinque_impianti::test_l_impianto_arriva_alla_posa[prova-5]` | la stessa |
| `test_posa_a_fasi::test_il_corredo_che_non_entra_allunga_il_tronco_e_non_lo_piega[macchina_e_accumulo]` | §A. La prova stringe la campata di una tratta di tronco finché il corredo non ci sta più, e misura che il tronco si allunghi invece di piegarsi. Con la compattazione nuova la campata non si fa mai stretta abbastanza — «la campata non si e' mai fatta stretta abbastanza», `assert 0 > 0` — perché la fase la riapre. |
| `test_stacchi_minimi_e_interasse::test_sulla_tavola_composta_nessuno_stacco_e_piu_lungo_del_minimo_senza_una_ragione[una_macchina_con_accumulo_combinato]` | §A.4. `stub-filling-unit-generatore-water-return-b` è lungo 12,5 mm contro un minimo di 5,0: è la figura allontanata lungo il proprio stacco per non stare addosso a un'altra. La prova ammette uno stacco più lungo del minimo solo se avvicinarlo di un passo lo farebbe toccare qualcuno, e sulla tavola composta non lo farebbe più. |
| `test_traslazione_di_blocco::test_la_traslazione_di_blocco_vince_dove_nessun_altra_vince` | §A. Il banco parte adesso da una posa con **una** coppia sovrapposta invece di tre, e su quella posa `asse+spazio` (4405,0 mm) batte `blocco` (4485,0 mm). La traslazione di blocco esiste ancora e batte la posa di partenza; non è più **strettamente** la migliore su quel banco. La misura è in §3.11. |

Le tre rosse che restano dalla base — `test_una_macchina_a_terra...`,
`test_the_hard_constraints_hold_after_improvement` (rischio 21, il pavimento
invisibile) e `test_la_valvola_che_isola_oltre_un_raccordo_passante...`
(DRAW-009 §6.7, la prova che ha perso il proprio caso) — sono fuori perimetro e
non sono state toccate. Restano rosse anche le tre di
`test_stacchi_minimi_e_interasse` che lo erano già.

### 6.3 Il ciclo rigira il prelievo

§3.8. La posa gliela dà giusta, il ciclo la disfa, e tenergliela costa
venticinque pieghe.

### 6.4 L'impianto 5 non arriva più alla posa

Prima: la posa arrivava in fondo e la fase del tronco consegnava una posa (con
quattro coppie sovrapposte e ventuno troppo vicine), poi la tavola non usciva
sull'instradamento. Adesso `place_sheet` si ferma prima, sulle fasce: 447,5 mm
contro 335. La causa è §D.1, come per le due rosse di §6.2.

L'impianto 5 non componeva né prima né dopo, quindi il criterio 16 regge; ma è un
arretramento misurato su un impianto che il pacchetto mette **fuori perimetro**
(«l'impianto 5 oltre la misura»), e sta qui perché il PM lo veda.

### 6.5 L'impianto 4 esce dal ripiego

§3.5. La catena a fasi e la posa seminata cadono tutt'e due su `s3-a`; la tavola
esce dal ciclo senza le fasi. È una tavola vera e misurata (14 pieghe, 9 incroci,
1327,5 mm), ma non è la tavola che la catena a fasi voleva. Il pacchetto non lo
chiede per l'impianto 4 — §B.2 parla della sola tavola 2 — e lo dichiaro perché
§B.4 vuole il conto del ripiego impianto per impianto.

### 6.6 Una coppia resta troppo vicina sull'impianto 3

`drain-connection-volano-a ↔ inlet-filling-unit-pdc-water-return` e
`filling-unit-pdc-water-return ↔ pdc`, due coppie, identiche a quelle della base.
Per l'impianto 3 la fase del tronco non consegna una posa — non si instrada — e
`carry_the_rest` restituisce la disposizione di partenza: la compattazione non
entra mai in gioco. Fuori dai criteri, che parlano della tavola 2.

---

## 7. Punti aperti per il PM

### 7.1 `against_the_anchor` cede a un vincolo dichiarato: è una scelta, non un dettaglio

§2.3. La cura che §D.3 prescrive — contare `carries_on_board` — da sola **non
cambia l'ordine di una riga**: misurato. Serve anche che il posto «attaccato alla
macchina» smetta di scavalcare in silenzio i vincoli `before`/`after`.

Ho scelto di farlo perché senza il criterio 10 non si chiude, perché il piede di
uno stacco non chiude niente — quindi la via di sfogo che quel vincolo difende
resta aperta — e perché quattro regole lo dichiarano e tre di esse non sono
toccate dal cambiamento (nessun pezzo pretende di stare fra una valvola di
sicurezza e la propria macchina).

**È però una modifica alla forza di un vincolo dichiarato, cioè materia MEP.** Se
il PM o il PO la ritengono sbagliata, la riga è una sola e la alternativa è
lasciare il criterio 10 non raggiunto.

### 7.2 `stub_minimum_mm` non contava il franco di estremità

§2.4. È un difetto **antecedente**: il conto dello stacco e il conto di chi
siede gli accessori non davano lo stesso numero, e la differenza si vedeva solo
su uno stacco che porta più di un accessorio — caso che non esisteva prima di
§D.3. L'ho corretto perché senza la tavola 2 non esce.

La correzione è limitata al caso da due accessori in su, perché con uno solo il
posto lo si trova comunque e allungare tutti gli stacchi avrebbe pagato
lunghezza su tavole che non ne avevano bisogno (I-046: ogni millimetro oltre il
minimo è tubo, e il tubo costa). Se il PM preferisce la correzione piena — il
franco sempre — la riga è una sola, e va rimisurato il budget della lunghezza
sulle due tavole.

### 7.3 Il prelievo: due configurazioni, un conto, una decisione

§3.8 e §3.13. Il PO ha disposto che il prelievo si posi come un ingresso, con la
propria giacitura scelta per non pagare pieghe, e ha detto perché: «Bastava
mettere ACS.01 verso destra ed era meglio», cioè per togliere una curva inutile.

Nella tavola consegnata **quella curva non esiste più** — la tratta del prelievo
passa da una piega a zero — ma `utenze` è ancora posato con la bocchetta verso il
basso, perché il ciclo di miglioramento lo rigira. Tenergli la giacitura costa
venticinque pieghe e mezzo metro di tubo.

Le due strade, con il numero:

1. **come consegnato**: tratta del prelievo senza pieghe, `utenze` con la
   bocchetta in basso; tavola 2 a 4 pieghe / 4 incroci / 645,0 mm;
2. **giacitura tenuta anche dal ciclo**: `utenze` con la bocchetta a sinistra;
   tavola 2 a 25 pieghe / 4 incroci / 1127,5 mm.

Non ho scelto al posto del PO: ho consegnato quella che non distrugge la tavola e
porto qui il conto. La seconda è una riga in `Improver._rehung`, e il rapporto ne
dice esattamente il punto.

### 7.4 Il rischio 16 va riletto: la tavola 2 non esce dal ripiego

§3.5. La premessa di §B.2 non si riscontra sul commit di partenza. Il rischio 16
resta vero come rischio — il ripiego esiste e lavora, sull'impianto 4 — ma non
descrive più la tavola 2.

### 7.5 L'impianto 5 e le fasce

§6.4. Se il PO vuole che l'impianto 5 torni almeno alla posa, la strada è che un
confine di rete appeso non allarghi la fascia del pezzo che serve. Non è nel
perimetro di questo pacchetto e non l'ho aperta.

### 7.6 Le otto rosse nuove

§6.2. Tre di esse (`l_allungo_non_sposta_nessuno_di_traverso` ×2,
`traslare_una_macchina_non_cambia_il_suo_riquadro`) misurano una proprietà che
l'allungo continua ad avere e che il **riappendimento** di un confine di rete non
ha: la prova non distingue le due operazioni. Sono prove di DRAW-008 e DRAW-009,
fuori perimetro, e non le ho toccate.

---

## 8. Che cosa **non** è stato fatto

- **Il ripiego di `compose_sheet` non è stato tolto**: §B.4 lo dice
  esplicitamente.
- **L'ordine degli stacchi lungo il tronco** (rischio 17) resta com'era.
- **Le due prove del pavimento invisibile** (rischio 21) restano rosse e intatte.
- **L'impianto 5 non è stato inseguito** oltre la misura.
- **La libreria dei simboli non è stata toccata.**
- **Nessuna decisione MEP è stata presa dal DEV.** Le due che il lavoro ha
  incontrato — la forza di `against_the_anchor` e la giacitura del prelievo nella
  tavola finita — stanno in §7.1 e §7.3, con il conto, e aspettano.
- **`PROJECT_STATE.md` non è stato aggiornato.** Il perimetro del pacchetto
  elenca ciò che sta dentro e quel file non c'è; i rischi che questa consegna
  tocca — il 14 e il 22 chiusi, il 16 da rileggere (§7.4), il 19 chiuso con §E —
  stanno qui, e la scrittura dello stato è del PM.
