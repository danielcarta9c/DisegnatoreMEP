# REL-026 — Voce C-3, la base architettonica della tavola MEP: rapporto

**Scritto il 13 novembre 2026** dall'agente esecutivo della voce C-3 (D-152). Base: `ff89e30` (il ramo della
sessione con i blocchi A e B). Quello che segue non è una misura per l'orchestratore finché non l'ha rieseguito.

> Il worktree era nato su `54262a1` (la 1.15.0) e il contenitore è stato riavviato a metà lavoro: il ramo, ancora
> senza commit, è stato portato su `ff89e30`, e il lavoro è ripartito da lì. Nessun altro ramo è stato toccato.

## 1. Le tavole, per prime

Da ogni caso esce la tavola. Si rifanno con `.venv/bin/python docs/collaudi/REL-026/blocco-c-base/rifai_le_tavole.py`
(il «prima» gira sulle sorgenti di `ff89e30`, estratte con `git archive`); formato e scala in `misure.txt`.

| cartella | che cosa guardare |
|---|---|
| `t3/prima/pianta.png` → `t3/dopo/pianta.png` | il collaudo T3 del banco: muri **grigio chiaro con un contorno sottile**, un grigio solo per perimetrali e tramezze (prima il perimetro era grigio scuro e le tramezze più chiare), angoli chiusi senza linee interne; **i nomi dei locali in grigio** invece che in blu scuro; l'impianto a colore pieno sopra. Stesso foglio (A3 1:50), stessi percorsi (`pianta.tracciati.json` del banco identico) |
| `t3/*/pianta-dettaglio-A/B/C.png` | i riquadri di dettaglio: la base ritagliata, la stessa grafica |
| `sagome/prima/` → `sagome/dopo/` | il caso di B-2: le sagome **unite** dove si toccano, un contorno solo; le finestre celesti; le porte a tratto fine; c'è il DXF (`sagome-muri.dxf`) |
| `anonimo/1-origine.png` | il caso anonimo di C-3: **la planimetria d'origine**, inventata e disegnata come la disegna un architetto — muri campiti di nero, arredi, quote, il retino del balcone, i nomi in maiuscolo coi mq, il cartiglio di uno studio che non esiste |
| `anonimo/2-base-standard.png` | **la stessa base, ridisegnata nella grafica standard**: arredi, quote e retini spariti, i nomi dei locali coi mq calcolati dal poligono, il balcone col contorno |
| `anonimo/3-sovrapposizione.png` (e `.pdf`) | **il controllo a vista**: la planimetria schiarita, la griglia in metri, la base trascritta sopra in rosso (muri), blu (finestre), verde (porte), viola (stanze), arancio (balconi) |
| `anonimo/4-impianto.png` (`.pdf`, `.dxf`) | la tavola con un canalizzato sopra la base: l'impianto si legge, la base sta dietro |

### Quello che le tavole hanno mostrato e i numeri no

1. **Il nome del bagno stretto usciva dalla porta** (corretto, `4c32dc5`). Sulla base trascritta dal vettoriale di
   progetto del PO, «Bagno 2 · 3,5 m²» stava a cavallo del vano della porta, fuori dal locale: il bagno è largo 1,36
   m e la scritta a 9 pt ne misura circa 1,5. Nessun controllo lo diceva (la scritta non toccava linee). Ora il nome
   sta dentro il poligono del locale; se non ci sta prova a 8 pt, poi il nome solo; e un balcone stretto del disegno a
   mano, che prima restava **senza nome in silenzio**, ora ha «Scala esterna».
2. **Le scritte della griglia della sovrapposizione cadevano fuori dall'immagine** (corretto): i numeri stavano sul
   bordo esterno della zona guardata, e la zona si taglia sul bordo della pagina; la legenda copriva il soggiorno.
   Ora `x=` e `y=` si ripetono dentro la zona ogni quattro maglie e la legenda è una riga sul bordo basso.
3. **Il contorno dei muri a 1:20 si vede appena** (non cambiato, §6 punto 3): è lo stesso tratto da 0,13 mm della
   tavola intera, su un grigio vicino.
4. **La tavola della sola base porta ancora la colonna dell'impianto vuota** (legenda «Pezzo posato», tabella
   TRATTE senza righe): è la colonna della pianta, che non è di C-3. Si vede su `anonimo/2-base-standard.png`.
5. Il T3 non ha finestre (è una planimetria a parole senza finestre dichiarate): il celeste si vede sugli altri casi.

## 2. Che cosa è stato fatto, punto per punto

### 2.1 Il pezzo AI «leggere la planimetria» — `skill/base/`

`ISTRUZIONI.md` (`a75f937`, 246 righe) nella forma di `skill/capire/`: parla all'agente e basta da sola. Dice che il
lavoro **si affida a un sub-agente** (§2, con il testo da passargli: il file, la pagina, quale piano e quale unità, le
quote note; e che cosa torna: `base.json`, la sovrapposizione, le domande e le stime, la tabella dei locali), i tre
comandi (§3), come si guarda una planimetria qualunque e che cosa è che cosa (§4: vettoriale, catastale, schizzo,
foto; più piani sul foglio; muri, serramenti, arredi, quote, retini, scale, balconi, altre unità), **la taratura**
(§5: quote nei due versi, la barra, la scala dichiarata col formato da verificare, le porte solo come ultima risorsa;
rotazione, prospettiva, origine; come ci si accorge che è sbagliata), che cosa si trascrive e che cosa no (§6),
la procedura (§7), **il controllo a vista obbligatorio** con i criteri (§8), che cosa si restituisce (§9) e gli
errori delle prove (§10). `CONSEGNA.md` dice che cosa si restituisce, come si giudica (quattro criteri e quattro
esiti) e come si conduce la prova in camera pulita sulle quattro planimetrie del PO, che non entrano nel repository.

L'aggancio: `skill/SKILL.md` (465 righe su 500: il sub-agente e la riga dei riferimenti), `skill/pianta/ISTRUZIONI.md`
(lo `sfondo`, i `balconi`, cerniera e anta delle porte, la base standard e i suoi layer), `skill/scripts/mep.py`
(`base` fra i comandi, con pypdfium2 facoltativo), `scripts/costruisci-skill.py` (`riferimenti/base.md`, con le
sostituzioni dei percorsi). La skill costruita in prova: **154 file**, controlli passati (sotto, §3).

### 2.2 La base in dati, e il suo disegno standard

**I campi nuovi del modello** (`f06e9bf`, `4c32dc5`; `schemas/pianta.schema.json` rigenerato):

| campo | che cosa |
|---|---|
| `sfondo.file` | ora un JPEG, **un PNG o un PDF** |
| `sfondo.pagina`, `sfondo.dpi` | per un PDF: la pagina e la risoluzione della pagina resa (di base 150), quella dei pixel della taratura |
| `sfondo.rotazione` | gradi, in senso orario: una scansione o una foto storte |
| `sfondo.px_per_m_y` | facoltativo: i pixel di un metro lungo y, se diversi da quelli lungo x (lo schizzo del PO: 4 %) |
| `sfondo.sulla_tavola` | se lo sfondo si stampa sulla tavola; se manca, **solo se la base non è ridisegnata** (niente muri, niente sagome) |
| `aperture[].cerniera` | lo stipite con la cerniera (`sinistra`/`destra` su un muro orizzontale, `sopra`/`sotto` su uno verticale; validato) |
| `aperture[].anta` | `battente` (di base), `doppia`, `scorrevole` — solo per le porte (validato) |
| `balconi` | `{id, nome, poligono}`: balconi, terrazzi, logge. **Non sono stanze** (per l'instradatore restano esterni) e non sono zone esterne |

**Il disegno** sta in un modulo nuovo, `pianta/base.py` (`fc09f35`), con i colori in un punto solo:

- **i muri dai `muri` asse-spessore, con i raccordi**: un capo che arriva su un altro muro (entro 5 cm) si allunga fino
  alla faccia lontana dell'altro — l'angolo e la T si chiudono anche con spessori diversi, niente sporge —, un capo
  libero finisce dov'è; poi **l'unione dei muri dritti in un contorno solo** (una griglia sulle coordinate dei
  vertici, le celle piene, i lati di contorno concatenati), con i buchi: un perimetro chiuso è un'area con un buco,
  una campitura sola nel DXF (HATCH con i percorsi dei buchi). Le `sagome_muri`, se ci sono, prendono il posto dei
  muri come in B-2, e anche loro si uniscono dove si toccano. Un muro obliquo si disegna per conto suo;
- **pieno grigio chiaro e contorno sottile** (`GRIGIO_DEI_MURI #dcdcdc`, `CONTORNO_DEI_MURI #a8a8a8`, 0,13 mm);
- **finestre**: il vano campito di celeste (`#d6ecfa`), telaio e vetro a tratto fine (`#74b3e0`), layer `A-GLAZ`;
- **porte**: anta e arco a tratto fine grigio (`#a0a0a0`), con la cerniera, a due ante o scorrevole; `A-DOOR`;
- **balconi**: il contorno (`A-FLOR-OTLN`); **nomi dei locali e dei balconi coi mq** in grigio (`#8a8a8a`), su
  `A-AREA-IDEN`, dentro il loro poligono;
- **lo sfondo resta fuori dalla tavola** quando la base è ridisegnata; il caso del corridoio, che lo stampa, ora lo
  chiede con `"sulla_tavola": true` (la sua prova c'è ancora). Sulla tavola va un JPEG o un PNG diritto: un PDF o
  uno sfondo ruotato si rifiutano col perché.

Il PDF del motore (`graphics/pdf.py`) incorpora ora anche i **PNG pieni** (FlateDecode col predittore PNG: gli IDAT
passano come sono); i PDF con JPEG escono identici a prima (il banco lo conferma). I riquadri di dettaglio
ritagliano le aree coi buchi anello per anello (pari e dispari).

### 2.3 Il controllo a vista — `mep.py base`

`pianta/sovrapposizione.py` (`9787ae1`), comando `base` della skill:

```
python3 scripts/mep.py base <planimetria.pdf|.jpg|.png> --out <cartella> [--pagina N] [--dpi 150] [--zona x0,y0,x1,y1]
python3 scripts/mep.py base <base.json> --out <cartella> [--zona x0,y0,x1,y1]
```

- **con la planimetria**: la pagina come immagine con la **griglia in pixel** (zona in pixel); in console i pixel di
  un metro a 1:50, 1:100 e 1:200 se la pagina è a misura reale;
- **con la pianta**: un foglio grande quanto l'immagine d'origine, l'origine schiarita, la **griglia della pianta in
  metri** (girata come lo sfondo), la base a colori forti; PDF (si ingrandisce) e PNG ai pixel dell'origine, o la
  zona (in metri) ingrandita; in console i **controlli della taratura**: luce mediana delle porte («la taratura è
  sbagliata» se non sta fra 0,65 e 1,00 m, col rapporto), porte fuori da 0,60–1,20, spessori fuori dal plausibile
  per tipo, superfici fuori da 1–80 m², il totale netto.

La pagina di un PDF la rende **quello che l'ambiente ha**, come l'anteprima: PyMuPDF, pypdfium2 o pdftoppm; senza,
il messaggio dice che cosa installare o di chiedere un JPEG. Un JPEG si incorpora com'è; un PNG con la trasparenza
si rifà pieno (libreria standard). **Nessuna dipendenza nuova.** Con il solo `sfondo` (niente muri) la sovrapposizione
è lo strumento per leggere: le coordinate si leggono in metri sulla griglia — è il metodo che le prove hanno
dimostrato più rapido e più sicuro (§4).

### 2.4 Gli aiuti deterministici sul PDF vettoriale — non fatti

Il punto 4 chiedeva un estrattore di tratti dai PDF vettoriali **solo se alla prova serviva**. Misurato con
pypdfium2 sulle quattro planimetrie: **solo il PDF di progetto dell'architetto è vettoriale**; i due «catastali
vettoriali» sono **immagini a 1 bit, 200 dpi, dentro il PDF** (1654 × 2340 px), con i testi del cartiglio in vettoriale;
il disegno a mano è una scansione a strisce (48 immagini). Sull'unico vettoriale la griglia in metri a riquadri di
5–7 m dà il centimetro (a 1:50 e 150 dpi un pixel è 8,5 mm): la precisione basta. Dove l'estrattore aiuterebbe è il
**tempo** — il progetto 1:50 con nicchie e armadi è la lettura più lunga (§4) —: è una proposta, non fatta (§6).

### 2.5 Il caso anonimo

`examples/pianta/casi/base-anonima/` (`73eb8e1`): `disegna_la_planimetria.py` disegna un trilocale inventato con il
PDF del motore (A3, 1:50, stessi byte a ogni giro — una prova lo verifica) — `planimetria.pdf` —; `base-anonima.json`
è la base, con lo `sfondo` tarato sulla scala dichiarata, il balcone, e un canalizzato (unità interna nell'ingresso,
tre bocchette, unità esterna e sezionatore sul balcone, linee frigo in fascio, condensa nel bagno, alimentazione dal
quadro). Entra fra i casi comuni della pianta (`tests/pianta/conftest.py`): niente diagonali, niente scritte su
linee, niente bloccanti. **È una prova del percorso, non della lettura**: la base è stata scritta da chi conosceva la
geometria dello script.

## 3. I controlli

```
$ .venv/bin/python -m pytest -q -p no:cacheprovider
3091 passed, 15 skipped, 11 xfailed in 252.54s (0:04:12)
$ .venv/bin/ruff check src tests scripts skill/scripts
All checks passed!
$ .venv/bin/python -m mypy
Success: no issues found in 130 source files
$ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_il_banco.py tests/test_le_release.py
37 passed in 23.73s
$ .venv/bin/python scripts/costruisci-skill.py --out <scratchpad>/skill-prova
Skill: …/disegnatore-mep (154 file, 3599 kB)
Controlli della guida di Anthropic, di skill-creator e del caricamento su claude.ai (al massimo 200 file): passati.
```

Base: `3054 passed, 15 skipped, 11 xfailed`. Le 37 in più: 22 in `tests/pianta/test_base.py` (raccordi, unione,
buchi, porte, balconi, sfondo fuori dalla tavola, layer del DXF, il PNG nel PDF, i colori in un punto solo,
determinismo), 9 in `tests/pianta/test_sovrapposizione.py`, 6 del caso anonimo nelle prove parametrizzate. Skip e
xfail sono gli stessi. Quattro prove di B-2 sulle sagome sono state riscritte sulla semantica nuova (il pieno è
l'unione delle sagome, provata a punti su una griglia di 61 × 61; nel DXF una campitura per gruppo, coi buchi), col
perché nella docstring. Release non costruita e versione non cambiata, per disposizione (la costruzione sopra è in
una cartella di prova).

## 4. Il banco

```
$ .venv/bin/python scripts/banco.py
… 29 uguali, 1 cambiati, su 30
collaudo-t3-rel012: CAMBIATO
  ~ pianta/pianta-dettaglio-A.svg, pianta-dettaglio-B.svg, pianta-dettaglio-C.svg, pianta.svg
$ .venv/bin/python scripts/banco.py --caso collaudo-t3-rel012 --registra
Impronte scritte: tests/banco/impronte.json (30 casi)
```

Il banco ha una sola pianta, il T3: cambiano le sue quattro tavole — i colori e il contorno della base, i nomi in
grigio —, `pianta.tracciati.json` no (stessi percorsi, stesse misure). Guardate: `t3/dopo/pianta.png`,
`t3/dopo/pianta-dettaglio-A.png`, `sagome/dopo/sagome-muri-dettaglio-A.png` (e tutte quelle del §1). L'orchestratore
le riregistra dopo l'unione col ramo delle scritte.

## 5. La prova sulle planimetrie vere del PO

Fatta in sessione, in `scratchpad/c3/` — **nel repository non c'è niente che ne derivi**. Due planimetrie, come
chiesto: il PDF di progetto dell'architetto (1:50 su A3, con gli arredi) e il disegno a mano quotato.

**Il PDF di progetto.** Taratura sulla scala dichiarata (118,11 px/m a 150 dpi), verificata su una porta (78 cm).
Trascritti 31 muri, 18 aperture, 6 stanze; sovrapposizione guardata intera e corretta una volta (il muro ovest della
cucina spostato di 25 cm, il muro del corridoio più spesso, una porta mancata). Combacia sul perimetro e sulle
tramezze principali; **non combacia nel blocco dei bagni** (nicchie, cavedi, una doccia in nicchia): lì la base è
semplificata. I locali non hanno nome sulla planimetria: nomi dedotti dagli arredi. Il progetto **non disegna i
balconi** che il catastale dello stesso appartamento mostra: è il caso in cui la seconda planimetria completa la
prima (scritto nelle istruzioni come domanda). Circa un'ora e mezza, comprese le correzioni al comando: **la
lettura più lunga**, e il primo tentativo a pixel (prima della griglia in metri) è stato lento e impreciso.

**Il disegno a mano.** Taratura sulle quote: 83,3 px/m in orizzontale e 86,3 in verticale — **4 % di differenza**, da
cui `px_per_m_y`. Coordinate costruite sommando le quote; 15 muri, 16 aperture, 7 stanze, la scala esterna come
balcone. La sovrapposizione mostra **scarti fino a 20 cm in verticale a metà pianta**: lo schizzo non è in scala
nemmeno in un verso solo; topologia, ordine dei locali e aperture combaciano. Le porte non hanno verso: stimato e
dichiarato. Circa 25 minuti.

**Dove il metodo regge e dove no:**

- regge: **tarare prima, poi leggere in metri** sulla griglia della sovrapposizione a riquadri di 5–7 m; il controllo
  a vista trova subito gli errori grossi (un muro spostato, una porta mancata, il verso sbagliato);
- regge con fatica: il **progetto con nicchie, armadi e muri di spessore variabile** — si semplifica, e la
  sovrapposizione dice dove;
- **lo schizzo**: le quote prevalgono, la sovrapposizione si giudica sulla topologia, non sul centimetro;
- **più piani sullo stesso foglio** (il catastale a tre piani): non trascritto da me; le istruzioni fanno della scelta
  del piano una domanda, e la taratura sul catastale (immagine a 200 dpi, 1:200, A4) passa per la scala dichiarata
  verificata;
- **la foto**: non c'era. La rotazione è nel modello e provata solo su dati inventati; la prospettiva non si corregge
  (le istruzioni chiedono una scansione o una foto dall'alto).

Che cosa le prove hanno cambiato nelle istruzioni e nel comando: leggere dai numeri della griglia e non dalla
posizione nell'immagine rimpicciolita; la taratura in due versi; `--zona=` con i negativi, e l'origine che tiene
tutto positivo; gli armadi a muro sono arredi; un muro per tratto dritto; il catastale «vettoriale» che è
un'immagine; il nome dei locali dentro il locale.

**File lasciati in sessione** (dati di clienti, mai nel repository): per ciascuna planimetria la base
(`c3/d01/base.json`, `c3/mano/base.json`), la tavola della base standard (`c3/d01/tavola/base.png`,
`c3/mano/tavola/base.png`), la sovrapposizione (`c3/d01/lavoro/base-sovrapposizione.png` e `.pdf`,
`c3/mano/lavoro/base-sovrapposizione.png` e `.pdf`).

## 6. Da decidere dal PO

1. **I colori della base** (proposte, in `pianta/base.py`): muri `#dcdcdc` con contorno `#a8a8a8` da 0,13 mm, finestre
   `#d6ecfa`/`#74b3e0`, porte `#a0a0a0`, nomi `#8a8a8a`.
2. **Un grigio solo per tutti i muri**: prima la tavola distingueva perimetrali (più scuri) e tramezze. «Muri
   grigiolini» l'ho letto come uno; distinguere i portanti con un grigio appena più scuro è una costante.
3. **Il contorno dei muri** a 1:20 quasi non si vede: tenerlo così, o più scuro nei dettagli.
4. **Le scale**: la base non le disegna; una scala interna è un locale col nome («Scala»). Disegnare i gradini?
5. **I locali stretti**: il nome a 8 pt, o il nome senza i mq («Disimpegno» sul progetto del PO).
6. **La portafinestra** si disegna come finestra (celeste), senza l'anta.
7. **I balconi** col solo contorno, senza retino.
8. **Lo sfondo fuori dalla tavola** quando la base è ridisegnata (così la disposizione): il caso del corridoio lo
   chiede ora esplicitamente.
9. **L'estrattore dei tratti dal PDF vettoriale** (§2.4): non fatto; servirebbe a fare prima sul progetto
   dell'architetto, non a fare meglio.

## 7. Per l'unione col ramo delle scritte

Ho toccato in `pianta/tavola.py`: le costanti (`COLORE_STANZE` → grigio; tolte `COLORE_MURI`, `COLORE_APERTURE`,
`COLORE_DELLE_SAGOME`), `LAYER_FINESTRE`, `LAYER_BALCONI` e due righe di `DESCRIZIONE_DEI_LAYER`; `Area` (campo
`buchi`); `retino_dei_muri` e `disegno_delle_aperture` (ora chiamano `base.py`); `estensione` (i balconi); in
`componi` il blocco dello sfondo e **il ciclo dei nomi dei locali** (stanze e balconi da `base.locali_con_nome`,
dentro il poligono, coi tentativi più piccoli) con la scelta di colore e layer (`del_locale`) — è la parte che
confina con le scritte —; tolta `_superficie`; `_svg`, `scrivi_dxf`, `ritaglia`, `_sposta` per i buchi. In
`pianta/comando.py`: il blocco dello sfondo in `disegna_la_pianta` e `_pixel_dell_immagine`. In `pianta/modello.py`:
`Apertura`, `Balcone` (nuovo), `DPI_DEL_PDF`, `Sfondo`, `Pianta` (`balconi`, `base_ridisegnata`,
`sfondo_sulla_tavola`, i controlli in `coerente`), `ESEMPI`. Fuori dalla pianta: `graphics/pdf.py` (i PNG),
`skill.py` (il comando `base`). Moduli nuovi: `pianta/base.py`, `pianta/sovrapposizione.py`.

## 8. Nessun dato di cliente

Il caso del repository è inventato (committente, studio e indirizzo non esistono). Le planimetrie del PO e tutto
quello che ne deriva stanno solo nella cartella di sessione; in questo rapporto sono descritte per tipo.

## 9. Quello che non è stato fatto o verificato

- **I due catastali non li ho trascritti** (quello a 1:200 dello stesso appartamento e quello a tre piani): restano
  alla prova in camera pulita dell'orchestratore, con `CONSEGNA.md`. **La foto** non c'era.
- **La prova in camera pulita** non è fatta: è dell'orchestratore, con agenti nuovi.
- L'unione dei muri vale per i muri dritti: un muro obliquo si disegna da sé, e dove incontra un muro dritto il suo
  contorno resta visibile. Una sagoma storta idem.
- Della resa della pagina di un PDF ho provato solo pypdfium2: i rami PyMuPDF e pdftoppm sono scritti come
  quelli dell'anteprima, non provati qui. Il PNG con la trasparenza si rifà pieno in Python puro: corretto (provato),
  lento su un'immagine grande (non misurato).
- Il DXF è aperto solo con ezdxf nelle prove, non in AutoCAD.
- La CI non è girata (niente push, per disposizione); nessuna release costruita in `releases/`.
