# Rapporto — Impianto 2

Committente: Nove C · Commessa: PROVA · Revisione 00 · 7 agosto 2026
Consegna: `consegna/grafo.json` (valida), `consegna/rilettura.md`, questo rapporto.

---

## 1. Che impianto ho capito

Una **pompa di calore aria-acqua reversibile da 15 kW** è l'unica macchina che genera
calore. È l'unica potenza che il testo dà, quindi il regime della centrale è
`up_to_35_kw` (15 ≤ 35).

Sulla sua mandata sta una **valvola deviatrice a tre vie** che manda il flusso, di volta
in volta, o alla climatizzazione o alla produzione sanitaria. Non sono due circuiti che
lavorano insieme: sono due rami **alternativi** dello stesso circuito primario, e la
scelta fra i due è una logica di regolazione (priorità al sanitario) che il grafo non
mostra.

- **Ramo climatizzazione:** un **volume tecnico da 100 litri a quattro tubi**. Il
  primario ci entra e ne esce; sul lato secondario parte un **circuito secondario con
  circolatore dedicato** che alimenta i **fan-coil** e torna al volume. I fan-coil
  lavorano sia in riscaldamento sia in raffrescamento: d'estate negli stessi tubi corre
  acqua refrigerata, perché la macchina è reversibile.
- **Ramo sanitario:** un **bollitore con serpentino**. Il primario attraversa il
  serpentino scambiando calore; l'acqua del bollitore è un'altra acqua, che entra fredda
  dall'alimentazione in basso ed esce calda in alto verso le utenze. Nessun ricircolo:
  il testo lo esclude.

I due ritorni del primario — quello dal volume tecnico e quello dal serpentino —
rientrano nello stesso attacco della pompa di calore. Un attacco porta una tubazione
sola, quindi in mezzo c'è un **raccordo a T di confluenza**: è la sola trascrizione
possibile di quello che il testo descrive.

Quattro reti: il **primario** (acqua di riscaldamento), il **secondario di
climatizzazione** (acqua di riscaldamento), l'**acqua fredda sanitaria**, l'**acqua
calda sanitaria**. L'acqua cambia dove il bollitore la cambia, e sono due reti diverse.

Fuori dal grafo per regola, ma registrati: il carico automatico da acquedotto e lo
scarico sul volume tecnico, e la valvola miscelatrice sull'uscita sanitaria. Sono
ferramenta di servizio: li aggiunge il pezzo successivo della catena.

Il grafo: 9 componenti, 4 reti, 11 tubazioni, 13 assunzioni. **Nessuna voce di tipo B**:
il catalogo aveva tutto quello che serviva per rappresentare l'impianto descritto.

---

## 2. Domande e assunzioni, in chiaro

Tutte sono nel JSON con `status: "proposed"`. Le riporto per esteso, con il tipo secondo
§6 delle istruzioni.

### Da portare all'ingegnere prima di andare avanti (tipo C)

**a12 — Il primario è una rete sola o due?**
Il testo distingue «il circuito di climatizzazione» dalla produzione di ACS, ma a monte
della valvola deviatrice il circuito è idraulicamente uno: stessa macchina, stessa acqua,
stessa mandata. Ho modellato pompa di calore, valvola e i due rami come **una rete unica
di primario**, e ho tenuto separato solo il circuito secondario, che il volume tecnico
separa davvero. La lettura opposta — due reti di primario, climatizzazione e produzione
ACS — è altrettanto difendibile e produce un modello diverso. *Quale delle due
l'ingegnere vuole vedere?*

### Chiuse in modo convenzionale e dichiarate (tipo A)

**a1 — Il circolatore del primario è a bordo macchina?**
Il testo non nomina nessun circolatore sul primario. La voce di catalogo scelta per la
pompa di calore lo dichiara a bordo, quindi non l'ho disegnato come pezzo a sé. *È così,
o il circolatore primario è esterno e va rappresentato?*

**a4 — Con che pezzo si riuniscono i due ritorni del primario?**
Il testo non lo dice. Ho messo un raccordo a T di confluenza prima del ritorno della
pompa di calore, perché un attacco porta una tubazione sola. *È così, o in quel punto
l'ingegnere prevede un collettore o un separatore idraulico?*

**a5 — Quanti sono i fan-coil?**
Il testo dice «fan-coil» al plurale senza dirne il numero. Ne ho disegnato **uno solo,
rappresentativo** dell'insieme. *Quanti sono davvero, e vanno rappresentati
separatamente?*

**a6 — Su quale ramo sta il circolatore del secondario?**
Il testo dice «circolatore dedicato» ma non dice dove. L'ho messo sulla **mandata** del
circuito secondario, che è la posizione convenzionale di disegno — non una regola
dell'impianto. *È così?*

**a11 — I confini del circuito sanitario.**
Il circuito sanitario è aperto: ho aggiunto i due confini di rete, l'alimentazione di
acqua fredda a monte del bollitore e le utenze sanitarie a valle. *Il testo non nomina né
l'una né le altre: sono i due confini convenzionali che chiudono il circuito.*

**a7 — Il volume tecnico «a quattro tubi» porta con sé un mestiere in più.**
Ho scelto la voce con quattro attacchi di flusso, che sono gli attacchi necessari a
scrivere i collegamenti descritti. Quella voce dichiara **anche** il mestiere di
separazione idraulica, che il testo non nomina: è una conseguenza del catalogo, non una
lettura del testo. Ha una conseguenza a valle — chi assegna le sigle leggerà «separatore»
prima di «accumulo». *Va bene?*

### Cose che il grafo non mostra, e non perché siano state perse

**a2 — Reversibilità e raffrescamento.**
La macchina è reversibile e i fan-coil lavorano anche in raffrescamento. La tabella dei
fluidi non ha un fluido per il raffrescamento, quindi primario e secondario sono
dichiarati «acqua di riscaldamento» e portano anche il raffrescamento. Il circuito resta
uno solo.

**a3 — La priorità sanitaria è regolazione, non topologia.**
Sul grafo si vede la valvola deviatrice che manda il flusso di qua o di là, non la
priorità che decide quando.

**a8 — Carico automatico da acquedotto e scarico sul volume tecnico.**
Ferramenta di servizio (gruppo di riempimento, attacco di scarico): li aggiunge il pezzo
della catena che completa il grafo. La nomina è registrata perché non vada persa. *Nota
di conseguenza: nel grafo la rete di acqua fredda non arriva al volume tecnico, benché il
testo descriva lì un collegamento fisico.*

**a9 — Valvola miscelatrice sull'uscita sanitaria.**
È una miscelatrice **sanitaria**: ferramenta di servizio, resta fuori dalla prima
stesura. La nomina è registrata.

**a10 — Il ricircolo ACS è escluso dal testo.**
Non è disegnato perché non c'è, non perché sia stato perso. Chi completa il grafo non lo
riaggiunga.

**a13 — Il regime è stato ricavato, non chiesto.**
15 kW, unica macchina che genera calore, quindi centrale fino a 35 kW. Il testo non dice
se i 15 kW sono potenza resa o assorbita: ho sommato il valore come sta.

---

## 3. Dove le istruzioni non mi hanno detto cosa fare

Questa è la parte che conta per la prova. In ordine di peso.

### 3.1 Una contraddizione vera, fra due documenti della cartella

**Il regime della centrale: §4.6 dice di calcolarlo, lo schema dice di non calcolarlo
mai.**

- `ISTRUZIONI.md` §4.6: *«Si ricava, non si chiede: somma le potenze delle macchine che
  generano calore e confronta con la soglia… il conto è aritmetica, non
  dimensionamento.»* E §9 mette il regime fra le quattro cose da cui dipende tutta la
  catena.
- `schemi/project.schema.json`, descrizione di `PlantRegime`: *«È un dato d'ingresso
  dichiarato dal progettista, mai calcolato: la taglia non la decide la skill (D-104),
  **nemmeno sommando le potenze che il testo nomina**.»*

Sono due prescrizioni opposte sulla stessa identica operazione, e la seconda sembra
scritta apposta per vietare la prima. Ho seguito **§4.6**, perché le istruzioni sono il
documento che governa questo lavoro e perché dicono esplicitamente di sé «queste
istruzioni bastano da sole»; ho scritto `plant_regime: "up_to_35_kw"` e ho aggiunto a13
per rendere visibile il conto. Ma se vale la regola dello schema, quel campo va omesso e
sostituito da una domanda. **Le due fonti vanno riconciliate**: chi legge il grafo non ha
modo di sapere quale delle due ha vinto.

### 3.2 Punti dove le istruzioni mi lasciano scegliere senza darmi un criterio

**a) Che cos'è una rete, quando il testo e l'idraulica non concordano.**
§4.2 dà due criteri che qui puntano in direzioni diverse: *«una rete è un circuito che il
testo nomina o distingue»* (e il testo nomina «il circuito di climatizzazione» e lo
distingue dalla produzione ACS) e *«il fluido cambia dove una macchina lo cambia; sono
due reti»* (e qui il fluido non cambia mai, sul primario). Non c'è una regola che dica
quale dei due comanda quando divergono. E se si sceglie di dividere, non c'è **nessun
criterio** per dire a quale delle due reti appartengano i tratti condivisi — la mandata
dalla pompa di calore alla valvola, e il ritorno dal raccordo alla pompa di calore.
Ho scelto una rete sola e l'ho dichiarata (a12), ma la scelta è mia, non delle istruzioni.

**b) Quale porta usare, fra due porte gemelle.**
La valvola deviatrice ha `out_a` e `out_b`, identiche per fluido e verso; il raccordo di
confluenza ha `a` e `c`, identiche allo stesso modo. Nessuna riga delle istruzioni dice
quale ramo attaccare a quale. Ho seguito **l'ordine in cui il testo li nomina**
(climatizzazione su `out_a`, bollitore su `out_b`; ritorno dal volume su `a`, ritorno dal
serpentino su `c`). È una convenzione che mi sono dato io. Non l'ho messa in
`assumptions` perché non cambia il disegno, ma è comunque una scelta senza criterio: se
il pezzo successivo della catena dà un significato a `out_a` contro `out_b` (per esempio
per l'impaginazione), la mia scelta diventa arbitraria in modo visibile.

**c) Il titolo da cui ricavare `project_id`.**
§3 dice di costruirlo «dal titolo dell'impianto». Il titolo del testo è «Esempio 2 –
Pompa di calore con deviazione tra climatizzazione e ACS». Non c'è un criterio su cosa
tenere: ho lasciato cadere la numerazione d'esempio e tenuto la parte descrittiva
(`pompa-di-calore-deviazione-climatizzazione-acs`). Un altro agente ne avrebbe scritto
uno diverso, e nessuno dei due sarebbe sbagliato.

**d) Il formato di `source_message_refs`.**
§3 dice che si può usare «per citare la frase del testo». Lo schema accetta stringhe
qualunque. Non è detto se ci vada la frase letterale, un numero di riga o un
identificatore. Ho messo la **frase letterale**, troncata dove era lunga.

### 3.3 Punti dove la regola c'è ma non copre il caso che avevo davanti

**a) La regola dei raccordi è scritta per flussi che si uniscono davvero.**
§4.4 dice *«dove il testo fa incontrare N tubazioni in un punto, servono N−1 raccordi»*, e
il caso 3 parla di *«N ritorni che rientrano sullo stesso attacco di una macchina»*. Qui i
due rami sono **alternativi**, non paralleli: la valvola deviatrice fa sì che i due flussi
non coesistano mai. Idraulicamente non si «uniscono»; topologicamente sì, perché due tubi
finiscono sullo stesso attacco. Ho applicato la regola generale (un attacco, una
tubazione) perché la regola dura di §4.3 non ammette eccezioni, ma le istruzioni non
prevedono il caso «rami alternativi che rientrano su un attacco solo» e non dicono se il
raccordo sia trascrizione obbligata o assunzione. L'ho trattato come **assunzione**
(a4), scegliendo la lettura più prudente.

**b) `carries_on_board` non è mai nominato nelle istruzioni.**
§4.1 dice di scegliere sui mestieri e sugli attacchi; §6 tipo A porta l'esempio del
circolatore e dice *«si segue quello che il catalogo dichiara per la voce scelta»*, ma
non dice **dove** il catalogo lo dichiara. Ho letto il campo `carries_on_board:
["circulation"]` della pompa di calore come quella dichiarazione. È un'interpretazione
plausibile e non contraddetta, ma è mia: le istruzioni non spiegano il campo.

**c) Quando una voce di catalogo porta un mestiere in più di quelli descritti.**
§4.1 insegna a scegliere sui mestieri e sugli attacchi, e a non ripiegare su una voce
sbagliata. Non dice cosa fare quando la voce giusta per gli attacchi dichiara **in
sovrappiù** un mestiere che il testo non nomina — qui la separazione idraulica del volume
a quattro attacchi. La cosa non è innocua: `naming/families.json` dice che «un pezzo che
fa più mestieri prende la prima famiglia che combacia», e in quell'ordine la separazione
idraulica viene prima dell'accumulo, quindi a valle il volano dell'ingegnere si chiamerà
«separatore». L'ho dichiarato (a7) per non lasciarlo silenzioso.

**d) I confini di rete: autorizzati o inventati?**
§4.3 dice *«per acquedotto e utenze il catalogo ha le voci di confine»*, che si legge come
un'autorizzazione. §6 dice *«mai inventare… collegamenti che il testo non descrive»*, e
il testo non nomina né l'acquedotto sanitario né le utenze — dice solo che l'acqua fredda
«entra» e l'ACS «viene prelevata». Ho aggiunto i due confini e l'ho dichiarato (a11).
Le istruzioni non chiariscono se in questo caso la dichiarazione serva o sia rumore.

**e) La reversibilità va dichiarata «sul circuito»: quale?**
§4.2 chiede di mettere in `assumptions` che la macchina è reversibile e che «quel
circuito» porta anche il raffrescamento. Qui i circuiti che portano il raffrescamento sono
due (primario e secondario), mentre il ramo verso il bollitore non lo porta mai. Ho
scritto l'assunzione riferendola a entrambi i circuiti di climatizzazione ed escludendo
implicitamente il ramo sanitario; le istruzioni parlano al singolare e non prevedono il
caso di un primario che serve anche l'ACS.

### 3.4 Una divergenza minore, che le istruzioni risolvono da sole

Il §2 indica i file per percorso di repository (`examples/layout/catalog/*.json`,
`schemas/project.schema.json`), mentre nella mia cartella si chiamano `catalogo/` e
`schemi/`. Non è un conflitto: §2 dice esplicitamente che «se i file ti arrivano copiati
in un'altra cartella, valgono lo stesso: contano i contenuti, non i percorsi». Lo segnalo
solo perché un agente meno attento potrebbe leggerlo come un invito ad andare a cercarli
nel repository, e quindi a rompere l'isolamento.

---

## 4. Isolamento

Ho letto **solo** file dentro la mia cartella di lavoro: `ISTRUZIONI.md`,
`testo-del-committente.txt`, i 53 file di `catalogo/`, `naming/families.json`,
`naming/media.json`, `schemi/project.schema.json`.

Fuori dalla cartella ho eseguito **una sola cosa**, il comando di validazione del §8 passo
7, lanciato dalla radice del repository come le istruzioni prescrivono. Nessun output:
il file carica. Non ho aperto, elencato, cercato né ispezionato nessun file di
`/home/user/DisegnatoreMEP` — né esempi, né prove, né documentazione, né codice.

**Nessuna infrazione da dichiarare.**
