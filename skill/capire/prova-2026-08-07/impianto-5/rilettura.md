# Tabella di rilettura — Esempio 5, tre pompe di calore con più circuiti secondari

Una riga per frase del testo. Per ciascuna: gli elementi del grafo che la rappresentano
(componenti in tondo, tubazioni con il loro `id`) e le voci di `assumptions` che la
coprono dove il grafo da solo non basta.

| # | Frase del testo | Componenti | Tubazioni | Assunzioni |
|---|---|---|---|---|
| 1 | «La centrale termica è composta da tre pompe di calore aria-acqua reversibili da 35 kW ciascuna, installate in parallelo e gestite in cascata.» | `pdc-1`, `pdc-2`, `pdc-3` (`heat-pump-air-water`, proprietà `potenza` = 35 kW, `tipo` = aria-acqua reversibile, `gestione` = in cascata); i raccordi che trascrivono il parallelo: `rc-mandata-generatori-1`, `rc-mandata-generatori-2`, `rip-ritorno-generatori-1`, `rip-ritorno-generatori-2`. Da qui anche `plant_regime` = `over_35_kw` (3 × 35 = 105 kW). | `p01`, `p02`, `p03`, `p04` (mandate che confluiscono); `p11`, `p12`, `p13`, `p14` (ritorni che si ripartiscono) | a1 (reversibili → il circuito porta anche il raffrescamento), a2 (cascata = regolazione), a3 (con che pezzo si fa il parallelo), a13 (come è stato ricavato il regime) |
| 2 | «Le pompe di calore alimentano un volume tecnico da 500 litri a quattro tubi, utilizzato come accumulo inerziale e punto di separazione tra il circuito dei generatori e i circuiti dell'edificio.» | `volano` (`buffer-four-port`: dichiara insieme `thermal_storage` e `hydraulic_separation`, e ha i quattro attacchi primario/secondario; proprietà `volume` = 500 litri, `configurazione` = a quattro tubi). La separazione è anche il confine fra la rete `primario` e la rete `secondario`. | `p06` (mandata primaria al volano), `p08` (ritorno primario dal volano) | a14 (lettura di «a quattro tubi») |
| 3 | «Dal volume tecnico partono tre circuiti secondari indipendenti:» | `rip-mandata-secondari-1`, `rip-mandata-secondari-2` (due ripartizioni in catena per tre rami); `rc-ritorno-secondari-1`, `rc-ritorno-secondari-2` (due confluenze sul ritorno). Rete `secondario`: i tre circuiti sono tre **rami** di una rete sola, perché nascono tutti dal volano. | `s01`, `s03` (mandata), `s15`, `s16` (ritorno al volano) | a4 (con che pezzo si staccano i tre circuiti) |
| 4 | «un circuito per le batterie calde e fredde delle unità di trattamento aria;» | `bat-uta` (`ahu-coil`, proprietà `tipo` = batterie calde e fredde delle unità di trattamento aria) | `s02` (dalla ripartizione al circolatore), `s06` (mandata alla batteria), `s07` (ritorno) | a9 (un terminale rappresentativo; «calde e fredde» potrebbe essere due batterie), a1 (d'estate lo stesso circuito porta acqua refrigerata) |
| 5 | «un circuito per i fan-coil;» | `fancoil` (`fan-coil`) | `s04`, `s08` (mandata), `s09` (ritorno) | a9 (un terminale rappresentativo, il numero non è detto), a1 |
| 6 | «un circuito miscelato dedicato al pavimento radiante, utilizzato solo in riscaldamento.» | `vmr-radiante` (`mixing-valve-3way`, `circuit_mixing`: è topologia, decide cosa entra nel circuito); `pav-radiante` (`underfloor-panel`, proprietà `funzionamento` = solo in riscaldamento); `rip-bypass-radiante` (ripartizione sul ritorno che alimenta l'ingresso freddo della miscelatrice) | `s05` (mandata alla miscelatrice), `s11` (mandata al pavimento), `s12` (ritorno dal pavimento), `s13` (by-pass alla miscelatrice), `s14` (ritorno verso il volano) | a8 (da dove è alimentato il secondo ingresso della miscelatrice), a9 |
| 7 | «Ogni circuito è dotato del proprio circolatore.» | `cir-uta`, `cir-fancoil`, `cir-radiante` (`pump-circulator`), uno per ciascuno dei tre circuiti secondari, sulla mandata | `s10` (dalla miscelatrice al circolatore del radiante); le mandate `s02`/`s06`, `s04`/`s08`, `s11` passano per i circolatori | a6 (a quali circuiti si riferisce «ogni»; il primario ha la circolazione a bordo macchina), a7 (posizione convenzionale sulla mandata) |
| 8 | «La produzione di ACS è centralizzata mediante un bollitore da 500 litri alimentato dalle pompe di calore.» | `bollitore` (`dhw-cylinder`, `dhw_storage`, `stored_medium` = acqua calda sanitaria, si riempie da `cold_in`; proprietà `volume` = 500 litri, `produzione` = centralizzata); `rc-ritorno-primario` (unisce il ritorno del serpentino a quello del volano) | `p07` (mandata al serpentino), `p09` (ritorno dal serpentino), `p10` (ritorno unito verso le macchine) | a5 (dove confluiscono i due ritorni sul primario) |
| 9 | «Una valvola a tre vie devia il flusso delle pompe di calore verso il serpentino del bollitore quando è richiesta la produzione sanitaria, dando priorità all'ACS.» | `vd-acs` (`diverting-valve-3way`, `diversion`): l'ingresso raccoglie la mandata delle tre macchine, un'uscita va al volano, l'altra al serpentino | `p05` (mandata dei generatori alla deviatrice), `p06` (uscita verso il volano), `p07` (uscita verso il serpentino) | a2 (la priorità sanitaria è regolazione: sul grafo si vede la valvola, non la priorità) |
| 10 | «L'acqua fredda sanitaria entra nella parte bassa del bollitore e l'ACS viene prelevata dalla parte alta.» | `acquedotto` (`cold-water-inlet`, confine) e `utenze` (`dhw-draw-off`, confine): il circuito sanitario è aperto. Reti `acqua-fredda` (cold_water) e `acs` (domestic_hot_water): il fluido cambia dentro il bollitore, quindi sono due reti. | `f01` (acquedotto → `cold_in`), `c01` (`dhw_out` → distribuzione), `c03` (distribuzione → utenze) | a12 (i confini non sono nominati dal testo; «parte alta/bassa» sono gli attacchi che il catalogo dichiara) |
| 11 | «Sull'uscita è prevista una valvola miscelatrice termostatica.» | **nessun elemento**: `dhw_mixing` è ferramenta sanitaria (§5), la aggiunge il pezzo che completa il grafo | — | a10 (la nomina è registrata, non persa) |
| 12 | «È presente anche un circuito di ricircolo ACS collegato al bollitore e dotato di proprio circolatore.» | `cir-ricircolo` (`pump-circulator-dhw`); `rip-ricircolo` (dove l'anello si stacca dalla distribuzione) e `rc-ricircolo` (dove rientra, subito a valle del bollitore): il bollitore di catalogo non ha l'attacco di ricircolo, quindi l'anello si chiude sul tubo | `c02` (tratto fra confluenza e ripartizione), `c04` (stacco del ricircolo), `c05` (rientro dell'anello) | a11 (l'attacco non si inventa; il punto di stacco e di rientro non sono detti dal testo) |

## Controllo inverso: ogni elemento del grafo risale a una frase

**Componenti (28/28).** Riga 1: `pdc-1`, `pdc-2`, `pdc-3`, `rc-mandata-generatori-1`,
`rc-mandata-generatori-2`, `rip-ritorno-generatori-1`, `rip-ritorno-generatori-2`.
Riga 2: `volano`. Riga 3: `rip-mandata-secondari-1`, `rip-mandata-secondari-2`,
`rc-ritorno-secondari-1`, `rc-ritorno-secondari-2`. Riga 4: `bat-uta`. Riga 5:
`fancoil`. Riga 6: `vmr-radiante`, `pav-radiante`, `rip-bypass-radiante`. Riga 7:
`cir-uta`, `cir-fancoil`, `cir-radiante`. Riga 8: `bollitore`, `rc-ritorno-primario`.
Riga 9: `vd-acs`. Riga 10: `acquedotto`, `utenze`. Riga 12: `rc-ricircolo`,
`rip-ricircolo`, `cir-ricircolo`.

**Tubazioni (36/36).** `p01`–`p04` e `p11`–`p14` riga 1; `p06`, `p08` riga 2 (e `p06`
anche riga 9); `p05`, `p07` riga 9; `p09`, `p10` riga 8; `s01`, `s03`, `s15`, `s16`
riga 3; `s02`, `s06`, `s07` riga 4; `s04`, `s08`, `s09` riga 5; `s05`, `s11`–`s14`
riga 6; `s10` riga 7; `f01`, `c01`, `c03` riga 10; `c02`, `c04`, `c05` riga 12.

**Reti (4/4).** `primario` e `secondario` nascono dalla riga 2 (il volano è il punto di
separazione dichiarato dal testo); `acqua-fredda` e `acs` dalla riga 10 (il fluido
cambia dentro il bollitore).

Nessun componente e nessuna tubazione resta fuori dalla tabella; nessuna affermazione
topologica del testo resta senza rappresentazione o senza una voce di `assumptions` che
la copra.
