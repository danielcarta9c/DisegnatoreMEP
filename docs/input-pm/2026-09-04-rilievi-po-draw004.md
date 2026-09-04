# Rilievi PO sulla tavola DRAW-004

- **Data:** 2026-09-04
- **Fonte:** revisione visiva del PO sulla tavola dell'impianto 1
- **Stato:** input PO validi e vincolanti, da tradurre nel Work Package successivo a DRAW-004
- **Regola di conservazione:** il testo PO e gli allegati restano separati dalla successiva
  specifica PM. Eventuali verifiche o precisazioni del PM non possono cancellare né
  sostituire l'input originario.

## Testo e intenzione del PO

### Etichette

- Le etichette dei nodi sono opzionali: il PO deve poter chiedere esplicitamente di
  mostrarle o non mostrarle.
- Le etichette delle macchine principali devono esserci sempre.
- Etichette e richiami restano l'ultima fase e non possono spostare tubi, accessori o
  macchine.

### Simboli e orientamento

- Il filtro a Y deve usare il simbolo classico a forma di Y, con ramo/gambo inferiore;
  il simbolo corrente non è approvato.
- Il confine di rete deve guardare **nel verso dell'acqua**.
- Le lettere interne ai simboli (`P` del manometro, `T` del termometro, `F` del
  flussostato e casi equivalenti) devono restare dritte secondo la direzione di lettura
  della tavola, anche quando il corpo del simbolo è ruotato.

### Intercettazione delle PDC e dell'accumulo

- Con il filtro a Y correttamente posto all'imbocco del ritorno della PDC, sul relativo
  ramo basta la valvola sul lato destro/rete: la valvola aggiuntiva fra filtro e PDC è
  ridondante.
- Le due valvole necessarie per la PDC possono essere collocate sui rispettivi rami di
  mandata e ritorno, senza aggiungere l'intercettazione ridondante.
- La valvola sulla mandata delle PDC verso il serbatoio deve stare vicino al serbatoio;
  non c'è motivo funzionale per lasciarla lontana.

### Accumuli, acqua tecnica, riempimento e acqua fredda

- L'impianto 1 usa acqua tecnica nel volume e un serpentino interno per la produzione
  istantanea di acqua calda sanitaria.
- Il gruppo di riempimento è **unico e sul circuito tecnico**. Per l'accumulo combinato
  va sul ritorno oppure direttamente sul serbatoio. Non va attribuito alla linea ACS.
- Deve essere presente e chiaramente rappresentato l'ingresso dell'acqua fredda al
  serpentino per la produzione istantanea.
- Devono esistere entità e simboli distinti per:
  1. puffer con sola acqua tecnica e senza serpentino;
  2. bollitore;
  3. accumulo combinato, con acqua tecnica nel volume e serpentino interno per ACS
     istantanea.
- Per la configurazione a volumi separati — puffer e bollitore separati con valvola a
  tre vie — resta vincolante l'indicazione PO originaria: «il gruppo di riempimento va
  sia sul volume del bollitore (l'acquedotto mette in pressione così il bollitore) che
  sul ritorno o diretto sul puffer della parte di acqua tecnica». La traduzione in
  oggetti di catalogo e regole deve essere verificata dal PM sulle fonti prima di essere
  consegnata al DEV, senza modificarne autonomamente il significato.

### Criterio di collaudo PM

- Gli schemi Caleffi, la documentazione tecnica dei produttori e gli schemi reali
  forniti dal PO devono essere usati dal PM per verificare non soltanto la qualità del
  routing, ma anche correttezza della posizione funzionale dei componenti, simboli,
  orientamenti e configurazione impiantistica.
- Il DEV non deve dedurre autonomamente i requisiti osservando gli esempi: il PM deve
  tradurli in regole, invarianti, moduli interessati, test e criteri di accettazione.

## Allegati originali

1. [`01-filtro-y.png`](rilievi-grafici/2026-09-04-draw004/01-filtro-y.png)
2. [`02-valvole-ritorno-pdc.png`](rilievi-grafici/2026-09-04-draw004/02-valvole-ritorno-pdc.png)
3. [`03-valvole-mandata-pdc.png`](rilievi-grafici/2026-09-04-draw004/03-valvole-mandata-pdc.png)
4. [`04-riempimento-e-af.png`](rilievi-grafici/2026-09-04-draw004/04-riempimento-e-af.png)
5. [`05-accumulo-combinato.png`](rilievi-grafici/2026-09-04-draw004/05-accumulo-combinato.png)
6. [`06-serpentino-riferimento.png`](rilievi-grafici/2026-09-04-draw004/06-serpentino-riferimento.png)

## Vincolo operativo

Questi rilievi non modificano il perimetro della PR #14. Dopo la chiusura e il merge di
DRAW-004, il PM deve verificarli sulle fonti tecniche e trasformarli nel successivo Work
Package esecutivo. Nessuna riga può essere dichiarata chiusa per la sola registrazione.
