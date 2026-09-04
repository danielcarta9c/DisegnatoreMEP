# PROJECT_STATE — Disegnatore MEP

> Stato vivo del progetto. `Now` contiene al massimo tre attività; `Next` è ordinato per priorità; `Done log` è anti-cronologico.

## Repository e ambienti

| Componente | Stato | Note |
|---|---|---|
| Repository | Git locale + GitHub | Remote `origin` su [danielcarta9c/DisegnatoreMEP](https://github.com/danielcarta9c/DisegnatoreMEP), **pubblico**, licenza MIT (D-038) |
| Sviluppo | Locale o cloud | Ambiente ricostruibile con `bash scripts/setup-env.sh` |
| Interprete | Python 3.12, minimo 3.11 | |
| Pacchetto | `disegnatore-mep` 0.1.0 | Installato in editable nella `.venv` |
| Test | **1103 verdi, 22 parcheggiate, 13 marcate sui difetti aperti** (DRAW-004, sul ramo in PR) | `pytest`, `ruff` e `mypy --strict` a exit `0` su `src`, `tests` ed `examples`. Delle 22 parcheggiate, **18 riguardano la composizione** — che ora compone, ma resta fuori dai budget di qualità — e 4 il foglio di riscontro dei simboli, che non entra più in una pagina sola |
| Libreria simboli | 39 pubblicati | A scala fissa ne entrano 32 per foglio: il foglio di riscontro va impaginato su piu' pagine |
| Catalogo | 53 voci, 17 regole | |
| Release | Non disponibile | |

## Now — in corso

> **✔ DRAW-004 è consegnato in PR (4 settembre), in attesa del verdetto del PM.** Il
> ciclo di miglioramento lavora in due fasi: la posa di DRAW-002 così com'era, poi la
> rifinitura da disegnatore a discesa più ripida — assi coordinati fra le porte, dorsale
> rimessa in fila con il pezzo all'altro capo sull'asse, la T che gira usando due attacchi
> ortogonali, le macchine a terra che possono cambiare quota — dove ogni candidata si
> misura dopo il reinstradamento completo e vince solo sul costo unico della tavola. La
> coppia di attacchi usata da un raccordo è una proprietà della posa (`port_map`), non del
> grafo. Impianto 1: curve da 10 a 6, incroci da 2 a 1, tubo da 597,5 a 577,5 mm,
> backtracking e tratte lunghe a zero, valvole 20/20, terra assente, sette sigle in
> consegna. Rapporto e artefatti in `docs/collaudi/DRAW-004/`.
>
> **DRAW-003-R1 è approvato e fuso.** La terra è assente; la geometria resta quella di
> DRAW-002; la consegna mostra soltanto sette sigle principali e nessun richiamo; gli
> indirizzi di verifica sono un velo best-effort che non muove nulla.

> **DRAW-002-R3 è stato approvato e fuso dal PM il 3 settembre (`2396bff`).** Il controllo
> del PO ha confermato il miglioramento, ma ha rilevato due difetti materiali per il gate
> della release 0.2: la linea continua di terra è ancora visibile, in violazione di
> D-121, e la fase delle etichette deve risultare inequivocabilmente successiva e
> indipendente dal routing. Il pacchetto attivo **DRAW-003** elimina il terreno dal
> rendering e rende contrattuale la sequenza posa → tubazioni → testi con richiamo.

Il progetto costruisce la skill **un pezzo alla volta**, sulla logica del grafo (D-099).
Piano corrente: `docs/plans/2026-08-06-piano-costruzione-skill.md`.

> ### ⛔ Due cose decise il 10 agosto, che cambiano dove si lavora e su cosa
>
> **1. Lo sviluppo si era biforcato l'8 agosto, e ora ha di nuovo un tronco solo (D-115).**
> Due linee erano partite dallo stesso punto senza vedersi, e una terza sessione è stata
> aperta su un punto più vecchio di entrambe. Il tronco è **la linea del 9 agosto** —
> questa — perché porta le tavole che il PM ha avuto in mano e il **registro dei suoi
> input**. Dell'altra linea manca ancora tutto, e va riportato **un pezzo per volta con le
> sue prove**: le quattro zone per i soli pezzi grossi (la correzione del PM sulle
> colonne, I-011), il tratto comune riconosciuto togliendolo — che chiude i **difetti 1 e
> 2** qui sotto — lo scarico dei serbatoi di fianco, la linea di terra ritirata, la fascia
> che si piega in colonne, il buco dei sottosistemi, la grammatica di centrale. Nessuna
> unione automatica: il collocatore è stato riscritto da entrambe in modo diverso.
>
> **2. Si guarda una tavola sola: l'impianto 1 (D-116).** Le altre quattro non si
> compongono e non si consegnano finché il PM non ha approvato la prima. Poi si fanno
> come prova, per trovare errori che la prima non poteva mostrare.
>
> **✔ Il primo pezzo riportato è fatto (D-118):** le zone valgono solo per i pezzi grossi
> e ciò che sta in parallelo si impila sempre. Sull'impianto 1 la posa passa da 330 a
> 253 mm, i rilievi da dodici a sei, le tratte con troppe pieghe da otto a due, e **la
> confluenza dei ritorni non sta più a sinistra delle pompe di calore da cui quei ritorni
> arrivano**. Prezzo misurato e non nascosto: gli incroci salgono da 11 a 13 e il disegno,
> essendosi stretto senza svilupparsi in altezza, riempie il 27 % invece del 35 % ed è
> tutto in un angolo. **Sono i due numeri del pezzo successivo.** Manca ancora il verdetto
> di un collaudo a contesto separato: qui è misurato, non approvato.
>
> **✔ E il pezzo successivo è fatto (DRAW-001, 1 settembre):** i due numeri che D-118
> aveva lasciato indietro sono rientrati e la regola di vicinanza del PO è consegnata.
> Sull'impianto 1 il riempimento passa dal 29 al 41 %, lo squilibrio fra quadranti da 12,6
> a 2,6 — dentro il limite dichiarato di 3 — gli incroci da 13 a 12, le pieghe da 33 a 27
> e le tratte con troppe pieghe da 3 a 1; le valvole che stanno sull'attacco che isolano
> passano da sei a diciassette su venti. Il prezzo è la lunghezza delle tubazioni, da 1030
> a 1178 mm. Il collaudo indipendente ha **respinto due volte** — un controllo grafico
> ristretto senza dirlo, un riempimento gonfiato da un pezzo spinto in aria, una collisione
> fra due indirizzi che la consegna dichiarava assente perché misurava un'altra tavola, e
> un rimedio che era matematicamente identico a ciò che c'era già — e la consegna risponde
> a tutti e otto i punti. La causa che teneva ferma la regola era una **misura**: «linea sotto il
> simbolo» guardava se il riquadro contenesse il tratto per intero, e non vedeva chi lo
> attraversava da parte a parte. Rapporto e artefatti in `docs/collaudi/DRAW-001/`.
>
> **✔ E DRAW-002-R3 è consegnato in PR (3 settembre), in attesa del verdetto del PM.**
> Il PO aveva respinto la tavola di DRAW-001 (I-021, I-022): tubi che tornano indietro,
> macchine equidistanti, spazio comprato con tubazioni. La causa era duplice: la posa
> iniziale metteva i raccordi del corredo di rete dalla parte opposta alla porta di
> uscita del ritorno, e il ciclo di miglioramento congelava quell'ordine muovendo un
> pezzo per volta di pochi passi, poi **distendeva** pagando riempimento con tubo. Ora
> la posa finale la decide **un solo confronto lessicografico della tavola** —
> violazioni, andate e ritorno in tratte e millimetri, tratte oltre tre pieghe, pieghe,
> incroci, lunghezza, e riempimento solo come spareggio — su candidati ricavati dalla
> topologia (porte allineate e affacciate, catene di raccordi rimesse in fila, pile e
> colonne traslate come gruppo, scambi nella pila, spazio aperto spingendo chi è
> d'intralcio), ognuno misurato dopo l'instradamento completo. Sull'impianto 1: andate e
> ritorno da 1 tratta e 75 mm a **zero**, incroci da 12 a **2**, pieghe da 27 a **10**,
> tratte oltre tre pieghe da 1 a **0**, tubo da 1177,5 a **597,5 mm**, valvole D-120
> sull'attacco da 17 a **20 su 20**; nessun rilievo bloccante. Prezzo dichiarato:
> riempimento dal 41 al 36 %, avviso e non obiettivo. Il collocatore non spareggia più
> per nome dei pezzi ma per posizione nel modello: due impianti uguali con nomi diversi
> danno la stessa tavola. Rapporto e artefatti in `docs/collaudi/DRAW-002/`.
>
> **✔ DRAW-003-R1 è consegnato sulla PR #11 (3 settembre), in attesa del verdetto del PM.**
> Il PO aveva visto ancora la linea continua di terra su DRAW-002 (I-024) e chiesto che i
> testi fossero l'ultima fase, senza toccare posa e tubazioni (I-025). La prima consegna
> toglieva la terra ma trattava le etichette come un criterio bloccante, con 38 richiami
> su 52 testi: il PO ha corretto la priorità e il PM ha chiesto la revisione. La gerarchia
> vincolante è: correttezza del grafo, geometria di macchine e tubazioni, costo delle
> tubazioni, e solo a geometria congelata i testi, che hanno costo nullo e non bloccano
> mai la tavola. Ora ogni testo prova i lati adiacenti in ordine fisso e si ferma al
> primo libero; le sole sigle delle macchine, senza un lato libero, prendono un richiamo
> corto che non attraversa niente, altrimenti si omettono con un avviso; gli indirizzi di
> verifica sono un velo a buon fine, adiacenti o omessi, mai richiamati. Sull'impianto 1
> simboli e rotte restano identici a DRAW-002; verifica: 42 etichette (7 sigle e 35 indirizzi su 45, 10 omessi perché senza un lato libero), nessun richiamo, nessuna scritta sopra tubi, simboli o altre scritte; consegna:
> le sole 7 sigle delle macchine, nessun richiamo, nessuna sigla omessa, tavola identica alla prima consegna. Rapporto e artefatti in `docs/collaudi/DRAW-003/`.
>
> **E il criterio con cui si sceglie cosa fare** (I-013): le tavole prodotte finora il PM
> le considera **da buttare**, quindi non si rifiniscono. Si chiudono le sue righe aperte
> nel registro degli input, che è il primo file da leggere dopo l'handoff.
>
> **3. Ogni sessione finisce su `main`** (D-117), e i conflitti si risolvono invece di
> aprire un ramo nuovo. Questo è il censimento dei rami, che va tenuto aggiornato perché è
> l'unico posto dove si vede se qualcosa è rimasto fuori:
>
> | Ramo | Cosa c'è sopra che `main` non ha |
> |---|---|
> | `claude/disegnatoremep-main-resume-890881` | **10 commit veri, ed è il debito aperto.** ✔ Riportate le zone per i soli pezzi grossi (I-011, D-118). **Restano:** il tratto comune riconosciuto togliendolo, lo scarico dei serbatoi di fianco, la linea di terra ritirata, la fascia che si piega in colonne, il buco dei sottosistemi, il resto della grammatica di centrale. Si riporta un pezzo per volta (D-115) |
> | `archivio/fase-grafica-2026-08-03` | **Niente da riportare, e non si fonde mai:** è una **storia separata**, senza nessun antenato in comune con `main`. È l'archivio della fase precedente al riavvio del 3 agosto. Sta scritto qui perché un ramo con 72 commit fuori da `main` e nessuna spiegazione fa perdere tempo a chiunque applichi D-117 |
> | tutti gli altri | Nulla: sono dentro `main` |

- [x] **Il grafo, le sigle e l'indirizzo dei nodi (D-105)** — sigle collaudate; l'indirizzo
      per linea (`CP.01`, `CP.01.N.02`, civici degli stacchi) **collaudato e APPROVATO**
      il 7 agosto, con le 91 prove del collaudo adottate come regressione.
- [x] **Il regime della centrale e il tratto comune (D-106, pacchetto E)** — costruito,
      **collaudato a contesto separato**: respinto su quattro difetti veri, tutti corretti
      lo stesso giorno e verdi sulle prove del collaudo, adottate come regressione. Il
      regime (sotto/sopra i 35 kW) si **legge dalle potenze dichiarate dal progettista**
      (D-108); se le potenze non sono disponibili, vale il corredo minimo e la mancanza
      viene dichiarata. Il corredo di rete sta sul **ritorno generale, a monte della prima
      ripartizione**; dove il tratto comune non esiste esce un punto aperto. Il catalogo
      dichiara **cosa la macchina porta a bordo** e **da quale attacco la riserva si riempie**.
- [x] **La correzione C2** — lo scarico del bollitore sta sull'ingresso freddo, con la
      derivazione sulla rete fredda; la prova del collaudo è tornata verde senza essere
      ammorbidita.
- [x] **Le correzioni chieste dal PM a fine sessione** (7 agosto, sera):
      la camminata del ritorno generale **si apre sui rami**, e l'ibrido riceve il
      corredo sul tratto che ha davvero — nessuno dei cinque impianti ha più punti
      aperti; e il **regime si legge dalle potenze** che il progettista ha dichiarato
      (D-108), scritto nel modello dove lui lo vede: quattro impianti sotto i 35 kW, la
      cascata di tre macchine sopra.
- [x] **Il quinto grafo pubblicato è stato rigenerato dalla pipeline** — completatore e
      assemblatore, nessuna correzione a mano. Da 98 a 108 pezzi: **il collettore
      sparisce** (il testo non lo nominava, e le sue due sole uscite erano il motivo per
      cui il terzo circuito restava fuori), **compare il circuito miscelato del pavimento
      radiante** con la sua miscelatrice e il suo circolatore, e i raccordi passano da
      otto a dodici — la regola generale a N vie al posto di un pezzo mai scritto dal
      progettista. Il documento porta ora tutti e tre i circuiti secondari.
- [x] **Il pezzo 1, «Capire», è APPROVATO** dal collaudo indipendente (7 agosto, giro 3).
      Su cinque impianti, 67 componenti e 82 tubazioni: **zero perso, zero inventato**;
      regime ricavato 5 su 5 e mai chiesto; raccordi N−1 col conto esatto; tutti e cinque
      i grafi attraversano il resto della catena con esito invariante al rimescolamento.
      Il quinto coincide col metro **arco per arco e sulle reti con la loro molteplicità**
      — il confronto più stretto che il contratto ammette — a meno di una valvola di
      ritegno che la lettura manuale porta e che il testo non nomina: ferramenta vietata
      all'interprete, classificata come assunzione tacita del metro. **Le letture manuali
      non sono state toccate.** Consegne agli atti in `skill/capire/prova-2026-08-07/`,
      verbali in `docs/collaudi/`.

- [x] **La tavola esce, e il PM l'ha in mano** (9 agosto). Un impianto su cinque esce
      su una A3, in **modalità verifica**: ogni pezzo porta stampato accanto il proprio
      indirizzo, così il progettista punta un pezzo sul disegno e lo cerca sul grafo.
      Escono anche con i rilievi di qualità aperti, marcate come tali — una tavola che
      serve a trovare gli errori deve poter uscire proprio quando ne ha. Da SVG a **PDF**
      a misura reale.
      - **Perché non uscivano.** Non era la carta, ed è stato misurato: fallivano identiche
        anche su A0. Gli accessori appesi a uno stacco — sfiato, scarico, vaso,
        riempimento, manometro — finivano in una colonna propria, ordinati per profondità
        come fossero un passo del processo. Lo scarico dell'accumulo stava sessanta
        millimetri a sinistra dell'accumulo, con due macchine in mezzo.
      - **E un secondo guasto della stessa specie** (D-113): davanti a ogni attacco c'è
        una cella sola, la sua unica uscita, e la valvola di un'altra tratta ci si era
        seduta sopra murandolo. L'impianto del pavimento radiante falliva identico su A3,
        A2 e A1.
      - **L'ordine di lettura era rovesciato**: le fasce venivano dall'ordine in cui il
        file elenca i sottosistemi, cioè dal loro nome. Ora vengono dal processo — chi
        genera a sinistra, chi accumula, chi utilizza — come D-111 chiede.
      - **Il collocatore usa anche l'altezza** (D-111, D-112): quando la fila non entra
        confronta poche disposizioni deterministiche e prende la meno cara, impilando ciò
        che sta in parallelo e scambiando colonne che nessuna tratta collega.

**Il prossimo lavoro è cambiato: si va sul disegnatore** (decisione del PM, 7 agosto
sera). Il contenuto si chiude «alla buona» e si porta a casa la tavola, perché il grafo
scritto è 300÷500 righe di tabelle e nessuno ci trova un accessorio fuori posto
leggendolo — mentre sulla tavola si vede in due secondi. Da lì il PM segna gli errori e le
regole si correggono su casi veri, invece di scriverle al buio: **è la stessa paura di
D-107, presa dal lato giusto.**

Tre cose, in ordine, e ci si ferma:

1. **Il criterio della camminata** (difetti aperti 1 e 2, che hanno una radice sola). Non
   per pulizia: oggi lo stesso impianto dà due risposte diverse a seconda di **come si
   chiamano le macchine**, e un ciclo di verifica ha bisogno che rigenerare due volte dia
   due volte la stessa tavola. È un prerequisito, non una rifinitura. **Non fatto:** il
   9 agosto si è saltato al punto 2 e 3 per portare al PM una tavola da guardare, che era
   lo scopo dichiarato. Resta il primo lavoro della prossima sessione.
2. **La modalità verifica** (D-110, come emendata da D-111): l'indirizzo del nodo stampato
   accanto al pezzo.
3. **La composizione** (D-111 e D-112): disporre meglio sul foglio che c'è, non spezzare.
   **La centrale è un'unità grafica indivisibile** e non si divide mai in automatico; una
   seconda tavola si apre solo se la distribuzione, presa da sola, merita un foglio; il
   formato maggiore è l'ultima risorsa e vuole una motivazione verificabile.

**Gli altri difetti aperti si rimandano**: le due correzioni alle istruzioni costano un
giro intero di camera pulita ciascuna e non cambiano niente di ciò che si vede sulla
tavola. Restano scritti qui sotto e si chiudono quando capita.

## I difetti aperti, inchiodati da prove

Nessuno è stato nascosto: ognuno ha una prova marcata che fallisce apposta, col motivo
scritto per esteso, e torna verde quando il difetto si chiude.

| # | Difetto | Dove |
|---|---|---|
| 1 | Sull'**ibrido**, il tratto scelto per il corredo **non porta** l'acqua che la caldaia rimanda dallo scambiatore sanitario: quel ramo rientra a valle. Per il defangatore, la cui ragione scritta è «lì passa tutta l'acqua che torna», la posa non regge — ed è una posa silenziosa, senza punto aperto | la camminata del tratto comune |
| 2 | Con un **anello** sul ritorno, il punto scelto cambia **col nome delle macchine** a topologia identica: la camminata parte dal primo generatore in ordine alfabetico | la camminata del tratto comune |
| 3 | Le **potenze da cui il regime è stato letto non stanno nel modello**: i cinque grafi dichiarano il regime e nessun componente porta la potenza. D-108 promette che l'ingegnere veda la lettura e la corregga | le letture manuali di `examples/prova/` |
| 4 | La regola del regime **non ha il caso di mezzo**: potenza dichiarata solo per alcune macchine. L'impianto 3 ne ha due che il catalogo dice generatrici e il testo ne dà una sola; l'impianto 4 sta a 34 kW su 35 | `ISTRUZIONI.md` §4.6 |
| 5 | Una voce dichiarata del primo grafo cita **identificativi interni** del JSON in una frase destinata all'ingegnere | il grafo dell'agente: si chiude alle istruzioni, non correggendo l'allegato |
| ~~6~~ | ~~La radice normativa della soglia non copre le pompe di calore~~ | **CHIUSA dal PM (D-109)**: le centrali domestiche stanno sempre sotto i 35 kW, e la skill disegna anche centrali a **caldaia a gas**, dove il focolare c'è. Niente da correggere, niente da chiedere |

## Il confine del prodotto, che vale su tutto (D-104)

La skill emula un **disegnatore MEP**, non un progettista. L'ingegnere consegna uno schema a
livello di definitivo; la skill lo porta a livello esecutivo aggiungendo la ferramenta che
su una tavola esecutiva c'è sempre. **Non decide quanti pezzi ci vanno, non cambia lo schema
ricevuto, non dimensiona.** Il regime della centrale è un **dato del progettista**, e la
skill lo **legge** dalle potenze che lui ha dichiarato (D-108): sommarle e confrontarle
con la soglia non è dimensionare. Se le potenze non ci sono, il regime resta non
dichiarato, vale il corredo minimo, e quella è una domanda — non un'invenzione.

## Next — i pezzi che restano

> **L'ordine vero del lavoro non è questo elenco: sono le righe aperte del registro degli
> input** (`docs/input-pm/REGISTRO.md`), perché è quello che il PM ha chiesto e perché le
> tavole già uscite lui le considera da buttare (I-013). Questo elenco resta la mappa dei
> pezzi che mancano al prodotto.

1. **I cinque difetti aperti** della tabella qui sopra (il sesto è chiuso), in ordine: i due della camminata del
   tratto comune (che sono difetti veri del completatore), il caso di mezzo del regime, le
   potenze nel modello, e la voce con gli identificativi interni. Ognuno ha già la prova
   che lo inchioda: si chiude quando quella prova torna verde senza essere ammorbidita.
2. **La traduzione in regole** delle posizioni chiuse con le fonti (bilanciamento,
   disconnettore, contabilizzatore — `DOVE_VA_CIASCUN_ACCESSORIO.md` §14-18), dentro il
   confine di D-104. Miscelatrice e ritegno sanitario hanno già le regole.
3. **La libreria dei simboli** — contenuto da completare (segno del rubinetto bloccabile).
4. **Il cartiglio.**
5. **La composizione** — **tre impianti su cinque escono** (9 agosto), ma il PM le giudica
   tavole da buttare, e **il campo si è ristretto al solo impianto 1** (D-116).
   Il quarto e il quinto **aspettano che il primo sia approvato**; quando toccherà a loro
   sarà **davvero larghezza**: le loro fasce chiedono 507 e 945 millimetri contro i 335 di
   una A3. Il quarto entra su A2; il quinto non entra nemmeno su A1. Sono i due casi per
   cui D-112 esiste — prima si stringe davvero, poi si valuta se la distribuzione merita
   una seconda tavola, e il formato maggiore per ultimo con la motivazione scritta.
   ⛔ **La vecchia motivazione scritta qui era falsa** e va ricordata: diceva «l'impianto
   completo non entra in larghezza», e per i primi tre non era vero — fallivano anche su
   A0, per l'instradamento. Le due cose si distinguono con una prova sola: **se il
   fallimento non cambia passando a un foglio più grande, non è spazio.**
6. **I validatori e il cancello dell'occhio terzo.**

## Done log — ultimo in cima

| Commit | Cosa |
|---|---|
| — | **DRAW-004 — assi fra le porte, dorsali e T che assorbe una curva** (in PR, verdetto del PM atteso). Seconda fase del ciclo a discesa più ripida con candidati da disegnatore, `port_map` sul simbolo posato, macchine a terra libere in quota nella rifinitura, diario delle candidate provate. Impianto 1: curve da 10 a 6, incroci da 2 a 1, tubo da 597,5 a 577,5 mm; otto prove generali scritte prima del codice |
| — | **DRAW-003-R1 — via la linea di terra, testi come fase terminale a costo zero** (sulla PR #11, verdetto del PM atteso). Nessuna linea o tratteggio di terra nell'SVG, quota non esportata, centratura su simboli e tubazioni; etichette sul primo lato adiacente libero, richiamo corto e pulito solo per le sigle delle macchine, indirizzi di verifica a buon fine; nessun rilievo sui testi è bloccante. Impianto 1: simboli e rotte identici a DRAW-002; verifica 42 etichette (7 sigle e 35 indirizzi su 45, 10 omessi perché senza un lato libero), nessun richiamo, nessuna scritta sopra tubi, simboli o altre scritte; consegna le sole 7 sigle delle macchine, nessun richiamo, nessuna sigla omessa, tavola identica alla prima consegna. Registrati I-026, I-027 e I-028 per DRAW-004 |
| `2396bff` | **DRAW-002-R3 — la posa finale la decide il costo delle tubazioni** (approvato e fuso dal PM il 3 settembre). Un solo confronto lessicografico della tavola, niente distensione, candidati dalla topologia, ogni prova dopo l'instradamento completo. Impianto 1: andate e ritorno a zero, incroci da 12 a 2, pieghe da 27 a 10, tubo da 1177,5 a 597,5 mm, valvole D-120 sull'attacco 20 su 20. Sei prove generali scritte prima del codice, cinque prove di regressione sui criteri della tavola 1 |
| `de5194c` `75bd720` | **DRAW-001 — la tavola dell'impianto 1 migliora, e la regola di vicinanza entra.** La linea non passa più sotto un simbolo: la misura contava il contenimento e lasciava passare chi attraversava da parte a parte, e chi si attaccava al simbolo era per di più esente dalla distanza. Chi isola si posa sull'attacco di ciò che si manutiene, a un passo oltre la cella riservata (D-113, D-120). Riempimento e bilanciamento diventano obiettivi del collocatore invece che avvisi a tavola finita (D-111): riempimento dal 29 al 41 %, squilibrio da 12,6 a 2,6, incroci da 13 a 12, pieghe da 33 a 27, tratte con troppe pieghe da 3 a 1, valvole sull'attacco da 6 a 17 su 20 |
| — | **La tavola esce**: tre impianti su cinque su A3, in modalità verifica, da SVG a PDF a misura reale. Chi pende da uno stacco sta accanto al proprio pezzo; la soglia di ogni attacco è riservata (D-113); le fasce si leggono per processo e non per nome di sottosistema; il collocatore usa anche l'altezza. 15 prove nuove, 1050 verdi |
| — | **Sei incoerenze chiuse nella documentazione** e l'indirizzo del PM dell'8 agosto registrato come **D-112**: la centrale non si spezza, prima si ottimizza il foglio che c'è, il formato maggiore per ultimo con motivazione verificabile |
| — | **I cinque grafi rigenerati dalla pipeline**: solo il quinto cambia, da 98 a 108 pezzi — via il collettore mai nominato, dentro il circuito miscelato del pavimento radiante. Le sei prove che presidiavano l'artefatto vecchio sono verdi |
| — | **Il pezzo 1 «Capire» è APPROVATO** al terzo giro: zero perso e zero inventato su 67 componenti e 82 tubazioni, e il quinto grafo coincide col metro arco per arco. Consegne dei tre giri agli atti |
| — | **Corretto §4.2**: una rete parte da una macchina che la alimenta o da un confine, **mai da un raccordo**. Era il buco che al giro 2 faceva rompere la catena al quinto grafo |
| — | **Collaudo delle due correzioni di fine sessione: RESPINTE** entrambe, cinque difetti veri ai bordi mentre il nocciolo regge. Prove che li inchiodano, verbale agli atti |
| — | **La contraddizione sul regime dentro il kit**, trovata da due camere pulite indipendenti: lo schema vietava per esteso la somma che le istruzioni prescrivono. Testo pre-D-108 in tre posti, corretto rigenerando lo schema |
| `1eefd56` | **Fixture JSON del quinto impianto rigenerata** dalla lettura corretta: UTA, fan-coil e pavimento radiante sono tutti presenti |
| `a136862` | **Quinto impianto corretto nel generatore**: tutti e tre i circuiti secondari restano nel grafo di prima stesura; il collettore a due uscite non limita più la lettura del testo |
| `8d5ec99` | **Le tredici correzioni alle istruzioni dell'interprete**: regola generale dei raccordi a N vie, esempi che non contengono più le soluzioni, il regime dalle potenze, il criterio per chiedere. Tre prove nuove le inchiodano |
| `50cb842` | **Le quattro cose che l'interprete deve capire**, contate sulle condizioni delle diciassette regole: materiale per il giro di correzioni del pezzo 1 |
| `a75197b` | **Il regime si legge dalle potenze dichiarate** (D-108): i cinque impianti lo portano scritto, la cascata è l'unico sopra i 35 kW |
| `4433665` | **Il ritorno generale dell'ibrido c'era**: la camminata si apre sui rami e nessuno dei cinque ha più punti aperti; ritirata prima di scriverla la regola del filtro sul sanitario (D-107) |
| `da2c5f2` | **Collaudo del pacchetto E: RESPINTO, corretto lo stesso giorno.** Il bordo macchina soddisfa chi lo porta (mai il bordo altrui: la sicurezza del serbatoio non sparisce più); il vaso sanitario firmato dalla regola giusta; la fonte sul riscontro. 25 prove del collaudo adottate |
| `b7ea439` | **Collaudo dell'indirizzo dei nodi (D-105): APPROVATO.** 91 prove proprie più dure, adottate come regressione |
| `7187437` | Le tre correzioni del collaudo al contratto di consegna del pezzo 1 (campi del confronto, quarta classe, consegne agli atti) |
| `39259bc` | Il punto aperto del tratto comune si dice per quello che è, anche nel documento del grafo |
| `d370bd9` | **C2 corretta**: la riserva si svuota da dove si riempie; il catalogo dichiara il punto di riempimento; la prova del collaudo verde senza ammorbidirla |
| `08a23f0` | **Il pacchetto E (D-106)**: regime dichiarato, tratto comune, 17 regole aggiornate come dato, bordo macchina; due difetti d'ordine chiusi alla radice |
| `65fc7af` | **Collaudo del pezzo 1: RESPINTO**, verdetto registrato |
| `6334c7b` | **Il riscontro di D-106 sugli schemi Caleffi**, riga per riga con le citazioni |
| `2d48411`+ | Tre dei quattro difetti del collaudo corretti (C1, C3, C4) e le 29 prove del collaudo come regressione |
| `feee446` | **L'indirizzo dei nodi (D-105)**: linee, nodi numerati, civici; cinque grafi rigenerati |
| `a503ee4`, `f8fc476` | **Il pezzo 1 «Capire»** come istruzioni, provato in camera pulita |
| `3aa31de` | Le cinque righe mancanti degli accessori chiuse con le fonti (SRC-020..026) |
| `05d302b` | I cinque impianti del committente, letti e assemblati |
| `8d7796b` | **L'assemblatore**: la fila la decidono i vincoli dichiarati |
| `8e70438` | Gli accessori su stacco vanno dove vanno davvero (D-101) |
| `ecac2fa` | Ritirate tre regole dedotte dalla norma: la skill disegna, non progetta (D-104) |
| `167b5be` | Dove va ciascun accessorio, con la fonte (D-103) |
| `0f3bb63`…`ef6fc78` | Il grafo dell'impianto, le sue sigle e la passeggiata |
| `78838c7` | **Gate G0 superato**: progetto misto a quattro domini validato senza codice specifico per schema |
