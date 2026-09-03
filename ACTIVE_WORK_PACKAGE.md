# ACTIVE WORK PACKAGE — DRAW-003

- **Release:** 0.2 — tavola 1 leggibile e approvabile
- **Stato:** ASSEGNATO DAL PM
- **Data:** 2026-09-03
- **Assegnato a:** DEV team (Claude)
- **Ramo:** `claude/draw-003-terra-etichette`
- **Base:** ultima `main`

## Risultato richiesto

Rigenerare la sola tavola 1 eliminando definitivamente la linea continua di terra e
rendendo verificabile l'ordine della pipeline grafica:

1. posa dei componenti;
2. instradamento completo delle tubazioni;
3. posa delle etichette, senza più modificare componenti o tubazioni;
4. se il posto preferito di un'etichetta collide, si sposta soltanto l'etichetta e si
   usa un richiamo obliquo.

Il grafo, i componenti, le rotte e le metriche di DRAW-002 restano invariati, salvo una
variazione che il DEV dimostri essere indispensabile per correggere un difetto reale.

## Diagnosi del PM

### Linea di terra

`D-121` è implementata soltanto a metà. Il routing e le etichette possono attraversare
la quota interna, ma la tavola continua a esportare `ground_line_y_mm` e il renderer
disegna una linea orizzontale continua con tratteggio. La tavola DRAW-002 mostra ancora
quel segno, nonostante D-121 stabilisca che nella centrale non deve esistere una linea di
terra che attraversa il foglio.

La quota interna può restare un riferimento di allineamento per le macchine appoggiate;
non deve diventare una primitiva grafica continua. Un eventuale segno di appoggio è parte
del singolo simbolo e resta corto sotto la sola macchina.

### Etichette

La pipeline corrente esegue già `settle_sheet` prima di `place_labels`: le tubazioni non
ricevono formalmente le etichette come ostacoli. Questo ordine deve diventare un contratto
provato, perché il risultato visivo dà al PO la sensazione opposta.

Il posizionatore attuale cerca numerose posizioni adiacenti senza richiamo prima di usare
la soluzione con leader. Il comportamento richiesto è più netto:

- per ogni testo esiste una posizione preferita adiacente al proprio componente;
- se quella posizione è libera, il testo resta lì senza richiamo;
- se collide con tubo, simbolo, altra etichetta o margine, **non si muove nulla di ciò che
  è già disegnato**: si cerca deterministicamente una posizione libera per il solo testo
  e si collega con un richiamo rettilineo obliquo;
- i richiami non sono tubazioni: mai ortogonali, a 45°, senza incrociarsi
  fra loro quando esiste un'alternativa libera equivalente;
- le etichette degli indirizzi della modalità verifica seguono lo stesso ordine postumo
  e non alterano la geometria che sarà consegnata senza indirizzi.

Questa specifica attua D-075, D-110, D-111 e D-121; il DEV non deve ricavarne altri
requisiti dall'immagine annotata del PO.

## Modifiche funzionali obbligatorie

### 1. Ritirare il terreno dalla tavola

- Non emettere nel PDF/SVG alcuna linea continua di terra, tratteggio o gruppo grafico
  equivalente.
- Non usare la quota di terra come ostacolo per routing, testi o centratura.
- Conservare, se necessario, una quota interna di posa per allineare le macchine, senza
  renderla e senza esportarla come elemento visibile della tavola.
- Cercare e correggere tutti i percorsi di rendering che possono reintrodurre il segno,
  non soltanto il caso dell'impianto 1.

### 2. Rendere le etichette una fase terminale indipendente

- Componenti e rotte devono essere definitivi prima della posa dei testi.
- Modificare contenuto, lunghezza, presenza o modalità delle etichette non deve cambiare
  coordinate e rotazioni dei simboli né punti e segmenti delle rotte.
- Nessuna metrica o funzione di costo del layout può includere gli ingombri delle
  etichette.

### 3. Risolvere i conflitti muovendo il testo

- Tentare una posizione preferita coerente col ruolo del testo.
- Al primo conflitto della posizione preferita, attivare la posa con richiamo; non
  peregrinare fra lati e distanze senza dichiarare graficamente il legame.
- La posizione richiamata deve evitare testi, simboli, tubazioni e limiti del foglio.
- Il richiamo deve identificare senza ambiguità il componente, essere obliquo e non
  sovrapporsi a una tubazione.

## Perimetro

- `src/disegnatore_mep/layout/compose.py`
- `src/disegnatore_mep/layout/composition.py`, solo se serve a separare quota interna e
  segno grafico
- `src/disegnatore_mep/layout/labels.py`
- `src/disegnatore_mep/layout/geometry.py`, solo se serve a ritirare il dato grafico
- `src/disegnatore_mep/graphics/sheet.py`
- `src/disegnatore_mep/validation/**`
- test grafici, layout, validazione e accettazione pertinenti
- `docs/collaudi/DRAW-003/**`
- `PROJECT_STATE.md`
- `docs/input-pm/REGISTRO.md`, senza chiudere input del PO

Fuori perimetro: grafo, interprete, completatore, assemblatore, cataloghi, simboli,
regole MEP, cartiglio, impianti 2–5 e modifiche al costo-peso di DRAW-002.

## Prove richieste prima del codice applicativo

1. Un test sul rendering fallisce se l'SVG contiene il gruppo, la linea o il tratteggio
   continuo del terreno.
2. La stessa geometria prodotta con indirizzi di verifica presenti e assenti ha simboli
   e rotte identici.
3. Cambiare una sigla con un testo molto più lungo non cambia simboli o rotte.
4. Un'etichetta con posizione preferita libera resta adiacente e senza richiamo.
5. Un'etichetta la cui posizione preferita interseca una tubazione viene spostata con
   richiamo obliquo; la tubazione resta bit-identica.
6. Due etichette in conflitto vengono risolte spostando quella posata dopo con richiamo,
   senza sovrapposizione finale.
7. Due generazioni consecutive producono lo stesso output.

## Criteri di accettazione DEV

1. Nessuna linea o tratteggio continuo di terra nel PDF, PNG e SVG della tavola 1.
2. Nessuna regressione sulle metriche di DRAW-002: backtracking 0, tratte oltre tre
   pieghe 0, incroci non oltre 2, lunghezza non superiore a 597,5 mm, valvole D-120
   20/20.
3. Simboli e rotte della tavola 1 coincidono con DRAW-002, salvo differenze motivate e
   approvate dal PM prima dell'implementazione.
4. Nessuna collisione finale etichetta/etichetta, etichetta/simbolo o etichetta/tubo.
5. Ogni etichetta spostata dalla posizione preferita porta un richiamo obliquo leggibile.
6. Modalità verifica e consegna differiscono soltanto per il velo delle etichette di
   indirizzo, mai per posa o routing.
7. Suite completa, `ruff` e `mypy --strict` verdi; output deterministico.
8. Consegna di PDF, PNG e SVG aggiornati, confronto con DRAW-002 e rapporto criterio per
   criterio.

## Collaudo del PM

Il PM controllerà il codice e la geometria, ma approverà il pacchetto soltanto guardando
il PDF e il raster a misura di stampa. Prima di consegnare al PO dovranno essere visibili:

- assenza completa della linea di terra continua;
- tubazioni geometricamente identiche a DRAW-002 e indipendenti dai testi;
- testi vicini quando liberi e richiamati quando spostati;
- richiami chiaramente distinguibili dalle tubazioni.

Il DEV apre la PR e si ferma. Il merge spetta al PM.
