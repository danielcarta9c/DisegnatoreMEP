# I piani di composizione — dalla prova del 19/20 settembre al prodotto

> ## ⛔ I cinque piani sono VECCHI, dal 21 settembre 2026. Non si correggono: si ricompongono.
>
> **D-167** ha spostato le porte dei terminali** — `radiator`, `fan-coil`, `ahu-coil`,
> `underfloor-panel` hanno adesso `in` e `out` **tutt'e due sulla faccia sinistra**, su
> disposizione del PO. Questi cinque piani sono composti per terminali **passanti**, con
> l'uscita sull'altra faccia, e **mettono le utenze dove il pettine di B12 non passa**.
>
> **Misurato**, e non si nasconde: i rilievi passano da **14 · 13 · 15 · 18 · 38** a
> **12 · 16 · 14 · 21 · 46**, l'impianto 5 apre un `RUN_OVERSHOOTS_ITS_PORT` **bloccante** su
> `s8`, e la suite passa da **38 rosse a 47** — le nove nuove sono tutte quel bloccante e le
> prove del revisore che cadono a valle.
>
> **Non sono da riparare a mano.** Sono il **bersaglio** che il pianificatore deve pareggiare
> (**D-155**), non il prodotto: chi li ritocca a mano rifà l'errore che D-155 esiste per
> impedire. Si chiudono **ricomponendoli con `skill/comporre/`**, ed è il punto 0 di
> `DRAW-016`.
>
> Finché non sono ricomposti, **ogni misura presa su di loro va letta sapendo questo**.


> **Aggiornato il 20 settembre 2026 (`DRAW-015`).** Questa cartella era il collaudo di una
> prova; adesso è **la casa dei piani**, e i piani sono cinque: uno per ogni impianto di
> prova. Il pezzo che li esegue non è più uno script — è
> `src/disegnatore_mep/piano/`, con il comando `disegnatore-mep piano`.

## La prova che ha deciso D-151 — 19/20 settembre 2026

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
| `impianto-1.json` … `impianto-5.json` | I cinque piani: **dove stanno i pezzi**, e la regola che ha messo ciascuno dove sta, scritta accanto. L'1 e il 5 sono del 19/20 settembre; il 2, il 3 e il 4 sono di `DRAW-015`, composti su disposizione del PO («tu scrivi ora i piani con le regole»). **Tutti e cinque hanno avuto il confine ACS corretto il 20 settembre sera**, guardando le tavole: A4 vuole lo stacco minimo, e la nota di ciascuno dice da quanto a quanto |
| `tavola1-DAL-PIANO.pdf`, `tavola5-DAL-PIANO.pdf` | Le due tavole della prova, agli atti come sono uscite allora |

Le tavole correnti di tutti e cinque stanno in `docs/collaudi/DRAW-015/tavole/`.

Si riproducono tutte con un comando solo:

```
scripts/tavole-dal-piano.sh
```

e uno per volta dalla CLI, che è il percorso vigente:

```
.venv/bin/python -m disegnatore_mep piano <progetto-completo.json> \
    --piano docs/collaudi/PROVA-PIANO/impianto-N.json \
    --catalog examples/layout/catalog --symbols assets/symbols \
    --naming naming --out <cartella-uscita>
```

⚠ **Il progetto si passa nella forma che `rules --apply-all --out` scrive.** Non è un
dettaglio: la forma canonica riordina i componenti per identificativo, la posa di partenza
è greedy e legge quell'ordine (`place.py::_file_order`), e sull'impianto 5 il piano si
instrada sull'ordine canonico e **non** su quello di dichiarazione. I cinque piani sono
stati composti contro quella forma.

⚠ **`scripts/piano.py` non esiste più** (`DRAW-015`): era uno script di collaudo, e il piano
è diventato un pezzo del prodotto. La sua logica — `orienta` compresa, con tutte le note
misurate — è in `src/disegnatore_mep/piano/esecutore.py`, e le due tavole che ne escono sono
**identiche byte per byte** a quelle che lo script produceva.

## Che cosa gira e che cosa no

**Non gira**: `lay_the_spine` (la fase del tronco) e `improve_sheet` (il ciclo di
miglioramento) — le due che *cercano* invece di comporre.

**Gira**: tutto il resto, cioè le parti che la ricerca del 4 agosto §3 dichiara sane — gli
accessori appesi seguono il proprio pezzo, l'instradamento è ortogonale e in griglia, le
linee si interrompono sotto i simboli, la legenda, le sigle, i validatori, il rendering.

## L'esito

**Impianto 1.** La mandata è una retta sola, da PDC-01 al radiatore, senza una piega; il ritorno
è la sua parallela. Le due pompe sono incolonnate (D-041 + D-118) e scendono sui collettori con uno
stacco corto. Il gruppo di servizio esce dalla fila e si appende sotto il ritorno (D-118).
L'ordine del processo si legge da sinistra a destra (D-060).

**È la prima tavola del progetto in cui l'autostrada non si piega.**

**Impianto 5.** I collettori della cascata sono **verticali e dritti**, i terminali a pettine
(D-144). È l'impianto su cui il PO aveva detto «quel nugolo di tubi invece di disegnare un
cavolo di collettore dritto in verticale».

### La misura, rifatta il 20 settembre

Comando di allora: `scripts/piano.py` (uscito da `DRAW-015`). Oggi: `disegnatore-mep piano`, e dà lo stesso byte per byte.

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
