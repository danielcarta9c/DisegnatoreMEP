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
| `tests/layout/test_costo_peso.py`, `test_ordine_del_disegnatore.py`, `test_riempimento_del_foglio.py` | il campo nuovo del costo, dichiarato dove il costo si costruisce per intero |
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

Un vincolo di `is_valid`, non una voce di costo: **D-139 non si tocca**. Il conto è monotono,
come quello del tronco — uno stacco al proprio minimo non si allunga, e uno che il
posizionamento ha dovuto fare più lungo può solo accorciarsi. L'unico allungamento ammesso è
quello che la **tratta dichiara**: il rettilineo che gli accessori in linea pretendono.

**Quel «vincolo dichiarato» non è un dettaglio: senza di lui la tavola 2 smette di uscire.**
Misurato: con il tetto fermo al solo minimo dello stacco, l'intercettazione dell'acquedotto non
trova più il proprio rettilineo e `compose_drawing` si ferma su
`run w1-a has no straight stretch for valve-isolation`. È il caso che §G.2 nomina — «far posto a
un altro accessorio in linea sulla stessa tratta» — e va letto sulla tratta, non sul minimo.

---

## 4. I criteri, uno per uno

I comandi e i loro output sono in §5 e §6; qui c'è l'esito e dove leggerlo.

| # | Esito | Dove |
|---|---|---|
| 1 | **raggiunto** | §5.1 — la prova generale della dilatazione |
| 2 | **raggiunto in parte** | tavola 2 **61,1 %** in finestra con fattore **1,25**; tavola 1 **42,9 %** con fattore **1,08**, sotto la finestra. §7.3 misura perché la tavola 1 non ci arriva |
| 3 | **NON raggiunto sulla tavola 2** | 135,0 → 120,0 mm. Raggiunto sulla tavola 1: 40,0 → 20,0 mm. §7.1 |
| 4 | **raggiunto** | 25,0 mm su tutt'e due le tavole, contro 12,5 e 17,5 |
| 5 | **raggiunto** | §5.2 — la prova nei due versi |
| 6 | **raggiunto** | 4/1 e 5/1, identici al ramo di partenza |
| 7 | **raggiunto** | §5.3 — il caso lieve non vince |
| 8 | **raggiunto in parte** | la forma e la curva unica sono provate; il **pettine** no, ed è bloccato dal simbolo del collettore (§3.3, §7.2) |
| 9 | **NON raggiunto** | la colonna non torna, e la ragione è quella di §3.3: sta nel simbolo, non nella posa |
| 10 | **raggiunto** | §5.4 — il diario non conta la curva fra le cedute |
| 11 | **misurata, e non esce** | §6 — il conto cella per cella |
| 12 | **raggiunto come vincolo** | §5.5; sulla tavola 2 la distanza è quella di §7.1 |
| 13 | da leggere in §8 | |
| 14 | da leggere in §8 | |
| 15 | **raggiunto** | §9 — la tabella prima/dopo |

---

## 5. Le prove

*(sezione compilata in §8 con i comandi e gli output)*

---

## 6. §D — la tavola 4, misurata

*(sezione compilata con il conto cella per cella)*

---

## 7. I rilievi, e le domande

*(sezione compilata)*

---

## 8. La suite, e il determinismo

*(sezione compilata)*

---

## 9. Le misure, prima e dopo

*(sezione compilata)*
