# Il DXF per AutoCAD: che cosa si scrive, e da quale fonte

**Data:** 26 settembre 2026 · **Serve a:** `REL-004`, cioè I-138 e I-139 · **Stato:** proposta, applicata
ai DXF delle sei tavole approvate; **la decisione si scrive dopo che il PO li ha aperti in AutoCAD** ·
**Note di partenza:** [buone pratiche AutoCAD e DXF](../research_notes/DXF%20per%20AutoCAD/buone-pratiche-autocad.md),
[layer, spessori, testi e blocchi dalle norme](../research_notes/DXF%20per%20AutoCAD/layer-spessori-testi.md)

**Lo studio non ha un riferimento CAD** (I-138): se ne crea uno. Il PO ha fissato quattro cose — **blocchi
per i simboli**, **linee col loro tratteggio**, **frecce già sulle linee**, un file **che si apre in
AutoCAD senza lavoro** — e poi due: **stampa sempre a colori**, **AutoCAD 2020, formato 2013 o successivo**
(I-139). Il resto viene dalle buone pratiche documentate, ogni scelta con la sua fonte. I marcatori sono
quelli delle note: **[V]** verificato su una fonte, **[M]** misurato qui, **[D]** deduzione, **[I]** incerto.

*Come è stata fatta.* Due agenti di ricerca in parallelo (D-152), ciascuno in una cartella fuori dal
repository: uno sulle pratiche AutoCAD e sul formato, con un DXF di prova e il giro con l'ODA File
Converter; uno sulle norme e sulle convenzioni dei layer. La sessione ha riletto le due note, ha scritto lo
scrittore (`src/disegnatore_mep/graphics/dxf.py`) e **l'ha poi confrontato con la proposta delle note**: tre
punti mancavano — il colore di ripiego, il cartiglio in spazio carta, il file che si apre sulla
presentazione — e sono stati aggiunti prima di mandare i DXF al PO.

## Formato e spazi

- **AutoCAD 2013 (AC1027).** Lo aprono AutoCAD e AutoCAD LT dal 2013 in poi; ha già spessori (R2000),
  colori esatti (R2004), testo UTF-8 (R2007), presentazioni e immagini [V: Autodesk, *AutoCAD drawing file
  format* e codici di versione; ezdxf, *True Color* e *Lineweights*].
- **Millimetri**: `$INSUNITS = 4`, `$MEASUREMENT = 1` [V: Autodesk, INSUNITS e MEASUREMENT]. ezdxf di suo
  scrive **metri** [V: sorgente ezdxf 1.4.4].
- **Lo schema nello spazio modello, a 1:1 in millimetri di carta**, con l'origine nell'angolo in basso a
  sinistra del foglio: a 1:1 coincidono tutte le scale — tratteggi, testi, spessori [D].
- **Squadratura e cartiglio nello spazio carta** [V: Gruppo CAP, specifiche di restituzione; D]: nello
  spazio modello resta lo schema, che si copia in un altro disegno senza portarsi dietro il cartiglio.
- **Una presentazione per formato** (`A3`, `A2`): margini zero, `DWG To PDF.pc3`, scala 1:1, una finestra
  1:1 **con lo zoom bloccato** su un layer che non si stampa [V: Autodesk, *Getting Started — Layout*:
  «create all viewport objects on a separate layer»; DXF, VIEWPORT 90 bit 16384 e LAYER 290]. **Il file si
  apre sulla presentazione** (`$TILEMODE = 0`): si vede la tavola come nel PDF.

## Layer

| layer | contiene | colore | tratto | spessore |
|---|---|---|---|---|
| `M-HWTR-SPLY`, `M-HWTR-RETN` | riscaldamento, mandata e ritorno, con frecce e scavalli | della tavola | continuo | 0,35 |
| `P-DOMW-CPIP` | acqua fredda sanitaria | della tavola | il tratteggio della tavola | 0,35 |
| `P-DOMW-HPIP`, `P-DOMW-RPIP` | acqua calda sanitaria e ricircolo | della tavola | continuo | 0,35 |
| `M-SOLR-SPLY`, `M-SOLR-RETN` | circuito solare | magenta (D-187) | continuo | 0,35 |
| `M-DIAG-EQPM` | i simboli, come blocchi | nero/bianco (7) | continuo | 0,35 |
| `M-ANNO-IDEN`, `M-ANNO-TEXT` | sigle e richiami; testi e rimandi | 7 | continuo | 0,18 |
| `M-ANNO-LEGN` | legenda | 7 | continuo | 0,18 |
| `G-ANNO-TTLB` | squadratura, cartiglio, logo | 7 | continuo | 0,18 |
| `G-ANNO-NPLT` | il bordo della finestra, **non si stampa** | 7 | continuo | 0,18 |

- **I nomi** seguono le linee guida dei layer dello US National CAD Standard (AIA CAD Layer Guidelines):
  disciplina, gruppo, sottogruppo; `HWTR`, `DOMW`, `CPIP`, `HPIP`, `RPIP` sono scritti lì [V]. `SOLR` è
  un codice del progetto, che le linee guida ammettono se documentato [V]. **ISO 13567** fissa la
  struttura dei nomi, non i codici degli impianti [V]: le linee guida si leggono come fonte, non come norma.
- **La descrizione in italiano** sta nella descrizione del layer [V: AEC (UK), «Always remember to
  utilise the layer description»]. Che AutoCAD la mostri nel gestore dei layer va visto [I].
- Refrigerata, gas, refrigerante, aria e condensa hanno i loro layer (`M-CWTR-*`, `M-NGAS-PIPE`,
  `M-REFG-*`, `M-HVAC-*`, `M-CNDS-PIPE`) quando una tavola li disegna.

## Colori, tratteggi, spessori

- **Il colore esatto della tavola** (codice 420) sui layer delle reti (I-139). Accanto, **un colore
  d'indice di ripiego** (codice 62), il più vicino in distanza RGB sulla tavolozza di ezdxf [D; M: la nota
  sui layer, appendice A.3]: AutoCAD usa il colore esatto, che vince [V: ezdxf, *True Color*]; il ripiego
  serve a chi non legge il 420. Anche l'ODA File Converter, quando riscrive il file, mette un ripiego, col
  suo criterio [M].
- **Un CTB non governa i colori esatti**: anche con `monochrome.ctb` escono a colori [V: Autodesk, *Black
  and white (monochrome/grayscale) CTB plots color*]. Lo studio stampa a colori (I-139): va bene così. Se un
  giorno servisse il bianco e nero, i rimedi documentati sono gli stili con nome (STB) o i colori d'indice.
- **Il tratteggio** è un tipo di linea definito nel file, **in millimetri uguali a quelli della tavola**
  (`NOVEC_TRATTO_3_2`: 3 pieno, 2 vuoto), con `LTSCALE = PSLTSCALE = CELTSCALE = 1`; le polilinee lo
  generano **di continuo sui vertici** (flag 128, PLINEGEN) [V: Autodesk DXF, LWPOLYLINE; D].
- **Gli spessori** sono quelli della tavola approvata, tutti nella serie di ISO 128-2 e tutti fra i valori
  che il DXF ammette [V]; `$LWDISPLAY = 1` li mostra all'apertura.

## Blocchi, frecce, testi, logo

- **Un blocco per simbolo**, `NoveC_` più il tipo in CamelCase dall'id della libreria
  (`pump-circulator` → `NoveC_PumpCirculator`) [V: BS 8541-1, opzione `Source_Type`, tramite AEC (UK)]; il
  più lungo ha 29 caratteri, tutti validi anche con `EXTNAMES = 0` [M]. Il nome italiano nella descrizione
  del blocco. Dentro, **layer 0, colore e spessore DaBlocco**: l'aspetto lo decide l'inserimento [V:
  Autodesk, *Block Object Properties Reference*]. Le lettere degli strumenti, che la tavola tiene diritte
  (I-033), sono un blocco a parte inserito diritto.
- **Le frecce del verso** sono un blocco, `NoveC_FlowArrow`, inserito sulla linea, ruotato, **sul layer
  della sua rete** [V: Autodesk, P&ID — «Flow Arrow» è un blocco; D]: prendono il colore della rete e si
  selezionano tutte per nome. Stanno dove le mette la tavola approvata.
- **I testi**: uno stile su `arial.ttf` (e il grassetto su `arialbd.ttf`), che ogni Windows ha [D].
  **L'altezza è tarata sulle maiuscole**: AutoCAD misura l'altezza sulle maiuscole, l'SVG sul corpo, e
  scrivere il corpo darebbe testi del 45 % più grandi della tavola [M: Liberation Sans, che ha le larghezze
  di Arial, maiuscole a 0,688 del corpo]. Che in AutoCAD la taratura torni si vede solo aprendo il file [I].
- **Il logo** è un'immagine **collegata, non contenuta**: il DXF le immagini non le contiene [V: ezdxf,
  *Image tutorial*]. Si consegna accanto al DXF e il DXF lo nomina senza percorso: AutoCAD lo cerca nella
  cartella del disegno [V: Autodesk, *About Changing the Path to Raster Images*]. Cornice dell'immagine
  spenta.

## Come si è verificato senza AutoCAD

- **L'audit di ezdxf**: nessun errore sulle sei tavole [M].
- **La geometria riletta dal DXF** contro quella della tavola: ogni tratta di ogni rete sul suo layer, e
  ogni simbolo come inserimento del suo blocco, **uguali entro un milionesimo di millimetro** sulle sei
  tavole [M: `docs/collaudi/REL-004/collaudo.py`].
- **Il giro con l'ODA File Converter** (DXF → DWG AutoCAD 2018 → DXF): i sei DWG escono in `AC1032`, e il
  ritorno è **identico** all'andata in layer, entità, blocchi, inserimenti, immagini, presentazione,
  stampa, finestre e stili; cambia solo il colore di ripiego, che ODA ricalcola. Le rese di andata e
  ritorno differiscono al più di 36 pixel su 1653 × 1169, sfumature di bordo [M:
  `docs/collaudi/REL-004/giro_oda.py`].
- **Due difetti trovati così, e corretti** prima dell'invio: ezdxf mette la finestra principale della
  presentazione su un layer `VIEWPORTS` che non definisce — l'audit non lo vede, il giro ODA sì —; e lo
  stesso piano dava due file diversi in due esecuzioni, perché ezdxf mette in fila le classi del file
  scorrendo un insieme [M].

## Che cosa non si è fatto, e che cosa resta da vedere

- **Le sigle sono testi**, sul loro layer, **non attributi dei blocchi**: con gli attributi AutoCAD può
  estrarre gli elenchi dei componenti, ma serve solo se lo studio li usa [D]. Il cartiglio non è un blocco,
  e il logo è un'immagine, non un disegno vettoriale.
- **Da vedere in AutoCAD** (le note, §«Incertezze»): che il file si apra sulla presentazione; che il nome
  della carta `ISO_full_bleed_A3_(420.00_x_297.00_MM)` esista nel `DWG To PDF.pc3` dello studio [I]; che i
  testi Arial abbiano l'altezza della tavola; che il logo si trovi; che la descrizione dei layer si veda.
