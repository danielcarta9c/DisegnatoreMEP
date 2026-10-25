# Vincoli — centrale-pdc-condominio-caso-reale-2

## Giro 1 — revisore esterno su `tavola/` (= `tavola-giro-0/`, piano `piano-0.json`)

Verdetto del revisore: «la tavola si può consegnare così», con tre vincoli che non fermano la
consegna. Numeri di partenza: pieghe 13 · sormonti 12 · cedute 0 · bloccanti 0.

### Il racconto del revisore contro il grafo

Sigle → identificativi (dalla tavola): GT-03/05/06/04 = pdc-r1/r2/r3/r4 · GT-01/02 =
pdc-a1/a2 · VOL-02 = volano-risc · VOL-01 = volano-acs · BOL-01 = bollitore · CIR-01 =
pompa-carico-acs · CIR-02 = pompa-mz2 · CIR-03 = pompa-mz1 · CIR-04 = pompa-ricircolo · CC =
contatore · VE-01/02/03 = vasi del secondario ACS, del secondario riscaldamento, sanitario.

- Riscaldamento: quattro pompe in cascata, corredo di mandata e di ritorno nell'ordine del
  grafo, gruppo di riempimento e contatore sul ritorno comune, volano, CIR-02 sulla colonna da
  5 collettori (pompa-mz2 → ts-mz2-*), CIR-03 con lo stacco in discesa sulla colonna da 3
  (pompa-mz1 → ts-mz1-*), ritorni riuniti in tj-mz, vaso e manometro sul ritorno prima del
  volano: **tutto giusto.**
- ACS: due pompe, volano con i due attacchi al solare, carico della serpentina, linea fredda
  nell'ordine del grafo (acquedotto → intercettazione → riduttore → T scarico → gruppo di
  sicurezza → T vaso → bollitore), miscelatrice con il suo confine freddo, ricircolo da destra:
  **tutto giusto.**
- Una sola lettura imprecisa: il revisore chiede se CIR-01 abbia l'intercettazione a valle. Il
  grafo ce l'ha (valve-isolation-bollitore-coil-in), ma il motore la posa addosso al bollitore,
  non accanto alla pompa: la tavola la fa leggere come la valvola della serpentina. Non è un
  circuito dato all'utenza sbagliata; il piano non sposta gli organi in linea. Nessun vincolo.

### I vincoli, tradotti nel piano

**V1 · addosso-a (A4, D-145)** — su ogni ritorno di pompa di calore, `tee-sfiato-X` /
`sfiato-X` e `giunto-ritorno-X` fra `pdc-X.water_return` e le colonne della cascata, per
X ∈ {r1, r2, r3, r4, a1, a2}. Nel piano: `tee-sfiato-X` e `sfiato-X` da x=107,5 a x=62,5.
Il giunto è un organo in linea e lo posa il motore **dal lato del raccordo di colonna**
(`ts-pr-*`, `ts-pa`): il piano lo porta fra pompa e colonne solo mettendo la colonna di
ritorno dalla parte delle pompe (vedi V2). **Rispettato.**

**V2 · addosso-a + almeno-3-corsie-da (B12, B3, B9)** — colonna di ritorno
(`ts-pr-1/2/3`, `ts-pa`) addosso alla colonna di mandata (`tj-pr-1/2/3`, `tj-pa`), a 10 mm.
Nel piano: ritorno a x=92,5, mandata a x=102,5 (prima: mandata 92,5, ritorno 137,5).
**Rispettato, con l'ordine delle colonne invertito.** Misurato con V1 e V2 tutt'e due:
- mandata vicina alle pompe (l'ordine di prima), colonne a 10 mm: pieghe 17, sormonti 12, tre
  `HIGHWAY_IS_NOT_STRAIGHT` e quattro `PARALLEL_RUNS_WITHOUT_A_FREE_LANE`; il giunto del
  ritorno scivola addosso all'incrocio con la colonna di mandata e la mandata di GT-04 gli gira
  intorno — V1 non sta;
- ritorno vicino alle pompe: pieghe 13, sormonti 14, V1 sta.
B3 sceglie l'ordine con meno sormonti, ma A4 sta sopra B3: tengo il ritorno vicino. I due
sormonti in più (la mandata di GT-05, GT-06, GT-04 e di GT-02 scavalca la colonna di ritorno,
e il ritorno comune scavalca la colonna di mandata) sono il prezzo di V1, e lo dico.

**V3 · addosso-a (A4, D-145, disposizione del PO sul gruppo di sicurezza)** —
`dhw-safety-group-bollitore-cold-in` addosso a `tee-expansion-connection-dhw-bollitore-cold-in`,
e quel T addosso a `bollitore.cold_in`. Nel piano: T del vaso da x=400 a x=405 (10 mm dal
bollitore, D-062), vaso con lui; T dello scarico da 355 a 375, così la tratta del gruppo resta
al minimo (con 20 mm il motore si ferma: «no straight stretch of 15mm for dhw-safety-group»;
con 25 mm passa); scarico a 375, y 447,5 (stacco al minimo); acquedotto da 315 a 340 (stacco
al minimo dei suoi due organi). **Rispettato**; e due avvisi A4 in meno (acquedotto, scarico).

### Quello che non è un vincolo

- Scarichi dei volani rossi con la freccia, freccia sullo scarico della linea fredda: colore e
  freccia li decide il motore dal grafo. Difetto del disegno, si scrive nella consegna.
- Barra di ritorno del collettore di zona interrotta dalle discese di mandata: convenzione del
  simbolo. Domanda, non vincolo.
- Domande sul contenuto (al progettista): intercettazione sul ritorno della serpentina lato
  bollitore; acqua fredda della miscelatrice dal suo confine, senza riduttore; contatore solo
  sul riscaldamento.

### Risultato del giro 1 → `tavola-giro-1/`, piano `piano-1.json` (= `piano.json`)

Formato A1 · tratte 137 · tratte cedute 0 · rilievi bloccanti 0 · pieghe 13 · sormonti 14 ·
avvisi e regole: HIGHWAY_IS_NOT_STRAIGHT x1, PIECE_OUTSIDE_ITS_BAND x7,
SERVICE_STUB_LONGER_THAN_ITS_MINIMUM x2, SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER x4

## Giro 2 — revisore esterno nuovo su `tavola-giro-1/`

Verdetto del revisore: «la tavola si può consegnare così»; tre vincoli, nessuno ferma la
consegna. La tavola ha 0 tratte cedute e 0 rilievi bloccanti.

### Il racconto del revisore contro il grafo

Tutto giusto: corredo di mandata e di ritorno di ogni pompa nell'ordine del grafo (sul ritorno,
dalla colonna: giunto, sfiato, intercettazione, filtro), le due colonne affiancate, riempimento
e contatore sul ritorno primario, CIR-02 sui 5 collettori e CIR-03 sui 3 sotto il ritorno
comune, ritorni riuniti con manometro e VE-02 accanto al volano; ACS, linea fredda,
miscelatrice, ricircolo come nel grafo. Quello che non sa dire — quale zona è quale — è vero:
collettori e terminali non hanno sigla nel grafo. È un dato, non una lettura sbagliata: va al
progettista come domanda. La sua domanda sull'intercettazione solo in mandata dei terminali ha
già risposta nel grafo (assunzione a-terminali, confermata: valvole sulle uscite del
collettore). Nessun vincolo dal confronto.

### I vincoli — scritti, **non applicati**

Il punto 5 di «Il revisore esterno» chiude qui: al più due giri, e ci si ferma quando il
revisore dice «si consegna» e la tavola non ha bloccanti né cedute. Tutt'e due le condizioni
valgono. Una tavola ricomposta adesso non l'avrebbe vista nessun revisore.

- **W1 · sulla-stessa-verticale + sopra (B11, B12, B10)** — `utenze-acs` e `ricircolo-utenze`
  affiancati, l'andata sopra: oggi l'andata ACS esce in alto dalla miscelatrice e il ricircolo
  entra da destra in `bollitore.recirculation_in`. Nel piano: `ricircolo-utenze` e
  `utenze-acs` sulla stessa verticale, a destra del bollitore, con la miscelatrice girata verso
  destra. Da provare; non provato.
- **W2 · addosso-a (A4)** — `dhw-safety-group-bollitore-cold-in` ancora più addosso a
  `bollitore`: dopo V3 fra i due restano il T del vaso (5 mm) e 10 mm di tubo; la tratta del
  gruppo non scende sotto i 25 mm (il motore si ferma a 20). Margine: portare il T a 5 mm dal
  bollitore, sotto la soglia di D-062. Poco da guadagnare.
- **W3 · addosso-a (A4)** — `tee-expansion-connection-volano-acs-secondary-in`,
  `expansion-connection-volano-acs-secondary-in`, `tee-pressure-gauge-volano-acs-secondary-in`,
  `pressure-gauge-volano-acs-secondary-in` addosso a `volano-acs.secondary_in` (oggi a x=290 e
  302,5, il volano finisce a 235). Lo contendono `solare-mandata` e `solare-ritorno` con la
  scritta «al solare termico», che stanno sotto il ritorno: A4 non cede alla scritta, la
  scritta va spostata con i suoi attacchi.

### Tavola tenuta: `tavola-giro-1/`

Contro `tavola-giro-0/`: V1, V2, V3 del primo revisore rispettati; avvisi A4 da 4 a 2; pieghe
13 = 13; sormonti da 12 a 14 (il prezzo di A4 su B3, vedi giro 1). Due revisori, due «si
consegna».
