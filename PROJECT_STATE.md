# PROJECT_STATE — Disegnatore MEP

> Stato vivo del progetto. `Now` contiene al massimo tre attività; `Next` è ordinato per priorità; `Done log` è anti-cronologico.

## Repository e ambienti

| Componente | Stato | Note |
|---|---|---|
| Repository | Git locale + GitHub | Remote `origin` su [danielcarta9c/DisegnatoreMEP](https://github.com/danielcarta9c/DisegnatoreMEP), **pubblico**, licenza MIT (D-038) |
| Sviluppo | Locale o cloud | Ambiente ricostruibile con `bash scripts/setup-env.sh` |
| Interprete | Python 3.12, minimo 3.11 | |
| Pacchetto | `disegnatore-mep` 0.1.0 | Installato in editable nella `.venv` |
| Test | **1052 verdi, 22 parcheggiate, 15 marcate sui difetti aperti** | `pytest`, `ruff` e `mypy --strict` a exit `0` su `src`, `tests` ed `examples` |
| Libreria simboli | 39 pubblicati | 18 delle 22 prove parcheggiate riguardano il **disegno** (composizione da rifare, D-113); le altre 4 il foglio di riscontro della libreria, che a scala fissa non tiene 39 simboli |
| Catalogo | 53 voci, 17 regole | |
| Release | Non disponibile | |

## Now — in corso

Il progetto costruisce la skill **un pezzo alla volta**, sulla logica del grafo (D-099).
Piano corrente: `docs/plans/2026-08-06-piano-costruzione-skill.md`.

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
- [x] **Le correzioni chieste dal PM a fine sessione** (7 agosto, sera): la camminata
      del ritorno generale **si apre sui rami**, e il **regime si legge dalle potenze**
      che il progettista ha dichiarato (D-108), scritto nel modello dove lui lo vede:
      quattro impianti sotto i 35 kW, la cascata di tre macchine sopra.
      ⚠ *Di quella riga, il pezzo che diceva «l'ibrido riceve il corredo sul tratto che
      ha davvero — nessuno dei cinque ha più punti aperti» era **falso**, e il collaudo
      indipendente l'ha respinto: l'ibrido un ritorno generale non ce l'ha. Corretto
      l'8 agosto (D-112). Aprirsi sui rami resta giusto — serve a trovare le tubazioni
      candidate — ma non era mai stato il criterio per sceglierne una.*
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

**Il prossimo lavoro è cambiato: si va sul disegnatore** (decisione del PM, 7 agosto
sera). Il contenuto si chiude «alla buona» e si porta a casa la tavola, perché il grafo
scritto è 300÷500 righe di tabelle e nessuno ci trova un accessorio fuori posto
leggendolo — mentre sulla tavola si vede in due secondi. Da lì il PM segna gli errori e le
regole si correggono su casi veri, invece di scriverle al buio: **è la stessa paura di
D-107, presa dal lato giusto.**

Tre cose, in ordine, e ci si ferma:

1. ~~**Il criterio della camminata**~~ — **FATTO l'8 agosto (D-112).** Il tratto comune si
   riconosce togliendolo: se il circuito di una macchina si chiude lo stesso, quel tratto
   la sua acqua non la porta. Il nome delle macchine non decide più niente. **E l'ibrido
   un ritorno generale non ce l'ha**: quattro punti aperti al posto di quattro pezzi
   posati in silenzio.
2. ~~**La modalità verifica**~~ — **FATTA l'8 agosto (D-114).** `draw --verifica --naming`
   stampa l'indirizzo accanto a ogni pezzo; `draw --anche-se-respinta` scrive la tavola
   anche coi rilievi bloccanti, dicendo che non è una consegna. L'invariante di D-110 è
   provato **sulla carta**: la tavola di consegna è una **sottosequenza esatta** di
   quella di verifica — 376 elementi su 376 ritrovati in ordine, 12 indirizzi in più,
   zero elementi persi.
3. **La composizione**: disporre in **due dimensioni** invece che in una striscia
   (D-111, D-113). Non «su più fogli»: il multi-foglio è l'ultima risorsa e la
   centrale non si spezza mai in automatico (input PM dell'8 agosto).

**Gli altri difetti aperti si rimandano**: le due correzioni alle istruzioni costano un
giro intero di camera pulita ciascuna e non cambiano niente di ciò che si vede sulla
tavola. Restano scritti qui sotto e si chiudono quando capita.

## I difetti aperti, inchiodati da prove

Nessuno è stato nascosto: ognuno ha una prova marcata che fallisce apposta, col motivo
scritto per esteso, e torna verde quando il difetto si chiude.

| # | Difetto | Dove |
|---|---|---|
| ~~1~~ | ~~Sull'**ibrido**, il tratto scelto per il corredo **non porta** l'acqua che la caldaia rimanda dallo scambiatore sanitario~~ | **CHIUSO l'8 agosto (D-112).** Il tratto comune ora si riconosce togliendolo: se il circuito di una macchina si chiude lo stesso, quel tratto la sua acqua non la porta. **Sull'ibrido un ritorno generale non esiste**, e vaso, riempimento, manometro e defangatore escono come **quattro punti aperti** invece che posati in silenzio. Le prove del collaudo sono verdi senza essere ammorbidite |
| ~~2~~ | ~~Con un **anello** sul ritorno, il punto scelto cambia **col nome delle macchine** a topologia identica~~ | **CHIUSO l'8 agosto (D-112).** Il criterio non guarda più l'ordine di scoperta: fra i tratti che reggono la prova si prende quello che si lascia dietro meno rete. Sull'anello la risposta è `s1.a` con qualunque nome, ed è quella che il collaudo aveva indicato come giusta |
| 3 | Le **potenze da cui il regime è stato letto non stanno nel modello**: i cinque grafi dichiarano il regime e nessun componente porta la potenza. D-108 promette che l'ingegnere veda la lettura e la corregga | le letture manuali di `examples/prova/` |
| 4 | La regola del regime **non ha il caso di mezzo**: potenza dichiarata solo per alcune macchine. L'impianto 3 ne ha due che il catalogo dice generatrici e il testo ne dà una sola; l'impianto 4 sta a 34 kW su 35 | `ISTRUZIONI.md` §4.6 |
| 5 | Una voce dichiarata del primo grafo cita **identificativi interni** del JSON in una frase destinata all'ingegnere | il grafo dell'agente: si chiude alle istruzioni, non correggendo l'allegato |
| ~~6~~ | ~~La radice normativa della soglia non copre le pompe di calore~~ | **CHIUSA dal PM (D-109)**: le centrali domestiche stanno sempre sotto i 35 kW, e la skill disegna anche centrali a **caldaia a gas**, dove il focolare c'è. Niente da correggere, niente da chiedere |
| ~~7~~ | ~~**L'attacco di scarico dei serbatoi è murato dal pavimento**: 54 posizioni provate, zero instradamenti riusciti~~ | **CHIUSO l'8 agosto (D-115).** Le fonti tacevano — dicono su quale attacco va lo scarico, non dove si disegna rispetto alla linea di terra — quindi la domanda è andata al PM, che ha scelto: **esce di fianco, in basso**. I tre volani hanno il `drain` sul fianco destro a 40 mm. La regressione guarda la **classe**: nessun attacco rivolto in basso di un pezzo posato a terra può cadere sul pavimento, per qualunque simbolo entri in libreria domani |
| 10 | **L'instradatore esaurisce il proprio budget di ricerca** — 400 000 espansioni — su una tratta sola, e si arrende dicendo «prova una partizione diversa». Non è congestione: il disegno occupa un quinto della carta. Si vede **solo dopo il ciclo di miglioramento**; sulla prima posa le stesse tratte si instradano. Ferma gli impianti 1 e 4 | `layout/route.py`, il budget di ricerca (D-115). **Era coperto dal difetto 7**: finché la catena si fermava prima, non si vedeva |
| 8 | **Il ripiego del collocatore può posare un pezzo sotto la linea di terra**, dove nessuna linea può raggiungerlo: il ciclo che lo spinge in giù cercando posto si ferma quando sfonderebbe il pavimento e usa lo stesso l'ultima quota. Sull'impianto 3 `zona-notte` finisce interamente sotto; sul 5 `miscelatrice-radiante` resta a cavallo | `layout/place.py`, il ramo di ripiego (D-113) |
| 9 | **Il rettilineo per gli accessori in linea si prenota solo fra colonne contigue**: una tratta fra colonne non contigue non ne riceve, e gli accessori non trovano i 10 mm dritti. Ferma gli impianti 2 e 5 | `layout/place.py`, la prenotazione dello spazio (D-113) |

## Il confine del prodotto, che vale su tutto (D-104)

La skill emula un **disegnatore MEP**, non un progettista. L'ingegnere consegna uno schema a
livello di definitivo; la skill lo porta a livello esecutivo aggiungendo la ferramenta che
su una tavola esecutiva c'è sempre. **Non decide quanti pezzi ci vanno, non cambia lo schema
ricevuto, non dimensiona.** Il regime della centrale è un **dato del progettista**, e la
skill lo **legge** dalle potenze che lui ha dichiarato (D-108): sommarle e confrontarle
con la soglia non è dimensionare. Se le potenze non ci sono, il regime resta non
dichiarato, vale il corredo minimo, e quella è una domanda — non un'invenzione.

## Next — i pezzi che restano

1. **I sei difetti aperti** della tabella qui sopra, in ordine: i due della camminata del
   tratto comune (che sono difetti veri del completatore), il caso di mezzo del regime, le
   potenze nel modello, e la voce con gli identificativi interni. Ognuno ha già la prova
   che lo inchioda: si chiude quando quella prova torna verde senza essere ammorbidita.
2. **La traduzione in regole** delle posizioni chiuse con le fonti (bilanciamento,
   disconnettore, contabilizzatore — `DOVE_VA_CIASCUN_ACCESSORIO.md` §14-18), dentro il
   confine di D-104. Miscelatrice e ritegno sanitario hanno già le regole.
3. **La libreria dei simboli** — contenuto da completare (segno del rubinetto bloccabile).
4. **Il cartiglio.**
5. **La composizione** — da rifare, ma **non è ciò che blocca il disegno** (D-113).
   Misurato l'8 agosto: i cinque impianti su A0, e perfino su un foglio 3000 × 2000,
   falliscono **negli stessi punti e alle stesse coordinate** che su A3, usando il
   21÷23 % dell'altezza. Più carta non sposta un pezzo, e di stretto non c'è niente.
   Ciò che li ferma sono **tre invarianti rotti**, elencati qui sotto.
6. **I validatori e il cancello dell'occhio terzo.**

## Done log — ultimo in cima

| Commit | Cosa |
|---|---|
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
