# Tabella di rilettura — Esempio 1, due pompe di calore in parallelo con accumulo combinato

Il controllo va fatto nei due versi (§8, passo 6): **ogni frase del testo** è rappresentata
nel grafo o coperta da un'assunzione, e **ogni elemento del grafo** risale a una frase precisa.
Perciò le tabelle sono due.

---

## A. Dal testo al grafo — una riga per frase

| # | Frase del testo | Cosa la rappresenta nel grafo | Assunzioni che la coprono |
|---|---|---|---|
| F0 | *(titolo)* «Due pompe di calore in parallelo con accumulo combinato» | `metadata.project_name`, `metadata.project_id` | — |
| F1a | «L'impianto è composto da due pompe di calore aria-acqua da 12 kW ciascuna…» | componenti `pdc-1`, `pdc-2` (`heat-pump-air-water`), con `properties` `potenza: "12 kW"` e `tipo: "aria-acqua"`; rete `primario`; `plant_regime: "up_to_35_kw"` (12 + 12 = 24 kW ≤ 35) | a10 (quale potenza è stata sommata) |
| F1b | «…installate in parallelo…» | `rc-mandata-generatori` (`tee-junction`) e `rip-ritorno-generatori` (`tee-split`); tubazioni `pri-pdc1-raccordo`, `pri-pdc2-raccordo`, `pri-raccordo-accumulo`, `pri-accumulo-ripartizione`, `pri-ripartizione-pdc1`, `pri-ripartizione-pdc2` (due tubazioni che si incontrano = un raccordo, §4.4) | a1 (il testo non dice con che pezzo) |
| F1c | «…e gestite una come master e una come slave.» | **niente**: è regolazione, non topologia | a2 (logica di regolazione; e il testo non dice quale sia la master) |
| F2a | «Le due macchine alimentano un accumulo ECOcombi da 200 litri…» | componente `accumulo` (`buffer-combined`), `properties` `modello: "ECOcombi"`, `volume: "200 litri"`; tubazioni `pri-raccordo-accumulo` (mandata) e `pri-accumulo-ripartizione` (ritorno) sugli attacchi `primary_in` / `primary_out` | a3 (circolatori primari: si è seguito il catalogo, che li porta a bordo) |
| F2b | «…utilizzato sia come volume tecnico a quattro tubi per il riscaldamento…» | i quattro attacchi di riscaldamento dell'accumulo: `primary_in`, `primary_out` (primario) e `secondary_out`, `secondary_in` (secondario); `properties` `configurazione: "a quattro tubi"` | — |
| F2c | «…sia per la produzione istantanea di acqua calda sanitaria tramite serpentino interno.» | gli attacchi sanitari dello stesso accumulo: `cold_in` e `dhw_out`; `properties` `produzione_acs: "istantanea tramite serpentino interno"`. La voce di catalogo scelta accumula acqua di riscaldamento (`stored_medium: heating_water`) e fa passare l'acqua sanitaria nel serpentino | a6 (come il serpentino è rappresentato) |
| F3a | «Sul lato riscaldamento, dal volume tecnico parte un circuito secondario…» | rete `secondario` (`heating_water`), che nasce dall'accumulo — la macchina che la alimenta (§4.2) | — |
| F3b | «…con circolatore dedicato…» | componente `circolatore-secondario` (`pump-circulator`); tubazioni `sec-accumulo-circolatore`, `sec-circolatore-radiatori` | a4 (messo sulla mandata per convenzione: il testo non dice su quale ramo) |
| F3c | «…che alimenta direttamente l'impianto esistente a radiatori.» | componente `radiatori` (`radiator`, `stato: "esistente"`); tubazioni `sec-circolatore-radiatori` (mandata) e `sec-radiatori-accumulo` (ritorno: un circuito chiuso si chiude, §4.3). «Direttamente» = nessun pezzo interposto fra circolatore e terminali | a5 (quanti radiatori: se n'è disegnato uno rappresentativo) |
| F4a | «Sul lato sanitario, l'acqua fredda di acquedotto entra nel serpentino interno…» | rete `acqua-fredda` (`cold_water`); componente `acquedotto` (`cold-water-inlet`, mestiere `boundary`); tubazione `fre-acquedotto-serpentino` verso `accumulo.cold_in` | a6 |
| F4b | «…e l'ACS viene prelevata in uscita.» | rete `acs` (`domestic_hot_water`) — il fluido cambia attraversando il serpentino, quindi la rete cambia (§4.2); componente `utenze-sanitarie` (`dhw-draw-off`, mestiere `boundary`); tubazione `acs-serpentino-utenze` da `accumulo.dhw_out` | a9 (le utenze non sono descritte: un confine solo, rappresentativo) |
| F5 | «Non è previsto ricircolo sanitario.» | **niente**: è un'esclusione esplicita, e il grafo non mostra ciò che non c'è | a7 (l'esclusione è registrata perché nessuno lo riaggiunga) |
| F6 | «Sul volume tecnico sono previsti anche il collegamento per il carico automatico dell'impianto da acquedotto e lo scarico.» | **niente**: carico e scarico sono ferramenta di servizio (`filling`, `drain`), che il pezzo successivo della catena aggiunge (§5). Gli attacchi di servizio dell'accumulo (`vent`, `drain`, `probe`) restano liberi apposta | a8 (la nomina non è persa; e il ramo di acquedotto verso il carico non è disegnato) |

---

## B. Dal grafo al testo — nessun elemento senza una frase dietro

### Componenti (9)

| id | voce di catalogo | frase |
|---|---|---|
| `pdc-1` | `heat-pump-air-water` | F1a |
| `pdc-2` | `heat-pump-air-water` | F1a |
| `rc-mandata-generatori` | `tee-junction` | F1b (raccordo imposto dal «in parallelo», §4.4 — a1) |
| `rip-ritorno-generatori` | `tee-split` | F1b (idem) |
| `accumulo` | `buffer-combined` | F2a, F2b, F2c |
| `circolatore-secondario` | `pump-circulator` | F3b |
| `radiatori` | `radiator` | F3c |
| `acquedotto` | `cold-water-inlet` | F4a |
| `utenze-sanitarie` | `dhw-draw-off` | F4b (a9) |

### Reti (4)

| id | fluido | frase |
|---|---|---|
| `primario` | `heating_water` | F1a + F2a — il circuito dei generatori, che nasce dalle pompe di calore |
| `secondario` | `heating_water` | F3a — «dal volume tecnico parte un circuito secondario», che nasce dall'accumulo |
| `acqua-fredda` | `cold_water` | F4a — nasce dal confine dell'acquedotto |
| `acs` | `domestic_hot_water` | F4b — nasce dall'uscita sanitaria dell'accumulo |

### Tubazioni (11)

| id | da → a | rete | frase |
|---|---|---|---|
| `pri-pdc1-raccordo` | `pdc-1.water_supply` → `rc-mandata-generatori.a` | `primario` | F1b |
| `pri-pdc2-raccordo` | `pdc-2.water_supply` → `rc-mandata-generatori.c` | `primario` | F1b |
| `pri-raccordo-accumulo` | `rc-mandata-generatori.b` → `accumulo.primary_in` | `primario` | F1b + F2a |
| `pri-accumulo-ripartizione` | `accumulo.primary_out` → `rip-ritorno-generatori.a` | `primario` | F2a (il ritorno del primario) |
| `pri-ripartizione-pdc1` | `rip-ritorno-generatori.b` → `pdc-1.water_return` | `primario` | F1b |
| `pri-ripartizione-pdc2` | `rip-ritorno-generatori.c` → `pdc-2.water_return` | `primario` | F1b |
| `sec-accumulo-circolatore` | `accumulo.secondary_out` → `circolatore-secondario.a` | `secondario` | F3a + F3b |
| `sec-circolatore-radiatori` | `circolatore-secondario.b` → `radiatori.in` | `secondario` | F3b + F3c |
| `sec-radiatori-accumulo` | `radiatori.out` → `accumulo.secondary_in` | `secondario` | F3c (il ritorno del circuito chiuso) |
| `fre-acquedotto-serpentino` | `acquedotto.a` → `accumulo.cold_in` | `acqua-fredda` | F4a |
| `acs-serpentino-utenze` | `accumulo.dhw_out` → `utenze-sanitarie.a` | `acs` | F4b |

### Assunzioni (10)

| id | frase da cui nasce |
|---|---|
| a1 | F1b |
| a2 | F1c |
| a3 | F2a |
| a4 | F3b |
| a5 | F3c |
| a6 | F2c, F4a |
| a7 | F5 |
| a8 | F6 |
| a9 | F4b |
| a10 | F1a |

---

## C. Controlli di chiusura (§9)

| Controllo | Esito |
|---|---|
| Il JSON carica con lo strumento di validazione | sì, nessun output |
| Ogni `definition_id` esiste in catalogo, nessuno è ferramenta (§5) | sì — mestieri usati: `heat_generation`, `hydraulic_separation` + `thermal_storage`, `circulation`, `emission`, `junction`, `boundary` |
| Ogni attacco esiste, nessun attacco porta due tubazioni, nessuna tubazione tocca uno `stub` | sì — gli stub `vent`, `drain`, `probe` dell'accumulo restano liberi |
| Ogni tubazione va da `out` a `in`, sullo stesso fluido della sua rete | sì |
| Ogni attacco `required: true` è collegato | sì — compresi `cold_in` e `dhw_out` dell'accumulo |
| I `tag` sono tutti `null` | sì — l'ingegnere non ha scritto nessuna sigla («ECOcombi» è un nome commerciale, ed è in `properties`) |
| `subsystems`, `rule_applications`, `sheets` vuoti | sì |
