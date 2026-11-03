# Rilievi della tavola — Centrale a pompa di calore aria-acqua villetta

Formato **A3** · tratte **27** · tratte cedute **0** · rilievi bloccanti **2**.

Li misurano i controlli della skill sulla tavola finita: il controllo di qualità e le regole del piano. Non sono un giudizio sull'impianto: dicono com'è disegnato.

## Bloccanti — la tavola non si consegna

- la tavola t1: la catena pdc -> tee-expansion-connection-pdc-water-return -> tee-filling-unit-pdc-water-return-b -> tee-pressure-gauge-pdc-water-return -> confluenza scavalca sé stessa 2 volte — la tratta fra raccordo a T e derivazione a T passa sopra quella fra derivazione a T e GT-01 a x=150.0, y=81.0; la tratta fra raccordo a T e derivazione a T passa sopra quella fra derivazione a T e derivazione a T a x=127.5, y=83.5: una linea che si scavalca è un groviglio. Si scioglie posando i raccordi e i pezzi nell'ordine in cui stanno lungo la catena, quello che `mep.py pezzi` stampa (REL-016, D1) (`RUN_CROSSES_ITSELF` · c6-a-1, c6-a-2, c6-a-3, c6-a-4-a, c6-a-4-b, c6-a-5-a, c6-a-5-b, c6-a-6, t1)
- la tavola t1: dirt-separator-pdc-water-return ha a e b su facce opposte, alla stessa quota x=95.0, ma il tratto che esce da a corre orizzontale a y=78.5 e il tratto che esce da b corre verticale a x=95.0 (tratta fra derivazione a T e GT-01): l'organo sta sulla piega e spezza il tratto, invece di lasciarlo passare (B4, D-154) (`INLINE_ORGAN_BREAKS_THE_RUN` · t1, dirt-separator-pdc-water-return, c6-a-4-a, c6-a-4-b, c6-a-5-a, c6-a-5-b, c6-a-6, c6-a-4-a, c6-a-4-b, c6-a-5-a, c6-a-5-b, c6-a-6)

## Da approvare — il progettista decide

- nessuno

## Avvisi — la tavola si consegna, e si sa

- nessuno

## Le regole del piano

- la tavola t1: lo stacco che porta af da tee-drain-connection-cold-bollitore-cold-in e' lungo 30.0 mm e il suo minimo su griglia e' 20.0, che e' quanto pretendono gli accessori in linea (valve-isolation-dhw-af-a), cioe' 10.0 mm di tubo in piu': un organo di servizio sta addosso al pezzo che serve (A4, D-145) (`SERVICE_STUB_LONGER_THAN_ITS_MINIMUM` · t1, af, tee-drain-connection-cold-bollitore-cold-in)
- la tavola t1: lo stacco che porta filling-unit-pdc-water-return da tee-filling-unit-pdc-water-return-b e' lungo 22.5 mm e il suo minimo su griglia e' 10.0, cioe' 12.5 mm di tubo in piu': un organo di servizio sta addosso al pezzo che serve (A4, D-145) (`SERVICE_STUB_LONGER_THAN_ITS_MINIMUM` · t1, filling-unit-pdc-water-return, tee-filling-unit-pdc-water-return-b)
- la tavola t1: lo stacco che porta inlet-filling-unit-pdc-water-return da filling-unit-pdc-water-return e' lungo 25.0 mm e il suo minimo su griglia e' 10.0, cioe' 15.0 mm di tubo in piu': un organo di servizio sta addosso al pezzo che serve (A4, D-145) (`SERVICE_STUB_LONGER_THAN_ITS_MINIMUM` · t1, inlet-filling-unit-pdc-water-return, filling-unit-pdc-water-return)
- la tavola t1: lo stacco che porta utenze da mixing-valve-thermostatic-bollitore-dhw-out e' lungo 40.0 mm e il suo minimo su griglia e' 20.0, che e' quanto pretendono gli accessori in linea (valve-isolation-dhw-hot-utenze-a), cioe' 20.0 mm di tubo in piu': un organo di servizio sta addosso al pezzo che serve (A4, D-145) (`SERVICE_STUB_LONGER_THAN_ITS_MINIMUM` · t1, utenze, mixing-valve-thermostatic-bollitore-dhw-out)
- la tavola t1: la tratta fra VD-01 e BOL-01 piega 3 volte, e i simboli che tocca ne impone 1: 2 di troppo — la catena e' bollitore -> deviatrice (B1, D-154, D-171) (`HIGHWAY_IS_NOT_STRAIGHT` · t1, c4-a, c4-b)
- la tavola t1: le tratte fra derivazione a T e GT-01 + fra derivazione a T e derivazione a T + fra derivazione a T e derivazione a T + fra raccordo a T e derivazione a T piegano 11 volte, e i simboli che toccano ne impongono 4: 7 di troppo — la catena e' pdc -> tee-expansion-connection-pdc-water-return -> tee-filling-unit-pdc-water-return-b -> tee-pressure-gauge-pdc-water-return -> confluenza (B1, D-154, D-171) (`HIGHWAY_IS_NOT_STRAIGHT` · t1, c6-a-1, c6-a-2, c6-a-3, c6-a-4-a, c6-a-4-b, c6-a-5-a, c6-a-5-b, c6-a-6)
- la tavola t1: la tratta fra raccordo a T e derivazione a T lascia la propria quota orizzontale 88.5, se ne scosta di 7.5 mm per 30.0 mm e ci torna: e' un sali-scendi, e si toglie spostando l'oggetto che occupa la quota, non piegando il tubo (B8, D-065) (`RUN_LEAVES_ITS_QUOTA_AND_COMES_BACK` · t1, c6-a-1)
- la tavola t1: la tratta fra derivazione a T e VD-01 e quella fra raccordo a T e derivazione a T corrono affiancate in orizzontale per 30.0 mm a 7.5 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, c1-b-a, c1-b-b, c6-a-1)
- la tavola t1: la tratta fra derivazione a T e VD-01 e quella fra derivazione a T e GT-01 corrono affiancate in orizzontale per 25.0 mm a 5.0 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, c1-b-a, c1-b-b, c6-a-4-a, c6-a-4-b, c6-a-5-a, c6-a-5-b, c6-a-6)
- la tavola t1: la tratta fra VOL-01 e raccordo a T e quella fra VD-01 e BOL-01 corrono affiancate in orizzontale per 5.0 mm a 5.0 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, c3-a, c3-b, c4-a, c4-b)
- la tavola t1: la tratta fra raccordo a T e derivazione a T e quella fra derivazione a T e derivazione a T corrono affiancate in orizzontale per 2.5 mm a 2.5 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, c6-a-1, c6-a-2)
- la tavola t1: la tratta fra raccordo a T e derivazione a T e quella fra derivazione a T e derivazione a T corrono affiancate in orizzontale per 10.0 mm a 7.5 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, c6-a-1, c6-a-3)
- la tavola t1: la tratta fra raccordo a T e derivazione a T e quella fra derivazione a T e GT-01 corrono affiancate in orizzontale per 22.5 mm a 2.5 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, c6-a-1, c6-a-4-a, c6-a-4-b, c6-a-5-a, c6-a-5-b, c6-a-6)
- la tavola t1: la tratta fra derivazione a T e derivazione a T e quella fra derivazione a T e GT-01 corrono affiancate in orizzontale per 5.0 mm a 5.0 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, c6-a-2, c6-a-4-a, c6-a-4-b, c6-a-5-a, c6-a-5-b, c6-a-6)
- la tavola t1: la tratta fra derivazione a T e derivazione a T e quella fra gruppo di riempimento e derivazione a T corrono affiancate in orizzontale per 7.5 mm a 5.0 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, c6-a-3, stub-filling-unit-pdc-water-return-b)
- la tavola t1: la tratta fra derivazione a T e VE-01 e quella fra gruppo di riempimento e derivazione a T corrono affiancate in verticale per 5.0 mm a 5.0 mm l'una dall'altra, e ne vogliono 10: sotto le tre corsie libere due tubi si leggono come uno (B9, D-062) (`PARALLEL_RUNS_WITHOUT_A_FREE_LANE` · t1, stub-expansion-connection-pdc-water-return-a, stub-expansion-connection-pdc-water-return-b, stub-filling-unit-pdc-water-return-b)
- la tavola t1: fra pannelli e volano la mandata e il ritorno corrono insieme per 40.0 mm ma tengono 2 interassi diversi (10, 15 mm): la coppia si apre, e mandata e ritorno corrono sempre insieme (B11, PO 20 settembre 2026) (`SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER` · t1, pannelli, volano)

## Il cartiglio

- compilato per intero
