# HANDOFF — Disegnatore MEP · 6 agosto 2026 (sera)

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
| 9 | `AGENTS.md` | Regole operative e i due ruoli |

---

## 6. Stato al 6 agosto 2026, sera

**Ramo:** il lavoro è su `main`.
**Prove:** 659 verdi, 22 parcheggiate con il motivo scritto; `ruff` e `mypy --strict` puliti.
**Ambiente:** `bash scripts/setup-env.sh` — **da eseguire per primo** in una sessione cloud.
**Numeri:** 39 simboli pubblicati, 51 voci di catalogo, 14 regole.

### I pezzi

| Pezzo | Stato |
|---|---|
| **1 — Capire** (dal testo al grafo di prima stesura) | **Non esiste.** Le letture sono fatte a mano in `examples/prova/` |
| **2 — Completare** (le regole) | Costruito e collaudato. Contenuto da estendere con le fonti |
| **3 — Assemblare** | **Costruito** in questa sessione. Da collaudare in modo indipendente |
| Il grafo e le sue sigle | Costruito e collaudato |
| Il vocabolario delle proprietà | Approvato |
| 4 — Disporre / libreria / cartiglio / composizione | Come prima: la composizione è da rifare |
| 5 — Validatori e cancello dell'occhio terzo | Correttezza e preflight esistono, il cancello no |

### Cosa è cambiato in questa sessione

- **Un attacco, una tubazione** (D-100), e i due raccordi — confluenza e ripartizione.
- **Gli attacchi di servizio** (D-101): l'accessorio a stacco va dove va davvero. Chiuso il
  debito che D-094 aveva congelato: nove accessori avevano due attacchi e ne hanno uno.
- **L'assemblatore** (D-093, D-094): la fila la decidono i vincoli dichiarati, non l'ordine
  alfabetico dei nomi dei file delle regole.
- **Nove famiglie di pezzi nuove** aggiunte come dato, senza toccare il motore.
- **I cinque impianti del committente** passano per la catena: i grafi sono in
  `docs/prodotto/grafi-di-prova/`.

---

## 7. Il primo lavoro della prossima sessione

### 7.1 — L'indirizzo dei nodi, che il PM ha già dato (D-105)

**È la prima cosa, e viene prima dei pezzi.** Il PM ha letto i grafi dei suoi cinque
impianti e ha detto: «non capisco i grafici che hai fatto». Aveva ragione. Le sigle dicono
**che cosa** è un pezzo e mai **dove** sta, e la linea idraulica non ha nome — così una
passeggiata che è una sola mandata sembra una sequenza di salti.

Da fare, come lui lo ha descritto:

- ogni **linea idraulica** ha una sigla di famiglia e un numero: `CP.01` mandata primaria,
  poi `RP` ritorno primario, `CS`/`RS` secondario, `AF`/`ACS` sanitario. La famiglia dice
  **che acqua porta e da che parte va**;
- ogni pezzo sulla linea è un **nodo numerato**: `CP.01.N.02`;
- accanto alla linea, in tabella, la sua descrizione: «da PDC-01 a ACC-01»;
- **dove due linee si incontrano la principale tira dritto e la secondaria muore** su quel
  nodo;
- **dove una linea si sdoppia la principale tiene il nome nudo e i rami prendono una
  lettera**: `CP.01` prosegue, `CP.01a` e `CP.01b` sono le diramazioni. La lettera non va
  mai sulla principale, così il suo nome non cambia per qualcosa successo altrove;
- in tutti e due i casi **la principale è quella che va verso la prima sorgente**,
  nell'ordine di D-098: sul ritorno comune di due macchine, `RP.01` arriva alla prima e
  `RP.01a` alla seconda;
- **ciò che pende da uno stacco non è un ramo ma un civico del nodo**: `CP.01.N.02.1` è il
  primo pezzo appeso al nodo 2;
- le sigle di famiglia dei pezzi (`VI-02`) **restano**: servono alla distinta, e sulla
  tavola convivono con l'indirizzo.

**Non è da rifare, è da battezzare.** L'assemblatore calcola già l'oggetto che serve: lavora
per **tratte**, e una tratta è una linea. Manca darle il nome e numerare i nodi.

**Nessuna domanda aperta su questo.** Il PM ha chiuso innesti, diramazioni e stacchi il
6 agosto; si esegue.

### 7.2 — Poi i pezzi da 1 a 3, fino al grafo definitivo

1. **Il pezzo 1, «Capire»** — le istruzioni dell'agente che legge il testo dell'ingegnere e
   costruisce il grafo di prima stesura. Oggi quella lettura la fa una persona a mano, e
   finché è così il primo pezzo della skill non esiste. È fatto di file di testo, non di
   programma (ADR 0005).
2. **Il contenuto delle regole**, esteso con il metodo delle fonti (D-103) e dentro il
   confine di D-104: bilanciamento, disconnettore sul riempimento, miscelatrice sanitaria,
   contabilizzazione, ritegno. Sono elencati in coda a
   `docs/prodotto/DOVE_VA_CIASCUN_ACCESSORIO.md`.
3. **Il collaudo indipendente dell'assemblatore**, che non c'è ancora: è stato costruito e
   verificato da chi lo ha scritto, e questo non basta (D-083).

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

---

## 9. Domande aperte per il PM

**Una sola, e sta dentro i grafi di prova.** Nel quinto impianto il testo chiede tre
circuiti secondari — batterie di trattamento aria, ventilconvettori e un circuito miscelato
per il pavimento radiante — e il collettore disponibile ne serve due. Il circuito miscelato
**non è disegnato**, ed è scritto come punto aperto invece di essere inventato.

---

## Ultimo aggiornamento

`2026-08-06`, sera — Claude — chiusi i due difetti di modellazione che il PM ha diagnosticato
(un attacco una tubazione, e gli attacchi di servizio delle macchine), costruito
l'assemblatore, aggiunte nove famiglie di pezzi come dato, e fatti passare i cinque impianti
di prova per la prima parte della catena. Registrato in §4 l'errore di metodo che si è
ripetuto tre volte, perché non si ripeta una quarta.
