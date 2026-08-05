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
| — | — | — | — | — |
