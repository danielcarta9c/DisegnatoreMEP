# Le offerte dei fornitori su PR.MI.059 — 18 novembre 2026 (I-302 … I-305)

Il PO ha consegnato in chat cinque PDF, con questa richiesta:

> «ho ricevuto queste 3 offerte da Idrosanitaria e abbattista in riferimento al progetto di cui ti carico schemi e
> lista materiali prodotta con la nostra skill. Per farti capire come sta lavorando la skill in primis ma soprattutto
> perche' vorrei che arricchissi il listino prezzi con queste altre voci (sempre tenendo in chiaro il fornitore) cosi'
> poi la skill quando la uso mi consiglia dove prendere il materiale in funzione del prezzo totale della minuteria.
> Ultimamente stiamo comprando da abbattista gli accessori piu' costosi (volani, circoaltore, v3vie) e poi sulla
> minuteria proprio stiamo un po' tra abbasttista, tecnomat e idrosanitaria. piano piano dobbiamo avere un listino
> completo di tutta la aminuteria di tutti e tre cosi' poi la skill mi aiuta a fare gli ordini (esempio compra queste 6
> cose da abbattista e queste 15 da Idrosaniatria).»

## I documenti

| Documento | Che cos'è | Righe | Totale (IVA esclusa) |
|---|---|--:|--:|
| Idrosanitaria, preventivo XC/STD/2704331 del 9 novembre 2026 (valido fino al 24 novembre) | tutta la commessa: pompa di calore, bollitore, volano, circolatore, minuteria idraulica, climatizzazione canalizzata Daikin con Airzone, rame, condensa | 81 | 10.835,01 € di merce + 8,75 € RAEE |
| Abbattista, ordine OC-STD-0185611 del 10 novembre 2026 (offerta 212119) | circolatore, volano, valvola di zona, bollitore | 4 | 1.058,62 € |
| Abbattista, ordine OC-STD-0188404 del 13 novembre 2026 (offerta 214224) | il circuito idraulico della pompa di calore | 42 | 1.547,12 € |
| Lista materiali PR.MI.059 rev. 01 del 6 novembre 2026 | la lista fatta con la skill, su cui i fornitori hanno quotato | — | — |
| Schema funzionale M.01 rev. 06 | la tavola della pompa di calore | — | — |

I totali delle righe trascritte tornano con quelli dei documenti (misura nel rapporto di `REL-027`).

## Perché i PDF non sono qui

La regola del registro vuole i documenti del PO copiati qui accanto. Questi **non si copiano**: portano il nome e
l'indirizzo del committente (la lista), i nomi e i telefoni degli addetti dei fornitori e l'email del PO (le offerte),
e il repository è pubblico (I-296). È la stessa scelta di I-300 per i file di BD.RM.260.

Quello che il PO ha chiesto di conservare — **le righe di prezzo, con il fornitore** — è nel listino:
`skill/distinta/LISTINO-MINUTERIA.md`, §4 (Abbattista) e §5 (Idrosanitaria), una riga per ogni riga dei documenti,
con il numero del documento e della riga (colonna Rif.). Le voci della lista, senza dati del committente, sono in
`docs/collaudi/REL-027/pr-mi-059/voci.json`.

**Da sapere:** con il listino nel repository pubblico, gli sconti di Abbattista (50+20, 50+25, 50+30, 50+15+3) e i
prezzi netti dei due fornitori sono leggibili da chiunque.
