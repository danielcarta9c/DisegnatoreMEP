# La prova del piano di composizione — 19/20 settembre 2026

**Domanda:** il disegno lo deve *trovare* un solutore che minimizza una somma pesata, o lo
deve **comporre** chi sa come si fa un disegno, lasciando al motore deterministico la
meccanica e i controlli?

**Come è nata.** Il PO, dopo aver guardato la cascata di tre pompe:

> «Il problema è che stiamo cercando di far fare il disegno a un motore deterministico
> matematico mettendo dentro regole e pesi e poi quello lavora da sé. Fosse stato così
> semplice ci sarebbero riusciti da tempo i vari Autodesk. Probabilmente dovremmo usare i
> criteri e pesi dati come linea guida e far disegnare il tutto a un agente AI.»

La prova costa poche ore e decide se vale la pena riscrivere: **il piano lo scrive l'agente
a mano, in sessione**, e lo esegue il motore che già c'è.

## Che cosa c'è qui

| File | Cos'è |
|---|---|
| `impianto-1.json` | Il piano dell'impianto 1: **dove stanno i pezzi**, e le regole del PO che lo motivano, scritte accanto |
| `tavola1-DAL-PIANO.pdf` | La tavola che ne esce |
| `impianto-5.json` | Il piano dell'impianto 5 — la cascata di tre PDC, l'impianto che il solutore non aveva mai fatto uscire decente |
| `tavola5-DAL-PIANO.pdf` | La tavola che ne esce |

Si riproduce con `scripts/piano.py`:

```
.venv/bin/python scripts/piano.py <progetto-completo.json> \
    docs/collaudi/PROVA-PIANO/impianto-N.json <cartella-uscita>
```

## Che cosa gira e che cosa no

**Non gira**: `lay_the_spine` (la fase del tronco) e `improve_sheet` (il ciclo di
miglioramento) — le due che *cercano* invece di comporre.

**Gira**: tutto il resto, cioè le parti che la ricerca del 4 agosto §3 dichiara sane — gli
accessori appesi seguono il proprio pezzo, l'instradamento è ortogonale e in griglia, le
linee si interrompono sotto i simboli, la legenda, le sigle, i validatori, il rendering.

## L'esito

**Impianto 1.** La mandata è una retta sola, da PDC-01 al radiatore, senza una piega; il ritorno
è la sua parallela. Le due pompe sono incolonnate (D-119) e scendono sui collettori con uno
stacco corto. Il gruppo di servizio esce dalla fila e si appende sotto il ritorno (D-118).
L'ordine del processo si legge da sinistra a destra (D-060).

**È la prima tavola del progetto in cui l'autostrada non si piega.**

**Impianto 5.** I collettori della cascata sono **verticali e dritti**, i terminali a pettine
(D-144). È l'impianto su cui il PO aveva detto «quel nugolo di tubi invece di disegnare un
cavolo di collettore dritto in verticale».

### La misura, rifatta il 20 settembre

Comando: `.venv/bin/python scripts/piano.py <completo.json> docs/collaudi/PROVA-PIANO/impianto-N.json <uscita>`

| | tratte | **cedute** | **rilievi bloccanti** | pieghe | incroci |
|---|---|---|---|---|---|
| impianto 1 | 21 | **0** | **0** | 8 | 1 |
| impianto 5 | 54 | **0** | **0** | 33 | 14 |

I tre rilievi che restano su ciascuna sono `warning`: pieghe in una tratta, riempimento sotto
la finestra (che D-149 ha tolto dagli obiettivi), e **il disegno tutto su un lato**.

**Il confronto onesto sulle pieghe.** Sulla tavola 1 il solutore della PR #44 faceva **4
pieghe e 1 incrocio**, meglio di queste 8; senza il riempimento come spareggio faceva 8 e 2.
Quindi il piano **non vince sui numeri**: vince su una cosa che i numeri non dicevano, cioè
che l'autostrada è dritta — ed è quella che il PO guarda.

### Quello che la prova ha misurato, e conta più della tavola

| | solutore | piano scritto a mano |
|---|---|---|
| tempo per tentativo | **10–40 minuti** | **~30 secondi** |
| che cosa dice quando sbaglia | un punteggio che non scende | «questa tratta è lunga 10 mm ma i suoi accessori ne chiedono 15» |

Il secondo è un messaggio su cui si **agisce**; il primo no. È la ragione per cui cinque
giri di correzione sono costati pochi minuti in tutto, e sono bastati.

## Quello che resta storto, dichiarato

- **Il disegno è una fascia nella metà alta**, su tutte e due. È colpa del piano, non del
  motore: nessuno distribuisce in verticale, e il rilievo `DRAWING_ALL_ON_ONE_SIDE` lo dice
  con un numero — 5,2 volte l'inchiostro sull'impianto 1, **9,0 volte** sul 5. Si corregge
  scrivendo un piano migliore, che è esattamente il punto della prova.
- **Quattordici incroci sull'impianto 5**, contro i cinque che il limite ammette.
- **È su A2** (D-148). Su A3 non ci stava con le distanze che gli accessori in linea
  pretendono.
- **Il PO l'ha detto guardandole:** «c'è molto da migliorare ancora, non assomiglia a come
  dovrebbe essere un disegno». La prova dimostra che **l'anello si chiude**, non che le
  tavole siano belle.

## Un difetto trovato strada facendo, e che cosa insegna

Per un raccordo a T **è la posa a decidere quale attacco fisico serve quale porta del
modello** (`PlacedSymbol.port_map`, D-004, I-027). Spostando i pezzi senza rifare quella
mappa, i T restano girati verso dove stavano prima: il ritorno arriva da destra e pretende di
entrare dall'attacco di sinistra, e non si instrada niente.

La cura **non** è scrivere l'orientamento nel piano: ogni raccordo si gira **verso i vicini
che ha davvero**, con un prodotto scalare e un'assegnazione avida. Nessun peso, nessuna
ricerca.

È la prima prova di una cosa che vale per il seguito: **molte delle decisioni che oggi
costano una ricerca sono deduzioni dirette**, e vanno tolte dal solutore prima ancora di
decidere chi compone.

**E subito dopo, il rovescio della stessa medaglia.** La prima versione della deduzione
rifaceva la mappa degli attacchi su **ogni** pezzo, macchine comprese: sull'impianto 1
l'acqua fredda è finita sull'uscita primaria dell'accumulo invece che sull'ingresso freddo.
Il grafo era giusto e il disegno era sbagliato — **una deduzione grafica che produce un
errore di contenuto**. L'ha visto il PO, a occhio, non una misura: «questo è proprio un
errore, hai messo il ritorno sull'ingresso ACS istantaneo». La regola che ne esce è stretta:
**la mappa degli attacchi si rifà solo per i raccordi**, e la rotazione si deduce solo per un
raccordo o per un pezzo che ha un attacco solo. Una macchina con due o più attacchi **ha** una
scelta, e quella scelta è del pianificatore.
