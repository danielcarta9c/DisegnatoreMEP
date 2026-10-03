# BETA-001 — il rapporto della beta della 1.2

Una sezione per ogni gruppo di correzioni, la più recente in alto.

## 2. La skill si carica: 104 file, e il limite è nel progetto

**3 ottobre 2026** · input **I-188**, **I-189** · decisione **D-200**, approvata (I-190) · release **1.2.2**

Il PO, caricando la 1.2.1 su claude.ai: «di nuovo lo steso errore... Zip contains too many files (maximum 200).
problema già affrontato nella vecchia sessione … questa cosa deve essere nel progetto».

### Le tavole, per prime: non cambia niente

```
$ docs/collaudi/REL-005/pulizia-del-solutore/confronta.sh <main 2bbab6b> <ramo>
file: 54 prima, 54 dopo
IDENTICI
```

Compresa la tavola D della prova del PO, che esce dalla skill costruita: la skill legge adesso i dati dai file
unici, e disegna gli stessi byte.

### Perché è successo di nuovo

La correzione c'era: l'aveva fatta il 2 ottobre mattina un'altra sessione, sul ramo
`claude/admiring-allen-u00wec` — la skill in 107 file, i controlli del caricamento nella costruzione, la prova in
camera pulita con Opus e Sonnet. **Quel ramo non è mai stato fuso.** Questa sessione è ripartita da `main` (PR
#66) senza saperlo, e la 1.2.0 e la 1.2.1 sono uscite con 287 e 284 file. La copia della skill sincronizzata
dall'account del PO è quella del ramo, a 107 file: è quella che si era caricata.

### Che cosa cambia

- **Il ramo è fuso**, con i suoi sette commit: la storia c'è tutta. Due conflitti di sostanza, risolti tenendo il
  lavoro dei due rami: il comando della skill senza il grafo da leggere (D-199), e il numero dell'input, I-171 sul
  ramo e già usato su `main`, che diventa **I-188**.
- **Lo ZIP ha 104 file** e 683 kB: simboli, catalogo e regole stanno in un file ciascuno, `dati/<nome>.json`, e
  il comando li riapre da sé; una voce si legge con `catalogo <id>`, un manifesto con `simbolo <id>`.
- **Il limite è nel progetto, in due posti con la stessa funzione** (`controlla_lo_zip`):
  - la costruzione si ferma se lo ZIP supera i 200 file, se esce dalla sua cartella, se passa i 30 MB, o se la
    skill dentro non rispetta le linee guida;
  - `tests/test_le_release.py` passa lo stesso controllo **su ogni ZIP pubblicato**: rossa sulla 1.2.1, verde sulla
    1.2.2. La 1.2.0 e la 1.2.1 restano nell'archivio, segnate come non caricabili, in un elenco chiuso.
- **La regola è scritta** in `CLAUDE.md`, che ogni sessione legge per primo, e i limiti con le fonti in
  `releases/README.md`. In `CLAUDE.md` c'è anche la causa vera: il lavoro di una sessione esiste quando è su
  `main`, e una sessione non si chiude con lavoro su un ramo senza PR.

### Le prove

```
$ python3 -m pytest -q
1981 passed, 15 skipped, 10 xfailed in 249.85s
$ ruff check src tests scripts skill/scripts
All checks passed!
$ python3 -m mypy src; python3 -m mypy scripts/costruisci-skill.py skill/scripts/mep.py
Success: no issues found in 87 source files
Success: no issues found in 2 source files
$ python3 scripts/costruisci-skill.py
ZIP:   outputs/skill/disegnatore-mep.zip (683 kB, sha256 fa922e80d8109a85)
Controlli della guida di Anthropic, di skill-creator e del caricamento su claude.ai (al massimo 200 file): passati.
```

⚠ **Un mio errore, preso in tempo**: uno `git stash` di controllo, a fusione in corso, ha cancellato lo stato della
fusione. I file erano tutti al loro posto; il commit di fusione l'ho ricostruito con i suoi due genitori.

**Che si carichi davvero lo dice soltanto il caricamento su claude.ai**: i controlli sono quelli del messaggio che
il caricamento ha dato, e delle fonti di Anthropic, ma da qui non posso caricare.

## 1. Le domande dell'inizio chiedono i diametri; il grafo da leggere non si manda più

**2 ottobre 2026** · input **I-185**, **I-186** · decisione **D-199**, approvata (I-187) · consegnata nella **1.2.1**

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
