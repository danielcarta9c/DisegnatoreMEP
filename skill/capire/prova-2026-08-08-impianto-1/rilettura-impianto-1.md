# Tabella di rilettura — Esempio 1

Due pompe di calore in parallelo con accumulo combinato.
Grafo: `grafo-impianto-1.json` · Commessa PROVA-01 · Committente Nove C.

## Parte 1 — Dal testo al grafo: una riga per frase

| # | Frase del testo | Cosa la rappresenta nel grafo | Assunzioni che la coprono |
|---|---|---|---|
| T | «Esempio 1 – Due pompe di calore in parallelo con accumulo combinato» (titolo) | `metadata.project_name`, `metadata.project_id` | — |
| F1a | «L'impianto è composto da due pompe di calore aria-acqua da 12 kW ciascuna…» | componenti `pdc-1` e `pdc-2` (voce di catalogo `heat-pump-air-water`), con `tipo: "aria-acqua"` e `potenza: "12 kW"` trascritte nelle proprietà di entrambe | — (la potenza è scritta dall'ingegnere: non si chiede) |
| F1b | «…da 12 kW ciascuna…» → regime della centrale | `plant_regime: "up_to_35_kw"` — 12 + 12 = 24 kW, sotto la soglia dei 35 kW. Sono le uniche due macchine che generano calore | — |
| F1c | «…installate in parallelo…» | rete `circuito-generatori`; confluenza `rc-mandata-generatori` (raccordo a T) sulle due mandate e ripartizione `rip-ritorno-generatori` (ripartizione a T) sui due ritorni; tubazioni `mand-pdc1-raccordo`, `mand-pdc2-raccordo`, `rit-ripartizione-pdc1`, `rit-ripartizione-pdc2` | **a1** — il testo dice «in parallelo» ma non con che pezzo i flussi si uniscono |
| F1d | «…e gestite una come master e una come slave.» | nessun nodo e nessuna tubazione: è regolazione. Il ruolo è trascritto come `gestione: "master"` su `pdc-1` e `gestione: "slave"` su `pdc-2` | **a2** — master/slave è logica di regolazione, sul grafo non si vede |
| F1e | (implicito in F1: come circola l'acqua fra le pompe e l'accumulo) | nessun circolatore disegnato sul circuito dei generatori: la voce di catalogo scelta lo porta a bordo | **a3** — il testo non dice se serva un circolatore separato sul primario |
| F2a | «Le due macchine alimentano un accumulo ECOcombi da 200 litri…» | componente `accumulo-combinato` (voce `buffer-combined`), con `modello: "ECOcombi"` e `volume: "200 litri"`; tubazione `mand-raccordo-accumulo` dalla confluenza all'attacco `primary_in` | — |
| F2b | «…utilizzato sia come volume tecnico a quattro tubi per il riscaldamento…» | i quattro attacchi di riscaldamento della voce scelta: `primary_in` / `primary_out` verso i generatori, `secondary_out` / `secondary_in` verso il circuito secondario; proprietà `configurazione: "a quattro tubi"`. Il ritorno al circuito dei generatori è la tubazione `rit-accumulo-ripartizione` (da `primary_out` alla ripartizione) | — (il ritorno di un circuito chiuso è trascrizione, non invenzione) |
| F2c | «…sia per la produzione istantanea di acqua calda sanitaria tramite serpentino interno.» | gli attacchi sanitari della stessa voce: `cold_in` (acqua fredda) e `dhw_out` (acqua calda sanitaria); proprietà `produzione_sanitaria: "istantanea tramite serpentino interno"` | **a4** — il serpentino è interno all'accumulo, non è un pezzo a sé |
| F3a | «Sul lato riscaldamento, dal volume tecnico parte un circuito secondario…» | rete `circuito-secondario` (acqua di riscaldamento), che nasce dall'attacco `secondary_out` dell'accumulo | — |
| F3b | «…con circolatore dedicato…» | componente `circolatore-secondario` (voce `pump-circulator`); tubazioni `sec-accumulo-circolatore` e `sec-circolatore-radiatori` | **a5** — il testo non dice se il circolatore stia sulla mandata o sul ritorno |
| F3c | «…che alimenta direttamente l'impianto esistente a radiatori.» | componente `radiatori` (voce `radiator`), con `stato: "esistente"`; tubazione di mandata `sec-circolatore-radiatori` e tubazione di ritorno `sec-radiatori-accumulo` verso l'attacco `secondary_in`. «Direttamente» = nessun pezzo interposto fra il circolatore e i radiatori | **a6** — quanti sono i radiatori: ne è disegnato uno rappresentativo |
| F4a | «Sul lato sanitario, l'acqua fredda di acquedotto entra nel serpentino interno…» | componente di confine `acquedotto` (voce `cold-water-inlet`); rete `acqua-fredda`; tubazione `san-acquedotto-accumulo` verso l'attacco `cold_in` dell'accumulo | — |
| F4b | «…e l'ACS viene prelevata in uscita.» | rete `acqua-calda-sanitaria`; tubazione `san-accumulo-utenze` dall'attacco `dhw_out` al confine `utenze-sanitarie` (voce `dhw-draw-off`) | — |
| F5 | «Non è previsto ricircolo sanitario.» | nessun elemento del grafo, ed è corretto così: è un'esclusione dichiarata | **a7** — il ricircolo è escluso dall'ingegnere, non perso |
| F6 | «Sul volume tecnico sono previsti anche il collegamento per il carico automatico dell'impianto da acquedotto e lo scarico.» | nessun elemento del grafo: sono accessori di servizio (riempimento e scarico), che aggiunge il passo successivo. Gli attacchi di servizio `vent`, `drain` e `probe` dell'accumulo restano liberi apposta, per riceverli | **a8** — la richiesta è registrata perché non vada persa |

## Parte 2 — Dal grafo al testo: nessun elemento in più

Ogni elemento del grafo, e la frase da cui nasce.

### Componenti (9)

| Id | Voce di catalogo | Frase |
|---|---|---|
| `pdc-1` | `heat-pump-air-water` | F1a |
| `pdc-2` | `heat-pump-air-water` | F1a |
| `rc-mandata-generatori` | `tee-junction` | F1c (+ a1) |
| `rip-ritorno-generatori` | `tee-split` | F1c (+ a1) |
| `accumulo-combinato` | `buffer-combined` | F2a, F2b, F2c |
| `circolatore-secondario` | `pump-circulator` | F3b |
| `radiatori` | `radiator` | F3c |
| `acquedotto` | `cold-water-inlet` | F4a |
| `utenze-sanitarie` | `dhw-draw-off` | F4b |

### Reti (4)

| Id | Fluido | Frase |
|---|---|---|
| `circuito-generatori` | `heating_water` | F1c, F2a |
| `circuito-secondario` | `heating_water` | F3a |
| `acqua-fredda` | `cold_water` | F4a |
| `acqua-calda-sanitaria` | `domestic_hot_water` | F4b |

### Tubazioni (11)

| Id | Da → a | Frase |
|---|---|---|
| `mand-pdc1-raccordo` | `pdc-1.water_supply` → `rc-mandata-generatori.a` | F1c |
| `mand-pdc2-raccordo` | `pdc-2.water_supply` → `rc-mandata-generatori.c` | F1c |
| `mand-raccordo-accumulo` | `rc-mandata-generatori.b` → `accumulo-combinato.primary_in` | F2a |
| `rit-accumulo-ripartizione` | `accumulo-combinato.primary_out` → `rip-ritorno-generatori.a` | F2b |
| `rit-ripartizione-pdc1` | `rip-ritorno-generatori.b` → `pdc-1.water_return` | F1c |
| `rit-ripartizione-pdc2` | `rip-ritorno-generatori.c` → `pdc-2.water_return` | F1c |
| `sec-accumulo-circolatore` | `accumulo-combinato.secondary_out` → `circolatore-secondario.a` | F3a, F3b |
| `sec-circolatore-radiatori` | `circolatore-secondario.b` → `radiatori.in` | F3c |
| `sec-radiatori-accumulo` | `radiatori.out` → `accumulo-combinato.secondary_in` | F3c |
| `san-acquedotto-accumulo` | `acquedotto.a` → `accumulo-combinato.cold_in` | F4a |
| `san-accumulo-utenze` | `accumulo-combinato.dhw_out` → `utenze-sanitarie.a` | F4b |

### Altri campi

| Campo | Frase |
|---|---|
| `plant_regime: "up_to_35_kw"` | F1b (ricavato da 12 + 12 = 24 kW) |
| `metadata` | dati di commessa forniti da chi ha lanciato il lavoro + titolo dell'esempio |
| `subsystems`, `rule_applications`, `sheets` | liste vuote: appartengono ai passi successivi |

## Parte 3 — Controlli passati

- Il file carica con lo strumento di validazione.
- Tutti i `definition_id` esistono nel catalogo; nessuno ha un mestiere della lista «ferramenta».
- Ogni attacco usato esiste nel catalogo del suo pezzo; nessun attacco porta due tubazioni;
  nessuna tubazione tocca un attacco di servizio (`vent`, `drain`, `probe` dell'accumulo restano liberi).
- Ogni tubazione va da un attacco di uscita a un attacco di ingresso, sullo stesso fluido della rete.
- Tutti gli attacchi obbligatori delle macchine scelte sono collegati.
- Tutti i `tag` sono nulli: l'ingegnere non ha scritto sigle.
- `subsystems`, `rule_applications` e `sheets` sono liste vuote.
