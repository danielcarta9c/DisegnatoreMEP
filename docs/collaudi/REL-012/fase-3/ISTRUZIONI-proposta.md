# Elettrico e comando: tavola unica o tavole separate — proposta per le istruzioni di Comporre

**REL-012, fase 3, punto 3.** **Proposta della sessione del 29 ottobre 2026, da approvare dal PO
sulle tavole** di questa cartella. Non è ancora in `skill/comporre/ISTRUZIONI.md`: è il testo che
ci entrerebbe, sotto un titolo suo, se il PO lo approva.

La disposizione del PO (I-227), testuale: «sulle tavole di centrale o dove è già molto denso meglio
disegnare l'elettrico e comando su tavola separata. Su tavole piccole come quella di sola
distribuzione oppure come il caso dell'esempio (una sola macchina canlizzata con singolo FC) si puo'
fare su tavola unica ok».

---

## Il testo proposto per `skill/comporre/ISTRUZIONI.md`

### Elettrico e comando: una tavola o due

Se il grafo porta cavi o bus — reti del dominio `control`: l'alimentazione dal quadro, i comandi del
regolatore, il bus, le sonde — decidi **prima di comporre** se l'elettrico sta sulla tavola
dell'impianto o su una tavola sua. Il grafo è uno solo: le due tavole escono dallo stesso grafo, con
due piani.

**Due tavole** se vale almeno una di queste:

1. **è una centrale**: il grafo ha un generatore sull'acqua (pompa di calore aria-acqua, caldaia,
   boiler in pompa di calore) oppure un accumulo (volano, accumulo combinato, bollitore);
2. **è densa**: `python3 scripts/mep.py pezzi <grafo> --vista idraulica` elenca **più di 15 pezzi da
   posare**;
3. **la tavola unica non esce**: composta in una vista sola ha un rilievo bloccante o una tratta
   ceduta, e un giro di ricomposizione non li toglie.

**Tavola unica** altrimenti: la sola distribuzione (un collettore con circolatore e miscelatrice, il
suo regolatore e le sue sonde), l'aria-aria con un'unità esterna e un'unità interna.

**Il progettista decide sempre.** Se ha detto «tavola unica» o «tavola a parte per l'elettrico», fai
quello che ha detto, anche contro la regola qui sopra; se la regola ti porta dove lui non ha detto,
dillo nella consegna in una riga («l'elettrico è su una tavola a parte: è una centrale»).

### Come si scrivono

Il campo **`vista`** del piano dice quale parte del grafo la tavola disegna:

| `vista` | che cosa disegna |
|---|---|
| `"tutto"` (se il campo manca) | il grafo intero: la tavola unica |
| `"idraulica"` | tutto **tranne** i cavi e i bus, e tranne i pezzi che stanno solo sul comando (quadro, sezionatore, regolatore, sonda esterna). La sonda a immersione resta sul suo tubo, senza il cavo |
| `"elettrico"` | i **soli** cavi e bus, e i pezzi che toccano: quadro, sezionatore, regolatore, sonde, e le macchine, i circolatori e le valvole che hanno un cavo. Niente acqua |

Per due tavole scrivi **due piani** sullo stesso grafo completo, `piano-idraulica.json` con
`"vista": "idraulica"` e `piano-elettrico.json` con `"vista": "elettrico"`, e disegna due volte. Il
motore fa il resto:

- il titolo della tavola porta «— idraulica» e «— elettrico e comando», e il numero della tavola
  dell'elettrico è quello del grafo con «-E» (P.04 e P.04-E);
- la legenda di ciascuna rimanda all'altra («Vedi tavola P.04-E «elettrico e comando»»);
- **le sigle sono le stesse** sulle due tavole: sono quelle del grafo intero;
- i file escono con nomi diversi (`…-idraulica-t1.pdf`, `…-elettrico-t1.pdf`).

I pezzi da posare non sono gli stessi nelle due viste: chiedili per ciascuna, con
`mep.py pezzi <grafo> --vista idraulica` e `--vista elettrico`. Sulla tavola dell'elettrico **il
circolatore va nel piano**: non ha il suo tubo, e non sta più in linea. Il sezionatore resta in
linea sul suo cavo, e lo posa il motore.

### Come si compone la tavola dell'elettrico

È uno schema di collegamento, non la centrale ridisegnata: i pezzi non devono stare dove stanno
sull'idraulica. Quello che conta è che i cavi siano corti e non si incrocino.

- **Il regolatore al centro.** Le sue porte: alimentazione e bus su un fianco, i comandi sull'altro,
  le sonde sotto. Specchialo (`"specchio": true`) se i pezzi che comanda stanno dall'altra parte.
- **Le macchine dal lato dell'alimentazione e del bus del regolatore**, le **valvole e i
  circolatori dal lato dei comandi**: girali (`rotazione`) perché l'attacco del comando guardi il
  regolatore — il cavo è una retta.
- **Il quadro vicino alle macchine che alimenta**, con un'uscita sull'asse dell'alimentazione della
  macchina: il cavo è una verticale, e il sezionatore di prossimità ci sta in mezzo da solo.
- **Le sonde sotto il regolatore**, nell'ordine dei loro ingressi: la più lontana sull'ingresso più
  lontano, così i cavi non si incrociano.
- **Guarda l'ordine delle porte prima di posare.** La pompa di calore ha l'alimentazione a sinistra
  del bus, sotto; il regolatore ha l'alimentazione sopra il bus. Con il quadro sotto la macchina e il
  regolatore accanto, il bus passa sotto il quadro: altrimenti incrocia l'alimentazione.

Sulla **tavola unica** l'acqua si compone come sempre, e i cavi vengono dopo: il motore instrada
prima tutta l'acqua e poi i cavi, nello spazio che resta. Metti il regolatore e il quadro **fuori**
dal disegno dell'acqua, dalla parte dei pezzi che comandano.

---

## Su che cosa si regge il criterio — le misure

Le tavole di questa cartella, disegnate con il motore del ramo (`mep.py disegna`, la riga
«Formato …» che il comando stampa):

| tavola | vista | pezzi da posare (`pezzi --vista`) | tratte | bloccanti | cedute | sormonti | formato |
|---|---|---|---|---|---|---|---|
| `piccolo/` — zona a pavimento con miscelatrice | `tutto` | 12 (9 nella vista idraulica) | 16 | 0 | 0 | 0 | A3 |
| `centrale/` — impianto 2 con elettrico | `idraulica` | 27 | 29 | 0 | 0 | 1 | A3 |
| `centrale/` | `elettrico` | 8 | 8 | 0 | 0 | 0 | A3 |
| `centrale/` — **confronto**, la stessa centrale su una tavola | `tutto` | 30 | 37 | **5** | 0 | **23** | A2 |

E fuori da questa cartella, per tarare la soglia dei 15 pezzi (`mep.py pezzi … --vista idraulica`):
il caso AA-01 dell'aria-aria (una UE, una UI canalizzata, un comando a filo) 10; l'impianto 3 delle
prove (una pompa di calore diretta sul pavimento) 24; l'impianto 5 (tre pompe di calore in cascata)
49.

**La centrale su una tavola sola non esce**: cinque rilievi bloccanti e ventitré sormonti su un A2,
contro zero bloccanti e un sormonto sulle due A3 separate. La distribuzione su una tavola sola esce
pulita su un A3. La soglia dei 15 pezzi separa i due casi che il PO ha nominato come piccoli (AA-01
10, la sola distribuzione 9) da tutte le centrali delle prove (24 e più); la regola 1 li separa già
da sola, e la 2 serve per una distribuzione grande, che non ha generatori ma è densa.

## Da decidere col PO

1. **Il criterio**: le tre condizioni, e la soglia dei **15 pezzi** da posare nella vista idraulica.
2. **La sonda a immersione sulla tavola idraulica**: resta sul suo tubo, senza il cavo (proposta). Il
   pacchetto la elencava fra i pezzi solo-elettrici; toglierla lascerebbe una derivazione a T senza
   niente appeso.
3. **Il numero della tavola dell'elettrico** con «-E», e il rimando nella legenda («Vedi»).
4. **Il comando della valvola motorizzata** (`comando`) è un cavo di alimentazione (`power_supply`),
   perché le uscite del regolatore sono a 230 V: in legenda si legge «Alimentazione elettrica» come
   il cavo del quadro.
