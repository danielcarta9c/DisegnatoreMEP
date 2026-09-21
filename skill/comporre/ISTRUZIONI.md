# Comporre — dal grafo completo al piano

**Queste istruzioni bastano da sole.** Non serve leggere altro per fare il lavoro: tutto
quello che ti serve — il metodo, i numeri delle porte, il formato del file, i controlli — sta
qui. I rimandi ai documenti servono a chi vuole sapere **da dove viene** una regola, non a chi
deve applicarla.

---

## 1. Il lavoro, in tre righe

Ricevi il **grafo completo** di un impianto — tutti i pezzi e tutte le tubazioni fra loro — e
produci il **piano**: un file JSON che dice **dove sta ogni pezzo posabile sul foglio**, e
nient'altro.

Non disegni tu. Il piano lo esegue un motore deterministico che posa, orienta, instrada in
griglia, interrompe le linee sotto i simboli, impagina e misura. **Tu decidi una cosa sola —
dove stanno i pezzi — e quella cosa decide la tavola.**

> **Il metro non è il numero di pieghe.** È se la tavola **assomiglia al lavoro di un
> disegnatore**. Un criterio grafico, non matematico.

---

## 2. Il metodo, e viene prima di ogni regola

**Il disegno nasce dalle autostrade.** Lo ha detto il committente così:

> «Sposta le macchine in modo che le linee delle autostrade vengano con pochissime curve, poi
> attacchi il resto delle valvole piccole e strade secondarie. Ma **il disegno nasce dalle
> linee delle autostrade**. LE AUTOSTRADE CON POCHE CURVE e pochi sormonti.»

Un'**autostrada** è la tubazione grossa che unisce due macchine: la mandata dal generatore
all'accumulo, il ritorno dall'utenza al generatore, il tronco che attraversa la centrale.
**Per definizione ha poche curve e tratti rettilinei.** Le strade secondarie sono gli stacchi
verso valvole, strumenti, confini di rete.

### 2.1 La cosa che devi sapere prima di tutte: **la quota di un'autostrada non si sceglie**

È quella della **porta** della macchina che la genera. Le porte stanno a **millimetri fissi
dall'origine del pezzo**, e li trovi nel manifesto del simbolo (`assets/symbols/<id>.json`).
Questi sono quelli che incontri quasi sempre:

| pezzo | ingombro | porte, e a che quota dall'origine |
|---|---|---|
| `heat-pump-air-water` | 40 × 30 | `water_supply` **destra +5** · `water_return` **destra +20** |
| `gas-boiler` | 40 × 30 | `water_supply` **destra +5** · `water_return` **destra +20** |
| `buffer-four-port` | 25 × 45 | `primary_in` **sinistra +5** · `primary_out` **sinistra +20** · `secondary_out` **destra +5** · `secondary_in` **destra +20** |
| `buffer-two-port` | 25 × 45 | `a` sinistra +5 · `b` destra +5 |
| `plate-heat-exchanger` | 12,5 × 25 | `primary_in` **sinistra +5** · `primary_out` **sinistra +20** · `secondary_out` destra +5 · `secondary_in` destra +20 |
| `dhw-cylinder` | 25 × 45 | `coil_in` sinistra **+7,5** · `coil_out` sinistra **+17,5** · `dhw_out` sopra · `cold_in` sinistra +37,5 |
| `radiator`, `fan-coil`, `ahu-coil` | 20 × 15 | `in` **sinistra +7,5** · `out` **destra +7,5** |

**Guarda l'interasse.** Pompa di calore, caldaia, volano e scambiatore a piastre hanno tutti
le due porte principali a **15 mm** l'una dall'altra, e alle **stesse quote +5 e +20**. Questo
vuol dire una cosa sola, ed è la leva più potente che hai:

> ## Due macchine posate allo **stesso y** danno **due autostrade perfettamente rette**, gratis.

Pompa a `y=60` e volano a `y=60`: la mandata corre a 65 da una porta all'altra senza una
piega, il ritorno a 80. **Non hai speso niente.** Se invece le posi a `y=60` e `y=75`, ogni
linea fra loro fa **due pieghe** e te le porti dietro per tutta la tavola.

⚠ **Il bollitore ha l'interasse 10, non 15** — `coil_in` +7,5 e `coil_out` +17,5 — perché
quelle due porte dicono **dov'è la serpentina dentro l'accumulo**, e non si spostano. La
coppia che lo serve **cambia interasse per forza**: è vero, è noto, e non si cura.

⚠ **Un terminale ha le due porte alla stessa quota su facce opposte** — `in` a sinistra +7,5,
`out` a destra +7,5 — quindi è un **passante**: la mandata entra da sinistra, il ritorno esce
da destra e **deve tornare indietro**. Quel giro attorno al terminale non è un difetto della
tua posa, è la forma del pezzo. Quello che **puoi** fare è posarlo alla quota giusta, così che
il giro sia corto e su una sola piega per lato.

### 2.2 Il procedimento, in quest'ordine e non in un altro

1. **Leggi le porte delle macchine di spina** — generatori, accumuli, scambiatori, volani. La
   quota delle autostrade è già decisa da loro.
2. **Posa le macchine su quelle quote.** È la mossa che decide la tavola. Scegli **una fascia
   orizzontale per il primario** e mettici tutte le macchine che quel tronco attraversa, con
   lo **stesso y**.
3. **Chi sta in parallelo si impila**, uno sopra l'altro, e si unisce con **una verticale sola,
   corta, accanto alle macchine** — non in mezzo al foglio. Ogni macchina ci entra con uno
   **stacco orizzontale corto**.
4. **Tira le autostrade con gli occhi e guarda se sono rette**, prima di appendere qualunque
   cosa. Se una piega, torna al punto 2: **si sposta la macchina, non si accetta la piega**.
5. **Solo adesso** appendi valvole, strumenti, confini di rete e strade secondarie.

---

## 3. Cosa ricevi

Il **grafo completo** in JSON. Quello che ti serve:

- `components` — ogni pezzo con `id`, `definition_id` (che dice quale simbolo è), `tag`;
- `connections` — ogni tubazione, con le due estremità `{component_id, port_id}` e la rete;
- `networks` — a che circuito appartiene ogni tubazione, e con che fluido.

**Chi è una macchina e chi è corredo** lo capisci dall'ingombro e dalle porte: un pezzo 40×30
o 25×45 è una macchina, un pezzo di 5 o 7,5 mm con due porte in linea è un organo che sta
**sopra una tubazione**. Un `tee` è un raccordo: unisce tre tubazioni e **non si posa a
occhio**, si posa dove il collettore deve stare.

---

## 4. Il file che produci

JSON, e solo queste chiavi:

```json
{
  "formato": "A2",
  "note": [
    "Le due pompe impilate a x=35, y=60 e y=110: il collettore e' una verticale corta accanto a loro (A2, B3).",
    "Volano a y=60, sulla stessa quota della pompa maestra: mandata e ritorno rette, zero pieghe (D-159)."
  ],
  "pezzi": {
    "pdc-1":   {"x": 35,  "y": 60,  "regola": "D-159 — quota della porta"},
    "pdc-2":   {"x": 35,  "y": 110, "regola": "A2 — chi sta in parallelo si impila"},
    "volano":  {"x": 220, "y": 60,  "regola": "D-159 — stesso y della pompa: autostrade rette"},
    "deviatrice": {"x": 150, "y": 62.5, "rotazione": 0}
  }
}
```

- **`formato`** — uno fra `A4`, `A3`, `A2`, `A1`. Scegli il più piccolo in cui l'impianto ci
  sta comodo: un foglio grande mezzo vuoto è un difetto.
- **`pezzi`** — un'**entrata per ogni pezzo posabile** del grafo. `x` sono i millimetri dal
  bordo sinistro, `y` dal bordo alto, **origine in alto a sinistra del pezzo**. Si arrotondano
  al passo di griglia: **usa multipli di 2,5**.
- **`rotazione`** — **scrivila solo dove la deduzione non arriva**: una macchina con due o più
  attacchi che ha davvero una scelta, e il gruppo di riempimento. Per un raccordo o per un
  pezzo con un attacco solo **non scriverla**: la rotazione è una conseguenza della posa e il
  motore la deduce dai vicini che il pezzo ha davvero. Scriverla dove si deduce è un modo di
  sbagliarla.
- **`note`** e **`regola`** — **non sono decorazione.** Il piano senza di loro dice dove
  stanno i pezzi e non dice **perché**, e chi lo rivede non può correggerlo: può solo
  spostare. `note` porta la motivazione del piano intero, `regola` la stessa cosa pezzo per
  pezzo. **Ogni pezzo che hai spostato per una ragione porta quella ragione.**

Niente altre chiavi: il caricatore rifiuta quello che non riconosce, e te lo dice.

---

## 5. Le regole, nell'ordine in cui si applicano

Quando due si contendono lo stesso pezzo, **vince quella più in alto**, e la più in basso
cede. **Non si sommano mai**: una media pesata fra regole è il modo in cui questo progetto ha
già sbagliato una volta.

### A1 — Tre fasce verticali, da sinistra a destra
**Generazione** (pompe, caldaie) · **accumulo** (volani, bollitori, separatori) ·
**distribuzione e utenze** (collettori, valvole di zona, terminali). Il processo si legge da
sinistra a destra.

### A2 — Chi sta in parallelo si impila
Due pompe, tre pompe in cascata, due caldaie: **uno sopra l'altro, stessa x**, con un passo
verticale costante. Mai affiancate.

### A4 — Un organo di servizio sta **addosso** al pezzo che serve
Un confine di rete, un prelievo, uno scarico: **lì accanto, con un tratto di tubazione
corto**. Non «da qualche parte nella fascia giusta». È l'errore più comune di chi legge solo
A1: mette il confine ACS nella fascia della distribuzione e lo fa finire **a mezzo foglio di
distanza** dal bollitore che serve.

### B1 — Le autostrade dritte
Vedi §2. **Se una piega, si sposta la macchina.**

### B3 — Più macchine in parallelo ⇒ **collettore verticale**
I due raccordi che uniscono un parallelo stanno su **una verticale corta accanto alle
macchine**. Due collettori — mandata e ritorno — stanno su **due verticali diverse**, e
**quale delle due sta più vicina alle macchine conta**: mettici il **ritorno**.

⚠ **E guarda che le due verticali non si incrocino.** Se la mandata di una macchina deve
attraversare la verticale del ritorno per arrivare al proprio collettore, **hai messo i due
collettori nell'ordine sbagliato**: scambiali.

### B8 — Una linea non lascia la propria quota per poi tornarci
Il sali-scendi. Se un pezzo sta su un'autostrada, **posalo sulla quota dell'autostrada**, o la
linea scende a prenderlo e poi risale, portandosi dietro tutto quello che le sta appeso.

### B10 — Mandata sopra, ritorno sotto
Sulle orizzontali, sempre. È anche il motivo per cui le porte sono a +5 e +20 e non viceversa.

### B11 — Mandata e ritorno corrono **insieme**
«Corrono sempre insieme, non esiste che una va e l'altra va zig zag accanto.» Stesso interasse
per tutta la corsa. Se lo perdono, è perché le due macchine agli estremi hanno interassi
diversi — e allora o le allinei, o è il caso noto del bollitore (§2.1).

### D1 — Il disegno non arriva al bordo
### D3 — Il disegno non sta tutto da una parte
Un foglio con l'inchiostro tutto in una fascia e tre quarti vuoti **è un difetto**, e si vede
a occhio prima che lo dica un numero.

---

## 6. Quello che il piano **non può** dire, e come si aggira

**Il piano non può chiedere la forma di una spezzata.** Dice dove stanno i pezzi, e la forma
della linea la sceglie l'instradatore sul costo. «Scendi e fai una curva sola» **non si può
scrivere.**

**L'unica leva che hai è togliere di mezzo chi occupa la strada.** Prima di appendere un
organo, guarda **quale autostrada deve passare di lì**: se ci metti un gruppo di riempimento
nella colonna sotto l'uscita di una valvola, la linea gira intorno — non perché l'instradatore
sbagli, ma perché **non può passare**. È successo, e spostare quel gruppo di 20 mm ha portato
una linea da 3 pieghe a 1.

---

## 7. Cosa non è tuo, e non lo diventa

- **Non cambi il grafo.** Non aggiungi un pezzo, non ne togli uno, non cambi una tubazione. Se
  ti sembra che ne manchi uno, **lo scrivi come domanda dichiarata** e componi lo stesso.
- **Non inventi contenuto MEP.** Dove va la presa del ricircolo, se una valvola ci vuole: non
  è tuo.
- **Non cambi la convenzione grafica.** Colori, tratteggi, incroci, raggi degli spigoli: sono
  decisi, e non si toccano.
- **Non tari soglie e non inventi numeri.** Se ti viene voglia di scrivere «al massimo N
  colonne verticali», fermati: **quel numero non esiste**, e il criterio è grafico.

---

## 8. Il metodo di lavoro, passo per passo

1. **Leggi il grafo e separa** le macchine dal corredo. Disegna a mente lo **scheletro**: solo
   macchine e collettori.
2. **Trova le catene principali** — quali macchine sono unite a quali, e per quale rete. Quelle
   sono le autostrade.
3. **Scegli le quote.** Per ogni catena, guarda le porte delle macchine agli estremi: se hanno
   le stesse quote relative, **posale allo stesso y** e la catena è retta.
4. **Posa le macchine**, fascia per fascia, da sinistra a destra (A1). Impila i paralleli (A2).
5. **Metti i collettori**: una verticale corta accanto al parallelo, ritorno più vicino (B3).
6. **Ricontrolla lo scheletro**: ogni catena fra due macchine è retta? Se no, torna al 3.
7. **Solo adesso appendi il corredo**, guardando per ognuno **quale autostrada passa di lì**
   (§6), e tenendo i confini di rete **addosso** al pezzo che servono (A4).
8. **Scrivi le note.** Ogni scelta che hai fatto per una ragione porta il nome della regola.

---

## 9. Prima di consegnare: il controllo finale

Rispondi a queste, e se una risposta è «no» torna indietro:

- [ ] **Ogni pezzo posabile del grafo ha un'entrata in `pezzi`?** Uno che manca fa fallire
      tutto il piano.
- [ ] **Le `x` e le `y` sono multipli di 2,5?**
- [ ] **Le macchine unite da un'autostrada hanno lo stesso `y`?** Se no, hai una ragione
      scritta nelle note?
- [ ] **I paralleli sono impilati alla stessa `x`, con passo costante?**
- [ ] **I due collettori di un parallelo sono su due verticali vicine, con il ritorno più
      vicino alle macchine, e non si incrociano?**
- [ ] **Ogni confine di rete sta accanto al pezzo che serve?**
- [ ] **Nessun pezzo di corredo sta nella colonna o nella riga che un'autostrada deve
      percorrere?**
- [ ] **Il disegno occupa il foglio, o sta tutto in una fascia?**
- [ ] **`rotazione` compare solo dove serve davvero?**
- [ ] **Ogni pezzo spostato per una ragione porta la sua `regola`?**

E l'ultima, che vale più delle altre:

- [ ] **Guarda lo scheletro che hai composto e chiediti: assomiglia a una tavola disegnata da
      un disegnatore?** Se la risposta è no, il piano non è finito — anche se tutte le caselle
      sopra sono spuntate.
