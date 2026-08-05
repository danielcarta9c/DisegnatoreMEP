# Com'è fatta la skill

> **Questo è il documento che mancava.** Dice di quali pezzi è fatta la skill, cosa fa
> ciascuno, con cosa lavora e **quando è finito**. Se una domanda comincia con «come
> funziona…» o «di chi è questo pezzo…», la risposta è qui e in nessun altro posto.
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
