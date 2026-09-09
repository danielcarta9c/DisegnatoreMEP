# DRAW-005-R1 — rifinitura della tavola 1 (consegna corretta)

**Ramo:** `claude/draw-005-r1-rifiniture-tavola1-3aad42` · **PR** #21, aggiornata sul posto
**Base:** `e3dec7f`, il `main` che porta la correzione PM del 2026-09-09 (I-046), integrato
nel ramo con un merge
**Prima consegna:** respinta dal PM. Questo rapporto sostituisce il precedente e dice, per
ciascun rilievo, che cosa è cambiato.
**Campo:** l'impianto 1 come **fixture di regressione** e i contratti generali che servono;
gli impianti 2–5 devono arrivare almeno alla posa come sulla base `cc7ff93`.

Il vincolo architetturale del pacchetto è rispettato alla lettera: nel codice di produzione
non compaiono identificativi o nomi di componenti della tavola 1, coordinate specifiche,
nomi di file d'esempio, un numero fisso di PDC né soglie numeriche ricavate dalla tavola 1.
I numeri della tavola 1 vivono **solo** nelle prove di regressione
(`tests/layout/test_stacchi_minimi_e_interasse.py`, ultima prova del file, e
`tests/rules/test_sicurezza_dominio_idraulico.py`, ultima prova del file). Verificato con
`grep` su `src/`: nessun identificativo della tavola 1 compare in una condizione, in una
costante o in un confronto, e nessuna delle sue misure è scritta nel codice. I nomi che si
leggono in `src/` stanno **nei commenti**, dove raccontano il caso che ha originato una
regola — «la valvola che isola l'accumulo restava a mezza strada» — e non entrano nel
comportamento: toglierli non cambierebbe una riga di esito.

## 1. I cinque rilievi, uno per uno

### 1.1 Sicurezza: una per **dominio idraulico**, non per macchina (rilievo 1)

La prima consegna aveva conservato la sicurezza sull'accumulo e ne aveva aggiunta una per
PDC. Era sbagliato: la sicurezza andava **spostata**, non duplicata.

- **Il dato di catalogo è tri-stato** (`catalog/schema.py`): una macchina dichiara che cosa
  porta a bordo (`carries_on_board`) e, se la scheda lo dice, che cosa **non** porta
  (`lacks_on_board`); dove tace, il dato è `UNKNOWN` — **ignoto, non assente**. Le due
  caselle non possono contenere la stessa funzione, né ripetere un mestiere dichiarato: un
  catalogo così non si carica.
- **Il dominio di protezione si legge dalla connettività** (`rules/context.py`):
  `own_closers` sono gli organi di chiusura *propri* di una macchina, quelli che il suo
  manutentore chiude; `cut_off_from` cammina sulla rete e attraversa tutto **tranne** gli
  organi altrui. Una macchina che, con i propri organi aperti, raggiunge la sicurezza
  comune è protetta; una che resta separata da un organo altrui è un dominio a sé.
- **Le regole** (18 in tutto, tre nuove o riscritte):
  `safety-relief-on-the-closed-circuit` (nuova, sotto i 35 kW) posa **una sola** sicurezza
  per rete, sulla **mandata comune**, attaccata a ciò che unisce i generatori e prima di
  qualunque organo: più vicino al gruppo di così non si può stare restando comune a tutti;
  `safety-relief-on-an-isolable-generator` (nuova) dà una sicurezza propria **solo** alla
  macchina che il catalogo dichiara *senza* sicurezza a bordo e che i propri organi
  isolano dal circuito; `safety-relief-where-heat-enters-the-water` torna alla semantica
  per-generatore **sopra i 35 kW**. La regola sul volume in serbo è stata **cancellata**.
- **Il dato ignoto genera una domanda, non un pezzo**: `if_on_board_is_unknown: ask` produce
  un `RuleGap` con motivo `ON_BOARD_UNKNOWN`, uno per macchina, che il rapporto delle regole
  scrive a parole («il catalogo di X non dice se la macchina porta a bordo la sicurezza: il
  dato è ignoto, non assente»).
- **Sulla tavola 1**: una sicurezza di circuito su `collettore-mandata.b` — la confluenza
  delle due mandate, il suo raccordo a 10 mm dalla confluenza — **zero** sull'accumulo,
  **zero** per PDC, **uno** sfogo aria sull'attacco alto dell'accumulo. Il modello completato
  ha **39 pezzi e 41 collegamenti**, gli stessi di DRAW-005.

### 1.2 Stacchi: il **minimo su griglia**, non una costante (rilievo 2)

`stub_minimum_mm` (in `layout/place.py`) calcola la lunghezza di uno stacco dalla tratta:
uno stacco vuoto è lungo **due passi** — la soglia dell'attacco del raccordo e quella
dell'attacco di chi pende (D-113), una per ciascuno; uno stacco con organi in mezzo è
lungo quanto la fila fra le **due soglie**, cioè da ciascun attacco la soglia più un passo
(la stessa distanza fissa della catena di macchina, I-044) più i pezzi con un passo fra
loro. Nessun franco costante: `HANGING_CLEARANCE_MM` è stato tolto. La posa siede ogni
appeso a quel minimo; il ciclo può allungarlo, e allora lo paga in lunghezza.

Sulla tavola consegnata i sei stacchi statici misurano **45 mm in tutto** (erano 6 stacchi
anche prima), nessuno con una curva, nessuno oltre il proprio minimo senza una ragione
visibile.

### 1.3 Traslazione gratuita delle macchine (rilievo 3)

- **L'interasse è la prima candidata**: `_lift_moves` trasla verticalmente una macchina con
  ciò che le pende, a passi di griglia, e il ciclo la prova **per prima** in tutte e due le
  fasi. Vale per qualunque componente, non per le PDC.
- **Chi sta a terra può cambiare quota anche nella prima fase**: prima non poteva, e
  l'interasse fra due macchine impilate non si apriva mai.
- **I raccordi di servizio seguono il proprio raccordo**: una candidata che sposta o gira un
  raccordo rimette in fila, dalla sua porta, i raccordi che gli stanno stretti su una tratta
  vuota, con ciò che a loro pende (`_with_followers`). Ed è un **vincolo**, non un costo: su
  una retta il tubo totale non cambia spostando un raccordo, quindi nessun costo terrebbe la
  sicurezza vicino al gruppo — `is_valid` rifiuta le pose che allungano quelle tratte vuote.
- **Il posto del raccordo è fra i due pezzi grossi che la sua tratta unisce** (D-120): la
  posa lo cerca dentro quella campata e, se lì non c'è posto, **al posto libero più vicino**,
  non in fondo alla tavola.
- **Lo spazio che avanza sul foglio si divide secondo il bisogno**: prima in parti uguali,
  ora prima alle gole che devono ospitare una catena di raccordi e solo per quel che manca
  loro, il resto come sempre. La larghezza totale della composizione non cambia.

Sulla tavola 1 l'interasse fra le due PDC **cresce da solo** da 40 a 45 mm e le due dorsali
diventano rettilinee.

### 1.4 Misure separate e regressione della tavola 1 (rilievo 4)

`metriche.py` misura ora **due reti**: `rete_ordinaria` (le tratte che portano il fluido di
processo) e `stacchi_statici` (sicurezza, sfogo, manometro, vaso, riempimento, scarico),
separate per `flow_kind`; un incrocio condiviso fra una tratta ordinaria e uno stacco è
attribuito allo stacco.

| Misura (consegna) | DRAW-005 | **DRAW-005-R1** | Criterio |
|---|---:|---:|---|
| Rete ordinaria — curve | 4 | **4** | 10 |
| Rete ordinaria — incroci | 1 | **1** | 10 |
| Rete ordinaria — lunghezza | 525,0 mm | **425,0 mm** | 10 |
| Stacchi statici — curve / incroci / lunghezza | — | **0 / 0 / 45,0 mm** | 10 |
| Pezzi del modello / simboli in tavola | 39 / 39 | **39 / 39** | 1, 2 |
| Sicurezze di circuito / per macchina / sul serbatoio | 0 / 0 / 1 | **1 / 0 / 0** | 2 |
| Sfoghi aria | 1 | **1** | 2 |
| Valvole D-120 a 2,5÷5 mm | 16 su 16 | **16 su 16** | 5 |
| Tubo sotto un simbolo · backtracking · tratte oltre tre curve | 0 · 0 · 0 | **0 · 0 · 0** | 7 |
| Ingombro del disegno | 255,0 × 107,5 mm | **247,5 × 105,0 mm** | — |

**Come leggere la riga di DRAW-005**: la sua geometria è agli atti senza `flow_kind`, quindi
lo strumento la conta tutta come rete ordinaria — i suoi 525 mm e le sue 4 curve
**comprendono** i suoi sei stacchi. Il confronto è quindi generoso verso di noi sulla
lunghezza: la rete ordinaria di oggi è 425 mm, e con gli stacchi 470 mm, comunque sotto i
525 mm di allora, a parità di curve e incroci.

La prova di regressione vive nella fixture, non nel motore:
`test_la_tavola_1_non_costa_piu_di_draw_005_sulla_rete_ordinaria` passa il modello dal JSON
canonico come fa la CLI, separa le due reti e pretende **≤ 4 curve, ≤ 1 incrocio, ≤ 525 mm**.

### 1.5 Composabilità dei cinque impianti (rilievo 5)

`tests/layout/test_posa_dei_cinque_impianti.py` (nuovo) pretende che **tutti e cinque** gli
impianti arrivino almeno alla posa, senza `try/except` e senza `skip`: se uno non si posa, la
prova è rossa. La rossa-apposta sulla qualità geometrica dell'impianto 5 resta dov'era, in
`test_zone_dei_pezzi_grossi.py`, e il `try/except → skip` che l'aveva sostituita è stato
tolto. Nessuna nuova `xfail`, nessun nuovo `skip`.

## 2. Che cosa è stato conservato dalla prima consegna

Filtro a Y con le barrette e tratto 0,50 mm; serpentina continua e morbida dell'accumulo;
colori dei rami di servizio (riempimento, vaso e manometro sul lato ritorno); riempimento con
la freccia **verso** il circuito; nessuna freccia su vaso, manometro e stacchi statici; catena
della macchina (porta → filtro → valvola) sul primo rettilineo; determinismo.

## 3. Prove nuove, scritte prima del codice

- `tests/rules/test_sicurezza_dominio_idraulico.py` (19 prove) sostituisce
  `test_sicurezza_generatori.py`: tri-stato del bordo macchina; una sicurezza per dominio
  qualunque sia il numero delle macchine; sulla mandata comune, attaccata alla confluenza e
  prima di ogni organo; niente per macchina né sulla riserva; comunicazione attraverso i
  **soli organi propri**; dominio isolabile con dato assente (sicurezza propria), ignoto
  (domanda aperta, una per macchina) e presente (niente); due reti, due domini; sopra i
  35 kW una per generatore; sfogo unico; idempotenza; permutazione; la tavola 1.
- `tests/layout/test_stacchi_minimi_e_interasse.py` (12 prove): il minimo dello stacco è una
  funzione della tratta; la posa iniziale lo rispetta, e dove non lo rispetta il posto è
  davvero preso; sulla tavola composta nessuno stacco è più lungo del minimo senza una
  ragione visibile; il ciclo prova per prima la traslazione verticale; traslare una macchina
  non cambia il suo riquadro né stacca ciò che le pende; il raccordo che regge uno stacco sta
  stretto al raccordo a cui è attaccato; la regressione della tavola 1.
- `tests/layout/test_posa_dei_cinque_impianti.py` (2 prove): i cinque impianti sono cinque, e
  ciascuno arriva alla posa.

## 4. Prove esistenti adattate, e perché

Tre prove misuravano una situazione che la correzione del PO ha **fatto sparire** o
descrivevano una convenzione che il pacchetto ha cambiato. Sono state adattate, mai
indebolite, e ciascuna dice nel proprio testo perché:

- `test_la_valvola_che_isola_oltre_un_raccordo_passante_si_stringe_al_raccordo`: cercava il
  raccordo passante **solo** al capo d'arrivo della tratta, e la sicurezza dell'accumulo lo
  metteva lì. Ora la ricerca è simmetrica e salta i pezzi che appartengono alla catena di una
  macchina, che stanno a stazione fissa dalla porta (I-044) e hanno una prova propria.
- `test_the_rotation_follows_the_run_and_is_allowed`: pretendeva la rotazione in `(0, 90)`.
  Il filtro a Y non si specchia — ammette 0 e 270 — quindi su un tratto verticale la sola
  giacitura possibile è 270. Ora la prova verifica ciò che il suo nome dice: la rotazione
  **segue la giacitura del tratto** ed è una che il simbolo ammette.
- `test_i_raccordi_non_prendono_una_colonna_a_testa`: misurava la larghezza della posa
  (≤ 280 mm) come indizio del fatto che i raccordi non prendono una colonna. Ora la gola fra
  due fasce prende, **dello spazio che avanza sul foglio**, quello che serve alla catena di
  raccordi che la attraversa: la posa iniziale si distende (335 mm) senza che nessuna fascia
  si allarghi, e la tavola consegnata è più stretta di quella di DRAW-005 (247,5 contro
  255,0 mm). La prova misura ora la cosa che nomina — la somma delle **colonne** dei pezzi
  grossi, ≤ 280 mm — e in più che la posa entri nell'area di disegno. **È l'unica soglia di
  una prova esistente che ho cambiato: la segnalo al PM perché la giudichi.**

## 5. Il ciclo, sulla tavola 1

`dopo/diario.json` registra la corsa: la posa iniziale costa 2 violazioni, 4 tratte con
backtracking, 31 pieghe, 9 incroci e 970 mm; dopo la fase di posa (1500 candidate provate)
0 violazioni, 10 pieghe, 3 incroci, 535 mm; dopo la rifinitura (646 candidate) **4 pieghe,
1 incrocio, 470 mm** in tutto, cioè 425 mm di rete ordinaria e 45 mm di stacchi. La specie
più provata è l'**interasse** — la traslazione verticale gratuita — in tutte e due le fasi
(452 e 177 tentativi), come il pacchetto chiede.

## 6. Verifiche

- `ruff check src tests examples docs/collaudi/DRAW-005-R1/metriche.py`: nessun rilievo.
  `mypy --strict src tests examples`: nessun errore su 149 file.
- Suite completa (`python -m pytest -q`, sul codice finale): **1334 verdi, 22 parcheggiate,
  14 rosse apposta**, nessuna rossa, in 25 minuti e 35 secondi. Contro la prima consegna
  (1290 / 23 / 13): quarantaquattro verdi in più (le prove nuove), **una parcheggiata in meno
  e una rossa-apposta in più**, che sono la stessa prova — la qualità geometrica dell'impianto
  5, tornata a essere rossa apposta invece che nascosta da uno `skip`. Nessuna nuova `xfail`.
- Determinismo: due generazioni consecutive dallo stesso ingresso danno lo stesso modello
  completato **byte per byte**, lo stesso SVG di consegna byte per byte e la stessa impronta
  `92262dce…`.
- Preflight: un solo avviso, `SHEET_BARELY_FILLED` (foglio pieno al 31,6 %); il riempimento
  del foglio è fuori perimetro.

## 7. Osservazioni per il PM, che non decido io

- **La soglia della prova sulle colonne** (§4, terza voce) è l'unico numero di una prova
  esistente che ho toccato. La alternativa era lasciare che un raccordo scivolasse oltre il
  pezzo grosso che la sua tratta unisce, e la tavola ne pagava tre curve.
- **L'impianto 4 (ibrido) ha tre punti aperti** sulla sicurezza: la sua mandata comune non si
  trova camminando sul grafo, perché fra le macchine e la ripartizione c'è una valvola
  deviatrice, che non è un pezzo passante. Il motore chiede invece di indovinare, ed è il
  comportamento che il pacchetto prescrive; se il PM vuole che una deviatrice sia
  attraversabile, è una decisione sua e una regola in più.
- **Il foglio resta pieno al 31,6 %**: composizione e riempimento sono fuori perimetro.
- **La dipendenza della geometria dall'ordine delle connessioni** resta com'era (DRAW-005 §8):
  la prova di regressione della tavola 1 passa perciò dal JSON canonico, come la CLI.

## 8. Artefatti

| File | Cosa |
|---|---|
| `prima/…` | la tavola di consegna di DRAW-005 e il suo modello, rimisurati con lo strumento di oggi |
| `dopo/impianto1-completo.json` · `dopo/integrazioni.txt` | il modello completato e le 26 integrazioni con le fonti |
| `dopo/impianto1.{pdf,png,svg}` · `dopo/geometria.json` · `dopo/metriche.json` · `dopo/preflight.txt` | la tavola in modalità verifica |
| `dopo/consegna/…` | la tavola definitiva, con metriche e preflight |
| `dopo/diario.json` | il diario del ciclo: candidate provate e accettate |
| `prima-dopo.png` | il confronto visivo, sopra DRAW-005 e sotto DRAW-005-R1 |
| `metriche.py` | lo strumento, ora con le due reti separate |
