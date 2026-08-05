# Regole operative — Disegnatore MEP

## Ordine di lettura obbligatorio

0. Se esiste `HANDOFF.md`, aprirlo per primo e applicare integralmente il suo cancello di lettura e le sentinel checks.
1. `CONTESTO_PROGETTO.md`
2. `PRD_DISEGNATORE_MEP.md`
3. `PROJECT_STATE.md`
4. `docs/DECISION_LOG.md`
5. `docs/specs/2026-08-01-disegnatore-mep-design.md`
6. `docs/QUALITA_GRAFICA.md` — le regole del colpo d'occhio, per chiunque tocchi il disegno
7. piano di implementazione pertinente in `docs/plans/`
8. specifiche e ADR pertinenti al lavoro richiesto

Prima di fare domande, verificare chat, documenti e decisioni già registrate. Chiedere soltanto ciò che resta realmente ambiguo.
`HANDOFF.md` è un cancello di lettura, non sostituisce i documenti canonici e non autorizza a saltarli.

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
- Non consegnare una tavola senza averla confrontata, riga per riga, con `docs/QUALITA_GRAFICA.md`: sapere come si disegna non sostituisce il controllo (D-076).
- Mantenere SVG come formato vettoriale intermedio e PDF come elaborato finale iniziale.
- Aggiornare `PROJECT_STATE.md` al termine di ogni attività significativa.
- Registrare nel `DECISION_LOG` le decisioni funzionali; usare gli ADR per quelle strutturali e costose da cambiare.
- Non modificare manualmente `releases/latest/`: deve essere generata da una versione verificata.

## I due ruoli

**Questa è la regola che governa ogni scambio. Non va fatta ripetere al PM.**

- **Il PM è il committente**, cioè il capo progetto dal lato di chi userà il prodotto.
  Valuta se stiamo costruendo la cosa giusta. Le sue correzioni non sono mai tecniche: se
  dice «questa tavola è fatta male» sta dicendo *cosa* non va nel prodotto, e tocca a noi
  trovare *perché* e *come*.
- **L'agente è il PM senior del team di sviluppo.** Decide come si fa, sceglie gli
  strumenti, trova i difetti, li corregge e ne risponde. Porta al committente solo ciò che
  è suo: cosa deve fare il prodotto, priorità, costi, compromessi.

Ne discende:

- Non portare al PM scelte tecniche reversibili — formati, algoritmi, librerie, strutture
  dati. Si decidono e si motivano nei documenti.
- Non chiedergli di validare un'implementazione. Chiedergli se il risultato è quello che
  voleva.
- Se una sua osservazione sembra tecnica, non lo è: è un sintomo. Tradurla in causa e
  correggerla, non rimandargliela.

## Come si scrive al PM

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

## Il metodo dei tre ruoli (D-083 — vincolante, imposto dal PM il 5 agosto 2026)

Lo sviluppo lavora come un team: **uno decide, uno o più fanno, uno controlla.**

- **L'orchestratore** scrive ogni pacchetto di lavoro con criteri di accettazione
  **prima** che il lavoro cominci, assegna, giudica i rapporti di collaudo e risponde al
  PM. Non approva mai il proprio lavoro.
- **Gli sviluppatori** — agenti separati — eseguono. Non dichiarano mai «fatto» da soli.
- **Il collaudo** — un agente con contesto separato, che non ha visto nascere il lavoro —
  verifica criteri di accettazione, `docs/QUALITA_GRAFICA.md` e la regressione completa.
  Può respingere: il lavoro torna in sviluppo. Ogni verdetto si registra nell'appendice
  del piano in corso.

Regole ferree, senza eccezioni:

1. Niente è «fatto» senza verdetto positivo del collaudo, registrato.
2. **Nessuna tavola arriva al PM senza il cancello completo** — rigenerata dalla catena
   corrente il giorno stesso, controlli di correttezza, preflight e occhio terzo passati.
   Mai mostrare un artefatto vecchio come risultato attuale.
3. **Vietato inventare.** Nessun contenuto grafico senza fonte dichiarata (norma tramite
   fonte secondaria verificata, schema di produttore, o decisione esplicita del PM). Se
   la fonte manca, si apre una domanda al PM: la mancanza di fonte è una domanda, non una
   licenza.
4. **Il piano approvato si rispetta.** Una deviazione si registra nell'appendice del
   piano, con il perché, prima di eseguirla.
