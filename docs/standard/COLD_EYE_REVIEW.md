# Cold eye review — protocollo dell'agente terzo

> Il giudice della tavola prima della consegna (D-063 livello 2, D-077, D-086).
> Questo file descrive **come si esegue** la revisione. Il prompt che l'agente riceve è
> in `docs/prompts/cold-eye-review.md` ed è deliberatamente povero: più contesto gli si
> dà, meno terzo è.

---

## 1. Perché deve essere terzo, e cosa vuol dire

Il PM, il 5 agosto 2026:

> «Continua a lavorare finché un agente terzo che opera come se fosse un disegnatore
> senior MEP lo approverebbe. **Deve essere un terzo**, un cold eye review. L'agente terzo
> non deve applicare i meccanismi e i ragionamenti delle regole qui scritte: deve
> controllare quell'elaborato e confrontarlo a livello qualitativo con quelli che ha in
> memoria o che può trovare facendo scraping su internet, su siti di produttori.»

Ne discendono tre vincoli, tutti verificabili:

1. **Contesto separato.** L'agente non ha visto costruire la tavola, non conosce il
   modello, non conosce i piani. Un agente che rilegge il proprio lavoro lo approva.
2. **Non riceve le nostre regole.** Niente `QUALITA_GRAFICA.md`, niente decision log,
   niente specifiche. Un giudice che usa le nostre regole conferma i nostri errori
   sistematici: se una regola è sbagliata o manca, solo un confronto esterno se ne
   accorge (D-086).
3. **Giudica per confronto con l'esterno.** Le tavole che conosce e quelle che trova in
   rete — schemi di produttori, tavole di progetto pubbliche. Il metro è «questa
   sembra una tavola fatta da uno studio serio?», non «rispetta il documento X».

---

## 2. Cosa riceve

| Riceve | Non riceve |
|---|---|
| L'immagine della tavola, renderizzata a misura di stampa | Il modello di progetto |
| Il formato dichiarato (A3, scala grafica sul foglio) | I documenti di progetto, in particolare la carta del colpo d'occhio |
| Una riga di contesto: che impianto è, e a che scopo serve la tavola | I rapporti dei controlli automatici |
| La possibilità di cercare in rete tavole di confronto | Il verdetto precedente, alla prima passata |

Il raster si produce con `scripts/rasterize.sh tavola.svg tavola.png` — strumento di
sessione, fuori dal nucleo deterministico.

---

## 3. Come giudica

1. **Da lontano, senza leggere.** Solo la composizione: il foglio è pieno in modo
   uniforme? c'è un ordine di lettura? qualcosa salta all'occhio come sbagliato?
   Se la composizione non regge, la tavola torna indietro **subito**, senza esaminare il
   resto: rifare la composizione cambia tutto ciò che sta sotto.
2. **Da vicino.** Linee, simboli, testi, contenuto, cornice.
3. **A confronto.** Mette la tavola accanto a due o tre schemi funzionali reali —
   dalla propria memoria o cercati in rete — e dice **in che cosa la nostra è diversa**.
   È il passaggio che il PM ha chiesto e quello che nessun controllo interno può fare.
4. **Verdetto.** `APPROVATA` oppure `RESPINTA`, con i rilievi.

**Un rilievo utile** dice tre cose: cosa si vede, dove, e perché è sbagliato in una tavola
tecnica. «Non mi piace» non è un rilievo. «Le linee di richiamo dei testi hanno lo stesso
aspetto delle tubazioni e si leggono come tubi» lo è.

---

## 4. Cosa succede quando respinge

Il ciclo cambia **gli ingressi**, mai il disegno (D-064):

    rilievi dell'agente terzo
       -> nuovo piano di impaginazione, o correzione a monte (regole, simboli, layout)
       -> la catena deterministica rigenera da capo
       -> controlli automatici + preflight
       -> nuova passata di cold eye review

Vincoli del ciclo:

- **massimo tre passate**, poi la tavola va al PM con i rilievi residui dichiarati;
- **monotono**: una passata si accetta solo se le misure del preflight non peggiorano;
- **nessun agente tocca la geometria prodotta**: stesso modello e stesso piano danno lo
  stesso identico file, e questa proprietà non è negoziabile;
- **ciò che viene respinto due volte per lo stesso motivo diventa una regola scritta** e,
  se misurabile, una soglia del preflight (D-065). È il modo in cui la carta del colpo
  d'occhio cresce senza diventare il proprio soffitto.

---

## 5. Registro delle passate

Ogni passata si registra qui: data, verdetto, rilievi, e cosa è stato cambiato a monte.
Il registro è la prova che il ciclo è avvenuto davvero e la fonte da cui si ricavano le
nuove regole.

| # | Data | Verdetto | Rilievi principali | Cosa è stato cambiato |
|---|---|---|---|---|
| 1 | 2026-08-05 | **RESPINTA** | 14 rilievi, di cui 3 bloccanti di composizione e 6 **errori funzionali veri**. Elenco integrale sotto | da fare |

---

## Passata 1 — 5 agosto 2026, RESPINTA

L'agente ha ricevuto solo l'immagine. Ha misurato la tavola sui pixel e l'ha confrontata
con **tre riferimenti**, due dei quali tavole vere di progetto pubblico: schema ACS
dell'Agenzia del Demanio (PE-IM-13, Reggio Calabria 2018), centrale termica del Comune di
Carrara (PD.IM.03.00), e gli schemi Caleffi per pompa di calore aria-acqua.

Prima impressione, sua: *«una striscia di disegno che galleggia nel terzo centrale di un
A3, con metà foglio bianco sotto. La scritta più grande di tutta la tavola è "BOZZA —
cartiglio non compilato". Il foglio non è composto: è un disegno appoggiato su una
cornice, e per giunta la cornice non chiude.»*

### Bloccanti di composizione

| # | Rilievo | Misura sua | Nostro stato |
|---|---|---|---|
| 1 | **Metà foglio vuoto.** Due fasce a inchiostro 0,00 %; il contenuto usa il 48 % dell'altezza e il 99,7 % della larghezza | fasce y 231÷533 e y 1439÷1890 vuote | il preflight lo dice già (`SHEET_BARELY_FILLED`, 39 %). **Nessuno lo corregge**: manca lo sviluppo verticale della composizione |
| 2 | **Cartiglio inesistente e cornice aperta in basso**; margini 10 mm sui quattro lati, manca la rilegatura da 20 mm | 177 px di montanti senza bordo inferiore | il cartiglio è P5, non ancora fatto. **La cornice aperta è un difetto nostro, nuovo** |
| 3 | **Testi a metà dell'altezza minima di norma**: 1,19 mm contro i 2,5 mm di UNI EN ISO 3098. Gerarchia invertita: la legenda pesa quanto il titolo, le sigle sono il testo più piccolo | misurato a 7,56 px/mm | **difetto nostro, nuovo.** `text_small_mm` vale 1,8 e va portato a 2,5 |

### Errori funzionali — nessuno di questi era noto

| # | Rilievo | Perché è grave |
|---|---|---|
| 4 | **Gli incroci si leggono come giunzioni.** La linea scavalcata passa dentro l'arco e lo taglia; su un nodo c'è pure una freccia di flusso piena | Un incrocio ambiguo fra **mandata e ritorno del generatore** letto alla lettera è un bypass che cortocircuita l'impianto. Il nostro scavallo interrompe la linea che scavalca ma **non** quella scavalcata |
| 5 | **La miscelatrice ACS non ha l'acqua fredda**: due sole vie, nessuna derivazione da AF | Una miscelatrice a due vie non miscela niente: la protezione antiscottatura non c'è |
| 6 | **Gruppo di riempimento in serie sul ritorno**, attraversato da tutta la portata e collegato a nessuna sorgente | Il riempimento è una derivazione dalla rete, non un organo di passaggio |
| 7 | **Zone senza regolazione**: radiatori e pavimento sulla stessa mandata, senza miscelazione, valvole di zona, circolatori né collettore di ritorno | Radiatori e pannello alla stessa temperatura non è un'opzione, è un errore |
| 8 | **Stesso simbolo per due componenti**: `FIL-01` etichetta il triangolo che la legenda chiama «confine di rete»; il filtro a Y vero è altrove senza sigla. E due valvole identiche in serie senza niente in mezzo, due volte | La legenda è un contratto: se un segno vale due cose la legenda non serve più |
| 9 | **Serpentino staccato dai bocchelli, volano vuoto** e diverso dal simbolo che la legenda gli assegna | Dal disegno non si deduce né che il bollitore sia a serpentino né che il volano abbia quattro attacchi: sono le due informazioni per cui quella parte esiste |

### Coerenza e dati

| # | Rilievo |
|---|---|
| 10 | **`200 l` galleggia sopra il bollitore siglato `300 l`.** Il volano non ha volume. Il circolatore è `CIR-02` e `CIR-01` non esiste. Siglate 2 valvole su 11 |
| 11 | **La legenda non corrisponde al disegno**: dichiara due ricircoli che non esistono; la linea AF è tracciata col colore che la legenda assegna al ritorno; ~40 % di ogni tubazione è disegnata nera perché i monconi dei simboli non prendono il colore del servizio |
| 12 | **Legenda composta male**: volano e bollitore **si sovrappongono fisicamente**, passi irregolari, scale incoerenti, nessuna intestazione, box mezzo disegnato |
| 13 | **Gerarchia dei tratti invertita**: la linea di terra (4 px) pesa più della cornice (3 px) e tocca il bordo. Frecce di flusso grandi come i simboli di valvola, tre triangoli diversi a pochi millimetri |
| 14 | **Nessun dato tecnico**: niente potenze, temperature di progetto (diverse per radiatori e pavimento!), diametri, prevalenza, tarature, note, regolazione, scarichi delle sicurezze, separazione esterno/interno |

### La differenza che riassume tutto, parole sue

> «Il punto non è che i riferimenti siano più ricchi: è che sono **documenti**, mentre
> questo è un disegno. Nelle tavole vere ogni segno grafico è agganciato a un dato numerico
> e a una responsabilità firmata; qui il segno grafico è tutto quello che c'è.»
