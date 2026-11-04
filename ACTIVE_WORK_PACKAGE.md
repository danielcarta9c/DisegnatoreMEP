# REL-017 — La villetta di riferimento con le regole della 1.9.0

> **Scritto il 4 novembre 2026**, dopo la fusione della 1.9.0 (`REL-011`, PR #85, I-268). È il resto di `REL-011`:
> rifacendo la tavola elettrica la sessione ha visto che il **piano idraulico della villetta di riferimento**
> (`docs/collaudi/REL-015/pdc-regola/`) non regge le regole nuove — giunti, valvole antigelo, vaso prima del
> defangatore —, e che il suo `grafo-completo.json` agli atti è ancora quello delle regole della 1.8.

**Da svolgere:** l'agente unico (**D-147**), con agenti paralleli in sessione (**D-152**)
**Stato:** **IN CONSEGNA** (4 novembre 2026) — piano ricomposto, grafo e tavole rigenerati, la prova di rigenerazione; PR al PO.
**Base:** `main` dopo la PR #85 (la 1.9.0).
**Ramo:** quello che l'ambiente della sessione assegna.
**Approvazione della fusione:** **del PO**, guardando le tavole (D-146, D-147).

## Le cose da fare

1. Ricomporre `piano-idraulica.json` della villetta per il corredo nuovo; `rifai.sh` rigenera grafo completo e tavole
   dalle regole correnti; la tavola elettrica resta con 0 rilievi bloccanti.
2. Le due tavole al PO, prima e dopo.
3. Una prova che il `grafo-completo.json` della villetta sia la rigenerazione corrente, perché non torni vecchio.

## Dopo, da scegliere col PO (non si sceglie da soli)

- **I-248**: dimensionare canali dell'aria, cavi elettrici e protezioni;
- i rimasti di `REL-010` e `REL-009` (`docs/plans/pacchetti/REL-011.md`, «Da decidere col PO»): la soglia del revisore,
  i quattro difetti del disegno, il segno della commutatrice;
- il limite del motore: una valvola e il pezzo che isola ai due lati di una curva si toccano nello spigolo (D-120);
- le domande aperte della 1.9.0: relè disegnati accanto o dentro il quadro; le tre generalizzazioni fatte sullo ZIP
  della distinta; allineare la specifica Nove C Rev. 01 (7 l/kW, termometri).

## Criteri di accettazione

Quelli di `REL-011`: le tavole per prime; suite a 0 failed senza skip o xfail nuovi; `ruff check src tests` verde; il
banco di `REL-011` fra `main` e il ramo; nessun dato di cliente nel diff; `tests/test_le_release.py` verde se c'è una
release.
