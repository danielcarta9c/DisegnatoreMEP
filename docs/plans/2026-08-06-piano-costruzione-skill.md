# Piano di costruzione della skill, pezzo per pezzo

**Data:** 6 agosto 2026
**Stato:** in attesa del via del PM.
**Sostituisce** il piano di rilancio del 5 agosto (D-084) come piano operativo. Quel piano
resta come storia: i suoi pacchetti WP1–WP5 sono eseguiti e collaudati, e ciò che hanno
prodotto viene qui riusato o rifatto secondo le tabelle §2.

**Architettura di riferimento:** ADR 0005 e `docs/SKILL.md`. Questo piano non ridiscute
l'architettura: la costruisce.

---

## 1. Le regole del gioco, valide per ogni pezzo

Sono le correzioni di metodo che il PM ha imposto e che hanno causato i difetti finora.
Nessun pezzo è «fatto» se ne viola una.

1. **Un pezzo alla volta.** Niente lavori in parallelo: si apre il successivo quando il
   precedente è collaudato e guardato (D-092).
2. **Criteri di accettazione come proprietà**, valide su qualunque impianto — «ogni
   attacco manutenibile ha la sua valvola» — mai come numeri di una tavola di prova.
   È vietato tarare una soglia su una fixture.
3. **Si verifica guardando, non contando** (D-088). Ogni prova asserisce la regola **dove
   la regola vive** — per attacco, per tratta, per simbolo — e ogni pezzo si chiude
   guardando l'artefatto che produce.
4. **Regole generali, mai particolari** (D-090). Una regola scritta su misura di un
   componente è codice travestito da dato.
5. **Tre ruoli** (D-083): chi orchestra scrive i criteri prima, chi sviluppa esegue, un
   collaudo a contesto separato può respingere. Verdetti registrati in appendice.
6. **Gli esempi del PM non sono l'elenco** (D-089): per ogni difetto segnalato si cercano
   tutti i suoi simili e si chiudono insieme.
7. **La skill non progetta** (D-087). Un rilievo che le chiede di inventare un dato di
   progetto non si esegue: torna al progettista.

**Ogni pezzo consegna al PM un artefatto che lui possa leggere e bocciare** — non un
rapporto tecnico. È il modo in cui verifichiamo di stare costruendo la cosa giusta senza
fargli leggere codice.

---

## 2. Cosa si tiene e cosa si rifà

Il giudizio è sul **pezzo**, non sul file.

| Pezzo | Stato | Decisione |
|---|---|---|
| Modello dell'impianto, senza coordinate | sano, collaudato | **si tiene** |
| Motore delle regole (caricamento, applicazione, tracciabilità, idempotenza) | sano | **si tiene** |
| **Contenuto** delle 19 regole | particolare invece che generale | **si rifà** (P2) |
| Vocabolario delle proprietà nel catalogo | non esiste | **si costruisce** (P1) |
| Assemblatore | non esiste | **si costruisce** (P3) |
| Meccanica della libreria dei simboli | sana | **si tiene** |
| Contenuto dei simboli | dalle fonti, ma manca la distinzione in linea / su stacco | **si completa** (P4) |
| Instradamento con la funzione di costo del PM | sano, il più difficile del progetto | **si tiene** |
| Composizione: il disegno è una striscia, riempie il 39 % | limite vero | **si rifà** (P6) |
| Cartiglio | mai disegnato, cornice aperta | **si costruisce** (P5) |
| Controlli di correttezza e preflight di qualità | sani e utili | **si tengono ed estendono** (P7) |
| Occhio terzo | protocollo scritto e provato | **si tiene**, diventa cancello di routine (P7) |
| Soglie e numeri tarati sulla tavola di prova | zavorra | **si buttano** (P7) |

---

## 3. I pezzi, in ordine di costruzione

L'ordine non è negoziabile: ciascuno ha bisogno del precedente.

### P1 — Il vocabolario delle proprietà

**Perché per primo.** Senza, una regola generale non può esistere: «tutto ciò che si
manutiene» non è dicibile se nessun componente dichiara di essere manutenibile.

**Contratto.** Il catalogo dichiara, per ogni componente, ciò che serve a una regola per
ragionarci senza nominarlo: si manutiene o si sostituisce; sporca il circuito; produce
aria; va protetto dalla sovrapressione; regime di intercettazione (normale / mai / solo
con valvola bloccabile); come si attacca (in linea / su stacco).

**Accettazione.** Ogni proprietà ha una definizione scritta in una riga comprensibile a un
non tecnico. Nessuna proprietà è il nome di un componente travestito. Una prova
automatica lo presidia.

**Artefatto per il PM:** l'elenco delle proprietà con la definizione di ciascuna.

### P2 — Le regole degli accessori, generali

**Contratto.** Ogni regola parte dal **motivo per cui l'accessorio esiste**, si esprime
sulle proprietà di P1, e dichiara: quando si applica, quante volte, cosa propone, **in che
punto della catena e perché**, come si riconosce che c'è già, la fonte.

**Accettazione (proprietà, non numeri).**
- Le sei regole di intercettazione diventano **una sola**, e vale anche sugli accessori
  che si dichiarano manutenibili.
- Su un impianto qualunque: ogni attacco di ogni cosa manutenibile ha la sua valvola;
  nulla di chiudibile fra una sicurezza e ciò che protegge; un vaso di espansione è
  isolabile solo con valvola bloccabile.
- Nessuna regola nomina un componente. Prova automatica esistente.
- Rieseguire le regole su un modello completo non propone nulla.

**Artefatto per il PM:** le schede delle regole, una pagina per regola, in italiano
semplice — da approvare o bocciare **una per una**.

### P3 — L'assemblatore

**Contratto.** Da modello + proposte a **un albero di catene**: per ogni tubo la fila
ordinata dei pezzi, e per ogni stacco la propria fila. Ordina risolvendo i **vincoli
dichiarati** (D-094), non numeri di priorità. Se due vincoli si contraddicono, **si ferma
e nomina le due regole**.

**Accettazione.**
- La fila prodotta è **scritta in parole** e leggibile: *PdC → valvola → filtro →
  defangatore → tratto → valvola → volano*.
- Gli stacchi hanno la propria catena, non sono disegnati dentro il simbolo (ritira D-071).
- Su un impianto costruito apposta con due regole incompatibili, si ferma e le nomina.
- Deterministico: stesso modello, stessa fila.

**Artefatto per il PM:** la fila di ogni tubo dell'impianto di prova, scritta a parole,
**prima che esista qualunque disegno**.

### P4 — La libreria dei simboli

**Contratto.** Ogni simbolo dichiara taglia, attacchi, imbocchi ammessi, rotazioni e
**fonte**; e dichiara se è un pezzo in linea o un pezzo da stacco.

**Accettazione.** Ogni simbolo è riconoscibile da un termotecnico senza leggere la
legenda; mostra ciò per cui esiste (un bollitore a serpentino mostra il serpentino
attaccato ai bocchelli); nessuno cita una convenzione inventata; l'altezza dei testi
rispetta il minimo di norma.

**Artefatto per il PM:** il foglio dei simboli.

### P5 — Il cartiglio

**Contratto.** Disegnare il cartiglio aziendale già fornito, compilarlo coi dati che il
progetto possiede, chiudere la cornice sui quattro lati.

**Accettazione.** Nessun campo obbligatorio vuoto su una versione finale; una bozza è
marcata come tale; la cornice è chiusa.

**Artefatto per il PM:** una tavola con il suo cartiglio.

### P6 — La composizione

**Contratto.** Il disegno usa il foglio, non una fascia. Sviluppo anche in verticale, non
solo da sinistra a destra. Resta il vincolo dell'ordine di processo.

**Accettazione.** Su impianti di taglia diversa il foglio risulta pieno oltre la soglia
dichiarata e nessun quadrante resta vuoto; il formato si sceglie sempre fra A4 e A3.

**Artefatto per il PM:** la tavola.

### P7 — Il validatore e il cancello

**Contratto.** Estendere le misure alle proprietà nuove (catena, stacchi, regimi di
intercettazione, altezza testi, cornice, cartiglio). Togliere le soglie tarate sulla
fixture. Rendere l'occhio terzo un **cancello di routine**: si guarda l'immagine dopo ogni
pezzo, non solo alla fine.

**Accettazione.** Nessuna soglia deriva da una singola tavola; una tavola con un difetto
bloccante non esce; l'occhio terzo la firmerebbe.

**Artefatto per il PM:** il verdetto dell'occhio terzo, integrale.

---

## 4. Come si chiude un pezzo

Sempre gli stessi cinque passi, e il quarto non si salta mai:

1. Si scrivono i criteri di accettazione **prima** di sviluppare.
2. Si sviluppa.
3. Un collaudo a contesto separato verifica criteri, regressione e regole del colpo
   d'occhio. Può respingere.
4. **Si guarda l'artefatto** — la fila scritta, il foglio dei simboli, la tavola.
5. Si consegna l'artefatto al PM e si registra il verdetto in appendice.

---

## Appendice — registro di esecuzione

| Pezzo | Sviluppo | Collaudo | Data | Note |
|---|---|---|---|---|
| — | — | — | — | — |
