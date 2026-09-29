# REL-001 — l'orchestratore della skill: rapporto

**Pacchetto:** `REL-001` (`ACTIVE_WORK_PACKAGE.md`; I-167) · **Ramo:** `claude/admiring-allen-u00wec`,
ripartito da `main` · **Base:** `main` a `6412016` (PR #65, `REL-008`) · **Avviato dal PO:** il 29 settembre
2026 · **Le regole:** **D-195** (da decidere)

> **Esito — in corso: prova in camera pulita con impianto-7**
>
> Due agenti (Opus e Sonnet) stanno eseguendo la skill da capo, usando soltanto la cartella
> `/outputs/skill/disegnatore-mep/`, con il testo di impianto-7 (una centrale condominiale con due pompe
> di calore in cascata, caldaia esistente, buffer a quattro porte, ACS, ricircolo, diametri sui generatori).
> Risultati attesi per il 29 settembre 2026.

## La tavola dell'impianto-7 in camera pulita

**Da aggiungere al rapporto finito:** PDF e DXF della tavola prodotta dalla skill, appena gli agenti
terminano. Deve avere **zero tratte cedute** e **zero rilievi bloccanti**.

| elemento | dove sta | note |
|---|---|---|
| PDF della tavola | `tavole/impianto-7-t1.pdf` | da produrre |
| DXF della tavola | `tavole/impianto-7-t1.dxf` | da produrre |
| Rilievi della tavola | `tavole/impianto-7-t1-rilievi.md` | da produrre |

## 1. Che cosa è REL-001

**L'orchestratore della skill** — la skill vera e propria che il progettista lancia in Claude. Tre pezzi:

1. **`SKILL.md`** — l'ingresso. Dice al progettista come descrivi un impianto, la skill ti chiede quello che
   manca, aspetta la tua approvazione, disegna, misura, consegna il PDF e il DXF.
2. **il comando unico** — `python3 scripts/mep.py <comando>`. Una riga di comandi: `completa`, `disegna`,
   `anteprima`, `consegna` sono quelli che la skill lancia da sé; il resto (`valida`, `catalogo`, `ambiente`)
   sono per il debug.
3. **la cartella installabile** — `disegnatore-mep/`, costruita da uno script **byte per byte identica** ogni
   volta. Dentro stanno il motore (tutto quello che fa il disegno, dal grafo alla tavola), la libreria, i dati,
   i riferimenti per le tre fasi che fa l'agente (Capire, Comporre, Rivedere).

Il PO aveva stabilito il flusso della skill in cinque pacchetti (`docs/plans/2026-09-03-release-plan.md`):
il primo è `REL-001`; gli altri quattro sono il cartiglio, i simboli nuovi, il DXF, il pacchetto della release.

## 2. Che cosa c'è

**Il PDF senza browser** — `src/disegnatore_mep/graphics/pdf.py`, che traduce l'SVG della tavola in PDF a
misura reale **senza nessun programma esterno**. Usa la libreria standard, scrive Helvetica (che ogni
lettore PDF ha), incorpora i JPEG, comprime il contenuto con zlib. I caratteri che WinAnsi non ha si
sostituiscono e **si dicono**.

**La costruzione della skill** — `scripts/costruisci-skill.py`. Copia il motore, adatta i percorsi dei
riferimenti (da `examples/layout/catalog` a `dati/catalogo`, il comando di validazione), aggiunge la
libreria, i dati, la licenza, il cartiglio. Due costruzioni dai medesimi file danno **gli stessi byte**.
La skill è di sola lettura.

**Il comando di ambiente** — `python3 scripts/mep.py ambiente`. Dice la versione di Python, le librerie,
quali comandi si possono eseguire (il DXF vuole ezdxf, l'anteprima un lettore di PDF; se mancano, il
comando installa o si arrangia).

**La ricerca nel catalogo** — `python3 scripts/mep.py catalogo --cerca <parola>`. «Capire» lo usa per
risolvere quando il testo non nomina il pezzo con la sigla esatta, o quando il progettista sa che
manca.

**Quattro miglioramenti alle istruzioni** di `SKILL.md` per la sessione che cucisce i pezzi da manuale:

1. Una riga di alert: se il testo non descrive un impianto deciso (chiede di dimensionare, o nomina
   vagamente), **la skill non lo progetta**, te lo dice subito, e ti chiede l'impianto.
2. Un blocco nuovo sulla potenza dei generatori: se il testo non la dà, il regime della centrale non si
   ricava, e il corredo cambia in funzione del regime; diglielo nel messaggio delle domande.
3. La istruzioni di Capire, scritte per un agente che lavora da solo, sono spiegate per una sessione: dove
   dice «chi ti ha lanciato» o «chi lancia il lavoro», quello sei tu; la tabella di rilettura è una tua
   verifica, non si manda.
4. I passi 1–8 del flusso raccontati in terza persona — «Leggo l'impianto», «Ti faccio le domande» — per
   essere più chiari.

## 3. Che cosa si è provato

**Due costruzioni della skill producono gli stessi byte.** Fatto il 29 settembre. (`tests/skill/test_costruzione_della_skill.py`, 7 prove, tutte verdi)

**La skill in camera pulita con impianto-7.** Due agenti, con soli gli strumenti di lettura, nessuno script di
sessione, nessun file fuori dalla cartella della skill (salvo l'input del progettista e la cartella di lavoro).
La skill esegue tutti e 8 i passi, la tavola esce, il PDF si produce dalla skill. **In corso.**

## 4. Criterio 6 della guida di Anthropic — il motore e i controlli sono pezzi della skill

Il PO ha chiesto (I-166): «tutto quello che hai fatto taggare e verificare i tag deve essere parte della
skill che faremo. […] Non è che i controlli li fai tu in questa sessione e poi spariscono». Dove sta
ciascuno:

| controllo | dove sta nella skill | come si verifica |
|---|---|---|
| **Completare** — aggiunge gli accessori | `scripts/disegnatore_mep/model/rules.py` | il comando `disegna` lo lancia |
| **Eseguire** — disegna e misura | `scripts/disegnatore_mep/piano/esecutore.py` | il comando `disegna` lo lancia |
| **Preflight** — i rilievi di qualità | `scripts/disegnatore_mep/validation/preflight.py` | il comando `disegna` lo lancia e lo stampa |
| **Rivedere** — l'occhio dell'agente | `skill/rivedere/ISTRUZIONI.md` | nel flusso è il passo 7 |

Nessuno di questi è uno script di sessione: stanno tutti nel comando `mep.py` che la skill lancia.

## 5. Che cosa va ancora fatto

- [ ] Gli agenti completano il test in camera pulita
- [ ] Estraggo la tavola prodotta e la misuro
- [ ] Scrivo il rapporto definitivo con la tavola in testa
- [ ] Verifico che la suite è ancora verde
- [ ] Preparo il file della guida di Anthropic spuntato
- [ ] Costruisco il pacchetto finale per il PO
