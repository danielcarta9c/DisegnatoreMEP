# HANDOFF — Disegnatore MEP

**Aggiornato:** 2026-09-22, a `DRAW-016` punto 0 **fatto** e a **D-169**, **D-170**, **D-171** e **D-172**
**Scopo:** ingresso operativo breve per una nuova sessione.

> **Se leggi una cosa sola oltre a questa pagina, leggi `docs/ARCHITETTURA-DEL-PIANO.md`.**
> Dice **quali sono i cinque pezzi della skill**, **di che pasta è fatto ciascuno** — agente
> AI, deterministico, o misto — e **che cosa passa fra l'uno e l'altro**.
>
> È stato riscritto il 20 settembre perché una sessione ha sbagliato lo sviluppo pur avendo
> tutte le decisioni sotto gli occhi: ha trattato il **piano** come un artefatto da
> consegnare invece che come qualcosa che la skill deve **imparare a scrivere**.

## ⛔ `DRAW-015` è fuso, e le tavole **non sono approvate**

Sono due cose diverse, e le ha separate il PO (**D-166**), il 21 settembre 2026:

> «La PR la puoi fondere **ma le tavole non sono "approvate"**. Stiamo ancora in fase di
> sviluppo quindi le tavole sono ancora **lontane da ciò che voglio**. Però **la direzione ora
> è quella giusta** quindi va tutto su `main` **con la registrazione che le tavole non vanno
> bene così**.»

**Quello che è approvato è la direzione.** Nessuna sessione può citare quella fusione come
approvazione di una tavola.

## ⛔ La regola che il PO ha disegnato, e che comanda il disegno: **B12**

Il 21 settembre ha ripreso due nostre tavole e **ci ha ridisegnato sopra**
(`docs/input-pm/riferimenti-grafici/2026-09-21/`):

> **La coppia mandata/ritorno è un oggetto solo — un binario a due corsie — e si ramifica a
> pettine.** Due colonne **adiacenti** portano il fluido, e da quelle si stacca **una coppia di
> orizzontali per ogni utenza**: mandata sopra, ritorno sotto, **affiancate per tutta la
> corsa**, fino al terminale, che si prende **da un lato solo**.

E le due cose che ha notato nella stessa risposta sono **i due impedimenti** a quella forma:

- **D-167** — un terminale si prende **da un lato solo**. `radiator`, `fan-coil`, `ahu-coil` e
  `underfloor-panel` hanno adesso tutt'e due le porte sulla **faccia sinistra**. Con le porte su
  facce opposte il ritorno è **costretto** a girare attorno al pezzo, e la coppia si apre.
  ⚠ **Supera D-163 punto 3 per questa classe di simboli e solo per questa.**
- **D-168** — la **rotazione di una tre vie si sceglie e si scrive nel piano**: la terza via
  guarda il pezzo che serve. La deduzione di C2 non la gira, quindi **senza la scelta di chi
  compone finisce sempre verso il basso**.
- **D-169** — **le giaciture di un simbolo sono otto, non quattro**: al `rotazione` del piano si
  affianca **`specchio`**, che si applica **prima** della rotazione. Serviva perché la terza via
  di una tre vie gira insieme alla via dritta: per riceverla **da destra** con ingresso dall'alto
  e uscita in basso, **fra le quattro rotazioni quella giacitura non esiste**. **Tocca il motore,
  non la libreria** — nessun manifesto lo dichiara, e **D-165 regge**.
- **D-171** — **B1 non è una soglia, è un confronto**: «più dritte possibili, meno curve
  possibili e meno sormonti possibili, e viaggiano in parallelo… **non c'è un numero
  massimo**». Tolti `Highway.turns_allowed` (zero o uno, e con lui la forma numerica di D-144)
  e `TOO_MANY_CROSSINGS` col suo cinque. Al loro posto un **pavimento**: le pieghe che le
  **facce dei simboli attraversati impongono**, invariante per giacitura. Quello che resta
  comparativo sta nel **punteggio** — `pieghe` e `incroci` — non fra i rilievi. **Chiude B1
  contro B3** e la metà misurabile di **B7**.
- **D-172** — ⛔ **la skill non progetta la distribuzione.** Il PO: «va disegnato come te l'ho
  detto io… **se il progettista vuole due dorsali distinte lo dice**… questo è un **errore di
  impostazione della skill**». L'**ordine** delle utenze e delle macchine è del progettista, e
  **il ritorno specchia la mandata**; un ritorno inverso o due dorsali si disegnano solo se lui
  li chiede. L'impianto 5 ne aveva uno **inventato su tutt'e due i collettori** — nato in
  «Capire» §4.4, che diceva quanti raccordi e non in che ordine — e la sessione l'aveva
  portato al PO come una domanda. **Una scelta fatta dalla skill non si rigira al progettista
  come se fosse sua.**

⚠ **L'impianto 5 è stato ridisegnato come il PO l'ha chiesto** — A3, zero cedute, zero bloccanti,
il pettine nell'ordine del testo, `docs/collaudi/DRAW-016/prova-camera-pulita-2026-09-22/` — **e
porta 7 rilievi di B1 su una tavola giusta**. Il pavimento di D-171 conta solo le pieghe imposte
dentro un pezzo, e non vede il gomito in fondo a un collettore verticale. È il primo punto da cui
si riparte.

⚠ **Il costo è dichiarato e va saputo prima di misurare**: i cinque piani a mano sono composti
per terminali passanti, e **la suite è passata da 38 rosse a 47**. Le nove nuove sono una cosa
sola — l'impianto 5 apre un bloccante su `s8` e le prove del revisore cadono a valle. **Si
chiudono ricomponendo i piani**, non toccando le prove.

## ⛔ E il criterio di un'autostrada non è un numero

**D-164**, e viene prima di qualunque misura:

> «Quante autostrade **non c'è un numero**… **Un'autostrada per definizione ha poche curve e
> tratti rettilinei.** Ho provato a spiegarlo in ogni modo ma tu ogni volta cerchi un criterio
> **matematico** ma non c'è questo criterio. **Un criterio grafico non matematico.**»

Chi giudica è l'**occhio** (D-162). **Trasformare un'osservazione in una soglia è il solutore
che rientra dalla finestra** (D-151). E **la convenzione grafica non si tocca** (**D-165**):
è quella sviluppata fino a qui; le tavole di riferimento del PO sono riferimenti
**sull'instradamento**, non una fonte di convenzione.

> **E la stessa cosa è successa dall'altro lato, ed è stata decisa** (**D-170**). Il 21
> settembre **due agenti su tre**, in camera pulita e indipendentemente, hanno **allontanato un
> pezzo dalla macchina che serve** — il volano dalle pompe, lo scambiatore dalla caldaia —
> **solo per spegnere `DRAWING_ALL_ON_ONE_SIDE`**, e tutt'e due hanno scritto da soli che un
> disegnatore non lo farebbe. Il PO ha sciolto il conflitto: **A4 vince sempre**, e «**si tiene
> il disegno stretto e si prende il foglio più piccolo che lo contiene — se poi resta del
> vuoto, pazienza: il vuoto non è un difetto**». `DRAWING_ALL_ON_ONE_SIDE` e
> `SHEET_BARELY_FILLED` **non esistono più**; al loro posto `SHEET_LARGER_THAN_NEEDED`, che
> chiede solo se il foglio poteva essere più piccolo.

## ✅ Il pianificatore esiste, e in camera pulita batte il piano scritto a mano

**Il punto 0 di `DRAW-016` — la prova che il PO ha chiesto — è fatto.** Agenti avviati da zero,
che hanno ricevuto **solo** `skill/comporre/ISTRUZIONI.md` e il grafo **scheletro** (sole
macchine e collettori, nessuna valvola), e a cui era vietato leggere qualunque piano esistente.

| impianto | | a mano | agente, 1° giro | agente **con B12** |
|---|---|---|---|---|
| **1** | formato · piegate · incroci | A2 · 4 · 1 | **A4 · 3 · 1** | — |
| **4** | formato · piegate · incroci | A2 · 7 · 3 | A3 · 5 · 5 | **A4 · 4 · 3** |
| **5** | formato · piegate · incroci | A1 · 13 · 12 | A2 · 13 · 6 | **A3 · 12 · 5** |

Zero cedute e zero bloccanti su tutti. **Il salto è il formato**: l'impianto 5 su un **quarto**
di foglio. Prova, piani e tavole in
`docs/collaudi/DRAW-016/prova-camera-pulita-2026-09-21/`; rapporto in
`docs/collaudi/DRAW-016/RAPPORTO.md`.

> **Le misure sono rieseguite dalla sessione, non riferite dagli agenti** (D-152). Ed è servito:
> gli agenti hanno trovato **due cose che nessun numero dava** — un controllo mio che accusava
> tavole giuste, e il fatto che **D3 spinge nel verso sbagliato**.

## Prodotto

Costruiamo una **skill/tool da installare e usare nelle chat di lavoro**. L'ingegnere
descrive un impianto già progettato e dimensionato; la skill lo interpreta, espone
assunzioni e integrazioni, ottiene l'approvazione dell'ingegnere e genera una tavola MEP
vettoriale e verificabile — in PDF e in **DXF**, che il disegnatore apre in AutoCAD e
rifinisce (I-072). **Il DXF non è ancora scritto**, ed è la contropartita di un prezzo già
pagato: vedi *Domande aperte*.

Claude è il team di sviluppo del repository **e**, da D-151, una parte del prodotto: il
disegno lo **compone un agente**.

## I cinque pezzi della skill

| | pezzo | di che pasta è | esiste? |
|---|---|---|---|
| **1** | **Capire** — dal testo dell'ingegnere al grafo di prima stesura | **agente AI** | **sì** — `skill/capire/` |
| **2** | **Completare** — accessori, ordine, domande all'ingegnere | **deterministico** | **sì** — `rules/` |
| **3** | **Comporre** — dal grafo completo al **piano** | **agente AI** | **no, ed è il buco** |
| **4** | **Eseguire** — dal piano alla tavola e ai rilievi | **deterministico** | **sì** — `piano/esecutore.py`, `layout/` |
| **5** | **Rivedere** — dalla tavola ai **vincoli** per il pezzo 3 | **AI + controlli** | **sì** — i controlli in `validation/regole.py`, l'**occhio** in `skill/rivedere/`. Manca l'anello: i vincoli non sono ancora dati |

**I pezzi 3 e 4 insieme sono l'instradatore-disegnatore, ed è misto** (D-156): l'agente
decide **dove stanno i pezzi**, lo script deterministico fa **tutto il resto**. **Il pezzo 5
rimanda al 3, mai al 4**: si corregge il piano, non il disegno.

Fra il 2 e il 3 c'è l'unico cancello umano: **l'ingegnere approva il grafo definitivo**.

**Una sola cosa attraversa la catena: il grafo.** La tavola è una sua vista, e nessun pezzo a
valle tocca la connettività approvata.

> ⚠ **Il piano non è un input del sistema** (**D-155**). Nasce al pezzo 3 e muore quando la
> tavola è uscita. **Non esiste «il piano dell'impianto N»**, e i cinque piani scritti a mano
> sono **materiale di collaudo del pezzo 3** — il bersaglio che deve pareggiare.

Quello che oggi si può guidare dalla CLI è il **4**, e il **3** lo fa un umano a mano:

```
disegnatore-mep rules     <progetto.json>  … --apply-all --out <completo.json>
disegnatore-mep piano     <completo.json>  --piano <piano.json> … --out <cartella>
disegnatore-mep revisiona <completo.json>  --piano <piano.json> … --out <cartella>
```

> **Il disegno nasce dalle autostrade** (**D-159**). La quota di un'autostrada **non si
> sceglie**: è quella della **porta** della macchina che la genera. Si posano le macchine su
> quelle quote, si guarda che le autostrade siano rette, e **solo dopo** si appendono valvole,
> strumenti e confini di rete. Il procedimento per intero sta in testa a
> `docs/regole-del-piano.md`, prima di ogni regola, perché dice **in che ordine** si applicano.

⚠ Il piano si esegue sul progetto nella forma che `rules --apply-all --out` scrive: la forma
canonica riordina i componenti, la posa di partenza legge quell'ordine
(`place.py::_file_order`), e l'impianto 5 si instrada su quello e non su un altro.

## Autorità — **un agente solo** (D-147), con agenti paralleli in sessione (D-152)

- **PO — Daniel Carta:** dominio MEP, requisiti, convenzioni grafiche, priorità, giudizio
  finale del prodotto, e **l'approvazione della fusione**.
- **L'agente — Claude, PM e DEV nella stessa sessione:** scrive il pacchetto, sviluppa,
  misura, mostra le tavole, e fonde **solo dopo il sì del PO**. Nella stessa sessione scrive
  `HANDOFF.md` e il pacchetto successivo.
- **Agenti paralleli:** si lanciano **dentro** la sessione, con un perimetro dichiarato prima
  — un file o una coda. Non consegnano, non fondono, non chiudono niente, e quello che
  riferiscono non è una misura finché la sessione non l'ha rieseguito. Su `DRAW-015` sono
  stati cinque, e ha funzionato: §11 del rapporto dice chi ha fatto che cosa. **Due volte
  quello che un agente ha riferito è stato smentito rieseguendolo**, ed è il motivo per cui
  la regola esiste.

**Il controllo è uno: il PO guarda le tavole.** Senza tavole non c'è niente da approvare, e
senza approvazione non si fonde.

## Stato corrente

- Release in corso: **0.3 — generalizzazione**.
- **`DRAW-015` fuso su `main`** con la PR **#46** — **e le tavole non approvate** (D-166, il
  cartello in testa a questa pagina). Rapporto in `docs/collaudi/DRAW-015/RAPPORTO.md`, col
  verdetto del PO in **§14**. Che cosa porta, in quattro righe:
  - **il revisore esiste** (`piano/revisore.py`): esegue il piano, misura, corregge il piano
    nominando **la regola** di ogni correzione, e si ferma dicendo perché — compreso quando
    un giro peggiora, e allora consegna il precedente;
  - **nove regole del PO sono nove controlli** (`validation/regole.py`): A1 le tre fasce,
    **A4 l'organo di servizio addosso al pezzo che serve**, B1 le autostrade dritte, B3 il
    collettore verticale, B4 l'organo in linea — e poi, guardando le tavole col PO, **B8** i
    sali-scendi, **B9** le corsie libere, **B10** mandata sopra e ritorno sotto, **B11** la
    coppia che corre insieme. Le prime quattro le chiedeva D-154; **A4 è nata guardando le
    tavole**, ed è la regola che ha prodotto D-158; le ultime quattro sono I-096 e D-160;
  - **il piano è un pezzo del prodotto** (`src/disegnatore_mep/piano/`), non più uno script;
  - **il solutore è uscito dalla catena** e i tre moduli lo dichiarano in testa.
- **Tutti e cinque gli impianti di prova producono una tavola**, dal piano, con **zero
  tratte cedute**; il quinto passa da 6 cedute a 0. L'unico rilievo bloccante è
  sull'impianto 3 ed è strutturale (vedi B7).
- **Poi il PO ha fermato lo sviluppo, e ha dettato l'architettura**: da lì **D-155**,
  **D-156**, **D-157** e **D-158**, che sono la parte più importante di questa consegna.
  Il piano **non è un input**; i pezzi della skill sono cinque; il revisore emette
  **vincoli** e non mosse; ogni vincolo di posa vuole un **rilievo sulla tavola**.
- **Un difetto trovato e chiuso in quella conversazione, ed è istruttivo.** I confini di rete
  finivano lontanissimi: il prelievo ACS misurava **205 mm** sull'impianto 2, **502,5** sul 3,
  **152,5** sul 4 — contro i **32,5 e 50** dei due piani composti il 19 e il 20 prima che A1
  fosse un controllo. L'agente aveva **peggiorato una cosa che funzionava applicando una
  regola** (A1) a un pezzo che quella regola non governa, e niente gliel'ha detto perché
  **D-145 vive nella posa del motore e il piano la sovrascrive**. Corretto: il prelievo ACS
  sta adesso a **40 · 20 · 20 · 22,5 · 22,5 mm** dal pezzo che serve, e **tre su cinque sono
  esattamente il proprio minimo**. Da qui D-158, e da D-158 il controllo **A4**, che adesso
  quel difetto lo misura sulla tavola finita.
- **I giri del revisore sui cinque piani consegnati: zero**, e la prima correzione ha
  **peggiorato su quattro su cinque**. È la misura che ha prodotto D-157: un revisore a mosse
  è un solutore in miniatura. Le cure deterministiche sono dichiarate superate in testa a
  `piano/revisore.py` ed escono in `DRAW-016`.
## Poi il PO ha guardato le tavole, e sono nate cinque decisioni

Il 20 settembre, con due tavole segnate a penna in mano
(`docs/input-pm/riferimenti-grafici/2026-09-20/`):

> «Le tavole fanno schifo… **il disegno nasce dalle linee delle autostrade.** LE AUTOSTRADE
> CON POCHE CURVE e pochi sormonti.» — e poi: «1, 2, 3 vanno quasi bene; **la 4 e la 5 mi
> sembra che non hai minimamente risolto il problema**.»

Da lì **D-159** (il metodo: prima le autostrade, e la quota è quella della porta), **D-160**
(una regola ha una fonte e un controllo, e un controllo fuori dal punteggio non è un
controllo), **D-161** (il piano non può chiedere la forma di una spezzata: può solo liberarle
il posto — la leva che manca è **`passa-per`**), **D-162** (l'occhio guarda e non ricalcola),
**D-163** (un attacco scorre lungo la propria faccia, mai di faccia, mai se è di un
serpentino).

**Che cosa è cambiato nel repository, in quattro righe:**

- **le regole misurate sono nove, non cinque**: alle cinque di `DRAW-015` si aggiungono
  **B8** i sali-scendi, **B9** le corsie libere fra due linee, **B10** mandata sopra e ritorno
  sotto, **B11** la coppia mandata/ritorno corre insieme. Ciascuna con **la propria fonte** e
  **il proprio controllo**, e tutte **dentro il punteggio** (D-160);
- **l'occhio del revisore esiste** — `skill/rivedere/`, provato in camera pulita, e ha trovato
  **due cose che nessun controllo poteva dare** (D-162);
- **gli attacchi si possono far scorrere lungo la propria faccia** (D-163): `gas-boiler` è
  passata da interasse 10 a 15 e la coppia `caldaia ~ disgiuntore` dell'impianto 4 da ZIG-ZAG
  a INSIEME;
- **i cinque piani sono stati corretti guardando le tavole**, e ogni mossa porta nel file la
  regola che la motiva e la misura prima/dopo.

### Le cinque tavole, misurate il 21 settembre

| impianto | tratte | cedute | incroci | rilievi | bloccanti | B1 storte | A4 confini lontani |
|---|---|---|---|---|---|---|---|
| **1** | 21 | **0** | 1 | 14 | 0 | 4 | 4 |
| **2** | 23 | **0** | 2 | 14 | 0 | 3 | 5 |
| **3** | 22 | **0** | 1 | 15 | **1** (B7) | 3 | 5 |
| **4** | 25 | **0** | 3 | 20 | 0 | 5 | 5 |
| **5** | 54 | **0** | 12 | **38** | 0 | **12** | 5 |

L'impianto 5 partiva da **49** rilievi e **14** incroci.
**`RUN_LEAVES_ITS_QUOTA_AND_COMES_BACK` è a zero su tutte e cinque**: i sali-scendi sono
chiusi, ed erano uno dei quattro difetti che il cold eye review aveva trovato il 4 agosto.

### Quello che è stato provato, e non va rifatto

1. **Il difetto è nella fase delle autostrade, non dopo.** L'esperimento l'ha chiesto il PO:
   ridotti il 4 e il 5 a **sole macchine e collettori, senza una valvola**, le autostrade
   restano storte — **5 spezzate piegate sul 4, 11 sul 5**.
2. **I collettori non si possono togliere**: tre pompe in parallelo senza collettore mettono
   tre tubazioni su una porta sola.
3. **L'impianto 4 non può uscire come lo schizzo del PO**: impilata la caldaia sotto la pompa
   di calore a sei quote, 2 non si instradano, 3 peggiorano, 1 pareggia. La topologia è
   diversa — c'è un disgiuntore idraulico in mezzo. **Va detto al PO.**
4. Ruotare il radiatore dell'impianto 1 apre un rilievo bloccante a ogni x provata: **provato
   e scartato**.

- **Quello che ancora non va:** il disegno è una fascia nella metà alta su tutte e cinque
  (D3); le **autostrade del 4 e del 5 sono storte**, ed è la cosa che il PO ha bocciato; e i
  due pezzi che mancano — il **pianificatore** e **l'anello che porta i vincoli dall'occhio a
  chi compone** — sono il pacchetto attivo.
- **A4 è misurata ma non è pulita:** restano 4 rilievi sull'impianto 1 e 5 su ciascuno degli
  altri, il peggiore **+50 mm** (l'acquedotto dell'impianto 3, che entra dal bordo sinistro).
  Sono difetti di composizione, non del controllo, e li chiude il pianificatore.
- **Il censimento di D-158, verificato sul codice vigente** (RAPPORTO §4bis): **A2, A3, B2,
  C1 e C3 non hanno un rilievo sulla tavola finita**. **A3 oggi non è tenuta su da niente** —
  l'unico posto che la faceva valere era il solutore — e **C3 è il buco peggiore**, perché è
  l'unico difetto di **contenuto** che nasce da una scelta **grafica**.
- **Il saldo della suite peggiora di ventuno, ed è dichiarato.** `main` 17 fallite, la
  consegna 38 (**1582** passate, 24 `skip`, 12 `xfail`; zero `skip` e zero `xfail` **nuovi**) — rimisurata il 21 settembre, e **l'insieme delle 38 rosse è identico** a quello del 20.
  È la contropartita di D-151: prove che, per la via ordinaria, pretendevano la qualità che
  il solutore produceva. `DRAW-016` le prende in carico una per una, **senza `skip` e senza
  `xfail`**, e da lì in poi il saldo si misura contro **38**, non contro `main`.
- **Le due PR bocciate e mai chiuse — #32 (`DRAW-010`) e #41 (`DRAW-012`) — sono state
  chiuse**, con il rimando al verdetto agli atti. I rami non sono stati cancellati.

## Chi tocca che cosa, legge prima

- **Chi compone un piano:** `docs/regole-del-piano.md`, **a partire dall'apertura** — «L'ordine
  in cui si compone: prima le autostrade» (D-159) — e poi l'elenco delle regole, ciascuna con
  la propria fonte e il proprio controllo. Le righe marcate `da scrivere` sono lavoro.
- **Chi rivede una tavola:** `skill/rivedere/ISTRUZIONI.md`, e la prima riga è che **non si
  ricalcola** (D-162): i numeri li hanno già misurati i controlli.
- **Chi vuole capire che cosa il PO boccia:** `docs/input-pm/riferimenti-grafici/2026-09-20/`,
  le due tavole che ha segnato a penna, col suo messaggio riportato per intero e la mappa di
  che cosa è uscito da ogni segno.
- **Chi tocca il disegno:** `docs/ARCHITETTURA-DEL-PIANO.md`, e la ricerca del 4 agosto
  `docs/fonti/2026-08-04-come-si-disegna-uno-schema-funzionale.md`.
- **Chi tocca il motore** (non il piano): `docs/pm/2026-09-11-architettura-della-posa-a-fasi.md`
  e `docs/pm/2026-09-16-come-ragiona-il-motore-e-come-dovrebbe.md`, sapendo che le parti sul
  **solutore** sono storia — e che quei due documenti **non lo dichiarano ancora in testa**.
- Stato e rischi: `PROJECT_STATE.md`. Roadmap: `docs/plans/2026-09-03-release-plan.md`.
  Architettura della skill: `docs/SKILL.md`. Input del PO: `docs/input-pm/REGISTRO.md`.

## Contratti da non violare

- un attacco porta una sola tubazione; ogni unione o diramazione è un raccordo nel grafo;
- il contenuto si giudica sul grafo, il disegno sulla tavola;
- **il piano dice dove stanno i pezzi, e nient'altro**: quello che si può **dedurre** — la
  rotazione di un raccordo, quella di un pezzo con un attacco solo, la mappa degli attacchi —
  si deduce dai vicini che il pezzo ha davvero. La deduzione vince sempre sulla ricerca;
- **la mappa degli attacchi si rifà solo per i raccordi** (D-004, I-027). Rifarla su una
  macchina è un **errore di contenuto**;
- **una correzione del revisore senza il nome di una regola non si fa**: sarebbe il solutore
  travestito;
- **una catena già nella propria forma non si smonta** per aggiustarne un'altra;
- spostare macchine e accessori non costa; backtracking, curve e incroci sì. **La lunghezza
  no** (D-139) e **il riempimento nemmeno** (D-149);
- testi e richiami vengono dopo e non influenzano posa o routing;
- nessun requisito MEP nasce dal codice, da un'immagine di esempio o dall'iniziativa
  dell'agente;
- ogni input del PO viene registrato e resta aperto finché il PO non lo chiude o ritira;
- **si consegna tramite PR, e si fonde solo col sì del PO sulle tavole** (D-147);
- **ogni consegna porta le tavole prodotte, in PDF, elencate in testa al rapporto** (D-146).
  Non è una buona pratica: è la porta della fusione.

## Domande aperte al PO — in ordine di quanto bloccano

> **Due domande che erano qui sono state chiuse dal PO il 21 settembre, e chi le ripropone
> perde un giro.** **Le convenzioni grafiche** (I-097) → **D-165**: «la convenzione grafica è
> quella che abbiamo sviluppato fino adesso e **non si tocca**». **Quante autostrade verticali**
> (I-098) → **D-164**: «**non c'è un numero**… il criterio è **grafico, non matematico**».

0. **La parola «solutore»** (I-100). Il PO chiede di «**aggiornare il solutore** in modo che il
   tutto funzioni», e nei nostri documenti quella parola indica la **ricerca abolita da
   D-151**. `DRAW-016` è stato scritto leggendo **«il motore che instrada e disegna»** (pezzo
   4, `layout/`), perché è la parte che disegna davvero e perché far tornare la ricerca
   contraddirebbe una decisione che il PO stesso ha approvato. *Se la lettura è sbagliata va
   corretta prima di toccare il motore*, e in ogni caso **la ricerca non torna**.
1. **B7 — due porte che guardano dalla stessa parte non si uniscono con un segmento.**
   **Metà chiusa** il 22 settembre (**D-171**): `turns_allowed` non esiste più, e il bilancio
   è diventato **il minimo raggiungibile** date le facce — era la seconda delle due letture,
   quella di codice. **Resta la prima, ed è materia MEP:** una macchina con due attacchi sullo
   stesso lato è un **simbolo** o un **vincolo idraulico**? Finché il PO non lo dice, quelle
   pieghe restano e non sono un difetto.
2. ~~**B1 e B3 si contraddicono sulla cascata.**~~ **Chiusa dal PO il 22 settembre**
   (**D-171**): «non c'è un numero massimo». Il collettore verticale che B3 pretende ha il
   proprio pavimento a **due**, e B1 non lo accusa più.
3. **Dove sta la presa del ricircolo sanitario.** Il confine ACS adesso sta addosso alla
   presa (A4, chiuso), ma sull'impianto 5 **la presa sta all'estremo destro del foglio** e la
   mandata sanitaria attraversa da sola i tre secondari per arrivarci: è lì che stanno quasi
   tutti i quattordici incroci di quella tavola. *O la presa sta in fondo all'anello e la
   linea lunga è vera, o è un nodo che il disegno può avvicinare al bollitore.* Contenuto MEP.
   — *La domanda precedente, «dove sta un confine di rete», l'ha chiusa il PO il 20 settembre:
   «si fa lì accanto facendo un tratto piccolo di tubazione». È A4, ed è un controllo.*
3bis. **Il verso del ricircolo ACS non si ricava** (D-059): la mandata e il ritorno del
   ricircolo portano **tutt'e due `supply=True`**, e per questo **B10 non vede** il ritorno
   che corre sopra la propria mandata per 265 mm sull'impianto 5. L'ha trovato l'occhio del
   revisore, non un controllo. *Serve sapere se il ricircolo è una rete con un verso, o due
   tratte della stessa.* Contenuto MEP.
4. **Quando si apre il pacchetto DXF.** La riproducibilità (D-023) e il vincolo dell'A3
   (D-148) sono stati lasciati andare **perché** l'elaborato esce in DXF e si rifinisce in
   CAD. Quel pezzo non esiste.
5. **Il formato definitivo** (D-148 è dichiarata momentanea dal PO stesso).

## Quello che è cambiato di prezzo, e va saputo

**La riproducibilità bit-per-bit se ne va** (D-023, sospesa da D-151). Il motore non
garantisce più che il disegno sia **bello** — garantisce che sia **valido** e che i difetti
siano **nominati**. Il bello lo porta il piano, e il giudizio resta del PO, sulle tavole.

**Senza un piano, la via ordinaria è peggiorata, ed è dichiarato.** Misurato sui cinque
impianti: senza il solutore e senza un piano finiscono tutti sul formato più grande col
ripiego, con 2–6 tratte cedute ciascuno. È la ragione per cui i piani si scrivono.

La storia precedente resta disponibile in Git. Non va caricata integralmente in ogni
sessione: si consulta solo quando un documento corrente rinvia a una decisione specifica.
