# DRAW-013 — La tavola si allarga tutta insieme, e non tocca il bordo

**Titolo:** La tavola si allarga tutta insieme, e non tocca il bordo
**Assegnato da:** PM (Claude — `OPERATING_MODEL.md` §1.2.1)
**Assegnato a:** DEV
**Data:** 2026-09-18
**Stato:** **BOZZA — da approvare dal PO prima che il lavoro cominci.**
**Release:** 0.3 — generalizzazione, revisione della tavola 2
**Ramo:** quello che la piattaforma assegna alla sessione. Il pacchetto **non ne prescrive uno**
**Commit di partenza:** **`17ff425`, la testa del ramo di `DRAW-012`** (`claude/hopeful-ramanujan-9bs0cb`).
**Non** la testa di `main`: il lavoro di `DRAW-012` non va rifatto, va corretto
**Fixture grafica principale:** impianto 1 e impianto 2; impianto 4 come misura

> **Leggere prima:** `docs/pm/2026-09-18-review-pr41-draw012.md` — il verdetto sulla PR #41, che
> dice che cosa di `DRAW-012` resta e che cosa si rifà. Poi **D-142** e **D-143**, che sono le
> due disposizioni nuove del PO e sono l'intero motivo di questo pacchetto.

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

## C. La tavola 4, e perché §B potrebbe chiuderla da sé

`DRAW-012` ha misurato cella per cella perché la tavola 4 non esce: il confine di rete del
prelievo sanitario viene posato a **x 365**, dieci millimetri oltre il bordo dell'area di
disegno, perché sta appeso alla macchina più a destra e «si posa addosso all'utente che serve».

**Ipotesi del PM, da misurare e non da credere:** con il margine di §B nessun pezzo può stare
oltre `x 325`, quindi un confine appeso al pezzo più a destra cade dentro la griglia e la tratta
si instrada. Se è così, la tavola 4 esce senza toccare `place.py`. Se non è così, il DEV misura
dove si ferma e **non amplia il perimetro**: `place.py` sarà un pacchetto a sé.

## D. La guardia del riempimento diventa il controllo della mossa

Il verdetto §5.1 ha misurato che la guardia di `DRAW-012` è una **soglia** (copertura sotto
0,75) e non il divieto che D-141 scrive: una posa che alza il riempimento e abbassa la copertura
da 0,80 a 0,70 **vince**. Con §A il problema si sposta: la dilatazione non può abbassare la
copertura. La guardia va quindi riscritta per quello che serve adesso — **verificare che il
riempimento sia salito per dilatazione e non per altro** — e la prova che la sorveglia deve
esercitare anche il caso lieve, non solo quello grosso.

## E. Le tre rosse di `DRAW-012`

Restano tre prove rosse in `test_stacchi_minimi_e_interasse.py`. Una si chiude rimettendo la
lunghezza nel costo, e **non si chiude così**: D-139 non si tocca. Il DEV di `DRAW-012` ha fatto
bene a portarla rossa invece di riscriverla, e la domanda che ne nasce è al PO (§Decisioni).

**Finché il PO non risponde, le tre restano rosse e dichiarate.** Il saldo di riferimento di
questo pacchetto non è più quello di `main`: è **13 rosse, 1482 verdi, 24 saltate, 11 xfailed**,
cioè la testa del ramo di partenza. Non peggiora, e le tre non si convertono in `skip` né in
`xfail`.

---

## Perimetro

**Dentro:** la dilatazione proporzionale e il fattore unico per foglio (§A); il margine variabile
dal bordo e il suo rilievo di preflight (§B); la misura sulla tavola 4 (§C); la guardia del
riempimento riscritta (§D); il pacchetto grafico prima/dopo.

**Fuori:** `place.py` e la posa dei pezzi appesi, salvo la misura di §C; la tightness degli
stacchi come vincolo, finché il PO non risponde; lo spessore del tratto per gerarchia (D-132);
il verso di mandata e ritorno deciso dalla geometria (D-136); qualunque decisione MEP che il PO
non abbia dato.

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
8. **La tavola 4 si misura.** Se esce, il rapporto porta la tavola e si chiude anche il criterio
   10 di `DRAW-012`. Se non esce, il rapporto dice dove si ferma, con il conto cella per cella.
9. **Il saldo della suite non peggiora** rispetto al ramo di partenza (13 rosse, 1482 verdi, 24
   saltate, 11 xfailed). Nessuna prova convertita in `skip` o `xfail`, nessuna soglia allentata,
   nessuna fixture toccata per far passare una prova.
10. **Determinismo:** doppia generazione dalla CLI con la stessa impronta.
11. **Le tavole 1 e 2 sono misurate e riferite, prima e dopo**: curve, attraversamenti,
    riempimento, copertura, riempimento senza il pezzo più isolato, ingombro, margine minimo dal
    bordo, e la lunghezza come misura e non come giudizio.

## Consegna

Una PR sola, non fusa, **sopra il ramo di `DRAW-012`**, in modo che la PR contenga tutto il
lavoro dei due pacchetti. Rapporto in `docs/collaudi/DRAW-013/RAPPORTO.md`, pacchetto grafico
`prima/` e `dopo/` per le tavole 1, 2 e 4 — dove `prima/` è **il ramo di partenza**, non `main`.

**Prima di aprire la PR:**

1. **Guarda le tavole.** `DRAW-012` è stato bocciato da un occhio, non da un numero, e il DEV
   quel difetto l'aveva visto e scritto. Se una tavola ti sembra sbagliata e i numeri dicono che
   va bene, **scrivilo nel rapporto**: è il rilievo più utile che puoi portare, e questa volta
   è dimostrato.
2. **Misura i criteri di non-regressione prima, non dopo.** Qui sono il 6 e il 9.
3. **Se una disposizione del PO ammette due letture, fermati e chiedi al PM.**

## Decisioni che restano al PO

1. **Le due zone parallele e la strada di ritorno dritta** si contendono la stessa coordinata:
   D-060 dice che i rami paralleli si impilano, D-138 dice che la strada verso i terminali è
   struttura e la struttura è dritta. Non possono valere insieme.
2. **Che cosa tiene un attacco di servizio vicino al pezzo che serve**, ora che i millimetri non
   costano: si accetta, o la vicinanza torna come vincolo invece che come costo?
3. **Il pallino di derivazione con due spessori** (D-132): il PM propone che segua il tratto più
   grosso.
4. **L'ordine degli stacchi lungo il tronco** (rischio 17).
5. **Gli attacchi pari di un collettore**, ereditata da `DRAW-009`.
