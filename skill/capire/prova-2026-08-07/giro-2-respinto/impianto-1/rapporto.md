# Rapporto di lavoro — impianto 1

Committente **Nove C**, commessa **PROVA**, revisione **00**, data **2026-08-07**.
Consegna: `consegna/grafo.json` (salvato per primo e validato), `consegna/rilettura.md`, questo file.

---

## 1. Cosa ho capito dell'impianto

Una piccola centrale a pompe di calore, con un solo serbatoio che fa due lavori.

**Generazione.** Due pompe di calore aria-acqua da 12 kW ciascuna, in parallelo. Sommate
fanno 24 kW di generazione: sotto la soglia dei 35 kW, quindi `plant_regime: "up_to_35_kw"`.
Il fatto che una sia master e l'altra slave è logica di regolazione: sul grafo le due
macchine sono identiche e collegate allo stesso modo, e la gerarchia non si vede.
Il «parallelo» l'ho trascritto con due raccordi a T: una confluenza dove le due mandate si
uniscono verso il volume, una ripartizione dove il ritorno si divide fra le due macchine.

**Il volume, che è il perno di tutto.** L'accumulo ECOcombi da 200 litri è insieme
*volume tecnico a quattro tubi* e *produttore istantaneo di ACS*. Nel catalogo c'è una
sola voce che regge entrambe le cose — quattro attacchi di riscaldamento (primario dai
generatori, secondario verso l'impianto) **più** gli attacchi del serpentino sanitario —
ed è quella che ho scelto. Il suo fluido in serbo è acqua di riscaldamento, e questo è il
punto che dice come i circuiti toccano il serbatoio: il primario e il secondario pescano
nella riserva; il sanitario, invece, la **attraversa** scambiando calore, entra freddo
dall'acquedotto nel serpentino ed esce caldo alle utenze, senza mai mescolarsi. Per questo
l'ACS non è accumulata: è istantanea, come dice il testo.

**Distribuzione.** Dal lato secondario del volume parte un circuito con circolatore
dedicato che alimenta i radiatori esistenti, «direttamente», cioè senza miscelazione. È un
circuito chiuso: l'acqua va ai radiatori e torna al volume, e disegnare il ritorno è
trascrizione, non invenzione.

**Sanitario.** Circuito aperto: acquedotto → serpentino → utenze. Due reti, perché il
fluido cambia dove la macchina lo cambia. Il ricircolo è escluso dal testo, esplicitamente.

**In cifre:** 9 componenti, 11 tubazioni, 4 reti (primario e secondario in acqua di
riscaldamento, acqua fredda, ACS), 10 voci in `assumptions`. Tutti i `tag` sono `null`:
l'ingegnere non scrive nessuna sigla. `subsystems`, `rule_applications` e `sheets` sono
liste vuote. Il file carica con il comando del §8 passo 7 senza output.

**Cosa non ho disegnato, e perché.** Nessun accessorio: niente valvole, sfiati, vasi,
filtri, strumenti. Nessun circolatore sul circuito primario (la voce di catalogo delle
pompe di calore dichiara la circolazione a bordo). Nessun gruppo di riempimento e nessun
attacco di scarico sul volume, benché il testo li nomini: sono ferramenta, e restano al
pezzo successivo della catena. Gli attacchi di servizio del volume (sfiato, scarico, sede
sonda) sono lasciati liberi apposta.

---

## 2. Le domande e le assunzioni, in chiaro

Sono le dieci voci di `assumptions` nel grafo, tutte con `status: "proposed"`.
**Nessuna è di tipo C**: non ho trovato in questo testo un bivio in cui due letture
ugualmente corrette producano due grafi diversi. Le voci aperte sono tutte di tipo A —
il grafo si chiude nel modo convenzionale e la scelta è dichiarata — oppure sono
registrazioni di cose che il testo dice e che il grafo, per regola, non mostra.

| id | Tipo | Cosa dice |
|---|---|---|
| `a1` | A — **domanda** | Il testo dice «installate in parallelo» ma non dice **con che pezzo** i due flussi si uniscono e si dividono: un collettore? un separatore? semplici raccordi? Ho usato i raccordi a T (una confluenza sulla mandata, una ripartizione sul ritorno). Va bene, o in centrale c'è un pezzo di distribuzione da rappresentare? |
| `a2` | registrazione | Le due macchine sono «una master e una slave»: è regolazione, non topologia, e sul grafo non si vede. Il testo non dice nemmeno quale delle due sia la master, quindi il ruolo non è stato attribuito a nessuna. |
| `a3` | A — **domanda** | Il testo non dice se il circuito primario ha circolatori dedicati o se la circolazione è a bordo delle pompe di calore. Ho seguito la voce di catalogo, che la dichiara a bordo: sul primario non è disegnato alcun circolatore. È così? |
| `a4` | A — decisione dichiarata | Il testo dice «circolatore dedicato» ma non dice su quale ramo sta. L'ho messo sulla **mandata** che esce dal volume verso i radiatori: è la posizione convenzionale di disegno, non una prescrizione ricavata dal testo. Se va sul ritorno, si sposta. |
| `a5` | A — **domanda** | «L'impianto esistente a radiatori» non dice quanti sono: ho disegnato **un solo radiatore**, rappresentativo. Quanti corpi scaldanti sono davvero, e vanno rappresentati singolarmente o come unico terminale? |
| `a6` | registrazione | Il secondario alimenta i radiatori «direttamente»: nessuna valvola miscelatrice di circuito, perché il testo non ne nomina e quella parola dice che non c'è miscelazione. |
| `a7` | registrazione | Il serpentino sanitario è **interno** all'accumulo: non è disegnato come scambiatore a sé, è rappresentato dagli attacchi sanitari del volume. Ne segue che il sanitario è istantaneo e non c'è accumulo di ACS. |
| `a8` | registrazione | Il testo **esclude** il ricircolo sanitario: non è disegnato perché non c'è, non perché sia stato perso. Chi completa il grafo non lo aggiunga. |
| `a9` | registrazione | Il carico automatico da acquedotto e lo scarico sul volume sono nominati dal testo ma sono ferramenta (`filling`, `drain`): fuori dal grafo di prima stesura, li aggiunge il pezzo che completa. La nomina è registrata perché non vada persa. |
| `a10` | registrazione | Il regime della centrale è **ricavato**, non chiesto: 12 + 12 = 24 kW ≤ 35 → `up_to_35_kw`. Sommate le sole pompe di calore, nella forma in cui il testo dà la potenza. |

Le due voci che chiedono davvero una risposta all'ingegnere, e che ripeto anche nella
risposta finale, sono **`a1`** (con che pezzo si fa il parallelo), **`a3`** (circolazione a
bordo o esterna sul primario) e **`a5`** (quanti radiatori). Le altre sono decisioni prese
e dichiarate, o registrazioni perché nulla vada perso.

---

## 3. Dove le istruzioni non mi hanno detto cosa fare

Questa è la parte per cui esiste la prova. Elenco i punti in cui ho dovuto decidere senza
un criterio scritto, o in cui due paragrafi tiravano in direzioni opposte. Sono ordinati
da quello che pesa di più a quello che pesa di meno.

### 3.1 Contrasto vero: la derivazione è ammessa dal §5 e resa inservibile dal §4.3

Il §4.4 prevede le derivazioni («il pezzo con un braccio che esce dal percorso») e il §5
mette `branch_off` nella lista dei mestieri **che entrano nel grafo**. Ma nel catalogo le
tre voci di derivazione hanno il terzo attacco marcato `stub: true`, e il §4.3 dice, senza
eccezioni: *«gli attacchi segnati `stub: true` sono attacchi di servizio… Tu non ci
colleghi niente.»* Il braccio della derivazione è dunque un attacco a cui è vietato
collegare, e la derivazione non è utilizzabile in nessun caso: due paragrafi ammettono un
pezzo che un terzo rende inservibile. Su questo impianto non mi ha toccato — il testo non
descrive nulla che si stacchi da un tubo — ma su un impianto con una derivazione descritta
il conflitto si presenterebbe subito.

### 3.2 Un'affermazione topologica del testo che le regole vietano di disegnare

«Sul volume tecnico sono previsti anche il collegamento per il **carico automatico
dell'impianto da acquedotto** e lo scarico.» Questa frase dice due cose insieme: nomina
della ferramenta (che per il §5 resta fuori) **e** un fatto topologico — l'acquedotto tocca
il circuito di riscaldamento. Il §5 mi dice di lasciar fuori il pezzo e di registrarne la
nomina; nessun paragrafo mi dice cosa fare del legame fra le due reti, che il testo
afferma e che nel grafo non compare. Non c'è nemmeno un pezzo ammesso per rappresentarlo:
il gruppo di riempimento è ferramenta. Ho scelto di **solo dichiararlo** (`a9`), perché la
regola del §5 è categorica; ma è il punto in cui il grafo dice meno del testo, e il
criterio per decidere non c'è.

### 3.3 Le due istruzioni su «master e slave» tirano in direzioni opposte

Il §3 dice di trascrivere in `properties` «le qualifiche che il testo usa». Il §4.5 dice
che master, slave, cascata e priorità sono **regolazione** e vanno in `assumptions`. La
stessa parola del testo cade sotto due regole diverse. Ho scelto `assumptions` — il §4.5 è
la regola specifica, il §3 quella generale — e con un motivo in più: il testo dice che una
è master e una è slave, ma **non dice quale**, quindi scriverlo in `properties` avrebbe
richiesto che scegliessi io a quale macchina attribuirlo, cioè un'invenzione.

### 3.4 Le chiavi delle `properties` non sono normate da nessuna tabella

Il §3 dà esempi (`potenza`, `volume`, `modello`, `tipo`, `configurazione`) ma non un
vocabolario chiuso, e non c'è una tabella dei nomi delle proprietà come ce n'è per i
mestieri e per i fluidi. Ho scelto io i nomi delle chiavi (`potenza`, `tipo`, `modello`,
`volume`, `configurazione`, `produzione_sanitaria`, `stato`). Due agenti diversi
produrrebbero chiavi diverse a partire dallo stesso testo, e nulla nelle istruzioni li
riallinea.

### 3.5 Manca il confine fra «trascrivere una qualifica» e «riassumere una frase»

Il §3 dice che trascrivere le qualifiche «non costa nulla». Ma «utilizzato… per la
produzione istantanea di acqua calda sanitaria tramite serpentino interno» è una frase, non
una qualifica: trascriverla in `properties` è a metà fra la citazione e il riassunto. Ho
adottato un criterio mio — trascrivo ciò che **identifica** la macchina o il circuito
(`produzione_sanitaria`, `configurazione`, `stato: "esistente"`), lascio fuori il resto —
ma è un criterio che mi sono dato io, non uno che ho letto.

### 3.6 Il catalogo non distingue per mestiere i due raccordi del §4.4

Il §4.1 insegna a scegliere **prima** per mestiere e **poi** per attacchi, e avverte:
«mai scegliere per somiglianza di nome». Ma il raccordo a T e la ripartizione a T
dichiarano **lo stesso mestiere** (`junction`) e persino lo stesso simbolo: a distinguerli
sono solo gli attacchi, e in parte il nome. La regola «scegli per mestiere» qui non
seleziona nulla, e il §4.4 di fatto mi chiede di sceglierli **per nome** («il raccordo a T
è due entrate e un'uscita»). Ho scelto sugli attacchi, che è ciò che il §4.1 mette al
secondo posto, e il risultato coincide col nome — ma i due paragrafi non dicono la stessa
cosa.

### 3.7 «Non inventare numerazioni» e «id parlanti» si toccano

Il §3 dice che i `tag` non si numerano («non inventare numerazioni») e, tre righe sopra,
porta `pdc-1` come esempio di **id** parlante ammesso. Due macchine identiche vanno
distinte per forza, e l'unica distinzione possibile è un numero. Ho usato `pdc-1` e `pdc-2`
appoggiandomi all'esempio; ma la frase «non inventare numerazioni» non dice esplicitamente
che vale solo per i `tag`, e a prima lettura sembra vietare anche questo.

### 3.8 `carries_on_board` non è mai nominato dalle istruzioni

L'assunzione `a3` nasce dal §7 e dall'esempio del §6 tipo A («si è seguita la macchina di
catalogo, che lo porta a bordo»). Nel catalogo la cosa è scritta in un campo che le
istruzioni non nominano mai: `carries_on_board: ["circulation"]`. Ho interpretato quel
campo come «quello che il catalogo dichiara per la voce scelta», ma è un'interpretazione:
le istruzioni descrivono `functions`, `ports`, `stub`, `flow`, `stored_medium`, e si
fermano lì. Lo stesso vale per `traits` e `fills_from`, che ho ignorato.

### 3.9 La lista `assumptions` fa tre lavori diversi senza un campo per distinguerli

Ci finiscono, tutte insieme: le domande aperte (`a1`, `a3`, `a5`), le decisioni prese e
dichiarate (`a4`), le registrazioni di cose che il testo **dice** e il grafo non mostra
(`a2`, `a6`, `a7`, `a8`, `a9`), e le note di trasparenza su un dato ricavato (`a10`). Lo
schema offre solo `status`, che è un ciclo di approvazione, non un tipo. Le istruzioni non
dicono se i tre tipi vadano marcati, né in che ordine elencarli, né quanto sia troppo. Ho
scelto di scriverli tutti e di distinguerli nella prosa; un altro agente potrebbe
legittimamente consegnare tre voci invece di dieci.

### 3.10 Il «circuito primario» è una rete che il testo non nomina

Il §4.2 dice che una rete è «un circuito che il testo nomina o distingue». Il testo nomina
esplicitamente solo il «circuito secondario». Il primario esiste per implicazione: perché
c'è un secondario, e perché i generatori alimentano il volume. Rientra in «distingue», ma
di stretta misura — e il criterio per decidere quando un circuito è *distinto abbastanza*
da meritare una rete propria non c'è.

### 3.11 Il titolo da cui costruire il `project_id`

Il §3 dice di costruire il `project_id` «dal titolo dell'impianto». Il testo ha
un'intestazione, «Esempio 1 – Due pompe di calore in parallelo con accumulo combinato»: ho
tolto «Esempio 1 –» perché è la numerazione della raccolta e non il titolo dell'impianto,
ma è una decisione mia. Non c'è un vincolo di lunghezza, e il risultato è un id di 54
caratteri.

### 3.12 Due dettagli minori, per completezza

- **`plant_regime` assente:** il §3 dice «ometti il campo», lo schema prevede `null` come
  valore ammesso. Le due cose non coincidono. Qui non mi ha toccato, perché le potenze
  c'erano.
- **Potenza non qualificata:** il §4.6 dice cosa fare se la potenza è data «in una forma
  diversa» (resa, assorbita). Il testo dice «12 kW» e basta. Ho sommato quello che c'è
  scritto, dichiarandolo in `a10`, perché il §6 vieta espressamente di chiedere le potenze:
  ma di una potenza non qualificata il §4.6 non parla.

---

## 4. Isolamento

Non ho aperto, letto, elencato né cercato alcun file fuori dalla mia cartella di lavoro.
Ho eseguito una sola volta il comando di validazione del §8 passo 7, che per costruzione
parte dalla radice del repository: quella è l'eccezione prevista, e non ha comportato la
lettura di alcun contenuto. **Nessuna infrazione da dichiarare.**
