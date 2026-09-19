# PROJECT STATE — Disegnatore MEP

**Aggiornato:** 2026-09-15 (PM, cold eye review dopo il merge di DRAW-009)
**Ingresso del PM:** `docs/pm/STATO-PM.md`
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

### Dove siamo davvero, con DRAW-009 fuso (PR #27, `2155c22`)

`DRAW-009` è stato **verificato dal PM e fuso** il 14 settembre 2026 attraverso la
PR #27, su autorizzazione del PO al merge (D-123, disposizione del 14 settembre): dodici
criteri raggiunti, quattro raggiunti in parte, nessuno non raggiunto. Verdetto criterio per
criterio in `docs/pm/2026-09-14-review-pr27-draw009.md`. Le misure qui sotto sono quelle del ramo di consegna,
lette sulla geometria che la CLI scrive; il rapporto completo sta in
`docs/collaudi/DRAW-009/RAPPORTO.md`.

| | testa di `main` (DRAW-008 fuso) | DRAW-009 |
|---|---|---|
| **Tavola 1** — rete ordinaria | 4 pieghe / 1 incrocio / 465,0 mm | **4 / 1 / 430,0 mm** |
| **Tavola 1** — totale | 10 pieghe / 1 incrocio / 620,0 mm | **4 / 1 / 470,0 mm** |
| **Tavola 1** — autostrade rettilinee | 8 su 8, zero pieghe | **8 su 8, zero pieghe** |
| **Tavola 1** — organi D-120 | 14 su 15 | **15 su 15** |
| **Tavola 2** — rete ordinaria | 9 / 6 / 755,0 mm | **5 / 1 / 555,0 mm** |
| **Tavola 2** — totale | 15 pieghe / 11 incroci / 877,5 mm | **5 / 1 / 600,0 mm** |
| **Tavola 2** — pieghe di autostrada | 4 | **2**, una per ciascuna delle due tratte che nessuna posa raddrizza |
| **Tavola 2** — `deviatrice.out_b → bollitore.coil_in` | 3 pieghe | **1 piega**: scende, attraversa il ritorno in perpendicolare, corre bassa |
| **Tavola 2** — nodi condivisi col tronco | 8 | **0** |
| **Tavola 2** — confini di rete su `cold_water` | 1, con una linea che serve due utenti in serie | **2**, uno per utente, ciascuno con la propria rete |
| **Tavola 2** — organi D-120 | 13 su 15 | **14 su 15** |
| **Suite** | 13 rosse, 1435 verdi | **10 rosse, 1470 verdi**: sei chiuse, tre nuove e dichiarate con la misura, sette che erano rosse e restano. Nessuna prova convertita in `skip` o `xfail` |

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
    **AVVERATO il 14 settembre 2026, dopo il merge di `DRAW-009`.** La rete non regge più:
    l'impianto 4 **non produce più una tavola**. Misurato dal PM con lo stesso
    comando sui due lati — su `b63e3e6` esce, su `2155c22` no, in 12 secondi, con
    `run s3-a on network secondario cannot be routed`. Nessuna prova se n'è accorta (rischio
    23). È il primo criterio di `DRAW-010`.
    `docs/pm/2026-09-14-review-pr27-draw009.md` §7.
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
20. **Due prove hanno perso il proprio caso.** La prova che tiene la valvola di isolamento
    stretta al raccordo passante non trova più, sulla propria fixture, nessuna tratta con
    quella forma: §A.1 ha tolto il raccordo dell'acqua fredda dal ritorno tecnico e con lui
    la scomposizione che metteva la valvola dalla parte giusta. La sua guardia grida invece
    di passare a vuoto, ed è giusto così, ma **quella proprietà non è più sorvegliata da
    nessuna parte**. E la prova sulle frecce pretende che ogni tratta non statica ne porti
    una, mentre il renderer una freccia la mette solo su un tratto lungo almeno 4,0 mm: la
    tavola ha adesso una tratta ordinaria lunga un passo. `RAPPORTO.md` §6.7 e §7.7–§7.8;
    lo strumento è `docs/collaudi/DRAW-009/due-prove-senza-caso.py`.
21. **Due prove difendono il pavimento invisibile, che non esiste più.**
    `test_una_macchina_a_terra_puo_partecipare_a_un_candidato_verticale` e
    `test_the_hard_constraints_hold_after_improvement` asseriscono ancora
    `bottom_mm <= levels.ground_mm`, cioè il vincolo che il PO ha abolito l'11 settembre
    2026 e che `DRAW-008` ha tolto da `is_valid`. Sono rosse sulla testa di `main` e restano
    rosse: fuori dal perimetro di `DRAW-009`, ma finché stanno lì chi le legge crede che la
    regola esista. `RAPPORTO.md` §7.6.
22. **Un cricchetto già scattato, e non incassato.** L'impianto 2 torna a comporsi su una A3
    — `test_tornano_a_comporre_quando_la_composizione_compatta` è un `xfail(strict=True)` ed
    è rosso **anche sulla testa di `main`**. Sul ramo di `DRAW-009` quell'impianto passa
    tutte e cinque le prove che `COMPONIBILI` impone, misurato. Spostarlo da
    `NON_COMPONGONO` a `COMPONIBILI` è una riga, toglie una rossa e ne rende esigibili
    cinque verdi; non è stata fatta perché la rossa non nasce qui. `RAPPORTO.md` §7.9.

23. **La suite sorveglia la composizione di un impianto solo.**
    `COMPONIBILI = ("prova-1-due-pdc-accumulo-combinato.json",)`: è l'unico impianto di cui
    una prova pretenda che sappia comporsi. Gli altri compongono — quando compongono — **per
    capacità, non per contratto**, e se la perdono la suite resta verde. È così che si è
    perso l'impianto 4 senza che nessuno se ne accorgesse, ed è un difetto della copertura
    che vale quanto il difetto che ha nascosto. `DRAW-010` §C.

24. **«Aperto» ha smesso di voler dire qualcosa nel registro degli input.** 54 righe aperte
    su 63, 5 chiuse. Molte sono con ogni evidenza soddisfatte — `I-019` sulla linea di terra
    è chiuso mentre `I-024`, che dice la stessa cosa, è aperto — e due chiedono oggi il
    **contrario** di una decisione vigente: `I-060` vuole il PM sdoppiato che `D-130` ha
    abolito, `I-014` vuole la regola «ogni sessione finisce su `main`» che `D-123` ha
    superato. Quattro righe non hanno uno stato leggibile (`I-001`, `I-003`, `I-004`,
    `I-005`). Serve una passata di triage col PO: la chiusura di un input è sua, non del PM.
25. **`DRAW-007` non ha cartella di collaudo.** `docs/collaudi/` porta DRAW-001…006-R1, 008
    e 009: il 007 è stato fuso senza rapporto agli atti, ed è l'unico buco nella catena delle
    consegne.

## Dove siamo — 19 settembre 2026, dopo la PR #44

**`DRAW-012` e `DRAW-013` sono fusi** con la PR #44 (`a835006`): la struttura, le autostrade
e l'invariante della catena di `DRAW-012`, piu' il margine di 25 mm dal bordo (D-143), il
vincolo degli organi di servizio (D-145) e la curva dichiarata della distribuzione (D-144, in
parte). Undici criteri su quindici; i quattro mancanti erano **tutti** bloccati da `place.py`
e dalle rotazioni del simbolo del collettore — cioe' da un perimetro che aveva scritto il PM.

**Lo stesso giorno il PO ha cambiato rotta**, e sono le disposizioni **D-147**–**D-150**:

| | |
|---|---|
| **D-147** | PM e DEV tornano a essere **un agente solo**, nella stessa sessione. La fusione la approva il PO guardando le tavole |
| **D-148** | **Oltre l'A3 si va**: i formati ordinari sono A4, A3, A2, A1 |
| **D-149** | **Il riempimento del foglio esce dagli obiettivi** e torna una misura; la dilatazione di D-142 e' ritirata |
| **D-150** | **Una tratta che non si instrada non uccide piu' la tavola**: prende una spezzata di ripiego, si marca `unresolved`, e il preflight la nomina |

La ragione di D-147, in una riga: **`place.py` e' stato fuori perimetro per quattro pacchetti
di fila, ed e' li' che stavano le tavole 3, 4 e 5.**

### Le tre tavole che non uscivano, e perche'

Misurato il 19 settembre, prima di toccare il codice. **Tutt'e tre morivano per una sola
tratta**, e tutt'e tre contro il **bordo destro dell'area A3**:

| Impianto | Dove moriva | Che cos'e' in millimetri |
|---|---|---|
| 3 | `give the run a longer straight length` | non c'e' rettilineo |
| 4 | `no route from (134, 80) to (144, 80)` | la destinazione e' a **x 370** su una griglia che finisce a **x 360**: e' fuori dal foglio |
| 5 | `run into an obstacle at (140, 65)` | «l'ostacolo» e' **x 360,0 mm**, cioe' il bordo |

**L'impianto 4 esce su A2 senza toccare nient'altro** (misurato: 195 s). Gli impianti 3 e 5
su A2 falliscono ancora, ma per difetti **veri** — un ostacolo vero a due passi dove ne
servono cinque, e uno stacco di 5 mm con un accessorio in linea che ne chiede 7,5 — non piu'
contro il bordo. Quelle sono le cause da curare, ed e' il lavoro corrente.

---

## ~~Consegna in revisione~~ — DRAW-012, **fuso** nella PR #44 (scritta dal DEV, 17 settembre 2026)

`DRAW-012 — il motore disegna nell'ordine del disegnatore` è consegnato in una PR non fusa,
dalla testa di `main` (`8589620`). Rapporto e artefatti: `docs/collaudi/DRAW-012/`.

**Che cosa cambia nel motore**

- **La gerarchia**: sono macchine di spina **tutti** i generatori, gli scambiatori, gli
  accumuli e i collettori; è autostrada anche la strada che dagli accumuli porta ai
  terminali e al prelievo sanitario, con il circolatore dentro la tratta. L'ingresso
  dell'acqua fredda resta uno stacco di servizio, riconosciuto dal verso della porta del
  confine di rete.
- **`layout/highways.py`** è nuovo: l'**autostrada intera**, la catena di tratte che
  attraversa i propri crocevia, con l'invariante verificato su di lei e non su ogni
  frammento.
- **Il costo** non guarda più i millimetri (D-139): restano curve e attraversamenti, e il
  riempimento entra come **finestra** 45–65 % (D-140) letta insieme alla copertura
  dell'ingombro (D-141). La finestra è un dato condiviso fra costo e preflight, che adesso
  avvisa anche quando il foglio è troppo pieno.
- **Quando la struttura non si instrada non si butta la fase**: si cede una catena per
  volta, e il diario della composizione dice con quale via la tavola è uscita.
- **Il caso di prova 4** è quello di D-137, e il catalogo ha la **commutatrice a tre vie**
  (`switching-valve-3way`, funzione `circuit_switching`, famiglia **VCR**). Il documento
  pubblicato dell'impianto 4 e il confronto per il PM sono rigenerati con il grafo nuovo:
  43 pezzi il 9 settembre, **46** oggi.

**Le misure**

| | tavola 1 | tavola 2 |
|---|---|---|
| riempimento | 29,8 % → **45,1 %** | 50,1 % → **64,1 %** |
| copertura ingombro | 0,625 → **0,750** | 0,625 → **0,750** |
| curve | 4 → 4 | 5 → 5 |
| attraversamenti | 1 → 1 | 1 → 1 |
| squilibrio quadranti | 2,11 → **1,94** | 32,5 → **8,16** |
| larghezza occupata | 245 → **322,5 mm** | 257,5 → **315 mm** |

Tutt'e due dentro la finestra 45–65 %, con la copertura dell'ingombro che sale insieme al
riempimento (D-141) e **nessun peggioramento** su curve e attraversamenti.

**La suite**

Su `main` 10 rosse, 1470 verdi, 24 saltate, 11 xfailed. Qui le rosse sono **13**: il
criterio 13 del pacchetto **non è raggiunto**, e le tre in più sono tutte in
`tests/layout/test_stacchi_minimi_e_interasse.py`, sulle due fixture
`*_con_accumulo_combinato`. Due di loro non falliscono su un'asserzione: falliscono perché
la tavola non esce. Nessuna prova è stata spenta per far quadrare il saldo; il rapporto
§7.7 porta le cinque misure con cui ho provato a chiuderle.

**Che cosa resta aperto, e sta nel rapporto §7**

1. **D-060 e D-138 si contendono la stessa coordinata**, ed è una domanda al PO: fra due
   zone impilate e una strada di ritorno rettilinea, quale delle due vuole. È la sola cosa
   che la consegna toglie — una prova di `test_objective.py` — ed è dichiarata.
2. Due **corsie di catena di macchina** che si incrociano non le separa nessuna mossa di un
   pezzo solo: è ciò che ferma le tavole 4 e 5, e in altra forma la 3. Gli impianti che
   producono una tavola restano 1 e 2, come su `main`.
3. L'ordine di instradamento e il rango sono la stessa chiave, e con la gerarchia nuova
   quella chiave governa una classe molto più grande. I confini di rete finiscono lontani
   dal pezzo che servono, e nessun numero se ne accorge.

---

## ~~Consegna in revisione~~ — DRAW-013, **fuso** nella PR #44 (scritta dal DEV, 19 settembre 2026)

`DRAW-013 — la tavola si allarga tutta insieme, non tocca il bordo, e la distribuzione ha la
sua forma` è consegnato in una PR non fusa. **Parte dal ramo di `DRAW-012`**, non da `main`:
il primo commit del ramo è il merge di `17ff425` su `651310f`, da solo. Rapporto e artefatti:
`docs/collaudi/DRAW-013/`, con le tavole in PDF (D-146).

**Che cosa cambia nel motore**

- **`layout/dilate.py`** è nuovo: la **dilatazione proporzionale** della posa (D-142). Su
  ciascun asse una funzione monotona a tratti — pendenza 1 sui simboli, vuoti allargati di un
  fattore unico per foglio — scelta dopo che il disegno è risolto. Simboli della loro misura,
  nessun pezzo spostato rispetto agli altri, nessuna piega e nessun attraversamento in più.
- **Il margine di rispetto** (D-143) entra in tre posti: la **chiave di costo della posa**
  (prima del riempimento), il limite della dilatazione, e un rilievo di preflight nuovo,
  `DRAWING_TOUCHES_THE_BORDER`, che scatta solo su chi il bordo lo tocca **senza esserne
  autorizzato**.
- **La forma della distribuzione** (D-144): `highways.turns_of` conta le curve, e la strada
  che da un accumulo porta a un'utenza ne può fare **una, dichiarata** — che il diario non
  conta fra le cedute. L'invariante della retta intera resta per le autostrade fra le macchine
  di spina.
- **La guardia del riempimento è un divieto** e non più una soglia (D-141): un riempimento
  salito mentre la copertura scende si legge come quello dell'altra posa, e il caso lieve
  costa quanto il caso grosso.
- **Gli organi di servizio stanno addosso al pezzo che servono** (D-145), come **vincolo** di
  `is_valid` e non come voce di costo: D-139 non è toccata.
- **Lo stiramento del singolo tratto** resta, e il riempimento non lo può più comprare.

**Le due tavole**

| | tavola 1 | tavola 2 |
|---|---|---|
| margine dal bordo | 12,5 → **25,0 mm** | 17,5 → **25,0 mm** |
| curve / attraversamenti | 4/1 → 4/1 | 5/1 → 5/1 |
| riempimento | 45,1 → 42,9 % | 64,1 → 61,1 % |
| acqua fredda dal pezzo che alimenta | 40,0 → **20,0 mm** | 135,0 → 120,0 mm |
| fattore di dilatazione | 1,08 | 1,25 |

Gli impianti che producono una tavola restano **1 e 2**, gli stessi del ramo di partenza.

**La suite**

Ramo di partenza: **13 rosse, 1482 verdi**, 24 saltate, 11 xfailed — esattamente il
riferimento che il pacchetto dichiara, riprodotto in un worktree su `0a2b7fd` con il proprio
ambiente. Qui: **12 rosse, 1500 verdi**, 24 saltate, 11 xfailed. Il criterio 13 è **raggiunto**,
e le dodici rosse sono tutte sottoinsieme delle tredici: nessuna rossa nuova.

⚠️ La rossa che si chiude **non è quella che il criterio nomina**: resta rossa
`test_sulla_tavola_composta_nessuno_stacco_e_piu_lungo_del_minimo_senza_una_ragione`, e si
chiude invece `test_rami_di_servizio.py::test_nessuna_freccia_sui_rami_statici...`. Il rapporto
§7.7 misura che cosa costerebbe chiudere quella nominata: due tavole peggiori.

`ruff` pulito; `mypy` con i **due** errori che stanno già sul ramo di partenza, in un file che
questo pacchetto non tocca.

**Che cosa resta aperto, e sta nel rapporto §7**

1. **Il pettine di D-144 è bloccato dal simbolo del collettore**: `zone-manifold` dichiara
   `allowed_rotations_deg: [0]`, e per D-049 quel campo è un vincolo tecnico. **Domanda al
   PO**: un collettore di zona si può disegnare in verticale?
2. **Il margine di D-143 e la finestra di D-140 non stanno insieme sulla tavola 1**: portarla
   in finestra vuol dire tornare a 322,5 mm di ingombro e 13,75 mm dal bordo, cioè alla tavola
   che il PO ha bocciato. **Domanda al PO.**
3. **La griglia quantizza la dilatazione**: un vuoto cresce solo se `round(g·k) > g`, e su
   questi impianti i vuoti sono quasi tutti di uno o due passi. La dilatazione ha mosso 2,5 mm
   sulla tavola 1 e 10 mm sulla tavola 2.
4. **Il riempimento non sale «per dilatazione e non per altro»**, come §E si aspettava: la posa
   ha ancora la finestra nella chiave, perché D-140 e D-141 non si toccano. **Da decidere dal
   PM**, con i numeri del rapporto §7.6.
5. **§G ammette due letture del «vincolo dichiarato», e la più stretta disegna peggio.** Il
   rapporto §7.7 porta tre varianti misurate sulle tavole: quella consegnata, il tetto stretto,
   e il tetto stretto con l'attuazione del vincolo — che chiude la rossa del criterio 13 e
   porta l'acqua fredda della tavola 2 a 192,5 mm, peggio dei 135 del ramo di partenza. **Da
   decidere dal PM.**
6. **L'acqua fredda della tavola 2** resta a 120 mm dal bollitore: il confine sta al proprio
   minimo dal raccordo che lo regge, ed è la posa del gruppo a essere lontana. `place.py` è
   fuori perimetro.
7. **La tavola 4 non esce**, e non per il motivo che §D ipotizzava: `utenze` è posato a `x 365`
   dalla fase del tronco, cinque millimetri oltre l'area. Conto cella per cella in
   `docs/collaudi/DRAW-013/dopo/prova-4-perche-non-esce.txt`.
