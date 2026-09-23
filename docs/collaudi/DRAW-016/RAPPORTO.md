# DRAW-016 — rapporto in corso

> **Il 23 settembre, per primo:** le tavole che il pianificatore ha composto **da solo** sui
> cinque impianti **completi** stanno in
> [`prova-camera-pulita-2026-09-23/`](prova-camera-pulita-2026-09-23/) — §6. **Approvate dal PO**
> (**I-109**): «hanno proprio l'aspetto di tavole professionali».

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

## 4bis. Il 22 settembre: «perché non lo ha disegnato così?» — e le giaciture diventano otto

Il PO ha ripreso la **tavola 4** composta dall'agente e ha **spostato la commutatrice**: dal
fondo, dov'era appesa, al punto dove la colonna del ritorno incontra la linea che arriva dallo
scambiatore. Poi ha chiesto perché l'agente non l'avesse fatto.

**Perché non poteva**, ed è una tabella di otto righe. La terza via di una tre vie è
**perpendicolare alla via dritta e gira insieme a lei**, quindi resta sempre dalla stessa
parte. Per ricevere dall'alto, mandare in basso e prendere la terza via **a destra**, fra le
**quattro rotazioni** quella giacitura **non esiste**:

| | `in_a` | `out` | `in_b` |
|---|---|---|---|
| rotazione 90 | **sopra** | **sotto** | sinistra |
| rotazione 270 | sotto | sopra | destra |
| **specchio + 270** | **sopra** | **sotto** | **destra** |

Forzando la 90, la linea dallo scambiatore **gira intorno alla valvola** con **quattro pieghe**.

**D-169** porta le giaciture a otto — lo specchio si applica prima della rotazione — e **tocca
il motore, non la libreria**: nessun manifesto lo dichiara, nessun simbolo nuovo esiste,
**D-165 regge**.

| impianto 4, scheletro | a mano | agente con B12 | **con lo specchio** |
|---|---|---|---|
| spezzate piegate | 7 | 4 | **3** |
| pieghe | 12 | 5 | **4** |
| incroci | 3 | 3 | **2** |

**Il saldo della suite non si muove**: 47 fallite, 1580 passate, **insieme identico** a prima
dello specchio — zero nuove, zero perse. *(L'unica caduta era una prova che teneva a mano una
copia dell'elenco dei campi del piano: adesso lo legge dal modello.)*

**E l'invariante che regge tutto ha la sua guardia:** una prova verifica su **tutta la libreria
in tutte e otto le giaciture** che il corpo grafico e il manifesto portino ogni porta **nello
stesso punto** — 268 giaciture, zero disallineamenti. È la guardia contro il difetto che il 21
settembre aveva lasciato la caldaia scollegata dalla propria porta.

**I due agenti l'avevano detto il giorno prima, indipendentemente** — «non esiste lo specchio, e
questo decide il piano intero», «servirebbe un ribaltamento». Nessuno dei due aveva **misurato
quanto costa**: il PO l'ha visto guardando la tavola.

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

---

## 6. Il 23 settembre: il pianificatore sul grafo completo — le tavole, per prime

> **Le tavole stanno in [`prova-camera-pulita-2026-09-23/`](prova-camera-pulita-2026-09-23/)**,
> con i grafi, i piani e il README che le misura. ✅ **Approvate dal PO il 23 settembre 2026**
> (**I-109**): «Si le approvo assolutamente vanno benissimo! Hanno proprio l'aspetto di tavole
> professionali!». Sono la prova che questo pacchetto doveva dare: il pianificatore compone **da
> solo** i cinque impianti **completi**, con tutto il corredo.

Cinque agenti avviati da zero, uno per impianto, con **soltanto** le istruzioni, il grafo
completo e i manifesti; più due sugli scheletri 2 e 3. **Tutti e sette i piani si caricano e si
instradano**, con **zero tratte cedute e zero rilievi bloccanti**.

| impianto | formato | rilievi | spezzate piegate / pieghe / incroci | contro il piano a mano |
|---|---|---|---|---|
| 1 | A3 | 1 | 3 / 4 / 1 | A2, 7 rilievi, 3 / 4 / 1 |
| 2 | A3 | 1 | 3 / 4 / 1 | A2, 9 rilievi, 6 / 10 / 2 |
| 3 | A3 | 2 | 3 / 3 / 2 | A2, **2 bloccanti**, 10 rilievi, 5 / 10 / 1 |
| 4 | A3 | 2 | 5 / 6 / 2 | A2, 11 rilievi, 8 / 14 / 3 |
| 5 | A2 | 3 | 10 / 13 / 5 | **non esce** |

Misura della sessione, con il motore corretto (§7). **Il piano dell'agente non perde niente su
nessun impianto**; l'unica voce peggiore è un incrocio in più sul 3, dichiarato dall'agente.

**Che cosa si vede.** L'impianto **4 assomiglia alla tavola che il PO ha ridisegnato il 21
settembre**: pompa sopra, caldaia sotto alla stessa `x`, le tre vie **sulle orizzontali della
caldaia**, lo scambiatore sotto — e l'agente non l'ha mai vista. L'1, il 3 e il 5 si leggono. Il
**2 ha un difetto che i numeri non vedono**: le discese verso il bollitore sono lunghe un
centinaio di millimetri e la colonna ACS sta stretta fra i due serbatoi, e la sigla del volano
cade accanto a una valvola.

**Criteri del pacchetto che questa prova misura:**

- **1** — il pianificatore gira in camera pulita e il piano si instrada: **cinque impianti su
  cinque**, sul grafo completo (ne servivano tre);
- **2** — il confronto impianto per impianto: la tabella qui sopra, e il README;
- **4** — nessuna tavola perde: cedute zero ovunque, bloccanti **zero** (erano uno sul 3). Il
  punto di partenza del pacchetto era 14 · 14 · 15 · 20 · 38 rilievi e 1 · 2 · 1 · 3 · 12
  incroci; adesso **1 · 1 · 2 · 2 · 3** e **1 · 1 · 2 · 2 · 5**. ⚠ Non è un confronto pulito:
  fra le due misure sono cambiati anche i rilievi (D-170, D-171, D-173);
- **5** — `HIGHWAY_IS_NOT_STRAIGHT` sul 4 e sul 5: da 5 e 12 a **0 e 1**. Il rilievo rimasto è
  l'anello del ricircolo, contato come autostrada: è la domanda di classificazione del 22
  settembre. **Il giudizio si dà guardando** (D-164), ed è sopra;
- **6** — A4 da 24 a **1**: lo sfiato del volano dell'impianto 3, 5 mm oltre il minimo, perché la
  mandata gli passa 10 mm sopra.

## 7. Cinque difetti del motore, trovati dagli agenti e verificati dalla sessione

Gli agenti hanno lavorato con il motore congelato a `1121a8c`. Ogni segnalazione qui sotto è
stata **rieseguita dalla sessione** prima di toccare il codice (D-152), e ogni correzione porta
una prova che **fallisce senza** e la misura prima/dopo su sedici tavole: la 5 approvata, le
quattro del 21 settembre, i cinque piani a mano, i quattro piani completi degli agenti e i due
scheletri.

| difetto | chi l'ha visto | che cosa cambia sulle tavole |
|---|---|---|
| **A4 non accusava un manometro lontano.** Il corridoio che la catena riserva davanti al suo attacco corre lungo il suo stesso stacco, e il controllo lo contava come un vicino: il posto «era preso» a qualunque distanza. Allontanato di 40 mm, nessun rilievo | agente dell'impianto 2 | nessun cambiamento sui piani degli agenti; **8 rilievi A4 in più** sui piani a mano 1–4, tutti vasi e manometri a 22,5 o 27,5 mm contro un minimo di 20 |
| **La posa stampata era 1 mm più in basso del piano**, e gli errori dell'instradatore davano celle della griglia del foglio | agenti degli impianti 3 e 4 | nessuno sul disegno; la posa è quella del piano, e l'errore nomina i due capi della tratta con le coordinate del piano |
| **Il colore di mandata e ritorno lo decideva la geometria** dove le camminate dai generatori si fermano: mandata se la tratta va verso destra. Il ritorno delle zone verso il volano **in serie sul ritorno** usciva rosso, e l'agente ha scartato una posa migliore per questo | agenti dell'impianto 3, completo e scheletro — sullo scheletro, girando un terminale, mandata e ritorno si scambiavano | geometria identica ovunque; cambiano colore **due** tratte: il ritorno raccordo→volano del piano a mano 3, e **2,5 mm della tavola 5 approvata** — il by-pass della miscelatrice, da rosso a blu |
| **Una valvola di ritegno in salita puntava in giù.** La rotazione degli organi in linea la dava la sola giacitura del tratto | agente dell'impianto 4 | nessun tubo si sposta; adesso puntano con il flusso la ritegno della caldaia sul piano a mano 4 e **il circolatore del ricircolo sull'impianto 5 dell'agente**, che era disegnato contro le frecce della propria linea; defangatori e miscelatori termostatici si specchiano, simboli simmetrici e quindi identici a vista |
| **La legenda elencava linee che la tavola non disegna** — «acqua fredda — ritorno», «acqua calda — ritorno» | agente dell'impianto 4 | ogni legenda perde le righe delle linee assenti: da 6 a 4 sui grafi completi, da 6 a 3 sugli scheletri — **anche sulla tavola 5 approvata**, che perde acqua fredda andata e ritorno e ACS ritorno, nessuna delle tre disegnata |

### Riferito dagli agenti, verificato, e non vero

- **«La mappa del raccordo a T è fissa: la porta `a` finisce sempre nella derivazione.»** Non è
  così: scambiando di posto le due zone che il raccordo riunisce, la mappa si inverte. Il
  raccordo segue la posa (C2); l'agente aveva provato pose in cui la stessa zona restava quella
  allineata. Scritto nelle istruzioni.
- **«Il motore rifiuta l'A4 per le fasce.»** Il messaggio viene dalla posa d'inventario, ma nel
  merito è giusto: le quattro tavole degli agenti sono larghe 240–288 mm, e l'area di un A4 ne
  ha 227.

## 8. Il pavimento di B1, la traslazione, e il posatore degli organi

- **Il pavimento di B1** (**D-173**, proposta al PO): conta anche le pieghe **fra due pezzi** —
  la L fra porte su assi perpendicolari, e il gradino di una coppia con interassi diversi. Sulla
  tavola 5 approvata i rilievi di B1 passano **da 7 a 0**; sulle nove tavole misurate da
  7·4·4·3·9·3·4·3·6 a **0·1·0·0·3·0·1·3·3**, e ogni rilievo rimasto è una piega che una posa
  diversa toglie. Guardia: `tests/validation/test_il_pavimento_di_b1.py`.
- **Il motore trasla prima di instradare.** Lo stesso piano spostato di (−20, −105), o lontano
  dall'origine, dà **la stessa tavola al decimo di millimetro**; le nove tavole agli atti non si
  spostano di un punto. Le istruzioni dicevano che contano solo le posizioni relative, e adesso è
  vero.
- **Il posatore degli organi scarta subito il posto dove la propria tratta rientra nel simbolo**,
  invece di scoprirlo a tratta finita. Le nove tavole non cambiano. ⚠ **Non ha fatto tornare
  verde nessuna delle prove rosse che fermava**: sotto c'era un secondo ostacolo, l'instradamento
  di `p4-a-4`, ed è ancora lì (punto 8 del pacchetto).
- **I cinque documenti del motore dichiarano in testa che sono storia** (punto 7, criterio 9).

## 9. Le istruzioni, dopo sette agenti

Entrato in `skill/comporre/ISTRUZIONI.md`, **dopo averlo verificato** sul codice o misurato:

- **chi sta in quale fascia**, come la legge il rilievo di A1 — la pompa di calore per ACS è
  generazione, lo scambiatore a piastre (anche istantaneo) è accumuli e scambiatori; raccordi,
  organi, appesi, collettori e confini di rete **non hanno fascia**;
- **le porte che mancavano**: collettore di zona, pompa di calore per ACS, sfiato e scarico del
  volano a due attacchi;
- **conta la quota della porta, non l'origine** — e il controllo finale lo chiede così;
- **lo specchio vale anche per chi non si ruota** (D-169): è il modo di voltare un volano;
- **il raccordo a T segue la posa**: il motore gli assegna le porte guardando i vicini;
- **quanto rettilineo chiede una fila di organi**, misurato sul motore: 17,5 mm per una valvola
  fra la porta di una pompa e un raccordo, 20–25 per due organi;
- **gli errori parlano nel sistema del piano**, e **il colore lo decide il grafo**;
- dal giro precedente (`39e8aad`): gli organi in linea non si posano, la tabella delle otto
  giaciture della deviatrice, il minimo di A4 per gli stacchi con organi, i casi noti di B11.

## 10. Che cosa resta, e che cosa va al PO

**Domande al PO** — nessuna è del pianificatore, e nessuna l'ho decisa:

1. **D-173**, il pavimento di B1 fra due pezzi: è una **proposta**, e cambia la ragione scritta
   in D-171 punto 3.
2. **B10 contro il pettine.** B10 confronta una mandata con **qualunque** ritorno affiancato,
   anche di un'altra utenza: in un pettine con le utenze impilate il ritorno della prima sta per
   forza sopra la mandata della seconda, e B10 si accende sulla forma che il PO ha disegnato
   (impianto 3, e lo scheletro 3). **Proposta:** B10 confronta una mandata solo con il proprio
   ritorno.
3. **La miscelatrice termostatica ACS ha due attacchi** nel catalogo, senza l'ingresso
   dell'acqua fredda (impianti 1, 2, 3, 5). Contenuto MEP.
4. **L'anello del ricircolo dell'impianto 5** si chiude subito dopo il bollitore e non raggiunge
   le utenze (assunzione a3 del grafo); e tutto il ricircolo esce **da andata**, perché il suo
   verso non si ricava (D-059, domanda 5 già aperta).
5. **La legenda decide il formato dell'impianto 5**: con la legenda corretta manca l'A3 per
   **2,5 mm** — 26 simboli in una colonna sola — e il disegno ci starebbe. L'impaginazione della
   legenda è convenzione grafica.
6. **Il ritorno ACS ha lo stesso colore dell'andata dell'acqua fredda** (`#5dade2`), e le due si
   distinguono solo dal tratteggio. Convenzione grafica.
7. **Sfiato e scarico di un volano in serie sul ritorno escono rossi**: uno stacco che pende da
   una macchina prende il colore base del fluido (I-042). Un agente l'ha letto come un errore.

**Fuori perimetro, scritto e non toccato:**

- la **freccia di verso** cade a metà del tratto più lungo, e due volte è caduta sul ponticello
  di un incrocio (`graphics/sheet.py`);
- la **sigla di un pezzo** a volte cade accanto a un altro (VOL-01 sugli impianti 2 e 4);
- la **ritegno sull'acqua calda** (`valve-check-dhw-hot`) è dichiarata senza verso nel catalogo,
  e il suo simbolo ha la freccia: il motore non sa in che verso disegnarla;
- il **minimo di A4 per uno stacco con rubinetto** è 20 mm, e il motore ne sa fare 15: A4
  tollera 5 mm;
- il **rifiuto dell'A4** arriva dalla posa d'inventario, che conta quattro fasce invece di tre:
  giusto nel merito, confuso nel messaggio;
- la **deduzione C2 dei raccordi** sceglie le porte per direzione verso il centro del vicino, e
  sulla presa del ricircolo dell'impianto 5 l'agente ha dovuto scrivere la rotazione a mano.

**Del pacchetto restano aperti** i punti 2 (vincoli come dati, l'anello), 3 (`passa-per`), 4 (le
cure del revisore), 5 (i piani a mano cambiano di posto e di nome), 6 (i rilievi di A2, A3, B5), 8
e il criterio 10 (la suite): **48 rosse, lo stesso insieme della base del pacchetto** — nessuna nuova, nessuna tornata verde — **1627 passate** (erano 1580: sono le prove nuove), 24 `skip` e 12 `xfail`, **nessuno nuovo**; `ruff` e `mypy` verdi. Il criterio 10 chiede **38 o sotto**, e non è raggiunto: le dieci in più sono il piano a mano dell'impianto 5 che non esce più e le prove del revisore a valle, e si chiudono portando nelle prove i piani del pianificatore al posto di quelli a mano (punto 5).
