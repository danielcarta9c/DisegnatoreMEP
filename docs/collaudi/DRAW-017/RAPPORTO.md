# DRAW-017 — rapporto

> **Le tavole, per prime:** le cinque ricomposte il 24 settembre 2026 stanno in
> [`prova-camera-pulita-2026-09-24/`](prova-camera-pulita-2026-09-24/), accanto a quelle
> approvate il 23 ([`../DRAW-016/prova-camera-pulita-2026-09-23/`](../DRAW-016/prova-camera-pulita-2026-09-23/)).
> ⏳ **Da guardare al PO.** La fusione aspetta il suo sì (D-146, D-147).

**Aperto:** 24 settembre 2026 · **Agente unico** (D-147), con agenti paralleli in sessione
(D-152) · **Base:** `732fa70`, la testa di `main` · **Ramo:** `claude/kind-dijkstra-lqc2zl`

---

## 1. Le tavole

| impianto | 23 settembre (approvata) | 24 settembre | com'è andata |
|---|---|---|---|
| 1 — due PDC e accumulo combinato | [tavola](../DRAW-016/prova-camera-pulita-2026-09-23/tavola-completo-1.pdf) | [tavola](prova-camera-pulita-2026-09-24/tavola-completo-1.pdf) | uguale al metro |
| 2 — PDC, deviatrice e ACS | [tavola](../DRAW-016/prova-camera-pulita-2026-09-23/tavola-completo-2.pdf) | [tavola](prova-camera-pulita-2026-09-24/tavola-completo-2.pdf) | una piega in più, sulla tratta verso la miscelatrice |
| 3 — PDC diretta su pavimento | [tavola](../DRAW-016/prova-camera-pulita-2026-09-23/tavola-completo-3.pdf) | [tavola](prova-camera-pulita-2026-09-24/tavola-completo-3.pdf) · [primo tentativo](prova-camera-pulita-2026-09-24/tavola-completo-3-primo-tentativo.pdf) | uguale al metro al secondo tentativo; il primo peggiorava |
| 4 — ibrido PDC e caldaia | [tavola](../DRAW-016/prova-camera-pulita-2026-09-23/tavola-completo-4.pdf) | [tavola](prova-camera-pulita-2026-09-24/tavola-completo-4.pdf) | uguale: stesso grafo, stesso piano |
| 5 — tre PDC in cascata | [tavola](../DRAW-016/prova-camera-pulita-2026-09-23/tavola-completo-5.pdf) | [tavola](prova-camera-pulita-2026-09-24/tavola-completo-5.pdf) | migliora: 1 rilievo invece di 3 |

La misura completa, i rilievi uno per uno e quello che gli agenti hanno visto stanno nel
[README della prova](prova-camera-pulita-2026-09-24/README.md).

**Quello che a guardarle salta all'occhio, e i numeri non dicono:**

- **la ritegno del ricircolo, sulla 5, ha la freccia contro il flusso.** Nel catalogo la ritegno
  sull'acqua calda non ha il verso, e il motore non sa girarla. È fra le piccole correzioni
  candidate del pacchetto, che non si fanno senza che il PO le chieda (I-112);
- **sul bollitore delle tavole 2 e 3 c'è un moncone in più**, a destra: è l'attacco del ricircolo
  che D-176 dà a ogni accumulo ACS, tappato dove il ricircolo non c'è;
- **sfiato e scarico escono rossi** anche sul ritorno: lo dicono tre agenti su quattro, ed era
  così anche il 23.

---

## 2. I criteri, uno per uno

Ogni criterio con il comando eseguito e il suo output. **Le misure delle tavole sono della
sessione** (D-152), non degli agenti: `docs/collaudi/DRAW-017/misura-tavole.py --dettaglio`, sul
motore congelato a `3b2eade` con cui gli agenti hanno lavorato, e rieseguite sul motore di questa
PR — stessi numeri.

**0. Le tavole, per prime** — ⏳ **al PO in questo passaggio**: cinque PDF, accanto a quelli del
23 settembre (§1). Il criterio si chiude quando il PO le ha viste.

**1. B10 sulla coppia** — ✅ fatto il 23 settembre (D-174), e tiene:

```
$ python -m pytest tests/validation/test_regole_del_piano.py -k "b10" -q
8 passed, 31 deselected
```

Sulle cinque tavole del 24 **nessun rilievo `RETURN_RUNS_ABOVE_ITS_SUPPLY`**: la misura del
criterio 5 li elenca per codice, tavola per tavola.

**2. La legenda su due colonne solo quando serve** — ✅ **chiuso dal PO il 23** (I-112):
misurata sull'impianto 5 la seconda colonna non basta, l'interlinea non si tocca, il 5 resta in
A2. Oggi la legenda del 5 ha una riga in più, quella del ricircolo:

```
legenda della tavola 5: 26 simboli e 5 linee, 32 righe da 7,5 mm piu' 5 di stacco = 245 mm;
la fascia della legenda in A3 e' alta 235 mm
```

(il 23 settembre erano 237,5). La legenda **non è cambiata**, e non si è scritto codice.

**3. La miscelatrice** — ✅ tre attacchi, l'ingresso AF da un confine con un tratto corto, fuori
dagli organi in linea; ruotata e specchiata nel piano:

```
$ python -m pytest tests/rules/test_miscelatrice_con_ingresso_af.py -v
test_la_miscelatrice_ha_tre_attacchi_e_l_acqua_fredda_sul_terzo PASSED
test_la_miscelatrice_non_e_piu_un_organo_in_linea PASSED
test_la_regola_le_porta_il_pezzetto_di_acqua_fredda_in_ingresso PASSED
test_ogni_miscelatrice_dei_cinque_impianti_ha_la_terza_via_collegata PASSED
```

Sul piano dell'impianto 1, scritto dall'agente: `"rotazione": 90, "specchio": true`, «tre vie sulla
colonna di dhw_out: hot_in sotto, out sopra, cold_in a sinistra»; AF-03 sta 22,5 mm a sinistra.

**4. Il ricircolo** — ✅ verde chiaro con la sua riga di legenda, entra dall'«ACS-R», dopo il
circolatore torna nell'accumulo, il grafo del 5 corretto:

```
$ python -m pytest tests/layout/test_il_ricircolo_ha_il_suo_colore.py \
    "tests/graph/test_lines.py::test_the_ricircolo_is_its_own_line_from_the_users_back_to_the_store" -v
test_il_ricircolo_entra_da_un_confine_acs_r_e_rientra_nell_accumulo PASSED
test_la_mandata_sanitaria_va_alle_utenze_senza_innesti PASSED
test_il_ricircolo_e_il_ritorno_dell_acqua_calda_e_si_disegna_verde_chiaro PASSED
test_la_legenda_ha_la_riga_del_ricircolo PASSED
test_the_ricircolo_is_its_own_line_from_the_users_back_to_the_store PASSED
```

**4bis. Il vaso sanitario** — ✅ **come il PO l'ha risolto il 24** (I-113, D-179): il criterio è
l'ACS **centralizzata**, non i 1000 litri. Una prova per parte:

```
$ python -m pytest tests/rules/test_vaso_sanitario_centralizzato.py -v
test_con_l_acs_centralizzata_il_vaso_si_posa_fra_il_non_ritorno_e_il_bollitore PASSED
test_senza_il_dato_la_regola_chiede_come_prima PASSED
test_il_dato_e_la_parola_del_progettista_trascritta_com_e PASSED
test_una_regola_che_non_chiede_non_puo_dire_quando_non_chiedere PASSED
```

**5. Nessuna tavola peggiora** — ✅ **rilievi e incroci mai in aumento**, zero cedute e zero bloccanti su
tutte e cinque, **con una piega in più dichiarata** sulla 2 e **un secondo tentativo** sulla 3.

```
$ python docs/collaudi/DRAW-017/misura-tavole.py --dettaglio impianto-N=grafo:piano ...
tavola                   formato tratte cedute blocc regole avvisi piegate pieghe incroci
impianto-1               A3          23      0     0      1      1       3      4       1
impianto-2               A3          25      0     0      1      1       4      5       1
impianto-3               A3          24      0     0      1      1       3      3       2
impianto-4               A3          25      0     0      2      2       5      6       2
impianto-5               A2          56      0     0      1      1       8      9       5
3-primo-tentativo        A3          24      0     0      2      2       3      4       1
```

| impianto | rilievi 23 → 24 | incroci 23 → 24 | spezzate piegate / pieghe 23 → 24 |
|---|---|---|---|
| 1 | 1 → 1 | 1 → 1 | 3 / 4 → 3 / 4 |
| 2 | 1 → 1 | 1 → 1 | 3 / 4 → **4 / 5** |
| 3 | 1 → 1 | 2 → 2 | 3 / 3 → 3 / 3 |
| 4 | 2 → 2 | 2 → 2 | 5 / 6 → 5 / 6 |
| 5 | 3 → **1** | 5 → 5 | 10 / 13 → **8 / 9** |

- **La piega in più sulla 2** sta sulla tratta dal bollitore alla miscelatrice, cioè sul pezzo
  nuovo: la miscelatrice, da pezzo del piano, sta in orizzontale a destra dell'uscita ACS, che
  esce dal cielo del bollitore. L'agente la dice imposta — sopra il bollitore pende lo scarico
  del volano —; sulla 1 lo stesso gruppo sta in colonna, perché lì sopra c'è posto. Il criterio
  chiede di dire dove e perché, ed è questo.
- **La 3 del primo tentativo peggiorava** — due rilievi, B1 sul ritorno della zona notte, e il
  pettine perso — **e non per i pezzi nuovi**. Si è rifatta la prova con un agente nuovo, stesso
  mandato e stesse istruzioni, senza suggerimenti: **il secondo tentativo è uguale al metro**, ed
  è la tavola agli atti. Il primo resta nella cartella col suo nome.
- Le tratte crescono di due dove c'è la miscelatrice (il suo ingresso AF, e la tratta dell'acqua
  calda che spezza in due); sul 5 il ricircolo cambia strada e non cambia il conto.

**6. La suite** — ❌ **in parte**. Nessuno `skip` e nessuno `xfail` nuovo, `ruff` e `mypy` verdi,
cinque rosse della base tornate verdi; ma **due rosse nuove**, dichiarate e non corrette:

```
$ python -m pytest -q
45 failed, 1651 passed, 24 skipped, 12 xfailed in 667.11s
$ python -m ruff check src tests examples scripts
All checks passed!
$ python -m mypy
Success: no issues found in 77 source files
```

| | base | oggi |
|---|---|---|
| rosse | 48 | **45** |
| passate | 1630 | 1651 |
| `skip` / `xfail` | 24 / 12 | 24 / 12 |

- **Tornate verdi (5)**: le due dell'esecutore sulla cascata, che il piano a mano del 5 non
  instradava più da D-167, e le tre dell'anello del revisore, il cui guasto sul piano a mano del
  4 non produceva più nessuna violazione di A1.
- **Nuove (2)**: `test_posa_a_fasi.py::test_il_corredo_che_non_entra_allunga_il_tronco_e_non_lo_piega`,
  sui due casi con l'accumulo combinato. Il file è marcato «difendeva il solutore»: sono le fasi
  del ciclo di miglioramento, che **D-151 ha tolto dalla decisione della posa** e che nessun
  percorso vigente chiama, e ne ha già 8 rosse nella base. Cadono perché la miscelatrice, da
  pezzo del piano, prende una colonna sua nella posa di partenza del solutore, e la prende fra
  mandata e ritorno del tronco: dopo l'allungo le tratte del secondario non si instradano più.
  Nel percorso vivo quella posizione la scrive il piano. **Correggere il solutore morto non è
  lavoro di questo pacchetto**, e non si marcano `xfail` (è vietato): restano rosse, e lo si dice.
- **Verso le 38**: delle 43 rosse della base che restano **nessuna legge un piano**: tutte
  compongono senza — `compose_drawing` o le fasi del solutore — cioè per il percorso che D-151 ha
  tolto dalla decisione della posa; alcune difendono proprietà del motore passando di lì
  (`test_rami_di_servizio` e `test_stacchi_minimi_e_interasse`, 8 ciascuna). Portare nelle prove
  i piani del pianificatore ne ha chiuse cinque, ed erano tutte quelle che un piano lo leggevano.

---

## 3. Che cosa è cambiato

### La miscelatrice termostatica ha l'ingresso dell'acqua fredda (D-175)

- **Libreria.** Il simbolo ha tre attacchi — `hot_in` a sinistra, `out` a destra, `cold_in` in
  basso — e la gamba della terza via arriva al bordo; nasce **nel generatore**
  (`examples/graphics/build_symbols.py`), versione 2.0.0. **Non è più un organo in linea**: il
  motore non la posa da solo sulla tratta, la posa il piano, e si ruota e si specchia come le tre
  vie (D-168, D-169).
- **Regola.** `dhw-mixing-on-draw-off` 4.0.0 la mette dentro la tubazione dell'acqua calda e le
  porta **il suo ingresso AF**: un confine di rete con la sua rete e il suo tratto, come il gruppo
  di riempimento ha il suo. Il motore delle regole sapeva fare o l'organo in linea o il ponte fra
  due reti; adesso sa fare **il ponte in linea** (`bridge_port`), e il caricamento controlla che
  l'attacco del ponte porti un altro fluido.
- **Le sigle.** Con due ponti sull'acqua fredda — il riempimento e la miscelatrice — la sigla AF
  andava a chi veniva applicato prima, cioè all'ordine alfabetico dei file delle regole. Adesso
  si danno in ordine di identificativo: il riempimento resta AF-02, la miscelatrice prende AF-03,
  comunque le regole si chiamino.

### Il ricircolo (D-176)

- **Topologia.** Il ricircolo entra in tavola da un confine «ACS-R» (`dhw-recirculation-inlet`,
  lo stesso simbolo del prelievo AF), passa per circolatore e ritegno e **torna nell'accumulo**,
  in un attacco nuovo, `recirculation_in` — nato nel generatore del catalogo per il bollitore e
  per il boiler in pompa di calore, e **tappato** dove il ricircolo non c'è.
- **Il grafo dell'impianto 5 è corretto**: l'assunzione a3 chiudeva l'anello subito dopo il
  bollitore. La regola sta ora nelle istruzioni di «Capire» (§4.3, §4.4).
- **Colore e nome.** Verde chiaro, `#58d68d`, con la sua riga in legenda («Acqua calda sanitaria —
  ricircolo»); la linea si chiama `ACSR.01` (`naming/lines.json`).

### Il vaso sanitario dove l'ACS è centralizzata (D-178, D-179)

- La regola `expansion-on-the-stored-volume-feed` 3.0.0 **non chiede più** se l'accumulo ha il
  vaso dentro quando l'accumulo dichiara `"produzione": "centralizzata"` — la parola del
  progettista, trascritta da «Capire» (§4.5). Dove il dato non c'è, chiede come prima.
- **Il dove.** Il vaso finiva dal lato dell'acquedotto rispetto al gruppo di sicurezza sanitario,
  che porta dentro il non ritorno. Riordinate le due regole dell'acqua fredda del bollitore, la
  fila dal bollitore è: **vaso, gruppo di sicurezza, scarico, valvola, acquedotto**. Gli impianti
  2 e 3 non cambiano.

### Le prove leggono i piani del pianificatore (punto 6)

Esecutore, revisore, comando e zone eseguono **grafo e piano agli atti** della prova del 24
settembre invece dei piani scritti a mano del 19/20. Le due prove sulle rotazioni stanno sul
piano approvato del 4: il gruppo di riempimento girato dal pianificatore, il tee del manometro
girato dalla deduzione. Il revisore si guasta spostando il radiatore a (150, 100), dentro la
fascia degli accumuli: il giro zero ha un rilievo di A1, la cura lo porta a x=225 e il rilievo
si spegne.

---

## 4. La suite

Il dettaglio è nel criterio 6, §2.

---

## 5. Deviazioni dal perimetro

Sono scritte nel pacchetto, alla sezione **«Deviazioni dichiarate — 24 settembre 2026»**. In
breve: il ramo è quello che l'ambiente assegna; tre file di codice fuori da `layout/`, `piano/` e
`rules/` (`graph/lines.py`, `graph/plant.py`, `catalog/schema.py`); i generatori e le fixture che
contengono i pezzi cambiati; l'ordinamento di due regole dell'acqua fredda del bollitore; il
criterio 4bis letto come il PO l'ha risolto (D-179); `docs/DEFERRED.md` non toccato.

---

## 6. Che cosa va al PO

**La decisione che serve per fondere è una: le tavole vanno bene?** Il resto si legge quando si
vuole, e non ferma niente.

- **Le tavole** (§1): la fusione aspetta il sì del PO. Sulla 3 ci sono due tavole: quella agli
  atti è il secondo tentativo, uguale al metro; il primo peggiorava, e lo si mostra.
- **Da chiudere, se il PO è d'accordo dopo averle viste**: **I-110** (le risposte alle domande di
  `DRAW-016`: la miscelatrice con l'ingresso AF e il ricircolo sono fatti), **I-111** (D-173
  approvata e il vaso sanitario: fatto, con D-179), **I-113** (conta «centralizzata»: fatto). La
  chiusura è del PO.
- **Una piccola correzione candidata che adesso si vede**: la ritegno del ricircolo con la freccia
  contro il flusso (tavola 5). Si corregge dando il verso ai due attacchi della ritegno
  sull'acqua calda nel catalogo. Non l'ho fatta: I-112 le lascia da parte finché il PO non le
  chiede.
- **Le domande che gli agenti hanno scritto per il progettista**, nel README della prova: lo
  scarico del bollitore a monte del gruppo di sicurezza con il ritegno (2, 3, 5 — ed era così
  anche nei grafi approvati il 23), il ritorno delle zone del pavimento su un raccordo a T invece
  che su un collettore (3), nessun ritegno sulle mandate della cascata (5), il posto del raccordo
  del bypass nel circuito miscelato (5).
