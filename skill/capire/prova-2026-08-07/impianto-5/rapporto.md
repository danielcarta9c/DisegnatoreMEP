# Rapporto — Esempio 5, tre pompe di calore con più circuiti secondari

Committente: Nove C · Commessa: PROVA · Revisione 00 · 7 agosto 2026

---

## 1. Cosa ho capito dell'impianto

Una centrale a pompe di calore con separazione idraulica e produzione sanitaria
centralizzata, articolata su quattro circuiti.

**Il circuito dei generatori.** Tre pompe di calore aria-acqua reversibili, 35 kW
ciascuna, in parallelo. Le tre mandate confluiscono in un'unica linea; sulla linea c'è
una valvola deviatrice a tre vie che manda il flusso o al volano o al serpentino del
bollitore. I due ritorni — quello del volano e quello del serpentino — si riuniscono e
si ripartiscono sui tre ritorni macchina. La circolazione del primario è a bordo delle
macchine (il catalogo la dichiara), e nessun circolatore primario è disegnato.

**Il volano.** Un volume tecnico da 500 litri «a quattro tubi» che fa due mestieri
insieme: accumulo inerziale e separazione idraulica. È il confine dichiarato dal testo
fra il circuito dei generatori e i circuiti dell'edificio, e nel grafo è il confine fra
la rete `primario` e la rete `secondario`.

**I tre circuiti secondari.** Batterie delle UTA, fan-coil, pavimento radiante. Nascono
tutti dal volano, quindi sono **tre rami di una rete sola**, non tre reti: una rete
parte dalla macchina che la alimenta, e la macchina qui è una sola. Ogni ramo ha il
proprio circolatore sulla mandata; il ramo del pavimento ha in più una valvola
miscelatrice di circuito, che è topologia (decide cosa entra nel circuito) e quindi
entra nel grafo.

**Il sanitario.** Un bollitore da 500 litri con serpentino: il serpentino sta sul
circuito dei generatori, l'acqua del bollitore viene dall'acquedotto ed esce alle
utenze. Sono due circuiti diversi che si toccano dentro la stessa macchina, e nel grafo
sono due reti distinte perché il fluido cambia — acqua fredda in basso, acqua calda
sanitaria in alto. Il ricircolo ACS è un anello sulla distribuzione calda, con il
proprio circolatore.

**Il regime:** 3 × 35 kW = 105 kW, quindi `over_35_kw`. Ricavato dalle potenze scritte
dall'ingegnere, non chiesto.

**Cosa il grafo non mostra, per scelta delle istruzioni:** la gestione in cascata e la
priorità sanitaria (sono regolazione), e la valvola miscelatrice termostatica
sull'uscita dell'ACS (è ferramenta sanitaria, la aggiunge il pezzo successivo della
catena). Tutte e tre sono registrate in `assumptions` perché non vadano perse.

Il file contiene 28 componenti, 36 tubazioni, 4 reti, 14 voci in `assumptions`.
`subsystems`, `rule_applications` e `sheets` sono liste vuote. Nessun `tag` è
compilato: l'ingegnere non ne ha scritto nessuno.

---

## 2. Scelte di catalogo che vale la pena spiegare

- **`buffer-four-port` e non `buffer-combined`.** Le due voci dichiarano gli stessi due
  mestieri (`hydraulic_separation` + `thermal_storage`), ma `buffer-combined` ha anche
  `cold_in` e `dhw_out`, cioè produce il sanitario da sé. Qui il sanitario lo fa un
  bollitore separato, che il testo descrive: comanda la descrizione, non il nome. E i
  quattro attacchi di `buffer-four-port` sono esattamente quelli che servono per
  scrivere i collegamenti descritti.
- **`dhw-cylinder` e non `dhw-heat-pump`.** Il bollitore è «alimentato dalle pompe di
  calore» attraverso un serpentino: non genera calore da sé. `dhw-heat-pump` dichiara
  anche `heat_generation` e non ha gli attacchi del serpentino — con quella voce i
  collegamenti descritti non si potrebbero scrivere. (Ed è anche la ragione per cui il
  regime resta 105 kW e non di più: il bollitore non è un generatore.)
- **`mixing-valve-3way` (`circuit_mixing`) entra; `mixing-valve-thermostatic`
  (`dhw_mixing`) no.** Le due valvole si somigliano nel nome e stanno su liste opposte
  del §5. La prima decide cosa entra in un circuito, la seconda protegge un'utenza.
- **`ahu-coil` per le batterie delle UTA.** Mestiere `emission`, come tutti i terminali.
  Il catalogo non ha né UTA né ventilatori: nel grafo entra la batteria, che è la parte
  idronica, e questa è l'unica parte che il testo mette su un circuito d'acqua.
- **Nessun buco di catalogo (nessuna voce di tipo B).** Tutto ciò che il testo nomina e
  che appartiene al corpo dell'impianto ha trovato una voce con i mestieri e gli
  attacchi giusti.

---

## 3. Domande e assunzioni, in chiaro

Le quattordici voci di `assumptions`, in italiano piano.

1. **Reversibilità e raffrescamento (a1).** Le pompe di calore sono reversibili:
   d'estate mandano acqua refrigerata negli stessi tubi. La tabella dei fluidi non ha un
   fluido per il raffrescamento, quindi tutti i circuiti termici sono dichiarati «acqua
   di riscaldamento»; il circuito dei generatori e i rami delle batterie UTA e dei
   fan-coil portano **anche** il raffrescamento. Il ramo del pavimento no: il testo dice
   «solo in riscaldamento».
2. **Cascata e priorità sanitaria (a2).** Sono logiche di regolazione, non topologia: sul
   grafo si vedono le tre macchine in parallelo e la valvola deviatrice, non la cascata
   e non la priorità.
3. **Con che pezzo si fa il parallelo (a3).** «In parallelo» dice che i flussi si
   uniscono, ma non con che pezzo: due raccordi a T in catena sulla mandata e due
   ripartizioni a T sul ritorno. Se in centrale è previsto un collettore, va messo al
   loro posto.
4. **Con che pezzo si staccano i tre circuiti (a4).** «Dal volume tecnico partono tre
   circuiti» non dice come: due ripartizioni a T in catena sulla mandata e due raccordi
   a T sul ritorno. È così, o dal volano parte un collettore di distribuzione?
5. **Dove confluiscono i due ritorni del primario (a5).** Il ritorno del volano e quello
   del serpentino rientrano sulle stesse macchine, e un attacco porta una tubazione
   sola: sono stati uniti con un raccordo a T prima della ripartizione. Il testo non
   dice dove.
6. **A quali circuiti si riferisce «ogni circuito» (a6).** L'ho letto come i tre
   circuiti secondari appena elencati. Per il circuito dei generatori il testo non
   nomina circolatori: ho seguito la macchina di catalogo, che porta la circolazione a
   bordo. **È così, o il primario ha circolatori esterni da rappresentare?**
7. **Dove stanno i tre circolatori (a7).** Il testo non dice su quale ramo: sono stati
   messi sulla mandata del circuito che servono, posizione convenzionale di disegno. Su
   quello del pavimento, a valle della miscelatrice.
8. **Da dove è alimentato il secondo ingresso della miscelatrice (a8).** «Circuito
   miscelato» impone la miscelazione, e la valvola di catalogo ha un secondo ingresso
   che deve essere alimentato perché ci sia. Ho assunto la soluzione convenzionale: una
   ripartizione sul ritorno del pavimento che rimanda parte dell'acqua all'ingresso
   freddo. **Il testo questo by-pass non lo descrive: confermate il punto di prelievo?**
9. **Quanti sono i terminali (a9).** «Le batterie calde e fredde delle UTA», «i
   fan-coil», «il pavimento radiante» sono insiemi senza numero: un solo terminale
   rappresenta ciascun ramo. Quante UTA, quante batterie, quanti fan-coil? E in
   particolare: **«batterie calde e fredde» sono due batterie distinte sullo stesso
   circuito, o una sola alimentata ora calda ora fredda?**
10. **La miscelatrice termostatica non è nel grafo (a10).** È ferramenta sanitaria: la
    aggiunge il pezzo che completa. La nomina è registrata perché non vada persa.
11. **Come si chiude l'anello del ricircolo ACS (a11).** Il bollitore di catalogo non ha
    l'attacco del ricircolo, e un attacco non si inventa: l'anello si chiude sul tubo,
    con una ripartizione a valle da cui si stacca e un raccordo, subito all'uscita del
    bollitore, dove rientra; il circolatore sta sul ramo di rientro. Il punto di stacco
    e quello di rientro non sono detti dal testo. Nota: le utenze sanitarie sono una
    voce di confine con un attacco solo, quindi il ricircolo **non** può essere
    rappresentato come stacco a valle dell'ultimo prelievo.
12. **I confini del sanitario (a12).** Il testo non nomina né l'acquedotto né le utenze,
    ma il circuito sanitario è aperto e va chiuso da qualche parte: ho usato le due voci
    di confine del catalogo. «Parte bassa» e «parte alta» del bollitore sono
    rappresentate dagli attacchi che il catalogo dichiara, non da una quota.
13. **Come è stato ricavato il regime (a13).** 3 × 35 kW = 105 kW, sopra la soglia:
    `over_35_kw`. Il testo non dice se i 35 kW sono resi o assorbiti, né se sono la
    potenza in riscaldamento o in raffrescamento: ho sommato la potenza come è scritta.
14. **Come ho letto «a quattro tubi» (a14).** Come un volano con quattro attacchi
    (primario mandata/ritorno, secondario mandata/ritorno), coerente con l'uso che il
    testo gli dà. **Non** come una distribuzione a quattro tubi con circuiti caldo e
    freddo separati, che con tre macchine reversibili identiche su un solo volano non
    sarebbe rappresentabile. **Confermate la lettura?**

Le domande vere e proprie — quelle che cambiano il disegno e su cui due letture
ragionevoli danno due grafi diversi — sono la 6, la 8, la 9 (seconda parte) e la 14.

---

## 4. Dove le istruzioni non mi hanno dato un criterio

Questa è la parte che la prova chiede espressamente. Ogni punto è un luogo dove le
istruzioni tacciono, si contraddicono, o lasciano scegliere senza dire come.

### 4.1 Contraddizione: attacco `required` libero — si chiude o si chiede?

Il caso è l'ingresso freddo della valvola miscelatrice di circuito (`cold_in`,
`required: true`). Tre passi delle istruzioni tirano in tre direzioni:

- **§4.3, ultimo capoverso:** «Dopo aver collegato, controlla gli attacchi
  `required: true` […] uno rimasto libero vuol dire che hai perso un collegamento
  descritto — **o che il testo davvero non lo dà, e allora è una domanda (§6)**.» → lascia
  l'attacco libero e chiedi.
- **§6, tipo A:** «il testo impone un collegamento ma non dice con che pezzo. Il grafo
  deve chiudersi […] chiudi così e dichiara» e «un grafo incompleto è meno utile di un
  grafo con una domanda sopra». → chiudi.
- **§6, «mai inventare»:** «collegamenti che il testo non descrive». → non chiudere.

Non c'è un criterio per dire quale prevale. Ho chiuso con il by-pass convenzionale
(assunzione 8), perché «miscelato» è una parola del testo e una miscelatrice con un solo
ingresso alimentato non miscela niente — ma è una tubazione che il testo non descrive, e
l'ho dichiarata come tale. Con la lettura opposta, `cold_in` resterebbe libero e il
componente `rip-bypass-radiante` e le tubazioni `s13`/`s14` non esisterebbero.

### 4.2 Silenzio: l'ordine fra miscelatrice e circolatore

§7 dice dove va il circolatore (sulla mandata) ma non dice se la valvola miscelatrice di
circuito sta a monte o a valle di esso: entrambe le posizioni sono «sulla mandata». Ho
scelto miscelatrice → circolatore → pavimento. Cambia il grafo, e nessuna riga lo
decide.

### 4.3 Silenzio: fin dove arriva «ogni circuito»

Le istruzioni non danno alcuna regola per risolvere la portata di un «ogni» nel testo
dell'ingegnere. «Ogni circuito è dotato del proprio circolatore» segue l'elenco dei tre
secondari, e così l'ho letto; ma letto largo comprenderebbe anche il circuito dei
generatori, e il grafo guadagnerebbe uno o tre circolatori primari. Due grafi diversi,
nessuna delle due letture manifestamente sbagliata.

### 4.4 Silenzio: il campo `carries_on_board` non è mai nominato

La voce `heat-pump-air-water` dichiara `carries_on_board: ["circulation"]`. Le istruzioni
non nominano mai questo campo: §7 parla di un componente «descritto come integrato»
**dal testo**, non dal catalogo. L'unico appiglio è l'esempio di §6 tipo A («si è seguita
la macchina di catalogo, che lo porta a bordo»), che però riguarda un caso in cui il
testo un circolatore lo nomina. Ho seguito il catalogo e dichiarato.

### 4.5 Silenzio: un terminale rappresentativo, o due?

§7 copre il plurale della stessa famiglia («i fan-coil» → un fan-coil rappresentativo).
Non dice cosa fare di una locuzione che nomina **due funzioni diverse** su un circuito
solo: «le batterie calde e fredde». Un terminale o due? Ho messo uno e dichiarato.

### 4.6 Silenzio: come si disambigua «a quattro tubi»

In termotecnica italiana la locuzione ha due significati correnti — un accumulo con
quattro attacchi, e una distribuzione a quattro tubi con caldo e freddo separati. Le
istruzioni insegnano a scegliere la **voce di catalogo** sui mestieri e sugli attacchi,
ma non danno un criterio per disambiguare la **frase dell'ingegnere** prima ancora di
arrivare al catalogo. Ho scelto la prima lettura per coerenza con il resto del testo (un
volano solo, tre macchine reversibili identiche) e l'ho dichiarata.

### 4.7 Silenzio: dove si stacca e dove rientra l'anello del ricircolo

§4.4 prescrive **come** chiudere un anello che non ha l'attacco sulla macchina (una
ripartizione dove esce, una confluenza dove rientra) e dice di dichiarare il punto
scelto, ma non dà nessuna preferenza su **quale** punto. In più il caso concreto è
irrappresentabile come sarebbe nella realtà: la voce di confine `dhw-draw-off` ha un
attacco solo, quindi non si può mettere lo stacco del ricircolo a valle dell'ultimo
prelievo. Le istruzioni non contemplano questo vincolo.

### 4.8 Silenzio: su quale ramo va il circolatore di un anello di ricircolo

La convenzione di §7 («sulla mandata del circuito che serve») è scritta per un circuito
che alimenta terminali. In un anello di ricircolo «mandata» non individua un ramo. L'ho
messo sul ramo di rientro, che è la posizione d'uso, senza una riga che lo dica.

### 4.9 Silenzio: quale uscita della deviatrice va dove

`diverting-valve-3way` ha `out_a` e `out_b`, indistinguibili a catalogo. Ho mandato
`out_a` al volano e `out_b` al serpentino. È una scelta silenziosa e senza conseguenze
idrauliche, ma è una scelta: se a valle qualcuno attribuisce un significato all'ordine
delle uscite, non c'è niente che me lo dica.

### 4.10 Silenzio: a quale rete appartiene la tubazione che tocca la macchina di confine

§4.2 dice che una rete **parte** da una macchina, ma non dice a quale rete appartengano
le tubazioni che **arrivano** a quella macchina dall'altro lato. Sul volano ho assegnato
`p06` e `p08` al `primario` e `s01`/`s16` al `secondario`, cioè ogni tubazione alla rete
del circuito a cui appartiene idraulicamente. È l'unica lettura sensata, ma non è
scritta.

Nello stesso paragrafo: una rete «parte da una macchina che la alimenta […] mai da un
raccordo». Il ramo del serpentino nasce da una **valvola deviatrice**, che non è né una
macchina che alimenta né un raccordo. L'ho tenuto dentro la rete `primario` (stesso
fluido, stessa sorgente), coerente con la regola dei rami, ma il caso non è previsto.

### 4.11 Silenzio: `metadata.project_name`

§3 spiega come si costruisce `project_id` e da dove vengono committente, commessa,
revisione e data. `project_name` è obbligatorio nello schema e non è spiegato da
nessuna parte. Ho usato il titolo del testo dell'ingegnere.

### 4.12 Lacuna: potenze di macchine reversibili

§4.6 dice di sommare «le potenze delle macchine che generano calore» e prevede il caso
«potenza resa / potenza assorbita». Non prevede il caso di una macchina reversibile, che
d'estate calore non ne genera affatto, e per cui un numero solo può essere la resa
termica o la resa frigorifera. Ho sommato come scritto e dichiarato l'incertezza —
senza però **chiedere**, perché §6 vieta di chiedere ciò che il testo ha già scritto.

### 4.13 Attrito minore: una parola di regolazione può stare in `properties`?

§3 dice di trascrivere «le qualifiche che il testo usa» perché «sono parole
dell'ingegnere»; §4.5 dice che la logica di regolazione non è topologia e va in
`assumptions`. «Gestite in cascata» è entrambe le cose. Ho fatto tutt'e due: proprietà
`gestione: "in cascata"` sulle tre macchine **e** voce in `assumptions`. Non è una
contraddizione secca, ma nessuna riga dice se una parola di regolazione debba comparire
anche fra le proprietà.

---

## 5. Controllo finale (§9)

| Domanda | Esito |
|---|---|
| Il JSON carica con lo strumento di validazione? | Sì, nessun output |
| Ogni `definition_id` esiste nel catalogo? | Sì, 28/28 |
| Nessun mestiere della lista «ferramenta»? | Nessuno |
| Ogni attacco usato esiste a catalogo? | Sì |
| Nessun attacco porta due tubazioni? | Verificato: 0 casi |
| Nessuna tubazione tocca uno `stub`? | Verificato: 0 casi (i tre stub del volano e la sede sonda del bollitore restano liberi) |
| Ogni tubazione va da `out` a `in`, sullo stesso fluido della rete? | Sì, 36/36 |
| Nessun attacco `required` è rimasto libero? | Nessuno |
| I `tag` sono solo quelli scritti dall'ingegnere? | L'ingegnere non ne ha scritti: tutti `null` |
| Ogni componente e ogni tubazione è nella tabella di rilettura? | Sì, 28/28 e 36/36 |
| `subsystems`, `rule_applications`, `sheets` vuote? | Sì |

Le quattro cose da cui dipende il resto della catena: **che macchina è ciascun pezzo**
(§2 di questo rapporto), **che acqua porta ogni circuito** (quattro reti, il sanitario
c'è ed è centralizzato), **il regime** (`over_35_kw`, ricavato), **come i circuiti
toccano i serbatoi** (il serpentino attraversa il bollitore scambiando calore; l'acqua
del bollitore è quella che entra dall'acquedotto; il volano è attraversato dal primario
su due attacchi e dal secondario sugli altri due).

---

## 6. Isolamento

Non ho aperto, letto, cercato né elencato alcun file fuori dalla mia cartella di lavoro.
L'unica cosa eseguita fuori è il comando di validazione del §8, passo 7, lanciato dalla
radice del repository come le istruzioni prescrivono ed espressamente permesso dal
vincolo. Nessuna infrazione da dichiarare.
