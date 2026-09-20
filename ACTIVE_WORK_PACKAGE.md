# DRAW-015 — Il repository segue l'architettura del piano

**Titolo:** Il repository segue l'architettura del piano
**Scritto e svolto da:** l'agente unico (**D-147**), che può lanciare agenti paralleli in
sessione (**D-152**, `docs/governance/OPERATING_MODEL.md` §1.2.2)
**Data:** 2026-09-20
**Stato:** **ATTIVO.** Sostituisce `DRAW-014`, superato in corsa da D-151
**Release:** 0.3 — generalizzazione
**Approvazione della fusione:** **del PO**, e si dà guardando le tavole (D-147, D-146)

> **Questo pacchetto non migliora nessuna tavola, e non deve provarci.** Mette il
> repository nella forma che l'architettura nuova richiede, e si giudica su una cosa sola:
> **le tavole che uscivano prima escono anche dopo, identiche o migliori.** Una
> ristrutturazione che perde una tavola è fallita, per bella che sia.

---

## Perché

Il PO, il 20 settembre, approvando l'architettura:

> «Approviamo questa nuova architettura della skill… dobbiamo preparare un hand off per la
> prossima sessione che sarà prettamente di ristrutturazione di tutto il materiale che
> abbiamo in git per sistemare tutto con la nuova architettura di skill e nuova impostazione
> di project management.»

Oggi il repository descrive un prodotto che non esiste più. `docs/SKILL.md` e l'ADR 0005
raccontano un solutore che minimizza una somma pesata; il pezzo che ha prodotto le due
tavole buone è uno **script di prova**, `scripts/piano.py`, dentro una cartella di collaudo;
e trentasei prove in `tests/layout/` difendono comportamenti di cui una parte è stata
revocata. Chi apre la prossima sessione, leggendo il repository, ricostruirebbe il solutore.

## Le due disposizioni che lo governano

| | |
|---|---|
| **D-151** | Il disegno lo compone un agente: pianificatore → motore → revisore. Il solutore esce dalla catena e resta agli atti |
| **D-152** | Due agenti paralleli dentro la sessione, mai due sessioni. Perimetro dichiarato prima, un file o una coda |

Il documento da cui si parte è `docs/ARCHITETTURA-DEL-PIANO.md`, che è **vigente**.

## Le cinque cose da fare

### 1. Il piano diventa un pezzo del prodotto

`scripts/piano.py` esce dagli script e diventa codice: un **formato del piano** dichiarato
(modello `pydantic`, come tutto il resto), un **esecutore**, e un comando della CLI. Il
formato è quello che la prova ha già usato — `formato`, `pezzi: {id: {x, y}}` — più le note,
che sono parte del piano e non un commento: dicono **quale regola** ha messo il pezzo lì.

**Il piano non contiene ciò che si deduce.** La rotazione di un raccordo, quella di un pezzo
con un attacco solo e la mappa degli attacchi si calcolano dai vicini
(`ARCHITETTURA-DEL-PIANO.md` §4). L'unica eccezione nota è **un pezzo con due attacchi che
non è una macchina** — il gruppo di riempimento: oggi la sua rotazione si scrive a mano, e il
pacchetto deve **nominare il buco**, non necessariamente tapparlo.

### 2. Il solutore esce dalla catena, e si vede che è uscito

`improve.py`, la fase del tronco di `spine.py` e `dilate.py` **non vengono cancellati**: il
percorso vigente non li chiama più, e in testa a ciascuno c'è una riga che dice **quando è
morto, perché, e dove è finito il suo lavoro**. Un file che nessuno chiama e non lo dichiara
è una trappola per chi arriva dopo: è esattamente com'è nata la ricerca del 4 agosto,
scritta e mai attuata per sei settimane.

### 3. Le prove dicono che cosa difendono adesso

Trentasei file in `tests/layout/`. Ognuno finisce in una delle tre categorie, e la categoria
si scrive nel file:

- **difende il motore** — resta e deve restare verde (instradamento, accessori appesi,
  interruzioni, legenda, sigle, griglia, formati);
- **difendeva il solutore** — si riscrive dichiarando che cosa difende adesso, oppure si
  **archivia dichiarando la decisione che l'ha revocata**. **Non si converte in `skip`, non
  si converte in `xfail`, non si allenta nessuna soglia**;
- **difende una regola del piano** — è la categoria nuova, e oggi è quasi vuota: ci
  finiscono le tre regole nate componendo il 20 settembre.

### 4. I documenti dicono il prodotto che c'è

`docs/SKILL.md`, ADR 0005, `PROJECT_STATE.md`, `README.md`, `AGENTS.md`, `CLAUDE.md`,
`docs/plans/2026-09-03-release-plan.md`. Regola unica: **un documento o è vigente, o dice in
testa che è storia e quale decisione l'ha superato.** Non esiste un terzo stato, ed è il
terzo stato che ha fatto danno.

### 5. Il primo foglio di regole del piano

Un solo file, `docs/regole-del-piano.md`, e **non si scrive in astratto** — è così che è nata
la funzione di costo. Ci entra solo ciò che ha già una fonte:

- le **regole che il PO ha dato**: D-144 (tratto dritto dal circolatore, una curva, dorsale,
  terminali a pettine), D-145 (organi di servizio addosso al pezzo che servono), D-119
  (generatori incolonnati), D-118, D-060 (l'ordine del processo da sinistra a destra);
- le **tre nate componendo** il 20 settembre, ciascuna con accanto **la tavola che l'ha
  generata**: un rettilineo per la tratta con più accessori in linea; un pezzo si prende dal
  lato delle sue porte; due linee fra gli stessi due raccordi si separano in quota;
- la **composizione a corsie** della ricerca del 4 agosto §2.2, che è l'unica misura che
  abbiamo su come sono fatte due tavole vere.

Niente regole dedotte a tavolino. Una riga senza fonte non entra.

## Perimetro

**Dentro:** `scripts/piano.py` e la sua nuova casa in `src/disegnatore_mep/`; `cli.py`;
`layout/improve.py`, `layout/spine.py`, `layout/dilate.py` (le righe che dichiarano, e le
chiamate che si tolgono dal percorso vigente); `tests/layout/**`; i documenti dell'elenco 4;
`docs/regole-del-piano.md` (nuovo); `docs/collaudi/PROVA-PIANO/**`.

**Fuori:** il motore che funziona — `route.py`, `inline.py`, `place.py` quanto alla posa
degli accessori appesi, `legend.py`, `labels.py`, `addresses.py`, `graphics/**`,
`validation/**` — salvo quando una cura dichiarata lo richiede, e allora si dice perché.
**Fuori** qualunque decisione MEP che il PO non abbia dato, e qualunque convenzione grafica.

**Non si migliora nessuna tavola in questo pacchetto.** Se componendo viene voglia di
sistemare la fascia nella metà alta o i quattordici incroci dell'impianto 5, si scrive nel
rapporto e si lascia al pacchetto dopo.

## Criteri di accettazione

Ogni criterio si chiude con **il comando eseguito e il suo output**.

1. **Le due tavole composte escono dal percorso nuovo**, cioè dalla CLI e non da uno script
   in una cartella di collaudo, e sono **identiche o migliori** a quelle del 20 settembre:
   **zero rilievi bloccanti, zero tratte cedute** su entrambe. Il rapporto le porta in PDF,
   per prime (D-146).
2. **I cinque impianti di prova producono ancora una tavola** per la via che avevano
   (D-148, D-150), e per ciascuno il rapporto dice **formato** e **tratte cedute**. Nessuno
   peggiora.
3. **Nessun percorso vigente chiama più il solutore**, e lo mostra un comando: né
   `improve_sheet`, né la fase del tronco, né la dilatazione. I file esistono e dichiarano
   in testa quando sono morti e perché.
4. **Ogni file di `tests/layout/` ha la sua categoria scritta dentro**, e il conteggio delle
   tre categorie sta nel rapporto. **Zero `skip` e zero `xfail` nuovi**, e lo mostra un
   comando.
5. **Il saldo della suite non peggiora** rispetto al ramo di partenza. Le prove che
   difendevano un comportamento **revocato dal PO** si riscrivono o si archiviano
   **dichiarando la decisione che le ha revocate** — non si zittiscono.
6. **Nessun documento resta in terzo stato**: un comando elenca i file di `docs/` toccati e,
   per ciascuno, la riga che dice «vigente» o «storia, superato da D-nnn».
7. **`docs/regole-del-piano.md` esiste e ogni riga ha una fonte** — una decisione, un input
   del PO, la ricerca del 4 agosto, o la tavola che l'ha generata. Una riga senza fonte è un
   criterio non raggiunto.
8. **Il formato del piano è documentato e validato**: un piano malformato dà un errore che
   dice cosa manca, non una traccia di stack. Una prova lo mostra.
9. **Il buco noto è nominato**: il pezzo a due attacchi che non è una macchina.

## Come si lavora, se si lanciano agenti paralleli (D-152)

La divisione pulita di questo pacchetto è **codice** (1, 2, 3, 8) e **documenti** (4, 6, 7):
due code che non toccano gli stessi file. Il perimetro di ciascun agente si dichiara **prima**
di lanciarlo. Nessuno dei due consegna, fonde o chiude niente, e **quello che riferiscono non
è una misura finché la sessione non l'ha rieseguito**.

## Consegna

Una PR sola verso `main`, **non fusa finché il PO non ha visto le tavole e detto di sì**.

**Le tavole, per prime** (D-146): le due composte, e le cinque della via ordinaria con
formato e tratte cedute. Rapporto in `docs/collaudi/DRAW-015/RAPPORTO.md`.

**Prima di chiedere l'approvazione:**

1. **Guarda le tavole.** Se una ti sembra sbagliata e i numeri dicono che va bene, scrivilo.
2. **Misura la non-regressione prima, non dopo.** Qui sono l'1, il 2 e il 5.
3. **Se una disposizione del PO ammette due letture, fermati e chiedi al PO.**

## Quello che questo pacchetto **non** chiude

- **Il revisore non si costruisce qui.** D-151 lo mette in catena; oggi l'anello lo chiude
  l'agente a mano, ed è già abbastanza per lavorare. Costruirlo è il pacchetto dopo, e va
  costruito **dopo** che qualche giro a mano avrà detto che forma hanno i rilievi utili.
- **Le tavole non migliorano qui**, e il PO ha già detto che non somigliano a un disegno
  (I-082). Il primo pacchetto dopo la ristrutturazione è quello: **la fascia nella metà alta**
  — nessuno distribuisce in verticale — e **i quattordici incroci dell'impianto 5**.
- **La domanda del PO sul seguito resta aperta** (I-083): la proposta dell'agente è di
  **non** scrivere tutte le regole in astratto, e di separare da subito le due code —
  difetti del motore e difetti del pianificatore — perché non si contendono niente. Ma è una
  proposta: decide il PO.
- **Il formato definitivo** (D-148 è dichiarata momentanea) e **la riproducibilità** (D-023,
  sospesa da D-151) restano domande aperte del PO.
