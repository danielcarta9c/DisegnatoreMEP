# Tabella di rilettura — Esempio 2, pompa di calore con deviazione tra climatizzazione e ACS

Riferimento: `consegna/grafo.json`. Metodo del §8, passo 6 delle istruzioni: prima il testo
frase per frase verso il grafo, poi il grafo elemento per elemento verso il testo.

---

## A — Dal testo al grafo: ogni frase è rappresentata o dichiarata

| # | Frase del testo | Cosa la rappresenta nel grafo | Assunzione che la copre |
|---|---|---|---|
| 0 | «Esempio 2 – Pompa di calore con deviazione tra climatizzazione e ACS» (titolo) | `metadata.project_name`, `metadata.project_id` | — |
| 1 | «L'impianto è servito da una pompa di calore aria-acqua reversibile…» | componente `pdc` = `heat-pump-air-water` (mestiere `heat_generation`); `properties.tipo` = «aria-acqua reversibile» | a5 (la reversibilità è nel fluido di un circuito solo) |
| 2 | «…da 15 kW.» | `pdc.properties.potenza` = «15 kW»; da qui `plant_regime` = `up_to_35_kw` (15 ≤ 35, §4.6) | — (le potenze il testo le dà: non si chiedono) |
| 3 | «Sulla mandata è prevista una valvola a tre vie…» | componente `valvola-deviatrice` = `diverting-valve-3way` (mestiere `diversion`); tubazione `p1` da `pdc.water_supply` a `valvola-deviatrice.in` | a1 (nessun circolatore primario nominato: circolazione a bordo della PdC) |
| 4 | «…che devia il flusso alternativamente verso il circuito di climatizzazione…» | tubazione `p2` da `valvola-deviatrice.out_a` a `volano.primary_in` | — |
| 5 | «…oppure verso il bollitore per la produzione di ACS…» | tubazione `p3` da `valvola-deviatrice.out_b` a `bollitore.coil_in` | — |
| 6 | «…con priorità alla produzione sanitaria.» | niente: è regolazione, non topologia (§4.5). Sul grafo si vede la deviatrice, non la priorità | a6 |
| 7 | «Il circuito di climatizzazione comprende un volume tecnico da 100 litri…» | componente `volano` = `buffer-four-port` (`thermal_storage` + `hydraulic_separation`); `properties.volume` = «100 litri» | a11 (il ramo climatizzazione e il ramo bollitore stanno in una rete sola, `primario`) |
| 8 | «…configurato a quattro tubi.» | scelta della voce `buffer-four-port` sui quattro attacchi di flusso (`primary_in/out`, `secondary_out/in`), tutti e quattro usati; `properties.configurazione` = «a quattro tubi» | — |
| 9 | «Sul volume tecnico sono previsti anche il collegamento per il carico automatico dell'impianto da acquedotto e lo scarico.» | **niente nel grafo**: `filling` e `drain` sono ferramenta di servizio (§5, §7). Gli stub `vent`/`drain`/`probe` del volano restano liberi | a7 |
| 10 | «Dal volume parte un circuito secondario…» | rete `secondario`; tubazione `s1` da `volano.secondary_out` | a11 |
| 11 | «…con circolatore dedicato…» | componente `circolatore-secondario` = `pump-circulator`; tubazioni `s1` (ingresso) e `s2` (uscita), sulla mandata del secondario | a2 (il testo non dice su quale ramo sta) |
| 12 | «…che alimenta fan-coil idronici…» | componente `fan-coil` = `fan-coil` (mestiere `emission`), uno rappresentativo; tubazione `s2` verso `fan-coil.in`; tubazione `s3` di ritorno da `fan-coil.out` a `volano.secondary_in` (un circuito chiuso si chiude, §4.3) | a3 (quanti sono) |
| 13 | «…utilizzati sia in riscaldamento sia in raffrescamento.» | `fan-coil.properties.impiego`; il fluido delle reti `primario` e `secondario` resta `heating_water` (la tabella dei fluidi non ha il raffrescamento, §4.2) | a5 |
| 14 | «La produzione di ACS avviene tramite un bollitore con serpentino…» | componente `bollitore` = `dhw-cylinder` (mestiere `dhw_storage`, `stored_medium: domestic_hot_water`), scelto perché ha gli attacchi del serpentino (`coil_in`/`coil_out`) oltre a `cold_in`/`dhw_out`; `properties.tipo` = «con serpentino» | — |
| 15 | «…collegato alla pompa di calore.» | tubazione `p3` (andata, dalla deviatrice) e tubazione `p5` da `bollitore.coil_out` al raccordo `rc-ritorni-primario`, poi `p6` fino a `pdc.water_return` | a4 (con che pezzo i due ritorni si uniscono) |
| 16 | (topologia imposta dalle frasi 4, 5, 15) due ritorni su un solo attacco della PdC | componente `rc-ritorni-primario` = `tee-junction` (N=2 tubazioni che si incontrano → N−1 = 1 raccordo, §4.4); tubazioni `p4` (dal volano) e `p5` (dal bollitore) in ingresso, `p6` in uscita | a4 |
| 17 | «L'acqua fredda sanitaria entra nella parte bassa del bollitore…» | rete `acqua-fredda` (`cold_water`); componente `acquedotto` = `cold-water-inlet` (mestiere `boundary`); tubazione `f1` fino a `bollitore.cold_in` | a10 (i confini non sono nominati dal testo) |
| 18 | «…e l'ACS viene prelevata dalla parte alta.» | rete `acs` (`domestic_hot_water`); tubazione `c1` da `bollitore.dhw_out` a `utenze-sanitarie` = `dhw-draw-off` (mestiere `boundary`) | a10 |
| 19 | «Sull'uscita sanitaria è prevista una valvola miscelatrice.» | **niente nel grafo**: la miscelatrice sanitaria è mestiere `dhw_mixing`, ferramenta di servizio (§5). L'ACS va dal bollitore direttamente alle utenze | a8 |
| 20 | «Non è previsto il circuito di ricircolo ACS.» | **niente nel grafo**, ed è un'esclusione esplicita: nessuna `pump-circulator-dhw`, nessun anello di ritorno sanitario | a9 |

Nessuna frase del testo è rimasta senza riga.

---

## B — Dal grafo al testo: ogni elemento risale a una frase

### Reti

| Rete | Fluido | Frase da cui nasce |
|---|---|---|
| `primario` | `heating_water` | 3, 4, 5, 15 — il circuito che parte dalla PdC e serve i due rami |
| `secondario` | `heating_water` | 10, 11, 12 — «Dal volume parte un circuito secondario…» |
| `acqua-fredda` | `cold_water` | 17 — «L'acqua fredda sanitaria entra…» |
| `acs` | `domestic_hot_water` | 18 — «…l'ACS viene prelevata dalla parte alta.» |

### Componenti

| Componente | Voce di catalogo | Frase da cui nasce |
|---|---|---|
| `pdc` | `heat-pump-air-water` | 1, 2 |
| `valvola-deviatrice` | `diverting-valve-3way` | 3, 4, 5 |
| `volano` | `buffer-four-port` | 7, 8 |
| `circolatore-secondario` | `pump-circulator` | 11 |
| `fan-coil` | `fan-coil` | 12, 13 |
| `bollitore` | `dhw-cylinder` | 14, 15, 17, 18 |
| `rc-ritorni-primario` | `tee-junction` | 16 — imposto dalle frasi 4, 5, 15 (§4.4), dichiarato in a4 |
| `acquedotto` | `cold-water-inlet` | 17, dichiarato in a10 |
| `utenze-sanitarie` | `dhw-draw-off` | 18, dichiarato in a10 |

Nessun componente della lista «ferramenta» del §5. Nessun `tag` compilato: l'ingegnere non
ne ha scritto nessuno nel testo.

### Tubazioni

| Tubo | Da (porta `out`) | A (porta `in`) | Rete | Frase |
|---|---|---|---|---|
| `p1` | `pdc.water_supply` | `valvola-deviatrice.in` | `primario` | 3 |
| `p2` | `valvola-deviatrice.out_a` | `volano.primary_in` | `primario` | 4 |
| `p3` | `valvola-deviatrice.out_b` | `bollitore.coil_in` | `primario` | 5, 14, 15 |
| `p4` | `volano.primary_out` | `rc-ritorni-primario.a` | `primario` | 4 + 16 (ritorno del ramo climatizzazione) |
| `p5` | `bollitore.coil_out` | `rc-ritorni-primario.c` | `primario` | 15 + 16 (ritorno del serpentino) |
| `p6` | `rc-ritorni-primario.b` | `pdc.water_return` | `primario` | 15, 16 |
| `s1` | `volano.secondary_out` | `circolatore-secondario.a` | `secondario` | 10, 11 |
| `s2` | `circolatore-secondario.b` | `fan-coil.in` | `secondario` | 11, 12 |
| `s3` | `fan-coil.out` | `volano.secondary_in` | `secondario` | 12 (chiusura del circuito, §4.3) |
| `f1` | `acquedotto.a` | `bollitore.cold_in` | `acqua-fredda` | 17 |
| `c1` | `bollitore.dhw_out` | `utenze-sanitarie.a` | `acs` | 18 |

Nessun elemento del grafo è rimasto fuori dalle righe: ogni componente e ogni tubazione ha
una frase dietro.

---

## C — Controlli del §9, uno per uno

| Controllo | Esito |
|---|---|
| Il JSON carica con lo strumento di validazione | sì, nessun output |
| Ogni `definition_id` esiste nel catalogo | sì, 9 su 9 |
| Nessun componente ha un mestiere della lista «ferramenta» (§5) | sì |
| Ogni attacco usato esiste nel catalogo del suo pezzo | sì, 22 estremi su 22 |
| Nessun attacco porta due tubazioni | sì |
| Nessuna tubazione tocca un attacco `stub` | sì (`vent`, `drain`, `probe` del volano e `probe` del bollitore restano liberi) |
| Ogni tubazione va da una porta `out` a una porta `in` | sì, 11 su 11 |
| Stesso fluido alle due estremità, e uguale al fluido della rete | sì, 11 su 11 |
| Nessun attacco `required: true` rimasto libero | sì, nessuno |
| I `tag` sono solo quelli scritti dall'ingegnere | sì: tutti `null`, il testo non ne scrive |
| Ogni componente e ogni tubazione compare in questa tabella | sì (sezione B) |
| `subsystems`, `rule_applications`, `sheets` sono liste vuote | sì |
| `plant_regime` ricavato dalle potenze | sì: 15 kW, unico generatore → `up_to_35_kw` |
