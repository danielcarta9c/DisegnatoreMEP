# Il grafo dell'impianto

> **Cosa approvi qui.** L'impianto — Pompa di calore diretta su pavimento radiante, ACS separata —
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

- **BPC-01** Boiler in pompa di calore, sull'acqua calda sanitaria
- **PDC-01** Pompa di calore aria-acqua, sull'acqua di riscaldamento
- **AF-01** Alimentazione acqua fredda, sull'acqua fredda sanitaria

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
| **BPC** | Generatore di calore — sigla che hai scelto tu nel modello |
| **COL** | Collettore |
| **DEF** | Defangatore |
| **DER** | Derivazione |
| **FIL** | Filtro |
| **GR** | Gruppo di riempimento |
| **MN** | Manometro |
| **PAV** | Terminale di emissione — sigla che hai scelto tu nel modello |
| **PDC** | Generatore di calore — sigla che hai scelto tu nel modello |
| **RC** | Raccordo |
| **SC** | Attacco di scarico |
| **SF** | Valvola di sfogo aria |
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
| **ACS.01** | acqua calda sanitaria | BPC-01 | ACS-01 |
| **CP.01** | mandata primaria | PDC-01 | COL-01 |
| **CP.02** | mandata primaria | COL-01 | PAV-01 |
| **CP.03** | mandata primaria | COL-01 | PAV-02 |
| **RP.01** | ritorno primario | PAV-01 | VOL-01 |
| **RP.02** | ritorno primario | VOL-01 | PDC-01 |
| **RP.03** | ritorno primario | PAV-02 | RC-01 |
| **AF.01** | acqua fredda sanitaria | AF-01 | BPC-01 |

---

## I nodi

Nell'ordine in cui la passeggiata li incontra, che e' l'ordine in cui sono stati
numerati. L'indirizzo dice dove sta il pezzo; la sigla che cos'e'.

| Indirizzo | Sigla | Che cos'e' | Su quale fluido |
|---|---|---|---|
| ACS.01.N.01 | **BPC-01** | Boiler in pompa di calore · tiene in serbo acqua calda sanitaria | acqua fredda sanitaria, acqua calda sanitaria |
| ACS.01.N.02 | **DER-01** | Derivazione a T sanitaria | acqua calda sanitaria |
| ACS.01.N.03 | **VI-01** | Valvola di intercettazione | acqua calda sanitaria |
| ACS.01.N.04 | **VM-01** | Valvola miscelatrice termostatica | acqua calda sanitaria |
| ACS.01.N.05 | **VI-02** | Valvola di intercettazione | acqua calda sanitaria |
| ACS.01.N.06 | **ACS-01** | Utenze sanitarie | acqua calda sanitaria |
| ACS.01.N.02.1 | **SC-01** | Attacco di scarico sanitario · pende dal tubo con una propria derivazione | acqua calda sanitaria |
| CP.01.N.01 | **PDC-01** | Pompa di calore aria-acqua | acqua di riscaldamento |
| CP.01.N.02 | **VI-03** | Valvola di intercettazione | acqua di riscaldamento |
| CP.01.N.03 | **VI-04** | Valvola di intercettazione | acqua di riscaldamento |
| CP.01.N.04 | **COL-01** | Collettore di zona | acqua di riscaldamento |
| CP.02.N.01 | **VI-05** | Valvola di intercettazione | acqua di riscaldamento |
| CP.02.N.02 | **VI-06** | Valvola di intercettazione | acqua di riscaldamento |
| CP.02.N.03 | **PAV-01** | Pannello radiante | acqua di riscaldamento |
| RP.01.N.01 | **VI-07** | Valvola di intercettazione | acqua di riscaldamento |
| RP.01.N.02 | **RC-01** | Raccordo a T | acqua di riscaldamento |
| RP.01.N.03 | **VI-08** | Valvola di intercettazione | acqua di riscaldamento |
| RP.01.N.04 | **DER-02** | Derivazione a T | acqua di riscaldamento |
| RP.01.N.05 | **VOL-01** | Volano termico a due attacchi · tiene in serbo acqua di riscaldamento | acqua di riscaldamento |
| RP.02.N.01 | **VI-09** | Valvola di intercettazione | acqua di riscaldamento |
| RP.02.N.02 | **DER-03** | Derivazione a T | acqua di riscaldamento |
| RP.02.N.03 | **DER-04** | Derivazione a T | acqua di riscaldamento |
| RP.02.N.04 | **DER-05** | Derivazione a T | acqua di riscaldamento |
| RP.02.N.05 | **FIL-01** | Filtro a Y | acqua di riscaldamento |
| RP.02.N.06 | **DEF-01** | Defangatore | acqua di riscaldamento |
| RP.02.N.07 | **VI-10** | Valvola di intercettazione | acqua di riscaldamento |
| RP.02.N.04.1 | **VI-11** | Valvola di intercettazione | acqua di riscaldamento |
| RP.02.N.04.2 | **MN-01** | Manometro · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| RP.02.N.03.1 | **VI-12** | Valvola di intercettazione | acqua di riscaldamento |
| RP.02.N.03.2 | **GR-01** | Gruppo di riempimento · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| RP.02.N.02.1 | **VIB-01** | Valvola di intercettazione bloccabile aperta | acqua di riscaldamento |
| RP.02.N.02.2 | **VE-01** | Vaso di espansione · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| RP.01.N.05.1 | **SF-01** | Valvola di sfogo aria · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| RP.01.N.05.2 | **SC-02** | Attacco di scarico · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| RP.01.N.04.1 | **VS-01** | Valvola di sicurezza · pende dal tubo con una propria derivazione | acqua di riscaldamento |
| RP.03.N.01 | **VI-13** | Valvola di intercettazione | acqua di riscaldamento |
| CP.03.N.03 | **PAV-02** | Pannello radiante | acqua di riscaldamento |
| CP.03.N.02 | **VI-14** | Valvola di intercettazione | acqua di riscaldamento |
| CP.03.N.01 | **VI-15** | Valvola di intercettazione | acqua di riscaldamento |
| AF.01.N.01 | **AF-01** | Alimentazione acqua fredda | acqua fredda sanitaria |
| AF.01.N.02 | **VI-16** | Valvola di intercettazione | acqua fredda sanitaria |
| AF.01.N.03 | **DER-06** | Derivazione a T sull'acqua fredda | acqua fredda sanitaria |
| AF.01.N.04 | **VI-17** | Valvola di intercettazione | acqua fredda sanitaria |
| AF.01.N.05 | **VR-01** | Valvola di ritegno sanitaria | acqua fredda sanitaria |
| AF.01.N.06 | **DER-07** | Derivazione a T sull'acqua fredda | acqua fredda sanitaria |
| AF.01.N.06.1 | **VS-02** | Valvola di sicurezza sanitaria · pende dal tubo con una propria derivazione | acqua fredda sanitaria |
| AF.01.N.03.1 | **VIB-02** | Valvola di intercettazione bloccabile aperta | acqua fredda sanitaria |
| AF.01.N.03.2 | **VE-02** | Vaso di espansione sanitario · pende dal tubo con una propria derivazione | acqua fredda sanitaria |

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

### ACS.01 — acqua calda sanitaria

Da **BPC-01** a **ACS-01**, acqua calda sanitaria.

1. **ACS.01.N.01 · BPC-01** Boiler in pompa di calore · tiene in serbo acqua calda sanitaria · la linea parte dal suo braccio 2
    - qui arriva **AF.01**, da **AF-01**, entrando dal braccio 1
2. **ACS.01.N.02 · DER-01** Derivazione a T sanitaria
    - **ACS.01.N.02.1 · SC-01** Attacco di scarico sanitario · pende dallo stacco
3. **ACS.01.N.03 · VI-01** Valvola di intercettazione
4. **ACS.01.N.04 · VM-01** Valvola miscelatrice termostatica
5. **ACS.01.N.05 · VI-02** Valvola di intercettazione
6. **ACS.01.N.06 · ACS-01** Utenze sanitarie

### CP.01 — mandata primaria

Da **PDC-01** a **COL-01**, circuito di riscaldamento.

1. **CP.01.N.01 · PDC-01** Pompa di calore aria-acqua · la linea parte dal suo braccio 1
    - qui arriva **RP.02**, da **VOL-01**, entrando dal braccio 2
2. **CP.01.N.02 · VI-03** Valvola di intercettazione
3. **CP.01.N.03 · VI-04** Valvola di intercettazione
4. **CP.01.N.04 · COL-01** Collettore di zona

### CP.02 — mandata primaria

Da **COL-01** a **PAV-01**, circuito di riscaldamento.

1. **COL-01** Collettore di zona · gia' numerato, indirizzo CP.01.N.04 · la linea parte dal suo braccio 2
2. **CP.02.N.01 · VI-05** Valvola di intercettazione
3. **CP.02.N.02 · VI-06** Valvola di intercettazione
4. **CP.02.N.03 · PAV-01** Pannello radiante

### CP.03 — mandata primaria

Da **COL-01** a **PAV-02**, circuito di riscaldamento.

1. **COL-01** Collettore di zona · gia' numerato, indirizzo CP.01.N.04 · la linea parte dal suo braccio 3
2. **CP.03.N.01 · VI-15** Valvola di intercettazione
3. **CP.03.N.02 · VI-14** Valvola di intercettazione
4. **CP.03.N.03 · PAV-02** Pannello radiante

### RP.01 — ritorno primario

Da **PAV-01** a **VOL-01**, circuito di riscaldamento.

1. **PAV-01** Pannello radiante · gia' numerato, indirizzo CP.02.N.03 · la linea parte dal suo braccio 2
2. **RP.01.N.01 · VI-07** Valvola di intercettazione
3. **RP.01.N.02 · RC-01** Raccordo a T
    - qui arriva **RP.03**, da **PAV-02**, entrando dal braccio 2
4. **RP.01.N.03 · VI-08** Valvola di intercettazione
5. **RP.01.N.04 · DER-02** Derivazione a T
    - **RP.01.N.04.1 · VS-01** Valvola di sicurezza · pende dallo stacco
6. **RP.01.N.05 · VOL-01** Volano termico a due attacchi · tiene in serbo acqua di riscaldamento
    - **RP.01.N.05.1 · SF-01** Valvola di sfogo aria · pende dallo stacco
    - **RP.01.N.05.2 · SC-02** Attacco di scarico · pende dallo stacco

### RP.02 — ritorno primario

Da **VOL-01** a **PDC-01**, circuito di riscaldamento.

1. **VOL-01** Volano termico a due attacchi · gia' numerato, indirizzo RP.01.N.05 · la linea parte dal suo braccio 2
2. **RP.02.N.01 · VI-09** Valvola di intercettazione
3. **RP.02.N.02 · DER-03** Derivazione a T
    - **RP.02.N.02.1 · VIB-01** Valvola di intercettazione bloccabile aperta · pende dallo stacco
    - **RP.02.N.02.2 · VE-01** Vaso di espansione · pende dallo stacco
4. **RP.02.N.03 · DER-04** Derivazione a T
    - **RP.02.N.03.1 · VI-12** Valvola di intercettazione · pende dallo stacco
    - **RP.02.N.03.2 · GR-01** Gruppo di riempimento · pende dallo stacco
5. **RP.02.N.04 · DER-05** Derivazione a T
    - **RP.02.N.04.1 · VI-11** Valvola di intercettazione · pende dallo stacco
    - **RP.02.N.04.2 · MN-01** Manometro · pende dallo stacco
6. **RP.02.N.05 · FIL-01** Filtro a Y
7. **RP.02.N.06 · DEF-01** Defangatore
8. **RP.02.N.07 · VI-10** Valvola di intercettazione
9. **PDC-01** Pompa di calore aria-acqua · **qui il giro si richiude su PDC-01**, entrando dal suo braccio 2 (CP.01.N.01)

### RP.03 — ritorno primario

Da **PAV-02** a **RC-01**, circuito di riscaldamento.

1. **PAV-02** Pannello radiante · gia' numerato, indirizzo CP.03.N.03 · la linea parte dal suo braccio 2
2. **RP.03.N.01 · VI-13** Valvola di intercettazione
3. **RC-01** Raccordo a T · **qui il giro si richiude su RC-01**, entrando dal suo braccio 2 (RP.01.N.02)

### AF.01 — acqua fredda sanitaria

Da **AF-01** a **BPC-01**, acqua fredda sanitaria.

1. **AF.01.N.01 · AF-01** Alimentazione acqua fredda · la linea parte dal suo braccio 1
2. **AF.01.N.02 · VI-16** Valvola di intercettazione
3. **AF.01.N.03 · DER-06** Derivazione a T sull'acqua fredda
    - **AF.01.N.03.1 · VIB-02** Valvola di intercettazione bloccabile aperta · pende dallo stacco
    - **AF.01.N.03.2 · VE-02** Vaso di espansione sanitario · pende dallo stacco
4. **AF.01.N.04 · VI-17** Valvola di intercettazione
5. **AF.01.N.05 · VR-01** Valvola di ritegno sanitaria
6. **AF.01.N.06 · DER-07** Derivazione a T sull'acqua fredda
    - **AF.01.N.06.1 · VS-02** Valvola di sicurezza sanitaria · pende dallo stacco
7. **BPC-01** Boiler in pompa di calore · **qui ci si innesta su BPC-01**, che si e' gia' letto, entrando dal suo braccio 1 (ACS.01.N.01)

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
