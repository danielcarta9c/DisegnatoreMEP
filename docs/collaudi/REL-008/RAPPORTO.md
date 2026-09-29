# REL-008 — le scritte della tavola a 9 punti: rapporto

**Pacchetto:** `REL-008` (`ACTIVE_WORK_PACKAGE.md`; I-159) · **Ramo:** `claude/pack-attivo-rel-007-0uotnp`,
ripartito da `main` · **Base:** `main` a `7f2bee8` (PR #64, `REL-007`) · **Avviato dal PO:** il 29 settembre
2026 · **Le regole:** **D-194**, proposta, dalle disposizioni del PO I-159 … I-162

> **Le tavole, per prime**
>
> **Le sei tavole approvate e la variante retrofit, con le scritte a 9 punti**, in PDF e in DXF, in
> [`tavole/`](tavole/): gli stessi grafi, piani e dati di prova di `REL-007`. **Da guardare accanto a quelle di
> `REL-007`** ([`../REL-007/tavole/`](../REL-007/tavole/)), che hanno le scritte a 5 punti.

| tavola | formato | PDF | DXF | che cosa mostra |
|---|---|---|---|---|
| 1 — due pompe di calore in parallelo, accumulo combinato | A3 | [`tavola-1.pdf`](tavole/tavola-1.pdf) | [`tavola-1.dxf`](tavole/tavola-1.dxf) | un DN staccato con freccia (accumulo → radiatori); due DN sacrificati sulle acque fredde |
| 2 — pompa di calore con deviazione fra climatizzazione e ACS | A3 | [`tavola-2.pdf`](tavole/tavola-2.pdf) | [`tavola-2.dxf`](tavole/tavola-2.dxf) | **il disegno scende di 5 mm**, tutto insieme, per la tabella più alta |
| 3 — pompa di calore diretta su pavimento radiante | A3 | [`tavola-3.pdf`](tavole/tavola-3.pdf) | [`tavola-3.dxf`](tavole/tavola-3.dxf) | tutto entra accanto al pezzo |
| 4 — ibrido pompa di calore e caldaia | A3 | [`tavola-4.pdf`](tavole/tavola-4.pdf) | [`tavola-4.dxf`](tavole/tavola-4.dxf) | due DN staccati con freccia (radiatori, acqua calda dello scambiatore); uno sacrificato |
| 5 — tre pompe di calore in cascata, tre secondari e ACS | A2 | [`tavola-5.pdf`](tavole/tavola-5.pdf) | [`tavola-5.dxf`](tavole/tavola-5.dxf) | **CIR-02 a 8 punti** accanto al circolatore; tre DN sacrificati sulle strade secondarie |
| 6 — centrale ibrida con PdC di alta potenza, caldaia modulare e solare | A2 | [`tavola-6.pdf`](tavole/tavola-6.pdf) | [`tavola-6.dxf`](tavole/tavola-6.dxf) | **CIR-03 a 8 punti**; un DN staccato con freccia; uno sacrificato |
| 1 — retrofit | A3 | [`tavola-1-retrofit.pdf`](tavole/tavola-1-retrofit.pdf) | [`tavola-1-retrofit.dxf`](tavole/tavola-1-retrofit.dxf) | tutto entra accanto al pezzo |

## 1. Che cosa guardare sulle tavole

1. **Il corpo.** Sigle, dati accanto ai pezzi, DN, legenda, nota «Øi», tabella, intestazione della bozza: **9
   punti** (3,175 mm), contro i 5,1 di prima. **In Arial**, tutte: la radice dell'SVG lo dichiara, e sigle e
   legenda non escono più con le grazie. Il cartiglio è quello di sempre.
2. **Le sigle.** Accanto al pezzo a 9 punti; dove non entrano, **a 8**, il minimo del PO: succede a CIR-02
   (tavola 5) e a CIR-03 (tavola 6), che sopra il circolatore hanno 5,0 mm e a 9 punti ne chiedono 5,2. **La
   sigla di un pezzo che sta in tabella non si omette** (I-160): se mancasse, il preflight bloccherebbe.
3. **I DN.** Accanto alla linea a 9 punti, poi a 8, poi fra le corsie di una coppia. Se non c'è posto:
   **sulle strade principali** — le autostrade del motore — **un'etichetta staccata con freccia** (I-162):
   quattro, sulle tavole 1, 4 e 6; **sulle strade secondarie il DN si sacrifica** (I-161): sette, sulle
   tavole 1, 4, 5 e 6, tutti su acque fredde in ingresso, bipassi e rami alle utenze.
4. **Il richiamo**, come il tuo esempio (I-162, I-163): **la freccia piena** di 2 mm sul pezzo o sulla
   linea, **un tratto obliquo a 45 gradi**, e **la spalla orizzontale** di 5 mm che arriva alla scritta a metà
   delle sue maiuscole. Sottile e nero, per le sigle e per i DN. **D-075 è superata** su questo punto: §3.1.
5. **La legenda** resta larga 50 mm: i nomi lunghi vanno a capo, a righe più uguali possibile («Valvola
   deviatrice / a tre vie»). La nota «Øi» sta su tre righe.
6. **La tabella** ha righe di 6,25 mm, ed è più larga: sulla tavola 1 da 92,5 a 152,5 mm.
7. **Il disegno** non si è mosso — simboli e linee uguali a quelli di `main` — tranne sulla tavola 2, che
   scende di 5 mm tutta insieme per far posto alla tabella più alta (il meccanismo di `REL-006`).

## 2. Che cosa c'è

- **Il corpo in un posto solo**, `graphics/standard.py`: `CORPO_DELLE_SCRITTE_PT = 9`, `CORPO_MINIMO_PT = 8`,
  `FAMIGLIA_DELLE_SCRITTE`. A4, A3 e A2 lo condividono.
- **La legenda**, `layout/legend.py`: `a_capo` con le larghezze di Arial, bilanciato; il passo di una voce di
  tre righe; SVG e DXF vanno a capo con la stessa funzione.
- **La tabella**, `graphics/tabella.py`: `altezza_della_riga_mm`, dal corpo.
- **Le sigle**, `layout/labels.py`: la larghezza con le metriche di Arial; il ripiego a 8 punti; il corpo
  della sigla nella geometria (`PlacedLabel.corpo_mm`), letto da SVG, DXF, preflight, DN e velo della verifica.
- **I DN**, `layout/diametri.py` e `diametri/tratti.py`: il ripiego a 8 punti, lo spazio dai capi di 1,0 mm, la
  strada principale o secondaria di ogni tratto, l'etichetta staccata con freccia (`richiamo_da`).
- **Il richiamo con freccia e spalla** (I-162, I-163): la geometria in `layout/geometry.py` (`Richiamo`: punta,
  gomito, spalla), costruita da `layout/labels.py` per le sigle e per i DN; SVG e DXF lo disegnano uguale, la
  freccia piena come `SOLID` nel DXF.
- **Il preflight**: `TABLE_EQUIPMENT_TAG_OMITTED`, bloccante (I-160); `DIAMETER_TAG_MISSING` solo sulle strade
  principali (I-161); i controlli sui richiami — incroci, 45 gradi — anche per i DN staccati.
- **Le prove**: `tests/scritte/` (33), e le prove dei diametri, delle etichette e del DXF alla regola nuova.

## 3. Che cosa ho trovato, e va detto

### 3.1 Il richiamo supera D-075

**D-075**, approvata ad agosto, voleva il richiamo come una sola diagonale a 45 gradi fino al testo, senza
tratti orizzontali, perché un tratto orizzontale accanto alle tubazioni si leggeva come un tubo. La sessione
l'aveva proposto così; il PO ha scelto il suo esempio: «a me pero' non piacciono 45 gardi dirette le preferisco
con la spalla come ti ho detto. quindi sovrascriviamo D-075 con questa mia istruzione» (I-163). Il richiamo ha
quindi la spalla; resta a 45 gradi il tratto obliquo, che la distingue da una tubazione, e il preflight lo
misura ancora. La spalla è sottile e nera, lunga 5 mm, e finisce a 0,75 mm dalla scritta: i tubi sono colorati
e più spessi.

### 3.2 Che cosa resta piccolo

Il **cartiglio** ha i corpi del modello dello studio: le etichette dei campi a 5–5,5 punti, le firme a 6,
indirizzo e revisione a 7, i valori principali a 8–9. Anche **l'intestazione** in alto — «NOVE C INGEGNERIA |
Documento confidenziale …» — è del cartiglio, a 5,5 punti. «Tutte le scritte» è stato letto come le scritte
del disegno; il cartiglio si può ingrandire in un passo a sé, dal suo generatore.

### 3.3 Strada principale e strada secondaria

«Strada secondaria» è letta come la linea che il motore non chiama autostrada. Sulle sette tavole i sette DN
sacrificati sono tutti su acque fredde in ingresso, bipassi e rami alle utenze. Il motore però chiama
«distribuzione» anche la mandata delle zone del pavimento radiante della tavola 3, e «autostrada» il loro
ritorno (è la stessa lettura di `REL-007`, §3.1): lì oggi tutto entra, ma se non entrasse la mandata si
sacrificherebbe e il ritorno no.

### 3.4 Le misure che si sono spostate

- Lo **spazio dai capi del pezzo** per il DN passa da 1,5 a 1,0 mm: con 1,5, tredici DN entravano solo a 8
  punti; con 1,0 entrano tutti a 9.
- Le **sigle si misurano in Arial** e non più a 0,6 corpi per carattere: il riquadro di una sigla è quello
  vero, e dove prima non entrava ora può entrare.

## 4. Le misure

**Le tavole e le misure sul disegno** — il collaudo, dalla radice. Prima la geometria di `main` (`REL-007`),
con il codice di `main`, da un albero di lavoro a parte; poi le tavole con il codice del ramo:

```
git worktree add --detach <albero> origin/main
PYTHONPATH=<albero>/src python3 docs/collaudi/REL-008/collaudo.py --base <geometria-di-main>
PYTHONPATH=src python3 docs/collaudi/REL-008/collaudo.py <cartella-di-lavoro> <geometria-di-main>
```

```
== tavola-1 — grafo-completo-1.json, formato A3
   SVG: disegno 54 scritte, 9.0–9.0 pt · tabella 30 scritte, 9.0–9.0 pt · cartiglio 23 scritte, 5.0–34.0 pt
   DXF: disegno 54 scritte, 9.0–9.0 pt · tabella 30 scritte, 9.0–9.0 pt · cartiglio 23 scritte, 5.0–34.0 pt · caratteri ['arial.ttf', 'arialbd.ttf']
   carattere: radice 'Arial, Helvetica, sans-serif'; scritte del disegno che ne dichiarano un altro: nessuna
   scritte accanto ai pezzi: main {'tag': 10, 'data': 2} · ora {'tag': 10, 'data': 2} · mancano nessuna · a 8 pt nessuna · con richiamo nessuna
   DN: main 11 · ora 9 (a 8 pt 0, staccati con freccia ['Øi 32']) · mancano sulle strade principali nessuno · sacrificati sulle secondarie 2 ['Øi 25 inlet-mixing-valve-thermostatic-accumulo-dhw-out→mixing-valve-thermostatic-accumulo-dhw-out', 'Øi 25 acquedotto→accumulo']
   rispetto a main: simboli uguali, tratte uguali · tabella 92.5x30.0 → 152.5x37.5 mm · voci della legenda 18 + 4 · riga «Øi»: si
   i DN toccano qualcosa: 0 — la cosa piu' vicina: Øi 32 da simbolo collettore-mandata a 1.21 mm
   deterministico: SVG uguale (d72d8f07a1df809b), DXF uguale (5b8a3d967414f066)
   preflight: nessun rilievo

== tavola-2 — grafo-completo-2.json, formato A3
   SVG: disegno 57 scritte, 9.0–9.0 pt · tabella 30 scritte, 9.0–9.0 pt · cartiglio 23 scritte, 5.0–34.0 pt
   DXF: disegno 57 scritte, 9.0–9.0 pt · tabella 30 scritte, 9.0–9.0 pt · cartiglio 23 scritte, 5.0–34.0 pt · caratteri ['arial.ttf', 'arialbd.ttf']
   carattere: radice 'Arial, Helvetica, sans-serif'; scritte del disegno che ne dichiarano un altro: nessuna
   scritte accanto ai pezzi: main {'tag': 11} · ora {'tag': 11} · mancano nessuna · a 8 pt nessuna · con richiamo nessuna
   DN: main 7 · ora 7 (a 8 pt 0, staccati con freccia nessuno) · mancano sulle strade principali nessuno · sacrificati sulle secondarie 0 
   rispetto a main: simboli DIVERSI, tratte DIVERSI · tabella 92.5x30.0 → 152.5x37.5 mm · voci della legenda 21 + 4 · riga «Øi»: si
   i DN toccano qualcosa: 0 — la cosa piu' vicina: Øi 25 da linea p4-a a 1.21 mm
   deterministico: SVG uguale (8e79a30fa713e8c6), DXF uguale (483b3dbb15b04162)
   preflight: nessun rilievo

== tavola-3 — grafo-completo-3.json, formato A3
   SVG: disegno 57 scritte, 9.0–9.0 pt · tabella 25 scritte, 9.0–9.0 pt · cartiglio 26 scritte, 5.0–34.0 pt
   DXF: disegno 57 scritte, 9.0–9.0 pt · tabella 25 scritte, 9.0–9.0 pt · cartiglio 26 scritte, 5.0–34.0 pt · caratteri ['arial.ttf', 'arialbd.ttf']
   carattere: radice 'Arial, Helvetica, sans-serif'; scritte del disegno che ne dichiarano un altro: nessuna
   scritte accanto ai pezzi: main {'tag': 11, 'data': 2} · ora {'tag': 11, 'data': 2} · mancano nessuna · a 8 pt nessuna · con richiamo nessuna
   DN: main 7 · ora 7 (a 8 pt 0, staccati con freccia nessuno) · mancano sulle strade principali nessuno · sacrificati sulle secondarie 0 
   rispetto a main: simboli uguali, tratte uguali · tabella 90.0x25.0 → 147.5x31.2 mm · voci della legenda 20 + 4 · riga «Øi»: si
   i DN toccano qualcosa: 0 — la cosa piu' vicina: Øi 25 da simbolo valve-isolation-volano-a a 1.21 mm
   deterministico: SVG uguale (bfd8a91dfe56da6f), DXF uguale (db226d8d469633f1)
   preflight: nessun rilievo

== tavola-4 — grafo-completo-4.json, formato A3
   SVG: disegno 66 scritte, 9.0–9.0 pt · tabella 35 scritte, 9.0–9.0 pt · cartiglio 23 scritte, 5.0–34.0 pt
   DXF: disegno 66 scritte, 9.0–9.0 pt · tabella 35 scritte, 9.0–9.0 pt · cartiglio 23 scritte, 5.0–34.0 pt · caratteri ['arial.ttf', 'arialbd.ttf']
   carattere: radice 'Arial, Helvetica, sans-serif'; scritte del disegno che ne dichiarano un altro: nessuna
   scritte accanto ai pezzi: main {'tag': 14, 'data': 2} · ora {'tag': 14, 'data': 2} · mancano nessuna · a 8 pt nessuna · con richiamo nessuna
   DN: main 12 · ora 11 (a 8 pt 0, staccati con freccia ['Øi 20', 'Øi 32']) · mancano sulle strade principali nessuno · sacrificati sulle secondarie 1 ['Øi 20 acquedotto→scambiatore']
   rispetto a main: simboli uguali, tratte uguali · tabella 92.5x35.0 → 152.5x43.8 mm · voci della legenda 22 + 4 · riga «Øi»: si
   i DN toccano qualcosa: 0 — la cosa piu' vicina: Øi 20 da sigla ACS-01 a 1.16 mm
   deterministico: SVG uguale (dd9cc4eda352d9c6), DXF uguale (9db59a0ea2aec278)
   preflight: nessun rilievo

== tavola-5 — grafo-completo-5.json, formato A2
   SVG: disegno 98 scritte, 8.0–9.0 pt · tabella 60 scritte, 9.0–9.0 pt · cartiglio 23 scritte, 5.0–34.0 pt
   DXF: disegno 98 scritte, 8.0–9.0 pt · tabella 60 scritte, 9.0–9.0 pt · cartiglio 23 scritte, 5.0–34.0 pt · caratteri ['arial.ttf', 'arialbd.ttf']
   carattere: radice 'Arial, Helvetica, sans-serif'; scritte del disegno che ne dichiarano un altro: nessuna
   scritte accanto ai pezzi: main {'tag': 22, 'data': 2} · ora {'tag': 22, 'data': 2} · mancano nessuna · a 8 pt ['CIR-02'] · con richiamo nessuna
   DN: main 29 · ora 26 (a 8 pt 0, staccati con freccia nessuno) · mancano sulle strade principali nessuno · sacrificati sulle secondarie 3 ['Øi 25 inlet-mixing-valve-thermostatic-bollitore-dhw-out→mixing-valve-thermostatic-bollitore-dhw-out', 'Øi 40 ritorno-radiante→miscelatrice-radiante', 'Øi 25 acquedotto→bollitore']
   rispetto a main: simboli uguali, tratte uguali · tabella 95.0x60.0 → 155.0x75.0 mm · voci della legenda 26 + 5 · riga «Øi»: si
   i DN toccano qualcosa: 0 — la cosa piu' vicina: Øi 40 da simbolo tee-thermometer-pdc-1-water-supply a 1.21 mm
   deterministico: SVG uguale (05e3fabbb77f0398), DXF uguale (f74d8255ad2d9ac3)
   preflight: nessun rilievo

== tavola-6 — grafo-completo-6.json, formato A2
   SVG: disegno 82 scritte, 8.0–9.0 pt · tabella 60 scritte, 9.0–9.0 pt · cartiglio 24 scritte, 5.0–34.0 pt
   DXF: disegno 82 scritte, 8.0–9.0 pt · tabella 60 scritte, 9.0–9.0 pt · cartiglio 24 scritte, 5.0–34.0 pt · caratteri ['arial.ttf', 'arialbd.ttf']
   carattere: radice 'Arial, Helvetica, sans-serif'; scritte del disegno che ne dichiarano un altro: nessuna
   scritte accanto ai pezzi: main {'tag': 11, 'data': 2} · ora {'tag': 11, 'data': 2} · mancano nessuna · a 8 pt ['CIR-03'] · con richiamo nessuna
   DN: main 20 · ora 19 (a 8 pt 0, staccati con freccia ['Øi 40']) · mancano sulle strade principali nessuno · sacrificati sulle secondarie 1 ['Øi 32 inlet-mixing-valve-thermostatic-bollitore-dhw-out→mixing-valve-thermostatic-bollitore-dhw-out']
   rispetto a main: simboli uguali, tratte uguali · tabella 102.5x60.0 → 170.0x75.0 mm · voci della legenda 26 + 5 · riga «Øi»: si
   i DN toccano qualcosa: 0 — la cosa piu' vicina: Øi 32 da simbolo circolatore-solare a 0.57 mm
   deterministico: SVG uguale (fe4c3cd8cf27ec25), DXF uguale (69d7aee2c62aefab)
   preflight: nessun rilievo

== tavola-1-retrofit — grafo-completo-1.json, formato A3
   SVG: disegno 49 scritte, 9.0–9.0 pt · tabella 30 scritte, 9.0–9.0 pt · cartiglio 23 scritte, 5.0–34.0 pt
   DXF: disegno 49 scritte, 9.0–9.0 pt · tabella 30 scritte, 9.0–9.0 pt · cartiglio 23 scritte, 5.0–34.0 pt · caratteri ['arial.ttf', 'arialbd.ttf']
   carattere: radice 'Arial, Helvetica, sans-serif'; scritte del disegno che ne dichiarano un altro: nessuna
   scritte accanto ai pezzi: main {'tag': 10} · ora {'tag': 10} · mancano nessuna · a 8 pt nessuna · con richiamo nessuna
   DN: main 6 · ora 6 (a 8 pt 0, staccati con freccia nessuno) · mancano sulle strade principali nessuno · sacrificati sulle secondarie 0 
   rispetto a main: simboli uguali, tratte uguali · tabella 92.5x30.0 → 152.5x37.5 mm · voci della legenda 18 + 4 · riga «Øi»: si
   i DN toccano qualcosa: 0 — la cosa piu' vicina: Øi 32 da simbolo collettore-mandata a 1.21 mm
   deterministico: SVG uguale (228f2ffbd82fdd5b), DXF uguale (13cfdaa8b2403cca)
   preflight: nessun rilievo
```

**Criterio 0 — le tavole, per prime**: in testa a questo rapporto, sei più la retrofit, in PDF e in DXF.

**Criterio 1 — il corpo lo ha fissato il PO**: I-159 (9 punti, mai sotto 8), e le sue disposizioni su che
cosa si sacrifica e che cosa no, I-160 … I-162; le regole sono **D-194**, proposta, da approvare con le tavole.

**Criterio 2 — nessuna scritta sotto il minimo**: nel collaudo, «SVG» e «DXF» di ogni tavola — il disegno e la
tabella fra 8,0 e 9,0 punti, il cartiglio com'è —; e `tests/scritte/test_scritte_a_nove_punti.py`, che lo
pretende su tutte le tavole, nell'SVG e nel DXF.

**Criterio 3 — niente si tocca; sigle e DN contati contro `REL-007`**: «scritte accanto ai pezzi» (nessuna
manca), «DN» (nessuno manca sulle strade principali; i sacrificati sono tutti su strade secondarie, uno per
uno), «i DN toccano qualcosa: 0», e il preflight senza rilievi — compresi quelli sulle sigle che si toccano e
sui richiami.

**Criterio 4 — il disegno non si muove, o si dice dove**: «rispetto a main»: simboli e tratte uguali su sei
tavole; sulla tavola 2 il disegno scende di 5,0 mm tutto insieme, per la tabella più alta.

**Criterio 5 — deterministico, e la suite**: «deterministico: SVG uguale, DXF uguale», due esecuzioni
separate. La suite, sul ramo e su `main`, e le rosse nome per nome:

```
La suite gira sulla testa del codice, c1faecd: l'esito si scrive qui appena finisce.
```

## 5. Che cosa ho toccato fuori dall'elenco del perimetro, e perché

Il perimetro dice: il corpo e ciò che si impagina col testo — `graphics/`, la posa delle scritte
(`layout/labels.py`, `layout/diametri.py`, `layout/addresses.py`), il preflight che misura le scritte —, le
prove, il collaudo, i documenti di stato. In più:

- **`diametri/tratti.py`**: ogni tratto sa se corre su una strada principale (I-161);
- **`validation/geometry.py`**: la validazione misura la sigla al suo corpo;
- **`docs/standard/GRAPHIC_STANDARD.md`**: il corpo nuovo.

**Non toccati**: posa dei simboli e instradamento, le regole, la libreria dei simboli e il catalogo, il
cartiglio, il PDF.

## 6. Le domande al PO

1. **Le tavole vanno bene?** Il corpo, le sigle a 8 dove servono, i DN staccati e quelli sacrificati, la
   legenda, la tabella (§1).
2. **Il richiamo** (§3.1): la spalla come nel tuo esempio, il tratto obliquo a 45 gradi. Va bene così?
