# Regole operative — Disegnatore MEP

## Ordine di lettura obbligatorio

0. Se esiste `HANDOFF.md`, aprirlo per primo e applicare integralmente il suo cancello di lettura e le sentinel checks.
1. `CONTESTO_PROGETTO.md`
2. `PRD_DISEGNATORE_MEP.md`
3. `PROJECT_STATE.md`
4. `docs/DECISION_LOG.md`
5. `docs/specs/2026-08-01-disegnatore-mep-design.md`
6. piano di implementazione pertinente in `docs/plans/`
7. specifiche e ADR pertinenti al lavoro richiesto

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
- Mantenere SVG come formato vettoriale intermedio e PDF come elaborato finale iniziale.
- Aggiornare `PROJECT_STATE.md` al termine di ogni attività significativa.
- Registrare nel `DECISION_LOG` le decisioni funzionali; usare gli ADR per quelle strutturali e costose da cambiare.
- Non modificare manualmente `releases/latest/`: deve essere generata da una versione verificata.

## Comunicazione con il PM

- Italiano, frasi chiare e brevi.
- Portare al PM decisioni di prodotto, priorità, rischi e compromessi.
- Non chiedere al PM di scegliere formati dati, algoritmi, dipendenze o altri dettagli informatici reversibili.
- Decidere autonomamente i dettagli tecnici reversibili, spiegando il perché nei documenti di progetto.
- Fermarsi prima di azioni distruttive, cambi di stack o ampliamenti sostanziali dello scope.
