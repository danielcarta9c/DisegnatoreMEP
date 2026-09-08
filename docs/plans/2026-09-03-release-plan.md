# Piano di release — Disegnatore MEP

**Stato:** piano operativo del PM, 2026-09-03.

## 0.2 — Prima tavola approvata

Obiettivo: portare l'impianto 1 a una tavola **impiantisticamente corretta secondo il
grafo approvato dal PO**, deterministica e graficamente approvata dal PM/PO.

- `DRAW-002`: motore di posa costo-peso e routing compatto;
- `DRAW-003`: rimozione definitiva della linea continua di terra e fase terminale delle
  etichette, indipendente da posa e routing;
- `DRAW-004`: candidati di allineamento fra porte, dorsali principali rettilinee e T che
  può assorbire una curva, sempre scelti dal costo globale e mai come regole assolute;
- `DRAW-005`: correttezza del grafo dell'impianto 1 e simboli/porte che influenzano la
  posa; etichette di nodo opzionali, sigle principali sempre presenti;
- `DRAW-005-R1`: rifiniture PO su flussi dei rami di servizio, sicurezza dei generatori,
  coerenza locale degli accessori e leggibilità dei simboli;
- uscita: PDF, PNG, SVG e metriche riproducibili della tavola 1.

Gate: il PO riconosce un disegno ordinato e tecnicamente leggibile. Finché questo gate
non passa, non si estende il lavoro agli altri impianti.

### 0.2B — Vertical slice nella chat di lavoro

Prima della generalizzazione, installare la skill in un ambiente pulito e collaudare un
percorso reale: input naturale → grafo e domande → approvazione PO → generazione
deterministica → verifica → link al PDF. Questo gate anticipa il rischio d'integrazione
oggi rimandato impropriamente alla 1.0.

## 0.3 — Generalizzazione

Applicare senza coordinate speciali lo stesso motore agli impianti 2–5, uno per volta.
Ogni nuovo impianto deve scoprire una classe di difetto nuova; non si ripetono quattro
cicli sullo stesso errore.

Gate: cinque impianti deterministici, senza regressioni sulla tavola 1 e senza eccezioni
legate agli identificativi degli esempi.

## 0.4 — Tavola professionale completa

Completare ciò che non altera la geometria critica già collaudata: simboli secondari,
spessori normati,
cartiglio Nove C, legenda, testi e gestione motivata del formato/paginazione.

Gate: tavola stampabile e utilizzabile come elaborato tecnico, non soltanto come prova
del motore.

## 0.5 — Drawing Director

Introdurre il supervisore AI soltanto dopo la stabilizzazione delle metriche
deterministiche. Il Director osserva il raster, propone correzioni attraverso parametri
e candidati ammessi e richiede una nuova generazione; non modifica direttamente la
tavola e non altera il grafo.

Gate: miglioramento misurabile su casi non usati per costruire le regole, mantenendo
riproducibilità e tracciabilità delle correzioni.

## 1.0 — Release utilizzabile

Pipeline completa dal modello approvato alla tavola verificata, documentazione di
installazione, pacchetto versionato e collaudo sui casi di accettazione.

Il PM aggiorna `ACTIVE_WORK_PACKAGE.md` dopo ogni merge. Il DEV esegue soltanto il
pacchetto attivo; il PO interviene sui requisiti e sul giudizio del risultato.
