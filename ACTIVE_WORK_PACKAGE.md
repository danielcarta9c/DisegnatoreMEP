# ACTIVE WORK PACKAGE — DRAW-002

**Stato:** ASSEGNATO DAL PM  
**Data:** 2026-09-03  
**Assegnato da:** PM (Codex)  
**Assegnato a:** DEV team (Claude)  
**Ramo da creare:** `claude/draw-002-routing-qualita`  
**Base:** l'ultima `main`, che deve contenere il merge commit di DRAW-001 `bbe33ec83f8f442090fd549b2145c145412f531d`.

## Regola di ingresso

Questo è l'unico incarico operativo corrente. Il DEV parte dall'ultima `main`, crea il ramo indicato, esegue un solo pacchetto sostanziale e apre una sola PR. Non pubblica gli stessi commit su rami storici.

Prima di lavorare legge `HANDOFF.md`, `AGENTS.md`, questo file, `PROJECT_STATE.md`, `docs/input-pm/REGISTRO.md` e il collaudo di DRAW-001.

## Contesto

DRAW-001 è stato accettato e fuso perché ha prodotto un avanzamento reale:

- riempimento 28,7% → 41,0%;
- squilibrio fra quadranti 12,6 → 2,59;
- incroci 13 → 12;
- pieghe 33 → 27;
- tratte oltre tre pieghe 3 → 1;
- valvole D-120 in soglia 6/20 → 17/20;
- nessuna tubazione attraversa il corpo di un simbolo;
- grafo canonico invariato e suite completa verde.

La tavola resta però in modalità verifica. Il preflight porta ancora un bloccante: una tratta del ramo sanitario supera la propria porta e torna indietro per 40 mm. Tre valvole D-120 sono ancora fuori dalla fascia 2,5–5 mm. Restano inoltre 12 incroci, contro la soglia di qualità di 5.

Questi sono difetti di prodotto, non formalismi documentali.

## Obiettivo

Portare la tavola 1 dal primo miglioramento misurabile a una disposizione idraulica pulita, senza giri di ritorno e senza perdere i risultati di DRAW-001.

Il pacchetto deve affrontare insieme le cause di disposizione e routing che producono:

1. il ritorno sanitario che supera la porta e torna indietro;
2. le tre valvole D-120 fuori soglia;
3. gli incroci e la tratta con troppe pieghe ancora presenti.

La correzione deve essere generale e deterministica. Vietate coordinate, identificativi o eccezioni specifiche dell'impianto 1.

## Perimetro consentito

Il DEV può modificare soltanto quanto necessario dentro:

- `src/disegnatore_mep/layout/**`
- `src/disegnatore_mep/validation/**`
- `tests/layout/**`
- `tests/validation/**`
- `tests/acceptance/test_drawing.py`
- `scripts/tavole-di-verifica.sh`, solo se necessario per la riproducibilità
- `docs/collaudi/DRAW-002/**`, per rapporto, metriche e artefatti prima/dopo
- `PROJECT_STATE.md`, per registrare la consegna
- `docs/input-pm/REGISTRO.md`, senza chiudere input del PO

Se la causa richiede un file fuori perimetro, il DEV si ferma e lo segnala al PM.

## Fuori perimetro

- interprete, grafo, assemblatore, regole MEP, cataloghi e simboli;
- modifica della linea di terra o della convenzione che tiene le macchine alla stessa quota;
- decisione sul formato minimo A3;
- obiettivo del 60% di riempimento;
- impianti 2–5;
- Drawing Director AI;
- modifica di questo Work Package;
- merge della propria PR o interventi su rami storici.

Le questioni su quota macchine, 60% e formato richiedono una successiva decisione del PO; non bloccano DRAW-002.

## Metodo

1. Rigenerare dall'ultima `main` la sola tavola 1 e usare l'uscita di DRAW-001 come baseline.
2. Riprodurre con test mirati il ritorno da 40 mm e ciascuna delle tre valvole fuori soglia.
3. Individuare la causa comune nella disposizione/routing; non limitarsi a spostare localmente il caso.
4. Integrare nel costo la gravità dell'andata e ritorno, non soltanto il suo conteggio.
5. Cercare posizioni alternative che rendano raggiungibile la fascia D-120 senza occupare la soglia delle porte.
6. Ridurre gli incroci e le pieghe proteggendo riempimento, bilanciamento e assenza di linee sotto i simboli.
7. Rigenerare PDF, PNG, SVG, metriche e confronto prima/dopo in `docs/collaudi/DRAW-002/`.
8. Eseguire test mirati, suite completa, ruff, mypy e collaudo indipendente D-083.

## Criteri di accettazione

La PR è accettabile soltanto se:

1. `RUN_OVERSHOOTS_ITS_PORT` è assente: nessuna tratta supera la propria porta per poi tornare indietro;
2. tutte le valvole interessate da D-120 sono a 2,5–5 mm dall'attacco che devono isolare; nessuna soglia di porta è occupata;
3. gli incroci della tavola 1 scendono da 12 a non più di 5;
4. nessuna tratta supera tre pieghe;
5. nessuna tubazione attraversa o corre sotto il corpo di un simbolo;
6. il riempimento resta almeno al 41% e il rapporto fra quadranti non supera 3;
7. il grafo canonico resta invariato;
8. due generazioni consecutive producono geometria e SVG identici;
9. il preflight non contiene bloccanti né gli avvisi `TOO_MANY_CROSSINGS` e `RUN_WITH_TOO_MANY_BENDS`; resta ammesso soltanto l'avviso sul riempimento sotto il 60%, perché dipende da una scelta del PO fuori perimetro;
10. suite completa, ruff e mypy passano;
11. il confronto raster mostra una tavola più pulita senza regressioni visive;
12. nessun file fuori perimetro è modificato e la PR resta aperta fino al verdetto PM.

Se un criterio risulta tecnicamente irraggiungibile, il DEV non lo allenta e non lo reinterpreta: si ferma con prova quantitativa e chiede una decisione al PM prima di continuare.

## Consegna al PM

La PR deve riportare:

- causa tecnica dei difetti;
- tabella prima/dopo;
- PDF e PNG finali;
- confronto raster;
- output di test, ruff e mypy;
- SHA iniziale e finale;
- elenco file modificati;
- risultato del collaudo indipendente;
- eventuali difetti residui, senza dichiarare consegnabile una tavola che il preflight blocca.

Il DEV consegna. Il PM verifica una volta, approva o respinge con soli blocker materiali e, se approva, esegue direttamente il merge.
