# Disegnatore MEP

Progetto per una skill capace di trasformare la configurazione di un impianto termotecnico già definito e dimensionato dall'ingegnere in uno schema unifilare tecnico-esecutivo professionale.

La skill analizzerà la configurazione, proporrà gli accessori necessari o raccomandati, raccoglierà l'approvazione dell'ingegnere e produrrà elaborati vettoriali SVG/PDF mediante regole tecniche e layout deterministici.

**Stato:** fondazione canonica e sistema grafico completati. Il motore generale valida un impianto che mescola idronica, aeraulica, refrigerante e gas senza codice specifico per quello schema, e produce un foglio A3 stampabile dei simboli a misura reale. Non disegna ancora impianti: layout, instradamento e cartiglio arrivano nelle fasi successive.

## Orientamento rapido

1. Leggere `CONTESTO_PROGETTO.md`.
2. Leggere `PRD_DISEGNATORE_MEP.md`.
3. Consultare `PROJECT_STATE.md` per lo stato corrente.
4. Consultare `docs/DECISION_LOG.md` per le decisioni approvate.
5. Consultare `docs/ROADMAP.md` per le fasi previste.
6. Leggere `docs/specs/2026-08-01-disegnatore-mep-design.md` per il design consolidato.
7. Leggere `docs/ARCHITECTURE.md` per la struttura del codice consegnato e `docs/GRAPHIC_STANDARD.md` per lo standard grafico.
8. Leggere `docs/P0_REVIEW_FINDINGS.md` prima di pianificare P1 o P2.
9. Leggere `docs/plans/2026-08-01-master-implementation-roadmap.md` e, del piano P0, almeno l'appendice finale sulle deviazioni.

## Preparazione dell'ambiente

Dalla radice del progetto, su Linux, macOS o Git Bash su Windows:

```bash
bash scripts/setup-env.sh
```

Crea la `.venv`, installa il pacchetto con le versioni pinnate e verifica test, lint e type check. È il primo comando da eseguire in una sessione cloud, che riparte sempre da un clone pulito.

## Uso del nucleo

```bash
.venv/bin/python -m disegnatore_mep validate examples/foundation/valid-mixed-project.json --catalog examples/foundation/catalog
```

Codici di uscita: `0` progetto valido, `2` errori di validazione, `1` errori di caricamento.

## Foglio dei simboli

```bash
.venv/bin/python -m disegnatore_mep symbols-sheet outputs/symbols.svg --symbols assets/symbols
```

Produce un A3 orizzontale a misura reale. Stampato al 100%, senza adattamento alla pagina, la
barra di scala deve misurare 100 mm col righello: è la prova che la scala è invariante.

Su Windows in locale l'interprete è `.venv/Scripts/python.exe` anziché `.venv/bin/python`.

## Cartelle principali

- `src/disegnatore_mep/`: il nucleo deterministico.
- `tests/`: suite di verifica, inclusi i test di accettazione del gate G0.
- `examples/foundation/`: catalogo e progetti di riferimento multi-dominio.
- `schemas/`: schema JSON versionato del modello di progetto.
- `assets/symbols/`: la libreria dei simboli pubblicati.
- `assets/`: materiali grafici e cartigli originali.
- `docs/`: roadmap, decisioni, ricerca, specifiche e ADR.
- `releases/latest/`: ultima versione approvata e installabile.
- `releases/archive/`: pacchetti storici numerati.

Il progetto è pubblicato su GitHub in [danielcarta9c/DisegnatoreMEP](https://github.com/danielcarta9c/DisegnatoreMEP), repository pubblico con licenza MIT.
