# La posa a fasi: prima le autostrade — architettura, 11 settembre 2026

> ⛔ **Storia, non vigente, dal 20 settembre 2026** (**D-151**, **D-155**, **D-156**). La posa
> a fasi qui descritta era il modo in cui **il motore decideva dove stanno i pezzi**: la fase
> del tronco (`layout/spine.py`) e il ciclo di miglioramento su una funzione di costo
> (`layout/improve.py`), cioè **il solutore**. D-151 l'ha tolto dalla catena: dove stanno i
> pezzi lo scrive il **piano**, che compone un agente (`skill/comporre/`), e il motore lo
> esegue senza cercare niente (`piano/esecutore.py`). **Resta vigente l'idea dell'ordine** —
> prima le autostrade, poi il resto — che è passata nel metodo del pianificatore (**D-159**,
> in testa a `docs/regole-del-piano.md`). L'architettura vigente è
> `docs/ARCHITETTURA-DEL-PIANO.md`.

**Chi decide:** PO (Daniel Carta), dominio MEP e convenzioni di rappresentazione.
**Chi scrive:** PM-autore (`docs/governance/OPERATING_MODEL.md` §1.2.1).
**Input del PO:** **I-057**, **I-058**, **I-061**, **I-062**, **I-063**.
**Perché esiste:** il ciclo di posa attuale non sbaglia una taratura, sbaglia **l'ordine
delle decisioni**. Questo documento fissa l'ordine giusto prima che qualcuno lo tari di
nuovo.

> ### ⚠️ §3 è stato riscritto il 17 settembre 2026 — **D-138**
>
> L'ordine a tre fasi che questo documento fissò l'11 settembre teneva le **strade
> secondarie nell'ultima fase**, non contava i **circolatori**, eleggeva **un solo
> generatore** e, quando l'invariante non si poteva tenere, **buttava via la fase**. Il PO
> ha dettato l'ordine nuovo il 16 settembre (**D-138**), e `DRAW-012` lo ha attuato: §3 qui
> sotto è quello nuovo, e porta accanto ciò che ha sostituito.
>
> Restano validi e non toccati: §1 (il difetto), §2 (le parole del PO dell'11 settembre),
> §4 (che cosa vuol dire «dritto» — che `DRAW-012` §C precisa, aggiungendo l’invariante
> sulla **catena intera**), §5 e §6.
>
> Le cinque differenze fra l'ordine vecchio e quello nuovo sono misurate in
> `2026-09-16-come-ragiona-il-motore-e-come-dovrebbe.md`.

---

## 1. Il difetto, detto in una riga

**Oggi il costo può barattare tutto con tutto, e infatti lo fa.**

Il ciclo è un greedy globale su una funzione di costo lessicografica. Ogni proprietà del
disegno — la rettilineità del tronco, l'allineamento delle macchine, i rami paralleli
impilati — è una **voce di costo** che compete con le altre. Quindi ciascuna si compra e
si vende. La sessione dell'11 settembre 2026 lo ha mostrato tre volte in poche ore:

| Modifica | Tavola 1 | Tavola 2 |
|---|---|---|
| Peso della gerarchia (DRAW-007 §B) | zone impilate tornano verdi | allineamento PDC–puffer **trovato** |
| Tolto il pavimento invisibile | 10 pieghe → 6, tronco dritto, macchine allineate | allineamento **perso** |
| Gerarchia attraverso il multivia | invariata | la tavola **non esce piu'** |

Non è sfortuna e non è un tetto di ricerca: alzarlo da 1 500/2 000 a 6 000/6 000 non
cambia nulla. È che la struttura della tavola viene **trovata o mancata** a seconda di
dove il greedy parte, invece di essere **costruita**.

## 2. Cosa ha detto il PO

> «Il sistema di instradatura deve prima disegnare le autostrade e farle più dritte
> possibile, come ho fatto io a colori. Poi si mettono dentro tutte le altre valvole e
> pezzi, e se non ci stanno le autostrade le puoi allungare, stretchare, spostando le
> macchine principali — sempre però mantenendo le autostrade dritte. Poi ci attacchiamo le
> reti stradali di servizio, e quelle sì, accettiamo qualche curva in più. Comunque sempre
> vanno ottimizzate con la funzione costo.»

E prima, sulla stessa tavola:

> «La linea dalla PDC 1 al puffer viene interrotta dall'ingresso dell'AF, che sappiamo
> essere meno di una strada di servizio. Qui c'è proprio un epic fail. Prima devi
> disegnare le autostrade.»

## 3. La traduzione operativa — **riscritta il 17 settembre, D-138**

Tre fasi, ciascuna con un **invariante duro** che le fasi successive non possono
comprare. La funzione di costo resta, e ottimizza **dentro** ciascuna fase.

### Fase 1 — **la struttura** (era: il tronco)

Si posano i **pezzi principali** e si tracciano **le autostrade e le strade secondarie,
insieme**.

**Che cosa è autostrada** (D-138, e `DRAW-012` §B):

1. dai **generatori** agli **accumuli** e agli **scambiatori**, passando per le valvole a
   tre vie e i **collettori che mettono insieme i generatori**: un collettore o una tre vie
   in mezzo non interrompe l'autostrada e non la declassa;
2. **sempre**, le linee che dagli **accumuli, puffer e scambiatori** vanno ai
   **circolatori** e da lì alla distribuzione;
3. con **più generatori**, le autostrade sono **più d'una**: non c'è un generatore eletto,
   ciascuno ha la propria fino al punto in cui confluiscono.

**Strade secondarie della stessa fase:** l'**uscita ACS** e la **distribuzione verso i
terminali**. Restano alla fase del corredo gli stacchi di servizio — ingresso AF, valvole
jolly, vasi di espansione.

**Che cosa costa in questa fase:** le **curve**, e in secondo luogo gli
**attraversamenti**. **La lunghezza no** (D-139): non è un parametro con cui si giudica un
disegno. Ci si tiene larghi e si occupa più foglio anche se non serve; il riempimento è una
**finestra**, 45–65 % dell'area di disegno (D-140), letta sempre insieme alla copertura
dell'ingombro (D-141).

L'obiettivo della fase non è un costo: è una forma. **L'autostrada intera — da un capo
all'altro, attraverso i propri crocevia — è una retta** (`DRAW-012` §C). Non ogni suo
frammento: la catena. Un frammento di cinque millimetri fra due raccordi è dritto sempre, e
verificare l'invariante su di lui è verificare niente — è il difetto per cui la tavola 4
usciva storta con tutti i numeri verdi.

Esito: una posa dei pezzi principali e una struttura dritta. Da qui in avanti la
rettilineità è un **vincolo**, non una voce di costo: nessun guadagno la compra.

> **Che cosa diceva la versione dell'11 settembre.** «Si posano le sole macchine di spina e
> si instrada la sola autostrada. Ogni tratta del tronco è un rettilineo.» Le strade
> secondarie finivano in fase 3, il circolatore non faceva nemmeno tratta, un solo
> generatore stava sulla spina, e l'invariante era su ogni tratta invece che sulla catena.

### Fase 2 — il corredo

Valvole, componenti piccoli e **strade di servizio** entrano su una struttura **già ferma**.
Se non ci stanno, il tronco **non si piega: si allunga**, e si trasla. Allontanare due
macchine di spina lungo l'asse è gratis e conserva la rettilineità; piegare il tronco per
far posto a un organo è vietato.

Esito: la struttura completa del proprio corredo, ancora dritta.

### Fase 3 — **l'ultima spiaggia** (era: le strade di servizio)

Se proprio non c'è spazio si concede **una curva sull'autostrada**, e si tiene la
struttura. La cessione è **graduale e dichiarata**: una piega per volta, sulla catena che
ne ha meno bisogno, e il rapporto dice dove e perché.

> **Che cosa diceva la versione dell'11 settembre.** Qui stavano gli stacchi, le
> diramazioni e gli accessori appesi, che adesso entrano in fase 2 con il resto del
> corredo. E non c'era nessuna cessione graduale: quando la fase non si instradava, il
> motore **la buttava via** e ripiegava sulla tavola che produceva prima che le autostrade
> esistessero. L'impianto 4 usciva da lì.

## 4. La precisazione che il PM porta, e che il PO conferma o corregge

**«Dritto» non può voler dire che tutto il tronco è una retta sola.**

Sulla tavola 2 la deviatrice manda la mandata in **due** posti — il puffer e il bollitore
— e i due rami non possono stare tutti e due sull'asse della pompa di calore. La lettura
che questo documento adotta, salvo diversa disposizione del PO:

- **ogni tratta del tronco è un rettilineo**;
- dove il tronco si biforca, **uno** dei due rami resta sull'asse principale e l'altro se
  ne stacca;
- resta sull'asse il ramo verso l'**accumulo maggiore**.

**Precisato il 17 settembre da `DRAW-012` §C, in due punti.**

1. **«Ogni tratta è un rettilineo» non basta, e da solo non dice niente.** Una tratta del
   modello finisce su ogni raccordo e su ogni multivia: sull'impianto 4 erano dieci
   tronconi lunghi cinque o dieci millimetri, e un frammento di cinque millimetri è dritto
   sempre. Ciò che si conserva è **l'autostrada intera** — la catena di tratte che si
   susseguono attraverso i propri crocevia, da una macchina all'altra — e l'invariante si
   verifica su di lei: la catena è una retta, né cambia direzione né cambia quota sul
   raccordo che unisce due sue tratte.
2. **«Il ramo verso l'accumulo maggiore» sono due parole, e vengono in quest'ordine.**
   Prima **accumulo** — chi il fluido lo riceve: accumuli, puffer, separatori, scambiatori
   e collettori — e poi **maggiore**, che è l'ingombro dichiarato dal simbolo. Finché un
   solo generatore stava sulla spina non c'era niente da scegliere; con tutti i generatori
   sulla spina (D-138) un collettore che unisce due pompe di calore vede due rami di
   autostrada, e guardando il solo ingombro vinceva la **seconda pompa** (1200 mm²) contro
   l'accumulo (1125 mm²): l'asse andava da un generatore all'altro e l'accumulo si
   staccava di lato.

## 5. Cosa questo cambia nel codice, in prima ipotesi

Non è il pacchetto: è il perimetro che il pacchetto dovrà confermare o smentire.

- **`place_sheet` si spezza in due**: una posa delle sole macchine di spina, e una posa
  del resto che parte da quella. Oggi posa tutto insieme.
- **`Improver.run` diventa a fasi**, con `is_valid` che nega ciò che rompe l'invariante
  della fase precedente — è già il posto dove stanno «i vincoli che nessun guadagno
  compra».
- **Lo stretch è una mossa nuova**: allontanare due macchine di spina lungo l'asse del
  tronco, portandosi dietro ciò che sta in mezzo. Oggi non esiste; le mosse muovono pezzi,
  non allungano tratte.
- **`hierarchy.py` resta la sorgente unica** di chi è tronco e chi no. È già scritta e
  provata (DRAW-007 §A).

## 6. Cosa resta fuori, e va detto

- **I-061, gli ingressi ripetuti dell'AF.** Finché l'acqua fredda attraversa il foglio con
  una linea sola, qualunque tronco prima o poi la incrocia. È l'altra metà del problema
  che il PO ha visto, e tocca disegno, nomenclatura e instradamento insieme.
- **I-059, lo spessore del tratto per gerarchia.** Rendering, dopo.
- **Il quarto caso di D-120** e la misura «stacchi statici», dalla retrospettiva del
  10 settembre.
