# ADR 0005 — I pezzi della skill e il confine fra AI e deterministico

**Data:** 5 agosto 2026
**Stato:** approvata dal PM
**Sostituisce:** nulla. **Precisa:** ADR 0001, ADR 0002.

## Contesto

Il progetto ha lavorato per mesi senza un documento che dicesse **di quali pezzi è fatta
la skill**. L'ha dovuto elencare il PM a voce. In assenza di quella mappa lo sviluppo ha
ottimizzato la singola tavola di prova invece di costruire i pezzi (D-092), ha scritto
regole particolari invece che generali (D-090), e ha verificato contando invece che
guardando (D-088).

## Decisione

**La skill è fatta di sette pezzi, in quest'ordine**, e la loro composizione tecnica non è
negoziabile:

| # | Pezzo | Di cosa è fatto |
|---|---|---|
| 1 | **Capire** — dalla conversazione al modello dell'impianto | **Agente AI** |
| 2 | **Completare** — quali accessori mancano e perché | **Programma**, con le regole come **dati** |
| 3 | **Assemblare** — la fila ordinata dei pezzi lungo ogni tubo | **Programma** |
| 4 | **Disporre** — posizionare, instradare, distribuire | **Programma** |
| 5 | **Libreria dei simboli** | **Dati** |
| 6 | **Cartiglio** | **Dati**, forniti dall'azienda |
| 7 | **Verificare** — controlli e misure / occhio terzo | **Programma** / **Agente AI** |

**Il confine, che è la parte strutturale della decisione:**

    AI          →  sceglie GLI INGRESSI      (pezzo 1)
    PROGRAMMA   →  produce L'ELABORATO       (pezzi 2, 3, 4, 5, 6)
    AI          →  giudica IL RISULTATO      (pezzo 7b)

**Nessuna AI disegna, nessuna AI corregge il disegno, nessuna AI decide un ordine.**
Quando l'occhio terzo respinge, cambia **gli ingressi** e il programma rigenera da capo.

## Conseguenze

- **Stesso impianto, stessa tavola, sempre.** È la proprietà che il prodotto non può
  perdere, e da cui discende tutto il resto: se un'AI potesse spostare una linea o
  scegliere un ordine, due esecuzioni identiche darebbero due risultati diversi e
  un'approvazione non varrebbe più niente.
- **Le regole e i simboli sono dati, non codice.** Si aggiunge una regola aggiungendo un
  file. Se per aggiungere una famiglia di accessori servisse modificare il motore, il
  motore sarebbe sbagliato.
- **Un contraddittorio si dichiara, non si risolve in silenzio.** Dove due regole non
  possono stare insieme, il programma si ferma e le nomina. Un'AI al suo posto sceglierebbe
  da sola, ogni volta in modo diverso.
- **La scrittura delle regole è attività separata**, fatta prima e fuori dalla catena: si
  autora con l'aiuto dell'intelligenza, si fa approvare al PM, e da quel momento è dato.
- Ogni pezzo si costruisce e si collauda **da solo**, con un contratto proprio e criteri di
  accettazione espressi come **proprietà valide su qualunque impianto**, mai come numeri
  di una tavola di prova.

Il dettaglio operativo di ciascun pezzo vive in `docs/SKILL.md`, che da oggi è il
documento autorevole sull'architettura del prodotto.
