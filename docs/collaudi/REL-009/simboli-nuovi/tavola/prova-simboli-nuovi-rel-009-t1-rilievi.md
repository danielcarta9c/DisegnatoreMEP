# Rilievi della tavola — REL-009 - i simboli nuovi del primo caso reale

Formato **A3** · tratte **22** · tratte cedute **0** · rilievi bloccanti **0**.

Li misurano i controlli della skill sulla tavola finita: il preflight di qualita' e le regole del piano. Non sono un giudizio sull'impianto: dicono come e' disegnato.

## Bloccanti — la tavola non si consegna

- nessuno

## Da approvare — il progettista decide

- nessuno

## Avvisi — la tavola si consegna, e si sa

- la tavola t1: il disegno arriva a 5.0 mm dal bordo dell'area, e con il suo ingombro poteva starne 10.0: un disegno comodo non si disegna dal bordo a bordo (D-143) (`DRAWING_TOUCHES_THE_BORDER` · t1)

## Le regole del piano

- la tavola t1: lo stacco che porta da-esistente da tj-sec e' lungo 27.5 mm e il suo minimo su griglia e' 20.0, che e' quanto pretendono gli accessori in linea (valve-isolation-da-esistente-a), cioe' 7.5 mm di tubo in piu': un organo di servizio sta addosso al pezzo che serve (A4, D-145) (`SERVICE_STUB_LONGER_THAN_ITS_MINIMUM` · t1, da-esistente, tj-sec)
- la tavola t1: lo stacco che porta solare-mandata da volano e' lungo 35.0 mm e il suo minimo su griglia e' 20.0, che e' quanto pretendono gli accessori in linea (valve-isolation-solare-mandata-a), cioe' 15.0 mm di tubo in piu': un organo di servizio sta addosso al pezzo che serve (A4, D-145) (`SERVICE_STUB_LONGER_THAN_ITS_MINIMUM` · t1, solare-mandata, volano)
- la tavola t1: lo stacco che porta solare-ritorno da volano e' lungo 35.0 mm e il suo minimo su griglia e' 20.0, che e' quanto pretendono gli accessori in linea (valve-isolation-solare-ritorno-a), cioe' 15.0 mm di tubo in piu': un organo di servizio sta addosso al pezzo che serve (A4, D-145) (`SERVICE_STUB_LONGER_THAN_ITS_MINIMUM` · t1, solare-ritorno, volano)
- la tavola t1: lo stacco che porta verso-esistente da ts-sec e' lungo 22.5 mm e il suo minimo su griglia e' 20.0, che e' quanto pretendono gli accessori in linea (valve-isolation-verso-esistente-a), cioe' 2.5 mm di tubo in piu': un organo di servizio sta addosso al pezzo che serve (A4, D-145) (`SERVICE_STUB_LONGER_THAN_ITS_MINIMUM` · t1, verso-esistente, ts-sec)
- la tavola t1: le tratte s11-a, s11-b e x2-a, x2-b corrono affiancate in orizzontale per 25.0 mm a 7.5 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, s11-a, s11-b, x2-a, x2-b)
- la tavola t1: le tratte s5-a, s5-b e s6-a, s6-b corrono affiancate in verticale per 15.0 mm a 5.0 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, s5-a, s5-b, s6-a, s6-b)
- la tavola t1: le tratte s6-a, s6-b e s7-a, s7-b corrono affiancate in verticale per 25.0 mm a 5.0 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, s6-a, s6-b, s7-a, s7-b)
- la tavola t1: le tratte s7-a, s7-b e s8-a, s8-b corrono affiancate in verticale per 45.0 mm a 5.0 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, s7-a, s7-b, s8-a, s8-b)
- la tavola t1: il ritorno x2-a, x2-b corre **sopra** la mandata x1-a, x1-b per 25.0 mm sulla rete predisposizione: mandata sopra, ritorno sotto (B10, composition.py) (`RETURN_RUNS_ABOVE_ITS_SUPPLY` · t1, x1-a, x1-b, x2-a, x2-b)
- la tavola t1: fra collettore e volano la mandata e il ritorno corrono insieme per 80.0 mm ma tengono 2 interassi diversi (10, 15 mm): la coppia si apre, e mandata e ritorno corrono sempre insieme (B11, PO 20 settembre 2026) (`SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER` · t1, collettore, volano)

## Il cartiglio

- campi da definire: INDIRIZZO — nella casella c'e' «DA DEFINIRE» e la tavola esce in bozza (D-025)
