# HANDOFF — Disegnatore MEP

**Aggiornato:** 2026-09-20, alla consegna di `DRAW-015`
**Scopo:** ingresso operativo breve per una nuova sessione.

> **Se leggi una cosa sola oltre a questa pagina, leggi `docs/ARCHITETTURA-DEL-PIANO.md`.**
> Dice **quali sono i cinque pezzi della skill**, **di che pasta è fatto ciascuno** — agente
> AI, deterministico, o misto — e **che cosa passa fra l'uno e l'altro**.
>
> È stato riscritto il 20 settembre perché una sessione ha sbagliato lo sviluppo pur avendo
> tutte le decisioni sotto gli occhi: ha trattato il **piano** come un artefatto da
> consegnare invece che come qualcosa che la skill deve **imparare a scrivere**.

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
| **5** | **Rivedere** — dalla tavola ai **vincoli** per il pezzo 3 | **AI + controlli** | **a metà**: i controlli ci sono, l'occhio no |

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
  stati quattro, e ha funzionato: §11 del rapporto dice chi ha fatto che cosa.

**Il controllo è uno: il PO guarda le tavole.** Senza tavole non c'è niente da approvare, e
senza approvazione non si fonde.

## Stato corrente

- Release in corso: **0.3 — generalizzazione**.
- **`DRAW-015` consegnato**, rapporto in `docs/collaudi/DRAW-015/RAPPORTO.md`. Che cosa
  porta, in quattro righe:
  - **il revisore esiste** (`piano/revisore.py`): esegue il piano, misura, corregge il piano
    nominando **la regola** di ogni correzione, e si ferma dicendo perché — compreso quando
    un giro peggiora, e allora consegna il precedente;
  - **le quattro regole del PO sono quattro controlli** (`validation/regole.py`): A1 le tre
    fasce, B1 le autostrade dritte, B3 il collettore verticale, B4 l'organo in linea;
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
  **D-145 vive nella posa del motore e il piano la sovrascrive**. Corretto: adesso stanno fra
  **17,5 e 50 mm**. Da qui D-158.
- **I giri del revisore sui cinque piani consegnati: zero**, e la prima correzione ha
  **peggiorato su quattro su cinque**. È la misura che ha prodotto D-157: un revisore a mosse
  è un solutore in miniatura. Le cure deterministiche sono dichiarate superate in testa a
  `piano/revisore.py` ed escono in `DRAW-016`.
- **Quello che ancora non va:** il disegno è una fascia nella metà alta su tutte e cinque
  (D3), e i due pezzi di skill che mancano — il **pianificatore** e **l'occhio del
  revisore** — sono il pacchetto attivo.
- **Le due PR bocciate e mai chiuse — #32 (`DRAW-010`) e #41 (`DRAW-012`) — sono state
  chiuse**, con il rimando al verdetto agli atti. I rami non sono stati cancellati.

## Chi tocca che cosa, legge prima

- **Chi compone un piano:** `docs/regole-del-piano.md` — l'elenco delle regole, ciascuna con
  la propria fonte e il proprio controllo. Le righe marcate `da scrivere` sono lavoro.
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

1. **B7 — due porte che guardano dalla stessa parte non si uniscono con un segmento.**
   `Highway.turns_allowed` vale zero per ogni catena fra macchine di spina senza guardare se
   le facce delle porte lo permettono. Quattro catene su tre impianti non si possono
   raddrizzare, e una di loro è **l'unico rilievo bloccante** che resta. *O il catalogo
   cambia, o `turns_allowed` diventa il minimo raggiungibile.* La prima è materia MEP.
2. **B1 e B3 si contraddicono sulla cascata.** Il collettore verticale che B3 pretende fa
   piegare la catena che B1 vuole dritta: **la tavola è giusta e il numero dice che è
   sbagliata.** Come si scrive «il più possibile».
3. **Dove sta un confine di rete.** A1 lo esclude dal conto delle fasce perché «va accanto
   all'utente che serve» (I-061), ma nessuna riga dice dove metterlo, e nei cinque piani
   finisce lontanissimo. È la cosa più brutta che si vede sulle tavole.
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
