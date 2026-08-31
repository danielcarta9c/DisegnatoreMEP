# Regole operative — Disegnatore MEP

## Ordine di lettura obbligatorio

**`HANDOFF.md` per primo: è il cancello di lettura e contiene le sentinel checks a cui
rispondere prima di toccare qualunque cosa.** Poi `docs/SKILL.md` (com'è fatta la skill) e
`PROJECT_STATE.md` (a che punto siamo). Il resto si apre quando serve, nell'ordine che
l'handoff indica.

Prima di fare domande, verificare chat, documenti e decisioni già registrate. Chiedere
soltanto ciò che resta realmente ambiguo.

**Poi `docs/input-pm/REGISTRO.md`: le righe aperte lì dentro sono lavoro, non archivio.**

**Poi `docs/governance/OPERATING_MODEL.md`: chi decide cosa, e su quale ramo finisce il
lavoro.**

## I tre ruoli: PO, PM, DEV

**Questa è la regola che governa ogni scambio. Non va fatta ripetere a nessuno dei tre.**

- **Daniel Carta è il Product Owner (PO)** ed è l'autorità sul dominio MEP. Dice *cosa*
  deve fare il prodotto e se il risultato è quello che voleva. Le sue correzioni non sono
  mai tecniche: se dice «questa tavola è fatta male» sta dicendo *cosa* non va nel
  prodotto, e tocca al DEV trovare *perché* e *come*. Ogni contenuto tecnico di dominio
  privo di fonte è una sua decisione, non un'ipotesi da colmare.
- **Codex è il Project Manager (PM).** Assegna i pacchetti di lavoro, ne scrive i criteri
  di accettazione **prima** che il lavoro cominci, giudica le consegne e le **approva o
  respinge**. Porta al PO ciò che è del PO: cosa deve fare il prodotto, priorità, costi,
  compromessi.
- **Claude è il DEV team.** Esegue il pacchetto assegnato dentro il perimetro dichiarato.
  Può **proporre** alternative tecniche, e le motiva; non decide al posto del PO né al
  posto del PM.

### Cosa il DEV non può fare, mai

1. **Marcare una decisione come approvata.** Il DEV può solo aggiungere una decisione in
   stato *Proposta*, con il proprio nome accanto. Lo stato *Approvata* lo assegna il PO.
2. **Chiudere un input del PO.** Una riga di `docs/input-pm/REGISTRO.md` esce solo chiusa
   dal PO o ritirata dal PO. Il DEV può portare le prove che la chiusura è possibile e
   chiedere che venga chiusa; non la chiude.
3. **Modificare i criteri di accettazione per far passare le verifiche.** I criteri sono
   del PM. Se un criterio è impossibile, sbagliato o ambiguo, si segnala e ci si ferma:
   non si riscrive.
4. **Trasformare una propria ipotesi in requisito.** Un'assunzione resta un'assunzione,
   dichiarata come tale, finché il PO non la conferma. Vale in particolare per il dominio
   MEP: **vietato inventare**, la mancanza di fonte è una domanda, non una licenza.
5. **Ampliare il perimetro del pacchetto.** Si toccano solo i file elencati nel pacchetto.
   Ciò che si scopre fuori perimetro si scrive nel rapporto finale e resta lì.

Ne discende:

- Non portare al PO scelte tecniche reversibili — formati, algoritmi, librerie, strutture
  dati. Si decidono, si motivano nei documenti e, se rilevanti, si dichiarano al PM.
- Non chiedere al PO di validare un'implementazione. Chiedergli se il risultato è quello
  che voleva.
- Se una sua osservazione sembra tecnica, non lo è: è un sintomo. Tradurla in causa e
  correggerla, non rimandargliela.
- Il DEV **non dichiara autonomamente completato** il proprio lavoro. Consegna, e aspetta
  il verdetto del PM.

### Vocabolario: cosa vuol dire «PM» nei documenti storici

Nei documenti scritti prima di questo modello — `docs/DECISION_LOG.md`,
`docs/input-pm/REGISTRO.md`, i piani e i collaudi — la parola **«PM» indica Daniel
Carta**, cioè quello che oggi si chiama **PO**. Quei documenti **non vanno riscritti**: si
leggono con questa chiave. Il percorso `docs/input-pm/` resta invariato per la stessa
ragione.

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

## Un pacchetto, un ramo, una PR

**Il lavoro non arriva su `main` da solo.** Ogni pacchetto di lavoro assegnato dal PM vive
su un **ramo dedicato**, e su `main` ci arriva **soltanto tramite pull request**, dopo
l'**accettazione del PM**.

- **Un pacchetto, un ramo.** Il nome del ramo lo dà il pacchetto. Nessun lavoro di un
  pacchetto su un ramo che ne ospita un altro.
- **Nessun merge diretto su `main`.** Né dal DEV né in locale: la PR è l'unico ingresso, ed
  è il PM che la accetta o la respinge.
- **Il DEV non chiude la propria PR** e non la fonde. La apre, la porta in stato
  revisionabile e si ferma.
- **Si spinge dopo ogni unità di lavoro compiuta**, non solo alla fine: una sessione può
  interrompersi senza preavviso, ed è già successo. Spingere sul proprio ramo è sempre
  lecito e sempre dovuto.
- **Prima di cominciare si guarda se esistono altri rami** con lavoro non riportato, e li
  si **elenca** nel rapporto finale. Elencarli è obbligatorio; fonderli, cancellarli o
  recuperarne i commit non lo è mai senza un pacchetto che lo chieda. Il ramo su cui una
  sessione si apre non è necessariamente l'ultimo che è stato scritto: il 10 agosto una
  sessione è partita da un punto più vecchio di due linee di lavoro, e il disallineamento
  non si vedeva da nessun documento.
- **I conflitti si risolvono, non si aggirano** aprendo un ramo nuovo. La risoluzione è
  lavoro del pacchetto in corso, e ciò che resta fuori si scrive in `PROJECT_STATE.md` con
  il nome del ramo.

> **Punto aperto per il PO.** Questa sezione sostituisce, nelle regole operative, l'obbligo
> di fondere ogni sessione direttamente su `main`. Quell'obbligo era stato registrato come
> **D-117** e **D-117 non è stata toccata**: superarla formalmente è una decisione del PO,
> non del DEV. Finché il PO non si pronuncia, `docs/DECISION_LOG.md` e questo file dicono
> due cose diverse su un punto solo, e questa nota esiste per renderlo visibile.

## Principi non negoziabili

- Non iniziare l'implementazione prima dell'approvazione del design.
- Non dimensionare né selezionare autonomamente generatori, accumuli, tubazioni o circolatori.
- Non modificare silenziosamente le scelte progettuali dell'ingegnere.
- Distinguere sempre elementi necessari, raccomandati e condizionati.
- Presentare integrazioni, assunzioni e domande prima di generare il disegno.
- Usare un modello strutturato, regole verificabili e layout deterministico.
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

## Come si scrive al PM

Il PM legge il tecnico, ma giudica il pacchetto. Al PM si scrive **sempre contro i criteri
di accettazione**: criterio per criterio, cosa è stato fatto e con quale prova.

- Rapporto finale con: ramo, SHA iniziale, SHA finale, file modificati, verifiche eseguite,
  difetti noti, link alla PR.
- Le ambiguità si riportano, non si risolvono. Una domanda al PM è sempre più economica di
  un'ipotesi diventata requisito.
- Ciò che è stato scoperto fuori perimetro si nomina e si lascia dov'è.

## Il metodo dei tre ruoli dentro il DEV (D-083 — vincolante, imposto dal PO il 5 agosto 2026)

Il DEV lavora al proprio interno come un team: **uno decide come si fa, uno o più fanno,
uno controlla.** È il metodo interno di esecuzione, e sta **sotto** l'assegnazione del PM:
non sostituisce né l'accettazione del PM né l'autorità del PO.

- **L'orchestratore** traduce il pacchetto del PM in unità di lavoro, assegna, giudica i
  rapporti di collaudo e risponde al PM. Non approva mai il proprio lavoro.
- **Gli sviluppatori** — agenti separati — eseguono. Non dichiarano mai «fatto» da soli.
- **Il collaudo** — un agente con contesto separato, che non ha visto nascere il lavoro —
  verifica criteri di accettazione, `docs/standard/QUALITA_GRAFICA.md` e la regressione completa.
  Può respingere: il lavoro torna in sviluppo. Ogni verdetto si registra nell'appendice
  del piano in corso.

Regole ferree, senza eccezioni:

1. Niente è «fatto» senza verdetto positivo del collaudo, registrato. Un verdetto positivo
   del collaudo è la condizione per **consegnare al PM**, non l'accettazione del pacchetto:
   quella è del PM.
2. **Nessuna tavola arriva al PO senza il cancello completo** — rigenerata dalla catena
   corrente il giorno stesso, controlli di correttezza, preflight e occhio terzo passati.
   Mai mostrare un artefatto vecchio come risultato attuale.
3. **Vietato inventare.** Nessun contenuto grafico senza fonte dichiarata (norma tramite
   fonte secondaria verificata, schema di produttore, o decisione esplicita del PO). Se
   la fonte manca, si apre una domanda al PO: la mancanza di fonte è una domanda, non una
   licenza.
4. **Il piano approvato si rispetta.** Una deviazione si registra nell'appendice del
   piano, con il perché, prima di eseguirla.
