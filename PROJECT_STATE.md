# PROJECT STATE — Disegnatore MEP

**Aggiornato:** 2026-09-11 (PM-autore, DRAW-006-R1 e DRAW-007 fusi in `main` dal PO)
**Fonte operativa:** `ACTIVE_WORK_PACKAGE.md`
**Release corrente:** 0.3 — generalizzazione controllata, impianto 2

## Stato verificato

| Area | Stato |
|---|---|
| Modello dati e grafo | operativi; il grafo resta la fonte unica |
| Completamento e assemblaggio | operativi sulla tavola 1; tutti e cinque gli impianti arrivano alla posa; aperta la semantica dei compositi e delle multivia |
| Posa e routing | `DRAW-004` fuso; costo-peso, assi, dorsali e T ortogonali operativi |
| Simboli | 39 manifesti: i 7 critici della tavola 1 sono verificati in DRAW-005; l'audit PM completo resta aperto prima della 0.3 |
| Etichette | fase separata dalla geometria; sigle principali sempre, indirizzi come velo esplicito (`--verifica`) |
| Packaging skill/chat | non ancora installabile né collaudato in una chat pulita |
| Release | versione Python `0.1.0`; `releases/latest/` ancora vuoto |

## Ultima baseline — DRAW-004

- PR #14, merge `c46f0db`;
- tavola 1: 6 curve, 1 incrocio, 577,5 mm di tubo;
- backtracking 0; tratte oltre tre pieghe 0;
- linea continua di terra assente;
- test dichiarati dal DEV: 1106 verdi, 22 sospesi, 13 xfail;
- controllo PM: 26 test mirati verdi, 8 sospesi; `ruff` e `mypy --strict` puliti.

Gli indicatori di DRAW-004 misurano il routing sul grafo ricevuto. Non certificano la
correttezza impiantistica del grafo, che il PO ha corretto con gli input I-030… I-040.

## Ultima baseline — DRAW-005

- PR #18, merge `006258c`; revisione PM conclusa il 2026-09-08;
- grafo dell'impianto 1: 39 pezzi (erano 45), 16 organi di chiusura (erano 21), nessuno
  fra filtro e PDC, nessuno consecutivo; un solo riempimento, sul ritorno tecnico;
- tavola 1: 4 curve, 1 incrocio, 525,0 mm — grafo diverso da DRAW-004, quindi non un
  miglioramento dichiarato: −37,5 mm vengono dal contenuto, −15,0 dal layout;
  backtracking 0; tratte oltre tre pieghe 0; 16 valvole su 16 a 2,5÷5 mm; la valvola
  comune di mandata a 5 mm dal raccordo della sicurezza;
- prove generali nuove: 35 (grafo), 39 (contratti grafici), 10 (posa e modalità);
  suite DEV 1190 verdi, 22 sospese, 14 xfail; controllo PM: 128 test mirati verdi,
  4 sospesi e 2 xfail dichiarati; `ruff` e `mypy --strict` puliti;
  determinismo verificato su due generazioni;
- rapporto e artefatti in `docs/collaudi/DRAW-005/`; righe I-030… I-040 restano aperte
  finché il PO non le chiude.

## Lavoro corrente

`DRAW-006-R1` e `DRAW-007` sono stati **fusi in `main` dal PO** l'11 settembre 2026, con i
rilievi aperti dichiarati qui sotto. Non erano approvati criterio per criterio: il PO ha
scelto di consolidare il lavoro e di ripartire da un'architettura nuova, che è
`DRAW-008`.

**DRAW-006-R1** ha chiuso i quattro difetti semantici — ordine indipendente dagli
identificativi, assi per stato idraulico, gruppo EN 1487 unico sull'adduzione ACS,
riempimento come ponte fra due reti — e ha peggiorato la geometria.

**DRAW-007** ha dato alla tavola una **gerarchia**: autostrada, distribuzione, servizio,
calcolata sul grafo in `src/disegnatore_mep/layout/hierarchy.py` e letta dal costo di posa
e dall'obiettivo di allineamento. Ha inoltre tolto due cose che non dovevano esserci:

- **il pavimento invisibile.** La linea di terra non si disegna più da DRAW-004, ma la
  regola era rimasta: niente poteva scendere sotto l'83% dell'altezza del foglio. Il PO ha
  disposto che quel vincolo non esiste — «è uno schema quello che disegniamo» — e toglierlo
  ha portato la tavola 1 da 10 pieghe a 6;
- **il multivia contato come macchina.** La mandata dalla pompa di calore al puffer non
  risultava nemmeno autostrada, perché in mezzo c'è una deviatrice. Il tronco ci passa
  attraverso, stato per stato.

### Dove siamo davvero, sulla testa di `main`

| | Stato |
|---|---|
| **Tavola 1** | esce, ed è la migliore mai prodotta: rete ordinaria 6 pieghe / 3 incroci / 550,0 mm; **zero pieghe** su tutte e otto le tratte di autostrada; accumulo e PDC-master con **quattro porte sullo stesso asse**; D-120 15 su 15 |
| **Tavola 2** | **non esce.** Il preflight trova un rilievo bloccante — una tratta supera di 2,5 mm la propria porta e ci torna indietro — e una tavola con un bloccante non si scrive (D-063) |
| **Suite** | **nove prove di geometria rosse**, elencate nel pacchetto DRAW-008. Nessuna ammorbidita, nessuna convertita in `skip` o `xfail` |
| **`ruff`, `mypy --strict`** | puliti |

Il PO ha visto la tavola 2 e l'ha dichiarata non revisionabile. Aveva ragione, e la causa
non era una taratura.

## Rischi aperti

1. **Prodotto non ancora eseguito nel suo ambiente finale.** Dopo il collaudo controllato
   dell'impianto 2 e prima di estendere il ciclo agli impianti 3–5 serve una prova
   verticale: nuova chat, input naturale, approvazione del grafo, generazione
   deterministica e restituzione del PDF.
2. **Libreria simboli non interamente certificata.** Prima di dichiarare completa la
   generalizzazione 0.3 il PM deve completare la matrice fonti/forma/porte/ingombri; il
   DEV implementa solo la matrice approvata.
3. **Costo computazionale.** La tavola 1 richiede circa 70 secondi e oltre 2.000 routing
   di prova; DRAW-006 deve misurare l'impianto 2 senza renderizzare inutilmente gli altri.
4. **Vincoli fisici di posa non modellati.** Dall'11 settembre 2026 **non esiste nessuna
   linea di terra**: il PO ha disposto che su uno schema non c'è un sopra e un sotto, e il
   pavimento invisibile che era rimasto in `is_valid` è stato tolto. Se un giorno servirà
   un vincolo fisico vero — un'altezza, un ancoraggio — dovrà essere un campo esplicito del
   modello, dichiarato, non una frazione dell'altezza del foglio.
5. **Debito documentale storico.** Le vecchie sezioni operative sono conservate in Git,
   non devono tornare nei file di ingresso correnti.
6. **Geometria sensibile all'ordine delle connessioni.** La tavola composta in memoria e
   quella ottenuta dalla CLI non hanno ancora la stessa impronta; va risolto prima di
   usare il percorso end-to-end come prova di determinismo.
7. **Test geometrico inefficace.** L'ultima condizione della prova sulle colonne dei
   raccordi è logicamente ridondante; DRAW-006 deve sostituirla con una prova negativa
   che fallisca realmente quando un raccordo diventa colonna.
8. **Connettività multivia non modellata per stati.** Sull'impianto 4 produce domande di
   sicurezza troppo ampie; DRAW-006 introduce configurazioni idrauliche alternative.
9. **La tavola 2 non esce.** Sulla testa di `main` il preflight trova un rilievo
   bloccante — una tratta supera di 2,5 mm la propria porta e ci torna indietro — e una
   tavola con un bloccante non si scrive (D-063). È una regressione comparsa l'11 settembre
   quando la gerarchia ha cominciato a riconoscere come autostrada la mandata attraverso la
   deviatrice: la classificazione è giusta, la posa non la sa ancora onorare. La chiude
   `DRAW-008`.
10. **Il costo può barattare tutto con tutto, ed è il difetto di fondo.** Il ciclo è un
    greedy globale su un costo lessicografico, quindi ogni proprietà del disegno — la
    rettilineità del tronco, l'allineamento, i rami impilati — è una voce che si compra e
    si vende. L'11 settembre la stessa serie di modifiche ha reso buona la tavola 1 e ha
    fatto smettere di uscire la tavola 2. Non è un tetto di ricerca: alzarlo da 1 500/2 000
    a 6 000/6 000 non cambia nulla. **È il rischio principale aperto**, lo attacca
    `DRAW-008` con le fasi, e l'analisi sta in
    `docs/pm/2026-09-11-architettura-della-posa-a-fasi.md`.
11. **La misura «stacchi statici» conta anche ciò che statico non è.** Nel bucket finisce
    ogni tratta che non è rete ordinaria, quindi anche la linea di alimentazione del
    riempimento, che il vocabolario del progetto chiama `INBOUND`. Con il ponte la riga
    cresce senza che sia comparso uno stacco statico in più. La misura non è stata toccata:
    è una soglia del Work Package.

## Pacchetto attivo

`DRAW-008 — la posa a fasi: prima le autostrade` (`ACTIVE_WORK_PACKAGE.md`), approvato dal
PO l'11 settembre 2026. Architettura in
`docs/pm/2026-09-11-architettura-della-posa-a-fasi.md`, che **va letta per intera prima
del pacchetto**.

Il difetto che attacca non è una soglia: è che oggi ogni proprietà del disegno è una voce
di costo, quindi si compra e si vende. Tre fasi con un invariante duro ciascuna — il
tronco dritto per primo, poi il corredo che allunga il tronco invece di piegarlo, poi le
strade di servizio dove le curve si accettano — e la funzione di costo che ottimizza
**dentro** ciascuna fase invece che attraverso tutte.

## Prossimi gate

1. `DRAW-005-R1`: tavola 1 rifinita — **accettata e fusa dal PM**.
2. `DRAW-006-R1`: **consegnato con riserva**, in attesa di verifica del PM sulla PR #24.
   Le decisioni che il pacchetto chiede sono due: il rilievo geometrico del §8 del
   rapporto e le 13 prove rosse del §9.1, che il DEV non ha ammorbidito.
3. `DRAW-007`: la gerarchia della tavola — **fuso in `main`** con rilievi aperti.
4. `DRAW-008`: la posa a fasi — **pacchetto attivo**.
5. `DRAW-009`: gli ingressi ripetuti dell'adduzione (**I-061**), dopo DRAW-008.
6. `DRAW-010`: lo spessore del tratto per gerarchia (**I-059**).
7. Gate vertical slice: skill in una chat di lavoro pulita.
8. Proseguire gli impianti 3–5 uno per volta, cercando classi di difetto nuove.

## Documenti canonici

- missione e architettura: `docs/SKILL.md`;
- requisiti prodotto: `docs/prodotto/PRD_DISEGNATORE_MEP.md`;
- incarico DEV: `ACTIVE_WORK_PACKAGE.md`;
- roadmap: `docs/plans/2026-09-03-release-plan.md`;
- responsabilità: `docs/governance/OPERATING_MODEL.md`;
- input PO: `docs/input-pm/REGISTRO.md`;
- retrospettive: `docs/retrospectives/2026-09-05-retro-pm.md` e
  `docs/retrospectives/2026-09-10-retro-draw006r1.md` — **quest'ultima è vincolante per
  chi tocca posa, costo o routing**: §4 elenca le regole che lascia alle sessioni
  successive.
