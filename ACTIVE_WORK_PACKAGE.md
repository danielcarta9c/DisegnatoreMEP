# DRAW-016 — Il pianificatore e l'occhio del revisore diventano pezzi della skill

**Titolo:** Il pianificatore e l'occhio del revisore diventano pezzi della skill
**Da svolgere:** l'agente unico (**D-147**), con agenti paralleli in sessione (**D-152**)
**Stato:** **ATTIVO** quando `DRAW-015` è fuso. Finché non lo è, l'incarico è rispondere al PO su quella consegna.
**Release:** 0.3 — generalizzazione
**Approvazione della fusione:** **del PO**, e si dà guardando le tavole (D-147, D-146)

> **Prima di tutto leggi `docs/ARCHITETTURA-DEL-PIANO.md`.** Dice quali sono i cinque pezzi
> della skill e di che pasta è fatto ciascuno. Questo pacchetto costruisce **i due che
> mancano**: il **pezzo 3 — Comporre** (non esiste) e **l'occhio del pezzo 5 — Rivedere**
> (esiste solo la metà deterministica).
>
> **Non comporre piani a mano e non committarli.** È l'errore che ha fatto la sessione del 20
> settembre, e **D-155** esiste per non ripeterlo: il piano è un intermedio che la skill deve
> **imparare a scrivere**, non un artefatto da consegnare.

---

## Perché

Il PO, il 20 settembre, fermando lo sviluppo:

> «Lo scopo del progetto è avere un pezzo della nostra skill che scrive i piani. Non è che
> c'è un piano scritto per ogni impianto. Poi capiamo come formalizzare nella skill il
> pianificatore (con che regole deve farlo, quali best practice ecc.)»

Oggi il pezzo 3 lo fa **un umano** — l'agente in sessione, a mano. Le cinque tavole escono,
ma escono perché qualcuno ha scritto cinque file di coordinate. La skill, da sola, non sa
comporre.

E il pezzo 5 misura ma **non guarda**: l'occhio che ha visto il prelievo ACS a mezzo foglio
di distanza era quello dell'agente che leggeva il PDF, non un pezzo del prodotto.

## Le decisioni che lo governano

| | |
|---|---|
| **D-155** | Il piano non è un input: lo scrive il pianificatore, che è un pezzo della skill |
| **D-156** | I cinque pezzi, e la natura di ciascuno. 3 e 4 sono l'instradatore-disegnatore, ed è misto |
| **D-157** | Il revisore emette **vincoli** su nodi nominati, **mai mosse**. Punto di passaggio = disegno; nodo del grafo = contenuto, si propone |
| **D-158** | Ogni vincolo di posa ha un **rilievo sulla tavola consegnata** |

---

## Le cose da fare

### 1. `skill/comporre/` — il pianificatore

Nella **stessa forma del pezzo 1**, che è il modello e funziona: `ISTRUZIONI.md`
autosufficienti («queste istruzioni bastano da sole, non serve leggere altro»),
`CONSEGNA.md`, e le prove in camera pulita.

Dentro `ISTRUZIONI.md` va **il metodo**, non l'elenco delle regole: *in che ordine si
compone*. Il materiale c'è tutto e non si inventa niente:

- `docs/regole-del-piano.md` — A1…A4, B1…B7, C1…C3, D1…D3, ciascuna con la propria fonte;
- le **cinque composizioni a mano** (vedi punto 5): sono il modo in cui si è già composto, con
  la regola scritta accanto a ogni pezzo;
- `docs/input-pm/REGISTRO.md`, che è il giacimento principale delle correzioni del PO;
- le tavole di riferimento del disegnatore del PO, `docs/input-pm/riferimenti-grafici/`.

**Il buco da chiudere per primo, e il PO l'ha già risposto:** un **confine di rete** non sta
in una fascia, sta **addosso al pezzo che serve** con lo stacco minimo (A4, D-145, I-061).
Chi scrive `ISTRUZIONI.md` deve dirlo esplicitamente, perché è l'errore che un agente che
legge solo A1 rifarà — e adesso c'è anche il rilievo che glielo dice,
`SERVICE_STUB_LONGER_THAN_ITS_MINIMUM`, che sui cinque piani a mano è **ancora acceso
ventiquattro volte** (punto 6bis).

⚠ **`ISTRUZIONI.md` non è il posto dove nascono le regole.** Se componendo si impara una cosa
nuova, la riga va in `docs/regole-del-piano.md` con la propria fonte e la propria tavola, e le
istruzioni la citano.

### 2. `skill/rivedere/` — l'occhio del revisore

Stessa forma. Riceve: la **tavola** (immagine), i **rilievi** (preflight + i controlli delle
regole), il **piano** che l'ha prodotta, e `docs/regole-del-piano.md`. Restituisce **vincoli**,
nel vocabolario di `ARCHITETTURA-DEL-PIANO.md` §5.

**Le tre regole che lo tengono lontano dal solutore**, e vanno scritte dentro `ISTRUZIONI.md`:

1. **gerarchia, mai somma** — A1 prima di B1 prima di B3 prima di B4; quando due vincoli si
   contendono un pezzo, quello sotto **cede e lo dice**;
2. **i vincoli nascono da un rilievo su una tavola vera**, pochi per giro;
3. **punto di passaggio sì, nodo del grafo no**: un nodo del grafo si **propone** come
   domanda dichiarata, nella forma delle `assumptions` del pezzo 1.

### 3. Il vocabolario dei vincoli, nel formato del piano

`piano/formato.py` cresce di una sezione `vincoli`. È il **contratto fra il pezzo 5 e il
pezzo 3**, e va validato come il resto: un vincolo malformato dà un errore che dice che cosa
manca (stesso criterio che `DRAW-015` ha chiuso per il piano).

Serve anche che il motore sappia eseguire **`passa-per`**: oggi la spezzata la decide da sola
l'instradatore, e il piano può solo spostare i pezzi. È la leva che manca per chiudere le U
del ritorno primario e gli incroci dell'impianto 5.

### 4. Le cure deterministiche del revisore escono

`piano/revisore.py` dichiara già in testa che sono superate da **D-157**. Qui si tolgono:
restano la misura, il punteggio, le condizioni d'arresto e la guardia che non peggiora in
silenzio. Chi corregge è il pezzo 5, che scrive vincoli.

### 5. I cinque piani a mano cambiano di posto e di nome

> Due di loro sono stati corretti il 20 settembre sera, **guardando le tavole**: il confine
> ACS dell'impianto 1 da 65 a 40 mm (il proprio minimo) e quello dell'impianto 5 da 37,5 a
> 22,5. Sul 5 più vicino **non si va**: a 662,5 la tavola non esce più. Il bersaglio quindi
> non è pulito, e le note dei piani lo dicono.

Escono da `docs/collaudi/PROVA-PIANO/` — che li faceva sembrare prodotto — ed entrano nel
**collaudo del pezzo 3**, accanto alle sue prove in camera pulita, nella stessa posizione in
cui stanno i grafi di `skill/capire/prova-2026-08-07/`. Con in testa la riga che dice **che
cosa sono**: il bersaglio, scritto a mano, che il pianificatore deve pareggiare.

### 6. I rilievi che mancano, censiti (D-158)

`DRAW-015` ha chiuso **A1** e **A4**. Il censimento del resto è in
`docs/collaudi/DRAW-015/RAPPORTO.md` §4bis, verificato riga per riga sul codice vigente:

| regola | oggi è tenuta su da | che cosa serve |
|---|---|---|
| **A2** — chi sta in parallelo si impila | `tests/layout/test_zone_dei_pezzi_grossi.py`, che misura **la posa**, non la tavola | il rilievo sulla tavola |
| **A3** — l'ordine del processo da sinistra a destra | **niente** | tutto |
| **B2** — dal circolatore un tratto dritto, una curva, la dorsale | l'errore dell'instradamento, quando c'è | il rilievo che lo nomina prima |
| **C1** — un pezzo si prende dal lato delle sue porte | idem | idem |
| **C3** — la mappa degli attacchi si rifà solo per i raccordi | **niente** | il confronto fra grafo e tavola |

**Per primi A2 e A3**, che sono vincoli di posa nel senso stretto di D-158.

> **Dove si aggancia un controllo nuovo, e non c'è un secondo posto:**
> `validation/regole.py::CODICE_DELLA_REGOLA` — sigla → codice, nell'ordine in cui i
> controlli girano. Da lì si ricavano `ORDINE_DELLE_REGOLE` e il `CODICI_DELLE_REGOLE` che il
> **punteggio** del revisore conta. Aggiungere il controllo e dimenticare la riga vuol dire
> che il rilievo finisce fra gli **avvisi**: è successo ad A4 e sono due prove a sorvegliarlo
> (RAPPORTO `DRAW-015` §7 e §10ter). **Un controllo che non entra nel punteggio non è un
> controllo.**
**A3 è il caso limite**: l'unico posto che la faceva valere era il solutore, morto con D-151.
**C3 è il buco peggiore** — lo dice già il foglio delle regole — perché è l'unico difetto di
**contenuto** che nasce da una scelta **grafica**: il 20 settembre ha mandato l'acqua fredda
sull'uscita primaria dell'accumulo, col grafo giusto e il disegno sbagliato.

### 6bis. I rilievi di A4 che restano accesi, e sono veri

Il controllo c'è, e sulle cinque tavole consegnate dice **4 rilievi sull'impianto 1 e 5 su
ciascuno degli altri** (RAPPORTO §4bis, con i millimetri organo per organo). Non sono rumore:
il peggiore è **l'acquedotto dell'impianto 3 a +50 mm**, e si vede a occhio — l'acqua fredda
entra dal bordo sinistro invece che da accanto al bollitore.

**Si chiudono componendo, non alzando la soglia.** Sette dei ventiquattro sono da **+2,5 mm**,
cioè un passo di griglia: se si decide di tollerarli, **la tolleranza è il passo del foglio**
e va scritta come decisione, non come costante.

### 7. I documenti del motore dichiarano che cosa è storia

`docs/pm/2026-09-11-architettura-della-posa-a-fasi.md`,
`docs/pm/2026-09-16-come-ragiona-il-motore-e-come-dovrebbe.md`,
`docs/plans/2026-08-06-piano-costruzione-skill.md`, `docs/standard/COLD_EYE_REVIEW.md` e
`docs/DEFERRED.md:254` raccontano ancora il solutore come vigente. Regola unica: o vigente, o
dice in testa che è storia e quale decisione l'ha superato.

### 8. Le ventuno prove rosse che il solutore si è portato dietro

`DRAW-015` lascia il saldo della suite **peggiore di ventuno**: `main` 17 fallite, questo ramo
38 (RAPPORTO §10). Sono la contropartita di D-151 — prove che, per la via ordinaria,
pretendevano la qualità che il solutore produceva — e ciascuna sta in un file che porta già
la propria riga `# categoria:`.

**Non si chiudono con uno `skip` né con un `xfail`**, che è la scorciatoia che questo
progetto non prende. Per ciascuna, una delle due:

1. **la proprietà vale ancora sulla via vigente** — allora è una regressione vera e si
   ripara, o si riscrive la prova perché misuri quella proprietà **dal piano**, come è stato
   fatto per `test_il_primo_impianto_esce_dal_proprio_piano`;
2. **la proprietà era del solutore** — allora la prova dichiara in testa che cosa difendeva e
   perché è caduta, e **il conto si dichiara nel rapporto**, non si nasconde.

**Dove sono, misurate** (RAPPORTO `DRAW-015` §10): `test_posa_a_fasi` 5 ·
`acceptance/test_drawing` 4 · `test_accessori_appesi` 3 · `test_assi_dorsali_tee` 2 ·
`test_catena_macchina` 2 · `test_ordine_degli_stacchi` 2 · `test_consegna_e_verifica` 1 ·
`test_costo_peso` 1 · `test_format_choice` 1. **Otto stanno in file che dichiarano di aver
difeso il solutore; le altre tredici no, e sono quelle da guardare per prime**: compongono
l'impianto **senza un piano**, ed è il prezzo di D-151 già misurato in
`misura-senza-solutore.txt`.

⚠ **`tests/acceptance/test_drawing.py` non ha la riga `# categoria:`** — il punto 5 di
`DRAW-015` diceva «i 36 file di `tests/layout/`», e quello sta altrove. Quattro delle ventuno
sono lì: la riga va scritta.

⚠ **Il criterio 9 di questo pacchetto si misura contro lo stato consegnato da `DRAW-015`,
non contro `main`**: partire da 38 e arrivare a 38 è «non peggiora». **Arrivare sotto è il
miglioramento che I-067 chiede.**

---

## Perimetro

**Dentro:** `skill/comporre/**`, `skill/rivedere/**`; `src/disegnatore_mep/piano/formato.py`
e `revisore.py`; `validation/regole.py` per i rilievi di A2 e A3; il `passa-per` nel motore —
`layout/route.py` — che è **l'unica cosa fuori dal motore-che-funziona che questo pacchetto
autorizza, e va dichiarata**; `docs/regole-del-piano.md`; i cinque documenti dell'elenco 7;
`docs/collaudi/DRAW-016/`.

**Fuori:** tutto il resto del motore — `inline.py`, `place.py`, `legend.py`, `labels.py`,
`addresses.py`, `graphics/**`. **Fuori** `highways.py` e `turns_allowed` finché il PO non ha
risposto alla domanda **B7**. **Fuori** qualunque decisione MEP che il PO non abbia dato.

---

## Criteri di accettazione

Ogni criterio si chiude con **il comando eseguito e il suo output**.

1. **Il pianificatore esiste e gira in camera pulita**: un agente avviato da zero, che riceve
   solo `skill/comporre/ISTRUZIONI.md` e il grafo completo, produce un piano che **si carica
   e si instrada**. Su almeno **tre** dei cinque impianti.
2. **Il confronto con il bersaglio, impianto per impianto**: rilievi bloccanti, tratte cedute,
   violazioni di regola, pieghe, incroci del piano dell'agente contro quello scritto a mano.
   **Se l'agente fa peggio si dice di quanto e su cosa** — non è un fallimento del pacchetto,
   è la misura da cui si migliorano le istruzioni.
3. **L'occhio del revisore esiste**, e su almeno un impianto **scrive vincoli** che il
   pianificatore rispetta: prima e dopo, con le due tavole.
4. **Nessuna tavola perde quello che ha guadagnato in `DRAW-015`**: cinque tavole, zero tratte
   cedute, e i rilievi bloccanti non aumentano su nessuna.
5. **Il confine di rete non si allontana**: lo stacco di ogni confine non cresce su nessuna
   delle cinque, e il rilievo di A4 lo misura. Il punto di partenza è **40 · 20 · 20 · 22,5 ·
   22,5 mm** per il prelievo ACS e **25 · 30 · 70 · 37,5 · 30** per l'acquedotto (minimo 20).
   *Migliorarli è il lavoro del pianificatore, e il bersaglio è zero rilievi di A4.*
6. **A2 e A3 hanno il loro rilievo**, ciascuno con la tavola su cui si vede.
7. **Le cure deterministiche non ci sono più**, e una prova lo sorveglia.
8. **Nessun documento resta in terzo stato**, compresi i cinque dell'elenco 7.
9. **Il saldo della suite non peggiora rispetto allo stato consegnato da `DRAW-015`**
   — 38 fallite, 1564 passate, 24 `skip`, 12 `xfail` — zero `skip` e zero `xfail` nuovi,
   `ruff` e `mypy` verdi. **Ogni prova che torna verde si dice**, ed è il punto 8.

---

## Consegna

Una PR sola verso `main`, **non fusa finché il PO non ha visto le tavole e detto di sì**.

**Le tavole, per prime** (D-146) — comprese quelle che il **pianificatore** ha composto da
solo, che sono il punto di questo pacchetto. Rapporto in `docs/collaudi/DRAW-016/RAPPORTO.md`.

**Prima di chiedere l'approvazione:**

1. **Guarda le tavole**, e mettile accanto a quelle del disegnatore del PO. Se una ti sembra
   sbagliata e i numeri dicono che va bene, scrivilo: su `DRAW-015` è successo due volte su
   due ed è servito tutt'e due le volte.
2. **Misura la non-regressione prima, non dopo.** Qui sono il 4, il 5 e il 9.
3. **Se una disposizione del PO ammette due letture, fermati e chiedi al PO.**

## Le domande aperte al PO — da portargli, non da risolvere

1. **B7** — `turns_allowed` vale zero per ogni catena fra macchine di spina senza guardare se
   le facce delle porte permettono una retta. Quattro catene su tre impianti non si possono
   raddrizzare, e una è **l'unico rilievo bloccante** che resta (impianto 3). *O cambia il
   catalogo, o il bilancio diventa il minimo raggiungibile.*
2. **B1 contro B3 sulla cascata** — il collettore verticale che B3 pretende fa piegare la
   catena che B1 vuole dritta: la tavola è giusta e il numero dice che è sbagliata.
3. **Quando si apre il pacchetto DXF** — D-023 e D-148 sono state lasciate andare **perché**
   l'elaborato esce in DXF, e quel pezzo non esiste.
4. **Dove sta la presa del ricircolo sanitario.** Sull'impianto 5 il confine ACS sta adesso
   addosso alla presa, com'è giusto, ma la presa sta **all'estremo destro del foglio** e la
   mandata sanitaria attraversa da sola i tre secondari per arrivarci: è lì che stanno quasi
   tutti i quattordici incroci. *O la presa sta in fondo all'anello e la linea lunga è vera,
   o è un nodo che il disegno può avvicinare al bollitore.* È contenuto MEP, e non è mio.

## Quello che questo pacchetto **non** chiude

- **Le tavole non diventano belle qui.** Il difetto in coda resta nominato e misurato: il
  disegno è una fascia nella metà alta su tutte e cinque (D3).
- **L'elenco delle regole**, che il PO ha dichiarato aperto (I-085).
- **La composizione a corsie** della ricerca del 4 agosto §2.2 — entra quando l'avremo
  composta almeno una volta, con la sua tavola.
