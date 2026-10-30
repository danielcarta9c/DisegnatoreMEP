# Rapporto della sessione del 29 ottobre 2026 — il canalizzato aria-aria col disegnatore MEP

Caso di prova **AA-01**. I dati del committente sono omessi: nome, indirizzo e codice di commessa sono sostituiti in
tutti i file del kit. La sessione è una sessione di lavoro su una commessa reale, non una sessione di sviluppo del
repository: la skill usata è la **1.4.1** (5 ottobre 2026), su una copia scrivibile, estesa con uno script.

---

## 0. In breve

- Il PO ha chiesto lo schema funzionale di un impianto canalizzato aria-aria, **quotabile da un installatore**: Ø e
  lunghezze su ogni tratto, e una stima dei pezzi speciali. Criterio dichiarato: **meglio sbagliare in su**.
- La skill non aveva quasi niente dell'aria-aria: simboli, catalogo, fluidi, regole erano idronici. L'ho estesa
  (11 simboli, 12 voci di catalogo, 5 fluidi, 8 famiglie, 8 file del motore toccati) e ho scritto fuori dalla skill
  il dimensionamento, la **distinta materiali** e le tabelle sul foglio.
- Uscite: **M.02** schema funzionale A2 con tabella delle tratte, note, attività e computo; **M.03** pianta dei
  posizionamenti e dei tracciati sul catastale 1:50; **computo Excel** per la quotazione a corpo. M.02 esce dal
  comando con **zero rilievi bloccanti, zero tratte cedute, 5 pieghe, 0 sormonti**.
- Un **revisore indipendente** (agente senza il contesto della sessione) ha trovato 31 rilievi; li ho applicati quasi
  tutti, compreso uno grave di lettura della planimetria (i disimpegni sono due).
- Il PO ha giudicato il lavoro molto buono e vuole che entri nella skill: **simboli**, **dimensionamento** (aria,
  elettrico, bus) e la nuova funzione **«distinta materiali»** (bill of quantities per l'installatore). Questo kit
  è il materiale per farlo nel repository, in un pacchetto proprio (proposta: **REL-012**, §9).

---

## 1. L'impianto del caso di prova

Abitazione unifamiliare, piano terra di circa 90 m², in ristrutturazione: tre camere (13, 15, 16 m²) e un soggiorno
con cucina (24 m²). Il riscaldamento è affidato a un'altra offerta (pompa di calore idronica su pavimento radiante);
il canalizzato serve il **raffrescamento**.

| Elemento | Scelta |
|---|---|
| Unità esterna | Daikin **RXM60A**, R32 (abbinata alla FBA60A9: 5,7 kW frigoriferi nominali) |
| Unità interna | Daikin **FBA60A9** canalizzata, 1000×800×245 mm, 35 kg, portata alta 1080 m³/h (bassa ~750), prevalenza 30 Pa nominale, fino a 150 Pa, scarico VP20 con pompa a bordo, attacchi 6,35/12,7 a cartella |
| Zonizzazione | Airzone **Easyzone** a 5 uscite Ø200 per FBA60-71 (es. AZEZ8DAIBS07M5, 1425×250×454 mm, Wi-Fi integrato, gateway Daikin AZX6GTCDA1): 4 zone, due serrande (S4a, S4b) asservite al termostato del soggiorno |
| Regolazione | 4 termostati Airzone Blueface a filo, comando Daikin Madoka sul P1-P2 |

Portate di zona, dal carico estivo orario calcolato per zona (`lavoro/riferimento_carichi_estivi.py`; 21 luglio,
32 °C / 26 °C 50%, ΔT 11 K sull'aria):

| Zona | Picco (kW tot.) | Portata di progetto |
|---|---|---|
| Z1 Camera 13 m² | 0,99 | 270 m³/h |
| Z2 Camera 15 m² | 1,05 | 280 m³/h |
| Z3 Camera 16 m² | 0,89 | 210 m³/h |
| Z4 Soggiorno-cucina 24 m² | 2,53 | 550 m³/h (due bocchette) |
| Contemporaneo, ore 20 | 5,23 (5,65 con i canali) | 1080 m³/h della UI |

---

## 2. Le richieste del PO, testuali

Sullo schema (14:55):
> «facciamo schema con skill disegnatore MEP per l'impianto canalizzato. So che nella skill non abbiamo tanti simboli
> per la parte ARIA-ARIA, usiamo quello che abbiamo e al massimo integri tu la libreria e i dimensionamenti della
> skill. hai domande ? Lo scopo è creare un disegno che sia quotabile dal nostro installatore. quindi servono anche le
> lunghezze (approssimate dalla planimetria) e i diametri.»

Alle otto proposte che gli ho fatto (15:04):
> «1 ok, 2 ok, 3 ok 4 ok e forse serve una stima di pezzi speciali curve accessori valvole ecc. 5 ok 6 ok 7 ok 8 ok.
> Impegno massimo. dimensiona tutto considera che su questo installatore farà il prezzo, quindi meglio sbagliare un
> po' in su che in giu altrimenti poi ho extraworkd e extramteriali di costo vs offerta chiavi in mano al cliente.»

Le otto proposte approvate:
1. pianta dal catastale (1:200, ±10-15%);
2. UI nel controsoffitto del disimpegno, ripresa nello stesso disimpegno; UE a parete sul fronte più vicino, lontana
   dalla PdC idronica e fuori dalla sua zona di rispetto, linee ~8 m;
3. plenum Airzone a **5 serrande**, 2 sul soggiorno con un solo termostato, flessibili Ø200 a 2,4-2,6 m/s;
4. schema funzionale con Ø e lunghezza su ogni tratto, e tabella delle quantità sul foglio (con la stima dei pezzi
   speciali, aggiunta dal PO);
5. diametri: frigo 6,35/12,70 dai dati Daikin, condensa VP20 con la pompa, flessibili ≤ 3 m/s, ripresa < 2 m/s;
6. elettrico e comandi: alimentazione UE dal quadro, cavo UI-UE, bus Airzone ai termostati; sezioni dai manuali
   Daikin, altrimenti «DA DEFINIRE»;
7. condensa allo scarico del bagno più vicino, con sifone;
8. cartiglio: titolo «Schema funzionale — impianto di climatizzazione canalizzato», tavola M.02, rev. 00,
   disegnato Nove C, controllato Ing. Daniel Carta.

Dopo la consegna (16:21):
> «lavoro eccellente davvero. Vorrei non buttare quello che hai fatto. Come possiamo aggiornare la skill Disegnatore
> MEP con il tuo lavoro? Mi sembra che 1 hai introdotto simboli che non c'erano e sono fatti molto bene i tuoi.
> 2-ahai aggiunto il dimensionamento impianti elettrici e dati e sono anche questi fatti molto bene 3- anche la parte
> aria l'hai fatta bene pensata. cosa hai usato della skill e cosa invece hai aggiunto di tuo ? la distinta materiali
> mi è piaciuta tantissimo. chiamiamola una funzionalità aggiuntiva "distinta materiali" o Bill of quantities o
> materiali per installatore ecc. non va buttato pero' il lavoro che hai fatto. e va integato nella skill in modo che
> il prossimo agente si trova un po' di lavoro già fatto.»

E per il kit (16:27):
> «dammi un .zip con dentro tutto qullo che devo dare alla sessione di sviluppo. compresa la tavola che hai generato
> che è venuta proprio bene ed è un ottimo riferimento, anche il report di tutta la nostra chat e di cosa hai fatto tu.
> Non voglio si perdi nulla. cosi' parto con la sessione in claude Code gli do lo zip e sviluppo li. Togli i dati del
> cliente ovviamente. non servono a nulla»

**Nota per lo sviluppo.** La skill dice «Non progetti» e «non aggiungi voci al catalogo né simboli alla libreria».
In questa sessione il PO ha chiesto esplicitamente il contrario per questo lavoro. Portarlo nella skill vuol dire
**cambiare quella regola**, ed è una decisione del PO (§9).

---

## 3. Il percorso

1. **Lettura del motore.** Il modello aveva già i domini aeraulico, refrigerante, condensa e controllo, e le famiglie
   UE, UI, TA, VEN; gli stili di legenda per aria di mandata e ripresa, refrigerante liquido e gas, condensa; i layer
   DXF di aria, refrigerante e condensa. Mancavano: simboli e voci di catalogo (tranne il diffusore, senza voce), i
   fluidi `return_air`, `condensate` e quelli elettrici nei nomi, uno stile per i circuiti elettrici, una scritta
   libera per tratto, un posto per le tabelle sul foglio.
2. **Estensione su una copia** della skill (`lavoro/estendi.py`, da applicare a `skill-orig`): dati nei tre fasci e
   in `naming`, codice per sostituzioni di testo controllate (ogni sostituzione verifica di trovare il testo una volta
   sola). Nel repository va rifatta bene: §5 e §9.
3. **Prima tavola** (A2): il motore instrada al primo colpo; 4 rilievi bloccanti (le scritte dei termostati, troppo
   vicini), bus a L non annidate con sormonti.
4. **Seconda tavola**: centrale Airzone separata dal plenum, con le porte di bus sul fianco e i termostati in colonna
   alla loro quota: bus rettilinei, **5 pieghe, 0 sormonti**, zero rilievi.
5. **Tabelle sul foglio**: telaio «A2T» che restringe l'area del disegno e lascia due zone libere (a destra e in
   basso); le tabelle si scrivono dopo nell'SVG, si rigenera il PDF col writer del motore e si aggiungono al DXF con
   ezdxf (`lavoro/tabelle.py`).
6. **Excel** per l'installatore (`lavoro/excel.py`).
7. **Revisione indipendente** (§8) e **rev. dei numeri**: UI spostata nel disimpegno est, ripresa 1000×250,
   bocchette 400×200, regola unica delle lunghezze, assistenze murarie, cantiere, prove fra i due accessi, varianti,
   Excel a corpo senza formule, tratte numerate T01-T18.
8. **Tavola M.03** (`lavoro/pianta.py`): il catastale schiarito come sfondo, a 1:50, coi tracciati degli stessi numeri
   e il cartiglio Nove C disegnato con la funzione del motore.
9. Consegna, poi questo kit (dati del committente sostituiti, tavole rigenerate da zero col `rifai.sh` del kit).

---

## 4. Cosa ho usato della skill e cosa ho aggiunto

| | Della skill, tale e quale | Aggiunto |
|---|---|---|
| Flusso | grafo → `valida` → `completa` → piano → `disegna` → `anteprima`; instradamento, posa degli organi in linea, sigle, legenda, cartiglio, tabella delle apparecchiature, PDF e DXF, preflight e regole del piano | — |
| Libreria | il simbolo `air-diffuser` (rinominato in legenda «Bocchetta di mandata con plenum di raccordo») | 11 simboli, 12 voci di catalogo, 5 fluidi, 8 famiglie con sigla (§5) |
| Motore | il posatore delle scritte dei diametri (`layout/diametri.py`) | scritta manuale per tratto; fluidi senza andata e ritorno; stili e layer elettrici; tabella apparecchiature estesa; telaio con zone per le tabelle |
| Fuori dalla skill | — | rilievo dal catastale e regola delle lunghezze; dimensionamento di aria, refrigerante, condensa, elettrico, bus; **distinta materiali**; tabella delle tratte, note e computo sul foglio; tavola M.03; Excel; revisione indipendente |

---

## 5. L'estensione, pezzo per pezzo

I file pronti per il repository sono in `per-il-repo/`, con lo stesso albero del repository.

### 5.1 Simboli (`per-il-repo/assets/symbols/`)

Fonte di tutti: «proposta della sessione del 29/10/2026 (caso di prova AA-01, canalizzato aria-aria): forma da
approvare dal PO sulla tavola». Nessuna fonte esterna citata, come prescrive D-083.

| id | mm | porte (faccia, x, y) | note |
|---|---|---|---|
| `split-outdoor-unit` | 40×30 | liquid R(40;7,5), gas R(40;17,5), power B(10;30), link B(27,5;30) | ventilatore e compressore; porte frigo a 10 mm, come la UI: linee rette se allineate |
| `ducted-indoor-unit` | 40×30 | liquid L(0;7,5), gas L(0;17,5), supply R(40;12,5), p1p2_a R(40;25), return T(20;0), link B(7,5;30), drain B(22,5;30), p1p2_b B(32,5;30) | batteria, ventilatore, collari di mandata e ripresa, vaschetta con pompa |
| `zoning-plenum-5` | 40×57,5 | in L(0;12,5), out_1..5 R(40; 5/17,5/30/42,5/55), motori B(20;57,5) | cinque serrande disegnate sulle uscite, passo 12,5 |
| `zone-controller` | 30×60 | serrande T(15;0), p1p2 L(0;10), power L(0;20), bus_1..4 R(30; 7,5/22,5/37,5/52,5) | centrale di zona; porte di bus a 15 mm per i termostati in colonna |
| `return-grille` | 10×10 | a R(10;5) | griglia con plenum e filtro; ruotabile |
| `condensate-trap` | 10×5, in linea | a, b | sifone (U sotto la linea) |
| `condensate-outlet` | 5×10 | a T(2,5;0) | allaccio allo scarico (imbuto) |
| `electrical-panel` | 25×15 | out_1 T(7,5;0), out_2 T(17,5;0) | quadro (rettangolo con triangolo pieno) |
| `isolator-switch` | 5×5, in linea | a, b | sezionatore |
| `room-thermostat` | 10×10 | a L(0;5) | «T» come glifo leggibile (`upright_glyphs`) |
| `wired-remote` | 10×10 | a L(0;5) | comando a filo |

Vincolo imparato: **una faccia con una porta vuole `keep_out` > 0** su quella faccia, o il manifesto non carica.

### 5.2 Catalogo (`per-il-repo/examples/layout/catalog/`)

`split-outdoor-unit` (refrigerant_generation), `ducted-indoor-unit` (direct_expansion_terminal),
`zoning-plenum-5` (air_zoning), `zone-controller` (zone_control), `air-supply-terminal` (air_terminal, simbolo
`air-diffuser`), `return-air-terminal` (air_return), `condensate-trap` (condensate_trap), `condensate-outlet`
(boundary), `electrical-panel` (power_source), `isolator-switch` (power_isolation), `room-thermostat`
(room_control), `wired-remote` (unit_control).

Tratti: tutte `shutoff_ordinary` + `attachment_inline`. **Nessuna `maintainable`**, apposta: farebbe scattare la
regola dell'intercettazione, che cercherebbe una valvola di intercettazione sul fluido frigorigeno o sull'aria, e il
catalogo non ne ha (il docstring di `MAINTAINABLE` dice già che un'unità su linea frigorifera o un ventilatore su un
canale non la hanno). Porte elettriche e di bus nel dominio `control`, coi fluidi `power_supply`,
`interconnection`, `control_bus`.

### 5.3 Fluidi e famiglie (`per-il-repo/naming/`)

Fluidi nuovi in `media.json`: `return_air`, `condensate`, `power_supply`, `interconnection`, `control_bus`.
Famiglie nuove in `families.json`, con sigla: PLZ (plenum motorizzato), CZ (centrale di zona), RA (ripresa), SIF
(sifone), QE (quadro), SZ (sezionatore), TZ (termostato di zona), CF (comando a filo).

### 5.4 Codice (`per-il-repo/src-estensione.patch`)

La patch è fatta sulla 1.4.1, ed **è stata provata su `main` dopo la PR #79 (1.5.0): `git apply --check` passa**.
L'esito dei test del repository con la patch e i dati applicati è in `per-il-repo/ESITO-DEI-TEST.md`.

| file | cosa | perché |
|---|---|---|
| `layout/legend.py` | stili di `power_supply`, `interconnection`, `control_bus`; nomi in legenda; gas a tratteggio corto (`3 1.5`) | il campione in legenda è corto: col tratteggio `6 2` il gas sembrava pieno |
| `layout/legend.py` | `NON_DIREZIONALI`: aria, refrigerante, condensa, circuiti elettrici hanno **una riga sola** in legenda e lo stesso tratto in qualunque verso | senza, comparivano «Aria di mandata — andata» e i colori del ritorno spostati |
| `graphics/dxf.py` | layer E-POWR-CIRC, E-POWR-LINK, E-CTRL-BUS | aria, refrigerante e condensa avevano già i loro |
| `diametri/tratti.py` | `_tratti_con_scritta`: una tubazione con `properties.scritta` dà al suo tratto quella scritta, posata dal posatore dei diametri; un DN calcolato sullo stesso tratto cede il posto | è il «Ø · L» su ogni linea |
| `layout/diametri.py` | testo e campione della riga di legenda («Ø · L», «diametro o sezione e lunghezza da quotare…») | — |
| `graphics/tabella.py` | nella tabella delle apparecchiature anche UI, plenum, centrale e comando a filo; per la UI potenza e portata | i termostati **no**: vedi §6, punto 2 |
| `graphics/frame.py`, `piano/formato.py`, `piano/esecutore.py` | `SheetFrameConTabelle` e il formato **A2T**: A2 con l'area del disegno ristretta di 175 mm a destra e 135 in basso | le tabelle stanno nelle zone liberate; i controlli del motore lavorano sull'area ristretta |

**Nel repository va rifatta, non incollata.** La scritta per tratto è meglio un campo del modello che una proprietà
libera. Il telaio con tabelle dovrebbe essere un'opzione del piano, non un formato in più. E le tabelle andrebbero
disegnate dal motore, che conosce le zone libere, invece che scritte dopo nell'SVG.

---

## 6. Comportamenti del motore scoperti lavorando (da guardare nello sviluppo)

1. **Sigle tutte o niente.** Se un pezzo ha `tag` esplicito, gli altri non ricevono più la sigla automatica (nella
   tabella compariva «–»). Rimedio usato: sigle esplicite su tutti i pezzi principali. Da verificare se è voluto.
2. **Etichetta e tabella in conflitto.** Un pezzo che sta nella tabella delle apparecchiature porta solo la sigla
   (`senza_valori`), quindi la sua `etichetta` non si scrive; ma il preflight la pretende (`FREE_LABEL_OMITTED`,
   bloccante). Rimedio usato: i termostati fuori dalla tabella.
3. **Dove si posa un organo in linea dipende dall'id delle tubazioni.** La tratta comincia dal primo capo non in linea
   della prima tubazione nell'ordine del modello, e `completa` ordina le tubazioni per id: il sezionatore è finito
   accanto al quadro finché la tubazione lato UE non si è chiamata `e-1a` (prima di `e-1b`). Fragile: un sezionatore
   «di prossimità» deve stare dalla parte della macchina per mestiere, non per nome.
4. **Pezzi a un attacco ruotati dalla deduzione** in modo inatteso quando la linea arriva dall'alto (termostati);
   risolto con la geometria (centrale separata), non con la rotazione.
5. **Il writer PDF è WinAnsi**: «≥», «≤», «→» diventano «?». Nelle tabelle ho scritto «min.», «max.», «-».
6. `DRAWING_TOUCHES_THE_BORDER` e `SERVICE_STUB_LONGER_THAN_ITS_MINIMUM` si sono chiusi accorciando gli stacchi
   (ripresa, scarico) e spostando la scritta della ripresa nell'etichetta del pezzo.

---

## 7. Dimensionamento e distinta: le regole usate

Tutto in `lavoro/dimensionamento.py`, che scrive `dim.json`, unica fonte dei numeri di tavole, tabelle ed Excel.
Questa è la conoscenza da trasformare in **regole come dato** (§9).

**Lunghezze.** Rilievo dal catastale (300 dpi, 1:200: 59,06 px/m), percorsi ortogonali in metri per ogni tratto.
`L stimata` = percorso + discese e raccordi; **`L da quotare` = (L stimata + 1 m) × 1,15, per eccesso al mezzo
metro**, mai sotto un minimo dato: linee frigo 12 m e condensa 10 m per l'incertezza dei percorsi, bus 5 m, ramo
d'aria 2 m (acustica: l'eccesso resta in ansa).

**Aria.**
- Velocità nei flessibili Ø200 da 1,9 a 2,5 m/s.
- Perdite lineari con Haaland su lamiera (ε 0,09 mm), moltiplicate per 2 per il flessibile coibentato steso (ASHRAE
  dà 1,5-2). Curve K 0,8 (3 per ramo), imbocco del plenum di bocchetta K 1,0.
- Prevalenza della UI a budget: ramo peggiore 18 Pa + bocchetta 10 + plenum 15 + ripresa e filtro 20 + transiti 5
  = circa 70 Pa, da impostare con la regolazione automatica in messa in servizio.
- Ripresa 1000×250, 1,2 m/s sulla sezione lorda. Bocchette 400×200 a doppio filare, Aeff ≥ 0,055 m².
- Griglie di transito a 1,5 m/s: camere Aeff ≥ 0,05 m², soggiorno ≥ 0,10, porta fra i disimpegni ≥ 0,09.
- Velocità minima della UI (~750 m³/h) maggiore della portata di ogni camera: Z4 zona di sfogo con apertura minima,
  niente serranda di bypass.

**Refrigerante.**
- Diametri dalla macchina: 6,35/12,7 a cartella. Isolamento ≥ 10 mm sul liquido e ≥ 13 mm sul gas, resistente a
  120 °C (manuale Daikin FTXM60-71A).
- Precarica fino a 10 m, oltre 20 g/m, massimo 30 m, dislivello 20 m (scheda RXM-A).
- Riserva di R32 di 0,2 kg.

**Condensa.**
- PVC Ø32 con raccordo di adattamento dall'attacco VP20 (Øe 26), pendenza ≥ 1%.
- Sifone ispezionabile, innesto Ø40 sullo scarico del bagno, isolamento anticondensa sul tratto in controsoffitto.

**Elettrico e bus.**
- Linea dedicata UE in FG16OR16 3G2,5, protetta da magnetotermico-differenziale 1P+N C16, Idn 30 mA, tipo A o F, 6 kA.
  La taglia è da verificare sulla targa della RXM60A: il riferimento usato è la RXM60R, con MCA 15,9 A e fusibile
  massimo 16 A.
- Sezionatore onnipolare di prossimità IP55 con apertura dei contatti ≥ 3 mm.
- Cavo UI-UE a 4 conduttori ≥ 1,5 mm² a doppio isolamento (manuale Daikin).
- Linea dedicata della centrale Airzone in 3G1,5 con magnetotermico C6.
- Bus Airzone a stella dalla centrale. P1-P2 per gateway e Madoka, con i ruoli da impostare.
- Lunghezze dei cavi: percorso + 1,2 m di discesa a 1,5 m + 0,5 m.

**Distinta materiali.** In sei sezioni più due:
- **A** apparecchiature (fornite da Nove C);
- **B** distribuzione aria:
  - flessibile in **confezioni da 10 m**, tratti interi senza giunte, 0,5 m di sfrido;
  - fascette 2+2 per tratto e riserva;
  - sostegni ogni ≤ 1,2 m;
  - kit sospensione: UI 4, plenum 4, ripresa 2;
  - curve in lamiera alle uscite strette;
  - nastro, isolamento;
- **C** circuito frigorifero e UE: coppie pre-isolate, canalina e accessori a numero, staffe, scarico della UE,
  riserva R32;
- **D** condensa;
- **E** elettrico e regolazione: cavi, protezioni, corrugati, scatole, aggiornamento dello schema del quadro;
- **F** assistenze murarie: le aperture sono dell'installatore, chiusure e ripristini del committente;
- **Z** opere del committente: controsoffitto con altezza libera e botole, velette, bocchette, griglie, transiti,
  ripristini;
- **G** attività a corpo: posa; prove fra i due accessi (azoto in pressione con manometro e verbale, prova della
  condensa prima della chiusura); messa in servizio con Nove C; DiCo D.M. 37/2008 lettera a) e lettera c);
  POS e mezzi; custodia delle macchine; protezioni; pulizia e smaltimenti;
- **V** varianti a prezzo unitario: metro di linea frigo completa, metro di flessibile, metro di cavo, accesso
  aggiuntivo, centralino aggiuntivo.

L'Excel chiede un **prezzo a corpo, fisso e invariabile**, con **sopralluogo obbligatorio** e una sezione **H** per le
voci che l'installatore aggiunge; **solo valori, nessuna formula** (preferenza del PO per i computi Excel).

---

## 8. La revisione indipendente

Testo integrale e cosa ne ho fatto: `REVISIONE-INDIPENDENTE.md`. I rilievi più pesanti, tutti applicati:
- **i disimpegni sono due**, separati da una tramezza con porta: il plenum cadeva nel varco. UI, plenum e ripresa sono
  passati nel disimpegno est;
- **l'impostazione dell'Excel**: prezzo unitario per quantità equivale a un contratto a misura, e ogni metro in più
  diventa un extra. È diventato a corpo, con il sopralluogo obbligatorio e la sezione H;
- **assistenze murarie e cantiere**: mancavano;
- **ripresa e bocchette**: erano rumorose al limite;
- **coerenza**: la regola delle lunghezze era dichiarata e non applicata ovunque.

---

## 9. Proposta per il repository: REL-012 «Aria-aria, regolazione e distinta materiali»

**Le decisioni che sono del PO, prima di cominciare:**
1. **«Non progetti».** Dimensionare l'aria, la prevalenza e le sezioni dei cavi, stimare i pezzi speciali e maggiorare
   le lunghezze è progettare. Proposta: lo stesso schema dei diametri (D-193). Spento di default, acceso solo su
   richiesta esplicita, ogni numero con la sua regola e la sua fonte, e il foglio dei calcoli accanto alla tavola.
2. **I simboli.** Sono proposte della sessione, e il PO li approva guardandoli sulla tavola (D-081, D-083).
3. **La precedenza rispetto a REL-011** (regole del corredo sul manuale Shenling, da cominciare).
4. **La tavola M.03** (pianta su raster): in REL-012 o in un pacchetto dopo.

**Il lavoro, in fasi:**
1. **Libreria**: i dati di `per-il-repo/` nel repository, con i test della libreria (rotazioni, porte sulle facce,
   `keep_out`, glifi).
2. **Motore**:
   - la scritta per tratto come dato del grafo;
   - i fluidi senza verso in legenda;
   - stili e layer elettrici;
   - le zone per le tabelle come opzione del piano;
   - la correzione dei punti 1-3 del §6 (sigle, etichetta in tabella, lato dell'organo in linea), se il PO li
     considera difetti.
3. **Distinta materiali** come funzione (`mep.py distinta`), con le **regole come dato**, per esempio in
   `rules/distinta/`:
   - ogni voce di catalogo dichiara il proprio **corredo di posa**;
   - ogni fluido dichiara quello che costa a metro e a giunzione;
   - attività e varianti per dominio;
   - le lunghezze sono un dato del progettista, oppure un rilievo su richiesta, con la maggiorazione configurabile;
   - escono la tabella sulla tavola e l'Excel solo valori.
4. **Accettazione**: questo impianto. La M.02 rigenerata dalla skill deve coincidere con
   `tavole/AA-01_M.02_Schema_funzionale_canalizzato_rev00.pdf` per contenuto, e uscire con zero rilievi bloccanti e
   zero tratte cedute. Il PO guarda le tavole, approva la fusione, e si fa la release 1.6.0 con
   `scripts/costruisci-skill.py`.

---

## 10. Fonti dei dati di macchina

- Daikin, RXM-A, tabella prodotto: <https://www.daikin.it/it_IT/cerca-prodotto/product.table.html/RXM-A.html>
  (30 m, 20 g/m oltre 10 m, 20 m di dislivello, 1~ 220-240 V).
- Daikin, FTXM60-71A, manuale di installazione:
  <https://www.daikin.it/content/dam/document-library/installation-manuals/ac/split/ftxm-a/FTXM60-71A_Installation%20manual_3PIT697375-10N_Italian.pdf>
  (cavo di collegamento a 4 conduttori ≥ 1,5 mm², isolamenti, interruttore onnipolare con 3 mm).
- Datasheet FBA-A9 / RXM-R (dal revisore): <https://oceanairuk.com/cdn/shop/files/FBA-A9_RXM-R_Datasheet_102B.pdf>
  (FBA60A9 18/15/12,48 m³/min, 35 kg; RXM60R 49 kg, MCA 15,86 A, fusibile massimo 16 A).
- Airzone Easyzone QAI 5 uscite per FBA60-71:
  <https://climaled.fr/en/airzone-easyzone-ducted-medium-motorised-plenum-cmv-daikin-fba60-71-5-outlets-azez8daibs07m5>
  (AZEZ8DAIBS07M5 / AZX6GTCDA1, 1425×250×454 mm, Wi-Fi integrato, termostati esclusi).
- Dati FBA60A9 (dimensioni, prevalenza, scarico VP20, sollevamento 625 mm): Data Book Daikin letto nella prima parte
  della sessione.

---

## 11. Indice del kit

Vedi `LEGGIMI.md`.
