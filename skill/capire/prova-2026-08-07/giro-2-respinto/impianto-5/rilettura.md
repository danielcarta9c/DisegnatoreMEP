# Tabella di rilettura — Esempio 5, tre pompe di calore con più circuiti secondari

Due letture incrociate, come chiede il §8 passo 6.

- **Tabella 1 — dal testo al grafo:** ogni frase del testo, e gli elementi del grafo che
  la rappresentano (o la voce di `assumptions` che la copre).
- **Tabella 2 — dal grafo al testo:** ogni componente e ogni tubazione, e la frase da cui
  nasce. Nessun elemento resta senza frase.

---

## Tabella 1 — dal testo al grafo

| # | Frase del testo | Cosa la rappresenta nel grafo | Assunzioni |
|---|---|---|---|
| F1 | «La centrale termica è composta da tre pompe di calore aria-acqua reversibili da 35 kW ciascuna…» | `pdc-1`, `pdc-2`, `pdc-3` (`heat-pump-air-water`), ciascuna con `potenza: "35 kW"` e `tipo: "aria-acqua reversibile"`. Somma 105 kW > 35 → `plant_regime: "over_35_kw"` | a01 (reversibilità e raffrescamento) |
| F2 | «…installate in parallelo…» | Mandata: `rc-mandata-pdc-1`, `rc-mandata-pdc-2` (due raccordi a T in catena, N−1 con N=3) — `p01`…`p04`. Ritorno: `rip-ritorno-pdc-1`, `rip-ritorno-pdc-2` (due ripartizioni a T) — `p10`…`p14` | a03 (il testo non dice con che pezzo) |
| F3 | «…e gestite in cascata.» | Nulla: è regolazione, non topologia | a02 |
| F4 | «Le pompe di calore alimentano un volume tecnico da 500 litri a quattro tubi…» | `volano` (`buffer-four-port`: mestieri `hydraulic_separation` + `thermal_storage`, quattro attacchi di flusso), `volume: "500 litri"`, `configurazione: "a quattro tubi"`. Mandata primaria `p06`, ritorno primario `p08` | — |
| F5 | «…utilizzato come accumulo inerziale e punto di separazione tra il circuito dei generatori e i circuiti dell'edificio.» | La scelta stessa della voce (che dichiara i due mestieri) e la divisione in reti: `circuito-generatori` sul primario, `distribuzione-secondaria` + i tre circuiti sul secondario | a16 (divisione in reti) |
| F6 | «Dal volume tecnico partono tre circuiti secondari indipendenti…» | Mandata: `rip-mandata-secondari-1`, `rip-mandata-secondari-2` (`p15`, `p16` e le tre partenze `p19`, `p22`, `p25`). Ritorno: `rc-ritorno-secondari-1`, `rc-ritorno-secondari-2` (`p17`, `p18`, `p21`, `p24`, `p30`). Tre reti distinte: `circuito-uta`, `circuito-fan-coil`, `circuito-pavimento` | a05 (non è detto con che pezzo si staccano) |
| F7 | «…un circuito per le batterie calde e fredde delle unità di trattamento aria;» | Rete `circuito-uta`; `batteria-uta` (`ahu-coil`, `emission`), `p19`–`p21` | a07 (una batteria rappresentativa; quante sono? calde e fredde sullo stesso circuito?), a01 (il circuito porta anche il freddo) |
| F8 | «…un circuito per i fan-coil;» | Rete `circuito-fan-coil`; `fan-coil` (`fan-coil`, `emission`), `p22`–`p24` | a08 (un terminale rappresentativo, numero non detto), a01 |
| F9 | «…un circuito miscelato dedicato al pavimento radiante, utilizzato solo in riscaldamento.» | Rete `circuito-pavimento`; `vmr-pavimento` (`mixing-valve-3way`, `circuit_mixing`), `pavimento-radiante` (`underfloor-panel`) con `impiego: "utilizzato solo in riscaldamento"`, `rip-ritorno-pavimento` per l'acqua di miscelazione; `p25`–`p30` | a09 (un pannello rappresentativo), a10 (da dove prende l'acqua di miscelazione) |
| F10 | «Ogni circuito è dotato del proprio circolatore.» | `cir-uta`, `cir-fan-coil`, `cir-pavimento` (`pump-circulator`), sulla mandata di ciascun circuito: `p19`/`p20`, `p22`/`p23`, `p26`/`p27` | a06 (posizione convenzionale), a04 (sul primario nessun circolatore separato: la pompa di calore lo porta a bordo) |
| F11 | «La produzione di ACS è centralizzata mediante un bollitore da 500 litri alimentato dalle pompe di calore.» | `bollitore` (`dhw-cylinder`, `dhw_storage`, `stored_medium: domestic_hot_water`), `volume: "500 litri"`; alimentazione dal primario `p07` (serpentino) e ritorno `p09` | — |
| F12 | «Una valvola a tre vie devia il flusso delle pompe di calore verso il serpentino del bollitore…» | `vd-acs` (`diverting-valve-3way`, `diversion`) sulla mandata comune: `p05` in ingresso, `p06` verso il volano, `p07` verso il serpentino. La confluenza dei due ritorni è `rc-ritorno-primario` (`p08`, `p09`, `p10`) | a12 (una sola valvola, sulla mandata comune) |
| F13 | «…quando è richiesta la produzione sanitaria, dando priorità all'ACS.» | Nulla: è regolazione. Sul grafo si vede la deviatrice, non la priorità | a11 |
| F14 | «L'acqua fredda sanitaria entra nella parte bassa del bollitore e l'ACS viene prelevata dalla parte alta.» | Rete `acqua-fredda`: `acquedotto` (`cold-water-inlet`, `boundary`) → `bollitore.cold_in` (`p31`). Rete `acqua-calda-sanitaria`: `bollitore.dhw_out` → … → `utenze-acs` (`dhw-draw-off`, `boundary`) (`p32`–`p34`) | a15 (acquedotto e utenze non sono nominati: sono i confini di un circuito aperto) |
| F15 | «Sull'uscita è prevista una valvola miscelatrice termostatica.» | Nulla nel grafo: `dhw_mixing` è ferramenta (§5), la aggiunge il pezzo successivo | a13 (la nomina non è persa) |
| F16 | «È presente anche un circuito di ricircolo ACS collegato al bollitore e dotato di proprio circolatore.» | Rete `ricircolo-acs`: `rip-ricircolo` (uscita dell'anello), `cir-ricircolo` (`pump-circulator-dhw`), `rc-ricircolo` (rientro sul tubo); `p33`, `p35`, `p36` | a14 (il bollitore di catalogo non ha l'attacco del ricircolo: l'anello si chiude sul tubo) |

Nessuna affermazione topologica del testo è rimasta fuori: le uniche frasi che non
producono nodi né tubi sono F3, F13 (regolazione) e F15 (ferramenta), e tutte e tre hanno
la loro voce in `assumptions`.

---

## Tabella 2 — dal grafo al testo

### Componenti (28)

| Componente | Voce di catalogo | Frase |
|---|---|---|
| `pdc-1`, `pdc-2`, `pdc-3` | `heat-pump-air-water` | F1 |
| `rc-mandata-pdc-1`, `rc-mandata-pdc-2` | `tee-junction` | F2 (parallelo, lato mandata) |
| `vd-acs` | `diverting-valve-3way` | F12 |
| `volano` | `buffer-four-port` | F4, F5 |
| `bollitore` | `dhw-cylinder` | F11 |
| `rc-ritorno-primario` | `tee-junction` | F4 + F12: due ritorni (volano e serpentino) su un attacco solo → una confluenza (§4.4) |
| `rip-ritorno-pdc-1`, `rip-ritorno-pdc-2` | `tee-split` | F2 (parallelo, lato ritorno) |
| `rip-mandata-secondari-1`, `rip-mandata-secondari-2` | `tee-split` | F6 (tre partenze dal volano) |
| `rc-ritorno-secondari-1`, `rc-ritorno-secondari-2` | `tee-junction` | F6 (tre ritorni su un attacco solo) |
| `cir-uta` | `pump-circulator` | F10 (+F7) |
| `batteria-uta` | `ahu-coil` | F7 |
| `cir-fan-coil` | `pump-circulator` | F10 (+F8) |
| `fan-coil` | `fan-coil` | F8 |
| `vmr-pavimento` | `mixing-valve-3way` | F9 («circuito miscelato») |
| `cir-pavimento` | `pump-circulator` | F10 (+F9) |
| `pavimento-radiante` | `underfloor-panel` | F9 |
| `rip-ritorno-pavimento` | `tee-split` | F9 + a10 (acqua di miscelazione dal ritorno) |
| `acquedotto` | `cold-water-inlet` | F14 |
| `utenze-acs` | `dhw-draw-off` | F14 |
| `rc-ricircolo` | `tee-junction-dhw` | F16 + a14 |
| `rip-ricircolo` | `tee-split-dhw` | F16 + a14 |
| `cir-ricircolo` | `pump-circulator-dhw` | F16 |

### Tubazioni (36)

| Tubazione | Percorso | Frase |
|---|---|---|
| `p01`, `p02`, `p03`, `p04` | mandate delle tre pompe → catena di due raccordi a T | F1, F2 |
| `p05` | mandata comune → `vd-acs` | F12 |
| `p06` | `vd-acs.out_a` → `volano.primary_in` | F4, F12 |
| `p07` | `vd-acs.out_b` → `bollitore.coil_in` | F11, F12 |
| `p08` | `volano.primary_out` → confluenza di ritorno | F4 |
| `p09` | `bollitore.coil_out` → confluenza di ritorno | F11 |
| `p10`, `p11`, `p12`, `p13`, `p14` | ritorno comune → catena di due ripartizioni → ritorni delle tre pompe | F2 |
| `p15`, `p16` | `volano.secondary_out` → catena delle due ripartizioni secondarie | F6 |
| `p17`, `p18` | catena delle due confluenze di ritorno → `volano.secondary_in` | F6 |
| `p19`, `p20`, `p21` | ripartizione → `cir-uta` → `batteria-uta` → confluenza | F7, F10 |
| `p22`, `p23`, `p24` | ripartizione → `cir-fan-coil` → `fan-coil` → confluenza | F8, F10 |
| `p25`, `p26`, `p27` | ripartizione → `vmr-pavimento` → `cir-pavimento` → `pavimento-radiante` | F9, F10 |
| `p28`, `p30` | ritorno del pavimento → ripartizione → confluenza di ritorno secondaria | F9 |
| `p29` | ripartizione sul ritorno → `vmr-pavimento.cold_in` (acqua di miscelazione) | F9 + a10 |
| `p31` | `acquedotto` → `bollitore.cold_in` | F14 |
| `p32`, `p33`, `p34` | `bollitore.dhw_out` → confluenza → ripartizione → `utenze-acs` | F14, F16 |
| `p35`, `p36` | ripartizione → `cir-ricircolo` → confluenza (anello di ricircolo) | F16 |

---

## Controllo finale (§9)

| Domanda | Esito |
|---|---|
| Il JSON carica con lo strumento di validazione? | Sì, nessun output |
| Ogni `definition_id` esiste nel catalogo? | Sì, 28 su 28 |
| Nessun mestiere della lista «ferramenta»? | Sì: solo `heat_generation`, `thermal_storage`, `hydraulic_separation`, `dhw_storage`, `diversion`, `circuit_mixing`, `circulation`, `emission`, `junction`, `boundary` |
| Ogni attacco usato esiste a catalogo? | Sì |
| Nessun attacco porta due tubazioni? | Sì, verificato: 72 estremi su 72 attacchi distinti |
| Nessuna tubazione tocca un attacco `stub`? | Sì: `vent`, `drain`, `probe` del volano e `probe` del bollitore restano liberi |
| Ogni tubazione va da `out` a `in`, sullo stesso fluido? | Sì, verificato attacco per attacco |
| Attacchi `required` rimasti liberi? | Nessuno |
| I `tag` sono tutti `null`? | Sì: l'ingegnere non ha scritto nessuna sigla |
| `subsystems`, `rule_applications`, `sheets` vuoti? | Sì |
| Regime ricavato dalle potenze? | Sì: 35 + 35 + 35 = 105 kW > 35 → `over_35_kw` |
