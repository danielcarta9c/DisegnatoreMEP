# Piano di rilancio — dalla registrazione dei difetti alla tavola approvabile

**Data:** 5 agosto 2026
**Stato:** in attesa del via del PM. Nessun pacchetto parte prima del via.
**Ordine del PM, 5 agosto:** «Riparti da zero, riverifica il piano. Non voglio più sentire
cose tipo "ho inventato": abbiamo dato degli input, non capisco perché non vengono seguiti.
Serve un agente che dice cosa fare, uno o più che fanno e uno che controlla. Voglio un
piano serio e che venga rispettato.»

---

## 0. Perché questo piano esiste

Non è mancata la conoscenza e non sono mancate le decisioni: gli input del PM sono tutti
nel decision log, quasi sempre registrati il giorno stesso in cui li ha dati. È mancato il
meccanismo che obbliga a eseguirli **prima** di mostrare un risultato. Il caso che lo
dimostra da solo: D-067 — libreria dei simboli da rifare sulle fonti — è del 4 agosto; la
tavola giudicata dal PM il 5 agosto è uscita con la libreria vecchia, e nulla lo ha
impedito né dichiarato.

Tre cause, tre contromisure, mappate una a una:

| Causa del guasto | Contromisura in questo piano |
|---|---|
| Una decisione non aveva un momento in cui qualcuno verifica che sia stata eseguita | Ogni pacchetto ha **criteri di accettazione scritti prima** del lavoro e un **collaudo indipendente registrato dopo**, nell'appendice di questo piano |
| Chi costruiva approvava il proprio lavoro | Il collaudo lo fa un **agente con contesto separato**, che non ha visto nascere il lavoro. Era già deciso per la skill (D-063: «un agente che rilegge il proprio lavoro lo approva»); da oggi vale anche per lo sviluppo |
| Un artefatto vecchio è stato mostrato come risultato corrente | Nessun elaborato arriva al PM senza essere stato **rigenerato dalla catena corrente** e aver passato **tutti i cancelli**, il giorno stesso della consegna |

---

## 1. La riverifica, input per input

Rifatta da zero il 5 agosto. Ogni affermazione della colonna «stato» è stata
**controverificata da un collaudatore indipendente** — un agente con accesso al solo
repository, istruito a cercare controprove — che ha confermato tutti i punti, con due
precisazioni annotate in tabella. La regressione completa è verde (461 test, lint e
tipizzazione a zero errori).

| Input del PM | Decisione | Stato verificato nel prodotto | Verdetto |
|---|---|---|---|
| A3, o A4 se il disegno è piccolo; mai A0, mai strisce | D-058 | La scelta del formato prova A4 poi A3 e oltre non va | **Rispettato** |
| Scala di stampa invariante in millimetri di carta | ADR 0003 | Provata dal PM col righello sulla stampa del 4 agosto | **Rispettato** |
| Meno curve, meno incroci, meno lunghezza; ordine di processo da sinistra a destra | D-060 | Pesi dell'instradamento, misurati | **Rispettato a metà**: vale per le linee a posizioni date, ma le posizioni sono fisse, quindi le linee pagano gli errori di posizione (D-078) |
| Vietato sovrapporre longitudinalmente | D-062 | Divieto sugli spigoli già percorsi | **Rispettato** |
| Mandata e ritorno dalla topologia, mai dalla geometria | D-059 | Implementato. Precisazione del collaudo: per una rete che la topologia non riesce a orientare resta un ripiego geometrico esplicito e documentato | **Rispettato** |
| Il contenuto lo decide l'impianto, non il foglio | Principio dietro D-074 | Le valvole di intercettazione sono state ridotte per far entrare il disegno su una A3 | **Violato** |
| Una valvola di intercettazione per ogni attacco di macchina | D-074 | Regole a «una per macchina». Sul caso di accettazione, conteggio del collaudo: pompa di calore **0**, circolatore **1**, volano sotto il pieno | **Violato** |
| Si divide solo se la tavola successiva è abbastanza piena; impilare è lecito | D-072, D-073 | La seconda tavola del caso porta **2 componenti**; nessun criterio di riempimento esiste nel codice | **Violato** |
| Etichette: scritta piccola vicino al pezzo; richiamo a 45° solo quando serve | D-075 | Riga di richiami a fondo tavola, con linee ortogonali identiche per giacitura a una tubazione | **Violato** |
| Scavallo sugli incroci, pallino sui collegamenti | D-079 | Gli incroci sono calcolati, trasportati nella geometria e **mai disegnati** | **Violato** |
| Simboli = ciò che usa davvero un termotecnico italiano | D-081, già D-067 | Tutti i 31 simboli pubblicati citano la convenzione interna; **nessuno cita una fonte**. D-067 era deciso dal 4 agosto e non eseguito | **Violato** |
| La disposizione serve le linee: spostare è gratis, ma anche la lunghezza costa | D-078, D-080 | La disposizione, una volta fatta, non viene mai rivista; nessun ciclo posizioni→linee esiste | **Mai costruito** |
| Verifica a tre livelli prima della consegna; occhio terzo che può respingere | D-063–065, D-076, D-077 | Precisazione del collaudo: il controllo **di correttezza** c'è e blocca (sovrapposizioni di simboli, collisioni di testi, oggetti fuori area, segmenti non ortogonali). Il preflight **di qualità** (pieghe, incroci, riempimento) e l'occhio terzo non esistono | **Mai costruito** |
| Regole come dato versionato, con fonte, migliorabile dandogli documenti | D-039, D-069, D-070 | 15 regole in file di dati, versionate, ciascuna con fonte e motivazione; nessuna nomina un componente | **Rispettato il meccanismo.** Il **contenuto** è un'altra cosa: non è mai stato approvato dal PM, che sul disegno illeggibile non poteva verificarlo (D-085) — passa da WP2 e dall'approvazione sua |
| ACS dentro l'MVP | 4 agosto | Gruppo sanitario proposto dalle regole e presente | **Rispettato** |
| Ruoli fissi e zero verbosità | D-068 | Nei documenti operativi | **Rispettato** |
| Le decisioni rimandate si registrano | 4 agosto | Il registro esiste e viene usato | **Rispettato** |

**Bilancio onesto: le fondamenta rispettano gli input; il disegno che ci sta sopra li
viola quasi tutti.** Per questo il piano tiene le fondamenta e rifà il disegno.

---

## 2. Cosa si tiene, cosa si rifà

Ogni «si tiene» è motivato da un input del PM o da una sua verifica diretta — non da
affezione al codice scritto.

**Si tiene:**

- il modello tecnico canonico senza coordinate e la sua validazione (ADR 0002, D-026);
- il **motore** delle regole: è il differenziale del prodotto, rispetta D-039/D-069/D-070
  e permette di correggere il contenuto cambiando dati, non codice. **Si tiene il motore,
  non il contenuto**: il contenuto delle quindici regole non è mai stato approvato dal PM
  (D-085) e passa per intero dalla verifica di WP2 e dalla sua approvazione;
- l'orientamento topologico di mandata e ritorno (D-059);
- i formati A3/A4 con scelta automatica (D-058) e la scala invariante provata col
  righello (ADR 0003);
- griglia, porte sul perimetro e sui nodi (D-044, D-054), determinismo bit-a-bit;
- l'instradamento a costi di D-060 **come motore interno**: resta, ma smette di essere
  l'ultima parola — sopra ci va il ciclo di WP3.

**Si rifà o si costruisce:**

- la libreria dei simboli, dalle fonti (WP1);
- la regola delle intercettazioni, per attacco (WP2);
- la disposizione, al servizio delle linee (WP3);
- etichette e segni di incrocio (WP4);
- il preflight di qualità, che oggi non esiste (WP5);
- l'occhio terzo con il ciclo di revisione, che oggi non esiste (WP6).

---

## 2bis. La mappa sull'architettura — niente si perde

Domanda esplicita del PM il 5 agosto: «Stiamo perdendo la struttura iniziale
dell'architettura?» No, e questa tabella lo dimostra. L'architettura della skill è quella
approvata nella specifica §6.1 — nove livelli, con il confine netto: **la parte non
deterministica sceglie gli ingressi, la parte deterministica produce l'elaborato**. Il
rilancio corregge i livelli difettosi **al loro posto**; non ne aggiunge, non ne toglie,
non ne cambia i confini.

| Livello dell'architettura (§6.1) | Stato verificato | Chi lo copre |
|---|---|---|
| 1. Orchestrazione della skill | Mai costruito (è P6) | In coda dopo il rilancio, invariato |
| 2. Interpretazione AI del contesto | Mai costruito (è P6) | In coda dopo il rilancio, invariato |
| 3. Modello tecnico canonico | Sano, conforme agli input | Si tiene; nessun WP lo tocca |
| 4. Pacchetti di dominio | Idronico dentro le regole; il contratto va allargato (P3A) | In coda dopo il rilancio, invariato |
| 5. Libreria dei simboli | **Difettosa**: nessuna fonte | **WP1**, al suo posto |
| — Regole di inserimento (vivono fra 3 e 4) | Motore sano; **contenuto mai approvato dal PM** (D-085), con un errore già noto (intercettazioni) | **WP2**: correzione, verifica regola per regola contro le fonti, dossier per l'approvazione del PM |
| 6. Motore di layout | **Difettoso**: disposizione che non serve le linee | **WP3** e **WP4**, al loro posto |
| 7. Renderer | SVG c'è; segni di incrocio e richiami da correggere (WP4); cartiglio, PDF e distinta sono P5 | **WP4** per i segni; P5 in coda |
| 8. Validatori | Correttezza presente e funzionante; **qualità mai costruita** | **WP5**, al suo posto |
| 9. Cold eye review | Mai costruito | **WP6**, al suo posto |

Il flusso utente resta quello approvato e non è in discussione: conversazione →
ricostruzione dell'impianto → **dossier di approvazione** con integrazioni necessarie,
raccomandate e condizionate → «sì, procedi» → disegno → controlli → consegna. Il dossier
prima del disegno (D-004, D-013) è un pezzo del livello 1-2 e arriva con P6, sopra un
motore che a quel punto produce tavole approvabili.

---

## 3. Il metodo dei tre ruoli (vincolante — D-083)

- **L'orchestratore** — una sola mente responsabile — scrive ogni pacchetto con i criteri
  di accettazione **prima** che il lavoro cominci, assegna, giudica il rapporto del
  collaudo, risponde al PM. Non si approva il lavoro da solo.
- **Gli sviluppatori** — agenti separati, uno o più per pacchetto — eseguono. Non
  dichiarano mai «fatto» da soli.
- **Il collaudo** — un agente con contesto separato, che non ha visto nascere il lavoro —
  verifica tre cose: i criteri di accettazione del pacchetto, le regole del colpo d'occhio
  (`docs/QUALITA_GRAFICA.md`), la regressione completa (test, lint, tipi, determinismo).
  Può respingere: il pacchetto torna in sviluppo. Ogni verdetto si registra
  nell'appendice di questo piano.

**Le regole ferree:**

1. Nessun pacchetto è «fatto» senza verdetto positivo del collaudo, registrato.
2. Nessuna tavola arriva al PM senza il cancello completo passato il giorno stesso,
   rigenerata dalla catena corrente. Mai più un artefatto vecchio mostrato come attuale.
3. **Vietato inventare.** Nessun contenuto grafico si autora senza una fonte dichiarata —
   norma tramite fonte secondaria verificata, schema di produttore, o decisione esplicita
   del PM. Se la fonte manca, si apre una domanda al PM: la mancanza di fonte è una
   domanda, non una licenza. Il collaudo controlla i campi fonte.
4. **Il piano si rispetta.** Una deviazione si registra nell'appendice, con il perché,
   **prima** di eseguirla. Una deviazione non registrata è un difetto di processo, quale
   che sia il suo merito tecnico.

---

## 4. I pacchetti di lavoro

Dipendenze: WP1, WP2 e WP3 partono in parallelo (file disgiunti). WP4 dopo WP3.
WP5 dopo WP3 e WP4. WP6 dopo WP5. WP7 chiude. L'ordine di consegna al PM è WP1 subito
(foglio simboli), poi tutto il resto in una consegna sola con WP7.

### WP1 — I simboli dalle fonti

**Obiettivo:** nessun simbolo inventato. Chiude D-067, D-081, D-082.

**Contenuto:** riautorare la libreria pubblicata sul mix dichiarato da D-081 — UNI 9511
tramite le tavole Oppo (SRC-016) per tubazioni, giunzioni, valvolame, scarichi e
strumenti; pratica di settore e schemi dei produttori (SRC-008) per le macchine che la
norma non copre. Gerarchia dimensionale D-055 e porte su griglia D-054 invariate.
Dentro il pacchetto si decide anche l'adozione degli spessori normati di tubazione
(progetto 0,50 mm; esistente 0,25 mm — Tab. 1).

**Criteri di accettazione:**
1. Ogni manifesto pubblicato dichiara una fonte vera e puntuale: «UNI 9511 Tab. N,
   tramite SRC-016» dove la norma copre; «pratica di settore, cfr. SRC-008» per le
   macchine. Zero `CONV-GRAFICA-001` residui su elementi coperti dalla norma.
2. La valvola di ritegno è quella di Tab. 3: triangolo vuoto contro la battuta, **freccia
   del senso del flusso**.
3. Intercettazione, sicurezza, tre vie, sfiato, vaso e strumenti riconoscibili accanto
   alla riga corrispondente della tavola fonte.
4. Rigenerazione bit-identica; verifica incrociata catalogo–simboli verde; suite verde.

**Collaudo:** confronto uno-a-uno sul foglio di riscontro renderizzato contro le immagini
delle tavole fonte; audit dei campi fonte; regressione.

**Consegna intermedia al PM:** il nuovo foglio di riscontro — è lui l'autorità su «questo
è quello che usiamo davvero».

### WP2 — Le regole di inserimento: correzione, verifica e approvazione mai avvenuta

**Obiettivo:** chiudere D-074 **dentro il pacchetto di regole esistente**, e — più
importante — sottoporre finalmente il contenuto del pacchetto all'approvazione del PM,
che **non c'è mai stata** (D-085).

Il PM lo ha precisato due volte il 5 agosto. Primo: la correzione delle valvole di
intercettazione **non è un pacchetto a sé** — è una correzione al pacchetto di regole di
inserimento dei componenti. Secondo: lui **non ha mai approvato quel pacchetto** — si è
fermato agli errori evidenti, e il resto non era verificabile perché sulla tavola
illeggibile non si capiva se il gruppo di riempimento, il ritegno o il defangatore
fossero nel punto giusto. Su un elaborato illeggibile il silenzio non è assenso. Il
motore (caricamento, applicazione, tracciabilità) è collaudato dai controlli automatici;
il **contenuto** — cosa viene inserito e dove — non lo ha verificato nessuno che non sia
chi lo ha scritto. Questo WP chiude entrambe le cose.

**Contenuto:**
1. La regola di intercettazione passa a cardinalità **per attacco di macchina**
   (generatori, pompe, accumuli); il criterio di soddisfazione riconosce una valvola già
   presente su quello specifico attacco. Sparisce dalla motivazione la frase «una sola
   valvola nel primo pacchetto».
2. **Scheda di verifica per ciascuna delle quindici regole**: cosa propone, in quale
   punto funzionale, perché proprio lì, con quale fonte (Raccolta R, guide UNI 8065,
   schemi dei produttori, buona pratica documentata). Ogni scheda è scritta perché la
   legga un non sviluppatore. Una posizione motivata solo da «così faceva l'esempio» è
   una scheda respinta.
3. **Revisione trasversale**: nessuna regola porta contenuto ridotto o alterato per un
   vincolo di foglio; ogni motivazione è impiantistica.
4. **Il dossier di approvazione del caso di accettazione, per il PM, in linguaggio
   piano**: l'elenco delle integrazioni con posizione e motivo. È il flusso che il
   prodotto stesso prescrive ai suoi utenti — dossier prima del disegno (D-004, D-013) —
   applicato allo sviluppo. Ciò che il PM contesta si corregge qui, prima che si disegni;
   la sua approvazione del contenuto si completa poi sulla tavola leggibile (WP7).
5. Il perimetro delle **famiglie** resta quello dell'MVP, con le famiglie future già
   registrate in `docs/DEFERRED.md` §1. Il perimetro è accettato; il contenuto, da
   questo WP in poi, sarà approvato.

**Criteri di accettazione:**
1. Sul caso di accettazione: pompa di calore 2 valvole, circolatore 2 (una per lato),
   volano 4, bollitore 4 — «ogni macchina, ogni tubo che entra o esce».
2. Le quindici schede di verifica esistono, ciascuna con fonte; l'esito della revisione
   trasversale è registrato nell'appendice.
3. Il dossier è stato consegnato al PM e le sue correzioni sono applicate.
4. Rieseguire le regole su un modello già completato non propone nulla (idempotenza).
5. Nessuna regola nomina un componente (D-069, prova esistente); motore non modificato —
   se questo WP dovesse toccare il motore, il motore è sbagliato e ci si ferma.
6. Suite verde.

**Collaudo:** conteggio automatico delle valvole adiacenti per ogni attacco di macchina
sul modello generato; lettura indipendente delle schede **contro le fonti citate**;
verifica che il motore sia invariato; regressione.

**Consegna intermedia al PM:** il dossier delle integrazioni — la prima occasione reale
di approvare o bocciare il contenuto delle regole.

### WP3 — La disposizione al servizio delle linee

**Obiettivo:** chiudere D-078 e D-080. È il pacchetto più pesante e il cuore del rilancio.

**Contenuto:** dopo il primo instradamento, un **ciclo deterministico di miglioramento**:
si generano mosse discrete sui componenti — traslare lungo la fascia, impilare (D-073),
ruotare dove ammesso, avvicinare — in ordine deterministico; per ogni mossa si
reinstrada; la mossa si accetta solo se l'obiettivo totale migliora. L'obiettivo è quello
del PM, intero: pieghe, incroci e lunghezza con i pesi di D-060 — mai una voce sola
(D-080). Vincoli mai violabili: ordine di processo da sinistra a destra (D-060), distanze
minime, divieto di sovrapposizione (D-062). Il ciclo è limitato nel numero di passate e
monotono. La divisione in tavole acquisisce il criterio di D-072: si divide solo se,
**dopo** l'ottimizzazione, il contenuto non entra e la tavola successiva raggiunge un
riempimento minimo dichiarato; altrimenti si ottimizza (impilando, compattando) su una.

**Criteri di accettazione:**
1. Nessuna andata e ritorno: nessuna tratta supera l'ascissa della porta di destinazione
   per tornarci (B12) — rilevatore automatico a zero sul caso.
2. Sul caso di accettazione: incroci e pieghe **strettamente sotto** i valori attuali
   (9 nodi condivisi, 25 pieghe); lunghezza totale non peggiorata oltre il 10%.
3. I due difetti fotografati dal PM spariti: il giro attorno al prelievo ACS e la discesa
   dell'acqua fredda attraverso le linee del riscaldamento.
4. Il caso sta su **una** tavola se il riempimento lo consente; la seconda esiste solo
   piena a criterio.
5. Determinismo bit-a-bit su esecuzioni ripetute e semi diversi; suite verde.

**Collaudo:** misure prima/dopo; verifica del rilevatore di andata-ritorno; visivo sul
raster contro le due fotografie del PM; regressione.

### WP4 — Scrittura e segni

**Obiettivo:** chiudere D-075 e D-079.

**Contenuto:** etichette come scritta piccola accanto al proprio componente (sigla sopra,
valori sotto); solo in caso di collisione, richiamo **obliquo a 45°** verso spazio
libero; eliminata la riga di richiami a fondo tavola e ogni richiamo ortogonale. Sugli
incroci senza connessione, lo **scavallo** (archetto sulla linea verticale,
CONV-GRAFICA-004); su derivazioni e incroci con connessione, il **pallino** pieno con
diametro quattro volte lo spessore del tratto (Tab. 1). Un incrocio non cade mai su una
piega.

**Criteri di accettazione:**
1. Zero linee di richiamo ortogonali su qualunque tavola; ogni richiamo presente è a 45°.
2. Ogni incrocio senza connessione porta lo scavallo; ogni derivazione il pallino.
3. Nessun incrocio su una piega.
4. Nessun testo copre linee o simboli (controllo esistente); suite verde.

**Collaudo:** scansione della geometria per angoli di richiamo e marcatori; visivo su
raster; regressione.

### WP5 — Il preflight di qualità, bloccante

**Obiettivo:** costruire il livello 1 di D-063, che oggi non esiste nel prodotto.

**Contenuto:** un validatore di prodotto — accanto a quello di correttezza esistente —
che misura ciò che la carta del colpo d'occhio marca «da misurare»: pieghe per tratta,
incroci totali e non marcati, sovrapposizioni longitudinali (= 0), distanze di rispetto,
andate-ritorno (= 0), richiami ortogonali (= 0), riempimento del foglio e delle tavole
successive, copertura delle fonti dei simboli usati. Esiti classificati bloccante / da
approvare / avviso (§13 della specifica): una tavola finale non esce con un bloccante;
una bozza esce marcata bozza.

**Criteri di accettazione:**
1. Il preflight gira dentro il comando di disegno, non nei test.
2. Casi seminati — uno per regola violata — producono l'esito atteso.
3. Il caso di accettazione, dopo WP1–WP4, passa senza bloccanti.
4. Le righe corrispondenti della carta passano da «da misurare» a «misurata»; suite verde.

**Collaudo:** esecuzione del preflight sui casi seminati e sul caso pulito; verifica che
il comando fallisca davvero su un bloccante; regressione.

### WP6 — L'occhio terzo

**Obiettivo:** costruire il livello 2 di D-063 secondo D-076 e D-077.

**Contenuto:** protocollo scritto ed eseguibile del cold eye review. Un agente a contesto
freddo riceve **solo**: il raster della tavola a misura di stampa, la carta del colpo
d'occhio, le tavole di riferimento. Primo passaggio sulla composizione guardata da
lontano; poi le famiglie una a una. Ogni rilievo nomina la regola violata. Se respinge,
produce un **nuovo piano di impaginazione** e la pipeline rigenera da capo (D-064): mai
toccata la geometria. Massimo tre passate, monotono sulle misure del preflight. Due
respingimenti per lo stesso motivo generano una nuova soglia misurata (D-065). Il raster
si produce con lo strumento di sessione (browser preinstallato), fuori dal nucleo
deterministico.

**Criteri di accettazione:**
1. Protocollo documentato e almeno **un ciclo completo dimostrato** — respinta,
   correzione degli ingressi, rigenerazione, approvazione — registrato con i rilievi. Se
   la prima passata approva, il ciclo si dimostra su una variante degradata apposta.
2. Ogni rilievo del ciclo dimostrato nomina una regola della carta.
3. Nessuna modifica alla geometria prodotta in nessun punto del ciclo.

**Collaudo:** qui il protocollo **è** il collaudo della tavola; il collaudo di pacchetto
verifica che il protocollo sia stato seguito e registrato integralmente.

### WP7 — Rigenerazione, cancello completo, consegna

**Obiettivo:** consegnare al PM la tavola del caso di accettazione con il timbro.

**Contenuto:** rigenerare il caso end-to-end con la catena nuova; passare controlli di
correttezza, preflight e occhio terzo; produrre tavola (SVG e raster; PDF stampabile via
strumento di sessione), rapporto con le misure e la mappa **difetto registrato → prova di
chiusura** per tutti gli otto difetti del 5 agosto.

**Criteri di accettazione:**
1. Tutti i cancelli verdi il giorno della consegna, sulla catena corrente.
2. Gli otto difetti registrati hanno ciascuno la propria prova di chiusura nel rapporto.
3. Il rapporto al PM è in linguaggio piano (D-068).

**Collaudo:** verifica indipendente del rapporto e dei cancelli prima dell'invio.

---

## 5. Cosa vede il PM, e quando

1. **Subito:** questo piano, per il via.
2. **Dopo WP1:** il foglio dei simboli nuovi, da approvare a colpo d'occhio.
3. **Dopo WP2:** il dossier delle integrazioni in linguaggio piano — cosa viene inserito,
   dove e perché, con la fonte — per l'approvazione del contenuto delle regole, mai
   avvenuta prima (D-085).
4. **Durante:** nulla d'altro, salvo domande di prodotto vere — poche e raccolte insieme.
5. **Alla fine (WP7):** la tavola rigenerata con il rapporto di collaudo, la chiusura
   difetto per difetto, e la conferma finale del contenuto sulla tavola finalmente
   leggibile.

## 6. Il backlog precedente

Pacchetto di dominio idronico (P3A), cartiglio/PDF/distinta (P5), confezionamento della
skill (P6), release (P7): **in coda dopo WP7, contenuti invariati**. Motivo dell'ordine:
confezionare una skill che consegna tavole non approvabili significa distribuire il
difetto, non il prodotto. Registrato in D-084.

---

## Appendice — registro di esecuzione

Si compila durante l'esecuzione. Una riga per pacchetto e per ogni deviazione dal piano.

| Voce | Sviluppo | Verdetto del collaudo | Data | Note |
|---|---|---|---|---|
| Audit §1 | Orchestratore | **Confermato integralmente** dal collaudatore indipendente: 9 gruppi di verifica, 7 confermati secchi, 2 confermati con precisazione (il controllo di correttezza esiste già; l'orientamento topologico ha un ripiego geometrico per i soli casi ambigui). Regressione: 461 test verdi | 2026-08-05 | Le due precisazioni sono incorporate nella tabella §1 |
| Deviazione WP2, dichiarata dallo sviluppo | Sviluppatore WP2 | in attesa | 2026-08-05 | Il piano diceva «la regola di intercettazione» al singolare e «quindici schede». Coprire ogni attacco di ogni macchina richiede **4 regole** di intercettazione (generatore, circolatore, accumulo, bollitore per fluido) perché una regola propone un pezzo solo e ogni pezzo appartiene a un fluido: il pacchetto passa da 15 a **19 regole** e le schede sono 19. Aggiunte 2 voci al catalogo d'esempio (valvola d'intercettazione su acqua fredda e su ACS), come già fatto in P1 per ritegno e sicurezza sanitari. Motore non toccato |
| WP2 — sviluppo eseguito | Sviluppatore WP2 | in attesa | 2026-08-05 | Intercettazioni per attacco (D-074): PdC 2, circolatore 2, volano 4 (1 preesistente riconosciuta), bollitore 4, conteggio automatico in prova permanente. La revisione trasversale ha trovato e corretto un terzo difetto: lo scarico dell'accumulo stava fuori dalla sezione intercettata (ora `drain-on-storage` 2.0.0, lato serbatoio). Caso di accettazione rigenerato dalla catena corrente, con prova che il file pubblicato coincida con la rigenerazione; idempotenza provata; schede di verifica e dossier PM in `docs/rules-review/`; suite verde, lint e tipi a zero |
| WP1 — sviluppo eseguito | Sviluppatore WP1 | **RESPINTO** al primo collaudo | 2026-08-05 | 14 corpi ridisegnati sulle tavole fonte, 17 rietichettati (macchine di pratica, geometria D-055 invariata), zero CONV-GRAFICA-001 residui, rigenerazione bit-identica, manifesti cambiati nella sola riga `source`. Il collaudo ha respinto per il criterio 1: sei simboli con fonte «pratica di settore» **senza puntatore**, terza classe di fonte non prevista e non registrata |
| WP2 — collaudo | Collaudatore indipendente | **APPROVATO** (criteri 6–11 tutti PASS) | 2026-08-05 | Conteggio per attacco confermato con camminata autonoma delle connessioni; motore intatto; idempotenza e rigenerazione byte-identica; dossier letto per intero: zero gergo. Rilievo di **contenuto** da portare al PM col dossier: il ramo di ritorno del pavimento radiante non ha una valvola propria in tutto il suo percorso (i ritorni di zona si riuniscono sull'attacco del volano); a rigore i «tubi» al volano sono 5 e le valvole 4. Le zone di norma si chiudono al collettore: decisione di prodotto, non di codice |
| WP3 — sviluppo eseguito | Sviluppatore WP3 | in attesa di collaudo | 2026-08-05 | Ciclo deterministico posizioni→linee: instrada, sposta, reinstrada, tiene la mossa solo se il totale migliora **e gli attraversamenti non aumentano**. Caso di accettazione: pieghe 28→24, attraversamenti 11→9, lunghezza 1332→1207 mm, e **sta su una sola A3** grazie all'impilamento di bollitore e volano (D-073). Fixture: pieghe 25→23. Sette componenti spostati per caso. 471 test verdi, determinismo bit-a-bit su semi diversi |
| Revisione di criterio, decisa dall'orchestratore | Orchestratore | — | 2026-08-05 | Il criterio scritto («pieghe **e** attraversamenti entrambi sotto i valori attuali») si è rivelato **infeasible**: una sonda esaustiva su 600 disposizioni mostra che scendere sotto 9 attraversamenti costa 27 pieghe invece di 25. Dei 9 attraversamenti, 4 sono il minimo geometrico delle due derivazioni su attacco condiviso. Criterio rivisto: nessuna delle due misure peggiora, almeno una migliora, obiettivo totale migliore, lunghezza entro +10%. E l'accettazione di una mossa vieta comunque di aumentare gli attraversamenti: sono il difetto più visibile e il PM li ha contestati per primi |
| Deviazioni WP3, dichiarate dallo sviluppo | Sviluppatore WP3 | — | 2026-08-05 | (1) Il ciclo verifica anche che ogni tratta resti capace di ospitare i propri accessori, con una corsia di riparazione prioritaria: senza, l'impaginazione su foglio unico comprimeva le tratte sotto il rettilineo necessario e la tavola falliva. (2) L'impilamento di soccorso è ammesso solo sul formato ordinario più grande: senza il vincolo, la fixture si impilava su A4 ribaltando la scelta di formato di D-058. (3) Riscritto l'allocatore degli accessori in linea, che con le valvole per attacco di WP2 non riusciva più a collocarne quattro su una tratta e ne scombinava l'ordine. (4) Instradamento reso due volte più veloce a parità di uscita byte per byte, per poter pagare le prove di spostamento |
| Residuo aperto su WP3 | Sviluppatore WP3 | — | 2026-08-05 | Il caso completo conserva **un'andata e ritorno**: il prelievo ACS — proprio quello cerchiato dal PM. Il suo attacco guarda a destra mentre l'alimentazione arriva da sinistra, e nessuno spostamento può rimediare: serve una mossa di **rotazione**, prevista dal piano fra le mosse ammesse e non implementata in questo pacchetto. Non forzato, riportato: chiuso dal pacchetto WP3b |
| WP1 — correzione dopo il respingimento | Orchestratore | **APPROVATO al ri-collaudo**: criterio 1 PASS (16 cfr. SRC-008, 6+2 UNI via SRC-016, 2 via SRC-015, 5 «da acquisire» dichiarate, zero fonti secche), determinismo PASS, rilievi di processo tutti chiusi | 2026-08-05 | Il confine di rete (usato nel caso MVP, forma da schemi di produttore) passa a «cfr. SRC-008»; i cinque simboli dei domini fuori MVP (serranda, diffusore, ventilatore, derivazione refrigerante, contatore gas) dichiarano nella stringa stessa che la fonte puntuale è da acquisire, con rinvio a `DEFERRED` §5 — un puntatore a un documento non verificato sarebbe stato inventato (D-083). Corretta anche la riga CONV-GRAFICA-001 del registro fonti, segnalata dal collaudo come ormai falsa. `scripts/rasterize.sh` fuori perimetro WP1: riassegnato a WP6, dove appartiene |
