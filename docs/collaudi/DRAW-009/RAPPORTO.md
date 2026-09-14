# RAPPORTO DI CONSEGNA — DRAW-009

**Pacchetto:** `ACTIVE_WORK_PACKAGE.md` — «L'ingresso vicino a chi serve, e il tronco che si
sposta tutto intero»
**Documenti di riferimento:** `docs/pm/2026-09-11-architettura-della-posa-a-fasi.md`;
`docs/collaudi/DRAW-008/RAPPORTO.md` §6 e §7
**Ruolo:** DEV
**Data:** 2026-09-13

---

## 0. Le quattro cose da leggere prima di tutto il resto

1. **Il criterio 9 ha una causa misurata, ed è che la strada bassa non esisteva.** Non è
   una questione di pesi e non è una questione di instradatore: delle 48 celle della
   spezzata a una piega, **sette erano murate** — tre dal vaso di espansione, tre dal
   manometro, una dalla soglia del gruppo di riempimento. Tutti e tre pendono **sotto** il
   tronco di ritorno, e il `coil_in` del bollitore sta esattamente alla loro quota. Con
   `TURN_COST` a 100, a 800 e a 2000 la spezzata esce identica: tre pieghe erano il
   **minimo disponibile**, non una scelta. §3.9 lo dimostra cella per cella.
2. **La risposta ha deciso il seguito, e il seguito è tutto.** Il criterio 9 non è un
   problema dell'instradatore: è il criterio 8 visto dall'altro capo. `route.py` **non è
   stato toccato**. Ciò che mancava era la mossa che alza il tronco insieme al corredo che
   gli pende sotto (§B) e l'ingresso di rete che non inchioda più il bollitore (§A).
3. **La tavola 2 migliora su ogni budget, e i nodi condivisi col tronco vanno da 8 a
   zero.** Rete ordinaria da 9 pieghe / 6 incroci / 755,0 mm a **5 / 1 / 555,0 mm**, e la
   tavola intera da 15 pieghe / 11 incroci / 877,5 mm a **5 / 1 / 607,5 mm**;
   `deviatrice.out_b → bollitore.coil_in` da **3 pieghe a 1**, che è lo schizzo del PO.
   La tavola 1 migliora anche lei su tutti e tre i budget — intera, da 10 / 1 / 620,0 mm a
   **4 / 1 / 485,0 mm** — e i suoi organi governati da D-120 tornano **15 su 15**.
4. **Due criteri non sono raggiunti alla lettera e sono dichiarati con la misura**: il 3
   (la tratta del prelievo ACS ha una piega, non zero) e l'11, di cui è raggiunta la
   proprietà — le due tratte corrono annidate, misurato — ma **non** il padrone: la fase
   del tronco ancora non sceglie l'ordine degli stacchi, lo eredita dalla topologia del
   flusso. §6 e §7.

---

## 1. Ramo, commit, file

| | |
|---|---|
| **Ramo** | `claude/draw-009-work-package-171cly` — quello che la piattaforma ha assegnato alla sessione; il pacchetto non ne prescrive uno |
| **SHA iniziale** | `b63e3e6`, sopra `c142ba9` (testa di `main`, DRAW-008 fuso, PR #26) |
| **SHA finale** | vedi `git log -1` sul ramo |

### File modificati

| File | Che cosa |
|---|---|
| `src/disegnatore_mep/rules/apply.py` | §A.1 — il ponte fra due reti porta il **proprio** confine invece di pescare dalla linea di un altro; la sigla del confine nuovo nella serie del suo pari |
| `src/disegnatore_mep/layout/place.py` | §A.2 — un **ingresso di rete** non ha una posizione propria e si posa addosso all'utente che serve; le figure appese possono essere profonde |
| `src/disegnatore_mep/layout/flow.py` | `BOUNDARY_FUNCTION`, il mestiere del confine, dichiarato dove stanno gli altri |
| `src/disegnatore_mep/layout/spine.py` | `carry_the_rest` riappende la figura **intera**, non il solo primo livello; `_inside` riporta dentro il foglio una figura riappesa che ne era uscita (§6.6) |
| `src/disegnatore_mep/layout/compose.py` | la fase del corredo riceve il foglio, perché `carry_the_rest` ne ha bisogno |
| `src/disegnatore_mep/layout/improve.py` | §B — `block_of` e `_block_moves`, la traslazione di blocco; `leader_of`/`place_unit` percorrono la figura fino in fondo; una mossa risponde delle sovrapposizioni che **crea**, non di quelle che trova |
| `src/disegnatore_mep/graph/lines.py` | una strada muore su un **civico** invece di ribattezzarlo: è la conseguenza di §A.1 sulla lettura degli indirizzi (§2.6) |
| `docs/prodotto/grafi-di-prova/*.md` | rigenerati dal loro generatore, perché il grafo completato porta un ingresso e una rete in più |
| `tests/layout/test_objective.py` | §D — la prova sull'impilamento riscritta su ciò che vuole davvero, con la sua negativa |
| `tests/collaudo/test_p2_attacchi_di_servizio.py` | il **terzo piede** di una catena appesa: un confine di rete (§2.6) |
| `tests/collaudo/test_p4_indirizzo_dei_nodi.py` | il **secondo modo** in cui una strada muore: su un civico (§2.6) |
| `PROJECT_STATE.md` | stato e rischi aggiornati |
| `tests/rules/test_ingressi_di_rete.py` | **nuovo** — le prove di §A.1 |
| `tests/layout/test_traslazione_di_blocco.py` | **nuovo** — le prove di §B |
| `tests/layout/test_ordine_degli_stacchi.py` | **nuovo** — le prove di §C |
| `tests/layout/test_posa_a_fasi.py`, `tests/layout/test_traslazione_di_blocco.py`, `tests/layout/test_ordine_degli_stacchi.py` | le tre chiamate a `carry_the_rest` passano il foglio |
| `docs/collaudi/DRAW-009/**` | rapporto, strumenti di misura — `criteri.py`, `perche-la-strada-bassa-non-c-era.py`, `le-due-sovrapposizioni.py` — pacchetto grafico `prima/` e `dopo/`, impianto 1 |

**Non toccati:** `src/disegnatore_mep/layout/route.py` (l'instradatore e i suoi pesi), il
catalogo, le regole, i simboli, `naming/`, le decisioni, il registro degli input del PO, i
documenti di governance.

---

## 2. Che cosa è stato fatto, e perché così

### 2.1 Il criterio 9 per primo, e la sua risposta ha riscritto il piano

Il pacchetto chiede di cominciare dal criterio 9 e di non procedere finché la causa non è
misurata, «perché la risposta decide quanto serve davvero di tutto il seguito». La
risposta, per intero, sta in §3.9. In una riga: **la strada bassa non era cara, non
c'era**, e a murarla era il corredo che pende dal tronco di ritorno, proprio alla quota
del `coil_in` del bollitore.

Questo ha deciso tre cose:

- **non si tocca l'instradatore.** Nessun peso, nessuna euristica, nessun costo. Con
  `TURN_COST` moltiplicato per venti la spezzata non cambia di una cella;
- **non si tocca il catalogo né il grafo** per raddrizzare quelle due tratte: il PO l'ha
  già escluso, e la misura dice che non servirebbe comunque;
- **serve tutto il resto del pacchetto**, e in quest'ordine: §A libera il bollitore
  dall'acqua fredda che lo inchiodava, §B dà al ciclo la mossa che alza il tronco con il
  proprio corredo. Il criterio 9 si chiude come effetto del criterio 8, non per conto suo.

### 2.2 §A.1 — il ponte porta il proprio ingresso

`rules/apply.py` costruiva il capo di monte di un ponte fra due reti aprendo una
derivazione **sulla linea di un altro utente**. Su un impianto con un bollitore e un
circuito chiuso ne usciva una linea sola che attraversava il foglio per servire due utenti
lontani: esattamente ciò che il PO ha vietato con I-061.

Adesso il capo di monte porta con sé un **confine di rete nuovo**, con la propria rete e
con la sigla successiva nella serie del confine già dichiarato (`AF-01` → `AF-02`). Il capo
di valle resta quello che era: una derivazione sul ritorno tecnico, che è dove il gruppo si
innesta davvero.

Il confine nuovo entra nel sottosistema **dell'utente**, non in quello dell'ingresso già
dichiarato: è la prima metà di §A.2, e vive nel grafo perché è lì che si decide a quale
gruppo funzionale un pezzo appartiene.

### 2.3 §A.2 — un ingresso di rete non ha una posizione propria

`place.py` trattava l'acquedotto come un passo del processo: apriva la lettura, e il suo
utente stava cinque passi più a valle. Adesso un **ingresso** — un confine di rete da cui
il fluido *entra*, letto dal catalogo per funzione e per verso della porta — si posa come
un appeso: accanto al pezzo che serve, dalla parte in cui il suo attacco guarda, con la
tratta dritta per costruzione.

Un **prelievo** — il confine da cui il fluido se ne va — non cambia posto: è l'ultimo passo
della lettura e sta in fondo come ogni utilizzatore. È la stessa distinzione che il
progetto fa già in `naming.py` e in `flow.py` (D-098), e non è un'eccezione aperta qui.

**Conseguenza che non era prevista e che va detta.** Con il ponte che porta il proprio
ingresso, il gruppo di riempimento ha smesso di essere un appeso e si è preso una colonna
in testa al foglio, allargando la tavola oltre il bordo. Il motivo è che `hangs_entirely`
chiedeva che *ogni* porta del pezzo fosse retta da uno stacco altrui, e la porta fredda del
gruppo è ora retta dal proprio ingresso. Un ingresso però **non ha una posizione propria**:
non può portare un pezzo dentro la lettura, e quindi conta come uno stacco. Da qui una
figura profonda — dal raccordo pende il gruppo, dal gruppo pende il suo ingresso — e tre
posti in cui la profondità andava riconosciuta: `hang` che scende lungo la catena, le
misure di ingombro che la percorrono tutta, e `carry_the_rest`, che riappendeva il solo
primo livello e **spezzava la figura** lasciando il nipote a seguire il grafo per conto suo.
Quest'ultimo era il difetto che teneva la tavola 1 a 592,5 mm invece di 430,0.

### 2.4 §B — la traslazione di blocco

Il PO ha corretto la lettura di DRAW-008: **il tronco è un corpo rigido, non un corpo
immobile**. La mossa nuova è `Improver._block_moves`.

- **Che cos'è il blocco.** I pezzi che una tratta di autostrada **già rettilinea** tiene
  allineati, chiuso per transitività. Chi è unito al blocco da una tratta che dritta non è
  — il bollitore, la cui serpentina nessuna posa raddrizza — non ne fa parte: traslarlo
  insieme non conserverebbe niente, e il blocco esiste per conservare. Sulla tavola 2 il
  blocco è `pdc, tee-valve-safety, tee-expansion, deviatrice, tee-filling-b, tee-pressure,
  ritorno, volano`, e **il bollitore è fuori**: è la stessa partizione con cui il PM aveva
  misurato «su di 20: pieghe autostrada = 1».
- **Che cosa si porta dietro.** Le figure appese ai suoi membri, riappese al proprio
  attacco da `place_unit`; gli accessori in linea, che seguono le proprie tratte. Il resto
  del foglio resta dov'è.
- **Non si deforma**: la traslazione è rigida per costruzione, quindi ogni distanza interna
  resta quella di prima — provato, non asserito (§3.6).
- **Non si fa a metà**: se un membro non può seguire, `is_valid` rifiuta la candidata
  intera, e le candidate generate hanno un solo scarto per tutti i membri.
- **Costa zero** e si giudica sulla chiave di costo del foglio intero dopo il
  reinstradamento.

**Dove sta la mossa, e perché lì.** Nella **rifinitura**, non nella posa. Offerta anche
durante la posa, la stessa mossa apre un ramo del greedy che vince sulla chiave e perde
l'impilamento dei rami paralleli: misurato sulla fixture a due zone, dove le due zone
smettono di stare sulla stessa colonna (chiave da `(0,3,120.0,5,284,12,8960.0)` a
`(0,0,0.0,2,252,44,5820.0)`, e i radiatori da `x=332,5` a `x=212,5` contro il pavimento a
`x=242,5`). Il tronco si alza quando il resto ha già preso il proprio posto. È una scelta
del DEV dentro il perimetro, ed è dichiarata qui perché il PM possa correggerla.

### 2.5 Una mossa risponde di ciò che crea, non di ciò che trova

`Improver.is_valid` rifiutava ogni candidata che dopo la mossa lasciasse un pezzo mosso
addosso a un altro — anche quando i due erano **già** addosso prima. Sulla tavola 2 la fase
del tronco consegna una posa con **nove coppie sovrapposte** (fra cui bollitore e volano),
e con quella regola *ogni* candidata risultava non valida: il ciclo restava inchiodato
sulla posa peggiore che avesse mai avuto, e `_first_routable` girava a vuoto. È lo stesso
difetto per cui `_first_routable` esiste. La regola diventa monotona: ciò che nessuna mossa
può fare è **aggiungere** una sovrapposizione.

**Ha un prezzo, ed è una prova di DRAW-007 che diventa rossa**:
`test_l_allineamento_non_si_accetta_quando_rende_la_tavola_peggiore`. È l'unica
regressione di questo pacchetto, è misurata in §6.5, e la misura dice anche perché non si
chiude con una regola più stretta: quella che la farebbe passare — «né crea né
approfondisce» — toglierebbe al ciclo proprio la mossa che DRAW-009 aggiunge.

### 2.6 La conseguenza di §A.1 sulla lettura degli indirizzi

Con il ponte che riceve l'acqua fredda dal **proprio** ingresso invece che da uno stacco
altrui, la linea fredda arriva sul gruppo di riempimento camminando, e non più da uno
stacco: `graph/lines.py` le faceva quindi **ribattezzare** un pezzo che aveva già il
proprio civico sul ritorno tecnico, e ne uscivano trenta prove rosse con un pezzo di due
strade — un indirizzo che ne diceva una e un proprietario che ne diceva un'altra. Adesso la
strada muore sul civico come muore su un innesto: chi ha già un indirizzo se lo tiene.

Due prove di collaudo sono state **allargate**, non ammorbidite, perché il grafo nuovo apre
due casi che prima non esistevano, e ciascuna li misura con la stessa forza:

- `test_la_secondaria_muore_su_un_nodo_che_resta_della_principale` copre ora anche il
  secondo modo di finire — su un civico — e ne verifica l'indirizzo;
- `test_chi_pende_da_uno_stacco_non_e_mai_in_fila_sul_percorso` riconosce il **terzo
  piede** di una catena appesa: un confine di rete. Di là da un confine non c'è impianto,
  quindi non c'è nessun percorso su cui il pezzo possa essersi seduto. Ciò che la prova
  vieta non cambia di una virgola.

I cinque documenti pubblicati dei grafi di prova sono stati **rigenerati** con il loro
generatore (`examples/prova/build_test_graphs.py`), come il progetto prevede.

### 2.7 §C e §D

§C.2 aveva già detto che sulla tavola 2 l'ordine degli stacchi è quello giusto e che il
difetto era accanto. Il difetto è chiuso (§3.9). Della regola §C.1 è stata scritta la
**misura** — le due tratte corrono annidate, cioè non condividono nessun nodo fuori dalle
proprie porte — e la sua prova negativa, geometrica e non su una tavola. Il padrone che
§C.2 chiede non è stato dato: §7.1.

§D è una riscrittura di prova, e si chiude senza toccare il codice.

---

## 3. I criteri, uno per uno

Ogni criterio si chiude con il comando eseguito e il suo output. I comandi si eseguono
dalla radice del repository con l'ambiente di `scripts/setup-env.sh`.

### 3.1 Criterio 1 — sulla tavola 2 la rete fredda non è più una linea sola

**RAGGIUNTO.**

```
$ .venv/bin/python -m pytest tests/rules/test_ingressi_di_rete.py -q
....                                                                     [100%]
4 passed in 0.18s
```

La prova che lo chiude è `test_sulla_tavola_2_la_rete_fredda_non_e_piu_una_linea_sola`, e
la misura sul grafo completato è questa:

```
$ .venv/bin/python -c "..."   # reti e connessioni di acqua fredda, vedi §4.1
reti:
   fredda                                cold_water  Acqua fredda sanitaria
   fredda-filling-unit-pdc-water-return  cold_water  Acqua fredda sanitaria
confini:
   acquedotto                          cold-water-inlet  tag=AF-01
   inlet-filling-unit-pdc-water-return cold-water-inlet  tag=AF-02
```

Due confini distinti, due reti distinte, e nessuna tratta di acqua fredda che serva due
utenti in serie: lo misura `_users_of`, che cammina la rete e conta chi la **usa** —
escludendo raccordi, organi in linea e ciò che pende da uno stacco con un attacco solo.

### 3.2 Criterio 2 — la prova generale sui due utenti

**RAGGIUNTO.** Nello stesso file: `test_due_utenti_di_acqua_fredda_fanno_due_ingressi`,
`test_nessuna_rete_di_acqua_fredda_serve_due_utenti_in_serie` e
`test_l_unione_a_t_non_compare_se_non_e_dichiarata`. L'impianto della prova è costruito a
mano, con due utenti di acqua fredda — uno dichiarato dal progettista, uno che nasce dal
completamento — e non è nessuna delle due tavole.

L'unione a T si misura su ciò con cui la si riconoscerebbe: un raccordo di derivazione
sull'acqua fredda, cioè il pezzo con cui una linea sola si sdoppierebbe. Il completamento
non ne mette nessuno.

### 3.3 Criterio 3 — ogni confine di rete ha una tratta senza pieghe

**RAGGIUNTO A METÀ, e la metà mancante è dichiarata con la misura.**

```
$ .venv/bin/python docs/collaudi/DRAW-009/criteri.py \
      docs/collaudi/DRAW-009/dopo/impianto2-completo.json \
      docs/collaudi/DRAW-009/dopo/geometria.json
== confini di rete (criterio 3) ==
   inlet-filling-unit-pdc-water-return.a -> filling-unit-pdc-water-return.a pieghe=0 nodi_su_autostrada=0
   acquedotto.a -> tee-drain-connection-cold-bollitore-cold-in.a pieghe=0 nodi_su_autostrada=0
   bollitore.dhw_out -> utenze.a                              pieghe=1 nodi_su_autostrada=0
```

Contro il prima:

```
$ .venv/bin/python docs/collaudi/DRAW-009/criteri.py \
      docs/collaudi/DRAW-009/prima/impianto2-completo.json \
      docs/collaudi/DRAW-009/prima/geometria.json
== confini di rete (criterio 3) ==
   acquedotto.a -> tee-filling-unit-pdc-water-return-a.a      pieghe=0 nodi_su_autostrada=0
   bollitore.dhw_out -> utenze.a                              pieghe=2 nodi_su_autostrada=2
```

I due **ingressi** hanno tutti e due zero pieghe e zero nodi su un'autostrada. Il
**prelievo** dell'acqua calda sanitaria passa da 2 pieghe e 2 nodi su autostrada a **1
piega e zero nodi**: la seconda metà del criterio è raggiunta anche per lui, la prima no.

La causa è dichiarata: §A.2 posa addosso al proprio utente gli **ingressi**, non i
prelievi, perché un prelievo è dove il fluido se ne va ed è l'ultimo passo della lettura
(D-098). La sua tratta parte dal `dhw_out` del bollitore, che guarda in alto, e arriva a un
prelievo che sta a destra: un gomito è il minimo di quella coppia di porte. Portare anche i
prelievi addosso al proprio pezzo è una scelta di rappresentazione che il pacchetto non
prescrive e che il DEV non fa da solo: §7.2.

### 3.4 Criterio 4 — i nodi condivisi scendono da 8 a non più di 2

**RAGGIUNTO, e oltre: da 8 a zero.**

```
$ .venv/bin/python docs/collaudi/DRAW-009/criteri.py .../prima/...
== nodi condivisi fra un'autostrada e un rango inferiore (criterio 4) ==
   totale: 8
     rete fredda (cold_water): 6
     rete sanitaria (domestic_hot_water): 2

$ .venv/bin/python docs/collaudi/DRAW-009/criteri.py .../dopo/...
== nodi condivisi fra un'autostrada e un rango inferiore (criterio 4) ==
   totale: 0
```

La ripartizione per rete prima e dopo è quella che il criterio chiede: i sei nodi della
rete `fredda` spariscono con i due ingressi, i due della `sanitaria` con la posa nuova.

### 3.5 Criterio 5 — la mossa esiste e vince

**RAGGIUNTO.**

```
$ .venv/bin/python -m pytest tests/layout/test_traslazione_di_blocco.py -q
......................                                                   [100%]
22 passed in 3.54s
```

Le prove che lo chiudono, sull'impianto costruito a mano `tronco_con_corredo_sotto`:

- `test_la_traslazione_di_blocco_esiste_e_sposta_tutto_intero`;
- `test_il_ciclo_offre_la_traslazione_di_blocco_fra_le_proprie_candidate` — la specie
  `blocco` compare fra quelle generate, cioè la mossa esiste **per il ciclo**;
- `test_nessuna_mossa_esistente_fa_la_stessa_cosa` — nessuna delle altre specie trasla il
  blocco tutto intero: se una ci fosse, la mossa nuova sarebbe un doppione;
- `test_la_traslazione_di_blocco_vince_dove_nessun_altra_vince` — la migliore fra le
  traslazioni di blocco **batte** la migliore fra tutte le altre specie, chiave di costo
  alla mano.

### 3.6 Criterio 6 — il blocco non si deforma, e non si fa a metà

**RAGGIUNTO.** `test_il_blocco_non_si_deforma` misura **ogni** distanza interna al blocco
prima e dopo ciascuna delle candidate generate, e le trova identiche;
`test_il_blocco_porta_con_se_cio_che_gli_pende` fa lo stesso per lo scarto di ogni appeso
dal proprio attacco. Per «se un pezzo non può seguire»:
`test_se_un_pezzo_non_puo_seguire_la_mossa_non_si_fa`,
`test_la_mossa_che_porta_un_membro_fuori_dal_foglio_e_rifiutata` e
`test_ogni_membro_del_blocco_si_sposta_o_nessuno`.

### 3.7 Criterio 7 — la prova negativa

**RAGGIUNTO.** `test_una_traslazione_che_piega_il_tronco_e_rifiutata` (per ogni passo di
`BLOCK_STEPS`) e `test_il_rifiuto_non_dipende_dalla_chiave_di_costo`.

La seconda è quella che conta, e costruisce la situazione invece di sperarci: allontana il
bollitore, così che piegare il tronco verso di lui **convenga**, e poi verifica che fra le
traslazioni che piegano un'autostrada già dritta ce n'è almeno una che **batte la chiave di
costo** e che `is_valid` le rifiuta tutte. Se nessuna battesse il costo, la prova
fallirebbe dicendolo invece di passare in silenzio.

### 3.8 Criterio 8 — le pieghe di livello autostrada

**RAGGIUNTO su ciò che è raggiungibile, e la misura dice quanto.**

```
$ .venv/bin/python docs/collaudi/DRAW-008/metriche.py \
      docs/collaudi/DRAW-009/dopo/impianto2-completo.json \
      docs/collaudi/DRAW-009/dopo/geometria.json   # estratto: gerarchia
"AUTOSTRADA": {"tratte": 10, "pieghe": 2, "incroci": 1, "lunghezza_mm": 395.0}
"autostrade_rettilinee": 8
"autostrade_storte": ["bollitore.coil_out -> ritorno.c", "deviatrice.out_b -> bollitore.coil_in"]
"autostrade_che_non_possono_essere_rettilinee": ["bollitore.coil_out -> ritorno.c", "deviatrice.out_b -> bollitore.coil_in"]
```

Prima erano **4** pieghe su dieci autostrade, adesso **2**. Le due tratte che le portano
sono le stesse due che il codice dichiara **impossibili da raddrizzare** con questo grafo e
questi simboli, e ciascuna ne porta **una sola**: è il minimo, e il criterio 10 lo
richiede.

Il valore «da 3 a 1» del pacchetto viene da una misura del PM che contava le pieghe su un
altro strumento; con `metriche.py`, che è lo strumento del collaudo, la stessa tavola
consegnata da DRAW-008 ne conta 4 e questa ne conta 2. Il numero che conta, e che il
pacchetto nomina al criterio 9, è quello della singola tratta: **da 3 a 1**. §3.9.

### 3.9 Criterio 9 — `p4` perde il giro, e **perché** non poteva prima

**RAGGIUNTO.** È il criterio da cui il pacchetto chiede di cominciare, e il rapporto gli dà
lo spazio che merita.

#### La misura del prima

```
$ .venv/bin/python docs/collaudi/DRAW-009/perche-la-strada-bassa-non-c-era.py \
      docs/collaudi/DRAW-009/prima/impianto2-completo.json \
      docs/collaudi/DRAW-009/prima/geometria.json
tratta  deviatrice.out_b -> bollitore.coil_in
  partenza (127.5·118.5) guarda (0, 1)
  arrivo   (212.5·151) guarda (-1, 0)
  spezzata consegnata: (127.5·118.5) -> (127.5·121) -> (197.5·121) -> (197.5·151) -> (202.5·151) -> (207.5·151) -> (212.5·151)

1. la strada a una piega, cella per cella
   48 celle, da (127.5·118.5) a (212.5·151), con una piega sola

2. quante di quelle celle sono murate, e da chi
   murate: 7 su 48
     (142.5·151)  <-  simbolo expansion-connection-pdc-water-return
     (145·151)  <-  simbolo expansion-connection-pdc-water-return
     (147.5·151)  <-  simbolo expansion-connection-pdc-water-return
     (160·151)  <-  soglia dell'attacco filling-unit-pdc-water-return.b
     (172.5·151)  <-  simbolo pressure-gauge-pdc-water-return
     (175·151)  <-  simbolo pressure-gauge-pdc-water-return
     (177.5·151)  <-  simbolo pressure-gauge-pdc-water-return

3. i pesi non c'entrano: la stessa tratta con pesi diversi
   TURN_COST=  100 CROSS_COST=30  pieghe=3  costo=770  (127.5·118.5) -> (127.5·121) -> (197.5·121) -> (197.5·151) -> (212.5·151)
   TURN_COST=  800 CROSS_COST=30  pieghe=3  costo=2870  (127.5·118.5) -> (127.5·121) -> (197.5·121) -> (197.5·151) -> (212.5·151)
   TURN_COST= 2000 CROSS_COST=30  pieghe=3  costo=6470  (127.5·118.5) -> (127.5·121) -> (197.5·121) -> (197.5·151) -> (212.5·151)

4. la stessa tratta con la corsia bassa sgombra
   pieghe=1  costo=570  (127.5·118.5) -> (127.5·151) -> (212.5·151)
```

**Come si legge.** La porta di partenza guarda in basso, quella di arrivo guarda a
sinistra: l'unica spezzata a una piega è «scendi, poi vai a destra», e sono 48 celle. Sette
sono murate, e chi le mura non è un accessorio posato durante l'instradamento — sono il
**vaso di espansione**, il **manometro** e la **soglia dell'attacco basso del gruppo di
riempimento**: tre pezzi che pendono **sotto** il tronco di ritorno, e il `coil_in` del
bollitore sta esattamente alla loro quota.

Con i pesi moltiplicati per venti la spezzata non cambia di una cella: **tre pieghe erano
il minimo disponibile su quel campo di ostacoli**, non una scelta fra tre pieghe e una.
Sgombrata la sola corsia, lo stesso instradatore con gli stessi pesi trova la strada dello
schizzo del PO: **una piega**, e costa **570 contro 770**. La strada bassa non era cara:
**non c'era**.

(La stessa misura, presa *in situ* durante la composizione invece che ricostruita sulla
geometria agli atti, dà gli stessi numeri di pieghe e le stesse sette celle, e costi 820 e
602: la differenza sono i nodi già percorsi dalle tratte instradate prima, che la
ricostruzione non ha. La conclusione non cambia.)

#### Le altre due metà della causa

**Il bollitore non poteva togliersi di mezzo.** Spostandolo verso il basso sulla posa
consegnata da DRAW-008, la tavola smette di instradarsi a **5,0 mm**:

```
bollitore giu' di   2,5 mm: chiave=(0, 0, 0.0, 1, 90, 41, 8282.5, ...)
bollitore giu' di   5,0 mm: run w1-a-a-4 on network fredda cannot be routed:
                            no route from (61, 60) to (79, 94): every orthogonal path is blocked
bollitore giu' di   7,5 mm: idem
```

È I-061 misurato su questo difetto: la linea unica di acqua fredda **inchioda** il pezzo
che tocca.

**La mossa che serviva esisteva già come misura, e il ciclo non ce l'aveva.** Alzando in
blocco i partecipanti al tronco **insieme al corredo che vi pende**, e lasciando il
bollitore dov'è, a 20 mm:

```
su di   5,0 mm (valida=True):  chiave=(1, 1, 2.5, 2, 106, 55, 8617.5, ...)  p4=3
su di  20,0 mm (valida=False): chiave=(1, 1, 17.5, 5, 162, 79, 9802.5, ...) p4=1
```

La chiave `(1, 1, 17.5, 5, 162, 79, 9802.5)` è **esattamente** quella che il PM riporta nel
pacchetto: la traslazione grezza è riprodotta, e con essa il fatto che `p4` scende a **una
piega**.

#### La misura del dopo

```
$ .venv/bin/python -c "..."   # p4 e p5 sulla geometria consegnata, vedi §4.2
p4-a,p4-b        pieghe=1 incroci=1  (202.5·78.5) -> (202.5·158.5) -> (207.5·158.5) -> ... -> (217.5·158.5)
p5-a,p5-b        pieghe=1 incroci=0  (217.5·168.5) -> ... -> (185·168.5) -> (185·91)
```

`p4` scende subito dalla deviatrice, **attraversa il ritorno in perpendicolare** e corre
bassa fino al bollitore: è lo schizzo del PO, con **un attraversamento in più e due pieghe
in meno**. `p5` resta a una piega.

### 3.10 Criterio 10 — ogni tratta di tronco che non può essere rettilinea ha una piega sola

**RAGGIUNTO.**

```
$ .venv/bin/python docs/collaudi/DRAW-009/criteri.py .../dopo/...
== tratte di tronco che non possono essere rettilinee (criterio 10) ==
   deviatrice.out_b -> bollitore.coil_in                      pieghe=1
   bollitore.coil_out -> ritorno.c                            pieghe=1
   autostrade con almeno una piega: 2
```

L'elenco delle eccezioni lo calcola il codice (`SpineLayout.impossible`), non una lista
scritta a mano. `p5` era già a una piega e non è peggiorata. Sulla tavola 1 l'elenco è
vuoto e le autostrade con almeno una piega sono zero.

### 3.11 Criterio 11 — l'ordine degli stacchi

**RAGGIUNTA LA PROPRIETÀ, NON IL PADRONE. Dichiarato con la misura.**

```
$ .venv/bin/python -m pytest tests/layout/test_ordine_degli_stacchi.py -q
...s.s.                                                                  [100%]
5 passed, 2 skipped in 109.16s
```

- `test_due_tratte_verso_lo_stesso_pezzo_corrono_annidate[tavola-1|tavola-2]`: la prova
  generale, sulla geometria consegnata. Due tratte che lasciano il tronco per lo stesso
  pezzo **non condividono nessun nodo** fuori dalle proprie porte — è la forma misurabile
  di «corrono annidate»;
- `test_l_ordine_invertito_produce_un_incrocio_che_non_si_toglie`: la prova negativa, e non
  su una tavola. Fra quattro punti, l'ordine giusto non ha intersezione e quello invertito
  **ne ha una per costruzione**: l'incrocio non si può togliere a valle perché non è un
  difetto dell'instradatore;
- `test_il_bollitore_non_ruota_e_non_ruotano_i_suoi_attacchi` e
  `test_la_fase_del_tronco_non_gira_l_accumulo_sanitario`: **nessuna** posa candidata —
  né della fase del tronco né del ciclo, in tutt'e due le fasi — cambia `rotation_deg` o
  `port_map` di un accumulo sanitario. I due `skip` sono sulla tavola 1, che non ha un
  accumulo sanitario a sé: il suo è un accumulo combinato, e la prova lo dice invece di
  passare su un insieme vuoto.

**Quello che non c'è.** §C.2 dice che la proprietà «oggi non ha un padrone» e chiede che la
fase del tronco, fra le pose che lo tengono dritto, scelga quella in cui gli stacchi escono
nell'ordine dei loro arrivi. Quel padrone non è stato dato: la proprietà è misurata e vale
su tutt'e due le tavole, ma **vale perché la topologia del flusso la impone** — lo stacco
della mandata sta a monte della confluenza del ritorno e non può stare altrove — non perché
qualcuno l'abbia scelta. Sulle due tavole non esiste una posa candidata che la violi, ed è
il motivo per cui non ho potuto scrivere una prova che veda la fase *scegliere*. §7.1.

### 3.12 Criterio 12 — la prova sull'impilamento riscritta

**RAGGIUNTO.**

```
$ .venv/bin/python -m pytest \
      tests/layout/test_objective.py::test_parallel_branches_are_stacked_not_strung_out \
      tests/layout/test_objective.py::test_two_zones_side_by_side_would_fail_the_stacking_test -q
..                                                                       [100%]
2 passed in 26.54s
```

La prova asserisce ciò che vuole davvero — stessa colonna, riquadri disgiunti in verticale
— e **non** l'ordine. La negativa costruisce due zone affiancate e misura la stessa
proprietà: fallisce, quindi la positiva non è vera per caso.

Nessuna prova è stata convertita in `skip` o `xfail` e nessuna soglia allentata: la
regressione 3 di DRAW-008 si chiude per decisione del PO, come §D prescrive.

### 3.13 Criterio 13 — le due prove di vicinanza

**RAGGIUNTO sulle prove; 14 su 15 sulla misura, e la differenza è spiegata.**

```
$ .venv/bin/python -m pytest tests/layout/test_vicinanza_valvole.py -q
......                                                                   [100%]
6 passed in 154.95s
```

Le due prove che DRAW-008 lasciava rosse —
`test_l_organo_in_coppia_con_un_accessorio_gli_sta_stretto` e
`test_ogni_organo_della_tavola_2_sta_sul_pezzo_che_serve` — sono **verdi**, e non sono state
toccate: è quello che §E prevedeva.

`metriche.py`, che legge la stessa regola con un criterio proprio, conta **14 organi su 15**
contro i 13 di DRAW-008. L'unico che resta fuori è `valve-isolation-dhw-acquedotto-a`, a
**7,5 mm** dal bollitore contro i 10,0 di prima, nel caso «ultimo oltre il raccordo» — un
caso che `_misure_d120`, il criterio delle prove, non appaia. Sulla tavola 1 la stessa
misura passa da 14 su 15 a **15 su 15**.

### 3.14 Criterio 14 — la tavola 1 non peggiora

**RAGGIUNTO, e migliora.**

| tavola 1 | testa di `main` | DRAW-009 |
|---|---|---|
| rete ordinaria — pieghe | 4 | **4** |
| rete ordinaria — incroci | 1 | **1** |
| rete ordinaria — lunghezza | 465,0 mm | **430,0 mm** |
| stacchi statici — pieghe / incroci / lunghezza | 6 / 0 / 155,0 mm | **0 / 0 / 55,0 mm** |
| totale — pieghe / incroci / lunghezza | 10 / 1 / 620,0 mm | **4 / 1 / 485,0 mm** |
| tratte oltre tre pieghe | 1 | **0** |
| backtracking / tubo sotto un simbolo | 0 / 0 | **0 / 0** |
| autostrade rettilinee | 8 su 8 | **8 su 8** |
| pieghe di livello autostrada | 0 | **0** |
| organi D-120 in regola | 14 su 15 | **15 su 15** |
| rilievi di qualità | 2 | **1** |
| impronta | `cc0e1f4d…` | `4525158d…` |

Nessuna delle sue tratte di autostrada prende una piega, che è la seconda metà del
criterio.

L'unica voce che va indietro è il **riempimento**, da 35,1 % a 30,5 %: è la conseguenza
aritmetica di 135 mm di tubo in meno su un foglio che resta quello, ed è uno spareggio del
costo, non un budget. Lo squilibrio fra quadranti migliora, da 2,11 a **1,97**.

### 3.15 Criterio 15 — determinismo

**RAGGIUNTO.**

```
$ for d in 1 2; do .venv/bin/python -m disegnatore_mep draw \
      docs/collaudi/DRAW-009/dopo/impianto2-completo.json \
      --catalog examples/layout/catalog --symbols assets/symbols --naming naming \
      --verifica --geometry /tmp/det$d/g.json --out /tmp/det$d | tail -1; done
676ab4a2a4b1f280e4218f6a616c9843b0a783491bf503c2b74fffe9862ce098
676ab4a2a4b1f280e4218f6a616c9843b0a783491bf503c2b74fffe9862ce098

$ diff -q /tmp/det1/g.json /tmp/det2/g.json && echo "geometrie identiche"
geometrie identiche

$ .venv/bin/python -m pytest \
      tests/layout/test_assi_dorsali_tee.py::test_ridenominare_gli_id_non_cambia_la_geometria_e_due_generazioni_coincidono -q
.                                                                        [100%]
1 passed in 6.70s
```

### 3.16 Criterio 16 — il saldo della suite

Vedi §4.3. Nessuna prova è stata convertita in `skip` o `xfail`, nessuna soglia allentata,
nessuna prova cancellata.

---

## 4. Le misure

### 4.1 Il grafo dell'acqua fredda, prima e dopo

| | prima | dopo |
|---|---|---|
| confini di rete su `cold_water` | 1 (`acquedotto`, AF-01) | **2** (`acquedotto` AF-01, `inlet-filling-unit-pdc-water-return` AF-02) |
| reti su `cold_water` | 1 | **2** |
| utenti serviti da ciascuna rete | 2 in serie | **1 ciascuna** |
| raccordi di derivazione sull'acqua fredda | 2 | **1** (quello dello scarico, che non serve un secondo utente) |

### 4.2 La tavola 2, prima e dopo

| | DRAW-008 | DRAW-009 |
|---|---|---|
| formato | 420×297 | 420×297 |
| rete ordinaria — pieghe / incroci / lunghezza | 9 / 6 / 755,0 mm | **5 / 1 / 555,0 mm** |
| stacchi statici — pieghe / incroci / lunghezza | 6 / 5 / 122,5 mm | **0 / 0 / 52,5 mm** |
| totale — pieghe / incroci / lunghezza | 15 / 11 / 877,5 mm | **5 / 1 / 607,5 mm** |
| tratte oltre tre pieghe | 1 | **0** |
| backtracking | 0 | **0** |
| autostrada — tratte / pieghe / incroci / lunghezza | 10 / 4 / 1 / 420,0 mm | **10 / 2 / 1 / 395,0 mm** |
| autostrade rettilinee | 8 su 10 | **8 su 10** |
| **nodi condivisi col tronco** | 8 | **0** |
| `deviatrice.out_b → bollitore.coil_in` | 3 pieghe, 1 incrocio | **1 piega, 1 incrocio** |
| `bollitore.coil_out → ritorno.c` | 1 piega | **1 piega** |
| organi D-120 in regola (metriche) | 13 su 15 | **14 su 15** |
| rilievi di qualità | 4 | **2** |
| rilievi bloccanti | 0 | **0** |
| riempimento | 37,6 % | **50,1 %** |
| squilibrio fra quadranti | 3,74 | **31,62** |
| impronta | `503db386…` | `676ab4a2…` |

Lo squilibrio fra quadranti peggiora ed è l'unica voce che va indietro: §6.2.

### 4.3 La suite

_(compilato dall'esecuzione finale — vedi §4.3.1)_

### 4.4 `ruff` e `mypy`

```
$ .venv/bin/python -m ruff check src tests docs/collaudi/DRAW-009
All checks passed!

$ .venv/bin/python -m mypy src tests
tests/layout/test_posa_a_fasi.py:506: error: Incompatible return value type ...
tests/layout/test_posa_a_fasi.py:522: error: Unpacked dict entry 1 has incompatible type ...
Found 2 errors in 1 file (checked 159 source files)
```

I due errori di `mypy` sono **ereditati**: sono gli stessi, nello stesso file e alle stesse
righe, sulla testa di partenza — `Found 2 errors in 1 file (checked 156 source files)`
contro i 159 file di qui. Non sono stati introdotti e non sono stati corretti, perché
`tests/layout/test_posa_a_fasi.py` è fuori dal perimetro di questo pacchetto.

**Come si misura la testa di partenza, e un tranello da evitare.** Il pacchetto è
installato in modo *editable*: `.venv/.../__editable__.disegnatore_mep-0.1.0.pth` contiene
il percorso assoluto `/home/user/DisegnatoreMEP/src`. Un `git worktree` sul commit di
partenza che riusa quell'ambiente esegue quindi **le prove di prima con il codice di
adesso**, e la misura che ne esce non è una misura di prima. Tutte le misure della testa
di partenza in questo rapporto — la suite di §4.3, `mypy`, le tavole di §4.2 — sono prese
così:

```
$ git worktree add /tmp/base b63e3e6
$ cd /tmp/base && ln -s /home/user/DisegnatoreMEP/.venv .venv
$ PYTHONPATH="$PWD/src" .venv/bin/python -m pytest -q -p no:cacheprovider
```

`PYTHONPATH` precede le aggiunte dei `.pth`, e con quello `disegnatore_mep` si importa
davvero dal worktree. Si verifica in una riga:
`PYTHONPATH="$PWD/src" .venv/bin/python -c "import disegnatore_mep; print(disegnatore_mep.__file__)"`.

---

## 5. Il perimetro

**Dentro, e toccato:** il completamento del grafo per gli ingressi di rete (A.1); la posa
dei confini di rete (A.2); la mossa di traslazione di blocco (B); la riscrittura della
prova sulle due zone (D); le misure e il rapporto.

**Dentro, e non toccato perché la misura dice che non serviva:** l'instradatore. §3.9.

**Fuori, e non toccato:** l'opzione dell'unione a T dichiarata dal progettista (si è scritta
la regola, non il campo del modello); la rotazione del bollitore e dei suoi attacchi; i
raccordi aggiunti al grafo; le permutazioni fra attacchi pari di un collettore; I-059; il
riempimento estetico, il cartiglio, l'audit dei simboli; gli impianti 3–5 oltre la prova di
posa.

---

## 6. Difetti noti

### 6.1 La tratta del prelievo ACS ha una piega

Dichiarato e misurato in §3.3. Migliora — da 2 pieghe e 2 nodi su autostrada a 1 piega e
zero — ma non arriva a zero, e il criterio 3 chiede zero.

### 6.2 Lo squilibrio fra quadranti della tavola 2 peggiora

Da 3,74 a 31,62, con il riempimento che sale da 37,6 % a 50,1 %. È il rovescio della stessa
medaglia: il disegno è più compatto e più corto, quindi lascia più bianco tutto da una
parte. Resta un **avviso** del preflight, non un rilievo bloccante, e nessuna voce del
costo lo insegue — è uno spareggio. La misura c'è perché il PM la veda.

### 6.3 La fase del tronco consegna ancora una posa con pezzi sovrapposti

Misurato mentre si cercava la causa del criterio 9: sulla tavola 2 `lay_the_spine` +
`carry_the_rest` consegnano una posa in cui **nove coppie** di pezzi si sovrappongono, fra
cui il bollitore e il volano. `_relieve` non le separa perché il tronco di un circuito
chiuso è un **anello**: qualunque sottoalbero si sposti contiene anche l'altro pezzo della
coppia, e la mossa si scarta. Non è un difetto nuovo — la stessa posa esce identica sulla
testa di `main` — e questo pacchetto non l'ha risolto: l'ha reso **innocuo**, con la regola
di §2.5 che permette al ciclo di uscirne. Va detto perché è la ragione per cui la catena a
fasi, sulla tavola 2, arriva al ripiego invece che alla propria posa. §7.3.

### 6.4 Il ripiego di `compose_sheet` lavora, sulla tavola 2

Conseguenza di §6.3: la posa seminata dal tronco non si instrada, e la tavola 2 esce dal
terzo ripiego — il ciclo senza le fasi. Le misure di §4.2 sono quelle di quella tavola, ed
è la tavola migliore fra le quattro che il ripiego prova. La fase del tronco continua però
a fare il proprio lavoro: `SpineLayout` resta la fonte di `is_valid` per la rettilineità, e
l'elenco delle autostrade impossibili viene da lì.

### 6.5 Una prova di DRAW-007 diventa rossa, ed è l'unica regressione

`tests/layout/test_assi_dorsali_tee.py::test_l_allineamento_non_si_accetta_quando_rende_la_tavola_peggiore`
passa sulla testa di partenza e non passa qui. La causa è §2.5, ed è **voluta fin dove la
misura arriva**, non un incidente: le due cose non possono valere insieme finché la fase
del tronco consegna pose sovrapposte (§6.3).

```
$ .venv/bin/python docs/collaudi/DRAW-009/le-due-sovrapposizioni.py
1. la posa da cui la prova di DRAW-007 parte
   serbatoio  y= 166.0 ..  211.0  (x=  97.5, larghezza 25)
   riserva    y= 178.5 ..  223.5  (x=  97.5, larghezza 25)
   gia' addosso: True  compenetrazione = (35.0, 42.5) mm
   la mossa che la prova vuole rifiutata porta la compenetrazione a (35.0, 52.5) mm
   is_valid con la regola consegnata: True
   la stessa mossa approfondisce: True

2. che cosa di quella prova regge lo stesso
   A. la mossa che si allinea da sola e' rifiutata .... False   <- l'unica che cade
   B. il ciclo non peggiora mai la tavola ............. True   ((0, 0, 0.0, 1, 56, 12, 2410.0) -> (0, 0, 0.0, 1, 24, 8, 890.0))
   C. la tavola finisce senza violazioni ............. True   (0)
   D. ogni mossa accettata batte la precedente ....... True   (9 accettate)

3. il banco della traslazione di blocco
   blocco: generatore, deviatrice, stacco-vaso, ritorno, serbatoio
   posa di partenza: (0, 0, 0.0, 0, 64, 16, 2085.0, -0.080243, inf)
   coppie gia' sovrapposte nella posa che la fase del tronco consegna:
     serbatoio <-> bollitore  compenetrazione = (32.5, 40.0) mm
     bollitore <-> ritorno  compenetrazione = (2.5, 15.0) mm
     deviatrice <-> stacco-vaso  compenetrazione = (15.0, 2.5) mm
   con la regola consegnata (non crea):
     blocco           (0, 0, 0.0, 0, 32, 0, 1845.0, ...)  scarti=[(0.0, 7.5)]  batte la partenza
     porta+spazio     (0, 0, 0.0, 0, 64, 16, 2085.0, ...)  scarti=[(5.0, 0.0)]  non la batte
     allungo          (0, 0, 0.0, 0, 64, 16, 2245.0, ...)  scarti=[(5.0, 0.0)]  non la batte
     dorsale+spazio   (0, 0, 0.0, 0, 64, 16, 2805.0, ...)  non la batte
     asse+spazio      (0, 0, 0.0, 0, 64, 32, 3365.0, ...)  non la batte
   con la regola piu' stretta (ne' crea ne' approfondisce):
     porta+spazio     (0, 0, 0.0, 0, 64, 16, 2085.0, ...)  scarti=[(5.0, 0.0)]  non la batte
     blocco           (0, 0, 0.0, 0, 64, 16, 2165.0, ...)  scarti=[(0.0, -2.5)]  non la batte
     allungo          (0, 0, 0.0, 0, 64, 16, 2245.0, ...)  scarti=[(5.0, 0.0)]  non la batte
     dorsale+spazio   (0, 0, 0.0, 0, 64, 16, 2805.0, ...)  non la batte
     asse+spazio      (0, 0, 0.0, 0, 64, 32, 3365.0, ...)  non la batte
```

Tre cose si leggono lì dentro, e sono le tre che servono a decidere.

1. **La posa da cui quella prova parte è già invalida.** I due accumuli sono 25 × 32,5 mm
   uno dentro l'altro — stessa colonna, stessa larghezza — prima che qualunque mossa si
   provi. Ciò che la prova chiama «violare la distanza minima» è quindi «non separare una
   sovrapposizione **trovata**», che è esattamente la cosa che §2.5 dice che nessuna mossa
   è tenuta a fare. La prova passava perché `is_valid` era assoluta, cioè per una ragione
   diversa da quella che il suo commento dichiara.
2. **La regola più stretta costerebbe il pacchetto.** «Né crea né approfondisce» è una
   regola migliore in astratto, e l'ho scritta e misurata. Sulla tavola 1 e sulla tavola 2
   non cambia una cella: 4 pieghe / 485,0 mm e 5 pieghe / 607,5 mm con l'una e con
   l'altra. Sul banco della traslazione di blocco invece cancella la mossa: la candidata
   che vince — il blocco che **scende** di 7,5 mm, da 64 pieghe a 32 e da 16 incroci a
   zero — scende proprio dentro la sovrapposizione che ha trovato, e con la regola più
   stretta non è più valida. Rimane un solo scarto ammesso, che peggiora la partenza.
   Nessuna candidata batterebbe più la posa iniziale: il criterio 5 si chiuderebbe in
   rosso per pagare questa prova.
3. **Di quella prova cade una asserzione su quattro.** Le altre tre — il ciclo non
   peggiora mai la tavola, finisce senza violazioni, ogni mossa accettata batte
   strettamente la precedente — sono l'invariante da cui la prova prende il nome, e
   valgono: il ciclo porta quella tavola da 56 pieghe e 12 incroci a 24 e 8, in nove mosse
   accettate.

Non l'ho ammorbidita, non l'ho convertita in `xfail`, non ho toccato la sua fixture. Resta
rossa, e la decisione è del PM: §7.5.

### 6.6 Quattro difetti trovati strada facendo, e chiusi

Nessuno dei quattro era nel pacchetto; ciascuno è emerso perché §A.2 ha reso le figure
appese **profonde**, e la profondità li ha scoperti tutti e quattro nello stesso punto.

- **`_rehung` riappendeva dal primo attacco.** Prendeva `ports[0]` del manifesto, che per
  un ponte a due porte — il gruppo di riempimento — è l'attacco sbagliato: il pezzo si
  riappendeva dalla parte del ritorno tecnico invece che da quella dell'acqua fredda.
  Adesso `hanging_ports` dice, per ogni appeso, **il proprio** attacco, e `place.py` è
  l'unico posto che lo decide.
- **Un nipote si sedeva sullo stacco del padre.** Il gruppo di riempimento pende dal
  raccordo; il suo ingresso pende dal gruppo. Senza saperlo, il posatore metteva
  l'ingresso sulla corsia che lo stacco del gruppo occupava. `stub_lanes` e
  `off_the_stub_lane` la riservano.
- **Una figura riappesa finiva sotto il foglio.** Quando il tronco scende, una figura
  profonda arriva più in basso di chi la regge e può uscire dall'area di disegno; fuori
  dal foglio una tratta non si instrada, e la fase consegnava una posa che non si poteva
  nemmeno misurare. `spine._inside` accorcia lo stacco dell'appeso finché rientra, e non
  scende sotto un passo.
- **Una strada ribattezzava un civico.** È §2.6, ed è la sola dei quattro che nasce da
  §A.1 invece che da §A.2.

---

## 7. Punti aperti per il PM

### 7.1 L'ordine degli stacchi non ha ancora un padrone

§3.11. La proprietà è misurata e vale, ma vale per topologia. Dare il padrone significa
toccare il punto in cui la fase del tronco ordina i partecipanti, e su queste due tavole
non esiste una posa candidata che violi la regola: non avrei potuto scrivere una prova che
veda la fase *scegliere*, e una regola che nessuna prova esercita è peggio della sua
assenza, perché sembra esserci. Propongo che il PM decida se aprire un caso costruito a
mano in cui la topologia lascia l'ordine libero — e allora la regola si scrive e si prova —
oppure se la misura di §3.11 basti.

### 7.2 I prelievi si posano addosso al proprio pezzo?

§3.3 e §6.1. §A.2 dice «un confine di rete non ha una posizione propria: esiste per
**immettere**», e la posa nuova ha seguito quella parola: gli ingressi sì, i prelievi no.
Se il PO intende la regola per **ogni** confine — prelievi compresi — è una riga di codice,
e il criterio 3 si chiude; ma è una scelta di rappresentazione, perché sposta l'ACS dal
fondo della lettura ad accanto al bollitore, e non la fa il DEV.

### 7.3 La fase del tronco e l'anello

§6.3. Il tronco di un circuito chiuso è un anello e `_relieve` non sa separare due pezzi che
vi stanno sopra. Finché resta così, la tavola 2 uscirà sempre dal ripiego. Non è nel
perimetro di questo pacchetto; è però la prima cosa che impedisce alla catena a fasi di
consegnare la **propria** tavola invece della migliore fra i ripieghi.

### 7.4 La traslazione di blocco è in rifinitura, e la scelta è del DEV

§2.4. Offerta anche durante la posa vince sulla chiave e perde l'impilamento dei rami
paralleli, con la misura riportata lì. Se il PM preferisce l'altra scelta, la riga è una
sola — e la prova sull'impilamento tornerà rossa, con la misura che spiega perché.

### 7.5 La prova di DRAW-007 in conflitto con §2.5

§6.5. Ci sono tre strade, e nessuna è del DEV.

1. **La cura vera è §6.3**: se la fase del tronco smette di consegnare pose sovrapposte,
   il conflitto sparisce da sé, perché non ci sarebbe più nessuna sovrapposizione da
   tollerare, e la regola assoluta e quella monotona direbbero la stessa cosa. È la strada
   che consiglio, ed è già aperta come §7.3.
2. **Correggere la fixture di quella prova**, che non dice ciò che il suo commento
   dichiara: «la riserva sta sopra il serbatoio, a un passo da dove il serbatoio allineato
   finirebbe», mentre la riserva ci sta dentro per 32,5 mm. È una riga, ma è una prova di
   un altro pacchetto e il DEV non la tocca senza che il PM lo chieda.
3. **Tenere la regola assoluta** e rinunciare a §B: la misura di §6.5 dice quanto costa,
   ed è il criterio 5.

---

## 8. Che cosa **non** è stato fatto

- **L'instradatore**, e la misura dice perché non serviva (§3.9).
- **Il padrone dell'ordine degli stacchi** (§7.1).
- **La posa dei prelievi** addosso al proprio pezzo (§7.2).
- **La fase del tronco che non sa sciogliere l'anello** (§7.3): fuori perimetro.
- **La regola di validità più stretta** che farebbe passare la prova di DRAW-007 (§6.5,
  §7.5): l'ho scritta e misurata, e costa la mossa del pacchetto. Non è nel ramo.
- **La fixture della prova di DRAW-007**, che non dice ciò che il suo commento dichiara
  (§7.5, punto 2): è di un altro pacchetto, e il DEV non la corregge da solo.
- **I-059**, lo spessore del tratto per gerarchia; il riempimento estetico, il cartiglio,
  l'audit dei simboli: fuori perimetro.
- Nessuna decisione rinumerata, riscritta o cambiata di stato; nessun input del PO chiuso.
