# Disegnatore MEP

Skill/tool installabile da usare nelle chat di lavoro, che trasforma un impianto
termotecnico **già deciso e dimensionato dall'ingegnere** in una tavola tecnica
professionale, pronta da stampare e da portare in cantiere.

La skill non progetta: non inventa potenze, temperature, prevalenze, tarature, volumi né
diametri. Interpreta l'impianto, propone gli accessori mancanti motivandoli, li fa
approvare, e poi disegna.

## Da dove si comincia

1. **`ACTIVE_WORK_PACKAGE.md`** — l'unico incarico operativo corrente del DEV.
2. **`HANDOFF.md`** — missione, stato sintetico e confini PO/PM/DEV.
3. **`docs/SKILL.md`** — com'è fatta la skill: i pezzi, cosa fa ciascuno e quando è
   finito. È il documento autorevole sull'architettura.
4. **`PROJECT_STATE.md`** — a che punto siamo e cosa manca. È l'unico posto in cui è
   scritto lo stato.
5. **`AGENTS.md`** — come si lavora: i tre ruoli, il metodo, come si consegna al PM.

Il resto si apre quando serve.

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
| `docs/SKILL.md` | **Com'è fatta la skill.** Una sola fonte. |
| `docs/DECISION_LOG.md` | Perché abbiamo deciso così, in ordine di tempo. |
| `docs/DEFERRED.md` | Cosa è stato rimandato, e cosa lo sbloccherebbe. |
| `docs/adr/` | Le decisioni strutturali, costose da cambiare. |
| `docs/prodotto/` | Cosa fa il prodotto e cosa non fa. |
| `docs/standard/` | Come si disegna: lo standard grafico, le regole del colpo d'occhio, il protocollo dell'occhio terzo. |
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
