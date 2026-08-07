# Rapporto — Esempio 1, due pompe di calore in parallelo con accumulo combinato

Committente: Nove C · Commessa: PROVA · Revisione 00 · 7 agosto 2026
Consegna: `consegna/grafo.json`, `consegna/rilettura.md`, questo rapporto.

---

## 1. Cosa ho capito dell'impianto

Una piccola centrale a pompa di calore con accumulo combinato, che fa riscaldamento e
sanitario con una macchina sola di accumulo.

**Generazione.** Due pompe di calore aria-acqua da 12 kW ciascuna, idraulicamente in
parallelo. Sommate fanno 24 kW di generazione: sotto la soglia dei 35 kW, quindi
`plant_regime = "up_to_35_kw"`. Master e slave descrivono come sono *gestite*, non come
sono *collegate*: sul grafo si vedono due macchine gemelle in parallelo.

**Il cuore dell'impianto è l'accumulo ECOcombi da 200 litri**, ed è il pezzo su cui si
gioca tutta la lettura. Fa tre mestieri insieme:

1. tiene in serbo **acqua di riscaldamento** (è il suo `stored_medium`);
2. **separa idraulicamente** il circuito dei generatori dal circuito dei radiatori — per
   questo ha quattro attacchi di flusso: primario mandata/ritorno verso le pompe di
   calore, secondario mandata/ritorno verso i radiatori. È questo il senso di «a quattro
   tubi»;
3. **produce l'acqua calda sanitaria in modo istantaneo** con un serpentino interno: il
   sanitario non è accumulato, **attraversa** il volume scambiando calore con l'acqua di
   riscaldamento che il volume tiene in serbo.

Il punto da non sbagliare è proprio il rovescio del bollitore: qui **non** c'è una
riserva di acqua calda sanitaria scaldata da un serpentino di riscaldamento; c'è una
riserva di acqua di riscaldamento attraversata da un serpentino sanitario. Il verso è
opposto, e la voce di catalogo scelta (`buffer-combined`, con `stored_medium:
heating_water` e i due attacchi `cold_in` / `dhw_out`) è l'unica che lo dica. Un
bollitore ACS (`dhw-cylinder`) avrebbe raccontato l'impianto al contrario.

**Riscaldamento.** Dal lato secondario del volume parte un unico circuito, con un
circolatore dedicato, che alimenta l'impianto esistente a radiatori e vi rientra. Niente
miscelazione, niente zone: «alimenta direttamente».

**Sanitario.** Circuito aperto e cortissimo: acquedotto → serpentino del volume → utenze.
Nessun ricircolo, escluso per iscritto.

**Quattro reti**, tutte idroniche: primario e secondario (acqua di riscaldamento),
acqua fredda di acquedotto, acqua calda sanitaria. Il fluido cambia dove la macchina lo
cambia — dentro il serpentino.

**Il grafo in numeri:** 9 componenti, 4 reti, 11 tubazioni, 10 voci in `assumptions`.
Nessun accessorio: né valvole, né vasi, né sfiati, né il gruppo di riempimento che il
testo nomina. Il file carica con lo strumento di validazione.

---

## 2. Domande e assunzioni, in chiaro

Sono le dieci voci di `assumptions`, tutte con `status: "proposed"`. Le prime sono
**domande** che aspettano una risposta; le ultime sono **note di tracciabilità**, perché
qualcosa che il testo dice non compare nel disegno e voglio che si veda che non è andato
perso.

### Domande all'ingegnere

1. **`a1` — Con che pezzo si realizza il parallelo?** Il testo dice «installate in
   parallelo» ma non dice *con cosa* i due flussi si uniscono. Ho usato un raccordo a T
   sulla mandata e una ripartizione a T sul ritorno (N=2 → N−1 = 1 per lato). Se in
   centrale c'è un collettore o un distributore, va rappresentato quello.
2. **`a3` — I circolatori del primario sono a bordo delle pompe di calore?** Il testo non
   nomina nessuna pompa fra le macchine e il volume. Ho seguito la voce di catalogo, che
   dichiara di portare la circolazione a bordo, e sul primario non ho disegnato niente.
3. **`a5` — Il circolatore del secondario sta sulla mandata?** Il testo dice «circolatore
   dedicato» senza dire su quale ramo. L'ho messo sulla mandata: è convenzione di
   disegno, non un dato dell'impianto. Se va sul ritorno, si sposta di un tubo.
4. **`a6` — Quanti sono i radiatori, e vanno raggruppati?** «L'impianto esistente a
   radiatori» è plurale e vago: ne ho disegnato uno solo, rappresentativo. Se servono
   zone o collettori di piano, il disegno cambia.
5. **`a10` — I 12 kW sono resi o assorbiti?** Il testo dice solo «12 kW». Li ho sommati
   come stanno (24 kW → piccola centrale). Se fossero potenze assorbite, la potenza resa
   sarebbe ben più alta e il regime andrebbe riverificato. Vedi anche il §3, punto 1:
   qui istruzioni e schema si contraddicono.

### Assunzioni di lettura e di disegno

6. **`a2` — Master e slave sono regolazione**, non topologia. In più il testo non dice
   *quale* delle due macchine sia la master: non ho attribuito il ruolo a nessuna delle
   due, perché sceglierlo sarebbe stato inventare.
7. **`a4` — Come ho letto l'ECOcombi**: accumulo combinato che tiene acqua di
   riscaldamento e produce il sanitario col serpentino interno; il serpentino è dentro
   la macchina e non è disegnato come scambiatore a sé. «A quattro tubi» l'ho letto come
   i quattro attacchi idraulici del volume, non come una distribuzione caldo+freddo a
   quattro tubi: il testo parla solo di riscaldamento e non descrive nessun circuito di
   raffrescamento.
8. **`a7` — Ho chiuso il circuito secondario.** Il testo dice che il circolatore alimenta
   i radiatori; un circuito di riscaldamento che va ai terminali torna. Il ritorno è
   trascrizione, non aggiunta.

### Note di tracciabilità (cose dette che il grafo non mostra)

9. **`a8` — Il ricircolo sanitario è escluso per iscritto**: non è disegnato perché non
   c'è, non perché sia stato perso. Chi completerà il grafo non deve riaggiungerlo.
10. **`a9` — Carico automatico e scarico sul volume tecnico**: sono ferramenta
    (riempimento e scarico) e non entrano nel grafo di prima stesura. La voce di catalogo
    del volume ha già gli attacchi di servizio (sfiato, scarico, sede sonda) lasciati
    liberi apposta. Ma vedi il §3, punto 4: qui c'è un buco vero nelle istruzioni.

**Domande di tipo C (quelle che cambiano il disegno e vanno decise dall'ingegnere prima
di andare avanti): nessuna.** Nessun punto soddisfa tutte e tre le condizioni del §6 —
la candidata più vicina era «raccordi o collettore?» (`a1`), ma il §4.4 dà il criterio
esplicito («se dice solo *in parallelo*, usa i raccordi e dichiara»), quindi è tipo A.

---

## 3. Dove le istruzioni non mi hanno detto cosa fare

Questa è la parte che la prova misura. Elenco in ordine di gravità.

### 1. Contraddizione netta: chi decide `plant_regime`

Le due fonti che ho ricevuto dicono il contrario l'una dell'altra.

- **ISTRUZIONI §4.6:** «**Si ricava, non si chiede:** somma le potenze delle macchine che
  generano calore e confronta con la soglia […] il conto è aritmetica, non
  dimensionamento». E il §6 rincara: quello che non si chiede mai è «qualunque cosa il
  testo abbia già scritto — a partire dalle potenze».
- **`schemi/project.schema.json`, descrizione di `PlantRegime`:** «È un **dato d'ingresso
  dichiarato dal progettista**, mai calcolato: la taglia non la decide la skill (D-104),
  **nemmeno sommando le potenze che il testo nomina**». E aggiunge che un progetto che
  non dichiara niente riceve il corredo minimo, cioè le regole del regime piccolo.

Non è una sfumatura: lo schema vieta esattamente l'operazione che le istruzioni
prescrivono, e con parole quasi identiche, come se una delle due fosse stata scritta per
smentire l'altra. **Ho seguito le istruzioni** (§4.6), perché sono il documento operativo
del mio lavoro, e ho scritto `up_to_35_kw` con l'assunzione `a10` che dichiara il conto.
Se vale invece la regola dello schema, il campo va omesso e la domanda va girata
all'ingegnere. Chiedo che le due fonti vengano allineate: così com'è, l'esito dipende da
quale documento l'agente legge per ultimo.

C'è anche un difetto di merito, sotto la contraddizione: la nota dello schema àncora la
soglia dei 35 kW alla «potenza dei focolari» della Raccolta R. **Una pompa di calore non
ha focolare.** Sommare 12+12 kW di pompe di calore e chiamarlo «regime della centrale» è
un conto che si può fare, ma non è il conto che la norma citata prevede. Le istruzioni
non dicono niente su cosa fare quando i generatori non sono a combustione — e in questo
impianto non lo sono.

### 2. Il «collegamento per il carico automatico da acquedotto»: topologia o ferramenta?

Il testo dice che sul volume tecnico c'è «il collegamento per il carico automatico
dell'impianto da acquedotto». Questa frase descrive **un tubo che va dalla rete
dell'acqua fredda al circuito di riscaldamento**: è un'affermazione topologica, e le
istruzioni al §4.3 e al §8 passo 6 chiedono che ogni affermazione topologica sia
rappresentata. Ma il §5 mette `filling` fra i mestieri che «non entrano mai», e il §7
dice che quando il testo nomina un accessorio per dire *dove* sta un attacco, resta
fuori.

Le due regole si applicano entrambe e danno esiti opposti. **Ho scelto di lasciarlo
fuori** (assunzione `a9`), perché il §5 è più esplicito e perché il gruppo di riempimento
è ferramenta a tutti gli effetti. La conseguenza però è visibile: nel grafo la rete
dell'acqua fredda tocca il volume **solo** attraverso il serpentino sanitario, e non
esiste alcun legame fra acquedotto e circuito di riscaldamento, benché il testo ne
descriva uno. Chi guarderà il grafo vedrà un impianto che non si può riempire.

Da notare che disegnarlo non sarebbe stato nemmeno immediato: la voce di confine
`cold-water-inlet` ha **un solo attacco**, già occupato dall'alimentazione del serpentino;
sarebbe servito un secondo confine o una ripartizione sull'acqua fredda, e le istruzioni
non dicono se un impianto può avere due voci di confine per la stessa alimentazione.

### 3. Primario e secondario: una rete o due? Il criterio dichiarato dice una cosa, gli esempi un'altra

Il §4.2 dà come criterio il fluido: «una rete è un circuito […] Il fluido cambia dove una
macchina lo cambia». Fra primario e secondario **il fluido non cambia**: è acqua di
riscaldamento di qua e di là del volume. Ma lo stesso paragrafo elenca fra gli esempi di
rete «il circuito dei generatori» **e** «il circuito secondario che parte da un
accumulo», cioè proprio i due che il criterio del fluido unirebbe.

Ho seguito gli esempi e ho fatto **due reti** (`primario` e `secondario`), perché il
volume separa idraulicamente e perché il testo li nomina distintamente. Ma il criterio
scritto, applicato alla lettera, ne avrebbe prodotta una sola: due letture ragionevoli,
nessun criterio che le arbitri.

### 4. `carries_on_board`: un campo del catalogo che le istruzioni non nominano mai

La voce `heat-pump-air-water` dichiara `"carries_on_board": ["circulation"]`. È il campo
su cui ho fondato l'assunzione `a3` (nessun circolatore disegnato sul primario). Ma le
istruzioni spiegano come si legge il catalogo — `functions`, `ports`, `stored_medium`,
`stub` — e **non nominano mai `carries_on_board`**. Non so se sia vincolante (la macchina
*ha* la pompa a bordo, quindi non se ne disegna una), o solo informativo (il progettista
può metterne una esterna lo stesso). Il §6 tipo A porta un esempio quasi identico, ma lì
parla genericamente di «quello che il catalogo dichiara per la voce scelta», senza dire
in che campo lo dichiari. Ho letto il campo come vincolante e l'ho dichiarato.

Stesso silenzio su altri due campi che ho trovato e non ho usato: `traits` e `fills_from`.
`fills_from` in particolare (sul bollitore ACS) sembra dire proprio quello che il §9
chiede di capire — «quale circuito riempie la riserva» — ma nessun paragrafo lo cita.

### 5. Scelte lasciate senza criterio, tutte innocue ma tutte arbitrarie

- **Quale ramo su quale attacco del raccordo.** Il raccordo a T ha due entrate, `a` e `c`;
  la ripartizione ha due uscite, `b` e `c`. Niente dice quale generatore va su quale.
  Ho messo `pdc-1` su `a`/`b` e `pdc-2` su `c`/`c` per simmetria di lettura. Se a valle
  qualcuno dà un significato geometrico a quelle lettere (destra/sinistra, dritto/derivato),
  la scelta smette di essere innocua.
- **Formato di `source_message_refs`.** Il §3 dice che serve «a citare la frase del testo»,
  ma non dice se ci va un identificatore di messaggio, un numero di riga o la frase
  stessa. Ho scritto una citazione leggibile («testo del committente, frase 3: …»).
- **`project_id` dal titolo.** Il testo si intitola «Esempio 1 – Due pompe di calore in
  parallelo con accumulo combinato». Le istruzioni dicono di costruire l'id «dal titolo
  dell'impianto», senza dire se le parole di servizio («Esempio 1») vadano tenute. Le ho
  tolte: `due-pompe-di-calore-accumulo-combinato`.
- **`name` delle reti.** Campo obbligatorio nello schema, nessun criterio nelle istruzioni
  su come chiamare una rete. Ho usato nomi descrittivi in italiano.
- **«Alimenta direttamente».** Ho letto «direttamente» come «senza pezzi interposti»
  (niente miscelatrice, niente collettore). È la lettura letterale, ma «direttamente»
  potrebbe anche voler dire solo «senza passare per altri accumuli».

### 6. `assumptions` mescola tre cose che l'ingegnere deve trattare in modo diverso

Nella stessa lista finiscono: domande vere che aspettano risposta (`a1`, `a3`, `a5`,
`a6`, `a10`), assunzioni di disegno già prese (`a2`, `a4`, `a7`), e note su cose dette dal
testo che il grafo non mostra (`a8`, `a9`). Lo schema offre solo `text` e `status`, e le
istruzioni chiedono di usare `status: "proposed"` per tutte. Chi legge non ha modo di
distinguere «devi rispondere» da «ti sto solo avvisando» se non leggendo la prosa. Ho
compensato scrivendo il tipo dentro il testo e separando le tre famiglie qui nel §2, ma
il modello non lo prevede.

### 7. Tensioni che le istruzioni risolvono da sé (le segnalo per completezza, non sono buchi)

- Il §1 dice «non completi», il §4.3 dice che un circuito chiuso si chiude e che
  disegnare il ritorno è trascrizione. Sembra una contraddizione, ma il §4.3 la scioglie
  esplicitamente. Ho disegnato i ritorni (`p4`–`p6`, `p9`).
- Il §2 indica il catalogo in `examples/layout/catalog/` e lo schema in `schemas/`, cioè
  dentro il repository che il vincolo di isolamento mi vieta di aprire; lo stesso §2 dice
  però che «se i file ti arrivano copiati in un'altra cartella, valgono lo stesso».
  Ho usato solo le copie nella mia cartella (`catalogo/`, `schemi/`, `naming/`).
- `tee-junction` e `tee-split` hanno lo stesso mestiere (`junction`) e lo stesso
  `symbol_id`: si distinguono solo dal verso delle porte. Il §4.4 lo dice abbastanza
  chiaramente da non lasciare dubbi.

---

## 4. Isolamento

Vincolo rispettato. Non ho aperto, letto, elencato né cercato alcun file fuori dalla
cartella di lavoro: né in `/home/user/DisegnatoreMEP`, né altrove. Nessun `grep`, `find`,
`ls`, `cat` o `glob` fuori dalla cartella. **Nessuna infrazione da dichiarare.**

Le uniche due esecuzioni fuori cartella sono quelle previste:

- il comando di validazione del §8 passo 7, lanciato dalla radice del repository sul mio
  file — è l'eccezione esplicitamente consentita, e non stampa nulla (il file carica);
- uno script di controllo che ho scritto io, `controllo.py`, dentro la mia cartella di
  lavoro: legge soltanto il mio grafo e il catalogo che ho ricevuto, e verifica attacchi
  esistenti, attacchi doppi, attacchi `stub`, verso del flusso, coerenza dei fluidi,
  attacchi obbligatori liberi e mestieri di ferramenta. Esito: nessun errore.
