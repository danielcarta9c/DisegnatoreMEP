# REL-002 — Il cartiglio Nove C, compilato, sulla tavola — rapporto

**Consegna del 25 settembre 2026** · ramo `claude/epic-newton-r94e4l` · base `main` a `130be28`
**Input:** I-123 («manca il cartiglio»), I-129 (la sessione è solo per il cartiglio), I-130 (il file A3
del 25 settembre), I-131 → **D-186** (gli altri formati).
**Verdetto del PO** (I-132, 26 settembre 2026): «Si tutto perfetto» — tavole approvate, fusione su
`main` con la PR #59.

> **I numeri sono cambiati alla fusione** (I-133). Mentre questa sessione faceva il cartiglio, un'altra
> faceva i simboli (`REL-003`), partita dallo stesso `main`, ed era già fusa: aveva preso I-126, I-127,
> I-128 e D-184. Quelli del cartiglio sono diventati **I-129, I-130, I-131 e D-186**; nei messaggi dei
> commit sul ramo si leggono ancora i vecchi. Prima di fondere, `main` — con i cinque simboli nuovi — è
> stato portato nel ramo, e la suite e il collaudo sono stati rimisurati sul risultato (§ 6).

## Le tavole, per prime (D-146)

Le cinque tavole approvate, rieseguite dai **loro** grafi e piani (`docs/collaudi/DRAW-018/`), col
cartiglio compilato; più una tavola in bozza.

| tavola | formato | che cosa mostra |
|---|---|---|
| [`tavola-1.pdf`](tavole/tavola-1.pdf) | A3 | impianto 1, cartiglio compilato |
| [`tavola-2.pdf`](tavole/tavola-2.pdf) | A3 | impianto 2 |
| [`tavola-3.pdf`](tavole/tavola-3.pdf) | A3 | impianto 3, **con i nomi sulle tre righe delle firme** |
| [`tavola-4.pdf`](tavole/tavola-4.pdf) | A3 | impianto 4 |
| [`tavola-5.pdf`](tavole/tavola-5.pdf) | **A2** | impianto 5: il cartiglio **a misura A3, contro l'angolo in basso a destra** (D-186) |
| [`tavola-1-bozza.pdf`](tavole/tavola-1-bozza.pdf) | A3 | impianto 1 dal grafo com'è agli atti: indirizzo, titolo e numero mancano → «DA DEFINIRE» e «BOZZA — cartiglio incompleto» in testata |

**I dati del cartiglio sono di prova, e inventati** (`dati-di-prova.json`): il repository è pubblico
(D-038). Committente «Condominio di prova», indirizzo «Via di Prova 1, 00000 Comune di Prova (XX)»,
titolo «Schema funzionale della centrale termica», numeri T1…T5, e come dicitura in testata quella
del file del PO. Progetto, commessa, data e revisione sono quelli che i grafi avevano già.

Per rifarle: `PYTHONPATH=src python3 docs/collaudi/REL-002/collaudo.py <cartella>` — vuole PyMuPDF,
numpy e il browser di `scripts/to-pdf.sh`, come gli altri strumenti di sessione.

## Che cosa cambia sulla tavola, e che cosa no

- **Il cartiglio è quello del file del PO**: logo, fasce, caselle, colori, caratteri, nell'ordine in
  cui il file li dipinge. Prima c'era una fascia vuota con «BOZZA — cartiglio non compilato».
- **La squadratura** è quella del file: blu `#1C2E4A`, 0,176 mm. Prima era nera, 0,35 mm.
- **La testata** è quella del file: «NOVE C INGEGNERIA | Documento confidenziale | *commessa* –
  Elaborati Grafici» a sinistra, la dicitura a destra. Prima c'era il nome del progetto, che adesso
  sta nella casella PROGETTO.
- **Il disegno non cambia di un pixel** (criterio 2, sotto).

## Le misure

Ogni criterio con il comando e il suo esito.

**1. Il cartiglio è quello del PO** — `PYTHONPATH=src python3 docs/collaudi/REL-002/fedelta.py <cartella> 300 --browser`.
Il cartiglio disegnato con **i segnaposto del file** al posto dei valori, su un A3 vuoto, contro il PDF
del PO, tutt'e due resi da MuPDF a 300 dpi:

```
l'SVG della skill, reso da MuPDF, contro il file del PO:
  pixel diversi (soglia 64/255): 2980 su 17403188 (0.017 %)
  pixel diversi fuori dai riquadri dei testi: 0
```

Contate casella per casella, le differenze stanno **solo nei sei valori che il PO ha ritoccato nel
suo editor** — nel file sono Arial, qui Helvetica: 637 · 180 · 635 · 465 · 304 · 186 pixel — e nella
scritta **«TAVOLA»** (573), che è bianca al 50 %: **MuPDF, rendendo un SVG, ignora la trasparenza** e la
fa bianca piena. Nel PDF della tavola, fatto dal browser, «TAVOLA» ha **esattamente** il colore del file
— 140 · 149 · 163 in tutt'e due. Tratti, campiture, etichette, testata e logo coincidono
([`differenze-fascia.png`](differenze-fascia.png)). In più, **letto con un secondo strumento**
(PyMuPDF) il modello torna su tutti i 21 tracciati e i 23 testi del file, scarto massimo 0,0004 mm.

**2. Il disegno non cambia** — `collaudo.py`, che confronta ogni tavola col cartiglio con la stessa
tavola senza cartiglio, dagli stessi grafo e piano, fra la testata e il cartiglio:

```
tavola       formato   disegno: pixel diversi  cartiglio
impianto-1   A3               0 su 5790706      completo
impianto-2   A3               0 su 5790706      completo
impianto-3   A3               0 su 5790706      completo
impianto-4   A3               0 su 5790706      completo
impianto-5   A2               0 su 12683232     completo
bozza-1      A3                                Cartiglio della tavola t1: campi da definire: INDIRIZZO, TITOLO TAVOLA, TAVOLA — nella casella c'e' «DA DEFINIRE» e la tavola esce in bozza (D-025)
```

E la misura della sessione (`docs/collaudi/DRAW-017/misura-tavole.py --dettaglio`) sui cinque piani
dà **le stesse righe su `main` e sul ramo**: formato, 25 · 25 · 24 · 27 · 56 tratte, zero cedute, zero
bloccanti, rilievi 1 · 1 · 1 · 2 · 1, incroci 1 · 1 · 2 · 2 · 5 — il metro delle tavole approvate.

**3. Il modello si rigenera identico, e il logo è quello del file** —
`tests/catalog/test_generated_fixtures.py` rilancia `examples/cartigli/build_cartiglio.py` e pretende
lo stesso modello; `tests/graphics/test_cartiglio.py` ritrova il logo nel PDF per conto suo e lo
confronta byte per byte (sha256 `779f3afe…`), e controlla che il modello porti l'impronta del PDF.

**4. I dati** — in `tests/graphics/test_cartiglio.py`: un campo obbligatorio che manca dà «DA
DEFINIRE» e la bozza; `ND` di «Capire» vale come dato che manca; firme e dicitura non sono
obbligatorie; un testo resta nella sua casella — scende di corpo fino a 7 pt, poi va su due righe
senza toccare l'etichetta — e se non entra nemmeno così si scrive **intero** e la tavola è una bozza;
i doppi spazi della testata restano due.

**5. I formati (D-186)** — il cartiglio sull'A3 sta dove sta nel file; su A2 e A1 si sposta intero
contro l'angolo in basso a destra, e la testata corre per tutta la squadratura; sull'A4 si rifiuta.
L'A4 è uscito dai formati ordinari: `frame.ORDINARY_FRAMES`, `piano/formato.py`, l'esecutore, il
preflight, le istruzioni di «Comporre» e `docs/regole-del-piano.md`.

**6. La suite** — `pytest -q`, sul commit `106bc18` e su `main` a `130be28`, ciascuno in una copia
ferma del repository:

```
main   130be28   46 failed, 1690 passed, 24 skipped, 12 xfailed
ramo   106bc18   46 failed, 1743 passed, 24 skipped, 12 xfailed
                 rosse nuove: 0 · rosse sparite: 0
```

Le 46 rosse sono **le stesse**, una per una. Zero `skip` e zero `xfail` nuovi. `ruff check src tests`:
verde. `mypy src tests`: 4 errori, **gli stessi 4 di `main`**, in due file che questo pacchetto non
tocca.

**E dopo aver portato nel ramo il `main` dei simboli** (`REL-003`, prima parte, PR #58), sul commit
di fusione `7a5d8e8` contro `main` a `6d8d82e`:

```
main   6d8d82e   46 failed, 1700 passed, 24 skipped, 12 xfailed
fuso   7a5d8e8   46 failed, 1753 passed, 24 skipped, 12 xfailed
                 rosse nuove: 0 · rosse sparite: 0
```

Le sei tavole, rifatte sul risultato della fusione, sono **identiche al pixel** — pagina intera, 150
dpi — a quelle che il PO ha approvato; `ruff` verde, `mypy` con gli stessi 4 errori.

La suite ha trovato **una cosa vera** a metà lavoro, ed è rimasta: togliendo l'A4 dalla scala, la
posa di partenza — che anche l'esecutore del piano usa — smetteva di impilare sull'A3, perché la sua
regola diceva «tranne sul foglio più piccolo» e il più piccolo era diventato l'A3. Sui cinque piani
approvati non cambiava niente, su altri impianti sì. **La riga adesso nomina l'A4** (`layout/place.py`,
fuori dal perimetro dichiarato, e il pacchetto lo dice), e una prova la tiene.

## Le scelte della sessione, da guardare

Il file non le dice, e le ho fatte io; sono tutte sulle tavole:

- **i nomi delle firme** si scrivono sulla riga della firma, 0,7 mm sopra, a 6 punti, nel colore dei
  valori (tavola 3);
- **la bozza e la modalità di verifica** si scrivono in testata a destra, prima della dicitura, in
  neretto e nel colore dei valori (tavola in bozza);
- **un testo lungo** scende di mezzo punto alla volta fino a 7 pt — il corpo più piccolo che il file
  usa per un valore — e poi va su due righe, con interlinea 1,2;
- **su A2 e A1 la testata corre per tutta la squadratura**, perché nel file sta sul bordo superiore e
  non dentro il cartiglio (D-186, nota della sessione);
- in testata il file ha ancora **«MI.223»** e **«Conto Termico con sconto in fattura»**: li ho letti
  come la commessa e una dicitura da compilare (I-130);
- **la scala è «—»** fissa, come nel file: lo schema non è in scala.

## Rilievi per il PO

- **Colori e carattere del cartiglio non sono quelli della guida brand di maggio 2026**: il file usa
  `#1C2E4A`, `#2ABFBF` e Helvetica/Arial, la guida Petrol Navy `#0B2F45`, Teal Cyan `#168995` e Aptos. Ho
  riprodotto il file com'è.
- **`scripts/to-pdf.sh` non stampa a misura esatta.** Il browser arrotonda la pagina a 420,2 mm e
  scala il disegno di −0,025 % in orizzontale e +0,043 % in verticale: 410 mm diventano 409,896, 287
  diventano 287,122. Vale per tutte le tavole fatte finora, approvate comprese; è lo strumento che
  `REL-001` sostituisce col PDF fatto dalla skill, e lì va misurato
  ([`differenze-fascia-browser.png`](differenze-fascia-browser.png)).
- **Il logo pesa**: è il JPEG del file, 2961 × 716 pixel su 58 mm — circa 1300 dpi —, e porta l'SVG
  di una tavola da 37 a 331 KB. Una copia più leggera sarebbe un'immagine derivata, e quindi una tua
  scelta.
- **I testi del disegno** — sigle, legenda — non dichiarano un carattere, e il browser li stampa con
  le grazie, mentre il cartiglio è in Helvetica. Non l'ho toccato: è convenzione grafica (D-165).
- **`mypy` ha 4 errori già su `main`**, in due file di prova che questo pacchetto non tocca
  (`tests/layout/test_posa_a_fasi.py`, `tests/validation/test_regole_del_piano.py`). Nessuno nuovo.

## Che cosa porta il ramo

| dove | che cosa |
|---|---|
| `assets/cartigli/` | il PDF del 25 settembre, il **modello** `Cartiglio_NoveC_A3.json` e il **logo**, derivati |
| `examples/cartigli/build_cartiglio.py` | il generatore del modello: legge il PDF con la sola libreria standard |
| `examples/cartigli/build_metriche.py` | il generatore delle larghezze dei caratteri, da Liberation Sans |
| `src/disegnatore_mep/graphics/cartiglio.py` | il modello, i dati, la misura dei testi, il disegno |
| `src/disegnatore_mep/graphics/metriche.py` | le larghezze, generate |
| `src/disegnatore_mep/graphics/sheet.py` | `render_sheet` disegna il cartiglio quando lo riceve |
| `src/disegnatore_mep/cli.py` | `--cartiglio` su `draw`, `piano`, `revisiona` |
| `src/disegnatore_mep/model/project.py`, `schemas/project.schema.json` | i dati del cartiglio: sette campi facoltativi nei metadati e il numero della tavola; **un dato che manca non si scrive**, quindi i documenti di prima si riscrivono identici e la loro impronta non cambia |
| `frame.py`, `piano/`, `validation/preflight.py` | l'A4 fuori dai formati ordinari (D-186) |
| `skill/capire/ISTRUZIONI.md` | che cosa chiedere per il cartiglio, in una voce sola, e che cosa non inventare |
| `tests/` | `tests/graphics/test_cartiglio.py`; le prove che nominavano l'A4 salgono di un foglio, con D-186 scritta accanto |

## Dopo

Il comando della skill che `REL-001` scriverà deve passare `--cartiglio`, e il PDF senza browser deve
saper scrivere un JPEG e un testo trasparente al 50 %. Le domande del cartiglio le fa già «Capire»:
`REL-001` le porta al progettista con le altre.
