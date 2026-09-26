# Rapporto — «Capire» sull'Esempio 6 (centrale ibrida condominiale con solare termico)

## 1. In breve

- **Questo pezzo non produce tavole**, solo il grafo di prima stesura. Il controllo sulle
  tavole si potrà fare solo più a valle della catena.
- Consegne, nell'ordine chiesto: `grafo.json`, `rilettura.md`, `rapporto.md`, tutte nella
  cartella `capire-6b/`.
- **Validazione** (§8, passo 7), lanciata dalla radice del repository sul file della
  cartella:
  `.venv/bin/python -c "from pathlib import Path; from disegnatore_mep.io.project_json import load_project; load_project(Path('…/capire-6b/grafo.json'))"`
  → nessun output, codice di uscita 0: **il file carica.**
- **Controlli del §9**, fatti con uno script sul catalogo della cartella (esito: nessun
  errore):
  - ogni `definition_id` esiste nel catalogo;
  - le 30 tubazioni vanno tutte da una porta `out` a una porta `in`, sul fluido della
    propria rete; fanno eccezione le 3 tubazioni che collegano due attacchi bidirezionali
    sulle derivazioni solari;
  - nessun attacco porta due tubazioni;
  - nessun attacco `stub` è collegato, tranne il braccio `branch` delle tre derivazioni
    solari;
  - tutti gli attacchi `required` sono collegati;
  - la ferramenta (ritegno, sicurezza, manometro, vaso) sta solo sulla rete solare;
  - tutti i `tag` sono `null`;
  - `subsystems`, `rule_applications` e `sheets` sono liste vuote.
- **Rilettura**: uno script ha verificato che ogni id del grafo compare nella tabella e che
  le tabelle dei componenti e delle tubazioni coincidono con il JSON. Esito: 25 componenti su
  25 e 30 tubazioni su 30, nessuna discordanza.
- **Numeri del grafo:** 25 componenti, 30 tubazioni, 5 reti, 16 voci di `assumptions`.
  Regime `over_35_kw`.
- **Metadati:** li ha dati chi ha lanciato il lavoro, nessun campo `ND`:
  - committente «Nove C — prova»;
  - commessa «PROVA-REL-003»;
  - revisione «00»;
  - data 2026-09-26;
  - `project_id` «prova-6-centrale-ibrida-solare».

  Il §3 dice di costruire il `project_id` dal titolo, ma qui l'identificativo era dato
  esplicitamente e ho usato quello. Il `project_name` è il titolo del testo.

## 2. L'impianto come è stato letto

- **Circuito primario** (`heating_water`), nasce dai generatori:
  - la pompa di calore di alta potenza (120 kW) e la caldaia modulare (150 kW), in
    parallelo, si uniscono su un raccordo a T;
  - la mandata comune passa per la valvola deviatrice a tre vie: la via `out_a` va al
    volume tecnico a quattro tubi, la via `out_b` al serpentino superiore del bollitore;
  - il ritorno del volume e quello del serpentino confluiscono in un raccordo a T, poi una
    ripartizione a T li riporta ai due generatori.
- **Circuito secondario** (`heating_water`), nasce dal volume tecnico:
  - una ripartizione a T apre due rami, radiatori e fan-coil canalizzati, ciascuno con il
    proprio circolatore sulla mandata;
  - un raccordo a T riporta i due ritorni al volume.
- **Circuito solare** (`solar_fluid`), nasce dal collettore:
  - la mandata va al serpentino inferiore;
  - sul ritorno ai collettori, nell'ordine: circolatore, ritegno, e poi tre derivazioni a T
    da cui pendono la valvola di sicurezza, il manometro e il vaso di espansione solare.
- **Acqua fredda** (`cold_water`): dal confine di alimentazione all'ingresso freddo del
  bollitore.
- **ACS** (`domestic_hot_water`): dall'uscita del bollitore al confine delle utenze.
- **Regime**: 120 + 150 = 270 kW, cioè più di 35 kW, quindi `over_35_kw`.

## 3. Le voci di catalogo scelte, e perché

| Macchina del testo | Mestiere | Voce scelta | Perché | Scartate, e perché |
|---|---|---|---|---|
| «pompa di calore aria-acqua di alta potenza da 120 kW» | `heat_generation` | `heat-pump-air-water-large` | Il testo nomina la variante: «alta potenza» è in `variant.named_as`. Gli attacchi `water_supply`/`water_return` bastano per il parallelo. La voce ha il circolatore a bordo, quindi non ne ho disegnato uno a sé. | `heat-pump-air-water`: è la voce base, ma il testo nomina la variante. `dhw-heat-pump`: produce ACS da sola, e il testo non lo dice. |
| «caldaia modulare a condensazione da 150 kW» | `heat_generation` | `gas-boiler-modular` | Il testo nomina la variante: «modulare» è in `variant.named_as`. Stessi attacchi della caldaia base, circolatore a bordo. | `gas-boiler`: è la voce base, e il testo nomina la variante. Nessuna voce «combinata»: la caldaia non è detta combinata, e l'ACS il testo la fa produrre al serpentino del bollitore. |
| «volume tecnico da 1000 litri a quattro tubi» | `thermal_storage` | `buffer-four-port` | Ha quattro attacchi di flusso (`primary_in`/`primary_out` verso i generatori, `secondary_out`/`secondary_in` verso i circuiti secondari): esattamente i collegamenti descritti da F3 e F5. `stored_medium` è l'acqua di riscaldamento. | `buffer-two-port`: ha due soli attacchi. `buffer-combined`: ha anche `cold_in`/`dhw_out`, cioè fa ACS, e il testo la fa fare al bollitore separato. |
| «bollitore a doppio serpentino da 1500 litri» | `dhw_storage` | `dhw-cylinder-twin-coil` | È l'unica voce con gli attacchi del serpentino solare (`solar_coil_in`/`solar_coil_out`) oltre a quelli del serpentino dei generatori (`coil_in`/`coil_out`). | `dhw-cylinder`: ha un solo serpentino, e il solare non si potrebbe collegare. `dhw-heat-pump`: genera calore da sola. |
| «valvola a tre vie sulla mandata [che] devia il flusso verso il bollitore» | `diversion` | `diverting-valve-3way` | Un ingresso (`in`) dalla mandata comune e due uscite (`out_a` al volume, `out_b` al serpentino): è la topologia del verbo «devia». | `switching-valve-3way` (`circuit_switching`): due ingressi e un'uscita, la topologia rovescia. `mixing-valve-3way`: miscela, non devia. |
| «ciascuno con il proprio circolatore» (due circuiti secondari) | `circulation` | `pump-circulator` ×2 | Circolatore per acqua di riscaldamento, uno per ramo. | `pump-circulator-dhw` e `pump-circulator-solar`: portano altri fluidi. |
| «radiatori degli appartamenti» | `emission` | `radiator` | Terminale rappresentativo, attacchi `in`/`out`. | — |
| «fan-coil canalizzati degli spazi comuni al piano terra» | `emission` | `fan-coil-ducted` | Il testo nomina la variante: «canalizzati» è la forma declinata di «canalizzato», che è in `variant.named_as`. | `fan-coil`: è la voce base, e il testo nomina la variante. |
| «campo di collettori solari termici» | `heat_generation` | `solar-collector` | Generatore sul fluido solare, con attacchi `supply`/`return`. | — |
| Gruppo di circolazione solare (F11) | `circulation`, `non_return`, `safety`, `pressure_measurement`, `expansion` | `pump-circulator-solar`, `valve-check-solar`, `valve-safety-solar`, `pressure-gauge-solar`, `expansion-connection-solar`; i tre pezzi appesi pendono ciascuno da una `tee-branch-solar` | Sono le voci con `medium: solar_fluid`. Il §4.2 ammette la ferramenta solo sulla rete solare, e solo se il testo la nomina: qui la nomina. | Le voci omonime su altri fluidi. |
| «in parallelo», «partono due circuiti», ritorno del serpentino | `junction` | `tee-junction` ×3 (confluenze), `tee-split` ×2 (ripartizioni) | Sono i raccordi del §4.4, nella variante per acqua di riscaldamento: N−1 raccordi per N tubazioni che si incontrano. | `zone-manifold`: il testo non nomina un collettore. |
| Acqua fredda che entra, ACS prelevata | `boundary` | `cold-water-inlet`, `dhw-draw-off` | Sono i confini delle due reti sanitarie aperte. | `dhw-recirculation-inlet`: il ricircolo è escluso dal testo (F14). |

Tre cose nominate dal testo non sono nel grafo perché sono ferramenta (§5), e la nomina è
riportata in `assumptions`: il carico automatico da acquedotto (`filling`) e lo scarico
(`drain`) sul volume tecnico, e la valvola miscelatrice termostatica sull'uscita dell'ACS
(`dhw_mixing`).

## 4. Domande e assunzioni, in chiaro

**Nessuna domanda di tipo C.** Nessun punto ammette due letture entrambe corrette che
producano due grafi diversi. Ci sono tre voci che chiedono conferma all'ingegnere e vanno
portate a lui:

1. **`a-ritorno-serpentino`.** Il testo dice dove il circuito del serpentino superiore si
   stacca (la deviatrice sulla mandata), non dove il suo ritorno rientra. L'ho unito, con un
   raccordo a T, al ritorno del volume verso i generatori, prima della ripartizione sui due
   generatori. Non c'era altra strada: i generatori hanno un solo ritorno ciascuno e il
   volume non ha attacchi liberi. *È il punto giusto?*
2. **`a-gruppo-solare-mancanti`.** Del gruppo solare ho disegnato solo i pezzi nominati.
   Non sono disegnati termometri, intercettazioni, sfogo dell'aria e attacchi di carico e
   scarico del solare: sulla rete solare nessun pezzo successivo li aggiunge. *Vanno
   aggiunti?*
3. **`a-circolatori-generatori`.** Il testo non dice se i generatori hanno il circolatore a
   bordo. Ho seguito le voci di catalogo, che lo portano integrato, e sul primario non c'è
   nessun circolatore a sé. *È così?*

Tutte le 16 voci di `assumptions`, in chiaro (stato `proposed`):

| Id | Tipo | Che cosa dice |
|---|---|---|
| `a-regime` | regime (§4.6) | 120 kW + 150 kW = 270 kW > 35 kW, quindi `over_35_kw`. Ho sommato le potenze come il testo le scrive, senza sapere se sono nominali, rese o al focolare. Il campo solare non ha potenza nel testo e non è sommato. Nessuna delle due precisazioni può riportare la somma sotto i 35 kW. |
| `a-circolatori-generatori` | A | Circolatore a bordo dei due generatori, come dicono le voci di catalogo. *È così?* |
| `a-parallelo` | A | «In parallelo» senza il pezzo: raccordo a T sulla mandata comune, ripartizione a T sul ritorno comune. La pompa di calore, nominata per prima, sta sul braccio laterale di entrambi, la caldaia sul passante. |
| `a-regolazione-generatori` | regolazione (§4.5) | Pompa di calore principale e caldaia in integrazione sono regolazione: il grafo mostra il parallelo, non la precedenza. |
| `a-carico-scarico-volume` | ferramenta nominata (§5, §7) | Carico automatico da acquedotto e scarico sul volume: li aggiunge il pezzo che completa il grafo. Per la stessa ragione non è disegnata nemmeno l'acqua di acquedotto che alimenta il carico. |
| `a-circuiti-secondari` | A | «Partono due circuiti» senza il pezzo: ripartizione a T in mandata, raccordo a T in ritorno. Sono due rami di una rete sola, che nasce dal volume. Radiatori sul braccio laterale, fan-coil sul passante; mandata e ritorno si specchiano. |
| `a-circolatori-secondari` | A (convenzione del §7) | Ogni circolatore è sulla mandata del proprio ramo, fra la ripartizione e i terminali. |
| `a-radiatori` | A | Il numero dei radiatori non è detto: ne è disegnato uno, rappresentativo. |
| `a-fancoil` | A | Il numero dei fan-coil canalizzati non è detto: ne è disegnato uno, rappresentativo. |
| `a-priorita-acs` | regolazione (§4.5) | La priorità ACS non si vede; si vede la deviatrice sulla mandata comune. `out_a` va al volume e `out_b` al bollitore: è un dettaglio che il testo non dà. |
| `a-ritorno-serpentino` | A (§4.4, l'anello che rientra senza attacco) | Il ritorno del serpentino superiore confluisce nel ritorno del volume prima della ripartizione sui generatori. *È il punto giusto?* |
| `a-collettori-solari` | A | Il campo di collettori è disegnato con un solo collettore, rappresentativo. |
| `a-gruppo-solare-posizione` | A (convenzione del §4.2) | Il gruppo sta sul ritorno ai collettori, nell'ordine del testo e nel verso del flusso: circolatore, ritegno, sicurezza, manometro, vaso. Sicurezza e vaso restano così dal lato dei collettori rispetto al ritegno. |
| `a-gruppo-solare-mancanti` | domanda (§4.2) | Termometri, intercettazioni, sfogo e carico/scarico del solare non sono nominati e non sono disegnati. *Vanno aggiunti?* |
| `a-miscelatrice` | ferramenta nominata (§5) | La miscelatrice termostatica sull'uscita dell'ACS la aggiunge il pezzo che completa il grafo. Qui l'ACS va diretta alle utenze. |
| `a-no-ricircolo` | esclusione esplicita (§4.5) | Il ricircolo non è disegnato perché il testo lo esclude, non perché sia stato perso. L'attacco `recirculation_in` del bollitore resta libero. |

## 5. Dove le istruzioni non mi hanno dato un criterio

Non ho inventato regole. Dove mancava un criterio ho preso la strada più piana e l'ho
dichiarata:

1. **Ordine sui raccordi quando il raccordo è uno solo.** Il §4.4 dice l'ordine delle
   utenze o delle macchine lungo una catena di raccordi. Con due elementi il raccordo è
   uno, e le istruzioni non dicono quale va sul braccio laterale `c` e quale sul passante.
   Ho usato una regola sola ovunque: il primo nominato sul braccio laterale, l'ultimo in
   fondo al passante. Mandata e ritorno si specchiano (pompa di calore e radiatori sul
   braccio, caldaia e fan-coil sul passante).
2. **Le due uscite della deviatrice.** Il catalogo le chiama «primo ramo» e «secondo
   ramo» senza altro significato. Ho mandato `out_a` al volume (la destinazione descritta
   per prima) e `out_b` al bollitore, e l'ho dichiarato in `a-priorita-acs`.
3. **Ordine dei pezzi dentro il gruppo solare.** Il §4.2 dice dove sta il gruppo (sul
   ritorno ai collettori), non in che ordine stanno i pezzi. Ho seguito l'ordine in cui il
   testo li elenca, nel verso del flusso, e l'ho dichiarato.
4. **Gruppo solare descritto solo in parte.** Il §4.2 copre il gruppo descritto
   (trascrivilo) e quello non descritto (non inventarlo, chiedi). Non copre un gruppo di
   cui il testo nomina solo alcuni pezzi. Ho trascritto i pezzi nominati e chiesto degli
   altri (`a-gruppo-solare-mancanti`).
5. **Verso di una tubazione fra due attacchi bidirezionali.** È il caso del braccio della
   derivazione solare e del pezzo appeso: la regola «da `out` a `in`» lì non si applica.
   Ho messo come `endpoint_a` la derivazione. Il validatore lo accetta, ma è una mia
   scelta, non una regola.
6. **Potenze date solo per alcuni generatori.** Il §4.6 prevede due casi: il testo dà le
   potenze, oppure non le dà. Qui manca la potenza del campo solare, che pure è un
   generatore. Il regime si ricava lo stesso solo perché le due potenze note superano già
   i 35 kW. Se la loro somma fosse stata sotto soglia, il regime non sarebbe stato
   ricavabile, e le istruzioni non dicono che cosa fare in quel caso.
7. **Un'osservazione, fuori da questo impianto.** Il catalogo ha voci con mestieri che
   non stanno in nessuna delle due liste del §5: `circuit_switching` (valvola commutatrice),
   `instrument_isolation` (rubinetto portamanometro), `air_separation` (separatore d'aria).
   Alla lettera del §5 andrebbero trattate come voci mancanti (tipo B) anche se esistono.
   Qui non ha pesato, perché nessuna delle tre serve.

## 6. Che cosa il testo non dice e io non ho dedotto

- **Reversibilità e raffrescamento.** Il testo non dice che la pompa di calore è
  reversibile né che i fan-coil raffrescano. Le reti sono dichiarate `heating_water` e
  nessuna assunzione parla di raffrescamento, perché il testo non lo nomina.
- **Quantità.** Il testo non dice il numero di moduli della caldaia, né quanti collettori,
  radiatori e fan-coil ci sono.
- **Grandezze di progetto.** Il testo non dà diametri, temperature, prevalenze o tarature,
  né la potenza del campo solare. Nessuno di questi dati compare nel grafo.
- **ACS centralizzata.** L'ho trascritta come `"produzione": "centralizzata"` sul
  bollitore, perché il testo lo dice (F8). Non è una deduzione dai litri.

## 7. Da guardare quando ci sarà la tavola

- **Posizioni sul bollitore.** Il grafo non scrive «alto» e «basso». Scrive quale
  serpentino è collegato a che cosa: i generatori su `coil_*`, il solare su `solar_coil_*`,
  l'acqua fredda su `cold_in`, l'ACS su `dhw_out`. Il testo mette il serpentino dei
  generatori in alto e quello solare in basso, l'acqua fredda in basso e il prelievo ACS
  in alto. Se in tavola il serpentino solare risultasse in alto, il simbolo contraddirebbe
  il testo anche con il grafo corretto.
- **L'acqua fredda che il grafo non porta.** La rete dell'acqua fredda del grafo porta
  solo al bollitore. La miscelatrice termostatica (ingresso freddo) e il carico automatico
  da acquedotto avranno bisogno dell'acqua fredda: deve portarla il pezzo che completa il
  grafo.

## 8. Isolamento

**Non l'ho violato.**

- Ho letto soltanto i file della cartella `capire-6b/`: `ISTRUZIONI.md`, `testo.md`,
  `catalogo/`, `nomi/`, `project.schema.json`.
- Fuori dalla cartella ho eseguito soltanto il comando di validazione prescritto, dalla
  radice del repository.
- Non ho aperto la cartella `capire-6/` né file del repository.
- Niente commit, niente push, nessuna azione su GitHub.

Due fatti da dichiarare per trasparenza. Nessuno dei due è una lettura mia:

- **Il `CLAUDE.md` del repository** mi è stato messo nel contesto dall'ambiente, all'avvio,
  senza che lo aprissi. Non ho seguito il suo rinvio a leggere altri documenti del
  repository.
- **Un output troppo lungo salvato fuori cartella.** L'ambiente ha salvato automaticamente
  in un file fuori cartella (sotto `/root/.claude/projects/…/tool-results/`) l'output
  troppo lungo di un mio comando: la stampa integrale del catalogo della mia cartella. Non
  ho aperto quel file. Ho invece ristampato il catalogo in forma compatta, leggendolo dalla
  cartella.
