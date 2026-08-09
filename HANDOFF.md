# HANDOFF — Disegnatore MEP · 9 agosto 2026

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

**Del 9 agosto — uno, ed è il più caro di tutti perché è durato settimane:**

0. **Una spiegazione che nessuno ha misurato ha diretto il lavoro per settimane.** Il
   progetto ha creduto che le tavole non uscissero perché «l'impianto non entra in
   larghezza su un foglio ordinario». Era scritto in ventidue prove parcheggiate, in
   `PROJECT_STATE.md` e nei piani. **Nessuno l'aveva verificata**, e bastava un minuto:
   ricomporre su un foglio più grande. Gli impianti falliscono identici su A0 — il
   problema era un accessorio posato lontano dal proprio pezzo e un attacco murato da una
   valvola altrui. La lezione non è «misura di più»: è che **una spiegazione ripetuta in
   tre documenti sembra verificata anche quando nessuno l'ha mai provata**, e che il modo
   di smascherarla è chiedersi *quale singolo esperimento la falsificherebbe*. Qui era:
   più carta cambia qualcosa? No → non è spazio.

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
| 3b | `INPUT_PROSSIMI_STEP_2026-08-08.md` | **Indirizzo diretto del PM sulla composizione**, consegnato l'8 agosto: la centrale non si spezza, prima si ottimizza il foglio che c'è, quando la distribuzione merita una tavola propria, il formato maggiore per ultimo. Registrato in **D-112** |
| 4 | `docs/plans/2026-08-06-piano-costruzione-skill.md` | Il piano corrente e i verdetti. **L'appendice è un registro storico: le sue righe raccontano com'era allora, non com'è oggi.** Dove una riga è stata superata, ha il rimando scritto sopra |
| 5 | `docs/DECISION_LOG.md` — **partire da D-096** | D-096÷D-112 sono la logica del grafo, il confine del prodotto, il regime, le due regole di metodo del 7 agosto e — **le ultime tre, che sono la specifica del lavoro in corso** — la modalità verifica (D-110), come si compone una tavola (D-111, che emenda D-110) e i vincoli della composizione (D-112: la centrale non si spezza, l'ordine dei rimedi, quando si apre una seconda tavola) |
| 5b | `docs/collaudi/` | I verbali per esteso dei collaudi indipendenti: i criteri che si sono scritti e l'esito di ciascuno |
| 6 | `docs/prodotto/DOVE_VA_CIASCUN_ACCESSORIO.md` | Dove va ciascun pezzo, con la fonte. **La parte terza è il riscontro di D-106, riga per riga** |
| 7 | `docs/adr/0005-*.md` | L'architettura, blindata |
| 8 | `docs/prodotto/GRAFO_IMPIANTO.md` e `docs/prodotto/grafi-di-prova/` | Gli artefatti che il PM legge e approva — **col confronto del 7 agosto** |
| 8b | `examples/prova/input/` | **Il testo originale del committente**, non toccato. Le letture manuali qui accanto sono **il metro** del pezzo 1 e non si toccano, nemmeno dove hanno torto |
| 8c | `skill/capire/COSA_DECIDE.md` | **Le quattro cose che l'interprete deve capire**, e quando invece chiede |
| 8d | `skill/capire/prova-2026-08-07/` | Le consegne dei tre giri della prova in camera pulita: **allegati dei verbali, congelati.** Non si correggono, nemmeno dove sbagliano |
| 9 | `AGENTS.md` | Regole operative e i due ruoli |

---

## 6. Stato al 9 agosto 2026

> ### ⚑ La tavola esce, e il PM ce l'ha in mano
>
> **Tre impianti su cinque escono su una A3, in modalità verifica, in PDF.** È il primo
> risultato che il PM può guardare, ed è quello che aveva chiesto. Si rigenerano con
> `bash scripts/tavole-di-verifica.sh`.
>
> **Il motivo per cui non uscivano non era la carta, e questo va ricordato** perché il
> progetto ci ha creduto per settimane: fallivano identiche anche su A0. Erano due guasti
> della stessa specie, e nessuno dei due si vede contando i millimetri del foglio.
>
> 1. **Gli accessori appesi a uno stacco stavano in una colonna propria**, ordinati per
>    profondità come fossero un passo del processo: lo scarico dell'accumulo si è
>    ritrovato sessanta millimetri a sinistra dell'accumulo, con due macchine in mezzo.
>    Ora stanno accanto al pezzo da cui pendono, dalla parte in cui il loro unico attacco
>    guarda. Ne discende che una macchina con lo stacco sul fondo **si alza da terra**
>    quanto basta a disegnarci sotto, e che un raccordo **si gira** perché il suo stacco
>    guardi dove l'accessorio deve stare.
> 2. **La soglia di un attacco** (D-113): davanti a ogni attacco c'è una cella sola, la
>    sua unica uscita. La valvola di un'altra tratta ci si era seduta sopra, e l'attacco
>    era murato. Ora è riservata.
>
> **Il criterio che distingue le due specie di fallimento, e che vale sempre:** se un
> fallimento di instradamento **non cambia passando a un foglio più grande**, non è una
> questione di spazio. Provarlo costa un minuto e chiude discussioni lunghe.

**Ramo:** `claude/project-docs-first-pdf-obh471`, che parte da `main`.
**Prove:** 1050 verdi, 22 parcheggiate col motivo scritto — **riscritto, perché il
vecchio era falso** — e **11 marcate rosse apposta sui difetti aperti**; `ruff` e
`mypy --strict` puliti.
**Ambiente:** `bash scripts/setup-env.sh` — **da eseguire per primo** in una sessione cloud.
**Numeri:** 39 simboli pubblicati, 53 voci di catalogo, 17 regole.

### I pezzi

> **I nomi dei pezzi sono quelli di `docs/SKILL.md`, e si citano per nome.** Numerarli qui
> in un altro modo è già costato una confusione: «pezzo 3» voleva dire *assemblare* in un
> documento e *disporre* nell'altro.

| Pezzo | Stato |
|---|---|
| **Capire** | **APPROVATO dal collaudo** (7 agosto, al terzo giro). Zero perso e zero inventato su cinque impianti, 67 componenti, 82 tubazioni. Consegne dei tre giri agli atti in `skill/capire/prova-2026-08-07/` |
| **Completare** (le regole) | Costruito e collaudato, **ma con quattro difetti aperti**. Il pacchetto E e C2 furono respinti al primo giro e corretti lo stesso giorno; poi il collaudo delle **due correzioni di fine sessione** (7 agosto, sera) le ha **respinte entrambe**: il nocciolo regge, ma restano i due della camminata del tratto comune, il caso di mezzo del regime e le potenze fuori dal modello. Elenco in `PROJECT_STATE.md`, prove marcate rosse apposta |
| **Assemblare** | Costruito e collaudato; il 7 agosto ha guadagnato la classificazione dei blocchi sul capofila e l'ordinamento dei blocchi di mezzo |
| Il grafo, le sigle e **l'indirizzo dei nodi (D-105)** | **Collaudato e APPROVATO** (7 agosto), 91 prove del collaudo adottate |
| Il vocabolario delle proprietà | Approvato; si aggiungono il bordo macchina e il punto di riempimento come dichiarazioni di catalogo |
| **Disporre** / libreria / cartiglio / **composizione** | **Compone, e tre impianti su cinque escono.** La **modalità verifica** (D-110/D-111) è fatta: indirizzi stampati, foglio scritto anche coi rilievi aperti, PDF a misura reale. Il collocatore ora usa anche l'altezza e sceglie fra poche disposizioni. **Restano:** il quarto e il quinto impianto (larghezza vera, 507 e 945 mm), il riempimento bilanciato come **obiettivo** del collocatore — la misura esiste già nel preflight —, la prenotazione dello spazio in avanti, l'anti-incrocio fra richiami, e il **cartiglio**, che è ancora vuoto |
| **Verificare** — validatori e cancello dell'occhio terzo | Correttezza e preflight esistono, il cancello no |

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

## 6bis. Il primo lavoro della prossima sessione, in una riga ciascuno

1. **Aspettare i rilievi del PM sulle tre tavole** e lavorare su quelli: è il motivo per
   cui esistono. Una sua correzione dice *cosa* è sbagliato, non *perché*: non diventa
   regola finché non si è trovata la fonte (§7, in fondo).
2. **Il criterio della camminata del tratto comune** — i difetti aperti 1 e 2, non fatti
   il 9 agosto perché si è preferito portargli una tavola. Restano il prerequisito del
   ciclo di verifica: oggi lo stesso impianto dà due risposte a seconda di come si
   chiamano le macchine.
3. **Il quarto e il quinto impianto**, che è larghezza vera (507 e 945 mm contro 335).
   L'ordine dei rimedi lo fissa **D-112** e non si salta: stringere davvero, poi la
   seconda tavola **solo se la distribuzione la merita**, poi il formato — e la centrale
   non si spezza mai in automatico.
4. **Il cartiglio**, che è l'ultima cosa che separa una bozza da una tavola.

---

## 7. Il lavoro impostato il 7 agosto sera — **si va sul disegno**

> **Cambio di rotta deciso dal PM la sera del 7 agosto, e va letto prima di tutto il
> resto di questo paragrafo.** Il contenuto si chiude «alla buona» e si porta a casa il
> disegnatore. Motivo suo: *«ho paura che in questa fase di perfezionismo creiamo anche
> regole sbagliate»* — ed è fondato, perché è già successo tre volte (D-102, D-104,
> D-107), sempre scrivendo regole senza poterne vedere l'effetto. Il grafo scritto è
> 300÷500 righe di tabelle: nessuno ci trova un accessorio fuori posto leggendolo. Sulla
> tavola si vede in due secondi.
>
> **Non rompe D-096.** D-096 dice dove si *attribuisce* un difetto, non su cosa lo si
> *scopre*. Il PM guarda la tavola, punta un pezzo, ne legge l'indirizzo; il difetto si
> trova e si corregge **sul grafo**. Le sigle e gli indirizzi sono stati costruiti
> apposta per questo (D-105).

**Le tre cose da fare, in ordine, e poi ci si ferma.** Niente regole nuove in quella
sessione: solo far uscire il disegno.

1. **Il criterio della camminata del tratto comune** — i difetti aperti 1 e 2, che hanno
   una radice sola, spiegata sotto. **Il motivo per farlo prima è concreto: senza, la
   tavola dell'ibrido porta il defangatore su un tratto che già sappiamo essere
   sbagliato**, e non ha senso far scoprire al PM una cosa già scoperta. È lavoro
   contenuto e le prove che lo inchiodano ci sono già.

   *Precisazione, perché non sia sopravvalutato:* la dipendenza dal nome delle macchine
   (difetto 2) si manifesta su un caso **costruito apposta con un anello sul ritorno**.
   Sui cinque impianti reali il collaudo ha provato otto rimescolamenti ciascuno e il
   punto non si è mai spostato: **le cinque tavole di oggi sono già riproducibili.**
2. **La modalità verifica** (D-110, **come emendata da D-111 — leggerle insieme**):
   l'indirizzo del nodo stampato accanto al pezzo. La sigla (`PDC-01`) è **già** stampata
   oggi; l'indirizzo (`CP.01.N.02`) no. L'etichetta sta vicino al nodo **quando c'è
   posto**, altrimenti prende una **linea di richiamo**; un tubo che le passa sopra non è
   un problema e non va evitato. Resta fermo che si posa **dopo** e **non sposta nessun
   pezzo**: le due modalità devono dare la stessa identica tavola, una con un velo in più.
3. **La composizione (D-111 e D-112).** ✅ **Fatta il 9 agosto, e la domanda che questo
   paragrafo poneva ha avuto risposta.** Chiedeva se i fallimenti fossero «piccoli difetti
   del tracciatore» o conseguenze della disposizione stretta. **Erano difetti del
   tracciatore e della posa**, e le tavole sono uscite lo stesso giorno.

   ⛔⛔ **La motivazione scritta nelle 22 prove parcheggiate era FALSA e ha ingannato due
   volte.** Diceva «l'impianto chiede più larghezza di quanta ne abbia un foglio
   ordinario». Non era vero per i primi tre impianti: fallivano identici su **A0**. La
   causa vera è nel §6 qui sopra. La motivazione delle prove è stata riscritta.

   **Dove sta il confine, adesso, misurato impianto per impianto:**

   | impianto | esito |
   |---|---|
   | 1, 2, 3 | **escono su A3** |
   | 4 | fasce per 507 mm contro 335: **larghezza vera**, entra su A2 |
   | 5 | fasce per 945 mm: non entra nemmeno su A1 — è il caso di D-112 |

   **Il resto del quadro:** area utile A3 350 × 235 mm. Il collocatore non dispone più su
   una riga sola: quando la fila non entra confronta poche disposizioni deterministiche e
   prende la meno cara, **impilando ciò che sta in parallelo** — due macchine sono in
   parallelo quando pendono dalle stesse cose, mai due raccordi in fila sulla stessa
   linea — e **scambiando due colonne che nessuna tratta collega**. In altezza il foglio
   resta comunque poco usato: il riempimento misurato è del 35 %.

   **E la soluzione non è «andare a capo»** — l'orchestratore l'aveva proposto e il PM
   l'ha respinto: farebbe ripartire il flusso da sinistra a metà tavola, rompendo
   l'ordinamento da sinistra a destra che è una regola sua. Si dispone in **due
   dimensioni**: macchine principali a sinistra, volumi collocati **lasciandosi lo spazio
   a destra** per il secondario, e i pezzi mossi per soddisfare **più obiettivi insieme**
   — riempimento bilanciato e simmetrico, poche curve, linee corte, nessun accavallamento.
   Le etichette **alla fine**, con richiamo dove non c'è posto, e i richiami disposti **a
   raggera senza incrociarsi**.

   Delle cinque cose, **tre ci sono**: le regole di costo del PM, il **richiamo obliquo**
   che sa già non passare sopra i simboli, e — dal 9 agosto — la capacità di mettere le
   cose **una sotto l'altra** e di scegliere fra le disposizioni possibili, che era il
   nodo tecnico. **Due mancano, ed è il lavoro:**

   - **il riempimento bilanciato e simmetrico come obiettivo**: la misura c'è già nel
     preflight, ma il collocatore non la guarda mentre dispone — la scopre alla fine, con
     un errore. Oggi il foglio è pieno al 35 % contro il 60 % dichiarato;
   - **l'anti-incrocio fra richiami** (la raggera).

   La **prenotazione dello spazio in avanti** è in parte risolta: il collocatore misura
   ora anche ciò che pende da un pezzo, sopra e sotto, e ne riserva il corridoio.

   > ⚠ **«Bilanciato e simmetrico» non va chiesto al PM: è già misurato.** Il preflight
   > controlla il **riempimento minimo del foglio (60 %)** e il **rapporto d'inchiostro fra
   > il quadrante più pieno e il più vuoto (massimo 3)**. Sono esattamente le due cose che
   > il PM ha descritto a parole, e chiedergliele di nuovo sarebbe l'errore di D-102.
   > **Quello che manca non è la misura: è che nessuno la usa come obiettivo mentre
   > dispone** — il collocatore la scopre alla fine, con un errore. Al PM si porta il
   > risultato: appena ci sono due tavole plausibili, si mostrano e si fa dire quale
   > preferisce.

Poi si consegnano le tavole **in modalità verifica** e ci si ferma: comincia il giro delle
correzioni del PM. **Fatto il 9 agosto per tre impianti su cinque**, e il giro delle sue
correzioni è aperto.

**Come si trattano le sue correzioni** (è la sua stessa cautela, D-107 dall'altro lato):
una correzione del PM dice sempre **cosa** è sbagliato, non sempre **perché**. Non diventa
regola finché non si è trovata la fonte o la buona pratica che la conferma. Se non si
trova, si torna da lui a dirlo — non si scrive la regola.

### Il resto, che si rimanda

Gli altri difetti aperti restano scritti in `PROJECT_STATE.md` e **non si toccano ora**:
le due correzioni alle istruzioni dell'interprete costano **un giro intero di camera
pulita ciascuna** e non cambiano niente di ciò che si vede sulla tavola.

### I difetti aperti, e la radice dei due della camminata

Ognuno è inchiodato da una prova marcata rossa apposta, col motivo scritto per esteso, e
si chiude quando quella prova torna verde **senza essere ammorbidita**. Nessuno è
nascosto. **Solo il primo si fa adesso**; gli altri aspettano il disegno.

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
- **Il disegno esce, e il controllo di qualità lo blocca — è un fatto, non un guasto.** La
  catena arriva fino in fondo e produce la geometria; poi il preflight rifiuta di scrivere
  la tavola se c'è un rilievo bloccante (D-063). **Ora c'è il modo di vederla lo stesso:**
  il comando di disegno ha la **modalità verifica**, che stampa gli indirizzi e scrive il
  foglio anche coi rilievi aperti, marcandolo. Non è un'eccezione a D-063 — quella vale
  per la **consegna** — ed è quello che il PM guarda.
- **Le tavole si rigenerano con un comando solo:** `bash scripts/tavole-di-verifica.sh`.
  Escono in `outputs/`, che non è versionata: quello che il PM vede va **mandato**, non
  committato.
- **Il «riempimento bilanciato» è già misurato**, contro quanto qualcuno ha creduto: il
  preflight controlla il **riempimento minimo del foglio (60 %)** e il **rapporto
  d'inchiostro fra il quadrante più pieno e il più vuoto (max 3)**. Non serve inventare
  una metrica nuova né chiederla al PM: esiste, e oggi su una tavola d'esempio dà 24 % e
  3,1. Sono esattamente le due cose che il PM ha descritto a parole. **Manca solo che
  qualcuno le usi come obiettivo mentre dispone**, invece di scoprirle alla fine (§7.3).
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

`2026-08-09` — **la tavola esce.** Tre impianti su cinque escono su una A3 in modalità
verifica, con l'indirizzo di ogni nodo stampato accanto, e in PDF a misura reale. Il PM
li ha in mano: comincia il giro delle sue correzioni.

Il motivo per cui non uscivano **non era la carta**, e il progetto ci ha creduto per
settimane: fallivano identiche anche su A0. Erano due guasti della stessa specie — gli
accessori appesi a uno stacco messi lontano dal proprio pezzo, e la soglia di un attacco
occupata da un accessorio altrui (D-113) — più un ordine di lettura rovesciato, che
veniva dal nome dei sottosistemi invece che dal processo.

Prima del disegno, un giro sulla documentazione: **sei incoerenze chiuse**, fra cui la
motivazione falsa che aveva già ingannato due volte, e l'indirizzo del PM dell'8 agosto
registrato come **D-112**.

**Non fatto**, e resta il primo lavoro: il criterio della camminata del tratto comune.
