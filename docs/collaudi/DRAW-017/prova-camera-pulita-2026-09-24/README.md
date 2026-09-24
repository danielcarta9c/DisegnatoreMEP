# Il pianificatore sulla libreria di DRAW-017 — 24 settembre 2026

> ⏳ **Da guardare al PO**, accanto alle tavole approvate il 23 settembre
> ([`../../DRAW-016/prova-camera-pulita-2026-09-23/`](../../DRAW-016/prova-camera-pulita-2026-09-23/)).

**Che cos'è.** Le tavole dei cinque impianti ricomposte dopo tre disposizioni del PO che cambiano
la libreria e i grafi: la **miscelatrice termostatica** ha l'ingresso dell'acqua fredda ed è un
pezzo del piano (**D-175**); il **ricircolo** entra da un confine «ACS-R» e torna nell'accumulo,
verde chiaro (**D-176**); il **vaso sanitario** si posa dove l'ACS è centralizzata (**D-178**,
**D-179**). I grafi completi sono quelli che `rules --apply-all --out` scrive oggi; **i piani non
si correggono a mano** (D-155).

- **Impianti 1, 2, 3 e 5**: un agente per impianto — due sul 3, §«La misura» —, avviato da zero
  in una camera pulita, con
  soltanto `skill/comporre/ISTRUZIONI.md` e `CONSEGNA.md` (versione di `3b2eade`), il grafo
  completo, i manifesti dei simboli, il catalogo e il naming (servono al comando). Il mandato è
  quello del 23 settembre ([`mandato.md`](../../DRAW-016/prova-camera-pulita-2026-09-23/mandato.md)),
  con la cartella e la descrizione dell'impianto. Il motore degli agenti era congelato a
  `3b2eade`.
- **Impianto 4**: il suo grafo è **identico** a quello del 23 (non ha accumulo ACS né
  miscelatrice), e il piano è quello approvato, rieseguito sul motore di oggi. Non si è rifatta la
  prova: un piano approvato su un grafo che non è cambiato è già il risultato.

**Ogni agente dichiara i file che ha aperto: nessuno è uscito dalla propria cartella.** Un agente
(il 2) segnala che il `CLAUDE.md` del repository gli è arrivato nel contesto all'avvio, senza che
lo aprisse: lo carica l'ambiente per ogni agente. Parla del modo di lavorare, non del disegno.

**La misura è quella della sessione** (D-152), rieseguita con
[`../misura-tavole.py`](../misura-tavole.py) sul motore congelato, non quella che gli agenti
dichiarano.

## Le tavole

| impianto | tavola | piano | grafo |
|---|---|---|---|
| 1 | [`tavola-completo-1.pdf`](tavola-completo-1.pdf) | `piano-completo-1.json` | `grafo-completo-1.json` |
| 2 | [`tavola-completo-2.pdf`](tavola-completo-2.pdf) | `piano-completo-2.json` | `grafo-completo-2.json` |
| 3 | [`tavola-completo-3.pdf`](tavola-completo-3.pdf) | `piano-completo-3.json` (secondo tentativo) | `grafo-completo-3.json` |
| 4 | [`tavola-completo-4.pdf`](tavola-completo-4.pdf) | `piano-completo-4.json` (del 23) | `grafo-completo-4.json` |
| 5 | [`tavola-completo-5.pdf`](tavola-completo-5.pdf) | `piano-completo-5.json` | `grafo-completo-5.json` |
| 3, primo tentativo | [`tavola-completo-3-primo-tentativo.pdf`](tavola-completo-3-primo-tentativo.pdf) | `piano-completo-3-primo-tentativo.json` | `grafo-completo-3.json` |

Per rifarle: `disegnatore-mep piano grafo-completo-N.json --piano piano-completo-N.json
--catalog examples/layout/catalog --symbols assets/symbols --naming naming --out <cartella>`, e
`scripts/to-pdf.sh` sull'SVG.

## La misura, contro il metro del 23 settembre

| impianto | | **23 settembre** (approvata) | **24 settembre** |
|---|---|---|---|
| **1** — due PDC e accumulo combinato | formato · tratte | A3 · 21 | A3 · 23 |
| | cedute / bloccanti | 0 / 0 | 0 / 0 |
| | rilievi | 1 — B11 | 1 — B11 |
| | spezzate piegate / pieghe / incroci | 3 / 4 / 1 | 3 / 4 / 1 |
| **2** — PDC, deviatrice e ACS | formato · tratte | A3 · 23 | A3 · 25 |
| | cedute / bloccanti | 0 / 0 | 0 / 0 |
| | rilievi | 1 — B11 | 1 — B11 |
| | spezzate piegate / pieghe / incroci | 3 / 4 / 1 | **4 / 5** / 1 |
| **3** — PDC diretta su pavimento | formato · tratte | A3 · 22 | A3 · 24 |
| | cedute / bloccanti | 0 / 0 | 0 / 0 |
| | rilievi | 1 — A4 | 1 — A4 |
| | spezzate piegate / pieghe / incroci | 3 / 3 / 2 | 3 / 3 / 2 |
| **4** — ibrido PDC e caldaia | formato · tratte | A3 · 25 | A3 · 25 |
| | cedute / bloccanti | 0 / 0 | 0 / 0 |
| | rilievi | 2 — B11 ×2 | 2 — B11 ×2 |
| | spezzate piegate / pieghe / incroci | 5 / 6 / 2 | 5 / 6 / 2 |
| **5** — tre PDC in cascata | formato · tratte | A2 · 54 | A2 · 56 |
| | cedute / bloccanti | 0 / 0 | 0 / 0 |
| | rilievi | 3 — B1, B9, B11 | **1** — B11 |
| | spezzate piegate / pieghe / incroci | 10 / 13 / 5 | **8 / 9** / 5 |
| 3, primo tentativo | | | A3 · 24 · 0 / 0 · **2** — B1, A4 · 3 / **4** / 1 |

Il 23 settembre si misura rieseguendo i piani approvati sui grafi del 23 con il motore di
allora (`732fa70`): i piani del 23 non si eseguono sui grafi di oggi, perché la miscelatrice ha
cambiato porte.

- **1 e 4** sono uguali al metro.
- **5** migliora: l'anello del ricircolo non c'è più (D-176), e con lui se ne vanno i rilievi B1
  e B9 che portava.
- **2** ha una piega in più, e una spezzata piegata in più, **sulla tratta dal bollitore alla
  miscelatrice**: la miscelatrice, da pezzo del piano, sta in orizzontale a destra dell'uscita
  ACS, con AF-03 sotto, e l'uscita esce dal cielo del bollitore. Il 23 la colonna saliva dritta.
  L'agente lo dice imposto: sopra il bollitore pende lo scarico del volano. Sulla tavola 1 lo
  stesso gruppo sta in colonna, perché lì sopra c'è posto.
- **3, primo tentativo**: peggiora, e non per i pezzi nuovi. Le due zone del pavimento sono
  ruotate e sfalsate, e il ritorno della zona notte gira attorno all'altra (B1 su `p5`): il
  pettine della tavola approvata si è perso. **Si è rifatta la prova** con un agente nuovo, in una
  camera nuova, con lo stesso mandato e le stesse istruzioni, senza suggerimenti: il secondo
  tentativo ritrova il pettine, ed è **uguale al metro** — un rilievo, lo stesso del 23. **La
  tavola 3 di questa cartella è quella del secondo tentativo**; la prima resta agli atti col suo
  nome, perché la tavola che peggiora va mostrata anche lei. Due agenti sullo stesso grafo, con
  le stesse istruzioni, fanno due tavole diverse: **il pettine con un collettore di zona e un
  raccordo di ritorno le istruzioni non lo descrivono** (lo dicono tutti e due, §«Che cosa manca
  nelle istruzioni»).

**Le tratte crescono di due** dove c'è la miscelatrice: la tratta del suo ingresso AF, e la tratta
dell'acqua calda che la miscelatrice, da pezzo del piano, spezza in due. Sull'impianto 5 il
ricircolo cambia strada e non cambia il conto.

## I rilievi che restano, uno per uno

| impianto | rilievo | che cos'è |
|---|---|---|
| 1, 2 | B11 | il gradino di interasse fra il terminale (10) e la coppia che lo serve (15): noto, e le istruzioni dicono di non inseguirlo |
| 4 | B11 ×2 | come il 23: le due verticali distinte fra caldaia e volano, e il gradino del radiatore |
| 5 | B11 | il gradino di interasse UTA/volano, 10 contro 15 |
| 3 | A4 | lo sfiato del volano, 15 mm contro 10, come il 23: la mandata passa 10 mm sopra il tetto del volano, e con lo stacco minimo lo sfiato cadrebbe sulla mandata |

## Che cosa si vede guardando

- **1** — come il 23: le due pompe impilate, i collettori accanto, l'accumulo combinato al centro.
  **La colonna ACS sale dritta sopra l'accumulo**: valvola, miscelatrice, valvola, ACS-01; AF-03
  entra da sinistra nella terza via, azzurro tratteggiato. La miscelatrice è **ruotata di 90° e
  specchiata nel piano** dall'agente (D-168, D-169, D-175).
- **2** — il bollitore sta sotto il volano, più in alto del 23, e le discese della serpentina sono
  più corte; l'uscita ACS fa la L verso la miscelatrice. **Sul lato destro del bollitore c'è un
  moncone in più**: è l'attacco del ricircolo che D-176 dà a ogni accumulo ACS, tappato dove il
  ricircolo non c'è. Lo stesso sulla 3.
- **3** — come il 23: mandata e ritorno dritti dalla pompa al collettore di zona e al
  raccordo, il volano **specchiato** in serie sul ritorno, il corredo appeso sotto il ritorno, le
  due zone a **pettine** a destra del collettore. Il boiler sta sotto la pompa, e **la colonna ACS
  sale dritta** con la miscelatrice specchiata e girata di 90°; AF-03 entra da sinistra. Sul
  lato destro del boiler due monconi: la sonda e l'attacco del ricircolo, tappato.
- **4** — identica al 23.
- **5** — si legge: cascata impilata con i due collettori, primario dritto fino al volano,
  deviatrice con la terza via che scende al bollitore, pettine a destra con la UTA in linea. **Il
  ricircolo è verde chiaro**, entra dall'«ACS-R», passa per circolatore e ritegno e torna nel
  bollitore sul lato destro; in legenda ha la sua riga, «Acqua calda sanitaria — ricircolo». **Il
  vaso sanitario** pende fra il gruppo di sicurezza sanitario e il bollitore.

## Che cosa gli agenti hanno visto, e i numeri no

Il metro del progetto: se una tavola sembra sbagliata e i numeri dicono che va bene, si scrive.

- **La ritegno del ricircolo punta contro il flusso** (5) — *visto dalla sessione*. L'acqua va
  dall'ACS-R al bollitore, da destra a sinistra, e la freccia del simbolo punta a destra. Nel
  catalogo la ritegno sull'acqua calda (`valve-check-dhw-hot`) ha i due attacchi senza verso, e
  il motore non sa girarla sul flusso: è una delle piccole correzioni candidate del pacchetto,
  che non si fanno senza che il PO le chieda (I-112).
- **Sfiato e scarico escono rossi** anche quando il pezzo sta sul ritorno (1, 2, 3 e il secondo
  tentativo sul 3 — quattro agenti su cinque, e sulla 3 il volano è in serie sul ritorno). Era
  così anche il 23.
- **Il motore mette in fila gli organi in linea da un capo della tratta che il piano non
  sceglie** (2, 3, 5): il gruppo di sicurezza sanitario lontano dal bollitore che protegge, la
  valvola d'uscita del bollitore accanto alla miscelatrice, la valvola della pompa attaccata al
  collettore, la seconda valvola del separatore d'aria 70 mm più in là della prima.
- **Uno scarico dell'acqua fredda che sembrava la continuazione storta di un ritorno** (2): cadeva
  a 2,5 mm dalla fine della verticale. Nessun rilievo lo coglie; l'agente l'ha spostato di una
  corsia.
- **La freccia di verso sul ponticello di un sormonto** (1) e **la sigla VOL-01 accanto a una
  valvola** (2): già fra le candidate. Sulla 1 l'agente ha allontanato i collettori di 5 mm per
  togliere la freccia dal ponticello.
- **L'elenco «Girati dalla deduzione» non dice tutto** (1, 3): i raccordi del vaso e del
  riempimento escono girati di 180° dalla posa di partenza, non dalla deduzione, e non compaiono.
- **Sulla 3 la discesa della seconda uscita del collettore è lunga 2,5 mm**, e la linea sembra
  uscire di lato dal collettore; **ACS-01 punta in su, verso la pompa di calore** (3, secondo
  tentativo).
- **`scripts/rasterize.sh` taglia il fondo del foglio** (1, 2, 3, 5): nel PNG mancano il bordo
  inferiore e il cartiglio. **I PDF sono interi** — la sessione li ha guardati resi pagina per
  pagina.

## Le domande che gli agenti hanno scritto per il progettista

Non sono del pianificatore e non si risolvono qui: vanno al PO.

- **Lo scarico del bollitore sta sull'acqua fredda a monte del gruppo di sicurezza**, che porta
  dentro il ritegno: da quello scarico il bollitore si svuota davvero? (2 — e la fila è la stessa
  sul 3 e sul 5, ed era la stessa nei grafi approvati il 23.)
- **Il ritorno delle zone del pavimento è un raccordo a T**, non un collettore di ritorno: è
  voluto? Un collettore darebbe al pettine la sua seconda colonna. (3)
- **Sulle mandate della cascata non ci sono ritegni**: è voluto? (5)
- **Il circuito miscelato del radiante**: dove sta il raccordo del bypass? Sotto la miscelatrice
  lo accusa `PARALLEL_MACHINES_WITHOUT_A_COLLECTOR`; sulla colonna di ritorno alla stessa quota
  le colonne devono stare a 25 mm, contro B12 e B9. (5)
- *Risposta già data:* un agente chiede perché AF-03 non prenda l'acqua dall'acquedotto AF-01
  (5). È **I-061**: «si fanno più ingressi», uno per utente dell'acqua fredda.

## Che cosa manca nelle istruzioni, secondo gli agenti

Sono il lavoro della prossima revisione di `skill/comporre/ISTRUZIONI.md`; qui si elencano.

- **Il rettilineo per gli organi in linea è sottostimato** (1, 5): «con due organi 20–25 mm» non
  basta — defangatore e valvola ne vogliono 30, valvola-circolatore-valvola 40.
- **La tabella del §2.1 ha buchi**: sfiato e scarico dell'accumulo combinato (1), la quota di
  `dhw_out` del bollitore (2); e non dice che gli attacchi non usati — sonda, ricircolo — si
  disegnano lo stesso come monconi (2).
- **B3 si può scrivere come esito**: in tutti e tre i casi misurati vince la mandata vicina alle
  macchine (1, 2, 5).
- **Da quale capo della tratta il motore allinea gli organi in linea**, e che il piano non ha
  una leva per sceglierlo (2, 3, 5): il §4bis dice che si posano «dalla porta del pezzo che
  isolano», e su una tratta lunga non è così.
- **Il pettine con un collettore di zona orizzontale e un raccordo di ritorno** non è descritto
  (3, tutti e due i tentativi): il secondo agente l'ha trovato — la zona dell'uscita più a destra
  in cima, alla quota del ritorno, il raccordo a sinistra delle discese, un incrocio imposto —, il
  primo no. È la ragione per cui i due tentativi sul 3 sono tavole diverse. Lo stesso per la
  testa del pettine quando la prima utenza non è in linea (5) e per il posto del circolatore
  delle utenze (5).
- **I sormonti imposti non elencati**: lo sfiato di un volano a due attacchi in serie sul
  ritorno scavalca la mandata, e il suo rilievo A4 non si cura (3); lo specchio del volano sul
  ritorno che corre da destra a sinistra va detto (3).
- **Dove va un sottosistema indipendente** — l'acqua calda di un boiler separato — che divide la
  fascia della generazione (3).
- **I terminali ruotati**: la deduzione non gira un pannello radiante, e le istruzioni non dicono
  dove finiscono le porte dopo la rotazione (3).
- **Gli stacchi minimi**: `SERVICE_STUB_LONGER_THAN_ITS_MINIMUM` non parla per i confini di rete
  (1), e sullo sfiato di un volano in serie sul ritorno il minimo non si può rispettare senza un
  sormonto (3).
- **Il formato**: la legenda da sola esclude l'A3 sul 5 (5); il messaggio del formato troppo
  piccolo suggerisce di dividere l'impianto, le istruzioni di prendere il foglio successivo (1).
- **Piccole cose**: i percorsi della camera (`simboli/`, `catalogo/`) non sono quelli che le
  istruzioni citano (1, 3); il comando non stampa il numero delle tratte, che `CONSEGNA.md` chiede
  di riferire (2, 5); la sezione «Avvisi» non è nominata (3).
