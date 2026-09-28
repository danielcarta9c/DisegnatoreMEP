# REL-006 — la tabella delle apparecchiature: rapporto

**Pacchetto:** `REL-006` (`ACTIVE_WORK_PACKAGE.md`; I-141, I-144, D-190) · **Ramo:**
`claude/peaceful-curie-9igqh8` · **Base:** `main` a `e0cefea` (PR #62) · **Avviato dal PO:** I-148

> **Le tavole, per prime**
>
> **Le sei tavole approvate, con la tabella**, in PDF e in DXF, in [`tavole/`](tavole/): i cinque
> impianti di `DRAW-018` (tavole 1–5) e l'impianto 6 di `REL-003` (tavola 6), rieseguiti dai **loro**
> grafi e piani, col cartiglio compilato coi dati di prova di `REL-002`. Accanto ai DXF c'è il logo,
> che il DXF collega e va tenuto nella stessa cartella.
>
> **I dati della tabella sono di prova, e inventati** ([`dati-di-prova.json`](dati-di-prova.json)):
> potenze, volumi, portate e prevalenze plausibili, marca «Marca di prova» e modelli «PRV-…» che non
> sono di nessun costruttore — il repository è pubblico (D-038). Vengono dal testo degli impianti solo
> le potenze di pompa di calore e caldaia e i volumi di bollitore e volume tecnico dell'impianto 6, e
> il volume del bollitore dell'impianto 5. **Due celle restano vuote apposta**: marca e modello dello
> scambiatore della tavola 4, la potenza del collettore solare della tavola 6.
>
> **E una tavola senza dati**, la 1 col suo grafo com'è agli atti: tutte le celle dei dati con il
> trattino.

| tavola | formato | PDF | DXF | che cosa mostra |
|---|---|---|---|---|
| 1 — due pompe di calore in parallelo, accumulo combinato | A3 | [`tavola-1.pdf`](tavole/tavola-1.pdf) | [`tavola-1.dxf`](tavole/tavola-1.dxf) | «nr 1», «nr 2» sulle due pompe di calore |
| 2 — pompa di calore con deviazione fra climatizzazione e ACS | A3 | [`tavola-2.pdf`](tavole/tavola-2.pdf) | [`tavola-2.dxf`](tavole/tavola-2.dxf) | la tavola con meno spazio libero in alto a sinistra |
| 3 — pompa di calore diretta su pavimento radiante, ACS separata | A3 | [`tavola-3.pdf`](tavole/tavola-3.pdf) | [`tavola-3.dxf`](tavole/tavola-3.dxf) | il boiler in pompa di calore: potenza **e** volume |
| 4 — sistema ibrido pompa di calore e caldaia | A3 | [`tavola-4.pdf`](tavole/tavola-4.pdf) | [`tavola-4.dxf`](tavole/tavola-4.dxf) | lo scambiatore senza marca e modello: il trattino |
| 5 — tre pompe di calore in cascata, tre secondari e ACS | A2 | [`tavola-5.pdf`](tavole/tavola-5.pdf) | [`tavola-5.dxf`](tavole/tavola-5.dxf) | undici righe; prevalenze in kPa e in m c.a. |
| 6 — centrale ibrida con PdC di alta potenza, caldaia modulare e solare | A2 | [`tavola-6.pdf`](tavole/tavola-6.pdf) | [`tavola-6.dxf`](tavole/tavola-6.dxf) | **tutte le sigle nuove**: il testo non ne dava nessuna |
| 1, senza dati | A3 | [`tavola-1-senza-dati.pdf`](tavole/tavola-1-senza-dati.pdf) | [`tavola-1-senza-dati.dxf`](tavole/tavola-1-senza-dati.dxf) | le celle vuote |

## 1. Che cosa guardare sulle tavole

Il PO ha fissato le colonne e il perimetro (D-190): **codice, descrizione, caratteristiche, marca,
modello**; le apparecchiature principali e il vaso di espansione, niente valvole. **Tutto il resto è
una proposta della sessione, scritta in D-192, e si giudica guardando le tavole** (D-146):

1. **Quali righe.** Generatori, accumuli e bollitori, separatori idraulici, scambiatori, circolatori e
   vasi di espansione. **Fuori** le valvole, e con loro filtri, strumenti, raccordi e attacchi — e
   **i terminali** (radiatori, ventilconvettori, pannelli), che nello schema di centrale sono le
   utenze: sulla tavola 2 il ventilconvettore VC-01 non è in tabella. Le righe sono in ordine di
   famiglia — prima chi produce calore, poi accumuli, separatori, circolatori, scambiatori, vasi — e
   dentro la famiglia in ordine di sigla.
2. **Il codice è la sigla del disegno** — `PDC-01`, non `pdc.01` come nel messaggio del PO —, e
   **adesso la sigla c'è sul disegno per ogni riga della tabella**. Prima non era così: vedi §3.1.
3. **«nr 1», «nr 2»** quando due apparecchiature hanno lo stesso nome (tavole 1, 5, 6): dice *quale*
   delle due, non *quante*. Una voce sola non lo porta.
4. **Le caratteristiche**, per mestiere: la potenza di generatori e scambiatori, il volume di accumuli,
   bollitori e vasi, portata e prevalenza dei circolatori, separate da « · ».
5. **Il trattino** in ogni cella senza dato.
6. **I dati non si ripetono accanto al pezzo**: sul disegno resta la sola sigla, perché i dati sono in
   tabella (D-052: accanto a un pezzo si scrive solo ciò che aggiunge informazione).
7. **La grafica**: nell'angolo in alto a sinistra, contro squadratura e testata come la legenda sta
   contro la squadratura a destra; griglia piena al tratto sottile della legenda (0,18 mm, nero); testi
   di 1,8 mm come legenda e sigle, in Arial; intestazione in neretto; righe di 5 mm; colonne larghe
   quanto il loro testo.

## 2. Che cosa c'è

- **La tabella**, `src/disegnatore_mep/graphics/tabella.py`: che cosa dice (`righe_della_tabella`),
  quanto è grande (`impagina_la_tabella`, con le larghezze di Helvetica del cartiglio), come si disegna
  (`tratti_della_tabella`: linee e testi che SVG e DXF scrivono **dalle stesse misure**). La geometria
  la porta la tavola (`SheetGeometry.tabella`, facoltativa: una tavola che non la ha si scrive come
  prima, byte per byte).
- **I dati con un nome fisso**, nelle proprietà del pezzo (`model/project.py`): `power_kw`,
  `volume_l`, `flow_rate_m3h` — numeri nell'unità del nome —, la prevalenza in `head_kpa` **oppure**
  `head_m` (metri di colonna d'acqua: non si converte, per non cambiare il numero del progettista),
  `marca`, `modello`. Il modello rifiuta un numero scritto come testo («15 kW» in `power_kw`). Le
  prime quattro erano già le chiavi che la tavola sapeva scrivere accanto a un pezzo; `modello` era
  già la chiave con cui «Capire» scriveva il nome commerciale.
- **«Capire»** (`skill/capire/ISTRUZIONI.md` §3, §4.5, §4.6, §6, §9): scrive quei dati solo dal testo,
  non propone marche né modelli, e **chiede quelli che mancano in una voce sola** di `assumptions`; se
  il progettista non risponde, la tavola esce lo stesso, col trattino. I dati di un vaso di espansione
  — che «Capire» non disegna: lo aggiunge il completamento — li scrive in un'assunzione, perché non
  vadano persi (§3.3).
- **Il posto sul foglio** (`layout/compose.py::sgombra_la_tabella`, chiamata dall'esecutore del
  piano): niente del disegno entra nella tabella allargata di 5 mm. **Se il disegno, centrato, non ci
  entra, resta dov'è**; se ci entra, si sposta tutto insieme del meno possibile, a destra o in basso,
  di passi di griglia. Sigle e indirizzi della verifica la evitano (`layout/labels.py`, parametro
  `ostacoli`).
- **Il rilievo**: `DRAWING_OVER_THE_EQUIPMENT_TABLE`, bloccante, se qualcosa del disegno entra nella
  tabella — succede solo se il foglio è troppo piccolo, e il formato lo sceglie il piano (D-151). Un
  vincolo della posa ha un rilievo sulla tavola finita (D-158). `SHEET_LARGER_THAN_NEEDED` conta la
  tabella quando dice che il disegno starebbe su un foglio più piccolo.
- **Il DXF** (`graphics/dxf.py`): la tabella nello spazio modello, come la legenda, sul layer
  `M-ANNO-SCHD` «Tabella delle apparecchiature» — `SCHD`, «Schedules», è il gruppo che le linee guida
  AIA danno alle tabelle, accanto a `LEGN` della legenda (AIA CAD Layer Guidelines, §3, codici delle
  annotazioni, [PDF](https://facilities.duke.edu/sites/default/files/AIA%20CAD%20Layer%20Guidelines.pdf)).
- **Le prove**: `tests/graphics/test_tabella.py`, 35; una misura in più nella prova dell'ordine del
  preflight (`tests/validation/test_preflight.py`).

## 3. Che cosa ho trovato, e va detto

### 3.1 Le sigle «che il disegno già scrive» non c'erano per tutti

Il pacchetto proponeva come codice «la sigla che il disegno già scrive accanto al pezzo». **Il disegno
ne scriveva solo una parte**: la sigla dell'ingegnere, quando il testo la dava. La lettura
dell'impianto assegna una sigla a ogni pezzo (`graph/plant.py`: D-097, «la sigla è una sola per tutto
il prodotto», D-098), ma sul disegno finiva solo quella scritta nel testo. Così **il vaso di espansione
non aveva sigla su nessuna delle sei tavole**, e **la tavola 6 non aveva nessuna sigla**, perché il
testo dell'impianto 6 non ne dava.

Un codice in tabella che sul disegno non c'è non identifica niente. **I pezzi della tabella portano
adesso la loro sigla anche sul disegno**, quella della lettura: sulle tavole 1–4 si aggiunge `VE-01`,
sulla 5 `VE-01` e `VE-02`, sulla 6 undici sigle. Nessun'altra sigla cambia o si sposta (§4, criterio 3).

### 3.2 Sulla tavola 6 i generatori sono GT-01, GT-02, GT-03

È la sigla della famiglia «Generatore di calore» di `naming/families.json` (mestiere
`heat_generation`), assegnata seguendo l'acqua dalle sorgenti (D-098): caldaia GT-01, pompa di calore
GT-02, collettore solare GT-03. Negli impianti 1–5 l'ingegnere aveva scritto `PDC-01`, `CAL-01`, e
quelle restano. **Se il PO vuole `PDC`, `CAL`, `SOL` anche quando il testo non li dà, è una domanda
sulle famiglie delle sigle**, non sulla tabella: oggi la famiglia si legge dal mestiere, e pompa di
calore e caldaia fanno lo stesso mestiere.

### 3.3 I dati dei vasi di espansione non hanno ancora una strada completa

I vasi li aggiunge il completamento (le regole), non «Capire»: se il progettista ne dà volume, marca e
modello, «Capire» non ha un pezzo su cui scriverli. Adesso li scrive in un'assunzione, perché non
vadano persi; **chi li riporta sul vaso, quando il progettista approva il grafo completo, è la skill
cucita di `REL-001`**, che ancora non c'è. Sulle tavole di prova i dati dei vasi sono scritti a mano
nei dati di prova.

### 3.4 I testi della tabella sono in Arial, quelli dello schema ancora con le grazie

La tabella dichiara il carattere (Arial, come il cartiglio e il DXF); legenda e sigle no, e il browser
le stampa con le grazie. È il difetto già noto dei PDF (I-122): si allinea nel pacchetto del PDF senza
browser, e sulla tavola la differenza si vede.

### 3.5 Il collettore solare non ha una caratteristica sua

Un campo solare si descrive spesso con la superficie o il numero dei collettori più che con la potenza:
la proposta gli assegna la potenza, come a ogni generatore, e sulla tavola 6 la cella è vuota apposta.
**Se il PO vuole la superficie**, è una chiave in più.

## 4. Le misure

Ogni criterio con il comando e il suo esito.

**Le tavole e le prime cinque misure** — la geometria di `main` scritta da
`geometria_di_main.py` su un albero di `main` a `e0cefea`, poi il collaudo:

```
git worktree add --detach <albero> origin/main
PYTHONPATH=<albero>/src python3 docs/collaudi/REL-006/geometria_di_main.py <albero> <geometria-main>
PYTHONPATH=src python3 docs/collaudi/REL-006/collaudo.py <lavoro> --prima <geometria-main>
```

```
== tavola-1 — grafo-completo-1.json, formato A3
   tabella 92.5 x 30 mm in (10, 16), colonne [12.5, 30.0, 20.0, 15.0, 15.0]
   | PDC-01 | Pompa di calore aria-acqua nr 1 | 15 kW | Marca di prova | PRV-PDC-15
   | PDC-02 | Pompa di calore aria-acqua nr 2 | 15 kW | Marca di prova | PRV-PDC-15
   | ACC-01 | Accumulo combinato | 800 l | Marca di prova | PRV-ACC-800
   | CIR-01 | Pompa di circolazione | 2,5 m³/h · 60 kPa | Marca di prova | PRV-CIR-25
   | VE-01 | Vaso di espansione | 24 l | Marca di prova | PRV-VE-24
   nella tabella: 0 — il piu' vicino: simbolo valve-safety-pdc-master-water-supply a 57.5 mm
   rispetto a main: simboli fermi (43), tratte uguali (25), sigle nuove ['VE-01'], sigle di main spostate o tolte []
   DXF: linee 13/13 uguali, testi 30/30 uguali
   deterministico: SVG uguale (a3ef5d9b1965ada5), DXF uguale (201b77110e34a5b3)
   preflight: nessun rilievo · regole: ['SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER']

== tavola-2 — grafo-completo-2.json, formato A3
   tabella 92.5 x 30 mm in (10, 16), colonne [12.5, 30.0, 20.0, 15.0, 15.0]
   | PDC-01 | Pompa di calore aria-acqua | 12 kW | Marca di prova | PRV-PDC-12
   | VOL-01 | Volano termico a quattro attacchi | 300 l | Marca di prova | PRV-VOL-300
   | BOL-01 | Bollitore ACS | 300 l | Marca di prova | PRV-BOL-300
   | CIR-01 | Pompa di circolazione | 2 m³/h · 50 kPa | Marca di prova | PRV-CIR-20
   | VE-01 | Vaso di espansione | 18 l | Marca di prova | PRV-VE-18
   nella tabella: 0 — il piu' vicino: simbolo valve-safety-pdc-water-supply a 7.5 mm
   rispetto a main: simboli fermi (43), tratte uguali (25), sigle nuove ['VE-01'], sigle di main spostate o tolte []
   DXF: linee 13/13 uguali, testi 30/30 uguali
   deterministico: SVG uguale (2da3572831758d3f), DXF uguale (638132c2260bb094)
   preflight: nessun rilievo · regole: ['SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER']

== tavola-3 — grafo-completo-3.json, formato A3
   tabella 90 x 25 mm in (10, 16), colonne [12.5, 27.5, 20.0, 15.0, 15.0]
   | BPC-01 | Boiler in pompa di calore | 1,9 kW · 200 l | Marca di prova | PRV-BPC-200
   | PDC-01 | Pompa di calore aria-acqua | 9 kW | Marca di prova | PRV-PDC-9
   | VOL-01 | Volano termico a due attacchi | 100 l | Marca di prova | PRV-VOL-100
   | VE-01 | Vaso di espansione | 12 l | Marca di prova | PRV-VE-12
   nella tabella: 0 — il piu' vicino: sigla PDC-01 a 26.7 mm
   rispetto a main: simboli fermi (41), tratte uguali (24), sigle nuove ['VE-01'], sigle di main spostate o tolte []
   DXF: linee 12/12 uguali, testi 25/25 uguali
   deterministico: SVG uguale (8e784ca3e39c6584), DXF uguale (596fe881c3950455)
   preflight: nessun rilievo · regole: ['SERVICE_STUB_LONGER_THAN_ITS_MINIMUM']

== tavola-4 — grafo-completo-4.json, formato A3
   tabella 92.5 x 35 mm in (10, 16), colonne [12.5, 30.0, 20.0, 15.0, 15.0]
   | CAL-01 | Caldaia a condensazione | 25 kW | Marca di prova | PRV-CAL-25
   | PDC-01 | Pompa di calore aria-acqua | 16 kW | Marca di prova | PRV-PDC-16
   | VOL-01 | Volano termico a quattro attacchi | 200 l | Marca di prova | PRV-VOL-200
   | CIR-01 | Pompa di circolazione | 3 m³/h · 60 kPa | Marca di prova | PRV-CIR-30
   | SCA-01 | Scambiatore a piastre | 30 kW | – | –
   | VE-01 | Vaso di espansione | 24 l | Marca di prova | PRV-VE-24
   nella tabella: 0 — il piu' vicino: simbolo valve-safety-pdc-water-supply a 22.5 mm
   rispetto a main: simboli fermi (48), tratte uguali (27), sigle nuove ['VE-01'], sigle di main spostate o tolte []
   DXF: linee 14/14 uguali, testi 35/35 uguali
   deterministico: SVG uguale (c4fd7dd45ff8ad0d), DXF uguale (f635eb9b221e6d1f)
   preflight: nessun rilievo · regole: ['SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER', 'SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER']

== tavola-5 — grafo-completo-5.json, formato A2
   tabella 95 x 60 mm in (10, 16), colonne [12.5, 30.0, 20.0, 15.0, 17.5]
   | PDC-01 | Pompa di calore aria-acqua nr 1 | 40 kW | Marca di prova | PRV-PDC-40
   | PDC-02 | Pompa di calore aria-acqua nr 2 | 40 kW | Marca di prova | PRV-PDC-40
   | PDC-03 | Pompa di calore aria-acqua nr 3 | 40 kW | Marca di prova | PRV-PDC-40
   | VOL-01 | Volano termico a quattro attacchi | 1000 l | Marca di prova | PRV-VOL-1000
   | BOL-01 | Bollitore ACS | 500 l | Marca di prova | PRV-BOL-500
   | CIR-01 | Pompa di circolazione nr 1 | 4,5 m³/h · 70 kPa | Marca di prova | PRV-CIR-45
   | CIR-02 | Pompa di circolazione nr 2 | 3,2 m³/h · 6 m c.a. | Marca di prova | PRV-CIR-32
   | CIR-03 | Pompa di circolazione nr 3 | 5 m³/h · 55 kPa | Marca di prova | PRV-CIR-50
   | CIR-04 | Pompa di ricircolo sanitario | 0,8 m³/h · 3 m c.a. | Marca di prova | PRV-RIC-08
   | VE-01 | Vaso di espansione | 80 l | Marca di prova | PRV-VE-80
   | VE-02 | Vaso di espansione sanitario | 35 l | Marca di prova | PRV-VES-35
   nella tabella: 0 — il piu' vicino: simbolo valve-safety-pdc-1-water-supply a 30.4 mm
   rispetto a main: simboli fermi (96), tratte uguali (56), sigle nuove ['VE-01', 'VE-02'], sigle di main spostate o tolte []
   DXF: linee 19/19 uguali, testi 60/60 uguali
   deterministico: SVG uguale (ef2dfcface270188), DXF uguale (78bfe334eba0e559)
   preflight: nessun rilievo · regole: ['SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER']

== tavola-6 — grafo-completo-6.json, formato A2
   tabella 102.5 x 60 mm in (10, 16), colonne [12.5, 37.5, 20.0, 15.0, 17.5]
   | GT-01 | Caldaia modulare a condensazione | 150 kW | Marca di prova | PRV-CAL-150
   | GT-02 | Pompa di calore aria-acqua di alta potenza | 120 kW | Marca di prova | PRV-PDC-120
   | GT-03 | Collettore solare | – | Marca di prova | PRV-SOL-10
   | VOL-01 | Volano termico a quattro attacchi | 1000 l | Marca di prova | PRV-VOL-1000
   | BOL-01 | Bollitore ACS a due serpentini | 1500 l | Marca di prova | PRV-BOL-1500
   | CIR-01 | Pompa di circolazione nr 1 | 4 m³/h · 50 kPa | Marca di prova | PRV-CIR-40
   | CIR-02 | Pompa di circolazione nr 2 | 6 m³/h · 60 kPa | Marca di prova | PRV-CIR-60
   | CIR-03 | Pompa di circolazione solare | 1,2 m³/h · 5 m c.a. | Marca di prova | PRV-CSO-12
   | VE-01 | Vaso di espansione | 105 l | Marca di prova | PRV-VE-105
   | VE-02 | Vaso di espansione solare | 25 l | Marca di prova | PRV-VSO-25
   | VE-03 | Vaso di espansione sanitario | 35 l | Marca di prova | PRV-VES-35
   nella tabella: 0 — il piu' vicino: sigla GT-02 a 52.2 mm
   rispetto a main: simboli fermi (79), tratte uguali (48), sigle nuove ['BOL-01', 'CIR-01', 'CIR-02', 'CIR-03', 'GT-01', 'GT-02', 'GT-03', 'VE-01', 'VE-02', 'VE-03', 'VOL-01'], sigle di main spostate o tolte []
   DXF: linee 19/19 uguali, testi 60/60 uguali
   deterministico: SVG uguale (3dbb10d665f66c9c), DXF uguale (b0787b7adf4cce0f)
   preflight: nessun rilievo · regole: ['HIGHWAY_IS_NOT_STRAIGHT', 'SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER', 'SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER']

== tavola-1-senza-dati — grafo-completo-1.json, formato A3
   tabella 85 x 30 mm in (10, 16), colonne [12.5, 30.0, 20.0, 10.0, 12.5]
   | PDC-01 | Pompa di calore aria-acqua nr 1 | – | – | –
   | PDC-02 | Pompa di calore aria-acqua nr 2 | – | – | –
   | ACC-01 | Accumulo combinato | – | – | –
   | CIR-01 | Pompa di circolazione | – | – | –
   | VE-01 | Vaso di espansione | – | – | –
   nella tabella: 0 — il piu' vicino: simbolo valve-safety-pdc-master-water-supply a 57.6 mm
   DXF: linee 13/13 uguali, testi 30/30 uguali
   deterministico: SVG uguale (b6b097a3bbc9f42b), DXF uguale (6a5708afc97424ff)
   preflight: nessun rilievo · regole: ['SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER']
```

**Criterio 0 — le tavole, per prime**: in testa a questo rapporto, sei più una, in PDF e in DXF.

**Criterio 1 — la tabella dice quello che il PO ha approvato**: le proposte sono in §1 e in **D-192**,
in stato *Proposta*. Si chiude col giudizio del PO sulle tavole.

**Criterio 2 — niente dati inventati**: la prova
`test_una_cella_senza_dato_nel_grafo_resta_vuota` pretende che sul grafo dell'impianto 1 com'è agli
atti caratteristiche, marca e modello siano vuoti su ogni riga e che la tavola scriva tre trattini per
riga e nessun numero con unità; `test_un_dato_scritto_a_parole_non_entra_nella_tabella`, che la
potenza scritta come testo libero nel grafo dell'impianto 6 («120 kW») non venga letta.

**Criterio 3 — il disegno non passa sulla tabella**: nel collaudo qui sopra, «nella tabella: 0» su
tutte le tavole, e il pezzo più vicino a 7,5 mm (tavola 2) o più; la prova
`test_sulle_sei_tavole_approvate_il_disegno_non_passa_sulla_tabella` lo pretende sulle sei, con lo
stacco di 5 mm, senza il rilievo e senza bloccanti. **E il disegno non si è spostato**: simboli e tratte
identici a quelli di `main` su tutte e sei; le sole differenze sono le sigle nuove di §3.1.

**Criterio 4 — nel DXF la tabella c'è**: «DXF: linee … uguali, testi … uguali» nel collaudo — ogni
linea e ogni testo del layer `M-ANNO-SCHD`, riletti dal file, coincidono con quelli dell'SVG —, e la
prova `test_nel_dxf_la_tabella_c_e_sul_suo_layer_uguale_all_svg`.

**Criterio 5 — deterministico**: «deterministico: SVG uguale, DXF uguale» nel collaudo, due esecuzioni
separate; la prova `test_lo_stesso_piano_da_la_stessa_tavola_svg_e_dxf`.

**Criterio 6 — la suite**:

@@SUITE@@

## 5. Che cosa ho toccato fuori dal perimetro scritto, e perché

- **`validation/preflight.py`**: il rilievo `DRAWING_OVER_THE_EQUIPMENT_TABLE` e la tabella nel conto di
  `SHEET_LARGER_THAN_NEEDED` e del margine dal bordo. Il pacchetto chiedeva di misurare che il disegno
  non passi sulla tabella; D-158 vuole che un vincolo della posa abbia un rilievo sulla tavola finita.
- **`layout/labels.py`**: sigle e indirizzi evitano la tabella — è «farle spazio» —, e i pezzi della
  tabella non ripetono i loro dati accanto al simbolo (D-192, punto 7).
- **`layout/addresses.py`**: gli indirizzi della verifica evitano la tabella.
- **`skill/capire/COSA_DECIDE.md`**: una riga diceva che «che marca è» non è una domanda legittima;
  resta vero per le regole, e adesso lo dice, rimandando alla voce della tabella.

**Non toccato, e da fare in un pacchetto suo**: le istruzioni del pianificatore (`skill/comporre/`)
non nominano la tabella. Il rilievo dice già «il foglio è troppo piccolo per questo disegno»; una riga
accanto a quella sulla legenda (§D3) lo renderebbe esplicito. La via senza piano — `disegnatore-mep
draw` — non porta la tabella: è la via che D-151 ha tolto dalla decisione della posa.

## 6. Domande al PO

1. **Le tavole vanno bene?** Righe, codice, «nr», caratteristiche, trattino, grafica, posto (§1).
2. **Le sigle dei generatori senza sigla nel testo**: GT-01, GT-02… come oggi, o una famiglia per tipo
   di macchina — PDC, CAL, SOL — anche quando il testo non la dà? (§3.2)
