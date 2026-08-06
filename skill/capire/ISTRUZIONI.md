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
contenuti, non i percorsi.

---

## 3. Il file che produci

Un JSON per impianto, versione `1.1.0`, con questa forma. I campi `subsystems`,
`rule_applications` e `sheets` restano **liste vuote**: appartengono a pezzi successivi
della catena.

Ecco un esempio **completo e caricabile** — un impianto inventato, minimo apposta:
una caldaia a condensazione con circolatore che alimenta radiatori esistenti.

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
  (`"potenza": "12 kW"`, `"volume": "200 litri"`). Nessun dato dedotto.
- **`metadata`**: identifica il documento, non l'impianto. Committente e codice di
  commessa te li dice chi lancia il lavoro; se mancano, scrivi `ND` e dillo nella
  risposta. `issue_date` è la data di oggi, `revision` è `00`.
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

- **Due macchine in parallelo** esigono una **confluenza** sulla mandata (due tubi
  diventano uno) e una **ripartizione** sul ritorno (uno si sdoppia su due). «In
  parallelo» *dice* che i flussi si uniscono; il raccordo è la trascrizione di quella
  parola.
- **Tre macchine in parallelo** esigono due confluenze in catena sulla mandata e due
  ripartizioni sul ritorno: i raccordi di catalogo hanno tre attacchi, e con N macchine
  ne servono N−1 per lato.
- Nel catalogo: la confluenza è il **raccordo a T** (due entrate, un'uscita), la
  ripartizione è la **ripartizione a T** (un'entrata, due uscite). Esistono in variante
  per fluido: scegli quella del fluido della rete.
- Se il testo **descrive come** le macchine si uniscono (un collettore, un separatore),
  usa quello. Se dice solo «in parallelo», usa i raccordi **e dichiara l'assunzione**
  (§6, tipo A): il testo non ha detto come si uniscono.

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
approvare o respingere. Mai risolvere in silenzio. Due tipi:

**Tipo A — il testo impone un collegamento ma non dice come.** Il grafo deve chiudersi,
e c'è un solo modo minimo e convenzionale di chiuderlo: chiudi così **e dichiara**.
Esempi:

- «due macchine in parallelo», senza dire come si uniscono → raccordi (§4.4) +
  assunzione: *«Il testo dice che le due macchine sono in parallelo e non dice come si
  uniscono: si è assunto un raccordo di mandata e uno di ritorno.»*;
- «un ricircolo collegato al bollitore», senza dire dove rientra il ritorno → chiusura
  sul tubo (§4.4) + assunzione: *«Il ritorno del ricircolo è innestato sulla mandata
  sanitaria: il testo dice solo che il ricircolo è collegato al bollitore. Va bene
  lì?»*;
- «più circuiti ambiente», senza numero → il minimo che rappresenta la pluralità (uno
  per uscita del collettore scelto, o un terminale rappresentativo per circuito) +
  assunzione con la domanda: quanti sono davvero?

**Tipo B — rappresentare richiederebbe progettare, o il catalogo non ha la voce.**
Non disegnare niente: la parte manca dal grafo, e una voce in `assumptions` lo dice a
chiare lettere. Esempi:

- il testo chiede tre circuiti secondari e il collettore disponibile a catalogo ne
  serve due → il terzo circuito **non si disegna**, e la voce dice: *«Il testo elenca
  tre circuiti secondari; il collettore disponibile ne serve due: il terzo non è
  disegnato, ed è una domanda per il progettista.»*;
- il testo nomina una macchina che il catalogo non ha → la macchina non si disegna, e
  la voce nomina il mestiere che manca.

Il criterio per distinguere: nel tipo A **ogni** lettura ragionevole del testo produce
lo stesso grafo a meno di un dettaglio da confermare; nel tipo B servirebbe una
decisione che spetta all'ingegnere. Nel dubbio, tipo B: meglio una domanda in più che
un'invenzione.

---

## 7. Regole pratiche di rappresentazione

- **Un terminale rappresentativo.** «L'impianto esistente a radiatori», «i fan-coil»:
  un solo componente della famiglia giusta rappresenta l'insieme. Il numero vero non è
  detto: se il testo è plurale o vago, dichiara la domanda (tipo A).
- **Un componente descritto come integrato** in una macchina («il circolatore integrato
  nella pompa di calore») non si disegna come pezzo a sé: dichiara in `assumptions` che
  è integrato, come dice il testo.
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
7. **Valida il file** con lo strumento del repository, dalla radice del repository:

   ```
   .venv/bin/python -c "from pathlib import Path; from disegnatore_mep.io.project_json import load_project; load_project(Path('percorso/del/tuo/file.json'))"
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
