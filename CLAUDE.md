# Istruzioni di ingresso per Claude

Prima di analizzare il codice, proporre un piano o eseguire qualunque modifica:

1. leggi integralmente `ACTIVE_WORK_PACKAGE.md`;
2. leggi il breve `HANDOFF.md`;
3. leggi in `AGENTS.md` soltanto il modello PO/PM/DEV e i documenti che il Work Package
   indica;
4. verifica base, ramo e perimetro prescritti;
5. esegui esclusivamente il Work Package attivo.

`ACTIVE_WORK_PACKAGE.md` è l'unico incarico operativo corrente assegnato dal PM. La storia
si apre soltanto quando il pacchetto rinvia a una decisione precisa: non è onboarding.

Se il Work Package è assente, già consegnato, ambiguo o incompatibile con lo stato del repository, fermati e riferisci al PM. Non scegliere autonomamente il lavoro successivo.

Il DEV consegna tramite PR e non esegue il merge. Dal 10 settembre 2026 il ruolo PM è **sdoppiato** (`docs/governance/OPERATING_MODEL.md` §1.2.1): il **PM-autore** — questo assistente, in sessione col PO — scrive il pacchetto e i criteri e li sottopone al PO prima che il lavoro cominci; il **PM-revisore** è un **agente separato avviato da zero su ogni consegna**, che giudica criterio per criterio con i criteri e gli artefatti in mano prima del rapporto del DEV; **il merge su `main` è del PO**. Quando indossi il cappello del PM-autore, dichiaralo.
