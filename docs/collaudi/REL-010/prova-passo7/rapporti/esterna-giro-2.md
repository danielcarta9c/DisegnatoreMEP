**Rapporto di revisione: tavola t1 (A1), sostituzione dei generatori, centrale a pompe di calore**

La tavola l'ho solo guardata: foglio intero e 22 ingrandimenti. I numeri non li ho ricalcolati.

**1. L'impianto come lo leggo**

Ci sono due impianti indipendenti, ciascuno con il suo gruppo di pompe di calore.

- **Riscaldamento (metà alta).**
  - Quattro PdC aria-acqua impilate a sinistra, nell'ordine GT-03, GT-05, GT-06, GT-04. Ognuna ha lo stesso corredo:
    - sulla mandata: valvola di sicurezza, intercettazione, ritegno, giunto antivibrante;
    - sul ritorno: giunto, sfiato con rubinetto, intercettazione, filtro a Y.
  - Le macchine si uniscono su due colonne affiancate subito alla loro destra, e da lì una coppia dritta va a VOL-02 (1000 l, quattro attacchi). Sul ritorno primario ci sono il gruppo di riempimento e il contatore di calore (CC).
  - All'uscita di VOL-02 la mandata si divide in due.
    - CIR-02 serve la colonna di destra: 5 collettori di zona.
    - CIR-03 passa sotto il ritorno comune e serve la colonna di sinistra: 3 collettori.
    - Ogni collettore alimenta un ventilconvettore e un pannello radiante, con l'intercettazione solo sulla discesa di mandata.
  - I ritorni delle due colonne si uniscono in un ritorno comune verso VOL-02. Su quel ritorno, accanto al volano, ci sono il manometro e VE-02.
- **ACS (fascia bassa).**
  - GT-01 e GT-02, con lo stesso corredo e le stesse due colonne, vanno a VOL-01 (200 l, sei attacchi). VOL-01 ha il gruppo di riempimento sul ritorno e due attacchi predisposti «al solare termico».
  - CIR-01 porta l'acqua alla serpentina di BOL-01 (1000 l). Il ritorno della serpentina torna a VOL-01, con VE-01 e un manometro.
  - L'acqua fredda entra da sinistra: confine, intercettazione, riduttore, scarico, gruppo di sicurezza sanitario, VE-03, poi BOL-01 dal basso.
  - L'ACS esce dall'alto e sale: intercettazione, miscelatrice termostatica (con la sua acqua fredda da un confine a destra), intercettazione, confine verso le utenze.
  - Il ricircolo arriva da destra: confine, intercettazione, CIR-04, intercettazione, fianco di BOL-01.
- **Quello che non riesco a dire:** quale zona è quale. Collettori e terminali non hanno sigla, e non sono in distinta.

**2. A colpo d'occhio**

La tavola si legge bene: due impianti separati, autostrade dritte, colonne dei collettori accanto alle macchine, pettini puliti. L'unico angolo disordinato è quello di BOL-01, in basso a destra: l'ACS esce verso l'alto, il ricircolo e l'acqua fredda della miscelatrice arrivano da destra, l'acqua fredda del bollitore da sinistra. Al centro il foglio è molto vuoto, ma per D-170 il vuoto non è un difetto.

**3. Mi sembrano sbagliate e i numeri non dicono niente**

- **Andata ACS e ricircolo non corrono insieme.** `utenze-acs` sale verso il suo confine in alto; `ricircolo-utenze` entra da destra. È la coppia di una sola utenza e lascia il foglio in due direzioni diverse. B11 non la vede perché i capi sono confini di rete e non macchine, ma il PO l'ha chiamato difetto proprio in questo caso.
- **Gruppo di sicurezza sanitario a qualche centimetro da BOL-01.** Fra i due ci sono il raccordo di VE-03 e un tratto di tubo tratteggiato con la freccia. È il caso preciso «gruppo di sicurezza a tre centimetri dal bollitore» che il PO ha chiamato difetto. Non c'è un rilievo, perché il controllo di A4 guarda gli stacchi e questo organo è in linea.
- **VE-01 e il suo manometro stanno a metà del ritorno fra VOL-01 e BOL-01**, oltre la scritta «al solare termico», staccati dal volano. In alto, invece, VE-02 e il manometro stanno addosso a VOL-02 (e in ordine inverso). Anche qui nessun rilievo.

**4. I vincoli** (nessuno dei tre ferma la consegna)

1. **ACS e ricircolo affiancati.** `utenze-acs` e `ricircolo-utenze` **sulla-stessa-verticale**, con `utenze-acs` **sopra** `ricircolo-utenze`: l'andata ACS e il ricircolo escono dal foglio affiancati, nello stesso verso.
   - Regole: B11 (mandata e ritorno corrono sempre insieme), B12 (la coppia è un binario), B10 (mandata sopra).
   - Perché questo verso: l'attacco del ricircolo sta sulla faccia destra di BOL-01 e non si muove.
   - Dove: a destra di BOL-01, linea arancione verticale contro linea verde orizzontale con CIR-04.
2. **Gruppo di sicurezza sanitario addosso a BOL-01.** Il gruppo di sicurezza sanitario sull'ingresso dell'acqua fredda **addosso-a** `bollitore` (BOL-01); fra i due resta soltanto il raccordo di VE-03.
   - Regola: A4 (D-145).
   - Dove: sulla linea tratteggiata azzurra a sinistra, sotto BOL-01.
3. **VE-01 e il manometro addosso a VOL-01.** `VE-01` e il manometro accanto **addosso-a** `VOL-01`, sul ritorno, come VE-02 e il suo manometro lo sono a VOL-02.
   - Regola: A4 (D-145).
   - Dove: in basso al centro, sul ritorno blu dopo la scritta «al solare termico».
   - Il posto glielo contendono gli attacchi predisposti del solare e la loro scritta, che stanno proprio sotto il ritorno. Chi compone lo risolve, ma A4 non cede a una scritta.

**5. Proposte invece di vincoli**

Difetti del disegno, che la composizione non toglie:
- Gli scarichi di VOL-01 e VOL-02 sono rossi, con la freccia in giù: il PO ha detto che «lo scarico rosso con la freccia resta un difetto».
- Nella legenda le prime tre voci (sfiato con rubinetto, volano a quattro attacchi, volano a sei attacchi) hanno i simboli che si toccano. Da lontano si leggono come un oggetto solo: uno sfiato in testa a due volani impilati.
- La miscelatrice termostatica e il rubinetto portamanometro a tre vie hanno quasi lo stesso segno: farfalla, triangolo di lato, stanghetta. Cambia solo il lato della stanghetta. È la classe «due organi diversi con lo stesso segno».

Domande al progettista:
- Collettori di zona e terminali non hanno sigla e non sono in distinta: vuole i nomi delle zone (piano, alloggio)?
- Ventilconvettori e pannelli hanno l'intercettazione solo sulla mandata: è voluto?

**6. Guardato e a posto**

- **Autostrade:** dritte, con pochissime curve, sia in alto (PdC → VOL-02 → zone) sia in basso (PdC → VOL-01 → BOL-01).
- **Collettori:** ogni cascata ha una sola coppia di colonne, corta e accanto alle macchine (B3); il corredo delle sei PdC è identico e allineato.
- **Pettini:** colonne adiacenti, coppie affiancate, terminali presi da un lato. I simboli dei terminali sono interi: serpentine e ventole stanno dentro i loro riquadri.
- **Sigle e bordo:** le sigle stanno vicino alle loro macchine; niente tocca il bordo del foglio.
- **Rilievi che il disegno non conferma**, con la tavola in mano:
  - B11 su `pdc-r4`, `pdc-a2` e `coll-mz2-5`: a vista le coppie corrono insieme. Gli interassi diversi cadono, per quanto vedo, negli angoli delle colonne dei collettori, non in un'apertura.
  - B11 su `bollitore` ~ `volano-acs` è il gradino della serpentina, che B11 stesso dichiara vero e non curabile.
  - B1 sul ritorno della zona 2: le due pieghe sono la testa e il piede della colonna del pettine, che B1 elenca come imposte. A vista è un tronco dritto con il pettine.
  - A1: BOL-01 e i terminali della zona 1 condividono la fascia in x, ma stanno lontanissimi in quota e la tavola si legge lo stesso. È un caso tollerato.
- **Tollerati o convenzioni:**
  - la mandata di CIR-03 che passa sotto il ritorno comune;
  - l'ordine delle colonne delle cascate;
  - le PdC impilate in un ordine diverso dalla distinta;
  - l'acqua fredda della miscelatrice dal proprio confine (C1, D-175);
  - il tratteggio dell'acqua fredda che parte con un vuoto;
  - gli attacchi liberi, che sono i pozzetti delle sonde;
  - gli stacchi lunghi di ricircolo e utenze-acs, già misurati;
  - il cartiglio «DA DEFINIRE», che rende la tavola una bozza.

VERDETTO: la tavola si può consegnare così, perché l'impianto si legge giusto e i difetti trovati (coppia ACS-ricircolo aperta, gruppo di sicurezza e VE-01 staccati, scarichi rossi, legenda e simboli) vanno corretti ma non ne cambiano la lettura.
