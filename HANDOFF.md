# HANDOFF — Disegnatore MEP

**Aggiornato:** 2026-09-19
**Scopo:** ingresso operativo breve per una nuova sessione.

## Prodotto

Costruiamo una **skill/tool da installare e usare nelle chat di lavoro**. L'ingegnere
descrive un impianto già progettato e dimensionato; la skill lo interpreta, espone
assunzioni e integrazioni, ottiene l'approvazione dell'ingegnere e genera una tavola MEP
vettoriale, deterministica e verificabile — in PDF e in **DXF**, che il disegnatore apre in
AutoCAD e rifinisce (I-072).

Claude è il team di sviluppo del repository, non il runtime finale del prodotto.

## Catena invariabile

1. l'AI interpreta la conversazione e produce il grafo di prima stesura;
2. il motore deterministico completa e ordina gli accessori;
3. il PO approva il grafo definitivo;
4. il motore deterministico dispone, instrada e disegna;
5. validatori deterministici e occhio terzo AI verificano;
6. la chat restituisce la tavola e i rilievi.

Una sola cosa attraversa la catena: **il grafo dell'impianto**. La tavola è una sua vista.
L'AI non modifica direttamente coordinate o connettività approvata.

## Autorità — **un agente solo** (D-147, 19 settembre 2026)

- **PO — Daniel Carta:** dominio MEP, requisiti, convenzioni grafiche, priorità, giudizio
  finale del prodotto, e **l'approvazione della fusione**.
- **L'agente — Claude, PM e DEV nella stessa sessione:** scrive il pacchetto, sviluppa,
  misura, mostra le tavole, e fonde **solo dopo il sì del PO**. Nella stessa sessione scrive
  `HANDOFF.md` e il pacchetto successivo.

Lo sdoppiamento PM/DEV in due sessioni è **abolito**: `docs/governance/OPERATING_MODEL.md`
§1.2.1 dice perché, con la misura che l'ha motivato. Non è cambiato il mestiere, è cambiato
chi lo fa: i confini di §1.1.1 valgono intatti, e **una disposizione del PO si implementa
come è espressa**.

**Il controllo è uno: il PO guarda le tavole.** Senza tavole non c'è niente da approvare, e
senza approvazione non si fonde.

## Stato corrente

- Release in corso: **0.3 — generalizzazione**. (Il numero di versione Python resta
  `0.1.0`: non ha mai seguito le release dichiarate.)
- **`DRAW-013` è stato fuso il 19 settembre con la PR #44.** Undici criteri su quindici;
  i quattro mancanti erano tutti bloccati da `place.py` e dalle rotazioni del simbolo del
  collettore, cioè da un perimetro che aveva scritto il PM. Verdetto nel corpo della PR.
  Restano validi: il margine di 25 mm dal bordo (D-143), le autostrade e l'invariante della
  catena (`DRAW-012`), il vincolo degli organi di servizio (D-145).
- **Quattro disposizioni del PO del 19 settembre** hanno cambiato la rotta, e sono
  `D-147`–`D-150`:
  - **D-147** — agente unico (sopra);
  - **D-148** — **oltre l'A3 si va**: i formati ordinari sono A4, A3, A2, A1. Misurato: le
    tre tavole che non uscivano fallivano tutte **contro il bordo destro dell'area A3**;
  - **D-149** — **il riempimento del foglio esce dagli obiettivi** e torna una misura; la
    dilatazione di D-142 è ritirata (`layout/dilate.py` resta agli atti, non cancellato).
    Restano lo stiramento per far entrare il corredo, e il margine di D-143;
  - **D-150** — **una tratta che non si instrada non uccide più la tavola**: prende una
    spezzata di ripiego, si marca `unresolved`, e il preflight la nomina con un rilievo
    bloccante. La tavola esce **marcata**: si guarda e si rifinisce in CAD, non si consegna.
- **Chi tocca la posa legge prima l'analisi del 16 settembre**,
  `docs/pm/2026-09-16-come-ragiona-il-motore-e-come-dovrebbe.md`.
- **Chi tocca posa, costo o routing legge prima**
  `docs/pm/2026-09-11-architettura-della-posa-a-fasi.md` e
  `docs/retrospectives/2026-09-10-retro-draw006r1.md`.
- Stato e rischi: `PROJECT_STATE.md`. Roadmap: `docs/plans/2026-09-03-release-plan.md`.
  Architettura: `docs/SKILL.md` e ADR 0005. Input del PO: `docs/input-pm/REGISTRO.md`.

## Contratti da non violare

- un attacco porta una sola tubazione; ogni unione o diramazione è un raccordo nel grafo;
- il contenuto si giudica sul grafo, il disegno sulla tavola;
- spostare macchine e accessori non costa; backtracking, curve e incroci sì. **La lunghezza
  no** (D-139) e **il riempimento nemmeno** (D-149): si riportano come misure e non come
  giudizi. Ciò che tiene un organo di servizio vicino al pezzo che serve è un **vincolo**,
  non un costo (D-145);
- testi e richiami vengono dopo e non influenzano posa o routing;
- nessun requisito MEP nasce dal codice, da un'immagine di esempio o dall'iniziativa
  dell'agente;
- ogni input del PO viene registrato e resta aperto finché il PO non lo chiude o ritira;
- **si consegna tramite PR, e si fonde solo col sì del PO sulle tavole** (D-147);
- **ogni consegna porta le tavole prodotte, in PDF, elencate in testa al rapporto** — e per
  ogni impianto che non ne produce una, il rapporto lo dice e dice dove si ferma (D-146).
  Non è più una buona pratica: è la porta della fusione.

La storia precedente resta disponibile in Git. Non va caricata integralmente in ogni
sessione: si consulta solo quando un documento corrente rinvia a una decisione specifica.
