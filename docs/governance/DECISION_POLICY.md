# Policy delle decisioni

> Come nasce, vive e si chiude una decisione. Si applica a `docs/DECISION_LOG.md` e, per le
> decisioni strutturali e costose da cambiare, agli ADR in `docs/adr/`.
>
> Questa policy **non rinumera e non riscrive** le decisioni esistenti. Vale da GOV-001 in
> avanti; le decisioni precedenti si leggono con la chiave di vocabolario in
> `OPERATING_MODEL.md` (§4).

---

## 1. I cinque stati

Una decisione attraversa cinque stati, in quest'ordine. **Ogni transizione ha un'autorità
esplicitamente assegnata**, e nessuno può eseguire una transizione che non è sua. Non vale
il contrario — PM e DEV sono autorità di più di una transizione — ma **nessuna transizione
ha due autorità**.

| # | Stato | Transizione, e chi ha l'autorità di eseguirla | Che cosa afferma | Che cosa **non** afferma |
|---|---|---|---|---|
| 1 | **Proposta** | *(nasce)* — **DEV o PM** | Esiste un'opzione, con motivazione e alternative scartate | Che si farà, né che si possa cominciare |
| 2 | **Approvata dal PO** | 1 → 2, **solo il PO** | Il PO vuole questa cosa | Che sia pianificata o fattibile ora |
| 3 | **Pianificata dal PM** | 2 → 3, **solo il PM** | È in un pacchetto di lavoro, con criteri di accettazione | Che sia implementata |
| 4 | **Implementata dal DEV** | 3 → 4, **solo il DEV** | Il codice o i documenti la realizzano, su un ramo, con la PR aperta | Che sia verificata o accettata |
| 5 | **Verificata dal PM** | 4 → 5, **solo il PM** | I criteri di accettazione sono soddisfatti; la PR può essere fusa | — |

Stati terminali alternativi:

| Stato | Chi lo assegna | Significato |
|---|---|---|
| **Respinta** | PO (di merito) o PM (di pianificazione) | Non si fa. Si dice perché. |
| **Ritirata** | Chi l'aveva proposta | La proposta cade prima di essere approvata. |
| **Superata da D-NNN** | PO | Una decisione successiva la sostituisce. **La decisione superata non si riscrive né si cancella**: cambia solo lo stato. |

---

## 2. Chi non può fare cosa

- **Il DEV non può marcare una decisione come approvata.** Può registrarne una in stato
  *Proposta*, con il proprio nome, e può portarla al PM. Lo stato *Approvata dal PO* lo
  assegna il PO, in modo tracciabile (una sua frase, citata).
- **Il DEV non può passare una decisione a *Verificata*.** L'autovalutazione non esiste:
  il verdetto è del PM.
- **Il PM non decide il merito degli ambiti del PO** — dominio MEP, requisiti di prodotto,
  convenzioni e qualità della rappresentazione grafica, risultato funzionale atteso. Può
  respingere per pianificazione, costo o perimetro; non può approvare al posto del PO.
- **Il DEV non sostituisce una soluzione prescritta dal PO** con una che ritiene migliore.
  La propone come decisione nuova, in stato *Proposta*, e aspetta il PO.

### 2.1 Niente implementazione prima dell'approvazione del PO

**Regola univoca, senza eccezioni.** Una decisione che riguarda **prodotto, dominio MEP o
rappresentazione grafica**:

1. **non può essere pianificata per l'implementazione** finché non è `Approvata dal PO`;
2. **non può essere implementata** finché non è `Approvata dal PO`;
3. finché è `Proposta` **può essere soltanto analizzata o sottoposta al PO**. Nient'altro.

Il PM **non ha** la facoltà di far procedere l'implementazione di una decisione ancora
*Proposta*: la transizione 2 → 3 richiede che lo stato 2 esista, e non esiste scorciatoia
che lo aggiri. Se serve procedere, si chiede l'approvazione al PO — non si procede
lasciando la decisione *Proposta*.

**Attività esplorativa.** Il PM può autorizzare uno studio, uno spike o un prototipo su una
decisione ancora *Proposta*. Vale a tre condizioni, tutte necessarie:

- **non costituisce implementazione** e non fa avanzare la decisione di stato;
- **non entra nel prodotto**: né in `main`, né in una PR di prodotto, né negli artefatti
  consegnati al PO;
- **non rende vigente la decisione**, qualunque risultato produca.

**Il DEV non può usare uno spike, un prototipo o un test come autorizzazione implicita a
cambiare il prodotto.** «Funzionava nel prototipo» non è un'approvazione del PO. Se
l'esplorazione mostra che la decisione va presa, il risultato si porta al PO come materiale
per decidere, e si aspetta lo stato 2.

---

## 3. Forma di una riga

Le righe esistenti restano come sono. Le nuove si scrivono così:

```
| D-NNN | AAAA-MM-GG | <Stato> | <La decisione, in una frase che si capisce da sola.> | <Motivazione: da cosa nasce, con la fonte o la citazione del PO.> |
```

Regole:

- **Il numero non si riusa e non si rinumera.** Mai. Un numero bruciato resta bruciato.
- **La motivazione cita la fonte.** Per il dominio MEP: norma tramite fonte secondaria
  verificata, schema di produttore, o frase esplicita del PO. **La mancanza di fonte è una
  domanda al PO, non una licenza** (D-083).
- **Una decisione superata non si modifica nel merito**: si cambia solo il campo *Stato* in
  «Superata da D-NNN».
- Le decisioni **strutturali e costose da cambiare** vanno in un ADR dedicato in
  `docs/adr/`, e nel decision log resta la riga che lo indica.

---

## 4. Il ciclo, in pratica

```
   ┌──────────┐   PO approva   ┌───────────────────┐   PM pianifica   ┌────────────────────┐
   │ Proposta │───────────────▶│ Approvata dal PO  │─────────────────▶│ Pianificata dal PM │
   └────┬─────┘                └─────────┬─────────┘                  └──────────┬─────────┘
        │                                │                                       │
        │ ritirata                       │ respinta (merito, PO)                 │ DEV implementa
        ▼                                ▼                                       ▼
   ┌──────────┐                    ┌──────────┐                     ┌────────────────────────┐
   │ Ritirata │                    │ Respinta │                     │ Implementata dal DEV   │
   └──────────┘                    └──────────┘                     └───────────┬────────────┘
                                                                                 │ PM verifica
                                                                                 ▼
                                                                    ┌────────────────────────┐
                                                                    │  Verificata dal PM     │
                                                                    └────────────────────────┘
```

**Non esiste una freccia da *Proposta* a *Pianificata* né da *Proposta* a *Implementata*.**
Ogni percorso verso l'implementazione passa per *Approvata dal PO* (§2.1). Un'attività
esplorativa autorizzata dal PM non è un ramo di questo diagramma: gira a vuoto accanto a
*Proposta* e non muove la decisione di uno stato.

Il ritorno indietro è sempre ammesso e si registra: una decisione *Implementata* che il PM
respinge in verifica torna a *Pianificata*, e il pacchetto torna in lavorazione.

---

## 5. Rapporto con gli input del PO

Una decisione e un input del PO sono cose diverse e non si sostituiscono a vicenda.

- Un input del PO vive in `docs/input-pm/REGISTRO.md` e **esce solo chiuso dal PO o
  ritirato dal PO**. Il DEV può proporne la chiusura portando le prove; non la esegue.
- Una decisione può **nascere** da un input, e in quel caso la riga dell'input cita la
  decisione. Approvare la decisione **non chiude** l'input: la chiusura resta un atto
  separato e del PO.
- Se un input contiene più cose da fare, restano più righe, anche quando una sola decisione
  le copre tutte.
