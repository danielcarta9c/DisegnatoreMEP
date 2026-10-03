# L'ultima release: 1.3.0

`DisegnatoreMEP-v1.3.0.zip` — sha256 `2d2870e738fb2495…`, 104 file — è **la tavola del costruito** (I-191 … I-199,
D-205): nasce dal primo caso reale, un impianto da lasciare in centrale e allegare alla dichiarazione di conformità.
Si carica come ogni skill personale, dallo ZIP così com'è.

Rispetto alla 1.2.2:
- **togliere e spostare** un accessorio delle regole, con il motivo, e il **bordo della singola macchina**: `completa`
  scrive accanto a ogni accessorio il nome con cui si toglie, e la scelta regge a ogni rilancio (D-201);
- **gli accessori che il progettista colloca** in un posto preciso entrano nel grafo, e le regole non li duplicano;
- **l'esistente per pezzo e per tratto**: un dato per le regole e per i diametri, disegnato come il nuovo (D-202);
- **le voci del costruito, con il simbolo** (D-203): contatore di calore, attacco predisposto con la sua scritta,
  volano a sei attacchi, collettore con mandata e ritorno, confini con l'impianto esistente, giunto antivibrante,
  dosatore di polifosfati — quest'ultimo solo sull'acqua fredda che entra nell'accumulo dell'ACS (D-204);
- una scritta libera che non trova posto ferma la tavola, invece di sparire.

Le tavole di regressione sono quelle della 1.2.2, byte per byte (`docs/collaudi/REL-009/RAPPORTO.md`). Il caso reale
rifatto e il limite d'intervento restano in `REL-009`.

Alla prossima versione questo file e lo ZIP si sostituiscono; la copia numerata resta in `../archive/`.
