# Rapporto — Esempio 4, sistema ibrido con pompa di calore e caldaia combinata

Committente: Nove C · Commessa: PROVA · Revisione 00 · 7 agosto 2026

Consegna: `consegna/grafo.json` (scritto e validato per primo), `consegna/rilettura.md`,
questo rapporto.

---

## 1. Cosa ho capito dell'impianto

Un impianto ibrido a due generatori in parallelo, con un volume tecnico che separa i
generatori dall'utenza di riscaldamento, e con la produzione sanitaria istantanea
ricavata deviando il circuito della sola caldaia su uno scambiatore a piastre.

**I generatori.** Una pompa di calore aria-acqua da 10 kW (generatore principale) e una
caldaia a condensazione da 24 kW, in parallelo. «In parallelo» è un'affermazione
topologica: le due mandate si uniscono in un punto (una confluenza) e il ritorno che
esce dal volume si divide verso le due macchine (una ripartizione). Sono i due raccordi
`rc-mandata-generatori` e `rc-ritorno-generatori`.

**Il volume tecnico.** 150 litri, «configurato a quattro tubi»: quattro attacchi di
flusso, due sul lato dei generatori e due sul lato dell'impianto. È il pezzo che tiene
separati i due circuiti — il primario dei generatori e il secondario di riscaldamento —
e per questo le due reti sono distinte anche se portano lo stesso fluido.

**Il riscaldamento.** Dal lato secondario del volume parte un solo circuito, con
circolatore dedicato, che alimenta l'impianto esistente a radiatori e vi ritorna. Il
circuito si chiude sul volume: mandata e ritorno sono la stessa affermazione.

**Il sanitario.** Non c'è accumulo: il testo lo esclude in modo esplicito. Quando c'è
richiesta di ACS, una valvola a tre vie sulla mandata della caldaia manda la portata
allo scambiatore a piastre invece che al volume tecnico. Sul lato secondario dello
scambiatore l'acqua fredda di acquedotto entra e ne esce acqua calda sanitaria diretta
alle utenze: qui il fluido cambia dentro la macchina, quindi sono due reti, `acqua-fredda`
e `acs`, e il circuito è aperto (entra da un confine, esce a un altro).

**Il punto che tiene insieme l'ultima frase con la prima.** «Durante la produzione di ACS
la pompa di calore può continuare ad alimentare il volume tecnico»: questo si regge solo
se la via della pompa di calore verso il volume non passa dalla valvola deviatrice. Nel
grafo infatti la valvola è solo sul ramo della caldaia, e la pompa di calore raggiunge la
confluenza di mandata per conto suo. Il ritorno dello scambiatore rientra sul ritorno
della caldaia, unito con una confluenza al ritorno che arriva dal volume, perché un
attacco porta una tubazione sola.

**Il regime.** 10 + 24 = 34 kW, quindi `up_to_35_kw`. Un solo kW sotto la soglia.

**Cosa non è nel grafo, e perché.** Il carico automatico da acquedotto e lo scarico sul
volume tecnico sono ferramenta di servizio; il bollitore non c'è perché il testo lo
esclude; la logica di integrazione fra i generatori e la priorità sanitaria sono
regolazione. Tutte e tre le cose sono registrate in `assumptions`, perché il pezzo
successivo della catena e l'ingegnere possano verificare che nulla è andato perso.

**Numeri della consegna.** 12 componenti, 4 reti, 15 tubazioni, 12 voci dichiarate.
`subsystems`, `rule_applications` e `sheets` sono liste vuote. Il file carica con lo
strumento di validazione.

---

## 2. Domande e assunzioni, in chiaro

Sono le dodici voci di `assumptions`, tutte con `status: "proposed"`. Fra parentesi il
tipo secondo §6 (il modello non ha un campo per il tipo, quindi lo scrivo solo qui).

1. **`a1` — La caldaia «combinata» (tipo A).** Il testo la chiama combinata, ma poi
   descrive *come* fa il sanitario: valvola a tre vie e scambiatore a piastre esterni.
   Comanda la descrizione, non l'aggettivo: la caldaia è la voce di catalogo base
   (solo generazione di calore) e la produzione sanitaria è disegnata con i pezzi
   descritti. La parola «combinata» è comunque trascritta nelle proprietà. È corretto?

2. **`a2` — Con che pezzo si mettono in parallelo i generatori (tipo A).** Il testo dice
   «in parallelo» ma non dice con che pezzo i flussi si uniscono e si dividono: si sono
   usati i raccordi di catalogo (una confluenza sulla mandata, una ripartizione sul
   ritorno). Se in centrale è previsto un collettore o un altro pezzo, va sostituito.

3. **`a3` — «Configurato a quattro tubi» (tipo A).** Letto come accumulo con quattro
   attacchi di flusso — due sul primario, due sul secondario — cioè un volano che separa
   idraulicamente i due circuiti. È questa la configurazione intesa?

4. **`a4` — Il circolatore del primario (tipo C: due letture, due grafi diversi).** Il
   testo non dice come è messa in circolazione l'acqua del primario. La pompa di calore
   di catalogo porta il circolatore a bordo, quindi non è disegnato; sul ramo della
   caldaia non è stato disegnato alcun circolatore, perché il testo non ne nomina e non
   si inventa. **Domanda per l'ingegnere: il ramo della caldaia ha il circolatore a bordo
   macchina, o ne serve uno esterno da rappresentare?** Se ne serve uno esterno, il grafo
   cambia (un componente e una tubazione in più).

5. **`a5` — Dove sta il circolatore del secondario (tipo A).** Il testo lo nomina ma non
   dice su quale ramo: messo sulla mandata che esce dal volume, per convenzione. Se va
   sul ritorno, si sposta.

6. **`a6` — Quanti terminali (tipo A).** «L'impianto esistente a radiatori» è
   rappresentato da un solo terminale che sta per l'insieme. Quanti circuiti terminali
   partono davvero dal volume tecnico?

7. **`a7` — Carico automatico e scarico sul volume (nomina registrata, §5).** Sono
   ferramenta di servizio e li aggiunge il pezzo successivo della catena. Per lo stesso
   motivo non è disegnato un secondo allacciamento di acquedotto verso il volume: l'unico
   allacciamento rappresentato è quello che alimenta lo scambiatore sanitario.

8. **`a8` — Nessun bollitore (esclusione esplicita, §4.5).** Il testo esclude l'accumulo
   sanitario: non è disegnato perché non c'è, non perché sia stato perso.

9. **`a9` — Regolazione (§4.5).** L'integrazione fra i due generatori e la priorità
   sanitaria non producono né pezzi né tubi. Sul grafo si vede la valvola deviatrice, non
   la priorità né la sequenza di intervento.

10. **`a10` — La valvola deviatrice e il ritorno del ramo sanitario (tipo A).** La valvola
    è sulla mandata della caldaia, perché la voce di catalogo ha un'entrata e due uscite e
    solo lì può stare. Il testo non dice dove rientra il ritorno del primario dello
    scambiatore: si è assunto che rientri sul ritorno della caldaia, con una confluenza
    che lo unisce al ritorno proveniente dal volume.

11. **`a11` — Il ramo verso lo scambiatore è rete a sé o no (tipo A).** Tenuto dentro la
    rete del primario: è la stessa acqua di riscaldamento della caldaia, deviata. Il testo
    lo chiama «il circuito della caldaia»; se lo si vuole leggere come rete separata, va
    separato.

12. **`a12` — Il regime della centrale (dato ricavato, §4.6).** 10 + 24 = 34 kW, quindi
    entro i 35 kW. **Si segnala che la somma sta un solo kW sotto la soglia** e che, in un
    ibrido, i due generatori potrebbero non lavorare mai insieme a pieno carico: se le
    potenze da considerare sono altre (rese, assorbite, al focolare), il regime va
    riverificato.

---

## 3. Dove le istruzioni non mi hanno dato un criterio

Questa è la parte che la prova misura. Elenco i punti in cui le istruzioni tacciono, si
contraddicono, o lasciano scegliere senza dire in base a cosa. Per ciascuno dico cosa ho
fatto.

### 3.1 Contraddizioni vere

**a) §6 vieta di chiedere le quantità, §7 impone di chiederle.** §6 mette fra le cose che
non si chiedono mai «quante taglie o diametri (sono dell'ingegnere, e se non li ha detti
non compaiono)» e fra le cose da non inventare «quantità e taglie non dette (quanti
terminali…)». §7 invece, sul terminale rappresentativo, dice: «se il testo è plurale o
vago, dichiara la domanda (tipo A)» — cioè chiedi quanti sono. Le due frasi si toccano
proprio sul numero dei terminali. *Ho seguito §7*, che è la regola specifica, e ho scritto
`a6`. Una lettura conciliante c'è (il numero dei terminali è topologia, i diametri no), ma
le istruzioni non la esplicitano.

**b) «Macchine che generano calore» (§4.6) contro «potenza dei focolari» (schema).** §4.6
dice di sommare le potenze delle macchine che generano calore. La descrizione del campo
`plant_regime` nello schema motiva la soglia con la Raccolta R, che si applica «agli
impianti con potenza dei focolari superiore a 35 kW». Una pompa di calore focolare non ne
ha: con la prima lettura si somma 10 + 24 = 34 kW, con la seconda si contano solo i 24 kW
della caldaia. Qui l'esito non cambia (entrambe sotto soglia), ma su un impianto un po'
più grande cambierebbe tutto il corredo di regole a valle. *Ho seguito §4.6*, che è la
regola operativa, e l'ho dichiarato in `a12`.

**c) La derivazione ammessa dalle istruzioni ma inservibile nel catalogo.** §5 mette
`branch_off` fra i mestieri che entrano nel grafo e §4.4 parla delle derivazioni come del
«pezzo con un braccio che esce dal percorso». Ma tutte e tre le voci di derivazione del
catalogo (`tee-branch`, `tee-branch-cold`, `tee-branch-dhw`) hanno il terzo attacco
`branch` marcato `stub: true`, e §4.3 vieta di collegare qualunque cosa a un attacco
`stub`. Una derivazione, quindi, è ammessa nel grafo ma non può ricevere niente sul
braccio. *Non ha toccato questo impianto* (non ho usato derivazioni: le due strade che si
separano sono ripartizioni, non derivazioni), ma la regola e il dato si contraddicono.

**d) Le due liste di §5 non coprono tutti i mestieri esistenti.** `air_separation`
(separatore d'aria), e in `families.json` anche `gas_combustion`, `refrigerant_generation`,
`air_movement`, `air_terminal`, `direct_expansion_terminal`, non stanno né nella lista
«entra» né nella lista «non entra mai». §5 dice che un mestiere fuori da entrambe le liste
va trattato come voce di catalogo mancante (tipo B) — ma il separatore d'aria a catalogo
c'è, ed è palesemente ferramenta: la regola porterebbe a dichiarare mancante un pezzo che
esiste. *Non ha toccato questo impianto*, perché il testo non nomina nessuno di questi
mestieri.

### 3.2 Punti in cui le istruzioni tacciono

**e) Il campo `carries_on_board` non è mai nominato.** La voce della pompa di calore
dichiara `carries_on_board: ["circulation"]`, e da questo dipende se il circolatore del
primario si disegna o no. Le istruzioni non nominano mai il campo: §4.1 dice di scegliere
su `functions` e `ports`, e §6 allude alla cosa solo di sbieco («si è seguita la macchina
di catalogo, che lo porta a bordo»). *Ho usato il campo* per non disegnare il circolatore
della pompa di calore.

**f) E il caso simmetrico: la caldaia il campo non ce l'ha.** Le istruzioni non dicono se
l'assenza di `carries_on_board` significhi «questa macchina il circolatore non ce l'ha»
(e allora sul ramo caldaia mancherebbe qualcosa) oppure «il catalogo non si pronuncia».
Fra il divieto di inventare (§6) e il controllo di completezza (§4.3), ho scelto di non
disegnare nulla e di *chiedere*: è `a4`, l'unica domanda di tipo C che pongo.

**g) Nessun criterio per decidere se un ramo deviato è una rete a sé.** §4.2 dà due
criteri che qui non coincidono: «una rete è un circuito che il testo nomina o distingue»
(e il testo dice «il circuito della caldaia») e «il fluido cambia dove una macchina lo
cambia» (e qui non cambia: è sempre acqua di riscaldamento). *Ho scelto la rete unica* e
l'ho dichiarato in `a11`, ma la scelta è mia, non delle istruzioni.

**h) Dove rientra il ritorno di un ramo deviato.** §4.4 dice quanti raccordi servono
quando N tubi si incontrano, ma non dice *dove* si incontrano quando il testo non lo dice.
*Ho scelto* il rientro diretto sul ritorno della caldaia (`a10`).

**i) `properties`: nessun vocabolario di chiavi.** §3 dà esempi (`potenza`, `volume`,
`modello`, `tipo`, `configurazione`) ma non un elenco chiuso, e non dice dove mettere
qualifiche come «combinata», «esistente», «generatore principale». *Ho scelto io* le
chiavi `qualifica`, `stato`, `ruolo`, `denominazione`. Sono parole dell'ingegnere messe
sotto etichette mie: chi legge a valle non ha modo di sapere che quelle etichette non sono
convenzionate.

**j) `project_name` non è definito.** §3 spiega come costruire `project_id` (dal titolo
dell'impianto) ma non dice cosa scrivere in `project_name`. *Ho usato* il titolo del testo
senza la numerazione dell'esempio: «Sistema ibrido con pompa di calore e caldaia
combinata».

**k) La tabella di rilettura non ha una forma prescritta.** §8 passo 6 dice cosa deve
contenere, non quali colonne avere né dove salvarla (il percorso me l'ha dato chi lancia
il lavoro). *Ho scelto io* due tabelle: una dal testo al grafo, una dal grafo al testo,
perché il passo 6 chiede entrambe le direzioni.

**l) Le assunzioni non hanno un campo per il tipo.** §6 costruisce con cura la distinzione
fra tipo A, B e C — e §6 tipo C chiede pure di ripetere la domanda in chiaro — ma il
modello non ha dove registrare il tipo, e le istruzioni non dicono di scriverlo nel testo
della voce. *Ho lasciato* le voci in italiano piano, come chiede §6, e ho messo la
classificazione qui: chi rilegge il solo JSON non distingue una domanda vera (`a4`) da una
registrazione di cose escluse (`a8`).

**m) Nessun ordine prescritto per `assumptions`, `components`, `connections`.** *Ho messo*
i componenti nell'ordine del flusso (generatori, accumulo, ramo sanitario, secondario,
confini) e le assunzioni nell'ordine delle frasi del testo.

### 3.3 Un punto in cui le istruzioni sono chiare ma il risultato è delicato

**n) Il regime a 34 kW.** La regola è aritmetica e l'ho applicata; ma un solo kW separa
questo impianto dal regime che cambia tutte le regole a valle, e §6 vieta esplicitamente
di chiedere all'ingegnere le potenze, perché le ha già scritte. Ho rispettato il divieto:
non chiedo le potenze, segnalo la vicinanza alla soglia e su quali potenze ho fatto la
somma (`a12`). Se le istruzioni volessero che un caso di confine venga sottoposto
all'ingegnere, dovrebbero dirlo: allo stato, il criterio non c'è.

---

## 4. Isolamento

Non ho aperto, letto, cercato né elencato alcun file fuori dalla cartella di lavoro.
L'unica cosa eseguita fuori è il comando di validazione di §8 passo 7, lanciato dalla
radice del repository come le istruzioni prescrivono, sul file in `consegna/`: nessun
output, cioè il file carica. Ho inoltre eseguito un controllo di coerenza scritto da me,
in memoria, che confronta il grafo con il solo catalogo della cartella di lavoro
(esistenza delle voci, esistenza degli attacchi, verso `out`→`in`, fluido uguale ai due
capi, un solo tubo per attacco, nessun attacco `stub` collegato, nessun mestiere della
lista ferramenta, nessun attacco `required` rimasto libero, `tag` tutti nulli): nessun
errore.
