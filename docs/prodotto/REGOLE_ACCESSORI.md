# Le regole degli accessori

> **Cosa approvi qui.** Diciassette regole, una per accessorio. Ognuna dice **perché**
> quell'accessorio esiste, **dove** va e perché proprio lì, **quante volte** compare, e
> **come facciamo a sapere** che in un impianto c'è già.
>
> **Come si legge.** Una per volta, e ognuna si può bocciare da sola: sono diciassette
> schede indipendenti, non un blocco unico. Se una non ti torna, dillo per quella — le
> altre restano in piedi.
>
> **Cosa non c'è, e apposta.** Nessun numero di taratura, nessun volume, nessun diametro.
> Le regole dicono *cosa ci va e dove*, mai *quanto grande*: quello resta del progettista.

---

## Il regime della centrale: sotto i 35 kW le regole cambiano

È la novità più grossa di questo giro, e viene dalla tua correzione: stavamo applicando
regole da grande centrale alle piccole. Adesso le regole conoscono **due regimi**.

**Sotto i 35 kW** la centrale è quella di casa: niente separatore d'aria — basta lo sfogo
sul serbatoio; niente termometro aggiunto — si usa quello della macchina; niente sicurezza
per ogni generatore — **una sola, di circuito, sulla mandata vicino al gruppo delle
macchine** (tua correzione dell'8 settembre 2026, I-046: prima stava sul serbatoio, e la
prima consegna l'aveva moltiplicata invece di spostarla). È la prassi che ci hai dato, e
l'abbiamo riscontrata riga per riga sugli schemi Caleffi delle centrali domestiche. Il
numero delle sicurezze non si deduce mai dal numero delle macchine: si protegge ogni
**dominio** — ciò che resta in comunicazione con la sicurezza mentre è in esercizio — e
una macchina che un organo altrui può separare da quella comune si guarda a parte, con il
dato del suo catalogo (scheda 3).

**Sopra i 35 kW** vale la Raccolta R, che da lì in su si applica: sicurezza e termometro
per ogni generatore, separatore d'aria vero.

**Chi decide il regime: tu, sempre.** È un dato del progetto, di chi lo firma. Noi lo
**leggiamo dalle potenze che hai scritto tu** e te lo riportiamo dove lo vedi: sommare
numeri che hai già dato e confrontarli con una soglia fissa è aritmetica, non
dimensionamento — la taglia non la decide la skill. Le regole, dal canto loro, quel dato
lo leggono e basta: non lo ricavano mai dalle proprietà dei pezzi. E se in un testo le
potenze non ci fossero, il regime resterebbe non dichiarato, l'impianto prenderebbe il
**corredo minimo** — le regole della piccola centrale — e la mancanza te la diremmo.

## Il ritorno generale: il corredo del circuito sta sul tratto comune

L'altra correzione che ci hai dato: vaso, riempimento, manometro e defangatore finivano
sul ramo della prima macchina, e con due macchine in parallelo era il ramo sbagliato.
Adesso le regole sanno trovare **il ritorno generale**: il tratto in cui passa tutta
l'acqua che torna, prima che si divida verso le macchine. Il corredo del circuito sta lì,
una volta sola — niente doppioni quando le macchine sono due o tre in parallelo.

E quando quel tratto **non esiste** — succede: un impianto dove il ritorno della caldaia
raccoglie anche lo scambiatore per conto suo — le regole non scelgono un ramo a caso: te
lo scrivono come punto aperto, e la posizione la decidi tu.

---

# Le sicurezze

Sono quelle che non si tolgono. Se se ne boccia una, l'impianto che disegniamo può
scoppiare.

## 1 · Valvola di sicurezza

**Cos'è.** Una valvola che si apre da sola quando la pressione supera il limite, e scarica.

**Perché esiste.** Dove il calore entra nell'acqua la pressione può salire più in fretta di
quanto il circuito riesca ad assorbire. Serve una via che si apra da sé, senza che nessuno
la comandi e senza che nessuno possa impedirlo.

**Quando vale.** Sopra i 35 kW: è la Raccolta R, che prescrive i dispositivi per ogni
generatore. Sotto i 35 kW non è una per generatore: è una per circuito (scheda 2), e la
macchina che può restare isolata da quella comune si guarda a parte (scheda 3).

**Dove va, e perché proprio lì.** Sulla tubazione che esce da ogni macchina che scalda, e
**attaccata alla macchina**, il più vicino possibile. Fra lei e ciò che protegge non ci va
niente che si possa chiudere: una valvola chiusa davanti a una sicurezza è una sicurezza
che non c'è.

**Quante volte.** Una per ogni macchina che scalda, sopra i 35 kW.

**Come sappiamo che c'è già.** Se su quella stessa tubazione c'è già un organo che scarica
la sovrapressione, o se la macchina dichiara di portarlo dentro il mantello, non ne
aggiungiamo un secondo.

**Da dove viene.** Dalla Raccolta R, che elenca i dispositivi obbligatori di un impianto a
vaso chiuso. È una prescrizione, non una buona abitudine. Il «più vicino possibile» è
della scheda tecnica Caleffi delle valvole di sicurezza: sulla sommità del generatore o
sulla mandata, con tubazione non intercettabile.

## 2 · Valvola di sicurezza del circuito

**Cos'è.** La stessa valvola della scheda 1, ma nella centrale di casa: una sola, per
tutto il circuito dell'acqua tecnica.

**Perché esiste.** Anche il circuito piccolo è chiuso e si scalda: la via che si apre da
sola serve comunque. E ne basta una finché tutte le macchine **restano in comunicazione
con lei** mentre sono in esercizio: la pressione è la stessa dappertutto, e una
sicurezza comune protegge tutto ciò che le sta attorno senza organi chiusi in mezzo.

**Quando vale.** Sotto i 35 kW, ed è la tua prassi corretta l'8 settembre 2026 (I-046):
**una sola, di circuito**, e non una per generatore. Prima stava sul serbatoio; tu hai
chiesto di spostarla, non di moltiplicarla.

**Dove va, e perché proprio lì.** Sulla mandata generale, nel punto in cui le mandate delle
macchine sono già diventate una — **attaccata a ciò che le unisce**, o alla macchina
stessa se è una sola — e prima di qualunque organo di chiusura di quel tratto. Più vicino
alle macchine di così non si può stare restando comune a tutte: da lì ogni macchina in
esercizio la raggiunge attraversando solo i propri organi, che tiene aperti. Il serbatoio
è protetto dalla stessa via finché comunica con le macchine; isolato da loro non si
scalda. Niente più sicurezza sul serbatoio.

**Quante volte.** Una per circuito. Non conta quante macchine ci sono.

**Come sappiamo che c'è già.** Se su quel circuito c'è già qualcosa che scarica la
sovrapressione, oppure se **ogni** macchina dichiara di portarla dentro il mantello: se
la dichiara una sola, il circuito la vuole lo stesso.

**Da dove viene.** Dalla scheda tecnica Caleffi delle valvole di sicurezza — sulla mandata,
il più vicino possibile, con tubazione non intercettabile — e dalla tua prassi corretta:
una sola, spostata dal serbatoio alla mandata vicino al gruppo delle macchine.

## 3 · Valvola di sicurezza della macchina isolabile

**Cos'è.** La stessa valvola, posata su una macchina sola: quella che un organo **non suo**
può separare dalla sicurezza del circuito.

**Perché esiste.** Se fra una macchina e la sicurezza comune c'è un organo che non è il
suo — una valvola di zona, un organo di rete scritto dal progettista — quando quell'organo
è chiuso e la macchina scalda, il suo volume è chiuso e non ha via d'uscita. È un altro
dominio, e vuole la sua protezione.

**Quando vale.** In tutti e due i regimi, ma solo per chi resta davvero separabile: si
legge dalla connettività e dagli organi di chiusura, macchina per macchina, dopo che il
circuito ha già ricevuto la sua sicurezza. Nella tavola 1 non vale per nessuna delle due
pompe di calore: fra loro e la sicurezza del circuito ci sono solo le loro valvole.

**Dove va, e perché proprio lì.** Sulla tubazione che esce dalla macchina, attaccata a lei
e prima del suo organo: come nella scheda 1.

**Quante volte.** Solo con un dato. Il catalogo della macchina dice se la sicurezza sta
dentro il mantello, e il dato ha **tre stati**: presente, assente, ignoto. Presente:
niente. Assente: la macchina la riceve. Ignoto — il campo manca, ed è il caso della pompa
di calore generica — non vuol dire assente: **non si aggiunge nulla, e ti facciamo una
domanda**. Un dispositivo in più su una presunzione è un errore quanto uno in meno.

**Come sappiamo che c'è già.** Se sulla tubazione di quell'attacco c'è già un organo che
scarica la sovrapressione, o se la macchina lo dichiara a bordo.

**Da dove viene.** Dalla scheda tecnica Caleffi delle valvole di sicurezza e da Idraulica
61, che dice che sfogo e sicurezza **possono** essere integrati nella macchina: quindi lo
dice il catalogo, macchina per macchina, e quando non lo dice si chiede.

## 4 · Gruppo di sicurezza sanitario

**Cos'è.** Il gruppo che sta sull'ingresso dell'acqua fredda di un bollitore e che scarica
se la pressione sale.

**Perché esiste.** Una riserva d'acqua che si scalda si dilata, e il ritegno le ha appena
tolto la via di ritorno verso la rete. Senza uno scarico che si apra da solo, la pressione
sale finché il serbatoio cede.

**Dove va, e perché proprio lì.** Sull'alimentazione fredda, e dal lato del serbatoio
rispetto a qualunque rubinetto. Stessa ragione della sicurezza di prima: una via di scarico
dietro un rubinetto chiuso non è una via di scarico.

**Quante volte.** Una per circuito di acqua fredda sanitaria.

**Come sappiamo che c'è già.** Se su quel circuito esiste già qualcosa che scarica la
sovrapressione.

**Da dove viene.** Dalla pratica corrente documentata negli schemi Caleffi: è il gruppo di
sicurezza sanitario che si monta su ogni bollitore.

## 5 · Vaso di espansione

**Cos'è.** Un recipiente con una membrana, che assorbe l'aumento di volume dell'acqua
quando si scalda.

**Perché esiste.** L'acqua scaldata occupa più spazio, e in un volume chiuso quello spazio
in più diventa pressione. Il vaso è il posto dove quel volume va, invece che contro le
pareti.

**Dove va, e perché proprio lì.** Sul **ritorno generale** del circuito, prima che il
ritorno si divida verso le macchine: è il punto più freddo — la membrana dura di più dove
l'acqua è meno calda — ed è il tratto che serve tutti i generatori insieme. Con due
macchine in parallelo il vaso non finisce più sul ramo di una sola: è la correzione che ci
hai chiesto.

**Quante volte.** Uno per circuito, perché la pressione è la stessa in tutto il circuito e
un secondo vaso non aggiungerebbe niente. Se la macchina ne porta già uno dentro il
mantello e tu lo dichiari sufficiente, non ne aggiungiamo un altro.

**Come sappiamo che c'è già.** Se su quel circuito c'è già qualcosa che assorbe la
dilatazione — anche a bordo macchina, se il suo catalogo lo dichiara.

**Da dove viene.** Dalla Raccolta R per il punto freddo; dagli schemi applicativi Caleffi,
che mettono il vaso dell'impianto sul ritorno generale in tutti e cinque gli schemi.

## 6 · Vaso di espansione sanitario

**Cos'è.** Lo stesso recipiente, per la riserva sanitaria.

**Perché esiste.** Anche l'acqua del bollitore si scalda e si dilata, e il ritegno le ha
tolto la via di ritorno: senza un vaso suo, la dilatazione apre la sicurezza a ogni ciclo.

**Dove va, e perché proprio lì.** Sull'alimentazione fredda della riserva, dal lato del
serbatoio: è dove il costruttore prescrive di prevederlo, insieme alla sicurezza.

**Quante volte.** Uno per circuito di acqua fredda sanitaria.

**Come sappiamo che c'è già.** Se su quel circuito c'è già qualcosa che assorbe la
dilatazione.

**Da dove viene.** Dalle istruzioni d'installazione dei costruttori di bollitori, e dagli
schemi Caleffi che lo disegnano sull'ingresso freddo.

## 7 · Valvola di ritegno sanitaria

**Cos'è.** Una valvola che lascia passare l'acqua in un verso solo.

**Perché esiste.** Un volume d'acqua che si scalda spinge indietro verso la rete che lo
alimenta, e l'acqua già scaldata non deve tornare nella rete dell'acqua potabile fredda.

**Dove va, e perché proprio lì.** Sull'alimentazione, che è l'unica via da cui quel ritorno
potrebbe avvenire. Non serve metterla altrove: altrove non c'è niente da fermare.

**Quante volte.** Una per circuito di acqua fredda sanitaria: la via è una.

**Come sappiamo che c'è già.** Se su quel circuito c'è già qualcosa che impedisce il
ritorno.

**Da dove viene.** Dalla pratica corrente documentata negli schemi Caleffi.

---

# Le intercettazioni

## 8 · Valvola di intercettazione — **la regola che era sei**

**Cos'è.** Il rubinetto che ferma l'acqua per poter togliere un pezzo.

**Perché esiste.** Un pezzo che si smonta a impianto acceso si toglie solo se prima si
ferma l'acqua che lo raggiunge. E l'acqua lo raggiunge da **ogni** tubo che lo tocca:
quindi ogni tubo che lo tocca vuole il proprio rubinetto. Con uno solo si finisce per
svuotare il circuito per cambiare un pezzo, che è esattamente ciò che non si vuole.

**Dove va, e perché proprio lì.** Su ogni tubo che esce dal **gruppo** che si manutiene
insieme, dal lato dell'impianto (aggiornato il 7 settembre 2026, DRAW-005, su tua
indicazione — I-034). La macchina e il filtro che le sta sul ritorno sono un gruppo: sul
ritorno il rubinetto sta oltre il filtro, lato rete, e sulla mandata sta sulla macchina;
fra il filtro e la macchina non ne va un secondo, perché chiuderebbe lo stesso volume. Un
tratto di tubo prende un rubinetto solo, anche quando due pezzi vi si affacciano dai due
capi. Un pezzo con quattro tubi ne riceve quattro: non è una scelta, è il conto dei tubi
che escono dal gruppo.

**A chi si applica.** A tutto ciò che dichiara di smontarsi a impianto acceso — **macchine
e accessori insieme**. Il filtro, il defangatore, il circolatore la ricevono come la pompa
di calore. Prima no: prima esistevano sei regole separate che dicevano tutte la stessa cosa.

**Il caso speciale, e non è un'eccezione.** Alcuni pezzi non devono mai restare esclusi per
distrazione — il vaso di espansione è il caso — e quelli si chiudono soltanto con una
valvola **bloccabile aperta**, che si può staccare per la verifica ma non si chiude per
sbaglio. Non è una regola in più: è lo stesso ragionamento, e quale rubinetto ci voglia lo
dichiara il pezzo, non la regola.

**Chi non la riceve, e perché.** Un rubinetto e una valvola di ritegno non la ricevono: si
sostituiscono a tratta già chiusa, e se la chiedessero, quei due rubinetti ne vorrebbero
altri quattro, senza fine. Un dispositivo di sicurezza non la riceve mai, per la ragione
della scheda 1.

**Come sappiamo che c'è già.** Se sul tratto di tubo che parte da quell'attacco c'è già un
rubinetto, quell'attacco è a posto e non ne aggiungiamo un secondo; e se il tratto finisce
su un membro dello stesso gruppo, fra i due non ne va nessuno. È il motivo per cui i
rubinetti che il progettista ha già messo a mano vengono riconosciuti e rispettati.

**Da dove viene.** Dagli schemi Caleffi per impianti a pompa di calore, dalla nota di
Idraulica 61 sul filtro immediatamente a monte dello scambiatore della macchina, e dalla
tua indicazione del 5 settembre 2026: si isola il gruppo, non ogni attacco (I-034).

## 9 · Valvola di intercettazione generale

**Cos'è.** Il rubinetto sul punto in cui il nostro impianto si attacca a qualcosa che non è
nostro: la rete idrica, la distribuzione dell'edificio.

**Perché esiste.** Per poter lavorare sull'impianto senza dipendere da un rubinetto che sta
altrove e che governa qualcun altro. È una ragione diversa da quella della scheda 7: lì si
chiude *un pezzo*, qui si chiude *il confine*.

**Dove va, e perché proprio lì.** Sul confine stesso, così che tutto ciò che viene dopo
resti lavorabile.

**Quante volte.** Una per ogni punto di confine.

**Come sappiamo che c'è già.** Se su quella tubazione c'è già un rubinetto.

**Da dove viene.** Dalla pratica corrente documentata negli schemi Caleffi.

---

# La protezione dell'acqua

Sono due accessori diversi che sembrano lo stesso, e vale la pena guardare la differenza.

## 10 · Filtro a Y

**Cos'è.** Un filtro a rete, che si smonta e si pulisce.

**Perché esiste.** Trucioli, sabbia e residui di montaggio restano in circolo per tutta la
vita dell'impianto e intasano gli scambiatori stretti delle macchine.

**Dove va, e perché proprio lì.** Sulla tubazione che **entra** in ogni generatore, sul suo
ritorno: è l'ultimo punto utile prima dello scambiatore. A valle non protegge più niente.

**Quante volte.** Uno per generatore, e **solo per i generatori**: è la tua correzione. Ai
circolatori il filtro dedicato non serve — il ritorno generale ha già il defangatore — e la
filtrazione sta solo sul primario.

**Come sappiamo che c'è già.** Se su quella tubazione c'è già un filtro.

**Da dove viene.** Dal quaderno Caleffi sulle pompe di calore — molte macchine hanno già un
filtro sull'ingresso dello scambiatore, e sporcandosi strozza la portata: quello esterno si
pulisce meglio — e dalla tua prassi: un filtro sul ritorno di ogni pompa di calore.

## 11 · Defangatore

**Cos'è.** Un corpo largo, spesso con una calamita, dove l'acqua rallenta e i fanghi si
depositano.

**Perché esiste.** Un circuito chiuso continua a produrre fanghi e ossidi anche dopo il
lavaggio, e sono così fini che un filtro a rete non li trattiene: si separano rallentando
l'acqua, non setacciandola. **È per questo che non sostituisce il filtro e il filtro non
sostituisce lui.**

**Dove va, e perché proprio lì.** **Uno solo per circuito, sul ritorno generale**, prima
che il ritorno si divida verso le macchine: lì passa tutta l'acqua che torna, quindi un
pezzo solo protegge ogni generatore. Prima ne mettevamo uno per macchina e perfino sui
circolatori: erano doppioni, e li abbiamo tolti — è la tua correzione.

**Come sappiamo che c'è già.** Se su quel circuito c'è già un separatore di fanghi.

**Da dove viene.** Dal quaderno Caleffi — un filtro defangatore sulla linea di ritorno
verso il generatore — e dagli schemi delle centrali domestiche, che ne disegnano uno solo.

---

# Aria, misure, riempimento, svuotamento

## 12 · Separatore d'aria

**Cos'è.** Un corpo dove l'acqua rallenta e le bollicine risalgono e vengono espulse.

**Perché esiste.** L'acqua libera l'aria che tiene disciolta quando si scalda, e l'aria in
circolo fa rumore, blocca i terminali e corrode.

**Quando vale.** Sopra i 35 kW. Sotto, non si mette: nelle piccole centrali basta lo sfogo
sul serbatoio — è la scheda dopo.

**Dove va, e perché proprio lì.** Sulla **mandata generale**, a valle di chi scalda e dove
le mandate sono già diventate una: lì le bollicine ci sono ancora e si lasciano
raccogliere. Uno per circuito: uno per macchina era un doppione.

**Come sappiamo che c'è già.** Se su quel circuito c'è già qualcosa che separa l'aria.

**Da dove viene.** Dal quaderno Caleffi: un disaeratore a valle della pompa di calore,
obbligatorio nei circuiti chiusi, salvo i piccoli contenuti d'acqua dove basta la valvola
di sfogo.

## 13 · Valvola di sfogo aria

**Cos'è.** La valvolina automatica che espelle l'aria dal punto alto.

**Perché esiste.** Nella piccola centrale l'aria non vuole un separatore: si raccoglie da
sola nel punto più alto, che è il serbatoio, e lì basta sfogarla.

**Quando vale.** Sotto i 35 kW, ed è la tua prassi: sfogo sul serbatoio, e stop.

**Dove va, e perché proprio lì.** Sull'attacco che il serbatoio dedica allo sfiato, come i
costruttori lo dichiarano in legenda. Una per serbatoio. Le macchine il proprio sfogo lo
portano già a bordo.

**Come sappiamo che c'è già.** Se quell'attacco ha già la sua valvola.

**Da dove viene.** Dal quaderno Caleffi — sotto i 300 litri di contenuto basta la valvola
di sfogo — e dalle legende dei costruttori di serbatoi, che dedicano allo sfiato un attacco.

## 14 · Termometro

**Cos'è.** Un termometro in un pozzetto, che si legge senza toccare l'acqua.

**Perché esiste.** La temperatura con cui l'acqua parte è il primo dato che si guarda per
sapere se l'impianto sta lavorando come deve.

**Quando vale.** Sopra i 35 kW, dove la Raccolta R lo prescrive per ogni generatore. Sotto,
non si aggiunge: si usa quello integrato della macchina — negli schemi delle piccole
centrali un termometro sul primario non compare.

**Dove va, e perché proprio lì.** Sulla tubazione che esce da dove il calore entra
nell'acqua. Più a valle si legge una temperatura già mescolata con i ritorni, che è un
altro numero.

**Come sappiamo che c'è già.** Se su quella tubazione c'è già un termometro.

**Da dove viene.** Dalla Raccolta R; sotto i 35 kW dalla tua prassi, riscontrata sugli
schemi.

## 15 · Manometro

**Cos'è.** Un manometro con il suo rubinetto, che si sfila chiudendo l'acqua.

**Perché esiste.** La pressione di un circuito chiuso è la spia della sua salute: se cala,
l'impianto perde; se sale, il vaso non sta lavorando.

**Dove va, e perché proprio lì.** Sul **ritorno generale**, accanto al punto in cui il
circuito si riempie, così chi reintegra legge mentre carica. Sul tratto comune, non sul
ramo di una macchina: stessa correzione del vaso.

**Quante volte.** Uno per circuito di riscaldamento: la pressione è la stessa dappertutto,
un secondo punto di lettura non aggiunge niente.

**Come sappiamo che c'è già.** Se su quel circuito c'è già una lettura di pressione.

**Da dove viene.** Dalla Raccolta R.

## 16 · Gruppo di riempimento

**Cos'è.** Il gruppo che collega la rete idrica al circuito chiuso e ne controlla la
pressione di carico.

**Perché esiste.** Un circuito chiuso non si alimenta da nessuna parte: va riempito, e poi
reintegrato quando cala. A pressione controllata, altrimenti la rete idrica lo porterebbe
alla propria.

**Dove va, e perché proprio lì.** Sul **ritorno generale**, nel punto più freddo del
circuito: l'acqua di rete entra senza scaldarsi di colpo, e il reintegro serve tutte le
macchine invece del ramo di una sola.

**Quante volte.** Uno per circuito di riscaldamento. **Solo sul riscaldamento:** il
circuito sanitario è già alimentato dalla rete e non ha niente da riempire.

**Come sappiamo che c'è già.** Se su quel circuito c'è già un punto di riempimento.

**Da dove viene.** Dalla Raccolta R; il punto d'innesto sul ritorno generale è quello
dello schema tipico e degli schemi applicativi Caleffi.

## 17 · Attacco di scarico

**Cos'è.** Il rubinetto in basso da cui si svuota un serbatoio.

**Perché esiste.** Chi tiene una riserva d'acqua propria la deve poter svuotare **da solo**,
senza scaricare l'impianto intero. Un tratto di tubo no: si svuota con la tratta a cui
appartiene.

**Dove va, e perché proprio lì.** Tre condizioni, e due ci sono costate un errore ciascuna.

La prima: **sull'attacco che il serbatoio gli dedica**, quando ce l'ha. Il volano lo
dichiara in legenda, e lo scarico si attacca lì senza toccare le tubazioni.

La seconda, per chi l'attacco non ce l'ha: **da dove la riserva si riempie, da lì si
svuota.** Il bollitore sanitario non ha lo scarico in legenda, e si svuota con una
derivazione sull'ingresso dell'acqua fredda. Prima finiva sull'uscita calda: era il
difetto trovato dal collaudo, e adesso ogni serbatoio che ha un punto di riempimento
proprio lo dichiara — mai su un circuito che attraversa il serbatoio scambiando calore,
perché quello svuoterebbe l'impianto e lascerebbe la riserva piena.

La terza: **dal lato del serbatoio** rispetto al rubinetto che lo chiude. Se stesse
dall'altra parte, a rubinetto chiuso svuoterebbe la tratta di là e non il serbatoio.

**Quante volte.** Uno per ogni serbatoio — il volano, il bollitore.

**Come sappiamo che c'è già.** Se su quella tubazione c'è già uno scarico.

**Da dove viene.** Dalle legende dei costruttori — il volano dichiara lo scarico, il
bollitore no — e dalla pratica corrente documentata negli schemi Caleffi.

---

# L'acqua calda sanitaria

## 18 · Valvola miscelatrice termostatica

**Cos'è.** Una valvola che mescola acqua calda e fredda e tiene costante la temperatura in
uscita.

**Perché esiste.** Una riserva d'acqua calda si tiene a temperatura alta per non far
proliferare la legionella. A quella temperatura, però, scotta.

**Dove va, e perché proprio lì.** Sulla tubazione che esce verso le utenze, subito dopo la
riserva: così l'accumulo resta caldo e ciò che arriva ai rubinetti è a temperatura di
utilizzo. Le due cose devono restare separate, ed è la miscelatrice a separarle.

**Quante volte.** Una per circuito di acqua calda sanitaria.

**Come sappiamo che c'è già.** Se su quel circuito c'è già una miscelazione.

**Da dove viene.** Dalla pratica corrente documentata negli schemi Caleffi.

---

# Cose che vale la pena guardare prima di approvare

**I rubinetti sono molti di più di com'era all'inizio, ed è voluto.** Sull'impianto di
prova sono più del doppio. Non è un'inflazione: prima li ricevevano solo le macchine, e il
filtro — che è il pezzo che si smonta più spesso di tutti — non ne aveva nessuno. Se la
crescita ti sembra eccessiva, il punto da discutere non è la regola: è **quali pezzi
dichiarano di smontarsi a impianto acceso**, cioè l'elenco che hai già approvato.

**Due pezzi affacciati sullo stesso tubo prendono un rubinetto solo, in mezzo.** Dal 7
settembre 2026 (DRAW-005): un tratto di tubo è un volume, e un volume si chiude una volta.
Ognuno dei due resta smontabile da solo, perché ha chiusi tutti i tubi che lo toccano; il
rubinetto in mezzo chiude quel tratto per tutti e due. Prima ne comparivano due in fila,
ed era il doppione che hai segnalato.

**Ciò che la macchina porta a bordo non si disegna.** Le monoblocco comuni hanno il
circolatore primario dentro il mantello, e il loro catalogo adesso lo dichiara: nessuna
regola aggiunge un pezzo che sta già dentro la macchina. Vale anche per il vaso, quando
una macchina lo integra e il suo catalogo lo dice.

**Il rubinetto bloccabile si disegna ancora uguale a quello comune.** La distinzione c'è
nel modello, non ancora nel segno: è il passo dei simboli, già in coda.

**L'impianto che ne esce non sta più su un foglio ordinario.** Con tutti questi accessori,
le quattro fasce chiedono più spazio di quanto una A3 ne offra. Non è un difetto delle
regole: è il passo della composizione, che deve ancora essere rifatto e che ha esattamente
questo compito. Le regole si approvano su cosa mettono e dove, non su come ci sta.

---

## Cosa ti stiamo chiedendo

Di leggere le diciassette schede e dirci, per ciascuna: **è vera, è al posto giusto, e ne
manca una?** Se una regola è sbagliata, si corregge da sola senza toccare le altre. Se ne
manca una, ce la dici e la scriviamo con lo stesso stampo: perché esiste, dove va, quante
volte, come si riconosce che c'è già.

**Queste schede dicono il perché. Che cosa sia effettivamente uscito lo mostra l'altro
documento, *Il grafo dell'impianto*:** l'impianto completo letto linea per linea, con
l'indirizzo di ogni pezzo, il fluido di ogni tubazione, e la fila ordinata dei pezzi lungo
ogni tratta — l'ordine lo decide l'assemblatore sui vincoli che ogni regola dichiara. Le
due letture servono insieme: qui si giudica la regola, lì si controlla il risultato. Se una
regola è giusta e il pezzo è finito nel posto sbagliato, si vede solo di là.
