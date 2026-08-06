# HANDOFF — Disegnatore MEP · 6 agosto 2026 (notte)

> ⛔ **Non è un riassunto del progetto.** È il cancello di lettura per la sessione
> successiva. Si legge tutto, poi si risponde alle domande del §2, poi si comincia.
>
> **Chi ha fretta legge questo file e `docs/SKILL.md`. Sono sufficienti per capire cosa
> stiamo costruendo e da dove si riparte.** Tutto il resto si apre quando serve.

---

## 1. Cosa stiamo costruendo, in una pagina

Una **skill** che trasforma un impianto termotecnico **già deciso e dimensionato
dall'ingegnere** in una tavola tecnica. Non progetta, non dimensiona, non sceglie le
macchine: aggiunge gli accessori che un impianto deve avere, li fa approvare, e disegna.

**La frase del PM che definisce il prodotto, e che va tenuta a mente sempre** (D-104):

> «Io sono un buon ingegnere ma non sono un disegnatore MEP super senior. Per questo nasce
> la skill: per far disegnare quello che so fare benissimo — lo schema a livello di
> definitivo — e portarlo a livello più esecutivo.»

Ne discende il confine, che in questa sessione è stato violato due volte e costa caro
ogni volta: **la skill mette le valvole, uno sfiato e quattro accessori standard. Non
decide quanti pezzi ci vanno, non cambia lo schema ricevuto, non dimensiona.**

### La catena (D-099)

```
l'ingegnere spiega l'impianto a parole
   → l'AI interpreta                        GRAFO DI PRIMA STESURA
   → le regole dicono cosa manca e perché
   → l'assemblatore dice dove va ciascuno   GRAFO DEFINITIVO
   → ★ L'INGEGNERE APPROVA                  cancello: niente si disegna prima
   → l'instradatore dispone e disegna        con i criteri di costo del PM
   → i validatori verificano
   → ★ L'OCCHIO TERZO GIUDICA               cancello: può respingere
   → la tavola
```

**Una cosa sola attraversa tutto: il grafo.** Nasce abbozzato, si arricchisce di nodi,
diventa definitivo. La tavola ne è la **rappresentazione**.

### Il grafo, come è fatto (D-097, D-098, D-100, D-101)

Come una **rete stradale**. Ogni pezzo è un **nodo con la propria sigla**; ogni tubo fra
due pezzi è un **arco** col proprio fluido. Le sigle si assegnano camminando dalle
**sorgenti dichiarate**, seguendo l'acqua. Una sigla sola per tutto il prodotto.

**Ogni attacco porta una tubazione sola, sempre** (D-100). Dove due tubazioni si
incontrano c'è un pezzo che le unisce, con la propria sigla: una **confluenza** se due
diventano una, una **ripartizione** se una si sdoppia.

**Una macchina ha più attacchi di quelli del flusso** (D-101): un volano dichiara anche
sfiato, scarico e sede della sonda. Un accessorio che pende da uno stacco va **su
quell'attacco** se la macchina ce l'ha, e su una **derivazione** saldata sul tubo se non
ce l'ha. Non spezza mai la tubazione principale.

### Dove si guarda cosa (D-096) — la regola che ha cambiato il progetto

**Il contenuto si giudica sul grafo scritto, non sul disegno.** Se il grafo è giusto e la
tavola è brutta, il difetto è nel disporre. Se il grafo è sbagliato, la tavola non c'entra.

---

## 2. Sentinel checks — rispondere prima di toccare qualunque cosa

1. Qual è l'unico oggetto che attraversa tutta la skill, e perché la tavola non è un
   oggetto a sé?
2. Su cosa si giudica il **contenuto** e su cosa il **disegno**?
3. Quante tubazioni porta un attacco, e cosa c'è dove due tubazioni si incontrano?
4. Dove va un accessorio che pende da uno stacco, e chi decide quale dei due casi vale?
5. Una norma dice che un impianto deve avere un certo dispositivo: la skill può
   aggiungerlo di propria iniziativa?
6. Chi decide l'ordine dei pezzi lungo un tubo, e su cosa lo decide?
7. Cosa deve succedere quando una regola si applica ma il catalogo non ha il pezzo adatto
   a quel fluido?

*Risposte attese:* il grafo, e la tavola ne è la rappresentazione; il contenuto sul grafo
scritto, il disegno sulla tavola (D-096); **una sola**, e dove se ne incontrano due c'è un
raccordo con la propria sigla (D-100); sull'attacco di servizio della macchina se ce l'ha,
altrimenti su una derivazione, e lo dice **il catalogo** (D-101); **no** — una prescrizione
dice cosa deve avere l'impianto, non autorizza la skill ad aggiungerlo, e quantità e
volumi restano dell'ingegnere (D-104); l'**assemblatore**, risolvendo i vincoli che ogni
regola dichiara rispetto ai **mestieri** degli altri pezzi, mai numeri di priorità (D-094);
lo deve **dire**, come punto aperto per il progettista, mai tacere.

---

## 3. Il metodo, che è vincolante (D-083)

**Tre ruoli: uno decide, uno o più fanno, uno controlla.** L'orchestratore scrive i criteri
di accettazione **prima**; sviluppatori separati eseguono; un collaudo **a contesto
separato** verifica e può respingere. I verdetti si registrano nell'appendice del piano.

Quattro regole ferree:

1. Niente è «fatto» senza verdetto positivo del collaudo, registrato.
2. Nessuna tavola arriva al PM senza il cancello completo, rigenerata il giorno stesso.
3. **Vietato inventare.** Se la fonte manca è una domanda per il PM, non una licenza. E se
   la fonte **esiste** — un catalogo, una norma — si va a cercarla invece di chiedere
   (D-102).
4. Il piano approvato si rispetta; una deviazione si registra **prima** di eseguirla.

**Come si scrive al PM:** zero verbosità, italiano, frasi corte, nessun nome di file o di
funzione, deve capirlo un non sviluppatore.

---

## 4. ⛔ L'errore di metodo di questa sessione, che non va ripetuto

È lo stesso, tre volte, e il PM ha dovuto fermare il lavoro ogni volta:

1. **Un rigo di norma trasformato in regola.** Dalla Raccolta R era stato dedotto «con due
   generatori due vasi di espansione». Nessuno lo fa, e comunque non è una decisione di
   disegno. Ritirato in D-104.
2. **Il disegno inseguito dentro una sessione sul contenuto.** Le prove del disegno erano
   diventate rosse perché l'impianto era cresciuto; invece di lasciarle stare sono state
   inseguite. Il disegno è un altro pezzo e lo fa un altro agente.
3. **Domande girate al PM che avevano risposta nei cataloghi.** Lui stesso ha avvertito:
   «io potrei sbagliare».

**La radice è una sola: prendere un segnale laterale e trattarlo come lavoro da fare,
invece di finire il pezzo.** Quando succede, fermarsi e tornare al pezzo.

---

## 5. Ordine di lettura

| # | File | Perché |
|---|---|---|
| 1 | Questo file | Cancello |
| 2 | `docs/SKILL.md` | Com'è fatta la skill, la catena, i pezzi |
| 3 | `PROJECT_STATE.md` | A che punto siamo |
| 4 | `docs/plans/2026-08-06-piano-costruzione-skill.md` | Il piano corrente e i verdetti |
| 5 | `docs/DECISION_LOG.md` — **partire da D-096** | D-096÷D-104 sono la logica del grafo e il confine del prodotto |
| 6 | `docs/prodotto/DOVE_VA_CIASCUN_ACCESSORIO.md` | Dove va ciascun pezzo, con la fonte. **Leggere prima il confine in testa** |
| 7 | `docs/adr/0005-*.md` | L'architettura, blindata |
| 8 | `docs/prodotto/GRAFO_IMPIANTO.md` e `docs/prodotto/grafi-di-prova/` | Gli artefatti che il PM legge e approva |
| 8b | `examples/prova/input/` | **Il testo originale del committente**, non toccato: è il metro con cui si giudica se il primo pezzo ha letto bene |
| 9 | `AGENTS.md` | Regole operative e i due ruoli |

---

## 6. Stato al 6 agosto 2026, notte

**Ramo:** il lavoro è su `main`.
**Prove:** 714 verdi, 23 parcheggiate con il motivo scritto; `ruff` e `mypy --strict` puliti.
**Ambiente:** `bash scripts/setup-env.sh` — **da eseguire per primo** in una sessione cloud.
**Numeri:** 39 simboli pubblicati, 51 voci di catalogo, 14 regole.

### I pezzi

| Pezzo | Stato |
|---|---|
| **1 — Capire** | **Costruito** (istruzioni in `skill/capire/`) e **provato in camera pulita**: 4 impianti su 5 letti identici alla lettura manuale, arco per arco. Da collaudare da contesto separato |
| **2 — Completare** (le regole) | Costruito e collaudato. Cinque posizioni nuove chiuse con le fonti, da tradurre in regole |
| **3 — Assemblare** | Costruito, **collaudato in modo indipendente**: respinto su due difetti veri, entrambi corretti lo stesso giorno |
| Il grafo, le sigle e **l'indirizzo dei nodi (D-105)** | Sigle collaudate; l'indirizzo è costruito e provato, da collaudare da contesto separato |
| Il vocabolario delle proprietà | Approvato |
| 4 — Disporre / libreria / cartiglio / composizione | Come prima: la composizione è da rifare |
| 5 — Validatori e cancello dell'occhio terzo | Correttezza e preflight esistono, il cancello no |

### Cosa è cambiato in questa sessione (la ripresa serale)

- **L'indirizzo dei nodi (D-105)**: ogni linea idraulica ha nome e numero (`CP.01`,
  `RP.01a`), ogni pezzo un indirizzo (`CP.01.N.02`), gli stacchi i civici
  (`CP.01.N.02.1`). Il documento del grafo si legge per linea, come il PM lo ha chiesto,
  e i cinque grafi sono rigenerati così.
- **Il pezzo 1 esiste**: istruzioni in file di testo (ADR 0005), provate su cinque agenti
  freschi in camera pulita contro i testi originali del committente. Verbale e
  classificazione delle divergenze in `skill/capire/PROVA-2026-08-06.md`.
- **Il collaudo indipendente** di D-100, D-101 e dell'assemblatore: quattro difetti veri
  trovati, tre corretti subito (C1 il corredo che migrava permutando il file; C3 il
  catalogo senza raccordo che faceva crollare la catena; C4 il doppio «attaccato alla
  macchina» che non fermava). Le prove del collaudo sono regressione in `tests/collaudo/`.
- **Il quarto difetto (C2) è aperto e progettato**: lo scarico del bollitore va
  sull'ingresso freddo e oggi sta sull'uscita calda. Il progetto della correzione è
  nell'appendice del piano; una prova parcheggiata lo aspetta.
- **Le cinque righe mancanti degli accessori** (bilanciamento, disconnettore,
  miscelatrice, contabilizzatore, ritegno) chiuse con fonti aperte e lette
  (SRC-020..SRC-026), solo posizioni, dentro il confine di D-104.

---

## 7. Il primo lavoro della prossima sessione

### 7.1 — I due collaudi che mancano (D-083)

Due pacchetti sono costruiti, provati e **non ancora «fatti»**, perché chi li ha
costruiti non può approvarli:

1. **L'indirizzo dei nodi (D-105)** — sviluppato dall'orchestratore (deviazione
   registrata nell'appendice del piano: gli agenti separati sono morti per limite di
   spesa). I criteri di accettazione sono in §3bis-A del piano; le prove esistenti sono
   in `tests/graph/test_lines.py`, ma il collaudo deve rifarle con criteri propri.
2. **Il pezzo 1, «Capire»** — le istruzioni e la prova in camera pulita ci sono
   (`skill/capire/`, verbale in `PROVA-2026-08-06.md`); il collaudo deve giudicare
   istruzioni e classificazione delle divergenze da contesto separato.

### 7.2 — Poi, in quest'ordine

1. **La correzione C2** (lo scarico del bollitore sull'ingresso freddo): il progetto è
   scritto nell'appendice del piano — una dichiarazione di catalogo nuova, «da quale
   attacco la riserva si riempie» — e una prova parcheggiata in `tests/collaudo/` la
   aspetta. Ricordarsi che il catalogo di prova ha un **generatore**: si riesegue, non
   si modifica a mano.
2. **Le correzioni alle istruzioni del pezzo 1** elencate nel verbale della prova: ogni
   correzione impone una prova nuova, con un agente nuovo, in camera pulita.
3. **La traduzione in regole** delle cinque posizioni chiuse con le fonti
   (`DOVE_VA_CIASCUN_ACCESSORIO.md` §14-18), dentro il confine di D-104: la fonte dice
   **dove** va un pezzo che il progettista ha messo in schema, mai **se** aggiungerlo.

**Non toccare il disegno.** La composizione, l'instradamento e il foglio dei simboli sono
pezzi successivi, e le loro prove sono parcheggiate con il motivo scritto.

---

## 8. Quirks e gotcha

- **Eseguire sempre la suite completa** e `mypy src tests examples`, mai il solo file del
  task.
- **Mai `git checkout --` o `git stash` su lavoro non committato** senza averne prima
  salvato una copia.
- **Il comando delle regole vuole anche `--naming`** oltre a `--catalog`, `--symbols` e
  `--rules`.
- **I generatori di fixture vanno rieseguiti**, non modificati a mano: c'è una prova che
  inchioda i file generati al proprio generatore, ed è nata da un incidente vero.
- **Firma dei commit:** in questo container `commit.gpgsign` è attivo con una chiave vuota.
  Si committa con `git -c commit.gpgsign=false`.
- **Gli agenti di sviluppo non committano.** Committa l'orchestratore, e i lavori a metà
  vanno come `wip:` con scritto che non sono collaudati.
- **Gli agenti in parallelo possono morire per limite di spesa dell'account**, a metà
  lavoro e senza preavviso: è successo in questa sessione. I loro worktree e file
  sopravvivono — prima di rifare, guardare cosa hanno lasciato. E il gancio di fine turno
  può committare da solo il lavoro non committato: controllare la storia con `git log`
  prima di ricommettere.
- **La prova in camera pulita del pezzo 1 non si fa da contaminati:** chi ha letto le
  letture manuali o i grafi non può fare l'interprete. Kit e divieti sono in
  `skill/capire/CONSEGNA.md`.

---

## 9. Domande aperte per il PM

**Una sola, e sta dentro i grafi di prova.** Nel quinto impianto il testo chiede tre
circuiti secondari — batterie di trattamento aria, ventilconvettori e un circuito miscelato
per il pavimento radiante — e il collettore disponibile ne serve due. Il circuito miscelato
**non è disegnato**, ed è scritto come punto aperto invece di essere inventato.

La prova in camera pulita del pezzo 1 ha aggiunto un elemento utile alla stessa domanda:
il testo non nomina nessun collettore, e un lettore indipendente ha chiuso i tre circuiti
con semplici raccordi a T, disegnando anche il miscelato e dichiarando l'assunzione sul
punto di ripresa della miscela. Le due letture sono due risposte diverse alla stessa
ambiguità, e la scelta resta del PM.

---

## Ultimo aggiornamento

`2026-08-06`, notte — Claude — eseguito D-105 (l'indirizzo dei nodi) e rigenerati i cinque
grafi con la convenzione nuova; costruito e provato in camera pulita il pezzo 1, con
quattro letture su cinque identiche a quelle manuali; collaudo indipendente di D-100,
D-101 e assemblatore con quattro difetti veri, tre corretti e uno progettato (C2);
chiuse con le fonti le cinque righe mancanti degli accessori. Restano i due collaudi
separati dei pacchetti nuovi: senza quelli, per D-083, niente è «fatto».
