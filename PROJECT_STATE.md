# PROJECT STATE — Disegnatore MEP

**Aggiornato:** 2026-09-26 (`REL-003` finito sul ramo, **la tavola di prova è al PO**; su `main` il cartiglio, `REL-002`, I-132; poi `REL-001`)
**Ingresso breve:** `HANDOFF.md` · **Architettura del disegno:**
`docs/ARCHITETTURA-DEL-PIANO.md` · **Regole:** `docs/regole-del-piano.md`
**Fonte operativa:** `ACTIVE_WORK_PACKAGE.md` · **Dossier di stato:** `docs/pm/STATO-PM.md`
**Release corrente:** **0.3 — generalizzazione** (il numero di versione Python resta
`0.1.0`: non ha mai seguito le release dichiarate)

> **Come è fatto questo file.** In testa c'è **lo stato al 20 settembre 2026**, e sotto la
> riga `# Storia di esecuzione` c'è il racconto dei pacchetti precedenti, ciascuno con la
> propria data. Quella parte **non descrive il prodotto di oggi**: si legge per sapere come
> ci siamo arrivati, non per sapere come funziona la skill.

---

## Dove siamo — 26 settembre 2026, `REL-003`

**La seconda parte dei simboli nuovi è pronta, e la tavola di prova è al PO** (ramo
`claude/missing-symbols-uuzbhb`, rapporto `docs/collaudi/REL-003/RAPPORTO.md`).

- **Catalogo**: le voci dei cinque simboli, dodici accessori del circuito solare, e il dato delle
  **varianti**, che «Capire» sceglie solo quando il testo le nomina (D-188). 73 voci.
- **Fluido solare**: magenta nei due versi (D-187), una riga in legenda; le regole non aggiungono
  niente sulla sua rete (D-188).
- **Impianto 6**: dal testo al PDF, i cinque simboli sulla stessa tavola, A2, zero cedute e zero
  bloccanti.
- **Suite**: le stesse 46 rosse di `main`; zero `skip` e zero `xfail` nuovi; `ruff` e `mypy` verdi.

## Dove siamo — 26 settembre 2026

**Il cartiglio Nove C è sulla tavola** (`REL-002`, I-132, PR #59): «Si tutto perfetto». L'ha fatto una
seconda sessione che il PO ha dedicato al cartiglio (I-129), mentre la prima faceva i simboli.

- **Il cartiglio è il file del PO** (I-130), letto da un generatore che ne scrive il modello e il
  logo; la tavola lo porta con `--cartiglio`, compilato con i dati del progetto. Un dato che manca è
  «DA DEFINIRE», e la tavola esce in bozza (D-025).
- **L'A4 non è più un formato ordinario** (D-186): il cartiglio è largo 400 mm e resta a misura su
  ogni foglio, contro l'angolo in basso a destra.
- **Il disegno delle cinque tavole approvate non si è mosso di un pixel**, e il cartiglio disegnato
  coincide col file del PO fuori dai testi.
- **Suite:** le stesse 46 rosse di `main`; zero `skip` e zero `xfail` nuovi. Rapporto:
  `docs/collaudi/REL-002/RAPPORTO.md`.
- **Le due sessioni avevano preso gli stessi numeri** (I-133): quelli del cartiglio sono diventati
  I-129 … I-131 e D-186.

## Dove siamo — 25 settembre 2026

**Il PO ha messo i simboli davanti alla skill** (I-126): il pacchetto attivo è `REL-003`, e
`REL-001` aspetta scritto in `docs/plans/pacchetti/REL-001.md`.

- **I cinque simboli nuovi ci sono**, e **le forme sono approvate** (I-128, D-185): la pompa di
  calore aria-acqua di alta potenza, la caldaia modulare a condensazione, il collettore solare, il
  bollitore a due serpentini, il ventilconvettore canalizzato. **UNI 9511 non ne ha nessuno**: le
  forme vengono dagli schemi dei costruttori e dei progetti pubblici (SRC-030 … SRC-041), e il
  foglio che il PO ha guardato è `docs/collaudi/REL-003/REL-003-simboli-nuovi.pdf`.
- **La skill non li può ancora usare**: mancano le voci di catalogo, e Capire, che sceglie per
  mestiere e attacchi, non avrebbe come distinguere tre di loro dal fratello. È il resto di
  `REL-003`, con la tavola di prova e il circuito solare da decidere con il PO (D-184, punto 5).
- **Suite:** **46 rosse**, le stesse di `main` nome per nome; 1700 passate, 24 `skip` e 12 `xfail` identici a `main`. Il primo giro ne aveva trovata una nuova — la prova che elenca per nome i simboli che stanno diritti non conosceva le quattro macchine nuove —, corretta nella prova.

**Rischio 5 — la libreria certificata** — un passo avanti: i cinque simboli nuovi hanno la loro
fonte scritta nel manifesto e nel registro. Il foglio della libreria intera, però, non si stampa
più con `symbols-sheet`, che su un A3 ne accetta 32 e adesso sono 47.

## Dove siamo — 24 settembre 2026, notte

**`DRAW-018` fuso con la PR #57, tavole approvate (I-119)**: una valvola di sicurezza per
generatore, attaccata alla sua uscita e prima dei rubinetti, a qualunque potenza (la strada A,
D-182). Il metro delle tavole approvate è 1 · 1 · 1 · 2 · 1 rilievi, zero cedute e zero bloccanti;
la suite è a **46 rosse**, tutte del percorso senza piano.

**Il PO ha aperto la fase della prima release** (I-121 … I-125, **D-183**): la skill che il
progettista usa in una sessione di Claude — spiega l'impianto, lancia la skill, e «Capire» può fare
domande chiarificatrici. Il perimetro è suo: **la skill vera e propria e il PDF** (`REL-001`,
attivo), **il cartiglio** (`REL-002`), **i simboli nuovi** (`REL-003`), **il DXF** (`REL-004`), **il
pacchetto della release** (`REL-005`). Il piano sta in `docs/plans/2026-09-03-release-plan.md`.

**Il rischio più vecchio è adesso il lavoro attivo**: la skill non è mai stata eseguita nel suo
ambiente. `REL-001` la costruisce, la prova in camera pulita e la consegna al PO da provare in Claude.

## Dove siamo — 24 settembre 2026

**`DRAW-017`, tavole approvate (I-117):** «Strada A e le tavole vanno benissimo». Sulle cinque
tavole ricomposte dal pianificatore in camera pulita
(`docs/collaudi/DRAW-017/prova-camera-pulita-2026-09-24/`) ci sono adesso **la miscelatrice
termostatica con l'ingresso AF** (D-175), **il ricircolo ACS** verde chiaro che torna
nell'accumulo (D-176), **il vaso sanitario** dove l'ACS è centralizzata (D-178, D-179), **la freccia
di ritegne e circolatori nel verso del flusso** (D-180) e **la ritegno a N** di UNI 9511 (D-181).

- **Il metro**: formato · rilievi · incroci — 1: A3 · 1 · 1; 2: A3 · 1 · 1; 3: A3 · 1 · 2; 4: A3 ·
  2 · 2; 5: A2 · 1 · 5. Zero cedute e zero bloccanti su tutte.
- **Suite: 45 rosse** (erano 48), 1663 passate, nessuno `skip` né `xfail` nuovo. Le cinque tornate
  verdi sono le prove che leggevano un piano, ora quello del pianificatore; le 45 restanti
  compongono senza piano, per il percorso che D-151 ha tolto dalla decisione della posa.
- **La ricerca su valvole di sicurezza e segno della ritegno**, chiesta dal PO (I-115):
  `docs/fonti/ricerche/reports/Valvole di sicurezza e simbolo ritegno.md`. Ne è nata **D-182**.

**Il pacchetto attivo è `DRAW-018`** — le valvole di sicurezza **una per generatore**, attaccate
all'uscita e prima dei rubinetti, a qualunque potenza (la strada A, **D-182**, I-116). Cambiano le
tavole 1 e 4, che il PO vede prima della fusione. **Poi la prima release** (**I-118**): che cosa
viene dopo la 0.3 lo sceglie il PO, su una proposta della sessione.

**Il rischio più vecchio resta aperto**: la skill **non è mai stata eseguita nel suo ambiente
finale**, la chat di lavoro, con i cinque pezzi cuciti insieme.

## Dove siamo — 23 settembre 2026

**`DRAW-016`, tavole approvate (I-109).** Il pianificatore (`skill/comporre/`) compone **da solo i
cinque impianti completi**, in camera pulita: tutte e cinque le tavole escono con **zero tratte
cedute e zero rilievi bloccanti**, rilievi **1 · 1 · 2 · 2 · 3** contro 7 · 9 · 12 · 11 dei piani a
mano, e il piano a mano dell'impianto 5 non esce più. Le tavole sono in
`docs/collaudi/DRAW-016/prova-camera-pulita-2026-09-23/`, e il PO le ha **approvate**: «hanno
proprio l'aspetto di tavole professionali». Da qui in poi, migliorie e piccole correzioni.

- **La tavola 5 (scheletro) è approvata** (**I-108**), ed è il metro del pavimento di B1, che
  adesso conta anche le pieghe fra due pezzi (**D-173**, approvata il 23 settembre): 7 rilievi di B1 → 0.
- **Il motore trasla prima di instradare**, e **cinque suoi difetti** trovati dagli agenti sono
  corretti — fra questi il colore di mandata e ritorno che dipendeva dal verso della tratta, e
  gli organi con un verso disegnati contro il flusso.
- **Suite: 48 rosse** (lo stesso insieme della base del pacchetto), 1627 passate, nessuno
  `skip` né `xfail` nuovo. Il bersaglio del pacchetto è 38.
- **Domande al PO**: `docs/collaudi/DRAW-016/RAPPORTO.md` §10.

**Fuso su `main` con la PR #53.** Il pacchetto attivo è **`DRAW-017`**: le risposte del PO alle domande del rapporto (I-110) — **D-174** B10 sulla coppia, **D-175** la miscelatrice termostatica con l'ingresso AF, **D-176** il ricircolo ACS verde chiaro che torna nell'accumulo, **D-177** la legenda su due colonne, **D-178** il vaso sanitario negli impianti centralizzati — e i piccoli difetti che il PO elencherà.

Il dettaglio sta in `HANDOFF.md` e nel rapporto; quello che segue è lo stato al 21.

## Dove siamo — 21 settembre 2026

> ⛔ **`DRAW-015` è fuso su `main`, e le tavole NON sono approvate** (**D-166**). Le ha
> separate il PO: «la PR la puoi fondere **ma le tavole non sono "approvate"**… sono ancora
> **lontane da ciò che voglio**. Però **la direzione ora è quella giusta**». **Quello che è
> approvato è la direzione**, e nessuna sessione può citare quella fusione come approvazione di
> una tavola.
>
> ⛔ **E il criterio di un'autostrada non è un numero** (**D-164**): «non c'è un numero…
> **un'autostrada per definizione ha poche curve e tratti rettilinei**… un criterio **grafico
> non matematico**». Chi giudica è l'**occhio**. **La convenzione grafica non si tocca**
> (**D-165**).

**Il 20 settembre il progetto ha cambiato architettura.** Il disegno non si cerca più: lo
**compone un agente** — pianificatore → motore → revisore (**D-151**). `layout/improve.py`,
la fase del tronco di `layout/spine.py` e `layout/dilate.py` **restano agli atti e non
decidono più la posa**.

| | |
|---|---|
| Release | **0.3 — generalizzazione** |
| Pacchetto attivo | **`DRAW-016`**, **ATTIVO**. **Il punto 0 è fatto**: il pianificatore esiste (`skill/comporre/`) e in camera pulita **batte il piano scritto a mano** — impianto 5 da **A1 ad A3**, impianto 4 da **A2 ad A4**. Si riparte **ricomponendo i cinque piani**, che dopo D-167 sono vecchi |
| Chi sviluppa | **un agente solo** (D-147), con agenti paralleli **dentro** la sessione (D-152) |
| Chi approva la fusione | **il PO, guardando le tavole** (D-146, D-147) |
| Architettura del disegno | `docs/ARCHITETTURA-DEL-PIANO.md` — vigente, sostituisce quella del solutore |
| Regole di composizione | `docs/regole-del-piano.md` — aperto per dichiarazione del PO |
| Prodotto in chat | **mai eseguito nel suo ambiente finale.** È il rischio più vecchio |

### Il 20 settembre il PO ha guardato le tavole, e ne sono uscite altre cinque

Con due tavole segnate a penna in mano (`docs/input-pm/riferimenti-grafici/2026-09-20/`):
«Le tavole fanno schifo… **il disegno nasce dalle linee delle autostrade**».

**D-159** il metodo — la quota di un'autostrada **non si sceglie**, è quella della **porta**
della macchina che la genera; si posa su quelle quote, si guarda che siano rette, e **solo
dopo** si appendono valvole e confini di rete · **D-160** una regola ha **una fonte** e **un
controllo**, e un controllo fuori dal punteggio non è un controllo · **D-161** il piano **non
può chiedere la forma di una spezzata**: può solo liberarle il posto, e la leva che manca si
chiama **`passa-per`** · **D-162** l'occhio del revisore **guarda** e **non ricalcola** ·
**D-163** un attacco scorre **lungo la propria faccia**, mai di faccia, mai se è di un
serpentino.

**Che cosa ne è uscito, misurato:** le regole misurate sono **nove** (A1, A4, B1, B3, B4, e
le nuove **B8** sali-scendi, **B9** corsie libere, **B10** mandata sopra ritorno sotto, **B11**
la coppia corre insieme); **l'occhio del revisore esiste** — `skill/rivedere/`, provato in
camera pulita, e ha trovato **due difetti che nessun controllo poteva dare**; i cinque piani
sono stati corretti **guardando le tavole**, e l'impianto 5 è passato da **49 a 38** rilievi e
da **14 a 12** incroci.

**Il giudizio del PO sulle cinque, ed è il metro vero:** «1, 2, 3 vanno quasi bene; **la 4 e
la 5 mi sembra che non hai minimamente risolto il problema. Non vedo le autostrade ben
tracciate.**»

### Le dodici disposizioni che hanno cambiato la rotta, 19–20 settembre

**D-147** agente unico · **D-148** oltre l'A3 si va: A4, A3, A2, A1, dichiarata momentanea
dal PO · **D-149** il riempimento del foglio esce dagli obiettivi e torna una misura; la
dilatazione di D-142 è ritirata · **D-150** una tratta che non si instrada non uccide più la
tavola: ripiego dichiarato, marcato `unresolved`, nominato dal preflight con un rilievo
bloccante · **D-151** il disegno lo compone un agente · **D-152** agenti paralleli in
sessione, mai sessioni · **D-153** il revisore si costruisce subito, ed è lo strumento con
cui si scrivono le regole · **D-154** tre macro fasce verticali, prima le autostrade dritte,
la tre vie non spezza il tratto, più generatori o più terminali ⇒ collettore verticale ·
**D-155** il piano non è un input: lo scrive il pianificatore, che è un pezzo della skill ·
**D-156** i cinque pezzi della skill e la natura di ciascuno; 3 e 4 sono l'instradatore-
disegnatore, ed è misto · **D-157** il revisore emette **vincoli** su nodi nominati, mai
mosse · **D-158** ogni vincolo di posa ha un **rilievo sulla tavola consegnata**.

### La misura che ha deciso D-151

`docs/collaudi/PROVA-PIANO/`: **impianto 1 e impianto 5 composti a mano** ed eseguiti dal
motore, **zero rilievi bloccanti e zero tratte cedute**, con un giro di correzione da **~30
secondi** contro i **10–40 minuti** del solutore.

**Quello che la prova non dimostra, e il PO l'ha detto:** che le tavole siano belle. «C'è
molto da migliorare ancora, non assomiglia a come dovrebbe essere un disegno» (**I-082**).
Resta storto, misurato: il disegno è una **fascia nella metà alta** del foglio, nessuno
distribuisce in verticale; l'impianto 5 ha **quattordici incroci**.

### Le consegne, e dove è finito il loro lavoro

- **PR #32 — `DRAW-010`: verificata e respinta** il 15 settembre 2026. Verdetto in
  `docs/pm/2026-09-15-review-pr32-draw010.md`. **Il suo lavoro non è su `main`**: la testa
  del ramo, `df66709`, non è antenata di `main` (verificato con `git merge-base
  --is-ancestor`).
- **PR #41 — `DRAW-012`: verificata e respinta** il 18 settembre 2026 — tredici criteri su
  sedici, nessuno barato, ma il PO ha guardato le tavole e ha detto «era meglio prima».
  Verdetto in `docs/pm/2026-09-18-review-pr41-draw012.md`. **Quella PR non è stata fusa** e
  la testa del suo ramo non è antenata di `main`.

  ⚠ **Va detto per intero, perché la misura dice una cosa in più del verdetto:**
  `DRAW-013` è ripartito **dal ramo di `DRAW-012`** e non da `main`, e il 19 settembre è
  entrato in `main` con la **PR #44** (`a835006`), che è il commit dove compaiono per la
  prima volta `layout/highways.py` e `layout/dilate.py`. Quindi **il contenuto** di
  `DRAW-012` è su `main` anche se la sua PR è stata respinta. Chi legge «respinta» e ne
  deduce «da rifare» sbaglia due volte: il lavoro c'è, e la dilatazione che portava con sé
  è stata poi **ritirata da D-149**.
- **`DRAW-014`: superato in corsa da D-151**, non chiuso come previsto. Ha fatto uscire le
  cinque tavole (D-148, D-150), e **proprio guardandole il PO ha fermato la linea del
  solutore**. **Quello che di `DRAW-014` resta vivo è in `main`**; quello che resta
  incompiuto è nominato nei rischi qui sotto.

## Rischi aperti — al 21 settembre 2026

1. **Le tavole non sono belle, e il PO lo ha detto guardandole** (I-082). Il primo difetto
   in coda è già nominato e misurato: il disegno è **una fascia nella metà alta** del foglio
   — `DRAWING_ALL_ON_ONE_SIDE`, D3 in `docs/regole-del-piano.md`, 5,2 volte l'inchiostro fra
   quadrante pieno e vuoto sull'impianto 1 e **9,0** sul 5. È il primo difetto aperto **del
   pianificatore**.
2. **Il pianificatore non esiste, e l'anello del revisore è aperto.** Il **pezzo 3** lo fa
   ancora un umano a mano (D-155, D-156). L'**occhio** del pezzo 5 adesso **c'è** —
   `skill/rivedere/`, D-162, provato in camera pulita — ma i vincoli che scrive sono un
   **rapporto in italiano**, non dati: il pezzo 3 non li riceve. Chiudere l'anello è il
   pacchetto attivo.
2bis. **Le autostrade del 4 e del 5 sono storte, e il PO le ha bocciate.**
   `HIGHWAY_IS_NOT_STRAIGHT` è acceso **5 volte sul 4 e 12 sul 5**. **Misurato dove sta il
   difetto**, ed è la fase delle autostrade, non quella degli organi: ridotti i due impianti
   a **sole macchine e collettori, senza una valvola**, restano **5 spezzate piegate sul 4 e
   11 sul 5**.
2ter. **Il piano non può chiedere la forma di una spezzata** (D-161), e `passa-per` non
   esiste: l'unica leva di chi compone è togliere di mezzo chi occupa la strada. Costa —
   sull'impianto 5 una linea faceva 3 pieghe invece di 1 **perché il gruppo di riempimento
   stava nella colonna**.
3. ~~**Nessun controllo sa che cos'è un'autostrada.**~~ **Chiuso da `DRAW-015`**, insieme
   alle altre quattro regole misurate: A1, **A4**, B1, B3, B4 in `validation/regole.py`.
   **Il 20 settembre sono diventate nove** — **B8** i sali-scendi, **B9** le corsie libere
   fra due linee, **B10** mandata sopra e ritorno sotto, **B11** la coppia mandata/ritorno
   corre insieme — ciascuna con la propria fonte e il proprio controllo (**D-160**).
   **Resta aperto il censimento di D-158**: A2, A3, B2, C1 e C3 non hanno un rilievo sulla
   tavola finita, e **A3 oggi non è tenuta su da niente**.
4. **Prodotto mai eseguito nel suo ambiente finale.** Nuova chat, input naturale,
   approvazione del grafo, generazione, restituzione del PDF: mai fatto. È il rischio più
   vecchio del progetto e il meno toccato. La 0.3 non si dichiara finita senza.
5. **Libreria simboli non interamente certificata.** La matrice fonti/forma/porte/ingombri
   va completata e **approvata dal PO** prima di dichiarare completa la 0.3.
6. ~~**Le prove non dicono più che cosa difendono.**~~ **Chiuso da `DRAW-015`:** i 36 file
   di `tests/layout/` portano la propria riga `# categoria:` — 24 motore, 10 solutore,
   4 regola del piano.
7. **Due prove difendono il pavimento invisibile, che non esiste più.** Asseriscono ancora
   `bottom_mm <= levels.ground_mm`, cioè il vincolo che il PO ha abolito l'11 settembre
   2026. Sono rosse, e finché stanno lì chi le legge crede che la regola esista.
8. **`DRAW-007` non ha cartella di collaudo.** È l'unico buco nella catena delle consegne:
   `docs/collaudi/` porta DRAW-001…006-R1, 008, 009, 012, 013.
9. **Il formato definitivo è una domanda aperta del PO.** D-148 è **dichiarata momentanea**:
   quando i cinque impianti usciranno tutti, «quale formato serve davvero» si riapre.
10. **La riproducibilità bit-per-bit se n'è andata** (D-023, sospesa da D-151). È un prezzo
    dichiarato e accettato — l'elaborato esce in DXF e si rifinisce in AutoCAD (I-072) — ma
    va saputo: due composizioni dello stesso impianto non danno la stessa tavola, e nessuna
    prova di non-regressione può più poggiare sull'impronta.
11. **Il motore non garantisce più che il disegno sia bello.** Garantisce che sia **valido**
    e che i difetti siano **nominati**. Il bello lo porta il piano, e il giudizio resta del
    PO, sulle tavole (D-146).
12. **Due tratte di autostrada della tavola 2 non possono essere rettilinee**, e non per
    difetto della posa: è il catalogo. Il PO decide se accettarlo, dare una rotazione al
    bollitore o mettere un raccordo nel grafo. **Domanda aperta, sua.**
13. **Il pettine di D-144 è bloccato dal simbolo del collettore**: `zone-manifold` dichiara
    `allowed_rotations_deg: [0]`, e per D-049 quel campo è un vincolo tecnico. **Domanda
    aperta al PO**: un collettore di zona si può disegnare in verticale?

**Che cosa non è più un rischio, e per quale decisione.** Il **riempimento del foglio** e la
**dilatazione** escono dai rischi perché escono dagli obiettivi (**D-149**); la **lunghezza**
era già uscita (D-139). Il **costo che poteva barattare tutto con tutto** e il **costo
computazionale del ciclo di miglioramento** non sono più rischi del percorso vigente, perché
quel percorso non chiama più il solutore (**D-151**); restano descritti nella storia qui
sotto. Il registro degli input non è più ingovernabile: dal triage del 15 settembre
(D-131…D-136) le righe aperte sono **dodici più quattro regole permanenti**, su 68.

**Che cosa questo riallineamento non ha misurato, e non va dato per fatto.** Che i cinque
impianti di prova producano oggi una tavola. D-148 e D-150 ne hanno cambiato le condizioni,
ed è il **criterio 6** di `DRAW-015` a chiederne la misura, impianto per impianto, con
formato e tratte cedute. Finché quella misura non è nel rapporto, qui non si scrive.

---

# Storia di esecuzione

**Tutto ciò che segue descrive il progetto prima del 19 settembre 2026**, pacchetto per
pacchetto. Si legge per sapere come ci siamo arrivati. Le parti che parlano di **costo**,
**ciclo di miglioramento**, **fase del tronco**, **riempimento** e **dilatazione** sono
storia: le hanno superate D-139, D-149 e D-151.

**Aggiornato:** 2026-09-15 (cold eye review dopo il merge di DRAW-009)

## Stato verificato — com'era al 15 settembre 2026

| Area | Stato |
|---|---|
| Modello dati e grafo | operativi; il grafo resta la fonte unica |
| Completamento e assemblaggio | operativi sulla tavola 1; tutti e cinque gli impianti arrivano alla posa; aperta la semantica dei compositi e delle multivia |
| Posa e routing | `DRAW-004` fuso; costo-peso, assi, dorsali e T ortogonali operativi. Da `DRAW-008` la posa è **a fasi**: il tronco si costruisce (`layout/spine.py`), il corredo lo allunga invece di piegarlo. Da `DRAW-009` il tronco **trasla tutto intero** portandosi dietro il proprio corredo (`Improver._block_moves`), e un **ingresso di rete** si posa addosso all'utente che serve invece di aprire la lettura. L'instradatore e i suoi pesi non sono stati toccati |
| Simboli | 39 manifesti: i 7 critici della tavola 1 sono verificati in DRAW-005; l'audit PM completo resta aperto prima della 0.3 |
| Etichette | fase separata dalla geometria; sigle principali sempre, indirizzi come velo esplicito (`--verifica`) |
| Packaging skill/chat | non ancora installabile né collaudato in una chat pulita |
| Release | versione Python `0.1.0`; `releases/latest/` ancora vuoto |

## Ultima baseline — DRAW-004

- PR #14, merge `c46f0db`;
- tavola 1: 6 curve, 1 incrocio, 577,5 mm di tubo;
- backtracking 0; tratte oltre tre pieghe 0;
- linea continua di terra assente;
- test dichiarati dal DEV: 1106 verdi, 22 sospesi, 13 xfail;
- controllo PM: 26 test mirati verdi, 8 sospesi; `ruff` e `mypy --strict` puliti.

Gli indicatori di DRAW-004 misurano il routing sul grafo ricevuto. Non certificano la
correttezza impiantistica del grafo, che il PO ha corretto con gli input I-030… I-040.

## Ultima baseline — DRAW-005

- PR #18, merge `006258c`; revisione PM conclusa il 2026-09-08;
- grafo dell'impianto 1: 39 pezzi (erano 45), 16 organi di chiusura (erano 21), nessuno
  fra filtro e PDC, nessuno consecutivo; un solo riempimento, sul ritorno tecnico;
- tavola 1: 4 curve, 1 incrocio, 525,0 mm — grafo diverso da DRAW-004, quindi non un
  miglioramento dichiarato: −37,5 mm vengono dal contenuto, −15,0 dal layout;
  backtracking 0; tratte oltre tre pieghe 0; 16 valvole su 16 a 2,5÷5 mm; la valvola
  comune di mandata a 5 mm dal raccordo della sicurezza;
- prove generali nuove: 35 (grafo), 39 (contratti grafici), 10 (posa e modalità);
  suite DEV 1190 verdi, 22 sospese, 14 xfail; controllo PM: 128 test mirati verdi,
  4 sospesi e 2 xfail dichiarati; `ruff` e `mypy --strict` puliti;
  determinismo verificato su due generazioni;
- rapporto e artefatti in `docs/collaudi/DRAW-005/`; righe I-030… I-040 restano aperte
  finché il PO non le chiude.

## Il lavoro di allora, pacchetto per pacchetto

`DRAW-006-R1` e `DRAW-007` sono stati **fusi in `main` dal PO** l'11 settembre 2026, con i
rilievi aperti dichiarati qui sotto. Non erano approvati criterio per criterio: il PO ha
scelto di consolidare il lavoro e di ripartire da un'architettura nuova, che è
`DRAW-008`.

**DRAW-006-R1** ha chiuso i quattro difetti semantici — ordine indipendente dagli
identificativi, assi per stato idraulico, gruppo EN 1487 unico sull'adduzione ACS,
riempimento come ponte fra due reti — e ha peggiorato la geometria.

**DRAW-007** ha dato alla tavola una **gerarchia**: autostrada, distribuzione, servizio,
calcolata sul grafo in `src/disegnatore_mep/layout/hierarchy.py` e letta dal costo di posa
e dall'obiettivo di allineamento. Ha inoltre tolto due cose che non dovevano esserci:

- **il pavimento invisibile.** La linea di terra non si disegna più da DRAW-004, ma la
  regola era rimasta: niente poteva scendere sotto l'83% dell'altezza del foglio. Il PO ha
  disposto che quel vincolo non esiste — «è uno schema quello che disegniamo» — e toglierlo
  ha portato la tavola 1 da 10 pieghe a 6;
- **il multivia contato come macchina.** La mandata dalla pompa di calore al puffer non
  risultava nemmeno autostrada, perché in mezzo c'è una deviatrice. Il tronco ci passa
  attraverso, stato per stato.

### Dove siamo davvero, con DRAW-009 fuso (PR #27, `2155c22`)

`DRAW-009` è stato **verificato dal PM e fuso** il 14 settembre 2026 attraverso la
PR #27, su autorizzazione del PO al merge (D-123, disposizione del 14 settembre): dodici
criteri raggiunti, quattro raggiunti in parte, nessuno non raggiunto. Verdetto criterio per
criterio in `docs/pm/2026-09-14-review-pr27-draw009.md`. Le misure qui sotto sono quelle del ramo di consegna,
lette sulla geometria che la CLI scrive; il rapporto completo sta in
`docs/collaudi/DRAW-009/RAPPORTO.md`.

| | testa di `main` (DRAW-008 fuso) | DRAW-009 |
|---|---|---|
| **Tavola 1** — rete ordinaria | 4 pieghe / 1 incrocio / 465,0 mm | **4 / 1 / 430,0 mm** |
| **Tavola 1** — totale | 10 pieghe / 1 incrocio / 620,0 mm | **4 / 1 / 470,0 mm** |
| **Tavola 1** — autostrade rettilinee | 8 su 8, zero pieghe | **8 su 8, zero pieghe** |
| **Tavola 1** — organi D-120 | 14 su 15 | **15 su 15** |
| **Tavola 2** — rete ordinaria | 9 / 6 / 755,0 mm | **5 / 1 / 555,0 mm** |
| **Tavola 2** — totale | 15 pieghe / 11 incroci / 877,5 mm | **5 / 1 / 600,0 mm** |
| **Tavola 2** — pieghe di autostrada | 4 | **2**, una per ciascuna delle due tratte che nessuna posa raddrizza |
| **Tavola 2** — `deviatrice.out_b → bollitore.coil_in` | 3 pieghe | **1 piega**: scende, attraversa il ritorno in perpendicolare, corre bassa |
| **Tavola 2** — nodi condivisi col tronco | 8 | **0** |
| **Tavola 2** — confini di rete su `cold_water` | 1, con una linea che serve due utenti in serie | **2**, uno per utente, ciascuno con la propria rete |
| **Tavola 2** — organi D-120 | 13 su 15 | **14 su 15** |
| **Suite** | 13 rosse, 1435 verdi | **10 rosse, 1470 verdi**: sei chiuse, tre nuove e dichiarate con la misura, sette che erano rosse e restano. Nessuna prova convertita in `skip` o `xfail` |

Il perché del salto sulla tratta `deviatrice.out_b → bollitore.coil_in` è misurato in
`docs/collaudi/DRAW-009/RAPPORTO.md` §3.9, e lo strumento che lo rimisura è
`docs/collaudi/DRAW-009/perche-la-strada-bassa-non-c-era.py`: la strada bassa non era cara,
**non c'era**, e a murarla erano il vaso, il manometro e la soglia del riempimento, tutti
appesi sotto il tronco alla quota del `coil_in`.

### Le misure di DRAW-008, per confronto

| | testa di `main` | DRAW-008 |
|---|---|---|
| **Tavola 1** | rete ordinaria 6 pieghe / 3 incroci / 550,0 mm; zero pieghe sulle 8 autostrade | rete ordinaria **4 / 1 / 465,0 mm**; zero pieghe sulle 8 autostrade; backtracking 0; D-120 14 su 15 |
| **Tavola 2** | **non esce**: un rilievo bloccante (`RUN_OVERSHOOTS_ITS_PORT`) | **esce, nessun bloccante**; rete ordinaria 9 / 6 / 755,0 mm; 8 autostrade rettilinee su 10 |
| **Autostrade storte, tavola 2** | 4 su 10 | **2 su 10**, ed è il massimo raggiungibile: nessuna posa ammessa dal catalogo le raddrizza (vedi rischio 12) |
| **Suite** | 11 rosse, 1411 verdi | **13 rosse, 1435 verdi**: una delle undici è tornata verde, tre sono nuove e sono regressioni dichiarate (rischio 15). Nessuna prova convertita in `skip` o `xfail` |
| **`ruff`, `mypy --strict`** | puliti | puliti |
| **Determinismo** | — | due generazioni, stessa impronta e stessa geometria byte per byte, su tavola 1 e tavola 2 |

## Rischi aperti — come stavano al 15 settembre 2026

> **Si leggono con l'elenco in testa a questo file**, che è quello vigente. Le voci che
> parlano di costo, ciclo di miglioramento, fase del tronco, riempimento e dilatazione sono
> storia: le hanno superate D-139, D-149 e D-151.

1. **Prodotto non ancora eseguito nel suo ambiente finale.** Dopo il collaudo controllato
   dell'impianto 2 e prima di estendere il ciclo agli impianti 3–5 serve una prova
   verticale: nuova chat, input naturale, approvazione del grafo, generazione
   deterministica e restituzione del PDF.
2. **Libreria simboli non interamente certificata.** Prima di dichiarare completa la
   generalizzazione 0.3 il PM deve completare la matrice fonti/forma/porte/ingombri; il
   DEV implementa solo la matrice approvata.
3. **Costo computazionale.** La tavola 1 richiede circa 70 secondi e oltre 2.000 routing
   di prova; DRAW-006 deve misurare l'impianto 2 senza renderizzare inutilmente gli altri.
4. **Vincoli fisici di posa non modellati.** Dall'11 settembre 2026 **non esiste nessuna
   linea di terra**: il PO ha disposto che su uno schema non c'è un sopra e un sotto, e il
   pavimento invisibile che era rimasto in `is_valid` è stato tolto. Se un giorno servirà
   un vincolo fisico vero — un'altezza, un ancoraggio — dovrà essere un campo esplicito del
   modello, dichiarato, non una frazione dell'altezza del foglio.
5. **Debito documentale storico.** Le vecchie sezioni operative sono conservate in Git,
   non devono tornare nei file di ingresso correnti.
6. **Geometria sensibile all'ordine delle connessioni.** La tavola composta in memoria e
   quella ottenuta dalla CLI non hanno ancora la stessa impronta; va risolto prima di
   usare il percorso end-to-end come prova di determinismo.
7. **Test geometrico inefficace.** L'ultima condizione della prova sulle colonne dei
   raccordi è logicamente ridondante; DRAW-006 deve sostituirla con una prova negativa
   che fallisca realmente quando un raccordo diventa colonna.
8. **Connettività multivia non modellata per stati.** Sull'impianto 4 produce domande di
   sicurezza troppo ampie; DRAW-006 introduce configurazioni idrauliche alternative.
9. **La tavola 2 non esce — chiuso da `DRAW-008`, in attesa del merge del PO.** Sulla
   testa di `main` il preflight trovava un rilievo bloccante; sul ramo di consegna di
   `DRAW-008` la tavola esce senza bloccanti.
10. **Il costo poteva barattare tutto con tutto — attenuato da `DRAW-008`, non chiuso.**
    Il ciclo resta un greedy su un costo lessicografico, ma **la rettilineità del tronco
    non è più una voce di costo**: è un vincolo di `Improver.is_valid`, e nessun guadagno
    la compra. Restano voci di costo l'allineamento del resto e i rami impilati. L'analisi
    sta in `docs/pm/2026-09-11-architettura-della-posa-a-fasi.md`.
11. **La misura «stacchi statici» conta anche ciò che statico non è.** Nel bucket finisce
    ogni tratta che non è rete ordinaria, quindi anche la linea di alimentazione del
    riempimento, che il vocabolario del progetto chiama `INBOUND`. Con il ponte la riga
    cresce senza che sia comparso uno stacco statico in più. La misura non è stata toccata:
    è una soglia del Work Package.
12. **Due tratte di autostrada della tavola 2 non possono essere rettilinee.** L'uscita
    secondaria della deviatrice guarda in basso, la serpentina del bollitore si imbocca da
    sinistra e il bollitore non ammette rotazioni: nessuna posa le mette una di fronte
    all'altra. Non è un difetto della posa, è il catalogo, e il codice lo calcola e lo
    nomina (`spine.SpineLayout.impossible`). Il PO decide se accettarlo, dare una
    rotazione al bollitore o mettere un raccordo nel grafo.
13. **Le tratte di rango inferiore attraversavano il tronco — chiuso da `DRAW-009`.**
    Erano 8 nodi condivisi; adesso sono **zero**. L'acqua fredda non attraversa più il
    foglio perché ciascun utente ha il proprio ingresso (I-061), e ogni ingresso si posa
    addosso a chi serve.
14. **La catena a fasi, da sola, toglieva la tavola all'impianto 4.** Sulla testa di `main`
    l'impianto 4 usciva; con le sole fasi l'instradamento falliva su `p7-a`. `compose_sheet`
    ha ora un **ripiego dichiarato** — posa seminata dal tronco, poi il ciclo senza le fasi,
    poi la disposizione di partenza — e con quello l'impianto 4 torna a uscire. Il ripiego
    è una rete di sicurezza, non una soluzione: finché scatta, quell'impianto non gode
    della posa a fasi. `docs/collaudi/DRAW-008/RAPPORTO.md` §6.2.
    **AVVERATO il 14 settembre 2026, dopo il merge di `DRAW-009`.** La rete non regge più:
    l'impianto 4 **non produce più una tavola**. Misurato dal PM con lo stesso
    comando sui due lati — su `b63e3e6` esce, su `2155c22` no, in 12 secondi, con
    `run s3-a on network secondario cannot be routed`. Nessuna prova se n'è accorta (rischio
    23). È il primo criterio di `DRAW-010`.
    `docs/pm/2026-09-14-review-pr27-draw009.md` §7.
15. **Le tre prove rosse di `DRAW-008` — chiuse da `DRAW-009`.** Le due di vicinanza
    tornano verdi senza essere toccate, come `DRAW-009` §E prevedeva; la terza si chiude
    per decisione del PO, con la prova riscritta su ciò che vuole davvero — l'impilamento,
    non l'ordine — e con la sua negativa.
16. **La fase del tronco consegna ancora una posa con pezzi sovrapposti.** Sulla tavola 2
    `lay_the_spine` + `carry_the_rest` consegnano nove coppie di pezzi addosso, fra cui il
    bollitore e il volano. `_relieve` non le separa perché il tronco di un circuito chiuso
    è un **anello**: qualunque sottoalbero si sposti contiene anche l'altro pezzo della
    coppia. Non è nuovo — la stessa posa esce identica sulla testa di `main` — e `DRAW-009`
    l'ha reso innocuo invece che risolto, permettendo al ciclo di uscirne. Finché resta
    così, la tavola 2 esce dal **ripiego** di `compose_sheet` invece che dalla propria posa
    a fasi. `docs/collaudi/DRAW-009/RAPPORTO.md` §6.3 e §7.3.
17. **L'ordine degli stacchi lungo il tronco non ha ancora un padrone.** La proprietà è
    misurata e vale su tutt'e due le tavole — le due tratte verso lo stesso pezzo corrono
    annidate — ma vale perché la topologia del flusso la impone, non perché la fase del
    tronco la scelga. `docs/collaudi/DRAW-009/RAPPORTO.md` §3.11 e §7.1.
18. **La tratta del prelievo ACS ha una piega.** Migliora — da 2 pieghe e 2 nodi su
    autostrada a 1 piega e zero — ma il criterio 3 chiede zero. `DRAW-009` posa addosso al
    proprio utente gli **ingressi**, non i prelievi: se il PO intende la regola anche per
    quelli è una riga, ma è una scelta di rappresentazione.
    `docs/collaudi/DRAW-009/RAPPORTO.md` §6.1 e §7.2.
19. **Una prova di `DRAW-007` e la regola monotona di `DRAW-009` non possono valere
    insieme.** `Improver.is_valid` rifiutava ogni candidata che lasciasse due pezzi
    addosso; `DRAW-009` la rende monotona — una mossa risponde delle sovrapposizioni che
    **crea**, non di quelle che trova — perché senza quella regola, sulla posa sovrapposta
    del rischio 16, *ogni* candidata è non valida e il ciclo resta inchiodato.
    `test_l_allineamento_non_si_accetta_quando_rende_la_tavola_peggiore` chiede il
    contrario, e diventa rossa: è l'unica regressione di `DRAW-009`. La regola più stretta
    che la farebbe passare — «né crea né approfondisce» — toglierebbe al ciclo la
    traslazione di blocco, misurato. La cura vera è il rischio 16.
    `docs/collaudi/DRAW-009/RAPPORTO.md` §6.5 e §7.5; lo strumento è
    `docs/collaudi/DRAW-009/le-due-sovrapposizioni.py`.
20. **Due prove hanno perso il proprio caso.** La prova che tiene la valvola di isolamento
    stretta al raccordo passante non trova più, sulla propria fixture, nessuna tratta con
    quella forma: §A.1 ha tolto il raccordo dell'acqua fredda dal ritorno tecnico e con lui
    la scomposizione che metteva la valvola dalla parte giusta. La sua guardia grida invece
    di passare a vuoto, ed è giusto così, ma **quella proprietà non è più sorvegliata da
    nessuna parte**. E la prova sulle frecce pretende che ogni tratta non statica ne porti
    una, mentre il renderer una freccia la mette solo su un tratto lungo almeno 4,0 mm: la
    tavola ha adesso una tratta ordinaria lunga un passo. `RAPPORTO.md` §6.7 e §7.7–§7.8;
    lo strumento è `docs/collaudi/DRAW-009/due-prove-senza-caso.py`.
21. **Due prove difendono il pavimento invisibile, che non esiste più.**
    `test_una_macchina_a_terra_puo_partecipare_a_un_candidato_verticale` e
    `test_the_hard_constraints_hold_after_improvement` asseriscono ancora
    `bottom_mm <= levels.ground_mm`, cioè il vincolo che il PO ha abolito l'11 settembre
    2026 e che `DRAW-008` ha tolto da `is_valid`. Sono rosse sulla testa di `main` e restano
    rosse: fuori dal perimetro di `DRAW-009`, ma finché stanno lì chi le legge crede che la
    regola esista. `RAPPORTO.md` §7.6.
22. **Un cricchetto già scattato, e non incassato.** L'impianto 2 torna a comporsi su una A3
    — `test_tornano_a_comporre_quando_la_composizione_compatta` è un `xfail(strict=True)` ed
    è rosso **anche sulla testa di `main`**. Sul ramo di `DRAW-009` quell'impianto passa
    tutte e cinque le prove che `COMPONIBILI` impone, misurato. Spostarlo da
    `NON_COMPONGONO` a `COMPONIBILI` è una riga, toglie una rossa e ne rende esigibili
    cinque verdi; non è stata fatta perché la rossa non nasce qui. `RAPPORTO.md` §7.9.

23. **La suite sorveglia la composizione di un impianto solo.**
    `COMPONIBILI = ("prova-1-due-pdc-accumulo-combinato.json",)`: è l'unico impianto di cui
    una prova pretenda che sappia comporsi. Gli altri compongono — quando compongono — **per
    capacità, non per contratto**, e se la perdono la suite resta verde. È così che si è
    perso l'impianto 4 senza che nessuno se ne accorgesse, ed è un difetto della copertura
    che vale quanto il difetto che ha nascosto. `DRAW-010` §C.

24. **«Aperto» ha smesso di voler dire qualcosa nel registro degli input.** 54 righe aperte
    su 63, 5 chiuse. Molte sono con ogni evidenza soddisfatte — `I-019` sulla linea di terra
    è chiuso mentre `I-024`, che dice la stessa cosa, è aperto — e due chiedono oggi il
    **contrario** di una decisione vigente: `I-060` vuole il PM sdoppiato che `D-130` ha
    abolito, `I-014` vuole la regola «ogni sessione finisce su `main`» che `D-123` ha
    superato. Quattro righe non hanno uno stato leggibile (`I-001`, `I-003`, `I-004`,
    `I-005`). Serve una passata di triage col PO: la chiusura di un input è sua, non del PM.
25. **`DRAW-007` non ha cartella di collaudo.** `docs/collaudi/` porta DRAW-001…006-R1, 008
    e 009: il 007 è stato fuso senza rapporto agli atti, ed è l'unico buco nella catena delle
    consegne.

## Dove siamo — 19 settembre 2026, dopo la PR #44

**`DRAW-012` e `DRAW-013` sono fusi** con la PR #44 (`a835006`): la struttura, le autostrade
e l'invariante della catena di `DRAW-012`, piu' il margine di 25 mm dal bordo (D-143), il
vincolo degli organi di servizio (D-145) e la curva dichiarata della distribuzione (D-144, in
parte). Undici criteri su quindici; i quattro mancanti erano **tutti** bloccati da `place.py`
e dalle rotazioni del simbolo del collettore — cioe' da un perimetro che aveva scritto il PM.

**Lo stesso giorno il PO ha cambiato rotta**, e sono le disposizioni **D-147**–**D-150**:

| | |
|---|---|
| **D-147** | PM e DEV tornano a essere **un agente solo**, nella stessa sessione. La fusione la approva il PO guardando le tavole |
| **D-148** | **Oltre l'A3 si va**: i formati ordinari sono A4, A3, A2, A1 |
| **D-149** | **Il riempimento del foglio esce dagli obiettivi** e torna una misura; la dilatazione di D-142 e' ritirata |
| **D-150** | **Una tratta che non si instrada non uccide piu' la tavola**: prende una spezzata di ripiego, si marca `unresolved`, e il preflight la nomina |

La ragione di D-147, in una riga: **`place.py` e' stato fuori perimetro per quattro pacchetti
di fila, ed e' li' che stavano le tavole 3, 4 e 5.**

### Le tre tavole che non uscivano, e perche'

Misurato il 19 settembre, prima di toccare il codice. **Tutt'e tre morivano per una sola
tratta**, e tutt'e tre contro il **bordo destro dell'area A3**:

| Impianto | Dove moriva | Che cos'e' in millimetri |
|---|---|---|
| 3 | `give the run a longer straight length` | non c'e' rettilineo |
| 4 | `no route from (134, 80) to (144, 80)` | la destinazione e' a **x 370** su una griglia che finisce a **x 360**: e' fuori dal foglio |
| 5 | `run into an obstacle at (140, 65)` | «l'ostacolo» e' **x 360,0 mm**, cioe' il bordo |

**L'impianto 4 esce su A2 senza toccare nient'altro** (misurato: 195 s). Gli impianti 3 e 5
su A2 falliscono ancora, ma per difetti **veri** — un ostacolo vero a due passi dove ne
servono cinque, e uno stacco di 5 mm con un accessorio in linea che ne chiede 7,5 — non piu'
contro il bordo. Quelle sono le cause da curare, ed e' il lavoro corrente.

---

## ~~Consegna in revisione~~ — DRAW-012, **fuso** nella PR #44 (scritta dal DEV, 17 settembre 2026)

`DRAW-012 — il motore disegna nell'ordine del disegnatore` è consegnato in una PR non fusa,
dalla testa di `main` (`8589620`). Rapporto e artefatti: `docs/collaudi/DRAW-012/`.

**Che cosa cambia nel motore**

- **La gerarchia**: sono macchine di spina **tutti** i generatori, gli scambiatori, gli
  accumuli e i collettori; è autostrada anche la strada che dagli accumuli porta ai
  terminali e al prelievo sanitario, con il circolatore dentro la tratta. L'ingresso
  dell'acqua fredda resta uno stacco di servizio, riconosciuto dal verso della porta del
  confine di rete.
- **`layout/highways.py`** è nuovo: l'**autostrada intera**, la catena di tratte che
  attraversa i propri crocevia, con l'invariante verificato su di lei e non su ogni
  frammento.
- **Il costo** non guarda più i millimetri (D-139): restano curve e attraversamenti, e il
  riempimento entra come **finestra** 45–65 % (D-140) letta insieme alla copertura
  dell'ingombro (D-141). La finestra è un dato condiviso fra costo e preflight, che adesso
  avvisa anche quando il foglio è troppo pieno.
- **Quando la struttura non si instrada non si butta la fase**: si cede una catena per
  volta, e il diario della composizione dice con quale via la tavola è uscita.
- **Il caso di prova 4** è quello di D-137, e il catalogo ha la **commutatrice a tre vie**
  (`switching-valve-3way`, funzione `circuit_switching`, famiglia **VCR**). Il documento
  pubblicato dell'impianto 4 e il confronto per il PM sono rigenerati con il grafo nuovo:
  43 pezzi il 9 settembre, **46** oggi.

**Le misure**

| | tavola 1 | tavola 2 |
|---|---|---|
| riempimento | 29,8 % → **45,1 %** | 50,1 % → **64,1 %** |
| copertura ingombro | 0,625 → **0,750** | 0,625 → **0,750** |
| curve | 4 → 4 | 5 → 5 |
| attraversamenti | 1 → 1 | 1 → 1 |
| squilibrio quadranti | 2,11 → **1,94** | 32,5 → **8,16** |
| larghezza occupata | 245 → **322,5 mm** | 257,5 → **315 mm** |

Tutt'e due dentro la finestra 45–65 %, con la copertura dell'ingombro che sale insieme al
riempimento (D-141) e **nessun peggioramento** su curve e attraversamenti.

**La suite**

Su `main` 10 rosse, 1470 verdi, 24 saltate, 11 xfailed. Qui le rosse sono **13**: il
criterio 13 del pacchetto **non è raggiunto**, e le tre in più sono tutte in
`tests/layout/test_stacchi_minimi_e_interasse.py`, sulle due fixture
`*_con_accumulo_combinato`. Due di loro non falliscono su un'asserzione: falliscono perché
la tavola non esce. Nessuna prova è stata spenta per far quadrare il saldo; il rapporto
§7.7 porta le cinque misure con cui ho provato a chiuderle.

**Che cosa resta aperto, e sta nel rapporto §7**

1. **D-060 e D-138 si contendono la stessa coordinata**, ed è una domanda al PO: fra due
   zone impilate e una strada di ritorno rettilinea, quale delle due vuole. È la sola cosa
   che la consegna toglie — una prova di `test_objective.py` — ed è dichiarata.
2. Due **corsie di catena di macchina** che si incrociano non le separa nessuna mossa di un
   pezzo solo: è ciò che ferma le tavole 4 e 5, e in altra forma la 3. Gli impianti che
   producono una tavola restano 1 e 2, come su `main`.
3. L'ordine di instradamento e il rango sono la stessa chiave, e con la gerarchia nuova
   quella chiave governa una classe molto più grande. I confini di rete finiscono lontani
   dal pezzo che servono, e nessun numero se ne accorge.

---

## ~~Consegna in revisione~~ — DRAW-013, **fuso** nella PR #44 (scritta dal DEV, 19 settembre 2026)

`DRAW-013 — la tavola si allarga tutta insieme, non tocca il bordo, e la distribuzione ha la
sua forma` è consegnato in una PR non fusa. **Parte dal ramo di `DRAW-012`**, non da `main`:
il primo commit del ramo è il merge di `17ff425` su `651310f`, da solo. Rapporto e artefatti:
`docs/collaudi/DRAW-013/`, con le tavole in PDF (D-146).

**Che cosa cambia nel motore**

- **`layout/dilate.py`** è nuovo: la **dilatazione proporzionale** della posa (D-142). Su
  ciascun asse una funzione monotona a tratti — pendenza 1 sui simboli, vuoti allargati di un
  fattore unico per foglio — scelta dopo che il disegno è risolto. Simboli della loro misura,
  nessun pezzo spostato rispetto agli altri, nessuna piega e nessun attraversamento in più.
- **Il margine di rispetto** (D-143) entra in tre posti: la **chiave di costo della posa**
  (prima del riempimento), il limite della dilatazione, e un rilievo di preflight nuovo,
  `DRAWING_TOUCHES_THE_BORDER`, che scatta solo su chi il bordo lo tocca **senza esserne
  autorizzato**.
- **La forma della distribuzione** (D-144): `highways.turns_of` conta le curve, e la strada
  che da un accumulo porta a un'utenza ne può fare **una, dichiarata** — che il diario non
  conta fra le cedute. L'invariante della retta intera resta per le autostrade fra le macchine
  di spina.
- **La guardia del riempimento è un divieto** e non più una soglia (D-141): un riempimento
  salito mentre la copertura scende si legge come quello dell'altra posa, e il caso lieve
  costa quanto il caso grosso.
- **Gli organi di servizio stanno addosso al pezzo che servono** (D-145), come **vincolo** di
  `is_valid` e non come voce di costo: D-139 non è toccata.
- **Lo stiramento del singolo tratto** resta, e il riempimento non lo può più comprare.

**Le due tavole**

| | tavola 1 | tavola 2 |
|---|---|---|
| margine dal bordo | 12,5 → **25,0 mm** | 17,5 → **25,0 mm** |
| curve / attraversamenti | 4/1 → 4/1 | 5/1 → 5/1 |
| riempimento | 45,1 → 42,9 % | 64,1 → 61,1 % |
| acqua fredda dal pezzo che alimenta | 40,0 → **20,0 mm** | 135,0 → 120,0 mm |
| fattore di dilatazione | 1,08 | 1,25 |

Gli impianti che producono una tavola restano **1 e 2**, gli stessi del ramo di partenza.

**La suite**

Ramo di partenza: **13 rosse, 1482 verdi**, 24 saltate, 11 xfailed — esattamente il
riferimento che il pacchetto dichiara, riprodotto in un worktree su `0a2b7fd` con il proprio
ambiente. Qui: **12 rosse, 1500 verdi**, 24 saltate, 11 xfailed. Il criterio 13 è **raggiunto**,
e le dodici rosse sono tutte sottoinsieme delle tredici: nessuna rossa nuova.

⚠️ La rossa che si chiude **non è quella che il criterio nomina**: resta rossa
`test_sulla_tavola_composta_nessuno_stacco_e_piu_lungo_del_minimo_senza_una_ragione`, e si
chiude invece `test_rami_di_servizio.py::test_nessuna_freccia_sui_rami_statici...`. Il rapporto
§7.7 misura che cosa costerebbe chiudere quella nominata: due tavole peggiori.

`ruff` pulito; `mypy` con i **due** errori che stanno già sul ramo di partenza, in un file che
questo pacchetto non tocca.

**Che cosa resta aperto, e sta nel rapporto §7**

1. **Il pettine di D-144 è bloccato dal simbolo del collettore**: `zone-manifold` dichiara
   `allowed_rotations_deg: [0]`, e per D-049 quel campo è un vincolo tecnico. **Domanda al
   PO**: un collettore di zona si può disegnare in verticale?
2. **Il margine di D-143 e la finestra di D-140 non stanno insieme sulla tavola 1**: portarla
   in finestra vuol dire tornare a 322,5 mm di ingombro e 13,75 mm dal bordo, cioè alla tavola
   che il PO ha bocciato. **Domanda al PO.**
3. **La griglia quantizza la dilatazione**: un vuoto cresce solo se `round(g·k) > g`, e su
   questi impianti i vuoti sono quasi tutti di uno o due passi. La dilatazione ha mosso 2,5 mm
   sulla tavola 1 e 10 mm sulla tavola 2.
4. **Il riempimento non sale «per dilatazione e non per altro»**, come §E si aspettava: la posa
   ha ancora la finestra nella chiave, perché D-140 e D-141 non si toccano. **Da decidere dal
   PM**, con i numeri del rapporto §7.6.
5. **§G ammette due letture del «vincolo dichiarato», e la più stretta disegna peggio.** Il
   rapporto §7.7 porta tre varianti misurate sulle tavole: quella consegnata, il tetto stretto,
   e il tetto stretto con l'attuazione del vincolo — che chiude la rossa del criterio 13 e
   porta l'acqua fredda della tavola 2 a 192,5 mm, peggio dei 135 del ramo di partenza. **Da
   decidere dal PM.**
6. **L'acqua fredda della tavola 2** resta a 120 mm dal bollitore: il confine sta al proprio
   minimo dal raccordo che lo regge, ed è la posa del gruppo a essere lontana. `place.py` è
   fuori perimetro.
7. **La tavola 4 non esce**, e non per il motivo che §D ipotizzava: `utenze` è posato a `x 365`
   dalla fase del tronco, cinque millimetri oltre l'area. Conto cella per cella in
   `docs/collaudi/DRAW-013/dopo/prova-4-perche-non-esce.txt`.
