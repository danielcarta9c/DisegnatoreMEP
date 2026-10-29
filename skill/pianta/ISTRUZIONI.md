# Pianta — dalla planimetria alla tavola dei posizionamenti e dei tracciati

> **A chi parla questo file.** A un agente che ha una planimetria (un PDF, una scansione, un
> catastale, o anche solo una descrizione a parole con le misure) e un impianto già deciso, e
> deve produrre la tavola **M.03**: la pianta con le macchine posizionate e i tracciati numerati
> come nella tabella delle tratte. Queste istruzioni bastano da sole.

---

## 1. Il lavoro, in tre righe

Tu **trascrivi la planimetria** in un JSON — muri, aperture, stanze — e ci metti i pezzi dove li
ha decisi il progettista e i tracciati da collegare. **La strada dei tracciati non la disegni tu**:
la sceglie l'instradatore, con la stessa regola del motore dello schema (I-229) — mai diagonali,
le curve e i sormonti si pagano, si segue il muro, si resta nel controsoffitto. Poi guardi la
tavola.

Non progetti. Diametri, sezioni, lunghezze, quote e posizioni sono del progettista: se non li hai,
sono **domande dichiarate**, non invenzioni.

## 2. Il comando

```
python3 scripts/mep.py pianta <pianta.json> --out <cartella> --distinta <distinta.json> --grafo <grafo-completo.json>
```

`--distinta` (il `distinta.json` che scrive il comando `distinta`) e `--grafo` (il grafo completo dello
schema) sono facoltativi, ma **passali tutte le volte che li hai**: il comando controlla con loro sigle,
numeri di tratta e lunghezze (§3), e prende dalla distinta la lunghezza dei tracciati che non ce l'hanno.

Esce, col nome del JSON: `.pdf`, `.svg`, `.dxf` (con il logo accanto), `.png` (l'anteprima: guardala),
`.tracciati.json` (percorsi, lunghezze, forature, rilievi, avvisi) e, se c'è un riquadro di
dettaglio, le stesse tavole `<nome>-dettaglio-A…`. Uscita `0` fatto, `2` fatto ma con un rilievo
che ferma la consegna, `1` il JSON non regge (il messaggio dice dove, il campo atteso e un esempio
dell'oggetto giusto).

## 3. Da dove prendi i dati

| dato | da dove |
|---|---|
| **la planimetria** | il disegno (PDF, immagine, catastale) **oppure una planimetria a parole** con le misure: va bene anche quella. Leggi le misure come **misure interne** dei locali, salvo che il testo dica altro («11 × 8 m esterni»); metti i muri perimetrali **fuori** dal rettangolo interno, e scrivi in `note` come l'hai letta. Se la descrizione è ambigua — quale parete, da che parte si apre una porta, dov'è il terrazzo — **chiedi**, non scegliere |
| **le sigle dei pezzi** | dalla **tavola dello schema funzionale**: la tabella delle apparecchiature e le sigle scritte sul disegno. Sono le stesse sulla pianta. Sul pezzo scrivi anche l'`id` del grafo: con `--grafo` il comando ritrova il pezzo e controlla la sigla |
| **i numeri di tratta** e le lunghezze | dalla **tabella delle tratte della distinta** (`tabelle-del-foglio.json`, o `distinta.json`, che il comando `distinta` scrive): T01, T02… e la lunghezza di ogni tratta. Una tratta della distinta che è un raccordo diretto (lunghezza 0, la ripresa attaccata alla macchina) non ha tracciato |
| **le posizioni** | dal progettista; quelle che assumi le scrivi in `note` come «da confermare» |
| **gli ingombri** (`larghezza`, `profondita`) | il catalogo **non** ha le dimensioni dei pezzi. **Chiedile al progettista**, o prendile dalla **scheda del costruttore** del modello che lui ha indicato. Se non ci sono, scrivi valori dichiarati e metti sul pezzo `"ingombro_da_confermare": true`: la tavola li elenca in nota («Ingombri da confermare»). Non scriverli come se fossero dati |

La tavola stampa la nota «Sigle e numeri di tratta come lo schema funzionale e la distinta». **Non
si ricopiano a mano e basta**: passa `--distinta` e `--grafo`, e il comando controlla che ogni
tracciato abbia nella distinta una tratta con lo stesso numero, gli stessi capi (le sigle, con gli
stessi organi in linea) e la stessa lunghezza data, che ogni tratta della distinta sia in pianta, e
che ogni pezzo con l'`id` del grafo abbia la sigla che lo schema gli dà. La nota dice allora
«Controllati con la distinta e il grafo: concordano», oppure «ci sono discordanze». Ogni discordanza
è un avviso, sulla tavola e in console; **un numero di tratta che nella distinta collega pezzi
diversi ferma la consegna** (uscita `2`). Senza i due file la nota dice «Non controllati dal
comando», ed è vero. Se lo schema non dà la sigla a un pezzo, o la distinta non numera una tratta,
non inventarli: chiedi, o fai rigenerare lo schema e la distinta.

## 4. Il JSON, campo per campo

Lo schema esatto è `schemas/pianta.schema.json`; un esempio completo è
`examples/pianta/appartamento-aria-aria.json`. **Metri**, origine **in alto a sinistra**, x verso
destra, **y verso il basso** — come leggi un'immagine.

| campo | che cosa | come lo ricavi |
|---|---|---|
| `muri` | asse (`da`, `a`) e `spessore`; `tipo` perimetrale, portante o tramezza | sul disegno, misurando con la scala; perimetrali 0,30, tramezze 0,10 se il disegno non dice altro |
| `aperture` | `muro`, `centro` (sull'asse del muro), `larghezza`, `tipo`: porta, varco, finestra, foro | le porte con il verso (`apre_verso`), i varchi a tutta altezza, i fori già previsti |
| `stanze` | `id`, `nome`, `zona`, `poligono` (le facce interne), `controsoffitto`, `disimpegno` | dove c'è il controsoffitto lo dice il progettista; i corridoi sono `disimpegno: true` |
| `velette` | rettangoli di controsoffitto fuori dalle stanze che ce l'hanno: `id` e `rettangolo` `[x0, y0, x1, y1]` | **non** un `poligono`: un rettangolo. Esempio sotto |
| `zone_esterne` | dove **fuori dall'edificio** le linee possono correre: `id`, `nome` (si scrive sulla tavola), `rettangolo`, `costo` (1 come in casa; 2-3 se fuori le vuole corte) | il terrazzo, il balcone, la facciata attrezzata: **solo quelli che il progettista dice**. Fuori dalle zone l'esterno non è una strada (§4bis) |
| `sfondo` | facoltativo: un **JPEG** con `px_per_m` e `origine_px` (il pixel del punto 0,0) | quando hai solo il catastale. **I muri principali si dichiarano lo stesso**: l'instradatore non legge l'immagine |
| `pezzi` | `sigla`, `tipo` (l'**id della voce di catalogo**: `return-air-terminal`, non l'id del simbolo `return-grille`), `x`/`y` (il **centro**), `larghezza` (lungo x), `profondita` (lungo y); facoltativi `id` (l'id del grafo), `sovrapposto_a` e `sta`, `ingombro_da_confermare` | le sigle dello schema funzionale. Bocchette e griglie a parete **a cavallo del muro**: il loro foro è il pezzo. Due pezzi uno sopra l'altro: §4ter |
| `tracciati` | `tratta` (T01…), `da`/`a` (sigla o id, o `{pezzo, lato}`), `passa_per`, `fluido`, `dimensione`, `quota`, `fascio`, `lunghezza_m`, `lunghezza_minima_m` | i numeri e le lunghezze della tabella delle tratte. `lato` (sopra, sotto, sinistra, destra) solo dove l'attacco c'è davvero: le uscite di un plenum |
| `dettagli` | facoltativo: i riquadri a scala maggiore, `{id, rettangolo, scala}` | di regola **non lo scrivi**: li fa la tavola dove serve (§6) |

```json
"velette": [{"id": "veletta-soggiorno", "rettangolo": [0.30, 4.95, 2.30, 5.45]}]
```

```json
"zone_esterne": [{"id": "terrazzo", "nome": "Terrazzo", "rettangolo": [0.0, 8.6, 7.35, 10.1]}]
```

I `fluido` sono quelli di `naming/media.json`: `supply_air`, `return_air`, `refrigerant_liquid`,
`refrigerant_gas`, `condensate`, `power_supply`, `interconnection`, `control_bus`, e gli idronici.

Le `quota`: `controsoffitto` (canali, linee frigo, condensa), `traccia` (cavi e bus), `pavimento`,
`a_vista`. Una **porta non lascia passare il controsoffitto** — sopra c'è l'architrave —, un varco
e un foro sì. **La porta di casa** (una porta nel muro perimetrale, una portafinestra) **non lascia
passare niente**: non è un passaggio per i cavi. Se il progettista vuole che un'apertura lasci
passare una quota, lo scrivi nell'apertura (`"passa": ["traccia"]`); un foro previsto nel muro è un'apertura
di tipo `foro`.

### 4bis. Fuori dall'edificio: `zone_esterne`

Fuori dall'edificio si passa **solo dove il progettista lo dichiara**: il terrazzo, il balcone, la
facciata attrezzata, ciascuno una zona in `zone_esterne`. Le linee escono dal muro dove costa meno
— **dal foro dichiarato più vicino al pezzo esterno**, se c'è (un'apertura `foro`), se no forando —
e corrono nella zona. Attorno a un pezzo che sta fuori (l'unità esterna sulla facciata, il suo
sezionatore) si passa anche senza zona, per 30 cm: è la strada dal muro al pezzo.

Altrove l'esterno costa moltissimo, e se una tratta ci passa lo stesso la tavola la segna con una
**fascia rossa** e il comando esce con un **rilievo bloccante** («la tratta esce dall'edificio
fuori dalle zone esterne dichiarate»). La cura non è spostare la linea: è chiedere al progettista
dove si può passare fuori, e dichiararlo. Se non sai dov'è il terrazzo, **chiedi**.

### 4ter. Pezzi uno sopra l'altro: `sovrapposto_a`

La centrale di zona sopra il plenum, la ripresa sotto l'unità interna: in pianta si sovrappongono.
**Non spostarli**: scrivi sul pezzo che sta sopra o sotto l'altro `sovrapposto_a` (la sigla o l'id
dell'altro) e `sta` (`"sopra"` o `"sotto"`):

```json
{"sigla": "CZ-01", "tipo": "zone-controller", "x": 5.5, "y": 4.3, "larghezza": 0.25, "profondita": 0.15,
 "sovrapposto_a": "PLZ-01", "sta": "sopra"}
```

La tavola disegna i due contorni — quello sotto **tratteggiato** — e lo scrive in nota; le linee
di ciascuno partono dal **suo** ingombro, passando sopra quello dell'altro. Due pezzi che si
sovrappongono **senza** `sovrapposto_a` sono un rilievo bloccante: o è un errore di posizione, o
manca la dichiarazione.

### La lunghezza: `lunghezza_m`

**La lunghezza è del progettista**: scrivi in `lunghezza_m` la stessa del grafo dello schema (la
`lunghezza_m` della tubazione, la colonna «L stim.» della tabella delle tratte); con `--distinta`, se
la dimentichi la prende dalla distinta, e la tabella lo dice. **La scritta sulla linea dice la
lunghezza del progettista**, come lo schema: «T01 · Ø200 · L 5 m», la stessa scritta che
l'installatore legge sullo schema per lo stesso tratto. La colonna «L quot.» della tabella usa la
stessa lunghezza con la regola della distinta — maggiorazione, minimo della classe del fluido, il
cavo fra le unità che segue le linee frigo —, e **pianta e distinta danno lo stesso numero** da
quotare. La scritta di un fascio dice una lunghezza sola se sono uguali, se no tutte: «T06+T07+T11
· L 9 m / 9 m / 10 m». La misura in pianta va nella colonna «L mis.»: è un controllo.
Se supera la lunghezza data di oltre il 15 % (`parametri.scarto_della_misura`), la tavola lo dice
negli avvisi e la colonna lo segna con `!`: o il percorso è sbagliato, o il dato; chiedi.

Se il progettista **non** ha dato la lunghezza, la scritta dice la misura col `°` («L 3,4 m°») e la
tavola quota la misura, segnata anche lei con `°`; in
`.tracciati.json` trovi `lunghezza_misurata_m`: **riportala nel grafo** (o chiedila), così la
distinta quota lo stesso numero. Non scrivere `maggiorazione` nella pianta: la regola è quella
della distinta; se il progettista ne dà un'altra, la tavola la usa e avvisa che i numeri possono
non coincidere.

### Organi in linea: `passa_per`

Lo schema numera quadro – sezionatore – unità esterna come **una** tratta. Nella pianta è **un**
tracciato, con il sezionatore in `passa_per` (sigla o id, in ordine da `da` ad `a`): si instrada
a tronchi, ma ha un numero solo, una scritta sola, una lunghezza sola. Non inventare «T10b».

```json
{"tratta": "T10", "da": "QE-01", "a": "UE-01", "passa_per": ["SZ-01"], "fluido": "power_supply",
 "dimensione": "3G4", "quota": "traccia", "lunghezza_m": 18}
```

### Fasci

Un **`fascio`** è fatto di tracciati fra **gli stessi due pezzi** (liquido, gas e cavo fra le due
unità): corrono paralleli a passo fisso e hanno una scritta sola. Non dichiarare fascio cavi che
vanno in posti diversi — i bus a stella dalla centrale non sono un fascio.

### Le forature, per la distinta: `attraversamenti`

`.tracciati.json` dice per ogni tratta `attraversamenti_di_parete`: le pareti **interne** che la
tratta fora (fuori da un'apertura che lascia passare la sua quota) più il foro del pezzo a parete
che è un suo capo (la bocchetta nella tramezza); i fori nel muro perimetrale stanno a parte
(`fori_nel_perimetrale`), perché quello dell'unità esterna la distinta lo conta già con la sua
posa. Li trovi tutti insieme in `per_il_grafo.attraversamenti`. **Riportali nel grafo**, fra le
`properties` di una tubazione della tratta, come `attraversamenti`, e rifai la distinta: così conta
le forature della pianta invece di assumerne una per ramo. Le linee frigo forano insieme: la
distinta le conta sulla linea del gas.

## 5. Che cosa la tavola garantisce — misurato, non promesso

Il comando stampa i controlli e li scrive in `.tracciati.json`:

- **diagonali: 0**, sempre — tracciati e richiami;
- **sovrapposizioni: 0** — due tracciati non corrono mai sullo stesso tratto;
- **nessuna linea sopra un pezzo** che non è un suo capo o un suo organo in linea;
- **scritte che toccano una linea o un'altra scritta: 0**;
- **richiami corti** (al più 12 mm di carta, 60 cm a 1:50) che non attraversano muri, pezzi né
  scritte, e al più **una** linea — contata e detta. Dove una scritta non ha posto vicino, va **in
  legenda**: un numero cerchiato accanto alla linea, il testo nella colonna;
- **tratte non instradate**: dette una per una, e disegnate tratteggiate;
- **sormonti**: contati ed elencati; il percorso li evita quando può, non sempre può;
- **forature**: ogni muro passato fuori da un'apertura che lascia passare quella quota, numerata
  F1, F2… sulla tavola e nella colonna. Un fascio che fora lo stesso muro fa un foro solo;
- **fuori dall'edificio solo nelle zone esterne**: una tratta che esce altrove ha la **fascia rossa**
  ed è un rilievo bloccante (§4bis);
- **pezzi sovrapposti solo se dichiarati** (§4ter), se no bloccante;
- **sigle, numeri di tratta, capi e lunghezze** come la distinta e il grafo, se li passi (§3);
- **controsoffitto che manca**: un tracciato in controsoffitto dove il controsoffitto non c'è ha
  sotto una **fascia arancio**, e la colonna lo dice negli avvisi («canalina o traccia, da
  verificare»). Il percorso lo evita quando c'è un'altra strada in controsoffitto, anche se più
  lunga; all'esterno, nelle zone esterne, non conta;
- **i fasci stanno insieme**: liquido, gas e cavo corrono paralleli, e un fascio intero si
  preferisce ai tracciati presi uno per uno anche se costa un po' di più (fino al 50 %).

Tutto quello che ferma la consegna esce come `BLOCCANTE` e con uscita `2`.

## 6. Il nodo fitto e il riquadro di dettaglio

Attorno a un'unità interna con il plenum, la ripresa e la centrale, a 1:50 le scritte possono non
starci. Allora la tavola fa da sé un **riquadro di dettaglio a 1:20**: incornicia la zona sulla
tavola intera («Dettaglio A 1:20») e la disegna su una tavola a parte, `<nome>-dettaglio-A`, con
le scritte che a 1:50 non stavano. Se vuoi tu la zona, la dichiari in `dettagli`; `"dettagli": []`
li spegne, e allora le scritte senza posto fermano la consegna. **Guarda anche il dettaglio.**

## 7. Che cosa la tavola non garantisce

- **I percorsi sono indicativi**: la tavola lo scrive, e vanno verificati in sopralluogo. Non
  conosce travi, impianti esistenti, pendenze della condensa, altezze libere.
- **Le lunghezze misurate** sono quelle della spezzata in pianta: salite e discese stanno
  nell'aggiunta della regola. Se la planimetria è un catastale a 1:200, valgono ±10-15 %.
- **Non sceglie dove stanno i pezzi**: se il disegno è un groviglio, il primo sospetto è la posa.
  Un'unità di 1 m in un corridoio di 1,5 m lascia 25 cm per lato: i tracciati non ci passano, e i
  bus finiscono a forare le stanze accanto. Sposta o ruota il pezzo, non chiedere
  all'instradatore di fare miracoli.

## 8. Prima di consegnare, guarda l'anteprima

Se i controlli sono a zero e la tavola a occhio non si legge — un groviglio, una linea che
gira intorno a una macchina, un bus che passa per il bagno — **scrivilo**: è il rilievo più utile
che puoi portare. Le cure sono nella posa dei pezzi e nei `lato`, non nei percorsi.
