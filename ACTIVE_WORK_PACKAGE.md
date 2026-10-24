# REL-010 — Il revisore esterno, e il metro con cui guarda

> **▶ Il pacchetto attivo, dal brief del PO** — *Brief_disegnatore-mep_revisore_rev01* (I-216): il passo 7 «Rivedere»
> delegabile, quando serve, a un sub-agente che non ha composto la tavola; versione **1.5.0**. E la sua
> preoccupazione: «l'agente esterno forse non ha un benchmark per capire se una tavola è disegnata bene o meno. questa
> è la parte che mi preoccupa di piu'». Scritto il 23 ottobre 2026, sulla 1.4.1.

**Da svolgere:** l'agente unico (**D-147**), con agenti paralleli in sessione (**D-152**)
**Stato:** **IN CORSO** — il punto 1 è su `main` (PR #78): la tavola C corretta, approvata dal PO, è l'esempio (I-218, D-211).
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

### 1. La tavola d'esempio — fatto, PR #78 (I-217, I-218, D-211)

La tavola C (`REL-009`, «tavola perfetta», I-214), guardata ingrandita, aveva due difetti che nessun numero vedeva: la
serpentina del pannello radiante fuori dal riquadro, e il giunto antivibrante dell'ultima pompa di ogni cascata sulla
verticale del collettore. Corretti (il simbolo, e una regola del motore); il PO: «la tavola C vabene» — è l'esempio. `docs/collaudi/REL-010/RAPPORTO.md` §1.

### 2. Gli esempi del revisore — da decidere col PO

- **Il buono**: la tavola C corretta (`docs/collaudi/REL-010/tavola-esempio/`), approvata (I-218). Per le tavole piccole, gli schemi tipologici A, B, C della
  *Specifica tecnica di installazione* Nove C, che sono fatti con questa skill (RAPPORTO §2) — se il PO li vuole nella
  skill.
- **Le coppie peggio / meglio**, con i simboli di oggi: la tavola del caso rifatta (`caso-reale-2`, I-207, collettore di
  ritorno lontano) e la C, sullo stesso impianto. Le tavole 4 e 5 di settembre **no** come immagini: foto del telefono e
  segni su un motore vecchio; il loro criterio è già scritto (B12, D-159).
- **Niente immagini dal web nella skill**: sono di terzi, il repository è pubblico, e hanno altre convenzioni (D-165).
- Dove stanno nella skill e quanti: lo ZIP ha 104 file su 200 (D-200); ogni immagine costa contesto. Si tengono quelli che
  la taratura (punto 3) dice utili.

### 3. La taratura del revisore — fatta, due giri (I-220, I-221)

Un agente avviato da zero riceve alla cieca tavole che il PO ha già giudicato e si guarda: **trova quello che il PO ha
cerchiato? lascia passare quello che ha approvato?** La seconda conta quanto la prima: un revisore che trova sempre
qualcosa non fa scattare la regola d'arresto. Le tavole della taratura non sono quelle date come esempio (altrimenti
riconosce invece di giudicare). Si misura con e senza gli esempi del punto 2. **Se non vede quello che vede il PO, il
revisore esterno non si costruisce**, e lo si dice.

**Primo giro fatto** (RAPPORTO §3, I-220): sette tavole già giudicate, sette revisori alla cieca. Il PO, vista ogni
tavola accanto al verdetto, lo dà **giusto sette volte su sette**, anche sulle quattro che aveva approvato: il revisore ha
visto difetti che il PO non aveva visto. Il revisore separato si costruisce. Quello che manca lo dice il PO punto per
punto (`docs/collaudi/REL-010/taratura-1/GIUDIZI-PO.md`):

- **la soglia**: le cose che il PO tollera — l'ordine delle due colonne di una cascata quando invertirle sposta solo gli
  scavalcamenti, la mandata di una zona sotto il ritorno comune, il bollitore fuori dalla sua fascia, un circuito lungo
  che si può accorciare, i pozzetti delle sonde senza tappo, derivazione e raccordo a T con lo stesso segno, l'ordine
  delle macchine nella pila, il cartiglio «DA DEFINIRE» — si dicono come miglioramenti, e non fermano la consegna;
- **guardare dentro i simboli**: la serpentina del pannello fuori dal riquadro «doveva vederla» (il PO, t1).

**Secondo giro fatto** (RAPPORTO §4, I-221), con la soglia e il settimo sguardo in `rivedere.md`, su **sei tavole
diverse** dalle sette — perché non le riconosca —, giudicate dal PO a settembre. Il PO dà il verdetto **giusto sei volte
su sei**, anche sulle due tavole del 23 settembre che aveva approvato e che il revisore respinge: **tredici su tredici**
nei due giri. Il revisore manca un solo difetto del PO, gli stacchi lunghi di DRAW-005-R1. Le scelte del PO sono entrate
nella soglia di `rivedere.md`, con la sfumatura che mancava: **un difetto da correggere non ferma per forza la consegna**.
Tutti e due i giri sono **senza gli esempi** del punto 2: il verdetto è giusto anche senza. Se entrano nella skill resta
da decidere col PO. **Il punto 3 è chiuso.**

### 4. La rilettura a freddo — scritta in `rivedere.md` (D-212), da provare al punto 6

Prima di giudicare, il revisore racconta l'impianto leggendolo dalla sola tavola: i generatori, dove va l'acqua, quale
circuito serve quale utenza, mandata e ritorno di ciascuno. Chi lo ha lanciato confronta il racconto con il grafo: dove
non torna, è un difetto di leggibilità — il metro è il grafo, che il revisore non vede. Racconta, non misura (D-162).

### 5. Il passo 7 in due modalità — scritto in `SKILL.md` (D-212, proposta), da provare al punto 6

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
- **Quando si attiva: solo se il progettista lo sceglie** (I-219), e la skill glielo chiede con una domanda a scelta al
  passo 2, solo dove i sub-agenti ci sono, senza un «io» ambiguo (I-222). I criteri
  automatici del brief — A2 o più, due giri leggeri senza miglioramento, tavola definitiva — cadono; tempo e token non
  sono un vincolo. Il giro ordinario resta la modalità leggera.
- Dove i sub-agenti non ci sono, la modalità leggera, detta nella consegna. Nella consegna una riga: chi ha guardato la
  tavola.

Fatto il 24 ottobre: il passo 7 ha le due modalità, il revisore esterno si attiva solo su richiesta, l'incarico è fisso
in `SKILL.md` con la cartella da preparare, il tetto è di due giri con un revisore nuovo per giro, la consegna dice chi
ha guardato; `rivedere.md` ha il §2 corretto e dice chi è «il PO». La skill si costruisce (104 file) e
`tests/test_le_release.py` passa.

### 6. La prova del brief — sulla stessa tavola, in sessione pulita

Il passo 7 nelle due modalità **partendo dalla stessa tavola** (D-023 è sospesa: due composizioni non danno la stessa
tavola), in una sessione nuova con il solo ZIP, sul `caso-reale-2`. Il metro non è «un vincolo in più»: è **il giro dopo
migliora** (`skill/rivedere/CONSEGNA.md` punto 4) e **il PO lo vede sulle tavole**. Con il tempo di ciascuna (I-205).

### 7. La release 1.5.0

Con `scripts/costruisci-skill.py`, e `tests/test_le_release.py` verde (D-200). La nota di `SKILL.md` al passo 1 su
`capire.md` resta com'è.

## Quello che la taratura ha riportato sul prodotto — dopo il revisore

Il PO li ha chiamati **difetti** (I-220, I-221). Non sono del revisore: sono della composizione, del motore o dei controlli, e
vanno nel pacchetto che segue `REL-010` («una cosa alla volta», I-218).

| difetto | dove si vede | di chi è |
|---|---|---|
| andata ACS, ricircolo e acqua fredda arrivano al bollitore da tre parti | t1, t3 | Comporre |
| i due collettori di una cascata lontani fra loro | t2 (il piano scritto dallo sviluppo) | Comporre (B3, B12); la tavola del caso va ricomposta |
| le pompe in parallelo non incolonnate | t2, t7 | il controllo di A2 che manca (D-158) |
| l'acqua fredda che entra nel bollitore con un gradino | t3 | Comporre |
| la coppia che si apre quando i capi sono raccordi (radiante, serpentina) | t5, t6 | il controllo di B11/B12 (D-174 non riconosce la coppia) |
| il gruppo di sicurezza sanitario lontano dal bollitore | t6 | il controllo di A4 misura solo gli stacchi |
| il disegno che tocca il bordo | t6 | il rilievo c'è (`DRAWING_TOUCHES_THE_BORDER`): Comporre |
| lo scarico in fondo al volano, rosso con la freccia | t1, t5, t7; tutte e sei del secondo giro | il motore: come si disegna è una convenzione, la decide il PO |
| due tratti in fila sulla stessa verticale che si leggono come un tubo solo (lo scarico del volano sopra la colonna ACS) | u1 | Comporre; B9 guarda solo i tratti affiancati |
| CIR-03 non incolonnato, con la miscelatrice del pannello sulla colonna del pettine | u5 | Comporre; il controllo di A2 che manca (D-158) |
| un gradino sulla mandata ACS prima del confine, con la corsia libera | u5 | Comporre (B1) |
| la coppia verso uno scambiatore che si apre nelle verticali | u3 | il controllo di B11/B12, come sopra |
| la sigla di una macchina lontana dalla macchina, sotto un altro pezzo («se possibile spostare le tag») | u1, u3 | il motore: nessuna regola dice dove sta una sigla |
| deviatrice e commutatrice con lo stesso segno | u3 | la libreria; **il segno lo sceglie il PO**: una «c» sopra o un simbolo leggermente diverso (I-221) |

E tre cose che il PO tollera ma preferirebbe altrimenti (I-221): il tratteggio dell'acqua fredda che parte pieno
sull'attacco, le valvole di mandata e ritorno di una macchina allineate, e gli attacchi dei terminali che oggi corrono a
filo degli spigoli del riquadro (radiatore, pannello, ventilconvettore, ventilconvettore canalizzato) — quest'ultimo
tollerato senza preferenza.

E una domanda di contenuto: «ho anche un dubbio sul vaso di espansione» (il PO, sul caso rifatto), che va con il
manuale Shenling e le regole del vaso (I-218).

## Da decidere col PO — non da scegliere da soli

- quali altri esempi entrano nella skill (punto 2): gli schemi A, B, C della specifica tecnica;
- **dopo il revisore, per ordine del PO** (I-218): **il manuale Shenling e la §2.4 della specifica tecnica contro le
  regole** di Completare — il vaso d'espansione (`rules/hydronic/expansion-on-closed-circuit.json`,
  `expansion-on-the-stored-volume-feed.json`), il volume minimo, la valvola di non ritorno su ogni unità in cascata. La
  valvola di sicurezza fuori da ogni pompa resta (I-218, D-182); lo sfiato, che la Shenling ha a bordo, per ora pure;
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
