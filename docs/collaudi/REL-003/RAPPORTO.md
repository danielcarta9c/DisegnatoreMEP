# REL-003 — i simboli nuovi: rapporto

**Pacchetto:** `REL-003` (`ACTIVE_WORK_PACKAGE.md`) · **Ramo:** `claude/missing-symbols-uuzbhb` ·
**Prima parte** su `main` con la PR #58 (SHA iniziale `130be28`) · **Seconda parte** con la PR #@@,
dopo aver portato nel ramo `main` con `REL-002` (PR #59)

> **Le tavole, per prime**
>
> 1. **La tavola di prova** — [`tavola-impianto-6.pdf`](tavola-impianto-6.pdf): una centrale che non è
>    fra i cinque impianti, con **i cinque simboli nuovi sulla stessa tavola** — pompa di calore di
>    alta potenza, caldaia modulare, collettore solare, bollitore a due serpentini, ventilconvettore
>    canalizzato. Dal testo dell'ingegnere al PDF **senza toccare niente a mano**: «Capire» ha scritto
>    il grafo, le regole l'hanno completato, un compositore in camera pulita ha scritto il piano.
>    **A2, 48 tratte, zero cedute, zero rilievi bloccanti**, col cartiglio compilato come in `REL-002`
>    (dati di prova, tavola T6). ✅ **Approvata dal PO il 26 settembre 2026** (I-136): «La tavola va
>    benissimo. Ottimo lavoro. Fondi».
> 2. **Il foglio dei simboli** — [`REL-003-simboli-nuovi.pdf`](REL-003-simboli-nuovi.pdf): ✅
>    **approvato il 25 settembre** (I-128, D-185).
>
> Accanto c'è **la seconda composizione** dello stesso grafo, di un altro compositore:
> [`impianto-6/tavola-impianto-6-seconda-composizione.pdf`](impianto-6/tavola-impianto-6-seconda-composizione.pdf)
> — stessa sostanza, il ventilconvettore girato sopra la distribuzione (§3).

## 1. Che cosa c'è

### 1.1 I cinque simboli — la prima parte, su `main`

Scritti dal generatore (`examples/graphics/build_symbols.py`) e mai a mano, ciascuno con la sua fonte
nel manifesto:

| simbolo | misura | attacchi | fonte |
|---|---|---|---|
| `heat-pump-air-water-large` — pompa di calore aria-acqua di alta potenza | 60 × 30 | mandata destra +5, ritorno destra +20 | SRC-030, SRC-031, SRC-032 |
| `gas-boiler-modular` — caldaia modulare a condensazione | 60 × 25 | mandata destra +5, ritorno destra +20 | SRC-033, SRC-009 |
| `solar-collector` — collettore solare | 40 × 25 | mandata destra +5, ritorno destra +20 | SRC-034, SRC-035 |
| `dhw-cylinder-twin-coil` — bollitore ACS a due serpentini | 25 × 55 | integrazione sinistra +7,5 e +17,5, solare sinistra +27,5 e +37,5, fredda sinistra +47,5, calda sopra, ricircolo destra +12,5, sonda destra +20 | SRC-036, SRC-037 |
| `fan-coil-ducted` — ventilconvettore canalizzato | 20 × 15 | ingresso e uscita sinistra +2,5 e +12,5 (D-167) | SRC-039, SRC-040 |

Le macchine hanno mandata e ritorno alle **quote di tutte le altre** (+5 e +20), il bollitore il
serpentino di integrazione **dove lo ha il bollitore a un serpentino**, il canalizzato le porte **dove le
hanno gli altri terminali**: nessuna convenzione in vigore è cambiata, e i 42 simboli di prima si
rigenerano identici. **UNI 9511 non ha nessuno dei cinque segni**; le forme vengono dagli schemi dei
costruttori e dei progetti pubblici, e il perché di ogni tratto sta nel rapporto della ricerca
(`docs/fonti/ricerche/reports/Simboli nuovi della prima release.md`, SRC-041). **L'unico scostamento
dalle fonti**, detto al PO prima del suo sì: nella caldaia modulare le fonti mettono i due collettori
sotto i moduli; qui la mandata corre sopra, per tenere le quote +5 e +20.

### 1.2 Il catalogo, le varianti e il fluido solare — la seconda parte

- **Diciassette voci di catalogo nuove**, dal generatore (`examples/layout/build_layout_fixtures.py`),
  mai a mano: le cinque dei simboli e **dodici accessori del circuito solare** — circolatore, ritegno,
  intercettazione, sicurezza, vaso, manometro, termometro, sfiato, carico e scarico, tre raccordi —,
  gli stessi simboli con il fluido solare, perché ogni voce dichiara il fluido dei suoi attacchi come
  già succede per l'acqua sanitaria. Il catalogo passa **da 56 a 73 voci**.
- **Il dato delle varianti** (`variant`: la voce base e le parole che la nominano) sulle tre voci che
  hanno un fratello con gli stessi mestieri e gli stessi attacchi: pompa di calore di alta potenza
  («alta potenza», «grande taglia»), caldaia modulare («modulare», «a moduli»), ventilconvettore
  canalizzato («canalizzato», «canalizzabile»). **Si sceglie solo quando il testo la nomina**, mai per
  potenza (D-188). Il registro rifiuta una variante che non sia la stessa macchina della sua base:
  mestieri o attacchi diversi, stesso simbolo, base che non c'è o che è a sua volta una variante.
- **Il circolatore a bordo** della pompa di calore grande e della caldaia modulare — per la caldaia,
  la correzione del PO: «anche loro le danno sempre con circolatore integrato» (D-188).
- **Il fluido solare** (`solar_fluid`): **magenta, andata e ritorno** (D-187), «Fluido solare» in
  legenda **su una riga sola** (§3); sulla sua rete **le regole non aggiungono niente** (D-188, punto
  3) — una condizione sola, nel punto in cui il motore delle regole decide di quali reti una regola
  parla. Il serpentino di integrazione del bollitore, che sta sulla rete di riscaldamento, riceve il
  suo corredo come prima.
- **Le istruzioni.** «Capire»: §4.1 le varianti, §4.2 il circuito solare — lo descrive il progettista
  e «Capire» lo trascrive, sul ritorno ai collettori, con le due eccezioni che servono per farlo —,
  §7 e §9. «Comporre»: §2.1, le righe dei simboli nuovi.

Tre estensioni del perimetro, **dichiarate nel pacchetto prima di eseguirle**: la condizione nel
motore delle regole, le istruzioni di «Capire» oltre la riga delle varianti, il nome del fluido in
`naming/media.json`.

## 2. Come si è lavorato

### 2.1 La prima parte

- **Le fonti prima delle forme.** Quattro agenti di ricerca in parallelo, uno per famiglia, ciascuno in
  una cartella fuori dal repository (D-152). La sessione ha aperto i ritagli delle fonti da cui vengono
  le forme e ha **riscaricato ogni fonte registrata** dall'indirizzo citato, controllando la pagina: 13
  documenti, tutti `200`, e ogni pagina citata contiene quello che le note dicono.
- **Il foglio lo ha guardato la sessione prima del PO**, a misura di stampa: due ritocchi ne sono usciti
  — le lamelle della batteria della pompa di calore grande più fitte, perché rade si leggevano come una
  scaffalatura, e i collari del canalizzato più larghi e sporgenti, perché a 1:1 non si vedevano.
- **Il repository è pubblico**: dei documenti protetti ci sono solo i ritagli dei singoli segni, e delle
  due tavole che vietano la riproduzione (Division Energia, Comune di Parma) nessun ritaglio.

### 2.2 L'impianto 6, dal testo alla tavola

La catena intera, ogni pezzo per quello che è (D-156):

1. **Il testo** — `examples/prova/input/2026-09-26-impianto-6-simboli-nuovi.txt`, scritto dalla
   sessione nello stile degli altri: centrale ibrida condominiale, pompa di calore aria-acqua di alta
   potenza da 120 kW e caldaia modulare a condensazione da 150 kW in parallelo, volume tecnico da 1000
   litri a quattro tubi, due secondari (radiatori, fan-coil canalizzati), bollitore a doppio serpentino
   da 1500 litri — il serpentino superiore dai generatori attraverso una deviatrice con priorità ACS,
   quello inferiore dal campo solare —, e il gruppo di circolazione solare descritto pezzo per pezzo.
2. **«Capire» in camera pulita, due giri** (`skill/capire/CONSEGNA.md`). Il primo
   (`capire-giro-1/`) ha trovato **due buchi nelle istruzioni**: per trascrivere il gruppo solare
   doveva usare pezzi della lista della ferramenta e appenderli all'attacco di servizio di una
   derivazione, tutt'e due vietati; e la convenzione del circolatore sulla mandata gli ha fatto
   mettere il gruppo sul tubo caldo, contro tutte le fonti (Parma, Caleffi Idraulica 32, Wolf: sul
   ritorno ai collettori). Istruzioni corrette (`0da7f78`) e **secondo giro da capo, con un agente
   nuovo** (`capire-giro-2/`): 25 componenti, 30 tubazioni, 5 reti, 16 assunzioni; le tre varianti
   scelte **perché il testo le nomina**, il bollitore a due serpentini dagli attacchi del serpentino
   solare, il gruppo sul ritorno ai collettori nell'ordine del testo. Il grafo valida:
   `disegnatore-mep validate grafo.json --catalog examples/layout/catalog --symbols assets/symbols` →
   `{"issues": []}`.
3. **Le domande all'ingegnere.** Le ha fatte «Capire», e la sessione ha risposto dal testo:
   - il ritorno del serpentino superiore confluisce in quello del volume prima della ripartizione sui
     generatori: **sì**;
   - termometri, intercettazioni, sfogo, carico e scarico del gruppo solare, che il testo non nomina:
     **no**, il gruppo è quello che il progettista descrive (D-188);
   - il circolatore dei generatori è a bordo: **sì** (D-188).
4. **Le regole** — `disegnatore-mep rules grafo.json --catalog examples/layout/catalog --symbols
   assets/symbols --rules rules/hydronic --naming naming --apply-all --out grafo-completo-6.json`:
   **43 integrazioni, 54 pezzi, nessuno sul circuito solare**. Rete per rete — un pezzo che sta su due
   reti conta per tutt'e due —: primario 33, secondario 8, acqua fredda e ACS 15, **solare 0**. Il
   grafo completo valida: `{"issues": []}`.
5. **Due compositori, ciascuno nella sua camera pulita** (`docs/collaudi/DRAW-017/prepara-camera.sh`,
   il mandato del 23 settembre), sul motore congelato a `967fc89`. Tutt'e due arrivano a zero cedute e
   zero bloccanti; i loro rapporti sono in `impianto-6/`, come li hanno scritti. Nel contenitore di
   questa sessione il `python3` di sistema non ha le dipendenze: `piano.sh` delle camere è stato
   puntato all'interprete del repository, e il motore è rimasto quello congelato.
6. **La misura è della sessione** (D-152), rieseguita sul codice finale — identica sul motore
   congelato dei compositori:

```
$ python docs/collaudi/DRAW-017/misura-tavole.py --dettaglio 6a=grafo-completo-6.json:piano-6-a.json 6b=grafo-completo-6.json:piano-6-b.json
tavola                   formato tratte cedute blocc regole avvisi piegate pieghe incroci
6a                       A2          48      0     0      3      3       9     10       3
      HIGHWAY_IS_NOT_STRAIGHT 1, SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER 2
6b                       A2          48      0     0      2      2       7      9       3
      HIGHWAY_IS_NOT_STRAIGHT 1, SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER 1
```

Per rifare le tavole: `bash docs/collaudi/REL-003/impianto-6/tavola.sh a <cartella>` (e `b` per la
seconda composizione). Aggiunge ai metadati del grafo i dati di prova del cartiglio di `REL-002` e il
numero T6, esegue il piano con `--cartiglio` e fa il PDF; rieseguito, dà la tavola agli atti identica
al pixel.

## 3. La tavola, guardata

**La tavola è quella del primo compositore (6a)**: la distribuzione è un pettine — dal volume una
colonna di mandata scende e dà un ramo a ciascun terminale, radiatore sopra e ventilconvettore
canalizzato sotto, tutti e due presi da sinistra, ognuno col suo circolatore — e il canalizzato sta
**diritto**, com'è nel foglio approvato. La seconda composizione ha una piega e un rilievo in meno,
ma prende il ventilconvettore da sopra, girato di 90° e specchiato: i numeri sono migliori, il disegno
si legge meno da disegnatore. **Si mostra la prima; se il PO preferisce la seconda, è agli atti.**

- **I cinque simboli sono sulla tavola**, tutti diritti, e **il bollitore dice il testo**: serpentino
  superiore dai generatori, inferiore dal solare, fredda in basso, ACS in alto.
- **Il circuito solare** è magenta nei due versi, e il verso lo dicono le frecce.
- **La legenda aveva due righe identiche**, «Fluido solare — andata» e «Fluido solare — ritorno»,
  stesso colore e stesso tratto: l'hanno visto tutt'e due i compositori. **Corretto** (`330f3ce`, con
  la sua prova): dove andata e ritorno si disegnano uguali la coppia si scrive una volta, «Fluido
  solare — andata e ritorno», per la stessa ragione per cui primario e secondario hanno una riga sola.
  Succede al solo fluido solare, ed è la conseguenza di D-187, non una convenzione nuova; ⚠ se il PO
  preferisce le due righe, si torna indietro con un commit.
- **L'A2 lo impone la legenda**: 26 simboli e 5 linee chiedono 245 mm, e la fascia dell'A3 ne ha 235 —
  come per l'impianto 5 (I-112, D-177 misurata). Il disegno della seconda composizione misura
  342,5 × 217,5 mm e starebbe nei 350 × 235 dell'A3; quello della prima, composto già su A2, 360 × 165.
- **Il gruppo solare è spezzato in due**, in tutt'e due le composizioni: circolatore e ritegno alla
  porta del bollitore, dove li posa il motore; sicurezza, manometro e vaso verso il collettore, perché
  accanto al bollitore, sotto il ritorno solare, corre l'acqua fredda.
- **La seconda valvola del separatore d'aria** il motore la posa all'altro capo della tratta, accanto
  alla deviatrice: dalla geometria, **72,5 mm** dal separatore (65 nella seconda composizione), contro
  i 7,5 della prima valvola. Il piano non può impedirlo; l'hanno visto tutt'e due i compositori.
- **I rilievi rimasti sono casi noti**: B11 sul serpentino solare (interasse 10 contro il 15 del
  collettore) e sul ventilconvettore (10 contro 15); `HIGHWAY_IS_NOT_STRAIGHT` sulla colonna del
  pettine, dove le L di testa e di piede sono quelle che B1 dà per imposte. Il compositore scrive che
  la tavola ha ragione e il rilievo no; la sessione, guardandola, è d'accordo.
- **Il carico automatico**: il testo lo mette «sul volume tecnico», le regole sul ritorno ai
  generatori, accanto al vaso. È la regola in vigore, e negli impianti 1–4, il cui testo dice la stessa
  frase, è così sulle tavole approvate.

## 4. Verifiche

### 4.1 La prima parte

- **Le prove della libreria e del catalogo** (`tests/graphics`, `tests/catalog`): 343 passate; il conto
  dei simboli pubblicati passa da 50 a 55, e **rieseguire il generatore riproduce la libreria
  committata**.
- **La suite**, due giri. Sul commit `247e932` una rossa nuova, trovata e corretta in `a7cb395`: la
  prova che elenca i simboli che si disegnano solo diritti non conosceva le quattro macchine nuove. Sul
  commit `a7cb395`: `46 failed, 1700 passed, 24 skipped, 12 xfailed`, **le stesse 46 rosse di `main`
  (`130be28`), nome per nome**, `skip` e `xfail` identici voce per voce.
- `ruff check src tests examples scripts` e `mypy` verdi.

### 4.2 La seconda parte

1. **Sul commit `0da7f78`** — catalogo, legenda, regole, istruzioni —, la suite intera in una copia del
   repository allo stesso commit, in due gruppi paralleli: `47 failed`. Delle 47, 46 sono quelle di
   `main` e **una era nuova**:
   `tests/graphics/test_contratti_simboli_tavola1.py::test_l_accumulo_combinato_e_il_bollitore_hanno_serpentini_diversi_e_il_puffer_nessuno`.
   Voleva che nel bollitore attraversassero la riserva i soli attacchi dell'acqua di riscaldamento, e
   il bollitore a due serpentini ha anche quello solare. Corretta in `233ece5` — attraversano i due
   serpentini, e nient'altro —, e rieseguita: `43 passed`.
2. **Sul commit `68a30f4`** — il codice finale, con `main` e il cartiglio dentro —, di nuovo intera:

```
gruppo A  tests/layout                           41 failed,  372 passed, 15 skipped,  3 xfailed   580 s
gruppo B  tutto il resto                          5 failed, 1417 passed,  9 skipped,  9 xfailed    69 s
totale                                           46 failed, 1789 passed, 24 skipped, 12 xfailed
```

   **Le 46 rosse sono le stesse di `main` (`130be28`), nome per nome**; nessuna nuova, nessuna tornata
   verde. `skip` e `xfail` **identici** voce per voce (36 righe). Le passate in più sono le prove della
   seconda parte e quelle del cartiglio arrivate da `main`. Dopo, il codice è cambiato solo nel
   generatore del cartiglio (punto 4), e la prova che lo rigenera è passata: `53 passed` con quelle del
   cartiglio.

3. **Le prove nuove della seconda parte**, con il loro contrario: la riga unica del solare in
   legenda **fallisce senza la correzione** e passa con; l'esclusione del solare dalle regole ha la sua
   prova controfattuale — tolta l'esclusione, qualche regola parla della rete solare.
4. `python -m ruff check src tests examples scripts` → `All checks passed!` · `python -m mypy` →
   `Success: no issues found in 79 source files`. `ruff` era rosso su `main` dopo `REL-002`, per una
   variabile mai letta nel generatore del cartiglio (`examples/cartigli/build_cartiglio.py`, F841): tolta
   in `e1c400b`, e il generatore rigenera lo stesso modello. È fuori dal perimetro, e lo si dichiara
   qui.

## 5. Criteri di accettazione

Dal pacchetto, uno per uno.

- [x] **0. Le tavole, per prime** — il foglio dei simboli è andato al PO per primo ed è approvato
  (I-128); la tavola di prova è andata al PO prima di ogni numero, ed è approvata (I-136).
- [x] **1. Le fonti** — ogni simbolo nuovo dichiara la sua fonte nel campo `source` del manifesto; le
  fonti sono nel registro (SRC-030 … SRC-041), con i ritagli dei segni nelle note della ricerca.
- [x] **2. Le forme le ha approvate il PO**, guardando il foglio: I-128, D-185.
- [x] **3. La libreria e il catalogo si rigenerano identici** —
  `python -m pytest tests/catalog/test_generated_fixtures.py tests/catalog/test_varianti.py tests/rules/test_circuito_solare.py tests/layout/test_legend.py tests/skill/test_istruzioni_capire.py tests/graphics/test_contratti_simboli_tavola1.py`
  → `97 passed`, sul commit finale; i simboli nuovi passano le prove che valgono per tutti.
- [x] **4. Capire sceglie la variante giusta** — `tests/catalog/test_varianti.py`: le varianti si
  distinguono per il dato `variant`, non per il nome; mestieri e attacchi sono quelli della base, e il
  registro lo pretende. **E l'ha fatto davvero**, in camera pulita: sull'impianto 6 «Capire» ha scelto
  le tre varianti perché il testo le nomina (§2.2).
- [x] **5. La tavola di prova** usa i cinque simboli ed esce in PDF con zero tratte cedute e zero
  rilievi bloccanti — `disegnatore-mep piano … --piano piano-6-a.json …` → `Tratte cedute: 0 · rilievi
  bloccanti: 0`; sulla tavola, dalla geometria: `heat-pump-air-water-large`, `gas-boiler-modular`,
  `solar-collector`, `dhw-cylinder-twin-coil`, `fan-coil-ducted`, tutti presenti. **Approvata dal PO**
  (I-136).
- [x] **6. La suite** — nessuna rossa nuova rispetto alle 46 di `130be28`, zero `skip` e zero `xfail`
  nuovi, `ruff` e `mypy` verdi (§4).

## 6. Quello che hanno trovato gli agenti, e non è di questo pacchetto

Le istruzioni di «Comporre» oltre al §2.1 e il motore del disegno sono fuori dal perimetro, e lo sono
anche per `REL-001`, che tocca le istruzioni solo nei percorsi. Quello che i due compositori e
«Capire» hanno trovato resta qui, **per il pacchetto che rimetterà mano alle istruzioni e al motore**
— quando il PO lo vorrà:

- **Visti da tutt'e due i compositori**: la seconda valvola di un organo che sta in mezzo alla tratta
  (il separatore d'aria) finisce all'altro capo; l'elenco «Girati dalla deduzione» che il comando stampa
  non comprende tutti i pezzi girati; §4bis dice «a partire dalla porta del pezzo che isolano», e il
  motore fa altro sulle file di valvola e circolatore; i rettilinei di §4bis sono più corti di quelli
  che servono.
- **Il pettine (B12) con i circolatori sui rami**: gli organi in linea cadono sulla verticale della
  colonna, o sulla piega; manca come si prende un terminale da sopra.
- **Un A3 troppo piccolo si annuncia male**: prima del «legend needs …» il comando dice che una tratta
  «run into an obstacle», e l'ostacolo è la fascia della legenda. Serve dire la forma dell'area utile.
- **B1 e il motore non concordano sul gradino 10/15 del terminale**: il motore lo riconosce come imposto
  solo se la catena passa per il passante del raccordo secondo le porte del grafo.
- **A1 non nomina il collettore solare** fra i generatori (il catalogo sì, e i compositori l'hanno messo
  giusto); **B11** può citare il serpentino solare fra i casi noti.
- **«Capire»**: l'ordine sui raccordi quando il raccordo è uno solo; le due uscite della deviatrice;
  l'ordine dei pezzi dentro il gruppo solare — è un contenuto impiantistico, e resta del PO —; un gruppo
  descritto solo in parte; il verso di una tubazione fra due attacchi bidirezionali; le potenze date
  solo per alcuni generatori; tre mestieri del catalogo che non stanno in nessuna delle due liste del
  §5 (`circuit_switching`, `instrument_isolation`, `air_separation`).

## 7. Difetti noti e cose trovate fuori perimetro

- **Il foglio della libreria intera non si stampa**: `disegnatore-mep symbols-sheet` rifiuta più di 32
  simboli su un A3, e sono 47. Il foglio di questo pacchetto si stampa sui soli simboli che servono.
- **`scripts/rasterize.sh` taglia il fondo del foglio**, come già detto in `DRAW-018`: le immagini si
  guardano dai PDF.
- **Il ricircolo del bollitore a due serpentini** sta a destra come in ogni accumulo sanitario della
  libreria (D-176); Vaillant e Cordivari lo mettono dal lato dei serpentini. Annotato, non cambiato.
- **Due sessioni in parallelo, gli stessi numeri** (I-133). Mentre questa faceva la seconda parte,
  `REL-002` è arrivato su `main` e ha preso I-129 … I-133 e D-186, che la seconda parte aveva già usato
  sul ramo. Si sono spostati i numeri di questo ramo che non erano ancora su `main` (`9b6b33b`):
  **I-129 → I-134, I-130 → I-135, D-186 → D-187, D-187 → D-188**, nel codice, nelle prove, nelle
  istruzioni, nel catalogo e nei registri. **I rapporti degli agenti in `capire-giro-1/` restano come li
  hanno scritti**, e lì «D-187» è quella che oggi è D-188.

## 8. Il verdetto del PO, e dopo

**La tavola è approvata** (I-136): «La tavola va benissimo. Ottimo lavoro. Fondi» — con la riga unica
del solare in legenda e la prima delle due composizioni. `REL-003` si fonde su `main` con la PR della
seconda parte; il sì chiude **I-124** (i simboli nuovi), **I-126** (prima i simboli), **I-127** (le
assunzioni), **I-134** (il solare magenta) e **I-135** (che cosa serve a «Capire»).

**Dopo**: `REL-001`, la skill vera e propria e il PDF, è il pacchetto attivo (`ACTIVE_WORK_PACKAGE.md`);
l'impianto 6 può fargli da impianto nuovo per la prova in camera pulita.
