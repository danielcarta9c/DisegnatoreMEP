# Rilettura frase per frase — Esempio 3, pompa di calore diretta su pavimento radiante

## A. Dal testo al grafo

Una riga per frase del testo. Ogni affermazione topologica ha, a destra, gli elementi
del grafo che la rappresentano, oppure la voce di `assumptions` che la copre.

| # | Frase del testo | Cosa la rappresenta nel grafo | Cosa non è rappresentato, e dove è dichiarato |
|---|---|---|---|
| F0 | «Esempio 3 – Pompa di calore diretta su pavimento radiante» (titolo) | `metadata.project_name`, `metadata.project_id` | — (il titolo non è topologia) |
| F1 | «L'impianto è composto da una pompa di calore aria-acqua da 8 kW…» | componente `pdc` = `heat-pump-air-water` (mestiere `heat_generation`); `properties.potenza` = «8 kW», `properties.tipo` = «aria-acqua»; da qui `plant_regime` = `up_to_35_kw` | il conto del regime e il fatto che sia stata sommata una sola potenza → `a8` |
| F1 | «…che alimenta **direttamente** un sistema radiante a pavimento a bassa temperatura.» | tubazione `t1` `pdc.water_supply` → `collettore-radiante.in`: nessun pezzo interposto; componenti `circuito-radiante-1` e `circuito-radiante-2` = `underfloor-panel` (mestiere `emission`), `properties.tipo` = «pavimento radiante a bassa temperatura»; rete `riscaldamento` (`heating_water`) | «direttamente» = niente separatore e niente circuito secondario → `a4` |
| F2 | «Non è previsto un separatore idraulico…» | *nulla*: il grafo non ha `hydraulic_separation`, ed è voluto | esclusione esplicita → `a4` |
| F2 | «…e la circolazione è affidata al circolatore integrato nella pompa di calore.» | *nessun componente*: la voce di catalogo `heat-pump-air-water` dichiara `carries_on_board: ["circulation"]` | componente integrato, non disegnato a sé → `a3` |
| F3 | «Sul ritorno dell'impianto radiante è installato un volume tecnico da 50 litri a due tubi, montato in serie…» | componente `volano` = `buffer-two-port` (mestiere `thermal_storage`, `stored_medium: heating_water`, due attacchi di flusso `a`/`b` come chiede «a due tubi»); tubazioni `t6` (`rc-ritorno-radiante.b` → `volano.a`) e `t7` (`volano.b` → `pdc.water_return`): è in serie sul ritorno, fra i circuiti radianti e la pompa di calore; `properties.volume` = «50 litri», `properties.configurazione` = «a due tubi, montato in serie» | come i ritorni dei circuiti ambiente si riuniscono prima del volano → `a2` |
| F3 | «…con funzione di aumento del contenuto d'acqua e stabilizzazione del funzionamento della pompa di calore.» | `volano.properties.funzione`, trascritta come sta | — (è la ragione del pezzo, non un collegamento) |
| F4 | «Sul volume tecnico sono previsti il collegamento per il carico automatico dell'impianto da acquedotto e lo scarico.» | *nulla*: `filling` e `drain` sono ferramenta di servizio (§5), e il volano ha già a catalogo gli attacchi `drain` e `vent`, lasciati liberi apposta | la nomina non è persa → `a5` |
| F5 | «Il collettore del pavimento radiante alimenta più circuiti ambiente…» | componente `collettore-radiante` = `zone-manifold` (mestiere `distribution`); tubazioni `t2` (`out_1` → `circuito-radiante-1.in`) e `t3` (`out_2` → `circuito-radiante-2.in`) | quanti sono davvero i circuiti ambiente → `a1` |
| F5 | «…con regolazione di zona.» | `collettore-radiante.properties.regolazione` = «di zona» | è logica di regolazione, non topologia: nessuna valvola disegnata → `a6` |
| F6 | «La produzione di ACS è completamente separata…» | reti separate `acqua-fredda` (`cold_water`) e `acqua-calda-sanitaria` (`domestic_hot_water`); nessuna tubazione fra il boiler e la rete `riscaldamento` | il ricircolo sanitario, di cui il testo non dice niente → `a9` |
| F6 | «…realizzata con un boiler in pompa di calore dedicato da 200 litri…» | componente `boiler-acs` = `dhw-heat-pump` (mestieri `heat_generation` **e** `dhw_storage`, `stored_medium: domestic_hot_water`: produce l'acqua calda **da solo** e la tiene in serbo); `properties.volume` = «200 litri», `properties.tipo` = «boiler in pompa di calore dedicato» | la sua potenza, che il testo non dà → `a8` |
| F6 | «…non collegato idraulicamente all'impianto di riscaldamento.» | *nessuna tubazione* fra `boiler-acs` e il circuito `riscaldamento`: nel grafo il boiler è un ramo aperto a sé | esclusione esplicita + i due confini aggiunti per chiudere gli attacchi obbligatori (`t8`, `t9`) → `a7` |

## B. Dal grafo al testo

Il controllo contrario: ogni componente e ogni tubazione del grafo risale a una frase precisa.
Nessun elemento resta senza riga.

| Elemento | Voce di catalogo | Da quale frase nasce |
|---|---|---|
| `pdc` | `heat-pump-air-water` | F1 «una pompa di calore aria-acqua da 8 kW» |
| `collettore-radiante` | `zone-manifold` | F5 «Il collettore del pavimento radiante» |
| `circuito-radiante-1` | `underfloor-panel` | F1 «un sistema radiante a pavimento a bassa temperatura» + F5 «più circuiti ambiente» |
| `circuito-radiante-2` | `underfloor-panel` | F5 «più circuiti ambiente» (secondo circuito rappresentativo, dichiarato in `a1`) |
| `rc-ritorno-radiante` | `tee-junction` | F3 «Sul ritorno dell'impianto radiante»: due ritorni, un solo attacco sul volano → 2−1 = 1 confluenza (§4.4), dichiarata in `a2` |
| `volano` | `buffer-two-port` | F3 «un volume tecnico da 50 litri a due tubi, montato in serie» |
| `boiler-acs` | `dhw-heat-pump` | F6 «un boiler in pompa di calore dedicato da 200 litri» |
| `acquedotto` | `cold-water-inlet` | F6 «La produzione di ACS»: confine di alimentazione, aggiunto per chiudere `cold_in` (obbligatorio) → `a7` |
| `utenze-acs` | `dhw-draw-off` | F6 «La produzione di ACS»: confine di erogazione, aggiunto per chiudere `dhw_out` (obbligatorio) → `a7` |
| `t1` `pdc.water_supply` → `collettore-radiante.in` | — | F1 «alimenta direttamente» |
| `t2` `collettore-radiante.out_1` → `circuito-radiante-1.in` | — | F5 «alimenta più circuiti ambiente» |
| `t3` `collettore-radiante.out_2` → `circuito-radiante-2.in` | — | F5 «alimenta più circuiti ambiente» |
| `t4` `circuito-radiante-1.out` → `rc-ritorno-radiante.a` | — | F3 «Sul ritorno dell'impianto radiante» (il circuito si chiude: §4.3) |
| `t5` `circuito-radiante-2.out` → `rc-ritorno-radiante.c` | — | F3, idem |
| `t6` `rc-ritorno-radiante.b` → `volano.a` | — | F3 «montato in serie» sul ritorno |
| `t7` `volano.b` → `pdc.water_return` | — | F3 «montato in serie» + F1: il circuito chiuso torna al generatore |
| `t8` `acquedotto.a` → `boiler-acs.cold_in` | — | F6, tramite `a7` |
| `t9` `boiler-acs.dhw_out` → `utenze-acs.a` | — | F6, tramite `a7` |

## C. Controllo finale (§9)

| Domanda | Esito |
|---|---|
| Il JSON carica con lo strumento di validazione? | sì, nessun output |
| Ogni `definition_id` esiste in catalogo, nessuno è ferramenta? | sì: 9 voci, tutte con mestiere della lista ammessa |
| Ogni attacco esiste, nessuno porta due tubazioni, nessuna tubazione tocca uno `stub`? | sì; gli `stub` di `volano` (`vent`, `drain`, `probe`) e di `boiler-acs` (`probe`) restano liberi |
| Ogni tubazione va da `out` a `in`, sullo stesso fluido della sua rete? | sì, 9 tubazioni su 9 |
| Nessun attacco obbligatorio è rimasto libero? | sì, nessuno |
| I `tag` sono solo quelli scritti dall'ingegnere? | il testo non scrive nessuna sigla: tutti i `tag` sono `null` |
| Ogni componente e ogni tubazione è in tabella? | sì, sezione B |
| Ogni cosa non detta è una voce di `assumptions`? | sì, 9 voci, tutte `proposed` |
| `subsystems`, `rule_applications`, `sheets` vuoti? | sì |
