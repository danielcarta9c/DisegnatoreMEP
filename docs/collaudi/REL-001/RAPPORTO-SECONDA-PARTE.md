# REL-001, seconda parte — la skill che si carica: rapporto

**Pacchetto:** `REL-001`, seconda parte (`ACTIVE_WORK_PACKAGE.md`; I-171) · **Ramo:** `claude/admiring-allen-u00wec`,
ripartito da `main` · **Base:** `main` a `65b0a97` (PR #66, `REL-001`) · **Avviato dal PO:** il 2 ottobre 2026 ·
**Codice finale:** `b5723dc`; il rapporto, le tavole e lo ZIP nei commit dopo

> **Esito — in attesa del PO.** La fusione aspetta che il PO carichi la skill su claude.ai, guardi la tavola e
> dica di sì.

> **Le tavole, per prime**
>
> **L'impianto 7 disegnato dalla skill nuova** — quella da 107 file — **in camera pulita**: un agente con la
> sola cartella della skill, il testo del progettista e un Python appena installato, senza librerie; la
> sessione faceva il progettista, con le stesse risposte della prima parte.

| tavola | chi l'ha fatta | formato | PDF | DXF | rilievi | esito |
|---|---|---|---|---|---|---|
| **impianto 7 — skill nuova** | Opus | A2 | [PDF](tavole/impianto-7-skill-nuova-opus-A2.pdf) | [DXF](tavole/impianto-7-skill-nuova-opus-A2.dxf) | [rilievi](tavole/impianto-7-skill-nuova-opus-A2-rilievi.md) | 45 tratte, **0 cedute, 0 bloccanti** |
| **impianto 7 — skill nuova** | Sonnet | A2 | [PDF](tavole/impianto-7-skill-nuova-sonnet-A2.pdf) | [DXF](tavole/impianto-7-skill-nuova-sonnet-A2.dxf) | [rilievi](tavole/impianto-7-skill-nuova-sonnet-A2-rilievi.md) | 45 tratte, **0 cedute, 0 bloccanti** |
| impianto 7 | Haiku | — | **nessuna tavola** | | | 18 prove di disegno, il piano non si instrada; ed è uscito dalla camera (criterio 4) |

Le due tavole sono quelle della prima parte nella sostanza: le stesse macchine, lo stesso corredo, gli stessi
diametri, lo stesso A2. Cambia la data del cartiglio, che è quella di oggi.

## 1. Che cosa è cambiato, per chi carica la skill

Il 2 ottobre il caricamento su claude.ai si è fermato: «Zip contains too many files (maximum 200)». Lo ZIP
di `REL-001` aveva **287 file**. **Adesso ne ha 107**, pesa 752 kB, e la skill fa le stesse cose:

- **simboli, catalogo e regole** — 183 file che legge solo il comando — stanno **in un file ciascuno**,
  leggibile; il comando li riapre da sé, una volta, in una cartella temporanea;
- chi compone una tavola legge una voce di catalogo o il manifesto di un simbolo con il comando:
  `mep.py catalogo <id>`, `mep.py simbolo <id>`; le istruzioni di Capire e di Comporre nominano il comando
  dove prima nominavano il file;
- **la descrizione** della skill sta nei 200 caratteri che il centro d'aiuto di claude.ai indica, e il
  frontespizio dice la licenza e che cosa vuole l'ambiente (`compatibility`);
- **la costruzione controlla il caricamento**: oltre 200 file, oltre 30 MB, una voce di cartella, un secondo
  `SKILL.md`, un campo che il validatore non ammette, una descrizione troppo lunga — si ferma e lo dice;
- **il lanciatore** installa pydantic anche dove il Python di sistema è protetto (Ubuntu 24.04, PEP 668).

## 2. I criteri, uno per uno

### Criterio 0 — le tavole, per prime: **raggiunto**

Le due tavole in testa, **rimisurate dalla sessione** con il codice del repository: dal grafo completo e dal
piano di ciascun agente escono lo stesso PDF, lo stesso DXF, lo stesso SVG e gli stessi rilievi, byte per byte.

```
$ python docs/collaudi/REL-001/rimisura.py disegna <camera Opus>/lavoro/grafo-completo.json --piano <camera Opus>/lavoro/piano.json --out <rimisura>
Area del disegno dell'A2: 524 x 358 mm, con la tabella delle apparecchiature in alto a sinistra (137.5 x 62.5 mm); la posa ne occupa 340 x 185.
Formato A2 · tratte 45 · tratte cedute 0 · rilievi bloccanti 0 · pieghe 7 · sormonti 3 · avvisi e regole: SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER x1
pdf identico · dxf identico · svg identico · rilievi identici
$ (lo stesso per la camera Sonnet)
Area del disegno dell'A2: 524 x 358 mm, con la tabella delle apparecchiature in alto a sinistra (137.5 x 62.5 mm); la posa ne occupa 360 x 187.5.
Formato A2 · tratte 45 · tratte cedute 0 · rilievi bloccanti 0 · pieghe 7 · sormonti 3 · avvisi e regole: SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER x1
pdf identico · dxf identico · svg identico · rilievi identici
```

### Criterio 1 — lo ZIP si carica: **raggiunto, per quello che si misura da qui**

```
$ python scripts/costruisci-skill.py
Skill: …/outputs/skill/disegnatore-mep (107 file, 2108 kB)
ZIP:   …/outputs/skill/disegnatore-mep.zip (752 kB, sha256 6fe16df1330c5018)
Controlli della guida di Anthropic e di skill-creator: passati.
$ python3 skill-creator/scripts/quick_validate.py outputs/skill/disegnatore-mep
Skill is valid!
$ (lo ZIP riletto) voci: 107 · voci di cartella: 0 · fuori da disegnatore-mep/: 0 · SKILL.md: 1 · 2,06 MB non compressi, il file più grande 211 kB
```

**Il caricamento vero lo fai tu**: da qui non c'è claude.ai. Le regole che un caricamento controlla, e da dove
vengono, sono in §3.1.

### Criterio 2 — la skill funziona come prima: **raggiunto**

`test_la_skill_costruita_disegna_da_sola` costruisce la skill, la lancia fuori dal repository con il suo comando
e il suo motore, e ne prova i comandi: `ambiente`, `completa` dal grafo di prima stesura della tavola 6,
`disegna` della tavola 6 e **dell'impianto 7, il cui PDF esce identico, byte per byte, a quello consegnato
dalla prima parte** (`tavole/impianto-7-finale-opus-A2.pdf`); `catalogo <id>`, `simbolo <id>`, `pezzi`. Il grafo
e il piano dell'impianto 7 sono in [`impianto-7/`](impianto-7/).

### Criterio 3 — le istruzioni cambiano nei soli percorsi: **raggiunto**

`test_le_istruzioni_cambiano_nei_soli_percorsi` applica alle istruzioni del repository le sostituzioni della
costruzione e ritrova, riga per riga, quelle della skill. Le sostituzioni nuove sono quattro: in Capire la riga
del catalogo («`python3 scripts/mep.py catalogo` (una riga per voce), `catalogo <id>` (la voce intera)»), in
Comporre il manifesto di un simbolo e la voce di catalogo di un pezzo («`python3 scripts/mep.py simbolo <id>`»,
«`… catalogo <definition_id>`»).

### Criterio 4 — la prova in camera pulita: **raggiunto con Opus e Sonnet**

| | Opus | Sonnet | Haiku |
|---|---|---|---|
| si prepara da un Python vuoto | sì, «Pronto.» | sì, «Pronto.» | sì |
| dove si ferma a chiedere | una volta: quattro domande con la proposta — il circolatore della caldaia, i ritegni, il carico automatico, i diametri —, le conferme e i dati, e l'approvazione del grafo completo | una volta: una cosa che non coincide col testo (il carico automatico), sette conferme, i dati, e l'approvazione | una volta, le domande; poi l'approvazione a parte |
| legge i dati col comando | `catalogo <id>` undici volte, `simbolo <id>` una | `catalogo <id>` cinque volte | — |
| la tavola | A2, 0 cedute, 0 bloccanti | A2, 0 cedute, 0 bloccanti | **nessuna**: 18 prove di disegno, il piano non si instrada |
| è rimasto nella camera | sì; da sé dice di aver guardato se c'era la cartella di consegna di claude.ai, senza scriverci | sì | **no**: ha cercato il comando nel repository e ha disegnato con la skill costruita lì; nel repository non ha scritto (`git status` pulito) |

I comandi delle tre camere, in ordine con il loro esito, sono in
[`camera-seconda-parte-opus-comandi.md`](camera-seconda-parte-opus-comandi.md),
[`camera-seconda-parte-sonnet-comandi.md`](camera-seconda-parte-sonnet-comandi.md) e
[`camera-seconda-parte-haiku-comandi.md`](camera-seconda-parte-haiku-comandi.md). **Con Haiku la skill non
funziona**, come nella prima parte; e non ha seguito la riga nuova di `SKILL.md` che gli chiede di dirlo al
progettista.

**La skill provata e quella consegnata.** Le camere hanno girato su una costruzione intermedia; lo ZIP
consegnato differisce in due punti, tutti e due sulla strada di un errore: l'installazione di pydantic su un
Python di sistema protetto (`test_lanciatore.py`) e la pulizia della cartella temporanea se un fascio non si
riapre (`test_i_fasci_si_riaprono_uguali_e_non_escono_dalla_loro_cartella`).

### Criterio 5 — la suite: **raggiunto**

```
main (6412016, REL-008): 46 failed, 1989 passed, 24 skipped, 12 xfailed
ramo (d8ea1b4):          46 failed, 2039 passed, 24 skipped, 12 xfailed in 1233.27s
rosse nuove: nessuna · rosse guarite: nessuna · skip e xfail: gli stessi, nome per nome
$ python -m pytest -q tests/skill        (sulla testa, con le due prove del lanciatore)
33 passed
$ ruff check src tests examples scripts skill docs/collaudi/REL-001
All checks passed!
$ mypy && mypy scripts/costruisci-skill.py skill/scripts/mep.py
Success: no issues found in 89 source files
Success: no issues found in 2 source files
```

## 3. Le linee guida di Anthropic, voce per voce

### 3.1 Quelle obbligatorie — senza, il caricamento si ferma

| regola | fonte | nella skill | la prova |
|---|---|---|---|
| al massimo **200 file** nello ZIP | il messaggio del caricamento su claude.ai (I-171) | **107** | la costruzione si ferma oltre 200; `test_lo_zip_sta_nei_limiti_del_caricamento`, `test_troppi_file_fermano_la_costruzione` |
| **la cartella della skill** alla radice dello ZIP, **nessuna voce di cartella** | centro d'aiuto, «Creating custom Skills»; guida delle Skills per l'API | tutte le voci in `disegnatore-mep/`, nessuna di cartella | la costruzione rilegge lo ZIP e lo controlla |
| **un solo `SKILL.md`** | `skill-creator` (`quick_validate`): «the Skills API and claude.ai reject multiple on upload» | uno | `quick_validate` → «Skill is valid!» |
| frontespizio **YAML** con `name` e `description` | centro d'aiuto; specifica | sì | `quick_validate` legge il frontespizio con YAML |
| `name`: al massimo 64 caratteri, minuscole, cifre e trattini, senza «anthropic» e «claude» | guida «Skill authoring best practices»; specifica | `disegnatore-mep` | `controlla` e `quick_validate` |
| `description`: non vuota, al massimo 1024 caratteri, senza tag | guida; specifica | 194 caratteri | `controlla` e `quick_validate` |
| `description` al massimo **200 caratteri** | centro d'aiuto di claude.ai, «Creating custom Skills» (22 luglio 2026) | 194 | `controlla`; le tue skill già caricate ne hanno 690–939, quindi oggi il limite non è applicato: lo si rispetta lo stesso |
| solo i campi `name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility` | `skill-creator` (`quick_validate`) | `name`, `description`, `license`, `compatibility` | `quick_validate`. Il centro d'aiuto cita anche un campo `dependencies`, che `skill-creator` rifiuta: le librerie stanno in `compatibility` e nel corpo |
| `compatibility` al massimo 500 caratteri | `skill-creator` | 296 | `controlla` |
| **sotto i 30 MB**, e ogni file sotto i 30 MB | guida delle Skills per l'API; centro d'aiuto, «Create and edit files» | 2,1 MB in tutto, il file più grande 211 kB | `controlla` |

### 3.2 Le buone pratiche — la lista della guida

La lista «Checklist for effective Skills» è quella del rapporto della prima parte (§3, criterio 7), voce per
voce; qui cambia solo dove la skill è cambiata.

| voce | | che cosa cambia |
|---|---|---|
| La descrizione è specifica e porta le parole chiave | sì | più corta: schema funzionale, centrale termica, pompe di calore, caldaie, accumuli, ACS, PDF, DXF, tavola |
| Dice che cosa fa e quando usarla | sì | «Disegna in PDF e DXF lo schema funzionale … Da usare quando chiede lo schema o la tavola dell'impianto.» |
| I dettagli stanno in file a parte, a un livello | sì | i riferimenti sono gli stessi; i dati si leggono col comando, non si aprono |
| Gli script risolvono invece di rimandare | sì | il comando riapre da sé i dati; `catalogo <id>` e `simbolo <id>` |
| Le librerie sono dette e verificate | sì | in `compatibility` e in «Prima di cominciare»; `ambiente` le verifica e le installa, anche su un Python protetto |
| Provata con Haiku, Sonnet e Opus | sì | §2, criterio 4; `SKILL.md` dice ad Haiku di avvisare il progettista |
| Il parere del gruppo | **aperto** | il caricamento e la prova tua (§4) |

## 4. Come si carica

[`disegnatore-mep.zip`](disegnatore-mep.zip) — 752 kB, 107 file, sha256 `6fe16df1330c5018…`.

1. **Su claude.ai, «Le tue competenze» › «Carica una skill»** — la pagina del tuo schermo del 2 ottobre —:
   scegli lo ZIP così com'è e premi «Carica». Serve l'esecuzione del codice attiva.
2. **In una conversazione nuova** descrivi l'impianto e chiedi lo schema, con Opus o Sonnet. La prima volta
   la skill installa pydantic da internet, in pochi secondi.

## 5. Che cosa resta aperto

- **Il caricamento vero e la tua prova** (I-170, I-171): da qui si misura tutto quello che un caricamento
  controlla, non il caricamento.
- **Se la rete del codice è spenta** nella tua organizzazione, la skill non installa pydantic e si ferma
  dicendolo. Le alternative — portare nella skill pydantic già compilato, una copia per ogni versione di
  Python e ogni macchina — si decidono se succede.
- **Il salvataggio in OneDrive** che hai chiesto: da qui non posso scrivere lo ZIP nella tua cartella. Il
  connettore di Microsoft 365 vuole il file intero dentro il messaggio, e uno ZIP da 750 kB non ci passa.
- **Quello che le prove dicono per il prossimo giro** — è di `REL-005` o di un giro della skill, e alcune
  cose sono tue:
  - un accessorio che il testo mette in un posto e le regole in un altro (il carico automatico) non ha
    un'istruzione: Opus e Sonnet l'hanno visto da soli;
  - le sigle dei generatori seguono l'ordine di lettura, non quello del testo (GT-01 è la caldaia);
  - «esistente» toglie il diametro e basta: la tavola non distingue la caldaia e la distribuzione esistenti;
  - Capire dice di scrivere «ND» dove il cartiglio non ha il dato, e `SKILL.md` dice «DA DEFINIRE»;
  - Comporre non dice gli stacchi minimi degli appesi né che la tabella delle apparecchiature occupa l'angolo
    in alto a sinistra: tutte e due le prove hanno provato l'A3 e sono salite all'A2;
  - l'uscita di `completa` è lunga e tecnica, senza un riassunto per famiglia;
  - le reti dell'acqua fredda che le regole creano non stanno nella lista dei diametri.
