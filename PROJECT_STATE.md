# PROJECT_STATE — Disegnatore MEP

> Stato vivo del progetto. `Now` contiene al massimo tre attività; `Next` è ordinato per priorità; `Done log` è anti-cronologico.

## Repository e ambienti

| Componente | Stato | Note |
|---|---|---|
| Repository | Git locale + GitHub | Remote `origin` su [danielcarta9c/DisegnatoreMEP](https://github.com/danielcarta9c/DisegnatoreMEP), **pubblico**, licenza MIT (D-038) |
| Sviluppo | Locale o cloud | Pronto per entrambi: comandi Bash, plugin dichiarato in `.claude/settings.json` |
| Interprete | Python 3.12, minimo 3.11 | Ambiente ricostruibile con `bash scripts/setup-env.sh` |
| Pacchetto | `disegnatore-mep` 0.1.0 | Installato in editable nella `.venv`; comando `disegnatore-mep` funzionante |
| Schema del progetto | `1.1.0` | I documenti `1.0.0` sono migrati al caricamento; fingerprint della fixture mista `31a6198e…` |
| Test | 190 verdi | `pytest`, `ruff` e `mypy --strict` a exit `0` su `src`, `tests` ed `examples` |
| Libreria simboli | 12 pubblicati + 8 di fixture | `assets/symbols/` e `examples/foundation/symbols/`, entrambe rigenerabili identiche |
| Release | Non disponibile | `releases/latest/` sarà popolata dopo la prima versione verificata |

## Now — in corso

- [x] ~~Prova fisica di stampa~~ — **superata il 4 agosto 2026**: il PM ha stampato l'A3 e la barra di scala misura 100 mm col righello. L'invarianza di scala e' dimostrata sulla carta e il gate grafico e' chiuso.

<details><summary>Testo originale della prova</summary>

- **Prova fisica di stampa, spetta al PM.** Stampare il foglio A3 al 100%, senza adattamento alla pagina, e misurare col righello la barra di scala: deve dare 100 mm. È l'unico passo del gate grafico non eseguibile in una sessione cloud, e con esso va raccolta l'impressione visiva sulla riconoscibilità dei dodici simboli alla loro dimensione reale. Il foglio si rigenera con `.venv/bin/python -m disegnatore_mep symbols-sheet outputs/symbols.svg --symbols assets/symbols`.

</details>

- [x] ~~Scrivere il piano di layout, instradamento e multi-tavola~~ — **scritto il 4 agosto 2026** in `docs/plans/2026-08-04-layout-routing-multitavola-plan.md`. Dodici task, non ancora eseguito.
- [x] ~~Decisioni di prodotto del piano~~ — **chiuse dal PM il 4 agosto 2026**: caso D-011 completo, divisione in tavole solo quando non entra, reti distinte per colore e tratto.
- [ ] **Approvazione del PM sul piano nel suo insieme.** Le tre decisioni sono chiuse; manca il via libera a eseguirlo.

## Next — backlog ordinato

1. Eseguire il piano di layout, instradamento e multi-tavola, una volta approvato. Nessun task è in attesa di decisioni: sono chiuse tutte.
2. Scrivere il piano di rendering, cartiglio e PDF, con distinta derivata dal modello e preflight.
3. Solo a questo punto il motore delle regole (ex P1), con `RuleApplicationModel` completato per la tracciabilità a valle (D-039), la rappresentazione dei dati mancanti e il percorso di migrazione dello schema. Dettagli in `docs/P0_REVIEW_FINDINGS.md` §3.2.
4. Allargare il contratto `DomainPack` prima che i quattro pacchetti di dominio procedano in parallelo (W3).
5. Implementare i pacchetti di dominio idronico, aeraulico, espansione diretta e gas.
6. Integrare la skill conversazionale.
7. Costruire la matrice di qualificazione e la prima release.

## Debito noto della fase grafica

Registrato per non riscoprirlo. Nessuno di questi è bloccante.

- Nessun test presidia che il corpo di un simbolo resti dentro il proprio riquadro e raggiunga le porte dichiarate. Oggi vale per tutti e venti, verificato dalle revisioni, ma un corpo modificato a mano potrebbe romperlo e continuare a caricare. Il corpo è comunque validato come XML ben formato al caricamento, quindi non può più corrompere la tavola generata.
- Nessun test protegge i due generatori dalla deriva rispetto ai file che hanno prodotto.
- `allowed_rotations_deg` è dichiarato ma non applicato: nulla ruota un simbolo, né scambia il riquadro a 90°/270°, né ruota una `PortFace` o un lato di `KeepOut` (D-049). Spetta al piano di layout.

Chiusi dalla revisione finale del ramo: la guardia di capacità ora difende anche l'asse orizzontale (D-045 su entrambi gli assi) e la verifica incrociata simbolo/catalogo è cablata sulla CLI `validate` tramite `--symbols`, opzionale.

Elenco completo nell'appendice di `docs/plans/2026-08-03-graphic-system-symbol-library-plan.md`.

## Trovato scrivendo il piano di layout

Registrato qui perché non venga perso se il piano resta fermo. Dettagli e misure nel §2 del piano.

- **Nessuno dei venti simboli sta sulla griglia.** Non un riquadro, non una porta: 3 mm sono 1,2 passi da 2,5. Un instradamento ortogonale su griglia non può raggiungere nessuna porta della libreria attuale. Il piano lo risolve ridimensionando la libreria (Task 7), il che è anche il modo naturale di chiudere D-050.
- **Il telaio del foglio non segue il cartiglio che il PM aveva fornito.** `assets/cartigli/Cartiglio_NoveC_A3.pdf` è nel repository dal primo commit (`fa7157c`, 1 agosto) e usa una squadratura a 10 mm sui quattro lati; `A3_LANDSCAPE` ne dichiara 20 a sinistra, scritti il 3 agosto citando ISO 5457 — che `SOURCE_REGISTER` elenca tuttora «da acquisire e valutare». Il piano grafico non nomina il cartiglio nemmeno una volta. È lo stesso errore che D-047 ha corretto per i simboli, ripetuto sulla carta e non intercettato dalle revisioni. Misurato dal PDF: banda del cartiglio 36 mm a tutta larghezza, intestazione 6 mm, area di disegno 350 × 235 mm. Registrato come CONV-GRAFICA-003.
- **`inline_gap_mm` è confrontato con la larghezza invece che con l'asse delle porte.** Innocuo finché tutti i simboli in linea sono quadrati; sbagliato appena uno viene ruotato di 90°.

## Domande aperte

Nessuna domanda di prodotto aperta.

Le tre del piano di layout sono state chiuse dal PM il 4 agosto 2026, tutte confermando la proposta: **caso D-011 completo** con la gerarchia dimensionale che chiude D-050 (Task 7), **divisione in tavole solo quando il contenuto non entra** (Task 6), **reti distinte da colore e tratto** perché la tavola resti leggibile anche fotocopiata (Task 11). Vanno registrate come D-055, D-056 e D-057 nei task che le applicano.

Una quarta era stata posta e ritirata: chiedeva la squadratura del foglio, che non era da decidere perché il cartiglio era già fra gli input del progetto.

## Done log — ultimo in cima

| Commit | Cosa |
|---|---|
| `f781d5c` | **Piano di layout, instradamento e multi-tavola scritto** (non eseguito): dodici task, con rotazione, tratte e instradamento prototipati e sotto test prima della stesura. Trovati tre difetti non registrati altrove: nessun simbolo sulla griglia, squadratura del cartiglio in disaccordo con `A3_LANDSCAPE`, interruzione di linea misurata sull'asse sbagliato |
| `8e2b664` | **Fase grafica integrata in `main`** con merge esplicito; convenzioni grafiche interne registrate in `SOURCE_REGISTER`; W8 e W9 di P0 marcati risolti |
| `fc97ad3`, `650f534`, `f90ede6`, `d193f6b`, `6516d77`, `0bb60ba`, `25fc9bc` | **Revisione finale del ramo grafico**: compositi che portano area di rispetto, interruzione di linea e ancoraggi (D-027); corpo SVG validato come XML; guardia di capacità sull'asse orizzontale (D-045); verifica incrociata cablata su `validate --symbols`; area di rispetto imposta sulle facce con porta; significato di `allowed_rotations_deg` (D-049, D-050) |
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
