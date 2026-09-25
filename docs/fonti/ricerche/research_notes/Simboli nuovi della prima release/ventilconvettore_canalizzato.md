# Ventilconvettore canalizzato — ricognizione delle fonti

> **Note di un agente di ricerca, 24 settembre 2026** (`REL-003`, agenti paralleli in sessione, D-152), riportate come le ha scritte. Quello che un agente riferisce non è una fonte finché la sessione non l'ha guardato: la sessione ha **riaperto i ritagli delle fonti da cui vengono le forme** e ha **riscaricato ogni fonte registrata** (SRC-030 … SRC-040, SRC-009) dall'indirizzo citato, controllando la pagina. **Nel repository ci sono soltanto i ritagli elencati nel rapporto** (`docs/fonti/ricerche/reports/Simboli nuovi della prima release.md`). Gli altri nomi di ritaglio citati qui sotto, e le cartelle di lavoro dell'agente (`work/`, `_work/`, `_download_non_pubblicare/`), sono rimasti fuori: pagine intere, figure intere, o tavole che ne vietano la riproduzione (Division Energia, Comune di Parma). Si rigenerano dalla fonte, alla pagina indicata.

Ricerca svolta il 24 settembre 2026 per `REL-003` (I-124, D-184). Prefisso dei ritagli: `fancoil`.

**Metodo.** Ogni segno descritto qui è stato guardato: pagina PDF rasterizzata con PyMuPDF e,
dove il PDF è vettoriale (Palermo, Sapienza), misurato sui vettori; nei PDF scansionati (Guerra,
UniFe) le misure sono prese sui pixel a 400–600 dpi. I ritagli sono in questa cartella; quelli
fatti di più riquadri (intestazione + segno + riga di legenda) sono composti **dalla stessa
pagina** con `show_pdf_page`, senza ritocchi, e l'ordine dei riquadri è scritto qui sotto.
Unità delle misure: pt = punto PDF (1/72 di pollice).

**Attenzione:** la sottocartella `_work/` contiene i PDF scaricati, le pagine intere rasterizzate
e gli script di ritaglio. Serve solo per rifare le misure: **non va copiata nel repository**
(pagine intere di documenti protetti). I ritagli composti si rigenerano da questa cartella con
`python _work/compose.py _work/spec_fNN.json <uscita>.png <dpi>` (specifiche `spec_f06` … `spec_f14`;
i Guerra composti con `spec_g5.json` e `spec_g6.json`).

Natura della fonte: [NORMA-2] norma tramite fonte secondaria · [PUBBLICO] elaborato di progetto
pubblico · [COSTRUTTORE] · [DIDATTICA].

---

## 1. UNI 9511 tramite «Tabelle utili — Norma UNI 9511, Segni grafici» (prof. Guerra) — SRC-015 [NORMA-2]

- URL: <https://professoreguerra.altervista.org/alterpages/files/UniIdraulica1.pdf> — 10 pagine
  scansionate (metadati: Acrobat PDFMaker per PowerPoint, gennaio 2003); ogni pagina porta in
  testa «TABELLE UTILI» e in piede «18 — IDRAULICA». Editore non indicato.
- **PDF p. 2** «Apparecchiatura per la distribuzione di acqua, gas e vapore»:
  - «Ventilconvettore»: riquadro orizzontale con le due diagonali da angolo ad angolo (una X).
    Misurato 38,9 × 11,7 pt, rapporto ≈ 3,3 : 1. Nessun attacco, nessuna freccia.
  - «Ventilconvettore con presa d'aria esterna»: stesso riquadro (38,9 × 10,8 pt) con sopra una
    **freccia verticale a punta aperta rivolta verso il basso**, centrata sull'asse del riquadro
    (x = 417 pt in entrambi), lunga ≈ 18 pt (≈ 1,6 volte l'altezza del riquadro) e staccata dal
    lato superiore di ≈ 4–5 pt. È l'unico segno della famiglia che disegna un collegamento d'aria:
    una freccia sul lato lungo, non un raccordo.
  - Nessun segno per ventilconvettore «canalizzato», «da incasso» o «a controsoffitto».
  - Ritaglio: `fancoil_01_guerra-uni9511-p2-ventilconvettore.png`.
- **PDF p. 5** «Canali, accessori e componenti per il trattamento e la distribuzione dell'aria»
  (ritaglio `fancoil_03_guerra-uni9511-p5-canali-giunto-bocchette.png`, due riquadri della stessa
  pagina: sopra sezioni dei canali e senso del flusso, sotto giunto antivibrante e bocchette):
  - «Canale di mandata — sezione visibile»: sezione rettangolare con X o circolare con X;
    «Canale di estrazione»: con una sola diagonale; «sezione nascosta»: a tratteggio.
  - «Senso del flusso»: punta aperta su una linea unifilare, oppure freccia dentro il canale a
    doppia linea con i segni di interruzione alle estremità.
  - «Giunto antivibrante»: breve tratto a soffietto (due verticali con piccole ondulazioni) fra
    due canali a doppia linea.
  - «Bocchetta di mandata»: freccia perpendicolare al canale, uscente, con una barretta alla
    base; «Bocchetta (o griglia) di ripresa»: freccia entrante verso il canale.
- **PDF p. 6** «Apparecchiature per il trattamento e la distribuzione dell'aria» (ritaglio
  `fancoil_04_guerra-uni9511-p6-apparecchi-aria.png`, due riquadri: ventilatore e filtro dalla
  colonna sinistra, batterie e cassette terminali dalla destra):
  - «Ventilatore»: cerchio con triangolo («il senso del flusso è indicato dalla posizione del
    vertice del triangolo»), un tratto di linea a sinistra e uno a destra.
  - «Filtro per aria»: rettangolo verticale con zig-zag, tratti a sinistra e a destra.
  - «Batteria di riscaldamento» / «di raffreddamento»: rettangolo verticale con un cerchio e
    «+» / «−», tratti a sinistra e a destra.
  - «Cassetta terminale miscelatrice» (M), «di postriscaldamento» (PR, con una doppia verticale
    sul lato destro), «per impianti a portata d'aria variabile» (PV): riquadro con la sigla e **un
    tratto di canale unifilare su ciascuno dei due lati opposti**, all'altezza del centro (due
    tratti in ingresso per la miscelatrice). Misurato su M e PV: riquadro largo 18,2 pt, tratti di
    11,6–12,1 pt per lato (≈ 2/3 della larghezza del riquadro).
  - È la convenzione UNI 9511 per un apparecchio montato su un canale: gli attacchi d'aria sono
    **tratti di canale su due lati opposti, lungo l'asse del flusso**. Nessuno di questi apparecchi
    ha attacchi d'acqua disegnati.

## 2. UNI 9511 tramite la dispensa «simbologie fornite», Università di Ferrara — SRC-015 [NORMA-2]

- URL: <https://docente.unife.it/graziano.trippa/materiale-didattico-e-avvisi-lca1-2009-2010-corso-a/SIMBOLOGIA%20def.pdf/at_download/file>
  — 3 pagine (PDF del 29/12/2009, corso LCA1 a.a. 2009-2010). Le immagini sono dichiarate «tratte
  da Milone E., Nicoletti M., Perris (a cura di), *Il Nuovissimo manuale dell'Architetto*, Sez. A,
  pp. 37-44, Mancosu, Roma 2008», con richiamo a UNI 9511 parti 1-5 (dicembre 1989).
- **PDF p. 3**, tabella «b) Corpi scaldanti prescelti», righe «Ventilconvettore» e
  «Ventilconvettore con presa d'aria esterna»: stesso disegno della fonte 1 — riquadro con X
  (30,8 × 9,7 pt, ≈ 3,2 : 1); per la presa d'aria esterna riquadro con X e freccia verticale verso il
  basso, centrata; qui la freccia **tocca** il lato superiore (nessuno stacco misurabile).
  Seconda riproduzione indipendente: conferma forma e denominazioni.
- Ritaglio: `fancoil_02_unife-uni9511-ventilconvettore.png`.

## 3. UNI 9511 nelle tavole Oppo — SRC-016 [NORMA-2] — **nessun segno**

- Indice <https://www.oppo.it/disegni/a_disegni-elenco.html>: dieci tabelle. Guardate le immagini
  della Tab. 1 «Tubazioni, canalizzazioni» (tubazioni, senso del flusso, incroci, tubi flessibili),
  della Tab. 4 (pozzetti, scarichi) e della Tab. 9 «Simboli letterali di identificazione dei
  componenti di impianto» (solo scarichi e ventilazione: SM, PL, SAU, SAN, SAI, V, VP, VS, F, P,
  PI, I, VA, VD, PU, PM, SO, SG). Le altre tabelle solo dai titoli (giunzioni, valvolame, sonde,
  grandezze, simboli letterali, fluidi, indicatori). **Oppo non riproduce le apparecchiature:
  nessun ventilconvettore, nessun apparecchio d'aria.** Nessun ritaglio.

## 4. CT Energia / Tiemme Sistemi — «Linea guida impianti termotecnici, capitolo 1°», Ing. G. Loffredo — SRC-011 [DIDATTICA]

- URL: <https://www.ctenergia.it/wp-content/uploads/downloads/2014/04/00-Lez.-cap.-1-segni-grafici-nella-rappr.-componenti.pdf>
  — 33 pagine (aprile 2014). **PDF p. 29** «Segni convenzionali componentistica termoidraulica».
- «fan-coil»: rettangolo vuoto, 47,4 × 34,6 pt (≈ 1,4 : 1), senza X, senza attacchi, senza
  frecce. Nessuna versione canalizzata.
- Ritaglio: `fancoil_05_ctenergia-p29-fancoil.png`.

## 5. Palermo, Stazione Politeama — «Impianto HVAC — Schema funzionale e di regolazione», progetto esecutivo [PUBBLICO]

- «Primo lotto funzionale chiusura dell'anello ferroviario in sotterraneo nel tratto di linea tra
  le stazioni di Palermo Notarbartolo e Giachery e proseguimento fino a Politeama» — «Stazione
  Politeama — Impianti tecnologici — Impianto HVAC — Schema funzionale e di regolazione»,
  elaborato RS72 01 E ZZ DX FV0309 001, rev. B del 19.09.11 («Emesso a seguito istruttoria
  Italferr»). Committente Comune di Palermo; progettazione ATI (nel cartiglio Progin S.p.A.);
  redatto R. Ciano, verificato R. Piccirillo, approvato S. Esposito.
- URL: <https://docs.comune.palermo.it/js/server/uploads/grandiopere/RS7201EZZDXFV0309001B.pdf>
  — **PDF p. 1** (tavola unica 5036 × 2443 pt, AutoCAD, vettoriale).
- Nella **stessa tavola** ci sono tre tipi di ventilconvettore: «(2) VENTILCONVETTORI CANALIZZABILI A
  SOFFITTO» (Sala relè, sigle CDZ-04a/b), «(2) VENTILCONVETTORI A SOFFITTO» (Locale UPS, sigle
  CDZ-01a/b), «VENTILCONVETTORE A PAVIMENTO» (Locale D.M., sigla FC).
- **Canalizzabile (CDZ-04a)**, misure sui vettori: corpo rettangolare orizzontale 102,4 × 54,3 pt
  (≈ 1,9 : 1), diviso da verticali in tre sezioni in fila lungo il flusso — filtro (14,8 pt, due
  pannelli a zig-zag), batteria (17,6 pt, con dentro il segno UNI 9511 della batteria di
  raffreddamento, cerchio con «−»), ventilatore (70,0 pt, coclea di centrifugo disegnata in modo
  figurativo, con un pannellino di comando in alto a sinistra).
  **Aria**: freccia «vuota» (a blocco, solo contorno, ≈ 12,6 × 14,4 pt), staccata dal corpo,
  entrante sul lato sinistro; attaccata al lato destro una **serranda servocomandata** (riquadro
  12,6 × 25,9 pt con la pala inclinata e, sopra, il servocomando «M» 13,7 × 13,7 pt), poi una
  seconda freccia vuota uscente, con la scritta «MANDATA».
  **Acqua**: due linee spesse (1,44 pt; una continua, una a tratto finissimo) escono dal **lato
  inferiore della sezione batteria**, a 8,8 pt l'una dall'altra, e scendono alla valvola a tre vie.
  **Nessun collare, nessun plenum, nessun canale disegnato.**
- **A soffitto (CDZ-01a)**: corpo identico, stesse frecce vuote, stessa scritta «MANDATA», **senza
  la serranda**. La differenza grafica fra canalizzabile e non canalizzabile è tutta qui: la
  serranda servocomandata sulla mandata e la parola «CANALIZZABILI» nell'intestazione del locale.
  Entrambi sono prescritti «marca SABIANA - mod. OCEAN 2 o equivalente approvato», portata
  1.600 m³/h il canalizzabile, 1.300 m³/h l'altro.
- **A pavimento (FC)**, per confronto (guardato, non ritagliato): segno diverso — riquadro con
  «FC», tratteggi orizzontali, zig-zag della batteria elettrica, regolatore «REG» sopra; nessuna
  freccia d'aria.
- **Legenda** (ritaglio): «CDZ — UNITA' DI TRATTAMENTO ARIA OVER DI PRECISIONE DA AMBIENTE»,
  «VENT — VENTILATORE DI ESTRAZIONE CASSONATO», «FC — FAN-COIL DEL TIPO VERTICALE CARENATO», e il
  segno «SERRANDA SERVOCOMANDATA» (riquadro verticale con la pala, servocomando «M» sopra).
  **La legenda non ha una voce per i ventilconvettori a soffitto né per i canalizzabili**: la sigla
  CDZ è usata sia per i condizionatori di precisione sia per i ventilconvettori, e il carattere
  «canalizzabile» sta solo nell'intestazione del locale.
- Ritagli: `fancoil_06_palermo-politeama-canalizzabile.png` (intestazione della Sala relè +
  unità CDZ-04a), `fancoil_07_palermo-politeama-a-soffitto.png` (intestazione del Locale UPS +
  unità CDZ-01a), `fancoil_08_palermo-politeama-legenda.png` (righe CDZ, VENT, FC + riga
  «serranda servocomandata»). Tutti e tre composti da due riquadri della stessa tavola.

## 6. Sapienza Università di Roma — tavola IM 04 «Impianto di climatizzazione — Schema funzionale altimetrico», progetto esecutivo [PUBBLICO]

- «Intervento di ristrutturazione dei locali presso il terzo piano dell'edificio "Caglioti" CU032
  da destinare a laboratori per il Dipartimento di Chimica e Tecnologia del Farmaco», progetto
  esecutivo, tavola IM 04, novembre 2018. Stazione appaltante Università degli Studi di Roma «La
  Sapienza»; progettista e CSP Ing. Leonardo Miozzi.
- URL: <https://web.uniroma1.it/gareappalti/sites/default/files/IM_04_Impianto%20di%20climatizzazione%20-%20Schema%20funzionale%20altimetrico.pdf>
  — **PDF p. 1** (1684 × 2384 pt; disegno ruotato di 90° sul foglio; vettoriale, testi in curve).
- **UTN-01** (nel controsoffitto del laboratorio), misure sui vettori: riquadro grigio orizzontale
  90,8 × 28,4 pt (≈ 3,2 : 1) con righe interne orizzontali e un riquadro blu dentro (il riquadro blu
  è anche il segno di legenda).
  **Acqua**: le due tubazioni — blu con la punta rivolta verso l'unità (mandata) e azzurra con la
  punta in uscita (ritorno), secondo le punte sulle linee — ciascuna con una valvola a sfera,
  entrano **entrambe dall'estremità sinistra** del riquadro, una sopra l'altra.
  **Aria**: dalle due estremità, in basso, partono due canali di mandata disegnati come **linea
  unifilare rossa** (≈ 35 pt in orizzontale, poi ≈ 8 pt in discesa) fino a due bocchette
  (rettangolini rossi 22,7 × 4,2 pt sulla linea del controsoffitto); sotto ciascuna bocchetta **due
  frecce vuote** divergenti verso il basso con la sigla «A_M»; sotto il riquadro **due frecce
  vuote rivolte verso l'alto**, verso l'unità: la ripresa dal locale, senza canale. A sinistra,
  sopra il canale, entrano i tubi: la stessa estremità porta acqua e aria.
- **Legenda**: «UTN-01 / UTN-02 — UNITÀ INTERNA TERMOVENTILANTE: VENTILCONVETTORE PER
  INSTALLAZIONE A VISTA IN POSIZIONE VERTICALE, COMPLETO DI MOBILE DI COPERTURA, PANNELLO DI
  COMANDO VELOCITÀ E TERMOSTATO INCORPORATI, FILTRO ARIA, BATTERIA PER ACQUA CALDA O REFRIGERATA.
  PORTATA D'ARIA 1200 mc/h, resa raffreddamento 6,30 kW, resa riscaldamento 8,10 kW»; «A_M — ARIA
  TRATTATA DI MANDATA IN AMBIENTE: BOCCHETTA DI MANDATA A DOPPIO ORDINE DI ALETTE … PORTATA D'ARIA
  600 mc/h».
- **La legenda e il disegno non stanno insieme**: la legenda dice «a vista, in posizione verticale,
  con mobile di copertura», il disegno mette l'unità nel controsoffitto con due canali di mandata.
  Per la forma conta il disegno; il testo di legenda non è affidabile per il tipo di apparecchio.
- **Contrasto nella stessa tavola — FC-01** (ventilconvettore esistente dell'ufficio, «allaccio
  alla rete esistente»): riquadro con gli angoli arrotondati appoggiato al pavimento, tubazioni
  che scendono dall'alto sul suo lato sinistro, **due frecce vuote divergenti verso l'alto che
  escono dalla sommità dell'apparecchio**: l'aria esce dall'apparecchio, non da una bocchetta.
- Ritagli: `fancoil_09_sapienza-im04-utn-controsoffitto.png` (tre riquadri della stessa tavola,
  ruotati per la lettura: UTN-01 ingrandito 2,6 volte, riga di legenda UTN, riga di legenda A_M);
  `fancoil_10_sapienza-im04-fc01-a-pavimento.png`.

## 7. Sabiana — «MTL / MTL-ECM, Ventilconvettori canalizzabili Maestro», catalogo 99A4340000L, 04/2026 [COSTRUTTORE]

- URL (sito ufficiale): <https://www.sabiana.it/sites/default/files/translation-editor/2026-05/Maestro_MTL_MTL-ECM_IT_cat_99A4340000L_Rev_04_2026.pdf>
  — 96 pagine; **PDF p. 26 e p. 89** (la numerazione stampata coincide). Gli stessi disegni ci sono
  nell'edizione 12/2021, vista su una copia di rivenditore che non cito.
- **p. 26** «Dimensioni, pesi e contenuti acqua — Esecuzione sinistra (standard)»: vista della
  fiancata con i quattro attacchi d'acqua numerati come cerchi (1 ingresso e 2 uscita batteria
  principale, 3 e 4 batteria addizionale), raggruppati verso il lato filtro; ai due lati della
  vista due frecce vuote «F.A.» (flusso aria) orizzontali, nello stesso verso: l'aria entra dal
  «LF = lato filtro (aspirazione)» ed esce dal «LV = lato ventilatori (mandata)». **Le due bocche
  dell'aria stanno su facce opposte; gli attacchi dell'acqua sulla fiancata, perpendicolare a
  entrambe.** Nella prospettiva «Standard»: «Attacchi idraulici a sinistra guardando la direzione
  dell'aria»; l'esecuzione destra è «su richiesta».
- **p. 89** «Accessori optional»:
  - «Plenum di mandata/ripresa con codoli PMM — Plenum di mandata e/o aspirazione con diffusori
    circolari a 3 codoli (Grandezze 1-2-3) o a 4 codoli (Grandezze 4-5-6-7)». Vista frontale:
    rettangolo A × C (1133 × 298 mm per le taglie 1-2, ≈ 3,8 : 1) con tre cerchi alti quasi quanto
    il plenum (codoli Ø 250 mm; Ø 300–355 per le taglie grandi). Vista dall'alto: rettangolo A × B
    con **tre brevi rettangoli che sporgono di 40 mm** da un lato lungo — così appare il collare
    in proiezione. Vista laterale: il plenum con il codolo di 40 mm.
  - «Giunto antivibrante GAV — da installare in mandata e/o aspirazione, composto da doppia
    cornice in lamiera zincata e da un giunto flessibile in PVC»: cornice rettangolare A × B,
    profondità 110 mm, con le ondulazioni del soffietto nella vista laterale.
- Ritagli: `fancoil_11_sabiana-mtl-attacchi-e-flusso-aria.png` (tre riquadri di p. 26: vista con
  attacchi e frecce F.A., elenco delle sigle, prospettiva «Standard»);
  `fancoil_12_sabiana-mtl-plenum-codoli-giunto.png` (quattro riquadri di p. 89: titolo e disegno
  del PMM, titolo e disegno del GAV).

## 8. Aermec — manuale VES_I e scheda VED_I [COSTRUTTORE]

- «Ventilconvettore per installazione canalizzata, orizzontale e verticale — Manuale d'uso e
  installazione — VES_I», codice 2509 - 5799500_06. URL (sito ufficiale):
  <https://www.aermec.com/download/?id=6239> — 36 pagine.
  - **PDF p. 8**, «Componenti principali» (guardato, non ritagliato): «1 Mandata dell'aria» e «21
    Flangia di mandata dell'aria» su una faccia lunga; «17 Filtro dell'aria (aspirazione)» e «16
    Ventilatore centrifugo» su un'altra faccia; «4 Collegamenti idraulici (uscita acqua)» e «7
    (ingresso acqua)» sulla «10 Fiancata sinistra».
  - **PDF p. 9**, testo: «Le bocche di aspirazione e di mandata sono realizzate per raccordare il
    ventilconvettore a ogni tipo di canalizzazione dell'aria. […] La bocca di mandata comprende la
    flangia di raccordo»; «I collegamenti, posizionati nella fiancata sinistra, sono ad attacco
    femmina. È prevista la possibilità di ruotare la batteria per portare gli attacchi sul lato
    destro».
  - **PDF p. 9**, «7. Esempi di impianto» (legenda: SW sonda acqua, VC/F valvola riscaldamento/
    raffrescamento, VC valvola riscaldamento, SA sonda ambiente, C/F e C batteria): schemi
    figurativi della **sola batteria**, in prospettiva, con i due attacchi dell'acqua **sullo
    stesso lato** (in alto e in basso sul collettore) e tubazioni orizzontali con frecce vuote di
    mandata e ritorno, valvola a tre o a due vie; l'aria è una **freccia vuota con la scritta
    «AIR»** che attraversa il pacco alettato. Mantello, ventilatore e raccordi dei canali non sono
    disegnati.
  - Ritaglio: `fancoil_14_aermec-ves-esempi-impianto.png` (titolo e legenda + i tre esempi
    «Impianto 2 tubi con sonda acqua», due riquadri della stessa pagina).
- Solo testo, stessa marca: scheda VED_I (VED-530-741-I_I_UN50_09),
  <https://www.aermec.com/download/?id=15374>, PDF pp. 3–4: accessori «Plenum di aspirazione con
  flangia rettangolare» / «con flange circolari», «Plenum di mandata isolato internamente con
  flangia rettangolare» / «con flange circolari», «Kit flangia circolare per plenum (KFV)», «MZC —
  Plenum con serrande motorizzate». Nessun disegno nella scheda. È il lessico del costruttore per i
  raccordi: **flange** circolari o rettangolari, dove Sabiana dice **codoli**.

## 9. Caleffi — Quaderni Caleffi, M. Doninelli, «I circuiti e i terminali degli impianti di climatizzazione» [COSTRUTTORE, DIDATTICA]

- URL: <https://www.caleffi.com/sites/default/files/media/external-file/I%20circuiti%20e%20i%20terminali%20degli%20impianti%20di%20climatizzazione_IT.pdf>
  — 170 pagine, PDF del 2001 (metadati).
- **PDF p. 156** (p. 144 stampata), «Classificazione» dei ventilconvettori: «in base al luogo di
  messa in opera: a pavimento, a parete, a controsoffitto, a soffitto»; «secondo il tipo di
  protezione: con mobiletto, ad incasso»; «in relazione alle caratteristiche del flusso d'aria: a
  percorso libero, a percorso canalizzato».
- **PDF p. 158** (p. 146 stampata), figura «Ventilconvettore a controsoffitto»: **sezione
  costruttiva, non segno di schema**. Apparecchio sospeso al solaio con due tiranti nel vano del
  controsoffitto; da sinistra filtro (campitura verticale), ventilatore centrifugo (coclea),
  batteria inclinata con la bacinella sotto; sul lato destro **un raccordo rastremato** porta alla
  **griglia di mandata** (campita) nella veletta verticale; nel controsoffitto, a sinistra, un
  secondo elemento campito che è verosimilmente la griglia di ripresa, con l'aria che passa per il
  vano (lo deduco dal disegno: nessuna scritta lo dice). Nessuna freccia, nessun attacco d'acqua
  disegnato.
- Ritaglio: `fancoil_13_caleffi-quaderno-controsoffitto.png`.

---

## Fonti guardate e scartate

- **ANAS**, progetto definitivo «Area esazione Collegamento A26 — Fabbricati di stazione —
  Impianti meccanici», tavola T00_PS01_IMP_DI04_A, 1:50 (procedura VIA MiTE,
  <https://va.mite.gov.it/File/Documento/340264>): la «Legenda simboli impianto di
  climatizzazione» ha solo il «ventilconvettore a mobiletto».
- **Aermec**, «Esempi di calcolo impiantistico — Impianto a ventilconvettori per uffici» (2004,
  copia didattica su energiazero.org): legenda di pianta «Ventilconvettore» = rettangolo campito
  con esagono della sigla; apparecchi a mobiletto. «Impianto a tutta aria» (2004): UTA.
- **Innova**, schemi d'impianto eHPoca (<https://rep.innova.it/downloads/disegni/ehpoca_-file_pdf_rev02.zip>):
  «FAN-COIL AIRLEAF» e «FILOMURO» a parete, in prospettiva frontale, attacchi a sinistra; nessun
  canalizzato. Le tavole dimensionali DUCTO sono solo DWG: non lette.
- **Caleffi**, *Idraulica* 25 (dic. 2003), p. 18 «Terminali di climatizzazione — cartella 40»:
  ventilconvettori a parete e a soffitto (tradizionale, a cassetta), nessun canalizzato; frecce
  vuote per presa e invio aria. Guardato sulla copia idroenergiaitalia; l'URL ufficiale
  <https://www.caleffi.com/sites/default/files/certification_contracts/idraulica_25_it.pdf>
  risponde 403 a questo client. *Idraulica* 57 (dic. 2019), Fig. 24: ventilconvettori a parete;
  *Idraulica* 63 (gen. 2023): VMC.
- **Beretta**, «Schema di impianto puramente indicativo» (2021): ventilconvettori a parete.
- **Sapienza**, e-learning, «TAV 05 Fan coil piano primo» (esercitazione di studenti, a.a.
  2015-16): il «fan coil in controsoffitto» è una cassetta a quattro vie.
- **Città metropolitana di Bologna** IM06 e **Comune di Rivarolo Canavese** E.8I: VMC;
  **Università di Trieste**, schema funzionale CT e CF: solo centrale.
- **Daikin**, catalogo unità fan coil 2025: solo tabelle, nessun disegno di plenum.
- Non raggiungibili: Aermec `SPAECLI39.pdf` (link morto, nessuna copia Wayback); Purmo
  «Ventilconvettori e unità termoventilanti canalizzabili» (404).
- **Norme internazionali**: EN 12792:2003 «Ventilation for buildings — Symbols, terminology and
  graphical symbols» (sostituisce DIN 1946-1): nessuna anteprima pubblica delle tabelle dei simboli
  trovata. ISO 14617 e ANSI/ASHRAE 134 non consultate. **Non verificato** se contengano un segno
  per il ventilconvettore canalizzato.

---

## Sintesi

### C'è una forma ricorrente?

**Un segno normato del ventilconvettore canalizzato non c'è** nelle fonti viste: UNI 9511 (due
riproduzioni) ha il ventilconvettore — riquadro orizzontale con X, ≈ 3,3 : 1 — e il ventilconvettore
con presa d'aria esterna — lo stesso con una freccia verticale sul lato lungo superiore —, niente
di più. Le due tavole pubbliche disegnano il canalizzato in due modi diversi. Quello che si ripete:

1. **Corpo**: rettangolo orizzontale (UNI 9511 3,3 : 1; Sapienza 3,2 : 1; Palermo 1,9 : 1 perché
   disegna le sezioni interne; CT Energia 1,4 : 1).
2. **Aria su due facce opposte**, in fila lungo l'asse lungo: Palermo (entra a sinistra, esce a
   destra), Sabiana (LF → LV), Caleffi (mandata da un lato; la ripresa dall'altro è dedotta dal
   disegno), UNI 9511 per ogni
   apparecchio montato sui canali (tratti di canale su due lati opposti). Eccezione: Sapienza,
   mandata dalle due estremità e ripresa dal basso.
3. **Frecce dell'aria vuote** (a blocco, solo contorno): Palermo, Sapienza, Sabiana «F.A.», Aermec
   «AIR». La UNI 9511 usa invece frecce a punta aperta su una linea (presa d'aria esterna, senso del
   flusso, bocchette).
4. **Acqua su un lato solo**, raggruppata: Sabiana e Aermec sulla fiancata sinistra (a richiesta
   destra), perpendicolare alle bocche dell'aria; Sapienza dall'estremità sinistra; Palermo dal
   fondo della sezione batteria.
5. **Il carattere «canalizzato» sta soprattutto nelle scritte** — «VENTILCONVETTORI CANALIZZABILI A
   SOFFITTO» a Palermo, la posizione «controsoffitto» a Sapienza — e nella posizione del disegno;
   graficamente Palermo aggiunge solo la serranda servocomandata sulla mandata, Sapienza disegna i
   canali fino alle bocchette.
6. **I collari**: nessuna delle due tavole pubbliche li disegna. Compaiono nei disegni dei
   costruttori — Sabiana: codoli circolari che sporgono 40 mm da un plenum; Aermec: flange circolari
   o rettangolari, flangia di mandata — e, come convenzione per «un canale attaccato a un
   apparecchio», nei tratti unifilari della UNI 9511 sugli apparecchi d'aria (≈ 2/3 della larghezza
   del riquadro, su due lati opposti).

### Varianti

- (a) **Sezione tipo UTA** — filtro, batteria col segno UNI «−», ventilatore, frecce vuote, serranda
  se canalizzabile (Palermo, `fancoil_06`/`07`).
- (b) **Riquadro semplice nel controsoffitto + canali unifilari + bocchette + frecce vuote**, acqua da
  un'estremità (Sapienza, `fancoil_09`).
- (c) **Riquadro con X** della UNI 9511, senza variante canalizzata; con presa d'aria esterna, una
  freccia verso il lato lungo superiore (`fancoil_01`, `fancoil_02`).
- (d) **Rettangolo vuoto** «fan-coil» (CT Energia, `fancoil_05`).
- (e) **Solo la batteria** con i due attacchi da un lato e la freccia «AIR» (Aermec, `fancoil_14`).

### Le fonti che la mostrano meglio

1. **Palermo, Stazione Politeama** (`fancoil_06`, `fancoil_07`, `fancoil_08`): nella stessa tavola il
   canalizzabile e il non canalizzabile; la differenza è la serranda sulla mandata e la scritta.
2. **Sapienza, IM 04** (`fancoil_09`, `fancoil_10`): riquadro semplice nel controsoffitto, acqua da
   sinistra, mandata canalizzata con frecce vuote; contro FC-01 a pavimento, che soffia dalla
   propria sommità.
3. **UNI 9511 tramite Guerra** (`fancoil_01`, `fancoil_03`, `fancoil_04`) insieme a **Sabiana MTL**
   (`fancoil_11`, `fancoil_12`): il segno della famiglia e la convenzione dei tratti di canale su due
   lati opposti; il collare fisico (codolo di 40 mm) e la disposizione acqua sulla fiancata, aria
   sulle facce opposte.

### Che cosa non ho trovato

- Nessun segno UNI 9511 per il canalizzato (due riproduzioni viste; il testo originale della norma,
  a pagamento, non l'ho consultato).
- Nessuno schema funzionale che disegni collari o raccordi sul simbolo del ventilconvettore.
- Nessuna planimetria di progetto pubblico con una voce di legenda «ventilconvettore canalizzato».
- Nessun costruttore che disegni il canalizzato come segno di schema: solo disegni dimensionali,
  prospettive e schemi della sola batteria.
- Nessuna anteprima di norme internazionali (EN 12792, ISO 14617, ASHRAE 134).

### Rilievi — tavole che sembrano sbagliate

- **Sapienza IM 04**: la legenda descrive UTN-01/02 come ventilconvettore «a vista, in posizione
  verticale, con mobile di copertura», mentre il disegno lo mette nel controsoffitto con due canali
  di mandata.
- **Palermo**: in legenda «CDZ = unità di trattamento aria over di precisione da ambiente», ma CDZ
  sigla anche i ventilconvettori a soffitto e canalizzabili, che in legenda non hanno una voce;
  inoltre gli attacchi d'acqua escono dal fondo della sezione batteria, non da un lato.

### Che cosa ne seguirebbe per il simbolo — inferenza, da decidere dal PO

Il PO ha fissato (D-184): porte dell'acqua su un lato solo, collari disegnati, nessuna tubazione
d'aria. I costruttori dicono che, sull'apparecchio vero, l'acqua sta sulla fiancata (Sabiana e
Aermec) e le due bocche dell'aria su due facce opposte, entrambe perpendicolari alla fiancata
(Sabiana): con l'acqua sul lato sinistro del simbolo, i due collari cadrebbero sul lato
superiore e su quello inferiore, uno di fronte all'altro. Sapienza però mette acqua e mandata sulla
stessa estremità, e Palermo l'acqua sul fondo: non c'è una regola unica. Per disegnare il collare le
fonti offrono tre modi: il tratto di canale unifilare della UNI 9511 (≈ 2/3 del lato), il codolo
Sabiana (rettangolino sporgente), la freccia vuota alla bocca (Palermo, Sapienza). Il corpo
potrebbe restare quello del ventilconvettore a vista del progetto o il riquadro con X della UNI
9511; nelle tavole viste il canalizzato si distingue comunque anche per la scritta in legenda.
La scelta fra questi è una convenzione grafica: resta al PO.
