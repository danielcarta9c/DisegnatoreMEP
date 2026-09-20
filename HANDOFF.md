# HANDOFF — Disegnatore MEP

**Aggiornato:** 2026-09-20, alla consegna di `DRAW-015`
**Scopo:** ingresso operativo breve per una nuova sessione.

> **Il 20 settembre il progetto ha cambiato architettura, e `DRAW-015` l'ha costruita.** Se
> leggi una cosa sola oltre a questa pagina, leggi `docs/ARCHITETTURA-DEL-PIANO.md`: dice chi
> decide cosa, e la divisione che ne esce è anche il modo in cui si legge ogni difetto.

## Prodotto

Costruiamo una **skill/tool da installare e usare nelle chat di lavoro**. L'ingegnere
descrive un impianto già progettato e dimensionato; la skill lo interpreta, espone
assunzioni e integrazioni, ottiene l'approvazione dell'ingegnere e genera una tavola MEP
vettoriale e verificabile — in PDF e in **DXF**, che il disegnatore apre in AutoCAD e
rifinisce (I-072). **Il DXF non è ancora scritto**, ed è la contropartita di un prezzo già
pagato: vedi *Domande aperte*.

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

**I passi 4-6 sono costruiti** (`DRAW-015`), e si guidano dalla CLI:

```
disegnatore-mep rules   <progetto.json> … --apply-all --out <completo.json>
disegnatore-mep piano   <completo.json> --piano <piano.json> … --out <cartella>
disegnatore-mep revisiona <completo.json> --piano <piano.json> … --out <cartella>
```

I cinque piani stanno in `docs/collaudi/PROVA-PIANO/impianto-N.json`, e
`scripts/tavole-dal-piano.sh` li esegue tutti in un colpo.

⚠ **Il piano si esegue sul progetto nella forma che `rules --apply-all --out` scrive.** La
forma canonica riordina i componenti per identificativo, la posa di partenza legge
quell'ordine (`place.py::_file_order`), e l'impianto 5 si instrada su quello e non su un
altro.

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
- **Quello che ancora non va, misurato e dichiarato:** il disegno è una fascia nella metà
  alta su tutte e cinque (D3), e i **confini di rete finiscono lontanissimi** dal pezzo che
  servono — a occhio è la cosa più brutta di queste tavole.
- **I giri del revisore sui cinque piani consegnati: zero.** Non è un difetto del revisore:
  i piani sono stati composti con le regole in mano, e quello che resta sono le violazioni
  strutturali di B7, che nessuno spostamento chiude. Su un piano guastato apposta l'anello
  gira e migliora in un giro.
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
