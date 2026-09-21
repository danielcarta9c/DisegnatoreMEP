# Le regole del piano

**Aperto il 20 settembre 2026 · Stato: vigente, e per dichiarazione del PO non è finito**

> Le regole con cui si **compone** una tavola. Non sono pesi da minimizzare: sono le
> istruzioni che il pianificatore segue e che il revisore verifica
> (`ARCHITETTURA-DEL-PIANO.md`, D-151).

## Come si scrive una regola qui, e perché così

**Una regola è un controllo che sa nominare la propria violazione** (D-153). Se non si può
misurare, il revisore non la può usare, e resta un'intenzione: è la differenza fra
«l'autostrada deve essere dritta» e «la tratta `s3` piega quattro volte, e su un'autostrada
le pieghe ammesse sono zero».

Ne seguono tre obblighi per chi aggiunge una riga:

1. **una fonte** — una decisione, un input del PO, la ricerca del 4 agosto, o la tavola che
   l'ha generata. Una riga senza fonte non entra: è così che è nata la funzione di costo;
2. **un controllo**, con il suo nome. Se non esiste ancora, si scrive `da scrivere` e si dice
   che cosa dovrebbe misurare. Una regola senza controllo è lavoro aperto, non una regola;
3. **una tavola** su cui la violazione si vede, quando c'è.

**Le regole si aggiungono componendo, una tavola alla volta** (D-153) — non in astratto.

---

## L'ordine in cui si compone — **prima le autostrade**

**È la disposizione del PO del 20 settembre 2026**, e viene prima di ogni regola di questo
foglio perché dice **in che ordine** si applicano:

> «Sposta le macchine in modo che le linee delle autostrade vengano con pochissime curve,
> poi attacchi il resto delle valvole piccole e strade secondarie. Ma **il disegno nasce
> dalle linee delle autostrade**. Le macchine o cose in parallelo si disegnano come ti ho
> già fatto vedere. LE AUTOSTRADE CON POCHE CURVE e pochi sormonti.»

Il procedimento, in quest'ordine e non in un altro:

1. **Leggi le porte delle macchine di spina.** La quota di un'autostrada **non si sceglie**:
   è quella della porta che la genera. Un `buffer-four-port` ha `primary_in` a **+5** dalla
   propria origine e `primary_out` a **+20**; una pompa di calore ha `water_supply` a **+5**
   e `water_return` a **+20**. Due macchine con lo **stesso y di origine** danno **due
   autostrade perfettamente rette**, gratis.
2. **Posa le macchine su quelle quote.** È la mossa che decide la tavola. Tutto il resto si
   adatta.
3. **Chi sta in parallelo si impila** (A2) e si unisce con **una verticale sola**, corta,
   **accanto alle macchine** (B3) — non in mezzo al foglio. Ogni macchina ci entra con uno
   **stacco orizzontale corto**.
4. **Tira le autostrade, e guarda che siano rette** prima di appendere qualunque cosa.
5. **Solo adesso** appendi valvole, strumenti, confini di rete (A4) e strade secondarie.

⚠ **Un pezzo che sta su un'autostrada si posa sulla quota dell'autostrada.** È l'errore che
ha prodotto le tavole del 20 settembre: il tronco del ritorno primario dell'impianto 5 stava
**20 mm sotto** la quota di `volano.primary_out`, e per raggiungerla risaliva con una
verticale di **120 mm** che si portava dietro manometro, riempimento, vaso e defangatore.
Rimesso sulla quota, il tronco è **una retta sola** dal volano fino all'ultima pompa.

**L'attrezzo per farlo esiste e si usa prima di comporre**, non dopo:
`layout/autostrade.py::porte_in_tavola` dice dove sta ogni porta di ogni pezzo posato, e
`autostrade_in_tavola` + `pieghe_dell_autostrada` dicono quali catene sono autostrade e
quante pieghe fanno, **spezzata per spezzata**.

**Non è solo nostra.** Caleffi, *Idraulica* n. 25 (dicembre 2003), monografico «Il disegno
degli impianti idrotermosanitari», racconta di aver dovuto rifare l'archivio dei blocchi
perché erano «disegni svolti in modo autonomo, **non pensati in modo specifico per essere fra
loro facilmente componibili**… i **collettori non si raccordavano alle derivazioni delle
caldaie**», e la cura è stata predisporli «per poter essere utilizzati come mattoncini Lego
facilmente assemblabili fra loro». È lo stesso punto: **le quote delle porte devono
combaciare fra i pezzi che si uniscono**, o la linea che li unisce piega.

⛔ **E c'è una cosa che il piano NON può dire, ed è la ragione di metà dei difetti.** Il
piano dice **dove stanno i pezzi**, e **niente** su dove le autostrade devono poter passare.
La forma della spezzata la sceglie l'instradatore sul costo: chiedergli «scendi e fai una
curva sola» **non si può scrivere**. L'unica leva del piano è **togliere di mezzo chi occupa
la strada**.

*Il caso, misurato il 20 settembre 2026.* Il PO, sull'impianto 5: «perché dai la curva subito
dopo la valvola a tre vie? Basta andare giù e poi girare una curva sola». Aveva ragione, e
**l'instradatore non aveva colpa**: la colonna sotto l'uscita della deviatrice era occupata
dal **gruppo di riempimento** — raccordo, gruppo e presa, tutti a x=307,5…317,5, cioè
esattamente sotto la porta. Spostato il gruppo di 20 mm, la linea **scende dritta: da 3
pieghe a 1**, e i rilievi della tavola passano da 42 a 38.

**Finché `passa-per` non esiste** (`DRAW-016` punto 3) una forma di spezzata non si chiede:
si libera il posto. Chi compone, prima di appendere un organo, guarda **quale autostrada deve
passare di lì**.

> **Quello che il piano non può raddrizzare, e va saputo.** Tre macchine in parallelo su due
> raccordi a T vogliono **due cambi di giacitura** sul collettore: sono nel grafo, non nel
> disegno, e ce li ha anche lo schizzo del PO del 3 settembre
> (`input-pm/riferimenti-grafici/2026-09-03/schizzo-informale-po.png`). «Poche curve» vuol
> dire **quelle e non altre**, non zero.

---

## A. Dove stanno i pezzi

### A1 — Tre macro fasce verticali

Da sinistra a destra: **generazione** · **accumuli e scambiatori** · **distribuzione**. Ogni
pezzo posabile sta nella fascia della propria categoria.

*Fonte:* PO, 20 settembre 2026 (**D-154**), che precisa **D-041** — quella nominava due poli,
generatori a sinistra e distribuzione a destra, e non diceva che cosa sta in mezzo.
*Controllo:* **`PIECE_OUTSIDE_ITS_BAND`** — `validation/regole.py::pezzi_fuori_fascia`. Ogni
fascia occupa l'intervallo in x dei propri pezzi; la violazione è un pezzo che ricade
nell'intervallo di un'altra fascia. **Chi non ha una fascia propria non viola niente**: un
raccordo è un punto sulla tubazione, e un **confine di rete** non sceglie dove stare — «va
accanto all'utente che serve» (I-061) — quindi nessuno dei due entra nel conto. *Tavola:*
`docs/collaudi/DRAW-015/tavole/tavola-4-*` prima della revisione, con il radiatore spostato
dentro la fascia dello scambiatore.

### A2 — Chi sta in parallelo si impila

Più generatori, più terminali, più pompe pari fra loro: **incolonnati**, non affiancati.
Chi non è un pezzo grosso — raccordi, organi, strumenti — **esce dalla fila** e si posa alla
fine, sulla campata fra i pezzi che la sua tratta unisce.

*Fonte:* **D-118**; la fascia dei generatori a sinistra è **D-041**.
*Controllo:* `tests/layout/test_zone_dei_pezzi_grossi.py` (posa); `da scrivere` come rilievo
sulla tavola.

> ⚠ **Correzione di citazione, 20 settembre.** Il codice attribuisce questa regola a
> **D-119** (`place.py`, `improve.py`, `test_zone_dei_pezzi_grossi.py`) e lo hanno fatto
> anche le note dei due piani e il README della prova. **D-119 è un'altra cosa** — l'area di
> rispetto dei raccordi. La regola è **D-041 + D-118**. Correggere le citazioni è dentro
> `DRAW-015`.

### A3 — L'ordine del processo si legge da sinistra a destra

*Fonte:* **D-060**, **D-041**.
*Controllo:* `da scrivere`.

### A4 — Un organo di servizio sta addosso al pezzo che serve

Valvole di intercettazione e sicurezza, scarichi, sfiati, manometri, vasi, gruppi di
riempimento, filtri, confini di rete: lo stacco che li porta è **il proprio minimo su
griglia**, e si allunga solo per un vincolo dichiarato. È **leggibilità**, non estetica: una
valvola lontana da tutto è equivoca.

*Fonte:* **D-145** (PO, I-076).
*Controllo:* **`SERVICE_STUB_LONGER_THAN_ITS_MINIMUM`** —
`validation/regole.py::organi_di_servizio_lontani`, che misura **sulla tavola finita** la
tratta che porta ogni organo di servizio e la confronta col proprio minimo. La posa del
motore ha ancora la sua prova (`tests/layout/test_vicinanza_valvole.py`), ma **non basta
più**: D-151 ha spostato la posa dal motore al piano, e il piano sovrascrive le coordinate.

> ⚠ **Il precedente, misurato il 20 settembre 2026.** Il confine di rete dell'ACS stava a
> **205,0**, **502,5** e **152,5 mm** dal pezzo che serve sugli impianti 2, 3 e 4 — cinquecento
> millimetri di tubo per arrivare a un prelievo che va messo lì accanto. Lo aveva scritto
> **chi ha composto i piani**, applicando **A1** a un pezzo che A1 non governa: un confine di
> rete **non ha una fascia**, perché non ha una posizione propria. È esattamente la classe di
> difetto che **D-158** nomina, ed è il motivo per cui il rilievo esiste.

---

## B. Come corrono le linee

### B1 — Prima le autostrade, e il più dritte possibile

La struttura si tira prima del corredo, e la sua **rettilineità** viene prima
dell'ottimizzazione degli stacchi. Il precedente che l'ha imposta: una tavola in cui curve e
attraversamenti erano ottimizzati **sugli stacchetti** mentre l'autostrada faceva «sta curva
senza senso».

*Fonte:* PO, 20 settembre 2026 (**D-154**); il precedente è del 19 (**D-151**).
*Controllo:* **`HIGHWAY_IS_NOT_STRAIGHT`** — `validation/regole.py::autostrade_storte`, che
conta le pieghe **della catena intera**: quelle dentro ogni tratta più i cambi di giacitura
**sui crocevia**, che nessuna tratta da sola vedeva. Il bilancio è `Highway.turns_allowed`
— zero sulla spina, **una** verso i terminali (D-144). La geometria adesso sa quali tratte
sono autostrada: `layout/autostrade.py`, e `RUN_WITH_TOO_MANY_BENDS` usa quel bilancio
invece del metro dello stacchetto. *Tavola:* impianto 1 composto, «la tratta `s3-a, s3-b`
piega 4 volte, e su un'autostrada le pieghe ammesse sono 1».

### B2 — Dal circolatore un tratto dritto, **una** curva, poi la dorsale a pettine

Dal circolatore esce un rettilineo e il ritorno rientra con un rettilineo: questo pezzo non
si piega. Poi è ammessa **una curva, e una sola**. Dopo la curva corrono mandata e ritorno
**affiancati e paralleli**, e i terminali si attaccano **a pettine** sul fianco, ciascuno col
proprio stacco corto, impilati.

*Fonte:* **D-144** (PO, I-075, con schizzo in
`docs/input-pm/riferimenti-grafici/2026-09-18/distribuzione-dorsale-a-pettine.png`).
*Controllo:* `da scrivere`. *Tavola:* impianto 5 composto, `docs/collaudi/PROVA-PIANO/`.

### B3 — Più generatori o più terminali ⇒ **collettore verticale**

Le macchine in parallelo si attaccano a una **catena di T verticale e allineata**, con uno
stacco corto ciascuna, invece di tirare ognuna la propria tratta verso la destinazione.

*Fonte:* PO, 20 settembre 2026 (**D-154**).
*Controllo:* **`PARALLEL_MACHINES_WITHOUT_A_COLLECTOR`** —
`validation/regole.py::macchine_in_parallelo_senza_collettore`. Camminando da ogni macchina
del gruppo si trova il proprio **nodo di collettore** (un raccordo con tre o più attacchi sul
percorso); la violazione è che i nodi non stiano sulla stessa verticale entro mezzo passo di
griglia, o che una tratta fra due nodi non corra in verticale.
⚠ **Non morde con due macchine in parallelo**: un nodo solo è allineato per costruzione, e la
regola comincia a dire qualcosa da tre in su. *Tavola:* impianto 5 composto — i due
collettori della cascata **passano**; la violazione si vede su una variante del piano 5 con
`cascata-ritorno-b` spostato di 40 mm.

### B4 — Un organo in linea non spezza il tratto

Una **valvola a tre vie** si posa con **ingresso e uscita allineati**; il terzo attacco esce
di lato. Vale per ogni organo che sta *sulla* linea: la linea passa, non si piega intorno a
lui.

*Fonte:* PO, 20 settembre 2026 (**D-154**).
*Controllo:* **`INLINE_ORGAN_BREAKS_THE_RUN`** —
`validation/regole.py::organi_che_spezzano_il_tratto`. Soggetto: un pezzo che **non è un
raccordo** e ha due porte su **facce opposte** del manifesto ruotato, tutt'e due in uso. La
violazione è che il tratto che esce da una e quello che esce dall'altra **non abbiano la
stessa giacitura**: stesso asse, stessa quota. *Tavola:* impianto 5 composto, il `ricircolo`
— «ha `a` e `b` su facce opposte alla stessa quota x=677,5, ma il tratto di `a` corre
orizzontale e quello di `b` verticale: l'organo sta sulla piega».

### B5 — Una tratta con più accessori in linea vuole il proprio rettilineo

Gli accessori in catena stanno a distanze fisse dalla porta (I-044): se la tratta non ha il
rettilineo che chiedono, non ci stanno. Sull'impianto 5 le tratte verso i terminali ne
portano tre — due intercettazioni e un circolatore — e vogliono **40 mm** liberi.

*Fonte:* **nata componendo**, 20 settembre 2026. *Tavola:* impianto 5 composto.
*Controllo:* c'è già, ed è il motore che lo dice bene: «questa tratta è lunga 10 mm ma i suoi
accessori ne chiedono 15».

### B6 — Due linee fra gli stessi due raccordi si separano in quota

Mandata e ricircolo che uniscono la stessa coppia di raccordi non possono stare alla stessa
altezza: si leggono come una sola linea.

*Fonte:* **nata componendo**, 20 settembre 2026. *Tavola:* impianto 5 composto.
*Controllo:* `PARALLEL_RUNS_TOO_CLOSE`, `RUNS_OVERLAP_LENGTHWISE`.

### B7 — Due porte che guardano dalla stessa parte non si uniscono con un segmento

Se la catena entra in una macchina da una porta e ne esce da una porta sulla **stessa faccia**
— o su una faccia **perpendicolare** — allora quella catena **non può essere una retta**, e
non è la posa a sbagliare: è la forma dei due simboli. Il piano non ci può fare niente, e il
rilievo che ne esce è vero ma non azionabile da chi compone.

*Fonte:* **nata componendo**, 20 settembre 2026, scrivendo i piani degli impianti 2, 3 e 4.
*Tavole:* tutte e tre, e si conta sui casi:

| catena | curve ammesse | perché non si chiude |
|---|---|---|
| impianto 2, `bollitore -> deviatrice` | 0 | `out_b` della tre vie è sulla faccia **inferiore**, `coil_in` del bollitore sulla **sinistra**: due facce perpendicolari |
| impianto 2, `volano -> ritorno -> bollitore` | 0 | `primary_out` e `coil_out` sono tutt'e due sulla faccia **sinistra**, e devono arrivare allo stesso raccordo da parti opposte |
| impianto 3, `volano -> … -> pdc` | 0 | `volano.b` e `pdc.water_return` guardano tutt'e due a **destra**: serve uscire, salire e tornare indietro — e quella è la **U** che `RUN_OVERSHOOTS_ITS_PORT` blocca |
| impianto 4, `scambiatore -> commutatrice` e `scambiatore -> deviatrice` | 0 | lo scambiatore a piastre ha `primary_in` e `primary_out` tutt'e due a **sinistra**, e non ruota |

*Controllo:* `da scrivere` — e va scritto **dove si assegnano le curve ammesse**, non fra i
rilievi: `Highway.turns_allowed` oggi vale zero per ogni catena fra macchine di spina, senza
guardare se le facce delle sue porte lo permettono. Finché non lo guarda, B1 accusa tavole
che nessun piano può raddrizzare, e un rilievo che non si può chiudere è rumore.

**Due letture, e la scelta è del PO.** O il catalogo cambia (una macchina con due attacchi
sullo stesso lato è un simbolo, non un vincolo idraulico), o `turns_allowed` diventa **il
minimo raggiungibile** date le facce. La prima è materia MEP, la seconda è codice.

### B8 — Una linea non lascia la propria quota per poi tornarci

Un **sali-scendi** è una linea che esce dalla riga su cui corre, percorre un tratto su
un'altra, e **ci torna**. Non è una piega: è un'**escursione**, e dice che due cose si
contendono la stessa quota. **Si toglie spostando l'oggetto, non piegando il tubo** — è la
stessa disposizione di B12 (D-078).

*Fonte:* **D-065**, 4 agosto 2026. I sali-scendi sono uno dei **quattro** difetti che il cold
eye review trovò a occhio; gli altri tre sono diventati regole misurate (D-059, D-062),
**questo no** — è rimasto soltanto un peso dell'instradatore (`route.TURN_COST`). Riaperto
dal **PO il 20 settembre 2026**, a penna rossa su due tavole.
*Controllo:* **`RUN_LEAVES_ITS_QUOTA_AND_COMES_BACK`** —
`validation/regole.py::scostamenti_che_tornano_indietro`. **Non ha soglie**: o la linea ci
torna, o non ci torna.
*Tavola:* impianto 1, il ritorno del radiatore (esce di 12,5 mm per 92,5 mm); impianto 4, il
ritorno della caldaia (7,5 mm per 80).

> ⚠ **Perché un peso non bastava**, e vale per ogni regola di questo foglio: un peso dice
> all'instradatore che cosa preferire **mentre cerca**; non dice a nessuno che cosa è
> **uscito**. Dal **D-151** la posa la decide il piano, e un piano che mette due tratte sulla
> stessa quota costringe l'instradatore a scansarne una. È **D-158** applicato alla tratta
> invece che al pezzo.

### B9 — Due tubazioni che si affiancano si tengono tre corsie libere

Due tubi a un passo di griglia **si leggono come un tubo solo**. Chi corre affiancato a un
altro si tiene **10 mm**, che sono quattro passi, cioè tre corsie libere.

*Fonte:* la nostra, **D-062** via `place.ROW_GAP_MM` — «due pezzi affiancati lasciano 10 mm
perché due tratte devono poterci passare senza sovrapporsi». La stessa misura vale fra due
**linee**, e per la stessa ragione.
*Corroborazione pubblicata, arrivata per un'altra strada:* KLM Technology Group, *Project
Engineering Standard — Piping and Instrumentation Diagrams*, Rev. 01, 2011, §5 *Line
spacing*: «a spacing of **10 mm and more** is desirable between flow lines». **Due
derivazioni indipendenti sullo stesso numero.**
*Controllo:* **`PARALLEL_RUNS_WITHOUT_A_FREE_LANE`** —
`validation/regole.py::linee_parallele_senza_corsie`.
*Tavola:* impianto 5, **quattordici** coppie; impianto 3, due. Sulle altre tre: **nessuna**,
perché lì tutti gli affiancamenti stanno già a 10 mm.

> **Non è `PARALLEL_RUNS_TOO_CLOSE` del preflight**, che misura se due linee si **toccano** —
> un fatto geometrico, bloccante. Questa misura se si **leggono**, ed è una regola del piano:
> si cura componendo.

> **Quando due tratti si affiancano davvero.** Il rilievo si accende solo se il fianco a
> fianco è **almeno lungo quanto la distanza che li separa**: due linee a 7,5 mm che si
> accostano per 2,5 sono uno **spigolo**, non un corridoio. È una **lettura dichiarata**, non
> una soglia tarata, e serve a non accusare ogni angolo.

### B10 — Mandata sopra, ritorno sotto. Sulle orizzontali, sempre.

*Fonte:* la nostra, e scritta da prima: `layout/composition.py` — «le tubazioni corrono su
corsie orizzontali a quote fisse, con la **mandata sopra il ritorno**» — ricavata misurando
una tavola di riferimento del PO. **Riscontro sul corpus** di
`docs/input-pm/riferimenti-grafici/`: costante su tutte le tavole, comprese le due di mano
del PO.
*Controllo:* **`RETURN_RUNS_ABOVE_ITS_SUPPLY`** —
`validation/regole.py::ritorni_sopra_la_mandata`.
*Tavola:* misurato sulle cinque consegnate — **49 coppie giuste, 7 sbagliate**, su quattro
tavole su cinque.

> **Perché adesso si può pretendere, e prima no.** La prova che difendeva questa convenzione
> — `tests/layout/test_composition.py` — dichiara che «sulla corsia la convenzione **non si
> può pretendere**… imporlo costerebbe pieghe». Era vero quando la posa la decideva
> **l'instradatore**. Dal **D-151** la posa la decide il **piano**, e mettere i pezzi sulle
> quote giuste **non costa nessuna piega**: la cura è di chi compone. È lo stesso passaggio
> di D-158, e vale per ogni convenzione che oggi vive come preferenza del router.

⚠ **Solo le orizzontali, e non è una dimenticanza.** Sulle **verticali** le tavole del PO non
hanno una costante: la colonna di mandata sta a sinistra del ritorno in una e a destra in
un'altra. **Una regola sul lato dei verticali non esiste, e non si inventa.**

### B11 — Mandata e ritorno corrono insieme, a interasse costante

*Fonte:* il **PO**, 20 settembre 2026: «devi ricordare di disegnarle mandata e ritorno
insieme… **corrono sempre insieme, non esiste che una va e l'altra va zig zag accanto**».
*Riscontro:* su `schema-tipologico.pdf` le due corsie tengono un interasse costante per
tutta la corsa e cominciano e finiscono alla stessa ascissa.
*Controllo:* **`SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER`** —
`validation/regole.py::coppie_che_non_corrono_insieme`. Si prendono **le due autostrade che
uniscono le stesse due macchine**, una di andata e una di ritorno, e si campiona il tratto
orizzontale **in comune** passo per passo.
*Tavola:* impianto 4, `caldaia ~ disgiuntore` — **170 mm in comune e sei interassi diversi**,
da −110 a +155: la coppia si apre e si scambia di lato. Impianto 1, `accumulo ~ radiatori`,
due interassi (10 e 15).

**Non si pretende un valore, si pretende che non cambi.** Quanto vale l'interasse lo
decidono le porte delle macchine, non questa regola.

⚠ **Quando il piano non ce la può fare.** Se le porte delle due macchine agli estremi
vogliono interassi diversi, **nessuna posa può tenere l'interasse costante**: il cambio è
**del catalogo**, non di chi compone.

**Un caso è stato chiuso così, ed è il modello.** `gas-boiler` aveva mandata e ritorno a
**10 mm** contro i **15** di tutte le altre macchine, e per questo la coppia
`caldaia ~ disgiuntore` dell'impianto 4 non poteva stare insieme. Il PO, il 20 settembre
2026 (**I-091**): «gli attacchi sulle macchine si devono poter spostare, sono simboli… si
sposta **lungo la faccia su cui sta**, serve solo per allineare meglio le autostrade».
`water_supply` è scesa da y=10 a y=5 sulla stessa faccia destra, e la coppia adesso
**corre insieme**. La libreria dei simboli non si tocca **di faccia** (D-126 punto 3): si
scorre lungo la faccia, e solo per le autostrade.

⛔ **E c'è un limite, dato dal PO nella stessa conversazione, che vale più della licenza:
gli attacchi di un serpentino non si spostano.** «I puffer hanno delle particolarità:
serpentino che va rispettato, altrimenti non si capisce a che serve quel serpentino senza
attacchi precisi su esso.» Sono `coil_in` e `coil_out` di `dhw-cylinder` — **10 mm l'uno
dall'altro, e restano lì**: la loro posizione dice dov'è la serpentina dentro l'accumulo, e
spostarli toglie senso al simbolo. **La conseguenza va accettata**: una coppia che serve una
serpentina **cambia interasse**, e il rilievo di B11 su quella coppia è vero e non si cura.
Chi scorre un attacco guarda prima se quell'attacco appartiene a uno scambiatore interno.

**Un caso resta aperto, e non si chiude così.** `radiator` ha `in` e `out` **alla stessa
quota** su facce opposte: la coppia che lo serve **deve** cambiare interasse, e farli
distare 15 mm su un simbolo alto 15 non è uno scorrimento ma un ridisegno. È la stessa
famiglia di **B7**, ed è una domanda al PO.

---

## C. Come si prende un pezzo

### C1 — Un pezzo si prende dal lato delle sue porte

La miscelatrice del radiante ha `hot_in` a sinistra, `out` a destra e `cold_in` sotto: presa
dall'alto non si instrada niente. Il piano deve avvicinarsi dal lato giusto.

*Fonte:* **nata componendo**, 20 settembre 2026. *Tavola:* impianto 5 composto.
*Controllo:* l'errore lo dà l'instradamento; `da scrivere` come rilievo che lo nomina prima.

### C2 — La rotazione si deduce, tranne dove c'è una scelta

Si deduce per un **raccordo** e per un pezzo con **un attacco solo**. Una **macchina con due
o più attacchi ha una scelta**, e quella scelta è del pianificatore.

*Fonte:* **D-004**, **I-027**; la forma stretta è del 20 settembre 2026.
*Controllo:* `piano/esecutore.py::orienta` — portato in `src/` da `DRAW-015`, come questa riga chiedeva.

### C3 — La mappa degli attacchi si rifà **solo per i raccordi**

Rifarla su una macchina è un **errore di contenuto**: il 20 settembre ha mandato l'acqua
fredda sull'uscita primaria dell'accumulo. Il grafo era giusto e il disegno era sbagliato.

*Fonte:* **D-004**, **I-027**; il precedente è del 20 settembre, e l'ha visto il PO a occhio,
non una misura.
*Controllo:* `da scrivere` — un confronto fra il grafo e ciò che la tavola mostra collegato.
È il controllo più importante dell'elenco, perché è l'unico difetto di **contenuto** nato da
una scelta **grafica**.

---

## D. Il foglio

### D1 — Il disegno non arriva al bordo

Margine di rispetto ampio sui disegni scarichi — 25 mm — che si stringe fino a 10 solo se il
disegno è davvero pieno.

*Fonte:* **D-143** (PO, I-074).
*Controllo:* `DRAWING_TOUCHES_THE_BORDER`.

### D2 — Il riempimento del foglio **non è un obiettivo**

Si riporta come misura, come la lunghezza (D-139). Il formato si sceglie sulla scala
ordinaria A4 → A3 → A2 → A1 (D-148, dichiarata momentanea dal PO).

*Fonte:* **D-149**, **D-148** (PO, I-079, I-080).
*Controllo:* `SHEET_BARELY_FILLED`, `SHEET_TOO_FULL` — **misure**, non difetti da chiudere.

### D3 — Il disegno non sta tutto da una parte

*Fonte:* **D-060**; il difetto è misurato sulle due tavole composte del 20 settembre — 5,2
volte l'inchiostro fra quadrante pieno e vuoto sull'impianto 1, **9,0** sul 5.
*Controllo:* `DRAWING_ALL_ON_ONE_SIDE`, limite **3,0**. **È il primo difetto aperto del
pianificatore.**

**La soglia è tarata dalle tavole del disegnatore del PO, e regge.** Misurato il 20 settembre
2026 rieseguendo la stessa formula — inchiostro per quadrante, rapporto pieno/vuoto — sui
quattro PDF di `docs/input-pm/riferimenti-grafici/2026-09-03/`:

| tavola del PO | sul foglio | sul riquadro del disegno |
|---|---|---|
| `schema-tipologico.pdf` | **1,4×** | 1,4× |
| `schema-idraulico-sdp.pdf` | **1,6×** | 1,6× |
| `schema-tipologico-pdc-volume-integrato.pdf` | **2,5×** | 2,8× |
| `schema-tipologico-3-vie.pdf` | *un quadrante senza inchiostro* | 9,9× |

**Tre su quattro stanno fra 1,4 e 2,5 contro un limite di 3,0**: il numero non è inventato, è
dove stanno le tavole buone. La quarta è l'eccezione, e **guardandola si capisce perché**: è
un'**A4 verticale con il disegno nella metà alta e la metà bassa bianca**, senza cornice né
cartiglio — l'esportazione di una regione, non un foglio finito. Misurarci D3 è misurare il
bianco del ritaglio.

⚠ **«Il disegno è una fascia» non è di per sé il difetto.** Anche le tavole del PO sono
fasce: `schema-tipologico.pdf` ha 3,7 e 3,0 mm di margine a sinistra e a destra contro 65 e
67 sopra e sotto. La differenza è **dove sta la fascia**: la sua attraversa il foglio per
intero ed è centrata, quindi tutti e quattro i quadranti portano inchiostro; la nostra sta in
alto e non arriva a destra. **Quello che D3 accusa non è la forma a nastro: è il nastro messo
storto sul foglio.**

---

## Quello che manca, e si sa che manca

- ~~**Nessun controllo sa che cos'è un'autostrada.**~~ **Chiuso il 20 settembre 2026**
  (`DRAW-015`): `layout/autostrade.py` porta l'autostrada fino alla tavola instradata, B1 ha
  il proprio rilievo, e `RUN_WITH_TOO_MANY_BENDS` usa il bilancio della catena invece del
  metro dello stacchetto. Era il difetto che ha generato D-151.
- ~~**A4 non ha un rilievo sulla tavola finita.**~~ **Chiuso il 20 settembre 2026**
  (`DRAW-015`): il vincolo era del motore, D-151 lo ha lasciato senza guardia, e adesso
  `SERVICE_STUB_LONGER_THAN_ITS_MINIMUM` lo misura dove conta, cioè sull'elaborato.
- **Cinque regole non hanno ancora un rilievo sulla tavola finita** — **A2**, **A3**, **B2**,
  **C1**, **C3** — ed è la stessa classe di difetto che D-158 nomina. Due si distinguono:
  **A3** oggi **non è tenuta su da niente** (l'unico posto che la faceva valere era il
  solutore, che è morto con D-151; `hierarchy.py` cita D-060 per l'impilamento di A2, non per
  l'ordine di processo), e **C3** è la peggiore, perché è l'unico difetto di **contenuto**
  che nasce da una scelta **grafica**. Le apre `DRAW-016`.
- **B1 e B3 si contraddicono sulla cascata, e la contraddizione è aperta.** Sull'impianto 5 la
  catena che attraversa il **collettore verticale che B3 pretende** fa due pieghe, e B1 —
  `turns_allowed` zero — la accusa. **Qui la tavola è giusta e il numero dice che è
  sbagliata**, ed è il rilievo che questo progetto chiede di portare per primo. Il PO ha detto
  «prima le autostrade dritte **il più possibile**», non «dritte». Come si scrive quel «il più
  possibile» è una domanda al PO, e sta accanto a B7.
- **La composizione a corsie** della ricerca del 4 agosto §2.2 — le dorsali di mandata e
  ritorno con i componenti appesi — è misurata su due tavole vere e **non è ancora una riga
  qui**, perché non è stata ancora composta da noi. Quando lo sarà, entra con la sua tavola.
- **Quante autostrade verticali sono ammesse fra due colonne? — domanda del PO, 20 settembre
  2026.** Lui l'ha posta dubitandone: «in genere fra due colonne è consentita **una sola**
  autostrada verticale se ho poi macchine/accumuli… ma forse non è una buona regola».
  **Misurato sulle nostre cinque tavole**, contando le colonne verticali di autostrada lunghe
  almeno 20 mm:

  | impianto | colonne verticali | giudizio del PO sulla tavola |
  |---|---|---|
  | 1 | **2** | «va quasi bene» |
  | 2 | **2** | «va quasi bene» |
  | 3 | **3** | «va quasi bene» |
  | 4 | **6** | «non hai minimamente risolto» |
  | 5 | **12** | «non hai minimamente risolto» |

  **È l'unico numero che separa le tavole che il PO approva da quelle che boccia**, e le
  separa nettamente. Non è codificata come regola perché **il PO stesso ne dubita** e perché
  «una sola» non regge sulle sue tavole di riferimento — ma il numero discrimina, e la
  domanda va riportata con questa tabella in mano.
- **Il PO ha detto che l'elenco è aperto**: «le regole sono sempre le stesse, vanno solo
  aggiunte altre e migliorate» (I-085, aperta).
