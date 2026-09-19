# RAPPORTO DI CONSEGNA — DRAW-013

**Pacchetto:** `ACTIVE_WORK_PACKAGE.md` — «La tavola si allarga tutta insieme, non tocca il
bordo, e la distribuzione ha la sua forma»
**Disposizioni di riferimento:** **D-142** (si allarga tutto insieme), **D-143** (il margine
dal bordo), **D-144** (la forma della distribuzione), **D-145** (gli organi di servizio),
**D-146** (le tavole per prime)
**Ruolo:** DEV
**Data:** 2026-09-19

---

## 0. LE TAVOLE (D-146)

Cinque impianti di prova. **Ne escono due**, e sono questi i PDF da guardare:

| Impianto | Tavola in PDF |
|---|---|
| 1 — due PdC con accumulo combinato | `docs/collaudi/DRAW-013/dopo/prova-1-due-pdc-accumulo-combinato-t1.pdf` |
| 2 — PdC con deviatrice e ACS | `docs/collaudi/DRAW-013/dopo/prova-2-pdc-deviatrice-acs-t1.pdf` |

Le stesse due, **prima** di questo pacchetto — cioè sul ramo di partenza, che è il ramo di
`DRAW-012` e non `main` — stanno in `docs/collaudi/DRAW-013/prima/`, con lo stesso nome. Il
confronto che il PO deve fare è quello, e sono quattro PDF in tutto.

**Gli altri tre impianti non producono nessuna tavola**, come non la producevano sul ramo di
partenza. Dove si fermano, con le parole del motore:

| Impianto | Dove si ferma |
|---|---|
| 3 — PdC diretta a pavimento | `run w2-a-a-a still passes under mixing-valve-thermostatic after breaking for it: the accessory sits where its own run bends back into it, give the run a longer straight length` |
| 4 — ibrido PdC + caldaia | `run w2-a on network sanitaria cannot be routed: no route from (134, 80) to (144, 80): every orthogonal path is blocked` |
| 5 — cascata di tre PdC | `run s4-a on network secondario cannot be routed: no route from (137, 65) to (105, 71): the 5 straight steps the chain needs beyond the port at (137, 65) run into an obstacle at (140, 65)` |

**Nessun impianto ha smesso di uscire** per colpa di questo pacchetto, e nessuno ha ricominciato:
escono gli stessi due di prima. La tavola 4 è misurata cella per cella in §6.

---

## 1. Le tre cose da guardare per prime, sulle tavole

### 1.1 Il disegno non tocca più il bordo, e si vede

Sulle due tavole il margine dal bordo dell'area di disegno passa da **12,5 mm** (tavola 1) e
**17,5 mm** (tavola 2) a **25,0 mm** su tutt'e due. È il numero che il PO ha chiesto — «non si
mettono gli oggetti così vicini al bordo del foglio» — ed è il primo effetto che si vede
guardando i quattro PDF affiancati.

Non è un ritocco finale: il margine è entrato nella **chiave di costo della posa**, prima del
riempimento. Un disegno che si allarga fino al bordo per far salire una percentuale adesso
perde, ed è esattamente la mossa che aveva fatto bocciare `DRAW-012`.

### 1.2 Il riempimento non si compra più allungando un tratto

Lo stiramento del singolo tratto resta — serve a far entrare il corredo dove non ci sta, che è
la ragione per cui il contratto lo ammetteva — ma **il riempimento non lo può più comprare**: nel
confronto che decide se un allungo passa, la voce del riempimento è tolta.

Al suo posto c'è la **dilatazione proporzionale** (`src/disegnatore_mep/layout/dilate.py`): a
disegno risolto si sceglie **un fattore per foglio** e si allargano **tutti** i vuoti della stessa
percentuale. Fattore usato: **1,08** sulla tavola 1 e **1,25** sulla tavola 2.

**Quanto ha davvero mosso, e il PM lo deve sapere prima di guardare i numeri**: la griglia
quantizza la mossa, e con un fattore piccolo la annulla quasi del tutto. Misurato sulla stessa
tavola, prima e dopo la dilatazione — §7.5 spiega il meccanismo:

| | prima della dilatazione | dopo |
|---|---|---|
| tavola 1 (fattore 1,08) | 297,5 × 117,5 mm — riempimento 42,5 % | **300,0 × 117,5 mm** — 42,9 % |
| tavola 2 (fattore 1,25) | 290,0 × 167,5 mm — riempimento 59,1 % | **300,0 × 167,5 mm** — 61,1 % |

La dilatazione ha aggiunto **due millimetri e mezzo** sulla tavola 1 e **dieci** sulla tavola
2, su un asse solo in tutt'e due i casi: in altezza non ha mosso nulla. §7.5 dice perché, ed è
un fatto della griglia, non una taratura.

**Va detto subito, perché cambia come si legge il criterio 2**: le due tavole erano già dov'erano
**prima** della dilatazione — 42,5 % e 59,1 % — e la dilatazione ha aggiunto meno di due punti.
Il riempimento lo raggiunge ancora la **posa**, che ha la finestra di D-140 nella propria chiave
come l'aveva prima; ciò che è cambiato è che adesso **il margine viene prima della finestra**,
e che lo stiramento del singolo tratto non la può più comprare. Cioè: le due mosse che il PO ha
bocciato sono chiuse, ma non è vero che «il riempimento sale per dilatazione e non per altro»
come §E si aspettava. §7.6 lo porta al PM come la cosa da decidere.

### 1.3 L'ingresso dell'acqua fredda è tornato addosso al pezzo che alimenta — sulla tavola 1

Sulla **tavola 1** la distanza fra il confine di rete dell'acquedotto e l'accumulo che alimenta
passa da **40,0 mm a 20,0 mm**: si vede, ed è il difetto di leggibilità che D-145 nomina.

Sulla **tavola 2** passa da **135,0 mm a 120,0 mm** — migliora, ma resta lontano, e **questo
criterio non è raggiunto**. §7.1 dice perché, con la misura: non è l'organo di servizio ad
essersi allontanato — quello sta al proprio minimo — è il gruppo dell'acqua fredda ad essere
posato lì, e la posa è fuori perimetro.

---

## 2. Ramo, base, file

| | |
|---|---|
| **Ramo** | `claude/draw-013-mep-ls35ta`, quello che la piattaforma ha assegnato alla sessione |
| **Base** | il **merge di `DRAW-012`** (`17ff425`) su `main` (`651310f`), primo commit del ramo e da solo, come il pacchetto prescrive |
| **Consegna** | una PR sola verso `main`, non fusa |

Il merge è passato senza conflitti: i due insiemi non si sovrappongono, e
`ACTIVE_WORK_PACKAGE.md` e `PROJECT_STATE.md` sono arrivati da `main` senza che nulla li
contendesse.

### File toccati

| File | Che cosa |
|---|---|
| `src/disegnatore_mep/layout/dilate.py` | **nuovo** — la dilatazione proporzionale (§A) |
| `src/disegnatore_mep/layout/geometry.py` | il margine di rispetto: le due costanti di D-143, il margine misurato e quello che un disegno può permettersi (§B) |
| `src/disegnatore_mep/layout/compose.py` | la dilatazione entra nella catena, dopo l'instradamento e prima della centratura; il diario porta il fattore |
| `src/disegnatore_mep/layout/improve.py` | il margine nella chiave di costo; la guardia del riempimento che diventa divieto (§E); l'allungo che il riempimento non compra (§A.3); il vincolo di D-145 (§G) |
| `src/disegnatore_mep/layout/highways.py` | `turns_of`, e la catena che porta ai terminali con **una** curva dichiarata (§C) |
| `src/disegnatore_mep/layout/hierarchy.py` | `source_machines`, letto da due — la gerarchia e le catene |
| `src/disegnatore_mep/validation/preflight.py` | il rilievo del disegno che tocca il bordo senza esserne autorizzato (§B.4) |
| `tests/layout/test_tavola_comoda.py` | **nuovo** — le prove del pacchetto |
| `tests/layout/test_objective.py` | la prova che la curva dichiarata non è una cessione; la prova dell'impilamento, riscritta con la ragione per cui la colonna non torna |
| `tests/layout/test_costo_peso.py`, `test_ordine_del_disegnatore.py`, `test_riempimento_del_foglio.py`, `test_assi_dorsali_tee.py` | il campo nuovo del costo, dichiarato dove il costo si costruisce per intero, e il tipo della chiave dove il diario la rilegge |
| `PROJECT_STATE.md` | la voce della consegna in revisione |
| `docs/collaudi/DRAW-013/**` | questo rapporto, gli strumenti di misura, il pacchetto grafico |

---

## 3. Che cosa è stato fatto, e perché così

### 3.1 §A — la dilatazione proporzionale (D-142)

`layout/dilate.py`. Su ciascun asse si costruisce una funzione monotona a tratti: **pendenza 1**
dove c'è un simbolo — così i simboli restano della loro misura, che ADR 0003 pretende — e il
**vuoto allargato del fattore** fra un simbolo e l'altro. Da qui discendono, per costruzione e
non per fortuna:

- nessun pezzo si sposta **rispetto agli altri**: chi stava in colonna resta in colonna, chi
  stava in quota resta in quota, perché la funzione è **una sola per asse**;
- un tratto orizzontale resta orizzontale e uno verticale resta verticale: **nessuna piega nasce
  e nessuna sparisce**;
- gli attraversamenti sono gli stessi punti, portati avanti dalla stessa funzione.

Il fattore si sceglie **dopo** che il disegno è risolto, ed è **uno solo per foglio**: il più
grande che tiene l'ingombro dentro il margine di §B e non spinge il riempimento oltre la sponda
alta di D-140.

**Dove ho dovuto scostarmi dalla lettera del pacchetto, e perché.** §A.2 chiede che il risultato
resti sulla griglia e che, se un fattore porta un pezzo fuori passo, si prenda «il fattore
ammissibile più vicino». Misurato: un vuoto lungo `m` passi resta un numero intero di passi solo
se il fattore è `t/q` con `q` divisore del **massimo comun divisore di tutti i vuoti**, e su
queste due tavole quel divisore è **1** — ci sono vuoti da un passo solo. Gli unici fattori
esatti sarebbero quindi gli **interi**, e nessun intero ci sta nel foglio: la dilatazione non
sarebbe **mai** entrata in gioco, su nessuna tavola.

Ho portato la cosa al PO invece di deciderla. Risposta: «stretchare tutto di un X per cento
finché ci sta spazio senza uscire dalla tavola. Se c'è spazio stretchi altrimenti no.» Il
fattore resta perciò **uno solo per foglio** e i vuoti si posano sul passo della griglia: lo
scarto fra il fattore nominale e quello realizzato su un vuoto è **meno di mezzo passo, cioè
meno di 1,25 mm**, e la tavola resta instradabile. `dilate.factor_error` lo misura e la prova
generale pretende che sia **zero** sui vuoti che il fattore divide esattamente.

**Come si distribuisce quello scarto, perché il PM non lo scopra da sé.** In millimetri è
limitato per costruzione: mezzo passo, cioè **1,25 mm**, su ogni vuoto. In proporzione no, ed è
tutto concentrato sui **vuoti da un passo solo**: un vuoto di 2,5 mm a fattore 1,25 resta di
2,5 mm — la griglia non ha nulla fra un passo e due. Sulle due tavole consegnate i vuoti da un
passo sono sette su diciassette (tavola 1) e cinque su quindici (tavola 2), e sono i minimi di
stacco, cioè i posti in cui allargare serviva meno. Il disegno cresce dove c'era spazio e non
si muove dove non ce n'era: è una conseguenza della griglia, non una scelta, e va guardata sulle
tavole prima che sul numero.

### 3.2 §B — il margine dal bordo (D-143)

Due costanti in `layout/geometry.py` — 25 mm di partenza, 10 mm di minimo — e due funzioni:
quanto dista dal bordo il pezzo che gli sta più vicino, e **quanto quel disegno poteva
permettersi**. La seconda è il metro con cui si giudica: vicino al bordo è **autorizzato** solo
quando il disegno, di suo, non poteva stare più dentro.

Il margine entra in **tre** posti, e sono tre perché uno solo non sarebbe bastato:

1. nella **chiave di costo della posa**, fra gli attraversamenti e il riempimento — è qui che si
   chiude il difetto vero: senza, il disegno si allargava da sé fino al bordo per far salire la
   percentuale, e poi non c'era più niente da dilatare;
2. come **limite della dilatazione**: il fattore si ferma lì, e il margine è quello che il
   disegno **a fattore 1** poteva permettersi — dilatare non lo può mai stringere di più;
3. nel **preflight**, che segnala il disegno che tocca il bordo senza esserne autorizzato.

### 3.3 §C — la forma della distribuzione (D-144)

`highways.turns_of` conta le curve di una catena; `lies_in_line` diventa «la catena sta nella
**propria forma**». Per l'autostrada fra le macchine di spina la forma è la retta intera, ed è
l'invariante che `DRAW-012` §C ha costruito: non si tocca. Per la strada che va da un accumulo,
un puffer o uno scambiatore a un'utenza la forma è quella di D-144: gamba dritta, **una** curva,
dorsale. La curva è **dichiarata**, e perciò il diario non la conta fra le catene cedute.

**Il pettine non c'è, ed è bloccato a monte.** §C.4 e il criterio 9 chiedono i terminali
impilati sul fianco della dorsale. Misurato sulla fixture delle due zone: non è la posa a
impedirlo. Le due zone pendono da un `zone-manifold` largo 40 mm con `out_1` e `out_2` sulla
faccia **inferiore**, a quindici millimetri l'uno dall'altro, e **chi pende da due attacchi
affiancati su una faccia orizzontale sta affiancato**. La dorsale dello schizzo del PO sarebbe lo
stesso collettore girato di novanta gradi, con gli attacchi impilati sul fianco — ma il simbolo
dichiara `allowed_rotations_deg: [0]`, e per **D-049** quel campo è un vincolo **tecnico**, non
geometrico. Non è il DEV a deciderlo. §7.2 lo porta al PO come domanda, con la riga da cambiare.

### 3.4 §E — la guardia del riempimento diventa un divieto (D-141)

Il verdetto sulla PR #41 §5.1 aveva misurato che la guardia era una **soglia**: finché la
copertura restava sopra 0,75, una posa che alzava il riempimento **e abbassava la copertura**
vinceva lo stesso. Adesso il riempimento salito così **si legge come quello dell'altra posa**, e
non compra niente: il caso **lieve** costa quanto il caso grosso, e la prova esercita tutt'e due.

### 3.5 §G — gli organi di servizio addosso al pezzo che servono (D-145)

Un vincolo di `is_valid`, non una voce di costo: **D-139 non si tocca**. Il tetto di uno stacco
è il più grande fra **il proprio minimo su griglia** e **il posto che gli accessori in linea
pretendono su quella tratta** — il «vincolo dichiarato» di §G.2, ed è l'esempio che D-145 fa.

**Quel «vincolo dichiarato» non è un dettaglio: senza di lui la tavola 2 smette di uscire.**
Misurato: con il tetto fermo al solo minimo dello stacco, l'intercettazione dell'acquedotto non
trova più il proprio rettilineo e `compose_drawing` si ferma su
`run w1-a has no straight stretch for valve-isolation`.

**Il vincolo è monotono, e questo è un limite dichiarato.** Impedisce a uno stacco di
**allungarsi**, ma lascia lungo quello che la posa iniziale ha già fatto lungo — che è metà del
difetto che il PO ha nominato. L'altra metà l'ho scritta, misurata e **tolta**, insieme a una
lettura più stretta del tetto: **§7.7 porta il conto di tutt'e tre le varianti**, ed è la cosa
più importante di questo rapporto dopo le tavole.

⚠️ **Un tetto sbagliato nascondeva tutto**: la prima scrittura leggeva il bisogno da
`_need_mm`, che sembra la funzione giusta e non lo è — non scende mai sotto i dieci millimetri
di `ROW_GAP_MM`, perché misura la distanza fra **due simboli** e non il bisogno di quella
tratta. Su uno stacco vuoto, il cui minimo è cinque, quel tetto regalava cinque millimetri di
gioco a ciascuno e il vincolo non teneva niente. Misurato sulla tavola 2: nove appesi, sei dei
quali con il posto richiesto a zero e `_need_mm` a dieci.

---

## 4. I criteri, uno per uno

I comandi e i loro output sono in §5 e §6; qui c'è l'esito e dove leggerlo.

| # | Esito | Dove |
|---|---|---|
| 1 | **raggiunto** | §5.1 — la prova generale della dilatazione |
| 2 | **NON raggiunto nel senso del pacchetto** | la tavola 2 è in finestra (61,1 %) e la tavola 1 no (42,9 %); ma **nessuna delle due ci entra *per dilatazione***: erano a 59,1 % e 42,5 % già prima, e la dilatazione ha aggiunto meno di due punti. §1.2, §7.3 e §7.6 |
| 3 | **NON raggiunto sulla tavola 2** | 135,0 → 120,0 mm. Raggiunto sulla tavola 1: 40,0 → 20,0 mm. §7.1 |
| 4 | **raggiunto** | 25,0 mm su tutt'e due le tavole, contro 12,5 e 17,5 |
| 5 | **raggiunto** | §5.2 — la prova nei due versi |
| 6 | **raggiunto** | 4/1 e 5/1, identici al ramo di partenza |
| 7 | **raggiunto** | §5.3 — il caso lieve non vince |
| 8 | **raggiunto in parte** | la forma e la curva unica sono provate; il **pettine** no, ed è bloccato dal simbolo del collettore (§3.3, §7.2) |
| 9 | **NON raggiunto** | la colonna non torna, e la ragione è quella di §3.3: sta nel simbolo, non nella posa |
| 10 | **raggiunto** | §5.4 — il diario non conta la curva fra le cedute |
| 11 | **misurata, e non esce** | §6 — il conto cella per cella |
| 12 | **raggiunto come vincolo**, non come attuazione | §5.5; il vincolo impedisce di allontanare e non accorcia, e §7.7 misura che cosa costerebbe farlo accorciare |
| 13 | da leggere in §8 | |
| 14 | da leggere in §8 | |
| 15 | **raggiunto** | §9 — la tabella prima/dopo |

---

## 5. Le prove

Le prove nuove stanno in `tests/layout/test_tavola_comoda.py`, e sono **sedici**.

```
$ .venv/bin/python -m pytest tests/layout/test_tavola_comoda.py -q
................                                                         [100%]
16 passed in 0.24s
```

### 5.1 §A — la dilatazione (criterio 1)

`test_la_dilatazione_allarga_tutti_i_vuoti_della_stessa_percentuale[1.5 | 2.0 | 2.5]`
costruisce una tavola di prova con vuoti di misura diversa, la dilata e pretende, in una
prova sola:

- `factor_error` **zero**: il fattore è esatto su ogni vuoto;
- ogni vuoto cresciuto **esattamente** del fattore, su tutt'e due gli assi;
- ogni simbolo della **stessa misura** di prima, e nessuno che ne scavalchi un altro;
- **pieghe e attraversamenti identici**.

Accanto, tre prove che tengono su il resto: `..._conserva_le_colonne_e_le_quote` (due pezzi
sulla stessa ascissa restano sulla stessa ascissa — è ciò che tiene insieme la dorsale),
`..._non_e_mai_una_contrazione` (§A.4: un disegno che non ci sta resta quello che è) e
`..._si_ferma_al_margine_e_non_lo_stringe`.

**E una quarta che dice una cosa che il pacchetto dava per scontata**: §A.1 scrive che «la
copertura dell'ingombro non può scendere». Il ragionamento è giusto — la dilatazione non
sposta nessun pezzo rispetto agli altri, quindi non crea la propaggine che D-141 teme — ma la
**misura** non è invariante: `ink_coverage` divide l'ingombro in sessantaquattro celle
*relative all'ingombro stesso*, e quando l'ingombro cresce le celle crescono con lui. Misurato
sulla tavola di prova: **0,3125 → 0,2500 a fattore 1,5**.
`test_la_dilatazione_non_crea_la_propaggine_che_la_copertura_cerca` lo dichiara e prova al suo
posto ciò che regge davvero: **tutti i vuoti crescono dello stesso fattore**, quindi nessun
pezzo si allontana dagli altri più degli altri. Per questo la copertura **non** è nella
guardia che accetta la dilatazione: tenercela l'avrebbe bocciata proprio sulle tavole scariche,
che sono quelle per cui esiste. La variazione misurata sulle due tavole vere è in §9.

### 5.2 §B — il margine (criteri 4 e 5)

`test_il_margine_parte_da_venticinque_e_si_stringe_solo_per_far_entrare` misura le tre
situazioni: un disegno piccolo ha 25 mm, uno largo 320 mm ne ha meno di 25 ma più di 10 e
sulla griglia, uno largo quanto il foglio si ferma a 10.

`test_il_preflight_segnala_il_disegno_che_tocca_il_bordo_senza_autorizzazione` è il criterio 5
**nei due versi**: un disegno piccolo spinto contro il bordo è un rilievo; lo stesso bordo,
toccato da un disegno largo 330 mm, non lo è — più dentro non ci stava.

### 5.3 §E — la guardia (criterio 7)

`test_la_guardia_del_riempimento_boccia_anche_il_caso_lieve` riproduce le tre pose che il PM
ha misurato in §5.1 del verdetto:

| posa | riempimento | copertura | prima | adesso |
|---|---|---|---|---|
| onesta | 30 % | 0,80 | — | — |
| trucco **lieve** | 50 % | 0,70 | **vinceva** | perde |
| trucco forte | 50 % | 0,45 | perdeva | perde |

E una quarta riga che la prova pretende e che è altrettanto importante: una posa che migliora
**tutt'e due** (50 %, 0,85) deve continuare a vincere, altrimenti la guardia avrebbe spento
l'obiettivo invece di sorvegliarlo.

`test_il_riempimento_non_compra_un_allungo` è §A.3, e
`test_il_margine_viene_prima_del_riempimento` è l'ordine delle due voci nella chiave.

### 5.4 §C — la forma, e la curva che non è una cessione (criteri 8 e 10)

`test_la_distribuzione_fa_una_curva_e_una_sola` costruisce la forma dello schizzo — gamba
dritta dal circolatore, curva, dorsale — e pretende che `turns_of` conti **una** curva e che la
catena stia nella propria forma; poi costruisce la stessa catena **senza** il diritto alla
curva, e pretende che cada; poi una catena con **due** curve, e pretende che cada anche con il
diritto. È il criterio 8 alla lettera: fallisce se la gamba si piega e fallisce se le curve
sono due.

`test_objective.py::test_la_curva_della_distribuzione_non_e_una_cessione` è il criterio 10,
misurato sulla tavola composta: il diario porta `conceded == ()` e **nessuna catena supera il
proprio budget di curve**.

### 5.5 §G — gli organi di servizio (criterio 12)

`test_un_organo_di_servizio_non_si_allontana_dal_pezzo_che_serve` prova il vincolo **dove
decide** — `is_valid` — e non su una tavola sola: per ogni appeso, una mossa che lo porta oltre
il proprio tetto è **non valida**, e nessun guadagno la compra.
`test_lo_stacco_puo_allungarsi_per_il_rettilineo_che_la_tratta_chiede` è §G.2: il tetto non è
il minimo da solo, è il minimo **o** il posto che gli accessori in linea pretendono.

La parte che **riporta indietro** uno stacco già lungo non c'è, ed è §7.7: l'ho scritta, ho
misurato che cosa faceva alle tavole, e l'ho tolta.

Sulle tavole vere il criterio si legge nelle prove che c'erano già,
`test_stacchi_minimi_e_interasse.py`, e nel numero di §1.3.

---

## 6. §D — la tavola 4, misurata

Il conto per esteso, con i comandi, è in **`dopo/prova-4-perche-non-esce.txt`**. In breve:

**L'ipotesi del pacchetto non è confermata.** §D proponeva che con il margine di §B nessun
pezzo potesse stare oltre `x 325`, e che quindi il confine di rete appeso alla macchina più a
destra cadesse dentro la griglia. Misurato:

```
formato 420 x 297: area x 10..360, y 16..251
griglia di instradamento: 140 colonne (indici 0..140), 94 righe

posa iniziale:          22 pezzi,  0 fuori dall'area
seminata dal tronco:    22 pezzi,  1 fuori dall'area
    utenze: x 365.0..370.0   y 158.5..163.5
dopo il ciclo:          22 pezzi,  1 fuori dall'area
    utenze: x 365.0..370.0   y 158.5..163.5
```

`utenze` è ACS-01, il confine del prelievo sanitario: cinque millimetri oltre il bordo destro
dell'area, due colonne oltre l'ultima che la griglia possiede. È **l'unico** pezzo fuori, su
ventidue, e la **posa iniziale lo teneva dentro**: è la fase del tronco a portarlo lì, perché
il confine si posa addosso all'utente che serve e l'utente che serve è la macchina più a
destra.

Il margine di D-143 non lo riporta dentro perché nessuno dei tre posti in cui è entrato è
quello che deciderebbe qui: la fase del tronco non legge il costo, e il ciclo rifiuta le mosse
che portano un pezzo **fuori** ma quel pezzo è già fuori quando il ciclo comincia — «una mossa
risponde di ciò che crea, non di ciò che trova».

**Non ho ampliato il perimetro.** Quel che servirebbe sta in `place.py` e in `spine.py`, e la
tavola 4 resta un pacchetto a sé — con, adesso, un numero solo da sistemare: cinque millimetri
su un pezzo su ventidue.

---

## 7. I rilievi, e le domande

### 7.1 L'acqua fredda della tavola 2 resta lontana, e non è l'organo ad essersi allontanato

Il criterio 3 non è raggiunto sulla tavola 2: 135,0 → 120,0 mm. La misura dice **dove non
cercare**:

```
acquedotto <- tee-drain-connection-cold-bollitore-cold-in (a)   min=15.0  gap=15.0  need=20.0
```

Il confine di rete sta **al proprio minimo** dal raccordo che lo regge, ed è esattamente ciò
che D-145 pretende: §G funziona. I centoventi millimetri sono la distanza fra quel **raccordo**
e il bollitore, cioè dove la posa mette il gruppo dell'acqua fredda — e la posa è `place.py`,
fuori perimetro.

C'è una cosa che il PM deve sapere prima di decidere il pacchetto che lo chiuderà: **niente
può tirare indietro quel gruppo con il costo di oggi.** Avvicinarlo non toglie una curva né un
attraversamento, e D-139 ha tolto i millimetri dalle voci di costo; D-145 dice esplicitamente
che la vicinanza **non torna come costo**. Quindi la strada è un vincolo — «un raccordo che
regge un confine di rete sta al minimo dalla macchina che il confine serve» — oppure una posa
che lo colloca già lì. Tutt'e due stanno fuori da questo pacchetto.

E c'è una cosa che il PM deve sapere **prima**: stringere §G sugli stacchi non lo avvicina, lo
**allontana**. §7.7 lo misura su tre varianti.

### 7.2 Il pettine di D-144 è bloccato dal simbolo del collettore — domanda al PO

Il criterio 9 non è raggiunto, e non per la posa. Sulla fixture delle due zone:

- le zone pendono da un `zone-manifold` largo 40 mm con `out_1` e `out_2` sulla faccia
  **inferiore**, a quindici millimetri l'uno dall'altro;
- chi pende da due attacchi affiancati su una faccia orizzontale **sta affiancato**: sulla
  stessa colonna non ci può stare;
- la dorsale dello schizzo del PO sarebbe **lo stesso collettore girato di novanta gradi**, con
  gli attacchi impilati sul fianco;
- `assets/symbols/zone-manifold.json` dichiara `allowed_rotations_deg: [0]`.

Per **D-049** quel campo è «un vincolo **tecnico**, non geometrico: dice in quali orientamenti
il pezzo si può disegnare in un impianto vero». Il collettore di zona non è fra i dodici che
D-049 nomina. **La domanda al PO è una riga**: un collettore di zona si può disegnare in
verticale? Se sì, `allowed_rotations_deg` diventa `[0, 90, 180, 270]` e il pettine ha dove
nascere; se no, D-144 su un impianto con collettore vuol dire un'altra cosa, e va detta.

Non l'ho cambiato da me: `HANDOFF.md` dice che nessun requisito MEP nasce dall'iniziativa DEV,
e questo è un requisito MEP scritto in un file di simboli.

Ho scritto e poi **tolto** la mossa che avrebbe portato un terminale sulla colonna di un altro:
misurata, non è mai valida — il posto è occupato da una parte e dall'altra la tratta si
piegherebbe — e una candidata che non può mai passare è codice che costa ricerca a ogni
tavola. La riga che la reggeva è nella storia del ramo, se serve.

### 7.3 La tavola 1 non entra nella finestra, e le due disposizioni si contendono il foglio

Il criterio 2 è raggiunto sulla tavola 2 (61,1 %) e non sulla tavola 1 (**42,9 %**, contro un
minimo di 45). Il conto, per esteso:

- l'area di disegno è 350 × 235 mm; con il margine di 25 mm per lato restano **300 × 185**;
- la tavola 1 è larga **esattamente 300 mm**: la dilatazione si è fermata lì, ed è il margine a
  fermarla;
- in **altezza** i vuoti della proiezione sono **due, di un passo ciascuno, cioè 5 mm in
  tutto**: i simboli coprono quasi per intero la fascia verticale che il disegno occupa, e una
  dilatazione che non sposta un pezzo rispetto a un altro **non ha niente da allargare** su
  quell'asse. A fattore 1,08 quei due vuoti restano di un passo (§7.5): l'altezza **non cambia
  affatto**, 117,5 mm prima e 117,5 mm dopo;
- 300 × 117,5 su 350 × 235 fa **42,9 %**. Per arrivare al 45 % servirebbero 123,4 mm di
  altezza, che su quell'asse non ci sono.

**Le due disposizioni si contendono il foglio, e su questa tavola non stanno insieme**: D-140
chiede almeno il 45 %, D-143 chiede 25 mm per lato, e D-142 vieta la sola mossa che le
concilierebbe — spostare un pezzo rispetto agli altri. Ho scelto il **margine**, perché §B.2 lo
dice in modo esplicito («non si stringe per far salire il riempimento») e perché è la
disposizione nata dal difetto che ha fatto bocciare `DRAW-012`. Il preflight lo dichiara:
`SHEET_BARELY_FILLED · t1`.

**Ed ecco il prezzo, in millimetri.** Ho misurato che cosa succederebbe togliendo il margine e
lasciando correre la dilatazione sulla tavola consegnata:

| fattore in più | ingombro | riempimento | margine che resta |
|---|---|---|---|
| — | 300,0 × 117,5 | 42,9 % | **25,0 mm** |
| × 1,2 | 322,5 × 117,5 | **46,1 %** | 13,75 mm |
| × 1,3 | 345,0 × 117,5 | **49,3 %** | 2,5 mm |

La riga di mezzo è esattamente la tavola che il PO ha bocciato: **322,5 mm di ingombro e
tredici millimetri e tre quarti dal bordo** sono i numeri della PR #41. Portare la tavola 1 in
finestra vuol dire tornare lì. Non è un'opinione: è il foglio.

È una decisione da confermare, e la porto al PM: **se il PO preferisce il riempimento al
margine, la tavola 1 torna in finestra stringendo il margine a 17,5 mm** — e allora D-143 va
riscritta, perché così com'è non lo permette.

### 7.4 Quello che vedo sulle tavole e che i numeri approvano

Il pacchetto chiede di guardarle, e questo è ciò che vedo.

1. **La tavola 1 resta una fascia in alto, con il terzo inferiore del foglio bianco.** I numeri
   dicono 4 pieghe, 1 attraversamento, squilibrio dei quadranti 1,92 — tutto buono — e il
   disegno è comunque sbilanciato in verticale. Non è un difetto che questo pacchetto potesse
   chiudere: nasce dal fatto che l'impianto è una linea orizzontale e che nulla, nel motore,
   distribuisce **in altezza**. Lo segnalo perché è la stessa specie di rilievo che il PO ha
   fatto sul bordo: si vede a occhio e nessun numero lo dice.
2. **Sulla tavola 1 la mandata della seconda pompa di calore corre a lungo alla propria quota
   prima di scendere.** È il rilievo che il DEV di `DRAW-012` aveva già scritto, ed è ancora
   lì: la linea rossa da PDC-02 attraversa mezzo foglio in orizzontale e poi scende. Con la
   dilatazione quel tratto si è allungato **in proporzione**, come tutto il resto, quindi non è
   peggiorato rispetto al disegno — ma resta la cosa più brutta della tavola.
3. **Sulla tavola 2 il bollitore e il suo gruppo stanno in basso a destra e il quadrante in
   basso a sinistra è vuoto**: lo squilibrio dei quadranti è 8,3, il preflight lo dice, e non è
   migliorato (era 8,16). La dilatazione non lo può toccare: allarga, non redistribuisce.

---
### 7.5 La griglia quantizza la dilatazione, e con un fattore piccolo la annulla

È il rilievo tecnico più importante che porto, e non è nel pacchetto.

Un vuoto lungo `g` passi, moltiplicato per il fattore `k` e riportato al passo, **cresce
soltanto se** `round(g·k) > g`, cioè se `g ≥ 0,5 / (k − 1)`. Tradotto:

| fattore | cresce solo un vuoto di almeno |
|---|---|
| 1,08 | **7 passi** (17,5 mm) |
| 1,25 | **2 passi** (5,0 mm) |
| 1,50 | **1 passo** (2,5 mm) |

Sulla tavola 1, a fattore 1,08, dei diciassette vuoti dell'asse orizzontale **uno solo** arriva
a sette passi: la dilatazione ha allargato quello, di un passo, e ha lasciato gli altri sedici
dov'erano. Due millimetri e mezzo su un disegno largo trecento.

**Perché il fattore si ferma a 1,08.** Non per prudenza: il passo successivo della scala, 1,09,
porta quello stesso vuoto da diciotto a **venti** passi — cinque millimetri in più — e il
disegno supera i trecento millimetri che il margine concede. La quantizzazione rende la ricerca
a scatti: fra 1,08 e 1,09 non c'è nulla di intermedio da prendere.

Ne segue una cosa che vale per il prossimo pacchetto: **la dilatazione paga dove i vuoti sono
grandi**, e su questi impianti i vuoti sono quasi tutti di uno o due passi, perché sono i minimi
di stacco che D-145 tiene stretti. Il riempimento «comodo» che il PO vuole non verrà mai da qui
finché il disegno sarà fatto di pezzi addossati: verrà da una posa che **distribuisce**, e
distribuire vuol dire spostare un pezzo rispetto a un altro — cioè proprio ciò che D-142 vieta
alla dilatazione. Non è una contraddizione del PO: è che le due cose sono due mosse diverse, e
questo pacchetto ne ha costruita una sola.

### 7.6 «Il riempimento sale per dilatazione e non per altro» non è vero, e va deciso

§E si aspettava che, con la dilatazione in campo, la guardia dovesse «verificare che il
riempimento sia salito **per dilatazione e non per altro**». Nel motore che consegno non è così,
e la scelta è mia: la spiego, perché il PM la deve poter ribaltare.

**Perché ho lasciato la finestra nella chiave di posa.** Il pacchetto è esplicito nel dire che
D-140 e D-141 **non si toccano**: la finestra resta 45–65 % e la copertura resta la guardia.
Toglierle dal costo della posa sarebbe stato toccarle. Quindi la posa insegue ancora la
finestra, e la dilatazione arriva dopo, su un disegno che ci è già quasi.

**Che cosa è cambiato davvero**, e si misura:

1. lo **stiramento del singolo tratto** non compra più riempimento (§A.3): è la mossa che il PO
   ha chiamato «proprio brutta»;
2. il **margine viene prima della finestra** nella chiave: allargarsi fino al bordo per far
   salire una percentuale non paga più. È la seconda mossa che il PO ha bocciato;
3. la **guardia di D-141 è un divieto** e non una soglia: il riempimento salito mentre la
   copertura scende non vale, nemmeno di poco.

**Che cosa non è cambiato**: la posa distribuisce ancora i pezzi anche per riempire, dentro il
margine. Se il PO intendeva che **nessuna** mossa della posa debba inseguire il riempimento — e
che la finestra debba essere un affare della sola dilatazione — allora la finestra esce dalla
chiave, la posa si compatta come faceva `main`, e la dilatazione deve riempire da sola. Sui
numeri di §7.5, **da sola non ce la fa**: i vuoti di questi impianti sono di uno o due passi e
non crescono. Le due cose vanno decise insieme, e non da me.

### 7.7 Tre varianti di §G, misurate sulle tavole: la più stretta disegna peggio

Il criterio 13 chiede **12 rosse invece di 13**, e nomina la prova che pretende che sulla
tavola composta nessuno stacco sia più lungo del proprio minimo senza una ragione. §G avrebbe
dovuto chiuderla. **Non la chiude**, e ho provato due strade per farlo. Le porto tutt'e due con
i numeri, perché la scelta fra loro è del PM e non mia.

| | **consegnata** | tetto stretto | tetto stretto + attuazione |
|---|---|---|---|
| tavola 2 — acqua fredda dal bollitore | **120,0 mm** | 192,5 mm | 192,5 mm |
| tavola 2 — lunghezza | **887,5 mm** | 1005,0 mm | 960,0 mm |
| tavola 2 — squilibrio quadranti | 8,30 | 7,21 | 7,97 |
| tavola 1 — acqua fredda dall'accumulo | 20,0 mm | **15,0 mm** | **15,0 mm** |
| tavola 1 — squilibrio quadranti | **1,92** | 3,78 ⚠️ | 3,78 ⚠️ |
| rilievi di preflight, in tutto | **2** | 3 | 3 |
| la prova rossa che il criterio 13 nomina | rossa | rossa | **verde** |

Sul ramo di partenza l'acqua fredda della tavola 2 sta a **135,0 mm**: le due varianti strette
la portano a 192,5, cioè **peggio di dove era**, con la linea tratteggiata che attraversa il
foglio da un capo all'altro.

**Che cosa sono le due varianti.**

1. **Il tetto stretto.** Il «vincolo dichiarato» di §G.2 ammette due letture, e sono tutt'e due
   dichiarate: il **rettilineo che la tratta pretende** — che non scende mai sotto lo stacco
   minimo fra due simboli, cioè **D-062** — oppure il solo **posto degli accessori in linea**.
   La seconda è più stretta sulla lettera. Misurata: stringe il corredo e **allontana il
   gruppo**, perché toglie al ciclo le mosse con cui lo avvicinava.
2. **L'attuazione.** Un vincolo monotono impedisce di allungare, non accorcia. Ho aggiunto al
   ciclo la regola che, fra due pose che costano uguale, prende quella che avvicina di più gli
   organi di servizio — non una voce di costo, che D-145 vieta, ma l'attuazione del vincolo. La
   prova è diventata verde. Il disegno no.

**Il meccanismo è quello che ci si aspetta da un greedy**: sia stringere i vincoli sia accettare
una posa che costa uguale cambiano la **traiettoria** della ricerca, e la traiettoria nuova
finisce in un minimo diverso. Il vincolo faceva il proprio mestiere — gli stacchi si
accorciavano — e il disegno intero peggiorava altrove.

**Ho consegnato la variante che disegna meglio**, e non è un compromesso sulla disposizione: le
due letture del tetto sono tutt'e due dichiarate, e fra due letture ammesse ho preso quella che
lascia la tavola migliore, perché è il PO che giudica il prodotto (D-146). Su `DRAW-010` e su
`DRAW-012` la risposta a «una riga verde vale una tavola peggiore?» è stata **no** due volte.

Tutt'e due le varianti sono nella storia del ramo, pronte a tornare se il PM decide
diversamente: i commit sono «il vincolo di D-145 morde, e adesso ripara anche» e «il tetto dello
stacco è il rettilineo della tratta, e perché».

---

## 8. La suite, e il determinismo

*(sezione compilata)*

---

## 9. Le misure, prima e dopo

`prima/` è **il ramo di partenza** — la testa di `DRAW-012`, `17ff425` — e non `main`: è il
confronto che il pacchetto chiede.

```
$ .venv/bin/python docs/collaudi/DRAW-013/criteri.py \
      docs/collaudi/DRAW-013/prima docs/collaudi/DRAW-013/dopo
```

| misura | t1 prima | **t1 dopo** | t2 prima | **t2 dopo** |
|---|---|---|---|---|
| larghezza dell'ingombro | 322,5 mm | **300,0 mm** | 315,0 mm | **300,0 mm** |
| altezza dell'ingombro | 115,0 mm | **117,5 mm** | 167,5 mm | **167,5 mm** |
| **margine minimo dal bordo** | 12,5 mm | **25,0 mm** | 17,5 mm | **25,0 mm** |
| margine che il disegno poteva permettersi | 12,5 mm | 25,0 mm | 17,5 mm | 25,0 mm |
| **curve** | 4 | **4** | 5 | **5** |
| **attraversamenti** | 1 | **1** | 1 | **1** |
| tratte con andata e ritorno | 0 | 0 | 0 | 0 |
| riempimento | 45,1 % | 42,9 % | 64,1 % | 61,1 % |
| riempimento senza il pezzo più isolato | 41,2 % | 38,9 % | 55,0 % | 51,9 % |
| copertura dell'ingombro | 0,750 | 0,703 | 0,750 | 0,656 |
| squilibrio fra i quadranti | 1,94 | 1,92 | 8,16 | 8,30 |
| lunghezza *(misura, non giudizio — D-139)* | 762,5 mm | 735,0 mm | 952,5 mm | 887,5 mm |
| **fattore di dilatazione** | — | **1,08** | — | **1,25** |
| acqua fredda dal pezzo che alimenta | 40,0 mm | **20,0 mm** | 135,0 mm | 120,0 mm |
| simboli / tratte | 39 / 21 | 39 / 21 | 41 / 23 | 41 / 23 |

Come si leggono le tre righe che peggiorano:

- **riempimento**: scende perché la posa non lo insegue più fino al bordo, e la dilatazione lo
  risale solo fin dove il margine permette. Sulla tavola 2 resta in finestra; sulla tavola 1
  no, ed è §7.3;
- **copertura**: scende perché è una misura **relativa all'ingombro** e l'ingombro è cresciuto
  — §5.1 lo misura su una tavola di prova e ne spiega il meccanismo. Nessun pezzo si è
  allontanato dagli altri: i vuoti sono cresciuti tutti dello stesso fattore;
- **squilibrio dei quadranti** della tavola 2: 8,16 → 8,30, cioè fermo. La dilatazione allarga,
  non redistribuisce, e il bollitore resta dov'è.

Le due righe da guardare per prime restano **margine** e **curve/attraversamenti**: il primo è
il difetto che il PO ha nominato, i secondi sono il prezzo che questo pacchetto **non** ha
pagato.

### I rilievi di preflight

| | prima | dopo |
|---|---|---|
| tavola 1 | *nessuno* | `SHEET_BARELY_FILLED` (43 % < 45 %) |
| tavola 2 | `DRAWING_ALL_ON_ONE_SIDE` (8,2×) | `DRAWING_ALL_ON_ONE_SIDE` (8,3×) |

Il rilievo nuovo sulla tavola 1 è **dichiarato e voluto**: è il prezzo di §7.3, ed è il motivo
per cui quel paragrafo esiste. **Nessuna delle due tavole porta `DRAWING_TOUCHES_THE_BORDER`**,
che è il rilievo nuovo di questo pacchetto: il margine è rispettato su tutt'e due.
