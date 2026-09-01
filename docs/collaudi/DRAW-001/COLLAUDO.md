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
