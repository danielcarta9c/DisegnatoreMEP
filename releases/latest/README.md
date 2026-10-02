# L'ultima release: 1.2.1

`DisegnatoreMEP-v1.2.1.zip` — sha256 `5c92d9b13b5f1552…` — è la prima consegna della beta (I-187), costruita da
`main` con `scripts/costruisci-skill.py`. Si carica come ogni skill personale, dallo ZIP.

Rispetto alla 1.2.0 (D-199):
- se il testo non dice se il progettista vuole i diametri delle tubazioni, la skill glielo chiede nel messaggio
  delle domande (I-185);
- all'approvazione la skill non manda più il grafo da leggere in `.md` (I-186): si approva sul riepilogo.

Le tavole sono le stesse della 1.2.0, byte per byte (`docs/collaudi/BETA-001/RAPPORTO.md`).

Alla prossima versione questo file e lo ZIP si sostituiscono; la copia numerata resta in `../archive/`.
