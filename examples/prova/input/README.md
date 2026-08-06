# Gli input del committente, come li ha scritti lui

Qui dentro c'è il **testo originale**, non toccato: le descrizioni a parole degli impianti,
come il committente le ha consegnate. È l'ingresso della skill — quello che un ingegnere
scrive in conversazione — ed è la sola cosa contro cui si può verificare se il primo pezzo
ha letto bene.

**Non si modifica.** Se una descrizione è ambigua, l'ambiguità va dichiarata nella lettura,
non risolta correggendo il testo. Le assunzioni fatte per chiudere ciascun grafo sono
elencate impianto per impianto nel generatore delle letture, qui accanto.

## Cosa c'è

| File | Cosa contiene |
|---|---|
| `2026-08-06-impianti-di-prova.txt` | Cinque impianti descritti a parole, consegnati il 6 agosto 2026 |

## La catena, da qui in poi

```
questo testo
   → la lettura                  examples/prova/build_test_plants.py
   → il grafo di prima stesura   examples/prova/prova-*.json
   → regole e assemblatore
   → il grafo definitivo         docs/prodotto/grafi-di-prova/
```

**La lettura oggi è fatta a mano**, e questo è il punto: il primo pezzo della skill —
l'agente che dal testo costruisce il grafo di prima stesura — non esiste ancora. Quando
esisterà, questo testo è il caso su cui si prova, e le letture qui accanto sono il metro con
cui si giudica il risultato.

Perché resti un metro onesto, la lettura fatta a mano va **congelata come è oggi**: se
domani la si corregge per farla combaciare con quello che l'agente produce, non misura più
niente.
