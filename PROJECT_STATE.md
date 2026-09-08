# PROJECT STATE — Disegnatore MEP

**Aggiornato:** 2026-09-08 (PM, dopo verifica e merge di DRAW-005)
**Fonte operativa:** `ACTIVE_WORK_PACKAGE.md`
**Release corrente:** 0.2 — prima tavola tecnicamente corretta e approvata

## Stato verificato

| Area | Stato |
|---|---|
| Modello dati e grafo | operativi; il grafo resta la fonte unica |
| Completamento e assemblaggio | operativi sulla tavola 1; intercettazione in logica di gruppo manutenibile verificata in DRAW-005 |
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

Nessun incarico DEV è attivo. `DRAW-005` è accettato dal PM e attende il giudizio visivo
del PO sul PDF per chiudere il gate 0.2A. La specifica PM è stata attuata senza chiedere
al DEV di interpretare gli esempi del PO.

Punti vincolanti del pacchetto, tutti attuati in PR:

- filtro a Y classico;
- orientamento dei confini secondo il verso dell'acqua;
- lettere interne ai simboli sempre leggibili rispetto al foglio;
- intercettazione ragionata sul gruppo manutenibile, senza valvole ridondanti;
- valvola comune di mandata vicina all'accumulo;
- distinzione fra puffer, bollitore e accumulo combinato;
- per l'accumulo combinato: acqua tecnica nel mantello, serpentino sanitario istantaneo,
  ingresso AF e uscita ACS; un solo riempimento sul circuito tecnico;
- geometria delle porte PDC compatibile con valvole e routing rettilineo;
- sigle delle macchine sempre presenti; indirizzi di nodo opzionali.

## Rischi aperti

1. **Prodotto non ancora eseguito nel suo ambiente finale.** Prima degli impianti 2–5
   serve una prova verticale: nuova chat, input naturale, approvazione del grafo,
   generazione deterministica e restituzione del PDF.
2. **Libreria simboli non interamente certificata.** Prima della generalizzazione il PM
   deve completare la matrice fonti/forma/porte/ingombri; il DEV implementa solo la
   matrice approvata.
3. **Costo computazionale.** La tavola 1 richiede circa 70 secondi e oltre 2.000 routing
   di prova; va misurato sugli altri casi prima di consolidare l'algoritmo.
4. **Vincoli fisici di posa non modellati.** Una macchina `GROUND` può oggi salire per
   allineare le porte; un futuro vincolo fisico deve essere un campo esplicito del modello.
5. **Debito documentale storico.** Le vecchie sezioni operative sono conservate in Git,
   non devono tornare nei file di ingresso correnti.
6. **Geometria sensibile all'ordine delle connessioni.** La tavola composta in memoria e
   quella ottenuta dalla CLI non hanno ancora la stessa impronta; va risolto prima di
   usare il percorso end-to-end come prova di determinismo.
7. **Regressione nota sull'impianto 3.** Il grafo aggiornato non compone; la prova è xfail
   e deve tornare verde prima di dichiarare completata la generalizzazione 0.3.

## Prossimi gate

1. `DRAW-005`: grafo e simboli critici dell'impianto 1 corretti — **accettato e fuso dal PM**.
2. Gate 0.2A: giudizio PO sul PDF e chiusura degli input attuati.
3. Gate 0.2B: vertical slice della skill in una chat di lavoro pulita.
4. Release 0.3: generalizzazione controllata agli impianti 2–5.

## Documenti canonici

- missione e architettura: `docs/SKILL.md`;
- requisiti prodotto: `docs/prodotto/PRD_DISEGNATORE_MEP.md`;
- incarico DEV: `ACTIVE_WORK_PACKAGE.md`;
- roadmap: `docs/plans/2026-09-03-release-plan.md`;
- responsabilità: `docs/governance/OPERATING_MODEL.md`;
- input PO: `docs/input-pm/REGISTRO.md`;
- retrospettiva: `docs/retrospectives/2026-09-05-retro-pm.md`.
