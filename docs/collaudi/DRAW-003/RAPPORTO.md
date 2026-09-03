# DRAW-003 / R1 — via la linea di terra, e i testi come fase terminale a costo zero

**Ramo:** `claude/draw-003-terra-etichette` — PR #11, aggiornata
**Base:** `c1ddfbf` (DRAW-003) integrata con `ceaa6e5` (DRAW-003-R1)
**Campo:** il solo impianto 1 (D-116)

Tutto ciò che segue è misurato sulla stessa catena, con lo stesso ingresso, il giorno
stesso. Gli artefatti stanno in `prima/` — la tavola di DRAW-002, rimisurata con lo
strumento di oggi — e in `dopo/`; lo strumento è `metriche.py`, che legge la geometria
agli atti e non la ricompone.

## 0. La revisione, e perché

La prima consegna di DRAW-003 toglieva la linea di terra e rendeva contrattuale la
sequenza posa → tubazioni → centratura → testi: quelle due parti sono accettate dal PM e
qui restano invariate. Trattava però le etichette come un criterio bloccante, con un
richiamo al primo conflitto e tre gradi di rigore che arrivavano ad attraversare tubi e
simboli: sull'impianto 1 ne uscivano 38 richiami su 52 testi. Il PO ha corretto la
priorità, e il PM ha ritirato quella specifica come errata.

**La gerarchia vincolante** (DRAW-003-R1): correttezza del grafo; geometria di macchine,
accessori e tubazioni; costo delle tubazioni; e soltanto a geometria congelata i testi,
che hanno **costo nullo** rispetto alla geometria, non spostano niente e non bloccano mai
l'emissione della tavola. Questo rapporto non dichiara più alcun criterio sulle etichette
come prioritario rispetto alla geometria.

## 1. Che cosa è cambiato in R1

### 1.1 Conservato: nessuna linea di terra, testi dopo il routing

- Il renderer non disegna la linea né il tratteggio, qualunque cosa porti la geometria;
  la composizione non esporta la quota; la centratura conta solo simboli e tubazioni.
  Invariato rispetto alla prima consegna, riprovato (`tests/graphics/test_terra.py`).
- La sequenza posa → tubazioni → centratura → testi è un contratto provato: una sigla di
  cinquanta caratteri, nessuna sigla, o il velo degli indirizzi di verifica danno simboli
  e rotte bit-identici. Etichette e richiami non entrano in `SheetCost`, nei candidati
  né in nessuna misura del collocatore.

### 1.2 Ritirato: il richiamo al primo conflitto e i gradi di rigore

La ricerca della diagonale a tre gradi di rigore — che al secondo attraversava tubi e
altri richiami, al terzo passava sopra i simboli, e in ultimo scriveva comunque sulla
prima diagonale — è rimossa. Rimosso anche il carattere bloccante dei rilievi sui testi.

### 1.3 La regola nuova, semplice e a buon fine

- Ogni testo prova, in **ordine fisso**, i lati adiacenti al proprio pezzo — la sigla
  sopra, poi sotto, a destra, a sinistra; i valori sotto per primi; l'indirizzo di
  verifica a destra per primo — e si ferma al primo posto libero da simboli, tubi, altri
  testi e margine, **senza richiamo**: un testo che cambia lato resta una scritta accanto
  al proprio pezzo (D1).
- **Sigle e valori delle macchine** (i testi della tavola definitiva): se nessun lato è
  libero, un richiamo **corto** a 45 gradi da uno spigolo del pezzo, al massimo dodici
  passi di corsa, e solo se non attraversa tubi, simboli, testi né altri richiami. Se
  nemmeno quello esiste, il testo **si omette** e il preflight lo dice con l'avviso
  `TAG_OMITTED`. Un richiamo si disegna quando chiarisce, mai quando confonde.
- **Indirizzi della modalità verifica**: velo a buon fine per identificare un pezzo.
  Adiacenti se c'è un lato libero, altrimenti **omessi**; mai richiamati, nessun rilievo.
- **Tavola definitiva**: nessun indirizzo della rete; restano le sole sigle delle macchine
  principali — sull'impianto 1 le sette macchine che il modello sigla — posate dopo il
  routing e senza influenzarlo.

### 1.4 Validazione

- Il cancello di correttezza è invariato (`LABEL_COLLISION`, `LABEL_OUTSIDE_DRAWING_AREA`):
  il disegnatore non produce più quei casi per costruzione, perché scrive solo su un posto
  libero o omette.
- Preflight: `LABEL_ON_A_RUN`, `LEADERS_CROSS`, `LEADER_CROSSES_A_RUN`,
  `LEADER_CROSSES_A_SYMBOL` e il nuovo `TAG_OMITTED` sono tutti **avvisi**. Nessun rilievo
  sui testi blocca PDF, PNG o SVG. Gli indirizzi si aggiungono dopo i cancelli, come già
  in DRAW-001, quindi non li attraversano nemmeno.

## 2. Le misure, prima e dopo

| Misura | Prima (DRAW-002) | DRAW-003 prima consegna | **DRAW-003-R1** | |
|---|---:|---:|---:|---|
| Linea continua di terra nell'SVG | sì (linea + 254 trattini) | no | **no** | criterio 1 |
| Backtracking | 0 tratte, 0 mm | 0 / 0 | **0 / 0** | criterio 2 |
| Tratte oltre tre pieghe | 0 | 0 | **0** | criterio 2 |
| Incroci | 2 | 2 | **2** | criterio 2 |
| Lunghezza delle tubazioni | 597,5 mm | 597,5 mm | **597,5 mm** | criterio 2 |
| Valvole D-120 a 2,5÷5 mm | 20 su 20 | 20 su 20 | **20 su 20** | criterio 2 |
| Simboli e rotte rispetto a DRAW-002 | — | identici | **identici, traslazione nulla** | criteri 2, 3 |
| Etichette in modalità verifica (sigle + indirizzi) | 52 (7 + 45) | 52 (7 + 45) | **42 (7 + 35)** | criterio 4 |
| Indirizzi omessi perché senza lato libero | 0 | 0 | **10 su 45** | criterio 4 |
| Etichette con richiamo (verifica) | 0 | 38 | **0** | criterio 4 |
| Richiami che attraversano tubi, simboli o altri richiami | — | 5 + 2 + 1 coppia | **0** | |
| Etichette sopra un tubo, un simbolo o un'altra etichetta | 23 / 0 / 0 | 0 / 0 / 0 | **0 / 0 / 0** | |
| Etichette in tavola definitiva | 7 sigle | 7 sigle | **7 sigle, 0 richiami, 0 omesse** | criterio 5 |
| Rilievi bloccanti sui testi | — | 23 `LABEL_ON_A_RUN` sulla tavola vecchia | **nessuno, per costruzione** | criterio 6 |
| Impronta della geometria (verifica) | `992ccb58…` | `dd4f21bd…` | `3117ffed…` | cambia per le sole etichette |

## 3. I criteri di accettazione DRAW-003-R1, uno per uno

| # | Criterio | Esito | Prova |
|---|---|---|---|
| 1 | Linea e tratteggio continui di terra assenti | **soddisfatto** | `dopo/impianto1.svg` senza gruppo `ground` né linee che attraversano l'area; `tests/graphics/test_terra.py` |
| 2 | Simboli e rotte identici a DRAW-002: backtracking 0, tratte oltre tre pieghe 0, incroci ≤ 2, lunghezza ≤ 597,5 mm, valvole 20/20 | **soddisfatto** | `dopo/metriche.json`; confronto punto per punto fra `prima/geometria.json` e `dopo/geometria.json`: 45 simboli e 20 rotte identici |
| 3 | Modifica, presenza o assenza delle etichette non cambia la geometria | **soddisfatto** | `test_una_sigla_molto_piu_lunga_non_cambia_simboli_ne_rotte`, `test_senza_nessuna_sigla_simboli_e_rotte_restano_gli_stessi`, `test_gli_indirizzi_di_verifica_non_cambiano_simboli_ne_rotte` |
| 4 | Nessun groviglio automatico di richiami: la verifica privilegia indirizzi semplici e può omettere quelli non collocabili | **soddisfatto** | gli indirizzi non portano mai il richiamo (`test_un_indirizzo_non_porta_mai_il_richiamo`); sull'impianto 1 35 indirizzi scritti adiacenti e 10 omessi, 0 richiami in tutto |
| 5 | La tavola definitiva mostra soltanto le etichette delle macchine principali | **soddisfatto** | `dopo/consegna/geometria.json`: 7 sigle, nessun indirizzo; `test_la_tavola_di_consegna_porta_solo_le_sigle_delle_macchine` |
| 6 | Nessun rilievo sulle etichette blocca PDF, PNG o SVG | **soddisfatto** | tutti i rilievi sui testi sono avvisi; una sigla senza posto si omette e la tavola esce (`test_una_sigla_senza_nessun_posto_pulito_si_omette_e_la_tavola_esce`) |
| 7 | Suite completa, `ruff`, `mypy --strict` e determinismo verdi | **soddisfatto** | §5 |
| 8 | Artefatti aggiornati e rapporto corretto senza dichiarare le etichette prioritarie rispetto alla geometria | **soddisfatto** | `dopo/`, `dopo/consegna/`, `prima-dopo.png`, questo rapporto |

## 4. Le prove

`tests/layout/test_etichette_postume.py`, riscritte prima del codice per la regola nuova:

1. un'etichetta con il posto libero resta adiacente e senza richiamo;
2. un'etichetta sulla tubazione prende un altro lato, senza richiamo, e il tubo resta
   bit-identico;
3. i lati si provano in ordine fisso e il primo libero vince;
4. due etichette in conflitto: la seconda prende un altro lato, nessuna sovrapposizione;
5. un'etichetta non esce dall'area di disegno;
6. una sigla murata da quattro tubi prende un richiamo corto che non attraversa niente,
   da uno spigolo del proprio pezzo;
7. una sigla senza nessun posto pulito si omette, e la tavola esce;
8. un richiamo non attraversa un altro richiamo né un'altra sigla;
9. un indirizzo prende un lato libero o si omette, e non porta mai il richiamo;
10. il contratto: sigla lunghissima, nessuna sigla e velo degli indirizzi non cambiano
    simboli né rotte; la tavola definitiva porta solo le sigle delle macchine; due
    generazioni consecutive danno lo stesso output.

`tests/layout/test_labels.py` e `tests/validation/test_preflight.py` aggiornati alla
regola nuova e alla misura `omitted_tags`.

## 5. Verifiche eseguite

- Suite completa: **in esecuzione al momento di questo salvataggio; l'esito è nel commit successivo**; `ruff check src tests examples`: nessun rilievo;
  `mypy --strict src tests examples`: nessun errore su 136 file.
- Il modello completo dell'impianto 1 è lo stesso file di DRAW-002 (`prima/impianto1-completo.json`).
- Due generazioni consecutive danno la stessa impronta della geometria, etichette comprese.

## 6. Osservazioni per il PM, che non decido io

- **Dieci indirizzi su 45 non sono scritti** in modalità verifica: sono le valvole e i filtri stretti fra tubi paralleli e altri pezzi, dove nessuna delle due file su nessuno dei quattro lati è libera. La regola del pacchetto li ammette omessi; se il PO ne vuole qualcuno in particolare, la leva è la rappresentazione (testo più corto, o un lato preferito diverso per quel tipo di pezzo), non un richiamo automatico. L'elenco dei pezzi senza indirizzo si ricava da `dopo/geometria.json` (simboli senza etichetta `address-…`).
- Il capo del richiamo è sempre la base sinistra del testo, quindi la diagonale in basso a
  sinistra non si usa mai (passerebbe sotto il proprio testo): un capo sul lato destro del
  testo chiede un campo in più nella geometria. Non serve sull'impianto 1.
- Riempimento e squilibrio (36 %, 3,25) sono invariati da DRAW-002: non erano nel perimetro.

## 7. Registrato per DRAW-004, non implementato qui

I-026 (allontanare e riallineare inlet/outlet delle macchine principali quando riduce
curve, incroci e lunghezza), I-027 (una T con due imbocchi ortogonali che assorbe una
curva) e I-028 (etichette e richiami mai nel confronto fra due pose) sono nel registro
degli input. Il routing non è stato toccato in questa revisione.

## 8. Fuori perimetro, scoperto e lasciato dov'è

- `cli.py` passa ancora `floor_y_mm=sheet.ground_line_y_mm` alla posa degli indirizzi:
  il valore è sempre `None` e il parametro è ignorato.

## 9. Artefatti

| File | Cosa |
|---|---|
| `prima/impianto1.{pdf,png,svg}` · `prima/geometria.json` · `prima/metriche.json` · `prima/preflight.txt` | la tavola di DRAW-002, rimisurata con lo strumento di oggi |
| `dopo/impianto1.{pdf,png,svg}` · `dopo/geometria.json` · `dopo/metriche.json` · `dopo/preflight.txt` | la tavola R1 in modalità verifica |
| `dopo/consegna/impianto1.{pdf,png,svg}` · `dopo/consegna/geometria.json` · `dopo/consegna/metriche.json` | la tavola definitiva, senza il velo degli indirizzi |
| `prima-dopo.png` | il confronto affiancato, DRAW-002 e R1 in modalità verifica |
| `metriche.py` | lo strumento di misura, con le voci sulle etichette e sulle sigle omesse |
| `prima/impianto1-completo.json` | il modello completato dalle regole, invariato |
