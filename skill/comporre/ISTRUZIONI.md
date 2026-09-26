# Comporre — dal grafo completo al piano

**Queste istruzioni bastano da sole.** Non serve leggere altro per fare il lavoro: tutto
quello che ti serve — il metodo, i numeri delle porte, il formato del file, i controlli — sta
qui. I rimandi ai documenti servono a chi vuole sapere **da dove viene** una regola, non a chi
deve applicarla.

---

## 1. Il lavoro, in tre righe

Ricevi il **grafo completo** di un impianto — tutti i pezzi e tutte le tubazioni fra loro — e
produci il **piano**: un file JSON che dice **dove sta ogni pezzo posabile sul foglio**, e
nient'altro.

Non disegni tu. Il piano lo esegue un motore deterministico che posa, orienta, instrada in
griglia, interrompe le linee sotto i simboli, impagina e misura. **Tu decidi una cosa sola —
dove stanno i pezzi — e quella cosa decide la tavola.**

> **Il metro non è il numero di pieghe.** È se la tavola **assomiglia al lavoro di un
> disegnatore**. Un criterio grafico, non matematico.
>
> **E non esiste un numero massimo di curve** (**D-171**). Il committente, il 22 settembre
> 2026: «più dritte possibili, meno curve possibili e meno sormonti possibili, e viaggiano in
> parallelo. **Non c'è un numero massimo** — dicevo una curva nel caso del generatore singolo e
> due accumuli, ma era per far capire il concetto». Quindi **non hai un budget da spendere**:
> hai un confronto da vincere. Fra due pose dello stesso impianto vince quella con meno pieghe
> e meno sormonti, e **una piega che i simboli impongono non la conti fra le tue** — un
> collettore verticale si attraversa con due pieghe, una tre vie sulla terza via con una,
> l'ultima macchina entra in fondo al collettore con un gomito, e quelle non sono tue.

---

## 2. Il metodo, e viene prima di ogni regola

**Il disegno nasce dalle autostrade.** Lo ha detto il committente così:

> «Sposta le macchine in modo che le linee delle autostrade vengano con pochissime curve, poi
> attacchi il resto delle valvole piccole e strade secondarie. Ma **il disegno nasce dalle
> linee delle autostrade**. LE AUTOSTRADE CON POCHE CURVE e pochi sormonti.»

Un'**autostrada** è la tubazione grossa che unisce due macchine: la mandata dal generatore
all'accumulo, il ritorno dall'utenza al generatore, il tronco che attraversa la centrale.
**Per definizione ha poche curve e tratti rettilinei.** Le strade secondarie sono gli stacchi
verso valvole, strumenti, confini di rete.

### 2.1 La cosa che devi sapere prima di tutte: **la quota di un'autostrada non si sceglie**

È quella della **porta** della macchina che la genera. Le porte stanno a **millimetri fissi
dall'origine del pezzo**, e li trovi nel manifesto del simbolo (`assets/symbols/<id>.json`).
Questi sono quelli che incontri quasi sempre:

| pezzo | ingombro | porte, e a che quota dall'origine |
|---|---|---|
| `heat-pump-air-water` | 40 × 30 | `water_supply` **destra +5** · `water_return` **destra +20** |
| `gas-boiler` | 40 × 30 | `water_supply` **destra +5** · `water_return` **destra +20** |
| `heat-pump-air-water-large` (pompa di calore di alta potenza) | 60 × 30 | `water_supply` **destra +5** · `water_return` **destra +20** |
| `gas-boiler-modular` (caldaia modulare) | 60 × 25 | `water_supply` **destra +5** · `water_return` **destra +20** |
| `solar-collector` (collettore solare) | 40 × 25 | `supply` **destra +5** · `return` **destra +20** — sul fluido solare |
| `buffer-four-port` | 25 × 45 | `primary_in` **sinistra +5** · `primary_out` **sinistra +20** · `secondary_out` **destra +5** · `secondary_in` **destra +20** · `vent` sopra e `drain` sotto, a x +12,5 |
| `buffer-two-port` | 25 × 45 | `a` sinistra +5 · `b` destra +5 · `vent` sopra e `drain` sotto, a x +12,5 |
| `dhw-heat-pump` (pompa di calore per ACS) | 25 × 45 | `cold_in` sinistra +37,5 · `dhw_out` sopra, a x +12,5 |
| `zone-manifold` (collettore di zona) | 40 × 5 | `in` sinistra +2,5 · `out_1` sotto, a x +12,5 · `out_2` sotto, a x +27,5 |
| `buffer-combined` | 25 × 45 | `primary_in` **sinistra +5** · `primary_out` **sinistra +20** · `secondary_out` **destra +5** · `secondary_in` **destra +20** · `dhw_out` sopra, a x +7,5 · `cold_in` sinistra +37,5 |
| `plate-heat-exchanger` | 12,5 × 25 | `primary_in` **sinistra +5** · `primary_out` **sinistra +20** · `secondary_out` destra +5 · `secondary_in` destra +20 |
| `dhw-cylinder` | 25 × 45 | `coil_in` sinistra **+7,5** · `coil_out` sinistra **+17,5** · `dhw_out` sopra · `cold_in` sinistra +37,5 · `recirculation_in` **destra +12,5**, il ricircolo (D-176) |
| `radiator`, `fan-coil`, `fan-coil-ducted`, `ahu-coil`, `underfloor-panel` | 20 × 15 | `in` **sinistra +2,5** · `out` **sinistra +12,5** — tutt'e due **sullo stesso lato** (D-167) |
| `dhw-cylinder-twin-coil` (bollitore a due serpentini) | 25 × 55 | `coil_in` sinistra **+7,5** · `coil_out` sinistra **+17,5** · `solar_coil_in` sinistra **+27,5** · `solar_coil_out` sinistra **+37,5** · `cold_in` sinistra +47,5 · `dhw_out` sopra, a x +7,5 · `recirculation_in` destra +12,5 |
| `mixing-valve-thermostatic` (miscelatrice termostatica ACS) | 5 × 10 | `hot_in` sinistra +5 · `out` destra +5 · `cold_in` **sotto, a x +2,5** — è una tre vie (D-175): la posi tu, e la giri |

**Guarda l'interasse.** Pompa di calore, caldaia, volano e scambiatore a piastre hanno tutti
le due porte principali a **15 mm** l'una dall'altra, e alle **stesse quote +5 e +20** — e
così la pompa di calore di alta potenza, la caldaia modulare e il collettore solare. Questo
vuol dire una cosa sola, ed è la leva più potente che hai:

> ## Due macchine posate allo **stesso y** danno **due autostrade perfettamente rette**, gratis.

Pompa a `y=60` e volano a `y=60`: la mandata corre a 65 da una porta all'altra senza una
piega, il ritorno a 80. **Non hai speso niente.** Se invece le posi a `y=60` e `y=75`, ogni
linea fra loro fa **due pieghe** e te le porti dietro per tutta la tavola.

⚠ **Conta la quota della porta, non l'origine.** «Stesso `y`» vale per chi ha le porte alle
stesse quote. Un volano **a due attacchi** ha `a` e `b` tutt'e due a +5: per metterlo sul
ritorno di una pompa, che esce a +20, lo posi **15 mm più in basso** della pompa.

⚠ **Il bollitore ha l'interasse 10, non 15** — `coil_in` +7,5 e `coil_out` +17,5 — perché
quelle due porte dicono **dov'è la serpentina dentro l'accumulo**, e non si spostano. La
coppia che lo serve **cambia interasse per forza**: è vero, è noto, e non si cura.

⚠ **Un terminale si prende da un lato solo**: `in` e `out` stanno tutt'e due sulla **faccia
sinistra**, a +2,5 e +12,5, con la mandata sopra. La coppia gli arriva **affiancata** e entra:
niente giro intorno, niente fascia sprecata a destra. È **D-167**, e il PO l'ha disposto così
dopo aver ridisegnato a mano due nostre tavole: «con uscita dall'altro lato **si spreca
spazio**, meglio metterli sempre con **ingresso e uscita su un lato solo**».

### 2.2 Il procedimento, in quest'ordine e non in un altro

1. **Leggi le porte delle macchine di spina** — generatori, accumuli, scambiatori, volani. La
   quota delle autostrade è già decisa da loro.
2. **Posa le macchine su quelle quote.** È la mossa che decide la tavola. Scegli **una fascia
   orizzontale per il primario** e mettici tutte le macchine che quel tronco attraversa, con
   lo **stesso y**.
3. **Chi sta in parallelo si impila**, uno sopra l'altro, e si unisce con **una verticale sola,
   corta, accanto alle macchine** — non in mezzo al foglio. Ogni macchina ci entra con uno
   **stacco orizzontale corto**.
4. **Tira le autostrade con gli occhi e guarda se sono rette**, prima di appendere qualunque
   cosa. Se una piega, torna al punto 2: **si sposta la macchina, non si accetta la piega**.
5. **Solo adesso** appendi valvole, strumenti, confini di rete e strade secondarie.

---

## 3. Cosa ricevi

Il **grafo completo** in JSON. Quello che ti serve:

- `components` — ogni pezzo con `id`, `definition_id` (che dice quale simbolo è), `tag`;
- `connections` — ogni tubazione, con le due estremità `{component_id, port_id}` e la rete;
- `networks` — a che circuito appartiene ogni tubazione, e con che fluido.

**Da un pezzo al suo simbolo.** `definition_id` dice **che cosa è** il pezzo, non quale
simbolo lo disegna: il simbolo lo dice la voce di catalogo del pezzo
(`examples/layout/catalog/<definition_id>.json`, campo `symbol_id`), e il manifesto è
`assets/symbols/<symbol_id>.json`. Serve, perché i nomi non coincidono sempre: `tee-split` e
`tee-junction-dhw` si disegnano col simbolo `tee-junction`, `cold-water-inlet` e
`dhw-draw-off` con `network-boundary`, tutte le `valve-isolation-*` con `valve-isolation`.

**Chi è una macchina e chi è corredo** lo capisci dall'ingombro e dalle porte: un pezzo 40×30
o 25×45 è una macchina, un pezzo di 5 o 7,5 mm con due porte in linea è un organo che sta
**sopra una tubazione**. Un `tee` è un raccordo: unisce tre tubazioni e **non si posa a
occhio**, si posa dove il collettore deve stare. **Quale tubazione gli passa dritta lo decide
la posa, non il grafo**: il motore gira il raccordo e gli assegna le porte guardando dove
stanno i vicini — chi è allineato con l'uscita entra dritto, l'altro dalla derivazione.
Misurato: scambiando di posto le due zone che un raccordo riunisce, la mappa delle porte si
inverte con loro.

---

## 4. Il file che produci

JSON, e solo queste chiavi:

```json
{
  "formato": "A2",
  "note": [
    "Le due pompe impilate a x=35, y=60 e y=110: il collettore e' una verticale corta accanto a loro (A2, B3).",
    "Volano a y=60, sulla stessa quota della pompa maestra: mandata e ritorno rette, zero pieghe (D-159)."
  ],
  "pezzi": {
    "pdc-1":   {"x": 35,  "y": 60,  "regola": "D-159 — quota della porta"},
    "pdc-2":   {"x": 35,  "y": 110, "regola": "A2 — chi sta in parallelo si impila"},
    "volano":  {"x": 220, "y": 60,  "regola": "D-159 — stesso y della pompa: autostrade rette"},
    "deviatrice": {"x": 150, "y": 62.5, "rotazione": 0}
  }
}
```

- **`formato`** — uno fra `A3`, `A2`, `A1` (l'A4 non c'è più: non contiene il cartiglio, **D-186**).
  Scegli il più piccolo in cui l'impianto ci sta comodo. ⚠ **Ma non allargare il disegno per riempirlo**: il vuoto non è un difetto
  (**D-170**, D3). **Se hai preso un foglio più grande del necessario te lo dice il rapporto**
  (`SHEET_LARGER_THAN_NEEDED`), e si cambia una riga e si rilancia.
- **`pezzi`** — un'entrata per **ogni pezzo di `components` che posi tu**, e **solo** per
  quelli. ⚠ Il grafo nomina altre decine di identificativi in `subsystems` e
  `rule_applications` che **non sono pezzi**: ignorali.
  **Gli organi in linea non li posi tu**: valvole d'intercettazione, filtri, defangatori,
  separatori d'aria, circolatori, ritegni, riduttori, gruppi di sicurezza sanitari. Li
  riconosci dal manifesto del simbolo, che dichiara `inline_gap_mm`: il motore li posa **da
  solo, sulla loro tratta** (§4bis). Se ne scrivi uno nel piano, il comando te lo dice e si
  ferma. ⚠ Il **rubinetto portamanometro** si chiama «a tre vie» (`valve-gauge-cock-3way`) ma
  è un organo in linea a due attacchi: non è una tre vie, non si posa e non si ruota.
  ⚠ **La miscelatrice termostatica dell'ACS non è più un organo in linea** (**D-175**): ha il
  terzo attacco, da cui entra l'acqua fredda, e **la posi tu** come ogni tre vie.
  **Tutti gli altri li posi tu**: macchine, raccordi (`tee-*`), valvole a tre vie — compresa
  la miscelatrice termostatica —, strumenti, sfiati, scarichi, vasi, gruppi di riempimento,
  confini di rete. Uno che dimentichi il motore
  lo mette accanto al pezzo a cui è attaccato, come può: è una rete di sicurezza, non un modo di
  comporre — **scrivili tutti**.
  `x` e `y` sono in millimetri, **origine in alto a sinistra del pezzo**, e si arrotondano al
  passo di griglia: **usa multipli di 2,5**.
  **Non sono coordinate sul foglio: contano solo le posizioni relative.** Prima di instradare
  il motore porta l'intero disegno al centro dell'area del formato che hai scelto, la stessa
  traslazione per tutti i pezzi — puoi cominciare da zero, e anche andare in negativo. Per
  questo non puoi collocare niente rispetto al bordo o al cartiglio: **D1 si governa con la
  forma della posa, D3 con la scelta del formato**. Quello che deve tornare è la misura: il
  disegno deve **starci** nell'area del formato, altrimenti le tratte che escono non trovano
  strada.
- **`rotazione`** — in **gradi orari**. **Scrivila solo dove la deduzione non arriva**: per un
  raccordo o per un pezzo con un attacco solo **non scriverla**, perché la rotazione è una
  conseguenza della posa e il motore la deduce dai vicini che il pezzo ha davvero.
  ⚠ **Su una valvola a tre vie devi scriverla** (**D-168**): la deduzione non la gira, e senza
  la tua scelta la terza via finisce **sempre verso il basso**. Il PO l'ha detto guardando le
  tavole: «la valvola a tre vie la metti sempre con uscita terza verso il basso, **guarda che
  puoi ruotarla**». **La terza via guarda il pezzo che serve**, e da che parte sta quel pezzo lo
  sai tu. Lo stesso vale per il **gruppo di riempimento**, che ha due attacchi e non è una
  macchina, e per la **miscelatrice termostatica**: il PO, il 23 settembre 2026, «anche lei è
  una di quelle valvole che deve poter ruotare e specchiare per evitare sormonti o curve non
  necessarie» (**D-175**).
- **`specchio`** — vero o falso, e si applica **prima** della rotazione, attorno all'asse
  verticale del pezzo. **Le giaciture sono otto, non quattro** (**D-169**), e per una valvola a
  tre vie le quattro rotazioni **non bastano**: leggi il riquadro qui sotto prima di posarne una.
  ⚠ **Molti simboli non si ruotano affatto** — pompa di calore, caldaia, volano, scambiatore a
  piastre dichiarano `allowed_rotations_deg: [0]`, e chiedere un'altra rotazione **fa abortire
  il comando**. Guarda il manifesto prima di scriverla. **Lo specchio invece vale per tutti**,
  anche per chi non si ruota (D-169): un volano a due attacchi specchiato ha `a` a destra e `b`
  a sinistra, ed è il modo di farlo guardare dall'altra parte senza girarlo.
- **`note`** e **`regola`** — **non sono decorazione.** Il piano senza di loro dice dove
  stanno i pezzi e non dice **perché**, e chi lo rivede non può correggerlo: può solo
  spostare. `note` porta la motivazione del piano intero, `regola` la stessa cosa pezzo per
  pezzo. **Ogni pezzo che hai spostato per una ragione porta quella ragione.**

Niente altre chiavi: il caricatore rifiuta quello che non riconosce, e te lo dice.

### 4bis. Il corredo: che cosa posa il motore, e che cosa chiede a te

Il grafo completo porta il **corredo** — organi in linea, strumenti, sfiati, scarichi, vasi,
gruppi di riempimento, confini di rete — e si mette **dopo** lo scheletro (§2.2, passo 5). È
di due specie, e le due si trattano in modo diverso:

- **gli organi in linea li posa il motore**. Si mettono in fila sulla loro tratta **a partire
  dalla porta del pezzo che isolano** — da un capo della tratta o dall'altro, secondo chi si
  manutiene —, a distanza fissa, e ogni organo vuole il proprio pezzo di rettilineo. **Il tuo
  lavoro è lasciarglielo** (B5): se la tratta non ha il rettilineo che la fila chiede, il
  comando si ferma e ti dice su quale tratta e quanti millimetri servono — «run X has no
  straight stretch of N mm for …». Si cura allontanando i due pezzi che la tratta unisce, o
  raddrizzandola; **mai** togliendo un organo, che è contenuto dell'impianto.
  **Quanto rettilineo chiede una fila**, misurato sul motore il 23 settembre 2026 fra la porta
  di una pompa e un raccordo: con una valvola **17,5 mm**, con due organi **20–25 mm**. Non è
  una costante: è il punto da cui partire, e se non basta il comando ti dice la tratta —
  allontana i due pezzi **un passo alla volta**;
- **gli appesi li posi tu**: un manometro, un termometro, uno sfiato, uno scarico, un vaso,
  una sicurezza, un gruppo di riempimento stanno all'altro capo di uno **stacco** che parte da
  un raccordo sulla linea (`tee-branch`). Stanno **addosso** (A4), con lo stacco più corto che
  la griglia consente: il rilievo `SERVICE_STUB_LONGER_THAN_ITS_MINIMUM` ti dice di quanti
  millimetri sei lontano. **Il raccordo che regge lo stacco sta sulla linea, alla sua quota**
  (B8): fuori quota, la linea va a prenderlo e torna. E **prima di appendere guarda quale
  autostrada passa di lì** (§6): un appeso nella colonna che una linea deve percorrere la
  costringe a girargli intorno;
- **i confini di rete** — l'acquedotto, le utenze sanitarie — stanno **addosso al pezzo che
  servono**, con lo stacco minimo (A4), non nella fascia della distribuzione. Vale anche per
  gli ingressi dell'acqua fredda che il completamento aggiunge — `AF-02`, `AF-03`… —, uno per
  ciascun pezzo che la usa: il gruppo di riempimento e la **miscelatrice termostatica**, che
  riceve il suo «pezzetto di AF in ingresso» (D-175) sulla terza via, `cold_in`. Il suo
  confine sta **sotto la terza via**, o dove l'hai girata, con la valvola di confine in mezzo.
- **il ricircolo sanitario**, dove c'è, **entra dal proprio confine** — sigla «ACS-R», lo
  stesso simbolo dell'ingresso dell'acqua fredda — e **torna nel bollitore** dal suo
  attacco destro, `recirculation_in` (D-176). Sulla sua tratta il motore mette in fila il
  circolatore, il ritegno e le valvole: è una tratta lunga, e vuole il suo rettilineo (B5).
  **Si disegna verde chiaro**, ed è giusto: è il colore che il committente usa per il
  ricircolo.

⚠ **Lo scheletro si posa pensando al corredo.** Le porte che il corredo userà dopo devono
restare raggiungibili: l'acqua fredda del bollitore entra da **sinistra a +37,5**, e se davanti
ci passano le due verticali della serpentina resta murata. Prima di chiudere lo scheletro,
guarda dove attaccherà ogni confine di rete e ogni appeso.

### L'algebra di una valvola a tre vie, e perché le rotazioni non bastano

Una tre vie ha la **via dritta** — `in_a`/`out` su facce opposte — e la **terza via
perpendicolare** a quella. Ruotando, **gira tutto insieme**: la terza via resta sempre dalla
stessa parte rispetto al verso della via dritta.

`switching-valve-3way`: `in_a` **sinistra** · `out` **destra** · `in_b` **sotto**.
`diverting-valve-3way`: `in` **sinistra** · `out_a` **destra** · `out_b` **sotto**.
`mixing-valve-thermostatic`: `hot_in` **sinistra** · `out` **destra** · `cold_in` **sotto** —
la via dritta è quella dell'acqua calda, dall'accumulo alle utenze, e la terza via è l'acqua
fredda che la miscela (D-175). Ha le giaciture della deviatrice, con `hot_in`, `out` e
`cold_in` al posto di `in`, `out_a` e `out_b`; è larga 5 e alta 10, quindi la terza via sta a
**x +2,5**, e ruotata di 90 o 270 diventa larga 10 e alta 5.

Le **otto** giaciture della commutatrice, e serve leggerla come una tabella:

| | `in_a` | `out` | `in_b` |
|---|---|---|---|
| rotazione 0 | sinistra | destra | sotto |
| rotazione 90 | **sopra** | **sotto** | sinistra |
| rotazione 180 | destra | sinistra | sopra |
| rotazione 270 | sotto | sopra | destra |
| specchio + 0 | destra | sinistra | sotto |
| specchio + 90 | sotto | sopra | sinistra |
| specchio + 180 | sinistra | destra | sopra |
| **specchio + 270** | **sopra** | **sotto** | **destra** |

E quelle della **deviatrice**, che ha la stessa forma con altri nomi:

| | `in` | `out_a` | `out_b` |
|---|---|---|---|
| rotazione 0 | sinistra | destra | sotto |
| rotazione 90 | sopra | sotto | sinistra |
| rotazione 180 | destra | sinistra | sopra |
| rotazione 270 | sotto | sopra | destra |
| specchio + 0 | destra | sinistra | sotto |
| specchio + 90 | sotto | sopra | sinistra |
| specchio + 180 | sinistra | destra | sopra |
| specchio + 270 | sopra | sotto | destra |

Serve ricevere dall'alto, mandare in basso e prendere la terza via **a destra**? **Nessuna
delle quattro rotazioni ce l'ha.** La 90 ha le prime due ma la terza via a sinistra; la 270 ha
la terza via giusta e le altre due rovesciate. La giacitura esiste, ed è **una sola**:
`{"rotazione": 270, "specchio": true}`.

⚠ **Che succede se la sbagli, misurato:** la linea che arriva dalla parte sbagliata **gira
intorno alla valvola** — scende sotto, la scavalca, rientra dall'altra faccia — con **quattro
pieghe**. Sull'impianto 4, mettere la giacitura giusta ha portato le spezzate piegate da 4 a 3,
le pieghe da 5 a 4 e i sormonti da 3 a 2.

**La regola che ne esce, e vale oltre le tre vie:** un organo a tre vie **non si appende a una
linea** — si posa **nel punto dove le sue tre linee si incontrano**, e poi si sceglie la
giacitura che fa entrare ciascuna dalla faccia da cui arriva.

### I quattro numeri che ti servono, e che nessun errore dovrebbe doverti insegnare

| | |
|---|---|
| passo di griglia | **2,5 mm** — ogni `x` e `y` è un suo multiplo |
| stacco minimo di un organo di servizio (A4) | **10 mm** se lo stacco è vuoto; se porta organi in linea, quanto chiede la loro fila — il rilievo `SERVICE_STUB_LONGER_THAN_ITS_MINIMUM` scrive il minimo di ogni stacco. Sotto i 10 mm il motore a volte instrada, ma **due simboli più vicini di 10 mm si leggono come uno** (D-062): non ci scendere |
| corsia libera fra due linee affiancate (B9) | **10 mm** |
| interasse delle porte principali di una macchina | **15 mm** — pompa, caldaia, volano, scambiatore |

---

## 5. Le regole, nell'ordine in cui si applicano

Quando due si contendono lo stesso pezzo, **vince quella più in alto**, e la più in basso
cede. **Non si sommano mai**: una media pesata fra regole è il modo in cui questo progetto ha
già sbagliato una volta.

### A1 — Tre fasce verticali, da sinistra a destra
**Generazione** · **accumuli e scambiatori** · **distribuzione**: le parole sono del PO, e il
processo si legge da sinistra a destra. Chi sta in quale fascia lo dice il catalogo, ed è la
stessa lettura del rilievo `PIECE_OUTSIDE_ITS_BAND`:

- **generazione** — chi genera: pompe di calore, caldaie, **e la pompa di calore per ACS**
  (`dhw-heat-pump`), che il catalogo dichiara generatore anche se ha un accumulo dentro;
- **accumuli e scambiatori** — volani, bollitori, separatori, **scambiatori a piastre**,
  compreso quello istantaneo dell'ACS;
- **distribuzione** — i terminali che consegnano il calore all'ambiente.

**Non hanno una fascia**, e quindi non la allargano e non la violano: raccordi, organi in
linea, appesi, collettori, valvole a tre vie, confini di rete. Stanno dove serve il pezzo a
cui sono legati.

### A2 — Chi sta in parallelo si impila
Due pompe, tre pompe in cascata, due caldaie: **uno sopra l'altro, stessa x**, con un passo
verticale costante. Mai affiancate.

### A4 — Un organo di servizio sta **addosso** al pezzo che serve
Un confine di rete, un prelievo, uno scarico: **lì accanto, con un tratto di tubazione
corto**. Non «da qualche parte nella fascia giusta». È l'errore più comune di chi legge solo
A1: mette il confine ACS nella fascia della distribuzione e lo fa finire **a mezzo foglio di
distanza** dal bollitore che serve.

### B1 — Le autostrade dritte
Vedi §2. **Se una piega, si sposta la macchina** — a meno che la piega non te la impongano i
simboli, e allora non è tua e non la puoi togliere spostando niente. **Non c'è un massimo di
curve** (**D-171**): il rilievo `HIGHWAY_IS_NOT_STRAIGHT` ti dice quante ne hai fatte **in
più** di quelle imposte, e quelle in più si tolgono spostando le macchine.

**Quali pieghe ti impongono i simboli, e quali no.** Sono imposte:
- **dentro un pezzo** che la catena attraversa: entrare da una faccia e uscire da una
  perpendicolare è una piega — il collettore verticale che B3 pretende ne costa due, una tre
  vie sulla terza via una;
- **fra due pezzi** le cui porte stanno su **assi perpendicolari** — una uscita orizzontale e
  una verticale: è una **L**, e non la toglie niente. È il gomito dell'ultima macchina in
  fondo al collettore verticale, la terza via della deviatrice che va alla serpentina del
  bollitore, la testa della colonna del pettine;
- il **gradino di una coppia** fra due macchine con interassi diversi — il volano a 15, il
  terminale a 10: una delle due linee corre dritta, l'altra scala di 5 mm, e quello è il suo
  prezzo.

**E un sormonto può essere imposto anche lui.** Un pezzo che prende dalla mandata e rende al
ritorno, e sta **fuori dalla coppia** — il bollitore appeso sotto o sopra le due linee del
primario — con una delle due diramazioni deve scavalcare l'altra linea: un sormonto che
nessuna posa toglie.

**Non sono imposte**, e il rilievo te le conta:
- una **U** fra due porte che guardano dalla stessa parte: si toglie **specchiando** uno dei due
  pezzi (§4, `specchio`);
- una linea che **gira intorno** a un pezzo che dovrebbe attraversare dritta — una tre vie o un
  raccordo di traverso sulla linea: si gira il pezzo, e la linea passa;
- il gradino fra due porte che si guardano, quando le due macchine non stanno allo stesso `y`;
- il giro largo, quando arrivi a una porta dalla parte sbagliata.

### B3 — Più macchine in parallelo ⇒ **collettore verticale**
I due raccordi che uniscono un parallelo stanno su **una verticale corta accanto alle
macchine**. Due collettori — mandata e ritorno — stanno su **due verticali diverse**, vicine.

**Quale delle due sta più vicina alle macchine lo decidono i sormonti**, ed è il committente
che l'ha detto: «indifferente, quello che fa **meno sormonti** direi; se indifferente scegli
tu». Con le macchine impilate, lo stacco che va alla verticale lontana attraversa quella
vicina: qualunque sia l'ordine, qualche sormonto c'è. **Prova i due ordini e tieni quello con
meno sormonti**; a parità scegli, e scrivi nelle note che cosa hai misurato. Misurato sulla
cascata di tre pompe: 5 sormonti con la mandata vicina, 6 col ritorno vicino.

### B8 — Una linea non lascia la propria quota per poi tornarci
Il sali-scendi. Se un pezzo sta su un'autostrada, **posalo sulla quota dell'autostrada**, o la
linea scende a prenderlo e poi risale, portandosi dietro tutto quello che le sta appeso.

### B10 — Mandata sopra, ritorno sotto
Sulle orizzontali, sempre. È anche il motivo per cui le porte sono a +5 e +20 e non viceversa.

### B11 — Mandata e ritorno corrono **insieme**
«Corrono sempre insieme, non esiste che una va e l'altra va zig zag accanto.» Stesso interasse
per tutta la corsa. Se lo perdono, è perché le due macchine agli estremi hanno interassi
diversi — e allora o le allinei, o è uno dei due casi noti: la **serpentina del bollitore**
(interasse 10, §2.1) e il **terminale** (interasse 10, D-167) contro una macchina a 15.

⚠ **Nei due casi noti il rilievo `SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER` è vero e non si
cura**: la coppia cambia interasse per forza, ed è lo stesso gradino che B1 ti dà per imposto.
**Non inseguirlo.** Il rilievo guarda solo le corse di almeno 20 mm: avvicinare il terminale
finché la corsa scende sotto i 20 mm lo spegne senza cambiare il disegno, ed è esattamente
inseguire un numero. Metti il terminale dove il disegno lo vuole, e scrivi nelle note che il
rilievo resta ed è il caso noto.

### B12 — La coppia è un binario, e si ramifica **a pettine**

**È la regola che il PO ha disegnato invece di dirla**, riprendendo due nostre tavole:

> **Mandata e ritorno sono un oggetto solo — un binario a due corsie — e si ramificano a
> pettine.** Due colonne **adiacenti** portano il fluido, e da quelle si stacca **una coppia di
> orizzontali per ogni utenza**: mandata sopra, ritorno sotto, **affiancate per tutta la
> corsa**, fino al terminale, che si prende **da un lato solo**.

Tre cose che questa regola vieta, e che si sbagliano sempre:

1. **una colonna di ritorno lontana**, con ogni utenza che va a prendersela. Le due colonne
   stanno **vicine**, e le utenze si servono dalla coppia;
2. **due collettori distanti fra loro**: stanno su **una colonna stretta addosso alle
   macchine**, non a duecento millimetri;
3. **una coppia che si apre**: se mandata e ritorno prendono strade diverse per arrivare allo
   stesso pezzo, la posa è sbagliata — non l'instradamento.

**Come si compone un pettine**, in pratica: impila le utenze in colonna, metti le due colonne
del binario **alla loro sinistra e vicine fra loro**, e posa ogni utenza alla quota che vuoi —
la coppia le arriva orizzontale, affiancata, e entra da sinistra.

### D1 — Il disegno non arriva al bordo

### D3 — Si prende il foglio più piccolo che contiene il disegno
**Il foglio deve contenere anche la legenda**: se il comando risponde «the legend needs … but
its band is … tall», o «the 3 functional bands need … but the drawing area is … wide», il
formato è troppo piccolo — si prende il successivo, non si comprime il disegno.
⚠ **Il vuoto non è un difetto** (**D-170**). Tieni il disegno **stretto** e prendi il foglio
più piccolo che lo contiene; il bianco che resta non si corregge. **Non allargare mai il
disegno per riempire il foglio**, e soprattutto **non allontanare un pezzo dalla macchina che
serve**: A4 vince su questa regola, sempre. Se hai sbagliato formato te lo dice
`SHEET_LARGER_THAN_NEEDED`, e si cambia una riga e si rilancia.

---

## 6. Quello che il piano **non può** dire, e come si aggira

**Il piano non può chiedere la forma di una spezzata.** Dice dove stanno i pezzi, e la forma
della linea la sceglie l'instradatore sul costo. «Scendi e fai una curva sola» **non si può
scrivere.**

**Se il piano non si instrada**, il comando dice quale tratta, fra quali due pezzi, e dove il
piano li ha messi. La «posa applicata» che stampa è **nel sistema del piano**, al decimo di
millimetro. Le coppie di numeri fra parentesi nel messaggio dell'instradatore sono **celle
della griglia del foglio**: non cercarle nel piano.

**Il colore di una linea lo decide il grafo**, non il verso in cui corre: un ritorno è blu
anche se va da sinistra a destra. Non spostare un pezzo per far uscire una linea del colore
giusto; se una linea esce del colore sbagliato, è un difetto del motore e va scritto.

**L'unica leva che hai è togliere di mezzo chi occupa la strada.** Prima di appendere un
organo, guarda **quale autostrada deve passare di lì**: se ci metti un gruppo di riempimento
nella colonna sotto l'uscita di una valvola, la linea gira intorno — non perché l'instradatore
sbagli, ma perché **non può passare**. È successo, e spostare quel gruppo di 20 mm ha portato
una linea da 3 pieghe a 1.

---

## 7. Cosa non è tuo, e non lo diventa

- **Non cambi il grafo.** Non aggiungi un pezzo, non ne togli uno, non cambi una tubazione. Se
  ti sembra che ne manchi uno, **lo scrivi come domanda dichiarata** e componi lo stesso.
- **Non inventi contenuto MEP.** Dove va la presa del ricircolo, se una valvola ci vuole: non
  è tuo.
- **Non cambi la convenzione grafica.** Colori, tratteggi, incroci, raggi degli spigoli: sono
  decisi, e non si toccano.
- **Non tari soglie e non inventi numeri.** Se ti viene voglia di scrivere «al massimo N
  colonne verticali», fermati: **quel numero non esiste**, e il criterio è grafico.

---

## 8. Il metodo di lavoro, passo per passo

1. **Leggi il grafo e separa** le macchine dal corredo. Disegna a mente lo **scheletro**: solo
   macchine e collettori.
2. **Trova le catene principali** — quali macchine sono unite a quali, e per quale rete. Quelle
   sono le autostrade.
3. **Scegli le quote.** Per ogni catena, guarda le porte delle macchine agli estremi: se hanno
   le stesse quote relative, **posale allo stesso y** e la catena è retta.
4. **Posa le macchine**, fascia per fascia, da sinistra a destra (A1). Impila i paralleli (A2).
5. **Metti i collettori**: una verticale corta accanto al parallelo, e fra mandata e ritorno
   più vicino alle macchine quello che fa meno sormonti (B3).
6. **Ricontrolla lo scheletro**: ogni catena fra due macchine è retta? Se no, torna al 3.
7. **Solo adesso appendi il corredo**, guardando per ognuno **quale autostrada passa di lì**
   (§6), e tenendo i confini di rete **addosso** al pezzo che servono (A4).
8. **Scrivi le note.** Ogni scelta che hai fatto per una ragione porta il nome della regola.

---

## 9. Prima di consegnare: il controllo finale

Rispondi a queste, e se una risposta è «no» torna indietro:

- [ ] **Ogni pezzo che posi tu ha un'entrata in `pezzi`, e nessun organo in linea ce l'ha?**
- [ ] **Le `x` e le `y` sono multipli di 2,5?**
- [ ] **Le porte che un'autostrada unisce stanno alla stessa quota?** Per pompa, caldaia,
      volano a quattro attacchi e scambiatore vuol dire lo stesso `y`; per chi ha le porte ad
      altre quote no (§2.1). Se no, hai una ragione scritta nelle note?
- [ ] **I paralleli sono impilati alla stessa `x`, con passo costante?**
- [ ] **I due collettori di un parallelo sono su due verticali vicine, nell'ordine che fa
      meno sormonti, e l'hai scritto nelle note?**
- [ ] **Ogni confine di rete sta accanto al pezzo che serve?**
- [ ] **Nessun pezzo di corredo sta nella colonna o nella riga che un'autostrada deve
      percorrere?**
- [ ] **Il foglio è il più piccolo che contiene il disegno?** Il bianco che resta non è un
      difetto (D3).
- [ ] **`rotazione` compare solo dove serve davvero?**
- [ ] **Ogni pezzo spostato per una ragione porta la sua `regola`?**

E l'ultima, che vale più delle altre:

- [ ] **Guarda lo scheletro che hai composto e chiediti: assomiglia a una tavola disegnata da
      un disegnatore?** Se la risposta è no, il piano non è finito — anche se tutte le caselle
      sopra sono spuntate.
