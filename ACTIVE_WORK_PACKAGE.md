# REL-030 — Il bollitore Boilernova euromax WWM nella skill (la 2.2.2)

> **Scritto il 18 novembre 2026**, dopo la fusione di `REL-029` (la 2.2.1, PR #99 e #100).

**Da svolgere:** l'agente unico (**D-147**), nella sessione.
**Stato:** **IN CORSO**, dalla disposizione del PO del 18 novembre 2026 («Si registralo», I-333).
**Base:** `main` dopo la PR #100. Ramo `claude/rel-030-euromax`.
**Approvazione della fusione:** del PO. Il pacchetto non tocca il disegno.

## Il lavoro

Il PO ha portato la scheda del Boilernova euromax WWM (https://www.boilernova.com/wp-content/uploads/2020/04/EUROMAX.pdf):
il 200 ha 190 l utili e un serpentino vetrificato da 3,0 m², per pompa di calore. Si registra come il Bolly 1 XL:

1. gli attacchi per porta (serpentino, acqua fredda, ACS, ricircolo, sonda) e la superficie del serpentino per taglia
   (`src/disegnatore_mep/diametri/costruttori.py`), così il raccordo all'attacco scrive il pollice giusto;
2. la superficie della scheda vale quando il grafo non la scrive (anche per il Bolly 1 XL), per gli avvisi del
   serpentino;
3. il prezzo **non** entra nel listino finché non c'è un'offerta (un prezzo senza fonte non entra).

## Criteri di accettazione

1. Prove: l'euromax WWM 200 sulla Shenling 12 kW dà raccordi M 1" all'attacco del serpentino e nessun avviso (3,0 ≥ 2,5);
   il Bolly 1 XL 200 senza superficie nel grafo dà l'avviso dei 2 m².
2. Banco, suite (0 failed, nessuno skip o xfail nuovo), ruff, mypy verdi; la release con `scripts/costruisci-skill.py`
   e `tests/test_le_release.py` verde; non si fonde senza il sì del PO.
