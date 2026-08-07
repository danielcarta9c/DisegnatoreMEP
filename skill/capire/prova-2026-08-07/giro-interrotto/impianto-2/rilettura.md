# Tabella di rilettura — Impianto 2

Impianto: «Pompa di calore con deviazione tra climatizzazione e ACS»
Grafo: `consegna/grafo.json` — 9 componenti, 4 reti, 11 tubazioni, 13 assunzioni.

---

## A. Dal testo al grafo — una riga per frase

| # | Frase del testo | Che cosa la rappresenta nel grafo | Assunzioni che la coprono |
|---|---|---|---|
| T | *«Esempio 2 – Pompa di calore con deviazione tra climatizzazione e ACS»* (titolo) | `metadata.project_name`, `metadata.project_id` | — |
| S1 | *«L'impianto è servito da una pompa di calore aria-acqua reversibile da 15 kW.»* | componente `pdc` (`heat-pump-air-water`, mestiere `heat_generation`); `properties.potenza = "15 kW"`; `properties.tipo = "aria-acqua reversibile"`; `plant_regime = "up_to_35_kw"` (15 kW ≤ 35, unica macchina che genera calore) | a1 (circolatore primario a bordo macchina, non disegnato), a2 (reversibile: il raffrescamento corre negli stessi tubi), a13 (regime ricavato dai 15 kW; resa o assorbita non è detto) |
| S2 | *«Sulla mandata è prevista una valvola a tre vie che devia il flusso alternativamente verso il circuito di climatizzazione oppure verso il bollitore per la produzione di ACS, con priorità alla produzione sanitaria.»* | componente `valvola-deviatrice` (`diverting-valve-3way`, mestiere `diversion`); tubazione `p1` (`pdc.water_supply` → `valvola-deviatrice.in`, «sulla mandata»); tubazione `p2` (`out_a` → volume tecnico, ramo climatizzazione); tubazione `p3` (`out_b` → serpentino del bollitore, ramo ACS) | a3 (la priorità è regolazione: il grafo mostra la valvola, non la priorità) |
| S3 | *«Il circuito di climatizzazione comprende un volume tecnico da 100 litri configurato a quattro tubi.»* | componente `volume-tecnico` (`buffer-four-port`, mestieri `hydraulic_separation` + `thermal_storage`, quattro attacchi di flusso); `properties.volume = "100 litri"`; `properties.configurazione = "a quattro tubi"`; rete `primario` sul lato primario | a7 (la voce a quattro attacchi dichiara anche la separazione idraulica, che il testo non nomina), a12 (climatizzazione e ACS modellate come rami di una rete unica di primario) |
| S4 | *«Sul volume tecnico sono previsti anche il collegamento per il carico automatico dell'impianto da acquedotto e lo scarico.»* | **niente nel grafo** — `filling` e `drain` sono ferramenta di servizio (§5) | a8 (la nomina è registrata: li aggiunge il pezzo che completa) |
| S5 | *«Dal volume parte un circuito secondario con circolatore dedicato che alimenta fan-coil idronici utilizzati sia in riscaldamento sia in raffrescamento.»* | rete `secondario-climatizzazione`; componente `circolatore-secondario` (`pump-circulator`); componente `fan-coil` (`fan-coil`, mestiere `emission`); tubazioni `p7` (`volume-tecnico.secondary_out` → circolatore), `p8` (circolatore → `fan-coil.in`), `p9` (`fan-coil.out` → `volume-tecnico.secondary_in`, il ritorno che chiude il circuito) | a2 (raffrescamento negli stessi tubi), a5 (un solo fan-coil rappresentativo: quanti sono?), a6 (circolatore messo sulla mandata, per convenzione) |
| S6 | *«La produzione di ACS avviene tramite un bollitore con serpentino collegato alla pompa di calore.»* | componente `bollitore` (`dhw-cylinder`, mestiere `dhw_storage`, `stored_medium = domestic_hot_water`); `properties.tipo = "con serpentino"`; tubazione `p3` (mandata al serpentino, da S2); tubazioni `p5` (`bollitore.coil_out` → raccordo) e `p6` (raccordo → `pdc.water_return`), più `p4` (`volume-tecnico.primary_out` → raccordo): è il «collegato alla pompa di calore»; componente `rc-ritorno-primario` (`tee-junction`) | a4 (il testo non dice con che pezzo i due ritorni si riuniscono: raccordo a T di confluenza) |
| S7 | *«L'acqua fredda sanitaria entra nella parte bassa del bollitore e l'ACS viene prelevata dalla parte alta.»* | rete `acqua-fredda-sanitaria` (`cold_water`) e rete `acqua-calda-sanitaria` (`domestic_hot_water`); componenti `acquedotto` (`cold-water-inlet`) e `utenze-acs` (`dhw-draw-off`), i due confini; tubazione `p10` (`acquedotto.a` → `bollitore.cold_in`) e tubazione `p11` (`bollitore.dhw_out` → `utenze-acs.a`) | a11 (i due confini chiudono il circuito sanitario aperto: il testo non li nomina) |
| S8 | *«Sull'uscita sanitaria è prevista una valvola miscelatrice.»* | **niente nel grafo** — mestiere `dhw_mixing`, miscelatrice sanitaria, ferramenta di servizio (§5) | a9 (la nomina è registrata: la aggiunge il pezzo che completa) |
| S9 | *«Non è previsto il circuito di ricircolo ACS.»* | **niente nel grafo** — esclusione esplicita | a10 (non è disegnato perché non c'è, non perché sia stato perso) |

Nessuna frase del testo è rimasta senza riga. Le tre frasi che non producono grafo (S4, S8, S9)
producono ciascuna una voce di `assumptions`, perché sono informazione, non silenzio.

---

## B. Dal grafo al testo — ogni pezzo risale a una frase

### Componenti

| id | voce di catalogo | frase di provenienza |
|---|---|---|
| `pdc` | `heat-pump-air-water` | S1 |
| `valvola-deviatrice` | `diverting-valve-3way` | S2 |
| `volume-tecnico` | `buffer-four-port` | S3 |
| `circolatore-secondario` | `pump-circulator` | S5 |
| `fan-coil` | `fan-coil` | S5 |
| `bollitore` | `dhw-cylinder` | S6 |
| `rc-ritorno-primario` | `tee-junction` | S6 + S2 (due ritorni su un attacco solo) — assunzione a4 |
| `acquedotto` | `cold-water-inlet` | S7 — assunzione a11 |
| `utenze-acs` | `dhw-draw-off` | S7 — assunzione a11 |

### Reti

| id | fluido | frase di provenienza |
|---|---|---|
| `primario` | `heating_water` | S1 + S2 (la mandata della pompa di calore e i suoi due rami) — assunzione a12 |
| `secondario-climatizzazione` | `heating_water` | S5 («Dal volume parte un circuito secondario») — assunzione a2 sul raffrescamento |
| `acqua-fredda-sanitaria` | `cold_water` | S7 («L'acqua fredda sanitaria entra…») |
| `acqua-calda-sanitaria` | `domestic_hot_water` | S7 («…l'ACS viene prelevata dalla parte alta») |

### Tubazioni

| id | da → a | rete | frase di provenienza |
|---|---|---|---|
| `p1` | `pdc.water_supply` → `valvola-deviatrice.in` | `primario` | S2 («sulla mandata è prevista una valvola a tre vie») |
| `p2` | `valvola-deviatrice.out_a` → `volume-tecnico.primary_in` | `primario` | S2 + S3 («verso il circuito di climatizzazione», che comprende il volume) |
| `p3` | `valvola-deviatrice.out_b` → `bollitore.coil_in` | `primario` | S2 + S6 («oppure verso il bollitore», serpentino) |
| `p4` | `volume-tecnico.primary_out` → `rc-ritorno-primario.a` | `primario` | S3 (il ramo di climatizzazione torna alla macchina) — a4 |
| `p5` | `bollitore.coil_out` → `rc-ritorno-primario.c` | `primario` | S6 («serpentino collegato alla pompa di calore») — a4 |
| `p6` | `rc-ritorno-primario.b` → `pdc.water_return` | `primario` | S1 + S6 (il circuito chiuso si chiude sulla macchina) — a4 |
| `p7` | `volume-tecnico.secondary_out` → `circolatore-secondario.a` | `secondario-climatizzazione` | S5 («dal volume parte… con circolatore dedicato») — a6 |
| `p8` | `circolatore-secondario.b` → `fan-coil.in` | `secondario-climatizzazione` | S5 («alimenta fan-coil idronici») |
| `p9` | `fan-coil.out` → `volume-tecnico.secondary_in` | `secondario-climatizzazione` | S5 (il circuito secondario si chiude sul volume) |
| `p10` | `acquedotto.a` → `bollitore.cold_in` | `acqua-fredda-sanitaria` | S7 («entra nella parte bassa del bollitore») — a11 |
| `p11` | `bollitore.dhw_out` → `utenze-acs.a` | `acqua-calda-sanitaria` | S7 («l'ACS viene prelevata dalla parte alta») — a11 |

Nessun componente e nessuna tubazione compare fuori da questa tabella: tutto risale a una
frase, o a una frase più un'assunzione dichiarata.

---

## C. Controllo finale (§9)

| Domanda | Esito |
|---|---|
| Il JSON carica con lo strumento di validazione? | sì — comando §8 passo 7 eseguito, nessun output |
| Ogni `definition_id` esiste nel catalogo? | sì — 9 su 9 |
| Nessun `definition_id` ha un mestiere della lista «ferramenta»? | sì — nessuno |
| Ogni attacco usato esiste nel catalogo del suo pezzo? | sì — 22 estremità verificate |
| Nessun attacco porta due tubazioni? | sì — nessuna coppia componente+attacco ripetuta |
| Nessuna tubazione tocca un attacco `stub`? | sì — `vent`, `drain`, `probe` del volume tecnico e `probe` del bollitore restano liberi |
| Ogni tubazione va da una porta `out` a una porta `in`? | sì — 11 su 11 |
| Stesso fluido alle due estremità, e uguale a quello della rete? | sì — 11 su 11 |
| Nessun attacco `required: true` rimasto libero? | sì — tutti collegati |
| I `tag` sono solo quelli scritti dall'ingegnere? | sì — il testo non scrive nessuna sigla, tutti i `tag` sono `null` |
| Ogni componente e ogni tubazione compare nella tabella di rilettura? | sì — sezione B |
| Ogni cosa non detta e chiusa o lasciata fuori è in `assumptions`? | sì — 13 voci, tutte `proposed` |
| `subsystems`, `rule_applications`, `sheets` sono liste vuote? | sì |
