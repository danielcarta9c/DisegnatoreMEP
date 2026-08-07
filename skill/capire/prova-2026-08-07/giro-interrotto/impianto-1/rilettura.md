# Tabella di rilettura — Esempio 1

Impianto: due pompe di calore in parallelo con accumulo combinato.
File del grafo: `consegna/grafo.json` (9 componenti, 4 reti, 11 tubazioni, 10 assunzioni).

## A. Dal testo al grafo — una riga per affermazione

| # | Frase del testo (o suo pezzo) | Cosa la rappresenta nel grafo | Voce di `assumptions` che la copre |
|---|---|---|---|
| T | Titolo: «Due pompe di calore in parallelo con accumulo combinato» | `metadata.project_name`, `metadata.project_id` | — |
| 1a | «due pompe di calore aria-acqua…» | `pdc-1`, `pdc-2` (`heat-pump-air-water`, mestiere `heat_generation`); `properties.tipo = "aria-acqua"` | — |
| 1b | «…da 12 kW ciascuna» | `properties.potenza = "12 kW"` su entrambe; `plant_regime = "up_to_35_kw"` (12+12 = 24 ≤ 35) | `a10` (quale potenza si è sommata) |
| 1c | «installate in parallelo» | `rc-mandata-generatori` (`tee-junction`) su `p1`+`p2`→`p3`; `rip-ritorno-generatori` (`tee-split`) su `p4`→`p5`+`p6`. N=2 → 1 confluenza in mandata, 1 ripartizione in ritorno | `a1` (il testo non dice con che pezzo) |
| 1d | «gestite una come master e una come slave» | nulla: è regolazione, non topologia | `a2` |
| 2a | «Le due macchine alimentano un accumulo…» | `p1`, `p2`, `p3`: mandata delle due PdC → raccordo → `volume-tecnico.primary_in`; ritorno `p4`, `p5`, `p6` da `volume-tecnico.primary_out` alle due PdC. Rete `primario` (`heating_water`) | `a3` (nessun circolatore primario a sé: la voce di catalogo lo porta a bordo); `a7` per la chiusura del circuito |
| 2b | «…ECOcombi da 200 litri» | `volume-tecnico`: `properties.modello = "ECOcombi"`, `properties.volume = "200 litri"` | — |
| 2c | «volume tecnico a quattro tubi per il riscaldamento» | scelta della voce `buffer-combined` (mestieri `hydraulic_separation` + `thermal_storage`, `stored_medium: heating_water`) e uso dei suoi quattro attacchi di flusso: `primary_in`, `primary_out`, `secondary_out`, `secondary_in`; `properties.configurazione = "a quattro tubi"` | `a4` (come si è letto «a quattro tubi») |
| 2d | «produzione istantanea di acqua calda sanitaria tramite serpentino interno» | attacchi `cold_in` e `dhw_out` della stessa voce `buffer-combined`, usati da `p10` e `p11`; `properties.produzione_sanitaria` | `a4` (il serpentino è dentro la macchina, non è uno scambiatore a sé) |
| 3a | «dal volume tecnico parte un circuito secondario» | rete `secondario` (`heating_water`); `p7` da `volume-tecnico.secondary_out` | `a7` (il circuito si chiude sul ritorno) |
| 3b | «con circolatore dedicato» | `circolatore-secondario` (`pump-circulator`, mestiere `circulation`), su `p7`→`p8` | `a5` (posizione sulla mandata: convenzione dichiarata) |
| 3c | «alimenta direttamente l'impianto esistente a radiatori» | `radiatori` (`radiator`, mestiere `emission`); `p8` in ingresso, `p9` in ritorno su `volume-tecnico.secondary_in`. «Direttamente» = nessun pezzo interposto fra circolatore e terminali | `a6` (quanti radiatori sono davvero) |
| 4a | «l'acqua fredda di acquedotto entra nel serpentino interno» | `acquedotto` (`cold-water-inlet`, mestiere `boundary`); rete `acqua-fredda` (`cold_water`); `p10` → `volume-tecnico.cold_in` | — |
| 4b | «l'ACS viene prelevata in uscita» | `utenze-sanitarie` (`dhw-draw-off`, mestiere `boundary`); rete `acs` (`domestic_hot_water`); `p11` da `volume-tecnico.dhw_out` | — |
| 4c | «Non è previsto ricircolo sanitario» | nulla nel grafo, di proposito: nessuna pompa di ricircolo, nessun anello | `a8` |
| 5 | «Sul volume tecnico… il carico automatico dell'impianto da acquedotto e lo scarico» | nulla nel grafo: sono ferramenta (`filling`, `drain`). Gli attacchi di servizio `vent`, `drain`, `probe` del volume restano liberi apposta | `a9` |

Nessuna affermazione del testo è rimasta fuori da questa tabella.

## B. Dal grafo al testo — ogni elemento risale a una frase

| Elemento del grafo | Voce di catalogo / fluido | Frase che lo giustifica |
|---|---|---|
| `pdc-1` | `heat-pump-air-water` | 1a, 1b |
| `pdc-2` | `heat-pump-air-water` | 1a, 1b |
| `volume-tecnico` | `buffer-combined` | 2b, 2c, 2d |
| `rc-mandata-generatori` | `tee-junction` | 1c (topologia imposta dal «in parallelo») |
| `rip-ritorno-generatori` | `tee-split` | 1c (idem, sul ritorno) |
| `circolatore-secondario` | `pump-circulator` | 3b |
| `radiatori` | `radiator` | 3c |
| `acquedotto` | `cold-water-inlet` | 4a |
| `utenze-sanitarie` | `dhw-draw-off` | 4b |
| rete `primario` | `heating_water` | 2a |
| rete `secondario` | `heating_water` | 3a |
| rete `acqua-fredda` | `cold_water` | 4a |
| rete `acs` | `domestic_hot_water` | 4b |
| `p1` pdc-1.water_supply → rc.a | `heating_water` | 1c, 2a |
| `p2` pdc-2.water_supply → rc.c | `heating_water` | 1c, 2a |
| `p3` rc.b → volume.primary_in | `heating_water` | 2a |
| `p4` volume.primary_out → rip.a | `heating_water` | 2a (ritorno del primario) |
| `p5` rip.b → pdc-1.water_return | `heating_water` | 1c, 2a |
| `p6` rip.c → pdc-2.water_return | `heating_water` | 1c, 2a |
| `p7` volume.secondary_out → circolatore.a | `heating_water` | 3a, 3b |
| `p8` circolatore.b → radiatori.in | `heating_water` | 3b, 3c |
| `p9` radiatori.out → volume.secondary_in | `heating_water` | 3c (ritorno del secondario) |
| `p10` acquedotto.a → volume.cold_in | `cold_water` | 4a |
| `p11` volume.dhw_out → utenze.a | `domestic_hot_water` | 4b |

Nessun elemento del grafo è privo di una frase alle spalle.

## C. Controlli di chiusura

- Il file carica con lo strumento di validazione (nessun output).
- Ogni `definition_id` esiste in catalogo; nessuno ha un mestiere della lista «ferramenta».
- Ogni attacco usato esiste in catalogo; nessun attacco porta due tubazioni; nessuna tubazione tocca un attacco `stub` (`vent`, `drain`, `probe` del volume restano liberi).
- Ogni tubazione va da una porta `out` a una porta `in`, e i due estremi hanno il fluido della propria rete.
- Nessun attacco `required` è rimasto libero: `pdc-1`, `pdc-2` (2 su 2 ciascuna), `volume-tecnico` (6 su 6 obbligatori), `circolatore-secondario`, `radiatori`, `acquedotto`, `utenze-sanitarie`, e i tre attacchi di ciascun raccordo.
- Tutti i `tag` sono `null`: il testo non scrive nessuna sigla.
- `subsystems`, `rule_applications`, `sheets` sono liste vuote.
