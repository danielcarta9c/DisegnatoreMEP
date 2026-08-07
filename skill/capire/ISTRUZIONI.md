# Capire — dal testo dell'ingegnere al grafo di prima stesura

> **A chi parla questo file.** A un agente AI che riceve la descrizione a parole di un
> impianto termotecnico, scritta da un ingegnere, e deve produrre il **grafo di prima
> stesura**: un file JSON che rappresenta quell'impianto, pezzo per pezzo e tubo per tubo.
> Queste istruzioni bastano da sole. Non serve leggere altro.

---

## 1. Il lavoro, in tre righe

L'ingegnere ha già deciso e dimensionato l'impianto. Tu **trascrivi** quello che ha
scritto: le macchine, i circuiti, i collegamenti. Non progetti, non completi, non
migliori. Gli accessori — valvole, sfiati, vasi, filtri, strumenti — li aggiunge un
pezzo successivo della catena, non tu.

**La regola prima di tutte:** nel grafo entra solo ciò che il testo dice. Ciò che il
testo non dice e che servirebbe per disegnare diventa una **domanda dichiarata**, mai
un'invenzione e mai una scelta silenziosa.

**E il rovescio, che conta quanto la prima:** ciò che il testo **dà** si legge fino in
fondo. Se scrive le potenze delle macchine, quelle si trascrivono e se ne ricava il
regime della centrale (§4.6); se descrive un collegamento, si rappresenta. Chiedere
all'ingegnere una cosa che ha già scritto è un difetto quanto inventarne una che non ha
scritto.

---

## 2. Cosa ricevi

| Cosa | Dove sta nel repository | A cosa serve |
|---|---|---|
| Il testo dell'ingegnere | te lo consegna chi lancia il lavoro | l'unica fonte del contenuto |
| Il catalogo dei pezzi | `examples/layout/catalog/*.json` (un file per pezzo) | le voci fra cui scegliere: id, mestieri, attacchi |
| La tabella dei mestieri | `naming/families.json` | traduce il mestiere in parole (`heat_generation` = generatore di calore) |
| La tabella dei fluidi | `naming/media.json` | i nomi dei fluidi ammessi (`heating_water` = acqua di riscaldamento…) |
| Lo schema del modello | `schemas/project.schema.json` | la forma esatta del JSON |
| Lo strumento di validazione | comando al §8, passo 7 | dice se il file carica |

Se i file ti arrivano copiati in un'altra cartella, valgono lo stesso: contano i
contenuti, non i percorsi. Il comando di validazione è l'unica cosa che puoi eseguire
fuori dalla tua cartella di lavoro: **eseguirlo non è leggere il repository**, e non
viola l'isolamento.

---

## 3. Il file che produci

Un JSON per impianto, versione `1.1.0`, con questa forma. I campi `subsystems`,
`rule_applications` e `sheets` restano **liste vuote**: appartengono a pezzi successivi
della catena.

Ecco un esempio **completo e caricabile** — un impianto inventato, minimo apposta:
una caldaia a condensazione da 24 kW con circolatore che alimenta radiatori esistenti.
Guarda come la potenza detta dal testo compare in due posti: trascritta in
`properties`, e usata per ricavare `plant_regime` (24 kW ≤ 35, quindi piccola centrale).

```json
{
  "schema_version": "1.1.0",
  "metadata": {
    "project_id": "esempio-caldaia-radiatori",
    "client": "Committente",
    "project_name": "Caldaia a condensazione su radiatori",
    "commission_code": "ESEMPIO",
    "revision": "00",
    "issue_date": "2026-08-06"
  },
  "plant_regime": "up_to_35_kw",
  "networks": [
    {
      "id": "riscaldamento",
      "name": "Circuito di riscaldamento",
      "domain": "hydronic",
      "medium": "heating_water"
    }
  ],
  "components": [
    {
      "id": "caldaia",
      "definition_id": "gas-boiler",
      "tag": null,
      "properties": { "potenza": "24 kW" }
    },
    {
      "id": "circolatore",
      "definition_id": "pump-circulator",
      "tag": null,
      "properties": {}
    },
    {
      "id": "radiatori",
      "definition_id": "radiator",
      "tag": null,
      "properties": {}
    }
  ],
  "connections": [
    {
      "id": "p1",
      "network_id": "riscaldamento",
      "endpoint_a": { "component_id": "caldaia", "port_id": "water_supply" },
      "endpoint_b": { "component_id": "circolatore", "port_id": "a" },
      "properties": {}
    },
    {
      "id": "p2",
      "network_id": "riscaldamento",
      "endpoint_a": { "component_id": "circolatore", "port_id": "b" },
      "endpoint_b": { "component_id": "radiatori", "port_id": "in" },
      "properties": {}
    },
    {
      "id": "p3",
      "network_id": "riscaldamento",
      "endpoint_a": { "component_id": "radiatori", "port_id": "out" },
      "endpoint_b": { "component_id": "caldaia", "port_id": "water_return" },
      "properties": {}
    }
  ],
  "assumptions": [
    {
      "id": "a1",
      "text": "Il testo dice «i radiatori esistenti» senza dirne il numero: se ne e' disegnato uno, rappresentativo. Quanti sono davvero?",
      "status": "proposed"
    }
  ],
  "rule_applications": [],
  "subsystems": [],
  "sheets": []
}
```

Regole di forma:

- **Ogni `id`** (componenti, reti, tubazioni, assunzioni) è minuscolo, inizia con una
  lettera, e usa solo lettere, cifre, `_` e `-`. Scegli id parlanti in italiano:
  `pdc-1`, `volano`, `collettore-mandata`.
- **`definition_id`** è l'id esatto di un file del catalogo. Mai un id che nel catalogo
  non c'è.
- **`tag`** è la sigla del pezzo, e la compili **solo se l'ingegnere l'ha scritta nel
  testo**. Se non l'ha scritta, `tag` è `null`: le sigle le assegna dopo, in automatico,
  chi battezza il grafo. Non inventare numerazioni.
- **`properties`** dei componenti: solo i dati che il testo dà, trascritti come stanno
  (`"potenza": "12 kW"`, `"volume": "200 litri"`). Nessun dato dedotto. Ci vanno anche
  il **nome commerciale** (`"modello": "ECOcombi"`) e le **qualifiche** che il testo usa
  (`"tipo": "aria-acqua reversibile"`, `"configurazione": "a quattro tubi"`): sono
  parole dell'ingegnere, e trascriverle non costa nulla — dedurne qualcosa sì.
- **`plant_regime`**: il regime della centrale, `up_to_35_kw` oppure `over_35_kw`. Si
  ricava dalle potenze che il testo dà (§4.6). Se il testo non le dà, **ometti il
  campo** e scrivi la domanda in `assumptions`.
- **`metadata`**: identifica il documento, non l'impianto. Committente e codice di
  commessa te li dice chi lancia il lavoro; se mancano, scrivi `ND` e dillo nella
  risposta. `issue_date` è la data di oggi, `revision` è `00`. Il `project_id` lo
  costruisci dal titolo dell'impianto, minuscolo e con i trattini
  (`caldaia-radiatori-esistenti`): identifica il documento, non è una sigla di commessa.
- Il campo `evidence` che lo schema prevede puoi lasciarlo vuoto: la tracciabilità la
  dai con la tabella di rilettura (§8, passo 6). Nelle assunzioni puoi usare
  `source_message_refs` per citare la frase del testo da cui nasce la voce.

---

## 4. Cosa tirare fuori dal testo

### 4.1 Le macchine, scelte dal catalogo per mestiere

Elenca ogni macchina che il testo nomina. Per ciascuna scegli **una voce di catalogo**,
così:

1. Traduci quello che la macchina **fa** nel mestiere della tabella
   `naming/families.json`: una pompa di calore aria-acqua *genera calore* →
   `heat_generation`; un volano *accumula* → `thermal_storage`; un bollitore *accumula
   acqua sanitaria* → `dhw_storage`.
2. Cerca nel catalogo le voci che dichiarano quel mestiere nel campo `functions`.
3. Fra quelle, scegli guardando **gli attacchi** (`ports`): un accumulo che il testo
   descrive con serpentino sanitario deve avere gli attacchi del serpentino; un volano
   «a due tubi, in serie» deve avere due attacchi di flusso; il campo `stored_medium`
   dice che acqua tiene in serbo. La voce giusta è quella i cui attacchi permettono di
   scrivere **esattamente** i collegamenti che il testo descrive.
4. Mai scegliere per somiglianza di nome. Il nome può ingannare; i mestieri e gli
   attacchi no.

**Un aggettivo che dice cosa la macchina fa, cambia la voce.** «Caldaia **combinata**»,
«boiler **in pompa di calore**», «pompa di calore **reversibile**»: prima di sceglierne
una, chiediti se quell'aggettivo aggiunge un mestiere. Una macchina che produce anche
l'acqua calda sanitaria **da sola** è una voce diversa da una che fa solo
riscaldamento — cerca nel catalogo una voce che dichiari entrambi i mestieri. Se il
testo descrive **come** produce il sanitario (uno scambiatore esterno, un bollitore
separato), quei pezzi sono nel grafo e la macchina resta quella base: comanda la
descrizione, non l'aggettivo.

**Se nessuna voce combacia** — il mestiere non c'è, o gli attacchi non bastano per i
collegamenti descritti — **non ripiegare su una voce sbagliata**: quel pezzo (o quel
circuito) non si disegna, e la mancanza diventa una voce dichiarata (§6, tipo B).

### 4.2 Le reti: un circuito, un fluido

Una rete è un circuito che il testo nomina o distingue: il circuito dei generatori, il
circuito secondario che parte da un accumulo, l'acqua fredda di acquedotto, l'acqua
calda sanitaria. Ogni rete dichiara il suo fluido (`medium`), scelto fra quelli della
tabella `naming/media.json`. Il fluido cambia dove una macchina lo cambia: prima del
bollitore c'è acqua fredda (`cold_water`), dopo c'è acqua calda sanitaria
(`domestic_hot_water`); sono due reti. Il dominio è `hydronic` per tutto ciò che è
acqua.

**Dove una rete comincia — e dove no.** Una rete parte sempre da una **macchina che la
alimenta** (un generatore, un accumulo, un bollitore) oppure da un **confine**
(l'acquedotto, le utenze). **Mai da un raccordo.** I rami che si staccano da una
ripartizione **restano nella rete da cui nascono**, anche quando il testo li elenca uno
per uno: «dal volume tecnico partono tre circuiti» distingue tre **rami**, non tre reti
— nascono tutti dal volume, e il volume è la macchina che li alimenta. Sono una rete
sola, insieme al tratto che li porta.

Questo non toglie niente al testo: i tre rami restano tre, con i loro raccordi (§4.4) e
i loro pezzi. Cambia solo come si raggruppano. E serve a chi viene dopo: chi battezza le
linee legge che acqua porta una linea e da che parte va **dalla macchina che la
alimenta**, e una rete che cominciasse su un raccordo non saprebbe dire né l'una né
l'altra cosa.

Il fluido resta il secondo criterio, e vale sempre: dove il fluido cambia, la rete
cambia, anche a valle della stessa macchina.

**Il raffrescamento non ha un fluido suo** nella tabella: una macchina reversibile
d'estate manda acqua fredda negli stessi tubi, e il circuito resta uno. Dichiaralo
`heating_water` come il resto del circuito, e metti in `assumptions` che la macchina è
reversibile e che quel circuito porta anche il raffrescamento. Non inventare un fluido
che la tabella non ha.

### 4.3 Le tubazioni

Ogni tubo fra due pezzi è una voce di `connections`. Quattro regole dure:

- **Un attacco porta una tubazione sola, sempre.** Due tubi sullo stesso bocchello non
  esistono nella realtà e non esistono nel grafo: se due tubazioni devono incontrarsi,
  in mezzo c'è un raccordo (§4.4). Mai due `connections` sulla stessa coppia
  componente+attacco.
- **Il verso segue il flusso:** `endpoint_a` è la porta da cui l'acqua esce (`flow:
  "out"` nel catalogo), `endpoint_b` è la porta in cui entra (`flow: "in"`).
- **Stesso fluido alle due estremità**, ed è il fluido della rete a cui la tubazione
  appartiene.
- **Solo attacchi che il catalogo dichiara.** Mai inventare una porta. E gli attacchi
  segnati `stub: true` nel catalogo sono attacchi di servizio (sfiato, scarico, sede
  sonda): esistono perché il pezzo successivo della catena ci appenda gli accessori.
  **Tu non ci colleghi niente.**

**Un circuito chiuso si chiude.** «Un circuito con circolatore che alimenta i
radiatori» dice che l'acqua va ai radiatori **e torna**: mandata e ritorno sono la
stessa affermazione topologica, e disegnare il ritorno è trascrizione, non invenzione.
I circuiti sanitari invece sono aperti: entrano dall'acquedotto, escono alle utenze.
Per acquedotto e utenze il catalogo ha le voci di confine (mestiere `boundary`).

Dopo aver collegato, controlla gli attacchi `required: true` delle macchine scelte: uno
rimasto libero vuol dire che hai perso un collegamento descritto — o che il testo
davvero non lo dà, e allora è una domanda (§6).

### 4.4 I raccordi che la topologia impone

Dove la topologia **descritta** fa incontrare due tubazioni, ci va un pezzo che le
unisce. Non è progettazione: è l'unico modo di scrivere quello che il testo dice.

**La regola generale, che vale in tutti i casi.** Nel catalogo la confluenza è il
**raccordo a T** (due entrate, un'uscita) e la ripartizione è la **ripartizione a T**
(un'entrata, due uscite); esistono in variante per fluido, e scegli quella del fluido
della rete. Ogni raccordo ha **tre** attacchi, quindi:

> dove il testo fa incontrare **N** tubazioni in un punto, servono **N−1** raccordi in
> catena.

Vale in tutte le direzioni, e questi sono i casi che ricorrono:

- **N macchine in parallelo**: N−1 confluenze sulla mandata (i flussi si uniscono) e
  N−1 ripartizioni sul ritorno (il flusso si divide). «In parallelo» *dice* che i flussi
  si uniscono; il raccordo è la trascrizione di quella parola.
- **N circuiti che partono da un accumulo o da un punto solo**: N−1 ripartizioni sulla
  mandata e N−1 confluenze sul ritorno. È lo stesso conto, letto dall'altra parte.
- **N ritorni che rientrano sullo stesso attacco di una macchina**: N−1 confluenze prima
  dell'attacco. Un attacco porta una tubazione sola (§4.3), sempre.

**Se il testo descrive come** i flussi si uniscono o si dividono — nomina un collettore,
un separatore idraulico, un distributore — usa **quello** e cerca la voce di catalogo
corrispondente. Se dice solo «in parallelo», «dal volume partono tre circuiti», o non
dice niente, usa i raccordi **e dichiara l'assunzione** (§6, tipo A): il testo non ha
detto con che pezzo.

**Le derivazioni** (il pezzo con un braccio che esce dal percorso) si usano **solo dove
il testo descrive qualcosa che si stacca da un tubo**. Mai metterne una per comodità o
per previdenza.

**Un anello che rientra su una macchina senza l'attacco per riceverlo** (per esempio un
ricircolo «collegato» a un bollitore che, a catalogo, l'attacco del ricircolo non ce
l'ha): l'attacco non si inventa — comanda il catalogo. L'anello si chiude sul tubo, con
una ripartizione dove esce e una confluenza dove rientra, e **il punto scelto si
dichiara come assunzione**, perché il testo non l'ha detto.

### 4.5 I dati detti, e la regolazione

- Potenze, volumi, temperature: **si trascrivono solo se il testo li dà**, in
  `properties` del componente, testuali e con l'unità. Se il testo non li dà, non
  compaiono e non si deducono.
- La **logica di regolazione** — priorità sanitaria, master e slave, «la caldaia
  interviene quando…» — non è topologia: non produce nodi né tubi. Non la perdere:
  scrivi una voce in `assumptions` che dice cosa il grafo mostra e cosa no («la
  priorità è una logica di regolazione: sul grafo si vede la valvola deviatrice, non la
  priorità»).
- Le **esclusioni esplicite** — «non è previsto il ricircolo», «senza bollitore di
  accumulo» — sono informazione, non silenzio: il grafo non le mostra, quindi vanno in
  `assumptions` («il testo esclude il ricircolo: non è disegnato perché non c'è, non
  perché sia stato perso»). Servono a chi legge dopo, per non riaggiungerlo.

### 4.6 Il regime della centrale, che si ricava dalle potenze

Sotto e sopra i **35 kW** le regole del pezzo successivo cambiano, quindi il regime è un
dato del modello. **Si ricava, non si chiede:** somma le potenze delle macchine che
**generano calore** e confronta con la soglia. Il dato è dell'ingegnere, la soglia è
fissa: il conto è aritmetica, non dimensionamento.

- somma ≤ 35 kW → `"plant_regime": "up_to_35_kw"`;
- somma > 35 kW → `"plant_regime": "over_35_kw"`;
- **il testo non dà le potenze** → ometti il campo e scrivi la domanda in `assumptions`:
  *«Il testo non dà le potenze: il regime della centrale non è stato ricavato. Sotto o
  sopra i 35 kW?»*

Contano solo i generatori: accumuli, circolatori e terminali non hanno potenza di
generazione. Se il testo dà una potenza in una forma diversa (potenza resa, potenza
assorbita) trascrivila come sta e dichiara nell'assunzione quale hai sommato.

---

## 5. Cosa entra nel grafo e cosa no: le due liste

Il catalogo contiene **anche** gli accessori che il pezzo successivo della catena
aggiunge. Che una voce esista in catalogo non ti autorizza a usarla.

**Entra nel grafo di prima stesura** ciò che il testo nomina e che appartiene al corpo
dell'impianto — i mestieri:

> `heat_generation`, `thermal_storage`, `dhw_storage`, `hydraulic_separation`,
> `heat_exchange`, `circulation`, `distribution`, `emission`, `diversion`,
> `circuit_mixing`, `junction`, `branch_off`, `boundary`.

Cioè: generatori, accumuli e bollitori, separatori, scambiatori, circolatori,
collettori, terminali (radiatori, ventilconvettori, batterie, pannelli), valvole
deviatrici e miscelatrici **di circuito** a tre vie (decidono dove va il flusso: sono
topologia), i raccordi del §4.4, i confini (acquedotto, utenze).

**Non entra mai**, nemmeno se il testo lo nomina, la ferramenta di servizio — i
mestieri:

> `isolation`, `isolation_locked_open`, `non_return`, `safety`, `expansion`,
> `filtration`, `sludge_separation`, `air_release`, `filling`, `drain`,
> `pressure_control`, `pressure_measurement`, `temperature_measurement`, `dhw_mixing`.

Cioè: intercettazioni, ritegni, sicurezze, vasi, filtri, defangatori, sfiati, gruppi di
riempimento, scarichi, riduttori, manometri, termometri, e la miscelatrice
**sanitaria** sull'uscita dell'acqua calda. Li aggiunge il pezzo delle regole, che sa
dove vanno e perché. **Se il testo li nomina, la nomina non si perde:** scrivi una voce
in `assumptions` che lo dice («il testo prevede il carico automatico da acquedotto e lo
scarico sul volume: li aggiunge il pezzo che completa, non questo grafo»). Così
l'ingegnere e il pezzo successivo possono verificare che nulla è andato perso.

Se il testo nomina un mestiere che non sta in nessuna delle due liste (un ventilatore,
una linea frigorifera…), trattalo come voce di catalogo mancante: §6, tipo B.

---

## 6. Cosa non inventare mai, e come si dichiara un'ambiguità

**Mai inventare:**

- accessori, in nessun caso (§5);
- quantità e taglie non dette (quanti terminali, che diametri, che potenze);
- collegamenti che il testo non descrive;
- attacchi che il catalogo non dichiara;
- potenze, temperature, volumi, prevalenze, tarature.

**Una prescrizione non è un permesso.** Se il testo dice «l'impianto dovrebbe avere X»
o una norma lo richiederebbe, questo **non** ti autorizza ad aggiungere X: dice cosa
deve avere l'impianto, e a metterlo ci pensa l'ingegnere o il pezzo delle regole. Tu al
massimo lo annoti in `assumptions`.

Ogni cosa che il testo non dice e che serve per disegnare diventa una **voce
nell'elenco `assumptions`** del JSON, con `status: "proposed"`, scritta in italiano
piano, come domanda o come assunzione esplicita che l'ingegnere possa leggere e
approvare o respingere. Mai risolvere in silenzio. Tre tipi.

**Tipo A — il testo impone un collegamento ma non dice con che pezzo.** Il grafo deve
chiudersi, e c'è un modo minimo e convenzionale di chiuderlo: chiudi così **e
dichiara**. Il grafo esce completo, e l'ingegnere corregge il dettaglio se vuole.
Esempi (inventati apposta, non presi da nessun impianto reale):

- «una caldaia murale alimenta l'impianto esistente a termosifoni», e non dice se il
  circolatore è a bordo o esterno → si segue quello che il catalogo dichiara per la
  voce scelta + assunzione: *«Il testo non dice se il circolatore è integrato nella
  caldaia: si è seguita la macchina di catalogo, che lo porta a bordo. È così?»*;
- «due sottocentrali derivate dal collettore di piano», senza dire da quali uscite →
  ripartizioni in catena (§4.4) + assunzione: *«Il testo non dice come le due
  sottocentrali si staccano: si sono assunte due derivazioni consecutive.»*

**Tipo B — il catalogo non ha con cosa rappresentarlo.** Non disegnare niente: la parte
manca dal grafo, e una voce in `assumptions` lo dice a chiare lettere. Esempi:

- il testo nomina una macchina il cui mestiere non esiste in catalogo → la macchina non
  si disegna, e la voce nomina il mestiere che manca;
- il testo descrive un collegamento che richiederebbe un attacco che la voce scelta non
  ha, e nessun'altra voce ce l'ha → quel collegamento non si disegna, e la voce lo dice.

**Tipo C — la scelta è dell'ingegnere, e va chiesta prima.** Si chiede solo quando
valgono **tutte e tre**:

1. il testo davvero non lo dice;
2. le due strade sono **entrambe corrette** — nessuna è l'errore;
3. la scelta **cambia il disegno**, non un dettaglio.

Allora scrivi la domanda in `assumptions` e **ripetila in chiaro nella risposta**, così
chi ti ha lanciato la porta all'ingegnere. Nel frattempo chiudi il grafo con la strada
che ti pare più convenzionale, dichiarandola: un grafo incompleto è meno utile di un
grafo con una domanda sopra.

**Il criterio per distinguere A da C:** nel tipo A ogni lettura ragionevole produce lo
stesso grafo a meno di un dettaglio; nel tipo C due letture ragionevoli producono
**due grafi diversi**, e nessuna delle due è sbagliata.

**Quello che non si chiede mai:** dove va un accessorio (lo sa il pezzo delle regole),
quante taglie o diametri (sono dell'ingegnere, e se non li ha detti non compaiono), e
qualunque cosa il testo abbia già scritto — a partire dalle potenze.

---

## 7. Regole pratiche di rappresentazione

- **Un terminale rappresentativo.** «L'impianto esistente a radiatori», «i fan-coil»:
  un solo componente della famiglia giusta rappresenta l'insieme. Il numero vero non è
  detto: se il testo è plurale o vago, dichiara la domanda (tipo A).
- **Un componente descritto come integrato** in una macchina («il circolatore integrato
  nella pompa di calore») non si disegna come pezzo a sé: dichiara in `assumptions` che
  è integrato, come dice il testo.
- **Dove sta il circolatore, quando il testo non lo dice.** Se il testo lo nomina come
  pezzo a sé («un circuito con circolatore dedicato») ma non dice su quale ramo, mettilo
  sulla **mandata** del circuito che serve: è la posizione convenzionale, e va
  dichiarata come assunzione. Non è una regola dell'impianto, è una convenzione di
  disegno: perciò si dichiara.
- **Master, slave, cascata, priorità** sono regolazione (§4.5), non pezzi.
- Il testo può nominare un accessorio per dire **dove** sta un attacco («sul volume
  tecnico sono previsti il carico e lo scarico»): resta ferramenta, resta fuori, la
  nomina va in `assumptions` (§5).

---

## 8. Il metodo di lavoro, passo per passo

1. **Leggi tutto il testo, fino in fondo, prima di scrivere qualsiasi cosa.** Un
   impianto si capisce intero: l'ultima frase può cambiare la lettura della prima.
2. **Elenca le macchine nominate** e per ciascuna scegli la voce di catalogo per
   mestiere dichiarato (§4.1). Segna subito i buchi di catalogo: sono voci di tipo B.
3. **Elenca le reti** con il proprio fluido (§4.2).
4. **Collega seguendo il fluido**, dalla sorgente in avanti — dai generatori per i
   circuiti termici, dall'acquedotto per il sanitario: tubazioni da porta `out` a porta
   `in`, un tubo per attacco, raccordi dove la topologia descritta li impone (§4.3,
   §4.4).
5. **Dichiara man mano** assunzioni e punti aperti (§6). Se ti accorgi di aver deciso
   qualcosa senza una frase del testo dietro, fermati: o è un'assunzione dichiarata, o
   non va nel grafo.
6. **Rileggi il testo frase per frase** e spunta: ogni affermazione topologica del
   testo è rappresentata nel grafo (o dichiarata in `assumptions`)? E, al contrario,
   ogni componente e ogni tubazione del grafo risale a una frase precisa? Costruisci la
   **tabella di rilettura**: una riga per frase, con gli elementi del grafo che la
   rappresentano, oppure la voce di `assumptions` che la copre. Un elemento che non
   compare in nessuna riga non doveva esserci.
7. **Valida il file.** Il comando va lanciato **dalla radice del repository**, dove vive
   l'interprete Python, ma il file che gli passi può stare dove vuoi — indica il suo
   percorso per esteso. Eseguire questo comando non è leggere il repository: se lavori
   isolato, l'isolamento resta.

   ```
   .venv/bin/python -c "from pathlib import Path; from disegnatore_mep.io.project_json import load_project; load_project(Path('/percorso/completo/del/tuo/file.json'))"
   ```

   Nessun output = il file carica. Un errore nomina il campo sbagliato: correggi e
   ripeti finché carica. Un file che non carica non è una consegna.

---

## 9. Prima di consegnare: il controllo finale

Rispondi a queste domande. Se una risposta è «no», il lavoro non è finito.

- Il JSON carica con lo strumento di validazione?
- Ogni `definition_id` esiste nel catalogo, e nessuno ha un mestiere della lista
  «ferramenta» (§5)?
- Ogni attacco usato esiste nel catalogo del suo pezzo, nessun attacco porta due
  tubazioni, nessuna tubazione tocca un attacco `stub`?
- Ogni tubazione va da una porta `out` a una porta `in`, sullo stesso fluido?
- I `tag` sono solo quelli scritti dall'ingegnere, e tutti gli altri sono `null`?
- Ogni componente e ogni tubazione compare nella tabella di rilettura, agganciato a una
  frase del testo?
- Ogni cosa che il testo non dice — e che hai dovuto chiudere o lasciare fuori — è una
  voce di `assumptions`, leggibile dall'ingegnere?
- `subsystems`, `rule_applications` e `sheets` sono liste vuote?

**E le quattro cose da cui dipende tutto il resto della catena** — se una ti è rimasta
oscura, quella è la domanda da fare (tipo C):

- **Che macchina è ciascun pezzo:** produce calore? produce **anche** l'acqua calda
  sanitaria da sola? tiene una riserva, e di quale acqua? La voce di catalogo scelta
  risponde a tutte e tre, ed è per questo che si sceglie sui mestieri e sugli attacchi.
- **Che acqua porta ogni circuito**, e soprattutto: c'è o non c'è il sanitario?
- **Il regime della centrale**, ricavato dalle potenze (§4.6) o dichiarato mancante.
- **Come i circuiti toccano un serbatoio:** quale lo attraversa scambiando calore e
  quale ne riempie la riserva. Il serpentino passa dentro il bollitore, ma l'acqua del
  bollitore è quella che entra dall'alimentazione fredda.
