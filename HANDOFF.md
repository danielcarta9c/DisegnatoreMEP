# HANDOFF — Disegnatore MEP · 7 agosto 2026

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
(`skill/capire/COSA_DECIDE.md`).

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

---

## 5. Ordine di lettura

| # | File | Perché |
|---|---|---|
| 1 | Questo file | Cancello |
| 2 | `docs/SKILL.md` | Com'è fatta la skill, la catena, i pezzi |
| 3 | `PROJECT_STATE.md` | A che punto siamo |
| 4 | `docs/plans/2026-08-06-piano-costruzione-skill.md` | Il piano corrente e i verdetti — **l'appendice del 7 agosto ha i tre verdetti nuovi** |
| 5 | `docs/DECISION_LOG.md` — **partire da D-096** | D-096÷D-108 sono la logica del grafo, il confine del prodotto, il regime e le due regole di metodo del 7 agosto |
| 6 | `docs/prodotto/DOVE_VA_CIASCUN_ACCESSORIO.md` | Dove va ciascun pezzo, con la fonte. **La parte terza è il riscontro di D-106, riga per riga** |
| 7 | `docs/adr/0005-*.md` | L'architettura, blindata |
| 8 | `docs/prodotto/GRAFO_IMPIANTO.md` e `docs/prodotto/grafi-di-prova/` | Gli artefatti che il PM legge e approva — **col confronto del 7 agosto** |
| 8b | `examples/prova/input/` | **Il testo originale del committente**, non toccato: è il metro del pezzo 1 |
| 8c | `skill/capire/COSA_DECIDE.md` | **Le quattro cose che l'interprete deve capire**, e quando invece chiede |
| 9 | `AGENTS.md` | Regole operative e i due ruoli |

---

## 6. Stato al 7 agosto 2026

**Ramo:** il lavoro è su `main` (e sul ramo `claude/disegnatoremep-interpreter-validation-6j9vk8`).
**Prove:** 1035 verdi, 22 parcheggiate col motivo scritto, **11 marcate rosse apposta sui
difetti aperti**; `ruff` e `mypy --strict` puliti.
**Ambiente:** `bash scripts/setup-env.sh` — **da eseguire per primo** in una sessione cloud.
**Numeri:** 39 simboli pubblicati, 53 voci di catalogo, 17 regole.

### I pezzi

| Pezzo | Stato |
|---|---|
| **1 — Capire** | **APPROVATO dal collaudo** (7 agosto, al terzo giro). Zero perso e zero inventato su cinque impianti, 67 componenti, 82 tubazioni. Consegne dei tre giri agli atti in `skill/capire/prova-2026-08-07/` |
| **2 — Completare** (le regole) | Costruito e collaudato. **Il pacchetto E (regime + tratto comune) e C2 sono collaudati**: respinti al primo giro, corretti lo stesso giorno, verdi sulle prove dei collaudi adottate come regressione |
| **3 — Assemblare** | Costruito e collaudato; il 7 agosto ha guadagnato la classificazione dei blocchi sul capofila e l'ordinamento dei blocchi di mezzo |
| Il grafo, le sigle e **l'indirizzo dei nodi (D-105)** | **Collaudato e APPROVATO** (7 agosto), 91 prove del collaudo adottate |
| Il vocabolario delle proprietà | Approvato; si aggiungono il bordo macchina e il punto di riempimento come dichiarazioni di catalogo |
| 4 — Disporre / libreria / cartiglio / composizione | Come prima: la composizione è da rifare |
| 5 — Validatori e cancello dell'occhio terzo | Correttezza e preflight esistono, il cancello no |

### Cosa è successo il 7 agosto, sera — la chiusura di «Capire»

- **La prova in camera pulita è costata tre giri**, ed è la lezione da portarsi dietro.
  Il **primo** si è fermato dopo due impianti: due agenti, in due camere separate e senza
  vedersi, hanno trovato che **il kit si contraddiceva** — le istruzioni ordinavano di
  ricavare il regime dalle potenze, lo schema del modello lo vietava per esteso. Era testo
  pre-D-108 sopravvissuto in tre posti. Un kit che si contraddice su una delle quattro
  cose che l'interprete deve capire non misura le istruzioni: misura **quale documento
  l'agente ha letto per ultimo**. Il **secondo** giro è stato respinto su un difetto solo,
  e non sulla fedeltà: §4.2 diceva cos'è una rete e mai **dove una rete può cominciare**,
  e il quinto grafo — fedele, dichiarato, identico al metro — rompeva la catena perché tre
  reti partivano da un raccordo. Il **terzo** è stato approvato.
- **Il difetto non lo ha trovato il confronto, lo ha trovato il determinismo a valle.**
  Sulla fedeltà il pezzo era pulito fin dal secondo giro. Vale la pena ricordarlo: un
  grafo può essere fedele parola per parola e comunque impresentabile al resto della catena.
- **Le due correzioni di fine sessione sono state respinte** da un collaudo indipendente.
  Il nocciolo di entrambe regge, verificato con prove più dure di quelle di casa; i cinque
  difetti stanno ai bordi e riguardano **cose che le correzioni affermano** — che è la
  classe di difetto più respinta della storia del progetto.

### Cosa era successo prima, il 7 agosto

- **Il riscontro di D-106 sugli schemi Caleffi** (Idraulica 61 + i cinque schemi
  applicativi), riga per riga con le citazioni, prima di scrivere qualunque regola.
- **Il pacchetto E**: regime ricavato dalle potenze dichiarate dal progettista (D-108),
  tratto comune deterministico, 17 regole aggiornate come dato, bordo macchina e punto di
  riempimento nel catalogo. Collaudato a contesto separato: respinto su quattro difetti
  veri, corretti lo stesso giorno.
- **C2 corretta**: il bollitore si svuota dall'ingresso freddo; la prova parcheggiata è
  tornata verde senza essere ammorbidita.
- **I cinque grafi rigenerati e messi a confronto** per il PM
  (`docs/prodotto/grafi-di-prova/CONFRONTO-2026-08-07.md`); i successivi rilievi del PM
  hanno poi corretto il ritorno generale dell'ibrido e il regime.
- **Tre collaudi indipendenti**: indirizzo dei nodi APPROVATO (91 prove adottate);
  pacchetto E+C2 RESPINTO e corretto (25 prove adottate); pezzo 1 RESPINTO.
- **Poi i rilievi del PM sul confronto**, e le correzioni: la camminata del ritorno
  generale **si apre sui rami**; il **regime si legge dalle potenze** che lui ha
  dichiarato nei testi; le quattro cose che l'interprete deve capire sono state censite;
  le **tredici correzioni alle istruzioni** sono state applicate.
- **Il quinto impianto è stato riallineato al testo originale**: il testo dice tre
  circuiti secondari e non nomina un collettore. La lettura manuale conserva quindi tutti
  e tre i circuiti e usa due ripartizioni sulla mandata e due confluenze sul ritorno,
  secondo la regola generale dei raccordi a N vie. La vecchia domanda «il collettore ne
  serve due» era un difetto della fixture, non una decisione del progettista.

---

## 7. Il primo lavoro della prossima sessione

**I sei difetti aperti**, che i collaudi hanno inchiodato con prove rosse apposta. Nessuno
è nascosto: ognuno ha il motivo scritto per esteso nella prova, e si chiude quando quella
prova torna verde **senza essere ammorbidita**. L'elenco completo è in `PROJECT_STATE.md`.

1. **I due della camminata del tratto comune**, che sono difetti veri del completatore.
   Sull'**ibrido** il tratto scelto non porta l'acqua che la caldaia rimanda dallo
   scambiatore sanitario, e il corredo ci va lo stesso **in silenzio**; su un **anello**
   il punto scelto cambia col nome delle macchine a topologia identica. La radice è una
   sola: la camminata considera «comune» un tratto **da cui si arriva a tutti i
   generatori risalendo**, mentre le regole dicono che lì deve **passare tutta l'acqua che
   torna**. Non è la stessa cosa, e su due grafi su sette danno risposte diverse.
2. **Il caso di mezzo del regime** (§4.6): potenza dichiarata solo per alcune macchine. Si
   somma il sottoinsieme e si scrive il regime in silenzio. Tre fonti indipendenti l'hanno
   segnalato — un collaudo e due camere pulite che non si vedevano.
3. **Le potenze nel modello.** D-108 promette che l'ingegnere veda la lettura e la
   corregga; nei cinque grafi c'è la conclusione e non il dato. Attenzione: le letture
   manuali sono **il metro** e non si toccano per far combaciare un confronto (`CONSEGNA.md`
   §2, criterio 4) — ma questo non è un aggiustamento del confronto, è un'informazione che
   il testo dà e il modello perde. Da fare **rigenerando il generatore**, mai a mano.
4. **La voce con gli identificativi interni**: si chiude alle **istruzioni**, non
   correggendo l'allegato del verbale.

Poi: **la traduzione in regole** delle posizioni §14-18 rimaste (bilanciamento,
disconnettore, contabilizzatore), dentro il confine di D-104.

**Se si toccano le istruzioni dell'interprete, la prova in camera pulita va rifatta da
capo con agenti nuovi.** Vale sempre, ed è già costato due giri in una sessione sola.

**Non toccare il disegno.** La composizione, l'instradamento e il foglio dei simboli sono
pezzi successivi, e le loro prove sono parcheggiate con il motivo scritto.

---

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

**Una sola osservazione, che non è una domanda.** La soglia dei 35 kW ha radice nella
Raccolta R, che si applica agli impianti con potenza **dei focolari** superiore a 35 kW —
e una pompa di calore focolare non ne ha. Il registro delle fonti lo dice esplicitamente,
e il quinto impianto sono tre pompe di calore. Il PM ha però **già deciso** in D-108 che
la cascata sta sopra la soglia, quindi la pratica è stabilita e non gli si richiede: lo si
segnala perché tre agenti indipendenti ci sono inciampati leggendo lo schema, non perché
serva una sua risposta.

Restano domande per il PM solo quando valgono i criteri di `skill/capire/COSA_DECIDE.md`:
il testo tace, le alternative sono entrambe corrette e la scelta cambia il disegno.

---

## Ultimo aggiornamento

`2026-08-07`, sera — **il pezzo «Capire» è approvato** e i cinque grafi sono rigenerati
dalla pipeline, col quinto finalmente completo dei suoi tre circuiti. La prova in camera
pulita è costata **tre giri**: il primo fermato perché il kit si contraddiceva sul regime
(trovato da due agenti che non si vedevano), il secondo respinto perché §4.2 non diceva
dove una rete può cominciare, il terzo approvato. Consegne di tutti e tre agli atti.

Il collaudo delle due correzioni di fine sessione precedente le ha **respinte entrambe**:
il nocciolo regge, i difetti stanno ai bordi e riguardano cose che quelle correzioni
affermavano. Sono i primi due della lista del §7.
