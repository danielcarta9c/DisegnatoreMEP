# Il pianificatore sul grafo completo — 23 settembre 2026

> ✅ **Approvate dal PO il 23 settembre 2026** (**I-109**): «Si le approvo assolutamente vanno
> benissimo! Hanno proprio l'aspetto di tavole professionali!». Sono le tavole che il
> pianificatore ha composto **da solo**, sul grafo **completo** — macchine, collettori e tutto il
> corredo. Il PO vede **piccoli difetti**, che apre dopo la fusione: da qui in poi si parla di
> migliorie e piccole correzioni.

**Che cos'è.** Cinque agenti avviati da zero, uno per impianto, che ricevono **soltanto**
`skill/comporre/ISTRUZIONI.md` (versione di `1121a8c`), `CONSEGNA.md`, il grafo completo e i
manifesti dei simboli, e scrivono il piano. Più due agenti sugli **scheletri** 2 e 3, per chiudere
la serie del 21 settembre. Il mandato è [`mandato.md`](mandato.md). **Vietati** il repository, i
piani a mano, le tavole già fatte, il registro. Ogni agente dichiara in fondo al rapporto i file
che ha aperto: nessuno è uscito dalla propria cartella.

**Il motore degli agenti era congelato a `1121a8c`.** Gli agenti hanno trovato cinque difetti del
motore; la sessione li ha verificati e corretti (RAPPORTO §7). **Le tavole di questa cartella sono
rigenerate con il motore corretto**, e la misura qui sotto è quella della sessione (D-152), non
quella dichiarata dagli agenti. La geometria non è cambiata su nessuna: sono cambiati colori di
poche tratte, gli specchi degli organi con un verso e le righe della legenda.

**Che cosa NON è.** Non è prodotto e **non si corregge a mano**: è la misura del pianificatore a
questa data. Un piano migliore si ottiene **rifacendo la prova** con istruzioni migliori.

## Le tavole

| impianto | tavola | piano | grafo |
|---|---|---|---|
| 1 | [`tavola-completo-1.pdf`](tavola-completo-1.pdf) | `piano-completo-1.json` | `grafo-completo-1.json` |
| 2 | [`tavola-completo-2.pdf`](tavola-completo-2.pdf) | `piano-completo-2.json` | `grafo-completo-2.json` |
| 3 | [`tavola-completo-3.pdf`](tavola-completo-3.pdf) | `piano-completo-3.json` | `grafo-completo-3.json` |
| 4 | [`tavola-completo-4.pdf`](tavola-completo-4.pdf) | `piano-completo-4.json` | `grafo-completo-4.json` |
| 5 | [`tavola-completo-5.pdf`](tavola-completo-5.pdf) | `piano-completo-5.json` | `grafo-completo-5.json` |
| scheletro 2 | [`tavola-scheletro-2.pdf`](tavola-scheletro-2.pdf) | `piano-scheletro-2.json` | `grafo-scheletro-2.json` |
| scheletro 3 | [`tavola-scheletro-3.pdf`](tavola-scheletro-3.pdf) | `piano-scheletro-3.json` | `grafo-scheletro-3.json` |

Per rifarle: `disegnatore-mep piano grafo-completo-N.json --piano piano-completo-N.json
--catalog examples/layout/catalog --symbols assets/symbols --naming naming --out <cartella>`, e
`scripts/to-pdf.sh` sull'SVG.

## La misura, rieseguita dalla sessione

| impianto | | piano a mano (`PROVA-PIANO/`) | **piano dell'agente** |
|---|---|---|---|
| **1** — due PDC e accumulo combinato | formato | A2 | **A3** |
| | cedute / bloccanti | 0 / 0 | **0 / 0** |
| | rilievi | 7 — A4 6, B11 1 | **1** — B11 |
| | spezzate piegate / pieghe / incroci | 3 / 4 / 1 | 3 / 4 / 1 |
| **2** — PDC, deviatrice e ACS | formato | A2 | **A3** |
| | cedute / bloccanti | 0 / 0 | **0 / 0** |
| | rilievi | 9 — B1 1, A4 7, B11 1 | **1** — B11 |
| | spezzate piegate / pieghe / incroci | 6 / 10 / 2 | **3 / 4 / 1** |
| **3** — PDC diretta su pavimento | formato | A2 | **A3** |
| | cedute / bloccanti | 0 / **2** | **0 / 0** |
| | rilievi | 10 — B1 3, A4 7 | **2** — B10 1, A4 1 |
| | spezzate piegate / pieghe / incroci | 5 / 10 / 1 | **3 / 3** / 2 |
| **4** — ibrido PDC e caldaia | formato | A2 | **A3** |
| | cedute / bloccanti | 0 / 0 | **0 / 0** |
| | rilievi | 11 — B1 3, A4 7, B11 1 | **2** — B11 2 |
| | spezzate piegate / pieghe / incroci | 8 / 14 / 3 | **5 / 6 / 2** |
| **5** — tre PDC in cascata | formato | **non esce** | **A2** |
| | cedute / bloccanti | — | **0 / 0** |
| | rilievi | — | **3** — B1 1, B9 1, B11 1 |
| | spezzate piegate / pieghe / incroci | — | 10 / 13 / 5 |
| scheletro 2 | | — | A4 · 0 / 0 · 0 rilievi · 3 / 4 / 1 |
| scheletro 3 | | — | A4 · 0 / 0 · 1 rilievo (B10) · 3 / 3 / 1 |

Il piano a mano dell'impianto 5 si ferma con «run w5 has no straight stretch of 7.5mm for
valve-isolation»: è **vecchio** (D-167), e il suo README lo dice in testa.

**Come si legge.** Il piano dell'agente **non perde niente** rispetto a quello a mano su nessun
impianto, e sulla maggior parte dei numeri vince. Il formato più piccolo non è un'estetica: è la
tavola stretta che il PO ha chiesto (**D-170**). L'unica voce peggiore è un incrocio in più
sull'impianto 3, dichiarato dall'agente: la calata di una zona attraversa il ritorno dell'altra.

## I rilievi che restano, uno per uno

| impianto | rilievo | che cos'è |
|---|---|---|
| 1, 2 | B11 | il gradino di interasse fra la serpentina del bollitore (10) e la coppia che la serve (15): noto, e le istruzioni dicono di non inseguirlo |
| 3 | B10 | il ritorno della zona in alto corre sopra la mandata della zona in basso: è la forma del **pettine** (B12). B10 confronta una mandata con qualunque ritorno affiancato, anche di un'altra utenza — **domanda al PO** |
| 3 | A4 | lo sfiato del volano, 15 mm contro 10: la mandata passa 10 mm sopra il volano, e con lo stacco minimo l'instradatore le faceva girare intorno allo sfiato con quattro pieghe |
| 4 | B11 ×2 | le due verticali distinte che B3 chiede fra caldaia e volano, e il gradino di interasse del radiatore (10 contro 15) |
| 5 | B1 | l'**anello del ricircolo** contato come autostrada: la sua U non si toglie. È la domanda di classificazione già scritta il 22 settembre |
| 5 | B9 | la linea ACS e l'anello del ricircolo a 5 mm per 5 mm |
| 5 | B11 | il gradino di interasse UTA/volano, 10 contro 15 |

## Che cosa si vede guardando

- **1** — si legge: le due pompe impilate, i collettori accanto, l'accumulo combinato al centro.
- **2** — si legge, con un difetto: le due discese verso il bollitore sono lunghe un centinaio di
  millimetri, e la colonna dell'ACS sta stretta fra i due serbatoi. La sigla del volano cade
  fuori dal suo simbolo, accanto a una valvola.
- **3** — si legge: mandata e ritorno rette dalla pompa al collettore di zona e ritorno, il volano
  **specchiato** in serie sul ritorno, il corredo appeso sotto il ritorno. L'uscita ACS punta
  verso il fondo della pompa di calore, a 10 mm: la sigla chiarisce, l'occhio no.
- **4** — **assomiglia alla tavola che il PO ha ridisegnato il 21 settembre**: pompa sopra,
  caldaia sotto alla stessa `x`, le due tre vie **sulle orizzontali della caldaia**, lo
  scambiatore sotto. I collettori stanno a 75 mm dalle macchine perché la catena della caldaia
  — filtro, valvola, commutatrice, valvola, deviatrice, valvola, ritegno — occupa il rettilineo.
- **5** — si legge: tre pompe impilate con i due collettori verticali accanto, il primario retto
  fino al volano, il pettine UTA, ventilconvettori, radiante con la miscelatrice sulla colonna di
  mandata. Le discese verso la serpentina sono lunghe (circa 140 mm): il bollitore sta in basso
  perché la linea ACS passi sotto il pettine.

## Le domande che gli agenti hanno scritto per il progettista

Non sono del pianificatore e non si risolvono qui: vanno al PO.

- La **miscelatrice termostatica ACS** è nel catalogo con due attacchi, senza l'ingresso
  dell'acqua fredda (impianti 1, 2, 3 e 5).
- L'**anello del ricircolo** dell'impianto 5 si chiude subito dopo il bollitore e non raggiunge
  le utenze (è l'assunzione a3 del grafo).
