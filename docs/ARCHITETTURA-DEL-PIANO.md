# L'architettura del piano — come si disegna, da D-151

**Data:** 20 settembre 2026 · **Stato:** vigente, sostituisce l'architettura del solutore

> Il documento da leggere prima di toccare il disegno. Dice **chi decide cosa**, e la
> divisione che ne esce è anche il modo in cui si legge ogni difetto.

---

## 1. La catena, in tre pezzi

```
    IL PIANIFICATORE          IL MOTORE                 IL REVISORE
    compone                   esegue e misura           rilegge e ricompone
    (agente, con le regole)   (deterministico)          (agente, con i rilievi)
         │                          │                         │
         │   piano di composizione  │      rilievi            │
         └─────────────────────────>└────────────────────────>┘
                                                              │
                             ◀────────────────────────────────┘
                                   piano corretto
```

**Il pianificatore** dice **dove stanno i pezzi**. Nient'altro: non coordinate di linee,
non simboli, non scelte MEP. Riceve il grafo, il foglio di regole e le tavole di
riferimento; produce un **piano di composizione**, che è un file leggibile e correggibile
a mano.

**Il motore** esegue il piano e lo **misura**. È deterministico e non cerca niente: posa
gli accessori appesi, orienta i raccordi, instrada in griglia, interrompe le linee sotto i
simboli, impagina, disegna, e passa i rilievi. È la parte che la ricerca del 4 agosto
dichiara sana (§3: «regge la meccanica»), ed è quella che **resta**.

**Il revisore** legge i rilievi, **guarda la tavola** e **corregge il piano**. È D-114,
scritta il 9 agosto e mai costruita: «il validatore AI smette di essere un cancello a valle e
diventa supervisore in anello chiuso». L'anello si chiude quando non resta nessun rilievo
bloccante — o quando un giro non migliora, e allora lo dice.

**Si costruisce subito** (D-153, PO): non è il premio a valle, è **l'attrezzo con cui si
scrivono le regole**, una tavola alla volta. E il suo metro non è solo numerico: mette la
nostra tavola accanto a quelle del disegnatore del PO
(`docs/input-pm/riferimenti-grafici/`), perché è lì che sta la differenza che si vede a colpo
d'occhio.

## 2. Che cosa è morto, e perché

**Il solutore.** `improve.py` e la fase del tronco cercavano il disegno minimizzando una
somma pesata — curve, attraversamenti, lunghezza, riempimento, copertura, squilibrio,
margine. Sette manopole.

Il difetto non era la taratura, era la forma della domanda. Una somma pesata **non sa
esprimere una gerarchia di giudizio**: il PO, il 20 settembre, guardando l'autostrada che
si piegava mentre gli stacchetti restavano dritti —

> «Abbiamo ottimizzato le curve e gli attraversamenti sugli attacchetti e abbiamo fatto sta
> curva senza senso.»

Una piega dell'autostrada e una piega di uno stacco pesavano quasi uguale, e una somma si
compra sempre. E nessun peso dice «un collettore è **una** linea dritta»: quella è una
figura, non un punteggio.

## 3. La divisione che serve a lavorare

**Ogni difetto è o del motore o del pianificatore, e va classificato.** È il guadagno più
grande dell'architettura nuova: prima ogni difetto era «la funzione di costo» e non si
sapeva dove mettere le mani.

| | difetto del **motore** | difetto del **pianificatore** |
|---|---|---|
| **suona così** | «il motore ha fatto una cosa che nessuno gli ha chiesto» | «il piano ha messo il pezzo dove non andava» |
| **si cura con** | codice migliore | una regola in più |
| **esempi del 20 settembre** | la mappa delle porte rimappata anche sulle macchine (l'acqua fredda finiva su `primary_out`); la spezzata di ripiego che tornava su sé stessa; `may_stack` irraggiungibile perché contava i raccordi fra i vicini; la fase del tronco che sovrapponeva due pompe | una tratta con più accessori in linea vuole il proprio rettilineo; un pezzo va preso dal lato delle sue porte; due linee fra gli stessi due raccordi vanno separate in quota |

Le due code si lavorano **in parallelo** e non si contendono niente.

## 4. Il piano di composizione

Oggi è `docs/collaudi/PROVA-PIANO/impianto-*.json`, eseguito da `scripts/piano.py`. Dice
**dove** sta ogni pezzo posabile, e nient'altro:

```json
{ "formato": "A2",
  "pezzi": { "pdc-1": {"x": 35, "y": 60}, "volano": {"x": 300, "y": 160} } }
```

**Che cosa il piano non deve contenere, perché si deduce.** Ogni pezzo si gira verso i
vicini che ha davvero: un prodotto scalare, nessun peso. La deduzione vale per chi **non ha
scelta** — un attacco solo (sfiato, scarico, vaso, manometro) o un raccordo, che è un punto
sulla tubazione. Una macchina con due o più attacchi **ha** una scelta, e quella è del
pianificatore.

> ⚠ **Un buco noto**: un pezzo con **due** attacchi che non è una macchina — il gruppo di
> riempimento — non rientra in nessuno dei due casi, e la sua rotazione va scritta a mano.

## 5. Le regole, e come si scrivono

**Vivono in `docs/regole-del-piano.md`**, e sono due cose insieme: ciò che il pianificatore
segue e ciò che il revisore verifica.

**Una regola è un controllo che sa nominare la propria violazione** (D-153). Se non si può
misurare, il revisore non la può usare e resta un'intenzione: è la differenza fra
«l'autostrada deve essere dritta» e «la tratta `s3` piega quattro volte, e su un'autostrada
le pieghe ammesse sono zero». Una riga senza controllo si scrive `da scrivere`, ed è lavoro
aperto.

**Non si scrivono in astratto.** È così che è nata la funzione di costo: regole dedotte a
tavolino, e poi il disegno non somigliava a niente.

Una regola si estrae **componendo**: si fa una tavola, la si guarda, e quello che si è
imparato diventa una riga — con accanto la tavola che l'ha generata. Le tre regole del 20
settembre sono nate così, e sono buone proprio per questo.

La fonte delle regole è, in quest'ordine:

1. le **correzioni del PO**, `docs/input-pm/REGISTRO.md` — sono ottantacinque, ed è il
   giacimento principale;
2. le **decisioni** che ne sono nate, `docs/DECISION_LOG.md`;
3. la **ricerca del 4 agosto**, `docs/fonti/2026-08-04-come-si-disegna-uno-schema-funzionale.md`,
   che ha misurato due tavole vere;
4. le **tavole di riferimento del disegnatore del PO**, `docs/input-pm/riferimenti-grafici/`.

## 6. Quello che questa architettura costa, e va detto

- **La riproducibilità bit-per-bit se ne va** (D-023): due composizioni dello stesso
  impianto non danno la stessa tavola. Per un elaborato che esce in DXF e si rifinisce in
  AutoCAD (I-072) è un prezzo accettabile, ed è una scelta di prodotto del PO.
- **Il motore non garantisce più che il disegno sia bello**, garantisce che sia **valido** e
  che i difetti siano **nominati**. Il bello lo porta il piano.
- **Il giudizio resta del PO**, e resta sulle tavole (D-146).
