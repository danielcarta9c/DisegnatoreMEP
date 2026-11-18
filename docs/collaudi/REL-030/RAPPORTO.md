# REL-030 — Il bollitore Boilernova euromax WWM nella skill (la 2.2.2) — rapporto

**18 novembre 2026.** Pacchetto: `ACTIVE_WORK_PACKAGE.md` (I-333). Ramo `claude/rel-030-euromax`.

## 1. Le tavole

**Nessuna tavola cambia** (il banco nella suite, §3). Il pacchetto tocca la lista materiali: i raccordi all'attacco e
gli avvisi del serpentino.

## 2. Che cosa sa la skill dell'euromax WWM

Dalla scheda Boilernova portata dal PO (https://www.boilernova.com/wp-content/uploads/2020/04/EUROMAX.pdf, pp. 61-64),
in `src/disegnatore_mep/diametri/costruttori.py`, per taglia (200 … 2000): mandata e ritorno del serpentino (1" sul
200-300, 1¼" dal 400), acqua fredda e ACS (1" fino al 500), ricircolo (½" fino al 500), sonda ½", superficie del
serpentino (200: 3,0 m²). Il pezzo si riconosce da marca «Boilernova» (o «euromax») e modello con «WWM», e dal
volume. Il prezzo non è nel listino: la scheda non lo dà, e un prezzo senza fonte non entra.

## 3. I criteri, con il comando e l'output

```
$ python3 -m pytest tests/distinta/test_rel028_due_liste_e_bollitore.py -q
16 passed
```

`test_l_euromax_wwm_200_ha_i_suoi_attacchi_e_il_suo_serpentino`: sulla Shenling 12 kW i due raccordi del serpentino
sono «M 1" × tubo multistrato MS 32×3, all'attacco» e non c'è nessun avviso (3,0 m² ≥ 2,5);
`test_il_bolly_1_xl_200_dice_i_suoi_2_m2_anche_se_il_grafo_non_li_scrive`: il Bolly 1 XL 200 dà l'avviso dei 2 m².

```
$ python3 -m pytest -q
SUITE

$ ruff check src tests      → All checks passed!
$ mypy                      → Success: no issues found in 133 source files
$ python3 scripts/costruisci-skill.py
ZIP sha256 3e324d57aa5dc751, 157 file → releases/latest/DisegnatoreMEP-v2.2.2.zip; controlli passati
```

## 4. Le scelte della sessione

- Le porte del catalogo del bollitore sono sei: la seconda uscita ACS in alto (1¼") e la resistenza (1½") del WWM non
  ci sono, e la skill non le conta.
- Il numero **2.2.2** è una proposta.
