# Traduzione PM dei rilievi PO su DRAW-005

**Data:** 2026-09-08  
**Esito PO:** impostazione generale approvata; gate 0.2A sospeso per rifiniture puntuali.  
**Allegati:** `docs/input-pm/rilievi-grafici/2026-09-08-draw005/`.

## Diagnosi verificata

1. **Filtro a Y.** Il corpo è riconoscibile ma incompleto: mancano le barrette terminali
   perpendicolari all'asse. Alla scala A3 il tratto medio da 0,35 mm è troppo debole per
   questo segno; il simbolo deve dichiarare il tratto spesso da 0,50 mm senza eccezioni
   legate al proprio identificativo.
2. **Riempimento.** È acqua che entra nell'impianto: la freccia sul ramo deve puntare dal
   gruppo verso il ritorno. Il tratto lato impianto appartiene alla rete tecnica di
   ritorno ed è blu; un eventuale tratto a monte del gruppo, se modellato, appartiene
   invece all'adduzione idrica. Caleffi 01025/11 conferma funzione e senso (SRC-022).
3. **Rami statici.** Nel modello corrente il simbolo `P` è un **manometro**, non un
   pressostato. Manometro e vaso insistono sul ritorno tecnico, quindi i loro stacchi sono
   blu. Non rappresentano una portata ordinaria unidirezionale: nessuna freccia di
   circolazione. Lo stesso principio vale per uno sfogo o una sicurezza finché non è
   modellata una vera tubazione di scarico.
4. **Sicurezza e sfogo aria sono separati.** SRC-027 prescrive la sommità del generatore
   o la mandata più vicina possibile, senza intercettazioni sulla connessione. Questo non
   significa però automaticamente “una sicurezza per ogni PDC”: va protetto ogni dominio
   pressurizzato che possa rimanere isolato dalla protezione nelle configurazioni ammesse.
   Una sicurezza comune può servire più macchine se resta comunicante col dominio da
   proteggere; una protezione per macchina richiede invece un dato di catalogo o uno
   schema che crei domini autonomi. Idraulica 61 dice inoltre che sicurezza e sfogo
   **possono** essere integrati nella PDC. L'assenza della funzione `safety` dal catalogo
   generico è un dato mancante, non la prova che il dispositivo non sia a bordo. Nella
   tavola 1 la sicurezza esistente va **spostata** dall'accumulo alla mandata vicino al
   gruppo PDC, non mantenuta e duplicata: deve risultarne una sola. Lo sfogo sull'attacco
   alto dell'accumulo resta distinto e non va moltiplicato per il numero delle PDC.
5. **Catena sul ritorno PDC.** Due macchine uguali con la stessa catena funzionale devono
   produrre la stessa geometria locale: porta PDC → filtro a Y → valvola → rete. Filtro e
   valvola stanno sul primo rettilineo utile dalla porta, prima della prima curva; una
   rotazione della catena non ne cambia distanze e ordine.
6. **Serpentino.** Deve restare continuo da `cold_in` a `dhw_out`, ma il corpo grafico
   diventa una serpentina morbida e centrata, con curve raccordate, senza cambiare porte,
   attacchi o grafo.

## Regole di rendering da implementare

- il colore deriva dalla rete del tratto, non dalla direzione grafica del ramo;
- la freccia compare solo quando esiste un flusso ordinario diretto;
- riempimento: flusso verso la rete tecnica;
- misura, espansione, sfiato e sicurezza su stacco: nessuna freccia di circolazione;
- eventuale scarico esplicitamente modellato: freccia verso lo scarico;
- il peso del tratto di un simbolo è un dato del manifesto (`thin`, `medium`, `thick`),
  validato e applicato in tavola, legenda e foglio simboli.

## Fonti e limiti

- [Caleffi, valvole di sicurezza 01253/25](https://www.caleffi.com/sites/default/files/media/external-file/01253_IT.pdf), p. 4;
- [Caleffi, Idraulica 61](https://www.caleffi.com/sites/default/files/media/external-file/Idraulica_61_IT_Gli%20impianti%20a%20pompa%20di%20calore%20aria-acqua.pdf), pp. 14–15 e 44–45;
- [UNI EN 12828:2014](https://store.uni.com/uni-en-12828-2014), in vigore;
- SRC-022 per il gruppo di riempimento.

L'immagine della ricerca Google è un input del PO, non una fonte tecnica. È corretta sul
principio della sicurezza non intercettabile vicino al generatore, ma non rende la
posizione dello sfogo aria una regola assoluta.

## Correzione PM dopo il collaudo DRAW-005-R1

Il PDF prodotto dalla PR #21 ha mostrato due ulteriori errori di posa (I-046):

- gli stacchi di sicurezza e degli altri accessori appesi non hanno una lunghezza fissa
  arbitraria: usano il minimo tratto compatibile con ingombro del simbolo, spessore e
  leggibilità; ogni millimetro ulteriore entra nel costo;
- se catene o raccordi delle PDC si contendono lo spazio, il primo candidato è aumentare
  l'interasse verticale fra le macchine a passi di griglia. La traslazione dei
  componenti non costa; curve, incroci e lunghezza sì.

La precedente imposizione di due sicurezze esterne per-PDC è ritirata.
