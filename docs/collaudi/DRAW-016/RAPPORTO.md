# DRAW-016 — rapporto in corso

**Aperto:** 21 settembre 2026 · **Agente unico** (D-147), con agenti paralleli in sessione
(D-152) · **Base:** `3bcf59d`, la testa di `main` dopo la fusione di `DRAW-015`

> ⛔ **Le tavole di `DRAW-015` sono fuse e non approvate** (D-166). Questo pacchetto parte da
> lì, e il suo punto 0 è la prova che il PO ha dichiarato: **le tavole senza il corredo**.

---

## 1. Il punto 0, e che cosa ha dato

> «Proviamo innanzi tutto nella prossima sessione a **disegnare le tavole senza le valvole in
> mezzo** in modo da vedere se **gli agenti riescono a disegnare queste autostrade come farebbe
> un disegnatore umano**.»

**Il riduttore è nel repository** — `riduci-a-scheletro.py`, qui accanto. Pota le foglie finché
ce ne sono (un organo di servizio è un vicolo cieco, e un T che reggeva solo lui scende a grado
2 e sparisce), tiene chi resta a **grado ≥ 3** perché quello è il collettore, e ricuce le
macchine dove erano unite passando per i pezzi tolti.

| impianto | pezzi | → scheletro | tubazioni | → scheletro |
|---|---|---|---|---|
| 1 | 39 | **7** | 41 | **9** |
| 2 | 41 | **7** | 43 | **9** |
| 3 | 39 | **8** | 39 | **8** |
| 4 | 46 | **10** | 49 | **13** |
| 5 | 93 | **23** | 101 | **31** |

### Il punto di partenza, misurato

Gli scheletri instradati con i **piani scritti a mano**:

| impianto | tratte | cedute | incroci | spezzate piegate | pieghe |
|---|---|---|---|---|---|
| 1 | 9 | 0 | 1 | 4 | 6 |
| 2 | 9 | 0 | 2 | 3 | 4 |
| 3 | 8 | 0 | 1 | 5 | 8 |
| 4 | 13 | 0 | 3 | **7** | 12 |
| 5 | 31 | 0 | **12** | **13** | 23 |

### Quello che le tavole dicono a occhio, e che nessun numero dice

**L'impianto 5 dimostra la tesi su sé stesso.** A sinistra le tre pompe sono impilate, i due
collettori sono verticali corte accanto a loro, i tronchi partono dritti: **quella metà si
legge**. A destra le macchine sono sparse e il disegno è un groviglio. Stessa tavola, stesso
motore, stesso giorno: **la differenza è solo la posa**.

**L'impianto 4 non ha una centrale.** Pompa e caldaia stanno alla stessa `x` ma a quote
lontanissime, e per unirle servono due colonne che attraversano mezzo foglio.

**E una cosa che il PO aveva approvato e a me sembra sbagliata:** sull'impianto 1 il ritorno
della pompa in alto **scavalca la mandata dell'altra** per raggiungere il proprio collettore.
È lo stesso difetto del bollitore corretto il 20 settembre — **i due collettori sono
nell'ordine sbagliato**.

---

## 2. Il pianificatore esiste, e in camera pulita batte il piano a mano

> **Le tavole, gli scheletri e i piani della prova stanno in
> [`prova-camera-pulita-2026-09-21/`](prova-camera-pulita-2026-09-21/).** Sono la **misura**
> di che cosa sa fare il pianificatore il 21 settembre 2026, non prodotto: non si correggono a
> mano, si **rifà la prova**.

`skill/comporre/`, nella stessa forma del pezzo 1. Le istruzioni portano **il metodo di D-159
prima delle regole**, con i numeri veri delle porte, e la leva che ne discende:

> **Due macchine posate allo stesso `y` danno due autostrade perfettamente rette, gratis.**

**Provato in camera pulita** su tre impianti: agenti avviati da zero, che ricevono **solo**
`ISTRUZIONI.md` e il grafo scheletro, e **non possono leggere i piani a mano**. Tutti e tre
producono un piano che si carica e si instrada, **zero tratte cedute**.

| impianto | | a mano | agente |
|---|---|---|---|
| **1** | spezzate piegate | 4 | **3** |
| | pieghe | 6 | **4** |
| | incroci | 1 | 1 |
| | formato | A2 | **A4** |
| **5** | spezzate piegate | 13 | 13 |
| | pieghe | 23 | **16** |
| | incroci | 12 | **6** |
| | formato | A1 | **A2** |

*(Misure rieseguite dalla sessione, non riferite dagli agenti — D-152.)*

### E poi è arrivata B12, e le tavole sono state ricomposte applicandola

| impianto | | a mano | 1° giro | **con B12** |
|---|---|---|---|---|
| **4** | formato | A2 | A3 | **A4** |
| | spezzate piegate | 7 | 5 | **4** |
| | pieghe | 12 | 7 | **5** |
| | incroci | 3 | 5 | **3** |
| **5** | formato | A1 | A2 | **A3** |
| | spezzate piegate | 13 | 13 | **12** |
| | pieghe | 23 | 16 | **16** |
| | incroci | 12 | 6 | **5** |

**Zero cedute e zero bloccanti su tutti.** Il salto è il **formato**: l'impianto 5 passa da
**A1 ad A3** — un quarto di foglio — e il 4 da **A2 ad A4**. Il foglio più piccolo in cui un
impianto ci sta è il modo più diretto che abbiamo per dire che il disegno **non spreca**.

**E il pettine si vede.** Sull'impianto 5 le tre pompe sono impilate strette, i collettori
stanno **addosso a loro**, e le tre utenze sono servite da **due colonne adiacenti con una
coppia di orizzontali ciascuna**, affiancate fino al terminale, che entra da sinistra.
Sull'impianto 4 la tratta caldaia → scambiatore corre come **due orizzontali a interasse 15**,
che è quello che il PO aveva ridisegnato a mano.

**Quello che non è venuto sta nel README della prova**, e sono tre cose che **non dipendono
dalla posa**: il bilancio di B1 irraggiungibile dove il simbolo impone la piega (due agenti su
due, con le stesse parole: «il numero è irraggiungibile, non il disegno è sbagliato»), B12 che
presuppone una ramificazione simmetrica, e l'interasse dei terminali a 10.

### Le due cose che gli agenti hanno visto e che valgono più dei numeri

**1. Un controllo mio accusava tavole giuste.** L'agente dell'impianto 1 l'ha detto con le
parole che il `CLAUDE.md` chiede: «la tavola mi sembra giusta e i numeri dicono che è
sbagliata». Aveva ragione — §3.

**2. Il controllo D3 sta peggiorando il disegno.** L'agente dell'impianto 5, da solo:

> «Il bilanciamento l'ho ottenuto **allontanando il volano dalle pompe**: 85 mm di autostrada
> vuota, solo per spostare inchiostro nel quadrante destro. È retta e il criterio è
> soddisfatto, ma **un disegnatore quel tratto lo accorcerebbe**. Se il PO guarda la tavola e
> quel vuoto gli sembra sbagliato, ha ragione lui: è il criterio dell'inchiostro per quadranti
> che sta spingendo **nella direzione opposta al buon disegno**.»

E l'agente dell'impianto 4, indipendentemente, la stessa cosa sullo scambiatore a piastre:
«l'ho spostato lontano dalla caldaia **solo** per l'inchiostro… un disegnatore lo terrebbe
accanto. Qui il numero e il disegno non dicono la stessa cosa, e ho seguito il numero».

**È D-164 vista dall'altro lato:** quando c'è un numero, l'agente lo insegue. **Un punteggio si
ottimizza, e questo si ottimizza nel verso sbagliato.** La direzione — da portare al PO — è che
**D3 diventi una cosa che l'occhio guarda, non un rilievo che entra nel punteggio.**

---

## 3. Un difetto mio, trovato da un agente: B10 accusava tavole giuste

Il controllo ricavava la quota di una tratta dal **minimo sull'intera spezzata**. Ma una
spezzata tocca più quote: il ritorno che gira attorno a un terminale esce con un mozzicone di
**2,5 mm** alla quota della mandata e fa la propria corsa quindici millimetri più in basso. Col
minimo le due quote pareggiavano, e il rilievo si accendeva su una tavola dove **la mandata sta
sopra**.

**È lo stesso errore corretto su B11 il 20 settembre, rifatto su B10 il 21.** Per questo la
correzione non sta nel controllo: `_affiancamenti` restituisce adesso **anche le due quote dei
tratti affiancati**, che è il posto dove vanno lette, e nessuno le ricava più altrove.

**Misurato, e cambia le tavole già fuse:** dei quattro rilievi di B10 sulle cinque tavole,
**tre erano falsi**.

| impianto | B10 prima | dopo | rilievi |
|---|---|---|---|
| 2 | 1 | **0** | 14 → **13** |
| 3 | 1 | 1 (vero, 5,0 mm) | 15 |
| 4 | 2 | **0** | 20 → **18** |
| 5 | 1 | 1 (vero, 50,0 mm) | 38 |

Due prove nuove sorvegliano i due versi.

---

## 4. La regola che il PO ha disegnato: **B12**

Il 21 settembre ha preso la tavola 5 e la tavola 4 e **ci ha ridisegnato sopra**, due volte la
stessa cosa (`input-pm/riferimenti-grafici/2026-09-21/`), poi ha chiesto: «riesci a tirare
fuori una regola?».

> **La coppia mandata/ritorno è un oggetto solo — un binario a due corsie — e si ramifica a
> pettine.**

**Non è nuova al progetto:** `B2` la nomina già per il circolatore («poi la dorsale a
pettine») e la ricerca del 4 agosto 2026 §2.2 l'aveva trovata sulle tavole vere chiamandola
«composizione a corsie», con la riga che diceva che sarebbe entrata «quando l'avremo composta
almeno una volta». **L'ha composta lui.**

**E le due cose che ha notato sono i due impedimenti a quella forma**, non due osservazioni
sparse:

**D-167 — un terminale si prende da un lato solo.** `radiator`, `fan-coil`, `ahu-coil` e
`underfloor-panel` hanno adesso tutt'e due le porte sulla **faccia sinistra**, `in` sopra e
`out` sotto, interasse **10**. Con le porte su facce opposte il ritorno è **costretto** a
girare attorno al pezzo. ⚠ **Era scritto nelle istruzioni del pianificatore come un fatto
immutabile** — «non è un difetto della tua posa, è la forma del pezzo» — **e non lo era: era un
difetto della libreria.**

**D-168 — la rotazione di una tre vie si sceglie e si scrive nel piano.** Corroborata dalla
sessione stessa: l'agente dell'impianto 4, che non conosceva la disposizione del PO, ha
riferito che «l'orientamento di una valvola di corredo ha deciso quale generatore va in alto» e
che la rotazione «la devi scrivere per forza». **Era già obbligatoria e non era scritto da
nessuna parte.**

### Il costo, dichiarato

**Il cambio dei simboli peggiora prima di migliorare, ed è la prova che i piani vanno
ricomposti.** I cinque piani a mano sono composti per terminali passanti, e mettono le utenze
dove il pettine non passa:

| | rilievi prima | dopo D-167 |
|---|---|---|
| impianto 1 | 14 | **12** |
| impianto 2 | 13 | 16 |
| impianto 3 | 15 (1 bloccante) | 14 (**2** bloccanti) |
| impianto 4 | 18 | 21 |
| impianto 5 | 38 | 46 (**1** bloccante) |

**E la suite passa da 38 rosse a 47.** Le nove nuove sono tutte la stessa cosa: il piano a mano
dell'impianto 5 apre un `RUN_OVERSHOOTS_ITS_PORT` bloccante su `s8`, e le prove del revisore
cadono a valle di quello. **Nessuna delle 38 precedenti è tornata verde.**

⚠ **Non è un difetto del cambio, ed è il punto da tenere fermo:** i piani a mano sono il
**bersaglio** del pianificatore, non il prodotto, e adesso sono **vecchi**. Si chiudono
ricomponendo, che è il punto 0 e il punto 5 del pacchetto. **Finché non sono ricomposti il
saldo resta 47, e si dichiara.**

---

## 5. Quello che gli agenti hanno detto delle istruzioni, e che è stato corretto

Tre agenti su tre hanno riferito le stesse mancanze. Sono entrate in `ISTRUZIONI.md`:

- **quali pezzi vanno nel piano** — solo quelli in `components`; il grafo ne nomina decine
  altrove che non sono pezzi. Tutti e tre l'hanno dovuto indovinare;
- **le coordinate non sono sul foglio** — il motore **trasla l'intero disegno** per centrarlo,
  e contano solo le posizioni relative. Due agenti hanno perso tentativi provando a collocare
  il disegno rispetto al bordo;
- **la rotazione va scritta sulle tre vie** (D-168), è in **gradi orari**, e molti simboli
  **non si ruotano affatto** — chiederlo fa abortire il comando;
- **i quattro numeri** che tutti e tre hanno letto dai messaggi d'errore invece che dalle
  istruzioni: passo di griglia 2,5, stacco minimo 10, corsia libera 10, interasse delle porte
  15.

**Resta aperto, e non è stato risolto:** il motore tratta come autostrada **ogni** tratta fra
due pezzi di spina, raccordi compresi, e le pieghe ammesse sono **zero**, non «poche». Due
agenti hanno segnalato che per una macchina impilata quelle due pieghe (una per salire, una per
rientrare) sono **strutturalmente non togliibili**, e che A2 e B1 si contendono lo stesso pezzo
senza che nessuna ceda. È la stessa famiglia della contraddizione **B1 contro B3**, già aperta
al PO.
