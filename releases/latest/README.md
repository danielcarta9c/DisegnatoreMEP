# L'ultima release: 1.9.0

`DisegnatoreMEP-v1.9.0.zip` — sha256 `248730560b224e43…`, 140 file — è `REL-011`: **le regole del corredo contro il
manuale Shenling ThermaX R290 e la specifica tecnica di installazione Nove C**, decise col PO un punto alla volta
(I-243 … I-264, D-217 … D-232). Si carica come ogni skill personale, dallo ZIP così com'è.

Rispetto alla 1.8.1:
- **il corredo della pompa di calore**: giunti antivibranti attaccati alla macchina; valvole antigelo nelle case (sopra i
  35 kW si chiede glicole o valvole); il ritegno su ogni generatore in parallelo, fra sicurezza e rubinetto; vaso,
  riempimento e manometro fra le macchine e il defangatore; il gruppo di riempimento con disconnettore;
- **le domande**: il volano a 4 attacchi quando manca, il vaso separato dalle macchine; gli avvisi del manuale
  (portata fuori campo, volano sotto il minimo, schema in serie);
- **il vaso dimensionato** (`mep.py vaso`) e **il livello del progetto**: nell'esecutivo precarica, tarature, pressione
  di carica e il riquadro delle note di posa;
- **il DN mai sotto l'attacco** delle Shenling;
- **il relè d'appoggio da 10 A** fra la pompa di calore e ogni circolatore;
- **la distinta** rivista su una commessa aria-aria, e la **lista della spesa** per l'installatore (`distinta --lista`).

Il banco di regressione di `REL-011` (24 tavole idroniche): tutte cambiano — la legenda del gruppo di riempimento e il
corredo nuovo —, 22 con gli stessi numeri, due tavole di confronto della prova del PO con più pieghe. Le prove sono in
`docs/collaudi/REL-011/`.

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
