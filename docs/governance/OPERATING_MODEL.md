# Modello operativo — PO / PM / DEV

> Documento di governance. Descrive **chi decide cosa** e **come il lavoro arriva su
> `main`**. Non contiene requisiti di prodotto e non modifica decisioni esistenti.
>
> Stato: **proposto dal DEV nel pacchetto GOV-001**, in attesa di accettazione del PM.

---

## 1. I tre ruoli

| Ruolo | Chi | Autorità | Non può |
|---|---|---|---|
| **PO** — Product Owner | Daniel Carta | Dominio MEP, cosa deve fare il prodotto, priorità, approvazione delle decisioni, chiusura dei propri input | — |
| **PM** — Project Manager | Codex | Pacchetti di lavoro, criteri di accettazione, accettazione o rifiuto delle consegne, pianificazione | Decidere al posto del PO sul dominio MEP |
| **DEV** — team di sviluppo | Claude | Esecuzione dentro il perimetro assegnato, proposte tecniche motivate, rapporti di consegna | Approvare decisioni, chiudere input del PO, cambiare criteri di accettazione, promuovere ipotesi a requisiti, ampliare il perimetro |

### 1.1 PO — Product Owner

È **l'autorità sul dominio MEP**. Un contenuto tecnico di dominio senza fonte verificabile
è una sua decisione, non un vuoto da colmare con un'ipotesi.

Gli appartengono in esclusiva:

- l'approvazione di una decisione (`docs/DECISION_LOG.md`, stato *Approvata*);
- la chiusura o il ritiro di una riga di `docs/input-pm/REGISTRO.md`;
- il giudizio su «è questo che volevo».

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

Cinque divieti, senza eccezioni:

1. **Non marca una decisione come approvata.** Può proporre; lo stato *Approvata* è del PO.
2. **Non chiude un input del PO.** Può portare le prove e chiedere la chiusura.
3. **Non modifica i criteri di accettazione per far passare le verifiche.** Un criterio
   impossibile, sbagliato o ambiguo si segnala al PM e si aspetta.
4. **Non trasforma una propria ipotesi in requisito.** L'assunzione resta dichiarata come
   tale finché il PO non la conferma.
5. **Non amplia il perimetro del pacchetto.** Ciò che scopre fuori perimetro lo nomina nel
   rapporto e lo lascia dov'è.

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

### 3.1 Le regole

1. **Un pacchetto, un ramo dedicato.** Il nome del ramo lo dà il pacchetto.
2. **Su `main` si arriva solo tramite pull request**, dopo l'accettazione del PM.
3. **Nessun merge diretto su `main`**, né dal DEV né in locale.
4. **Il DEV non fonde e non chiude la propria PR.** La apre, la porta in stato
   revisionabile e si ferma.
5. **Si spinge sul proprio ramo dopo ogni unità di lavoro compiuta**, non solo alla fine:
   una sessione può interrompersi senza preavviso.
6. **I conflitti si risolvono dentro il pacchetto**, non si aggirano aprendo un ramo nuovo.
   Ciò che resta fuori si scrive in `PROJECT_STATE.md` col nome del ramo.
7. **All'apertura di una sessione si elencano i rami divergenti esistenti.** Elencarli è
   obbligatorio. Fonderli, cancellarli o recuperarne i commit richiede un pacchetto che lo
   chieda esplicitamente.

### 3.2 Perché non si fonde più ogni sessione su `main`

L'obbligo precedente — «una sessione finisce su `main`, sempre» — nasceva da un guasto
reale: l'8 agosto lo sviluppo si biforcò in due rami che non si videro mai, e una
correzione del PO restò invisibile per due giorni. Il problema che quell'obbligo risolveva
è **lavoro che si perde perché nessun elenco lo nomina**, ed è reale.

Il modello PO/PM/DEV lo risolve diversamente, senza rinunciare alla garanzia:

- ciò che rendeva invisibile il lavoro non era il ramo, era l'**assenza di un elenco**: qui
  l'elenco è il pacchetto, e i rami divergenti si elencano a ogni sessione (regola 7);
- il push frequente sul ramo resta obbligatorio (regola 5), quindi nulla vive solo in
  locale;
- ciò che si guadagna è la **revisione**: il merge diretto rende impossibile per il PM
  respingere una consegna, perché quando la vede è già dentro.

> **Punto aperto per il PO.** L'obbligo di merge diretto è registrato come decisione
> **D-117**, in stato *Approvata*. Questo pacchetto **non l'ha toccata**: superarla
> formalmente è una decisione del PO. Finché il PO non si pronuncia, `AGENTS.md` e
> `docs/DECISION_LOG.md` divergono su questo punto, e la divergenza è dichiarata qui e in
> `AGENTS.md` invece di essere risolta d'ufficio dal DEV.

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

---

## 5. Documenti di questo modello

| Documento | A cosa serve | Chi lo scrive |
|---|---|---|
| `OPERATING_MODEL.md` | Ruoli, flusso, regole su rami e PR | PM (proposta del DEV) |
| `WORK_PACKAGE_TEMPLATE.md` | Forma di un pacchetto di lavoro | PM |
| `DECISION_POLICY.md` | Ciclo di vita di una decisione | PM, con approvazione del PO |
| `.github/pull_request_template.md` | Forma di una consegna | DEV compila, PM giudica |
