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

- [x] ~~Scrivere il piano di layout, instradamento e multi-tavola~~ — **scritto il 4 agosto 2026** in `docs/archivio/2026-08-04-layout-routing-multitavola-plan.md`. Dodici task, non ancora eseguito.
- [x] ~~Piano di layout, instradamento e multi-tavola~~ — **eseguito il 4 agosto 2026**: dodici task, dodici commit, 383 test verdi. Il caso D-011 si disegna su una A3 e passa tutti i controlli geometrici.
- [x] ~~**La regola del PM su linee e posizioni**~~ — **implementata il 4 agosto 2026 (D-060, D-062).** «Minimizzare le curve disegnate, minimizzare gli attraversamenti tra linee e minimizzare la lunghezza delle linee, mantenendo però ordinamenti da sinistra a destra», e «vietato sovrapporre longitudinalmente: sempre separate e ben distinte». Tre voci di costo nell'instradamento, un divieto sui tratti già percorsi, un vincolo nel posizionamento. Sul caso D-011: pieghe da 31 a 25, nodi condivisi da 24 a 9, sovrapposizione longitudinale da 12,5 mm a 5 — i due imbocchi da un passo dove due ritorni entrano nello stesso attacco. Misurate da `tests/layout/test_objective.py`.
- [x] ~~**Il ritorno blu che entrava nella valvola a tre vie**~~ — **risolto (D-059)**: il verso di una tratta veniva letto dalla geometria del disegno già fatto, non dalla topologia del modello, che è orientata per costruzione.
- [ ] **Rifare il linguaggio grafico sulle fonti, non sulla convenzione inventata.** Il PM ha giudicato la prima tavola mal disegnata e ha chiesto la ricerca che il progetto non aveva mai fatto. Esito in `docs/fonti/2026-08-04-come-si-disegna-uno-schema-funzionale.md`: manca **UNI 9511**, mandata e ritorno devono essere linee distinte, la tavola porta i diametri, le sigle sono mnemoniche funzionali, la composizione è a corsie orizzontali e non a pile verticali, e la libreria copre meno di un ottavo dei simboli di una tavola reale.
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
quello che l'occhio umano fa da solo. Il risultato è `docs/standard/QUALITA_GRAFICA.md` (D-076):
una quarantina di regole in sei famiglie, ciascuna con **come si vede a occhio** e uno stato —
garantita dal motore, misurabile ma non ancora misurata, da giudicare, oppure violata oggi.

Non erano regole da scoprire: erano già note, e i difetti segnalati sono tutti nell'elenco.
Mancava l'artefatto, e il momento in cui la tavola ci viene confrontata. Da qui discende
anche che l'agente terzo giudichi **l'immagine** e non il sorgente (D-077): nel sorgente il
richiamo delle etichette è una linea di richiamo corretta, sull'immagine è un tubo in più.

## Difetti della seconda tornata — 5 agosto 2026, sera

Segnalati dal PM sulle immagini della tavola rigenerata, **piu** i rilievi dell'occhio
terzo filtrati contro il perimetro (D-087). Non ancora corretti.

> **Questi sono esempi, non l'elenco** (D-089). Il PM non sta approvando il resto. Per ogni
> riga qui sotto vanno cercati **tutti i casi simili** su tutta la tavola e chiusi insieme:
> correggere solo dove lui ha cerchiato non chiude il difetto.

- [ ] **Le valvole del volano stanno tutte da un lato.** Tre attacchi su quattro non ne
  hanno nessuna, e le due che ci sono, affiancate sulla stessa uscita, non si capisce se
  siano del volano o del circolatore. D-074 non e' soddisfatta: la prova contava un totale
  invece di guardare attacco per attacco (D-088).
- [ ] **Il circolatore deve avere le proprie due**, riconoscibili come sue.
- [ ] **Curvette senza senso**: dove basta un angolo, l'instradamento fa una scaletta di
  due pieghe. Anche le curve costano (D-060) e queste non le paga nessuno.
- [ ] **Incrocio evitabile sul collettore**: invertendo le due uscite l'incrocio sparisce.
  L'ordine delle uscite di un collettore e' una variabile libera che nessuno usa.
- [ ] **Ci sono ancora simboli non autorizzati** (segnalato dal PM, da identificare uno per
  uno confrontando ogni simbolo usato con la propria fonte dichiarata).
- [ ] **Lo scavallo taglia in due la linea scavalcata** invece di lasciarla intera: un
  incrocio fra mandata e ritorno si legge come un bypass.
- [ ] **La miscelatrice sanitaria non ha l'alimentazione fredda.**
- [ ] **Il gruppo di riempimento e' in serie sul ritorno** invece che in derivazione.
- [ ] **Il serpentino del bollitore non tocca i bocchelli**; il volano e' un rettangolo
  vuoto che non mostra i quattro attacchi.
- [ ] **Cornice aperta in basso** e **testi a 1,19 mm** contro i 2,5 mm minimi di norma.

**Fuori perimetro per D-087**, e registrati come tali: potenze, temperature di progetto,
prevalenze, tarature, volumi e diametri non forniti dal progettista; tabella apparecchiature
con marca e modello; logica di regolazione. Non li inventa la skill.

## Next — il piano di costruzione, sulla logica del grafo

Il 6 agosto 2026 il PM ha corretto due cose insieme: **il contenuto si verifica su un grafo
scritto, non su un disegno** (D-096), e **il grafo si legge come una rete stradale, con una
sigla per nodo e la codifica che parte dalle sorgenti** — generatori di calore e acquedotto
(D-097, D-098). Da lì ha riformulato l'intera catena della skill, e la sua formulazione è
diventata quella ufficiale (D-099): **lo stesso grafo attraversa tutto**, nasce abbozzato
dall'interpretazione, si arricchisce di nodi con le regole e l'assemblatore, e la tavola ne
è la rappresentazione. I due cancelli restano: l'ingegnere approva prima che si disegni,
l'occhio terzo giudica prima che si consegni.

Il piano è stato rifatto su questa logica e **si riparte dal primo pezzo**:
`docs/plans/2026-08-06-piano-costruzione-skill.md`.

1. **G1 — Il grafo e le sue sigle** ← si riparte da qui. Nodi, archi, incroci, codifica
   camminando dalle sorgenti, e la lettura scritta che il PM approva. Chiude anche il
   rilievo del collaudo per cui lo stesso impianto, con le connessioni in ordine diverso,
   dava un impianto diverso.
2. **G2 — Il vocabolario delle proprietà** — approvato il 6 agosto, resta com'è.
3. **G3 — Le regole degli accessori** — respinto dal collaudo, in correzione.
4. **G4 — L'assemblatore** — dove va ciascun pezzo lungo la fila, risolvendo vincoli
   dichiarati e non numeri di priorità.
5. **G5 — La libreria dei simboli** — in linea contro su stacco, e il rubinetto bloccabile
   distinto da quello comune.
6. **G6 — Il cartiglio.**
7. **G7 — La composizione** — oggi il foglio è pieno al 39 % e l'impianto completo non ci
   entra più.
8. **G8 — I validatori e il cancello dell'occhio terzo.**

## Done log — ultimo in cima

| Commit | Cosa |
|---|---|
| `da67b9d`…`c3f0a97` | **Piano di layout eseguito**: dodici task. `ResolvedComponent`, rotazione del manifesto, piano di impaginazione nel modello con migrazione dello schema (W2), telaio Nove C (D-053), tratte (W4), partizione e rimandi, libreria sulla griglia con gerarchia dimensionale (D-054, D-055), posizionamento a fasce, instradamento, accessori in linea, tag e legenda, validazione geometrica e comando `draw`. Nove difetti trovati eseguendo, elencati nell'appendice del piano |
| `f781d5c` | **Piano di layout, instradamento e multi-tavola scritto** (non eseguito): dodici task, con rotazione, tratte e instradamento prototipati e sotto test prima della stesura. Trovati tre difetti non registrati altrove: nessun simbolo sulla griglia, squadratura del cartiglio in disaccordo con `A3_LANDSCAPE`, interruzione di linea misurata sull'asse sbagliato |
| `8e2b664` | **Fase grafica integrata in `main`** con merge esplicito; convenzioni grafiche interne registrate in `SOURCE_REGISTER`; W8 e W9 di P0 marcati risolti |
| `fc97ad3`, `650f534`, `f90ede6`, `d193f6b`, `6516d77`, `0bb60ba`, `25fc9bc` | **Revisione finale del ramo grafico**: compositi che portano area di rispetto, interruzione di linea e ancoraggi (D-027); corpo SVG validato come XML; guardia di capacità sull'asse orizzontale (D-045); verifica incrociata cablata su `validate --symbols`; area di rispetto imposta sulle facce con porta; significato di `allowed_rotations_deg` (D-049, D-050) |
| `c1ab602` | Comando `symbols-sheet`, gate di accettazione, migrazione delle fixture ai simboli reali, `docs/standard/GRAPHIC_STANDARD.md` |
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
