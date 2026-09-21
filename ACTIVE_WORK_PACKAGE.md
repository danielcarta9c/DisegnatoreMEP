# DRAW-016 — L'agente che scrive il piano, e l'agente che dice dove passare

**Titolo:** L'agente che scrive il piano, e l'agente che dà i suggerimenti precisi su dove passare
**Da svolgere:** l'agente unico (**D-147**), con agenti paralleli in sessione (**D-152**)
**Stato:** **ATTIVO** quando `DRAW-015` è fuso. Finché non lo è, l'incarico è rispondere al PO su quella consegna.
**Release:** 0.3 — generalizzazione
**Approvazione della fusione:** **del PO**, e si dà guardando le tavole (D-147, D-146)

Il PO, chiudendo la sessione del 20 settembre 2026:

> «Nella prossima sessione possiamo fare questo lavoro **dell'agente che scrive il piano,
> l'agente che fa le verifiche che dà i suggerimenti precisi su dove passare**.»

Sono i **due pezzi che mancano** di `docs/ARCHITETTURA-DEL-PIANO.md`: il **pezzo 3 —
Comporre** e l'**occhio del pezzo 5 — Rivedere**. «Dove passare» non è un modo di dire: è la
**leva che al piano manca**, e ha un nome — **`passa-per`** (D-161, punto 3).

> **Prima di tutto leggi `docs/ARCHITETTURA-DEL-PIANO.md`**, e poi l'apertura di
> `docs/regole-del-piano.md`, «**L'ordine in cui si compone — prima le autostrade**»: è la
> disposizione del PO (**D-159**) e dice in che ordine le regole si applicano.
>
> **Non comporre piani a mano e non committarli.** È l'errore della sessione del 20
> settembre, e **D-155** esiste per non ripeterlo: il piano è un intermedio che la skill deve
> **imparare a scrivere**, non un artefatto da consegnare.

---

## Da dove si parte — quello che la sessione del 20–21 settembre ha lasciato pronto

Questo pacchetto non riparte da zero. Quattro cose sono già in piedi, e vanno usate.

**1. Il metodo esiste ed è scritto** — `docs/regole-del-piano.md`, in testa, prima di ogni
regola. La quota di un'autostrada **non si sceglie**: è quella della **porta** della macchina
che la genera. Due macchine allo stesso `y` danno due autostrade rette, gratis. Poi si posa,
poi si guarda che siano rette, e **solo dopo** si appendono valvole e confini di rete.

**2. L'occhio del revisore esiste** — `skill/rivedere/`, con `ISTRUZIONI.md`, `CONSEGNA.md` e
la prova in camera pulita `prova-2026-09-20/`. **È già stato provato e ha trovato due cose che
nessun controllo poteva dare** (D-162): tre simboli in linea uno dentro l'altro
sull'alimentazione fredda del bollitore, e il ritorno ACS che corre sopra la propria mandata
senza che `RETURN_RUNS_ABOVE_ITS_SUPPLY` lo veda. Quello che gli manca **non è l'occhio**: è
il pezzo 3 a cui parlare e la sezione `vincoli` in cui scrivere.

**3. Le regole misurate sono nove, non cinque** — `validation/regole.py`:

| | regola | codice del rilievo |
|---|---|---|
| **A1** | tre macro fasce verticali | `PIECE_OUTSIDE_ITS_BAND` |
| **A4** | l'organo di servizio addosso al pezzo che serve | `SERVICE_STUB_LONGER_THAN_ITS_MINIMUM` |
| **B1** | le autostrade dritte | `HIGHWAY_IS_NOT_STRAIGHT` |
| **B3** | più macchine in parallelo ⇒ collettore verticale | `PARALLEL_MACHINES_WITHOUT_A_COLLECTOR` |
| **B4** | un organo in linea non spezza il tratto | `INLINE_ORGAN_BREAKS_THE_RUN` |
| **B8** | una linea non lascia la propria quota per tornarci | `RUN_LEAVES_ITS_QUOTA_AND_COMES_BACK` |
| **B9** | due tubazioni affiancate si tengono le corsie libere | `PARALLEL_RUNS_WITHOUT_A_FREE_LANE` |
| **B10** | mandata sopra, ritorno sotto — sulle orizzontali | `RETURN_RUNS_ABOVE_ITS_SUPPLY` |
| **B11** | mandata e ritorno corrono insieme, a interasse costante | `SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER` |

Le quattro nuove — **B8, B9, B10, B11** — nascono dalla disposizione «crea delle regole di
best practice di disegno **e poi le fai rispettare**» (I-096), ciascuna con **la propria
fonte** e **il proprio controllo** (**D-160**).

**4. Gli attacchi si possono far scorrere** — **D-163**: lungo la **faccia su cui stanno**,
mai di faccia, **mai** se appartengono a un serpentino. È una leva del pianificatore, e ha già
prodotto una misura: `gas-boiler.water_supply` da y=10 a y=5 ha portato la coppia
`caldaia ~ disgiuntore` dell'impianto 4 **da ZIG-ZAG a INSIEME**.

### Il punto di partenza, misurato

Comando: `disegnatore-mep piano` sui cinque impianti coi cinque piani a mano, il 21 settembre.

| impianto | tratte | cedute | incroci | rilievi | bloccanti | B1 autostrade storte | A4 confini lontani |
|---|---|---|---|---|---|---|---|
| **1** | 21 | **0** | 1 | 14 | 0 | 4 | 4 |
| **2** | 23 | **0** | 2 | 14 | 0 | 3 | 5 |
| **3** | 22 | **0** | 1 | 15 | **1** (B7, strutturale) | 3 | 5 |
| **4** | 25 | **0** | 3 | 20 | 0 | 5 | 5 |
| **5** | 54 | **0** | 12 | 38 | 0 | **12** | 5 |

**Il giudizio del PO su queste cinque**, ed è il metro vero: «1, 2, 3 vanno quasi bene; **la 4
e la 5 mi sembra che non hai minimamente risolto il problema. Non vedo le autostrade ben
tracciate**».

**`RUN_LEAVES_ITS_QUOTA_AND_COMES_BACK` è a zero su tutte e cinque**: i sali-scendi sono
chiusi, ed è il difetto che il cold eye review aveva trovato il 4 agosto (D-065) e che è
riemerso a penna rossa quarantasette giorni dopo.

---

## Che cosa è stato provato, e non va rifatto

Misurato il 20 settembre. Sta qui perché la prossima sessione non ci perda un'altra giornata.

1. **Il difetto è nella fase delle autostrade, non dopo.** Ridotti gli impianti 4 e 5 a
   **sole macchine e collettori, senza una valvola**, le autostrade restano storte: **5
   spezzate piegate sul 4, 11 sul 5**. L'esperimento l'ha chiesto il PO, e la risposta è la
   sua: il problema **non** nasce quando si appendono gli organi.
2. **I collettori non si possono togliere.** Tre pompe in parallelo senza collettore mettono
   **tre tubazioni su una porta sola**: il grafo non lo permette, e non è una questione di
   disegno.
3. **L'impianto 4 non può uscire come lo schizzo del PO.** Impilata la caldaia sotto la pompa
   di calore a sei quote diverse: **2 non si instradano affatto, 3 peggiorano, 1 pareggia.**
   La topologia del 4 non è quella dello schizzo — c'è un disgiuntore idraulico in mezzo.
   **Va detto al PO**, non aggirato.
4. **Ruotare il radiatore dell'impianto 1** toglie una piega e apre un rilievo **bloccante**
   `RUN_OVERSHOOTS_ITS_PORT` a ogni x provata. Provato e scartato.
5. **Allineare la commutatrice esattamente sulla quota del ritorno della caldaia crea un
   sali-scendi**: lo stacco del collettore e il ritorno finiscono sulla stessa quota. Va
   tenuta **a 20 mm**.
6. **L'ordine dei due collettori** (I-099): sormonti **pari** (12 e 12), ma col collettore
   del **ritorno più vicino alle macchine** i rilievi scendono **da 49 a 42**. Scelto quello.

---

## Le decisioni che lo governano

| | |
|---|---|
| **D-155** | Il piano non è un input: lo scrive il pianificatore, che è un pezzo della skill |
| **D-156** | I cinque pezzi, e la natura di ciascuno. 3 e 4 sono l'instradatore-disegnatore, ed è misto |
| **D-157** | Il revisore emette **vincoli** su nodi nominati, **mai mosse** |
| **D-158** | Ogni vincolo di posa ha un **rilievo sulla tavola consegnata** |
| **D-159** | **Il disegno nasce dalle autostrade**, e l'ordine in cui si compone è quello |
| **D-160** | Una regola ha una **fonte** e un **controllo**; un controllo fuori dal punteggio non è un controllo |
| **D-161** | Il piano **non può chiedere la forma di una spezzata**: può solo liberarle il posto. La leva che manca è **`passa-per`** |
| **D-162** | L'occhio del revisore **guarda** e **non ricalcola** |
| **D-163** | Un attacco scorre **lungo la propria faccia**, mai di faccia, mai se è di un serpentino |

---

## Le cose da fare

### 1. `skill/comporre/` — l'agente che scrive il piano

Nella **stessa forma del pezzo 1**, che è il modello e funziona: `ISTRUZIONI.md`
autosufficienti («queste istruzioni bastano da sole, non serve leggere altro»),
`CONSEGNA.md`, e le prove in camera pulita.

Dentro `ISTRUZIONI.md` va **il metodo**, non l'elenco delle regole. **Il metodo c'è già
scritto** ed è **D-159**: si copia da `docs/regole-del-piano.md`, sezione «L'ordine in cui si
compone», nei suoi cinque passi, **e si scrive per primo**, perché è l'ordine in cui tutto il
resto si applica.

L'attrezzo per eseguirlo esiste e si usa **prima** di posare, non dopo:
`layout/autostrade.py::porte_in_tavola` dice dove sta ogni porta di ogni pezzo posato;
`autostrade_in_tavola` e `pieghe_dell_autostrada` dicono quali catene sono autostrade e quante
pieghe fanno, spezzata per spezzata.

Il resto del materiale, e non si inventa niente:

- `docs/regole-del-piano.md` — A1…A4, B1…B11, C1…C3, D1…D3, ciascuna con la propria fonte;
- le **cinque composizioni a mano** (punto 5): il modo in cui si è già composto, con la regola
  scritta accanto a ogni pezzo e, dal 20 settembre, la **misura prima/dopo** di ogni mossa;
- `docs/input-pm/REGISTRO.md`, che è il giacimento principale delle correzioni del PO;
- le tavole di riferimento del disegnatore del PO, `docs/input-pm/riferimenti-grafici/` —
  comprese **le due segnate a penna dal PO**, `riferimenti-grafici/2026-09-20/`.

**Tre buchi da chiudere esplicitamente, perché un agente che legge solo A1 li rifarà:**

1. un **confine di rete** non sta in una fascia, sta **addosso al pezzo che serve** con lo
   stacco minimo (A4, D-145, I-061) — il rilievo `SERVICE_STUB_LONGER_THAN_ITS_MINIMUM` è
   ancora acceso **24 volte** sui cinque piani a mano;
2. **un pezzo che sta su un'autostrada si posa sulla quota dell'autostrada** — è l'errore che
   ha prodotto la U da 120 mm dell'impianto 5;
3. **prima di appendere un organo si guarda quale autostrada deve passare di lì** (D-161).

⚠ **`ISTRUZIONI.md` non è il posto dove nascono le regole.** Se componendo si impara una cosa
nuova, la riga va in `docs/regole-del-piano.md` **con la propria fonte e il proprio controllo**
(D-160), e le istruzioni la citano.

### 2. `skill/rivedere/` — l'agente che dà i suggerimenti su dove passare

**Esiste** (D-162), ed è stato provato in camera pulita. Qui **non si riscrive**: si attacca
all'anello. Tre cose, e sono le uniche.

1. **I vincoli diventano dati**, non solo prosa: la sezione `vincoli` del piano (punto 3), nel
   vocabolario di `ARCHITETTURA-DEL-PIANO.md` §5.
2. **Il pezzo 3 li riceve e li rispetta**, e si misura il giro: stessa tavola, vincoli
   applicati, rilievi prima e dopo. **Se peggiora, il rapporto era sbagliato, non la tavola**
   — è il criterio 4 di `skill/rivedere/CONSEGNA.md`.
3. **I due difetti che l'occhio ha già trovato si chiudono**, perché sono veri:
   - sull'alimentazione fredda del bollitore dell'impianto 5 **tre simboli in linea sono uno
     dentro l'altro**, e l'unico rilievo su quella tratta chiede di **accorciarla** —
     applicarlo **peggiora**. È un difetto di B5 che nessun controllo nomina;
   - il **ritorno ACS corre sopra la propria mandata** e B10 non lo vede perché **le due
     tratte portano tutt'e due `supply=True`**: è il verso del ricircolo che non si ricava
     (**D-059**). Non è un difetto del controllo: è un buco nel modello.

⚠ **La regola prima di tutte, e sta già scritta in `ISTRUZIONI.md`: l'occhio non ricalcola.**
Se si mette a contare pieghe e millimetri è **una copia peggiore dei controlli**. Chi tocca
quelle istruzioni non tocchi quella riga.

### 3. `passa-per` — la leva che manca, e che il PO ha chiesto con altre parole

È **D-161**, ed è il «dove passare» della sua frase.

`piano/formato.py` cresce di una sezione `vincoli`, validata come il resto: un vincolo
malformato dà un errore che dice che cosa manca. E il motore — `layout/route.py` — impara a
eseguire **`passa-per`**: oggi la spezzata la decide da sola l'instradatore sul costo, e il
piano può **solo** spostare i pezzi.

**La misura che dice quanto vale**, ed è già fatta: sull'impianto 5 la colonna sotto l'uscita
della deviatrice era occupata dal gruppo di riempimento; **spostare il gruppo di 20 mm ha
portato quella linea da 3 pieghe a 1** e i rilievi della tavola **da 42 a 38**. Con
`passa-per` non serviva spostare niente.

> ⚠ `layout/route.py` è **motore**, ed è **l'unica cosa fuori dal motore-che-funziona che
> questo pacchetto autorizza**. Va dichiarata prima di toccarla.

### 4. Le cure deterministiche del revisore escono

`piano/revisore.py` dichiara già in testa che sono superate da **D-157**. Qui si tolgono:
restano la misura, il punteggio, le condizioni d'arresto e la guardia che non peggiora in
silenzio. Chi corregge è il pezzo 5, che scrive vincoli.

### 5. I cinque piani a mano cambiano di posto e di nome

Escono da `docs/collaudi/PROVA-PIANO/` — che li faceva sembrare prodotto — ed entrano nel
**collaudo del pezzo 3**, accanto alle sue prove in camera pulita, nella stessa posizione in
cui stanno i grafi di `skill/capire/prova-2026-08-07/`. Con in testa la riga che dice **che
cosa sono**: il bersaglio, scritto a mano, che il pianificatore deve pareggiare.

> **Sono stati corretti il 20 settembre guardando le tavole**, e ogni mossa porta nel file la
> **regola** che la motiva e la **misura prima/dopo**. Il bersaglio **non è pulito** e le note
> lo dicono: sull'impianto 5 il confine ACS non si può avvicinare oltre 22,5 mm, a 662,5 la
> tavola non esce più.

### 6. I rilievi che mancano, censiti (D-158)

`DRAW-015` ha chiuso **A1** e **A4**; la sessione del 20 settembre ha aggiunto **B8, B9, B10,
B11**. Resta:

| regola | oggi è tenuta su da | che cosa serve |
|---|---|---|
| **A2** — chi sta in parallelo si impila | `tests/layout/test_zone_dei_pezzi_grossi.py`, che misura **la posa**, non la tavola | il rilievo sulla tavola |
| **A3** — l'ordine del processo da sinistra a destra | **niente** | tutto |
| **B2** — dal circolatore un tratto dritto, una curva, la dorsale | l'errore dell'instradamento, quando c'è | il rilievo che lo nomina prima |
| **B5** — una tratta con più accessori vuole il proprio rettilineo | **niente sulla tavola** | il rilievo — è il difetto che l'occhio ha trovato sull'alimentazione fredda |
| **C1** — un pezzo si prende dal lato delle sue porte | l'errore dell'instradamento | idem |
| **C3** — la mappa degli attacchi si rifà solo per i raccordi | **niente** | il confronto fra grafo e tavola |

**Per primi A2, A3 e B5.** I primi due sono vincoli di posa nel senso stretto di D-158; **B5 è
il difetto che il PO vedrebbe a occhio** — tre simboli sovrapposti sono illeggibili.

> **Dove si aggancia un controllo nuovo, e non c'è un secondo posto:**
> `validation/regole.py::CODICE_DELLA_REGOLA` — sigla → codice, nell'ordine in cui i controlli
> girano. Da lì si ricavano `ORDINE_DELLE_REGOLE` e il `CODICI_DELLE_REGOLE` che il
> **punteggio** conta. Aggiungere il controllo e dimenticare la riga vuol dire che il rilievo
> finisce fra gli **avvisi**: è successo ad A4, ed è **D-160**. Una prova lo sorveglia, e il 20
> settembre ha fermato B8, B9 e B11 esattamente per questo.

**A3 è il caso limite**: l'unico posto che la faceva valere era il solutore, morto con D-151.
**C3 è il buco peggiore** — lo dice già il foglio delle regole — perché è l'unico difetto di
**contenuto** che nasce da una scelta **grafica**.

### 7. I documenti del motore dichiarano che cosa è storia

`docs/pm/2026-09-11-architettura-della-posa-a-fasi.md`,
`docs/pm/2026-09-16-come-ragiona-il-motore-e-come-dovrebbe.md`,
`docs/plans/2026-08-06-piano-costruzione-skill.md`, `docs/standard/COLD_EYE_REVIEW.md` e
`docs/DEFERRED.md:254` raccontano ancora il solutore come vigente. Regola unica: o vigente, o
dice in testa che è storia e quale decisione l'ha superato.

### 8. Le ventuno prove rosse che il solutore si è portato dietro

`DRAW-015` lascia il saldo della suite **peggiore di ventuno**: `main` 17 fallite, questo ramo
38 (RAPPORTO §10). Sono la contropartita di D-151 — prove che, per la via ordinaria,
pretendevano la qualità che il solutore produceva.

**Non si chiudono con uno `skip` né con un `xfail`**, che è la scorciatoia che questo progetto
non prende. Per ciascuna, una delle due:

1. **la proprietà vale ancora sulla via vigente** — allora è una regressione vera e si ripara,
   o si riscrive la prova perché misuri quella proprietà **dal piano**;
2. **la proprietà era del solutore** — allora la prova dichiara in testa che cosa difendeva e
   perché è caduta, e **il conto si dichiara nel rapporto**.

**E la prima cosa da provare non è riscriverle.** Misurato chiedendo **alle ventidue e solo a
quelle** quale errore le ferma (RAPPORTO §10): **diciassette nominano lo stesso pezzo**, il
miscelatore termostatico, e **diciannove su ventidue sono un errore della posa
deterministica**, non un'asserzione — la mandata sanitaria porta **tre accessori in linea** e
non trova il rettilineo che pretendono (**B5**, e vedi il punto 6: è lo stesso difetto che
l'occhio ha visto sulla tavola).

> **Un difetto solo che spiega diciassette prove è un candidato serio**, ed è lo stesso che il
> punto 6 chiede di misurare e il punto 2 di chiudere. Si prova questo per primo.
> ⚠ Toccare la posa deterministica vuol dire toccare **il motore**: si dichiara prima.

⚠ **`tests/acceptance/test_drawing.py` non ha la riga `# categoria:`.** Quattro delle ventuno
sono lì: la riga va scritta.

---

## Perimetro

**Dentro:** `skill/comporre/**`, `skill/rivedere/**`; `src/disegnatore_mep/piano/formato.py` e
`revisore.py`; `validation/regole.py` per i rilievi di A2, A3 e B5; il `passa-per` nel motore —
`layout/route.py` — che è **l'unica cosa fuori dal motore-che-funziona che questo pacchetto
autorizza, e va dichiarata**; `docs/regole-del-piano.md`; i cinque documenti dell'elenco 7;
`docs/collaudi/DRAW-016/`.

**Fuori:** tutto il resto del motore — `inline.py`, `place.py`, `legend.py`, `labels.py`,
`addresses.py`, `graphics/**`. **Fuori** `highways.py` e `turns_allowed` finché il PO non ha
risposto alla domanda **B7**. **Fuori** qualunque decisione MEP o convenzione grafica che il
PO non abbia dato — e ce ne sono tre in attesa, I-097.

**Gli attacchi dei simboli**: si possono far scorrere **lungo la propria faccia** (D-163), mai
di faccia, **mai** se appartengono a un serpentino. Ogni scorrimento alza la versione del file
del simbolo e porta la misura che lo giustifica.

---

## Criteri di accettazione

Ogni criterio si chiude con **il comando eseguito e il suo output**.

1. **Il pianificatore esiste e gira in camera pulita**: un agente avviato da zero, che riceve
   solo `skill/comporre/ISTRUZIONI.md` e il grafo completo, produce un piano che **si carica e
   si instrada**. Su almeno **tre** dei cinque impianti.
2. **Il confronto con il bersaglio, impianto per impianto**: rilievi bloccanti, tratte cedute,
   violazioni di regola, pieghe, incroci del piano dell'agente contro quello scritto a mano.
   **Se l'agente fa peggio si dice di quanto e su cosa** — non è un fallimento del pacchetto,
   è la misura da cui si migliorano le istruzioni.
3. **L'anello si chiude**: l'occhio scrive **vincoli in forma di dati**, il pianificatore li
   rispetta, e su almeno un impianto il giro **migliora**. Prima e dopo, con le due tavole.
4. **Nessuna tavola perde quello che ha guadagnato**: cinque tavole, **zero tratte cedute**, e
   i rilievi bloccanti non aumentano su nessuna. Il punto di partenza è la tabella qui sopra —
   **14 · 14 · 15 · 20 · 38** rilievi, **1 · 2 · 1 · 3 · 12** incroci, un bloccante sul 3.
5. **Le autostrade del 4 e del 5 si raddrizzano**, perché è la cosa che il PO ha bocciato:
   `HIGHWAY_IS_NOT_STRAIGHT` è acceso **5 volte sul 4 e 12 sul 5**, e scendere è il punto di
   questo pacchetto.
   *Sotto, la misura che le separa dalle tavole che il PO approva: le colonne verticali di
   autostrada sono **2 · 2 · 3 · 6 · 12** (I-098).*
6. **Il confine di rete non si allontana**: il rilievo di A4 è acceso **24 volte** e il
   bersaglio è **zero**.
7. **A2, A3 e B5 hanno il loro rilievo**, ciascuno con la tavola su cui si vede.
8. **Le cure deterministiche non ci sono più**, e una prova lo sorveglia.
9. **Nessun documento resta in terzo stato**, compresi i cinque dell'elenco 7.
10. **Il saldo della suite non peggiora rispetto allo stato consegnato da `DRAW-015`** — 38
    fallite, 1564 passate, 24 `skip`, 12 `xfail` — zero `skip` e zero `xfail` nuovi, `ruff` e
    `mypy` verdi. **Ogni prova che torna verde si dice.**

⚠ **Il criterio 10 si misura contro lo stato consegnato da `DRAW-015`, non contro `main`**:
partire da 38 e arrivare a 38 è «non peggiora». **Arrivare sotto è il miglioramento che I-067
chiede.**

---

## Consegna

Una PR sola verso `main`, **non fusa finché il PO non ha visto le tavole e detto di sì**.

**Le tavole, per prime** (D-146) — comprese quelle che il **pianificatore** ha composto da
solo, che sono il punto di questo pacchetto. Rapporto in `docs/collaudi/DRAW-016/RAPPORTO.md`.

**Prima di chiedere l'approvazione:**

1. **Guarda le tavole**, e mettile accanto a quelle del disegnatore del PO e alle **due che ha
   segnato a penna**. Se una ti sembra sbagliata e i numeri dicono che va bene, scrivilo: è
   successo due volte su due ed è servito tutt'e due le volte.
2. **Misura la non-regressione prima, non dopo.** Qui sono il 4, il 5 e il 10.
3. **Se una disposizione del PO ammette due letture, fermati e chiedi al PO.** Il 20 settembre
   I-091 ne ammetteva due, si è chiesto, e la risposta ha cambiato il lavoro.

---

## Le domande aperte al PO — da portargli, non da risolvere

1. **Le tre convenzioni grafiche** (I-097), e nessuna si può decidere senza di lui perché le
   sue stesse tavole non concordano fra loro. **Gli incroci:** sul suo corpus, 4 volte niente,
   3 volte interruzione, 1 volta salto ad arco. **Gli spigoli:** una tavola li raccorda tutti
   con lo stesso raggio, un'altra li fa vivi. **Il tratteggio:** in una tavola vuol dire
   «limite di fornitura», in un'altra «ritorno» — lo stesso stile con due significati non può
   stare nella stessa grammatica. *In Italia nessuna norma prescrive come si traccia uno schema
   funzionale: UNI 9511 dà i segni grafici, non il tracciamento. È una scelta di progetto
   legittima, ma va dichiarata in legenda.*
2. **Quante autostrade verticali fra due colonne** (I-098). Lui stesso ne dubitava: «in genere
   ne è consentita una sola… ma forse non è una buona regola». **Contate: 2 · 2 · 3 · 6 · 12**,
   e lui ha approvato le prime tre e bocciato le ultime due. **È l'unico numero che separa le
   tavole che approva da quelle che boccia**, e le separa nettamente — ma «una sola» non regge
   sulle sue tavole di riferimento. La soglia è sua.
3. **B7** — `turns_allowed` vale zero per ogni catena fra macchine di spina senza guardare se
   le facce delle porte permettono una retta. Quattro catene su tre impianti non si possono
   raddrizzare, e una è **l'unico rilievo bloccante** che resta (impianto 3). *O cambia il
   catalogo, o il bilancio diventa il minimo raggiungibile.* La prima è materia MEP.
4. **B1 contro B3 sulla cascata** — il collettore verticale che B3 pretende fa piegare la
   catena che B1 vuole dritta: **la tavola è giusta e il numero dice che è sbagliata.**
5. **Dove sta la presa del ricircolo sanitario.** Sull'impianto 5 sta **all'estremo destro del
   foglio** e la mandata sanitaria attraversa da sola i tre secondari per arrivarci: è lì che
   stanno quasi tutti gli incroci di quella tavola. Contenuto MEP.
6. **Il verso del ricircolo ACS non si ricava** (D-059): mandata e ritorno portano tutt'e due
   `supply=True`, e per questo B10 non vede il ritorno che corre sopra la propria mandata.
   *Serve sapere da lui se il ricircolo è una rete con un verso, o due tratte della stessa.*
7. **Quando si apre il pacchetto DXF** — D-023 e D-148 sono state lasciate andare **perché**
   l'elaborato esce in DXF, e quel pezzo non esiste.

---

## Quello che questo pacchetto **non** chiude

- **Le tavole non diventano belle qui.** Il difetto in coda resta nominato e misurato: il
  disegno è una fascia nella metà alta su tutte e cinque (D3). *La soglia 3,0 di D3 è tarata
  sulle tavole del PO stesso — 1,4 / 1,6 / 2,5 — e l'unico caso fuori scala è un ritaglio, non
  una tavola finita.*
- **L'elenco delle regole**, che il PO ha dichiarato aperto (I-085) e che I-096 riapre.
- **La composizione a corsie** della ricerca del 4 agosto §2.2 — entra quando l'avremo composta
  almeno una volta, con la sua tavola.
