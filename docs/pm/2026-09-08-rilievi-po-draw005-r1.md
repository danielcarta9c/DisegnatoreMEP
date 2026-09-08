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
4. **Sicurezza e sfogo aria sono separati.** La sicurezza esterna di DRAW-005, vicina
   all'accumulo e separata dalle PDC dalle loro intercettazioni, non protegge i generatori.
   SRC-027 prescrive la sommità del generatore o la mandata più vicina possibile, senza
   intercettazioni sulla connessione. Idraulica 61 dice che sicurezza e sfogo **possono**
   essere integrati nella PDC: il catalogo deve dichiararlo macchina per macchina. Il
   catalogo generico attuale dichiara a bordo soltanto il circolatore, quindi non può
   presumere la sicurezza integrata. Per la tavola 1 servono due sicurezze esterne, una
   per ciascuna PDC isolabile, prima della rispettiva valvola di mandata. Lo sfogo
   sull'attacco alto dell'accumulo resta corretto e non va spostato per analogia.
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
