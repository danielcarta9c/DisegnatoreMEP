# REL-024 — Rapporto della fase 1, prima parte: la CI e mypy

**6 novembre 2026.** Il pacchetto è in `ACTIVE_WORK_PACKAGE.md`; la disposizione del PO è I-295.

## Le tavole

**Nessuna tavola cambia, e lo si misura.** `confronta.sh` costruisce la skill da `main` (la 1.15.0) e dal ramo, e
con ciascuna rifà le stesse uscite: il T1 di `REL-023` (idraulica), la villetta di `REL-015` (idraulica ed
elettrico, più `completa` dal grafo), il caso aria-aria di `REL-012` fase 2 (`completa` e disegno), la distinta del
T1, la pianta del collaudo T3 di `REL-012`.

```
bash docs/collaudi/REL-024/confronta.sh <worktree di main> <uscita-main>
bash docs/collaudi/REL-024/confronta.sh .                  <uscita-ramo>
```

Esito: **16 file DXF e PDF su 16 identici byte per byte**; identici anche tutti gli SVG, i rilievi, i grafi completi,
la distinta (`distinta.json`, il foglio dei calcoli, le tabelle del foglio) e i tracciati della pianta. I log dei
comandi sono diversi solo per il percorso della cartella d'uscita. Il riepilogo del T1, uguale sui due lati:
`Formato A3 · tratte 29 · tratte cedute 0 · rilievi bloccanti 0 · pieghe 7 · sormonti 1 · avvisi e regole:
SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER x1`.

## mypy

Prima: con `python_version = "3.11"` mypy si fermava sugli stub di numpy (arriva con ezdxf, e i suoi stub usano
`type X = ...`, sintassi di Python 3.12) **prima di controllare il nostro codice**; `HANDOFF.md` lo dava per «è
l'ambiente». Forzato su 3.13, trovava **50 errori in 13 file**.

Che cosa si è fatto:

- `pyproject.toml`: `python_version = "3.12"`, il riferimento di `scripts/setup-env.sh`. Il minimo di 3.11 lo tiene
  la CI, che fa girare le prove anche su 3.11.
- Gli errori, uno per uno: quasi tutti **lo stesso nome riusato per due cose diverse** nella stessa funzione (`pezzo`
  prima lista di punti e poi pezzo della pianta, `c` prima punto e poi colonna, `tubazione`, `catena`, `chiave`,
  `lato`, `compagni`, `colore`, `tabelle`). Rinominati; il comportamento non cambiava, perché a runtime vinceva sempre
  l'ultimo legame. Poi annotazioni mancanti (`cast` sui JSON letti, il tipo di ritorno di un generatore, `PortFace`
  al posto di `str`, la chiave delle varianti dei blocchi DXF che ha tre elementi e non due) e un `assert` dove il
  ramo era già escluso.
- Nessun `type: ignore` aggiunto, nessun controllo spento.

Dopo: `python -m mypy` → `Success: no issues found in 127 source files`.

## La CI

`.github/workflows/ci.yml`, a ogni PR e su `main`:

- **prove** su Python 3.11 e 3.12: `pytest` (dentro c'è `tests/test_le_release.py`, che costruisce la skill e ne
  controlla i limiti del caricamento su claude.ai);
- **controlli** su 3.12: `ruff check src tests`, `mypy`.

La prima esecuzione è quella della PR di questo lavoro.

## Le misure

| comando | esito |
|---|---|
| `python -m pytest -q` (3.13, l'ambiente della sessione) | `2889 passed, 15 skipped, 11 xfailed` — come su `main` |
| `python -m pytest -q` (3.11, ambiente pulito con `uv`) | `2889 passed, 15 skipped, 11 xfailed` |
| `python -m ruff check src tests` | `All checks passed!` |
| `python -m mypy` | `Success: no issues found in 127 source files` |

**Un rilievo sulla suite.** Una prima esecuzione su 3.13, lanciata mentre giravano anche la suite su 3.11 e le due
costruzioni di `confronta.sh`, ha dato 5 rosse in `tests/graph/test_lines.py` (un simbolo che non si validava).
Rifatta da sola: verde, e il file da solo 27/27. Qualcosa nella suite o negli strumenti tocca i file condivisi
mentre un'altra esecuzione li legge: in CI non succede (ogni lavoro ha la sua macchina), ma va trovato prima di far
girare le prove in parallelo.

## Che cosa resta della fase 1

Il banco come prova (punto 3: `confronta.sh` è il primo passo, ma è ancora uno strumento di sessione) e la prova
senza rete (punto 4).
