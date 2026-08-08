# HANDOFF — Disegnatore MEP · 8 agosto 2026

> ⛔ **Non è un riassunto del progetto.** È il cancello di lettura per la sessione
> successiva. Si legge tutto, poi si risponde alle domande del §2, poi si comincia.
>
> **Chi ha fretta legge questo file e `docs/SKILL.md`. Sono sufficienti per capire cosa
> stiamo costruendo e da dove si riparte.** Tutto il resto si apre quando serve.

---

## 1. Cosa stiamo costruendo, in una pagina

Una **skill** che trasforma un impianto termotecnico **già deciso e dimensionato
dall'ingegnere** in una tavola tecnica. Non progetta, non dimensiona, non sceglie le
macchine: aggiunge gli accessori che un impianto deve avere, li fa approvare, e disegna.

**La frase del PM che definisce il prodotto, e che va tenuta a mente sempre** (D-104):

> «Io sono un buon ingegnere ma non sono un disegnatore MEP super senior. Per questo nasce
> la skill: per far disegnare quello che so fare benissimo — lo schema a livello di
> definitivo — e portarlo a livello più esecutivo.»

Ne discende il confine: **la skill mette le valvole, uno sfiato e quattro accessori
standard. Non decide quanti pezzi ci vanno, non cambia lo schema ricevuto, non
dimensiona.** E da D-106 e D-108: **il regime della centrale — sotto o sopra i 35 kW — è
un dato del progettista**, e la skill lo **legge** dalle potenze che lui ha scritto:
sommarle e confrontarle con la soglia non è dimensionare. Se le potenze non ci sono, il
regime resta non dichiarato, vale il corredo minimo, e quella è una domanda.

### La catena (D-099)

```
l'ingegnere spiega l'impianto a parole
   → l'AI interpreta                        GRAFO DI PRIMA STESURA
   → le regole dicono cosa manca e perché
   → l'assemblatore dice dove va ciascuno   GRAFO DEFINITIVO
   → ★ L'INGEGNERE APPROVA                  cancello: niente si disegna prima
   → l'instradatore dispone e disegna        con i criteri di costo del PM
   → i validatori verificano
   → ★ L'OCCHIO TERZO GIUDICA               cancello: può respingere
   → la tavola
```

**Una cosa sola attraversa tutto: il grafo.** Nasce abbozzato, si arricchisce di nodi,
diventa definitivo. La tavola ne è la **rappresentazione**.

### Il grafo, come è fatto (D-097, D-098, D-100, D-101, D-105)

Come una **rete stradale**. Ogni pezzo è un **nodo con la propria sigla**; ogni tubo fra
due pezzi è un **arco** col proprio fluido. Le sigle si assegnano camminando dalle
**sorgenti dichiarate**, seguendo l'acqua. Ogni linea idraulica ha nome e numero
(`CP.01`), ogni pezzo un indirizzo (`CP.01.N.02`), gli stacchi i civici (`CP.01.N.02.1`).

**Ogni attacco porta una tubazione sola, sempre** (D-100). Dove due tubazioni si
incontrano c'è un pezzo che le unisce, con la propria sigla: una **confluenza** se due
diventano una, una **ripartizione** se una si sdoppia.

**Una macchina ha più attacchi di quelli del flusso** (D-101), e il catalogo dichiara
anche **cosa porta a bordo di fabbrica** e **da quale attacco la riserva si riempie**
(D-106, C2). Un accessorio che pende da uno stacco va sull'attacco di servizio se la
macchina ce l'ha, su una derivazione se non ce l'ha — e una riserva che dichiara il punto
di riempimento riceve le derivazioni **solo lì**: da dove si riempie, da lì si svuota.

**Il corredo di rete sta sul tratto comune** (D-106): vaso, riempimento, manometro e
defangatore sul **ritorno generale, a monte della prima ripartizione** verso le macchine
— trovato camminando sulla struttura, mai scelto dall'ordine del file. Dove il tratto
comune non esiste, il punto aperto lo dice e la scelta torna al progettista.

### Dove si guarda cosa (D-096) — la regola che ha cambiato il progetto

**Il contenuto si giudica sul grafo scritto, non sul disegno.** Se il grafo è giusto e la
tavola è brutta, il difetto è nel disporre. Se il grafo è sbagliato, la tavola non c'entra.

---

## 2. Sentinel checks — rispondere prima di toccare qualunque cosa

1. Qual è l'unico oggetto che attraversa tutta la skill, e perché la tavola non è un
   oggetto a sé?
2. Su cosa si giudica il **contenuto** e su cosa il **disegno**?
3. Quante tubazioni porta un attacco, e cosa c'è dove due tubazioni si incontrano?
4. Dove va un accessorio che pende da uno stacco, e chi decide quale dei due casi vale?
5. Una norma dice che un impianto deve avere un certo dispositivo: la skill può
   aggiungerlo di propria iniziativa?
6. Chi decide l'ordine dei pezzi lungo un tubo, e su cosa lo decide?
7. Cosa deve succedere quando una regola si applica ma il catalogo non ha il pezzo adatto
   a quel fluido — o la rete non ha il tratto comune su cui la regola si posa?
8. Chi decide il regime della centrale, come si ricava, e cosa vale se non si ricava?
9. Quali sono le **quattro cose** che l'interprete deve capire dal testo, e qual è il
   criterio per cui una cosa non decisa si **chiede** invece di dichiararla?
10. Sulla tavola c'è una linea di terra su cui le macchine appoggiano? E **spostare un
    componente o un'intera colonna quanto costa?**

*Risposte attese:* il grafo, e la tavola ne è la rappresentazione; il contenuto sul grafo
scritto, il disegno sulla tavola (D-096); **una sola**, e dove se ne incontrano due c'è un
raccordo con la propria sigla (D-100); sull'attacco di servizio della macchina se ce l'ha,
altrimenti su una derivazione, e lo dice **il catalogo** (D-101) — e se la riserva dichiara
da dove si riempie, la derivazione va solo lì (C2); **no** — una prescrizione dice cosa
deve avere l'impianto, non autorizza la skill ad aggiungerlo (D-104); l'**assemblatore**,
risolvendo i vincoli che ogni regola dichiara rispetto ai **mestieri** degli altri pezzi,
mai numeri di priorità (D-094); lo deve **dire** — punto aperto per il progettista, con il
motivo vero (pezzo mancante in catalogo, o tratto comune che non esiste), mai tacere;
il **progettista**, e la skill lo **legge dalle potenze che lui ha dichiarato**
(D-108); se il testo non le dà, vale il **corredo minimo** e si chiede; le quattro cose
sono che macchina è ciascun pezzo, che acqua porta ogni circuito, il regime, e come i
circuiti toccano una riserva — si chiede solo quando il testo tace **e** le due strade
sono entrambe corrette **e** la scelta cambia il disegno
(`skill/capire/COSA_DECIDE.md`); **no, la linea di terra non esiste** — non è mai stata
decisa, nasceva da una proporzione misurata su una tavola del PM e promossa a divieto, ed
è stata ritirata (D-116) — e **spostare non costa niente**: si penalizzano le conseguenze
— lunghezza, curve, incroci, ritorni a sinistra, congestione, squilibrio — mai il
movimento (D-119).

---

## 3. Il metodo, che è vincolante (D-083)

**Tre ruoli: uno decide, uno o più fanno, uno controlla.** L'orchestratore scrive i criteri
di accettazione **prima**; sviluppatori separati eseguono; un collaudo **a contesto
separato** verifica e può respingere. I verdetti si registrano nell'appendice del piano.

Quattro regole ferree:

1. Niente è «fatto» senza verdetto positivo del collaudo, registrato.
2. Nessuna tavola arriva al PM senza il cancello completo, rigenerata il giorno stesso.
3. **Vietato inventare.** Se la fonte manca è una domanda per il PM, non una licenza. E se
   la fonte **esiste** — un catalogo, una norma — si va a cercarla invece di chiedere
   (D-102).
4. Il piano approvato si rispetta; una deviazione si registra **prima** di eseguirla.

**Come si scrive al PM:** zero verbosità, italiano, frasi corte, nessun nome di file o di
funzione, deve capirlo un non sviluppatore.

---

## 4. ⛔ Gli errori di metodo da non ripetere

**Della sessione del 6 agosto — lo stesso errore tre volte:** un segnale laterale
trattato come lavoro da fare invece di finire il pezzo (un rigo di norma trasformato in
regola, ritirato in D-104; il disegno inseguito in una sessione sul contenuto; domande al
PM che avevano risposta nei cataloghi — «io potrei sbagliare»). Quando succede, fermarsi
e tornare al pezzo.

**Della sessione del 7 agosto — quattro. Due colti dai collaudi:**

1. **Un criterio implementato a metà è un criterio violato.** «Una regola non aggiunge
   ciò che la macchina dichiara di avere» era stato cablato per il solo ambito di rete:
   le regole per attacco aggiungevano lo stesso, e — il rovescio, più grave — il bordo di
   una macchina spegneva **in silenzio** la sicurezza del serbatoio. Il collaudo lo ha
   respinto; la correzione è dello stesso giorno. La lezione: quando un criterio dice
   «una regola», va provato su **ogni specie** di regola, non sulla prima che capita.
2. **Un'affermazione che il PM non può verificare è un difetto anche quando il pezzo è
   giusto.** Il vaso sanitario era al posto giusto ma firmato dalla regola sbagliata nel
   dossier; un punto aperto diceva «manca il pezzo in catalogo» quando a mancare era il
   tratto comune; una fonte affermava più di quanto il riscontro documentasse. Tre facce
   della stessa classe (D-085, D-039, D-103), la più respinta della storia del progetto.

**E due colti dal PM, che sono le due facce dello stesso errore — non fare il proprio
lavoro** (D-107 e D-108). Vanno letti insieme, perché correggerne uno solo fa cadere
nell'altro:

3. **Una mezza frase del PM non è una fonte.** A una sua domanda retorica — «io voglio
   il filtro?» — stavo per rispondere con una regola che mette il filtro a Y sull'acqua
   calda sanitaria di un impianto domestico, dove non ci va. Le sue parole si
   **verificano** sulle fonti e sulla buona pratica prima di diventare regole, e una sua
   domanda non è un ordine. È la terza volta: prima le domande girate a lui che avevano
   risposta nei cataloghi, poi il rigo della Raccolta R diventato tre regole.
4. **Ciò che si può ricavare non si chiede.** Gli avevo portato come domanda il regime
   dei cinque impianti: ma le potenze le aveva scritte lui nei testi, e sommarle non è
   progettare. «Sei serio?». Delle tre domande che gli erano state portate, due erano
   mie da risolvere.

**Della sera del 7 agosto — uno solo, e costa un giro di prova ogni volta:**

5. **Una prova non misura niente se il materiale che le dai si contraddice.** La prova in
   camera pulita è stata lanciata con un kit in cui le istruzioni ordinavano di ricavare
   il regime dalle potenze e lo schema del modello lo vietava per esteso: due agenti
   l'hanno trovato, il giro è stato buttato. Era una frase pre-D-108 rimasta in piedi in
   tre posti. La lezione non è «leggi meglio»: è che **quando una decisione cambia una
   regola, la stessa frase va cercata ovunque sia stata scritta** — regola del gioco n. 6,
   cercare tutti i simili, applicata ai documenti e non solo ai difetti. Prima di lanciare
   una prova che costa cinque agenti, vale la spesa di un `grep` sul kit.

**Dell'8 agosto — uno solo, ed è nuovo di specie:**

6. **Una regola che nessuno ha mai chiesto va ritirata, non aggirata.** La «linea di
   terra» non compare in nessuna decisione: nasceva da una proporzione **misurata** su una
   tavola di riferimento del PM e promossa a **divieto** in due punti del motore. È stata
   aggirata **due volte** — il 4 agosto spostando l'ingresso freddo di un bollitore, l'8
   spostando lo scarico dei volani — e la seconda volta la domanda è pure stata portata al
   PM formulata su quel presupposto. Nessuno ha chiesto **da dove venisse** finché non
   l'ha fatto lui. Quando un vincolo costa due aggiramenti identici, il vincolo è
   l'imputato: si va a cercare la riga che lo istituisce, e se non c'è, non è una regola.

**E due errori di consegna, della stessa giornata:** una tavola mostrata al PM su un
foglio **A0 costruito come banco di misura**, cioè su un formato che nel prodotto non
esiste, con scritto «l'impianto si compone» quando si componeva solo lì; e una diagnosi
scritta nel registro — «è la disposizione» — che era dedotta dai sintomi invece che
misurata, e ha dovuto essere corretta nella riga stessa. Sono la classe di difetto più
respinta della storia del progetto: **un'affermazione che il PM non può verificare.**

---

## 5. Ordine di lettura

| # | File | Perché |
|---|---|---|
| 1 | Questo file | Cancello |
| 2 | `docs/SKILL.md` | Com'è fatta la skill, la catena, i pezzi |
| 3 | `PROJECT_STATE.md` | A che punto siamo |
| 4 | `docs/plans/2026-08-06-piano-costruzione-skill.md` | Il piano corrente e i verdetti. **L'appendice è un registro storico: le sue righe raccontano com'era allora, non com'è oggi.** Dove una riga è stata superata, ha il rimando scritto sopra |
| 5 | `docs/DECISION_LOG.md` — **partire da D-096** | D-096÷D-111 sono la logica del grafo, il confine del prodotto, il regime, le due regole di metodo del 7 agosto e — **le ultime due, che sono la specifica del lavoro in corso** — la modalità verifica (D-110) e come si compone una tavola (D-111, che emenda D-110) |
| 5b | `docs/collaudi/` | I verbali per esteso dei collaudi indipendenti: i criteri che si sono scritti e l'esito di ciascuno |
| 6 | `docs/prodotto/DOVE_VA_CIASCUN_ACCESSORIO.md` | Dove va ciascun pezzo, con la fonte. **La parte terza è il riscontro di D-106, riga per riga** |
| 7 | `docs/adr/0005-*.md` | L'architettura, blindata |
| 8 | `docs/prodotto/GRAFO_IMPIANTO.md` e `docs/prodotto/grafi-di-prova/` | Gli artefatti che il PM legge e approva — **col confronto del 7 agosto** |
| 8b | `examples/prova/input/` | **Il testo originale del committente**, non toccato. Le letture manuali qui accanto sono **il metro** del pezzo 1 e non si toccano, nemmeno dove hanno torto |
| 8c | `skill/capire/COSA_DECIDE.md` | **Le quattro cose che l'interprete deve capire**, e quando invece chiede |
| 8d | `skill/capire/prova-2026-08-07/` | Le consegne dei tre giri della prova in camera pulita: **allegati dei verbali, congelati.** Non si correggono, nemmeno dove sbagliano |
| 9 | `AGENTS.md` | Regole operative e i due ruoli |

---

## 6. Stato all'8 agosto 2026

**Ramo:** `claude/disegnatoremep-main-resume-890881`, allineato a `origin`.
**Prove:** 1054 verdi, 22 parcheggiate col motivo scritto, **12 marcate rosse apposta
sui difetti aperti**; `ruff` e `mypy --strict` puliti su `src`, `tests` ed `examples`.
**Ambiente:** `bash scripts/setup-env.sh` — **da eseguire per primo** in una sessione cloud.
**Numeri:** 39 simboli pubblicati, 53 voci di catalogo, 17 regole.

### I pezzi

| Pezzo | Stato |
|---|---|
| **1 — Capire** | **APPROVATO** dal collaudo (7 agosto) e **riprovato l'8 agosto end-to-end**: un agente in camera pulita ha letto l'impianto 1 dal testo del committente e ha consegnato al primo colpo — grafo valido, 8 domande dichiarate, regime ricavato dalle potenze senza chiederlo. Consegne agli atti in `skill/capire/prova-2026-08-07/` e `prova-2026-08-08-impianto-1/` |
| **2 — Completare** (le regole) | Costruito e collaudato. **I due difetti della camminata sono chiusi** (D-112): il tratto comune si riconosce togliendolo, e il nome delle macchine non decide più niente. Restano il caso di mezzo del regime e le potenze fuori dal modello |
| **3 — Assemblare** | Costruito e collaudato |
| Il grafo, le sigle e l'indirizzo dei nodi | **APPROVATO**, 91 prove del collaudo adottate |
| **4 — Disporre** | **È il lavoro.** La modalità verifica è **fatta** (D-114); la grammatica delle fasce è **fatta** (D-119, primo dei tre pezzi). **Una tavola esce**: l'impianto 4, su A3, con tutti i 41 indirizzi. Le altre quattro no |
| 5 — Validatori e cancello dell'occhio terzo | Correttezza e preflight esistono, il cancello no |

### Cosa è successo l'8 agosto — otto decisioni, e tre erano regole mai chieste

- **D-112, il tratto comune si riconosce togliendolo.** Se il circuito di una macchina si
  chiude lo stesso, quel tratto la sua acqua non la porta. **Conseguenza sostanziale:
  l'ibrido non ha un ritorno generale** — il ramo del sanitario rientra a valle — quindi
  vaso, riempimento, manometro e defangatore escono come **quattro punti aperti**. La
  frase «nessuno dei cinque ha punti aperti» era falsa ed è stata corretta.
- **D-114, la modalità verifica.** `draw --verifica --naming` stampa l'indirizzo accanto a
  ogni pezzo; `draw --anche-se-respinta` scrive la tavola anche coi rilievi bloccanti,
  dicendo che non è una consegna. L'invariante di D-110 è provato **sulla carta**: la
  tavola di consegna è una sottosequenza esatta di quella di verifica.
- **D-113, perché la composizione falliva** — e la prima risposta scritta lì era
  sbagliata, corretta lo stesso giorno misurando.
- **D-115 e D-116, due regole che nessuno aveva mai chiesto.** Lo scarico dei serbatoi era
  murato dal pavimento; e **la linea di terra non era mai stata decisa** — nasceva da una
  proporzione *misurata* su una tavola del PM e promossa a divieto in due punti del
  motore. Ritirata. Costava due aggiramenti identici, il 4 e l'8 agosto.
- **D-117, la fascia si piega in colonne**, e la piega si sceglie provandola.
- **D-118, un buco della catena: nessuno crea i sottosistemi.** Le istruzioni ordinano
  all'interprete di lasciarli vuoti; nessun pezzo successivo li crea. Le cinque letture
  manuali li hanno scritti a mano, quindi **le fixture stavano coprendo il buco**.
- **D-119, la grammatica MEP di partenza**, dettata dal PM. È la specifica del lavoro che
  resta: leggerla per intera prima di toccare il collocatore.

## 7. Il primo lavoro della prossima sessione

**La specifica è D-119, e va letta per intera.** Il PM l'ha dettata l'8 agosto: una
grammatica di partenza, il movimento gratis, il costo sulle conseguenze. Dei tre pezzi
**uno è fatto**:

1. ~~**La grammatica di partenza**~~ — **FATTA** (D-119). Le fasce si leggono dal
   **mestiere dichiarato in catalogo** quando i sottosistemi mancano: generatori a
   sinistra, volumi subito a destra, distribuzione dopo, terminali per ultimi. Misurato
   sull'impianto 1: le fasce tornano quattro invece di una, e **le due pompe di calore si
   impilano**.

2. **⛔ MUOVERE È GRATIS — è il pezzo che blocca il disegno.** Oggi lo stacco fra due
   colonne è una **costante** (`ROW_GAP_MM`, 15 mm). Quando fra due colonne devono entrare
   degli accessori e non ci stanno, il motore **fallisce** invece di allontanare la
   colonna dopo. Il PM, alla lettera: *«non comprimere i pezzi e non creare tubazioni
   contorte: sposta la colonna successiva e, se necessario, tutto ciò che viene dopo. Le
   colonne possono allontanarsi, avvicinarsi o traslare verticalmente liberamente.»*
   È qui che si fermano quattro delle cinque tavole.

3. **Il costo sulle conseguenze.** Curve, incroci e lunghezza ci sono già
   (`layout/improve.py`). Mancano il **ritorno innaturale verso sinistra**, la
   **congestione** e lo **squilibrio del riempimento** — quest'ultimo è già *misurato* dal
   preflight (60 % e rapporto fra quadranti) ma non è obiettivo di nessuno.
   E resta D-041: **un incrocio leggibile costa meno di una tubazione lunga fatta solo per
   evitarlo.**

**Poi si rigenerano le cinque tavole in modalità verifica e si portano al PM.** È il ciclo
che aspetta da due sessioni: lui guarda, punta un pezzo, ne legge l'indirizzo, e da lì si
correggono le regole su casi veri.

### Il buco dei sottosistemi (D-118), che è una domanda aperta

Nessun pezzo della catena crea i sottosistemi. La grammatica di D-119 ci gira intorno —
legge le fasce dal mestiere — ma il piano di impaginazione di D-042 resta senza un
ingresso. Va deciso **dove** si chiude: se li scrive l'interprete (e cambiano le
istruzioni), se serve un pezzo nuovo fra assemblatore e disegnatore, o se il collocatore
lavora sempre senza. **Non deciderlo da soli.**

### I difetti aperti

Stanno in `PROJECT_STATE.md`, ognuno inchiodato da una prova marcata rossa col motivo
scritto per esteso, e si chiude quando quella prova torna verde **senza essere
ammorbidita**. Nessuno è nascosto.

### Come si trattano le correzioni del PM

Una correzione dice sempre **cosa** è sbagliato, non sempre **perché**. Non diventa regola
finché non si è trovata la fonte o la buona pratica che la conferma; se non si trova, si
torna da lui a dirlo. **Ma attenzione al rovescio, che l'8 agosto è costato caro:** una
regola che *nessuno* ha mai chiesto va ritirata, non aggirata. La linea di terra è stata
aggirata due volte prima che qualcuno chiedesse da dove venisse.

## 8. Quirks e gotcha

- **Eseguire sempre la suite completa** e `mypy src tests examples`, mai il solo file del
  task.
- **Mai `git checkout --` o `git stash` su lavoro non committato** senza averne prima
  salvato una copia.
- **Il comando delle regole vuole anche `--naming`** oltre a `--catalog`, `--symbols` e
  `--rules`.
- **I generatori di fixture vanno rieseguiti**, non modificati a mano. La `completa` si
  rigenera con `saturate` sull'essenziale (la prova che la inchioda dice come);
  il catalogo di prova esce da `examples/layout/build_layout_fixtures.py`, ma **22 voci
  sono file di dato autonomi** (accessori) che si modificano direttamente.
- **Firma dei commit:** in questo container `commit.gpgsign` è attivo con una chiave vuota.
  Si committa con `git -c commit.gpgsign=false`.
- **Gli agenti di sviluppo non committano.** Committa l'orchestratore.
- **Gli agenti in parallelo muoiono per il limite di spesa mensile dell'account**, a metà
  lavoro e senza preavviso: è successo due volte (uno è morto senza lasciare **nulla**).
  Prima di rifare, guardare il worktree che lasciano. I collaudi su worktree isolato
  devono crearsi la propria `.venv` con `setup-env.sh`.
- **`air_release` è lo sfogo, `air_separation` il separatore**: due mestieri, due pezzi.
  Il braccio `vent` dei serbatoi serve `air_release`.
- **La prova in camera pulita del pezzo 1 non si fa da contaminati**, e le **consegne degli
  agenti si conservano agli atti**: kit e divieti in `skill/capire/CONSEGNA.md`. Gli
  esempi delle istruzioni sono stati sostituiti con casi estranei ai cinque testi di
  prova; dopo ogni modifica alle istruzioni la prova va rifatta da capo.
- **Il disegno esce, e il controllo di qualità lo blocca — è un fatto, non un guasto.** La
  catena arriva fino in fondo e produce la geometria; poi il preflight rifiuta di scrivere
  la tavola se c'è un rilievo bloccante (D-063). Per **vedere** una tavola durante il
  lavoro c'è ora `draw --anche-se-respinta`, che la scrive e dice a voce alta che non è
  una consegna. *Fino all'8 agosto questa riga descriveva la scorciatoia come esistente e
  **non esisteva**: `draw` tornava `2` prima di scrivere qualunque cosa.*
- **Il «riempimento bilanciato» è misurato a valle, e non è obiettivo di nessuno a monte.**
  Il preflight controlla il **riempimento minimo del foglio (60 %)** e il **rapporto
  d'inchiostro fra il quadrante più pieno e il più vuoto (max 3)**: su una tavola
  d'esempio dà 24 % e 3,1, verificato. **Tre avvertenze, perché questa riga ha già
  ingannato:** (a) sono **avvisi, non bloccanti** — quei numeri non impediscono niente;
  (b) le due misure **non sono omogenee** — il 60 % è il rapporto di un rettangolo di
  ingombro, il «max 3» è area d'inchiostro vera; (c) **la simmetria non è misurata da
  nessuno**, ed è metà di ciò che il PM ha chiesto. Quindi la metrica c'è e non va
  reinventata, ma non è vero che al PM non si debba chiedere nulla: le due soglie si
  dichiarano da sole «taratura, non norma, da rivedere sulle tavole reali». Sopra ogni
  cosa: **il collocatore non ottimizza nessuna delle due** — le scopre alla fine.
- **Prima di lanciare la prova, controllare che il kit non si contraddica.** Il kit sono
  cinque documenti — istruzioni, testo, catalogo, tabelle dei nomi, schema — e lo schema
  porta prosa che può invecchiare. È già costato un giro intero. Il modo pratico:
  allestire le cartelle con lo script e fargli fare il riscontro sulle frasi che una
  decisione recente ha cambiato.
- **Le consegne degli agenti sono allegati del verbale e non si correggono a mano**,
  nemmeno per un difetto piccolo: se il grafo di un agente viola una regola, la regola si
  chiude nelle **istruzioni** e la prova si rifà.
- **Due osservazioni non bloccanti dei collaudi da chiudere al prossimo passaggio sui
  file**: l'ordine interno di `run_pipes` nella lettura delle linee segue il file (nessun
  consumatore lo usa: ordinare o documentare); il ramo silenzioso della camminata del
  tratto comune quando non c'è né camminata né ripiego.

---

## 9. Domande aperte per il PM

**Nessuna sul quinto impianto, e la questione è chiusa nei fatti.** Il grafo pubblicato
porta ora tutti e tre i circuiti secondari — batterie UTA, ventilconvettori, pannello
radiante — e il collettore non c'è più: il testo non lo nominava.

**Nessuna, e una è stata appena chiusa: non riproporla.** Era stato osservato che la
soglia dei 35 kW ha radice nella Raccolta R, che parla di potenza **dei focolari**, e che
una pompa di calore focolare non ne ha. **Il PM ha chiuso l'osservazione (D-109):** le
centrali domestiche in cui si sostituisce una caldaia a gas con una pompa di calore
stanno **sempre sotto i 35 kW**, e la skill **non è limitata alle rinnovabili** —
disegnare centrali a caldaia a gas è nel suo perimetro, e lì il focolare c'è davvero.
Niente eccezione da scrivere, niente da chiedere.

**E una precisazione di perimetro che ne discende:** le fonti rinnovabili sono l'**MVP,
non il confine del prodotto**. Nessuna regola va scritta assumendo che il generatore sia
una pompa di calore; il catalogo la caldaia a gas ce l'ha già.

Restano domande per il PM solo quando valgono i criteri di `skill/capire/COSA_DECIDE.md`:
il testo tace, le alternative sono entrambe corrette e la scelta cambia il disegno.

---

## Ultimo aggiornamento

`2026-08-08` — **la prima tavola del progetto esce**: l'impianto 4, su A3, in modalità
verifica, con tutti i 41 indirizzi. Otto decisioni (D-112÷D-119), di cui **due ritirano
regole che nessuno aveva mai chiesto** — la linea di terra e lo scarico murato. E la prima
prova end-to-end vera, dal testo del committente alla tavola con un agente in camera
pulita, che ha trovato un buco che le fixture coprivano: nessuno crea i sottosistemi.

Il lavoro che resta è **D-119, punto 2: muovere è gratis.** È lì che si fermano quattro
tavole su cinque.
