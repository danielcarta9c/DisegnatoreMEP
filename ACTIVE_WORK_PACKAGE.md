# REL-010 — Il revisore esterno, e il metro con cui guarda

> **▶ Il pacchetto attivo, dal brief del PO** — *Brief_disegnatore-mep_revisore_rev01* (I-216): il passo 7 «Rivedere»
> delegabile, quando serve, a un sub-agente che non ha composto la tavola; versione **1.5.0**. E la sua
> preoccupazione: «l'agente esterno forse non ha un benchmark per capire se una tavola è disegnata bene o meno. questa
> è la parte che mi preoccupa di piu'». Scritto il 23 ottobre 2026, sulla 1.4.1.

**Da svolgere:** l'agente unico (**D-147**), con agenti paralleli in sessione (**D-152**)
**Stato:** **IN CORSO** — il punto 1 è sul ramo `claude/nifty-archimedes-4hnzcu`, con la tavola al PO (D-211 proposta).
**Base:** `main` dopo la PR #77 (la 1.4.1).
**Ramo:** quello che l'ambiente della sessione assegna.
**Approvazione della fusione:** **del PO**, guardando le tavole (D-146, D-147). Una PR per punto, o per gruppo di punti.

---

## Perché

Oggi la tavola la guarda lo stesso agente che ha scritto il piano, e tende a vedere la posa che aveva in mente. Il
brief vuole un revisore separato **solo quando serve**. Torna con l'architettura: l'occhio era nato separato (D-162,
`docs/ARCHITETTURA-DEL-PIANO.md` §3), e la prova in camera pulita del 20 settembre (`skill/rivedere/prova-2026-09-20/`)
l'ha fatto così — tavola, rilievi, istruzioni, tavole di riferimento; niente piano.

Il PO ha messo il dito sul punto debole: **un revisore senza metro dà il giudizio di un modello generalista**. Il metro
si costruisce in tre pezzi, ed è questo l'ordine del pacchetto: la **rilettura a freddo** contro il grafo, gli
**esempi** fatti dal PO o approvati da lui, la **taratura** del revisore sul giudizio del PO — prima di scrivere il
passo 7.

## Le cose da fare, in quest'ordine

### 1. La tavola d'esempio — fatto sul ramo, aspetta il PO (I-217, D-211)

La tavola C (`REL-009`, «tavola perfetta», I-214), guardata ingrandita, aveva due difetti che nessun numero vedeva: la
serpentina del pannello radiante fuori dal riquadro, e il giunto antivibrante dell'ultima pompa di ogni cascata sulla
verticale del collettore. Corretti (il simbolo, e una regola del motore); la tavola corretta è al PO, che decide se è
l'esempio. `docs/collaudi/REL-010/RAPPORTO.md` §1.

### 2. Gli esempi del revisore — da decidere col PO

- **Il buono**: la tavola C corretta, se il PO la approva. Per le tavole piccole, gli schemi tipologici A, B, C della
  *Specifica tecnica di installazione* Nove C, che sono fatti con questa skill (RAPPORTO §2) — se il PO li vuole nella
  skill.
- **Le coppie peggio / meglio**, con i simboli di oggi: la tavola del caso rifatta (`caso-reale-2`, I-207, collettore di
  ritorno lontano) e la C, sullo stesso impianto. Le tavole 4 e 5 di settembre **no** come immagini: foto del telefono e
  segni su un motore vecchio; il loro criterio è già scritto (B12, D-159).
- **Niente immagini dal web nella skill**: sono di terzi, il repository è pubblico, e hanno altre convenzioni (D-165).
- Dove stanno nella skill e quanti: lo ZIP ha 104 file su 200 (D-200); ogni immagine costa contesto. Si tengono quelli che
  la taratura (punto 3) dice utili.

### 3. La taratura del revisore — prima di toccare `SKILL.md`

Un agente avviato da zero riceve alla cieca tavole che il PO ha già giudicato e si guarda: **trova quello che il PO ha
cerchiato? lascia passare quello che ha approvato?** La seconda conta quanto la prima: un revisore che trova sempre
qualcosa non fa scattare la regola d'arresto. Le tavole della taratura non sono quelle date come esempio (altrimenti
riconosce invece di giudicare). Si misura con e senza gli esempi del punto 2. **Se non vede quello che vede il PO, il
revisore esterno non si costruisce**, e lo si dice.

### 4. La rilettura a freddo — in `rivedere.md`

Prima di giudicare, il revisore racconta l'impianto leggendolo dalla sola tavola: i generatori, dove va l'acqua, quale
circuito serve quale utenza, mandata e ritorno di ciascuno. Chi lo ha lanciato confronta il racconto con il grafo: dove
non torna, è un difetto di leggibilità — il metro è il grafo, che il revisore non vede. Racconta, non misura (D-162).

### 5. Il passo 7 in due modalità — il brief, con le correzioni della sessione

- **`rivedere.md` §2 va toccato**: elenca il piano, che il revisore separato non riceve, e le tavole di riferimento, che
  nella skill non ci sono; «il PO» per il sub-agente è il progettista. E deve dire dei pozzetti delle sonde e delle
  altre convenzioni che un lettore a freddo scambia per difetti.
- **I nomi**: sulla tavola ci sono solo le sigle delle macchine; il revisore nomina il resto descrivendolo, e la
  traduzione negli identificativi la fa chi compone.
- **`passa-per` non si applica** (D-161, il piano non ha il campo): un vincolo che non si può applicare cede, e lo si dice.
- **Il tetto ai giri** (architettura §5, regola 3): proposta 2 leggeri + 2 col revisore. Il secondo criterio d'attivazione
  del brief cambia la regola d'arresto di oggi: va scritto.
- **L'indipendenza nei fatti**: il testo dell'incarico è fisso, in `SKILL.md`; il revisore sceglie lui gli ingrandimenti
  (gli si dà il comando `anteprima` e una cartella con il solo PDF e i rilievi); gira con lo stesso modello di chi compone.
- I criteri d'attivazione del brief; «più generatori e più collettori» vale per quasi ogni centrale: proposta di
  toglierlo e tenere «A2 o più».
- Dove i sub-agenti non ci sono, la modalità leggera, detta nella consegna. Nella consegna una riga: chi ha guardato la
  tavola.

### 6. La prova del brief — sulla stessa tavola, in sessione pulita

Il passo 7 nelle due modalità **partendo dalla stessa tavola** (D-023 è sospesa: due composizioni non danno la stessa
tavola), in una sessione nuova con il solo ZIP, sul `caso-reale-2`. Il metro non è «un vincolo in più»: è **il giro dopo
migliora** (`skill/rivedere/CONSEGNA.md` punto 4) e **il PO lo vede sulle tavole**. Con il tempo di ciascuna (I-205).

### 7. La release 1.5.0

Con `scripts/costruisci-skill.py`, e `tests/test_le_release.py` verde (D-200). La nota di `SKILL.md` al passo 1 su
`capire.md` resta com'è.

## Da decidere col PO — non da scegliere da soli

- quali esempi entrano nella skill (punto 2), e se la tavola C corretta è l'esempio (D-211);
- **il manuale Shenling** (RAPPORTO §2, ricontrollato): la macchina ha **a bordo** valvola di sicurezza a 3 bar, sfiato
  automatico, flussostato e pompa; non il vaso; vuole almeno 40 l d'impianto a valvole chiuse, e in cascata una valvola
  di non ritorno sull'uscita di ogni unità. La tavola del caso disegna fuori da ogni macchina la valvola di sicurezza
  (D-182 la vuole sempre) e lo sfiato. Si tengono così, o la Shenling li porta `a_bordo`? È D-015: il manuale cambia gli
  accessori rappresentati;
- **la §2.4 della specifica tecnica** contro le regole di Completare: il corredo del primario che il progettista vuole;
- da `REL-009`, punto 9: la distanza della valvola di sicurezza sopra il suo raccordo; B3 contro B1 nell'ordine dei
  collettori primari; la quota del primo raccordo della zona vicina; da dove arriva la fredda del bollitore. E il
  **limite d'intervento** facoltativo (I-195, D-202).

## Perimetro

**Dentro:** `skill/**`, `src/**`, la libreria (`examples/graphics/build_symbols.py` → `assets/symbols/`), `tests/**`,
`docs/collaudi/REL-010/`, `releases/`, il registro, il registro delle decisioni (come proposte), `HANDOFF.md`, questo file.

**Fuori:** i dati del cliente, in qualunque file; i manuali dei costruttori, la specifica tecnica Nove C e le immagini
di terzi (il repository è pubblico); un contenuto MEP o una convenzione grafica decisi dalla sessione.

## Criteri di accettazione — per ogni PR

Ogni criterio si chiude con **il comando eseguito e il suo output**.

0. **Le tavole, per prime**: quelle che la PR cambia, prima e dopo, al PO.
1. **La suite**: `0 failed`; nessuno `skip` e nessuno `xfail` nuovi; `ruff check src tests` verde; `mypy` verde dove
   l'ambiente lo lascia girare (sul `main` del 23 ottobre si ferma sugli stub di numpy).
2. **La regressione**: il banco di `REL-009` (`docs/collaudi/REL-009/la-1.4-sulle-tavole-agli-atti/banco.py`, più le
   tre prove pulite) fra `main` e il ramo, ogni tavola cambiata spiegata.
3. **Ogni correzione ha la sua prova**, rossa sul commit di partenza.
4. **Gli input del PO nel registro** il giorno in cui arrivano.
5. **Nessun dato di cliente nel diff**: il comando di ricerca e il suo output vuoto.
6. **La release**: `tests/test_le_release.py` verde — la skill si carica (D-200).
