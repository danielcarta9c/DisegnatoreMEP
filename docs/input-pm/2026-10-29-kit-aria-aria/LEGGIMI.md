# Kit per la sessione di sviluppo — aria-aria, regolazione e distinta materiali

Tutto quello che è stato fatto il 29/10/2026 su un impianto canalizzato reale, con i dati del committente tolti
(caso di prova **AA-01**), per portarlo nel repository DisegnatoreMEP.

## Da leggere per primi

1. `RAPPORTO.md` — la sessione intera: le richieste del PO testuali, il percorso, cosa è della skill e cosa è stato
   aggiunto, l'estensione pezzo per pezzo, i comportamenti del motore scoperti, le regole di dimensionamento e di
   distinta, la proposta **REL-012** con le decisioni che sono del PO.
2. `tavole/AA-01_M.02_anteprima.png` — la tavola di riferimento, da guardare prima dei numeri (D-146).
3. `per-il-repo/ESITO-DEI-TEST.md` — la patch applicata a `main` 1.5.0 e i test che cambia.
4. `REVISIONE-INDIPENDENTE.md` — i 31 rilievi del revisore e cosa ne è stato fatto.

## Cosa c'è

| cartella | contenuto |
|---|---|
| `tavole/` | **M.02** schema funzionale A2 (PDF, DXF, SVG, anteprime, rilievi del comando); **M.03** pianta dei posizionamenti e dei tracciati 1:50 (PDF, anteprima); **computo Excel** per l'installatore |
| `per-il-repo/` | con l'albero del repository: `assets/symbols/` (11 simboli nuovi + il nome del diffusore), `examples/layout/catalog/` (12 voci), `naming/` (`media.json`, `families.json`), `src-estensione.patch` (8 file del motore), `ESITO-DEI-TEST.md` |
| `lavoro/` | gli script della sessione, che rifanno tutto da zero: `rifai.sh` |
| `lavoro/skill-orig/` | la skill **1.4.1** su cui l'estensione è stata fatta |

### `lavoro/`, file per file

| file | che cosa fa |
|---|---|
| `estendi.py` | applica l'estensione a una copia di `skill-orig`: simboli, catalogo, fluidi, famiglie e le sostituzioni nel codice |
| `dimensionamento.py` | rilievo dal catastale, percorsi, regola delle lunghezze, dimensionamento di aria, frigo, condensa, elettrico e bus, **distinta materiali**, note e attività. Scrive `dim.json`, unica fonte dei numeri |
| `grafo.py` | scrive il grafo dai numeri, con le scritte «Ø · L» sulle tubazioni |
| `piano.json` | la posa della M.02, con le ragioni |
| `tabelle.py` | tabella delle tratte, note, attività e computo sulla M.02 (SVG, PDF e DXF) |
| `pianta.py` | la tavola M.03 sul catastale `pt_crop.png` |
| `excel.py` | il computo Excel: a corpo, solo valori |
| `riferimento_carichi_estivi.py` | il calcolo orario dei carichi estivi per zona da cui vengono le portate |
| `rifai.sh` | la sequenza completa: da `lavoro/`, `./rifai.sh` |

Per rifare le tavole serve Python 3.11 o più recente con pydantic 2, ezdxf, pypdfium2, Pillow e openpyxl. Le tavole
del kit sono state rigenerate così, da zero, e escono con zero rilievi bloccanti.

## Come partire in Claude Code

Copia il kit nel repository, per esempio in `docs/input-pm/2026-10-29-kit-aria-aria/` (è un input del PO), e dai alla
sessione un messaggio come questo:

> Ti do un input del PO: `docs/input-pm/2026-10-29-kit-aria-aria/`. Leggi `LEGGIMI.md` e `RAPPORTO.md`, guarda la
> tavola `tavole/AA-01_M.02_anteprima.png`. Voglio portare nella skill l'aria-aria, la regolazione, l'elettrico e la
> nuova funzione «distinta materiali» (materiali per l'installatore), come proposto nel §9 del rapporto. Prima di
> scrivere il pacchetto REL-012 portami le decisioni del §9 in un messaggio solo, con la tua proposta per ciascuna.
> L'accettazione è la M.02 del kit: rigenerata dalla skill, stessa tavola, zero rilievi bloccanti.

Le decisioni che il pacchetto chiede al PO sono quattro, e sono nel §9 del rapporto:
- dimensionamento e distinta dentro una skill che oggi «non progetta»;
- i simboli, da approvare sulla tavola;
- la precedenza rispetto a REL-011;
- la tavola M.03.

## Cosa è stato tolto

- Nome, indirizzo e codice di commessa del committente: al loro posto ci sono «Committente (dati omessi)»,
  «Indirizzo omesso» e «AA-01».
- La pagina intera del catastale, con le intestazioni: c'è solo il ritaglio della pianta.
- Le offerte, i prezzi e i dati commerciali.

Il PO resta nel cartiglio come verificatore. Il repository è pubblico: prima di copiare il kit, una ricerca dei dati
del committente sul kit intero restituisce zero risultati.
