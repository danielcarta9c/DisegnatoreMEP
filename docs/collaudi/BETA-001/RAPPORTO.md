# BETA-001 — il rapporto della beta della 1.2

Una sezione per ogni gruppo di correzioni, la più recente in alto.

## 1. Le domande dell'inizio chiedono i diametri; il grafo da leggere non si manda più

**2 ottobre 2026** · input **I-185**, **I-186** · decisione **D-199** (proposta)

Il PO, dopo la sua prova su claude.ai (I-171): «sarebbe carino che la skill all inizio fa come
domanda … se il progettista vuole anche il dimensionamento dei tubi o no. Trovo invece molto
inutile che la skill all'inizio proponga il file grafo in formato .md … Mi sembrano token
sprecati.»

### Le tavole, per prime: non cambia niente

Le 55 uscite di regressione, su `main` (`c2506b4`) e sul ramo:

```
$ docs/collaudi/REL-005/pulizia-del-solutore/confronta.sh <main> <ramo>
file: 55 prima, 54 dopo
2d1
< f02bd8c452b05029  ./D/gc-da-leggere.md
```

Le tavole sono identiche byte per byte. Il file che manca è il grafo da leggere della prova del
PO: è quello che si toglie.

### Che cosa cambia

- **La domanda sui diametri** (I-185). Il calcolo resta facoltativo: senza un sì il campo
  `diametri` non c'è. Ma se il testo non dice se il progettista li vuole, **lo si chiede**:
  - Capire §4.7 scrive la domanda in `assumptions`, con la prima interpretazione — no, la tavola
    esce senza — e, per il sì, le reti e i dati che servono, così che basti una risposta;
  - `SKILL.md`, passo 2, la mette fra le domande che fermano.

  Prima Capire diceva «se il testo non lo chiede non scrivi niente, e non lo proponi»: era la
  lettura della sessione di I-145, dove il PO aveva detto soltanto che il calcolo è facoltativo.
- **Il grafo da leggere** (I-186):
  - `completa` scrive solo il grafo completo;
  - il passo 4 porta il corredo per famiglia, i punti aperti e le assunzioni, e nessun file;
  - `scripts/grafo_leggibile.py` esce dallo ZIP: 284 file e 751 kB, contro 285 e 760.

  Il generatore resta nel repository (`examples/graph/build_plant_graph.py`): lo usano le prove
  e i collaudi.

### Le prove

```
$ python3 -m pytest -q
1973 passed, 15 skipped, 10 xfailed in 272.67s
```

`ruff check src tests` e `mypy src` verdi. Nessuno `skip` e nessuno `xfail` nuovi.

- `test_se_il_testo_non_parla_dei_diametri_capire_chiede_se_li_vuole` e
  `test_la_skill_non_porta_e_non_propone_il_grafo_da_leggere`: rosse su `main`, verdi sul ramo.
- `test_completa_scrive_il_grafo_completo_e_nessun_grafo_da_leggere` sostituisce la prova che
  voleva il file; quella che diceva quando il file non si scrive diventa
  `test_completa_scrive_il_grafo_completo_della_catena_di_rel_003`, e tiene il suo confronto.

La domanda la fa un agente, e una prova sul testo dice soltanto che le istruzioni la chiedono:
che la skill la faccia davvero si vede alla prossima prova su claude.ai.
