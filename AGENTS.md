# Regole operative — Disegnatore MEP

## Ordine di lettura obbligatorio

1. `CONTESTO_PROGETTO.md`
2. `PRD_DISEGNATORE_MEP.md`
3. `PROJECT_STATE.md`
4. `docs/DECISION_LOG.md`
5. specifiche e ADR pertinenti al lavoro richiesto

Prima di fare domande, verificare chat, documenti e decisioni già registrate. Chiedere soltanto ciò che resta realmente ambiguo.

## Principi non negoziabili

- Non iniziare l'implementazione prima dell'approvazione del design.
- Non dimensionare né selezionare autonomamente generatori, accumuli, tubazioni o circolatori.
- Non modificare silenziosamente le scelte progettuali dell'ingegnere.
- Distinguere sempre elementi necessari, raccomandati e condizionati.
- Presentare integrazioni, assunzioni e domande prima di generare il disegno.
- Usare un modello strutturato, regole verificabili e layout deterministico.
- Mantenere SVG come formato vettoriale intermedio e PDF come elaborato finale iniziale.
- Aggiornare `PROJECT_STATE.md` al termine di ogni attività significativa.
- Registrare nel `DECISION_LOG` le decisioni funzionali; usare gli ADR per quelle strutturali e costose da cambiare.
- Non modificare manualmente `releases/latest/`: deve essere generata da una versione verificata.

## Comunicazione con il PM

- Italiano, frasi chiare e brevi.
- Portare al PM decisioni di prodotto, priorità, rischi e compromessi.
- Decidere autonomamente i dettagli tecnici reversibili, spiegando il perché.
- Fermarsi prima di azioni distruttive, cambi di stack o ampliamenti sostanziali dello scope.
