# Solare termico: collettore, campo di collettori, bollitore bivalente. Ricognizione delle fonti

> **Note di un agente di ricerca, 24 settembre 2026** (`REL-003`, agenti paralleli in sessione, D-152), riportate come le ha scritte. Quello che un agente riferisce non è una fonte finché la sessione non l'ha guardato: la sessione ha **riaperto i ritagli delle fonti da cui vengono le forme** e ha **riscaricato ogni fonte registrata** (SRC-030 … SRC-040, SRC-009) dall'indirizzo citato, controllando la pagina. **Nel repository ci sono soltanto i ritagli elencati nel rapporto** (`docs/fonti/ricerche/reports/Simboli nuovi della prima release.md`). Gli altri nomi di ritaglio citati qui sotto, e le cartelle di lavoro dell'agente (`work/`, `_work/`, `_download_non_pubblicare/`), sono rimasti fuori: pagine intere, figure intere, o tavole che ne vietano la riproduzione (Division Energia, Comune di Parma). Si rigenerano dalla fonte, alla pagina indicata.

Ricerca del 24/09/2026, prefisso dei ritagli `solare`. Per ogni fonte dico di che cosa si tratta:
**[NORMA-SEC]** è la UNI 9511 letta attraverso una fonte secondaria, **[PUBBLICO]** il progetto di un ente pubblico,
**[COSTRUTTORE]** la documentazione di un fabbricante, **[DIDATTICA]** il materiale didattico.
«PDF p. N» è la pagina del file, «pag. N» la numerazione a stampa.

Tutti i ritagli sono in questa cartella e li ho aperti uno per uno prima di descriverli. I colori delle linee,
dove lo dico, li ho letti dai tratti vettoriali del PDF (PyMuPDF, `get_drawings`); per Beretta li ho verificati
anche campionando i pixel. Nessuna pagina intera è salvata come ritaglio. Le pagine intere che ho guardato stanno
in `work/`, che **non va nel repository**.

---

## 1. [NORMA-SEC] UNI 9511, attraverso le tavole del prof. Guerra (SRC-015)

- «Norma UNI 9511 — Segni grafici», tabelle utili, prof. Guerra. PDF di 10 pagine, scansioni senza testo
  (metadati: creato l'08/01/2003). URL:
  https://professoreguerra.altervista.org/alterpages/files/UniIdraulica1.pdf. Copia locale:
  `ricerca/guerra-uni9511.pdf`.
- Ho sfogliato tutte e dieci le pagine: valvolame; apparecchiature per acqua, gas e vapore; unità di misura;
  giunzioni; canali; trattamento dell'aria; UNI 9182 sanitari; UNI 9511/1 regolazione e sonde; UNI 9511/3.
  **Nessun segno per il collettore solare** e **nessun segno per il bollitore a due serpentini**.
- **PDF p. 2** («Apparecchiatura per la distribuzione di acqua, gas e vapore»), segno «**Scambiatore di calore
  ad accumulo**». Il contorno è una capsula verticale: un rettangolo chiuso sopra e sotto da due calotte
  semicircolari, con proporzione di circa 1:2,5 fra larghezza e altezza. Dentro c'è un serpentino disegnato come
  una spezzata a zig-zag fra due orizzontali. Le due orizzontali escono a **sinistra**, attraversano il mantello
  e stanno nella fascia centrale, a circa il 35% e il 58% dell'altezza: sono gli attacchi del primario. A
  **destra** ci sono due tratti brevi, uno alto sotto la calotta superiore e uno basso sopra quella inferiore: sono
  gli attacchi dell'acqua. Il segno ha **un solo** serpentino. → `solare_01_guerra-uni9511-p2-accumulo.png`
- **PDF p. 9** (UNI 9511/1, «Segni grafici per sonde e trasmettitori da ambiente o da esterno»), segno «Sonda di
  temperatura o climatica per esterno sensibile anche all'irraggiamento solare». È un cerchio con la T appoggiato
  a una parete tratteggiata. Due **frecce parallele oblique**, dall'alto a sinistra verso il basso a destra,
  puntano sul cerchio. Nelle tavole viste è l'unico modo in cui la UNI 9511 rappresenta l'irraggiamento solare.
  → `solare_02_guerra-uni9511-p9-irraggiamento.png`

## 2. [NORMA-SEC] UNI 9511, attraverso le tavole pubblicate da Oppo (SRC-016)

- Oppo S.r.l., «Simboli grafici Idraulica». L'indice è https://www.oppo.it/disegni/a_disegni-elenco.html e
  conta dieci tabelle; nessuna riguarda generatori, scambiatori, accumuli o collettori.
  - Tab. 1 «Tubazioni, Canalizzazioni»: https://www.oppo.it/disegni/simboli_idra_1.htm, immagine
    `img/simboli_idra_1.jpg`;
  - Tab. 8 «Simboli per l'identificazione della natura del fluido convogliato»:
    https://www.oppo.it/disegni/simboli_idra_8.htm, immagine `img/simb-idra-8.gif`.
- I PDF e i DWG si scaricano con un modulo in due passaggi. Da curl il modulo restituisce solo pagine HTML,
  quindi **ho letto le immagini delle pagine web, non i PDF**.
- **Tab. 1, prima riga**, testuale: «Simbolo grafico generale per le tubazioni di progetto (spessore 0,50 mm). La
  natura dei fluidi deve essere specificata come descritto nella Tab. 8 o precisato sul disegno con apposita
  legenda.» Il segno di esempio sono tre linee: una continua, una tratteggiata e una a tratto e punto.
  → `solare_06_oppo-uni9511-tab1-tubazioni-legenda.png`
- **Tab. 8**, trascritta dall'immagine. Sigle:
  - A…\* aria compressa;
  - AC acqua calda (T ≤ 373 K);
  - ACR acqua calda e/o refrigerata;
  - AR acqua refrigerata;
  - AT acqua trattata;
  - CG condensa di vapore acqueo, flusso a gravità;
  - CH₄ gas metano;
  - CP condensa pompata;
  - D drenaggio di apparecchi (spurgo);
  - G gas generico;
  - GM gas manufatturato;
  - GPL;
  - SP sfogo di atmosfera;
  - V…\* vapore acqueo.

  L'asterisco vuol dire che al posto dei puntini si indica la pressione in kPa. **Nessuna sigla per il fluido
  solare, il glicole o l'antigelo.**
  Non ho ritagliato la Tab. 8 perché sarebbe la tabella intera; la cito e basta.

## 3. [PUBBLICO] Comune di Parma: tavole IM05 e IM06

- Comune di Parma, Settore Lavori Pubblici e Sismica, «Impianto Signorini ex Cral AUSL — Nuovo blocco spogliatoi
  (Obiettivo Parma Città dello Sport)», **PROGETTO ESECUTIVO**, emissione dicembre 2019.
  - Progetto dell'impianto meccanico: ing. Nicola Bedotti. RUP: ing. Alice Bonati.
  - CUP I98B18000170004. Tavole firmate digitalmente il 10/07/2020.
  - Le tavole portano la dicitura «E' vietata la riproduzione e diffusione in qualsiasi forma»: tengo solo
    ritagli di singoli segni.
- **IM05** «Schemi funzionali impianti meccanici»:
  https://atti.comune.parma.it/AttiVisualizzatore/download/allegato/217147?fId=217148. PDF p. 1, un foglio
  vettoriale di 1684×1191 pt. A sinistra c'è lo «**SCHEMA FUNZIONALE IMPIANTO PRODUZIONE ACQUA CALDA
  SANITARIA**».
- **IM06** «Impianto idrico-sanitario e scarichi», pianta 1:50:
  https://atti.comune.parma.it/AttiVisualizzatore/download/allegato/217149?fId=217150. PDF p. 1.
- **Collettori.** Nota: «N°5 pannelli solari, marca Viessmann, Vitosol 100-FM, mod. SV1F».
  - **Vista frontale**: cinque rettangoli verticali affiancati con proporzione di circa 0,6 fra larghezza e altezza.
    Ognuno ha una cornice esterna e un rettangolo interno (il vetro) con tre brevi tratti obliqui azzurri, due
    paralleli in alto a sinistra e uno in basso a destra: sono i riflessi del vetro.
  - Niente tubi interni, niente sole né raggi.
  - Il campo sta su un'area grigia tratteggiata, la copertura, con la nota «Predisposizione pannelli solari
    termici».
  - La **mandata** (arancio, continua) esce dall'**angolo in alto a sinistra del primo pannello**. Sopra ha la
    sonda, un cerchio con T collegato da un filo tratteggiato.
  - Il **ritorno** (arancio, tratteggiato) entra nell'**angolo in basso a destra dell'ultimo**. È un collegamento
    in diagonale, con un solo ingresso e una sola uscita per tutto il campo.

  → `solare_20_parma-im05-campo-collettori.png`
- **Gruppo.** «Centralina solare SD1» è un rettangolo grigio sottile che racchiude la centralina e i componenti
  disegnati uno per uno.
  - Sulla mandata (continua): valvola a sfera, termometro, ritegno con freccia ↓.
  - Sul ritorno (tratteggiato): valvola a sfera, termometro, ritegno con freccia ↑, circolatore (cerchio con
    triangolo pieno arancio), valvola a sfera e misuratore di portata.
  - Sono disegnati anche la valvola di sicurezza con lo scarico e una valvola di carico.
  - Il **vaso "VE 50 lt" sta fuori dal riquadro**.

  → `solare_22_parma-im05-gruppo-solare.png`
- **Bollitore.** Nota: «Bollitore bivalente, marca Viessmann o similare, mod. SOLARCELL BIV 750».
  - È disegnato con un contorno da costruttore: mantello rettangolare con il cielo leggermente bombato, vaso
    interno con le testate arrotondate, proporzione del vaso di circa 1:3.
  - I due serpentini sono serie di anse a U. Quello superiore va dal 18% al 41% circa dell'altezza del vaso;
    quello inferiore, più grande, dal 46% al 96%.
  - **Tutti gli attacchi stanno a destra.** Dall'alto:
    1. acqua calda: rosa, tratto e punto, in alto a destra, con un tubo interno che sale fino in cima;
    2. mandata del serpentino superiore dalla caldaia: rosso-arancio, continua;
    3. sonda T;
    4. ritorno del serpentino superiore: rosso-arancio, tratteggiato;
    5. **mandata solare** in cima al serpentino inferiore: arancio, continua, con valvola;
    6. sonda T;
    7. **ritorno solare** in fondo al serpentino inferiore: arancio, tratteggiato, con valvola;
    8. **acqua fredda** in basso a destra: blu, con un tubo interno che scende; sulla linea ci sono il vaso
       "VE 35 lt", la valvola di sicurezza e il ritegno.
  - In cima c'è lo sfiato. A sinistra, in basso, una flangia. **Nessun ricircolo.**

  → `solare_21_parma-im05-bollitore-bivalente.png`
- **Legenda delle tubazioni**, uguale in IM05 e IM06. Colori letti dai tratti vettoriali:

  | Voce | Colore | Tipo di linea |
  |---|---|---|
  | «TUBAZIONE ACQUA RISCALDATA MAN/RIT» | rosso-arancio (1; 0,25; 0) | coppia: continua sopra, tratteggiata a trattini lunghi sotto |
  | «TUBAZIONE GAS METANO» | giallo | continua e tratto-punto |
  | «TUBAZIONE ACQUA FREDDA SANITARIA» | blu | continua e tratto-punto |
  | «TUBAZIONE ACQUA CALDA SANITARIA» | rosa | tratto-punto |
  | «**TUBAZIONE CIRCUITO SOLARE**» | **arancio (1; 0,5; 0)** | coppia: continua (mandata) e tratteggiata a trattini corti (ritorno) |
  | «TUBAZIONE GAS REFRIGERANTE» | verde | continua |
  | «Collegamenti Elettrici» | grigio | tratto-punto |

  Il tubo del circuito solare è il «05 TUBO IN RAME PREISOLATO» (05-22x1,5). → `solare_23_parma-im05-legenda-tubazioni.png`
- La legenda di IM06 lo chiama «B — **Bollitore bivalente con doppi serpentini**».

## 4. [PUBBLICO, peso basso] Università della Campania, PFTE del campus ex Caserma Barducci (Caserta)

- «RELAZIONE Impianto Solare Termico», progetto di fattibilità tecnica ed economica, CUP B28H22000430001, 2024.
  URL:
  https://www.unicampania.it/elaboratipftemulinobarducci/128_Imp.CV.03%20Relazione%20Impianto%20Solare%20Termico.pdf.
  Il disegno è a PDF p. 13 (pag. 12), «Schema dell'impianto — Produzione ACS».
- È un'illustrazione generica. Non ho verificato se venga da un programma di calcolo.
  - Il collettore è un rettangolo blu in vista frontale.
  - Tutti i tubi sono grigi, senza colori per circuito.
  - Il bollitore è un cilindro grigio con una finestra rossa in sezione che mostra due serpentini. **Entrambi sono
    attaccati a sinistra**: quello superiore alla caldaia, quello inferiore al solare.
  - L'acqua calda esce dall'alto.
  - Non c'è legenda.

  → `solare_31_unicampania-pfte-p13-bollitore.png`

## 5. [COSTRUTTORE, quaderno tecnico] Caleffi, *Idraulica* n. 29, «Gli impianti a pannelli solari», dicembre 2005

- 36 pagine. URL:
  https://www.caleffi.com/sites/default/files/media/external-file/Idraulica_29_IT_Gli%20impianti%20a%20pannelli%20solari.pdf,
  collegato dalla pagina https://idraulica.caleffi.com/rivista/29-gli-impianti-pannelli-solari.
  **Verificato: i quaderni Caleffi sul solare esistono, sono il n. 29 e il n. 32.**
- **PDF p. 8 = pag. 8**, «Serbatoi d'accumulo dell'energia solare». Ci sono tre disegni con frecce ed etichette:
  serbatoio ad intercapedine, a semplice serpentino e **a doppio serpentino**. Nel doppio serpentino:
  - il vaso ha le testate ellittiche e sta su piedi, dentro un mantello isolante rettangolare; la proporzione del
    vaso è di circa 1:2,2;
  - il **serpentino superiore** occupa il terzo alto. I suoi attacchi stanno a **destra** e sono etichettati
    «Attacchi circuito caldaia»: entrata in alto con la freccia verso il bollitore, uscita in basso con la freccia
    in fuori;
  - il **serpentino inferiore** occupa il terzo basso. I suoi attacchi stanno a **sinistra** e sono etichettati
    «Attacchi circuito pannelli solari»: entrata in alto, uscita in basso;
  - l'«**Acqua calda**» esce **in alto al centro**, con la freccia verso l'alto;
  - l'«**Acqua fredda**» entra **in basso a destra**, alla quota dell'uscita del serpentino solare ma sul lato
    opposto.

  Testo: «Quelli a doppio serpentino servono, invece, anche per riscaldare l'acqua (se necessario) fino alla
  temperatura d'uso richiesta.» Il semplice serpentino ha lo stesso schema: serpentino in basso a sinistra, fredda
  in basso a destra, calda in alto al centro.
  → `solare_07_caleffi-idraulica29-p8-doppio-serpentino.png`
- **PDF p. 6–7**, disegni di prodotto in vista frontale.
  - «Pannello a fluido liquido con protezione»: cornice, vetro, assorbitore con **tubi verticali** su un collettore
    inferiore; entrata in alto a sinistra con la freccia blu, uscita in alto a destra con la freccia rossa.
    → `solare_09_caleffi-idraulica29-p6-collettore-piano.png`
  - «Pannello a fluido liquido con tubi sotto vuoto»: una cassetta collettore **in alto**, con entrata a sinistra e
    uscita a destra, da cui pendono circa 15 tubi. → `solare_10_caleffi-idraulica29-p7-collettore-sottovuoto.png`
- **PDF p. 11**, schemi 3–5 (non ritagliati). Il collettore è il rettangolo inclinato con sfumatura e frecce rosse
  parallele dei raggi. La sonda «1» sta sull'estremo alto. La mandata è rossa continua e parte dall'alto; il
  ritorno è blu tratteggiato e arriva in basso. Il bollitore sta su piedi, con il serpentino in basso e gli attacchi
  a sinistra.
- **PDF p. 21**, «Collegamento e bilanciamento dei pannelli». Il **campo è disegnato in vista frontale** come una
  matrice di 4 file per 5 pannelli.
  - Ogni pannello è un rettangolo verticale riempito con una sfumatura dal blu al rosso nel verso del flusso.
  - I pannelli sono in serie dentro la fila e le file sono in parallelo.
  - Didascalia: «Bilanciamento rete pannelli con collegamento a tre tubi e con autoflow». Nella variante con
    autoflow c'è un regolatore all'ingresso di ogni fila.
  - Ingresso (cerchio blu) e uscita (cerchio rosso) stanno in basso a sinistra.

  → `solare_08_caleffi-idraulica29-p21-campo-serie-parallelo.png`
- **PDF p. 28**, schema pittorico con richiami (non ritagliato): il «Gruppo solare preassemblato» è disegnato come
  un blocco, con la legenda dei pezzi (valvola di sicurezza, collegamento al vaso, idrometro, rubinetti di
  carico/scarico, termometri con valvola Ballstop, pompa, regolatore e misuratore di portata, sfogo aria,
  coibentazione a guscio).

## 6. [COSTRUTTORE, quaderno tecnico] Caleffi, *Idraulica* n. 32, «Impianti solari — Schemi di realizzazione», giugno 2007

- Autori: M. Doninelli, M. Doninelli, A. Perini. 44 pagine. URL:
  https://www.caleffi.com/sites/default/files/media/external-file/Idraulica_32_IT_Impianti%20solari.pdf. Tutti gli
  schemi portano la dicitura «Schema funzionale non esecutivo».
- **PDF p. 22 = pag. 22**, schema 11, «Impianto autonomo con pannelli solari a circolazione forzata, bollitore a
  doppio serpentino e caldaia a terra per solo riscaldamento».
  - **Collettore.**
    - È un rettangolo lungo e stretto (circa 1:10) inclinato di circa 45°, con l'estremo alto a sinistra, contorno
      nero e riempimento sfumato dal rosso in alto al blu in basso.
    - **Cinque frecce rosse parallele**, i raggi, arrivano da destra in alto perpendicolari al pannello.
    - Niente tubi interni.
    - **La mandata (rossa, continua) parte dall'estremo alto** e ridiscende parallela al pannello. **Il ritorno
      (blu, tratteggiato) entra nell'estremo basso.**

    → `solare_11_caleffi-idraulica32-p22-collettore.png`
  - **Bollitore.**
    - È un vaso a capsula dentro un mantello rettangolare con texture beige.
    - Il **serpentino superiore** (caldaia) ha gli attacchi a **sinistra**: mandata in alto dalla pompa, ritorno in
      basso blu tratteggiato, con la sonda del termostato fra i due.
    - Il **serpentino inferiore** (solare) ha gli attacchi a **destra**: mandata solare rossa in alto, ritorno blu
      tratteggiato in basso.
    - L'**acqua calda** esce **in alto al centro**, in rosso a tratto e punto.
    - L'**acqua fredda** entra **in basso a sinistra**, blu continua, con ritegno.
    - A valle c'è un miscelatore con «M»; l'acqua miscelata è arancio tratteggiata. **Niente ricircolo.**
  - **Gruppo.**
    - È un **blocco grigio unico a spigoli arrotondati** con dentro due colonne: valvole a sfera, ritegni con le
      frecce ↓ e ↑, termometri T, circolatore, misuratore di portata e manometro «M».
    - Valvola di sicurezza, vaso e tanica di raccolta stanno fuori dal blocco.

  → `solare_12_caleffi-idraulica32-p22-bollitore-doppio-serpentino.png` (bollitore e gruppo)
- **PDF p. 24**, schema 13, «Accumulo solare centralizzato».
  - **Due collettori** uguali, ciascuno inclinato e con i suoi raggi, collegati **in parallelo**. Le mandate
    scendono dagli estremi alti e si uniscono in un collettore orizzontale rosso con un pallino di derivazione; i
    ritorni si uniscono in un collettore tratteggiato, anche lui con il pallino.
  - Qui il gruppo **non** è disegnato come blocco: i pezzi stanno in fila sul ritorno.
  - Il bollitore ha un solo serpentino, in basso, con gli attacchi a destra. La calda esce in alto, la fredda entra
    in basso a sinistra. Il **ricircolo** (arancio, tratto e punto sottile) entra **a sinistra, a circa il 40%
    dell'altezza**.

  → `solare_13_caleffi-idraulica32-p24-campo-due-collettori.png`
- **Linee in tutti gli schemi**: mandata rossa continua e ritorno blu tratteggiato, **uguali per il solare e per il
  riscaldamento**; acqua calda rossa a tratto e punto; miscelata arancio tratteggiata; fredda blu continua con le
  frecce; ricircolo arancio. Le etichette di PDF p. 25 e 29 sono «Ricircolo», «Acqua dal solare», «Acqua fredda» e
  «Acqua calda».
- PDF p. 4, sul fluido: «Dove le temperature esterne lo richiedono, vanno utilizzate miscele antigelo».

## 7. [COSTRUTTORE] Caleffi, «Componenti e schemi per impianti a pompa di calore aria-acqua» (SRC-008), PDF p. 14 «Schema esempio - 4»

- Slide «Coffee with Caleffi» (PDF di 24 pagine, 2022; URL nel registro fonti). Voci della slide: «PDC Split —
  Produzione ACS ad accumulo con integrazione pannelli solari — Gruppi di rilancio diretti e miscelati — Accumulo
  inerziale come separatore idraulico».
- Il disegno è pittorico, con volumi e colori.
- **Collettore**:
  - un solo pannello visto di fianco, inclinato di circa 35° e in salita verso destra;
  - l'assorbitore è color crema, con un tubo sfumato dal blu (estremo basso a sinistra) al rosso (estremo alto a
    destra);
  - il **ritorno** (blu) entra nell'estremo basso; la **mandata** (rossa) esce dall'estremo alto, dove c'è uno
    sfiato automatico;
  - su entrambe le linee c'è una valvola a sfera con scarico; il filo della sonda è una linea grigia sottile;
  - niente sole.

  → `solare_03_caleffi25-p14-collettore.png`
- **Bollitore**:
  - mantello grigio rettangolare, vaso con le testate arrotondate, sfumatura dall'arancio al verde;
  - due serpentini ad anse orizzontali, con **tutti gli attacchi dei serpentini a sinistra**;
  - lato sanitario **a destra**: calda in alto a destra, fredda in basso a destra con valvola di sicurezza e vaso;
    miscelatore termostatico.
  - **Anomalia**: qui **il solare va al serpentino SUPERIORE**. La linea rossa dal collettore passa nella colonna
    destra del gruppo e arriva all'attacco alto del serpentino superiore; il ritorno blu torna alla colonna
    sinistra. La pompa di calore va al serpentino **inferiore**. È l'**unico caso**, fra le fonti viste, con il
    solare in alto. Sulla slide non c'è testo che lo spieghi: non so se sia una scelta voluta o una svista.

  → `solare_04_caleffi25-p14-bollitore.png`
- **Gruppo**: disegnato come un prodotto, cioè due colonne su una piastra grigia, un blocco unico. Il vaso è bianco;
  la tanica di raccolta del glicole sta sotto la valvola di sicurezza. → `solare_05_caleffi25-p14-gruppo-circolazione.png`

## 8. [COSTRUTTORE] Cordivari, scheda tecnica «Sistema Termico Solare B2»

- Cordivari, «Sistema termico solare B2 — Sistemi a circolazione forzata per acqua calda sanitaria con doppio
  scambio per integrazione caldaia». PDF di 4 pagine del luglio 2022. URL:
  https://www.cordivari.it/wp-content/uploads/2022/07/Cordivari-Scheda-tecnica-Sistema-Termico-Solare-B2.pdf.
  Il disegno è a PDF p. 3.
- Esempio di installazione con **legenda** (→ `solare_16_cordivari-b2-p3-legenda.png`):
  - 1 Bollitore BOLLY® 2 ST FB;
  - 2 Generatore (caldaia a gas);
  - 3 Vaso di espansione;
  - 4 Circolatore ricircolo ACS;
  - 5 Gruppo di sicurezza idraulico;
  - 6 Miscelatore termostatico;
  - 7 **Gruppo di circolazione solare completo**;
  - 8 **Collettore/i solare/i**;
  - 9 Impianto di riscaldamento;
  - 10 Valvola deviatrice.

  Nota: «Gli esempi di installazione riportati hanno solo scopo illustrativo».
- **Collettori**: due pannelli in **vista frontale**, rettangoli blu scuro con la cornice chiara e circa sette righe
  verticali bianche ciascuno, le strisce dell'assorbitore, affiancati.
  - La mandata (rossa) parte dall'angolo in alto a sinistra del primo pannello.
  - Il ritorno (giallo) arriva sul lato destro del secondo, in alto, e ridiscende passando sotto i pannelli.
- **Gruppo 7**: un'immagine di prodotto, quindi un blocco unico, con il vaso accanto.

  → `solare_14_cordivari-b2-p3-collettori-gruppo.png`
- **Bollitore BOLLY 2 ST FB**:
  - mantello grigio rettangolare e vaso a capsula; due serpentini ad anse grigie, e le ultime spire del serpentino
    inferiore sono oblique;
  - **tutti gli attacchi dei serpentini, e il ricircolo, stanno a SINISTRA**, ognuno con la sua valvola.
    Dall'alto:
    1. mandata caldaia, rossa, in cima al serpentino superiore;
    2. **ricircolo**, giallo, dalla pompa 4, all'altezza del serpentino superiore;
    3. ritorno caldaia, giallo, in fondo al serpentino superiore;
    4. mandata solare, rossa, in cima al serpentino inferiore;
    5. ritorno solare, giallo, in fondo al serpentino inferiore.
  - L'**acqua calda** esce **dall'alto, al centro della calotta**, in giallo con valvola, e va al miscelatore 6.
  - In basso ci sono due linee blu senza etichetta. Una esce dal fondo al centro con una valvola; l'altra parte da
    un punto dentro il vaso, vicino al fondo, ed esce in basso a destra. La mia lettura è che la seconda sia
    l'entrata della fredda e la prima lo scarico, ma **non è verificata**.

  → `solare_15_cordivari-b2-p3-bollitore-bolly2.png`
- **Colori**: rosso per la mandata e giallo per il ritorno, **uguali per il circuito solare e per quello della
  caldaia**. Giallo anche per l'acqua calda sanitaria e per il ricircolo; blu per la fredda. Il circuito solare non
  ha un colore suo.

## 9. [COSTRUTTORE] Beretta, «Schema di impianto puramente indicativo» (sistema ibrido)

- Beretta (gruppo Riello). PDF di 3 pagine, titolo nei metadati «slide 7 MONOBLOCCO HYBRID KIT D», creato il
  28/06/2021. URL: https://www.berettaclima.it/files//progettisti/Beretta.pdf. Il disegno è a PDF p. 1.
- **Legenda dei componenti**:
  - 1 Pompa di calore monoblocco idronico;
  - 2 Caldaia solo riscaldamento;
  - 3 Distributore idraulico BAG HYBRID;
  - 4 Energy Manager REC10;
  - 5 Sonda esterna;
  - 6 Accumulo inerziale;
  - 7 KIT Cronotermostato + Wi-fi BOX;
  - 8 Cronotermostato;
  - 9 Ventilconvettori;
  - 10 **Bollitore sanitario doppio serpentino**;
  - 11 Valvola miscelatrice;
  - 12 **Collettore solare**;
  - 13 **Gruppo idraulico solare con sonde**;
  - 14 Impianto fotovoltaico.
- **Legenda delle linee**. Colori letti dai tratti vettoriali; tutte le linee sono continue, spessore 0,72 pt,
  tranne le connessioni elettriche:

  | Voce | Colore |
  |---|---|
  | Mandata riscaldamento | rosso (1, 0, 0) |
  | Ritorno riscaldamento | blu (0, 0, 1) |
  | Uscita acqua calda | arancio (1; 0,49; 0) |
  | Ingresso acqua fredda | verde (0, 1, 0) |
  | Connessioni elettriche sonde | grigio tratteggiato |
  | **Mandata solare** | **magenta (1, 0, 1)** |
  | **Ritorno solare** | **ciano (0, 1, 1)** |

  → `solare_17_beretta-schema-legenda-linee.png`
- **Incongruenza nella fonte**. Nel disegno la mandata solare è davvero magenta, ma **il ritorno solare è
  disegnato ARANCIO**, il colore dell'«uscita acqua calda», dal fondo del serpentino inferiore, attraverso il
  gruppo 13, fino all'estremo basso del collettore. Ho campionato i pixel della zona: nessun pixel ciano.
- **Collettore 12**: una barra inclinata di circa 45°, in salita verso destra. È il pannello visto di taglio,
  disegnato come prodotto con righe parallele sottili.
  - La mandata parte dall'estremo alto, il ritorno dall'estremo basso.
  - La sonda del collettore, un segno a lecca-lecca con il filo grigio tratteggiato, sta vicino all'estremo alto.
  - Niente sole.

  → `solare_18_beretta-collettore.png`
- **Bollitore 10**: sezione tecnica con vaso bombato su piedi dentro un mantello rettangolare.
  - Il **serpentino superiore** (riscaldamento) ha gli attacchi a **sinistra**: rosso in alto, blu in basso, sonda
    SBS fra i due.
  - L'**acqua calda** esce **in alto a sinistra**, con un tubo interno curvato verso la cima.
  - Il **serpentino inferiore** (solare) ha gli attacchi a **destra**: magenta in alto, arancio in basso, sonda SBI.
  - La **fredda** (verde) entra **in basso a destra**. Nessun ricircolo collegato.
- **Gruppo 13**: disegno di prodotto, cioè la stazione con la centralina accanto, e il vaso «VE».

  → `solare_19_beretta-bollitore-doppio-serpentino-gruppo.png`

## 10. [COSTRUTTORE] Vaillant, «Impianti solari termici — Edizione Settembre 2017 — Informazioni di prodotto e progettazione»

- In testata le pagine dicono «Specifica tecnica solare termico 2017». 190 pagine. URL:
  https://www.vaillant.it/downloads/vgoa-vaillant-it-doc/specifiche-tecniche/solare-termico-4/specificatecnica-solaretermico-09-2017-1067754.pdf.
- **PDF p. 16 = pag. 14**, legenda della numerazione usata negli schemi (→ `solare_28_vaillant-legenda-5-5a-6-7b.png`):
  - 5 «Bollitore di acqua calda sanitaria ad uso domestico monovalente»;
  - 5a «… **bivalente**»;
  - 6 «**Collettore solare (termico)**»;
  - 7b «**Gruppo pompa solare**»;
  - 8g «Vaso di espansione a membrana per **fluido solare/soluzione salina**»;
  - 8h «Vaso di protezione in linea per impianti solari»;
  - 10f «Contenitore di raccolta fluido solare/soluzione salina».
- **PDF p. 19 = pag. 17**, Fig. 17 «0020199448 – Schema idraulico», con la pagina ruotata.
  - **Collettore 6**:
    - un rettangolo in leggera prospettiva, cioè un parallelogramma sottile con lo spessore del bordo, inclinato
      con l'estremo alto a sinistra;
    - la sonda «COL (S5)» sta sull'angolo alto;
    - la **mandata** (**magenta**, continua, freccia ↓) esce dall'angolo alto; il **ritorno** (blu tratteggiato,
      freccia ↑) entra nell'angolo basso;
    - niente sole, niente tubi.
  - **Gruppo 7b**: un rettangolo a spigoli arrotondati che racchiude due colonne con valvole a sfera, termometri,
    ritegni, la pompa «PWM (S7)» e un separatore d'aria; sopra c'è la valvola di sicurezza. Fuori stanno il 10f,
    l'8h e l'8g.

    → `solare_26_vaillant-0020199448-collettore-gruppo.png`
  - **Bollitore 5a**: mantello rettangolare, vaso a capsula, due serpentini a zig-zag di anse. **Gli attacchi sono
    cerchi marcati allineati in colonna** sulla faccia del vaso. Dall'alto:
    1. sonda;
    2. acqua calda, rossa a tratto e punto, verso sinistra;
    3. mandata dell'integrazione, rossa continua, da sinistra, in cima al serpentino superiore;
    4. **ricircolo**, arancio, da sinistra, a metà del serpentino superiore, con la sonda S1;
    5. ritorno dell'integrazione, blu tratteggiato, verso sinistra, in fondo al serpentino superiore;
    6. **mandata solare**, magenta, **da destra**, in cima al serpentino inferiore;
    7. sonda S2;
    8. **ritorno solare**, blu tratteggiato, **verso destra**, in fondo al serpentino inferiore;
    9. **acqua fredda**, verde, da sinistra, sul fondo.

    → `solare_27_vaillant-0020199448-bollitore-bivalente.png`
  - **Colori** letti dai tratti: rosso, blu scuro, verde (fredda), arancio (ricircolo) e **magenta (0,93; 0,21;
    0,54), usato solo sulla mandata solare**. Il ritorno solare è blu tratteggiato come ogni altro ritorno. Nel
    documento **non ho trovato una legenda delle linee**.
- **PDF p. 79 = pag. 77**, Fig. 75 «Dimensioni degli attacchi per auroSTOR VIH S da 750 a 2000», con legenda.
  - È il bollitore **bivalente reale**: **tutti gli attacchi stanno su un lato**.
  - Dal basso, con le quote del modello VIH S 750:
    1. n. 6 raccordo acqua fredda, 140 mm;
    2. n. 7 **ritorno solare**, 240 mm;
    3. n. 8 **mandata solare**, 690 mm;
    4. n. 9 ritorno riscaldamento, 1095 mm;
    5. n. 10 **raccordo per ricircolo**, 1207 mm;
    6. n. 11 mandata riscaldamento, 1500 mm;
    7. n. 12 raccordo acqua calda, 1600 mm.
  - La vista frontale mostra i due serpentini, con quello solare in basso.

  → `solare_24_vaillant-auroSTOR-VIHS-attacchi.png`, `solare_25_vaillant-auroSTOR-VIHS-legenda-attacchi.png`

## 11. [COSTRUTTORE, Germania] Wolf GmbH, schemi idraulici («Installationsprinzip»)

- Wolf GmbH, Zeichn.-Nr. **32-52-006-305**, Index 02, 29/02/2024 (CHA-16/20, CHA-20/24, CGB-11/20/24,
  BSP-W-SL1000). URL: https://konfig.wolf.eu/hydraulik/resources/pdf/32-52-006-305.pdf, PDF p. 1. Lo stesso segno
  compare nel 32-52-006-012, Index 02, del 15/01/2011.
- **Collettore**:
  - è un **rettangolo vuoto inclinato** di circa 45°, con proporzione di circa 1:5–1:6 e l'estremo alto a sinistra;
  - dentro, vicino agli estremi, ci sono **due cerchietti**, gli attacchi: quello alto è la mandata, quello basso il
    ritorno;
  - sull'angolo alto c'è un quadratino nero pieno, il pozzetto della sonda S/SFK1;
  - in alto a destra c'è **un sole**, un cerchio con circa nove raggi;
  - la mandata (rossa) va dall'attacco alto a uno sfiato («Entlüfter», un rettangolino verticale con la croce) e poi
    scende; il ritorno (azzurro) entra nell'attacco basso.
- **Gruppo**:
  - un **riquadro tratteggiato a L** racchiude ritegni, intercettazioni, la pompa (S/SKP1), il misuratore di
    portata, il manometro e la valvola di sicurezza;
  - fuori dal riquadro stanno il vaso a membrana, con la valvola a cappuccio, e l'«Ablauftrichter mit
    Auffangbehälter für Solarflüssigkeit» (imbuto di scarico sopra un rettangolo).

  → `solare_29_wolf-32-52-006-305-collettore-gruppo.png`
- Colori: mandata rossa e ritorno azzurro come in tutti gli altri circuiti; fredda verde, calda arancio. **Nessun
  colore proprio per il solare.**
- Legenda «**Symbole Hydraulikschemen**», Index 08, 19/04/2023:
  https://konfig.wolf.eu/hydraulik/resources/pdf/Legende_Symbole.pdf, PDF p. 2. **Non contiene il segno del
  collettore.** Contiene l'«Ablauftrichter mit Auffangbehälter für Solarflüssigkeit», cioè l'imbuto di scarico
  con il contenitore di raccolta del fluido solare. → `solare_30_wolf-legende-ablauftrichter-solarfluessigkeit.png`
- A PDF p. 1 ci sono le sigle: SFK sonda del collettore, SFS sonda del bollitore solare, SKP pompa del circuito
  solare, SM1-2/SM2-2 moduli solari.
- L'accumulo di questi schemi è un serbatoio stratificato (BSP), **non** un bollitore bivalente: per il bollitore
  Wolf non serve.

## 12. [COSTRUTTORE] Junkers (Bosch), «Energie rinnovabili - Solare termico — Esempi di impianti (schemi di principio)»

- È un capitolo di catalogo, pag. 107–114, PDF di 8 pagine del 2008. **La copia sta su un sito terzo**, non su
  quello Junkers o Bosch, quindi l'edizione non è verificata:
  https://climanetonline.it/public/allegati/schemi_impianto_multifamily.pdf. Il disegno che uso è a PDF p. 3 =
  pag. 109, «Produzione ACS con bollitore bivalente e regolazione TDS».
- La legenda è a sigle: AGS5 Stazione solare, SP Pompa circuito solare, SAG Vaso d'espansione, AB Contenitore di
  raccolta, SB Valvola di ritegno, SV Valvola di sicurezza, E Rubinetto di scarico/riempimento, LA Separatore
  d'aria, RE Regolatore di portata, TWM Miscelatore termostatico, WW Uscita acqua calda, KW Ingresso acqua fredda.
- **Collettori**: due pannelli in vista frontale, cornice grigia e vetro con due tratti obliqui. La **mandata**
  (rossa) esce dall'**angolo in alto a sinistra del primo**, dove sta la sonda T1; il **ritorno** (blu
  tratteggiato) entra nell'**angolo in basso a destra del secondo**. È un collegamento in diagonale, come a Parma.
- **Stazione AGS5/TDS100**: un **rettangolo grigio**, un blocco con i pezzi disegnati dentro. AB e SAG stanno
  fuori.

  → `solare_32_junkers-p109-collettori-stazione.png`
- **Bollitore «SK …solar»**: mantello giallo e vaso a capsula sfumato, due serpentini. **Tutti gli attacchi stanno
  a DESTRA**:
  - la calda esce in alto e va al TWM;
  - il serpentino superiore è collegato alla caldaia con linee a tratto e punto rosse e blu, con il blu
    sull'attacco alto: **dal disegno non si capisce il verso**; fra i due attacchi c'è la sonda SF;
  - il serpentino inferiore ha la mandata solare in alto (rossa continua) e il ritorno solare in basso (blu
    tratteggiato); la sonda T2 sta sul serpentino solare;
  - la fredda (azzurra) entra in basso a destra.

  → `solare_33_junkers-p109-bollitore-bivalente.png`
- **Colori**: il solare è rosso continuo e blu tratteggiato, come un primario qualunque; il circuito della caldaia
  al serpentino è a tratto e punto. Non c'è una legenda delle linee.

## 13. Fonti viste e scartate, o non verificate

- **Senza solare**, quindi inutili per questa ricerca:
  - [PUBBLICO] Comune di Carrara, PD.IM.03.00 «Centrale termica — schema funzionale», scuola M. Buonarroti,
    progetto definitivo, aprile 2023:
    http://servizi.comune.carrara.ms.it/buonarroti_definitivo/2021_llppe_038_pd_IMPIANTI%20TERMO-MECCANICI/PD.IM.03.00%20-%20Centrale%20termica%20-%20schema%20funzionale.pdf.
    Nella legenda compare solo la pompa di calore ACS con «scambiatore a serpentino per integrazione solare»;
    collettori non ce ne sono.
  - [PUBBLICO] Comune di Trezzano, schema funzionale centrale termica:
    https://trezzano.e-pal.it/AttiVisualizzatore/download/allegato/837815?fId=837822&sbustato=true.
  - [PUBBLICO] Provincia di Ravenna, SM03 Oriani, SA02 ITI Baldini, SM04 Ballardini (SRC-010).
  - [PUBBLICO] Unione Appennino Reggiano, T09, Casa della Salute:
    https://www.unioneappennino.re.it/wp-content/uploads/2018/04/TAVOLA-T09-SCHEMA-FUNZIONALE-IMPIANTO-TERMICO.pdf.
  - [PUBBLICO] Comune di Morra De Sanctis, IM-08, zona piscina terapeutica:
    https://www.comune.morradesanctis.av.it/it-it/download/im-08-schema-funzionale-centrale-termica-18711-2-1248-3f148e03e545bdbe4025f1c3ebc55d8e.
  - [PUBBLICO] GSE, «Il solare termico (2C) nelle regole applicative»: solo testo, nessuno schema.
- **Non esaminate a fondo**:
  - Studio Sabattini, pratica depositata al Comune di San Lazzaro, 2015:
    https://www.studiosabattini.it/download/progetto/Tavola1Schemacentraletermica.pdf. È una scansione di 26
    pagine; ho guardato solo le prime due.
  - Manuale ACCA «Impianti solari termici»:
    http://download.acca.it/BibLus-net/VecchiAllegatiBiblus/Approfondimenti_Tecnici/Manuale_Impianti_%20Solari_%20Termici_73.pdf.
- **Vista, ma non usata come prova**:
  - [DIDATTICA] CT Energia (SRC-011), PDF p. 4–5. Sono slide che riproducono schemi di un costruttore: sulla p. 5
    si vede il logo Tiemme, ma l'attribuzione non è verificata. Collettori in vista frontale e linee del solare
    magenta, **senza legenda** e a bassa risoluzione.
- **ISO 14617-11:2002**, «Devices for heat transfer and heat engines»: potrebbe contenere un segno di collettore
  solare, ma **non ho trovato un'anteprima pubblica**. Nelle anteprime iTeh della ISO 14617-1 (2005 e 2025) la
  parola «solar» non compare. **Non verificato.**

---

# Sintesi

## A. Il collettore solare

**Nella UNI 9511 non c'è.** Non c'è nelle dieci tavole di Guerra e nemmeno nelle dieci tabelle di Oppo. L'unico
precedente normativo per il sole sono le **due frecce parallele oblique** della «sonda … sensibile anche
all'irraggiamento solare» (`solare_02`).

Nella pratica ci sono due forme.

1. **Il pannello visto di fianco: un rettangolo lungo e stretto inclinato di 35–45°**, senza tubi dentro.
   - Caleffi *Idraulica* 32: circa 1:10, con sfumatura rosso-blu e frecce dei raggi (`solare_11`).
   - Wolf: circa 1:5, vuoto, con i due cerchietti degli attacchi e il sole (`solare_29`).
   - Vaillant: in leggera prospettiva (`solare_26`).
   - Beretta, Caleffi SRC-008: disegno di prodotto (`solare_18`, `solare_03`).

   **La mandata esce sempre dall'estremo alto e il ritorno entra da quello basso.** La sonda del collettore sta
   sull'estremo alto: Wolf S/SFK, Vaillant COL (S5), Caleffi sonda «1», Beretta. Il verso dell'inclinazione
   cambia da fonte a fonte, a seconda di dove va la mandata.
2. **Il pannello visto di fronte: un rettangolo verticale** con proporzione di circa 0,6.
   - Parma: cornice doppia e riflessi del vetro.
   - Junkers: lo stesso.
   - Cordivari: disegno di prodotto con le strisce verticali.

**Sole o raggi.** Caleffi disegna 4–5 frecce rosse parallele, perpendicolari al pannello (*Idraulica* 29 e 32);
Wolf un sole con i raggi. Tutti gli altri non disegnano niente, e il progetto pubblico (Parma) nemmeno.

**Tubi interni** li hanno solo i disegni di prodotto: nel pannello piano un'arpa di tubi verticali, nel sottovuoto
tubi appesi a una cassetta in alto (Caleffi *Idraulica* 29, `solare_09` e `solare_10`). **Nessuno schema funzionale
distingue il piano dal sottovuoto**: il tipo lo dice la nota, come a Parma con «Vitosol 100-FM».

Le fonti migliori: **Caleffi *Idraulica* 32, PDF p. 22** (`solare_11`), **Wolf 32-52-006-305** (`solare_29`),
**Parma IM05** per la vista frontale (`solare_20`).

## B. Il campo di più collettori

Tre varianti.

1. **Pannelli inclinati ripetuti, in parallelo**, con un collettore orizzontale di mandata e uno di ritorno e un
   pallino in ogni derivazione (Caleffi *Idraulica* 32, PDF p. 24, `solare_13`).
2. **Una fila di pannelli visti di fronte, affiancati, con un solo ingresso e una sola uscita in diagonale**: la
   mandata dall'angolo alto del primo, il ritorno nell'angolo basso dell'ultimo. Lo fanno Parma con cinque pannelli
   (`solare_20`) e Junkers con due (`solare_32`); in Cordivari il ritorno arriva sul lato destro (`solare_14`).
3. **Una matrice di file e colonne**: serie dentro la fila, file in parallelo a tre tubi (ritorno inverso) oppure a
   due tubi con autoflow. La sfumatura dal blu al rosso dà il verso (Caleffi *Idraulica* 29, PDF p. 21,
   `solare_08`).

Il numero dei pannelli sta nella nota: «N°5 pannelli solari», a Parma.

## C. Il bollitore bivalente

**La forma ricorrente** è un vaso verticale a capsula, spesso dentro un mantello rettangolare, con **due serpentini
disegnati ad anse o a zig-zag**.

- **Solare sotto**, di solito il serpentino più grande; **integrazione sopra**.
- Ogni serpentino ha la **mandata in alto e il ritorno in basso**.
- L'**acqua calda esce in alto**, al centro della calotta o in alto su un fianco; la **fredda entra in basso**.
- L'**unica eccezione** è Caleffi SRC-008, PDF p. 14: il solare va al serpentino superiore e la pompa di calore
  a quello inferiore (`solare_04`).

**L'ordine fisico degli attacchi**, dal bollitore Vaillant auroSTOR VIH S, con tutti gli attacchi su un lato
(`solare_24`, `solare_25`). Dal basso:
1. fredda;
2. ritorno solare;
3. mandata solare;
4. ritorno integrazione;
5. **ricircolo**;
6. mandata integrazione;
7. calda.

**Il ricircolo** entra all'altezza del serpentino superiore, fra i suoi due attacchi e dallo stesso lato: così in
Vaillant, sia nell'oggetto sia nello schema (`solare_27`), e in Cordivari (`solare_15`). In Caleffi *Idraulica*
32, PDF p. 24, con un solo serpentino, entra a sinistra a circa il 40% dell'altezza.

**Il lato degli attacchi ha due varianti.**

1. **Tutto dallo stesso lato**:
   - Cordivari: tutto a sinistra, ricircolo compreso; calda in alto al centro (`solare_15`).
   - Parma: tutto a destra, calda e fredda comprese (`solare_21`).
   - Junkers: tutto a destra (`solare_33`).
   - Unicampania: i serpentini a sinistra (`solare_31`).
   - Caleffi SRC-008: i serpentini a sinistra, il sanitario a destra (`solare_04`).
   - Il bollitore reale di Vaillant ha tutto su un lato (`solare_24`).
2. **I serpentini su lati opposti, ognuno verso la sua sorgente**:
   - Caleffi *Idraulica* 29: solare a sinistra, caldaia a destra, fredda in basso a destra (`solare_07`).
   - Caleffi *Idraulica* 32: caldaia a sinistra, solare a destra, fredda in basso a sinistra (`solare_12`).
   - Beretta: riscaldamento a sinistra, solare a destra, fredda in basso a destra, calda in alto a sinistra
     (`solare_19`).
   - Vaillant, nello schema: attacchi in colonna, linee del solare da destra e le altre da sinistra (`solare_27`).

**La UNI 9511** ha soltanto lo «scambiatore di calore ad accumulo» con **un** serpentino, attacchi del primario a
sinistra e del secondario a destra (`solare_01`). **Un segno a due serpentini non c'è.**

**I nomi**: «bollitore bivalente» (Parma IM05, Vaillant 5a); «bollitore bivalente con doppi serpentini» (Parma
IM06); «bollitore (sanitario) a doppio serpentino» (Caleffi *Idraulica* 32, Beretta); «serbatoio a doppio
serpentino» (Caleffi *Idraulica* 29).

**Rispetto al simbolo che il progetto ha già** (`dhw-cylinder`: serpentino a sinistra nella metà alta, fredda in
basso a sinistra, calda in alto, ricircolo e sonda a destra), le fonti che mettono tutto a sinistra (Cordivari,
Unicampania) sono le più vicine. Però in Vaillant e in Cordivari il ricircolo sta dal lato dei serpentini, non dal
lato opposto. Rilevo il fatto; la decisione è del PO.

Le fonti migliori: **Caleffi *Idraulica* 29, PDF p. 8** (`solare_07`), **Vaillant, PDF p. 79 e p. 19**
(`solare_24`, `solare_25`, `solare_27`), **Parma IM05** (`solare_21`) oppure Cordivari B2 (`solare_15`).

## D. Colore e tipo di linea del circuito solare (per la decisione del PO)

**Una convenzione comune non c'è.**

- **UNI 9511** (Oppo, Tab. 1 e Tab. 8): il fluido si indica con una sigla o con la legenda, e nella Tab. 8 **non
  c'è una sigla per il fluido solare o glicolato** (`solare_06`).
- **Progetto pubblico, Comune di Parma, IM05 e IM06**: la voce «**TUBAZIONE CIRCUITO SOLARE**» è una **coppia di
  linee arancio**, **continua per la mandata e tratteggiata per il ritorno**. Il colore è diverso da «ACQUA
  RISCALDATA MAN/RIT», che è rosso-arancio, ma la convenzione continua/tratteggiata è la stessa (`solare_23`).
  **È l'unica legenda pubblica trovata che dà al solare una voce e un colore suoi.**
- **Beretta**: in legenda la «**Mandata solare**» è **magenta** e il «**Ritorno solare**» è **ciano**, tutte linee
  continue. Nel disegno però il ritorno è arancio (`solare_17`).
- **Vaillant**: la mandata solare è **magenta** e il ritorno è blu tratteggiato come gli altri ritorni. Non c'è una
  legenda delle linee (`solare_26`).
- **Nessun colore proprio**:
  - Caleffi, *Idraulica* 29 e 32 e SRC-008: rosso e blu tratteggiato come il riscaldamento;
  - Cordivari: rosso e giallo come la caldaia;
  - Wolf: rosso e azzurro;
  - Junkers: rosso e blu tratteggiato, con il circuito della caldaia a tratto e punto.
- **Come lo chiamano**: «circuito solare», «tubazione circuito solare», «mandata solare / ritorno solare», «fluido
  solare/soluzione salina» (Vaillant), «miscele antigelo» (Caleffi), «Solarflüssigkeit» (Wolf). **Nessuna legenda
  vista scrive «glicole».**

Quando il solare ha un colore suo, è un colore caldo o violaceo diverso da quello del riscaldamento: **arancio**
nel progetto pubblico, **magenta** in due costruttori.

## E. Il gruppo di circolazione solare è disegnato come blocco unico?

**Di solito sì.** I singoli pezzi sono disegnati dentro un contorno:

- un blocco grigio (Caleffi *Idraulica* 32 p. 22, Junkers AGS5);
- un rettangolo sottile (Parma, «Centralina solare SD1»);
- un rettangolo arrotondato (Vaillant 7b);
- un riquadro tratteggiato (Wolf).

Oppure è un'immagine di prodotto: Caleffi SRC-008, Cordivari 7 «Gruppo di circolazione solare completo», Beretta
13 «Gruppo idraulico solare con sonde».

**Il vaso e il contenitore di raccolta stanno sempre fuori dal contorno.** L'eccezione è Caleffi *Idraulica* 32
p. 24, dove i pezzi stanno in fila sul ritorno, senza contorno.

## F. Che cosa NON ho trovato

- Un segno UNI 9511 del collettore solare o del bollitore a due serpentini: non c'è né in Guerra né in Oppo.
- Un segno ISO 14617 del collettore: la parte 11 potrebbe averlo, ma non ne ho trovato un'anteprima pubblica.
- **Un secondo schema funzionale pubblico con il solare**: ne ho trovato uno solo, Parma IM05. Gli altri schemi
  pubblici aperti non hanno il solare; Unicampania è un'illustrazione generica.
- Uno schema funzionale che distingua graficamente il collettore piano dal sottovuoto.
- Una legenda pubblica che nomini il glicole.
- Una spiegazione del serpentino solare in alto in Caleffi SRC-008, PDF p. 14.
- Le tabelle Oppo in PDF o DWG: le ho lette dalle immagini delle pagine web.

---

## Indice dei ritagli

| File | Fonte | PDF p. |
|---|---|---|
| `solare_01_guerra-uni9511-p2-accumulo.png` | UNI 9511 via Guerra: scambiatore di calore ad accumulo | 2 |
| `solare_02_guerra-uni9511-p9-irraggiamento.png` | UNI 9511 via Guerra: sonda sensibile all'irraggiamento solare | 9 |
| `solare_03_caleffi25-p14-collettore.png` | Caleffi SRC-008: collettore | 14 |
| `solare_04_caleffi25-p14-bollitore.png` | Caleffi SRC-008: bollitore, con il solare sul serpentino alto | 14 |
| `solare_05_caleffi25-p14-gruppo-circolazione.png` | Caleffi SRC-008: gruppo | 14 |
| `solare_06_oppo-uni9511-tab1-tubazioni-legenda.png` | UNI 9511 via Oppo: Tab. 1, prima riga | immagine web |
| `solare_07_caleffi-idraulica29-p8-doppio-serpentino.png` | Caleffi *Idraulica* 29: serbatoio a doppio serpentino | 8 |
| `solare_08_caleffi-idraulica29-p21-campo-serie-parallelo.png` | Caleffi *Idraulica* 29: campo | 21 |
| `solare_09_caleffi-idraulica29-p6-collettore-piano.png` | Caleffi *Idraulica* 29: collettore piano | 6 |
| `solare_10_caleffi-idraulica29-p7-collettore-sottovuoto.png` | Caleffi *Idraulica* 29: collettore sottovuoto | 7 |
| `solare_11_caleffi-idraulica32-p22-collettore.png` | Caleffi *Idraulica* 32: collettore con raggi | 22 |
| `solare_12_caleffi-idraulica32-p22-bollitore-doppio-serpentino.png` | Caleffi *Idraulica* 32: bollitore e gruppo a blocco | 22 |
| `solare_13_caleffi-idraulica32-p24-campo-due-collettori.png` | Caleffi *Idraulica* 32: due collettori in parallelo | 24 |
| `solare_14_cordivari-b2-p3-collettori-gruppo.png` | Cordivari B2: collettori e gruppo | 3 |
| `solare_15_cordivari-b2-p3-bollitore-bolly2.png` | Cordivari B2: BOLLY 2 | 3 |
| `solare_16_cordivari-b2-p3-legenda.png` | Cordivari B2: legenda | 3 |
| `solare_17_beretta-schema-legenda-linee.png` | Beretta: legenda delle linee | 1 |
| `solare_18_beretta-collettore.png` | Beretta: collettore 12 | 1 |
| `solare_19_beretta-bollitore-doppio-serpentino-gruppo.png` | Beretta: bollitore 10 e gruppo 13 | 1 |
| `solare_20_parma-im05-campo-collettori.png` | Parma IM05: campo di 5 collettori | 1 |
| `solare_21_parma-im05-bollitore-bivalente.png` | Parma IM05: bollitore bivalente | 1 |
| `solare_22_parma-im05-gruppo-solare.png` | Parma IM05: centralina e gruppo solare | 1 |
| `solare_23_parma-im05-legenda-tubazioni.png` | Parma IM05: legenda, «TUBAZIONE CIRCUITO SOLARE» | 1 |
| `solare_24_vaillant-auroSTOR-VIHS-attacchi.png` | Vaillant: auroSTOR VIH S, attacchi | 79 |
| `solare_25_vaillant-auroSTOR-VIHS-legenda-attacchi.png` | Vaillant: legenda degli attacchi 6–12 | 79 |
| `solare_26_vaillant-0020199448-collettore-gruppo.png` | Vaillant: collettore 6 e gruppo 7b | 19 |
| `solare_27_vaillant-0020199448-bollitore-bivalente.png` | Vaillant: bollitore 5a | 19 |
| `solare_28_vaillant-legenda-5-5a-6-7b.png` | Vaillant: legenda della numerazione | 16 |
| `solare_29_wolf-32-52-006-305-collettore-gruppo.png` | Wolf: collettore con sole e gruppo tratteggiato | 1 |
| `solare_30_wolf-legende-ablauftrichter-solarfluessigkeit.png` | Wolf, legenda simboli: imbuto con contenitore del fluido solare | 2 |
| `solare_31_unicampania-pfte-p13-bollitore.png` | Unicampania PFTE: bollitore (illustrazione generica) | 13 |
| `solare_32_junkers-p109-collettori-stazione.png` | Junkers: collettori e stazione AGS5 | 3 |
| `solare_33_junkers-p109-bollitore-bivalente.png` | Junkers: bollitore «SK …solar» | 3 |
