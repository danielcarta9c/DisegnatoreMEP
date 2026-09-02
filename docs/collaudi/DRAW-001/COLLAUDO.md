# DRAW-001 — collaudo indipendente (D-083)

**Oggetto:** la consegna del Work Package DRAW-001 sul ramo `claude/draw-001-tavola1-qualita`.
**Revisione di base:** `ebe165a` — **revisione collaudata:** `df48457`.
**Chi collauda:** agente a contesto separato, che non ha scritto questo codice e non ha
visto nascere il lavoro. Nessun file del repository è stato modificato tranne questo
verbale; le misure sono state fatte con script propri, scritti in una cartella temporanea.

---

## Verdetto complessivo

# RESPINTO

Il nucleo tecnico è buono e **non va rifatto**: la causa dei due difetti è stata trovata
davvero, la correzione è generale, il grafo non si è mosso di un byte, la tavola è
deterministica, ruff e mypy sono verdi e nessun file è fuori perimetro. Il collaudo si
ferma su quattro cose:

0. **la suite non passa al commit consegnato.** Eseguita da me su `df48457`,
   `test_tornano_a_comporre_quando_la_composizione_compatta[prova-3-…]` **fallisce** con
   `XPASS(strict)`. Non è un difetto preesistente documentato: è una prova di guardia rotta
   **dalla modifica di questo pacchetto**, e il rapporto (§5) dichiara invece la suite
   completa fra le verifiche eseguite. Vedi **D-6**;
1. **il criterio 3 non è soddisfatto come è scritto** — quattro valvole su diciannove
   restano fuori dalla forbice 2,5÷5 mm, e una di queste è a **0 mm** proprio sulla coppia
   valvola-circolatore, che è il caso che il PO ha nominato;
2. **il criterio 1 risulta soddisfatto anche perché un controllo preesistente è stato
   ristretto**: la misura vecchia segnalava la linea che corre **a filo del fianco** di un
   simbolo e la chiamava, con parole sue, «esattamente il difetto peggiore»; la misura
   nuova la ammette per costruzione. Sulla tavola finale ci sono **sei** tratti a filo di un
   simbolo (baseline: zero), e **due di essi il cancello di correttezza della revisione di
   base li avrebbe segnalati come bloccanti**. Restringere una convenzione di
   rappresentazione è materia del PO (D-124 §2-§3): andava proposta, non attuata, e in
   nessun punto del rapporto è dichiarata;
3. **il numero di punta del criterio 5 è gonfiato da un artefatto non dichiarato**: dei
   +13,1 punti di riempimento, **9,2 vengono da un solo pezzo leggero** — la valvola di
   sicurezza, 5 × 5 mm — spinto 27,5 mm sopra tutto il resto dell'inchiostro. È
   letteralmente il meccanismo che il rapporto dice, al §1.3, di avere evitato.

A queste si aggiunge una **proposta di chiusura che afferma più di quanto le prove
mostrino** (I-007), che è la classe di difetto più respinta della storia del progetto.

---

## Tabella criterio per criterio

| # | Criterio | Verdetto | Prova, e numero misurato |
|---|---|---|---|
| 1 | Nessuna tubazione attraversa il corpo pieno di un simbolo | **soddisfatto, con riserva** | Misura mia, indipendente, su `finale/geometria.json`: **0 attraversamenti** su 72 tratti elementari × 45 simboli, riquadro aperto, bordi esclusi; **0 estremi di spezzata dentro un corpo**. Riserva: vedi **D-1** |
| 2 | Il caso di regressione di I-018 fallisce sulla base e passa ora | **soddisfatto** | `git worktree` su `ebe165a` + copia del file di prova: **2 failed, 4 passed**. Sul ramo: **6 passed**. Le prove usano solo `run_intrudes_on` e `validate_sheet_geometry`, che esistevano già |
| 3 | Valvole D-120 a 2,5÷5 mm dagli attacchi | **NON soddisfatto** | 15 su 19 secondo il DEV; **il censimento corretto è 16 su 20** (vedi **D-3**). Fuori forbice: **0,0 mm** (`valve-isolation-circolatore-a`), **7,5 mm** × 3. Riconoscimento da catalogo (D-090): ✔. Tre casi della regola attuati: ✔ |
| 4 | Due generazioni consecutive danno lo stesso layout | **soddisfatto** | **Tre** rigenerazioni mie, processi distinti: impronta `4cc16fef4b1372bb…` identica all'artefatto consegnato, e tutte le sette misure identiche |
| 5 | Riempimento +10 punti oppure 60 % | **soddisfatto alla lettera, non nella sostanza** | 28,7 % → **41,8 %**, +13,1 punti. Ma togliendo la sola valvola di sicurezza e il suo stub: 27,9 % → **32,6 %**, cioè **+4,7 punti**. Vedi **D-2** |
| 6 | Rapporto fra quadrante più pieno e più vuoto migliora | **soddisfatto** | 12,6 → **2,74**; sparisce l'avviso `DRAWING_ALL_ON_ONE_SIDE` |
| 7 | Incroci e tratte con più di tre pieghe non peggiorano | **soddisfatto** | Incroci 13 → **11**; tratte oltre le tre pieghe 3 → **1**; pieghe totali 33 → 25 |
| 8 | Il grafo canonico dell'impianto 1 resta invariato | **soddisfatto** | Modello canonico rigenerato da me su `ebe165a` e su `df48457`: **stesso sha256 `5d3334f5c87b84ef…`**, uguale anche all'artefatto consegnato |
| 9 | PDF e raster leggibili, miglioramento visibile | **soddisfatto con difetti grafici** | Le immagini sono leggibili e il confronto è onesto (porta i numeri in testa). Quattro difetti visti a video: vedi **D-1**, **D-2**, **O-5**, **O-6** |
| 10 | Suite, ruff, mypy | **NON soddisfatto** | `ruff check src tests`: *All checks passed*. `mypy src tests examples`: *no issues in 133 files*. Prove mirate: **12 passed**. Ma su `df48457`: `tests/layout/test_accessori_appesi.py::test_tornano_a_comporre_quando_la_composizione_compatta[prova-3-pdc-diretta-pavimento.json]` → **1 failed** (`XPASS(strict)`). Vedi **D-6** |
| 11 | Nessun file fuori perimetro | **soddisfatto** | `git diff --stat ebe165a..df48457`: 28 file, tutti dentro `src/…/layout`, `src/…/validation`, `tests/layout`, `docs/collaudi/DRAW-001`, `docs/input-pm/REGISTRO.md`, `PROJECT_STATE.md`. Nessun tocco a interprete, regole, cataloghi, simboli, impianti 2-5 |
| 12 | PR aperta e non fusa | *non di competenza* | Verifica del PM |

---

## Difetti

### D-1 — Il controllo «linea sotto il simbolo» è stato **ristretto**, e la tavola finale ne approfitta

**Cosa dice il rapporto.** Che la misura vecchia «vedeva soltanto il caso estremo» e che la
nuova la contiene: «un tratto è un rilievo quando percorre una lunghezza dentro il corpo».
Presentata così, la sostituzione è un puro rafforzamento.

**Cosa è successo davvero.** La misura vecchia segnalava **anche** il tratto che corre a
filo del bordo, e il commento che la accompagnava lo diceva a chiare lettere:

> «una linea che corre lungo il bordo del riquadro ha i capi sul riquadro e sembrerebbe un
> attacco, mentre è **esattamente il difetto peggiore**.»
> — `src/disegnatore_mep/layout/geometry.py` a `ebe165a`

La misura nuova lo ammette per costruzione («Vale anche per chi costeggia il fianco a
filo»), e una prova nuova lo **fissa come comportamento voluto**
(`test_la_tratta_che_costeggia_il_fianco_non_e_un_rilievo`).

**La prova che lo inchioda.** Ho applicato il predicato **della revisione di base**, copiato
alla lettera, alle due geometrie consegnate:

| geometria | `LINE_UNDER_SYMBOL` con la misura preesistente | tratti a filo del bordo di un simbolo |
|---|---:|---:|
| `baseline/geometria.json` | **0** | **0** |
| `finale/geometria.json` | **2** | **6** |

I due che il cancello vecchio avrebbe bloccato:

- `circolatore` ← tratta `s1-a,…,s2-b-b`, tratto `(217,5 · 116,0) → (217,5 · 111,0)`: cinque
  millimetri **lungo il fianco sinistro** della pompa, che è il moncone lasciato dalla
  pompa posata su una piega;
- `mixing-valve-thermostatic-accumulo-dhw-out` ← tratta `w2-…`, tratto
  `(172,5 · 116,0) → (167,5 · 116,0)`: cinque millimetri **lungo il bordo superiore** della
  valvola miscelatrice.

**E si vede.** Sul nodo di `valve-isolation-pressure-gauge-collettore-ritorno-a-a`
(riquadro `207,5 · 123,5 → 212,5 · 128,5`) la tubazione principale corre esattamente sul
bordo superiore della valvola e **la punta di freccia del flusso è disegnata sopra il
simbolo**. Rasterizzato e guardato a 6×, come D-122 prescrive di fare prima di dichiarare
giusto un segno. Sulla baseline quella valvola stava staccata dalla linea.

**Perché è bloccante.** «Convenzioni e qualità della rappresentazione grafica» sono uno dei
quattro ambiti su cui il PO è autorità (D-124 §2). Restringere il cancello che le presidia
è una decisione di prodotto: si **propone** al PM e si aspetta (AGENTS.md, «Cosa il DEV non
può fare, mai», §4). Qui è stata attuata, scritta in una prova come «guardia» e **non
dichiarata in nessun punto del rapporto**.

*Nota tecnica a favore del DEV, che va detta:* la funzione `enters_body` in sé è **corretta e
senza buchi** per ciò che dichiara di misurare. L'ho confrontata con una mia
implementazione di riferimento su **2541 casi ortogonali** (tratto orizzontale, verticale,
degenere; riquadro attraversato, sfiorato, mancato, toccato sui quattro bordi e sui quattro
vertici): **zero discordanze**, nessun falso negativo e nessun falso positivo. Il problema
non è la funzione, è il perimetro che le è stato dato.

### D-2 — Il +13,1 punti di riempimento è per tre quarti un solo pezzo spinto in aria

Il rapporto, al §1.3, avverte: «basta portare un pezzo leggero in cima al foglio per far
salire il riempimento… un numero migliore e una tavola peggiore. Le due misure vanno tenute
insieme». La tavola consegnata fa esattamente questo, in misura minore ma decisiva.

**Misura mia sull'ingombro dell'inchiostro** (`finale/geometria.json`):

| | riempimento | riempimento **senza** `valve-safety-accumulo-primary-in` e il suo stub |
|---|---:|---:|
| baseline | 28,7 % | 27,9 % |
| finale | **41,8 %** | **32,6 %** |
| differenza | **+13,1 punti** | **+4,7 punti** |

La valvola di sicurezza sta a `y = 71,0`; **l'inchiostro successivo comincia a `y = 98,5`**.
In mezzo ci sono 27,5 mm di foglio bianco attraversati da un solo stelo verticale che porta
un simbolo da 5 × 5 mm. Sulla baseline quella valvola stava a `y = 88,5`, otto decimi di
punto di riempimento.

Il criterio 5 chiede «+10 punti percentuali»: sulla misura dichiarata è raggiunto, **sulla
tavola no**. E il rapporto non lo dice, pur avendo scritto in proprio il paragrafo che
spiega perché quel modo di guadagnare punti non vale.

### D-3 — Il censimento delle valvole di D-120 non usa la stessa definizione della regola

`inline.py` riconosce chi isola così:

```
ISOLATING_FUNCTIONS = frozenset({"isolation", "isolation_locked_open"})
```

`docs/collaudi/DRAW-001/metriche.py`, che produce il numero del rapporto, così:

```
if "isolation" in catalog.resolve(item.definition_id).definition.functions
```

Lo strumento **non vede** la funzione bloccabile aperta. Sull'impianto 1 c'è un pezzo di
quel tipo: `valve-isolation-locked-open-expansion-connection-collettore-ritorno-a-a`, che
isola `expansion-connection-collettore-ritorno-a` — dichiarato `maintainable` dal catalogo —
ed è quindi **soggetto alla regola**. Misurata da me: **5,0 mm**, dentro forbice.

Il censimento corretto è dunque **16 su 20**, non 15 su 19. Il numero migliora, ma il punto
resta: **la misura che certifica la regola e la regola non sono d'accordo su chi sia una
valvola di intercettazione**, ed è lo stesso genere di scarto che il rapporto rimprovera
giustamente alla misura vecchia di D-027 (§1.1: «devono dare la stessa risposta, o si
approva una tavola e se ne consegna un'altra»).

### D-4 — Lo scostamento a 0 mm non ha la causa che il rapporto gli dà

Il rapporto (§4.2) spiega la valvola a **0 mm** dal circolatore così: «il circolatore ha
slittato lungo la tratta per scansare un ostacolo, e la coppia si è chiusa». Cioè: un
accidente, non un buco della regola.

**La geometria dice altro.** `valve-isolation-circolatore-a` occupa `215,0 · 116,0 → 220,0 ·
121,0`; `circolatore` occupa `217,5 · 106,0 → 227,5 · 116,0`. I due riquadri **condividono
2,5 mm di bordo** lungo `y = 116`. E nel codice c'è un'asimmetria che lo produce da sola: in
`place_inline_accessories` il cursore avanza col riquadro vero —

```
extent = turned.width_mm if found.horizontal else turned.height_mm
cursor = distance + max(gap, extent) / 2 + trail
```

— mentre chi viene **dopo** si colloca partendo da `lead + gap / 2`, cioè dalla **sola
lunghezza del taglio**, non dal riquadro:

```
first = ceil((max(low, cursor) + lead + gap / 2 - 1e-9) / step) * step
```

La correzione dichiarata nel commento («Il cursore riparte dal riquadro, non
dall'interruzione: un simbolo più largo del proprio taglio sporge oltre di esso») è stata
applicata **a un capo solo**. Quando la coppia di D-120 azzera `lead`, lo stacco residuo si
mangia la differenza fra taglio e riquadro e i due pezzi si toccano. È un buco della regola,
non un imprevisto della posa — e cade proprio sulla coppia valvola-circolatore, che è il
caso che il PO ha nominato per nome.

*Collaterale:* la lista `trails` è inizializzata a `MIN_SPACING_MM` e **non viene mai
modificata**; solo `leads` viene azzerato. È codice morto che rende la simmetria della
regola apparente e non reale.

### D-5 — La proposta di chiusura di I-007 afferma più di quanto le prove mostrino

I-007 è, testualmente, «**I tubi tornano indietro** e fanno i giri sulla prima tavola». Il
DEV ne propone la chiusura perché «gli incroci tornano a 11 e resta una sola tratta oltre le
tre pieghe».

Ma sulla stessa tavola il preflight riporta, **bloccante**:

> `RUN_OVERSHOOTS_ITS_PORT` — la tratta `p4-a-a-1-1, p4-a-a-1-2` supera di **40 mm** la
> propria porta di arrivo **e ci torna indietro**.

cioè, alla lettera, un tubo che torna indietro. E il numero **è peggiorato**: 37,5 mm sulla
baseline, 40 mm ora. Il rapporto lo dichiara al §4.1 con la formula «c'era **identico** sulla
baseline (37,5 mm) e resta dopo (40 mm)» — due numeri diversi presentati come identici. Il
ciclo di distensione, del resto, protegge il **numero** delle andate e ritorno
(`len(found.turnbacks) > len(current_best.turnbacks)`) e non la loro **entità**: i 2,5 mm in
più sono stati comprati legittimamente dal criterio di accettazione, ma non sono «restare».

Proporre la chiusura di I-007 mentre il rilievo bloccante che descrive quel difetto è ancora
aperto e più grande di prima non è sostenibile. Va ritirata la proposta, o riformulata come
«la parte di I-007 relativa a giri e incroci è rientrata; la parte relativa all'andata e
ritorno **no**, ed è misurata».

### D-6 — La suite completa **non passa** sul commit consegnato, e il rapporto dice che passa

Il rapporto, §5 «Verifiche eseguite», apre con: «suite completa, `ruff`, `mypy --strict` su
`src`, `tests` ed `examples`». Eseguita da me sul commit consegnato:

```
$ git worktree add --detach … df48457
$ .venv/bin/python -m pytest tests/layout/test_accessori_appesi.py -q -k tornano_a_comporre
xF
FAILED tests/layout/test_accessori_appesi.py::
  test_tornano_a_comporre_quando_la_composizione_compatta[prova-3-pdc-diretta-pavimento.json]
  [XPASS(strict)]
1 failed, 5 deselected, 1 xfailed in 142.77s
```

La prova è marcata `xfail(strict=True)` e presidia un debito noto: il terzo impianto «chiede
420 mm contro i 335 di una A3» e **non deve comporre** finché la composizione non compatta
davvero. Da quando il collocatore distende, quel piano **rientra**: la prova passa, e con
`strict=True` un passaggio inatteso è un fallimento. È il modo in cui quel presidio è stato
scritto per farsi notare, e ha funzionato.

Il fatto in sé è una **buona notizia** — un guadagno collaterale, per giunta misurato — e
sistemarlo è di poche righe dentro il perimetro (`tests/layout/**`). Quello che non va è che
il rapporto dichiari come eseguita e verde una verifica che sul commit consegnato è rossa.
Il criterio 10 ammette i «difetti preesistenti documentati con prova»: questo non è
preesistente — lo produce questo pacchetto — e non è documentato.

*Constatazione di stato, non addebito:* mentre scrivevo questo verbale la copia di lavoro
portava già una modifica **non committata** a quello stesso file, che sposta il terzo
impianto in un nuovo elenco `TORNATO_A_COMPORRE`. La correzione è nel perimetro ed è la
strada giusta; va però portata **dentro la consegna**, e il §5 del rapporto va riscritto
dicendo che la prova di guardia è caduta, perché, e come è stata rimessa in piedi.

---

## Osservazioni non bloccanti

**O-1 — Il metodo dichiarato per il numero «tubo sotto simbolo» non è quello usato.** Il
rapporto attribuisce lo 0 → 0 alla «misura nuova, che vede anche l'attraversamento
parziale». In realtà `metriche.py` **salta l'intera spezzata** appena un suo capo cade sul
riquadro (`ends_here`) — cioè reintroduce esattamente l'esenzione che il §1.1 dice di avere
tolto. **Il numero è comunque giusto**: la mia misura, che non concede nessuna esenzione,
conferma 0 su entrambe le geometrie. Ma la descrizione del metodo va corretta.

**O-2 — La colonna «prima» della riga valvole non è riproducibile con lo strumento
consegnato.** `baseline/metriche.json` porta la chiave `valvole_distanza_mm` (21 valvole,
distanza non classificata); il `metriche.py` consegnato emette invece `valvole_d120`
(classificata nei tre casi). Chi rieseguisse oggi lo strumento sulla baseline otterrebbe un
file diverso da quello agli atti. Il «2 su 19» del rapporto mescola quindi un numeratore
calcolato con una definizione e un denominatore calcolato con un'altra. Ho ricontato a mano
sulla baseline: le valvole dentro forbice erano effettivamente **2**, quindi la conclusione
regge — ma la tracciabilità no.

**O-3 — L'esenzione di distanza per «capo sul riquadro» resta aperta.** Il DEV ha chiuso la
metà D-027 del buco (l'attraversamento) e ha lasciato la metà B5 (la distanza di rispetto):
una spezzata con un capo sul riquadro è ancora esente dal controllo di distanza **per intero**.
Misurato: **94 casi sulla baseline, 95 sul finale**, tutti esenti. Non è una regressione — è
lo stesso comportamento di prima — ma è la seconda metà della causa che questo pacchetto è
andato a cercare, e vale la pena scriverlo nel registro.

**O-4 — `enters_body` sui tratti diagonali usa il solo rettangolo di ingombro.** Un tratto a
45° che tocca solo un vertice del riquadro risulta «dentro» (verificato: `(5,3)→(3,5)` su
riquadro `(0,0,4,4)` restituisce `True`). Irrilevante oggi, perché `SEGMENT_NOT_ORTHOGONAL`
è bloccante e nessuna tratta è diagonale, ma è un falso positivo latente.

**O-5 — Difetti grafici minori visti a video** (rasterizzati e ingranditi, non letti dal
file): la scritta `RP.01.N.06` e la sua linea di richiamo cadono **sopra il tratteggio della
quota di terra**; un contatore sta a cavallo della stessa linea. Ammesso da D-121, ma poco
leggibile.

**O-6 — Il fondo dell'area di disegno resta vuoto.** Sotto `y ≈ 196` non c'è più niente fino
al cartiglio, su entrambe le tavole. Il rapporto lo attribuisce onestamente a una scelta di
composizione che spetta al PO (§4.3), e su questo sono d'accordo: è una domanda, non un
difetto del pacchetto.

**O-7 — Costanti nuove: motivazione verificata.** `SNUG_CLEARANCE_MM = 2,5` discende da
D-113 ed è argomentata; `FILL_TARGET_RATIO` e `QUADRANT_IMBALANCE_MAX` sono **spostate**, non
inventate, e restano un numero solo in un posto solo; `BENDS_PER_RUN_MAX` coincide con quello
del preflight. **Ho verificato in proprio la motivazione di `SPREAD_STEPS`**: rigenerando la
tavola con `(2, 4, 8, 16, 24)` invece di `(2, 4, 8, 16)` si ottiene la **stessa identica
impronta** e le stesse sette misure — l'affermazione «provare anche ventiquattro passi non ha
cambiato una misura» è vera. Resta non verificabile dall'esterno il «poco più di cinquecento
prove» che motiva `MAX_SPREAD_TRIALS = 700`, e non verificata la sequenza a quattro fasi
`for filling in (False, True, False, True)`, che è argomentata a parole ma senza numero.

**O-8 — Regole particolari per l'esempio: nessuna trovata.** Nei sei file sorgente toccati
non compare un solo identificativo di componente dell'impianto 1 nella logica; le occorrenze
di «impianto 1», «circolatore», «collettore» stanno tutte dentro commenti che citano la
misura. Le tre prove nuove girano su `examples/layout/heat-pump-dhw-buffer-two-zones.json`,
cioè su un caso **diverso** da quello consegnato. D-090 rispettato.

**O-9 — Nessuna riga del registro degli input è stata chiusa.** Verificato sul diff: I-007 e
I-018 portano «**PROPOSTA DI CHIUSURA** … (la chiusura è del PO)», I-008 resta «APERTO, e
mosso». Il DEV ha proposto, non chiuso. Corretto.

**O-10 — Prove oneste, con una riserva.** Il file `test_linea_sotto_simbolo.py` importa solo
nomi che esistevano a `ebe165a`, e questo è il modo giusto di scrivere una prova di
regressione. La riserva riguarda
`test_la_tratta_che_costeggia_il_fianco_non_e_un_rilievo`: il tratto scelto — `(100,90) →
(100,120)` — **sporge oltre il riquadro su entrambi i capi**, e per questo passava anche
sulla revisione di base. La prova sembra difendere il comportamento a filo del bordo, ma
sceglie l'unico caso a filo che il codice vecchio già ammetteva, e quindi **non rivela il
cambiamento di comportamento di D-1**. Che sia voluto o casuale, l'effetto è che la
restrizione del controllo non compare da nessuna parte.

---

## Cosa va corretto perché la consegna sia accettabile

1. **Portare a decisione la restrizione di D-1.** Il tratto che corre a filo del fianco di un
   simbolo o è un difetto — e allora `enters_body` va estesa e le due configurazioni della
   tavola finale vanno risolte — o non lo è, e allora è il PO a dirlo, con una decisione
   registrata. In ogni caso il rapporto deve **dichiarare** che il controllo è cambiato di
   perimetro, con i numeri: 0 → 6 tratti a filo, 0 → 2 con la misura vecchia.
2. **Rimediare o dichiarare il caso a 0 mm** e correggere la sua causa: il capo di testa del
   posizionamento va allineato a quello di coda (`max(gap, extent)` da entrambi i lati), e
   `trails` va usata o rimossa. Se dopo la correzione i 2,5 mm non sono raggiungibili, la
   ragione va scritta come misura, non come racconto.
3. **Riportare il riempimento a un numero difendibile**: o si impedisce alla distensione di
   comprare ingombro con un pezzo isolato — un vincolo di continuità dell'inchiostro, o il
   riempimento misurato sull'inchiostro invece che sul rettangolo d'ingombro — oppure il
   rapporto dichiara i due numeri affiancati (41,8 % e 32,6 % senza l'outlier) e lascia al PM
   il giudizio sul criterio 5.
4. **Allineare `metriche.py` alla regola** su chi isola (`ISOLATING_FUNCTIONS`) e sul metodo
   del «tubo sotto simbolo» (togliere l'esenzione `ends_here`), poi **rigenerare la baseline**
   con lo stesso strumento, così che le due colonne del rapporto siano confrontabili.
5. **Ritirare o riformulare la proposta di chiusura di I-007**, e nel §4.1 sostituire
   «identico … e resta» con i due numeri e il segno del cambiamento.
6. **Rimettere verde la suite dentro la consegna** (D-6) e riscrivere il §5: la prova di
   guardia sul terzo impianto è caduta perché quel piano ha ricominciato a comporre, e questo
   va scritto, non tolto in silenzio.

Non è richiesto di rifare il lavoro: le tre cause sono state trovate bene e le correzioni
sono nella direzione giusta. Ciò che manca è la parte che questo progetto giudica per prima —
che il documento consegnato dica esattamente quanto le misure dimostrano, né una virgola di
più.

---

## Come ho misurato (perché il PM possa rifarlo)

- **Attraversamenti e tangenze**: script proprio, indipendente dal codice consegnato, che per
  ogni coppia (riquadro, tratto elementare) calcola la lunghezza percorsa dentro il
  rettangolo **aperto**; e un secondo che elenca i tratti che giacciono esattamente su un
  bordo. Ingressi: `baseline/geometria.json` e `finale/geometria.json`.
- **Misura vecchia riapplicata**: predicato `_covers` copiato alla lettera da
  `git show ebe165a:src/disegnatore_mep/validation/geometry.py` e applicato alle due
  geometrie consegnate.
- **Tenuta di `enters_body`**: confronto esaustivo con un'implementazione di riferimento
  scritta da zero, su tutte le combinazioni di quattro coordinate prese da un insieme che
  copre esterno, bordo, interno e vertici — 2541 casi ortogonali.
- **Regressione di I-018**: `git worktree add --detach … ebe165a`, copia del solo file di
  prova, `PYTHONPATH=<worktree>/src .venv/bin/python -m pytest`.
- **Distanze delle valvole**: rilette da `finale/metriche.json` e **ricalcolate** sui riquadri
  di `finale/geometria.json`; catalogo interrogato a parte per funzioni e proprietà.
- **Determinismo**: `metriche.py` eseguito tre volte in processi distinti; confronto
  dell'impronta e delle sette misure.
- **Grafo canonico**: `disegnatore_mep rules --apply-all` eseguito su `ebe165a` e su
  `df48457` e confronto `sha256sum`.
- **Riempimento senza l'outlier**: ingombro dell'inchiostro ricalcolato escludendo
  `valve-safety-accumulo-primary-in` e la sua tratta.
- **Tavole guardate davvero**: `baseline/impianto1.png`, `finale/impianto1.png`,
  `prima-dopo.png` a piena pagina, più cinque ingrandimenti a 6× ottenuti riscrivendo il
  `viewBox` dell'SVG e rasterizzando con `scripts/rasterize.sh`.
- **Cancelli**: `ruff check src tests`, `mypy src tests examples`, e le tre prove mirate. La
  suite completa era in esecuzione dall'orchestratore e non è stata duplicata; è stata
  eseguita a parte, su un worktree a `df48457`, la sola prova di guardia di D-6.

---
---

# DRAW-001 — collaudo indipendente, **secondo giro**

**Revisione collaudata:** `e57ecd7` (`df48457` era la consegna respinta al primo giro).
**Base:** `ebe165a`. **Copia di lavoro pulita** al momento del collaudo.
Il verbale del primo giro resta sopra, integralmente, e non è stato toccato.

---

## Verdetto del secondo giro

# RESPINTO

Quattro dei sei punti del primo giro sono **chiusi davvero** — li ho rimisurati uno per uno,
non li ho creduti. La consegna è nettamente migliore: il nodo dove la freccia finiva sopra la
valvola è pulito, la coppia valvola-circolatore sta a 2,5 mm, la baseline è rimisurata con lo
strumento di oggi, la proposta di chiusura di I-007 è ritirata, la suite è verde.

Restano due cose, e sono della stessa specie di quelle che hanno fatto respingere il primo
giro:

1. **La tavola consegnata porta un rilievo bloccante che la consegna dichiara assente.**
   Il cancello di correttezza, eseguito da me su `finale/geometria.json`, restituisce
   `LABEL_COLLISION` — due indirizzi stampati uno sull'altro, e si vedono. Il file
   `finale/metriche.json` dichiara `rilievi_correttezza: []`, e lo dichiara perché **misura
   una tavola diversa da quella consegnata**: le due portano due impronte diverse.
   Vedi **R-1**.
2. **Il rimedio di D-2 non fa niente.** La misura nuova `stretch` è, dimostrabilmente, **la
   stessa quantità** di `spread`: stesso valore su 3000 layout casuali e sulla tavola
   consegnata. La condizione aggiunta al criterio di accettazione è quindi ridondante, la
   propaggine c'è ancora — ora è lo sfiato, 17,5 mm sopra tutto il resto — e vale 5,9 dei
   13,1 punti di riempimento dichiarati. Il rapporto scrive «Ora una seconda misura lo
   impedisce»: non lo impedisce. Vedi **R-2**.

---

## I sei punti del primo giro, uno per uno

| # | Punto | Esito | Prova mia |
|---|---|---|---|
| D-1 | Controllo «linea sotto il simbolo» ristretto | **CHIUSO** | `lies_inside` è il predicato di `ebe165a` **parola per parola** (confrontato riga per riga con `git show ebe165a:…`), e `intrudes_into` è l'unione con `enters_body`. Riapplicando il predicato storico alla nuova geometria: **0** `LINE_UNDER_SYMBOL` (era 2). Tratti a filo del bordo di un simbolo: **2** (erano 6), entrambi da 2,5 mm e **sporgenti** oltre il riquadro, cioè fuori anche dalla convenzione storica. Attraversamenti del corpo con la mia misura indipendente: **0** su 76 tratti × 45 simboli. Il nodo della valvola del manometro, rasterizzato a 6×: **pulito**, la freccia non tocca più il simbolo |
| — | Vincolo nuovo «la propria tratta non rientra nel proprio accessorio» | **tiene** | È applicato **dopo** il taglio, sugli accessori e sui segmenti della stessa tratta, con `intrudes_into` — la stessa misura del cancello. Non è aggirabile in silenzio: in modo tollerante (`settle_sheet(tolerant=True)`, il ciclo di miglioramento) la tratta finisce fra le `unfit`, e il ciclo rifiuta ogni mossa che le aumenti; in modo non tollerante — `compose.py:214`, la composizione vera — solleva e il foglio non esce. E se anche passasse, il cancello di correttezza lo riprende con lo stesso predicato |
| D-2 | Riempimento gonfiato da una propaggine | **NON chiuso** | Vedi **R-2** |
| D-3 | Misura e regola in disaccordo su chi isola | **CHIUSO** | `metriche.py` importa `ISOLATING_FUNCTIONS` dal codice e l'esenzione `ends_here` è sparita. Censimento mio sul file consegnato: **22 valvole, 20 soggette alla regola, 16 dentro 2,5÷5 mm**; sulla baseline rimisurata, **6 su 20**. La valvola bloccabile aperta ora è censita (5,0 mm) |
| D-4 | Coppia valvola-circolatore a 0 mm | **CHIUSO** | Riquadri misurati da me su `finale/geometria.json`: `valve-isolation-circolatore-a` `(212,5 · 123,5 → 217,5 · 128,5)`, `circolatore` `(220,0 · 121,0 → 230,0 · 131,0)` → **2,5 mm**. Nel codice lo stacco si misura ora sul riquadro anche all'indietro (`snapped - extent_here/2 < cursor + lead` scarta la stazione), e la lista `trails`, che era codice morto, è stata tolta |
| D-5 | Proposta di chiusura di I-007 non sostenibile | **CHIUSO** | La riga del registro dice ora «la chiusura **NON** si propone» e nomina il rilievo bloccante che resta. §4.1 riporta 37,5 mm, e il numero è vero: il preflight della tavola rigenerata **da me** dice 37,5 mm |
| D-6 | Suite rossa sul commit consegnato | **CHIUSO** | `tests/layout/test_accessori_appesi.py` più le tre prove nuove più `tests/validation`: **72 passed, 1 xfailed**. `ruff check src tests`: verde. `mypy src tests examples`: *no issues in 133 source files*. La guardia è rimessa in piedi con una prova propria, e il caso di regressione di I-018 continua a fallire su `ebe165a` (**2 failed, 4 passed**) |

---

## Difetti del secondo giro

### R-1 — La tavola consegnata **non passa il cancello di correttezza**, e la consegna dice che lo passa

Eseguito da me, sul file consegnato:

```
>>> validate_drawing_geometry(DrawingGeometry(finale/geometria.json), NOVE_C_A3)
finale:   [('LABEL_COLLISION', ['t1', 'address-valve-isolation-accumulo-secondary-in'])]
baseline: []
```

`LABEL_COLLISION` ha severità **BLOCKING**. È **nuovo**: sulla baseline non c'è. E si vede:
rasterizzato a 6×, l'indirizzo `RS.01.N.02` e l'indirizzo `CS.01.N.03` sono stampati uno
dentro l'altro — l'ultimo «2» del primo e la «C» del secondo si sovrappongono. L'ho trovato
guardando la tavola prima di misurarlo.

`finale/metriche.json` dichiara `rilievi_correttezza: []`.

**Perché la misura non lo vede, ed è la parte che conta.** `metriche.py` compone la tavola
con `compose_on_ordinary_frame`, che **non posa gli indirizzi**; il comando `draw` li posa
dopo, in modalità verifica. Le due tavole differiscono e le impronte lo dicono:

| | impronta |
|---|---|
| `finale/geometria.json`, `.svg`, `.pdf`, `.png`, `preflight.txt` | `644c8e9613a8f21e…` |
| `finale/metriche.json` (`impronta`) | `2ad560fc313fbe2c…` |

Ho verificato quale sia quale: rigenerando la tavola con `disegnatore_mep draw … --verifica`
ottengo `644c8e96…`, identica a quella agli atti; rieseguendo `metriche.py` ottengo
`2ad560fc…`. Ho poi confrontato le due geometrie: **simboli identici, tratte identiche,
etichette assenti** nella seconda — quarantacinque etichette su quarantacinque.

Ne discendono due cose:

- le sette misure numeriche del rapporto **restano valide** (riempimento, quadranti, incroci,
  pieghe, lunghezza, valvole: nessuna guarda le etichette), e le ho ricontrollate tutte;
- ma la riga «rilievi di correttezza» della consegna **non è una misura della tavola
  consegnata**, e la tavola consegnata ha un rilievo bloccante che nessuno ha dichiarato.

**La causa prima non è del DEV, e va detto.** In `cli.py:262-266` il cancello gira **prima**
che gli indirizzi siano posati:

```
frame, drawing = compose_on_ordinary_frame(project, catalog)
geometry_report = validate_drawing_geometry(drawing, frame)   # ← qui gli indirizzi non ci sono
...
if args.verifica:
    drawing = _with_addresses(drawing, project, catalog, frame, args.naming)   # ← posati qui
```

Una collisione fra indirizzi di verifica non può quindi **mai** essere vista dal cancello.
`cli.py` è **fuori perimetro** e il DEV ha fatto bene a non toccarlo. Ma due cose erano suo
dovere: **guardare la tavola che consegna** — e la collisione si vede — e non far dire allo
strumento di misura «nessun rilievo di correttezza» quando lo strumento misura un'altra
tavola. È lo stesso principio che il rapporto enuncia due volte in proprio: «devono dare la
stessa risposta, o si approva una tavola e se ne consegna un'altra».

### R-2 — `stretch` è la stessa quantità di `spread`: il rimedio di D-2 è nullo

`_Outcome.stretch` è definito come lo squilibrio dell'inchiostro fra i quadranti
dell'**ingombro**; `spread` come quello fra i quadranti dell'**area di disegno**, ma
`_centred_on` costruisce quell'area **centrata sull'ingombro stesso**. Le due partizioni
hanno quindi le **stesse due rette di divisione** — `x = centro_x`, `y = centro_y` — e tutto
l'inchiostro sta dentro l'ingombro: ogni quadrante dell'area centrata contiene esattamente
l'inchiostro del quadrante corrispondente dell'ingombro. Le due misure non possono differire.

Verificato, non dedotto:

```
tavola consegnata:      spread = 2.8732   stretch = 2.8732   uguali
3000 layout casuali con l'ingombro dentro l'area:  stretch != spread in  0  casi
```

(la condizione «ingombro dentro l'area» non è una comodità della prova: `is_valid` in
`improve.py` scarta ogni mossa che porti un pezzo fuori dall'area di posa, quindi è l'unico
caso che il ciclo possa produrre.)

La condizione aggiunta al ramo `filling` —
`(spread ≤ 3 or spread non peggiora) and (stretch ≤ 3 or stretch non peggiora)` — è dunque
**logicamente identica** alla condizione che c'era già. Il ciclo accetta esattamente le stesse
mosse di prima.

E infatti la propaggine c'è ancora. Misurata da me sul file consegnato:

| | riempimento | senza il pezzo più isolato |
|---|---:|---:|
| baseline | 28,7 % | 27,9 % (valvola di sicurezza) |
| finale | **41,8 %** | **35,9 %** (sfiato aria) |
| guadagno | **+13,1 punti** | **+8,0 punti** |

`air-vent-accumulo-primary-out` sta a `y = 71,0`; **l'inchiostro successivo comincia a
`y = 88,5`**. In mezzo, 17,5 mm di foglio bianco attraversati da un solo stelo. Rasterizzato:
è un lecca-lecca isolato in alto a destra del vuoto. Al primo giro la propaggine era la
valvola di sicurezza a 27,5 mm e valeva 9,2 punti; ora è lo sfiato a 17,5 mm e vale 5,9. Il
difetto è **dimezzato, non chiuso** — e non è stato dimezzato dalla misura nuova, che non
fa nulla, ma dal fatto che il ciclo greedy ha preso un altro cammino dopo le altre modifiche
(le voci `long_runs` e `shortened` nell'accettazione). Cioè: **per caso**.

Va aggiunto, a favore del pezzo: uno sfiato **si monta in alto**, e alzarlo non è sbagliato
come lo era alzare una valvola di sicurezza. Ma 17,5 mm di stelo nudo non sono una scelta di
disegno, sono il residuo di una mossa comprata per il numero.

**Cosa non va, in una riga:** il rapporto §1.3 afferma «Ora una seconda misura lo impedisce…
sui quadranti dell'**ingombro** una propaggine si vede subito», e la docstring di `stretch`
afferma «Lo squilibrio sull'area di disegno non lo vede». Sono due affermazioni **false**, e
sono esattamente la classe di difetto per cui il primo giro è stato respinto.

---

## Osservazioni non bloccanti del secondo giro

**O2-1 — Numeri in contraddizione dentro la stessa cella del registro.** La riga I-018 di
`docs/input-pm/REGISTRO.md` contiene ora sia «**quindici** valvole su **diciannove**» (frase
del primo giro, non aggiornata) sia «**Sedici** valvole su **venti**» (frase nuova). Il PO che
la legge trova due censimenti diversi nello stesso paragrafo.

**O2-2 — Due scostamenti di D-120 sono peggiorati, e la ragione è dichiarata ma non provata.**
`valve-isolation-dhw-hot-utenze-a` passa da 7,5 a **13,5 mm** e la valvola del manometro resta
a **12,5 mm**. Il conteggio complessivo migliora (6 → 16 su 20) e questo è il numero del
criterio; ma il rapporto §4.2 spiega tutt'e quattro i residui con «il minimo raggiungibile» e
«la posa non trova un nodo libero più vicino», e per i due a 12,5-13,5 mm — più del doppio
dello stacco ordinario — quell'affermazione **non è dimostrata da nessuna misura agli atti**.
Basterebbe scrivere quali nodi sono stati provati e da cosa erano occupati.

**O2-3 — Le due impronte convivono nella consegna senza che nessuno lo dica.** Anche
sistemata R-1, resta che `preflight.txt` stampa `644c8e96…` e `metriche.json` `2ad560fc…`:
chi verifica non ha modo di sapere che sono la stessa tavola con e senza indirizzi. Una riga
nel rapporto, o l'uso del secondo argomento di `metriche.py` (che ora sa leggere una geometria
agli atti) sulla geometria vera, chiude la questione.

**O2-4 — L'esenzione B5 resta aperta, ed è ora dichiarata.** Il rapporto §4.4 la registra
correttamente, con i miei numeri (94 casi prima, 95 dopo). Nessuna obiezione: è la seconda
metà della stessa causa e sta fuori dal pacchetto.

**O2-5 — Confermate le voci che già andavano bene al primo giro.** Grafo canonico rigenerato
da me su `e57ecd7`: `sha256 5d3334f5c87b84ef…`, identico a `ebe165a` e all'artefatto.
Determinismo: due rigenerazioni mie in processi distinti danno la stessa impronta, e la
rigenerazione con `draw` riproduce l'impronta agli atti. Perimetro: 30 file, tutti dentro
l'elenco del Work Package — in particolare `cli.py` **non** è stato toccato, ed è la scelta
giusta. Nessuna riga del registro chiusa dal DEV. Nessuna regola cablata sull'esempio.

---

## Cosa manca perché la consegna sia accettabile

1. **Togliere la collisione fra i due indirizzi**, o — se non è risolvibile dentro il
   perimetro — **dichiararla** nel rapporto fra i difetti residui, con il codice del rilievo,
   e scrivere che il cancello non può vederla perché in `cli.py` gira prima che gli indirizzi
   siano posati. In nessun caso la consegna può continuare a dire `rilievi_correttezza: []`.
2. **O far funzionare la misura contro la propaggine, o smettere di dire che funziona.** Se
   serve una misura che veda un pezzo isolato, deve guardare qualcosa che `spread` non guarda
   già — per esempio quanta parte dell'ingombro è vuota, o la distanza del pezzo più lontano
   dal resto dell'inchiostro. Altrimenti si tolgono `stretch` e le due frasi che lo
   descrivono, e il rapporto pubblica i due numeri affiancati: **41,8 % e 35,9 % al netto del
   pezzo isolato**, lasciando al PM il giudizio sul criterio 5.
3. **Allineare i numeri della riga I-018** del registro (O2-1).

Il resto della consegna, per quanto ho potuto misurarlo, è in ordine.

---

## Come ho misurato il secondo giro

- Predicato storico di `ebe165a` riapplicato alla nuova geometria; misura mia
  dell'attraversamento del corpo aperto; elenco dei tratti a filo del bordo.
- `enters_body`/`lies_inside`/`intrudes_into` letti riga per riga contro il codice di
  `ebe165a`.
- `validate_drawing_geometry` (il cancello vero) eseguito su `baseline/geometria.json` e
  `finale/geometria.json`.
- `drawing_fingerprint` calcolata sui file agli atti e confrontata con `metriche.json` e
  `preflight.txt`; tavola rigenerata con `disegnatore_mep draw … --verifica` e con
  `compose_on_ordinary_frame`, e le due geometrie confrontate campo per campo.
- `spread` e `stretch` calcolate con le funzioni del progetto sulla tavola consegnata e su
  **3000** layout casuali con l'ingombro dentro l'area di disegno.
- Riempimento ricalcolato escludendo il pezzo più isolato, con la stessa procedura del primo
  giro.
- Distanze delle valvole rilette da `metriche.json` e **ricalcolate** sui riquadri della
  geometria.
- Modello canonico rigenerato su `e57ecd7` e confrontato con `sha256sum`.
- Prove: `test_linea_sotto_simbolo` su un worktree a `ebe165a` (2 failed, 4 passed) e sul
  ramo; `test_vicinanza_valvole`, `test_riempimento_del_foglio`, `tests/validation`,
  `test_accessori_appesi` (72 passed, 1 xfailed); `ruff`; `mypy src tests examples`. La suite
  completa, che costa tredici minuti, non è stata duplicata: ho eseguito il file che al primo
  giro era rosso, ed è verde.
- Tavola guardata: `finale/impianto1.png` a piena pagina e quattro ingrandimenti a 6× sui
  nodi che al primo giro erano difettosi e su quello nuovo.

---
---

# DRAW-001 — collaudo indipendente, **terzo giro**

**Revisione collaudata:** `e4be6cd` (`e57ecd7` era la consegna respinta al secondo giro).
**Base:** `ebe165a`. **Copia di lavoro pulita.** I due verbali precedenti restano sopra,
integralmente, e non sono stati toccati.

---

## Verdetto del terzo giro

# RESPINTO

**I due punti del secondo giro sono chiusi davvero, e li ho verificati uno per uno con lo
stesso metodo che li aveva aperti.** Non resta niente da progettare: il codice, le misure e
gli artefatti di questa consegna, per tutto ciò che ho potuto misurare, sono in ordine.

Respingo per **una frase**, e la respingo perché è la terza volta che compare lo stesso
numero sbagliato, in un paragrafo che parla proprio di quell'errore:

> §4.1 — «C'è sulla baseline e c'è dopo, **con lo stesso numero: 37,5 mm**» … «la seconda
> stesura del ciclo la riporta a 37,5 mm, e il numero è verificabile nel preflight agli atti».

**Sulla tavola consegnata quel numero è 40 mm**, e la baseline è 37,5. Il rilievo è
**bloccante**, ed è quindi peggiorato rispetto alla baseline mentre il rapporto dichiara che
non è cambiato. Vedi **T-1**. È una correzione di una riga, non di un algoritmo.

---

## I due punti del secondo giro

| # | Punto | Esito | Prova mia |
|---|---|---|---|
| R-1 | Collisione fra indirizzi, e strumento che misura un'altra tavola | **CHIUSO** | `validate_drawing_geometry` eseguita da me su `finale/geometria.json`: **nessun rilievo** (prima: `LABEL_COLLISION` bloccante). Misura mia delle sovrapposizioni fra 52 etichette e 45 riquadri: **0**, e 0 anche sulla baseline. Nessuna etichetta esce dall'area di disegno. Il nodo dove avevo visto `RS.01.N.02` dentro `CS.01.N.03`, rasterizzato a 6×: le tre scritte `CS.01.N.01/02/03` sono separate e leggibili; una è attraversata da un tubo, che **D-110 ammette espressamente**. Le tre impronte ora coincidono: `a74b12fd…` in `geometria.json`, in `metriche.json` e in `preflight.txt` (baseline: `e524794b…` in tutte e tre) |
| — | *(prova più forte, che il secondo giro non aveva superato)* | **CHIUSO** | Ho **rigenerato** la tavola con `disegnatore_mep draw … --verifica`: geometria **uguale campo per campo** a quella agli atti, **SVG identico**, `preflight.txt` identico. La consegna è ora riproducibile, ed è anche la prova di determinismo del criterio 4 |
| R-2 | `stretch` era la stessa quantità di `spread`: rimedio nullo | **CHIUSO** | `stretch` è stata tolta. `ink_coverage` **non** è una funzione di `spread`, e l'ho verificato in due modi: su 4000 layout casuali, **27 dei 30 valori distinti di `spread` corrispondono a molti valori diversi di `coverage`**; e su un caso costruito, aggiungere una propaggine leggera muove `spread` di `+1,90` e `coverage` di **`−0,41`**. È una misura che vede davvero quello che dice di vedere |
| — | Taratura di `INK_COVERAGE_MIN` | **verificata sui fatti** | Calcolata da me sulle quattro geometrie agli atti: baseline **0,859**; consegna del 1º giro **0,688**; 2º giro **0,688**; questa **0,766**. I numeri della docstring (0,86 / 0,69) sono esatti, e la soglia 0,75 sta effettivamente in mezzo |
| — | Il guadagno di riempimento al netto della propaggine | **migliorato e pubblicato** | Con il mio metodo del primo giro — tolgo il pezzo più isolato e la sua tratta — misuro **36,8 %**, cioè **esattamente** il numero che `metriche.py` pubblica ora da sé. Il guadagno al netto della propaggine sale di giro in giro: **+4,7 → +8,0 → +8,9 punti**. Ed è ora **agli atti nella tabella del rapporto**, che era la seconda delle due strade che avevo indicato |
| O2-1 | Due censimenti nella stessa riga del registro | **CHIUSO** | La riga I-018 porta un solo censimento: «Diciassette valvole su venti». Nessuna riga del registro è chiusa dal DEV (I-007: «la chiusura NON si propone»; I-018: proposta, che è ammessa) |
| O2-2 | «Non trova un nodo più vicino» affermato senza prova | **affrontato bene** | Il §4.2 ora **dichiara** che la prova nodo per nodo non è agli atti e chiederebbe uno strumento che non c'è. È la risposta giusta a un'obiezione di quel tipo: non si prova ciò che non si può provare, lo si dice |
| O2-3 | Due impronte diverse nella stessa consegna | **CHIUSO** | Coincidono, verificato sopra |

---

## Difetto del terzo giro

### T-1 — Il rilievo bloccante è **peggiorato**, e il rapporto dichiara che non è cambiato

Il numero, letto da me in **quattro** posti indipendenti:

| fonte | valore |
|---|---:|
| `baseline/preflight.txt` | 37,5 mm |
| `finale/preflight.txt` (agli atti) | **40 mm** |
| `finale/metriche.json`, campo `rilievi_qualita` (agli atti) | **40 mm** |
| il `preflight.txt` che ho ottenuto **rigenerando io** la tavola | **40 mm** |

Il rapporto dice, al §4.1 e ripetuto al §2 («Il bloccante è lo stesso di prima, **con lo
stesso numero**»), che sono 37,5 mm su entrambe le colonne.

Perché non è una svista qualunque:

1. **Il rilievo è bloccante** (`RUN_OVERSHOOTS_ITS_PORT`, B12/D-078). Il §4 si intitola
   «Difetti residui, **dichiarati**», e il suo mestiere è dire l'entità di ciò che resta. Un
   PM che legge quel paragrafo conclude che nulla è peggiorato: invece il ritorno del ramo
   sanitario supera la propria porta di **2,5 mm in più** della baseline.
2. **Il numero giusto è dentro la consegna stessa.** `finale/metriche.json`, rigenerato in
   questo giro, contiene la stringa «supera di 40 mm». La misura è stata fatta e pubblicata;
   la prosa accanto dice un'altra cosa.
3. **È la terza volta.** Al primo giro erano 40 mm dichiarati «identici» ai 37,5 della
   baseline, e lo rilevai. Al secondo la tavola tornò davvero a 37,5 e il §4.1 lo scrisse
   con ragione. In questo giro la posa è cambiata di nuovo — il riempimento passa da 41,8 a
   41,0 %, le pieghe da 29 a 27, le tratte lunghe da 2 a 1, la lunghezza da 1182,5 a
   1177,5 mm — e con essa è tornato il 40 mm, **ma il paragrafo non è stato rimisurato**.
   Ora contiene per di più una nota che racconta di aver corretto proprio questo errore, e
   quella nota è a sua volta falsa rispetto all'artefatto che accompagna.

Non chiedo di togliere i 40 mm dalla tavola: è un difetto preesistente, sta fuori dalle due
cause del pacchetto, e il ciclo di miglioramento protegge il **numero** delle andate e
ritorno, non la loro entità — cosa che va detta, perché spiega come 2,5 mm possano essere
comprati legittimamente. Chiedo che il §4.1 e il §2 dicano **40 mm contro 37,5**, che è
quello che gli artefatti mostrano.

---

## Osservazioni non bloccanti del terzo giro

**O3-1 — La citazione che motiva la correzione di R-1 è attribuita alla decisione sbagliata.**
La docstring di `free()` e il §4.5 scrivono «D-111 dice espressamente che *un tubo che passa
sopra l'etichetta non è un problema e non va evitato*». La regola c'è ed è vera, ma sta in
**D-110** («l'etichetta dell'indirizzo … **può essere attraversata da un tubo**, non deve
essere allineata alle altre, non si sposta per evitare sovrapposizioni»); D-111 la emenda su
altro. Inoltre la frase è fra virgolette ma è una parafrasi, non il testo. Su un progetto la
cui regola numero uno è «una fonte si guarda, non si descrive a memoria», vale la pena
sistemare il riferimento.

**O3-2 — La spiegazione dei tre residui di D-120 non regge sui dati agli atti.** Il §4.2
dice che i tre stanno «tutti su coppie di accessori consecutivi». Nel censimento di
`finale/metriche.json` **uno solo** è classificato `coppia` (prelievo ACS, 13,5 mm); gli
altri due — valvola del manometro e ingresso freddo del bollitore, 7,5 mm — sono
classificati `ultimo`. Il conteggio 17 su 20 è giusto e l'ho ricontato; è la frase che lo
spiega a non corrispondere.

**O3-3 — La propaggine è ridotta, non sparita, e la consegna ora lo dice.** Lo sfiato aria
sta ancora a `y = 71,0` con il simbolo successivo a `y = 83,5`: dodici millimetri e mezzo di
stelo nudo (erano 27,5 al primo giro, 17,5 al secondo). La copertura dell'ingombro, **0,766**,
è sopra la soglia di 0,75 ma sotto lo 0,81 che la docstring di `INK_COVERAGE_MIN` indica come
valore di una tavola «senza propaggini». Nessuna obiezione: uno sfiato **si monta in alto**,
il numero al netto del pezzo isolato è pubblicato, e il giudizio è del PM.

**O3-4 — Voci confermate.** Attraversamenti del corpo di un simbolo con la mia misura
indipendente: **0** su 74 tratti × 45 simboli; `LINE_UNDER_SYMBOL` con il predicato storico
di `ebe165a`: **0** su entrambe le colonne; tratti a filo del bordo: **2**, da 2,5 mm,
entrambi sporgenti oltre il riquadro e quindi fuori anche dalla convenzione storica. Grafo
canonico rigenerato da me su `e4be6cd`: `sha256 5d3334f5c87b84ef…`, identico. Valvole:
**17 su 20** dentro forbice contro **6 su 20** della baseline, ricontate da me sulla
geometria. `ruff check src tests` verde; `mypy src tests examples`: *no issues in 133 source
files*; `pytest tests/layout tests/validation`: **206 passed, 13 skipped, 2 xfailed**.
Perimetro: 31 file, tutti dentro l'elenco del Work Package; `cli.py` **non** toccato, ed è
la scelta giusta. Tavola guardata a piena pagina e a 6×: leggibile, e il confronto
prima/dopo rende visibile il miglioramento.

---

## Cosa manca

Una cosa sola, e non è lavoro di progettazione:

1. **Rimisurare il §4.1 sull'artefatto consegnato** e scrivere **40 mm contro i 37,5 mm della
   baseline**, correggendo di conseguenza la frase «con lo stesso numero» al §2 e la nota
   storica che dichiara chiuso quell'errore. Se serve, aggiungere la ragione tecnica — il
   ciclo protegge il numero delle andate e ritorno, non la loro entità — che è vera e va a
   favore di chi consegna.

Facoltativi, non bloccanti: il riferimento a D-110 invece di D-111 (**O3-1**) e la frase sui
tre residui (**O3-2**).

Un quarto giro può limitarsi a rileggere quelle righe: **tutto il resto è verificato**.

---

## Come ho misurato il terzo giro

- `validate_drawing_geometry` (il cancello vero) su `baseline/geometria.json` e
  `finale/geometria.json`; misura mia delle sovrapposizioni etichetta/simbolo e
  etichetta/etichetta; controllo che nessuna etichetta esca dall'area di disegno.
- `drawing_fingerprint` calcolata sui file agli atti e confrontata con `metriche.json` e
  `preflight.txt`; tavola **rigenerata** con `disegnatore_mep draw … --verifica --geometry` e
  confrontata con gli artefatti (geometria `==`, SVG identico, preflight identico).
- `ink_coverage` e `ink_imbalance` calcolate con le funzioni del progetto sulle **quattro**
  geometrie agli atti (baseline e le tre consegne), e su 4000 layout casuali per verificare
  che `coverage` non sia una funzione di `spread`; più un caso costruito con e senza
  propaggine.
- Riempimento al netto del pezzo più isolato ricalcolato con **il mio** metodo, indipendente
  da `_fill_without_the_loneliest`, sulle quattro geometrie.
- Misura mia dell'attraversamento del corpo aperto e dei tratti a filo del bordo; predicato
  storico di `ebe165a` riapplicato.
- Censimento delle valvole D-120 ricontato dalla geometria; numero dell'andata e ritorno
  letto da quattro fonti indipendenti.
- Modello canonico rigenerato e confrontato con `sha256sum`; `ruff`; `mypy src tests
  examples`; `pytest tests/layout tests/validation`.
- `finale/impianto1.png` e `prima-dopo.png` a piena pagina, più due ingrandimenti a 6× sul
  nodo di R-1 e sulla propaggine.
