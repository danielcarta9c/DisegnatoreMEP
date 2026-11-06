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

**La prima esecuzione (PR #92) ha trovato subito una dipendenza nascosta.** Due prove della pianta
(`tests/pianta/test_tavola.py`, `tests/pianta/test_collaudo_t1.py`) si aspettano l'anteprima PNG, che la fa
pypdfium2 o, in mancanza, `pdftoppm`. Le dipendenze di sviluppo non avevano né l'uno né l'altro: le prove passavano
solo dove `pdftoppm` era installato per caso, come nell'ambiente delle sessioni. Riprodotto in locale con un `PATH`
senza `pdftoppm` (2 failed), corretto aggiungendo `pypdfium2==5.13.0` alle dipendenze `dev` (la stessa versione che la
skill installa da sé, `skill/scripts/mep.py`), e riverificato: 2 passed, e la suite intera su 3.11 con il `PATH`
ridotto all'osso `2889 passed, 15 skipped, 11 xfailed`.

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

---

# Fase 1, seconda parte: il banco come prova e la skill senza rete

**6 novembre 2026**, dopo la 1.15.1 (PR #92).

## Le tavole

**Nessuna tavola cambia**, e da qui lo dice una prova. Il banco nuovo: 28 casi, i 24 di `REL-011` più il T1 di
`REL-023` con la sua distinta, la villetta di `REL-015` (idraulica ed elettrico), l'aria-aria di `REL-012` fase 2 e il
collaudo T3 di `REL-012` con la sua pianta. `python scripts/banco.py` → `28 uguali, 0 cambiati, su 28`.

## Il banco come prova (punto 3)

- `scripts/banco.py` rifà ogni caso dal codice del repository (`completa` se il grafo è di prima stesura, `disegna`
  con ogni piano, la distinta e la pianta dove ci sono) e ne prende le impronte: sha256 degli SVG, dei rilievi, del
  grafo completo, della distinta e dei tracciati, più la riga di sintesi di `disegna`. Il PDF e il DXF ne sono
  traduzioni e non si improntano.
- `tests/banco/impronte.json` le registra; `tests/test_il_banco.py` le confronta a ogni PR (29 prove, 24 s).
- **Una tavola cambiata non si fa tacere**: se la modifica è voluta, `python scripts/banco.py --registra --uscita
  <cartella>` riscrive le impronte e lascia le tavole da mostrare al PO nella PR (D-146).

Misure:

| controllo | esito |
|---|---|
| determinismo: il banco di `REL-011` su Python 3.13 e su 3.11 con `PYTHONHASHSEED=123` | 24 SVG su 24 identici |
| `python scripts/banco.py` su 3.13 e su 3.11 con `PYTHONHASHSEED=7` | `28 uguali, 0 cambiati, su 28` tutte e due |
| la prova sa fallire: `LINE_CLEARANCE_MM` da 0,5 a 1,0 mm (poi rimesso) | `9 failed, 20 passed`, con le uscite cambiate per nome |

## La skill senza rete (punto 4)

Lo ZIP della 1.15.1 in un Python 3.12 pulito, con l'indice di PyPI puntato su una porta chiusa:

| situazione | esito |
|---|---|
| senza pydantic | `ambiente` si ferma in 8 s: «Senza pydantic il comando non parte. Serve un ambiente con Python 3.11 o più e la libreria pydantic==2.13.4, oppure la rete per installarla.» `SKILL.md` («Prima di cominciare», punto 1) dice all'agente di riferirlo al progettista |
| con pydantic, senza ezdxf e pypdfium2 | la tavola esce, **identica** (SVG uguale byte per byte), in PDF e SVG; il DXF manca e lo dice |
| **il difetto** | ogni comando ritentava l'installazione delle facoltative: `disegna` 8,8 s invece di 1,2 (pip riprova cinque volte) |

La correzione (`skill/scripts/mep.py`): un'installazione facoltativa non riuscita lascia un segno nella cartella
temporanea e non si ritenta nella stessa sessione (lo dice, con il comando per riprovare); pip con `--timeout 15
--retries 1`. pydantic, senza il quale il comando non parte, si ritenta sempre. Dopo: `disegna` 1,3 s al primo comando,
0,85 s ai successivi, SVG identico. Tre prove nuove in `tests/skill/test_lanciatore.py`.

**Che cosa non è misurato**: una rete che non risponde affatto (pacchetti persi). La sandbox rifiuta subito anche un
indirizzo irraggiungibile; il limite lì è quello di pip, 15 s per due tentativi.

**Che cosa non si fa**: le dipendenze dentro lo ZIP. pydantic ha una parte compilata diversa per ogni versione di
Python, ezdxf porta numpy; la skill è già usata dal PO su claude.ai, dove la rete verso PyPI c'è, e i progettisti sono
nella stessa organizzazione. Se un giorno servisse una macchina senza rete, la strada è quella delle ruote (wheel)
nello ZIP con `pip install --no-index`, dentro il limite dei 200 file.

## Un difetto della distinta dal progetto reale (punto 12, I-297)

«La dicitura “compreso con la PdC” non toglie dalla distinta gli accessori di corredo (filtro a Y, pozzetti)»: vero,
`compreso_in` toglieva solo la riga della macchina in sezione A (`_apparecchiature`), e il corredo dell'accessorio si
contava lo stesso. Prova scritta prima della correzione (`tests/distinta/test_il_corredo_idronico_e_il_costo.py`,
`test_compreso_nella_pompa_di_calore_non_si_compra_due_volte`): rossa con «Filtro a Y 1" FF, maglia 500 µm» ancora in
distinta; dopo la correzione (`_corredo` salta i pezzi con `compreso_in`) verde, e la riga della pompa di calore dice
«comprende FY-01 …, comprende SO-01 …». L'accessorio resta sulla tavola e nelle giunzioni.

Il banco l'ha visto: la distinta del T1 cambiava, ma **solo nell'impronta delle regole** (`"impronta"` di
`distinta.json`, l'hash dei file delle regole, perché la nota di `corredo.json` dice adesso che `compreso_in` vale per
ogni pezzo). Le voci sono identiche; impronta registrata con `--registra`.

## Le misure

| comando | esito |
|---|---|
| `python -m pytest -q` (3.13) | `2922 passed, 15 skipped, 11 xfailed` (29 del banco, 3 del lanciatore e 1 di `compreso_in` in più) |
| `python -m ruff check src tests scripts skill/scripts` | `All checks passed!` (la CI ora controlla anche `scripts/` e `skill/scripts/`) |
| `python -m mypy` | `Success: no issues found in 127 source files` |
| release 1.15.2 | `scripts/costruisci-skill.py`: 150 file, sha256 `a65051b1430bd08b…`, controlli passati |
