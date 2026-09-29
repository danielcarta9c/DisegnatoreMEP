# REL-008 — Le scritte della tavola più grandi: 9 punti, mai sotto 8

> **▶ Consegnato il 29 settembre 2026**: le sette tavole a 9 punti sono al PO (`docs/collaudi/REL-008/RAPPORTO.md`). Si fonde solo dopo il suo sì.
>
> **▶ Attivo dal 29 settembre 2026** (I-159). Fuso `REL-007`, i diametri, con le tavole approvate dal PO —
> «Approvato tutto, pr e metti su main» (I-158) —, il PO ha chiesto nello stesso messaggio una REL nuova,
> prima delle altre. *Assunzione della sessione:* dopo, l'ordine di prima — il PDF senza browser, `REL-001`
> la skill, per ultimo `REL-005`.

**Da svolgere:** l'agente unico (**D-147**), con agenti paralleli in sessione (**D-152**)
**Stato:** **CONSEGNATO AL PO** il 29 settembre 2026, in attesa del suo giudizio sulle tavole — rapporto `docs/collaudi/REL-008/RAPPORTO.md`, tavole in `docs/collaudi/REL-008/tavole/`, regole in **D-194** (proposta). ATTIVO dal 29 settembre 2026 (I-159); il PO ha deciso lo stesso giorno che cosa si sacrifica e che cosa no (I-160 … I-162) e la forma del richiamo, con la spalla (I-163).
**Base:** `main` dopo la fusione di `REL-007`.
**Ramo:** quello che l'ambiente della sessione assegna, ripartito da `main`.
**Release:** la prima release (**D-183**), aggiunto dal PO il 29 settembre (I-159).
**Approvazione della fusione:** **del PO**, guardando le tavole (D-146, D-147).

Il PO:

> «Poi facciamo una nuova REL. vorrei provare ad aumentare il font utilizzato per tutte le scritte. Al
> momento mi sembra poco leggibile. Adesso mi sembra che sta a circa 5, dovrebbe essere almeno 8 o meglio
> 9.» (I-159, 29 settembre 2026)

---

## Dove siamo — 29 settembre 2026

- **Il «circa 5» del PO è misurato.** Le scritte del disegno — le sigle, i dati del progettista accanto ai
  pezzi, i DN, la legenda e la sua nota, la tabella delle apparecchiature, la riga d'intestazione, gli
  indirizzi della verifica — hanno **un corpo solo**: `GraphicStandard.text_small_mm`, **1,8 mm**, cioè
  **5,1 pt** (`src/disegnatore_mep/graphics/standard.py`). A4, A3 e A2 lo condividono: la scala di stampa
  è invariante (ADR 0003). **9 pt sono 3,18 mm, 8 pt 2,82 mm**: le scritte crescono di 1,76 volte.
- **Il corpo è anche in una decisione approvata**: la tabella delle apparecchiature ha «testi di 1,8 mm come
  legenda e sigle, in Arial» e «righe di 5 mm» (**D-192**, punto 8). La disposizione del PO la cambia per il
  corpo: una decisione nuova, al punto 1.
- **Il cartiglio Nove C** (`REL-002`) ha i suoi corpi, in punti, dal modello dello studio, e li riduce da
  sé quando un testo non entra nel suo campo (`graphics/cartiglio.py`). Quali siano sotto gli 8 pt si
  misura al punto 1.
- **Il corpo decide lo spazio.** La posa delle sigle e dei DN misura il riquadro di ogni scritta
  (`layout/labels.py`, `layout/diametri.py`); la legenda sta in una fascia di 50 mm (`graphics/frame.py`,
  `LEGEND_WIDTH_MM`); la tabella è larga quanto i suoi testi e alta cinque millimetri a riga; il preflight
  misura le scritte per le sovrapposizioni e i margini; il DXF scrive l'altezza delle maiuscole. **A 9 pt
  ogni scritta occupa quasi il doppio**: sigle e DN che oggi entrano possono non entrare, la tabella si
  allarga verso il disegno, la legenda va a capo più spesso, e il foglio può non bastare.
- **Il carattere.** Il DN e la tabella dichiarano Arial; sigle, legenda e rimandi non dichiarano niente, e
  il PDF li stampa con le grazie (I-122). Che il carattere voluto sia l'Arial è un'assunzione detta al PO
  il 26 settembre, senza obiezioni.

---

## Le cose da fare, in quest'ordine

### 1. Che cosa cresce, e quanto — con il PO

Il PO ha detto «tutte le scritte», «almeno 8 o meglio 9». Restano da fissare con lui, perché sono
convenzione grafica:

- **il corpo**: 9 pt per tutte le scritte del disegno, e 8 pt come minimo dove 9 non entra — o 9 pt e
  basta;
- **il cartiglio**: se i suoi testi sotto gli 8 pt crescono anche loro, o se il modello dello studio resta
  com'è;
- **il carattere**: Arial per tutte le scritte, come il DN, la tabella, il cartiglio e il DXF.

Le risposte vanno nel registro, e il corpo in una decisione che supera D-192 per il punto 8.

### 2. Il corpo nuovo, in un punto solo

`text_small_mm` al corpo deciso, e tutto ciò che ne dipende lo legge da lì: i testi più grandi
(`text_normal_mm`, `text_title_mm`) restano più grandi; nessun numero nuovo anonimo nel codice.

### 3. Lo spazio che serve alle scritte

Sigle, DN, legenda, tabella, intestazione, velo della verifica: ognuno trova posto col corpo nuovo, oppure
lo dice. Lo stacco del DN dalla linea, i margini delle etichette, la fascia della legenda e le righe della
tabella si ricavano dal corpo, non restano quelli tarati a 1,8 mm. Nel DXF gli stessi testi, con le altezze
nuove.

### 4. La prova sulle tavole approvate

Le sei tavole approvate e la tavola in retrofit, rieseguite dai loro grafi e piani con i dati di prova di
`REL-002`, `REL-006` e `REL-007`, **accanto a quelle di `REL-007`**, perché il PO veda la differenza.

---

## Perimetro

**Dentro:** il corpo del testo e tutto ciò che si impagina col testo — `graphics/` (standard, tavola, DXF,
tabella, legenda), la posa delle scritte (`layout/labels.py`, `layout/diametri.py`, `layout/addresses.py`),
il preflight che misura le scritte; il cartiglio solo se il PO lo decide al punto 1; `tests/**`;
`docs/collaudi/REL-008/`; i documenti di stato.

**Fuori:** la posa dei simboli e l'instradamento delle linee; le regole; la libreria dei simboli e il
catalogo; il PDF senza browser. Se le scritte nuove non entrano senza spostare il disegno, **lo si dice al
PO con le tavole**, non si sposta il disegno di nascosto.

---

## Criteri di accettazione

Ogni criterio si chiude con **il comando eseguito e il suo output**.

0. **Le tavole, per prime**: le sei tavole approvate e la retrofit con le scritte nuove, in PDF e in DXF,
   accanto a quelle di `REL-007`.
1. **Il corpo lo ha fissato il PO** (punto 1): una riga del registro e una decisione.
2. **Nessuna scritta sotto il minimo**: su ogni tavola, nell'SVG e nel DXF, ogni testo misurato.
3. **Niente si tocca**: scritte contro simboli, linee, altre scritte, tabella e cartiglio; nessuna sigla e
   nessun DN persi rispetto a `REL-007`, o detti uno per uno.
4. **Il disegno non si muove**, o si dice dove e perché: simboli e tratte confrontati con le tavole di
   `REL-007`, e il formato del foglio.
5. **Deterministico**, e **la suite**: nessuna rossa nuova rispetto a `main`; zero `skip` e zero `xfail`
   nuovi; `ruff` e `mypy` verdi.

## Consegna

Una PR verso `main`, **fusa solo dopo che il PO ha visto le tavole e ha detto di sì**. Rapporto in
`docs/collaudi/REL-008/RAPPORTO.md`, con le tavole in testa.
