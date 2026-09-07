# ACTIVE WORK PACKAGE — DRAW-005

- **Release:** 0.2A — tavola 1 tecnicamente corretta e approvabile
- **Stato:** APPROVATO DAL PM, PRONTO PER IL DEV
- **Data:** 2026-09-05
- **Assegnato a:** DEV team (Claude)
- **Base:** ultima `main`, contenente il merge di `DRAW-004` e questo pacchetto
- **Ramo:** `claude/draw-005-contenuto-simboli-tavola1`
- **Campo:** solo impianto 1 (D-116)

## Obiettivo

Correggere contenuto MEP e simboli critici della tavola 1 secondo la matrice già
verificata dal PM in `docs/pm/2026-09-05-audit-simboli-e-contenuto-tavola1.md`.

Non devi interpretare gli allegati del PO, fare ricerca di dominio, scegliere una
simbologia o ridefinire la roadmap. Implementa la matrice e segnala soltanto eventuali
incompatibilità tecniche reali.

## Ordine di lavoro

### A. Prove del grafo prima del disegno

Scrivere test generali che dimostrino:

1. una macchina e il filtro sul proprio ritorno possono formare un gruppo isolato da una
   sola valvola lato rete più l'intercettazione sull'altro ramo; non compare una valvola
   ridondante fra filtro e macchina;
2. il gruppo di riempimento dell'accumulo combinato è uno solo e appartiene alla rete di
   acqua tecnica, sul ritorno comune o su attacco tecnico dedicato; mai sulla rete
   sanitaria;
3. l'accumulo combinato espone `cold_in` e `dhw_out`, collegati rispettivamente ad AF e
   distribuzione ACS, mentre il volume tecnico alimenta primario e secondario;
4. puffer, bollitore e accumulo combinato sono definizioni diverse con porte e medium
   coerenti; nessuna porta viene permutata dal layout.

Correggere regole, catalogo, assemblatore e fixture della tavola 1 quanto basta a far
passare queste prove. Non aggiungere dispositivi non richiesti e non modificare potenze,
volumi, temperature o diametri.

### B. Contratti grafici

Scrivere test generali che dimostrino:

1. il filtro è una Y riconoscibile con ramo e gambo inferiori in ogni rotazione ammessa;
2. un confine uscente e uno entrante condividono il tipo grafico ma puntano entrambi nel
   verso locale dell'acqua;
3. `P`, `T`, `F` e qualunque futuro glifo interno dichiarato leggibile restano dritti
   rispetto al foglio a 0/90/180/270°, senza alterare corpo e porte;
4. il simbolo PDC usato dalla tavola 1 ha 15 mm fra mandata e ritorno e lascia spazio
   funzionale agli accessori senza sovrapposizioni;
5. il simbolo dell'accumulo combinato mostra un serpentino sanitario continuo da
   `cold_in` a `dhw_out`, mentre gli attacchi tecnici entrano nel volume del mantello;
6. sigle delle macchine principali sempre presenti; indirizzi di nodo assenti per
   default e attivabili esplicitamente; testi invarianti rispetto a simboli e tubazioni.

Aggiornare i manifesti, il generatore dei simboli e il renderer con una soluzione
generale. Non correggere stringhe SVG a mano senza aggiornare la fonte generativa e i
test raster/vector.

### C. Posa sul nuovo grafo

- rigenerare la tavola 1 usando il motore `DRAW-004`;
- mettere la valvola comune di mandata vicino a `primary_in` dell'accumulo;
- usare il maggiore interasse PDC per ridurre i gradini, senza imporre l'allineamento se
  il costo globale peggiora;
- dopo ogni modifica al grafo eseguire routing e costo sull'intera tavola;
- non introdurre coordinate o eccezioni per ID dell'impianto 1.

## Gerarchia di accettazione

1. correttezza del grafo e delle porte;
2. nessun dispositivo ridondante o sulla rete sbagliata;
3. simboli conformi alla matrice e leggibili;
4. zero backtracking e zero tratte oltre tre pieghe;
5. minimizzazione di curve, incroci e lunghezza sul **nuovo grafo**;
6. testi solo dopo la geometria e con costo nullo.

La lunghezza DRAW-004 di 577,5 mm non è un limite sul nuovo grafo: il contenuto cambia.
Il rapporto deve però separare chiaramente quanto tubo deriva da nuovi collegamenti e
quanto dal layout, evitando di dichiarare miglioramenti fra grafi non equivalenti.

## Criteri di accettazione

1. Tutte le prove A e B sono verdi e non dipendono da ID o coordinate della tavola 1.
2. Il JSON completato dell'impianto 1 soddisfa integralmente le cinque regole
   impiantistiche dell'audit PM.
3. Nessuna valvola fra ciascun filtro a Y di ritorno e la relativa PDC; una valvola lato
   rete per ramo di ritorno e l'intercettazione di mandata necessaria.
4. Un solo gruppo di riempimento sulla rete tecnica; zero gruppi sulle reti AF/ACS.
5. AF collegata a `cold_in` e uscita sanitaria da `dhw_out`, visibili anche nel simbolo.
6. Confini orientati col flusso e glifi interni sempre leggibili rispetto alla tavola.
7. Nessuna sovrapposizione simbolo/simbolo o tubo/simbolo; zero backtracking; zero tratte
   oltre tre pieghe. Curve, incroci e lunghezza sono riportati senza confronto improprio.
8. Modalità consegna: sole sigle principali. Modalità verifica: indirizzi attivabili;
   nessuna modalità modifica posa o routing.
9. Suite completa, `ruff`, `mypy --strict` e determinismo verdi.
10. PDF, PNG, SVG, modello completato, geometria, metriche, preflight e rapporto in
    `docs/collaudi/DRAW-005/`, con confronto visivo contro DRAW-004.

## Perimetro consentito

- `rules/hydronic/` e moduli di rules/assembly necessari alla logica di isolamento;
- `examples/layout/catalog/` e fixture dell'impianto 1;
- `assets/symbols/`, `examples/graphics/build_symbols.py`, registry/renderer grafico;
- posa/routing soltanto se richiesti dalla nuova geometria delle porte, senza cambiare
  l'ordine di `SheetCost`;
- test generali e `docs/collaudi/DRAW-005/**`;
- aggiornamento di `PROJECT_STATE.md` e dello stato delle righe I-030… I-040, senza
  chiuderle.

Vietati: impianti 2–5, audit autonomo dei restanti simboli, nuova architettura AI,
cartiglio/spessori, chiusura degli input PO, modifica dei criteri o merge.

## Consegna

Salva progressivamente sul ramo remoto, apri una sola PR verso `main` e fermati. Il PM
verifica codice, grafo, fonti applicate e PDF; il PO decide la chiusura dei propri input.
