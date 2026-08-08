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

**Le letture qui accanto sono fatte a mano, e sono il metro.** Il primo pezzo della skill
— l'agente che dal testo costruisce il grafo di prima stesura — **adesso esiste**
(`skill/capire/ISTRUZIONI.md`) ed è stato **provato su questi cinque testi in camera
pulita e approvato** dal collaudo indipendente il 7 agosto 2026: zero elementi persi, zero
inventati. Le consegne di quella prova sono in `skill/capire/prova-2026-08-07/`.

Perché resti un metro onesto, la lettura fatta a mano va **congelata come è oggi**: se
domani la si corregge per farla combaciare con quello che l'agente produce, non misura più
niente. Vale **anche quando la lettura manuale ha torto** — e in un punto ce l'ha: sul
quinto impianto porta una valvola di ritegno che il testo non nomina e che le istruzioni
vietano all'interprete di aggiungere. La differenza si **classifica e si registra**
(`skill/capire/CONSEGNA.md` §2, criterio 4), il file non si cambia.

Resta però una cosa che queste letture **perdono** rispetto al testo, ed è un difetto
aperto: dichiarano il regime della centrale ma **non portano le potenze** da cui è stato
ricavato, mentre le istruzioni ordinano all'interprete di trascriverle. Si chiude
rigenerando il generatore, mai correggendo i file a mano.
