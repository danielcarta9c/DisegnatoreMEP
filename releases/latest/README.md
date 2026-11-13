# L'ultima release: 2.1.0

`DisegnatoreMEP-v2.1.0.zip` — sha256 `f80a8a05da5041e6…`, 155 file — è `REL-026` (I-300): **i rilievi d'uso della 2.0.0 su una
commessa**. Si carica come ogni skill personale, dallo ZIP così com'è.

Rispetto alla 2.0.0:
- **la base architettonica della tavola**: la planimetria (il PDF dell'architetto, un catastale, un disegno a mano)
  la legge un sub-agente con istruzioni proprie (`riferimenti/base.md`) e la trascrive in dati — muri, aperture,
  stanze, balconi —; il comando la ridisegna sempre nello stesso modo, in mezzatinta sotto l'impianto (muri grigio
  chiaro, finestre celesti, nome del locale con i mq); `mep.py base` la sovrappone all'origine per il controllo a vista;
- **le scritte che non stanno in pianta vanno fuori**, col richiamo; i riquadri di dettaglio solo se chiesti
  (`dettagli`); una scritta sola per due tubi che corrono insieme;
- **`pianta --grafo` scrive nel grafo le lunghezze misurate** (quelle del progettista restano, e si segnala quando la
  pianta misura altro; `--grafo-in-sola-lettura` per il solo confronto); il confronto con grafo e distinta non cambia
  più il formato del foglio; le forature spente di base (`"forature": true` le accende); `sagome_muri`; il nome corto
  dei fluidi nella tabella delle tratte;
- **nel catalogo**: il ventilconvettore canalizzato idronico col lato aria (`fan-coil-ducted-air`), il plenum di
  mandata non motorizzato da 2 a 6 uscite (`supply-plenum-2` … `-6`, sigla PL), provati anche col plenum motorizzato;
- **`vaso --sanitario`**: il vaso del bollitore da volume, temperatura d'accumulo, pressione di rete e taratura della
  valvola (metodo dal focus tecnico Caleffi 0851415; proposta, nessuna norma letta);
- le porte di comando non contano come attraversamento nelle portate; i terminali con marca e modello nella tabella
  delle apparecchiature.

Forma dei simboli, colori della base, metodo del vaso e uscita delle scritte sono **proposte** in attesa del PO
(`docs/collaudi/REL-026/RAPPORTO.md`, §6). Il banco: 30 casi, cambia la sola pianta del collaudo T3.

Prima, la **2.0.0**:
`DisegnatoreMEP-v2.0.0.zip` — sha256 `193f7194d2385472…`, 150 file — è **la versione da dare ai progettisti** (I-295,
I-299). Si carica come ogni skill personale, dallo ZIP così com'è; il nome della skill su claude.ai è
`disegnatore-mep`, qualunque sia il nome del file.

**È la 1.15.2 con il numero della 2.0**: tavole, distinta e pianta sono le stesse, byte per byte. Rispetto alla 1.15
la 2.0 porta il consolidamento fatto fin qui: ogni modifica passa da una CI con le prove su Python 3.11 e 3.12, il
controllo dei tipi e il confronto automatico di 28 tavole di riferimento; la skill senza rete non perde tempo a
ritentare; un accessorio «compreso con la PdC» non esce più in distinta. Il resto del consolidamento (la prova su sei
impianti tipo, la guida per il progettista) esce nelle 2.0.x; le funzioni nuove chieste dal progetto reale (I-297)
nella 2.1.

Prima, la **1.15.2**:

`DisegnatoreMEP-v1.15.2.zip` — sha256 `a65051b1430bd08b…`, 150 file — è la seconda consegna di `REL-024`, la 2.0 di
consolidamento. Si carica come ogni skill personale, dallo ZIP così com'è.

**Senza rete la skill non perde più tempo**: quando una libreria facoltativa (ezdxf per il DXF, pypdfium2 per
l'anteprima) non si riesce a installare, la skill lo dice una volta e non ritenta a ogni comando; pip non aspetta più
minuti su una rete che non risponde. **Un accessorio «compreso con la PdC»** (`compreso_in`: il filtro a Y, il
pozzetto) **non esce più in distinta**: la riga della pompa di calore dice «comprende …» (I-297, dal progetto reale).
Le tavole sono identiche alla 1.15.1, e da questa release lo dice una prova: il
banco delle 28 tavole di riferimento gira a ogni modifica.

Prima, la **1.15.1**:

`DisegnatoreMEP-v1.15.1.zip` — sha256 `732d0714e3dc3918…`, 150 file — è la prima consegna di `REL-024`, la 2.0 di
consolidamento (I-295, I-296). Si carica come ogni skill personale, dallo ZIP così com'è.

**Per chi disegna non cambia niente**: le tavole, la distinta e la pianta sono identiche byte per byte a quelle della
1.15.0 (`docs/collaudi/REL-024/RAPPORTO.md`). Cambia quello che sta sotto: il codice passa il controllo dei tipi
(mypy strict, 50 errori corretti) e ogni modifica passa da una CI con le prove su Python 3.11 e 3.12.

Prima, la **1.15.0**:

`DisegnatoreMEP-v1.15.0.zip` — sha256 `56514abd21c372c9…`, 150 file — è `REL-022` (I-288, I-289, D-237) e la prima parte
di `REL-023` (I-290 … I-292, D-238, D-239). Si carica come ogni skill personale, dallo ZIP così com'è.

Rispetto alla 1.14.0:
- **i tubi d'acqua dalla chat**: l'agente chiede al progettista, per rete, il tubo, i metri e l'isolamento (preisolato,
  o nudo con guaina e spessore) e li scrive nel blocco `distinta` del grafo, che `completa` non cancella; il grafo non
  dà più lunghezze per l'acqua;
- **i gomiti a corpo** come ipotesi (20) che si chiede in chat;
- **la pompa di calore a terra** su supporti antivibranti; le staffe solo se il progettista le chiede;
- **il differenziale di tipo A** in ambito domestico sulla linea della pompa di calore (il tipo B se il progettista lo
  scrive);
- **il listino rev. 04**: 27 voci nuove, dall'interruttore tipo B alle valvole antigelo, dai cavi 3G1,5 al circolatore
  sanitario; **rev. 05**: i nippli, dalle fatture dell'installatore;
- **le giunzioni**: un nipplo fra due accessori che si toccano, un raccordo a pressare fra tubo e accessorio, il tee dal
  grafo; ogni tratto fra due pezzi che non sono tee ha almeno un tubo; il tratto esterno dopo il giunto della pompa di
  calore;
- **niente valvole antigelo di base** nelle case: si chiedono per una seconda casa, una zona fredda, un tratto esterno
  lungo; senza, la nota 2 della tavola dice di tenere la pompa di calore alimentata d'inverno;
- **il circolatore** fra le apparecchiature (sezione A): Nove C lo compra a parte.

La PdC 12 kW con la 3 vie, con i metri di una commessa vera, esce a 1.425 € di materiale
(`docs/collaudi/REL-023/RAPPORTO.md`).

Prima, la **1.14.0**:

`DisegnatoreMEP-v1.14.0.zip` — sha256 `af0c5451bf57de42…`, 150 file — è `REL-019`, `REL-020` e `REL-021` (I-284 …
I-287, D-235, D-236): **la distinta della parte idronica e il costo della minuteria**. Si carica come ogni skill
personale, dallo ZIP così com'è.

Rispetto alla 1.12.1:
- **il listino della minuteria** nella skill (`riferimenti/listino-minuteria.md`): le 150 voci Tecnomat del PO e il
  riferimento online delle 18 che mancavano;
- **la distinta idronica**: la sezione I con il corredo di ogni pezzo d'acqua del catalogo — prima usciva tutto nella X;
- **`distinta --costo`**: il costo a listino del materiale, in `interno/`, fuori dal documento per l'installatore e
  dalla consegna; le voci che il listino non ha sono DA PREZZARE, col loro perché;
- la protezione si chiede solo sulle linee che partono dal quadro.

I collaudi (quattro agenti freschi) e il confronto col riferimento del PO sono in `docs/collaudi/REL-021/RAPPORTO.md`.
Il disegno non cambia.

Prima, la **1.12.1** (`REL-018`, D-234): le protezioni elettriche sulla tavola dell'elettrico.

Prima, la **1.11.0** (`REL-017`, D-233): sulla tavola il tubo da comprare e la riduzione all'attacco.

Prima, la **1.10.0**: i rilievi di una commessa reale (I-269 … I-277) — il termostato ambiente a contatto, la tabella
elettrica con i dati elettrici, il vaso sanitario messo dalla regola, le note di posa del progettista, l'avviso della
prevalenza, scarico, sigla e legenda.

Prima, la **1.9.0** (`REL-011`): il corredo contro il manuale Shenling e la specifica Nove C (D-217 … D-232).

Prima, la **1.8.1**: la terza via della deviatrice verso la serpentina del bollitore corre accanto al ritorno (I-240).

La 1.8.0 sono **i tre rilievi del collaudo della 1.7.0** (`REL-016`, I-237, I-239, D-216).

Rispetto alla 1.7.1:
- **una tavola aggrovigliata non si consegna**: una linea che scavalca sé stessa e un organo in linea su una piega sono
  rilievi bloccanti; `pezzi` dice in che ordine i pezzi stanno lungo le tratte, e Comporre li posa così;
- **il collettore di zona da 3 a 12 vie**, una mandata e un ritorno per via (proposta di simbolo);
- **le domande della distinta al passo 2**: `distinta --domande`, nello stesso giro delle domande del disegno.

Il banco di regressione di `REL-011` (24 tavole idroniche): 24 identiche. Le prove sono in `docs/collaudi/REL-016/`.

Prima, la **1.7.1** (I-236, D-215): i circolatori comandati dalla pompa di calore prendono alimentazione e comando
dalla sua morsettiera, con un cavo solo. E la **1.7.0** (`REL-015`):

Rispetto alla 1.6.0:
- **sulla tavola solo la tabella delle apparecchiature e la legenda** (I-233): tratte, computo e note vanno nel
  documento della distinta; la M.02 di riferimento e il canalizzato del collaudo T3 escono in A3;
- **la distinta in PDF** (I-232) con l'impaginazione della skill dei report Nove C, se è installata accanto
  (`distinta --report <cartella della skill>`): copertina senza KPI, niente «Chi siamo», niente Excel. Senza la skill
  dei report la distinta lo dice e scrive lo stesso contenuto in Markdown;
- **prima l'idraulica e l'aeraulica, poi l'elettrico e il comando** (I-231): le linee e i pezzi dell'acqua e dell'aria
  della tavola unica sono quelli della vista idraulica; le loro scritte si posano prima dei cavi, lasciando libera la
  strada dei cavi diritti e i pezzi del comando; i cavi si instradano dopo, intorno alle scritte;
- **il collettore a coppia col ritorno continuo** (I-231): cambia, solo nel simbolo, le tavole idroniche che lo usano;
- **la pompa di calore che regola da sé** (I-230, proposta): alimentata, con le sue sonde e le sue uscite di comando
  quando non c'è un regolatore d'impianto.

Il banco di regressione di `REL-011` (24 tavole): 19 identiche byte per byte, 5 cambiate soltanto nel simbolo del
collettore. Le prove sono in `docs/collaudi/REL-015/`.

Alla prossima versione questo file e lo ZIP si sostituiscono; la copia numerata resta in `../archive/`.
