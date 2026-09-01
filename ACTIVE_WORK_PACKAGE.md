# ACTIVE WORK PACKAGE — DRAW-001

**Stato:** ASSEGNATO DAL PM  
**Data:** 2026-09-01  
**Assegnato da:** PM (Codex)  
**Assegnato a:** DEV team (Claude)  
**Ramo da creare:** `claude/draw-001-tavola1-qualita`  
**Base:** il `main` corrente che contiene questo Work Package. Prima di lavorare, il DEV deve riportarne lo SHA.

## Regola di ingresso

Questo è l'unico incarico operativo corrente. Le sezioni storiche `Now`, `Next` e “primo lavoro” di `HANDOFF.md` e `PROJECT_STATE.md` servono come contesto, ma non autorizzano attività aggiuntive.

Il DEV deve:

1. leggere integralmente `HANDOFF.md`, `AGENTS.md`, questo file e gli input PO collegati;
2. rispondere ai sentinel checks dell'handoff;
3. creare il ramo indicato dal `main` corrente;
4. lavorare solo su questo pacchetto;
5. aprire una sola PR e fermarsi in attesa della verifica PM.

## Contesto

Il PO vuole tornare subito allo sviluppo reale e vedere un miglioramento visibile della tavola dell'**impianto 1**. Le prime tavole sono state giudicate da buttare: tubazioni con giri inutili, spazio usato male e componenti troppo distanti.

Il primo blocco tecnico già misurato è I-018/D-120: avvicinando correttamente le valvole di intercettazione agli attacchi delle macchine, una tubazione finisce sotto un simbolo invece di essere interrotta. La regola di vicinanza è già costruita e migliorativa, ma non può essere consegnata finché questo difetto non è chiuso.

La tavola, dopo D-118, è inoltre troppo compressa in un angolo: riempimento storico circa 27%, mentre la misura di qualità esistente richiede 60%. La misura esiste già; deve diventare un obiettivo del collocatore, come previsto da D-111 e D-114.

## Obiettivo del pacchetto

Produrre una nuova tavola dell'impianto 1 **visibilmente migliore**, chiudendo nello stesso ciclo due cause ad alto impatto:

1. impedire che una tubazione attraversi il corpo di un simbolo quando deve terminare sul suo attacco;
2. attivare la vicinanza delle valvole di intercettazione prevista da D-120;
3. usare riempimento e bilanciamento già misurati come obiettivi nella scelta deterministica del layout, senza introdurre un Drawing Director AI.

Non è un audit e non è un pacchetto di documentazione. Il risultato principale è una tavola PDF e raster confrontabile con la baseline.

## Perimetro consentito

Il DEV può modificare soltanto quanto necessario dentro:

- `src/disegnatore_mep/layout/**`
- `src/disegnatore_mep/validation/**`
- `tests/layout/**`
- `tests/validation/**`
- `tests/acceptance/test_drawing.py`
- `scripts/tavole-di-verifica.sh`, solo se necessario per rendere riproducibile la generazione
- `docs/collaudi/DRAW-001/**`, esclusivamente per rapporto, metriche e artefatti prima/dopo
- `PROJECT_STATE.md`, esclusivamente per registrare la consegna e i risultati misurati
- `docs/input-pm/REGISTRO.md`, senza chiudere input del PO: il DEV può soltanto proporne la chiusura

Se la causa richiede un file fuori da questo elenco, il DEV si ferma e lo comunica al PM prima di modificarlo.

## Fuori perimetro

- interprete, grafo, assemblatore e regole MEP;
- cataloghi e simboli;
- impianti 2–5;
- Drawing Director AI;
- nuove decisioni di prodotto;
- riorganizzazione generale dei documenti;
- recupero, merge o cancellazione dei rami storici;
- modifica di questo Work Package;
- merge della propria PR.

## Metodo di esecuzione

### 1. Baseline obbligatoria

Prima delle modifiche:

- eseguire `bash scripts/setup-env.sh`;
- rigenerare esclusivamente la tavola dell'impianto 1 dalla pipeline corrente;
- salvare PDF, PNG rasterizzato e metriche in `docs/collaudi/DRAW-001/baseline/`;
- registrare almeno: riempimento, rapporto tra quadranti, incroci, lunghezza totale, tratte con più di tre pieghe, collisioni tubo-simbolo e distanza delle valvole dagli attacchi;
- verificare che due generazioni dallo stesso input producano lo stesso layout.

### 2. Correzione delle cause

- trovare la causa per cui la linea non viene interrotta dal simbolo;
- correggerla come invariante generale di routing/resa grafica, non come eccezione per l'impianto 1;
- attivare la regola D-120 sulle valvole vicine;
- integrare riempimento e bilanciamento nella funzione di costo o nella scelta tra candidati già deterministici;
- non spostare manualmente componenti e non introdurre coordinate specifiche dell'esempio.

### 3. Verifica e artefatti

Dopo le modifiche:

- rigenerare l'impianto 1;
- salvare PDF, PNG e metriche in `docs/collaudi/DRAW-001/finale/`;
- produrre un confronto affiancato `prima-dopo.png`;
- eseguire test mirati, suite completa, ruff e mypy;
- far eseguire il collaudo indipendente previsto da D-083.

## Criteri di accettazione

La PR è accettabile soltanto se:

1. nessuna tubazione attraversa il corpo pieno di un simbolo, salvo il tratto che termina esattamente su un attacco previsto;
2. il caso di regressione che riproduce I-018 fallisce sulla baseline e passa dopo la correzione;
3. le valvole interessate da D-120 risultano a 2,5–5 mm dagli attacchi dell'apparecchio da isolare;
4. due generazioni consecutive dello stesso input producono lo stesso layout;
5. il riempimento aumenta di almeno 10 punti percentuali rispetto alla baseline oppure raggiunge il 60%;
6. il rapporto tra quadrante più pieno e più vuoto migliora rispetto alla baseline;
7. incroci e tratte con più di tre pieghe non peggiorano rispetto alla baseline;
8. il grafo canonico dell'impianto 1 resta invariato;
9. PDF e raster finale sono leggibili e il confronto prima/dopo rende visibile il miglioramento;
10. la suite completa, ruff e mypy passano, salvo difetti preesistenti documentati con prova;
11. nessun file fuori perimetro è modificato;
12. la PR resta aperta e non fusa fino al verdetto del PM.

## Consegna al PM

La PR deve contenere:

- causa tecnica dei due difetti;
- metriche prima/dopo in tabella;
- PDF finale;
- PNG finale;
- confronto raster prima/dopo;
- test aggiunti e output delle verifiche;
- elenco completo dei file modificati;
- SHA iniziale e SHA finale;
- eventuali difetti residui realmente bloccanti.

Il DEV consegna. Il PM verifica, approva o respinge e, se approva, esegue direttamente il merge.
