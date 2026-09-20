# Com'è fatta la skill

**Stato: vigente. Riallineato il 20 settembre 2026 a D-151** (`DRAW-015`).

La posa non è più una **ricerca**. Il disegno lo **compone** un agente, il motore lo
**esegue e lo misura**, un revisore rilegge i rilievi e **corregge il piano**. Il ciclo di
miglioramento (`layout/improve.py`), la fase del tronco di `layout/spine.py` e
`layout/dilate.py` **restano agli atti e non decidono più la posa** (D-151, D-149).

> **Questo è il documento che mancava.** Dice di quali pezzi è fatta la skill, cosa fa
> ciascuno, con cosa lavora e **quando è finito**. Se una domanda comincia con «come
> funziona…» o «di chi è questo pezzo…», la risposta è qui e in nessun altro posto.
>
> **La catena del disegno sta in `docs/ARCHITETTURA-DEL-PIANO.md`**, che dice chi decide
> cosa ed è il documento che vince su ogni contrasto; le regole con cui si compone stanno
> in `docs/regole-del-piano.md`, che il PO ha dichiarato aperto.
>
> **ADR 0005 è superata da D-151** e vale come storia: fissava sette pezzi e il confine
> «nessuna AI disegna, nessuna AI corregge il disegno», che è esattamente ciò che D-151 ha
> cambiato.
>
> Non contiene stato («a che punto siamo» sta in `PROJECT_STATE.md`), non contiene storia
> («perché abbiamo deciso così» sta in `docs/DECISION_LOG.md`), non contiene numeri di
> stampa (stanno in `docs/standard/GRAPHIC_STANDARD.md`).

---

## 1. Cosa fa la skill, in tre righe

L'ingegnere ha già deciso e dimensionato l'impianto. Glielo dice a parole, nella
conversazione. La skill capisce di che impianto si tratta, **aggiunge gli accessori che
mancano e che un impianto deve avere**, glieli fa approvare, e poi ne **disegna la tavola
tecnica** — pronta da stampare e da portare in cantiere.

Il prodotto finale non è il solo pacchetto Python: è una **skill/tool installabile nelle
chat di lavoro** che orchestra interpretazione, approvazione, motore deterministico,
verifica e restituzione degli artefatti. `CLAUDE.md` istruisce l'agente che sviluppa il
repository e non è l'entrypoint della skill destinata all'utente.

**Quello che la skill non fa mai:** progettare. Non inventa potenze, temperature,
prevalenze, tarature, volumi né diametri. Se il progettista glieli dà, li scrive sulla
tavola; se non glieli dà, sulla tavola non compaiono (D-087).

**Il confine, detto come lo ha detto il PO** (D-104). Lui porta lo schema a livello di
**definitivo**; la skill lo porta a livello **esecutivo** aggiungendo la ferramenta che su
una tavola esecutiva c'è sempre — le intercettazioni, uno sfiato, un filtro, uno scarico,
gli strumenti di lettura. Nient'altro. In particolare: **non decide quanti pezzi ci
vanno** — un vaso di espansione, non due — e **non cambia lo schema che ha ricevuto**. Una
prescrizione normativa dice cosa deve avere *l'impianto*; non autorizza la skill ad
aggiungerlo. La fonte serve a sapere **dove** va un pezzo che comunque si disegna, non
**se** l'impianto debba averlo.

---

## 2. La catena, e il grafo che l'attraversa

**Una cosa sola attraversa tutta la skill: il grafo dell'impianto** (D-099). Non un
modello, poi delle catene di pezzi, poi una geometria: lo **stesso** grafo, che nasce
abbozzato dalla conversazione, si arricchisce di nodi e diventa definitivo. La tavola è la
sua **rappresentazione**, non un oggetto separato.

Il grafo è fatto come una rete stradale (D-097): ogni pezzo — macchina o accessorio — è un
**nodo con la propria sigla**; ogni tubo fra due pezzi è un **arco** con il proprio fluido.
Le sigle si assegnano camminando dalle **sorgenti dichiarate** — i generatori di calore per
i circuiti termici, l'acquedotto per il sanitario — nell'ordine in cui i pezzi si incontrano
seguendo il fluido (D-098).

**Ogni attacco porta una tubazione sola, sempre** (D-100). Due tubi sullo stesso bocchello
non esistono: dove due tubazioni si incontrano c'è un **pezzo** che le unisce, con la
propria sigla. Sono due pezzi distinti, e la differenza conta: la **confluenza** fa
diventare due tubazioni una sola, e ha tutti e tre gli attacchi sul percorso; la
**ripartizione** ne sdoppia una — il ritorno comune che rientra su due macchine in
parallelo — e vale lo stesso. La **derivazione** è un terzo pezzo: il suo braccio esce dal
percorso, e ci pende un accessorio.

**Una macchina ha più attacchi di quelli del flusso** (D-101). Un volano a quattro tubi non
ha quattro attacchi: i cataloghi dei costruttori dichiarano anche lo sfiato, lo scarico e la
sede della sonda. Sono **attacchi di servizio**, ciascuno esiste per una funzione precisa, e
il catalogo li dichiara macchina per macchina.

> ⚠ **Il piano non è un ingresso della skill** (**D-155**). Nasce al pezzo 3a e muore quando
> la tavola è uscita: **non esiste «il piano dell'impianto N»**, e il pianificatore è un pezzo
> che la skill deve **imparare a scrivere**. I cinque piani scritti a mano che si trovano nel
> repository sono **materiale di collaudo** del pezzo 3a — il bersaglio che deve pareggiare.

La catena è quella di `HANDOFF.md` §«Catena invariabile» e di
`docs/ARCHITETTURA-DEL-PIANO.md` §1, e si legge in sette passi:

```
   la conversazione con l'ingegnere
              │
        ┌─────┴──────┐
        │  1. CAPIRE │  l'AI interpreta                ← non deterministico
        └─────┬──────┘
              │  GRAFO DI PRIMA STESURA — solo ciò che l'ingegnere ha detto
        ┌─────┴──────────────┐
        │ 2. COMPLETARE      │  regole degli accessori: cosa manca e perché
        └─────┬──────────────┘
        ┌─────┴──────────────┐
        │ 2bis. ASSEMBLARE   │  dove va ciascuno: la fila lungo ogni tubo
        └─────┬──────────────┘
              │  GRAFO DEFINITIVO — leggibile come testo, senza disegnare niente
        ┌─────┴──────────────┐
        │    L'INGEGNERE APPROVA         ← cancello: niente si disegna prima
        └─────┬──────────────┘
        ┌─────┴──────────────┐
        │ 3a. COMPORRE       │  il pianificatore dice DOVE STANNO I PEZZI,
        └─────┬──────────────┘  e nient'altro                    ← agente
        ┌─────┴──────────────┐
        │ 3b. ESEGUIRE       │  il motore orienta, instrada, interrompe,
        └─────┬──────────────┘  impagina, disegna e MISURA  ← deterministico
              │  usa: 4. LIBRERIA DEI SIMBOLI   e   5. CARTIGLIO
              │  produce: la tavola   +   i rilievi del 6. VERIFICARE
        ┌─────┴──────────────┐
        │ 3c. RIVEDERE       │  il revisore rilegge i rilievi, guarda la
        └─────┬──────────────┘  tavola e CORREGGE IL PIANO       ← agente
              │  si torna a 3b, finché non resta nessun rilievo bloccante
              │
       la chat restituisce la tavola e i rilievi
```

**I passi 3a–3c sono nuovi (D-151) e sostituiscono il solutore.** Il passo 3c **si
costruisce adesso** (D-153): finché non esiste, l'anello lo chiude l'agente a mano.

**Il cancello dell'approvazione non è opzionale**: senza di essa la skill modificherebbe
l'impianto dell'ingegnere in silenzio (D-004, D-013). E **l'agente non modifica
connettività approvata: sposta pezzi, non collega pezzi** (`HANDOFF.md`).

**L'occhio terzo non è più un cancello a valle.** D-114 — «il validatore AI smette di
essere un cancello a valle e diventa supervisore in anello chiuso» — è scritta il 9 agosto
e costruita da D-151: quel giudizio è il **revisore**, ed entra nell'anello invece di stare
alla fine. Il giudizio finale del prodotto resta del PO, e si dà **sulle tavole** (D-146).

**Dove si guarda cosa.** Il contenuto — quali pezzi, in che punto, su che fluido — si
giudica sul **grafo scritto**, non su un disegno (D-096). Il disegno è il banco di prova
del motore, dei validatori e della skill finita. Se il grafo è sbagliato, la tavola non
c'entra. Se il grafo è giusto e la tavola è brutta, il difetto è **o del motore o del
pianificatore**, e la prima cosa da fare è dire quale dei due
(`docs/ARCHITETTURA-DEL-PIANO.md` §3).

Ogni pezzo si costruisce e si collauda **da solo**, con un contratto suo. Il disegno di
prova serve a **scoprire** i difetti, mai a **definire** cosa è giusto (D-092).

---

## 2bis. Di che pasta è fatto ogni pezzo

**È la domanda che decide tutto, e va risposta prima di costruire.** Un pezzo fatto di
istruzioni per un'AI e un pezzo fatto di programma non si scrivono, non si provano e non
si correggono allo stesso modo.

> **Due numerazioni, e sono la stessa cosa.** `docs/ARCHITETTURA-DEL-PIANO.md` conta **i
> cinque pezzi della catena**; questa tabella conta **tutti i pezzi della skill**, dati
> compresi. Si leggono così, e chi trova una differenza fra i due documenti segnali il
> difetto invece di scegliere:
>
> | architettura | qui |
> |---|---|
> | 1 Capire | 1 |
> | 2 Completare | 2 e 2bis |
> | 3 Comporre | 3a |
> | 4 Eseguire | 3b, con 4 (simboli), 5 (cartiglio) e 6 (verificare) che lo servono |
> | 5 Rivedere | 3c, che riceve i rilievi del 6 |

| # | Pezzo | Di cosa è fatto | Dove vive |
|---|---|---|---|
| 1 | **Capire** | **Agente AI**, istruito con file di testo `.md` che gli spiegano cosa deve tirare fuori dalla conversazione e cosa non deve inventare | istruzioni della skill |
| 2 | **Completare** | **Programma deterministico** che legge **regole scritte come dato** (un file per regola) e le applica al modello | motore in codice, regole in file di dati |
| 2bis | **Assemblare** | **Programma deterministico**: mette in fila i pezzi lungo ogni tubo secondo la posizione che ogni regola dichiara | codice + la posizione dichiarata in ogni regola |
| 3a | **Comporre** | **Agente AI**, che segue le regole di `docs/regole-del-piano.md` e produce un **piano**: un file leggibile e correggibile a mano | istruzioni della skill + il foglio di regole |
| 3b | **Eseguire e misurare** | **Programma deterministico**: posa gli accessori appesi, orienta, instrada in griglia, interrompe, impagina, disegna, misura. Non cerca niente | codice |
| 3c | **Rivedere** | **Agente AI**, che legge i rilievi, **guarda la tavola** e scrive **vincoli** per 3a — mai mosse (**D-157**). Insieme a lui, deterministici, i controlli e le condizioni d'arresto | istruzioni della skill + codice |
| 4 | **Libreria simboli** | **Dati**: per ogni simbolo un disegno vettoriale e una scheda che dichiara taglia, attacchi, imbocchi ammessi, rotazioni e fonte | file, uno per simbolo |
| 5 | **Cartiglio** | **Dati**: un modello di riquadro fornito dall'azienda, riempito coi dati del progetto | file fornito dal PO |
| 6 | **Verificare** | **Programma deterministico**: controlli di correttezza e preflight di qualità. I rilievi che produce sono l'ingresso del pezzo 3c | codice |

### La linea di confine, e perché sta lì

```
   AI          →   interpreta LA CONVERSAZIONE   (pezzo 1)
   PROGRAMMA   →   completa e ordina IL GRAFO    (pezzi 2, 2bis)
   AI          →   compone IL PIANO              (pezzo 3a)
   PROGRAMMA   →   esegue, disegna e MISURA      (pezzi 3b, 4, 5, 6)
   AI          →   rilegge i rilievi e CORREGGE IL PIANO   (pezzo 3c)
```

**L'agente compone e corregge il piano; non tocca la geometria.** Il piano dice **dove
stanno i pezzi**, e nient'altro: non coordinate di linee, non simboli, non scelte MEP. La
connettività approvata non si tocca — si spostano pezzi, non si collegano pezzi.

**Quello che si può dedurre non entra nel piano, e non si cerca.** La rotazione di un
raccordo, quella di un pezzo con un attacco solo, la mappa degli attacchi: si deducono dai
vicini che il pezzo ha davvero, e **la deduzione vince sempre sulla ricerca** (D-151). Una
macchina con due o più attacchi **ha** una scelta, e quella è del pianificatore.

**Il prezzo, ed è dichiarato.** La riproducibilità bit-per-bit di **D-023** se ne va: due
composizioni dello stesso impianto non danno la stessa tavola. È accettabile perché
l'elaborato esce anche in **DXF** e il disegnatore lo rifinisce in AutoCAD (I-072, D-148),
ed è una scelta di prodotto del PO. ⚠ **L'export DXF non è ancora costruito**: `I-072` è
aperta, e in `src/` non c'è nulla che lo scriva — il prezzo è già pagato, la contropartita
no. Il motore non garantisce più che il disegno sia
**bello**: garantisce che sia **valido** e che i difetti siano **nominati**. Il bello lo
porta il piano, e il giudizio resta del PO, sulle tavole (D-146).

### Come sono fatte le regole del pezzo 2 — la risposta esatta

**Non sono programma e non sono un database. Sono file di dati, uno per regola.** Ogni
file dice, in forma leggibile anche da un non programmatore:

- **quando** si applica — espresso solo con le **funzioni** dei componenti («qualsiasi cosa
  si manutenga», «qualsiasi generatore»), mai col nome di un componente;
- **quante volte** può proporre — una per rete, una per componente, una per attacco o
  **una per gruppo/tratto**, secondo lo scopo dichiarato dalla regola;
- **cosa** propone e **in che punto** funzionale;
- **come si riconosce che c'è già**, così rieseguirla non duplica niente;
- **perché**, in una frase leggibile dal PO, e da **quale fonte** viene.

Questo è il motivo per cui sono dati e non codice: **si aggiunge una regola aggiungendo un
file, senza toccare il programma.** Se per aggiungere una famiglia di accessori servisse
modificare il motore, il motore sarebbe sbagliato. Ed è anche il motivo per cui una regola
deve essere generale (D-090): una regola scritta su misura di un componente è codice
travestito da dato.

Stessa logica per il pezzo 4: un simbolo si aggiunge aggiungendo due file, non toccando il
programma.

---

### Pezzo 1 — Capire

**Cosa fa.** Legge la conversazione e costruisce il **modello dell'impianto**: quali
macchine ci sono, quanti attacchi ha ciascuna, quali tubi le collegano, a quale rete
appartiene ogni tubo (riscaldamento andata, riscaldamento ritorno, acqua fredda, acqua
calda sanitaria…).

**Con cosa lavora.** Solo con quello che l'ingegnere ha detto. Ciò che è ambiguo diventa
una domanda, non un'invenzione.

**Cosa deve capire, e cosa chiede.** Le regole cambiano esito su **quattro** dati, e
sono quelli che l'interprete deve ricavare dal testo: che macchina è ciascun pezzo (e
quindi se produce calore, se produce anche il sanitario da sola, se tiene una riserva e
di quale acqua, da dove la riempie, cosa porta già a bordo); che acqua porta ogni
circuito; il regime della centrale; come i circuiti toccano una riserva. L'elenco, con
il conto di quante regole dipendono da ciascuno, è in `skill/capire/COSA_DECIDE.md`.

Ciò che il testo dà, si **legge** — comprese le potenze, da cui si ricava il regime.
Ciò che il testo non dà si **chiede**, ma solo quando valgono tutte e tre: il testo
davvero tace, le due strade sono entrambe corrette, e la scelta cambia il disegno.
Altrimenti si sceglie la strada convenzionale e si **dichiara**, così l'ingegnere
corregge tutto in un colpo solo (D-006, D-013).

**Cosa produce.** Il modello — **l'unica fonte di verità del progetto**. Non contiene
coordinate: dove sta un pezzo sul foglio lo decide il pezzo 3, e si può ricalcolare
sempre.

**È finito quando** da una descrizione a parole esce un modello che l'ingegnere riconosce
come il proprio impianto, e ogni cosa non detta è o una domanda posta o un'assunzione
dichiarata.

---

### Pezzo 2 — Completare: le regole degli accessori

**Cosa fa.** Guarda il modello e dice cosa manca: *«questo circuito chiuso non ha il vaso
di espansione», «questa macchina non si può isolare per manutenzione», «il ritorno del
generatore non ha il defangatore»*. Ogni proposta porta il **perché** e la **fonte**.

**Come è scritta una regola — e questo è il punto che abbiamo sbagliato.** Una regola
parte dal **motivo per cui l'accessorio esiste**, ed è sempre **generale**:

> La valvola di intercettazione serve a chiudere l'acqua per smontare o sostituire un
> pezzo o un gruppo che si manutiene insieme. Quindi va su **ogni tubo che esce dal
> gruppo verso l'impianto**, senza duplicarla fra membri dello stesso gruppo né sullo
> stesso tratto condiviso.

Non «il volano vuole quattro valvole». Quattro è il *risultato*, perché quel volano ha
quattro attacchi. Il catalogo dichiara le **proprietà** dei componenti (si manutiene, si
sostituisce, sporca il circuito, produce aria, va protetto dalla sovrapressione) e le
regole leggono quelle proprietà — mai il nome di un componente (D-069, D-090).

Ogni accessorio ha la propria ragione di posizionamento, ed è buona pratica consolidata:

| Accessorio | Perché sta lì |
|---|---|
| Valvola di intercettazione | per isolare un pezzo o gruppo senza svuotare l'impianto → sui tubi che escono dal gruppo, un solo organo per tratto condiviso |
| Filtro a Y | protegge lo scambiatore stretto → sul ritorno di **ogni generatore**, e solo sul primario |
| Defangatore | i fanghi viaggiano col ritorno → **uno solo**, sul ritorno generale, a monte della prima ripartizione |
| Separatore d'aria | l'aria si libera dove l'acqua è più calda → sulla mandata generale, **sopra i 35 kW**; sotto basta lo sfogo sul serbatoio |
| Vaso di espansione | l'acqua scaldata dilata → sul ritorno generale, dove lavora più freddo, sempre raggiungibile |
| Valvola di sicurezza | deve poter scaricare **sempre** → fra lei e ciò che protegge non ci va nulla di chiudibile: sotto i 35 kW **una per circuito chiuso**, sulla mandata comune subito dopo la confluenza dei generatori, prima di ogni intercettazione (I-046); sopra i 35 kW una per generatore che non la dichiara a bordo; una propria solo alla macchina che il catalogo dichiara **senza** sicurezza e che le sue intercettazioni isolano dal circuito; se il catalogo tace, il dato è ignoto e il motore chiede al progettista invece di aggiungere |
| Gruppo di riempimento | è una **derivazione dall'acqua di rete** sul ritorno generale, non un organo di passaggio |
| Scarico | da dove la riserva si riempie, da lì si svuota → sull'attacco dedicato, o sull'alimentazione della riserva |
| Miscelatrice sanitaria | miscela caldo e freddo → vuole **entrambe** le alimentazioni |

### I due livelli che il posizionamento usa, oltre al componente e all'attacco

**Il tratto comune** (D-106). Il corredo di un circuito — vaso, riempimento, manometro,
defangatore — non appartiene a una macchina: appartiene al **ritorno generale**, il
tratto attraversato da tutta l'acqua che torna, a monte di dove si divide verso le
macchine. Si trova camminando sulla struttura dai generatori e aprendosi sui rami, mai
scegliendo dall'ordine del file. Dove quel tratto non esiste — succede — la regola non
sceglie un ramo: apre un **punto aperto** e la scelta torna al progettista.

**Il regime della centrale** (D-106, D-108). Sotto e sopra i 35 kW le regole sono
diverse, e i due regimi non si mescolano mai sullo stesso impianto. Il regime **si legge
dalle potenze che il progettista ha dichiarato**: sommarle e confrontarle con la soglia
non è dimensionare — il dato è suo, la soglia ha radice normativa, il conto è aritmetica.
Se le potenze non ci sono, il regime resta non dichiarato, vale il corredo minimo, e
quella è una domanda per l'ingegnere.

**È finito quando** le regole coprono le famiglie dichiarate, ognuna è generale, ognuna ha
una scheda leggibile da un non tecnico, e l'ingegnere ha approvato il dossier.

---

### Pezzo 2bis — Assemblare: la sequenza dei pezzi

**Cosa fa.** Prima che esista qualunque disegno, scrive **per ogni tubo la fila ordinata
dei pezzi** che ci stanno sopra:

    pompa di calore → valvola → filtro a Y → defangatore → tratto di tubo → valvola → volano

**Perché serve, e perché la sua mancanza si vede in tavola.** Oggi ogni regola infila il
proprio accessorio per conto suo e l'ordine che ne esce non l'ha deciso nessuno: sul
volano due valvole finiscono affiancate dalla stessa parte e tre attacchi restano nudi.
Peggio: l'ordine dipende dall'ordine alfabetico dei nomi dei file delle regole. Un ordine
impiantistico deciso dal nome di un file non è un ordine (D-093).

**Come lo fa.** Ogni regola, oltre a dire *cosa* propone, dichiara **dove sta nella
catena**: attaccato alla macchina, prima dell'intercettazione, subito dopo, lato impianto.
L'assemblatore mette in fila secondo quelle dichiarazioni. Sono le stesse ragioni
impiantistiche del pezzo 2: la sicurezza sta attaccata alla macchina perché fra lei e la
macchina non ci va nulla di chiudibile; il defangatore sta lato impianto perché deve
poter essere pulito a macchina isolata.

**Il vantaggio più grande.** La sequenza **si legge e si approva a parole**, senza
disegnare niente. Separa *cos'è l'impianto* da *come viene disegnato*: se la fila è
sbagliata lo si vede subito, e non serve una tavola per accorgersene.

**Come è fatto oggi.** Costruito il 6 agosto 2026. Riordina **solo ciò che le regole hanno
aggiunto**: quello che il progettista ha scritto resta dove lo ha messo. Ogni accessorio
viaggia col proprio blocco — le valvole che lo isolano sono ancorate a lui e stanno una per
lato, e spostarlo lasciandole indietro le renderebbe due valvole che non chiudono niente.
Lavora **dentro** il ciclo di completamento e non in coda: rimettere in fila può scoprire un
attacco che era coperto solo perché un pezzo stava dove non doveva.

### Il modo intelligente di farlo: vincoli, non numeri di priorità

La tentazione è dare a ogni accessorio un numero d'ordine. Sarebbe di nuovo un ordine
arbitrario, come oggi lo è l'ordine alfabetico dei file. Invece **ogni pezzo dichiara il
perché della propria posizione**, e la fila la calcola il programma:

1. **Come si attacca.** *In linea* sul tubo (valvola, filtro, defangatore, contatore,
   pompa) oppure **su uno stacco**, con una propria piccola catena che pende dal tubo —
   ed è il caso di vaso di espansione, valvola di sicurezza, scarico, riempimento, sfiato
   e strumenti. **La catena è quindi un albero, non una lista.**
2. **I vincoli di vicinanza**, detti come ragioni e riferiti alle *funzioni* degli altri
   pezzi, mai ai loro nomi: «fra me e la macchina non ci va nulla di chiudibile» (valvola
   di sicurezza), «io sto lato impianto rispetto all'intercettazione» (defangatore, così
   si pulisce a macchina isolata), «io vengo prima di ciò che proteggo» (filtro).
3. **Il regime di intercettazione**: mi si isola normalmente; **non mi si isola mai** (la
   sicurezza); mi si isola **solo con valvola bloccabile** (il vaso di espansione).

Il programma fa un ordinamento su questi vincoli ed espande gli stacchi uno dentro
l'altro. **Se due vincoli si contraddicono, si ferma e dice quali due regole non possono
stare insieme** — invece di produrre in silenzio una fila sbagliata, che è esattamente
quello che succede oggi.

Il guadagno: la regola dell'intercettazione resta **una sola** e vale anche **sugli
accessori** che si dichiarano manutenibili; e i casi speciali che il PO ha segnalato non
sono eccezioni scritte dentro il programma, ma **proprietà dichiarate** dal pezzo.

**È finito quando** per ogni tubo di un impianto qualunque esiste una fila scritta, ogni
pezzo ci sta per una ragione dichiarata, gli stacchi hanno la propria catena, e la fila è
la stessa che scriverebbe a mano un termotecnico.

---

### Pezzo 3 — Comporre, eseguire, rivedere

Tre mestieri diversi, e la divisione serve a lavorare: **ogni difetto è o del motore o del
pianificatore, e va classificato** (`docs/ARCHITETTURA-DEL-PIANO.md` §3). Un difetto del
motore suona «ha fatto una cosa che nessuno gli ha chiesto» e si cura con codice migliore;
un difetto del pianificatore suona «il piano ha messo il pezzo dove non andava» e si cura
con **una regola in più**.

**3a — Il pianificatore compone.** Riceve il grafo definitivo, il foglio di regole
(`docs/regole-del-piano.md`) e le tavole di riferimento del disegnatore del PO
(`docs/input-pm/riferimenti-grafici/`). Produce un **piano di composizione**: quale
formato, e dove sta ogni pezzo posabile. È un file leggibile e correggibile a mano, e le
sue note dicono **quale regola** ha messo il pezzo lì.

**3b — Il motore esegue e misura.** È deterministico e **non cerca niente**: posa gli
accessori appesi, orienta i raccordi per deduzione, instrada in griglia, interrompe le
linee sotto i simboli, impagina, disegna e passa i rilievi. È la parte che la ricerca del
4 agosto dichiara sana — «regge la meccanica» — ed è quella che **resta**.

**3c — Il revisore rilegge e corregge.** Entra con la tavola, i rilievi del preflight, le
misure della geometria e il piano che ha prodotto quella tavola. Esce con **un piano
corretto**, e ogni spostamento porta **il nome della regola** che lo motiva. Si ferma
quando non resta nessun rilievo bloccante, quando un giro **non migliora**, o al tetto di
giri — e in tutti e tre i casi **dice perché si è fermato**.

**Che cosa costa, oggi.** Restano a costo le **curve** e gli **incroci**. Non costano più:
la **lunghezza** (D-139) e il **riempimento del foglio** (D-149), che si riportano come
misure. La vicinanza di un organo di servizio al pezzo che serve è un **vincolo**, non un
costo (D-145). I formati ordinari sono **A4, A3, A2, A1** (D-148, dichiarata momentanea dal
PO), e una tratta che non si instrada non uccide più la tavola: prende un ripiego
dichiarato, si marca `unresolved` e il preflight la nomina con un rilievo bloccante
(D-150).

**Il solutore è uscito.** `layout/improve.py`, la fase del tronco di `layout/spine.py` e
`layout/dilate.py` restano agli atti e non decidono più la posa. Il motivo non era la
taratura, era la forma della domanda: una somma pesata **non sa esprimere una gerarchia di
giudizio**, e nessun peso dice «un collettore è **una** linea dritta» — quella è una
figura, non un punteggio (D-151).

**È finito quando** il revisore gira su un impianto qualunque, ogni sua correzione porta il
nome della regola che la motiva, e l'anello si chiude senza rilievi bloccanti o dice perché
si è fermato.

---

### Pezzo 4 — La libreria dei simboli

**Cosa fa.** Contiene il disegno di ogni componente, la sua taglia in millimetri di carta,
**dove sono i suoi attacchi**, da che lato si può imboccare, e come può essere ruotato.

**Da dove vengono i simboli.** Dalla norma italiana UNI 9511 per tubi, giunzioni,
valvolame e strumenti; dalla pratica dei produttori per le macchine, che la norma non
copre. **Nessun simbolo inventato**: ognuno dichiara la propria fonte, e se la fonte non
c'è si chiede al PM invece di disegnare a naso (D-083).

**È finito quando** ogni simbolo usato è riconoscibile da un termotecnico italiano senza
guardare la legenda, dichiara la propria fonte, e mostra ciò per cui esiste (un bollitore
a serpentino deve *mostrare* il serpentino attaccato ai bocchelli).

---

### Pezzo 5 — Il cartiglio

**Cosa fa.** Il riquadro con committente, oggetto, tavola, scala, data, revisione e
firme, più la squadratura del foglio.

**Non va inventato: è un ingresso del progetto.** Il cartiglio aziendale Nove C è nel
repository dal primo giorno (`assets/cartigli/`). Finora ne abbiamo usato solo i margini
per misurare (D-091).

**È finito quando** la tavola esce con il cartiglio compilato coi dati che il progetto
possiede, la cornice chiusa sui quattro lati, e nessun campo obbligatorio vuoto su una
versione finale.

---

### Pezzo 6 — Verificare

Due livelli deterministici, e i loro rilievi sono l'ingresso del revisore:

1. **Controlli di correttezza** — nulla si sovrappone, niente esce dal foglio, i testi non
   si scontrano, ogni rimando ha il suo gemello. Bloccanti.
2. **Controllo di qualità (preflight)** — misura *come è disegnata*: curve, incroci,
   distanze, giri inutili, altezza dei testi, fonte dei simboli, tratte cedute (D-150).
   Bloccante o avviso. Il **riempimento del foglio** resta qui come **misura**, non come
   obiettivo (D-149). **Ogni misura va fatta dove la regola vive** — per attacco, per
   tratta, per simbolo — mai su un totale: contare non è guardare (D-088).

**Una regola è un controllo che sa nominare la propria violazione** (D-153). Se non si può
misurare, il revisore non la può usare e resta un'intenzione: è la differenza fra
«l'autostrada deve essere dritta» e «la tratta `s3` piega quattro volte, e su un'autostrada
le pieghe ammesse sono zero». Le righe di `docs/regole-del-piano.md` marcate `da scrivere`
sono i controlli che mancano, ed è lavoro aperto.

**Le regole misurate sono cinque** — A1, A4, B1, B3, B4 — e stanno in
`validation/regole.py`, con sigla e codice in **un posto solo**, `CODICE_DELLA_REGOLA`. Chi
ne aggiunge una entra da lì: **un controllo che non entra nel punteggio del revisore non è
un controllo**, ed è successo ad A4 per un giorno (`DRAW-015` §10ter).

⚠ **Un vincolo che vive solo nella posa del motore è un vincolo che il piano può rompere**
(**D-158**): da D-151 la posa non decide più dove stanno i pezzi. Chi scrive una regola di
posizione scrive **anche il rilievo sulla tavola finita**, non solo il vincolo.

**Il terzo livello non è più un cancello a valle: è il revisore** (pezzo 3c, D-114 attuata
da D-151), e il suo metro non è solo numerico — mette la nostra tavola accanto a quelle del
disegnatore del PO, perché è lì che sta la differenza che si vede a colpo d'occhio (D-153).

**È finito quando** la tavola passa i due livelli e il revisore non ha più una regola da
nominare. Il giudizio del prodotto resta del PO, sulle tavole (D-146).

---

## 3. Le tre regole di metodo che ci siamo dati, e che valgono per ogni pezzo

1. **Il controllo è uno: il PO guarda le tavole** (D-146, D-147). Il metodo dei tre ruoli
   dentro il DEV (D-083 — «uno decide, uno o più fanno, uno controlla») presupponeva più
   sessioni, e da D-147 la sessione è una sola: quel controllo incrociato non c'è più, e
   **non si fonde finché il PO non ha visto le tavole e detto di sì**. Se da un impianto di
   prova non esce nessuna tavola, quella è la **prima** cosa che si dice.
2. **Si verifica guardando, non contando.** Ogni modifica si chiude guardando l'immagine
   rigenerata, non solo la batteria di prove (D-088). E **se una tavola sembra sbagliata e
   i numeri dicono che va bene, si scrive**: è il rilievo più utile, ed è due volte su due
   il modo in cui i difetti veri sono stati trovati.
3. **Gli esempi del PO non sono l'elenco dei difetti.** Per ogni difetto segnalato si
   cercano tutti i suoi simili e si chiudono insieme (D-089).

---

## 4. Dove sta scritto cos'altro

| Domanda | Documento, e uno solo |
|---|---|
| **Chi decide cosa nel disegno** | **`docs/ARCHITETTURA-DEL-PIANO.md`** — vince su ogni contrasto |
| **Con quali regole si compone** | **`docs/regole-del-piano.md`** — aperto per dichiarazione del PO |
| Dove siamo adesso, in breve | `HANDOFF.md` |
| Cosa fa il prodotto e cosa non fa | `docs/prodotto/PRD_DISEGNATORE_MEP.md` |
| Cosa dichiara di sé un componente, e perché | `docs/prodotto/PROPRIETA_COMPONENTI.md` |
| **Dove va ciascun accessorio, e chi lo dice** | `docs/prodotto/DOVE_VA_CIASCUN_ACCESSORIO.md` |
| **Cosa l'interprete deve capire, e cosa chiede** | `skill/capire/COSA_DECIDE.md` |
| Come si prova l'interprete, e come si giudica | `skill/capire/CONSEGNA.md` |
| **Com'è fatta la skill** | **questo file** |
| Come si collabora, chi decide cosa | `AGENTS.md` |
| Come si disegna bene, regola per regola | `docs/standard/QUALITA_GRAFICA.md` |
| I numeri della carta: millimetri, spessori, testi | `docs/standard/GRAPHIC_STANDARD.md` |
| Perché abbiamo deciso una certa cosa | `docs/DECISION_LOG.md` |
| A che punto siamo e cosa manca | `PROJECT_STATE.md` |
| Cosa è stato rimandato, e perché | `docs/DEFERRED.md` |
| Da dove vengono simboli e prescrizioni | `docs/fonti/SOURCE_REGISTER.md` |
| Come giudicava l'occhio terzo, prima che diventasse il revisore (D-151) | `docs/standard/COLD_EYE_REVIEW.md` |

`docs/plans/` contiene il **piano corrente** e i verdetti dei collaudi, ma è un registro di
**esecuzione**: racconta come è andata, non cosa è vero adesso. Serve a sapere a che punto è
un pacchetto di lavoro, non a sapere come funziona la skill — per quello c'è questo file.
