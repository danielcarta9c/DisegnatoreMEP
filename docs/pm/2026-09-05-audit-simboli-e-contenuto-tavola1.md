# Audit PM — simboli e contenuto della tavola 1

**Data:** 2026-09-05  
**Input:** I-030… I-040  
**Scopo:** traduzione vincolante per il DEV; gli allegati del PO restano materiale di
verifica PM e non una specifica da interpretare.

## Stato della libreria

La libreria contiene 39 simboli: 13 dichiarano derivazione da UNI 9511 tramite fonti
secondarie registrate, 21 rinviano a pratica/documentazione di settore e 5 dichiarano
esplicitamente una fonte puntuale ancora da acquisire. Il manifesto verifica porte,
rotazioni e aree di rispetto, ma non certifica da solo che la forma sia corretta.

Regola permanente:

> Un simbolo entra in una release soltanto se il PM ha verificato separatamente forma,
> semantica delle porte, orientamenti ammessi e compatibilità geometrica con gli
> accessori collegabili. Il DEV implementa la matrice approvata e i controlli meccanici;
> non sceglie la simbologia.

Il completamento della matrice per tutti i 39 simboli è attività PM prima della release
0.3. `DRAW-005` applica la matrice ai soli simboli critici della tavola 1.

## Matrice vincolante per DRAW-005

| Oggetto | Requisito | Riscontro PM | Implementazione attesa |
|---|---|---|---|
| Filtro a Y | forma classica a Y, con ramo inclinato e gambo inferiore; due porte in linea | il simbolo corrente è un segno a V e non è approvato dal PO; Caleffi conferma il filtro sul ritorno verso il generatore, non la forma convenzionale | rifare corpo SVG e raster di prova; mantenere due porte in linea e rotazioni coerenti |
| Confine di rete | punta nel verso locale dell'acqua | `cold-water-inlet` è uscente, `dhw-draw-off` entrante; condividono oggi lo stesso simbolo | la posa/renderer orienta dal `PortFlow`, non dall'ID o dal bordo del foglio |
| P/T/F interne | lettera sempre dritta rispetto al foglio | le tavole UNI 9511 riprodotte in SRC-016 sono il riferimento degli strumenti; la leggibilità non ruota col corpo | separare glifo dal corpo ruotabile o contro-ruotarlo; regola generale provata a 0/90/180/270° |
| PDC | porte di mandata e ritorno con spazio funzionale | interasse attuale 5 mm = altezza della valvola; causa sovrapposizioni e gradini; l'accumulo usa 15 mm | adottare per il simbolo PDC della tavola 1 interasse 15 mm, o variante di catalogo equivalente; non farne costante universale |
| Accumulo combinato | mantello con acqua tecnica e serpentino sanitario istantaneo | Rehau Taddy: accumulo per acqua di riscaldamento con scambiatore sanitario, ingresso AF e uscita ACS | simbolo distinto da puffer e bollitore; serpentino continuo leggibile fra `cold_in` e `dhw_out`; primario/secondario comunicano col volume tecnico, non con una serpentina |
| Puffer | solo volume di acqua tecnica | Caleffi distingue le configurazioni dell'accumulo inerziale; nessun circuito sanitario | simbolo e catalogo distinti dall'accumulo combinato |
| Bollitore | riserva sanitaria scaldata da serpentino tecnico | Rehau ACS Puffer distingue acqua sanitaria accumulata e mandata/ritorno serpentino | simbolo e porte distinti dal puffer e dal combinato |
| Etichette | sigle macchine sempre; indirizzi nodo opzionali | la consegna DRAW-004 ha 7 sigle e nessun indirizzo; la verifica mantiene il velo degli indirizzi | default consegna senza indirizzi; opzione esplicita per mostrarli; nessun impatto su geometria |

## Regole impiantistiche vincolanti per l'impianto 1

1. **Intercettazione delle PDC.** La coppia PDC + filtro a Y sul ritorno è un gruppo
   manutenibile: sul ritorno basta la valvola lato rete, oltre alla valvola sul ramo di
   mandata. Non va inserita una seconda valvola fra filtro e PDC. La regola generale non
   è più «una valvola per ogni porta di ogni pezzo manutenibile», ma «isolare il gruppo
   senza duplicare organi consecutivi che chiudono lo stesso volume».
2. **Valvola comune verso l'accumulo.** L'intercettazione sulla mandata comune deve stare
   vicina all'attacco `primary_in` dell'accumulo, salvo un organo che per funzione debba
   restare fra i due. La distanza è una proprietà di posa, non dell'ordine del file.
3. **Riempimento.** Un solo gruppo sul circuito di acqua tecnica: sul ritorno comune
   oppure su un attacco tecnico dedicato dell'accumulo. Per l'impianto 1 si conserva il
   ritorno comune già presente. Non si aggiunge alcun gruppo sulla linea sanitaria.
4. **Serpentino sanitario.** L'accumulo combinato deve avere `cold_in` alimentato dal
   confine AF e `dhw_out` diretto alla distribuzione ACS. Il modello DRAW-004 possiede già
   entrambe le connessioni: vanno preservate e rese graficamente riconoscibili, non
   duplicate.
5. **Costo dopo la correttezza.** Le variazioni del grafo rendono non confrontabile la
   lunghezza assoluta con DRAW-004. Prima si valida il nuovo grafo; poi si minimizzano,
   nell'ordine già vigente, backtracking, curve, incroci e lunghezza. Testi esclusi.

## Fonti verificate dal PM

- Caleffi, *Idraulica 61*, fig. 41 e pp. 43–45: accumulo inerziale, gruppo di caricamento
  e filtro defangatore sul ritorno verso il generatore (`SRC-019`).
- Rehau, *Manuale accumuli e bollitori*, pp. 12–16: Taddy, volume di acqua tecnica con
  serpentino sanitario, ingresso acqua fredda e mandata acqua calda (`SRC-018`).
- Tavole UNI 9511 riprodotte da Oppo, tabelle 2 e 10 (`SRC-016`), per convenzioni di
  giunzioni/accessori e strumenti; forma finale soggetta al giudizio PO.
- Schemi del disegnatore del PO: benchmark PM per composizione e colpo d'occhio, non
  fonte di requisiti da delegare al DEV (`I-023`, `I-038`).

## Fuori da DRAW-005

- audit visivo completo dei 39 simboli: attività PM prima di 0.3;
- spessori, cartiglio definitivo e finitura della legenda: release 0.4;
- impianti 2–5: solo dopo i gate 0.2A e 0.2B.
