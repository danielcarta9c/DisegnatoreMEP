# La posa a fasi: prima le autostrade — architettura, 11 settembre 2026

**Chi decide:** PO (Daniel Carta), dominio MEP e convenzioni di rappresentazione.
**Chi scrive:** PM-autore (`docs/governance/OPERATING_MODEL.md` §1.2.1).
**Input del PO:** **I-057**, **I-058**, **I-061**, **I-062**, **I-063**.
**Perché esiste:** il ciclo di posa attuale non sbaglia una taratura, sbaglia **l'ordine
delle decisioni**. Questo documento fissa l'ordine giusto prima che qualcuno lo tari di
nuovo.

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

## 3. La traduzione operativa

Tre fasi, ciascuna con un **invariante duro** che le fasi successive non possono
comprare. La funzione di costo resta, e ottimizza **dentro** ciascuna fase.

### Fase 1 — il tronco

Si posano le sole **macchine di spina** e si instrada la sola **autostrada**. L'obiettivo
della fase non è un costo: è una forma. **Ogni tratta del tronco è un rettilineo.**
Spostare una macchina costa zero, quindi la fase ha tutta la libertà che le serve.

Esito: una posa delle macchine di spina e un tronco dritto. Da qui in avanti la
rettilineità del tronco è un **vincolo**, non una voce di costo: nessun guadagno la compra.

### Fase 2 — il corredo

Valvole, filtri, raccordi, accessori in linea entrano **dentro** il tronco. Se non ci
stanno, il tronco **non si piega: si allunga.** Allontanare due macchine di spina lungo
l'asse è gratis e conserva la rettilineità; piegare il tronco per far posto a un organo è
vietato.

Esito: il tronco completo dei propri pezzi, ancora dritto.

### Fase 3 — le strade di servizio

Stacchi, diramazioni, adduzioni e accessori appesi si attaccano a un tronco **già fermo**.
Qui le curve si pagano — con i pesi della gerarchia — ma si accettano. Una strada di
servizio non piega mai un'autostrada per accorciarsi.

## 4. La precisazione che il PM porta, e che il PO conferma o corregge

**«Dritto» non può voler dire che tutto il tronco è una retta sola.**

Sulla tavola 2 la deviatrice manda la mandata in **due** posti — il puffer e il bollitore
— e i due rami non possono stare tutti e due sull'asse della pompa di calore. La lettura
che questo documento adotta, salvo diversa disposizione del PO:

- **ogni tratta del tronco è un rettilineo**;
- dove il tronco si biforca, **uno** dei due rami resta sull'asse principale e l'altro se
  ne stacca;
- resta sull'asse il ramo verso l'**accumulo maggiore**.

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
