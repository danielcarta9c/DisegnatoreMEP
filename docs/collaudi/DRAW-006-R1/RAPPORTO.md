# DRAW-006-R1 — ordine semantico, assi, adduzione ACS e riempimento

**Ramo:** `claude/draw-006-tavola2-semantica-v4n8o5` · **PR:** #24, aggiornata
**Base:** testa `9b925b7` di DRAW-006, integrata con l'ultima `main` (`a4b3430`)
**Campo:** l'**impianto 2** come unica consegna grafica; la tavola 1 come regressione
automatica; gli impianti 3–5 alla sola posa.

> **Una sola tavola è stata renderizzata come consegna: la tavola 2.** La tavola 1 non è
> stata riconsegnata — è verificata dalle prove — e gli impianti 3, 4 e 5 sono stati usati
> soltanto nelle prove di posa e nella logica dei domini di protezione, che non produce
> disegno.

**Il PDF della tavola 2:** `docs/collaudi/DRAW-006-R1/dopo/consegna/impianto2.pdf`
(A3, 420 × 297 mm, a misura reale). Accanto stanno il PNG, l'SVG, la geometria, le misure
e il preflight; in `dopo/` la stessa tavola in modalità verifica.

---

## 0. In una riga

I quattro difetti che il PM ha nominato sono corretti e provati da prove generali; il
grafo dell'impianto 2 ne esce **più piccolo e più giusto** — 45 pezzi → 41, il ritegno
sanitario duplicato sparisce, il vaso ignoto diventa una domanda, il riempimento diventa
un ponte vero fra due reti. **La geometria però peggiora**, e non l'ho recuperata: la
tavola 2 passa da 7 pieghe / 2 incroci / 670 mm a 12 / 8 / 785 mm sulla rete ordinaria, e
la tavola 1 esce dalle soglie del §A.5. È il punto aperto vero di questo pacchetto ed è
descritto per intero al §8, con le misure e con quello che ho provato.

---

## 1. Che cosa è cambiato nel grafo della tavola 2

| Tavola 2 | prima (`9b925b7`) | **dopo (DRAW-006-R1)** |
|---|---|---|
| Pezzi del modello / collegamenti | 45 / 47 | **41 / 44** |
| Integrazioni proposte / punti aperti | 29 / 0 | **26 / 1** |
| Ritegno sanitario separato sull'ingresso freddo | 1 | **0** (nel gruppo EN 1487) |
| Intercettazione separata sull'ingresso freddo | 1 | **0** (nel gruppo EN 1487) |
| Vaso di espansione sanitario | 1 pezzo posato | **1 domanda al progettista** |
| Attacchi del gruppo di riempimento | 1 (solo acqua tecnica) | **2: acqua fredda → circuito** |
| Manometro rispetto al riempimento | **prima** (contro la sua regola) | **dopo**, come la regola dichiara |
| Organi D-120 fuori dai 2,5÷5 mm | 1 su 16 | **1 su 15** |

Il punto aperto è quello che il §C.2 chiede: il catalogo del bollitore non dice se porta a
bordo il vaso sanitario, e un dato ignoto è una domanda, non un pezzo.

## 2. La geometria della tavola 2, prima e dopo

| Tavola 2 | prima (`9b925b7`) | **dopo** |
|---|---:|---:|
| Rete ordinaria — pieghe / incroci / lunghezza | 7 / 2 / 670,0 mm | **12 / 8 / 785,0 mm** |
| Stacchi — pieghe / incroci / lunghezza | 0 / 0 / 62,5 mm | **6 / 4 / 125,0 mm** |
| Tubo totale | 732,5 mm | **910,0 mm** |
| Backtracking · tubo sotto un simbolo | 0 · 0 | **0 · 0** |
| Tratte oltre tre pieghe — rete ordinaria · stacchi | 0 · 0 | **0 · 1**: lo stacco tecnico del riempimento, a quattro |
| Organi D-120 nei 2,5÷5 mm | 15 su 16 | **14 su 15** (uno a 7,5 mm) |
| Riempimento del foglio | 39,4 % | **41,4 %** |
| Impronta della geometria | `903c926b…` | `8249bab1…` |

Le due tavole non disegnano lo stesso grafo: quattro pezzi in meno e un ponte fra due reti
in più. Una parte dei millimetri viene dal contenuto — la derivazione dall'acquedotto al
ritorno tecnico è una tubazione nuova e lunga, che prima non c'era perché il gruppo di
riempimento pendeva da un tubo solo. Il resto viene dalla posa, ed è il §8.

---

## 3. A — l'ordine non dipende più dagli identificativi

Il difetto: il piede di uno stacco dichiarava i vincoli d'ordine del **primo organo** che
incontrava — la valvola bloccabile del vaso, il rubinetto del manometro — e quegli organi
di vincoli non ne hanno. Da lì in poi l'ordine del corredo di rete lo decideva l'ordine
alfabetico degli identificativi, e il manometro finiva prima del riempimento contro la
propria regola.

La correzione cammina lungo la derivazione **attraverso i raccordi e gli organi propri
dello stacco** e si ferma sul primo pezzo che non è né l'uno né l'altro: quello è il
soggetto semantico. Sulla tavola 2, camminando dalla pompa di calore verso l'impianto:
filtro, defangatore col suo organo per lato, vaso, **riempimento, manometro**.

L'altra metà del blocco è lo **spareggio**. Fra pezzi che nessun vincolo distingue serviva
un ordine, e quell'ordine era due volte sbagliato: alfabetico nel completamento — così
rinominare i pezzi cambiava l'impianto — e la posizione nel file nella posa, che però il
JSON canonico riordina per identificativo, cioè di nuovo per nome. Adesso è **strutturale**
(`src/disegnatore_mep/model/order.py`): il raffinamento dei colori sul grafo dei componenti
— voce di catalogo, e come si è attaccati al resto — e l'identificativo spareggia soltanto
fra pezzi che nessun dato dell'impianto distingue, che è ciò che il §A.2 ammette. Lo
leggono in tre: i membri di una rete nel completamento, l'ordine di posa, e l'ordine in cui
le tratte si instradano.

Le prove: `tests/rules/test_ordine_semantico.py`. Rinominare gli identificativi,
invertirne l'ordinamento e mescolare le connessioni non cambia né la fila dei mestieri né
il costo della tavola.

## 4. B — gli assi si cercano attraverso i pezzi

`Improver.linked_peers` non guarda più i soli capi diretti di una tratta: cammina
attraverso i raccordi, le catene di accessori in linea e i multivia — **uno stato ammesso
per volta**, letto dal catalogo. Sulla forma dell'impianto 2 questo apre la coppia
PDC–puffer attraverso la deviatrice, che prima non veniva nemmeno generata; e non apre
mai la coppia fra i due rami della deviatrice, perché `out_a ↔ out_b` non è un passaggio
in nessuno stato.

Da ogni coppia nascono le tre mosse del §B.2 — la mia colonna sull'asse della sua porta,
la sua sulla mia, l'asse comune a metà strada — e le coppie che chiedono **lo stesso
spostamento** si servono con una mossa sola: è l'allineamento simultaneo di mandata e
ritorno, che una candidata per coppia non avrebbe mai prodotto.

Le prove: `tests/layout/test_assi_per_stato_idraulico.py`.

## 5. C — l'adduzione fredda del bollitore

Un solo **gruppo composito EN 1487** (`dhw-safety-group`) sull'ingresso freddo, che
dichiara fra le proprie funzioni interne l'intercettazione e il ritegno controllabile.
Spariscono la valvola di sicurezza sanitaria isolata, il ritegno separato e
l'intercettazione esterna: erano i duplicati che il PM ha tolto.

La regola generale che lo rende possibile: **ciò che un gruppo si porta dentro conta sul
proprio tratto** — non sulla rete intera, che resta la decisione di DRAW-006, e non su ciò
che pende da uno stacco, che la corsa non attraversa. Un gruppo è un mantello attorno a
organi che stanno sulla tubazione; il bordo di una macchina no. E le regole che un gruppo
in linea può soddisfare parlano in **fase due**, così l'ordine alfabetico dei file delle
regole non decide chi vince.

Il **vaso sanitario** segue il dato di bordo nei tre casi: dichiarato assente si applica,
dichiarato presente non si aggiunge, ignoto si chiede. Nessuno **sfiato** automatico
compare sul bollitore. Lo **scarico** preferisce la porta dedicata quando il serbatoio la
dichiara — il volano — e ripiega sulla linea di riempimento soltanto quando non c'è, che è
il caso del bollitore sanitario: i cataloghi dei costruttori non gli danno una porta di
scarico, e lo si svuota da dove si riempie.

Le prove: `tests/rules/test_adduzione_acs.py`.

## 6. D — il riempimento è un ponte fra due reti

`filling-unit` acquista la seconda porta e il verso: `cold_water` in ingresso →
`heating_water` in uscita, con riduttore, filtro, intercettazione e ritegno dichiarati
**interni** (serie 553). Il catalogo sa risolvere un ponte (`bridging`/`bridge`), la regola
lo dichiara (`bridges_from_medium`), il motore cerca la **sorgente fredda già approvata**
dal progettista — il confine di rete da cui l'acqua esce — e chi applica apre una
derivazione da ciascuna parte. Dove l'acqua fredda non è dichiarata, il gruppo non si posa
appeso a nulla: esce un punto aperto.

Sulla tavola 2 il ponte c'è ed è uno solo: una presa sull'adduzione fredda dopo
l'intercettazione generale, il gruppo, e lo sbocco sul ritorno tecnico comune. Le due
derivazioni restano distinte da quella del bollitore, che è più a valle sulla stessa linea.

Le prove: `tests/rules/test_riempimento_tecnico.py`.

## 7. E — la vicinanza degli organi D-120

Il §E nomina **la valvola rimasta a 27,5 mm**: è
`valve-isolation-dirt-separator-pdc-water-return-a`, l'organo in coppia col defangatore.
Oggi sta a **2,5 mm**, e non ci sta per una costante: la proprietà è stata scritta come
relazione — *questo organo serve quel pezzo* — nel terzo caso di D-120, quello dei due
pezzi in fila in mezzo alla tubazione, e vale ovunque quella relazione esista.

Le prove sono generali e verdi: `test_l_organo_in_coppia_con_un_accessorio_gli_sta_stretto`
per il terzo caso, e `test_ogni_organo_della_tavola_2_sta_sul_pezzo_che_serve` per tutti
gli organi della tavola 2 senza fissare quanti siano — quel numero è della fixture, non
della regola.

**Il criterio 7 chiede però 16 su 16, e la misura di collaudo dice 14 su 15.** I due conti
non si contraddicono, misurano cose diverse, e la differenza va detta:

- gli organi governati da D-120 sulla tavola 2 sono passati da **16 a 15**, perché
  l'intercettazione separata sull'ingresso freddo è finita dentro il gruppo EN 1487 del §C:
  è un pezzo in meno, non un organo perso;
- `metriche.py` misura un **quarto caso** che i tre di D-120 non prevedono, «ultimo oltre
  il raccordo»: l'organo e il pezzo che serve con una diramazione in mezzo. In quel caso
  cade `valve-isolation-dhw-acquedotto-a`, l'intercettazione generale dell'acqua fredda,
  che sta a **7,5 mm dal bollitore invece dei 5,0 di prima** — un passo di griglia.
  La ragione è il ponte del §D: sulla stessa adduzione fredda c'è adesso **una seconda
  presa**, quella del riempimento, e l'organo si trova due raccordi più a monte del pezzo
  che serve invece di uno.

Non ho scritto un'eccezione per riportarla a 5,0: la traslazione gratuita del gruppo locale
è già nel ciclo ed è quella che ha chiuso i 27,5 mm del defangatore; su questa forma non
avvicina di più senza spostare l'ordine funzionale, che il §A dichiara duro. Se il PM vuole
il quarto caso dentro la regola — un organo può stare a 2,5÷5 mm anche da un pezzo che
raggiunge attraverso un raccordo — è un vincolo nuovo di posa, e lo dichiara lui.

La tavola 1, sulla stessa misura, è **15 su 15**.

Le prove: `tests/layout/test_vicinanza_valvole.py`.

## 8. Il punto aperto vero: la geometria non è stata recuperata

Il §A.3 chiede che l'ordine semantico sia un vincolo duro e che la geometria si recuperi
con traslazioni, movimenti di gruppo e nuovo routing. **L'ordine è un vincolo duro e lo
rispetta; la geometria non l'ho recuperata**, e questo è il rilievo che porto al PM invece
di allentare una soglia.

I numeri, misurati sulle due tavole:

| | alla testa `9b925b7` | criterio §A.5 / §E | **oggi** |
|---|---:|---:|---:|
| Tavola 1 — rete ordinaria, pieghe | 4 | ≤ 4 | **11** |
| Tavola 1 — rete ordinaria, incroci | 1 | ≤ 1 | **1** |
| Tavola 1 — rete ordinaria, lunghezza | 417,5 mm | ≤ 425 mm | **487,5 mm** |
| Tavola 1 — stacchi, pieghe / incroci / lunghezza | 0 / 0 / 40,0 mm | 0 / 0 / ≤ 45 mm | **6 / 0 / 125,0 mm** |
| Tavola 1 — backtracking · tubo sotto simbolo | 0 · 0 | 0 · 0 | **0 · 0** |
| Tavola 1 — organi D-120 nei 2,5÷5 mm | — | tutti | **15 su 15** |
| Tavola 2 — rete ordinaria, pieghe / incroci / lunghezza | 7 / 2 / 670,0 mm | — | **12 / 8 / 785,0 mm** |
| Tavola 2 — stacchi, pieghe / incroci / lunghezza | 0 / 0 / 62,5 mm | — | **6 / 4 / 125,0 mm** |
| Tavola 2 — organi D-120 nei 2,5÷5 mm | 15 su 16 | 16 su 16 | **14 su 15** |

I numeri della colonna «alla testa `9b925b7`» per la tavola 1 sono quelli dichiarati dalla
consegna di DRAW-006 sulla stessa PR; quelli della tavola 2 vengono da
`prima/metriche.json`, ricalcolati con lo strumento di oggi. La colonna «oggi» è misurata
con il codice di questo commit: la tavola 1 con la stessa catena della prova di
regressione, la tavola 2 da `dopo/consegna/metriche.json`. Il conto D-120 della tavola 1
non era agli atti alla testa `9b925b7`: la colonna «oggi» è l'unica misurata, ed è piena.

`test_la_tavola_1_non_costa_piu_di_draw_005_sulla_rete_ordinaria` **è rossa**, e l'ho
lasciata rossa: il Work Package dice che un'incompatibilità si porta al PM prima di
cambiare la prova, e questa è un'incompatibilità.

**Che cosa è successo, in ordine di peso.**

1. **Il ponte è una tubazione nuova e lunga.** Il gruppo di riempimento pendeva da un tubo
   solo; adesso ha un capo sull'acquedotto e uno sul ritorno tecnico, che su queste due
   tavole stanno lontani. Sono ~100 mm di tubo che il grafo di prima non aveva, più le
   pieghe per arrivarci. È contenuto, non posa: sparirebbe soltanto tornando al modello a
   una porta, che è ciò che il §D vieta.
2. **La misura degli «stacchi statici» non regge più il proprio nome.** Nel conteggio
   finiscono tutte le tratte che non sono rete ordinaria, quindi anche la linea di
   alimentazione del riempimento, che statica non è: il vocabolario del progetto la chiama
   `INBOUND`, cioè acqua che entra nel circuito. Con il ponte quella riga passa da 45 mm a
   125 mm senza che sia comparso un solo stacco statico in più. **Non ho toccato la
   misura**: se il PM conferma, separarla è una riga in `metriche.py` e una nella prova.
3. **Il ciclo di miglioramento si ferma in un ottimo locale peggiore.** Non è il tetto di
   prove: alzandolo da 1 500/2 000 a 6 000/6 000 la tavola 2 dà lo stesso identico
   risultato, e la tavola 1 pure. Il ciclo è greedy e la posa iniziale è cambiata sotto di
   lui — l'ordine strutturale, il ponte che non entra più nelle catene, il gruppo EN 1487
   che è largo il doppio di un accessorio in linea. Le candidate nuove del blocco B
   allineano, ma non bastano a riportarlo dove era.

**Che cosa ho provato e che cosa ho tenuto.** Ho provato a lasciare il ponte come colonna
propria della fascia (finiva a mezzo foglio dalle proprie prese), a farlo pendere dal capo
freddo invece che da quello tecnico (il ciclo non trovava più nessuna posa instradabile),
a togliere l'ordine strutturale dalla posa (tavola 2: 23 pieghe, 7 incroci, 892,5 mm —
peggio sulle pieghe, che vengono prima nel confronto), e ad alzare i tetti di ricerca
(nessuna differenza: alzandoli da 1 500/2 000 a 6 000/6 000 l'esito è identico). Ho tenuto
tre cose che pagano: il ponte pende dal capo su cui è montato e non prende una colonna
propria, il gruppo EN 1487 è largo il doppio e non alto il doppio — alto il doppio si
sedeva sugli attacchi del bollitore e la tavola non usciva affatto — e la **corsia della
catena di macchina è riservata a tutte le tratte**, non solo la soglia: senza, una tratta
altrui ci passava sopra e la catena falliva più tardi, con una diagnostica che parlava di
un'altra tratta.

Quello che resta da fare non è una rifinitura: è rimettere mano al ciclo di posa perché
sappia trattare un pezzo con due prese su due reti, e vale un pacchetto suo. Non l'ho
aperto da solo.

## 9. Verifiche

- **Suite completa** (`python -m pytest -q`, 35 min 39 s): **1373 verdi, 29 rosse, 22
  parcheggiate, 11 rosse apposta.** La suite **non è verde**, e questo è il secondo
  rilievo del pacchetto insieme a quello del §8. Nessuna prova è stata convertita in
  `skip` o in `xfail`; due `xfail` sono anzi state tolte perché il difetto che
  presidiavano è chiuso.
  Delle 29 rosse ne ho chiuse 16 dopo quella esecuzione, riportando la prova a dire il
  vero senza allentare nessun criterio (dettaglio al §9.1); **13 restano rosse** e non le
  ho verificate con una seconda esecuzione completa: il tempo del pacchetto è finito qui.
  Il conteggio 1373/29 è quindi l'ultima misura **integrale** e va riletto dal PM come
  tale.
- **`ruff check src tests examples docs/collaudi/DRAW-006-R1/metriche.py`**: nessun rilievo.
- **`mypy src tests examples`** con il profilo `strict` di `pyproject.toml`: nessun errore
  su 156 file.
- **Determinismo**: due esecuzioni consecutive dallo stesso ingresso danno il modello
  completato, la geometria e l'SVG **identici byte per byte**, e la stessa impronta.
- **Preflight della tavola 2 di consegna**: nessun rilievo bloccante; quattro avvisi —
  una tratta a quattro pieghe (lo stacco tecnico del riempimento), dodici incroci, foglio
  pieno al 41,4 %, disegno su un lato. I primi due sono il §8; gli ultimi due sono la
  composizione, che il perimetro esclude.
- **Impianti 3–5**: `tests/layout/test_posa_dei_cinque_impianti.py` pretende che tutti e
  cinque arrivino alla posa, senza `skip` e senza `try/except`. Nessun loro artefatto è
  stato prodotto.

### 9.1 Le rosse: quelle chiuse e quelle aperte

**Chiuse dopo l'ultima esecuzione integrale** (16):

- `tests/graph/test_plant_graph.py` (10) — il caso di posa congelato
  `examples/layout/centrale-pdc-quattro-fasce.json` nominava ancora
  `valve-safety-dhw`, la voce che il §C ha sostituito col gruppo EN 1487. Il catalogo
  rifiuta due pezzi con la stessa funzione sullo stesso fluido, quindi la voce **deve**
  sparire: la fixture è stata portata al gruppo in linea, e il raccordo che reggeva lo
  stacco con essa.
- `tests/graph/test_document.py` (2) — l'impianto essenziale un punto aperto ora ce l'ha
  davvero, il vaso sanitario del §C.2. Le due prove sono state stirate, non allentate:
  una sceglie il punto aperto di cui parla invece del primo che capita, l'altra pretende
  che **ogni** punto aperto trovato compaia nel documento sul proprio nodo, e prova il
  «nessuno» sul verso in cui davvero non ce n'è.
- `tests/graphics/test_bodies.py` (1) — l'inventario dei segni passa da 48 a 49: il
  gruppo EN 1487 è un segno nuovo.
- `tests/test_cli.py` (1) — stessa causa del documento. Il verso negativo si prova ora su
  una copia di lavoro del catalogo in cui l'accumulo **dichiara** di portare il vaso a
  bordo: il dato di un prodotto reale lo dichiara il PM, non la prova.
- `tests/layout/test_rami_di_servizio.py` (2) — il riempimento è un ponte e ha due capi.
  La prova distingue ora il capo che pesca dall'altra rete — l'ingresso di un pezzo che
  vive su due fluidi — e pretende, in più rispetto a prima, che il capo sul circuito
  **esista**; su quel capo la vecchia asserzione è intatta.

**Rimaste rosse** (13), tutte sulla geometria e tutte figlie del §8:

- `tests/layout/test_stacchi_minimi_e_interasse.py` (6), fra cui la regressione della
  tavola 1;
- `tests/acceptance/test_drawing.py` (2) — backtracking e pieghe/incroci della tavola 1;
- `tests/layout/test_catena_macchina.py` (2) — **non** è geometria: l'impianto di prova
  non dichiara nessuna rete di acqua fredda, e il ponte del §D senza sorgente apre un
  punto aperto, che la prova non si aspetta. Si chiude dichiarando l'allaccio all'acquedotto
  nella fixture, o accettando quel punto aperto: è una scelta di lettura, e non l'ho fatta
  da solo a fine pacchetto;
- `tests/layout/test_objective.py` (1) — le due zone dello stesso collettore non stanno
  più in colonna. Qui il ciclo **migliora**: 11 pieghe contro 12 e 437,5 mm contro 467,5,
  al prezzo di un nodo condiviso in più. La proprietà «rami paralleli impilati» non è nel
  costo, e il costo l'ha barattata. Metterla nel costo è una regola di posa nuova;
- `tests/layout/test_accessori_appesi.py` (1) e `tests/layout/test_zone_dei_pezzi_grossi.py`
  (1) — sulla tavola 2, la posa del §8.

## 10. Osservazioni per il PM, che non decido io

0. **La suite non è verde** (§9.1): 13 prove restano rosse, e nessuna di esse è stata
   ammorbidita per farla passare. Dodici sono la geometria del §8; una, quella delle
   catene di macchina, chiede una decisione di lettura sul ponte senza sorgente fredda.
1. **La geometria del §8.** È il rilievo principale e chiede una decisione: accettare la
   tavola 2 così com'è e aprire un pacchetto sulla posa del ponte, oppure rivedere il
   modello del riempimento. Non ho fatto nessuna delle due cose da solo.
2. **«Stacchi statici» misura anche ciò che statico non è** (§8.2). Separare la linea di
   alimentazione dalle derivazioni cieche è una riga di misura e una di prova; l'ho
   lasciata dov'era perché è una soglia del Work Package.
3. **Il quarto caso di D-120 non è nella regola** (§7). L'organo che raggiunge il proprio
   pezzo *attraverso un raccordo* non è uno dei tre casi che la decisione dichiara, ma la
   misura di collaudo lo conta: è così che nasce il 14 su 15. Metterlo nella regola è un
   vincolo di posa nuovo, e lo decide il PM.
4. **Il segno del gruppo EN 1487 è largo 10 mm e alto 5.** È il primo accessorio in linea
   che porta più di un organo, e la libreria non aveva una taglia per lui. L'ho aggiunta
   (`WIDE_INLINE_ACCESSORY`) invece di stringere il segno fino a renderlo illeggibile.
5. **La sorgente dell'acqua di riempimento è il confine di rete da cui l'acqua esce.** È
   la lettura più semplice di «sorgente AF già approvata»; se il PM intende qualcosa di
   più stretto — un attacco dichiarato dal progettista come punto di riempimento — è un
   campo del modello, non una regola.
6. **Il vaso sanitario resta una domanda su ogni impianto di prova**, perché nessun
   bollitore del catalogo dichiara il dato. Basta una riga `lacks_on_board` o
   `carries_on_board` per chiuderla, e quella riga la decide il PM.
7. **La variante del gruppo di riempimento con disconnettore non esiste in catalogo**, e
   il meccanismo che la sosterrebbe c'è ed è provato. Resta dov'era da DRAW-006.

## 11. Artefatti

| File | Cosa |
|---|---|
| `prima/impianto2-completo.json` · `prima/integrazioni.txt` · `prima/geometria.json` · `prima/metriche.json` · `prima/preflight.txt` · `prima/impianto2.{svg,pdf,png}` | la tavola 2 alla testa `9b925b7`, cioè lo stato che il PM ha respinto |
| `dopo/impianto2-completo.json` · `dopo/integrazioni.txt` | il modello completato di oggi, con le sue 26 integrazioni e il suo punto aperto |
| `dopo/impianto2.{pdf,png,svg}` · `dopo/geometria.json` · `dopo/metriche.json` · `dopo/preflight.txt` | la tavola in **modalità verifica**, con gli indirizzi dei nodi |
| `dopo/consegna/impianto2.{pdf,png,svg}` · `dopo/consegna/…` | **la tavola 2 di consegna**, con metriche, geometria e preflight |
| `metriche.py` | lo strumento di misura, quello di DRAW-006 |
