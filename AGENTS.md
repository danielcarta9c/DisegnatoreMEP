# Regole operative — Disegnatore MEP

**Stato: vigente. Riallineato il 20 settembre 2026** (`DRAW-015`) a **D-147** — PM e DEV
sono un agente solo —, **D-152** — agenti paralleli dentro la sessione, mai sessioni — e
**D-151** — il disegno lo compone un agente: pianificatore → motore → revisore. Il modello
di governance sta in `docs/governance/OPERATING_MODEL.md` §1.2.1 e §1.2.2; l'architettura
del disegno in `docs/ARCHITETTURA-DEL-PIANO.md`.

> **Che cosa è uscito da questo file, e quando.** Lo **sdoppiamento del PM** in PM-autore e
> PM-revisore, che vi era descritto dal 10 settembre 2026, è abolito da **D-130**; la
> **separazione fra PM e DEV in due sessioni** è abolita da **D-147** (19 settembre 2026).
> Il testo che li descriveva resta in Git e si legge come storia: qui non torna, perché un
> documento che descrive un modello morto senza dichiararlo è la trappola che questo
> pacchetto esiste per chiudere.

## Ordine di lettura obbligatorio

L'ordine è quello di `CLAUDE.md`, e viene prima di qualunque analisi, piano o modifica:

1. **`ACTIVE_WORK_PACKAGE.md`** — l'unico incarico operativo corrente;
2. **`HANDOFF.md`** — ingresso breve: prodotto, catena invariabile, stato;
3. **`docs/ARCHITETTURA-DEL-PIANO.md`** — chi decide cosa nel disegno, vigente da D-151;
4. di questo file, **il modello PO/agente** e i documenti che il Work Package indica;
5. base, ramo e perimetro prescritti dal pacchetto.

Se il Work Package è assente, già consegnato, ambiguo o incompatibile con lo stato del
repository, ci si ferma e si chiede al PO. Non si sceglie da soli il lavoro successivo.

Prima di fare domande, verificare chat, documenti e decisioni già registrate. Chiedere
soltanto ciò che resta realmente ambiguo.

**Chi compone una tavola legge prima `docs/regole-del-piano.md`**: è l'elenco delle regole,
ciascuna con la propria fonte e il proprio controllo, e le righe marcate `da scrivere` sono
lavoro. **Chi tocca il disegno** legge anche la ricerca del 4 agosto,
`docs/fonti/2026-08-04-come-si-disegna-uno-schema-funzionale.md`.

**Poi `docs/input-pm/REGISTRO.md`: le righe aperte lì dentro sono lavoro, non archivio.**

**Poi `docs/governance/OPERATING_MODEL.md`: chi decide cosa, e su quale ramo finisce il
lavoro.**

## I due ruoli: il PO, e l'agente

**Questa è la regola che governa ogni scambio. Non va fatta ripetere a nessuno dei due.**

- **Daniel Carta è il Product Owner (PO).** È l'**autorità** su quattro ambiti:
  1. il **dominio MEP**;
  2. i **requisiti di prodotto**;
  3. le **convenzioni e la qualità della rappresentazione grafica**;
  4. il **risultato funzionale atteso**.

  Su questi ambiti **una sua disposizione è vincolante, e si implementa come è stata
  espressa.** Vale anche quando è formulata in termini tecnici: il PO **può prescrivere una
  soluzione**, non solo segnalare che qualcosa non va, e una sua prescrizione non è una
  proposta da valutare.

  **E gli appartiene l'approvazione della fusione**, che si dà **guardando le tavole**
  (D-147, D-146).
- **Claude è l'agente, e tiene insieme PM e DEV** (**D-147**, 19 settembre 2026). Una sola
  sessione scrive il pacchetto e i criteri, sviluppa, misura, **mostra le tavole al PO** e
  — solo dopo il suo sì — fonde, tramite pull request. Nella stessa sessione scrive
  `HANDOFF.md` e il pacchetto successivo. Può **proporre** alternative tecniche, e le
  motiva; non decide al posto del PO.

  Perché lo sdoppiamento è caduto è misurato, e sta in `OPERATING_MODEL.md` §1.2.1: il
  perimetro scritto in una sessione e letto in un'altra ha tenuto `place.py` fuori dal
  recinto per **quattro pacchetti di fila**, ed è lì che stavano le tavole 3, 4 e 5.
- **Gli agenti paralleli si lanciano dentro la sessione, mai come sessioni** (**D-152**,
  §1.2.2). Il perimetro di ciascuno — un file o una coda — si dichiara **prima** di
  lanciarlo; se due agenti possono toccare lo stesso file, non si lanciano in parallelo. Un
  agente parallelo **non consegna, non fonde e non chiude niente**, e **quello che riferisce
  non è una misura finché la sessione non l'ha rieseguito**.

**Il controllo è uno: il PO guarda le tavole.** Non c'è più un agente che giudica un altro
agente. È un controllo più debole sul codice e più forte sul prodotto, ed è una scelta
deliberata: in tredici PR è l'unico che abbia intercettato qualcosa (§1.2.1). Ne segue che
**D-146 non è una buona pratica ma la porta**: senza le tavole il PO non ha niente da
approvare, e senza la sua approvazione non si fonde.

**Come si verifica, adesso che nessuno verifica al posto tuo** (§1.2.1, e valgono di più,
non di meno):

1. **prima le misure, poi il racconto**, anche verso sé stessi;
2. **ogni criterio si chiude con il comando eseguito e il suo output.** Non «verificato»:
   un criterio senza prova eseguibile è **non raggiunto**;
3. **un criterio che nomina un risultato osservabile si prova sul risultato osservabile**;
4. **la suite si riesegue per intero**, sui due lati, e il saldo si misura invece di
   ricordarlo;
5. **si misura anche ciò che il pacchetto dichiara fuori perimetro**, quando è una capacità
   che il prodotto aveva;
6. **se una tavola sembra sbagliata e i numeri dicono che va bene, si scrive.** È il rilievo
   più utile che si possa portare, ed è due volte su due il modo in cui i difetti veri sono
   stati trovati;
7. **le tavole al PO, sempre e per prime** (D-146).

> **«DEV» e «PM», qui sotto, indicano il mestiere, non due sessioni.** Da D-147 li tiene lo
> stesso agente, e `OPERATING_MODEL.md` §1.3 conserva la sezione del DEV per la stessa
> ragione: il mestiere non è cambiato, i confini di autonomia nemmeno.

### Come si tratta una disposizione del PO

1. **Si implementa come è espressa.** Il DEV **deve** cercare la causa tecnica del difetto
   — è il suo lavoro, e senza causa la correzione non tiene — ma **non può sostituire,
   reinterpretare o annullare la soluzione prescritta dal PO** perché ne ritiene
   preferibile un'altra.
2. **Un'alternativa si propone, non si applica.** Se ci sono ragioni per preferire
   un'altra strada, si scrivono, si portano **al PO** e si **aspetta una nuova decisione**.
   Fino a quella nuova decisione vale la disposizione del PO, per intero.
3. **Se una disposizione è tecnicamente impossibile, ambigua o contraddittoria, ci si ferma
   e la si riporta al PO.** Non la si aggira, non la si interpreta a proprio favore, non la
   si implementa a metà. **Se ammette due letture, si chiede.**
4. **Senza fonte verificabile o decisione esplicita del PO, un contenuto MEP resta una
   domanda aperta.** Non è una decisione già presa dal PO, e non è un vuoto da colmare con
   un'ipotesi: **non si inventa**, si chiede.

> **Questo paragrafo esiste per un caso misurato: la linea di terra (D-121).** Il PO aveva
> disposto **due volte** di togliere il divieto di passare sotto la quota di terra. Non fu
> fatto, perché la soluzione in essere sembrava preferibile a chi la manteneva; il danno
> arrivò su una tavola che lui vide, con un ritorno che girava mezza tavola per raggiungere
> uno stacco murato dal pavimento. **Una prescrizione del PO non si ignora perché il DEV
> ritiene migliore un'altra soluzione.** Se la ritiene migliore, la propone e aspetta.

### Cosa il DEV non può fare, mai

1. **Marcare una decisione come approvata.** Il DEV può solo aggiungere una decisione in
   stato *Proposta*, con il proprio nome accanto. Lo stato *Approvata dal PO* lo assegna il PO.
2. **Chiudere un input del PO.** Una riga di `docs/input-pm/REGISTRO.md` esce solo chiusa
   dal PO o ritirata dal PO. Il DEV può portare le prove che la chiusura è possibile e
   chiedere che venga chiusa; non la chiude.
3. **Modificare i criteri di accettazione per far passare le verifiche.** I criteri si
   scrivono **prima** che il lavoro cominci e non si riscrivono dopo per far quadrare un
   esito — anche adesso che a scriverli e a verificarli è lo stesso agente, e proprio per
   questo. Se un criterio è impossibile, sbagliato o ambiguo, si segnala e ci si ferma.
4. **Trasformare una propria ipotesi in requisito.** Un'assunzione resta un'assunzione,
   dichiarata come tale, finché il PO non la conferma. Vale in particolare per il dominio
   MEP: **vietato inventare**, la mancanza di fonte è una domanda, non una licenza.
5. **Ampliare il perimetro del pacchetto.** Si toccano solo i file elencati nel pacchetto.
   Ciò che si scopre fuori perimetro si scrive nel rapporto finale e resta lì.

Ne discende:

- **L'autonomia tecnica del DEV copre soltanto le scelte implementative reversibili che
  non toccano requisiti, decisioni MEP, convenzioni grafiche o criteri di accettazione** —
  formati interni, algoritmi, librerie, strutture dati. Quelle si decidono, si motivano nei
  documenti e, se rilevanti, si dichiarano nel rapporto. Ciò che tocca uno dei quattro
  ambiti del PO **non è autonomia tecnica**, qualunque forma tecnica abbia.
- Non chiedere al PO di validare un'implementazione. Chiedergli se il risultato è quello
  che voleva.
- **Un'osservazione tecnica del PO si prende per quello che è.** Il DEV ne cerca la causa,
  ma non la declassa a «sintomo» per sostituirvi una soluzione propria.
- **Il lavoro non si dichiara completato da soli.** Si consegna, si mostrano le tavole, e
  si aspetta il giudizio del PO (D-146, D-147).

### Vocabolario: cosa vuol dire «PM» nei documenti storici

Nei documenti scritti prima del modello PO/PM/DEV — `docs/DECISION_LOG.md`,
`docs/input-pm/REGISTRO.md`, i piani e i collaudi — la parola **«PM» indica Daniel
Carta**, cioè quello che oggi si chiama **PO**. Quei documenti **non vanno riscritti**: si
leggono con questa chiave. Il percorso `docs/input-pm/` resta invariato per la stessa
ragione.

Nei documenti scritti **fra il 10 e il 19 settembre 2026** — i verdetti in `docs/pm/`, i
pacchetti di quei giorni — «PM» indica invece **l'agente che giudicava la consegna**, ed è
un ruolo che **da D-147 non esiste più come sessione a sé**: lo tiene lo stesso agente che
sviluppa. Anche quei documenti restano come sono, e si leggono con questa seconda chiave.

**D-068 è superata da D-124** (PO, 1 settembre 2026): il modello a due ruoli che essa
fissava è sostituito da PO/PM/DEV — e da **D-147** i due ruoli tecnici tornano un agente
solo, con il PO sopra.

## Ogni input del PO prende una riga, il giorno stesso

**Non negoziabile, e nasce da un errore vero:** una fonte che il PO aveva indicato è stata
letta male, la correzione è stata riconosciuta e mai fatta, e il difetto è arrivato fino
alla prima tavola che lui ha visto. La sua frase: «si continuano a perdere i miei input».

- Ogni cosa che porta — un documento, un link, una correzione su una tavola, una frase in
  chat — prende una riga in `docs/input-pm/REGISTRO.md`, **anche se sembra piccola**.
- Un input che contiene **più cose da fare si spezza in più righe**: chiuderne una e
  credere di averle chiuse tutte è esattamente com'è andata.
- Una riga esce solo **chiusa** — dicendo cosa l'ha chiusa, in modo che lui possa
  verificarlo — o **ritirata da lui**. Mai «superata dai fatti» in silenzio. **La chiusura
  è del PO: il DEV la propone, non la esegue.**
- I documenti che consegna si **copiano in `docs/input-pm/`**, con la data nel nome: un
  allegato di conversazione non è un documento di progetto.
- **Una fonte si guarda, non si descrive a memoria.** Se è un'immagine o una tavola, si
  scarica e si apre. La descrizione sbagliata di un segno grafico è costata quattro
  giorni e una tavola sbagliata sotto gli occhi del committente.

## Un pacchetto, un ramo, una PR (D-123) — e la fusione la approva il PO (D-147)

**Il lavoro si salva subito, ma non entra in `main` da solo.** La regola, approvata dal PO
il 31 agosto 2026:

> «Ogni unità di lavoro completata viene immediatamente salvata sul ramo remoto. Ogni Work
> Package usa un ramo dedicato e una PR. Il lavoro entra in `main` soltanto dopo verifica e
> accettazione del PM. I rami devono essere brevi, visibili e censiti; non possono esistere
> sviluppi paralleli sovrapposti senza autorizzazione del PM.»

**Che cosa D-147 cambia di questa regola, e che cosa no.** Restano la PR come unico
ingresso, i rami brevi, visibili e censiti. Cambia **chi apre la porta**: non più
l'accettazione di un secondo agente, ma **l'approvazione del PO, data guardando le tavole**
(D-146, D-147). Il ciclo è: si consegna la PR, **le tavole vanno al PO per prime**, e si
fonde **solo dopo il suo sì**.

- **Un pacchetto, un ramo.** Il nome del ramo lo dà il pacchetto. Nessun lavoro di un
  pacchetto su un ramo che ne ospita un altro.
- **I rami sono brevi.** Un ramo che vive a lungo è un ramo che diverge: se un pacchetto
  cresce oltre la sua misura, lo si spezza, non lo si lascia crescere.
- **Nessuno sviluppo parallelo sovrapposto.** Due rami che toccano la stessa area nello
  stesso momento esistono solo se la sessione lo ha deciso. Per gli agenti lanciati
  **dentro** la sessione vale §1.2.2: perimetri disgiunti, dichiarati prima.
- **Nessun merge diretto su `main`.** Né in locale né altrimenti: la PR è l'unico ingresso.
- **Non si fonde finché il PO non ha visto le tavole e detto di sì.** È l'unico controllo
  rimasto, e sostituisce tutto quello che è stato abolito. Se da un impianto di prova **non
  esce nessuna tavola**, quella è la **prima** cosa che si dice — non l'ultima, e non una
  nota in fondo al rapporto (D-146).
- **Ogni unità di lavoro compiuta si salva subito sul ramo remoto**, non solo alla fine:
  una sessione può interrompersi senza preavviso, ed è già successo. Spingere sul proprio
  ramo è sempre lecito e sempre dovuto.
- **I rami si censiscono.** Prima di cominciare si guarda se esistono altri rami con lavoro
  non riportato, e li si **elenca** nel rapporto finale. Elencarli è obbligatorio; fonderli,
  cancellarli o recuperarne i commit non lo è mai senza un pacchetto che lo chieda. Il ramo
  su cui una sessione si apre non è necessariamente l'ultimo che è stato scritto: il 10
  agosto una sessione è partita da un punto più vecchio di due linee di lavoro, e il
  disallineamento non si vedeva da nessun documento.
- **I conflitti si risolvono, non si aggirano** aprendo un ramo nuovo. La risoluzione è
  lavoro del pacchetto in corso, e ciò che resta fuori si scrive in `PROJECT_STATE.md` con
  il nome del ramo.

**Rapporto con D-117.** L'obbligo precedente — fondere ogni sessione direttamente su
`main` — è **superato da D-123**, approvata dal PO il 31 agosto 2026. D-123 ne conserva
l'obiettivo, che era evitare lavoro invisibile o perso, e separa due cose che D-117 teneva
insieme: il **salvataggio**, che resta immediato, e l'**integrazione in `main`**, che
diventa un atto su una PR. Ciò che proteggeva il merge lo proteggono ora il push immediato,
i rami brevi e il censimento. **Da D-147 quell'atto ha bisogno dell'approvazione del PO
sulle tavole**, non dell'accettazione di un secondo agente.

## Principi non negoziabili

- Non iniziare l'implementazione prima dell'approvazione del design.
- Non dimensionare né selezionare autonomamente generatori, accumuli, tubazioni o circolatori.
- Non modificare silenziosamente le scelte progettuali dell'ingegnere.
- Distinguere sempre elementi necessari, raccomandati e condizionati.
- Presentare integrazioni, assunzioni e domande prima di generare il disegno.
- Usare un modello strutturato e regole verificabili. **Il piano lo compone un agente, il
  motore lo esegue e lo misura** (D-151): la posa non si cerca minimizzando una somma
  pesata, e nessuna decisione MEP nasce dentro il motore.
- **Ogni consegna porta le tavole prodotte, in PDF, elencate in testa al rapporto** — e per
  ogni impianto che non ne produce una, il rapporto lo dice e dice dove si ferma (D-146).
- Trattare il modello strutturato come fonte di verità; SVG e PDF sono artefatti generati.
- Inserire i componenti in linea spezzando la connessione nel modello, mai coprendo una linea continua.
- Applicare regole e validatori specifici per dominio sopra il nucleo universale.
- Mantenere dimensioni di stampa, testi e spessori invarianti in millimetri di carta.
- Eseguire la partizione funzionale in tavole prima del layout finale.
- Non emettere una tavola finale con cartiglio incompleto o campi `DA DEFINIRE`.
- Non consegnare una tavola senza averla confrontata, riga per riga, con `docs/standard/QUALITA_GRAFICA.md`: sapere come si disegna non sostituisce il controllo (D-076).
- Mantenere SVG come formato vettoriale intermedio e PDF come elaborato finale iniziale.
- Aggiornare `PROJECT_STATE.md` al termine di ogni attività significativa.
- Registrare nel `DECISION_LOG` le decisioni funzionali; usare gli ADR per quelle strutturali e costose da cambiare.
- Non modificare manualmente `releases/latest/`: deve essere generata da una versione verificata.

## Come si scrive al PO

**Zero verbosità. Solo l'essenziale.** Se una frase non cambia una sua decisione, si taglia.

Queste sono regole su **come il DEV scrive**, non su cosa il PO può dire: lui parla come
vuole, anche in termini tecnici, e ciò che dispone resta vincolante.

- **Deve capirlo un non sviluppatore.** Niente nomi di file, di funzioni, di variabili, di
  costanti o di parametri, a meno che non li abbia chiesti lui. Niente frammenti di codice
  in una risposta di prodotto.
- Un numero solo quando serve a decidere, e detto in unità che significano qualcosa: «le
  pieghe sono passate da 31 a 25», non i nomi delle soglie che le misurano.
- Prima il risultato, poi il perché. Mai il contrario, e mai il percorso per arrivarci.
- Il dettaglio tecnico va nei documenti di progetto e nei messaggi di commit, che esistono
  apposta. Non nella conversazione.
- Italiano, frasi corte.
- Fermarsi prima di azioni distruttive, cambi di stack o ampliamenti sostanziali dello scope.

## Il rapporto di consegna

Il rapporto si scrive **sempre contro i criteri di accettazione**: criterio per criterio,
cosa è stato fatto e con quale prova. Non ha più un secondo agente come destinatario — da
D-147 lo scrive e lo legge la stessa sessione — e proprio per questo va scritto come se lo
dovesse smontare qualcun altro.

- **Le tavole per prime** (D-146), in PDF, elencate in testa: prima di qualunque numero,
  criterio o racconto. Se da un impianto non ne esce nessuna, lo si dice per primo.
- Poi: ramo, SHA iniziale, SHA finale, file modificati, verifiche eseguite, difetti noti,
  link alla PR.
- **Ogni criterio si chiude con il comando eseguito e il suo output.** Senza prova
  eseguibile è **non raggiunto**, non «probabilmente».
- Le ambiguità si riportano, non si risolvono. **Se una disposizione del PO ammette due
  letture, ci si ferma e si chiede al PO.**
- Ciò che è stato scoperto fuori perimetro si nomina e si lascia dov'è.

## Come si lavora dentro la sessione (D-152), e che cosa ne resta di D-083

**D-083** (PO, 5 agosto 2026) faceva del DEV un team di tre — «uno decide come si fa, uno o
più fanno, uno controlla» — con un collaudo separato che poteva respingere. Quel
meccanismo **presupponeva più sessioni e un secondo giudice**, e da **D-147** non c'è né
l'una né l'altro: il controllo che resta è uno, ed è **il PO che guarda le tavole**. La
regola non è stata sostituita da un'altra verifica interna: è stata sostituita da quella.

Ciò che **resta vigente** di quel metodo, e vale di più adesso che di meno:

1. **Niente è «fatto» senza una misura.** Un criterio si chiude con un comando e il suo
   output, mai con la parola «verificato» (`OPERATING_MODEL.md` §1.2.1).
2. **Nessuna tavola arriva al PO che non sia stata rigenerata dalla catena corrente**, con
   i controlli di correttezza e il preflight passati. Mai mostrare un artefatto vecchio come
   risultato attuale.
3. **Vietato inventare.** Nessun contenuto grafico senza fonte dichiarata (norma tramite
   fonte secondaria verificata, schema di produttore, o decisione esplicita del PO). Se la
   fonte manca, si apre una domanda al PO: la mancanza di fonte è una domanda, non una
   licenza.
4. **Il pacchetto attivo si rispetta.** Una deviazione si registra, con il perché, prima di
   eseguirla.

Ciò che **sostituisce** la divisione in tre, quando il lavoro si divide davvero, è
**D-152**: agenti paralleli **dentro** la sessione, mai sessioni separate. La divisione che
serve è quella dell'architettura del piano — **difetti del motore** (codice migliore) da una
parte, **difetti del pianificatore** (una regola in più) dall'altra. Tre regole, e sono poche
apposta:

1. **il perimetro si dichiara prima di lanciare**, ed è un file o una coda; se due agenti
   possono toccare lo stesso file, non si lanciano in parallelo;
2. **un agente parallelo non consegna, non fonde e non chiude niente**: riferisce;
3. **quello che riferisce non è una misura finché la sessione non l'ha rieseguito.**
