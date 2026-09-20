# DRAW-015 — Il revisore, e il repository che lo regge

**Data:** 20 settembre 2026 · **Agente unico** (D-147), con quattro agenti paralleli in
sessione (D-152) · **Base:** `8b08233`, la testa di `origin/main`

---

## Le tavole, per prime (D-146)

**Escono tutte e cinque.** È la prima volta nel progetto.

| | tavola | formato | tratte | **cedute** | **bloccanti** | pieghe | incroci |
|---|---|---|---|---|---|---|---|
| impianto 1 — due PDC e accumulo combinato | [`tavole/tavola-1-DAL-PIANO.pdf`](tavole/tavola-1-DAL-PIANO.pdf) | A2 | 21 | **0** | **0** | 8 | 1 |
| impianto 2 — PDC con deviatrice e ACS | [`tavole/tavola-2-DAL-PIANO.pdf`](tavole/tavola-2-DAL-PIANO.pdf) | A2 | 23 | **0** | **0** | 9 | 2 |
| impianto 3 — PDC diretta su pavimento | [`tavole/tavola-3-DAL-PIANO.pdf`](tavole/tavola-3-DAL-PIANO.pdf) | A2 | 22 | **0** | **1** | 9 | 3 |
| impianto 4 — ibrido PDC + caldaia | [`tavole/tavola-4-DAL-PIANO.pdf`](tavole/tavola-4-DAL-PIANO.pdf) | A2 | 25 | **0** | **0** | 14 | 3 |
| impianto 5 — cascata di tre PDC | [`tavole/tavola-5-DAL-PIANO.pdf`](tavole/tavola-5-DAL-PIANO.pdf) | A1 | 54 | **0** | **0** | 33 | 14 |

**L'unico rilievo bloccante è sull'impianto 3**, ed è strutturale — §6.

Il prima e il dopo del revisore sono in [`anello/`](anello/): `impianto-4-giro0.pdf` e
`impianto-4-giro1.pdf`, su un piano **guastato apposta** perché l'anello si vedesse girare.

Comando, e si riproduce intero:

```
$ scripts/tavole-dal-piano.sh
prova-1-due-pdc-accumulo-combinato   ESCE (uscita 0)  21 tratte, 0 cedute  bloccanti 0  rilievi 10
prova-2-pdc-deviatrice-acs           ESCE (uscita 0)  23 tratte, 0 cedute  bloccanti 0  rilievi 7
prova-3-pdc-diretta-pavimento        ESCE (uscita 2)  22 tratte, 0 cedute  bloccanti 1  rilievi 7
prova-4-ibrido-pdc-caldaia           ESCE (uscita 0)  25 tratte, 0 cedute  bloccanti 0  rilievi 12
prova-5-cascata-tre-pdc              ESCE (uscita 0)  54 tratte, 0 cedute  bloccanti 0  rilievi 27
```

### Il confronto con `main`, misurato

Su `main` le cinque tavole escono per la via ordinaria, cioè **con il solutore**
(`esito-via-ordinaria-su-main.txt`):

| | su `main`, col solutore | qui, dal piano |
|---|---|---|
| impianto 1 | 21 tratte, **0 cedute** | 21 tratte, **0 cedute** |
| impianto 2 | 23 tratte, **0 cedute** | 23 tratte, **0 cedute** |
| impianto 3 | 22 tratte, **0 cedute** | 22 tratte, **0 cedute** |
| impianto 4 | 25 tratte, **0 cedute** | 25 tratte, **0 cedute** |
| impianto 5 | 54 tratte, **6 cedute** | 54 tratte, **0 cedute** |

**Nessuno peggiora, e il quinto migliora di sei tratte.** Il quinto è l'impianto su cui il
PO aveva detto «quel nugolo di tubi invece di disegnare un cavolo di collettore dritto in
verticale».

---

## 1. Quello che ho guardato, e che i numeri non dicono

**Le cinque tavole si leggono**, e non è una frase: le due primarie sono due rette che
attraversano il foglio su 1, 2, 3 e 4; i generatori stanno a sinistra e incolonnati; la tre
vie sta **in linea** sulla mandata invece che sulla piega; sul 5 i due collettori della
cascata sono verticali e dritti. Sull'impianto 2 la deviatrice, il volano e il bollitore
stanno sulle stesse due quote, e la linea le passa dentro.

**Quello che resta storto, e lo dico io guardando, non un numero:**

1. **Il disegno è ancora una fascia, e adesso è una fascia larga.** Su tutte e cinque il
   terzo inferiore del foglio è vuoto. `DRAWING_ALL_ON_ONE_SIDE` lo dice con un numero
   (5,2 sull'1, 7,6 sul 2, 3,9 sul 4), ma il numero non rende quanto si vede: la tavola
   sembra un nastro appoggiato in alto. **È il primo difetto aperto del pianificatore**
   (D3), ed è mio, non del motore.
2. ~~**I confini di rete finiscono lontanissimi.**~~ **Trovato guardando, e chiuso** — §10bis.
   Il prelievo ACS stava all'estrema destra con una linea che attraversava mezzo foglio
   vuoto: **205, 502 e 152 mm** su 2, 3 e 4. Era una conseguenza di A1 — «la distribuzione
   sta a destra» — applicata da me a un pezzo che **non ha una posizione propria** (I-061,
   D-145). Adesso stanno fra **17,5 e 50 mm**. La cosa che conta non è la correzione: è che
   **nessun numero me l'aveva detto**, e da lì viene **D-158**.
3. **Sull'impianto 5 i quattordici incroci si vedono**, e stanno quasi tutti dove il
   circuito sanitario attraversa i tre secondari.
4. **Una tavola mi sembra sbagliata e i numeri dicono che va bene**, ed è il rilievo che
   questo progetto chiede di portare per primo: sull'impianto 5 la catena che attraversa il
   **collettore verticale che B3 pretende** fa due pieghe, e B1 la accusa perché
   `turns_allowed` vale zero. Qui il disegno è giusto e la regola ha torto. §6.

---

## 2. Il revisore — quanti giri sono serviti

**La risposta secca, e non è quella che speravo: sui cinque piani consegnati, zero.**

| impianto | giri di revisione serviti | giri provati | perché si è fermato |
|---|---|---|---|
| 1 | **0** | 1 | un giro ha peggiorato la tavola su `bloccanti, pieghe, incroci` |
| 2 | **0** | 0 | nessuna cura si applica ai rilievi che restano (`DRAWING_ALL_ON_ONE_SIDE`, `HIGHWAY_IS_NOT_STRAIGHT`) |
| 3 | **0** | 1 | un giro ha peggiorato la tavola su `avvisi, pieghe, incroci` |
| 4 | **0** | 1 | la correzione ha tolto la tavola: il piano corretto non si instrada più |
| 5 | **0** | 1 | un giro ha peggiorato la tavola su `avvisi, pieghe` |

**Perché zero, e non è un difetto del revisore.** I cinque piani li ho composti **con le
regole in mano**, quindi quello che resta sono le violazioni **strutturali** di §6, che
nessuno spostamento di un pezzo chiude. Il revisore ci prova, misura che ha peggiorato, si
ferma e lo dice. È esattamente il criterio 3, e in tutti e cinque i casi ha funzionato.

**E l'anello gira davvero, quando c'è qualcosa da curare.** Sul piano dell'impianto 4
guastato apposta — il radiatore portato dentro la fascia dello scambiatore —
(`anello/impianto-4-guasto.json`):

```
— giro 0: bloccanti 0, cedute 0, violazioni 7, avvisi 14, pieghe 14, incroci 3
  > radiatori: (310.0, 98.5) -> (315.0, 98.5) — regola A1 [PIECE_OUTSIDE_ITS_BAND]
— giro 1: bloccanti 0, cedute 0, violazioni 5, avvisi 12, pieghe 14, incroci 3
  > caldaia: (30.0, 221.0) -> (30.0, 96.0) — regola B1 [HIGHWAY_IS_NOT_STRAIGHT]
  > deviatrice-caldaia: (120.0, 226.0) -> (120.0, 101.0) — regola B1 [HIGHWAY_IS_NOT_STRAIGHT]
— giro 2: la correzione ha tolto la tavola
Si e' fermato perche': la correzione ha tolto la tavola: il piano corretto non si instrada
piu' (run p4-a ... run into an obstacle at (50, 36)). Si consegna il giro precedente
Giri di revisione serviti: 1 (su 2 provati) · ha migliorato: si
```

**Un giro**, violazioni da 7 a 5, nessuna misura peggiorata, e l'arresto nominato. Le due
tavole sono in `anello/`.

### Due difetti del revisore, trovati guardando l'esito e chiusi

1. **Contava due volte lo stesso difetto.** Da quando il preflight sa che cos'è
   un'autostrada, `RUN_WITH_TOO_MANY_BENDS` dice la stessa cosa di
   `HIGHWAY_IS_NOT_STRAIGHT` su una catena di una tratta sola: il punteggio era gonfio e una
   tavola con un difetto ne mostrava due. Sull'impianto 1 le violazioni erano 8, e sono 4.
2. **Smontava quello che era a posto.** La cura di B1 sulla tratta `radiatori -> accumulo`
   spostava l'accumulo di 15 mm e **piegava le due primarie**, che erano due rette: lo
   squilibrio fra i quadranti passava da 5,2 a 11,5. Adesso una catena già nella propria
   forma è intoccabile — con un'eccezione dichiarata, **A1 viene prima di B1**, perché è
   l'ordine in cui il PO ha dettato le regole.

---

## 3. I criteri, uno per uno

Ogni criterio si chiude con il comando eseguito e il suo output. Dove non è raggiunto, è
scritto qui e non altrove.

| | criterio | esito |
|---|---|---|
| 1 | Il revisore gira su almeno tre impianti, con la tavola prima e dopo | **raggiunto** — gira su tutti e cinque; su nessuno migliora, ed è scritto in §2 per primo. Il prima/dopo con un miglioramento vero è sull'impianto 4 guastato |
| 2 | Ogni correzione porta il nome della regola | **raggiunto** — `Correzione.regola`, `tests/piano/test_revisore.py::test_ogni_correzione_porta_il_nome_della_regola` su tutt'e due i piani, più `test_ogni_cura_conosciuta_ha_la_propria_regola` |
| 3 | Il revisore non peggiora in silenzio | **raggiunto** — §2, e quattro prove: `test_si_ferma_sempre_dicendo_perche`, `test_consegna_il_giro_migliore_e_mai_uno_peggiore`, `test_un_giro_che_peggiora_nomina_le_misure_peggiorate`, `test_non_smonta_una_catena_gia_dritta` |
| 4 | Le quattro regole di D-154 hanno ciascuna un controllo, e una tavola su cui si vede | **raggiunto** — §4 |
| 5 | Le due tavole composte restano a zero, dalla CLI | **raggiunto** — impianto 1 e 5: 0 bloccanti, 0 cedute, dal comando `disegnatore-mep piano` |
| 6 | I cinque impianti producono ancora una tavola, e nessuno peggiora | **raggiunto e migliorato** — tutti e cinque, e il quinto passa da 6 tratte cedute a 0 |
| 7 | Nessun percorso vigente chiama più il solutore | **raggiunto** — §5, con cinque prove in `tests/layout/test_il_solutore_e_fuori.py` |
| 8 | Ogni file di `tests/layout/` ha la sua categoria, zero `skip`/`xfail` nuovi, saldo non peggiore | **§7** |
| 9 | Nessun documento in terzo stato, citazione D-119 corretta ovunque | **raggiunto** — §8 |
| 10 | Il formato del piano è documentato e validato | **raggiunto** — §9 |

---

## 4. Le quattro regole del PO sono diventate quattro controlli (criterio 4)

`src/disegnatore_mep/validation/regole.py`, una funzione per regola, tutte `warning`: una
violazione di regola è un **difetto del piano da correggere dal revisore**, non un motivo
per rifiutare la tavola — il cancello di consegna resta il preflight (D-063).

| | codice | che cosa misura | dove si vede |
|---|---|---|---|
| **A1** | `PIECE_OUTSIDE_ITS_BAND` | ogni fascia occupa l'intervallo in x dei propri pezzi; violazione = un pezzo dentro l'intervallo di un'altra | `anello/impianto-4-giro0.pdf`, il radiatore nella fascia dello scambiatore |
| **B1** | `HIGHWAY_IS_NOT_STRAIGHT` | le pieghe della **catena intera** — dentro le tratte **più** i cambi di giacitura sui crocevia — contro `turns_allowed` | impianto 1: «la tratta `s3-a, s3-b` piega 4 volte, e su un'autostrada le pieghe ammesse sono 1» |
| **B3** | `PARALLEL_MACHINES_WITHOUT_A_COLLECTOR` | i nodi del collettore che serve macchine in parallelo stanno sulla stessa verticale, e le tratte fra loro sono verticali | impianto 5: i collettori veri **passano**; la violazione si vede su una variante con un nodo spostato di 40 mm |
| **B4** | `INLINE_ORGAN_BREAKS_THE_RUN` | le due tratte attaccate alle porte su facce opposte hanno la stessa giacitura | impianto 5, il `ricircolo` |

**B1 chiudeva il difetto che ha generato D-151**, e adesso è chiuso: `layout/autostrade.py`
porta l'autostrada fino alla tavola instradata, e `RUN_WITH_TOO_MANY_BENDS` usa il bilancio
della catena invece del metro dello stacchetto. Prima contava una piega della dorsale come
una piega di uno stacchetto.

**La piega che nessuna tratta vedeva**, misurata sull'impianto 5: la catena
`volano -> deviatrice -> cascata-mandata-b -> … -> pdc-2` ha **sei tratte tutte con zero
pieghe** e la catena ne fa **due**. I numeri per tratta erano verdi e la catena era storta.

---

## 5. Il solutore è uscito dalla catena, e si vede (criterio 7)

`layout/compose.py` non importa più né `improve_sheet` né `lay_the_spine`. La scala dei sei
ripieghi è caduta con loro — cinque delle sei erano modi di richiamare il solutore con un
vincolo in meno — e resta la posa deterministica più il ripiego di **D-150**, che è un'altra
cosa e va difeso apposta.

I tre moduli **restano agli atti** e lo dichiarano in testa, ciascuno con **quando**,
**perché** e **dove è finito il suo lavoro**: `improve.py` (D-151), `spine.py` — solo la fase
del tronco, `carry_the_rest` vive ed è chiamato ogni giorno — e `dilate.py` (D-149).

```
$ .venv/bin/python -m pytest -q tests/layout/test_il_solutore_e_fuori.py
5 passed
```

Le cinque prove misurano in un **processo nuovo** quali moduli risultano importati: la via
ordinaria (`compose_on_ordinary_frame`), la via del piano (`esegui_piano`, `revisiona`) e la
CLI intera non tirano dentro né `improve` né `dilate`.

### Che cosa costa, misurato e dichiarato

**Senza il solutore e senza un piano, la via ordinaria peggiora, e molto**
(`misura-senza-solutore.txt`): tutti e cinque gli impianti finiscono su **A1** col ripiego
dichiarato, con 2–6 tratte cedute e 11–19 rilievi bloccanti ciascuno.

**Non è una regressione nascosta: è la ragione per cui i piani si scrivono**, ed è la
disposizione del PO del 20 settembre — «tu scrivi ora i piani con le regole». Le cinque
tavole di questa consegna escono **dal piano**, e il confronto con `main` è in testa.

---

## 6. Quello che nessun piano può chiudere, e va deciso

Componendo i piani 2, 3 e 4 è venuta fuori **una cosa sola, tre volte**, ed è la riga **B7**
nuova in `docs/regole-del-piano.md`:

> **Due porte che guardano dalla stessa parte non si uniscono con un segmento.**

`Highway.turns_allowed` vale zero per ogni catena fra macchine di spina, **senza guardare se
le facce delle sue porte lo permettono**:

| catena | perché non si chiude |
|---|---|
| imp. 2, `bollitore -> deviatrice` | `out_b` della tre vie è sotto, `coil_in` del bollitore a sinistra: facce perpendicolari |
| imp. 2, `volano -> ritorno -> bollitore` | `primary_out` e `coil_out` sono tutt'e due a sinistra |
| imp. 3, `volano -> … -> pdc` | `volano.b` e `pdc.water_return` guardano tutt'e due a destra: serve una **U** — ed è il **rilievo bloccante** dell'impianto 3, `RUN_OVERSHOOTS_ITS_PORT` |
| imp. 4, `scambiatore -> commutatrice`, `scambiatore -> deviatrice` | lo scambiatore a piastre ha `primary_in` e `primary_out` tutt'e due a sinistra, e non ruota |

**Due letture, e la scelta è del PO.** O il catalogo cambia — una macchina con due attacchi
sullo stesso lato è una scelta di simbolo, non un vincolo idraulico — o `turns_allowed`
diventa il **minimo raggiungibile** date le facce. La prima è materia MEP, la seconda è
codice. Non l'ho decisa io.

**Accanto sta la contraddizione fra B1 e B3** già nominata in §1.4: il collettore verticale
che B3 pretende fa piegare la catena che B1 vuole dritta. Il PO ha detto «prima le autostrade
dritte **il più possibile**»; come si scrive quel «il più possibile» è la stessa domanda.

---

## 7. Le prove (criterio 8)

**I 36 file di `tests/layout/` portano dentro la propria categoria**, più i due nuovi:

| categoria | quanti |
|---|---|
| difende il motore | 24 |
| difendeva il solutore | 10 |
| difende una regola del piano | 4 |

**Tre prove riscritte, nessuna archiviata in silenzio, zero `skip` e zero `xfail` nuovi:**

- `test_ordine_del_disegnatore.py::test_il_ciclo_senza_le_fasi_…` → **`test_la_scala_dei_ripieghi_e_caduta_con_il_solutore`**: difendeva l'ordine delle sei vie; adesso difende che la scala **non torni**;
- `test_ordine_del_disegnatore.py::test_si_cede_prima_a_chi_ne_ha_meno_bisogno_…` → **`test_il_ripiego_di_D_150_resta_intero`**: la cessione non esiste più, e quello che non è caduto con lei va difeso apposta;
- `test_zone_dei_pezzi_grossi.py::test_il_primo_impianto_esce_ancora` → **`test_il_primo_impianto_esce_dal_proprio_piano`**: difendeva che l'impianto 1 si componesse da solo su una A3, e quella proprietà gliela dava il solutore. Adesso difende che esca **dal proprio piano**, a zero bloccanti e zero cedute.

Prove nuove: `tests/layout/test_autostrade.py`, `tests/layout/test_il_solutore_e_fuori.py`,
`tests/validation/test_regole_del_piano.py`, `tests/piano/test_formato_del_piano.py`,
`tests/piano/test_esecutore.py`, `tests/piano/test_revisore.py`.

**Il saldo della suite: §10.**

---

## 8. I documenti (criterio 9)

`docs/SKILL.md` e `AGENTS.md` riallineati e il riquadro «in riallineamento» **chiuso**;
**ADR 0005 marcata storia** con la decisione che l'ha superata (D-151) e dove è finito il suo
argomento; `PROJECT_STATE.md`, `docs/pm/STATO-PM.md`, `README.md` portati al 20 settembre con
la storia separata e datata; `docs/plans/2026-09-03-release-plan.md` annotato, con la 0.5
«Drawing Director» barrata e dichiarata superata da D-151 e D-153. `CLAUDE.md` verificato e
**non toccato**: era già coerente.

**La citazione D-119 è corretta ovunque.** «Generatori a sinistra, impilati in verticale» è
**D-041 + D-118**; D-119 è l'area di rispetto dei raccordi. Corretta in `place.py` (2
occorrenze), `improve.py` (1, dove la regola era D-118 punto 3) e
`test_zone_dei_pezzi_grossi.py` (1). Gli usi legittimi di D-119 — l'area di rispetto nei
simboli dei raccordi — non sono stati toccati.

---

## 9. Il piano è un pezzo del prodotto (criteri 5 e 10)

`src/disegnatore_mep/piano/`: `formato.py` (modelli `pydantic`), `esecutore.py` (`orienta`,
la semina, l'instradamento, la legenda, i testi — **nessuna ricerca**), `revisore.py`.
Comandi nuovi: `disegnatore-mep piano` e `disegnatore-mep revisiona`. `scripts/piano.py`
**non esiste più**, e le tavole che escono dalla CLI sono identiche **byte per byte** a
quelle che lo script produceva.

**Criterio 10 — un piano malformato dà un errore che dice cosa manca**, non una traccia di
stack. Tredici casi coperti in `tests/piano/test_formato_del_piano.py`; per esempio:

```
al pezzo «volano» manca «x»: era atteso un numero, i millimetri dal bordo sinistro del foglio
il campo «formato» non e' valido ('A5'): era atteso uno dei formati ordinari: A4, A3, A2, A1 (D-148)
il piano nomina pezzi che non esistono nel modello: caldaia-fantasma, pompa-che-non-c-e
```

**Una correzione al comando `piano`, fatta guardando le tavole**: applicava **sempre** il
velo degli indirizzi (D-110), e la tavola che il PO guarda per giudicare il disegno arrivava
coperta di sigle di verifica. Adesso `--verifica` si chiede, come su `draw`.

---

## 10. Le misure della suite e dei cancelli

```
$ .venv/bin/python -m ruff check src tests
All checks passed!

$ .venv/bin/python -m mypy
Success: no issues found in 77 source files
```

⚠ **`mypy` non passava su `main`**: undici errori in `layout/place.py`, verificati estraendo
`origin/main` in una cartella pulita — `Found 11 errors in 1 file (checked 71 source files)`.
La causa è che `first` e `last`, in `place_sheet`, erano già presi da due **identificativi**
trenta righe sopra: `mypy --strict` ne deduceva `str`. Rinominati in `capo` e `coda` dentro
il solo blocco che li usa; **nessuna riga di codice cambia**. È **fuori dal perimetro
dichiarato** del pacchetto e lo dichiaro: l'ho fatto perché un cancello rotto non misura
niente, e perché la correzione è meccanica e verificabile.

<!-- Il saldo della suite si scrive qui, con le due misure a confronto. -->

---

## 10bis. Il PO ha fermato lo sviluppo, e da lì sono nate quattro decisioni

**È la parte più importante di questa consegna, e non è codice.** Dopo aver visto le tavole
il PO ha fermato il lavoro e ha dettato l'architettura della skill. Le quattro decisioni che
ne escono — **D-155**, **D-156**, **D-157**, **D-158** — stanno nel registro, e
`docs/ARCHITETTURA-DEL-PIANO.md` è stato riscritto su di esse.

### Che cosa ho sbagliato, ed è il motivo per cui l'architettura va scritta

**Ho trattato il piano come un artefatto da consegnare.** Ho composto a mano i piani 2, 3 e 4
e li ho committati come prodotto. Il PO:

> «Lo scopo del progetto è avere un pezzo della nostra skill che scrive i piani. Non è che
> c'è un piano scritto per ogni impianto. […] Se è così il piano non è mai qualcosa di pronto
> input ma qualcosa che dobbiamo imparare a far scrivere all'agente AI della skill.»

Il pianificatore — il **pezzo 3** — non esiste, e per cinque tavole l'ho fatto io a mano.
I cinque piani non sono prodotto: sono **il bersaglio** che il pianificatore deve pareggiare.

### Il revisore a mosse è un solutore in miniatura

Il PO, sul revisore:

> «Perché il revisore non fa la stessa cosa e gli dice cosa correggere? Dandogli magari dei
> punti sulla tavola da rispettare.»

Ha ragione, e la misura di questa stessa consegna lo dimostra: **la prima correzione del
revisore a mosse ha peggiorato su quattro impianti su cinque** (§2). Una mossa è cieca a
quello che le altre regole stavano tenendo. Un **vincolo** no: si accumula, si controlla per
coerenza prima di comporre, e sopravvive alla ricomposizione. Da qui **D-157**, e la
scoperta che **un vincolo e una regola sono la stessa cosa** — una regola è uno schema, una
correzione è lo schema istanziato su identificativi veri.

Le cure deterministiche di `piano/revisore.py` sono **dichiarate superate in testa al
modulo** ed escono in `DRAW-016`. Restano la misura, il punteggio e le condizioni d'arresto.

### Il difetto che ha prodotto D-158, e che avevo introdotto io

Il PO, sui confini di rete:

> «Il confine di rete lo sanno anche i muri. Si fa lì accanto facendo un tratto piccolo di
> tubazione, non serve metterlo da qualche parte specifica della tavola.»

Misurato, la tratta che porta il prelievo ACS, **prima e dopo**:

| impianto | prima | dopo |
|---|---|---|
| 1 | 50,0 mm | 50,0 mm |
| 2 | **205,0 mm** | **20,0 mm** |
| 3 | **502,5 mm** | **20,0 mm** |
| 4 | **152,5 mm** | **17,5 mm** |
| 5 | 32,5 mm | 32,5 mm |

**I tre lunghi erano esattamente i tre piani che ho composto io applicando A1**; i due corti
sono quelli composti il 19 e il 20 prima che A1 fosse un controllo. Ho **peggiorato una cosa
che funzionava applicando una regola** a un pezzo che quella regola non governa — un confine
di rete non ha una posizione propria (I-061) — e **niente me l'ha detto**.

Il perché è architetturale, ed è la decisione più utile di tutta la conversazione: **D-145 è
un vincolo della posa del motore, D-151 ha spostato la posa al piano, e il piano la
sovrascrive.** Senza un rilievo sulla tavola finita, si viola in silenzio. **Da qui D-158:
ogni vincolo di posa ha un rilievo sulla tavola consegnata**, e vale per A1, A2, A3 e A4.

Il foglio delle regole lo aveva già previsto senza che nessuno ci facesse caso: il controllo
di A2 dice «`test_zone_dei_pezzi_grossi.py` (posa); **`da scrivere` come rilievo sulla
tavola**».

**Sulla lunghezza come costo**, che il PO ha riaperto: D-145 punto 2 aveva già risposto, e la
risposta è migliore di un costo — «non torna come costo: D-139 resta, i millimetri restano
fuori dalle voci di costo, e la proprietà che quel costo teneva su torna nella forma
giusta». Ciò che mancava non era il costo: era il controllo.

## 11. Come è stato diviso il lavoro (D-152)

Quattro agenti paralleli **dentro** la sessione, perimetro dichiarato prima di lanciarli:

| agente | perimetro | che cosa ha portato |
|---|---|---|
| controlli | `layout/autostrade.py`, `validation/regole.py`, `validation/preflight.py`, due file di prova | i quattro controlli di D-154 e l'autostrada in tavola |
| piano | `piano/**`, `cli.py`, `tests/piano/**`, `tests/test_cli.py` | il formato, l'esecutore, il comando |
| documenti | i sette documenti dell'elenco 6, più i commenti di `place.py` e `improve.py` | il riallineamento e la citazione D-119 |
| categorie | i 36 file di `tests/layout/*.py` | la categoria dentro ciascuno |

**Il revisore, la rimozione del solutore, i tre piani nuovi e tutte le misure di questo
rapporto sono della sessione**, e quello che gli agenti hanno riferito è stato **rieseguito**
prima di finire qui dentro: la suite, `mypy`, `ruff`, le cinque tavole e i giri del revisore
li ho rifatti io.

---

## 12. Quello che questo pacchetto non chiude

- **Le tavole non sono diventate belle**, e non doveva chiuderlo. Il difetto in coda è
  nominato e misurato: il disegno è una fascia nella metà alta (D3), e i confini di rete
  finiscono lontanissimi (§1.2).
- **B7 e la contraddizione B1/B3 sono domande al PO** (§6).
- **B3 non morde con due macchine in parallelo**, e non misura *se* un collettore ci sia.
- **Il DXF non esiste ancora.** La riproducibilità (D-023) e il vincolo dell'A3 (D-148) sono
  stati lasciati andare **perché** la tavola esce in DXF e si rifinisce in CAD (I-072), e in
  `src/` non c'è niente che scriva DXF. È la contropartita di un prezzo già pagato.
