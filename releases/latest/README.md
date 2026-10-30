# L'ultima release: 1.7.0

`DisegnatoreMEP-v1.7.0.zip` — sha256 `39031f6bb96524bb…`, 134 file — è **la distinta in un documento a parte, la
tavola in A3, l'elettrico dopo l'idraulica** (`REL-015`), sulle osservazioni del PO alla 1.6.0 (I-230 … I-234). Si
carica come ogni skill personale, dallo ZIP così com'è.

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
