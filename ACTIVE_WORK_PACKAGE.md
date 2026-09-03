# ACTIVE WORK PACKAGE — DRAW-003-R1

- **Release:** 0.2 — tavola 1 leggibile e approvabile
- **Stato:** REVISIONE RICHIESTA DAL PM SULLA PR #11
- **Data:** 2026-09-03
- **Assegnato a:** DEV team (Claude)
- **Ramo:** `claude/draw-003-terra-etichette`
- **PR:** `#11`, da aggiornare senza aprirne un'altra
- **Base:** integrare l'ultima `main` nel ramo esistente

## Correzione del PM

Questa revisione sostituisce le parti di DRAW-003 che rendevano bloccante la posa delle
etichette e ordinavano di usare il richiamo al primo conflitto. Erano specifiche errate.

Le etichette dei nodi sono un ausilio della modalità verifica: servono al PO per indicare
un elemento durante la revisione. Non governano il disegno e non compariranno nella
tavola definitiva.

## Gerarchia vincolante del prodotto

1. correttezza del grafo e delle connessioni;
2. geometria di macchine, accessori e tubazioni;
3. costo delle tubazioni: backtracking, curve, incroci/sormonti e lunghezza;
4. soltanto dopo che la geometria è congelata, annotazioni e testi.

Spostare macchine e accessori costa zero. Etichette e richiami hanno costo nullo rispetto
alla geometria e non possono far spostare, ruotare o reinstradare niente.

## Risultato richiesto in questa revisione

### 1. Linea di terra

Conservare la correzione già consegnata:

- nessuna linea o tratteggio continuo di terra nel PDF, PNG o SVG;
- la quota interna può allineare le macchine ma non è renderizzata e non è un ostacolo;
- l'eventuale segno di appoggio è corto e appartiene al singolo simbolo.

### 2. Indipendenza dei testi

Conservare e provare il contratto:

- posa e routing terminano prima dei testi;
- aggiungere, cambiare o togliere testi non modifica simboli, rotazioni o segmenti;
- etichette e richiami non entrano in metriche, candidati o funzione di costo del layout.

### 3. Semplificare le etichette

Ritirare l'algoritmo che ha prodotto 38 richiami su 52 testi e che degrada volontariamente
fino ad attraversare tubi, simboli e altri richiami.

- **Modalità verifica:** gli indirizzi dei nodi sono un overlay best-effort. Si scrivono
  vicino al nodo quando esiste una posizione semplice e leggibile; possono essere omessi
  quando non esiste. Nessun obbligo di mostrarli tutti, nessun groviglio di richiami,
  nessun errore bloccante per un indirizzo omesso o imperfetto.
- **Tavola definitiva:** nessun indirizzo della rete. Restano soltanto le etichette delle
  macchine principali, posate dopo il routing e senza influenzarlo.
- Un richiamo si usa soltanto quando chiarisce davvero il rapporto fra testo e macchina;
  non viene aggiunto automaticamente se produce più confusione del testo.
- L'impossibilità di collocare un'etichetta non blocca mai l'emissione della tavola.

Non costruire in questa revisione un ottimizzatore globale delle annotazioni: non è il
cuore del prodotto e non deve assorbire altro sviluppo della release 0.2.

## Perimetro

Restano ammessi i file di DRAW-003 necessari a semplificare o ritirare il codice già
introdotto, più:

- `docs/collaudi/DRAW-003/**`;
- `PROJECT_STATE.md`;
- `docs/input-pm/REGISTRO.md`, senza chiudere input del PO.

Fuori perimetro: modifiche al routing, al grafo, alle regole MEP, ai cataloghi e ai
simboli. I nuovi rilievi sul costo geometrico si registrano ma si implementano in
DRAW-004.

## Input PO da registrare per DRAW-004, senza implementarli qui

1. Le linee fra PDC e accumulo conservano curve evitabili. Il motore deve poter
   allontanare leggermente e riallineare inlet/outlet delle macchine principali quando
   ciò riduce curve, incroci e lunghezza complessiva.
2. Una T può usare due imbocchi ortogonali e assorbire una curva, eliminando un gomito.
   Questa posa deve entrare fra i candidati quando riduce il costo totale.
3. Etichette e richiami non partecipano mai al confronto fra due pose.

## Criteri di accettazione

1. Linea e tratteggio continui di terra assenti.
2. Simboli e rotte identici a DRAW-002: backtracking 0, tratte oltre tre pieghe 0,
   incroci non oltre 2, lunghezza non oltre 597,5 mm, valvole D-120 20/20.
3. Modifica, presenza o assenza delle etichette non cambia la geometria.
4. Nessun groviglio automatico di richiami: la modalità verifica privilegia indirizzi
   semplici e può omettere quelli non collocabili.
5. La tavola definitiva mostra soltanto le etichette delle macchine principali.
6. Nessun rilievo sulle etichette blocca PDF, PNG o SVG.
7. Suite completa, `ruff`, `mypy --strict` e determinismo verdi.
8. Artefatti aggiornati e rapporto corretto senza dichiarare le etichette prioritarie
   rispetto alla geometria.

Il DEV aggiorna la PR #11 e si ferma. Il merge spetta al PM.
