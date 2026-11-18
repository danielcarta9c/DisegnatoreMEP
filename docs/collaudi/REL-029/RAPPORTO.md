# REL-029 — Il bollitore sbagliato si esclude (la 2.2.1) — rapporto

**18 novembre 2026.** Pacchetto: `ACTIVE_WORK_PACKAGE.md` (I-330 … I-332, D-244). Ramo `claude/rel-029-bollitore-escluso`.

## 1. Le tavole

**Nessuna tavola cambia**: il pacchetto tocca solo il conto della lista prezzata (il banco lo conferma nella suite,
§3). Quello che il PO guarda è il costo di PR.MI.059 (§2).

## 2. La misura su PR.MI.059

Il PO, da progettista, ha accettato il Bolly 1 XL da 2 m² (I-330): il minimo della voce è 2 m².

```
$ python3 docs/collaudi/REL-027/pr-mi-059/misura.py
apparecchiature: 8 voci, prezzate 8, totale 6946.00 €
  P-A.2 Bollitore ACS — 200 l, a serpentino maggiorato …, non minore di 2 m²     626.52 €
      Abbattista        626.52 €, serpentino 2 m²
      Idrosanitaria     461.40 €  ESCLUSO: serpentino 0,8 m², sotto il minimo di 2 m²
voci 99, prezzate 90, da prezzare 9; totale 8907.68 €
ordine: 8855.00 € + senza fornitore 52.68 €
  Idrosanitaria: 33 articoli, 7511.78 €
  Tecnomat: 38 articoli, 686.73 €
  Abbattista: 3 articoli, 656.49 €
avviso M01c: Idrosanitaria 3103.60 € ⚠ è una Haier GT R290 12 kW trifase, non la Shenling ThermaX della commessa
```

La lista prezzata completa è **8.907,68 €**: 6.946,00 € di apparecchiature (il bollitore di Abbattista, 626,52 €) e
1.961,68 € di minuteria, invariata. Il bollitore di Idrosanitaria non è più un avviso: è escluso, e il conto lo dice.

## 3. I criteri, con il comando e l'output

**1 — l'esclusione.**

```
$ python3 -m pytest tests/distinta/test_rel028_due_liste_e_bollitore.py -q
14 passed
```

`test_il_listino_dice_il_serpentino_e_il_confronto_lo_usa`: con la 9 kW (2 m²) il bollitore di Idrosanitaria è escluso
(non è fra le offerte né fra gli avvisi) e vince Abbattista, con la nota «esclusi perché sbagliati: Idrosanitaria
(serpentino 0,8 m², sotto il minimo di 2 m²)»; con la 12 kW (2,5 m²) nessuno si sceglie, la voce è DA PREZZARE
(«nessun articolo del listino rispetta la voce; esclusi: …») e l'ordine non ha il bollitore.

**2 — la misura**: §2.

**3 — le prove di sempre.**

```
$ python3 -m pytest -q
SUITE

$ ruff check src tests
All checks passed!

$ mypy
Success: no issues found in 133 source files

$ python3 scripts/costruisci-skill.py
Skill: …/outputs/skill/disegnatore-mep (157 file, 3775 kB); ZIP sha256 4ca139d843a2ee21 → releases/latest/DisegnatoreMEP-v2.2.1.zip
Controlli … (al massimo 200 file): passati.
```

## 4. Le scelte della sessione

- Un bollitore che **non dice** la superficie resta uno scostamento ⚠ (non escluso): non è noto come sbagliato.
- Il numero **2.2.1** è una proposta: lo decide il PO.
