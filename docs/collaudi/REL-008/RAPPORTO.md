# REL-008 — le scritte della tavola a 9 punti: rapporto

**Pacchetto:** `REL-008` (`ACTIVE_WORK_PACKAGE.md`; I-159) · **Ramo:** `claude/pack-attivo-rel-007-0uotnp`,
ripartito da `main` · **Base:** `main` a `7f2bee8` (PR #64, `REL-007`) · **Avviato dal PO:** il 29 settembre
2026 · **Le regole:** **D-194**, dalle disposizioni del PO I-159 … I-163

> **Esito — 29 settembre 2026: approvato dal PO** (I-164): «le tavole vanno bene», il richiamo va bene, le
> distanze vanno bene; la legenda resta com'è (I-165). D-194 è approvata per intero. Prima di fondere, alla
> domanda del PO su dove stanno nella skill il motore che tagga e i suoi controlli (I-166), le quattro regole
> delle distanze hanno avuto il loro rilievo nel preflight: §3.7.

> **Le tavole, per prime**
>
> **Le sei tavole approvate e la variante retrofit, con le scritte a 9 punti**, in PDF e in DXF, in
> [`tavole/`](tavole/): gli stessi grafi, piani e dati di prova di `REL-007`. **Da guardare accanto a quelle di
> `REL-007`** ([`../REL-007/tavole/`](../REL-007/tavole/)), che hanno le scritte a 5 punti.

| tavola | formato | PDF | DXF | che cosa mostra |
|---|---|---|---|---|
| 1 — due pompe di calore in parallelo, accumulo combinato | A3 | [`tavola-1.pdf`](tavole/tavola-1.pdf) | [`tavola-1.dxf`](tavole/tavola-1.dxf) | un DN staccato con freccia (accumulo → radiatori), staccato anche da RAD-01; due DN sacrificati sulle acque fredde |
| 2 — pompa di calore con deviazione fra climatizzazione e ACS | A3 | [`tavola-2.pdf`](tavole/tavola-2.pdf) | [`tavola-2.dxf`](tavole/tavola-2.dxf) | **il disegno scende di 5 mm**, tutto insieme, per la tabella più alta |
| 3 — pompa di calore diretta su pavimento radiante | A3 | [`tavola-3.pdf`](tavole/tavola-3.pdf) | [`tavola-3.dxf`](tavole/tavola-3.dxf) | tutto entra accanto al pezzo; «4 kW» di PAV-02 a destra del pannello, non sopra «PAV-01» |
| 4 — ibrido pompa di calore e caldaia | A3 | [`tavola-4.pdf`](tavole/tavola-4.pdf) | [`tavola-4.dxf`](tavole/tavola-4.dxf) | due DN staccati con freccia (radiatori, acqua calda dello scambiatore); uno sacrificato; «0,7 m³/h» di ACS-01 accanto al suo confine, non sopra «AF-01» |
| 5 — tre pompe di calore in cascata, tre secondari e ACS | A2 | [`tavola-5.pdf`](tavole/tavola-5.pdf) | [`tavola-5.dxf`](tavole/tavola-5.dxf) | **CIR-02 a 8 punti** accanto al circolatore; tre DN sacrificati sulle strade secondarie |
| 6 — centrale ibrida con PdC di alta potenza, caldaia modulare e solare | A2 | [`tavola-6.pdf`](tavole/tavola-6.pdf) | [`tavola-6.dxf`](tavole/tavola-6.dxf) | **CIR-03 a 8 punti**; **CIR-01 sotto la sua pompa**, lontana dalla valvola; un DN staccato con freccia; uno sacrificato |
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
8. **Le distanze fra le scritte** (§3.5): fra scritte di pezzi diversi un corpo lungo la riga e mezzo fra le
   righe; una sigla non sta più vicina a un altro pezzo che al suo; il DN staccato sta a un corpo da tutto, e
   la sua freccia non cade sulla freccia del flusso. Le ho aggiunte dopo aver guardato le tavole: sono
   tarature mie, da giudicare.

## 2. Che cosa c'è

- **Il corpo in un posto solo**, `graphics/standard.py`: `CORPO_DELLE_SCRITTE_PT = 9`, `CORPO_MINIMO_PT = 8`,
  `FAMIGLIA_DELLE_SCRITTE`. A4, A3 e A2 lo condividono.
- **La legenda**, `layout/legend.py`: `a_capo` con le larghezze di Arial, bilanciato; il passo di una voce di
  tre righe; SVG e DXF vanno a capo con la stessa funzione.
- **La tabella**, `graphics/tabella.py`: `altezza_della_riga_mm`, dal corpo.
- **Le sigle**, `layout/labels.py`: la larghezza con le metriche di Arial; il ripiego a 8 punti; il corpo
  della sigla nella geometria (`PlacedLabel.corpo_mm`), letto da SVG, DXF, preflight, DN e velo della verifica.
- **I DN**, `layout/diametri.py` e `diametri/tratti.py`: il ripiego a 8 punti, lo spazio dai capi di 1,0 mm, la
  strada principale o secondaria di ogni tratto, l'etichetta staccata con freccia (`labels.richiamo_verso`).
- **Il richiamo con freccia e spalla** (I-162, I-163): la geometria in `layout/geometry.py` (`Richiamo`: punta,
  gomito, spalla), costruita da `layout/labels.py` per le sigle e per i DN; SVG e DXF lo disegnano uguale, la
  freccia piena come `SOLID` nel DXF.
- **Il preflight**: `TABLE_EQUIPMENT_TAG_OMITTED`, bloccante (I-160); `DIAMETER_TAG_MISSING` solo sulle strade
  principali (I-161); i controlli sui richiami — incroci, 45 gradi — anche per i DN staccati.
- **Le distanze fra le scritte** (§3.5): `layout/labels.py` — `riquadro_di_rispetto` (`STACCO_SULLA_RIGA_EM`,
  `STACCO_FRA_LE_RIGHE_EM`), che vale per sigle, dati e DN, e `vicina_al_suo`; `layout/diametri.py` —
  `FRANCO_DELLA_STACCATA_EM` e le frecce del flusso, lette dove le disegnano SVG e DXF.
- **Il rilievo delle distanze** (§3.7): `validation/preflight.py`, `text_spacing`, fra le misure dichiarate.
- **Le prove**: `tests/scritte/` (54), le prove del preflight per ciascun codice nuovo, e le prove dei diametri,
  delle etichette e del DXF alla regola nuova.

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

### 3.5 Quattro difetti che i numeri davano per buoni

Guardando le tavole prima di mandartele ho trovato quattro cose sbagliate che il collaudo non vedeva — niente
si toccava, il preflight era pulito —, tutte figlie del corpo più grande:

1. **Il DN staccato si incollava alla sigla accanto**: sulle tavole 1 e 4 «Øi 32» finiva sulla riga di
   «RAD-01», a 1,66 mm, e si leggeva «Øi 32 RAD-01». Ora la scritta staccata sta **a un corpo** (3,2 mm) da
   scritte, simboli e linee degli altri tratti: sulle tavole la cosa più vicina è a 3,85–4,21 mm.
2. **La freccia del richiamo cadeva sulla freccia del flusso**: la punta partiva dal centro del rettilineo,
   che è proprio dove sta la freccia di verso: tutte e quattro le punte ci cadevano sopra. Ora ne stanno
   fuori, a 1,25 mm.
3. **Scritte di pezzi diversi che si leggevano come una sola**: «CIR-01» e il DN «Øi 40» sulla stessa riga a
   1,15 mm (tavola 6); «4 kW» di PAV-02 sopra «PAV-01» (tavola 3) e «0,7 m³/h» di ACS-01 sopra «AF-01»
   (tavola 4), a 0,65 mm, come due righe dello stesso blocco. Su `main`, a 5 punti, non succedeva. Ora fra
   scritte di pezzi diversi c'è **un corpo lungo la riga e mezzo corpo fra le righe**.
4. **CIR-01 toccava la valvola** (tavola 6): centrata sopra la sua pompa, a 9 punti arrivava sul riquadro
   della valvola del ramo accanto, a 0,00 mm, e si leggeva come sua. Ora una sigla o un dato **non sta più
   vicino a un altro pezzo che al suo**: CIR-01 è scesa sotto la pompa.

Rispetto alle tavole di prima di queste correzioni si sono spostate **tre scritte accanto ai pezzi** («4 kW»,
«0,7 m³/h», «CIR-01») **e cinque DN**, quattro dei quali staccati; nessuna scritta è sparita o comparsa, simboli
e linee sono identici. Sono tarature della sessione, scritte in **D-194, punto 9**. Fuori dalle sette
tavole, sulla prova-1 della suite, la regola della sigla più vicina al suo pezzo manda AF-02 sul richiamo
(§4, criterio 5): accanto, in seconda fila, si leggeva come la sigla del defangatore.

### 3.6 Nella legenda, due voci di due righe di fila si leggono come una

A 9 punti molti nomi vanno su due righe, e il passo di una voce è rimasto quello di sempre, **7,5 mm** («tre
passi di griglia», `legend.ROW_HEIGHT_MM`). Fra due voci di due righe di fila restano 1,7 mm di bianco, quasi
quanto fra le due righe della stessa voce (1,5): nei fluidi otto righe di fila fanno un blocco solo, e le voci
si distinguono dal campione accanto e dalla maiuscola. **Non l'ho cambiato**, perché il passo è una convenzione:
la proposta è **mezzo passo di griglia in più (1,25 mm) per le voci di due righe**, che porta il bianco fra
due voci a 2,9 mm. Provato in memoria: la legenda entra ancora su tutte le tavole, e sotto la nota «Øi» della
tavola 4, la A3 più piena, restano 8,9 mm di fascia invece di 20,2; su una A3 più piena di questa la legenda
non entrerebbe, ed è un errore che ferma la tavola.

### 3.7 Il motore che tagga e i suoi controlli sono pezzi della skill (I-166)

Il PO, approvando: «tutto quello che hai fatto taggare e verificare i tag deve essere parte della skill che
faremo. […] Non è che i controlli li fai tu in questa sessione e poi spariscono». Dove sta ciascuna cosa,
nell'architettura (`docs/ARCHITETTURA-DEL-PIANO.md`, §1 e §3):

| che cosa | dove | pezzo della skill |
|---|---|---|
| **la posa delle scritte** — sigle e dati accanto al pezzo, 9 poi 8 punti, il richiamo; il DN in linea, staccato o sacrificato; le distanze | `layout/labels.py`, `layout/diametri.py`, chiamati da `piano/esecutore.py` | **4, Eseguire** — deterministico |
| **i controlli sulla tavola finita** — la sigla in tabella omessa (bloccante), il DN mancante su una strada principale, i richiami che incrociano o non sono a 45 gradi, e ora le distanze | `validation/preflight.py` | l'uscita del **4**, e la metà deterministica del **5**, Rivedere: gli avvisi entrano nel punteggio del revisore |
| **le prove** | `tests/` | sorvegliano il codice, non le tavole del progettista |
| **il collaudo** | `docs/collaudi/REL-008/collaudo.py` | **nessuno**: è lo strumento della sessione per mostrare le tavole al PO |

**Il buco, trovato rispondendo.** Le quattro regole di §3.5 vivevano nella posa, nelle prove e nel collaudo, ma
**non nel preflight**: su un impianto nuovo la skill le avrebbe rispettate senza poterlo dire. È l'avvertenza di
§7 dell'architettura — «una regola che vive solo nella posa del motore è una regola che il piano può rompere:
scrivi il rilievo, non solo il vincolo» (D-158). Adesso ce l'hanno: `text_spacing`, con `TEXTS_READ_AS_ONE`,
`TAG_NEARER_ANOTHER_PIECE`, `DETACHED_DIAMETER_CROWDED` e `LEADER_ON_A_FLOW_ARROW`, avvisi come ogni rilievo sui
testi. Sulle geometrie di prima delle correzioni trova **i quattordici difetti** (tavole 1, 3, 4 e 6); sulle
sette tavole approvate **nessuno**, e le tavole non cambiano. Per `REL-001` resta la seconda metà di I-166: la
skill esegue il motore e il preflight su ogni tavola e ne consegna i rilievi.

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
   scritte di pezzi diversi a meno di un corpo lungo la riga e mezzo fra le righe: 0 
   sigle piu' vicine a un altro pezzo che al loro: 0 
   staccate (un corpo = 3.17 mm): Øi 32: la cosa piu' vicina tag RAD-01 a 4.21 mm, la punta a 1.25 mm dalla freccia di verso piu' vicina
   deterministico: SVG uguale (a65bef4bdfb934b8), DXF uguale (5e690034b07b1664)
   preflight: nessun rilievo

== tavola-2 — grafo-completo-2.json, formato A3
   SVG: disegno 57 scritte, 9.0–9.0 pt · tabella 30 scritte, 9.0–9.0 pt · cartiglio 23 scritte, 5.0–34.0 pt
   DXF: disegno 57 scritte, 9.0–9.0 pt · tabella 30 scritte, 9.0–9.0 pt · cartiglio 23 scritte, 5.0–34.0 pt · caratteri ['arial.ttf', 'arialbd.ttf']
   carattere: radice 'Arial, Helvetica, sans-serif'; scritte del disegno che ne dichiarano un altro: nessuna
   scritte accanto ai pezzi: main {'tag': 11} · ora {'tag': 11} · mancano nessuna · a 8 pt nessuna · con richiamo nessuna
   DN: main 7 · ora 7 (a 8 pt 0, staccati con freccia nessuno) · mancano sulle strade principali nessuno · sacrificati sulle secondarie 0 
   rispetto a main: simboli DIVERSI, tratte DIVERSI · tabella 92.5x30.0 → 152.5x37.5 mm · voci della legenda 21 + 4 · riga «Øi»: si
   i DN toccano qualcosa: 0 — la cosa piu' vicina: Øi 25 da linea p4-a a 1.21 mm
   scritte di pezzi diversi a meno di un corpo lungo la riga e mezzo fra le righe: 0 
   sigle piu' vicine a un altro pezzo che al loro: 0 
   staccate: nessuna
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
   scritte di pezzi diversi a meno di un corpo lungo la riga e mezzo fra le righe: 0 
   sigle piu' vicine a un altro pezzo che al loro: 0 
   staccate: nessuna
   deterministico: SVG uguale (8ff2a1fa4dd1140a), DXF uguale (552dd056ebf36013)
   preflight: nessun rilievo

== tavola-4 — grafo-completo-4.json, formato A3
   SVG: disegno 66 scritte, 9.0–9.0 pt · tabella 35 scritte, 9.0–9.0 pt · cartiglio 23 scritte, 5.0–34.0 pt
   DXF: disegno 66 scritte, 9.0–9.0 pt · tabella 35 scritte, 9.0–9.0 pt · cartiglio 23 scritte, 5.0–34.0 pt · caratteri ['arial.ttf', 'arialbd.ttf']
   carattere: radice 'Arial, Helvetica, sans-serif'; scritte del disegno che ne dichiarano un altro: nessuna
   scritte accanto ai pezzi: main {'tag': 14, 'data': 2} · ora {'tag': 14, 'data': 2} · mancano nessuna · a 8 pt nessuna · con richiamo nessuna
   DN: main 12 · ora 11 (a 8 pt 0, staccati con freccia ['Øi 20', 'Øi 32']) · mancano sulle strade principali nessuno · sacrificati sulle secondarie 1 ['Øi 20 acquedotto→scambiatore']
   rispetto a main: simboli uguali, tratte uguali · tabella 92.5x35.0 → 152.5x43.8 mm · voci della legenda 22 + 4 · riga «Øi»: si
   i DN toccano qualcosa: 0 — la cosa piu' vicina: Øi 40 da simbolo tee-expansion-connection-collettore-ritorno-a a 1.21 mm
   scritte di pezzi diversi a meno di un corpo lungo la riga e mezzo fra le righe: 0 
   sigle piu' vicine a un altro pezzo che al loro: 0 
   staccate (un corpo = 3.17 mm): Øi 32: la cosa piu' vicina tag RAD-01 a 4.21 mm, la punta a 1.25 mm dalla freccia di verso piu' vicina · Øi 20: la cosa piu' vicina data 0,7 m³/h a 3.85 mm, la punta a 1.25 mm dalla freccia di verso piu' vicina
   deterministico: SVG uguale (36a6b3a3cd018d5f), DXF uguale (2c9f5e4bdb65634d)
   preflight: nessun rilievo

== tavola-5 — grafo-completo-5.json, formato A2
   SVG: disegno 98 scritte, 8.0–9.0 pt · tabella 60 scritte, 9.0–9.0 pt · cartiglio 23 scritte, 5.0–34.0 pt
   DXF: disegno 98 scritte, 8.0–9.0 pt · tabella 60 scritte, 9.0–9.0 pt · cartiglio 23 scritte, 5.0–34.0 pt · caratteri ['arial.ttf', 'arialbd.ttf']
   carattere: radice 'Arial, Helvetica, sans-serif'; scritte del disegno che ne dichiarano un altro: nessuna
   scritte accanto ai pezzi: main {'tag': 22, 'data': 2} · ora {'tag': 22, 'data': 2} · mancano nessuna · a 8 pt ['CIR-02'] · con richiamo nessuna
   DN: main 29 · ora 26 (a 8 pt 0, staccati con freccia nessuno) · mancano sulle strade principali nessuno · sacrificati sulle secondarie 3 ['Øi 25 inlet-mixing-valve-thermostatic-bollitore-dhw-out→mixing-valve-thermostatic-bollitore-dhw-out', 'Øi 40 ritorno-radiante→miscelatrice-radiante', 'Øi 25 acquedotto→bollitore']
   rispetto a main: simboli uguali, tratte uguali · tabella 95.0x60.0 → 155.0x75.0 mm · voci della legenda 26 + 5 · riga «Øi»: si
   i DN toccano qualcosa: 0 — la cosa piu' vicina: Øi 40 da simbolo tee-thermometer-pdc-1-water-supply a 1.21 mm
   scritte di pezzi diversi a meno di un corpo lungo la riga e mezzo fra le righe: 0 
   sigle piu' vicine a un altro pezzo che al loro: 0 
   staccate: nessuna
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
   scritte di pezzi diversi a meno di un corpo lungo la riga e mezzo fra le righe: 0 
   sigle piu' vicine a un altro pezzo che al loro: 0 
   staccate (un corpo = 3.17 mm): Øi 40: la cosa piu' vicina simbolo radiatori a 3.89 mm, la punta a 1.25 mm dalla freccia di verso piu' vicina
   deterministico: SVG uguale (415afb20944d96bd), DXF uguale (8aa3fc741a677234)
   preflight: nessun rilievo

== tavola-1-retrofit — grafo-completo-1.json, formato A3
   SVG: disegno 49 scritte, 9.0–9.0 pt · tabella 30 scritte, 9.0–9.0 pt · cartiglio 23 scritte, 5.0–34.0 pt
   DXF: disegno 49 scritte, 9.0–9.0 pt · tabella 30 scritte, 9.0–9.0 pt · cartiglio 23 scritte, 5.0–34.0 pt · caratteri ['arial.ttf', 'arialbd.ttf']
   carattere: radice 'Arial, Helvetica, sans-serif'; scritte del disegno che ne dichiarano un altro: nessuna
   scritte accanto ai pezzi: main {'tag': 10} · ora {'tag': 10} · mancano nessuna · a 8 pt nessuna · con richiamo nessuna
   DN: main 6 · ora 6 (a 8 pt 0, staccati con freccia nessuno) · mancano sulle strade principali nessuno · sacrificati sulle secondarie 0 
   rispetto a main: simboli uguali, tratte uguali · tabella 92.5x30.0 → 152.5x37.5 mm · voci della legenda 18 + 4 · riga «Øi»: si
   i DN toccano qualcosa: 0 — la cosa piu' vicina: Øi 32 da simbolo collettore-mandata a 1.21 mm
   scritte di pezzi diversi a meno di un corpo lungo la riga e mezzo fra le righe: 0 
   sigle piu' vicine a un altro pezzo che al loro: 0 
   staccate: nessuna
   deterministico: SVG uguale (228f2ffbd82fdd5b), DXF uguale (13cfdaa8b2403cca)
   preflight: nessun rilievo
```

**Criterio 0 — le tavole, per prime**: in testa a questo rapporto, sei più la retrofit, in PDF e in DXF.

**Criterio 1 — il corpo lo ha fissato il PO**: I-159 (9 punti, mai sotto 8), e le sue disposizioni su che
cosa si sacrifica e che cosa no, I-160 … I-162, e sulla forma del richiamo, I-163; le regole sono **D-194**,
proposta, da approvare con le tavole.

**Criterio 2 — nessuna scritta sotto il minimo**: nel collaudo, «SVG» e «DXF» di ogni tavola — il disegno e la
tabella fra 8,0 e 9,0 punti, il cartiglio com'è —; e `tests/scritte/test_scritte_a_nove_punti.py`, che lo
pretende su tutte le tavole, nell'SVG e nel DXF.

**Criterio 3 — niente si tocca; sigle e DN contati contro `REL-007`**: «scritte accanto ai pezzi» (nessuna
manca), «DN» (nessuno manca sulle strade principali; i sacrificati sono tutti su strade secondarie, uno per
uno), «i DN toccano qualcosa: 0», e il preflight senza rilievi — compresi quelli sulle sigle che si toccano e
sui richiami. Per le distanze di §3.5: «scritte di pezzi diversi a meno di un corpo lungo la riga e mezzo fra
le righe: 0» e «sigle più vicine a un altro pezzo che al loro: 0» su tutte (prima delle correzioni: cinque
coppie sulle tavole 1, 3, 4 e 6, e CIR-01); «staccate»: la cosa più vicina a 3,85 mm o più, la punta a 1,25
mm dalla freccia del flusso. In `tests/scritte/` le prove che lo pretendono su tutte le tavole: sul codice di
prima falliscono in otto casi, i quattro difetti.

**Criterio 4 — il disegno non si muove, o si dice dove**: «rispetto a main»: simboli e tratte uguali su sei
tavole; sulla tavola 2 il disegno scende di 5,0 mm tutto insieme, per la tabella più alta.

**Criterio 5 — deterministico, e la suite**: «deterministico: SVG uguale, DXF uguale», due esecuzioni
separate. La suite, sul ramo e su `main`, e le rosse nome per nome:

```
main : 46 failed, 1932 passed, 24 skipped, 12 xfailed in 808.58s (0:13:28)
ramo : 47 failed, 1979 passed, 24 skipped, 12 xfailed in 883.96s (0:14:43)
rosse main 46 ramo 47 errori 0 0
nuove nel ramo: ['tests/layout/test_etichette_postume.py::test_la_tavola_di_consegna_porta_solo_le_sigle_delle_macchine']
guarite nel ramo: []
uguali nome per nome: False
skip main 24 ramo 24 nuovi: []
xfail main 12 ramo 12 nuovi: []
```

Sul codice di `cbc9af7` una rossa nuova, `test_la_tavola_di_consegna_porta_solo_le_sigle_delle_macchine`: è la
prova, non la tavola. Sulla tavola della prova-1 composta su un foglio qualunque — non una delle sette — la
sigla **AF-02** in seconda fila stava a 5,18 mm dal suo confine e a 2,68 mm dal defangatore, e per la regola
di §3.5 si leggerebbe come sua: va sul richiamo, l'ultima spiaggia. La prova riconosceva il richiamo solo nella
forma di prima (`leader_from`); ora legge `richiamo`, e controlla che sia a 45 gradi e non attraversi niente:
il modulo passa, 15 su 15. La suite sulla testa finale, `5c0cee8` — le stesse 46 rosse di `main`, nome per
nome:

```
main : 46 failed, 1932 passed, 24 skipped, 12 xfailed in 808.58s (0:13:28)
ramo : 46 failed, 1980 passed, 24 skipped, 12 xfailed in 866.31s (0:14:26)
rosse main 46 ramo 46 errori 0 0
nuove nel ramo: []
guarite nel ramo: []
uguali nome per nome: True
skip main 24 ramo 24 nuovi: []
xfail main 12 ramo 12 nuovi: []
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
3. **Le distanze fra le scritte** (§3.5): un corpo lungo la riga, mezzo fra le righe, la sigla più vicina al
   suo pezzo che agli altri. Vanno bene, o le vuoi più larghe o più strette?
4. **La legenda** (§3.6): le voci di due righe con 1,25 mm in più di passo, o com'è?

**Le risposte del PO, il 29 settembre** (I-164, I-165): «1. le tavole vanno bene. 2. il riciamo va bene 3. le
distanze vanno bene. 4. lascia cosi' va bene come sta. apri PR e fondi.»
