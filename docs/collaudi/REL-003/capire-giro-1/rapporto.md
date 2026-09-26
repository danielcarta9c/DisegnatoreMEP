# Rapporto — «Capire», prova 6: centrale ibrida condominiale con solare termico

Consegne nella cartella di lavoro, nell'ordine chiesto: `grafo.json`, `rilettura.md`, questo
`rapporto.md`.

## 1. Le misure, prima del racconto

**Validazione** (dalla radice del repository, comando del §8 passo 7, con in coda un
`echo` del codice di uscita):

```
$ cd /home/user/DisegnatoreMEP && .venv/bin/python -c "from pathlib import Path; from disegnatore_mep.io.project_json import load_project; load_project(Path('/tmp/claude-0/-home-user-DisegnatoreMEP/2de6da8f-6fb3-528e-9700-9ae81466ad83/scratchpad/capire-6/grafo.json'))"; echo "exit=$?"
exit=0
```

Nessun output: **il file carica**.

**Controllo del §9, fatto con uno script che confronta `grafo.json` con `catalogo/`:**

| Controllo | Esito |
|---|---|
| Conteggi | 25 componenti, 30 tubazioni, 5 reti, 16 assunzioni |
| Ogni `definition_id` esiste nel catalogo | sì |
| Ogni attacco usato esiste nella voce del suo pezzo | sì |
| Nessun attacco porta due tubazioni | sì |
| Ogni tubazione va da `out` a `in`, con il fluido della sua rete | sì; le 3 tubazioni `q04`, `q06`, `q08` vanno da un attacco `bidirectional` a un altro `bidirectional` (braccio della derivazione → accessorio solare) |
| Nessun attacco `required: true` libero | sì; liberi solo stub (`volume-tecnico.vent/drain/probe`, `bollitore.probe`) e `bollitore.recirculation_in` (ricircolo escluso) |
| `tag` tutti `null` | sì: il testo non scrive nessuna sigla |
| `subsystems`, `rule_applications`, `sheets` vuote | sì |
| **Nessun `definition_id` con mestiere «ferramenta»** | **no, per scelta**: 4 pezzi del gruppo solare (`valve-check-solar`, `valve-safety-solar`, `pressure-gauge-solar`, `expansion-connection-solar`). Li chiede il §4.2 (D-187). Vedi §7, R2 |
| **Nessuna tubazione tocca uno stub** | **no, per scelta**: `q04`, `q06`, `q08` usano l'attacco `branch` (stub) delle tre `tee-branch-solar`. Vedi §7, R1 |
| Rilettura | ogni componente, tubazione, rete e assunzione compare nella tabella frase per frase; ogni frase del testo è citata alla lettera (verificato con uno script) |

## 2. Le macchine: voce di catalogo scelta, e perché

| Macchina nel testo | Mestiere | Voce scelta | Perché | Scartate |
|---|---|---|---|---|
| «pompa di calore aria-acqua di alta potenza da 120 kW» | `heat_generation` | `heat-pump-air-water-large` | Il testo nomina la variante: «alta potenza» è alla lettera in `variant.named_as`. Stessi attacchi della voce base (`water_supply`/`water_return`). Porta a bordo il circolatore, quindi sul primario non c'è un circolatore separato (`a02`). | `heat-pump-air-water`, perché il testo nomina la variante. `dhw-heat-pump`, perché il testo non dice che produce ACS da sola: la produce attraverso il serpentino del bollitore, che è descritto. |
| «caldaia modulare a condensazione da 150 kW» | `heat_generation` | `gas-boiler-modular` | «modulare» è in `variant.named_as`. Porta a bordo il circolatore. Il testo non dice «combinata», quindi la voce non ha il mestiere sanitario. | `gas-boiler`, perché il testo nomina la variante |
| «volume tecnico da 1000 litri a quattro tubi» | `thermal_storage` (+ `hydraulic_separation`) | `buffer-four-port` | Quattro attacchi di flusso: `primary_in`/`primary_out` dai generatori e `secondary_out`/`secondary_in` ai circuiti. Sono esattamente i collegamenti descritti. Il fluido tenuto in serbo (`stored_medium`) è `heating_water`. | `buffer-two-port`, che ha due soli attacchi e non fa «a quattro tubi». `buffer-combined`, che ha `cold_in`/`dhw_out` obbligatori: farebbe produrre ACS al volume, mentre il testo la affida al bollitore. |
| «bollitore a doppio serpentino da 1500 litri» | `dhw_storage` | `dhw-cylinder-twin-coil` | È l'unica voce con i due serpentini: `coil_in`/`coil_out` ad acqua di riscaldamento, cioè il superiore, «alimentato dai generatori», e `solar_coil_in`/`solar_coil_out` a fluido solare, cioè l'inferiore, «alimentato da un campo di collettori». Fluido tenuto in serbo: ACS. Si riempie da `cold_in`. | `dhw-cylinder` (un solo serpentino); `dhw-heat-pump` (genera calore da sé) |
| «un campo di collettori solari termici» | `heat_generation` | `solar-collector` | È l'unico generatore con attacchi a `solar_fluid` (`supply`/`return`). Un collettore rappresenta tutto il campo (`a11`). | — |
| «una valvola a tre vie sulla mandata devia il flusso» | `diversion` | `diverting-valve-3way` | Il verbo «devia» e gli attacchi: un ingresso, `out_a` verso il volume, `out_b` verso il serpentino superiore. | `mixing-valve-3way` (`circuit_mixing`, due ingressi); `switching-valve-3way` (`circuit_switching`, due ingressi e un'uscita) |
| «ciascuno con il proprio circolatore» (×2) | `circulation` | `pump-circulator` | Il circuito è ad acqua di riscaldamento. | `pump-circulator-dhw`, `pump-circulator-solar` (altri fluidi) |
| «i radiatori degli appartamenti» | `emission` | `radiator` | Un terminale rappresentativo (`a08`). | Vedi R7: fra i terminali mestiere e attacchi non distinguono |
| «i fan-coil canalizzati degli spazi comuni» | `emission` | `fan-coil-ducted` | «canalizzati» è «canalizzato» di `named_as`, declinato. Un terminale rappresentativo (`a08`). | `fan-coil`, perché il testo nomina la variante |
| Gruppo di circolazione solare: «circolatore, valvola di ritegno, valvola di sicurezza, manometro e vaso di espansione solare» | `circulation`, `non_return`, `safety`, `pressure_measurement`, `expansion` | `pump-circulator-solar`, `valve-check-solar`, `valve-safety-solar`, `pressure-gauge-solar`, `expansion-connection-solar`, più 3 × `tee-branch-solar` | Lo impone il §4.2 (D-187): il gruppo solare lo trascrivo io, come lo descrive il testo, con le voci a `solar_fluid`. Le regole su quella rete non aggiungono niente. Sicurezza, manometro e vaso hanno un solo attacco (`attachment_branch`): ciascuno sta su una propria derivazione (`a13`). | Termometri, intercettazioni, sfiato e carico/scarico solari non sono nel testo e non li ho messi (`a14`) |
| Raccordi imposti dalla topologia | `junction` | `tee-junction` ×3, `tee-split` ×2 | Le confluenze sono: le mandate dei due generatori in parallelo; il ritorno del volume con quello del serpentino; i ritorni dei due secondari. Le ripartizioni sono: il ritorno verso i due generatori; la mandata verso i due secondari. Fluido: acqua di riscaldamento. | `zone-manifold`, perché il testo non nomina un collettore |
| Acquedotto e utenze sanitarie | `boundary` | `cold-water-inlet`, `dhw-draw-off` | Sono i confini del circuito sanitario, che è aperto. | `dhw-recirculation-inlet`, perché il ricircolo è escluso |

**Nominati nel testo e lasciati fuori perché ferramenta (§5):**
- il carico automatico da acquedotto (`filling`) e lo scarico (`drain`) sul volume, in `a05`;
- la miscelatrice termostatica sull'uscita dell'ACS (`dhw_mixing`), in `a15`.

**Escluso dal testo:** il ricircolo ACS, in `a16`.

## 3. Le reti

| Rete | Fluido | Nasce da | Contenuto |
|---|---|---|---|
| `primario` | `heating_water` | i due generatori | Parallelo dei generatori, poi la deviatrice sulla mandata comune. Da lì una via va al lato primario del volume, l'altra al serpentino superiore del bollitore. Il ritorno del serpentino entra in quello del volume, poi il flusso si riparte verso i due generatori. |
| `secondario` | `heating_water` | `volume-tecnico` | Due rami, radiatori e fan-coil, ciascuno con il suo circolatore sulla mandata. È una rete sola perché i due rami nascono entrambi dal volume (§4.2). |
| `solare` | `solar_fluid` | `collettori-solari` | Andata con il gruppo di circolazione, fino al serpentino inferiore, e ritorno ai collettori. |
| `acqua-fredda` | `cold_water` | `acquedotto` | Dall'acquedotto al bollitore (`cold_in`). |
| `acs` | `domestic_hot_water` | `bollitore` | Dal bollitore (`dhw_out`) alle utenze. |

## 4. Il regime della centrale

`plant_regime` = **`over_35_kw`**: 120 kW (pompa di calore) + 150 kW (caldaia) = 270 kW,
cioè più di 35 kW. Il campo solare non ha una potenza nel testo, quindi non è sommato. Il
risultato non cambierebbe comunque (`a01`).

## 5. Le assunzioni, in chiaro (16 voci, tutte `proposed`)

1. **`a01-regime`** (dichiarazione, non domanda). Il regime è ricavato dalle potenze del
   testo: 120 kW + 150 kW = 270 kW, oltre i 35 kW. Le potenze sono sommate come il testo le
   scrive. Il campo solare è un generatore senza potenza nel testo: non è nella somma, e il
   regime non cambierebbe.
2. **`a02-circolatori-generatori`** (tipo A). Il testo non dice se pompa di calore e
   caldaia hanno il circolatore a bordo. Ho seguito le voci di catalogo, che lo portano
   integrato: sul circuito dei generatori non c'è un circolatore separato. *È così?*
3. **`a03-parallelo-generatori`** (tipo A). «Collegate in parallelo» non dice con che
   pezzo. Ho messo un raccordo a T sulla mandata comune e una ripartizione a T sul ritorno
   comune. Niente collettore né separatore idraulico, che il testo non nomina.
4. **`a04-regolazione-generatori`** (regolazione). Pompa di calore principale e caldaia di
   integrazione, che interviene quando servono più potenza o una mandata più calda, sono
   logica di regolazione. Il grafo mostra il parallelo, non la sequenza.
5. **`a05-carico-scarico-volume`** (ferramenta nominata). Il carico automatico da
   acquedotto e lo scarico sul volume tecnico li aggiunge il pezzo che completa il grafo.
   Qui non sono disegnati, ma non sono stati persi.
6. **`a06-ripartizione-secondari`** (tipo A). «Dal volume tecnico partono due circuiti
   secondari» non dice con che pezzo. Ho messo una ripartizione a T sulla mandata e un
   raccordo a T sul ritorno, senza collettore. I due circuiti sono due rami della stessa
   rete.
7. **`a07-circolatori-secondari`** (convenzione di disegno, §7). Il testo non dice su quale
   tubo stanno i circolatori dei secondari: ciascuno è sulla mandata del suo ramo, subito
   dopo la ripartizione.
8. **`a08-terminali-rappresentativi`** (tipo A). Il testo non dà il numero di radiatori e
   di fan-coil: un terminale rappresentativo per ramo. *Quanti sono davvero?*
9. **`a09-deviatrice-priorita`** (regolazione). La priorità all'ACS non si vede sul grafo.
   Si vede la deviatrice sulla mandata comune dei generatori, dopo il raccordo delle due
   mandate: `out_a` va al volume (funzionamento normale), `out_b` al serpentino superiore
   (richiesta sanitaria).
10. **`a10-ritorno-serpentino-superiore`** (tipo A). Il testo non dice dove rientra il
    ritorno del serpentino superiore. L'ho chiuso sui generatori con un raccordo a T sul
    ritorno comune, fra l'uscita del volume e la ripartizione verso i due generatori.
    *È questo il punto?*
11. **`a11-campo-solare`** (tipo A). Il testo non dice quanti collettori compongono il
    campo né come sono collegati fra loro: un collettore rappresentativo.
12. **`a12-posizione-gruppo-solare`** (**domanda**). Il testo non dice su quale tubo del
    circuito solare sta il gruppo di circolazione. Seguendo la convenzione del §7
    (circolatore sulla mandata del circuito che serve), l'ho disegnato sulla mandata, dai
    collettori verso il serpentino inferiore. I pezzi seguono il verso del flusso,
    nell'ordine del testo: circolatore, ritegno, sicurezza, manometro, vaso. Nella pratica
    il gruppo solare si monta di solito sul ritorno ai collettori, dal lato freddo.
    *Va spostato sul ritorno?*
13. **`a13-attacco-accessori-solari`** (tipo A). Sicurezza, manometro e vaso si attaccano
    al tubo, non stanno in linea, e il testo non dice come. Ciascuno sta su una propria
    derivazione a T. Le tre derivazioni sono in serie dopo il ritegno.
14. **`a14-solare-pezzi-non-descritti`** (**domanda**). Sul circuito solare le regole non
    aggiungono niente, e il gruppo ha solo i pezzi del testo. Mancano termometri,
    intercettazioni, sfiato e attacco di carico e scarico del fluido solare. *Vanno
    aggiunti?* Non c'è gruppo di riempimento da acquedotto: il solare si riempie di
    antigelo.
15. **`a15-miscelatrice-termostatica`** (ferramenta nominata). La miscelatrice termostatica
    sull'uscita dell'ACS la aggiunge il pezzo che completa il grafo. Qui non è disegnata,
    ma non è stata persa.
16. **`a16-ricircolo-escluso`** (esclusione esplicita). Il ricircolo ACS non è disegnato
    perché non c'è, non perché sia stato perso. L'attacco di ricircolo del bollitore resta
    libero.

## 6. Le domande da portare all'ingegnere

- **La più importante, perché cambia il disegno:** il gruppo di circolazione solare va
  sulla mandata dai collettori, come l'ho disegnato seguendo il §7, oppure sul ritorno ai
  collettori, come si usa di solito (`a12`)?
- Il gruppo solare ha bisogno anche di termometri, intercettazioni, sfiato e attacco di
  carico e scarico, che il testo non elenca e che nessun altro pezzo della catena
  aggiungerà (`a14`)?
- Da confermare:
  - i circolatori integrati nei generatori (`a02`);
  - quanti radiatori e quanti fan-coil ci sono (`a08`);
  - dove rientra il ritorno del serpentino superiore (`a10`).

Metadati: committente, codice di commessa, revisione, data e identificativo sono quelli
dati da chi ha lanciato il lavoro. Nessun campo è `ND`.

## 7. Dove le istruzioni non mi hanno dato un criterio, o si contraddicono

- **R1: stub e gruppo solare.** Il §4.3 e il §9 vietano di collegare qualcosa a un
  attacco `stub`. Il §4.2 (D-187) mi chiede invece di trascrivere io il gruppo solare, con
  valvola di sicurezza, manometro e vaso. Questi pezzi hanno un solo attacco
  (`attachment_branch`). L'unica voce di catalogo su cui appenderli è `tee-branch-solar`,
  e il suo `branch` è stub. Ho seguito il §4.2 e li ho collegati allo stub (`q04`, `q06`,
  `q08`). La ragione del divieto («esistono perché il pezzo successivo ci appenda gli
  accessori») sulla rete solare non vale, perché lì il pezzo successivo non aggiunge
  niente. Il divieto però è scritto senza eccezioni. **Serve una riga nelle istruzioni.**
  Ho scartato due alternative:
  - `tee-split-solar`, che non è stub, ma usa una ripartizione di flusso per un ramo
    cieco;
  - gli accessori lasciati scollegati, con l'attacco obbligatorio libero.
- **R2: §9 contro §4.2.** Il controllo «nessun `definition_id` ha un mestiere
  ferramenta» fallisce per forza quando si applica il §4.2 al gruppo solare. Poco più
  sotto il §9 chiede, in una domanda a parte, che il gruppo solare sia «quello del testo»,
  ma le due domande non sono conciliate.
- **R3: una tavola che può sembrare sbagliata con tutte le regole rispettate.** Il §7
  mette il circolatore «sulla mandata del circuito che serve». Sul circuito solare questo
  porta tutto il gruppo, compresi vaso e valvola di sicurezza, sul tubo caldo in uscita
  dai collettori. Nella pratica il gruppo solare sta sul ritorno. Le istruzioni non hanno
  un criterio per il solare. Ho applicato il §7 come è scritto, perché la convenzione di
  disegno non è mia, e ho fatto la domanda (`a12`). **Mi aspetto che la tavola risultante
  sembri sbagliata a un ingegnere.**
- **R4: l'ordine dei pezzi nel gruppo solare.** Nessun criterio. Ho usato l'ordine in cui
  il testo li elenca, nel verso del flusso, e l'ho dichiarato in `a12`.
- **R5: quale attacco del raccordo con due soli rami.** Il §4.4 dice che il primo in
  elenco sta «sul raccordo più vicino alla sorgente». Con due rami c'è un solo raccordo
  per lato, e non si dice su quale attacco. Il catalogo non dice nemmeno quale attacco del
  raccordo sia il passaggio diritto e quale il braccio. Io leggo `a`–`b` come passaggio
  diritto e `c` come braccio, per analogia con la derivazione a T (`a`, `b`, `branch`).
  Ho messo il primo in elenco sul braccio `c` su entrambi i lati, cioè la pompa di calore
  e i radiatori, e il secondo sul passaggio diritto: mandata e ritorno si specchiano. Non
  l'ho dichiarato come assunzione, perché il §4.4 dice che l'ordine non lo è. La scelta
  dell'attacco però è mia.
- **R6: le due vie della deviatrice.** Il catalogo le chiama «primo ramo» e «secondo
  ramo» senza dire quale sia la via normale. Ho messo `out_a` verso il volume e `out_b`
  verso il bollitore, e l'ho dichiarato in `a09`.
- **R7: i terminali.** Radiatore, ventilconvettore, pannello e batteria hanno lo stesso
  mestiere (`emission`) e gli stessi attacchi (`in`/`out`). Il §4.1 dice di non scegliere
  per nome, ma fra i terminali l'unico criterio è il tipo di terminale che il testo nomina.
  Ho scelto così.
- **R8: la validazione non vede il §9.** Il file carica anche con tubazioni su attacchi
  stub e con pezzi del gruppo solare, che nella lista del §5 sono ferramenta. Quindi
  «carica» non vuol dire che i controlli del §9 siano passati. Per questo li ho verificati
  a parte (§1).
- **R9: un generatore senza potenza.** Il §4.6 non dice cosa fare con un generatore di
  cui il testo non dà la potenza, qui il campo solare. Qui non conta, perché 270 kW
  bastano, ma in un impianto al limite dei 35 kW deciderebbe.
- **R10: i nomi delle proprietà.** Non c'è un elenco di chiavi ammesse. Oltre a
  `potenza`, `volume`, `tipo`, `configurazione` e `produzione` ho usato `servizio`
  («appartamenti», «spazi comuni al piano terra») per trascrivere dove servono i
  terminali.

## 8. Isolamento

**Non l'ho violato.**
- Ho letto solo i file della cartella `capire-6/`: `ISTRUZIONI.md`, `testo.md`,
  `catalogo/*.json`, `nomi/*.json` e `project.schema.json`.
- Fuori dalla cartella ho eseguito solo la validazione prescritta, sempre con in coda
  `; echo "exit=$?"`. L'ho lanciata due volte: dopo aver scritto il grafo e a consegne
  finite. Il file non era cambiato, ed entrambe le volte non c'è stato output, `exit=0`.
- Niente commit, niente push, nessuna azione su GitHub.

Due note, per trasparenza:
- Il primo `cat` dell'intero catalogo superava il limite di visualizzazione. Lo strumento
  ha salvato quell'output, cioè il contenuto dei miei file di catalogo, in un file fuori
  dalla cartella, sotto `/root/.claude/projects/…/tool-results/`. Non l'ho aperto: ho
  riletto il catalogo in forma compatta dalla mia cartella.
- All'avvio l'ambiente ha inserito nel mio contesto il `CLAUDE.md` del repository, senza
  che lo aprissi. Contiene regole di governo del progetto (pacchetti di lavoro,
  approvazione del PO), niente sull'impianto né sul catalogo. Non l'ho usato.
