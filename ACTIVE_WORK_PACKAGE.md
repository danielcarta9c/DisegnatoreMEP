# REL-026 — La 2.1.0: i rilievi d'uso della 2.0.0 su una commessa

> **Scritto il 13 novembre 2026.** Il PO ha usato la 2.0.0 su una commessa (BD.RM.260, tavola IM.03) e la sessione che
> la usava ha lavorato su una copia della skill, annotando che cosa ha dovuto cambiare e che cosa manca (I-300). Gli
> allegati sono in `docs/input-pm/2026-11-13-rilievi-bd-rm-260/`: `LEGGIMI.txt` (le richieste, con le priorità decise
> dal PO il 12 novembre), `modifiche-alla-skill.diff` (il codice cambiato nella copia), `estendi_catalogo.py` (i pezzi
> aggiunti al catalogo).

**Da svolgere:** l'agente unico (**D-147**) come PM; lo sviluppo esecutivo ad **agenti della sessione** (**D-152**),
su disposizione del PO (I-300): quello che riferiscono non è una misura finché la sessione non l'ha rieseguito.
**Stato:** **IN CORSO**
**Base:** `main` con la 2.0.0 (`a43e414`, PR #94). Ramo: `claude/magical-wright-ffrf86`.
**Approvazione della fusione:** **del PO**, guardando le tavole (D-146, D-147) e una spiegazione in termini semplici.
**Il numero:** **2.1.0** (I-300). Il contenuto di `REL-025` slitta alla 2.2. `REL-024` è sospeso
(`docs/plans/pacchetti/REL-024.md`): le sue fasi 2, 3 e 4 riprendono dopo.

## Il caso di prova

Il grafo e la pianta di BD.RM.260 **non entrano nel repository** (I-300: «solo in sessione»). Ogni voce si prova su
un caso del repository (`examples/pianta/`, i casi del banco) o su un caso anonimo scritto apposta; dove la commessa
vera serve a misurare (i 72 avvisi di `pianta --grafo`, il retino sulle sagome), la misura si fa in sessione sui file
del PO, e il rapporto dice se è stata fatta.

## Che cosa si fa

Tre blocchi. I primi due non si toccano fra loro e si sviluppano in parallelo; il terzo viene dopo il secondo.

### Blocco A — catalogo, schema, vaso (fuori dalla pianta)

| # | voce | origine |
|---|---|---|
| A-1 | **Tre pezzi nuovi**, simbolo e voce: il ventilconvettore canalizzato idronico con il lato aria (`fan-coil-ducted-air`), il plenum di mandata non motorizzato a 2 e a 3 uscite (`supply-plenum-2`, `supply-plenum-3`), la famiglia `air_distribution` con la sigla **PL**. Si parte da `estendi_catalogo.py`. Forma e sigla sono **proposte**, da giudicare sulla tavola. | LEGGIMI 1 |
| A-2 | **Il plenum a due uscite ha l'ingresso centrato** fra le due uscite, come quello a tre (I-300, risposta del PO): il plenum non è una tre vie, e B4 non lo deve trattare da tale. Il plenum di zona motorizzato che c'è già **non si tocca**: se ha lo stesso difetto si scrive nel rapporto. | LEGGIMI B3 |
| A-3 | **Le porte di comando non contano come attraversamento** nel calcolo delle portate: una pompa di calore con `power` e una sola uscita di comando collegata (`out_acs`) restava senza portata sul primario. Con la prova che lo riproduce. | LEGGIMI 2, diff |
| A-4 | **I terminali con marca e modello entrano nella tabella delle apparecchiature**, con potenza e portata. | LEGGIMI 3, diff |
| A-5 | **Il vaso sanitario**: il comando `vaso` dimensiona anche il vaso del bollitore ACS, da volume del bollitore, temperatura massima di accumulo, pressione di rete, taratura della valvola di sicurezza. Stesso impianto del vaso di riscaldamento (`vaso/calcolatore.py`): costanti con un nome, fonti dichiarate, e dove una fonte non è stata letta **lo dice**. Il metodo è una **proposta al PO**: il rapporto porta la formula, i margini e un esempio numerico. | LEGGIMI M1 |
| A-6 | **La distinta con le voci nuove**: i tre pezzi di A-1 in una distinta, con la colonna Fornitura; le prove sulle modifiche di A-3 e A-4. | LEGGIMI B5 |

### Blocco B — la pianta, prima parte

| # | voce | origine |
|---|---|---|
| B-1 | **Il nome corto dei fluidi idronici** nella tabella delle tratte (la scritta lunga finiva sulla colonna «Da»). | LEGGIMI 4, diff |
| B-2 | **`sagome_muri`**: campo facoltativo della pianta, poligoni in metri. Se c'è, il retino dei muri si disegna sulle sagome e non sui rettangoli asse-spessore di `muri`, che restano per l'instradamento. Vale nei riquadri di dettaglio (sagome ritagliate) e nel DXF (HATCH sul layer dei muri). Lo schema `schemas/pianta.schema.json` e le istruzioni della pianta aggiornati. **`muri_visibili` non entra** (LEGGIMI B4: è rimasto dalla rev02 e non serve). | LEGGIMI 5, B4, diff |
| B-3 | **Le forature spente di base**: niente F1/F2 sulla tavola, niente elenco, niente conteggio in distinta. Si accendono su richiesta del progettista, con un campo della pianta. Il costo della foratura nell'instradamento resta: è la scelta del percorso, non una scritta. | LEGGIMI B1 |
| B-4 | **Le lunghezze dalla pianta al grafo, in un passaggio solo.** Con `--grafo`, dopo la pianta le lunghezze misurate si scrivono nel grafo, con l'elenco di che cosa è cambiato; quelle date a mano dal progettista **restano** e vengono segnalate quando la pianta misura altro. Il grafo deve quindi dire da dove viene una lunghezza. Solo le lunghezze (e gli attraversamenti, se le forature sono accese): **la connettività non si tocca** (`docs/ARCHITETTURA-DEL-PIANO.md` §2). Un'opzione lascia il grafo in sola lettura. Schema e distinta, rifatti dopo, leggono i numeri nuovi. | LEGGIMI A1 |
| B-5 | **Il confronto con grafo e distinta non cambia il foglio.** Oggi `pianta --grafo` sulla commessa dà 72 avvisi e porta il foglio da A2 ad A1; `--distinta` lo porta in A1. Gli avvisi del confronto si riassumono sulla tavola e stanno per esteso nei dati; il formato lo decide il disegno, non l'elenco degli avvisi. | LEGGIMI A1, B2 |

### Blocco C — la pianta, seconda parte (dopo il blocco B)

| # | voce | origine |
|---|---|---|
| C-1 | **Le scritte che non stanno in pianta vanno fuori**, nello spazio bianco attorno alla pianta, collegate al pezzo da una linea di richiamo, incolonnate e senza incroci. **Niente tavole di dettaglio aperte in automatico**: il riquadro di dettaglio si fa solo se il progettista lo chiede (`dettagli` nella pianta). I numeri cerchiati con il testo in legenda **restano**. | LEGGIMI M2 |
| C-2 | **Una scritta sola per due tubi che corrono insieme** (M1/R1). | LEGGIMI M2 |
| C-3 | **Le sagome dei muri lette dal disegno di base**, con le correzioni a mano (aggiungi o togli una regione). Si parte da `muri_da_pdf.py` della commessa (base vettoriale). Per il catastale raster lo stesso criterio sull'immagine: **non provato** nella commessa, e se in sessione non c'è un catastale su cui provarlo esce dichiarato come tale o resta fuori. Dipende dai file del PO. | LEGGIMI M3, 6 |

## Fuori

La base vettoriale dell'architetto nel DXF (`base_e_retini_dxf.py`): resta uno script di commessa (LEGGIMI, «non
richiesto»). Il contenuto di `REL-025` (la 2.2). Le fasi aperte di `REL-024`.

## Che cosa decide il PO, e non la sessione

La forma dei tre simboli nuovi e la sigla PL; il plenum a due uscite centrato; il metodo del vaso sanitario; come
escono le scritte fuori pianta. Tutto si mostra sulla tavola o nella spiegazione, **prima** della fusione.

## Criteri di accettazione

Le tavole per prime; suite a 0 failed senza skip o xfail nuovi; `ruff check src tests` e `mypy` verdi; il banco verde,
con le tavole cambiate **registrate e mostrate** (`scripts/banco.py --registra`); nessun dato di cliente nel diff; la
2.1.0 costruita con `scripts/costruisci-skill.py` e `tests/test_le_release.py` verde; la CI verde sulla PR. Ogni
criterio con il comando e il suo output in `docs/collaudi/REL-026/RAPPORTO.md`.
