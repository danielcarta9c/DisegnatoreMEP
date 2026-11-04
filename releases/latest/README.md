# L'ultima release: 1.11.0

`DisegnatoreMEP-v1.11.0.zip` — sha256 `2fd795f3dcca463a…`, 144 file — è ancora `REL-017`, con **il tubo da comprare
sulla tavola** al posto del diametro interno (I-279, I-281, D-233). Si carica come ogni skill personale, dallo ZIP così
com'è.

Rispetto alla 1.10.0:
- **il materiale delle tubazioni** (`materiale_tubazioni`: multistrato, acciaio, rame; sul progetto o sulla rete),
  multistrato se il testo non lo dice, dichiarato come assunzione;
- **il tubo commerciale scelto per velocità** (tab. 9 del Quaderno Caleffi 5, sul pollice del tubo): «MS 32×3»,
  «DN 25 (1")», «Cu 28×1» sulla tavola, con la riga della legenda del materiale; l'Øi resta solo nel foglio dei calcoli
  (Øi minimo, tubo, Øi reale, velocità); le tabelle dei tubi con le fonti in `diametri/tubi.json`;
- **il tubo del progettista vince** (`sezione`), con un avviso se la velocità supera il limite;
- **una scritta per tratta**, niente sui tratti cortissimi fra due raccordi e sugli stacchi;
- **la distinta** con la stessa dicitura («multistrato MS 32×3») e il pollice degli accessori in linea;
- **la nota dell'isolamento** con lo spessore sul tubo vero («MS 32×3: 30 mm»);
- **l'attacco della Shenling non è più un minimo** (D-233, emenda D-223): di regola MS 32×3 sul 12 kW, MS 40×3,5 sul
  15 kW; dove il tubo è sotto l'attacco c'è **la riduzione all'attacco**, un pezzo con il suo simbolo (trapezio, proposta)
  subito dopo il giunto antivibrante, in legenda e in distinta;
- **la prevalenza della pompa a bordo**: senza il dato del progettista, 8 m c.a. sulle Shenling (indicativo del PO).

Il banco di regressione di `REL-011` (24 tavole idroniche): 24 su 24 con 0 tratte cedute e 0 rilievi bloccanti.
Le prove sono in `docs/collaudi/REL-017/tubi/` e `docs/collaudi/REL-017/riduzione/`.

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
