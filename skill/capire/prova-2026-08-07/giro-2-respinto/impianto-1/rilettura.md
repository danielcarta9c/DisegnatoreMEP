# Tabella di rilettura

Impianto: *Due pompe di calore in parallelo con accumulo combinato* — grafo `consegna/grafo.json`.

La tabella si legge nei due versi, come chiede il §8 passo 6: prima **dal testo al grafo**
(ogni affermazione del testo è rappresentata o dichiarata), poi **dal grafo al testo**
(ogni componente e ogni tubazione risale a una frase precisa).

---

## Parte 1 — Dal testo al grafo

| # | Frase del testo | Cosa afferma | Elementi del grafo che la rappresentano | Assunzione che la copre |
|---|---|---|---|---|
| T | «Due pompe di calore in parallelo con accumulo combinato» (titolo) | il nome dell'impianto | `metadata.project_name`, `metadata.project_id` | — |
| 1a | «L'impianto è composto da due pompe di calore aria-acqua…» | due generatori, di tipo aria-acqua | `pdc-1`, `pdc-2` (`heat-pump-air-water`), proprietà `tipo: "aria-acqua"` | — |
| 1b | «…da 12 kW ciascuna…» | la potenza di ciascun generatore | proprietà `potenza: "12 kW"` su `pdc-1` e `pdc-2`; da qui `plant_regime: "up_to_35_kw"` (12+12 = 24 kW ≤ 35) | `a10` (dice quali potenze sono state sommate) |
| 1c | «…installate in parallelo…» | i due flussi di mandata si uniscono, il ritorno si divide fra le due macchine | `rc-mandata-generatori` (`tee-junction`) con `t1`, `t2`, `t3`; `rc-ritorno-generatori` (`tee-split`) con `t4`, `t5`, `t6` | `a1` (il testo non dice **con che pezzo** si uniscono) |
| 1d | «…e gestite una come master e una come slave.» | logica di regolazione | *nessun elemento*: non è topologia, non produce né nodi né tubi | `a2` |
| — | (il testo non dice nulla sulla circolazione del circuito primario) | — | *nessun circolatore sul primario*: la voce di catalogo scelta dichiara la circolazione a bordo macchina | `a3` |
| 2a | «Le due macchine alimentano un accumulo ECOcombi da 200 litri…» | i generatori alimentano un accumulo; nome commerciale e volume | `volano` (`buffer-combined`), proprietà `modello: "ECOcombi"`, `volume: "200 litri"`; tubazioni `t3` (mandata al volume) e `t4` (ritorno dal volume) | — |
| 2b | «…utilizzato sia come volume tecnico a quattro tubi per il riscaldamento…» | l'accumulo ha quattro attacchi di riscaldamento: primario dai generatori, secondario verso l'impianto | attacchi `primary_in` (`t3`), `primary_out` (`t4`), `secondary_out` (`t7`), `secondary_in` (`t9`) del `volano`; proprietà `configurazione: "a quattro tubi"` | — |
| 2c | «…sia per la produzione istantanea di acqua calda sanitaria tramite serpentino interno.» | lo stesso accumulo produce l'ACS in modo istantaneo, con un serpentino **interno** | attacchi sanitari del `volano`: `cold_in` (`t10`) e `dhw_out` (`t11`); proprietà `produzione_sanitaria: "istantanea tramite serpentino interno"`. La voce di catalogo scelta è l'unica con quattro attacchi di riscaldamento **più** gli attacchi del serpentino, e il suo fluido in serbo è acqua di riscaldamento: perciò niente accumulo di ACS | `a7` (il serpentino è integrato, non è un pezzo a sé) |
| 3a | «Sul lato riscaldamento, dal volume tecnico parte un circuito secondario…» | esiste una seconda rete, distinta dal primario, che nasce dal volume | rete `secondario-radiatori` (`heating_water`), tubazioni `t7`, `t8`, `t9` | — |
| 3b | «…con circolatore dedicato…» | un circolatore proprio del circuito secondario, pezzo a sé | `circolatore-secondario` (`pump-circulator`), `t7` e `t8` | `a4` (il testo non dice su quale ramo: messo sulla mandata, per convenzione) |
| 3c | «…che alimenta direttamente l'impianto esistente a radiatori.» | il secondario alimenta i radiatori esistenti, senza miscelazione; l'acqua va **e torna** (circuito chiuso) | `radiatori` (`radiator`), proprietà `stato: "esistente"`; `t8` (mandata) e `t9` (ritorno al `volano`) | `a5` (quanti radiatori? uno solo, rappresentativo) · `a6` («direttamente» = nessuna valvola miscelatrice) |
| 4a | «Sul lato sanitario, l'acqua fredda di acquedotto entra nel serpentino interno…» | l'acquedotto è il confine da cui entra l'acqua fredda, e va al serpentino | `acquedotto` (`cold-water-inlet`), rete `acqua-fredda` (`cold_water`), tubazione `t10` verso `volano.cold_in` | — |
| 4b | «…e l'ACS viene prelevata in uscita.» | l'acqua calda sanitaria esce dal serpentino e va alle utenze (circuito aperto) | `utenze-sanitarie` (`dhw-draw-off`), rete `acs` (`domestic_hot_water`), tubazione `t11` da `volano.dhw_out` | — |
| 5 | «Non è previsto ricircolo sanitario.» | esclusione esplicita | *nessun elemento*: il ricircolo non è disegnato perché il testo lo esclude | `a8` |
| 6 | «Sul volume tecnico sono previsti anche il collegamento per il carico automatico dell'impianto da acquedotto e lo scarico.» | ferramenta di servizio nominata dal testo (gruppo di riempimento, attacco di scarico) | *nessun elemento*: mestieri `filling` e `drain`, fuori dal grafo di prima stesura. Gli attacchi di servizio del `volano` (`vent`, `drain`, `probe`) restano liberi apposta | `a9` |

---

## Parte 2 — Dal grafo al testo

Nessun elemento del grafo senza una frase dietro.

### Componenti

| Componente | Voce di catalogo | Frase che lo giustifica |
|---|---|---|
| `pdc-1` | `heat-pump-air-water` | 1a, 1b |
| `pdc-2` | `heat-pump-air-water` | 1a, 1b |
| `rc-mandata-generatori` | `tee-junction` | 1c (raccordo imposto dal «in parallelo» — `a1`) |
| `rc-ritorno-generatori` | `tee-split` | 1c (raccordo imposto dal «in parallelo» — `a1`) |
| `volano` | `buffer-combined` | 2a, 2b, 2c |
| `circolatore-secondario` | `pump-circulator` | 3b |
| `radiatori` | `radiator` | 3c |
| `acquedotto` | `cold-water-inlet` | 4a |
| `utenze-sanitarie` | `dhw-draw-off` | 4b |

### Tubazioni

| Tubazione | Da → a | Rete | Frase che la giustifica |
|---|---|---|---|
| `t1` | `pdc-1.water_supply` → `rc-mandata-generatori.a` | `primario-generatori` | 1c, 2a |
| `t2` | `pdc-2.water_supply` → `rc-mandata-generatori.c` | `primario-generatori` | 1c, 2a |
| `t3` | `rc-mandata-generatori.b` → `volano.primary_in` | `primario-generatori` | 2a, 2b |
| `t4` | `volano.primary_out` → `rc-ritorno-generatori.a` | `primario-generatori` | 2b, 1c (il circuito chiuso si chiude) |
| `t5` | `rc-ritorno-generatori.b` → `pdc-1.water_return` | `primario-generatori` | 1c |
| `t6` | `rc-ritorno-generatori.c` → `pdc-2.water_return` | `primario-generatori` | 1c |
| `t7` | `volano.secondary_out` → `circolatore-secondario.a` | `secondario-radiatori` | 3a, 3b |
| `t8` | `circolatore-secondario.b` → `radiatori.in` | `secondario-radiatori` | 3b, 3c |
| `t9` | `radiatori.out` → `volano.secondary_in` | `secondario-radiatori` | 3c, 2b (il circuito chiuso si chiude) |
| `t10` | `acquedotto.a` → `volano.cold_in` | `acqua-fredda` | 4a |
| `t11` | `volano.dhw_out` → `utenze-sanitarie.a` | `acs` | 4b |

### Reti

| Rete | Fluido | Frase che la giustifica |
|---|---|---|
| `primario-generatori` | `heating_water` | 1a, 1c, 2a (il circuito dei generatori verso il volume) |
| `secondario-radiatori` | `heating_water` | 3a («parte un circuito secondario») |
| `acqua-fredda` | `cold_water` | 4a («l'acqua fredda di acquedotto») |
| `acs` | `domestic_hot_water` | 4b («l'ACS viene prelevata in uscita») |

---

## Parte 3 — Il controllo finale del §9

| Domanda | Risposta |
|---|---|
| Il JSON carica con lo strumento di validazione? | Sì (comando del §8 passo 7, nessun output). |
| Ogni `definition_id` esiste nel catalogo, e nessuno ha un mestiere della lista «ferramenta»? | Sì: i mestieri usati sono `heat_generation`, `hydraulic_separation` + `thermal_storage`, `junction`, `circulation`, `emission`, `boundary`. |
| Ogni attacco usato esiste, nessun attacco porta due tubazioni, nessuna tubazione tocca uno `stub`? | Sì: 22 estremi di tubazione su 22 attacchi distinti; gli `stub` del `volano` (`vent`, `drain`, `probe`) sono liberi. |
| Ogni tubazione va da una porta `out` a una porta `in`, sullo stesso fluido? | Sì, verificata una per una contro il catalogo. |
| Nessun attacco `required` è rimasto libero? | Sì: tutti collegati, compresi i sei attacchi obbligatori del `volano`. |
| I `tag` sono solo quelli scritti dall'ingegnere? | Il testo non scrive nessuna sigla: tutti i `tag` sono `null`. |
| Ogni componente e ogni tubazione compare in questa tabella? | Sì, Parte 2. |
| Ogni cosa non detta che è stata chiusa o lasciata fuori è in `assumptions`? | Sì: dieci voci, `a1`–`a10`, tutte `proposed`. |
| `subsystems`, `rule_applications`, `sheets` sono liste vuote? | Sì. |

**Le quattro cose da cui dipende il resto della catena**

- **Che macchina è ciascun pezzo.** Due pompe di calore aria-acqua: producono calore, non producono l'ACS da sole, non tengono riserva. Un accumulo combinato: separa idraulicamente e tiene una riserva **di acqua di riscaldamento**; l'ACS la produce di passaggio, con il serpentino, e non la accumula.
- **Che acqua porta ogni circuito, e c'è il sanitario?** Sì, il sanitario c'è: acqua fredda di acquedotto in ingresso al serpentino, acqua calda sanitaria in uscita alle utenze. Gli altri due circuiti (primario e secondario) portano acqua di riscaldamento.
- **Il regime della centrale.** Ricavato: 12 + 12 = 24 kW ≤ 35 → `up_to_35_kw`.
- **Come i circuiti toccano il serbatoio.** Primario e secondario **pescano nella riserva** del volume tecnico (quattro attacchi, acqua di riscaldamento). Il circuito sanitario **lo attraversa scambiando calore**: entra freddo dall'acquedotto nel serpentino, esce caldo alle utenze, e non si mescola mai con l'acqua del volume.
