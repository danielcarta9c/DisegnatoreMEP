# Piano di costruzione della skill, pezzo per pezzo

**Data:** 6 agosto 2026 — **rifatto sulla logica del grafo** su indicazione del PM
(D-096, D-097, D-098, D-099).
**Stato:** in corso. Un pezzo alla volta.
**Sostituisce** il piano di rilancio del 5 agosto (D-084) e la propria prima stesura del
6 agosto, che resta come storia: i suoi verdetti valgono e sono in appendice.

**Architettura di riferimento:** ADR 0005 e `docs/SKILL.md` §2.

---

## 0. Cosa è cambiato, e perché si riparte dal primo pezzo

La prima stesura di questo piano trattava tre oggetti diversi — un modello dell'impianto,
poi delle catene di pezzi, poi una geometria — e verificava il contenuto guardando un
disegno. Il PM ha corretto entrambe le cose:

> «Le regole degli accessori e componenti non li avrei testati facendo un disegno ma
> costruendo un albero. Il disegno è soprattutto il test per l'instradatore e il
> validatore, o per la skill finita.»
>
> «Penserei proprio a una sorta di grafo a punti come si fa con le strade. Ogni nodo ha un
> codice così riesci a creare un albero.»
>
> «Il grafo tanto parte sempre dalle stesse cose: i generatori di calore e l'acquedotto
> sono i punti di partenza, e da lì sviluppo la codifica dei nodi.»

Ne discende una cosa sola, ma cambia l'ordine dei pezzi: **il grafo è l'oggetto che
attraversa tutta la catena** (D-099), e quindi è il **primo** pezzo da costruire, non un
sottoprodotto degli altri. Tutto ciò che viene dopo lo legge e lo arricchisce; tutto ciò
che si approva, si approva leggendolo.

**Non si butta niente di ciò che è collaudato.** Il giudizio è sul pezzo, non sul file: il
vocabolario delle proprietà, già approvato, e il lavoro sulle regole, in correzione,
entrano nella nuova numerazione senza essere rifatti.

---

## 1. Le regole del gioco, valide per ogni pezzo

Sono le correzioni di metodo che il PM ha imposto. Nessun pezzo è «fatto» se ne viola una.

1. **Un pezzo alla volta** (D-092): il successivo si apre quando il precedente è collaudato
   e guardato.
2. **Criteri di accettazione come proprietà**, valide su qualunque impianto — «ogni attacco
   manutenibile ha la sua valvola» — mai come numeri di una tavola di prova. Vietato tarare
   una soglia su una fixture.
3. **Si verifica guardando, non contando** (D-088). Ogni prova asserisce la regola **dove
   la regola vive** — per attacco, per tratta, per nodo — e ogni pezzo si chiude guardando
   l'artefatto che produce.
4. **Regole generali, mai particolari** (D-090). Una regola scritta su misura di un
   componente è codice travestito da dato.
5. **Tre ruoli** (D-083): chi orchestra scrive i criteri prima, chi sviluppa esegue, un
   collaudo a contesto separato può respingere. Verdetti registrati in appendice.
6. **Gli esempi del PM non sono l'elenco** (D-089): per ogni difetto segnalato si cercano
   tutti i suoi simili e si chiudono insieme.
7. **La skill non progetta** (D-087). Un rilievo che le chiede di inventare un dato di
   progetto torna al progettista.
8. **Il contenuto si giudica sul grafo scritto, non sul disegno** (D-096). *Nuova.*

**Ogni pezzo consegna al PM un artefatto che lui possa leggere e bocciare.** Da qui in
avanti, per i pezzi di contenuto, quell'artefatto è **il grafo stesso**.

---

## 2. Cosa si tiene e cosa si rifà

| Pezzo | Stato | Decisione |
|---|---|---|
| Modello dell'impianto senza coordinate — nodi e archi | sano, collaudato | **si tiene, ed è il grafo** (G1) |
| Sigle dei nodi, codifica dalle sorgenti, lettura scritta | non esistono | **si costruiscono** (G1) |
| Vocabolario delle proprietà | approvato il 6 agosto | **si tiene**, si estende solo quando un pezzo lo richiede |
| Motore delle regole: caricamento, applicazione, tracciabilità, idempotenza, saturazione | sano | **si tiene** |
| **Contenuto** delle regole | in correzione dopo respingimento | **si chiude** (G3) |
| Assemblatore | non esiste | **si costruisce** (G4) |
| Meccanica della libreria dei simboli | sana | **si tiene** |
| Contenuto dei simboli: manca la distinzione in linea / su stacco | incompleto | **si completa** (G5) |
| Instradamento con la funzione di costo del PM | sano, il più difficile del progetto | **si tiene** |
| Cartiglio | mai disegnato, cornice aperta | **si costruisce** (G6) |
| Composizione: il disegno è una striscia, riempie il 39 % | limite vero | **si rifà** (G7) |
| Controlli di correttezza e preflight di qualità | sani e utili | **si tengono ed estendono** (G8) |
| Occhio terzo | protocollo scritto, una passata respinta | **si tiene**, diventa cancello di routine (G8) |
| Soglie tarate sulla tavola di prova | zavorra | **si buttano** (G8) |

---

## 3. I pezzi, in ordine di costruzione

L'ordine non è negoziabile: ciascuno ha bisogno del precedente.

### G1 — Il grafo e le sue sigle  ← **si riparte da qui**

**Perché per primo.** È l'oggetto che tutti gli altri leggono e scrivono. Finché non esiste
in forma leggibile, ogni pezzo successivo si può giudicare solo guardando un disegno — che
è esattamente l'errore che il PM ha corretto.

**Contratto.**

- Ogni pezzo dell'impianto è un **nodo con la propria sigla**; ogni tubo fra due pezzi è un
  **arco** col proprio fluido; un attacco su cui convergono più tubi è un **incrocio** e i
  suoi rami si numerano (D-097).
- Le sigle si assegnano camminando dalle **sorgenti dichiarate** — generatori di calore per
  i circuiti termici, acquedotto per il sanitario — nell'ordine in cui i pezzi si
  incontrano seguendo il fluido (D-098). Le sorgenti si riconoscono da proprietà
  dichiarate, mai da un elenco di nomi.
- **Una sigla sola per tutto il prodotto**: la stessa sul grafo, sulla tavola e sulla
  distinta. Chiude il rilievo dell'occhio terzo sui pezzi senza sigla.
- Il grafo si legge in due modi, entrambi generati: l'**elenco di nodi e archi**, e la
  **passeggiata** che parte da ogni sorgente, segue l'acqua e dice dove il circuito si
  richiude.

**Accettazione (proprietà).**

- Ogni nodo ha una sigla; nessuna sigla è ripetuta.
- Stesso impianto → stesse sigle, **qualunque sia l'ordine delle connessioni nel file di
  ingresso**. Chiude alla radice il rilievo R2 del collaudo di G3.
- Un anello si legge come anello: la passeggiata dice dove si chiude, non si interrompe.
- Il documento pubblicato **è** la rigenerazione corrente, e una prova lo inchioda.
- Nessun identificativo di codice, nessun nome di file, nessun inglese nel documento.

**Artefatto per il PM:** il grafo dell'impianto di accettazione — elenco dei nodi e
passeggiata. È il documento su cui giudicherà tutto ciò che viene dopo.

### G2 — Il vocabolario delle proprietà

**Approvato il 6 agosto 2026.** Resta com'è. Si estende solo quando un pezzo successivo
dimostra che una regola generale non è dicibile senza una proprietà nuova — è già successo
per «il fluido che il serbatoio tiene in serbo». Ogni estensione entra nel documento delle
proprietà.

### G3 — Le regole degli accessori, generali

**In correzione dopo respingimento del collaudo** (verdetto in appendice).

**Contratto.** Ogni regola parte dal **motivo per cui l'accessorio esiste**, si esprime
sulle proprietà di G2, e dichiara: quando si applica, quante volte, cosa propone, in che
punto della catena e perché, come si riconosce che c'è già, la fonte.

**Accettazione (proprietà, non numeri).**

- Le sei regole di intercettazione sono **una sola**, e vale anche sugli accessori che si
  dichiarano manutenibili.
- Su un impianto qualunque: ogni attacco di ogni cosa manutenibile ha la sua valvola; nulla
  di chiudibile fra una sicurezza e ciò che protegge; un vaso è isolabile solo con valvola
  bloccabile; ogni serbatoio può svuotare **l'acqua che tiene davvero in serbo**.
- Nessuna regola nomina un componente. Prova automatica.
- Rieseguire le regole su un modello completo non propone nulla.
- **Una regola che si applica ma non ha nulla da offrire lo dice**, non tace.

**Artefatti per il PM:** le schede delle regole, una per regola, da approvare una per una;
e il grafo di G1 **dopo** le integrazioni, dove si vede dove ciascuna è finita.

### G4 — L'assemblatore

**Contratto.** Da grafo più proposte alla **fila ordinata dei pezzi** su ogni arco, e per
ogni stacco la propria fila. Ordina risolvendo i **vincoli dichiarati** (D-094), non numeri
di priorità. Se due vincoli si contraddicono, **si ferma e nomina le due regole**.

**Accettazione.**

- La fila prodotta è leggibile sul grafo scritto, nodo per nodo.
- Gli stacchi hanno la propria fila, non sono disegnati dentro il simbolo (ritira D-071).
- L'ordine **non dipende dall'ordine alfabetico dei nomi delle regole**: è il difetto che
  il collaudo di G3 ha trovato, e qui si chiude alla radice.
- Su un impianto costruito apposta con due regole incompatibili, si ferma e le nomina.
- Deterministico: stesso grafo, stessa fila.

### G5 — La libreria dei simboli

Completare la distinzione **in linea / su stacco**, e dare al rubinetto bloccabile aperto
un segno distinto da quello comune: oggi sono identici sulla tavola, ed è un rilievo di
sicurezza aperto. Fonti come da D-081: norma dove copre, pratica di settore altrove.

### G6 — Il cartiglio

Cornice chiusa, cartiglio compilato, gerarchia dei testi conforme. Chiude tre rilievi
dell'occhio terzo.

### G7 — La composizione

Oggi il disegno è una striscia che riempie il 39 % del foglio, e con le integrazioni di G3
l'impianto **non entra più su un foglio ordinario**. Qui si rifà: sviluppo verticale,
riempimento uniforme, divisione in tavole col criterio del foglio abbastanza pieno (D-072).

### G8 — I validatori e il cancello

Preflight di qualità esteso alle proprietà di G1–G7, soglie tarate su fixture buttate,
occhio terzo come cancello di routine prima di ogni consegna.

---

## 3bis. La ripresa del 6 agosto, sera — i pacchetti di questa sessione

Tre pacchetti, nell'ordine chiesto dal PM. I criteri sono scritti **prima** che lo
sviluppo cominci (D-083).

### A — L'indirizzo dei nodi (D-105)

**Contratto.** Ogni linea idraulica ha sigla di famiglia e numero; ogni pezzo e' un nodo
numerato lungo la sua linea; le diramazioni prendono la lettera, gli stacchi il civico.
E' una **lettura** del grafo, come le sigle: si ricalcola sempre, non si scrive nel modello.

**Accettazione (proprieta').**

1. La famiglia di una linea si legge da una **tabella di dati** in `naming/`, su proprieta'
   dichiarate — il fluido della rete, il mestiere della sorgente da cui la rete parte, il
   verso (mandata o ritorno) — mai dal nome di una rete o di un componente. Una linea che
   la tabella non sa nominare ferma la generazione nominando il colpevole.
2. Ogni pezzo ha **un solo indirizzo** (`CP.01.N.02`), assegnato camminando dalle sorgenti
   nell'ordine di D-098. Stesso impianto → stessi indirizzi, qualunque sia l'ordine del
   file di ingresso (da provare con permutazioni).
3. **Innesto** (confluenza): la principale tira dritto e il raccordo e' un nodo suo; la
   secondaria e' una linea numerata a se' che **muore su quel nodo**. La principale e'
   quella il cui giro viene prima nell'ordine di D-098 — la prima sorgente vince.
4. **Diramazione** (ripartizione, deviatrice): la principale tiene il nome nudo, i rami
   prendono la lettera (`RP.01a`) nell'ordine della passeggiata. La principale e' quella
   che va verso la prima sorgente; dove nessun ramo va verso una sorgente, e' la prima via
   nell'ordine dei bracci dichiarati dal pezzo.
5. **Stacchi**: cio' che pende e' un **civico del nodo** (`CP.01.N.02.1`), numerato lungo
   la catena appesa; l'accessorio sull'attacco di servizio di una macchina e' un civico
   della macchina.
6. Le **sigle dei pezzi restano identiche** a prima del pacchetto: l'indirizzo convive con
   la sigla, non la sostituisce.
7. Il documento del grafo mostra: la **tabella delle linee** con la descrizione da→a
   («CP.01 — mandata primaria, da PDC-01 a ACC-01»); la **lettura per linea** — la fila
   dei nodi con indirizzo e sigla, i civici sotto il proprio nodo, innesti e diramazioni
   detti sul nodo dove accadono; gli anelli dichiarati come prima. Italiano, nessun
   identificativo interno.
8. I cinque grafi di prova e il grafo dell'impianto di accettazione **rigenerati dai
   generatori**; le prove che inchiodano i documenti alla rigenerazione restano verdi.
9. Suite completa, `ruff` e `mypy --strict` puliti. Nessun tocco a disegno, assemblatore,
   regole, modello.

### B — Il pezzo 1, «Capire»

**Contratto.** Le istruzioni dell'agente che legge il testo dell'ingegnere e costruisce il
grafo di prima stesura. File di testo, non programma (ADR 0005).

**Accettazione (proprieta').**

1. Le istruzioni dicono **cosa tirare fuori** (macchine, attacchi, tubazioni, reti,
   fluidi), **cosa non inventare mai** (quantita', taglie, accessori non detti, collegamenti
   non descritti), e **come dichiarare ogni ambiguita' come domanda** invece che risolverla.
2. Provate sui cinque testi originali del committente (`examples/prova/input/`): il grafo
   di prima stesura che ne esce si confronta con la lettura manuale, e ogni differenza si
   classifica — detto dal testo e perso; inventato; assunzione tacita della lettura manuale
   che le istruzioni trasformano in domanda.
3. Ogni pezzo del grafo di prima stesura risale a una frase del testo. Cio' che il testo
   non dice e' una domanda dichiarata, mai un'invenzione.
4. **Le letture manuali non si aggiustano** per far combaciare il confronto.

### E — Il regime della centrale: sotto i 35 kW le regole cambiano (D-106)

**Contratto.** Le buone pratiche delle piccole centrali, date dal PM e registrate in
D-106, diventano contenuto delle regole. Il **regime** — sotto o sopra i 35 kW — e' un
dato d'ingresso dichiarato dal progettista (il pezzo 1 lo chiede quando non e' detto),
mai calcolato dalla skill: la taglia non la decide lei (D-104).

**Accettazione (proprieta').**

1. Prima di scrivere qualunque regola, **il riscontro sulle fonti** (D-102, D-103): gli
   schemi Caleffi per centrali domestiche sotto i 35 kW — il quaderno *Idraulica 61* e'
   gia' acquisito — confermano o correggono ogni riga di D-106, e l'esito entra in
   `DOVE_VA_CIASCUN_ACCESSORIO.md` con la citazione. Una riga senza riscontro resta
   sulla sola autorita' del PM, e lo dice.
2. Sotto i 35 kW: sfogo aria e sicurezza **sul serbatoio, e stop**; niente separatore
   d'aria e niente termometro aggiunti (si usa quello integrato); filtro a Y **uno sul
   ritorno di ogni generatore**; defangatore **uno solo sul ritorno generale del
   primario**, prima della ripartizione; vaso di espansione **sul ritorno generale del
   primario**; filtrazione solo sul primario, salvo separazione netta con scambiatore.
3. Sopra i 35 kW: il contenuto attuale resta (Raccolta R), e i due regimi non si
   mescolano sullo stesso impianto.
4. Il catalogo impara a dichiarare **cio' che una macchina porta a bordo** (circolatore
   primario delle monoblocco); una regola non aggiunge cio' che la macchina dichiara di
   avere. Stessa dichiarazione che serve alla correzione C2.
5. Regole come dato, mai nomi di componenti; il regime si legge come ogni altra
   proprieta' dichiarata. Cinque grafi rigenerati; suite, ruff e mypy puliti; collaudo a
   contesto separato.

**L'audit dei livelli (6 agosto, notte) — il verdetto regola per regola, approvato dal
PM come base del pacchetto.** Ogni accessorio appartiene a uno di quattro livelli:
componente, attacco, ramo, rete. Il motore ne conosce tre; **manca il «tratto comune del
ramo idraulico»**, e le regole «per rete» ripiegano sul primo attacco di macchina — per
questo vaso, riempimento e manometro pendono oggi dal ramo della prima macchina invece
che dal ritorno generale. Da costruire: un ancoraggio dichiarabile «sul ritorno generale,
a monte della prima ripartizione», deterministico.

- **Corrette** (livello e molteplicita'): intercettazioni (per attacco); rubinetto al
  confine; ritegno sanitario; miscelatrice sanitaria; manometro (una per rete); gruppo
  di sicurezza sanitario; scarico del serbatoio (livello attacco giusto; resta C2
  sull'attacco sbagliato del bollitore).
- **Molteplicita' sbagliata**: separatore d'aria (per macchina → rete, e sotto i 35 kW
  e' lo sfiato sul serbatoio); defangatore (per macchina e perfino sui circolatori →
  uno, sul ritorno generale); termometro e sicurezza del generatore (per macchina →
  dipendono dal regime: sotto i 35 kW niente termometro e sicurezza sul serbatoio).
- **Livello giusto, platea o posizione da correggere**: filtro a Y (resta per
  generatore, esce dai circolatori, solo primario); vaso, riempimento, manometro
  (molteplicita' gia' giusta, posizione dal ramo della prima macchina al tratto comune).
- **Livello «ramo» oggi senza regole**: il ritegno sui rami di generatori in parallelo
  e' il caso d'uso; si scrive quando l'ancoraggio esiste, con la sua fonte.

Percorso concordato col PM: riscontro sugli schemi Caleffi gia' scaricati → regole
aggiornate come dato → collaudo separato → i cinque grafi rigenerati accanto agli
attuali, per il confronto.

### C — Il collaudo indipendente dei tre pacchetti «da collaudare»

Un attacco una tubazione (D-100), gli attacchi di servizio (D-101), l'assemblatore (G4):
costruiti e verificati da chi li ha scritti, e per D-083 non basta. Il collaudo rifa' le
prove **con criteri propri**, da contesto separato, sui contratti gia' scritti in questo
piano (§3, G4) e nelle decisioni D-100 e D-101. Verdetti in appendice.

---

## 4. Come si chiude un pezzo

1. L'orchestratore scrive i criteri di accettazione **prima**.
2. Uno o più sviluppatori eseguono.
3. Un collaudo a contesto separato verifica con prove **proprie** e può respingere.
4. Il verdetto si registra in appendice, respingimenti compresi.
5. L'artefatto arriva al PM da approvare o bocciare.

---

## Appendice — registro di esecuzione

| Pezzo | Sviluppo | Collaudo | Data | Note |
|---|---|---|---|---|
| **G3 — regole degli accessori** *(era P2)* | Sviluppatore P2 | **RESPINTO** al primo giro | 2026-08-06 | Diciannove regole diventano quattordici: le sei dell'intercettazione una sola, ancorata a «si smonta in esercizio» invece che alla macchina, e il vaso sanitario rientra nella regola del vaso di riscaldamento. Il collaudo indipendente ha confermato con prove proprie le tre proprieta' di accettazione — ogni attacco manutenibile chiudibile (46 controllati, zero scoperti), nessun organo chiudibile fra una sicurezza e cio' che protegge, vasi isolati solo da organi bloccabili — e ha respinto su due punti. **Primo:** lo scarico del bollitore e' finito sul ritorno del serpentino, cioe' scarica il circuito primario e non il volume del serbatoio, mentre la scheda per il PM dichiarava il bollitore coperto: un'affermazione falsa che il PM non puo' verificare. **Secondo:** il motore, quando il catalogo non ha un pezzo per quel fluido, **tace** e tratta la regola come non applicabile — un accessorio necessario puo' sparire senza che nessuno lo dica. Piu' un errore di conteggio nel limite di saturazione. Rimandato in sviluppo. |
| **G2 — vocabolario delle proprietà** *(era P1)* | Sviluppatore P1 | **RESPINTO** al primo giro, **APPROVATO** al secondo | 2026-08-06 | Undici proprietà chiuse e validate al caricamento. Respinto su correttezza impiantistica (ventilatore e VRV dichiarati manutenibili avrebbero fatto mettere valvole d'acqua su canali d'aria e linee frigorifere) e sul documento per il PM (consuntivo falso delle proprietà aggiunte). Corretto e approvato. Il collaudo ha poi dimostrato, aggiungendo un componente del prossimo pacchetto, che la guardia anti-travestimento avrebbe costretto a rinominare il vocabolario: dipendenza sciolta prima di P2. Artefatto per il PM: `docs/prodotto/PROPRIETA_COMPONENTI.md` | Rilievo R2 del collaudo — lo stesso impianto con le connessioni in ordine diverso dà un impianto diverso — riassegnato a **G1**, dove si chiude alla radice.
| **G1 — il grafo e le sue sigle** | Sviluppatore G1 | **APPROVATO** | 2026-08-06 | Il collaudo indipendente ha rifatto ogni prova con criteri più duri di quelli consegnati: permutazioni combinate di tubazioni, pezzi e reti invece delle sole tubazioni; confronto sul dump completo del grafo invece che sulle sole sigle; anelli verificati con una union-find sulla struttura invece che sul testo; nove semi di hash invece di quattro. Esito: sigle uniche su sei impianti, la sigla scritta a mano conservata e il numero prenotato, un solo grafo su 64 riordinamenti, quattro anelli dichiarati e quattro anelli veri, zero falsi. Ha inoltre provato a rompere il vincolo «da proprietà dichiarate, mai da nomi» dai dati: rinominando una famiglia le sigle seguono senza toccare il programma, togliendone una il caricamento fallisce **nominando il mestiere**, e rinominando il pezzo di catalogo in «Zqrflx modello 9» non cambia nulla. |
| **G3 — correzioni dopo il respingimento** | Sviluppatore G3 | **APPROVATO** sui tre punti | 2026-08-06 | Scarico del bollitore sul fluido che il serbatoio dichiara di tenere in serbo, verificato dal collaudo con una camminata propria che si ferma sugli organi di chiusura: `SC-02` è sull'acqua calda sanitaria e nessuno scarico tocca più i bracci del serpentino. La regola che non ha nulla da offrire parla in tutti e tre i posti — dossier, comando, grafo — non blocca, e il comando non può più stampare «modello già completo» sopra un pezzo mancante. Il limite di saturazione è corretto al confine esatto: otto passate produttive completano, nove si fermano nominando una regola vera. |
| **Riconciliazione delle due implementazioni** | Orchestratore | **RESPINTA**, poi **corretta** | 2026-08-06 | Due difetti, entrambi della classe per cui G2 e G3 erano già stati respinti — un'affermazione che il PM non può verificare. **Primo:** il documento delle regole mandava il PM a leggere «L'albero dell'impianto», cancellato dalla riconciliazione stessa, e gli prometteva la fila ordinata dei pezzi, che il grafo non dà ancora. Corretto: il rimando va al grafo, e ciò che il grafo non dà è detto. **Secondo:** il messaggio di commit `0f3bb63` afferma «Nessuna sigla e' cambiata» ed è **falso** — il collaudo ha eseguito la vecchia implementazione contro la nuova e ha trovato sei sigle diverse sull'impianto di accettazione, due su altri due impianti. Ciò che non è cambiato è la **tabella delle famiglie**: ventitré voci vecchie mappano una a una sulle nuove, nessun prefisso e nessun nome italiano modificato. I **numeri** sì, ed è legittimo — D-098 mette in conto la rinumerazione e la vecchia implementazione era quella respinta — ma la frase resta falsa nella storia del ramo, e questa riga la corregge a verbale. |
| **Difetto bloccante trovato dal collaudo** | Orchestratore | **corretto** | 2026-08-06 | Il generatore committato del catalogo di prova **cancellava** il fluido che i serbatoi dichiarano di tenere in serbo: rieseguirlo spegneva l'intera catena con un errore di caricamento. La correzione dello scarico aveva modificato a mano due file **generati** senza toccare il generatore che li genera. Nessuna prova presidiava il giro completo, e il docstring dello stesso generatore documenta un incidente identico avvenuto in passato: la regola del gioco n. 6 — cercare tutti i simili di un difetto — non era stata applicata. Corretto il generatore e aggiunta la prova che mancava: rieseguire un generatore di fixture non deve cambiare ciò che è committato. |
| **G1 bis — un attacco, una tubazione** *(D-100)* | Orchestratore | **da collaudare** | 2026-08-06 | Il PM ha corretto una diagnosi sbagliata: «un attacco porta tutte le sue tubazioni» non e' un vincolo di realta', e' una scorciatoia di modellazione. Il modello adesso rifiuta la seconda tubazione su un attacco, e dove due si incontrano c'e' un pezzo che le unisce con la propria sigla — confluenza o ripartizione, che sono due pezzi distinti perche' nella prima tutti e tre gli attacchi sono sul percorso e nella seconda no. Con questo si chiude alla radice il difetto per cui lo stesso impianto scritto in un altro ordine ne produceva tre: non c'e' piu' niente da scegliere. |
| **G3 bis — gli attacchi di servizio** *(D-101)* | Orchestratore | **da collaudare** | 2026-08-06 | Un volano a quattro tubi non ha quattro attacchi: i cataloghi dei costruttori (SRC-017, SRC-018) dichiarano anche sfiato, scarico e sede della sonda. Un accessorio che pende da uno stacco va su quell'attacco quando la macchina ce l'ha, e su una derivazione saldata sul tubo quando non ce l'ha — il bollitore lo scarico non ce l'ha, e infatti lo si svuota dall'ingresso freddo. Chiuso il debito che D-094 aveva congelato e che il codice non aveva mai tolto: nove accessori dichiaravano di pendere da un tubo e avevano un ingresso e un'uscita. |
| **G4 — l'assemblatore** | Orchestratore | **da collaudare** | 2026-08-06 | Costruito. Ogni regola dichiara rispetto a quali **mestieri** il proprio pezzo viene prima o dopo, e un pezzo puo' dichiarare di stare **attaccato alla macchina**; il programma ordina su quei vincoli e, se si contraddicono, si ferma nominando le due regole. Riordina solo cio' che le regole hanno aggiunto, e muove ogni accessorio col proprio blocco di valvole. Lavora **dentro** il ciclo di completamento: rimettere in fila puo' scoprire un attacco che era coperto solo perche' un pezzo stava dove non doveva, ed e' successo davvero. **Non e' stato collaudato da un contesto separato**, e per D-083 non e' «fatto». |
| **Ricerca sulle fonti, e il suo eccesso** *(D-102, D-103, D-104)* | Orchestratore | **corretta dal PM** | 2026-08-06 | Tre domande sugli attacchi delle macchine erano state girate al PM: hanno risposta nei cataloghi, e il PM stesso ha avvertito che la sua risposta poteva essere sbagliata. Acquisite due fonti e scritto `docs/prodotto/DOVE_VA_CIASCUN_ACCESSORIO.md`. **Poi l'errore opposto:** da un rigo della Raccolta R era stata dedotta la regola «con due generatori due vasi di espansione», piu' la tre vie al posto del rubinetto bloccabile e lo spostamento del manometro. Il PM: «non diventare un progettista, non devi trasformare il progetto input dell'ingegnere». Tutte e tre ritirate. Resta la parte utile — **dove** va un pezzo che comunque si disegna — e il documento porta il confine in testa. |
| **I cinque impianti di prova** | Orchestratore | **consegnati al PM** | 2026-08-06 | I cinque testi del committente passano per lettura, regole e assemblatore. Nove famiglie di pezzi aggiunte come **dato**, nessuna riga di motore toccata. La lettura dei testi e' fatta a mano e dichiarata tale: e' il pezzo 1 della skill, che non esiste ancora. Grafi in `docs/prodotto/grafi-di-prova/`. |
| **C-fix — le correzioni dei difetti del collaudo** | Orchestratore | **C1, C3, C4 corretti e verdi sulle prove del collaudo · C2 progettato, aperto** | 2026-08-06 (sera) | **(C1)** Gli ancoraggi si scelgono in ordine di nome — i membri di ogni rete e le reti stesse — mai nell'ordine del file: il corredo di rete non migra piu' permutando l'ingresso, e le prove di determinismo del collaudo passano. **(C3)** Uno stacco che vorrebbe una derivazione su un fluido per cui il catalogo non ha il raccordo diventa un **punto aperto** al momento della proposta, invece di far crollare l'applicazione a meta' catena. **(C4)** Due pezzi che dichiarano entrambi «attaccato alla macchina» fermano l'assemblatore nominando le due regole. Le prove del collaudo sono **adottate come regressione** in `tests/collaudo/` (28 verdi), con le due prove che il giudizio aveva respinto come difetti di prova corrette a verbale. **(C2, aperto e progettato):** lo scarico del bollitore va sull'ingresso freddo (SRC-017, SRC-018, D-101) e oggi finisce sull'uscita calda. La correzione senza euristiche fragili richiede una dichiarazione di catalogo nuova — **da quale attacco la riserva si riempie** — e la regola dello scarico che posa la derivazione li'; tocca lo schema del catalogo, i dati delle voci con volume proprio e il loro generatore di fixture. La prova del collaudo resta parcheggiata col motivo scritto e torna verde con quella correzione. |
| **A — l'indirizzo dei nodi (D-105)** | Orchestratore | **costruito, da collaudare** | 2026-08-06 (sera) | **Deviazione registrata prima di eseguire:** lo sviluppatore separato e' stato interrotto dal limite di spesa prima di scrivere qualunque file; ha sviluppato l'orchestratore sui criteri di §3bis-A. Costruito: la lettura delle linee (`CP.01`, `RP.01a`, `CP.01.N.02`, civici degli stacchi), le famiglie di linea come dato in `naming/lines.json`, il documento del grafo per linea, i cinque grafi e il grafo di accettazione rigenerati. Ventisette prove nuove, fra cui l'invarianza degli indirizzi su ogni permutazione dell'ingresso e le regole della strada del PM pinnate testualmente. Durante lo sviluppo l'orchestratore ha trovato e corretto due difetti propri (il ricircolo che rubava il nome alla mandata sanitaria; il pari-merito fra reti con la stessa sorgente deciso dall'ordine del file). **Per D-083 non e' «fatto»**: manca il collaudo a contesto separato, primo lavoro della prossima sessione. |
| **B — il pezzo 1, «Capire»** | Sviluppatore B + cinque agenti in camera pulita | **costruito e provato, da collaudare** | 2026-08-06 (sera) | Le istruzioni sono in `skill/capire/` (ISTRUZIONI.md, CONSEGNA.md). Provate in camera pulita sui cinque testi originali, con agenti freschi che non hanno visto ne' letture manuali ne' documentazione: **quattro impianti su cinque letti in modo identico alla lettura manuale, arco per arco**; il quinto diverge solo dove il testo era ambiguo, con ogni divergenza dichiarata — verbale completo e classificazione in `skill/capire/PROVA-2026-08-06.md`. Le letture manuali **non sono state toccate**. Il quinto agente e' stato interrotto dal limite di spesa dopo la consegna dei file, prima del rapporto. Resta dovuto il collaudo a contesto separato, e il giro di correzioni alle istruzioni raccolto dai rapporti degli agenti (ogni correzione impone una prova nuova con un agente nuovo). |
| **Deviazione registrata — 7 agosto, ripresa** | Orchestratore | **registrata prima di eseguire** | 2026-08-07 | Il pacchetto E (§3bis-E) viene sviluppato **dall'orchestratore**, non da uno sviluppatore separato: nelle due sessioni precedenti gli agenti separati sono morti a meta' lavoro per limite di spesa dell'account, ed e' il precedente gia' registrato per D-105. I due collaudi dovuti — l'indirizzo dei nodi (§3bis-A) e il pezzo 1 (§3bis-B) — partono **subito e in parallelo** come agenti a contesto separato su copie isolate del repository, prima che lo sviluppo del pacchetto E tocchi qualunque file: giudicano lo stato committato, non il lavoro in corso. Il collaudo del pacchetto E seguira' a sviluppo finito, a contesto separato anch'esso. La domanda del regime nel pezzo 1 («sotto o sopra i 35 kW?», D-106) non si aggiunge alle istruzioni in questo pacchetto: ogni modifica alle istruzioni impone una prova nuova in camera pulita, e va nel giro di correzioni del pezzo 1 gia' in coda. |
| **C — collaudo indipendente di D-100, D-101 e G4** | Collaudo a contesto separato | **D-100: APPROVATO sulla lettura, RESPINTO sulla catena completata · D-101: RESPINTO · G4: RESPINTO** | 2026-08-06 (sera) | **Deviazione registrata:** il collaudatore indipendente ha scritto 29 prove proprie (1.179 righe, tre file) ed e' stato interrotto dal limite di spesa dell'account prima del verdetto; l'orchestratore ha eseguito le sue prove cosi' come lasciate e ha giudicato le rosse una per una. Esito: 22 verdi, 7 rosse, di cui **4 difetti veri del prodotto** e 3 difetti delle prove. **(C1)** La saturazione non e' invariante all'ordine del file: permutando l'ingresso, il corredo di rete — riempimento, vaso, manometro, filtro, defangatore — migra dal ritorno della prima pompa di calore a quello della seconda, e la derivazione dello scarico cambia tubazione (`primary_out`/`secondary_out`). Viola «stesso impianto, stesso grafo». **(C2)** Lo scarico del bollitore e' saldato sull'uscita dell'acqua calda sanitaria; le fonti gia' acquisite (SRC-017, SRC-018, e il testo stesso di D-101) dicono che si svuota **dall'ingresso freddo**. La regola «sul fluido tenuto in serbo» sceglie il tubo sbagliato. **(C3)** Un catalogo senza raccordo di derivazione per un fluido fa **crollare il caricamento dell'intera catena** invece di produrre un punto aperto quando e solo quando una regola ne ha bisogno. **(C4)** Due regole che dichiarano entrambe «fra me e la macchina non ci va nessun altro pezzo» sullo stesso attacco **non fermano l'assemblatore**: la fila esce in silenzio con uno dei due vincoli falso (il ramo di `_sorted` che separa chi sta attaccato alla macchina non scatta quando lo dichiarano tutti). Le tre rosse respinte come difetti di prova: la bloccabile del vaso sta nella fila **dello stacco** (che e' il contratto, non una violazione); la pretesa di due valvole dedicate per accessorio (la valvola condivisa fra filtro e defangatore e' la convenzione approvata in G3: ogni **attacco** chiudibile, non due valvole per pezzo); un'asserzione gemella della prima. Le prove del collaudo sono conservate e vanno adottate come regressione insieme alle correzioni. |
