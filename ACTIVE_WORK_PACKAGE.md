# ACTIVE WORK PACKAGE — DRAW-004

- **Release:** 0.2 — tavola 1 leggibile e approvabile
- **Stato:** APPROVATO DAL PM, PRONTO PER IL DEV
- **Data:** 2026-09-04
- **Assegnato a:** DEV team (Claude)
- **Base:** ultima `main`
- **Ramo:** `claude/draw-004-assi-dorsali-tee`
- **Campo:** solo impianto 1 (D-116)

## Obiettivo di prodotto

Ridurre ancora il costo reale della rete facendo ragionare la posa come un disegnatore:
prima si cercano buoni assi fra le porte delle macchine e dorsali principali continue;
poi si innestano gli stacchi. Spostare o ruotare macchine, pile e accessori non ha costo;
backtracking, curve, incroci/sormonti e lunghezza delle tubazioni hanno costo.

Questa non è una regola geometrica assoluta. L'allineamento fra due porte, la dorsale
rettilinea e la T che assorbe una curva sono **candidati** da generare e confrontare con
la posa corrente. Il motore li accetta solo se la tavola completa, dopo il routing di
tutte le reti, migliora secondo `SheetCost` e rispetta tutti i vincoli.

Gli esempi grafici del PO restano materiale del collaudo PM. Il DEV non deve ricavarne
requisiti ulteriori: deve attuare quanto scritto qui.

## Diagnosi tecnica del PM

La pipeline resta `place_sheet -> improve_sheet -> settle_sheet`.

1. `layout/improve.py::_port_moves()` genera già l'allineamento con la porta del vicino,
   ma per una porta orizzontale salta il candidato quando il leader è `Standing.GROUND`.
   Anche `_column_moves()` annulla lo spostamento verticale se nella colonna esiste un
   pezzo a terra. In uno schema funzionale la quota iniziale è un suggerimento di posa,
   non una ragione per conservare una curva evitabile.
2. Le mosse correnti tendono a muovere un solo estremo verso l'altro. Mancano candidati
   coordinati che confrontino almeno: movimento del gruppo a monte, movimento del gruppo
   a valle e riallineamento di entrambi attorno a un asse comune.
3. La rete viene misurata correttamente come tavola completa, ma fra i candidati manca
   l'ossatura «dorsale prima, stacchi dopo»: una catena principale può quindi conservare
   un dogleg anche quando spostare gratuitamente i suoi pezzi renderebbe continuo l'asse.
4. `layout/place.py::rotation_for()` impone che tutti gli attacchi non destinati al ramo
   di una T restino orizzontali. Di conseguenza il raccordo non può usare due imbocchi
   ortogonali come prosecuzione e assorbire il gomito nel punto di diramazione.

## Comportamento da costruire

### 1. Candidati di allineamento delle porte

Per ogni collegamento fra macchine principali o fra una macchina e una dorsale:

- ricavare gli assi possibili dalle coordinate e dalle facce delle porte, mai dagli ID;
- generare l'alternativa che allinea le porte e lascia il rettilineo necessario agli
  accessori in linea;
- generare, quando applicabile, lo spostamento del gruppo a monte, del gruppo a valle e
  dei due gruppi verso un asse comune;
- consentire anche spostamenti verticali di macchine o pile inizialmente classificate a
  terra, se non esiste un vincolo fisico dichiarato dal modello e se restano rispettati
  griglia, distanze, area e ordinamento di processo;
- una pila può cambiare posizione o interasse in modo coordinato, ma non può perdere il
  proprio ordine né sovrapporre i membri.

Non scrivere coordinate, nomi `pdc-*`, `accumulo` o eccezioni per l'impianto 1.

### 2. Dorsale prima, stacchi dopo

Individuare dalla topologia le sequenze principali fra sorgente, accumulo/separatore e
utilizzatore. Fra i candidati deve esistere una posa che:

- conserva rettilineo l'asse principale finché non serve davvero cambiare direzione;
- colloca i raccordi sulla dorsale e fa partire da lì i rami;
- evita che l'inserimento di un ramo pieghi inutilmente la dorsale;
- valuta comunque l'esito soltanto dopo `settle_sheet` e il reinstradamento completo di
  tutte le reti.

Non introdurre un secondo costo o un secondo decisore: il confronto finale resta
`SheetCost`.

### 3. T che può assorbire una curva

Quando tre collegamenti si incontrano, il motore deve poter provare anche una posa nella
quale il percorso principale usa due attacchi ortogonali della T e il terzo è lo stacco.
La T resta presente: ciò che può sparire è il gomito separato.

- la scelta della coppia di attraversamento è una proprietà della posa, non una modifica
  del grafo né della connettività;
- provare soltanto rotazioni e permutazioni ammesse dal simbolo;
- conservare verso del fluido, appartenenza alla rete e `connection_ids`;
- la configurazione ortogonale vince solo se riduce il costo complessivo della tavola.

### 4. Gerarchia invariata

- correttezza del grafo e delle connessioni;
- violazioni geometriche e accessori non ospitati;
- backtracking, tratte oltre tre pieghe, curve, incroci/sormonti, lunghezza;
- riempimento e bilanciamento soltanto come spareggio;
- testi e richiami dopo la geometria, con costo nullo e senza alcuna influenza sul
  confronto.

Non cambiare l'ordine di `SheetCost` in questo pacchetto. Se due obiettivi rivelano un
conflitto concreto, misurarlo nel rapporto e lasciarne la decisione al PM.

## Test generali da scrivere prima del codice

1. Due macchine con porte collegabili direttamente ma disallineate: esiste un candidato
   che sposta gratuitamente una macchina o il suo gruppo, elimina almeno una curva e
   batte la posa iniziale.
2. Lo stesso allineamento non viene accettato quando introduce una violazione, un
   backtracking o un incrocio che lo rende globalmente peggiore.
3. Una macchina classificata `Standing.GROUND` può partecipare a un candidato verticale
   quando la quota non è un vincolo fisico del modello.
4. Una sequenza principale con uno stacco conserva la dorsale rettilinea e colloca la T
   sull'asse, invece di piegare l'intera sequenza per il ramo.
5. Una T con due imbocchi ortogonali assorbe un gomito e batte la variante T più gomito;
   il grafo e gli identificativi delle connessioni restano identici.
6. Se la T ortogonale peggiora la tavola completa, resta la configurazione corrente.
7. Ridenominare tutti gli ID non cambia la geometria; due generazioni sono identiche.
8. Aggiungere, cambiare o togliere testi non modifica nessun candidato, simbolo o tubo.

## Criteri di accettazione sulla tavola 1

Baseline DRAW-003-R1: backtracking `0`, tratte oltre tre pieghe `0`, curve `10`,
incroci `2`, lunghezza `597,5 mm`, valvole D-120 `20/20`.

La consegna deve rispettare tutti i punti seguenti:

1. nessuna regressione di correttezza, backtracking, tratte lunghe o valvole;
2. incroci non oltre `2` e lunghezza non oltre `597,5 mm`;
3. curve totali non oltre `8`;
4. nessun dogleg evitabile fra le PDC e la dorsale primaria: il rapporto deve mostrare
   quali alternative di asse sono state provate e perché quella finale ha vinto;
5. almeno un caso generale dimostra la T che assorbe una curva; sulla tavola 1 la si usa
   soltanto se il costo completo migliora;
6. linea di terra assente; tavola definitiva con sole sigle principali; modalità
   verifica best-effort e mai influente sulla geometria;
7. suite completa, `ruff`, `mypy --strict` e determinismo verdi;
8. PDF, PNG, SVG, geometria, metriche e confronto prima/dopo in
   `docs/collaudi/DRAW-004/`.

Il limite di 8 curve è il target misurabile di questo ciclo, non un invito a comprare il
numero con più incroci o più tubo: i limiti 1 e 2 restano simultaneamente vincolanti.

## Perimetro

Consentiti:

- `src/disegnatore_mep/layout/improve.py`;
- `src/disegnatore_mep/layout/place.py` e i moduli di posa/routing strettamente necessari
  per rappresentare la coppia di attacchi usata dalla T;
- test generali di layout, costo e routing;
- `docs/collaudi/DRAW-004/**`, `PROJECT_STATE.md`, `docs/input-pm/REGISTRO.md`.

Vietati: modifica del grafo dell'impianto 1, coordinate speciali, eccezioni per ID,
ottimizzazione delle etichette, lavoro sugli impianti 2-5, simboli e cartiglio.

## Consegna

Il DEV salva progressivamente sul ramo remoto, apre una sola PR verso `main` e si ferma.
Il PM verifica codice, metriche e tavola; il merge spetta al PM.
