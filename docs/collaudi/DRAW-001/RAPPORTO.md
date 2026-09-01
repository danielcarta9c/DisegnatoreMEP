# DRAW-001 — la tavola dell'impianto 1, prima e dopo

**Ramo:** `claude/draw-001-tavola1-qualita`
**Base:** `ebe165a5d0651d108c78833f1275d1327a96d59c` (il `main` che porta il Work Package)
**Campo:** il solo impianto 1 (D-116).

Tutto quello che segue è misurato sulla stessa catena, con lo stesso ingresso, il
giorno stesso. Gli artefatti stanno in `baseline/` e `finale/`; lo strumento che
li misura è `metriche.py`, che non fa parte del nucleo deterministico ed è uno
strumento di sessione come lo script che rasterizza.

## 1. Le due cause chiuse

### 1.1 La tubazione che finisce sotto un simbolo (I-018, D-027)

**Causa tecnica.** «Linea sotto il simbolo» era misurata come **contenimento**:
un tratto valeva un rilievo solo se il riquadro di un simbolo lo conteneva per
intero. Da lì due buchi che si sommavano:

1. un tratto che **entra da un lato ed esce dall'altro** non è contenuto da
   nessuna parte, quindi passava per buono;
2. una spezzata con un capo sul riquadro era per di più **esente** dal controllo
   di distanza — è così che si riconosce un attacco — e poteva quindi
   attraversare il corpo indisturbata.

Bastava che un accessorio si sedesse dove un'altra tratta si attacca alla stessa
macchina. È esattamente ciò che succede avvicinando le valvole agli attacchi, ed
è il motivo per cui la regola del PO era ferma.

**Correzione.** Una misura sola, generale, senza eccezioni costruite
sull'esempio: un tratto è un rilievo quando percorre una lunghezza **dentro il
corpo** del riquadro, bordi esclusi. Il tratto che termina su un attacco non
entra — una porta sta sul perimetro del simbolo — quindi il caso ammesso dal
pacchetto non ha bisogno di nessuna deroga. La stessa funzione la leggono il
cancello di correttezza e chi posa gli accessori: devono dare la stessa
risposta, o si approva una tavola e se ne consegna un'altra.

### 1.2 Le valvole lontane dagli attacchi (I-018, D-120)

**Causa tecnica.** Lo stacco fra un accessorio e il componente all'estremo della
propria tratta era **una costante sola per tutti**, tarata sul caso peggiore —
serve una colonna libera per le tubazioni degli altri attacchi del pezzo. Non
distingueva la valvola che isola una macchina da un accessorio qualunque in
mezzo a una tratta, e abbassarla per tutti era già stato provato e ritirato
perché peggiorava i numeri di qualità.

**Correzione.** Chi isola si posa **sull'attacco di ciò che si manutiene**, a un
passo oltre la cella riservata davanti alla porta (D-113), che resta libera
perché è l'unica uscita di quell'attacco. Chi isola e cosa si manutiene lo dice
il **catalogo** — le funzioni dell'intercettazione e la proprietà
`maintainable`, la stessa che la regola dell'intercettazione legge per chiedere
quella valvola — mai il nome del pezzo. I tre casi della regola sono attuati
tutti: il primo accessorio contro l'estremo da cui la tratta parte, l'ultimo
contro quello a cui arriva (posato **all'indietro dal proprio attacco** invece
che lasciato a mezza strada), e la coppia in fila con un apparecchio che sta
esso stesso sulla tubazione.

### 1.3 Il foglio riempito e l'inchiostro distribuito (D-111, A1, A3)

Le due misure c'erano già nel controllo di qualità, ma nessuno le guardava
**mentre disponeva**: il collocatore le scopriva alla fine, come avviso. Il ciclo
che rivede la disposizione tira in una direzione sola — stringere — perché
pieghe, incroci e lunghezza si pagano tutti accorciando.

Dopo quel ciclo il collocatore ora **distende**: allontana dal centro i pezzi che
stanno sul bordo dell'ingombro e tiene la mossa solo se il foglio si riempie o
l'inchiostro si distribuisce meglio, e solo se non costa niente di ciò che viene
prima — nessuna piega in più, nessun incrocio in più, nessuna andata e ritorno in
più, nessuna tratta che perde i propri accessori. Cresce solo la **lunghezza**,
che è il prezzo dichiarato del riempimento.

⚠ **Una cosa vale la pena scriverla, perché è costata una prova sbagliata:**
riempire senza guardare la distribuzione non fa una tavola. Basta portare un
pezzo leggero in cima al foglio per far salire il riempimento — è un rettangolo
che si allunga — mentre l'inchiostro resta tutto in basso: alla prima prova il
riempimento saliva dal 29 al 63 % e lo squilibrio fra quadranti da 12 a 32. Un
numero migliore e una tavola peggiore. Le due misure vanno tenute insieme.

## 2. Le misure, prima e dopo

| Misura | Prima | Dopo | |
|---|---:|---:|---|
| Riempimento del foglio | 28,7 % | **41,8 %** | +13,1 punti |
| Rapporto fra quadrante più pieno e più vuoto | 12,6 | **2,74** | rientra nel limite di 3 |
| Incroci | 13 | **11** | |
| Pieghe totali | 33 | **25** | |
| Tratte con più di tre pieghe | 3 | **1** | |
| Lunghezza totale delle tubazioni | 1030 mm | 1150 mm | è il prezzo del riempimento |
| Tubazioni dentro il corpo di un simbolo | 0 | **0** | con la misura nuova, che vede anche l'attraversamento parziale |
| Valvole di isolamento a 2,5÷5 mm dal proprio attacco | 2 su 19 | **15 su 19** | i quattro casi residui al §4 |

Rilievi del controllo di qualità sulla tavola: da **1 bloccante + 6 avvisi** a
**1 bloccante + 3 avvisi**. Sparito l'avviso «il disegno è tutto su un lato»;
spariti due dei tre «tratta con troppe pieghe». Il bloccante è lo stesso di
prima ed è un difetto preesistente (§4.1).

Formato: A3, come prima. Area di disegno 350 × 235 mm.

## 3. Il grafo non è cambiato

Il modello tecnico dell'impianto 1 è lo stesso file in ingresso, prima e dopo
(`baseline/impianto1-completo.json`): nessuna modifica ha toccato interprete,
regole, assemblatore o catalogo. Il perimetro toccato è soltanto quello del
disegno e dei suoi controlli.

## 4. Difetti residui, dichiarati

### 4.1 L'andata e ritorno del ramo sanitario — **preesistente, non introdotto**

`RUN_OVERSHOOTS_ITS_PORT` sulla tratta `p4-a-a-1-1, p4-a-a-1-2`: la linea supera
la propria porta di arrivo e ci torna. C'era identico sulla baseline (37,5 mm) e
resta dopo (40 mm). Il ciclo di miglioramento lo conta fra le voci che non deve
peggiorare, ma non è riuscito a toglierlo né prima né dopo: è un difetto della
disposizione, non della distensione, e sta fuori dalle due cause di questo
pacchetto.

### 4.2 Quattro valvole su diciannove non arrivano al minimo

| Valvola | Distanza | Perché |
|---|---:|---|
| quella a valle del circolatore | 0 mm | i due riquadri si **toccano** invece di stare a un passo: il circolatore ha slittato lungo la tratta per scansare un ostacolo, e la coppia si è chiusa. Non è una sovrapposizione — quella è vietata e verificata — ma è più stretto di quanto la regola chieda |
| prelievo ACS, defangatore, ingresso freddo del bollitore | 7,5 mm | il nodo a 5 mm era occupato — dalla soglia di un altro attacco, da un simbolo o da una tratta già disegnata — e la posa è avanzata di un passo. È il «minimo **raggiungibile**» che la regola prevede |

### 4.3 Il riempimento resta sotto il 60 % dichiarato

41,8 % contro 60 %. Il limite è strutturale e va detto: le macchine appoggiano a
una linea di terra posta all'83 % dell'altezza dell'area, e sotto di essa nessun
simbolo può stare; sopra la corsia alta non c'è nulla da mettere. La distensione
riempie quello che può senza sfondare il limite di squilibrio, e si ferma lì.
Portare il riempimento al 60 % chiede una scelta di composizione — dove stanno le
macchine in altezza — che è del PO, non del disegnatore.

## 5. Verifiche eseguite

- suite completa, `ruff`, `mypy --strict` su `src`, `tests` ed `examples`;
- il caso di regressione di I-018 è scritto con le **sole funzioni che
  esistevano prima della correzione**: eseguito sulla revisione di base
  (`ebe165a`) fallisce su due prove, e sul ramo passa;
- due generazioni consecutive dello stesso ingresso danno la **stessa impronta**
  della geometria e lo stesso SVG, byte per byte;
- collaudo indipendente a contesto separato (D-083), verbale in coda a questo
  rapporto.

## 6. Artefatti

| File | Cosa |
|---|---|
| `baseline/impianto1.pdf` · `.png` · `.svg` | la tavola prima |
| `baseline/metriche.json` · `preflight.txt` · `geometria.json` | le misure prima |
| `finale/impianto1.pdf` · `.png` · `.svg` | la tavola dopo |
| `finale/metriche.json` · `preflight.txt` · `geometria.json` | le misure dopo |
| `prima-dopo.png` | il confronto affiancato |
| `metriche.py` | lo strumento che calcola le misure |
