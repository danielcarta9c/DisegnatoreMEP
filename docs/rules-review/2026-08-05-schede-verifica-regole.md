# Schede di verifica delle regole di inserimento — pacchetto idronico

**Data:** 5 agosto 2026 · **Pacchetto:** WP2 del piano di rilancio
**Perché questo documento esiste:** il contenuto delle regole non è mai stato approvato dal
PM (D-085). Qui ogni regola del pacchetto ha una scheda: cosa propone, in quale punto
funzionale, perché proprio lì, con quale fonte. Una posizione motivata solo da «così faceva
l'esempio» è una scheda respinta. Le posizioni dichiarate sono state **verificate sul
modello rigenerato** del caso di accettazione, non dedotte dalle intenzioni.

Il pacchetto conta **19 regole**: le 15 del primo pacchetto (3 delle quali corrette in
questa revisione) più 4 nuove regole di intercettazione nate da D-074 — una valvola per
ogni attacco di macchina. Sono 4 e non 1 perché ogni regola propone un pezzo solo e ogni
pezzo appartiene a un fluido: servono regole distinte per generatore, circolatore, accumulo
tecnico e per i tre fluidi che toccano il bollitore.

**Legenda esiti:** ✔ conforme · ✔* conforme con osservazione registrata · ✎ corretta in
questa revisione · ✚ nuova.

**Fonti citate** (registro fonti del progetto):
- **SRC-012** — Raccolta R ed. 2009 (INAIL): prescrizioni per gli impianti di
  riscaldamento a vaso chiuso; il cap. R.3.B.1 elenca i dispositivi obbligatori. Nata per
  le centrali oltre 35 kW: sotto quella soglia resta il riferimento di buona pratica.
- **SRC-014** — UNI 8065:2019 (trattamento dell'acqua), tramite guida Aqua Italia.
- **SRC-008** — Caleffi, Quaderni e Tabelle; in particolare «Componenti e schemi per
  impianti a pompa di calore aria-acqua».
- **D-074** — decisione del PM: «ogni macchina vuole una valvola di intercettazione su
  ogni attacco».

---

## Famiglia sicurezza

### 1. Vaso di espansione — `expansion-on-closed-circuit` v1.0.0 ✔

- **Cosa propone:** un attacco con vaso di espansione a membrana, uno per circuito chiuso.
- **Posizione funzionale:** sul ritorno al generatore, dal lato del circuito rispetto alla
  valvola di macchina.
- **Perché lì:** un circuito chiuso che si scalda aumenta di volume; senza un polmone la
  pressione sale fino a far scaricare la sicurezza. Sul ritorno il vaso lavora alla
  temperatura più bassa, che è la condizione buona per la membrana. Stando dal lato del
  circuito, il circuito resta protetto anche quando la macchina è esclusa per manutenzione;
  il tratto di macchina sigillato resta a sua volta protetto dalla valvola di sicurezza,
  che sta dentro quel tratto (scheda 2 e 12).
- **Fonte:** Raccolta R ed. 2009, cap. R.3.B.1 (SRC-012).

### 2. Valvola di sicurezza — `safety-valve-on-generator` v1.0.0 ✔

- **Cosa propone:** una valvola di sicurezza per generatore.
- **Posizione funzionale:** sulla mandata, il primo organo dopo il termometro, **prima**
  della valvola di intercettazione della macchina.
- **Perché lì:** deve poter scaricare la sovrapressione del generatore in ogni condizione,
  quindi fra lei e la macchina non deve esserci nessun organo di chiusura. La Raccolta R
  la vuole sul generatore o sulla mandata in prossimità della macchina. Verificato sul
  modello rigenerato: la valvola di intercettazione sta a valle, mai in mezzo.
- **Fonte:** Raccolta R ed. 2009, cap. R.3.B.1 (SRC-012).

## Famiglia intercettazione — «ogni macchina, ogni attacco» (D-074)

### 3. Intercettazione del generatore — `isolation-around-generator` v1.0.0 ✚

- **Cosa propone:** una valvola di intercettazione su **ogni** attacco idraulico del
  generatore: due per la pompa di calore del caso (mandata e ritorno).
- **Posizione funzionale:** sulla mandata, a valle degli strumenti e della valvola di
  sicurezza di macchina; sul ritorno, a valle del manometro di macchina.
- **Perché lì:** il generatore è il pezzo che si stacca per manutenzione o sostituzione:
  si seziona ogni tubo che vi entra o ne esce, così il lavoro non richiede di svuotare
  l'impianto. Gli organi di sicurezza e gli strumenti di macchina restano dal lato del
  generatore, dentro il tratto sezionato: la sicurezza non è mai esclusa e a macchina
  ferma si legge ancora pressione e temperatura del tratto.
- **Fonte:** pratica di settore, schemi Caleffi per impianti a pompa di calore (SRC-008);
  regola per attacco fissata dal PM (D-074).

### 4. Intercettazione del circolatore — `isolation-around-pump` **v2.0.0** ✎

- **Correzione:** cardinalità da «una per componente» a «una per attacco»; rimossa dalla
  motivazione la frase «una sola valvola nel primo pacchetto», che era un vincolo di
  foglio e non una ragione impiantistica. Prima il circolatore aveva una valvola sola.
- **Cosa propone:** una valvola per ciascun lato del circolatore (aspirazione e mandata).
- **Posizione funzionale:** sull'aspirazione, a monte del filtro raccoglitore di impurità;
  sulla mandata, subito a valle della pompa.
- **Perché lì:** il circolatore è il pezzo che si sostituisce più spesso; con le due
  valvole si smonta senza svuotare il circuito. La valvola d'aspirazione a monte del
  filtro serve anche la pulizia del filtro stesso (scheda 8).
- **Fonte:** buona pratica documentata, Caleffi (SRC-008); D-074.

### 5. Intercettazione dell'accumulo tecnico — `isolation-around-storage` **v2.0.0** ✎ ✔*

- **Correzione:** come la scheda 4: da «una per componente» a «una per attacco», rimossa
  la stessa frase di vincolo di foglio. Prima il volano restava sotto il pieno.
- **Cosa propone:** una valvola su ogni attacco del volano termico: quattro nel caso
  (ingresso e uscita lato generazione, uscita e ritorno lato distribuzione).
- **Posizione funzionale:** su ciascun attacco, dal lato del tubo che vi arriva; una
  valvola già presente su un attacco viene riconosciuta e **non** duplicata — nel caso di
  accettazione l'uscita verso la pompa di calore aveva già la sua valvola disegnata
  dall'ingegnere, e resta quella.
- **Perché lì:** un accumulo si sostituisce e si manutiene; con una valvola per attacco si
  isola il solo serbatoio senza svuotare i circuiti che vi fanno capo.
- **Fonte:** buona pratica documentata, Caleffi (SRC-008); D-074.
- **Osservazione registrata:** il ritorno della distribuzione arriva al volano con **due**
  tubazioni (le due zone) che si giuntano sull'attacco stesso. La valvola dell'attacco si
  posa sul ramo principale; il secondo ramo non porta una valvola propria, perché nel
  modello il punto di giunzione coincide con l'attacco e non esiste un tratto comune su
  cui posarla. L'attacco risulta comunque presidiato; il caso limite è segnalato al PM nel
  dossier ed è un limite del modello del caso, non della regola.

### 6. Intercettazione del bollitore, lato riscaldamento — `isolation-around-dhw-coil` v1.0.0 ✚

- **Cosa propone:** una valvola su ciascuno dei due attacchi del circuito di riscaldamento
  del bollitore (andata e ritorno dello scambiatore).
- **Posizione funzionale:** sugli attacchi dello scambiatore, dal lato del circuito
  primario.
- **Perché lì:** anche il bollitore è una macchina da poter scollegare: con le due valvole
  lo scambiatore si esclude senza svuotare il circuito primario.
- **Fonte:** buona pratica documentata, Caleffi (SRC-008); D-074.

### 7a. Intercettazione del bollitore, ingresso acqua fredda — `cold-feed-isolation-on-dhw-storage` v1.0.0 ✚

- **Cosa propone:** una valvola di intercettazione sull'alimentazione di acqua fredda del
  bollitore.
- **Posizione funzionale:** in testa alla fila degli accessori dell'ingresso freddo, verso
  la rete: prima del ritegno, del vaso sanitario e del gruppo di sicurezza.
- **Perché lì:** chiudendola si lavora sul bollitore e su **tutti** i suoi accessori
  sanitari; ritegno e gruppo di sicurezza restano dal lato del bollitore, che non deve mai
  poterne essere separato. È la disposizione dei gruppi di sicurezza sanitari di pratica
  corrente (rubinetto — ritegno — sicurezza — bollitore). Verificato sul modello
  rigenerato: la fila dall'acquedotto è intercettazione, ritegno, vaso, sicurezza,
  bollitore.
- **Fonte:** buona pratica documentata, Caleffi (SRC-008); D-074.
- **Nota di costruzione (per chi manutiene il pacchetto):** l'ordine dei pezzi su uno
  stesso attacco segue l'ordine deterministico delle regole nel registro; il nome di
  questa regola è scelto perché applichi **prima** delle regole sanitarie e la valvola
  resti a monte degli organi di sicurezza. Se si rinomina la regola, la posizione nella
  fila cambia: la prova automatica sul caso di accettazione lo segnalerebbe.

### 7b. Intercettazione del bollitore, uscita acqua calda — `isolation-on-dhw-outlet` v1.0.0 ✚

- **Cosa propone:** una valvola di intercettazione sull'uscita dell'acqua calda sanitaria.
- **Posizione funzionale:** subito all'uscita del bollitore, prima della valvola
  miscelatrice.
- **Perché lì:** insieme alla valvola sull'ingresso freddo isola completamente il
  bollitore dalla rete sanitaria; e la miscelatrice a valle si smonta senza svuotare la
  distribuzione.
- **Fonte:** buona pratica documentata, Caleffi (SRC-008); D-074.

## Famiglia protezione

### 8. Filtro a Y — `strainer-upstream-of-pump` v1.0.0 ✔

- **Cosa propone:** un filtro raccoglitore di impurità per circolatore.
- **Posizione funzionale:** sull'aspirazione, immediatamente a monte del circolatore, a
  valle della valvola di intercettazione.
- **Perché lì:** protegge la girante dai residui che restano in impianto dopo il
  montaggio; l'ultimo posto utile prima della pompa è quello che la protegge da tutto ciò
  che arriva. Con la valvola a monte chiusa, il filtro si apre e si pulisce senza svuotare.
- **Fonte:** buona pratica documentata, Caleffi (SRC-008).

### 9. Defangatore — `dirt-separator-on-generator-return` v1.0.0 ✔

- **Cosa propone:** un defangatore per generatore.
- **Posizione funzionale:** sul ritorno al generatore, dal lato del circuito, a monte del
  tratto di macchina.
- **Perché lì:** i fanghi e le ossidazioni dell'impianto convergono col ritorno verso lo
  scambiatore del generatore, che è il componente più delicato: il defangatore li separa
  prima. La UNI 8065 chiede la protezione dell'acqua del circuito; stando fuori dal tratto
  sezionato si spurga anche a macchina esclusa.
- **Fonte:** UNI 8065:2019 tramite guida Aqua Italia (SRC-014).

## Famiglia aria

### 10. Separatore d'aria — `air-separator-on-generator-flow` v1.0.0 ✔

- **Cosa propone:** un separatore di microbolle per generatore.
- **Posizione funzionale:** sulla mandata del generatore, dal lato del circuito, oltre la
  valvola di macchina.
- **Perché lì:** l'aria disciolta si libera dove l'acqua è più calda, cioè appena fuori
  dal generatore: lì il separatore la raccoglie prima che raggiunga i terminali. Dal lato
  del circuito, continua a servire l'impianto anche a macchina esclusa.
- **Fonte:** buona pratica documentata, Caleffi (SRC-008).

## Famiglia riempimento e scarico

### 11. Gruppo di riempimento — `filling-unit-on-return` v1.0.0 ✔

- **Cosa propone:** un gruppo di riempimento per circuito chiuso.
- **Posizione funzionale:** sul ritorno, accanto al punto in cui è attestato il vaso di
  espansione, dal lato del circuito.
- **Perché lì:** l'impianto si riempie e si reintegra a pressione controllata dal punto
  più freddo; farlo vicino al vaso rende la pressione di carica direttamente confrontabile
  con la precarica del vaso.
- **Fonte:** Raccolta R ed. 2009, cap. R.3.B.1 (SRC-012).
- **Nota:** il disconnettore a valle del riempimento è registrato fra le famiglie future
  (documento delle decisioni rimandate, §1).

### 12. Attacco di scarico — `drain-on-storage` **v2.0.0** ✎

- **Correzione trovata dalla revisione trasversale:** la regola posava lo scarico sul ramo
  d'ingresso, **fuori** dalla sezione intercettata: a valvole chiuse avrebbe svuotato il
  circuito, non il serbatoio. Ora lo scarico sta dal lato del serbatoio rispetto alla
  valvola d'attacco.
- **Cosa propone:** uno scarico per accumulo (uno per pezzo: la cardinalità per componente
  qui è quella impiantisticamente giusta, un rubinetto di scarico per serbatoio).
- **Posizione funzionale:** sull'attacco basso dell'accumulo — nel caso, l'uscita verso il
  ritorno del generatore — **fra il serbatoio e la sua valvola d'attacco**. Verificato sul
  modello rigenerato.
- **Perché lì:** un accumulo va potuto svuotare per manutenzione senza scaricare l'intero
  impianto: le valvole d'attacco (scheda 5) chiudono, lo scarico — che sta dentro la
  sezione chiusa, in basso — svuota il solo serbatoio.
- **Fonte:** buona pratica documentata, Caleffi (SRC-008).
- **Ipotesi dichiarata:** «l'uscita è l'attacco basso» vale per il volano a quattro
  attacchi del catalogo attuale. Il linguaggio delle condizioni non sa dire «punto più
  basso»: se entrasse in catalogo un accumulo con uscita alta, la scheda va riesaminata.
- **Nota sul bollitore:** il bollitore non riceve uno scarico dedicato: nella pratica lo
  svuotamento avviene dal rubinetto del gruppo di sicurezza sanitario (scheda 17), che ne
  integra la funzione.

## Famiglia misura

### 13. Termometro — `thermometer-on-generator-flow` v1.0.0 ✔

- **Cosa propone:** un termometro per generatore.
- **Posizione funzionale:** sulla mandata, il primo pezzo fuori dalla macchina, dentro il
  tratto di macchina.
- **Perché lì:** la temperatura di mandata è il dato di esercizio del generatore e va
  letta sul posto, senza smontare nulla; la Raccolta R lo elenca fra i dispositivi
  obbligatori dell'impianto a vaso chiuso.
- **Fonte:** Raccolta R ed. 2009, cap. R.3.B.1 (SRC-012).

### 14. Manometro — `pressure-gauge-on-generator-return` v1.0.0 ✔

- **Cosa propone:** un manometro per generatore.
- **Posizione funzionale:** sul ritorno, il primo pezzo fuori dalla macchina, dentro il
  tratto di macchina.
- **Perché lì:** la pressione è la prima cosa che si guarda quando qualcosa non va, e la
  Raccolta R la vuole leggibile sull'impianto. A ridosso della macchina il manometro dà la
  pressione del generatore anche a tratto sezionato; a valvole aperte — l'esercizio — è la
  pressione dell'intero circuito.
- **Fonte:** Raccolta R ed. 2009, cap. R.3.B.1 (SRC-012).

## Famiglia acqua calda sanitaria

### 15. Valvola di ritegno sanitaria — `dhw-check-on-cold-inlet` v1.0.0 ✔

- **Cosa propone:** un ritegno sull'alimentazione fredda del bollitore.
- **Posizione funzionale:** sull'ingresso freddo, a valle della valvola di intercettazione
  (scheda 7a), a monte del vaso e del gruppo di sicurezza.
- **Perché lì:** l'acqua scaldata non deve poter rifluire verso la rete potabile; messo a
  monte del vaso, la dilatazione resta dal lato del bollitore dove il vaso può assorbirla.
- **Fonte:** buona pratica documentata, Caleffi (SRC-008).

### 16. Vaso di espansione sanitario — `dhw-expansion-on-cold-inlet` v1.0.0 ✔

- **Cosa propone:** un vaso di espansione sanitario.
- **Posizione funzionale:** sull'ingresso freddo, fra il ritegno e il gruppo di sicurezza,
  cioè nel tratto che il ritegno chiude verso la rete.
- **Perché lì:** con il ritegno installato la dilatazione dell'acqua scaldata non ha più
  dove andare: il vaso la assorbe ed evita che la valvola di sicurezza sgoccioli a ogni
  ciclo di riscaldo.
- **Fonte:** buona pratica documentata, Caleffi (SRC-008).

### 17. Gruppo di sicurezza sanitario — `dhw-safety-group-on-cold-inlet` v1.0.0 ✔

- **Cosa propone:** la valvola di sicurezza sanitaria dell'ingresso freddo.
- **Posizione funzionale:** l'ultimo organo prima del bollitore, senza alcuna
  intercettazione fra sé e il serbatoio.
- **Perché lì:** protegge il serbatoio dalla sovrapressione e non deve mai poterne essere
  separata; è la disposizione dei gruppi di sicurezza sanitari di pratica corrente.
  Verificato sul modello rigenerato: fra gruppo e bollitore non c'è nulla.
- **Fonte:** buona pratica documentata, Caleffi (SRC-008).

### 18. Valvola miscelatrice termostatica — `dhw-mixing-on-draw-off` v1.0.0 ✔

- **Cosa propone:** una miscelatrice termostatica sull'uscita dell'acqua calda.
- **Posizione funzionale:** a valle della valvola di intercettazione dell'uscita (scheda
  7b), prima della distribuzione alle utenze.
- **Perché lì:** l'accumulo si tiene caldo contro la legionella, ma alle utenze l'acqua
  deve arrivare a temperatura d'uso: la miscelatrice separa le due esigenze e protegge
  dalle scottature.
- **Fonte:** buona pratica documentata, Caleffi (SRC-008).

### 19. Ricircolo sanitario — regola **non presente**, rinvio registrato ✔

Il ricircolo ACS resta fuori dal pacchetto: sarebbe la prima regola «condizionata» e
richiede un dato (lunghezza della distribuzione) che il modello oggi non porta. Il rinvio
è registrato nel documento delle decisioni rimandate, §6. Non è una scheda mancante: è un
perimetro dichiarato.

---

## Esito della revisione trasversale (criterio 3 del WP2)

Domanda posta a ogni regola: **c'è contenuto ridotto o alterato per far entrare il disegno
nel foglio? La motivazione è impiantistica?**

| Regola | Esito |
|---|---|
| expansion-on-closed-circuit | ✔ conforme |
| safety-valve-on-generator | ✔ conforme |
| isolation-around-generator | ✚ nuova, conforme |
| isolation-around-pump | ✎ **corretta**: cardinalità ridotta per vincolo di foglio (D-074), frase «una sola valvola nel primo pacchetto» rimossa; ora 2.0.0 |
| isolation-around-storage | ✎ **corretta**: come sopra; ora 2.0.0, con osservazione sul doppio ritorno di zona |
| isolation-around-dhw-coil | ✚ nuova, conforme |
| cold-feed-isolation-on-dhw-storage | ✚ nuova, conforme |
| isolation-on-dhw-outlet | ✚ nuova, conforme |
| strainer-upstream-of-pump | ✔ conforme |
| dirt-separator-on-generator-return | ✔ conforme |
| air-separator-on-generator-flow | ✔ conforme |
| filling-unit-on-return | ✔ conforme |
| drain-on-storage | ✎ **corretta**: lo scarico stava fuori dalla sezione intercettata e a valvole chiuse avrebbe svuotato il circuito invece del serbatoio; spostato dal lato del serbatoio; ora 2.0.0 |
| thermometer-on-generator-flow | ✔ conforme |
| pressure-gauge-on-generator-return | ✔ conforme |
| dhw-check-on-cold-inlet | ✔ conforme |
| dhw-expansion-on-cold-inlet | ✔ conforme |
| dhw-safety-group-on-cold-inlet | ✔ conforme |
| dhw-mixing-on-draw-off | ✔ conforme |

Le uniche due regole che portavano contenuto ridotto per un vincolo di foglio erano le due
di intercettazione, e sono corrette. La revisione ha inoltre trovato **un errore di
posizione** che il pieno delle valvole ha reso visibile: lo scarico dell'accumulo finiva
fuori dalla sezione intercettata (scheda 12), ed è corretto. Nessun'altra motivazione cita
il foglio, la tavola o la resa grafica; tutte le motivazioni sono ragioni d'impianto. Le
fonti citano solo documenti presenti nel registro fonti con stato «acquisita/consultata»,
nella forma già prevista da D-047 e D-066 (fonte secondaria dichiarata secondaria).

## Verifiche eseguite su questo pacchetto

- Modello del caso di accettazione **rigenerato dalla catena corrente** e validato; una
  prova automatica ora impone che il file pubblicato coincida byte per byte con la
  rigenerazione.
- Conteggio automatico per ogni attacco di macchina: pompa di calore 2 valvole,
  circolatore 2, volano 4 (di cui 1 preesistente riconosciuta e non duplicata),
  bollitore 4. Nessun attacco collegato di macchina resta senza intercettazione sulla
  propria fila.
- Idempotenza: rieseguire le regole sul modello completato non propone nulla (provato in
  automatico e dalla riga di comando).
- Guardia D-069 verde: nessuna regola nomina un componente o una definizione in una
  condizione. Motore non toccato: la correzione è tutta nei dati.
- Rigenerazione identica bit a bit con semi di hash diversi.
