# Policy delle decisioni

> Come nasce, vive e si chiude una decisione. Si applica a `docs/DECISION_LOG.md` e, per le
> decisioni strutturali e costose da cambiare, agli ADR in `docs/adr/`.
>
> Questa policy **non rinumera e non riscrive** le decisioni esistenti. Vale da GOV-001 in
> avanti; le decisioni precedenti si leggono con la chiave di vocabolario in
> `OPERATING_MODEL.md` (§4).

---

## 1. I cinque stati

Una decisione attraversa cinque stati, in quest'ordine. **Ogni stato ha un proprietario
diverso**, e nessuno può assegnare uno stato che non è suo.

| # | Stato | Chi lo assegna | Che cosa afferma | Che cosa **non** afferma |
|---|---|---|---|---|
| 1 | **Proposta** | DEV o PM | Esiste un'opzione, con motivazione e alternative scartate | Che si farà |
| 2 | **Approvata dal PO** | **PO** | Il PO vuole questa cosa | Che sia pianificata o fattibile ora |
| 3 | **Pianificata dal PM** | **PM** | È in un pacchetto di lavoro, con criteri di accettazione | Che sia implementata |
| 4 | **Implementata dal DEV** | DEV | Il codice o i documenti la realizzano, su un ramo, con la PR aperta | Che sia verificata o accettata |
| 5 | **Verificata dal PM** | **PM** | I criteri di accettazione sono soddisfatti; la PR può essere fusa | — |

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
- **Il PM non decide il merito di dominio MEP.** Può respingere per pianificazione, costo o
  perimetro; non può approvare al posto del PO una scelta impiantistica.
- **Nessuno salta lo stato 2.** Una decisione non può essere *Pianificata* se non è
  *Approvata dal PO*. Se il PM ha bisogno di procedere prima, il pacchetto lo dice
  esplicitamente e la decisione resta *Proposta*.

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
