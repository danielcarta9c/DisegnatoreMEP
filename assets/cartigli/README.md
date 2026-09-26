# Cartigli

Cartigli originali Nove C utilizzabili per gli elaborati del progetto.

I file sorgente vengono conservati senza modifiche. Eventuali adattamenti o versioni derivate dovranno avere un nome distinto e una provenienza documentata.

| file | che cos'è | da dove viene |
|---|---|---|
| `Cartiglio_NoveC_A3.pdf` | **il cartiglio**, il file sorgente | dato dal PO il 25 settembre 2026: «questo è il cartiglio che usiamo per i fogli A3» (I-130). Sostituisce la versione del primo commit, che resta in Git: stessa geometria, i valori sono diventati segnaposto |
| `Cartiglio_NoveC_A3.json` | il **modello** del cartiglio: ogni tratto, campitura, testo e segnaposto, nell'ordine in cui il file li dipinge | **derivato**: lo scrive `examples/cartigli/build_cartiglio.py` leggendo il PDF, e una prova pretende che rieseguirlo dia lo stesso file. Non si modifica a mano |
| `Cartiglio_NoveC_A3-logo.jpg` | il logo | **derivato**: il JPEG contenuto nel PDF, estratto byte per byte dallo stesso generatore |

Il cartiglio è largo 400 mm: su ogni formato resta a misura, contro l'angolo in basso a destra della squadratura, e l'A4 — 277 mm utili — non lo contiene (D-186). La tavola lo porta quando il comando riceve `--cartiglio assets/cartigli/Cartiglio_NoveC_A3.json`.

**Se il PO manda una versione nuova del PDF**, si sostituisce il file e si rilancia il generatore. Se il generatore si ferma, dice perché: un testo nuovo va dichiarato nel generatore, un segnaposto sparito va cercato.
