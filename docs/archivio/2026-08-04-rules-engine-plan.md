# Piano P1 — Motore delle regole e prima libreria idronica

**Data:** 4 agosto 2026
**Stato:** **eseguito** il 4 agosto 2026. Il corpo dei task è stato scritto prima e non riscritto: in caso di divergenza fa fede l'appendice.
**Fase:** P1 della roadmap master. Segue P0 (fondazione), P2 (grafica) e P4 (layout).

---

## 0. Decisioni di prodotto

Tutte già chiuse. Il piano non ne apre di nuove.

| Decisione | Cosa fissa |
|---|---|
| §9 della specifica | Cosa dichiara una regola: identificativo, versione, dominio, condizione, fatti richiesti, proposta, posizione funzionale, categoria, motivazione, fonte, vincolo grafico, criterio di verifica |
| §9.1 | Gerarchia delle fonti: norma, prescrizione del produttore, buona pratica documentata, convenzione interna |
| §9.2 | **Limite di autorità**: il motore non trasforma una proposta in progetto approvato |
| D-039 | `RuleApplicationModel` esiste per la tracciabilità a valle e va finalmente scritto |
| **D-066** | La skill non diventa un manuale di progettazione. Il contenuto viene dalla buona pratica; la fonte dichiarata deve dire il vero; non si acquistano norme che non sbloccano nulla |
| ADR 0002, D-026 | Il modello tecnico è la fonte di verità. Le regole lo completano prima del disegno, non dopo |

Il perimetro del primo pacchetto è stato concordato col PM il 4 agosto 2026: **sette
famiglie** — sicurezza, intercettazione, protezione, aria, riempimento e scarico, misura, e
**acqua calda sanitaria**. Bastano a completare il caso di accettazione D-011 e non fanno un
manuale. Tutto il resto — aeraulico, regolazione, bilanciamento, contabilizzazione — è in
`docs/DEFERRED.md` §1.

L'ACS è stata riportata dentro dal PM subito dopo la prima stesura, ed è la scelta giusta:
il caso di accettazione **ha un bollitore**. Lasciare fuori i suoi accessori avrebbe
significato generare un impianto completo su metà tavola e lasciare l'altra metà nuda, che
è precisamente il difetto che P1 esiste per chiudere.

---

## 1. Obiettivo

Oggi il caso di prova è **scritto a mano** e ha dieci componenti: nessun vaso di
espansione, nessun gruppo di riempimento, nessuna valvola di sicurezza, nessuno sfiato.
Finché il modello non li genera, ogni giudizio sulla tavola giudica un impianto che non
esiste, e il foglio resta mezzo vuoto perché non c'è niente da disegnarci.

Al termine di P1 il progetto deve saper prendere una topologia essenziale — quella che
l'ingegnere ha davvero deciso — e proporre le integrazioni che la rendono un impianto,
ciascuna con la propria motivazione, categoria e fonte, **senza toccare il modello finché
qualcuno non approva**.

### Cosa P1 non fa

- **Non dimensiona.** Nessuna regola calcola un volume, una portata o un diametro. Una
  regola dice *quale componente serve e dove*; quanto sia grande lo dice l'ingegnere, e
  finché non lo dice resta `DA DEFINIRE` su una bozza.
- **Non seleziona apparecchiature principali.** Generatori, accumuli e circolatori sono
  scelte dell'ingegnere (§3 della specifica).
- **Non modifica il modello di propria iniziativa.** Produce proposte; l'applicazione è un
  passo separato ed esplicito.

---

## 2. Cosa è stato scoperto prototipando

Il metodo che ha funzionato per il piano di layout: prototipare le parti a rischio
**prima** di scrivere il piano. Fatto anche qui, e ha già prodotto tre risultati. Tutti
**verificati** eseguendo, non dedotti.

### 2.1 Inserire un accessorio in linea spezza la connessione, e le tratte reggono

**Verificato.** Inserito un `valve-isolation` sulla connessione `p1` del caso D-011:

    prima: 10 componenti, 13 connessioni
    dopo:  11 componenti, 14 connessioni
    tratta: ('p1-a', 'p1-b')  accessori: ('valve-isolation-p1',)
            da hp.water_supply a dv.in

La connessione `p1` diventa `p1-a` e `p1-b`, e `build_trunks` ricompone la tratta
originaria con l'accessorio sopra. Nessuna modifica al pacchetto di layout: il meccanismo
che serve esiste già ed è quello di W4. L'applicazione è **ripetibile byte per byte**.

### 2.2 Una regola senza cardinalità dichiarata propone lo stesso pezzo più volte

**Verificato, ed è un difetto di progetto trovato prima di scrivere il codice.** La regola
«un circuito chiuso con generatore e senza vaso di espansione ne vuole uno» è uscita
**due volte**:

    -> expansion-on-closed-circuit: expansion-vessel in linea su p5 (a monte di hp)
    -> expansion-on-closed-circuit: expansion-vessel in linea su p7 (a monte di hp)

perché la pompa di calore ha due connessioni entranti. Un vaso di espansione è **uno per
circuito**, non uno per attacco. Ogni regola deve quindi dichiarare la propria
**cardinalità**: una volta per rete, una per componente ancorante, o una per connessione.
Senza, il motore riempie lo schema di doppioni e nessuno se ne accorge finché non lo
guarda. Diventa un campo obbligatorio dello schema (Task 1) e una prova del motore (Task 5).

### 2.3 Senza criterio di soddisfazione il motore non è idempotente

Rieseguire le regole su un modello **già completato** ripropone tutto da capo, perché
nulla dice a una regola come riconoscere ciò che ha già inserito. Il criterio va
dichiarato per regola e va scritto **in termini di funzioni**, non di identificativi:
«questa rete ha già un componente di funzione `expansion`» — non «esiste `vaso-01`».

È lo stesso vincolo del §3.1 qui sotto, e vale la pena dirlo due volte.

### 2.4 La guardia contro gli schemi tipo funziona

**Verificato.** Le condizioni scritte come dato non hanno nominato nessun componente né
nessuna definizione del progetto:

    expansion-on-closed-circuit      nomina componenti nel `when`: nessuno
    strainer-upstream-of-pump        nomina componenti nel `when`: nessuno

È la proprietà su cui poggia tutto il prodotto, e il motore delle regole è esattamente il
posto dove si romperebbe. Diventa una prova automatica (Task 3).

---

## 3. Vincoli da non violare

### 3.1 Una regola non può nominare un componente

Le condizioni parlano di **funzioni di catalogo**, domini, media e forme topologiche. Mai
di identificativi di componente né di definizione, in nessun campo valutato.

Il motivo è il differenziale del prodotto: il gate G0 ha dimostrato che il nucleo è
compositivo cercando ogni termine impiantistico nel sorgente e trovando solo i nomi di
dominio. Una regola che dicesse «se c'è una pompa di calore metti una valvola deviatrice»
riporterebbe dentro un catalogo di schemi tipo dalla porta di servizio.

Il campo `then.definition_id` è l'unica eccezione, ed è per costruzione: una proposta deve
pur dire cosa propone. Ma è un **esito**, non una condizione, e la prova lo distingue.

### 3.2 Una regola è dato, non codice

Vive in un file, ha una versione, si cambia senza toccare il motore. È il requisito che il
PM ha posto per poter migliorare le regole «dandogli in pasto documenti o normativa nuova
o un manuale specifico» (`docs/DEFERRED.md` §2). Se aggiungere una regola richiede di
modificare `engine.py`, il motore è sbagliato.

### 3.3 Il motore non modifica il modello

`evaluate` è una funzione pura: modello + catalogo + regole → proposte. L'applicazione è
un passo separato che prende **solo le proposte approvate**. Nessun percorso di codice
scrive nel modello senza passare da lì (§9.2).

### 3.4 Determinismo

Stesso modello, stesso catalogo, stesso pacchetto di regole → stesse proposte, nello
stesso ordine, con gli stessi identificativi generati. Gli identificativi si derivano dai
dati — definizione più ancoraggio, come `expansion-vessel-p5` — mai da un contatore, o
rieseguire produrrebbe un modello diverso.

### 3.5 La posizione è topologica

«Sul ritorno del generatore» si dichiara come *la connessione entrante nella porta di
flusso `in` del componente di funzione `heat_generation`*. Mai in millimetri: il modello
tecnico non contiene coordinate (D-026), e la posizione sulla tavola la decide il layout.

---

## 4. I task

Ogni task: file toccati, test da scrivere **prima**, comandi di verifica, commit. La suite
completa e `mypy src tests examples` girano a ogni task, mai il solo file del task in corso.

---

### Task 1 — Lo schema di una regola

**File:** `src/disegnatore_mep/rules/__init__.py`, `rules/schema.py`, `rules/errors.py`

`RuleDefinition`, modello Pydantic stretto, con i campi che §9 impone:

| Campo | Tipo | Note |
|---|---|---|
| `id` | `str` | `ID_PATTERN` |
| `version` | `str` | semver, come il catalogo |
| `name` | `str` | italiano, è ciò che l'ingegnere legge (D-051) |
| `domain` | `Domain` | dominio di applicazione |
| `category` | `IntegrationCategory` | necessaria, raccomandata, condizionata |
| `cardinality` | `RuleCardinality` | **per rete, per componente, per connessione** (§2.2) |
| `when` | `RuleCondition` | condizione di attivazione |
| `then` | `RuleProposalTemplate` | cosa propone e dove |
| `satisfied_by` | `SatisfactionCriterion` | come riconoscere che c'è già (§2.3) |
| `rationale` | `str` | la motivazione che finisce nel dossier |
| `source` | `str` | la fonte, che deve dire il vero (D-066) |

`RuleError` in `rules/errors.py`, sul modello di `CatalogError`: un pacchetto separato ha
il proprio errore, e non lo importa da un altro.

**Test prima:** un file di regola valido si carica; una versione non semver è rifiutata;
una categoria sconosciuta è rifiutata; un campo in più è rifiutato (i modelli sono
stretti); manca `cardinality` → errore che la nomina.

**Verifica:** `.venv/bin/python -m pytest tests/rules/test_schema.py -q`
**Commit:** `feat: lo schema di una regola, con la cardinalita' fra i campi obbligatori`

---

### Task 2 — Il registro delle regole

**File:** `src/disegnatore_mep/rules/registry.py`

`RuleRegistry.from_directory(path)`, sul modello di `ComponentRegistry`: carica un
pacchetto di regole da una cartella, ordine deterministico per identificativo, rifiuta
duplicati e file malformati nominando il file colpevole.

Verifica incrociata col catalogo, opzionale come `--symbols` sulla CLI `validate`: le
funzioni citate da una regola devono esistere in almeno una definizione, e la
`definition_id` proposta deve esistere. Una regola che propone un componente che il
catalogo non ha è un errore di caricamento, non una sorpresa a metà valutazione.

**Test prima:** una cartella con due regole carica in ordine; identificativi duplicati
falliscono nominando entrambi i file; una `definition_id` inesistente fallisce; una
funzione mai dichiarata in catalogo fallisce; una cartella vuota dà un registro vuoto,
non un errore.

**Verifica:** `.venv/bin/python -m pytest tests/rules/test_registry.py -q`
**Commit:** `feat: il registro delle regole, verificato contro il catalogo`

---

### Task 3 — Il linguaggio delle condizioni, e la guardia

**File:** `src/disegnatore_mep/rules/conditions.py`

Insieme **chiuso** di predicati, ciascuno un campo di `RuleCondition`:

- `network_domain` — la rete è di questo dominio;
- `network_medium` — e porta questo fluido;
- `network_has_function` / `network_lacks_function` — la rete contiene, o non contiene, un
  componente con questa funzione di catalogo;
- `component_has_function` — l'ancoraggio è un componente con questa funzione;
- `port_flow` — e l'attacco interessato ha questo verso;
- `connection_carries_function` — la connessione porta già un accessorio con questa
  funzione.

Niente espressioni, niente annidamento arbitrario, niente riferimenti a identificativi.
La combinazione è la congiunzione di ciò che è dichiarato: un linguaggio che si legge tutto
in una schermata, e che l'ingegnere può correggere senza sapere Python.

**Test prima:** ogni predicato valutato su un caso positivo e uno negativo. E soprattutto
**la guardia**: una prova che scandisce l'intero pacchetto di regole pubblicato e fallisce
se un campo di condizione contiene un identificativo di componente o di definizione. È il
vincolo §3.1 reso automatico, come il gate G0 lo è per il nucleo.

**Verifica:** `.venv/bin/python -m pytest tests/rules/test_conditions.py -q`
**Commit:** `feat: un linguaggio di condizioni chiuso, che non puo' nominare un componente`

---

### Task 4 — Il contesto di valutazione

**File:** `src/disegnatore_mep/rules/context.py`

`RuleContext`: vista **di sola lettura** su `ProjectModel` più `ComponentRegistry`, che
risponde ai predicati del Task 3 e nient'altro. Costruita una volta per valutazione, con
gli indici già pronti — funzioni per componente, componenti per funzione e per rete,
connessioni entranti e uscenti da un componente, accessori già in linea su una connessione.

Non espone il modello: chi valuta una condizione non deve poter leggere un identificativo,
altrimenti §3.1 resta un'intenzione invece che una proprietà.

**Test prima:** le funzioni di un componente vengono dal catalogo e non dal nome;
`network_has_function` è vero solo per le reti che il componente tocca davvero; un
componente in linea risulta sulla propria connessione; il contesto è immutabile.

**Verifica:** `.venv/bin/python -m pytest tests/rules/test_context.py -q`
**Commit:** `feat: il contesto di valutazione, che risponde solo per funzione`

---

### Task 5 — Il motore

**File:** `src/disegnatore_mep/rules/engine.py`

`evaluate(project, catalog, rules) -> list[RuleProposal]`. Funzione pura. Per ogni regola,
per ogni ancoraggio ammesso dalla propria cardinalità, se `when` è vera e `satisfied_by` è
falsa, emette una proposta.

L'ordine è quello delle regole nel registro, poi degli ancoraggi in ordine di modello:
deterministico e ispezionabile.

**Test prima:** il difetto del §2.2 non torna — la regola del vaso di espansione su un
generatore con due ritorni emette **una** proposta, non due; il motore è **idempotente**,
cioè valutare un modello già completato non produce nulla; una regola il cui `when` è
falso non emette; l'ordine è stabile fra esecuzioni e fra `PYTHONHASHSEED` diversi; il
modello in ingresso **non viene modificato**, verificato confrontando il JSON canonico
prima e dopo.

**Verifica:** `.venv/bin/python -m pytest tests/rules/test_engine.py -q`
**Commit:** `feat: il motore delle regole, idempotente e senza effetti sul modello`

---

### Task 6 — La proposta

**File:** `src/disegnatore_mep/rules/proposal.py`

`RuleProposal`: cosa si propone (`definition_id`), dove (posizione topologica del §3.5),
con quale identificativo generato, di quale categoria, con quale motivazione e fonte, e da
quale regola in quale versione.

L'identificativo si deriva dai dati: `<definition_id>-<ancoraggio>`, verificato nel
prototipo — `valve-isolation-p1`. Se collide con un identificativo esistente, si aggiunge
un discriminante ricavato dall'ancoraggio, mai un contatore.

**Test prima:** l'identificativo generato rispetta `ID_PATTERN`; è stabile fra esecuzioni;
due proposte della stessa regola su ancoraggi diversi hanno identificativi diversi; una
collisione con un componente esistente si risolve senza contatori.

**Verifica:** `.venv/bin/python -m pytest tests/rules/test_proposal.py -q`
**Commit:** `feat: la proposta, con identificativi derivati dai dati`

---

### Task 7 — L'applicazione approvata

**File:** `src/disegnatore_mep/rules/apply.py`

`apply_proposals(project, approved) -> ProjectModel`. Prende **solo** le proposte
approvate e restituisce un modello nuovo:

- aggiunge il componente;
- se è in linea, spezza la connessione in `<id>-a` e `<id>-b` (§2.1);
- scrive un `RuleApplicationModel` per ciascuna, con regola, versione, categoria, stato e
  entità toccate — il campo che D-039 aspetta da P0.

Il modello in ingresso non viene mutato. Il modello in uscita passa la validazione
topologica esistente: se non la passa, l'applicazione fallisce nominando la proposta
colpevole invece di consegnare un modello rotto.

**Test prima:** applicare zero proposte restituisce un modello identico; applicare una
proposta in linea produce le due connessioni e la tratta si ricompone (è la prova del
§2.1, portata da prototipo a test); il `RuleApplicationModel` è scritto e completo;
applicare due volte le stesse proposte dà lo stesso risultato; il modello risultante passa
`validate_project`.

**Verifica:** `.venv/bin/python -m pytest tests/rules/test_apply.py -q`
**Commit:** `feat: l'applicazione delle sole proposte approvate, con la tracciabilita' di D-039`

---

### Task 8 — Il primo pacchetto di regole idroniche

**File:** `rules/hydronic/*.json`, più le definizioni di catalogo mancanti in
`examples/layout/catalog/`

Le sei famiglie concordate. Indicativamente:

| Famiglia | Regole |
|---|---|
| Sicurezza | vaso di espansione sul circuito chiuso; valvola di sicurezza sul generatore |
| Intercettazione | sezionamento sugli attacchi dei componenti sostituibili |
| Protezione | filtro a monte del circolatore; defangatore sul ritorno al generatore |
| Aria | sfiato nei punti alti; disaeratore sulla mandata del generatore |
| Riempimento e scarico | gruppo di riempimento sul ritorno; scarico ai punti bassi |
| Misura | termometro e manometro sugli attacchi del generatore |
| Acqua calda sanitaria | gruppo di sicurezza sull'ingresso acqua fredda — ritegno, valvola di sicurezza sanitaria, riduttore di pressione; vaso di espansione sanitario; miscelatrice termostatica sull'uscita ACS; ricircolo con pompa e ritegno, **condizionato** |

Ogni regola porta `rationale` e `source` veri. La maggior parte sarà «buona pratica
tecnica documentata» con riferimento Caleffi (SRC-008); dove si applica la Raccolta R
(SRC-012) si cita il capitolo puntuale — per esempio R.3.B.1 per l'elenco dei dispositivi
obbligatori di un impianto a vaso chiuso. **Nessuna attribuzione gonfiata** (D-047, D-066).

Il catalogo va completato con le definizioni che oggi mancano: `expansion-vessel`,
`air-vent`, `valve-check` hanno già il simbolo in `assets/symbols/` e servono solo le voci
di catalogo con funzioni e porte.

Per l'ACS mancano invece **anche i simboli**, e vanno disegnati con
`examples/graphics/build_symbols.py` seguendo la gerarchia dimensionale di D-055 e le
tavole UNI 9511 di SRC-015: miscelatrice termostatica, valvola di sicurezza, riduttore di
pressione. È lavoro di libreria dentro un piano di regole, quindi va tenuto separato in un
proprio commit e non mescolato alle regole.

Il ricircolo ACS è l'unica regola **condizionata** del pacchetto: su un
monofamiliare non serve, su un edificio con lunghe distribuzioni sì. È anche il caso di
prova naturale per la terza categoria di `IntegrationCategory`, che altrimenti resterebbe
senza un esempio reale.

**Test prima:** ogni regola del pacchetto carica e supera la guardia del Task 3; ogni
`source` è non vuota e, se cita una norma, quella norma è nel registro fonti con stato
«acquisita»; le sei famiglie sono tutte rappresentate.

**Verifica:** `.venv/bin/python -m pytest tests/rules/test_library.py -q`
**Commit:** `feat: il primo pacchetto di regole idroniche, sei famiglie`

---

### Task 9 — Il report delle integrazioni

**File:** `src/disegnatore_mep/rules/report.py`

`IntegrationReport`: le proposte raggruppate per categoria, ciascuna con cosa, dove, perché
e da quale regola. È il materiale del dossier di approvazione (§5.3): la skill lo
presenterà, il nucleo lo produce.

Diagnostica in italiano, perché è ciò che l'ingegnere legge (D-051).

**Test prima:** le tre categorie compaiono separate; una proposta senza motivazione non è
rappresentabile; l'ordine è deterministico; il report serializza in JSON canonico stabile.

**Verifica:** `.venv/bin/python -m pytest tests/rules/test_report.py -q`
**Commit:** `feat: il report delle integrazioni, che e' il materiale del dossier`

---

### Task 10 — Il comando `rules`

**File:** `src/disegnatore_mep/cli.py`

    disegnatore-mep rules <progetto> --catalog <dir> --rules <dir>
    disegnatore-mep rules <progetto> --catalog <dir> --rules <dir> --apply-all --out <file>

Senza `--apply-all` stampa il report e non tocca niente. Con `--apply-all` scrive il
modello completato: è la scorciatoia per lo sviluppo e per il caso di accettazione, e
**non è l'approvazione** — quella vive nella conversazione (§5.3), e il flag lo dice nella
propria descrizione.

Codici di uscita coerenti col resto: `0` fatto, `2` errori bloccanti, `1` errori di
caricamento.

**Test prima:** il comando senza `--apply-all` non scrive nulla; con `--apply-all` scrive
un modello che si ricarica e valida; un pacchetto di regole malformato esce con `1` e la
diagnostica nomina il file.

**Verifica:** `.venv/bin/python -m pytest tests/test_cli.py -q`
**Commit:** `feat: il comando rules, che propone e non applica`

---

### Task 11 — Il caso D-011, completo

**File:** `examples/layout/heat-pump-dhw-buffer-two-zones.json` (essenziale, invariato),
nuovo `examples/rules/heat-pump-dhw-buffer-two-zones-completo.json` generato

Si esegue il pacchetto sul caso essenziale, si applica tutto, e si disegna il risultato.
È il primo impianto del progetto che **non è stato scritto a mano**.

Da qui si misura cosa succede alla tavola quando il contenuto raddoppia: pieghe,
attraversamenti, sovrapposizioni e riempimento del foglio. `tests/layout/test_objective.py`
guadagna il caso completo accanto a quello essenziale, con le proprie soglie.

**Test prima:** il caso completo si genera, si valida, si disegna; nessuna sovrapposizione
longitudinale oltre gli imbocchi (D-062); il fingerprint del modello completo è stabile fra
esecuzioni e fra `PYTHONHASHSEED` diversi.

**Verifica:**
```
.venv/bin/python -m disegnatore_mep rules examples/layout/heat-pump-dhw-buffer-two-zones.json \
  --catalog examples/layout/catalog --rules rules/hydronic --apply-all \
  --out examples/rules/heat-pump-dhw-buffer-two-zones-completo.json
.venv/bin/python -m disegnatore_mep draw examples/rules/heat-pump-dhw-buffer-two-zones-completo.json \
  --catalog examples/layout/catalog --symbols assets/symbols --out outputs/
```
**Commit:** `feat: il caso D-011 completo, generato dalle regole e disegnato`

---

### Task 12 — Il gate G1 e i documenti

**File:** `tests/rules/test_gate.py`, `PROJECT_STATE.md`, `docs/archivio/ARCHITECTURE.md`,
`docs/DECISION_LOG.md`, `docs/DEFERRED.md`, appendice di questo piano

Il gate che la roadmap master dichiara per P1: **le stesse regole producono risultati
motivati su varianti topologiche e non modificano il modello senza approvazione.**

Tre varianti dello stesso impianto, che condividono zero identificativi: pompa di calore,
caldaia, e caldaia più accumulo. Le stesse regole devono produrre proposte coerenti su
tutte e tre, ciascuna con la propria motivazione, e nessuna deve produrre un componente il
cui identificativo compaia nel sorgente del motore.

Poi i documenti: promuovere in `ARCHITECTURE.md` il pacchetto `rules/`, aggiornare il
backlog, cancellare da `DEFERRED.md` §6 la riga di `RuleApplicationModel`, e scrivere
l'appendice di questo piano con i difetti trovati eseguendo.

**Verifica:** `.venv/bin/python -m pytest -q && .venv/bin/ruff check . && .venv/bin/mypy src tests examples`
**Commit:** `feat: gate G1 superato su tre varianti topologiche`

---

## 5. Gate di uscita di P1

1. Le stesse regole producono risultati motivati su tre varianti topologiche che non
   condividono identificativi.
2. Nessuna regola nomina un componente o una definizione in una condizione, e una prova
   automatica lo presidia.
3. Il motore non modifica il modello: verificato confrontando il JSON canonico.
4. Ogni proposta porta categoria, motivazione e fonte, e la fonte dice il vero.
5. Il caso D-011 completo è generato dalle regole, non scritto a mano, e si disegna.
6. Suite completa verde, `ruff` e `mypy --strict` a exit `0` su `src`, `tests` ed
   `examples`.

---

## Appendice — Difetti trovati eseguendo

Sette, oltre ai due già trovati prototipando (§2.2 e §2.3). Tutti in codice scritto
durante questa esecuzione, tutti trovati da un test o dal disegno che si rifiutava di
uscire.

**1. Una regola per componente si accontenta di un accessorio sul pezzo.** Il criterio di
soddisfazione guardava il singolo attacco, quindi l'intercettazione del volano veniva
riproposta a ogni passata: la valvola era finita sull'attacco primario, e quello
secondario risultava scoperto. Per una regola *per componente* basta che il pezzo sia
servito da qualche parte.

**2. Un componente servito su una rete è servito e basta.** Il volano sta sul primario e
sul secondario. La seconda passata non registrava chi era già a posto, perché non aveva
proposto nulla per lui, e sulla rete successiva ricominciava.

**3. Il criterio di soddisfazione guardava solo il vicino.** Dopo tre applicazioni una
tubazione porta parecchi accessori in fila: lo scarico già posato due pezzi più in là non
veniva visto. Ora si cammina lungo la fila.

**4. Il verso di una connessione non si sceglie.** Va sempre da una porta che esce a una
che entra. Orientare l'accessorio rispetto all'ancoraggio produceva connessioni fra due
uscite, e il validatore topologico le respingeva — correttamente.

**5. Un accessorio senza sottosistema non sta su nessuna tavola.** Il layout lo rifiuta
invece di farlo sparire in silenzio, con una diagnostica che li elencava tutti e diciotto.
Ora un accessorio entra nel gruppo funzionale del pezzo che serve.

**6. Un accessorio attaccato al fianco di un componente chiude un corridoio.** La valvola
di sicurezza della pompa di calore si è posata a due millimetri e mezzo dal suo bordo, e
fra i due non è rimasta una sola colonna libera: il ritorno del primario non aveva più da
dove scendere, e l'instradamento è fallito con una diagnostica che parlava di tutt'altro.
Da qui `END_CLEARANCE_MM`, distinto dalla distanza fra due accessori: fra due accessori
basta che si distinguano, contro un componente serve una colonna libera.

**7. L'ingresso freddo sul fondo di un accumulo è irraggiungibile.** Un attacco sulla
faccia inferiore di un bollitore appoggiato a terra vorrebbe una tubazione che passa sotto
la linea di terra. Spostato sul fianco, in basso, che è anche come lo disegna un tecnico.

### Cosa è cambiato rispetto al piano

- **Il posizionamento ha dovuto imparare a fare spazio.** Il piano non lo prevedeva: gli
  stacchi fra colonne e fra fasce sono ora dimensionati sugli accessori che quelle tratte
  porteranno, e chi prosegue nella fascia successiva si posa per ultimo. Senza, la tratta
  che collega due fasce si ritrovava senza rettilineo e il foglio falliva dopo
  l'instradamento, quando spostare qualcosa non è più possibile.
- **Il corridoio di bordo è sceso da quattro colonne a tre.** Quattro era un numero tondo,
  non una misura.
- **Le valvole di intercettazione sono una per componente, non una per attacco.**
  Sezionare ogni attacco è corretto e raddoppia gli accessori: registrato in
  `docs/DEFERRED.md` §6.
- **Il caso completo non entra su una A3 sola** e si divide in due tavole, che è quello che
  D-056 prevede. L'unico taglio possibile è fra la distribuzione e le zone, perché una
  tratta che attraversa un confine non può portare accessori: anche questo è in `DEFERRED`.
- **Il caso essenziale di P1 è un file nuovo**, non quello del piano di layout. Mutare la
  fixture di un'altra fase avrebbe fatto cadere tredici prove che non c'entravano nulla.
