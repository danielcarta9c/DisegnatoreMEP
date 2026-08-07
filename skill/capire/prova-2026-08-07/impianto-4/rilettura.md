# Tabella di rilettura — Esempio 4, sistema ibrido pompa di calore + caldaia combinata

Una riga per frase del testo dell'ingegnere. Per ogni frase: che cosa afferma sulla
topologia, quali elementi del grafo la rappresentano, quale voce di `assumptions` la
copre dove il grafo non la mostra.

## A — Dal testo al grafo

| # | Frase del testo | Che cosa afferma | Elementi del grafo | Assunzioni |
|---|---|---|---|---|
| 1 | «Sistema ibrido con pompa di calore e caldaia combinata» (titolo) | nomina l'impianto; nessuna affermazione topologica | `metadata.project_name`, `metadata.project_id` | — |
| 2 | «L'impianto è costituito da una pompa di calore aria-acqua da 10 kW e da una caldaia a condensazione combinata da 24 kW, collegate in parallelo.» | due generatori; potenze dette; sono in parallelo, quindi le mandate si uniscono e i ritorni si dividono | `pdc` (heat-pump-air-water, potenza 10 kW, tipo aria-acqua), `caldaia` (gas-boiler, potenza 24 kW, tipo a condensazione combinata), `rc-mandata-generatori` (raccordo a T), `rip-ritorno-generatori` (ripartizione a T), tubazioni `t-pdc-mandata`, `t-deviatrice-riscaldamento`, `t-ritorno-pdc`, `t-ritorno-verso-caldaia`; rete `primario`; `plant_regime: up_to_35_kw` (10 + 24 = 34 kW) | a1 (con che pezzo si fa il parallelo), a4 (nessun circolatore sul primario), a9 (perché «combinata» non ha cambiato la voce di catalogo), a10 (come è stato ricavato il regime) |
| 3 | «La pompa di calore lavora come generatore principale, mentre la caldaia interviene quando la temperatura esterna è bassa, quando serve maggiore potenza oppure quando l'impianto richiede temperature di mandata più alte.» | logica di regolazione: nessun nodo, nessun tubo | — (nulla nel grafo: è regolazione) | a7 |
| 4 | «I due generatori alimentano un volume tecnico da 150 litri configurato a quattro tubi.» | i due generatori confluiscono nel primario dell'accumulo; volume detto; quattro attacchi di flusso | `volano` (buffer-four-port, volume 150 litri, configurazione a quattro tubi), `t-mandata-volano` (verso `primary_in`), `t-volano-ritorno` (da `primary_out`), `rc-mandata-generatori`, `rip-ritorno-generatori`; rete `primario` | a1 |
| 5 | «Sul volume tecnico sono previsti il collegamento per il carico automatico dell'impianto da acquedotto e lo scarico.» | dice dove stanno due accessori di servizio (riempimento, scarico) | — (ferramenta: non entra in questa stesura; gli attacchi di servizio del volano restano liberi) | a6 |
| 6 | «Dal volume parte un circuito secondario con circolatore dedicato che alimenta direttamente l'impianto esistente a radiatori.» | seconda rete alimentata dall'accumulo; circolatore come pezzo a sé; terminali a radiatori; circuito chiuso, quindi anche il ritorno | rete `secondario`; `circolatore-secondario` (pump-circulator), `radiatori` (radiator); tubazioni `t-volano-circolatore` (da `secondary_out`), `t-circolatore-radiatori`, `t-radiatori-volano` (verso `secondary_in`) | a3 (circolatore sulla mandata), a5 (un solo terminale rappresentativo) |
| 7 | «La produzione di acqua calda sanitaria è affidata alla caldaia in modo istantaneo, senza bollitore di accumulo.» | il sanitario c'è, ed è istantaneo; esclusione esplicita dell'accumulo | — (nessun accumulo sanitario disegnato; il come è descritto nella frase 8) | a8, a9 |
| 8 | «Quando viene richiesta ACS, una valvola a tre vie devia il circuito della caldaia verso uno scambiatore di calore a piastre.» | sul ramo della caldaia c'è una deviazione a due strade: verso il volano o verso lo scambiatore; il primario dello scambiatore è acqua di riscaldamento della caldaia e il circuito si chiude | `valvola-deviatrice-acs` (diverting-valve-3way), `scambiatore-acs` (plate-heat-exchanger, lato primario), `rc-ritorno-caldaia` (raccordo a T); tubazioni `t-caldaia-mandata`, `t-deviatrice-riscaldamento` (`out_a` verso il volano), `t-deviatrice-scambiatore` (`out_b` verso lo scambiatore), `t-scambiatore-ritorno`, `t-ritorno-caldaia` | a2 (dove sta la valvola e dove rientra il ritorno dello scambiatore), a9, a11 (il ramo resta nella rete del primario) |
| 9 | «L'acqua fredda sanitaria proveniente dall'acquedotto attraversa lo scambiatore e viene riscaldata istantaneamente prima di essere inviata alle utenze.» | circuito sanitario aperto: confine acquedotto → secondario dello scambiatore → confine utenze; il fluido cambia dentro lo scambiatore, quindi due reti | `acquedotto` (cold-water-inlet), `utenze-sanitarie` (dhw-draw-off), lato secondario di `scambiatore-acs`; reti `acqua-fredda` e `acs`; tubazioni `t-acquedotto-scambiatore`, `t-scambiatore-utenze` | a8 (nessun ricircolo: il testo non lo nomina), a11 |
| 10 | «Durante la produzione di ACS la caldaia dà priorità al sanitario, mentre la pompa di calore può continuare ad alimentare il volume tecnico e il circuito di riscaldamento.» | logica di regolazione; conferma però una lettura topologica: la deviazione è sul solo ramo della caldaia, non sulla mandata comune, altrimenti la pompa di calore non potrebbe continuare | conferma la posizione di `valvola-deviatrice-acs` fra `caldaia` e `rc-mandata-generatori` | a7, a2 |

## B — Dal grafo al testo (nessun elemento senza una frase dietro)

| Elemento | Frase che lo genera |
|---|---|
| rete `primario` | 2, 4 |
| rete `secondario` | 6 |
| rete `acqua-fredda` | 9 |
| rete `acs` | 9 |
| `pdc` | 2 |
| `caldaia` | 2 |
| `valvola-deviatrice-acs` | 8 |
| `scambiatore-acs` | 8, 9 |
| `rc-mandata-generatori` | 2 («in parallelo») + 4 (un solo attacco sul volano) |
| `rip-ritorno-generatori` | 2 («in parallelo») + 4 |
| `rc-ritorno-caldaia` | 8 (il ritorno dello scambiatore e quello dal volano arrivano sullo stesso attacco della caldaia) |
| `volano` | 4 |
| `circolatore-secondario` | 6 |
| `radiatori` | 6 |
| `acquedotto` | 9 |
| `utenze-sanitarie` | 9 |
| `t-pdc-mandata` | 2, 4 |
| `t-caldaia-mandata` | 2, 8 |
| `t-deviatrice-riscaldamento` | 2, 4, 8 |
| `t-mandata-volano` | 4 |
| `t-volano-ritorno` | 4 (circuito chiuso) |
| `t-ritorno-pdc` | 2, 4 |
| `t-ritorno-verso-caldaia` | 2, 4 |
| `t-deviatrice-scambiatore` | 8 |
| `t-scambiatore-ritorno` | 8 (circuito chiuso) |
| `t-ritorno-caldaia` | 8 |
| `t-volano-circolatore` | 6 |
| `t-circolatore-radiatori` | 6 |
| `t-radiatori-volano` | 6 (circuito chiuso) |
| `t-acquedotto-scambiatore` | 9 |
| `t-scambiatore-utenze` | 9 |
| `plant_regime` | 2 (potenze dette: 10 + 24 = 34 kW) |

Nessun componente e nessuna tubazione del grafo resta fuori da questa seconda tabella;
nessuna frase del testo resta senza una riga nella prima.
