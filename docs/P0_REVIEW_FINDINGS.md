# Esito delle revisioni di P0

**Data:** 1 agosto 2026
**Stato del codice esaminato:** ramo `feat/p0-foundation-core`, 59 test verdi, `ruff` e `mypy --strict` puliti, gate G0 superato.

Questo documento raccoglie ciò che le revisioni di P0 hanno trovato e **non** è stato risolto dentro P0. Serve a due scopi: evitare che una sessione futura riscopra da zero le stesse cose, e distinguere ciò che l'agente può decidere da ciò che spetta al PM.

## 1. Come è stato revisionato

Ogni task è passato per un implementatore e almeno due revisioni indipendenti (conformità alla specifica, poi qualità del codice), con contesti separati. Al termine della fase sono stati eseguiti tre revisori finali in parallelo, su lenti diverse e senza comunicazione fra loro:

| Lente | Domanda | Verdetto |
|---|---|---|
| Conformità architetturale | Il codice rispetta la specifica approvata, gli ADR e il decision log? | Conforme con riserve |
| Correttezza avversariale | Si riesce a rompere il validatore o a fargli approvare un impianto incoerente? | Difetti reali trovati, i piu' gravi corretti |
| Prontezza per le fasi successive | Cosa faticherà in P1–P7 a causa di scelte fatte in P0? | Pronto con debito noto |

Due revisori indipendenti hanno individuato **la stessa** lacuna principale (§3.1). La convergenza fra lenti che non si sono parlate è il segnale piu' affidabile prodotto da questo metodo.

## 2. Difetti corretti dentro P0

Trovati dalla revisione avversariale e risolti prima della chiusura della fase.

| # | Difetto | Perché contava |
|---|---|---|
| D1 | Una connessione che univa un componente a sé stesso validava pulita | Falso PASS: una caldaia che manda nel proprio ritorno, senza terminali, usciva con `0` |
| D2 | Un valore numerico non finito faceva emettere alla forma canonica un testo non-JSON, e il salva-ricarica distruggeva il valore cambiando l'impronta | Minava la garanzia di riproducibilità su cui poggia l'intera fase |
| D3 | Tre codici diagnostici collassavano fra connessioni diverse | Quaranta connessioni rotte producevano una sola riga, non azionabile |
| D8 | Il messaggio di duplicato nominava come originale la connessione sbagliata | Indicava all'ingegnere l'entità sbagliata |

Corretti nel commit `2c78731`. La forma canonica dei dati ordinari non è cambiata: il fingerprint della fixture di riferimento è rimasto `3347374e8b3f006c6f387c6228e0d9d2b885cbf57e65991937e985af32306573`.

## 3. Il flusso di lavoro, e una lettura sbagliata da non ripetere

### 3.1 Cosa fa davvero la skill

**Chiarito dal PM il 3 agosto 2026, dopo che questa sezione conteneva una lettura errata.** Vale la pena fissarlo qui perché due revisori indipendenti erano partiti dallo stesso presupposto sbagliato, e chiunque legga la specifica senza questo inquadramento rischia di ripeterlo.

La skill **trasforma un input in uno schema grafico**. Non è un sistema di archiviazione né di gestione del ciclo di vita di un progetto. Il flusso è:

1. l'ingegnere progetta e dimensiona parlando, senza compilare moduli;
2. chiede «ora disegna l'impianto che abbiamo deciso»;
3. la skill ricostruisce l'impianto dalla conversazione;
4. applica le regole e determina cosa manca perché lo schema sia esecutivo: intercettazioni, filtro, vaso, sicurezza, sfiati, scarichi, ritegni, strumenti;
5. prima di disegnare presenta un riepilogo unico di interpretazione, integrazioni, assunzioni e domande residue;
6. l'ingegnere conferma o corregge;
7. la pipeline deterministica costruisce il modello, valida, dispone, instrada, renderizza ed esporta.

Il passaggio 6 **non è una macchina di stati persistente**: è una conferma dentro la conversazione. Se l'ingegnere rifiuta un'integrazione, la skill semplicemente non la inserisce. Non serve conservare proposte pendenti o rifiutate, perché una nuova esecuzione è una nuova conversazione. La memoria del passaggio è la conversazione stessa.

### 3.2 La lettura sbagliata, e cosa invece resta valido

Questa sezione affermava in precedenza che «il modello ha il vocabolario dell'approvazione ma non il meccanismo», e ne faceva il rischio principale della fase, con una decisione di prodotto da portare al PM su «dove vive una proposta non approvata». **Era sbagliato**: quel meccanismo non serve, perché il flusso non lo richiede. La domanda è stata ritirata (D-036).

Restano invece valide, e vanno affrontate in P1, tre osservazioni che quei revisori avevano colto correttamente:

- **`RuleApplicationModel` non porta né posizione funzionale, né quantità, né motivazione, né fonte**, richieste dalla §9 e da D-022, ed è l'unica entità priva di `evidence`. Servono per la **tracciabilità a valle** (D-039): quando l'ingegnere legge la distinta e trova accessori che non aveva nominato, deve poter risalire alla regola che li ha inseriti e al perché. Non servono per gestire un'approvazione pendente.
- **Manca la rappresentazione dei dati mancanti**, richiesta da §7.1 e D-014 e presupposta dal controllo che vieta `DA DEFINIRE` in una tavola finale. Questa è indipendente dal flusso di approvazione e resta un requisito reale.
- **`schema_version` è fissato a `Literal["1.0.0"]` senza percorso di migrazione.** Le due voci sopra comportano campi nuovi, quindi il tema va affrontato al primo cambiamento di modello, quando ancora non esistono file di progetto reali.

### 3.3 Invarianti riasseriti dal validatore

Con `validate_assignment`, un assegnamento rifiutato da un validatore di modello lascia comunque il valore scartato dentro l'istanza. La revisione avversariale ha mostrato che questo produce un verdetto **sbagliato**, non solo un oggetto sorprendente: un progetto con identificativi duplicati puo' essere portato in uno stato in cui `validate_project` lo dichiara pulito pur non riuscendo a ricaricare il proprio stesso dump.

Deciso (D-037): **il validatore riasserisce gli invarianti invece di fidarsi del costruttore**. Un cancello che presume corretto il proprio ingresso non è un cancello. L'eventuale immutabilità del modello resta un dettaglio implementativo dell'agente.

## 4. Da fare prima di specifiche fasi — tecnico, non del PM

| Rif. | Cosa | Quando serve |
|---|---|---|
| W3 | `DomainPack` esprime solo compatibilità fra due porte. Non vede proprietà del componente, connessione né grafo, quindi nessuna regola idronica o aeraulica reale è esprimibile. Va allargato **prima** che i quattro pacchetti P3 partano in parallelo, altrimenti ognuno modificherà il nucleo per conto proprio | Prima di P3 |
| W2 | `schema_version` è un letterale senza percorso di migrazione. Il primo campo aggiunto rompe letterale, esempi, schema esportato e file salvati | Prima del primo cambiamento di modello |
| W4 | Il componente in linea è rappresentabile ma **mai esercitato**: nessuna fixture ne contiene uno, `inline_gap_mm` non è letto da nessuna parte, e nulla lega due segmenti alla stessa tratta originaria | Primo compito di P4, non l'ultimo |
| W8 | La geometria vive sulla definizione di componente, non sul simbolo, e `symbol_id` punta a una libreria inesistente. Mancano i punti di ancoraggio delle etichette; l'area di rispetto è uno scalare, quindi non puo' essere anisotropa | Primo giorno di P2 |
| W9 | Nessun invariante lega `angle_deg` alla posizione della porta, e in tutte le fixture vale `0` anche per porte su lati opposti. Come dati di prova per l'instradamento sono inutilizzabili e vanno riscritti | Prima che P3 ne scriva centinaia nello stesso stile |
| W5 | `entity_ids` è una lista piatta di stringhe che mescola spazi di nomi diversi, e gli identificativi sono unici solo dentro la propria collezione. Un consumatore non puo' risalire dall'anomalia all'entità | Prima che P1 e P5 costruiscano dossier e preflight |
| W6 | `ValidationIssue` porta quattro dei campi che la §13 richiede: mancano regola, conseguenza e azione consigliata | Prima che P1 emetta diagnostiche di regola |
| W7 | `IssueSeverity` ha tre valori, la §13 ne elenca quattro: manca «correzione grafica automatica». Inoltre `ok` ignora `APPROVAL`, quindi un progetto con approvazioni pendenti esce `0` | P4/P5 |
| W12 | Il pacchetto installato non contiene catalogo, schema né esempi, e manca il comando di autoverifica dell'installazione richiesto dalla §15. La versione è duplicata fra `pyproject.toml` e `__init__.py` | P7 |

## 5. Controlli che il validatore non fa

Il validatore verifica **riferimenti**, non **topologia**: risponde a «ogni nome si risolve, e ogni coppia di porte concorda su dominio, fluido e verso?», non a «questo è un impianto?».

Passano puliti, oggi: una rete dichiarata e mai usata; un sottosistema o una tavola vuoti; identificativi duplicati dentro `component_ids`; `rule_applications.entity_ids` che puntano a entità inesistenti; due isole disgiunte senza alcun collegamento fra loro.

Il piu' importante da introdurre, e la ragione per cui non è stato fatto ora:

> **Un componente che non appartiene a nessun sottosistema.** Le tavole disegnano sottosistemi, quindi un componente fuori da tutti sparisce silenziosamente dall'elaborato: l'ingegnere consegnerebbe uno schema a cui manca una pompa senza che nulla lo avvisi. Un'omissione silenziosa dal disegno è peggio di un errore visibile. Non puo' essere bloccante perché i sottosistemi sono opzionali: serve prima la gravità «avviso», che in P0 non è ancora in uso.

Altri differiti per la stessa ragione: `MISSING_DOMAIN_PACK` (oggi un registry parziale solleva un'eccezione invece di produrre una diagnostica), il rimappaggio del codice di uscita `2` che `argparse` usa anche per errori di sintassi del comando, e il `glob` del catalogo che è sensibile alle maiuscole su Linux ma non su Windows, quindi lo stesso catalogo puo' dare verdetti diversi su piattaforme diverse.

## 6. Cosa ha retto agli attacchi

Utile quanto l'elenco dei difetti, perché dice dove **non** serve tornare.

- Determinismo del fingerprint fra processi separati e con `PYTHONHASHSEED` variabile.
- Nessuna collisione fra `True`, `1`, `1.0`, `False`, `0`; né fra `0.0` e `-0.0`, `1` e `1.0`, unicode NFC e NFD.
- Fedeltà del round-trip su denormali, valori estremi, caratteri di controllo, emoji e stringhe lunghe.
- Robustezza del catalogo: BOM, UTF-16, array JSON al posto di un oggetto, scalare nudo, file vuoto, directory chiamata `x.json`, identificativi duplicati fra file — sempre un errore pulito, mai un'eccezione non gestita.
- Invarianti geometrici delle definizioni: porte fuori dal riquadro, identificativi di porta duplicati, rotazioni non ortogonali o ripetute.
- Classificazione degli errori della CLI: percorso che è una directory, file mancante, JSON valido ma non un progetto, catalogo che punta a un file.
- Scala: 20 000 componenti e 20 000 connessioni, analisi in 0,21 s e validazione in 0,07 s, senza crescita quadratica.
