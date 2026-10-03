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
      "properties": { "power_kw": 24 }
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
- **`properties`** dei componenti: solo i dati che il testo dà. Nessun dato dedotto.
  **Sette dati hanno un nome fisso**, perché li legge la tabella delle apparecchiature
  che la tavola porta in alto a sinistra (§4.5) e il calcolo dei diametri (§4.7):

  | dato | chiave | come si scrive |
  |---|---|---|
  | potenza termica | `power_kw` | un numero, in kW: `"power_kw": 12` |
  | volume | `volume_l` | un numero, in litri: `"volume_l": 500` |
  | portata | `flow_rate_m3h` | un numero, in m³/h: `"flow_rate_m3h": 2.5` |
  | prevalenza | `head_kpa` oppure `head_m` | un numero, in kPa o in metri di colonna d'acqua, **nell'unità del testo** |
  | salto termico di progetto | `delta_t_k` | un numero, in kelvin: `"delta_t_k": 5` (§4.7) |
  | marca | `marca` | il testo com'è scritto |
  | modello | `modello` | il testo com'è scritto: `"modello": "ECOcombi"` |

  Il numero va col punto decimale (`2.5`) e senza unità: l'unità è nel nome, e il file
  non carica se in `power_kw` scrivi `"12 kW"`. Si cambia unità solo quando il cambio è
  **esatto** — «1,5 m³» di accumulo sono `"volume_l": 1500`, «800 l/h» sono
  `"flow_rate_m3h": 0.8` —, mai con un coefficiente: per questo la prevalenza ha due
  chiavi, e si usa quella dell'unità che il testo dà. **Marca e modello non si scelgono e
  non si propongono**: sono un dato del progettista, e se il testo non li dà non ci sono.
  Tutto il resto che il testo dice di un pezzo si trascrive com'è, a parole: le
  **qualifiche** (`"tipo": "aria-acqua reversibile"`, `"configurazione": "a quattro
  tubi"`), le temperature, una potenza che non è quella termica (§4.6) — sono parole
  dell'ingegnere, e trascriverle non costa nulla, dedurne qualcosa sì.
- **`plant_regime`**: il regime della centrale, `up_to_35_kw` oppure `over_35_kw`. Si
  ricava dalle potenze che il testo dà (§4.6). Se il testo non le dà, **ometti il
  campo** e scrivi la domanda in `assumptions`.
- **`diametri`**: la richiesta dei diametri delle tubazioni, **solo se il progettista li
  chiede** (§4.7): `"diametri": {"reti": ["primario"]}`, le reti su cui calcolarli. Se non
  li chiede, **ometti il campo**; se il testo non ne parla, glielo domandi in `assumptions`.
  Una rete che il testo dice **esistente** — «la distribuzione dagli accumuli in poi è
  esistente» — porta `"esistente": true` fra i suoi campi, e non sta mai fra le reti dei
  diametri.
- **`a_bordo`**, su un pezzo: le funzioni che **quella** macchina porta dentro il
  mantello, **solo se il testo lo dice** («le pompe di calore hanno il circolatore e il
  vaso a bordo»): `"a_bordo": ["expansion"]`, con i nomi dei mestieri della ferramenta
  (§5). Le regole allora non lo aggiungono fuori da quel pezzo — salvo dove lo vogliono
  comunque, come la valvola di sicurezza di ogni generatore: lo dice `completa`. Se il
  testo non lo dice, ometti il campo: quello che il modello porta dentro lo sa già il
  catalogo.
- **`esistente`**, su un pezzo o su una tubazione: c'era già, e l'intervento non lo tocca
  — «il bollitore esistente», «i collettori d'appartamento e i terminali sono esistenti»,
  «il circuito di carico si riattacca alle tubazioni esistenti che scendono al
  serpentino»: `"esistente": true`. Se una rete intera è esistente, il campo va sulla
  rete (§4.7). Si disegna come il nuovo, e la tabella non cambia: serve alle regole —
  `completa` chiede del corredo che vi posano — e ai diametri, che sull'esistente non si
  calcolano. Se il testo non lo dice, ometti il campo.
- **`accessori_tolti`**: gli accessori che le regole aggiungerebbero e che il
  progettista dice che **non ci sono** — l'impianto è costruito, o lui ha deciso così.
  Li conosci dopo `completa`, che scrive accanto a ogni accessorio il suo nome:
  `"accessori_tolti": [{"pezzo": "air-separator-tj-pr-3-b", "motivo": "non installato:
  lo sfiato è sul volano"}]`. Il motivo è suo, con le sue parole. Se il pezzo **sta
  altrove** — il vaso è sul secondario, non sul primario —, la voce dice dove con
  `"altrove": "pezzo.attacco"`, un attacco collegato della rete giusta: la regola lo posa
  lì, con quello che ne pende. Stanno nel grafo di prima stesura, e `completa` li rispetta
  a ogni rilancio (I-192).
- **`metadata`**: identifica il documento, non l'impianto, ed è quello che il
  **cartiglio** della tavola scrive. Committente e codice di
  commessa te li dice chi lancia il lavoro; se mancano, scrivi `ND` e dillo nella
  risposta. `issue_date` è la data di oggi, `revision` è `00`. Il `project_id` lo
  costruisci dal titolo dell'impianto, minuscolo e con i trattini
  (`caldaia-radiatori-esistenti`): identifica il documento, non è una sigla di commessa.
  Il cartiglio chiede altri tre dati, e li scrivi **solo se il testo o chi ti lancia li
  dà**: `address`, l'indirizzo dell'intervento — via, comune e provincia —;
  `sheet_title`, il titolo della tavola; `sheet_number`, il numero della tavola
  nell'elenco degli elaborati, come «T3». Se ne manca qualcuno **ometti il campo** e
  scrivi **una sola** voce in `assumptions` che chiede quelli che mancano, e ripetila
  nella risposta. Senza, la tavola esce in bozza con «DA DEFINIRE» nella casella, ed è
  giusto così: **non inventarli**, nemmeno il titolo. Facoltativi, e solo se dati:
  `drawn_by`, `checked_by`, `approved_by` — chi ha disegnato, verificato e approvato — e
  `header_note`, la dicitura che il cartiglio porta in testata a destra (per esempio
  «Conto Termico con sconto in fattura»). Senza, restano vuoti, e non si chiedono.
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

**Le varianti: la stessa macchina con un altro simbolo** (D-188). Alcune voci dichiarano
`variant`: fanno quello che fa la voce `variant.of`, hanno i suoi stessi attacchi, e si
disegnano con un altro simbolo — la pompa di calore di **alta potenza**, la caldaia
**modulare**, il ventilconvettore **canalizzato**. Mestieri e attacchi qui non ti aiutano,
e il nome non deve farlo. **Scegli la variante solo se il testo la nomina**, con una delle
espressioni di `variant.named_as` — «alta potenza», «grande taglia», «modulare», «a
moduli», «canalizzato», «canalizzabile» — o con la stessa parola declinata
(«modulari», «canalizzabili»). Se il testo non la nomina, la voce base, **anche per una
macchina di grande potenza**: nessuna soglia di kW decide al posto del testo. E segui
quello che la voce scelta porta a bordo: la pompa di calore di alta potenza e la
caldaia modulare hanno il **circolatore integrato** (§6, tipo A).

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

**Il circuito solare è una rete a sé, con il suo fluido**, `solar_fluid` (D-188): va dal
collettore al serpentino solare del bollitore e torna. Il collettore è un generatore;
il bollitore a due serpentini lo riconosci dagli attacchi `solar_coil_in` e
`solar_coil_out`, che solo lui ha. **Su quella rete le regole non aggiungono niente**: il
gruppo di circolazione solare — circolatore, ritegno, valvola di sicurezza, vaso,
manometro, termometri, intercettazioni — lo trascrivi tu, come il testo lo descrive,
con le voci di catalogo il cui fluido è `solar_fluid`. **Se il testo non lo descrive, non
inventarlo**: una voce in `assumptions` dice che il circuito solare è disegnato senza, e
chiede se va aggiunto. E nessun gruppo di riempimento dall'acquedotto: il circuito
solare si riempie di fluido antigelo.

Per trascriverlo valgono **due eccezioni**, e solo sulla rete solare:

- **la lista della ferramenta (§5) non vale**: ritegno, sicurezza, vaso, manometro,
  termometri, intercettazioni, sfogo dell'aria del gruppo solare entrano nel grafo, se
  il testo li nomina — nessun pezzo successivo li aggiungerebbe;
- **i pezzi che pendono da uno stacco** — sicurezza, vaso, manometro, termometro, sfogo —
  **si appendono al braccio `branch` di una derivazione a T solare** (`tee-branch-solar`),
  una derivazione per pezzo: è l'unico caso in cui colleghi un attacco di servizio (§4.3).

**Dove sta il gruppo, quando il testo non lo dice: sul ritorno ai collettori**, il lato
freddo, fra l'uscita del serpentino solare e l'ingresso del collettore. È dove lo mettono
gli schemi dei costruttori e dei progetti: circolatore e ritegno in linea, sicurezza,
manometro e vaso appesi a quella tubazione. **Sul solare la convenzione del circolatore
sulla mandata (§7) non vale.** Come ogni posizione che il testo non dice, va dichiarata
come assunzione.

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

**Il ricircolo dell'acqua calda preleva dalle utenze e torna nell'accumulo** (**D-176**).
Quando il testo dice che c'è un ricircolo sanitario, si scrive così, e in nessun altro
modo:

- entra nel grafo da un **confine di rete suo**, la voce `dhw-recirculation-inlet`: è
  l'acqua che torna dalle utenze. La sigla segue la regola di tutte le sigle (§3); sulle
  tavole del committente questo confine si legge «ACS-R»;
- attraversa **il proprio circolatore** — e quello che il testo gli dà;
- **rientra nell'accumulo di acqua calda** dal suo attacco del ricircolo,
  `recirculation_in`: il committente, «dopo il circolatore va nell'accumulo ACS (se ho
  accumulo) altrimenti idraulicamente e termicamente non ha senso».

Sta sulla **stessa rete** della mandata sanitaria: è la stessa acqua, che va alle utenze e
ne torna. **Non si chiude mai sulla mandata sanitaria** subito dopo l'accumulo, con una
ripartizione e una confluenza sullo stesso tubo: quell'anello non raggiunge le utenze, ed
è l'errore che ha prodotto la prima lettura di uno dei testi di prova. Se l'impianto **non
ha un accumulo** di acqua calda, dove il ricircolo rientri non lo dice nessuna regola: è
una domanda al progettista (§6).

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

**L'ordine non lo scegli tu: è quello del progettista, ed è lo stesso sulla mandata e sul
ritorno.** Il conto qui sopra dice *quanti* raccordi servono, non *in che ordine* le macchine
ci si attaccano — e l'ordine è una decisione di progetto:

- le utenze stanno lungo la dorsale **nell'ordine in cui il testo le elenca**; le macchine
  numerate, nell'ordine dei numeri;
- mandata e ritorno le incontrano **nello stesso ordine**, partendo dal capo del collettore:
  la prima che la mandata serve uscendo dalla sorgente è la prima che il ritorno raccoglie
  arrivando alla sorgente. Su entrambe le catene sta **sul raccordo più vicino alla
  sorgente**;
- **scrivi le due catene dal capo verso il fondo**, e controlla che si specchino. L'errore
  che questa regola chiude è nato proprio così: ciascuna catena scritta nell'ordine di
  elenco *nel verso del flusso* — la mandata dalla sorgente verso le utenze, il ritorno
  dalle utenze verso la sorgente — e il ritorno esce **rovesciato** senza che nessuno l'abbia
  deciso.

Un **ritorno inverso** (Tichelmann), **due dorsali distinte**, un ordine diverso fra mandata
e ritorno sono **scelte del progettista**. Si trascrivono **solo se il testo le dice**; se
non le dice, la distribuzione è una sola e il ritorno specchia la mandata. **Non è una
assunzione da dichiarare**: è quello che il testo dice quando non dice altro. (**D-172**, che
precisa D-087 e D-104: la skill non progetta e non trasforma il progetto che le danno.)

**Se il testo descrive come** i flussi si uniscono o si dividono — nomina un collettore,
un separatore idraulico, un distributore — usa **quello** e cerca la voce di catalogo
corrispondente. Se dice solo «in parallelo», «dal volume partono tre circuiti», o non
dice niente, usa i raccordi **e dichiara l'assunzione** (§6, tipo A): il testo non ha
detto con che pezzo.

**Le derivazioni** (il pezzo con un braccio che esce dal percorso) si usano **solo dove
il testo descrive qualcosa che si stacca da un tubo**. Mai metterne una per comodità o
per previdenza.

**Un anello che rientra su una macchina senza l'attacco per riceverlo**: l'attacco non si
inventa — comanda il catalogo. L'anello si chiude sul tubo, con una ripartizione dove esce
e una confluenza dove rientra, e **il punto scelto si dichiara come assunzione**, perché il
testo non l'ha detto. ⚠ **Non vale per il ricircolo sanitario**, che ha la sua regola
(§4.3) e gli accumuli di acqua calda l'attacco per riceverlo ce l'hanno.

### 4.5 I dati detti, e la regolazione

- Potenze, volumi, portate, prevalenze, temperature: **si trascrivono solo se il testo
  li dà**, in `properties` del componente — con le chiavi fisse di §3 quelli che le
  hanno, a parole e con l'unità gli altri. Se il testo non li dà, non compaiono e non si
  deducono.
- **La tabella delle apparecchiature.** La tavola porta in alto a sinistra una tabella
  di generatori, accumuli e bollitori, separatori, scambiatori, circolatori e vasi di
  espansione, con le loro caratteristiche, la marca e il modello. I dati vengono **solo
  dal progettista**. Per le macchine che disegni, quelli che il testo non dà — la
  potenza di generatori e scambiatori, il volume di accumuli e bollitori, portata e
  prevalenza dei circolatori, marca e modello di tutte — li chiedi in **una sola voce**
  di `assumptions`, pezzo per pezzo, e la ripeti nella risposta: *«Per la tabella delle
  apparecchiature mancano: la marca e il modello della pompa di calore; portata e
  prevalenza del circolatore. Se non li dai, sulla tavola quelle celle restano
  vuote.»* Non servono a disegnare: senza risposta la tavola esce lo stesso, con un
  trattino. **Non proporre marche né modelli**, nemmeno come esempio.
- **I vasi di espansione non li disegni tu** (§5): li aggiunge il pezzo successivo. Se il
  testo dà i dati di un vaso — volume, marca, modello —, scrivili in un'assunzione,
  vaso per vaso, perché non vadano persi: sul vaso li riporta chi completa il grafo,
  quando il progettista lo approva.
- **Come è prodotta l'acqua calda.** Se il testo dice che la produzione di acqua calda
  sanitaria è **centralizzata**, scrivilo nell'accumulo di acqua calda:
  `"produzione": "centralizzata"`. Non è un aggettivo da buttare: il pezzo che completa
  il grafo lo legge, e dove l'acqua calda è centralizzata mette il vaso di espansione
  sanitario senza chiederlo (**D-178**). Se il testo non lo dice, non lo scrivi e non lo
  deduci — né dai litri, né dalle potenze: resterà una domanda.
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
**generano calore** — i loro `power_kw` — e confronta con la soglia. Il dato è
dell'ingegnere, la soglia è fissa: il conto è aritmetica, non dimensionamento.

- somma ≤ 35 kW → `"plant_regime": "up_to_35_kw"`;
- somma > 35 kW → `"plant_regime": "over_35_kw"`;
- **il testo non dà le potenze** → ometti il campo e scrivi la domanda in `assumptions`:
  *«Il testo non dà le potenze: il regime della centrale non è stato ricavato. Sotto o
  sopra i 35 kW?»*

Contano solo i generatori: accumuli, circolatori e terminali non hanno potenza di
generazione. `power_kw` è la **potenza termica** della macchina. Se il testo le distingue
— potenza resa e potenza assorbita — in `power_kw` va la resa, e l'altra si trascrive a
parole; se il testo dà soltanto una potenza che termica non è, o non si capisce quale
sia, trascrivila a parole, non scrivere `power_kw`, e dichiara nell'assunzione che cosa
hai sommato e che cosa no.

### 4.7 I diametri, se il progettista li chiede

La tavola può portare il **diametro di ogni tratto**, calcolato — «Øi 32» lungo la linea,
il diametro interno netto minimo in millimetri (D-191, D-193). **Il calcolo è
facoltativo**: si fa **solo se il progettista lo chiede** («calcola i diametri», «metti i
DN», «dimensiona le tubazioni della centrale»), e **solo sulla parte che dice lui**.

**Se il testo non ne parla, lo chiedi** (I-185): ometti il campo e scrivi una voce di
`assumptions` che glielo domanda, con la tua prima interpretazione — la tavola esce senza
diametri — e quello che servirebbe se li vuole, così che una risposta basti: *«Diametri delle
tubazioni: il testo non li chiede, e la tavola esce senza. Se li vuoi, li calcolo su tutte le
reti nuove, e mi servono il salto termico della pompa di calore e la portata di progetto
dell'acqua calda sanitaria.»* Se risponde sì, scrivi il campo e i dati che ti dà; se risponde
no, la voce passa ad approvata. Se il testo li esclude («senza diametri»), non chiedi niente.

**Dove.** Scrivi `"diametri": {"reti": [...]}` con le reti su cui il progettista vuole il
DN. Il caso ricorrente è il **retrofit**: «la centrale è nuova, la distribuzione dagli
accumuli in poi è esistente» — il DN va sul circuito dei generatori, e le reti della
distribuzione esistente portano `"esistente": true`. Una rete esistente non si
dimensiona mai. Se il testo chiede i diametri senza dire dove, le reti sono tutte quelle
non esistenti; se non si capisce che cosa è esistente, è una domanda.

**Con quali dati.** Il calcolo non inventa niente: la portata di ogni tratto viene dai
dati del progettista, e senza quei dati quel tratto resta senza DN.

- **riscaldamento e raffrescamento**: la potenza e il salto termico di progetto del
  circuito — `power_kw` e `delta_t_k` sul **generatore**, e per un circuito di utenza sul
  **terminale** (i radiatori, i ventilconvettori, la zona a pavimento); oppure la portata
  del **circolatore** del circuito, `flow_rate_m3h`, se il testo la dà;
- **acqua fredda, acqua calda sanitaria, ricircolo e solare**: la **portata di progetto**,
  `flow_rate_m3h` — sui confini, l'acquedotto e le utenze, o sul circolatore del ricircolo
  e del solare. Qui la potenza non basta: il sanitario si dimensiona sulle utenze, e il
  fluido solare non è acqua.

Il salto termico, se il testo dà le **temperature di mandata e di ritorno** di quel
circuito, è la loro differenza: «45/40 °C» è `"delta_t_k": 5`. È aritmetica sui dati del
progettista, come il regime (§4.6). **Non scriverne uno «tipico»**: 5 K per una pompa di
calore è un'abitudine, non un dato del testo.

**Quelli che mancano li chiedi in una voce sola** di `assumptions`, pezzo per pezzo, e la
ripeti nella risposta: *«Per i diametri mancano: il salto termico della pompa di calore;
la portata di progetto dell'acqua calda sanitaria. Se non li dai, quei tratti restano
senza DN.»* Senza risposta la tavola esce lo stesso, e quei tratti non portano il
diametro.

---

## 5. Cosa entra nel grafo e cosa no: le due liste

Il catalogo contiene **anche** gli accessori che il pezzo successivo della catena
aggiunge. Che una voce esista in catalogo non ti autorizza a usarla.

**Entra nel grafo di prima stesura** ciò che il testo nomina e che appartiene al corpo
dell'impianto — i mestieri:

> `heat_generation`, `thermal_storage`, `dhw_storage`, `hydraulic_separation`,
> `heat_exchange`, `circulation`, `distribution`, `emission`, `diversion`,
> `circuit_mixing`, `junction`, `branch_off`, `boundary`, `heat_metering`.

Cioè: generatori, accumuli e bollitori, separatori, scambiatori, circolatori,
collettori, terminali (radiatori, ventilconvettori, batterie, pannelli), valvole
deviatrici e miscelatrici **di circuito** a tre vie (decidono dove va il flusso: sono
topologia), i raccordi del §4.4, i confini (acquedotto, utenze), il contatore di calore.

Le voci per **il costruito** (I-194), quando il testo le dice:

- il **contatore di calore** (`heat-meter`), in linea dove il progettista lo mette — di
  solito sul ritorno: le regole gli mettono le intercettazioni prima e dopo;
- il **collettore d'appartamento con mandata e ritorno** (`zone-manifold-pair`): ogni
  circuito esce da `out_n` e rientra in `ret_n`, e il ritorno esce da `out` — senza
  raccordi a T per richiudere i ritorni;
- il **volano a sei attacchi** (`buffer-six-port`), quando ne ha due predisposti in più
  (`aux_in`, `aux_out`);
- l'**attacco predisposto** (`capped-connection`): un tubo corto tappato su un attacco che
  oggi non serve, con la scritta che il progettista gli dà in `etichetta` («al solare
  termico»), su una rete sua;
- il **confine con l'impianto esistente** su acqua di riscaldamento
  (`existing-plant-inlet`, `existing-plant-outlet`), con la sua `etichetta` («al serpentino
  del bollitore esistente»).

`etichetta`, fra le `properties` di un pezzo, è **la scritta che la tavola porta accanto al
pezzo**, com'è scritta: solo se il progettista la dice.

**Non entra**, se il testo non la mette in un posto preciso, la ferramenta di servizio —
i mestieri:

> `isolation`, `isolation_locked_open`, `non_return`, `safety`, `expansion`,
> `filtration`, `sludge_separation`, `air_release`, `filling`, `drain`,
> `pressure_control`, `pressure_measurement`, `temperature_measurement`, `dhw_mixing`.

Cioè: intercettazioni, ritegni, sicurezze, vasi, filtri, defangatori, sfiati, gruppi di
riempimento, scarichi, riduttori, manometri, termometri, e la miscelatrice
**sanitaria** sull'uscita dell'acqua calda. Li aggiunge il pezzo delle regole, che sa
dove vanno e perché. **Se il testo li nomina senza dire dove, la nomina non si perde:**
scrivi una voce in `assumptions` che lo dice («il testo prevede il carico automatico da
acquedotto e lo scarico sul volume: li aggiunge il pezzo che completa, non questo
grafo»). Così l'ingegnere e il pezzo successivo possono verificare che nulla è andato
perso.

**Entra, se il progettista la mette in un posto preciso** (I-193): «sfiato automatico con
valvola a sfera sul ritorno di ogni pompa di calore», «ritegno sull'uscita delle pompe»,
«riduttore di pressione sull'acqua fredda», «valvole manuali sulle due uscite del
collettore». È il caso dell'impianto costruito, la cui tavola deve dire che cosa c'è. Lo
scrivi dove lui dice, con la voce del catalogo che fa quel mestiere su quel fluido:

- **in linea**, se l'acqua ci passa dentro — intercettazione, ritegno, filtro, riduttore:
  la tubazione si spezza in due, la prima entra nell'attacco `a` del pezzo e la seconda
  riparte dal suo attacco `b`, sulla stessa rete;
- **appeso**, se sta su uno stacco — sfiato, manometro, termometro, scarico: un raccordo
  di derivazione in linea (`tee-branch`, o la voce del suo fluido: `tee-branch-cold`,
  `tee-branch-dhw`), e dal suo braccio `branch` una tubazione corta al pezzo; una valvola
  sullo stacco («con valvola a sfera») sta fra il braccio e il pezzo;
- **sull'attacco di servizio** della macchina, se ce l'ha (`vent`, `drain`, `probe` di un
  volano): la tubazione corta parte da lì.

Le regole **non lo duplicano**: dove una regola vuole quel mestiere su quel tratto, lo
trova. Se ne mettono uno dove sul costruito non c'è, si toglie; se lo mettono in un posto
diverso, si sposta (`accessori_tolti`, §3). Quello che il testo nomina senza un posto
resta alle regole.

Se il testo nomina un mestiere che non sta in nessuna delle due liste (un ventilatore,
una linea frigorifera…), trattalo come voce di catalogo mancante: §6, tipo B.

---

## 6. Cosa non inventare mai, e come si dichiara un'ambiguità

**Mai inventare:**

- accessori, in nessun caso (§5);
- quantità e taglie non dette (quanti terminali, che diametri, che potenze);
- collegamenti che il testo non descrive;
- attacchi che il catalogo non dichiara;
- potenze, temperature, volumi, portate, prevalenze, tarature;
- **marche e modelli**: sono un dato del progettista, e la skill non ne ha un elenco.

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
qualunque cosa il testo abbia già scritto — a partire dalle potenze. **L'unica
eccezione sono i dati della tabella delle apparecchiature** (§4.5): si chiedono, tutti
in una voce sola, perché la tabella li scrive; chiederli non vuol dire proporli.

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
  disegno: perciò si dichiara. **Non vale sul circuito solare**, dove il gruppo sta sul
  ritorno ai collettori (§4.2).
- **Le due uscite di una deviatrice fra riscaldamento e ACS** (**D-196**). La valvola
  deviatrice a tre vie ha la **via dritta** — `in` → `out_a` — e la **terza via**,
  `out_b`. La via dritta va al **riscaldamento** — il volano, l'accumulo, la
  distribuzione —; la terza via va all'**ACS**, la serpentina del bollitore. Il testo di
  solito non lo dice, ed è questa la lettura, senza domanda: è quella dell'impianto di
  prova 2 e dello schema a tre vie del disegnatore del committente, e il committente l'ha
  confermata guardando una tavola che la rovesciava («prova 2 è quello corretto», I-175).
  Rovesciata, la tavola non si compone bene: la via dritta porta all'ACS, e la deviatrice
  non può più stare dritta sulla mandata con la terza via in basso verso il bollitore.
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
  «ferramenta» (§5) — salvo i pezzi del gruppo solare, sulla rete solare (§4.2)?
- Ogni attacco usato esiste nel catalogo del suo pezzo, nessun attacco porta due
  tubazioni, nessuna tubazione tocca un attacco `stub` — salvo il braccio delle
  derivazioni solari, da cui pendono i pezzi del gruppo (§4.2)?
- Ogni tubazione va da una porta `out` a una porta `in`, sullo stesso fluido?
- I `tag` sono solo quelli scritti dall'ingegnere, e tutti gli altri sono `null`?
- I dati con un nome fisso (§3) sono numeri nell'unità del nome, e ogni marca e ogni
  modello è scritto nel testo? I dati della tabella che il testo non dà sono chiesti in
  una voce sola (§4.5)?
- I diametri: il campo `diametri` c'è **solo se** il progettista li ha chiesti, con le reti
  che ha detto, e nessuna è `esistente`? I dati che mancano al calcolo — salti termici,
  portate di progetto — sono chiesti in una voce sola (§4.7)? Se il testo non ne parla, c'è
  la voce che gli chiede se li vuole?
- Ogni componente e ogni tubazione compare nella tabella di rilettura, agganciato a una
  frase del testo?
- Ogni cosa che il testo non dice — e che hai dovuto chiudere o lasciare fuori — è una
  voce di `assumptions`, leggibile dall'ingegnere?
- `subsystems`, `rule_applications` e `sheets` sono liste vuote?
- Ogni variante che hai scelto — alta potenza, modulare, canalizzato — il testo la
  nomina davvero (§4.1)? E il gruppo di circolazione solare, se c'è un solare, è quello
  del testo, o una domanda (§4.2)?

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
