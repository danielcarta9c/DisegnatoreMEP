# HANDOFF — Disegnatore MEP · 2026-08-01

> ⛔ **STOP. Questo file NON è un riassunto del progetto.** È il cancello
> di lettura per la sessione successiva. Leggere tutti i documenti indicati
> nell'ordine sotto prima di modificare file, scrivere codice o porre domande
> al PM. Solo dopo completare le sentinel checks del §2.

---

## 1. Reading order obbligatorio

Leggere integralmente nell'ordine. I gruppi di file vanno letti al completo.

| # | File | Funzione |
|---|---|---|
| 1 | `AGENTS.md` | Regole operative e profilo di collaborazione con il PM |
| 2 | `CONTESTO_PROGETTO.md` | Storia completa e punto di partenza del progetto |
| 3 | `README.md` | Scopo e orientamento del repository |
| 4 | `PRD_DISEGNATORE_MEP.md` | Requisiti di prodotto approvati |
| 5 | `PROJECT_STATE.md` | Stato vivo e prossimo passo |
| 6 | `docs/specs/2026-08-01-disegnatore-mep-design.md` | Design consolidato e approvato |
| 7 | `docs/adr/README.md`, poi `docs/adr/0001-*.md` fino a `0004-*.md` | Decisioni architetturali in ordine cronologico |
| 8 | `docs/DECISION_LOG.md` | Decisioni funzionali D-001–D-033 |
| 9 | `docs/ROADMAP.md` | Fasi del progetto e perimetro futuro |
| 10 | `docs/plans/README.md` e `docs/plans/2026-08-01-master-implementation-roadmap.md` | Sequenza P0–P7 |
| 11 | `docs/plans/2026-08-01-foundation-core-plan.md` | Piano eseguibile da cui ripartire |
| 12 | `docs/research/README.md` e `docs/research/SOURCE_REGISTER.md` | Regole per fonti e stato della ricerca |
| 13 | `assets/cartigli/README.md` e `releases/README.md`, `releases/latest/README.md`, `releases/archive/README.md` | Vincoli su cartiglio e rilascio |
| 14 | [`nove-c-kit` PLAYBOOK](https://github.com/danielcarta9c/nove-c-kit/blob/main/PLAYBOOK.md) e [`EXAMPLES`](https://github.com/danielcarta9c/nove-c-kit/blob/main/EXAMPLES.md) | Metodo di project management Nove C |
| 15 | Questo file dal §2 in poi | Verifica di comprensione e delta operativo |

Non usare questo HANDOFF come scorciatoia. Il contenuto tecnico vive nei documenti canonici sopra.

---

## 2. Sentinel checks — verifica che hai letto

Prima di iniziare il lavoro, rispondere esplicitamente a queste domande nella nuova sessione. Se una risposta non è certa, tornare al §1.

1. Perché il prodotto non è un catalogo di schemi tipo e come si combinano nucleo universale e pacchetti di dominio?
2. Qual è la fonte di verità del progetto e quali artefatti sono soltanto derivati rigenerabili?
3. Quale dossier deve essere approvato prima di disegnare e quali scelte la skill non può compiere al posto dell'ingegnere?
4. Come deve essere rappresentato topologicamente e graficamente un componente inserito in linea, per esempio una valvola?
5. Qual è il prossimo piano operativo, è già iniziato e quale decisione deve chiedere al PM prima di partire?

Risposte attese dai documenti: motore compositivo generale; modello tecnico canonico; approvazione preventiva di interpretazione, integrazioni, assunzioni, domande, tavole e metadati; nessun dimensionamento o selezione autonoma delle apparecchiature principali; connessione spezzata e mai simbolo sovrapposto a linea continua; P0 non ancora iniziato e nessuna decisione tecnica da scaricare sul PM.

---

## 3. Stato attuale del progetto

- **Versione installabile:** nessuna; `releases/latest/` non è ancora una release.
- **Ultimo commit significativo prima della chiusura:** `abfa683` — milestone della pianificazione registrata.
- **Stato prodotto:** design approvato; roadmap P0–P7 e piano dettagliato P0 pronti.
- **Implementazione:** non iniziata; non esistono ancora pacchetto Python, test o artefatti generati.
- **Repository:** Git locale, branch `main`, nessun remote.
- **In flight:** nessuna modifica applicativa a metà.
- **Blocco:** nessun blocco di progetto; sessione chiusa volontariamente e in modo prudenziale per il possibile esaurimento del limite d'uso, che l'app non espone in modo verificabile.
- **Check rapido alla ripresa:** `git status --short` deve essere vuoto e `git log -1 --oneline` deve mostrare il commit di chiusura.

---

## 4. Cosa è cambiato dall'ultima sessione (delta)

- Il design è stato approvato e consolidato nella specifica, nei quattro ADR e nelle decisioni D-001–D-033.
- Sono stati creati la roadmap master e il piano eseguibile P0 con gate e verifiche.
- Sono stati registrati come futuro remoto del progetto generale le tavole planimetriche e gli schemi elettrici esecutivi completi; restano fuori scope della skill attuale.
- Tutte queste modifiche sono già promosse nei documenti canonici: non ricostruirle da questo elenco.

---

## 5. In-flight task — dove sei rimasto

- **Task:** P0 — fondazione canonica e validatore multi-dominio.
- **Branch:** `main`.
- **Ultimo commit di lavoro:** `abfa683` — milestone della pianificazione.
- **Cosa è stato fatto:** piano P0 completo e verificato come documento.
- **Cosa stava per iniziare:** esecuzione di `docs/plans/2026-08-01-foundation-core-plan.md` dal Task 1.
- **Cosa è dubbio / non deciso:** nulla di prodotto; i dettagli di esecuzione sono responsabilità tecnica dell'agente.
- **Loci di interesse:** `docs/plans/2026-08-01-foundation-core-plan.md`; `docs/plans/2026-08-01-master-implementation-roadmap.md`; `PROJECT_STATE.md`.
- **Stato test:** nessuna suite ancora presente perché l'implementazione non è iniziata.

Alla ripresa usare il piano inline con gate di revisione. Non chiedere al PM di scegliere fra modalità tecniche di esecuzione.

---

## 6. Decisioni di questa sessione (mini-ADR cronologici)

- Le decisioni di prodotto sono già promosse in `docs/DECISION_LOG.md` D-001–D-033.
- Le decisioni strutturali sono già promosse negli ADR 0001–0004.
- Il design approvato è consolidato in `docs/specs/2026-08-01-disegnatore-mep-design.md`.
- Nessun mini-ADR resta da promuovere.

---

## 7. Quirks e gotcha emersi (non duplicati altrove)

- **OneDrive:** il repository è in una cartella sincronizzata; evitare modifiche contemporanee da due computer e verificare lo stato Git prima di intervenire.
- **Cartiglio PDF:** le anomalie di font osservate in ispezione sono già descritte nella specifica approvata; consultarla prima di costruire il rendering.
- **Quota dell'app:** non è disponibile un indicatore interrogabile del limite residuo o dell'ora di ripristino; non inventare stime.

---

## 8. Cross-refs — dove vivono le cose

| Quando serve sapere… | File del progetto | Riferimento nel kit |
|---|---|---|
| Come collaborare con il PM | `AGENTS.md` | PLAYBOOK §23 e §36 |
| Qual è il prodotto e cosa esclude | `PRD_DISEGNATORE_MEP.md` | — |
| Perché il motore è generale | ADR 0001 e specifica approvata | — |
| Qual è la fonte di verità | ADR 0002 | — |
| Come gestire scala e tavole | ADR 0003 | — |
| Perché si approva prima di disegnare | ADR 0004 | — |
| Qual è il prossimo passo | `PROJECT_STATE.md` e piano P0 | PLAYBOOK §32 |
| Dove trovare le decisioni | `docs/DECISION_LOG.md` e `docs/adr/` | — |
| Come gestire fonti tecniche | `docs/research/SOURCE_REGISTER.md` | — |
| Come produrre una release | `releases/README.md` | — |

---

## 9. Domande aperte per il PM

Nessuna. Alla ripresa non chiedere al PM di ricostruire il contesto né di scegliere dettagli informatici reversibili. Completare il cancello di lettura, dichiarare brevemente il punto ritrovato e iniziare P0 quando il PM dice di procedere.

---

## Ultimo aggiornamento

`2026-08-01` — Codex — creato il cancello di lettura per la chiusura pulita della sessione prima dell'implementazione P0.

