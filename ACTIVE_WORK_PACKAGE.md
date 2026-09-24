# DRAW-017 — Migliorie e piccole correzioni, a partire dalle tavole approvate

**Da svolgere:** l'agente unico (**D-147**), con agenti paralleli in sessione (**D-152**)
**Stato:** **ATTIVO.** `DRAW-016` è fuso su `main` con la PR **#53**, e **le tavole sono approvate**
(**I-109**).
**Base:** `main`, allineato e pulito.
**Ramo:** `claude/handoff-work-package-s11fah`, ripartito da `main` dopo la fusione di #53.
**Release:** 0.3 — generalizzazione
**Approvazione della fusione:** **del PO**, e si dà guardando le tavole (D-146, D-147)

Il PO, il 23 settembre 2026, approvando le tavole di `DRAW-016`:

> «Finalmente un vero miglioramento!!!! Si le approvo assolutamente vanno benissimo! Hanno
> proprio l'aspetto di tavole professionali! **Da qui in poi si parla di migliorie e piccole
> correzioni.** Ma questa è una PR milestone.»

---

## Il metro: le tavole del 23 settembre

Le cinque tavole che il pianificatore ha composto da solo sui grafi completi —
[`docs/collaudi/DRAW-016/prova-camera-pulita-2026-09-23/`](docs/collaudi/DRAW-016/prova-camera-pulita-2026-09-23/)
— sono **approvate**, e sono il risultato di riferimento: «seguiamo quello che hai fatto come
risultato finale» (**D-174**). **Nessuna correzione di questo pacchetto le può peggiorare.** Il
punto di partenza, misurato dalla sessione:

| impianto | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| formato | A3 | A3 | A3 | A3 | A2 |
| cedute / bloccanti | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| rilievi | 1 | 1 | 1 (era 2: B10 del pettine, D-174) | 2 | 3 |
| spezzate piegate / pieghe / incroci | 3 / 4 / 1 | 3 / 4 / 1 | 3 / 3 / 2 | 5 / 6 / 2 | 10 / 13 / 5 |

Suite: **48 rosse** (lo stesso insieme della base di `DRAW-016`), 1629 passate, 24 `skip`, 12
`xfail`.

---

## Le cose da fare, in quest'ordine

### 0. ~~I piccoli difetti che il PO vede~~ — lasciati da parte dal PO (I-112)

Il PO, approvando, aveva detto «vedo piccoli difetti»; il 23 sera: «Lasciamo stare per ora va
bene così». **Non sono lavoro di questo pacchetto** finché il PO non li riapre.

### 1. ✅ B10 confronta la mandata solo con il proprio ritorno — **D-174**, fatto il 23

I tre rilievi del pettine sono spariti, nessun altro si è acceso; la prova tace sul pettine e
accusa la coppia rovesciata.


Prima `RETURN_RUNS_ABOVE_ITS_SUPPLY` confrontava una mandata con **qualunque** ritorno
affiancato sulla stessa rete, e si accendeva sul pettine con le utenze impilate — la forma che il
PO ha disegnato. Adesso guarda la **coppia della stessa utenza**: due tratte con la stessa
macchina a un capo.

### 2. La legenda su due colonne, quando in una non ci sta — **D-177**, misurata il 23

Sull'impianto 5 la legenda in colonna unica chiede 237,5 mm e la banda dell'A3 ne ha 235: il
disegno ci starebbe, e il foglio cresce per la legenda. **Prima di prendere un foglio più grande
si prova la seconda colonna.** Il giudizio si dà sulla tavola.

⚠ **Provata sui numeri il 23 settembre, prima di scrivere codice: sull'impianto 5 non basta.** La
legenda sfora di **una riga** (31 righe da 7,5 mm più lo stacco fra le sezioni: 237,5 contro
235). Una seconda colonna larga come la prima (50 mm) lascia al disegno **300 mm** di larghezza, e
il disegno dell'impianto 5 ne occupa **337,5**: l'A3 non arriva lo stesso. L'unica leva che lo
porterebbe in A3 è l'interlinea della legenda, che è convenzione grafica — e il PO: «**Interlinea
legenda non si tocca**» (I-112). **Chiuso: l'impianto 5 resta in A2, e la legenda non cambia.**

### 3. La miscelatrice termostatica ha l'ingresso dell'acqua fredda — **D-175**

- **Libreria**: la definizione ha un terzo attacco, l'acqua fredda in ingresso; il simbolo ha già
  il terzo lato disegnato, e la porta si aggiunge **nel generatore**
  (`examples/graphics/build_symbols.py`), mai nel file generato. **Non è più un organo in
  linea**: il motore non la posa da solo sulla tratta.
- **Regola di completamento** (`rules/hydronic/dhw-mixing-on-draw-off.json`): con la miscelatrice
  arriva **il suo ingresso AF**, un confine di rete con un tratto corto — «serve il pezzetto di af
  in ingresso» — come il gruppo di riempimento ha già il suo (AF-02 sulle tavole).
- **Pianificatore**: la miscelatrice si posa e **si ruota e si specchia nel piano** come le tre
  vie (D-168, D-169), «per evitare sormonti o curve non necessarie». Le istruzioni lo dicono.

### 4. Il ricircolo ACS — **D-176**

- **Colore**: la linea di ricircolo ha un colore suo, **verde chiaro**, e una riga sua in
  legenda. È una modifica della convenzione grafica, **decisa dal PO**.
- **Topologia**: il ricircolo **preleva dalle utenze** — in tavola entra da un **confine di rete
  «ACS-R»**, lo stesso simbolo del prelievo AF — e **dopo il circolatore torna nell'accumulo
  ACS**, se c'è. Gli accumuli ACS hanno bisogno dell'**attacco del ricircolo**, nel generatore.
- **Il grafo dell'impianto 5 è sbagliato**, ed è un errore di «Capire» (l'assunzione a3 chiudeva
  l'anello subito dopo il bollitore): si corregge il grafo e si scrive la regola nelle istruzioni
  di `skill/capire/`, dove il ricircolo si modella.

### 5. Le tavole si ricompongono col pianificatore

La libreria e i grafi cambiano: la miscelatrice diventa un pezzo del piano, arrivano i confini
AF delle miscelatrici e l'«ACS-R». **I piani non si correggono a mano** (D-155): i grafi completi
si rigenerano con le regole, e il pianificatore ricompone in camera pulita almeno gli impianti
che cambiano (1, 2, 3, 5). **Le tavole, per prime, al PO**, accanto a quelle del 23 settembre.

### 6. I piani del pianificatore nelle prove

Il criterio 10 di `DRAW-016` (38 rosse o meno) non è raggiunto: le dieci in più sono i piani a
mano, vecchi, e il 5 non esce più. **Le prove leggono i piani del pianificatore** — che restano
materiale di collaudo — e le prove del revisore che cadevano a valle si rimisurano.

---

## Piccole correzioni candidate, trovate dagli agenti

Restano **candidate**: il PO ha lasciato da parte i suoi piccoli difetti (I-112), e queste non si fanno senza che lui le chieda:

- la freccia di verso che cade sul ponticello di un incrocio;
- la sigla di un pezzo che cade accanto a un altro (VOL-01 sugli impianti 2 e 4);
- ~~la ritegno sull'acqua calda (`valve-check-dhw-hot`) senza verso nel catalogo, col simbolo che
  ha la freccia~~ — **chiesta dal PO il 24 settembre e fatta** (I-114, D-180, punto 8);
- il minimo di A4 per uno stacco con rubinetto, che tollera 5 mm;
- il rifiuto dell'A4 che viene dalla posa d'inventario, con un messaggio che confonde;
- la deduzione dei raccordi sulla presa del ricircolo — probabilmente la toglie il punto 4.

### 7. Il vaso d'espansione sanitario negli impianti centralizzati — **D-178**

Il PO: «quando abbiamo impianti centralizzati con ACS (quindi parliamo di accumuli ACS da 1000
litri in su) conviene mettere un vaso di espansione sanitario, ma non sulla mandata ACS calda. Va
normalmente collegato sull'ingresso AF del bollitore, nel tratto compreso fra il dispositivo di
non ritorno e il bollitore».

- **La regola c'è già** (`rules/hydronic/expansion-on-the-stored-volume-feed.json`) e posa il
  vaso proprio lì, ma **non scatta mai da sola**: chiede sempre al progettista se l'accumulo lo ha
  dentro. Da 1000 litri in su, nell'impianto centralizzato, il vaso si mette.
- **Serve il volume dell'accumulo nel grafo**, e oggi non c'è: lo legge «Capire» dal testo del
  progettista (`skill/capire/`), e dove manca resta una domanda.
- Sotto i 1000 litri non cambia niente. Una prova per parte: da 1000 litri in su il vaso c'è, fra
  ritegno e bollitore; sotto, la regola chiede come oggi.
- **Fra gli impianti di prova solo il 5 ha l'accumulo ACS da 1000 litri in su** (I-112): è l'unica
  tavola che guadagna il vaso. **Il volume esatto non è dato**, e non si inventa: nel grafo va la
  soglia che il PO ha detto, non un numero.

### 8. Le correzioni del PO sulle tavole del 24 settembre — **I-114**

Il PO, sul confronto delle tavole: «le integrazioni che hai fatto per AF e ricircolo sono
perfette», e due correzioni — «Fai le verifiche e in caso le correzioni».

- ✅ **La freccia della ritegno nel verso del flusso — D-180.** Verificato sulle cinque tavole:
  dieci organi con la freccia, uno solo contro il flusso, la ritegno del ricircolo del 5; era
  l'unica voce del catalogo con la freccia e le porte senza verso. Il verso nasce nel generatore
  del catalogo; due prove (catalogo, cinque tavole). La tavola 5 si ridisegna con lo stesso piano.
- ⏳ **Le valvole di sicurezza, una per macchina, senza intercettazioni in mezzo** (impianti 1 e
  4). Le tavole fanno quello che dispone **I-046** (8 settembre: «spostare la sicurezza, non
  moltiplicarla»), che le regole applicano sotto i 35 kW; sopra i 35 kW è già una per macchina.
  **Domanda al PO** prima di toccare le regole. Se conferma, cambiano i grafi 1 e 4, e le due
  tavole si ricompongono in camera pulita.

## Deciso dal PO il 23 settembre

- **D-173** — il pavimento di B1 fra due pezzi è **approvato** (I-111), dopo la spiegazione che il
  PO aveva chiesto. Il codice fuso con #53 resta com'è.

## Quello che questo pacchetto **non** chiude, e resta aperto da `DRAW-016`

L'**anello** — l'occhio che scrive vincoli come dati e il pianificatore che li rispetta —, le
**cure deterministiche** del revisore che escono, **`passa-per`**, i rilievi di **A2, A3 e B5**.
Non si toccano qui: il PO ha detto che adesso si parla di migliorie e correzioni.

---

## Perimetro

**Dentro:** `src/disegnatore_mep/layout/**`, `graphics/**` (legenda, colore del ricircolo),
`validation/regole.py` (B10), `piano/**`, **`rules/**`** — il motore delle regole, perché la
miscelatrice è un pezzo in linea sull'ACS con un ingresso AF suo, e oggi il motore sa fare o
l'uno o l'altro; la libreria — `examples/layout/catalog/**` e i
simboli **attraverso il generatore** `examples/graphics/build_symbols.py`; `rules/hydronic/**`
(la miscelatrice, il ricircolo se nasce da una regola); `naming/**` (la linea del ricircolo);
`examples/prova/prova-5-cascata-tre-pdc.json` (il ricircolo); `skill/capire/**` (la regola del
ricircolo, il volume dell'accumulo ACS), `skill/comporre/**`; `docs/regole-del-piano.md`; `docs/collaudi/DRAW-017/`;
`tests/**`.

**Fuori:** qualunque contenuto MEP che il PO non abbia dato — **D-175, D-176 e D-178 sono le sue
disposizioni, e si implementano come sono espresse**; qualunque convenzione grafica oltre **D-176** e
**D-177**. **Gli attacchi dei simboli** si spostano e si aggiungono solo nel
generatore, e ogni cambiamento di manifesto ne alza la versione.

### Deviazioni dichiarate — 24 settembre 2026

Quello che la sessione ha toccato fuori dal perimetro scritto, e perché:

- **Il ramo** è `claude/kind-dijkstra-lqc2zl`, non `claude/handoff-work-package-s11fah`: è quello
  che l'ambiente della sessione assegna.
- **Codice fuori da `layout/`, `graphics/`, `piano/` e `rules/`:**
  - `src/disegnatore_mep/graph/lines.py` — senza, il ricircolo restava una derivazione della
    mandata (`ACS.01a`) e non la linea sua che `naming/` gli dà (`ACSR.01`);
  - `src/disegnatore_mep/graph/plant.py` e `src/disegnatore_mep/catalog/schema.py` — l'attacco
    del ricircolo è **tappato quando non serve**: senza, ogni accumulo ACS senza ricircolo
    (impianti 2 e 3) accusava un attacco libero.
- **Generatori e dati che contengono i pezzi cambiati:**
  - `examples/prova/build_test_plants.py` — genera il JSON dell'impianto 5 che il perimetro
    nomina: il file generato non si scrive a mano;
  - `examples/layout/build_layout_fixtures.py` — genera le voci di catalogo dell'accumulo ACS e
    della pompa di calore sanitaria: l'attacco del ricircolo nasce lì, e la prova dei generatori
    ribalta qualunque voce scritta a mano;
  - `examples/layout/centrale-pdc-quattro-fasce.json` e `examples/rules/centrale-pdc-completa.json`
    — fixture di prove che contengono una miscelatrice: le porte hanno cambiato nome, e il confine
    AF con la sua tubazione è aggiunto **in coda, senza riordinare**;
  - `docs/prodotto/grafi-di-prova/*.md` e `docs/prodotto/GRAFO_IMPIANTO.md` — rigenerati dai
    grafi, come le prove di collaudo pretendono; in `CONFRONTO-2026-08-07.md` il conteggio dei
    pezzi e i punti aperti dell'impianto 5.
- **Regole oltre la miscelatrice e il vaso:** l'ordinamento di `dhw-check-on-cold-inlet.json` e
  `safety-group-on-the-stored-volume.json`. Senza, il vaso finiva dal lato dell'acquedotto
  rispetto al gruppo di sicurezza sanitario — che porta dentro il non ritorno —, cioè fuori dal
  tratto che D-178 indica.
- **Il criterio 4bis e il punto 7** parlano di «1000 litri in su» e del volume nel grafo. Il PO,
  il 24 (I-113, **D-179**): «Sì, conta "centralizzata"». Nel grafo va `"produzione":
  "centralizzata"`, non un volume; le prove restano una per parte.
- **`docs/DEFERRED.md` non è toccato**, ed è fuori perimetro: due sue voci — la miscelatrice «con
  due porte sullo stesso fluido» (§6) e le sue «porte che dicono il falso» (§8) — sono chiuse nei
  fatti da D-175, e lo dice il rapporto. La parte della seconda voce sul gruppo di riempimento
  resta aperta.

## Criteri di accettazione

Ogni criterio si chiude con **il comando eseguito e il suo output**.

0. **Le tavole, per prime**: i cinque impianti completi, ricomposti dal pianificatore sulla
   libreria nuova, in PDF, al PO — accanto a quelle approvate il 23 settembre.
1. **B10 sulla coppia**: una prova tace sul pettine e accusa la coppia rovesciata; sulle
   tavole il rilievo del pettine sparisce, e nessun altro si accende.
2. **La legenda su due colonne** solo quando serve; misurato sull'impianto 5.
3. **La miscelatrice**: tre attacchi, l'ingresso AF da un confine con un tratto corto, ruotabile
   e specchiabile nel piano, non più posata sulla tratta dal motore; una prova.
4. **Il ricircolo**: verde chiaro e una riga di legenda; entra dall'«ACS-R»; dopo il circolatore
   torna nell'accumulo; il grafo dell'impianto 5 corretto; una prova sul colore e una sulla
   topologia.
4bis. **Il vaso sanitario** (D-178): con un accumulo ACS da 1000 litri in su la regola lo posa fra
   ritegno e bollitore senza chiedere; sotto, chiede come oggi; una prova per parte.
5. **Nessuna tavola peggiora** rispetto al metro: zero cedute, zero bloccanti, rilievi e incroci
   non in aumento — salvo dove i pezzi nuovi lo impongono, e allora si dice dove e perché.
6. **La suite**: nessuna rossa nuova rispetto alle 48, e verso le 38 col punto 6; zero `skip` e
   zero `xfail` nuovi; `ruff` e `mypy` verdi.

## Consegna

Una PR verso `main`, **fusa solo dopo che il PO ha visto le tavole e ha detto di sì**. Rapporto in
`docs/collaudi/DRAW-017/RAPPORTO.md`, con le tavole in testa.
