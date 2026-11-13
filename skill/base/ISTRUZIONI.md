# Base — leggere la planimetria e trascriverne la base

> **A chi parla questo file.** A un agente — di solito un sub-agente lanciato apposta — che
> riceve una planimetria (il PDF dell'architetto, un catastale, un disegno a mano scansito, la
> foto di una planimetria stampata) e deve restituire **la base in dati**: muri, aperture,
> stanze e balconi, in metri, nel JSON della pianta. Il §2 parla invece a chi lo lancia.
> Queste istruzioni bastano da sole.

---

## 1. Il lavoro, in tre righe

Tu **leggi e trascrivi**; il disegno lo fa il comando. La tavola impiantistica ha una base
sola, qualunque fosse l'ingresso: muri grigio chiaro, finestre celesti, porte a tratto fine, il
nome di ogni locale con i suoi mq (li calcola il comando dal poligono), tutto in mezzatinta
sotto l'impianto. Per questo **non si trascrive niente che non sia architettura**: arredi,
sanitari, cucina, armadi, quote, retini, testi e cartigli restano sulla planimetria.

**La regola prima di tutte:** una misura che la planimetria non dà diventa una **domanda
dichiarata**, mai un numero inventato. Quello che stimi lo dici come stima.

## 2. Chi lo fa: un sub-agente

Guardare una planimetria vuol dire guardare molte immagini, e ingrandirle; chi poi disegna
l'impianto non deve averle nel contesto. **Chi ha l'impianto lancia un sub-agente** con il suo
stesso modello e gli passa questo testo, con i posti tra graffe riempiti, e nient'altro:

> Leggi una planimetria e trascrivine la base. Le istruzioni sono {SKILL}/riferimenti/base.md:
> leggile per intero, bastano da sole. La planimetria è {FILE} (pagina {PAGINA}). Il piano e
> l'unità da trascrivere: {QUALE, con le parole del progettista, o «l'unica del foglio»}. Le
> misure note: {quote o superfici date dal progettista, o «nessuna»}. Lavora nella cartella
> {CARTELLA} e lancia i comandi con python3 {SKILL}/scripts/mep.py. Restituisci quello che
> dice il §9 delle istruzioni.

Quello che torna è la base (`base.json`), le due immagini da guardare e le domande. Chi l'ha
lanciato **guarda la sovrapposizione** (§8) prima di usare la base, aggiunge al JSON pezzi e
tracciati, e porta le domande al progettista con le sue. Se l'ambiente non lancia sub-agenti,
il lavoro lo fai tu con queste istruzioni, e lo dici nella consegna.

## 3. I comandi

```
python3 scripts/mep.py base <planimetria.pdf|.jpg|.png> --out <cartella> [--pagina N] [--dpi 150] [--zona x0,y0,x1,y1]
python3 scripts/mep.py base <base.json> --out <cartella> [--zona x0,y0,x1,y1]
python3 scripts/mep.py pianta <base.json> --out <cartella>
```

- **con la planimetria**: la pagina come immagine (un PDF si rende a `--dpi`, di base 150) con
  una **griglia in pixel** e i numeri sui bordi; `--zona` ingrandisce un riquadro, **in pixel
  della pagina**. Serve a orientarsi e alla taratura (§5);
- **con la base**: la planimetria schiarita, la **griglia della pianta in metri** e sopra la base
  trascritta a colori forti — muri rossi, finestre blu, porte verdi, stanze viola, balconi
  arancio —; `--zona` ingrandisce un riquadro, **in metri**. In console i controlli della
  taratura (porte, spessori, superfici). Con il solo `sfondo` e niente muri è **lo strumento per
  leggere**: le coordinate si leggono in metri sulla griglia. Con `--zona` il riquadro va in un
  file suo (`…-sovrapposizione-zona-….png`): la sovrapposizione intera resta quella senza;
- **`pianta`**: la base standard, com'è sulla tavola consegnata. Sceglie da sé il formato, scrive
  anche SVG, PDF e DXF (al primo uso può installare `ezdxf`, se c'è la rete) e stampa in console i
  controlli dell'impianto, che su una base sola sono tutti a zero: non ti riguardano.

**Prima di tutto copia la planimetria nella cartella di lavoro con un nome neutro**
(`planimetria.pdf`, `planimetria.jpg`): il nome del file che ricevi porta spesso il nome o
l'indirizzo del committente, e i file che il comando scrive prendono il nome dell'origine. In
`sfondo.file` il percorso è relativo alla cartella di `base.json`.

Due avvertenze che le prove hanno insegnato:

- **le coordinate si leggono dai numeri della griglia**, mai dalla posizione nell'immagine come
  la vedi: chi guarda un'immagine grande la vede rimpicciolita, e i pixel non sono i suoi;
- una zona con un numero negativo si scrive col segno uguale: `--zona=-0.5,0,6,4`. Meglio
  ancora: scegli l'origine in modo che l'unità stia tutta in coordinate positive (§5).

## 4. Guardare la planimetria

### 4.1 Che cosa hai davanti

| planimetria | che cosa aspettarti |
|---|---|
| **il PDF dell'architetto** | la scala nel cartiglio (1:50, 1:100) e il formato di stampa; muri a due linee senza campitura, o poligoni chiusi attorno alla massa del muro; **armadi a muro** come rettangoli con una croce (sono arredi); quote; i nomi dei locali possono mancare |
| **il catastale** | «Scala 1:200» nell'intestazione; **la planimetria è spesso un'immagine dentro il PDF**, anche quando sembra vettoriale; a volte **più piani sullo stesso foglio**, ciascuno col suo titolo («PIANO TERRA», «PIANO PRIMO SOTTOSTRADA»); «altra U.I.U.» sono altre unità; muri neri spessi, finestre a linee sottili attraverso il muro, balconi fuori dal perimetro col loro nome, l'altezza «H» |
| **il disegno a mano quotato** | le quote dei locali in metri; **non è in scala**, e nemmeno in scala uguale nei due versi; porte come vuoti nel muro, senza arco |
| **la foto** | storta, e con la prospettiva: le pareti parallele convergono |

**Se il PDF porta un'immagine** (il catastale, la scansione), rendila **alla sua risoluzione**:
`--dpi 200` se l'immagine è nata a 200 punti per pollice (lo dice `pdfimages -list`, se c'è; se
no prova 200 e 300 e tieni quella in cui le linee sono nette, larghe un pixel). A 150, il valore di
base, le linee sottili di un catastale si impastano. La stessa risoluzione va poi in `sfondo.dpi`.
Su un 1:200 un pixel vale 2–3 cm: dove la griglia non basta, conta i pixel scuri lungo una riga
o una colonna dell'immagine resa (un piccolo script va bene, e lo dici).

**Se il PDF è vettoriale** (linee e curve, non un'immagine: lo vedi ingrandendo, i tratti restano
netti) e nell'ambiente hai di che leggerne i tratti (pdfplumber, PyMuPDF), puoi estrarre le linee
dei muri — di solito le più spesse, nere — e convertirle in metri **con la stessa taratura**. È un
aiuto, e su una planimetria con molti muri risparmia tempo e dà il centimetro; ma **non è il
lettore**: che cosa è un muro e che cosa un armadio lo decidi tu, e il controllo resta la
sovrapposizione (§8). Se lo fai, dillo nella consegna.

**Stato di fatto o di progetto.** Se la planimetria porta demolizioni e costruzioni (per
convenzione **giallo** quello che si demolisce, **rosso** quello che si costruisce) e la richiesta
non dice quale stato serve, **è una domanda**. Se nessuno può rispondere, trascrivi lo stato di
progetto — quello che ci sarà quando l'impianto si monta — e dichiaralo fra le stime.

### 4.2 Quale piano, quale unità

Quello che la richiesta dice. Se il foglio ne ha più d'uno e la richiesta non dice quale, **è una
domanda**: non si sceglie. Le altre unità, le scale **comuni** e gli spazi comuni non si
trascrivono, salvo i muri che l'unità ha in comune con loro (sono i suoi perimetrali). Una scala
esterna **dell'unità** va fra i balconi (§6); se non si capisce di chi è, la trascrivi come
balcone e lo chiedi.

### 4.3 Che cosa è che cosa

- **muri**: linee spesse o campite, o coppie di linee parallele a 8–50 cm;
- **finestre**: linee sottili nello spessore del muro; **la portafinestra si trascrive come
  finestra** (sulla tavola è celeste come le altre);
- **porte**: l'arco e l'anta; in uno schizzo un vuoto con i segni degli stipiti; la scorrevole
  una linea lungo il muro, senza arco. **Sul catastale** la porta è un vuoto nel muro con un
  trattino di traverso, senza arco; la finestra ha lo stesso trattino e in più le linee del
  telaio nello spessore del muro;
- **varchi**: un vuoto nel muro senza porta;
- **arredi**: letti, divani, tavoli, sedie, cucina, sanitari, vasca e doccia, armadi — **non si
  trascrivono**, e lo spazio che occupano è del locale;
- **quote**: linee coi trattini e un numero; **retini**: giardini, campiture, gradini;
- **scale**: gradini con la freccia — una scala interna chiusa nel suo vano è un locale
  («Scala»); una scala aperta dentro un locale (a giorno) non è un locale a sé: il locale resta
  intero, e lo dici;
- **pilastri, cavedi, canne**: un ingrossamento pieno del muro, o un blocco con una croce. Si
  trascrivono come un muro corto col loro spessore (`portante` il pilastro, `tramezza` il
  cavedio) e si dicono fra le stime: in console escono fra i «DA GUARDARE», ed è giusto;
- **balconi e terrazzi**: fuori dal muro esterno, col parapetto a linea sottile.

## 5. La taratura

La taratura dice dove la pianta cade sull'immagine: `px_per_m` (i pixel di un metro),
`origine_px` (il pixel del punto 0, 0), e se serve `rotazione` e `px_per_m_y`. Si trova, in
quest'ordine di preferenza:

1. **le quote scritte** (il disegno a mano, una tavola quotata): misura in pixel i due capi di una
   quota lunga — `px_per_m` = pixel / metri. **Prendine almeno due, una per verso**: se
   differiscono più del 2 %, il disegno non è in scala uguale nei due versi, e allora
   `px_per_m` è quello lungo x e `px_per_m_y` quello lungo y. **In uno schizzo le quote
   prevalgono sul disegno**: le coordinate si costruiscono sommando le quote e gli spessori, e il
   disegno serve solo per quello che le quote non dicono (dove sta una porta). Se le quote sono
   numeri scritti in mezzo ai locali, senza linee di quota, i capi sono **le facce interne del
   locale**. Con molte quote tara su tutte le facce che le quote collocano (la retta che meglio
   le mette d'accordo), non su due sole. **Quando una catena di quote non chiude** con quella
   accanto, prevale la catena esterna, la più lunga; le quote piccole si adattano, e la
   differenza va fra le domande;
2. **la barra della scala** (catastali, tavole): misura in pixel la barra dei 10 metri, o quella
   che c'è;
3. **la scala dichiarata con il formato**: su un PDF a misura reale un metro fa
   `dpi / 25,4 × 1000 / scala` pixel — il comando lo stampa per 1:50, 1:100 e 1:200. Vale solo
   se la pagina è a misura reale (il catastale dice il formato di stampa: A4): **verificala**
   almeno su una quota o su una porta. Verificata solo sulle porte è una taratura buona ma
   **non misurata**: lo dici fra le stime;
4. solo se non c'è niente di meglio, **le porte** (80 cm): e allora la taratura è una stima, e va
   fra le domande.

- **La rotazione**: se un muro lungo non è orizzontale nell'immagine, `rotazione` è il suo
  angolo in gradi, positivo in senso orario (la y va in basso).
- **La prospettiva** (la foto): se le pareti parallele convergono a vista, la sovrapposizione
  non combacerà dappertutto. Chiedi una scansione, o una foto fatta dall'alto e diritta; se vai
  avanti lo stesso, di' dove la base è incerta.
- **I pixel** si contano dall'angolo in alto a sinistra dell'immagine resa, da zero; mezzo pixel
  in più o in meno non conta.
- **L'origine**: scegli il punto 0, 0 in modo che l'unità stia tutta in coordinate positive —
  lo spigolo esterno in alto a sinistra, o poco fuori. Le coordinate sono in metri, **x verso
  destra e y verso il basso**, come in un'immagine.

Scrivi lo `sfondo` in `base.json` e lancia `base base.json`: sulla griglia in metri leggi le
coordinate direttamente. **Come ti accorgi che la taratura è sbagliata** — il comando stampa
questi controlli —: le porte interne misurano 70–90 cm (se misurano 1,6 m la scala è la metà);
i perimetrali 25–50 cm (60 in un edificio vecchio), le tramezze 8–15; le superfici sono
plausibili (una camera 9–16 m², un bagno 3–7); il totale torna con la superficie, se il
progettista o il catastale la danno.

## 6. Che cosa si trascrive

Il file, con lo schema della pianta (`schemas/pianta.schema.json`):

```json
{
  "versione": "1.0.0",
  "titolo": "Base: planimetria di progetto 1:50",
  "note": ["Da dove viene la base, come l'hai letta, come hai verificato la taratura."],
  "sfondo": {"file": "planimetria.pdf", "pagina": 1, "dpi": 150, "px_per_m": 118.11, "origine_px": [120, 190]},
  "muri": [
    {"id": "p-nord", "da": [0.15, 0.15], "a": [8.15, 0.15], "spessore": 0.30, "tipo": "perimetrale"},
    {"id": "t-camera", "da": [4.35, 0.15], "a": [4.35, 4.15], "spessore": 0.10, "tipo": "tramezza"}
  ],
  "aperture": [
    {"id": "f-camera", "muro": "p-nord", "centro": [2.30, 0.15], "larghezza": 1.20, "tipo": "finestra"},
    {"id": "p-camera", "muro": "t-camera", "centro": [4.35, 3.40], "larghezza": 0.80, "tipo": "porta",
     "apre_verso": "sinistra", "cerniera": "sotto"}
  ],
  "stanze": [
    {"id": "camera", "nome": "Camera", "poligono": [[0.30, 0.30], [4.30, 0.30], [4.30, 4.10], [0.30, 4.10]]}
  ],
  "balconi": [
    {"id": "balcone", "nome": "Balcone", "poligono": [[0.30, -1.50], [4.00, -1.50], [4.00, 0.00], [0.30, 0.00]]}
  ]
}
```

| campo | che cosa | come |
|---|---|---|
| `muri` | l'**asse** (`da`, `a`), lo `spessore`, il `tipo` | l'asse è la linea a metà fra le due facce, lo spessore la distanza fra le facce. **Un capo che arriva su un altro muro va sull'asse dell'altro**: il comando chiude da sé l'angolo e la T, senza sporgenze (entro 5 cm il raccordo c'è lo stesso); un capo libero (una spalletta) va dove il muro finisce. **Un muro per ogni tratto dritto**, anche con porte e finestre: le aperture stanno sul muro, il muro non si spezza. Dove lo spessore cambia, due muri. Un muro curvo o obliquo: tratti dritti. `tipo`: `perimetrale` (l'involucro, e i muri verso altre unità e spazi comuni), `portante` (un muro interno spesso che riconosci come strutturale; nel dubbio `tramezza`, e lo dici), `tramezza` |
| `aperture` | `muro`, `centro` (sull'asse), `larghezza` (la luce fra gli stipiti), `tipo`: `porta`, `finestra`, `varco`, `foro` | per le porte: `apre_verso` (il lato del muro in cui l'anta si apre), `cerniera` (lo stipite con la cerniera: `sinistra`/`destra` su un muro orizzontale, `sopra`/`sotto` su uno verticale), `anta`: `battente`, `doppia`, `scorrevole` (anche a scomparsa). `apre_verso` è `sopra` o `sotto` per un muro orizzontale, `sinistra` o `destra` per uno verticale. Se il verso non è disegnato (uno schizzo) lascia fuori `apre_verso` e `cerniera`: **la porta esce disegnata chiusa**, senza arco, e lo dici fra le stime. Due ante disuguali: `doppia` (esce con due ante uguali), e lo dici. Un vano solo con un'anta e un pannello fisso è **un'apertura sola**. Un varco in un vuoto fra un pilastro e un muro, o una porta fra due spallette senza un muro intero: stendi un muro attraverso il vuoto e mettici l'apertura. Un setto isolato dentro un locale (lo spigolo di una scala) è un muro coi due capi liberi |
| `stanze` | `id`, `nome`, `poligono`, `disimpegno` | il nome **come sulla planimetria**, in minuscolo con l'iniziale («CAMERA» → «Camera»; due camere: «Camera 1», «Camera 2»). Senza nomi sulla planimetria, il nome da quello che c'è (un letto: Camera; un WC: Bagno; i fornelli: Cucina), e lo dici fra le stime. Il poligono segue **le facce interne dei muri**: i mq sono quelli netti; nicchie e armadi a muro stanno dentro il poligono del locale da cui si aprono, gli sguinci delle finestre fuori. `disimpegno: true` per i corridoi. **`controsoffitto` e `zona` non li scrivi**: sono del progettista |
| `balconi` | `id`, `nome`, `poligono` | balconi, terrazzi, logge, **portici**, scale esterne: dal filo del muro al parapetto (o alla linea esterna del cordolo e dei pilastri). Un portico continuo è un poligono solo, anche se il nome è scritto due volte. Non sono stanze: sono fuori. Su un balcone stretto un nome lungo non trova posto: tienilo corto («Scala est.»), e guarda la riga «Locali col nome sulla tavola» che `pianta` stampa |
| `sagome_muri` | i contorni dei muri come poligoni | **di regola no**. Solo se il progettista vuole la forma esatta del disegno dell'architetto: allora il disegno usa solo le sagome, per tutti i muri, e i `muri` restano per l'instradamento |

**Non si trascrive:** arredi, sanitari, cucina, armadi (anche a muro: il loro spazio è del
locale), quote, retini, testi e cartigli — **e mai nomi, indirizzi o codici fiscali del
committente**, che sul catastale ci sono —, le altre unità, i giardini e le aree fuori
dall'unità, salvo che il progettista le chieda.

## 7. Come si legge, in pratica

1. `base planimetria.pdf`: la pagina intera. Che planimetria è, quale piano e quale unità, che
   scala dichiara.
2. Ingrandisci (`--zona`, in pixel) la barra della scala o due quote lunghe: è la taratura (§5).
3. Scrivi `base.json` col solo `sfondo` e guarda `base base.json --zona …` a riquadri di 5–7
   metri: a 1:50 si vede il centimetro, a 1:200 i cinque centimetri.
4. Trascrivi in quest'ordine: **il perimetro**, i muri interni, le aperture, le stanze, i balconi.
5. `base base.json`: guarda la sovrapposizione (§8), correggi, rilancia.
6. `pianta base.json`: la base standard. Ogni locale ha il suo nome e i suoi mq, dentro.

Una planimetria di progetto con molti locali, armadi e nicchie chiede tempo — un'ora non è
troppo —; un catastale o uno schizzo di cinque stanze molto meno. Non si accorcia saltando il
§8.

## 8. Il controllo a vista: obbligatorio

Prima di consegnare guardi **la sovrapposizione intera, e poi ingrandita locale per locale**.
Si consegna quando:

- **ogni muro rosso sta su un muro della planimetria**: entro 3 cm a 1:50, entro 10 cm su un
  catastale a 1:200; in uno schizzo le quote prevalgono, e uno scarto di qualche punto
  percentuale è lo schizzo, non un errore — ma ogni muro del disegno ha il suo rosso;
- **nessun muro della planimetria è rimasto senza rosso**, e nessun rosso sta dove la
  planimetria non ha un muro;
- **ogni porta e ogni finestra sta sul suo vano** (il verde e il blu sui vuoti), e le porte si
  aprono dalla parte giusta;
- **le stanze** (viola) seguono le facce interne, con i nomi della planimetria; i balconi
  (arancio) ci sono;
- i controlli in console non hanno un «DA GUARDARE» senza una spiegazione (un perimetrale
  sottile può esserci: allora lo dici);
- sulla base standard (`pianta`) ogni locale ha il suo nome: la console dice «Locali col nome
  sulla tavola: n su n», e quali restano senza.

Dove non combacia e la planimetria non basta a deciderlo, è una domanda.

## 9. Che cosa restituisci

1. **`base.json`**: solo la base — `sfondo`, `muri`, `aperture`, `stanze`, `balconi`, e in
   `note` **due o tre righe**: che planimetria era, come l'hai tarata, se la taratura è misurata
   o stimata. Le `note` **escono sulla tavola**, nella colonna delle note: il racconto del lavoro
   (catene di quote, scarti, script) va nella consegna, non lì. **Niente pezzi, niente
   tracciati**: li mette chi disegna l'impianto.
2. I percorsi della **sovrapposizione** (il PNG e il suo PDF) e della **base standard** (il PNG di
   `pianta`).
3. **Le domande** — quello che la planimetria non dice e che serve — e **le stime** — quello che
   hai stimato: spessori, versi delle porte, nomi dedotti, la taratura se non è da una misura —,
   in italiano piano, ciascuna comprensibile da sola.
4. Una tabella: locale, mq.

## 10. Gli errori che le prove hanno fatto

- leggere le coordinate dalla posizione nell'immagine rimpicciolita invece che dai numeri della
  griglia;
- tarare uno schizzo su una quota sola, e trovarsi i muri spostati di venti centimetri a metà
  pianta;
- prendere gli armadi a muro per muri;
- spezzare un muro a ogni porta;
- chiudere un angolo mettendo il capo sulla faccia dell'altro muro invece che sull'asse;
- prendere un catastale per vettoriale: spesso è un'immagine dentro il PDF;
- scegliere da sé il piano quando il foglio ne ha tre;
- ricopiare nel JSON il nome del committente dal cartiglio, o lasciarlo nel nome dei file;
- consegnare come sovrapposizione l'ultimo riquadro ingrandito invece di quella intera;
- scrivere nelle `note` il diario del lavoro, che poi esce sulla tavola.
