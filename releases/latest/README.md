# L'ultima release: 1.2.2

`DisegnatoreMEP-v1.2.2.zip` — sha256 `fa922e80d8109a85…`, 104 file — è **la prima che si carica su claude.ai** (I-189,
D-200). Si carica come ogni skill personale, dallo ZIP così com'è.

Rispetto alla 1.2.1:
- simboli, catalogo e regole stanno in un file ciascuno: lo ZIP passa da 284 a 104 file, sotto i 200 che claude.ai
  accetta. Era la correzione del 2 ottobre rimasta su un ramo mai fuso (I-188);
- la descrizione sta nei 200 caratteri di claude.ai, e il frontespizio dichiara licenza e compatibilità;
- il lanciatore installa pydantic anche su un Python di sistema protetto;
- con Haiku la skill avvisa il progettista che il piano non si compone.

Le tavole sono quelle della 1.2.1, byte per byte (`docs/collaudi/BETA-001/RAPPORTO.md` §2).

Alla prossima versione questo file e lo ZIP si sostituiscono; la copia numerata resta in `../archive/`.
