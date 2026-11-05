# L'ultima release: 1.12.1

`DisegnatoreMEP-v1.12.1.zip` — sha256 `2a3a66a9d86034ee…`, 147 file — è `REL-018`, con le tre scelte di D-234: **le protezioni elettriche sulla
tavola dell'elettrico** (I-278). Si carica come ogni skill personale, dallo ZIP così com'è.

Rispetto alla 1.11.0 (la 1.12.0 aveva il 6 kW a C16; la 1.12.1 lo porta a C20, scrive in Capire il differenziale separato
con la corrente del magnetotermico, e lascia le linee di servizio protette solo se dichiarate):
- **l'interruttore magnetotermico differenziale** (`circuit-breaker-rcbo`, sigla QF-nn) in serie sulla linea dal quadro
  alla pompa di calore, stretto all'uscita del quadro; in tabella («2P C32 · Idn 30 mA tipo B») e in legenda; simbolo
  proposto dalla sessione;
- **i dati elettrici delle Shenling** (manuale ThermaX R290 §7.4 p. 55; specifica Nove C §3.2–3.4, «vale il maggiore»),
  scritti da `completa` dove il progettista non li dà, e detti: 6 kW 16 A 3G4 C20 (D-234); 9 kW 20,5 A 3G4 C25; 12 e 15 kW
  30 A 3G6 C32; tutti 230 V 1~, differenziale 30 mA tipo B; il trifase solo se dichiarato (14 A, 5G2,5, 4P C16);
- **gli avvisi**: protezione sotto la corrente massima del manuale, cavo sotto la sua sezione, linea della pompa di
  calore senza protezione;
- **niente sezionatore locale** di regola (specifica §3.2): Capire lo mette solo se il testo lo chiede;
- **la distinta** con la voce dell'interruttore.

Il banco di regressione di `REL-011` (24 tavole idroniche): 24 su 24 con 0 tratte cedute e 0 rilievi bloccanti, tavole
identiche alla 1.11.0. Le prove sono in `docs/collaudi/REL-018/protezione/` e nella villetta di `REL-015/pdc-regola/`.

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
