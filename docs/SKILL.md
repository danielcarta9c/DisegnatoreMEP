# Com'è fatta la skill

> **Questo è il documento che mancava.** Dice di quali pezzi è fatta la skill, cosa fa
> ciascuno, con cosa lavora e **quando è finito**. Se una domanda comincia con «come
> funziona…» o «di chi è questo pezzo…», la risposta è qui e in nessun altro posto.
>
> **Blindato in ADR 0005.** L'architettura qui descritta non si ridiscute pezzo per pezzo:
> si cambia con una nuova ADR.
>
> Non contiene stato («a che punto siamo» sta in `PROJECT_STATE.md`), non contiene storia
> («perché abbiamo deciso così» sta in `docs/DECISION_LOG.md`), non contiene numeri di
> stampa (stanno in `docs/GRAPHIC_STANDARD.md`).

---

## 1. Cosa fa la skill, in tre righe

L'ingegnere ha già deciso e dimensionato l'impianto. Glielo dice a parole, nella
conversazione. La skill capisce di che impianto si tratta, **aggiunge gli accessori che
mancano e che un impianto deve avere**, glieli fa approvare, e poi ne **disegna la tavola
tecnica** — pronta da stampare e da portare in cantiere.

**Quello che la skill non fa mai:** progettare. Non inventa potenze, temperature,
prevalenze, tarature, volumi né diametri. Se il progettista glieli dà, li scrive sulla
tavola; se non glieli dà, sulla tavola non compaiono (D-087).

---

## 2. I sei pezzi

```
   la conversazione con l'ingegnere
              │
        ┌─────┴──────┐
        │  1. CAPIRE │  interpretazione       ← non deterministico
        └─────┬──────┘
              │  il modello dell'impianto: componenti, attacchi, tubi, reti
        ┌─────┴──────────────┐
        │ 2. COMPLETARE      │  regole degli accessori
        └─────┬──────────────┘
              │  l'ingegnere approva il dossier delle integrazioni
        ┌─────┴──────────────┐
        │ 2bis. ASSEMBLARE   │  la sequenza dei pezzi lungo ogni tubo
        └─────┬──────────────┘
              │  «PdC → valvola → filtro → defangatore → tratto → valvola → volano»
        ┌─────┴──────────────┐
        │ 3. DISPORRE        │  posizionamento, instradamento, distribuzione
        └─────┬──────────────┘
              │  usa: 4. LIBRERIA DEI SIMBOLI   e   5. CARTIGLIO
        ┌─────┴──────────────┐
        │ 6. VERIFICARE      │  validatore + occhio terzo
        └─────┬──────────────┘
              │
          la tavola
```

Ogni pezzo si costruisce e si collauda **da solo**, con un contratto suo. Il disegno di
prova serve a **scoprire** i difetti, mai a **definire** cosa è giusto (D-092).

---

## 2bis. Di che pasta è fatto ogni pezzo

**È la domanda che decide tutto, e va risposta prima di costruire.** Un pezzo fatto di
istruzioni per un'AI e un pezzo fatto di programma non si scrivono, non si provano e non
si correggono allo stesso modo.

| # | Pezzo | Di cosa è fatto | Dove vive |
|---|---|---|---|
| 1 | **Capire** | **Agente AI**, istruito con file di testo `.md` che gli spiegano cosa deve tirare fuori dalla conversazione e cosa non deve inventare | istruzioni della skill |
| 2 | **Completare** | **Programma deterministico** che legge **regole scritte come dato** (un file per regola) e le applica al modello | motore in codice, regole in file di dati |
| 2bis | **Assemblare** | **Programma deterministico**: mette in fila i pezzi lungo ogni tubo secondo la posizione che ogni regola dichiara | codice + la posizione dichiarata in ogni regola |
| 3 | **Disporre** | **Programma deterministico**: posiziona, instrada, distribuisce. Nessuna AI tocca le coordinate | codice |
| 4 | **Libreria simboli** | **Dati**: per ogni simbolo un disegno vettoriale e una scheda che dichiara taglia, attacchi, imbocchi ammessi, rotazioni e fonte | file, uno per simbolo |
| 5 | **Cartiglio** | **Dati**: un modello di riquadro fornito dall'azienda, riempito coi dati del progetto | file fornito dal PM |
| 6 | **Verificare** | **Due cose diverse**: (a) controlli e misure = **programma deterministico**; (b) occhio terzo = **agente AI** con contesto proprio | codice + istruzioni della skill |

### La linea di confine, e perché sta lì

```
   AI          →   scegli GLI INGRESSI     (pezzo 1: capire)
   PROGRAMMA   →   produci L'ELABORATO     (pezzi 2, 3, 4, 5)
   AI          →   giudica IL RISULTATO    (pezzo 6b: occhio terzo)
```

**Nessuna AI disegna e nessuna AI corregge il disegno.** Il motivo è una proprietà che il
prodotto non può perdere: *stesso impianto, stessa tavola, sempre*. Se un'AI potesse
spostare una linea, due esecuzioni identiche darebbero due tavole diverse e non si
saprebbe più quale è quella buona. Quando l'occhio terzo respinge, non tocca il disegno:
cambia **gli ingressi** — l'impaginazione, l'ordine, il formato — e il programma
ridisegna tutto da capo.

### Come sono fatte le regole del pezzo 2 — la risposta esatta

**Non sono programma e non sono un database. Sono file di dati, uno per regola.** Ogni
file dice, in forma leggibile anche da un non programmatore:

- **quando** si applica — espresso solo con le **funzioni** dei componenti («qualsiasi cosa
  si manutenga», «qualsiasi generatore»), mai col nome di un componente;
- **quante volte** può proporre — una per rete, una per componente, **una per attacco**;
- **cosa** propone e **in che punto** funzionale;
- **come si riconosce che c'è già**, così rieseguirla non duplica niente;
- **perché**, in una frase leggibile dal PM, e da **quale fonte** viene.

Questo è il motivo per cui sono dati e non codice: **si aggiunge una regola aggiungendo un
file, senza toccare il programma.** Se per aggiungere una famiglia di accessori servisse
modificare il motore, il motore sarebbe sbagliato. Ed è anche il motivo per cui una regola
deve essere generale (D-090): una regola scritta su misura di un componente è codice
travestito da dato.

Stessa logica per il pezzo 4: un simbolo si aggiunge aggiungendo due file, non toccando il
programma.

---

### Pezzo 1 — Capire

**Cosa fa.** Legge la conversazione e costruisce il **modello dell'impianto**: quali
macchine ci sono, quanti attacchi ha ciascuna, quali tubi le collegano, a quale rete
appartiene ogni tubo (riscaldamento andata, riscaldamento ritorno, acqua fredda, acqua
calda sanitaria…).

**Con cosa lavora.** Solo con quello che l'ingegnere ha detto. Ciò che è ambiguo diventa
una domanda, non un'invenzione.

**Cosa produce.** Il modello — **l'unica fonte di verità del progetto**. Non contiene
coordinate: dove sta un pezzo sul foglio lo decide il pezzo 3, e si può ricalcolare
sempre.

**È finito quando** da una descrizione a parole esce un modello che l'ingegnere riconosce
come il proprio impianto, e ogni cosa non detta è una domanda posta.

---

### Pezzo 2 — Completare: le regole degli accessori

**Cosa fa.** Guarda il modello e dice cosa manca: *«questo circuito chiuso non ha il vaso
di espansione», «questa macchina non si può isolare per manutenzione», «il ritorno del
generatore non ha il defangatore»*. Ogni proposta porta il **perché** e la **fonte**.

**Come è scritta una regola — e questo è il punto che abbiamo sbagliato.** Una regola
parte dal **motivo per cui l'accessorio esiste**, ed è sempre **generale**:

> La valvola di intercettazione serve a chiudere l'acqua per smontare o sostituire un
> pezzo. Quindi va su **ogni tubo che entra o esce da qualcosa che si manutiene o si
> sostituisce**.

Non «il volano vuole quattro valvole». Quattro è il *risultato*, perché quel volano ha
quattro attacchi. Il catalogo dichiara le **proprietà** dei componenti (si manutiene, si
sostituisce, sporca il circuito, produce aria, va protetto dalla sovrapressione) e le
regole leggono quelle proprietà — mai il nome di un componente (D-069, D-090).

Ogni accessorio ha la propria ragione di posizionamento, ed è buona pratica consolidata:

| Accessorio | Perché sta lì |
|---|---|
| Valvola di intercettazione | per isolare un pezzo senza svuotare l'impianto → su ogni attacco di ciò che si manutiene |
| Filtro / defangatore | i residui viaggiano col ritorno verso lo scambiatore → sul ritorno, prima della macchina da proteggere |
| Separatore d'aria | l'aria si libera dove l'acqua è più calda → sulla mandata, appena fuori dal generatore |
| Vaso di espansione | l'acqua scaldata dilata → sul ritorno, dove lavora più freddo, sempre raggiungibile |
| Valvola di sicurezza | deve poter scaricare **sempre** → fra lei e la macchina non ci va nulla che si possa chiudere |
| Gruppo di riempimento | è una **derivazione dall'acqua di rete**, non un organo di passaggio |
| Miscelatrice sanitaria | miscela caldo e freddo → vuole **entrambe** le alimentazioni |

**È finito quando** le regole coprono le famiglie dichiarate, ognuna è generale, ognuna ha
una scheda leggibile da un non tecnico, e l'ingegnere ha approvato il dossier.

---

### Pezzo 2bis — Assemblare: la sequenza dei pezzi

**Cosa fa.** Prima che esista qualunque disegno, scrive **per ogni tubo la fila ordinata
dei pezzi** che ci stanno sopra:

    pompa di calore → valvola → filtro a Y → defangatore → tratto di tubo → valvola → volano

**Perché serve, e perché la sua mancanza si vede in tavola.** Oggi ogni regola infila il
proprio accessorio per conto suo e l'ordine che ne esce non l'ha deciso nessuno: sul
volano due valvole finiscono affiancate dalla stessa parte e tre attacchi restano nudi.
Peggio: l'ordine dipende dall'ordine alfabetico dei nomi dei file delle regole. Un ordine
impiantistico deciso dal nome di un file non è un ordine (D-093).

**Come lo fa.** Ogni regola, oltre a dire *cosa* propone, dichiara **dove sta nella
catena**: attaccato alla macchina, prima dell'intercettazione, subito dopo, lato impianto.
L'assemblatore mette in fila secondo quelle dichiarazioni. Sono le stesse ragioni
impiantistiche del pezzo 2: la sicurezza sta attaccata alla macchina perché fra lei e la
macchina non ci va nulla di chiudibile; il defangatore sta lato impianto perché deve
poter essere pulito a macchina isolata.

**Il vantaggio più grande.** La sequenza **si legge e si approva a parole**, senza
disegnare niente. Separa *cos'è l'impianto* da *come viene disegnato*: se la fila è
sbagliata lo si vede subito, e non serve una tavola per accorgersene.

### Il modo intelligente di farlo: vincoli, non numeri di priorità

La tentazione è dare a ogni accessorio un numero d'ordine. Sarebbe di nuovo un ordine
arbitrario, come oggi lo è l'ordine alfabetico dei file. Invece **ogni pezzo dichiara il
perché della propria posizione**, e la fila la calcola il programma:

1. **Come si attacca.** *In linea* sul tubo (valvola, filtro, defangatore, contatore,
   pompa) oppure **su uno stacco**, con una propria piccola catena che pende dal tubo —
   ed è il caso di vaso di espansione, valvola di sicurezza, scarico, riempimento, sfiato
   e strumenti. **La catena è quindi un albero, non una lista.**
2. **I vincoli di vicinanza**, detti come ragioni e riferiti alle *funzioni* degli altri
   pezzi, mai ai loro nomi: «fra me e la macchina non ci va nulla di chiudibile» (valvola
   di sicurezza), «io sto lato impianto rispetto all'intercettazione» (defangatore, così
   si pulisce a macchina isolata), «io vengo prima di ciò che proteggo» (filtro).
3. **Il regime di intercettazione**: mi si isola normalmente; **non mi si isola mai** (la
   sicurezza); mi si isola **solo con valvola bloccabile** (il vaso di espansione).

Il programma fa un ordinamento su questi vincoli ed espande gli stacchi uno dentro
l'altro. **Se due vincoli si contraddicono, si ferma e dice quali due regole non possono
stare insieme** — invece di produrre in silenzio una fila sbagliata, che è esattamente
quello che succede oggi.

Il guadagno: la regola dell'intercettazione resta **una sola** e vale anche **sugli
accessori** che si dichiarano manutenibili; e i casi speciali che il PM ha segnalato non
sono eccezioni scritte dentro il programma, ma **proprietà dichiarate** dal pezzo.

**È finito quando** per ogni tubo di un impianto qualunque esiste una fila scritta, ogni
pezzo ci sta per una ragione dichiarata, gli stacchi hanno la propria catena, e la fila è
la stessa che scriverebbe a mano un termotecnico.

---

### Pezzo 3 — Disporre: posizionamento, instradamento, distribuzione

**Cosa fa.** Decide **dove** va ogni macchina sul foglio e **come** corrono i tubi.

**Le regole, che vengono dal PM e non si negoziano.** Si legge da sinistra a destra
seguendo il processo. Costano, in quest'ordine: le **curve**, gli **incroci**, la
**lunghezza**. Vietato sovrapporre due linee per il lungo. E soprattutto: **spostare un
oggetto è gratis, piegare una linea costa** — quindi la posizione delle macchine non è un
dato, è una variabile: si dispone, si instrada, si sposta, si reinstrada. Ma spostare non
vuol dire spargere: il foglio deve restare pieno.

**È finito quando** su un impianto qualunque nessuna linea fa un giro che si toglie
spostando un pezzo, nessun incrocio resta se si può evitare invertendo qualcosa di libero,
e nessuna curva è pagata senza motivo.

---

### Pezzo 4 — La libreria dei simboli

**Cosa fa.** Contiene il disegno di ogni componente, la sua taglia in millimetri di carta,
**dove sono i suoi attacchi**, da che lato si può imboccare, e come può essere ruotato.

**Da dove vengono i simboli.** Dalla norma italiana UNI 9511 per tubi, giunzioni,
valvolame e strumenti; dalla pratica dei produttori per le macchine, che la norma non
copre. **Nessun simbolo inventato**: ognuno dichiara la propria fonte, e se la fonte non
c'è si chiede al PM invece di disegnare a naso (D-083).

**È finito quando** ogni simbolo usato è riconoscibile da un termotecnico italiano senza
guardare la legenda, dichiara la propria fonte, e mostra ciò per cui esiste (un bollitore
a serpentino deve *mostrare* il serpentino attaccato ai bocchelli).

---

### Pezzo 5 — Il cartiglio

**Cosa fa.** Il riquadro con committente, oggetto, tavola, scala, data, revisione e
firme, più la squadratura del foglio.

**Non va inventato: è un ingresso del progetto.** Il cartiglio aziendale Nove C è nel
repository dal primo giorno (`assets/cartigli/`). Finora ne abbiamo usato solo i margini
per misurare (D-091).

**È finito quando** la tavola esce con il cartiglio compilato coi dati che il progetto
possiede, la cornice chiusa sui quattro lati, e nessun campo obbligatorio vuoto su una
versione finale.

---

### Pezzo 6 — Verificare

Tre livelli, e servono tutti e tre:

1. **Controlli di correttezza** — nulla si sovrappone, niente esce dal foglio, i testi non
   si scontrano, ogni rimando ha il suo gemello. Bloccanti.
2. **Controllo di qualità (preflight)** — misura *come è disegnata*: curve, incroci,
   distanze, giri inutili, riempimento del foglio, altezza dei testi, fonte dei simboli.
   Bloccante o avviso. **Ogni misura va fatta dove la regola vive** — per attacco, per
   tratta, per simbolo — mai su un totale: contare non è guardare (D-088).
3. **Occhio terzo** — un disegnatore senior che **non conosce le nostre regole**, riceve
   solo l'immagine stampata e la confronta con tavole vere. Può respingere. Ciò che
   respinge due volte per lo stesso motivo diventa una misura automatica (D-065, D-086).

**È finito quando** la tavola passa i primi due e l'occhio terzo la firmerebbe.

---

## 3. Le tre regole di metodo che ci siamo dati, e che valgono per tutti e sei

1. **Uno decide, uno o più fanno, uno controlla.** Chi costruisce non approva il proprio
   lavoro (D-083).
2. **Si verifica guardando, non contando.** Ogni modifica si chiude guardando l'immagine
   rigenerata, non solo la batteria di prove (D-088).
3. **Gli esempi del PM non sono l'elenco dei difetti.** Per ogni difetto segnalato si
   cercano tutti i suoi simili e si chiudono insieme (D-089).

---

## 4. Dove sta scritto cos'altro

| Domanda | Documento, e uno solo |
|---|---|
| Cosa fa il prodotto e cosa non fa | `PRD_DISEGNATORE_MEP.md` |
| **Com'è fatta la skill** | **questo file** |
| Come si collabora, chi decide cosa | `AGENTS.md` |
| Come si disegna bene, regola per regola | `docs/QUALITA_GRAFICA.md` |
| I numeri della carta: millimetri, spessori, testi | `docs/GRAPHIC_STANDARD.md` |
| Perché abbiamo deciso una certa cosa | `docs/DECISION_LOG.md` |
| A che punto siamo e cosa manca | `PROJECT_STATE.md` |
| Cosa è stato rimandato, e perché | `docs/DEFERRED.md` |
| Da dove vengono simboli e prescrizioni | `docs/research/SOURCE_REGISTER.md` |
| Come giudica l'occhio terzo | `docs/COLD_EYE_REVIEW.md` |

Tutto ciò che sta in `docs/plans/` è **storia**: racconta come è andata un'esecuzione, non
cosa è vero adesso. Non va letto per sapere come funziona la skill.
