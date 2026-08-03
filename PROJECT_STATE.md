# PROJECT_STATE — Disegnatore MEP

> Stato vivo del progetto. `Now` contiene al massimo tre attività; `Next` è ordinato per priorità; `Done log` è anti-cronologico.

## Repository e ambienti

| Componente | Stato | Note |
|---|---|---|
| Repository | Git locale + GitHub | Remote `origin` su [danielcarta9c/DisegnatoreMEP](https://github.com/danielcarta9c/DisegnatoreMEP), **pubblico**, licenza MIT (D-038) |
| Sviluppo | Locale o cloud | Pronto per entrambi: comandi Bash, plugin dichiarato in `.claude/settings.json` |
| Interprete | Python 3.12, minimo 3.11 | Ambiente ricostruibile con `bash scripts/setup-env.sh` |
| Pacchetto | `disegnatore-mep` 0.1.0 | Installato in editable nella `.venv`; comando `disegnatore-mep` funzionante |
| Test | 116 verdi | `pytest`, `ruff` e `mypy --strict` a exit `0` su `src`, `tests` ed `examples` |
| Libreria simboli | 12 pubblicati + 8 di fixture | `assets/symbols/` e `examples/foundation/symbols/`, entrambe rigenerabili identiche |
| Release | Non disponibile | `releases/latest/` sarà popolata dopo la prima versione verificata |

## Now — in corso

- [ ] **Prova fisica di stampa, spetta al PM.** Stampare `outputs/symbols.svg` su A3 al 100%, senza adattamento alla pagina, e misurare col righello la barra di scala: deve dare 100 mm. È l'unico passo del gate grafico non eseguibile in una sessione cloud. Il foglio si rigenera con `.venv/bin/python -m disegnatore_mep symbols-sheet outputs/symbols.svg --symbols assets/symbols`.

## Next — backlog ordinato

1. Scrivere il piano di layout, instradamento e multi-tavola, incorporando le convenzioni di impaginazione e il rapporto di costo fra incrocio e percorso lungo (D-041) e il ruolo dell'AI limitato al piano di impaginazione (D-042). Progettare lì la vista che unisce semantica e geometria: il piano grafico la elencava come `ResolvedComponent` ma non l'ha costruita, perché non aveva consumatori.
2. Scrivere il piano di rendering, cartiglio e PDF, con distinta derivata dal modello e preflight.
3. Solo a questo punto il motore delle regole (ex P1), con `RuleApplicationModel` completato per la tracciabilità a valle (D-039), la rappresentazione dei dati mancanti e il percorso di migrazione dello schema. Dettagli in `docs/P0_REVIEW_FINDINGS.md` §3.2.
4. Allargare il contratto `DomainPack` prima che i quattro pacchetti di dominio procedano in parallelo (W3).
5. Implementare i pacchetti di dominio idronico, aeraulico, espansione diretta e gas.
6. Integrare la skill conversazionale.
7. Costruire la matrice di qualificazione e la prima release.

## Debito noto della fase grafica

Registrato per non riscoprirlo. Nessuno di questi è bloccante.

- Nessun test presidia che il corpo di un simbolo resti dentro il proprio riquadro e raggiunga le porte dichiarate. Oggi vale per tutti e venti, verificato dalle revisioni, ma un corpo modificato a mano potrebbe romperlo e continuare a caricare.
- Manca l'analogo orizzontale della guardia di capacità: un simbolo più largo dell'area utile può sbordare a destra. Nessun rischio con la libreria attuale, il simbolo più largo è 8 mm su 390.
- La verifica incrociata simbolo/catalogo non gira sulla CLI `validate`, che non passa il registro dei simboli. Il rischio reale è chiuso da un test sulle fixture; il cablaggio spetta al piano di layout.
- Nessun test protegge i due generatori dalla deriva rispetto ai file che hanno prodotto.

Elenco completo nell'appendice di `docs/plans/2026-08-03-graphic-system-symbol-library-plan.md`.

## Domande aperte

Nessuna domanda di prodotto aperta.

## Done log — ultimo in cima

| Commit | Cosa |
|---|---|
| `c1ab602` | Comando `symbols-sheet`, gate di accettazione, migrazione delle fixture ai simboli reali, `docs/GRAPHIC_STANDARD.md` |
| `59851b0` | Fonte dei simboli ricondotta alla convenzione interna del progetto (D-047) |
| `987aeec` | **Prima libreria trasversale**: dodici simboli, quattro domini, rigenerazione deterministica |
| `473ea13` | Rifiutata la libreria che non entra nel foglio, invece di disegnare fuori pagina (D-045) |
| `5e87d27` | Nominate le costanti di impaginazione del foglio (D-046) |
| `b6257ad` | **Foglio dei simboli a misura reale**: 420×297 mm, una unità utente = un millimetro |
| `da3ad29`, `cd38339`, `4abb5b8` | Compositi compilati da primitive e pubblicati come simbolo unico |
| `46d4872`, `757393e`, `1546a2c` | **Geometria spostata dal catalogo al simbolo** (D-043), con verifica incrociata al caricamento |
| `eef471e`, `d97a21c` | Manifesto del simbolo con porte sul perimetro (D-044) |
| `8e76987`, `0d64f8b` | Standard grafico in millimetri di carta |
| `2c78731` | Chiusi i difetti trovati dalla revisione avversariale di P0 |
| `78838c7` | **Gate G0 superato**: progetto misto a quattro domini validato senza codice specifico per schema |
| `dffaf37` | CLI `validate` / `export-schema` / `fingerprint` con codici di uscita `0`/`2`/`1` |
| `c9716ac` | Serializzazione canonica e fingerprint riproducibile |
| `f1b763f`, `a70b6af`, `553cf0d`, `584bf26` | Validatore topologico, contratti di dominio, catalogo, modello canonico |
| `d0d85ba` | Bootstrap del pacchetto e della toolchain |
| `0bb4ef8` | Design concettuale completato, verificato end-to-end e formalizzato |
