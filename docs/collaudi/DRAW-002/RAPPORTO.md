# DRAW-002-R3 — la tavola dell'impianto 1 governata dal costo delle tubazioni

**Ramo:** `claude/draw-002-routing-qualita-rhy6yu` (il nome che l'ambiente ha assegnato al
ramo del pacchetto `claude/draw-002-routing-qualita`)
**Base:** `40aebfe` — il `main` che porta il Work Package DRAW-002-R3
**Campo:** il solo impianto 1 (D-116)

Tutto ciò che segue è misurato sulla stessa catena, con lo stesso ingresso, il giorno
stesso. Gli artefatti stanno in `prima/` e `dopo/`; lo strumento che li misura è
`metriche.py`, che legge la geometria agli atti e non la ricompone: le due colonne
descrivono esattamente le due tavole consegnate, e l'impronta di `metriche.json`
coincide con quella di `preflight.txt`.

I PDF di riferimento del PO in `docs/input-pm/riferimenti-grafici/2026-09-03/` non sono
stati usati per ricavare requisiti: questo lavoro attua la specifica tecnica del Work
Package e nient'altro.

## 1. Che cosa è cambiato, e perché

### 1.1 La causa del backtracking

La tratta di ritorno dall'accumulo superava di 40 mm la propria porta e tornava
indietro. La causa era nella **posa iniziale** e nel vincolo che la congelava: i tre
raccordi del corredo di rete (vaso, riempimento, manometro) venivano posati **a destra**
dell'accumulo, mentre la porta di uscita del ritorno guarda a sinistra; il ciclo di
miglioramento conservava per ogni tratta l'ordine orizzontale disegnato all'inizio,
quindi nessuna mossa poteva riportare quei raccordi dalla parte giusta. E in ogni caso
il ciclo muoveva un pezzo per volta di uno, due o quattro passi: una catena di quattro
raccordi non si sposta così.

### 1.2 Un solo confronto della tavola

Il miglioratore (`layout/improve.py`) è riscritto attorno a un valore confrontabile
della geometria completa, con precedenza lessicografica nell'ordine del pacchetto:

1. violazioni bloccanti e tratte che non ospitano i propri accessori;
2. tratte con andata e ritorno;
3. millimetri complessivi di andata e ritorno;
4. tratte oltre tre pieghe;
5. pieghe;
6. incroci;
7. lunghezza;
8. riempimento e bilanciamento, soltanto come spareggio fra geometrie uguali sulle
   sette voci precedenti.

Nessun peso: una voce successiva non compensa mai una precedente. Il movimento dei
simboli non entra nel costo. Ogni candidato si misura dopo `settle_sheet`, con gli
accessori in linea posati e tutte le tratte reinstradate.

### 1.3 La distensione è rimossa

Il comportamento con cui il ciclo comprava riempimento allungando le tubazioni non
esiste più: niente obiettivo minimo di riempimento, niente passi di allontanamento dal
centro. Riempimento e bilanciamento restano misure diagnostiche del preflight e
spareggi del confronto.

### 1.4 Le pose vengono dalla topologia

I candidati si ricavano dalle coordinate delle porte e dei vicini collegati, e possono
valere molti passi di griglia:

- l'allineamento fra le due porte di una tratta, e l'affaccio alla distanza minima che
  lascia il rettilineo agli accessori in linea, con la rotazione che rivolge la porta
  verso il collegamento;
- la **catena di raccordi rimessa in fila** dalla porta del pezzo grosso, ogni membro
  con la propria rotazione e la propria distanza;
- la traslazione di una **pila o di una colonna come gruppo**, senza sfilarne un
  elemento; lo **scambio** di due membri di una pila, insieme al raccordo rifatto;
- l'avvicinamento di tutto ciò che sta oltre un pezzo al pezzo che lo precede;
- lo **spazio aperto** a chi arriva addosso a qualcun altro: si spinge chi è d'intralcio
  lungo l'asse della mossa, in un verso o nell'altro, oppure si arretra la mossa con
  tutto ciò che le sta dietro;
- lo stacco di un accessorio appeso allungato o accorciato di qualche passo;
- le rotazioni ammesse dal manifesto e, per ultime, le traslazioni cieche.

Il ciclo è greedy: si tiene la prima mossa che batte la posa corrente sul confronto
unico, e ogni mossa accettata batte strettamente la precedente, quindi termina. Il
limite di ricerca è dichiarato: `MAX_TRIAL_ROUTINGS = 1500` instradamenti di prova per
foglio; sull'impianto 1 il ciclo converge da solo dopo 1291, in 46 secondi.

### 1.5 L'ordine di processo si legge sul verso del fluido

Il vincolo di D-060 resta un vincolo, non un costo, ma non congela più la posa iniziale:
una tratta di mandata non porta la meta a sinistra della sorgente, una di ritorno non
la porta a destra; dove il verso non è deciso vale l'ordine disegnato. Una posa iniziale
che già contraddice il verso può essere corretta, mai peggiorata. Chi sta a terra resta
alla propria quota, salvo lo scambio fra due membri della stessa pila.

### 1.6 Il collocatore non decide in base ai nomi

Dove `place.py` spareggiava per ordine alfabetico degli identificativi (l'ordine dei
raccordi in una catena, l'ordine delle catene, dei sottosistemi, degli appesi, dei pezzi
a pari profondità) ora spareggia per **posizione nel modello**. È la condizione perché
due impianti uguali con nomi diversi diano la stessa tavola, che il pacchetto chiede
come prova.

## 2. Le misure, prima e dopo

Entrambe le colonne sono calcolate con lo strumento di oggi sulla geometria agli atti.

| Misura | Prima (DRAW-001) | Dopo (DRAW-002) | |
|---|---:|---:|---|
| Tratte con andata e ritorno | 1 | **0** | criterio 1 |
| Millimetri di andata e ritorno | 75 | **0** | criterio 1 |
| Valvole D-120 a 2,5÷5 mm dall'attacco che isolano | 17 su 20 | **20 su 20** | criterio 2 |
| Tratte oltre tre pieghe | 1 | **0** | criterio 3 |
| Incroci | 12 | **2** | criterio 4, obiettivo ≤ 5 |
| Lunghezza totale delle tubazioni | 1177,5 mm | **597,5 mm** | criterio 5 |
| Tubazioni dentro il corpo di un simbolo | 0 | **0** | criterio 6 |
| Sovrapposizioni longitudinali fra tubi | 0 | **0** | criterio 6 |
| Pieghe totali | 27 | **10** | |
| Rilievi di correttezza | nessuno | **nessuno** | |
| Rilievi bloccanti del preflight | 1 | **0** | |
| Riempimento del foglio | 41,0 % | 36,4 % | diagnostica, non obiettivo |
| Rapporto fra quadrante più pieno e più vuoto | 2,59 | 3,25 | diagnostica, non obiettivo |
| Impronta della geometria | `a74b12fd…` | `992ccb58…` | |

I 75 mm di andata e ritorno della colonna «prima» sono la misura del ciclo di posa — il
giro attorno alla porta di arrivo, contato dal punto più lontano — mentre il preflight
ne contava 40 sulla spezzata: sono due misure dello stesso difetto, entrambe a zero dopo.

Le due voci diagnostiche peggiorano di poco ed è il prezzo dichiarato dal pacchetto:
nessuna distanza è più introdotta per riempire il foglio. Il preflight le riporta come
avvisi, non come rilievi bloccanti.

## 3. I criteri di accettazione DEV, uno per uno

| # | Criterio | Esito | Prova |
|---|---|---|---|
| 1 | Backtracking: zero tratte e zero millimetri | **soddisfatto** | `dopo/metriche.json`: `backtracking_tratte 0`, `backtracking_mm 0`; nessun `RUN_OVERSHOOTS_ITS_PORT` nel preflight |
| 2 | Tutte le valvole D-120 a 2,5÷5 mm | **soddisfatto** | 20 su 20 fra 2,5 e 5 mm (`valvole_d120`); le due «fuori regola» isolano un confine di rete o un raccordo, che non sono manutenibili |
| 3 | Nessuna tratta oltre tre pieghe | **soddisfatto** | `tratte_oltre_tre_pieghe 0`; nessun `RUN_WITH_TOO_MANY_BENDS` |
| 4 | Incroci sotto 12, obiettivo ≤ 5 | **soddisfatto** | 2 nodi condivisi; sparito `TOO_MANY_CROSSINGS` |
| 5 | Lunghezza sotto 1177,5 mm | **soddisfatto** | 597,5 mm |
| 6 | Nessun tubo sotto un simbolo, nessuna sovrapposizione longitudinale | **soddisfatto** | `tubo_sotto_simbolo []`, rilievi di correttezza vuoti, nessun `RUNS_OVERLAP_LENGTHWISE` |
| 7 | Terminale e accumulo adiacenti quanto consentito | **soddisfatto** | le porte dell'accumulo e del radiatore distano 55 mm sulla mandata, meno dei 65 mm che il conto nominale dei cinque accessori in linea prevede (quattro valvole e il circolatore, con le valvole che isolano a un passo dall'attacco invece di due); la prova `test_tavola_1_il_terminale_sta_addosso_all_accumulo` lo misura |
| 8 | Grafo invariato, nessuna coordinata dell'impianto 1 nel motore | **soddisfatto** | il modello completo ha lo stesso `sha256` della baseline di DRAW-001 (`5d3334f5…`); il motore legge solo porte, funzioni di catalogo e ordine del modello |
| 9 | Suite completa, `ruff`, `mypy --strict` verdi | **soddisfatto** | vedi §5 |
| 10 | PDF, PNG, SVG, confronto raster, tabella prima/dopo | **soddisfatto** | `dopo/impianto1.{pdf,png,svg}`, `prima-dopo.png`, §2 |

## 4. Le prove generali, scritte prima del codice

`tests/layout/test_costo_peso.py`, su impianti costruiti nel test con il catalogo di
prova e senza identificativi dell'impianto 1:

- una posa compatta batte una posa equidistante, e il miglioratore torna da quella
  equidistante a una geometria che non costa più della compatta;
- nessun aumento di riempimento compra tubo, pieghe, incroci o andate e ritorno: sul
  confronto unico e sul ciclo, che non peggiora mai il costo di partenza;
- una pila collegata trasla come gruppo, e nessun candidato ne sfila un elemento;
- i candidati raggiungono direttamente l'allineamento fra porte anche a otto passi;
- due ingressi topologicamente equivalenti, con ogni identificativo cambiato e l'ordine
  alfabetico rovesciato, producono la stessa geometria;
- due generazioni consecutive danno lo stesso fingerprint.

I criteri di accettazione della tavola 1 sono anche una regressione in
`tests/acceptance/test_drawing.py` (cinque prove `test_tavola_1_*`), che trova i pezzi
dal catalogo e non dai nomi.

## 5. Verifiche eseguite

- Suite completa: **1077 verdi, 22 parcheggiate, 13 marcate rosse apposta** sui difetti
  aperti (in 14 minuti); `ruff check src tests examples`: nessun rilievo;
  `mypy --strict src tests examples`: nessun errore su 134 file.
- Due generazioni consecutive dello stesso ingresso danno la stessa impronta; la
  composizione dell'impianto 1 dura circa 46 secondi, contro i due minuti di DRAW-001.
- Il modello completo dell'impianto 1 generato oggi dalle regole ha lo stesso `sha256`
  di quello di DRAW-001: interprete, regole, assemblatore e cataloghi non sono toccati.

## 6. Osservazioni per il PM, che non decido io

- **Il manometro sta sotto la tubazione, capovolto.** I tre raccordi del corredo di rete
  hanno una mano sola (ingresso a sinistra, stacco in alto, uscita a destra); posati sul
  ritorno che scorre da destra a sinistra, il loro stacco guarda in basso, e vaso,
  riempimento e manometro pendono tutti sotto la linea. Per vaso e riempimento è la
  posa consueta; per il manometro no. Un simbolo speculare del raccordo, o una regola
  su dove pende ciascun accessorio, sono scelte di rappresentazione del PO.
- **Il riempimento resta al 36 % e lo squilibrio a 3,25**, entrambi avvisi del
  preflight. Il pacchetto esclude che si compri carta con tubo; se per la release 0.2
  serve un foglio più pieno, è una scelta di composizione (dove stanno le macchine in
  altezza, il formato) che spetta al PO.
- **I due incroci residui stanno sulla stessa tratta**: il ritorno della pompa in cima
  alla pila scende dal raccordo di ritorno e, risalendo verso il proprio attacco,
  attraversa le tratte della pompa in basso. Con due macchine impilate e due raccordi a
  T di una mano sola l'incrocio fra mandata e ritorno è topologicamente forzato: il
  ciclo lo ha ridotto al minimo che quella mano consente.

## 7. Fuori perimetro, scoperto e lasciato dov'è

- I simboli dei raccordi a T non ammettono una versione speculare: ogni posa di catena
  ne eredita la mano, e alcune figure (due ingressi da sinistra e dal basso, uscita a
  destra) non sono disegnabili senza un'andata e ritorno. È materia della libreria dei
  simboli.
- Le prove di `tests/layout/test_improve.py` marcate «saltate» dal 9 agosto restano
  saltate: descrivono soglie del vecchio caso di accettazione che questo pacchetto non
  ha in perimetro.

## 8. Artefatti

| File | Cosa |
|---|---|
| `prima/impianto1.{pdf,png,svg}` · `prima/geometria.json` · `prima/metriche.json` · `prima/preflight.txt` | la tavola prima, generata oggi dalla catena di `main` (impronta identica a DRAW-001 finale) |
| `dopo/impianto1.{pdf,png,svg}` · `dopo/geometria.json` · `dopo/metriche.json` · `dopo/preflight.txt` | la tavola dopo |
| `prima-dopo.png` | il confronto affiancato, con le misure in testa |
| `metriche.py` | lo strumento che calcola le misure, lo stesso per le due colonne |
| `prima/impianto1-completo.json` | il modello completato dalle regole, invariato |

Si rigenera tutto con `bash scripts/tavole-di-verifica.sh`, che da questo pacchetto
scrive anche geometria, PNG e misure di ogni tavola.

## 9. Censimento dei rami (D-123)

Rami remoti con commit che `origin/main` non contiene, al momento della consegna.
Elencati e lasciati dove sono: fonderli o cancellarli non è di questo pacchetto.

| Ramo | Commit fuori da `main` | Cosa |
|---|---:|---|
| `claude/draw-002-routing-qualita-rhy6yu` | 3 | **questo pacchetto**, in PR |
| `claude/disegnatoremep-main-resume-890881` | 10 | la linea dell'8 agosto, il debito aperto già censito in `PROJECT_STATE.md` (D-115): si riporta un pezzo per volta |
| `archivio/fase-grafica-2026-08-03` | 72 | storia separata, senza antenati in comune: archivio, non si fonde |
| `claude/gov-001-baseline-m6b0mn` | 3 | i commit originali di GOV-001, entrati in `main` per merge del PM con altra storia |
| `pm/claude-entrypoint`, `pm/draw-001-active-work-package`, `pm/draw-002-r2-riferimenti-visivi`, `pm/draw-002-r3-specifica-tecnica` | 1–2 ciascuno | rami del PM, i cui contenuti sono in `main` con commit di merge propri |

Gli altri rami remoti sono dentro `main`.
