# REL-007 — i diametri delle tubazioni: rapporto

**Pacchetto:** `REL-007` (`ACTIVE_WORK_PACKAGE.md`; I-142, I-143, I-145, D-191) · **Ramo:**
`claude/pack-attivo-rel-007-0uotnp` · **Base:** `main` a `2616a92` (PR #63) · **Avviato dal PO:** il 28
settembre 2026, con i chiarimenti I-150 … I-153 · **Le basi del calcolo:** **D-193**, dalle risposte del PO
I-154 … I-157

> **Le tavole, per prime**
>
> **Le sei tavole approvate, con i diametri**, in PDF e in DXF, in [`tavole/`](tavole/): i cinque impianti
> di `DRAW-018` (tavole 1–5) e l'impianto 6 di `REL-003` (tavola 6), rieseguiti dai **loro** grafi e piani,
> col cartiglio e la tabella dei dati di prova di `REL-002` e `REL-006`. **E una settima**: l'impianto 1
> **in retrofit** — la centrale si progetta, la distribuzione dagli accumuli in poi è esistente (I-145) —,
> con il DN sul solo circuito primario. Accanto ai DXF c'è il logo, che il DXF collega.
>
> **I dati del calcolo sono di prova, e inventati** ([`dati-di-prova.json`](dati-di-prova.json)): i salti
> termici dei generatori, le potenze delle zone dell'impianto 3, le portate di progetto del sanitario. Le
> potenze dei generatori e le portate dei circolatori sono quelle della tabella di `REL-006`. **Il sanitario
> delle tavole 2 e 3 resta senza dati apposta**: lì il DN non compare.
>
> **Il foglio dei calcoli** — per ogni tratto i dati usati, la potenza, la portata, il DN, la velocità e la
> massima del suo diametro — è [`foglio-dei-calcoli.md`](foglio-dei-calcoli.md).

| tavola | formato | PDF | DXF | che cosa mostra |
|---|---|---|---|---|
| 1 — due pompe di calore in parallelo, accumulo combinato | A3 | [`tavola-1.pdf`](tavole/tavola-1.pdf) | [`tavola-1.dxf`](tavole/tavola-1.dxf) | **un tag per ramo fino al raccordo e uno dopo** (I-153): Øi 32 sulle due pompe di calore, Øi 40 dopo il raccordo; il sanitario dalla portata delle utenze |
| 2 — pompa di calore con deviazione fra climatizzazione e ACS | A3 | [`tavola-2.pdf`](tavole/tavola-2.pdf) | [`tavola-2.dxf`](tavole/tavola-2.dxf) | **la deviatrice non spezza il tratto** (I-143): un tag dalla pompa di calore al volano, uno sul ramo del bollitore; sanitario senza dati, senza DN |
| 3 — pompa di calore diretta su pavimento radiante | A3 | [`tavola-3.pdf`](tavole/tavola-3.pdf) | [`tavola-3.dxf`](tavole/tavola-3.dxf) | le due zone dalla loro potenza: Øi 20 e Øi 15 |
| 4 — ibrido pompa di calore e caldaia | A3 | [`tavola-4.pdf`](tavole/tavola-4.pdf) | [`tavola-4.dxf`](tavole/tavola-4.dxf) | deviatrice e commutatrice **provate in ogni posizione**: la caldaia porta Øi 25 da qualunque parte vada |
| 5 — tre pompe di calore in cascata, tre secondari e ACS | A2 | [`tavola-5.pdf`](tavole/tavola-5.pdf) | [`tavola-5.dxf`](tavole/tavola-5.dxf) | **Øi 40 → Øi 50 → Øi 65** ai due raccordi della cascata; la miscelatrice non spezza il tratto del radiante; il ricircolo Øi 20; sei tag verticali |
| 6 — centrale ibrida con PdC di alta potenza, caldaia modulare e solare | A2 | [`tavola-6.pdf`](tavole/tavola-6.pdf) | [`tavola-6.dxf`](tavole/tavola-6.dxf) | caldaia Øi 50, pompa di calore Øi 65, tratto comune Øi 80; **il solare dalla portata del circolatore**, Øi 20 all'andata e al ritorno |
| 1 — retrofit | A3 | [`tavola-1-retrofit.pdf`](tavole/tavola-1-retrofit.pdf) | [`tavola-1-retrofit.dxf`](tavole/tavola-1-retrofit.dxf) | **la distribuzione esistente senza DN**: solo i sei tratti del primario; secondario e sanitaria sono esistenti, l'acqua fredda non è chiesta |

## 1. Che cosa guardare sulle tavole

Il PO ha fissato il metodo e la forma (D-193, dalle sue risposte): il DN come diametro interno netto, la
velocità massima che cresce col diametro, il DN standard subito più grande, «Øi 32», il tag in linea con la
tubazione — sopra la mandata, sotto il ritorno, sui verticali dal basso verso l'alto —, un tag per tratto
anche attraverso valvole e tre vie, uno per ramo fino al raccordo e uno dopo, il sanitario e il solare dalla
portata. **Il resto lo propone la sessione, ed è in D-193 come proposta**: si giudica guardando le tavole.

1. **La scritta.** «Øi 32» in Arial alto 1,8 mm come le sigle, nero, a 1,25 mm dall'asse della linea — un
   millimetro dal suo bordo. **Una riga della legenda la spiega**, sotto i fluidi: «Øi — diametro interno
   netto minimo in mm, materiale a scelta», su due righe perché la fascia è larga 50 mm.
2. **Il lato.** Sui verticali la mandata prova prima la destra, il ritorno la sinistra. **Mai fra le due
   corsie di una coppia** — la mandata e il suo ritorno affiancati: una scritta in mezzo non dice di quale
   delle due è —, finché c'è un altro posto: sulle coppie verticali della tavola 5 il tag sta sui due lati
   esterni. **Un caso solo in cui non c'è**: sulla tavola 3, la mandata della zona notte ha sopra il
   collettore, e il tag sta sotto la linea, addosso a lei, fra le due corsie.
3. **Dove lungo la linea.** Sul rettilineo orizzontale più lungo del tratto, al centro; poi a mezzo passo per
   volta verso i capi; poi sui verticali. Mai sopra un simbolo, una sigla, un'altra linea o la tabella.
4. **Quali tratti.** Ogni linea che porta acqua: dai generatori agli accumuli, agli scambiatori e ai
   collettori, e da lì alle utenze; **mai i rami di servizio** (sicurezze, vasi, riempimento, strumenti,
   scarichi). Il tratto attraversa valvole, filtri, circolatori, tre vie e i raccordi da cui pende un
   servizio, e **si divide ai raccordi che uniscono o dividono due linee** — anche dove la portata non
   cambia: è §3.6. Perché «ogni linea che porta acqua» e non «le autostrade del motore» è in §3.1.
5. **La miscelatrice.** Il bipasso della miscelatrice del radiante (tavola 5) e l'acqua fredda delle
   miscelatrici termostatiche (tavole 1, 5, 6) portano **la portata piena**: è la posizione estrema della
   valvola, quando prende tutto da un ingresso solo.
6. **I dati del progettista accanto ai pezzi.** Le portate di progetto accanto all'acquedotto e alle
   utenze sanitarie, le potenze accanto alle zone della tavola 3: **non sono di `REL-007`**, la tavola ha
   sempre scritto così i dati che il progettista dà per un pezzo fuori dalla tabella (D-052). Si vedono
   adesso perché i dati di prova li danno.
7. **Nel DXF** i tag sono testi sul layer `M-ANNO-DIAM`, «Diametri delle tubazioni», girati di 90 gradi
   sui verticali.

## 2. Che cosa c'è

- **Il calcolatore**, `src/disegnatore_mep/diametri/calcolatore.py`: dalla potenza e dal salto termico la
  portata, dalla portata il DN più piccolo della serie in cui la velocità non supera la sua massima. Le
  costanti e la tabella sono quelle di D-193, con le fonti (SRC-048 … SRC-052).
- **La portata di ogni tratto**, `diametri/portate.py`: dai soli dati del progettista — generatori e utenze
  (portata, oppure potenza e salto termico per l'acqua di riscaldamento e refrigerata), circolatori, confini
  sanitari —, e poi **per conservazione**, con il verso che il catalogo dichiara per ogni attacco: un
  raccordo somma o divide, un collettore di zona ripartisce, generatori, utenze, serpentini e il primario
  degli scambiatori si attraversano, il volume di un accumulo no. **Le tre vie si provano in ogni
  posizione**, e ogni tratto prende la portata più grande delle posizioni che i dati reggono. Dove i dati
  non bastano, il tratto resta senza portata.
- **Il tratto che porta un'etichetta sola**, `diametri/tratti.py`, e **il foglio dei calcoli**,
  `diametri/foglio.py`.
- **La posa del tag**, `layout/diametri.py`, chiamata dall'esecutore del piano dopo le sigle; la geometria
  la porta la tavola (`SheetGeometry.diametri`, `note_della_legenda`, facoltative: una tavola senza DN si
  scrive come prima, byte per byte). SVG e DXF la disegnano dalla stessa ancora.
- **Il grafo**: `diametri: {"reti": [...]}`, la richiesta del progettista; `esistente: true` su una rete; il
  salto termico `delta_t_k` fra i dati con un nome fisso. Tutti additivi: i grafi agli atti restano identici
  byte per byte. Lo schema JSON è rigenerato.
- **Il preflight**: `DIAMETER_TAG_MISSING` (avviso: un tratto col DN che non ha trovato posto),
  `DIAMETER_TAG_REPEATED` e `DIAMETER_TAG_WITHOUT_RUN` (bloccanti: difetti del disegnatore).
- **«Capire»**, `skill/capire/ISTRUZIONI.md` §3, §4.7, §9: scrive la richiesta solo se il progettista la fa,
  sulle reti che dice; segna le reti esistenti; scrive salti termici e portate solo dal testo — «45/40 °C» è
  un salto di 5 K, uno «tipico» no —; chiede quelli che mancano in una voce sola.
- **Le prove**, `tests/diametri/`: 86; e la prova di §4.7 in `tests/skill/test_istruzioni_capire.py`, i tre
  rilievi nuovi in `tests/validation/test_preflight.py`.

## 3. Che cosa ho trovato, e va detto

### 3.1 L'«autostrada» del motore non è quella che serve al DN

Il PO ha detto «basta metterlo sui tratti principali (autostrade)» (I-153). Il motore ha già una parola
«autostrada», ma è della **posa**: la usa per tenere dritte le linee fra le macchine della spina. Letta alla
lettera per il DN, sulla tavola 3 porterebbe il DN **il ritorno** delle due zone a pavimento e **non la loro
mandata**: dal collettore di zona alla zona il motore dice «distribuzione», dalla zona al volano
«autostrada». Il DN va quindi su **ogni linea che porta acqua**, esclusi i rami di servizio: è D-193, punto
7, **proposta della sessione**. Se sulle tavole ci sono tag che il PO non vuole, si restringe da lì.

### 3.2 La skill dei computi usa 2,0 m/s

La skill dei computi PdC di Nove C dimensiona il primario a 2,0 m/s con ΔT 5 K (SRC-052); il PO ha scelto
la velocità che cresce col diametro (I-154). **Sopra gli 80 kW i due criteri danno quasi sempre lo stesso
DN; sotto, la skill dei computi ne dà uno più piccolo.** Non è di questo pacchetto: va detto a chi la cura.

### 3.3 Che cosa il calcolo non sa fare, e lo dice

- **Due utenze in parallelo sullo stesso raccordo, senza una tre vie e senza i loro dati**: la portata si
  divide in un modo che i dati non dicono, e quei tratti restano senza DN. Sulle sei tavole non succede.
- **La parte esistente si dice per rete.** Nei sei impianti le reti si separano proprio agli accumuli, dove
  il PO mette il confine del retrofit. Un impianto con una rete sola, come il 3, non può dire «esistente»
  per un pezzo di rete: se serve, è un passo in più.
- **Il sanitario dal lato dell'accumulo non si somma**: l'acqua fredda che entra nel bollitore e la calda
  che esce hanno ciascuna la sua portata di progetto — le due linee e il ricircolo non si ricavano l'una
  dall'altra. «Capire» chiede la portata di progetto per ciascuna.

### 3.4 I testi della tavola

Il tag del DN dichiara Arial, come la tabella di `REL-006`; le sigle e la legenda non dichiarano un
carattere e il browser le stampa con le grazie. È il difetto già noto dei PDF (I-122), che si chiude nel
pacchetto del PDF senza browser: sulla tavola la differenza si vede.

### 3.5 La via senza piano

`disegnatore-mep draw`, la via senza piano, non posa il DN, come non porta la tabella: è la via che D-151
ha tolto dalla decisione della posa. Con la richiesta dei diametri, il suo preflight dice
`DIAMETER_TAG_MISSING` per ogni tratto.

### 3.6 Due tag uguali sul ritorno, dove la mandata ne ha uno

Sulla mandata la deviatrice non spezza il tratto: dal generatore all'accumulo c'è un tag solo, e il ramo
del bollitore ha il suo. Sul ritorno il ramo del bollitore rientra con un raccordo, e **il raccordo spezza
il tratto** (D-193, punto 7: «il raccordo che unisce o divide due linee»): prima e dopo ci sono due tag
con lo stesso DN, a pochi centimetri l'uno dall'altro. Succede in quattro punti: sul ritorno del primario
dove rientra il bollitore, nelle tavole 2, 5 e 6, e sul ritorno del radiante della tavola 5, dove si stacca
il bipasso della miscelatrice. **Lì la portata non cambia**: la deviatrice manda tutta l'acqua da una
parte o dall'altra, la miscelatrice la prende tutta da un ingresso o dall'altro.

Se il PO vuole, **il raccordo si attraversa anche lui quando la portata sulla sua via dritta non cambia**, e
i quattro tag doppi spariscono: la tavola 2 passa da 7 tag a 6, la 5 da 29 a 27, la 6 da 20 a 19. Con più
generatori in parallelo la portata al raccordo cambia sempre, e i tag prima e dopo restano (I-153). I conti
sono dello script che ha contato i raccordi sulle sette tavole; il cambio non è fatto, perché è una
convenzione grafica e la decide il PO.

## 4. Le misure

Ogni criterio con il comando e il suo esito.

**Le tavole e le misure sul disegno** — il collaudo, dalla radice:

```
PYTHONPATH=src python3 docs/collaudi/REL-007/collaudo.py <cartella-di-lavoro>
```

```
tavole/tavola-1.pdf (420x297 mm)

== tavola-1 — grafo-completo-1.json, formato A3
   etichette 11 (1 verticali) ['Øi 25', 'Øi 32', 'Øi 40'] · tratti col DN 11: senza etichetta 0, con piu' di una 0, etichette su un tratto che non lo porta 0
   tratti d'acqua 11: col DN 11, senza DN 0 []
   toccano qualcosa: 0 — la cosa piu' vicina: Øi 25 da sigla AF-01 a 1.53 mm · dalla propria linea: 1.25–1.25 mm (stacco dichiarato 1.25)
   rispetto alla tavola senza diametri: simboli uguali, tratte uguali, sigle uguali, tabella uguali, legenda uguali · riga della legenda: si (diametro interno netto minimo in mm, / materiale a scelta)
   DXF: etichette sul layer M-ANNO-DIAM 11/11 uguali
   deterministico: SVG uguale (986e9e0e2c622f47), DXF uguale (66256594f0e5fa23)
   preflight: nessun rilievo · regole: ['SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER']
tavole/tavola-2.pdf (420x297 mm)

== tavola-2 — grafo-completo-2.json, formato A3
   etichette 7 (0 verticali) ['Øi 25'] · tratti col DN 7: senza etichetta 0, con piu' di una 0, etichette su un tratto che non lo porta 0
   tratti d'acqua 10: col DN 7, senza DN 3 ['la portata non viene dai dati del progettista']
   toccano qualcosa: 0 — la cosa piu' vicina: Øi 25 da linea p4-a a 1.60 mm · dalla propria linea: 1.25–1.25 mm (stacco dichiarato 1.25)
   rispetto alla tavola senza diametri: simboli uguali, tratte uguali, sigle uguali, tabella uguali, legenda uguali · riga della legenda: si (diametro interno netto minimo in mm, / materiale a scelta)
   DXF: etichette sul layer M-ANNO-DIAM 7/7 uguali
   deterministico: SVG uguale (3756e75aeebfa07f), DXF uguale (80d45322917e607f)
   preflight: nessun rilievo · regole: ['SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER']
tavole/tavola-3.pdf (420x297 mm)

== tavola-3 — grafo-completo-3.json, formato A3
   etichette 7 (0 verticali) ['Øi 15', 'Øi 20', 'Øi 25'] · tratti col DN 7: senza etichetta 0, con piu' di una 0, etichette su un tratto che non lo porta 0
   tratti d'acqua 10: col DN 7, senza DN 3 ['la portata non viene dai dati del progettista']
   toccano qualcosa: 0 — la cosa piu' vicina: Øi 25 da simbolo valve-isolation-volano-a a 2.85 mm · dalla propria linea: 1.25–1.25 mm (stacco dichiarato 1.25)
   rispetto alla tavola senza diametri: simboli uguali, tratte uguali, sigle uguali, tabella uguali, legenda uguali · riga della legenda: si (diametro interno netto minimo in mm, / materiale a scelta)
   DXF: etichette sul layer M-ANNO-DIAM 7/7 uguali
   deterministico: SVG uguale (97e3f6c3d01807b2), DXF uguale (92daed047cdf0827)
   preflight: nessun rilievo · regole: ['SERVICE_STUB_LONGER_THAN_ITS_MINIMUM']
tavole/tavola-4.pdf (420x297 mm)

== tavola-4 — grafo-completo-4.json, formato A3
   etichette 12 (0 verticali) ['Øi 20', 'Øi 25', 'Øi 32', 'Øi 40'] · tratti col DN 12: senza etichetta 0, con piu' di una 0, etichette su un tratto che non lo porta 0
   tratti d'acqua 12: col DN 12, senza DN 0 []
   toccano qualcosa: 0 — la cosa piu' vicina: Øi 32 da simbolo circolatore a 1.60 mm · dalla propria linea: 1.25–1.25 mm (stacco dichiarato 1.25)
   rispetto alla tavola senza diametri: simboli uguali, tratte uguali, sigle uguali, tabella uguali, legenda uguali · riga della legenda: si (diametro interno netto minimo in mm, / materiale a scelta)
   DXF: etichette sul layer M-ANNO-DIAM 12/12 uguali
   deterministico: SVG uguale (cb21c6acb98ac97f), DXF uguale (d8dd2046d4130cf5)
   preflight: nessun rilievo · regole: ['SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER', 'SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER']
tavole/tavola-5.pdf (594x420 mm)

== tavola-5 — grafo-completo-5.json, formato A2
   etichette 29 (6 verticali) ['Øi 20', 'Øi 25', 'Øi 32', 'Øi 40', 'Øi 50', 'Øi 65'] · tratti col DN 29: senza etichetta 0, con piu' di una 0, etichette su un tratto che non lo porta 0
   tratti d'acqua 29: col DN 29, senza DN 0 []
   toccano qualcosa: 0 — la cosa piu' vicina: Øi 25 da sigla AF-01 a 1.53 mm · dalla propria linea: 1.25–1.25 mm (stacco dichiarato 1.25)
   rispetto alla tavola senza diametri: simboli uguali, tratte uguali, sigle uguali, tabella uguali, legenda uguali · riga della legenda: si (diametro interno netto minimo in mm, / materiale a scelta)
   DXF: etichette sul layer M-ANNO-DIAM 29/29 uguali
   deterministico: SVG uguale (81d83bdafff225d9), DXF uguale (6ab63ae0543bf32d)
   preflight: nessun rilievo · regole: ['SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER']
tavole/tavola-6.pdf (594x420 mm)

== tavola-6 — grafo-completo-6.json, formato A2
   etichette 20 (1 verticali) ['Øi 20', 'Øi 32', 'Øi 40', 'Øi 50', 'Øi 65', 'Øi 80'] · tratti col DN 20: senza etichetta 0, con piu' di una 0, etichette su un tratto che non lo porta 0
   tratti d'acqua 20: col DN 20, senza DN 0 []
   toccano qualcosa: 0 — la cosa piu' vicina: Øi 40 da sigla CIR-01 a 1.16 mm · dalla propria linea: 1.25–1.25 mm (stacco dichiarato 1.25)
   rispetto alla tavola senza diametri: simboli uguali, tratte uguali, sigle uguali, tabella uguali, legenda uguali · riga della legenda: si (diametro interno netto minimo in mm, / materiale a scelta)
   DXF: etichette sul layer M-ANNO-DIAM 20/20 uguali
   deterministico: SVG uguale (9428b00bb1cc32d1), DXF uguale (c2dad782344cf34f)
   preflight: nessun rilievo · regole: ['HIGHWAY_IS_NOT_STRAIGHT', 'SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER', 'SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER']
tavole/tavola-1-retrofit.pdf (420x297 mm)

== tavola-1-retrofit — grafo-completo-1.json, formato A3
   etichette 6 (0 verticali) ['Øi 32', 'Øi 40'] · tratti col DN 6: senza etichetta 0, con piu' di una 0, etichette su un tratto che non lo porta 0
   tratti d'acqua 11: col DN 6, senza DN 5 ['diametri non chiesti su questa rete', 'rete esistente']
   toccano qualcosa: 0 — la cosa piu' vicina: Øi 32 da simbolo collettore-mandata a 2.85 mm · dalla propria linea: 1.25–1.25 mm (stacco dichiarato 1.25)
   rispetto alla tavola senza diametri: simboli uguali, tratte uguali, sigle uguali, tabella uguali, legenda uguali · riga della legenda: si (diametro interno netto minimo in mm, / materiale a scelta)
   DXF: etichette sul layer M-ANNO-DIAM 6/6 uguali
   deterministico: SVG uguale (991f6ac592e10eaa), DXF uguale (7e1aee8a75896323)
   preflight: nessun rilievo · regole: ['SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER']
```

I rilievi delle regole sono quelli delle stesse tavole nel rapporto di `REL-006`, uno per uno: sono della
posa, che il pacchetto non tocca, e il DN non ne aggiunge né ne toglie.

**Criterio 0 — le tavole, per prime**: in testa a questo rapporto, sei più la variante retrofit, in PDF e in
DXF, con il foglio dei calcoli.

**Criterio 1 — le basi del calcolo le ha fissate il PO**: le righe **I-150 … I-157** del registro e la
decisione **D-193**. Il PO ha scelto la velocità per diametro, «Øi», un tag su ciascuna linea, il sanitario
e il solare dalla portata; la serie EN ISO 6708, le costanti dell'acqua, la parte esistente per rete e
«quali tratti» sono proposte dette al PO, che nella risposta non le ha corrette: si giudicano sulle tavole.

```
$ grep -hE '^\| (I-15[0-7]|D-193) \|' docs/input-pm/REGISTRO.md docs/DECISION_LOG.md   # i primi 100 caratteri
| I-157 | 2026-09-28 | **Sanitarie e solare: il DN dalla portata del progettista.** Alla domanda del
| I-156 | 2026-09-28 | **Il tag su ciascuna linea: la mandata col tag sopra, il ritorno col tag sott
| I-155 | 2026-09-28 | **La scritta è «Øi 32», e la legenda la spiega.** Alla domanda della sessione
| I-154 | 2026-09-28 | **La velocità massima cresce col diametro: la tabella Caleffi.** Alla domanda
| I-153 | 2026-09-28 | **Il DN non va su tutti i tratti: sulle autostrade, una volta per autostrada 
| I-152 | 2026-09-28 | **Dove si scrive il DN: in linea con la tubazione, subito sopra o sotto; sui 
| I-151 | 2026-09-28 | **La velocità limite: 2,5 m/s, e il DN standard subito più grande — «aiutami 
| I-150 | 2026-09-28 | **Il «DN» dello studio è il diametro netto interno; il materiale resta libero
| D-193 | 2026-09-28 | Approvata — il PO, 28 settembre 2026, scegliendo fra le proposte della sessio
```

**Criterio 2 — il calcolatore è giusto**: `tests/diametri/test_calcolatore.py`, con il conto a mano nella
testa del file — per ogni DN la portata appena sotto il bordo e appena sopra, il bordo esatto, la portata
dalla potenza, il caso della pompa di calore da 15 kW portato al PO.

```
$ python -m pytest -q tests/diametri/test_calcolatore.py
35 passed in 0.06s
```

**Criterio 3 — un'etichetta per tratto**: nel collaudo «senza etichetta 0, con più di una 0, etichette su
un tratto che non lo porta 0» su tutte le tavole; le prove `test_un_etichetta_per_tratto` (le sei tavole) e
`test_valvole_e_valvole_a_tre_vie_non_spezzano_il_tratto` (deviatrice, miscelatrice, commutatrice), e il
preflight che lo misura su ogni tavola del piano.

**Criterio 4 — niente dati inventati, e solo dove il progettista lo vuole**:
`tests/diametri/test_niente_dati_inventati.py` — senza la richiesta nessun tratto porta il DN, con tutti i
dati; senza il salto termico la potenza non basta; il solare non si dimensiona con la potenza; una rete
esistente si disegna senza DN, e chiederlo lì non si può; i grafi agli atti non cambiano di un byte —; e la
tavola retrofit.

```
$ python -m pytest -v tests/diametri/test_niente_dati_inventati.py
test_senza_la_richiesta_nessun_tratto_porta_il_dn PASSED [  9%]
test_senza_salto_termico_la_potenza_non_basta PASSED [ 18%]
test_il_solare_non_si_dimensiona_con_la_potenza PASSED [ 27%]
test_una_rete_esistente_si_disegna_senza_dn PASSED [ 36%]
test_i_diametri_non_si_chiedono_su_una_rete_esistente_o_che_non_c_e PASSED [ 45%]
test_il_salto_termico_e_un_numero_positivo[5 K] PASSED [ 54%]
test_il_salto_termico_e_un_numero_positivo[0] PASSED [ 63%]
test_il_salto_termico_e_un_numero_positivo[-5] PASSED [ 72%]
test_il_salto_termico_e_un_numero_positivo[True] PASSED [ 81%]
test_i_grafi_agli_atti_non_cambiano_di_un_byte PASSED [ 90%]
test_richiesta_e_rete_esistente_si_rileggono_come_sono_scritte PASSED [100%]
============================== 11 passed in 0.15s ==============================
```

**Criterio 5 — deterministico, e la suite**: «deterministico: SVG uguale, DXF uguale» nel collaudo, due
esecuzioni separate, e `test_deterministico`. La suite, sul ramo e su `main`, e le rosse nome per nome:

```
La suite gira sulla testa del codice, 725f256: l'esito si scrive qui appena finisce.
```

## 5. Che cosa ho toccato fuori dall'elenco del perimetro, e perché

Il perimetro dice: il calcolatore, l'etichetta nel disegno — SVG e DXF — e il suo posto, le istruzioni di
«Capire», le prove, il collaudo, i documenti di stato. Per farlo ho toccato anche:

- **`model/project.py`** e **`schemas/project.schema.json`**: la richiesta dei diametri, la rete esistente
  e `delta_t_k`. Il pacchetto lo chiede al punto 1 bis — «il grafo impara a dire che una parte
  dell'impianto è esistente» —, e senza la richiesta nel grafo il criterio 4 non si può misurare;
- **`layout/geometry.py`** e **`piano/esecutore.py`**: la geometria del tag e la sua posa, dopo le sigle;
- **`validation/preflight.py`** e la sua prova dell'ordine: il rilievo che misura il criterio 3 su ogni
  tavola (D-158: ciò che la posa garantisce ha un rilievo sulla tavola finita);
- **`layout/addresses.py`**: gli indirizzi della modalità verifica (D-110) non coprono il DN, come non
  coprono la tabella (`REL-006`); una prova lo misura sugli impianti 1 e 5.

**Non toccati**: posa e instradamento, le regole, la libreria dei simboli e il catalogo, la tabella, il PDF.

## 6. Le domande al PO

1. **Le tavole vanno bene?** La scritta, il posto, quali tratti portano il tag, la riga della legenda
   (§1).
2. **Il tag su ogni linea che porta acqua**, e non sulle sole autostrade del motore (§3.1): va bene così?
3. **Il tag doppio sul ritorno** (§3.6): il raccordo dove rientra il bollitore spezza il tratto, e prima e
   dopo c'è lo stesso DN. Lo attraverso quando la portata non cambia?

## 7. I rami

Sul remoto ci sono i rami dei pacchetti passati, fusi o bocciati, e questo: la sessione ha scritto solo
su questo, e `main` è ancora alla base.

```
$ git fetch origin && git log --oneline -1 origin/main && git branch -r | wc -l
2616a92 REL-006 — la tabella delle apparecchiature in alto a sinistra: tavole approvate dal PO (I-149, D-192) (#63)
49
```
