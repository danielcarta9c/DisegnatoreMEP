# REL-011 — Le regole del corredo contro il manuale Shenling · il confronto

**29 ottobre 2026** · pacchetto `docs/plans/pacchetti/REL-011.md`, punti 1–3 (il 4 preparato, non applicato) · base
`6e04487`

> **Per il PO, una cosa prima di tutto.** La skill decide **se** un accessorio si disegna e **dove**, mai **quanto è
> grande** (D-002, «Non progetti»). Il vaso d'espansione che chiede I-218 («le regole che dicono vaso d'espansione se ci
> va quanto grande») sta in `rules/hydronic/expansion-on-closed-circuit.json`: la regola dice che ci va, uno per
> circuito, sul ritorno generale del primario. La taglia non c'è da nessuna parte, e non c'è per scelta: se il PO la
> vuole sulla tavola è un **dato del progettista** da chiedere e da scrivere in tabella, non un calcolo (proposta 5).

Le fonti, e i loro limiti:

- **il manuale Shenling ThermaX R290 6–15 kW** non è nel repository. I fatti usati qui sono **solo** quelli letti e
  ricontrollati in sessione, pagine 40–43 e 51–53, riportati in `docs/collaudi/REL-010/RAPPORTO.md` §2. Dove una regola
  tocca qualcosa che quelle pagine non dicono, la colonna dice «non nelle pagine lette»;
- **la *Specifica tecnica di installazione* Nove C, Rev. 00, §2.4** non è nel repository. Ne resta traccia in un punto
  solo, lo stesso §2 del rapporto di `REL-010`: l'**elenco** del corredo del primario di una PdC monoblocco — giunti
  antivibranti, intercettazioni, filtro a Y e defangatore magnetico sul ritorno, sfoghi e scarichi, manometro e
  termometro, vaso, valvola di sicurezza, gruppo di riempimento con disconnettore. Dove serve il **dove** o il
  **quando**, la colonna dice «non nel repository: da verificare col PO».

Le regole sono di **Completare**, il pezzo 2, deterministico (`docs/ARCHITETTURA-DEL-PIANO.md` §1): un file per regola in
`rules/hydronic/`, il motore in `src/disegnatore_mep/rules/`. Il progettista vede quello che aggiungono nell'elenco di
`completa`, e lo approva prima del disegno (D-004).

---

## 1. Dove stanno le regole — che cosa fanno, in parole d'impiantista

Le sedici regole di `rules/hydronic/`, a `6e04487`. «Necessaria» e «raccomandata» sono le categorie di D-005. Il
**regime** è la soglia dei 35 kW dichiarata dal progettista (D-106, D-108); dove non c'è scritto vale sotto e sopra.

### Quelle che il manuale tocca

| regola (file) | quando scatta | che cosa mette, e dove |
|---|---|---|
| `expansion-on-closed-circuit` — vaso di espansione, necessaria | su ogni circuito chiuso di acqua di riscaldamento che ha un generatore di calore | **un** vaso per circuito, sul **ritorno generale**, a monte della prima ripartizione verso le macchine; con la valvola **bloccabile aperta** (la mette `isolate-what-is-serviced`). Non lo mette se **tutti** i generatori del circuito lo dichiarano a bordo; il catalogo oggi non lo dichiara per nessuna pompa di calore, quindi si mette sempre |
| `safety-relief-where-heat-enters-the-water` — valvola di sicurezza, necessaria | su ogni generatore di un circuito chiuso, a qualunque potenza | **una per generatore**, sulla mandata, attaccata alla macchina, prima di ogni cosa che si chiude; **anche se la macchina ne ha una a bordo** (D-182, confermata da I-218) |
| `air-release-where-the-water-is-hottest` — separatore d'aria, raccomandata, **sopra i 35 kW** | sul circuito che ha un generatore che scalda | un separatore sulla **mandata generale**, dove le mandate sono già una |
| `air-vent-on-the-stored-volume` — valvola di sfogo aria, raccomandata, **fino a 35 kW** | su ogni serbatoio dell'acqua di riscaldamento (volano, accumulo) | lo sfogo sull'attacco di sfiato del serbatoio; nessuno sfogo per macchina, che il proprio lo porta a bordo |
| `filling-unit-on-return` — gruppo di riempimento, necessaria | su ogni circuito chiuso con un generatore | il gruppo sul ritorno generale, che pesca dall'acqua fredda già dichiarata; se l'acqua fredda non c'è, una domanda |
| `gauge-where-the-plant-is-charged` — manometro, necessaria | come il gruppo di riempimento | un manometro sul ritorno generale, dopo il punto di riempimento, con il suo rubinetto portamanometro |
| `debris-guard-before-what-it-would-ruin` — filtro a Y, raccomandata | su ogni generatore che teme i residui | un filtro sul **ritorno di ogni macchina**, dopo il suo rubinetto |
| `dirt-separation-before-what-it-would-ruin` — defangatore, raccomandata | sul circuito che ha un generatore che teme i residui | **un** defangatore sul ritorno generale, a monte della ripartizione |
| `flow-temperature-where-heat-enters-the-water` — termometro, necessaria, **sopra i 35 kW** | su ogni generatore | un termometro sulla mandata di ogni macchina; sotto i 35 kW si usa quello della macchina |
| `isolate-what-is-serviced` — intercettazione, raccomandata | su ogni attacco di ciò che si smonta in esercizio | una valvola per tubo che esce dal **gruppo** (la macchina con il suo filtro); bloccabile aperta per il vaso, il rubinetto della presa per uno strumento |
| `let-what-holds-its-own-volume-empty` — attacco di scarico, raccomandata | su ogni serbatoio | lo scarico sull'attacco che il serbatoio gli dedica; il bollitore si svuota dall'ingresso freddo |

### Le altre, in breve (il manuale della pompa di calore non le tocca)

| regola | quando scatta | che cosa mette |
|---|---|---|
| `expansion-on-the-stored-volume-feed` — vaso sanitario | bollitore che si riempie dalla fredda | il vaso sull'ingresso freddo, fra il non ritorno e il bollitore, se l'ACS è centralizzata (D-178, D-179); altrimenti una domanda |
| `safety-group-on-the-stored-volume` — gruppo di sicurezza sanitario | come sopra | il gruppo EN 1487 sull'ingresso freddo, attaccato al serbatoio |
| `dhw-check-on-cold-inlet` — ritegno sanitario | come sopra | il ritegno sull'ingresso freddo, se il gruppo non lo porta già dentro |
| `dhw-mixing-on-draw-off` — miscelatrice termostatica | uscita dell'acqua calda di un accumulo | la miscelatrice sull'uscita, con il suo ingresso di fredda (D-175) |
| `boundary-shutoff-at-the-edge-of-the-plant` — intercettazione generale | ogni confine dell'impianto | una valvola sul confine |

**Che cosa non c'è, oggi, fra le regole**: nessun **ritegno sulla mandata dei generatori in parallelo** — lo mette
solo il progettista quando lo scrive (il caso reale, I-193) o il grafo che già lo porta (l'ibrido, D-137); nessuna
regola sul **volume minimo** dell'impianto né sul **volano**: il volano lo disegna la skill solo se il progettista lo
nomina; nessuna regola sui **giunti antivibranti**, che il catalogo ha (`flexible-joint`) ma che entrano solo se il
progettista li scrive.

---

## 2. Il confronto, regola per regola

Esiti: **d'accordo** · **in disaccordo** · **manca** (la cosa c'è nel manuale o nella specifica, e la skill non la fa) ·
**da verificare** (la fonte in repository non basta per dirlo).

| regola | la skill | Shenling ThermaX R290 6–15 kW | specifica Nove C §2.4 | esito |
|---|---|---|---|---|
| vaso di espansione (`expansion-on-closed-circuit`) | sempre, uno per circuito, sul ritorno generale del primario; mai la taglia | **non a bordo** (p. 52): serve fuori | «vaso» nell'elenco; dove, non nel repository: da verificare col PO | **d'accordo** sul *se*. **Manca** il controllo che il vaso resti sul circuito delle macchine quando il progettista lo sposta (proposta 3). La taglia: proposta 5 |
| valvola di sicurezza (`safety-relief-…`) | una per generatore, fuori, anche se a bordo | **a bordo**, apre a 3 bar (p. 43) | «valvola di sicurezza» nell'elenco | **d'accordo**: il PO la vuole lo stesso fuori (D-182, I-218). La taratura, 3 bar, è un dato di tabella, non una regola |
| separatore d'aria / sfogo (`air-release-…`, `air-vent-…`) | sopra 35 kW separatore sulla mandata generale; sotto, sfogo sul serbatoio; niente per macchina | **valvola automatica di spurgo a bordo** (p. 43) | «sfoghi»; dove, non nel repository: da verificare col PO | **d'accordo**: la skill non aggiunge uno sfogo per macchina, e la macchina lo ha. Sul caso reale lo sfogo per pompa lo ha scritto il progettista (I-193) |
| scarico (`let-what-holds-its-own-volume-empty`) | sui serbatoi; non sulle macchine | **porta di scarico a bordo** (p. 43) | «scarichi»; dove, non nel repository: da verificare col PO | **d'accordo** sulla macchina; **da verificare** se la §2.4 vuole scarichi anche nei punti bassi del primario |
| intercettazione (`isolate-what-is-serviced`) | su ogni attacco del gruppo macchina-filtro | non nelle pagine lette | «intercettazioni» | **d'accordo** con la §2.4 |
| filtro a Y (`debris-guard-…`) | uno sul ritorno di ogni macchina | non nelle pagine lette | «filtro a Y … sul ritorno» | **d'accordo** con la §2.4 |
| defangatore (`dirt-separation-…`) | uno sul ritorno generale | non nelle pagine lette | «defangatore magnetico sul ritorno» | **d'accordo**; «magnetico» è una caratteristica del pezzo, un dato di tabella |
| manometro (`gauge-…`) | uno sul ritorno generale, accanto al riempimento | non nelle pagine lette | «manometro» | **d'accordo** |
| termometro (`flow-temperature-…`) | solo sopra i 35 kW, uno per macchina | non nelle pagine lette | «termometro», senza soglia nel repository | **da verificare**: se la §2.4 lo vuole anche sotto i 35 kW, è **in disaccordo** con D-106 (domanda 7) |
| gruppo di riempimento (`filling-unit-on-return`) | sul ritorno generale; il catalogo gli dà a bordo il **ritegno**, non un disconnettore | non nelle pagine lette | «gruppo di riempimento **con disconnettore**» | **da verificare**: un ritegno non è un disconnettore (domanda 8) |
| ritegno sulla mandata di ogni unità in cascata | **nessuna regola** | **sì**, sull'uscita di ogni unità (p. 40) | non nell'elenco del repository | **manca** → proposta 1 |
| volume minimo dell'impianto | **nessuna regola** | **≥ 40 l** esclusa la macchina, anche a valvole chiuse (p. 52) | non nel repository | **manca** → proposta 2 |
| tampone che cresce con le unità | **nessuna regola**; il volume del volano, se il progettista lo dà, va in tabella (`volume_l`) | **≥ 25 l** (6–9 kW), **≥ 40 l** (12–15 kW), **≥ 40 l × n** in cascata (p. 40) | non nel repository | **manca** → proposta 4 |
| giunti antivibranti | **nessuna regola**; solo se il progettista li scrive | non nelle pagine lette | «giunti antivibranti» | **manca** rispetto alla §2.4 → domanda 6 |
| ritorno inverso in cascata | non è una regola di Completare: è il tracciato | **suggerito** (p. 40) | non nel repository | fuori dalle regole: è di Comporre, il pezzo 3 |
| valvola a tre vie ACS/riscaldamento | la deviatrice del catalogo, senza tipo né tempi | **a sfera**, inversione entro 60 s (p. 53) | non nel repository | fuori dalle regole: è un dato del pezzo, per la tabella |
| sanitario: vaso, gruppo, ritegno, miscelatrice, confini | come in §1 | il manuale della pompa di calore non ne parla | non nell'elenco del primario | — |

**In sintesi**: sul *se* il corredo del primario della skill e il manuale Shenling sono d'accordo, voce per voce, tranne
tre cose che il manuale chiede e la skill non fa: il **ritegno in cascata**, il **volume minimo**, il **tampone per
unità**. La §2.4, per quel che ne è nel repository, aggiunge due **forse**: i **giunti** e il **termometro** sotto i
35 kW, e un dubbio sul **disconnettore**.

---

## 3. Che cosa manca, e come si traduce in una regola che disegna

La skill disegna pezzi: una regola risponde a «ci va?» e «dove?». Un **numero** — 40 litri, 40 litri per unità, la
taglia del vaso — non è un pezzo. Ci sono tre modi onesti di tradurlo, e nessuno è dimensionare:

1. **una domanda al progettista**, quando il dato manca: la skill non sa quanti litri ha l'impianto (le tubazioni
   esistenti, i terminali, le valvole di zona che chiudono) e non lo deve calcolare. Lo chiede, come chiede del bordo
   macchina (I-046) o dell'ACS centralizzata (D-179). È la forma che propongo;
2. **un pezzo che scatta da un dato dichiarato**: se il progettista dichiara «il volume non basta», si mette il volano.
   Ma **quale** volano e **dove** — due attacchi in serie sul ritorno, o quattro attacchi a separare primario e
   secondario — è un contenuto MEP che oggi nessuna fonte del repository fissa, e il catalogo ne ha tre (due, quattro,
   sei attacchi): la regola non saprebbe quale proporre. Lo lascio al PO;
3. **un controllo aritmetico su dati dichiarati**, come la soglia dei 35 kW (D-108): il volume del volano è già un dato
   del progettista (`volume_l`, sul caso reale 1000 l e 200 l), e «40 l × n» è un conto. Serve però il minimo del
   costruttore **per modello**, e il catalogo è generico: non sa che una «pompa di calore aria-acqua» è una ThermaX da
   12 kW. È una voce di catalogo nuova, fuori dal perimetro di questo pacchetto.

Le quattro cose che mancano, una per una:

- **il ritegno su ogni unità in cascata** — è un pezzo, e si traduce diretto: proposta 1;
- **il volume minimo (40 l)** — domanda al progettista dove il circuito della macchina non ha un serbatoio: proposta 2;
- **il tampone che cresce col numero delle unità** — controllo sul volume dichiarato del volano, quando il catalogo
  saprà il minimo per modello: proposta 4, non implementata;
- **il vaso** — il manuale dice «non a bordo», e la skill lo mette già sempre. Quello che manca è l'altra metà: che le
  macchine, che il vaso non lo hanno, **non restino separate** dal vaso dell'impianto da rubinetti che non sono loro.
  Sul caso rifatto succede (§5): proposta 3.

---

## 4. Le proposte

Il contenuto MEP è del PO: queste sono proposte. Le prime tre sono **implementate sul ramo, una per commit**, ciascuna
con la regola, la prova (rossa senza la modifica) e il banco di regressione; **nessuna è su `main`**, e **nessuna è
attiva**.

**Perché non attive.** Il motore che le legge entra nel prodotto, inerte finché nessuna regola lo usa; la regola, invece,
sta nella cartella della proposta (`proposta-N/regola/`), non in `rules/hydronic/`, e le prove la caricano accanto a
quelle del prodotto. La ragione è misurata: copiata in `rules/hydronic/`, ogni regola fa cadere prove che confrontano
con documenti e piani agli atti fuori dal perimetro di questo lavoro (`docs/prodotto/`, i piani di `DRAW-018` e di
`REL-003`) — 27 la 1, 34 la 2, 5 la 3; l'elenco è in `proposta-N/suite-con-la-regola-attiva.txt`. **Attivarla vuol dire
spostare il file in `rules/hydronic/` e rifare quelle prove e quei documenti**, ed è un lavoro da fare dopo il sì del PO,
non prima. Così ogni commit lascia la suite com'era (una sola rossa, quella ambientale) e si prende da solo.

La 3 usa la «domanda al progettista» che la 2 porta nel motore: si prende dopo la 2, o con lei.

Il banco è `docs/collaudi/REL-011/banco.py`: quello di `REL-009` più le tre prove pulite, i cinque impianti di
`examples/prova/` e l'impianto 6 di `REL-003` **completati dalle regole** (nel banco di `REL-009` entrano già completi, e
una regola nuova non li tocca). La base è `esiti-base-6e04487.json`; il confronto, tavola per tavola, è
`proposta-N/banco-confronto.txt`, fatto con `confronta.py`.

### Proposta 1 — il ritegno sulla mandata di ogni generatore in parallelo

- **Le tavole, prima e dopo**: `proposta-1/impianto-1-prima.png` e `-dopo.png` (due pompe e accumulo combinato),
  `impianto-5-…` (tre pompe in cascata), `impianto-6a-…` (pompa di alta potenza e caldaia modulare: la tavola che il PO ha
  dato «va benissimo», I-136). Dopo, su ogni mandata, dalla macchina: sicurezza, rubinetto, **ritegno**, collettore.
- **Che cosa cambia**: una regola nuova, `proposta-1/regola/non-return-where-generators-run-in-parallel.json`, necessaria:
  su ogni generatore la cui mandata confluisce con quella di un altro prima di una macchina o di un serbatoio, un
  ritegno sulla mandata, **dopo i rubinetti della macchina**, lato impianto — come il progettista lo ha disposto sul caso
  reale (I-193). Al motore serve una condizione nuova, `anchor_runs_in_parallel` (`src/disegnatore_mep/rules/schema.py`,
  `engine.py`): si legge dalle camminate delle mandate, come la mandata generale, e non nomina né macchine né
  collettori. Il ritegno che c'è già sul **tratto proprio** della macchina conta, anche lontano dall'attacco: la prima
  stesura ne metteva un secondo alla caldaia dell'ibrido, che il suo ce l'ha dopo la deviatrice (D-137). La prova:
  `tests/rules/test_ritegno_in_cascata.py`.
- **Il banco**: 20 tavole su 24 identiche. Le 4 che cambiano sono quelle con macchine in parallelo e senza ritegni
  scritti — impianto 1, impianto 5, impianto 6 nelle due composizioni —, e con i piani agli atti **non si instradano più**:
  il ritegno vuole 10 mm di rettilineo che il piano non lascia. Il piano va ricomposto (pezzo 3). Per le tavole «dopo» la
  sessione ha fatto posto a mano, 15 mm fra le macchine e il collettore (`proposta-1/fai_spazio.py`,
  `piano-*-dopo.json`): **stessi numeri di prima** su tutte e tre — tratte, cedute 0, bloccanti 0, pieghe, sormonti. Il
  caso reale e le prove pulite non cambiano: i ritegni li ha scritti il progettista, e la regola li riconosce.
- **Attivarla** costa: i piani dell'impianto 1 e 5 (`DRAW-018`) e del 6 (`REL-003`) ricomposti, i grafi completi agli
  atti rigenerati, i documenti di `docs/prodotto/` (`REGOLE_ACCESSORI.md`, la scheda della regola; `grafi-di-prova/`;
  `GRAFO_IMPIANTO.md`), e i conteggi delle prove che li contano.
- **La domanda al PO**: *«Su ogni macchina in cascata il ritegno sulla mandata, dopo i suoi rubinetti, lo mette la skill
  da sola, come necessario — anche quando il progettista non lo scrive?»*

### Proposta 2 — il volume minimo: una domanda al progettista

- **Le tavole**: **nessuna cambia**, per costruzione — la regola non posa pezzi. Il banco: 24 su 24 identiche. Cambia
  l'elenco di `completa`: `proposta-2/completa-impianto-3-senza-volano.diff`.
- **Che cosa cambia**: una regola nuova, `proposta-2/regola/minimum-volume-where-the-generator-has-no-storage.json`: dove
  il circuito di un generatore **non ha nessun serbatoio** (né volano né accumulo), `completa` non mette niente e
  **chiede**: il volume d'acqua dell'impianto, esclusa la macchina e con le valvole di zona chiuse, raggiunge il minimo
  che il costruttore chiede? (per la ThermaX 40 l, p. 52). Se il progettista lo dichiara sulla macchina
  (`"volume_minimo": "verificato"`), la domanda non si fa. Al motore serve la regola che **chiede e non posa**
  (`then.question`, `schema.py`), un punto aperto di specie nuova (`proposal.py`, `report.py`), e il registro che non
  cerca in catalogo un pezzo che la regola non propone (`registry.py`). La prova:
  `tests/rules/test_domanda_al_progettista.py`.
- **Un fatto che la misura ha detto**: **nessuno** degli impianti di prova e dei casi agli atti ha una pompa di calore
  senza serbatoio — anche l'impianto 3, «diretta a pavimento», ha un volano a due attacchi. La domanda si vede solo
  sull'impianto 3 col volano tolto, che la prova costruisce. Sulle 34 prove che cadono ad attivarla, 32 sono impianti
  **sintetici** delle prove del motore (una macchina in anello, senza serbatoio) che pretendono «nessun punto aperto»:
  la domanda lì è giusta, e quelle prove andrebbero a filtrarla.
- **La domanda al PO**: *«Dove la pompa di calore va diretta sull'impianto senza volano, la skill chiede al progettista
  se il volume minimo del costruttore è garantito — o deve mettere un volano da sola? E se sì, quale: a due attacchi in
  serie sul ritorno, o a quattro?»*
- **Fuori dal perimetro, se il PO la prende**: Capire deve imparare la chiave `volume_minimo` (`skill/capire/`), perché
  la risposta del progettista finisca nel grafo.

### Proposta 3 — il vaso sul circuito dei generatori

- **Le tavole**: **nessuna cambia** — 24 su 24 identiche. Cambia l'elenco di `completa` sul caso rifatto: due domande,
  una per primario (`proposta-3/completa-caso-rifatto.diff`).
- **Che cosa cambia**: una regola nuova, `proposta-3/regola/expansion-on-the-generators-own-circuit.json`, che si valuta
  dopo tutte le altre: se il circuito dei generatori è rimasto **senza vaso** — il progettista lo ha spostato su
  un'altra rete, oltre un volano, o lo ha tolto —, `completa` lo chiede. Non sposta il vaso e non ne aggiunge: dove il
  progettista lo vuole resta. Se la separazione è voluta, `"vaso_separabile": "accettato"` sul generatore toglie la
  domanda. Usa la domanda della proposta 2; nessuna riga di motore in più. La prova:
  `tests/rules/test_vaso_sul_circuito_dei_generatori.py`.
- **Dove scatta**: sul caso rifatto (e quindi sulle tre prove pulite, che hanno lo stesso grafo) per il primario del
  riscaldamento e per quello dell'ACS; su nessun altro degli undici casi provati.
- **Un rilievo, dalla prima stesura della regola.** La prima stesura era più severa: chiedeva quando fra **qualunque**
  generatore e il vaso c'è un rubinetto che non è della macchina (il dominio di protezione di I-046, letto sul vaso). Ha
  chiesto su **nove casi su undici**, anche sulle tavole che la skill compone da sola: sul ritorno generale la skill mette
  il vaso **lato impianto rispetto al defangatore**, e le due valvole del defangatore stanno fra le macchine e il vaso
  (si vede su `proposta-1/impianto-1-prima.png`: collettore, valvola, defangatore, valvola, poi VE-01). Chiuse per pulire
  il defangatore, le macchine restano senza vaso. Per la Raccolta R sopra i 35 kW a combustione sulla tubazione di
  espansione non ci vanno organi di intercettazione (R.3.B.5.1); per le pompe di calore la norma non obbliga. **I numeri
  dicono che il corredo è giusto; l'ordine sul ritorno forse no.** Non l'ho cambiato: è una domanda al PO (la 9, sotto).
- **La domanda al PO**: *«Se il vaso non sta sul circuito delle pompe — come sul caso rifatto, oltre il volano — la
  skill lo chiede al progettista (questa proposta), o lo deve rimettere lei sul ritorno del primario?»*

### Proposta 4 — il tampone che cresce con le unità (non implementata)

- **Che cosa cambierebbe**: un controllo aritmetico sul volume del volano che il progettista dichiara (`volume_l`) contro
  il minimo del costruttore moltiplicato per le unità in cascata. Serve il minimo **per modello** nel catalogo (oggi la
  voce è generica), e la riga della tabella apparecchiature non cambierebbe: cambierebbe l'elenco di `completa`, con un
  avviso se il volume dichiarato è sotto. Sul caso reale, **se** le sue pompe da 15 kW sono della serie del manuale
  (la tabella dice Shenling, 15 kW; il modello va confermato): 1000 l per quattro unità contro 160 l, 200 l per due
  contro 80 l — d'accordo.
- **Perché non è sul ramo**: tocca il catalogo, fuori perimetro, e una soglia per modello è una decisione del PO.
- **La domanda al PO**: *«Vuoi che il catalogo porti i minimi del costruttore per modello — 25 l, 40 l, 40 l per unità
  — e che la skill avvisi quando il volano dichiarato è sotto?»*

### Proposta 5 — la taglia del vaso, come dato del progettista (non implementata)

- **Che cosa cambierebbe**: la tabella apparecchiature, colonna **caratteristiche**, scriverebbe il volume e la
  precarica del vaso **se il progettista li dà**. Oggi non può: il vaso lo aggiunge una regola, e il progettista non ha
  dove scriverne i dati; li scrive solo se il vaso lo dichiara lui nel grafo (I-193). Sul caso rifatto VE-01, VE-02,
  VE-03 hanno «–».
- **Perché non è sul ramo**: non è una regola, è il modo in cui un dato del progettista raggiunge un
  pezzo proposto. E toccherebbe D-002.
- **La domanda al PO**: *«La taglia del vaso la vuoi sulla tavola? Se sì, la skill la chiede al progettista e la scrive
  in tabella, senza calcolarla — va bene così?»*

### Le altre domande (senza proposta, finché il PO non risponde)

Tre le porta la §2.4, una la misura della proposta 3.

6. *«I giunti antivibranti sulla mandata e sul ritorno di ogni pompa monoblocco, la skill li mette da sola?»* Oggi solo
   se il progettista li scrive. Una regola vorrebbe una proprietà di catalogo («vibra»), fuori perimetro.
7. *«Il termometro sulla mandata di ogni macchina anche sotto i 35 kW?»* Oggi no, per D-106 («si usa quello integrato
   della macchina»). Cambiarlo è cambiare D-106.
8. *«Il gruppo di riempimento "con disconnettore": è il gruppo di oggi con un dato in tabella, o un disconnettore come
   pezzo a sé prima del gruppo?»* Il catalogo dà al gruppo un ritegno a bordo, non un disconnettore.
9. *«Sul ritorno generale il vaso va fra le macchine e il defangatore, così che chiudere il defangatore non lasci le
   macchine senza vaso?»* Oggi sta dall'altra parte (proposta 3, il rilievo). È un ordine di posa, nella regola del vaso
   (`ordering`), e cambierebbe le tavole di tutte le centrali.

---

## 5. Il dubbio del PO sul vaso (I-220)

Sulla tavola del caso rifatto, alla prima taratura, il PO ha scritto: «Ho anche un dubbio sul vaso di espansione». La
tavola è `docs/collaudi/REL-009/caso-reale-2/tavola/centrale-pdc-condominio-caso-reale-2-t1.pdf` (anteprima
`anteprima.png` nella stessa cartella); i due ritagli sono in `dubbio-sul-vaso/`.

**Come è disegnato.** Due vasi d'impianto, uno per primario:

- **VE-02**, il primario del riscaldamento (quattro pompe, GT-03…GT-06, volano VOL-02 da 1000 l): il vaso pende dal
  **ritorno del secondario**, fra i collettori di zona e il volano, accanto al manometro;
- **VE-01**, il primario dell'ACS (due pompe, GT-01 e GT-02, volano VOL-01 da 200 l): sul ritorno del secondario, cioè
  sul ritorno del serpentino del bollitore verso il volano, accanto al manometro;
- il **gruppo di riempimento**, invece, è rimasto sul **ritorno del primario**, vicino alle pompe. Vaso e manometro da
  una parte del volano, riempimento dall'altra.

È la scelta **T5** del progettista, cioè della tavola del PO del 3 ottobre (`docs/collaudi/REL-009/RAPPORTO.md`, «Sul
caso, con le scelte T1–T5»): il grafo toglie il vaso e il manometro dal ritorno del primario e li sposta sul secondario
(`costruisci_grafo.py`, `accessori_tolti`, «altrove»). **Da sola la skill li avrebbe messi sul ritorno generale del
primario**, accanto al gruppo di riempimento, come sull'impianto di prova 1 (`proposta-1/impianto-1-prima.png`, VE-01).

**Le ipotesi**, dalla più probabile:

1. **Il vaso sta oltre i rubinetti del volano.** Fra ogni pompa e il suo vaso ci sono due valvole che non sono della
   pompa: quella sull'attacco del primario e quella sull'attacco del secondario del volano. Chiusa una delle due, le
   pompe — che il vaso **non lo hanno a bordo** (Shenling p. 52) — restano su un circuito chiuso senza espansione, con la
   sola valvola di sicurezza. La Raccolta R, per i generatori a combustione sopra i 35 kW, vuole ogni generatore
   «collegato direttamente al vaso» e nessun organo di intercettazione sulla tubazione di espansione, salvo una tre vie
   verso l'atmosfera (R.3.B.5.1, R.3.B.5.3, SRC-029; per le pompe di calore la norma non obbliga, ma il principio è
   quello). È la proposta 3.
2. **Vaso e manometro separati dal riempimento.** La regola del manometro lo vuole «accanto al punto in cui il circuito
   si riempie, così chi reintegra legge mentre carica»: sul caso il riempimento è sul primario e il manometro sul
   secondario, oltre il volano. Chi carica non legge.
3. **Quanto è grande, e quanti.** Uno per primario, senza taglia («–» in tabella), per quattro pompe e 1000 l di volano.
   Il PO ha chiesto delle regole che dicono «quanto grande» (I-218): la skill non lo dice per scelta (D-002), e la tabella
   non ha dove scriverlo (proposta 5). O il dubbio è se in cascata ci vada un vaso per macchina.

Una quarta, più piccola: la valvola sotto il vaso è **bloccabile aperta** nel grafo (`valve-isolation-locked-open`), ma
ha lo stesso segno della valvola comune, e in legenda c'è solo «Valvola di intercettazione». Chi legge la tavola non
sa che quella non si chiude.

**La domanda al PO**, con la tavola in mano: *«Sul caso rifatto i vasi VE-01 e VE-02 stanno sul ritorno del secondario,
oltre il volano, come sulla tua tavola del 3 ottobre; il gruppo di riempimento è rimasto sul primario. Il dubbio è
(1) che le pompe possano restare separate dal vaso chiudendo le valvole del volano, (2) che vaso e manometro siano
lontani dal riempimento, (3) la taglia o il numero dei vasi, o (4) il segno della valvola bloccata aperta? Il vaso lo
vuoi sul ritorno del primario, dove la skill lo metterebbe da sola?»*
