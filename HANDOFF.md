# HANDOFF — Disegnatore MEP · 6 agosto 2026

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

### La catena, come il PM l'ha riformulata il 6 agosto (D-099)

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

**Una cosa sola attraversa tutto: il grafo.** Non un modello, poi delle catene, poi una
geometria — lo **stesso grafo**, che nasce abbozzato, si arricchisce di nodi e diventa
definitivo. La tavola ne è la **rappresentazione**.

I due cancelli con la stella non sono opzionali: senza il primo la skill modificherebbe
l'impianto dell'ingegnere in silenzio (D-004, D-013); senza il secondo consegnerebbe ciò
che i propri controlli non sanno vedere (D-063, D-086).

### Il grafo, come è fatto (D-097, D-098)

Come una **rete stradale**. Ogni pezzo — macchina o accessorio — è un **nodo con la propria
sigla**; ogni tubo fra due pezzi è un **arco** col proprio fluido; un attacco su cui
convergono più tubi è un **incrocio** con i rami numerati. Le sigle si assegnano camminando
dalle **sorgenti dichiarate** — chi genera calore, l'allacciamento da cui il fluido entra —
seguendo l'acqua. **Una sigla sola per tutto il prodotto**: la stessa sul grafo, sulla
tavola e sulla distinta.

### Dove si guarda cosa (D-096) — la regola che ha cambiato il progetto

**Il contenuto si giudica sul grafo scritto, non sul disegno.** Il disegno è il banco di
prova dell'instradatore, dei validatori e della skill finita. Se il grafo è giusto e la
tavola è brutta, il difetto è nel disporre. Se il grafo è sbagliato, la tavola non c'entra.

Prima di questa regola il progetto ha perso giorni a tarare un disegno mentre il contenuto
non era approvato da nessuno. **Non rifarlo.**

---

## 2. Sentinel checks — rispondere prima di toccare qualunque cosa

1. Qual è l'unico oggetto che attraversa tutta la skill, e perché la tavola non è un
   oggetto a sé?
2. Su cosa si giudica il **contenuto** — quali pezzi, in che punto, su che fluido — e su
   cosa si giudica il **disegno**?
3. Da dove partono le sigle dei nodi, e perché non dall'ordine in cui i pezzi compaiono nel
   file?
4. Quali sono i due cancelli obbligatori della catena, e cosa succede se si saltano?
5. Perché una regola non può nominare un componente, e cosa la fa fallire se ci prova?
6. Chi decide se un pezzo di lavoro è «fatto», e chi non può deciderlo?
7. Cosa deve succedere quando una regola si applica ma il catalogo non ha il pezzo adatto a
   quel fluido?

*Risposte attese:* il grafo, e la tavola ne è la rappresentazione — se il grafo è giusto e
la tavola brutta il difetto è a valle; il contenuto sul grafo scritto, il disegno sulla
tavola (D-096); dalle sorgenti dichiarate camminando col fluido, perché l'ordine del file
non è un ordine (D-098); l'approvazione dell'ingegnere prima di disegnare e l'occhio terzo
prima di consegnare, e saltandoli si modifica l'impianto in silenzio o si consegna ciò che
i nostri controlli non vedono; perché il motore delle regole è la porta di servizio da cui
rientrerebbe un catalogo di schemi tipo, e una prova automatica scandisce l'intero
pacchetto (D-069); il collaudo indipendente, e non può deciderlo chi ha scritto il lavoro
(D-083); lo deve **dire**, come punto aperto per il progettista, mai tacere.

---

## 3. Il metodo, che è vincolante (D-083)

**Tre ruoli: uno decide, uno o più fanno, uno controlla.** L'orchestratore scrive i criteri
di accettazione **prima** che il lavoro cominci; sviluppatori separati eseguono; un
collaudo **a contesto separato** verifica con prove proprie e può respingere. I verdetti si
registrano nell'appendice del piano, respingimenti compresi.

Quattro regole ferree:

1. Niente è «fatto» senza verdetto positivo del collaudo, registrato.
2. Nessuna tavola arriva al PM senza il cancello completo, rigenerata dalla catena corrente
   il giorno stesso. Mai mostrare un artefatto vecchio come risultato attuale.
3. **Vietato inventare.** Nessun contenuto grafico senza fonte dichiarata. Se la fonte
   manca, è una domanda per il PM, non una licenza.
4. Il piano approvato si rispetta; una deviazione si registra **prima** di eseguirla.

E le regole del gioco di ogni pezzo (§1 del piano): un pezzo alla volta; criteri di
accettazione come **proprietà** valide su qualunque impianto, mai numeri di una tavola di
prova; si verifica **guardando, non contando**; regole generali mai particolari; gli esempi
del PM non sono l'elenco dei difetti, si cercano tutti i simili; la skill non progetta.

**Come si scrive al PM:** zero verbosità, italiano, frasi corte, nessun nome di file o di
funzione, deve capirlo un non sviluppatore. Il dettaglio tecnico vive nei documenti e nei
messaggi di commit.

---

## 4. Ordine di lettura

| # | File | Perché |
|---|---|---|
| 1 | Questo file | Cancello |
| 2 | `docs/SKILL.md` | Com'è fatta la skill, la catena, i pezzi |
| 3 | `PROJECT_STATE.md` | A che punto siamo |
| 4 | `docs/plans/2026-08-06-piano-costruzione-skill.md` | Il piano corrente, otto pezzi, e l'appendice coi verdetti |
| 5 | `docs/DECISION_LOG.md` — **partire da D-087** | Le decisioni che governano il lavoro di oggi. D-096÷D-099 sono la logica del grafo |
| 6 | `docs/adr/0005-*.md` | L'architettura, blindata |
| 7 | `docs/prodotto/PROPRIETA_COMPONENTI.md` e `docs/prodotto/GRAFO_IMPIANTO.md` | I due artefatti che il PM legge e approva |
| 8 | `docs/standard/QUALITA_GRAFICA.md` | Le regole del colpo d'occhio, per chi tocca il disegno |
| 9 | `docs/standard/COLD_EYE_REVIEW.md` e `docs/prompts/cold-eye-review.md` | Protocollo dell'occhio terzo e verdetto della prima passata |
| 10 | `AGENTS.md` | Regole operative e i due ruoli |

`docs/archivio/` contiene la storia: piani eseguiti, specifica originale, handoff
precedenti. Si apre per capire **perché** una cosa è com'è, non per sapere cosa fare.

---

## 5. Stato al 6 agosto 2026

**Ramo:** `claude/layout-routing-multitable-plan-cbezrw`.
**Prove:** vedere `PROJECT_STATE.md`; `pytest`, `ruff` e `mypy --strict` verdi.
**Ambiente:** `bash scripts/setup-env.sh` — **da eseguire per primo** in una sessione cloud,
che riparte sempre da un clone pulito.

### I pezzi

| Pezzo | Stato |
|---|---|
| **G1 — il grafo e le sue sigle** | **Costruito**, collaudato alla chiusura di questa sessione |
| **G2 — il vocabolario delle proprietà** | **Approvato** (respinto al primo giro, corretto) |
| **G3 — le regole degli accessori** | **Respinto** dal collaudo, **corretto**, ri-verificato alla chiusura |
| G4 — l'assemblatore | Non iniziato |
| G5 — la libreria dei simboli | Meccanica sana, contenuto da completare |
| G6 — il cartiglio | Mai disegnato |
| G7 — la composizione | Da rifare: il foglio si riempie al 39 % e l'impianto completo non ci entra più |
| G8 — validatori e cancello dell'occhio terzo | Correttezza e preflight esistono, il cancello no |

### Il primo lavoro della prossima sessione

**Chiudere il difetto dell'ordine delle connessioni**, già diagnosticato e dimensionato.
Lo stesso impianto, con le tubazioni elencate in un altro ordine, produce **tre impianti
diversi** (22, 23 o 25 valvole su 31 rimescolamenti). La radice **non** è che due parti del
programma scelgono tubi diversi — allineare quelle due non basta, provato — è il
presupposto **«un attacco, una tubazione»**, che il catalogo stesso smentisce: un volano ha
attacchi con due. La correzione vive in `src/disegnatore_mep/rules/` e deve far portare a
un attacco **tutte** le sue tubazioni, decidendo per tubazione. Il grafo è già immune per
costruzione. Costo stimato: una sessione, per lo più ri-verifica.

Poi **G4, l'assemblatore**, che chiude un altro difetto trovato dal collaudo: oggi l'ordine
dei pezzi lungo un tubo dipende dall'**ordine alfabetico dei nomi delle regole**. Due prove
lo presidiano, ma è una coincidenza, non una struttura.

---

## 6. Ciò che non va rifatto, perché è già stato pagato

- **Non trasformare un esempio in una legge.** Il PM ha dovuto correggerlo due volte: dalla
  prima tavola di riferimento erano state ricavate le corsie a quota fissa (rimosse,
  producevano sali-scendi) e la disposizione in fila dei componenti (D-073, sbagliata allo
  stesso modo). Un esempio mostra **una** soluzione ammissibile, non l'unica.
- **Non decidere il contenuto in base a quanto ci sta sul foglio.** Le valvole di
  intercettazione erano passate da una per attacco a una per componente perché l'A3 non
  reggeva. È al contrario: cosa va disegnato lo decide l'impianto (D-074, D-072).
- **Non aggiungere un segno senza chiedersi come si legge.** I richiami delle etichette
  erano ortogonali e sottili come tubazioni, e si leggevano come tubi (D-075).
- **Non tarare una soglia su una fixture.** I criteri sono proprietà valide su qualunque
  impianto.
- **Non scrivere al PM una frase che non può verificare.** Due pezzi sono stati respinti per
  questo: un consuntivo falso delle proprietà, e una scheda che dichiarava coperto un
  bollitore il cui scarico stava sul circuito sbagliato.
- **Non far approvare al proprio autore il proprio lavoro.** È la ragione per cui il metodo
  dei tre ruoli esiste.

---

## 7. Quirks e gotcha

- **Eseguire sempre la suite completa** e `mypy src tests examples`, mai il solo file del
  task: un import circolare passava sul proprio file e falliva sull'intera suite.
- **Mai `git checkout --` o `git stash` su lavoro non committato.** In una sessione è stata
  cancellata così una correzione appena scritta.
- **Il comando delle regole vuole anche `--naming`** oltre a `--catalog`, `--symbols` e
  `--rules`: le famiglie delle sigle sono dato, non codice.
- **Il corpo dei piani archiviati contiene codice difettoso.** Le appendici finali sono le
  fonti autorevoli sulle differenze.
- **Firma dei commit:** in questo container `commit.gpgsign` è attivo con una chiave vuota,
  quindi i commit escono non firmati. Non risolvibile da dentro la sessione.
- **Gli agenti di sviluppo non committano.** Committa l'orchestratore, e i lavori a metà
  vanno come `wip:` con scritto che non sono collaudati.

---

## 8. Domande aperte per il PM

**Nessuna.** L'ultima serie — formato, verifica, ruoli, perimetro MVP, ACS, fonti — è chiusa.
Il PM ha in mano da approvare, quando vorrà, i due artefatti di prodotto: le proprietà dei
componenti e il grafo dell'impianto.

---

## Ultimo aggiornamento

`2026-08-06` — Claude — riscritto per intero sulla logica del grafo. Il PM ha corretto due
cose che hanno cambiato il progetto: il contenuto si verifica su un grafo scritto e non su
un disegno (D-096), e il grafo si legge come una rete stradale con la codifica che parte
dalle sorgenti (D-097, D-098). Da lì ha riformulato l'intera catena della skill, e la sua
formulazione è diventata quella ufficiale (D-099). Piano rinumerato in otto pezzi, si
riparte dal grafo. Costruiti il grafo con le sue sigle e le correzioni delle regole;
riconciliate due implementazioni parallele delle sigle in una sola.
