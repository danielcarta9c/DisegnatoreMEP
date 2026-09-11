# DRAW-006 — semantica dei componenti e prima tavola nuova

**Ramo:** `claude/draw-006-tavola2-semantica-v4n8o5` · **Base:** `913dddb`, la `main` che
porta il Work Package
**Campo:** l'**impianto 2** come fixture grafica principale; la tavola 1 come regressione
automatica; gli impianti 3–5 alla sola posa.

> **Una sola tavola è stata renderizzata come consegna: la tavola 2.** La tavola 1 non è
> stata riconsegnata — è verificata dalle prove di regressione, senza artefatti — e gli
> impianti 3, 4 e 5 sono stati usati esclusivamente nelle prove prescritte: composizione
> fino alla posa per tutti e cinque, e per il quarto la logica dei domini di protezione,
> che non produce disegno.

**Il PDF della tavola 2:** `docs/collaudi/DRAW-006/dopo/consegna/impianto2.pdf`
(A3, 420 × 297 mm, a misura reale). Accanto stanno il PNG e l'SVG.

---

## 1. Il risultato in una riga

Sulla base la tavola 2 **non usciva affatto**: nessun formato ordinario la conteneva.
Adesso esce su A3, senza rilievi bloccanti, con zero backtracking, zero tubo sotto un
simbolo e nessuna tratta oltre tre pieghe.

| Tavola 2 | prima (`913dddb`) | **dopo (DRAW-006)** |
|---|---|---|
| Tavola | **non esce**: `run p6-a-1-4 has no straight stretch of 10 mm for valve-isolation` | **A3, 420 × 297 mm** |
| Pezzi del modello / collegamenti | 46 / 48 | **45 / 47** |
| Integrazioni proposte / punti aperti | 30 / 0 | **29 / 0** |
| Rete ordinaria — pieghe / incroci / lunghezza | — | **7 / 2 / 670,0 mm** |
| Stacchi statici — pieghe / incroci / lunghezza | — | **0 / 0 / 62,5 mm** |
| Backtracking · tubo sotto un simbolo · tratte oltre tre pieghe | — | **0 · 0 · 0** |
| Valvole D-120 a 2,5÷5 mm | — | **15 su 16** (una a 27,5 mm) |
| Ingombro del disegno | — | **270,0 × 120,0 mm** |
| Rilievi bloccanti · avvisi | 1 bloccante (la tavola non esce) | **0 · 2** |

I due avvisi che restano sono di sola composizione — foglio pieno al 39,4 % e disegno
tutto su un lato — e il riempimento del foglio è dichiarato fuori perimetro.

### Che cosa è cambiato, separatamente

**Il grafo** perde un pezzo netto (46 → 45) e non ne guadagna nessuno: la valvola esterna
del gruppo di riempimento sparisce perché il gruppo la porta dentro, e la valvola
ordinaria del manometro diventa il rubinetto portamanometro a tre vie. In numeri:
`valve-isolation` passa da 12 a 10, compare un `valve-gauge-cock-3way`. Nessun'altra
integrazione cambia, e i punti aperti restano zero.

**La posa** cambia per due ragioni, tutte e due generali. La prima è il pezzo in meno:
lo stacco del riempimento è più corto e la fila lungo il ritorno si accorcia. La seconda
è che il rubinetto della presa, pur non essendo un organo di chiusura, è **un organo di
servizio**: la posa lo stringe al proprio strumento come stringe una valvola alla macchina
che isola (D-120). Senza questa distinzione il rubinetto scivolava lungo lo stacco e il
disegno peggiorava — lo si vede al §5.

**Il rendering** non cambia: nessuna regola grafica nuova, nessuna eccezione per la
geometria dell'impianto 2. L'unico segno nuovo è quello del rubinetto a tre vie, che è un
componente nuovo e non una convenzione nuova.

---

## 2. I tre difetti di semantica, uno per uno

### 2.1 A — manometro e rubinetto portamanometro a tre vie

Il vocabolario delle proprietà acquista un **quarto regime di intercettazione**:
`shutoff_instrument_tap`, «lo si chiude con il rubinetto della propria presa». Non è una
deroga alla regola dell'intercettazione, che resta **una sola**: il pezzo dichiara come si
lascia chiudere, la regola dice quale mestiere ciascun regime pretende — comune per la
maggior parte, bloccabile aperto per il vaso, rubinetto della presa per uno strumento
indicatore. Il manometro dichiara il nuovo regime, la regola chiede
`instrument_isolation`, e il catalogo risolve con `valve-gauge-cock-3way`.

Il gruppo che ne esce è quello del Work Package: **presa sulla tubazione → stacco statico
minimo → rubinetto a tre vie → manometro**. Il rubinetto vive sullo stacco: la condotta
non lo attraversa, e nessuna tubazione del percorso lo tocca.

`instrument_isolation` **non** entra fra i mestieri di chiusura. È la ragione per cui il
rubinetto non divide un dominio idraulico: chi cammina sulla rete per sapere se un
generatore può restare separato dalla propria sicurezza non lo conta. Per la **posa**,
invece, è un organo come gli altri, e il catalogo dichiara i due insiemi separatamente —
`CLOSING_FUNCTIONS` per l'idraulica, `SERVICE_ORGAN_FUNCTIONS` per il disegno.

Il **pressostato** non riceve niente, e non per un'eccezione: un pressostato di sicurezza
o di minima non si smonta a impianto in pressione, quindi non dichiara di manutenersi, e
il suo regime è «non lo si chiude mai». La prova costruisce quel componente e verifica
che nessun organo gli venga posato addosso.

Il segno è nuovo e distinto: tre triangoli convergenti come la deviatrice, ma con la terza
via **su tappo** — l'attacco per il manometro campione, che non è una tubazione
dell'impianto e perciò non è una porta del componente. La famiglia di sigle è `RM`.

### 2.2 B — gruppi compositi e riempimento

Un composito adesso **deve dichiarare** quali funzioni si porta dentro: `composite: true`
senza `carries_on_board` non si carica. La bandiera da sola non dota di niente, ed è
esattamente il punto — «il gruppo ha già le sue valvole» smette di essere una cosa che si
sa e diventa una cosa che il catalogo dice.

Il gruppo di riempimento pubblicato dichiara `isolation` e nient'altro: niente
disconnettore, niente filtro, niente ritegno, niente riduzione di pressione. Quelle
appartengono alle varianti che le dichiarano, e nel catalogo pubblicato non ne esiste
nessuna: le prove le costruiscono al proprio interno, perché una variante di prodotto la
decide il PM, non il DEV.

Nel catalogo di fondazione `composite` **non si deduce più dal numero dei mestieri**: una
caldaia che genera calore e brucia gas fa due cose e resta un apparecchio, non un gruppo.
Era l'unica dichiarazione automatica rimasta, e attribuiva una dotazione a chi non ne ha
nessuna.

Sulla tavola 2 il riempimento c'è, ed è come il §B.5 lo vuole: **uno solo** sul circuito
tecnico, sullo stacco del ritorno generale, con la freccia **verso** il circuito
(`specie: inbound`, `verso_la_radice: true` nelle misure) e senza nessuna valvola esterna.

### 2.3 C — stati idraulici e domini di protezione

Il catalogo dichiara gli **stati idraulici ammessi** di un componente multivia. Per la
deviatrice a tre vie sono due: `in ↔ out_a` oppure `in ↔ out_b`. `out_a ↔ out_b` non
compare in nessuno stato, e non c'è modo di scriverlo per sbaglio: uno stato solo non si
carica (non sarebbe un'alternativa), due stati identici nemmeno, e una porta del percorso
che non comunichi in nessuno stato è un errore di catalogo.

Il dato è **uno solo** e lo leggono in due. La nomenclatura delle linee ha perso il
proprio elenco di mestieri (`PASS_THROUGH_FUNCTIONS`) e chiede al catalogo se il pezzo
dichiara stati. L'analisi della sicurezza rifà la camminata **in ogni configurazione
ammessa della rete** e dichiara protetto solo chi raggiunge la funzione in tutte: basta
uno stato in cui non la raggiunge perché quel generatore sia un dominio a sé.

Il tratto comune si calcola **per dominio**. Le camminate degli ancoraggi si raggruppano
per la tubazione che condividono; ogni gruppo ha la propria testa. La sicurezza del
circuito dichiara la cardinalità nuova `per_protection_domain` e serve **ogni** dominio:
una protezione valida per una parte della rete non si scarta più perché un'altra parte non
la raggiunge. Le altre regole di rete restano `per_network` e conservano il punto aperto
di sempre quando la rete non ha un tratto comune unico — è la decisione di P2 sul
defangatore fra due anelli separati, e non è stata toccata.

**Sull'impianto 4**, che il pacchetto usa senza produrre disegno: il `NO_COMMON_RUN`
globale è sparito, la pompa di calore conserva la protezione del proprio dominio, e resta
**una sola** domanda aperta — quella dovuta al dato di catalogo realmente ignoto sulla
caldaia, che la deviatrice può isolare. Prima erano tre punti aperti: un tratto comune
negato e due domande.

---

## 3. Le prove, scritte prima del codice

`tests/rules/test_semantica_dei_componenti.py` (15 prove, blocchi A e B) e
`tests/rules/test_stati_idraulici_e_domini.py` (18 prove, blocco C) sono state scritte e
consegnate **prima** dell'implementazione, nel primo commit del ramo, dichiarate rosse.

Sono generali. Gli impianti si costruiscono nelle prove — un anello, una linea sanitaria,
N macchine in parallelo, due circuiti chiusi indipendenti sulla stessa rete, la forma
dell'ibrido con la deviatrice; le voci di catalogo che servono a dimostrare una proprietà
e che nessun impianto usa (il manometro su un altro fluido, il pressostato, tre compositi
con dotazioni diverse, le due pompe di calore con il dato di bordo dichiarato) vivono
dentro le prove. Nessun identificativo, nessuna coordinata e nessuna soglia di una tavola
entra nelle attese. L'unica prova che legge una fixture è quella dell'impianto 4, che
verifica un comportamento e non decide niente.

Fra le proprietà provate: il rubinetto è distinto dalla valvola per voce, mestiere e segno;
il regime della presa è un regime dichiarato e non si somma a un altro; il rubinetto non
compare fra gli organi propri di un generatore e non lo separa dalla sicurezza; il gruppo
della presa è presa → rubinetto → strumento e non tocca la condotta; la stessa proprietà
vale su un altro fluido, e né le regole né il catalogo hanno un campo che parli della
misura della condotta; un composito muto non si carica; due gruppi con lo stesso nome e lo
stesso segno ricevono dotazioni diverse solo per ciò che dichiarano; i due rami di una
deviatrice non comunicano in nessuno stato; una macchina dietro la deviatrice è tagliata
fuori e una sul circuito no; due domini scollegati ricevono una sicurezza ciascuno; il
generatore isolabile segue il dato di bordo nei tre casi.

---

## 4. Il test sulle colonne dei raccordi (blocco D)

L'ultima asserzione era `assert not (raccordi - colonne) or somma <= 280.0`, e la
condizione di destra era già stata asserita due righe sopra: la prova non poteva fallire
per quel motivo. Peggio, la misura non vedeva la proprietà che nomina — promuovere un
raccordo a colonna non cambiava la somma, perché i raccordi erano esclusi dal conto per
costruzione.

La prova nuova deriva **l'attesa dalla classificazione** — le colonne della fila sono
quelle dei pezzi che il catalogo dichiara degni di una zona (D-120) — e **la misura dalla
posa**: l'ascissa a cui ciascun pezzo è finito. La proprietà è che nessun raccordo sta su
una di quelle ascisse. Nessuna soglia della tavola 1 compare più: l'unica misura assoluta
è l'area di disegno del foglio, che è del formato e non dell'impianto.

In coda la prova costruisce la **mutazione negativa**: lo stesso raccordo che dichiara
anche un mestiere da colonna. Sotto la mutazione la fila cresce di una colonna e la misura
lo vede — se non lo vedesse, la prova non starebbe misurando ciò che nomina.

---

## 5. La tavola 1, regressione automatica

Non è stata riconsegnata come elaborato: nessun PDF, nessun PNG, nessun SVG. La
regressione è nella prova, e le soglie sono passate a quelle del §E del Work Package —
più strette di quelle che c'erano.

| Misura (tavola 1) | DRAW-005-R1 (consegna) | criterio §E | **oggi** |
|---|---:|---:|---:|
| Rete ordinaria — curve | 4 | ≤ 4 | **4** |
| Rete ordinaria — incroci | 1 | ≤ 1 | **1** |
| Rete ordinaria — lunghezza | 425,0 mm | ≤ 425 mm | **417,5 mm** |
| Stacchi statici — curve / incroci / lunghezza | 0 / 0 / 45,0 mm | 0 / 0 / ≤ 45 mm | **0 / 0 / 40,0 mm** |
| Backtracking · tubo sotto un simbolo · tratte oltre tre curve | 0 · 0 · 0 | 0 · 0 · 0 | **0 · 0 · 0** |

Le tre qualità senza numero non si ricontano più a mano nella prova: si leggono dai
validatori (`LINE_UNDER_SYMBOL`, `RUN_OVERSHOOTS_ITS_PORT`, `RUN_WITH_TOO_MANY_BENDS`),
che sono gli stessi che governano la consegna.

**La strada per arrivarci, perché è il rilievo tecnico del pacchetto.** Con il solo
cambio del riempimento la tavola 1 migliorava subito (4 / 1 / 417,5). Aggiungendo il
rubinetto peggiorava di colpo: 6 curve, 2 incroci, e lo stacco del manometro con quattro
pieghe. La causa non era il segno né la misura del pezzo — è identica a quella della
valvola — ma il fatto che la posa riconosce «l'organo che isola un apparecchio» dai
**mestieri di chiusura**, e il rubinetto non è uno di quelli. Da lì la distinzione fra i
due insiemi del catalogo: `CLOSING_FUNCTIONS` è una domanda idraulica, `SERVICE_ORGAN_FUNCTIONS`
è una domanda di disegno, e confonderle costava tre curve.

### Il difetto di posa che la correzione ha fatto affiorare

È della specie che questo progetto conosce — D-120 fece affiorare «la linea sotto il
simbolo» — e va detto per intero, perché non è un effetto della correzione ma un difetto
che la correzione **scopre**.

Togliere la valvola dallo stacco del riempimento cambia quale accessorio pende da quale
raccordo. Un accessorio che pende **verso il basso** finisce contro la linea di terra, e
lì non ha più dove allontanarsi. Se quel posto cade dentro il rettilineo che la catena di
una macchina pretende davanti alla propria porta (I-044) — un contratto duro, non una
preferenza — la tratta non si instrada più, e non su un formato: su nessuno. È successo
sul gemello sintetico della tavola 1 che vive nelle prove (`due_macchine_con_accumulo_combinato`,
la stessa topologia senza i suoi identificativi): la tavola smetteva di comporsi.

La correzione è dove il difetto vive. Chi sceglie il posto di un raccordo guarda adesso
anche **dove finisce ciò che gli pende**, e scarta i posti da cui l'appeso non può
uscire. Il conto di dove l'appeso finisce vive in un posto solo — `hanging_place` — ed è
lo stesso che la posa esegue: prima erano due conti che dovevano dare lo stesso numero, e
divergevano. Tutti i ripieghi di prima restano: se nessun posto rispetta i corridoi si
scende a quelli che non li rispettano, perché una posa che non c'è non la migliora
nessuno. Tavola 1 e tavola 2 non cambiano di un millimetro — stesse impronte.

Due strade sono state provate e **buttate**, e vale la pena non riprovarle: far scivolare
l'appeso *di lato* quando lo stacco è murato (la tavola 1 passava a 8 curve e 4 incroci),
e far parlare la derivazione per l'accessorio in fondo allo stacco invece che per l'organo
che vi sta in mezzo (8 curve, 4 incroci, 457,5 mm). La seconda è però un difetto vero e
sopravvive a questo pacchetto: la derivazione dichiara i vincoli d'ordine **dell'organo**
sullo stacco, non dell'accessorio che ci pende, e l'ordine del corredo di rete finisce
per dipendere dall'ordine alfabetico degli identificativi. Lo segnalo al PM al §9.

---

## 6. Gli impianti 3–5

Solo prove di componibilità, nessun pacchetto completo.
`tests/layout/test_posa_dei_cinque_impianti.py` pretende che tutti e cinque arrivino alla
posa, senza `try/except` e senza `skip`: verde. La rossa-apposta sulla qualità geometrica
dell'impianto 5 resta dov'era, in `test_zone_dei_pezzi_grossi.py`, e non è stata toccata.

L'impianto 3 e l'impianto 4 non arrivano a una tavola su A3 — l'instradamento non trova
posto per una catena — ma **era già così sulla base**, con lo stesso messaggio: non è una
regressione di questo pacchetto e sta fuori dal suo perimetro.

---

## 7. Prove esistenti adattate, e perché

Nessuna è stata indebolita; ciascuna dice nel proprio testo perché è cambiata.

- `test_ogni_gruppo_manutenibile_si_isola_su_ogni_attacco_verso_l_esterno` esclude ora chi
  **dichiara l'organo a bordo**: il gruppo di riempimento è isolato lo stesso, e
  pretendergli una valvola esterna sarebbe pretendere il pezzo ridondante che il PM ha
  tolto.
- `closers_of`, in `test_acceptance_properties.py`, cerca l'organo che il **regime
  dichiarato** pretende invece di un elenco proprio di due mestieri: legge la stessa
  tabella della regola, così non può divergere da lei.
- `test_the_libraries_are_not_empty`: 47 → 48 simboli, che è il rubinetto nuovo.
- `test_i_raccordi_non_prendono_una_colonna_a_testa`: riscritta per intero (§4).
- `test_la_tavola_1_non_costa_piu_di_draw_005_sulla_rete_ordinaria`: soglie **strette**
  a quelle del §E (§5).
- `test_dove_il_tratto_comune_non_esiste_davvero_esce_un_punto_aperto` (collaudo P5): su
  due anelli separati la **sicurezza** non apre più il proprio punto e ne posa una per
  anello — è il §C.4 e il §C.5 alla lettera, e nessun anello viene scelto in silenzio
  perché si servono tutti e due. Le altre quattro regole di rete restano `per_network` e
  il loro punto aperto, deciso in P2, è invariato: la prova adesso lo pretende
  esplicitamente.
- `test_il_confronto_per_il_pm_dice_il_vero_sui_documenti` (collaudo P5): i punti aperti
  dell'ibrido passano da tre a **uno**.

Fixture rigenerate dai loro generatori, mai a mano: il catalogo di layout, la libreria dei
simboli, il catalogo di fondazione, il caso di accettazione completo
(`examples/rules/centrale-pdc-completa.json`), il documento del grafo
(`docs/prodotto/GRAFO_IMPIANTO.md`) e i cinque grafi di prova
(`docs/prodotto/grafi-di-prova/prova-*.md`). Il documento delle proprietà per il
committente guadagna la riga del quarto regime; il confronto per il PM
(`CONFRONTO-2026-08-07.md`) porta i conteggi di oggi e una nota datata su che cosa li ha
cambiati, come già faceva per DRAW-005 e DRAW-005-R1.

---

## 8. Verifiche

- **Suite completa** (`python -m pytest -q`): **1369 verdi, 22 parcheggiate, 14 rosse
  apposta, nessuna rossa**, in 42 minuti e 13 secondi. Contro la base di partenza: le
  rosse apposta e le parcheggiate sono le stesse — nessuna prova è stata convertita in
  `skip` o `xfail` — e le verdi crescono di trentatré, che sono le prove nuove dei
  blocchi A, B e C.
- **`ruff check src tests examples docs/collaudi/DRAW-006/metriche.py`**: nessun rilievo.
- **`mypy src tests examples`** con il profilo `strict` di `pyproject.toml`: nessun errore
  su 151 file.
- **Determinismo**: due esecuzioni consecutive dallo stesso ingresso danno il modello
  completato **identico byte per byte**, l'SVG di consegna **identico byte per byte**, la
  stessa geometria e la stessa impronta `903c926b…`.
- **Preflight della tavola 2**: **nessun rilievo bloccante**; due avvisi di composizione
  (`SHEET_BARELY_FILLED` al 39,4 %, `DRAWING_ALL_ON_ONE_SIDE`), che il perimetro esclude.

---

## 9. Osservazioni per il PM, che non decido io

1. **La sigla del rubinetto è `RM`.** Il pacchetto chiedeva un componente e un simbolo
   distinti; la sigla di famiglia serviva perché la tavola esca, e nessuna fonte del PM
   ne indica una. È un dato in `naming/families.json`: cambiarla è una riga.
2. **La cardinalità per dominio l'ho data alla sola sicurezza**, come il §C.4 dice
   testualmente. Le altre regole di tratto comune — riempimento, manometro, vaso,
   defangatore — restano per rete, e su due circuiti chiusi indipendenti dichiarati sulla
   stessa rete continuano a produrre un punto aperto invece di servirli entrambi. È la
   decisione di P2 («sceglierne uno sarebbe decidere al posto del progettista») e non l'ho
   toccata: se il PM la vuole allineata alla sicurezza, è una riga per regola.
3. **La variante del gruppo di riempimento con disconnettore non esiste in catalogo.** Il
   meccanismo che la sosterrebbe c'è ed è provato; la dotazione di un prodotto la dichiara
   il PM.
4. **Il foglio della tavola 2 è pieno al 39,4 % e il disegno sta su un lato.** Composizione
   e riempimento sono fuori perimetro; li segnalo perché il PM li veda quando toccherà a
   loro.
5. **Gli impianti 3 e 4 non arrivano a una tavola su A3**, già dalla base. Se la release
   0.3 li vuole disegnabili, è un pacchetto suo.
6. **L'ordine del corredo di rete su una tratta dipende ancora dall'ordine alfabetico
   degli identificativi**, e non dovrebbe. Una derivazione «parla per» ciò che le pende,
   ma si ferma al **primo** pezzo dello stacco: se lì c'è un organo — la valvola del vaso,
   il rubinetto del manometro — la derivazione dichiara i vincoli di quell'organo, che
   non ne ha, invece di quelli dell'accessorio in fondo. Sulla tavola 1 il manometro
   finisce così **prima** del riempimento, mentre la sua regola gli chiede di seguirlo.
   Ho provato la correzione — far camminare la lettura fino in fondo allo stacco — e
   l'ordine torna quello dichiarato, ma la tavola 1 passa a 8 curve, 4 incroci e 457,5 mm:
   il difetto è vero, la sua correzione costa, e la scelta è del PM. Non l'ho consegnata.

---

## 10. Artefatti

| File | Cosa |
|---|---|
| `prima/impianto2-completo.json` · `prima/integrazioni.txt` | il modello completato sulla base e le sue 30 integrazioni |
| `prima/preflight.txt` | il motivo per cui la tavola 2 non usciva |
| `dopo/impianto2-completo.json` · `dopo/integrazioni.txt` | il modello completato di oggi e le sue 29 integrazioni |
| `dopo/impianto2.{pdf,png,svg}` · `dopo/geometria.json` · `dopo/metriche.json` · `dopo/preflight.txt` | la tavola in **modalità verifica**, con gli indirizzi dei nodi |
| `dopo/consegna/impianto2.{pdf,png,svg}` · `dopo/consegna/…` | **la tavola 2 definitiva**, con metriche, geometria e preflight |
| `metriche.py` | lo strumento di misura, quello di DRAW-005-R1 |
