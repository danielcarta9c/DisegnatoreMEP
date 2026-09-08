# ACTIVE WORK PACKAGE — DRAW-005-R1

- **Release:** 0.2A — rifinitura della tavola 1
- **Stato:** APPROVATO DAL PM, PRONTO PER IL DEV
- **Data:** 2026-09-08
- **Base:** ultima `main`, contenente la chiusura PM di DRAW-005
- **Ramo:** `claude/draw-005-r1-rifiniture-tavola1`
- **Campo:** solo impianto 1 e contratti generali necessari

## Obiettivo

Attuare gli input PO I-041…I-046 secondo la traduzione già svolta dal PM in
`docs/pm/2026-09-08-rilievi-po-draw005-r1.md`. Non interpretare gli allegati e non fare
ricerca di dominio: le decisioni da implementare sono qui sotto.

## A. Sicurezza e sfiato

1. Non dedurre il numero delle sicurezze dal numero dei generatori.
2. Modellare il dominio di protezione: una sicurezza comune soddisfa più macchine solo
   quando resta comunicante col volume da proteggere nelle configurazioni ammesse.
3. La presenza a bordo è un dato esplicito tri-stato del catalogo: presente, assente,
   ignoto. Un campo mancante significa **ignoto**, non assente, e non autorizza ad
   aggiungere dispositivi.
4. Sulla tavola 1 eliminare la sicurezza sull'accumulo e le due sicurezze per-PDC della
   PR #21. Posare **una sola sicurezza di circuito** sulla mandata, vicino al gruppo PDC;
   questa è la sicurezza di DRAW-005 riposizionata, non un nuovo dispositivo.
5. Protezioni ulteriori compaiono solo con un dato di catalogo o con domini autonomi
   esplicitamente modellati; in caso indeterminato il motore genera una domanda aperta.
6. Non confondere lo sfogo aria con la sicurezza: conservare un solo sfogo sull'attacco
   alto dell'accumulo.

Scrivere prima prove generali su dominio unico e domini isolabili, con presenza a bordo
presente, assente e ignota.

## B. Medium, colore e frecce dei rami di servizio

Introdurre una semantica generale che distingua flusso ordinario, ramo statico ed
eventuale scarico:

- il tratto lato impianto del riempimento è ritorno tecnico blu e la freccia punta dal
  gruppo verso il circuito;
- un eventuale tratto a monte del riempimento, se esplicitamente modellato, è adduzione
  idrica;
- gli stacchi di manometro e vaso sono dello stesso medium/colore del ritorno tecnico e
  non hanno frecce;
- sfiato e sicurezza su uno stacco non mostrano una freccia di circolazione; un'eventuale
  tubazione di scarico esplicita potrà invece avere verso uscente;
- il componente `P` della tavola 1 resta un manometro: non rinominarlo pressostato.

La scelta non deve dipendere dall'orientamento geometrico, dall'ID o dal colore scritto a
mano nel renderer.

## C. Simboli

1. **Filtro a Y:** aggiungere le due barrette terminali perpendicolari all'asse passante.
2. Aggiungere al manifesto una proprietà generale di peso del tratto (`thin`, `medium`,
   `thick`) o soluzione equivalente validata; il filtro usa `thick` = 0,50 mm in tavola,
   legenda e foglio simboli. Vietate eccezioni per `symbol_id` nel renderer.
3. **Accumulo combinato:** sostituire il serpentino rettangolare con una serpentina
   continua, morbida e centrata. Porte, riquadro, attacchi e grafo restano invariati.
4. Aggiornare sempre `examples/graphics/build_symbols.py`; nessuna modifica manuale ai
   soli SVG generati.

## D. Posa locale degli accessori PDC

Per una catena appartenente alla macchina, la posa locale deve essere congruente sotto
traslazione e rotazione:

- ordine sul ritorno: porta PDC → filtro a Y → valvola → rete;
- filtro e valvola sul primo segmento rettilineo utile dalla porta, prima della prima
  curva;
- due PDC identiche con la stessa catena hanno le stesse distanze locali fra porta,
  filtro e valvola, anche se una catena ruota;
- nessuna coordinata o eccezione per gli ID della tavola 1.

Il costo globale resta il criterio fra pose che rispettano questo contratto duro.

## E. Stacchi minimi e spostamento gratuito delle macchine

1. La lunghezza degli stacchi di sicurezza, sfiato, misura, espansione e riempimento è
   la minima lunghezza su griglia che evita il contatto fra tubo e ingombro del simbolo
   e conserva la leggibilità di stampa; non è una costante arbitraria.
2. Ogni millimetro oltre il minimo peggiora il costo.
3. Prima di introdurre curve, deviazioni o corridoi, il posatore prova la traslazione
   verticale delle PDC e dei gruppi collegati a passi di griglia.
4. L'interasse verticale delle PDC cresce quanto basta per non sovrapporre le catene
   locali e rendere più rettilinee le dorsali: spostare le macchine costa zero.
5. I corridoi davanti alle porte sono locali e non possono impedire la posa degli altri
   impianti o deformare la composizione globale.

## Criteri di accettazione

1. Tutti gli input I-041…I-046 sono visibili nel PDF e provati con test generali.
2. Una sola sicurezza di circuito sulla mandata vicino al gruppo PDC; zero sicurezza
   sull'accumulo e zero duplicazioni automatiche per macchina.
3. Riempimento diretto verso l'impianto; riempimento, vaso e manometro correttamente blu
   sul lato ritorno; zero frecce su vaso e manometro.
4. Filtro a Y leggibile con barrette e tratto 0,50 mm in tavola, legenda e riscontro.
5. Le due catene di ritorno PDC hanno ordine e distanze locali congruenti e stanno prima
   della prima curva.
6. Serpentino continuo e graficamente morbido; nessuna variazione delle porte.
7. Zero tubo sotto simboli, zero backtracking, zero tratte oltre tre curve; curve,
   incroci e lunghezza riportati sul nuovo grafo senza confronto improprio.
8. Nessuna nuova `xfail`; suite completa, ruff, mypy strict e determinismo verdi.
9. PDF, PNG, SVG, geometria, metriche, preflight e confronto contro DRAW-005 in
   `docs/collaudi/DRAW-005-R1/`.
10. Le PDC possono aumentare il proprio interasse verticale; nessuno stacco è più lungo
    del minimo valido. La rete a flusso ordinario non supera DRAW-005: massimo 4 curve,
    1 incrocio e 525 mm, misurati separatamente dagli stacchi statici.
11. Tutti e cinque gli impianti arrivano almeno alla posa come sulla base `cc7ff93`;
    nessuna regressione viene convertita in `skip` o `xfail`.

## Fuori perimetro

- impianti 2–5 e regressione dell'impianto 3;
- dipendenza della geometria dall'ordine delle connessioni;
- packaging e vertical slice della skill;
- audit dei simboli non coinvolti;
- cartiglio, riempimento del foglio, etichette e funzione di costo globale.

## Consegna

Apri una PR dal ramo indicato verso `main` e fermati senza merge. Il PM verifica codice,
fonti applicate e PDF; il PO giudica la tavola.
