# HANDOFF — Disegnatore MEP

**Aggiornato:** 2026-09-18
**Scopo:** ingresso operativo breve per una nuova sessione DEV.

## Prodotto

Costruiamo una **skill/tool da installare e usare nelle chat di lavoro**. L'ingegnere
descrive un impianto già progettato e dimensionato; la skill lo interpreta, espone
assunzioni e integrazioni, ottiene l'approvazione dell'ingegnere e genera una tavola MEP
vettoriale, deterministica e verificabile.

Claude è il team di sviluppo del repository, non il runtime finale del prodotto.
L'eseguibilità reale della skill in una chat pulita deve essere collaudata prima della
generalizzazione agli impianti 2–5.

## Catena invariabile

1. l'AI interpreta la conversazione e produce il grafo di prima stesura;
2. il motore deterministico completa e ordina gli accessori;
3. il PO approva il grafo definitivo;
4. il motore deterministico dispone, instrada e disegna;
5. validatori deterministici e occhio terzo AI verificano;
6. la chat restituisce la tavola e i rilievi.

Una sola cosa attraversa la catena: **il grafo dell'impianto**. La tavola è una sua vista.
L'AI non modifica direttamente coordinate o connettività approvata.

## Autorità

- **PO — Daniel Carta:** dominio MEP, requisiti, convenzioni grafiche, priorità e giudizio
  finale del prodotto.
- **PM — Claude, uno solo** (D-130, 14 settembre 2026): pacchetti, criteri di
  accettazione, fonti, traduzione degli input del PO, roadmap, documentazione corrente;
  verifica della consegna **criterio per criterio**; merge su `main`, solo tramite pull
  request. Non approva i propri pacchetti al posto del PO: li sottopone prima che il lavoro
  cominci. Lo sdoppiamento in PM-autore e PM-revisore, disposto il 10 settembre, è abolito.

  **Ciò che resta separato è che il PM non è il DEV.** Le regole con cui il PM verifica —
  prima le misure e poi il racconto del DEV, ogni criterio chiuso con un comando e il suo
  output, la suite riletta per intero — stanno in `OPERATING_MODEL.md` §1.2.1.

- **DEV — Claude, in una sessione diversa dal PM:** implementazione, test, artefatti e
  proposte tecniche reversibili dentro il Work Package. Non deduce requisiti dagli esempi e
  non decide regole MEP.

## Se sei il PM

Il tuo documento d'ingresso è **`docs/pm/STATO-PM.md`**: stato di fatto, fili aperti,
incoerenze note, igiene di git e che cosa fare appena subentri. Leggi quello e sei operativo.

## Ordine di lettura DEV

1. `CLAUDE.md`;
2. `ACTIVE_WORK_PACKAGE.md`;
3. questo file;
4. soltanto i documenti indicati dal Work Package.

`ACTIVE_WORK_PACKAGE.md` è l'unico incarico operativo. Se manca, è già consegnato, è
ambiguo o contrasta con `main`, il DEV si ferma e riferisce al PM.

## Stato corrente

- Release in corso: **0.3 — generalizzazione, impianto 2**. (Il numero di versione
  Python resta `0.1.0`: non ha mai seguito le release dichiarate.)
- `DRAW-005` è stato verificato e fuso nella PR #18: tavola 1 con 4 curve, 1 incrocio,
  525 mm, zero backtracking; simboli e contenuto critici corretti.
- `DRAW-005-R1` è stato fuso con la PR #21; `DRAW-006` e `DRAW-006-R1` con la PR #24.
- `DRAW-007` e `DRAW-008` sono stati fusi su `main`. `DRAW-008` — la posa a fasi — ha
  riportato in tavola l'impianto 2 e ha consegnato con **tre regressioni dichiarate** e due
  criteri irraggiungibili alla lettera: `docs/collaudi/DRAW-008/RAPPORTO.md` §6 e §7. Una
  delle tre regressioni il PO l'ha già chiusa per decisione (l'ordine delle due zone è
  indifferente); le altre due sono voci di `DRAW-009`.
- `DRAW-009` è stato **verificato dal PM e fuso** il 14 settembre con la PR #27
  (`2155c22`): dodici criteri raggiunti, quattro raggiunti in parte, nessuno non raggiunto.
  Verdetto in `docs/pm/2026-09-14-review-pr27-draw009.md`. **Dopo il merge** si è scoperto
  che l'impianto 4 non produce più una tavola: §7 del verdetto, e primo criterio del
  pacchetto nuovo.
- **`DRAW-010` è stato consegnato con la PR #32 e respinto dal PM** il 15 settembre; il suo
  lavoro non è su `main`. Verdetto in `docs/pm/2026-09-15-review-pr32-draw010.md`.
- **`DRAW-012` è stato consegnato con la PR #41 e respinto dal PM** il 18 settembre. Tredici
  criteri su sedici, nessuno barato, rapporto onesto — ma **il PO ha guardato le tavole e ha
  detto che erano meglio prima**: il riempimento era stato comprato allungando i singoli
  tratti, e il disegno arrivava quasi al bordo del foglio. Verdetto in
  `docs/pm/2026-09-18-review-pr41-draw012.md`. Ne sono nate **D-142** (la tavola si allarga
  tutta insieme, in proporzione) e **D-143** (il disegno non tocca il bordo; margine
  variabile). **Il suo lavoro non va rifatto**: la struttura, le autostrade e l'invariante
  della catena intera restano validi.
- Il pacchetto attivo è **`DRAW-013`** (`ACTIVE_WORK_PACKAGE.md`), in **bozza da approvare
  dal PO**: la tavola si allarga tutta insieme e non tocca il bordo. **Parte dal ramo di
  `DRAW-012`** (`claude/hopeful-ramanujan-9bs0cb`, `17ff425`), non dalla testa di `main`.
- **Chi tocca la posa legge prima l'analisi del 16 settembre**,
  `docs/pm/2026-09-16-come-ragiona-il-motore-e-come-dovrebbe.md`: le cinque differenze
  misurate fra l'ordine del disegnatore e quello del motore.
- **Chi tocca posa, costo o routing legge prima due documenti**, in quest'ordine:
  `docs/pm/2026-09-11-architettura-della-posa-a-fasi.md` — l'ordine delle decisioni che il
  PO ha fissato: prima le autostrade e dritte, poi il corredo con lo stretch invece della
  piega, poi le strade di servizio — e
  `docs/retrospectives/2026-09-10-retro-draw006r1.md`, che dice come ci siamo arrivati
  (input I-057, I-058, I-061, I-062, I-063).
- Stato e rischi: `PROJECT_STATE.md`.
- Roadmap: `docs/plans/2026-09-03-release-plan.md`.
- Architettura: `docs/SKILL.md` e ADR 0005.
- Input del PO: `docs/input-pm/REGISTRO.md`.

## Contratti da non violare

- un attacco porta una sola tubazione; ogni unione o diramazione è un raccordo nel grafo;
- il contenuto si giudica sul grafo, il disegno sulla tavola;
- spostare macchine e accessori non costa; backtracking, curve, incroci e lunghezza sì;
- testi e richiami vengono dopo e non influenzano posa o routing;
- nessun requisito MEP nasce dal codice, da un'immagine di esempio o dall'iniziativa DEV;
- ogni input del PO viene registrato e resta aperto finché il PO non lo chiude o ritira;
- il DEV apre la PR e si ferma; il PM revisiona e fonde.

La storia precedente resta disponibile in Git. Non va caricata integralmente in ogni
sessione: si consulta solo quando un documento corrente rinvia a una decisione specifica.
