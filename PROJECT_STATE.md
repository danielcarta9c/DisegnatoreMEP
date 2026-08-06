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

Il progetto costruisce la skill **un pezzo alla volta**, sulla logica del grafo (D-099).
Piano corrente: `docs/plans/2026-08-06-piano-costruzione-skill.md`. Il metodo dei tre ruoli
(D-083) è vincolante: nessun pezzo è «fatto» senza il verdetto di un collaudo indipendente,
registrato nell'appendice del piano.

- [x] **G1 — il grafo e le sue sigle** — costruito. Nodi, archi, incroci, sigle assegnate
      camminando dalle sorgenti dichiarate, e la passeggiata che segue l'acqua e dice dove
      il circuito si richiude. Le famiglie delle sigle sono **dato**, non codice.
      Artefatto per il PM: `docs/prodotto/GRAFO_IMPIANTO.md`.
- [x] **G2 — il vocabolario delle proprietà** — approvato il 6 agosto, respinto al primo
      giro e corretto. Artefatto: `docs/prodotto/PROPRIETA_COMPONENTI.md`.
- [x] **G3 — le regole degli accessori** — diciannove regole diventano quattordici, le sei
      dell'intercettazione una sola. Respinto dal collaudo su due difetti — lo scarico del
      bollitore sul circuito sbagliato, e il motore che taceva quando il catalogo non aveva
      il pezzo — corretto su entrambi. Artefatto: `docs/prodotto/REGOLE_ACCESSORI.md`.
- [x] **Riconciliazione**: due implementazioni parallele delle sigle e due documenti del
      grafo ridotti a uno solo, senza che nessuna sigla cambiasse.

**Il prossimo lavoro**, già diagnosticato e dimensionato: chiudere il difetto per cui lo
stesso impianto, con le tubazioni elencate in ordine diverso, produce tre impianti diversi.
La radice è il presupposto «un attacco, una tubazione», che il catalogo smentisce. Dettagli
in `HANDOFF.md` §5.

## I difetti segnalati dal PM — dove sono finiti

Le due tornate di difetti del 5 agosto, e i quattordici rilievi della prima passata
dell'occhio terzo, sono la ragione per cui il progetto ha smesso di correggere una tavola e
ha cominciato a costruire la skill pezzo per pezzo. **Il loro elenco integrale e il loro
stato vivono ora nel piano** (`docs/plans/2026-08-06-piano-costruzione-skill.md`), dove
ciascuno è assegnato al pezzo che lo chiude, e nel verdetto dell'occhio terzo
(`docs/standard/COLD_EYE_REVIEW.md`). La storia — chi li ha segnalati, con che parole, e
l'errore di metodo che li aveva generati — è in `docs/archivio/`.

Tenerli anche qui significherebbe due elenchi che divergono. Ne resta uno.

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
