# PROJECT_STATE — Disegnatore MEP

> Stato vivo del progetto. `Now` contiene al massimo tre attività; `Next` è ordinato per priorità; `Done log` è anti-cronologico.

## Repository e ambienti

| Componente | Stato | Note |
|---|---|---|
| Repository | Git locale + GitHub | Remote `origin` su [danielcarta9c/DisegnatoreMEP](https://github.com/danielcarta9c/DisegnatoreMEP), **pubblico**, licenza MIT (D-038) |
| Sviluppo | Locale o cloud | Pronto per entrambi: comandi Bash, plugin dichiarato in `.claude/settings.json` |
| Interprete | Python 3.12, minimo 3.11 | Ambiente ricostruibile con `bash scripts/setup-env.sh` |
| Pacchetto | `disegnatore-mep` 0.1.0 | Installato in editable nella `.venv`; comando `disegnatore-mep` funzionante |
| Test | 59 verdi | `pytest`, `ruff` e `mypy --strict` tutti a exit `0` |
| Release | Non disponibile | `releases/latest/` sarà popolata dopo la prima versione verificata |

## Now — in corso

- [ ] Eseguire `docs/plans/2026-08-03-graphic-system-symbol-library-plan.md` con `superpowers:subagent-driven-development`, un agente per task e due revisioni indipendenti fra un task e l'altro. Metodo scelto dal PM il 3 agosto 2026.

## Next — backlog ordinato

1. Scrivere il piano di layout, instradamento e multi-tavola, incorporando le convenzioni di impaginazione e il rapporto di costo fra incrocio e percorso lungo (D-041) e il ruolo dell'AI limitato al piano di impaginazione (D-042).
2. Scrivere il piano di rendering, cartiglio e PDF, con distinta derivata dal modello e preflight.
3. Solo a questo punto il motore delle regole (ex P1), con `RuleApplicationModel` completato per la tracciabilità a valle (D-039), la rappresentazione dei dati mancanti e il percorso di migrazione dello schema. Dettagli in `docs/P0_REVIEW_FINDINGS.md` §3.2.
4. Allargare il contratto `DomainPack` prima che i quattro pacchetti di dominio procedano in parallelo (W3).
5. Implementare i pacchetti di dominio idronico, aeraulico, espansione diretta e gas.
6. Integrare la skill conversazionale.
7. Costruire la matrice di qualificazione e la prima release.

## Domande aperte

Nessuna domanda di prodotto aperta. Le due precedenti sono state chiuse il 3 agosto 2026: la prima ritirata perché nasceva da un fraintendimento del flusso (D-036), la seconda ricondotta a decisione tecnica dell'agente (D-037). Il flusso di lavoro corretto è fissato in `docs/P0_REVIEW_FINDINGS.md` §3.1.

## Done log — ultimo in cima

| Commit | Cosa |
|---|---|
| `2c78731` | Chiusi i difetti trovati dalla revisione avversariale: falso PASS su auto-anello, integrità della forma canonica, sotto-segnalazione, duplicato mal nominato |
| `958e7eb` | Gate G0 reso indipendente dalla directory di lancio |
| `78838c7` | **Gate G0 superato**: progetto misto a quattro domini validato senza codice specifico per schema |
| `dffaf37` | CLI `validate` / `export-schema` / `fingerprint` con codici di uscita `0`/`2`/`1` |
| `c9716ac` | Serializzazione canonica e fingerprint riproducibile |
| `6a413f0` | Diagnostiche del validatore rese distinte e azionabili |
| `f1b763f` | Validatore topologico multi-dominio |
| `a70b6af` | Contratti di compatibilità dei domini |
| `553cf0d` | Catalogo componenti versionato |
| `584bf26` | Modello canonico di progetto |
| `d0d85ba` | Bootstrap del pacchetto e della toolchain |
| `290c8de` | Handoff di sessione e cancello di lettura creati |
| `abfa683` | Milestone della pianificazione di implementazione registrata |
| `66d5406` | Roadmap master e piano eseguibile P0 completati |
| `7cf58e1` | Specifica approvata e planimetrie/schemi elettrici registrati nella visione futura |
| `0bb4ef8` | Design concettuale completato, verificato end-to-end e formalizzato |
| `fa7157c` | Bootstrap della struttura di project management e avvio del repository Git locale |
