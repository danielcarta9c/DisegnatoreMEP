---
name: disegnatore-mep
description: Disegna in PDF e DXF lo schema funzionale di centrali termiche e impianti aria-aria, con elettrico e comando; su richiesta pianta dei tracciati e distinta materiali. Da usare quando chiede la tavola.
license: MIT, il testo completo in LICENSE.txt
compatibility: Richiede l'esecuzione del codice (claude.ai, Claude Cowork o Claude Code) con Python 3.11 o più recente. Al primo uso il comando installa pydantic 2 da PyPI se manca, e per questo serve la rete verso PyPI; ezdxf per il DXF e pypdfium2 per l'anteprima sono facoltative; il PDF della distinta vuole la skill nove-c-report installata accanto. Da usare con Opus o Sonnet.
---

# Disegnatore MEP

**Versione 2.1.0** — 13 novembre 2026.

Il progettista ha già deciso e dimensionato l'impianto, e te lo descrive a parole. Tu ne fai la
**tavola dello schema funzionale**: la leggi, chiedi quello che manca, la fai approvare, la componi e
la consegni in PDF e DXF, con i rilievi dei controlli accanto. L'impianto può essere una centrale
idronica, un impianto aria-aria (unità esterna, unità interna canalizzata, plenum di zona,
bocchette), e le loro **linee elettriche e di comando** (quadro, interruttori e sezionatori, regolatore, sonde,
termostati, bus).

**Solo se il progettista li chiede**, due elaborati in più dallo stesso impianto: la **pianta dei
posizionamenti e dei tracciati** sulla sua planimetria, e la **distinta materiali** per
l'installatore che fa il prezzo a corpo (un PDF a parte, impaginato come i report Nove C).

Il lavoro è fatto di cinque pezzi. Tre li fai tu, con istruzioni scritte apposta — **Capire**,
**Comporre**, **Rivedere** —; due li fa il comando della skill, che è deterministico e misura —
**Completare** ed **Eseguire**. Il comando è uno solo:

```bash
python3 scripts/mep.py <comando> ...     # dalla cartella di questa skill
```

## Quello che non fai mai

- **Non progetti.** Non scegli macchine, taglie, potenze, portate, temperature, tarature,
  diametri; non decidi quanti pezzi ci vanno; non cambi l'ordine delle utenze e delle macchine,
  che è del progettista. Un ritorno inverso o due dorsali si disegnano solo se li chiede lui.
  La **sezione** e la **lunghezza** di un tratto («Ø200 · L 6 m», «3G2,5 · L 20 m») le dà lui: le
  trascrivi, non le ricavi (`capire.md`). La distinta materiali e la maggiorazione delle
  lunghezze si fanno solo se la chiede, con le regole della skill, ognuna con la sua fonte.
- **Non inventi dati.** Quello che il testo non dice o lo chiedi, o lo dichiari come assunzione
  che il progettista vede. Un dato che manca non compare sulla tavola: al suo posto c'è «DA
  DEFINIRE», o niente.
- **Non cambi lo schema che hai ricevuto.** Dopo l'approvazione il grafo non si tocca: il
  disegno sposta i pezzi, non li collega. Se ti sembra che manchi qualcosa, è una domanda.
- **Non sostituisci un pezzo che il catalogo non ha**, nemmeno con una voce che fa lo stesso
  mestiere con gli stessi attacchi: un cogeneratore non è una caldaia. E non aggiungi voci al
  catalogo né simboli alla libreria. Il pezzo manca dal grafo, e lo dici (Capire, «tipo B»):
  `python3 scripts/mep.py catalogo --cerca <parola>` ti dice subito se c'è.
- **Non consegni una tavola con rilievi bloccanti o tratte cedute**, e non la presenti come
  finita: la mostri per quello che è, e dici che cosa la ferma.

## Prima di cominciare

1. `python3 scripts/mep.py ambiente` — dice se il comando è pronto: la versione di Python, le
   librerie, i dati della skill. Il comando vuole **Python 3.11** o più recente e **pydantic 2**;
   il DXF vuole **ezdxf**, l'anteprima **pypdfium2** o PyMuPDF. Se una libreria manca prova a
   installarla da sé, e per questo serve la rete; se non ci riesce lo dice, e tu lo dici al
   progettista con le sue parole: senza pydantic non si disegna, senza le altre la tavola esce
   senza DXF o non la puoi guardare.
   Se dice che l'anteprima non c'è, la tavola non la potrai guardare prima di consegnarla:
   diglielo già nel primo messaggio.
2. **Una cartella di lavoro fuori dalla skill**, per l'impianto: `mkdir -p /tmp/mep/<progetto>`.
   La cartella della skill può essere di sola lettura, e i file dell'impianto non ci vanno.
   Qui sotto la chiamo `$L`; i percorsi dei file che passi al comando scrivili per esteso.
3. **Il modello.** Il piano del passo 5 lo compongono Opus e Sonnet; con Haiku, nelle prove, non
   si è mai instradato. Se sei Haiku, dillo al progettista nel primo messaggio: può cambiare
   modello prima di cominciare.

## Se il testo non descrive un impianto deciso

Se il progettista ti chiede di dimensionare o di scegliere le macchine, o nomina due pezzi e
chiede la centrale, digli subito che la skill disegna l'impianto che lui ha deciso e non lo
progetta, e chiedigli le macchine, i circuiti e come si collegano. Non chiudere un grafo fatto
quasi tutto di tue assunzioni: lì la risposta è una domanda, non un grafo.

## Il flusso

Copia questa lista nella risposta e spuntala man mano:

```
Avanzamento:
- [ ] 1. Leggo l'impianto e ne scrivo il grafo
- [ ] 2. Ti faccio le domande, in un messaggio solo
- [ ] 3. Aggiungo il corredo d'obbligo
- [ ] 4. Approvi il grafo completo
- [ ] 5. Compongo la tavola
- [ ] 6. La disegno e la misuro
- [ ] 7. La guardo e la correggo
- [ ] 8. Te la consegno, con quello che resta aperto
```

### 1. Capire — dal testo al grafo di prima stesura

Leggi **per intero** [riferimenti/capire.md](riferimenti/capire.md): è tutto il lavoro, con il
formato del file e il controllo finale. Il testo è la descrizione del progettista, com'è nella
conversazione.

- Le voci del catalogo, una riga ciascuna — id, nome, mestieri, attacchi:
  `python3 scripts/mep.py catalogo` (oppure `--mestiere heat_generation`, e così via); una voce
  intera con `python3 scripts/mep.py catalogo <id>`. I nomi dei mestieri e dei fluidi stanno in
  `dati/naming/`.
- Scrivi `$L/grafo.json`, e validalo finché regge:
  `python3 scripts/mep.py valida $L/grafo.json`. L'uscita elenca anche le assunzioni che hai
  dichiarato: sono le domande del passo 2.
- `capire.md` è scritto per un agente che lavora da solo: dove dice «chi ti ha lanciato» o «chi
  lancia il lavoro», quello sei tu, e le domande al progettista le porti tu. La tabella di
  rilettura (§8) è una verifica tua: non si manda.

### 2. Le domande — in un passaggio solo

Il grafo porta in `assumptions` quello che il testo non dice. Prima di scrivere al progettista
lancia anche `completa` (passo 3): i punti aperti che trova sono domande dello stesso messaggio.

**Fermati e chiedi**, in **un messaggio solo**, se c'è anche una sola di queste:

- una domanda che cambia il disegno — due letture corrette e diverse, il «tipo C» di Capire;
- un pezzo principale che il catalogo non ha: chiedi se procedere senza, o fermarsi;
- le potenze dei generatori, se il testo non le dà: senza, il regime della centrale non si
  ricava, e le regole mettono il corredo di una centrale fino a 35 kW — diglielo;
- **il livello del progetto**, se il testo non lo dice: **definitivo** o **esecutivo-costruttivo**
  (`metadata.livello`). La tua prima interpretazione è definitivo: tarature, precarica e note di
  posa escono solo nell'esecutivo (D-224);
- **marca, modello e potenza delle pompe di calore**: con le Shenling `completa` controlla il
  manuale — attacchi, portata, volano — e lo dice negli «avvisi del manuale»;
- **l'antigelo**: sopra i 35 kW glicole o valvole (`"antigelo"` nel grafo). Nelle case di base
  niente valvole: la pompa di calore si protegge da sé finché ha corrente, e la tavola lo dice in
  nota. Chiedi se la casa resta vuota d'inverno (seconda casa), se la zona è fredda o il tratto
  esterno lungo: se sì, `"antigelo": "valvole"`;
- **i dati del vaso**, se vuole il vaso dimensionato: il contenuto d'acqua di tutto il circuito che
  il vaso vede (se non lo sa, lo stimi dai terminali e dici che è una stima), la temperatura
  massima di mandata, il dislivello fra il vaso e il punto più alto dell'impianto;
- **i diametri delle tubazioni, se il testo non dice se li vuole**: chiedigli se vuole anche il
  dimensionamento. La tua prima interpretazione è no, e la tavola esce senza; per il sì gli dici
  su quali reti li calcoli e quali dati ti servono — i salti termici, le portate di progetto
  che il testo non dà —, così che risponda una volta sola (`capire.md` §4.7);
- **sezioni e lunghezze dei tratti**, su un impianto aria-aria o sulle linee elettriche, se vuole
  la tavola quotabile e il testo non le dà: le chiedi; un tratto senza dato resta senza scritta;
- **la distinta materiali e la pianta dei tracciati**, se il testo non dice se le vuole: la tua
  prima interpretazione è no. Per la pianta serve la planimetria (PDF o immagine, con la scala);
- **i dati della distinta**, se la vuole o se glielo chiedi adesso. Dopo `completa` lancia
  `python3 scripts/mep.py distinta $L/grafo-completo.json --domande`: non scrive niente, e dice in
  parole i dati senza i quali le voci escono «DA DEFINIRE» — marca e modello, refrigerante e
  precarica, bocchette, attacco della condensa, protezioni, portate… —, a quali pezzi mancano e in
  che campo del grafo va la risposta. Le porti **in questo stesso messaggio** (se non sai ancora se
  la vuole, sotto «se vuoi la distinta, mi servono anche:»), non dopo il primo lancio. **Per
  l'acqua** chiedi sempre i metri di tubo per rete e diametro, l'isolamento (preisolato, o nudo con
  guaina e spessore), i gomiti a corpo (di regola 20) e la posa della pompa di calore (a terra, o
  staffe se le vuole): lo schema è uno spazio di disegno, e non li dà (`riferimenti/distinta.md`).

Il messaggio porta:

- che cosa hai capito, in poche righe: le macchine, i circuiti, come si collegano;
- le domande che cambiano il disegno, **ciascuna con la tua prima interpretazione**, così che
  il progettista possa rispondere «va bene» o correggere;
- le assunzioni che hai fatto per chiudere il grafo, da confermare tutte insieme;
- i dati che la tavola scrive e che il testo non dà, in una riga ciascuno: committente e
  commessa, indirizzo, titolo e numero della tavola; marca e modello delle apparecchiature;
  i salti termici e le portate, se ha chiesto i diametri;
- **come si rivede la tavola**, se l'ambiente lancia sub-agenti, come Claude Code o Cowork; su
  claude.ai la scelta non c'è, e non la fai. Con la prima come proposta, in queste parole — con
  lo strumento delle domande a scelta, se l'ambiente ne ha uno:

  > Come vuoi che sia rivista la tavola, prima della consegna?
  > 1. **In questa conversazione**: la guarda Claude, lo stesso agente che l'ha composta. Più
  >    veloce, meno token.
  > 2. **Da un revisore esterno**: un altro agente Claude, che non conosce l'impianto, la
  >    guarda a occhio fresco. Più lento e più token: circa 10 minuti e 200 mila token a giro,
  >    al più due giri.

  Questa domanda da sola non ti ferma: se al passo 2 non c'è altro da chiedere, la porti al
  passo 4 con il grafo.

Poi **aspetta la risposta**. Riporta le risposte nel grafo — un dato dato si trascrive (quelli
della distinta nel campo che `--domande` dice), una lettura corretta si ridisegna, un'assunzione
confermata passa a `"status": "approved"` — e rivalida.

Se non ce n'è nessuna, non fermarti qui: le assunzioni e i dati che mancano li porti al
passo 4, insieme al grafo completo.

### 3. Completare — il corredo

```bash
python3 scripts/mep.py completa $L/grafo.json --out $L/grafo-completo.json
```

Le regole aggiungono gli accessori che un esecutivo porta, ciascuno con il perché e la fonte, e
dicono quelli che servirebbero e non si possono proporre: i **punti aperti**, che sono domande
al progettista. Il comando scrive il grafo completo. Se esce con un errore, il grafo di prima
stesura non regge: si corregge al passo 1.

**Il vaso d'espansione** lo dimensiona il comando, non tu (D-220), sul grafo completo:

```bash
python3 scripts/mep.py vaso $L/grafo-completo.json --contenuto <l> --tmax <°C> --dislivello <m> [--stimato]
```

Scrive la taglia sulla riga del vaso in tabella e, nell'esecutivo, la precarica, la taratura
accanto alle valvole di sicurezza e la pressione di carica accanto al gruppo di riempimento. Con
le Shenling usa la loro pressione minima (1,5 bar) e di riempimento (2,0 bar). Con il glicole
passa `--coefficiente` della miscela, dalla sua scheda. **Il vaso sanitario** del bollitore:
`vaso --sanitario --tmax <°C di accumulo> --rete <bar> --taratura <bar della valvola>
[--bollitore <l>]` (i dati e il metodo in `capire.md` §3; senza `--bollitore`, il `volume_l` del bollitore).

### 4. L'approvazione — l'unico cancello

Niente si compone prima che il progettista abbia approvato il grafo completo. In un messaggio
solo gli porti:

- che cosa le regole hanno aggiunto, per famiglia — «12 valvole di intercettazione, 2 valvole
  di sicurezza, una per generatore…» —, e il perché solo se lo chiede;
- i punti aperti, come domande;
- quello che il progettista ha tolto, spostato o dichiarato a bordo, se c'è, e le voci che
  `completa` segnala come senza effetto;
- il corredo che le regole posano **sulle parti esistenti**, come domanda: c'è davvero? Quello
  che non c'è si toglie;
- le assunzioni ancora da confermare e i dati che mancano.

Il grafo completo non si manda come file: il progettista lo approva su questo messaggio, e lo
vede disegnato al passo 6.

Chiedi l'approvazione esplicita, e **aspettala**. Se corregge la lettura, torni al passo 1 e poi
al 3 e al 4. **Se toglie un accessorio** — «questo non c'è», «la pompa lo porta dentro» — lo
scrivi nel grafo di prima stesura: in `accessori_tolti`, con il nome che `completa` gli dà e il
motivo del progettista, o in `a_bordo` sulla macchina (`capire.md` §3). **Se lo vuole altrove**,
la stessa voce dice dove (`altrove`). **Se ne aggiunge uno** che le regole non mettono, in un
posto preciso, lo scrivi nel grafo dove lui dice (`capire.md` §5). **Il vaso sanitario no**:
alla domanda «il bollitore lo porta a bordo?» il «no» è `"non_a_bordo": ["expansion"]` sul
bollitore, e il vaso lo posa la regola fra il non ritorno e il bollitore (D-178, I-272).
**Le note di posa sue** vanno in `metadata.note_di_posa`: vengono prima di quelle generate, e
una che comincia con il soggetto di una generata (Isolamento, Antigelo, Sfiati, Vaso, Sonda) la
sostituisce; `metadata.note_tolte` ne toglie una (`capire.md` §3, I-271). Poi rilanci `completa` e gli
riporti che cosa è cambiato. Le scelte restano nel grafo e valgono a ogni rilancio. Lo stesso
vale prima del passo 4, se le dice già nel testo o nelle risposte del passo 2.

### 5. Comporre — il piano

Leggi **per intero** [riferimenti/comporre.md](riferimenti/comporre.md). Scrivi `$L/piano.json`:
dice dove sta ogni pezzo sul foglio, e niente altro. `python3 scripts/mep.py pezzi
$L/grafo-completo.json` elenca i pezzi che il piano posa — ingombro, rotazioni ammesse, porte — e
quelli in linea, che posa il motore, e in che ordine stanno lungo ciascuna tratta: i raccordi si
posano in quell'ordine. Il manifesto intero di un simbolo lo stampa
`python3 scripts/mep.py simbolo <id>`.

### 6. Eseguire — la tavola e i rilievi

```bash
python3 scripts/mep.py disegna $L/grafo-completo.json --piano $L/piano.json --out $L/tavola
```

Sulla tavola vanno **la tabella delle apparecchiature e la legenda, nient'altro** (I-233): tratte,
note e computo stanno nel PDF della distinta, così il disegno sta nel foglio più piccolo — di
solito un A3. Il piano non riserva zone per altre tabelle e il comando non riceve `--tabelle`.

Il comando dice per prima cosa l'area del disegno del formato e quanto ne occupa la posa; poi
esegue il piano, disegna, misura e scrive in `$L/tavola/` l'SVG, **il PDF**, il DXF e
**i rilievi della tavola** (`*-rilievi.md`): il preflight di qualità, le regole del piano, il
cartiglio. In fondo stampa formato, tratte, tratte cedute, rilievi bloccanti, pieghe e sormonti:
sono i numeri con cui confronti due pose (per esempio i due ordini dei collettori, B3).

- **Il piano non si instrada**: il messaggio dice quale tratta non trova strada, e sotto quali
  pezzi unisce e dove stanno; poi la posa applicata, pezzo per pezzo. Se la posa non sta
  nell'area del formato lo dice come probabile causa: allora la tratta è innocente, e si stringe
  la posa o si prende il formato successivo. Si corregge il piano
  ([riferimenti/comporre.md](riferimenti/comporre.md) §6).
- **Rilievi bloccanti o tratte cedute**: si corregge il piano, e si rilancia.

#### Elettrico e comando: una tavola o due

Le linee elettriche e di comando escono dallo stesso grafo. **Sulle centrali e dove la tavola è
già densa vanno su una tavola a parte**; sulle tavole piccole — la sola distribuzione, una
macchina sola con i suoi terminali — stanno sulla tavola unica: è la disposizione del PO. Il
piano lo dice con la vista; il criterio misurabile, che ne è l'applicazione, è in
[riferimenti/comporre.md](riferimenti/comporre.md), e il progettista può sempre forzare.

#### Le tabelle sul foglio

Solo la tabella delle apparecchiature e la legenda, che il comando posa da sé. La tabella delle
tratte, il computo e le note della distinta sono nel suo PDF, non sulla tavola (I-233).

### 7. Rivedere — si guarda la tavola, e si torna al piano

La tavola la guardi tu. **Un revisore esterno** — un altro agente, che non l'ha composta e non
sa niente dell'impianto — la guarda **se il progettista l'ha scelto** alla domanda del passo 2 o
del passo 4, o se lo chiede dopo; non lo attivi da te. Come si fa è sotto, in «Il revisore
esterno».

```bash
python3 scripts/mep.py anteprima $L/tavola/<progetto>-t1.pdf
```

Scrive un PNG della tavola; `--zona x0,y0,x1,y1 --dpi 300` ne ingrandisce un riquadro, in
millimetri dall'alto a sinistra — su un A2 intero le valvole non si leggono. **Guardalo**, se
l'ambiente ti lascia vedere le immagini, con
[riferimenti/rivedere.md](riferimenti/rivedere.md): non ricalcolare quello che i rilievi hanno
già misurato; guarda quello che i numeri non dicono. Scrivi i **vincoli** in `$L/vincoli.md` —
mai mosse —, torna al passo 5 e ricomponi rispettandoli.

Ti fermi quando la tavola esce con **zero tratte cedute e zero rilievi bloccanti** e l'occhio non
ha più un vincolo che la migliori — se la prima tavola è già così, il giro è finito —; oppure
quando due giri di fila non migliorano: allora tieni la tavola migliore e dici perché ti sei
fermato. **Se non puoi vedere le immagini**, lavora sui
rilievi e dillo al progettista: la tavola non l'ha guardata nessuno prima di lui.

`regole-del-piano.md` ([riferimenti/regole-del-piano.md](riferimenti/regole-del-piano.md)) è
l'elenco delle regole del disegno con la fonte di ciascuna: si apre quando un rilievo cita una
regola e serve sapere da dove viene.

#### Il revisore esterno

Vuole un ambiente che lanci sub-agenti, come Claude Code o Cowork. Se non c'è, la tavola la
guardi tu e lo dici nella consegna.

1. **Una cartella con la sola tavola**, i rilievi e le istruzioni; niente grafo, niente piano:

   ```bash
   R=$L/revisione-1 && mkdir -p $R
   cp $L/tavola/<progetto>-t1.pdf $R/tavola.pdf
   cp $L/tavola/<progetto>-t1-rilievi.md $R/rilievi.md
   cp riferimenti/rivedere.md riferimenti/regole-del-piano.md $R/
   python3 scripts/mep.py anteprima $R/tavola.pdf --out $R/tavola.png
   ```

2. **Lancia un sub-agente** con il tuo stesso modello e dagli **questo testo e nient'altro**,
   con `{CARTELLA}` e `{SKILL}` al posto dei percorsi completi della cartella e della skill.
   Non aggiungere niente sull'impianto: il revisore serve perché non lo conosce.

   > Sei il revisore di una tavola di schema funzionale di impianto (centrale termica, aria-aria,
   > linee elettriche e di comando). Non l'hai
   > composta tu, e non sai niente dell'impianto oltre a quello che la tavola mostra.
   > Lavori solo con i file della cartella {CARTELLA}: non aprire, non cercare e non elencare
   > altri file. Tutto quello che ti serve è lì, più il comando per ingrandire.
   > 1. Leggi per intero {CARTELLA}/rivedere.md: sono le tue istruzioni, e bastano da sole.
   > 2. La tavola è {CARTELLA}/tavola.png (il foglio intero) e {CARTELLA}/tavola.pdf.
   > Guardala. Per ingrandire una zona: python3 {SKILL}/scripts/mep.py anteprima
   > {CARTELLA}/tavola.pdf --zona x0,y0,x1,y1 --dpi 300 --out {CARTELLA}/zoom-N.png, con
   > x0,y0,x1,y1 in millimetri dall'alto a sinistra del foglio; poi guarda zoom-N.png.
   > Scegli tu le zone.
   > 3. I rilievi già misurati sono in {CARTELLA}/rilievi.md: sono dati, non il tuo lavoro.
   > 4. {CARTELLA}/regole-del-piano.md si apre quando un rilievo o un tuo vincolo cita una
   > regola.
   > Restituisci il rapporto nella forma di rivedere.md §6, in italiano. In fondo aggiungi
   > una riga sola, che comincia con «VERDETTO:», con una di queste due frasi: «la tavola si
   > può consegnare così» oppure «la tavola va ricomposta prima di consegnarla», e il perché
   > in una frase.

3. **Il rapporto comincia con l'impianto come il revisore lo legge.** Confrontalo con il
   grafo: dove il racconto sbaglia — un circuito dato all'utenza sbagliata, un ritorno che
   non si capisce dove va —, la tavola si legge male anche se nessun rilievo lo dice. È un
   vincolo da scrivere.
4. **I vincoli nominano i pezzi con le sigle**, o li descrivono: li traduci negli
   identificativi del piano, li scrivi in `$L/vincoli.md` e ricomponi (passo 5). Un vincolo
   che il piano non sa esprimere cede, e lo dici. Le domande sul contenuto non sono vincoli:
   vanno al progettista.
5. **I vincoli si applicano anche quando il verdetto è «si consegna»**: il verdetto dice se
   la tavola si legge giusta, i vincoli la migliorano. Sulla tavola nuova, **un revisore
   nuovo**, con una cartella nuova (`revisione-2`). **Al più due revisori**:
   - ti fermi quando un revisore dice «si consegna» e non ha vincoli, e la tavola non ha
     rilievi bloccanti né tratte cedute;
   - se il secondo dice «si consegna» con dei vincoli, **non li applichi**: consegni la
     tavola che ha visto, e i suoi vincoli li dici al progettista come miglioramenti;
   - se il secondo dice «va ricomposta», applichi i suoi vincoli, guardi tu la tavola nuova
     e dici al progettista che l'ultima l'ha guardata chi l'ha composta.

   Se una tavola ricomposta ha più rilievi bloccanti o tratte cedute di quella prima, tieni
   quella prima, e dici perché.

### Su richiesta — la distinta materiali

Solo se il progettista l'ha chiesta, dopo il passo 4: è un documento a parte, la tavola non cambia.
Leggi **per intero** [riferimenti/distinta.md](riferimenti/distinta.md): dice come trovi la skill
dei report Nove C (`nove-c-report`), che fa il PDF; poi:

```bash
python3 scripts/mep.py distinta $L/grafo-completo.json --out $L/distinta --report <nove-c-report>
```

Scrive il **PDF per l'installatore** — copertina dei report Nove C, **a corpo, quantità
indicative, sopralluogo obbligatorio**, le tratte, il computo per sezioni, nessun prezzo —, la
distinta in JSON e il foglio dei calcoli. Senza la skill dei report scrive lo stesso contenuto in
Markdown, e lo dice. Le pagine del PDF le guardi una per una. Dove manca un dato la voce dice «DA
DEFINIRE» e diventa una domanda: non inventi la quantità. Esce con **2** se ci sono voci da
definire. Le domande le hai fatte al passo 2 con `--domande`: al lancio restano «DA DEFINIRE» solo
i dati che il progettista ha lasciato aperti.

Se il progettista chiede **quanto costa la minuteria**, o un prezzo di riferimento per confrontare
i preventivi, aggiungi `--costo` al comando: esce `costo-minuteria.md`, la distinta prezzata con
il listino interno di Nove C ([riferimenti/listino-minuteria.md](riferimenti/listino-minuteria.md),
con la data e la fonte di ogni prezzo). Quel conto lo dai al progettista e resta fuori dal
documento per l'installatore, che non ha prezzi. Una voce che non è nel listino resta «DA
PREZZARE»: non la stimi.

### Su richiesta — la pianta dei posizionamenti e dei tracciati

Solo se il progettista l'ha chiesta e ti ha dato la planimetria. **La planimetria la legge un
sub-agente** con [riferimenti/base.md](riferimenti/base.md) (il §2 dice che cosa passargli): torna
`base.json`, la base in dati — muri, aperture, stanze, balconi — e la sovrapposizione, che guardi.
Poi leggi **per intero** [riferimenti/pianta.md](riferimenti/pianta.md): nella base metti pezzi e
tracciati; il comando instrada i tracciati **ortogonali**, lungo i muri, pagando curve e sormonti, e
misura le lunghezze: con `--grafo` le scrive nel grafo (quelle del progettista restano), non a mano.
Poi rifai schema e distinta.

```bash
python3 scripts/mep.py pianta $L/pianta.json --out $L/pianta --grafo $L/grafo-completo.json
```

Le sigle e i numeri di tratta sono quelli dello schema funzionale. Guarda la tavola come al
passo 7: una scritta che indica la stanza sbagliata, un tracciato che fa il giro, un nodo troppo
fitto per la scala sono rilievi tuoi.

### 8. Consegnare

La tavola da consegnare è l'ultima eseguita, senza `--verifica`. Copiala dove il progettista la
riceve, con la distinta e la pianta se le hai fatte (un comando solo: aggiungi le loro cartelle)
— su claude.ai è `/mnt/user-data/outputs`; se quella cartella non c'è, lascia i file in
`$L/tavola` e dai i percorsi:

```bash
python3 scripts/mep.py consegna $L/tavola $L/distinta $L/pianta /mnt/user-data/outputs
```

Poi, in poche righe:

- **il PDF**, il DXF (si apre in AutoCAD) e i rilievi della tavola; la pianta e il PDF della
  distinta, accanto alle tavole, se le ha chieste;
- **che cosa resta aperto**: le assunzioni non confermate, i punti aperti, i rilievi che restano
  — detti con parole sue, non con i codici —, i campi del cartiglio «DA DEFINIRE» (la tavola
  allora è una **bozza**), un carattere che il PDF ha dovuto sostituire;
- le domande sul contenuto che ti sono venute componendo o rivedendo: come domande, non come
  decisioni prese;
- **chi ha guardato la tavola**: tu, oppure il revisore esterno, con il suo verdetto e i giri
  fatti; o nessuno, se l'ambiente non ti lascia vedere le immagini.

Se chiede come sono calcolati i diametri: dalla portata — che viene dalla potenza e dal salto
termico che ha dato lui, o dalla portata di progetto — il tubo commerciale più piccolo del suo
materiale (multistrato, se non dice altro) in cui la velocità sul diametro interno reale non
supera la massima del suo pollice (Caleffi, Quaderno n. 5, tab. 9). In tavola il tubo da
comprare, «MS 32×3», «DN 25 (1")», «Cu 28×1»; il diametro interno nel foglio dei calcoli.

## Come si parla al progettista

È un ingegnere esperto: niente spiegazioni di base, niente codici interni — nomi di file, di
regole, di rilievi — se non li chiede. Italiano, frasi corte. Ogni domanda porta la tua proposta,
così basta un sì. Un messaggio per passo, non uno per domanda.

## I file della skill

| file | che cosa è | quando si apre |
|---|---|---|
| [riferimenti/capire.md](riferimenti/capire.md) | le istruzioni di Capire: dal testo al grafo | al passo 1, per intero |
| [riferimenti/comporre.md](riferimenti/comporre.md) | le istruzioni di Comporre: dal grafo al piano | al passo 5, per intero |
| [riferimenti/rivedere.md](riferimenti/rivedere.md) | le istruzioni di Rivedere: dalla tavola ai vincoli | al passo 7 |
| [riferimenti/regole-del-piano.md](riferimenti/regole-del-piano.md) | le regole del disegno, con le fonti | quando un rilievo cita una regola |
| [riferimenti/distinta.md](riferimenti/distinta.md) | la distinta materiali per l'installatore | solo se il progettista la chiede |
| [riferimenti/listino-minuteria.md](riferimenti/listino-minuteria.md) | il listino interno della minuteria, con data e fonte dei prezzi | solo se il progettista chiede un costo |
| [riferimenti/pianta.md](riferimenti/pianta.md) | la pianta dei posizionamenti e dei tracciati | solo se il progettista la chiede |
| [riferimenti/base.md](riferimenti/base.md) | leggere la planimetria e trascriverne la base, per un sub-agente | con la pianta, a chi legge la planimetria |
| `dati/` | simboli, catalogo, regole degli accessori e della distinta — un file ciascuno —, nomi, cartiglio, lo schema e un esempio della pianta | li legge il comando; una voce e un manifesto si leggono con `catalogo <id>` e `simbolo <id>` |
| `scripts/mep.py` | il comando | si esegue, non si legge |

## Quando il comando si ferma

Il comando esce con **0** quando ha fatto, con **2** quando ha fatto ma qualcosa ferma la
consegna — un grafo che non regge, un piano che non si instrada, un rilievo bloccante —, con
**1** quando non ha potuto fare: un file che non si legge, un dato che manca. Il messaggio dice
sempre quale file e perché. `python3 scripts/mep.py <comando> --help` dice che cosa vuole
ciascun comando.
