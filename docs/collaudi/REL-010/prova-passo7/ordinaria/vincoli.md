# Vincoli — passo 7, revisione della tavola (modalità ordinaria: la guarda chi l'ha composta)

Tavola di partenza: `tavola/` (piano `piano-0.json`), rimisurata in `tavola-giro-0/`:
A1 · tratte 137 · cedute 0 · bloccanti 0 · pieghe 13 · sormonti 12 · avvisi HIGHWAY_IS_NOT_STRAIGHT x1,
PIECE_OUTSIDE_ITS_BAND x7, SERVICE_STUB_LONGER_THAN_ITS_MINIMUM x4, SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER x4.

## Giro 1 — sulla tavola di partenza

**A colpo d'occhio.** Lo scheletro è buono: primari dritti dalle pompe ai volani, secondario
dritto fino al pettine della zona 2, pettini ordinati, gruppo ACS leggibile da sinistra a destra.
Quello che l'occhio vede e i numeri non dicono: nelle due cascate i **due collettori sono due
colonne staccate** — la colonna di ritorno sta 45 mm a destra di quella di mandata e quasi 100 mm
dalle macchine, con un corridoio vuoto in mezzo. Da lontano si leggono come due collettori
separati, non come il binario stretto accanto alle pompe.

**Se una cosa sembra sbagliata e i numeri la approvano.** Proprio questa: nessun rilievo
segnala la distanza fra le due colonne della cascata (né sopra né sotto), e il PO l'ha chiamata
difetto («i due collettori di una cascata lontani fra loro, invece di una colonna stretta accanto
alle macchine»).

### V1 — `addosso-a`: colonna di ritorno della cascata addosso a quella di mandata
- **Pezzi**: `ts-pr-1`, `ts-pr-2`, `ts-pr-3` addosso alla verticale di `tj-pr-1..3`; `ts-pa`
  addosso alla verticale di `tj-pa`. Fra le due verticali resta solo quello che il ritorno porta
  per contenuto: il raccordo dello sfiato (`tee-sfiato-*`, 10 mm dalla colonna di mandata) e il
  rettilineo del giunto antivibrante (`giunto-ritorno-*`, che il motore posa addosso al collettore).
- **Regola**: B3 (due verticali **vicine**), B12 (punto 2: «due collettori distanti fra loro»),
  difetto nominato dal PO in rivedere §6.
- **Dove si vede**: le due cascate a sinistra, GT-03/05/06/04 in alto e GT-01/02 in basso.
- **Cede in parte, e lo dico**: la colonna stretta a 10 mm non si raggiunge, perché fra le due
  verticali il grafo mette lo sfiato e il giunto del ritorno (contenuto, non si tocca). Si
  stringe fino a quello che quei due pezzi chiedono. L'ordine (mandata vicina, ritorno lontano)
  resta: con le pompe impilate fa gli stessi sormonti dell'ordine inverso, e il ritorno vicino
  metterebbe lo sfiato sotto gli organi della mandata.
- **Non ferma la consegna**: la tavola si legge giusta anche così; è un difetto che si toglie.

### V2 — `addosso-a`: gli organi di servizio dell'ACS addosso al pezzo che servono
- **Pezzi**: `ricircolo-utenze` addosso a `bollitore` (lo stacco del ricircolo ha 10 mm in più
  della fila che porta); `utenze-acs` addosso alla miscelatrice
  `mixing-valve-thermostatic-bollitore-dhw-out` (+5 mm); `acquedotto` addosso a
  `tee-drain-connection-cold-bollitore-cold-in` (+5 mm); `drain-connection-cold-bollitore-cold-in`
  addosso al suo raccordo (+2,5 mm).
- **Regola**: A4 (D-145). Le misure sono dei rilievi, non mie.
- **Dove si vede**: il gruppo ACS in basso a destra, attorno a BOL-01.
- **Non ferma la consegna.**

### Guardato e a posto (o tollerato)
- Autostrade del primario (pompe → VOL-02, pompe → VOL-01) e del secondario (VOL-02 → CIR-02 →
  pettine zona 2): dritte. La zona 1 parte da un raccordo sulla mandata e scende sotto il ritorno
  incrociandolo una volta: è la posa prescritta (I-204, punto 2).
- I due pettini: colonne a 10 mm, collettori uno sotto l'altro, terminali presi da un lato solo.
  Il rilievo «autostrada non dritta» sul ritorno della zona 2 sono le due pieghe della colonna
  del pettine: non le tolgo, la colonna è il pettine.
- Le coppie che «si aprono» (B11) sono le cascate con i collettori e la serpentina del bollitore
  (interasse 10 contro 15): casi noti, non si inseguono.
- BOL-01 sta nella fascia della distribuzione (e sei terminali della zona 1 nella fascia degli
  accumuli): la tavola si legge lo stesso, il gruppo ACS è una riga a sé sotto il riscaldamento.
  Tollerato (rivedere §6); spostare il bollitore a sinistra porterebbe l'acqua fredda addosso agli
  attacchi «al solare termico».
- Il vuoto fra il riscaldamento e il gruppo ACS: non è un difetto (D-170). Alzare il gruppo ACS
  porterebbe la colonna dell'acqua calda sotto la colonna di ritorno della zona 2, in fila con lei.
- Dentro i simboli (terminali, collettori, bollitore con serpentina, miscelatrice): niente esce dal
  proprio riquadro.

### Proposte, non vincoli (la composizione non le toglie)
- **Gli scarichi dei due volani sono rossi e con la freccia** (VOL-02 in basso, VOL-01 in basso):
  è un difetto nominato dal PO («lo scarico rosso con la freccia resta un difetto»). Il colore lo
  decide il grafo/motore, non il piano: difetto del disegno.
- Le sigle delle pompe nella pila alta sono GT-03, GT-05, GT-06, GT-04 dall'alto: convenzione
  tollerata della skill (ordine della pila diverso dalla distinta). Si dice al progettista.

### Esito del giro 1 — `tavola-giro-1/` (piano `piano.json`)
- Numeri: A1 · tratte 137 · cedute 0 · bloccanti 0 · pieghe 13 · sormonti 12 · avvisi
  HIGHWAY_IS_NOT_STRAIGHT x1, PIECE_OUTSIDE_ITS_BAND x7, SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER x4
  (i quattro SERVICE_STUB_LONGER_THAN_ITS_MINIMUM sono spariti).
- V1 applicato fin dove il contenuto lo lascia: colonne della cascata da 45 a **35 mm** (sfiato a
  10 mm dalla mandata, collettore di ritorno a 127,5). A 122,5 e a 125 il comando si ferma: il
  giunto antivibrante del ritorno non ha il suo rettilineo (`run t103 has no straight stretch of
  10mm for flexible-joint`). Il vincolo **cede** lì, e resta il fatto: le due colonne non diventano
  un binario a 10 mm finché fra loro ci sono sfiato e giunto.
- V2 applicato: i quattro stacchi ACS al minimo.
- Guardata la tavola nuova (foglio intero e zoom su cascate e gruppo ACS): le cascate si leggono
  come una coppia di colonne accanto alle pompe; niente di nuovo fuori posto; il resto come al giro 1.

## Arresto
Zero tratte cedute, zero bloccanti, e l'occhio non ha più un vincolo che la migliori: quello che
resta è tollerato (bollitore fuori fascia, vuoto fra i due gruppi, pieghe della colonna del
pettine, coppie che cambiano interasse nei casi noti) o non è del piano (scarichi rossi con la
freccia, sigle GT). Mi fermo dopo **un giro**; si consegna `tavola-giro-1/`.
