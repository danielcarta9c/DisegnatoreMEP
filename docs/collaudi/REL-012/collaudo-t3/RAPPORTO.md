# Rapporto di collaudo della skill disegnatore-mep 1.6.0 — prova T3 (canalizzato in appartamento)

Collaudo della **skill**, non dell'impianto. Cartella di lavoro: `collaudo3/t3/lavoro/`.
Revisione scelta: «in questa conversazione», cioè le tavole le ho guardate io sui PNG dell'anteprima.

## 1. File prodotti, numeri finali, tempi

Consegnati in `lavoro/consegna/` (non c'è `/mnt/user-data/outputs`):

| elaborato | file | esito del comando |
|---|---|---|
| Schema funzionale | `canalizzato-appartamento-secondo-piano-t1.pdf` (+ `.dxf`, `-rilievi.md`) | A2 · 18 tratte · **0 tratte cedute · 0 rilievi bloccanti** · 4 pieghe · **0 sormonti** · 1 avviso (sigla SIF-01 non scritta) · 1 regola del piano (stacco della condensa 10 mm più lungo del minimo) · cartiglio in **bozza** (5 campi DA DEFINIRE) |
| Distinta | `distinta.xlsx` (+ `distinta.json`, `distinta-calcoli.md`, `tabelle-del-foglio.json`) | 80 voci in 9 sezioni, 16 tratte · uscita 2 · **7 righe DA DEFINIRE** (il comando ne elenca 13 come domande) · fornitura `confermata` |
| Pianta | `pianta.pdf` + `pianta-dettaglio-A/B/C.pdf` (+ `.dxf`) | A2 1:50 · 15 tracciati, 0 non instradati · 0 diagonali · 0 sovrapposizioni · **16 sormonti** · 4 forature · uscita **0** (nessun BLOCCANTE) · 2 avvisi (T11 misurata 12,8 m su 10, +28 %; T03 e T08 fuori dal controsoffitto) |

Righe DA DEFINIRE della distinta: dimensione delle 4 bocchette (porta-bocchetta B.7 e bocchetta Z.2), riserva di
R32 (C.7: mancano precarica e carica aggiuntiva dell'UE), attacco condensa della UI (D.9), protezione delle due
linee nel quadro (E.3, E.4), sezione del bus ai termostati (E.8).

Tempi (orologio del contenitore): inizio 22:35, consegna 22:44. Il comando è sempre rapido: `ambiente` 0,5 s,
`completa` 0,4 s, `distinta` 0,6 s, `disegna` 0,5 s, `pianta` 3,8 s. Giri: schema **4 esecuzioni** di `disegna`
(A3 non si instrada → A2 con 1 bloccante → 2 bloccanti e 4 sormonti → pulita); pianta **2 giri** più 3 varianti di
prova. Il grafo ha validato **al primo colpo** (17 pezzi, 20 tubazioni, 12 reti); `completa` aggiunge 0 accessori e
0 punti aperti, come ci si aspetta su un aria-aria.

**Giudizio a occhio, che i numeri non dicono:** lo schema si consegna (in bozza). **La pianta no**, anche se il
comando esce con 0: vedi §3.

## 2. Dove la skill mi ha fatto inciampare

### Istruzioni ambigue o contraddittorie

1. **`riferimenti/capire.md` §4.6, righe 484-502 (regime della centrale)** — dice di sommare i `power_kw` dei
   `heat_generation` e, se mancano, «ometti il campo e scrivi la domanda in assumptions». Un'unità esterna è
   `refrigerant_generation`: alla lettera dovrei chiedere al progettista «sotto o sopra 35 kW?» su un canalizzato,
   dove non vuol dire niente. `valida` stampa «regime della centrale: non dichiarato» senza dire se è un problema.
   Manca una riga: «sull'aria-aria il regime non si scrive e non si chiede».
2. **`SKILL.md` righe 119-124 contro 123-124** e **`capire.md` §4.7** — «i diametri, se il testo non dice se li
   vuole: chiedi se vuole il dimensionamento». Il progettista ha scritto «voglio diametri e lunghezze di ogni
   tratto», intendendo le **sezioni che ha dato lui**. Non è chiaro se «diametri» dell'aria-aria faccia scattare il
   §4.7 (calcolo idronico) o il §4.8 (trascrizione). L'ho letta come §4.8, e l'ho dichiarata.
3. **`riferimenti/pianta.md` righe 238-247 contro `dati/esempi/pianta-appartamento.json`** — il riferimento dice che
   quadro–sezionatore–UE è **una** tratta con `passa_per` («Non inventare T10b»); l'esempio la spezza in **T11 e T12**
   senza `passa_per`. L'esempio usa anche `"tipo": "return-grille"`, che è l'id del **simbolo**, mentre il catalogo
   chiama il pezzo `return-air-terminal`: non si capisce che cosa voglia `tipo` (ho usato l'id di catalogo e passa).
4. **`riferimenti/pianta.md` righe 186-192 e 224-228** — sigle e numeri di tratta «dalla tavola dello schema» e
   «dalla tabella delle tratte»: si **ricopiano a mano**. Il comando `pianta` non riceve il grafo né la distinta e
   quindi **non può controllare** che le sigle e i numeri coincidano. La nota stampata sulla tavola («Sigle e numeri
   di tratta come lo schema funzionale e la distinta») è vera solo se l'agente non sbaglia a copiare.
5. **`riferimenti/pianta.md` riga 188 («le posizioni: dal progettista») e §4 (`larghezza`, `profondita`)** — la
   pianta vuole l'ingombro di ogni pezzo, ma il catalogo non ha dimensioni e il progettista non le dà. Non c'è
   istruzione su dove prenderle. Ho scritto UI 1,10 × 0,73 (dato di scheda che conosco, cioè un dato non del testo)
   e plenum, centrale, ripresa a stima, tutto «da confermare» nelle note. È esattamente l'«inventare» che `SKILL.md`
   riga 39 vieta, ma senza ingombri la pianta non si fa.
6. **Pezzi sovrapposti in pianta** — il progettista dice «centrale di zona sopra il plenum» e «ripresa nel disimpegno,
   sotto la UI». In pianta sono pezzi uno sopra l'altro. Con la centrale sopra il plenum: **5 tratte non
   instradate, 8 linee sopra un pezzo, 3 scritte bloccanti**. `pianta.md` non dice come si dichiara un pezzo sopra
   un altro: li ho spostati accanto e l'ho scritto nelle note. La posizione sulla pianta quindi **non è quella
   vera**.
7. **`riferimenti/distinta.md` riga 59** — «se manca `attraversamenti`, la distinta ne assume uno per l'aria, la
   condensa e la linea del gas». Ne conta 1 per ramo d'aria, 1 per il gas, 1 per la condensa. Intanto la pianta
   misura le sue forature (F1-F4: frigo attraverso la tramezza **e** il perimetrale, il cavo UI-UE da un altro foro
   nel perimetrale ovest). **Forature della pianta e forature della distinta non si parlano**: la distinta non legge
   la pianta, e non c'è un'istruzione per riportarle nel grafo.
8. **`SKILL.md` righe 361-367 (Consegnare)** — `mep.py consegna` copia **solo la cartella della tavola**. Distinta
   (Excel) e pianta, che lo stesso paragrafo dice di consegnare, vanno copiate a mano. Non è scritto.
9. **`riferimenti/comporre.md` riga 236-245 (`zone_tabelle`)** — dice «allarga le zone o prendi il formato
   successivo», ma non quanto spazio vuole una tabella delle tratte di 16 righe. Ho tirato a indovinare `basso_mm:
   120`. Su A3 l'area è rimasta 350 × 115 mm e il piano non si è instradato. Il messaggio era buono: dava la causa
   probabile, la posa 250 × 160 che non sta nell'area.
10. **Contrasto fra A4 e la scritta del tratto (`comporre.md` §4bis / A4 contro REL-012)** — con lo scarico della
    condensa al minimo dello stacco (25 mm), la scritta «PVC Ø32 · L 8 m» non trova posto → **bloccante**.
    Allontanandolo di 10 mm la scritta entra, ma esce la regola A4 («stacco più lungo del minimo»). Due regole della
    skill tirano in versi opposti, e nessuna delle due dice che l'altra vince.

### Comandi che hanno dato errore

- `python3 scripts/mep.py completa … | head -1` → `Errore: [Errno 32] Broken pipe`. È colpa del tubo verso `head`,
  ma il comando lo stampa come «Errore» e non si capisce se il file è stato scritto: ho rilanciato senza tubo.
- `disegna` su A3: `Il piano non si instrada: la tratta alim-centrale-zona … nessuna strada da (28, 38) a (86,
  48)` — corretto, con la causa giusta (la posa non sta nell'area).
- `disegna` su A2, primo giro: `RUN_LABEL_OMITTED` sul cavo del comando a filo (rettilineo di 15 mm). Secondo giro:
  `RUN_OVERSHOOTS_ITS_PORT` + `RUN_LABEL_OMITTED` + 4 sormonti. Si è risolto cambiando l'uscita del quadro per la
  centrale (`out_2` → `out_3`) nel grafo, cosa che `comporre.md` §5 permette.
- `pianta` con la centrale sopra il plenum: uscita 2, 4 BLOCCANTI (vedi punto 6).
- `pianta` con `"foglio": {"formato": "A3"}`: «la colonna non entra nel foglio: la tavola esce lo stesso, e va
  vista». Esce lo stesso con uscita 0, cioè una tavola con la colonna tagliata non ferma niente.

### Voci che mancavano, dati che non sapevo dove mettere

- **Pompa di condensa a bordo della UI**: nel catalogo non c'è un mestiere, e `a_bordo` vuole un mestiere. L'ho
  messa a parole fra le `properties` (`pompa_condensa: "a bordo"`). La distinta ne tiene conto solo in G.5 («prova
  della pompa»).
- **«Due bocchette asservite allo stesso termostato»**: è regolazione, e sul grafo non c'è un posto dove dirlo. Sullo
  schema **non si vede** che TZ-03 comanda TA-03 e TA-04: lo dicono solo le etichette dei locali.
- **Cavo del bus Airzone**: lunghezza data, sezione no. Il tratto resta senza sezione (giusto), ma sulla tavola si
  legge solo «L 7 m».
- **Esterno e terrazzo in pianta**: lo schema della pianta non sa che cosa c'è fuori dal muro. Il terrazzo sta solo a
  sud del soggiorno, ma l'instradatore porta la linea dell'UE fuori dalla **porta di casa** e lungo la facciata
  (vedi §3). Non c'è un campo «esterno praticabile» o «terrazzo».
- **Ingombri dei pezzi** per la pianta (punto 5).
- **La tabella delle apparecchiature dello schema non porta i termostati**: marca e modello «Airzone Think a filo»,
  dati dal progettista, sulla tavola **non compaiono**. Restano solo nell'Excel (A.3).

## 3. Che cosa ho visto sulle tavole e i numeri non dicono

### Le sigle sono le stesse sui tre elaborati; i numeri di tratta solo su due

- **Le sigle** (UE-01, UI-01, PLZ-01, CZ-01, TA-01…04, TZ-01…03, CF-01, QE-01, SZ-01, SIF-01, AL-01, RA-01) sono le
  stesse su schema, distinta e pianta. Sulla pianta però **le ho ricopiate io**: niente le controlla (§2, punto 4).
- **Lo schema funzionale non scrive i numeri di tratta sulle linee.** T01…T16 compaiono solo nella tabella delle
  tratte sul foglio, nell'Excel e sulla pianta. Sullo schema la riga della tabella si ritrova solo con la colonna
  «Da - a». Per un installatore che legge lo schema e la pianta insieme è il primo inciampo.
- **T03 e T04 sono incrociati con TA-03 e TA-04**: T03 = PLZ-01 → **TA-04** (6 m), T04 = PLZ-01 → **TA-03** (4 m).
  Sullo schema TA-03 sta sull'uscita 3 del plenum e TA-04 sull'uscita 4. Non è un errore, ma si legge male.

### Le lunghezze: coincidono i numeri, non le scritte

- **«L quot.» coincide fra distinta e pianta su tutte le 15 tratte instradate**: misurato confrontando
  `tabelle-del-foglio.json` con `pianta.tracciati.json` (T01 7, T02 5, T03 8,5, T04 6, T06 12, T07 12, T08 10,5, T09
  10,5, T10 22, T11 13, T12 9,5, T13 7, T14 11,5, T15 8,5, T16 5).
- **Le scritte sulle linee però non coincidono.** Lo schema scrive la lunghezza del progettista («Ø200 · L 5 m»,
  «2×0,75 · L 2 m»). La pianta scrive sulla stessa tratta la lunghezza **da quotare** («T01 · Ø200 · L 7 m», «T16 ·
  2×0,75 · L 5 m»). Chi mette le due tavole una accanto all'altra legge **due lunghezze diverse per lo stesso
  tratto**, e solo la legenda della pianta spiega perché. Questo è il rilievo più serio del collaudo, e nessun
  numero lo segnala.
- **La scritta del fascio frigo sulla pianta**, «T06+T07+T11 · L 13 m», dà **una** lunghezza a tre tratte che ne
  hanno due diverse (12, 12, 13). E sulla tavola T11 non è nemmeno nel fascio.
- **T05 (ripresa 800×300)**: sullo schema la linea non ha scritta, perché è un raccordo diretto. Nella tabella delle
  tratte del foglio è «canale di ripresa coibentato», senza lunghezze. Nell'Excel è invece un «plenum di ripresa»
  (B.10). Sono tre letture diverse dello stesso raccordo, e la tabella fa pensare a un canale che non c'è.
- **Lunghezze misurate in pianta contro quelle date**: T02 (singola) 3,4 m contro 3; T08 (condensa) 1,9 m contro 8;
  T10 (UE) 10,8 m contro 18. Le misure sono controlli e non entrano nei conti: va bene. Ma lo scarto della
  condensa (8 m contro 1,9) dice che la mia posizione dell'allaccio non è quella del progettista. La skill lo
  segnala solo sopra il +15 %, mai sotto.

### Lo schema (lo consegnerei, in bozza)

- È pulito e si legge: frigo rette fra UE e UI, plenum con le 4 bocchette in colonna, centrale e termostati in colonna,
  quadro sotto l'UE con il sezionatore in linea. Zero sormonti.
- **SIF-01 senza sigla** (avviso `TAG_OMITTED`): il sifone si vede, la sigla no, e la tabella delle tratte dice
  «UI-01 - SIF-01 - AL-01».
- **Il cablaggio di fabbrica plenum–centrale** (lunghezza 0) è disegnato come un bus qualunque, tratteggio blu senza
  scritta. Non si distingue da un cavo da posare.
- **La tabella delle tratte** va su due colonne, e la seconda contiene **una sola riga (T16)** con l'intestazione
  ripetuta. Spazio sprecato, e si legge come una tabella diversa.
- Le etichette dei locali dei termostati sono una sopra il simbolo, una a destra e una sotto: incoerenti, e
  «Camera matrimoniale» sopra TZ-01 si può leggere come scritta della linea del bus.
- Il foglio è un A2 per uno schema che ne occupa un terzo. Lo spazio lo prende la tabella delle tratte in basso.

### La pianta (non la consegnerei, anche se esce con 0)

- **T11, il cavo UI-UE, esce dal muro perimetrale ovest (F3) e fa il giro dell'edificio all'esterno** fino all'UE,
  separato dalle linee frigo con cui dovrebbe correre in fascio. Il fascio «frigo» sta insieme solo per il 58 % del
  percorso. Il comando lo dice soltanto come avviso (+28 %).
- **T10, l'alimentazione dell'UE, esce dalla porta di casa** e corre lungo la facciata sud, cioè sul pianerottolo o
  fuori dall'appartamento, per arrivare al sezionatore sul terrazzo.
- **16 sormonti** e uscita 0: fra i bus a stella della centrale, le linee frigo e le alimentazioni il nodo del
  corridoio è un groviglio. La regola «tutto quello che ferma la consegna esce come BLOCCANTE» qui non ferma niente.
- **La centrale e la ripresa non stanno dove dice il progettista** (accanto e non sopra o sotto: §2, punto 6).
- **Dettaglio A 1:20**: il plenum e la UI sono **rettangoli senza sigla**, e il riquadro è tagliato in modo che non si
  capisce dove sta. Il numero della tavola del dettaglio è «DA DEFINIRE.A».
- Il formato scelto da solo è un A2 con la pianta in un terzo del foglio. Forzando l'A3 la colonna di destra non entra,
  ma la tavola esce lo stesso con uscita 0.
- Ho provato 3 varianti del lato da cui il fascio lascia la UI (sotto, sopra, libero): sormonti 16 / 24 / 15, fascio
  58 / 68 / 59 %, sempre un tracciato oltre il +15 %. Ho tenuto «sotto». Dai `lato` e dalla posa, le sole leve che
  la skill dà, non si ottiene una pianta presentabile.

### Altro

- Il file `-rilievi.md` consegnato al progettista porta i codici interni (`TAG_OMITTED`, `D-025`, `A4, D-145`) e gli
  apostrofi ASCII («qualita'», «e'»). `SKILL.md` riga 389 dice «niente codici interni».
- Il comando `distinta` dice «DA DEFINIRE — 7 voci» e sotto elenca **13** domande: la stessa «dimensione della
  bocchetta» è ripetuta 8 volte (4 bocchette × 2 voci).

## 4. Le domande che avrei fatto al progettista

Le ho scritte per intero in `lavoro/domande.md`, con la prima interpretazione di ciascuna. In breve:

1. Le bocchette del soggiorno: la 4 m è quella sopra il varco e la 6 m quella a x=1? (assunto sì)
2. La ripresa è attaccata direttamente alla UI, senza canale? (assunto sì, lunghezza 0)
3. Il plenum è sulla bocca della UI, il comando delle serrande è cablato di fabbrica e la centrale è nel kit del
   plenum? (assunto sì)
4. La UI è alimentata dall'UE con il 4G1,5, senza linea dal quadro? La centrale Airzone non ha un sezionatore
   locale? (assunto sì)
5. Camera singola: 3 m di flessibile bastano, con il plenum a ovest della UI e la bocchetta a x=8,75? (in pianta 3,4 m)
6. 7,1 kW è la resa in raffrescamento?
7. Dati: committente, commessa, indirizzo, titolo e numero delle tavole; modello del plenum e della centrale Airzone;
   cavo del bus Airzone; dimensioni delle bocchette; attacco condensa della UI; precarica, carica aggiuntiva e
   lunghezza massima delle linee dell'UE; protezioni nel quadro.
8. Fornitura come al solito (macchine Nove C, bocchette, griglie e ripresa del Committente)? (assunto sì →
   `--fornitura confermata`)
9. Sullo schema solo tratte e note, il computo nell'Excel? (assunto sì)
10. Per la pianta: ingombri reali di UI, plenum e ripresa; dove stanno termostati, comando a filo, sezionatore e
    allaccio alla cucina; dove le linee possono uscire sul terrazzo (un foro previsto?).

## 5. Giudizio secco

**Non pronta per un uso dal vivo domani, per la parte della pianta. Lo schema funzionale e la distinta sì,
con riserve.**

- **Schema + distinta**: il grafo valida al primo colpo, i comandi sono veloci e i messaggi portano alla correzione.
  In quattro giri si arriva a una tavola pulita, e l'Excel è completo e onesto sulle voci DA DEFINIRE. Restano tre
  cose: i numeri di tratta che lo schema non scrive sulle linee; la tabella delle apparecchiature che perde i
  termostati; T05, che la tabella delle tratte chiama «canale».
- **Che cosa ferma la pianta**:
  1. esce con **uscita 0** con un cavo che fa il giro dell'edificio, un'alimentazione che passa dalla porta di casa
     e 16 sormonti. Il controllo che dovrebbe fermarla non scatta, e un progettista che si fida dell'uscita la
     riceverebbe così;
  2. sigle e numeri di tratta si ricopiano a mano, senza nessun controllo incrociato con il grafo e la distinta;
  3. **le scritte delle lunghezze sulla pianta (L da quotare) non sono quelle dello schema (L del progettista)**
     per lo stesso tratto: davanti all'installatore è la contraddizione più visibile dei tre elaborati;
  4. mancano il modo di dire «sopra/sotto un altro pezzo», l'esterno praticabile (il terrazzo) e da dove prendere
     gli ingombri, che oggi l'agente deve inventare.
- Da sistemare comunque prima dell'uso dal vivo: `consegna`, che non copia distinta e pianta; i codici interni nel
  file dei rilievi; la regola A4 contro la scritta obbligatoria del tratto; il regime della centrale che `capire.md`
  fa chiedere anche sull'aria-aria.
