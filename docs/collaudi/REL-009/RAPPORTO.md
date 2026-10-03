# REL-009 — la 1.3: il rapporto

Una sezione per ogni gruppo di punti, la più recente in alto. Il caso è il primo impianto reale (I-191),
ricostruito anonimo in `caso-reale-1/`: il documento della sessione di disegno porta i dati del cliente e non è
nel repository.

## 3. R3 — le voci del costruito, con il simbolo (I-194, I-197, I-198)

**3 ottobre 2026** · decisioni **D-203** (proposta; il contatore approvato) e **D-204** (approvata) · la forma la
approva il PO

### La tavola, per prima

`simboli-nuovi/tavola/` — un impianto piccolo che mette insieme le voci nuove: pompa di calore con i **giunti
antivibranti** sui due attacchi e il **contatore di calore «CC»** sul ritorno del primario; **volano a sei
attacchi** con i due **predisposti**, tappati, «al solare termico», la mandata sopra; **collettore d'appartamento
con mandata e ritorno** verso un ventilconvettore e un pannello; una derivazione **verso e da un impianto
esistente**; e, sotto, l'acqua fredda dall'acquedotto al **dosatore di polifosfati** e al bollitore in pompa di
calore.

```
Formato A2 · tratte 31 · tratte cedute 0 · rilievi bloccanti 0 · pieghe 7 · sormonti 0
```

Le tavole di regressione non cambiano (`confronta.sh`: 54 e 54, IDENTICI).

### Dopo la prima tavola: il PO (I-197, I-198)

«il contabilizzatore va bene. il volano a 6 tubi hai invertito mandata e ritorno sull'attacco del solare termico.
la mandata è sempre sopra il suo ritorno non viceversa. giunto antivibrante e dosatore polifosfati perche' non li
hai fatti? se servono e il progettista puo chiederli vanno messi.»

- **La mandata del predisposto sopra il ritorno.** Il motore colora una rete partendo da chi la alimenta; la coppia
  predisposta, senza nessuno a monte, era colorata al contrario, e il piano aveva seguito i colori. Ora un attacco
  predisposto che immette sta per la macchina che verrà ed è la **sorgente della sua rete**: la mandata esce da
  lui ed entra nel volano dall'attacco alto, il ritorno esce dal basso (`flow.py`, funzione `provision`).
  La prova lo misura sulle tratte classificate, non sul disegno.
- **Il giunto antivibrante** (`flexible-joint`, GA). Il progettista lo mette sull'attacco della macchina. Due cose
  non andavano, e le ha mostrate la tavola:
  - le regole posavano il loro corredo **fra il giunto e la pompa di calore**: ora tagliano il tubo oltre il giunto
    (`apply.py`, `_connection_to_split`);
  - così però la fila dei pezzi della pompa si contava dal giunto, e il filtro e il defangatore della macchina
    finivano dall'altra parte del contatore: il ritorno faceva un giro. Ora la fila si conta **dalla macchina dietro
    il giunto** (`runs.py`, `head_anchor`/`tail_anchor`), e il ritorno è quello di prima più il giunto:
    pompa ← giunto ← filtro ← defangatore ← vaso, riempimento, manometro ← contatore ← volano.
- **Il dosatore di polifosfati** (`polyphosphate-doser`, DP) e la nota del PO: «va installato esclusivamente sulla
  linea di ingresso dell'acqua fredda sanitaria che alimenta il boiler di accumulo dell'ACS … Non deve
  assolutamente essere inserito nell'acqua tecnica». Gli attacchi sono di acqua fredda; la validazione segue
  l'acqua dall'uscita del dosatore e ferma il grafo se non arriva a chi scalda l'ACS (`DOSER_NOT_ON_THE_DHW_FEED`) o
  se arriva a un riempimento (`DOSER_FEEDS_THE_TECHNICAL_WATER`). Capire §5 lo dice prima.

⚠ **Un mio errore, preso dalla suite**: il controllo del dosatore chiedeva al catalogo la geometria dei pezzi, che la
validazione topologica non deve pretendere — 17 prove di topologia rosse. E seguiva l'acqua da `endpoint_a` a
`endpoint_b`, un verso che il grafo non garantisce. Ora legge solo le definizioni e parte dall'attacco d'uscita del
dosatore; la prova nuova scrive i tubi al contrario e carica il catalogo senza simboli.

### Che cosa la tavola ha insegnato

- **Una scritta del progettista si perdeva in silenzio.** Alla prima posa «dal solare termico» non aveva un
  lato libero — accanto c'era la verticale del confine —, e il motore l'ha omessa senza dirlo. Ora è un rilievo
  **bloccante**, `FREE_LABEL_OMITTED`: la scritta l'ha data il progettista. Per la coppia di attacchi predisposti
  basta una scritta, come dice il documento del caso.
- **Il collettore con ritorno era alto 10**, con mandata e ritorno a 5 mm: le due intercettazioni che le regole
  ci posano si toccavano. Ora è 20 × 15, a 10 mm come i terminali.
- **Lo scarico e lo sfiato del volano** pendono già dai loro attacchi di servizio: il loro nome cita l'attacco da
  cui la regola parte, non quello a cui sono appesi. Lo spostamento su un attacco di servizio, scritto e poi
  tolto, non serviva.

### Le prove

`tests/acceptance/test_simboli_rel009.py` disegna la tavola di prova col comando della skill: zero bloccanti,
i simboli nuovi, le tre scritte; la mandata del predisposto entra dall'alto; il giunto sta attaccato alla pompa e
oltre di lui c'è il filtro della pompa. `tests/validation/test_dosatore_di_polifosfati.py` prova i due rilievi del
dosatore e il verso dei tubi. `test_preflight.py` prova `FREE_LABEL_OMITTED`. I conteggi della libreria salgono da
55 a 61 simboli.

## 2. R2 — gli accessori del costruito, e lo spostare (I-193)

**3 ottobre 2026** · decisione **D-201** (proposta, punto «altrove»)

- **Dichiarati**: sfiati con valvola a sfera sul ritorno di ogni pompa e sui volani, ritegni sulle mandate,
  manometro sui montanti, riduttore sull'acqua fredda, valvole sulle uscite dei collettori. Nessuno si raddoppia;
  le valvole sulle uscite dei collettori bastano già alla regola sull'ingresso dei terminali (16 in meno).
- **Spostati**: vaso, riempimento e manometro del primario sul secondario in centrale (T5), con quello che ne
  pende.
- **L'esistente** per pezzo e per tratto (I-195, D-202): un dato per le regole e i diametri; `completa` chiede
  del corredo che le regole posano sull'esistente (T6).

## 1. R1 — togliere, e «a bordo» per singola macchina (I-192)

**3 ottobre 2026** · decisione **D-201** (proposta)

### Le tavole, per prime: non cambia niente

Il punto 1 cambia il grafo completo, non il disegno. Le uscite di regressione, su `main` (`1dc2d80`) e sul ramo:

```
$ docs/collaudi/REL-005/pulizia-del-solutore/confronta.sh <main> <ramo>
file: 54 prima, 54 dopo
IDENTICI
```

La tavola del caso non c'è ancora: si fa al punto 5, quando la skill sa disegnare l'esistente.

### Sul caso, con le scelte T1–T5 del progettista

```
                                  1.2.2        con il punto 1
pezzi del grafo completo          207          149
accessori delle regole            114           64
tolti dal progettista               —           42
punti aperti                        0            0
```

I 42 tolti, ciascuno con il motivo:
- **T1**: le 32 intercettazioni su ingresso e uscita di ventilconvettori e pannelli;
- **T3**: i due separatori d'aria;
- **T4**: i due defangatori;
- **T5**: vaso, riempimento e manometro sul ritorno dei due primari, 6 pezzi.

Con loro se ne vanno i pezzi che ne pendevano: le intercettazioni dei separatori, la valvola bloccata aperta dei
vasi, il rubinetto portamanometro. Rilanciare le regole sul grafo completo non propone niente.

**T2**, le valvole di sicurezza delle sei pompe: dichiarate a bordo, le regole le posano lo stesso. La sicurezza
di ogni generatore la vuole anche col bordo (D-182), e `completa` lo dice; se sul costruito non ci sono, si
tolgono con «togli», e il motivo.

### Come si scrive

- `accessori_tolti`, nel grafo di prima stesura: `{"pezzo": "air-separator-tj-pr-3-b", "motivo": "…"}`. Il nome è
  quello che `completa` scrive accanto a ogni accessorio: è derivato dai dati — voce, pezzo, attacco — e non cambia
  da un rilancio all'altro.
- `a_bordo`, sulla singola macchina: le funzioni che porta dentro, coi nomi del catalogo (`"a_bordo":
  ["filtration"]`). Le regole lo leggono come il bordo del catalogo.
- `completa` riporta:
  - i tolti per famiglia, con il motivo;
  - le voci che non tolgono niente;
  - i pezzi dichiarati a bordo che la regola posa lo stesso.

  Un nome di funzione sconosciuto nel bordo ferma la validazione.
- Capire §3 e `SKILL.md` passo 4 dicono quando si scrivono. «Spostare» è togliere da una parte e dichiarare
  dall'altra: la seconda metà è il punto 2.

### Le prove

`tests/rules/test_accessori_tolti.py` (9 prove, sul caso) e una prova sull'uscita di `completa`. Senza il filtro
del motore le due prove centrali cadono.

```
$ python3 -m pytest -q
1991 passed, 15 skipped, 10 xfailed in 249.55s
```

`ruff check src tests` e `mypy src` verdi. I grafi agli atti restano identici byte per byte: un campo vuoto non
si scrive.
