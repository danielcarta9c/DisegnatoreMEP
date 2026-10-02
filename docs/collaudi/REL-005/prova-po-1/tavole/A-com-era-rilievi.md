# Rilievi della tavola — Prova del PO 1 — come l'ha letta la skill: la via dritta della deviatrice all'ACS

Formato **A3** · tratte **24** · tratte cedute **0** · rilievi bloccanti **0**.

Li misurano i controlli della skill sulla tavola finita: il preflight di qualita' e le regole del piano. Non sono un giudizio sull'impianto: dicono come e' disegnato.

## Bloccanti — la tavola non si consegna

- nessuno

## Da approvare — il progettista decide

- nessuno

## Avvisi — la tavola si consegna, e si sa

- la tavola t1: il foglio e' pieno al 85%, sopra il 65% di D-140, e li' lo spazio per le sigle si stringe davvero. Resta una **misura** e non un difetto da chiudere (D-149): la posa non insegue piu' questo numero (`SHEET_TOO_FULL` · t1)
- la tavola t1: il disegno arriva a 5.0 mm dal bordo dell'area, e con il suo ingombro poteva starne 10.0: un disegno comodo non si disegna dal bordo a bordo (D-143) (`DRAWING_TOUCHES_THE_BORDER` · t1)

## Le regole del piano

- la tavola t1: le tratte p2-a, p2-b + p1-b-a, p1-b-b + p1-a piegano 2 volte, e i simboli che toccano ne impongono 0: 2 di troppo — la catena e' bollitore -> deviatrice -> tee-valve-safety-pdc-water-supply -> pdc (B1, D-154, D-171) (`HIGHWAY_IS_NOT_STRAIGHT` · t1, p1-a, p1-b-a, p1-b-b, p2-a, p2-b)
- la tavola t1: la tratta p5-a, p5-b piega 2 volte, e i simboli che tocca ne impongono 0: 2 di troppo — la catena e' pavimento -> ritorno (B1, D-154, D-171) (`HIGHWAY_IS_NOT_STRAIGHT` · t1, p5-a, p5-b)

## Il cartiglio

- campi da definire: INDIRIZZO, TITOLO TAVOLA, TAVOLA — nella casella c'e' «DA DEFINIRE» e la tavola esce in bozza (D-025)
