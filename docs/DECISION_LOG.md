# Decision log — Disegnatore MEP

Registro sintetico delle decisioni funzionali e di processo. Le decisioni architetturali costose da cambiare saranno promosse in ADR dedicati.

| ID | Data | Stato | Decisione | Motivazione |
|---|---|---|---|---|
| D-001 | 2026-08-01 | Superata da D-017 | La prima famiglia era stata inizialmente limitata agli impianti idronici domestici aria-acqua. | Il brainstorming ha chiarito che il prodotto deve essere un disegnatore generale di impianti termici. |
| D-002 | 2026-08-01 | Approvata | La prima versione non effettua dimensionamenti né seleziona autonomamente le apparecchiature principali. | L'ingegnere conserva responsabilità e controllo progettuale. |
| D-003 | 2026-08-01 | Approvata | Il risultato è uno schema tecnico-esecutivo impiantistico senza annotazioni dettagliate di posa. | Servono valvole, strumenti e accessori, non un semplice schema funzionale. |
| D-004 | 2026-08-01 | Approvata | Prima del disegno, la skill presenta l'elenco delle integrazioni e attende l'approvazione. | Evita modifiche silenziose e mantiene rapido il controllo dell'ingegnere. |
| D-005 | 2026-08-01 | Approvata | Le integrazioni sono classificate come necessarie, raccomandate o condizionate. | Rende comprensibili priorità, obblighi e scelte progettuali. |
| D-006 | 2026-08-01 | Approvata | L'analisi include una prima interpretazione tecnica probabile e raccoglie tutte le domande in un unico passaggio. | L'ingegnere può approvare rapidamente con «sì, procedi». |
| D-007 | 2026-08-01 | Approvata | Le regole saranno costruite da zero usando fonti normative e tecniche autorevoli. | Non esiste uno standard grafico o tecnico interno preesistente. |
| D-008 | 2026-08-01 | Approvata | Il progetto usa Git locale; un repository online privato sarà valutato in seguito. | Versionamento immediato senza introdurre ora gestione remota. |
| D-009 | 2026-08-01 | Approvata | Ogni release produce una cartella `latest/` installabile e uno ZIP numerato in archivio. | Permette di trovare subito l'ultima versione e recuperare revisioni precedenti. |
| D-010 | 2026-08-01 | Approvata | Il primo impianto campione è un caso di accettazione, non una topologia codificata rigidamente. | Il motore deve comporre varianti a partire da componenti, porte, circuiti e regole generali. |
| D-011 | 2026-08-01 | Approvata | Il primo caso comprende pompa di calore aria-acqua, ACS con valvola deviatrice, bollitore, volano a quattro attacchi, circolatore secondario e collettore a due zone. | È abbastanza completo per verificare la prima grammatica senza definire il limite della skill. |
| D-012 | 2026-08-01 | Approvata | L'ingresso principale è il contesto della conversazione in cui l'ingegnere ha già definito l'impianto; non è richiesta una nuova descrizione o la compilazione preventiva di un modulo. | La skill viene richiamata con una richiesta come «ora disegna l'impianto deciso», interpreta il contesto e costruisce autonomamente il modello strutturato. |
| D-013 | 2026-08-01 | Approvata | Un unico riepilogo presenta impianto interpretato, integrazioni, assunzioni e domande; «sì, procedi» approva l'intero insieme. | Riduce il carico dell'ingegnere mantenendo trasparente l'interpretazione della skill. |
| D-014 | 2026-08-01 | Approvata | Dati documentali mancanti ma non bloccanti possono comparire come `DA DEFINIRE` in bozza; la versione finale richiede il loro completamento e non inventa valori. | L'ingegnere può completare calcoli come diametri e isolamenti nella stessa conversazione prima dell'emissione finale. |
| D-015 | 2026-08-01 | Approvata | I manuali di prodotto sono consultati solo quando una prescrizione specifica modifica topologia o accessori rappresentati; le prescrizioni di posa restano fuori scope. | Evita di sovraccaricare lo schema con dettagli non pertinenti al livello richiesto. |
| D-016 | 2026-08-01 | Approvata | Un prodotto che integra più funzioni viene rappresentato con un simbolo composito unico e riconoscibile, non con simboli separati annidati. | Il disegno resta pulito e comunica che si tratta di un solo componente da acquistare. |
| D-017 | 2026-08-01 | Approvata | Il prodotto usa un nucleo universale con pacchetti di dominio e una libreria iniziale ampia per idronica, aeraulica, espansione diretta/VRV, gas e reti ausiliarie. | La skill deve disegnare l'impianto deciso nella conversazione, anche quando combina più sistemi, non riprodurre pochi schemi tipo. |
| D-018 | 2026-08-01 | Approvata | Simboli, testi e spessori hanno dimensioni fisiche di stampa invarianti definite in millimetri di carta. | La complessità dell'impianto non deve ridurre la leggibilità o deformare la grammatica grafica. |
| D-019 | 2026-08-01 | Approvata | Quando l'impianto non entra nell'area utile, si producono più A3 coordinati; A1 e A0 restano alternative secondarie. | I progetti sono prevalentemente residenziali o del piccolo terziario e devono poter essere stampati facilmente in ufficio. |
