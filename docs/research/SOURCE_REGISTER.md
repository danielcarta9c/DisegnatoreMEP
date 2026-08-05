# Registro iniziale delle fonti

**Stato:** prima acquisizione effettuata il 4 agosto 2026, su richiesta del PM. Nessuna fonte è ancora stata tradotta in simboli della skill: la libreria attuale segue tuttora la convenzione interna, e questo è il difetto principale del progetto oggi. L'analisi è in `2026-08-04-come-si-disegna-uno-schema-funzionale.md`.

| ID | Fonte | Autorità/uso previsto | Stato |
|---|---|---|---|
| SRC-001 | [ISO 5457:1999](https://www.iso.org/standard/29017.html) | Formati e organizzazione delle tavole tecniche; confermata da ISO nel 2021 | Da acquisire e valutare |
| SRC-002 | [ISO 7200:2004](https://www.iso.org/standard/35446.html) | Campi dati dei cartigli e intestazioni; confermata da ISO nel 2025 | Da acquisire e confrontare con cartiglio Nove C |
| SRC-003 | [ISO 14617-1:2025](https://www.iso.org/standard/85641.html) | Regole generali di preparazione e presentazione dei simboli per diagrammi | Da acquisire e valutare |
| SRC-004 | [ISO 14617-2:2025](https://www.iso.org/standard/83364.html) | Libreria generale di simboli per componenti e processi | Da acquisire e mappare |
| SRC-005 | [ANSI/ASHRAE Standard 134-2005 (RA 2014)](https://www.ashrae.org/File%20Library/Technical%20Resources/ASHRAE%20Handbook/Standards-and-Guidelines-List.pdf) | Linguaggio simbolico HVAC&R; riferimento complementare da verificare rispetto alla pratica italiana | Da acquisire e valutare |
| SRC-006 | [SVG 2 - Coordinate Systems, Transformations and Units](https://www.w3.org/TR/SVG/coords.html) | Unità, coordinate, trasformazioni e spessori vettoriali | Consultata per il design |
| SRC-007 | UNI 9511 (5 parti, 1989), «Disegni tecnici. Rappresentazione delle installazioni» | **La** simbologia italiana degli impianti civili: riscaldamento, condizionamento, idrosanitario, gas. È la norma che un termotecnico italiano si aspetta, ed è quella che mancava | **Non si acquista.** I suoi segni grafici sono riprodotti per esteso in materiale didattico e di settore liberamente accessibile: si usano quelli, citati come fonte secondaria (SRC-015) |
| SRC-015 | Tabelle dei segni grafici UNI 9511 riprodotte in materiale didattico: [«Norma UNI 9511 — Segni grafici», tabelle utili, prof. Guerra](https://professoreguerra.altervista.org/alterpages/files/UniIdraulica1.pdf); [dispensa di simbologia, Università di Ferrara](https://docente.unife.it/graziano.trippa/materiale-didattico-e-avvisi-lca1-2009-2010-corso-a/SIMBOLOGIA%20def.pdf/at_download/file) | I segni grafici della norma, con le denominazioni italiane, tavola per tavola: giunzioni e accessori per tubazioni, apparecchiature per la distribuzione di acqua, gas e vapore, filtri, vasi di espansione (aperto, a membrana, autopressurizzato), scambiatori, pompe, terminali | **Acquisita il 4 agosto 2026**, dieci tavole verificate a schermo. **Fonte secondaria**: il campo `source` dei simboli dirà «UNI 9511, tramite SRC-015», mai «UNI 9511» |
| SRC-008 | [Caleffi — Quaderni e Tabelle](https://www.caleffi.com/it-it/formazione/quaderni-e-tabelle); [Componenti e schemi per impianti a pompa di calore aria-acqua](https://www.caleffi.com/sites/default/files/media/external-file/25%20-%20Componenti%20e%20schemi%20per%20impianti%20a%20pompa%20di%20calore%20aria-acqua.pdf) | Casi di studio e prescrizioni di prodotto (D-015). Distinguono separatore idraulico, compensatore e accumulo inerziale, che il nostro `buffer-four-port` confonde | Consultata il 4 agosto 2026 |
| SRC-009 | [Schema funzionale centrale termica — Condominio Tower House, Treviso, Divisione Energia srl](https://www.divisionenergia.it/wp-content/uploads/2025/02/Cond.TH_schema-ct-as-built.pdf) | Caso di studio di tavola reale: legenda tubazioni, composizione a corsie, diametri sulle linee, sigle funzionali, tabelle. Documento pubblico | Letta e misurata il 4 agosto 2026, **non riprodotta** |
| SRC-010 | [Schema funzionale centrale termica — Liceo «G. Ballardini», Provincia di Ravenna](https://presadmin.provincia.ra.it/content/download/88849/1115730/file/SM04%20-%20BALLARDINI%20Stato%20Modificato%20Schema%20funzionale%20Centrale%20Termica.pdf) | Caso di studio: legenda colori tubazioni con mandata e ritorno distinti, sigle, tabella caratteristiche pompe. Documento pubblico di gara | Letta il 4 agosto 2026, **non riprodotta** |
| SRC-011 | [Segni grafici nella rappresentazione dei componenti — CT Energia](https://www.ctenergia.it/wp-content/uploads/downloads/2014/04/00-Lez.-cap.-1-segni-grafici-nella-rappr.-componenti.pdf) | Materiale didattico sulla rappresentazione degli impianti fluidotermici | Acquisita il 4 agosto 2026 |
| SRC-012 | **Raccolta R, edizione 2009** — specificazioni tecniche applicative del Titolo II del D.M. 1.12.1975, ai sensi dell'art. 26. [Testo integrale commentato Caleffi](https://raccoltar.caleffi.it/pdf/raccolta_r_commentata_caleffi.pdf), [testo Raccolta R](https://raccoltar.caleffi.it/pdf/raccolta_r.pdf) | **Prescrizione normativa applicabile**, livello 1 della gerarchia §9.1: attua un decreto ministeriale. In vigore dal 1° marzo 2011 (circolare INAIL 1-IN/2010). Il cap. R.3.B.1 elenca i dispositivi obbligatori di un impianto a vaso chiuso; R.2.A i dispositivi di sicurezza e i loro dimensionamenti; R.3 le configurazioni di impianto | **Acquisita e letta il 4 agosto 2026**, 55 pagine. Liberamente accessibile |
| SRC-013 | **UNI 10412-1:2006** «Impianti di riscaldamento ad acqua calda — Requisiti di sicurezza — Parte 1: generatori alimentati da combustibili liquidi, gassosi, solidi polverizzati o **generatori di calore elettrici**» | Coprirebbe il caso di accettazione D-011, che è a **pompa di calore** e che la Raccolta R esclude | **Non acquistata, e non blocca.** Le regole di sicurezza per la pompa di calore restano su buona pratica documentata e manuali di prodotto, dichiarati come livello 2-3. Resta registrata qui come acquisto possibile, non come prerequisito |
| SRC-014 | **UNI 8065:2019** «Trattamento dell'acqua negli impianti termici ad uso civile», tramite guide di settore: [Guida Aqua Italia](https://www.atlasfiltriengineering.com/sites/default/files/news/files/Giuda%20Aqua%20Italia_UNI.8065.19_0.pdf) | Filtro di sicurezza, filtro dissabbiatore, condizionamento chimico, soglie di addolcimento. La norma è a pagamento; le guide ne riportano le prescrizioni con soglie puntuali | Guide **consultate il 4 agosto 2026**. Fonte **secondaria**: le regole che ne derivano citano la guida, non la norma |

## Convenzioni grafiche interne

Le fonti esterne sopra non sono ancora state acquisite, quindi **nessun simbolo della libreria
ne deriva**. I simboli seguono forme schematiche di pratica comune, codificate come convenzione
interna del progetto e citate nel campo `source` di ogni manifesto.

| ID | Ambito | Definita in | Stato |
|---|---|---|---|
| CONV-GRAFICA-001 | Forma e geometria di un simbolo singolo: dimensioni in millimetri di carta, porte sul perimetro con faccia coerente, area di rispetto sulle facce con porta, orientamenti tecnicamente ammessi | `docs/GRAPHIC_STANDARD.md` | In uso: la citano i dodici simboli pubblicati e gli otto di fixture |
| CONV-GRAFICA-002 | Composizione di un simbolo composito da primitive, pubblicato e contato come prodotto unico | `docs/GRAPHIC_STANDARD.md` §6 | Definita, nessun composito ancora pubblicato |
| CONV-GRAFICA-003 | Squadratura e impaginazione del foglio: margini, banda del cartiglio, fascia d'intestazione, area di disegno | `assets/cartigli/Cartiglio_NoveC_A3.pdf`, misurato | Da applicare al Task 4 del piano di layout |
| CONV-GRAFICA-004 | Scavallo su un incrocio fra linee che non si collegano: archetto sulla linea **verticale**, la orizzontale prosegue intera; nessuno scavallo su una piega | Schizzo a mano del PM, 5 agosto 2026 (D-079) | Da implementare nel rendering; la scelta di quale linea scavalca va confermata sulle tavole di riferimento |

**Il telaio del foglio deriva dal cartiglio aziendale, non da ISO 5457.** `A3_LANDSCAPE`
motiva oggi il proprio margine sinistro da 20 mm con la rilegatura ISO 5457, che questo
registro elenca come SRC-001 «da acquisire e valutare»: non ottenuta, non valutata. Il
cartiglio Nove C — fornito dal PM nel primo commit del progetto, `fa7157c` del 1 agosto 2026 —
usa invece 10 mm sui quattro lati. È lo stesso errore che D-047 ha corretto per i simboli:
una geometria attribuita a una norma che il progetto non possiede, mentre lo standard
aziendale reale era già sul disco. CONV-GRAFICA-003 registra la provenienza vera.

**Perché una convenzione interna e non una norma.** ANSI/ASHRAE 134 (SRC-005) sarebbe il
riferimento naturale per la simbologia HVAC, ma il registro la classifica «da acquisire e
valutare»: non è stata ottenuta, non è stata confrontata con la pratica italiana e la sua
licenza non è stata verificata. Dichiararla come fonte di simboli disegnati altrimenti sarebbe
un'attribuzione falsa proprio nel campo che esiste per la tracciabilità (D-047).

**Ma la convenzione interna era un ripiego, non una destinazione.** La ricerca del 4 agosto
2026 ha mostrato che il riferimento giusto per la pratica italiana non era ASHRAE ma
**UNI 9511** (SRC-007), che nessuno aveva cercato. `CONV-GRAFICA-001` e `CONV-GRAFICA-003`
restano dichiarazioni oneste di provenienza per ciò che c'è oggi, non una scelta difendibile
per la libreria definitiva: i venti simboli pubblicati coprono meno di un ottavo di quelli
che una tavola reale usa. Si veda `2026-08-04-come-si-disegna-uno-schema-funzionale.md`.

## Cercate in rete il 4 agosto 2026, e perché non si usano

Il PM ha chiesto se una ricerca seria trovasse in rete i PDF delle norme. La ricerca è
stata fatta ed è servita: ha prodotto SRC-012, SRC-013 e SRC-014. Ha anche prodotto due
esiti negativi che vanno registrati, perché altrimenti qualcuno li riscoprirà.

**UNI 9511 parti 4 e 5 compaiono su Scribd**, caricate da utenti. Sono documenti UNI
protetti da diritto d'autore, senza licenza dichiarata. Non vengono usati. Il motivo non
è cautela generica: questo registro impone di annotare **edizione e licenza** di ogni
fonte, e «trovato su Scribd» non è una licenza. Scriverla nel campo `fonte` di una regola
che finisce in un dossier firmato da un ingegnere sarebbe la stessa classe di errore che
D-047 ha corretto per i simboli — attribuire a una norma ciò che il progetto non possiede.

**Esistono materiali didattici che riportano i segni grafici UNI 9511** — dispense
universitarie e scolastiche. Servono come riscontro incrociato, non come fonte: sono
rielaborazioni di terzi, senza garanzia di completezza né di edizione.

## La Raccolta R non copre il caso di accettazione

Va scritto qui perché è il vincolo che decide il perimetro di P1. La Raccolta R si applica
agli impianti «utilizzanti acqua calda sotto pressione con temperatura non superiore a
110 °C e potenza nominale massima complessiva dei **focolari** superiore a 35 kW»
(cap. R.1.A.1). Una pompa di calore non ha focolare e la sorgente elettrica non rientra nel
campo del D.M. 1.12.1975: [Caleffi lo dichiara
esplicitamente](https://www.caleffi.com/it-it/blog/le-pompe-di-calore-e-la-raccolta-r).

Quindi la fonte normativa gratuita copre **integralmente** una centrale a combustione e
**non copre** il caso D-011, che è a pompa di calore. Per quello serve SRC-013.

## Il perimetro della ricerca normativa

Deciso dal PM il 4 agosto 2026, dopo che questa sessione stava aprendo un programma di
acquisizione normativa: **la skill non deve diventare un manuale di progettazione.** La
ricerca aiuta, non è il cuore. La maggior parte di ciò che serve — quale accessorio ci
vuole e dove — è buona pratica consolidata, e non richiede di comprare norme.

Ne segue una regola pratica per chi scrive le regole di P1:

- il **contenuto** di una regola viene dalla buona pratica e dai manuali dei produttori;
- la **fonte dichiarata** deve dire il vero: «buona pratica tecnica documentata» con un
  riferimento puntuale è una risposta corretta e sufficiente, e vale più di una citazione
  normativa gonfiata;
- si sale di livello nella gerarchia §9.1 solo quando la fonte c'è davvero, come per la
  Raccolta R (SRC-012);
- non si apre una ricerca normativa per una regola che nessuno contesta.

## Regole di utilizzo

- Registrare edizione, data di consultazione, ambito e licenza.
- Separare prescrizioni normative, buona pratica e convenzioni grafiche.
- Non copiare integralmente contenuti protetti: estrarre regole motivate e riferimenti puntuali.
- Verificare la pertinenza italiana/europea prima di promuovere una fonte a base normativa.
- Associare ogni regola implementata ad almeno una fonte o a una convenzione interna esplicitamente approvata.
- Trattare gli schemi dei produttori come casi di studio e prescrizioni di prodotto, non come standard universali.
