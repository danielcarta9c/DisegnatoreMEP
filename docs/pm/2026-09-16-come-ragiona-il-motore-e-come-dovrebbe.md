# Come ragiona il motore, e come ragiona un disegnatore — l'analisi, 16 settembre 2026

**Chi decide:** PO (Daniel Carta), dominio MEP e convenzioni di rappresentazione.
**Chi scrive:** il PM.
**Perché esiste:** il PO, guardando la tavola 4: «è inutile che continuiamo a ottimizzare un
motore di disegno che se non ragiona bene in questo ordine e non ha regole per fare queste
cose: stiamo ottimizzando la punta di una lancia storta».
**Che cosa contiene:** l'ordine che il PO ha dettato, l'ordine che il motore esegue oggi, e
le **cinque differenze misurate** fra i due. Non una opinione: ogni riga porta il comando e
il numero.

---

## 1. L'ordine del disegnatore, come il PO l'ha dettato

> «Un disegnatore umano prima sistema i pezzi principali, quelli da progetto definitivo, e
> traccia le autostrade, che sono poi i tubi principali dell'impianto. Quindi dai generatori
> agli accumuli/scambio passando per le eventuali valvole a tre vie o collettori che mettono
> insieme i generatori, e disegna **sempre come autostrada** le linee che da
> accumuli-puffer-scambiatori collegano con i circolatori. Poi **già qui** disegna le strade
> secondarie (tipo uscita ACS e distribuzione verso i terminali).
>
> Quando si fa questo disegno non si cerca di farlo più piccolo possibile — quindi la
> **lunghezza delle linee non è un costo** — il vero costo sono le **curve** e in secondo
> luogo gli **attraversamenti**, che sono quelle che rendono brutto il disegno. Quindi qua
> bisogna **tenersi larghi** e occupare più porzione di foglio anche se non ne ho bisogno.
>
> Poi a quel punto vado a inserire valvole e componenti piccoli e strade di servizio
> (ingresso AF, stacchi per valvole jolly o vasi di espansione) e **se non ho spazio stretcho
> e sposto traslando i tronchi autostradali**. Se proprio non c'è spazio si aggiunge qualche
> curva sulle autostrade, **ma proprio come ultima spiaggia**.»

Ridotto a fasi:

| | fase | che cosa entra | che cosa costa |
|---|---|---|---|
| **1** | la struttura | pezzi principali, autostrade **e strade secondarie** | curve, poi attraversamenti. **La lunghezza no** |
| **2** | il corredo | valvole, componenti piccoli, strade di servizio | se manca spazio: **stretch e traslazione** dei tronchi |
| **3** | l'ultima spiaggia | — | una curva sull'autostrada, **solo se non c'è altro modo** |

## 2. L'ordine che il motore esegue oggi

Documentato in `2026-09-11-architettura-della-posa-a-fasi.md` §3 e attuato da `DRAW-008`:

| | fase | che cosa entra |
|---|---|---|
| **1** | il tronco | macchine di spina, sola autostrada. Invariante: **ogni tratta è un rettilineo** |
| **2** | il corredo | accessori in linea; il tronco **non si piega, si allunga** |
| **3** | le strade di servizio | stacchi, diramazioni, adduzioni, accessori appesi. Qui le curve si pagano |

## 3. Le cinque differenze, misurate

### 3.1 Le strade secondarie sono in fase 3, e il PO le vuole in fase 1

Sulla tavola 2, **dieci tratte su ventitré** sono autostrada, e sono **tutte** sul circuito
dei generatori. Non lo sono:

```
   no  volano.secondary_out  → ventilconvettori.in     ← la mandata ai terminali
   no  ventilconvettori.out  → volano.secondary_in     ← il suo ritorno
   no  bollitore.dhw_out     → utenze.a                ← l'uscita ACS
```

Sono esattamente le tre linee che il PO nomina — «le linee che da accumuli-puffer-scambiatori
collegano con i circolatori» e «uscita ACS e distribuzione verso i terminali». Oggi cadono in
**fase 3**, insieme agli stacchi dei vasi di espansione e agli ingressi dell'acqua fredda:
l'ultima fase, quella dove le curve si accettano.

### 3.2 Il circolatore non fa nemmeno tratta

`circolatore` è fra i **venti** componenti trattati come accessori in linea. La linea
«accumulo → circolatore → terminali», che per il PO è un'autostrada, per il motore non è
neppure una tratta di tronco: è un pezzo di corredo dentro una tratta di rango minore.

### 3.3 Con due generatori, uno dei due non è autostrada

Già misurato il 16 settembre e agli atti in `ACTIVE_WORK_PACKAGE.md` §E.1. Sull'impianto 4 le
autostrade partono dalla **caldaia**; mandata e ritorno della **pompa di calore** non lo
sono. Sulla tavola 2 — un generatore solo — `pdc.water_supply` è la prima dell'elenco.

Il PO dice «dai generatori agli accumuli, **passando per le eventuali valvole a tre vie o
collettori che mettono insieme i generatori**»: cioè un impianto con due generatori ha **due**
autostrade che confluiscono, non una eletta e una scartata.

### 3.4 L'autostrada non è un oggetto: è una catena di frammenti

Dieci tronconi su venticinque tratte per l'impianto 4, ciascuno lungo 5 o 10 mm, uno per ogni
accessorio incontrato. L'invariante «ogni tratta del tronco è un rettilineo» è verificato **su
ciascun frammento**, ed è vero per costruzione: un frammento di 5 mm è dritto sempre. **Nessun
invariante dice che la catena intera sia una retta.**

### 3.5 Quando l'invariante non si può tenere, si butta via la fase invece di cedere di poco

È il difetto che spiega la tavola 4, ed è scritto nel codice stesso (`compose.py`). Quando la
catena a fasi non si instrada, `compose_sheet` prova in quest'ordine:

```
1. improved   — la posa delle fasi, migliorata
2. seeded     — la posa che la fase del tronco ha seminato
3. improve_sheet(first)  — «il ciclo senza le fasi, cioè la tavola che sarebbe uscita
                            prima di DRAW-008»
4. first      — la disposizione di partenza
```

L'impianto 4 esce dal **terzo**: la tavola che il motore produceva **prima che le autostrade
esistessero**. Non è che l'autostrada sia venuta storta — è che quella tavola non è stata
disegnata da un motore che sa cosa sia un'autostrada.

Il PO chiede il contrario: se non c'è spazio, **una curva sull'autostrada come ultima
spiaggia**. Cioè cedere un millimetro sul vincolo e tenere la struttura, invece di buttare la
struttura e tenere il vincolo.

### 3.6 Sul costo, una precisazione a favore del motore

L'ordine delle voci di `SheetCost` è già quello che il PO vuole — **prima le curve, poi gli
attraversamenti, poi la lunghezza**:

```
violations · turnback_runs · turnback_mm · long_runs · bends · crossings · length_mm · fill · imbalance
```

Quindi una posa più lunga che toglie una curva **vince già**. Ciò che manca non è l'ordine: è
che **a parità di curve e attraversamenti il motore sceglie sempre la più corta**, e il
riempimento è l'ultimo spareggio, dopo la lunghezza — non può mai comprare un millimetro.
Sommato all'assenza di una mossa che allarghi davvero, il risultato è la compattazione che si
misura sulla tavola 2: **257,5 mm occupati su 350 disponibili**, con il prelievo rientrato di
45 mm verso il centro mentre a destra il foglio era libero.

## 4. Che cosa se ne ricava

Il PO ha ragione, e la frase «stiamo ottimizzando la punta di una lancia storta» descrive un
fatto: **quattro delle cinque differenze stanno a monte di qualunque taratura.** Un pacchetto
che corregge la posa del prelievo, o che guadagna tre millimetri sulla tavola 2, lavora sulla
punta. Le differenze 3.1, 3.2, 3.3 e 3.5 cambiano **che cosa il motore considera struttura**,
e nessuna quantità di ottimizzazione le raggiunge.

**Conseguenza sulla priorità dei pacchetti**, che il PM propone e il PO approva:

- `DRAW-011` — il prelievo nella distribuzione, gli stacchi che non attraversano, i budget
  della tavola 2 — **si sospende**. Cura sintomi dell'architettura che stiamo per cambiare, e
  i suoi criteri sui budget sarebbero misurati con un metro che sta per cambiare.
- Sopravvive di `DRAW-011` la sola parte che serve comunque e non dipende dal motore: **la
  riscrittura del caso di prova 4** (D-137), che anzi diventa il **banco** su cui l'ordine
  nuovo si mette alla prova — due generatori, un collettore che li unisce, un disgiuntore, un
  circolatore, una distribuzione.
- Il pacchetto nuovo è **l'ordine delle fasi**, con le cinque differenze come criteri.

**E una cosa va detta al PO prima che cominci**, perché è il prezzo del cambio: rifare
l'ordine delle decisioni **può far peggiorare i numeri delle tavole 1 e 2 per un giro**. Non
sarebbe una regressione da respingere: sarebbe il metro che cambia. Il miglioramento da
guardare non è «meno millimetri», è **l'autostrada che esiste, è una linea sola e si vede** —
che è ciò che il PO chiede di vedere da tre giri.
