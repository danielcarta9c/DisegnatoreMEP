# Revisione della tavola: centrale termica a pompe di calore (A1, t1)

## 1. L'impianto come lo leggo

Sul foglio ci sono **due impianti separati**, che non hanno tubi in comune.

**Riscaldamento (metà alta)**
- **Generazione:** quattro pompe di calore aria-acqua impilate, nell'ordine GT-03, GT-05, GT-06, GT-04. Lavorano in parallelo su due colonne verticali: quella di mandata sta vicino alle macchine, quella di ritorno più a destra.
- **Corredo di ogni macchina:**
  - in mandata: valvola di sicurezza, intercettazione, ritegno, giunto antivibrante;
  - in ritorno: filtro a Y e intercettazione vicino alla macchina, poi, oltre la colonna di mandata, una T con lo sfiato e un giunto antivibrante.
- **Verso il volano:** la mandata comune va dritta a VOL-02 (1000 l, 4 attacchi). Sul ritorno comune ci sono il contatore di calore CC e il gruppo di riempimento dall'acqua fredda. VOL-02 ha lo sfiato in alto, lo scarico in basso e un attacco libero a sinistra.
- **Distribuzione:** dal lato destro di VOL-02 la mandata si divide con una T.
  - CIR-02 prosegue dritto sulla mandata alta fino al pettine di destra: 5 collettori di zona.
  - CIR-03 scende di un piano e alimenta il pettine di sinistra: 3 collettori di zona.
  - Ogni collettore di zona serve un ventilconvettore e un pannello radiante, con un'intercettazione sulla discesa di mandata.
- **Ritorni:** la colonna del pettine di destra risale e diventa il ritorno comune. Il pettine di sinistra ci si innesta con una T. Prima di VOL-02, sul ritorno, ci sono il manometro e il vaso VE-02.

**ACS (metà bassa)**
- **Generazione:** GT-01 e GT-02, con lo stesso corredo e le stesse due colonne, alimentano VOL-01 (200 l, 6 attacchi). VOL-01 ha due attacchi predisposti «al solare termico».
- **Serpentina:** CIR-01 manda alla serpentina di BOL-01 (1000 l). Il ritorno esce dal fondo della serpentina e torna a VOL-01 passando per il vaso VE-01 e il manometro.
- **Acqua fredda:** dal confine di rete passa per intercettazione, riduttore, scarico, gruppo di sicurezza sanitario e vaso VE-03, poi entra in basso nel bollitore.
- **ACS alle utenze:** esce dall'alto e passa per intercettazione, miscelatrice termostatica (la sua acqua fredda arriva da un confine di rete proprio), intercettazione, confine di rete.
- **Ricircolo:** torna dalle utenze con CIR-04 ed entra nel fianco destro del bollitore.

**Quello che dalla tavola non riesco a dire**
- A quali zone corrispondano gli 8 collettori: nessuno ha una sigla.
- Il ritorno del collettore di zona è disegnato in tre pezzi staccati (vedi §5). Letto alla lettera, non si vede come i ritorni dei due terminali raggiungano l'uscita.

## 2. A colpo d'occhio

- **Lo scheletro è buono.** Le autostrade sono poche e rette, l'ordine va da sinistra a destra, i due pettini sono puliti.
- **Quello che stona da lontano sono le due cascate.** La colonna di ritorno sta lontana da quella di mandata. Ogni ritorno scavalca la mandata e si porta dietro, staccati dalla macchina, lo sfiato e il giunto antivibrante.
- Al centro a sinistra c'è un grande vuoto. Non è un difetto (D3).

## 3. Cose che mi sembrano sbagliate e che i numeri approvano

1. **Gli scarichi di VOL-01 e VOL-02 sono rossi e hanno la freccia.** Sotto ciascun volano, a x≈403 mm, y≈95 e y≈505, si legge un tratto di mandata che esce dal fondo. È esattamente il difetto che il PO ha nominato: «lo scarico rosso con la freccia resta un difetto». Lo stesso vale per lo scarico sull'acqua fredda del bollitore (x≈540 mm, y≈485): è tratteggiato come l'andata e ha la freccia. Nessun rilievo lo vede.
2. **Gli organi del ritorno delle sei pompe di calore stanno lontano dalla loro macchina.** Lo sfiato e il giunto antivibrante stanno oltre la colonna di mandata, vicino alla colonna di ritorno, e si leggono come organi del collettore. Gli organi gemelli della mandata invece stanno addosso alla macchina. I rilievi A4 misurano solo gli stacchi, non gli organi in linea, quindi qui tacciono.
3. **CIR-02 e CIR-03 non sono incolonnati.** Sono due circolatori in parallelo che partono dalla stessa T, ma CIR-03 e le sue valvole sono spostati di qualche millimetro rispetto a CIR-02 (x≈493–495 mm, y≈51 e 98). Il PO ha nominato questo difetto («le pompe in parallelo non incolonnate»). A2 non ha ancora un rilievo.
4. **Il gruppo di sicurezza sanitario sta a metà della linea dell'acqua fredda.** È a circa 5 cm da BOL-01, con la T di VE-03 e lunghi tratti vuoti in mezzo (x≈550–606 mm, y≈481). Il PO aveva chiamato difetto «un gruppo di sicurezza a tre centimetri dal bollitore».

## 4. I vincoli

Valgono in quest'ordine: A2, poi A4, poi B3/B12. **Nessuno dei quattro ferma la consegna.**

- **V1 · `sulla-stessa-verticale`.** CIR-02 e CIR-03, con le rispettive intercettazioni a monte e a valle.
  - *Regola:* A2 (D-118), «più pompe pari fra loro: incolonnati».
  - *Dove:* x≈490–500 mm, y≈51 / 98.
- **V2 · `addosso-a`.** La T dello sfiato sul ritorno di ciascuna macchina (GT-01…GT-06) va addosso alla propria GT, nel tratto fra la macchina e la colonna di mandata, come gli organi della mandata. Il giunto antivibrante del ritorno lo segue per forza, se vale V3. Non trovo una regola che lo nomini come organo di servizio, quindi non lo impongo: lo chiedo (§5).
  - *Regola:* A4 (D-145), dove gli sfiati sono nell'elenco.
  - *Dove:* x≈290–312 mm, sulle sei linee di ritorno.
- **V3 · `addosso-a` + `almeno-3-corsie-da`.** La colonna di ritorno della cascata GT-03/05/06/04 (le quattro T blu, oggi a x≈322 mm) va addosso alla colonna di mandata della stessa cascata (x≈277 mm), a tre corsie libere e non di più. Lo stesso per la cascata GT-01/GT-02 verso VOL-01.
  - *Regole:* B12, cioè i «due collettori lontani fra loro» che il PO ha ripassato «addosso alle pompe, su una colonna stretta»; poi B3, e B9 per la distanza.
  - *Rilievi collegati:* B11 pdc-r4 ~ volano-risc (195 mm) e pdc-a2 ~ volano-acs (75 mm). Le coppie si aprono proprio sul tratto di ritorno fra le due colonne.
  - *Se il corredo del ritorno non ci sta:* V3 cede a V2. Si sposta a destra la colonna di mandata per fare posto, non si allontana quella di ritorno.
  - *Dove:* y≈51–246 mm in alto e y≈451–526 mm in basso.
- **V4 · `addosso-a`.** Il gruppo di sicurezza sanitario va addosso a BOL-01 (attacco dell'acqua fredda), con in mezzo solo la T di VE-03. L'ordine degli organi non lo tocco.
  - *Regola:* A4 (D-145), con il caso del PO del gruppo di sicurezza.
  - *Dove:* x≈550–606 mm, y≈481.

## 5. Quello che propongo invece di imporre

- **Difetto del disegno (colore e freccia, non si cura componendo).** Gli scarichi di VOL-01 e VOL-02, e lo scarico sulla linea dell'acqua fredda del bollitore, vanno disegnati senza il colore della mandata e senza freccia.
- **Domanda al PO sul simbolo «collettore di zona con ritorno».** La barra del ritorno è spezzata in tre dove passano le discese di mandata. Anche il simbolo in legenda è fatto così, quindi è il simbolo di catalogo. Nel resto del foglio però gli incroci si fanno con il ponticello. Letto alla lettera, i ritorni del ventilconvettore e del pannello entrano in due pezzi di barra che non toccano l'uscita. Come si disegna questo incrocio?
- **Domanda al PO sulla regola.** Il giunto antivibrante del ritorno di una pompa di calore rientra in A4, cioè deve stare addosso alla macchina?
- **Difetto del disegno (legenda).** In testa alla legenda il simbolo dello sfiato esce sopra il bordo del riquadro e tocca il volano a quattro attacchi, che a sua volta tocca quello a sei. Sono tre simboli impilati senza aria, e si leggono come un oggetto solo.
- **Domande al progettista:**
  - Come si chiamano le 8 zone? Senza sigle i collettori e i 16 terminali non si possono riferire a niente.
  - Ventilconvettore e pannello radiante stanno sullo stesso collettore di zona, alla stessa mandata, senza una regolazione propria. È voluto?

## 6. Quello che ho guardato e mi sembra a posto

- **Autostrade.** Mandata e ritorno principali sono rette dalla cascata al volano e dal volano ai pettini e al bollitore, in tutti e due gli impianti, con pochi incroci.
- **Pettini.** Le colonne sono affiancate, c'è una coppia di orizzontali per utenza con la mandata sopra, i terminali sono impilati. È la forma di B12.
- **Simboli e sigle.** La serpentina del bollitore e quella del pannello stanno dentro il riquadro. Non ho trovato simboli uno dentro l'altro nel disegno. Le sigle stanno accanto ai loro pezzi.
- **Foglio e cartiglio.** Il disegno non tocca il bordo. Distinta e legenda corrispondono a quello che è disegnato. Il cartiglio «DA DEFINIRE» fa della tavola una bozza, ed è una convenzione.
- **Tollerati.**
  - La mandata di CIR-03 passa sotto il ritorno comune per raggiungere il suo pettine.
  - L'ordine delle colonne è invertito fra i due pettini: sulle verticali non c'è una regola.
  - BOL-01 e i terminali del pettine sinistro stanno fuori fascia (PIECE_OUTSIDE_ITS_BAND), ma la parte bassa si legge lo stesso da sinistra a destra.
  - Ci sono quattro stacchi ACS un po' lunghi.
  - La mandata di CIR-01 è lunga.
  - L'ordine delle macchine nella pila è diverso da quello della distinta.
- **Rilievi che il controllo accusa e a occhio vanno bene.**
  - *B1 sulla catena di ritorno verso coll-mz2-5.* Le due pieghe sono la testa e il piede della colonna del pettine di destra, cioè la forma del pettine, e la regola stessa le elenca fra le L imposte. La mandata dello stesso pettine è disegnata uguale e non è accusata. Il pavimento lì sembra troppo basso: lo deve guardare chi mantiene il controllo.
  - *B11 coll-mz2-5 ~ volano-risc.* A occhio la coppia corre insieme per tutta la corsa: è il pettine.
  - *B11 bollitore ~ volano-acs.* È il gradino imposto dagli attacchi della serpentina, che non si spostano. Sta addosso al bollitore e si legge bene.

VERDETTO: la tavola si può consegnare così — l'impianto si legge giusto da cima a fondo, e i difetti trovati (colonne della cascata staccate, organi del ritorno lontani dalla macchina, scarichi rossi con freccia, circolatori non incolonnati, gruppo di sicurezza lontano dal bollitore) si possono disegnare meglio ma non ne cambiano la lettura.

Le zone ingrandite che ho guardato sono in revisione/ (da zoom-1.png a zoom-18.png).
