# DRAW-016 — L'agente che scrive il piano, e l'agente che dice dove passare

**Titolo:** L'agente che scrive il piano, e l'agente che dà i suggerimenti precisi su dove passare
**Da svolgere:** l'agente unico (**D-147**), con agenti paralleli in sessione (**D-152**)
**Stato:** **ATTIVO.** `DRAW-015` è fuso su `main` (**D-166**).
**Release:** 0.3 — generalizzazione
**Approvazione della fusione:** **del PO**, e si dà guardando le tavole (D-147, D-146)

Il PO, il 21 settembre 2026, aprendo questo pacchetto:

> «Serve di sviluppare gli agenti della skill **Pianificatore e verificatore** e **aggiornare
> il solutore** in modo che il tutto funzioni. Proviamo innanzi tutto nella prossima sessione a
> **disegnare le tavole senza le valvole in mezzo** in modo da vedere se **gli agenti riescono
> a disegnare queste autostrade come farebbe un disegnatore umano**.»

E, il 20 settembre, chiudendo `DRAW-015`:

> «L'agente che scrive il piano, l'agente che fa le verifiche che dà i suggerimenti precisi su
> dove passare.»

Sono i **due pezzi che mancano** di `docs/ARCHITETTURA-DEL-PIANO.md` — il **pezzo 3 —
Comporre** e l'**anello del pezzo 5 — Rivedere** — più il **motore** che li deve reggere.
«Dove passare» non è un modo di dire: è la **leva che al piano manca**, e ha un nome —
**`passa-per`** (D-161).

---

## ⛔ Le tavole non sono approvate, e questo pacchetto parte da lì

`DRAW-015` è stato fuso, **e le tavole no** (**D-166**). Sono due cose diverse, e il PO le ha
separate lui:

> «La PR la puoi fondere **ma le tavole non sono "approvate"**. Stiamo ancora in fase di
> sviluppo quindi le tavole sono ancora **lontane da ciò che voglio**. Però **la direzione ora
> è quella giusta** quindi va tutto su `main` **con la registrazione che le tavole non vanno
> bene così**.»

Quello che è approvato è **la direzione**. **Nessuna sessione può citare quella fusione come
approvazione di una tavola.**

## ⛔ E il criterio non è un numero

**D-164**, e va letta prima di scrivere una riga di questo pacchetto:

> «Quante autostrade **non c'è un numero**… **Un'autostrada per definizione ha poche curve e
> tratti rettilinei.** Ho provato a spiegarlo in ogni modo ma tu ogni volta cerchi un criterio
> **matematico** ma non c'è questo criterio. **Un criterio grafico non matematico.** Nei miei
> schizzi è piuttosto evidente.»

Il conto delle colonne verticali — 2 · 2 · 3 · 6 · 12 — resta agli atti come **sintomo** e
**non diventa una soglia**. Chi giudica se un'autostrada è un'autostrada è l'**occhio**
(D-162). **Trasformare un'osservazione in una soglia è il solutore che rientra dalla finestra**
(D-151), ed è l'errore che questo pacchetto ha più probabilità di rifare.

**E la convenzione grafica non si tocca** (**D-165**): è quella sviluppata fino a qui. Le
tavole di `docs/input-pm/riferimenti-grafici/` sono riferimenti **su come si instradano i
tubi**, non una fonte di convenzione, e le loro discordanze non sono un problema da risolvere.

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
| **D-164** | **Un'autostrada si giudica a occhio: il criterio è grafico, non matematico.** Nessuna soglia, mai |
| **D-165** | **La convenzione grafica è quella sviluppata finora, e non si tocca** |
| **D-166** | `DRAW-015` **è fuso**, e le tavole **non sono approvate**. Quello che è approvato è la direzione |
| **D-167** | **Un terminale si prende da un lato solo**: `in` e `out` tutt'e due sulla faccia sinistra |
| **D-168** | La **rotazione di una tre vie si sceglie e si scrive nel piano**: la terza via guarda il pezzo che serve |

---

## Le cose da fare

### 0. La prima prova, e l'ha dichiarata il PO: **le tavole senza il corredo**

> «Proviamo **innanzi tutto** nella prossima sessione a **disegnare le tavole senza le valvole
> in mezzo** in modo da vedere se **gli agenti riescono a disegnare queste autostrade come
> farebbe un disegnatore umano**.»

**Si fa per prima, prima di tutto il resto**, e non è un esperimento diagnostico come quello
del 20 settembre: quello serviva a capire **dove** stava il difetto, e la risposta c'è già —
è nella fase delle autostrade. **Questo serve a vedere se gli agenti sanno disegnare.**

Come si imposta, e il materiale c'è:

- **l'ingresso è il grafo ridotto** — solo macchine, accumuli e collettori, **nessun organo in
  linea, nessun confine di rete, nessuno strumento**. Il riduttore usato il 20 settembre sta in
  `scratchpad` e va **portato nel repository**, in `docs/collaudi/DRAW-016/`, perché una prova
  che non si riesegue non è una prova;
- **il pianificatore compone quel grafo** seguendo il metodo di **D-159**, e nient'altro;
- **il metro non è un numero**: si mettono le tavole **accanto agli schizzi del PO**
  (`docs/input-pm/riferimenti-grafici/`, comprese le due segnate a penna) e si guarda se
  **assomigliano al lavoro di un disegnatore**. È D-164, ed è il punto dell'esercizio;
- **il punto di partenza, misurato il 20 settembre**: sul grafo ridotto restano **5 spezzate
  piegate sull'impianto 4 e 11 sul 5**. Se l'agente fa meglio, si dice di quanto; se fa peggio,
  pure.

⚠ **Se da questa prova non esce nessuna tavola, è la prima cosa che si dice** (`CLAUDE.md`),
non una nota in fondo al rapporto.

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

**Dentro:** `skill/comporre/**`, `skill/rivedere/**`; `src/disegnatore_mep/piano/**`;
`validation/regole.py` per i rilievi di A2, A3 e B5; `docs/regole-del-piano.md`; i cinque
documenti dell'elenco 7; `docs/collaudi/DRAW-016/`.

**E il motore, che questo pacchetto apre.** Il PO, il 21 settembre: «sviluppare gli agenti
della skill Pianificatore e verificatore **e aggiornare il solutore in modo che il tutto
funzioni**». `layout/**` è **dentro** — `route.py` per `passa-per`, e il resto per quello che
la prova 0 dimostrerà necessario.

> ⚠ **Una parola da chiarire prima di toccarla, e non la decide questa sessione.** Nei nostri
> documenti «**solutore**» è la **ricerca** che **D-151** ha abolito, e il PO chiede di
> aggiornarlo. La lettura con cui questo perimetro è stato scritto è **«il motore che instrada
> e disegna»** — il **pezzo 4**, `layout/` — perché è la parte che disegna davvero e perché
> far tornare la ricerca contraddirebbe D-151, che il PO stesso ha approvato. **È I-100, ed è
> aperta:** se la lettura è sbagliata, si corregge **prima** di toccare il motore.
>
> E in ogni caso **il solutore non torna**: nessuna somma pesata, nessuna ricerca che sceglie
> la posa. Se il motore va cambiato, si cambia quello che **esegue**, non quello che **decide**.

**Fuori:** `highways.py` e `turns_allowed` finché il PO non ha risposto alla domanda **B7**.
**Fuori** qualunque decisione MEP che il PO non abbia dato. **Fuori la convenzione grafica**,
che **non si tocca** (D-165).

**Gli attacchi dei simboli**: si possono far scorrere **lungo la propria faccia** (D-163), mai
di faccia, **mai** se appartengono a un serpentino. **Si spostano nel generatore** —
`examples/graphics/build_symbols.py` — **mai nel file generato**, perché da lì si ricava anche
il mozzicone disegnato: cambiare solo il manifesto lascia il corpo del simbolo scollegato dalla
porta che dichiara, ed è già successo (`DRAW-015` RAPPORTO §13.8). Ogni scorrimento alza la
versione del manifesto e porta la misura che lo giustifica.

---

## Criteri di accettazione

Ogni criterio si chiude con **il comando eseguito e il suo output**.

0bis. **Il pettine si compone** (**B12**, la regola che il PO ha disegnato il 21 settembre):
   su almeno due impianti la coppia mandata/ritorno resta **affiancata** dalla colonna fino al
   terminale, i collettori stanno **addosso alle macchine**, e il terminale si prende **da un
   lato solo**. Le due tavole che il PO ha ridisegnato — la 4 e la 5 — sono il metro, e stanno
   in `docs/input-pm/riferimenti-grafici/2026-09-21/`.
0. **Le tavole senza il corredo, per prime** (punto 0, ed è la prova che il PO ha chiesto):
   il pianificatore compone i **cinque grafi ridotti a sole macchine, accumuli e collettori**,
   e le tavole escono. **Il giudizio si dà guardandole accanto agli schizzi del PO**, non
   contando (D-164): *assomigliano al lavoro di un disegnatore?* Si scrive la risposta, e se è
   no si scrive **che cosa** non assomiglia. Il riduttore del grafo entra nel repository.
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
   questo pacchetto. ⚠ **Ma il criterio non è quel numero** (D-164): il numero serve a non
   peggiorare in silenzio, **il giudizio si dà guardando**. Un pacchetto che porta il conto a
   zero e lascia tavole che non si leggono **non ha raggiunto questo criterio**.
6. **Il confine di rete non si allontana**: il rilievo di A4 è acceso **24 volte** e il
   bersaglio è **zero**.
7. **A2, A3 e B5 hanno il loro rilievo**, ciascuno con la tavola su cui si vede.
8. **Le cure deterministiche non ci sono più**, e una prova lo sorveglia.
9. **Nessun documento resta in terzo stato**, compresi i cinque dell'elenco 7.
10. **Il saldo della suite torna a 38 o sotto** — zero `skip` e zero `xfail` nuovi, `ruff` e
    `mypy` verdi. **Ogni prova che torna verde si dice.**

⚠ **Il saldo è salito a 47, per una ragione dichiarata, e va riportato giù.** `DRAW-015` aveva
consegnato **38** fallite e **1582** passate. **D-167** — le porte dei terminali tutt'e due
sullo stesso lato — ne ha aperte **nove**, e sono **una cosa sola**: i cinque piani scritti a
mano sono composti per terminali **passanti**, mettono le utenze dove il pettine non passa, e
sull'impianto 5 aprono un `RUN_OVERSHOOTS_ITS_PORT` **bloccante** su `s8`; le prove del
revisore cadono a valle di quello. **Nessuna delle 38 precedenti è tornata verde.**
**Si chiudono ricomponendo i cinque piani** (punti 0 e 5), non toccando le prove: i piani a
mano sono il **bersaglio** del pianificatore, non il prodotto, e adesso sono **vecchi**.

---

## Consegna

Una PR sola verso `main`, **non fusa finché il PO non ha visto le tavole e detto di sì**.

⚠ **E «fusa» non vuol dire «approvate»** (**D-166**): `DRAW-015` è stato fuso con le tavole
esplicitamente **non approvate**. Se il PO autorizza la fusione senza approvare le tavole,
**la registrazione di questo viaggia con la fusione**.

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

> **Due sono state chiuse dal PO il 21 settembre, e chi le ripropone perde un giro.**
> **Le convenzioni grafiche** (I-097): «la convenzione grafica è quella che abbiamo sviluppato
> fino adesso e **non si tocca**», e le sue tavole sono riferimenti **sull'instradamento**, non
> una fonte di convenzione — **D-165**. **Quante autostrade verticali** (I-098): «**non c'è un
> numero**… il criterio è **grafico, non matematico**» — **D-164**.

1. **La parola «solutore»** (I-100). Il PO chiede di «aggiornare il solutore in modo che il
   tutto funzioni», e nei nostri documenti quella parola indica la **ricerca abolita da
   D-151**. Il perimetro è stato scritto leggendo **«il motore che instrada e disegna»**
   (pezzo 4, `layout/`). *Se la lettura è sbagliata va corretta prima di toccare il motore*,
   e in ogni caso **la ricerca non torna**.
2. **B7** — `turns_allowed` vale zero per ogni catena fra macchine di spina senza guardare se
   le facce delle porte permettono una retta. Quattro catene su tre impianti non si possono
   raddrizzare, e una è **l'unico rilievo bloccante** che resta (impianto 3). *O cambia il
   catalogo, o il bilancio diventa il minimo raggiungibile.* La prima è materia MEP.
3. **B1 contro B3 sulla cascata** — il collettore verticale che B3 pretende fa piegare la
   catena che B1 vuole dritta: **la tavola è giusta e il numero dice che è sbagliata.**
4. **Dove sta la presa del ricircolo sanitario.** Sull'impianto 5 sta **all'estremo destro del
   foglio** e la mandata sanitaria attraversa da sola i tre secondari per arrivarci: è lì che
   stanno quasi tutti gli incroci di quella tavola. Contenuto MEP.
5. **Il verso del ricircolo ACS non si ricava** (D-059): mandata e ritorno portano tutt'e due
   `supply=True`, e per questo B10 non vede il ritorno che corre sopra la propria mandata.
   *Serve sapere da lui se il ricircolo è una rete con un verso, o due tratte della stessa.*
6. **Quando si apre il pacchetto DXF** — D-023 e D-148 sono state lasciate andare **perché**
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
