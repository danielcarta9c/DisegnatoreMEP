# PROJECT STATE — Disegnatore MEP

**Aggiornato:** 2026-09-10 (PM, revisione PR #24 e apertura DRAW-006-R1)
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

`DRAW-005-R1` è approvato e fuso con PR #21, merge `eeebc58`. Baseline della tavola 1:
una sicurezza di circuito sulla mandata comune, zero sull'accumulo e sulle singole PDC;
39 pezzi; rete ordinaria 4 curve, 1 incrocio e 425 mm; stacchi statici 0 curve,
0 incroci e 45 mm. Tutti e cinque gli impianti arrivano alla posa.

La PR #24 di `DRAW-006`, testa `9b925b7`, è respinta nello stato corrente. Conserva
avanzamenti validi su rubinetto portamanometro, compositi e stati delle multivia, ma
presenta blocker materiali: ordine degli accessori dipendente dagli ID, mancato
allineamento PDC–puffer attraverso la deviatrice, adduzione ACS e riempimento tecnico
modellati in modo non corretto e una valvola D-120 a 27,5 mm.

`DRAW-006-R1` corregge gli stessi punti sulla stessa PR #24. La tavola 2 resta l'unica
consegna grafica completa; tavola 1 regressione automatica, impianti 3–5 soltanto posa.

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
4. **Vincoli fisici di posa non modellati.** Una macchina `GROUND` può oggi salire per
   allineare le porte; un futuro vincolo fisico deve essere un campo esplicito del modello.
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
9. **Semantica e geometria ancora accoppiate.** Applicare il corretto ordine funzionale
   peggiora oggi curve e incroci: DRAW-006-R1 rende l'ordine un vincolo e recupera costo
   con movimenti di gruppo e routing, mai alterando la semantica.
10. **Riempimento tecnico modellato a una porta.** Non rappresenta il ponte reale fra
    acqua fredda e ritorno tecnico; DRAW-006-R1 introduce due reti, due porte e funzioni
    integrate di catalogo.

## Prossimi gate

1. `DRAW-005-R1`: tavola 1 rifinita — **accettata e fusa dal PM**.
2. `DRAW-006-R1`: approvare la PR #24 corretta sulla prima generalizzazione dell'impianto 2.
3. Gate vertical slice: skill in una chat di lavoro pulita.
4. Proseguire gli impianti 3–5 uno per volta, cercando classi di difetto nuove.

## Documenti canonici

- missione e architettura: `docs/SKILL.md`;
- requisiti prodotto: `docs/prodotto/PRD_DISEGNATORE_MEP.md`;
- incarico DEV: `ACTIVE_WORK_PACKAGE.md`;
- roadmap: `docs/plans/2026-09-03-release-plan.md`;
- responsabilità: `docs/governance/OPERATING_MODEL.md`;
- input PO: `docs/input-pm/REGISTRO.md`;
- retrospettiva: `docs/retrospectives/2026-09-05-retro-pm.md`.
