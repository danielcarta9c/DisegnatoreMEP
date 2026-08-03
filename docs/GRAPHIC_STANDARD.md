# Standard grafico — Disegnatore MEP

Questo documento descrive come vive, in codice, lo standard grafico costruito per trasformare un modello tecnico approvato in una tavola tecnica stampabile: dove sono definite le grandezze in millimetri, come è fatto il manifesto geometrico di un simbolo, come si separa dalla semantica del catalogo, come si aggiunge un simbolo alla libreria, come si compone un simbolo composito da primitive e come si verifica per stampa il foglio di riscontro. Copre l'esito dei Task 1-7 del piano `docs/plans/2026-08-03-graphic-system-symbol-library-plan.md`. Non copre layout, instradamento, multi-tavola, cartiglio o distinta: sono oggetto del piano successivo (si veda D-033).

## 1. Un'unica autorità dimensionale

`src/disegnatore_mep/graphics/standard.py` è il solo punto in cui vivono le grandezze grafiche in millimetri di carta: dimensioni del foglio, margini, passo della griglia, spessori dei tratti, altezze di testo, distanza minima di rispetto. La classe `GraphicStandard` le dichiara come campi Pydantic con vincoli (positività, coerenza fra soglie) e l'istanza `A3_LANDSCAPE` è il valore concreto usato in tutto il progetto.

### 1.1 Le grandezze di `A3_LANDSCAPE`

| Campo | Valore | Motivazione |
|---|---|---|
| `sheet_width_mm` | 420.0 | Larghezza del formato A3 orizzontale, ISO 216 |
| `sheet_height_mm` | 297.0 | Altezza del formato A3 orizzontale, ISO 216 |
| `margin_left_mm` | 20.0 | Margine di rilegatura ISO 5457, maggiorato sul lato sinistro |
| `margin_right_mm` | 10.0 | Margine ISO 5457 sugli altri tre lati |
| `margin_top_mm` | 10.0 | Margine ISO 5457 sugli altri tre lati |
| `margin_bottom_mm` | 10.0 | Margine ISO 5457 sugli altri tre lati |
| `grid_mm` | 2.5 | Passo della griglia di allineamento per la disposizione dei simboli |
| `line_thin_mm` | 0.18 | Spessore del tratto sottile: contorni secondari, riquadro dell'area utile |
| `line_medium_mm` | 0.35 | Spessore del tratto medio: corpo dei simboli, barra di scala |
| `line_thick_mm` | 0.50 | Spessore del tratto spesso, riservato ai tracciati da enfatizzare |
| `text_small_mm` | 1.8 | Altezza minima di testo leggibile in stampa: etichette, quota della barra di scala |
| `text_normal_mm` | 2.5 | Altezza di testo corrente |
| `text_title_mm` | 3.5 | Altezza di testo dei titoli |
| `min_clearance_mm` | 2.0 | Distanza minima libera intorno a una porta (area di rispetto, `keep_out`) |

`usable_width_mm` e `usable_height_mm` sono proprietà derivate (foglio meno margini), non campi propri: `390.0` e `277.0` con i valori sopra. `GraphicStandard.geometry_is_coherent` verifica ad ogni costruzione che l'area utile sia positiva su entrambi gli assi e che le soglie di spessore e di testo crescano in ordine (sottile < medio < spesso, piccolo < normale < titolo).

### 1.2 Un'asimmetria voluta fra i due assi

`usable_width_mm` (390.0 mm) è un numero intero di passi di griglia da 2.5 mm (156 passi esatti). `usable_height_mm` (277.0 mm) non lo è (110.8 passi). Non è un difetto da correggere: i margini seguono ISO 5457 (rilegatura maggiorata a sinistra, gli altri tre lati uguali) e non sono stati alterati per far tornare anche l'asse verticale sulla griglia. Allineare entrambi gli assi richiederebbe cambiare i margini, che è una decisione di prodotto — non un dettaglio tecnico reversibile — e non è stata presa. `tests/graphics/test_standard.py` fissa esplicitamente entrambi i fatti: l'asse orizzontale è allineato, quello verticale no, per lo stesso motivo.

## 2. Dove vivono le grandezze dimensionali

La regola vale per l'intero progetto: nessun valore dimensionale può comparire come numero anonimo nel codice. Ma "vivere in `standard.py`" e "non essere anonimo" non sono la stessa cosa.

`standard.py` è l'autorità sulla **carta**: le grandezze che descrivono il foglio come supporto fisico e che qualunque disegno su quel foglio deve rispettare. Un modulo che disegna qualcosa di più specifico — per esempio `src/disegnatore_mep/graphics/svg.py`, che compone il foglio di riscontro della libreria simboli — può nominare le proprie costanti di impaginazione locali (`SCALE_BAR_MM`, `COLUMN_GAP_MM`, `ROW_GAP_MM`, `SCALE_BAR_TICK_HALF_MM`, `SCALE_BAR_LABEL_GAP_MM`, `SYMBOL_LABEL_GAP_MM`, `PORT_MARKER_RADIUS_MM` in `svg.py`), perché quelle misure appartengono a *quel* foglio — un layout a griglia di anteprima, non alla tavola tecnica finale — e non alla carta in generale. Ciò che resta vietato ovunque è il numero dimensionale senza nome: ogni costante deve essere dichiarata, con un nome che ne spieghi il ruolo, e vivere il più vicino possibile al modulo che la usa.

`GraphicStandard` non è stato esteso per portare anche queste costanti di impaginazione del foglio di riscontro. Farlo avrebbe mescolato due cose diverse: le grandezze della carta, che ogni tavola del progetto deve rispettare per essere stampabile e misurabile, e le scelte di layout di un singolo foglio di anteprima della libreria simboli, che potrebbero cambiare (per esempio la spaziatura fra colonne) senza che nulla della carta stessa cambi. `standard.py` resta quindi il modello load-bearing su cui la stampa dipende; `svg.py` resta libero di evolvere la propria impaginazione senza toccarlo.

## 3. Il manifesto: porte sul perimetro e rotazioni ammesse

`src/disegnatore_mep/graphics/symbol.py` definisce `SymbolManifest`: riquadro (`width_mm`, `height_mm`), porte (`SymbolPort`, con `face` e coordinate `x_mm`/`y_mm`), area di rispetto per lato (`KeepOut`), ancoraggi di etichetta (`LabelAnchor`), rotazioni ammesse e interruzione di linea per i componenti in linea (`inline_gap_mm`).

Ogni porta dichiara una `PortFace` (`left`, `right`, `top`, `bottom`) e una coordinata. Il validatore del manifesto (`geometry_is_coherent`) impone che la coordinata coincida esattamente con quella attesa per quella faccia — per `left`, `x_mm = 0`; per `right`, `x_mm = width_mm`; per `top`, `y_mm = 0`; per `bottom`, `y_mm = height_mm` — entro una tolleranza di `1e-6` mm per assorbire l'arrotondamento in virgola mobile. Una porta la cui coordinata cade all'interno del riquadro, anche di poco, è respinta.

### 3.1 Perché sostituisce il vincolo P0

La fondazione (P0) dichiarava esplicitamente il contrario, e lo elencava fra i vincoli da **non** violare per sviste: *"Le porte possono stare ovunque dentro il riquadro del simbolo, non solo sul perimetro"* (`docs/plans/2026-08-01-foundation-core-plan.md`, sezione "Vincoli da non violare"), motivato dal fatto che un test P0 approvato definiva una porta al centro di un simbolo 10×10.

Questo piano ritira quel vincolo, deliberatamente. Una porta al centro di un simbolo non è un punto a cui una tubazione disegnata possa realisticamente attaccarsi: geometricamente valida, ma priva di significato per un disegno che deve poi instradare connessioni ortogonali fino al bordo dei componenti. La regola perimetro-faccia non è quindi un irrigidimento imprevisto del codice P0, né una svista che rompe un vincolo dichiarato: è la ragione stessa per cui questo piano esiste, registrata come "Decisione strutturale" nel piano e qui riportata perché chi legge questo documento sappia che il cambiamento è intenzionale, non un incidente da segnalare.

### 3.2 `allowed_rotations_deg`: un vincolo tecnico, non geometrico

`allowed_rotations_deg` elenca gli orientamenti in cui il simbolo può essere disegnato **in un impianto reale**. Non dice quali rotazioni siano geometricamente possibili — tutte e quattro lo sono sempre, per qualunque riquadro — ma quali siano tecnicamente corrette su una tavola. È quindi un vincolo impiantistico, deciso da chi conosce il componente, non una proprietà derivabile dalla forma. Il validatore impone soltanto che i valori appartengano a `{0, 90, 180, 270}`, che ce ne sia almeno uno e che non si ripetano: quali siano, lo dichiara chi autora il simbolo.

Dieci dei dodici simboli pubblicati dichiarano tutti e quattro gli orientamenti. Due no, e sono l'esempio di cosa significhi il campo:

| Simbolo | Rotazioni | Perché |
|---|---|---|
| `air-vent` | `[0]` | Uno sfiato d'aria automatico scarica verso l'alto. Una tavola che lo mostra rivolto in basso o di lato è sbagliata. |
| `expansion-vessel` | `[0, 180]` | Un vaso di espansione a membrana si disegna in piedi, non coricato. |

**Cosa resta da risolvere a chi consumerà il campo.** Questo ramo dichiara le rotazioni ammesse; non le applica. Ruotare un simbolo di 90° o 270° scambia il suo riquadro — `expansion-vessel` è 6×10 mm e ruotato occuperebbe 10×6 mm — e nulla qui esegue quella trasformazione, né ruota una `PortFace` (una porta `left` ruotata di 90° non è più a sinistra) né un lato di `KeepOut`. Il piano di layout possiede quel lavoro; è annotato qui perché chi lo affronterà non dia per scontato che il manifesto lo faccia già.

## 4. Geometria del simbolo, semantica del catalogo

In P0 `ComponentDefinition` portava sia la geometria sia la semantica delle porte, e `symbol_id` puntava a una libreria che non esisteva ancora. Due definizioni con lo stesso `symbol_id` potevano dichiarare geometrie fra loro incoerenti, senza che nulla se ne accorgesse.

Da questo piano in avanti la geometria si sposta interamente nel simbolo; la definizione di componente del catalogo (`src/disegnatore_mep/catalog/schema.py`) conserva solo la semantica:

| Vive nel **simbolo** | Vive nella **definizione di componente** |
|---|---|
| larghezza e altezza in mm | dominio della porta |
| posizione delle porte sul perimetro e loro faccia | fluido della porta |
| area di rispetto per lato | verso del flusso |
| ancoraggi di tag e descrizioni | porta obbligatoria sì/no |
| rotazioni ammesse | numero massimo di connessioni |
| interruzione di linea per i componenti in linea | funzioni, versione, fonti |

Le due parti si uniscono per identificativo di porta: `ComponentDefinition.port_ids` e `SymbolManifest.port_ids` devono coincidere esattamente. `ComponentRegistry` (`src/disegnatore_mep/catalog/registry.py`) esegue questa verifica incrociata quando viene costruito con un `SymbolRegistry` opzionale: se il `symbol_id` di una definizione non esiste nel registro dei simboli, o se l'insieme delle porte non coincide da un lato o dall'altro del confronto, il caricamento fallisce con `CatalogError` invece di produrre silenziosamente un catalogo incoerente.

Il parametro `symbols` resta opzionale per scelta: il validatore topologico (`src/disegnatore_mep/validation/topology.py`) funziona sulla sola semantica quindi un progetto puo' essere validato senza avere la libreria dei simboli sotto mano. La CLI `validate` accetta pero' un `--symbols` opzionale: quando lo si passa, la verifica incrociata viene eseguita; quando manca, il comportamento e' quello di sempre. Perché l'opzionalità non lasci comunque una libreria di fatto mai verificata, `tests/acceptance/test_foundation_cli.py::test_foundation_catalog_matches_its_symbols` carica il catalogo di fondazione **insieme** a `SymbolRegistry.from_directory(examples/foundation/symbols)` e pretende che la verifica incrociata passi per tutte le otto definizioni: un futuro `symbol_id` che punti a un simbolo inesistente, o una porta rinominata su un solo lato del confronto, fanno fallire questo test invece di essere spediti senza che nulla lo dica.

## 5. Come aggiungere un simbolo alla libreria

Un simbolo pubblicato è una coppia di file nella stessa cartella: `<id>.json` (il manifesto, validato da `SymbolManifest`) e `<id>.svg` (il corpo grafico). Per aggiungerne uno:

1. **Scegliere `id`, `version`, `name`.** `id` segue `^[a-z][a-z0-9_-]*$` e deve coincidere con il nome dei due file; `version` segue SemVer (`\d+\.\d+\.\d+`).
2. **Fissare il riquadro e le porte.** `width_mm`/`height_mm` in millimetri fisici; ogni porta dichiara la propria `face` e la coordinata coerente con quella faccia (si veda §3) — due porte possono condividere la stessa faccia a posizioni diverse. Un componente in linea (due porte su facce opposte) dichiara `inline_gap_mm` pari alla propria larghezza. Dichiarare anche `allowed_rotations_deg` (§3.2): gli orientamenti tecnicamente corretti per quel componente, non tutti quelli geometricamente possibili.
3. **Fissare `keep_out`** almeno pari a `A3_LANDSCAPE.min_clearance_mm` sui lati che portano una porta, `0` sugli altri: è lo spazio libero minimo perché una connessione possa raggiungere la porta senza toccare un altro oggetto. La regola è divisa in due, per competenza. Il manifesto **impone** che ogni faccia che porta una porta abbia `keep_out` maggiore di zero: è l'invariante che gli appartiene, perché `SymbolManifest` non conosce il `GraphicStandard` e non può quindi pretendere un valore specifico in millimetri. Il valore concreto — `min_clearance_mm` — lo fissa chi genera il simbolo. Entrambi i generatori lo **derivano dalle porte del simbolo** invece di riceverlo come elenco parallelo di nomi di lato: un refuso in quell'elenco (`"rigth"`) non produceva alcun errore e spediva in silenzio un simbolo con area di rispetto nulla, che l'instradamento avrebbe accostato a un oggetto vicino.
4. **Disegnare il corpo SVG** come frammento senza radice `<svg>` propria (viene inserito dentro un gruppo del foglio che lo ospita), in coordinate locali in millimetri con l'origine nell'angolo in alto a sinistra del riquadro. Il corpo non dichiara mai il proprio `stroke`: spessore e colore sono decisi dal foglio ospitante. Il corpo deve restare dentro il riquadro dichiarato e i tratti di attacco devono raggiungere esattamente le porte dichiarate.
5. **Validare prima di scrivere.** Costruire il dizionario del manifesto e chiamare `SymbolManifest.model_validate(...)` prima di scrivere qualunque file: un manifesto non valido non deve mai arrivare su disco. `examples/graphics/build_symbols.py` (libreria pubblicata, dodici simboli in `assets/symbols/`) ed `examples/foundation/build_fixtures.py` (simboli di fixture, in `examples/foundation/symbols/`) sono i due generatori esistenti: hanno proprietà e cicli di vita separati — la libreria pubblicata non contiene artefatti di prova — ma seguono lo stesso schema (dizionario tipizzato, validazione, scrittura).
6. **Rigenerare e verificare il determinismo.** Rieseguire lo script generatore e controllare che `git status --short <cartella>` non mostri differenze: la generazione deve essere riproducibile bit per bit, senza timestamp, ordine di dizionario o rappresentazione in virgola mobile che vari da un'esecuzione all'altra.
7. **Verificare che il registro carichi la libreria** con il conteggio atteso, per esempio `SymbolRegistry.from_directory(percorso).all()`.
8. **Guardare il simbolo, non solo misurarlo.** Renderizzare il foglio di riscontro (§7) e controllare a vista che il simbolo sia riconoscibile: un simbolo che valida ma non si legge ha comunque fallito. Il Task 6 ha scoperto così che una prima versione del simbolo del filtro a Y si leggeva come il segnale internazionale di divieto, non come un filtro, ed è stata ridisegnata.

### 5.1 I dodici simboli sono un insieme di prova, non la libreria definitiva

I dodici simboli in `assets/symbols/` servono a dimostrare che il meccanismo funziona su quattro domini: non sono la libreria che verrà usata in produzione. In particolare **le loro dimensioni sono una convenzione di prova, non una regola da ereditare**: 6×6 mm per i componenti in linea, 8×8 mm e 6×10 mm per gli altri sono taglie scelte per avere una libreria uniforme e misurabile, non perché quelle misure significhino qualcosa.

Nella libreria reale la dimensione porta significato. In una tavola tecnica la taglia di un simbolo comunica il peso del componente nell'impianto: una valvola si disegna piccola, un vaso di espansione più grande, un accumulo più grande ancora. La libreria definitiva dovrà quindi avere una gerarchia dimensionale coerente con l'importanza del componente. Quella gerarchia non è stata progettata qui: è un ingresso di progetto registrato per il piano successivo, e la taglia uniforme di questi dodici non va scambiata per lo standard.

## 6. Simboli compositi: un prodotto, un simbolo

Un prodotto che integra più funzioni — un gruppo di riempimento che porta valvola, filtro e ritegno in un solo corpo — viene disegnato con **un solo simbolo riconoscibile**, non con più simboli annidati (D-016), e conta **una sola volta nella distinta** (D-031). Il fatto che internamente sia assemblato da primitive riusabili è un dettaglio di autoraggio: non è visibile né a chi legge la tavola, né a chi conta i componenti da acquistare.

`src/disegnatore_mep/graphics/composite.py` fornisce questa via. `CompositeSpec` descrive l'assemblaggio, `compile_composite(spec, symbols)` lo compila in un `Symbol` — manifesto più corpo SVG — usando un `SymbolRegistry` come fonte delle primitive.

### 6.1 Come si autora un composito

1. **Riquadro e rotazioni** come per un simbolo scritto a mano: `id`, `version`, `name`, `width_mm`, `height_mm`, `allowed_rotations_deg`, `source`.
2. **Le parti** (`parts`): per ciascuna, il `symbol_id` della primitiva nel registro e lo scostamento `offset_x_mm`/`offset_y_mm` rispetto all'angolo in alto a sinistra del riquadro del composito. Una parte che sporge dal riquadro è respinta.
3. **Le porte esposte** (`exposed_ports`): quali porte delle parti diventano porte del composito, con l'indice della parte, l'identificativo della porta di origine e il nuovo identificativo (`as_id`). Le porte non esposte spariscono: sono interne al prodotto. Ogni porta esposta viene traslata dello scostamento della sua parte e deve cadere sul perimetro del composito (§3), altrimenti la compilazione fallisce.
4. **`inline_gap_mm`, `keep_out`, `label_anchors`** si dichiarano **esplicitamente sulla specifica**, con gli stessi valori di default del manifesto (`keep_out` a zero, `inline_gap_mm` assente, nessun ancoraggio). Non sono dedotti dalle parti, e la ragione è di sostanza, non di comodità:
   - l'area di rispetto di un composito non è l'unione di quelle delle sue parti: una parte interna al riquadro non contribuisce nulla all'involucro esterno, e la sua area di rispetto interna non deve gonfiare quella del composito;
   - l'interruzione di linea appartiene al composito intero — un gruppo da 16 mm costruito con due primitive in linea da 6 mm interrompe la connessione per 16 mm, non per 6 né per 12: nessuna somma o massimo delle parti dà il numero giusto;
   - gli ancoraggi di etichetta di un composito sono quelli dell'unico prodotto: unire quelli delle parti produrrebbe ancoraggi privi di senso e, con due primitive uguali, identificativi duplicati che il manifesto respinge.

   La conseguenza pratica è che un composito in linea va dichiarato tale: un gruppo assemblato da primitive in linea che non dichiari il proprio `inline_gap_mm` risulta **non** in linea, e l'instradamento gli disegnerebbe attraverso una linea continua invece di spezzare la connessione — esattamente ciò che D-027 vieta.

### 6.2 Il risultato è un simbolo come gli altri

`compile_composite` non produce una categoria a parte: costruisce un `SymbolManifest` e lo fa validare dalle stesse regole di §3 e §5. Un composito in linea deve quindi soddisfare davvero la regola delle due porte opposte e avere un `inline_gap_mm` non superiore alla propria larghezza, come qualunque simbolo scritto a mano; se non ci riesce, la compilazione fallisce invece di pubblicare un manifesto incoerente. Il corpo SVG è la concatenazione dei corpi delle parti, ciascuno annidato in un gruppo traslato del proprio scostamento.

Da lì in avanti, per il registro, per il foglio di riscontro e per chiunque consumi la libreria, un composito compilato è **indistinguibile** da un simbolo scritto a mano: stessa classe, stessi campi, stessi invarianti.

## 7. Il foglio di riscontro: comando, stampa, cosa misurare

Il comando CLI `symbols-sheet` carica una cartella di simboli e scrive un foglio SVG A3 a misura reale:

```bash
.venv/bin/python -m disegnatore_mep symbols-sheet outputs/symbols.svg --symbols assets/symbols
```

Il foglio (`src/disegnatore_mep/graphics/svg.py::render_symbol_sheet`) dichiara `width="420mm"` / `height="297mm"` e un `viewBox="0 0 420 297"` numericamente identico: un'unità utente SVG corrisponde esattamente a un millimetro di carta, senza fattori di scala nascosti nella trasformazione. Ogni simbolo compare una sola volta, con il proprio identificativo (`data-symbol-id`), i marcatori delle porte e un'etichetta; una barra di scala di 100 mm compare in basso a sinistra, ancorata al margine.

Per verificarlo fisicamente:

1. Aprire il file SVG in un browser.
2. Stamparlo su carta A3 **senza adattamento alla pagina** ("scala 100%", non "adatta al foglio").
3. Misurare con un righello la barra di scala: deve misurare **100 mm** esatti. Se misura di meno, la stampa ha applicato un adattamento non voluto e la prova va ripetuta con le impostazioni corrette.
4. Controllare a vista che ogni simbolo sia riconoscibile da un termotecnico e che le porte cadano visibilmente sul perimetro del proprio riquadro, non al suo interno.

Questo è il vero gate della fase: i controlli automatici (validazione del manifesto, XML ben formato, nessun simbolo fuori dall'area utile, capacità del foglio) dimostrano che nulla si sovrappone o esce dai margini, non che il disegno sia leggibile. Solo la prova di stampa risponde a quella domanda, coerentemente con l'immutabilità di scala richiesta al sistema (ADR 0003): le dimensioni stampate non devono ridursi in funzione della complessità o del numero di simboli sul foglio.
