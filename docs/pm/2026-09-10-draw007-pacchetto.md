# ACTIVE WORK PACKAGE — DRAW-007

**Assegnato da:** PM-autore (Claude, in sessione col PO — `OPERATING_MODEL.md` §1.2.1)
**Assegnato a:** DEV
**Data:** 2026-09-10
**Release:** 0.3 — generalizzazione, revisione della tavola 2
**Stato:** APPROVATO DAL PO — 2026-09-10, con la primitiva del §A.1 scelta dal PO fra tre
**Ramo da riutilizzare:** `claude/draw-006-tavola2-semantica-v4n8o5`
**PR da aggiornare:** #24
**Commit di partenza:** `e415dc0`
**Fixture grafica principale:** impianto 2; impianto 1 come regressione automatica

---

## Contesto

`DRAW-006-R1` ha chiuso i quattro difetti semantici e ha **peggiorato la geometria**: la
rete ordinaria della tavola 2 è passata da 7 pieghe / 2 incroci / 670 mm a 12 / 8 / 785 mm,
la tavola 1 è uscita dalle proprie soglie, e tredici prove sono rimaste rosse. Il rapporto
di collaudo attribuiva il fatto a un ciclo greedy fermo in un ottimo locale. **Era una
diagnosi sbagliata**, ed è stata corretta dalla revisione incrociata del 10 settembre e dal
riscontro del PO:

> «Le tubazioni che vanno alle macchine principali sono l'autostrada, e su quelle i costi
> dovrebbero essere ancora maggiori. Oggi nel nostro router non abbiamo distinzione tra
> autostrada principale e strade secondarie: tutto è principale ma non è così.»

Il costo di posa è **piatto**: una piega sulla dorsale generatore–accumulo pesa quanto una
piega sullo stacco del manometro. Con quel criterio il ciclo respinge un allineamento che
costa tre pieghe di contorno, e lo fa **correttamente** — sta ottimizzando la cosa
sbagliata. La stessa causa spiega la prova rossa sulle zone non impilate, dove il ciclo
migliora il totale (11 pieghe contro 12, 437,5 mm contro 467,5) barattando la struttura
della tavola.

Input del PO collegati: **I-056**, **I-057**, **I-058**. Retrospettiva che li motiva:
`docs/retrospectives/2026-09-10-retro-draw006r1.md`.

**I-059 — lo spessore del tratto per gerarchia — è fuori da questo pacchetto** e sarà
`DRAW-008`: è rendering, dipende da questo ma non lo condiziona.

---

## A. La gerarchia è una grandezza del grafo

> **Nota del PM, 2026-09-10, seconda stesura.** La prima stesura diceva «quanta parte
> dell'impianto dipende da quella tratta». Il DEV l'ha prototipata prima di scrivere
> codice, sulle due tavole vere, e **la misura collassa**: su un circuito chiuso il
> cammino a valle rientra su sé stesso, quindi ogni tratta dell'anello raggiunge ogni
> utilizzatore. Ventuno tratte su ventidue prendono lo stesso peso sulla tavola 1,
> ventuno su ventitré sulla tavola 2. Non è una toppa mancante: è la primitiva sbagliata.
> Il PO ha scelto fra tre alternative quella qui sotto. Il prototipo e il suo esito
> restano nel rapporto di consegna.

1. La gerarchia di una tratta si **calcola** dal grafo, non si elenca, e nasce dal
   **tronco fra le macchine principali**:
   - **macchine di spina** — le macchine di rango più alto della rete: la macchina di
     generazione principale, ogni macchina che accumula o separa idraulicamente, ogni
     collettore o ripartitore. «Principale», dove ce n'è più d'una, è la più alta di
     mestiere, e a parità decide lo **spareggio strutturale** che già esiste
     (`model/order.py`), mai un identificativo;
   - **autostrada** — una tratta sta su un percorso fra **due** macchine di spina che non
     attraversa né un'altra macchina di spina né un utilizzatore. Su un circuito chiuso
     questo include **sia la mandata sia il ritorno**, che è precisamente ciò che il PO
     chiama «le due macro-linee parallele»;
   - **distribuzione** — il percorso porta a un utilizzatore;
   - **servizio** — non porta né all'una né all'altro: stacchi ciechi e accessori.
2. Si calcola **una volta sola** e ha **un solo posto**. In questo pacchetto la leggono
   due clienti — il costo di posa (§B) e l'obiettivo di allineamento (§C); un terzo
   arriverà con `DRAW-008`. Tre calcoli separati sono un pacchetto respinto.
3. I livelli sono tre, e sono quelli che il PO ha definito:
   - **autostrada** — il tronco che porta la portata piena: generatore ↔ accumulo,
     accumulo ↔ circolatore ↔ collettore;
   - **distribuzione** — ciò che si dirama portando una frazione: collettore → utenze,
     i generatori oltre il primo allineato, volume ACS → miscelatrice;
   - **servizio** — tubazioni accessorie e stacchi ciechi: l'AF dei ricarichi, l'uscita
     ACS, vaso, manometro, sicurezze.
4. La classificazione **non nomina nessun componente, nessun identificativo, nessun file,
   nessuna quantità di fixture**. Vale D-069 senza eccezioni.
5. **La portata di progetto non entra qui.** È il criterio idraulico più corretto e il PO
   lo sa, ma quel dato nel modello non esiste: nessun componente dichiara una portata.
   Aggiungerlo è un dato di prodotto, quindi catalogo, quindi fuori dal perimetro di
   questo pacchetto. Se la definizione del §A.1 ha un limite su una forma di impianto,
   **si dichiara nel rapporto**, non si nasconde in una costante.

## B. Il costo di posa pesa la gerarchia

1. Pieghe, incroci e lunghezza su una tratta di livello **autostrada** costano più che
   sulle stesse misure a livello distribuzione, che a loro volta costano più che a livello
   servizio.
2. Il peso è un dato dichiarato in un posto solo, leggibile, non sparso fra le funzioni di
   costo.
3. L'ordine lessicografico esistente di `SheetCost` **non si stravolge**: le violazioni
   restano prima di tutto, il backtracking resta prima delle pieghe. Cambia il **conto
   dentro ciascuna voce**, non l'ordine delle voci.

## C. L'allineamento è un obiettivo di fase, non una candidata

1. L'allineamento delle porte delle macchine di livello autostrada si **cerca prima**
   della rifinitura, non si mette in concorrenza a costo piatto dentro il ciclo greedy.
2. La mossa di allineamento deve poter muovere **una macchina con il proprio corredo**, e
   non soltanto una colonna intera: la granularità di colonna di oggi trascina pezzi che
   non c'entrano e fa pagare contorno estraneo. Questo è il primo sospettato per lo scarto
   della candidata PDC–puffer sulla tavola 2.
3. Prima di dichiarare irraggiungibile un allineamento, il DEV **stampa e riporta** le
   coppie che il generatore di candidate produce su quella tavola. Alzare i tetti di
   ricerca non serve: è già stato provato (1 500/2 000 → 6 000/6 000, esito identico).

## D. Le tredici prove rosse

1. Tornano verdi tutte. Ognuna è elencata nel rapporto con l'esito e la causa.
2. `tests/layout/test_catena_macchina.py` **non è geometria**: l'impianto di prova non
   dichiara nessuna rete di acqua fredda e il ponte del riempimento apre un punto aperto.
   È manutenzione ordinaria di prova, e la fa il DEV: dichiarare l'allaccio nella fixture,
   oppure restringere la guardia a «nessun punto aperto oltre quello, e quello per questa
   ragione». **Non si porta al PM.**
3. Nessuna prova diventa `skip` o `xfail`.

## E. Le soglie: cosa questo pacchetto ribattezza, e cosa no

Cambiando il conto del costo, **i totali diventano incomparabili**: 4 pieghe, 1 incrocio e
425 mm sono numeri di un costo piatto. Gating su quei numeri sarebbe misurare il vecchio
comportamento col nuovo motore. Il PM decide quindi così, ed è una decisione del PM, non
del DEV:

1. **Il cancello si sposta sulle proprietà strutturali** (§Criteri 4, 5, 6): allineamento,
   dorsali senza pieghe, rami paralleli impilati, zero backtracking, nessun tubo sotto un
   simbolo. Sono binarie e non dipendono da come si pesa il costo.
2. **I totali restano misurati e riportati**, e non peggiorano rispetto a `71b39db`.
3. **L'unico allentamento consentito** è convertire un'asserzione su un totale assoluto in
   un'asserzione di non-regressione contro i valori misurati a `71b39db`, elencando ogni
   conversione nel rapporto con il valore vecchio e quello nuovo. Qualunque altro
   allentamento è un pacchetto respinto.
4. **I bersagli dichiarati**, che il rapporto riporta come distanza residua e che **non
   sono cancelli**: tavola 1 rete ordinaria 4 / 1 / 425 mm e stacchi 0 / 0 / 45 mm;
   tavola 2 rete ordinaria non peggiore di 7 / 2 / 670 mm.

---

## Perimetro dei file — modifiche consentite esclusivamente a

- `src/disegnatore_mep/layout/**` (compreso il modulo nuovo della gerarchia)
- `src/disegnatore_mep/model/order.py`
- `tests/**`
- `docs/collaudi/DRAW-007/**`
- `PROJECT_STATE.md`

## Fuori perimetro — da non toccare

- **catalogo, regole, simboli, `naming/`**: questo pacchetto non cambia il contenuto del
  grafo. Se un difetto di contenuto emerge, si riporta e non si corregge qui;
- **spessori di linea e qualunque cosa di I-059**: è `DRAW-008`;
- riempimento estetico del foglio, cartiglio, sigla provvisoria `RM`, audit dei simboli;
- gli impianti 3–5 oltre la prova di posa: nessun loro PDF, PNG, SVG o rapporto;
- decisioni esistenti, registro degli input del PO, documenti di governance.

## Vincoli

- Nessun merge su `main`. **Il merge è del PO** (`OPERATING_MODEL.md` §1.2.1).
- Nessuna decisione esistente rinumerata, riscritta o cambiata di stato. Una decisione
  nuova si registra come **Proposta**.
- Nessun input del PO chiuso: al massimo se ne propone la chiusura.
- **Deviazione da D-123 dichiarata:** un pacchetto, un ramo, una PR. Qui `DRAW-007`
  riusa il ramo e la PR di `DRAW-006-R1`, perché quella consegna **non è fusa e non è
  mergeable** — tredici prove rosse — e questo pacchetto la porta a termine invece di
  affiancarle un secondo ramo. La PR #24 diventa la consegna di `DRAW-006-R1 + DRAW-007`.
  Il PO può disporre diversamente.

## Criteri di accettazione

Ogni criterio si chiude con **il comando eseguito e il suo output**, mai con la parola
«verificato». Un criterio che nomina un risultato osservabile si prova sul risultato
osservabile: «il motore genera la candidata» non chiude «le due macchine sono allineate».

- [ ] **1. La gerarchia è strutturale.** Una prova generale mostra che rinominando gli
      identificativi, invertendone l'ordinamento e mescolando le connessioni la
      classificazione delle tratte **non cambia**. Una seconda prova mostra che nel modulo
      che la calcola non compare nessun identificativo, nome di componente o nome di file
      di fixture.
- [ ] **2. I tre livelli rispettano l'ordine dichiarato.** Prova generale, su impianti
      costruiti dentro la prova: ogni tratta che unisce due macchine che portano la
      portata piena pesa **più** di ogni tratta che termina su un accessorio appeso; una
      tratta pesa **almeno quanto** ogni tratta che dipende da lei. Nessuna soglia
      numerica, nessun nome.
- [ ] **3. Il costo pesa la gerarchia, e si vede.** Prova **negativa** costruita dentro la
      prova: una posa in cui la stessa piega può stare sulla dorsale o su uno stacco. Con
      il costo di questo pacchetto il ciclo la mette sullo stacco; la stessa prova
      fallisce se i pesi sono resi uguali. La prova esibisce entrambi gli esiti.
- [ ] **4. Sulla tavola 2 le porte di mandata e ritorno della macchina principale e
      dell'accumulo principale stanno sullo stesso asse.** Osservabile sulla geometria
      composta, non sul generatore di candidate. Chiude I-056 dal lato del risultato.
- [ ] **5. Nessuna piega sulle tratte di livello autostrada**, sulla tavola 1 e sulla
      tavola 2. È l'espressione geometrica delle «due macro-linee parallele» di I-057. Se
      il DEV dimostra che su una forma specifica è irraggiungibile, **si ferma e riporta
      il caso**: non allarga il criterio.
- [ ] **6. `tests/layout/test_objective.py::test_parallel_branches_are_stacked_not_strung_out`
      è verde** senza che la prova sia stata toccata.
- [ ] **7. La suite è verde.** `python -m pytest -q` senza prove rosse. Nessuna prova
      convertita in `skip` o `xfail`. Le tredici rosse di `71b39db` elencate una per una
      nel rapporto con l'esito e la causa.
- [ ] **8. Le soglie ribattezzate sono soltanto quelle del §E.3**, ciascuna elencata nel
      rapporto con il valore vecchio, quello nuovo e la ragione. Nessun altro allentamento.
- [ ] **9. I totali non peggiorano** rispetto a `71b39db`: tavola 1 rete ordinaria
      11 / 1 / 487,5 mm e stacchi 6 / 0 / 125,0 mm; tavola 2 rete ordinaria
      12 / 8 / 785,0 mm e stacchi 6 / 4 / 125,0 mm. Il rapporto riporta anche la distanza
      residua dai bersagli del §E.4.
- [ ] **10. `ruff`, `mypy --strict` e doppia generazione deterministica** verdi, con
      l'impronta della geometria riportata.
- [ ] **11. Tutti e cinque gli impianti arrivano alla posa**, e nessun artefatto grafico è
      prodotto oltre quello della tavola 2.
- [ ] **12. Nessun file fuori dal perimetro risulta modificato nel diff.**

## Consegna attesa

- La PR #24 aggiornata, **non fusa**.
- Rapporto in `docs/collaudi/DRAW-007/RAPPORTO.md` con: ramo, SHA iniziale, SHA finale,
  file modificati, criteri uno per uno **col comando e l'output**, misure prima/dopo,
  difetti noti, punti aperti.
- Pacchetto grafico della **sola tavola 2**: PDF, PNG, SVG, geometria, metriche,
  preflight, e il confronto con `71b39db`.

## In caso di ambiguità o di criterio irraggiungibile

Fermarsi e riportarlo, **prima** di cambiare la prova. Un'incompatibilità si porta al PM;
la manutenzione ordinaria di una prova, no — quella la fa il DEV (§D.2).
