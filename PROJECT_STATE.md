# PROJECT STATE — Disegnatore MEP

**Aggiornato:** 2026-09-13 (DEV, consegna di DRAW-009 — l'ingresso vicino a chi serve,
e il tronco che si sposta tutto intero)
**Fonte operativa:** `ACTIVE_WORK_PACKAGE.md`
**Release corrente:** 0.3 — generalizzazione controllata, impianto 2

## Stato verificato

| Area | Stato |
|---|---|
| Modello dati e grafo | operativi; il grafo resta la fonte unica |
| Completamento e assemblaggio | operativi sulla tavola 1; tutti e cinque gli impianti arrivano alla posa; aperta la semantica dei compositi e delle multivia |
| Posa e routing | `DRAW-004` fuso; costo-peso, assi, dorsali e T ortogonali operativi. Da `DRAW-008` la posa è **a fasi**: il tronco si costruisce (`layout/spine.py`), il corredo lo allunga invece di piegarlo. Da `DRAW-009` il tronco **trasla tutto intero** portandosi dietro il proprio corredo (`Improver._block_moves`), e un **ingresso di rete** si posa addosso all'utente che serve invece di aprire la lettura. L'instradatore e i suoi pesi non sono stati toccati |
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

### Dove siamo davvero, con DRAW-009 consegnato (non fuso)

`DRAW-009` è **consegnato in PR, non fuso**: il merge su `main` è del PO
(`OPERATING_MODEL.md` §1.2.1). Le misure qui sotto sono quelle del ramo di consegna,
lette sulla geometria che la CLI scrive; il rapporto completo sta in
`docs/collaudi/DRAW-009/RAPPORTO.md`.

| | testa di `main` (DRAW-008 fuso) | DRAW-009 |
|---|---|---|
| **Tavola 1** — rete ordinaria | 4 pieghe / 1 incrocio / 465,0 mm | **4 / 1 / 430,0 mm** |
| **Tavola 1** — totale | 10 pieghe / 1 incrocio / 620,0 mm | **4 / 1 / 485,0 mm** |
| **Tavola 1** — autostrade rettilinee | 8 su 8, zero pieghe | **8 su 8, zero pieghe** |
| **Tavola 1** — organi D-120 | 14 su 15 | **15 su 15** |
| **Tavola 2** — rete ordinaria | 9 / 6 / 755,0 mm | **5 / 1 / 555,0 mm** |
| **Tavola 2** — totale | 15 pieghe / 11 incroci / 877,5 mm | **5 / 1 / 607,5 mm** |
| **Tavola 2** — pieghe di autostrada | 4 | **2**, una per ciascuna delle due tratte che nessuna posa raddrizza |
| **Tavola 2** — `deviatrice.out_b → bollitore.coil_in` | 3 pieghe | **1 piega**: scende, attraversa il ritorno in perpendicolare, corre bassa |
| **Tavola 2** — nodi condivisi col tronco | 8 | **0** |
| **Tavola 2** — confini di rete su `cold_water` | 1, con una linea che serve due utenti in serie | **2**, uno per utente, ciascuno con la propria rete |
| **Tavola 2** — organi D-120 | 13 su 15 | **14 su 15** |

Il perché del salto sulla tratta `deviatrice.out_b → bollitore.coil_in` è misurato in
`docs/collaudi/DRAW-009/RAPPORTO.md` §3.9, e lo strumento che lo rimisura è
`docs/collaudi/DRAW-009/perche-la-strada-bassa-non-c-era.py`: la strada bassa non era cara,
**non c'era**, e a murarla erano il vaso, il manometro e la soglia del riempimento, tutti
appesi sotto il tronco alla quota del `coil_in`.

### Le misure di DRAW-008, per confronto

| | testa di `main` | DRAW-008 |
|---|---|---|
| **Tavola 1** | rete ordinaria 6 pieghe / 3 incroci / 550,0 mm; zero pieghe sulle 8 autostrade | rete ordinaria **4 / 1 / 465,0 mm**; zero pieghe sulle 8 autostrade; backtracking 0; D-120 14 su 15 |
| **Tavola 2** | **non esce**: un rilievo bloccante (`RUN_OVERSHOOTS_ITS_PORT`) | **esce, nessun bloccante**; rete ordinaria 9 / 6 / 755,0 mm; 8 autostrade rettilinee su 10 |
| **Autostrade storte, tavola 2** | 4 su 10 | **2 su 10**, ed è il massimo raggiungibile: nessuna posa ammessa dal catalogo le raddrizza (vedi rischio 12) |
| **Suite** | 11 rosse, 1411 verdi | **13 rosse, 1435 verdi**: una delle undici è tornata verde, tre sono nuove e sono regressioni dichiarate (rischio 15). Nessuna prova convertita in `skip` o `xfail` |
| **`ruff`, `mypy --strict`** | puliti | puliti |
| **Determinismo** | — | due generazioni, stessa impronta e stessa geometria byte per byte, su tavola 1 e tavola 2 |

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
9. **La tavola 2 non esce — chiuso da `DRAW-008`, in attesa del merge del PO.** Sulla
   testa di `main` il preflight trovava un rilievo bloccante; sul ramo di consegna di
   `DRAW-008` la tavola esce senza bloccanti.
10. **Il costo poteva barattare tutto con tutto — attenuato da `DRAW-008`, non chiuso.**
    Il ciclo resta un greedy su un costo lessicografico, ma **la rettilineità del tronco
    non è più una voce di costo**: è un vincolo di `Improver.is_valid`, e nessun guadagno
    la compra. Restano voci di costo l'allineamento del resto e i rami impilati. L'analisi
    sta in `docs/pm/2026-09-11-architettura-della-posa-a-fasi.md`.
11. **La misura «stacchi statici» conta anche ciò che statico non è.** Nel bucket finisce
    ogni tratta che non è rete ordinaria, quindi anche la linea di alimentazione del
    riempimento, che il vocabolario del progetto chiama `INBOUND`. Con il ponte la riga
    cresce senza che sia comparso uno stacco statico in più. La misura non è stata toccata:
    è una soglia del Work Package.
12. **Due tratte di autostrada della tavola 2 non possono essere rettilinee.** L'uscita
    secondaria della deviatrice guarda in basso, la serpentina del bollitore si imbocca da
    sinistra e il bollitore non ammette rotazioni: nessuna posa le mette una di fronte
    all'altra. Non è un difetto della posa, è il catalogo, e il codice lo calcola e lo
    nomina (`spine.SpineLayout.impossible`). Il PO decide se accettarlo, dare una
    rotazione al bollitore o mettere un raccordo nel grafo.
13. **Le tratte di rango inferiore attraversavano il tronco — chiuso da `DRAW-009`.**
    Erano 8 nodi condivisi; adesso sono **zero**. L'acqua fredda non attraversa più il
    foglio perché ciascun utente ha il proprio ingresso (I-061), e ogni ingresso si posa
    addosso a chi serve.
14. **La catena a fasi, da sola, toglieva la tavola all'impianto 4.** Sulla testa di `main`
    l'impianto 4 usciva; con le sole fasi l'instradamento falliva su `p7-a`. `compose_sheet`
    ha ora un **ripiego dichiarato** — posa seminata dal tronco, poi il ciclo senza le fasi,
    poi la disposizione di partenza — e con quello l'impianto 4 torna a uscire. Il ripiego
    è una rete di sicurezza, non una soluzione: finché scatta, quell'impianto non gode
    della posa a fasi. `docs/collaudi/DRAW-008/RAPPORTO.md` §6.2.
15. **Le tre prove rosse di `DRAW-008` — chiuse da `DRAW-009`.** Le due di vicinanza
    tornano verdi senza essere toccate, come `DRAW-009` §E prevedeva; la terza si chiude
    per decisione del PO, con la prova riscritta su ciò che vuole davvero — l'impilamento,
    non l'ordine — e con la sua negativa.
16. **La fase del tronco consegna ancora una posa con pezzi sovrapposti.** Sulla tavola 2
    `lay_the_spine` + `carry_the_rest` consegnano nove coppie di pezzi addosso, fra cui il
    bollitore e il volano. `_relieve` non le separa perché il tronco di un circuito chiuso
    è un **anello**: qualunque sottoalbero si sposti contiene anche l'altro pezzo della
    coppia. Non è nuovo — la stessa posa esce identica sulla testa di `main` — e `DRAW-009`
    l'ha reso innocuo invece che risolto, permettendo al ciclo di uscirne. Finché resta
    così, la tavola 2 esce dal **ripiego** di `compose_sheet` invece che dalla propria posa
    a fasi. `docs/collaudi/DRAW-009/RAPPORTO.md` §6.3 e §7.3.
17. **L'ordine degli stacchi lungo il tronco non ha ancora un padrone.** La proprietà è
    misurata e vale su tutt'e due le tavole — le due tratte verso lo stesso pezzo corrono
    annidate — ma vale perché la topologia del flusso la impone, non perché la fase del
    tronco la scelga. `docs/collaudi/DRAW-009/RAPPORTO.md` §3.11 e §7.1.
18. **La tratta del prelievo ACS ha una piega.** Migliora — da 2 pieghe e 2 nodi su
    autostrada a 1 piega e zero — ma il criterio 3 chiede zero. `DRAW-009` posa addosso al
    proprio utente gli **ingressi**, non i prelievi: se il PO intende la regola anche per
    quelli è una riga, ma è una scelta di rappresentazione.
    `docs/collaudi/DRAW-009/RAPPORTO.md` §6.1 e §7.2.
19. **Una prova di `DRAW-007` e la regola monotona di `DRAW-009` non possono valere
    insieme.** `Improver.is_valid` rifiutava ogni candidata che lasciasse due pezzi
    addosso; `DRAW-009` la rende monotona — una mossa risponde delle sovrapposizioni che
    **crea**, non di quelle che trova — perché senza quella regola, sulla posa sovrapposta
    del rischio 16, *ogni* candidata è non valida e il ciclo resta inchiodato.
    `test_l_allineamento_non_si_accetta_quando_rende_la_tavola_peggiore` chiede il
    contrario, e diventa rossa: è l'unica regressione di `DRAW-009`. La regola più stretta
    che la farebbe passare — «né crea né approfondisce» — toglierebbe al ciclo la
    traslazione di blocco, misurato. La cura vera è il rischio 16.
    `docs/collaudi/DRAW-009/RAPPORTO.md` §6.5 e §7.5; lo strumento è
    `docs/collaudi/DRAW-009/le-due-sovrapposizioni.py`.

## Pacchetto attivo

`DRAW-009 — l'ingresso vicino a chi serve, e il tronco che si sposta tutto intero`
(`ACTIVE_WORK_PACKAGE.md`), approvato dal PO in sessione fra l'11 e il 13 settembre 2026.
Parte dalla testa di `main` con `DRAW-008` fuso, ed è **consegnato in PR, non fuso**:
`docs/collaudi/DRAW-009/RAPPORTO.md`.

Le tre cose che il PO ha deciso e che il pacchetto attua:

1. **Gli ingressi dell'acqua fredda si moltiplicano e si posano addosso a chi servono**
   (I-061). Sulla tavola 2 la rete `fredda` è oggi **una linea sola che serve due utenti in
   serie** ai due capi del foglio, e sei degli otto nodi che un rango inferiore condivide
   col tronco sono suoi.
2. **Il tronco è un corpo rigido, non un corpo immobile**: trasla tutto intero portandosi
   dietro ciò che gli pende, e si allunga lungo il proprio asse. Non si piega e non si
   deforma. È una mossa che il ciclo oggi non ha.
3. **Il bollitore non ruota, né lui né i suoi attacchi.** Le due tratte che non possono
   essere rettilinee si risolvono con l'**ordine degli stacchi lungo il tronco**, non con
   una rotazione né con un raccordo aggiunto al grafo.

Rapporto della consegna precedente in `docs/collaudi/DRAW-008/RAPPORTO.md`; architettura
della posa a fasi in `docs/pm/2026-09-11-architettura-della-posa-a-fasi.md`, che resta da
leggere per intera prima del pacchetto.
