# Rilievi della tavola — Prova del PO 1 — proposta del PO: la via dritta della deviatrice al pavimento, la terza all'ACS

Formato **A3** · tratte **24** · tratte cedute **0** · rilievi bloccanti **0**.

Li misurano i controlli della skill sulla tavola finita: il preflight di qualita' e le regole del piano. Non sono un giudizio sull'impianto: dicono come e' disegnato.

## Bloccanti — la tavola non si consegna

- nessuno

## Da approvare — il progettista decide

- nessuno

## Avvisi — la tavola si consegna, e si sa

- la tavola t1: il disegno arriva a 0.0 mm dal bordo dell'area, e con il suo ingombro poteva starne 10.0: un disegno comodo non si disegna dal bordo a bordo (D-143) (`DRAWING_TOUCHES_THE_BORDER` · t1)

## Le regole del piano

- la tavola t1: lo stacco che porta acquedotto da tee-drain-connection-cold-bollitore-cold-in e' lungo 30.0 mm e il suo minimo su griglia e' 20.0, che e' quanto pretendono gli accessori in linea (valve-isolation-dhw-acquedotto-a), cioe' 10.0 mm di tubo in piu': un organo di servizio sta addosso al pezzo che serve (A4, D-145) (`SERVICE_STUB_LONGER_THAN_ITS_MINIMUM` · t1, acquedotto, tee-drain-connection-cold-bollitore-cold-in)
- la tavola t1: le tratte p6-a, p6-b + p4-a, p4-b piegano 4 volte, e i simboli che toccano ne impongono 2: 2 di troppo — la catena e' volano -> ritorno -> bollitore (B1, D-154, D-171) (`HIGHWAY_IS_NOT_STRAIGHT` · t1, p4-a, p4-b, p6-a, p6-b)
- la tavola t1: le tratte p7-a-1-a, p7-a-1-b + p7-a-2 + p7-a-3 + p7-a-4, p7-a-5-a, p7-a-5-b, p7-a-6 piegano 2 volte, e i simboli che toccano ne impongono 0: 2 di troppo — la catena e' volano -> tee-pressure-gauge-pdc-water-return -> tee-filling-unit-pdc-water-return-b -> tee-expansion-connection-pdc-water-return -> pdc (B1, D-154, D-171) (`HIGHWAY_IS_NOT_STRAIGHT` · t1, p7-a-1-a, p7-a-1-b, p7-a-2, p7-a-3, p7-a-4, p7-a-5-a, p7-a-5-b, p7-a-6)
- la tavola t1: la tratta p5-a, p5-b piega 2 volte, e i simboli che tocca ne impongono 0: 2 di troppo — la catena e' pavimento -> ritorno (B1, D-154, D-171) (`HIGHWAY_IS_NOT_STRAIGHT` · t1, p5-a, p5-b)

## Il cartiglio

- campi da definire: INDIRIZZO, TITOLO TAVOLA, TAVOLA — nella casella c'e' «DA DEFINIRE» e la tavola esce in bozza (D-025)
