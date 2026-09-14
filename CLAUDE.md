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

Il DEV consegna tramite PR e non esegue il merge. **Il PM è uno solo**
(`docs/governance/OPERATING_MODEL.md` §1.2.1, D-130 del 14 settembre 2026): scrive i pacchetti
e i criteri, li sottopone al PO prima che il lavoro cominci, verifica la consegna criterio per
criterio e fonde su `main` — solo tramite pull request. Ciò che resta separato è che **il PM
non è il DEV**: il DEV lavora in una sessione diversa, esegue soltanto il pacchetto attivo,
apre la PR e si ferma.
