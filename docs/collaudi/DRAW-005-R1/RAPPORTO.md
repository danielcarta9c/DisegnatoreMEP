# DRAW-005-R1 — rifinitura della tavola 1

**Ramo:** `claude/draw-005-r1-rifiniture-tavola1-3aad42` (la sessione ha assegnato il
suffisso; il Work Package nomina il ramo senza suffisso — vedi §8)
**Base:** `cc7ff93` — il `main` che porta il Work Package DRAW-005-R1
**Campo:** il solo impianto 1 e i contratti generali necessari; gli impianti 2–5 non sono
stati lavorati

Tutto ciò che segue è misurato sulla stessa catena, con lo stesso ingresso
(`examples/prova/prova-1-due-pdc-accumulo-combinato.json`), il giorno stesso. Gli
artefatti stanno in `prima/` — la tavola di consegna di DRAW-005, con il suo modello
completato, rimisurata con lo strumento di oggi — e in `dopo/`; lo strumento è
`metriche.py`, che legge la geometria agli atti e non la ricompone, e da questo pacchetto
misura anche le sicurezze, gli stacchi, le catene e i pesi del tratto. Le decisioni
attuate sono quelle del Work Package e della traduzione PM
(`docs/pm/2026-09-08-rilievi-po-draw005-r1.md`); gli allegati del PO non sono stati usati
per ricavare requisiti.

## 1. Che cosa è cambiato, e perché

### 1.1 Blocco A — la sicurezza per generatore è un dato di catalogo (I-043)

- **La regola** `safety-relief-where-heat-enters-the-water` passa alla 4.0.0: vale in
  ogni regime (prima solo sopra i 35 kW) su ogni pezzo con funzione `heat_generation`,
  sulla mandata, attaccata alla macchina (`against_the_anchor`) e prima di qualunque
  organo che chiuda; si riconosce soddisfatta solo **sull'attacco** che protegge. La
  presenza a bordo resta ciò che era: il `carries_on_board` del catalogo, che per la
  pompa di calore generica dichiara solo `circulation`. Non c'è più nessuna assunzione
  implicita: chi non dichiara la sicurezza la riceve esterna, chi la dichiara non riceve
  il doppione. Fonti nel campo `source` della regola: SRC-027, SRC-019 p. 15, SRC-028,
  SRC-012 sopra i 35 kW.
- **La regola del serbatoio** `safety-relief-on-the-stored-volume` passa alla 2.0.0: si
  riconosce soddisfatta solo sull'attacco (era `on_the_network`), perché la sicurezza di
  un generatore protegge un altro volume e non la sostituisce, né ne è sostituita.
- **Il motore** (`rules/engine.py`): la deduplicazione «un pezzo per tratto» non si
  applica alle regole `against_the_anchor`, altrimenti la sicurezza del serbatoio
  cancellava quella del generatore sullo stesso tratto (con una macchina sola, serbatoio e
  generatore stanno sullo stesso tubo). Il contesto (`rules/context.py`) legge anche le
  funzioni che **pendono** da un raccordo passante (`hanging_functions`): così la
  sicurezza sul suo raccordo si vede dall'attacco della macchina, e rieseguire le regole
  sul modello completato non propone nulla.
- **Lo sfogo aria** non è stato toccato: resta sull'attacco alto dell'accumulo, uno solo,
  e nessuno per PDC (§6, prove).
- **Un vincolo aggiunto, da registrare (§8):** la regola del generatore vale sul medium
  `heating_water`. Senza, la pompa di calore sanitaria dell'impianto 3 riceveva una
  sicurezza sulla rete dell'acqua calda sanitaria, che era un punto aperto falso.

### 1.2 Blocco B — specie del flusso, colore e frecce dei rami di servizio (I-042)

- **Il modello di geometria** (`layout/geometry.py`) acquista `FlowKind`
  (`ordinary`, `static`, `inbound`, `outbound`) e `flow_from_start` su ogni tratta
  instradata; una geometria agli atti senza i campi nuovi si rilegge come flusso
  ordinario.
- **La classificazione** (`layout/flow.py`, `classify_trunks`) legge il grafo, mai la
  spezzata: uno stacco prende la specie dalle **funzioni** di ciò che regge — `filling`
  entra (`inbound`, freccia verso il circuito), `drain` esce (`outbound`, freccia verso
  fuori), tutto il resto che pende da uno stacco è statico (manometro, vaso, sfogo,
  sicurezza: nessuna freccia); il servizio (andata/ritorno, quindi il colore) è quello
  della tratta ospite, ereditato attraverso il raccordo. Per le tratte ordinarie la
  classificazione è allineata al verso del flusso e parte da tutte le sorgenti: con due
  macchine in parallelo nessuna tratta del primario resta indecisa (prima la seconda PDC
  aveva il ritorno in colore di andata).
- **Il renderer** (`graphics/sheet.py`) disegna la freccia secondo la specie: nessuna sui
  rami statici, invertita dove il flusso va verso il capo di partenza; non conosce né
  colori scritti a mano né nomi di pezzi (provato).
- **`P` resta un manometro:** `pressure-gauge`, funzione `pressure_measurement`; nessuna
  rinomina.

### 1.3 Blocco C — filtro a Y, peso del tratto, serpentina (I-041, I-045)

- **Il manifesto** (`graphics/symbol.py`) acquista `stroke_weight` (`thin`, `medium`,
  `thick`, sottinteso `medium`), validato e conservato dalla rotazione; lo standard
  (`graphics/standard.py`) è l'unica traduzione in millimetri: `thick` = 0,50 mm. La
  tavola disegna ogni gruppo di simbolo con il proprio peso; la legenda alleggerisce i
  simboli ordinari a `thin` come faceva e **conserva `thick`** per chi lo dichiara; il
  foglio di riscontro (`graphics/svg.py`) usa il peso dichiarato. Nessun renderer conosce
  l'identificativo del filtro (provato con `grep` sul sorgente).
- **Il filtro a Y** (`strainer` 3.0.0) ha le due barrette terminali perpendicolari
  all'asse e dichiara `thick`.
- **L'accumulo combinato** (`buffer-combined` 3.0.0) ha la serpentina continua da
  `cold_in` a `dhw_out`, con ogni cambio di direzione ad arco (`A` nel tracciato),
  centrata nel mantello; porte, riquadro, attacchi e grafo non cambiano (provato
  confrontando il manifesto).
- Tutto passa da `examples/graphics/build_symbols.py`; i 39 manifesti sono rigenerati
  (tutti portano ora `stroke_weight`) e la prova di rigenerazione li confronta.

### 1.4 Blocco D — la catena della macchina (I-044)

- **Il contratto** vive in `layout/chains.py`: dalla porta di un pezzo che si manutiene
  (`maintainable`, non raccordo), i pezzi in linea fino al primo organo di chiusura
  compreso — letto dal catalogo, mai dal nome — si posano a **stazioni fisse** dalla
  porta: la soglia dell'attacco più un passo (5 mm, lo stesso che D-120 dava alla
  valvola che isola), poi un passo fra un pezzo e l'altro; sul **primo rettilineo** dalla
  porta, prima della prima curva. Una posa che non lo rispetta non è una candidata
  (`LayoutError`), non una posa peggiore.
- **La posa** (`layout/inline.py`): le catene di testa e di coda si siedono per prime
  alle loro stazioni; il resto della fila avanza dal cursore come prima. Oltre un
  raccordo passante l'organo si stringe al raccordo scorrendo (I-035, contratto morbido
  com'era). Un organo solo fra due manutenibili (I-034) appartiene al capo che porta anche
  i pezzi propri, a pari titolo al capo di arrivo.
- **L'instradatore** (`layout/route.py`) riceve da ogni capo il rettilineo che la catena
  occuperà (`chain_room_mm`) e lo **impone**: le prime celle dalla porta sono forzate
  dritte, e una curva prima di esse costa come una curva in più. È il pezzo che manca
  perché il contratto sia soddisfacibile: senza, la spezzata piegava sulla soglia e la
  catena non stava sul primo rettilineo.
- **La posa dei simboli** (`layout/place.py`) riserva davanti a ogni porta di macchina un
  **corridoio** lungo quanto la catena più due passi, che nessun simbolo occupa; lega le
  macchine in parallelo attraverso i raccordi passanti (`neighbours_beyond_fittings`,
  anche in `improve.py`), così che le due PDC con il proprio raccordo di sicurezza
  restino impilate; e ordina una catena biforcata per livello di distanza dall'ancora,
  così che due rami paralleli abbiano la stessa ascissa. Nessuna coordinata, nessun
  identificativo.
- **Un difetto trovato in collaudo e corretto:** dopo una catena di testa, il pezzo che
  segue e fa coppia con l'organo (D-120: circolatore dopo la valvola dell'accumulo,
  miscelatrice dopo la valvola sanitaria) ripartiva dal riquadro senza il passo e lo
  toccava. Il cursore riparte dal riquadro più il passo, com'è per ogni pezzo posato;
  prova generale aggiunta (`test_chi_segue_la_catena_di_testa_le_sta_a_un_passo_e_non_la_tocca`).

### 1.5 Conseguenze meccaniche sui documenti derivati

`examples/rules/centrale-pdc-completa.json`, `docs/prodotto/GRAFO_IMPIANTO.md` e i
grafi di prova 1–4 sono rigenerati dalle prove (una sicurezza per macchina, con il suo
raccordo); `CONFRONTO-2026-08-07.md` porta la nota datata e i conteggi di oggi
(43/48/46/47/98); `REGOLE_ACCESSORI.md` (introduzione, schede 1 e 2) e la riga della
sicurezza in `docs/SKILL.md` dicono il minimo che la regola nuova rendeva falso.

## 2. Il grafo dell'impianto 1 (criteri 1, 2)

Le regole propongono **28 integrazioni** (erano 26): le due in più sono le sicurezze su
`pdc-master.water_supply` e `pdc-slave.water_supply`, ciascuna sul proprio raccordo,
attaccata alla macchina e **prima** della valvola di mandata; la sicurezza dell'accumulo
resta su `accumulo.primary_in`. Il modello completato ha 43 pezzi e 45 collegamenti (39 e
41 in DRAW-005). Con la sicurezza dichiarata a bordo (prova generale con un catalogo che
la dichiara) la sicurezza esterna del generatore non compare, e il bordo macchina è
l'unica differenza fra i due esiti. Lo sfogo aria è uno, su `accumulo.primary_out`.

`metriche.json` → `sicurezze`: per ciascuna delle tre, la fila dal capo, ciò che sta
prima dell'intercettazione, il ruolo (`generatore` con `a_bordo: [circulation]`, o
`riserva`).

## 3. Le misure, prima e dopo (criterio 7)

Il grafo non è lo stesso — due raccordi e due sicurezze in più, con i loro stacchi — e
la posa ha un contratto duro in più: **curve, incroci e lunghezza si riportano sul grafo
nuovo, senza leggerli come peggioramenti** della stessa tavola.

| Misura | Prima (DRAW-005, consegna) | **Dopo (DRAW-005-R1, consegna)** | Criterio |
|---|---:|---:|---|
| Pezzi del modello / simboli in tavola | 39 / 39 | **43 / 43** | 1, 2 |
| Sicurezze esterne prima dell'intercettazione (generatori / riserva) | 0 / 1 | **2 / 1** | 2 |
| Sfoghi aria | 1 | **1** | A.6 |
| Stacchi statici senza freccia (manometro, vaso, sfogo, sicurezze) | 0 su 6 (tutti ordinari, con freccia, colore di andata) | **6 su 6** | 3 |
| Riempimento: freccia verso il circuito, colore del ritorno | no (freccia verso il gruppo, colore di andata) | **sì** | 3 |
| Scarico: freccia uscente | ordinario | **sì** (`outbound`) | B |
| Simboli a tratto spesso (0,50 mm) in tavola | 0 (i filtri a 0,35 mm) | **2** (i due filtri) | 4 |
| Catene PDC (porta→filtro, filtro→valvola) | PDC-01: 7,5 / 5,0 mm sul primo rettilineo; PDC-02: filtro a 29,3 mm, **oltre la curva** | **5,0 / 2,5 mm su entrambe, sul primo rettilineo** | 5 |
| Rilievi di correttezza | 0 | **0** | 7 |
| Tubo sotto un simbolo | 0 | **0** | 7 |
| Backtracking | 0 tratte, 0 mm | **0 tratte, 0 mm** | 7 |
| Tratte oltre tre pieghe | 0 | **0** | 7 |
| Curve totali | 4 | **7** | riportato |
| Incroci | 1 | **2** | riportato |
| Lunghezza delle tubazioni | 525,0 mm | **767,5 mm** | riportato |
| Valvole D-120 a 2,5÷5 mm | 16 su 16 | **14 su 16 (le due valvole di mandata delle PDC: 10,0 mm oltre il raccordo, nota sotto)** | — (§8) |
| Sigle in consegna / indirizzi | 7 / 0 | **7 / 0** (verifica: 7 / 41) | — |
| Riempimento del foglio (solo diagnostica) | 33,3 % | 41,5 % | fuori perimetro |
| Preflight | 1 avviso (`SHEET_BARELY_FILLED`) | 2 avvisi (`SHEET_BARELY_FILLED`, `DRAWING_ALL_ON_ONE_SIDE`) | — |
| Impronta della geometria (consegna) | `a84cfe1a…` | `45fcab22…` | 9 |

La geometria di DRAW-005 riletta con lo schema di oggi — che ha `flow_kind` e
`flow_from_start` — dà l'impronta `3f5e97af…`, non `a84cfe1a…`: è la stessa tavola con
due campi in più a valore predefinito (DRAW-005 §3 aveva già notato l'effetto). Le due
valvole di mandata delle PDC contano fuori dai 2,5÷5 mm perché ora **fra la macchina e
la valvola c'è il raccordo della sicurezza**: la valvola è «primo oltre il raccordo»
(I-035) e si stringe al raccordo scorrendo fino al primo posto libero; il tratto fra il
raccordo e la confluenza è lungo 17,5 mm e lo stacco dalla confluenza (5 mm, la colonna
libera) la tiene a 10 mm dal raccordo. Non è la catena della macchina, che sul ritorno
è a 5,0 / 2,5 mm su entrambe. Le 14 dentro sono le 16 di prima meno queste due.

## 4. La posa: che cosa è servito perché la tavola componesse

Con le due sicurezze e i loro raccordi la tavola di DRAW-005, posata con il codice di
prima, non rispettava il contratto D e degradava (7 incroci, 12 pieghe, 987 mm nel primo
tentativo). Le prove a cavallo lo hanno isolato: il grafo di DRAW-005 con il codice
nuovo componeva bene (1 incrocio, 6 pieghe, 580 mm); il grafo nuovo con la posa vecchia
degradava allo stesso modo. Erano i raccordi di sicurezza a rompere la posa iniziale:
spezzavano la vicinanza fra le PDC e la confluenza, e sedevano sulla soglia della porta.
Le quattro correzioni di §1.4 (rettilineo imposto, corridoi, vicini attraverso i
raccordi, rami paralleli allo stesso livello) sono generali e riportano la tavola a
comporre con il contratto duro soddisfatto. Il costo globale (funzione invariata, fuori
perimetro) sceglie fra le pose che lo rispettano: `dopo/diario.json` elenca le
candidate provate e accettate. Il ciclo parte da una posa iniziale che rispetta il
contratto (0 violazioni, 12 pieghe, 5 incroci, 712,5 mm dopo la posa) e arriva alla
tavola consegnata (7 pieghe, 2 incroci, 767,5 mm): 1500 candidate di posa e 1000 di
rifinitura, 51 e 11 accettate; la lunghezza cresce di 55 mm per togliere 5 pieghe e 3
incroci, che è l'ordine dei pesi della funzione di costo com'è.

## 5. Le curve e gli incroci che restano

Sul grafo nuovo la confluenza delle due mandate e i due raccordi di sicurezza stanno fra
le PDC e l'accumulo; il ritorno della prima PDC attraversa le due verticali di mandata
(gli incroci). Sono conseguenze della funzione di costo, che non è in perimetro; il
contratto D è soddisfatto e i budget del criterio 7 (tubo sotto simbolo, backtracking,
tre pieghe per tratta) sono a zero.

## 6. Le prove generali, scritte prima del codice (criterio 1)

Quattro file nuovi, tutti su impianti costruiti nella prova o su modelli a mano, nessuno
su coordinate o identificativi della tavola 1:

- `tests/rules/test_sicurezza_generatori.py` (13): una e due macchine, con e senza
  sicurezza a bordo (catalogo di prova che la dichiara); la sicurezza attaccata alla
  macchina e prima di ogni intercettazione; il bordo macchina come unica differenza; la
  riserva con una sicurezza sola; pezzi distinti; lo sfogo resta sull'attacco dedicato e
  non condivide mai il pezzo con la sicurezza; rieseguire non propone; ogni regime;
  permutazione di componenti e connessioni; la tavola 1 protegge ciascuna macchina
  isolabile prima della sua intercettazione.
- `tests/layout/test_rami_di_servizio.py` (15): specie dalla funzione, servizio dalla
  tratta ospite, nessuna tratta indecisa con due macchine, riempimento/vaso/manometro
  ritorno tecnico, nessuna coordinata letta, invarianza al riordino del file, verso del
  flusso dal modello, frecce sulla tavola per specie, colore dello stacco, renderer
  senza colori né nomi, `P` manometro.
- `tests/graphics/test_rifiniture_simboli_tavola1.py` (16): peso nel manifesto e valore
  sottinteso, peso non valido rifiutato, peso conservato dalla rotazione, `thick` =
  0,50 mm, ogni manifesto pubblicato dichiara il peso, barrette del filtro, tratto in
  tavola/legenda/foglio di riscontro, nessun renderer conosce il filtro, serpentina
  continua, morbida, centrata, con abbastanza giri, porte e riquadro invariati.
- `tests/layout/test_catena_macchina.py` (9): catena sul primo rettilineo nell'ordine
  giusto nelle due giaciture, distanze invarianti a rotazione e traslazione, pezzi di
  rete dietro la catena, catena fuori dal primo rettilineo rifiutata, lettura dal
  catalogo, chi segue la catena le sta a un passo, le due catene della tavola 1
  congruenti, nessun tubo sotto la catena.

Prove esistenti adattate: `test_regime_and_common_return.py` (la sicurezza del generatore
non è più «solo sopra i 35 kW»), `test_contratti_simboli_tavola1.py` e `test_bodies.py`
(il lettore dei tracciati capisce gli archi).

## 7. Verifiche eseguite (criterio 8)

- `ruff check src tests examples docs/collaudi/DRAW-005-R1/metriche.py`: nessun rilievo;
  `mypy --strict src tests examples`: nessun errore su 147 file.
- Suite completa (`python -m pytest -q`, sul codice finale): **1290 verdi, 23 parcheggiate,
  13 marcate rosse apposta** in 31 minuti e 52 secondi. Contro DRAW-005 (1190 / 22 / 14):
  cento verdi in più (le 53 prove nuove e le parametrizzazioni), **nessuna nuova `xfail`**;
  una rossa-apposta in meno e una parcheggiata in più sono la stessa prova, quella del
  quinto impianto in `test_zone_dei_pezzi_grossi.py`, che su `cc7ff93` era rossa apposta
  sull'asserzione e oggi è parcheggiata perché l'impianto 5 non si posa (§9).
- La prova del difetto di §1.4 (`test_chi_segue_la_catena_di_testa_le_sta_a_un_passo_e_non_la_tocca`)
  è rossa senza la correzione del cursore e verde con essa (verificato riportando la riga
  e rieseguendola).
- Determinismo: due generazioni consecutive dallo stesso ingresso (`rules` e `draw`, una
  in `dopo/consegna/`, una in una cartella di sessione) danno lo stesso modello completato
  byte per byte, lo stesso SVG di consegna byte per byte e la stessa impronta `45fcab22…`.
- Verifica e consegna: stessi simboli e stesse rotte (43 simboli, 24 tratte in entrambe,
  7 curve, 2 incroci, 767,5 mm); la verifica aggiunge 41 indirizzi, nessuno su tubo,
  simbolo o altra scritta (`dopo/metriche.json`).

## 8. Osservazioni per il PM, che non decido io

- **Il ramo.** Il Work Package nomina `claude/draw-005-r1-rifiniture-tavola1`; la
  sessione ha assegnato `claude/draw-005-r1-rifiniture-tavola1-3aad42` e ho lavorato lì.
- **Il medium della regola del generatore.** Ho ristretto
  `safety-relief-where-heat-enters-the-water` a `network_medium: heating_water`: senza,
  la pompa di calore sanitaria dell'impianto 3 (`dhw_out` sulla rete sanitaria) riceveva
  una sicurezza sull'acqua calda sanitaria, punto aperto che il Work Package non chiede.
  Il gruppo di sicurezza di una riserva sanitaria che si scalda da sé è un'altra regola,
  oggi non scritta: se il PM la vuole, è un pacchetto suo.
- **Le valvole di mandata delle PDC** stanno ora **oltre** il raccordo della sicurezza
  (I-035, «primo oltre il raccordo»), non più a 5 mm dalla porta: è la conseguenza
  voluta del blocco A — la sicurezza sta fra macchina e valvola — e la valvola si
  stringe al raccordo per quanto il tratto consente (§3, nota alla tabella).
- **Gli stacchi che pendono da una macchina** (sfogo e scarico sull'accumulo) prendono il
  colore del servizio della tratta ospite come gli altri; non avendo una tratta ospite
  con servizio proprio, oggi risultano «andata»: è una scelta di default, non una
  decisione.
- **La legenda** alleggerisce ancora a `thin` i simboli ordinari e conserva `thick` per
  chi lo dichiara: se il PM preferisce una legenda con i pesi veri di ogni simbolo, è
  una riga in `legend_line_mm`.
- **Il serpentino del bollitore** (`dhw-cylinder`) resta rettangolare: fuori perimetro
  (audit dei simboli non coinvolti).
- **Il foglio** è pieno al 41,5 % e il preflight segnala anche
  `DRAWING_ALL_ON_ONE_SIDE`: composizione e riempimento sono fuori perimetro.
- **Il costo globale** non è stato toccato; la tavola ha più curve e incroci di DRAW-005
  perché il grafo ha due raccordi e due sicurezze in più e la posa ha un contratto duro
  in più (§3, §5). Se il PO giudica la tavola meno leggibile, è una decisione di costo,
  non di contratto.

## 9. Fuori perimetro, scoperto e lasciato dov'è

- Gli impianti 2–5 cambiano nei documenti derivati per conseguenza meccanica della
  regola (una sicurezza per generatore); non li ho guardati per merito né composti.
- La dipendenza della geometria dall'ordine delle connessioni resta com'era (DRAW-005 §8).
- **L'impianto 5 non si posa più** (`cascata-ritorno-a sits on a run and finds no free
  spot along it`): su `cc7ff93` si posava, e la prova
  `test_nessun_raccordo_sta_a_sinistra_di_cio_che_unisce[prova-5]` era rossa apposta
  sull'asserzione; oggi è parcheggiata perché la posa non riesce. È verosimile che siano
  i corridoi davanti alle porte delle tre macchine in cascata a togliere al raccordo il
  posto sulla tratta, ma non l'ho indagato oltre la misura: gli impianti 2–5 sono fuori
  perimetro (D-116) e la riga esiste perché il difetto non sia scoperto due volte.
- Nessuna modifica a cartiglio, etichette, riempimento del foglio, funzione di costo,
  packaging.

## 10. Artefatti

| File | Cosa |
|---|---|
| `prima/impianto1.{pdf,png,svg}` · `prima/geometria.json` · `prima/preflight.txt` · `prima/impianto1-completo.json` | la tavola di consegna di DRAW-005 e il suo modello, copiati |
| `prima/metriche.json` | la tavola di DRAW-005 rimisurata con lo strumento di oggi |
| `dopo/impianto1-completo.json` · `dopo/integrazioni.txt` | il modello completato dalle regole nuove, e le 28 integrazioni con le fonti |
| `dopo/impianto1.{pdf,png,svg}` · `dopo/geometria.json` · `dopo/metriche.json` · `dopo/preflight.txt` | la tavola dopo, in modalità verifica |
| `dopo/consegna/impianto1.{pdf,png,svg}` · `dopo/consegna/geometria.json` · `dopo/consegna/metriche.json` · `dopo/consegna/preflight.txt` | la tavola definitiva |
| `dopo/diario.json` | il diario del ciclo: candidate provate e accettate |
| `prima-dopo.png` | il confronto visivo, sopra DRAW-005 e sotto DRAW-005-R1 |
| `metriche.py` | lo strumento di misura, con sicurezze, sfoghi, stacchi, catene e pesi del tratto |
