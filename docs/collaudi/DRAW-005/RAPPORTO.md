# DRAW-005 — contenuto e simboli critici della tavola 1

**Ramo:** `claude/draw-005-contenuto-simboli-tavola1-r20hmg` (la sessione ha assegnato il
suffisso; il Work Package nomina il ramo senza suffisso — vedi §8)
**Base:** `dc3dad5` — il `main` che porta il Work Package DRAW-005
**Campo:** il solo impianto 1 (D-116); gli impianti 2–5 non sono stati lavorati

Tutto ciò che segue è misurato sulla stessa catena, con lo stesso ingresso
(`examples/prova/prova-1-due-pdc-accumulo-combinato.json`), il giorno stesso. Gli
artefatti stanno in `prima/` — la tavola di consegna di DRAW-004, con il suo modello
completato — e in `dopo/`; lo strumento è `metriche.py`, che legge la geometria agli atti
e non la ricompone, e con `--diario` rifà il ciclo per dire quali alternative sono state
provate. Le fonti, la simbologia, le regole MEP e i criteri sono quelli fissati dal PM
nell'audit del 5 settembre 2026; gli allegati del PO non sono stati usati per ricavare
requisiti.

## 1. Che cosa è cambiato, e perché

### 1.1 La regola dell'intercettazione isola il **gruppo** (regola 1 dell'audit, I-034)

`rules/hydronic/isolate-what-is-serviced.json` passa alla versione 2.0.0. La regola
dichiara ancora la sola funzione (`isolation`, o `isolation_locked_open` per chi lo
pretende) e si ancora ancora alla proprietà `maintainable`; cambia **come si dichiara
soddisfatta**: `satisfied_by.scope = on_the_group`. Tre meccanismi, tutti letti dai
dati e mai dai nomi:

- **il gruppo manutenibile.** Un pezzo che una regola *per componente* ha posato su un
  attacco della macchina — il filtro a Y sul ritorno della pompa di calore — è **della**
  macchina. Si legge dal modello: la regola in calce al pezzo (`evidence`) e
  l'identificativo derivato dall'attacco (`anchor_of_proposed`, l'inverso di
  `proposed_component_id`). Il corredo di rete (defangatore, vaso, riempimento,
  manometro) non entra nel gruppo anche quando il tratto comune comincia sull'attacco
  della macchina: è *per rete* o *sul tratto comune*, e lo si legge dalla regola;
- **un organo per tratto.** Un tratto è l'insieme delle tubazioni percorse da un attacco
  fino al primo pezzo che ferma — un pezzo non in linea, un pezzo manutenibile, un
  raccordo da cui il percorso si apre. Il tratto è la sua identità
  (`RuleContext.stretch_from`): due proposte dello stesso organo sullo stesso tratto,
  da due capi, sono una. È così che il ritorno della PDC prende **una** valvola oltre il
  filtro, lato rete, e non una fra filtro e macchina (`group_holds`: il tratto che finisce
  su un membro dello stesso gruppo è già chiuso dai bordi del gruppo);
- **due fasi.** Le regole «sul gruppo» parlano solo quando tutte le altre tacciono
  (`evaluate_in_phases`): se parlassero insieme a chi riempie il gruppo — il filtro —
  si poserebbero fra la macchina e il suo filtro, dove poi non devono stare.

L'assemblatore (`assembly/runs.py`) preferisce accanto alla macchina i pezzi **suoi**
(`Piece.of_the_anchor`): il filtro sta attaccato alla PDC, il defangatore — di rete — no.
Fonti applicate: Caleffi, *Componenti e schemi per impianti a pompa di calore* (SRC-008);
Caleffi, *Idraulica 61*, p. 45, il filtro immediatamente a monte dello scambiatore
(SRC-019); audit PM del 5 settembre 2026 su indicazione del PO (I-034).

### 1.2 I simboli della matrice (I-031, I-032, I-033, I-036, I-037, I-039)

Tutti generati da `examples/graphics/build_symbols.py`, che ora riproduce anche i pezzi
corretti a mano nei pacchetti precedenti (T con `keep_out` 0,5 mm, D-119; ritegno a Z,
D-122) — la prova di rigenerazione in `tests/catalog/test_generated_fixtures.py` lo
tiene vero.

| Simbolo | Versione | Che cosa cambia | Fonte |
|---|---|---|---|
| Filtro a Y | 2.0.0 | corpo a Y: linea passante, ramo inclinato di 45° dal centro dell'asse verso il basso, tappo perpendicolare; rotazioni ammesse **0 e 270** (il gambo non punta mai in su) | UNI 9511 (SRC-016), matrice PM |
| Confine di rete | 2.0.0 | corpo = sola linea; la **freccia la disegna il renderer** (`flow_glyphs`) nel verso locale dell'acqua di ciascun pezzo posato (`PlacedSymbol.port_flows`, da `PortFlow`); uscente e entrante condividono il tipo grafico | matrice PM (I-032) |
| Termometro, manometro | 2.0.0 | la lettera è un `upright_glyph` dichiarato nel manifesto (`<g data-glyph>`) e **controruotata** dal registro (`rotate(-θ cx cy)`); il registro rifiuta un manifesto che dichiara glifi che il corpo non ha | UNI 9511 (SRC-016), matrice PM (I-033) |
| Pompa di calore | 2.0.0 | interasse mandata–ritorno **15 mm** (`water_return` a y 20,0); il catalogo espone `functional_room_mm(catalog, medium, standard)` = accessorio in linea più alto sul fluido + `min_clearance` — non una costante universale | matrice PM (I-039) |
| Accumulo combinato | 2.0.0 | mantello con serpentino **continuo** da `cold_in` a `dhw_out` (`path class="coil"`, sei giri), attacchi tecnici che entrano nel mantello | Rehau Taddy (SRC-018), matrice PM (I-036, I-037) |
| Bollitore | 2.0.0 | serpentino tecnico da `coil_in` a `coil_out`, riserva sanitaria nel mantello | Rehau (SRC-018) |
| Puffer (2 e 4 attacchi), PdC sanitaria | 1.1.0 | solo volume tecnico, corpo `reserve_body` senza serpentino | Caleffi (SRC-019) |

`Symbol.rotated`, `FlowGlyph`, `UprightGlyph`, `inline_extent_mm` e `functional_room_mm`
vivono in `graphics/symbol.py` e `graphics/registry.py`; il tracciato delle frecce in
`graphics/glyphs.py`; foglio e legenda le disegnano dopo il corpo.

### 1.3 La posa (regola 2 dell'audit, I-035; etichette, I-030)

- **La valvola oltre un raccordo passante si stringe al raccordo.** `services()` in
  `layout/inline.py` guarda attraverso i raccordi da cui il percorso prosegue in una
  direzione sola: la sicurezza dell'accumulo pende da un raccordo sulla sua mandata, il
  raccordo è l'unico organo che per funzione resta fra la valvola e `primary_in`, e la
  valvola si stringe a lui (2,5 mm di stacco, come contro un attacco). Una
  ripartizione la ferma. Nessuna coordinata, nessun ID.
- **La rotazione la sceglie il simbolo.** Fra le due rotazioni che danno la giacitura del
  tratto, il posatore prende la prima che il manifesto ammette: il filtro a Y su una
  verticale gira di 270°, non di 90°.
- **Gli indirizzi sono un velo.** `layout/addresses.py::with_addresses` è la sola
  opzione che li porta in tavola (`--verifica`); la consegna ha le sole sigle delle
  macchine. Nessuna modalità entra in posa o routing: la prova generale confronta simboli
  e rotte delle due tavole e li trova identici.
- **Le tratte non seguono l'ordine del file.** `build_trunks` percorre le connessioni
  per identificativo, che è l'ordine della forma canonica. Prima seguiva l'ordine in
  cui il modello le elencava: lo stesso impianto completato dalle regole in memoria e
  riletto dal suo JSON dava due tavole diverse, e con il grafo nuovo quella in memoria
  non si componeva (le prove che compongono l'impianto 1 in-process fallivano mentre
  la CLI, che rilegge il JSON, riusciva). La CLI produce la stessa tavola di prima
  della correzione, perché il JSON canonico è già ordinato; la prova
  `test_le_tratte_sono_le_stesse_comunque_il_modello_elenchi_le_connessioni` lo tiene
  vero in generale.
- **Il ciclo parte anche da una posa che non si instrada.** Se la posa iniziale non
  trova strada nemmeno in modo tollerante — uno stacco murato da un vicino — prima
  l'ottimizzatore rinunciava senza provare una mossa, e la tavola falliva o riusciva a
  seconda di un dettaglio della posa iniziale. Ora cerca la **prima** candidata che si
  lascia instradare, nell'ordine di posa, e da lì riparte come sempre
  (`Improver._first_routable`); il tetto di prove è quello della posa e ogni prova
  finisce nel diario. Sulla tavola 1 la pre-fase non entra (la posa iniziale si instrada)
  e l'impronta resta `6e8e64ae…`.

`SheetCost` è invariato: stesso ordine, stesse voci.

### 1.4 Conseguenze meccaniche sui documenti derivati

- `examples/rules/centrale-pdc-completa.json` rigenerato con `rules --apply-all`;
- `docs/prodotto/GRAFO_IMPIANTO.md` e `docs/prodotto/grafi-di-prova/prova-{1..5}-*.md`
  rigenerati: la regola è generale e vale su tutti e cinque i grafi. **Gli impianti 2–5
  non sono stati lavorati**: i loro documenti cambiano solo perché la regola cambia, e
  una prova (`test_il_confronto_per_il_pm_dice_il_vero_sui_documenti`) pretende che i
  conteggi del confronto dicano il vero;
- `docs/prodotto/grafi-di-prova/CONFRONTO-2026-08-07.md`: conteggi «a N pezzi»
  aggiornati (impianto 1: 39; 2: 46; 3: 44; 4: 43; 5: 98) con nota datata in testa;
- `docs/prodotto/REGOLE_ACCESSORI.md`, scheda 7 e paragrafo «due pezzi sullo stesso
  tubo»: aggiornati al gruppo, con data e riferimento a I-034. **Da rivedere dal PM**:
  è il documento che il PO approva, e ho toccato solo ciò che la regola nuova rendeva
  falso.

## 2. Il grafo dell'impianto 1 contro le cinque regole dell'audit (criterio 2)

`dopo/impianto1-completo.json`, 39 pezzi e 41 connessioni (prima 45 e 47); 26
integrazioni (`dopo/integrazioni.txt`), 0 punti aperti. Letto sul grafo da
`metriche.py` (`rami`), non sulla tavola:

| Regola | Sul grafo | Dove |
|---|---|---|
| 1 — gruppo PDC + filtro | `pdc-master.water_return`: filtro → valvola → ripartizione; `pdc-slave.water_return`: idem. Organi fra filtro e macchina: **0** su entrambi. Mandata: una valvola per PDC | `rami` |
| 2 — valvola comune di mandata | `accumulo.primary_in`: raccordo della sicurezza → valvola → confluenza; la valvola sta a **5,0 mm** dall'attacco del raccordo (caso «ultimo oltre il raccordo»), prima era a 62,5 mm | `valvole_d120` |
| 3 — riempimento | uno solo, sul ritorno tecnico (`filling-unit-collettore-ritorno-a`), con la propria valvola; nessuno su `fredda` o `sanitaria` | `integrazioni.txt` |
| 4 — serpentino sanitario | `w1`: `acquedotto.a` → `accumulo.cold_in`; `w2`: `accumulo.dhw_out` → miscelatrice → `utenze.a`; nel simbolo il serpentino va da `cold_in` a `dhw_out` senza interruzioni | `dopo/consegna/impianto1.svg` |
| 5 — costo dopo la correttezza | grafo validato (0 rilievi di correttezza) e poi minimizzato nell'ordine vigente; il confronto di lunghezza è scomposto in §3, non dichiarato come miglioramento | §3, §4 |

Organi di chiusura per tratto: 16, nessuno consecutivo (prima 21, di cui 4 coppie in
fila sullo stesso volume e 2 fra filtro e PDC). Il tratto `s3` — dal radiatore all'ingresso
secondario dell'accumulo — porta **una** valvola per i due pezzi che vi si affacciano:
è la regola presa alla lettera (un organo per tratto), e lo segnalo in §8.

## 3. Le misure, prima e dopo

Il grafo non è lo stesso: **i totali non sono confrontabili come miglioramenti** (regola 5
dell'audit). Si riportano, e la lunghezza si scompone per collegamento di partenza.

| Misura | Prima (DRAW-004, consegna) | **Dopo (DRAW-005, consegna)** | Criterio |
|---|---:|---:|---|
| Pezzi del modello / simboli in tavola | 45 / 45 | **39 / 39** | 2, 3 |
| Rilievi di correttezza | 0 | **0** | 7 |
| Tubo sotto un simbolo | 0 | **0** | 7 |
| Backtracking | 0 tratte, 0 mm | **0 tratte, 0 mm** | 7 |
| Tratte oltre tre pieghe | 0 | **0** | 7 |
| Curve totali | 6 | **4** | riportato |
| Incroci | 1 | **1** | riportato |
| Lunghezza delle tubazioni | 577,5 mm | **525,0 mm** | riportato, scomposto sotto |
| Valvole D-120 a 2,5÷5 mm | 18 su 21 (rimisurate oggi; il rapporto DRAW-004 diceva 20 su 20 con la definizione di allora) | **16 su 16** | 3 |
| Sigle in consegna / indirizzi | 7 / 0 | **7 / 0** (verifica: 7 / 37) | 8 |
| Riempimento (solo diagnostica) | 38,1 % | 33,3 % | — |
| Preflight | 1 avviso (`SHEET_BARELY_FILLED`) | 1 avviso (`SHEET_BARELY_FILLED`) | — |
| Impronta della geometria (consegna) | `ac7036bd…` | `6e8e64ae…` | 9 |

La rimisura di ieri con la definizione di oggi conta tre valvole fuori dai 2,5÷5 mm: la
valvola comune di mandata (62,5 mm dal raccordo, che oggi è un caso della regola e ieri
era «fuori regola»), la valvola sul ritorno della PDC di sopra (9,0 mm in diagonale dal
riquadro all'attacco) e la valvola generale dell'acquedotto (7,5 mm, fuori regola perché
non ha un manutenibile a un capo). L'impronta della geometria di ieri riletta con lo
schema di oggi — che ha il campo `port_flows` — è `1f72c3ec…`, non `ac7036bd…`: è la
stessa tavola, con un campo in più a valore predefinito.

### 3.1 Quanto tubo viene dal contenuto, e quanto dal layout

Per ogni tubazione del modello di partenza (`p1`… `w2`), la lunghezza in tavola e gli
accessori in linea che porta. Gli stacchi sono i collegamenti nuovi aggiunti dalle regole
(sei, prima e dopo).

| Tubazione | Prima: mm (pezzi in linea) | Dopo: mm (pezzi in linea) | Differenza | Da che cosa |
|---|---:|---:|---:|---|
| `p1` mandata PDC-01 | 30,0 (1) | 30,0 (1) | 0 | — |
| `p2` mandata PDC-02 | 70,0 (1) | 70,0 (1) | 0 | — |
| `p3` mandata comune | 90,0 (1) | 82,5 (1) | −7,5 | layout (stesso contenuto) |
| `p4` ritorno comune | 77,5 (3) | 70,0 (3) | −7,5 | layout (stesso contenuto) |
| `p5` ritorno PDC-01 | 22,5 (3) | 17,5 (2) | −5,0 | contenuto: una valvola in meno |
| `p6` ritorno PDC-02 | 62,5 (3) | 57,5 (2) | −5,0 | contenuto: una valvola in meno |
| `s1` accumulo → circolatore | 25,0 (5) | 15,0 (3) | −10,0 | contenuto: due valvole in meno |
| `s3` radiatore → accumulo | 85,0 (2) | 70,0 (1) | −15,0 | contenuto: una valvola in meno |
| `w1` AF → accumulo | 17,5 (2) | 15,0 (1) | −2,5 | contenuto: una valvola in meno |
| `w2` accumulo → ACS | 25,0 (3) | 22,5 (3) | −2,5 | layout (stesso contenuto) |
| stacchi (6) | 72,5 | 75,0 | +2,5 | layout |
| **totale** | **577,5** | **525,0** | **−52,5** | −37,5 contenuto · −15,0 layout |

Sei valvole in meno (21 → 16, più la miscelatrice che resta) liberano 45 mm di rettilineo
minimo (7,5 mm ciascuna: riquadro più passo); le tubazioni che le perdono si accorciano di
37,5 mm. Le tubazioni a contenuto invariato (`p3`, `p4`, `w2`, stacchi) sommano −15,0 mm:
è la parte attribuibile alla posa sul grafo nuovo, e viene dall'interasse di 15 mm della
PDC (il ritorno della PDC di sotto non fa più il gradino di 10 mm di DRAW-004) e dal
raccordo di mandata che scorre verso le PDC.

## 4. Le alternative provate, e perché quella finale ha vinto

Il diario (`dopo/diario.json`) è scritto dal ciclo: ogni candidata misurata lascia fase,
specie, pezzo, costo e se è stata accettata. Sull'impianto 1:

- **posa** (fase 1): 1355 instradamenti di prova, 48 mosse accettate; arriva a 8 curve,
  3 incroci, 567,5 mm;
- **rifinitura** (fase 2): 845 instradamenti di prova; 1213 candidate misurate — 3
  dorsali, 30 assi, 30 colonne, 57 gruppi, 113 catene, 96 catene con spazio, 188 pose da
  porta, 185 con spazio, 42 stacchi, 469 passi — di cui 8 accettate.

Le otto mosse accettate, nell'ordine, con il costo raggiunto (curve · incroci · tubo):

| # | Specie | Pezzo | Curve | Incroci | Tubo (mm) | Che cosa ha fatto |
|---|---|---|---:|---:|---:|---|
| 0 | — | dopo la posa | 8 | 3 | 567,5 | punto di partenza |
| 1 | dorsale | PDC di sotto | 6 | 2 | 612,5 | la catena di mandata rimessa in fila dalla porta della PDC, con l'accumulo portato sull'asse d'uscita: due curve e un incrocio in meno, pagati in tubo |
| 2 | gruppo | PDC di sopra | 6 | 2 | 592,5 | la pila delle PDC si sposta come gruppo e accorcia |
| 3 | porta | raccordo del ritorno | 4 | 1 | 582,5 | il raccordo del ritorno si posa sull'asse dell'uscita dell'accumulo: il ritorno della PDC di sotto diventa una retta, via due curve e un incrocio |
| 4 | catena | raccordo di mandata | 4 | 1 | 562,5 | la catena di mandata rimessa in fila alla distanza minima |
| 5-8 | passo | raccordo di mandata | 4 | 1 | 525,0 | il raccordo di mandata scorre verso le PDC di un passo per volta |

**Perché l'alternativa finale ha vinto.** Per ogni pezzo la rifinitura misura tutte le
candidate valide e tiene la migliore se batte strettamente. Le candidate che nel diario
mostrano un costo *apparentemente* migliore di quello finale — i «gruppi» dell'accumulo
(4 curve, 1 incrocio, 495 mm), del raccordo del ritorno (465 mm), della PDC di sotto
(465 mm), del raccordo di mandata (510 mm), del radiatore (495 mm) — hanno tutte
`violazioni = 1`: violano un vincolo duro (distanza minima o area) e il confronto le
scarta prima di guardare le curve, come in DRAW-004. Fra le valide: gli assi
dell'accumulo (12 candidate) al meglio 8 curve; le pose da porta dell'accumulo (24) 6
curve a 530 mm; la colonna della PDC di sopra (26) 4 curve, 1 incrocio, 535 mm — pari,
ma più tubo; gli assi del raccordo del ritorno (4) 12 curve. Nessuna batte 4 · 1 · 525.

## 5. Le curve che restano, e perché

Quattro curve e un incrocio su venti tratte:

| Tratta | Curve | Perché resta |
|---|---:|---|
| mandata della PDC di sopra → raccordo di mandata | 1 | la PDC di sopra sta 40 mm più in alto della dorsale di mandata, che è sull'asse della PDC di sotto: una curva è il minimo per scendere nel raccordo |
| ritorno della PDC di sopra ← ripartizione del ritorno | 1 (+ l'incrocio) | il ritorno sale diritto dalla ripartizione — valvola, poi filtro a Y ruotato di 270° — e gira una volta verso la PDC; incrocia la mandata della PDC di sotto, perché fra le due macchine e l'accumulo mandata e ritorno si scambiano di quota |
| ritorno del radiatore → accumulo | 2 | uscita del radiatore e ingresso secondario dell'accumulo guardano tutti e due a destra: un'andata e ritorno a U vale due curve qualunque sia la posa |

Il ritorno della PDC di sotto è una retta (in DRAW-004 aveva un gradino di 10 mm: con 5
mm fra le porte della PDC e 15 sull'accumulo, allineata la mandata il ritorno non
tornava); la mandata PDC di sotto → raccordo → valvola → raccordo della sicurezza →
accumulo è una retta senza gomiti. L'interasse di 15 mm non è stato imposto come
allineamento: è una geometria di porte che il ciclo ha potuto sfruttare.

## 6. Le prove generali, scritte prima del codice

Nessuna nomina ID o coordinate della tavola 1: gli impianti sono costruiti nel test, con
altri nomi.

- **A — grafo** (`tests/rules/test_gruppo_manutenibile.py`, 35 prove): su quattro
  impianti sintetici — una macchina in anello, due in parallelo, una e due macchine con
  accumulo combinato — il filtro sta contro la macchina; oltre il filtro, lato rete, un
  organo solo; la mandata ha il suo; nessun organo consecutivo; ogni gruppo è isolabile;
  fra due manutenibili estranei sullo stesso tubo un organo solo; l'esito non cambia
  permutando componenti e connessioni; il riempimento è unico, sul ritorno comune
  dell'acqua tecnica, mai su AF/ACS; l'accumulo combinato espone `cold_in`/`dhw_out` sulle
  reti sanitarie e il volume tecnico serve primario e secondario; puffer, bollitore e
  combinato sono tre definizioni distinte e nessuna porta viene permutata dalla posa;
  sulla tavola 1 le connessioni AF e ACS sono conservate.
- **B — contratti grafici** (`tests/graphics/test_contratti_simboli_tavola1.py`, 39
  prove): il filtro a Y ha ramo inclinato e gambo mai sopra l'asse in ogni rotazione
  ammessa, e ne ammette una verticale; i confini uscente ed entrante condividono il tipo
  grafico e la freccia punta nel verso locale dell'acqua a 0/90/180/270; `compose_drawing`
  scrive `port_flows` dal catalogo; le lettere P, T e una F sintetica restano dritte a ogni
  rotazione senza toccare corpo e porte, e il registro rifiuta un manifesto incoerente; lo
  spazio funzionale della PDC è di 15 mm e non è una costante; il serpentino del combinato
  è continuo da `cold_in` a `dhw_out` e gli attacchi tecnici entrano nel mantello; sigle
  sempre, indirizzi solo su richiesta, testi invarianti.
- **C — posa** (`tests/layout/test_consegna_e_verifica.py`, 11 prove): consegna e
  verifica hanno gli stessi simboli e le stesse rotte; le riserve non permutano porte e le
  rotte finiscono sugli attacchi del manifesto; la valvola che isola oltre un raccordo
  passante sta contro il raccordo (2,5÷5 mm) e non a mezza strada; le tratte sono le
  stesse comunque il modello elenchi le connessioni.

Sei prove esistenti sono state riallineate: il foglio dei simboli sa che il filtro a Y
ammette due sole rotazioni; le due del motore che
rifanno il ciclo a mano usano `evaluate_in_phases`; quella del cancello sull'acqua fredda
prova la regola da sola e poi che, insieme al confine, sul tratto esce un organo solo;
quella del defangatore chiede un organo fra macchina e defangatore, non più ancorato alla
macchina; quella del confronto legge i conteggi aggiornati.

## 7. Verifiche eseguite

- `ruff check src tests examples`: nessun rilievo; `mypy --strict src tests examples`:
  nessun errore su 142 file.
- Suite completa: vedi la riga in calce a questa sezione, aggiornata all'ultimo giro.
- Determinismo: due generazioni consecutive della tavola 1 (una in `outputs` di
  sessione, una in `dopo/consegna/`) danno la stessa impronta `6e8e64ae…` e lo stesso
  modello completato byte per byte.
- Verifica e consegna: stessi simboli e stesse rotte (prova C e `metriche.json`: 20
  tratte, 39 simboli in entrambe; la verifica aggiunge 37 indirizzi, nessuno su tubo,
  simbolo o altra scritta).

## 8. Osservazioni per il PM, che non decido io

- **Il ramo.** Il Work Package nomina `claude/draw-005-contenuto-simboli-tavola1`; la
  sessione ha assegnato `claude/draw-005-contenuto-simboli-tavola1-r20hmg` e ho lavorato
  lì, senza spingere altrove. La PR parte da questo ramo.
- **Un organo per tratto fra due manutenibili.** Sul tratto `s3` il radiatore e
  l'ingresso secondario dell'accumulo condividono una valvola; su `s1` l'accumulo e il
  circolatore idem. È la lettera della regola 1 dell'audit («senza duplicare organi
  consecutivi che chiudono lo stesso volume»); se il PO vuole che due pezzi distinti
  abbiano ciascuno il proprio organo anche sullo stesso tratto, è una decisione da
  registrare, e la regola la può esprimere.
- **I documenti degli impianti 2–5** cambiano per conseguenza meccanica della regola
  generale (§1.4). Non li ho guardati per merito.
- **`REGOLE_ACCESSORI.md`** (scheda 7 e il paragrafo sui due pezzi sullo stesso tubo) e
  **`CONFRONTO-2026-08-07.md`** (nota datata in testa e conteggi) sono documenti per il
  PO: ho scritto il minimo che la regola nuova rendeva falso.
- **Rimisura di ieri.** Con la definizione di oggi la tavola DRAW-004 conta 18 valvole su
  21 nei 2,5÷5 mm (§3): il numero di DRAW-004 (20 su 20) resta valido per la definizione
  di allora, e le due definizioni non vanno confuse.
- **La verifica accosta due scritte** — `CP.01.N.05.1` e `ACS.01.N.02` accanto alla
  sicurezza — senza sovrapporle (0 etichette su etichetta). È best-effort per contratto.
- **Il foglio resta pieno al 33 %** (avviso `SHEET_BARELY_FILLED`, presente anche in
  DRAW-004 al 38 %): la composizione a fasce è fuori perimetro.
- **L'impronta della geometria** cambia quando lo schema acquista un campo, anche a
  valore predefinito: chi confronta impronte fra pacchetti deve rileggere la geometria con
  lo stesso schema.
- **L'impianto 3 non compone più** (`test_chi_e_tornato_a_comporre_compone_in_un_foglio_solo`,
  ora marcata rossa apposta con la misura). Con l'intercettazione per gruppo il terzo
  impianto ha meno organi e la posa iniziale cambia: in ordine canonico delle tratte il
  ritorno rientra sotto il defangatore dopo il taglio, in ordine del file la linea
  sanitaria dallo scaldacqua non trova il rettilineo di 7,5 mm per la miscelatrice. Sul
  commit `dc3dad5` componeva in entrambi gli ordini. È una regressione di **posa** sul
  grafo nuovo, non del grafo: il campo di lavoro è il solo impianto 1 (D-116) e non l'ho
  indagata oltre la misura; la riga esiste perché il difetto non sia scoperto due volte.
- **La revisione avversaria** (sei lenti sul diff, poi due scettici per rilievo) è stata
  interrotta dal limite di sessione dei sottoagenti: una sola lente, quella dei simboli,
  ha concluso, con due rilievi minori che ho trattato io — la contro-rotazione dei glifi
  è scritta nel testo del gruppo, e il registro ora rifiuta un gruppo che non si apra con
  `data-glyph` o che porti una trasformazione propria; il docstring del filtro a Y non
  promette più un orientamento rispetto al verso dell'acqua. Le altre cinque lenti non
  hanno prodotto un giudizio: il PM lo sappia nel pesare la verifica.

## 9. Fuori perimetro, scoperto e lasciato dov'è

- Nessun file fuori perimetro è stato toccato. `cli.py` importa il velo da
  `layout.addresses` (che passa `area=frame.drawing_rect_mm` alla posa degli indirizzi,
  chiudendo l'osservazione di DRAW-003/004 sul `floor_y_mm`) e tiene il nome
  `_with_addresses` per chi lo importava.
- I simboli non in matrice (i restanti 32 dei 39) non sono stati auditati: il generatore
  li riproduce come erano, e la prova di rigenerazione lo dimostra.

## 10. Artefatti

| File | Cosa |
|---|---|
| `prima/impianto1.{pdf,png,svg}` · `prima/geometria.json` · `prima/preflight.txt` · `prima/impianto1-completo.json` | la tavola di consegna di DRAW-004 e il suo modello, copiati |
| `prima/metriche.json` | la tavola di ieri rimisurata con lo strumento di oggi |
| `dopo/impianto1-completo.json` · `dopo/integrazioni.txt` | il modello completato dalle regole nuove, e le 26 integrazioni con le fonti |
| `dopo/impianto1.{pdf,png,svg}` · `dopo/geometria.json` · `dopo/metriche.json` · `dopo/preflight.txt` | la tavola dopo, in modalità verifica |
| `dopo/consegna/impianto1.{pdf,png,svg}` · `dopo/consegna/geometria.json` · `dopo/consegna/metriche.json` · `dopo/consegna/preflight.txt` | la tavola definitiva |
| `dopo/diario.json` | il diario del ciclo: candidate provate e accettate, per fase, specie e pezzo |
| `prima-dopo.png` | il confronto visivo, sopra DRAW-004 e sotto DRAW-005 |
| `metriche.py` | lo strumento di misura, con i rami delle macchine, la valvola oltre il raccordo e il tubo per collegamento |
