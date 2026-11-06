# REL-023 — le giunzioni, l'antigelo di base, il circolatore fuori dalla minuteria

**Le disposizioni del PO** (6 novembre 2026):

- **I-290**: nelle case di base niente valvole antigelo; la skill le chiede per una seconda casa, una zona fredda, un
  tratto esterno lungo; senza, una nota sulla tavola dice di tenere la pompa di calore alimentata (D-238, supera
  D-230 nelle case);
- **I-291**: «I nippli vanno tra due accessori minori i raccordi a pressare tra tubo e accessorio e tra tubo e tubo.
  Le curve una ventina o le stima agente in contesto di progetto le tee invece le conta dal grafo»; i metri dal
  contesto del progetto, non dallo schema (D-239);
- **I-292**: il circolatore, come la pompa di calore e gli accumuli, lo compra Nove C a parte (D-239).

## La tavola

La villetta del collaudo T1 (12 kW, deviatrice a tre vie, volano, bollitore), rifatta nell'esecutivo con la 1.15.0 (`T1/`: grafo, piano, tavola, costo):
le due valvole antigelo non ci sono più, e la nota 2 dice «Antigelo: la pompa di calore resta alimentata d'inverno; la
sua protezione antigelo funziona solo con la corrente». La stessa cosa sulla villetta di `REL-017`
(`docs/collaudi/REL-017/vaso-note/tavola/`), rifatta con il suo `rifai.sh`.

**Il rilievo del PO sulla tavola del T1** (6 novembre 2026, «occhio a ste robe»): la discesa dalla terza via della
deviatrice al serpentino del bollitore faceva un dente proprio sull'incrocio col ritorno. Il disegno lo diceva
(`HIGHWAY_IS_NOT_STRAIGHT`: tre pieghe dove ne basta una), era già nella tavola di `REL-021`, e la sessione non l'ha
riferito prima di mostrare la tavola. Corretto nel piano: il bollitore e i suoi pezzi 10 mm a destra, lo stacco delle
utenze accorciato di 2,5 mm. Restano nella tavola, come nella villetta di `REL-017`, la coppia del secondario che
fra collettore e volano cambia interasse (10 e 15 mm, `SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER`): gli attacchi del volano
e del collettore hanno passi diversi, e il piano da solo non li allinea.

## Le misure

Il costo della minuteria del T1, con la stessa skill costruita da `scripts/costruisci-skill.py`:

| | grafo | metri d'acqua | € |
|---|---|---|--:|
| `REL-022` (la 1.15.0 prima di oggi) | con le valvole antigelo | 43 m di MS 32 e 9,5 di MS 26 e 20, preisolato (dati dal collaudatore) | 1.929 |
| giunzioni e circolatore fuori | lo stesso | gli stessi | 1.683 |
| **la 1.15.0 di oggi** | `completa` senza valvole antigelo | **18,5 m di MS 32 e 2,5 m di MS 26, nudi con guaina 19 mm**: quelli comprati per la commessa PR.BG.017 | **1.425** |

L'ultima riga lascia fuori, **DA PREZZARE**, le tre reti dell'acqua fredda senza metri, il vaso di riscaldamento
senza volume e quattro pezzi sull'acqua fredda senza tubo: circa 50 € a listino. Sulla commessa PR.BG.017
l'installatore ha comprato **1.419 €** di materiale d'impianto (fatture Bricoman, 27 ottobre – 2 novembre 2026), senza
circolatore, cavo della pompa di calore e interruttore. Le due cifre si somigliano anche per caso: le due liste non
contengono le stesse cose.

**Le giunzioni del T1 di oggi**: 11 nippli da 1" e 3 da ¾"; 18 raccordi a pressare M 1" × MS 32, 8 M ¾" × MS 26,
5 all'attacco; in tutto circa **200 €**, contro i circa 360 € dei «due raccordi per accessorio» di D-236. Sulle fatture
dell'installatore: 19 nippli (30 €), circa 28 raccordi a pressare filettati, 42 pezzi filettati in ghisa e ottone (72 €).

## Che cosa è stato scelto dalla sessione, e va guardato

- **Ogni tratto fra due pezzi che non sono tee ha almeno un tubo**: la deviatrice e la sfera del volano non si toccano.
- **Il tratto esterno** comincia dopo il giunto, la riduzione e (se c'è) la valvola antigelo.
- Dove il contesto del progetto vede un tubo fra due accessori che la regola non vede: `"tubo": true` sulla tubazione.
- I nippli costano quanto sulle fatture dell'installatore (listino §2ter); il nipplo ridotto 1¼" × 1" si prezza con la
  riduzione M × F del listino; il ¾" × ½" non è nel listino ed è DA PREZZARE.
- **La posa automatica** dell'impianto di prova 2 mette ora la confluenza dei ritorni a sinistra del bollitore: la prova
  `test_nessun_raccordo_sta_a_sinistra_di_cio_che_unisce` è marcata rossa apposta (`SECONDO_APERTO`). Da D-151 quella
  posa è solo l'inventario dei simboli; le coordinate della tavola le scrive il piano.

## Le prove

```
.venv/bin/python -m pytest -q -p no:cacheprovider --ignore=tests/test_le_release.py
```

Dopo l'aggiornamento delle prove che davano per scontate le valvole antigelo (le catene della macchina, la riduzione
all'attacco, i cinque grafi di prova, il caso completo delle regole, i grafi completi di DRAW-018, REL-015, REL-017,
REL-018): l'esito è nel messaggio della PR.
