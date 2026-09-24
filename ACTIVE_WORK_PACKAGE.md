# DRAW-018 — Le valvole di sicurezza, una per generatore (la strada A)

**Da svolgere:** l'agente unico (**D-147**), con agenti paralleli in sessione (**D-152**)
**Stato:** **ATTIVO.** `DRAW-017` è fuso su `main` con la PR **#56**, e **le tavole sono approvate**
(**I-117**).
**Base:** `main` dopo la fusione di #56.
**Ramo:** quello che l'ambiente della sessione assegna, ripartito da `main` dopo la fusione.
**Release:** 0.3 — generalizzazione
**Approvazione della fusione:** **del PO**, e si dà guardando le tavole (D-146, D-147)

Il PO, il 24 settembre 2026, guardando le tavole 1 e 4 di `DRAW-017`: «forse di valvole di
sicurezza ne vanno 2 no ? uno per ogni macchina e senza valvole di interruzione in mezzo» (I-114).
Poi ha chiesto la ricerca su norme e prassi dei produttori (I-115), e fra le quattro strade che la
ricerca ha portato ha scelto la prima (I-116):

> «Strada A»

cioè **una valvola per macchina, sull'uscita e prima dei suoi rubinetti, senza valvola comune** —
e vale anche quando la macchina ne porta una a bordo. È **D-182**. La ricerca:
`docs/fonti/ricerche/reports/Valvole di sicurezza e simbolo ritegno.md`.

---

## Che cosa cambia — misurato prima di scrivere il pacchetto

Su una copia delle regole, con la regola «per generatore» estesa a ogni potenza e le due regole
della sicurezza comune tolte, i cinque grafi completi rigenerati con
`disegnatore-mep rules … --rules <copia> --apply-all` e confrontati con quelli di `DRAW-017`
(che la testa di `main` rigenera identici):

| impianto | che cosa cambia nel grafo | la tavola |
|---|---|---|
| **1** — due PDC | esce la sicurezza sulla mandata comune; ne entra una su ciascuna PDC, fra la macchina e il suo rubinetto | **si ricompone** |
| **4** — PDC e caldaia | lo stesso, sulla PDC e sulla caldaia | **si ricompone** |
| **2**, **3** — una PDC | stessi pezzi e stessi collegamenti: cambia solo la motivazione scritta nel grafo | si riesegue col suo piano |
| **5** — tre PDC, sopra i 35 kW | identico | non cambia |

---

## Le cose da fare, in quest'ordine

### 1. Le regole

- `rules/hydronic/safety-relief-where-heat-enters-the-water.json` vale **a qualunque potenza**, sul
  circuito chiuso dell'acqua tecnica (i generatori che dichiarano di aver bisogno di protezione
  dalla sovrapressione): una sicurezza per generatore, **attaccata all'uscita e prima di ogni organo
  che si possa chiudere**. Motivazione e fonte si riscrivono per D-182: UNI EN 12828:2003
  § 4.6.2.2.1; la Raccolta R, R.3.B.2.4–2.5, per i generatori a combustione sopra i 35 kW; Caleffi
  dp 01253/26, p. 5. **Versione maggiore.**
- **Escono** `safety-relief-on-the-closed-circuit.json` — la sicurezza comune che D-182 toglie — e
  `safety-relief-on-an-isolable-generator.json`, che proteggeva un generatore separabile dalla
  sicurezza comune: senza sicurezza comune non ha più niente da proteggere, e la sua domanda
  («la macchina la porta a bordo?») D-182 l'ha già risposta.
- La riserva sanitaria che si scalda da sé **non cambia**: ha il proprio gruppo sull'alimentazione
  fredda (EN 1487).

### 2. Le fonti

In `docs/fonti/SOURCE_REGISTER.md`: **SRC-027** passa all'edizione dp 01253/26, p. 5 (quella che
oggi sta all'indirizzo registrato); la **ricerca del 24 settembre** entra come fonte, con quello
che ha letto e quello che non ha potuto leggere (EN 12828:2014, UNI 10412). Il repository è
pubblico: nessuna pagina intera di un documento protetto, nessun collegamento a copie non
ufficiali di una norma.

### 3. Le prove

Quelle che tenevano ferma I-046 — una sola sicurezza per dominio sotto i 35 kW, la domanda sulla
valvola a bordo — **si riscrivono per D-182**, dicendolo nel file:
`tests/rules/test_regime_and_common_return.py`, `tests/rules/test_stati_idraulici_e_domini.py`,
`tests/rules/test_sicurezza_dominio_idraulico.py`, `tests/rules/test_gate.py`,
`tests/collaudo/test_p5_regime_e_tratto_comune.py`, e quelle che la suite trova in più. Una prova
nuova: **sotto e sopra i 35 kW**, ogni generatore del circuito chiuso ha la sua sicurezza sull'uscita,
prima di ogni organo che si chiude, e **nessuna sicurezza sta sulla mandata comune**.

### 4. Grafi e documenti rigenerati

I cinque grafi completi; `examples/rules/centrale-pdc-completa.json`;
`docs/prodotto/GRAFO_IMPIANTO.md` e `docs/prodotto/grafi-di-prova/`; le fixture che portano le
regole tolte, **dal loro generatore** quando ne hanno uno.

### 5. Le tavole

Le **1 e 4 si ricompongono in camera pulita** (D-155: un piano non si corregge a mano), col
protocollo di `DRAW-017` — `docs/collaudi/DRAW-017/prepara-camera.sh`, il mandato di
`docs/collaudi/DRAW-016/prova-camera-pulita-2026-09-23/mandato.md`, la misura della sessione con
`docs/collaudi/DRAW-017/misura-tavole.py`. Le 2 e 3 si rieseguono col loro piano e si confrontano
con quelle approvate; la 5 non si tocca. **Le tavole al PO per prime.**

---

## Perimetro

**Dentro:** `rules/hydronic/safety-relief-*.json`; `docs/fonti/SOURCE_REGISTER.md` e
`docs/fonti/ricerche/`; `tests/**`; `examples/rules/centrale-pdc-completa.json`,
`docs/prodotto/**` e le fixture che contengono le regole tolte, rigenerati; `docs/collaudi/DRAW-018/`.

**Fuori:** il motore (`src/disegnatore_mep/layout/`, `piano/`), la libreria dei simboli, ogni altra
regola. **Il regime dei 35 kW (D-108) resta** per le regole che lo usano: che sommi anche le
pompe di calore, mentre per la Raccolta R contano i soli generatori a combustione, è un rilievo
della ricerca e non lavoro di qui — si porta al PO se una tavola lo mostra.

---

## Criteri di accettazione

Ogni criterio si chiude con **il comando eseguito e il suo output**.

0. **Le tavole, per prime**: le 1 e 4 ricomposte, in PDF, al PO, accanto a quelle di `DRAW-017`.
1. **La regola**: una prova — sotto e sopra i 35 kW ogni generatore del circuito chiuso ha la sua
   sicurezza attaccata all'uscita, prima dei rubinetti; nessuna sicurezza sulla mandata comune.
2. **I grafi**: l'1 e il 4 cambiano soltanto nelle sicurezze; il 2 e il 3 soltanto nella
   motivazione; il 5 è identico — col confronto eseguito.
3. **Nessuna tavola peggiora** rispetto a quelle approvate il 24 settembre: zero cedute, zero
   bloccanti, rilievi e incroci non in aumento — salvo dove i pezzi nuovi lo impongono, e allora si
   dice dove e perché.
4. **La suite**: nessuna rossa nuova rispetto alle 45 di `DRAW-017`; zero `skip` e zero `xfail`
   nuovi; `ruff` e `mypy` verdi.

## Dopo `DRAW-018`: la prima release (I-118)

Il PO, il 24 settembre: «Alla fine parliamo di quali sono i prossimi step per arrivare alla prima
release della skill». La sessione porta una proposta; **che cosa viene dopo la 0.3 lo sceglie il
PO**, e con la sua scelta si aggiornano `docs/plans/2026-09-03-release-plan.md` e il pacchetto
successivo.

## Consegna

Una PR verso `main`, **fusa solo dopo che il PO ha visto le tavole 1 e 4 e ha detto di sì**.
Rapporto in `docs/collaudi/DRAW-018/RAPPORTO.md`, con le tavole in testa.
