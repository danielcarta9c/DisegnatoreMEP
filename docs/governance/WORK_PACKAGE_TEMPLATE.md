# Template di pacchetto di lavoro

> Il pacchetto lo scrive il **PM**, **prima** che il lavoro cominci. Il DEV non lo modifica:
> se un criterio è impossibile, sbagliato o ambiguo, lo segnala e si ferma.
>
> Un pacchetto senza criteri di accettazione non è un pacchetto: è una richiesta.

---

## Come si usa

1. Il PM copia il blocco qui sotto e lo compila.
2. Il pacchetto prende un **identificatore** (`AREA-NNN`, es. `GOV-001`, `DRAW-014`) e dà
   il nome al **ramo dedicato**.
3. Il DEV esegue solo ciò che è nel perimetro, apre la PR e consegna il rapporto finale.
4. Il PM accetta o respinge **criterio per criterio**.

---

## Blocco da compilare

```markdown
# <AREA-NNN> — <titolo breve>

**Assegnato da:** PM (Codex)
**Assegnato a:** DEV
**Data:** AAAA-MM-GG
**Ramo:** <nome-ramo-dedicato>
**Commit di partenza:** <SHA di `main` atteso>

## Contesto
<Due o tre frasi: da dove nasce il pacchetto. Input del PO collegati, decisioni
collegate, difetto che lo motiva.>

## Obiettivi
1. <obiettivo verificabile>
2. <obiettivo verificabile>

## Perimetro dei file — modifiche consentite esclusivamente a:
- `<percorso>`
- `<percorso>`

## Fuori perimetro — da non toccare
- <codice, test, esempi, asset, regole, schemi, decisioni esistenti, stato degli input PO…>

## Vincoli
- <es. nessun merge su `main`>
- <es. nessuna decisione esistente rinumerata o riscritta>
- <es. nessun input del PO chiuso>

## Criteri di accettazione
- [ ] <criterio osservabile, verificabile da chi non ha fatto il lavoro>
- [ ] <criterio osservabile>
- [ ] <criterio osservabile>

## Consegna attesa
- Una sola PR, pronta per la revisione del PM, non fusa.
- Rapporto finale con: ramo, SHA iniziale, SHA finale, file modificati, verifiche
  eseguite, difetti noti, link alla PR.
- <eventuali elenchi richiesti, es. rami divergenti esistenti>

## In caso di ambiguità
Fermarsi e riportarla. Non decidere al posto del PO né del PM.
```

---

## Regole di scrittura di un criterio di accettazione

Un criterio è utilizzabile solo se **chi non ha fatto il lavoro** può verificarlo da solo.

| Scrivere così | Non così |
|---|---|
| «Nessun file fuori dall'elenco consentito risulta modificato nel diff» | «Le modifiche sono contenute» |
| «`docs/DECISION_LOG.md` è identico al commit di partenza» | «Le decisioni sono rispettate» |
| «Il rapporto elenca tutti i rami remoti divergenti da `main`» | «I rami sono sotto controllo» |
| «La PR è aperta e non fusa» | «Il lavoro è pronto» |

Un criterio che contiene «adeguato», «pulito», «ragionevole» o «se possibile» non è un
criterio: è un'opinione delegata al DEV, ed è esattamente ciò che questo modello impedisce.

---

## Regole di esecuzione per il DEV

- Si toccano **solo** i file del perimetro. Un file fuori perimetro modificato è un
  pacchetto respinto, anche se la modifica era giusta.
- Un'ipotesi resta un'ipotesi: si dichiara nel rapporto, non diventa requisito.
- Una decisione nuova si registra come **Proposta** (vedi `DECISION_POLICY.md`), mai come
  *Approvata*.
- Nessun input del PO viene chiuso: al massimo se ne propone la chiusura.
- Il DEV **non dichiara completato** il pacchetto: consegna, e aspetta il verdetto del PM.
