# PROJECT STATE — Disegnatore MEP

**Aggiornato:** 2026-09-05
**Fonte operativa:** `ACTIVE_WORK_PACKAGE.md`
**Release corrente:** 0.2 — prima tavola tecnicamente corretta e approvata

## Stato verificato

| Area | Stato |
|---|---|
| Modello dati e grafo | operativi; il grafo resta la fonte unica |
| Completamento e assemblaggio | operativi, ma l'intercettazione per singola porta va corretta in logica di gruppo |
| Posa e routing | `DRAW-004` fuso; costo-peso, assi, dorsali e T ortogonali operativi |
| Simboli | 39 manifesti: 13 derivati da UNI 9511, 21 da pratica/fonti di settore, 5 ancora senza fonte puntuale |
| Etichette | fase separata dalla geometria; sigle principali sempre, indirizzi opzionali |
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

## Lavoro corrente

Il Work Package successivo è `DRAW-005`: correttezza MEP e simboli critici della tavola 1.
Deve attuare la specifica PM senza chiedere al DEV di interpretare gli esempi del PO.

Punti vincolanti:

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

## Prossimi gate

1. `DRAW-005`: grafo e simboli critici dell'impianto 1 corretti, tavola rigenerata.
2. Gate 0.2A: approvazione PO della tavola 1 per contenuto e colpo d'occhio.
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
