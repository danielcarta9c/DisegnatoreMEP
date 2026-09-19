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
| `impianto-1.json` | Il piano: **dove stanno i pezzi**, e le regole del PO che lo motivano, scritte accanto |
| `tavola1-DAL-PIANO.pdf` | La tavola che ne esce |

Si riproduce con `scripts/piano.py`:

```
.venv/bin/python scripts/piano.py <progetto-completo.json> \
    docs/collaudi/PROVA-PIANO/impianto-1.json <cartella-uscita>
```

## Che cosa gira e che cosa no

**Non gira**: `lay_the_spine` (la fase del tronco) e `improve_sheet` (il ciclo di
miglioramento) — le due che *cercano* invece di comporre.

**Gira**: tutto il resto, cioè le parti che la ricerca del 4 agosto §3 dichiara sane — gli
accessori appesi seguono il proprio pezzo, l'instradamento è ortogonale e in griglia, le
linee si interrompono sotto i simboli, la legenda, le sigle, i validatori, il rendering.

## L'esito

**La mandata è una retta sola**, da PDC-01 al radiatore, senza una piega; il ritorno è la sua
parallela. Le due pompe sono incolonnate (D-119) e scendono sui collettori con uno stacco
corto. Il gruppo di servizio esce dalla fila e si appende sotto il ritorno (D-118). L'ordine
del processo si legge da sinistra a destra (D-060). Quattro rilievi, uno solo bloccante.

**È la prima tavola del progetto in cui l'autostrada non si piega.**

### Quello che la prova ha misurato, e conta più della tavola

| | solutore | piano scritto a mano |
|---|---|---|
| tempo per tentativo | **10–40 minuti** | **~30 secondi** |
| che cosa dice quando sbaglia | un punteggio che non scende | «questa tratta è lunga 10 mm ma i suoi accessori ne chiedono 15» |

Il secondo è un messaggio su cui si **agisce**; il primo no. È la ragione per cui cinque
giri di correzione sono costati pochi minuti in tutto, e sono bastati.

## Quello che resta storto, dichiarato

- **Il disegno è una fascia nella metà alta.** È colpa del piano, non del motore: tutto sta
  fra y 65 e 190 su un'area alta 358. Si corregge scrivendo un piano migliore — che è
  esattamente il punto della prova.
- **Il gruppo del manometro fa un cappio**: è il rilievo bloccante rimasto, 2,5 mm di
  superamento della porta.
- **È su A2.** Su A3 non ci stava con le distanze che gli accessori in linea pretendono.

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
