# DRAW-018 — rapporto

> **Le tavole, per prime:** le 1 e 4 ricomposte il 24 settembre 2026, sera, stanno in
> [`prova-camera-pulita-2026-09-24/`](prova-camera-pulita-2026-09-24/), accanto a quelle approvate
> la mattina ([`../DRAW-017/prova-camera-pulita-2026-09-24/`](../DRAW-017/prova-camera-pulita-2026-09-24/)).
> ⏳ **Da guardare al PO.** La fusione aspetta il suo sì (D-146, D-147).

**Aperto:** 24 settembre 2026 · **Agente unico** (D-147), con agenti paralleli in sessione
(D-152) · **Base:** `6d6ecc6`, la testa di `main` dopo la fusione di `DRAW-017` · **Ramo:**
`claude/kind-dijkstra-lqc2zl`

---

## 1. Le tavole

| impianto | approvata la mattina | adesso | com'è andata |
|---|---|---|---|
| 1 — due PDC e accumulo combinato | [tavola](../DRAW-017/prova-camera-pulita-2026-09-24/tavola-completo-1.pdf) | [tavola](prova-camera-pulita-2026-09-24/tavola-completo-1.pdf) · [altro agente](prova-camera-pulita-2026-09-24/tavola-completo-1-altro-agente.pdf) | uguale al metro; una sicurezza per PDC |
| 4 — ibrido PDC e caldaia | [tavola](../DRAW-017/prova-camera-pulita-2026-09-24/tavola-completo-4.pdf) | [tavola](prova-camera-pulita-2026-09-24/tavola-completo-4.pdf) · [altro agente](prova-camera-pulita-2026-09-24/tavola-completo-4-altro-agente.pdf) | uguale al metro; una sicurezza sulla PDC e una sulla caldaia |
| 2, 3, 5 | [cartella di `DRAW-017`](../DRAW-017/prova-camera-pulita-2026-09-24/) | le stesse | una macchina sola sul 2 e sul 3, e sopra i 35 kW sul 5: cambia solo la motivazione nel grafo, e con lo stesso piano l'SVG è identico |

**Dove stanno le sicurezze, guardate sulla tavola**: su ogni macchina un raccordo subito
all'uscita, la valvola sul suo stacco, e il rubinetto della macchina dopo. Nessuna sulla mandata
comune.

**Quello che a guardarle salta all'occhio, e i numeri non dicono** — tutto già presente nelle
tavole approvate: sfiato e scarico dell'accumulo e del volano escono rossi; l'attacco della sonda è
disegnato come un moncone. Il README della prova raccoglie anche le domande degli agenti per il
progettista.

---

## 2. I criteri, uno per uno

**0. Le tavole, per prime** — ⏳ al PO in questo passaggio.

**1. La regola** — ✅. Sotto e sopra i 35 kW, con la sicurezza a bordo presente, assente o ignota,
su sei impianti costruiti nella prova, ogni generatore del circuito chiuso ha la sua sicurezza
attaccata all'uscita, prima di ogni organo che chiude, e nessuna sta sulla mandata comune o sulla
riserva:

```
$ python -m pytest tests/rules/test_sicurezza_dominio_idraulico.py
101 passed
# con le regole di prima (quelle di main):
45 failed, 56 passed
```

**2. I grafi** — ✅. Rigenerati con `disegnatore-mep rules … --rules rules/hydronic --apply-all`
e confrontati con quelli di `DRAW-017`:

```
impianto 1: tolti  tee-valve-safety-collettore-mandata-b, valve-safety-collettore-mandata-b
            aggiunti tee-valve-safety-pdc-{master,slave}-water-supply, valve-safety-pdc-{master,slave}-water-supply
impianto 4: tolti  tee-valve-safety-collettore-mandata-b, valve-safety-collettore-mandata-b
            aggiunti tee-valve-safety-{caldaia,pdc}-water-supply, valve-safety-{caldaia,pdc}-water-supply
impianti 2, 3, 5: stessi pezzi e stessi collegamenti; cambia solo la motivazione
```

**3. Nessuna tavola peggiora** — ✅. Misura della sessione:

```
$ python docs/collaudi/DRAW-017/misura-tavole.py impianto-N=grafo-completo-N.json:piano-completo-N.json …
tavola                   formato tratte cedute blocc regole avvisi piegate pieghe incroci
impianto-1               A3          25      0     0      1      1       3      4       1
impianto-2               A3          25      0     0      1      1       4      5       1
impianto-3               A3          24      0     0      1      1       3      3       2
impianto-4               A3          27      0     0      2      2       5      6       2
impianto-5               A2          56      0     0      1      1       8      9       5
```

Uguale al metro della mattina riga per riga; le tratte crescono di due sull'1 e sul 4, gli stacchi
delle sicurezze nuove. Le 2, 3 e 5 rieseguite coi loro piani sui grafi nuovi: **SVG identici**.

**4. La suite** — {SUITE}

---

## 3. Che cosa è cambiato

- **Le regole** (D-182): la sicurezza «dove il calore entra nell'acqua» vale a qualunque potenza sul
  circuito chiuso, attaccata all'uscita e prima di ogni organo che chiude (4.0.0); escono la
  sicurezza di circuito sulla mandata comune e quella del generatore separabile. Da diciotto regole
  a **sedici**.
- **Il bordo macchina non basta, per la sicurezza**: il criterio di soddisfazione di una regola
  dichiara se ciò che la macchina porta a bordo la soddisfa — vero di norma, falso per questa
  (D-182, punto 2). Nessun impianto di prova cambia per questo: nessuna macchina del catalogo
  dichiara la sicurezza a bordo.
- **Le fonti**: SRC-027 all'edizione Caleffi dp 01253/26, p. 5; SRC-028 annotata (il § 4.6
  dell'edizione vigente di EN 12828 non è stato letto); la ricerca del 24 settembre registrata come
  **SRC-029**.
- **Le prove** che tenevano ferma I-046 riscritte per D-182, dicendolo in testa ai file; la
  capacità del motore di dire chi una multivia separa da una sicurezza resta provata, su un
  impianto con una sola sicurezza messa a mano.
- **I documenti rigenerati**: i grafi di prova, il caso completo, il confronto per il PO, le schede
  delle regole per l'ingegnere (sedici).
- **Le prove che leggono i piani agli atti** leggono il collaudo di `DRAW-018`; il banco del
  revisore resta quello di `DRAW-017`, perché il suo guasto è scritto per quella posa.

---

## 4. Deviazioni dal perimetro

Scritte nel pacchetto, «Deviazioni dichiarate»: il motore delle regole (il criterio del bordo
macchina); le schede delle regole per l'ingegnere; la proposta per la prima release
(`docs/plans/2026-09-24-verso-la-prima-release.md`, I-118), che è una proposta e non una decisione.

---

## 5. Che cosa va al PO

- **Le tavole 1 e 4**: la fusione aspetta il suo sì.
- **Le domande degli agenti per il progettista** (README della prova): il ritegno sui rami delle
  due PDC in parallelo dell'impianto 1; il filtro davanti al circolatore del secondario; il lato
  sanitario del serpentino; nell'ibrido, il vaso che nella produzione sanitaria non vede più
  l'anello caldaia–scambiatore, e chi fa circolare quell'anello.
- **La prima release** (I-118): la proposta, e la domanda sul DXF.
