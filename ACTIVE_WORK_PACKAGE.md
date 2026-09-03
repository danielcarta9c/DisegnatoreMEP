# ACTIVE WORK PACKAGE — DRAW-002-R3

- **Release:** 0.2 — tavola 1 leggibile e approvabile
- **Stato:** ASSEGNATO DAL PM
- **Data:** 2026-09-03
- **Assegnato a:** DEV team (Claude)
- **Ramo:** `claude/draw-002-routing-qualita`
**Base:** ultima `main`; se il ramo esiste già, integrare `main` prima di lavorare.

## Risultato richiesto

Rigenerare la tavola 1 con una disposizione compatta governata dal costo delle
tubazioni. PDC, accumulo e terminale non devono occupare fasce equidistanti: le
macchine si spostano gratuitamente; costano backtracking, curve, incroci e lunghezza.

Il grafo idraulico e i componenti restano invariati. Il lavoro riguarda esclusivamente
la trasformazione dal grafo già approvato alla geometria della tavola.

## Diagnosi del PM sull'architettura attuale

La pipeline vigente è:

`place_sheet` → `improve_sheet` → `settle_sheet` → validazione/rendering.

Il difetto nasce principalmente in `src/disegnatore_mep/layout/improve.py`:

- `_spread_out()` riallontana i componenti per inseguire il 60% di riempimento e
  ammette un aumento della lunghezza;
- i candidati sono quasi tutti piccoli spostamenti di un solo simbolo;
- una colonna o una pila non può traslare orizzontalmente come gruppo;
- il confronto mescola pesi numerici e vincoli, quindi il riempimento può conservare
  spazio vuoto che il costo-peso dovrebbe eliminare.

`place.py` deve produrre soltanto una posa iniziale valida e ordinata per processo.
`improve.py` deve decidere la posa finale reinstradando l'intera tavola.
`route.py` resta l'instradatore ortogonale per singola tratta e si modifica solo se,
dopo la nuova posa, continua a scegliere un percorso contrario alla funzione di costo.

## Modifiche funzionali obbligatorie

### 1. Un solo confronto esplicito della tavola

Introdurre un valore confrontabile della geometria completa, con precedenza
lessicografica:

1. violazioni bloccanti e tratte che non ospitano i propri accessori;
2. numero di tratte con backtracking;
3. millimetri complessivi di backtracking;
4. numero di tratte oltre tre pieghe;
5. numero totale di pieghe;
6. numero di incroci;
7. lunghezza complessiva delle tubazioni;
8. riempimento e bilanciamento, soltanto come spareggio fra geometrie uguali sulle
   sette voci precedenti.

Non sono ammessi pesi che permettano a una voce successiva di compensarne una
precedente. Il movimento dei simboli non entra nel costo.

### 2. Eliminare la distensione come obiettivo autonomo

Rimuovere o neutralizzare il comportamento con cui `_spread_out()` compra riempimento
allungando le tubazioni. Per la release 0.2 non esiste un obiettivo minimo di
riempimento: `fill`, `coverage`, `spread` e `imbalance` restano metriche diagnostiche o
spareggi, mai ragioni per aumentare tubo, curve, incroci o backtracking.

### 3. Generare pose dalla topologia, non da distanze prefissate

Il miglioratore deve poter provare deterministicamente almeno:

- allineamento delle porte di due macchine collegate;
- avvicinamento alla distanza minima che lascia spazio agli accessori in linea e ai
  franchi grafici;
- traslazione coordinata di pile e colonne, senza sfilarne un solo elemento;
- avvicinamento di un gruppo funzionale al gruppo successivo;
- rotazioni consentite dal manifesto per rivolgere le porte verso il collegamento;
- spostamenti ricavati dalle coordinate delle porte e dei vicini collegati, quindi
  anche maggiori dei vecchi `NUDGE_STEPS`.

Il DEV sceglie liberamente l'algoritmo reversibile — greedy, beam search o altro — ma
deve produrre questi comportamenti, restare deterministico e rispettare un limite di
ricerca dichiarato.

### 4. Misurare sempre ciò che viene realmente disegnato

Ogni candidato viene valutato dopo `settle_sheet`, con accessori in linea e tutte le
tratte reinstradate. Non sono valide approssimazioni su geometrie parziali.

## Perimetro

- `src/disegnatore_mep/layout/**`
- `src/disegnatore_mep/validation/**`
- `tests/layout/**`
- `tests/validation/**`
- `tests/acceptance/test_drawing.py`
- `scripts/tavole-di-verifica.sh`, solo per riproducibilità
- `docs/collaudi/DRAW-002/**`
- `PROJECT_STATE.md`
- `docs/input-pm/REGISTRO.md`, senza chiudere input del PO

Fuori perimetro: interprete, grafo, assemblatore, regole MEP, cataloghi, simboli,
cartiglio, impianti 2–5, Drawing Director AI e modifiche manuali della tavola.

## Prove richieste prima del codice applicativo

I test generali devono dimostrare che:

- una posa compatta batte una posa equidistante quando riduce il costo;
- nessun aumento di riempimento può comprare tubo, pieghe, incroci o backtracking;
- una pila collegata può traslare come gruppo;
- i candidati raggiungono direttamente un allineamento fra porte anche quando dista
  più di quattro passi di griglia;
- due ingressi topologicamente equivalenti, con identificativi diversi, producono la
  stessa geometria;
- due generazioni consecutive producono lo stesso fingerprint.

È vietato codificare coordinate o identificativi dell'impianto 1 nella logica.

## Criteri di accettazione DEV

1. Backtracking: zero tratte e zero millimetri.
2. Tutte le valvole D-120 sono a 2,5–5 mm dall'attacco che isolano.
3. Nessuna tratta supera tre pieghe.
4. Incroci inferiori ai 12 di DRAW-001; obiettivo non superiore a 5.
5. Lunghezza totale inferiore ai 1177,5 mm di DRAW-001.
6. Nessuna tubazione attraversa o corre sotto un simbolo e nessuna sovrapposizione
   longitudinale fra tubi.
7. Terminale e accumulo risultano adiacenti quanto consentito da accessori e franchi;
   nessuna distanza è introdotta per riempire il foglio.
8. Grafo canonico invariato; nessuna coordinata specifica dell'impianto 1 nel motore.
9. Suite completa, `ruff` e `mypy --strict` verdi.
10. PDF, PNG e SVG della tavola 1, confronto raster e tabella delle metriche prima/dopo.

Se l'obiettivo di cinque incroci non è raggiungibile senza peggiorare una voce
precedente, consegnare la migliore frontiera misurata. Non alterare l'ordine del costo.

## Collaudo del PM

I PDF forniti dal PO in `docs/input-pm/riferimenti-grafici/2026-09-03/` sono materiale
di giudizio del PM. Il DEV non deve dedurre requisiti da quei disegni e non deve
produrre una relazione interpretativa su di essi.

Il PM confronterà il raster finale con i riferimenti per verificare, in particolare:

- leggibilità immediata dei percorsi di mandata e ritorno;
- vicinanza delle macchine secondo le connessioni;
- assenza di spazi vuoti comprati con tubazioni;
- assenza di flussi che avanzano e poi tornano indietro;
- ordine complessivo confrontabile con una tavola professionale.

Il superamento dei test abilita la consegna; l'approvazione grafica e il merge spettano
al PM.
