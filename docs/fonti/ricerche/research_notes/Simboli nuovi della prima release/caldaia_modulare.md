# Caldaia modulare a condensazione: come la disegnano le fonti

> **Note di un agente di ricerca, 24 settembre 2026** (`REL-003`, agenti paralleli in sessione, D-152), riportate come le ha scritte. Quello che un agente riferisce non è una fonte finché la sessione non l'ha guardato: la sessione ha **riaperto i ritagli delle fonti da cui vengono le forme** e ha **riscaricato ogni fonte registrata** (SRC-030 … SRC-040, SRC-009) dall'indirizzo citato, controllando la pagina. **Nel repository ci sono soltanto i ritagli elencati nel rapporto** (`docs/fonti/ricerche/reports/Simboli nuovi della prima release.md`). Gli altri nomi di ritaglio citati qui sotto, e le cartelle di lavoro dell'agente (`work/`, `_work/`, `_download_non_pubblicare/`), sono rimasti fuori: pagine intere, figure intere, o tavole che ne vietano la riproduzione (Division Energia, Comune di Parma). Si rigenerano dalla fonte, alla pagina indicata.

Ricognizione del 24 settembre 2026, prefisso dei ritagli `modulare`.

## Perimetro e metodo

- Gli URL sono stati consultati il 24 settembre 2026. «PDF p.» è la pagina del file PDF,
  contata da 1; quando la numerazione stampata è diversa, la indico a parte.
- Ho aperto e guardato ogni ritaglio prima di descriverlo. `rifai_ritagli.py` li rigenera
  dalle copie locali, con il rettangolo di ritaglio e i dpi di ognuno. Rieseguito: **16 su
  16 identici** (md5).
- Le proporzioni citate vengono da `misure.py`, eseguito sulle geometrie vettoriali dei PDF.
  Per Guerra, che è una scansione, la misura è fatta su pixel con una soglia di grigio.
  L'output è riportato in fondo.
- In `_download_non_pubblicare/` ci sono le copie dei documenti e i render a pagina intera.
  Sono documenti interi protetti e **non vanno nel repository**: servono solo a rifare le
  misure.
- La natura di ogni fonte è indicata sempre, con una di queste voci: norma tramite fonte
  secondaria, prescrizione, progetto, costruttore, didattica.

## I termini: Raccolta R, cap. R.3.F

Non dà segni grafici. Dice però **che cosa è** un generatore modulare, e da qui viene la
differenza con una cascata.

- **Fonte**: Raccolta R ed. 2009, Fascicolo R.3, cap. R.3.F «Impianti con generatori di
  calore modulari», testo pubblicato da Caleffi:
  <https://raccoltar.caleffi.it/r3_impiantigenmodulari.html>
- **Natura**: prescrizione applicabile. È la stessa raccolta già registrata come SRC-012.
- **1.1**: «Un generatore di calore modulare è costituito da uno o più moduli termici
  predisposti dal fabbricante per funzionare singolarmente o contemporaneamente collegati ad
  un unico circuito idraulico.»
- **1.2**: «Il modulo termico è un generatore di calore costituito da uno o più elementi
  termici, funzionalmente dipendenti.»
- **1.3**: «Un elemento termico è costituito da uno scambiatore di calore e da un bruciatore
  (o porzione).»
- **1.4**: è «predisposto dal fabbricante» in due casi. Il primo: il fabbricante fornisce
  «il generatore modulare completo di ogni accessorio». Il secondo: fornisce «i singoli
  moduli termici insieme con un disegno esecutivo» dell'insieme.
- **2.2**: i dispositivi di sicurezza, protezione e controllo, «qualora non installati
  all'interno del mantello di rivestimento», vanno «sulla tubazione di mandata,
  immediatamente a valle dell'ultimo modulo, entro una distanza, all'esterno del mantello,
  non superiore a 1 metro».
- **3.1**: il circuito d'acqua di ciascun elemento termico va collegato a espansione e
  sicurezze «senza intercettazioni».
- **3.2**: «È ammessa l'installazione di una valvola a tre vie che mette in comunicazione il
  modulo con l'atmosfera.»
- **Cosa ne segue per il disegno.** Nella norma «generatore modulare» copre due cose: la cassa
  unica con più elementi (tipo Modulex) e il gruppo di moduli murali predisposto dal
  fabbricante (tipo cascata a kit). Le tavole che seguono usano infatti lo stesso nome per
  entrambi.

---

## Fonte 1: UNI 9511 tramite Guerra (SRC-015)

- **Titolo**: «Norma UNI 9511 — Segni grafici — Apparecchiatura per la distribuzione di
  acqua, gas e vapore». Tavola «Tabelle utili» riprodotta nel materiale del prof. Guerra. La
  pagina porta la testata e il piede della rivista «Idraulica», pag. 18 stampata.
- **URL**: <https://professoreguerra.altervista.org/alterpages/files/UniIdraulica1.pdf>. È
  la copia locale `../guerra-uni9511.pdf`, a **PDF p. 2**.
- **Natura**: norma tramite fonte secondaria (didattica).
- **Che cosa c'è.** Quattro generatori di calore: a combustibile solido, liquido, gassoso ed
  elettrico. **Nessun segno per un generatore modulare, per un gruppo di generatori o per un
  involucro con più bruciatori.** Ho scorso anche le altre nove pagine del PDF, in un foglio
  di provini a 45 dpi: valvolame, unità di misura, giunzioni, canali, trattamento dell'aria,
  UNI 9182, regolazione, sonde. Nessuna contiene generatori.
- **«Generatore di calore a combustibile gassoso; preparatore a gas di acqua calda di
  consumo»**:
  - rettangolo verticale, larghezza/altezza **0,54** (circa 1:2), nessun tratto di tubo
    disegnato;
  - dentro, un triangolo con il vertice in alto, al centro, fra **0,37 e 0,60**
    dell'altezza;
  - base del triangolo **0,69** della larghezza del rettangolo, altezza/base **0,61**: è un
    triangolo alto, non schiacciato.
- **«Apparecchio, segno grafico generale»**: cerchio per i componenti con parti in movimento,
  rettangolo negli altri casi. Nota: «il simbolo rettangolare può essere utilizzato sia
  verticalmente sia orizzontalmente». È l'unico segno normato che possa fare da contenitore
  generico.
- **Ritagli**:
  - `modulare_01_guerra-uni9511-generatore-gas.png`: segno e riga di legenda;
  - `modulare_01b_guerra-uni9511-apparecchio-generale.png`: segno generale e nota.

## Fonte 2: UNI 9511 tramite Oppo (SRC-016). Nessun segno

- **URL**: indice <https://www.oppo.it/disegni/a_disegni-elenco.html>, tabelle
  `https://www.oppo.it/disegni/simboli_idra_1.htm` … `simboli_idra_10.htm`.
- **Natura**: norma tramite fonte secondaria (operatore di settore).
- **Cosa c'è.** Le dieci tabelle sono:
  1. tubazioni e canalizzazioni;
  2. giunzioni e accessori;
  3. valvolame;
  4. pozzetti, scarichi e dispositivi diversi;
  5. sonde e trasmettitori;
  6. grandezze, sonde e rilevatori;
  7. simboli letterali delle grandezze;
  8. identificazione del fluido;
  9. simboli letterali dei componenti, che riguardano solo gli scarichi (SM, PL, SAU, …,
     P pompa);
  10. apparecchi indicatori.

  **Nessun generatore di calore, né singolo né modulare**, come già annotato nel registro per
  SRC-016. Nessun ritaglio.

## Fonte 3: Caleffi, schemi 1.103 e 1.101 (costruttore di componenti, famiglia SRC-008)

La coppia migliore: stesso autore e stessa grafica, con da una parte due moduli in un
involucro e dall'altra due caldaie separate.

- **Schema 1.103**, «Centrale termica con due moduli termici e regolazione climatica (senza
  produzione acqua calda sanitaria)». Nel PDF il titolo è in inglese: «Central heating system
  with two thermal modules and outside temperature regulation…».
  - Pagina: <https://www.caleffi.com/it-it/schemi/centrale-termica-con-due-moduli-termici-e-regolazione-climatica-senza-produzione-acqua-calda-sanitaria-1103>
  - PDF: <https://www.caleffi.com/sites/default/files/media/external-file/1.103.pdf>
    (pagina unica, **PDF p. 1**, creato il 30/09/2024). Esiste anche il DXF.
  - Dalla pagina: «La centrale termica è essenzialmente costituita da: moduli termici con
    pompe e regolazione climatica interne; separatore idraulico multifunzione…».
- **Schema 1.101**, «Centrale termica con regolazione climatica interna (senza produzione
  acqua calda sanitaria)».
  - Pagina: <https://www.caleffi.com/it-it/schemi/centrale-termica-con-regolazione-climatica-interna-senza-produzione-acqua-calda-sanitaria-1101>
  - PDF: <https://www.caleffi.com/sites/default/files/media/external-file/1.101.pdf>
    (**PDF p. 1**).
  - Dalla pagina: «caldaie a condensazione dotate di pompe e regolazione climatica interne, e
    in grado di funzionare a portata nulla…».
- **Natura**: costruttore di componenti, schemi applicativi di principio. Nel PDF: «These
  schemes do not replace HVAC system planning».

**Che cosa si vede nell'1.103: due moduli in un involucro**

- **Involucro.** Rettangolo pieno color beige chiaro con contorno scuro, **274,2 × 350,0 pt**,
  larghezza/altezza 0,78. Contiene i due moduli, le linee di collegamento e i collettori.
- **Moduli.** Due, uguali, affiancati in orizzontale con 18 pt di spazio fra loro. Ciascuno è
  un rettangolo ad angoli arrotondati di **116,9 × 164,8 pt** (larghezza/altezza 0,71),
  grigio sfumato.
- **Segno di ogni modulo**:
  - una linea orizzontale divide il modulo a **0,69** dell'altezza;
  - subito sopra c'è un **triangolo piatto con il vertice in alto**: base 0,67 della
    larghezza, altezza/base **0,27**, fra 0,53 e 0,66 dell'altezza;
  - sotto la linea, un cerchio con un triangolo pieno: la pompa, dentro il modulo;
  - **nessuna fiamma**.
- **Attacchi.** Dal lato inferiore di ogni modulo scendono tre linee: ritorno (blu) a
  sinistra, gas (giallo, con valvola a sfera) al centro, mandata (rossa) a destra.
- **Collettori interni**, nella parte bassa dell'involucro:
  - collettore di mandata: barra rossa piena ad angoli arrotondati, **195,9 × 16,5 pt**, in
    alto;
  - collettore di ritorno: barra blu, **190,2 × 16,5 pt**, sotto, spostata a sinistra;
  - la linea gas corre orizzontale sopra i due collettori ed entra dal lato **sinistro**
    (0,70 dell'altezza).
- **Uscite.** La mandata esce dal lato **destro** a **0,78** dell'altezza dell'involucro. Il
  ritorno esce anch'esso dal lato **destro**, più in basso, a **0,92**, con un tubo che
  scende dalla testa della barra blu.
- **A valle, una sola volta**: un solo gruppo di sicurezza sulla mandata comune, subito fuori
  dall'involucro (collettore verde con termometro, manometro e dispositivi, codici 335, 527 e
  5520 nella tavola). Poi valvole e separatore 5495. Sul ritorno comune un solo vaso
  d'espansione (556).

**Che cosa si vede nell'1.101: due caldaie separate (la cascata)**

- **Corpo.** Nessun involucro comune. Ogni caldaia è un rettangolo grigio di 98,3 × 141,9 pt
  (0,69) su uno zoccolo di 86,5 × 6,2 pt.
- **Segno.** Stesso triangolo piatto (base 0,67 della larghezza, altezza/base **0,27**) e
  stessa pompa nel cerchio: il glifo della caldaia e quello del modulo sono **lo stesso
  segno**.
- **Attacchi**, tutti sul **fianco destro** della caldaia: la mandata esce in alto e sale al
  proprio gruppo di sicurezza; il ritorno entra in basso. Il gas entra dal fianco sinistro in
  basso, con la propria valvola di intercettazione del combustibile.
- **Sicurezze.** **Ogni caldaia ha il proprio gruppo di sicurezza, il proprio vaso e le
  proprie valvole.** Si collegano con tubi separati al separatore comune.

**Ritagli**

- `modulare_07_caleffi-schema1.103-due-moduli-in-involucro.png`
- `modulare_07b_caleffi-schema1.101-due-caldaie-separate.png`

**Da notare**: il catalogo BIM Caleffi ha anche uno schema intitolato proprio «**10.30
Centrale Termica con caldaia modulare e regolazione climatica interna**»:
<https://bim.caleffi.com/it-it/schemi-bim/centrale-termica-con-caldaia-modulare-e-regolazione-climatica-interna>.
L'immagine sta su `bim.caleffi.com:8085` e dal proxy la connessione è rifiutata:
**non l'ho vista**. Il testo della pagina parla di «caldaia a moduli con regolazione
climatica interna; separatore idraulico; pompe di circolazione gemellari…». È la fonte non
vista che più conviene aprire da un browser.

## Fonte 4: Division Energia, Condominio Tower House, Treviso, elaborato IM01 (progetto, SRC-009)

- **Titolo**: «Schema funzionale centrale termica — Impianto di riscaldamento —
  Riqualificazione impiantistica dell'edificio "Condominio Tower House", sito presso il Comune
  di Treviso, in via Pisa 15».
- **Estremi**: elaborato **IM01**, data settembre 2024, «Rev. 03.c del 27/09/2024 (as
  built)». Committente: Condominio Tower House. Progettista: Ing. Davide Fraccaro, Divisione
  Energia srl.
- **URL**: <https://www.divisionenergia.it/wp-content/uploads/2025/02/Cond.TH_schema-ct-as-built.pdf>,
  **PDF p. 1**, tavola unica.
- **Natura**: progetto (committente privato), pubblicato dal progettista.
- **Avvertenza**: la tavola dichiara «non può essere riprodotto o comunicato a terzi senza
  preventiva autorizzazione scritta». Nel registro SRC-009 è «non riprodotta». I ritagli 02 e
  02b servono a guardare; **per pubblicarli nel repository decide il PO**.
- **Legenda**, ritagliata:
  - «**GM** — Generatore di calore modulare a gas a condensazione — MARCA: WEISHAUPT, MOD.:
    WTC-GW 110-A x 4 — P. focolare 13,4–376,0 kW»;
  - «**MT** — Modulo termico a gas a condensazione — WTC-GW 110-A — 13,4–94,0 kW».

  I nomi di prodotto sono riportati così come stanno nella legenda: non li ho verificati
  presso Weishaupt.

**Che cosa si vede**

- **Involucro GM.** Rettangolo a tratteggio nero, trattini da 11,7 pt e intervalli da 5,9 pt,
  **368,8 × 254,5 pt** (orizzontale). Contiene i quattro moduli **e** i tre collettori. Porta
  la sigla «GM» con una linea di richiamo. Il primo modulo porta il richiamo «Modulo
  Master».
- **Moduli MT.** Quattro, uguali, affiancati in orizzontale con passo 87,4 pt. Ciascuno è un
  rettangolo ciano di **58,5 × 84,3 pt** (0,69), con in alto al centro un rettangolino
  (7,5 × 10 pt) per l'attacco fumi.
- **Dentro ogni modulo**:
  - in alto a destra, due quadratini «Tr» e «Pm»: termostato di regolazione e pressostato di
    minima (nota 3S: «ogni singolo modulo termico presenta a corredo un termostato di
    regolazione e un pressostato di minima»);
  - un **triangolo piatto con vertice in alto** fra 0,53 e 0,66 dell'altezza: base 0,67 della
    larghezza, altezza/base **0,27**;
  - una divisoria orizzontale a **0,69**;
  - sotto la divisoria, un riquadro nero con la sigla «**MT**»;
  - **nessuna fiamma**.
- **Le proporzioni del triangolo e della divisoria coincidono al centesimo con il glifo
  Caleffi** (fonte 3). Caleffi pubblica gli schemi anche in DXF: è plausibile che il blocco
  venga da lì. **Non verificato.**
- **Attacchi.** Dal lato inferiore di ogni modulo, gas a sinistra (0,09 della larghezza),
  mandata al centro (0,45), ritorno a destra (0,84). Su ogni modulo:
  - **gas**: una valvola;
  - **mandata**: un organo a tre vie con scarico verso un imbuto. È una lettura mia, coerente
    con R.3.F 3.2, e la legenda non lo conferma;
  - **ritorno**: valvola, ritegno, **circolatore del modulo** e valvola.
- **Collettori interni.** Tre rettangoli ciano sottili, orizzontali, sotto i moduli e dentro
  l'involucro:
  - mandata (346,3 × 10,4 pt) in alto, a **0,78** dell'altezza dell'involucro;
  - ritorno (329,1 × 10,4 pt) a **0,88**;
  - gas (346,3 × 5,2 pt) a **0,97**.

  Il reintegro (verde) entra nel ritorno da sinistra.
- **Uscite, tutte sul lato destro.**
  - La **mandata** («3"») esce in alto e porta i dispositivi di sicurezza: Tb, Pb, termometro,
    manometro, PSV 5,0 bar. Sono raggruppati in una quota «**< 1 m**» dall'uscita.
  - Il **ritorno** («3"») è sotto.
  - Il **gas** è in basso, con la valvola di intercettazione del combustibile (VIC) e un
    filtro DN65.
- **Figure accessorie.** «Fig. 1 Esempio illustrativo di generatore modulare con moduli
  termici installati schiena/schiena (caso esemplificativo con n.4 moduli…)» è un'assonometria
  del prodotto e non l'ho ritagliata. Fig. 2 mostra una coppia di caldaie schiena/schiena con
  il collettore fumi del fabbricante.
- **Ritagli**:
  - `modulare_02_divisionenergia-TH-GM-weishaupt-4moduli.png`: involucro, moduli, collettori
    e uscite;
  - `modulare_02b_divisionenergia-TH-legenda-GM-MT.png`: righe di legenda GM e MT.

## Fonte 5: Teatro Le Muse, Ancona, tavola M.EL.17 (progetto pubblico PNRR)

- **Titolo**: «Schema termoregolazione caldaie e pompe di calore», **Progetto esecutivo —
  Impianto elettrico, M.EL.17**, maggio 2022.
- **Committenti e progettisti**: stazione appaltante Marche Teatro scarl. L'intervento è
  l'efficientamento energetico del Teatro Le Muse, nel Comune di Ancona (PNRR M1C3, inv. 1.3).
  Progettista WePlan Ingegneria (Osimo), Ing. M. Baleani.
- **URL**: <https://www.comuneancona.it/ankonline/wp-content/uploads/2022/12/M.03-M.EL_.17-Rev.01-Schema-termoregolazione-caldaie-e-pompa-di-calore.pdf>,
  **PDF p. 1**, tavola unica di 7228 × 2580 pt. Con curl la connessione veniva chiusa; il file
  l'ho ottenuto con WebFetch.
- **Natura**: progetto pubblico. È una tavola di regolazione che contiene lo schema idraulico
  della centrale.
- **Legenda, voce 1** (ritagliata): «Generatore modulare a condensazione tipo VIESSMANN mod.
  Vitomodul 200-W 3x150kW — P.utile=408kW Tm/Tr=80/60°C, P.foc.=426kW».
  - Il nome compare nella tavola.
  - I risultati di ricerca (Edilportale e rivenditori) descrivono il Vitomodul 200-W come un
    sistema di più Vitodens 200-W.
  - **Non ho aperto una fonte Viessmann**: la scheda disponibile sta su siti di terzi e il
    tentativo è fallito.

**Che cosa si vede**

- **Moduli.** Tre, disegnati come blocchi CAD di una caldaia murale vista di fronte: un
  rettangolo alto (larghezza/altezza circa 0,56), una fascia inferiore di comando con display
  e manopola, e in alto l'attacco fumi con canna Ø 110 mm, una per modulo. **Nessun triangolo
  e nessuna fiamma.** Li attraversa una linea tratteggiata di comando.
- **Nessun involucro.** L'unità del generatore è data **solo da una sigla**: il richiamo «1»
  cerchiato sopra il modulo centrale, uno solo per tutti e tre, e la voce 1 della legenda.
- **Attacchi.** Sotto ogni modulo, da sinistra: scarico (azzurro, con imbuto), mandata
  (rosso continuo), gas (verde), ritorno. Sul ritorno ogni modulo ha la propria **pompa e il
  proprio ritegno**, disegnati fuori dal modulo.
- **Collettori comuni.** Linee orizzontali sotto i moduli: mandata in rosso continuo in alto,
  ritorno in rosso tratteggiato sotto, gas in verde più in basso. Il gas «Ø 2"» entra da
  **sinistra**.
- **Uscite, a destra.**
  - La **mandata** «Ø 3"» esce verso destra, con la freccia in uscita. Subito dopo l'ultimo
    modulo ha il gruppo «3» dei dispositivi: Tr, Tb, Pb, termometro, valvola di sicurezza e
    altri. Poi va allo scambiatore «2».
  - Il **ritorno** «Ø 3"» rientra da destra, sotto la mandata.
- **Ritagli**:
  - `modulare_08_ancona-teatromuse-MEL17-generatore-modulare-3moduli.png`
  - `modulare_08b_ancona-teatromuse-MEL17-legenda-1.png`

## Fonte 6: Unical, MODULEX EXT (costruttore). Cassa unica con più bruciatori

**6a. Catalogo tecnico MODULEX EXT 2024, PDF p. 19**

- **URL**: <https://www.unicalag.it/upload/blocchi/X347allegatoDATI_TECNICI2-1X_modulex-ext_2024_it.pdf>.
  Sulla pagina prodotto il link si chiama «CATALOGO TECNICO»:
  <https://www.unicalag.it/prodotti/caldaie-professionali-300/condensazione-alluminio/347/modulex-ext-100-1500>.
  Il PDF è stato creato il 30/08/2024.
- **Natura**: costruttore. Il dépliant del 2023 lo descrive così: «MODULEX EXT è un
  generatore a basamento multibruciatore modulare a condensazione».
  - Dépliant: <https://www.unicalag.it/upload/blocchi/X347allegatoDEPLIANT1-1X_modulex-ext_05_2023.pdf>,
    PDF p. 4.
  - A PDF p. 6 lo stesso dépliant dice: «Connessioni idrauliche tra gli elementi contigui
    prive di intercettazioni, realizzate mediante collettori bilanciati idraulicamente».
  - Il numero di elementi termici va da 2 (mod. 100) a 14 (mod. 1500): catalogo, PDF p. 8–9.
- **Titolo della figura**: «SCHEMA PER INSTALLAZIONE GENERATORE DI CALORE DI TIPO MODULARE —
  Conforme alla certificazione INAIL N° 18012 del 14/03/2022.000177 ed al capitolo R 3F —
  Raccolta R ed. 2009».

**Che cosa si vede**

- **Il generatore** è disegnato **in modo pittorico, non simbolico**:
  - una cassa grigia vista di fronte, con il pannello comandi in alto (richiamo 1, termostato
    di regolazione) e un moncone di scarico fumi in basso a sinistra;
  - dal fronte si vedono gli elementi termici, resi in modo fotografico con fiamme arancio in
    alto;
  - sotto gli elementi, i numeri «1 2 3 4 … 14» separati da linee a puntini e la scritta
    «ELEMENTI TERMICI»: i puntini «…» stanno per un numero generico di elementi.
- **Collettori interni**: **non disegnati**.
- **Attacchi, tutti sul lato destro della cassa**, dall'alto in basso:
  1. **mandata**, a circa 0,38 dell'altezza della cassa, con il «**Tronchetto INAIL (\*) ≤ 1
     m**»: dispositivi 13, 10, 13, 2, 8, 7, 12, 14, 11, 9, 4 e il collegamento del vaso 6;
  2. **gas**, a circa 0,63, con la valvola di intercettazione del combustibile 16;
  3. **ritorno**, a circa 0,84, con filtro 5 e pompa 3.
- **A valle.** Compensatore idraulico 15a oppure scambiatore a piastre 15b, poi le frecce
  «MANDATA» e «RITORNO».
- **Nota (\*)**: «Deve essere installato immediatamente a valle dell'ultimo modulo, entro una
  distanza sulla tubazione di mandata non superiore a 1 metro… Lo schema riporta nel
  dettaglio quali dispositivi devono essere installati a valle dell'ultimo modulo».
- **Ritagli**:
  - `modulare_05_unical-modulexEXT-catalogo2024-p19-generatore.png`: il solo generatore con i
    tre attacchi;
  - `modulare_05b_unical-modulexEXT-catalogo2024-p19-schema-INAIL.png`: la figura intera con
    la nota.

**6b. Dépliant MODULEX, «Cod. 20305 — Ed.6 — 05/2009», PDF p. 12** (prodotto fuori listino)

- **URL**: <https://www.unicalag.it/upload/blocchi/X346allegatoDEPLIANT1-1X_0723_6_modulex.pdf>,
  pagina <https://www.unicalag.it/fuori-listino/346/modulex-e-supermodulex>.
- **Figura**: «Impianto MODULEX con sistema di produzione di acqua calda sanitaria ad
  integrazione Solare».
- **Che cosa si vede.** La MODULEX è **una scatola unica**, grigia e resa in leggera
  prospettiva, con la scritta «MODULEX». **Nessun modulo visibile.** Il camino verticale
  (D=150) sta a sinistra. A destra escono due attacchi: in alto la mandata con termometro,
  manometro e dispositivi; in basso il ritorno con filtro a Y e pompa. Vanno a un separatore
  idraulico. È una lettura mia del disegno pittorico: la figura non ha legenda.
- **Ritaglio**: `modulare_06_unical-modulex-depliant2009-p12-scatola-unica.png`.

## Fonte 7: Baltur, GTMIX MK, «Gruppo termico modulare a condensazione ad alto contenuto d'acqua» (costruttore)

- **URL**: <https://www.baltur.com/it/wp-content/uploads/2024/07/gruppo-termico-modulare_GTMIX-250-1000-MK.pdf>,
  «Cod. 0001001543 — Ediz. 06/2022» (PDF p. 8), **PDF p. 3**.
- **Natura**: costruttore.
  - Il testo dice: «GTMIX MK è un modulo termico costituito da un insieme di elementi
    termici… può essere assemblato in batteria per costituire un generatore di calore
    modulare» (PDF p. 4).
  - E ancora: «Collettori idraulici unificati privi di intercettazioni tra gli elementi»
    (PDF p. 2).
  - Elementi per modello: 2, 3, 4, 2+3, 2+4, 4+3, 4+4 (M oppure M+S, cioè Master + Slave).
- **Titolo della figura**: «SCHEMA PER INSTALLAZIONE GRUPPO TERMICO DI TIPO MODULARE —
  Conforme alla certificazione INAIL 60202. 24/07/2019. 0008974 e dal capitolo R 3F —
  Raccolta R ed. 2009». La figura è un'immagine raster di **634 × 216 px**: si legge a
  fatica.

**Che cosa si vede**

- **Vista dall'alto, non simbolica.** Due gruppi affiancati, ciascuno racchiuso in un
  **rettangolo tratteggiato** diviso a metà da un tratteggio verticale.
- **Elementi.** Ogni gruppo contiene **quattro cerchi grigi**, cioè gli elementi visti dal
  sopra, disposti 2 × 2 e numerati 1–4 e 5–8.
- **Collettori.** Le **due linee dei collettori**, mandata sopra e ritorno sotto, attraversano
  i gruppi in orizzontale **fra le due file di elementi**. Non si vedono stacchi verso i
  singoli elementi.
- **Fra i due gruppi** ci sono organi disegnati a coppia su entrambe le linee: il simbolo non
  è spiegato in legenda.
- **Richiamo 16.** Ogni elemento ha un richiamo «16» con un piccolo dispositivo fuori dalla
  cassa; la legenda di pagina non spiega il 16.
- **Uscite a destra.** La mandata, in alto, passa per il «**Tronchetto INAIL (\*) ≤ 1 m**» e
  va al compensatore 15a o allo scambiatore 15b, poi «MANDATA». Il ritorno, in basso, torna
  con pompa 3 e filtro 5.
- **Una terza linea.** Esce dal lato destro vicino al ritorno e porta una valvola con
  attuatore, legata con un capillare al pozzetto 12. Nella figura Unical equivalente quella
  valvola è la valvola di intercettazione del combustibile 16: è verosimilmente il gas, ma a
  questa risoluzione non si legge con certezza.
- **Stessa matrice di Unical.** La numerazione dei dispositivi (1–15b) e il testo della nota
  (\*) sono **gli stessi dello schema Unical**. Sembrano derivare dallo stesso schema tipo:
  l'origine non l'ho verificata.
- **Ritaglio**: `modulare_03_baltur-GTMIX-MK-schema-modulare.png`, la figura intera.

## Fonte 8: Studio GLT, «Schema funzionale centrale termica», SF_01 (progetto di uno studio privato)

- **URL**: <http://studioglt.it/files/SCHEMA-CENTRALE-SF_01.pdf>, **PDF p. 1**.
  - La pagina è ruotata di 270°: i rettangoli di ritaglio sono nelle coordinate della pagina
    mostrata.
  - I metadati PDF dicono «SF_01» e 21/03/2016.
  - L'opera e il committente **non sono indicati** nella tavola.
- **Natura**: progetto. La fonte non è identificabile come pubblica.
- **Legenda**: «**GC1-2** GENERATORE DI CALORE MODULARE A CONDENSAZIONE, kW 56,5».
- **Moduli.** Due, disegnati come **caldaie murali in contorno**: rettangolo esterno,
  rettangolo interno sfalsato e rettangolino (display) in basso. All'interno le scritte «GC1»
  e «GC2». **Nessun triangolo e nessuna fiamma.** In alto, gli scarichi fumi vanno a un
  collettore fumi comune con scarico condensa.
- **Collettori comuni.** Sotto i moduli, tre tubi a doppia linea con flange terminali:
  1. **mandata** in alto: esce a **destra** con freccia; poi tr, trs, psr, valvola di
     sicurezza «3 bar DN15», termometro, manometro;
  2. **gas** in mezzo: entra da **sinistra** con filtro e valvola di intercettazione del
     combustibile;
  3. **ritorno** in basso: rientra da **destra**.
- **Tratteggio.** Una **linea tratteggiata sottile** racchiude la parte bassa dei moduli e i
  collettori, cioè il kit dei collettori; la legenda non la spiega.
- **Ritagli**:
  - `modulare_04_studioglt-SF01-GC1-2-due-moduli-murali.png`
  - `modulare_04b_studioglt-SF01-legenda-GC1-2.png`

## Fonte 9: Biasi, Multiparva Cond H (costruttore)

- **URL**: <https://www.biasi.it/images/pdf/depliant-prodotti/Folder_Multiparva_CondH.pdf>.
  Editore: BSG Caldaie a Gas S.p.A.; metadati 13/04/2016. Figura a **PDF p. 13** (stampata
  12), «Schemi d'impianto».
- **Natura**: costruttore. Il testo dice:
  - «la nuova caldaia modulare a condensazione» (PDF p. 2);
  - moduli da 34 a 115 kW, «combinando fino a 6 moduli» (PDF p. 4);
  - la valvola di sicurezza è «presente in ogni singola caldaia, non solo sulla centrale»
    (PDF p. 2).
- **Moduli.** In una vista pittorica leggera, due caldaie murali affiancate, etichettate
  «master 1» e «slave 1». Portano un solo numero di legenda, «1 Caldaia».
- **Collettori.** Sotto i moduli, tre file di tubi flangiati, **un tronco per ogni caldaia**
  (graffa «2» sotto ciascuno):
  - **5**, collettore di mandata, in alto: freccia verso destra;
  - **6**, collettore di ritorno, in mezzo: freccia verso sinistra;
  - **gas** in basso: entra da **destra** con la valvola 23.
- **Uscite a destra.** Sulla mandata «3 Modulo sicurezze INAIL», poi «4 Separatore idraulico
  oppure scambiatore a piastre».
- **Ritagli**:
  - `modulare_09_biasi-multiparvaCondH-p13-master-slave-collettori.png`
  - `modulare_09b_biasi-multiparvaCondH-p13-legenda-1-6.png`

## Fonte 10: ISO 14617 (solo l'indice pubblico)

- **URL**: ISO 14617-1:2005, anteprima iTeh:
  <https://cdn.standards.iteh.ai/samples/41838/3bdf620c00c841c5bb0628e97e4b8592/ISO-14617-1-2005.pdf>,
  **PDF p. 15**, indice alfabetico.
- **Natura**: norma internazionale, solo l'anteprima pubblica.
- **Che cosa dice l'indice.** Sotto «Boilers» (parte 11, § 7) ci sono solo «Boiler 2531»,
  «– of fired type X2531», «– with dome 2532», «– of electrode type X2533» e «– with
  superheater X2534». Sono caldaie di processo. **Nessuna voce per caldaie modulari, a più
  bruciatori o in batteria.**
- **Geometria**: non vista. L'anteprima della parte 11 non l'ho trovata, e ISO 14617-11:2002
  risulta sostituita dalla ISO 14617-2:2025. Nessun ritaglio. EN e DIN non li ho cercati oltre.

---

## Viste e non usate

| Fonte | URL | Perché non è usata |
|---|---|---|
| Comune di Carrara, PD.IM.03.00, schema funzionale | <http://servizi.comune.carrara.ms.it/buonarroti_definitivo/2021_llppe_038_pd_IMPIANTI%20TERMO-MECCANICI/PD.IM.03.00%20-%20Centrale%20termica%20-%20schema%20funzionale.pdf> | Solo pompe di calore, nessuna caldaia |
| Trezzano, schema funzionale P07 | <https://trezzano.e-pal.it/AttiVisualizzatore/download/allegato/837815?fId=837822&sbustato=true> | Cogeneratori e caldaie non modulari |
| Università di Trieste, schema CT e CF | <https://amm.units.it/sites/default/files/gar/procedure/Allegato%20D-1%20-%203%20-%20140627%20schema%20funzionale%20CT%20e%20CF.pdf> | Una caldaia singola, Baltur EVOMIX 560 |
| Provincia di Ravenna, Ballardini SM04 (SRC-010) | vedi registro | Tre caldaie a basamento con bruciatore, non modulari |
| Provincia di Ravenna, Baldini SA02 | <https://presadmin.provincia.ra.it/content/download/88837/1115634/file/SA02%20-%20ITI%20BALDINI%20Stato%20Attuale%20Schema%20funzionale%20Centrale%20Termica.pdf> | Nel testo nessuna occorrenza di «modul»; la tavola **non l'ho guardata** |
| Comune di Padova, APPR_56 | <https://www.comune.padova.it/bandigara/Impianti%20termici/APPR_56_signed_signed_signed_signed.pdf> | Due caldaie Riello «ALU PRO» disegnate come rettangoli semplici con TB/TR e bruciatore. **Non ho verificato** che il prodotto sia modulare |
| Arezzo Casa, Bibbiena, ES_IM02 (23/01/2018) | <https://www.arezzocasa.net/wp-content/uploads/2019/03/ES_IM02_Schema-centrale-termica-01_23012018.pdf> | Vedi la nota qui sotto: non l'ho usata perché la tavola e il computo dello stesso intervento non concordano |
| Comune di Vinci, E-MN0 | <https://vecchiosito.comune.vinci.fi.it/images/stories/maternaVinci/04_IMP_MECCANICI/E-MN0-SCHEMA_FUNZIONALE_CENTRALE_TERMICA_Rev1.pdf> | Pompa di calore |
| Sapienza, Tav. T-17 | <https://elearning.uniroma1.it/pluginfile.php/648953/mod_folder/content/0/Imp.%20Termico/Tav.T-17%20Imp%20Termico%20Schema%20funzionale_REV02.pdf?forcedownload=1> | Caldaia singola Unical Alkon 70 |
| Politecnico di Milano, ML0-01 | <https://www.polimi.it/fileadmin/user_upload/allegati_bandi_gara_pnrr/All._E_Tavola_ML0-01.pdf> | Caldaie ICI di grande taglia, non modulari |
| Studio Sabattini, «Tavola Schema centrale termica» | <https://www.studiosabattini.it/download/progetto/Tavola1Schemacentraletermica.pdf> | 26 pagine scansionate, **non esaminate** |
| Unical, manuali installatore MODULEX EXT (00338277, 00338303, 00338585) | dalla pagina prodotto Unical | Le pagine «Esempio schema di collegamento» sono **schemi elettrici** |
| Riello, Condexa PRO | link di download su riello.it | Il link restituisce una pagina HTML, non il PDF: **non letto** |
| Viessmann, Vitomodul 200-W | scheda su siti di terzi | Tentativo di scaricarla fallito: **non letta** |
| Ferroli, Scheme Selector | <https://www.ferroli.com/it/scheme-selector> | Richiede l'accesso |
| CT Energia (SRC-011) | vedi registro | Non consultata in questa ricerca |

**Nota su Arezzo Casa, Bibbiena.** La tavola ES_IM02 disegna **tre** unità siglate «01», con
qtà 1 nella tabella componenti («Generatore Qf = 200,00 kW»). Il computo dello stesso
intervento, con la stessa data, descrive una «Modulex 10GT, Caldaia Modulex EXT 200»:
<https://www.arezzocasa.net/wp-content/uploads/2019/03/caratteristiche-caldaia-01_23012018.pdf>.
Il catalogo Unical dà 4 elementi per il modello 200. La discordanza non è risolta, perciò la
fonte non è usata.

---

## Sintesi

### La forma ricorrente

Le fonti che disegnano la caldaia modulare come **un oggetto solo** sono le fonti 3–9.
Coincidono su quattro punti.

1. **Più moduli uguali, affiancati in orizzontale**:
   - di solito disegnati **tutti**: 2 in Caleffi, Studio GLT e Biasi; 3 ad Ancona; 4 in
     Division Energia; 4 + 4 in Baltur;
   - Unical 2024 usa un numero generico, «1 2 3 4 … 14»;
   - Unical 2009 non mostra i moduli.
2. **Collettori comuni orizzontali sotto i moduli.** Ogni modulo vi scende con i propri
   attacchi, dal lato inferiore. La mandata sta sempre sopra il ritorno. Due eccezioni:
   - Baltur, disegnato in pianta: i collettori passano fra le due file di elementi;
   - Unical: i collettori non sono disegnati.
3. **Mandata e ritorno escono da un lato solo, il destro in tutte le fonti viste, con la
   mandata più in alto del ritorno.** Nelle due fonti schematiche misurate escono entrambi
   nella parte bassa del lato destro:
   - Caleffi 1.103: mandata a 0,78 e ritorno a 0,92 dell'altezza dell'involucro;
   - Division Energia: collettore di mandata a 0,78 e di ritorno a 0,88.

   Il gas invece **non ha un lato fisso**: da sinistra in Caleffi 1.103, Ancona e Studio GLT;
   da destra in Division Energia, Unical e Biasi.
4. **I dispositivi di sicurezza compaiono una volta sola**, sulla mandata comune, subito fuori
   dall'involucro o dopo l'ultimo modulo. Division Energia, Unical e Baltur scrivono anche
   «≤ 1 m» o «< 1 m». È la regola di R.3.F 2.2.

### Il segno del singolo modulo

- **Nelle fonti schematiche** (Caleffi, Division Energia) il modulo porta un **triangolo piatto
  con il vertice in alto**.
  - Le proporzioni sono identiche nelle due fonti: base 0,67 della larghezza, altezza/base
    0,27, fra 0,53 e 0,66 dell'altezza, subito sopra una divisoria a 0,69.
  - Sotto la divisoria: la pompa (Caleffi), oppure la sigla MT con i quadratini Tr/Pm
    (Division Energia).
  - **Nessuna fiamma.**
- **Non è il triangolo UNI 9511**, se lo si misura: in Guerra il triangolo è alto
  (altezza/base 0,61) e sta al centro di un rettangolo verticale circa 1:2 (0,54). Nessuna
  fonte dichiara di usare UNI 9511 per il modulo.
- **Nelle tavole che usano i blocchi CAD dei prodotti** (Ancona, Studio GLT, Biasi) il modulo
  è il contorno della caldaia murale reale, **senza alcun segno di combustione**.
- **Le fiamme** compaiono solo nella resa fotografica di Unical.

### Le varianti

- **A: involucro disegnato, con moduli e collettori dentro.**
  - Caleffi 1.103: rettangolo pieno chiaro.
  - Division Energia: rettangolo a tratteggio lungo, con la sigla GM.
  - Baltur: rettangolo tratteggiato, ma in pianta.
- **B: nessun involucro.** I moduli murali stanno sui collettori e l'unità è data solo dalla
  **sigla unica** e dalla legenda.
  - Ancona: «1».
  - Studio GLT: «GC1-2», con un tratteggio solo attorno al kit dei collettori.
  - Biasi: «1», master e slave.
- **C: cassa unica pittorica.** Con gli elementi visibili e numerati (Unical 2024), oppure
  come scatola senza moduli (Unical 2009).
  - È il caso della vera **caldaia a cassa unica con più bruciatori**.
  - Qui **i collettori interni non si vedono mai**: Unical li dichiara nel testo ma non li
    disegna.

### Come la distinguono da una cascata di caldaie separate

Il confronto più pulito è **Caleffi 1.103 contro 1.101**: stesso glifo di caldaia, tre
differenze.

1. **Contenitore**: nella caldaia modulare c'è un involucro comune che racchiude moduli e
   collettori; nella cascata nessuno.
2. **Collettori**: nella modulare sono interni all'involucro e ne escono con una mandata e un
   ritorno. Nella cascata ogni caldaia ha tubi propri fino al separatore comune.
3. **Sicurezze**: nella modulare un solo gruppo di sicurezza sulla mandata comune e un solo
   vaso. Nella cascata ogni caldaia ha **il proprio** gruppo di sicurezza, vaso e valvola di
   intercettazione del combustibile.

Le altre fonti aggiungono due cose.

- **La sigla.** Il generatore ha una sola sigla: GM, «1», GC1-2. I moduli sono voci
  subordinate: MT in Division Energia, master/slave in Biasi, elementi 1…N in Unical e
  Baltur.
- **La quota.** La distanza «≤ 1 m» dei dispositivi di sicurezza si misura dall'ultimo
  modulo.

Nella norma la distinzione è R.3.F:
- moduli «predisposti dal fabbricante» e collegati «ad un unico circuito idraulico»;
- nessuna intercettazione fra elemento e sicurezze, salvo la valvola a tre vie verso
  l'atmosfera.

### Le fonti che la mostrano meglio

1. **Caleffi, schemi 1.103 e 1.101.** `modulare_07_caleffi-schema1.103-due-moduli-in-involucro.png`
   e `modulare_07b_caleffi-schema1.101-due-caldaie-separate.png`.
   - 1.103: <https://www.caleffi.com/sites/default/files/media/external-file/1.103.pdf>,
     PDF p. 1.
   - 1.101: <https://www.caleffi.com/sites/default/files/media/external-file/1.101.pdf>,
     PDF p. 1.
   - Modulare e cascata dallo stesso autore, con lo stesso segno.
2. **Division Energia, IM01 Treviso.** `modulare_02_divisionenergia-TH-GM-weishaupt-4moduli.png`
   e `modulare_02b_divisionenergia-TH-legenda-GM-MT.png`, PDF p. 1.
   - Progetto reale con involucro tratteggiato, legenda GM/MT e quota «< 1 m».
   - **Vincolo di riproduzione dichiarato sulla tavola.**
3. **Unical, catalogo tecnico MODULEX EXT 2024.** `modulare_05_unical-modulexEXT-catalogo2024-p19-generatore.png`
   e `modulare_05b_unical-modulexEXT-catalogo2024-p19-schema-INAIL.png`, PDF p. 19.
   - Il costruttore di una vera cassa unica a più bruciatori.
   - Mostra gli elementi numerati e le uscite a destra: mandata, gas, ritorno.

Come progetto pubblico: **Ancona, M.EL.17**
(`modulare_08_ancona-teatromuse-MEL17-generatore-modulare-3moduli.png`,
`modulare_08b_ancona-teatromuse-MEL17-legenda-1.png`), che però è della variante B.

### Che cosa non ho trovato

- **Nessun segno normato** per caldaia o generatore modulare:
  - in UNI 9511, per le tavole viste: Guerra p. 2 e Oppo tab. 1–10;
  - nell'indice ISO 14617.
- **Nessun progetto pubblico** che disegni una caldaia **a cassa unica con più bruciatori**
  (tipo Modulex) con un segno schematico. I progetti pubblici trovati hanno generatori
  modulari fatti di moduli murali. L'unico candidato, Arezzo Casa a Bibbiena, non concorda
  con il proprio computo.
- **Nessuna fonte disegna i collettori interni di una cassa unica.** I collettori interni
  disegnati (Caleffi, Division Energia) sono quelli di moduli murali in un telaio o
  involucro.
- **Non visti**:
  - lo schema Caleffi BIM «10.30 Centrale Termica con caldaia modulare», immagine non
    raggiungibile dal proxy;
  - i documenti Riello Condexa PRO e Viessmann Vitomodul 200-W.

## Avvertenze per l'uso dei ritagli

- Division Energia (`modulare_02*`): la tavola vieta la riproduzione senza autorizzazione
  scritta. Per il repository pubblico decide il PO.
- Baltur (`modulare_03`) viene da un'immagine raster a bassa risoluzione: i dettagli piccoli
  (richiami, organi fra i gruppi) non si leggono con certezza.
- `modulare_05b` e `modulare_03` sono figure intere, non segni singoli. Sono figure, non
  pagine; lo segnalo comunque.

## Misure (output di `misure.py`, rieseguito)

```
Division Energia IM01 (PDF p.1)
  moduli trovati: 4, passo x = 87.4 pt
  modulo larghezza/altezza: 0.69
  base triangolo / larghezza modulo: 0.67
  altezza triangolo / base triangolo: 0.27
  triangolo da (quota relativa dall'alto): 0.53
  triangolo a: 0.66
  divisoria (quota relativa): 0.69
  involucro GM: 368.8 x 254.5 pt
  collettore mandata (quota relativa nell'involucro): 0.78
  collettore ritorno (quota relativa nell'involucro): 0.88
  collettore gas (quota relativa nell'involucro): 0.97
Caleffi schema 1.103
  involucro 274.2 x 350.0 pt; moduli 2 da 116.9 x 164.8
  involucro larghezza/altezza: 0.78
  modulo larghezza/altezza: 0.71
  base triangolo / larghezza modulo: 0.67
  altezza triangolo / base: 0.27
  triangolo da: 0.53
  triangolo a: 0.66
  divisoria (y=328.8): 0.69
  mandata esce a destra (quota relativa nell'involucro): 0.78
  ritorno esce a destra (quota relativa nell'involucro): 0.92
  gas entra a sinistra (quota relativa nell'involucro): 0.70
Caleffi schema 1.101
  corpo larghezza/altezza: 0.69
  base triangolo / larghezza corpo: 0.67
  altezza triangolo / base: 0.27
UNI 9511 tramite Guerra, PDF p.2 (scansione)
  rettangolo larghezza/altezza: 0.54
  base triangolo / larghezza: 0.69
  altezza triangolo / base: 0.61
  triangolo da: 0.37
  triangolo a: 0.60
```

Le quote delle uscite per Unical (0,38 / 0,63 / 0,84) e per Ancona sono lette sul raster dei
ritagli: sono approssimative e **non** vengono da `misure.py`.

## Indice dei ritagli

| File | Fonte | PDF p. | Ritaglio (pt) | dpi |
|---|---|---|---|---|
| `modulare_01_guerra-uni9511-generatore-gas.png` | Guerra, UNI 9511 | 2 | 72,321–250,357 | 250 |
| `modulare_01b_guerra-uni9511-apparecchio-generale.png` | Guerra, UNI 9511 | 2 | 72,188–250,232 | 250 |
| `modulare_02_divisionenergia-TH-GM-weishaupt-4moduli.png` | Division Energia IM01 | 1 | 640,815–1195,1125 | 200 |
| `modulare_02b_divisionenergia-TH-legenda-GM-MT.png` | Division Energia IM01 | 1 | 535,1282–1005,1339.5 | 200 |
| `modulare_03_baltur-GTMIX-MK-schema-modulare.png` | Baltur GTMIX MK | 3 | 80,498–545,655 | 250 |
| `modulare_04_studioglt-SF01-GC1-2-due-moduli-murali.png` | Studio GLT SF_01 | 1 | 140,535–345,650 | 250 |
| `modulare_04b_studioglt-SF01-legenda-GC1-2.png` | Studio GLT SF_01 | 1 | 862,222–1120,248 | 250 |
| `modulare_05_unical-modulexEXT-catalogo2024-p19-generatore.png` | Unical catalogo 2024 | 19 | 32,452–300,640 | 220 |
| `modulare_05b_unical-modulexEXT-catalogo2024-p19-schema-INAIL.png` | Unical catalogo 2024 | 19 | 32,452–563,640 | 170 |
| `modulare_06_unical-modulex-depliant2009-p12-scatola-unica.png` | Unical dépliant 2009 | 12 | 28,708–152,776 | 300 |
| `modulare_07_caleffi-schema1.103-due-moduli-in-involucro.png` | Caleffi 1.103 | 1 | 318,178–700,540 | 170 |
| `modulare_07b_caleffi-schema1.101-due-caldaie-separate.png` | Caleffi 1.101 | 1 | 290,110–1000,660 | 110 |
| `modulare_08_ancona-teatromuse-MEL17-generatore-modulare-3moduli.png` | Ancona M.EL.17 | 1 | 3575,1195–4095,1560 | 150 |
| `modulare_08b_ancona-teatromuse-MEL17-legenda-1.png` | Ancona M.EL.17 | 1 | 2490,668–2950,700 | 250 |
| `modulare_09_biasi-multiparvaCondH-p13-master-slave-collettori.png` | Biasi Multiparva Cond H | 13 | 62,172–300,385 | 220 |
| `modulare_09b_biasi-multiparvaCondH-p13-legenda-1-6.png` | Biasi Multiparva Cond H | 13 | 55,428–200,523 | 220 |
