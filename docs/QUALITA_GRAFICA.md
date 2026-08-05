# Le regole del colpo d'occhio

> Lo standard grafico **scritto** contro cui giudica l'agente terzo (§12.5 della specifica).
> Non è una norma. È quello che un disegnatore senior vede in due secondi, messo per iscritto
> perché una macchina possa vederlo anche lei.

---

## Perché esiste

Il PM, il 5 agosto 2026: *«qualunque disegnatore senior se ne accorge a colpo d'occhio che
questo è un disegno orrido. Basta confrontarlo con altri disegni per capire che non va bene.
Dobbiamo riuscire a tradurre quello che un occhio umano fa in automatico in delle regole.»*

Ha ragione, e la cosa scomoda va detta chiara: **queste regole erano già note.** Non è
mancata la conoscenza di come si fa una tavola tecnica — è mancato il momento in cui
qualcuno la confronta con quella conoscenza. Sapere non è controllare. I difetti che il PM
ha trovato a occhio in trenta secondi sono tutti nell'elenco qui sotto, e nessuno di loro
richiedeva una ricerca: richiedeva che questo elenco esistesse e che qualcuno lo scorresse
prima di consegnare.

Da qui discendono due cose:

1. **La carta si scrive una volta e vale sempre.** Non è un promemoria di sessione.
2. **L'agente terzo non è il custode di queste regole, è lo scopritore delle prossime.**
   Ciò che respinge due volte per lo stesso motivo diventa una misura deterministica
   (D-065). Un giudice che non lascia dietro regole fa ricominciare ogni tavola da zero,
   costa a ogni esecuzione e sbaglia in modo diverso ogni volta.

**Cosa non è.** Non è un manuale di progettazione (D-066) e non dice cosa mettere in un
impianto: dice come si disegna quello che l'ingegnere ha deciso. L'unica famiglia che parla
di contenuto è la E, ed è lì perché una tavola cui manca un pezzo è sbagliata anche se è
bellissima.

---

## Come si legge una regola

Ogni regola dice tre cose: **cosa vuole**, **come si vede a occhio**, e **a che punto siamo**.

| Stato | Significato |
|---|---|
| `per costruzione` | Il motore non può fare diversamente: la regola è dentro il modo in cui il disegno viene generato. |
| `da misurare` | È misurabile, ma il controllo non esiste ancora. Sono queste che riempiono il preflight grafico. |
| `giudizio` | Non si misura. La deve vedere l'agente terzo. |
| `difetto aperto` | Oggi la tavola la viola, il difetto è registrato e non ancora corretto. |

---

## A. Composizione — quello che si vede da due metri, prima di leggere

| # | La regola | Come si vede | Stato |
|---|---|---|---|
| A1 | Il foglio è pieno in modo uniforme. | Si copre metà foglio con una mano: se una metà è quasi bianca e l'altra è fitta, non va. | `da misurare` |
| A2 | Una seconda tavola esiste solo se porta contenuto vero (D-072). | La seconda tavola si guarda da sola: se sembra un ritaglio, doveva stare sulla prima. | `difetto aperto` |
| A3 | Il blocco disegnato è centrato e i quattro margini bianchi si somigliano. | Il disegno non è appoggiato a un bordo con il vuoto dall'altra parte. | `da misurare` |
| A4 | Si legge da sinistra a destra seguendo il processo: generazione, distribuzione, accumulo, utenze (D-060). | Si segue il flusso con il dito senza mai tornare indietro. | `per costruzione` |
| A5 | Ciò che sta insieme è vicino. | I pezzi dello stesso sottosistema formano un gruppo, non sono sparsi ai due capi del foglio. | `giudizio` |
| A6 | Disporre in fila non è una legge: si può impilare (D-073). | Due macchine alte e strette una sopra l'altra riempiono meglio di due in fila. | `difetto aperto` |
| A7 | Il peso grafico è distribuito. | Nessuna macchia nera di segni addensati accanto a una zona vuota. | `giudizio` |
| A8 | Se una piega si elimina spostando un oggetto, si sposta l'oggetto (D-078). | Muovere un pezzo sul foglio non costa niente; una piega in più si vede per sempre. | `difetto aperto` |
| A9 | La posizione dei componenti è una variabile, non un dato. | La disposizione è la prima ipotesi, non la risposta: le linee hanno diritto di farla cambiare. | `difetto aperto` |
| A10 | Spostare è gratis, spargere no (D-080). | Macchine allontanate per raddrizzare una linea, con dieci centimetri di tubo in più: si è pagato di più di quanto si è risparmiato. | `difetto aperto` |

## B. Linee — dove si perde o si vince una tavola

| # | La regola | Come si vede | Stato |
|---|---|---|---|
| B1 | Le tubazioni sono sempre ortogonali. Un segno obliquo non è mai un tubo. | Nessuna diagonale fra le linee di impianto. | `per costruzione` |
| B2 | Due linee non corrono mai sovrapposte per un tratto (D-062). | Una linea che «sparisce» dentro un'altra e riappare dopo. | `per costruzione` |
| B3 | Gli incroci sono pochi. | Si contano: su una centrale semplice devono stare sulle dita di una mano. | `da misurare` |
| B4 | Una linea cambia direzione solo per una ragione. | Sali-scendi, gomiti doppi, deviazioni che tornano da dove venivano. | `da misurare` |
| B5 | Le linee non sfiorano i simboli. | Un tratto che passa a filo di un riquadro sembra disegnato sopra il pezzo. | `per costruzione` |
| B6 | Le linee parallele corrono a distanza uguale e costante. | Due tubi affiancati a 4 mm qui e 9 mm là si notano subito. | `da misurare` |
| B7 | Nessuna linea finisce nel vuoto. | Ogni capo finisce su un componente o su un rimando dichiarato. | `per costruzione` |
| B8 | Gli spessori sono gerarchici: squadratura, tubazioni principali, ausiliari, richiami. | Se tutto ha lo stesso spessore la tavola è piatta e si legge male. | `da misurare` |
| B9 | Mandata e ritorno si distinguono sempre, e il verso segue il processo (D-057, D-059). | Il ritorno non entra mai dove deve entrare la mandata. | `per costruzione` |
| B10 | Il percorso è quello breve. | Un tubo che gira intorno al foglio per raggiungere la macchina accanto. | `da misurare` |
| B11 | L'ultimo tratto prima di un attacco è dritto e perpendicolare all'attacco. | Una linea che arriva di sbieco e piega proprio sul bocchello. | `da misurare` |
| B12 | Nessuna andata e ritorno per raggiungere un pezzo (D-078). | La linea supera l'oggetto, scende e torna indietro a prenderlo. Va spostato l'oggetto, non allungata la linea. | `difetto aperto` |
| B13 | Un incrocio fra linee che non si collegano porta il proprio scavallo (D-079). | Senza archetto, un incrocio e un raccordo a T hanno lo stesso segno e non si distinguono. | `difetto aperto` |
| B14 | Un attraversamento non si paga per una scelta di posizione. | Una linea che scende tagliando tutte le altre perché il suo pezzo è stato messo in alto. | `difetto aperto` |
| B15 | Un collegamento fra due linee porta il proprio pallino (UNI 9511, SRC-016). | Cerchio pieno di diametro quattro volte lo spessore del tratto, su derivazioni e incroci connessi. | `difetto aperto` |

## C. Simboli e allineamenti — quello che fa sembrare una tavola «fatta da un professionista»

| # | La regola | Come si vede | Stato |
|---|---|---|---|
| C1 | I componenti sulla stessa tratta hanno gli attacchi alla stessa quota (D-061). | Un disallineamento di due millimetri si vede a occhio nudo. | `per costruzione` |
| C2 | Componenti simili sono allineati fra loro. | Le macchine formano colonne e righe implicite, non una nuvola. | `da misurare` |
| C3 | Stesso componente, stesso simbolo, sempre. | Due valvole uguali disegnate in due modi diversi sulla stessa tavola. | `da misurare` |
| C4 | I simboli sono dritti; se ruotano, ruotano di 90°, e il testo dentro resta orizzontale. | Nessun simbolo storto, nessuna scritta da leggere girando la testa. | `per costruzione` |
| C5 | Le distanze fra i componenti sono regolari. | Spazi tutti diversi fanno sembrare la tavola improvvisata. | `da misurare` |
| C6 | Nessun simbolo tocca o copre un altro. | | `per costruzione` |
| C7 | La taglia del simbolo comunica il peso del componente. | Una valvola piccola, un accumulo grande. Tutti uguali non dicono niente. | `da misurare` |
| C8 | Ogni simbolo è quello che un termotecnico italiano si aspetta di vedere (D-081, D-082). | Se chi guarda deve chiedersi «e questo cos'è?», il simbolo è sbagliato anche se è bello. | `difetto aperto` |
| C9 | Un simbolo che porta un verso lo dichiara. | La valvola di ritegno ha la freccia del senso del flusso; senza, non si sa da che parte tiene. | `difetto aperto` |

## D. Testi — la famiglia dove si sbaglia più spesso

| # | La regola | Come si vede | Stato |
|---|---|---|---|
| D1 | L'etichetta è una scritta piccola accanto al proprio pezzo, e basta (D-075). | Il testo sta vicino a ciò che nomina: non serve seguire niente per capire a chi si riferisce. | `difetto aperto` |
| D2 | Se il testo non ci sta o dà fastidio, e solo allora, si allontana con un richiamo obliquo a 45°. | La diagonale si distingue al primo sguardo da una tubazione, che obliqua non è mai. | `difetto aperto` |
| D3 | Nessun richiamo ortogonale, nessuna riga di richiami a fondo tavola. | Quelle linee sottili ad angolo retto si leggono come altri tubi. | `difetto aperto` |
| D4 | Tutti i testi sono orizzontali e si leggono dal basso. | Niente scritte capovolte o verticali. | `da misurare` |
| D5 | Un testo non copre mai una linea né un simbolo. | | `per costruzione` |
| D6 | Stessa informazione, stesso corpo di testo. | Sigle tutte uguali fra loro, valori tutti uguali fra loro. | `da misurare` |
| D7 | Il testo non ripete la legenda (D-052). | Il nome del componente si scrive una volta sola, in legenda. | `per costruzione` |
| D8 | I testi sono pochi. | Ciò che può stare in legenda o in distinta non satura il disegno. | `giudizio` |

## E. Contenuto — quello che un impiantista si aspetta di trovare

| # | La regola | Come si vede | Stato |
|---|---|---|---|
| E1 | Ogni macchina ha una valvola di intercettazione su ogni attacco (D-074). | Si contano i tubi che entrano ed escono: tante valvole quante quelli. | `difetto aperto` |
| E2 | Ogni componente si può isolare senza svuotare l'impianto. | È il perché di E1: se per smontare un pezzo va svuotato tutto, manca qualcosa. | `difetto aperto` |
| E3 | Ogni circuito chiuso ha vaso di espansione, sicurezza, sfiato, scarico e riempimento. | Sono i pezzi che un termotecnico cerca per primi. | `per costruzione` |
| E4 | Niente è disegnato due volte, niente manca rispetto al modello approvato. | | `per costruzione` |
| E5 | Il contenuto lo decide l'impianto, mai lo spazio disponibile sul foglio. | Se non ci sta, si cambia disposizione o si divide (D-072): non si tolgono pezzi. | `difetto aperto` |

## F. Cornice, legenda, rimandi

| # | La regola | Come si vede | Stato |
|---|---|---|---|
| F1 | Il formato è ordinario: A3, oppure A4 se il disegno è davvero piccolo (D-058). | Mai strisce, mai formati fuori misura. | `per costruzione` |
| F2 | Il cartiglio è completo. | Committente, oggetto, tavola, scala, data, revisione. | `da misurare` |
| F3 | La legenda elenca tutti e soli i simboli presenti sulla tavola. | Una voce in legenda che sul disegno non c'è, o viceversa. | `per costruzione` |
| F4 | I rimandi fra tavole sono accoppiati e scritti in italiano (D-051). | A ogni «va alla tavola 2» corrisponde un «viene dalla tavola 1». | `per costruzione` |
| F5 | Nessun `DA DEFINIRE` in una versione finale. | | `da misurare` |

---

## Chi usa questa carta — e chi non deve usarla

**La usano** il preflight deterministico (le righe `da misurare` sono il suo programma di
lavoro) e il collaudo interno dei pacchetti di sviluppo.

**Non la usa l'occhio terzo** (D-086, per ordine diretto del PM). L'occhio terzo riceve
la tavola renderizzata a misura di stampa e la giudica **per confronto con l'esterno**:
le tavole professionali che conosce e quelle che può cercare in rete, sui siti dei
produttori. Non riceve questa carta né altri documenti interni, perché un giudice che usa
le nostre regole conferma i nostri errori sistematici: se una regola qui è sbagliata o
manca, solo un confronto esterno può accorgersene. Guarda prima da lontano — la
composizione — poi da vicino, e restituisce difetti puntuali e circostanziati, non un
voto. Quando respinge, cambia il **piano di impaginazione** e la pipeline rigenera da
capo: nessun agente tocca la geometria prodotta (D-064).

Ciò che l'occhio terzo rileva e questa carta non prevedeva **diventa una riga nuova**
(D-065): è così che la carta cresce senza diventare il proprio soffitto.

---

## Come cresce questa carta

Tre sorgenti, in ordine di autorità:

1. **Il PM.** Ogni difetto che segnala diventa una riga qui, con il perché. Le famiglie A, D
   ed E sono nate così.
2. **L'agente terzo.** Ciò che respinge due volte per lo stesso motivo diventa una regola
   scritta e, se misurabile, passa da `giudizio` a `da misurare` (D-065).
3. **Le tavole reali e i manuali di settore.** Servono a tarare i valori — quanto è «pieno»,
   quanto è «vicino» — non a scoprire le regole: quelle sono buona pratica consolidata e
   sono già note. Non si apre una ricerca per una regola che nessuno contesta (D-066).

Una regola aggiunta qui non è finita finché non ha uno stato. Se è `da misurare` e nessuno
la misura, la tavola può violarla e nessuno se ne accorge finché non la guarda il PM — che è
esattamente ciò che è successo.
