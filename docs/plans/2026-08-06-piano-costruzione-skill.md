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
