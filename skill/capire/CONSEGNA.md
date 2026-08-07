# Consegna e collaudo del pezzo «Capire»

> **A chi parla questo file.** A chi lancia la prova del pezzo 1, a chi la giudica, e
> all'agente che consegna. Dice **cosa** si restituisce, **come** si giudica, e come si
> conduce la prova in camera pulita. Le istruzioni operative dell'agente sono in
> `ISTRUZIONI.md`, qui accanto: questo file non le ripete.

---

## 1. Cosa restituisce l'agente

Per ogni impianto descritto nel testo, tre cose:

1. **Il grafo di prima stesura**: un file JSON, versione `1.1.0`, che carica con lo
   strumento di validazione del repository. Un file che non carica non è una consegna.
2. **L'elenco delle domande**: le voci `assumptions` del JSON, ripetute in chiaro nella
   risposta, impianto per impianto. Sono le domande e le assunzioni che l'ingegnere
   deve leggere: italiano piano, niente identificativi interni, ogni voce comprensibile
   da sola.
3. **La tabella di rilettura**: una riga per frase del testo, con gli elementi del
   grafo che la rappresentano oppure la voce di `assumptions` che la copre. È la prova,
   scritta dall'agente stesso, che niente è stato perso e niente è stato aggiunto.

Nient'altro. L'agente non consegna accessori, non consegna disegni, non consegna
proposte di completamento: quelli sono pezzi successivi della catena.

---

## 2. Come si giudica

I criteri sono quelli del piano di costruzione (§3bis-B), e si applicano così:

**Criterio 1 — ogni pezzo risale a una frase del testo.** Per ogni componente e ogni
tubazione del grafo deve esistere la frase che lo giustifica, e la tabella di rilettura
deve mostrarla. Un elemento senza frase è un'invenzione, e basta da solo a respingere.
I raccordi imposti dalla topologia descritta (il parallelo che esige confluenza e
ripartizione) risalgono alla frase che descrive la topologia.

**Criterio 2 — ciò che il testo non dice è una domanda.** Ogni scelta che il testo non
copre deve comparire in `assumptions`, come domanda o assunzione esplicita. Una scelta
fatta in silenzio — un punto di innesto deciso e non dichiarato, un numero di terminali
scelto e non dichiarato — respinge, anche se la scelta era ragionevole.

**Criterio 3 — il confronto con la lettura manuale.** Il grafo prodotto si confronta
con la lettura manuale congelata dello stesso testo (`examples/prova/*.json`).

**Su quali campi si giudica l'identità** (correzione imposta dal collaudo del 7 agosto):
sulle **reti** (dominio e fluido), sui **componenti** (voce di catalogo di ciascuno) e
sulle **tubazioni** (quale attacco con quale attacco, su quale rete) — cioè sulla
topologia, arco per arco. Le **sigle** (`tag`) e i **sottosistemi** restano fuori dal
confronto **per costruzione**: le letture manuali li portano, le istruzioni vietano di
inventarli, e due file corretti divergono lì senza che nessuno abbia sbagliato.

Le differenze **non sono automaticamente errori**: ognuna si classifica, una per una,
in uno di quattro esiti —

| Esito | Cosa significa | A carico di chi |
|---|---|---|
| **Detto dal testo e perso** | il testo lo dice, l'agente non l'ha rappresentato né dichiarato | difetto dell'agente (o delle istruzioni) |
| **Inventato** | l'agente ha scritto qualcosa che il testo non dice e non ha dichiarato | difetto dell'agente (o delle istruzioni) |
| **Assunzione tacita della lettura manuale** | la lettura manuale aveva risolto in silenzio ciò che le istruzioni trasformano in domanda o lasciano fuori | non è un difetto: è il pezzo 1 che lavora meglio della lettura a mano |
| **Ambiguità dichiarata da entrambe, risolta diversamente** | il testo non decide; tutte e due le letture lo dicono apertamente e chiudono in due modi diversi | non è un difetto di nessuno: è una domanda per il progettista, e si registra come tale |

**Criterio 4 — le letture manuali non si toccano.** Sono il metro, congelate come
sono: se si correggono per far combaciare il confronto, non misurano più niente. Vale
anche quando la lettura manuale ha torto: la differenza si classifica nel terzo esito e
si registra, il file non si cambia.

Chi giudica è un **collaudo a contesto separato**: non chi ha scritto le istruzioni,
non l'agente che ha prodotto i grafi. Il verdetto — con la classificazione di ogni
differenza — si registra nell'appendice del piano di costruzione, respingimenti
compresi.

---

## 3. Il protocollo di prova in camera pulita

La prova misura se **le istruzioni bastano da sole**. Perciò l'agente di prova lavora
isolato: se vede come la lettura è stata fatta a mano, la prova non prova niente.

**L'agente di prova riceve SOLO questo:**

| Cosa | Dove sta |
|---|---|
| Le istruzioni | `skill/capire/ISTRUZIONI.md` |
| Il testo del committente | `examples/prova/input/2026-08-06-impianti-di-prova.txt` |
| Il catalogo | `examples/layout/catalog/*.json` |
| Le tabelle dei nomi | `naming/families.json`, `naming/media.json` |
| Lo schema | `schemas/project.schema.json` |

Più lo **strumento di validazione** (il comando in `ISTRUZIONI.md`, §8 passo 7), che
può eseguire quante volte vuole.

**L'agente di prova NON riceve, e non apre, MAI:**

- le letture manuali: `examples/prova/prova-*.json` e
  `examples/prova/build_test_plants.py`;
- i grafi pubblicati: `docs/prodotto/grafi-di-prova/`;
- la documentazione del progetto: `HANDOFF.md`, `docs/SKILL.md`, il registro delle
  decisioni, i piani, le ADR;
- le prove automatiche (`tests/`), che contengono impianti già letti.

In pratica: **fuori dal kit della tabella, nel repository non si apre niente**, salvo
eseguire il comando di validazione. Il modo più pulito di condurre la prova è
consegnare il kit copiato in una cartella di lavoro separata, e lasciare del
repository solo l'ambiente per validare.

**Chi lancia la prova** scrive all'agente un incarico minimo: «leggi le istruzioni e
producile per questi impianti», più committente e codice di commessa per i metadati.
Niente suggerimenti sul contenuto, niente esempi risolti, niente correzioni in corsa:
se l'agente si blocca, il blocco è un risultato della prova e si registra.

**Le consegne restano agli atti** (correzione imposta dal collaudo del 7 agosto): i
grafi prodotti dagli agenti, le loro tabelle di rilettura e i loro rapporti si
conservano nel repository come allegati del verbale, così che il confronto sia
riproducibile da chiunque, dopo. La prova del 6 agosto non li ha conservati, e il suo
verbale è stato respinto proprio per questo: un confronto di cui restano solo le
conclusioni non è un confronto.

**Dopo la consegna**, il collaudo confronta e classifica (§2). Se una differenza rivela
un buco delle **istruzioni** — un caso che non sanno dire — la correzione si fa alle
istruzioni, si registra, e la prova **si ripete da capo con un agente nuovo**: un
agente che ha già visto il confronto non è più in camera pulita. E un agente nuovo
serve anche quando gli **esempi** delle istruzioni contengono le soluzioni dei testi di
prova: finché è così, la prova su quei testi non misura le istruzioni da sole — o gli
esempi diventano estranei ai testi, o i testi di prova diventano nuovi.

---

## 4. Quando il pezzo è finito

Quando, sui testi di prova, l'agente in camera pulita produce grafi che caricano, in
cui ogni elemento risale a una frase, in cui ogni cosa non detta è una domanda
dichiarata — e il collaudo ha classificato ogni differenza dalla lettura manuale senza
trovarne una nei primi due esiti. Allora vale la definizione del piano: da una
descrizione a parole esce un modello che l'ingegnere riconosce come il proprio
impianto, e ogni cosa non detta è una domanda posta.
