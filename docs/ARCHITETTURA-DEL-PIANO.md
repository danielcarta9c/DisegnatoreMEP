# L'architettura della skill — che pezzi ha, e cosa fa ciascuno

**Data:** 20 settembre 2026 · **Stato:** vigente
**Decisioni che la fissano:** **D-151**, **D-155**, **D-156**, **D-157**, **D-158**

> **Il documento da leggere prima di toccare qualunque cosa.** Dice **quali sono i pezzi
> della skill**, **di che pasta è fatto ciascuno** — agente AI, deterministico, o misto — e
> **che cosa passa fra l'uno e l'altro**.
>
> È stato scritto perché una sessione ha sbagliato lo sviluppo pur avendo tutte le decisioni
> sotto gli occhi: ha trattato il **piano** come un artefatto da consegnare invece che come
> qualcosa che la skill deve **imparare a scrivere**. Se stai per fare una cosa che questo
> documento non prevede, non è una svista del documento: fermati e chiedi al PO.

---

## 1. I cinque pezzi

```
   1 CAPIRE          2 COMPLETARE       3 COMPORRE         4 ESEGUIRE        5 RIVEDERE
   agente AI         deterministico     agente AI          deterministico    AI + controlli
  ┌───────────┐     ┌───────────┐     ┌───────────┐      ┌───────────┐     ┌───────────┐
  │  testo    │     │  grafo    │     │  grafo    │      │  piano    │     │ tavola +  │
  │ ingegnere │ ──> │ 1ª stesura│ ──> │ completo  │ ───> │           │ ──> │  rilievi  │
  └───────────┘     └───────────┘     └───────────┘      └───────────┘     └───────────┘
        │                 │                 │                  │                 │
        ▼                 ▼                 ▼                  ▼                 ▼
   grafo 1ª           grafo completo     PIANO            tavola + rilievi    VINCOLI
   stesura            + domande                                                  │
                           │                 ▲                                   │
                           ▼                 └───────────────────────────────────┘
                  [ l'ingegnere approva ]          il revisore rimanda al 3,
                                                        non al 4
                          └──────────── 3 + 4 = instradatore-disegnatore ─────────┘
                                                (ed è MISTO)
```

| | pezzo | di che pasta è | esiste? |
|---|---|---|---|
| **1** | **Capire** — dal testo dell'ingegnere al grafo di prima stesura | **agente AI** | **sì** — `skill/capire/` |
| **2** | **Completare** — accessori, ordine, domande all'ingegnere | **deterministico** | **sì** — `src/disegnatore_mep/rules/` |
| **3** | **Comporre** — dal grafo completo al **piano** | **agente AI** | **no, ed è il buco** |
| **4** | **Eseguire** — dal piano alla tavola e ai rilievi | **deterministico** | **sì** — `src/disegnatore_mep/piano/esecutore.py` e `layout/` |
| **5** | **Rivedere** — dalla tavola ai **vincoli** per il pezzo 3 | **AI + controlli deterministici** | **a metà** — i controlli ci sono, l'occhio no |

**I pezzi 3 e 4 insieme sono l'instradatore-disegnatore, ed è misto**: l'agente decide
**dove stanno i pezzi**, lo script deterministico fa **tutto il resto**. Il tentativo di
farlo interamente deterministico è stato fatto, è durato sei settimane ed è fallito: la
ragione è in §4.

**Il pezzo 5 rimanda al 3, mai al 4.** Si corregge il **piano**, non il disegno. Un revisore
che ritoccasse la tavola sarebbe un disegnatore che cancella sopra, e il giro dopo il difetto
tornerebbe.

---

## 2. Che cosa attraversa la catena, e che cosa nasce dentro

**Una sola cosa attraversa la catena da un capo all'altro: il grafo dell'impianto.** La
tavola è una sua vista. Nessun pezzo a valle modifica la connettività che l'ingegnere ha
approvato: si spostano pezzi, non si collegano pezzi.

**Il piano non è un ingresso del sistema** (**D-155**). Nasce dentro, al pezzo 3, e muore
quando la tavola è uscita. Non esiste «il piano dell'impianto N» da tenere in repository, e
chi ne trova uno deve sapere perché sta lì:

> ⚠ **I cinque piani in `docs/collaudi/PROVA-PIANO/` non sono prodotto.** Sono **materiale di
> collaudo del pezzo 3**: piani scritti a mano da un agente in sessione, che servono come
> **bersaglio** — il pianificatore deve arrivarci da solo. Sono nella stessa posizione in cui
> stanno i grafi di `skill/capire/prova-2026-08-07/`, che nessuno ha mai scambiato per
> prodotto.

---

## 3. I pezzi, uno per uno

### Pezzo 1 — Capire · agente AI

Dal testo dell'ingegnere al **grafo di prima stesura**. Trascrive, non progetta: ciò che il
testo non dice e che servirebbe diventa una **domanda dichiarata**, mai un'invenzione.

Vive in `skill/capire/`, ed è **la forma che tutti i pezzi AI devono avere**:

- **`ISTRUZIONI.md`** — parlano all'agente, e bastano da sole. «Non serve leggere altro.»
- **`CONSEGNA.md`** — che cosa restituisce e come si giudica.
- **le prove in camera pulita** — un agente avviato da zero, il suo esito agli atti.

### Pezzo 2 — Completare · deterministico

Il motore delle regole aggiunge gli accessori che il grafo non ha e li mette in ordine, e
produce i **punti aperti**: gli accessori che servirebbero e che non si possono proporre.
Poi **l'ingegnere approva il grafo definitivo**, ed è l'unico cancello umano dentro la
catena.

`src/disegnatore_mep/rules/`, comando `disegnatore-mep rules`.

### Pezzo 3 — Comporre · agente AI · **non esiste**

Dal grafo completo al **piano**: un file che dice **dove stanno i pezzi posabili**, e
nient'altro.

Riceve: il grafo completo, `docs/regole-del-piano.md`, le tavole di riferimento del
disegnatore del PO (`docs/input-pm/riferimenti-grafici/`), e — dal secondo giro in poi — i
**vincoli** che il revisore ha scritto.

**Che cosa il piano non contiene, perché si deduce.** La rotazione di un **raccordo** e
quella di un pezzo con **un attacco solo** si calcolano dai vicini che il pezzo ha davvero:
un prodotto scalare, nessun peso. La deduzione vince sempre sulla ricerca.

**Che cosa il piano contiene e nessuno può dedurre:** la posizione di ogni pezzo posabile, e
la rotazione di una **macchina con due o più attacchi**, che ha una scelta.

> ⚠ **Un buco noto:** un pezzo con **due** attacchi che non è una macchina — il gruppo di
> riempimento — non rientra in nessuno dei due casi, e la sua rotazione va scritta a mano.

**Oggi questo pezzo lo fa un umano**, cioè l'agente in sessione, a mano. È esattamente il
lavoro che manca.

### Pezzo 4 — Eseguire · deterministico

Dal piano alla tavola. **Non cerca niente**: posa gli accessori appesi, orienta i raccordi,
instrada in griglia, interrompe le linee sotto i simboli, impagina, disegna, misura.

`src/disegnatore_mep/piano/esecutore.py` più tutto `layout/`, comando
`disegnatore-mep piano`. È la parte che la ricerca del 4 agosto §3 dichiara sana — «regge la
meccanica» — ed è quella che **resta**.

Esce con la tavola **e con i rilievi**: il preflight di qualità e i controlli delle regole
(`validation/preflight.py`, `validation/regole.py`).

### Pezzo 5 — Rivedere · agente AI + controlli deterministici

È **D-114**, scritta il 9 agosto e mai costruita: «il validatore AI smette di essere un
cancello a valle e diventa supervisore in anello chiuso».

**Due metà, e vanno tenute distinte.**

| metà | che cos'è | stato |
|---|---|---|
| **i controlli** | le quattro regole di D-154 più il preflight; il **punteggio** lessicografico; le **condizioni d'arresto**; la guardia che non peggiora in silenzio | **deterministica, e c'è** |
| **l'occhio** | guarda la **tavola**, con accanto quelle del disegnatore del PO, e scrive i **vincoli** | **agente AI, e manca** |

**Il revisore non sposta niente. Dichiara vincoli** (**D-157**), e il pianificatore
ricompone rispettandoli. §5 dice perché, e non è una preferenza di stile: è una misura.

---

## 4. Che cosa è morto, e perché — perché nessuno lo rifaccia

### Il solutore

`improve.py` e la fase del tronco di `spine.py` cercavano il disegno minimizzando una **somma
pesata**: curve, attraversamenti, lunghezza, riempimento, copertura, squilibrio, margine.
Sette manopole. `dilate.py` allargava il disegno per riempire il foglio.

**Il difetto non era la taratura, era la forma della domanda.** Una somma pesata **non sa
esprimere una gerarchia di giudizio**. Il PO, guardando l'autostrada che si piegava mentre
gli stacchetti restavano dritti:

> «Abbiamo ottimizzato le curve e gli attraversamenti sugli attacchetti e abbiamo fatto sta
> curva senza senso.»

Una piega dell'autostrada e una piega di uno stacco pesavano quasi uguale, e **una somma si
compra sempre**. E nessun peso dice «un collettore è **una** linea dritta»: quella è una
figura, non un punteggio.

I tre moduli **restano agli atti** e lo dichiarano in testa, ciascuno con quando è morto,
perché, e dove è finito il suo lavoro. Nessun percorso vigente li chiama, e una prova lo
sorveglia (`tests/layout/test_il_solutore_e_fuori.py`).

### Il revisore a mosse

Il primo revisore, costruito il 20 settembre, **spostava i pezzi** con cure scritte a mano.
Misurato sui cinque impianti: **la prima correzione ha peggiorato su quattro su cinque.**
Ogni mossa è cieca a quello che le altre regole stavano tenendo — la cura di A1 spostava il
radiatore e piegava un'autostrada, quella di B1 spostava l'accumulo e rompeva le due
primarie, che erano due rette.

**Un revisore a mosse è un solutore in miniatura**, e sbaglia per la stessa ragione.

---

## 5. I vincoli: il linguaggio fra il pezzo 5 e il pezzo 3

**Un vincolo e una regola sono la stessa cosa.** Una riga di `docs/regole-del-piano.md` è uno
**schema di vincolo**; una correzione del revisore è quello schema **istanziato su
identificativi veri**. Un solo vocabolario, non due — ed è il motivo per cui scrivere bene le
regole è anche scrivere bene il revisore.

| regola | vincolo che genera |
|---|---|
| **A1** — tre fasce verticali | `fascia: {radiatori: distribuzione}` |
| **A4** — un organo di servizio sta addosso al pezzo che serve | `addosso-a: {utenze: bollitore}` |
| **B1** — l'autostrada è dritta | `stessa-quota: [pdc.water_supply, deviatrice.in, volano.primary_in]` |
| **B3** — collettore verticale | `stessa-verticale: [cascata-mandata-a, cascata-mandata-b]` |
| **B4** — la tre vie non spezza il tratto | `in-linea: [deviatrice.in, deviatrice.out_a]` |
| — | `passa-per: {tratta: w2-a, punto: {x, y}}` |

**Perché vincoli e non mosse.** Una mossa è imperativa e cieca: due mosse si combattono. Un
vincolo è dichiarativo: si accumula fra un giro e l'altro, si controlla per coerenza **prima**
di comporre, e sopravvive alla ricomposizione.

### Le tre regole che tengono i vincoli lontani dal solutore

1. **Gerarchia, mai somma.** L'ordine è quello in cui il PO ha dettato le regole: **A1 prima
   di B1 prima di B3 prima di B4** — prima dove stanno i pezzi, poi come corrono le linee.
   Quando due vincoli si contendono lo stesso pezzo, **quello sotto cede e lo dice**. Il
   giorno in cui diventassero pesi da sommare, il solutore è rientrato dalla finestra.
2. **I vincoli nascono da un rilievo su una tavola vera**, pochi per giro. Non si generano a
   tavolino: è così che è nata la funzione di costo.
3. **Un tetto dichiarato ai giri**, e quando si ferma dice perché.

### Il confine che non si passa: punto di passaggio sì, nodo del grafo no

| | che cos'è | chi decide |
|---|---|---|
| **punto di passaggio** | «questa tratta passa per (300, 250)» — non tocca il grafo | **il revisore**, liberamente |
| **nodo del grafo** | un raccordo vero, un pezzo che si compra e si monta | **il PO**: il revisore lo **propone** come domanda dichiarata |

Aggiungere un nodo al grafo per far girare una linea vuol dire che **il disegno ha cambiato
l'impianto**. È la stessa specie di errore che il 20 settembre ha mandato l'acqua fredda
sull'uscita primaria dell'accumulo: una deduzione grafica che produce un errore di contenuto.
L'ha visto il PO guardando la tavola, non una misura.

---

## 6. La divisione che serve a lavorare

**Ogni difetto è o del motore o del pianificatore, e va classificato.** È il guadagno più
grande di questa architettura: prima ogni difetto era «la funzione di costo» e non si sapeva
dove mettere le mani.

| | difetto del **motore** (pezzi 2 e 4) | difetto del **pianificatore** (pezzo 3) |
|---|---|---|
| **suona così** | «il motore ha fatto una cosa che nessuno gli ha chiesto» | «il piano ha messo il pezzo dove non andava» |
| **si cura con** | codice migliore | una regola in più |
| **esempi misurati** | la mappa delle porte rimappata anche sulle macchine; la spezzata di ripiego che tornava su sé stessa; `may_stack` irraggiungibile | il prelievo ACS a 502,5 mm dal bollitore; il disegno tutto nella metà alta; un pezzo preso dal lato sbagliato |

Le due code si lavorano **in parallelo** e non si contendono niente.

---

## 7. La trappola che D-151 ha aperto, e che va sorvegliata

**D-151 ha spostato la posa dal motore al piano.** Tutto ciò che il motore garantiva
**posando** è oggi **sovrascrivibile dal piano**, e senza un rilievo che lo misuri sulla
tavola finita si viola **in silenzio**.

È già successo, ed è la prova che serve: **D-145** dice che un confine di rete sta addosso al
pezzo che serve, con lo stacco minimo. È un vincolo della posa. Il 20 settembre un agente ha
composto tre piani applicando A1 — «la distribuzione sta a destra» — e ha portato il prelievo
ACS a **205, 502 e 152 millimetri** dal bollitore, contro i **32 e 50** dei due piani
composti prima che A1 fosse un controllo. **Ha peggiorato una cosa che funzionava applicando
una regola**, e niente gliel'ha detto.

**Da qui D-158: ogni vincolo di posa ha un rilievo sulla tavola consegnata.** Vale per tutte
le regole su *dove sta un pezzo rispetto a un altro* — A1, A2, A3, A4.

> ⚠ E vale anche al contrario, per chi aggiunge una regola: **una regola che vive solo nella
> posa del motore è una regola che il piano può rompere.** Quando ne scrivi una, scrivi il
> rilievo, non solo il vincolo.

---

## 8. Quello che questa architettura costa, e va detto

- **La riproducibilità bit-per-bit se ne va** (D-023, sospesa da D-151): due composizioni
  dello stesso impianto non danno la stessa tavola. Per un elaborato che esce in DXF e si
  rifinisce in AutoCAD (I-072) è un prezzo accettabile, ed è una scelta di prodotto del PO.
- **Il motore non garantisce più che il disegno sia bello**: garantisce che sia **valido** e
  che i difetti siano **nominati**. Il bello lo porta il piano.
- **Senza un piano la via ordinaria è peggiorata**, ed è misurato: senza il solutore e senza
  un piano i cinque impianti di prova finiscono tutti sul formato più grande col ripiego, con
  2–6 tratte cedute ciascuno. È la ragione per cui il pezzo 3 deve esistere.
- **Il giudizio resta del PO**, e resta sulle tavole (D-146).
