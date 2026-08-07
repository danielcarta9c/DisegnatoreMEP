# Tabella di rilettura — Esempio 2, pompa di calore con deviazione tra climatizzazione e ACS

Riferimento: `consegna/grafo.json`. Due letture incrociate, come chiede il §8 passo 6:
prima dal testo al grafo (ogni frase è rappresentata o dichiarata), poi dal grafo al testo
(ogni pezzo e ogni tubo risalgono a una frase).

## A. Dal testo al grafo — una riga per frase

| # | Frase del testo | Cosa la rappresenta nel grafo | Assunzioni che la coprono |
|---|---|---|---|
| F0 | *«Esempio 2 – Pompa di calore con deviazione tra climatizzazione e ACS»* (titolo) | `metadata.project_name`, `metadata.project_id` | — |
| F1 | *«L'impianto è servito da una pompa di calore aria-acqua reversibile da 15 kW.»* | componente `pdc` (`heat-pump-air-water`); `properties.potenza = "15 kW"`; `properties.tipo = "aria-acqua reversibile"`; `plant_regime = "up_to_35_kw"` (15 kW ≤ 35 kW, unico generatore); rete `primario`; tubazione `t-raccordo-pdc` (il ritorno alla macchina) | a1 (reversibile: il raffrescamento non ha un fluido suo), a2 (circolatore primario a bordo macchina, come dichiara la voce di catalogo) |
| F2 | *«Sulla mandata è prevista una valvola a tre vie che devia il flusso alternativamente verso il circuito di climatizzazione oppure verso il bollitore per la produzione di ACS, con priorità alla produzione sanitaria.»* | componente `valvola-deviatrice` (`diverting-valve-3way`); tubazioni `t-pdc-valvola` (mandata PdC → valvola), `t-valvola-volume` (ramo climatizzazione), `t-valvola-bollitore` (ramo sanitario) | a6 (la priorità è regolazione: si vede la valvola, non la priorità), a12 (i due rami restano una sola rete primaria) |
| F3 | *«Il circuito di climatizzazione comprende un volume tecnico da 100 litri configurato a quattro tubi.»* | componente `volume-tecnico` (`buffer-four-port`: quattro attacchi di flusso, accumula e separa idraulicamente); `properties.volume = "100 litri"`; `properties.configurazione = "a quattro tubi"`; tubazioni `t-valvola-volume` (primario in ingresso) e `t-volume-raccordo` (primario in uscita) | — |
| F4 | *«Sul volume tecnico sono previsti anche il collegamento per il carico automatico dell'impianto da acquedotto e lo scarico.»* | **niente nel grafo** — sono accessori di servizio (`filling`, `drain`), li aggiunge il pezzo successivo della catena; gli attacchi di servizio del volume restano liberi apposta | a7 |
| F5 | *«Dal volume parte un circuito secondario con circolatore dedicato che alimenta fan-coil idronici utilizzati sia in riscaldamento sia in raffrescamento.»* | rete `secondario`; componenti `circolatore-secondario` (`pump-circulator`) e `fan-coil` (`fan-coil`, con `properties.tipo` e `properties.impiego`); tubazioni `t-volume-circolatore`, `t-circolatore-fancoil`, `t-fancoil-volume` (il circuito si chiude sul volume) | a3 (circolatore sulla mandata, per convenzione), a4 (un solo fan-coil, rappresentativo), a1 (raffrescamento), a12 (il secondario è rete a sé perché il volume separa) |
| F6 | *«La produzione di ACS avviene tramite un bollitore con serpentino collegato alla pompa di calore.»* | componente `bollitore` (`dhw-cylinder`: accumula acqua calda sanitaria e ha gli attacchi del serpentino); `properties.tipo = "con serpentino"`; tubazioni `t-valvola-bollitore` (serpentino in ingresso) e `t-bollitore-raccordo` (serpentino in uscita); componente `raccordo-ritorni` (`tee-junction`) e tubazione `t-raccordo-pdc`, che riportano il serpentino alla pompa di calore | a5 (il testo non dice con che pezzo i due ritorni si riuniscono) |
| F7 | *«L'acqua fredda sanitaria entra nella parte bassa del bollitore e l'ACS viene prelevata dalla parte alta.»* | reti `acqua-fredda` (`cold_water`) e `acs` (`domestic_hot_water`); componenti di confine `acquedotto` (`cold-water-inlet`) e `utenze-sanitarie` (`dhw-draw-off`); tubazioni `t-acquedotto-bollitore` (→ `cold_in`) e `t-bollitore-utenze` (da `dhw_out`) | a10 (i due confini non sono nominati dal testo), a11 (il grafo non porta la quota degli attacchi) |
| F8 | *«Sull'uscita sanitaria è prevista una valvola miscelatrice.»* | **niente nel grafo** — la miscelatrice sanitaria (`dhw_mixing`) è ferramenta di servizio, la aggiunge il pezzo delle regole | a8 |
| F9 | *«Non è previsto il circuito di ricircolo ACS.»* | **niente nel grafo** — esclusione esplicita, registrata perché non venga riaggiunta | a9 |

## B. Dal grafo al testo — ogni elemento risale a una frase

### Componenti

| Componente | Voce di catalogo | Frase |
|---|---|---|
| `pdc` | `heat-pump-air-water` | F1 |
| `valvola-deviatrice` | `diverting-valve-3way` | F2 |
| `volume-tecnico` | `buffer-four-port` | F3 |
| `circolatore-secondario` | `pump-circulator` | F5 |
| `fan-coil` | `fan-coil` | F5 |
| `bollitore` | `dhw-cylinder` | F6 |
| `raccordo-ritorni` | `tee-junction` | F2 + F6, imposto dalla topologia descritta (due ritorni, un attacco solo sulla PdC) — dichiarato in a5 |
| `acquedotto` | `cold-water-inlet` | F7 (confine, dichiarato in a10) |
| `utenze-sanitarie` | `dhw-draw-off` | F7 (confine, dichiarato in a10) |

### Tubazioni

| Tubazione | Da → a | Rete | Frase |
|---|---|---|---|
| `t-pdc-valvola` | `pdc.water_supply` → `valvola-deviatrice.in` | `primario` | F2 («sulla mandata») |
| `t-valvola-volume` | `valvola-deviatrice.out_a` → `volume-tecnico.primary_in` | `primario` | F2 + F3 (ramo climatizzazione) |
| `t-valvola-bollitore` | `valvola-deviatrice.out_b` → `bollitore.coil_in` | `primario` | F2 + F6 (ramo sanitario) |
| `t-volume-raccordo` | `volume-tecnico.primary_out` → `raccordo-ritorni.a` | `primario` | F3 + F1 (il circuito si chiude sulla PdC) — a5 |
| `t-bollitore-raccordo` | `bollitore.coil_out` → `raccordo-ritorni.c` | `primario` | F6 («collegato alla pompa di calore») — a5 |
| `t-raccordo-pdc` | `raccordo-ritorni.b` → `pdc.water_return` | `primario` | F1 + F6 — a5 |
| `t-volume-circolatore` | `volume-tecnico.secondary_out` → `circolatore-secondario.a` | `secondario` | F5 — a3 |
| `t-circolatore-fancoil` | `circolatore-secondario.b` → `fan-coil.in` | `secondario` | F5 |
| `t-fancoil-volume` | `fan-coil.out` → `volume-tecnico.secondary_in` | `secondario` | F5 (il circuito secondario torna al volume) |
| `t-acquedotto-bollitore` | `acquedotto.a` → `bollitore.cold_in` | `acqua-fredda` | F7 |
| `t-bollitore-utenze` | `bollitore.dhw_out` → `utenze-sanitarie.a` | `acs` | F7 |

### Reti

| Rete | Fluido | Frase |
|---|---|---|
| `primario` | `heating_water` | F1, F2 (nasce dalla pompa di calore, ne raccoglie i due rami) |
| `secondario` | `heating_water` | F5 (nasce dal volume tecnico, che separa idraulicamente) |
| `acqua-fredda` | `cold_water` | F7 (dall'acquedotto al bollitore) |
| `acs` | `domestic_hot_water` | F7 (dal bollitore alle utenze) |

Nessun elemento del grafo resta senza riga; nessuna frase del testo resta senza
rappresentazione o senza assunzione che la copra.

## C. Controlli del §9

| Controllo | Esito |
|---|---|
| Il JSON carica con lo strumento di validazione | sì, nessun output |
| Ogni `definition_id` esiste in catalogo, nessuno è ferramenta | sì (9 su 9) |
| Ogni attacco esiste, nessun attacco porta due tubazioni, nessuna tubazione tocca uno `stub` | sì (11 tubazioni, 22 estremità, tutte distinte) |
| Ogni tubazione va da `out` a `in`, sullo stesso fluido della rete | sì |
| Nessun attacco `required: true` è rimasto libero | sì |
| I `tag` sono tutti `null` (il testo non scrive sigle) | sì |
| `subsystems`, `rule_applications`, `sheets` sono liste vuote | sì |
