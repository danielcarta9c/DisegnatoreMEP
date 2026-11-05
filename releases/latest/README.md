# L'ultima release: 1.13.0

`DisegnatoreMEP-v1.13.0.zip` — sha256 `0d86685a8bdd35de…`, 148 file — è `REL-019` (I-284 … I-286, D-235): **il listino
interno della minuteria** nella skill. Si carica come ogni skill personale, dallo ZIP così com'è.

Rispetto alla 1.12.1:
- **`riferimenti/listino-minuteria.md`**, dal foglio del PO (`listino_minuteria_pdc_rev02.xlsx`):
  - le 150 voci Tecnomat del 2 novembre;
  - il riferimento online delle 18 voci che mancavano, con 167 riscontri, la forbice e la mediana per misura e il link
    di ogni prezzo;
  - quello che resta da prezzare;
- **`SKILL.md`** lo nomina nella sezione della distinta: l'agente lo apre solo quando il progettista chiede un costo, e
  una voce che manca resta «DA PREZZARE»;
- **il documento della distinta per l'installatore resta senza prezzi**; disegno e distinta invariati.

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
