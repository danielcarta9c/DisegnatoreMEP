# Rapporto — Esempio 3, pompa di calore diretta su pavimento radiante

Consegna: `consegna/grafo.json` (scritto e validato per primo), `consegna/rilettura.md`, questo file.
Committente «Nove C», codice di commessa «PROVA», revisione `00`, data 2026-08-07.

---

## 1. Cosa ho capito dell'impianto

**Un solo circuito termico, chiuso, senza separazione.** Una pompa di calore aria-acqua da
8 kW alimenta *direttamente* il pavimento radiante: nessun separatore idraulico (il testo lo
esclude in parole), nessun circolatore esterno (è quello a bordo della macchina). Il circuito
è uno solo, dal generatore al collettore ai circuiti ambiente e ritorno: una sola rete
`heating_water`.

**Il volume tecnico è un volano in serie, non un disaccoppiatore.** Cinquanta litri «a due
tubi, montato in serie» sul ritorno: entra da un attacco ed esce dall'altro, sulla stessa
acqua e sullo stesso circuito. Serve a fare massa d'acqua per la pompa di calore, non a
separare due circuiti — ed è la ragione per cui la voce di catalogo giusta è il volano a due
attacchi e non uno dei due accumuli a quattro, che dichiarano anche `hydraulic_separation`:
quel mestiere il testo lo esclude espressamente. Le tre cose (niente separatore, due tubi, in
serie) dicono la stessa cosa da tre lati.

**Il sanitario esiste, e non tocca il riscaldamento.** Il boiler in pompa di calore da 200
litri produce l'acqua calda **da solo** — la voce di catalogo scelta dichiara insieme
`heat_generation` e `dhw_storage`, e infatti è una macchina che scalda e accumula senza
serpentino da alimentare. Questa è l'affermazione più importante da non sbagliare: il testo
dice «completamente separata» e «non collegato idraulicamente», quindi fra boiler e circuito
di riscaldamento non c'è e non deve comparire nessun tubo. Il sanitario resta un circuito
aperto a sé: acqua fredda in ingresso, acqua calda alle utenze — due reti, perché il fluido
cambia dentro la macchina.

**Il regime è quello della piccola centrale.** L'unica potenza scritta è 8 kW; 8 ≤ 35, quindi
`up_to_35_kw`. Il dato è dell'ingegnere, il conto è aritmetica.

**Cosa il grafo non mostra, e non perché sia stato perso:** il gruppo di riempimento da
acquedotto e lo scarico sul volano (ferramenta), le valvole di zona e la regolazione di zona
(logica), il circolatore integrato (è dentro la macchina), il separatore idraulico (non c'è).
Tutte e quattro le cose sono scritte in `assumptions`, così il pezzo che completa il grafo sa
che sono state lette.

Il grafo risultante: 9 componenti, 9 tubazioni, 3 reti, 8 voci in `assumptions`. Nessun
attacco obbligatorio libero, nessuno `stub` toccato, nessun `tag` inventato.

---

## 2. Domande e assunzioni, in chiaro

Le otto voci sono nel JSON con `status: "proposed"` e la frase del testo da cui nascono.
Qui in chiaro, con il tipo secondo §6 — il tipo **non** entra nel JSON, che non ha un campo
per dirlo (vedi §3, punto 8).

### Domande vere (chiedono una risposta all'ingegnere)

1. **`a1` — Quanti sono i circuiti ambiente?** *(tipo A)*
   Il testo dice «più circuiti ambiente» e non dice quanti. Ne ho disegnati **due**,
   rappresentativi, uno per ciascuna delle due uscite che la voce di catalogo del collettore
   dichiara obbligatorie. Il numero vero è dell'ingegnere.

2. **`a2` — Con che pezzo si riuniscono i ritorni dei circuiti prima del volano?** *(tipo A,
   con un difetto di catalogo dentro — vedi §3, punto 2)*
   La voce di catalogo del collettore ha solo il lato di mandata (un ingresso, due uscite) e
   **non ha la barra di ritorno**. Per scrivere il ritorno unico che il testo descrive («sul
   ritorno dell'impianto radiante») ho riunito i due ritorni con un raccordo a T. Nella
   realtà il punto di riunione è quasi certamente la barra di ritorno dello stesso collettore:
   confermare, o dire come sta davvero.

3. **`a7` — Il boiler sanitario è alimentato da acquedotto e serve le utenze?** *(tipo C — la
   scelta cambia il disegno, e nessuna delle due strade è sbagliata; vedi §3, punto 3)*
   Il testo dice che la produzione di ACS è completamente separata e non collegata
   idraulicamente al riscaldamento — e così l'ho rappresentata. Ma non dice **come** il boiler
   sia alimentato né dove mandi l'acqua calda. Ho chiuso i suoi due attacchi obbligatori sui
   confini di rete (alimentazione di acqua fredda in ingresso, utenze sanitarie in uscita).
   L'altra lettura possibile — disegnare il boiler isolato, con i due attacchi liberi, perché
   il testo quei collegamenti non li scrive — dà un grafo diverso e altrettanto difendibile.

4. **`a8` — La potenza del boiler in pompa di calore va dichiarata?** *(tipo A/C di confine;
   vedi §3, punto 4)*
   Il regime è ricavato dall'unica potenza scritta: 8 kW ≤ 35 kW → `up_to_35_kw`. Ma il boiler
   in pompa di calore è anch'esso una macchina che genera calore (la sua voce di catalogo
   dichiara `heat_generation`) e il testo non ne dà la potenza — i 200 litri sono il volume di
   accumulo. Se una potenza va dichiarata anche per quello, il conto della somma va rifatto.

### Assunzioni dichiarate che non chiedono risposta (dicono cosa il grafo mostra e cosa no)

5. **`a3` — Circolatore integrato.** La circolazione è affidata al circolatore a bordo della
   pompa di calore: non è disegnato come pezzo a sé, come dice il testo, e la voce di catalogo
   scelta lo porta a bordo. Nessun circolatore esterno sul circuito radiante.

6. **`a4` — Separatore idraulico escluso.** «Non è previsto»: non è disegnato perché non c'è,
   non perché sia stato perso. Da qui anche la scelta del volano a due attacchi.

7. **`a5` — Carico automatico e scarico sul volume tecnico.** Il testo li nomina; sono
   ferramenta (`filling`, `drain`) e li aggiunge il pezzo successivo della catena. La nomina
   non è persa, e la voce del volano porta gli attacchi di servizio a cui appenderli.

8. **`a6` — Regolazione di zona.** È logica di regolazione, non topologia: sul grafo si vedono
   il collettore e i circuiti che ne partono, non la regolazione né le valvole di zona (che
   sono ferramenta).

---

## 3. Dove le istruzioni non mi hanno dato un criterio

Ordinati dal più pesante al più leggero. Sono i punti in cui ho dovuto decidere io con le
istruzioni in mano ma senza una regola che arbitrasse.

**1. «Un terminale rappresentativo» contro gli attacchi obbligatori del collettore — due
regole che si contraddicono su questo impianto.**
§7 dice, senza eccezioni: «i fan-coil» → *un solo* componente rappresenta l'insieme. Ma la
voce di catalogo del collettore di zona ha **due** uscite entrambe `required: true`, e §4.3
prescrive di controllare che nessun attacco obbligatorio resti libero, e §9 lo rimette in
lista di controllo. Seguendo §7 alla lettera resta un'uscita obbligatoria scollegata;
riempiendole tutte e due si disegnano due terminali dove §7 ne vuole uno.
*Ho scelto due circuiti rappresentativi* — perché il testo dice «più circuiti» (plurale, cioè
almeno due) e perché §4.1 vuole la voce «i cui attacchi permettono di scrivere esattamente i
collegamenti che il testo descrive» — e ho dichiarato la domanda sul numero vero (`a1`). Ma le
istruzioni non dicono quale delle due regole vince, e con un catalogo diverso (un collettore a
sei uscite obbligatorie) la contraddizione sarebbe molto più vistosa.

**2. Il collettore di catalogo non ha il lato di ritorno: tipo A o tipo B?**
Un collettore di zona, nella realtà, ha una barra di mandata **e** una di ritorno. La voce
`zone-manifold` ha un ingresso e due uscite, e basta. Il testo descrive un ritorno unico
dell'impianto radiante, quindi i ritorni dei circuiti si riuniscono da qualche parte.
Le istruzioni offrono due strade opposte e non dicono quale si applica:
- §4.4 → «dove il testo fa incontrare N tubazioni in un punto, servono N−1 raccordi» +
  assunzione (tipo A: chiudi e dichiara);
- §4.1 e §6 tipo B → «se nessuna voce combacia — gli attacchi non bastano per i collegamenti
  descritti — non ripiegare su una voce sbagliata»: quel collegamento non si disegna.
*Ho scelto la strada A* (raccordo a T + `a2`), perché §4.3 dice che un circuito chiuso si
chiude e un grafo aperto sul ritorno non sarebbe utilizzabile a valle. Ma il risultato è che
nel grafo compare un raccordo dove in cantiere c'è la barra di ritorno del collettore: è una
piccola bugia topologica che le istruzioni non mi danno modo di evitare.

**3. «Solo ciò che il testo dice» contro «i circuiti sanitari sono aperti»: il boiler
separato.**
§1 e §6 sono categorici: nel grafo entra solo ciò che il testo dice, mai collegamenti che il
testo non descrive. §4.3 è altrettanto esplicito nella direzione opposta: «i circuiti sanitari
sono aperti: entrano dall'acquedotto, escono alle utenze», e il catalogo ha le voci di confine
apposta. Qui il testo nomina una macchina che produce ACS ma **non nomina né l'acquedotto né
le utenze** — anzi insiste sul fatto che è «completamente separata».
Le istruzioni non dicono se la frase di §4.3 sia una regola di trascrizione (come «un circuito
chiuso si chiude», dove disegnare il ritorno è trascrizione e non invenzione) oppure una
descrizione di come sono fatti gli impianti, che non autorizza ad aggiungere niente.
*Ho chiuso sui confini e l'ho dichiarato* (`a7`), perché i due attacchi del boiler sono
`required: true` e perché un boiler che non riceve acqua fredda e non serve nessuno non è
leggibile a valle. È la voce che ho segnalato come tipo C: due letture ragionevoli, due grafi
diversi, nessuna delle due sbagliata.

**4. Il regime della centrale quando *una parte* delle potenze è data.**
§4.6 prevede due casi soli: il testo dà le potenze (sommale) oppure il testo non le dà (ometti
il campo e chiedi). Qui il testo dà la potenza di **uno** dei due generatori — la pompa di
calore, 8 kW — e non dà quella dell'altro, il boiler in pompa di calore, che pure dichiara
`heat_generation` in catalogo e quindi, alla lettera di §4.6, «conta».
Nessuna delle due strade previste combacia. *Ho scritto il regime ricavandolo dalla potenza
scritta e ho dichiarato la lacuna* (`a8`), perché §1 e §6 vietano di chiedere una cosa che il
testo ha già scritto, e omettere il campo avrebbe buttato via gli 8 kW che l'ingegnere ha
scritto. Ma è una scelta mia: l'altra lettura («le potenze non ci sono tutte, quindi ometti»)
non è esclusa dalle istruzioni.
*Nota di contorno:* la soglia dei 35 kW nasce, come dice lo schema stesso, dalla potenza dei
**focolari**. Qui non c'è nessun focolare: sono due pompe di calore. §4.6 non prevede
l'eccezione e dice di sommare «le macchine che generano calore», quindi l'ho applicata alla
lettera — ma vale la pena saperlo.

**5. Quanto della prosa diventa `properties`, e con che nomi di campo.**
§3 dice di trascrivere «i dati che il testo dà» e anche «le qualifiche che il testo usa»,
perché «trascriverle non costa nulla». Non dice dove finisce la qualifica e comincia il
racconto: «con funzione di aumento del contenuto d'acqua e stabilizzazione del funzionamento
della pompa di calore» è una qualifica o una spiegazione? E i nomi delle chiavi
(`potenza`, `volume`, `modello`, `tipo`, `configurazione`) sono esempi, non un elenco chiuso:
niente vieta che due grafi scritti da due agenti diversi chiamino la stessa cosa in due modi.
*Ho trascritto in modo generoso* (compresa la funzione del volano, sotto la chiave `funzione`)
e ho usato le chiavi italiane degli esempi dove combaciavano.

**6. Il `project_id` «costruito dal titolo dell'impianto».**
Il testo si intitola «Esempio 3 – Pompa di calore diretta su pavimento radiante». Le
istruzioni non dicono se la numerazione della raccolta faccia parte del titolo.
*Ho tenuto solo il titolo descrittivo* → `pompa-di-calore-diretta-su-pavimento-radiante`,
perché «Esempio 3» descrive la raccolta di prove, non l'impianto.

**7. `source_message_refs`: nessun formato dichiarato.**
§3 dice che «puoi usare `source_message_refs` per citare la frase del testo», e lo schema
vuole una lista di stringhe. Non dice se siano identificativi di messaggio, numeri di riga o
citazioni. *Ho messo la frase citata alla lettera*, che è la cosa che si rilegge da sola.

**8. `assumptions` porta tre cose diverse, e il modello non le distingue.**
Le istruzioni ci fanno entrare (a) le domande vere da girare all'ingegnere, (b) le chiusure
convenzionali già decise e da confermare, (c) le semplici notifiche che qualcosa è stato letto
e lasciato fuori apposta (la ferramenta di §5, le esclusioni esplicite di §4.5, la logica di
regolazione). Sono tre atti diversi: una vuole risposta, una vuole conferma, una non vuole
niente. Lo schema ha solo `status: proposed | approved | rejected`, e §6 chiede di distinguere
i tipi A/B/C ma il JSON non ha un campo per scriverli. *Ho tenuto la distinzione nella prosa
di ogni voce e in questo rapporto* — dove però il pezzo successivo della catena non la legge.

**9. Cosa faccio del secondo pezzo rappresentativo quando ne servono due.**
Legato al punto 1: due `underfloor-panel` identici, entrambi con le stesse `properties`,
rappresentano «più circuiti ambiente». Le istruzioni non dicono se due terminali
rappresentativi vadano distinti in qualche modo (nomi, proprietà, una nota) o se debbano
restare gemelli. *Li ho lasciati gemelli*, con la sola differenza dell'`id`.

---

## 4. Isolamento

Non ho aperto, letto, elencato né cercato alcun file fuori dalla cartella di lavoro. Ho
eseguito, dalla radice del repository, il solo comando di validazione descritto al §8 passo 7
delle istruzioni — l'eccezione prevista — che ha caricato il grafo senza output, cioè senza
errori. Nessuna infrazione da dichiarare.
