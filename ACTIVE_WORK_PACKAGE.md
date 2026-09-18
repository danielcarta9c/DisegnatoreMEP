# DRAW-013 — La tavola si allarga tutta insieme, non tocca il bordo, e la distribuzione ha la sua forma

**Titolo:** La tavola si allarga tutta insieme, non tocca il bordo, e la distribuzione ha la sua forma
**Assegnato da:** PM (Claude — `OPERATING_MODEL.md` §1.2.1)
**Assegnato a:** DEV
**Data:** 2026-09-18
**Stato:** **ATTIVO.** Sostituisce `DRAW-012`, respinto con la PR #41 il 18 settembre. Il PO ha
dato il via libera il 18 settembre, chiedendo come lanciarlo; le quattro disposizioni che lo
motivano — **D-142, D-143, D-144, D-145** — sono sue e sono dello stesso giorno
**Release:** 0.3 — generalizzazione, revisione della tavola 2
**Ramo:** quello che la piattaforma assegna alla sessione. Il pacchetto **non ne prescrive uno**
**Commit di partenza:** il lavoro di `DRAW-012` **non va rifatto, va corretto**, e questo pacchetto
vive su `main`. Quindi, come **primo atto della sessione**, prima di leggere il codice:

```
git checkout -b <ramo-della-sessione> origin/main
git merge origin/claude/hopeful-ramanujan-9bs0cb     # la testa di DRAW-012, 17ff425
```

Il ramo porta così il codice di `DRAW-012` **e** le disposizioni correnti. Se il merge dà
conflitti, si risolvono tenendo il codice di `DRAW-012` e i documenti di `main`: i due insiemi
non si sovrappongono, salvo `ACTIVE_WORK_PACKAGE.md` e `PROJECT_STATE.md`, dove vince `main`.
**Il primo commit del ramo è quel merge**, da solo, così la revisione vede dove finisce
`DRAW-012` e dove comincia `DRAW-013`
**Fixture grafica principale:** impianto 1 e impianto 2; impianto 4 come misura

> **Leggere prima:** `docs/pm/2026-09-18-review-pr41-draw012.md` — il verdetto sulla PR #41, che
> dice che cosa di `DRAW-012` resta e che cosa si rifà. Poi **D-142**, **D-143**, **D-144** e **D-145**,
> le quattro disposizioni nuove del PO che sono l'intero motivo di questo pacchetto. D-144 ha uno schizzo
> del PO: `docs/input-pm/riferimenti-grafici/2026-09-18/`, e si legge molto meglio guardandolo.

---

## Contesto

`DRAW-012` ha fatto la cosa grossa e l'ha fatta bene: su tutt'e due le tavole la mandata e il
ritorno sono adesso **due rette che attraversano il foglio**, e l'accumulo, il circolatore e i
terminali stanno **sulla** mandata. È la figura che il PO descrive dal 10 settembre.

Poi ha comprato il riempimento nel modo sbagliato, e il PO l'ha bocciata:

> «Ha poco senso questo stretch fatto così per il gusto di riempire la tavola. Il Disegnatore
> non ha colto il senso. È stato tradotto in un criterio informatico sbagliato. Se devo rendere
> comoda la tavola allargo tutte le linee di un X per cento, non che allungo solo un tratto per
> prendere più spazio, è proprio brutto così. Era meglio prima.»
>
> «Non si mettono gli oggetti così vicini al bordo del foglio a meno che non ci sia un disegno
> molto molto pieno. Ma un disegno così comodo non si disegna dal bordo a bordo.»

**L'errore è del pacchetto, non del DEV.** `DRAW-012` chiedeva un numero dentro una finestra e
lasciava al motore la scelta di come farcelo entrare; il motore ha scelto la strada che non
costava, cioè allungare i tratti. Il numero è entrato e il disegno è peggiorato.

## Che cosa **non** si rifà

Si riparte dal ramo di `DRAW-012` e si tiene tutto questo, che il PM ha verificato e che resta
valido: la classificazione delle autostrade (§B), l'autostrada come oggetto intero e il suo
invariante (§C), la struttura in fase 1 (§A), la cessione graduale al posto del ripiego che
scarta le fasi (§F), il caso di prova 4 e la commutatrice (§G), il documento di architettura
aggiornato, e le quattordici prove nuove.

**La lunghezza resta fuori dalle voci di costo** (D-139), la finestra resta **45–65 %** (D-140),
la copertura dell'ingombro resta la guardia (D-141). Nessuna delle tre si tocca.

---

## A. La tavola comoda si ottiene dilatando tutto, non allungando un tratto (D-142)

1. Entra una mossa nuova: la **dilatazione proporzionale** della posa. Tutte le distanze fra i
   pezzi si moltiplicano per **lo stesso fattore**; i simboli restano della loro misura. Il
   disegno cresce **conservando la propria forma**: nessun pezzo si sposta rispetto agli altri,
   quindi la copertura dell'ingombro non può scendere e le curve e gli attraversamenti non
   possono aumentare.
2. Il fattore si sceglie **dopo** che il disegno è risolto, ed è **uno solo per foglio**: si
   cerca il più grande che tenga il disegno dentro il margine di §B, e che porti il riempimento
   dentro la finestra di D-140. Il risultato resta sulla griglia: se il fattore porta un pezzo
   fuori passo, si prende il fattore ammissibile più vicino, non si arrotonda pezzo per pezzo.
3. **Lo stretch del singolo tratto** (`DRAW-012` §E) **resta**, e resta ammesso soltanto per la
   ragione per cui il contratto lo ammetteva: **far entrare il corredo dove non ci sta**. Non è
   più uno strumento di riempimento, e il riempimento non deve poterlo comprare.
4. Se il disegno non ci sta nemmeno al fattore 1, la dilatazione non entra in gioco e il foglio
   resta quello: la dilatazione **non può** essere una contrazione.

## B. Il margine dal bordo, e non è fisso (D-143)

1. Fra l'inchiostro e il bordo dell'**area di disegno** (350 × 235 mm su A3, già al netto di
   cartiglio e legenda) c'è un **margine di rispetto**.
2. Il margine **parte da 25 mm per lato** e si stringe **fino a 10 mm** soltanto quando il
   disegno, a fattore 1, non ci starebbe altrimenti. Non si stringe per far salire il
   riempimento: si stringe solo per far entrare un disegno.
3. Il riempimento continua a misurarsi sui **350 × 235 mm**: il margine sta dentro quell'area,
   non in aggiunta.
4. Il preflight impara a segnalare il disegno che tocca il bordo senza esserne autorizzato.

## C. La forma della distribuzione: dritto, una curva, la dorsale, i terminali a pettine (D-144)

Il PO l'ha dettata come **best practice** — «si fa sempre così» — con uno schizzo a mano.

1. Dal **circolatore** esce un **tratto rettilineo**, e il ritorno rientra nell'accumulo con un
   tratto rettilineo. Questo pezzo è autostrada e **non si piega**: è ciò che `DRAW-012` §C
   proteggeva, e resta protetto.
2. La distribuzione può poi fare **una curva, e una sola**.
3. Dopo la curva c'è la **dorsale**: mandata e ritorno **affiancati e paralleli**, ciascuno
   rettilineo.
4. I **terminali si attaccano a pettine** sul fianco della dorsale, ciascuno con il proprio
   stacco corto di mandata e di ritorno, **impilati** uno sotto l'altro lungo la dorsale.

**Che cosa cambia rispetto a `DRAW-012`.** L'invariante della catena intera non si applica più
da un capo all'altro della strada verso i terminali: si applica **a tratti** — la gamba che esce
dal circolatore, e la dorsale — con **una curva dichiarata** fra le due. Quella curva **non è una
cessione** di §F e non si conta come tale: è la forma giusta, non un ripiego.

**E chiude il conflitto che `DRAW-012` aveva lasciato aperto.** Il DEV aveva dovuto togliere
l'asserzione «le due zone stanno sulla stessa colonna» perché D-060 e D-138 si contendevano la
stessa coordinata. Con D-144 non se la contendono più: i rami paralleli si impilano **perché si
appendono alla dorsale**. L'asserzione va **rimessa**, scritta su ciò che la dorsale garantisce.

## D. La tavola 4, e perché §B potrebbe chiuderla da sé

`DRAW-012` ha misurato cella per cella perché la tavola 4 non esce: il confine di rete del
prelievo sanitario viene posato a **x 365**, dieci millimetri oltre il bordo dell'area di
disegno, perché sta appeso alla macchina più a destra e «si posa addosso all'utente che serve».

**Ipotesi del PM, da misurare e non da credere:** con il margine di §B nessun pezzo può stare
oltre `x 325`, quindi un confine appeso al pezzo più a destra cade dentro la griglia e la tratta
si instrada. Se è così, la tavola 4 esce senza toccare `place.py`. Se non è così, il DEV misura
dove si ferma e **non amplia il perimetro**: `place.py` sarà un pacchetto a sé.

## E. La guardia del riempimento diventa il controllo della mossa

Il verdetto §5.1 ha misurato che la guardia di `DRAW-012` è una **soglia** (copertura sotto
0,75) e non il divieto che D-141 scrive: una posa che alza il riempimento e abbassa la copertura
da 0,80 a 0,70 **vince**. Con §A il problema si sposta: la dilatazione non può abbassare la
copertura. La guardia va quindi riscritta per quello che serve adesso — **verificare che il
riempimento sia salito per dilatazione e non per altro** — e la prova che la sorveglia deve
esercitare anche il caso lieve, non solo quello grosso.

## F. Le tre rosse di `DRAW-012`

Restano tre prove rosse in `test_stacchi_minimi_e_interasse.py`.

- **La terza** — lo stacco di 7,5 mm contro un minimo di 5,0 — **si chiude con §G**: non
  rimettendo la lunghezza nel costo, che D-139 vieta, ma facendo tornare la vicinanza come
  **vincolo** (D-145). Il DEV di `DRAW-012` l'aveva portata rossa invece di riscriverla, e aveva
  ragione.
- **Le altre due** non falliscono su un'asserzione: falliscono perché `compose_drawing` non
  consegna la tavola su due fixture che erano già fragili su `main`. `DRAW-012` §7.7 ha misurato
  sette strade e nessuna le chiude; la causa sta nel **posizionamento**, che qui resta fuori
  perimetro. Restano rosse, dichiarate, e **non si convertono in `skip` né in `xfail`**.

Il saldo di riferimento di questo pacchetto non è più quello di `main`: è **13 rosse, 1482
verdi, 24 saltate, 11 xfailed**, cioè la testa del ramo di partenza. Deve **migliorare di una**.

## G. Gli organi di servizio tornano addosso al pezzo che servono (D-145)

È la cura del difetto che ha fatto bocciare `DRAW-012` insieme al riempimento, e il PO l'ha
dettata come vincolo e non come costo.

1. Valvole di intercettazione e di sicurezza, scarichi, sfiati, manometri, vasi, gruppi di
   riempimento, filtri e **confini di rete** si posano **addosso al pezzo che servono**: lo
   stacco che li porta è **il proprio minimo su griglia**.
2. Lo stacco può allungarsi **solo per un vincolo dichiarato** — per esempio far posto a un
   altro accessorio in linea sulla stessa tratta — e mai per far salire un numero.
3. È un **vincolo del motore**, che nessuna voce di costo può comprare. **D-139 non si tocca**:
   i millimetri restano fuori dalle voci di costo, e la proprietà che quel costo teneva su torna
   nella forma giusta.
4. **La dilatazione di §A non lo viola**, perché scala tutto della stessa percentuale: uno stacco
   al minimo resta al minimo *in proporzione*. Se invece il vincolo va inteso in millimetri
   assoluti — cioè lo stacco non cresce mentre il resto cresce — **è una domanda al PM prima di
   scrivere codice**, non una scelta del DEV.
5. La ragione è **la leggibilità**: una valvola vicina al proprio oggetto dice a che serve; una
   valvola in mezzo a una linea, lontana da tutto, è equivoca.

**Questo chiude la terza rossa di §F**, quella che il DEV di `DRAW-012` aveva portato rossa
invece di riscriverla. Aveva ragione lui.

---

## Perimetro

**Dentro:** la dilatazione proporzionale e il fattore unico per foglio (§A); il margine variabile
dal bordo e il suo rilievo di preflight (§B); la forma della distribuzione — gamba dritta, una
curva, dorsale, terminali a pettine (§C); la misura sulla tavola 4 (§D); la guardia del
riempimento riscritta (§E); gli organi di servizio addosso al pezzo che servono (§G); il
pacchetto grafico prima/dopo.

**Fuori:** `place.py` e la posa dei pezzi appesi, salvo la misura di §D; lo spessore del tratto
per gerarchia (D-132); il verso di mandata e ritorno deciso dalla geometria (D-136); qualunque
decisione MEP che il PO non abbia dato.

## Criteri di accettazione

Ogni criterio si chiude con **il comando eseguito e il suo output**.

1. **Esiste la dilatazione proporzionale**, con un fattore unico per foglio, e una prova generale
   mostra che dopo la dilatazione **curve, attraversamenti e copertura dell'ingombro non
   cambiano** e tutte le distanze fra i pezzi sono cresciute della stessa percentuale.
2. **Il riempimento della tavola 1 e della tavola 2 entra nella finestra 45–65 % per
   dilatazione**, e il rapporto porta il fattore usato per ciascuna.
3. **Nessun tratto è più lungo del proprio minimo per ragioni di riempimento.** Sulla tavola 2,
   l'ingresso dell'acqua fredda torna vicino al bollitore che alimenta: il rapporto porta la
   distanza prima (140 mm sulla PR #41) e dopo.
4. **Nessun pezzo sta a meno di 25 mm dal bordo dell'area di disegno**, su nessuna tavola che ci
   sta; e se una non ci sta, il rapporto dice quale, di quanto si è stretta e perché.
5. **Il preflight segnala un disegno che tocca il bordo senza essere autorizzato**, e una prova
   lo mostra nei due versi.
6. **Le tavole 1 e 2 non peggiorano su curve e attraversamenti** rispetto al ramo di partenza:
   4/1 e 5/1. Un peggioramento va spiegato, e qui **non** è ammesso in bianco come lo era in
   `DRAW-012`: il metro non cambia più.
7. **La prova della guardia esercita anche il caso lieve** — riempimento che sale e copertura che
   scende di poco — e il caso lieve non deve vincere.
8. **La distribuzione ha la forma di D-144**, e una prova generale la pretende: gamba rettilinea
   dal circolatore, **una** curva, dorsale con mandata e ritorno affiancati, terminali a pettine
   con stacchi corti. La prova fallisce se la gamba si piega, se le curve sono due, o se un
   terminale si attacca fuori dalla dorsale.
9. **Sulla tavola 1 i radiatori e il pavimento radiante tornano impilati**, e l'asserzione che
   `DRAW-012` aveva tolto da `test_objective.py` è **rimessa**, scritta su ciò che la dorsale
   garantisce e non sull'abitudine della fixture.
10. **La curva della distribuzione non è una cessione**: il diario non la conta fra le catene
    cedute, e una prova lo mostra.
11. **La tavola 4 si misura.** Se esce, il rapporto porta la tavola e si chiude anche il criterio
    10 di `DRAW-012`. Se non esce, il rapporto dice dove si ferma, con il conto cella per cella.
12. **Gli organi di servizio stanno al proprio minimo**, e una prova generale fallisce se uno si
    allontana senza un vincolo dichiarato. Sulla tavola 2 il rapporto porta la distanza
    dell'ingresso dell'acqua fredda dal bollitore, prima e dopo.
13. **Il saldo della suite migliora di una** rispetto al ramo di partenza: **12 rosse** invece di
    13, perché §G chiude
    `test_stacchi_minimi_e_interasse.py::test_nella_posa_iniziale_ogni_stacco_e_lungo_il_proprio_minimo`.
    Le altre due restano, dichiarate. Nessuna prova convertita in `skip` o `xfail`, nessuna soglia allentata,
    nessuna fixture toccata per far passare una prova.
14. **Determinismo:** doppia generazione dalla CLI con la stessa impronta.
15. **Le tavole 1 e 2 sono misurate e riferite, prima e dopo**: curve, attraversamenti,
    riempimento, copertura, riempimento senza il pezzo più isolato, ingombro, margine minimo dal
    bordo, e la lunghezza come misura e non come giudizio.

## Consegna

Una PR sola verso `main`, non fusa, che contiene **tutto il lavoro dei due pacchetti**: il merge
di `DRAW-012` come primo commit e le correzioni di `DRAW-013` sopra. Rapporto in `docs/collaudi/DRAW-013/RAPPORTO.md`, pacchetto grafico
`prima/` e `dopo/` per le tavole 1, 2 e 4 — dove `prima/` è **il ramo di partenza**, non `main`.

**Prima di aprire la PR:**

1. **Guarda le tavole.** `DRAW-012` è stato bocciato da un occhio, non da un numero, e il DEV
   quel difetto l'aveva visto e scritto. Se una tavola ti sembra sbagliata e i numeri dicono che
   va bene, **scrivilo nel rapporto**: è il rilievo più utile che puoi portare, e questa volta
   è dimostrato.
2. **Misura i criteri di non-regressione prima, non dopo.** Qui sono il 6 e il 13.
3. **Se una disposizione del PO ammette due letture, fermati e chiedi al PM.**

## Decisioni che restano al PO

1. **Il pallino di derivazione con due spessori** (D-132): il PM propone che segua il tratto più
   grosso.
2. **L'ordine degli stacchi lungo il tronco** (rischio 17).
3. **Gli attacchi pari di un collettore**, ereditata da `DRAW-009`.

> Le due domande che `DRAW-012` lasciava aperte **sono chiuse**: il conflitto fra D-060 e D-138
> da **D-144** (§C lo attua), e la tightness degli stacchi da **D-145** (§G la attua). Nessuna
> delle due è più una domanda.
