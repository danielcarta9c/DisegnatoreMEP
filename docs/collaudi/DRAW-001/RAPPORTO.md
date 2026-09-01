# DRAW-001 — la tavola dell'impianto 1, prima e dopo

**Ramo:** `claude/draw-001-tavola1-qualita`
**Base:** `ebe165a5d0651d108c78833f1275d1327a96d59c` (il `main` che porta il Work Package)
**Campo:** il solo impianto 1 (D-116).

Tutto quello che segue è misurato sulla stessa catena, con lo stesso ingresso, il
giorno stesso. Gli artefatti stanno in `baseline/` e `finale/`; lo strumento che
li misura è `metriche.py`, che non fa parte del nucleo deterministico ed è uno
strumento di sessione come lo script che rasterizza.

> **Questa è la seconda stesura.** La prima è stata **respinta** dal collaudo
> indipendente (`COLLAUDO.md`) su sei punti, e i sei sono corretti qui: quattro
> nel codice, due nel modo di dichiarare i numeri. Dove il collaudo ha misurato
> qualcosa che questo rapporto affermava senza prova, vince la sua misura.

## 1. Le tre cause chiuse

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

**Correzione.** La misura dell'attraversamento — un tratto che percorre una
lunghezza **dentro il corpo** del riquadro, bordi esclusi — **si aggiunge** a
quella storica del contenimento, non la sostituisce.

⚠ **Questo punto è cambiato dopo il collaudo, e va detto.** Nella prima stesura
la misura nuova *sostituiva* la vecchia, e ne perdeva un caso: il tratto che
corre **a filo del fianco** di un simbolo, che il contenimento prendeva e che
l'attraversamento per costruzione non prende. Sulla tavola consegnata allora
c'erano sei tratti a filo di un simbolo (baseline: zero), due dei quali il
cancello della revisione di base avrebbe bloccato, e su uno di essi la punta di
freccia del flusso finiva disegnata sopra il simbolo. Restringere una convenzione
di rappresentazione **non è del disegnatore** (D-124): le due misure ora si usano
insieme, e la tavola finale non ha nessuno dei due difetti.

Il tratto che termina su un attacco resta ammesso per costruzione — una porta sta
sul perimetro — quindi il caso ammesso dal pacchetto non ha bisogno di deroghe.
La stessa funzione la leggono il cancello di correttezza, chi posa gli accessori
e lo strumento che misura: devono dare la stessa risposta, o si approva una
tavola e se ne consegna un'altra.

Ne discende una terza correzione, trovata mentre si chiudeva la prima: **la
propria tratta non deve rientrare nel riquadro del proprio accessorio**. Il
taglio toglie il pezzo di linea che passa *per* il simbolo, ma una spezzata che
piega lì accanto può rientrare da un altro lato, e allora la linea è disegnata
sotto il simbolo come se non fosse stata interrotta. Si guarda dopo il taglio,
con la stessa misura del cancello.

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
il **catalogo** — le funzioni dell'intercettazione, quella comune e quella
bloccabile aperta, e la proprietà `maintainable` — mai il nome del pezzo. I tre
casi della regola sono attuati tutti: il primo accessorio contro l'estremo da cui
la tratta parte, l'ultimo contro quello a cui arriva (posato **all'indietro dal
proprio attacco** invece che lasciato a mezza strada), e la coppia in fila con un
apparecchio che sta esso stesso sulla tubazione.

⚠ **Corretto dopo il collaudo:** lo stacco fra due accessori si misura ora sul
**riquadro** da tutt'e due i lati, non solo da quello di coda. Un simbolo più
largo del proprio taglio sporge oltre di esso, e con la coppia di D-120 — che
rinuncia al proprio passo di testa — la valvola e il circolatore arrivavano a
**toccarsi**, proprio sul caso che il PO ha nominato per nome.

### 1.3 Il foglio riempito e l'inchiostro distribuito (D-111, A1, A3)

Le due misure c'erano già nel controllo di qualità, ma nessuno le guardava
**mentre disponeva**: il collocatore le scopriva alla fine, come avviso. Il ciclo
che rivede la disposizione tira in una direzione sola — stringere — perché
pieghe, incroci e lunghezza si pagano tutti accorciando.

Dopo quel ciclo il collocatore ora **distende**: allontana dal centro i pezzi che
stanno sul bordo dell'ingombro e tiene la mossa solo se il foglio si riempie o
l'inchiostro si distribuisce meglio, e solo se non costa niente di ciò che viene
prima — nessuna piega in più, nessun incrocio in più, nessuna tratta in più oltre
le tre pieghe, nessuna andata e ritorno in più, nessuna tratta che perde i propri
accessori. Cresce solo la **lunghezza**, che è il prezzo dichiarato del
riempimento.

⚠ **Riempire senza guardare la distribuzione non fa una tavola, e la prima
stesura c'è cascata.** Basta portare un pezzo leggero lontano da tutti per
allungare il rettangolo che il riempimento misura: nella tavola respinta, dei
tredici punti guadagnati **nove venivano da una sola valvola di sicurezza**
spinta ventisette millimetri sopra il resto dell'inchiostro. Ora una seconda
misura lo impedisce: oltre allo squilibrio fra i quadranti dell'**area**, che
dice se la tavola sta da un lato, si guarda quello fra i quadranti del **proprio
ingombro**, che è dove una propaggine si vede subito — il quadrante che si
allunga resta vuoto.

## 2. Le misure, prima e dopo

Entrambe le colonne sono calcolate **con lo strumento di oggi**: la baseline è
stata rimisurata leggendo la geometria agli atti, così che le due colonne usino
la stessa definizione di ogni voce.

| Misura | Prima | Dopo | |
|---|---:|---:|---|
| Riempimento del foglio | 28,7 % | **41,8 %** | +13,1 punti |
| Rapporto fra quadrante più pieno e più vuoto | 12,6 | **2,87** | rientra nel limite di 3 |
| Incroci | 13 | **12** | |
| Pieghe totali | 33 | **29** | |
| Tratte con più di tre pieghe | 3 | **2** | |
| Lunghezza totale delle tubazioni | 1030 mm | 1182,5 mm | è il prezzo del riempimento |
| Tubazioni dentro il corpo di un simbolo | 0 | **0** | misura completa: attraversamento **e** filo del bordo, nessuna esenzione |
| Valvole di isolamento a 2,5÷5 mm dal proprio attacco | 6 su 20 | **16 su 20** | i quattro casi residui al §4.2 |

Rilievi del controllo di qualità sulla tavola: da **1 bloccante + 6 avvisi** a
**1 bloccante + 4 avvisi**. Sparito l'avviso «il disegno è tutto su un lato»;
spariti uno dei tre «tratta con troppe pieghe» e la metà degli incroci di troppo.
Il bloccante è lo stesso di prima, **con lo stesso numero** (§4.1).

Formato: A3, come prima. Area di disegno 350 × 235 mm.

## 3. Il grafo non è cambiato

Il modello tecnico dell'impianto 1 è lo stesso file in ingresso, prima e dopo
(`baseline/impianto1-completo.json`): nessuna modifica ha toccato interprete,
regole, assemblatore o catalogo. Il perimetro toccato è soltanto quello del
disegno e dei suoi controlli. Il collaudo ha rigenerato il modello canonico su
entrambe le revisioni e ha verificato lo stesso `sha256`.

## 4. Difetti residui, dichiarati

### 4.1 L'andata e ritorno del ramo sanitario — **preesistente, e identica**

`RUN_OVERSHOOTS_ITS_PORT` sulla tratta `p4-a-a-1-1, p4-a-a-1-2`: la linea supera
la propria porta di arrivo e ci torna. C'è sulla baseline e c'è dopo, **con lo
stesso numero: 37,5 mm**. Il ciclo di miglioramento la conta fra le voci che non
deve peggiorare, ma non riesce a toglierla né prima né dopo: è un difetto della
disposizione e sta fuori dalle due cause di questo pacchetto.

*Nella prima stesura questa tratta arrivava a 40 mm e il rapporto la dichiarava
«identica»: due numeri diversi presentati come uno. Il collaudo l'ha rilevato; la
seconda stesura del ciclo la riporta a 37,5 mm, e il numero è verificabile nel
preflight agli atti.*

### 4.2 Quattro valvole su venti non arrivano al minimo

| Valvola | Distanza | Perché |
|---|---:|---:|
| prelievo ACS | 13,5 mm | la coppia con la miscelatrice non si stringe: fra le due la posa non trova un nodo libero più vicino |
| valvola del manometro | 12,5 mm | idem, sul collettore di ritorno |
| defangatore, ingresso freddo del bollitore | 7,5 mm | il nodo a 5 mm era occupato — dalla soglia di un altro attacco, da un simbolo o da una tratta già disegnata — e la posa è arretrata di un passo |

È il «minimo **raggiungibile**» che la regola prevede: la cella davanti a un
attacco resta libera perché è la sua unica uscita (D-113), e chi non trova posto
al primo nodo si sposta di un passo. Sulla baseline le valvole entro forbice
erano **6 su 20**.

### 4.3 Il riempimento resta sotto il 60 % dichiarato

41,8 % contro 60 %. Il limite è strutturale e va detto: le macchine appoggiano a
una linea di terra posta all'83 % dell'altezza dell'area, e sotto di essa nessun
simbolo può stare; sopra la corsia alta non c'è nulla da mettere. La distensione
riempie quello che può senza sfondare i due limiti di distribuzione, e si ferma
lì. Portare il riempimento al 60 % chiede una scelta di composizione — dove
stanno le macchine in altezza — che è del PO, non del disegnatore.

### 4.4 L'esenzione di distanza per «capo sul riquadro» resta aperta

Il collaudo l'ha censita e ha ragione: una spezzata con un capo sul riquadro è
ancora esente **per intero** dal controllo della distanza di rispetto (B5), non
solo per il proprio tratto terminale. Questo pacchetto ha chiuso la metà D-027
del buco — l'attraversamento — e lascia aperta la metà B5. Non è una regressione
(è lo stesso comportamento della baseline: 94 casi prima, 95 dopo), ma è la
seconda metà della stessa causa, e va scritta perché non si perda.

## 5. Verifiche eseguite

- **Suite completa**, `ruff`, `mypy --strict` su `src`, `tests` ed `examples`.
  ⚠ Sul primo commit consegnato la suite **era rossa**, e il collaudo l'ha
  trovata: la prova di guardia `test_tornano_a_comporre_quando_la_composizione_compatta`
  è marcata `xfail(strict)` e ha cominciato a **passare**, perché il terzo
  impianto — che chiedeva 420 mm contro i 335 di una A3 — da quando il
  collocatore distende ci rientra. È un guadagno collaterale, non un difetto:
  la prova è stata rimessa in piedi spostando quel piano in un elenco proprio,
  con una prova che verifica soltanto che **compone**. La sua qualità non si
  guarda: le altre quattro tavole si guardano dopo che il PO ha approvato la
  prima (D-116).
- Il **caso di regressione di I-018** è scritto con le sole funzioni che
  esistevano prima della correzione: eseguito sulla revisione di base
  (`ebe165a`) fallisce su due prove, e sul ramo passa.
- **Due generazioni consecutive** dello stesso ingresso danno la stessa impronta
  della geometria e lo stesso SVG, byte per byte; il collaudo ne ha fatte tre.
- **Collaudo indipendente a contesto separato** (D-083): verbale in
  `COLLAUDO.md`. Il primo giro è stato **RESPINTO**; questa consegna risponde a
  tutti e sei i punti.

## 6. Artefatti

| File | Cosa |
|---|---|
| `baseline/impianto1.pdf` · `.png` · `.svg` | la tavola prima |
| `baseline/metriche.json` · `preflight.txt` · `geometria.json` | le misure prima |
| `finale/impianto1.pdf` · `.png` · `.svg` | la tavola dopo |
| `finale/metriche.json` · `preflight.txt` · `geometria.json` | le misure dopo |
| `prima-dopo.png` | il confronto affiancato |
| `metriche.py` | lo strumento che calcola le misure |
| `COLLAUDO.md` | il verbale del collaudo indipendente, primo giro |
