# Vincoli — giro 1 (tavola A2, 45 tratte, 0 cedute, 0 bloccanti, 7 pieghe, 3 sormonti)

## A colpo d'occhio
Scheletro buono: autostrade primarie rette, collettori verticali corti accanto alle macchine,
coppia della serpentina che corre insieme. Due punti larghi: il secondario e l'uscita ACS.

## Cosa sembra sbagliato e i numeri approvano
- Sul secondario la seconda valvola del circolatore (CIR-01) finisce attaccata al radiatore,
  a 40 mm dalla pompa: si legge come valvola del radiatore, e la pompa sembra isolata da un
  lato solo. Nessun rilievo lo segnala.
- Sulla mandata comune succede lo stesso al separatore d'aria: la sua seconda valvola sta
  davanti alla deviatrice. Qui il tratto e' lungo per forza (sotto ci sono gli appesi del
  ritorno comune), e la valvola e' condivisa fra separatore e deviatrice: lo lascio.

## Vincoli
1. `radiatori` **addosso-a** `volano`: la mandata del secondario non piu' lunga di quanto
   chiede la fila VI + CIR-01 + VI. Regola: D3 (D-170, il disegno si tiene stretto).
   Si vede: secondario, fra VOL-01 e il radiatore.
2. `mixing-valve-thermostatic-bollitore-dhw-out` **addosso-a** `bollitore`: la risalita
   dell'ACS dall'attacco alto del bollitore la piu' corta che la fila consente.
   Regola: A4. Si vede: sopra BOL-01, la linea arancione sale di 25 mm prima di girare.

## Misurato (B3)
Ordine dei collettori: mandata vicina alle macchine 3 sormonti, ritorno vicino 4. Si tiene la
mandata vicina.

## Guardato e a posto
Pile dei generatori, appesi di sicurezza e termometri, gruppo del ritorno comune (vaso,
riempimento, manometro, defangatore), acqua fredda del bollitore con scarico e vaso sotto la
linea, ricircolo da destra, confini di rete addosso ai pezzi che servono.
