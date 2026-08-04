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
| SRC-007 | UNI 9511 (4 parti), «Disegni tecnici. Rappresentazione delle installazioni» | **La** simbologia italiana degli impianti civili: riscaldamento, condizionamento, idrosanitario, gas. È la norma che un termotecnico italiano si aspetta, ed è quella che mancava | **Da acquistare.** Decisione di prodotto: la norma è a pagamento |
| SRC-008 | [Caleffi — Quaderni e Tabelle](https://www.caleffi.com/it-it/formazione/quaderni-e-tabelle); [Componenti e schemi per impianti a pompa di calore aria-acqua](https://www.caleffi.com/sites/default/files/media/external-file/25%20-%20Componenti%20e%20schemi%20per%20impianti%20a%20pompa%20di%20calore%20aria-acqua.pdf) | Casi di studio e prescrizioni di prodotto (D-015). Distinguono separatore idraulico, compensatore e accumulo inerziale, che il nostro `buffer-four-port` confonde | Consultata il 4 agosto 2026 |
| SRC-009 | [Schema funzionale centrale termica — Condominio Tower House, Treviso, Divisione Energia srl](https://www.divisionenergia.it/wp-content/uploads/2025/02/Cond.TH_schema-ct-as-built.pdf) | Caso di studio di tavola reale: legenda tubazioni, composizione a corsie, diametri sulle linee, sigle funzionali, tabelle. Documento pubblico | Letta e misurata il 4 agosto 2026, **non riprodotta** |
| SRC-010 | [Schema funzionale centrale termica — Liceo «G. Ballardini», Provincia di Ravenna](https://presadmin.provincia.ra.it/content/download/88849/1115730/file/SM04%20-%20BALLARDINI%20Stato%20Modificato%20Schema%20funzionale%20Centrale%20Termica.pdf) | Caso di studio: legenda colori tubazioni con mandata e ritorno distinti, sigle, tabella caratteristiche pompe. Documento pubblico di gara | Letta il 4 agosto 2026, **non riprodotta** |
| SRC-011 | [Segni grafici nella rappresentazione dei componenti — CT Energia](https://www.ctenergia.it/wp-content/uploads/downloads/2014/04/00-Lez.-cap.-1-segni-grafici-nella-rappr.-componenti.pdf) | Materiale didattico sulla rappresentazione degli impianti fluidotermici | Acquisita il 4 agosto 2026 |

## Convenzioni grafiche interne

Le fonti esterne sopra non sono ancora state acquisite, quindi **nessun simbolo della libreria
ne deriva**. I simboli seguono forme schematiche di pratica comune, codificate come convenzione
interna del progetto e citate nel campo `source` di ogni manifesto.

| ID | Ambito | Definita in | Stato |
|---|---|---|---|
| CONV-GRAFICA-001 | Forma e geometria di un simbolo singolo: dimensioni in millimetri di carta, porte sul perimetro con faccia coerente, area di rispetto sulle facce con porta, orientamenti tecnicamente ammessi | `docs/GRAPHIC_STANDARD.md` | In uso: la citano i dodici simboli pubblicati e gli otto di fixture |
| CONV-GRAFICA-002 | Composizione di un simbolo composito da primitive, pubblicato e contato come prodotto unico | `docs/GRAPHIC_STANDARD.md` §6 | Definita, nessun composito ancora pubblicato |
| CONV-GRAFICA-003 | Squadratura e impaginazione del foglio: margini, banda del cartiglio, fascia d'intestazione, area di disegno | `assets/cartigli/Cartiglio_NoveC_A3.pdf`, misurato | Da applicare al Task 4 del piano di layout |

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

## Regole di utilizzo

- Registrare edizione, data di consultazione, ambito e licenza.
- Separare prescrizioni normative, buona pratica e convenzioni grafiche.
- Non copiare integralmente contenuti protetti: estrarre regole motivate e riferimenti puntuali.
- Verificare la pertinenza italiana/europea prima di promuovere una fonte a base normativa.
- Associare ogni regola implementata ad almeno una fonte o a una convenzione interna esplicitamente approvata.
- Trattare gli schemi dei produttori come casi di studio e prescrizioni di prodotto, non come standard universali.
