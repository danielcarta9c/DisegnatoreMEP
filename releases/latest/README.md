# L'ultima release: 1.5.0

`DisegnatoreMEP-v1.5.0.zip` — sha256 `36d03a1f17ca154a…`, 104 file — è **il revisore esterno** (`REL-010`, I-216,
I-219, I-222, D-212 proposta) e **la tavola d'esempio senza i due difetti dell'occhio** (D-211). Si carica come ogni
skill personale, dallo ZIP così com'è.

Rispetto alla 1.4.1:
- **la tavola si può far rivedere a un revisore esterno**: un altro agente Claude, che non ha composto la tavola e non
  conosce l'impianto, la guarda a occhio fresco. La skill lo chiede al progettista con una domanda a scelta, insieme
  alle altre domande, **solo dove i sub-agenti ci sono** (Claude Code, Cowork); la proposta è la revisione in
  conversazione. Il revisore riceve la sola tavola, i rilievi e le istruzioni — niente grafo, niente piano —, con un
  incarico fisso; al più due revisori, uno nuovo per giro; la consegna dice chi ha guardato la tavola;
- **il revisore prima racconta l'impianto** che legge dalla tavola, e chi compone confronta il racconto con il grafo;
- **la soglia del PO** nelle istruzioni di Rivedere: che cosa ferma la consegna e che cosa no, tarata su tredici tavole
  che il PO ha giudicato (I-220, I-221), e lo sguardo dentro i simboli;
- **la serpentina del pannello radiante dentro il suo riquadro**, e **il giunto dell'ultima pompa di una cascata fuori
  dal prolungamento del collettore** (D-211).

La prova del passo 7 nelle due modalità, sulla tavola del caso rifatta, è in `docs/collaudi/REL-010/RAPPORTO.md` §5.

Alla prossima versione questo file e lo ZIP si sostituiscono; la copia numerata resta in `../archive/`.
