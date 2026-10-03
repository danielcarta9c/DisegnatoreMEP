# L'ultima release: 1.4.0

`DisegnatoreMEP-v1.4.0.zip` — sha256 `9759280de271941e…`, 104 file — è **la tavola del caso reale rifatta** (I-201 …
I-206, D-206 … D-209): quello che il primo impianto vero ha riportato sulla 1.3.0, e il tempo del disegna.
Si carica come ogni skill personale, dallo ZIP così com'è.

Rispetto alla 1.3.0:
- **prima le autostrade**: il motore instrada le autostrade, poi la distribuzione, per ultimi gli stacchi, e
  un'autostrada disegnata non si sposta per una valvola di sfiato (D-206);
- **il collettore con ritorno si raccorda dritto ai terminali**: 40 × 15, a coppie mandata-ritorno di 10 mm come gli
  attacchi dei terminali; e **i colori della distribuzione**: il ritorno che esce dal collettore è ritorno, la mandata
  della pompa di carico del bollitore è mandata (D-207);
- **le pompe in parallelo con lo stesso verso**, e il controllo A2 che lo misura (D-208);
- **il disegna più veloce, con le stesse tavole**: sul caso reale 3,4 secondi invece di 107; sulle tavole agli atti
  da 1,3 a 7 volte meno della 1.3.0, fra mezzo secondo e due (D-209).

Fra le tavole agli atti cambiano solo quelle con due pompe in parallelo e quella dei simboli nuovi; le altre sono
quelle della 1.3.0 byte per byte (`docs/collaudi/REL-009/RAPPORTO.md`, §6).

Alla prossima versione questo file e lo ZIP si sostituiscono; la copia numerata resta in `../archive/`.
