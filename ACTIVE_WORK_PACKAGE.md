# REL-004 — Il DXF: la tavola che il disegnatore apre in AutoCAD

> **▶ Attivo dal 26 settembre 2026** (I-137). Finito `REL-003`, il PO ha messo prima **i pezzi che
> mancano** e per ultima la skill: «Io pensavo di chiedere prima la chiusura dei pezzi che mancano,
> in particolare manca ancora esportazione dxf. La composizione della skill vera e propria con il
> file skill.md che orchestra il tutto l'avrei tenuto per ultimo». `REL-001` torna in attesa, com'è
> scritto in `docs/plans/pacchetti/REL-001.md`.

**Da svolgere:** l'agente unico (**D-147**), con agenti paralleli in sessione (**D-152**)
**Stato:** **ATTIVO** dal 26 settembre 2026 (I-137).
**Base:** `main` a `32da9df` — `REL-003` fuso con la PR #60, tavola approvata (**I-136**).
**Ramo:** quello che l'ambiente della sessione assegna, ripartito da `main`.
**Release:** la prima release (**D-183**), il quarto dei cinque pacchetti, anteposto alla skill.
**Approvazione della fusione:** **del PO**, aprendo i DXF in AutoCAD (D-146, D-147).

Il PO:

> «Invece del file SVG è possibile avere il file in DXF? Perché DXF o meglio DWG AutoCAD lo legge,
> quindi il nostro disegnatore umano potrebbe aprire il file e fare un editing finale, se il PDF non è
> perfetto» (I-072, 17 settembre 2026)
>
> «il motore dxf da definire come esportare» (I-125, 24 settembre 2026)

---

## Dove siamo — 26 settembre 2026

- **Il DXF non esiste.** La tavola esce in SVG; il PDF lo fa uno strumento dell'ambiente
  (`scripts/to-pdf.sh`), e il PDF senza browser è di `REL-001`.
- **La valutazione del 17 settembre** (I-072) regge, e va rimisurata sui 47 simboli di oggi (allora
  erano 41): **DXF, non DWG** — il DWG è proprietario e non si scrive senza le librerie di Autodesk;
  AutoCAD apre il DXF e lo salva in DWG. I simboli sono segmenti, rettangoli, cerchi, pochi archi e
  nessuna curva di Bézier cubica: primitive che il DXF ha. L'esportazione legge **la stessa geometria**
  che alimenta l'SVG (`disegnatore-mep piano … --geometry`), quindi **non tocca posa né
  instradamento**: è un consumatore in più, accanto all'SVG.
- **Il DXF dà due cose che l'SVG non ha**: i **layer** e i **blocchi** — un simbolo definito una volta
  e inserito dove serve, così il disegnatore lo cambia in un colpo solo.
- **Il cartiglio** (`REL-002`) porta testi, tracciati e un'immagine JPEG, il logo.
- **La libreria candidata**, `ezdxf` 1.4.4, è MIT e richiede `pyparsing`, `typing_extensions`, **`numpy`**
  e **`fonttools`** (metadati del pacchetto, `pip download ezdxf`, 26 settembre 2026): `numpy` non è pura
  Python, e per la skill di `REL-001` va verificato che l'ambiente lo abbia.

---

## Le cose da fare, in quest'ordine

### 1. Come si esporta — lo decide il PO (I-125), guardando il DXF (I-138)

> **▶ 26 settembre 2026 — il PO ha risposto** (I-138): **nessun riferimento di studio**, se ne crea uno
> nuovo. Fissa quattro cose: **blocchi per i simboli**, **linee col loro tratteggio**, **frecce già
> sulle linee**, un DXF **che si apre in AutoCAD senza lavoro** — e il PDF resta quello delle tavole
> approvate. **Il resto lo propone la sessione dalle buone pratiche documentate**, ogni scelta con la sua
> fonte nel registro (come per i simboli), e **il PO lo giudica aprendo il DXF in AutoCAD**: la
> decisione si scrive dopo il suo sì, non prima.

> **▶ E la seconda risposta** (I-139): «Stampiamo sempre a colori e dxf 2013 in poi va benissimo
> (usiamo il 2020). Procedi». Quindi **colori RGB esatti** — gli stessi della tavola — e **formato
> AutoCAD 2013**. Le due ricerche della sessione (buone pratiche AutoCAD e DXF; layer, spessori e
> testi dalle norme) sono in `docs/fonti/ricerche/` con le loro fonti.

Le scelte da fare, con le fonti:

- **i layer**: per fluido, e per mandata e ritorno? simboli, testi, legenda e cartiglio separati?
- **i blocchi**: un blocco per simbolo, con che nome, e con gli attacchi segnati o no;
- **i testi**: lo stile e il carattere — AutoCAD non ha i caratteri del browser;
- **la scala e le unità**: millimetri di carta, 1:1 nello spazio modello, o una presentazione;
- **i colori e i tipi di linea**: quelli della tavola, compreso il tratteggio dell'acqua fredda;
- **il cartiglio**: dentro il DXF, come blocco, con il logo o no;
- **la versione del DXF** che l'AutoCAD dello studio apre.

### 2. Lo scrittore del DXF

Un modulo che dalla geometria della tavola scrive il DXF, **deterministico**: lo stesso piano, lo
stesso file, byte per byte. La libreria si sceglie qui, e **pura Python**, perché la skill di
`REL-001` la dovrà portare con sé.

### 3. La prova, e le tavole al PO

Le **sei tavole approvate** — i cinque impianti e l'impianto 6 — in DXF. La sessione le rilegge con
un secondo strumento e le confronta con la geometria dell'SVG; poi **il PO le apre in AutoCAD**, che
è il metro vero.

> **▶ 26 settembre 2026 — i DXF sono al PO** (`docs/collaudi/REL-004/RAPPORTO.md`): geometria riletta
> uguale alla tavola entro 10⁻⁶ mm sulle sei tavole, giro DXF → DWG → DXF con l'ODA File Converter
> identico, file uguale byte per byte fra processi diversi, suite con le stesse 46 rosse di `main`.
> Prima dell'invio la sessione ha confrontato lo scrittore con la proposta della ricerca e ha aggiunto
> i tre punti che mancavano (cartiglio in spazio carta, file che si apre sulla presentazione, colore di
> ripiego), e ha corretto due difetti trovati col giro ODA e col collaudo. **Si aspetta il PO.**

---

## Perimetro

**Dentro:** un modulo nuovo in `src/disegnatore_mep/` per il DXF, e il suo comando nella CLI;
`pyproject.toml`, se serve una libreria; `tests/**`; `docs/collaudi/REL-004/`; i documenti di stato
(`REGISTRO`, `DECISION_LOG`, piano di release, `HANDOFF.md`, `PROJECT_STATE.md`).

**Fuori:** posa e instradamento (`layout/`, `piano/`), le regole, la libreria dei simboli e il
catalogo, le istruzioni della skill, il cartiglio nel suo disegno, il PDF (`REL-001`).

---

## Criteri di accettazione

Ogni criterio si chiude con **il comando eseguito e il suo output**.

0. **Le tavole, per prime**: i DXF delle tavole approvate al PO, che li apre in AutoCAD.
1. **Come si esporta l'ha deciso il PO** (punto 1): una riga del registro, e una decisione.
2. **Il DXF è la tavola**: la geometria riletta dal DXF coincide con quella dell'SVG, entro una
   tolleranza misurata.
3. **Layer, blocchi, testi e scala** come deciso al punto 1.
4. **Deterministico**: una prova pretende che lo stesso piano dia lo stesso DXF.
5. **La suite**: nessuna rossa nuova rispetto alle 46 di `main`; zero `skip` e zero `xfail` nuovi;
   `ruff check src tests examples scripts` e `mypy` verdi.

## Dopo `REL-004`

Gli altri pezzi che mancano, poi la skill (I-137): **il PDF senza browser** — oggi dentro `REL-001`,
e per l'assunzione della sessione su I-137 viene prima della skill, come pezzo a sé —; poi **`REL-001`
la skill**, con il suo `SKILL.md`; per ultimo **`REL-005`**, il pacchetto della release.

## Consegna

Una PR verso `main`, **fusa solo dopo che il PO ha aperto i DXF e ha detto di sì**. Rapporto in
`docs/collaudi/REL-004/RAPPORTO.md`, con le tavole in testa.
