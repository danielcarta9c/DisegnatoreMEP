# Rilettura — Esempio 6, centrale ibrida condominiale con solare termico

Tabella di rilettura del grafo `grafo.json` (ISTRUZIONI §8, passo 6): una riga per frase del
testo, con gli elementi del grafo che la rappresentano oppure la voce di `assumptions` che la
copre. In fondo, il controllo inverso: ogni componente, ogni tubazione, ogni rete e ogni
assunzione risale ad almeno una frase.

## Le frasi del testo

| N. | Frase |
|---|---|
| T0 | «Esempio 6 – Centrale ibrida condominiale con pompa di calore di alta potenza, caldaia modulare e solare termico» (titolo) |
| F1 | «La centrale termica di un condominio è composta da una pompa di calore aria-acqua di alta potenza da 120 kW e da una caldaia modulare a condensazione da 150 kW, collegate in parallelo.» |
| F2 | «La pompa di calore lavora come generatore principale, mentre la caldaia interviene come integrazione quando serve maggiore potenza oppure temperature di mandata più alte.» |
| F3 | «I due generatori alimentano un volume tecnico da 1000 litri a quattro tubi.» |
| F4 | «Sul volume tecnico sono previsti il collegamento per il carico automatico dell’impianto da acquedotto e lo scarico.» |
| F5 | «Dal volume tecnico partono due circuiti secondari, ciascuno con il proprio circolatore:» |
| F6 | «– un circuito che alimenta i radiatori degli appartamenti;» |
| F7 | «– un circuito che alimenta i fan-coil canalizzati degli spazi comuni al piano terra.» |
| F8 | «La produzione di ACS è centralizzata con un bollitore a doppio serpentino da 1500 litri.» |
| F9 | «Il serpentino superiore è alimentato dai generatori: una valvola a tre vie sulla mandata devia il flusso verso il bollitore quando è richiesta la produzione sanitaria, dando priorità all’ACS.» |
| F10 | «Il serpentino inferiore è alimentato da un campo di collettori solari termici.» |
| F11 | «Il circuito solare ha un gruppo di circolazione con circolatore, valvola di ritegno, valvola di sicurezza, manometro e vaso di espansione solare.» |
| F12 | «L’acqua fredda sanitaria entra nella parte bassa del bollitore e l’ACS viene prelevata dalla parte alta.» |
| F13 | «Sull’uscita è prevista una valvola miscelatrice termostatica.» |
| F14 | «Non è previsto il circuito di ricircolo ACS.» |

## Tabella di rilettura

| N. | Che cosa afferma | Nel grafo | In `assumptions` |
|---|---|---|---|
| T0 | Il nome dell'impianto: i tre generatori che F1 e F10 descrivono. | `metadata.project_name`. I pezzi sono agganciati alle frasi F1 e F10. | — |
| F1 | Una pompa di calore aria-acqua **di alta potenza**, 120 kW. | `pdc` → `heat-pump-air-water-large` (variante nominata: «alta potenza»); `properties`: potenza «120 kW», tipo «aria-acqua», taglia «alta potenza». | `a-circolatori-generatori` (circolatore a bordo, dalla voce di catalogo) |
| F1 | Una caldaia **modulare** a condensazione, 150 kW. | `caldaia` → `gas-boiler-modular` (variante nominata: «modulare»); `properties`: potenza «150 kW», tipo «a condensazione», configurazione «modulare». | `a-circolatori-generatori` |
| F1 | Le potenze dei generatori. | `plant_regime: "over_35_kw"` (120 + 150 = 270 kW > 35 kW). | `a-regime` |
| F1 | «Collegate in parallelo»: i flussi si uniscono in mandata e si dividono in ritorno. | `rc-mandata-generatori` (raccordo a T) con `pr-1` (pdc → braccio `c`), `pr-2` (caldaia → passante `a`); `rip-ritorno-generatori` (ripartizione a T) con `pr-9` (braccio `c` → pdc), `pr-10` (passante `b` → caldaia). Mandata e ritorno si specchiano. | `a-parallelo` |
| F2 | Pompa di calore generatore principale, caldaia in integrazione. | Nessun nodo né tubo: è regolazione. | `a-regolazione-generatori` |
| F3 | Un volume tecnico da 1000 litri **a quattro tubi**. | `volume-tecnico` → `buffer-four-port` (quattro attacchi di flusso: primario e secondario); `properties`: volume «1000 litri», configurazione «a quattro tubi». | — |
| F3 | I due generatori alimentano il volume (circuito chiuso: mandata e ritorno). | Rete `circuito-primario` (`heating_water`), nasce dai generatori. Mandata: `pr-3` (raccordo → valvola), `pr-4` (via `out_a` della valvola → `primary_in`). Ritorno: `pr-6` (`primary_out` → raccordo di ritorno), `pr-8` (→ ripartizione sui generatori), poi `pr-9`, `pr-10`. La valvola e il raccordo di ritorno stanno su questo percorso per F9. | — |
| F4 | Carico automatico da acquedotto e scarico sul volume tecnico. | Non disegnati: ferramenta (`filling`, `drain`). Gli attacchi di servizio `vent`, `drain`, `probe` del volume restano liberi. | `a-carico-scarico-volume` |
| F5 | Dal volume partono due circuiti secondari (due rami di una rete). | Rete `circuito-secondario` (`heating_water`), nasce dal volume. `se-1` (`secondary_out` → `rip-mandata-secondario`), `se-8` (`rc-ritorno-secondario` → `secondary_in`). | `a-circuiti-secondari` |
| F5 | Ciascun circuito con il proprio circolatore. | `circolatore-radiatori` (`pump-circulator`) fra `se-2` e `se-3`; `circolatore-fancoil` (`pump-circulator`) fra `se-5` e `se-6`: uno per ramo, sulla mandata. | `a-circolatori-secondari` |
| F6 | Primo ramo: radiatori degli appartamenti. | `radiatori` → `radiator` (`properties`: zona «appartamenti»). Mandata `se-2` (braccio `c` della ripartizione → circolatore), `se-3` (circolatore → radiatori); ritorno `se-4` (radiatori → braccio `c` del raccordo). | `a-radiatori` |
| F7 | Secondo ramo: fan-coil **canalizzati** degli spazi comuni al piano terra. | `fancoil` → `fan-coil-ducted` (variante nominata: «canalizzati»); `properties`: tipo «canalizzati», zona «spazi comuni al piano terra». Mandata `se-5` (passante `b` → circolatore), `se-6`; ritorno `se-7` (→ passante `a` del raccordo). | `a-fancoil` |
| F8 | ACS centralizzata con bollitore a doppio serpentino da 1500 litri. | `bollitore` → `dhw-cylinder-twin-coil` (l'unica voce con gli attacchi `solar_coil_in`/`solar_coil_out`); `properties`: volume «1500 litri», configurazione «a doppio serpentino», produzione «centralizzata» (§4.5). | — |
| F9 | Il serpentino superiore è alimentato dai generatori. | Serpentino superiore = attacchi `coil_in`/`coil_out` (`heating_water`), sulla rete `circuito-primario`: `pr-5` (valvola `out_b` → `coil_in`), `pr-7` (`coil_out` → braccio `c` di `rc-ritorno-primario`), poi `pr-8`, `pr-9`, `pr-10` ai generatori. | `a-ritorno-serpentino` (dove rientra il ritorno) |
| F9 | Una valvola a tre vie sulla mandata devia il flusso verso il bollitore; priorità ACS. | `valvola-deviatrice` → `diverting-valve-3way` (mestiere `diversion`, un ingresso e due uscite) sulla mandata comune: `pr-3` (raccordo di mandata → `in`), `pr-4` (`out_a` → volume), `pr-5` (`out_b` → bollitore). La priorità non ha nodi. | `a-priorita-acs` |
| F10 | Il serpentino inferiore è alimentato da un campo di collettori solari. | `collettore-solare` → `solar-collector` (`properties`: descrizione «campo di collettori solari termici»). Rete `circuito-solare` (`solar_fluid`), nasce dal collettore: mandata `so-1` (`supply` → `solar_coil_in`); ritorno chiuso da `solar_coil_out` a `return` con `so-2`…`so-7`. Serpentino inferiore = attacchi `solar_coil_*`. | `a-collettori-solari`; `a-regime` (potenza del campo non data) |
| F11 | Gruppo di circolazione solare: circolatore, valvola di ritegno, valvola di sicurezza, manometro, vaso di espansione solare. | Sul ritorno ai collettori, nel verso del flusso: `circolatore-solare` (`pump-circulator-solar`, `so-2`, `so-3`), `ritegno-solare` (`valve-check-solar`, `so-3`, `so-4`), `der-sicurezza-solare` + `sicurezza-solare` (`tee-branch-solar` + `valve-safety-solar`, `so-4`, `so-5`, `so-8`), `der-manometro-solare` + `manometro-solare` (`tee-branch-solar` + `pressure-gauge-solar`, `so-5`, `so-6`, `so-9`), `der-vaso-solare` + `vaso-solare` (`tee-branch-solar` + `expansion-connection-solar`, `so-6`, `so-7`, `so-10`). Nessun gruppo di riempimento da acquedotto. | `a-gruppo-solare-posizione`; `a-gruppo-solare-mancanti` |
| F12 | L'acqua fredda entra in basso nel bollitore. | Rete `rete-acqua-fredda` (`cold_water`), nasce dal confine `alimentazione-af` (`cold-water-inlet`): `af-1` → `cold_in`. «In basso» è la posizione dell'attacco `cold_in` nel simbolo, non un dato del grafo. | — |
| F12 | L'ACS si preleva in alto. | Rete `rete-acs` (`domestic_hot_water`), nasce dal bollitore: `acs-1` (`dhw_out` → confine `utenze-acs`, `dhw-draw-off`). «In alto» è la posizione dell'attacco `dhw_out` nel simbolo. | — |
| F13 | Miscelatrice termostatica sull'uscita dell'ACS. | Non disegnata: ferramenta (`dhw_mixing`). `acs-1` va diretto dal bollitore alle utenze. | `a-miscelatrice` |
| F14 | Nessun ricircolo ACS. | Nessun confine `dhw-recirculation-inlet`, nessun circolatore sanitario; l'attacco `recirculation_in` del bollitore resta libero (la voce lo dichiara tappato quando non usato). | `a-no-ricircolo` |

Nota su F9 e F10: «superiore» e «inferiore» il grafo non li scrive; li scrive la scelta degli
attacchi (generatori su `coil_in`/`coil_out`, solare su `solar_coil_in`/`solar_coil_out`). Che il
serpentino solare stia in basso è compito del simbolo `dhw-cylinder-twin-coil`: in tavola va
controllato.

## Controllo inverso: ogni elemento del grafo e la sua frase

### Componenti (25)

| Componente | Voce di catalogo | Frase |
|---|---|---|
| `pdc` | `heat-pump-air-water-large` | F1 |
| `caldaia` | `gas-boiler-modular` | F1 |
| `rc-mandata-generatori` | `tee-junction` | F1 («in parallelo») |
| `rip-ritorno-generatori` | `tee-split` | F1 («in parallelo»), F3 (circuito chiuso) |
| `valvola-deviatrice` | `diverting-valve-3way` | F9 |
| `volume-tecnico` | `buffer-four-port` | F3 |
| `bollitore` | `dhw-cylinder-twin-coil` | F8 |
| `rc-ritorno-primario` | `tee-junction` | F9 (ritorno del serpentino superiore ai generatori) |
| `rip-mandata-secondario` | `tee-split` | F5 |
| `rc-ritorno-secondario` | `tee-junction` | F5 |
| `circolatore-radiatori` | `pump-circulator` | F5, F6 |
| `radiatori` | `radiator` | F6 |
| `circolatore-fancoil` | `pump-circulator` | F5, F7 |
| `fancoil` | `fan-coil-ducted` | F7 |
| `collettore-solare` | `solar-collector` | F10 |
| `circolatore-solare` | `pump-circulator-solar` | F11 |
| `ritegno-solare` | `valve-check-solar` | F11 |
| `der-sicurezza-solare` | `tee-branch-solar` | F11 |
| `sicurezza-solare` | `valve-safety-solar` | F11 |
| `der-manometro-solare` | `tee-branch-solar` | F11 |
| `manometro-solare` | `pressure-gauge-solar` | F11 |
| `der-vaso-solare` | `tee-branch-solar` | F11 |
| `vaso-solare` | `expansion-connection-solar` | F11 |
| `alimentazione-af` | `cold-water-inlet` | F12 |
| `utenze-acs` | `dhw-draw-off` | F12 |

### Tubazioni (30)

| Tubazione | Rete | Da (porta `out`) | A (porta `in`) | Frase |
|---|---|---|---|---|
| `pr-1` | `circuito-primario` | `pdc.water_supply` | `rc-mandata-generatori.c` | F1 |
| `pr-2` | `circuito-primario` | `caldaia.water_supply` | `rc-mandata-generatori.a` | F1 |
| `pr-3` | `circuito-primario` | `rc-mandata-generatori.b` | `valvola-deviatrice.in` | F3, F9 |
| `pr-4` | `circuito-primario` | `valvola-deviatrice.out_a` | `volume-tecnico.primary_in` | F3, F9 |
| `pr-5` | `circuito-primario` | `valvola-deviatrice.out_b` | `bollitore.coil_in` | F9 |
| `pr-6` | `circuito-primario` | `volume-tecnico.primary_out` | `rc-ritorno-primario.a` | F3 |
| `pr-7` | `circuito-primario` | `bollitore.coil_out` | `rc-ritorno-primario.c` | F9 |
| `pr-8` | `circuito-primario` | `rc-ritorno-primario.b` | `rip-ritorno-generatori.a` | F3, F9 |
| `pr-9` | `circuito-primario` | `rip-ritorno-generatori.c` | `pdc.water_return` | F1, F3 |
| `pr-10` | `circuito-primario` | `rip-ritorno-generatori.b` | `caldaia.water_return` | F1, F3 |
| `se-1` | `circuito-secondario` | `volume-tecnico.secondary_out` | `rip-mandata-secondario.a` | F5 |
| `se-2` | `circuito-secondario` | `rip-mandata-secondario.c` | `circolatore-radiatori.a` | F5, F6 |
| `se-3` | `circuito-secondario` | `circolatore-radiatori.b` | `radiatori.in` | F6 |
| `se-4` | `circuito-secondario` | `radiatori.out` | `rc-ritorno-secondario.c` | F6 |
| `se-5` | `circuito-secondario` | `rip-mandata-secondario.b` | `circolatore-fancoil.a` | F5, F7 |
| `se-6` | `circuito-secondario` | `circolatore-fancoil.b` | `fancoil.in` | F7 |
| `se-7` | `circuito-secondario` | `fancoil.out` | `rc-ritorno-secondario.a` | F7 |
| `se-8` | `circuito-secondario` | `rc-ritorno-secondario.b` | `volume-tecnico.secondary_in` | F5 |
| `so-1` | `circuito-solare` | `collettore-solare.supply` | `bollitore.solar_coil_in` | F10 |
| `so-2` | `circuito-solare` | `bollitore.solar_coil_out` | `circolatore-solare.a` | F10, F11 |
| `so-3` | `circuito-solare` | `circolatore-solare.b` | `ritegno-solare.a` | F11 |
| `so-4` | `circuito-solare` | `ritegno-solare.b` | `der-sicurezza-solare.a` | F11 |
| `so-5` | `circuito-solare` | `der-sicurezza-solare.b` | `der-manometro-solare.a` | F11 |
| `so-6` | `circuito-solare` | `der-manometro-solare.b` | `der-vaso-solare.a` | F11 |
| `so-7` | `circuito-solare` | `der-vaso-solare.b` | `collettore-solare.return` | F10, F11 |
| `so-8` | `circuito-solare` | `der-sicurezza-solare.branch` (stacco) | `sicurezza-solare.a` | F11 |
| `so-9` | `circuito-solare` | `der-manometro-solare.branch` (stacco) | `manometro-solare.a` | F11 |
| `so-10` | `circuito-solare` | `der-vaso-solare.branch` (stacco) | `vaso-solare.a` | F11 |
| `af-1` | `rete-acqua-fredda` | `alimentazione-af.a` | `bollitore.cold_in` | F12 |
| `acs-1` | `rete-acs` | `bollitore.dhw_out` | `utenze-acs.a` | F12 |

`so-8`, `so-9`, `so-10` collegano due attacchi bidirezionali (lo stacco della derivazione e il
pezzo appeso): il verso «da `out` a `in`» lì non si applica, e il capo `endpoint_a` è la
derivazione.

### Reti (5)

| Rete | Fluido | Nasce da | Frase |
|---|---|---|---|
| `circuito-primario` | `heating_water` | i generatori `pdc` e `caldaia` | F1, F3, F9 |
| `circuito-secondario` | `heating_water` | il volume tecnico | F5, F6, F7 |
| `circuito-solare` | `solar_fluid` | il collettore solare | F10, F11 |
| `rete-acqua-fredda` | `cold_water` | il confine `alimentazione-af` | F12 |
| `rete-acs` | `domestic_hot_water` | il bollitore | F12 |

### Assunzioni (16)

| Assunzione | Frase |
|---|---|
| `a-regime` | F1, F10 |
| `a-circolatori-generatori` | F1 |
| `a-parallelo` | F1 |
| `a-regolazione-generatori` | F2 |
| `a-carico-scarico-volume` | F4 |
| `a-circuiti-secondari` | F5 |
| `a-circolatori-secondari` | F5 |
| `a-radiatori` | F6 |
| `a-fancoil` | F7 |
| `a-priorita-acs` | F9 |
| `a-ritorno-serpentino` | F9 |
| `a-collettori-solari` | F10 |
| `a-gruppo-solare-posizione` | F11 |
| `a-gruppo-solare-mancanti` | F11 |
| `a-miscelatrice` | F13 |
| `a-no-ricircolo` | F14 |

Esito: ogni frase del testo è rappresentata nel grafo o coperta da una voce di `assumptions`;
ogni componente, tubazione, rete e assunzione del grafo risale ad almeno una frase. Nessun
elemento è rimasto senza riga.
