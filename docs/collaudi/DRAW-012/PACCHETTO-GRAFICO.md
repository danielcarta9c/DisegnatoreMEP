# Il pacchetto grafico di DRAW-012

`prima/` è la testa di `main` (`8589620`); `dopo/` è questa consegna. Le due colonne sono
prodotte **dallo stesso comando**, `docs/collaudi/DRAW-012/tavole.sh`, che è la catena della
CLI per intero: completamento con le regole, disegno in modalità verifica, misure con
`docs/collaudi/DRAW-002/metriche.py`.

```
docs/collaudi/DRAW-012/tavole.sh <cartella-sorgente> <cartella-di-uscita> <nome-impianto>...
```

Per ciascun impianto:

| file | che cos'è |
|---|---|
| `*-completo.json` | il modello dopo il completamento delle regole: è ciò che si disegna |
| `*-integrazioni.txt` | che cosa le regole hanno aggiunto, e perché |
| `*-geometria.json` | la geometria della tavola, esportata |
| `*-metriche.json` | le misure, con l'impronta di riproducibilità |
| `*-preflight.txt` | i rilievi, o l'errore per cui la tavola non esce |
| `*-t1.svg`, `tavola-N.png` | la tavola, dove esce |

**Gli impianti 3, 4 e 5 non producono una tavola né prima né dopo**: per loro la colonna
porta l'errore, che è il dato che il pacchetto chiede (criteri 9 e 12).
