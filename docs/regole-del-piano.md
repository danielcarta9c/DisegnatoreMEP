# Le regole del piano

**Aperto il 20 settembre 2026 · Stato: vigente, e per dichiarazione del PO non è finito**

> Le regole con cui si **compone** una tavola. Non sono pesi da minimizzare: sono le
> istruzioni che il pianificatore segue e che il revisore verifica
> (`ARCHITETTURA-DEL-PIANO.md`, D-151).

## Come si scrive una regola qui, e perché così

**Una regola è un controllo che sa nominare la propria violazione** (D-153). Se non si può
misurare, il revisore non la può usare, e resta un'intenzione: è la differenza fra
«l'autostrada deve essere dritta» e «la tratta `s3` piega quattro volte, e su un'autostrada
le pieghe ammesse sono zero».

Ne seguono tre obblighi per chi aggiunge una riga:

1. **una fonte** — una decisione, un input del PO, la ricerca del 4 agosto, o la tavola che
   l'ha generata. Una riga senza fonte non entra: è così che è nata la funzione di costo;
2. **un controllo**, con il suo nome. Se non esiste ancora, si scrive `da scrivere` e si dice
   che cosa dovrebbe misurare. Una regola senza controllo è lavoro aperto, non una regola;
3. **una tavola** su cui la violazione si vede, quando c'è.

**Le regole si aggiungono componendo, una tavola alla volta** (D-153) — non in astratto.

---

## A. Dove stanno i pezzi

### A1 — Tre macro fasce verticali

Da sinistra a destra: **generazione** · **accumuli e scambiatori** · **distribuzione**. Ogni
pezzo posabile sta nella fascia della propria categoria.

*Fonte:* PO, 20 settembre 2026 (**D-154**), che precisa **D-041** — quella nominava due poli,
generatori a sinistra e distribuzione a destra, e non diceva che cosa sta in mezzo.
*Controllo:* `da scrivere` — ogni pezzo grosso ricade nella fascia della propria categoria, e
le fasce non si accavallano in orizzontale.

### A2 — Chi sta in parallelo si impila

Più generatori, più terminali, più pompe pari fra loro: **incolonnati**, non affiancati.
Chi non è un pezzo grosso — raccordi, organi, strumenti — **esce dalla fila** e si posa alla
fine, sulla campata fra i pezzi che la sua tratta unisce.

*Fonte:* **D-118**; la fascia dei generatori a sinistra è **D-041**.
*Controllo:* `tests/layout/test_zone_dei_pezzi_grossi.py` (posa); `da scrivere` come rilievo
sulla tavola.

> ⚠ **Correzione di citazione, 20 settembre.** Il codice attribuisce questa regola a
> **D-119** (`place.py`, `improve.py`, `test_zone_dei_pezzi_grossi.py`) e lo hanno fatto
> anche le note dei due piani e il README della prova. **D-119 è un'altra cosa** — l'area di
> rispetto dei raccordi. La regola è **D-041 + D-118**. Correggere le citazioni è dentro
> `DRAW-015`.

### A3 — L'ordine del processo si legge da sinistra a destra

*Fonte:* **D-060**, **D-041**.
*Controllo:* `da scrivere`.

### A4 — Un organo di servizio sta addosso al pezzo che serve

Valvole di intercettazione e sicurezza, scarichi, sfiati, manometri, vasi, gruppi di
riempimento, filtri, confini di rete: lo stacco che li porta è **il proprio minimo su
griglia**, e si allunga solo per un vincolo dichiarato. È **leggibilità**, non estetica: una
valvola lontana da tutto è equivoca.

*Fonte:* **D-145** (PO, I-076).
*Controllo:* vincolo del motore, `tests/layout/test_vicinanza_valvole.py`.

---

## B. Come corrono le linee

### B1 — Prima le autostrade, e il più dritte possibile

La struttura si tira prima del corredo, e la sua **rettilineità** viene prima
dell'ottimizzazione degli stacchi. Il precedente che l'ha imposta: una tavola in cui curve e
attraversamenti erano ottimizzati **sugli stacchetti** mentre l'autostrada faceva «sta curva
senza senso».

*Fonte:* PO, 20 settembre 2026 (**D-154**); il precedente è del 19 (**D-151**).
*Controllo:* `da scrivere` — serve che la geometria sappia **quali tratte sono autostrada**;
`RUN_WITH_TOO_MANY_BENDS` oggi conta le pieghe di tutte allo stesso modo, ed è il difetto.

### B2 — Dal circolatore un tratto dritto, **una** curva, poi la dorsale a pettine

Dal circolatore esce un rettilineo e il ritorno rientra con un rettilineo: questo pezzo non
si piega. Poi è ammessa **una curva, e una sola**. Dopo la curva corrono mandata e ritorno
**affiancati e paralleli**, e i terminali si attaccano **a pettine** sul fianco, ciascuno col
proprio stacco corto, impilati.

*Fonte:* **D-144** (PO, I-075, con schizzo in
`docs/input-pm/riferimenti-grafici/2026-09-18/distribuzione-dorsale-a-pettine.png`).
*Controllo:* `da scrivere`. *Tavola:* impianto 5 composto, `docs/collaudi/PROVA-PIANO/`.

### B3 — Più generatori o più terminali ⇒ **collettore verticale**

Le macchine in parallelo si attaccano a una **catena di T verticale e allineata**, con uno
stacco corto ciascuna, invece di tirare ognuna la propria tratta verso la destinazione.

*Fonte:* PO, 20 settembre 2026 (**D-154**).
*Controllo:* `da scrivere`. *Tavola:* impianto 5 composto — i due collettori della cascata.

### B4 — Un organo in linea non spezza il tratto

Una **valvola a tre vie** si posa con **ingresso e uscita allineati**; il terzo attacco esce
di lato. Vale per ogni organo che sta *sulla* linea: la linea passa, non si piega intorno a
lui.

*Fonte:* PO, 20 settembre 2026 (**D-154**).
*Controllo:* `da scrivere` — le due porte in linea del pezzo stanno alla stessa quota, e la
tratta che le unisce non ha pieghe nel suo intorno.

### B5 — Una tratta con più accessori in linea vuole il proprio rettilineo

Gli accessori in catena stanno a distanze fisse dalla porta (I-044): se la tratta non ha il
rettilineo che chiedono, non ci stanno. Sull'impianto 5 le tratte verso i terminali ne
portano tre — due intercettazioni e un circolatore — e vogliono **40 mm** liberi.

*Fonte:* **nata componendo**, 20 settembre 2026. *Tavola:* impianto 5 composto.
*Controllo:* c'è già, ed è il motore che lo dice bene: «questa tratta è lunga 10 mm ma i suoi
accessori ne chiedono 15».

### B6 — Due linee fra gli stessi due raccordi si separano in quota

Mandata e ricircolo che uniscono la stessa coppia di raccordi non possono stare alla stessa
altezza: si leggono come una sola linea.

*Fonte:* **nata componendo**, 20 settembre 2026. *Tavola:* impianto 5 composto.
*Controllo:* `PARALLEL_RUNS_TOO_CLOSE`, `RUNS_OVERLAP_LENGTHWISE`.

---

## C. Come si prende un pezzo

### C1 — Un pezzo si prende dal lato delle sue porte

La miscelatrice del radiante ha `hot_in` a sinistra, `out` a destra e `cold_in` sotto: presa
dall'alto non si instrada niente. Il piano deve avvicinarsi dal lato giusto.

*Fonte:* **nata componendo**, 20 settembre 2026. *Tavola:* impianto 5 composto.
*Controllo:* l'errore lo dà l'instradamento; `da scrivere` come rilievo che lo nomina prima.

### C2 — La rotazione si deduce, tranne dove c'è una scelta

Si deduce per un **raccordo** e per un pezzo con **un attacco solo**. Una **macchina con due
o più attacchi ha una scelta**, e quella scelta è del pianificatore.

*Fonte:* **D-004**, **I-027**; la forma stretta è del 20 settembre 2026.
*Controllo:* `scripts/piano.py::orienta` (da portare in `src/`, `DRAW-015`).

### C3 — La mappa degli attacchi si rifà **solo per i raccordi**

Rifarla su una macchina è un **errore di contenuto**: il 20 settembre ha mandato l'acqua
fredda sull'uscita primaria dell'accumulo. Il grafo era giusto e il disegno era sbagliato.

*Fonte:* **D-004**, **I-027**; il precedente è del 20 settembre, e l'ha visto il PO a occhio,
non una misura.
*Controllo:* `da scrivere` — un confronto fra il grafo e ciò che la tavola mostra collegato.
È il controllo più importante dell'elenco, perché è l'unico difetto di **contenuto** nato da
una scelta **grafica**.

---

## D. Il foglio

### D1 — Il disegno non arriva al bordo

Margine di rispetto ampio sui disegni scarichi — 25 mm — che si stringe fino a 10 solo se il
disegno è davvero pieno.

*Fonte:* **D-143** (PO, I-074).
*Controllo:* `DRAWING_TOUCHES_THE_BORDER`.

### D2 — Il riempimento del foglio **non è un obiettivo**

Si riporta come misura, come la lunghezza (D-139). Il formato si sceglie sulla scala
ordinaria A4 → A3 → A2 → A1 (D-148, dichiarata momentanea dal PO).

*Fonte:* **D-149**, **D-148** (PO, I-079, I-080).
*Controllo:* `SHEET_BARELY_FILLED`, `SHEET_TOO_FULL` — **misure**, non difetti da chiudere.

### D3 — Il disegno non sta tutto da una parte

*Fonte:* **D-060**; il difetto è misurato sulle due tavole composte del 20 settembre — 5,2
volte l'inchiostro fra quadrante pieno e vuoto sull'impianto 1, **9,0** sul 5.
*Controllo:* `DRAWING_ALL_ON_ONE_SIDE`. **È il primo difetto aperto del pianificatore.**

---

## Quello che manca, e si sa che manca

- **Nessun controllo sa che cos'è un'autostrada.** Finché la geometria non distingue
  struttura e corredo, B1 non è verificabile e `RUN_WITH_TOO_MANY_BENDS` conta una piega
  della dorsale come una piega di uno stacchetto. È il difetto che ha generato D-151.
- **La composizione a corsie** della ricerca del 4 agosto §2.2 — le dorsali di mandata e
  ritorno con i componenti appesi — è misurata su due tavole vere e **non è ancora una riga
  qui**, perché non è stata ancora composta da noi. Quando lo sarà, entra con la sua tavola.
- **Il PO ha detto che l'elenco è aperto**: «le regole sono sempre le stesse, vanno solo
  aggiunte altre e migliorate» (I-085, aperta).
