# PROJECT STATE — Disegnatore MEP

**Aggiornato:** 2026-09-10 (DEV, consegna di DRAW-006-R1 sulla PR #24)
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

`DRAW-006-R1` è stato eseguito sulla stessa PR #24 e consegnato il 2026-09-10 **con due
rilievi aperti dichiarati**: la geometria non recuperata e la **suite non verde** (1373
verdi, 29 rosse all'ultima esecuzione integrale; 16 chiuse dopo, 13 rimaste). Il PM non
l'ha ancora verificato. I quattro difetti semantici sono corretti e provati:

- **ordine semantico** indipendente dagli identificativi: il piede di uno stacco parla per
  l'accessorio terminale, e lo spareggio fra pezzi altrimenti pari è **strutturale**
  (`src/disegnatore_mep/model/order.py`), non un nome né una posizione nel file. Chiude
  anche il DIFETTO 2 del collaudo di fine sessione, che era ancora `xfail`;
- **assi attraverso i pezzi**: `Improver.linked_peers` cammina fra raccordi, catene in
  linea e multivia, uno stato ammesso per volta;
- **adduzione ACS**: un solo gruppo composito EN 1487 (`dhw-safety-group`), nessun
  duplicato esterno di ritegno e intercettazione, vaso sanitario condizionale al dato di
  bordo, scarico sulla porta dedicata dove il serbatoio la dichiara;
- **riempimento**: ponte a due reti e due porte, `cold_water` → `heating_water`, con le
  funzioni della serie 553 dichiarate interne e una domanda dove la sorgente fredda non è
  dichiarata.

La vicinanza D-120 del §E è chiusa dove il Work Package la nomina: la valvola che stava a
27,5 mm dal defangatore sta a 2,5 mm, e le due prove generali del blocco sono verdi. La
misura di collaudo dice però 14 su 15, perché conta anche un quarto caso che la regola non
dichiara — l'organo che raggiunge il pezzo servito attraverso un raccordo: l'intercettazione
generale dell'acqua fredda passa da 5,0 a 7,5 mm perché il ponte del riempimento aggiunge
una seconda presa sulla stessa linea.

Il grafo dell'impianto 2 passa da 45 a 41 pezzi. **La geometria non è stata recuperata** e
resta il rilievo aperto del pacchetto: rete ordinaria della tavola 2 da 7/2/670 mm a
12/8/785 mm, e la tavola 1 esce dalle soglie del §A.5 (11 pieghe contro 4, 487,5 mm contro
425). La prova di regressione della tavola 1 è **rossa e lasciata rossa**, come il Work
Package prescrive per un'incompatibilità. Misure, analisi e alternative provate stanno in
`docs/collaudi/DRAW-006-R1/RAPPORTO.md` §8.

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
9. **La posa non sa ancora trattare un ponte fra due reti.** DRAW-006-R1 ha reso l'ordine
   funzionale un vincolo duro e ha generalizzato i candidati di asse, ma il ciclo di posa
   si ferma in un ottimo locale peggiore: la tavola 2 passa da 7 pieghe e 2 incroci a 12 e
   8, e la tavola 1 esce dalle soglie di regressione. Non è il tetto di ricerca —
   alzandolo l'esito non cambia. La revisione incrociata del 10 settembre indica come
   causa più probabile il rischio 10, non il ciclo in sé.
10. **Il costo di posa non ha gerarchia: per il router tutte le tubazioni sono uguali.**
    La dorsale che unisce generatore e accumulo — quella che il PO chiama «l'autostrada» —
    pesa quanto lo stacco di un manometro, quindi il ciclo baratta volentieri la struttura
    della tavola per un numero totale più basso. È la spiegazione più probabile del
    rilievo 9 e della prova sulle zone impilate, e **non è intercettabile da nessuna
    soglia**, perché le soglie misurano il totale e non dove il totale si concentra.
    Input **I-057** e **I-058**; analisi in
    `docs/retrospectives/2026-09-10-retro-draw006r1.md` §1. **È il rischio principale
    aperto oggi**, e viene prima del rilievo 9.
11. **La misura «stacchi statici» conta anche ciò che statico non è.** Nel bucket finisce
    ogni tratta che non è rete ordinaria, quindi anche la linea di alimentazione del
    riempimento, che il vocabolario del progetto chiama `INBOUND`. Con il ponte la riga
    cresce senza che sia comparso uno stacco statico in più. La misura non è stata toccata:
    è una soglia del Work Package.

## Prossimi gate

1. `DRAW-005-R1`: tavola 1 rifinita — **accettata e fusa dal PM**.
2. `DRAW-006-R1`: **consegnato con riserva**, in attesa di verifica del PM sulla PR #24.
   Le decisioni che il pacchetto chiede sono due: il rilievo geometrico del §8 del
   rapporto e le 13 prove rosse del §9.1, che il DEV non ha ammorbidito.
3. Gate vertical slice: skill in una chat di lavoro pulita.
4. Proseguire gli impianti 3–5 uno per volta, cercando classi di difetto nuove.

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
