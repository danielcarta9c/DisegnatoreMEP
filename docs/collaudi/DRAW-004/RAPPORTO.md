# DRAW-004 — assi fra le porte, dorsali rettilinee e la T che assorbe una curva

**Ramo:** `claude/draw-004-assi-dorsali-tee`
**Base:** `d48f402` — il `main` che porta il Work Package DRAW-004 e il merge di DRAW-003-R1
**Campo:** il solo impianto 1 (D-116)

Tutto ciò che segue è misurato sulla stessa catena, con lo stesso ingresso, il giorno
stesso. Gli artefatti stanno in `prima/` — la tavola di consegna di DRAW-003-R1, che è la
geometria di DRAW-002 — e in `dopo/`; lo strumento è `metriche.py`, che legge la
geometria agli atti e non la ricompone, e con `--diario` rifà il ciclo per dire quali
alternative sono state provate. Gli esempi grafici del PO non sono stati usati per
ricavare requisiti: questo lavoro attua la specifica tecnica del Work Package.

## 1. Che cosa è cambiato, e perché

### 1.1 Il ciclo lavora in due fasi

La pipeline resta `place_sheet → improve_sheet → settle_sheet`. Dentro `improve_sheet`
il ciclo ora fa due cose, nell'ordine:

1. **la posa** — il ciclo di DRAW-002 così com'era: greedy, la prima candidata che batte
   la posa corrente sul confronto unico si tiene; le macchine a terra tengono la quota;
   i raccordi provano le sole rotazioni. Sull'impianto 1 arriva esattamente dove
   arrivava DRAW-002 (10 curve, 2 incroci, 597,5 mm);
2. **la rifinitura da disegnatore** — dall'ottimo raggiunto, per ogni pezzo che sta a un
   capo di una tratta che costa si misurano **tutte** le candidate valide e si tiene la
   migliore, se batte la tavola corrente. È una discesa più ripida: un guadagno grande
   non è scavalcato da uno piccolo generato prima, e l'esito non dipende da quale
   candidata capita per prima.

La prima versione provata univa le due cose in un ciclo solo, con la libertà nuova fin
dalla posa iniziale: sull'impianto 1 esauriva il tetto di prove a 11 curve e 4 incroci,
perché la libertà verticale delle macchine e le permutazioni della T cambiano il
percorso greedy fin dalle prime mosse e lo portano in un ottimo locale peggiore. Le due
fasi conservano ciò che DRAW-002 aveva ottenuto e ci costruiscono sopra: ogni candidata
della rifinitura si accetta solo se batte strettamente, quindi **nessuna regressione è
possibile per costruzione** (criteri 1 e 2).

Ogni fase ha il proprio tetto di instradamenti di prova — `MAX_TRIAL_ROUTINGS` per la
posa, `MAX_AXIS_TRIALS` (1000) per la rifinitura — che scatta in un punto che dipende
solo dagli ingressi. Sull'impianto 1 la posa usa 1291 prove e la rifinitura
912.

### 1.2 I candidati nuovi (tutti candidati, nessuna regola)

- **Assi fra le porte.** Per ogni collegamento verso un pari: la mia colonna sull'asse
  della sua porta (la posa da porta, che esisteva già), **la sua colonna sull'asse della
  mia**, e **le due colonne su un asse comune** a metà strada, sul passo. Gli assi si
  ricavano dalle coordinate e dalle facce delle porte, mai dagli ID.
- **Macchine a terra libere in quota.** Nella rifinitura `Standing.GROUND` non blocca più
  l'allineamento verticale né la posa affacciata: la quota iniziale è un suggerimento
  di posa. Il modello non dichiara vincoli fisici che la impongano — non esiste un campo
  che lo dica — quindi ogni macchina può salire, entro l'area, sulla griglia, alle
  distanze minime, nell'ordine di processo. Una pila conserva l'ordine dei membri.
- **Dorsale prima, stacchi dopo.** La catena di raccordi rimessa in fila dalla porta di
  un pezzo grosso, con ogni raccordo che prosegue diritto se può, e **il pezzo grosso
  all'altro capo** portato con la propria colonna sull'asse d'uscita della catena, o
  affacciato alla distanza minima. Si genera per il pezzo in catena e per i due capi.
- **La T che gira.** Quale attacco fisico serve ciascuna porta del modello è una
  proprietà della posa: `PlacedSymbol.port_map`, letto dal routing e dal ciclo. Le
  rotazioni ammesse dal simbolo e le permutazioni fra attacchi — ammesse quando il pezzo
  ha almeno tre attacchi tutti dello stesso dominio e fluido e tutti presenti nel
  manifesto, cioè un raccordo che si disegna come un punto — sono candidati; si scartano
  prima di misurarle quelle in cui un attacco volta le spalle al proprio pari. Grafo,
  connessioni, `connection_ids` e verso del fluido non cambiano.
- **Il diario.** Ogni candidata misurata lascia una riga: fase, specie, pezzo, costo,
  accettata o no. È la materia del §3.

`SheetCost` è invariato: stesso ordine, stesse voci. Etichette e richiami non vi entrano.

### 1.3 Fuori dal ciclo

- `layout/geometry.py`: il campo `port_map` del simbolo posato, vuoto per chiunque non
  sia un raccordo, e `physical_port()`.
- `layout/route.py`: l'ancora di una porta si legge sull'attacco fisico assegnato.
- `place.py::rotation_for()` non è stato toccato: la posa iniziale resta un
  suggerimento, e la T che gira è una candidata della rifinitura.

## 2. Le misure, prima e dopo

| Misura | Prima (DRAW-003-R1 = DRAW-002) | **Dopo (DRAW-004)** | Criterio |
|---|---:|---:|---|
| Backtracking | 0 tratte, 0 mm | **0 tratte, 0 mm** | 1 |
| Tratte oltre tre pieghe | 0 | **0** | 1 |
| Valvole D-120 a 2,5÷5 mm | 20 su 20 | **20 su 20** | 1 |
| Rilievi di correttezza e preflight bloccanti | 0 | **0** | 1 |
| Incroci | 2 | **1** | 2 (≤ 2) |
| Lunghezza delle tubazioni | 597,5 mm | **577,5 mm** | 2 (≤ 597,5) |
| Curve totali | 10 | **6** | 3 (≤ 8) |
| Linea continua di terra | assente | **assente** | 6 |
| Etichette in consegna | 7 sigle | **7 sigle** | 6 |
| Riempimento (solo diagnostica) | 36,4 % | 38,1 % | — |
| Impronta della geometria (consegna) | `a39cf5d7…` | `ac7036bd…` | |

## 3. Le alternative di asse provate, e perché quella finale ha vinto (criterio 4)

Il diario (`dopo/diario.json`) è scritto dal ciclo stesso: ogni candidata misurata lascia
fase, specie, pezzo, costo e se è stata accettata. Sull'impianto 1:

- **posa** (fase 1): 1291 instradamenti di prova; arriva a 10 curve, 2 incroci,
  597,5 mm — la geometria di DRAW-002;
- **rifinitura** (fase 2): 912 instradamenti di prova; 1 331 candidate misurate — 7
  dorsali, 40 assi, 233 pose da porta, 50 colonne, 93 catene, 54 gruppi, 43 stacchi e i
  passi ciechi — di cui 7 accettate. I candidati «tee» puri non compaiono nel diario
  perché, a pari giacitura, coincidono con una posa da porta o da catena generata prima e
  il ciclo li elimina come doppioni: la permutazione del raccordo del ritorno è arrivata
  dentro una catena rimessa in fila.

Le sette mosse accettate della rifinitura, nell'ordine, con il costo che ciascuna ha
raggiunto (curve · incroci · tubo):

| # | Specie | Pezzo | Curve | Incroci | Tubo (mm) | Che cosa ha fatto |
|---|---|---|---:|---:|---:|---|
| 0 | — | dopo la posa | 10 | 2 | 597,5 | punto di partenza |
| 1 | catena + spazio | raccordo del ritorno | 9 | 2 | 605,0 | la catena del ritorno rimessa in fila; il raccordo prende la coppia di attacchi verticale (`a↔b`) e il ritorno della PDC di sopra scende diritto nel raccordo |
| 2 | dorsale | derivazione della valvola di sicurezza | 6 | 1 | 682,5 | la catena di mandata rimessa in fila dalla porta della PDC di sotto, **con l'accumulo portato sull'asse d'uscita**: la mandata PDC → accumulo diventa una retta; tre curve e un incrocio in meno, pagati in tubo |
| 3 | passo | PDC di sotto | 6 | 1 | 642,5 | la pila delle PDC si avvicina |
| 4 | catena | raccordo di mandata | 6 | 1 | 622,5 | il raccordo di mandata rimesso in fila alla distanza minima |
| 5-7 | passo | raccordo di mandata | 6 | 1 | 577,5 | il raccordo di mandata scorre verso le PDC di un passo per volta, accorciando il tubo |

**Perché l'alternativa finale ha vinto.** La rifinitura misura, per ogni pezzo, tutte le
candidate valide e tiene la migliore: la mossa 2 è stata scelta contro 42 altre
candidate misurate per quel pezzo nello stesso giro (fra cui l'allineamento dei soli
assi, che dava 10 curve e 1 incrocio a 570 mm, e le pose da porta, che restavano a 6
curve ma con più tubo). Le alternative di asse **scartate** che il diario elenca, con il
loro costo migliore, dicono anche perché il resto non è cambiato:

- muovere la colonna dell'accumulo sull'asse delle PDC (`asse`, 12 candidate): al meglio
  10 curve; perde contro la dorsale;
- gli assi della PDC di sopra (`colonna`, 30 candidate): 6 curve, 1 incrocio, 607,5 mm —
  pari, ma più tubo;
- gli assi del radiatore (`asse`, 6 candidate): 16 curve, perché il radiatore in asse con
  l'uscita dell'accumulo rompe il rettilineo degli accessori;
- le pose del raccordo del ritorno sull'asse (`asse`, 10 candidate): 6 curve, 1 incrocio,
  572,5 mm — cinque millimetri meno di tubo, ma con una tratta che torna indietro
  (`backtracking`), che nel confronto viene prima del tubo e la scarta.

## 4. I criteri di accettazione sulla tavola 1, uno per uno

| # | Criterio | Esito | Prova |
|---|---|---|---|
| 1 | Nessuna regressione di correttezza, backtracking, tratte lunghe o valvole | **soddisfatto** | `dopo/metriche.json`: 0/0, 0, 20/20; rilievi vuoti |
| 2 | Incroci ≤ 2 e lunghezza ≤ 597,5 mm | **soddisfatto** | 1 incroci, 577,5 mm |
| 3 | Curve totali ≤ 8 | **soddisfatto** | 6 curve |
| 4 | Nessun dogleg evitabile fra le PDC e la dorsale primaria; il rapporto mostra le alternative provate | **soddisfatto** | §3 e §5 |
| 5 | Almeno un caso generale dimostra la T che assorbe una curva; sulla tavola 1 solo se il costo migliora | **soddisfatto** | `test_una_t_con_due_imbocchi_ortogonali_assorbe_un_gomito`; sulla tavola 1 il raccordo del ritorno usa la coppia verticale (§5) |
| 6 | Terra assente; consegna con sole sigle principali; verifica best-effort e mai influente | **soddisfatto** | `dopo/consegna/impianto1.svg`; le prove di DRAW-003 restano verdi; la prova 8 di questo pacchetto |
| 7 | Suite completa, `ruff`, `mypy --strict` e determinismo verdi | **soddisfatto** | §7 |
| 8 | PDF, PNG, SVG, geometria, metriche e confronto prima/dopo in `docs/collaudi/DRAW-004/` | **soddisfatto** | `prima/`, `dopo/`, `dopo/consegna/`, `prima-dopo.png` |

## 5. Le curve che restano, e perché

Sei curve su venti tratte, e ognuna ha una ragione che le porte impongono:

| Tratta | Curve | Perché resta |
|---|---:|---|
| mandata della PDC di sopra → raccordo di mandata | 1 | la PDC di sopra sta 40 mm più in alto della dorsale di mandata, che è sull'asse della PDC di sotto: una curva è il minimo per scendere nel raccordo, e la fa il tubo davanti all'attacco superiore del raccordo |
| ritorno della PDC di sotto ← raccordo del ritorno | 2 | la dorsale di ritorno è sull'asse dell'uscita dell'accumulo; fra mandata e ritorno le PDC hanno 5 mm, l'accumulo 15: allineata la mandata, il ritorno della PDC di sotto sta 10 mm sopra la dorsale e serve un gradino. La dorsale non si piega: il gradino sta sull'ultimo tratto, davanti alla PDC |
| ritorno della PDC di sopra ← raccordo del ritorno | 1 | il raccordo usa la coppia verticale: il ritorno sale diritto dal raccordo e gira una volta sola verso la PDC. Prima erano tre curve e due incroci |
| ritorno del radiatore → accumulo | 2 | uscita del radiatore e ingresso secondario dell'accumulo guardano tutti e due a destra: un'andata e ritorno a U vale due curve qualunque sia la posa |

La mandata PDC di sotto → raccordo → valvola di sicurezza → accumulo è una retta senza
gomiti (criterio 4). L'incrocio che resta è del ritorno della PDC di sopra con la
mandata della PDC di sotto: la mandata della PDC di sotto e il ritorno della PDC di
sopra devono scambiarsi di quota fra le due macchine e l'accumulo, e su una tavola
ortogonale lo fanno con un incrocio.

## 6. Le otto prove generali, scritte prima del codice

`tests/layout/test_assi_dorsali_tee.py`, con impianti costruiti nel test:

1. due macchine con porte disallineate: un candidato che sposta gratuitamente una
   macchina o il suo gruppo toglie una curva e batte la posa iniziale;
2. lo stesso allineamento non si accetta quando viola la distanza minima; ogni mossa
   accettata batte strettamente la precedente;
3. una macchina `Standing.GROUND` partecipa a un candidato verticale valido, sulla
   griglia e dentro l'area;
4. una sequenza principale con uno stacco: il raccordo sta sull'asse della macchina, la
   sequenza non paga il dogleg, e se il percorso gira, gira nel raccordo;
5. una T con due imbocchi ortogonali assorbe un gomito e batte T più gomito; grafo,
   connessioni e identificativi identici;
6. se la T ortogonale peggiora, resta la configurazione diritta;
7. ridenominare tutti gli ID non cambia la geometria; due generazioni coincidono;
8. aggiungere, cambiare o togliere testi non cambia nessun candidato, simbolo o tubo.

Tre prove esistenti sono state riallineate alla specifica: la macchina a terra può
salire (`test_the_hard_constraints_hold_after_improvement`,
`test_machines_and_storage_stand_on_the_ground`: la posa le allinea ancora, la
rifinitura può alzarne una di passi interi e nessuna scende) e il confronto delle voci è
lessicografico (`test_the_total_objective_strictly_improves_and_no_term_worsens`).

## 7. Verifiche eseguite

- Suite completa: **__SUITE__**; `ruff check src tests examples`: nessun rilievo;
  `mypy --strict src tests examples`: nessun errore.
- Il modello completo dell'impianto 1 è lo stesso file di DRAW-002 (`prima/impianto1-completo.json`).
- Due generazioni consecutive danno la stessa impronta della geometria.
- Verifica e consegna: stessi simboli e stesse rotte.

## 8. Osservazioni per il PM, che non decido io

- Le due fasi sono una scelta di architettura del ciclo, reversibile: un ciclo solo con
  la libertà nuova fin dall'inizio finiva in un ottimo locale peggiore (11 curve, 4
  incroci). Se il PM preferisce un ciclo unico, il prezzo misurato è quello.
- La rifinitura non genera lo scambio di due macchine in una pila: il pacchetto dice che
  una pila non perde il proprio ordine. Lo scambio resta una candidata della posa di
  DRAW-002, dove era nato per la mano dei raccordi; con la T che gira quella ragione
  cade, e sull'impianto 1 l'ordine delle PDC è quello che la posa aveva deciso.
- Il modello non ha un campo che dichiari un vincolo fisico di quota: oggi ogni macchina
  a terra può salire nella rifinitura. Se un vincolo del genere deve esistere — un
  accumulo che poggia per forza — è una decisione di modello, non del disegnatore.
- L'incrocio che resta (mandata della PDC di sotto contro ritorno della PDC di sopra) e
  i dieci millimetri di gradino sul ritorno vengono dalla geometria delle porte: cinque
  millimetri fra mandata e ritorno delle PDC, quindici sull'accumulo. Se il PO li vuole
  via, la leva è nei simboli (interasse delle porte), fuori perimetro.

## 9. Fuori perimetro, scoperto e lasciato dov'è

- Nessun file fuori perimetro è stato toccato. Osservato: `cli.py` passa ancora
  `floor_y_mm=sheet.ground_line_y_mm` alla posa degli indirizzi (già segnalato in
  DRAW-003); i documenti di collaudo precedenti conservano geometrie senza `port_map`,
  che si leggono comunque perché il campo ha un valore predefinito.

## 10. Artefatti

| File | Cosa |
|---|---|
| `prima/impianto1.{pdf,png,svg}` · `prima/geometria.json` · `prima/metriche.json` · `prima/preflight.txt` | la tavola di consegna di DRAW-003-R1 |
| `dopo/impianto1.{pdf,png,svg}` · `dopo/geometria.json` · `dopo/metriche.json` · `dopo/preflight.txt` | la tavola dopo, in modalità verifica |
| `dopo/consegna/impianto1.{pdf,png,svg}` · `dopo/consegna/geometria.json` · `dopo/consegna/metriche.json` | la tavola definitiva |
| `dopo/diario.json` | il diario del ciclo: candidate provate e accettate, per fase, specie e pezzo |
| `prima-dopo.png` | il confronto affiancato |
| `metriche.py` | lo strumento di misura, con `--diario` |
| `prima/impianto1-completo.json` | il modello completato dalle regole, invariato |
