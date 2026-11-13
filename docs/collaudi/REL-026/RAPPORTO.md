# REL-026 — La 2.1.0: i rilievi d'uso della 2.0.0 su una commessa. Rapporto

**13 novembre 2026.** Pacchetto: `ACTIVE_WORK_PACKAGE.md` (I-300). Ramo `claude/magical-wright-ffrf86`, PR #95.
**Stato: in attesa che il PO guardi le tavole. Non è fuso.**

Il lavoro esecutivo l'hanno fatto quattro agenti della sessione (D-152), uno per blocco, ciascuno nel suo albero di
lavoro; la sessione ha scritto il pacchetto, unito i rami, rieseguito le misure e guardato le tavole. Quello che gli
agenti hanno riferito sta nei rapporti dei blocchi; **quello che è scritto qui è stato rieseguito dalla sessione** sul
ramo unito, salvo dove è detto il contrario.

| blocco | che cosa | rapporto |
|---|---|---|
| A | catalogo, schema, vaso | `blocco-a/RAPPORTO.md` |
| B | la pianta, prima parte | `blocco-b/RAPPORTO.md` |
| C-1, C-2 | le scritte fuori pianta | `blocco-c-scritte/RAPPORTO.md` |
| C-3 | la base architettonica | `blocco-c-base/RAPPORTO.md` |

## 1. Le tavole, per prime (D-146)

**Le tavole escono da tutti i casi.** Nessun caso di prova è rimasto senza tavola.

| che cosa guardare | dove |
|---|---|
| la base architettonica: origine, base standard, sovrapposizione, impianto sopra | `blocco-c-base/anonimo/1-origine.png` … `4-impianto.png` |
| le scritte fuori pianta: prima tre fogli, dopo uno | `blocco-c-scritte/fitta/prima/`, `…/fitta/dopo/centrale-fitta.png` |
| lo stesso sull'appartamento e sul T3 | `blocco-c-scritte/appartamento/`, `…/t3/`, `…/t3-esempio/` |
| i simboli nuovi | `blocco-a/simboli-nuovi.png` |
| tre ventilconvettori con plenum a 2, 3, 6 uscite | `blocco-a/plenum-di-mandata/tavola/` |
| il plenum motorizzato col ventilconvettore idronico | `blocco-a/plenum-motorizzato/tavola/` |
| il confronto che non cambia il foglio: prima A1, dopo A3 | `blocco-b/discordanze/prima/discordanze.png`, `finale/discordanze/discordanze.png` |
| le lunghezze dalla pianta al grafo | `blocco-b/lunghezze/` |

Le cartelle `blocco-b/` sono la fotografia del blocco B alla sua consegna (i dettagli si aprivano ancora da soli); le
cartelle `blocco-c-*/` e `finale/` sono rifatte **col codice unito** (`rifai_le_tavole.py` in ciascuna).

### Quello che alla sessione sembra sbagliato, anche con i controlli a posto

- **I richiami lunghi.** Un pezzo in mezzo alla pianta (un termostato, la centrale di zona) esce con un richiamo di
  8–12 cm che taglia un locale intero: `blocco-c-scritte/appartamento/dopo/` (TZ-03, TZ-04, CZ-01),
  `finale/discordanze/` (TZ-01 e T55, due linee parallele lungo tutto il disimpegno). Si legge, ma è pesante. Nel caso
  fitto il vecchio dettaglio a 1:20 si leggeva meglio: si può ancora chiedere in `dettagli`.
- **Un richiamo sopra una scritta**: nell'appartamento TZ-04 passa sopra la scritta di T16. Il controllo lo conta
  (`richiami_fuori_sopra_scritte_o_pezzi`) e non ferma la consegna.
- **Il ritorno «col dente»** a ogni confluenza dei ventilconvettori nello schema (i raccordi a T non si specchiano).
- **I plenum a 2 e 3 uscite** si leggono «rettangolo dentro rettangolo»; l'ingresso dei plenum pari sta 1,25 mm fuori
  dal centro, sulla griglia.
- **Le sigle numerate dal basso** (PL-01 è l'ultimo in fondo alla tavola).
- **La tavola della sola base** porta la colonna dell'impianto vuota; **il contorno dei muri** a 1:20 si vede appena.

## 2. Che cosa ha cambiato l'unione dei blocchi

I due rami del blocco C toccavano gli stessi file. Conflitti in `pianta/tavola.py` (il blocco delle scritte fuori e il
ciclo dei nomi dei locali) e in `tests/pianta/conftest.py`, risolti tenendo le due cose.

**Un difetto è nato dall'unione, e l'ha visto una prova, poi la tavola**: con i richiami delle scritte fuori che
attraversano i locali, il nome di un locale non trovava più posto per la scritta intera e perdeva i mq («Camera 3»,
«Disimpegno»). Corretto: prima di rinunciare ai mq il nome va **su due righe**, il nome sopra, zona e mq sotto
(`scritte.posa_dentro_su_due_righe`). Ordine dei tentativi: una riga a 9 pt, due righe a 9 pt, una riga a 8 pt, due
righe a 8 pt, il nome solo. È una scelta grafica: **da confermare dal PO** (§6).

Durante l'unione una corsa della suite ha dato 9 falliti: la sessione stava cambiando i file mentre girava. Rifatta a
file fermi, 0 falliti (§3).

## 3. I criteri, ciascuno col suo comando

Misurati dalla sessione sull'ultima testa del ramo (il commit che porta questo rapporto), nel `.venv` del repository.
La base (`d9c8f2e`, la 2.0.0 col pacchetto scritto) dava 2922 passed, 15 skipped, 11 xfailed (`blocco-a/RAPPORTO.md`, §3).

| criterio | comando | output | esito |
|---|---|---|---|
| le tavole per prime | §1 | escono da tutti i casi | raggiunto |
| suite a 0 failed, senza skip o xfail nuovi | `python -m pytest -q -p no:cacheprovider` | `3156 passed, 15 skipped, 11 xfailed in 369.22s` | raggiunto (skip e xfail: gli stessi 15 e 11 della base) |
| ruff verde | `ruff check src tests scripts skill/scripts` | `All checks passed!` | raggiunto |
| mypy verde | `python -m mypy` | `Success: no issues found in 131 source files` | raggiunto |
| il banco verde | `python scripts/banco.py` | `30 uguali, 0 cambiati, su 30` | raggiunto |
| le tavole cambiate registrate e mostrate | confronto di `tests/banco/impronte.json` con `origin/main` | 28 casi → 30: nuovi `plenum-di-mandata-rel026`, `plenum-motorizzato-rel026`; cambiato `collaudo-t3-rel012` (la pianta: niente dettagli automatici, la base nuova, le scritte fuori); cambiata un'impronta di `t1-rel023`, `distinta/distinta.json` (la sola impronta delle regole, per la riga in più di `corredo.json`: `blocco-a/RAPPORTO.md`) | raggiunto: `blocco-c-scritte/t3/`, `blocco-c-base/t3/` |
| nessun dato di cliente nel diff | ricerca nel diff di nomi, indirizzi e codici fiscali delle planimetrie del PO; elenco dei PDF e delle immagini fuori da `docs/collaudi` | nessun riscontro; un solo PDF, `examples/pianta/casi/base-anonima/planimetria.pdf`, inventato | raggiunto |
| la 2.1.0 costruita con `scripts/costruisci-skill.py` | `python scripts/costruisci-skill.py --out …` | `155 file, 3659 kB` · `Controlli della guida di Anthropic, di skill-creator e del caricamento su claude.ai (al massimo 200 file): passati.` · sha256 `d14b83f0ba00760b…` | raggiunto |
| `tests/test_le_release.py` verde | `python -m pytest -q -p no:cacheprovider tests/test_le_release.py tests/test_il_banco.py tests/test_package.py` | `38 passed in 27.89s` | raggiunto |
| `SKILL.md` sotto le 500 righe | `wc -l skill/SKILL.md` | `465` | raggiunto |
| la CI verde sulla PR | GitHub Actions sulla PR #95 | verde sull'unione dei blocchi (`2ef0ad0`); **sull'ultima testa si legge sulla PR**: questo rapporto è scritto prima che giri | da leggere sulla PR |

## 4. Che cosa non è stato fatto o verificato

- **La misura dei 72 avvisi di `pianta --grafo` sulla commessa** (B-5): grafo e pianta di BD.RM.260 non sono arrivati
  in sessione. Il comportamento è provato su un caso anonimo con 49 discordanze (`finale/discordanze/`).
- **La fotografia di un catastale stampato**: l'immagine era solo nella conversazione, non su disco. Non provata.
- **Gli aiuti deterministici sul PDF vettoriale** (leggere i tratti): non fatti. Due «catastali vettoriali» su due
  sono immagini a 1 bit dentro il PDF.
- **Il DXF non è stato aperto in AutoCAD**; della resa dei PDF è provato solo pypdfium2.
- **Il PDF della distinta** non esce in sessione (serve la skill `nove-c-report` accanto): il contenuto è in Markdown.
- **I tempi**: la suite passa da 248 a circa 370 secondi; la pianta dell'appartamento, senza PNG, da 2,2 a 5,5 s (le
  prove di spostamento della pianta per le scritte fuori).

## 5. La prova in camera pulita della lettura della base (C-3)

Quattro agenti nuovi, uno per planimetria, hanno ricevuto **solo** il testo che `skill/base/ISTRUZIONI.md` §2 dice
di passare al sub-agente, la skill costruita (`scripts/costruisci-skill.py`) e la planimetria. Non potevano leggere il
repository né il lavoro dell'agente che ha scritto le istruzioni. Le planimetrie sono quelle vere del PO: basi,
immagini e rapporti stanno **nella sessione**, non qui. La sessione ha guardato le otto immagini (sovrapposizione e
base standard di ciascuna).

| planimetria | tempo dichiarato | che cosa ha consegnato | come combacia (controllo a vista della sessione) |
|---|---|---|---|
| progetto dell'architetto, 1:50 su A3, vettoriale, con arredi | 13 min | 47 muri, 19 aperture, 8 stanze; 107,7 m² netti; 9 domande | i muri sulle linee del disegno, nicchie e cavedi compresi; arredi e armadi a muro fuori |
| catastale 1:200 (immagine a 200 dpi nel PDF), un piano | 22 min | 34 muri, 24 aperture, 10 stanze, 4 balconi; 104,6 m²; 7 domande | i muri sulle linee, balconi sui parapetti; taratura sulla barra e sulle porte |
| catastale 1:200 con tre piani sul foglio | 15 min | il solo piano terra: 13 muri, 14 aperture, 7 stanze, 4 fra portici e scale esterne; 80,6 m²; 8 domande | i muri sulle linee entro un pixel (2,5 cm); taratura sulla barra, scarto 0,05 % |
| disegno a mano quotato, scansito | 12 min | 15 muri, 16 aperture, 8 stanze, una scala esterna; 96,0 m²; 7 domande | i muri entro 5–10 cm dallo schizzo, come le quote; scala diversa nei due versi (2,9 %), trovata e dichiarata |

**Esito: le istruzioni sono bastate in tutti e quattro i casi.** Ogni agente ha consegnato una base che si carica, una
sovrapposizione che combacia, i locali col nome e i mq, e le cose non dette come **domande** (l'ingresso, i versi
delle porte, lo stato di fatto o di progetto, i locali senza nome). Nessuno ha trascritto arredi, né nomi o dati
catastali dal cartiglio. **Ma in due basi su quattro `sfondo.file` porta il nome del file ricevuto, che contiene un
riferimento al committente** (contato dalla sessione sui quattro `base.json`): gli altri due agenti l'avevano copiato
con un nome neutro di loro iniziativa. Ora lo dicono le istruzioni. I tempi sono quelli dichiarati dagli agenti: non
sono stati misurati dalla sessione.

**Limiti della prova, da dire:**
- nel caso dei tre piani la richiesta **diceva già** quale piano («quello con soggiorno e cucina»): la domanda sul
  piano, che `CONSEGNA.md` voleva provare, non è stata provata;
- sul progetto vettoriale l'agente **non ha seguito il metodo a griglia**: ha letto i tratti del PDF con uno script
  suo (pdfplumber) e li ha convertiti con la stessa taratura. Il risultato è buono, ma la lettura a griglia di una
  planimetria di 47 muri non è provata;
- due agenti su quattro si sono scritti un piccolo strumento per **misurare** i pixel scuri lungo una riga: sul
  catastale a 1:200 la sola griglia non bastava (uno ha sbagliato di 0,5 m una faccia, e se n'è accorto dalla
  sovrapposizione);
- la fotografia di un catastale non è provata (§4).

**Che cosa la prova ha fatto correggere** (nello stesso ramo, dopo la prova: le correzioni non sono a loro volta provate
in camera pulita):
- **la porta senza verso** usciva con un arco da una parte a caso, che sulla tavola sembra un dato letto: ora esce
  **chiusa**, un tratto nel vano (`pianta/base.py`, con la prova). Segnalato da tre agenti su quattro;
- **`base base.json --zona`** riscriveva la sovrapposizione intera con l'ultimo riquadro: ora il riquadro ha il suo
  file. Segnalato da tre agenti su quattro;
- **un locale stretto col nome lungo restava senza nome in silenzio**: `pianta` ora stampa «Locali col nome sulla
  tavola: n su n», con quelli che restano senza;
- **nelle istruzioni**: il file della planimetria si copia con un nome neutro (quello ricevuto portava il nome del
  committente, e finiva nei nomi dei file); la risoluzione nativa dell'immagine; il PDF vettoriale come aiuto; stato di
  fatto e di progetto (gialli e rossi); le catene di quote che non chiudono; i segni di porte e finestre sul catastale;
  portici, pilastri, cavedi, setti isolati; i nomi senza arredi; la barra della scala da confermare sulle porte; le
  `note` che escono sulla tavola.

**Che cosa la prova suggerisce, e non è stato fatto** (va fra le decisioni del PO, §6):
- **un aiuto per misurare**: un'opzione del comando che stampi, in metri, le linee incontrate lungo una riga o una
  colonna dell'immagine; e, per il PDF vettoriale, l'elenco dei tratti spessi. Due agenti se li sono costruiti da sé in
  pochi minuti. Il rapporto del blocco C-3 aveva concluso che l'estrattore non serviva: la prova dice il contrario per
  il progetto dell'architetto;
- **il comando potrebbe dire** da sé che la pagina è un'immagine e a quale risoluzione è nata;
- **la tavola della sola base** esce in A2 o in A1 con la colonna dell'impianto vuota e le note di lavoro: una resa
  «solo base», più piccola, sarebbe più utile da mostrare al progettista;
- la porta **a due ante disuguali** non ha una voce (esce con due ante uguali).

## 6. Che cosa decide il PO

Niente di quanto segue è stato deciso dalla sessione: è implementato come **proposta**, perché si veda sulla tavola.

**Simboli e schema** — la forma del ventilconvettore canalizzato idronico e dei plenum di mandata, la sigla PL;
l'ingresso dei plenum pari sulla griglia (1,25 mm fuori centro) o al centro esatto; il nome «Ventilconvettore
canalizzato», oggi uguale per `fan-coil-ducted` e `fan-coil-ducted-air`; il corredo di distinta dei pezzi nuovi (oggi
DA DEFINIRE, sezione X); la distinta che dice «unità interna» anche per il ventilconvettore; le porte
`consenso_in`/`consenso` tenute facoltative; la porta `p1p2` del `zone-controller`, obbligatoria, nell'esempio collegata
al `bus` del ventilconvettore.

**Vaso sanitario** — la precarica uguale alla pressione di rete; il margine fino a 5 bar (taratura − 0,5); la serie
delle taglie e la scelta della taglia (sull'esempio di Caleffi il comando sceglie 80 l, Caleffi propone 60); l'acqua
fredda a 10 °C.

**Base architettonica** — i colori (muri `#dcdcdc` col contorno `#a8a8a8`, finestre `#d6ecfa`/`#74b3e0`, porte
`#a0a0a0`, nomi `#8a8a8a`); un grigio solo per perimetrali e tramezze; il contorno dei muri a 1:20; i gradini delle
scale; il nome su due righe, poi a 8 pt, poi senza mq; la portafinestra come finestra; i balconi col solo contorno; lo
sfondo fuori dalla tavola quando la base è ridisegnata; **la porta senza verso disegnata chiusa**; lo stato di progetto
come assunzione quando nessuno risponde; gli aiuti per misurare (le linee lungo una riga, i tratti del PDF
vettoriale), che la camera pulita suggerisce (§5).

**Scritte e pianta** — l'ordine dei ripieghi (accanto, richiamo corto, numero in legenda, e solo alla fine fuori); le
righe sopra e sotto oltre alle colonne ai lati; la pianta spostata dal centro del foglio prima di cambiare formato; i
richiami lunghi; «T05/T06» con la barra; il richiamo sopra una scritta permesso come ultima risorsa; un dettaglio
chiesto che si tiene le scritte del suo nodo; le lunghezze nel grafo al millimetro; le tubazioni della centrale «non
in pianta» nel confronto; l'A2 → A3 del T3 con le forature spente.
