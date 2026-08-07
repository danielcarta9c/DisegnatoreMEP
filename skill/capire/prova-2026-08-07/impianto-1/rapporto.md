# Rapporto — grafo di prima stesura, Esempio 1

Committente: **Nove C** · commessa: **PROVA** · revisione 00 · data 2026-08-07
Consegna: `consegna/grafo.json` (validato), `consegna/rilettura.md`, questo rapporto.

---

## 1. Cosa ho capito dell'impianto

Una **piccola centrale a pompa di calore con accumulo combinato**, che fa riscaldamento e
acqua calda sanitaria con una macchina sola di accumulo.

**Generazione.** Due pompe di calore aria-acqua da 12 kW ciascuna, **in parallelo**: le due
mandate confluiscono in un tubo solo che entra nell'accumulo, e il ritorno dall'accumulo si
divide per rientrare nelle due macchine. Somma delle potenze di generazione: **24 kW**, sotto
la soglia dei 35 kW → `plant_regime: "up_to_35_kw"`. Master e slave è regolazione, non
topologia: sul grafo le due macchine sono uguali e intercambiabili.

**L'accumulo, che è il pezzo su cui si decide tutto il resto.** L'ECOcombi da 200 litri fa
**due mestieri contemporaneamente**, e li fa su acque diverse:

- **accumula acqua di riscaldamento** e separa idraulicamente il primario dal secondario —
  da qui i «quattro tubi» del testo: due verso i generatori, due verso il circuito secondario;
- **produce l'ACS in modo istantaneo** facendo passare l'acqua **sanitaria** dentro un
  serpentino immerso nel volume: entra fredda da un lato, esce calda dall'altro.

È il punto del §9 («quale circuito attraversa il serbatoio scambiando calore e quale ne riempie
la riserva»): qui **la riserva è di acqua di riscaldamento** e **nel serpentino corre l'acqua
sanitaria** — il contrario di un bollitore, dove la riserva è sanitaria e nel serpentino corre
l'acqua di riscaldamento. Per questo la voce di catalogo è `buffer-combined` (mestieri
`hydraulic_separation` + `thermal_storage`, `stored_medium: heating_water`, con gli attacchi
`cold_in` / `dhw_out` per il serpentino sanitario) e **non** `dhw-cylinder`, che è il bollitore
e avrebbe rovesciato la lettura, né `buffer-four-port`, che il sanitario non lo fa affatto.

**Distribuzione.** Dal volume tecnico parte un solo circuito secondario, con circolatore
dedicato, che alimenta **direttamente** i radiatori esistenti — nessuna miscelazione, nessun
collettore interposto: il testo dice «direttamente».

**Sanitario.** Circuito **aperto**: entra dall'acquedotto (confine), attraversa il serpentino,
esce alle utenze (confine). Il fluido cambia attraversando il serpentino, quindi le reti sono
due: `cold_water` prima, `domestic_hot_water` dopo. Niente ricircolo — il testo lo esclude.

**Reti in tutto: quattro.** `primario` e `secondario` (entrambe `heating_water`, ma il testo le
distingue e l'accumulo le separa idraulicamente), `acqua-fredda`, `acs`.

**Fuori dal grafo per scelta delle istruzioni:** carico automatico e scarico sul volume
tecnico (ferramenta di servizio), che aggiunge il pezzo successivo della catena.

Numeri: 9 componenti, 4 reti, 11 tubazioni, 10 assunzioni. Nessun attacco `required` è rimasto
libero, nessun attacco porta due tubazioni, nessuno stub è stato toccato.

---

## 2. Domande e assunzioni, in chiaro

Sono le dieci voci di `assumptions` del JSON, tutte con `status: "proposed"`. Quelle con il
punto interrogativo aspettano una risposta dell'ingegnere; le altre sono registrazioni, perché
un'informazione del testo che il grafo non mostra non vada persa.

### Domande (aspettano una risposta)

1. **a1 — Con che pezzo si mettono in parallelo le due pompe di calore?** Il testo dice «in
   parallelo» ma non dice come: ho usato un raccordo a T sulla mandata e una ripartizione a T
   sul ritorno (due tubazioni che si incontrano = un raccordo). Se in centrale c'è un
   collettore o un separatore idraulico dedicato, il grafo va corretto.
2. **a3 — I circolatori del primario sono a bordo delle pompe di calore?** Il testo non lo
   dice; ho seguito la macchina di catalogo, che dichiara di portarli a bordo. Se ci sono
   circolatori primari esterni, vanno disegnati.
3. **a4 — Il circolatore del secondario sta sulla mandata o sul ritorno?** Il testo dice
   «circolatore dedicato» senza dire su quale ramo: l'ho messo sulla mandata che esce
   dall'accumulo, per convenzione di disegno.
4. **a5 — Quanti sono i radiatori, e c'è una distribuzione a monte?** «L'impianto esistente a
   radiatori» è plurale e vago: ne ho disegnato uno solo, rappresentativo dell'insieme.
5. **a6 — È giusta questa lettura dell'ECOcombi?** Nel grafo il volume accumula acqua di
   riscaldamento e nel serpentino passa l'acqua sanitaria che si scalda attraversandolo; il
   serpentino non è un componente a sé, è la coppia di attacchi sanitari dell'accumulo. Se
   l'ECOcombi funzionasse al contrario (riserva sanitaria, serpentino di riscaldamento), la
   voce di catalogo sarebbe un'altra e il grafo cambierebbe.
6. **a10 — I 12 kW sono potenza resa o assorbita?** Ho sommato i numeri come sono scritti
   (12 + 12 = 24 kW). *Nota: in questo caso la risposta non cambia il regime — sotto i 35 kW
   con ogni lettura — ma cambia la lettura del dato.*

### Registrazioni (nessuna risposta necessaria, servono a chi viene dopo)

7. **a2 — Master e slave sono regolazione:** sul grafo si vedono due macchine uguali in
   parallelo, non chi comanda. E poiché il testo non dice **quale** delle due sia la master,
   nel grafo le due non sono distinte: attribuire il ruolo sarebbe stata una scelta silenziosa.
8. **a7 — Il ricircolo sanitario è escluso dal testo:** non è disegnato perché non c'è, non
   perché sia stato perso. Chi completa il grafo non lo aggiunga.
9. **a8 — Carico automatico e scarico sul volume tecnico sono nominati dal testo** ma sono
   ferramenta di servizio: li aggiunge il pezzo delle regole. Conseguenza da leggere insieme:
   in questo grafo l'acqua di acquedotto arriva **solo** al serpentino sanitario, e il ramo che
   porterebbe l'acquedotto al carico del volume non è disegnato.
10. **a9 — Le utenze sanitarie non sono descritte:** l'uscita dell'ACS è chiusa su un solo
    confine rappresentativo, come l'ingresso è chiuso sul confine dell'acquedotto.

### Nessuna domanda di **tipo C** in senso stretto

Nessuna delle ambiguità trovate soddisfa tutte e tre le condizioni del §6 (il testo tace + due
strade entrambe corrette + il disegno cambia davvero). Sono tutte di **tipo A**: chiuse nel modo
convenzionale che le istruzioni indicano, e dichiarate. Le due più vicine al tipo C sono a1
(raccordi contro collettore: cambierebbe il numero dei nodi, non la topologia) e a6 (che
cambierebbe il grafo, ma il testo *lo dice* — «volume tecnico a quattro tubi» + «produzione
istantanea tramite serpentino interno» — quindi la prima condizione non vale).

---

## 3. Dove le istruzioni non mi hanno detto cosa fare

Questo è il punto della prova. Elenco i casi in cui ho dovuto decidere senza una regola, o con
due regole che tiravano in direzioni opposte. In ordine di quanto pesano sul risultato.

### 3.1 Un accessorio escluso che si porta dietro una tubazione (il caso più grosso)

Il §5 dice che la ferramenta non entra mai nel grafo, «nemmeno se il testo la nomina», e il §6
dice che **dove va un accessorio non si chiede mai**. Ma la frase F6 del testo non nomina solo
un accessorio: afferma un **fatto topologico** — l'acqua di acquedotto arriva al volume tecnico,
per una strada che non è il serpentino. Sulla rete `acqua-fredda` questo vorrebbe dire una
ripartizione a T e un secondo ramo.

Le istruzioni non dicono cosa fare della **conseguenza topologica di un accessorio escluso**.
Le due letture possibili:

- disegnare la biforcazione dell'acquedotto (topologia detta dal testo) e lasciare che il pezzo
  successivo ci appenda il gruppo di riempimento;
- non disegnare niente, perché il tubo esiste solo per servire un accessorio che non c'è ancora,
  e il punto in cui si stacca è esattamente ciò che il §6 vieta di chiedere.

Ho scelto la seconda — l'accessorio escluso si porta dietro il suo tubo — perché disegnare la
ripartizione avrebbe significato scegliere in silenzio *dove* si stacca, e perché il §5 dice
che la nomina si conserva in `assumptions`, non nel grafo. Ma è una decisione mia, senza una
riga delle istruzioni dietro, e l'ho scritta per esteso in a8.

### 3.2 Il confine delle utenze sanitarie: due regole che tirano al contrario

Il §4.3 dice che i circuiti sanitari «escono alle utenze» e che per acquedotto e utenze il
catalogo ha le voci di confine. Il §6 vieta di inventare componenti che il testo non nomina —
e il testo dice solo «l'ACS viene prelevata in uscita», le utenze non le nomina.

Ho messo il confine (`dhw-draw-off`) per tre ragioni: «prelevata» è un prelievo, cioè
un'utenza; l'attacco `dhw_out` dell'accumulo è `required: true` a catalogo e senza confine
resterebbe libero, che il §4.3 segnala come un collegamento perso; e senza confine la rete
`acs` non avrebbe termine. L'ho comunque dichiarato (a9). Ma quale delle due regole prevale,
le istruzioni non lo dicono.

### 3.3 Due reti con lo stesso fluido: la priorità fra i due criteri non è detta

Il §4.2 dà due criteri per separare le reti: **il testo le distingue** («il circuito dei
generatori, il circuito secondario che parte da un accumulo») e **il fluido cambia** («dove il
fluido cambia, la rete cambia»). Qui il primo criterio dice due reti, il secondo tace: primario
e secondario portano tutti e due `heating_water`. Il §4.2 dice anche che il fluido «resta il
secondo criterio», ma non dice se il primo basta da solo.

Ho fatto due reti, perché il testo le distingue esplicitamente («parte un circuito secondario»)
e perché l'accumulo scelto dichiara `hydraulic_separation`: sono due circuiti separati, non due
rami dello stesso. Se il criterio giusto fosse il fluido, sarebbero una rete sola.

### 3.4 Una qualifica che il testo dà ma non attribuisce

Il testo distingue le due pompe di calore («una come master e una come slave») ma non dice
quale sia quale. Il §3 dice di trascrivere in `properties` «le qualifiche che il testo usa»; il
§4.5 e il §7 dicono che master/slave è regolazione e va in `assumptions`. Nessuno dei due dice
cosa fare quando la qualifica **esiste ma non è attribuibile**. Non l'ho messa in `properties`
(avrebbe richiesto di scegliere in silenzio quale macchina è la master) e l'ho scritta in a2,
segnalando anche che le due macchine restano indistinguibili nel grafo.

### 3.5 Nomi delle chiavi di `properties`: nessun vocabolario

Il §3 dà esempi (`potenza`, `volume`, `modello`, `tipo`, `configurazione`) ma non un elenco
chiuso, e non dice cosa fare delle qualifiche che negli esempi non compaiono. Ho usato le
chiavi degli esempi e ne ho coniate due: `produzione_acs` («produzione istantanea di acqua
calda sanitaria tramite serpentino interno») e `stato` («esistente», per i radiatori). Se a
valle qualcuno legge le `properties` **per chiave**, questa libertà è un rischio: due agenti
scriveranno chiavi diverse per lo stesso dato.

### 3.6 Metadati e nomi senza criterio

- `metadata.project_name`: il §3 spiega come costruire `project_id` (dal titolo dell'impianto)
  ma non dice cosa metterci dentro. Ho usato il titolo del testo del committente.
- `NetworkModel.name`: il §4.2 non dice come si nomina una rete. Ho usato nomi descrittivi in
  italiano («Circuito primario dei generatori»).
- Gli `id` delle tubazioni: il §3 chiede «id parlanti in italiano», ma l'esempio del §3 usa
  `p1`, `p2`, `p3`. Ho seguito la regola scritta, non l'esempio (`pri-pdc1-raccordo`…).

### 3.7 La tabella di rilettura non ha una forma prescritta

Il §8 passo 6 la chiede — «una riga per frase, con gli elementi del grafo che la rappresentano»
— ma non fissa né le colonne né il formato del file (il nome `rilettura.md` me l'ha dato chi mi
ha lanciato). Ho fatto **due** tabelle, perché il passo 6 chiede il controllo nei due versi
(frase → elementi, ed elemento → frase) e con una tabella sola il secondo verso non si legge.

### 3.8 Gli `stub` nominati dal testo non hanno dove agganciarsi

L'accumulo di catalogo ha tre attacchi di servizio (`vent`, `drain`, `probe`) e il §4.3 dice di
non collegarci niente: rispettato. Ma il testo nomina proprio lo scarico, che è uno di quegli
stub. Il modello non ha un campo per dire «questa nomina riguarda quell'attacco», quindi il
collegamento fra la frase e lo stub vive solo nel testo libero di a8. Non è un errore, è
un'informazione che perde precisione.

### 3.9 Potenza resa o assorbita: il §4.6 chiede di dichiarare, ma non di scegliere

Il §4.6 dice che, se il testo dà la potenza «in una forma diversa», va trascritta com'è e va
dichiarato quale si è sommata. Qui il testo non qualifica affatto il dato («da 12 kW ciascuna»):
non c'è una forma diversa da riconoscere, c'è un'assenza. Ho sommato i numeri come sono scritti
e l'ho dichiarato (a10). Il §4.6 non copre il caso, ma l'esito qui non cambia: 24 kW restano
sotto i 35 con qualunque lettura.

---

## 4. Isolamento

Ho lavorato solo dentro la mia cartella
`…/scratchpad/camera-pulita/impianto-1/`: istruzioni, testo del committente, 53 file di
catalogo (ne ho letti 22, quelli utili alla scelta e ai controlli), `naming/families.json`,
`naming/media.json`, `schemas/project.schema.json`.

**Non ho letto, elencato, cercato né ispezionato alcun file di `/home/user/DisegnatoreMEP`.**
Del repository ho usato soltanto due esecuzioni:

1. il comando di validazione del §8 passo 7, lanciato con la working directory del repository
   com'è prescritto (nessun output = il file carica);
2. l'interprete `.venv/bin/python` per eseguire uno script di controllo **scritto da me** nella
   mia area di scratch, che rilegge solo il mio grafo e il mio catalogo e verifica la lista del
   §9 (attacchi esistenti, nessun doppio collegamento, nessuno stub toccato, verso `out` → `in`,
   fluido coerente, `required` tutti collegati, `tag` nulli, liste vuote). Esito: tutti i
   controlli passati.

Nessun'altra infrazione da dichiarare.
