# L'ultima release: 1.10.0

`DisegnatoreMEP-v1.10.0.zip` — sha256 `11c6a81f5e60b47f…`, 141 file — è `REL-017`: **i rilievi di una commessa reale** (una
villetta con PdC Shenling 12 kW, volano a 4 attacchi, ACS su deviatrice, pavimento radiante; I-269 … I-277). Si carica
come ogni skill personale, dallo ZIP così com'è.

Rispetto alla 1.9.0:
- **il termostato ambiente a contatto** (`room-thermostat-contact`, sigla TAC-nn): in serie sulla linea quadro →
  circolatore, solo sulla tavola elettrica, in tabella e in legenda; niente relè d'appoggio, che resta per il
  circolatore comandato da un'uscita della pompa di calore (D-228); in distinta scatola 503 e traccia;
- **la tabella della tavola elettrica**: tutti i pezzi del foglio (deviatrice, miscelatrice, quadro, relè, sonde,
  comando) e solo dati elettrici — `alimentazione`, `potenza_elettrica_kw`, `corrente_max_a`, `cavo_minimo`, il
  `contatto` di relè e termostato; la tabella della tavola idraulica non cambia;
- **il vaso sanitario** fra il gruppo di sicurezza e il bollitore anche senza «produzione centralizzata»: la risposta
  del progettista si scrive `non_a_bordo: ["expansion"]` sul bollitore e il vaso lo mette la regola; un vaso scritto
  a mano a monte del non ritorno è un errore di validazione;
- **le note di posa del progettista** (`note_di_posa`, `note_tolte`): vengono prima, e sostituiscono la nota generata
  che comincia con la stessa parola; sempre al più cinque, solo nell'esecutivo;
- **la prevalenza della pompa a bordo**: con `prevalenza_utile_kpa` e le lunghezze del primario, un avviso se il giro
  più costoso perde più di quanto la pompa dà (Darcy-Weisbach, più il 30% di perdite concentrate);
- `completa` non perde più lunghezze, sezioni e scritte del progettista sulle tubazioni che riordina;
- **la grafica**: lo scarico senza freccia (e dal fondo di una macchina col colore del ritorno), la sigla di un pezzo
  alto accanto al suo simbolo, i simboli della legenda che non si toccano.

Con la deviatrice la portata del ritorno comune è già quella della macchina, non la somma (verificato, I-270): il
Øi 32 vicino alla PdC Shenling 12 kW è il DN dell'attacco (D-223).

Il banco di regressione di `REL-011` (24 tavole idroniche): 24 su 24 con 0 tratte cedute e 0 rilievi bloccanti.
Le prove sono in `docs/collaudi/REL-017/`.

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
