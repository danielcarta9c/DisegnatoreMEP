# Rilievi della tavola — Prova REL-012 fase 3: la centrale dell'impianto 2 con elettrico e comando

Formato **A2** · tratte **37** · tratte cedute **0** · rilievi bloccanti **5**.

Li misurano i controlli della skill sulla tavola finita: il controllo di qualità e le regole del piano. Non sono un giudizio sull'impianto: dicono com'è disegnato.

## Bloccanti — la tavola non si consegna

- la tratta fra RG-01 e PDC-01 supera di 2.5 mm la propria porta di arrivo e ci torna indietro: si sposta l'oggetto, non si allunga la linea (B12, D-078) (`RUN_OVERSHOOTS_ITS_PORT` · t1, b1)
- la tratta fra RG-01 e VD-01 supera di 22.5 mm la propria porta di arrivo e ci torna indietro: si sposta l'oggetto, non si allunga la linea (B12, D-078) (`RUN_OVERSHOOTS_ITS_PORT` · t1, c1)
- la tratta fra RG-01 e CIR-01 supera di 17.5 mm la propria porta di arrivo e ci torna indietro: si sposta l'oggetto, non si allunga la linea (B12, D-078) (`RUN_OVERSHOOTS_ITS_PORT` · t1, c2)
- la tratta fra QE-01 e RG-01 supera di 7.5 mm la propria porta di arrivo e ci torna indietro: si sposta l'oggetto, non si allunga la linea (B12, D-078) (`RUN_OVERSHOOTS_ITS_PORT` · t1, e3)
- la tratta fra SO-01 e RG-01 supera di 5 mm la propria porta di arrivo e ci torna indietro: si sposta l'oggetto, non si allunga la linea (B12, D-078) (`RUN_OVERSHOOTS_ITS_PORT` · t1, t1)

## Da approvare — il progettista decide

- nessuno

## Avvisi — la tavola si consegna, e si sa

- la tratta fra RG-01 e PDC-01 cambia direzione 5 volte, oltre le 3 pieghe che bastano a unire due porte: la piega in piu' la chiede un ostacolo, e l'ostacolo si sposta (B4, D-078) (`RUN_WITH_TOO_MANY_BENDS` · t1, b1)
- la tratta fra QE-01 e PDC-01 cambia direzione 4 volte, oltre le 3 pieghe che bastano a unire due porte: la piega in piu' la chiede un ostacolo, e l'ostacolo si sposta (B4, D-078) (`RUN_WITH_TOO_MANY_BENDS` · t1, e1, e2)
- la tratta fra SO-01 e RG-01 cambia direzione 4 volte, oltre le 3 pieghe che bastano a unire due porte: la piega in piu' la chiede un ostacolo, e l'ostacolo si sposta (B4, D-078) (`RUN_WITH_TOO_MANY_BENDS` · t1, t1)
- la tratta fra SO-02 e RG-01 cambia direzione 4 volte, oltre le 3 pieghe che bastano a unire due porte: la piega in piu' la chiede un ostacolo, e l'ostacolo si sposta (B4, D-078) (`RUN_WITH_TOO_MANY_BENDS` · t1, t2)

## Le regole del piano

- la tavola t1: lo stacco che porta air-vent-volano-primary-out da volano e' lungo 12.5 mm e il suo minimo su griglia e' 0.0, cioe' 12.5 mm di tubo in piu': un organo di servizio sta addosso al pezzo che serve (A4, D-145) (`SERVICE_STUB_LONGER_THAN_ITS_MINIMUM` · t1, air-vent-volano-primary-out, volano)
- la tavola t1: la tratta fra RG-01 e PDC-01 e quella fra QE-01 e RG-01 corrono affiancate in verticale per 30.0 mm a 5.0 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, b1, e3)
- la tavola t1: la tratta fra RG-01 e PDC-01 e quella fra SO-01 e RG-01 corrono affiancate in orizzontale per 52.5 mm a 2.5 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, b1, t1)
- la tavola t1: la tratta fra RG-01 e PDC-01 e quella fra SO-02 e RG-01 corrono affiancate in orizzontale per 17.5 mm a 2.5 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, b1, t2)
- la tavola t1: la tratta fra RG-01 e PDC-01 e quella fra SE-01 e RG-01 corrono affiancate in orizzontale per 20.0 mm a 5.0 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, b1, t3)
- la tavola t1: la tratta fra RG-01 e PDC-01 e quella fra QE-01 e PDC-01 corrono affiancate in verticale per 7.5 mm a 5.0 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, b1, e1, e2)
- la tavola t1: la tratta fra RG-01 e PDC-01 e quella fra BOL-01 e valvola miscelatrice termostatica corrono affiancate in orizzontale per 22.5 mm a 7.5 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, b1, w2-a-a-a, w2-a-a-b)
- la tavola t1: la tratta fra RG-01 e VD-01 e quella fra RG-01 e CIR-01 corrono affiancate in verticale per 67.5 mm a 5.0 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, c1, c2)
- la tavola t1: la tratta fra RG-01 e VD-01 e quella fra SO-01 e RG-01 corrono affiancate in orizzontale per 47.5 mm a 7.5 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, c1, t1)
- la tavola t1: la tratta fra RG-01 e CIR-01 e quella fra SO-02 e RG-01 corrono affiancate in verticale per 15.0 mm a 5.0 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, c2, t2)
- la tavola t1: la tratta fra RG-01 e CIR-01 e quella fra SO-01 e RG-01 corrono affiancate in orizzontale per 47.5 mm a 2.5 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, c2, t1)
- la tavola t1: la tratta fra QE-01 e PDC-01 e quella fra QE-01 e RG-01 corrono affiancate in orizzontale per 10.0 mm a 5.0 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, e1, e2, e3)
- la tavola t1: la tratta fra QE-01 e PDC-01 e quella fra SO-01 e RG-01 corrono affiancate in orizzontale per 52.5 mm a 7.5 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, e1, e2, t1)
- la tavola t1: la tratta fra QE-01 e PDC-01 e quella fra SE-01 e RG-01 corrono affiancate in orizzontale per 20.0 mm a 5.0 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, e1, e2, t3)
- la tavola t1: la tratta fra QE-01 e PDC-01 e quella fra BOL-01 e valvola miscelatrice termostatica corrono affiancate in orizzontale per 22.5 mm a 7.5 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, e1, e2, w2-a-a-a, w2-a-a-b)
- la tavola t1: la tratta fra SO-01 e RG-01 e quella fra SO-02 e RG-01 corrono affiancate in orizzontale per 17.5 mm a 5.0 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, t1, t2)
- la tavola t1: la tratta fra SO-01 e RG-01 e quella fra SE-01 e RG-01 corrono affiancate in orizzontale per 20.0 mm a 2.5 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, t1, t3)
- la tavola t1: la tratta fra SO-02 e RG-01 e quella fra SE-01 e RG-01 corrono affiancate in orizzontale per 12.5 mm a 7.5 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, t2, t3)
- la tavola t1: fra ventilconvettori e volano la mandata e il ritorno corrono insieme per 50.0 mm ma tengono 2 interassi diversi (10, 15 mm): la coppia si apre, e mandata e ritorno corrono sempre insieme (B11, PO 20 settembre 2026) (`SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER` · t1, ventilconvettori, volano)

## Il cartiglio

- campi da definire: INDIRIZZO — nella casella c'e' «DA DEFINIRE» e la tavola esce in bozza (D-025)
