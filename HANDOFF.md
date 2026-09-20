# HANDOFF — Disegnatore MEP

**Aggiornato:** 2026-09-20
**Scopo:** ingresso operativo breve per una nuova sessione.

> **Il 20 settembre il progetto ha cambiato architettura.** Se leggi una cosa sola oltre a
> questa pagina, leggi `docs/ARCHITETTURA-DEL-PIANO.md`: dice chi decide cosa, e la
> divisione che ne esce è anche il modo in cui si legge ogni difetto.

## Prodotto

Costruiamo una **skill/tool da installare e usare nelle chat di lavoro**. L'ingegnere
descrive un impianto già progettato e dimensionato; la skill lo interpreta, espone
assunzioni e integrazioni, ottiene l'approvazione dell'ingegnere e genera una tavola MEP
vettoriale e verificabile — in PDF e in **DXF**, che il disegnatore apre in AutoCAD e
rifinisce (I-072).

Claude è il team di sviluppo del repository **e**, da D-151, una parte del prodotto: il
disegno lo **compone un agente**.

## Catena invariabile

1. l'AI interpreta la conversazione e produce il grafo di prima stesura;
2. il motore deterministico completa e ordina gli accessori;
3. il PO approva il grafo definitivo;
4. **il pianificatore compone** — un piano che dice soltanto **dove stanno i pezzi**;
5. **il motore esegue e misura** — orienta, instrada, interrompe, impagina, disegna, valida;
6. **il revisore rilegge i rilievi e corregge il piano**, finché non ne resta uno bloccante;
7. la chat restituisce la tavola e i rilievi.

Una sola cosa attraversa la catena: **il grafo dell'impianto**. La tavola è una sua vista.
L'agente non modifica connettività approvata: sposta pezzi, non collega pezzi.

**I passi 4-6 sono nuovi (D-151) e sostituiscono il solutore.** `improve.py` e la fase del
tronco non decidono più la posa. Restano agli atti, non cancellati.

## Autorità — **un agente solo** (D-147), con agenti paralleli in sessione (D-152)

- **PO — Daniel Carta:** dominio MEP, requisiti, convenzioni grafiche, priorità, giudizio
  finale del prodotto, e **l'approvazione della fusione**.
- **L'agente — Claude, PM e DEV nella stessa sessione:** scrive il pacchetto, sviluppa,
  misura, mostra le tavole, e fonde **solo dopo il sì del PO**. Nella stessa sessione scrive
  `HANDOFF.md` e il pacchetto successivo.
- **Agenti paralleli:** si lanciano **dentro** la sessione, con un perimetro dichiarato prima
  — un file o una coda. Non consegnano, non fondono, non chiudono niente, e quello che
  riferiscono non è una misura finché la sessione non l'ha rieseguito
  (`OPERATING_MODEL.md` §1.2.2).

Lo sdoppiamento PM/DEV in **due sessioni** è abolito: §1.2.1 dice perché, con la misura che
l'ha motivato. I confini di §1.1.1 valgono intatti, e **una disposizione del PO si implementa
come è espressa**.

**Il controllo è uno: il PO guarda le tavole.** Senza tavole non c'è niente da approvare, e
senza approvazione non si fonde.

## Stato corrente

- Release in corso: **0.3 — generalizzazione**. (Il numero di versione Python resta
  `0.1.0`: non ha mai seguito le release dichiarate.)
- **`DRAW-014` non si chiude come previsto**: è stato superato in corsa. Ha fatto uscire le
  cinque tavole (D-148, D-150), e proprio guardandole il PO ha fermato la linea del solutore.
  Quello che di `DRAW-014` resta vivo è in `main` col ramo corrente; quello che resta
  incompiuto è nominato qui sotto.
- **Sei disposizioni del PO fra il 19 e il 20 settembre** hanno cambiato la rotta, e sono
  `D-147`–`D-152`:
  - **D-147** — agente unico; **D-152** — agenti paralleli in sessione, mai sessioni;
  - **D-148** — **oltre l'A3 si va**: i formati ordinari sono A4, A3, A2, A1. Dichiarata
    momentanea dal PO stesso;
  - **D-149** — **il riempimento del foglio esce dagli obiettivi** e torna una misura; la
    dilatazione di D-142 è ritirata (`layout/dilate.py` resta agli atti);
  - **D-150** — **una tratta che non si instrada non uccide più la tavola**: ripiego
    dichiarato, marcato `unresolved`, nominato dal preflight con un rilievo bloccante;
  - **D-151** — **il disegno lo compone un agente, non lo trova un solutore.** È la
    decisione che governa tutto il resto.
- **La prova che ha deciso D-151** è in `docs/collaudi/PROVA-PIANO/`: impianto 1 e impianto 5
  composti a mano ed eseguiti dal motore, **zero rilievi bloccanti e zero tratte cedute**,
  con un giro da **~30 secondi** contro i **10–40 minuti** del solutore.
- **Quello che la prova non dimostra, e il PO l'ha detto:** che le tavole siano belle. «C'è
  molto da migliorare ancora, non assomiglia a come dovrebbe essere un disegno» (I-082).
  Resta storto, misurato: il disegno è una **fascia nella metà alta** del foglio, nessuno
  distribuisce in verticale; l'impianto 5 ha **quattordici incroci**.
- **Chi tocca il disegno legge prima**: `docs/ARCHITETTURA-DEL-PIANO.md`, e la ricerca del
  4 agosto `docs/fonti/2026-08-04-come-si-disegna-uno-schema-funzionale.md`, che è il
  documento che aveva già detto tutto e che il progetto non ha attuato per sei settimane.
- **Chi tocca il motore** (non il piano) legge `docs/pm/2026-09-11-architettura-della-posa-a-fasi.md`
  e `docs/pm/2026-09-16-come-ragiona-il-motore-e-come-dovrebbe.md`, sapendo che le parti sul
  **solutore** sono storia.
- Stato e rischi: `PROJECT_STATE.md`. Roadmap: `docs/plans/2026-09-03-release-plan.md`.
  Architettura della skill: `docs/SKILL.md` e ADR 0005 — **da riallineare, è il pacchetto
  attivo**. Input del PO: `docs/input-pm/REGISTRO.md`.

## Contratti da non violare

- un attacco porta una sola tubazione; ogni unione o diramazione è un raccordo nel grafo;
- il contenuto si giudica sul grafo, il disegno sulla tavola;
- **il piano dice dove stanno i pezzi, e nient'altro**: quello che si può **dedurre** — la
  rotazione di un raccordo, quella di un pezzo con un attacco solo, la mappa degli attacchi —
  si deduce dai vicini che il pezzo ha davvero. La deduzione vince sempre sulla ricerca;
- **la mappa degli attacchi si rifà solo per i raccordi** (D-004, I-027). Rifarla su una
  macchina è un **errore di contenuto**: il 20 settembre ha mandato l'acqua fredda
  sull'uscita primaria dell'accumulo, e l'ha visto il PO, non una misura;
- spostare macchine e accessori non costa; backtracking, curve e incroci sì. **La lunghezza
  no** (D-139) e **il riempimento nemmeno** (D-149): si riportano come misure. Ciò che tiene
  un organo di servizio vicino al pezzo che serve è un **vincolo**, non un costo (D-145);
- testi e richiami vengono dopo e non influenzano posa o routing;
- nessun requisito MEP nasce dal codice, da un'immagine di esempio o dall'iniziativa
  dell'agente;
- ogni input del PO viene registrato e resta aperto finché il PO non lo chiude o ritira;
- **si consegna tramite PR, e si fonde solo col sì del PO sulle tavole** (D-147);
- **ogni consegna porta le tavole prodotte, in PDF, elencate in testa al rapporto** — e per
  ogni impianto che non ne produce una, il rapporto lo dice e dice dove si ferma (D-146).
  Non è una buona pratica: è la porta della fusione.

## Quello che è cambiato di prezzo, e va saputo

**La riproducibilità bit-per-bit se ne va** (D-023, sospesa da D-151): due composizioni dello
stesso impianto non danno la stessa tavola. Il motore non garantisce più che il disegno sia
**bello** — garantisce che sia **valido** e che i difetti siano **nominati**. Il bello lo
porta il piano, e il giudizio resta del PO, sulle tavole (D-146).

La storia precedente resta disponibile in Git. Non va caricata integralmente in ogni
sessione: si consulta solo quando un documento corrente rinvia a una decisione specifica.
