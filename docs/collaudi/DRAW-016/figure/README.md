# Figure di spiegazione

**Non sono tavole.** Sono disegni fatti per spiegare una regola al PO quando le parole non
bastavano, e **non fanno convenzione grafica** (D-165): la convenzione è quella sviluppata
fino a qui, e questi fogli la usano soltanto per farsi leggere.

Ciascuna figura sta qui col **programma che la genera**, perché una figura che non si può
rifare non si può correggere.

| figura | perché esiste | stato |
|---|---|---|
| `b12-il-pettine` | Il PO, il 22 settembre 2026: «**B12 non l'ho capita, mi spiace, dovrei vederla disegnata per capire**». Mostra il pettine accanto all'impianto 5, e dove il secondario dell'impianto 5 non ci sta: la mandata serve il radiante **per ultimo** e il ritorno lo raccoglie **per primo**, quindi serve una terza verticale | **domanda aperta al PO** — ritorno invertito voluto, o ordine sbagliato nel grafo? |

## Come si rifà una figura

```sh
python3 docs/collaudi/DRAW-016/figure/b12-il-pettine.py   # scrive l'SVG in /tmp
scripts/to-pdf.sh <svg> <pdf>
```

⚠ **`scripts/rasterize.sh` taglia sotto i ~272 mm** di un foglio da 297: apre l'SVG come
documento nel browser, e la finestra non arriva in fondo. Chi disegna una figura per
rivederla in PNG tenga il contenuto **sopra i 265 mm**, o non vedrà quello che ha scritto in
fondo al foglio e lo crederà mancante. Il PDF non ha questo limite.
