# DRAW-015 — consegnato, in attesa del sì del PO

**Stato:** **CONSEGNATO**, non fuso. Rapporto e tavole in `docs/collaudi/DRAW-015/`.
**La fusione è del PO**, e si dà guardando le tavole (D-146, D-147).

> Le cinque tavole sono in `docs/collaudi/DRAW-015/tavole/`. **Escono tutte e cinque, con
> zero tratte cedute**; l'unico rilievo bloccante è sull'impianto 3 ed è strutturale (B7).
> Che cosa resta storto, lo dice §1 del rapporto — e lo dice guardando, non contando.

Sotto c'è il pacchetto che **diventa attivo quando il PO approva la fusione**. Finché non
l'ha approvata, l'incarico corrente è: rispondere al PO su `DRAW-015`.

---

# DRAW-016 — Il disegno smette di essere un nastro

**Titolo:** Il disegno smette di essere un nastro
**Da svolgere:** l'agente unico (**D-147**), con agenti paralleli in sessione (**D-152**)
**Release:** 0.3 — generalizzazione
**Approvazione della fusione:** **del PO**, e si dà guardando le tavole (D-147, D-146)

> **Questo pacchetto ha un solo obiettivo, ed è visivo:** che le cinque tavole smettano di
> essere una fascia appoggiata nella metà alta del foglio, e che i confini di rete smettano
> di finire dall'altra parte del disegno.
>
> `DRAW-015` ha costruito l'attrezzo — il revisore, e quattro regole che sanno nominare la
> propria violazione. **Adesso l'attrezzo si usa per quello per cui è stato fatto**: si
> compone, si guarda, e quello che si impara diventa una riga (D-153).

## Perché

Il PO, guardando le due tavole della prova: «c'è molto da migliorare ancora, non assomiglia
a come dovrebbe essere un disegno» (I-082). Dopo `DRAW-015` le tavole sono cinque e le
autostrade sono dritte, ma il difetto che il PO ha nominato **non è stato toccato**, ed è
misurato: `DRAWING_ALL_ON_ONE_SIDE` dà 5,2 sull'impianto 1, 7,6 sul 2, 3,9 sul 4, contro un
limite di 3. Il terzo inferiore del foglio è vuoto su tutte e cinque.

E accanto ce n'è uno che il numero non dice: **il prelievo ACS sta all'estrema destra con
una linea che attraversa mezzo foglio vuoto**, su tre tavole su cinque. Il controllo A1 lo
esclude dal conto delle fasce — un confine di rete «va accanto all'utente che serve»
(I-061) — ma **nessuna riga dice dove metterlo**, e nei cinque piani l'ho messo lontano io.

## Prima di cominciare: tre domande al PO

**Questo pacchetto non parte finché il PO non ha risposto alle prime due.** Sono in
`HANDOFF.md`, e sono di contenuto:

1. **B7** — `turns_allowed` vale zero senza guardare le facce delle porte, e quattro catene
   su tre impianti non si possono raddrizzare. *O il catalogo cambia, o il bilancio diventa
   il minimo raggiungibile.*
2. **B1 contro B3 sulla cascata** — il collettore verticale che B3 pretende fa piegare la
   catena che B1 vuole dritta: la tavola è giusta e il numero dice che è sbagliata.
3. **Dove sta un confine di rete** — e questa il pacchetto la può anche portare al PO
   **componendo**, con due tavole a confronto, che è il modo che D-153 prescrive.

## Le cose da fare

### 1. La regola che distribuisce in verticale — composta, non dedotta

Si compone una tavola alla volta, si guarda, e la riga nasce da lì. **Non si scrive in
astratto**: è così che è nata la funzione di costo.

Il punto di partenza è che oggi tutte le corsie stanno fra y=100 e y=260 su un'area alta
358: le ho messe io così, per abitudine. Va provato che cosa succede distribuendo davvero —
e va misurato con `DRAWING_ALL_ON_ONE_SIDE`, tavola per tavola, prima e dopo.

⚠ **La cura ovvia è già stata bocciata**: allargare il disegno per riempire è D-142, che il
PO ha respinto («era meglio prima») e che **D-149** ha ritirato. Qui si distribuiscono i
**pezzi**, non si stira il disegno.

### 2. Dove sta un confine di rete

Una riga in `docs/regole-del-piano.md`, con il proprio controllo e la propria tavola. Il
materiale c'è: I-017, I-061, D-145 («un organo di servizio sta addosso al pezzo che serve»),
e `flow.BOUNDARY_FUNCTION`, che dichiara già che un confine non ha una posizione propria.

**Il contenuto è del PO**: il pacchetto porta due tavole a confronto e la domanda.

### 3. Il revisore impara le cure che oggi non ha

Oggi cura quattro rilievi e si ferma su tutto il resto. Quello che ha incontrato e non sa
chiudere, nominato dal rapporto: `RUN_OVERSHOOTS_ITS_PORT`, `TOO_MANY_CROSSINGS`,
`DRAWING_ALL_ON_ONE_SIDE`.

**Non si aggiunge una cura senza la sua regola** (`REGOLA_DEL_RILIEVO`): una correzione che
non sa dire quale regola la vuole è il solutore travestito.

⚠ E non si aggiunge la cura di `DRAWING_ALL_ON_ONE_SIDE` finché il punto 1 non ha prodotto
una riga: senza, il revisore rifarebbe D-142 da solo.

### 4. Il revisore prova più di una cura per giro

Misurato su `DRAW-015`: su quattro impianti su cinque la **prima** correzione peggiora, il
revisore si ferma, e le correzioni successive — che magari andavano bene — non vengono mai
provate. Un giro che ricade indietro e prova la cura successiva **non è una ricerca**: è un
tetto dichiarato, come il tetto dei giri.

**Il confine da non passare, e va scritto nel pacchetto prima di cominciare:** il numero di
cure provate per giro è un tetto fisso e piccolo, e il criterio di scelta resta
**lessicografico**. Il giorno in cui diventasse una somma pesata su un albero di tentativi,
sarebbe il solutore rientrato dalla finestra.

### 5. I due documenti del motore dichiarano che cosa è storia

`docs/pm/2026-09-11-architettura-della-posa-a-fasi.md` e
`docs/pm/2026-09-16-come-ragiona-il-motore-e-come-dovrebbe.md` descrivono la fase del tronco
e il ciclo di costo **come il modo in cui si decide la posa**. Oggi lo dichiara solo
`HANDOFF.md`, dall'esterno, ed è il **terzo stato** che `DRAW-015` ha tolto da tutto il
resto. Stessa regola: o vigente, o dice in testa che è storia e quale decisione l'ha
superato. Stesso trattamento per `docs/plans/2026-08-06-piano-costruzione-skill.md`
(«Stato: in corso»), `docs/standard/COLD_EYE_REVIEW.md` e `docs/DEFERRED.md:254`.

## Perimetro

**Dentro:** `docs/collaudi/PROVA-PIANO/impianto-*.json` (i piani si ricompongono, ed è il
lavoro); `docs/regole-del-piano.md`; `src/disegnatore_mep/piano/revisore.py`;
`validation/regole.py` per i controlli nuovi; i cinque documenti dell'elenco 5;
`docs/collaudi/DRAW-016/`.

**Fuori:** il motore che funziona — `route.py`, `inline.py`, `place.py`, `legend.py`,
`labels.py`, `addresses.py`, `graphics/**` — salvo quando una cura dichiarata lo richiede, e
allora si dice perché. **Fuori** `highways.py` e `turns_allowed` finché il PO non ha risposto
alla domanda 1. **Fuori** qualunque decisione MEP che il PO non abbia dato.

**Non si inventa nessuna regola.** Una riga di `regole-del-piano.md` senza fonte è un difetto
del pacchetto, non un contributo.

## Criteri di accettazione

Ogni criterio si chiude con **il comando eseguito e il suo output**.

1. **`DRAWING_ALL_ON_ONE_SIDE` migliora su almeno tre tavole su cinque**, con il numero prima
   e dopo per tutte e cinque. Se su una peggiora, si dice quale e perché.
2. **La regola che distribuisce in verticale è scritta**, con fonte, controllo e **la tavola
   che l'ha generata**. Se dal comporre non ne esce nessuna, il pacchetto lo dichiara: una
   riga dedotta a tavolino è un difetto, non un contributo.
3. **Nessuna tavola perde quello che ha guadagnato in `DRAW-015`**: zero tratte cedute su
   tutte e cinque, e i rilievi bloccanti non aumentano su nessuna.
4. **Il revisore chiude almeno un rilievo in più** di quelli che chiude oggi, e ogni cura
   nuova porta il nome della propria regola.
5. **Su almeno un impianto il revisore serve più di zero giri**, e il rapporto porta la
   tavola prima e la tavola dopo.
6. **Nessun documento resta in terzo stato**, compresi i cinque dell'elenco 5.
7. **Il saldo della suite non peggiora**, zero `skip` e zero `xfail` nuovi, e `ruff` e `mypy`
   restano verdi.

## Consegna

Una PR sola verso `main`, **non fusa finché il PO non ha visto le tavole e detto di sì**.

**Le tavole, per prime** (D-146). Rapporto in `docs/collaudi/DRAW-016/RAPPORTO.md`.

**Prima di chiedere l'approvazione:**

1. **Guarda le tavole**, e mettile accanto a quelle del disegnatore del PO,
   `docs/input-pm/riferimenti-grafici/`. Se una ti sembra sbagliata e i numeri dicono che va
   bene, scrivilo: su `DRAW-015` è successo due volte su due ed è servito.
2. **Misura la non-regressione prima, non dopo.** Qui sono il 3 e il 7.
3. **Se una disposizione del PO ammette due letture, fermati e chiedi al PO.**

## Quello che questo pacchetto **non** chiude

- **Il DXF**, che è la contropartita di un prezzo già pagato (D-023 sospesa, D-148): resta
  una domanda al PO su **quando**, non su **se**.
- **L'elenco delle regole**, che il PO ha dichiarato aperto (I-085).
- **La composizione a corsie** della ricerca del 4 agosto §2.2 — entra quando l'avremo
  composta almeno una volta, con la sua tavola.
