---
name: disegnatore-mep
description: Disegna in PDF e DXF lo schema funzionale di una centrale termica (pompe di calore, caldaie, accumuli, ACS) descritta dal progettista. Da usare quando chiede lo schema o la tavola dell'impianto.
license: MIT, il testo completo in LICENSE.txt
compatibility: Richiede l'esecuzione del codice (claude.ai, Claude Cowork o Claude Code) con Python 3.11 o più recente. Al primo uso il comando installa pydantic 2 da PyPI se manca, e per questo serve la rete verso PyPI; ezdxf per il DXF e pypdfium2 per l'anteprima sono facoltative. Da usare con Opus o Sonnet.
---

# Disegnatore MEP

**Versione 1.2.2** — 3 ottobre 2026.

Il progettista ha già deciso e dimensionato l'impianto, e te lo descrive a parole. Tu ne fai la
**tavola dello schema funzionale**: la leggi, chiedi quello che manca, la fai approvare, la componi e
la consegni in PDF e DXF, con i rilievi dei controlli accanto.

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
- **i diametri delle tubazioni, se il testo non dice se li vuole**: chiedigli se vuole anche il
  dimensionamento. La tua prima interpretazione è no, e la tavola esce senza; per il sì gli dici
  su quali reti li calcoli e quali dati ti servono — i salti termici, le portate di progetto
  che il testo non dà —, così che risponda una volta sola (`capire.md` §4.7).

Il messaggio porta:

- che cosa hai capito, in poche righe: le macchine, i circuiti, come si collegano;
- le domande che cambiano il disegno, **ciascuna con la tua prima interpretazione**, così che
  il progettista possa rispondere «va bene» o correggere;
- le assunzioni che hai fatto per chiudere il grafo, da confermare tutte insieme;
- i dati che la tavola scrive e che il testo non dà, in una riga ciascuno: committente e
  commessa, indirizzo, titolo e numero della tavola; marca e modello delle apparecchiature;
  i salti termici e le portate, se ha chiesto i diametri.

Poi **aspetta la risposta**. Riporta le risposte nel grafo — un dato dato si trascrive, una
lettura corretta si ridisegna, un'assunzione confermata passa a `"status": "approved"` — e
rivalida.

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

### 4. L'approvazione — l'unico cancello

Niente si compone prima che il progettista abbia approvato il grafo completo. In un messaggio
solo gli porti:

- che cosa le regole hanno aggiunto, per famiglia — «12 valvole di intercettazione, 2 valvole
  di sicurezza, una per generatore…» —, e il perché solo se lo chiede;
- i punti aperti, come domande;
- le assunzioni ancora da confermare e i dati che mancano.

Il grafo completo non si manda come file: il progettista lo approva su questo messaggio, e lo
vede disegnato al passo 6.

Chiedi l'approvazione esplicita, e **aspettala**. Se corregge la lettura, torni al passo 1 e poi
al 3 e al 4. Se rifiuta un accessorio che le regole hanno aggiunto, la skill non sa ancora
toglierlo da sé: diglielo, e chiedi se procedere col grafo com'è — l'accessorio resta, e lo
scrivi fra le cose aperte — o fermarsi.

### 5. Comporre — il piano

Leggi **per intero** [riferimenti/comporre.md](riferimenti/comporre.md). Scrivi `$L/piano.json`:
dice dove sta ogni pezzo sul foglio, e niente altro. `python3 scripts/mep.py pezzi
$L/grafo-completo.json` elenca i pezzi che il piano posa — ingombro, rotazioni ammesse, porte — e
quelli in linea, che posa il motore; il manifesto intero di un simbolo lo stampa
`python3 scripts/mep.py simbolo <id>`.

### 6. Eseguire — la tavola e i rilievi

```bash
python3 scripts/mep.py disegna $L/grafo-completo.json --piano $L/piano.json --out $L/tavola
```

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

### 7. Rivedere — si guarda la tavola, e si torna al piano

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

### 8. Consegnare

La tavola da consegnare è l'ultima eseguita, senza `--verifica`. Copiala dove il progettista la
riceve — su claude.ai è `/mnt/user-data/outputs`; se quella cartella non c'è, lascia i file in
`$L/tavola` e dai i percorsi:

```bash
python3 scripts/mep.py consegna $L/tavola /mnt/user-data/outputs
```

Poi, in poche righe:

- **il PDF**, il DXF (si apre in AutoCAD) e i rilievi della tavola;
- **che cosa resta aperto**: le assunzioni non confermate, i punti aperti, i rilievi che restano
  — detti con parole sue, non con i codici —, i campi del cartiglio «DA DEFINIRE» (la tavola
  allora è una **bozza**), un carattere che il PDF ha dovuto sostituire;
- le domande sul contenuto che ti sono venute componendo o rivedendo: come domande, non come
  decisioni prese.

Se chiede come sono calcolati i diametri: il diametro interno netto minimo, dalla portata — che
viene dalla potenza e dal salto termico che ha dato lui, o dalla portata di progetto — e da una
velocità massima che cresce col diametro (Caleffi, Quaderno n. 5, tab. 9), prendendo il diametro
standard subito più grande.

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
| `dati/` | simboli, catalogo e regole degli accessori — un file ciascuno —, nomi, cartiglio | li legge il comando; una voce e un manifesto si leggono con `catalogo <id>` e `simbolo <id>` |
| `scripts/mep.py` | il comando | si esegue, non si legge |

## Quando il comando si ferma

Il comando esce con **0** quando ha fatto, con **2** quando ha fatto ma qualcosa ferma la
consegna — un grafo che non regge, un piano che non si instrada, un rilievo bloccante —, con
**1** quando non ha potuto fare: un file che non si legge, un dato che manca. Il messaggio dice
sempre quale file e perché. `python3 scripts/mep.py <comando> --help` dice che cosa vuole
ciascun comando.
