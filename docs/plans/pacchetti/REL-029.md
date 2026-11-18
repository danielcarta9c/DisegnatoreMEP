# REL-029 — Il bollitore sbagliato si esclude (la 2.2.1)

> **Scritto il 18 novembre 2026**, dopo la fusione di `REL-028` (la 2.2.0, PR #98). Il pacchetto precedente è in
> `docs/plans/pacchetti/REL-028.md`, il suo rapporto in `docs/collaudi/REL-028/RAPPORTO.md`.

**Da svolgere:** l'agente unico (**D-147**), nella sessione.
**Stato:** **CONSEGNATO** il 18 novembre 2026 (la 2.2.1, PR #99, fusa col sì del PO: «Si grazie»). Non c'è un pacchetto successivo: lo sceglie il PO.
**Base:** `main` con la 2.2.0 (PR #98). Ramo `claude/rel-029-bollitore-escluso`.
**Approvazione della fusione:** del PO. Il pacchetto non tocca il disegno: il PO guarda il costo di PR.MI.059.

## Il lavoro

Il PO, letta la 2.2.0: «Si ho accettato quello di Abbattista la skill. Comunque dovrebbe escludere quello di
Idrosanitaria perché è sbagliato. Certo ad oggi non ho neanche un bollitore da 2,5 mq per 150 o 200 litri di accumulo
in listino. Non riesco a trovarli sul mercato italiano.»

1. **Il bollitore col serpentino sotto il minimo è escluso dal confronto** (I-331, D-244): non si sceglie, nemmeno
   come ripiego; il conto dice chi è escluso; senza un bollitore buono la voce è DA PREZZARE.
2. **PR.MI.059 col Bolly 1 XL accettato** (I-330): il minimo della voce è 2 m², come lo scrive il progettista.
3. **Le istruzioni** (I-332): se nessun bollitore arriva al minimo, l'agente chiede al progettista se accetta un
   serpentino minore.

## Criteri di accettazione

Prima le misure, poi il racconto; il rapporto è `docs/collaudi/REL-029/RAPPORTO.md`.

1. Una prova: con la 9 kW il bollitore di Idrosanitaria (0,8 m²) è escluso e non è un avviso, vince Abbattista; con la
   12 kW (2,5 m²) nessuno si sceglie e la voce è DA PREZZARE con gli esclusi.
2. La misura di PR.MI.059 rifatta e mostrata al PO.
3. Banco, suite (0 failed, nessuno skip o xfail nuovo), ruff, mypy verdi; la release costruita con
   `scripts/costruisci-skill.py` e `tests/test_le_release.py` verde; non si fonde senza il sì del PO.
