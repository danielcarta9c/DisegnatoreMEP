# Modello operativo — PO / PM / DEV

> Documento di governance. Descrive **chi decide cosa** e **come il lavoro arriva su
> `main`**. Non contiene requisiti di prodotto e non modifica decisioni esistenti.
>
> **Stato: candidato nella PR #1** del pacchetto GOV-001. **Diventa vigente soltanto con il
> merge della PR, dopo la verifica del PM.** Finché la PR non è fusa, questo documento non
> è una regola in vigore, e il DEV non può dichiararlo approvato o vigente da sé.

---

## 1. I tre ruoli

| Ruolo | Chi | Autorità | Non può |
|---|---|---|---|
| **PO** — Product Owner | Daniel Carta | Dominio MEP; requisiti di prodotto; convenzioni e qualità della rappresentazione grafica; risultato funzionale atteso. Più: priorità, approvazione delle decisioni, chiusura dei propri input | — |
| **PM** — Project Manager | Codex | Pacchetti di lavoro, criteri di accettazione, accettazione o rifiuto delle consegne, pianificazione | Decidere al posto del PO su uno dei suoi quattro ambiti |
| **DEV** — team di sviluppo | Claude | Esecuzione dentro il perimetro assegnato; scelte implementative **reversibili** che non toccano requisiti, decisioni MEP, convenzioni grafiche o criteri di accettazione; proposte tecniche motivate; rapporti di consegna | Approvare decisioni, chiudere input del PO, cambiare criteri di accettazione, promuovere ipotesi a requisiti, ampliare il perimetro, **sostituire o reinterpretare una soluzione prescritta dal PO** |

### 1.1 PO — Product Owner

È l'**autorità** su quattro ambiti:

1. il **dominio MEP**;
2. i **requisiti di prodotto**;
3. le **convenzioni e la qualità della rappresentazione grafica**;
4. il **risultato funzionale atteso**.

**Una sua disposizione su questi ambiti è vincolante e va implementata come è espressa**,
anche quando è formulata in termini tecnici: il PO può prescrivere una soluzione, non solo
segnalare che qualcosa non va, e la sua prescrizione non è una proposta da valutare.

Gli appartengono in esclusiva:

- l'approvazione di una decisione (`docs/DECISION_LOG.md`, stato *Approvata dal PO*);
- la chiusura o il ritiro di una riga di `docs/input-pm/REGISTRO.md`;
- il giudizio su «è questo che volevo».

#### 1.1.1 Come il DEV tratta una disposizione del PO

- **La implementa come è espressa.** Deve cercare la **causa tecnica** del difetto — è il
  suo lavoro — ma **non può sostituire, reinterpretare o annullare la soluzione prescritta
  dal PO** perché ne ritiene preferibile un'altra.
- **Un'alternativa si propone e si aspetta.** Il DEV la scrive, la motiva, la porta al PM e
  attende **una nuova decisione**. Fino ad allora vale la disposizione del PO.
- **Impossibile, ambigua o contraddittoria → ci si ferma e si riporta al PM.** Non si
  aggira, non si interpreta a proprio favore, non si implementa a metà.
- **Senza fonte verificabile o decisione esplicita del PO, un contenuto MEP resta una
  domanda aperta.** Non è una decisione già presa dal PO e non è un vuoto da colmare con
  un'ipotesi: non si inventa, si chiede.

> **Il precedente misurato è la linea di terra (D-121).** Il PO aveva disposto due volte di
> togliere il divieto di passare sotto la quota di terra; non fu fatto, perché la soluzione
> in essere sembrava preferibile a chi la manteneva, e il danno arrivò su una tavola che lui
> vide. **Una prescrizione del PO non si ignora perché il DEV ritiene migliore un'altra
> soluzione.**

### 1.2 PM — Project Manager

Assegna i pacchetti di lavoro e li giudica.

Gli appartengono:

- la scrittura del pacchetto **prima** che il lavoro cominci: obiettivi, perimetro dei file,
  criteri di accettazione (`WORK_PACKAGE_TEMPLATE.md`);
- la pianificazione: cosa si fa prima, cosa dopo, cosa non si fa adesso;
- l'**accettazione o il rifiuto** della consegna, criterio per criterio;
- la porta d'ingresso su `main`: nessuna PR entra senza la sua accettazione.

### 1.3 DEV — team di sviluppo

Esegue. Può **proporre** alternative tecniche e deve motivarle. Il metodo interno del DEV
(orchestratore, sviluppatori, collaudo indipendente — D-083) resta in vigore e sta **sotto**
l'assegnazione del PM: un verdetto positivo del collaudo abilita la **consegna**, non
l'accettazione.

**La sua autonomia tecnica ha un confine preciso**: copre le **scelte implementative
reversibili** che non toccano requisiti, decisioni MEP, convenzioni grafiche o criteri di
accettazione — formati interni, algoritmi, librerie, strutture dati. Tutto ciò che tocca uno
dei quattro ambiti del PO non è autonomia tecnica, qualunque forma tecnica abbia.

Sei divieti, senza eccezioni:

1. **Non marca una decisione come approvata.** Può proporre; lo stato *Approvata dal PO* è
   del PO.
2. **Non chiude un input del PO.** Può portare le prove e chiedere la chiusura.
3. **Non modifica i criteri di accettazione per far passare le verifiche.** Un criterio
   impossibile, sbagliato o ambiguo si segnala al PM e si aspetta.
4. **Non trasforma una propria ipotesi in requisito.** L'assunzione resta dichiarata come
   tale finché il PO non la conferma.
5. **Non amplia il perimetro del pacchetto.** Ciò che scopre fuori perimetro lo nomina nel
   rapporto e lo lascia dov'è.
6. **Non sostituisce, reinterpreta o annulla una soluzione prescritta dal PO** perché ne
   ritiene preferibile un'altra (§1.1.1). La propone e aspetta una nuova decisione.

E una regola di consegna: **il DEV non dichiara autonomamente completato il proprio
lavoro.** Consegna e aspetta il verdetto del PM.

---

## 2. Il flusso di un pacchetto

```
PO                    PM                         DEV
 │                     │                          │
 │ input / decisione   │                          │
 ├────────────────────▶│                          │
 │                     │ scrive il pacchetto      │
 │                     │ (obiettivi, perimetro,   │
 │                     │  criteri di accettazione)│
 │                     ├─────────────────────────▶│
 │                     │                          │ ramo dedicato
 │                     │                          │ implementa + verifica
 │                     │                          │ apre la PR
 │                     │◀─────────────────────────┤ rapporto di consegna
 │                     │ verifica criterio        │
 │                     │ per criterio             │
 │                     │                          │
 │                     ├── respinto ─────────────▶│ torna in lavorazione
 │                     │                          │
 │                     └── accettato ──▶ merge della PR su `main`
 │                                                 │
 │◀── il PO vede il risultato, non l'implementazione
```

Nessuna freccia salta un passaggio. In particolare: **non esiste una freccia dal DEV a
`main`.**

---

## 3. Rami, PR e `main`

### 3.1 La regola approvata (D-123, PO, 31 agosto 2026)

> «Ogni unità di lavoro completata viene immediatamente salvata sul ramo remoto. Ogni Work
> Package usa un ramo dedicato e una PR. Il lavoro entra in `main` soltanto dopo verifica e
> accettazione del PM. I rami devono essere brevi, visibili e censiti; non possono esistere
> sviluppi paralleli sovrapposti senza autorizzazione del PM.»

Ne discendono nove obblighi operativi:

1. **Un pacchetto, un ramo dedicato.** Il nome del ramo lo dà il pacchetto.
2. **Su `main` si arriva solo tramite pull request**, dopo l'accettazione del PM.
3. **Nessun merge diretto su `main`**, né dal DEV né in locale.
4. **Il DEV non fonde e non chiude la propria PR.** La apre, la porta in stato
   revisionabile e si ferma.
5. **Ogni unità di lavoro compiuta si salva subito sul ramo remoto**, non solo alla fine:
   una sessione può interrompersi senza preavviso.
6. **I conflitti si risolvono dentro il pacchetto**, non si aggirano aprendo un ramo nuovo.
   Ciò che resta fuori si scrive in `PROJECT_STATE.md` col nome del ramo.
7. **All'apertura di una sessione si censiscono i rami divergenti esistenti.** Elencarli è
   obbligatorio. Fonderli, cancellarli o recuperarne i commit richiede un pacchetto che lo
   chieda esplicitamente.
8. **I rami sono brevi.** Un pacchetto che cresce oltre la propria misura torna dal PM e si
   spezza: un ramo lungo è un ramo che diverge.
9. **Nessuno sviluppo parallelo sovrapposto senza autorizzazione del PM.** Due rami che
   toccano la stessa area nello stesso momento esistono solo se il PM lo ha deciso.

### 3.2 Rapporto con D-117, che è superata

L'obbligo precedente — «una sessione finisce su `main`, sempre» (**D-117**) — nasceva da un
guasto reale: l'8 agosto lo sviluppo si biforcò in due rami che non si videro mai, e una
correzione del PO restò invisibile per due giorni. Il problema che quell'obbligo risolveva
è **lavoro che si perde perché nessun elenco lo nomina**, ed è reale.

**D-123 conserva quell'obiettivo e cambia il mezzo**, separando due cose che D-117 teneva
insieme:

- il **salvataggio**, che resta immediato e non negoziabile: ogni unità di lavoro compiuta
  finisce subito sul ramo remoto, quindi nulla vive solo in locale (obbligo 5);
- l'**integrazione in `main`**, che smette di essere automatica e diventa un atto del PM su
  una PR verificata (obblighi 2–4).

Ciò che il merge proteggeva lo proteggono ora tre obblighi insieme: **push immediato**,
**rami brevi** (8) e **censimento** dei rami a ogni sessione (7). Il divieto di sviluppi
paralleli sovrapposti (9) è la parte di D-117 che sopravvive immutata.

Ciò che si guadagna è la **revisione**: il merge diretto rende impossibile per il PM
respingere una consegna, perché quando la vede è già dentro `main`.

Stato formale: **D-117 è `Superata da D-123`** nel decision log; il suo testo e la sua
motivazione non sono stati riscritti. Fra `AGENTS.md`, questo documento e
`docs/DECISION_LOG.md` **non resta alcuna contraddizione vigente** su ramo, PR e merge.

---

## 4. Vocabolario storico

Nei documenti scritti prima di questo modello — `docs/DECISION_LOG.md`,
`docs/input-pm/REGISTRO.md`, i piani in `docs/plans/`, i collaudi in `docs/collaudi/` — la
parola **«PM» indica Daniel Carta**, cioè quello che oggi si chiama **PO**.

Quei documenti **non vanno riscritti**: si leggono con questa chiave. Il percorso
`docs/input-pm/` resta invariato per la stessa ragione — rinominarlo spezzerebbe i
riferimenti senza aggiungere una sola informazione.

| Documento storico | Dice | Oggi si legge |
|---|---|---|
| `docs/input-pm/REGISTRO.md` | PM | PO (Daniel Carta) |
| `docs/DECISION_LOG.md` | PM | PO (Daniel Carta) |
| D-083, «l'orchestratore» | orchestratore | orchestratore **interno al DEV** |
| D-083, «il committente» | committente | PO |

**D-124** (PO, 1 settembre 2026) ha sostituito il precedente **modello a due ruoli** —
fissato da D-068, ora `Superata da D-124` — con il modello **PO/PM/DEV** descritto in §1, e
ha stabilito che **le disposizioni del PO possono essere tecniche e sono vincolanti**. Di
D-068 restano valide le parti che non riguardavano l'autorità tecnica: il PO giudica il
risultato, la comunicazione verso di lui è essenziale, il dettaglio implementativo vive nei
documenti tecnici.

---

## 5. Documenti di questo modello

| Documento | A cosa serve | Chi lo scrive |
|---|---|---|
| `OPERATING_MODEL.md` | Ruoli, flusso, regole su rami e PR | PM (proposta del DEV) |
| `WORK_PACKAGE_TEMPLATE.md` | Forma di un pacchetto di lavoro | PM |
| `DECISION_POLICY.md` | Ciclo di vita di una decisione | PM, con approvazione del PO |
| `.github/pull_request_template.md` | Forma di una consegna | DEV compila, PM giudica |
