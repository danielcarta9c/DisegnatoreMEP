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
3193 passed, 15 skipped, 11 xfailed in 306.96s (0:05:06)   (skip e xfail invariati; banco verde, nessuna tavola cambia)

$ ruff check src tests      → All checks passed!
$ mypy                      → Success: no issues found in 133 source files
$ python3 scripts/costruisci-skill.py
ZIP sha256 6f2ea4e5a60f9153, 157 file → releases/latest/DisegnatoreMEP-v2.2.2.zip; controlli passati
```

## 3bis. Il preventivo corretto di Idrosanitaria (I-334)

Il PO: «il Bolly XL Idrosanitaria ce lo ha corretto e lo ha quotato a 546». Nel listino §5 la riga M10b di
Idrosanitaria è il Bolly 1 XL WB 200 a 546,00 € (2 m²); il Bolly 1 ST da 0,8 m² resta documentato senza ID. Il
modello WB e il codice 3104162330011 sono assunti dalla scheda Cordivari: da confermare.

```
$ python3 docs/collaudi/REL-027/pr-mi-059/misura.py
  P-A.2 Bollitore ACS — 200 l, … non minore di 2 m²     546.00 €
      Idrosanitaria     546.00 €, serpentino 2 m²
      Abbattista        626.52 €, serpentino 2 m²
voci 99, prezzate 90, da prezzare 9; totale 8827.16 €
ordine: 8774.48 € + senza fornitore 52.68 €
  Idrosanitaria: 34 articoli, 8057.78 €   Tecnomat: 38 articoli, 686.73 €   Abbattista: 2 articoli, 29.97 €
```

Su PR.MI.059 il bollitore costa 80,52 € meno che da Abbattista, e la lista prezzata completa scende a 8.827,16 €. Le
prove dell'esclusione usano ora un bollitore di prova da 0,8 m² (`_con_un_bollitore_piccolo`), perché nel listino vero
non c'è più.

## 4. Le scelte della sessione

- Le porte del catalogo del bollitore sono sei: la seconda uscita ACS in alto (1¼") e la resistenza (1½") del WWM non
  ci sono, e la skill non le conta.
- Il numero **2.2.2** è una proposta.
