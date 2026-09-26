# REL-004 — il DXF: rapporto

**Pacchetto:** `REL-004` (`ACTIVE_WORK_PACKAGE.md`) · **Ramo:** `claude/missing-symbols-uuzbhb` ·
**Base:** `main` a `32da9df` (`REL-003` fuso con la PR #60)

> **Le tavole, per prime**
>
> **Le sei tavole approvate in DXF**, in [`dxf/`](dxf/): i cinque impianti di `DRAW-018` (tavole 1–5)
> e l'impianto 6 di `REL-003` (tavola 6), col cartiglio compilato coi dati di prova di `REL-002`.
> Accanto ai DXF c'è il **logo** (`Cartiglio_NoveC_A3-logo.jpg`): il DXF lo collega, non lo contiene, e
> va tenuto **nella stessa cartella**.
>
> **Si giudicano aprendole in AutoCAD** (I-138): è l'unico metro vero, e qui AutoCAD non c'è. Per chi non
> l'ha sottomano, in [`rese/`](rese/) c'è la presentazione di ciascun DXF resa da ezdxf a foglio intero:
> la geometria è quella, i testi no — qui non c'è Arial.
>
> ⏳ **In attesa del PO**: la fusione aspetta che le abbia aperte e abbia detto di sì.

| tavola | formato | file | resa |
|---|---|---|---|
| 1 — due pompe di calore in parallelo con accumulo combinato | A3 | [`tavola-1.dxf`](dxf/tavola-1.dxf) | [`tavola-1.png`](rese/tavola-1.png) |
| 2 — pompa di calore con deviazione fra climatizzazione e ACS | A3 | [`tavola-2.dxf`](dxf/tavola-2.dxf) | [`tavola-2.png`](rese/tavola-2.png) |
| 3 — pompa di calore diretta su pavimento radiante, ACS separata | A3 | [`tavola-3.dxf`](dxf/tavola-3.dxf) | [`tavola-3.png`](rese/tavola-3.png) |
| 4 — sistema ibrido con pompa di calore e caldaia a condensazione | A3 | [`tavola-4.dxf`](dxf/tavola-4.dxf) | [`tavola-4.png`](rese/tavola-4.png) |
| 5 — tre pompe di calore in cascata con tre circuiti secondari e ACS | A2 | [`tavola-5.dxf`](dxf/tavola-5.dxf) | [`tavola-5.png`](rese/tavola-5.png) |
| 6 — centrale ibrida con pompa di calore di alta potenza, caldaia modulare e solare termico | A2 | [`tavola-6.dxf`](dxf/tavola-6.dxf) | [`tavola-6.png`](rese/tavola-6.png) |

## 1. Che cosa c'è

- **Lo scrittore**, `src/disegnatore_mep/graphics/dxf.py`: dalla stessa geometria che disegna l'SVG
  scrive il DXF, con le stesse funzioni che decidono dove stanno scavalli, pallini e frecce. Non tocca
  posa né instradamento.
- **Che cosa contiene il DXF**, con le fonti di ogni scelta nel rapporto della ricerca
  (`docs/fonti/ricerche/reports/DXF per AutoCAD.md`, SRC-047):
  - **formato AutoCAD 2013** (I-139), millimetri;
  - **lo schema nello spazio modello a 1:1**, **squadratura e cartiglio nello spazio carta** della
    presentazione `A3` o `A2`, che ha una finestra 1:1 bloccata ed è pronta per la stampa; **il file si
    apre sulla presentazione**;
  - **un layer per rete** — fluido e verso — col **colore esatto della tavola** (I-139), il tratteggio e
    lo spessore; poi simboli, sigle, testi, legenda, cartiglio; nomi dello US National CAD Standard e
    **descrizione in italiano**;
  - **un blocco per simbolo** (`NoveC_…`), inserito ruotato e specchiato come nella tavola, con la
    geometria su layer 0 e DaBlocco; **le frecce del verso** come blocco sul layer della loro rete (I-138);
  - **i tratteggi** definiti in millimetri come nella tavola, continui sui vertici;
  - **testi in Arial**, con l'altezza tarata sulle maiuscole.
- **Il comando**: `disegnatore-mep draw … --dxf` e `disegnatore-mep piano … --dxf` scrivono il DXF
  accanto all'SVG, e con il cartiglio il logo. La libreria è `ezdxf` 1.4.4, MIT, nel gruppo facoltativo
  `dxf` di `pyproject.toml`; senza, il comando lo dice e si ferma.
- **Le prove**: `tests/graphics/test_dxf.py`, 20 prove, e una in `tests/test_cli.py`.

## 2. Le misure

**Le sei tavole** — `PYTHONPATH=src python3 docs/collaudi/REL-004/collaudo.py <cartella>`:

```
tavola     formato audit           entita blocchi layer  geometria
tavola-1   A3      nessun errore      232      20    12  tratte 46/46 uguali, simboli 43/43 uguali
tavola-2   A3      nessun errore      240      23    12  tratte 46/46 uguali, simboli 43/43 uguali
tavola-3   A3      nessun errore      236      22    12  tratte 43/43 uguali, simboli 41/41 uguali
tavola-4   A3      nessun errore      262      24    12  tratte 53/53 uguali, simboli 48/48 uguali
tavola-5   A2      nessun errore      432      29    13  tratte 108/108 uguali, simboli 96/96 uguali
tavola-6   A2      nessun errore      356      29    14  tratte 87/87 uguali, simboli 79/79 uguali
```

«Uguali» vuol dire: ogni tratta di ogni rete, riletta dal DXF sul layer della sua rete, e ogni simbolo,
come inserimento del suo blocco — punto, rotazione, specchio —, **coincidono con la tavola entro un
milionesimo di millimetro**.

**Il giro con l'ODA File Converter** (DXF → DWG AutoCAD 2018 → DXF), che legge e scrive DWG con le
librerie di molti programmi CAD — `PYTHONPATH=src python3 docs/collaudi/REL-004/giro_oda.py <AppRun> <cartella>`:

```
DXF -> DWG, uscita 0
DWG -> DXF, uscita 0
tavola-1   DWG AC1032  ritorno identico  resa 1653x1169, pixel diversi 0
tavola-2   DWG AC1032  ritorno identico  resa 1653x1169, pixel diversi 0
tavola-3   DWG AC1032  ritorno identico  resa 1653x1169, pixel diversi 36
tavola-4   DWG AC1032  ritorno identico  resa 1653x1169, pixel diversi 3
tavola-5   DWG AC1032  ritorno identico  resa 2338x1653, pixel diversi 0
tavola-6   DWG AC1032  ritorno identico  resa 2338x1653, pixel diversi 6
```

«Identico» su layer, entità dei due spazi, colori esatti, blocchi, inserimenti, immagini, intestazione,
presentazione attiva, impostazione di stampa, finestre e stili di testo. Non si confronta il colore
d'indice di ripiego, che ODA ricalcola col suo criterio. I pixel diversi sono sfumature di bordo: due
livelli di grigio su qualche decina di pixel.

**Deterministico**: lo stesso piano dà lo stesso file byte per byte, anche fra processi diversi — la
tavola 6 scritta con cinque semi di hash diversi (`PYTHONHASHSEED` 0–4) dà cinque file con la stessa
impronta, e le sei tavole di due esecuzioni del collaudo coincidono.

**La suite** — `python -m pytest -q`: `46 failed, 1809 passed, 24 skipped, 12 xfailed`. Le 46 rosse
sono **le stesse di `main`**, nome per nome; skip e xfail invariati. `ruff check src tests examples
scripts` e `mypy src`: verdi.

## 3. Che cosa ho trovato guardando, e ho corretto prima dell'invio

- **Tre punti della proposta della ricerca non c'erano** nella prima versione dello scrittore: il
  cartiglio stava nello spazio modello, il file si apriva sul modello, e accanto al colore esatto non
  c'era il colore d'indice di ripiego. Aggiunti. Spostare il cartiglio nello spazio carta **non ha
  cambiato un pixel** della presentazione: le rese di prima e di dopo, sulle sei tavole, coincidono.
- **La finestra principale della presentazione stava su un layer che non esisteva** (`VIEWPORTS`, lo
  mette ezdxf): l'audit non lo vedeva, il giro con ODA sì. Ora sta sul layer 0, e una prova pretende che
  ogni entità stia su un layer definito.
- **Lo stesso piano dava due file diversi in due esecuzioni**: ezdxf mette in fila le classi del file
  scorrendo un insieme, il cui ordine cambia da un processo all'altro. La prova byte per byte non lo
  vedeva, perché scriveva due volte nello stesso processo. Ora le classi sono in ordine di nome, e una
  prova lo pretende.

## 4. Che cosa resta da vedere in AutoCAD

Quello che nessuna misura qui può dire:

1. che il file **si apra sulla presentazione** e la tavola sia quella del PDF — colori, tratteggi, frecce,
   cartiglio, **logo al suo posto**;
2. che i **testi Arial** abbiano l'altezza della tavola (la taratura sulle maiuscole è misurata sul
   carattere gemello, non su Arial in AutoCAD);
3. che **la stampa in PDF** esca al formato giusto: la carta `ISO_full_bleed_A3_(420.00_x_297.00_MM)`
   segue lo schema dei nomi di `DWG To PDF.pc3`, ma non è stata trovata scritta in una pagina Autodesk;
4. che nel gestore dei layer si veda **la descrizione italiana**.

## 5. Criteri di accettazione

| # | criterio | stato |
|---|---|---|
| 0 | le tavole al PO, che le apre in AutoCAD | ⏳ DXF inviati; **in attesa del PO** |
| 1 | come si esporta l'ha deciso il PO | ⏳ registro e decisione **dopo il suo sì** (I-138) |
| 2 | il DXF è la tavola, entro una tolleranza misurata | ✅ §2: tratte e simboli uguali entro 10⁻⁶ mm, sei tavole su sei |
| 3 | layer, blocchi, testi e scala come deciso | ⏳ come proposto in SRC-047; decisi con il sì del PO |
| 4 | deterministico | ✅ §2, e due prove: stesso processo, e classi in ordine |
| 5 | la suite, ruff e mypy | ✅ §2 |
