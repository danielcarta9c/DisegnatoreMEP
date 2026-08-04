# Layout, instradamento e multi-tavola — piano di implementazione

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Data:** 4 agosto 2026 · **Stato:** in attesa di approvazione del PM

**Goal:** trasformare un modello tecnico approvato in una o più tavole A3 disposte, instradate e impaginate: componenti a fasce funzionali sulla griglia, tubazioni ortogonali che non passano sotto i simboli, accessori in linea che spezzano davvero la connessione, legenda a destra costruita dai soli simboli usati, rimandi accoppiati fra tavole. Il gate è visivo: un termotecnico deve riconoscere lo schema del caso D-011 come una tavola disegnata da un tecnico.

**Architecture:** il modello tecnico canonico resta la fonte di verità e non acquisisce coordinate. Da esso si deriva un **modello geometrico** separato (§7.2 della specifica): posizioni, spezzate, testi, legenda e rimandi. In mezzo si inserisce il **piano di impaginazione** (D-042): un insieme ristretto di scelte discrete — quale sottosistema su quale fascia, in che ordine, su quale tavola — che l'AI può scegliere, che vive **dentro** il modello e che il motore deterministico esegue e verifica. La catena segue l'ordine fissato dalla specifica §10.1: partizione → assegnazione dei simboli → posizionamento → instradamento → testi → rimandi → rendering.

**Tech Stack:** Python 3.12.3, Pydantic 2.13.4, SVG 1.1/2 senza dipendenze esterne, pytest 9.1.1, Ruff 0.15.22, mypy 2.3.0. Nessuna dipendenza nuova.

**Punto di partenza verificato:** 147 test verdi, `ruff` e `mypy --strict` a `0` su `src`, `tests` ed `examples`, `git status --short` vuoto, fingerprint del progetto misto `3347374e8b3f006c6f387c6228e0d9d2b885cbf57e65991937e985af32306573`.

---

## 0. Le decisioni di prodotto, tutte chiuse

**Il PM ha risposto il 4 agosto 2026 e ha confermato tutte e tre le proposte.** Nessun task è in attesa: il piano è eseguibile dal Task 1 al Task 12. Le risposte restano registrate qui perché ognuna è isolata in un solo task, quindi resta chiaro cosa toccare se una cambiasse.

| # | Domanda | Decisione del PM | Cosa cambierebbe l'alternativa |
|---|---|---|---|
| P1 | Su quale impianto si giudica il layout? | **Il caso D-011 completo.** Confermato. Il piano aggiunge i circa dieci simboli mancanti (pompa di calore, bollitore ACS, volano a quattro attacchi, valvola deviatrice, collettore di zona, terminali) e fissa la gerarchia dimensionale rimasta aperta con D-050 | Restando ai dodici simboli attuali il Task 7 sparisce, ma il gate visivo — la ragione per cui D-040 ha anticipato la grafica — resta rimandato: valvole e filtri disposti a fasce non somigliano a un impianto |
| P3 | Quando l'impianto si spezza in più tavole? | Confermato: **solo quando non entra** alla scala fissa, seguendo i confini dei sottosistemi (lettura letterale di D-020) | Con «una tavola per sottosistema» il Task 6 diventa più semplice ma anche impianti piccoli producono più fogli; con una soglia di riempimento serve un parametro in più e la soglia diventa una costante di prodotto |
| P4 | Come si distinguono le reti sulla tavola? | Confermato: **colore più tratto distinto**. ogni rete ha un colore e anche un tratto proprio, così la tavola resta leggibile fotocopiata in bianco e nero. La legenda porta una sezione fluidi oltre a quella dei simboli | Con il solo colore la sezione fluidi della legenda resta ma il tratto sparisce; in monocromatico il Task 11 perde la palette e il Task 12 acquista un controllo di distinguibilità dei soli tratti |

### P2 era una domanda mal posta, ed è chiusa

Una prima stesura di questo piano chiedeva al PM se il disegno dovesse usare la squadratura del cartiglio o conservare il margine di rilegatura ISO 5457. **Non è una decisione di prodotto: è un input che il progetto aveva già.** Il cartiglio Nove C è stato fornito nel **primo commit del progetto**, `fa7157c` del 1 agosto 2026. I margini ISO sono stati scritti in `A3_LANDSCAPE` il 3 agosto, due giorni dopo, e il piano grafico non nomina il cartiglio **nemmeno una volta**.

La squadratura del foglio, quindi, non si sceglie: si legge dal cartiglio che il PM ha consegnato. Il Task 4 la applica senza chiedere nulla.

Vale la pena vedere che errore è, perché il progetto lo ha già commesso una volta e se n'era accorto. Il campo `source` dei dodici simboli dichiarava ANSI/ASHRAE 134, che il registro fonti elenca «da acquisire e valutare»: attribuzione falsa, corretta da D-047. I margini fanno la stessa cosa con ISO 5457, che il registro elenca **tuttora** «da acquisire e valutare» (SRC-001): una geometria di carta motivata da una norma mai ottenuta, mentre lo standard aziendale reale era sul disco. Stesso schema, stessa fase, questa volta non intercettato dalle revisioni.

**Decisioni da registrare nel `DECISION_LOG`**, con i numeri liberi successivi, nel task che le applica:

- **D-053** — la squadratura della tavola è quella del cartiglio Nove C fornito, e ritira il margine di rilegatura ISO 5457 (Task 4). Non deriva da P2: deriva dall'input.
- **D-054** — le porte dei simboli cadono su nodi di griglia; è un requisito dell'instradamento, non un'estetica (Task 7, §2.2).
- **D-055** — la gerarchia dimensionale dei simboli, che chiude D-050 (P1, Task 7).
- **D-056** — regola di divisione multi-tavola (P3, Task 6).
- **D-057** — codifica delle reti su carta: colore e tratto (P4, Task 11).

---

## 1. Vincoli globali

- I comandi sono Bash e l'interprete è `.venv/bin/python`. Su Windows in locale il percorso è `.venv/Scripts/python.exe`; `scripts/setup-env.sh` rileva quale dei due esiste.
- Il modello tecnico canonico resta la fonte di verità e **non contiene coordinate**. La geometria è un modello derivato e rigenerabile (D-026, ADR 0002).
- **L'AI non assegna coordinate** (D-042). Sceglie il piano di impaginazione, che è un insieme ristretto di scelte discrete registrate nel modello; il motore le esegue e le verifica.
- Nessun simbolo, testo o spessore viene ridotto in funzione della complessità. Se non entra, si fallisce con una diagnostica che dice di quanto (D-045, ADR 0003, specifica §10.2).
- Un componente in linea **spezza la connessione** e non viene sovrapposto a una linea continua (D-027).
- Nella funzione di costo **l'incrocio è economico e il percorso lungo è carissimo** (D-041). Un instradatore che vieta l'incrocio produce il difetto che D-041 esiste per evitare.
- Nel corpo del disegno **nessuna didascalia ripete la legenda** (D-052). Tutto ciò che si legge è in italiano (D-051).
- Nessun file contiene una funzione dedicata a uno schema tipo. Nessun ramo logico su un nome di componente.
- Ogni identificativo segue `^[a-z][a-z0-9_-]*$`; le versioni seguono SemVer; tutti i modelli rifiutano campi sconosciuti.
- Nessun valore dimensionale resta un numero anonimo: `graphics/standard.py` è l'autorità sulla carta, ogni altro modulo nomina le proprie costanti (D-046).
- `releases/` non viene modificata.
- Ogni task segue red-green-refactor e termina con un commit autonomo.
- **Eseguire sempre la suite completa** e `mypy src tests examples`, mai il solo file di test del task in corso.

---

## 2. Le tre scoperte che questo piano ha fatto prima di scriversi

Il piano P0 e il piano grafico sono stati scritti senza eseguire il codice, e le loro appendici registrano rispettivamente nove e sei difetti del codice letterale. Questo piano ha invertito il metodo: le tre parti a rischio sono state prototipate e messe sotto test **prima** di essere scritte qui. Tutto ciò che segue è misurato, non supposto.

### 2.1 Il codice usa una squadratura diversa da quella del cartiglio fornito

`assets/cartigli/Cartiglio_NoveC_A3.pdf` è nel repository dal **primo commit** e nessuno lo aveva mai aperto. È stato misurato estraendone la geometria vettoriale. Il risultato:

| Elemento | Geometria misurata |
|---|---|
| Foglio | 420 × 297 mm (A3 orizzontale) |
| Squadratura | rettangolo da (10, 10) a (410, 287): **margini 10 mm sui quattro lati**, area 400 × 277 mm |
| Banda del cartiglio | fascia a tutta larghezza dal bordo inferiore della squadratura fino a 36 mm più in alto (34 mm di banda più 2 mm di filetto) |
| Intestazione | filetto a 6 mm dal bordo superiore della squadratura, largo 392 mm |
| Suddivisioni interne | montanti verticali a x = 79, 157, 257, 312, 362 mm; blocco «TAVOLA» da x = 362 a 410 |
| Campi | COMMITTENTE, INDIRIZZO, PROGETTO, TITOLO TAVOLA, SCALA, DATA, COMMESSA, REVISIONE, DISEGNATO, VERIFICATO, APPROVATO, TAVOLA |

Il corpo del disegno è quindi **400 × 235 mm**, e la sua altezza è un numero intero di passi:

```text
altezza corpo  235 mm / 2,5 = 94,000 passi  -> esatto
```

**Attenzione a non usare questo numero come argomento.** Il conto è stato rifatto con entrambi i margini, e l'altezza del corpo è 235 mm in ogni caso, perché non dipende dal margine sinistro: 94 passi esatti sia con 20 mm sia con 10 mm. Anche la larghezza cade esatta in entrambi i casi, 156 passi contro 160. **L'allineamento alla griglia non c'entra nulla**, e lo stesso vale per l'asimmetria registrata in `docs/GRAPHIC_STANDARD.md` §1.2, che riguarda `usable_height_mm` — 277 mm, 110,8 passi — e **resta tale e quale**: quel documento non va corretto su questo punto, va soltanto affiancato dalle misure del telaio.

Il punto è un altro, e non è una scelta. Il cartiglio Nove C **è già disegnato** con la propria squadratura a 10 mm e occupa i 400 mm pieni; è lo standard aziendale, consegnato dal PM come input del progetto. `A3_LANDSCAPE` ne dichiara invece 20 a sinistra, motivandoli con ISO 5457. Tenere i 20 mm significherebbe o ridisegnare il cartiglio aziendale perché stia in 390 mm — e `assets/cartigli/README.md` prescrive che una versione derivata abbia nome distinto e provenienza documentata — oppure stampare due squadrature diverse sullo stesso foglio. Nessuna delle due è una posizione difendibile davanti a un input già fornito.

Il codice si allinea quindi al cartiglio, e questo ritira il vincolo ISO 5457 elencato al punto 4 dell'appendice del piano grafico. È un ritiro deliberato, dello stesso tipo di D-044: va registrato come D-053 e scritto in `GRAPHIC_STANDARD.md`. Il prezzo è la rilegatura — una foratura entrerebbe nel disegno — e lo paga il cartiglio aziendale, non questo piano: gli elaborati Nove C sono già impaginati così.

**Verificato:** portando `margin_left_mm` a 10.0 la suite passa 145 test su 147. I due che falliscono sono `tests/graphics/test_svg.py::test_symbol_wider_than_the_usable_area_raises_naming_both_measurements` e `tests/graphics/test_svg.py::test_scale_bar_wider_than_the_usable_area_is_rejected`: entrambi asseriscono numeri derivati dal margine da 20 mm (`390` e `90`) e vanno portati a `400` e `100`. Nessun altro test è accoppiato al margine.

### 2.2 Nessuno dei venti simboli sta sulla griglia

È il difetto più grave trovato, e non è registrato da nessuna parte. L'instradamento ortogonale lavora su nodi di griglia; una rotta può quindi terminare solo su un nodo. Ma:

```text
=== assets/symbols (passo 2,5 mm) ===
  air-diffuser        riquadro 8x8;  porta a (0,4)
  air-vent            riquadro 8x8;  porta a (4,8)
  duct-damper         riquadro 6x6;  porta a (0,3); porta b (6,3)
  expansion-vessel    riquadro 6x10; porta a (3,0)
  ... tutti e dodici, e tutti e otto quelli di fixture ...
  -> simboli allineati alla griglia: 0 su 20
```

Nessun riquadro e **nessuna porta** cade su un nodo: 3 mm sono 1,2 passi, 4 mm sono 1,6. Un instradatore su griglia non può raggiungere una sola porta della libreria attuale. Le vie d'uscita sono tre: instradare fuori griglia, e allora l'allineamento richiesto dalla specifica §10.2 sparisce; aggiungere a ogni porta un tratto di raccordo obliquo o spezzato fino al nodo più vicino, e allora ogni attacco della tavola porta un gomito che nessun tecnico disegnerebbe; oppure dimensionare i simboli sulla griglia.

Il piano sceglie la terza. È anche l'unica coerente con D-050, che dichiara le taglie attuali «una convenzione di prova, non uno standard da ereditare», e con l'ingresso registrato dal PM: la dimensione del simbolo comunica il peso del componente. La regola precisa, da imporre con un controllo (Task 7):

> Ogni coordinata di porta di un simbolo è un multiplo del passo di griglia. Ne segue che riquadro e centratura devono esserlo: una porta centrata su un lato richiede che il lato sia un numero **pari** di passi.

Il controllo non può stare in `SymbolManifest`, che per costruzione non conosce `GraphicStandard` — la stessa ragione per cui l'area di rispetto è imposta «maggiore di zero» e non «almeno `min_clearance_mm`». Vive quindi nel pacchetto di layout, dove lo standard è noto.

### 2.3 L'invariante dell'interruzione di linea è scritto sull'asse sbagliato

`SymbolManifest.geometry_is_coherent` verifica `inline_gap_mm <= width_mm`. È corretto oggi solo perché tutti i simboli in linea sono quadrati. Un simbolo in linea largo 10 e alto 6, con le porte a sinistra e a destra e un'interruzione di 10 mm, è legittimo; ruotato di 90° diventa 6 × 10 con le porte in alto e in basso, l'interruzione resta di 10 mm — e il validatore lo rifiuta, perché confronta con la larghezza.

**Verificato:** il prototipo della rotazione fallisce esattamente lì, con `inline gap cannot exceed the symbol width`. L'interruzione va misurata **lungo l'asse che unisce le due porte opposte**: la larghezza se le porte sono a sinistra e a destra, l'altezza se sono in alto e in basso.

**Verificato:** applicando la correzione, la suite passa 145 test su 147; i due che falliscono sono `tests/graphics/test_symbol.py::test_inline_gap_cannot_exceed_the_symbol_width` e `tests/graphics/test_composite.py::test_inline_gap_wider_than_the_composite_box_is_rejected`, che asseriscono il vecchio messaggio. Entrambi continuano a rifiutare il caso che devono rifiutare: cambia solo il testo, e il nome del primo, che parla di `width`, non è più esatto.

---

## 3. Decisione strutturale di questo piano

**Il piano di impaginazione è un dato del modello, non uno stato del motore.**

D-042 dice che l'AI può scegliere quale sottosistema va su quale fascia, in che ordine si leggono le zone e dove si spezza in più tavole, e che quella scelta va registrata nel modello. Il modello P0 ha già `SheetIntentModel(id, title, subsystem_ids)`: è metà del piano di impaginazione — dice cosa sta su quale tavola, non dove sta dentro la tavola.

Questo piano completa quella struttura invece di costruirne una parallela. `SheetIntentModel` acquista le assegnazioni di fascia; nasce `BandRole`; il validatore topologico impara a verificare che il piano sia eseguibile — ogni sottosistema assegnato una volta sola, nessun riferimento pendente, nessuna tavola vuota.

**Conseguenza: è il primo cambiamento del modello dopo P0, quindi apre W2.** `schema_version` è oggi `Literal["1.0.0"]` senza percorso di migrazione, e `docs/P0_REVIEW_FINDINGS.md` §4 dice che il tema va affrontato «prima del primo cambiamento di modello, quando ancora non esistono file di progetto reali». È adesso.

**Seconda conseguenza, da mettere in conto: il fingerprint del progetto misto si muove.** `3347374e…` è l'impronta di un documento che dichiara `schema_version: "1.0.0"`. Portato a `1.1.0` cambia, ed è corretto che cambi: è un documento diverso. Il Task 3 lo ricalcola, lo registra in `PROJECT_STATE.md` e aggiunge la prova che conta davvero — un file `1.0.0` migrato in memoria e un file scritto nativamente `1.1.0` producono la **stessa** impronta.

---

## 4. Struttura dei file

```text
src/disegnatore_mep/catalog/
  resolved.py          # ResolvedComponent: semantica + geometria, la vista mancante
src/disegnatore_mep/graphics/
  symbol.py            # + rotazione; interruzione di linea sull'asse delle porte
  registry.py          # + Symbol.rotated con la trasformazione del corpo SVG
  standard.py          # margini della squadratura Nove C
  frame.py             # SheetFrame: corpo, fascia legenda, riserva del cartiglio
  sheet.py             # renderer della tavola: telaio, simboli posati, rotte, testi
src/disegnatore_mep/layout/
  __init__.py
  errors.py            # LayoutError, unico errore del pacchetto
  grid.py              # nodi, conversione mm <-> passi, allineamento dei simboli
  geometry.py          # modello geometrico derivato: posature, rotte, testi, rimandi
  plan.py              # lettura ed esecuzione del piano di impaginazione
  trunks.py            # le tratte che gli accessori in linea hanno spezzato
  partition.py         # divisione in tavole e rimandi accoppiati
  place.py             # posizionamento a fasce sulla griglia
  route.py             # instradamento ortogonale con funzione di costo
  inline.py            # accessori in linea posati sulla tratta instradata
  labels.py            # tag di valore agli ancoraggi
  legend.py            # fascia della legenda dai soli simboli usati
src/disegnatore_mep/validation/
  geometry.py          # i controlli geometrici della specifica §12.2
tests/layout/
  test_grid.py  test_geometry.py  test_plan.py  test_trunks.py
  test_partition.py  test_place.py  test_route.py  test_inline.py
  test_labels.py  test_legend.py
tests/graphics/
  test_rotation.py  test_frame.py  test_sheet.py
tests/catalog/
  test_resolved.py
tests/model/
  test_schema_migration.py  test_pagination_plan.py
tests/validation/
  test_geometry.py
tests/acceptance/
  test_drawing.py      # il gate: il caso D-011 disegnato end-to-end
examples/layout/
  heat-pump-dhw-buffer-two-zones.json
  catalog/             # definizioni di componente del caso D-011
  build_layout_fixtures.py
```

Modificati: `src/disegnatore_mep/model/project.py`, `src/disegnatore_mep/model/types.py`, `src/disegnatore_mep/io/project_json.py`, `src/disegnatore_mep/io/canonical.py`, `src/disegnatore_mep/catalog/registry.py`, `src/disegnatore_mep/cli.py`, `examples/graphics/build_symbols.py`, `examples/foundation/build_fixtures.py`, `schemas/project.schema.json`, `docs/GRAPHIC_STANDARD.md`, `docs/ARCHITECTURE.md`, `docs/DECISION_LOG.md`, `PROJECT_STATE.md`, e i test elencati nei singoli task.

## 5. Contratti pubblici prodotti dal piano

- `ResolvedComponent`, con `.definition`, `.symbol`, `.port(port_id)`, `.is_inline`; `ComponentRegistry.resolve(definition_id)`.
- `SymbolManifest.rotated(degrees)`, `Symbol.rotated(degrees)`, `PortFace.rotated`, `KeepOut.rotated`.
- `BandRole`, `BandAssignment`, `SheetIntentModel.band_assignments`; `SCHEMA_VERSION`, `migrate_project_document`.
- `SheetFrame`, con `body_rect_mm`, `drawing_rect_mm`, `legend_rect_mm`, `title_block_rect_mm`, `header_rect_mm`; istanza `NOVE_C_A3`.
- `GridSpace`, con `to_cell`, `to_mm`, `assert_symbol_is_aligned`.
- `Trunk`, `build_trunks`.
- `SheetPartition`, `partition_project`, `SheetLink`.
- `PlacedSymbol`, `RoutedTrunk`, `PlacedLabel`, `LegendEntry`, `SheetGeometry`, `DrawingGeometry`, `drawing_fingerprint`.
- `place_sheet`, `route_sheet`, `validate_drawing_geometry`.
- `render_sheet(sheet_geometry, frame)`; CLI: comando `draw`.

---

### Task 1: `ResolvedComponent`, la vista che unisce semantica e geometria

Il piano grafico la elencava fra i propri contratti e non l'ha costruita, perché non aveva consumatori (appendice, difetto 4). Oggi la verifica incrociata dimostra che i due insiemi di porte coincidono e poi **butta via l'accoppiamento**: non esiste modo supportato di passare da un componente alla sua geometria. Il consumatore ora c'è: tutto il resto di questo piano.

**Files:**
- Create: `src/disegnatore_mep/catalog/resolved.py`
- Create: `tests/catalog/test_resolved.py`
- Modify: `src/disegnatore_mep/catalog/registry.py`

**Interfaces:** produce `ResolvedPort`, `ResolvedComponent`, `ComponentRegistry.resolve`.

- [ ] **Step 1: scrivere il test che fallisce**

`tests/catalog/test_resolved.py` copre:

1. `resolve` di una definizione di fondazione restituisce un `ResolvedComponent` i cui `port_ids` coincidono con quelli della definizione e con quelli del manifesto;
2. `resolved.port("water_supply")` restituisce **entrambe** le facce del dato: `.definition.flow` semantico e `.geometry.face` geometrica;
3. una porta inesistente solleva `CatalogError`, non `KeyError` (è il difetto R3 del piano grafico, da non ripetere);
4. `resolve` su un registro costruito **senza** `SymbolRegistry` solleva `CatalogError` con un messaggio che dice come rimediare, invece di restituire `None`;
5. `.is_inline` è vero per un componente il cui simbolo dichiara `inline_gap_mm`, falso altrimenti;
6. `.box_mm` restituisce larghezza e altezza del riquadro del simbolo;
7. `resolve` è coerente con la verifica incrociata: dopo un caricamento riuscito, per **ogni** definizione del catalogo di fondazione `resolve` non solleva;
8. un `ResolvedComponent` costruito a mano con insiemi di porte discordi è respinto, così l'invariante non dipende solo dal registro.

- [ ] **Step 2: verificare il fallimento**

```bash
.venv/bin/python -m pytest tests/catalog/test_resolved.py -v
```

Expected: FAIL con `ModuleNotFoundError: No module named 'disegnatore_mep.catalog.resolved'`.

- [ ] **Step 3: implementare**

`resolved.py` definisce due dataclass frozen. `ResolvedPort` tiene `definition: PortDefinition` e `geometry: SymbolPort`. `ResolvedComponent` tiene `definition: ComponentDefinition` e `symbol: Symbol`, e nel `__post_init__` riasserisce che `definition.port_ids == symbol.manifest.port_ids`, sollevando `CatalogError` — il validatore riasserisce l'invariante invece di fidarsi del costruttore (D-037).

`ComponentRegistry` conserva il `SymbolRegistry` ricevuto e aggiunge `resolve(definition_id) -> ResolvedComponent`. Se è stato costruito senza simboli, `resolve` solleva `CatalogError("the catalog was loaded without a symbol library: pass symbols= to from_directory")`. Il parametro resta opzionale: il validatore topologico lavora sulla sola semantica e non deve pretendere la libreria (vincolo 3 dell'appendice grafica).

Attenzione all'import: `catalog/registry.py` importa già `graphics.registry`; `resolved.py` deve importare da `graphics.registry` e da `catalog.schema`, mai il contrario, o si ricrea l'import circolare che P0 ha pagato al Task 5.

- [ ] **Step 4: verificare**

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check src tests examples
.venv/bin/python -m mypy src tests examples
```

Expected: exit `0`; il totale sale da 147 a circa 155.

- [ ] **Step 5: commit**

```bash
git add src/disegnatore_mep/catalog tests/catalog/test_resolved.py
git commit -m "feat: join a component's semantics to its geometry"
```

---

### Task 2: La rotazione vive nel manifesto

D-049 dichiara gli orientamenti tecnicamente ammessi ma nulla ruota un simbolo. Se ogni consumatore si scrive la propria trasformazione, l'invariante perimetro-faccia diverge subito: una porta `left` ruotata di 90° non è più a sinistra. La trasformazione va accanto al validatore che impone l'invariante.

**Files:**
- Modify: `src/disegnatore_mep/graphics/symbol.py`
- Modify: `src/disegnatore_mep/graphics/registry.py`
- Create: `tests/graphics/test_rotation.py`
- Modify: `tests/graphics/test_symbol.py`, `tests/graphics/test_composite.py`

**Interfaces:** produce `PortFace.rotated`, `KeepOut.rotated`, `SymbolManifest.rotated`, `Symbol.rotated`.

- [ ] **Step 1: scrivere il test che fallisce**

Il file di prova è già stato scritto ed eseguito contro la libreria pubblicata: **otto prove, tutte verdi** sul prototipo. Vanno riportate in `tests/graphics/test_rotation.py`. `PUBLISHED` è il percorso di `assets/symbols` ancorato a `__file__` — mai relativo alla directory di lancio, che è il difetto 9 del piano P0 — e `apply_svg_transform`, `rotate_point` e `OBLONG_INLINE_10x6` sono ausiliari definiti nello stesso file di test.

```python
def test_faces_turn_clockwise() -> None:
    assert PortFace.LEFT.rotated(90) is PortFace.TOP
    assert PortFace.TOP.rotated(90) is PortFace.RIGHT
    assert PortFace.RIGHT.rotated(90) is PortFace.BOTTOM
    assert PortFace.BOTTOM.rotated(90) is PortFace.LEFT
    assert PortFace.LEFT.rotated(180) is PortFace.RIGHT
    assert PortFace.LEFT.rotated(270) is PortFace.BOTTOM


def test_every_published_symbol_survives_its_allowed_rotations() -> None:
    """Ogni rotazione dichiarata ammessa deve produrre un manifesto valido:
    e' il validatore di §3 a ricontrollarlo, non una regola nuova."""
    for symbol in SymbolRegistry.from_directory(PUBLISHED).all():
        manifest = symbol.manifest
        for degrees in manifest.allowed_rotations_deg:
            rotated = manifest.rotated(degrees)
            swapped = degrees in (90, 270)
            assert rotated.width_mm == (manifest.height_mm if swapped else manifest.width_mm)
            assert rotated.height_mm == (manifest.width_mm if swapped else manifest.height_mm)
            assert rotated.port_ids == manifest.port_ids


def test_four_quarter_turns_return_the_original() -> None:
    for symbol in SymbolRegistry.from_directory(PUBLISHED).all():
        manifest = symbol.manifest
        if 90 not in manifest.allowed_rotations_deg:
            continue
        turned = manifest
        for _ in range(4):
            turned = turned.rotated(90)
        assert turned.model_dump() == manifest.model_dump()


def test_a_disallowed_rotation_is_refused() -> None:
    """D-049 e' un vincolo impiantistico: uno sfiato coricato e' sbagliato,
    non solo insolito."""
    manifest = SymbolRegistry.from_directory(PUBLISHED).get("air-vent").manifest
    with pytest.raises(SymbolError, match="may not be drawn rotated"):
        manifest.rotated(90)


def test_keep_out_follows_the_face_it_protects() -> None:
    manifest = SymbolRegistry.from_directory(PUBLISHED).get("expansion-vessel").manifest
    assert manifest.keep_out.top_mm > 0
    rotated = manifest.rotated(180)
    assert rotated.keep_out.bottom_mm == manifest.keep_out.top_mm
    assert rotated.keep_out.top_mm == 0


def test_the_body_transform_agrees_with_the_point_transform() -> None:
    """La matrice applicata al corpo SVG e quella applicata alle porte devono
    essere la stessa, o il disegno si stacca dai propri attacchi."""
    for symbol in SymbolRegistry.from_directory(PUBLISHED).all():
        for degrees in symbol.manifest.allowed_rotations_deg:
            if degrees == 0:
                continue
            for corner in ((0.0, 0.0), (symbol.manifest.width_mm, symbol.manifest.height_mm)):
                assert apply_svg_transform(symbol.rotated(degrees).body_transform, corner) == (
                    pytest.approx(rotate_point(corner, symbol.manifest, degrees))
                )


def test_an_inline_symbol_keeps_its_gap_across_a_quarter_turn() -> None:
    """§2.3: l'interruzione si misura sull'asse delle porte, non sulla larghezza."""
    oblong = SymbolManifest.model_validate(OBLONG_INLINE_10x6)
    rotated = oblong.rotated(90)
    assert (rotated.width_mm, rotated.height_mm) == (6.0, 10.0)
    assert rotated.inline_gap_mm == 10.0


def test_the_gap_is_still_refused_when_it_exceeds_the_port_axis() -> None:
    with pytest.raises(ValidationError, match="exceeds the 10mm span between the two opposed ports"):
        SymbolManifest.model_validate(OBLONG_INLINE_10x6 | {"inline_gap_mm": 12.0})
```

- [ ] **Step 2: verificare il fallimento**

```bash
.venv/bin/python -m pytest tests/graphics/test_rotation.py -v
```

Expected: FAIL con `AttributeError: 'PortFace' object has no attribute 'rotated'`.

- [ ] **Step 3: implementare**

Codice verificato sul prototipo. In `symbol.py`:

La tabella delle facce va costruita **dentro** il metodo, come già fanno `opposite` e
`outward_angle_deg`: a livello di modulo, sopra la classe, nominerebbe `PortFace` prima che
esista e uscirebbe `NameError`. Sotto la classe funzionerebbe, ma spezzerebbe lo stile del file.

```python
class PortFace(StrEnum):
    ...

    def rotated(self, degrees: int) -> "PortFace":
        """Rotazione oraria con y crescente verso il basso, come in SVG."""
        clockwise = {
            PortFace.LEFT: PortFace.TOP,
            PortFace.TOP: PortFace.RIGHT,
            PortFace.RIGHT: PortFace.BOTTOM,
            PortFace.BOTTOM: PortFace.LEFT,
        }
        face = self
        for _ in range(degrees // 90):
            face = clockwise[face]
        return face


class KeepOut(StrictModel):
    ...

    def rotated(self, degrees: int) -> "KeepOut":
        result = self
        for _ in range(degrees // 90):
            result = KeepOut(
                left_mm=result.bottom_mm,
                top_mm=result.left_mm,
                right_mm=result.top_mm,
                bottom_mm=result.right_mm,
            )
        return result
```

Il punto ruotato, con `W`/`H` il riquadro **originale**:

| Rotazione | Punto | Riquadro |
|---|---|---|
| 0 | `(x, y)` | `W x H` |
| 90 | `(H - y, x)` | `H x W` |
| 180 | `(W - x, H - y)` | `W x H` |
| 270 | `(y, W - x)` | `H x W` |

`SymbolManifest.rotated(degrees)` rifiuta con `SymbolError` una rotazione non ortogonale e una non presente in `allowed_rotations_deg`; a 0° restituisce `self`; altrimenti costruisce un nuovo `SymbolManifest` — quindi **rivalidato dalle stesse regole**, che è la garanzia centrale del task — con riquadro scambiato per 90/270, porte e ancoraggi trasformati, facce ruotate, area di rispetto ruotata, e

```python
allowed_rotations_deg=[(value - degrees) % 360 for value in self.allowed_rotations_deg]
```

perché su un manifesto già ruotato di `r` una rotazione ulteriore `d` è ammessa se e solo se `r + d` era ammessa in origine. È questa formula a rendere vera la proprietà «quattro quarti di giro tornano all'originale».

**Correggere l'invariante dell'interruzione di linea** (§2.3), dentro `geometry_is_coherent`:

```python
if self.inline_gap_mm is not None:
    faces = {port.face for port in self.ports}
    opposed = any(face.opposite in faces for face in faces)
    if len(self.ports) != 2 or not opposed:
        raise ValueError("an inline symbol needs two opposed ports")
    span = self.width_mm if PortFace.LEFT in faces else self.height_mm
    if self.inline_gap_mm > span + TOLERANCE_MM:
        raise ValueError(
            f"inline gap {self.inline_gap_mm:g}mm exceeds the {span:g}mm "
            f"span between the two opposed ports"
        )
```

Nota l'ordine: il controllo delle due porte opposte va **prima**, perché il calcolo di `span` presuppone che le porte siano opposte.

In `registry.py`, `Symbol.rotated(degrees) -> Symbol` restituisce manifesto ruotato e corpo avvolto nella trasformazione SVG corrispondente:

| Rotazione | Trasformazione |
|---|---|
| 90 | `translate({H} 0) rotate(90)` |
| 180 | `translate({W} {H}) rotate(180)` |
| 270 | `translate(0 {W}) rotate(270)` |

**Verificato:** queste tre matrici muovono gli angoli del riquadro esattamente dove li porta la tabella dei punti, per tutti i dodici simboli pubblicati e per ogni loro rotazione ammessa.

- [ ] **Step 4: aggiornare le due prove accoppiate al vecchio messaggio**

`tests/graphics/test_symbol.py::test_inline_gap_cannot_exceed_the_symbol_width` va rinominato in `test_inline_gap_cannot_exceed_the_port_axis` e il suo `match` portato al messaggio nuovo. Stesso `match` in `tests/graphics/test_composite.py::test_inline_gap_wider_than_the_composite_box_is_rejected`. **Sono le uniche due**: verificato eseguendo la suite con la correzione applicata, 145 passati e 2 falliti, entrambi sul solo testo del messaggio.

- [ ] **Step 5: verificare**

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check src tests examples
.venv/bin/python -m mypy src tests examples
```

Expected: exit `0`; il totale sale a circa 169.

- [ ] **Step 6: commit**

```bash
git add src/disegnatore_mep/graphics tests/graphics
git commit -m "feat: rotate a symbol without breaking the perimeter rule"
```

---

### Task 3: Il piano di impaginazione entra nel modello, e lo schema impara a migrare

**Files:**
- Modify: `src/disegnatore_mep/model/types.py`, `src/disegnatore_mep/model/project.py`, `src/disegnatore_mep/io/project_json.py`, `src/disegnatore_mep/validation/topology.py`
- Create: `tests/model/test_pagination_plan.py`, `tests/model/test_schema_migration.py`
- Modify: `schemas/project.schema.json`, `examples/foundation/valid-mixed-project.json`, `examples/foundation/invalid-cross-medium.json`, `examples/foundation/build_fixtures.py`, `PROJECT_STATE.md`

**Interfaces:** produce `BandRole`, `BandAssignment`, `SheetIntentModel.band_assignments`, `SCHEMA_VERSION`, `migrate_project_document`.

- [ ] **Step 1: scrivere il test che fallisce**

`tests/model/test_pagination_plan.py`:

1. una tavola con `band_assignments` valide costruisce;
2. due assegnazioni allo stesso sottosistema sulla stessa tavola sono rifiutate dal modello;
3. un `subsystem_id` assegnato a una fascia ma assente da `subsystem_ids` della tavola è rifiutato;
4. `BandRole` accetta i quattro valori e rifiuta gli altri;
5. `order` negativo è rifiutato;
6. il validatore topologico emette `UNKNOWN_BAND_SUBSYSTEM` per un sottosistema inesistente;
7. il validatore emette `UNASSIGNED_SUBSYSTEM` quando una tavola elenca un sottosistema che nessuna fascia raccoglie — è la versione di prodotto dell'omissione silenziosa descritta in `P0_REVIEW_FINDINGS` §5: un sottosistema che non finisce su nessuna fascia sparisce dal disegno;
8. un progetto senza tavole resta valido, perché la partizione è facoltativa (D-020).

`tests/model/test_schema_migration.py`:

1. un documento `1.0.0` viene caricato e riportato a `SCHEMA_VERSION` con `band_assignments` vuote;
2. un documento `1.1.0` viene caricato invariato;
3. un documento `2.0.0` è rifiutato con un messaggio che nomina le versioni supportate;
4. `schema_version` assente è rifiutato invece di essere indovinato;
5. **un documento `1.0.0` migrato e il corrispondente `1.1.0` nativo hanno lo stesso fingerprint**;
6. la migrazione è idempotente: applicata due volte dà lo stesso documento;
7. lo schema JSON esportato si rigenera senza differenze.

- [ ] **Step 2: verificare il fallimento**

```bash
.venv/bin/python -m pytest tests/model -v
```

Expected: FAIL con `ImportError: cannot import name 'BandRole'`.

- [ ] **Step 3: implementare**

In `types.py`:

```python
class BandRole(StrEnum):
    """Le fasce funzionali della tavola, da sinistra a destra (D-041)."""

    GENERATION = "generation"
    PRIMARY = "primary"
    DISTRIBUTION = "distribution"
    TERMINAL = "terminal"

    @property
    def reading_order(self) -> int:
        return list(BandRole).index(self)
```

In `project.py`, `BandAssignment(subsystem_id, band: BandRole, order: int = Field(ge=0))`; `SheetIntentModel` acquista `band_assignments: list[BandAssignment]` con un validatore che rifiuta un sottosistema assegnato due volte e uno non elencato in `subsystem_ids`. `schema_version` passa da `Literal["1.0.0"]` a `str` con `pattern=r"^\d+\.\d+\.\d+$"` più un validatore che pretende `SCHEMA_VERSION`: il modello in memoria parla **una sola** versione, la migrazione avviene al confine.

In `project_json.py`, `migrate_project_document(document: dict) -> dict` alza `1.0.0` a `1.1.0` aggiungendo `band_assignments: []` a ogni tavola e rifiuta ogni altra versione con `f"unsupported schema version {found}: this build reads {sorted(MIGRATIONS)} and writes {SCHEMA_VERSION}"`. `load_project` la applica prima di validare.

In `topology.py`, i due codici nuovi `UNKNOWN_BAND_SUBSYSTEM` e `UNASSIGNED_SUBSYSTEM`. Il primo è bloccante, il secondo pure: una tavola che dichiara un sottosistema e non gli dà una fascia non è disegnabile, non è un avviso.

- [ ] **Step 4: rigenerare fixture, schema e impronta**

```bash
.venv/bin/python examples/foundation/build_fixtures.py
.venv/bin/python -m disegnatore_mep export-schema schemas/project.schema.json
.venv/bin/python -m disegnatore_mep fingerprint examples/foundation/valid-mixed-project.json
```

L'impronta **cambia** rispetto a `3347374e8b3f006c6f387c6228e0d9d2b885cbf57e65991937e985af32306573`, perché il documento dichiara ora `1.1.0`. Riportare il valore nuovo in `PROJECT_STATE.md` e nei test di accettazione che lo fissano, con una riga che dice perché è cambiato. **Non aggirare il cambiamento** lasciando la fixture a `1.0.0`: la forma canonica si calcola dopo il caricamento, quindi l'impronta sarebbe comunque quella della `1.1.0` e il file su disco mentirebbe.

- [ ] **Step 5: verificare**

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check src tests examples
.venv/bin/python -m mypy src tests examples
git status --short
```

Expected: exit `0`; il totale sale a circa 181; `git status` mostra solo i file attesi.

- [ ] **Step 6: commit**

```bash
git add src tests schemas examples PROJECT_STATE.md
git commit -m "feat: record the pagination plan in the model, with a migration path"
```

---

### Task 4: Il telaio della tavola Nove C

**Files:**
- Modify: `src/disegnatore_mep/graphics/standard.py`
- Create: `src/disegnatore_mep/graphics/frame.py`, `tests/graphics/test_frame.py`
- Modify: `tests/graphics/test_standard.py`, `tests/graphics/test_svg.py`, `docs/GRAPHIC_STANDARD.md`, `docs/DECISION_LOG.md`

**Interfaces:** produce `SheetFrame`, `NOVE_C_A3`.

> Non richiede conferme: le misure sono lette dal cartiglio fornito dal PM (§0 e §2.1).

- [ ] **Step 1: scrivere il test che fallisce**

`tests/graphics/test_frame.py`:

Tre nomi, da tenere distinti perché è facile confonderli e il piano ne usa tutti e tre: la
**squadratura** è il rettangolo del cartiglio, 400 × 277 mm; il **corpo** è ciò che resta
togliendo intestazione e cartiglio, 400 × 235 mm; l'**area di disegno** è il corpo meno la
fascia della legenda, 350 × 235 mm, ed è la superficie su cui il layout dispone e instrada.

1. la squadratura è 400 × 277 mm con margini 10 mm sui quattro lati;
2. il corpo è 400 × 235 mm, fra intestazione e cartiglio;
3. la fascia della legenda è larga 50 mm (20 passi) e alta quanto il corpo, ancorata a destra (D-052);
4. l'area di disegno è quindi 350 × 235 mm;
5. **entrambi gli assi dell'area di disegno sono un numero intero di passi di griglia**, 140 e 94: è ciò da cui dipende l'instradamento, e va fissato da un test perché una futura modifica delle bande non lo rompa senza accorgersene;
6. la riserva del cartiglio è alta 36 mm e larga quanto la squadratura, e **non si sovrappone** né al corpo né alla legenda;
7. le quattro aree — intestazione, corpo, legenda, cartiglio — sono disgiunte a due a due e contenute nella squadratura;
8. un `SheetFrame` le cui bande non stanno nel foglio è rifiutato in costruzione;
9. una fascia legenda più larga del corpo è rifiutata;
10. `NOVE_C_A3` deriva le proprie misure da `A3_LANDSCAPE` e non ridichiara le grandezze della carta.

`tests/graphics/test_standard.py` **non perde nulla**. In particolare la prova che fissa come voluta l'asimmetria di `usable_height_mm` resta valida: 277 mm restano 110,8 passi anche col margine nuovo, perché l'altezza utile non dipende dal margine sinistro. Cambia soltanto il valore della larghezza, da 390 a 400, che nessuna prova asserisce direttamente. Chi eseguirà il task non si aspetti quindi di dover cancellare quella prova: se si trova a volerlo fare, ha sbagliato qualcos'altro.

- [ ] **Step 2: verificare il fallimento**

```bash
.venv/bin/python -m pytest tests/graphics/test_frame.py -v
```

Expected: FAIL con `ModuleNotFoundError: No module named 'disegnatore_mep.graphics.frame'`.

- [ ] **Step 3: implementare**

`A3_LANDSCAPE` porta `margin_left_mm` da `20.0` a `10.0`. `frame.py` dichiara le proprie costanti di impaginazione, nominate, come `svg.py` già fa (D-046):

```python
TITLE_BLOCK_HEIGHT_MM = 36.0
"""Banda del cartiglio Nove C: 34 mm di banda piu' 2 mm di filetto, misurati
su assets/cartigli/Cartiglio_NoveC_A3.pdf."""
HEADER_HEIGHT_MM = 6.0
"""Fascia d'intestazione, dal filetto superiore del cartiglio."""
LEGEND_WIDTH_MM = 50.0
"""Fascia della legenda sul lato destro (D-052): venti passi di griglia,
larghi abbastanza per un simbolo e la sua denominazione italiana."""
BAND_GUTTER_MM = 10.0
"""Distanza fra due fasce funzionali contigue."""
```

`SheetFrame` è un `StrictModel` con un validatore `areas_are_disjoint` che riasserisce i punti 6 e 7 della lista sopra. Espone `body_rect_mm`, `drawing_rect_mm`, `legend_rect_mm`, `title_block_rect_mm` e `header_rect_mm` come `Rect` con origine in alto a sinistra, come SVG — non come il PDF del cartiglio, che ha l'origine in basso e da cui le misure di §2.1 vanno quindi ribaltate.

Il cartiglio **non viene disegnato** da questo piano: qui se ne riserva soltanto lo spazio, perché un layout che ignorasse la riserva andrebbe rifatto quando il cartiglio arriverà. Il template vettoriale compilabile è del piano successivo.

- [ ] **Step 4: aggiornare le due prove accoppiate al margine**

`tests/graphics/test_svg.py::test_symbol_wider_than_the_usable_area_raises_naming_both_measurements` porta `390` a `400`; `test_scale_bar_wider_than_the_usable_area_is_rejected` porta `90` a `100`. **Sono le uniche due**: verificato eseguendo la suite col margine a 10 mm, 145 passati e 2 falliti.

- [ ] **Step 5: aggiornare i documenti**

`docs/GRAPHIC_STANDARD.md` §1.1: la tabella dei valori, dove `margin_left_mm` passa a 10,0 e la motivazione non è più la rilegatura ISO 5457 ma la squadratura del cartiglio (D-053). §1.2 **resta vera e non va toccata nel merito**: l'asimmetria di `usable_height_mm` non è cambiata; va solo aggiornato il numero della larghezza e aggiunta una riga che rimanda alla sezione nuova. Aggiungere una sezione sul telaio con le misure di §2.1 di questo piano, e dire esplicitamente che l'area di disegno — 350 × 235 mm, il corpo meno la fascia della legenda — è la superficie su cui il layout lavora, distinta dall'area utile del foglio. Registrare D-053 nel `DECISION_LOG`.

- [ ] **Step 6: verificare e committare**

```bash
.venv/bin/python -m pytest -q && .venv/bin/python -m ruff check src tests examples && .venv/bin/python -m mypy src tests examples
git add src/disegnatore_mep/graphics tests/graphics docs
git commit -m "feat: give the sheet the Nove C frame it will be printed in"
```

Expected: exit `0`; il totale sale a circa 191.

---

### Task 5: Le tratte, ovvero l'accessorio in linea non è un nodo

W4 di `P0_REVIEW_FINDINGS` dice: «il componente in linea è rappresentabile ma mai esercitato, `inline_gap_mm` non è letto da nessuna parte, e **nulla lega due segmenti alla stessa tratta originaria**. Primo compito di P4, non l'ultimo.» È questo task.

**Files:**
- Create: `src/disegnatore_mep/layout/__init__.py`, `src/disegnatore_mep/layout/errors.py`, `src/disegnatore_mep/layout/trunks.py`
- Create: `tests/layout/test_trunks.py`

**Interfaces:** produce `LayoutError`, `Trunk`, `build_trunks`.

- [ ] **Step 1: scrivere il test che fallisce**

Prototipo già scritto ed eseguito: **sei prove, tutte verdi**.

1. tre accessori in fila fra pompa e caldaia collassano in **una** tratta, con estremi `pump` e `boiler` e le quattro connessioni in ordine;
2. una connessione senza accessori è comunque una tratta;
3. ogni connessione del progetto finisce in **esattamente una** tratta, senza ripetizioni;
4. un accessorio in linea con una sola connessione è rifiutato: spezza una tratta, quindi ne ha due;
5. un accessorio che unisce due reti diverse è rifiutato;
6. un anello di soli accessori, che non tocca nessun componente non in linea, è rifiutato invece di sparire in silenzio.

- [ ] **Step 2: verificare il fallimento**

```bash
.venv/bin/python -m pytest tests/layout/test_trunks.py -v
```

Expected: FAIL con `ModuleNotFoundError: No module named 'disegnatore_mep.layout'`.

- [ ] **Step 3: implementare**

`Trunk` è una dataclass frozen con `network_id`, `start: PortRef`, `end: PortRef`, `connection_ids: tuple[str, ...]` e `inline_component_ids: tuple[str, ...]`.

`build_trunks(project, inline_component_ids)` costruisce l'incidenza per componente, controlla i due invarianti sugli accessori (due connessioni, una sola rete), poi per ogni connessione non ancora consumata parte da un estremo non in linea e cammina attraverso gli accessori — entrando da una porta ed uscendo dall'altra, che il manifesto garantisce essere opposta — fino al primo componente non in linea. Chiude verificando che l'insieme delle connessioni consumate sia **tutto**: ciò che resta è un anello di soli accessori, e va segnalato.

L'insieme `inline_component_ids` arriva da `ResolvedComponent.is_inline` del Task 1: è la libreria a dire quali componenti sono in linea, non un elenco scritto nel motore.

- [ ] **Step 4: verificare e committare**

```bash
.venv/bin/python -m pytest -q && .venv/bin/python -m ruff check src tests examples && .venv/bin/python -m mypy src tests examples
git add src/disegnatore_mep/layout tests/layout
git commit -m "feat: rebuild the run an inline accessory broke"
```

Expected: exit `0`; il totale sale a circa 199.

---

### Task 6: Partizione multi-tavola e rimandi accoppiati

La partizione precede il layout (D-028, specifica §10.1): tagliare un disegno già disposto spezzerebbe circuiti in modo arbitrario.

**Files:**
- Create: `src/disegnatore_mep/layout/partition.py`, `tests/layout/test_partition.py`

**Interfaces:** produce `SheetPartition`, `SheetLink`, `partition_project`.

> P3 decisa: si spezza solo quando non entra.

- [ ] **Step 1: scrivere il test che fallisce**

1. un progetto senza tavole dichiarate produce una partizione a **una** tavola che contiene tutto;
2. un progetto con due tavole dichiarate produce due partizioni, ciascuna coi propri componenti e reti;
3. ogni componente del progetto appartiene ad **almeno** una tavola: nessuna omissione silenziosa;
4. una connessione i cui estremi stanno su tavole diverse genera **due** rimandi, uno per tavola, con lo stesso identificativo di coppia;
5. ogni rimando ha esattamente un gemello: la prova di accoppiamento richiesta dalla specifica §12.2;
6. un rimando porta identificativo, provenienza, destinazione e fluido (specifica §10.3);
7. una tratta spezzata da un confine di tavola conserva i propri accessori sulla tavola dove cade ciascuno, e non ne perde nessuno;
8. una tavola vuota è rifiutata con `LayoutError`;
9. un componente in nessun sottosistema, con più tavole dichiarate, è rifiutato: non saprebbe dove finire;
10. la partizione è deterministica: stesso progetto, stessa partizione, e l'ordine delle tavole segue quello dichiarato nel modello.

- [ ] **Step 2: verificare il fallimento**

```bash
.venv/bin/python -m pytest tests/layout/test_partition.py -v
```

Expected: FAIL con `ImportError: cannot import name 'partition_project'`.

- [ ] **Step 3: implementare**

`partition_project(project, resolved, trunks) -> list[SheetPartition]`. Senza tavole dichiarate restituisce una partizione unica. Con tavole dichiarate, ogni componente segue il sottosistema che lo contiene; le connessioni interamente dentro una tavola le appartengono, quelle a cavallo generano una coppia di `SheetLink`.

`SheetLink` porta `id`, `pair_id`, `sheet_id`, `peer_sheet_id`, `connection_id`, `network_id`, `medium` e la porta a cui si attacca. L'identificativo di coppia è derivato dal `connection_id`, quindi stabile fra rigenerazioni.

La regola di divisione (P3) vive **solo qui**, in una funzione con un nome che la dichiara — `partition_is_needed(project, frame)` — così cambiarla non tocca il resto del motore.

- [ ] **Step 4: verificare e committare**

```bash
.venv/bin/python -m pytest -q && .venv/bin/python -m ruff check src tests examples && .venv/bin/python -m mypy src tests examples
git add src/disegnatore_mep/layout tests/layout
git commit -m "feat: split a plant across sheets without cutting a circuit"
```

Expected: exit `0`; il totale sale a circa 209.

---

### Task 7: La libreria del caso D-011, sulla griglia

> P1 decisa: caso D-011 completo. Questo task chiude **D-050**.

**Files:**
- Create: `src/disegnatore_mep/layout/grid.py`, `tests/layout/test_grid.py`
- Modify: `examples/graphics/build_symbols.py`, `examples/foundation/build_fixtures.py`
- Create/Modify: i manifesti e i corpi in `assets/symbols/`
- Create: `examples/layout/catalog/`, `examples/layout/build_layout_fixtures.py`
- Modify: `tests/acceptance/test_symbol_sheet.py`, `docs/GRAPHIC_STANDARD.md`, `docs/DECISION_LOG.md`

**Interfaces:** produce `GridSpace`, `assert_symbol_is_aligned`.

- [ ] **Step 1: scrivere il test che fallisce**

`tests/layout/test_grid.py`:

1. `GridSpace.to_cell` e `to_mm` sono l'una l'inversa dell'altra sui multipli del passo;
2. una coordinata fuori griglia sollevata a `to_cell` produce `LayoutError` con il valore e il passo, non un arrotondamento silenzioso;
3. **ogni simbolo della libreria pubblicata è allineato**: riquadro e ogni coordinata di porta sono multipli del passo;
4. lo stesso per la libreria di fixture;
5. `assert_symbol_is_aligned` nomina il simbolo, la porta e la coordinata colpevole;
6. un simbolo con una porta centrata su un lato di lunghezza dispari in passi è rifiutato, con un messaggio che spiega che il lato deve essere pari.

La prova 3 **fallisce oggi su tutti e dodici** i simboli: è la scoperta di §2.2, e va vista fallire prima di essere risolta.

- [ ] **Step 2: verificare il fallimento**

```bash
.venv/bin/python -m pytest tests/layout/test_grid.py -v
```

Expected: FAIL; il messaggio elenca venti simboli fuori griglia.

- [ ] **Step 3: ridimensionare la libreria sulla gerarchia**

La gerarchia proposta, tutte misure multiple del passo da 2,5 mm e con lati pari dove serve una porta centrata:

| Classe | Riquadro | Passi | Componenti |
|---|---|---|---|
| Accessorio in linea | 7,5 × 5 | 3 × 2 | valvola di intercettazione, ritegno, filtro a Y, valvola gas, serranda |
| Accessorio terminale | 5 × 10 | 2 × 4 | sfiato aria automatico |
| Strumento e apparecchio | 10 × 10 | 4 × 4 | circolatore, contatore gas, ventilatore in linea, diffusore, stacco refrigerante, valvola deviatrice a tre vie |
| Terminale | 15 × 10 | 6 × 4 | radiatore, pannello radiante, ventilconvettore, unità interna, terminale aria |
| Collettore | 30 × 5 | 12 × 2 | collettore di zona |
| Vaso di espansione | 10 × 15 | 4 × 6 | vaso di espansione a membrana |
| Generatore e macchina | 20 × 15 | 8 × 6 | pompa di calore aria-acqua, caldaia, unità esterna VRV |
| Accumulo | 15 × 25 | 6 × 10 | bollitore ACS, volano termico a quattro attacchi |

La scala è quella che D-050 chiede: **verificato**, l'area di una valvola sta dieci volte in quella di un accumulo. P1 ha deciso che la gerarchia si fissa qui; i millimetri esatti si giudicano a vista sul foglio di riscontro (Step 4), come per ogni simbolo di questa libreria. La **regola** invece non è negoziabile, perché senza di essa l'instradamento non arriva agli attacchi:

> Ogni lato è un multiplo del passo. Il lato su cui una porta è **centrata** è un numero **pari** di passi, così il centro cade su un nodo. Un lato dispari è legittimo se nessuna porta vi è centrata: l'accessorio in linea 7,5 × 5 è largo tre passi, ma le sue due porte stanno sulle facce sinistra e destra, alle ascisse 0 e 7,5, e sono centrate sull'altezza, che è di due passi.

**Verificato:** tutte le taglie della tabella sono multiple del passo da 2,5 mm.

I dodici simboli esistenti vanno rigenerati alle taglie nuove: i corpi SVG si riscalano, non si ridisegnano, tranne dove il rapporto fra i lati cambia. I circa dieci nuovi seguono la procedura di `GRAPHIC_STANDARD.md` §5, compresa la validazione prima della scrittura e il controllo a vista sul foglio di riscontro (§5 punto 8): un simbolo che valida ma non si legge ha fallito, come il filtro a Y del Task 6 del piano grafico.

Le definizioni di catalogo del caso D-011 vanno in `examples/layout/catalog/`, non nella fondazione, e sono generate da uno script come le altre.

- [ ] **Step 4: aggiornare il foglio di riscontro**

`tests/acceptance/test_symbol_sheet.py` asserisce dodici simboli: passa al numero della libreria nuova, che l'elenco definitivo fisserà intorno a ventiquattro. Il foglio continua a entrare, e non di misura: **verificato** su ventiquattro simboli con le taglie della tabella, la colonna più larga è 45,6 mm — la detta la denominazione «Volano termico a quattro attacchi», non il simbolo — e ne stanno otto per riga sui 400 mm di area utile; tre righe da 39 mm occupano 117 mm dei 277 disponibili. La guardia di capacità va comunque **vista** passare, non supposta: rigenerare il foglio e aprirlo.

```bash
.venv/bin/python examples/graphics/build_symbols.py
.venv/bin/python examples/layout/build_layout_fixtures.py
git status --short assets/symbols examples
.venv/bin/python -m disegnatore_mep symbols-sheet outputs/symbols.svg --symbols assets/symbols
```

La seconda esecuzione dei generatori non deve produrre differenze: la rigenerazione è riproducibile bit per bit.

- [ ] **Step 5: verificare e committare**

```bash
.venv/bin/python -m pytest -q && .venv/bin/python -m ruff check src tests examples && .venv/bin/python -m mypy src tests examples
git add src tests assets examples docs
git commit -m "feat: put the symbol library on the grid and give size a meaning"
```

Expected: exit `0`; il totale sale a circa 221.

---

### Task 8: Posizionamento a fasce sulla griglia

**Files:**
- Create: `src/disegnatore_mep/layout/geometry.py`, `src/disegnatore_mep/layout/plan.py`, `src/disegnatore_mep/layout/place.py`
- Create: `tests/layout/test_geometry.py`, `tests/layout/test_plan.py`, `tests/layout/test_place.py`

**Interfaces:** produce `PlacedSymbol`, `SheetGeometry`, `DrawingGeometry`, `place_sheet`.

- [ ] **Step 1: scrivere il test che fallisce**

1. i generatori finiscono nella fascia più a sinistra e i terminali in quella più a destra (D-041);
2. ogni simbolo posato ha origine su un nodo di griglia;
3. due simboli posati non si sovrappongono, **aree di rispetto comprese**;
4. nessun simbolo esce dall'**area di disegno**: nulla entra nella fascia della legenda, nell'intestazione o nella riserva del cartiglio;
5. la mandata sta sopra il ritorno all'interno della stessa fascia;
6. l'ordine di lettura dentro una fascia segue il campo `order` del piano di impaginazione, non l'ordine di dichiarazione dei componenti;
7. un componente in linea **non** viene posato qui: appartiene alla sua tratta (Task 10);
8. la rotazione scelta per un simbolo appartiene sempre a `allowed_rotations_deg`;
9. un impianto che non entra nell'area di disegno fallisce con una diagnostica che dice quanti simboli entrano e su quale asse manca lo spazio — mai un rimpicciolimento, mai un disegno fuori pagina (D-045);
10. il posizionamento è deterministico: stessa geometria a ogni esecuzione e con `PYTHONHASHSEED` variabile;
11. lo stesso progetto con un piano di impaginazione diverso produce una geometria diversa: è la proprietà che rende utile registrare il piano (D-042);
12. un piano che assegna un sottosistema a una fascia inesistente è rifiutato prima di posare qualunque cosa.

- [ ] **Step 2: verificare il fallimento**

```bash
.venv/bin/python -m pytest tests/layout/test_place.py -v
```

Expected: FAIL con `ImportError: cannot import name 'place_sheet'`.

- [ ] **Step 3: implementare**

`geometry.py` porta il modello geometrico derivato: `Rect`, `PlacedSymbol(component_id, symbol_id, rotation_deg, origin_cell, box_cells)`, e i contenitori `SheetGeometry` e `DrawingGeometry`. Sono `StrictModel`, quindi serializzabili e confrontabili, e da lì nasce `drawing_fingerprint` per la riproducibilità (Task 12).

`place_sheet(partition, frame, plan)` procede in quattro passi deterministici: raccogliere i componenti non in linea per fascia; ordinarli dentro la fascia per `(order del piano, rete, verso, id)`; scegliere per ciascuno la rotazione che porta le porte verso la fascia adiacente giusta, fra quelle ammesse; incolonnarli sulla griglia lasciando l'area di rispetto e la distanza minima. Le larghezze di fascia si derivano dal contenuto, con `BAND_GUTTER_MM` fra l'una e l'altra; se la somma supera i 350 mm dell'area di disegno, si fallisce con la diagnostica del punto 9.

Nessun ramo logico guarda il nome di un componente: la fascia arriva dal piano, il verso dalla porta, la taglia dal simbolo.

- [ ] **Step 4: verificare e committare**

```bash
.venv/bin/python -m pytest -q && .venv/bin/python -m ruff check src tests examples && .venv/bin/python -m mypy src tests examples
git add src/disegnatore_mep/layout tests/layout
git commit -m "feat: place components in functional bands on the grid"
```

Expected: exit `0`; il totale sale a circa 233.

---

### Task 9: Instradamento ortogonale, dove l'incrocio costa poco

**Files:**
- Create: `src/disegnatore_mep/layout/route.py`, `tests/layout/test_route.py`

**Interfaces:** produce `Route`, `RoutedTrunk`, `route_sheet`.

- [ ] **Step 1: scrivere il test che fallisce**

Prototipo già scritto ed eseguito: **undici prove, tutte verdi**, su una griglia di 160 × 94 celle. L'area di disegno reale ne misura 140 × 94, quindi le prove girano su una superficie più larga di quella vera e i tempi misurati sono un limite superiore.

1. una tratta libera è una linea retta, e costa esattamente la sua lunghezza;
2. il percorso è ortogonale e contiguo: ogni passo muove di una cella su un solo asse;
3. **una rete che ne incrocia un'altra passa sopra invece di girarle intorno**, e il costo è la lunghezza più un incrocio: è il cuore di D-041;
4. il costo di un incrocio è minore del giro minimo per evitarlo, che vale due passi — la disuguaglianza va asserita, non lasciata alla taratura;
5. un ostacolo si aggira, non si attraversa: un simbolo posato non ha tubazioni che gli passano sotto;
6. due reti si incrociano ma **non si costeggiano**: la rotta non percorre in parallelo le celle di un'altra;
7. una porta murata fallisce con una diagnostica, non con un percorso assurdo;
8. il limite di iterazioni produce una diagnostica e non un blocco (specifica §10.2);
9. lo stesso ingresso dà sempre la stessa rotta;
10. una rotta d'angolo su tutto il foglio si calcola in meno di un secondo;
11. **la direzione di una porta è quella uscente**, e passarla al contrario non fallisce: costruisce un cappio che rientra dal lato sbagliato.

La prova 11 documenta un errore in cui questo piano è caduto scrivendo il proprio prototipo. La conseguenza pratica è nel codice: la direzione **non si passa a mano**, si deriva da `PortFace.outward_angle_deg`.

- [ ] **Step 2: verificare il fallimento**

```bash
.venv/bin/python -m pytest tests/layout/test_route.py -v
```

Expected: FAIL con `ImportError: cannot import name 'route_sheet'`.

- [ ] **Step 3: implementare**

Costi verificati sul prototipo:

```python
STEP_COST = 10
"""Costo di un passo di griglia. La lunghezza e' la voce dominante."""
TURN_COST = 15
"""Costo di una piega: una tubazione che serpeggia si legge male."""
CROSS_COST = 5
"""Costo di un incrocio segnato. Meno di un passo, quindi meno del giro
minimo per evitarlo, che ne costa due: l'instradatore non deviera' mai per
schivare un incrocio, che e' esattamente cio' che D-041 chiede."""
```

A* su stato `(cella, direzione di arrivo)` — la direzione entra nello stato perché il costo di piega dipende da come ci si è arrivati — con euristica di Manhattan moltiplicata per `STEP_COST`, ammissibile perché piega e incrocio possono solo aggiungere. Il determinismo viene da un ordine fisso dei vicini e da una chiave di coda totale; **verificato**: con `PYTHONHASHSEED` a 0, 1, 7 e 12345 la stessa rotta, `sha256` identico, costo 2050. **Verificato** anche il tempo: una rotta da un angolo all'altro di una griglia 160 × 94, con un muro da 120 celle da aggirare, si risolve in 0,09 s — su una griglia più grande dell'area di disegno reale.

Le celle proibite sono i riquadri dei simboli posati più la loro area di rispetto. Le celle occupate sono quelle già percorse da un'altra tratta: attraversarle costa `CROSS_COST`, percorrerle in parallelo non è ammesso — si controlla che la cella successiva nella stessa direzione non sia anch'essa occupata.

`route_sheet` instrada le tratte in un ordine deterministico e accumula le celle occupate; se una tratta non converge, la diagnostica dice quale e propone una partizione diversa, come vuole §10.2.

- [ ] **Step 4: verificare e committare**

```bash
.venv/bin/python -m pytest -q && .venv/bin/python -m ruff check src tests examples && .venv/bin/python -m mypy src tests examples
git add src/disegnatore_mep/layout tests/layout
git commit -m "feat: route runs orthogonally, crossing rather than detouring"
```

Expected: exit `0`; il totale sale a circa 247.

---

### Task 10: L'accessorio in linea posato sulla tratta

**Files:**
- Create: `src/disegnatore_mep/layout/inline.py`, `tests/layout/test_inline.py`

**Interfaces:** produce `place_inline_accessories`.

- [ ] **Step 1: scrivere il test che fallisce**

1. un accessorio in linea è posato **sulla spezzata** della propria tratta, non accanto;
2. la spezzata è **interrotta** per `inline_gap_mm` centrati sull'accessorio: nessuna linea continua gli passa sotto (D-027);
3. l'interruzione è misurata sull'asse delle porte, quindi vale anche per un accessorio ruotato di 90° (§2.3);
4. la rotazione dell'accessorio segue la direzione del tratto su cui sta, e appartiene ad `allowed_rotations_deg`;
5. tre accessori sulla stessa tratta si distribuiscono in ordine topologico, non si sovrappongono e mantengono la distanza minima;
6. un accessorio che non entra nel proprio tratto — la tratta è più corta della somma delle interruzioni — fallisce con una diagnostica che dice quanto manca;
7. un accessorio posato su un tratto obliquo è impossibile per costruzione, perché le rotte sono ortogonali: la prova fissa l'invariante;
8. le due connessioni che l'accessorio separa restano associate alla stessa tratta, e la distinta continua a contarlo una volta sola.

- [ ] **Step 2: verificare il fallimento**

```bash
.venv/bin/python -m pytest tests/layout/test_inline.py -v
```

Expected: FAIL con `ModuleNotFoundError`.

- [ ] **Step 3: implementare**

`place_inline_accessories(routed_trunk, resolved)` percorre la spezzata, distribuisce gli accessori nell'ordine in cui la tratta li incontra, e per ciascuno calcola centro, rotazione dal verso del segmento e le due interruzioni della spezzata. Restituisce i `PlacedSymbol` degli accessori e la spezzata spezzata.

È qui che `inline_gap_mm` acquista finalmente un lettore: W4 si chiude.

- [ ] **Step 4: verificare e committare**

```bash
.venv/bin/python -m pytest -q && .venv/bin/python -m ruff check src tests examples && .venv/bin/python -m mypy src tests examples
git add src/disegnatore_mep/layout tests/layout
git commit -m "feat: break the line where an inline accessory sits"
```

Expected: exit `0`; il totale sale a circa 255.

---

### Task 11: Tag di valore e fascia della legenda

**Files:**
- Create: `src/disegnatore_mep/layout/labels.py`, `src/disegnatore_mep/layout/legend.py`
- Create: `tests/layout/test_labels.py`, `tests/layout/test_legend.py`
- Modify: `docs/DECISION_LOG.md`

**Interfaces:** produce `PlacedLabel`, `LegendEntry`, `place_labels`, `build_legend`.

> P4 decisa: colore più tratto distinto per ogni rete.

- [ ] **Step 1: scrivere il test che fallisce**

1. la legenda contiene **solo** i simboli usati sulla tavola, non l'intera libreria (D-052);
2. un simbolo usato dieci volte compare in legenda **una** volta;
3. le voci di legenda portano la denominazione italiana del manifesto, mai l'identificativo (D-051);
4. nel corpo del disegno **nessuna etichetta ripete** una denominazione presente in legenda: è la prova che rende vera la divisione dei ruoli di D-052;
5. un tag di valore — i litri di un vaso, la portata di un circolatore — compare accanto al componente, ancorato a un `label_anchor` di ruolo `tag` o `data`;
6. la sigla di un componente (`ComponentInstance.tag`) compare quando c'è e non viene inventata quando manca;
7. due etichette non si sovrappongono, né fra loro né a un simbolo o a una rotta;
8. la legenda porta anche la sezione delle reti, con colore e tratto di ciascuna;
9. una legenda più alta della propria fascia fallisce con una diagnostica: non si rimpicciolisce il testo (ADR 0003);
10. l'ordine delle voci è deterministico e stabile fra rigenerazioni.

- [ ] **Step 2: verificare il fallimento**

```bash
.venv/bin/python -m pytest tests/layout/test_legend.py tests/layout/test_labels.py -v
```

Expected: FAIL con `ModuleNotFoundError`.

- [ ] **Step 3: implementare**

`build_legend(sheet_geometry, resolved, networks)` raccoglie i `symbol_id` distinti effettivamente posati, li ordina, ne prende la denominazione italiana e impagina la fascia dall'alto. Poi la sezione delle reti: per ciascuna, un tratto campione con il proprio colore e la propria trattina, e il nome della rete.

`place_labels` posiziona i soli tag che aggiungono informazione: la sigla del componente e le proprietà di valore del modello. **La denominazione non si scrive mai nel corpo**: la dice la legenda. La prova 4 lo presidia.

La codifica delle reti (P4) vive in una tabella nominata in `legend.py`, associata al `medium` della rete, non al dominio: acqua calda e acqua refrigerata sono entrambe idroniche e devono distinguersi.

- [ ] **Step 4: verificare e committare**

```bash
.venv/bin/python -m pytest -q && .venv/bin/python -m ruff check src tests examples && .venv/bin/python -m mypy src tests examples
git add src/disegnatore_mep/layout tests/layout docs
git commit -m "feat: the legend says what, the tag says how much"
```

Expected: exit `0`; il totale sale a circa 265.

---

### Task 12: Validazione geometrica, renderer della tavola e gate di accettazione

**Files:**
- Create: `src/disegnatore_mep/validation/geometry.py`, `src/disegnatore_mep/graphics/sheet.py`
- Create: `tests/validation/test_geometry.py`, `tests/graphics/test_sheet.py`, `tests/acceptance/test_drawing.py`
- Create: `examples/layout/heat-pump-dhw-buffer-two-zones.json`
- Modify: `src/disegnatore_mep/cli.py`, `src/disegnatore_mep/io/canonical.py`, `docs/ARCHITECTURE.md`, `docs/GRAPHIC_STANDARD.md`, `README.md`, `PROJECT_STATE.md`

**Interfaces:** produce `validate_drawing_geometry`, `render_sheet`, `drawing_fingerprint`, comando CLI `draw`.

- [ ] **Step 1: scrivere il test che fallisce**

`tests/validation/test_geometry.py` copre uno a uno i controlli della specifica §12.2, ciascuno con il caso che deve passare e quello che deve fallire: nessun componente flottante; nessuna linea attraversa un simbolo in linea; porte e segmenti coincidono entro tolleranza; nessuna sovrapposizione non ammessa; testi e tag non collidono; distanze minime rispettate; rimandi accoppiati; oggetti interamente dentro l'area utile.

`tests/graphics/test_sheet.py`: il foglio dichiara millimetri fisici e `viewBox` numericamente identico; è XML ben formato; contiene il telaio, i simboli posati con la propria trasformazione di rotazione, le spezzate, le etichette e la legenda; è deterministico byte per byte.

`tests/acceptance/test_drawing.py` è **il gate**:

1. il progetto D-011 — pompa di calore aria-acqua, ACS con valvola deviatrice, bollitore, volano a quattro attacchi, circolatore secondario, collettore a due zone con terminali diversi — si carica, valida, dispone, instrada e renderizza senza errori;
2. il disegno rispetta **tutti** i controlli geometrici;
3. **nessuna linea passa sotto un componente in linea**: è il gate dichiarato per P4 nella roadmap master;
4. la scala è invariante: il foglio dichiara 420 × 297 mm e i simboli hanno le misure del proprio manifesto;
5. il caso entra in **una** tavola; un caso volutamente sovrabbondante ne produce due, con rimandi accoppiati;
6. `drawing_fingerprint` è stabile fra processi separati e con `PYTHONHASHSEED` variabile;
7. il gate G0 di P0 continua a passare.

- [ ] **Step 2: verificare il fallimento**

```bash
.venv/bin/python -m pytest tests/acceptance/test_drawing.py -v
```

Expected: FAIL con `ModuleNotFoundError: No module named 'disegnatore_mep.graphics.sheet'`.

- [ ] **Step 3: implementare**

`render_sheet(sheet_geometry, frame)` emette il foglio come `render_symbol_sheet` già fa per la libreria — `width`/`height` in millimetri, `viewBox` numericamente identico — ma componendo telaio, riserva del cartiglio, simboli posati ciascuno col proprio `transform`, spezzate, interruzioni, etichette e fascia della legenda. `render_symbol_sheet` **resta com'è**: è un banco di prova della libreria, non la tavola, e non va generalizzato.

La CLI acquista `draw`:

```bash
.venv/bin/python -m disegnatore_mep draw examples/layout/heat-pump-dhw-buffer-two-zones.json \
  --catalog examples/layout/catalog --symbols assets/symbols --out outputs/
```

Codici di uscita coerenti con quelli esistenti: `0` disegno prodotto, `2` errori bloccanti di validazione tecnica o geometrica, `1` errori di caricamento.

Il foglio prodotto è **marcato come bozza**: il cartiglio non è ancora compilato, e una tavola finale con cartiglio incompleto non si emette (D-025). Toglierlo spetta al piano di rendering e cartiglio.

- [ ] **Step 4: guardare la tavola**

I controlli automatici dimostrano che nulla si sovrappone, non che il disegno si legga. Rigenerare la tavola, aprirla, e controllare a vista: le fasce si leggono da sinistra a destra? Le mandate stanno sopra i ritorni? Gli accessori sono vicini al componente che servono? Ci sono serpentine dove basterebbe una linea retta? La legenda è completa e il corpo non la ripete?

Ciò che non si può fare in una sessione cloud, e che va lasciato al PM, è la stampa. Va chiesta **una volta sola**, alla fine del piano, non a ogni task.

- [ ] **Step 5: aggiornare i documenti**

`docs/ARCHITECTURE.md` acquista il pacchetto `layout/` e i comandi nuovi. `docs/GRAPHIC_STANDARD.md` acquista la sezione sul telaio e sulla legenda. `README.md` mostra il comando `draw`. `PROJECT_STATE.md` registra stato, impronta nuova e debito residuo. `docs/ROADMAP.md` marca «partizionare semanticamente» e «implementare layout e instradamento deterministici» come fatti.

- [ ] **Step 6: verificare e committare**

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check src tests examples
.venv/bin/python -m mypy src tests examples
git status --short
git add src tests examples docs README.md PROJECT_STATE.md
git commit -m "feat: draw a plant on an A3 sheet, checked geometrically"
```

Expected: exit `0`; il totale sale a circa 281; `git status` vuoto dopo il commit.

---

## 6. Copertura della specifica

| Area della specifica | Copertura |
|---|---|
| §7.2 modello geometrico derivato | Task 8, `layout/geometry.py` |
| §7.3 componenti in linea che spezzano la connessione | Task 5, Task 10 |
| §10.1 ordine della pipeline | Task 6 prima di Task 8, per costruzione |
| §10.2 layout deterministico, limiti di iterazione, diagnostica | Task 8, Task 9 |
| §10.3 multi-tavola semantico e rimandi | Task 6 |
| §11.1 spazio carta e grandezze in mm | Task 4 |
| §12.2 controlli geometrici | Task 12 |
| §12.4 controllo visivo | Task 7 Step 4, Task 12 Step 4 |
| §13 diagnostica azionabile | Task 8, Task 9, Task 10 |
| D-041 fasce e costo dell'incrocio | Task 8, Task 9 |
| D-042 piano di impaginazione registrato nel modello | Task 3, Task 8 |
| D-049 rotazioni ammesse applicate | Task 2 |
| D-050 gerarchia dimensionale | Task 7 |
| D-051, D-052 nomenclatura e legenda | Task 11 |
| W2 percorso di migrazione dello schema | Task 3 |
| W4 componente in linea esercitato | Task 5, Task 10 |
| Cartiglio compilato, PDF, distinta, preflight | Piano successivo |
| Motore delle regole | Piano successivo (D-040) |

## 7. Vincoli da non violare

Chi eseguirà questo piano deve sapere che queste **non** sono sviste.

1. **`render_symbol_sheet` non si estende.** È il banco di prova della libreria. La tavola è un altro renderer, in `graphics/sheet.py`.
2. **`symbols` resta opzionale in `ComponentRegistry.from_directory`.** Il validatore topologico lavora sulla sola semantica. È `resolve` a pretendere la libreria, e solo chi disegna chiama `resolve`.
3. **Il modello tecnico non acquista coordinate.** Acquista il piano di impaginazione, che è fatto di scelte discrete. Se un task si trova a voler scrivere millimetri nel `ProjectModel`, ha sbagliato strada.
4. **L'incrocio resta più economico del giro.** La disuguaglianza `CROSS_COST < 2 * STEP_COST` è sotto test proprio perché una futura taratura non la rompa senza accorgersene.
5. **Le porte restano sul perimetro** (D-044) e ora anche **sui nodi di griglia** (D-054). La seconda regola vive nel layout, non nel manifesto, perché `SymbolManifest` non conosce `GraphicStandard`.
6. **Il fingerprint del progetto misto cambia una volta**, al Task 3, e il valore nuovo va registrato. Cambiarlo di nuovo più avanti è un difetto, non un aggiornamento.

## 8. Self-review checklist

- [ ] Ogni requisito del piano ha almeno un test.
- [ ] Nessuna funzione, fixture o costante contiene un nome di schema tipo come ramo logico.
- [ ] Nessun valore dimensionale compare come numero anonimo.
- [ ] Ogni porta di simbolo sta sul perimetro **e** su un nodo di griglia.
- [ ] Nessuna linea passa sotto un componente in linea.
- [ ] Nessun oggetto esce dall'area utile; nulla è disegnato sopra la riserva del cartiglio.
- [ ] La legenda contiene i soli simboli usati; il corpo non ripete alcuna denominazione.
- [ ] Ogni rimando fra tavole ha esattamente un gemello.
- [ ] Stesso ingresso, stessa geometria e stesso SVG, byte per byte, con `PYTHONHASHSEED` variabile.
- [ ] Il gate G0 di P0 continua a passare.
- [ ] `pytest`, Ruff e mypy hanno exit code `0` su `src`, `tests` ed `examples`.
- [ ] La tavola del caso D-011 è stata **guardata**, non solo misurata.
- [ ] `git status --short` è vuoto dopo l'ultimo commit.

## 9. Cosa questo piano non fa

- Non compila il cartiglio: ne riserva lo spazio. Template vettoriale, campi obbligatori e blocco della tavola finale incompleta sono del piano di rendering.
- Non produce PDF. SVG resta il formato intermedio; il PDF è del piano successivo, con il manifest di riproducibilità.
- Non produce la distinta quantitativa.
- Non applica regole impiantistiche: disegna esattamente ciò che il modello contiene, senza aggiungere accessori (D-040).
- Non tocca A1 e A0: restano alternative secondarie (D-019), e nulla nel telaio impedisce di aggiungerle poi.
- Non affronta i colori del rendering oltre alla codifica delle reti necessaria alla legenda.

---

## Appendice — deviazioni approvate durante l'esecuzione

*Da compilare durante l'esecuzione.* Come per i due piani precedenti, questa appendice diventerà la fonte autorevole sulle differenze fra il piano e il codice consegnato, e va letta al posto del corpo.

A differenza dei due piani precedenti, il codice riportato nei Task 2, 5 e 9 **è stato eseguito prima di essere scritto qui**, insieme alle proprie prove, contro la libreria di simboli reale: otto prove verdi sulla rotazione, sei sulle tratte, undici sull'instradamento. Anche le due modifiche che rompono test esistenti — l'invariante dell'interruzione di linea e il margine sinistro — sono state applicate in prova alla suite completa, e i test che ne cadono sono nominati uno per uno nei rispettivi task. Restano non eseguiti i Task 1, 3, 4, 6, 7, 8, 10, 11 e 12: là il rischio di difetti nel testo del piano è quello di sempre.
