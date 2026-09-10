# ACTIVE WORK PACKAGE — DRAW-006-R1

- **Release:** 0.3 — generalizzazione, revisione della tavola 2
- **Stato:** APPROVATO DAL PM, PRONTO PER IL DEV
- **Data:** 2026-09-10
- **PR da aggiornare:** #24
- **Base tecnica da conservare:** testa `9b925b7`, integrata con l'ultima `main`
- **Ramo da riutilizzare:** `claude/draw-006-tavola2-semantica-v4n8o5`
- **Fixture grafica principale:** impianto 2

## Verdetto e obiettivo

La PR #24 non è approvata nello stato corrente, ma contiene avanzamenti validi da
conservare: rubinetto portamanometro, funzioni interne dei compositi e stati idraulici
delle multivia. Questa revisione corregge quattro difetti generali: ordine semantico degli
accessori, allineamento attraverso componenti multivia, distinzione fra adduzione ACS e
riempimento tecnico, vicinanza D-120.

Le correzioni sono regole di prodotto valide per qualunque impianto. Sono vietate
eccezioni basate su ID, coordinate, nomi dei file o quantità dei componenti delle fixture.

## A. Ordine semantico indipendente dagli identificativi

1. Il soggetto semantico di uno stacco è l'accessorio terminale raggiunto attraverso i
   raccordi e gli organi propri dello stacco, non il primo organo incontrato.
2. I vincoli `before`/`after` ordinano topologicamente i componenti nel verso del fluido.
   ID, ordine nel file e ordine delle connessioni possono spareggiare soltanto elementi
   semanticamente equivalenti.
3. L'ordine semantico è un vincolo duro. Se aumenta curve o incroci, il motore deve
   recuperare geometria con traslazioni, movimenti di gruppo e nuovo routing; non può
   conservare l'ordine sbagliato perché costa meno.
4. Scrivere prima prove che rinominano gli ID, ne invertono l'ordinamento e mescolano le
   connessioni: l'ordine funzionale e il costo devono restare invarianti.
5. Regressione tavola 1: il manometro resta dopo il riempimento, con rete ordinaria non
   oltre 4 curve, 1 incrocio e 425 mm; stacchi statici non oltre 0/0/45 mm.

## B. Allineamento per stato idraulico

1. Generalizzare i candidati di asse: cercare coppie di porte compatibili fra macchine
   principali anche attraverso raccordi, catene inline e componenti multivia, per ciascuno
   stato idraulico ammesso dal catalogo.
2. Provare almeno: traslazione del gruppo a monte, del gruppo a valle e asse comune.
   Quando due macchine hanno coppie mandata/ritorno compatibili, provare l'allineamento
   simultaneo delle due coppie.
3. Gli accessori locali si muovono con il gruppo; ogni candidata viene reinstradata per
   intero e confrontata col costo-peso. L'allineamento è una candidata, non un assoluto.
4. Sulla tavola 2 deve essere realmente provato l'allineamento PDC–puffer attraverso la
   deviatrice e scelto quando riduce il costo totale.

## C. Adduzione fredda del bollitore ACS

1. Per un accumulo sanitario pressurizzato usare un solo **gruppo di sicurezza composito
   EN 1487** sull'ingresso freddo. Il catalogo ne dichiara intercettazione, ritegno
   controllabile e sicurezza; le regole non aggiungono duplicati esterni.
2. Il vaso di espansione sanitario non è automatico: dato di progetto/catalogo presente
   → applicare; assente → domanda o raccomandazione, senza aggiungere il pezzo. Nella
   fixture 2, priva del dato, non va generato automaticamente.
3. Non aggiungere uno sfiato automatico al bollitore ACS salvo porta dedicata e fonte o
   requisito esplicito. Il riempimento sanitario ordinario si sfoga da un'utenza aperta.
4. Lo scarico preferisce la porta `drain` dichiarata dal serbatoio. Soltanto se la porta
   non esiste è ammesso lo stacco sulla linea fredda, con motivazione nel rapporto.
5. Prove sintetiche devono coprire sia il serbatoio con porta di scarico sia quello senza.

## D. Riempimento del circuito tecnico

1. Modellare il gruppo di riempimento come ponte a due reti e due porte:
   `cold_water` in ingresso → gruppo → `heating_water` in uscita.
2. Collegarlo mediante T a una sorgente AF già approvata e al ritorno tecnico comune. Se
   manca una sorgente AF approvata, produrre una domanda: mai un componente pendente.
3. La variante Caleffi 553 dichiara come funzioni interne riduttore di pressione, filtro,
   intercettazione e ritegno; non vanno duplicati esternamente.
4. Il verso è AF → circuito tecnico e la posa deve mantenere leggibilmente distinta questa
   derivazione dall'adduzione fredda del bollitore ACS.
5. Scrivere prove generali su medium, porte, verso, funzioni integrate e assenza di
   duplicati.

## E. Vicinanza degli organi D-120

1. Correggere la valvola rimasta a 27,5 mm: tutti i 16 organi della tavola 2 devono stare
   a 2,5÷5 mm dal pezzo servito.
2. La proprietà deve derivare dalla relazione funzionale. Prima di dichiararla
   irrealizzabile provare la traslazione gratuita del gruppo locale.

## Criteri di accettazione

1. Ordine degli accessori invariato rinominando ID e mescolando connessioni.
2. La tavola 1 conserva ordine funzionale e soglie 4/1/425 mm e 0/0/45 mm.
3. Il motore genera e valuta assi attraverso multivia; sulla tavola 2 PDC e puffer sono
   allineati quando questa è la candidata di costo minore.
4. L'ingresso ACS contiene un solo gruppo EN 1487 composito, senza vaso o sfiato inventati.
5. Lo scarico usa la porta dedicata quando dichiarata e il fallback soltanto quando manca.
6. Il riempimento tecnico collega davvero AF e ritorno tecnico comune, senza organi
   duplicati e senza confondersi con l'adduzione ACS.
7. Vicinanza D-120 tavola 2: 16/16.
8. Tutti e cinque gli impianti arrivano alla posa; nessuna regressione diventa `skip` o
   `xfail`.
9. Suite completa, `ruff`, `mypy --strict` e doppia generazione deterministica verdi.

## Consegna e perimetro

Aggiornare la stessa PR #24 e lo stesso ramo, senza merge. Consegnare PDF, PNG, SVG,
geometria, metriche, preflight e confronto prima/dopo della **sola tavola 2**, usando
`9b925b7` come prima. La tavola 1 è soltanto regressione automatica; gli impianti 3–5
sono soltanto test di posa. Non generare i loro pacchetti grafici completi.

Fuori perimetro: riempimento estetico del foglio, cartiglio, revisione della sigla
provvisoria `RM`, audit di simboli estranei, governance e ottimizzazione generale delle
prestazioni.
