# Il grafo dell'impianto

> **Cosa approvi qui.** L'impianto — Pompa di calore con deviazione fra climatizzazione e ACS —
> scritto invece che disegnato: ogni pezzo con la propria sigla, ogni tubazione
> fra due pezzi, e la passeggiata che parte dalle sorgenti e segue l'acqua fino a
> dove il giro si richiude.
>
> **Perche' non un disegno.** Un disegno prova come l'impianto e' stato messo sul
> foglio. Qui la domanda e' un'altra: **il pezzo giusto e' nel punto giusto, sul
> tubo giusto?** Quella si legge, non si guarda. E con una sigla per pezzo puoi
> correggere puntando — «questo qui e' nel posto sbagliato» — invece di
> descrivere a parole dove guardare.

---

## Come si legge

- **Ogni linea idraulica ha un nome**, come una strada: la famiglia dice che acqua
  porta e da che parte va — `CP.01` e' la prima mandata primaria — e la tabella
  accanto dice da dove a dove va. Dove una linea si sdoppia, la principale tiene il
  nome nudo e i rami prendono una lettera (`RP.01a`); dove due linee si incontrano,
  la principale tira dritto e la secondaria muore su quel nodo.
- **Ogni pezzo e' un nodo numerato lungo la sua linea**, e quello e' il suo
  indirizzo: `CP.01.N.02` e' il secondo nodo della prima mandata primaria. Cio' che
  pende da uno stacco e' un **civico** del nodo: `CP.01.N.02.1`.
- **La sigla resta** (`VI-02`): dice che cosa e' il pezzo, e serve alla distinta.
  L'indirizzo dice dove sta. Sulla tavola convivono, e per citare un punto basta
  uno dei due. Le sigle che hai gia' scritto tu restano come le hai scritte.
- **Ogni tubazione fra due pezzi e' un arco**, e porta il proprio fluido.
- **Ogni attacco e' un braccio numerato**, come in un incrocio stradale: un volano
  a quattro attacchi e' un nodo solo con quattro bracci, contati nell'ordine in cui
  il pezzo li dichiara.
- **Un braccio su cui convergono piu' tubazioni e' un incrocio**, e le tubazioni che
  ci arrivano si contano.
- **Non e' un albero, e' un anello.** Un circuito si chiude su se' stesso: dove
  succede, la lettura lo dice e non si interrompe.

---

## Da dove si comincia a contare

Non dall'ordine in cui il modello elenca i pezzi, che e' un fatto di come e'
scritto e non dell'impianto: **dalle sorgenti**, seguendo il fluido. La prima
valvola che si incontra uscendo dal generatore e' la numero uno della sua
famiglia. Sono sorgenti chi il calore lo produce e il punto da cui l'acqua entra
nell'edificio; si riconoscono da cio' che ogni pezzo dichiara di saper fare, mai
da un elenco di nomi — un impianto con una caldaia al posto della pompa di calore
comincia esattamente allo stesso modo.

Qui si parte da:

- **PDC-01** Pompa di calore aria-acqua, sull'acqua di riscaldamento
- **AF-01** Alimentazione acqua fredda, sull'acqua fredda sanitaria
- **BOL-01** Bollitore ACS, dove nasce l'acqua calda sanitaria

**Costo di questa scelta, detto subito:** se domani si aggiunge un pezzo vicino a
una sorgente, i numeri della sua famiglia a valle scalano tutti di uno. E' normale
per un documento che si rigenera a ogni revisione; cio' che non cambia mai e' che
lo stesso impianto dia sempre le stesse sigle, comunque sia scritto il modello che
lo descrive.

---

## Le famiglie delle sigle

La sigla di un pezzo dice a quale famiglia appartiene, e la famiglia si legge dal
mestiere che quel pezzo dichiara di fare — mai dal suo nome. Aggiungere una
famiglia vuol dire aggiungere una riga a una tabella, non toccare il programma.

| Sigla | Famiglia |
|---|---|
| **ACS** | Allacciamento — sigla che hai scelto tu nel modello |
| **AF** | Allacciamento — sigla che hai scelto tu nel modello |
| **BOL** | Accumulo di acqua calda sanitaria |
| **CIR** | Circolatore |
| **DEF** | Defangatore |
| **DER** | Derivazione |
| **FIL** | Filtro |
| **GR** | Gruppo di riempimento |
| **MN** | Manometro |
| **PDC** | Generatore di calore — sigla che hai scelto tu nel modello |
| **RC** | Raccordo |
| **SA** | Separatore d'aria |
| **SC** | Attacco di scarico |
| **TM** | Termometro |
| **VC** | Terminale di emissione — sigla che hai scelto tu nel modello |
| **VD** | Valvola deviatrice |
| **VE** | Vaso di espansione |
| **VI** | Valvola di intercettazione |
| **VIB** | Valvola di intercettazione bloccabile aperta |
| **VM** | Valvola miscelatrice |
| **VOL** | Accumulo inerziale |
| **VR** | Valvola di ritegno |
| **VS** | Valvola di sicurezza |

---

## Le linee

Le tubazioni dell'impianto, lette come strade: ogni linea parte da una macchina,
arriva alla prossima, e i pezzi in mezzo sono i suoi nodi numerati. La famiglia
dice che acqua porta e da che parte va.

| Linea | Che acqua porta | Da | A |
|---|---|---|---|
| **CP.01** | mandata primaria | PDC-01 | VOL-01 |
| **CP.01a** | mandata primaria · si stacca da CP.01 | VD-01 | BOL-01 |
| **RP.01** | ritorno primario | VOL-01 | PDC-01 |
| **RP.02** | ritorno primario | BOL-01 | RC-01 |
| **CS.01** | mandata secondaria | VOL-01 | VC-01 |
| **RS.01** | ritorno secondario | VC-01 | VOL-01 |
| **ACS.01** | acqua calda sanitaria | BOL-01 | ACS-01 |
| **AF.01** | acqua fredda sanitaria | AF-01 | BOL-01 |

---

## I nodi

Nell'ordine in cui la passeggiata li incontra, che e' l'ordine in cui sono stati
numerati. L'indirizzo dice dove sta il pezzo; la sigla che cos'e'.

| Indirizzo | Sigla | Che cos'e' | Su quale fluido |
|---|---|---|---|
| CP.01.N.01 | **PDC-01** | Pompa di calore aria-acqua | acqua di riscaldamento |
| CP.01.N.02 | **DER-01** | Derivazione a T | acqua di riscaldamento |
| CP.01.N.03 | **DER-02** | Derivazione a T | acqua di riscaldamento |
| CP.01.N.04 | **VI-01** | Valvola di intercettazione | acqua di riscaldamento |
| CP.01.N.05 | **VI-02** | Valvola di intercettazione | acqua di riscaldamento |
| CP.01.N.06 | **SA-01** | Separatore d'aria | acqua di riscaldamento |
| CP.01.N.07 | **VI-03** | Valvola di intercettazione | acqua di riscaldamento |
| CP.01.N.08 | **VI-04** | Valvola di intercettazione | acqua di riscaldamento |
| CP.01.N.09 | **VD-01** | Valvola deviatrice a tre vie | acqua di riscaldamento |
| CP.01.N.10 | **VI-05** | Valvola di intercettazione | acqua di riscaldamento |
| CP.01.N.11 | **VI-06** | Valvola di intercettazione | acqua di riscaldamento |
| CP.01.N.12 | **VOL-01** | Volano termico a quattro attacchi · tiene in serbo acqua di riscaldamento | acqua di riscaldamento |
| RP.01.N.01 | **VI-07** | Valvola di intercettazione | acqua di riscaldamento |
| RP.01.N.02 | **RC-01** | Raccordo a T | acqua di riscaldamento |
| RP.01.N.03 | **FIL-01** | Filtro a Y | acqua di riscaldamento |
| RP.01.N.04 | **DEF-01** | Defangatore | acqua di riscaldamento |
| RP.01.N.05 | **VI-08** | Valvola di intercettazione | acqua di riscaldamento |
| RP.02.N.01 | **VI-09** | Valvola di intercettazione | acqua di riscaldamento |
| CP.01a.N.06 | **BOL-01** | Bollitore ACS · tiene in serbo acqua calda sanitaria | acqua di riscaldamento, acqua fredda sanitaria, acqua calda sanitaria |
| CP.01a.N.05 | **VI-10** | Valvola di intercettazione | acqua di riscaldamento |
| CP.01a.N.04 | **DER-03** | Derivazione a T | acqua di riscaldamento |
| CP.01a.N.04.1 | **VI-11** | Valvola di intercettazione | acqua di riscaldamento |
| CP.01a.N.04.2 | **MN-01** | Manometro · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| CP.01a.N.03 | **DER-04** | Derivazione a T | acqua di riscaldamento |
| CP.01a.N.03.1 | **VIB-01** | Valvola di intercettazione bloccabile aperta | acqua di riscaldamento |
| CP.01a.N.03.2 | **VE-01** | Vaso di espansione · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| CP.01a.N.02 | **DER-05** | Derivazione a T | acqua di riscaldamento |
| CP.01a.N.02.1 | **VI-12** | Valvola di intercettazione | acqua di riscaldamento |
| CP.01a.N.02.2 | **GR-01** | Gruppo di riempimento · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| CP.01a.N.01 | **VI-13** | Valvola di intercettazione | acqua di riscaldamento |
| CS.01.N.01 | **VI-14** | Valvola di intercettazione | acqua di riscaldamento |
| CS.01.N.02 | **FIL-02** | Filtro a Y | acqua di riscaldamento |
| CS.01.N.03 | **DEF-02** | Defangatore | acqua di riscaldamento |
| CS.01.N.04 | **VI-15** | Valvola di intercettazione | acqua di riscaldamento |
| CS.01.N.05 | **CIR-01** | Pompa di circolazione | acqua di riscaldamento |
| CS.01.N.06 | **VI-16** | Valvola di intercettazione | acqua di riscaldamento |
| CS.01.N.07 | **VI-17** | Valvola di intercettazione | acqua di riscaldamento |
| CS.01.N.08 | **VC-01** | Ventilconvettore | acqua di riscaldamento |
| RS.01.N.01 | **VI-18** | Valvola di intercettazione | acqua di riscaldamento |
| RS.01.N.02 | **VI-19** | Valvola di intercettazione | acqua di riscaldamento |
| CP.01.N.12.1 | **SC-01** | Attacco di scarico · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| CP.01.N.03.1 | **TM-01** | Termometro · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| CP.01.N.02.1 | **VS-01** | Valvola di sicurezza · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| AF.01.N.01 | **AF-01** | Alimentazione acqua fredda | acqua fredda sanitaria |
| AF.01.N.02 | **VI-20** | Valvola di intercettazione | acqua fredda sanitaria |
| AF.01.N.03 | **DER-06** | Derivazione a T sull'acqua fredda | acqua fredda sanitaria |
| AF.01.N.04 | **VI-21** | Valvola di intercettazione | acqua fredda sanitaria |
| AF.01.N.05 | **VR-01** | Valvola di ritegno sanitaria | acqua fredda sanitaria |
| AF.01.N.06 | **DER-07** | Derivazione a T sull'acqua fredda | acqua fredda sanitaria |
| AF.01.N.06.1 | **VS-02** | Valvola di sicurezza sanitaria · pende dal tubo con una propria derivazione | acqua fredda sanitaria |
| AF.01.N.03.1 | **VIB-02** | Valvola di intercettazione bloccabile aperta | acqua fredda sanitaria |
| AF.01.N.03.2 | **VE-02** | Vaso di espansione sanitario · pende dal tubo con una propria derivazione | acqua fredda sanitaria |
| ACS.01.N.01 | **DER-08** | Derivazione a T sanitaria | acqua calda sanitaria |
| ACS.01.N.02 | **VI-22** | Valvola di intercettazione | acqua calda sanitaria |
| ACS.01.N.03 | **VM-01** | Valvola miscelatrice termostatica | acqua calda sanitaria |
| ACS.01.N.04 | **VI-23** | Valvola di intercettazione | acqua calda sanitaria |
| ACS.01.N.05 | **ACS-01** | Utenze sanitarie | acqua calda sanitaria |
| ACS.01.N.01.1 | **SC-02** | Attacco di scarico sanitario · pende dal tubo con una propria derivazione | acqua calda sanitaria |

---

## Gli incroci

Nessuno: su questo impianto ogni attacco porta una sola tubazione.

---

## Le linee, una per una

Ogni linea si legge dal suo capo, un nodo alla volta; i civici stanno sotto il
proprio nodo. Dove la linea finisce su un nodo che ha gia' un indirizzo, la
lettura dice quale delle due cose e' successa — **il giro si richiude**, perche'
un circuito e' un anello, oppure **ci si innesta** su un giro gia' letto — e in
nessuno dei due casi il nome della principale cambia. Ogni tubazione
dell'impianto sta su una linea sola.

### CP.01 — mandata primaria

Da **PDC-01** a **VOL-01**, circuito primario.

1. **CP.01.N.01 · PDC-01** Pompa di calore aria-acqua · la linea parte dal suo braccio 1
    - qui arriva **RP.01**, da **VOL-01**, entrando dal braccio 2
2. **CP.01.N.02 · DER-01** Derivazione a T
    - **CP.01.N.02.1 · VS-01** Valvola di sicurezza · pende dallo stacco
3. **CP.01.N.03 · DER-02** Derivazione a T
    - **CP.01.N.03.1 · TM-01** Termometro · pende dallo stacco
4. **CP.01.N.04 · VI-01** Valvola di intercettazione
5. **CP.01.N.05 · VI-02** Valvola di intercettazione
6. **CP.01.N.06 · SA-01** Separatore d'aria
7. **CP.01.N.07 · VI-03** Valvola di intercettazione
8. **CP.01.N.08 · VI-04** Valvola di intercettazione
9. **CP.01.N.09 · VD-01** Valvola deviatrice a tre vie
    - qui si stacca **CP.01a**, verso **BOL-01**, dal braccio 3
10. **CP.01.N.10 · VI-05** Valvola di intercettazione
11. **CP.01.N.11 · VI-06** Valvola di intercettazione
12. **CP.01.N.12 · VOL-01** Volano termico a quattro attacchi · tiene in serbo acqua di riscaldamento
    - **CP.01.N.12.1 · SC-01** Attacco di scarico · pende dallo stacco
    - qui arriva **RS.01**, da **VC-01**, entrando dal braccio 4

### CP.01a — mandata primaria

Da **VD-01** a **BOL-01**, circuito primario.
Si stacca da **CP.01**.

1. **VD-01** Valvola deviatrice a tre vie · gia' numerato, indirizzo CP.01.N.09 · la linea parte dal suo braccio 3
2. **CP.01a.N.01 · VI-13** Valvola di intercettazione
3. **CP.01a.N.02 · DER-05** Derivazione a T
    - **CP.01a.N.02.1 · VI-12** Valvola di intercettazione · pende dallo stacco
    - **CP.01a.N.02.2 · GR-01** Gruppo di riempimento · pende dallo stacco
4. **CP.01a.N.03 · DER-04** Derivazione a T
    - **CP.01a.N.03.1 · VIB-01** Valvola di intercettazione bloccabile aperta · pende dallo stacco
    - **CP.01a.N.03.2 · VE-01** Vaso di espansione · pende dallo stacco
5. **CP.01a.N.04 · DER-03** Derivazione a T
    - **CP.01a.N.04.1 · VI-11** Valvola di intercettazione · pende dallo stacco
    - **CP.01a.N.04.2 · MN-01** Manometro · pende dallo stacco
6. **CP.01a.N.05 · VI-10** Valvola di intercettazione
7. **CP.01a.N.06 · BOL-01** Bollitore ACS · tiene in serbo acqua calda sanitaria
    - qui arriva **AF.01**, da **AF-01**, entrando dal braccio 4

### RP.01 — ritorno primario

Da **VOL-01** a **PDC-01**, circuito primario.

1. **VOL-01** Volano termico a quattro attacchi · gia' numerato, indirizzo CP.01.N.12 · la linea parte dal suo braccio 2
2. **RP.01.N.01 · VI-07** Valvola di intercettazione
3. **RP.01.N.02 · RC-01** Raccordo a T
    - qui arriva **RP.02**, da **BOL-01**, entrando dal braccio 2
4. **RP.01.N.03 · FIL-01** Filtro a Y
5. **RP.01.N.04 · DEF-01** Defangatore
6. **RP.01.N.05 · VI-08** Valvola di intercettazione
7. **PDC-01** Pompa di calore aria-acqua · **qui il giro si richiude su PDC-01**, entrando dal suo braccio 2 (CP.01.N.01)

### RP.02 — ritorno primario

Da **BOL-01** a **RC-01**, circuito primario.

1. **BOL-01** Bollitore ACS · gia' numerato, indirizzo CP.01a.N.06 · la linea parte dal suo braccio 2
2. **RP.02.N.01 · VI-09** Valvola di intercettazione
3. **RC-01** Raccordo a T · **qui il giro si richiude su RC-01**, entrando dal suo braccio 2 (RP.01.N.02)

### CS.01 — mandata secondaria

Da **VOL-01** a **VC-01**, circuito secondario.

1. **VOL-01** Volano termico a quattro attacchi · gia' numerato, indirizzo CP.01.N.12 · la linea parte dal suo braccio 3
2. **CS.01.N.01 · VI-14** Valvola di intercettazione
3. **CS.01.N.02 · FIL-02** Filtro a Y
4. **CS.01.N.03 · DEF-02** Defangatore
5. **CS.01.N.04 · VI-15** Valvola di intercettazione
6. **CS.01.N.05 · CIR-01** Pompa di circolazione
7. **CS.01.N.06 · VI-16** Valvola di intercettazione
8. **CS.01.N.07 · VI-17** Valvola di intercettazione
9. **CS.01.N.08 · VC-01** Ventilconvettore

### RS.01 — ritorno secondario

Da **VC-01** a **VOL-01**, circuito secondario.

1. **VC-01** Ventilconvettore · gia' numerato, indirizzo CS.01.N.08 · la linea parte dal suo braccio 2
2. **RS.01.N.01 · VI-18** Valvola di intercettazione
3. **RS.01.N.02 · VI-19** Valvola di intercettazione
4. **VOL-01** Volano termico a quattro attacchi · **qui il giro si richiude su VOL-01**, entrando dal suo braccio 4 (CP.01.N.12)

### ACS.01 — acqua calda sanitaria

Da **BOL-01** a **ACS-01**, acqua calda sanitaria.

1. **BOL-01** Bollitore ACS · gia' numerato, indirizzo CP.01a.N.06 · la linea parte dal suo braccio 3
2. **ACS.01.N.01 · DER-08** Derivazione a T sanitaria
    - **ACS.01.N.01.1 · SC-02** Attacco di scarico sanitario · pende dallo stacco
3. **ACS.01.N.02 · VI-22** Valvola di intercettazione
4. **ACS.01.N.03 · VM-01** Valvola miscelatrice termostatica
5. **ACS.01.N.04 · VI-23** Valvola di intercettazione
6. **ACS.01.N.05 · ACS-01** Utenze sanitarie

### AF.01 — acqua fredda sanitaria

Da **AF-01** a **BOL-01**, acqua fredda sanitaria.

1. **AF.01.N.01 · AF-01** Alimentazione acqua fredda · la linea parte dal suo braccio 1
2. **AF.01.N.02 · VI-20** Valvola di intercettazione
3. **AF.01.N.03 · DER-06** Derivazione a T sull'acqua fredda
    - **AF.01.N.03.1 · VIB-02** Valvola di intercettazione bloccabile aperta · pende dallo stacco
    - **AF.01.N.03.2 · VE-02** Vaso di espansione sanitario · pende dallo stacco
4. **AF.01.N.04 · VI-21** Valvola di intercettazione
5. **AF.01.N.05 · VR-01** Valvola di ritegno sanitaria
6. **AF.01.N.06 · DER-07** Derivazione a T sull'acqua fredda
    - **AF.01.N.06.1 · VS-02** Valvola di sicurezza sanitaria · pende dallo stacco
7. **BOL-01** Bollitore ACS · **qui ci si innesta su BOL-01**, che si e' gia' letto, entrando dal suo braccio 4 (CP.01a.N.06)

---

## Quello che il grafo non tace

Le cose che un elenco muto lascerebbe scoprire in cantiere.

**Attacchi liberi:** nessuno. Ogni attacco di ogni pezzo porta la sua
tubazione.

**Pezzi che nessuna sorgente raggiunge:** nessuno. Partendo dalle sorgenti si
arriva a ogni pezzo dell'impianto.

**Tubazioni non lette:** nessuna. Ogni tubazione compare nella passeggiata.

**Punti aperti:** nessuno. Per ogni accessorio che le regole hanno chiesto, il
catalogo aveva il pezzo adatto al fluido di quella tubazione.

---

## Cosa ti stiamo chiedendo

Di scorrere le linee e dirci, per ogni pezzo: **e' quello giusto, ed e' nel
punto giusto, sul tubo giusto?** Se un accessorio e' finito sul circuito sbagliato
si vede da qui, senza aprire nient'altro — e per segnalarcelo bastano
l'indirizzo o la sigla.
