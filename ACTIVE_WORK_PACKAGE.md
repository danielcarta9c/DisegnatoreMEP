# DRAW-014 — Tutte e cinque le tavole escono

**Titolo:** Tutte e cinque le tavole escono
**Scritto e svolto da:** l'agente unico (**D-147**, `docs/governance/OPERATING_MODEL.md` §1.2.1)
**Data:** 2026-09-19
**Stato:** **ATTIVO.** Sostituisce `DRAW-013`, fuso con la PR #44
**Release:** 0.3 — generalizzazione
**Approvazione della fusione:** **del PO**, e si dà guardando le tavole (D-147, D-146)

> **Questo pacchetto è il primo scritto sotto D-147**, e si vede: è corto. Non deve
> proteggere un passaggio di consegne che non c'è più. Quello che deve fare è **non lasciare
> fuori perimetro il file dove sta il blocco** — l'errore che ha fermato quattro pacchetti
> di fila.

---

## Perché

Il PO, il 19 settembre, dopo la PR #44:

> «A mio avviso il progetto sta per essere buttato. Ancora siamo fermi a far uscire solo le
> prime due tavole e a far piccoli aggiustamenti quando invece le tavole di test 3/4/5 non
> escono proprio.»

Ha ragione, e la misura lo conferma: su cinque impianti di prova ne uscivano **due**, e le
altre tre morivano per **una sola tratta** ciascuna — su decine — tutte contro il **bordo
destro dell'area A3**.

## Le quattro disposizioni che lo governano

| | |
|---|---|
| **D-147** | PM e DEV sono un agente solo; la fusione la approva il PO guardando le tavole |
| **D-148** | Oltre l'A3 si va: i formati ordinari sono A4, A3, A2, A1 |
| **D-149** | Il riempimento del foglio esce dagli obiettivi e torna una misura; la dilatazione è ritirata |
| **D-150** | Una tratta che non si instrada non uccide più la tavola: ripiego dichiarato, marcato e nominato dal preflight |

## Perimetro

**Dentro:** `graphics/standard.py` e `graphics/frame.py` (i formati); `layout/route.py`,
`layout/inline.py`, `layout/compose.py` (il ripiego dichiarato); `layout/improve.py` (il
riempimento fuori dalla chiave); `validation/preflight.py` e `cli.py` (il rilievo e la porta);
`graphics/sheet.py` (il segno). **E `layout/place.py` quando la cura di una causa lo
richiede**: è il file che quattro pacchetti hanno tenuto fuori, ed è dove stanno le cause.

**Fuori:** qualunque decisione MEP che il PO non abbia dato; le convenzioni grafiche non
toccate dalle quattro disposizioni.

## Criteri di accettazione

Ogni criterio si chiude con **il comando eseguito e il suo output**.

1. **Tutti e cinque gli impianti di prova producono una tavola**, e il rapporto si apre con i
   cinque PDF (D-146). Per ciascuno dice il **formato** su cui è uscita e **quante tratte
   sono cedute**.
2. **Una tavola senza tratte cedute non è degradata in nessun modo**: il ripiego non si
   accende, la validazione geometrica la misura come sempre, e il preflight non porta
   `RUN_UNRESOLVED`.
3. **Il ripiego non anticipa mai la scala dei formati**: un impianto che entra su un foglio
   esce su quel foglio, non su uno più grande col ripiego. Una prova lo mostra.
4. **Il ciclo di miglioramento continua a vedere l'errore** e non accetta una posa che non si
   instrada. Una prova lo mostra: i due interruttori — `tolerant` e `last_resort` — restano
   separati.
5. **Le tavole 1 e 2 non peggiorano** su curve e attraversamenti rispetto alla PR #44 (4/1 e
   5/1), adesso che il riempimento è uscito dalla chiave. Un peggioramento va **spiegato e
   guardato**, non giustificato con un numero.
6. **Il riempimento non decide più niente nella posa**, e una prova lo mostra sulla chiave di
   costo. Resta come misura nel rapporto e nel preflight.
7. **Il saldo della suite non peggiora** rispetto alla PR #44 (12 rosse, 1500 verdi). Le
   prove che difendevano un comportamento **revocato dal PO** si riscrivono dichiarando che
   cosa difendono adesso — **non si convertono in `skip` né in `xfail`, e non si allenta
   nessuna soglia**.
8. **Determinismo:** doppia generazione dalla CLI con la stessa impronta.
9. **Le cinque tavole sono misurate e riferite**: curve, attraversamenti, incroci, ingombro,
   margine minimo dal bordo, riempimento come misura, e le tratte cedute nominate una per una.

## Consegna

Una PR sola verso `main`, **non fusa finché il PO non ha visto le tavole e detto di sì**.

**Le tavole, per prime** (D-146). Il rapporto si apre con i cinque PDF e, per ogni impianto,
dice formato e tratte cedute. Rapporto in `docs/collaudi/DRAW-014/RAPPORTO.md`.

**Prima di chiedere l'approvazione:**

1. **Guarda le tavole.** Se una ti sembra sbagliata e i numeri dicono che va bene, scrivilo:
   è il rilievo più utile che puoi portare, ed è due volte su due il modo in cui i difetti
   veri sono stati trovati qui.
2. **Misura i criteri di non-regressione prima, non dopo.** Qui sono il 5 e il 7.
3. **Se una disposizione del PO ammette due letture, fermati e chiedi al PO.**

## Quello che questo pacchetto **non** chiude, e va detto al PO

- **Le cause vere delle tavole 3 e 5.** Il PO ha scelto «prima degrada, poi curo le cause»
  (I-081): la prima metà si chiude qui, la seconda è il lavoro successivo. Le cause, misurate
  su A2: un ostacolo vero a due passi dove ne servono cinque (impianto 5); uno stacco di 5 mm
  con un accessorio in linea che ne chiede 7,5 (impianto 3).
- **Il formato definitivo.** D-148 è dichiarata **momentanea** dal PO stesso: quando le
  cinque tavole escono, la domanda «quale formato serve davvero» si riapre.
- **Il tempo di un giro.** La suite gira in **40–66 minuti** e una tavola che scala fino
  all'A1 può costare decine di minuti. Con un'ora a giro una sessione ci sta dentro una
  volta sola, ed è metà della lentezza di questo progetto. Non è in questo perimetro, ma è
  la prima cosa da mettere nel prossimo.
