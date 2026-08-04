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
| Test | 416 verdi | `pytest`, `ruff` e `mypy --strict` a exit `0` su `src`, `tests` ed `examples` |
| Libreria simboli | 20 pubblicati + 8 di fixture | `assets/symbols/` e `examples/foundation/symbols/`, entrambe rigenerabili identiche |
| Release | Non disponibile | `releases/latest/` sarà popolata dopo la prima versione verificata |

## Now — in corso

- [x] ~~Prova fisica di stampa~~ — **superata il 4 agosto 2026**: il PM ha stampato l'A3 e la barra di scala misura 100 mm col righello. L'invarianza di scala e' dimostrata sulla carta e il gate grafico e' chiuso.

<details><summary>Testo originale della prova</summary>

- **Prova fisica di stampa, spetta al PM.** Stampare il foglio A3 al 100%, senza adattamento alla pagina, e misurare col righello la barra di scala: deve dare 100 mm. È l'unico passo del gate grafico non eseguibile in una sessione cloud, e con esso va raccolta l'impressione visiva sulla riconoscibilità dei dodici simboli alla loro dimensione reale. Il foglio si rigenera con `.venv/bin/python -m disegnatore_mep symbols-sheet outputs/symbols.svg --symbols assets/symbols`.

</details>

- [x] ~~Scrivere il piano di layout, instradamento e multi-tavola~~ — **scritto il 4 agosto 2026** in `docs/plans/2026-08-04-layout-routing-multitavola-plan.md`. Dodici task, non ancora eseguito.
- [x] ~~Piano di layout, instradamento e multi-tavola~~ — **eseguito il 4 agosto 2026**: dodici task, dodici commit, 383 test verdi. Il caso D-011 si disegna su una A3 e passa tutti i controlli geometrici.
- [x] ~~**La regola del PM su linee e posizioni**~~ — **implementata il 4 agosto 2026 (D-060, D-062).** «Minimizzare le curve disegnate, minimizzare gli attraversamenti tra linee e minimizzare la lunghezza delle linee, mantenendo però ordinamenti da sinistra a destra», e «vietato sovrapporre longitudinalmente: sempre separate e ben distinte». Tre voci di costo nell'instradamento, un divieto sui tratti già percorsi, un vincolo nel posizionamento. Sul caso D-011: pieghe da 31 a 25, nodi condivisi da 24 a 9, sovrapposizione longitudinale da 12,5 mm a 5 — i due imbocchi da un passo dove due ritorni entrano nello stesso attacco. Misurate da `tests/layout/test_objective.py`.
- [x] ~~**Il ritorno blu che entrava nella valvola a tre vie**~~ — **risolto (D-059)**: il verso di una tratta veniva letto dalla geometria del disegno già fatto, non dalla topologia del modello, che è orientata per costruzione.
- [ ] **Rifare il linguaggio grafico sulle fonti, non sulla convenzione inventata.** Il PM ha giudicato la prima tavola mal disegnata e ha chiesto la ricerca che il progetto non aveva mai fatto. Esito in `docs/research/2026-08-04-come-si-disegna-uno-schema-funzionale.md`: manca **UNI 9511**, mandata e ritorno devono essere linee distinte, la tavola porta i diametri, le sigle sono mnemoniche funzionali, la composizione è a corsie orizzontali e non a pile verticali, e la libreria copre meno di un ottavo dei simboli di una tavola reale.
- [ ] ~~Giudizio del PM sulla prima tavola~~ — **dato: la tavola è fatta male.** I controlli automatici dimostrano che nulla si sovrappone, non che la tavola si legga come l'avrebbe disegnata un tecnico. Si rigenera con `.venv/bin/python -m disegnatore_mep draw examples/layout/heat-pump-dhw-buffer-two-zones.json --catalog examples/layout/catalog --symbols assets/symbols --out outputs/`.

## Next — backlog ordinato

Ordine concordato col PM il 4 agosto 2026, dopo il punto fatto sullo stato reale del
progetto: **P1 prima di P5**. Il motivo è che oggi il caso di prova è scritto a mano e
ha dieci componenti — nessun vaso di espansione, nessun gruppo di riempimento, nessuna
valvola di sicurezza, nessun diametro. Finché il modello non li genera, ogni giudizio
sulla tavola giudica un impianto che non esiste, e il foglio resta mezzo vuoto perché
non c'è niente da disegnarci.

1. **Motore delle regole (P1)**, con `RuleApplicationModel` completato per la tracciabilità a valle (D-039), la rappresentazione dei dati mancanti e il percorso di migrazione dello schema. Dettagli in `docs/P0_REVIEW_FINDINGS.md` §3.2.
2. Allargare il contratto `DomainPack` prima che i quattro pacchetti di dominio procedano in parallelo (W3).
3. **Pacchetto di dominio idronico (P3A)**, che è il dominio del caso di accettazione e dà alle regole di cosa parlare. Gli altri tre a seguire.
4. **Rendering, cartiglio e PDF (P5)**, con distinta derivata dal modello e **preflight grafico** (D-063): le soglie di `tests/layout/test_objective.py` devono diventare un validatore di prodotto che gira su ogni tavola, non un test su una fixture.
5. **Skill conversazionale (P6)**, col **cold eye review** e il ciclo di revisione (D-063, D-064): agente terzo, giudica ciò che non si misura, respinge cambiando il piano di impaginazione e mai la geometria.
6. Costruire la matrice di qualificazione e la prima release (P7).

Sull'instradamento si torna solo se, con un impianto **completo**, resta qualcosa che
non va: a quel punto è un difetto vero e non un'ipotesi su un caso povero.

Tutto ciò che è stato **rimandato** — famiglie di accessori oltre l'MVP, aeraulico,
regolazione, diametri, fonti acquistabili, debito della libreria — sta in
`docs/DEFERRED.md`, non qui. Una decisione rimandata che non viene scritta è persa.

## Debito noto della fase grafica

Registrato per non riscoprirlo. Nessuno di questi è bloccante.

- Nessun test presidia che il corpo di un simbolo resti dentro il proprio riquadro e raggiunga le porte dichiarate. Oggi vale per tutti e venti, verificato dalle revisioni, ma un corpo modificato a mano potrebbe romperlo e continuare a caricare. Il corpo è comunque validato come XML ben formato al caricamento, quindi non può più corrompere la tavola generata.
- Nessun test protegge i due generatori dalla deriva rispetto ai file che hanno prodotto.
- `allowed_rotations_deg` è dichiarato ma non applicato: nulla ruota un simbolo, né scambia il riquadro a 90°/270°, né ruota una `PortFace` o un lato di `KeepOut` (D-049). Spetta al piano di layout.

Chiusi dalla revisione finale del ramo: la guardia di capacità ora difende anche l'asse orizzontale (D-045 su entrambi gli assi) e la verifica incrociata simbolo/catalogo è cablata sulla CLI `validate` tramite `--symbols`, opzionale.

Elenco completo nell'appendice di `docs/plans/2026-08-03-graphic-system-symbol-library-plan.md`.

## Il difetto principale, oggi

Il linguaggio grafico è inventato. La fase grafica ha creato `CONV-GRAFICA-001` perché le
fonti non erano state acquisite (D-047), e il motore di layout ci è stato costruito sopra
senza mai confrontarsi con una tavola reale. Regge la meccanica — griglia, scala invariante,
tratte, interruzione della linea, multi-tavola, validazione geometrica, riproducibilità — non
regge cosa viene disegnato e come è composto. Analisi e fonti in
`docs/research/2026-08-04-come-si-disegna-uno-schema-funzionale.md`.

## Debito noto del layout

- **La qualità grafica è misurata da un test, non da un validatore.** `tests/layout/test_objective.py` misura pieghe, attraversamenti, sovrapposizioni longitudinali e lunghezza — ma su **una** fixture, e solo in fase di sviluppo. Deve diventare il preflight grafico di D-063, che gira su ogni tavola e classifica gli esiti come bloccante, da approvare o avviso. È il pezzo che manca perché la skill possa verificare prima di consegnare.
- **Su una A3 un impianto piccolo lascia il foglio a metà vuoto.** Il blocco viene centrato (D-061) ma non ingrandito, perché la scala di stampa è invariante (ADR 0003). Quello che riempirebbe davvero l'altezza è contenuto che oggi non c'è: gli ausiliari che P1 deve generare, la fascia di regolazione tratteggiata (`Domain.CONTROL` è inutilizzato) e i diametri sulle tubazioni. Il formato si sceglie provando: si prende il più piccolo su cui il contenuto **rispetta le distanze minime**, e il caso D-011 non entra su una A4.
- **La corsia di mandata non è garantita sopra quella di ritorno.** Dove due tratte devono scavalcare lo stesso ostacolo, la prima prende la quota più vicina e la seconda quella sopra; chi sia la prima lo decide l'ordine del modello. Imporre la convenzione costerebbe pieghe, che D-060 mette al primo posto. La convenzione resta garantita **sui simboli** — l'attacco di mandata sta sopra quello di ritorno — e le due linee restano distinte per colore e tratto (D-057).
- **Una tratta che attraversa un confine di tavola non viene disegnata** su nessuna delle due: compaiono i rimandi accoppiati, non il tratto che li raggiunge. Per la stessa ragione, un confine che tagliasse una tratta con accessori in linea viene **rifiutato**, perché quegli accessori resterebbero senza una linea su cui posarsi. Spetta al piano di rendering, che possiede i rimandi.
- **Il cartiglio non è compilato**: la tavola esce marcata come bozza (D-025).
- **La rotazione scelta dal posizionamento è sempre 0** quando il simbolo la ammette. Gli accessori **in linea** ruotano già, seguendo la giacitura della tratta su cui stanno — è così che il circolatore si mette in verticale quando la sua tratta è verticale — ma un componente posato non viene mai orientato verso la fascia adiacente. È un grado di libertà in più per D-060, non ancora sfruttato.

## Trovato scrivendo il piano di layout, e poi risolto

Dettagli e misure nel §2 del piano; le correzioni nella sua appendice.

- ~~**Nessuno dei venti simboli sta sulla griglia.**~~ **Risolto (D-054, D-055):** venti simboli pubblicati e otto di fixture, tutti con riquadro e porte su nodi. Senza, l'instradamento non avrebbe raggiunto un solo attacco.
- **Il telaio del foglio non seguiva il cartiglio che il PM aveva fornito.** `assets/cartigli/Cartiglio_NoveC_A3.pdf` è nel repository dal primo commit (`fa7157c`, 1 agosto) e usa una squadratura a 10 mm sui quattro lati; `A3_LANDSCAPE` ne dichiara 20 a sinistra, scritti il 3 agosto citando ISO 5457 — che `SOURCE_REGISTER` elenca tuttora «da acquisire e valutare». Il piano grafico non nomina il cartiglio nemmeno una volta. È lo stesso errore che D-047 ha corretto per i simboli, ripetuto sulla carta e non intercettato dalle revisioni. Misurato dal PDF: banda del cartiglio 36 mm a tutta larghezza, intestazione 6 mm, area di disegno 350 × 235 mm. Registrato come CONV-GRAFICA-003 e risolto da D-053.
- ~~**`inline_gap_mm` è confrontato con la larghezza invece che con l'asse delle porte.**~~ **Risolto al Task 2.**

## Domande aperte

| # | Domanda | Perché serve |
|---|---|---|
| ~~P5~~ | ~~Si acquista **UNI 9511** e la libreria si rifà su quella?~~ | **Chiusa dal PM il 4 agosto 2026: non si compra.** I segni grafici della norma sono riprodotti per esteso in materiale didattico e di settore liberamente accessibile (SRC-015), verificati. La libreria si rifà su quelli, citati come fonte secondaria |
| ~~P6~~ | ~~L'A3 resta il formato ordinario?~~ | **Chiusa dal PM il 4 agosto 2026 (D-058): A3, o A4 se il disegno è proprio piccolo. Niente A0, niente strisce.** La domanda non andava posta: il formato era già deciso da D-019 |

Le tre del piano di layout sono state chiuse dal PM il 4 agosto 2026 e registrate come D-055, D-056 e D-057.

Una quarta era stata posta e ritirata: chiedeva la squadratura del foglio, che non era da decidere perché il cartiglio era già fra gli input del progetto.

## Done log — ultimo in cima

| Commit | Cosa |
|---|---|
| `da67b9d`…`c3f0a97` | **Piano di layout eseguito**: dodici task. `ResolvedComponent`, rotazione del manifesto, piano di impaginazione nel modello con migrazione dello schema (W2), telaio Nove C (D-053), tratte (W4), partizione e rimandi, libreria sulla griglia con gerarchia dimensionale (D-054, D-055), posizionamento a fasce, instradamento, accessori in linea, tag e legenda, validazione geometrica e comando `draw`. Nove difetti trovati eseguendo, elencati nell'appendice del piano |
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
