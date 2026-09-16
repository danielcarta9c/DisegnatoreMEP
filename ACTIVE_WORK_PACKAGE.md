# DRAW-012 — Il motore disegna nell'ordine del disegnatore

**Titolo:** Il motore disegna nell'ordine del disegnatore
**Assegnato da:** PM (Claude — `OPERATING_MODEL.md` §1.2.1)
**Assegnato a:** DEV
**Data:** 2026-09-16
**Stato:** **ATTIVO.** Sostituisce `DRAW-011`, che è **sospeso**: curava sintomi
dell'architettura che questo pacchetto cambia, e misurava budget con un metro che sta per
cambiare. Di `DRAW-011` sopravvive solo §D — la riscrittura del caso di prova 4 — che qui
diventa il **banco** (§G).
**Release:** 0.3 — generalizzazione, revisione della tavola 2
**Ramo:** quello che la piattaforma assegna alla sessione. Il pacchetto **non ne prescrive uno**
**Commit di partenza:** **la testa di `main`**. Contenuto della base: `DRAW-010` **non fuso**
(PR #32 respinta), `DRAW-011` mai consegnato.
**Fixture grafica principale:** impianto 2 e impianto 4; impianto 1 come regressione; impianti 3 e 5 come misura

> **Leggere prima:** `docs/pm/2026-09-16-come-ragiona-il-motore-e-come-dovrebbe.md` — le
> cinque differenze misurate fra l'ordine del disegnatore e quello del motore, con i comandi.
> Questo pacchetto è la loro cura e non le ripete. Poi `D-138`, che è la disposizione del PO.

---

## Contesto

Il PO, guardando la tavola 4: «è inutile che continuiamo a ottimizzare un motore di disegno
che se non ragiona bene in questo ordine e non ha regole per fare queste cose: stiamo
ottimizzando la punta di una lancia storta».

Ha ragione, ed è misurato. Gli ultimi tre pacchetti hanno lavorato sulla punta — tre
millimetri qui, una piega là — mentre **quattro difetti su cinque stanno a monte di qualunque
taratura**: le strade secondarie sono nell'ultima fase, il circolatore non fa nemmeno tratta,
con due generatori uno perde la classificazione, e quando l'invariante di fase non si può
tenere il motore **butta via la fase** e ripiega sulla tavola che produceva prima che le
autostrade esistessero. La tavola 4 è uscita da lì.

**Questo pacchetto cambia l'ordine delle decisioni, non le tarature.**

### Il prezzo, dichiarato prima di cominciare

Rifare l'ordine **può far peggiorare i budget delle tavole 1 e 2 per un giro**, e non sarebbe
una regressione da respingere: è il metro che cambia. Il miglioramento da guardare non è
«meno millimetri» — è **l'autostrada che esiste, è una linea sola e si vede a occhio**. Il PO
lo ha accettato esplicitamente prima che il lavoro cominciasse.

### Se il pacchetto non ci sta in una consegna

È grosso, e una consegna parziale mal tagliata è il modo in cui abbiamo perso gli ultimi due
giri. Se il DEV vede che non ce la fa, **taglia così e lo dice nel rapporto**:

- **Prima metà, che vale da sola:** §A, §B, §C — che cosa è autostrada e che sia un oggetto
  intero. Cambia ciò che il motore considera struttura, e si vede sulla tavola.
- **Seconda metà:** §D, §E, §F — il costo della fase, lo stretch, l'ultima spiaggia.

Non si taglia altrove, e **non si consegna una metà senza le sue prove**.

---

## A. La fase 1 traccia la struttura, non il solo tronco

1. La prima fase posa **i pezzi principali** e traccia **le autostrade e le strade
   secondarie**, insieme. Oggi traccia la sola autostrada del circuito dei generatori e manda
   tutto il resto in ultima fase.
2. **Strade secondarie di fase 1** sono l'**uscita ACS** e la **distribuzione verso i
   terminali**. Restano in fase 2 gli stacchi di servizio: ingresso AF, valvole jolly, vasi
   di espansione.
3. L'ordine dell'11 settembre (`2026-09-11-architettura-della-posa-a-fasi.md` §3) va
   **aggiornato** da questo pacchetto, non lasciato a contraddire il codice.

## B. Che cosa è autostrada, e chi lo decide

Tre regole, dettate dal PO in **D-138**:

1. **Dai generatori agli accumuli e agli scambiatori**, passando per le valvole a tre vie e i
   **collettori che mettono insieme i generatori**. Un collettore o una tre vie in mezzo non
   interrompe l'autostrada e non la declassa.
2. **Sempre**, le linee che dagli **accumuli, puffer e scambiatori** vanno ai **circolatori**
   e da lì alla distribuzione. Oggi il circolatore è fra i venti componenti trattati come
   accessori in linea e quella linea non è neppure una tratta di tronco.
3. **Con più generatori, le autostrade sono più d'una.** Oggi sull'impianto 4 sono autostrada
   le tratte della caldaia e non quelle della pompa di calore. Non c'è un generatore eletto:
   ciascuno ha la propria autostrada fino al punto in cui confluiscono.

**Prova richiesta:** un caso generale con due generatori mostra che **entrambe** le mandate
sono autostrada, e un caso con accumulo e circolatore mostra che la linea verso i terminali
lo è.

## C. Un'autostrada è un oggetto intero, non una catena di frammenti

1. Oggi un'autostrada è spezzata da ogni accessorio che incontra — dieci tronconi su
   venticinque tratte sull'impianto 4 — e l'invariante «ogni tratta è un rettilineo» è
   verificato su ciascun frammento, dove è vero per costruzione: un frammento di 5 mm è dritto
   sempre.
2. Serve un **oggetto che rappresenti l'autostrada intera**, da un capo all'altro attraverso
   i propri accessori, e **l'invariante si verifica su di lui**: la catena intera è una retta,
   salvo le pieghe che §F ammette.
3. **Prova richiesta:** una prova generale che fallisce se la catena intera prende una piega
   pur essendo ogni frammento dritto. È la prova che oggi manca, ed è il motivo per cui il
   difetto non si vedeva.

## D. I millimetri escono dal costo, il riempimento entra come finestra

Disposizione del PO, **D-139**: «i mm non sono un vero costo da misurare, lo è più avere un
buon riempimento, né troppo poco né troppo».

1. **La lunghezza delle tubazioni esce dalle voci di costo.** Non in fase 1 soltanto: esce.
   Restano i costi veri, nell'ordine — le **curve**, poi gli **attraversamenti**. Oggi
   `SheetCost` porta `length_mm` fra `crossings` e `fill`, ed è lei che a parità di curve e
   attraversamenti decide sempre per la posa più corta.
2. **Al suo posto entra il riempimento, e non è monotono.** Non «più è meglio» — che è ciò che
   D-134 ha rifiutato e resta rifiutato — ma una **finestra**: sotto si è vuoti, sopra si è
   stretti. Un disegno ben fatto è **comodo**, e ci deve stare lo spazio per le sigle.
3. **La finestra la fissa il PO**, e finché non l'ha fissata il DEV **non la inventa**: usa il
   valore che il pacchetto porterà qui, e se non c'è si ferma e chiede al PM.
4. **Ci si tiene larghi.** Misura del PM su tutte le tavole prodotte: nessuna supera i
   **262,5 mm di larghezza su 350 disponibili**, su nessuno dei cinque impianti; l'altezza
   usata va da 100 a 177,5 mm su 235. Il tetto di fatto intorno ai 260 mm è il primo posto
   dove guardare.
5. **L'agio smette di essere un passo finale.** D-134 lo metteva in coda, a disegno risolto;
   D-139 lo rende il parametro stesso. Non serve più un passo separato che allarga.

## E. In fase 2 il corredo entra, e se non ci sta si allarga

1. Valvole, componenti piccoli e strade di servizio entrano su una struttura **già ferma**.
2. Se lo spazio non basta: **stretch e traslazione del tronco autostradale**, che è la mossa
   che il contratto ammette da sempre — spostare le macchine non costa — e che nessuna
   consegna ha ancora usato davvero.
3. L'invariante di §C regge: allungare conserva la rettilineità, piegare no.

## F. L'ultima spiaggia: cedere una curva invece di buttare la struttura

1. Quando la struttura non si instrada, oggi `compose_sheet` ripiega in quattro passi e il
   terzo è **«il ciclo senza le fasi, cioè la tavola che sarebbe uscita prima di DRAW-008»**.
   L'impianto 4 esce da lì: non è un'autostrada venuta storta, è una tavola disegnata da un
   motore che non sa cosa sia un'autostrada.
2. Il PO dispone il contrario: **si concede una curva sull'autostrada, come ultima spiaggia**,
   e si tiene la struttura.
3. La cessione è **graduale e dichiarata**: si cede una piega per volta, sulla tratta che ne
   ha meno bisogno, e **il rapporto dice dove e perché** per ciascun impianto che ha dovuto
   cedere. Un ripiego che scarta l'intera fase resta solo come ultimissima rete, e ogni volta
   che scatta va scritto.

## G. Il banco: il caso di prova 4 riscritto

Il caso di prova 4 si riscrive secondo **D-137** — il grafo è dettato per esteso lì, componente
per componente e collegamento per collegamento — e serve come banco di questo pacchetto: ha
due generatori, un collettore che li unisce, un disgiuntore, un circolatore e una
distribuzione, cioè **tutte e tre le regole di §B insieme**.

Compresa la voce di catalogo nuova: la **commutatrice a tre vie** sul ritorno della caldaia,
due ingressi e un'uscita, funzione di commutazione dichiarata — non la miscelatrice esistente
piegata, che dichiara `circuit_mixing` e serve ad altro.

---

## Perimetro

**Dentro:** l'ordine delle fasi e che cosa entra in ciascuna (§A); la classificazione delle
autostrade (§B); l'autostrada come oggetto intero e il suo invariante (§C); il costo della
fase della struttura (§D); stretch e traslazione in fase 2 (§E); la cessione graduale al posto
del ripiego (§F); il caso di prova 4 e la commutatrice (§G); l'aggiornamento del documento di
architettura dell'11 settembre.

**Fuori:** lo spessore del tratto per gerarchia (**D-132**); il verso di mandata e ritorno
deciso dalla geometria (**D-136**); la libreria dei simboli, salvo
il simbolo della commutatrice; qualunque decisione MEP che il PO non abbia dato.

---

## Criteri di accettazione

Ogni criterio si chiude con **il comando eseguito e il suo output**.

1. **Sulla tavola 2, la mandata dall'accumulo ai terminali e l'uscita ACS risultano
   autostrada.** Oggi non lo sono: `volano.secondary_out → ventilconvettori.in`,
   `ventilconvettori.out → volano.secondary_in`, `bollitore.dhw_out → utenze.a`.
2. **Sull'impianto 4, entrambi i generatori hanno la propria autostrada.** Oggi la caldaia sì
   e la pompa di calore no.
3. **Una prova generale mostra che un collettore o una tre vie fra due generatori non
   interrompe né declassa l'autostrada.**
4. **Esiste un oggetto «autostrada intera»** e una prova generale **fallisce** se la catena
   prende una piega mentre ogni suo frammento è dritto.
5. **La lunghezza non entra più nel confronto fra due pose**, e una prova generale lo mostra
   su due pose che differiscono solo per quella.
6. **Il riempimento è una voce di costo a finestra**, non monotona, e una prova mostra che una
   posa dentro la finestra batte sia una più vuota sia una più stretta. La finestra è quella
   che il PO ha fissato: **[da fissare]**.
7. **La tavola 2 occupa più foglio di adesso**, e il prelievo non rientra verso il centro
   quando a destra c'è spazio. Riferimenti: 257,5 mm di larghezza su 350, riempimento 50,1 %.
8. **Lo stretch si usa davvero**: il rapporto mostra almeno un caso in cui il corredo non
   entrava e il tronco si è allungato invece di piegarsi, con le posizioni prima e dopo.
9. **Nessun impianto esce dal ripiego che scarta le fasi.** Se uno ci esce, il rapporto dice
   quale, perché, e che cosa ha impedito la cessione graduale di §F.
10. **La tavola 4 ha un'autostrada visibile dalla pompa di calore all'accumulo**, e il rapporto
   porta la tavola. È il criterio che il PO giudica a occhio.
11. **Il caso di prova 4 è riscritto** secondo D-137, e la commutatrice è una voce di catalogo
    con la propria funzione dichiarata e il proprio simbolo.
12. **Gli impianti 1, 2 e 4 producono una tavola.** Il 3 e il 5 si misurano e si riferiscono:
    se l'ordine nuovo li fa uscire, bene; se no, il rapporto dice dove si fermano.
13. **Il saldo della suite non peggiora.** Riferimento su `main`: 10 rosse, 1470 verdi,
    24 saltate, 11 xfailed. Nessuna prova convertita in `skip` o `xfail`, nessuna soglia
    allentata, nessuna fixture toccata per far passare una prova.
14. **Le tavole 1 e 2 sono misurate e riferite, prima e dopo, con il metro nuovo**: curve,
    attraversamenti e riempimento. Riferimenti: tavola 1 · 4 curve, 1 attraversamento,
    riempimento 29,8 %; tavola 2 · 5 curve, 1 attraversamento, riempimento 50,1 %. La
    lunghezza si riporta ancora, ma **come misura e non come giudizio** (D-139).
    **Non è un criterio di non-regressione**: un peggioramento su curve o attraversamenti è
    ammesso se il rapporto lo spiega con l'ordine nuovo. È il metro che cambia, e va visto
    cambiare.
15. **Determinismo**: doppia generazione dalla CLI con la stessa impronta.
16. **Il documento di architettura dell'11 settembre è aggiornato** all'ordine di D-138, o
    marcato come superato da un documento nuovo. Non resta a contraddire il codice.
---

## Consegna

Una PR sola, non fusa. Rapporto in `docs/collaudi/DRAW-012/RAPPORTO.md` con i quindici criteri
chiusi uno per uno; pacchetto grafico `prima/` e `dopo/` per le tavole 1, 2 e 4.

**Prima di aprire la PR**, le tre cose che `DRAW-011` §F aveva introdotto e che restano:

1. **Guarda le tavole.** I difetti che hanno respinto DRAW-010 li ha visti il PO a occhio e
   nessun criterio li copriva. Se una tavola ti sembra sbagliata e i numeri dicono che va
   bene, **scrivilo nel rapporto**: è il rilievo più utile che puoi portare.
2. **Misura i criteri di non-regressione prima, non dopo.** Qui sono il 12 e l'11.
3. **Se una disposizione del PO ammette due letture, fermati e chiedi al PM.** D-126 letta in
   un modo invece che nell'altro è costata un pacchetto intero.

---

## Decisioni che restano al PO

1. **Il pallino di derivazione con due spessori** (D-132): il PM propone che segua il tratto
   più grosso.
2. **L'ordine degli stacchi lungo il tronco** (rischio 17).
3. **Gli attacchi pari di un collettore**, ereditata da `DRAW-009`.
