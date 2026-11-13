# Consegna e collaudo del pezzo «Base»

> **A chi parla questo file.** A chi lancia la prova del pezzo che legge le planimetrie, a chi
> la giudica, e all'agente che consegna. Dice **che cosa** si restituisce, **come** si giudica,
> e come si conduce la prova in camera pulita. Le istruzioni operative dell'agente sono in
> `ISTRUZIONI.md`, qui accanto: questo file non le ripete.

---

## 1. Che cosa restituisce l'agente

Per ogni planimetria:

1. **la base**: `base.json`, che carica (`mep.py base base.json` non da' errore), con lo `sfondo`
   tarato, muri, aperture, stanze e balconi — niente pezzi, niente tracciati, niente arredi;
2. **la sovrapposizione** (PNG e PDF) e **la base standard** (il PNG di `mep.py pianta`): le
   immagini su cui si giudica;
3. **le domande e le stime**, in chiaro, ciascuna comprensibile da sola;
4. **la tabella dei locali** con i mq.

Un file che non carica non è una consegna. Una base senza la sovrapposizione guardata non è una
consegna: il controllo a vista è il pezzo.

## 2. Come si giudica

**Si giudica sulle immagini**, come il PO giudica le tavole (D-146): la sovrapposizione prima,
la base standard dopo, i numeri per ultimi.

**Criterio 1 — combacia.** Sulla sovrapposizione ogni muro rosso sta su un muro della
planimetria, e ogni muro della planimetria ha il suo rosso: entro 3 cm a 1:50, entro 10 cm a
1:200; su uno schizzo quotato vale la quota, e lo scarto dal disegno si accetta se ogni muro c'è
ed è nell'ordine giusto. Porte e finestre sui loro vani, le porte dalla parte in cui si aprono.

**Criterio 2 — c'è tutto, e solo quello.** Ogni locale dell'unità chiesta è una stanza col suo
nome (quello della planimetria, o dedotto e dichiarato); i balconi ci sono. Non c'è un arredo,
una quota, un retino, un'altra unità, un locale di un altro piano. Nel JSON non c'è un nome, un
indirizzo o un codice fiscale del committente.

**Criterio 3 — la taratura regge.** I controlli della console tornano: porte di 70–90 cm,
spessori plausibili, superfici plausibili; dove non tornano c'è una spiegazione. La taratura dice
da che cosa viene (quota, barra, scala dichiarata verificata), e se è una stima lo dice.

**Criterio 4 — ciò che la planimetria non dice è una domanda.** Il piano da trascrivere quando
il foglio ne ha più d'uno, una quota illeggibile, una foto troppo storta, un tratto ambiguo:
domande dichiarate. Una misura inventata e taciuta respinge, anche se era ragionevole.

Ogni difetto si classifica:

| esito | che cosa significa | a carico di chi |
|---|---|---|
| **muro, apertura o locale perso** | la planimetria lo mostra, la base non lo ha e non lo dice | dell'agente, o delle istruzioni |
| **inventato** | la base ha qualcosa che la planimetria non ha, e non lo dichiara | dell'agente, o delle istruzioni |
| **fuori posto** | c'è, ma la sovrapposizione mostra che non combacia oltre la tolleranza | della taratura o della lettura |
| **ambiguità dichiarata** | la planimetria non decide, e l'agente lo ha detto | di nessuno: è una domanda per il progettista |

Un difetto delle prime tre righe che viene da un buco delle istruzioni si cura nelle istruzioni,
e la prova **si ripete da capo con un agente nuovo**: chi ha visto il giudizio non è più in
camera pulita.

## 3. La prova in camera pulita

La prova misura se **le istruzioni bastano da sole**. L'agente di prova riceve **solo**:

| che cosa | dove |
|---|---|
| le istruzioni | `skill/base/ISTRUZIONI.md` (nella skill, `riferimenti/base.md`) |
| la planimetria | il file del PO, copiato nella sua cartella di lavoro |
| la richiesta | il testo del §2 delle istruzioni, coi posti riempiti: quale piano e quale unità, le misure note |
| il comando | `mep.py` della skill, da lanciare (lanciarlo non è leggere il repository) |

**Non riceve e non apre mai** le basi trascritte da altri (comprese quelle della sessione che ha
scritto le istruzioni), questo file, il repository, la storia del progetto. Niente correzioni in
corsa: se si blocca, il blocco è un risultato.

**Le planimetrie del PO portano nomi, indirizzi e codici fiscali: non entrano nel repository**,
né loro né niente che ne derivi — basi, immagini, sovrapposizioni. La prova si conduce in
sessione, e nel repository si registra **il verdetto**: per ogni planimetria il tipo, l'esito di
ciascun criterio, i difetti classificati, le domande che l'agente ha fatto, il tempo che ci ha
messo; le immagini si mostrano al PO in sessione.

**Le quattro planimetrie di REL-026** e che cosa ciascuna prova:

| planimetria | che cosa prova |
|---|---|
| il PDF di progetto dell'architetto, 1:50 su A3, con gli arredi | togliere gli arredi (armadi a muro compresi); le nicchie e i muri di spessore variabile; i nomi dei locali che mancano |
| il catastale dello stesso appartamento, 1:200 | la taratura sulla scala dichiarata di un catastale che è un'immagine nel PDF; i balconi che il progetto non disegna |
| il catastale con tre piani sullo stesso foglio | **la domanda** su quale piano, se la richiesta non lo dice; poi il piano giusto, e niente degli altri |
| il disegno a mano quotato e scansito | la taratura sulle quote nei due versi; le quote che prevalgono sul disegno; le porte senza verso |

La quinta del PO, la foto di un catastale stampato, prova la rotazione e la prospettiva: va fatta
appena c'è.

## 4. Quando il pezzo è finito

Quando, sulle planimetrie di prova, l'agente in camera pulita consegna basi che caricano, le cui
sovrapposizioni combaciano entro la tolleranza, senza arredi né dati del committente, con ogni
cosa non detta trasformata in domanda — e il giudizio non ha trovato difetti delle prime tre righe
che non fossero dichiarati. Allora la base della tavola è quella della planimetria del
progettista, ridisegnata in una grafica sola.
