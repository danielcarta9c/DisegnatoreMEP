# Disegnatore MEP

Skill/tool installabile da usare nelle chat di lavoro, che trasforma un impianto
termotecnico **già deciso e dimensionato dall'ingegnere** in una tavola tecnica
professionale, pronta da stampare e da portare in cantiere.

La skill non progetta: non inventa potenze, temperature, prevalenze, tarature, volumi né
diametri. Interpreta l'impianto, propone gli accessori mancanti motivandoli, li fa
approvare, e poi disegna.

## Da dove si comincia

1. **`ACTIVE_WORK_PACKAGE.md`** — l'unico incarico operativo corrente.
2. **`HANDOFF.md`** — missione, catena invariabile, stato sintetico, confini PO/agente.
3. **`docs/ARCHITETTURA-DEL-PIANO.md`** — **chi decide cosa nel disegno.** Vigente dal 20
   settembre 2026 (D-151): il disegno lo compone un agente — pianificatore → motore →
   revisore — e non lo trova un solutore. Si legge prima di toccare il disegno.
4. **`docs/SKILL.md`** — com'è fatta la skill: i pezzi, cosa fa ciascuno e quando è
   finito.
5. **`docs/regole-del-piano.md`** — le regole con cui si compone una tavola, ciascuna con
   la propria fonte e il proprio controllo. Aperto per dichiarazione del PO.
6. **`PROJECT_STATE.md`** — a che punto siamo e cosa manca. È l'unico posto in cui è
   scritto lo stato.
7. **`AGENTS.md`** — come si lavora: il PO e l'agente, il metodo, come si consegna.

`CLAUDE.md` è l'istruzione di ingresso dell'agente che sviluppa il repository, e ripete
questo ordine in forma breve. Il resto si apre quando serve.

## Com'è organizzata la repository

| Area | Dove | Cosa contiene |
|---|---|---|
| **Prodotto — dati** | `rules/`, `assets/`, `schemas/` | Le regole degli accessori (un file per regola), la libreria dei simboli, il cartiglio aziendale, gli schemi dei dati. **Si modificano senza toccare il programma.** |
| **Sviluppo** | `src/`, `tests/`, `scripts/`, `pyproject.toml` | Il programma e le sue prove. |
| **Esempi** | `examples/` | Impianti di prova e cataloghi di esempio. Servono a **scoprire** i difetti, mai a definire cosa è giusto. |
| **Documentazione** | `docs/` | Vedi sotto. |
| **Release** | `releases/` | Le versioni installabili: `latest/` e l'archivio numerato. |
| **Lavoro** | `outputs/` | Uscite di prova, non versionate. |

### Dentro `docs/`

| Cartella | Cosa c'è |
|---|---|
| `docs/ARCHITETTURA-DEL-PIANO.md` | **Chi decide cosa nel disegno**, da D-151. Vince su ogni contrasto. |
| `docs/regole-del-piano.md` | **Le regole con cui si compone**, con fonte e controllo. Aperto. |
| `docs/SKILL.md` | **Com'è fatta la skill.** Una sola fonte. |
| `docs/DECISION_LOG.md` | Perché abbiamo deciso così, in ordine di tempo. |
| `docs/DEFERRED.md` | Cosa è stato rimandato, e cosa lo sbloccherebbe. |
| `docs/adr/` | Le decisioni strutturali, costose da cambiare. L'ADR 0005 è **storia**: superata da D-151. |
| `docs/prodotto/` | Cosa fa il prodotto e cosa non fa. |
| `docs/standard/` | Come si disegna: lo standard grafico e le regole del colpo d'occhio. Il protocollo dell'occhio terzo è storia: da D-151 quel giudizio è il **revisore**, dentro l'anello. |
| `docs/plans/` | La roadmap corrente è `2026-09-03-release-plan.md`; gli altri piani sono storia di esecuzione. |
| `docs/collaudi/` | I verbali per esteso dei collaudi indipendenti: i criteri scritti prima e l'esito di ciascuno. |
| `docs/fonti/` | Da dove vengono simboli e prescrizioni. |
| `docs/prompts/` | Le istruzioni degli agenti AI della skill. |
| `docs/archivio/` | **Storia.** Piani eseguiti, specifiche superate, revisioni passate, contesto iniziale. Non va letto per sapere come funziona la skill. |

## Ambiente

```bash
bash scripts/setup-env.sh
.venv/bin/python -m pytest -q
```

Licenza MIT.
