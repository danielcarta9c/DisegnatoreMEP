# REL-009 — la 1.3: il rapporto

Una sezione per ogni gruppo di punti, la più recente in alto. Il caso è il primo impianto reale (I-191),
ricostruito anonimo in `caso-reale-1/`: il documento della sessione di disegno porta i dati del cliente e non è
nel repository.

## 8. Lo sfiato con il suo rubinetto (I-210, I-211)

**5 ottobre 2026** · input **I-210**, **I-211** · decisione **D-210** (proposta) · la tavola al PO

Il PO, con uno schizzo: lo sfiato e il suo rubinetto in un simbolo solo, «cosi' riusciamo a disegnarlo piccolo e il
disegno si compatta e abbiamo meno sormonti e meno lunghezze»; e poi «sostituiamo il simbolo ovunque».

### Le tavole, per prime

- **Il caso reale** (`caso-reale-2/tavola/`): sulle pompe di calore 2–4 lo sfiato col rubinetto pende due passi sopra il
  ritorno, oltre la colonna di mandata, e non incrocia niente; sulla prima, la cui mandata è l'autostrada, la scavalca
  con 15 mm di stacco invece di 35. Sui due volani sta addosso al cielo.
- **La tavola D della prova del PO**: lo sfiato sul cielo del volano coricato, e la mandata gli passa sopra.
- Le altre tavole agli atti cambiano solo nel simbolo dello sfiato.

### Le misure

| | prima (1.4.0) | dopo |
|---|---:|---:|
| caso reale: pieghe · sormonti | 13 · 14 | 13 · 14 |
| caso reale: tubo degli stacchi degli sfiati | 175 mm | **70 mm** |
| caso reale: pezzi sulla tavola | 216 | **208** — otto valvole in meno |
| le 14 tavole agli atti: pieghe e sormonti | — | gli stessi, tavola per tavola |

Sulla prova pulita A (§7), composta per lo sfiato di prima, 8 dei 20 sormonti e i 6 stacchi più lunghi del minimo
erano degli sfiati: è il guadagno che resta a chi compone il piano con le istruzioni nuove.

### Il vincolo, e perché il simbolo è alto 7,5

Il motore vuole fra un raccordo e il pezzo che ne pende **due passi**, 5 mm (D-113), e il raccordo sporge di 2,5 sulla
linea. Sulla pompa di calore mandata e ritorno sono a 15 mm: dal ritorno alla mandata restano 7,5 mm, e lì lo sfiato
non ci sta, né alto 10 né alto 7,5. Sul volano coricato sul ritorno (D-196), dove lo sfiato sta addosso al cielo senza
stacco, alto 10 toccherebbe la mandata e alto 7,5 ne resta a 2,5: per questo 7,5. Il rubinetto è grande quanto il segno
della valvola in linea.

### Che cosa è cambiato, oltre al simbolo

- **Il catalogo**: `air-vent` e `air-vent-solar` si disegnano col simbolo nuovo; `air-vent-plain` è la variante senza
  rubinetto. Le regole non propongono mai una variante: il catalogo lo dice in `providing`.
- **La validazione** ferma una valvola d'intercettazione sullo stacco di uno sfiato col rubinetto
  (`AIR_VENT_ISOLATED_TWICE`): un grafo scritto prima la dichiarava, e disegnerebbe due rubinetti.
- **I piani agli atti** posavano lo sfiato alto 5: quelli che lo mettevano addosso a un volano (la tavola D, la tavola dei
  simboli nuovi) lo alzano di 2,5, e la porta resta dov'era; `tavole_di_prova.py` sposta gli sfiati della differenza fra
  10 — l'altezza con cui quei piani furono scritti — e quella di oggi.
- **Capire e Comporre**: lo sfiato si scrive senza valvola; si pende a due passi dal raccordo, oltre la colonna di
  mandata.

### Una cosa vista

- ⚠ **Sul caso, togliendo la valvola dallo sfiato del volano dell'ACS, le valvole sugli attacchi predisposti hanno cambiato
  nome**: prima le metteva la regola del volano, col nome del volano; ora la regola del confine, col nome del confine.
  `completa` l'ha detto — «accessori tolti che non tolgono niente» — e l'elenco dei tolti si è corretto con i nomi nuovi.
  È il meccanismo di D-201 che funziona; ma lo stesso pezzo sullo stesso attacco ha preso un altro nome per un cambiamento
  altrove nel grafo.

### Le prove

`tests/graphics/test_sfiato_con_rubinetto.py` (il simbolo, la regola che non propone la variante, lo sfiato sotto la
mandata sulla tavola D) e `tests/rules/test_accessori_dichiarati.py` (la valvola doppia): **rosse su `main`, verdi
adesso**. Suite: 2042 passate, 15 saltate, 10 attese rosse.

## 7. La 1.4.0 in una sessione pulita (I-208)

**3 ottobre 2026, sera** · input **I-208**, **I-209**

Il PO ha usato la 1.4.0 **nella stessa chat in cui aveva lavorato con la 1.3.0**, e la tavola è uscita «sporca»,
molto peggio di quella del §5. Ha chiesto perché, e una prova della 1.4 in una sessione pulita. La sua tavola porta i
dati del cliente e non è nel repository.

### Le tavole, per prime

`prova-pulita-1.4/tavola-A/` e `tavola-B/`: due sessioni nuove e indipendenti, ciascuna con il solo ZIP della 1.4.0 e
il grafo anonimo del caso (`caso-reale-2/grafo-prima-stesura.json`), senza codice, piano e istruzioni di sviluppo.
Partono dal grafo approvato e seguono la skill: Comporre, `disegna`, Rivedere. I piani sono `piano-A.json` e
`piano-B.json`; le tavole qui sono rifatte con lo ZIP da quei piani, e i numeri coincidono con quelli che le due sessioni
hanno riportato.

| | minuti | `disegna` lanciati | il più lento | pieghe | sormonti | bloccanti |
|---|---:|---:|---:|---:|---:|---:|
| A | 8 | 13 | 3,3 s | 15 | 20 | 0 |
| B | 11 | 7 | 3,1 s | 18 | 14 | 0 |
| il piano del §5, scritto dallo sviluppo | — | — | — | 13 | 14 | 0 |

Tutte e due tengono la distribuzione a colonne affiancate, le pompe di zona sullo stesso verso e i terminali sotto la
coppia del collettore. Il difetto che resta in B l'ha detto la sessione stessa: la linea della pompa della zona vicina
corre fra la mandata e il ritorno della dorsale (avviso B9).

### Perché la tavola della chat del PO è peggiore

- **Il piano è quello della 1.3.0.** La tavola del PO fatta con la 1.4 ha la stessa disposizione di quella fatta con la
  1.3.0 nella stessa chat: macchine, volani e zone negli stessi posti. Cambia quello che decide il motore — le pompe in
  parallelo, il collettore, i colori — e non quello che decide il piano — la distribuzione, i terminali sotto la
  coppia (I-205). La chat ha ridisegnato il piano che aveva, invece di ricomporlo con le istruzioni nuove.
- **La tavola del §5 non è della skill.** Il suo piano l'ha scritto lo sviluppo con `componi_piano.py`, sapendo che cosa
  correggere. Il metro della skill è la sessione pulita: A e B ci arrivano vicino da sole.

### Che cosa delle istruzioni di Comporre le due sessioni hanno trovato difficile

- la giacitura dei pezzi è scritta caso per caso (miscelatrice, gruppo di riempimento, raccordi del pettine): manca una
  regola sola su quale faccia guarda il vicino; e non è detto se il primo raccordo girato a mano valga anche per una
  colonna in cui la mandata arriva di lato (A);
- B3 chiede l'ordine dei collettori con meno sormonti, ma l'altro ordine dava meno pieghe e nessuna corsa senza corsia:
  A ha scelto contro la lettera di B3 (A);
- l'ordine e l'ingombro degli organi in linea, e le porte di raccordi e appesi, si sono trovati per tentativi (A, B);
- la forma della zona vicina «sotto il ritorno» il piano non la impone, e le istruzioni non dicono che cosa fare quando
  il motore porta la pompa fra mandata e ritorno (B);
- che lo sfiato di una pompa di calore vada oltre la colonna di mandata, perché incrociarla piega la mandata della
  macchina sotto, non è scritto (B);
- l'ingombro della tabella delle apparecchiature nella scelta del formato non è detto (B).

Restano da decidere: sono il lavoro possibile su Comporre.

## 6. La 1.4.0 sulle tavole agli atti, e il tempo (punto 7)

**3 ottobre 2026** · input **I-206**, **I-207** · decisione **D-209**, approvata (I-207: «Si fondi»)

Il PO: «Crea la nuova skill V 1.4 e testala sulle vecchie tavole sia come risultato che come velocità e cerca di
capire se ci sono problemi sia su uno che sull'altro e in caso perché». Le misure sono in
`la-1.4-sulle-tavole-agli-atti/`: `banco.py` disegna ogni tavola in un processo nuovo, col suo grafo e il suo
piano, e scrive `esiti-*.json`.

### Le tavole, per prime

Fra la 1.3.0 e la 1.4.0, su quattordici tavole agli atti, ne cambiano tre, e per le ragioni che il PO ha approvato:

| tavola | che cosa cambia | perché |
|---|---|---|
| `REL-003/impianto-6`, piano A | la valvola del circolatore dei fancoil passa dalla discesa all'orizzontale, accanto alla sua pompa (`impianto-6a-1.3.0-e-1.4.0.png`); stessi numeri, 10 pieghe e 3 sormonti | le pompe in parallelo con lo stesso verso (D-208) |
| la tavola di prova 6 | la stessa cosa | D-208, già nella PR #74 |
| `simboli-nuovi` | il collettore con ritorno | 40 × 15, a coppie di 10 (D-207) |

Le altre undici — i cinque impianti di `DRAW-018`, l'impianto 6 col piano B, l'impianto 7, le quattro della prova
del PO — sono **identiche byte per byte**. La correzione del tempo non cambia niente: le quattordici tavole della
1.4.0 sono quelle di `main` prima della correzione, e dallo ZIP pubblicato escono le stesse; la regressione di
progetto è identica, 54 file su 54.

### Il tempo

`disegna`, in secondi, nel processo:

| tavola | 1.3.0 | 1.4 prima della correzione | **1.4.0** |
|---|---:|---:|---:|
| `DRAW-018`, impianti 1 … 4 | 0,8 – 1,2 | 1,0 – 4,2 | **0,4 – 0,6** |
| `DRAW-018`, impianto 5 | 4,4 | 5,3 | **1,1** |
| impianto 6, piani A e B | 5,9 – 6,0 | 7,0 – 7,3 | **0,9 – 1,7** |
| impianto 7 | 4,9 | 4,2 | **0,7** |
| prova del PO, A … D | 1,2 – 1,3 | 1,2 – 1,4 | **0,5 – 0,6** |
| simboli nuovi | 0,8 | 0,7 | **0,6** |
| **il caso reale** (137 tratte, A1) | si ferma in 0,2: la posa d'inventario non entra nell'A1 | **106,8** | **3,4** |
| le sette tavole di prova, insieme | 14,3 | 14,5 | **3,3** |

Con lo ZIP della 1.4.0, ogni comando in un processo nuovo come su claude.ai, sul caso: `valida` 0,5 s, `completa`
0,9, `pezzi` 0,6, **`disegna` 4,4** (con PDF e DXF), `anteprima` 0,9. Le altre tredici tavole: `disegna` fra 1,1 e
1,5 s.

### Perché la 1.4 era lenta, e perché lo erano già le tavole piccole

Il profilo del caso, prima della correzione: 271 s, e **269 nella posa d'inventario** (`place_sheet`), che
dell'esecuzione del piano dà solo simboli, rotazioni e porte — le coordinate le sovrascrive il piano. Dentro, a ogni
posto che prova per un pezzo, la posa rifà i corridoi davanti a tutti gli attacchi già posati (I-044), e per ogni
attacco cercava la sua tratta **rileggendole tutte**, confrontando gli attacchi come modelli: 460 mila domande, **74
milioni di confronti**, 200 s. Il routing vero, `settle_sheet`, sta sotto il secondo.

- **Il caso a 107 s l'ha introdotto la PR #74.** Con il collettore largo 40 la posa d'inventario non entrava più
  nell'A1, e la si rifà su un foglio di 4 × 3 m (I-205): lì i posti da provare sono molti di più. La 1.3.0, sullo
  stesso grafo, si fermava subito con un errore.
- **Sulle tavole piccole lo stesso conto valeva tre quarti del tempo** (14,3 s contro 3,3 sulle sette tavole di
  prova).

La correzione (D-209): un indice degli attacchi delle tratte, letto una volta, e la catena di ogni attacco contata
una volta per posa. La risposta è la stessa. `tests/layout/test_il_tempo_della_posa_d_inventario.py` conta le catene
che la posa chiede sul caso: **453 045 su `main`, rossa; al più due per attacco adesso, verde in 3,4 s.**

### Quello che non so, e correggo

- ⚠ **Al §5 avevo scritto che i 30 minuti erano probabilmente nei 107 s di un disegna.** Non regge: quei 107 s sono
  della 1.4 prima della correzione, e la sessione del PO girava con la 1.3.0, che sul caso ricostruito non arriva
  nemmeno a disegnare. Con la 1.3.0 un `disegna` sulle tavole agli atti costa da 1 a 7 secondi, e i 30 minuti non
  stanno nel motore. **Dove vadano non lo posso misurare da qui**: la sessione del PO non è nel repository. Il
  sospetto è il lavoro del modello — scrivere un grafo e un piano di 150 pezzi, rileggere le istruzioni, guardare le
  anteprime, ritentare dopo un errore come quello dell'inventario —, e per saperlo serve il registro di una sessione
  vera.
- ⚠ **Due esiti non nulli nella regressione di progetto, uguali dalla 1.2.0:** i cinque piani di `PROVA-PIANO`
  nominano pezzi che D-182 ha rinominato, e la via senza piano (`draw`), che la skill non usa, ferma gli impianti
  3, 4 e 5 con un rilievo bloccante (`RUN_OVERSHOOTS_ITS_PORT`). `confronta.sh` li confronta byte per byte,
  errori compresi.

## 5. Quello che il caso ha riportato (I-201 … I-205)

**3 ottobre 2026** · decisioni **D-206**, **D-207**, **D-208** (proposte) · la tavola al PO

Il PO ha rifatto la tavola del caso con la 1.3.0 nella sua sessione di lavoro e ne ha riportato i difetti. La sua
tavola porta i dati del cliente e non è nel repository; il grafo è ricostruito anonimo da quello che vi è disegnato,
in `caso-reale-2/` (`costruisci_grafo.py`), e il piano lo compone `componi_piano.py` come Comporre deve adesso.

### La tavola, per prima

`caso-reale-2/tavola/` — la tavola del caso rifatta:

```
Formato A1 · tratte 137 · tratte cedute 0 · rilievi bloccanti 0 · pieghe 13 · sormonti 14
```

Ci sono **le valvole di sicurezza delle sei pompe di calore**, che sulla tavola del PO mancano: D-202 dice che si
disegnano sempre.

### Che cosa non andava, e perché

- **L'autostrada scavalcava la valvola dello sfiato** (I-201, I-203). Il motore instradava nell'ordine dei nomi
  delle tubazioni: lo stacco dello sfiato, passato prima della mandata, ci aveva posato la sua valvola sopra. Con la
  1.3 gli stacchi dichiarati li scrive Capire, con nomi suoi; prima erano delle regole, `stub-…`. Ora si instradano
  le autostrade, poi la distribuzione, poi gli stacchi (D-206): la valvola va oltre l'incrocio.
- **Le pompe di zona una orizzontale e una verticale** (I-204). Il motore posa la fila di una pompa sul primo
  rettilineo che la contiene, e una delle due tratte partiva in verticale. Ora la fila di una pompa in parallelo va
  sul primo orizzontale, e il controllo A2 lo misura (D-208).
- **I colori sbagliati nella distribuzione** (I-202). Due difetti, trovati sul caso ricostruito: la camminata del
  colore attraversava il collettore con ritorno dall'ingresso all'uscita del ritorno — la colonna di ritorno usciva
  rossa —, e sul circuito di carico il bollitore era preso per sorgente — la mandata della pompa di carico usciva blu.
  Il catalogo dichiara ora i passaggi interni del collettore, e chi scambia sulla serpentina non è una sorgente.
- **Nessuna autostrada nella distribuzione** (I-205). Le dorsali erano già autostrade per il motore; mancava il
  piano. La coppia del secondario resta sulle quote del volano fino alla zona lontana, e ogni zona ha le sue due
  colonne affiancate (Comporre, «La distribuzione di una centrale grande»).
- **Il collettore con ritorno pagava quattro pieghe per terminale** (I-205): coppie a 5 mm, mandate e ritorni
  alternati, contro i terminali a 10. Ora è 40 × 15, a coppie di 10, e il terminale sotto la coppia si raccorda dritto.

### Le tavole di regressione

```
$ confronta.sh <main> <ramo>
file: 54 prima, 54 dopo
<   ./tp/tavola-6.dxf, ./tp/tavola-6.svg
```

Cambia la sola tavola di prova 6, che ha due pompe in parallelo: la valvola della seconda passa dalla discesa
all'orizzontale, accanto alla sua pompa, come la prima. Le altre sono identiche byte per byte.

### Due cose che la sessione ha visto

- ⚠ **I cinque impianti di prova sulla via del piano non producono tavola già su `main`**: i loro piani nominano
  pezzi rinominati da D-182. La regressione copre le tavole di prova, la via senza piano e la tavola D.
- ⚠ **Il controllo B1 conta 2 pieghe di troppo sul ritorno della zona lontana**, che sono la discesa in colonna e
  l'ultimo collettore preso a gomito: la stessa geometria della mandata, che il controllo accetta. È il raccordo
  girato e specchiato che il pavimento del controllo non legge; la tavola mi sembra giusta.
- **Il tempo** (punto 7): disegnare il caso una volta richiede 107 secondi. Con i giri di Rivedere è probabilmente lì
  che vanno i 30 minuti.

### Le prove

`tests/acceptance/test_prima_le_autostrade.py` (la tavola D con lo sfiato, due nomi per lo stacco);
`tests/layout/test_la_distribuzione_del_caso_reale.py` (la fila della pompa in parallelo, i colori del collettore
e del circuito di carico, le coppie del collettore); `tests/validation/test_regole_del_piano.py` (A2). Rosse sul
codice di partenza, verdi adesso.

## 4. La 1.3.0

**3 ottobre 2026** · input **I-199** · decisione **D-205**, approvata

Il PO, sulla tavola dei simboli nuovi rifatta: «pr approvata fondi su main. dammi anche la skill v 1.3 da
scaricare.» Il pacchetto voleva la release dopo la tavola del caso; la 1.3.0 esce con i punti 1–4, e il caso rifatto
resta il punto 5.

```
$ python3 scripts/costruisci-skill.py
ZIP:   outputs/skill/disegnatore-mep.zip (694 kB, sha256 2d2870e738fb2495)
Controlli della guida di Anthropic, di skill-creator e del caricamento su claude.ai (al massimo 200 file): passati.
$ python3 -m pytest -q tests/test_le_release.py tests/test_package.py
7 passed
```

Lo ZIP ha 104 file; dentro ci sono le voci nuove del catalogo e della libreria, le famiglie CC, GA e DP, e lo schema
con `accessori_tolti`, `a_bordo`, `esistente`, `altrove`. Le tavole di regressione sono quelle della 1.2.2.

## 3. R3 — le voci del costruito, con il simbolo (I-194, I-197, I-198)

**3 ottobre 2026** · decisioni **D-203** (proposta; il contatore approvato) e **D-204** (approvata) · la forma la
approva il PO

### La tavola, per prima

`simboli-nuovi/tavola/` — un impianto piccolo che mette insieme le voci nuove: pompa di calore con i **giunti
antivibranti** sui due attacchi e il **contatore di calore «CC»** sul ritorno del primario; **volano a sei
attacchi** con i due **predisposti**, tappati, «al solare termico», la mandata sopra; **collettore d'appartamento
con mandata e ritorno** verso un ventilconvettore e un pannello; una derivazione **verso e da un impianto
esistente**; e, sotto, l'acqua fredda dall'acquedotto al **dosatore di polifosfati** e al bollitore in pompa di
calore.

```
Formato A2 · tratte 31 · tratte cedute 0 · rilievi bloccanti 0 · pieghe 7 · sormonti 0
```

Le tavole di regressione non cambiano (`confronta.sh`: 54 e 54, IDENTICI).

### Dopo la prima tavola: il PO (I-197, I-198)

«il contabilizzatore va bene. il volano a 6 tubi hai invertito mandata e ritorno sull'attacco del solare termico.
la mandata è sempre sopra il suo ritorno non viceversa. giunto antivibrante e dosatore polifosfati perche' non li
hai fatti? se servono e il progettista puo chiederli vanno messi.»

- **La mandata del predisposto sopra il ritorno.** Il motore colora una rete partendo da chi la alimenta; la coppia
  predisposta, senza nessuno a monte, era colorata al contrario, e il piano aveva seguito i colori. Ora un attacco
  predisposto che immette sta per la macchina che verrà ed è la **sorgente della sua rete**: la mandata esce da
  lui ed entra nel volano dall'attacco alto, il ritorno esce dal basso (`flow.py`, funzione `provision`).
  La prova lo misura sulle tratte classificate, non sul disegno.
- **Il giunto antivibrante** (`flexible-joint`, GA). Il progettista lo mette sull'attacco della macchina. Due cose
  non andavano, e le ha mostrate la tavola:
  - le regole posavano il loro corredo **fra il giunto e la pompa di calore**: ora tagliano il tubo oltre il giunto
    (`apply.py`, `_connection_to_split`);
  - così però la fila dei pezzi della pompa si contava dal giunto, e il filtro e il defangatore della macchina
    finivano dall'altra parte del contatore: il ritorno faceva un giro. Ora la fila si conta **dalla macchina dietro
    il giunto** (`runs.py`, `head_anchor`/`tail_anchor`), e il ritorno è quello di prima più il giunto:
    pompa ← giunto ← filtro ← defangatore ← vaso, riempimento, manometro ← contatore ← volano.
- **Il dosatore di polifosfati** (`polyphosphate-doser`, DP) e la nota del PO: «va installato esclusivamente sulla
  linea di ingresso dell'acqua fredda sanitaria che alimenta il boiler di accumulo dell'ACS … Non deve
  assolutamente essere inserito nell'acqua tecnica». Gli attacchi sono di acqua fredda; la validazione segue
  l'acqua dall'uscita del dosatore e ferma il grafo se non arriva a chi scalda l'ACS (`DOSER_NOT_ON_THE_DHW_FEED`) o
  se arriva a un riempimento (`DOSER_FEEDS_THE_TECHNICAL_WATER`). Capire §5 lo dice prima.

⚠ **Un mio errore, preso dalla suite**: il controllo del dosatore chiedeva al catalogo la geometria dei pezzi, che la
validazione topologica non deve pretendere — 17 prove di topologia rosse. E seguiva l'acqua da `endpoint_a` a
`endpoint_b`, un verso che il grafo non garantisce. Ora legge solo le definizioni e parte dall'attacco d'uscita del
dosatore; la prova nuova scrive i tubi al contrario e carica il catalogo senza simboli.

### Che cosa la tavola ha insegnato

- **Una scritta del progettista si perdeva in silenzio.** Alla prima posa «dal solare termico» non aveva un
  lato libero — accanto c'era la verticale del confine —, e il motore l'ha omessa senza dirlo. Ora è un rilievo
  **bloccante**, `FREE_LABEL_OMITTED`: la scritta l'ha data il progettista. Per la coppia di attacchi predisposti
  basta una scritta, come dice il documento del caso.
- **Il collettore con ritorno era alto 10**, con mandata e ritorno a 5 mm: le due intercettazioni che le regole
  ci posano si toccavano. Ora è 20 × 15, a 10 mm come i terminali.
- **Lo scarico e lo sfiato del volano** pendono già dai loro attacchi di servizio: il loro nome cita l'attacco da
  cui la regola parte, non quello a cui sono appesi. Lo spostamento su un attacco di servizio, scritto e poi
  tolto, non serviva.

### Le prove

`tests/acceptance/test_simboli_rel009.py` disegna la tavola di prova col comando della skill: zero bloccanti,
i simboli nuovi, le tre scritte; la mandata del predisposto entra dall'alto; il giunto sta attaccato alla pompa e
oltre di lui c'è il filtro della pompa. `tests/validation/test_dosatore_di_polifosfati.py` prova i due rilievi del
dosatore e il verso dei tubi. `test_preflight.py` prova `FREE_LABEL_OMITTED`. I conteggi della libreria salgono da
55 a 61 simboli.

## 2. R2 — gli accessori del costruito, e lo spostare (I-193)

**3 ottobre 2026** · decisione **D-201** (proposta, punto «altrove»)

- **Dichiarati**: sfiati con valvola a sfera sul ritorno di ogni pompa e sui volani, ritegni sulle mandate,
  manometro sui montanti, riduttore sull'acqua fredda, valvole sulle uscite dei collettori. Nessuno si raddoppia;
  le valvole sulle uscite dei collettori bastano già alla regola sull'ingresso dei terminali (16 in meno).
- **Spostati**: vaso, riempimento e manometro del primario sul secondario in centrale (T5), con quello che ne
  pende.
- **L'esistente** per pezzo e per tratto (I-195, D-202): un dato per le regole e i diametri; `completa` chiede
  del corredo che le regole posano sull'esistente (T6).

## 1. R1 — togliere, e «a bordo» per singola macchina (I-192)

**3 ottobre 2026** · decisione **D-201** (proposta)

### Le tavole, per prime: non cambia niente

Il punto 1 cambia il grafo completo, non il disegno. Le uscite di regressione, su `main` (`1dc2d80`) e sul ramo:

```
$ docs/collaudi/REL-005/pulizia-del-solutore/confronta.sh <main> <ramo>
file: 54 prima, 54 dopo
IDENTICI
```

La tavola del caso non c'è ancora: si fa al punto 5, quando la skill sa disegnare l'esistente.

### Sul caso, con le scelte T1–T5 del progettista

```
                                  1.2.2        con il punto 1
pezzi del grafo completo          207          149
accessori delle regole            114           64
tolti dal progettista               —           42
punti aperti                        0            0
```

I 42 tolti, ciascuno con il motivo:
- **T1**: le 32 intercettazioni su ingresso e uscita di ventilconvettori e pannelli;
- **T3**: i due separatori d'aria;
- **T4**: i due defangatori;
- **T5**: vaso, riempimento e manometro sul ritorno dei due primari, 6 pezzi.

Con loro se ne vanno i pezzi che ne pendevano: le intercettazioni dei separatori, la valvola bloccata aperta dei
vasi, il rubinetto portamanometro. Rilanciare le regole sul grafo completo non propone niente.

**T2**, le valvole di sicurezza delle sei pompe: dichiarate a bordo, le regole le posano lo stesso. La sicurezza
di ogni generatore la vuole anche col bordo (D-182), e `completa` lo dice; se sul costruito non ci sono, si
tolgono con «togli», e il motivo.

### Come si scrive

- `accessori_tolti`, nel grafo di prima stesura: `{"pezzo": "air-separator-tj-pr-3-b", "motivo": "…"}`. Il nome è
  quello che `completa` scrive accanto a ogni accessorio: è derivato dai dati — voce, pezzo, attacco — e non cambia
  da un rilancio all'altro.
- `a_bordo`, sulla singola macchina: le funzioni che porta dentro, coi nomi del catalogo (`"a_bordo":
  ["filtration"]`). Le regole lo leggono come il bordo del catalogo.
- `completa` riporta:
  - i tolti per famiglia, con il motivo;
  - le voci che non tolgono niente;
  - i pezzi dichiarati a bordo che la regola posa lo stesso.

  Un nome di funzione sconosciuto nel bordo ferma la validazione.
- Capire §3 e `SKILL.md` passo 4 dicono quando si scrivono. «Spostare» è togliere da una parte e dichiarare
  dall'altra: la seconda metà è il punto 2.

### Le prove

`tests/rules/test_accessori_tolti.py` (9 prove, sul caso) e una prova sull'uscita di `completa`. Senza il filtro
del motore le due prove centrali cadono.

```
$ python3 -m pytest -q
1991 passed, 15 skipped, 10 xfailed in 249.55s
```

`ruff check src tests` e `mypy src` verdi. I grafi agli atti restano identici byte per byte: un campo vuoto non
si scrive.
