# DRAW-015 — Il revisore, e il repository che lo regge

**Titolo:** Il revisore, e il repository che lo regge
**Scritto e svolto da:** l'agente unico (**D-147**), che può lanciare agenti paralleli in
sessione (**D-152**, `docs/governance/OPERATING_MODEL.md` §1.2.2)
**Data:** 2026-09-20
**Stato:** **ATTIVO.** Sostituisce `DRAW-014`, superato in corsa da D-151
**Release:** 0.3 — generalizzazione
**Approvazione della fusione:** **del PO**, e si dà guardando le tavole (D-147, D-146)

> **Il cuore di questo pacchetto è il revisore**, e la ristrutturazione gli sta sotto perché
> senza quella il revisore non ha su cosa lavorare: gli serve un **piano** che sia un
> oggetto vero e non uno script di prova, e gli servono **regole che siano controlli**.
>
> Il PO ha corretto l'ordine dei lavori che l'agente aveva proposto, e la ragione è nella sua
> frase: il revisore **è lo strumento con cui si scrivono le regole**, non il premio finale.

---

## Perché

Il PO, il 20 settembre, sull'ordine dei lavori:

> «Secondo me il revisore va costruito subito perché è proprio quello che può aiutarci a
> scrivere le regole una tavola alla volta. Altrimenti torniamo a fare tavole orribili e a
> stressare me con tavole che qualunque AI confrontandole con quelle fatte da un disegnatore
> vero riconosce subito che non vanno.»

E sul contenuto delle regole:

> «Tre macro fasce verticali di disegno: generazione, accumuli e scambiatori, distribuzione.
> Prima le autostrade dritte il più possibile (la valvola a tre vie non deve spezzare il
> tratto, allineare inlet-outlet; se ho più generatori o più terminali si fa un collettore
> verticale… ecc).»

Oggi il repository descrive un prodotto che non esiste più: `docs/SKILL.md` e l'ADR 0005
raccontano un solutore che minimizza una somma pesata, e il pezzo che ha prodotto le due
tavole buone è uno **script di prova** in una cartella di collaudo. Chi apre la prossima
sessione, leggendo il repository, ricostruirebbe il solutore.

## Le quattro disposizioni che lo governano

| | |
|---|---|
| **D-151** | Il disegno lo compone un agente: pianificatore → motore → revisore |
| **D-152** | Due agenti paralleli dentro la sessione, mai due sessioni |
| **D-153** | Il revisore si costruisce **subito**, ed è lo strumento con cui si scrivono le regole. **Una regola è un controllo che sa nominare la propria violazione** |
| **D-154** | Tre macro fasce verticali; prima le autostrade dritte; la tre vie non spezza il tratto; più generatori o più terminali ⇒ collettore verticale |

Documenti: `docs/ARCHITETTURA-DEL-PIANO.md` (vigente) e `docs/regole-del-piano.md` (aperto).

## Le sei cose da fare

### 1. Il revisore — l'anello si chiude

Legge quello che è uscito e **corregge il piano**, poi rifà girare. Entra con:

- la **tavola**, e la guarda — non solo i numeri (**D-153** punto 3). Con accanto le tavole
  di riferimento del disegnatore del PO, `docs/input-pm/riferimenti-grafici/`;
- i **rilievi** del preflight e le misure della geometria;
- il **piano** che ha prodotto quella tavola e **`docs/regole-del-piano.md`**.

Esce con **un piano corretto**, e ogni spostamento porta **il nome della regola** che lo
motiva. Si ferma quando non resta nessun rilievo bloccante, quando un giro **non migliora**,
o al tetto di giri — e in tutti e tre i casi **dice perché si è fermato**.

Ogni giro lascia la propria traccia: piano → rilievi → piano. È quella traccia che diventa
una riga nuova in `docs/regole-del-piano.md`, ed è il motivo per cui il revisore viene prima
delle regole e non dopo.

### 2. Le quattro regole del PO diventano controlli

Senza controllo il revisore non le può usare. Servono, per **A1** (tre fasce), **B1**
(autostrade dritte), **B3** (collettore verticale) e **B4** (la tre vie non spezza il
tratto), quattro rilievi che **nominino la violazione** e la dicano su una tavola.

**B1 chiede una cosa che oggi non c'è:** la geometria non sa **quali tratte sono autostrada**,
e `RUN_WITH_TOO_MANY_BENDS` conta una piega della dorsale come una piega di uno stacchetto.
È esattamente il difetto che ha generato D-151, e va chiuso qui.

### 3. Il piano diventa un pezzo del prodotto

`scripts/piano.py` esce dagli script: **formato** dichiarato (modello `pydantic`),
**esecutore**, e un **comando della CLI**. Il formato è quello che la prova ha già usato —
`formato`, `pezzi: {id: {x, y}}` — più le note, che sono parte del piano: dicono **quale
regola** ha messo il pezzo lì.

**Il piano non contiene ciò che si deduce** (C2, C3 in `regole-del-piano.md`). Buco noto da
nominare: un pezzo con **due** attacchi che non è una macchina — il gruppo di riempimento.

### 4. Il solutore esce dalla catena, e si vede che è uscito

`improve.py`, la fase del tronco di `spine.py` e `dilate.py` **non si cancellano**: il
percorso vigente non li chiama più, e in testa a ciascuno una riga dice **quando è morto,
perché, e dove è finito il suo lavoro**. Un file che nessuno chiama e non lo dichiara è una
trappola: è così che la ricerca del 4 agosto è rimasta inattuata per sei settimane.

### 5. Le prove dicono che cosa difendono adesso

Trentasei file in `tests/layout/`, ognuno in una delle tre categorie, scritta dentro:
**difende il motore** (resta verde), **difendeva il solutore** (si riscrive dichiarando che
cosa difende adesso, o si archivia dichiarando la decisione che l'ha revocato — **mai `skip`,
mai `xfail`, nessuna soglia allentata**), **difende una regola del piano** (categoria nuova,
oggi quasi vuota).

### 6. I documenti dicono il prodotto che c'è

`docs/SKILL.md`, ADR 0005, `PROJECT_STATE.md`, `README.md`, `AGENTS.md`, `CLAUDE.md`,
`docs/plans/2026-09-03-release-plan.md`. Regola unica: **un documento o è vigente, o dice in
testa che è storia e quale decisione l'ha superato.** Il terzo stato è quello che fa danno.

**E una correzione di citazione**: «generatori a sinistra, impilati in verticale» è attribuita
a **D-119** in `place.py`, `improve.py`, `test_zone_dei_pezzi_grossi.py`, nelle note dei due
piani e nel README della prova. D-119 è l'area di rispetto dei raccordi. La regola è
**D-041 + D-118**.

## Perimetro

**Dentro:** il revisore e la sua casa in `src/disegnatore_mep/`; `scripts/piano.py` e la sua
casa nuova; `cli.py`; `validation/**` (i controlli nuovi); `layout/geometry.py` (che cos'è
un'autostrada); `layout/improve.py`, `layout/spine.py`, `layout/dilate.py` (le righe che
dichiarano e le chiamate che si tolgono); `tests/**`; i documenti dell'elenco 6;
`docs/regole-del-piano.md`; `docs/collaudi/PROVA-PIANO/**` e `docs/collaudi/DRAW-015/`.

**Fuori:** il motore che funziona — `route.py`, `inline.py`, `place.py` quanto alla posa,
`legend.py`, `labels.py`, `addresses.py`, `graphics/**` — salvo quando una cura dichiarata lo
richiede, e allora si dice perché. **Fuori** qualunque decisione MEP che il PO non abbia dato
e qualunque convenzione grafica non dettata da D-154.

**Non si inventa nessuna regola.** Una riga di `regole-del-piano.md` senza fonte è un difetto
del pacchetto, non un contributo.

## Criteri di accettazione

Ogni criterio si chiude con **il comando eseguito e il suo output**.

1. **Il revisore gira su almeno tre impianti** e il rapporto porta, per ciascuno, **la tavola
   prima e la tavola dopo** e le misure di entrambe. Se non migliora, si dice.
2. **Ogni correzione del revisore porta il nome della regola** che la motiva. Una correzione
   senza regola è un criterio non raggiunto.
3. **Il revisore non peggiora in silenzio**: se un giro peggiora una misura, si ferma e lo
   nomina. Una prova lo mostra.
4. **Le quattro regole di D-154 hanno ciascuna un controllo** che nomina la violazione, e per
   ciascuna una tavola su cui si vede. **Compresa B1**, che richiede di distinguere
   l'autostrada dal corredo nella geometria.
5. **Le due tavole composte restano a zero**: zero rilievi bloccanti, zero tratte cedute, dal
   percorso nuovo — la CLI, non uno script di collaudo.
6. **I cinque impianti di prova producono ancora una tavola** per la via che avevano (D-148,
   D-150), e nessuno peggiora. Formato e tratte cedute per ciascuno, nel rapporto.
7. **Nessun percorso vigente chiama più il solutore**, e lo mostra un comando.
8. **Ogni file di `tests/layout/` ha la sua categoria scritta dentro**, con il conteggio nel
   rapporto, **zero `skip` e zero `xfail` nuovi**, e il saldo della suite non peggiora.
9. **Nessun documento resta in terzo stato**, e la citazione D-119 è corretta ovunque.
10. **Il formato del piano è documentato e validato**: un piano malformato dà un errore che
    dice cosa manca, non una traccia di stack.

## Come si lavora, se si lanciano agenti paralleli (D-152)

La divisione pulita è **il revisore e i controlli** (1, 2, 4) da una parte, **la
ristrutturazione** (3, 5, 6) dall'altra: code diverse, file diversi. Il perimetro di ciascun
agente si dichiara **prima** di lanciarlo. Nessuno dei due consegna, fonde o chiude niente, e
**quello che riferiscono non è una misura finché la sessione non l'ha rieseguito**.

## Consegna

Una PR sola verso `main`, **non fusa finché il PO non ha visto le tavole e detto di sì**.

**Le tavole, per prime** (D-146): il prima e il dopo del revisore, e le cinque della via
ordinaria con formato e tratte cedute. Rapporto in `docs/collaudi/DRAW-015/RAPPORTO.md`.

**Prima di chiedere l'approvazione:**

1. **Guarda le tavole**, e mettile accanto a quelle del disegnatore del PO. Se una ti sembra
   sbagliata e i numeri dicono che va bene, scrivilo.
2. **Misura la non-regressione prima, non dopo.** Qui sono il 5, il 6 e l'8.
3. **Se una disposizione del PO ammette due letture, fermati e chiedi al PO.**

## Quello che questo pacchetto **non** chiude

- **Le tavole non diventano belle qui.** Il revisore serve a **trovare** perché non lo sono,
  e a scrivere le regole che le miglioreranno. Il primo difetto in coda è già nominato: il
  disegno è **una fascia nella metà alta** (D3 in `regole-del-piano.md`).
- **L'elenco delle regole non si chiude** — lo ha detto il PO (I-085, aperta): «vanno solo
  aggiunte altre e migliorate».
- **La composizione a corsie** della ricerca del 4 agosto non entra finché non l'avremo
  composta noi almeno una volta.
- **Il formato definitivo** (D-148 è momentanea) e **la riproducibilità** (D-023, sospesa da
  D-151) restano domande aperte del PO.
