# REL-001 — la skill vera e propria: rapporto

**Pacchetto:** `REL-001` (`ACTIVE_WORK_PACKAGE.md`; I-166, I-167) · **Ramo:** `claude/admiring-allen-u00wec`,
ripartito da `main` · **Base:** `main` a `6412016` (PR #65, `REL-008`) · **Avviato dal PO:** il 29 settembre
2026 (I-168) · **Codice finale:** `a139a43`; il rapporto e lo ZIP stanno nei commit dopo

> **Esito — in attesa del PO.** La fusione aspetta che il PO guardi la tavola e dica di sì (D-146, D-147).

> **Le tavole, per prime**
>
> **L'impianto 7**, che non è fra i sei di prova — due pompe di calore in cascata e una caldaia
> esistente in parallelo, volume tecnico, bollitore con serpentino e ricircolo, i diametri della parte
> nuova ([il testo](impianto-7.txt)) —, **disegnato dalla skill in camera pulita**: un agente con la sola
> cartella della skill, il testo del progettista e un Python appena installato, senza librerie; la
> sessione faceva il progettista. **Il PDF l'ha scritto la skill**, senza browser.

| tavola | chi l'ha fatta | formato | PDF | DXF | rilievi | esito |
|---|---|---|---|---|---|---|
| **impianto 7 — giro finale** | Opus, con la skill finale | A2 | [PDF](tavole/impianto-7-finale-opus-A2.pdf) | [DXF](tavole/impianto-7-finale-opus-A2.dxf) | [rilievi](tavole/impianto-7-finale-opus-A2-rilievi.md) | 45 tratte, **0 cedute, 0 bloccanti** |
| impianto 7 — primo giro | Sonnet, con la skill del primo giro | A3 | [PDF](tavole/impianto-7-primo-giro-sonnet-A3.pdf) | — | [rilievi](tavole/impianto-7-primo-giro-sonnet-A3-rilievi.md) | 45 tratte, 0 cedute, 0 bloccanti |
| impianto 7 — primo giro | Opus, con la skill del primo giro | A2 | [PDF](tavole/impianto-7-primo-giro-opus-A2.pdf) | — | [rilievi](tavole/impianto-7-primo-giro-opus-A2-rilievi.md) | 45 tratte, 0 cedute, 0 bloccanti |
| impianto 7 | Haiku, giro finale | — | **nessuna tavola** | | | 32 prove di disegno, il piano non si instrada mai (§5) |

E **le sette tavole approvate di `REL-008` in PDF senza browser**, in [`pdf-senza-browser/`](pdf-senza-browser/):
sono il criterio 1.

## 1. Che cosa guardare sulla tavola

1. **È il flusso intero, senza la sessione in mezzo.** Dal testo, la skill ha fatto le domande in un
   messaggio solo, ha aggiunto il corredo, ha chiesto l'approvazione del grafo completo, poi ha composto,
   disegnato, controllato e consegnato. La sessione ha scritto soltanto le due risposte del progettista.
2. **Il disegno**: i tre generatori impilati a sinistra con i loro collettori corti, mandata e ritorno
   comuni dritti fino al volume tecnico, la deviatrice sulla mandata che scende al serpentino, il bollitore
   sotto il volume, il secondario a destra, il sanitario sotto. I diametri solo sul circuito dei
   generatori, come chiesto: Øi 40 sui rami delle pompe di calore, Øi 65 sul ramo della caldaia e sui
   collettori, Øi 80 sulle linee comuni e sul ramo del serpentino.
3. **L'agente l'ha guardata e l'ha corretta** prima di consegnarla: al primo disegno la seconda valvola
   del circolatore del secondario finiva attaccata al radiatore, a 40 mm dalla pompa, e sembrava la
   valvola del radiatore. Nessun rilievo lo segnalava; l'ha visto, ha scritto il vincolo e ha ricomposto.
4. **Il foglio è un A2 con molto bianco intorno.** È la regola di Comporre: con quella posa l'A3 non
   bastava — il disegno passava sulla tabella delle apparecchiature, un rilievo bloccante —, e le
   istruzioni dicono di prendere il formato successivo senza comprimere il disegno; **il vuoto non è un
   difetto** (D-170). Te lo segnalo perché Sonnet, al primo giro, aveva composto lo stesso impianto più
   stretto e l'aveva fatto stare in un A3: la seconda riga della tabella. Da adesso il comando dice
   quanto è grande la tabella (137,5 × 62,5 mm), e chi compone può giudicare se la posa le passa sotto.
5. **Quello che resta aperto, detto dalla skill al progettista**: il carico automatico sta sul ritorno
   comune e non sul volume, perché il volume del catalogo non ha l'attacco; niente valvole di ritegno né
   sui generatori in parallelo né sul ricircolo, perché le regole non le mettono; le celle di marche,
   modelli, portate e prevalenze vuote, come chiesto; niente diametri sul secondario esistente e sul
   sanitario. E tre domande: il ramo del serpentino a Øi 80, le parti esistenti che la tavola non
   distingue, le sigle solo sui pezzi della tabella. Le raccolgo in §6.1: sono domande per te.

**Confrontata con `docs/standard/QUALITA_GRAFICA.md`**: composizione per fasce da sinistra a destra (A4),
paralleli impilati (A6), tre incroci con lo scavalco (B3, B13), i pallini dei collegamenti (B15), le
sigle accanto ai pezzi (D1), un'intercettazione su ogni attacco delle macchine (E1), cartiglio compilato
e nessun «DA DEFINIRE» (F2, F5). Sul foglio pieno (A1) vale D-170, e l'ho detto al punto 4.

## 2. Che cosa c'è

- **L'ingresso**, [`skill/SKILL.md`](../../../skill/SKILL.md) (241 righe di corpo): che cosa la skill non fa
  mai, l'ambiente, e il flusso in otto passi — Capire, le domande in un messaggio solo, Completare,
  l'approvazione del grafo completo (l'unico cancello), Comporre, Eseguire, Rivedere, Consegnare —, con
  la lista dei passi da copiare nella risposta, in parole del progettista.
- **Il comando unico**, `python3 scripts/mep.py <comando>` ([`skill/scripts/mep.py`](../../../skill/scripts/mep.py)
  e [`src/disegnatore_mep/skill.py`](../../../src/disegnatore_mep/skill.py)): `ambiente`, `catalogo`
  (anche `--cerca`), `valida`, `completa`, `pezzi`, `disegna`, `anteprima` (anche `--zona`), `consegna`.
  Esce con 0; con 2 quando qualcosa ferma la consegna; con 1 quando non ha potuto fare.
- **Il PDF senza browser**, [`src/disegnatore_mep/graphics/pdf.py`](../../../src/disegnatore_mep/graphics/pdf.py):
  dall'SVG della tavola al PDF con la sola libreria standard, la pagina grande quanto il foglio. Anche
  `disegnatore-mep draw` e `piano` lo scrivono, con `--pdf`.
- **La cartella della skill**, costruita da [`scripts/costruisci-skill.py`](../../../scripts/costruisci-skill.py)
  in `outputs/skill/`, con lo ZIP: `SKILL.md`; le istruzioni di Capire, Comporre e Rivedere e le regole
  del piano in `riferimenti/`, cambiate nei soli percorsi; il comando e il motore in `scripts/`;
  simboli, catalogo, regole, naming, cartiglio e schema in `dati/`.
- **Le valutazioni**, [`skill/evals/evals.json`](../../../skill/evals/evals.json): quattro, nella forma di
  `skill-creator`.
- **Le prove**: `tests/graphics/test_pdf.py` (25), `tests/skill/test_comando.py` (14),
  `tests/skill/test_costruzione_della_skill.py` (7).
- **Gli strumenti della sessione**, qui: [`confronto_pdf.py`](confronto_pdf.py) e
  [`tavole_approvate.py`](tavole_approvate.py) per il criterio 1; [`rimisura.py`](rimisura.py) e
  [`comandi_della_camera.py`](comandi_della_camera.py) per i criteri 0, 4 e 6; la
  [skill di prova dell'ambiente](prova-ambiente/) per il punto 1.
- **Lo ZIP per il PO**: [`disegnatore-mep.zip`](disegnatore-mep.zip) (§7).

**La skill consegnata e quella provata.** Le prove finali hanno girato sullo ZIP del commit `704bb77`.
Dopo, tre ritocchi, nessuno nel disegno: in `SKILL.md` il paragrafo che nomina le librerie (la lista di
controllo lo chiede, criterio 7); in `mep.py` un commento per `mypy`; in `disegna` la misura della
tabella nella riga dell'area (§1, punto 4). La differenza fra le due cartelle è tutta qui:

```
$ diff -r <camera>/skill/disegnatore-mep outputs/skill/disegnatore-mep
SKILL.md: 40,41c40,44 — le librerie (Python 3.11, pydantic 2, ezdxf, pypdfium2) e che cosa succede se mancano
scripts/mep.py: 100c100,102 — un commento e «# type: ignore[import-not-found]»
scripts/disegnatore_mep/skill.py — la riga dell'area con la misura della tabella
```

## 3. I criteri, uno per uno

### Criterio 0 — le tavole, per prime: **raggiunto**

In testa, la tavola del giro finale, uscita dalla skill in camera pulita, nel PDF che la skill ha
scritto. **Rimisurata dalla sessione** con il codice del repository (D-152, regola 3): dal grafo
completo e dal piano dell'agente escono lo stesso PDF, lo stesso DXF, lo stesso SVG e gli stessi
rilievi, byte per byte.

```
$ git log --oneline -1
a139a43 REL-001: disegna dice quanto posto prende la tabella delle apparecchiature
$ python docs/collaudi/REL-001/rimisura.py disegna <camera>/lavoro/grafo-completo.json \
      --piano <camera>/lavoro/piano.json --out <rimisura>
Area del disegno dell'A2: 524 x 358 mm, con la tabella delle apparecchiature in alto a sinistra (137.5 x 62.5 mm); la posa ne occupa 335 x 197.5.
Formato A2 · tratte 45 · tratte cedute 0 · rilievi bloccanti 0 · pieghe 7 · sormonti 3 · avvisi e regole: SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER x1
$ cmp <camera>/lavoro/consegna/<tavola>.{pdf,dxf,svg} <rimisura>/<tavola>.{pdf,dxf,svg}; cmp … -rilievi.md
pdf identico · dxf identico · svg identico · rilievi identici
```

Le due tavole del primo giro, rimisurate allo stesso modo:

```
camera Opus:   Formato A2 · tratte 45 · tratte cedute 0 · rilievi bloccanti 0 · pieghe 7 · sormonti 3 · … — PDF identico
camera Sonnet: Formato A3 · tratte 45 · tratte cedute 0 · rilievi bloccanti 0 · pieghe 7 · sormonti 3 · … — PDF identico
```

### Criterio 1 — il PDF senza browser: **raggiunto**

- **La pagina è il foglio**: 420,000 × 297,000 mm sull'A3, 594,000 × 420,000 sull'A2. Quella del browser
  è 420,201 × 297,011 (+0,048 %) e 594,106 × 420,201.
- **Sulle sette tavole approvate**, rasterizzate a 200 dpi tutt'e due: **nel disegno 0 pixel diversi**,
  col browser com'è e col browser riportato a misura; le differenze stanno tutte **nei caratteri**
  (Helvetica qui, Liberation Sans nel browser, con le stesse larghezze). Nessun carattere sostituito.
  Sono le cinque del pacchetto più la 6 e il retrofit, **nelle versioni di `REL-008`**, le ultime che hai
  approvato (I-164): quelle di `DRAW-017` e `DRAW-018` sono le stesse tavole con le scritte a 5 punti.
- **Il controllo negativo**: la tavola 1 con una valvola spostata di 0,3 mm. Col browser com'è il
  confronto trova **362 pixel** diversi nel disegno, dove sulle tavole vere ne trova 0. Col browser
  riportato a misura ne trova 1, nel punto della valvola: a quella distanza il secondo confronto è quasi
  cieco, e decide il primo.

```
$ python docs/collaudi/REL-001/tavole_approvate.py <svg>
$ python docs/collaudi/REL-001/confronto_pdf.py <svg> <uscita>
tavola-1   pagina: foglio 420x297 mm · nuova 420.000x297.000 · browser 420.201x297.011 (+0.048 %, +0.004 %)
           pixel diversi su 7737412: col browser com'e' — caratteri 9592, disegno 0; col browser a misura — caratteri 2295, disegno 0
tavola-5   pagina: foglio 594x420 mm · nuova 594.000x420.000 · browser 594.106x420.201 (+0.018 %, +0.048 %)
           pixel diversi su 15474824: col browser com'e' — caratteri 11767, disegno 0; col browser a misura — caratteri 18126, disegno 0
…          (le altre cinque: disegno 0 e 0)
$ python docs/collaudi/REL-001/confronto_pdf.py --controllo <svg>/tavola-1.svg \
      docs/collaudi/REL-001/pdf-senza-browser/controllo-tavola-1-valvola-spostata.svg <uscita>
tavola-1   pixel diversi su 7737412: col browser com'e' — caratteri 9592, disegno 362; col browser a misura — caratteri 2295, disegno 1
           dove resta una differenza nel disegno (mm, arrotondati): [(228, 88)]
```

L'output intero è in [`confronto-pdf.txt`](confronto-pdf.txt); i sette PDF in
[`pdf-senza-browser/`](pdf-senza-browser/).

### Criterio 2 — la cartella si costruisce con un comando e si rigenera identica: **raggiunto**

```
$ python scripts/costruisci-skill.py
Skill: …/outputs/skill/disegnatore-mep (287 file, 2094 kB)
ZIP:   …/outputs/skill/disegnatore-mep.zip (821 kB, sha256 c203d388cdba49fc)
Controlli della guida di Anthropic e di skill-creator: passati.
$ python -m pytest -q tests/skill/test_costruzione_della_skill.py
7 passed
```

Le sette prove: **due costruzioni danno gli stessi byte**, cartella e ZIP; lo ZIP ha la skill alla radice
e niente file compilati; la skill passa i controlli della guida e quelli del validatore di
`skill-creator`; un frontespizio che YAML non legge ferma la costruzione; le istruzioni di Capire,
Comporre e Rivedere arrivano **cambiate nei soli percorsi**, e una sostituzione che non trova il suo
posto ferma la costruzione; **la skill costruita disegna da sola**, fuori dal repository, dal grafo di
prima stesura della tavola 6 al PDF con i rilievi.

### Criterio 3 — l'ingresso dice il flusso, le domande e l'approvazione; nessun pezzo lo cuce la sessione: **raggiunto**

`SKILL.md` dice in testa che cosa la skill non fa mai: non progetta, non inventa dati, non cambia lo
schema, non sostituisce un pezzo che il catalogo non ha, non consegna una tavola con rilievi bloccanti o
tratte cedute. Poi il flusso in otto passi. Le domande sono il passo 2, **in un messaggio solo e
ciascuna con la sua proposta**; l'approvazione del grafo completo è il passo 4, **l'unico cancello**.

Nella prova la sessione ha scritto **soltanto i due messaggi del progettista** (§4). Ogni comando l'ha
lanciato l'agente (criterio 6), e l'agente ha aperto soltanto file della sua camera.

### Criterio 4 — la prova in camera pulita: **raggiunto**

Dal testo al PDF, con Opus: 45 tratte, **0 cedute, 0 bloccanti**. Dove la skill si è fermata a chiedere, e che cosa ha chiesto, è in §4; le prove con gli
altri modelli, e le valutazioni, in §5.

### Criterio 5 — la suite: **raggiunto**

```
⟦SUITE⟧
```

```
$ ruff check src tests examples scripts skill docs/collaudi/REL-001
All checks passed!
$ mypy
Success: no issues found in 89 source files
$ mypy scripts/costruisci-skill.py skill/scripts/mep.py
Success: no issues found in 2 source files
```

### Criterio 6 — il motore e i controlli sono della skill: **raggiunto**

L'agente ha lanciato da sé ogni passo deterministico — Completare (`completa`), Eseguire e il preflight
(`disegna`), l'anteprima e la consegna — con il comando e il motore della cartella della skill:
`ambiente` lo dice («Motore: <cartella della skill>/scripts/disegnatore_mep», provato in
`test_la_skill_costruita_disegna_da_sola`). Una riga per ogni chiamata dell'agente che nomina
`mep.py`, con il codice d'uscita e la riga che dice l'esito:

```
$ python docs/collaudi/REL-001/comandi_della_camera.py <trascrizione dell'agente> <camera>
1. `ambiente` — uscita 0 — Pronto.
2. `catalogo` — uscita 0 — …
4. `valida` — uscita 0 — - a-radiatori: La distribuzione esistente a radiatori … e' rappresentata da un radiatore solo.
5. `completa` — uscita 0 — …
7. `valida` — uscita 0 — Nessuna assunzione da confermare.
8. `completa` — uscita 0 — Grafo da leggere, per l'approvazione del progettista: <camera>/lavoro/grafo-completo-da-leggere.md
10. `pezzi` — uscita 0 — valve-isolation-volano-secondary-out — Valvola di intercettazione · simbolo valve-isolation 5 x 5 · …
12. `disegna` — uscita 2 — Formato A3 · tratte 45 · tratte cedute 0 · rilievi bloccanti 1 · pieghe 7 · sormonti 3 · … DRAWING_OVER_THE_EQUIPMENT_TABLE …
13. `disegna` — uscita 0 — Formato A2 · tratte 45 · tratte cedute 0 · rilievi bloccanti 0 · pieghe 7 · sormonti 3 · …
15. `anteprima` — uscita 0 — Anteprima: <camera>/lavoro/z2-primario.png (con pypdfium2, 300 dpi)
17. `disegna` — uscita 0 — Formato A2 · … · sormonti 4 · …      (la prova dell'altro ordine dei collettori, B3)
18. `disegna` — uscita 0 — Formato A2 · tratte 45 · tratte cedute 0 · rilievi bloccanti 0 · pieghe 7 · sormonti 3 · …
20. `anteprima` — uscita 0 — Anteprima: <camera>/lavoro/z3-tabella.png (con pypdfium2, 200 dpi)
21. `consegna` — uscita 0 — …
## Fuori dalla camera
- niente
```

L'elenco intero, 22 righe, è in [`camera-finale-opus-comandi.md`](camera-finale-opus-comandi.md) (qui ne
tengo 13, e accorcio le righe lunghe); quello di Haiku in [`camera-finale-haiku-comandi.md`](camera-finale-haiku-comandi.md).
Una riga è una chiamata dell'agente: dove ne ha messi due in una, la riga dice l'esito del primo che
riconosce. «?» è un codice che la trascrizione non mostra, perché l'agente aveva messo il comando dietro
una pipe. Con il PDF la
skill consegna **i rilievi della tavola**, scritti da `disegna`: [li trovi qui](tavole/impianto-7-finale-opus-A2-rilievi.md),
e dicono 0 bloccanti, 0 da approvare, 0 avvisi, una regola del piano (il ritorno del secondario fa un
gradino accanto al radiatore) e il cartiglio compilato per intero.

**Nessun controllo è rimasto nella sessione**: il preflight gira dentro `disegna`, nel motore della
skill. La sessione ha usato due strumenti suoi, e nessuno dei due entra nella tavola: `rimisura.py`,
che riesegue il comando con il codice del repository, e `comandi_della_camera.py`, che legge la
trascrizione dell'agente.

### Criterio 7 — la guida di Anthropic: **raggiunto, con due voci aperte**

La lista «Checklist for effective Skills» della guida
([Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices),
letta il 29 settembre 2026), voce per voce.

| voce | | la prova |
|---|---|---|
| La descrizione è specifica e porta le parole chiave | sì | schema funzionale, centrale termica, pompe di calore, caldaie, volani e accumuli, bollitori ACS, solare, PDF, DXF, cartiglio Nove C. **Non misurato:** se la skill scatta da sola dalla descrizione; nelle camere l'agente sapeva della skill. Lo dirà la tua prova |
| Dice che cosa fa e quando usarla | sì | «Da usare quando il progettista descrive un impianto e chiede lo schema, …, anche senza nominare la skill»; 920 caratteri su 1024, in terza persona |
| Il corpo di `SKILL.md` sta sotto le 500 righe | sì | 241 righe; la costruzione lo controlla |
| I dettagli stanno in file a parte | sì | `riferimenti/`: capire (715 righe), comporre (541), rivedere (139), regole del piano (697) |
| Niente informazioni che scadono | sì | `SKILL.md` non ha date. Nei riferimenti le date dicono **da dove viene** una regola («PO, 20 settembre 2026»), non fino a quando vale |
| Terminologia coerente | sì | «progettista» 18 volte, mai «utente» o «cliente»; «grafo di prima stesura», «grafo completo», «piano», «tavola», «rilievi» sempre per la stessa cosa, e sono le parole dei riferimenti |
| Esempi concreti | sì | i comandi per intero, con i file; che cosa porta il messaggio delle domande; gli esempi di grafo e di piano stanno nei riferimenti |
| I rimandi stanno a un livello | sì | `SKILL.md` rimanda a tutti e quattro i riferimenti; l'unico rimando fra riferimenti (rivedere → regole del piano) va a un file che `SKILL.md` richiama già. I riferimenti oltre le 100 righe hanno l'indice in testa |
| Si carica quello che serve, quando serve | sì | ogni riferimento si legge al suo passo («Leggi per intero riferimenti/comporre.md» al passo 5); un manifesto di simbolo si apre solo per il pezzo che serve |
| I flussi hanno passi chiari | sì | otto passi numerati, e la lista che l'agente copia e spunta: Opus e Sonnet la riportano in ogni messaggio, **Haiku mai** |
| Gli script risolvono invece di rimandare | sì | `completa` raggruppa il corredo e scrive il grafo da leggere; `disegna` dice l'area del formato, la tabella e la probabile causa di una tratta che non passa; `catalogo --cerca`; `consegna` |
| Errori espliciti e utili | sì | uscita 0, 2, 1; il messaggio dice il file e il perché, per esempio «il piano posa organi in linea, che il motore mette da solo sulla loro tratta: … toglili dal piano». **Ma** il dettaglio che viene dal motore è in inglese (§6.2) |
| Niente costanti senza ragione | sì | ogni costante del comando ha la sua ragione scritta accanto (`PYDANTIC`, `FACOLTATIVE`, `ATTESA_PIP_S`) |
| Le librerie sono dette e verificate | **in parte** | dette in `SKILL.md` («Prima di cominciare») e verificate da `ambiente`; in camera, da un Python senza librerie, il comando ha installato da sé pydantic 2.13.4, ezdxf 1.4.4 e pypdfium2 5.13.0. **Non verificate su claude.ai**: dipende dalla rete del tuo ambiente (§6.3) |
| Gli script sono documentati | sì | `mep.py <comando> --help` per ciascun comando; l'intestazione di `mep.py` |
| Niente percorsi alla Windows | sì | nessuna barra rovescia in `SKILL.md` e nei riferimenti |
| Verifiche sulle operazioni critiche | sì | `valida` prima di completare; il preflight dentro `disegna`; con un rilievo bloccante o una tratta ceduta il comando esce con 2 e la tavola non si consegna |
| Anelli di verifica | sì | disegna → anteprima → vincoli → piano → disegna, con il criterio d'arresto (passo 7). Nel giro finale: A3 bloccata → A2; anteprima a zone; un vincolo sul secondario; la prova dell'altro ordine dei collettori (3 sormonti contro 4); tavola rifatta |
| Almeno tre valutazioni | sì | quattro, in [`skill/evals/evals.json`](../../../skill/evals/evals.json) |
| Provata con Haiku, Sonnet e Opus | sì | §5: Opus e Sonnet arrivano alla tavola; **Haiku no** |
| Provata su casi veri | sì | l'impianto 7, scritto come li scrive un progettista; un testo che non dice abbastanza; una richiesta di dimensionare; un pezzo che il catalogo non ha |
| Il parere del gruppo | **aperto** | è la tua prova su un impianto tuo (§7) |

## 4. Dove la skill si è fermata a chiedere, e che cosa ha chiesto

Il giro finale, con Opus, si è fermato **due volte**, ai due punti che `SKILL.md` prescrive.

**Al passo 2, dopo Capire** — un messaggio solo: che cosa ha capito (tre generatori in parallelo, 190 kW
in tutto, quindi sopra i 35 kW; la deviatrice sulla mandata comune; il secondario con un radiatore
rappresentativo; il ricircolo; la regolazione — cascata, integrazione, priorità — che non si disegna);
**due domande che cambiano il disegno**, ciascuna con la proposta: il circolatore della caldaia (il
catalogo non ce l'ha a bordo) e l'ordine dei generatori sul collettore; **quattro assunzioni** da
confermare insieme; **i dati che la tavola scrive e il testo non dà**: il cartiglio, marche e modelli,
le portate per i diametri del secondario e del sanitario. Il progettista (la sessione) ha risposto:

> La caldaia ha il circolatore a bordo: nessun circolatore dedicato sul suo ramo, come proponi. Ordine
> sul collettore: va bene come proponi, quello del testo. Le assunzioni vanno bene, tranne una
> precisazione sulla quarta: il secondario dei radiatori è esistente, lì niente diametri. […] Dati per
> la tavola: committente «Condominio di prova», commessa «PROVA-REL-001», […] Marche, modelli, portate e
> prevalenze dei circolatori non sono ancora scelti: lascia le celle vuote. Vai avanti.

**Al passo 4, l'approvazione del grafo completo**: che cosa ha riportato; che cosa hanno aggiunto le
regole — 45 accessori, da 17 a 75 pezzi, detti circuito per circuito —; le sigle; e **due cose da
vedere, con la proposta**: il carico automatico, che il testo vuole sul volume e le regole mettono sul
ritorno comune; i ritegni, che le regole non mettono. Il progettista:

> Le sigle vanno bene. Carico automatico: va bene sul ritorno comune, lascialo lì e segnalo fra le cose
> aperte. Ritegni: procedi senza e scrivili fra le cose aperte. I litri dei vasi non li ho: celle vuote.
> Il grafo va bene: approvato, componi e disegna la tavola.

Poi non si è più fermata fino alla consegna. Al primo giro Opus aveva messo tutto nel messaggio
dell'approvazione (nessuna domanda che cambiasse il disegno), Sonnet si era fermato al passo 2 con due
domande — il circolatore della caldaia, i diametri — e al passo 4 con quattro cose da vedere.

## 5. Le prove, modello per modello

La skill ha fatto **tre giri**: il primo (`f6ebf64`) sulle quattro valutazioni e sull'impianto 7; il
secondo (`81f9089`) dalle valutazioni; il terzo (`704bb77`) dalle prove intere dell'impianto 7. Il giro
finale ha girato sul terzo.

| | Opus | Sonnet | Haiku |
|---|---|---|---|
| **1 — l'impianto 7, dal testo al PDF** | primo giro: A2, 0 cedute, 0 bloccanti · **giro finale: A2, 0 cedute, 0 bloccanti** | primo giro: **A3**, 0 cedute, 0 bloccanti | primo giro: **prova nulla**, è uscito dalla camera · giro finale: **nessuna tavola** |
| **2 — un testo che non dice abbastanza** | passa: si ferma dopo Capire con tre domande che cambiano il disegno, ciascuna con la proposta; chiede le potenze; il grafo non porta potenze né volumi | — | passa: le stesse domande, e le potenze; il grafo non porta potenze né volumi |
| **3 — una richiesta di dimensionare** | passa: «Non posso dimensionarti la pompa di calore e il volume tecnico», nessuna taglia | — | passa: dice che la skill non dimensiona e chiede come procedere |
| **4 — un pezzo che il catalogo non ha** (un cogeneratore) | passa: non lo sostituisce, lo dice, propone di procedere senza o di fermarsi | — | primo giro: **non passa** (proponeva un'altra macchina al suo posto, o di aggiungerlo al catalogo) · giro finale: **passa** |

**Haiku non compone il piano.** Nel giro finale ha fatto Capire, le domande e il completamento, poi ha
provato 32 volte a disegnare, e il piano non si è mai instradato: pezzi troppo vicini, tratte senza
strada. Dopo una ventina di minuti si è fermato, con un resoconto in inglese per chi sviluppa invece del messaggio
al progettista. Non riporta mai la lista dei passi. **La skill va usata con Opus o Sonnet.**

**Haiku, al primo giro, è uscito dalla camera**: ha scritto e committato nel repository un suo rapporto
e una sua lista (`d0f069a`). L'ho spinto senza guardarlo, ed è un errore mio; l'ho annullato con
`f1e18d2`. La prova non vale. Da lì il mandato delle camere dice che le regole del repository non
valgono per l'agente, e ogni camera si controlla con `comandi_della_camera.py`: nel giro finale né
Opus né Haiku hanno aperto niente fuori dalla camera (Haiku ha tentato una volta un percorso sbagliato
della sua stessa camera, che non esiste).

Che cosa hanno cambiato i due giri: dopo le valutazioni, il divieto di sostituire un pezzo che il
catalogo non ha e `catalogo --cerca`; le potenze e il pezzo principale che mancano come domande del
passo 2; la risposta a chi chiede di dimensionare; `ambiente` che installa anche il lettore
dell'anteprima. Dopo l'impianto 7, `disegna` che dice l'area del formato e la probabile causa di una
tratta che non passa (Sonnet aveva fatto sette prove su una tratta innocente), pieghe e sormonti nel
riepilogo, `pezzi`, `anteprima --zona`.

## 6. Che cosa ho trovato, e va detto

### 6.1 Domande per te — contenuto e convenzioni, non miei

1. **Ritegni.** Né sui rami dei tre generatori in parallelo né sul ricircolo ACS: le regole non li
   mettono, e la skill non ha modo di aggiungerli. L'hanno notato tutti e tre i modelli.
2. **Carico automatico.** Il testo lo vuole sul volume tecnico; il volume del catalogo non ha l'attacco,
   e le regole mettono il gruppo di riempimento sul ritorno comune, subito a valle del volume.
3. **Scarico del bollitore.** Sta sull'acqua fredda, a monte del gruppo di sicurezza, che porta il
   ritegno: da lì si svuota la rete, non il bollitore (l'hanno notato Sonnet e Opus al primo giro).
4. **Sigle dei generatori.** GT-01 è la caldaia, in fondo alla pila; GT-03 la pompa di calore più vicina
   al volume: l'ordine inverso del testo. In tabella «nr 1» è GT-02 e «nr 2» GT-03, quella in alto.
5. **Nuovo ed esistente.** La caldaia esistente e la distribuzione esistente sono disegnate come il
   nuovo; «esistente» su una rete toglie soltanto il diametro.
6. **Il ramo del serpentino a Øi 80**: porta la portata di tutti e tre i generatori, perché in priorità
   ACS la deviatrice gli manda tutto. Va bene così?
7. **Sulla tavola**: gli attacchi di servizio liberi (sfiato e sonda del volume, sonda del bollitore)
   sono tronchetti senza voce in legenda; lo scarico del volume è rosso, con la freccia di flusso, come
   una mandata; la sigla sul disegno c'è solo per i pezzi della tabella, e la deviatrice (VD-01), che il
   grafo da leggere nomina, sul disegno non ce l'ha.

### 6.2 Per il prossimo giro della skill

1. **Haiku non compone il piano** (§5). Si scrive in testa a `SKILL.md` che la skill vuole Opus o
   Sonnet, o si dà a chi compone un aiuto che oggi non c'è.
2. **Il dettaglio dei messaggi del motore è in inglese** («run p10-a-2 on network primario cannot be
   routed…»): il comando lo stampa com'è.
3. **Le integrazioni escono «approvate» nel grafo completo** prima che il progettista lo approvi: la sua
   approvazione non lascia traccia nel file.
4. **Un'integrazione che il progettista rifiuta, o vuole spostare, non si toglie e non si sposta**: la
   skill può solo dichiararla aperta.
5. **`completa` dice l'ancora della proposta, non l'attacco vero**: «su volano.primary_in» per lo scarico
   che sta sull'attacco di scarico del volume. Viene dal resoconto delle regole.
6. **Valvole in linea condivise**: la seconda valvola di un pezzo in linea può finire lontana, attaccata
   al pezzo dopo — quella del separatore d'aria sta davanti alla deviatrice —, e nessun rilievo lo
   segnala.
7. **Capire e il catalogo non si dicono la stessa cosa**: la caldaia del catalogo non porta il
   circolatore a bordo, l'esempio di Capire (§6) dice di sì; §5 di Capire non elenca fra i mestieri la
   deviatrice, il separatore d'aria e il rubinetto portamanometro.
8. **Le reti dell'acqua fredda che le regole creano** — quella del riempimento, quella della miscelatrice
   — non stanno nella lista dei diametri.
9. **Il grafo da leggere non si scrive per un impianto col solare**: nel naming manca la famiglia di
   linee del solare. Il comando lo dice e continua (è una prova in `tests/skill/test_comando.py`).

### 6.3 L'ambiente in cui la skill gira (punto 1 del pacchetto)

La skill vuole **pydantic**, che la libreria standard non ha: al primo uso `ambiente` lo installa dalla
rete. Le fonti ufficiali, lette il 29 settembre 2026: **su claude.ai la rete di una skill dipende dalle
impostazioni** — piena, parziale o nessuna ([Agent Skills, «Limitations and constraints»](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview));
**dall'API non c'è rete**, e pydantic non è nell'elenco delle librerie installate
([Code execution tool, «Pre-installed libraries»](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool)):
lì la skill non parte, e lo dice. Il PDF invece non ha bisogno di niente, e l'anteprima trova
pypdfium2, che nell'elenco c'è. **Il dato vero del tuo ambiente lo dà la tua prova**: la skill di prova
dell'ambiente che ti ho mandato all'inizio, o più semplicemente il primo messaggio della skill vera, che
dice se è pronta.

Il pacchetto chiedeva, finché il dato non c'è, «dipendenze pure Python portate nella cartella»:
pydantic non è puro Python — il suo nucleo è compilato, per ogni versione di Python e ogni macchina —, e
portarlo nella cartella vorrebbe dire portarne una copia per ciascuna. Ho scelto di installarlo alla
prima chiamata, e di dirlo quando non si può.

## 7. Lo ZIP, e come si carica

[`disegnatore-mep.zip`](disegnatore-mep.zip) — 821 kB, sha256 `c203d388cdba49fc…`, costruito da
`scripts/costruisci-skill.py` sul codice finale.

1. **Su claude.ai, Impostazioni › Funzionalità** (Settings › Features), con l'esecuzione del codice
   attiva: fra le skill, carica lo ZIP così com'è.
2. **In una conversazione nuova, descrivi l'impianto e chiedi lo schema**: la skill parte da sola; se
   non parte, scrivi «usa la skill disegnatore-mep».

Il piano della release vuole che tu la provi **su un impianto tuo** (`PROJECT_STATE.md`, rischio 4):
l'esito si registra.

## 8. Che cosa resta aperto

- **La tua prova su un impianto tuo**, con l'ambiente vero: il criterio 7 ne ha due voci aperte (lo
  scatto dalla descrizione, le librerie su claude.ai).
- **La lettura di I-167**: ho letto lo «skill creatore di dominio» come `skill-creator`, e ne ho usato
  il validatore e la forma delle valutazioni. Se intendevi un'altra cosa, dimmelo.
- **I punti di §6.1**, che sono tuoi, e quelli di §6.2, per il prossimo giro.

## 9. I rami

Sul remoto ci sono i rami dei pacchetti passati, fusi o bocciati, e questo: la sessione ha scritto solo
su questo, e `main` è ancora alla base.

```
$ git fetch origin && git log --oneline -1 origin/main && git branch -r | wc -l
6412016 REL-008 — le scritte della tavola a 9 punti, mai sotto 8: tavole approvate dal PO (I-164, D-194) (#65)
50
```
