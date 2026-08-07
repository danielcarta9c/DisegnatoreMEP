# Rapporto — Esempio 5, tre pompe di calore con più circuiti secondari

Committente: Nove C · Commessa: PROVA · Revisione 00 · 7 agosto 2026

Consegna: `consegna/grafo.json` (28 componenti, 36 tubazioni, 8 reti, 16 assunzioni),
`consegna/rilettura.md`, questo rapporto. Il grafo è stato salvato e validato per primo:
il comando del §8 passo 7 non produce output, cioè il file carica.

---

## 1. Cosa ho capito dell'impianto

Una centrale a pompe di calore con **due destinazioni** e un punto di separazione in mezzo.

**Il primario.** Tre pompe di calore aria-acqua reversibili da 35 kW ciascuna, in
parallelo: le tre mandate confluiscono in una mandata comune, i tre ritorni si dividono da
un ritorno comune. Sulla mandata comune c'è una valvola deviatrice a tre vie che manda il
flusso **o** al volume tecnico **o** al serpentino del bollitore. I due ritorni (dal volume
tecnico e dal serpentino) si riuniscono prima di tornare alle macchine. La somma delle
potenze è **105 kW**, quindi il regime della centrale è **oltre i 35 kW**: il conto è
aritmetica su un dato dell'ingegnere, non l'ho chiesto.

**Il punto di separazione.** Il volume tecnico da 500 litri «a quattro tubi» fa due
mestieri insieme — accumula e separa — ed è per questo che a catalogo corrisponde alla voce
con quattro attacchi di flusso (due primari, due secondari): sono esattamente i quattro
tubi che il testo nomina. A monte c'è il circuito dei generatori, a valle i circuiti
dell'edificio, e le due parti non si toccano se non attraverso il volume.

**Il secondario.** Dal volume partono tre circuiti indipendenti, ciascuno con il proprio
circolatore: le batterie delle unità di trattamento aria, i fan-coil, e il pavimento
radiante — quest'ultimo miscelato, cioè con una valvola a tre vie che abbassa la
temperatura di mandata, e usato solo in riscaldamento. Poiché le macchine sono reversibili
e la tabella dei fluidi non ha un fluido per il freddo, i primi due circuiti d'estate
portano acqua refrigerata **negli stessi tubi**: nel modello restano acqua di
riscaldamento, e la cosa è dichiarata.

**Il sanitario.** È un ramo del primario, non un circuito a sé: la stessa acqua delle pompe
di calore, deviata al serpentino del bollitore da 500 litri quando c'è richiesta. Il
sanitario vero e proprio è aperto — entra acqua fredda in basso, esce acqua calda in alto
verso le utenze — con un anello di ricircolo dotato di proprio circolatore. La miscelatrice
termostatica sull'uscita è ferramenta e non entra in questo grafo.

**In una riga:** un primario a tre generatori che si biforca fra accumulo inerziale e
bollitore, e un secondario a tre circuiti che pesca dall'accumulo.

---

## 2. Le domande e le assunzioni, in chiaro

Sedici voci, tutte in `assumptions` con `status: "proposed"`. Le raggruppo per tipo.

### Tipo C — la scelta è dell'ingegnere e cambia il disegno (da portargli prima)

**C1 (a07) — Le batterie delle UTA: una o due?**
Il testo dice «un circuito per le **batterie calde e fredde** delle unità di trattamento
aria»: plurale, e con una distinzione funzionale dentro. Ho disegnato **una sola batteria
rappresentativa** su un solo circuito, come vuole la regola del terminale rappresentativo.
Ma due letture ragionevoli danno due grafi diversi: (a) un circuito con un gruppo di
batterie, (b) un circuito con due rami — batterie calde e batterie fredde — che si staccano
separatamente. *Quante UTA e quante batterie sono? Calde e fredde stanno sullo stesso
circuito o su rami distinti?*

**C2 (a10) — Da dove prende l'acqua di miscelazione la valvola del pavimento?**
Il testo dice «circuito miscelato» e si ferma lì. La valvola a tre vie di catalogo ha tre
attacchi obbligatori: mandata calda, acqua di miscelazione, uscita. Ho chiuso nel modo
convenzionale — una ripartizione a T sul ritorno del pavimento riporta parte dell'acqua
alla valvola — ma se la miscelazione è fatta per iniezione dal primario il disegno è un
altro. *Come è collegata idraulicamente la miscelatrice?*

### Tipo A — chiusure convenzionali dichiarate (il grafo è completo, il dettaglio si corregge)

- **a03 — Come si uniscono le tre pompe in parallelo.** Il testo dice «in parallelo» ma non
  con che pezzo: due raccordi a T in catena sulla mandata, due ripartizioni sul ritorno. Se
  in centrale c'è un collettore va detto — segnalo che il collettore di catalogo ha **due
  sole uscite** e non potrebbe servire tre macchine.
- **a05 — Come si staccano i tre circuiti secondari.** Stesso conto letto dall'altra parte:
  due ripartizioni sulla mandata secondaria, due confluenze sul ritorno. Se è previsto un
  collettore di distribuzione, va detto.
- **a04 — Circolatori sul primario.** Il testo non dice se il circuito dei generatori ha
  circolatori propri: ho seguito la voce di catalogo della pompa di calore, che dichiara di
  portare il circolatore **a bordo**, e sul primario non ho disegnato nulla. *È così?*
- **a06 — Dove stanno i tre circolatori secondari.** Il testo dice «ogni circuito è dotato
  del proprio circolatore» ma non su quale ramo: sulla **mandata** del circuito servito, e
  per il pavimento **a valle** della miscelatrice. Convenzione di disegno, non prescrizione.
- **a08 — Quanti fan-coil.** Uno rappresentativo; il numero non è detto.
- **a09 — Quante zone di pavimento radiante.** Un pannello rappresentativo; il testo non
  dice in quante zone o collettori si divide.
- **a12 — Una sola valvola deviatrice, sulla mandata comune.** Il testo usa il singolare per
  la valvola e il plurale per le pompe: l'ho messa a valle del punto in cui i flussi si
  uniscono. Se invece ogni macchina ha la sua deviatrice, il disegno cambia.
- **a14 — Dove si aggancia il ricircolo ACS.** Il testo dice «collegato al bollitore», ma
  la voce di catalogo del bollitore **non ha l'attacco del ricircolo** e l'attacco non si
  inventa: l'anello si chiude sul tubo, con una ripartizione a valle (verso le utenze) e una
  confluenza subito all'uscita del bollitore. I due punti sono una scelta di disegno.
- **a15 — Acquedotto e utenze.** Il testo non li nomina: ci sono perché il circuito
  sanitario è aperto e il catalogo ha le voci di confine.
- **a16 — Divisione in reti.** Circuito dei generatori + tre circuiti secondari sono reti
  che il testo distingue. Il tratto comune fra volume tecnico e partenze non ha nome nel
  testo e sta in una rete a parte («distribuzione secondaria»); il ramo che carica il
  serpentino è rimasto dentro il circuito dei generatori. Scelta di modello, non frase del
  testo.

### Regolazione ed esclusioni — informazione che il grafo non può mostrare (§4.5, §5)

- **a01 — Reversibilità e raffrescamento.** Le macchine sono reversibili; la tabella dei
  fluidi non ha un fluido per il freddo, quindi tutti i circuiti idronici sono dichiarati
  «acqua di riscaldamento». Circuito dei generatori, batterie UTA e fan-coil portano
  **anche** il raffrescamento; il pavimento no, per dichiarazione del testo.
- **a02 — La cascata è regolazione:** sul grafo si vedono tre macchine in parallelo, non la
  cascata.
- **a11 — La priorità ACS è regolazione:** sul grafo si vede la valvola deviatrice, non la
  priorità.
- **a13 — La miscelatrice termostatica resta fuori:** è ferramenta sanitaria, la aggiunge il
  pezzo successivo della catena. La nomina è registrata perché non vada persa.

### Tipo B — nessuna

Il catalogo aveva una voce per ogni macchina e ogni raccordo che il testo impone. Niente è
rimasto fuori dal grafo per mancanza di catalogo.

---

## 3. Dove le istruzioni non mi hanno detto cosa fare

Questa è la parte che la prova misura. Elenco i punti in cui ho dovuto decidere **senza**
una regola, o con due regole che tiravano in direzioni diverse.

### 3.1 Due istruzioni in contrasto

**P1 — Attacco obbligatorio senza sorgente descritta: chiudere o chiedere?**
Il §4.3 dice che un attacco `required` rimasto libero «vuol dire che hai perso un
collegamento descritto — o che il testo davvero non lo dà, e allora è una **domanda**». Il
§6 dice «mai inventare collegamenti che il testo non descrive», ma il tipo A dice
«il grafo deve chiudersi… **chiudi così e dichiara**». Le tre frasi non si accordano sul
caso concreto della miscelatrice del pavimento: il testo impone la miscelazione (la parola
«miscelato»), il catalogo impone tre attacchi, il testo non dice da dove viene il terzo.
Ho scelto di **chiudere e dichiarare** (C2), perché il §6 dice esplicitamente che «un grafo
incompleto è meno utile di un grafo con una domanda sopra» — ma il §4.3 letto da solo
avrebbe portato a lasciare l'attacco libero, e allora il file non sarebbe stato coerente
con sé stesso. Manca il criterio che dice quale delle due frasi vince.

**P2 — La derivazione di catalogo non è collegabile.**
Il §4.4 parla delle «derivazioni (il pezzo con un braccio che esce dal percorso)» e dice di
usarle «solo dove il testo descrive qualcosa che si stacca da un tubo». Ma le tre voci di
catalogo con mestiere `branch_off` (`tee-branch`, `tee-branch-dhw`, `tee-branch-cold`) hanno
l'attacco `branch` marcato **`stub: true`**, e il §4.3 vieta di collegare qualunque cosa a
un attacco `stub`. Quindi la derivazione, se si seguono le istruzioni alla lettera, **non
può mai essere usata**: il suo unico braccio utile è vietato. Ho usato ripartizioni e
confluenze ovunque, che è anche ciò che il paragrafo sul ricircolo prescrive
esplicitamente; ma la regola sulle derivazioni resta lettera morta e questo va sistemato a
monte (o nel catalogo o nel §4.4).

### 3.2 Scelte lasciate senza criterio

**P3 — A quale rete appartiene un tratto condiviso.**
Ogni tubazione deve dichiarare **una** rete, ma il §4.2 definisce la rete come «un circuito
che il testo nomina o distingue». Il tratto fra il volume tecnico e le tre partenze serve
tutti e tre i circuiti nominati e non ha un nome suo. Le istruzioni non dicono se in questo
caso si debba (a) creare una rete in più, (b) allungare una delle tre, (c) fondere i tre
circuiti in una rete sola. Ho creato la rete `distribuzione-secondaria` e l'ho dichiarata
(a16), ma è una mia invenzione di modello e due agenti diversi qui divergerebbero.

**P4 — Un ramo creato da una deviatrice è una rete nuova?**
Stessa famiglia di problema: il flusso deviato verso il serpentino del bollitore è la stessa
acqua di riscaldamento delle pompe, ma serve un'altra macchina e un altro scopo. L'ho
tenuto dentro il circuito dei generatori. Nessuna regola dice se una biforcazione di
destinazione crei un circuito distinto o no.

**P5 — Un plurale con dentro una distinzione funzionale: si collassa o no?**
Il §7 dice che un plurale vago diventa **un** terminale rappresentativo. Ma «batterie calde
**e fredde**» non è solo un plurale: contiene una distinzione. Le istruzioni non dicono se
la distinzione sopravvive al collasso. Ho collassato e ho chiesto (C1).

**P6 — Su un circuito miscelato, il circolatore va prima o dopo la valvola?**
Il §7 dice «mettilo sulla **mandata** del circuito che serve», ma su un circuito miscelato
la mandata comincia dopo la valvola e prima della valvola c'è ancora il primario. Ho messo
il circolatore **a valle**. La regola non copre il caso.

**P7 — Dove sta una deviatrice rispetto a un gruppo in parallelo.**
Sulla mandata comune (una sola) o su ciascuna macchina (tre)? Nessuna regola; mi sono
appoggiato al singolare/plurale della frase e l'ho dichiarato (a12).

**P8 — L'ordine e l'orientamento delle catene di raccordi.**
Il §4.4 dice quanti raccordi servono (N−1), non **in che ordine** le macchine entrano nella
catena né quale ramo prende l'uscita `b` e quale la `c`. Sono scelte arbitrarie che cambiano
il disegno finale e che ho fatto senza criterio (pdc-1 e pdc-2 sul primo raccordo, pdc-3 sul
secondo; e così per i tre circuiti secondari).

**P9 — I nomi delle chiavi di `properties`.**
Le istruzioni danno esempi (`potenza`, `volume`, `modello`, `tipo`, `configurazione`) ma non
un elenco chiuso. Per le qualifiche d'uso dell'ingegnere («accumulo inerziale e punto di
separazione», «utilizzato solo in riscaldamento», «batterie calde e fredde») ho inventato la
chiave `impiego`. Due esecuzioni della stessa istruzione produrrebbero chiavi diverse per lo
stesso testo, e chi legge dopo non sa cosa cercare.

**P10 — `project_id` dal «titolo dell'impianto».**
Il titolo del testo è «Esempio 5 – Tre pompe di calore con più circuiti secondari». Le
istruzioni non dicono se la numerazione dell'esempio faccia parte del titolo, né come
trattare le lettere accentate (lo schema vuole `^[a-z][a-z0-9_-]*$`). Ho tolto «Esempio 5»
e ho scritto `tre-pompe-di-calore-circuiti-secondari`, perdendo la parola «più».

**P11 — Il formato di `source_message_refs`.**
Le istruzioni dicono che serve «per citare la frase del testo», non in che forma (citazione
letterale? numero di frase? identificativo del messaggio?). Ho usato citazioni letterali
brevi.

**P12 — Accenti sì o no nel JSON.**
L'esempio del §3 scrive le assunzioni in ASCII («e'» invece di «è»), ma nulla dice che il
file debba essere ASCII. Ho seguito lo stile dell'esempio dentro i testi delle assunzioni e
ho usato gli accenti veri nei metadati e nei nomi delle reti: il risultato è un file
tipograficamente incoerente per colpa di un'istruzione che non c'è.

### 3.3 Cose che le istruzioni coprono, ma solo per implicazione

**P13 — Togliere un accessorio in linea salda i due tubi che separava.**
La miscelatrice termostatica sta *sull'uscita* dell'ACS, cioè in mezzo al percorso. Il §5
dice di non disegnarla; ne segue che la tubazione dal bollitore alle utenze diventa
continua, ma questo le istruzioni non lo dicono mai in modo esplicito. L'ho fatto e l'ho
dichiarato (a13), così il pezzo successivo sa che deve inserirla, non aggiungerla in fondo.

**P14 — Il regime si ricava anche quando la singola macchina sta esattamente sulla soglia.**
Ogni pompa è da 35 kW, cioè *esattamente* il valore di confronto; il §4.6 però dice di
sommare, e la somma è 105 kW. Nessuna ambiguità nel testo delle istruzioni — lo segnalo solo
perché è il tipo di numero su cui un lettore distratto sbaglierebbe, e perché il risultato
(`over_35_kw`) cambia le regole del pezzo successivo della catena.

---

## 4. Isolamento

Il vincolo è stato rispettato: ho letto **solo** file dentro la mia cartella di lavoro
(`ISTRUZIONI.md`, `testo-del-committente.txt`, i 53 file di `examples/layout/catalog/`,
`naming/families.json`, `naming/media.json`, `schemas/project.schema.json`). L'unica cosa
eseguita fuori è il comando di validazione del §8 passo 7, lanciato dalla radice del
repository come le istruzioni prescrivono, senza aprire, elencare o ispezionare nulla.
Nessuna infrazione da dichiarare.
