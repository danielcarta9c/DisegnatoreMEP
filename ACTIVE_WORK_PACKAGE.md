# REL-023 — Il corredo standard: una 12 kW sui 1.700 € di materiale

> **Scritto il 6 novembre 2026**, dopo `REL-022` (la 1.15.0). Il PO: «Dobbiamo fare dopo un lavoro di ottimizzazione
> e pensare ad un corredo standard per cui su una 12 kw stiamo sui 1700 di materiale. Mettiamolo come prox task una
> volta finito quello che stiamo facendo» (I-289).

**Da svolgere:** l'agente unico (**D-147**), con agenti paralleli in sessione (**D-152**)
**Stato:** **IN CORSO** — i punti 2 (le giunzioni, I-291) e una parte dell'1 (antigelo di base senza valvole, I-290; il circolatore fuori dalla minuteria, I-292) sono sul ramo della 1.15.0, `claude/distinta-dal-contesto`, in attesa che il PO guardi le tavole e approvi la fusione. Restano 1 (defangatore, intercettazioni, il tipo del differenziale), 3 e 4.
**Base:** il ramo della 1.15.0 (PR #90).

## Il punto di partenza (misurato, `docs/collaudi/REL-022/RAPPORTO.md`)

La 12 kW con la 3 vie del collaudo T1 costa **1.929 €** a listino, il 13% sopra il riferimento. Le voci più pesanti:
33 raccordi a pressare M 1" × MS 32 (212 €), 43 m di MS 32 preisolato (170 €), 2 valvole antigelo (155 €), 20 gomiti
MS 32 (149 €), il defangatore magnetico 1" (105 €), la deviatrice (93 €), il circolatore (92 €).

## Che cosa si fa (da concordare col PO prima di scrivere le regole)

1. **Il corredo standard di una centrale domestica**: quali accessori Nove C mette davvero (antigelo o glicole, un
   defangatore di quale fascia, quante intercettazioni), con il PO, su una sua distinta d'acquisto reale.
2. **I raccordi** — **FATTO** (D-239): un nipplo fra due accessori, un raccordo a pressare fra tubo e accessorio, i tee dal grafo, i gomiti a corpo o dal contesto del progetto. Collaudo in `docs/collaudi/REL-023/RAPPORTO.md`: il T1 coi metri di una commessa vera fa 1.425 €.
3. **Le scelte del listino** di fascia giusta per Nove C (marche, prezzi d'acquisto invece che al banco).
4. **La prova**: la 12 kW con la 3 vie sui 1.700 € di materiale, e le altre taglie in proporzione.
