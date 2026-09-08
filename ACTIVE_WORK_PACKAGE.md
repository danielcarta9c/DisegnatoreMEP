# ACTIVE WORK PACKAGE — DRAW-005-R1

- **Release:** 0.2A — rifinitura della tavola 1
- **Stato:** APPROVATO DAL PM, PRONTO PER IL DEV
- **Data:** 2026-09-08
- **Base:** ultima `main`, contenente la chiusura PM di DRAW-005
- **Ramo:** `claude/draw-005-r1-rifiniture-tavola1`
- **Campo:** solo impianto 1 e contratti generali necessari

## Obiettivo

Attuare gli input PO I-041…I-045 secondo la traduzione già svolta dal PM in
`docs/pm/2026-09-08-rilievi-po-draw005-r1.md`. Non interpretare gli allegati e non fare
ricerca di dominio: le decisioni da implementare sono qui sotto.

## A. Sicurezza e sfiato

1. Eliminare l'assunzione che ogni PDC generica porti la sicurezza a bordo.
2. La presenza a bordo è un dato esplicito del catalogo della macchina.
3. Per ogni generatore che non dichiara una sicurezza integrata, posare una sicurezza
   esterna sulla mandata, il più vicino possibile alla macchina e prima di qualunque
   organo di intercettazione.
4. Se la sicurezza è dichiarata a bordo, non aggiungere il doppione esterno.
5. Sulla tavola 1, il catalogo generico dichiara solo il circolatore: servono quindi due
   sicurezze esterne, una per ciascuna PDC isolabile. La sicurezza oggi vicina
   all'accumulo non sostituisce quelle dei generatori.
6. Non confondere lo sfogo aria con la sicurezza: conservare lo sfogo sull'attacco alto
   dell'accumulo e non aggiungerne uno per PDC senza dato di catalogo o regola.

Scrivere prima prove generali su una e due macchine, con e senza sicurezza integrata.

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

## Criteri di accettazione

1. Tutti gli input I-041…I-045 sono visibili nel PDF e provati con test generali.
2. Due sicurezze esterne proteggono le due PDC della tavola 1 prima delle rispettive
   intercettazioni; zero sicurezza esterna duplicata quando il catalogo la dichiara a
   bordo.
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

## Fuori perimetro

- impianti 2–5 e regressione dell'impianto 3;
- dipendenza della geometria dall'ordine delle connessioni;
- packaging e vertical slice della skill;
- audit dei simboli non coinvolti;
- cartiglio, riempimento del foglio, etichette e funzione di costo globale.

## Consegna

Apri una PR dal ramo indicato verso `main` e fermati senza merge. Il PM verifica codice,
fonti applicate e PDF; il PO giudica la tavola.
