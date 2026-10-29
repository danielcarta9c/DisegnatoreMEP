# Esito dei test del repository con l'estensione applicata

Misurato il 29/10/2026 su una copia di `main` dopo la PR #79 (1.5.0, `dfc68c1`). I comandi:

```bash
git apply --check -p1 per-il-repo/src-estensione.patch        # passa
git apply -p1 per-il-repo/src-estensione.patch
cp per-il-repo/assets/symbols/* assets/symbols/
cp per-il-repo/examples/layout/catalog/* examples/layout/catalog/
cp per-il-repo/naming/* naming/
PYTHONPATH=src python3 -m pytest -q --ignore=tests/test_le_release.py -p no:cacheprovider
```

| | passati | falliti | saltati | xfail |
|---|---|---|---|---|
| `main` com'è (base) | 2037 | 7 | 15 | 10 |
| `main` + estensione | 2054 | 17 | 15 | 10 |

**I 7 falliti della base** falliscono anche senza l'estensione, in questo ambiente. Sono probabilmente ambientali:
`test_the_sigle_do_not_depend_on_the_hash_seed` (5 casi), `test_un_json_non_valido_dice_dove_si_e_rotto`,
`test_la_skill_costruita_disegna_da_sola`. Vanno riguardati nella sessione di sviluppo, a parte.

**I 10 falliti in più sono dell'estensione**, e dicono che cosa va rifatto bene:

| test | perché fallisce | come si chiude |
|---|---|---|
| `tests/catalog/test_generated_fixtures.py::test_the_generator_reproduces_what_is_committed[examples/graphics/build_symbols.py-assets/symbols]` | `assets/symbols/` è **generata** da `examples/graphics/build_symbols.py`: i file copiati a mano non coincidono con il generatore | aggiungere gli 11 simboli al generatore (i corpi SVG e i manifesti sono in `assets/symbols/` di questo kit) e rigenerare |
| `tests/acceptance/test_symbol_sheet.py::test_every_other_shipped_symbol_admits_all_four_rotations` | UE, UI, plenum, centrale e quadro dichiarano solo la rotazione 0, e il test ammette questa eccezione solo per un elenco chiuso di simboli | decidere se aggiungerli all'elenco delle macchine che non si ruotano, come pompa di calore e caldaia, oppure renderli ruotabili |
| `tests/graphics/test_bodies.py::test_the_libraries_are_not_empty` (62 → 73) e `tests/graphics/test_pdf.py::test_ogni_simbolo_della_libreria_si_traduce` (54 → 65) | contano i simboli della libreria | aggiornare i conteggi con la libreria nuova |
| `tests/diametri/test_sulla_tavola.py::test_il_disegno_non_si_muove_e_senza_richiesta_non_c_e_niente[1-6]` | la riga di legenda del DN era «Øi» ed è diventata «Ø · L» per tutti | nel repository la scritta manuale per tratto deve avere **la sua** riga di legenda: quella del DN calcolato resta «Øi», come prescrive I-155 |

In sintesi la patch è applicabile e non rompe il motore. I falliti sono di libreria (generatore, conteggi, rotazioni)
più uno di progetto: la legenda della scritta manuale. Sono tutti lavoro previsto di REL-012.
