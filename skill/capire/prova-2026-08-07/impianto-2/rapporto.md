# Rapporto — Esempio 2, pompa di calore con deviazione tra climatizzazione e ACS

Committente: Nove C · Codice di commessa: PROVA · Revisione 00 · Data 2026-08-07
Consegna: `consegna/grafo.json` (validato), `consegna/rilettura.md`, questo rapporto.

---

## 1. Che impianto ho capito

Una **pompa di calore aria-acqua reversibile da 15 kW** serve, da sola, sia la
climatizzazione sia l'acqua calda sanitaria, e le serve **una alla volta**: sulla sua
mandata c'è una **valvola deviatrice a tre vie** che manda tutto il flusso o al circuito di
climatizzazione o al serpentino del bollitore, con precedenza al sanitario. Sono quindi
due rami che partono dallo stesso punto e rientrano sullo stesso ritorno della macchina.

Sul ramo di climatizzazione c'è un **volume tecnico da 100 litri «a quattro tubi»**: due
attacchi verso la pompa di calore e due verso il circuito che ne esce. Quattro tubi vuol
dire che il volume **separa idraulicamente** il primario dal secondario — è la ragione per
cui il circuito che ne parte è una rete a sé e non il prolungamento del primario. Dal
volume esce il **circuito secondario**, con **circolatore dedicato**, che alimenta i
**fan-coil**, usati d'inverno e d'estate.

Sul ramo sanitario c'è un **bollitore con serpentino**: il serpentino è un pezzo del
circuito della pompa di calore (ci passa acqua di riscaldamento, entra e torna alla
macchina), mentre l'acqua che il bollitore tiene in serbo è un'altra: entra fredda
dall'acquedotto in basso ed esce calda in alto verso le utenze. Sono due cose diverse che
toccano lo stesso serbatoio, ed è per questo che il bollitore è l'unico pezzo del grafo
attraversato da tre fluidi.

Quindi, nelle quattro domande che contano:

- **Che macchina è ciascun pezzo.** La pompa di calore genera calore e basta: il sanitario
  non lo produce da sola, lo produce **tramite** un bollitore separato, quindi resta la voce
  base (`heat-pump-air-water`) e non una macchina che dichiari anche `dhw_storage`. Il
  volume tecnico accumula **e** separa (`buffer-four-port`); il bollitore accumula acqua
  **sanitaria** e ha gli attacchi del serpentino (`dhw-cylinder`).
- **Che acqua porta ogni circuito.** Il sanitario c'è, ed è netto: primario e secondario
  portano acqua di riscaldamento; dall'acquedotto al bollitore c'è acqua fredda sanitaria;
  dal bollitore alle utenze acqua calda sanitaria. Quattro reti.
- **Il regime della centrale.** Un solo generatore, 15 kW, sotto la soglia: `up_to_35_kw`.
  Ricavato, non chiesto.
- **Come i circuiti toccano i serbatoi.** Il serpentino **attraversa** il bollitore
  scambiando calore (`coil_in` → `coil_out`, acqua di riscaldamento); la riserva del
  bollitore la riempie l'alimentazione fredda (`cold_in`) e la preleva `dhw_out`. Sul volume
  tecnico invece l'acqua è la stessa sui quattro attacchi: primario da una parte,
  secondario dall'altra.

Il grafo risultante: **9 componenti, 11 tubazioni, 4 reti, 12 voci dichiarate**. Nessun
accessorio, nessuna sigla inventata (tutti i `tag` sono `null`: il testo non ne scrive).

---

## 2. Domande e assunzioni, in chiaro

Tutte e dodici sono nel JSON in `assumptions`, con `status: "proposed"`. Qui sono
raggruppate per tipo, secondo il §6.

### Tipo A — il testo impone qualcosa ma non dice con che pezzo: chiuso e dichiarato

- **a2 — Circolatore del primario.** Il testo non dice se sul circuito primario ci sia un
  circolatore. Ho seguito la voce di catalogo scelta per la pompa di calore, che dichiara
  il circolatore **a bordo macchina**: nessun circolatore primario è disegnato come pezzo a
  sé. *È così?*
- **a3 — Dove sta il circolatore del secondario.** Il testo dice «circuito secondario con
  circolatore dedicato» ma non su quale ramo. L'ho messo sulla **mandata** del secondario,
  fra l'uscita secondaria del volume e i fan-coil: è la posizione convenzionale, non un
  dato del testo. *Confermare, o spostarlo sul ritorno.*
- **a4 — Quanti fan-coil.** Il testo dice «fan-coil» al plurale senza dirne il numero: ne ho
  disegnato **uno solo, rappresentativo**. *Quanti sono davvero, e come si attestano sul
  circuito secondario — in parallelo su un collettore, su derivazioni consecutive?*
- **a5 — Come si riuniscono i due ritorni.** Il testo non dice con che pezzo il ritorno
  della climatizzazione e il ritorno del serpentino si riuniscono prima di rientrare nella
  pompa di calore. Ho assunto un **raccordo a T di confluenza**, perché un attacco porta una
  tubazione sola. *Se in centrale c'è un collettore o un altro pezzo, va indicato.*
- **a10 — I confini del circuito sanitario.** Il testo dice che l'acqua fredda entra e che
  l'ACS viene prelevata, senza nominare l'acquedotto e le utenze: ho chiuso il circuito
  aperto con le due voci di confine del catalogo.
- **a12 — Come si raggruppano le reti.** Il testo distingue «il circuito di climatizzazione»
  dal ramo verso il bollitore, ma i due nascono entrambi dalla mandata della pompa di calore
  e rientrano sullo stesso ritorno: li ho rappresentati come **due rami di una sola rete
  primaria**, perché una rete parte dalla macchina che la alimenta. Il secondario che parte
  dal volume è invece rete a sé. *Vedi anche §3, punto 1: qui le istruzioni non danno un
  criterio pulito.*

### Tipo B — il catalogo non ha con cosa rappresentarlo

Nessuna. Ogni macchina nominata dal testo ha una voce di catalogo con il mestiere giusto e
gli attacchi che servono a scrivere i collegamenti descritti.

### Tipo C — la scelta è dell'ingegnere, va chiesta prima

Nessuna in senso proprio: non ho trovato un punto in cui due letture ugualmente corrette
producano **due impianti diversi**. L'unica che ci si avvicina è **a12** (raggruppamento
delle reti): due letture ragionevoli producono lo stesso disegno — stessi pezzi, stessi
tubi — ma due modelli diversi, perché cinque tubazioni cambierebbero rete. È una domanda per
chi ha scritto le istruzioni più che per l'ingegnere, e la ritrovi al §3.

### Cose che il testo dice e che il grafo non mostra (registrate perché non vadano perse)

- **a1 — Reversibilità e raffrescamento.** La macchina è reversibile e i fan-coil lavorano
  anche in raffrescamento, ma la tabella dei fluidi non ha un fluido per il freddo:
  primario e secondario sono dichiarati `heating_water`, ed è negli stessi tubi che d'estate
  scorre l'acqua refrigerata. Non ho inventato un fluido che la tabella non ha.
- **a6 — Priorità sanitaria.** È regolazione, non topologia: sul grafo si vede la valvola
  deviatrice, non la priorità.
- **a7 — Carico automatico da acquedotto e scarico sul volume tecnico.** Ferramenta di
  servizio (`filling`, `drain`): li aggiunge il pezzo successivo della catena. Il volume
  scelto ha gli attacchi di servizio (sfiato, scarico, sede sonda) rimasti liberi apposta.
- **a8 — Valvola miscelatrice sull'uscita sanitaria.** La miscelatrice **sanitaria**
  (`dhw_mixing`) è nell'elenco di ciò che non entra mai: la aggiunge il pezzo delle regole.
  *Se invece si intendeva una miscelatrice di circuito a tre vie, va detto: quella sarebbe
  topologia e andrebbe disegnata.*
- **a9 — Ricircolo ACS escluso.** Esclusione esplicita: non è disegnato perché non c'è, non
  perché sia stato perso. Registrato perché nessuno lo riaggiunga.
- **a11 — Alto e basso del bollitore.** Il testo colloca l'ingresso freddo in basso e il
  prelievo in alto: i due attacchi di catalogo lo rappresentano, ma il grafo non porta la
  quota degli attacchi.

---

## 3. Dove le istruzioni non mi hanno detto cosa fare

Sono i punti in cui ho dovuto decidere senza che il §-di-turno mi desse una regola, o in cui
due regole si pestano i piedi. In ordine di peso.

**1. Una valvola deviatrice apre reti nuove, oppure no? (§4.2)**
Il §4.2 dice che «i rami che si staccano da una **ripartizione** restano nella rete da cui
nascono» e che una rete «parte sempre da una macchina che la alimenta … **mai da un
raccordo**». Ma qui il flusso si divide su una **valvola deviatrice**, che il §5 elenca fra
i pezzi di **topologia** (non è un raccordo, ed è una macchina in senso lato: «decide dove
va il flusso»). Le istruzioni non dicono se una deviatrice sia una ripartizione ai fini
delle reti. Due letture, entrambe difendibili: una rete primaria con due rami (la mia,
perché entrambi i rami nascono dalla pompa di calore), oppure due reti perché il testo
nomina «il circuito di climatizzazione» come circuito e lo contrappone alla produzione ACS.
Cambia la rete di 5 tubazioni su 11. Ho scelto e dichiarato (a12), ma il criterio manca.

**2. La derivazione a T è inutilizzabile: due regole che si annullano (§4.3 vs §4.4).**
Il §4.4 prescrive di usare le derivazioni «solo dove il testo descrive qualcosa che si
stacca da un tubo». Ma nel catalogo tutte e tre le derivazioni (`tee-branch`,
`tee-branch-cold`, `tee-branch-dhw`) hanno l'attacco `branch` marcato `stub: true`, e il
§4.3 vieta di collegare qualunque cosa a uno `stub`. Una derivazione, così, non può mai
ricevere il suo ramo: la regola che la prescrive e la regola che la vieta si annullano.
Non mi ha bloccato — qui serviva una confluenza, non una derivazione — ma è una
contraddizione che il prossimo impianto incontrerà (per esempio un ricircolo ACS che
rientra sul tubo, caso citato proprio dal §4.4).

**3. «Valvola miscelatrice» senza aggettivo: dentro o fuori? (§5)**
Il §5 mette dentro le «miscelatrici **di circuito** a tre vie» e fuori la miscelatrice
**sanitaria**. Il testo scrive solo «una valvola miscelatrice». L'ho risolta sulla
posizione — «sull'uscita sanitaria» — e sul catalogo, dove `mixing-valve-thermostatic`
dichiara `dhw_mixing`. Ma le istruzioni non danno il criterio di disambiguazione, e le due
strade non producono un dettaglio diverso: producono un componente in più o in meno.
Dichiarata in a8.

**4. La potenza di una macchina reversibile: 15 kW di che cosa? (§4.6 vs §6)**
Il §4.6 dice cosa fare se il testo dà la potenza «in una forma diversa (potenza resa,
potenza assorbita)», ma non dice niente per un numero nudo — «da 15 kW» — su una macchina
che d'estate non genera affatto calore. Il §6 per contro vieta di chiedere le potenze già
scritte. Ho sommato i 15 kW come potenza del generatore. Qui l'esito non cambia (qualunque
lettura resta sotto i 35 kW), ma su un impianto vicino alla soglia la regola mancherebbe
proprio dove serve.

**5. Il `project_id` e il «titolo dell'impianto» (§3).**
Il §3 dice di costruire il `project_id` «dal titolo dell'impianto» ma non dice da dove si
prende il titolo, né cosa farne quando l'intestazione porta un numero di serie: qui è
«Esempio 2 – Pompa di calore con deviazione tra climatizzazione e ACS». Ho tolto «Esempio
2 –» e tenuto il resto. Scelta mia, senza criterio.

**6. Le chiavi delle `properties` (§3).**
Il §3 chiede di trascrivere «le qualifiche che il testo usa» e mostra tre esempi
(`modello`, `tipo`, `configurazione`), ma non dà un elenco di chiavi né una regola per
inventarne. `tipo`, `impiego`, `configurazione`, `volume`, `potenza` sono nomi che ho scelto
io: due agenti diversi produrrebbero due grafi che dicono la stessa cosa con chiavi diverse,
e chi legge dopo non può contarci.

**7. Il formato della tabella di rilettura (§8, passo 6).**
Le istruzioni chiedono «una riga per frase» e nient'altro: non dicono dove scriverla, in che
formato, né se la verifica al contrario (ogni elemento del grafo risale a una frase) sia una
seconda tabella o la stessa. Ho fatto due tabelle più la lista dei controlli del §9.

**8. Quale uscita della deviatrice va a quale ramo.**
`out_a` e `out_b` sono indistinguibili nel catalogo e le istruzioni non ne parlano. Ho messo
la climatizzazione su `out_a` e il bollitore su `out_b`, seguendo l'ordine in cui il testo
li nomina. Arbitrario, senza conseguenze sul disegno — ma arbitrario.

**9. Dove si incontrano i due ritorni: prima della macchina o dentro il volume.**
Il §4.4 dà il conto dei raccordi («N ritorni sullo stesso attacco → N−1 confluenze») ma non
dà un criterio per il **punto** in cui metterli. Il ritorno del serpentino potrebbe anche
rientrare nel primario del volume tecnico invece che direttamente sulla macchina. Ho scelto
la confluenza subito prima della pompa di calore, perché «devia … **alternativamente**» dice
che i due rami sono paralleli sulla stessa sorgente. Dichiarata in a5.

**Una nota, non una contraddizione.** Il §5 dice che gli accessori nominati dal testo li
aggiungerà il pezzo delle regole, e il §4.3 dice che gli attacchi `stub` esistono apposta.
Il volume tecnico ha gli stub per sfiato, scarico e sonda — ma **non** per il carico
automatico da acquedotto, che il testo nomina (a7). Non è un problema mio, è
un'informazione per chi completerà il grafo: quel gruppo di riempimento dovrà attestarsi sul
tubo, non sul serbatoio.

---

## 4. Isolamento

Ho lavorato solo dentro la mia cartella. Non ho aperto, elencato, cercato né ispezionato
alcun file fuori da
`…/camera-pulita/impianto-2/`: non gli esempi, non le prove, non la documentazione, non il
codice di `/home/user/DisegnatoreMEP`.

L'unica cosa eseguita fuori è **il comando di validazione del §8, passo 7**, lanciato dalla
radice del repository come le istruzioni prescrivono, sul file
`consegna/grafo.json` indicato per percorso esteso. Nessun output: il file carica.
Oltre a quello ho eseguito un controllo scritto da me, che legge soltanto il catalogo della
mia cartella e il mio grafo, per verificare attacchi, versi, fluidi, stub e attacchi
obbligatori liberi (nessun errore).

Nessuna infrazione da dichiarare.
