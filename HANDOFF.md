# HANDOFF — Disegnatore MEP

**Aggiornato:** 2026-09-08
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
- **PM — Codex:** ricerca e verifica delle fonti, traduzione degli input PO, roadmap,
  Work Package, criteri di accettazione, revisione, documentazione corrente e merge.
- **DEV — Claude:** implementazione, test, artefatti e proposte tecniche reversibili
  dentro il Work Package. Non deduce requisiti dagli esempi e non decide regole MEP.

## Ordine di lettura DEV

1. `CLAUDE.md`;
2. `ACTIVE_WORK_PACKAGE.md`;
3. questo file;
4. soltanto i documenti indicati dal Work Package.

`ACTIVE_WORK_PACKAGE.md` è l'unico incarico operativo. Se manca, è già consegnato, è
ambiguo o contrasta con `main`, il DEV si ferma e riferisce al PM.

## Stato corrente

- Release in corso: **0.2 — prima tavola tecnicamente corretta e approvata**.
- `DRAW-005` è stato verificato e fuso nella PR #18: tavola 1 con 4 curve, 1 incrocio,
  525 mm, zero backtracking; simboli e contenuto critici corretti.
- Il PO ha approvato l'impostazione generale e ha richiesto le rifiniture raccolte in
  `DRAW-005-R1`, ora unico incarico DEV attivo.
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
