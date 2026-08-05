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
| Test | 461 verdi | `pytest`, `ruff` e `mypy --strict` a exit `0` su `src`, `tests` ed `examples` |
| Libreria simboli | 31 pubblicati + 8 di fixture | `assets/symbols/` e `examples/foundation/symbols/`, entrambe rigenerabili identiche |
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

## Difetti segnalati dal PM sulla tavola completa — 5 agosto 2026

**Registrati, non ancora corretti.** L'elenco si è chiuso il 5 agosto («non mi viene in
mente altro») e la correzione è organizzata dal piano di rilancio (D-084): ogni difetto ha
il suo pacchetto, e la chiusura di ciascuno andrà provata nel rapporto finale, non
dichiarata.

- [ ] **Divisione in due tavole con la seconda quasi vuota** (D-072). Il criterio deve
  diventare «la tavola successiva è abbastanza piena», e prima si ottimizza quella che
  c'è. Oggi si divide appena il contenuto non entra **come è stato disposto**, che è una
  cosa diversa.
- [ ] **Mancano quasi tutte le valvole di intercettazione** (D-074). Ogni macchina ne vuole
  una **per ogni attacco**: due sulla pompa di calore, due sul circolatore, quattro sul
  volano. Oggi ne mette una per componente, e quella semplificazione era stata fatta per
  far entrare il disegno su una A3 — cioè decidendo il contenuto in base al foglio, che è
  esattamente al contrario.
- [ ] **La disposizione in fila trattata come legge** (D-073). Bollitore e volano potevano
  stare uno sopra l'altro invece che uno dopo l'altro. Impilare è una disposizione
  legittima quanto affiancare, e va scelta quando riempie meglio il foglio.
- [ ] **Le etichette sembrano tubazioni** (D-075). Oggi sigle e valori scendono in una riga
  di richiami sotto il disegno, collegati al pezzo da una linea ortogonale: stessa forma e
  stessa giacitura di una tubazione. Devono tornare a essere una scritta piccola accanto al
  proprio componente; quando non ci sta, un richiamo obliquo a 45°, che nessuna tubazione
  può essere.
- [ ] **La linea fa il giro per raggiungere un pezzo invece di spostare il pezzo** (D-078).
  Il prelievo ACS è raggiunto da una tratta che lo supera, scende e torna indietro. Oggi la
  disposizione decide per prima e in modo definitivo, e l'instradamento paga in pieghe
  qualunque cosa essa abbia deciso. Va invertito: la posizione dei componenti è una
  variabile del problema, e spostare un oggetto è gratis mentre una piega costa.
  Il secondo esempio del PM — l'ingresso dell'acqua fredda posato in alto, che scende
  tagliando tutte le linee di riscaldamento per arrivare al bollitore — mostra che la
  disposizione non si paga solo in pieghe ma anche in **attraversamenti**: posato in basso,
  quel tratto sarebbe stato dritto e non avrebbe incrociato niente.
- [ ] **Gli attraversamenti non hanno il loro simbolo** (D-079). Due linee che si incrociano
  e due linee che si collegano oggi hanno lo stesso segno: chi legge non può distinguere un
  incrocio da un raccordo. Serve lo scavallo, l'archetto che scavalca, e il pallino sul
  collegamento che la norma prescrive. Gli attraversamenti sono già calcolati e portati nella
  geometria — semplicemente nessuno li disegna.
- [ ] **I simboli non vengono da nessuna fonte** (D-081, D-082). Il PM ha riconosciuto a
  occhio la valvola di ritegno sbagliata. La causa è più larga del singolo simbolo: la
  libreria è inventata, e il rifacimento deciso il 4 agosto (D-067) non è stato eseguito. La
  fonte di lavoro è ora SRC-016, le tavole UNI 9511 pubblicate da Oppo e indicate dal PM,
  scaricabili anche in DWG; per le macchine, che la norma non copre, la pratica e gli schemi
  dei produttori.
- [ ] **Spostare è gratis, spargere no** (D-080). Vincolo che accompagna il difetto
  precedente: lo spostamento dei componenti serve l'obiettivo intero — pieghe,
  attraversamenti e lunghezza — non una sola delle tre voci.

### L'errore di metodo che li ha generati

Vale più dei difetti presi singolarmente, ed è il PM a nominarlo: **una singola tavola
di riferimento è stata generalizzata in una regola.** Dal primo schema fornito è stata
ricavata la disposizione in fila, e da lì applicata a ogni impianto come se fosse una
legge del disegno tecnico. Non lo è.

La stessa cosa era già successa con le corsie a quota fissa, ricavate dalla stessa tavola
e poi rimosse perché producevano sali-scendi. Un esempio mostra **una** soluzione
ammissibile, non l'unica: da un esempio si ricava un vincolo solo quando lo si riconosce
anche altrove, o quando il PM lo dichiara tale.

Il difetto delle valvole ha invece una causa diversa e altrettanto seria: **il contenuto
del disegno è stato deciso in base a quanto ci stava sul foglio.** Le valvole di
intercettazione sono passate da una per attacco a una per componente perché con quattro
valvole sul volano l'A3 non reggeva. È al contrario: cosa va disegnato lo decide
l'impianto, e se non ci sta si cambia disposizione o si divide.

Il difetto delle etichette ne mostra un terzo: **un problema risolto introducendo un segno
nuovo, senza chiedersi come quel segno si legge.** I testi si sovrapponevano ai simboli, e
la risposta è stata portarli sotto il disegno con una linea di collegamento — risolvendo la
sovrapposizione e creando un'ambiguità peggiore, perché quella linea è ortogonale e sottile
come una tubazione. Ogni segno aggiunto alla tavola va verificato contro i segni che ci
sono già.

Il difetto del giro attorno al prelievo ACS ne mostra un quarto, ed è il più profondo:
**l'ordine della catena è stato scambiato per un ordine di autorità.** Disporre prima e
instradare dopo è una sequenza ragionevole di calcolo; è diventata la regola che la
disposizione non si tocca più, e da lì ogni difetto di posizione si è scaricato sulle
linee. Il PM lo dice in una riga: le curve costano, spostare un oggetto è gratis. Chi paga
di meno deve cedere.

### La risposta strutturale: le regole del colpo d'occhio

I difetti hanno una cosa in comune: un disegnatore senior li vede in due secondi.
Il PM lo ha nominato come il lavoro dell'agente terzo e ha chiesto di tradurre in regole
quello che l'occhio umano fa da solo. Il risultato è `docs/QUALITA_GRAFICA.md` (D-076):
una quarantina di regole in sei famiglie, ciascuna con **come si vede a occhio** e uno stato —
garantita dal motore, misurabile ma non ancora misurata, da giudicare, oppure violata oggi.

Non erano regole da scoprire: erano già note, e i difetti segnalati sono tutti nell'elenco.
Mancava l'artefatto, e il momento in cui la tavola ci viene confrontata. Da qui discende
anche che l'agente terzo giudichi **l'immagine** e non il sorgente (D-077): nel sorgente il
richiamo delle etichette è una linea di richiamo corretta, sull'immagine è un tubo in più.

## Next — il piano di rilancio (D-084)

Il 5 agosto 2026, dopo otto difetti registrati sulla tavola completa, il PM ha ordinato di
ripartire da zero con la riverifica e con un metodo a tre ruoli — uno decide, uno o più
fanno, uno controlla (D-083). Il piano è scritto, la riverifica input per input è stata
controverificata da un collaudatore indipendente, e **si attende il via del PM**:
`docs/plans/2026-08-05-rilancio-qualita-tavola-plan.md`.

1. **WP1 — Simboli dalle fonti** (D-067, D-081, D-082): UNI 9511 via Oppo per il
   valvolame e gli accessori, pratica e produttori per le macchine. Consegna intermedia:
   foglio di riscontro al PM.
2. **WP2 — Contenuto per attacco** (D-074): pompa di calore 2, circolatore 2, volano 4.
3. **WP3 — Disposizione al servizio delle linee** (D-078, D-080): ciclo deterministico
   posizioni→linee, impilamento (D-073), criterio di riempimento per dividere (D-072).
4. **WP4 — Scrittura e segni** (D-075, D-079): etichette accanto al pezzo con richiami a
   45°, scavallo e pallino.
5. **WP5 — Preflight di qualità bloccante** (D-063 livello 1).
6. **WP6 — Occhio terzo** (D-063 livello 2, D-076, D-077): ciclo dimostrato.
7. **WP7 — Rigenerazione e consegna col timbro**: cancello completo, otto difetti chiusi
   con prova.

**Dopo il rilancio, in coda e invariati:** pacchetto di dominio idronico (P3A) con
l'allargamento del contratto `DomainPack` (W3); rendering, cartiglio, PDF e distinta
(P5); skill conversazionale (P6); matrice di qualificazione e prima release (P7).

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
