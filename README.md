# Disegnatore MEP

Progetto per una skill capace di trasformare la configurazione di un impianto termotecnico già definito e dimensionato dall'ingegnere in uno schema unifilare tecnico-esecutivo professionale.

La skill analizzerà la configurazione, proporrà gli accessori necessari o raccomandati, raccoglierà l'approvazione dell'ingegnere e produrrà elaborati vettoriali SVG/PDF mediante regole tecniche e layout deterministici.

**Stato:** fase P0 completata. La fondazione canonica esiste, è testata e supera il gate G0: un impianto che mescola idronica, aeraulica, refrigerante e gas viene validato dal motore generale senza codice specifico per quello schema. Non esiste ancora alcun disegno: il rendering arriva nelle fasi successive.

## Orientamento rapido

1. Leggere `CONTESTO_PROGETTO.md`.
2. Leggere `PRD_DISEGNATORE_MEP.md`.
3. Consultare `PROJECT_STATE.md` per lo stato corrente.
4. Consultare `docs/DECISION_LOG.md` per le decisioni approvate.
5. Consultare `docs/ROADMAP.md` per le fasi previste.
6. Leggere `docs/specs/2026-08-01-disegnatore-mep-design.md` per il design consolidato.
7. Leggere `docs/ARCHITECTURE.md` per la struttura del codice consegnato.
8. Leggere `docs/P0_REVIEW_FINDINGS.md` prima di pianificare P1 o P2.
9. Leggere `docs/plans/2026-08-01-master-implementation-roadmap.md` e, del piano P0, almeno l'appendice finale sulle deviazioni.

## Uso del nucleo

Dalla radice del progetto, con la `.venv` già creata:

```powershell
& .\.venv\Scripts\python.exe -m disegnatore_mep validate examples/foundation/valid-mixed-project.json --catalog examples/foundation/catalog
```

Codici di uscita: `0` progetto valido, `2` errori di validazione, `1` errori di caricamento.

## Cartelle principali

- `src/disegnatore_mep/`: il nucleo deterministico.
- `tests/`: suite di verifica, inclusi i test di accettazione del gate G0.
- `examples/foundation/`: catalogo e progetti di riferimento multi-dominio.
- `schemas/`: schema JSON versionato del modello di progetto.
- `assets/`: materiali grafici e cartigli originali.
- `docs/`: roadmap, decisioni, ricerca, specifiche e ADR.
- `releases/latest/`: ultima versione approvata e installabile.
- `releases/archive/`: pacchetti storici numerati.

Il progetto è pubblicato su GitHub in [danielcarta9c/DisegnatoreMEP](https://github.com/danielcarta9c/DisegnatoreMEP), repository pubblico con licenza MIT.
