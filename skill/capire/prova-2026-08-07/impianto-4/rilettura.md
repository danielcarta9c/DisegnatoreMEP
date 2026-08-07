# Tabella di rilettura — Esempio 4, sistema ibrido con pompa di calore e caldaia combinata

Rilettura del testo dell'ingegnere frase per frase. Ogni riga porta gli elementi del
grafo che rappresentano quella frase, oppure la voce di `assumptions` che la copre.
La seconda tabella fa il percorso inverso: ogni componente e ogni tubazione del grafo
risale alla frase da cui nasce.

## 1. Dal testo al grafo

| # | Frase del testo | Cosa nel grafo | Voci dichiarate |
|---|---|---|---|
| T | «Esempio 4 – Sistema ibrido con pompa di calore e caldaia combinata» (titolo) | `metadata.project_name`, `metadata.project_id`. Nessuna affermazione topologica. | — |
| S1 | «L'impianto è costituito da una pompa di calore aria-acqua da 10 kW e da una caldaia a condensazione combinata da 24 kW, collegate in parallelo.» | Componenti `pdc` (`heat-pump-air-water`, `potenza: 10 kW`, `tipo: aria-acqua`) e `caldaia` (`gas-boiler`, `potenza: 24 kW`, `tipo: a condensazione`, `qualifica: combinata`). «In parallelo»: confluenza sulla mandata `rc-mandata-generatori` (`tee-junction`) con `t1` e `t3` in ingresso, e ripartizione sul ritorno `rc-ritorno-generatori` (`tee-split`) con `t5` in ingresso, `t6` e `t7` in uscita. Le due potenze danno `plant_regime: up_to_35_kw` (10 + 24 = 34 kW). | `a1` (la caldaia «combinata» resta la voce base), `a2` (con che pezzo si uniscono i flussi), `a4` (circolazione del primario), `a12` (somma delle potenze e regime) |
| S2 | «La pompa di calore lavora come generatore principale, mentre la caldaia interviene quando la temperatura esterna è bassa, quando serve maggiore potenza oppure quando l'impianto richiede temperature di mandata più alte.» | Nessun nodo e nessuna tubazione: è logica di regolazione. L'unica traccia è la parola dell'ingegnere trascritta in `pdc.properties.ruolo` = «generatore principale». | `a9` (la sequenza di intervento è regolazione, il grafo non la mostra) |
| S3 | «I due generatori alimentano un volume tecnico da 150 litri configurato a quattro tubi.» | Componente `volano` (`buffer-four-port`, `volume: 150 litri`, `configurazione: a quattro tubi`, `denominazione: volume tecnico`). Alimentazione: `t4` (`rc-mandata-generatori.b` → `volano.primary_in`) e ritorno `t5` (`volano.primary_out` → `rc-ritorno-generatori.a`). | `a3` (lettura di «a quattro tubi») |
| S4 | «Sul volume tecnico sono previsti il collegamento per il carico automatico dell'impianto da acquedotto e lo scarico.» | Niente nel grafo: gruppo di riempimento (`filling`) e attacco di scarico (`drain`) sono ferramenta di servizio, li aggiunge il pezzo successivo della catena. Gli attacchi `vent`, `drain` e `probe` del volano sono `stub` e restano liberi. | `a7` (la nomina è registrata, e non è disegnato un secondo allacciamento di acquedotto verso il volume) |
| S5 | «Dal volume parte un circuito secondario con circolatore dedicato che alimenta direttamente l'impianto esistente a radiatori.» | Rete `secondario-riscaldamento`. Componenti `circolatore-secondario` (`pump-circulator`) e `radiatori` (`radiator`, `stato: esistente`). Tubazioni `t11` (`volano.secondary_out` → circolatore), `t12` (circolatore → radiatori), `t13` (radiatori → `volano.secondary_in`): il circuito si chiude sul volume. «Direttamente» = nessun pezzo interposto fra circolatore e terminali. | `a5` (circolatore messo sulla mandata, convenzione), `a6` (un terminale rappresentativo: quanti sono davvero?) |
| S6 | «La produzione di acqua calda sanitaria è affidata alla caldaia in modo istantaneo, senza bollitore di accumulo.» | Nessun accumulo sanitario nel grafo. La produzione è la catena `caldaia` → `valvola-deviatrice-acs` → `scambiatore-acs` descritta in S7. | `a8` (esclusione esplicita: non c'è perché il testo lo esclude), `a1` |
| S7 | «Quando viene richiesta ACS, una valvola a tre vie devia il circuito della caldaia verso uno scambiatore di calore a piastre.» | Componenti `valvola-deviatrice-acs` (`diverting-valve-3way`) e `scambiatore-acs` (`plate-heat-exchanger`). Tubazioni `t2` (`caldaia.water_supply` → `valvola.in`), `t3` (`valvola.out_a` → confluenza verso il volume tecnico), `t8` (`valvola.out_b` → `scambiatore.primary_in`). Il ritorno del primario si chiude con `t9` (`scambiatore.primary_out` → `rc-ritorno-caldaia.c`), `t7` (ritorno dal volume → `rc-ritorno-caldaia.a`) e `t10` (`rc-ritorno-caldaia.b` → `caldaia.water_return`): due ritorni su un solo attacco, quindi una confluenza (`rc-ritorno-caldaia`, `tee-junction`). | `a10` (valvola sulla mandata; dove rientra il ritorno dello scambiatore), `a11` (il ramo resta dentro la rete del primario) |
| S8 | «L'acqua fredda sanitaria proveniente dall'acquedotto attraversa lo scambiatore e viene riscaldata istantaneamente prima di essere inviata alle utenze.» | Reti `acqua-fredda` (`cold_water`) e `acs` (`domestic_hot_water`): il fluido cambia dentro lo scambiatore, quindi sono due reti. Componenti di confine `acquedotto` (`cold-water-inlet`) e `utenze-acs` (`dhw-draw-off`). Tubazioni `t14` (acquedotto → `scambiatore.secondary_in`) e `t15` (`scambiatore.secondary_out` → utenze). Circuito aperto: entra dall'acquedotto, esce alle utenze. | — |
| S9 | «Durante la produzione di ACS la caldaia dà priorità al sanitario, mentre la pompa di calore può continuare ad alimentare il volume tecnico e il circuito di riscaldamento.» | Nessun elemento nuovo. La frase conferma la topologia già scritta: la pompa di calore raggiunge il volume tecnico per una via propria (`t1` → `rc-mandata-generatori` → `t4`) che non passa dalla valvola deviatrice, quindi resta percorribile quando la caldaia è deviata sul sanitario. La priorità in sé è regolazione. | `a9` |

## 2. Dal grafo al testo

| Elemento | Voce di catalogo | Frase da cui nasce |
|---|---|---|
| `pdc` | `heat-pump-air-water` | S1 |
| `caldaia` | `gas-boiler` | S1 (qualifica «combinata»), S6–S7 per il modo di produrre l'ACS |
| `volano` | `buffer-four-port` | S3 |
| `rc-mandata-generatori` | `tee-junction` | S1 («in parallelo») |
| `rc-ritorno-generatori` | `tee-split` | S1 («in parallelo») |
| `valvola-deviatrice-acs` | `diverting-valve-3way` | S7 |
| `scambiatore-acs` | `plate-heat-exchanger` | S7, S8 |
| `rc-ritorno-caldaia` | `tee-junction` | S7 (due ritorni su un attacco solo) |
| `circolatore-secondario` | `pump-circulator` | S5 |
| `radiatori` | `radiator` | S5 |
| `acquedotto` | `cold-water-inlet` | S8 |
| `utenze-acs` | `dhw-draw-off` | S8 |
| `t1` `pdc.water_supply` → `rc-mandata-generatori.a` | — | S1, S3 |
| `t2` `caldaia.water_supply` → `valvola-deviatrice-acs.in` | — | S7 |
| `t3` `valvola-deviatrice-acs.out_a` → `rc-mandata-generatori.c` | — | S1, S3, S7 |
| `t4` `rc-mandata-generatori.b` → `volano.primary_in` | — | S3 |
| `t5` `volano.primary_out` → `rc-ritorno-generatori.a` | — | S1, S3 |
| `t6` `rc-ritorno-generatori.b` → `pdc.water_return` | — | S1, S3 |
| `t7` `rc-ritorno-generatori.c` → `rc-ritorno-caldaia.a` | — | S1, S3, S7 |
| `t8` `valvola-deviatrice-acs.out_b` → `scambiatore-acs.primary_in` | — | S7 |
| `t9` `scambiatore-acs.primary_out` → `rc-ritorno-caldaia.c` | — | S7 |
| `t10` `rc-ritorno-caldaia.b` → `caldaia.water_return` | — | S7 |
| `t11` `volano.secondary_out` → `circolatore-secondario.a` | — | S5 |
| `t12` `circolatore-secondario.b` → `radiatori.in` | — | S5 |
| `t13` `radiatori.out` → `volano.secondary_in` | — | S5 |
| `t14` `acquedotto.a` → `scambiatore-acs.secondary_in` | — | S8 |
| `t15` `scambiatore-acs.secondary_out` → `utenze-acs.a` | — | S8 |
| rete `primario` | — | S1, S3, S7 |
| rete `secondario-riscaldamento` | — | S5 |
| rete `acqua-fredda` | — | S8 |
| rete `acs` | — | S8 |
| `plant_regime: up_to_35_kw` | — | S1 (10 kW + 24 kW = 34 kW) |

Nessun elemento del grafo resta senza riga. Nessuna affermazione topologica del testo
resta senza rappresentazione o senza una voce dichiarata.
