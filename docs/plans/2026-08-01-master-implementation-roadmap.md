# Disegnatore MEP - Master Implementation Roadmap

> **For agentic workers:** ogni piano figlio deve essere eseguito con `superpowers:subagent-driven-development` oppure `superpowers:executing-plans`, mantenendo un gate di revisione fra i task.

**Goal:** trasformare la specifica approvata in una serie di sottoprogetti indipendenti, ciascuno funzionante, verificabile e utile al successivo.

**Architecture:** il programma parte dal modello canonico e dai contratti dei domini, poi costruisce in parallelo conoscenza tecnica e libreria grafica. Regole, layout, rendering e orchestrazione si appoggiano a contratti già collaudati. La qualificazione finale verifica combinazioni miste e produce la release installabile.

**Tech Stack:** Python 3.12 di riferimento, Pydantic, SVG, PDF vettoriale, pytest, Ruff, mypy, Git locale.

## Vincoli globali

- Nessun piano può introdurre schemi tipo codificati rigidamente.
- Nessun modulo effettua dimensionamenti o seleziona apparecchiature principali.
- Il modello tecnico canonico resta la fonte di verità.
- Ogni sottoprogetto deve avere test positivi, negativi e di composizione.
- Dimensioni, testi e spessori sono espressi in millimetri di carta.
- `releases/latest/` viene aggiornata soltanto dal piano di rilascio dopo tutti i gate.
- Planimetrie ed elettrico completo restano nella roadmap futura e non entrano nei piani attuali.

---

## Sequenza dei piani

### P0 - Fondazione canonica

**Piano:** `docs/plans/2026-08-01-foundation-core-plan.md`

**Consegna:** pacchetto Python installabile con modello canonico, catalogo dei componenti, contratti dei domini, validatore topologico, serializzazione riproducibile e CLI di validazione.

**Gate:** un progetto misto idronico-aeraulico-refrigerante-gas viene caricato e validato senza codice speciale per lo schema.

### P1 - Ricerca tecnica e sistema delle regole

**Consegna:** registro fonti operativo, schema versionato delle regole, motore di attivazione, classificazione necessaria/raccomandata/condizionata e report delle integrazioni.

**Gate:** le stesse regole producono risultati motivati su varianti topologiche e non modificano il modello senza approvazione.

### P2 - Sistema grafico A3 e compilatore dei simboli

**Consegna:** standard grafico in millimetri, formato dei manifesti SVG, compilazione dei compositi, controlli di porte/ingombri/orientamenti e prima libreria trasversale.

**Gate:** ogni simbolo supera controlli metrici e di stampa; i compositi sono contati come un unico prodotto.

### P3 - Pacchetti di dominio

Il piano P3 viene separato in quattro piani coordinati che condividono i contratti di P0-P2:

- P3A idronica;
- P3B aeraulica;
- P3C espansione diretta e VRV;
- P3D gas, condensa e reti ausiliarie.

**Consegna comune:** vocabolario, componenti frequenti, compatibilità, regole e casi di prova di ciascun dominio.

**Gate:** ogni pacchetto funziona da solo e in almeno due combinazioni con gli altri pacchetti.

### P4 - Layout, instradamento e multi-tavola

**Consegna:** partizione funzionale, layout vincolato, routing ortogonale, inserimento topologico degli accessori, label placement e rimandi accoppiati.

**Gate:** nessuna linea passa sotto un componente in linea; il motore mantiene la scala e suddivide semanticamente quando l'A3 non basta.

### P5 - Renderer, cartiglio e PDF

**Consegna:** SVG metrico, cartiglio Nove C compilabile, PDF vettoriale, distinta quantitativa, **preflight grafico** (D-063) e manifest di riproducibilità.

Il preflight grafico misura la qualità del disegno, non la sua validità: pieghe per tratta, attraversamenti, sovrapposizioni longitudinali, distanze di rispetto, area occupata. Le soglie oggi vivono in `tests/layout/test_objective.py` su una sola fixture e vanno promosse a validatore di prodotto.

**Gate:** un A3 stampato mantiene le dimensioni previste; una finale incompleta viene bloccata; il preflight grafico non ha esiti bloccanti; il PDF supera controllo visivo rasterizzato.

### P6 - Orchestrazione della skill

**Consegna:** skill installabile che legge il contesto disponibile, costruisce la proposta, presenta il dossier unico, registra l'approvazione, invoca la pipeline e **verifica prima di consegnare** — cold eye review con agente terzo e ciclo di revisione (D-063, D-064).

Il ciclo cambia il piano di impaginazione e rigenera; non tocca mai la geometria prodotta. È limitato nel numero di passate e monotono sulle misure del preflight.

**Gate:** il flusso conversazione -> dossier -> approvazione -> elaborato -> verifica funziona senza richiedere una nuova compilazione manuale dell'impianto; un elaborato respinto dal cold eye review viene rigenerato con un piano diverso e la rigenerazione resta deterministica.

### P7 - Qualificazione trasversale e release

**Consegna:** matrice di regressione, prove di stampa, installazione pulita, pacchetto `latest/`, ZIP versionato e inventario delle coperture.

**Gate:** test completi, revisione tecnica dell'ingegnere, installazione pulita e confronto riproducibile fra manifest e commit.

## Dipendenze

```text
P0 -> P1
P0 -> P2
P0 + P1 + P2 -> P3A/P3B/P3C/P3D
P0 + P2 -> P4
P2 + P4 -> P5
P1 + P3 + P5 -> P6
P3 + P4 + P5 + P6 -> P7
```

P1 e P2 possono procedere in parallelo dopo P0. I quattro piani P3 possono procedere in parallelo dopo la stabilizzazione dei contratti condivisi.

## Gate di programma

- **G0:** fondazione valida un progetto misto.
- **G1:** fonti, regole e simboli hanno versione e tracciabilità.
- **G2:** almeno quattro domini sono componibili senza eccezioni nel nucleo.
- **G3:** layout e PDF superano controlli metrici e visivi.
- **G4:** skill utilizzabile end-to-end nella conversazione.
- **G5:** release installabile, riproducibile e approvata.
