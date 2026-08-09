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
| SRC-016 | **Tavole UNI 9511 pubblicate da Oppo**, dieci tabelle scaricabili anche in DWG e PDF: [Tab. 1 Tubazioni e canalizzazioni](https://www.oppo.it/disegni/simboli_idra_1.htm), [Tab. 2 Giunzioni e accessori](https://www.oppo.it/disegni/simboli_idra_2.htm), [Tab. 3 Valvolame](https://www.oppo.it/disegni/simboli_idra_3.htm), [Tab. 4 Pozzetti e scarichi](https://www.oppo.it/disegni/simboli_idra_4.htm), Tab. 5-10 sonde, grandezze, fluidi, sigle di componente, apparecchi indicatori — indice in [a_disegni-elenco.html](https://www.oppo.it/disegni/a_disegni-elenco.html) | **Indicata dal PM il 5 agosto 2026** come la simbologia giusta. È la stessa norma di SRC-015, ma pubblicata da un operatore del settore e **con la geometria scaricabile in DWG**: è la fonte di lavoro per rifare la libreria. Copre tubazioni, giunzioni, valvolame, scarichi, strumenti — **non** le macchine (pompa di calore, bollitore, volano, circolatore, collettore), che vengono dalla pratica e dai manuali dei produttori | **Acquisita e letta il 5 agosto 2026**, tabelle 1-4 verificate a schermo. Fonte secondaria come SRC-015: il campo `source` dirà «UNI 9511, tramite SRC-016» |
| SRC-008 | [Caleffi — Quaderni e Tabelle](https://www.caleffi.com/it-it/formazione/quaderni-e-tabelle); [Componenti e schemi per impianti a pompa di calore aria-acqua](https://www.caleffi.com/sites/default/files/media/external-file/25%20-%20Componenti%20e%20schemi%20per%20impianti%20a%20pompa%20di%20calore%20aria-acqua.pdf) | Casi di studio e prescrizioni di prodotto (D-015). Distinguono separatore idraulico, compensatore e accumulo inerziale, che il nostro `buffer-four-port` confonde. **Cinque schemi applicativi completi** (monoblocco, monoblocco con gruppi miscelati, split, split con solare, hydrosplit): in tutti e cinque il corredo di rete — vaso, defangatore, gruppo di caricamento — sta sul **ritorno generale del primario**, una volta sola, e nessuno schema aggiunge sicurezze o termometri per generatore | Consultata il 4 agosto 2026; **riletta per intero il 7 agosto 2026** per il riscontro di D-106, schema per schema |
| SRC-009 | [Schema funzionale centrale termica — Condominio Tower House, Treviso, Divisione Energia srl](https://www.divisionenergia.it/wp-content/uploads/2025/02/Cond.TH_schema-ct-as-built.pdf) | Caso di studio di tavola reale: legenda tubazioni, composizione a corsie, diametri sulle linee, sigle funzionali, tabelle. Documento pubblico | Letta e misurata il 4 agosto 2026, **non riprodotta** |
| SRC-010 | [Schema funzionale centrale termica — Liceo «G. Ballardini», Provincia di Ravenna](https://presadmin.provincia.ra.it/content/download/88849/1115730/file/SM04%20-%20BALLARDINI%20Stato%20Modificato%20Schema%20funzionale%20Centrale%20Termica.pdf) | Caso di studio: legenda colori tubazioni con mandata e ritorno distinti, sigle, tabella caratteristiche pompe. Documento pubblico di gara | Letta il 4 agosto 2026, **non riprodotta** |
| SRC-011 | [Segni grafici nella rappresentazione dei componenti — CT Energia](https://www.ctenergia.it/wp-content/uploads/downloads/2014/04/00-Lez.-cap.-1-segni-grafici-nella-rappr.-componenti.pdf) | Materiale didattico sulla rappresentazione degli impianti fluidotermici | Acquisita il 4 agosto 2026 |
| SRC-012 | **Raccolta R, edizione 2009** — specificazioni tecniche applicative del Titolo II del D.M. 1.12.1975, ai sensi dell'art. 26. [Testo integrale commentato Caleffi](https://raccoltar.caleffi.it/pdf/raccolta_r_commentata_caleffi.pdf), [testo Raccolta R](https://raccoltar.caleffi.it/pdf/raccolta_r.pdf) | **Prescrizione normativa applicabile**, livello 1 della gerarchia §9.1: attua un decreto ministeriale. In vigore dal 1° marzo 2011 (circolare INAIL 1-IN/2010). Il cap. R.3.B.1 elenca i dispositivi obbligatori di un impianto a vaso chiuso; R.2.A i dispositivi di sicurezza e i loro dimensionamenti; R.3 le configurazioni di impianto | **Acquisita e letta il 4 agosto 2026**, 55 pagine. Liberamente accessibile |
| SRC-013 | **UNI 10412-1:2006** «Impianti di riscaldamento ad acqua calda — Requisiti di sicurezza — Parte 1: generatori alimentati da combustibili liquidi, gassosi, solidi polverizzati o **generatori di calore elettrici**» | Coprirebbe il caso di accettazione D-011, che è a **pompa di calore** e che la Raccolta R esclude | **Non acquistata, e non blocca.** Le regole di sicurezza per la pompa di calore restano su buona pratica documentata e manuali di prodotto, dichiarati come livello 2-3. Resta registrata qui come acquisto possibile, non come prerequisito |
| SRC-014 | **UNI 8065:2019** «Trattamento dell'acqua negli impianti termici ad uso civile», tramite guide di settore: [Guida Aqua Italia](https://www.atlasfiltriengineering.com/sites/default/files/news/files/Giuda%20Aqua%20Italia_UNI.8065.19_0.pdf) | Filtro di sicurezza, filtro dissabbiatore, condizionamento chimico, soglie di addolcimento. La norma è a pagamento; le guide ne riportano le prescrizioni con soglie puntuali | Guide **consultate il 4 agosto 2026**. Fonte **secondaria**: le regole che ne derivano citano la guida, non la norma |

## Cosa dicono i cataloghi dei produttori sugli attacchi, letto il 6 agosto 2026

Acquisite per rispondere a una domanda che era stata girata al PM e che invece aveva
risposta nei cataloghi: **quali attacchi ha davvero un accumulo, oltre a quelli del flusso
principale.** Il PM: «sono tutte domande che se cerchi nella tua memoria o cerchi in
cataloghi di produttori trovi tutto; io potrei sbagliare».

| ID | Fonte | Cosa dice | Stato |
|---|---|---|---|
| SRC-017 | [Cordivari — scheda tecnica PUFFER, termoaccumulatore per acqua di riscaldamento, 200÷5000 l](https://www.cordivari.it/wp-content/uploads/2023/10/IT-Cordivari_TEC-Scheda-PUFFER_06.2024.pdf) | Legenda degli attacchi: **A** mandata riscaldamento/dal generatore, **B** connessione per strumentazione G½" F, **C** ritorno riscaldamento/al generatore, **I** connessione per integrazione elettrica, **O** scarico *solo* per i modelli 3000 e 5000. Le A e le C sono **piu' di quattro** e stanno a quote diverse: si sceglie quali usare | Acquisita e letta il 6 agosto 2026 |
| SRC-019 | [Caleffi — *Idraulica 61*, «Gli impianti a pompa di calore aria-acqua»](https://www.caleffi.com/sites/default/files/media/external-file/Idraulica_61_IT_Gli%20impianti%20a%20pompa%20di%20calore%20aria-acqua.pdf), 56 pagine | Le regole di posizionamento che la norma non copre. Testuale: «La presenza di un dispositivo di disaerazione e' **obbligatoria in ciascun circuito chiuso**. Occorre installare **a valle della pompa di calore** un disaeratore e **non e' sufficiente una valvola sfogo aria**, ad eccezione di impianti con contenuto d'acqua inferiore ai 300 litri». E per le impurita': «e' opportuno installare un filtro defangatore **sulla linea di ritorno verso il generatore**», esterno alla macchina perche' quello interno, sporcandosi, strozza la portata. Piu' le tre configurazioni dell'accumulo inerziale — separatore idraulico a quattro tubi, in linea sul ritorno, versione a tre tubi — ciascuna con i propri vantaggi dichiarati. **Lo schema tipico (Fig. 41)** disegna: il corredo su un collettore portastrumenti (sicurezza, sfogo, manometro, vaso appeso) sul tratto comune della **mandata** in uscita macchina; **un solo** defangatore sul ritorno generale, ultimo prima della macchina; il caricamento innestato sul ritorno; lo sfogo aria sull'attacco superiore di ogni serbatoio; nessun termometro aggiunto sul primario. Sui pezzi di bordo macchina: monoblocco «**possono** essere integrati... circolatore, flussostato, vaso, sfogo aria e sicurezza» (p. 15), split li ha di serie (p. 16); «solitamente le pompe di calore contengono un vaso di espansione» da 6–8 litri, se non basta se ne installa uno aggiuntivo (pp. 50–51) | Acquisita e letta il 6 agosto 2026; **riscontro D-106 il 7 agosto 2026** (Fig. 41 e capitoli Componenti, pp. 41–51) |
| SRC-018 | [Rehau — manuale accumuli e bollitori](https://www.rehau.com/downloads/495810/manuale-accumuli-bollitori.pdf), 44 pagine | Tre legende complete. **T-Puffer** (acqua tecnica): 1 sfiato · 2 mandata caldaia · 3 mandata riscaldamento · 4 ritorno caldaia-riscaldamento · 5 resistenza elettrica · 6 termometro · 7 sonda · 8 scarico. **ACS Puffer** (bollitore a serpentino): 1 e 11 mandata acqua calda · 2 anodo · 3 termometro-sonda · 4 resistenza elettrica · 5 attacco bancale cieco · 6 entrata acqua fredda · 7 ritorno serpentino · 8 sonda · 9 **ricircolo** · 10 mandata serpentino. **Taddy** (accumulo con serpentino sanitario): sfiato, mandate e ritorni di caldaia, riscaldamento, solare e ausiliaria, termometro, sonda, resistenza. Le istruzioni d'installazione di **ogni** bollitore prescrivono che l'installazione preveda valvola di sicurezza e vaso di espansione: non sono attacchi del serbatoio | Acquisita e letta il 6 agosto 2026 |

**Le tre cose che ne discendono, e che nessuno di noi due aveva esatte.**

- **Il volano ha sfiato, scarico e attacchi per la strumentazione**, e li dichiara in
  legenda: il PM aveva ragione su sonde, sfiato e scarico. Cordivari il drenaggio lo mette
  solo sui modelli grandissimi, Rehau su tutti — quindi e' un fatto del modello, non della
  famiglia, ed e' giusto che lo dichiari la voce di catalogo.
- **Nessuno dei due dichiara un attacco per il vaso di espansione o per la ricarica.** La
  domanda che avevo girato al PM — «ci metto anche l'attacco del vaso?» — ha risposta no:
  vaso e riempimento stanno **sulla tubazione**, con una derivazione.
- **Il bollitore non ha lo scarico**, e non ha ne' l'attacco della sicurezza ne' quello del
  vaso: il manuale dice a chiare lettere che li deve prevedere l'installazione. Ha invece
  il **ricircolo**, che il nostro catalogo non contempla. Svuotare un bollitore si fa
  dall'ingresso dell'acqua fredda, con una derivazione — non da un bocchello dedicato.

Ne discende la regola generale, che vale per qualunque macchina: **l'accessorio va
sull'attacco dedicato quando la macchina ce l'ha, e su una derivazione della tubazione
quando non ce l'ha.** Tutti e due i casi sono reali e documentati, e quale dei due si
applichi lo dice il catalogo, non il programma.

## Le fonti degli accessori di linea, lette il 6 agosto 2026

Acquisite per chiudere le cinque righe della coda di `DOVE_VA_CIASCUN_ACCESSORIO.md`
(bilanciamento, disconnettore, miscelatrice, contabilizzatore, ritegno). Tutte
documentazione tecnica Caleffi liberamente accessibile, aperta e letta per intero: fonti di
**posizione**, mai di quantità (D-104). Ora vivono nelle sezioni 14-18 di quel documento.

| ID | Fonte | Cosa dice | Stato |
|---|---|---|---|
| SRC-020 | [Caleffi — dispensa tecnica *Il bilanciamento dinamico dei circuiti idronici — lo stabilizzatore automatico di portata AUTOFLOW*](https://www.caleffi.com/sites/default/files/media/external-file/04011_IL%20BILANCIAMENTO%20DEI%20CIRCUITI%20IDRONICI_IT.pdf), 3ª ed. aprile 2003, 62 pp. | Testuale, ripetuto per ogni configurazione applicativa (piede di colonna, ogni terminale, derivazioni di zona, batterie, sottocentrali di teleriscaldamento): «I dispositivi Autoflow **vanno installati sulla tubazione di ritorno del circuito**». Negli schemi degli impianti bilanciati con valvole manuali, la **valvola di bilanciamento sta sul ritorno di ogni derivato** e la valvola di regolazione sulla mandata | Acquisita e letta il 6 agosto 2026 |
| SRC-021 | [Caleffi — scheda H0009761.01, contatore di calore diretto compatto serie CAL1913.](https://www.caleffi.com/sites/default/files/media/external-file/H0009761_IT.pdf), 12 pp. | Testuale: «Il corretto posizionamento del contatore è **sulla tubazione di ritorno**, mentre la valvola sfera con pozzetto della sonda deve essere **sulla mandata** dell'impianto». «Prima e dopo il contatore devono essere previste **valvole a sfera di intercettazione**»; «verificare la presenza di un **filtro a monte**». Sonda di andata lunga 1,5 m, «non allungabile o accorciabile». L'inosservanza «può pregiudicare la validazione della garanzia» | Acquisita e letta il 6 agosto 2026 |
| SRC-022 | [Caleffi — dp 01125/11, gruppi di riempimento e caricamento serie 554-574](https://www.caleffi.com/sites/default/files/media/external-file/01125_IT.pdf), 4 pp. | Il gruppo di riempimento è «composto da un riduttore di pressione a sede compensata, un filtro in entrata, una **valvola di intercettazione a monte con ritegno incorporato** ed una valvola di intercettazione a valle» e «va installato **sulla tubazione di adduzione dell'acqua**». Il gruppo di caricamento 574001 aggiunge **disconnettore BA e filtro a Y fra la rete e il riduttore**, manometro a valle, imbuto di scarico collegato alla tubazione di scarico; solo orizzontale | Acquisita e letta il 6 agosto 2026 |
| SRC-023 | [Caleffi — dp 01022/25, disconnettore a zona di pressione ridotta tipo BA, serie 574-575-570](https://www.caleffi.com/sites/default/files/media/external-file/01022_IT.pdf) | Testuale: «Il disconnettore va installato **dopo una valvola di intercettazione a monte ed un filtro ispezionabile** con scarico; **a valle va montata un'altra valvola di intercettazione**»; «in una zona accessibile», non allagabile; «orizzontalmente»; imbuto EN 1717 «collegato alla tubazione di collegamento alla **fognatura**». E la posizione nella rete: «Per la protezione della rete pubblica il disconnettore va installato **dopo il contatore dell'acqua**, mentre per la protezione delle erogazioni ad uso sanitario nella rete interna si installa **al limite delle zone nelle quali si può verificare un inquinamento** ad esempio: riscaldamenti centralizzati» | Acquisita e letta il 6 agosto 2026 |
| SRC-024 | [Caleffi — istruzioni 28286, disconnettore tipo BA con geometria multifunzione serie 580](https://www.caleffi.com/sites/default/files/media/external-file/28286.pdf), 24 pp. | Conferma la sequenza di montaggio numerata: intercettazione a monte — filtro — disconnettore — intercettazione a valle, con filtro a Y obbligatorio secondo EN 1717. Imbuto di scarico «orientato verso il basso e collegato alla tubazione di convogliamento alla fognatura»; zona accessibile, non allagabile, non a rischio gelo; ammessa anche l'installazione su tubo verticale **solo con flusso discendente** | Acquisita e letta il 6 agosto 2026 |
| SRC-025 | [Caleffi — dp 01050/21, miscelatori termostatici anticalcare regolabili serie 521](https://www.caleffi.com/sites/default/files/media/external-file/01050_IT.pdf) | Vie marcate sul corpo: ingressi caldo e freddo, «uscita acqua miscelata con scritta “MIX”». Testuale: «Negli impianti con miscelatori termostatici **occorre inserire le valvole di ritegno** per evitare indesiderati ritorni di fluido»; filtri consigliati all'ingresso. Schemi applicativi con bollitore: miscelatore **sull'uscita calda del bollitore** dopo l'intercettazione, fredda da una **derivazione della stessa adduzione** che alimenta il bollitore, miscelata alla distribuzione, ricircolo sull'**attacco dedicato del bollitore** | Acquisita e letta il 6 agosto 2026 |
| SRC-026 | [Caleffi — dp 01019/15, gruppi di sicurezza per scaldacqua ad accumulo serie 5261, EN 1487](https://www.caleffi.com/sites/default/files/media/external-file/01019_IT.pdf), 2 pp. | Componenti e ordine, dal disegno quotato: **entrata acqua fredda → rubinetto di intercettazione → valvola di ritegno tipo EA controllabile → ingresso scaldacqua**, con la valvola di sicurezza e il sifone di scarico **a valle del ritegno**, lato scaldacqua. Funzione dichiarata del ritegno: «antinquinamento, per evitare il ritorno dell'acqua calda nella rete di alimentazione dell'acqua fredda» | Acquisita e letta il 6 agosto 2026 |

**Due tentativi a vuoto, registrati perché nessuno li ripeta.** La scheda del contatore
CONTECA (dp 01111) sul sito Caleffi risponde 403 e non è stata letta: **non si cita**; la
posizione del contabilizzatore è comunque coperta da SRC-021. Un quaderno «Idraulica»
dedicato alla sola contabilizzazione non è stato trovato liberamente accessibile: non si
cita. Le frasi di obbligo presenti in queste schede («la cui installazione è resa
obbligatoria», «rende obbligatorio l'impiego del miscelatore») **non sono entrate** nel
documento degli accessori: dicono che cosa deve avere l'impianto, e quello non è materiale
nostro (D-104).

## Cosa dicono le tavole di SRC-016, letto il 5 agosto 2026

Quattro cose utili subito, che nessun'altra fonte del registro dava con questa precisione.

- **Incrocio e derivazione si distinguono per il pallino, non per lo scavallo.** Tab. 1:
  «incrocio di tubazioni o canalizzazioni **senza** connessione» è una croce semplice;
  «incrocio **con** connessione» e «derivazione» portano un **cerchio pieno di diametro pari
  a quattro volte lo spessore del tratto». La norma disambigua marcando il collegamento; la
  pratica CAD, e lo schizzo del PM, disambiguano marcando l'incrocio con lo scavallo. Le due
  cose non si escludono: farle entrambe toglie ogni ambiguità e non costa nulla (D-079).
- **Gli spessori hanno valori normati.** Tab. 1: tubazione **di progetto 0,50 mm**, tubazione
  **esistente 0,25 mm**; tutti i segni grafici sono tracciati a 0,50 mm salvo dove la
  descrizione dice altro. Oggi `A3_LANDSCAPE` usa 0,18 / 0,35 / 0,50 scelti internamente.
- **La valvola di ritegno è una «z coricata», non un triangolo.** Tab. 3, «valvola di non
  ritorno»: **due barrette verticali unite da una diagonale** che scende dall'alto della
  prima al basso della seconda, **con una freccia sopra**; la descrizione della norma dice
  testualmente «la freccia indica il senso del flusso». ⛔ **Questa riga il 5 agosto diceva
  «triangolo vuoto contro la battuta»: era sbagliata**, e il simbolo è rimasto sbagliato
  per quattro giorni, fino alla prima tavola vista dal PM. La tavola è un'immagine
  pubblicata: è stata riletta **guardandola**, il 9 agosto. **Chiusa**: il simbolo ora è
  quello della norma (`I-004` nel registro degli input del PM).
- **Le tavole non coprono le macchine.** Tubazioni, giunzioni, valvolame, scarichi, sonde e
  strumenti sì; pompa di calore, bollitore, volano, circolatore e collettore no. Quelli
  vengono dalla pratica e dagli schemi dei produttori (SRC-008), ed è esattamente il «mix»
  che il PM descrive: un po' norma italiana, un po' forme ereditate dall'area ASHRAE.

## Convenzioni grafiche interne

Le fonti esterne sopra non sono ancora state tradotte in simboli, quindi **nessun simbolo della
libreria ne deriva**. I simboli seguono forme schematiche di pratica comune, codificate come
convenzione interna del progetto e citate nel campo `source` di ogni manifesto.

| ID | Ambito | Definita in | Stato |
|---|---|---|---|
| CONV-GRAFICA-001 | Forma e geometria di un simbolo singolo: dimensioni in millimetri di carta, porte sul perimetro con faccia coerente, area di rispetto sulle facce con porta, orientamenti tecnicamente ammessi | `docs/standard/GRAPHIC_STANDARD.md` | **Ritirata come fonte di forma il 5 agosto 2026** (D-081, D-082): nessun simbolo pubblicato la cita più — le forme vengono da UNI 9511 (SRC-015/016) e dalla pratica di settore (SRC-008). Restano valide le sole regole *meccaniche* (porte sul perimetro, aree di rispetto), che ora vivono nei vincoli del manifesto. La citano solo le fixture di test |
| CONV-GRAFICA-002 | Composizione di un simbolo composito da primitive, pubblicato e contato come prodotto unico | `docs/standard/GRAPHIC_STANDARD.md` §6 | Definita, nessun composito ancora pubblicato |
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
