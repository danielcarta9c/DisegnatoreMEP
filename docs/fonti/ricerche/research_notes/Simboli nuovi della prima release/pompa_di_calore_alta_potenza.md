# Pompa di calore aria-acqua di alta potenza — ricognizione delle fonti (prefisso `pdc`)

> **Note di un agente di ricerca, 24 settembre 2026** (`REL-003`, agenti paralleli in sessione, D-152), riportate come le ha scritte. Quello che un agente riferisce non è una fonte finché la sessione non l'ha guardato: la sessione ha **riaperto i ritagli delle fonti da cui vengono le forme** e ha **riscaricato ogni fonte registrata** (SRC-030 … SRC-040, SRC-009) dall'indirizzo citato, controllando la pagina. **Nel repository ci sono soltanto i ritagli elencati nel rapporto** (`docs/fonti/ricerche/reports/Simboli nuovi della prima release.md`). Gli altri nomi di ritaglio citati qui sotto, e le cartelle di lavoro dell'agente (`work/`, `_work/`, `_download_non_pubblicare/`), sono rimasti fuori: pagine intere, figure intere, o tavole che ne vietano la riproduzione (Division Energia, Comune di Parma). Si rigenerano dalla fonte, alla pagina indicata.

Ricerca del 24 settembre 2026, agente di ricerca dentro la sessione di sviluppo. Tutto in sola
lettura; nessun file del repository toccato.

**Come leggere.** «PDF p.» è la pagina del file PDF contata da 1 (per le riviste Caleffi coincide col
numero stampato). Le misure in pt sono state lette dai vettori del PDF con pymupdf
(`page.get_drawings()`); dove il segno è un'immagine raster, o dove non sono riuscito a isolare i
vettori, la misura è **a vista sul ritaglio** e lo dico. Ogni ritaglio è stato aperto e guardato
prima di scriverne. Le scritte in rosso piccolo in cima ai ritagli sono mie (fonte e pagina), non
della fonte.

**Il segno di partenza del progetto** (per confronto, letto da
`assets/symbols/heat-pump-air-water.svg`): rettangolo 35,2 × 24 mm (1,47:1), un ventilatore a cerchio
con tre pale a sinistra (diametro 14,4 = 60 % dell'altezza), quattro alette verticali a destra,
mandata e ritorno sul fianco destro — mandata in alto (all'8 % dell'altezza del rettangolo), ritorno
in basso (al 71 %).

---

## 1. UNI 9511, tramite SRC-015 (Guerra) e SRC-016 (Oppo) — norma tramite fonte secondaria

- **Guerra**, «Norma UNI 9511 — Segni grafici», tabelle utili da *Idraulica* (materiale didattico),
  file `ricerca/guerra-uni9511.pdf` (SRC-015,
  <https://professoreguerra.altervista.org/alterpages/files/UniIdraulica1.pdf>). Guardate tutte e
  dieci le pagine (scansioni).
- **Oppo**, tavole UNI 9511, <https://www.oppo.it/disegni/a_disegni-elenco.html> (SRC-016). Letto
  l'elenco dei titoli delle 10 tabelle e guardate le immagini di Tab. 4
  (<https://www.oppo.it/disegni/simboli_idra_4.htm>) e Tab. 9
  (<https://www.oppo.it/disegni/simboli_idra_9.htm>).

**Che cosa si vede.** Nessun segno per la pompa di calore, né per il gruppo frigorifero, né per un
condensatore ad aria, in nessuna delle due riproduzioni. Oppo: le 10 tabelle sono tubazioni,
giunzioni, valvolame, pozzetti e scarichi, sonde, grandezze, fluidi, sigle, strumenti; la Tab. 9
«Simboli letterali di identificazione dei componenti di impianto» è tutta di scarichi (SM, PL, SAU,
…): **nessuna sigla normata per la PdC**. Conferma quanto già scritto nel registro delle fonti il 5
agosto («Le tavole non coprono le macchine»).

I segni della stessa famiglia che la norma ha (Guerra), ritagliati insieme in
**`pdc_01_guerra-uni9511-famiglia.png`**:
- PDF p.2 — «Apparecchio, segno grafico generale (il cerchio per i componenti che hanno parti in
  movimento ed il rettangolo negli altri casi)»; nota: il rettangolo si usa sia verticale sia
  orizzontale;
- PDF p.2 — «Generatore di calore elettrico»: rettangolo verticale con una saetta dentro;
- PDF p.6 — «Ventilatore»: cerchio con un triangolo il cui vertice indica il senso del flusso, sul
  tubo (non le tre pale del segno attuale del progetto);
- PDF p.6 — «Batteria di riscaldamento / di raffreddamento»: rettangolo verticale con cerchio e + / −;
- PDF p.8 (UNI 9511/1) — «Compressore aria»: cerchio con due corde convergenti. È l'unico segno di
  compressore nelle tabelle viste, ed è nella tabella degli organi di regolazione.

**La parte che manca.** Esiste **UNI 9511-4:1989 «Segni grafici per impianti di refrigerazione»**,
in vigore: «Fornisce i segni grafici per le apparecchiature e i collegamenti da utilizzare nei
disegni e negli schemi degli impianti di refrigerazione» (scheda del catalogo,
<https://store.uni.com/uni-9511-4-1989>, letta con WebFetch; la stessa scheda la dice in parziale
accordo con «ISO 4067/4-87»). **Non l'ho vista**: né Guerra né Oppo la riproducono, e le copie in
rete sono caricamenti non ufficiali (Scribd), che non ho aperto. Se un segno normato italiano per il
gruppo frigorifero o la pompa di calore esiste, sta lì: **non verificato**.

---

## 2. Caleffi, *Idraulica* 65 «I sistemi ibridi: caldaia - pompa di calore aria acqua» — costruttore

Caleffi S.p.A., rivista *Idraulica* n. 65, gennaio 2024,
<https://www.caleffi.com/sites/default/files/media/external-file/Idraulica_65_IT_Caldaia%20-%20pompa%20di%20calore%20aria%20acqua.pdf>.
Stesso editore di SRC-008 (fonte del segno domestico) e di SRC-019. Copyright Caleffi, «tutti i
diritti riservati»: nel repository solo i ritagli. Disegni vettoriali.

**È la fonte che mette a confronto le due macchine nella stessa pagina.** PDF p.8, testo:
«PLURIGENERATORE O MODULARI — I plurigeneratori o sistemi modulari sono costituiti da più pompe di
calore e caldaie. […] sono adottati in contesti dove è richiesta una potenzialità di generazione
medio-alta.»

- **Fig. 3 «Sistema ibrido monogeneratore»** (PDF p.8) — `pdc_02_caleffi-idraulica65-p8-fig3-monogeneratore.png`.
  La PdC domestica: cassa 71,7 × 54,6 pt (1,31:1) su **due piedini**; a sinistra (63 % della
  larghezza) il **ventilatore frontale**: griglia a cerchi concentrici con elica a tre pale (cerchio
  35,6 pt, 65 % dell'altezza); a destra un vano (33 %) con la saetta blu in un cerchio in alto e il
  segno della pompa (cerchio con triangolo) sul ritorno. Attacchi sul **fianco destro**, rosso sopra
  (circa 1/3 dell'altezza), blu sotto (circa 1/2) — a vista sul ritaglio.
- **Fig. 4 «Sistema ibrido plurigeneratore»** (PDF p.8) — `pdc_03_caleffi-idraulica65-p8-fig4-plurigeneratore.png`.
  **Due** PdC grandi affiancate, identiche. Ciascuna: cassa 68,3 × 51,1 pt (1,34:1), **senza
  piedini**; a sinistra un **pannello batteria** (57 % della larghezza; riquadro con cornice e
  sfumatura a righe orizzontali fitte), a destra un vano (39 %) con la saetta; **sul lato superiore
  due griglie di ventilatore** piatte (21,8 pt ciascuna, 32 % della larghezza, alte ~3,3 pt), una
  sopra la batteria e una sopra il vano. **Nessun disco frontale.** Attacchi **sul fondo** del vano:
  blu a sinistra, rosso a destra, verso un collettore comune.
- **Fig. 47, «SCHEMA 5 – Impianto di medio-grandi dimensioni: riscaldamento e ACS con doppio
  accumulo»** (PDF p.40) — `pdc_04_caleffi-idraulica65-p40-fig47-medio-grandi.png`. Testo: «Sono
  presenti due pompe di calore […] Lato riscaldamento le due macchine sono collegate ad un collettore».
  Due PdC **impilate**, identiche: cassa 76,0 × 55,8 pt (1,36:1); pannello batteria 57 % a sinistra
  con la saetta in alto a sinistra; vano 39 % a destra con un piccolo display in alto, **lo
  scambiatore a piastre disegnato** (rettangolo verticale con un percorso a zig-zag dal blu in basso
  al rosso in alto) e **la pompa interna sul ritorno** (cerchio con triangolo rivolto verso lo
  scambiatore); **una** griglia di ventilatore sopra (35,2 pt, 46 % della larghezza, sopra la
  batteria). Attacchi sul **fianco destro**: rosso a 55 % dell'altezza, blu a 75 %. La rivista non
  ha una legenda dei colori; che il rosso sia la mandata lo dice il disegno stesso: l'acqua entra dal
  blu spinta dalla pompa ed esce dal rosso dopo lo scambiatore.
- **Fig. 48, «SCHEMA 6 – Impianto di medio-grandi dimensioni, […] raffrescamento con pompa di
  calore»** (PDF p.42) — `pdc_05_caleffi-idraulica65-p42-fig48-R-P.png`. Testo: «Le due pompe di
  calore sono di tipologia diversa, quella polivalente (evidenziata con la lettera P) […] quella
  reversibile (evidenziata con la lettera R)». Stessa cassa (70,7 × 52,0 pt, 1,36:1), stessa
  griglia singola sopra (32,7 pt). **Sigla: una lettera maiuscola in un quadrato bianco** in basso a
  sinistra del pannello batteria. R: due attacchi a destra (rosso 55 %, blu 75 %). **P: quattro
  attacchi** a destra, due scambiatori impilati, ciascuno con la sua coppia rosso sopra / blu sotto
  (pompa interna solo sul secondo).

**Il rilievo che conta.** In Caleffi la macchina grande e quella domestica hanno **quasi la stessa
proporzione** (1,31 contro 1,34–1,36). Non le distingue la forma del contorno: le distinguono **dove
sta il ventilatore** (disco sul fronte contro griglie piatte sul lato superiore), **che cosa occupa la
faccia** (il ventilatore contro la batteria), i piedini, e nella cascata la ripetizione.

---

## 3. Comune di Carrara, Scuola «M. Buonarroti», tav. PD.IM.03.00 — progetto pubblico

«Centrale termica - schema funzionale», progetto definitivo, aprile 2023, CUP F86F22000160001,
<http://servizi.comune.carrara.ms.it/buonarroti_definitivo/2021_llppe_038_pd_IMPIANTI%20TERMO-MECCANICI/PD.IM.03.00%20-%20Centrale%20termica%20-%20schema%20funzionale.pdf>,
PDF p.1 (tavola unica). Vettoriale. Ritaglio: **`pdc_06_carrara-pdim0300-schema-e-legenda.png`**
(il segno nello schema, il segno in legenda, la riga di legenda, la voce 1 dell'elenco).

**La macchina.** Legenda apparecchiature, testuale: «POMPA DI CALORE — Pompa di calore reversibile
aria-acqua per istallazione esterna costituita da due compressori ermetici scroll […] ventilatori
elicoidali […] scambiatore aria-refrigerante del tipo a pacco alettato […] doppio circuito
frigorifero»; «Potenzailità termica= 127,3 kW»; «Pompa di calore aria/acqua tipo AERMEC NRB H° 602 o
equivalente». Elenco apparecchiature: «1 POMPA DI CALORE ARIA/ACQUA».

**Il segno.** È il blocco CAD del costruttore in **prospetto laterale**, lo stesso nello schema e in
legenda: cassa 185,8 × 83,8 pt (**2,22:1**) su due piedini; **batteria a rete (griglia fitta) sull'80 %
della larghezza**; vano tecnico a destra (17 %) con la scritta «PDC» e due tondi; **quattro
ventilatori sul lato superiore**, disegnati come coprivolute con il motore che sporge, equidistanti
sopra la batteria. Attacchi sul **fianco destro, nella parte bassa del vano**: il superiore (a 70 %
dell'altezza) prosegue sulla linea blu, l'inferiore (a 84 %) sulla linea rossa. **La legenda tubazioni
non dice quale colore è la mandata** (riga unica «Riscaldamento/Raffrescamento» con quattro tratti):
quale dei due attacchi sia la mandata **non è verificato**. Richiamo numerato «1» accanto al segno.
Compressori e circuiti sono scritti in legenda, **non disegnati**.

---

## 4. Comune di Padova, «Girotondo», tav. M.02 — progetto pubblico

«Nuovo plesso scolastico "Girotondo" e demolizione dell'esistente», LLPP EDP 2020/073, CUP
H93H19000910004, progetto esecutivo, «Impianti meccanici — Schema funzionale centrali trattamento
aria», tav. M.02, data stampa 08/2021, firmata digitalmente il 29/09/2021,
<https://www.comune.padova.it/bandigara/EDP%202020-073%20costruzione%20Girotondo/APPR_59_EDP_Schema%20funz-%20centrali%20tratt_aria(firmato).pdf>,
PDF p.1, riquadro «Schema funzionale - impianto di climatizzazione ed idrico». Vettoriale.
Ritaglio: **`pdc_07_padova-girotondo-M02-schema.png`**.

**La macchina**, dal riquadro dati accanto al segno: «POMPA DI CALORE ARIA ACQUA (G1) — Potenza
frigorifera: 114,8 kW — Potenza termica: 86,7 kW — COP: 2,73 — Dimensione (LxPxH): 3259x1126x2376 mm —
Numero pompe: 2». **La legenda simboli della tavola non ha una riga per la PdC**: il segno si spiega
col riquadro dati e la sigla in cerchio «G1».

**Il segno.** Prospetto frontale: cassa 291,4 × 137,6 pt (**2,12:1**), su un telaio di base e due piedi
(sembrano supporti antivibranti: non verificato) poggiati su una linea di pavimento tratteggiata; da sinistra: vano quadro elettrico (9,5 %)
con la **saetta**, **due pannelli batteria** a lamelle orizzontali (31 % ciascuno), vano idraulico a
destra (22 %) con **due pompe** (due cerchi sovrapposti con triangolo, attraversati da una
diagonale) e un riquadro tratteggiato che accavalla batteria e vano; **due ventilatori sul lato superiore**, profili bassi a gobba con il motore
che sporge. **Mandata e ritorno sul fianco destro**: sopra (a ~38 % dell'altezza) la linea con la
freccia che **esce** dalla macchina, sotto (a ~70 %) quella con la freccia che **entra** — quindi
**mandata sopra, ritorno sotto**, letto dalle frecce del disegno. Sul **fianco sinistro** una
**seconda coppia di attacchi** (1"1/2, linee siglate «RIR» e «RIM», a ~80 % e ~94 %) verso un
accumulo da 1000 l e un «circuito postriscaldamento»: il significato delle sigle non è scritto in
testo estraibile né in legenda — che sia un recupero di calore è una lettura **non verificata**.

**Un secondo rilievo.** Il blocco disegnato è 2,12:1, la macchina dichiarata è 3259 × 2376 mm (1,37:1):
**il blocco non è in scala con la macchina scelta**. Serve a riconoscerla, non a misurarla.

---

## 5. Albo di Trezzano, tav. P07 — progetto pubblico: una cascata di due

«P07 — Impianti meccanici: centrale termica e cogenerazione — Schema funzionale (ex tavola M06) —
Rev.01 del 28/08/2017», albo online `trezzano.e-pal.it` (il comune non è verificato: il sito risponde
403 alla pagina principale, e la tavola non lo nomina in testo estraibile),
<https://trezzano.e-pal.it/AttiVisualizzatore/download/allegato/837815?fId=837822&sbustato=true>,
PDF p.1. Serve piscina, aule, palestre, mensa (dalle scritte della tavola). Vettoriale.
Ritaglio: **`pdc_08_trezzano-P07-cascata-due-pdc.png`**.

**Le macchine**, dal riquadro dati: «n°2_ POMPE DI CALORE — DATI PER UNA PDC — Potenza termica
nominale: 37,6 KW (EN14511) — BLUEBOX - GEYSER 2 HT41 o similare»: due macchine da 37,6 kW,
75 kW in tutto. Sotto la soglia di taglia della ricerca per macchina, sopra come impianto.

**Il segno.** Prospetto frontale di una monoblocco a **due ventilatori frontali sovrapposti**: cassa
64,7 × 78,5 pt (0,82:1, **verticale**), a sinistra (68 %) due dischi di ventilatore (30,8 pt, cerchi
concentrici con griglia a croce), a destra un vano stretto con la saetta; sopra, collegamento
elettrico «M.elettrica» con sigle **E5** ed **E6**. **Le due macchine sono speculari**: la sinistra ha
gli attacchi sul fianco sinistro, la destra sul destro; in entrambe **rosso sopra, blu sotto**. La
legenda della tavola dà solo «Mandata acqua impianto» (rosso scuro): quale colore sia la mandata
qui **non è verificato**. È la forma delle unità medio-piccole a flusso orizzontale (la stessa di
CT Energia, § 9), non quella della grande taglia.

---

## 6. Aermec, «Multichiller EVO: il sistema intelligente di gestione delle centrali termo-frigorifere» — costruttore

Aermec S.p.A., Servizio Tecnico Commerciale, presentazione, Venezia 9 maggio 2016 (convegno «F-Gas
and Ecodesign», Mestre), ospitata da Carel,
<https://www.carel.com/documents/10191/427888/AERMEC+Multichiller+EVO+Venezia.pdf/9e6800c2-9bea-4deb-8c8e-17e13ef2ec07>,
PDF p.5 (e p.7). Immagine raster nella slide. Ritaglio:
**`pdc_09_aermec-multichiller-2016-p5-GF-in-parallelo.png`**.

**Il testo**, PDF p.5: «La maggior parte delle centrali con più refrigeratori /pompe di calore prevede
una architettura come quella sotto riportata: circuito primario con macchine collegate in parallelo;
una pompa per ogni singola macchina, con valvola di non ritorno sul ramo della stessa».

**Il segno.** Schema di principio: **tre rettangoli verticali vuoti** (circa 0,7:1, a vista),
**siglati «GF1», «GF2», «GF3»** (gruppo frigorifero), tra due collettori; per ogni macchina il
**ritegno sul ramo superiore** e la **pompa sul ramo inferiore**. Niente ventilatori, niente batteria:
la macchina è solo un blocco con la sigla. A PDF p.7 lo stesso schema con due macchine e la
percentuale di carico scritta dentro il rettangolo («GF1 100 %»).

---

## 7. BWP, *Leitfaden Hydraulik* — associazione di settore (Germania)

Bundesverband Wärmepumpe (BWP) e.V., Berlino, *Leitfaden Hydraulik*, 2016 (PDF creato il 9 agosto
2016), <https://www.waermepumpe.de/uploads/media/BWP_LF_Hydraulik_final_web.pdf>. PDF p.26 «Schema 11:
Wärmepumpen als Kaskadenlösung» (disegno raster ruotato di 90° nella pagina), p.27 le opzioni, p.4 la
premessa. Ritaglio: **`pdc_10_bwp-leitfaden-hydraulik-schema11-kaskade.png`** (le quattro macchine,
una ingrandita, le prime due righe di legenda).

**Il testo.** p.4: «Die Hydraulikpläne wurden als firmenübergreifende Standards in der Branche
erarbeitet» — schemi scritti come standard comuni a più costruttori. p.27: lo schema vale per
«Sole/Wasser-, Wasser/Wasser- oder Luft/Wasser-Wärmepumpen».

**Il segno.** Un **segno generico di pompa di calore**, identico per ogni tipo di sorgente: rettangolo
verticale (circa 0,75:1, a vista) con dentro un grande cerchio col **segno del compressore** (due corde)
e un **asterisco** (il cui significato la legenda non spiega). **La sorgente aria non è disegnata**:
nessun ventilatore, nessuna batteria. Attacchi **sul lato superiore**: ritorno (RL, blu tratteggiato)
a sinistra, mandata (VL, rosso) a destra — colori dalla legenda dello schema. **Cascata: quattro segni
identici in fila**, ciascuno con i suoi accessori sul ramo (pompa e ritegno sulla mandata, vaso sul
ritorno) sotto due collettori comuni. Lo stesso segno è usato per la macchina singola (Schema 1,
PDF p.6): la taglia non cambia il segno.

---

## 8. G. Cammarata, «Mini guida per la progettazione di un impianto termotecnico» — didattica

Prof. Ing. Giuliano Cammarata, presentazione, PDF del 5 novembre 2016 (metadati), copia su
<https://energiazero.org/cartelle/aermec/mini%20guida%20progettazione.pdf> — sito di terzi, dentro una
cartella chiamata «aermec»: **provenienza non verificata**, l'autore è quello dei metadati e della
copertina. PDF p.48 «Esempio di Schema funzionale centrale termica», «SCHEMA DI IMPIANTO CON PdC
REVERSIBILE». Immagine raster. Ritaglio: **`pdc_11_cammarata-miniguida-p48-pdc-346kWt.png`**.

**Il segno.** Blocco CAD in prospetto, quasi quadrato (circa 1:1, a vista), pannello grande a
sinistra, vano a destra (circa 27 %), **due ventilatori sul lato superiore**; sotto, la scritta
**«PdC 346kWt»**. Attacchi sul **fianco destro**: in alto (circa 15 % dell'altezza) con la freccia che
esce — **mandata** — in basso (circa 84 %) con la freccia che entra — **ritorno**. Per 346 kW due
ventilatori: anche qui il numero di ventilatori è quello del blocco, non della potenza.

---

## 9. CT Energia, «Segni grafici nella rappresentazione dei componenti» (SRC-011) — didattica

Lezione in slide, 2014 (metadati: autore «Loffredo», 9 aprile 2014), logo Tiemme Sistemi,
<https://www.ctenergia.it/wp-content/uploads/downloads/2014/04/00-Lez.-cap.-1-segni-grafici-nella-rappr.-componenti.pdf>.
Ritaglio: **`pdc_14_ctenergia-p15-nota-e-p6-due-ventilatori.png`**.

- PDF p.15, testuale: **«Quando nella normativa non sussistono segni grafici relativi ad una
  specifica componentistica è opportuno inserire i costruttivi»**. È la regola che spiega i §§ 3, 4,
  8: dove la norma tace, lo schema usa il disegno del costruttore. (Il disegno della stessa pagina è
  una PdC **geotermica**, fuori perimetro: non l'ho ritagliata.)
- PDF p.6: «1 Pompa di calore Acqua Snap 30AV attacchi 1" 16 kW riscaldamento 15 kW
  raffreddamento», disegnata come prospetto frontale a **due dischi di ventilatore sovrapposti** e il
  nome scritto in verticale sul vano: due ventilatori anche a 16 kW. Il numero di dischi frontali
  **non** segnala la grande taglia.

---

## Conferme e fuori perimetro (brevi)

- **Comune di Vinci**, nuova scuola dell'infanzia «Staccia Buratta», progetto esecutivo, «E-MN0
  Schema funzionale centrale termica», aprile 2021,
  <https://vecchiosito.comune.vinci.fi.it/images/stories/maternaVinci/04_IMP_MECCANICI/E-MN0-SCHEMA_FUNZIONALE_CENTRALE_TERMICA_Rev1.pdf>,
  PDF p.1 — **`pdc_12_vinci-E-MN0-pdc-48kW.png`**. «POMPA DI CALORE 48.6 KWt TIPO CLIVET […] KIT
  IDRONICO INTEGRATO COMPRENDENTE ACCUMULO DA 180L E POMPA AD INVERTER» (nota nel disegno; la legenda
  della tavola non ha una riga per la PdC). Stesso stile di Carrara: blocco CAD in prospetto, cassa
  127,7 × 87,7 pt (1,46:1), **due ventilatori sul lato superiore**, pannello grande, vano a sinistra (24 %)
  con il segno della pompa integrata; attacchi sul fianco **sinistro** (il blocco è specchiato verso
  la centrale), arancio sopra e nero sotto con contatore di calore «CC»; colori non verificati.
  Appena sotto la soglia dei 50 kW.
- **Università di Trieste** (amm.units.it), «K1107 — Schema funzionale centrale termica e
  frigorifera», DEA Engineering, 2014,
  <https://amm.units.it/sites/default/files/gar/procedure/Allegato%20D-1%20-%203%20-%20140627%20schema%20funzionale%20CT%20e%20CF.pdf>,
  PDF p.1 — **`pdc_13_units-trieste-gruppo-frigo-fuori-perimetro.png`**. **Non è una PdC**: legenda
  «A — GRUPPO FRIGORIFERO CONDENSATO AD ARIA CON RECUPERO PARZIALE DI CALORE». Unico esempio visto di
  macchina **aperta per funzioni**: celle impilate — «condensatore recupero calore» (serpentina),
  compressore (cerchio con due corde), evaporatore (serpentina, sigla «A»), un cerchio con triangolo
  che la legenda non spiega — con gli attacchi tutti sul fianco destro. Non l'ho trovato per una PdC
  aria-acqua.

## Cercato e non trovato, o non letto

- **Un segno UNI per la PdC**: nessuno nelle due riproduzioni viste; la parte **UNI 9511-4
  (refrigerazione)** esiste ed è in vigore, ma non ne ho trovato una riproduzione lecita: **non vista**.
- **EN 1861:1998** «Refrigerating systems and heat pumps — System flow diagrams and piping and
  instrument diagrams — Layout and symbols» e **ISO 14617-11:2002** «Devices for heat transfer and
  heat engines» (secondo DIN Media sostituita da ISO 14617-2:2025): esistono; l'anteprima iTeh non
  l'ho raggiunta (pagina che si carica solo con JavaScript). **Non lette**: non so se contengano un
  segno di pompa di calore.
- **La vista dall'alto** (rettangolo con i ventilatori a cerchio) in uno schema funzionale: **in
  nessuna fonte vista**; tutti gli schemi disegnano la macchina in prospetto.
- **Le batterie a V** disegnate: in nessuna fonte. Carrara scrive «pacco alettato», non la forma.
- **I compressori disegnati dentro una PdC aria-acqua** in uno schema italiano: in nessuna fonte (solo
  il segno generico BWP e il gruppo frigo di Trieste). Carrara li scrive in legenda.
- **Uno schema pubblico di centrale condominiale con PdC grandi in cascata**: non trovato. Il
  condominio Tower House (SRC-009) è a moduli a gas (Weishaupt WTC-GW 110-A ×4), controllato.
- **Schemateca Mitsubishi Electric** (403) e pagina schemi Caleffi (caricata da JavaScript): non
  raggiunte. Aermec global (i PDF «TVCFX4UI», «SPAECLI39», «TNRP2UI») risponde con un file che non è
  il PDF.
- Viste e scartate perché fuori taglia o fuori tema: Caleffi *Idraulica* 33, 61, 64 (macchine
  domestiche o canalizzate), Caleffi 25 (SRC-008, domestica), Daikin «Impianti centralizzati» 2023
  (cascate di Altherma domestiche), CAV (polivalente da 27 kW), Wolf legenda simboli (nessun segno di
  generatore); WP-System-Modul (CH), «Schemi di funzionamento», letto solo nel testo: nessun
  riferimento alla grande taglia.

La cartella `work/` contiene i PDF scaricati e gli script per rieseguire le misure (`compose2.py`,
`spec*.json`): **non va nel repository** (sono documenti interi, alcuni protetti).

---

## Sintesi

### La forma ricorrente

**Nessuna norma disponibile dà il segno** (UNI 9511 riprodotta: niente; parte 4 non vista). In
assenza, la pratica italiana documentata fa quello che la lezione CT Energia prescrive: «inserire i
costruttivi». La PdC di alta potenza, negli schemi di progetto pubblico e nel costruttore di
componenti, è disegnata così:

1. **in prospetto** (vista di fianco o di fronte), **mai dall'alto**;
2. un **rettangolo orizzontale** con la faccia occupata in gran parte dalla **batteria alettata**
   (griglia, lamelle orizzontali o pannello), e un **vano tecnico** stretto a un'estremità (quadro,
   modulo idraulico, pompe, scambiatore);
3. **i ventilatori sul lato superiore**, come profili bassi o griglie piatte che sporgono sopra il
   bordo: 1–2 in Caleffi, 2 a Padova, Vinci e nella guida Cammarata, 4 a Carrara;
4. **mandata e ritorno sullo stesso fianco, quello del vano, mandata sopra e ritorno sotto** —
   verificato su tre fonti (Caleffi figg. 47–48 dal percorso interno; Padova e Cammarata dalle
   frecce). Nelle altre tre i colori non bastano: Trezzano rosso sopra e blu sotto, Vinci arancio
   sopra e nero sotto, **Carrara al contrario, blu sopra e rosso sotto**; in nessuna delle tre la
   legenda dice quale colore sia la mandata;
5. accanto, una **sigla** (PDC, PdC, G1, un numero d'elenco, R/P) e un **riquadro dati con i kW**.
   Nessuna sigla è normata.

**Che cosa la distingue dalla domestica**, nelle fonti: la domestica ha il **ventilatore a disco sul
fronte** (Caleffi fig. 3, e anche le medio-piccole a due dischi sovrapposti di Trezzano e CT
Energia); la grande ha **i ventilatori sopra e la batteria sulla faccia**. Non la proporzione:
in Caleffi la cassa è 1,31:1 la domestica e 1,34–1,36:1 la grande. Non il numero di ventilatori: due
per 346 kW (Cammarata), quattro per 127 kW (Carrara), due dischi anche a 16 kW (CT Energia).

**La cascata** è sempre **la ripetizione del segno**: macchine identiche affiancate o impilate, ognuna
con la sua coppia di attacchi a due collettori comuni, e sul ramo di ciascuna la pompa (e il
ritegno) — Aermec, BWP — oppure la pompa dentro la macchina (Caleffi fig. 47). Nessuna fonte usa un
segno unico «per N macchine».

### Le varianti

| Variante | Chi | Contorno (l:h) | Ventilatori | Attacchi |
|---|---|---|---|---|
| blocco CAD del costruttore, dettagliato, non in scala | Carrara, Padova, Vinci, Cammarata | 2,22 · 2,12 · 1,46 · ~1 | 4 · 2 · 2 · 2, sopra | fianco del vano; mandata sopra dove verificato |
| stilizzata del costruttore di componenti | Caleffi 65 (figg. 4, 47, 48) | 1,34–1,36 | 1–2 griglie sopra | fianco destro, rosso 55 % / blu 75 %; sul fondo in fig. 4 |
| prospetto a dischi frontali sovrapposti (taglie medio-piccole) | Trezzano (37,6 kW ×2), CT Energia (16 kW) | 0,82 (Trezzano) | 2 dischi sul fronte | fianco; rosso sopra |
| schema di principio: blocco con sigla | Aermec (GF1–GF3) | ~0,7, a vista | nessuno | sopra (ritegno) e sotto (pompa) |
| segno generico di PdC con compressore | BWP | ~0,75, a vista | nessuno | sopra: ritorno a sinistra, mandata a destra |
| macchina aperta per funzioni (fuori perimetro) | Univ. Trieste (gruppo frigo) | celle impilate | — | fianco destro |

### Le fonti che la mostrano meglio

1. **Caleffi, *Idraulica* 65, gennaio 2024** — PDF p.8, 40, 42 —
   `pdc_02_caleffi-idraulica65-p8-fig3-monogeneratore.png`,
   `pdc_03_caleffi-idraulica65-p8-fig4-plurigeneratore.png`,
   `pdc_04_caleffi-idraulica65-p40-fig47-medio-grandi.png`,
   `pdc_05_caleffi-idraulica65-p42-fig48-R-P.png`. Stesso editore della fonte del segno domestico,
   mette le due macchine a confronto nella stessa pagina, disegna la cascata, dà le sigle R/P.
2. **Comune di Padova, «Girotondo», tav. M.02** — PDF p.1 —
   `pdc_07_padova-girotondo-M02-schema.png`. Vettoriale, attacchi con le frecce del verso, due
   pannelli batteria, ventilatori sopra, modulo idraulico con due pompe, seconda coppia di attacchi.
3. **Comune di Carrara, tav. PD.IM.03.00** — PDF p.1 —
   `pdc_06_carrara-pdim0300-schema-e-legenda.png`. Quattro ventilatori sopra, batteria sull'80 %,
   e la riga di legenda con descrizione e modello.

Per la cascata in schema di principio: Aermec (`pdc_09_…`) e BWP (`pdc_10_…`).

### Che cosa NON ho trovato

Un segno normato (UNI 9511-4 non vista; EN 1861 e ISO 14617-11 non lette); la vista dall'alto; le
batterie a V; i compressori disegnati in una PdC aria-acqua; uno schema pubblico di centrale
condominiale con PdC grandi in cascata.
