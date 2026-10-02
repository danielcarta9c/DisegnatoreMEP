# L'ultima release: 1.2.0

`DisegnatoreMEP-v1.2.0.zip` — sha256 `fa9e410a7e994f66…` — è la skill che il PO ha distribuito ai suoi
collaboratori il 2 ottobre 2026 (I-178, I-181, I-184), **così com'è stata consegnata**. Si carica come ogni
skill personale, dallo ZIP.

È stata costruita prima della pulizia del solutore (D-197): lo ZIP che `main` costruisce oggi è più leggero
(760 kB contro 822) perché non porta più `improve.py` e `dilate.py`, che la skill non chiamava, e **disegna le
stesse tavole, byte per byte** (`docs/collaudi/REL-005/pulizia-del-solutore/RAPPORTO.md`).

Alla prossima versione questo file e lo ZIP si sostituiscono; la copia numerata resta in `../archive/`.
