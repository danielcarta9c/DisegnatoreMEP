# DRAW-003 — via la linea di terra, e i testi come fase terminale

**Ramo:** `claude/draw-003-terra-etichette`
**Base:** `c1ddfbf` — il `main` che porta il Work Package DRAW-003 e il merge di DRAW-002
**Campo:** il solo impianto 1 (D-116)

Tutto ciò che segue è misurato sulla stessa catena, con lo stesso ingresso, il giorno
stesso. Gli artefatti stanno in `prima/` — la tavola di DRAW-002, rimisurata con lo
strumento di oggi — e in `dopo/`; lo strumento è `metriche.py`, che legge la geometria
agli atti e non la ricompone. L'immagine annotata del PO non è stata usata per ricavare
requisiti: questo lavoro attua la specifica del Work Package.

## 1. Che cosa è cambiato, e perché

### 1.1 La linea di terra non esiste più sulla tavola (D-121, I-024)

**Causa.** D-121 era attuata a metà: tubazioni e testi potevano attraversare la quota,
ma la composizione continuava a scrivere `ground_line_y_mm` nella geometria, il renderer
disegnava una linea continua con il tratteggio del pavimento su tutta la larghezza
dell'area, e la centratura del blocco contava quella quota come fondo del disegno.

**Correzione.**
- Il renderer non disegna più la linea né il tratteggio, **qualunque cosa porti la
  geometria**: anche una geometria vecchia con la quota scritta esce senza terra. È
  l'unico percorso di rendering della tavola; il foglio di riscontro dei simboli non ha
  mai avuto una terra.
- La composizione non esporta più la quota. Il campo resta nel modello geometrico,
  sempre `None`, perché le geometrie già agli atti si leggano e perché il comando di
  disegno, fuori perimetro, lo nomina ancora passandolo alla posa degli indirizzi, che
  ora lo ignora.
- La quota interna di posa (`levels.ground_mm`) resta il riferimento su cui le macchine
  si allineano in basso: è un dato del collocatore, non un elemento della tavola.
- La centratura conta soltanto simboli e tubazioni.

### 1.2 I testi sono l'ultima fase, e non toccano niente (I-025, D-075, D-110, D-111)

**Sequenza.** `compose_sheet` ora fa, nell'ordine: posa, instradamento completo con gli
accessori in linea, centratura del blocco, e **solo alla fine** i testi, su simboli e
rotte già definitivi. Prima i testi entravano nella centratura: la lunghezza di una sigla
poteva spostare le macchine. Il contratto è provato: una sigla di cinquanta caratteri,
o nessuna sigla, o il velo degli indirizzi di verifica, danno simboli e rotte
bit-identici.

**Posa dei testi.** Ogni testo ha una posizione preferita: la sigla sopra il pezzo, i
valori sotto, l'indirizzo di verifica a destra. Se è libera, il testo resta lì senza
richiamo. Se collide con un tubo, un simbolo, un'altra etichetta o il margine dell'area
di disegno, non si muove nulla di ciò che è disegnato: il testo prende una diagonale a
45 gradi da uno spigolo del proprio pezzo, allungata di un passo per volta, e si ferma
al primo posto libero. Le vecchie ricerche per lati e anelli senza richiamo — fino a
otto passi di distanza — sono rimosse.

**Il richiamo.** Tre gradi di rigore, provati in quest'ordine: la diagonale non
attraversa tubi, simboli, testi né altri richiami; poi può attraversare tubi e altri
richiami; poi, ultima risorsa di un pezzo murato fra due macchine, anche un simbolo. In
ogni caso il testo sta dentro l'area e non copre nulla. Il preflight dice dove il rigore
è sceso.

**Gli indirizzi di verifica** seguono lo stesso ordine e la stessa regola, e da oggi
non finiscono più sopra un tubo: la vecchia nota di D-110 che li ammetteva attraversati
da una tubazione è superata dal criterio 4 del pacchetto.

### 1.3 Validazione

- Cancello di correttezza: `LABEL_OUTSIDE_DRAWING_AREA` (bloccante), oltre a
  `LABEL_COLLISION` che c'era.
- Preflight: `LABEL_ON_A_RUN` (bloccante); `LEADERS_CROSS`, `LEADER_CROSSES_A_RUN`,
  `LEADER_CROSSES_A_SYMBOL` (avvisi, perché sono l'esito dichiarato di una tavola
  affollata, non un difetto della regola).

## 2. Le misure, prima e dopo

| Misura | Prima (DRAW-002) | Dopo (DRAW-003) | |
|---|---:|---:|---|
| Linea continua di terra nell'SVG | sì (gruppo `ground`, linea + 254 trattini) | **no** | criterio 1 |
| Quota di terra esportata nella geometria | 188,5 mm | **nessuna** | |
| Etichette (modalità verifica) | 52 | 52 | |
| Etichette sopra un tubo | 23 | **0** | criterio 4 |
| Etichette sopra un simbolo o un'altra etichetta | 0 | **0** | criterio 4 |
| Etichette con richiamo obliquo | 0 | 38 | criterio 5 |
| Richiami che attraversano un tubo | — | 5 | avviso |
| Richiami che passano sopra un simbolo | — | 2 | avviso |
| Coppie di richiami che si incrociano | — | 1 | avviso |
| Backtracking | 0 tratte, 0 mm | **0 tratte, 0 mm** | criterio 2 |
| Tratte oltre tre pieghe | 0 | **0** | criterio 2 |
| Incroci | 2 | **2** | criterio 2 |
| Lunghezza delle tubazioni | 597,5 mm | **597,5 mm** | criterio 2 |
| Valvole D-120 a 2,5÷5 mm | 20 su 20 | **20 su 20** | criterio 2 |
| Simboli e rotte rispetto a DRAW-002 | — | **identici, traslazione nulla** | criterio 3 |
| Rilievi bloccanti (con lo strumento di oggi) | 23 `LABEL_ON_A_RUN` | **0** | |
| Impronta della geometria (verifica) | `992ccb58…` | `dd4f21bd…` | cambia per le sole etichette |

I 23 rilievi bloccanti della colonna «prima» non esistevano al tempo di DRAW-002: sono
la misura nuova di questo pacchetto applicata alla tavola vecchia, e dicono quanto quel
difetto era esteso.

## 3. I criteri di accettazione DEV, uno per uno

| # | Criterio | Esito | Prova |
|---|---|---|---|
| 1 | Nessuna linea o tratteggio continuo di terra nel PDF, PNG e SVG | **soddisfatto** | `dopo/impianto1.svg` non contiene il gruppo `ground` né linee orizzontali che attraversano l'area; PDF e PNG sono resi da quello stesso SVG; prova `tests/graphics/test_terra.py` su una tavola a mano che dichiara ancora la quota e sulla tavola composta |
| 2 | Nessuna regressione sulle metriche di DRAW-002 | **soddisfatto** | `dopo/metriche.json`: backtracking 0/0, tratte oltre tre pieghe 0, incroci 2, lunghezza 597,5 mm, valvole 20/20 |
| 3 | Simboli e rotte coincidono con DRAW-002 | **soddisfatto** | confronto punto per punto fra `prima/geometria.json` e `dopo/geometria.json`: stesse origini, rotazioni e riquadri dei 45 simboli, stessi punti delle 20 rotte, traslazione nulla |
| 4 | Nessuna collisione finale etichetta/etichetta, etichetta/simbolo, etichetta/tubo | **soddisfatto** | `etichette_su_tubo 0`, `etichette_su_simbolo 0`, `etichette_su_etichetta 0`; rilievi di correttezza vuoti; nessun `LABEL_ON_A_RUN` |
| 5 | Ogni etichetta spostata porta un richiamo obliquo leggibile | **soddisfatto** | 38 richiami, tutti a 45 gradi da uno spigolo del proprio pezzo (nessun `ORTHOGONAL_LABEL_LEADER` né `LEADER_NOT_AT_45_DEGREES`); i 14 testi senza richiamo stanno al posto preferito |
| 6 | Verifica e consegna differiscono solo per il velo degli indirizzi | **soddisfatto** | `dopo/geometria.json` e `dopo/consegna/geometria.json`: simboli e rotte uguali; le 7 sigle di consegna sono identiche nelle due tavole; prova `test_gli_indirizzi_di_verifica_non_cambiano_simboli_ne_rotte` |
| 7 | Suite, `ruff`, `mypy --strict` verdi; output deterministico | **soddisfatto** | §5; due generazioni consecutive danno la stessa impronta |
| 8 | PDF, PNG, SVG aggiornati, confronto con DRAW-002, rapporto criterio per criterio | **soddisfatto** | `dopo/`, `dopo/consegna/`, `prima-dopo.png`, questo rapporto |

## 4. Le prove scritte prima del codice

`tests/graphics/test_terra.py` e `tests/layout/test_etichette_postume.py`:

1. l'SVG di una tavola che dichiara la quota di terra, e quello della tavola composta,
   non contengono il gruppo, la linea o il tratteggio del terreno;
2. la stessa geometria con e senza indirizzi di verifica ha simboli e rotte identici;
3. una sigla molto più lunga — e nessuna sigla — non cambia simboli o rotte;
4. un'etichetta con posizione preferita libera resta adiacente e senza richiamo;
5. un'etichetta la cui posizione preferita interseca una tubazione si sposta con
   richiamo obliquo, la tubazione resta bit-identica, e il richiamo non la attraversa;
6. due etichette in conflitto: la seconda prende il richiamo, nessuna sovrapposizione;
7. due generazioni consecutive danno lo stesso output.

Più: l'indirizzo di verifica segue lo stesso ordine; un'etichetta non esce dall'area di
disegno; i richiami non si incrociano quando esiste un'alternativa; sulla tavola 1 ogni
etichetta è libera o richiamata a 45 gradi.

## 5. Verifiche eseguite

- Suite completa: **__SUITE__**; `ruff check src tests examples`: nessun rilievo;
  `mypy --strict src tests examples`: nessun errore.
- Il modello completo dell'impianto 1 è lo stesso file di DRAW-002 (`prima/impianto1-completo.json`).
- Due generazioni consecutive danno la stessa impronta della geometria, etichette comprese.

## 6. Osservazioni per il PM, che non decido io

- **In modalità verifica 38 testi su 52 portano il richiamo.** È l'effetto della regola
  netta del pacchetto su una tavola compatta: gli indirizzi sono lunghi (dieci caratteri)
  e il posto preferito di fianco a una valvola su un tubo è quasi sempre occupato dal
  tubo stesso. La tavola di consegna, con le sole sette sigle, non ha nessun richiamo.
  Se il PO preferisce meno richiami in verifica, la leva è la posizione preferita degli
  indirizzi o la loro lunghezza: scelte di rappresentazione, non del disegnatore.
- **Otto richiami sono al rigore ridotto**: cinque attraversano un tubo, due passano
  sopra un simbolo vicino, una coppia si incrocia. Il preflight li elenca come avvisi.
  Sono i pezzi murati fra due macchine o fra tubi paralleli, dove nessuna diagonale
  libera esiste; scrivere il testo comunque è la scelta fatta, perché un testo mancante
  è peggio.
- Riempimento e squilibrio (36 %, 3,25) sono invariati da DRAW-002: non erano nel
  perimetro.

## 7. Fuori perimetro, scoperto e lasciato dov'è

- `cli.py` passa ancora `floor_y_mm=sheet.ground_line_y_mm` alla posa degli indirizzi:
  il valore è sempre `None` e il parametro è ignorato, ma la riga e il campo si tolgono
  in un pacchetto che abbia il comando di disegno in perimetro.
- Il richiamo termina sempre alla base sinistra del testo: sulla diagonale in basso a
  sinistra passerebbe sotto il proprio testo, quindi quella direzione si usa solo
  all'ultimo grado di rigore. Un capo di richiamo sul lato destro del testo chiede un
  campo in più nella geometria.

## 8. Artefatti

| File | Cosa |
|---|---|
| `prima/impianto1.{pdf,png,svg}` · `prima/geometria.json` · `prima/metriche.json` · `prima/preflight.txt` | la tavola di DRAW-002, rimisurata con lo strumento di oggi |
| `dopo/impianto1.{pdf,png,svg}` · `dopo/geometria.json` · `dopo/metriche.json` · `dopo/preflight.txt` | la tavola dopo, in modalità verifica |
| `dopo/consegna/impianto1.{pdf,png,svg}` · `dopo/consegna/geometria.json` | la stessa tavola senza il velo degli indirizzi |
| `prima-dopo.png` | il confronto affiancato |
| `metriche.py` | lo strumento di misura, con le voci sulle etichette |
| `prima/impianto1-completo.json` | il modello completato dalle regole, invariato |
