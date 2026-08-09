# Input PM — prossimi step · 8 agosto 2026

> Questo documento contiene indicazioni dirette del PM per la prossima sessione di sviluppo.
> Va letto dopo `HANDOFF.md` e `PROJECT_STATE.md`, prima di modificare il disegnatore.
> Non sostituisce l'architettura: precisa la composizione della tavola e l'ordine del lavoro.
> Dove precisa decisioni precedenti, registrare la precisazione nel decision log prima di implementarla.

## 1. Obiettivo della prossima fase

La parte di interpretazione e costruzione del grafo e' ormai abbastanza matura da poter usare la tavola come banco di prova reale.

L'ordine di lavoro e':

1. chiudere i due difetti della camminata del **tratto comune**, perche' oggi possono rendere il risultato dipendente dalla topologia particolare o perfino dal nome delle macchine;
2. portare a casa la **modalita' verifica**, con l'indirizzo del nodo vicino al componente, secondo D-110/D-111;
3. lavorare sulla **composizione della tavola**, mantenendo la centrale come unita' grafica indivisibile e ottimizzando davvero la disposizione prima di pensare a piu' fogli o formati maggiori;
4. completare cio' che serve della **libreria simboli** e il **cartiglio** per produrre tavole leggibili e confrontabili;
5. rigenerare le cinque tavole in modalita' verifica e farle giudicare visivamente dal PM;
6. usare gli errori visibili sulle tavole per tornare, se serve, alle regole del completatore invece di perfezionarle al buio.

I difetti non bloccanti dell'interprete e le regole accessorie ancora mancanti restano tracciati, ma non devono impedire di portare a casa il disegnatore.

---

## 2. Regola fondamentale: la centrale non si spezza

La **centrale termica va vista tutta insieme**.

Il compositore non deve mai dividere automaticamente la centrale su piu' fogli. GeneratorI, primario, accumuli/separatori, produzione ACS di centrale e relativi accessori principali devono restare nello stesso elaborato grafico.

La distinzione fra **centrale** e **distribuzione secondaria** deve essere esplicita e deterministica nel modello/piano di impaginazione: non puo' dipendere da una scelta opportunistica fatta durante il routing.

Se una centrale non entra, la prima risposta non e' spezzarla e non e' aumentare subito il formato: e' **ridisporre meglio gli oggetti**.

---

## 3. Prima si ottimizza il foglio esistente

L'escalation di formato e' una delle operazioni piu' costose e deve essere motivata.

Prima di aumentare formato o creare un'altra tavola, il compositore deve cercare seriamente una disposizione migliore, rispettando D-111:

- spostare i blocchi;
- cambiare il loro ordine relativo quando la topologia lo consente;
- usare meglio larghezza e altezza disponibili;
- prenotare spazio per cio' che verra' dopo;
- compattare gli spazi entro i minimi grafici ammessi;
- ridurre linee inutilmente lunghe;
- ridurre curve e accavallamenti;
- cercare un riempimento bilanciato e simmetrico del foglio.

Non basta trovare una soluzione valida: bisogna cercare una soluzione a **costo basso**.

In termini qualitativi:

`ridisporre oggetti` << `accettare qualche percorso piu' lungo` << `separare una distribuzione significativa` << `aumentare formato` << `spezzare la centrale`

L'ultimo caso e' vietato in automatico.

---

## 4. Quando la distribuzione puo' andare su un secondo foglio

Separare la distribuzione non e' una soluzione automatica al problema dello spazio.

La distribuzione va su una seconda tavola solo se valgono entrambe queste condizioni:

1. toglierla dalla tavola principale migliora in modo sostanziale la leggibilita' della centrale;
2. la distribuzione, presa da sola, ha abbastanza contenuto tecnico e grafico da costituire una tavola utile.

Una seconda tavola quasi vuota e' un errore di composizione.

### Esempio da NON fare

Seconda tavola con soltanto:

`circolatore -> collettore -> due tubazioni`

Questa distribuzione deve restare sulla tavola della centrale.

### Esempio che puo' meritare una tavola propria

Distribuzione con piu' circuiti e contenuto autonomo, per esempio:

- collettore generale;
- diversi gruppi di pompaggio;
- circuiti miscelati;
- UTA;
- fan-coil;
- pavimento radiante;
- ritorni e relativi accessori.

Non fissare ora una soglia banale del tipo «N componenti = seconda tavola». Il criterio deve misurare l'**utilita' reale del foglio** e penalizzare fortemente una tavola poco occupata.

---

## 5. Escalation di formato

Il formato superiore e' l'ultima risorsa, non la prima.

Ordine concettuale:

1. provare a comporre centrale + distribuzione sul formato previsto;
2. ottimizzare seriamente la disposizione;
3. se la distribuzione e' abbastanza ricca da meritare una tavola autonoma, provare centrale su foglio 1 e distribuzione su foglio 2;
4. solo se la **centrale da sola**, ben composta, continua a non entrare, valutare il formato superiore;
5. la centrale non viene comunque spezzata automaticamente.

Per centrali eccezionalmente grandi — ad esempio impianti dell'ordine del MW con molte macchine e sistemi diversi, caldo/freddo, chiller, trattamento o filtrazione acqua, ecc. — il passaggio ad A1 e' una soluzione naturale. Questo esempio non va trasformato in una soglia automatica da 1000 kW: il criterio resta la capacita' di comporre in modo leggibile la centrale completa.

Ogni escalation di formato deve lasciare una motivazione verificabile: deve risultare che le alternative a costo inferiore sono state tentate e non hanno prodotto una tavola accettabile.

---

## 6. Conseguenza pratica per il compositore

La composizione non deve essere un semplice algoritmo «non entra -> nuovo foglio».

Deve confrontare poche alternative deterministiche e scegliere quella a costo minore, preservando questi vincoli:

- centrale intera su un solo foglio;
- lettura da sinistra a destra;
- macchine principali a sinistra;
- spazio prenotato per i blocchi successivi;
- foglio riempito in modo equilibrato;
- lunghezze, curve e accavallamenti penalizzati;
- seconda tavola solo se il sottosistema separato la giustifica;
- formato maggiore fortemente penalizzato;
- nessuna tavola quasi vuota.

Il risultato atteso non e' soltanto «ci sta»: deve assomigliare a una tavola che un disegnatore MEP sceglierebbe davvero di produrre.

---

## 7. Cosa mostrare al PM al prossimo giro

Dopo i primi tre step — tratto comune, modalita' verifica, composizione — rigenerare le cinque tavole.

Il PM deve poter giudicare visivamente almeno:

- se la centrale si legge tutta insieme;
- se i gruppi sono disposti con una logica naturale;
- se ci sono accessori palesemente duplicati o fuori posto;
- se le linee sono inutilmente lunghe o contorte;
- se gli indirizzi in modalita' verifica permettono di indicare subito un pezzo sbagliato;
- se un eventuale secondo foglio contiene davvero una distribuzione che merita una tavola autonoma.

Da quel giudizio si decide il giro successivo sulle regole e sulla grafica.
