# Rilettura — prova 6, centrale ibrida condominiale con solare termico

Tabella di rilettura del §8, passo 6: una riga per frase del testo, con gli elementi di
`grafo.json` che la rappresentano oppure la voce di `assumptions` che la copre. Sotto, la
verifica inversa: ogni componente e ogni tubazione del grafo, con la riga da cui nasce.

Convenzioni della tabella: i componenti sono scritti con il loro `id` e la voce di catalogo
(`id` = `definition_id`); le tubazioni come `id` (porta di uscita → porta di ingresso); le
assunzioni con il loro `id` (`a01`…`a16`).

## 1. Frase per frase

| # | Frase del testo | Elementi del grafo | Assunzioni |
|---|---|---|---|
| F0 | «Esempio 6 – Centrale ibrida condominiale con pompa di calore di alta potenza, caldaia modulare e solare termico» | `metadata.project_name`. Il titolo nomina le varianti «alta potenza» e «modulare» che F1 ripete: nessun elemento proprio. | — |
| F1 | «La centrale termica di un condominio è composta da una pompa di calore aria-acqua di alta potenza da 120 kW e da una caldaia modulare a condensazione da 150 kW, collegate in parallelo.» | «pompa di calore aria-acqua di alta potenza da 120 kW» → `pdc` = `heat-pump-air-water-large` (`potenza` «120 kW», `tipo` «aria-acqua di alta potenza»).<br>«caldaia modulare a condensazione da 150 kW» → `caldaia` = `gas-boiler-modular` (`potenza` «150 kW», `tipo` «modulare a condensazione»).<br>Le due potenze → `plant_regime` = `over_35_kw` (120 + 150 = 270 kW).<br>«collegate in parallelo» → rete `primario`; confluenza `rc-mandata-generatori` = `tee-junction` con `p01` (pdc.water_supply → c) e `p02` (caldaia.water_supply → a); ripartizione `rip-ritorno-generatori` = `tee-split` con `p09` (c → pdc.water_return) e `p10` (b → caldaia.water_return). La pompa di calore, nominata per prima, sta sul braccio `c` di entrambi i raccordi: mandata e ritorno si specchiano. | `a01-regime`, `a02-circolatori-generatori`, `a03-parallelo-generatori` |
| F2 | «La pompa di calore lavora come generatore principale, mentre la caldaia interviene come integrazione quando serve maggiore potenza oppure temperature di mandata più alte.» | Nessun elemento: è logica di regolazione. | `a04-regolazione-generatori` |
| F3 | «I due generatori alimentano un volume tecnico da 1000 litri a quattro tubi.» | `volume-tecnico` = `buffer-four-port` (`volume` «1000 litri», `configurazione` «a quattro tubi»): i quattro tubi sono gli attacchi primary_in/primary_out (lato generatori) e secondary_out/secondary_in (lato circuiti).<br>Lato generatori, rete `primario`: `p03` (rc-mandata-generatori.b → deviatrice-acs.in), `p04` (deviatrice-acs.out_a → volume-tecnico.primary_in), `p06` (volume-tecnico.primary_out → rc-ritorno-primario.a), `p08` (rc-ritorno-primario.b → rip-ritorno-generatori.a). | `a02-circolatori-generatori` (nessun circolatore separato fra generatori e volume) |
| F4 | «Sul volume tecnico sono previsti il collegamento per il carico automatico dell’impianto da acquedotto e lo scarico.» | Nessun elemento: carico e scarico sono ferramenta (mestieri `filling`, `drain`). L'attacco `volume-tecnico.drain` è uno stub e resta libero per il pezzo successivo. | `a05-carico-scarico-volume` |
| F5 | «Dal volume tecnico partono due circuiti secondari, ciascuno con il proprio circolatore:» | Rete `secondario` (una rete, due rami, perché nascono entrambi dal volume).<br>Ripartizione `rip-mandata-secondario` = `tee-split` con `s01` (volume-tecnico.secondary_out → a); confluenza `rc-ritorno-secondario` = `tee-junction` con `s08` (b → volume-tecnico.secondary_in).<br>«ciascuno con il proprio circolatore» → `circolatore-radiatori` e `circolatore-fancoil` = `pump-circulator`, uno per ramo, sulla mandata. | `a06-ripartizione-secondari`, `a07-circolatori-secondari` |
| F6 | «un circuito che alimenta i radiatori degli appartamenti;» | Ramo 1, primo in elenco, sul braccio `c` di entrambi i raccordi: `s02` (rip-mandata-secondario.c → circolatore-radiatori.a), `s03` (circolatore-radiatori.b → radiatori.in), `s04` (radiatori.out → rc-ritorno-secondario.c).<br>`radiatori` = `radiator` (`servizio` «appartamenti»), terminale rappresentativo. | `a07-circolatori-secondari`, `a08-terminali-rappresentativi` |
| F7 | «un circuito che alimenta i fan-coil canalizzati degli spazi comuni al piano terra.» | Ramo 2, sul passaggio diritto di entrambi i raccordi: `s05` (rip-mandata-secondario.b → circolatore-fancoil.a), `s06` (circolatore-fancoil.b → fancoil.in), `s07` (fancoil.out → rc-ritorno-secondario.a).<br>`fancoil` = `fan-coil-ducted` (variante nominata da «canalizzati»; `tipo` «canalizzati», `servizio` «spazi comuni al piano terra»), terminale rappresentativo. | `a07-circolatori-secondari`, `a08-terminali-rappresentativi` |
| F8 | «La produzione di ACS è centralizzata con un bollitore a doppio serpentino da 1500 litri.» | `bollitore` = `dhw-cylinder-twin-coil` (`volume` «1500 litri», `configurazione` «a doppio serpentino», `produzione` «centralizzata»). | — |
| F9 | «Il serpentino superiore è alimentato dai generatori: una valvola a tre vie sulla mandata devia il flusso verso il bollitore quando è richiesta la produzione sanitaria, dando priorità all’ACS.» | «serpentino superiore … alimentato dai generatori» → attacchi `bollitore.coil_in` / `bollitore.coil_out` (acqua di riscaldamento), sulla rete `primario`.<br>«una valvola a tre vie sulla mandata devia il flusso verso il bollitore» → `deviatrice-acs` = `diverting-valve-3way` sulla mandata comune: `p03` (rc-mandata-generatori.b → in), `p04` (out_a → volume-tecnico.primary_in), `p05` (out_b → bollitore.coil_in).<br>Ritorno del serpentino, per chiudere il circuito sui generatori: `p07` (bollitore.coil_out → rc-ritorno-primario.c), confluenza `rc-ritorno-primario` = `tee-junction`, `p08` (b → rip-ritorno-generatori.a).<br>«dando priorità all’ACS» → nessun elemento: regolazione. | `a09-deviatrice-priorita`, `a10-ritorno-serpentino-superiore` |
| F10 | «Il serpentino inferiore è alimentato da un campo di collettori solari termici.» | «serpentino inferiore» → attacchi `bollitore.solar_coil_in` / `bollitore.solar_coil_out` (fluido solare).<br>Rete `solare`; `collettori-solari` = `solar-collector` (`configurazione` «campo di collettori solari termici»), collettore rappresentativo.<br>Andata: `q01` (collettori-solari.supply → circolatore-solare.a) … `q09` (der-vaso-solare.b → bollitore.solar_coil_in); ritorno: `q10` (bollitore.solar_coil_out → collettori-solari.return). | `a11-campo-solare`, `a12-posizione-gruppo-solare` |
| F11 | «Il circuito solare ha un gruppo di circolazione con circolatore, valvola di ritegno, valvola di sicurezza, manometro e vaso di espansione solare.» | Nell'ordine del testo e nel verso del flusso, sull'andata del circuito solare:<br>«circolatore» → `circolatore-solare` = `pump-circulator-solar` (`q01`, `q02`);<br>«valvola di ritegno» → `ritegno-solare` = `valve-check-solar` (`q02`, `q03`);<br>«valvola di sicurezza» → `der-sicurezza-solare` = `tee-branch-solar` + `sicurezza-solare` = `valve-safety-solar` (`q03`, `q04` sul braccio, `q05`);<br>«manometro» → `der-manometro-solare` = `tee-branch-solar` + `manometro-solare` = `pressure-gauge-solar` (`q05`, `q06` sul braccio, `q07`);<br>«vaso di espansione solare» → `der-vaso-solare` = `tee-branch-solar` + `vaso-solare` = `expansion-connection-solar` (`q07`, `q08` sul braccio, `q09`). | `a12-posizione-gruppo-solare`, `a13-attacco-accessori-solari`, `a14-solare-pezzi-non-descritti` |
| F12 | «L’acqua fredda sanitaria entra nella parte bassa del bollitore e l’ACS viene prelevata dalla parte alta.» | «acqua fredda sanitaria entra … nel bollitore» → rete `acqua-fredda`; `acquedotto` = `cold-water-inlet`; `f01` (acquedotto.a → bollitore.cold_in, l'attacco da cui il bollitore si riempie).<br>«l’ACS viene prelevata» → rete `acs`; `utenze-acs` = `dhw-draw-off`; `h01` (bollitore.dhw_out → utenze-acs.a).<br>«parte bassa», «parte alta»: gli attacchi del catalogo non portano la quota; la posizione è quella che il simbolo del bollitore dà a `cold_in` e `dhw_out`. | — |
| F13 | «Sull’uscita è prevista una valvola miscelatrice termostatica.» | Nessun elemento: è la miscelatrice sanitaria (mestiere `dhw_mixing`, ferramenta). | `a15-miscelatrice-termostatica` |
| F14 | «Non è previsto il circuito di ricircolo ACS.» | Nessun elemento: esclusione esplicita. L'attacco `bollitore.recirculation_in` resta libero (il catalogo lo dà tappato quando non si usa). | `a16-ricircolo-escluso` |

## 2. Verifica inversa: ogni elemento del grafo risale a una frase

### Componenti (25)

| Componente | Voce di catalogo | Righe |
|---|---|---|
| `pdc` | `heat-pump-air-water-large` | F1 |
| `caldaia` | `gas-boiler-modular` | F1 |
| `rc-mandata-generatori` | `tee-junction` | F1, F9 |
| `rip-ritorno-generatori` | `tee-split` | F1, F3 |
| `deviatrice-acs` | `diverting-valve-3way` | F9 |
| `volume-tecnico` | `buffer-four-port` | F3, F5 |
| `rc-ritorno-primario` | `tee-junction` | F9, F3 |
| `bollitore` | `dhw-cylinder-twin-coil` | F8, F9, F10, F12 |
| `rip-mandata-secondario` | `tee-split` | F5 |
| `rc-ritorno-secondario` | `tee-junction` | F5 |
| `circolatore-radiatori` | `pump-circulator` | F5, F6 |
| `radiatori` | `radiator` | F6 |
| `circolatore-fancoil` | `pump-circulator` | F5, F7 |
| `fancoil` | `fan-coil-ducted` | F7 |
| `collettori-solari` | `solar-collector` | F10 |
| `circolatore-solare` | `pump-circulator-solar` | F11 |
| `ritegno-solare` | `valve-check-solar` | F11 |
| `der-sicurezza-solare` | `tee-branch-solar` | F11 |
| `sicurezza-solare` | `valve-safety-solar` | F11 |
| `der-manometro-solare` | `tee-branch-solar` | F11 |
| `manometro-solare` | `pressure-gauge-solar` | F11 |
| `der-vaso-solare` | `tee-branch-solar` | F11 |
| `vaso-solare` | `expansion-connection-solar` | F11 |
| `acquedotto` | `cold-water-inlet` | F12 |
| `utenze-acs` | `dhw-draw-off` | F12 |

### Tubazioni (30)

| Tubazione | Rete | Da → a | Righe |
|---|---|---|---|
| `p01` | `primario` | pdc.water_supply → rc-mandata-generatori.c | F1 |
| `p02` | `primario` | caldaia.water_supply → rc-mandata-generatori.a | F1 |
| `p03` | `primario` | rc-mandata-generatori.b → deviatrice-acs.in | F3, F9 |
| `p04` | `primario` | deviatrice-acs.out_a → volume-tecnico.primary_in | F3, F9 |
| `p05` | `primario` | deviatrice-acs.out_b → bollitore.coil_in | F9 |
| `p06` | `primario` | volume-tecnico.primary_out → rc-ritorno-primario.a | F3 |
| `p07` | `primario` | bollitore.coil_out → rc-ritorno-primario.c | F9 |
| `p08` | `primario` | rc-ritorno-primario.b → rip-ritorno-generatori.a | F3, F9 |
| `p09` | `primario` | rip-ritorno-generatori.c → pdc.water_return | F1 |
| `p10` | `primario` | rip-ritorno-generatori.b → caldaia.water_return | F1 |
| `s01` | `secondario` | volume-tecnico.secondary_out → rip-mandata-secondario.a | F5 |
| `s02` | `secondario` | rip-mandata-secondario.c → circolatore-radiatori.a | F6 |
| `s03` | `secondario` | circolatore-radiatori.b → radiatori.in | F6 |
| `s04` | `secondario` | radiatori.out → rc-ritorno-secondario.c | F6 |
| `s05` | `secondario` | rip-mandata-secondario.b → circolatore-fancoil.a | F7 |
| `s06` | `secondario` | circolatore-fancoil.b → fancoil.in | F7 |
| `s07` | `secondario` | fancoil.out → rc-ritorno-secondario.a | F7 |
| `s08` | `secondario` | rc-ritorno-secondario.b → volume-tecnico.secondary_in | F5 |
| `q01` | `solare` | collettori-solari.supply → circolatore-solare.a | F10, F11 |
| `q02` | `solare` | circolatore-solare.b → ritegno-solare.a | F11 |
| `q03` | `solare` | ritegno-solare.b → der-sicurezza-solare.a | F11 |
| `q04` | `solare` | der-sicurezza-solare.branch → sicurezza-solare.a | F11 |
| `q05` | `solare` | der-sicurezza-solare.b → der-manometro-solare.a | F11 |
| `q06` | `solare` | der-manometro-solare.branch → manometro-solare.a | F11 |
| `q07` | `solare` | der-manometro-solare.b → der-vaso-solare.a | F11 |
| `q08` | `solare` | der-vaso-solare.branch → vaso-solare.a | F11 |
| `q09` | `solare` | der-vaso-solare.b → bollitore.solar_coil_in | F10, F11 |
| `q10` | `solare` | bollitore.solar_coil_out → collettori-solari.return | F10 |
| `f01` | `acqua-fredda` | acquedotto.a → bollitore.cold_in | F12 |
| `h01` | `acs` | bollitore.dhw_out → utenze-acs.a | F12 |

### Reti (5)

| Rete | Fluido | Macchina o confine che la alimenta | Righe |
|---|---|---|---|
| `primario` | `heating_water` | i due generatori (`pdc`, `caldaia`) | F1, F3, F9 |
| `secondario` | `heating_water` | `volume-tecnico` | F5, F6, F7 |
| `solare` | `solar_fluid` | `collettori-solari` | F10, F11 |
| `acqua-fredda` | `cold_water` | `acquedotto` (confine) | F12 |
| `acs` | `domestic_hot_water` | `bollitore` | F12 |

### Attacchi rimasti liberi, e perché

| Attacco | Perché è libero |
|---|---|
| `volume-tecnico.vent`, `volume-tecnico.drain`, `volume-tecnico.probe` | stub: ci appende gli accessori il pezzo successivo (F4 per lo scarico) |
| `bollitore.probe` | stub: sede sonda, del pezzo successivo |
| `bollitore.recirculation_in` | il ricircolo è escluso dal testo (F14); il catalogo lo dà tappato quando non si usa |

Nessun attacco `required: true` è rimasto libero.

### Assunzioni → righe

| Assunzione | Righe |
|---|---|
| `a01-regime` | F1 |
| `a02-circolatori-generatori` | F1, F3 |
| `a03-parallelo-generatori` | F1 |
| `a04-regolazione-generatori` | F2 |
| `a05-carico-scarico-volume` | F4 |
| `a06-ripartizione-secondari` | F5 |
| `a07-circolatori-secondari` | F5, F6, F7 |
| `a08-terminali-rappresentativi` | F6, F7 |
| `a09-deviatrice-priorita` | F9 |
| `a10-ritorno-serpentino-superiore` | F9 |
| `a11-campo-solare` | F10 |
| `a12-posizione-gruppo-solare` | F10, F11 |
| `a13-attacco-accessori-solari` | F11 |
| `a14-solare-pezzi-non-descritti` | F11 |
| `a15-miscelatrice-termostatica` | F13 |
| `a16-ricircolo-escluso` | F14 |
