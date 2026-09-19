# Il pacchetto grafico di DRAW-013

**`prima/` è il ramo di partenza, non `main`.** È la testa di `DRAW-012`
(`claude/hopeful-ramanujan-9bs0cb`, `17ff425`), che questo pacchetto corregge invece di
rifare: il confronto che conta è con quelle tavole, non con quelle che `main` produceva
prima delle autostrade. `dopo/` è questa consegna.

Le due colonne sono prodotte **dallo stesso comando**, che è la catena della CLI per intero —
completamento con le regole, disegno in modalità verifica (D-110), misure con
`docs/collaudi/DRAW-002/metriche.py` — e, da **D-146**, arriva fino al **PDF**:

```
docs/collaudi/DRAW-013/tavole.sh <cartella-sorgente> <cartella-di-uscita> <nome-impianto>...
```

Per ciascun impianto:

| file | che cos'è |
|---|---|
| `*-completo.json` | il modello dopo il completamento delle regole: è ciò che si disegna |
| `*-integrazioni.txt` | che cosa le regole hanno aggiunto, e perché |
| `*-geometria.json` | la geometria della tavola, esportata |
| `*-metriche.json` | le misure, con l'impronta di riproducibilità |
| `*-preflight.txt` | i rilievi, o l'errore per cui la tavola non esce |
| `*-t1.svg` | la tavola, come il motore la scrive |
| **`*-t1.pdf`** | **la tavola a misura reale: è questo che il PO guarda** (D-146) |
| `*-t1.png` | la stessa, rasterizzata per l'occhio terzo |

**Gli impianti 3, 4 e 5 non producono una tavola né prima né dopo**: per loro la colonna porta
l'errore, che è il dato che D-146 pretende. Per la tavola 4 c'è in più
`dopo/prova-4-perche-non-esce.txt`, il conto cella per cella che il criterio 11 chiede.

## I quattro file da guardare, in quest'ordine

1. `prima/prova-1-due-pdc-accumulo-combinato-t1.pdf`
2. `dopo/prova-1-due-pdc-accumulo-combinato-t1.pdf`
3. `prima/prova-2-pdc-deviatrice-acs-t1.pdf`
4. `dopo/prova-2-pdc-deviatrice-acs-t1.pdf`

Che cosa si vede, e dove il rapporto lo misura:

- **il disegno non tocca più il bordo**: 12,5 → 25,0 mm sulla tavola 1 e 17,5 → 25,0 mm sulla
  tavola 2 (§1.1 del rapporto);
- **l'ingresso dell'acqua fredda è tornato addosso all'accumulo** sulla tavola 1: 40 → 20 mm.
  Sulla tavola 2 no, ed è il rilievo di §7.1;
- **nessuna curva e nessun attraversamento in più**: 4/1 e 5/1, identici al ramo di partenza;
- e, sulla tavola 1, **il difetto che il DEV di `DRAW-012` aveva già scritto resta**: la
  mandata della seconda pompa di calore corre a lungo alla propria quota prima di scendere
  (§7.4 del rapporto).
