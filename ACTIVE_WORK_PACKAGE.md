# ACTIVE WORK PACKAGE — DRAW-008

**Titolo:** La posa a fasi — prima le autostrade
**Assegnato da:** PM-autore (Claude, in sessione col PO — `OPERATING_MODEL.md` §1.2.1)
**Assegnato a:** DEV
**Data:** 2026-09-11
**Stato:** APPROVATO DAL PO — architettura confermata in sessione l'11 settembre 2026
**Release:** 0.3 — generalizzazione, revisione della tavola 2
**Ramo:** `claude/draw-008-posa-a-fasi`
**Commit di partenza:** la testa di `main` (DRAW-007 è fuso)
**Fixture grafica principale:** impianto 2; impianto 1 come regressione automatica

> **Leggere prima, e per intero:** `docs/pm/2026-09-11-architettura-della-posa-a-fasi.md`.
> Questo pacchetto ne è l'attuazione e non lo ripete.

---

## Contesto

DRAW-007 ha dato alla tavola una **gerarchia** — autostrada, distribuzione, servizio — e
l'ha messa nel costo. Non è bastato, e il perché è architetturale: il ciclo è un greedy
globale, quindi ogni proprietà del disegno è una voce di costo che si compra e si vende.
In poche ore la stessa serie di modifiche ha reso buona la tavola 1 e ha fatto smettere di
uscire la tavola 2.

Il PO ha dato l'ordine delle decisioni: **prima le autostrade, dritte; poi il corredo, e
se non ci sta si allunga il tronco invece di piegarlo; poi le strade di servizio, dove
qualche curva si accetta.** La funzione di costo resta e ottimizza dentro ciascuna fase.

**Stato di partenza, dichiarato:** sulla testa di `main` la **tavola 2 non esce** — il
preflight trova un rilievo bloccante (`RUN_OVERSHOOTS_ITS_PORT`) e una tavola con un
bloccante non si scrive (D-063). La tavola 1 esce ed è la migliore mai prodotta: rete
ordinaria 6 pieghe, 3 incroci, 550,0 mm; zero pieghe su tutte e otto le tratte di
autostrada; accumulo e PDC-master con quattro porte sullo stesso asse. Nove prove di
geometria sono rosse. **Non è un difetto da nascondere: è il punto di partenza.**

## A. La fase del tronco

1. Si posano le sole **macchine di spina** (`layout/hierarchy.spine_machines`) e si
   instrada la sola **autostrada** (`layout/hierarchy.Level.AUTOSTRADA`).
2. L'obiettivo della fase è una **forma**, non un costo: ogni tratta del tronco è un
   rettilineo. Dove il tronco si biforca, uno dei due rami resta sull'asse principale e
   l'altro se ne stacca; resta sull'asse il ramo verso l'accumulo maggiore.
3. Spostare una macchina costa zero: la fase ha tutta la libertà che le serve.
4. Al termine la rettilineità del tronco diventa un **vincolo duro**. Va dove stanno «i
   vincoli che nessun guadagno compra» (`Improver.is_valid`), non fra le voci di
   `SheetCost`.

## B. La fase del corredo

1. Valvole, filtri, raccordi e accessori in linea entrano **dentro** il tronco già posato.
2. Dove non ci stanno, il tronco **si allunga**: due macchine di spina si allontanano
   lungo l'asse e ciò che sta in mezzo le segue. È una **mossa nuova** — oggi il ciclo
   muove pezzi, non allunga tratte — e costa zero, come ogni spostamento di macchina.
3. Piegare il tronco per far posto a un organo è **vietato**, non caro.

## C. La fase delle strade di servizio

1. Stacchi, diramazioni, adduzioni e accessori appesi si attaccano a un tronco **fermo**.
2. Qui le curve si pagano, con i pesi di gerarchia già scritti, e si accettano.
3. Una strada di servizio non piega mai un'autostrada per accorciarsi.

## D. Il costo, che resta

1. `SheetCost` e i pesi di `hierarchy.weight_of` **non si toccano** salvo che una prova
   dimostri il contrario: ottimizzano dentro ciascuna fase.
2. L'ordine lessicografico resta quello che è.

## Perimetro dei file — modifiche consentite esclusivamente a

- `src/disegnatore_mep/layout/**`
- `tests/**`
- `docs/collaudi/DRAW-008/**`
- `PROJECT_STATE.md`

## Fuori perimetro — da non toccare

- **catalogo, regole, simboli, `naming/`**: questo pacchetto non cambia il contenuto del
  grafo;
- **I-061**, gli ingressi ripetuti dell'AF: è il pacchetto successivo, e va fatto **dopo**
  perché cambia cosa c'è da instradare, non come lo si instrada;
- **I-059**, lo spessore del tratto per gerarchia;
- riempimento estetico del foglio, cartiglio, audit dei simboli;
- gli impianti 3–5 oltre la prova di posa;
- decisioni esistenti, registro degli input del PO, documenti di governance.

## Vincoli

- Nessun merge su `main`: **il merge è del PO** (`OPERATING_MODEL.md` §1.2.1).
- Nessuna decisione esistente rinumerata, riscritta o cambiata di stato.
- Nessun input del PO chiuso: al massimo se ne propone la chiusura.
- Un pacchetto, un ramo, una PR (D-123).

## Criteri di accettazione

Ogni criterio si chiude con **il comando eseguito e il suo output**, mai con la parola
«verificato». Un criterio che nomina un risultato osservabile si prova sul risultato
osservabile.

- [ ] **1. La fase del tronco esiste ed è separata.** Una prova generale mostra che la
      posa del tronco produce una geometria delle sole macchine di spina e delle sole
      tratte di autostrada, e che il resto dell'impianto non vi partecipa.
- [ ] **2. Il tronco è dritto.** Su impianti costruiti dentro la prova, e sulle due tavole:
      **zero pieghe** su ogni tratta di livello autostrada.
- [ ] **3. La rettilineità è un vincolo, non un costo.** Prova negativa: una mossa che
      piegherebbe il tronco guadagnando sul costo totale viene **rifiutata**, e la stessa
      prova fallisce se il vincolo è spostato fra le voci di `SheetCost`.
- [ ] **4. Il tronco si allunga invece di piegarsi.** Prova generale: un corredo che non
      entra nella campata disponibile produce uno **stretch** — due macchine di spina più
      lontane, tronco ancora dritto — e non una piega.
- [ ] **5. Le strade di servizio non piegano il tronco.** Prova generale su un impianto in
      cui una diramazione accorcerebbe piegando un'autostrada: non lo fa.
- [ ] **6. La tavola 2 esce**, senza rilievi bloccanti nel preflight.
- [ ] **7. La tavola 2 rispetta il §4 dell'architettura**: le porte della macchina
      principale e dell'accumulo maggiore sono sullo stesso asse, e nessuna tratta di rango
      inferiore attraversa un'autostrada.
- [ ] **8. La tavola 1 non peggiora** rispetto alla testa di `main`: rete ordinaria non
      oltre 6 pieghe / 3 incroci / 550,0 mm, zero pieghe di autostrada, macchine allineate.
- [ ] **9. La suite è verde.** Nessuna prova convertita in `skip` o `xfail`. Le nove rosse
      di partenza elencate una per una nel rapporto con l'esito.
- [ ] **10. `ruff`, `mypy --strict` e doppia generazione deterministica** verdi, con
      l'impronta della geometria riportata.
- [ ] **11. Tutti e cinque gli impianti arrivano alla posa**, e nessun artefatto grafico è
      prodotto oltre quello della tavola 2.
- [ ] **12. Nessun file fuori dal perimetro risulta modificato nel diff.**

## Consegna attesa

- Una sola PR, **non fusa**.
- Rapporto in `docs/collaudi/DRAW-008/RAPPORTO.md`: ramo, SHA iniziale, SHA finale, file
  modificati, criteri uno per uno **col comando e l'output**, misure prima/dopo, difetti
  noti, punti aperti.
- Pacchetto grafico della **sola tavola 2**: PDF, PNG, SVG, geometria, metriche, preflight
  e confronto con la testa di `main`.

## In caso di ambiguità o di criterio irraggiungibile

Fermarsi e riportarlo, **prima** di cambiare la prova. Un'incompatibilità si porta al PM;
la manutenzione ordinaria di una prova, no — quella la fa il DEV.
