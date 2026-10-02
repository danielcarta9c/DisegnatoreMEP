# BETA-001 — La beta della 1.2: il debug sulle tavole dei collaboratori

> **▶ Il prossimo, per l'ordine del PO** — «distribuisco la release 1.2 ai miei collaboratori ed entriamo nella
> fase di beta testing e debug» (I-181); «prepara il workpack per la prossima sessione» (I-183). Scritto il
> 2 ottobre 2026, a PR #68 fusa. **Si parte dal punto 0**, in un messaggio solo al PO.

**Da svolgere:** l'agente unico (**D-147**), con agenti paralleli in sessione (**D-152**)
**Stato:** **PROSSIMO** — si avvia quando il PO apre la sessione.
**Base:** `main` dopo la fusione della PR #68.
**Ramo:** quello che l'ambiente della sessione assegna, ripartito da `main`.
**Approvazione della fusione:** **del PO**, e si dà guardando le tavole (D-146, D-147).
**`REL-005` è chiuso con la 1.2** (D-198): la release è `releases/archive/DisegnatoreMEP-v1.2.0.zip`. La storia del
pacchetto è in `docs/plans/pacchetti/REL-005.md`.

---

## Dove siamo — misurato il 2 ottobre 2026

- **La skill 1.2 è dai collaboratori del PO.** Lo ZIP distribuito è la release 1.2.0,
  `releases/latest/DisegnatoreMEP-v1.2.0.zip` (sha256 `fa9e410a7e994f66`), con la copia numerata in `releases/archive/`. È stato costruito prima della
  pulizia: lo ZIP che `main` costruisce oggi è più leggero (760 kB contro 822) ma **disegna le stesse tavole**,
  byte per byte. Non c'è niente da ridistribuire finché non arriva una correzione.
- **La suite è verde**: `1967 passed, 15 skipped, 10 xfailed`, in 4 minuti e mezzo; `ruff` e `mypy` verdi.
  **Da qui una rossa è un difetto**, non rumore di fondo.
- **Il solutore non c'è più** (D-197). Le prove del motore leggono un piano: quelli approvati di
  `docs/collaudi/DRAW-018/prova-camera-pulita-2026-09-24/`, o quelli tradotti in `tests/layout/piani/`. La via
  senza piano (`draw`) resta nel codice, ma la sua qualità non la garantisce nessuno (D-151).
- **Gli strumenti per lavorare** ci sono già, provati sulla prova del PO:
  - `docs/collaudi/REL-005/prova-po-1/` — come si ricostruisce **anonima** una tavola vera (grafo e piano dal
    DXF), e come si mostrano al PO le alternative;
  - `docs/collaudi/REL-005/prova-po-1/tavole_di_prova.py` — le sette tavole di prova approvate, rifatte col codice
    corrente;
  - `docs/collaudi/REL-005/pulizia-del-solutore/uscite.sh` e `confronta.sh` — **la misura di regressione**: 55
    uscite generate prima e dopo, confrontate byte per byte.
- **Il primo difetto è già noto** (I-182): sulla tavola 1 dal piano due valvole che isolano stanno a 10 mm dal
  proprio attacco, contro i 2,5–5 di D-120.

## 0. Quello che serve dal PO, in un messaggio solo

1. **Le tavole dei collaboratori**, man mano che arrivano: il DXF, **il testo esatto** che hanno scritto alla
   skill, le risposte che hanno dato alle sue domande, e che cosa non va, con parole loro. Senza almeno una, il
   punto 3 resta fermo e la sessione lavora sul punto 1.
2. **La numerazione delle consegne in beta.** *Proposta della sessione:* `1.2.1`, `1.2.2`… a ogni gruppo di
   correzioni fuso e consegnato ai collaboratori; `1.3` se cambia il comportamento visibile in modo che il
   collaboratore debba saperlo, come un simbolo nuovo. Lo decide il PO.
3. **Le domande di contenuto aperte**, con la proposta della sessione per ciascuna:
   - **lo scarico del volano a due attacchi** in serie sul ritorno esce rosso (colore base del fluido). *Proposta:*
     prende il ritorno, perché il volume è acqua di ritorno;
   - **le sette domande** del rapporto di `REL-001` §6.1.

## Le cose da fare, in quest'ordine

### 1. I-182 — le valvole di D-120 fuori misura sulla tavola dal piano

- **Misurare prima di toccare**: su tutte le sette tavole di prova e sulla tavola D, l'elenco di ogni valvola che
  isola un pezzo manutenibile e sta fuori dai 2,5–5 mm dal suo attacco.
- **Classificare** (architettura §6): difetto del motore (la posa degli organi in linea) o del piano.
- **Se è del motore, si cura nel motore**, con una prova che fallisce senza la correzione. Le tavole cambiano,
  ed è il punto: prima e dopo, al PO.
- **La prova di accettazione torna sul piano**: `test_tavola_1_le_valvole_d120_stanno_sull_attacco` legge di
  nuovo `_tavola_1()`, e `_tavola_1_senza_piano` esce se non serve più a nessuno.
- **D-158**: ogni vincolo di posa ha un rilievo sulla tavola consegnata. Se D-120 non ce l'ha nel preflight, si
  scrive.

### 2. Il modulo della segnalazione, per i collaboratori

Una pagina, `docs/beta/SEGNALAZIONE.md`, che il PO inoltra ai collaboratori:
- che cosa mandare: il DXF o il PDF, il testo scritto alla skill, le risposte alle sue domande, che cosa non va;
- con che modello hanno usato la skill: con Haiku il piano non si compone (`REL-001`);
- che i dati del cliente restano nella conversazione, e nel repository non entrano.

È corta, ed è la prima cosa che il PO può usare subito.

### 3. Ogni tavola dei collaboratori: il ciclo della prova del PO

Per ciascuna, come in `docs/collaudi/REL-005/prova-po-1/`:

- **si registra il giorno stesso** (I-nnn, una riga per rilievo, rule 3 del registro);
- **si legge il DXF e non si copia**: grafo e piano si ricostruiscono **anonimi**, in
  `docs/collaudi/BETA-001/<nn>-<parola>/`, e la tavola si rifà identica prima di toccare niente;
- **ogni difetto si classifica**:
  - Capire (il grafo);
  - Comporre (le istruzioni del piano);
  - il motore;
  - la libreria dei simboli;
  - il contenuto MEP, che è una domanda al PO con la proposta;
- **si cura con una prova** che fallisce senza la correzione;
- **le tavole al PO**: quella com'era, quella dopo, e le alternative quando la cura è una scelta, come A, B, C e D
  della prova del PO.

### 4. Le consegne in beta

Quando un gruppo di correzioni è fuso:
- la skill si costruisce da `main` (`scripts/costruisci-skill.py`);
- la versione sale come il PO ha deciso (punto 0.2), in `pyproject.toml`, nel pacchetto e in `SKILL.md`;
- lo ZIP va in `releases/latest/DisegnatoreMEP-v<versione>.zip`, che sostituisce il precedente, e in
  `releases/archive/`, dove resta; poi al PO. `tests/test_le_release.py` tiene insieme il numero del pacchetto,
  quello in `SKILL.md` e il nome dello ZIP.

## Perimetro

**Dentro:**
- le istruzioni della skill (`skill/**`), per una rottura misurata, con la parola del PO dove è contenuto;
- il motore (`src/**`), per un difetto misurato;
- la libreria (`examples/graphics/build_symbols.py` → `assets/symbols/`), con la forma approvata dal PO sulle
  tavole;
- `tests/**`; `docs/collaudi/BETA-001/`; `docs/beta/`;
- `pyproject.toml`, la versione e `releases/`;
- il registro, il registro delle decisioni (come proposte), `HANDOFF.md`, questo file.

**Fuori:**
- la libreria certificata — la matrice fonti, forma, porte e ingombri — che si fa quando la beta smette di
  toccare i simboli;
- **i dati dei clienti, in qualunque file**;
- un contenuto MEP deciso dalla sessione.

## Le regole che in beta valgono di più

- **Il repository è pubblico.** Un DXF di un collaboratore porta nome e indirizzo del cliente: si legge nella
  conversazione, non si committa, non si cita. Prima di ogni commit si cerca nel diff il nome e l'indirizzo
  ricevuti.
- **Una rossa è un difetto.** La suite resta a zero rosse a ogni PR; niente `skip`, niente `xfail` nuovi.
- **Ogni PR dice quali tavole cambia.** `uscite.sh` su `main` e sul ramo, poi `confronta.sh`: ogni file che
  cambia ha la sua ragione nel rapporto, e le tavole che cambiano vanno al PO.

## Criteri di accettazione — per ogni PR della beta

Ogni criterio si chiude con **il comando eseguito e il suo output**.

0. **Le tavole, per prime**: quelle che la PR cambia, prima e dopo, al PO. Se una tavola di un collaboratore
   non si rifà, è la prima cosa che si dice.
1. **La suite**: `0 failed`; nessuno `skip` e nessuno `xfail` nuovi; `ruff check src tests` e `mypy src` verdi.
2. **La regressione**: l'output di `confronta.sh` fra `main` e il ramo, con ogni file cambiato spiegato.
3. **Ogni correzione ha la sua prova**, rossa sul commit di partenza e verde sul ramo.
4. **Ogni input del PO è nel registro** il giorno in cui arriva.
5. **Nessun dato di cliente nel diff**: il comando di ricerca e il suo output vuoto.

## Consegna

Una PR verso `main` per ogni gruppo di correzioni, **fusa solo dopo che il PO ha visto le tavole e ha detto di
sì**. Rapporto in `docs/collaudi/BETA-001/RAPPORTO.md`, con le tavole in testa. A ogni fusione:
- `HANDOFF.md` aggiornato;
- se il PO lo vuole, la consegna `1.2.x` del punto 4.
