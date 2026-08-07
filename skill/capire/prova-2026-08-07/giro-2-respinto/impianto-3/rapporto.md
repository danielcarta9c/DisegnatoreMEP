# Rapporto — Esempio 3, pompa di calore diretta su pavimento radiante

Committente «Nove C», codice di commessa «PROVA», revisione 00, data 2026-08-07.
Consegna: `consegna/grafo.json` (scritto e validato per primo), `consegna/rilettura.md`, questo file.

---

## 1. Cosa ho capito dell'impianto

Un impianto piccolo e lineare, fatto di **due parti che non si toccano**.

**La parte di riscaldamento è un unico circuito chiuso, senza primario e senza secondario.**
Una pompa di calore aria-acqua da 8 kW manda l'acqua *direttamente* al collettore del pavimento
radiante — il testo esclude il separatore idraulico, e questo è il punto che decide la lettura:
senza separatore non ci sono due circuiti, ce n'è uno solo, e nel grafo c'è una sola rete
`heating_water`. Dal collettore partono i circuiti ambiente; i loro ritorni si riuniscono e
attraversano in serie un volume tecnico da 50 litri a due tubi, che sta **sul ritorno**, e da lì
l'acqua rientra nella pompa di calore. Il volano non separa e non fa da polmone di un secondario:
serve, dice il testo, ad aumentare il contenuto d'acqua e a stabilizzare il funzionamento della
macchina — perciò è la voce di catalogo a due attacchi (`buffer-two-port`, solo `thermal_storage`)
e non una a quattro attacchi, che separerebbe e cambierebbe l'impianto.

Nessun circolatore compare come pezzo: il testo lo dichiara integrato nella pompa di calore, e la
voce di catalogo scelta lo conferma (`carries_on_board: ["circulation"]`).

**La parte sanitaria è staccata.** Un boiler in pompa di calore da 200 litri, dedicato, dichiarato
*non collegato idraulicamente* al riscaldamento. È una macchina che il calore se lo fa da sola e
l'acqua calda se la tiene in serbo: nel catalogo è la voce che dichiara **entrambi** i mestieri
(`heat_generation` + `dhw_storage`, `stored_medium: domestic_hot_water`) e che non ha nessun
serpentino da alimentare. Nel grafo è un ramo aperto: acqua fredda in ingresso, acqua calda in
uscita, e non un solo tubo verso il circuito radiante.

**Il regime della centrale**: 8 kW è l'unica potenza scritta, 8 ≤ 35, quindi `up_to_35_kw`.

Il conto finale: 9 componenti, 9 tubazioni, 3 reti (riscaldamento, acqua fredda, acqua calda
sanitaria), 9 voci dichiarate.

---

## 2. Le domande e le assunzioni, in chiaro

Sono le nove voci di `assumptions`, tutte con `status: "proposed"`. Le prime due **cambiano il
disegno** e sono quelle da portare all'ingegnere; le altre sette sono dichiarazioni perché nulla
di quello che ha scritto vada perso.

### Le due che cambiano il disegno

**D1 — Quanti sono i circuiti ambiente?** (`a1`)
Il testo dice che il collettore «alimenta più circuiti ambiente» senza darne il numero. La voce di
catalogo del collettore ha esattamente due uscite, entrambe obbligatorie: ho disegnato due
circuiti radianti rappresentativi, uno per uscita. Se i circuiti sono tre o più, il numero va
detto e il collettore va rappresentato diversamente.

**D2 — Come si raccolgono i ritorni dei circuiti ambiente?** (`a2`)
Il collettore, a catalogo, dichiara solo le uscite di mandata: attacchi per i ritorni non ne ha.
Il testo non dice con che pezzo i ritorni si riuniscono prima del volume tecnico. Ho assunto una
confluenza a T (§4.4: due ritorni su un solo attacco → 2−1 = 1 raccordo). Se in centrale c'è un
collettore di ritorno, va detto: **in catalogo non c'è una voce che lo rappresenti.**

### Le sette dichiarazioni

**A3 — Il circolatore non è disegnato.** Il testo lo dice integrato nella pompa di calore, e la
macchina di catalogo lo porta a bordo: nel grafo non c'è nessun circolatore, ed è voluto.

**A4 — Il separatore idraulico è escluso dal testo.** Non è disegnato perché non c'è, non perché
sia stato perso. La mandata arriva direttamente al collettore, come dice «alimenta direttamente».

**A5 — Carico automatico e scarico sul volume tecnico.** Il testo li prevede; sono ferramenta di
servizio (`filling`, `drain`) e li aggiunge il pezzo della catena che completa il grafo, non questa
prima stesura. La nomina è scritta perché non vada persa: il volano ha già a catalogo gli attacchi
di servizio (`drain`, `vent`, `probe`) a cui appenderli, e li ho lasciati liberi apposta.

**A6 — La regolazione di zona non è topologia.** È una logica: nel grafo non produce né nodi né
tubi. Il testo non nomina valvole di zona e io non ne ho disegnate. Se sulle partenze del
collettore ci sono organi di regolazione da rappresentare, vanno detti.

**A7 — I due confini della parte sanitaria.** Il testo non nomina né l'allacciamento dell'acqua
fredda né le utenze, ma il boiler ha due attacchi obbligatori (freddo in ingresso, acqua calda in
uscita) e un circuito sanitario è aperto per definizione: ho aggiunto i due confini di catalogo
per chiuderlo. È così?

**A8 — Come è stato ricavato il regime.** Ho sommato l'unica potenza scritta, gli 8 kW della
pompa di calore aria-acqua. Del boiler in pompa di calore il testo dà solo il volume, 200 litri:
per lui non ho sommato niente. Anche volendo sommarne la potenza, la somma non si avvicina ai
35 kW — ma il dato è dell'ingegnere: se la potenza c'è, va detta.

**A9 — Il ricircolo sanitario.** Il testo non ne parla, e nel grafo l'acqua calda va dal boiler
alle utenze e basta. Se un anello di ricircolo c'è, va detto: il boiler in pompa di calore, a
catalogo, l'attacco per riceverlo non ce l'ha.

---

## 3. Dove le istruzioni non mi hanno dato un criterio

Questa è la parte che la prova misura. Sette punti, dal più pesante al più leggero.

### 3.1 Contraddizione — «un terminale rappresentativo» contro «gli attacchi obbligatori si collegano tutti»

§7 dice: un plurale vago si rappresenta con **un solo** componente della famiglia giusta.
§4.3 dice: dopo aver collegato, un attacco `required: true` rimasto libero vuol dire che hai perso
un collegamento. Il collettore di catalogo (`zone-manifold`) ha **due** uscite, `out_1` e `out_2`,
**entrambe obbligatorie**.

Le due regole non possono valere insieme: seguendo §7 disegno un solo circuito radiante e lascio
`out_2` libero (attacco obbligatorio scoperto); seguendo §4.3 disegno due circuiti e con ciò
scrivo una **quantità che il testo non dà** — proprio quello che §6 vieta («quanti terminali»).
Le istruzioni non dicono quale regola vince.

**Cosa ho fatto e perché:** ho disegnato due circuiti. Il testo dice «più circuiti», cioè almeno
due, quindi il secondo circuito non è inventato dal nulla: è il plurale scritto dall'ingegnere,
ed è il minimo che il plurale consente. Il numero vero resta la domanda D1. La strada opposta —
un circuito solo — avrebbe consegnato un grafo che *nega* il plurale del testo e con un attacco
obbligatorio scoperto: mi è parsa peggiore su entrambi i fronti.

### 3.2 Vuoto — una voce di catalogo che rappresenta solo metà di quello che il testo descrive

§4.1 dà due esiti soli: la voce combacia, oppure «nessuna voce combacia» e allora il pezzo **non si
disegna** (tipo B). Non c'è il caso di mezzo, che è esattamente il caso qui: il collettore esiste
in catalogo, ha il mestiere giusto (`distribution`) e gli attacchi giusti **per la mandata**, ma
non ha nulla per il lato ritorno — mentre un collettore di pavimento radiante, nella realtà e nel
testo, è mandata **e** ritorno.

Preso alla lettera, §4.1 direbbe di non disegnare il collettore: gli attacchi non permettono di
scrivere «esattamente» i collegamenti descritti. Ma il collettore è nominato dal testo e il lato
mandata è descritto senza ambiguità: buttarlo via sarebbe stato perdere un'affermazione esplicita
dell'ingegnere.

**Cosa ho fatto e perché:** ho usato il collettore per la mandata e ho chiuso i ritorni con la
confluenza a T di §4.4, dichiarando entrambe le cose in `a2` — l'assunzione del raccordo (tipo A)
e la mancanza in catalogo di una voce «collettore di ritorno» (tipo B). Un pezzo detto dal testo
resta nel grafo; quello che il catalogo non sa dire è scritto nero su bianco.

### 3.3 Vuoto — il regime quando le potenze ci sono solo per alcune macchine

§4.6 prevede due casi: il testo dà le potenze (somma e confronta) oppure non le dà (ometti il
campo e chiedi). Non prevede il caso reale di questo impianto: il testo dà la potenza di **un**
generatore (8 kW) e non dell'altro. E il boiler in pompa di calore è, a catalogo, una macchina che
dichiara `heat_generation`: rientra nella lettera di «somma le potenze delle macchine che generano
calore».

Manca anche un secondo criterio: §4.6 dice «il regime **della centrale**», ma non dice se una
macchina sanitaria **idraulicamente separata** dalla centrale entri o no in quella somma.

**Cosa ho fatto e perché:** ho scritto `up_to_35_kw` sommando i soli 8 kW scritti, e ho dichiarato
in `a8` che cosa ho sommato e che cosa no. Qui le due letture (contare o non contare il boiler)
portano allo stesso risultato — nessuna potenza dichiarata da aggiungere, e comunque nessun
avvicinamento alla soglia — quindi la mancanza di criterio non ha cambiato il grafo. Ma su un
impianto diverso l'avrebbe cambiato, e va segnalato.

### 3.4 Tensione — aggiungere i confini sanitari è trascrizione o invenzione?

§6 vieta «collegamenti che il testo non descrive». Il testo non nomina l'acquedotto, non nomina le
utenze: dice solo che il boiler produce l'ACS. §4.3 però dice che i circuiti sanitari «entrano
dall'acquedotto, escono alle utenze» e che il catalogo ha apposta le voci di confine; e i due
attacchi del boiler sono obbligatori. Le istruzioni non dicono a chiare lettere che un attacco
obbligatorio verso l'esterno **autorizza** ad aggiungere il confine.

**Cosa ho fatto e perché:** l'ho letto come tipo A — il testo *impone* il collegamento (produrre
acqua calda sanitaria vuol dire acqua fredda che entra e acqua calda che esce) ma non nomina il
pezzo — e ho chiuso con i due confini di catalogo, dichiarando in `a7`. L'alternativa, lasciare
scoperti due attacchi obbligatori su una macchina che il testo descrive come funzionante,
avrebbe consegnato un grafo mutilo.

### 3.5 Scelta senza criterio — i nomi delle chiavi in `properties`

§3 dice di trascrivere i dati «come stanno» e dà esempi di chiavi (`potenza`, `volume`, `modello`,
`tipo`, `configurazione`), ma non c'è un elenco chiuso e non c'è una regola per le frasi che non
sono né un dato né una qualifica secca — per esempio «con funzione di aumento del contenuto
d'acqua e stabilizzazione del funzionamento della pompa di calore».

**Cosa ho fatto:** ho usato le chiavi degli esempi dove combaciavano (`potenza`, `volume`, `tipo`,
`configurazione`) e ho aggiunto `funzione` e `regolazione` per le due frasi che non ci stavano.
Sono nomi miei: se a valle qualcuno li legge per chiave, va fissato un vocabolario.

### 3.6 Scelta senza criterio — il `project_id` quando il titolo porta un numero di raccolta

§3 dice di costruire il `project_id` «dal titolo dell'impianto». Il titolo scritto è «Esempio 3 –
Pompa di calore diretta su pavimento radiante»: la parte «Esempio 3» è un numero della raccolta da
cui il testo viene, non un pezzo del nome dell'impianto. Le istruzioni non dicono se il titolo si
prende alla lettera o si ripulisce.

**Cosa ho fatto:** l'ho ripulito — `pompa-di-calore-diretta-su-pavimento-radiante` — perché §3 dice
che il `project_id` identifica il documento e non è una sigla di commessa, e «esempio-3» sarebbe
stato un riferimento alla raccolta, non all'impianto. Lo stesso titolo ripulito è finito in
`project_name`, campo che le istruzioni nominano nell'esempio ma non spiegano.

### 3.7 Minuzia — due voci di catalogo diverse con lo stesso mestiere e lo stesso simbolo

§4.4 chiama il primo raccordo «raccordo a T» (confluenza) e il secondo «ripartizione a T». In
catalogo sono `tee-junction` e `tee-split`, e **dichiarano lo stesso mestiere** (`junction`) e lo
stesso `symbol_id`: si distinguono solo dal verso degli attacchi. Il metodo di §4.1 — scegli per
mestiere, poi per attacchi — funziona lo stesso, perché il verso degli attacchi decide; ma il
mestiere da solo non basta a scegliere, e le istruzioni presentano i due pezzi come se fossero due
famiglie diverse. Qui non ha prodotto nessun dubbio: servivano due entrate e un'uscita, cioè
`tee-junction`.

---

## 4. Nota sull'isolamento

Ho letto soltanto file dentro la mia cartella di lavoro: `ISTRUZIONI.md`,
`testo-del-committente.txt`, i 53 file di `examples/layout/catalog/`, `naming/families.json`,
`naming/media.json`, `schemas/project.schema.json`. Non ho aperto, elencato, cercato né ispezionato
nulla in `/home/user/DisegnatoreMEP`.

L'unica cosa eseguita fuori dalla cartella è il comando di validazione di §8, passo 7, lanciato
dalla radice del repository sul file in `consegna/`, come le istruzioni prescrivono: nessun output,
il file carica. Nessuna infrazione da dichiarare.
