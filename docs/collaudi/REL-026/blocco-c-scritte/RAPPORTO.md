# REL-026 — Blocco C, le scritte della pianta (C-1 e C-2): rapporto

**Scritto il 13 novembre 2026** dall'agente esecutivo delle voci C-1 e C-2 (D-152). Base: `ff89e30` (il ramo
della sessione `claude/magical-wright-ffrf86`, coi blocchi A e B). Quello che segue non è una misura per
l'orchestratore finché non l'ha rieseguito.

> Il worktree era nato su `54262a1` (la 1.15.0), senza REL-026: il ramo, ancora senza lavoro, è stato portato su
> `ff89e30` prima di cominciare. Un riavvio del contenitore a metà ha tolto il lavoro non registrato: ripreso da
> `ff89e30`, con un commit a ogni passo. Nessun altro ramo è stato toccato.

## 1. Le tavole, per prime

**Da tutti e cinque i casi escono le tavole**, prima e dopo. Si rifanno con
`.venv/bin/python docs/collaudi/REL-026/blocco-c-scritte/rifai_le_tavole.py` (il «prima» gira sulle sorgenti di
`ff89e30` estratte con `git archive`); per ogni tavola SVG, PDF, PNG e i tracciati; le misure in `misure.txt`.

| cartella | prima | dopo |
|---|---|---|
| `t3/` (il T3 del banco, `docs/collaudi/REL-012/collaudo-t3`) | A3 + **tre dettagli automatici A, B, C** (il B è un A3 con un angolo di muro, tre linee e il numero ① di SZ-01) | **un A3 solo**: T16, SZ-01, TZ-02, TZ-03 fuori dalla pianta col richiamo |
| `t3-esempio/` (`examples/pianta/casi/collaudo-t3.json`, con distinta e grafo) | A3 + un dettaglio automatico A | un A3: T15, TZ-01, TZ-03 fuori |
| `sagome/` (`examples/pianta/casi/sagome-muri.json`) | A3 + il dettaglio A **chiesto** dalla pianta | uguale, col dettaglio A; la coppia del primario ora è **«T01/T02 · MS 26 · L 6,4 m°»** (C-2) |
| `appartamento/` (l'aria-aria della skill) | A3 + due dettagli automatici A, B | un A3: CZ-01, TZ-03, TZ-04 fuori |
| `fitta/` (il caso anonimo di questo blocco, `examples/pianta/casi/centrale-fitta.json`) | A3 + due dettagli automatici (A sul locale tecnico, B su TA-03) | un A3, **pianta spostata a destra e in basso**: sette scritte fuori; T05/T06 con una scritta sola |

### Guardate una per una: quello che le tavole mostrano e i numeri no

Sui cinque casi nessun bloccante, nessuna scritta senza posto, nessun richiamo incrociato; un solo richiamo sopra
una scritta (punto 3), contato. Le tavole dicono di più:

1. **I richiami dei termostati sono lunghi** (`t3`, `t3-esempio`, `appartamento`). TZ-02, TZ-03, TZ-04 sono pezzi
   di 12 cm in mezzo alla pianta, in un corridoio fitto: non c'è posto nemmeno per il numero, e fuori dalla pianta
   ci arrivano con 80-120 mm di richiamo, che attraversa una stanza intera. Si seguono (sono sottili, ortogonali,
   non si incrociano, non passano sulle scritte salvo il caso del punto 3), ma sono la parte meno bella delle
   tavole. È la conseguenza diretta di «fuori dalla pianta» per un oggetto che sta nel mezzo: **da guardare dal PO**.
2. **Il richiamo di TZ-03 costeggia il fascio frigo** (`t3`, `t3-esempio`): scende nel soggiorno a 3-4 mm dalla
   fascia arancio del fascio UI-UE, per una decina di centimetri. Il costo del «correre accanto» (entro 4 mm) c'è,
   ma le altre strade passano su scritte o pezzi e costano di più. Si legge, ma a colpo d'occhio sembra un'altra
   linea del fascio.
3. **Nell'appartamento il richiamo di TZ-04 passa sopra la scritta di T16** («T1|6 · bus · L 4,4 m°»). È l'unico
   caso: il controllo lo conta e la console lo dice (`richiami_fuori_sopra_scritte_o_pezzi: 1`), non ferma la
   consegna («per quanto possibile», come l'ha chiesto il PO). Spostare la pianta non lo toglie (provato dal motore:
   le prove spostate costavano di più).
4. **Nel T3 di esempio, «Disimpegno · 13,2 m²» sta stretto fra due richiami** paralleli (TZ-01 e T15, che vanno
   alla colonna di sinistra): non li tocca, ma il nome del locale è schiacciato fra due linee.
5. **Il caso fitto, prima della correzione, aveva richiami da 200 mm che sbarravano i margini** (un richiamo di
   riga che scendeva nel margine di sinistra per 15 cm chiudeva la colonna a tutti gli altri, e QE-01 finiva
   dall'altra parte della pianta). Corretto prima del commit (§2, «Che cosa ho dovuto correggere guardando»): il
   richiamo di una riga non corre più nei margini di fianco, e la pianta si sposta sul foglio quando un richiamo
   resta lungo.
6. **Le scritte in legenda cambiano un po'** anche dove non c'erano scritte fuori: senza le cornici dei dettagli
   (che occupavano posto sulla tavola intera), qualche scritta che era un numero ora sta accanto, e viceversa (T3
   del banco: T14 e RA-01 tornano accanto, CZ-01 e TA-03 diventano numeri). Le scritte in legenda restano dove
   erano come meccanismo: è solo la posa che cambia.
7. **La pianta spostata** (`fitta`): il disegno non è più al centro del suo campo; dalla parte del locale tecnico
   il margine raddoppia, e lì stanno le scritte. È una scelta che cambia l'aspetto: **da decidere dal PO** (§6).
8. **Nel caso fitto il dettaglio di prima si leggeva bene** (`fitta/prima/centrale-fitta-dettaglio-A.png`): il
   locale tecnico a 1:20 ha ogni scritta accanto al suo pezzo. A 1:50 con le scritte fuori si legge anche, ma ci
   vuole l'occhio sui richiami. È il caso in cui il progettista può chiedere il dettaglio (`dettagli`): resta
   possibile, solo non nasce più da solo.

## 2. Che cosa ho fatto

### C-1 — i dettagli solo se chiesti, le scritte che non stanno vanno fuori

**Dove si sostituisce il meccanismo, e dove no.** Una scritta (di tratta, di fascio, di pezzo, di foratura) prova,
come prima: accanto al suo oggetto; con il richiamo corto (≤ 12 mm); come **numero cerchiato col testo in
legenda**. Solo se non c'è posto nemmeno per il numero tornava «senza posto» (`libera=False`), e
`comando._la_tavola_e_i_dettagli` apriva un riquadro di dettaglio attorno a lei. **Solo quest'ultimo passo è
cambiato**: la scritta senza posto ora va **fuori dalla pianta** (`src/disegnatore_mep/pianta/fuori_pianta.py`,
nuovo). I numeri in legenda restano com'erano.

**I dettagli** (`comando._la_tavola_e_i_dettagli`): non nascono più da soli. `dettagli` assente, `null` o `[]` =
nessun riquadro. Se il progettista ne dichiara uno, si fa come prima, e una scritta senza posto il cui oggetto
cade nella zona va nel dettaglio invece che fuori (il riquadro chiesto continua a servire a quello). Tolti
`MARGINE_DEL_DETTAGLIO_M`, `VICINI_M`, il campo `automatico` nei tracciati e la nota «perché a 1:50 le scritte non
ci stanno». Schema: il campo non cambia (resta `list | null`), cambia la descrizione di `Dettaglio`
(`schemas/pianta.schema.json` rigenerato dal modello, la prova che li confronta passa).

**Le scritte fuori** (`fuori_pianta.posa_fuori`, in millimetri di carta):

- **dove**: nei margini del campo del disegno attorno all'ingombro della pianta (muri, pezzi, zone esterne,
  tracciati: `tavola.estensione`), a `STACCO_MM` = 3 mm. **A destra** una colonna di scritte allineate a
  sinistra, **a sinistra** allineate a destra, su una griglia a passo fisso `PASSO_MM` = 4,5 mm (la stessa per
  tutto il lato, dall'alto del campo); **sopra e sotto** righe a passo fisso dalla pianta. Le righe servono perché
  una scritta di tratta è lunga 24-45 mm e i margini di fianco su un A3 a 1:50 ne hanno 11-27: le sigle stanno
  nelle colonne, le scritte lunghe spesso solo nelle righe (§6, punto 2);
- **il richiamo**: dal suo oggetto (un punto del tubo; il bordo del pezzo, verso fuori) al bordo della scritta,
  ortogonale, **al più un gomito**; dritto quando il punto può scorrere fino all'altezza della scritta (un tratto
  del tubo perpendicolare, il fianco del pezzo). Mai lungo una linea: un tratto che corre su una linea o un muro
  costa 20 al millimetro, accanto (entro 4 mm) 3 al millimetro;
- **i vincoli**: un richiamo fuori non incrocia un altro richiamo, né fuori né corto, e non passa su un'altra
  scritta fuori; la scritta fuori non tocca niente (le prove nei margini usano `Ingombri.libero`). Sopra le
  scritte e i pezzi della pianta il richiamo passa solo se non c'è altro modo: costa 1000, e si conta;
- **la scelta**: fra tutti i posti, quello col richiamo che costa meno (lunghezza, gomito 8, ogni linea 15, ogni
  muro 2, il correre accanto); il lato più vicino viene da sé, e siccome i richiami dritti di un lato sono
  paralleli, l'ordine delle scritte di una colonna è quello dei loro punti d'attacco. Le scritte si posano una
  alla volta, poi **si ripassano** due volte ciascuna con le altre ferme (cambia posto solo se costa meno), e se
  ne resta una da migliorare si rifà tutto nell'ordine inverso e si tiene il migliore. Deterministico: a parità
  vince il primo in un ordine fisso;
- **dopo**: le scritte e i richiami fuori entrano negli ingombri **prima** dei nomi delle stanze, che poi non ci
  vanno sopra.

**La regola con cui il foglio si allarga** (`tavola.componi`): se una scritta fuori non trova posto, o il suo
richiamo passa su una scritta o un pezzo, o è più lungo di `LUNGO_MM` = 120 mm, **la pianta si sposta sul foglio**
— tutta da una parte, verso il lato opposto a quello di quelle scritte, fino al margine minimo — e la prova si
tiene se tutte hanno posto e i richiami costano meno. Se nemmeno così ci stanno tutte, **il formato successivo con
la stessa scala** (A3 → A2 → A1), con la stessa funzione che già lo faceva per la colonna che non entra
(`_sul_formato_dopo`, ora una sola per tutti e due); il formato dopo si tiene solo se lì ci stanno tutte. A
formato fissato dalla pianta, o sull'A1, la scritta resta senza posto dove era provata e il controllo la conta
(bloccante). Il foglio non cresce se lo spazio c'è già: nel caso fitto la pianta si sposta e resta A3.

**I controlli** (`controlli._i_richiami_fuori`): per ogni scritta fuori la lunghezza del richiamo e i gomiti
(`scritte_fuori_pianta`, `richiamo_fuori_piu_lungo_mm`); **due richiami che si incrociano**, uno almeno fuori,
**fermano la consegna** (`richiami_che_si_incrociano`); il richiamo che passa sopra una scritta o un pezzo della
pianta (non i pezzi sotto la sua linea) si conta e si dice (`richiami_fuori_sopra_scritte_o_pezzi`). I richiami
fuori non contano più come «richiami lunghi» né come «scritte su linee»: hanno regole loro. Il riassunto in console
ha una riga in più; i tracciati i campi nuovi.

### C-2 — una scritta sola per due tubi che corrono insieme

C'era già: un **fascio** (tratte con lo stesso `fascio` fra gli stessi due pezzi) ha una scritta sola,
«T07–T09 · L 9,3 m°», «T06+T07+T11 · L 9 m / 9 m / 10 m»: le sigle, una lunghezza se uguali, se no tutte; la
dimensione mai. Completato (`tavola._gruppi_delle_scritte`, `_con_le_coppie`, `scritta_del_gruppo`):

- **due tratte che corrono insieme anche senza fascio**: fra gli stessi due pezzi, stesso fluido, **stessa
  dimensione**, **stessa lunghezza scritta e quotata**, e una accanto all'altra (parallele, a non più di due passi
  del fascio, 20 cm) per almeno l'**80 %** del percorso (`scritte.affiancate`, `CORRONO_INSIEME`). Con dimensione o
  lunghezza diversa non si uniscono: la scritta ne direbbe una sola;
- **la scritta** di una coppia è «**T05/T06 · MS 16 · L 11 m**»: le due sigle con la barra (il «M1/R1» del PO), la
  dimensione e la lunghezza una volta. Di un fascio di tre o più resta «T07–T09» o «T06+T07+T11»; la **dimensione
  si scrive una volta se è la stessa per tutti** (nel fascio frigo, liquido gas e cavo, non lo è: non si scrive,
  come prima).

Nel caso fitto: T01/T02 (fascio del primario) e T03/T04, T07/T08 (fasci dichiarati) hanno una scritta sola; T05/T06
(senza fascio, corrono insieme al 96 %) anche; T09/T10 (senza fascio, l'instradatore li porta per strade diverse:
29 %) ne hanno due, ed è giusto così.

### Che cosa ho dovuto correggere guardando le tavole (e le prove passavano)

- un richiamo che correva **dentro il muro** del corridoio, invisibile (TZ-02 nel T3): ora correre dentro un muro o
  accanto costa al millimetro;
- richiami che **sbarravano i margini** (punto 5 del §1): il gomito di un richiamo di riga sta dentro l'ingombro
  della pianta;
- una tratta corta fra due pezzi vicini (T16 del T1, T15 del T3) **senza nessun punto d'attacco** buono: punti più
  fitti sui tratti corti, e il punto può stare sul bordo di un pezzo (non dentro), e sui pezzi sotto la linea;
- la prima scritta posata che prendeva il posto che serviva alla seconda (TZ-03 sotto T16 nel T3): i giri di
  miglioria e l'ordine inverso.

E uno che non si vedeva sulle tavole ma sul tempo della suite: una prova con la pianta spostata che non bastava
tornava a provare il formato dopo, che a sua volta si spostava — fino a 69 composizioni per una pianta coi pezzi
sovrapposti (la prova del T3 senza `sovrapposto_a` durava minuti, ora 14 s). Il formato dopo lo decide solo la
pianta al centro (commit `397167f`); le tavole dei cinque casi non cambiano (SVG confrontati).

## 3. I controlli

```
$ .venv/bin/python -m pytest -q -p no:cacheprovider --durations=15      # a 397167f
3112 passed, 15 skipped, 11 xfailed in 339.59s (0:05:39)
$ .venv/bin/ruff check src tests scripts skill/scripts                   # a 4a4b9e3
All checks passed!
$ .venv/bin/python -m mypy
Success: no issues found in 129 source files
$ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_il_banco.py tests/test_le_release.py
37 passed in 24.31s
```

Base misurata su `ff89e30`: `3054 passed, 15 skipped, 11 xfailed in 248.32s`. Le 58 in più sono le prove nuove (quelle
di `test_scritte_fuori.py`, molte parametrizzate sugli otto casi della pianta, e il caso fitto nelle prove
parametrizzate che c'erano); skip e xfail sono gli stessi. Dopo `397167f` c'è solo un commit di testo nella
descrizione di `fuori_pianta.py` (`4a4b9e3`), con ruff, mypy, banco e release rifatti dopo.

**Il tempo della suite sale di un terzo** (248 → 340 s). Le prove più lente: la preparazione dei casi comuni della
pianta (29 s, c'è il caso fitto), il T3 senza zona esterna (19 s) e senza `sovrapposto_a` (14 s), le due varianti del
caso fitto di C-2 (14 s l'una). Un primo giro della suite ci aveva messo 484 s: una pianta coi pezzi sovrapposti
faceva fino a 69 composizioni (§2, l'ultimo punto).

Le prove nuove (`tests/pianta/test_scritte_fuori.py`; il caso fitto entra fra i casi comuni di
`tests/pianta/conftest.py`, quindi passa anche per le prove parametrizzate: niente diagonali, niente scritte su
linee, niente bloccanti, richiami corti a posto):

- C-1: nessun dettaglio nasce da solo; le scritte fuori stanno fuori dalla pianta e dentro il campo; il richiamo
  parte dal suo oggetto (sul tubo, sul bordo del pezzo), arriva sul bordo della scritta, è ortogonale con al più un
  gomito; **incolonnate** (colonna: stessa x a 3 mm dalla pianta e griglia di 4,5 mm; riga: passo di 4,5 mm dalla
  pianta); **i richiami non si incrociano**, misurato sui segmenti; i numeri in legenda restano; nel caso fitto il
  foglio non cresce e la pianta si sposta; il controllo trova due richiami messi a mano a croce e ferma la
  consegna; se fuori non c'è posto la tavola passa all'A2 con la stessa scala; a formato fissato la scritta senza
  posto ferma la consegna; il dettaglio chiesto si fa, e le scritte del suo nodo ci vanno, libere; con `[]` nessun
  dettaglio e nessun bloccante.
- C-2: la coppia che corre insieme ha una scritta sola, «T05/T06 · MS 16 · L 11 m»; la coppia di un fascio dice
  la dimensione una volta; due tratte che non corrono insieme ne hanno due; dimensione o lunghezza diversa non si
  uniscono; `affiancate` misura la parte che corre insieme.
- Rotta di proposito la griglia delle colonne (mezzo passo spostato), la prova dell'incolonnamento va rossa su tre
  casi (controllato, poi ripristinato).

Adattate, col perché nella prova: `test_collaudo_t1.py::test_dove_1_50_e_troppo_fitto_c_e_il_dettaglio_a_1_20`
(ora `…_le_scritte_vanno_fuori_e_nessun_dettaglio`) e `test_i_dettagli_si_possono_spegnere` (ora
`test_il_dettaglio_si_fa_se_il_progettista_lo_chiede` e `test_con_dettagli_vuoti_nessun_dettaglio_e_la_consegna_non_si_ferma`).

## 4. Il banco

```
$ .venv/bin/python scripts/banco.py
...
collaudo-t3-rel012: CAMBIATO
  - pianta/pianta-dettaglio-A.svg: non esce piu'
  - pianta/pianta-dettaglio-B.svg: non esce piu'
  - pianta/pianta-dettaglio-C.svg: non esce piu'
  ~ pianta/pianta.svg: cambiato
  ~ pianta/pianta.tracciati.json: cambiato
...
29 uguali, 1 cambiati, su 30
```

Una tavola sola del banco cambia, il collaudo T3 di REL-012 (l'unico caso con la pianta). Uscita per uscita:

- `pianta/pianta-dettaglio-A.svg`, `-B.svg`, `-C.svg` — **non escono più** (C-1): i tre riquadri automatici;
- `pianta/pianta.svg` — senza le tre cornici «Dettaglio A/B/C 1:20» e senza la nota dei dettagli; T16, SZ-01,
  TZ-02 e TZ-03 fuori dalla pianta col richiamo; qualche scritta passa fra accanto e numero in legenda (§1,
  punto 6). Il foglio resta A3 (`t3/prima` → `t3/dopo`);
- `pianta/pianta.tracciati.json` — `dettagli: []`, i rilievi nuovi (`scritte_fuori_pianta`,
  `richiamo_fuori_piu_lungo_mm`, `richiami_che_si_incrociano`, `richiami_fuori_sopra_scritte_o_pezzi`), le scritte
  in legenda e nel dettaglio che cambiano.

Impronte registrate con `scripts/banco.py --caso collaudo-t3-rel012 --registra` (`tests/banco/impronte.json`). C-2 non
cambia il banco (il T3 non ha coppie che corrono insieme; il fascio frigo ha dimensioni diverse, e la sua scritta è
quella di prima). **Dopo l'unione col ramo di C-3 le impronte vanno riregistrate**: la base disegnata cambia anche
lei la stessa tavola.

## 5. I file toccati (per l'unione col ramo della base, C-3)

- `src/disegnatore_mep/pianta/fuori_pianta.py` — nuovo.
- `src/disegnatore_mep/pianta/scritte.py` — `ScrittaPosata.richiamo_fuori`; la scritta senza posto non occupa
  più niente (`_senza_posto`, `occupa`); `Ingombri.copia`/`prendi`; `affiancate`, `CORRONO_INSIEME`.
- `src/disegnatore_mep/pianta/tavola.py` — **solo la posa delle scritte e la composizione, niente della base**
  (muri, aperture, stanze, sfondo, colori non toccati): gli import; `Tavola.costo_fuori`; `componi`: il parametro
  `spostamento` e il calcolo di `ox`/`oy` (con `gioco_x`/`gioco_y`), i dizionari `oggetti`/`proprie_di` riempiti
  dopo ogni `posa_accanto`/`posa_intorno`, il blocco delle scritte fuori **subito prima del ciclo dei nomi delle
  stanze**, i richiami fuori disegnati dopo il ritaglio del dettaglio, la colonna che non entra via
  `_sul_formato_dopo`; il testo e la guida del gruppo nel ciclo delle scritte dei tracciati; funzioni nuove
  `_versi_dello_spostamento`, `_sul_formato_dopo` (prima di `_sovrapposti_stretti`), `_con_le_coppie`,
  `_sigle_del_gruppo`, `scritta_del_gruppo`; `_gruppi_delle_scritte` con un parametro in più.
- `src/disegnatore_mep/pianta/comando.py` — `_la_tavola_e_i_dettagli` riscritta (niente dettagli automatici),
  tolte due costanti e l'import di `estensione`, `"automatico"` tolto dai dati dei dettagli, una riga nel
  `riassunto` e tre elenchi in più.
- `src/disegnatore_mep/pianta/controlli.py` — campi nuovi di `Rilievi` (con `come_dati`, `bloccanti`,
  `unisci_le_scritte`), `_i_richiami_fuori` nuova, il controllo delle scritte su linee che salta i richiami fuori.
  Non era nel perimetro scritto, ma i richiami fuori senza regole loro sarebbero tutti «lunghi» e «che passano i
  muri»: lo dico.
- `src/disegnatore_mep/pianta/modello.py` — **solo due descrizioni** (`Dettaglio` e `Pianta.dettagli`); nessun
  campo. `schemas/pianta.schema.json` rigenerato (cambia la descrizione di `Dettaglio`).
- `skill/pianta/ISTRUZIONI.md` — §2, la riga `dettagli` del §4, «Fasci», §5, §6 riscritto. `skill/SKILL.md` non
  toccato (non parla di dettagli).
- `examples/pianta/casi/centrale-fitta.json` — nuovo, anonimo.
- `tests/pianta/conftest.py`, `tests/pianta/test_collaudo_t1.py`, `tests/pianta/test_scritte_fuori.py` (nuovo),
  `tests/banco/impronte.json`, questa cartella.

## 6. Da decidere dal PO

1. **La gerarchia.** Ho scelto la più conservativa: accanto → richiamo corto → **numero in legenda** → fuori. I
   numeri restano dove erano, e fuori va solo quello che prima apriva il dettaglio. L'altra lettura di M2 —
   accanto → fuori col richiamo → numero in legenda — toglierebbe molti numeri e porterebbe molte più scritte
   fuori (con più richiami lunghi).
2. **Le righe sopra e sotto.** M2 dice «incolonnata». A destra e a sinistra le scritte sono in colonna, allineate e
   a passo; ma le scritte di tratta (24-45 mm) di regola non stanno nei margini di fianco di un A3, e vanno in
   **righe** sopra e sotto la pianta, ciascuna sopra il suo oggetto, a passo fisso. Senza righe, quasi tutte le
   tavole passerebbero all'A2.
3. **La pianta spostata sul foglio** prima di passare al formato dopo: cambia l'aspetto (il disegno non è più al
   centro), ma tiene l'A3.
4. **I richiami lunghi** dei pezzi che stanno in mezzo alla pianta (80-120 mm): conseguenza di «fuori dalla
   pianta». Alternative possibili, non fatte: un richiamo «medio» verso lo spazio bianco di una stanza vuota
   (dentro la pianta), o il numero in legenda con un richiamo più lungo dei 12 mm di oggi.
5. **«T05/T06»** con la barra per le coppie (il «M1/R1» del PO), anche per un fascio dichiarato di due tratte (prima
   «T01–T02»); «T07–T09» e «T06+T07+T11» per i fasci più grandi come prima. E la dimensione una volta nei fasci
   dove è la stessa.
6. **Il richiamo sopra una scritta** (il TZ-04 dell'appartamento): ammesso come ultima risorsa e contato, non
   bloccante. Se il PO lo vuole bloccante, la cura è nella posa dei pezzi o in un dettaglio chiesto.
7. **Un dettaglio chiesto prende le scritte del suo nodo** invece di mandarle fuori (come prima). Si potrebbe anche
   mandarle fuori sulla tavola intera e ripeterle nel dettaglio.

## 7. Quello che non ho fatto o verificato

- **La commessa BD.RM.260** (il dettaglio B «due tubi e le parole mandata/ritorno»): i file non sono nella
  sessione; la prova è sul T3, sull'appartamento e sul caso fitto anonimo.
- **Il tempo**: una pianta con una scritta fuori da migliorare si ricompone fino a tre volte (gli spostamenti).
  Misurato senza PNG né DXF, base → ramo: T3 del banco 4,9 → 5,4 s; appartamento 2,2 → 5,5 s (si prova a spostare
  per il TZ-04 sopra la scritta, invano); caso fitto 4,4 → 14,8 s; T1 2,9 → 2,5 s. La suite intera è più lenta
  (§3); non ho ottimizzato oltre.
- La CI non è girata (niente push, per disposizione); niente versione né release.
- L'unione con C-3 (la base architettonica) non è provata: i nomi delle stanze, che C-3 rifà, stanno subito dopo
  il blocco delle scritte fuori in `componi`.
- Nessun dato di cliente: i casi sono anonimi; BD.RM.260 compare solo come riferimento nei commenti.
