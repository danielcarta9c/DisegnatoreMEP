# DRAW-015 — Il revisore, e il repository che lo regge

**Data:** 20 settembre 2026 · **Agente unico** (D-147), con quattro agenti paralleli in
sessione (D-152) · **Base:** `8b08233`, la testa di `origin/main`

---

## Le tavole, per prime (D-146)

**Escono tutte e cinque.** È la prima volta nel progetto.

| | tavola | formato | tratte | **cedute** | **bloccanti** | violazioni | pieghe | incroci |
|---|---|---|---|---|---|---|---|---|
| impianto 1 — due PDC e accumulo combinato | [`tavole/tavola-1-DAL-PIANO.pdf`](tavole/tavola-1-DAL-PIANO.pdf) | A2 | 21 | **0** | **0** | 8 | 8 | 1 |
| impianto 2 — PDC con deviatrice e ACS | [`tavole/tavola-2-DAL-PIANO.pdf`](tavole/tavola-2-DAL-PIANO.pdf) | A2 | 23 | **0** | **0** | 8 | 8 | 2 |
| impianto 3 — PDC diretta su pavimento | [`tavole/tavola-3-DAL-PIANO.pdf`](tavole/tavola-3-DAL-PIANO.pdf) | A2 | 22 | **0** | **1** | 8 | 8 | 1 |
| impianto 4 — ibrido PDC + caldaia | [`tavole/tavola-4-DAL-PIANO.pdf`](tavole/tavola-4-DAL-PIANO.pdf) | A2 | 25 | **0** | **0** | 10 | 14 | 3 |
| impianto 5 — cascata di tre PDC | [`tavole/tavola-5-DAL-PIANO.pdf`](tavole/tavola-5-DAL-PIANO.pdf) | A1 | 54 | **0** | **0** | 18 | 33 | 14 |

> **La colonna «violazioni» conta cinque regole, non quattro.** Da quando **A4** ha il
> proprio rilievo (§4bis) il punteggio del revisore lo conta, e sono **cinque violazioni per
> tavola** che prima non si vedevano: tutte e cinque le tavole ne portano quattro o cinque, e
> §4bis le elenca con i millimetri. **Non è un peggioramento: è la misura che prima mancava.**

**L'unico rilievo bloccante è sull'impianto 3**, ed è strutturale — §6.

Il prima e il dopo del revisore sono in [`anello/`](anello/): `impianto-4-giro0.pdf` e
`impianto-4-giro1.pdf`, su un piano **guastato apposta** perché l'anello si vedesse girare.

Comando, e si riproduce intero:

```
$ scripts/tavole-dal-piano.sh
prova-1-due-pdc-accumulo-combinato   ESCE (uscita 0)  21 tratte, 0 cedute  bloccanti 0  rilievi 13
prova-2-pdc-deviatrice-acs           ESCE (uscita 0)  23 tratte, 0 cedute  bloccanti 0  rilievi 13
prova-3-pdc-diretta-pavimento        ESCE (uscita 2)  22 tratte, 0 cedute  bloccanti 1  rilievi 12
prova-4-ibrido-pdc-caldaia           ESCE (uscita 0)  25 tratte, 0 cedute  bloccanti 0  rilievi 17
prova-5-cascata-tre-pdc              ESCE (uscita 0)  54 tratte, 0 cedute  bloccanti 0  rilievi 32
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
   D-145). Adesso il prelievo ACS sta a **40 · 20 · 20 · 22,5 · 22,5 mm** dal pezzo che
   serve, e **tre dei cinque sono esattamente il proprio minimo**; gli altri due sono a un
   passo di griglia, e §4bis dice perché più vicino non si va. La cosa che conta non è la
   correzione: è che **nessun numero me l'aveva detto**, e da lì viene **D-158** — e infatti
   adesso un numero c'è, ed è **A4** (§4bis).
   ⚠ **L'acquedotto invece è ancora lontano su quattro tavole su cinque** — 25 · 30 · **70**
   · 37,5 · 30 mm contro un minimo di 20 — e il peggiore, l'impianto 3, si vede a occhio:
   l'acqua fredda entra dal bordo sinistro. È mio, e si cura componendo.
3. **Sull'impianto 5 i quattordici incroci si vedono**, e stanno quasi tutti dove il
   circuito sanitario attraversa i tre secondari. **Guardandola dopo la correzione di A4,
   quella linea ha un nome:** il confine ACS adesso sta addosso alla **presa del ricircolo**
   — A4 è a posto — ma la presa l'ho messa io **all'estremo destro del foglio**, e la
   mandata sanitaria attraversa da sola tutti e tre i secondari per arrivarci. È lo **stesso
   difetto dei 502 mm, salito di un piano**: A4 governa l'organo, non il nodo del grafo da
   cui pende. **Non la sposto**, perché dove sta la presa di un ricircolo è un contenuto MEP
   e non è mio: è la domanda 4 al PO (§6).
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
| 2 | **0** | 0 | nessuna cura si applica ai rilievi che restano (`DRAWING_ALL_ON_ONE_SIDE`, `HIGHWAY_IS_NOT_STRAIGHT`, `SERVICE_STUB_LONGER_THAN_ITS_MINIMUM`, `SHEET_BARELY_FILLED`) |
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
— giro 0: bloccanti 0, cedute 0, violazioni 12, avvisi 19, pieghe 14, incroci 3
  > radiatori: (310.0, 98.5) -> (315.0, 98.5) — regola A1 [PIECE_OUTSIDE_ITS_BAND]
— giro 1: bloccanti 0, cedute 0, violazioni 10, avvisi 17, pieghe 14, incroci 3
  > caldaia: (30.0, 221.0) -> (30.0, 96.0) — regola B1 [HIGHWAY_IS_NOT_STRAIGHT]
  > deviatrice-caldaia: (120.0, 226.0) -> (120.0, 101.0) — regola B1 [HIGHWAY_IS_NOT_STRAIGHT]
— giro 2: la correzione ha tolto la tavola
Si e' fermato perche': la correzione ha tolto la tavola: il piano corretto non si instrada
piu' (run p4-a ... run into an obstacle at (50, 36)). Si consegna il giro precedente
Giri di revisione serviti: 1 (su 2 provati) · ha migliorato: si
Rilievi per cui il revisore non ha una cura, e restano a chi compone:
SERVICE_STUB_LONGER_THAN_ITS_MINIMUM
```

**Un giro**, violazioni da 12 a 10, nessuna misura peggiorata, e l'arresto nominato. Le due
tavole sono in `anello/`.

E l'ultima riga è il comportamento che **D-157** chiede: A4 non ha una cura, quindi il
revisore **la nomina e la lascia a chi compone** invece di inventarsi una mossa. È già la
forma del pezzo 5.

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

> **E poi sono diventate cinque.** **A4** è stata aggiunta dopo, guardando le tavole, e ha il
> suo paragrafo: **§4bis**. Le quattro di questa tabella sono quelle che D-154 chiedeva.


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

## 4bis. La quinta regola, A4 — e la classe di difetto che ha aperto

**Non era nel pacchetto.** È nata guardando le tavole, dopo che il PO ha detto che un
confine di rete «si fa lì accanto, facendo un tratto piccolo di tubazione». §10bis racconta
come, D-158 è la decisione che ne esce; qui c'è la misura.

| | codice | che cosa misura |
|---|---|---|
| **A4** | `SERVICE_STUB_LONGER_THAN_ITS_MINIMUM` | la **lunghezza della spezzata** che porta ogni organo di servizio — la spezzata come il foglio la disegna — contro **il proprio minimo su griglia**, letto da `place.py` e non tarato qui |

Le due eccezioni che D-145 punto 1 chiama «vincoli dichiarati» sono dentro la misura e non
sono casi a parte: gli **accessori in linea sulla derivazione** alzano il minimo da soli
(I-044), e il **posto al minimo occupato** — un simbolo o il corridoio di una porta — si
riconosce e tace. Se è lontano e basta, il rilievo si accende.

### Quello che il rilievo dice sulle cinque tavole consegnate, ed è tutto vero

Dopo la correzione dei confini di rete restano **4 rilievi sull'impianto 1 e 5 su ciascuno
degli altri**. Non ne ho nascosto nessuno e non ho alzato nessuna soglia:

| impianto | i millimetri di tubo in più, organo per organo |
|---|---|
| 1 | acquedotto **+5,0** · scarico dell'accumulo **+2,5** · gruppo di riempimento **+17,5** · presa del riempimento **+5,0** |
| 2 | acquedotto **+10,0** · scarico **+10,0** · riempimento **+12,5** · presa **+5,0** · sicurezza **+2,5** |
| 3 | acquedotto **+50,0** · scarico **+5,0** · riempimento **+17,5** · presa **+5,0** · sicurezza **+2,5** |
| 4 | acquedotto **+17,5** · riempimento **+17,5** · presa **+5,0** · prelievo ACS **+2,5** · sicurezza **+2,5** |
| 5 | acquedotto **+10,0** · scarico **+5,0** · riempimento **+22,5** · presa **+20,0** · prelievo ACS **+2,5** |

**Sono miei, e si curano componendo meglio.** Il più grosso — l'acquedotto dell'impianto 3 a
**+50 mm** — si vede a occhio: l'acqua fredda entra dal bordo sinistro invece che da accanto
al bollitore. I sette rilievi da **+2,5 mm** sono un passo di griglia, cioè la risoluzione su
cui vive tutto il disegno: se si decide di tollerarli, **la tolleranza è il passo del foglio**
e non un numero inventato, ma è una scelta e la lascio dichiarata invece di farla di nascosto.

### Le due correzioni fatte guardando, e la misura che le ha chieste

Un agente parallelo ha misurato il rilievo su tutte e cinque e ha **rifiutato di aggiustare
la soglia**, rimandando a me il giudizio sulla tavola: sull'1 il prelievo ACS stava a 65,0 mm
dove il minimo ne vuole 40, sul 5 a 37,5 dove ne vuole 20. **Ho guardato, e i numeri avevano
ragione:**

- **impianto 1** — misurato sulla geometria consegnata, i tre organi in linea dell'ACS stanno
  fra y=166 e y=186 e il confine stava a y=121: fra l'ultima valvola e il confine c'erano
  **40 mm di tubo nudo**, di cui 15 sono il minimo del confine e **25 erano vuoti**. Portato
  da y=45 a y=70 nel piano: adesso lo stacco è **40,0 mm, cioè esattamente il minimo**, e il
  rilievo si spegne.
- **impianto 5** — portato da x=680 a **x=665**. Più vicino non si va: a 662,5 la tavola
  **non esce più** — «run w6-a has no straight stretch of 10mm for valve-isolation» — perché
  l'intercettazione in linea pretende il proprio rettilineo (B5). Restano **2,5 mm**, un
  passo, e sono misurati, non tollerati per comodità.

**E guardando l'impianto 5 si vede il difetto salito di un piano** (§1.3): il confine adesso
sta addosso alla presa del ricircolo, ma **la presa sta all'estremo destro del foglio** e la
mandata sanitaria attraversa da sola i tre secondari per arrivarci. A4 governa l'organo, non
il nodo del grafo da cui pende. Dove va la presa di un ricircolo è **contenuto MEP**: §6,
domanda 4.

### Il censimento di D-158: quali vincoli di posa non hanno ancora un rilievo

Verificato riga per riga su `docs/regole-del-piano.md` e sul codice vigente:

| regola | oggi è tenuta su da | manca |
|---|---|---|
| **A1** | `PIECE_OUTSIDE_ITS_BAND` | — chiusa qui |
| **A4** | `SERVICE_STUB_LONGER_THAN_ITS_MINIMUM` | — chiusa qui |
| **A2** | `tests/layout/test_zone_dei_pezzi_grossi.py`, che misura **la posa**, non la tavola | il rilievo |
| **A3** | **niente** | tutto |
| **B2**, **C1**, **C3** | l'errore dell'instradamento, quando c'è | il rilievo che li nomina prima |

**A3 è il caso limite, e va detto chiaro: oggi non è tenuta su da niente.** L'unico posto che
faceva valere l'ordine di processo era il solutore, ed è morto con D-151; `hierarchy.py` cita
D-060 per l'impilamento di A2, non per l'ordine da sinistra a destra, e `compose.py` lo cita
solo per dire che centrare il blocco non lo cambia.

**C3 è il buco peggiore**, e lo dice già il foglio delle regole: è **l'unico difetto di
contenuto che nasce da una scelta grafica** — il 20 settembre ha mandato l'acqua fredda
sull'uscita primaria dell'accumulo, con il grafo giusto e il disegno sbagliato.

Le apre `DRAW-016`.

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

### Domanda 4 — dove sta la presa del ricircolo sanitario

Nata guardando l'impianto 5 dopo la correzione di A4 (§4bis). Il confine ACS sta adesso
**addosso alla presa del ricircolo**, com'è giusto, ma **la presa l'ho messa io all'estremo
destro del foglio** e la mandata sanitaria attraversa da sola i tre circuiti secondari per
arrivarci: è lì che stanno quasi tutti i quattordici incroci di quella tavola.

Le due letture, e **non scelgo io perché è contenuto MEP**:

1. **la presa sta in fondo alla distribuzione sanitaria e ci deve stare** — è il punto più
   lontano dell'anello, e allora la linea lunga è vera e il difetto non esiste;
2. **la presa è un nodo che il disegno può avvicinare** — e allora va accanto al bollitore
   come il confine, e l'impianto 5 perde una decina di incroci.

Se vale la seconda, diventa una riga nuova di `docs/regole-del-piano.md` con la propria
fonte, e il rilievo che la misura è lo stesso di A4 salito di un piano.

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

### La prova che sorveglia il difetto di §10ter

`tests/piano/test_revisore.py::test_ogni_regola_misurata_conta_come_violazione` pretende che
**ogni sigla di `ORDINE_DELLE_REGOLE` sia portata da un codice di `CODICI_DELLE_REGOLE`**.
Serve perché il difetto che ha lasciato A4 fuori dal punteggio era esattamente questo: una
lista di codici scritta a mano accanto a una lista di regole che cresceva. Adesso i codici si
**ricavano** dalla mappa `REGOLA_DEL_RILIEVO`, e la prova sorveglia che restino ricavati.

### La prova di A4 che `main` non aveva, e il conto onesto

`tests/layout/test_stacchi_minimi_e_interasse.py` era l'**unica** guardia di A4 prima di
questo pacchetto, ed era già rossa su `main`. Misurato in una cartella pulita a
`origin/main`, con `PYTHONPATH` e non con l'installazione modificabile:

```
$ PYTHONPATH=$PWD/src python -m pytest tests/layout/test_stacchi_minimi_e_interasse.py -q
7 failed, 5 passed in 149.37s        # origin/main

$ .venv/bin/python -m pytest tests/layout/test_stacchi_minimi_e_interasse.py -q
8 failed, 4 passed                   # questo ramo
```

**Una prova in più è rossa qui, e la dico:**
`test_il_raccordo_che_regge_uno_stacco_sta_stretto_al_raccordo_a_cui_e_attaccato[una_macchina_con_accumulo_combinato]`.
Non si instrada — «run s3-a … the 6 straight steps the chain needs beyond the port at (47,62)
run into an obstacle» — e su `main` passava **perché il solutore spostava i pezzi finché
l'instradamento riusciva**. È la contropartita di D-151 su questo caso, non un difetto nuovo
del motore: la stessa proprietà, sulla via vigente, la difende il piano dell'impianto 1, che
esce a **zero cedute e zero bloccanti**. Il file lo dichiara già nella riga `# categoria:`.

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

## 10ter. Due cose che avevo scritto e che la misura ha smentito

**Prima le misure, poi il racconto** vale anche verso il proprio lavoro fatto, e queste due
non le tolgo: le correggo qui, perché chi legge la storia del ramo legge prima i messaggi di
commit.

### Il messaggio del commit `c5d5aed` descrive male quello che ha aggiustato

Dice: «il controllo sotto-contava il minimo quando fra l'organo e il pezzo che serve il
grafo mette un **nodo** — tipicamente una valvola di intercettazione — invece di un
accessorio in linea. Adesso il minimo è quello dell'intera catena di derivazione».

**È sbagliato, e l'ha smentito una misura di un agente parallelo.** La valvola citata,
`valve-isolation-locked-open`, è `attachment_inline`: `build_trunks` la ricompone **dentro**
la stessa tratta, e il minimo la contava già — leggeva 15,0, non 5,0. Il caso «minimo 5,0»
era un **altro pezzo**, il gruppo di riempimento.

**Quello che ha davvero aggiustato il conto** è che il minimo ha smesso di essere un numero
di questo modulo ed è diventato **le tre voci che la posa usa già**:
`place.stub_minimum_mm`, `place.inline_room_mm` e `place.ROW_GAP_MM`, prese su griglia come
fa `improve.py::_hang_ceiling`; più l'eccezione del **posto occupato**, che è la lettura che
`test_stacchi_minimi_e_interasse.py::_taken_one_step_closer` difende nella posa. Il numero
del rapporto resta quello misurato — 48 rilievi diventano 25 — ma **la ragione non è quella
scritta nel commit**.

Il codice è a posto: il docstring di `organi_di_servizio_lontani` dice le tre voci e non
ripete la diagnosi sbagliata. Resta sbagliato **solo** il messaggio di commit, e la storia
non si riscrive su un ramo già spinto: sta qui.

### A4 è entrata fra le regole e per un giorno non ha contato

Aggiunta a `ORDINE_DELLE_REGOLE`, il suo rilievo finiva fra gli **avvisi** — l'ultima voce
del punteggio, quella che una piega in meno si compra — perché `CODICI_DELLE_REGOLE` in
`piano/revisore.py` era una lista di quattro codici **scritta a mano**. Cioè: il controllo
che serviva a non violare una regola in silenzio è stato per un giorno il controllo che
nessuno contava. Adesso i codici si ricavano, e una prova lo sorveglia (§7).

---

## 11. Come è stato diviso il lavoro (D-152)

Quattro agenti paralleli **dentro** la sessione, perimetro dichiarato prima di lanciarli:

| agente | perimetro | che cosa ha portato |
|---|---|---|
| controlli | `layout/autostrade.py`, `validation/regole.py`, `validation/preflight.py`, due file di prova | i quattro controlli di D-154 e l'autostrada in tavola |
| piano | `piano/**`, `cli.py`, `tests/piano/**`, `tests/test_cli.py` | il formato, l'esecutore, il comando |
| documenti | i sette documenti dell'elenco 6, più i commenti di `place.py` e `improve.py` | il riallineamento e la citazione D-119 |
| categorie | i 36 file di `tests/layout/*.py` | la categoria dentro ciascuno |
| A4 | `validation/regole.py`, `tests/validation/test_regole_del_piano.py` | il quinto controllo, e il censimento dei vincoli di posa senza rilievo (§4bis) |

**Il revisore, la rimozione del solutore, i tre piani nuovi e tutte le misure di questo
rapporto sono della sessione**, e quello che gli agenti hanno riferito è stato **rieseguito**
prima di finire qui dentro: la suite, `mypy`, `ruff`, le cinque tavole e i giri del revisore
li ho rifatti io.

**Due volte quello che un agente ha riferito è stato smentito rieseguendolo**, ed è il motivo
per cui la regola di D-152 esiste: la diagnosi del minimo di A4 (§10ter) e un esempio non
riproducibile nella prima stesura di `ARCHITETTURA-DEL-PIANO.md`. **E una volta un agente ha
rifiutato di aggiustare una soglia e ha rimandato indietro il giudizio sulla tavola** — «la
tavola la guardi tu» — ed è così che sono nate le due correzioni di §4bis.

---

## 12. Quello che questo pacchetto non chiude

- **Le tavole non sono diventate belle**, e non doveva chiuderlo. Il difetto in coda è
  nominato e misurato: il disegno è una fascia nella metà alta (D3).
- **A4 è misurata ma non è pulita**: restano 4 rilievi sull'impianto 1 e 5 su ciascuno degli
  altri, e sono veri (§4bis). Li chiude chi compone, cioè `DRAW-016`.
- **A2, A3, B2, C1 e C3 non hanno ancora un rilievo sulla tavola finita** (§4bis), e **A3
  oggi non è tenuta su da niente**.
- **B7 e la contraddizione B1/B3 sono domande al PO** (§6).
- **B3 non morde con due macchine in parallelo**, e non misura *se* un collettore ci sia.
- **Il DXF non esiste ancora.** La riproducibilità (D-023) e il vincolo dell'A3 (D-148) sono
  stati lasciati andare **perché** la tavola esce in DXF e si rifinisce in CAD (I-072), e in
  `src/` non c'è niente che scriva DXF. È la contropartita di un prezzo già pagato.
