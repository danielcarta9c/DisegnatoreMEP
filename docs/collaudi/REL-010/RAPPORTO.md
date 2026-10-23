# REL-010 — Il revisore esterno e la sua tavola d'esempio · rapporto

## 1. La tavola d'esempio (I-217, D-211)

**23 ottobre 2026** · input **I-216**, **I-217**, **I-218** · la tavola al PO: «la tavola C vabene»; D-211 approvata, PR #78

### Le tavole, per prime

- `tavola-esempio/`: la tavola della prova pulita C (`docs/collaudi/REL-009/prova-pulita-1.4/piano-C.json`, grafo
  anonimo del caso) ridisegnata con le due correzioni — il PDF, i rilievi e l'anteprima.
- `cascata-prima-e-dopo.png`: GT-06 e GT-04, prima e dopo. Il giunto antivibrante del ritorno di GT-04 stava sulla
  verticale del collettore; ora sta sul suo stacco orizzontale, in fila con quello di GT-06.
- `pannelli-prima-e-dopo.png`: un collettore di zona con il ventilconvettore e il pannello radiante. La serpentina
  del pannello usciva dal riquadro e correva sotto il suo lato; ora sta dentro.

### Che cosa ha visto l'occhio, e nessun numero

La sessione ha guardato la tavola C ingrandita, zona per zona, prima di proporla come esempio per il revisore (I-216):
il PO l'aveva chiamata «perfetta» (I-214), e un esempio deve esserlo. **I rilievi la danno pulita** — zero tratte
cedute, zero bloccanti, un'autostrada non dritta e quattro coppie che si aprono, come sul caso —, e i due difetti
stavano lì lo stesso:

1. **la serpentina del pannello radiante fuori dal riquadro** (`underfloor-panel`): l'ultima delle quattro anse
   cominciava a 0,92 della larghezza e ne prendeva altri 0,14. Su ogni pannello di ogni tavola dal 21 settembre;
2. **il giunto antivibrante del ritorno dell'ultima pompa di ogni cascata sulla verticale del collettore** (GT-04,
   GT-02): la tratta di quella pompa esce dall'ultimo raccordo del collettore in prolungamento del collettore, scende
   e solo dopo piega verso la macchina; il motore posava i pezzi sul primo rettilineo libero. A chi legge a freddo il
   giunto sembra del collettore comune, e la colonna dei sei giunti non è in fila.

Visti e **non toccati**, perché non sono difetti del disegno o non sono della sessione:

- il ritorno dalla serpentina del bollitore fa un gradino di circa 4 mm prima di partire verso il volano: le due porte
  non stanno alla stessa quota, e quella della serpentina non scorre (D-163);
- la valvola di sicurezza 10 mm sopra la mandata: è già fra le domande al PO (`REL-009`, punto 9);
- gli attacchi liberi senza tappo su volani e bollitore sono i pozzetti delle sonde del simbolo (`probe`): convenzione
  del PO. Un revisore a freddo li solleverà — va detto nelle sue istruzioni;
- l'acqua fredda della miscelatrice termostatica arriva da un confine suo: è una domanda di contenuto, vicina a quella
  già aperta sulla fredda del bollitore (`REL-009`, punto 9).

### Le correzioni

- **Il simbolo** (`examples/graphics/build_symbols.py`, `underfloor_body`): quattro anse larghe 0,14 del riquadro con
  lo stesso margine ai due lati; `underfloor-panel` passa a 1.2.0. Cambiano solo i due file del simbolo.
- **Il motore** (`src/disegnatore_mep/layout/inline.py`, `place_inline_accessories`): un accessorio non si posa sul
  prolungamento del tubo comune da cui la sua tratta si stacca. La regola per intero è in D-211.

La prima stesura della regola era più larga, e la regressione l'ha fermata due volte prima della consegna:

- valeva per **ogni** raccordo con un attacco di fronte. Sulla tavola del caso (`caso-reale-2`) la fila della pompa
  di zona CIR-03 arriva nell'**ingresso** del raccordo della sua colonna, in linea col ramo che prosegue: le toglieva
  l'ultimo rettilineo e la mandava in verticale — pieghe da 13 a 17, tre avvisi in più. Ora vale solo se di fronte
  c'è l'**attacco comune**: chi ci arriva *dentro* è lui il tubo comune;
- valeva anche per le file con una **pompa in parallelo**: la pompa della zona lontana (CIR-02), che prosegue dritta
  sull'autostrada, finiva in verticale e la sorella restava orizzontale (`PARALLEL_PUMPS_FACE_DIFFERENT_WAYS`). Ora
  quelle file le governa I-204, che è del PO e viene prima.

Ogni stesura sbagliata ha la sua prova, rossa sulla stesura sbagliata e verde sulla regola consegnata.

### Le misure

```
$ .venv/bin/python -m pytest -q tests/layout/test_l_accessorio_non_sta_sul_prolungamento.py \
      tests/graphics/test_il_pannello_sta_nel_suo_riquadro.py          # sul commit di partenza
FAILED test_il_giunto_non_sta_sul_prolungamento_del_collettore
FAILED test_e_sta_alla_stessa_distanza_dal_collettore_dei_fratelli
FAILED test_la_serpentina_non_esce_dal_riquadro
```

Sul ramo le sei prove sono verdi. La tavola C, con lo ZIP costruito dal ramo:

| | formato | tratte | cedute | bloccanti | pieghe | sormonti | avvisi e regole |
|---|---|---:|---:|---:|---:|---:|---|
| prima (agli atti) | A1 | 137 | 0 | 0 | 14 | 14 | `HIGHWAY_IS_NOT_STRAIGHT` ×1, `SUPPLY_AND_RETURN_DO_NOT_RUN_TOGETHER` ×4 |
| dopo | A1 | 137 | 0 | 0 | 14 | 14 | gli stessi |

I sei giunti dei ritorni delle due cascate stanno tutti a x = 277,5 mm.

**La regressione** — `docs/collaudi/REL-009/la-1.4-sulle-tavole-agli-atti/banco.py`, con le tre prove pulite in più,
sul `main` (worktree, `PYTHONPATH` sul suo `src/`) e sul ramo:

| tavole | numeri | il disegno |
|---|---|---|
| impianti 1, 2, 4, 6a, 6b, 7 | identici | identico byte per byte |
| impianti 3, 5; prova-po A–D; simboli-rel009 | identici | cambia solo il pannello radiante |
| caso-reale-2; prove pulite A, B, C | identici | il pannello, e i due giunti delle ultime pompe: sull'orizzontale, in fila con gli altri |

Nessun altro pezzo si sposta su nessuna delle 17 tavole.

**La suite** sul ramo: `2050 passed, 15 skipped, 10 xfailed` (sul commit di partenza `2044 passed`, con gli stessi 15 e
10: le sei prove in più sono queste). `ruff check src tests`: «All checks passed!». **mypy** si ferma su
`numpy/__init__.pyi` («Type statement is only supported in Python 3.12 and greater»): è l'ambiente, e succede uguale
sul `main`.

## 2. Il materiale per il metro del revisore (I-217)

Il PO chiede se l'agente si possa addestrare. **Il modello no**: una skill non cambia i pesi, e il modello è lo stesso
per tutti. Si addestra **il contesto**: quello che il revisore legge ogni volta — istruzioni, esempi, criteri — e lo si
tara contro il giudizio del PO (`REL-010`, punto 3). Più immagini non vuol dire meglio: ogni immagine costa contesto e
tempo, e una con convenzioni diverse dalle nostre insegna a segnalarle come difetti (D-165). Si tiene solo quello che,
misurato, avvicina il revisore al PO.

### Le immagini dal web

Un 3D BIM di Caleffi, uno schema solare senza fonte leggibile, uno schema Caleffi con i codici prodotto, uno schema
Vaillant. **Nessuna entra nella skill né nel repository**: sono di terzi, e il repository è pubblico con licenza MIT.
Come metro hanno anche convenzioni diverse — nero e tratteggio per il ritorno nello schema Caleffi, come in `sdp`
(I-097) —; il 3D non è uno schema funzionale.

### La specifica tecnica di installazione Nove C (Rev. 00, 16 ottobre 2026)

Non entra nel repository (è un documento Nove C per le ditte). Due cose servono al prodotto:

- **gli schemi tipologici A, B, C dell'Allegato A sono disegnati con questa skill** — stessi simboli, GT-01, VOL-01,
  CIR-01, gli stessi colori —: sono tavole piccole fatte bene e con la nostra convenzione, approvate dalla Direzione
  Tecnica in un documento ufficiale. Come esempi per il revisore sulle tavole piccole: decide il PO;
- **la §2.4 è l'elenco del corredo del primario** che il progettista vuole su una PdC monoblocco: giunti antivibranti,
  intercettazioni, filtro a Y e defangatore magnetico sul ritorno, sfoghi e scarichi, manometro e termometro, vaso,
  valvola di sicurezza, gruppo di riempimento con disconnettore. È un confronto con le regole di Completare: contenuto,
  quindi domande al PO.

### Il manuale Shenling ThermaX R290 6–15 kW (OneDrive del PO)

Letto da un agente in sessione; **ricontrollato dalla sessione** sulle pagine del PDF 40–43 e 51–53:

- **a bordo**: pompa, flussostato, valvola automatica di spurgo dell'aria, valvola di sicurezza che apre a 3 bar,
  porta di scarico (p. 43, «Componente del sistema idrico»);
- **non a bordo il vaso** (p. 52); volume dell'impianto, esclusa la macchina, **almeno 40 l**, da mantenere anche a
  valvole chiuse (p. 52);
- **in cascata**: valvola di non ritorno sull'uscita di ogni unità, ritorno inverso suggerito, tampone ≥ 25 l (6–9
  kW), ≥ 40 l (12–15 kW), ≥ 40 l × n in cascata (p. 40);
- la valvola a tre vie fra ACS e riscaldamento «a sfera», inversione entro 60 s (p. 53).

Sono prescrizioni che cambiano gli accessori rappresentati, cioè il caso in cui D-015 vuole il manuale. Le domande al PO
sono in `REL-010`, «Da decidere col PO».

### Il documento Vaillant (OneDrive del PO)

È la *Specifica tecnica pompe di calore 2020*; la parte aria-acqua riguarda aroTHERM monoblocco R410A, non R290. Letto
da un agente e **non ricontrollato**: volume minimo per taglia, disaccoppiatore MPS 40, vaso e sicurezza nei moduli
interni. Si apre quando un caso reale porta una Vaillant.
