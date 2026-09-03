# ACTIVE WORK PACKAGE — DRAW-002-R2

**Stato:** ASSEGNATO DAL PM — revisione vincolante dopo controllo visivo del PO  
**Data:** 2026-09-03  
**Assegnato da:** PM (Codex)  
**Assegnato a:** DEV team (Claude)  
**Ramo di lavoro:** `claude/draw-002-routing-qualita`  
**Base:** l'ultima `main` che contiene questa revisione. Se il ramo era già stato creato, il DEV si ferma, integra l'ultima `main` e riparte da questo testo.

## Correzione del PO

Il PO ha controllato la tavola di DRAW-001 e ha respinto la logica implicita del layout:

> «È come se aveste deciso che le PDC vanno a sinistra, il volume al centro e la distribuzione a destra equidistanti. Ho sempre detto che bisogna spostare le macchine perché spostare le macchine costa zero; invece gli incroci dei tubi, le curve e le lunghezze costano. Il flusso dei tubi è illeggibile e senza senso. Il ritorno dal serbatoio va prima avanti e poi torna indietro.»

Questa non è una nuova preferenza: è l'applicazione vincolante di D-078, D-080 e D-111.

- sinistra → destra esprime l'ordine di processo, non una distanza prefissata;
- il movimento di un componente non ha costo proprio;
- costano le conseguenze: ritorni, pieghe, incroci e lunghezza;
- riempimento e simmetria non autorizzano a spargere le macchine;
- se una linea supera la propria meta e torna indietro, la posizione dell'oggetto è sbagliata.

La precedente versione di DRAW-002 subordinava ancora troppo il lavoro alle rotte esistenti e imponeva di conservare il riempimento al 41%. Quel vincolo è ritirato: non si conserva una dispersione ottenuta allungando le tubazioni.

## Riferimenti visivi vincolanti

Prima di modificare il codice, il DEV e il collaudatore indipendente devono aprire e renderizzare tutti i PDF in:

`docs/input-pm/riferimenti-grafici/2026-09-03/`

Riferimenti principali forniti dal PO e prodotti dal suo disegnatore:

1. `schema-tipologico-pdc-volume-integrato.pdf` — riferimento più vicino alla tavola 1: PDC raggruppate, dorsali mandata/ritorno parallele, accumulo e distribuzione adiacenti;
2. `schema-tipologico-3-vie.pdf` — riferimento per compattezza, connessioni dirette e accessori prossimi alla tratta servita;
3. `schema-idraulico-sdp.pdf` — dimostra che anche un impianto complesso resta leggibile tramite gruppi funzionali e percorsi principali riconoscibili;
4. `schema-tipologico.pdf` — riferimento per dorsali rettilinee e sequenza degli apparecchi lungo il flusso.

Lo schizzo `schizzo-informale-po.png` conserva l'intuizione del PO, ma è secondario e non è un benchmark di qualità.

Questi documenti definiscono la grammatica grafica, non la topologia tecnica della tavola 1. Non si devono copiare componenti, collegamenti o contenuti appartenenti ad altri impianti. Si devono invece applicare le regole ricorrenti:

- mandata e ritorno leggibili come dorsali continue e distinguibili;
- apparecchi principali vicini in funzione delle connessioni, senza equidistanza artificiale;
- sequenza geometrica coerente con la sequenza idraulica;
- accessori collocati vicino all'attacco o alla tratta che servono;
- rami brevi, diretti e ortogonali; nessun avanzamento seguito da ritorno;
- etichette e richiami tenuti fuori dai percorsi principali;
- circuiti ausiliari separati quando la separazione aumenta la leggibilità.

Il rapporto finale deve includere una tabella «regola osservata → almeno due riferimenti in cui ricorre → applicazione nella tavola 1». Non è sufficiente affermare di aver letto i file.

## Obiettivo

Ricostruire la disposizione della tavola 1 facendo dipendere le posizioni delle macchine dal costo complessivo delle tubazioni.

Il risultato atteso non è «la stessa composizione con linee un po' migliori». Il motore deve poter avvicinare, allineare, traslare e ruotare PDC, accumulo, terminale e componenti principali finché il disegno completo risulta più economico e leggibile.

In particolare, il terminale non deve restare estremamente lontano dall'accumulo solo per occupare la fascia destra: va avvicinato se ciò riduce tubo, pieghe o incroci mantenendo l'ordine di processo.

## Principio costo-peso

La valutazione riguarda la tavola completa, accessori compresi. Lo spostamento geometrico di un simbolo pesa zero; pesa ciò che produce.

Ordine vincolante di valutazione:

1. **correttezza dura:** niente collisioni, sovrapposizioni longitudinali, tubi sotto simboli o soglie di porta occupate;
2. **backtracking:** prima il numero di tratte che superano la meta e tornano indietro, poi la somma dei millimetri di ritorno;
3. **pieghe:** numero complessivo e tratte oltre tre pieghe;
4. **incroci:** costano, ma un incrocio leggibile resta più economico di un lungo giro costruito per evitarlo;
6. **lunghezza totale delle tubazioni;**
7. **riempimento, equilibrio e simmetria:** discriminano soltanto fra soluzioni comparabili sui costi precedenti; non comprano tubo, curve o dispersione artificiale.

Il confronto può essere lessicografico o numerico con pesi documentati, ma deve dimostrare queste priorità con test di proprietà. Non è ammesso premiare la distanza regolare fra gruppi o la distanza dal centro del foglio.

## Perimetro consentito

- `src/disegnatore_mep/layout/**`
- `src/disegnatore_mep/validation/**`
- `tests/layout/**`
- `tests/validation/**`
- `tests/acceptance/test_drawing.py`
- `scripts/tavole-di-verifica.sh`, solo per la riproducibilità
- `docs/collaudi/DRAW-002/**`
- `PROJECT_STATE.md`
- `docs/input-pm/REGISTRO.md`, senza chiudere input del PO

Se la causa richiede altro, il DEV si ferma e lo segnala al PM.

## Fuori perimetro

- interprete, grafo, assemblatore, regole MEP, cataloghi e simboli;
- coordinate o identificativi specifici dell'impianto 1;
- modifiche manuali alla tavola;
- impianti 2–5;
- Drawing Director AI;
- decisioni su formato minimo, linea di terra o più tavole;
- modifica di questo Work Package;
- merge della propria PR o lavoro su rami storici.

## Metodo obbligatorio

1. Aprire e renderizzare i quattro PDF di riferimento; registrare le regole ricorrenti prima di formulare la soluzione.
2. Usare la tavola finale DRAW-001 come baseline.
3. Individuare perché il posizionamento produce fasce quasi equidistanti e perché il ciclo di miglioramento non sa avvicinare terminale e accumulo.
4. Scrivere prima test generali che dimostrino:
   - una macchina collegata può spostarsi senza penalità propria;
   - fra due disposizioni valide vince quella con meno ritorno, pieghe, incroci o tubo, nell'ordine stabilito;
   - il riempimento non può vincere comprando lunghezza o curve;
   - l'ordine di processo resta rispettato senza imporre distanze regolari.
5. Ampliare la ricerca delle posizioni: non soltanto piccoli spostamenti attorno alla posa iniziale, ma candidati deterministici ricavati da porte, adiacenze funzionali e allineamenti con i componenti collegati.
6. Re-instradare sempre l'intera tavola dopo ogni candidato e misurare l'uscita effettivamente disegnata.
7. Rigenerare PDF, PNG, SVG, metriche e confronto prima/dopo.
8. Eseguire test mirati, suite completa, ruff, mypy e collaudo indipendente D-083.

## Criteri di accettazione

1. Il terminale viene avvicinato all'accumulo quando ciò riduce il costo delle tubazioni; non resta a distanza regolare per riempire la fascia.
2. Nessuna tratta supera la propria porta e torna indietro: conteggio e millimetri di backtracking pari a zero.
3. Tutte le valvole D-120 stanno a 2,5–5 mm dall'attacco che isolano, senza occupare la soglia.
4. Nessuna tratta supera tre pieghe.
5. Gli incroci scendono dai 12 della baseline e la tavola non costruisce giri più lunghi per evitarli. Obiettivo di qualità: non più di 5.
6. Lunghezza totale inferiore alla baseline DRAW-001 di 1177,5 mm; il rapporto deve indicare quanto tubo è stato eliminato.
7. Nessuna tubazione attraversa o corre sotto un simbolo; nessuna collisione grafica.
8. L'ordine di processo da sinistra a destra resta leggibile, ma non compaiono distanze equidistanti imposte.
9. Il riempimento può scendere sotto il 41% se la tavola diventa più compatta e le tubazioni costano meno. Non sono ammesse propaggini create solo per aumentarlo.
10. Grafo canonico invariato e due generazioni consecutive identiche.
11. Suite completa, ruff e mypy verdi.
12. Il collaudo indipendente giudica leggibile il flusso complessivo, non soltanto conformi le metriche.
13. La tavola rende immediatamente riconoscibili le dorsali di mandata e ritorno e applica la grammatica ricorrente dei quattro riferimenti, senza copiarne la topologia.
14. Il collaudatore dichiara esplicitamente di avere aperto e confrontato i quattro PDF con il raster finale.
15. Nessun file fuori perimetro; PR aperta fino al verdetto PM.

Se l'obiettivo di 5 incroci non è raggiungibile senza aumentare backtracking, pieghe o lunghezza in modo contrario al costo-peso, il DEV consegna la frontiera dei candidati misurati e chiede al PM; non altera i pesi e non forza un giro.

## Consegna al PM

La PR deve mostrare:

- tabella delle regole ricorrenti osservate nei quattro PDF e loro applicazione;
- causa dell'equidistanza implicita;
- funzione costo-peso prima e dopo;
- tabella con backtracking, pieghe, incroci, lunghezza, distanze valvole e riempimento;
- PDF e PNG finali e confronto raster;
- prove che il posizionamento, non un rattoppo locale del routing, ha prodotto il miglioramento;
- test, ruff, mypy, SHA e file modificati;
- verdetto del collaudo indipendente.

Il DEV consegna. Il PM esegue una sola revisione decisionale e fonde soltanto se la tavola mostra un miglioramento materiale.
