# Pianta — dalla planimetria alla tavola dei posizionamenti e dei tracciati

> **A chi parla questo file.** A un agente che ha una planimetria (un PDF, una scansione, un
> catastale) e un impianto già deciso, e deve produrre la tavola **M.03**: la pianta con le
> macchine posizionate e i tracciati numerati come nella tabella delle tratte dello schema
> funzionale. Queste istruzioni bastano da sole.

---

## 1. Il lavoro, in tre righe

Tu **trascrivi la planimetria** in un JSON — muri, aperture, stanze — e ci metti i pezzi dove li
ha decisi il progettista e i tracciati da collegare. **La strada dei tracciati non la disegni tu**:
la sceglie l'instradatore, con la stessa regola del motore dello schema (I-229) — mai diagonali,
le curve e i sormonti si pagano, si segue il muro. Poi guardi la tavola.

Non progetti. Diametri, sezioni, quote e posizioni sono del progettista: se non li hai, sono
**domande dichiarate**, non invenzioni.

## 2. Il comando

```
python3 scripts/mep.py pianta <pianta.json> --out <cartella>
```

Esce, col nome del JSON: `.pdf`, `.svg`, `.dxf` (con il logo accanto), `.png` (l'anteprima: guardala),
`.tracciati.json` (percorsi, lunghezze misurate e da quotare, forature, rilievi). Uscita `0` fatto,
`2` fatto ma con un rilievo che ferma la consegna, `1` il JSON non regge (il messaggio dice dove).

## 3. Il JSON, campo per campo

Lo schema esatto è `schemas/pianta.schema.json`; un esempio completo è
`examples/pianta/appartamento-aria-aria.json`. **Metri**, origine **in alto a sinistra**, x verso
destra, **y verso il basso** — come leggi un'immagine.

| campo | che cosa | come lo ricavi |
|---|---|---|
| `muri` | asse (`da`, `a`) e `spessore`; `tipo` perimetrale, portante o tramezza | sul disegno, misurando con la scala; perimetrali 0,30, tramezze 0,10 se il disegno non dice altro |
| `aperture` | `muro`, `centro` (sull'asse del muro), `larghezza`, `tipo`: porta, varco, finestra, foro | le porte con il verso (`apre_verso`), i varchi a tutta altezza, i fori già previsti |
| `stanze` | `nome`, `zona`, `poligono` (le facce interne), `controsoffitto`, `disimpegno` | dove c'è il controsoffitto lo dice il progettista; i corridoi sono `disimpegno: true` |
| `velette` | rettangoli di controsoffitto fuori dalle stanze che ce l'hanno | |
| `sfondo` | facoltativo: un **JPEG** con `px_per_m` e `origine_px` (il pixel del punto 0,0) | quando hai solo il catastale. **I muri principali si dichiarano lo stesso**: l'instradatore non legge l'immagine |
| `pezzi` | `sigla`, `tipo`, `x`/`y` (il **centro**), `larghezza` (lungo x), `profondita` (lungo y) | le sigle dello schema funzionale. Bocchette e griglie a parete **a cavallo del muro**: il loro foro è il pezzo |
| `tracciati` | `tratta` (T01…), `da`/`a` (sigla, o `{pezzo, lato}`), `fluido`, `dimensione`, `quota`, `fascio` | i numeri della tabella delle tratte. `lato` (sopra, sotto, sinistra, destra) solo dove l'attacco c'è davvero: le uscite di un plenum |
| `maggiorazione` | la regola della lunghezza da quotare | se il progettista non ne dà un'altra, quella del kit: `(L + 1 m) × 1,15` per eccesso a 0,5 m |

I `fluido` sono quelli di `naming/media.json`: `supply_air`, `return_air`, `refrigerant_liquid`,
`refrigerant_gas`, `condensate`, `power_supply`, `interconnection`, `control_bus`, e gli idronici.

Le `quota`: `controsoffitto` (canali, linee frigo, condensa: fuori dal controsoffitto costa il
triplo), `traccia` (cavi e bus), `pavimento`, `a_vista`. Una **porta non lascia passare il
controsoffitto** — sopra c'è l'architrave —, un varco e un foro sì.

Un **`fascio`** è fatto di tracciati fra **gli stessi due pezzi** (liquido, gas e cavo fra le due
unità): corrono paralleli a passo fisso e hanno una scritta sola. Non dichiarare fascio cavi che
vanno in posti diversi — i bus a stella dalla centrale non sono un fascio: la tavola lo misura e
te lo dice.

## 4. Che cosa la tavola garantisce — misurato, non promesso

Il comando stampa i controlli e li scrive in `.tracciati.json`:

- **diagonali: 0**, sempre — tracciati e richiami;
- **sovrapposizioni: 0** — due tracciati non corrono mai sullo stesso tratto;
- **scritte che toccano una linea o un'altra scritta: 0** — altrimenti è un rilievo bloccante;
- **tratte non instradate**: dette una per una, e disegnate tratteggiate;
- **sormonti**: contati ed elencati; il percorso li evita quando può, non sempre può;
- **forature**: ogni muro passato fuori da un'apertura che lascia passare quella quota, numerata
  F1, F2… sulla tavola e nella colonna. Un fascio che fora lo stesso muro fa un foro solo.

## 5. Che cosa la tavola non garantisce

- **I percorsi sono indicativi**: la tavola lo scrive, e vanno verificati in sopralluogo. Non
  conosce travi, impianti esistenti, pendenze della condensa, altezze libere.
- **Le lunghezze** sono quelle della spezzata in pianta: salite e discese stanno nell'aggiunta
  della regola. Se la planimetria è un catastale a 1:200, valgono ±10-15 %.
- **Non sceglie dove stanno i pezzi**: se il disegno è un groviglio, il primo sospetto è la posa.
  Un'unità di 1 m in un corridoio di 1,5 m lascia 25 cm per lato: i tracciati non ci passano.
  Sposta o ruota il pezzo, non chiedere all'instradatore di fare miracoli.

## 6. Prima di consegnare, guarda l'anteprima

Se i controlli sono a zero e la tavola a occhio non si legge — un groviglio, un richiamo lungo che
attraversa una stanza, una linea che gira intorno a una macchina — **scrivilo**: è il rilievo più
utile che puoi portare. Le cure sono nella posa dei pezzi e nei `lato`, non nei percorsi.
