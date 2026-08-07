# Tabella di rilettura — Esempio 3, pompa di calore diretta su pavimento radiante

Riferimento: `consegna/grafo.json` (schema 1.1.0, caricato senza errori con lo strumento di validazione).

## A. Dal testo al grafo — una riga per frase

| # | Frase del testo (o sua proposizione) | Elementi del grafo che la rappresentano | Voci di `assumptions` che la coprono |
|---|---|---|---|
| 1 | «L'impianto è composto da una pompa di calore aria-acqua da 8 kW…» | componente `pdc` (`heat-pump-air-water`), `properties.potenza = "8 kW"`, `properties.tipo = "aria-acqua"`; campo `plant_regime = "up_to_35_kw"` ricavato da questa potenza | `a8` |
| 2 | «…che alimenta direttamente un sistema radiante a pavimento a bassa temperatura.» | rete `riscaldamento` (`hydronic` / `heating_water`); tubazione `mandata-pdc-collettore`; componenti `circuito-radiante-1` e `circuito-radiante-2` (`underfloor-panel`, `properties.tipo = "sistema radiante a pavimento a bassa temperatura"`); l'anello si chiude con `ritorno-volano-pdc` su `pdc.water_return` | `a4` (per la parola «direttamente»: nessun pezzo interposto fra generatore e distribuzione) |
| 3 | «Non è previsto un separatore idraulico…» | **nessun elemento** — esclusione esplicita: il separatore non c'è. Ne è traccia anche la scelta del volano a due attacchi (`buffer-two-port`), l'unica voce di accumulo che *non* dichiara `hydraulic_separation` | `a4` |
| 4 | «…e la circolazione è affidata al circolatore integrato nella pompa di calore.» | **nessun componente circolatore**: la voce `heat-pump-air-water` dichiara `carries_on_board: ["circulation"]` | `a3` |
| 5 | «Sul ritorno dell'impianto radiante è installato un volume tecnico da 50 litri a due tubi, montato in serie…» | componente `volano` (`buffer-two-port`, `properties.volume = "50 litri"`, `properties.tipo = "volume tecnico a due tubi, montato in serie"`); tubazioni `ritorno-radiante-volano` (entra in `volano.a`) e `ritorno-volano-pdc` (esce da `volano.b` verso il ritorno della pompa di calore): è la serie, sul ritorno | `a2` (per il punto in cui i ritorni dei circuiti si riuniscono prima del volano) |
| 6 | «…con funzione di aumento del contenuto d'acqua e stabilizzazione del funzionamento della pompa di calore.» | `volano.properties.funzione`, trascritta come sta | — |
| 7 | «Sul volume tecnico sono previsti il collegamento per il carico automatico dell'impianto da acquedotto e lo scarico.» | **nessun elemento**: sono ferramenta di servizio (`filling`, `drain`), le mette il pezzo successivo della catena. La voce `buffer-two-port` porta gli attacchi di servizio `drain`, `vent`, `probe` — lasciati liberi apposta | `a5` |
| 8 | «Il collettore del pavimento radiante…» | componente `collettore-radiante` (`zone-manifold`), alimentato da `mandata-pdc-collettore` | — |
| 9 | «…alimenta più circuiti ambiente…» | tubazioni `mandata-circuito-1` e `mandata-circuito-2` (dalle due uscite del collettore); componenti `circuito-radiante-1` e `circuito-radiante-2`; ritorni `ritorno-circuito-1` e `ritorno-circuito-2` sul raccordo `raccordo-ritorno-radiante` (`tee-junction`) | `a1` (quanti sono davvero), `a2` (con che pezzo si riuniscono i ritorni) |
| 10 | «…con regolazione di zona.» | **nessun elemento**: è logica di regolazione, e le valvole di zona sono ferramenta | `a6` |
| 11 | «La produzione di ACS è completamente separata…» | due reti distinte da quella di riscaldamento: `acqua-fredda` (`cold_water`) e `acs` (`domestic_hot_water`); nessuna tubazione fra il boiler e la rete `riscaldamento` | `a7` |
| 12 | «…ed è realizzata con un boiler in pompa di calore dedicato da 200 litri…» | componente `boiler-acs` (`dhw-heat-pump`: dichiara insieme `heat_generation` e `dhw_storage` — produce l'acqua calda **da solo** e ne tiene la riserva), `properties.volume = "200 litri"`, `properties.tipo = "boiler in pompa di calore dedicato"` | `a7`, `a8` (la sua potenza non è data) |
| 13 | «…non collegato idraulicamente all'impianto di riscaldamento.» | **assenza** di qualunque tubazione fra `boiler-acs` e la rete `riscaldamento`; il sanitario è un circuito aperto chiuso sui confini: `acquedotto` (`cold-water-inlet`) → `acquedotto-boiler` → `boiler-acs.cold_in`, e `boiler-acs.dhw_out` → `boiler-utenze` → `utenze-acs` (`dhw-draw-off`) | `a7` |

## B. Dal grafo al testo — nessun elemento senza una frase dietro

### Componenti (9)

| Componente | Voce di catalogo | Frase (riga della tabella A) |
|---|---|---|
| `pdc` | `heat-pump-air-water` | 1, 2, 4 |
| `collettore-radiante` | `zone-manifold` | 8 |
| `circuito-radiante-1` | `underfloor-panel` | 2, 9 |
| `circuito-radiante-2` | `underfloor-panel` | 2, 9 (secondo circuito rappresentativo — `a1`) |
| `raccordo-ritorno-radiante` | `tee-junction` | 9 — raccordo imposto dalla topologia descritta (§4.4: due tubazioni in un punto = un raccordo), dichiarato in `a2` |
| `volano` | `buffer-two-port` | 5, 6 |
| `boiler-acs` | `dhw-heat-pump` | 12 |
| `acquedotto` | `cold-water-inlet` | 13 — confine di rete, dichiarato in `a7` |
| `utenze-acs` | `dhw-draw-off` | 13 — confine di rete, dichiarato in `a7` |

### Tubazioni (9)

| Tubazione | Da → a | Rete | Frase (riga della tabella A) |
|---|---|---|---|
| `mandata-pdc-collettore` | `pdc.water_supply` → `collettore-radiante.in` | `riscaldamento` | 2, 8 |
| `mandata-circuito-1` | `collettore-radiante.out_1` → `circuito-radiante-1.in` | `riscaldamento` | 9 |
| `mandata-circuito-2` | `collettore-radiante.out_2` → `circuito-radiante-2.in` | `riscaldamento` | 9 |
| `ritorno-circuito-1` | `circuito-radiante-1.out` → `raccordo-ritorno-radiante.a` | `riscaldamento` | 9 (il circuito chiuso si chiude) |
| `ritorno-circuito-2` | `circuito-radiante-2.out` → `raccordo-ritorno-radiante.c` | `riscaldamento` | 9 |
| `ritorno-radiante-volano` | `raccordo-ritorno-radiante.b` → `volano.a` | `riscaldamento` | 5 |
| `ritorno-volano-pdc` | `volano.b` → `pdc.water_return` | `riscaldamento` | 5, 2 |
| `acquedotto-boiler` | `acquedotto.a` → `boiler-acs.cold_in` | `acqua-fredda` | 13 |
| `boiler-utenze` | `boiler-acs.dhw_out` → `utenze-acs.a` | `acs` | 13 |

### Reti (3)

| Rete | Fluido | Da che macchina nasce | Frase |
|---|---|---|---|
| `riscaldamento` | `heating_water` | dalla pompa di calore, che la alimenta | 2 |
| `acqua-fredda` | `cold_water` | dal confine di acquedotto | 13 |
| `acs` | `domestic_hot_water` | dal boiler in pompa di calore, dove il fluido cambia | 11, 13 |

## C. Il controllo finale (§9)

| Domanda | Esito |
|---|---|
| Il JSON carica con lo strumento di validazione? | sì, nessun output |
| Ogni `definition_id` esiste in catalogo, nessuno è ferramenta? | sì: i mestieri usati sono `heat_generation`, `distribution`, `emission`, `junction`, `thermal_storage`, `heat_generation`+`dhw_storage`, `boundary` |
| Ogni attacco esiste, nessun attacco porta due tubazioni, nessuna tubazione tocca uno `stub`? | sì (verificato meccanicamente contro il catalogo) |
| Ogni tubazione va da `out` a `in`, sullo stesso fluido della rete? | sì |
| Attacchi `required: true` rimasti liberi? | nessuno |
| I `tag` sono solo quelli scritti dall'ingegnere? | il testo non scrive nessuna sigla: tutti i `tag` sono `null` |
| Ogni componente e ogni tubazione compare in questa tabella? | sì, sezione B |
| `subsystems`, `rule_applications`, `sheets` vuoti? | sì |
