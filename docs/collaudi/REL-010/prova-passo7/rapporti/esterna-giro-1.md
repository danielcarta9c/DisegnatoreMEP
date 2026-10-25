**Rapporto del revisore esterno: tavola t1 (A1), centrale termica a pompe di calore**

Ho guardato il foglio intero e 20 ingrandimenti, salvati come revisione-1/zoom-1.png … zoom-20.png. Le posizioni in mm sono lette sul foglio, dall'alto a sinistra.

## 1. L'impianto come lo leggo

Ci sono due impianti indipendenti, uno sopra l'altro.

**Sopra: riscaldamento.**
- **Generatori:** quattro pompe di calore impilate (GT-03, GT-05, GT-06, GT-04). Su ogni mandata ci sono valvola di sicurezza, intercettazione, ritegno e giunto antivibrante. Su ogni ritorno ci sono filtro a Y e intercettazione e, oltre la colonna di mandata, sfiato con rubinetto e giunto.
- **Collettori della cascata:** la mandata si raccoglie in una colonna rossa, il ritorno si distribuisce da una colonna blu più a destra. Sul ritorno comune c'è il gruppo di riempimento.
- **Volano e contatore:** la coppia va dritta a VOL-02 (1000 l). Sul ritorno verso le pompe di calore c'è il contatore di calore CC.
- **Circuiti:** da VOL-02, CIR-02 alimenta la colonna di destra (5 piani) e CIR-03, con uno stacco in discesa, alimenta la colonna di sinistra (3 piani).
- **Piani:** su ogni piano un collettore di zona serve un ventilconvettore e un pannello radiante, con una valvola sulla mandata di ciascuno.
- **Ritorni:** il ritorno della zona sinistra entra con un T nel ritorno comune. Quello della zona destra sale e corre a sinistra. Prima di VOL-02 il ritorno passa per VE-02 e il manometro.

**Sotto: acqua calda sanitaria.**
- **Generatori e volano:** GT-01 e GT-02 sono impilati con lo stesso corredo e vanno a VOL-01 (200 l). Su VOL-01 ci sono due attacchi tappati «al solare termico».
- **Circuito della serpentina:** VOL-01 → intercettazione → CIR-01 → intercettazione → serpentina di BOL-01 (1000 l). Il ritorno passa per VE-01 e il manometro.
- **Acqua fredda:** dall'acquedotto (confine a sinistra) passa per intercettazione, riduttore, T di scarico, gruppo di sicurezza sanitario e T del VE-03, ed entra dal basso in BOL-01.
- **Acqua calda e ricircolo:** l'ACS esce dall'alto e passa per la miscelatrice termostatica, che ha la sua acqua fredda da un confine proprio a destra; poi va al confine «utenze» in alto. Il ricircolo arriva da destra con CIR-04 ed entra sul fianco destro di BOL-01.

**Cosa non si capisce dalla tavola:** se l'acqua fredda della miscelatrice è presa a valle del riduttore. Non ho trovato altri punti oscuri.

## 2. A colpo d'occhio

Le autostrade sono poche, dritte e leggibili, e l'impianto si segue senza fatica. Tre cose stonano.
- In tutte e due le cascate le colonne di mandata e di ritorno stanno a circa 4–5 cm l'una dall'altra, con il corredo del ritorno in mezzo: si leggono come due colonne separate e non come un binario.
- I due scarichi sotto i volani sono rossi e hanno la freccia.
- Il centro-sinistra del foglio è vuoto. Non è un difetto (D3).

## 3. Sembra sbagliato e i numeri lo approvano

**Il gruppo di sicurezza sanitario sta lontano da BOL-01.** È a circa metà della linea fredda, a x≈555 mm, y≈481. Fra il gruppo e il T del VE-03 c'è un lungo tratto vuoto, e fra il T e il bollitore un altro. È il difetto che il PO ha chiamato con il suo nome: «un gruppo di sicurezza a tre centimetri dal bollitore». Qui la distanza è maggiore. A4 non lo vede perché misura gli stacchi, non la posizione degli organi in linea; i rilievi accusano solo +5 mm sull'acquedotto e +2,5 mm sullo scarico.

**Sfiato e giunto antivibrante sul ritorno di ogni pompa di calore (da GT-01 a GT-06).** Stanno oltre lo scavalcamento della colonna di mandata, a x≈292 e x≈310 mm, cioè fra le due colonne e lontani dalla macchina che servono. Nessun rilievo li vede. È questo che tiene distanti le due colonne.

## 4. I vincoli

In ordine di gerarchia: A4 prima di B.

**V1 · `addosso-a`**
- **Pezzi:** sul ritorno di ciascuna pompa di calore (GT-01…GT-06), sfiato con rubinetto e giunto antivibrante addosso a quella pompa di calore. Stanno fra la macchina e il collettore di mandata, come già il corredo della mandata. L'ordine degli organi lungo la linea non cambia.
- **Regola:** A4 (D-145).
- **Dove:** sfiati a x≈292, giunti a x≈310 mm, nella cascata in alto (y 51–246) e in quella in basso (y 451–526).
- **Ferma la consegna?** No.

**V2 · `addosso-a` + `almeno-3-corsie-da`**
- **Pezzi:** collettore di ritorno della cascata (colonna blu) addosso al collettore di mandata (colonna rossa), con almeno 3 corsie libere fra i due. Vale per tutte e due le cascate.
- **Regola:** B12 («due collettori lontani fra loro… colonna stretta addosso alle pompe»), B3, B9 per la distanza minima. Il rilievo che lo tocca è B11 (pdc-r4~volano-risc, pdc-a2~volano-acs). Si regge su V1.
- **Dove:** colonne a x≈277 e x≈322 mm, in alto e in basso.
- **Ferma la consegna?** No.

**V3 · `addosso-a`**
- **Pezzi:** gruppo di sicurezza sanitario addosso al T del VE-03, e T del VE-03 addosso a BOL-01 (attacco dell'acqua fredda).
- **Regola:** A4 (D-145) e la disposizione del PO sul gruppo di sicurezza.
- **Dove:** linea fredda, x≈555–606 mm, y≈481.
- **Ferma la consegna?** No.

## 5. Proposte invece di imposizioni

**Difetti di disegno che la composizione non toglie:**
- **Scarichi dei volani.** Sotto VOL-01 e VOL-02 (x≈405 mm) lo scarico è rosso e ha la freccia. Il PO lo dice esplicitamente: «lo scarico rosso con la freccia resta un difetto».
- **Scarico sulla linea fredda.** Anche quello a x≈540, y≈481–502 ha la freccia. È della stessa famiglia: chiedo al PO se la freccia va tolta da tutti gli scarichi.
- **Simbolo «collettore di zona con ritorno».** La barra di ritorno è interrotta dove passano le discese di mandata, e da lontano il ritorno dei terminali sembra staccato dall'uscita. Altrove sulla tavola gli incroci sono a scavalco. È una convenzione: domanda al PO, non rilievo.

**Domande al progettista:**
- CIR-01 ha l'intercettazione solo a monte (CIR-02 e CIR-03 le hanno su tutti e due i lati). Ne serve una a valle?
- Il ritorno della serpentina di BOL-01 non ha intercettazione, la mandata sì. È voluto?
- L'acqua fredda della miscelatrice arriva da un confine proprio, senza passare dal riduttore. È così nell'impianto?
- Il contatore di calore c'è solo sull'impianto di riscaldamento. È voluto?

## 6. Guardato e a posto

**Autostrade e coppie**
- Le due coppie principali sono rette per tutto il foglio, con mandata sopra e ritorno sotto, e corrono insieme a interasse costante.
- Gli scavalcamenti sono il minimo: uno per ogni ritorno delle pompe di calore e uno per piano.

**Rilievi su cui non agirei**
- **B1 sulla catena volano-risc → coll-mz2-5:** sulla tavola è una dorsale e una colonna a pettine, la forma di B12. Si legge bene; i numeri accusano, l'occhio no.
- **B11 su coll-mz2-5 ~ volano-risc:** la coppia sale insieme lungo la colonna. Non ho visto aperture.
- **B11 su bollitore ~ volano-acs:** il gradino del ritorno vicino a BOL-01 (x≈597 mm) è imposto dalla serpentina, che per B11 «è vero e non si cura».
- **I 7 rilievi A1 (fasce):** nascono tutti da BOL-01, che sta sotto i terminali della zona sinistra. I due impianti stanno su righe diverse e la tavola si legge lo stesso (tolleranza del PO). Il circuito VOL-01 → BOL-01 è lungo, ed è tollerato.
- **I quattro rilievi A4 da +2,5 a +10 mm:** sulla tavola non si vedono.

**Corredo, sigle e simboli**
- Il corredo delle pompe di calore è incolonnato da macchina a macchina.
- Le sigle stanno vicino ai loro pezzi.
- Pompe e ritegni sono orientati col flusso.
- Nessun segno esce dal proprio riquadro: serpentina del bollitore, pannelli radianti, ventilconvettori.
- Il disegno non tocca i bordi. La distinta è vicina a GT-03 e GT-05 (circa 7 mm) ma staccata.
- La freccia dell'ACS non si allinea con niente sopra.

**Convenzioni tollerate**
- L'ordine della pila diverso dalla distinta.
- Gli attacchi liberi su volani e bollitore (pozzetti delle sonde).
- Il cartiglio «DA DEFINIRE».
- Gli stacchi di servizio col colore della linea da cui partono.
- Il tratteggio dell'acqua fredda che comincia con un vuoto.

VERDETTO: la tavola si può consegnare così, perché l'impianto si legge giusto, con autostrade dritte e coppie unite, e i difetti trovati (collettori delle cascate distanti, gruppo di sicurezza lontano dal bollitore, scarichi rossi con freccia) andrebbero disegnati meglio ma non cambiano la lettura.
