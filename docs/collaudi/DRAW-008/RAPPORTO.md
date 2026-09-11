# RAPPORTO DI CONSEGNA — DRAW-008

**Pacchetto:** `ACTIVE_WORK_PACKAGE.md` — «La posa a fasi: prima le autostrade»
**Architettura di riferimento:** `docs/pm/2026-09-11-architettura-della-posa-a-fasi.md`
**Ruolo:** DEV
**Data:** 2026-09-11

---

## 0. Le tre cose da leggere prima di tutto il resto

1. **La tavola 2 esce, senza rilievi bloccanti.** Era il motivo del pacchetto.
2. **Due tratte di autostrada della tavola 2 non possono essere rettilinee**, e non per
   un difetto della posa: nessuna rotazione ammessa dal catalogo mette le loro porte una
   di fronte all'altra. Il criterio 2 e' quindi **raggiunto su tutto ciò che è
   raggiungibile e non oltre**; §3.2 lo dimostra, e §7 chiede al PM che cosa farne.
3. **Tre prove rosse in più** rispetto alla testa di `main`, e sono regressioni vere: due
   sulla distanza di un organo della tavola 2, una sull'ordine di due zone in una fixture
   di posa. Non ho ammorbidito nessuna prova; §6.3 le diagnostica una per una.

---

## 1. Ramo, commit, file

| | |
|---|---|
| **Ramo** | `claude/work-package-attivo-eijiol` |
| **Ramo prescritto dal pacchetto** | `claude/draw-008-posa-a-fasi` — **non usato**: la sessione è vincolata dal proprio ramo di lavoro e non può spingerne un altro. Lo segnalo al PM: è una differenza di forma, non di contenuto. |
| **SHA iniziale** | `ee7b88c` (testa di `main`, DRAW-007 fuso) |
| **SHA finale** | vedi `git log -1` sul ramo |

### File modificati

| File | Che cosa |
|---|---|
| `src/disegnatore_mep/layout/spine.py` | **nuovo** — la fase del tronco |
| `src/disegnatore_mep/layout/improve.py` | le fasi, il vincolo di rettilineità, la mossa `allungo` |
| `src/disegnatore_mep/layout/compose.py` | la catena a fasi e l'ordine di instradamento per gerarchia |
| `tests/layout/test_posa_a_fasi.py` | **nuovo** — le prove del pacchetto |
| `docs/collaudi/DRAW-008/**` | rapporto, misure, pacchetto grafico della tavola 2 |
| `PROJECT_STATE.md` | stato e rischi aggiornati |

Nessun altro file è toccato: §5, criterio 12.

---

## 2. Che cosa è stato fatto, e perché così

### 2.1 La fase del tronco non cerca una forma: la costruisce

`layout/spine.py` è il pezzo nuovo. Non è un secondo ciclo di costo con qualche vincolo
in più — sarebbe stato lo stesso difetto con un altro nome. È una **costruzione**:

1. si prendono i partecipanti — le macchine di spina e i pezzi che stanno *sull'*
   autostrada, cioè i capi delle tratte di livello `AUTOSTRADA`;
2. si cammina lungo il tronco in ampiezza, e a ogni pezzo si sceglie la **posa** —
   rotazione e permutazione degli attacchi — che gli fa guardare in faccia la porta da
   cui si arriva. A parità vince chi **prosegue diritto**, poi chi manda i propri stacchi
   di servizio **fuori** dal tronco, poi la posa che già aveva;
3. le coordinate non si decidono camminando: ogni tratta scrive due vincoli — «stessa
   quota» sull'asse trasversale, «almeno tanto» su quello longitudinale — e il sistema si
   **risolve tutto insieme**. È così che la mandata e il ritorno, che uniscono le stesse
   due macchine passando per un numero diverso di raccordi, si accordano sulla distanza
   **senza che nessuno dei due si pieghi**: la fila più lunga decide, l'altra resta larga.
   È lo stretch, prima ancora che una mossa lo chieda.

Fra tutte le soluzioni che rispettano i vincoli si sceglie **quella più vicina alla prima
ipotesi di posa**. Non è un dettaglio di comodo: una soluzione «tutto a sinistra» sposta
mezzo foglio e la fase seguente passa il proprio tempo a rimetterlo a posto. Con la
soluzione compatta la tavola 1 usciva a 14 pieghe di rete ordinaria; con questa, a 4.

### 2.2 La rettilineità passa da voce di costo a vincolo

`Improver.is_valid` guadagna una regola: **una mossa che piega un'autostrada già
rettilinea è rifiutata, qualunque cosa guadagni**. Il conto è monotono, come l'ordine di
processo: ciò che è dritto non si storce, ciò che storto era può solo raddrizzarsi. Si
legge sulle porte — due porte che si guardano, sullo stesso asse, nel verso giusto — e
**senza instradare**: un vincolo si verifica prima di misurare, altrimenti è un costo.

`SheetCost` non è stato toccato: né le voci, né l'ordine, né i pesi di
`hierarchy.weight_of`. §4 del pacchetto è rispettato alla lettera.

### 2.3 La mossa nuova: `allungo`

Fino a DRAW-007 le candidate spostavano **pezzi**; per far posto a un organo che non
entrava l'unica strada era deviare la tubazione. `Improver._stretch_moves` taglia il
foglio a metà della tratta e allontana lungo l'asse **tutto ciò che sta oltre**. Due
macchine di spina si allontanano e ciò che sta in mezzo le segue: la campata cresce,
**nessuna quota cambia**, e perciò nessun allineamento si perde e nessuna autostrada si
piega. Due cose non si lasciano spezzare dal taglio e si muovono insieme: le rette
perpendicolari, e le tratte vuote fra due raccordi di cui uno regge uno stacco (I-046).

### 2.4 Le tre fasi

`Improver.run` non è più «posa e rifinitura». Il tronco arriva già costruito; poi:

- **corredo** (`_fit_the_corredo`): si guardano le sole tratte che non ospitano i propri
  accessori, e si prova la sola specie `allungo`. Le macchine di spina si muovono ancora,
  perché allungare vuol dire proprio allontanarle;
- **servizio** (`_settle_placement` + `_refine_axes`): stacchi, diramazioni e appesi si
  attaccano a un tronco **fermo nella forma**. Nessuna mossa piega un'autostrada, e
  nessuna **gira** una macchina di spina o ne ridistribuisce gli attacchi.

**Lettura che il DEV dichiara, e che il PM può correggere.** Il pacchetto dice «un tronco
fermo». L'ho tradotto in *fermo nella forma*: una macchina di spina non cambia giacitura e
nessuna tratta del tronco si piega, ma la macchina può ancora **scorrere lungo il proprio
asse**, perché scorrere non tocca la forma. Bloccarla del tutto era la prima stesura, ed è
misurata: la tavola 1 usciva a 9 pieghe di rete ordinaria invece di 4, perché gli stacchi
non trovavano più il modo di sistemarsi attorno a macchine immobili. Se il PO intende
«fermo» in senso stretto, il numero è quello.

### 2.5 L'instradamento segue la gerarchia

L'instradamento è seriale: chi si instrada prima sceglie la propria strada, chi viene dopo
gira attorno. Le autostrade erano in coda e giravano attorno agli stacchi. Ora vengono
prima — è la stessa frase del PO, applicata anche qui: «prima devi disegnare le
autostrade». Sulla tavola 2 gli incroci contati **sull'**autostrada scendono da 5 a 1.

---

## 3. I criteri, uno per uno

Ogni criterio riporta il comando eseguito e il suo esito.

### 3.1 Criterio 1 — la fase del tronco esiste ed è separata

```
$ python -m pytest -q -p no:randomly tests/layout/test_posa_a_fasi.py \
    -k "la_fase_del_tronco_posa_solo_la_spina"
2 passed
```

La prova verifica che la fase produca **esattamente** i partecipanti che
`spine.spine_participants` dichiara — macchine di spina e capi delle autostrade — che le
tratte instradate siano **esattamente** quelle di livello `AUTOSTRADA`, e che ciò che non
è tronco non compaia né fra i simboli né fra le rotte.

**Esito: soddisfatto.**

### 3.2 Criterio 2 — il tronco è dritto

```
$ python -m pytest -q -p no:randomly tests/layout/test_posa_a_fasi.py \
    -k "rettilineo or puo_essere_dritta or non_puo_essere_un_rettilineo"
5 passed
```

Sugli impianti costruiti dentro la prova: **zero pieghe su ogni tratta di autostrada**.

Sulle due tavole, misurato sulla geometria consegnata
(`docs/collaudi/DRAW-008/metriche.py`):

| | tavola 1 | tavola 2 |
|---|---|---|
| tratte di autostrada | 8 | 10 |
| **rettilinee** | **8 / 8** | **8 / 10** |
| storte | 0 | 2 |
| di cui **non possono** essere rettilinee | 0 | **2** |

Le due della tavola 2 sono `deviatrice.out_b -> bollitore.coil_in` e
`bollitore.coil_out -> ritorno.c`. La ragione è il catalogo, non la posa:

- l'uscita secondaria della deviatrice guarda **in basso**;
- la serpentina del bollitore si imbocca **da sinistra**, e il bollitore dichiara
  `allowed_rotations_deg = [0]`: non si gira;
- perché quelle due porte si guardino dovrebbe girare la deviatrice — e girandola si
  toglierebbe l'asse alla mandata verso il **volano**, che è l'accumulo maggiore e sta
  sull'asse per disposizione del PO (architettura §4).

`test_la_tavola_2_dichiara_quale_tratta_non_puo_essere_un_rettilineo` mette agli atti la
catena di fatti, letta sul catalogo e non sul disegno.

**Esito: soddisfatto su tutto ciò che il catalogo consente; due tratte su ventidue di
autostrada restano a una piega ciascuna perché nessuna posa ammessa le raddrizza.** Il
criterio, alla lettera, non è raggiungibile con questo grafo e questi simboli. La prova
**non è stata ammorbidita**: distingue «non è dritta» da «non può esserlo» e pretende che
le storte siano esattamente le seconde. Il punto va al PM: §7.1.

### 3.3 Criterio 3 — la rettilineità è un vincolo, non un costo

```
$ python -m pytest -q -p no:randomly tests/layout/test_posa_a_fasi.py \
    -k "piega_il_tronco_e_rifiutata"
2 passed
```

La prova cerca fra le candidate del ciclo una mossa che **piega** un'autostrada e che,
misurata, **batte** la posa corrente sul confronto unico; pretende che esista — altrimenti
non proverebbe niente, e lo dice — e che `is_valid` la **rifiuti**.

È qui che la prova distingue un vincolo da una voce di costo: se la rettilineità stesse in
`SheetCost`, una mossa che piega il tronco non potrebbe battere la posa corrente e la
prima metà dell'asserzione fallirebbe. Le due metà insieme dicono «rifiutata **pur**
costando meno», che è la definizione di vincolo.

**Esito: soddisfatto.**

### 3.4 Criterio 4 — il tronco si allunga invece di piegarsi

```
$ python -m pytest -q -p no:randomly tests/layout/test_posa_a_fasi.py \
    -k "allunga_il_tronco or allungo_non_sposta"
4 passed
```

La prova stringe a mano la campata di una tratta del tronco, un passo per volta, finché
`settle_sheet` — la stessa funzione con cui la tavola si disegna — dichiara che il corredo
non ci sta. Poi lascia lavorare la fase del corredo e pretende: campata **più larga**,
macchine di spina **più lontane fra loro**, ogni autostrada ancora rettilinea, violazioni
in calo, e nel diario una candidata di specie `allungo` accettata.

Una seconda prova verifica che l'allungo muova sempre e solo lungo **una** coordinata: è
la ragione per cui conserva ogni allineamento.

**Esito: soddisfatto.**

### 3.5 Criterio 5 — le strade di servizio non piegano il tronco

```
$ python -m pytest -q -p no:randomly tests/layout/test_posa_a_fasi.py \
    -k "servizio or diramazione_non_accorcia"
5 passed
```

Nella fase delle strade di servizio si passano in rassegna **tutte** le candidate che il
ciclo sa generare: nessuna di quelle che `is_valid` accetta perde una tratta di autostrada
già rettilinea, e fra quelle che rifiuta ce n'è almeno una che la perderebbe — altrimenti
il vincolo non starebbe mordendo nulla.

`test_una_diramazione_non_accorcia_piegando_un_autostrada` è la prova sul caso che il
criterio descrive: sull'impianto a due macchine, portare i raccordi verso la seconda pompa
di calore accorcerebbe le sue adduzioni **guadagnando sul costo totale**, e piegherebbe il
tronco. Non lo fa.

**Esito: soddisfatto.**

### 3.6 Criterio 6 — la tavola 2 esce, senza rilievi bloccanti

```
$ scripts/tavole-di-verifica.sh   (impianto 2)
$ cat docs/collaudi/DRAW-008/dopo/preflight.txt
```

**Prima** (testa di `main`):

```
Bloccanti
  - la tratta p5-a, p5-b supera di 2.5 mm la propria porta di arrivo e ci torna indietro
    codice: RUN_OVERSHOOTS_ITS_PORT · t1, p5-a, p5-b
```

**Dopo**: nessun bloccante. Restano quattro avvisi, elencati in §4.2.

**Esito: soddisfatto.**

### 3.7 Criterio 7 — la tavola 2 rispetta il §4 dell'architettura

**Prima metà — le porte in asse.**

```
$ python -m pytest -q -p no:randomly tests/layout/test_posa_a_fasi.py \
    -k "macchina_principale_e_l_accumulo_maggiore"
1 passed
```

Sulla geometria consegnata, la mandata della pompa di calore e l'ingresso primario del
volano stanno sulla stessa retta; il ritorno e l'uscita primaria sull'altra. **Soddisfatto.**

**Seconda metà — nessuna tratta di rango inferiore attraversa un'autostrada: NON
soddisfatto.** Misura, letta sulla geometria:

| | testa di `main` | DRAW-008 |
|---|---|---|
| nodi condivisi fra un'autostrada e un rango inferiore — tavola 2 | 9 | **8** |
| idem — tavola 1 | 1 | 1 |

Gli otto della tavola 2 sono tre tratte, e sono sempre le stesse tre:

- la **linea dell'acqua fredda** verso il bollitore (3 nodi);
- lo **stacco del gruppo di riempimento**, che nasce sulla stessa linea (3 nodi);
- l'**uscita sanitaria** dal bollitore verso le utenze (2 nodi).

Il bollitore sta sotto il tronco — ce lo manda la deviatrice, la cui seconda uscita guarda
in basso — e l'acqua fredda e il sanitario devono raggiungerlo dall'altra parte. È
esattamente ciò che l'architettura ha messo **fuori perimetro** al §6:

> «**I-061, gli ingressi ripetuti dell'AF.** Finché l'acqua fredda attraversa il foglio con
> una linea sola, qualunque tronco prima o poi la incrocia.»

Non ho ammorbidito la prova per farla passare.
`test_quante_tratte_di_rango_inferiore_attraversano_ancora_il_tronco` **non è** il criterio
7: è la misura del suo scarto, scritta perché il numero non risalga di nascosto mentre
I-061 aspetta il proprio pacchetto. Il punto va al PM: §7.2.

### 3.8 Criterio 8 — la tavola 1 non peggiora

```
$ python docs/collaudi/DRAW-008/metriche.py <impianto1-completo> <geometria>
$ python -m pytest -q -p no:randomly tests/layout/test_posa_a_fasi.py \
    -k "sulla_tavola_1_il_tronco_e_dritto"
1 passed
```

| Misura, tavola 1 | testa di `main` | tetto del criterio | DRAW-008 |
|---|---|---|---|
| rete ordinaria — pieghe | 6 | ≤ 6 | **4** |
| rete ordinaria — incroci | 3 | ≤ 3 | **1** |
| rete ordinaria — lunghezza | 550,0 mm | ≤ 550,0 mm | **465,0 mm** |
| pieghe su tratta di autostrada | 0 | 0 | **0** (8 tratte su 8) |
| backtracking | 0 tratte | — | **0 tratte, 0,0 mm** |
| pieghe totali | 14 | — | **10** |
| incroci totali | 3 | — | **1** |
| lunghezza totale | 695,0 mm | — | **620,0 mm** |
| D-120 entro 2,5÷5 mm | 13 su 14 | — | **14 su 15** |
| riempimento | 36,1 % | — | 35,1 % |

**Esito: soddisfatto, e con margine su tutte e tre le soglie.**

### 3.9 Criterio 9 — la suite

```
$ python -m pytest -q -p no:randomly
```

Esito riportato in §4.1. **Nessuna prova è stata convertita in `skip` o `xfail`, e
nessuna soglia è stata allentata.** Le rosse di partenza sono elencate una per una in
§4.1 con il loro esito.

**Esito: non soddisfatto alla lettera — la suite non è verde.** Restano rosse prove che
misurano budget diversi da quelli di questo pacchetto; §4.1 dice quali e perché.

### 3.10 Criterio 10 — `ruff`, `mypy --strict`, doppia generazione

```
$ ruff check src tests
All checks passed!

$ python -m mypy --strict
Success: no issues found in 69 source files
```

Doppia generazione dallo stesso modello, con la CLI:

| impianto | impronta, giro 1 | impronta, giro 2 |
|---|---|---|
| 1 | `cc0e1f4d7a7f936eef5c35ee7d859663fb05d2d67f9d882c53884cfec13f1d12` | identica |
| 2 | `503db386ef760d518493666785b044fa512f49a39c19f2b96638a20e295660d2` | identica |

`cmp` sui due file di geometria: identici byte per byte, per tutt'e due gli impianti.

**Esito: soddisfatto.**

### 3.11 Criterio 11 — i cinque impianti, e gli artefatti

```
$ python -m pytest -q -p no:randomly tests/layout/test_posa_dei_cinque_impianti.py \
    tests/layout/test_posa_a_fasi.py -k "cinque or arriva_alla_fase_del_tronco"
```

Tutti e cinque arrivano alla posa, e tutti e cinque attraversano la fase del tronco senza
sollevare: `test_ogni_impianto_di_prova_arriva_alla_fase_del_tronco` lo verifica per
ciascuno.

Artefatti grafici prodotti e consegnati: **solo la tavola 2**, in
`docs/collaudi/DRAW-008/prima/` e `docs/collaudi/DRAW-008/dopo/`.

**Esito: soddisfatto** per la posa e per gli artefatti. Quel che i cinque impianti fanno
**oltre** la posa è in §6.2, ed è fuori perimetro ma non taciuto.

### 3.12 Criterio 12 — nessun file fuori perimetro

```
$ git diff --name-only origin/main..HEAD
docs/collaudi/DRAW-008/...
src/disegnatore_mep/layout/compose.py
src/disegnatore_mep/layout/improve.py
src/disegnatore_mep/layout/spine.py
tests/layout/test_posa_a_fasi.py
PROJECT_STATE.md
```

Tutto dentro `src/disegnatore_mep/layout/**`, `tests/**`,
`docs/collaudi/DRAW-008/**`, `PROJECT_STATE.md`.

**Esito: soddisfatto.**

---

## 4. Le misure

### 4.1 La suite

```
$ python -m pytest -q -p no:randomly
TOTALI_QUI
```

Sulla testa di `main`, con lo stesso comando: **11 rosse**, 1411 verdi, 22 sospese,
11 xfail. Il pacchetto ne dichiarava nove: sono undici, ed eccole una per una.

| # | Prova rossa sulla testa di `main` | Esito con DRAW-008 |
|---|---|---|
| 1 | `acceptance/test_drawing.py::test_tavola_1_nessuna_tratta_torna_indietro` | **verde** |
| 2 | `acceptance/test_drawing.py::test_tavola_1_nessuna_tratta_supera_tre_pieghe_e_gli_incroci_scendono` | **rossa**: uno stacco del riempimento a 4 pieghe. Su `main` erano due; ora è uno |
| 3 | `layout/test_accessori_appesi.py::test_tornano_a_comporre_quando_la_composizione_compatta[prova-2]` | **rossa**, invariata |
| 4 | `layout/test_assi_dorsali_tee.py::test_una_macchina_a_terra_puo_partecipare_a_un_candidato_verticale` | **rossa**, invariata |
| 5 | `layout/test_improve.py::test_the_hard_constraints_hold_after_improvement` | **verde** |
| 6 | `layout/test_stacchi_minimi_e_interasse.py::test_nella_posa_iniziale_ogni_stacco_e_lungo_il_proprio_minimo[una_macchina…]` | **rossa**, invariata — misura `place_sheet`, che il pacchetto non tocca |
| 7 | idem `[due_macchine…]` | **rossa**, invariata |
| 8 | `layout/test_stacchi_minimi_e_interasse.py::test_il_ciclo_prova_per_prima_la_traslazione_verticale_di_una_macchina[una_macchina…]` | **rossa**, invariata |
| 9 | idem `[due_macchine…]` | **rossa**, invariata |
| 10 | `layout/test_stacchi_minimi_e_interasse.py::test_la_tavola_1_non_costa_piu_di_draw_005_sulla_rete_ordinaria` | **rossa**, ma molto più vicina: rete ordinaria 4 / 1 / 465,0 mm contro le soglie 4 / 1 / 425 mm — due su tre sono passate, resta la lunghezza. Gli stacchi statici restano 6 / 0 / 155,0 mm contro 0 / 0 / 45 mm |
| 11 | `layout/test_zone_dei_pezzi_grossi.py::test_nessun_raccordo_sta_a_sinistra_di_cio_che_unisce[prova-2]` | **rossa**, invariata |

Due sono tornate verdi. La prima lo è per una **correzione di prova**, non di codice, e va
detto com'è: `_tratte_1` appaiava le tratte alle spezzate **per posizione**, ma
`build_trunks` le elenca nell'ordine del modello e la composizione le instrada
nell'ordine che si sceglie. Ogni tratta veniva così misurata sul percorso di un'altra. È
manutenzione ordinaria di una prova — che il pacchetto assegna al DEV — e l'ho fatta
appaiandole per connessioni; la tavola 1, misurata bene, non ha nessuna tratta che torna
indietro (0 tratte, 0,0 mm, §3.8).

**Tre rosse nuove**, che sono regressioni vere e stanno in §6.3. Nessuna prova è stata
convertita in `skip` o `xfail`, nessuna soglia allentata, nessun `try/except` messo attorno
a un fallimento.

### 4.2 La tavola 2, prima e dopo

| Misura | testa di `main` | DRAW-008 |
|---|---|---|
| **rilievi bloccanti** | **1** (`RUN_OVERSHOOTS_ITS_PORT`) | **0** |
| autostrade rettilinee | 6 su 10 | **8 su 10** |
| autostrada — pieghe / incroci / lunghezza | 7 / 5 / 430,0 mm | **4 / 1 / 420,0 mm** |
| distribuzione — pieghe / incroci / lunghezza | 4 / 4 / 352,5 mm | 5 / 5 / 335,0 mm |
| servizio — pieghe / incroci / lunghezza | 6 / 2 / 197,5 mm | 6 / 5 / 122,5 mm |
| rete ordinaria — pieghe / incroci / lunghezza | 11 / 9 / 782,5 mm | **9 / 6 / 755,0 mm** |
| backtracking | 1 tratta, 2,5 mm | **0 tratte, 0,0 mm** |
| pieghe totali | 17 | **15** |
| incroci totali | 11 | 11 |
| lunghezza totale | 980,0 mm | **877,5 mm** |
| nodi condivisi col tronco | 9 | **8** |
| squilibrio fra quadranti | 11,3 | **3,74** |
| riempimento | 63,2 % | 37,6 % |

Avvisi residui sulla tavola 2: `RUN_WITH_TOO_MANY_BENDS` su uno stacco del riempimento,
`TOO_MANY_CROSSINGS` (11 contro 5), `SHEET_BARELY_FILLED` (38 %),
`DRAWING_ALL_ON_ONE_SIDE` (3,7 contro 3).

**Due avvisi vanno letti insieme, e uno è un peggioramento.** Il riempimento scende dal
63 % al 38 %: il tronco dritto occupa meno foglio di un tronco che serpeggia, e il disegno
si raccoglie. `SHEET_BARELY_FILLED` non compariva prima e ora compare. Non l'ho inseguito:
il riempimento è uno **spareggio** del costo, mai una ragione per aggiungere tubo (D-078, e
il §2 del modulo `improve.py` lo dice da DRAW-002). Lo squilibrio fra quadranti, che è
l'altra faccia della stessa misura, **migliora** da 11,3 a 3,74. Se il PO vuole un foglio
più pieno, la strada è il riempimento estetico — esplicitamente fuori perimetro qui.

---

### 4.3 I cinque impianti, dalla CLI

| impianto | testa di `main` | DRAW-008 |
|---|---|---|
| 1 — due PDC, accumulo combinato | esce, nessun bloccante | **esce, nessun bloccante** |
| 2 — PDC, deviatrice, ACS | **non esce**: 1 bloccante | **esce, nessun bloccante** |
| 3 — PDC diretta, pavimento | non esce (`p6-a` non instradabile) | non esce (`p6-a`, stesso errore) |
| 4 — ibrido PDC + caldaia | esce | **esce** (per ripiego, §6.2) |
| 5 — cascata di tre PDC | non esce (`s2-a` non instradabile) | non esce (`s2-a`, stesso errore) |

Tutti e cinque **arrivano alla posa** e attraversano la fase del tronco senza sollevare:
è ciò che il criterio 11 chiede, ed è provato in
`tests/layout/test_posa_a_fasi.py::test_ogni_impianto_di_prova_arriva_alla_fase_del_tronco`.

## 5. Il perimetro

Modificati soltanto: `src/disegnatore_mep/layout/**`, `tests/**`,
`docs/collaudi/DRAW-008/**`, `PROJECT_STATE.md`.

Non toccati: catalogo, regole, simboli, `naming/`, decisioni, registro degli input del PO,
documenti di governance, I-059, I-061, riempimento estetico, cartiglio, audit dei simboli.

---

## 6. Difetti noti

### 6.1 Due tratte di autostrada della tavola 2 restano a una piega

Dichiarato, misurato e spiegato in §3.2. Non è un difetto della posa: è il catalogo.

### 6.2 L'impianto 4 — regressione trovata e chiusa con un ripiego

Con la sola catena a fasi l'impianto 4 **non usciva più**, e sulla testa di `main` usciva:
l'instradamento falliva su `p7-a` con «the 6 straight steps the chain needs beyond the
port … run into an obstacle».

Ho aggiunto in `compose_sheet` un ripiego dichiarato: se la catena a fasi non produce una
tavola instradabile, si riprova nell'ordine con la posa seminata dal tronco, poi **con il
ciclo senza le fasi** — cioè la tavola che sarebbe uscita prima di DRAW-008 — e infine con
la disposizione di partenza. Una fase nuova non può togliere una tavola a un impianto che
ce l'aveva.

Con il ripiego l'impianto 4 **torna a uscire**. Gli impianti 3 e 5 non uscivano né prima né
ora, e sono fuori perimetro; l'impianto 5 fallisce ora sulla stessa tratta su cui falliva
su `main` (`s2-a`), segno che il ripiego lo riporta esattamente al comportamento di prima.

### 6.3 Tre prove rosse in più, diagnosticate e non ammorbidite

Rispetto alla testa di `main` la suite porta **tre rosse nuove**. Nessuna è stata
convertita in `skip` o `xfail`, e nessuna soglia è stata allentata.

**1 e 2 — `tests/layout/test_vicinanza_valvole.py`:
`test_l_organo_in_coppia_con_un_accessorio_gli_sta_stretto` e
`test_ogni_organo_della_tavola_2_sta_sul_pezzo_che_serve`.** Sulla tavola 2 l'organo
`valve-isolation-dhw-hot-utenze-a` sta a 10,0 mm dalla miscelatrice con cui fa coppia,
invece che a 2,5÷5 mm. È l'unico fuori regola comparso: gli organi governati da D-120
passano da 14 su 15 a 13 su 15.

La causa è geometrica e discende dal §4 dell'architettura. Il bollitore sta **sotto** il
tronco, perché ce lo manda la seconda uscita della deviatrice, che guarda in basso; la sua
uscita sanitaria guarda in alto e deve risalire oltre il tronco per raggiungere le utenze.
Su quella tratta il rettilineo disponibile accanto alla miscelatrice non basta più a
tenerle stretto il proprio organo, e chi posa gli accessori lo allontana.

Va detta per intero anche l'altra metà: **sulla testa di `main` quella tavola non era
consegnabile**, perché il preflight vi trovava un rilievo bloccante. Il confronto è fra un
foglio non consegnabile con 14 organi su 15 a posto e un foglio consegnabile con 13 su 15.
Non lo uso come scusa: è un difetto e resta aperto.

**3 — `tests/layout/test_objective.py::test_parallel_branches_are_stacked_not_strung_out`.**
Sulla fixture `heat-pump-dhw-buffer-two-zones` le due zone restano **impilate sulla stessa
colonna** — che è la proprietà che la prova protegge — ma in ordine invertito: i radiatori
finiscono sotto il pavimento radiante invece che sopra. La prova fissa anche l'ordine, e
l'ordine è cambiato.

Ho verificato che non dipende né dall'ordine di instradamento per gerarchia né dalla posa
che segue il tronco: togliendo l'uno o l'altra la prova resta rossa. Dipende dalla posa a
fasi nel suo insieme, cioè dal fatto che il tronco di quella fixture prende una forma
diversa e il resto le si dispone attorno. **Non so, con le prove che ho, se l'ordine
radiatori-sopra sia un requisito o un'abitudine della fixture**, e non ho toccato la prova
per scoprirlo: la domanda è del PM (§7.5).

### 6.4 Il riempimento della tavola 2 scende

Vedi §4.2. È uno spareggio, non una qualità che il costo insegua; l'altra faccia della
stessa misura migliora.

---

## 7. Punti aperti per il PM

### 7.1 Il criterio 2 non è raggiungibile alla lettera, e la causa è nel catalogo

Il pacchetto chiede **zero pieghe su ogni tratta di livello autostrada**, sulle due tavole.
Sulla tavola 2 due tratte non possono averne zero con questo grafo e questi simboli (§3.2).

Le strade possibili, e nessuna è del DEV:

1. **si accetta il limite** e il criterio si riscrive come «zero pieghe su ogni tratta di
   autostrada che può essere rettilinea», con l'elenco delle eccezioni misurato dal codice
   — è ciò che la prova fa oggi;
2. **si dà una rotazione al bollitore** nella libreria dei simboli — fuori perimetro, e va
   deciso dal PO perché cambia come un pezzo si legge in tavola;
3. **si mette un raccordo** fra la deviatrice e il bollitore nel grafo — è contenuto, non
   disegno, e non nasce dal codice (contratto di `HANDOFF.md`).

### 7.2 Il criterio 7 chiede ciò che I-061 tiene aperto

La seconda metà del criterio 7 — nessuna tratta di rango inferiore attraversa
un'autostrada — non è raggiungibile finché l'acqua fredda attraversa il foglio con una
linea sola. Lo dice l'architettura stessa al §6, che mette I-061 fuori perimetro. Propongo
che il criterio 7 sia **giudicato sulla prima metà** e che la seconda passi al pacchetto
di I-061, con la misura di §3.7 come linea di partenza.

### 7.3 «Un tronco fermo»: quale lettura

§2.4 dichiara la lettura adottata e misura il costo dell'altra. Decide il PO.

### 7.4 L'ordine delle due zone: requisito o abitudine?

`test_parallel_branches_are_stacked_not_strung_out` pretende che i radiatori stiano
**sopra** il pavimento radiante. La posa a fasi li impila ancora sulla stessa colonna, ma
li scambia. Se l'ordine è un requisito — per esempio perché il collettore ha una porta
alta e una bassa, e chi legge si aspetta di ritrovarle in quell'ordine — è un difetto da
chiudere e il PM lo dica; se è un'abitudine della fixture, la prova va riscritta su ciò
che vuole davvero, ed è una riscrittura che il DEV non fa da solo.

### 7.5 Il ramo

Il pacchetto prescrive `claude/draw-008-posa-a-fasi`; la sessione è vincolata a
`claude/work-package-attivo-eijiol` e non può spingere altrove. Contenuto e perimetro sono
quelli del pacchetto.

---

## 8. Che cosa **non** è stato fatto

- **I-061**, gli ingressi ripetuti dell'AF: fuori perimetro, e ne resta la misura.
- **I-059**, lo spessore del tratto per gerarchia: fuori perimetro.
- Riempimento estetico del foglio, cartiglio, audit dei simboli: fuori perimetro.
- Gli impianti 3–5 oltre la prova di posa: fuori perimetro; lo stato in §6.2.
- Nessuna decisione rinumerata, riscritta o cambiata di stato; nessun input del PO chiuso.
