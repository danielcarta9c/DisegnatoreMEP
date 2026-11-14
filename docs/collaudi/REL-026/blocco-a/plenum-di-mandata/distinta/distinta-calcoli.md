# Distinta materiali — foglio dei calcoli (PROVA-A, tavola M.01 rev. 00)

Committente: Committente (dati omessi) · Progetto: Tre ventilconvettori canalizzati idronici con plenum di mandata · Data: 13.11.2026

> proposta (D-213, REL-013): il PO non ha ancora deciso se la skill fa la distinta; finché non decide, la distinta si fa solo col comando esplicito `mep.py distinta`. Regole `13d6f4ef01e2a96a` (distinta 1.3.0, lunghezze 1.1.0, fluidi 1.3.0, corredo 1.7.0, attivita 1.2.0, verifica 1.1.0).

## DA DEFINIRE — le domande al progettista

- GT-01 (Pompa di calore aria-acqua): marca e modello li dà il progettista.
- TZ-01, TZ-02, TZ-03 (Termostato di zona): marca e modello li dà il progettista.
- RA-01 (Griglia di ripresa con plenum e filtro): su che tubo sta? Il tubo del suo tratto non c'e': i diametri non sono chiesti su quella rete, o il calcolo non ne ha la portata. Serve la `sezione` del tratto (es. «MS 32×3»).
- RA-02 (Griglia di ripresa con plenum e filtro): su che tubo sta? Il tubo del suo tratto non c'e': i diametri non sono chiesti su quella rete, o il calcolo non ne ha la portata. Serve la `sezione` del tratto (es. «MS 32×3»).
- RA-03 (Griglia di ripresa con plenum e filtro): su che tubo sta? Il tubo del suo tratto non c'e': i diametri non sono chiesti su quella rete, o il calcolo non ne ha la portata. Serve la `sezione` del tratto (es. «MS 32×3»).
- Rete «Circuito dei ventilconvettori»: quanti metri di tubo, di che diametro e come isolato (preisolato, o nudo con guaina e il suo spessore)? Si scrivono nel blocco «distinta» del grafo.
- VE-01 (Vaso di espansione): manca il dato «volume_l» per «Vaso di espansione chiuso a membrana per riscaldamento DA DEFINIRE (volume_l) l, con attacco e staffa».
- VIB-01 (Valvola di intercettazione bloccabile aperta): su che tubo sta? Il tubo del suo tratto non c'e': i diametri non sono chiesti su quella rete, o il calcolo non ne ha la portata. Serve la `sezione` del tratto (es. «MS 32×3»).
- T15 (Alimentazione pompa di calore): manca `protezione` sul tratto.
- T16 (Alimentazione ventilconvettore 3): manca `protezione` sul tratto.
- T17 (Alimentazione ventilconvettore 1): manca `protezione` sul tratto.
- T18 (Alimentazione ventilconvettore 2): manca `protezione` sul tratto.
- «Ventilconvettore canalizzato» (TE-02, TE-03, TE-01) non ha corredo di posa nelle regole della distinta: chi lo fornisce e che cosa porta con se'? Si scrive nelle regole della distinta (corredo).
- «Plenum di mandata a due uscite» (PL-02) non ha corredo di posa nelle regole della distinta: chi lo fornisce e che cosa porta con se'? Si scrive nelle regole della distinta (corredo).
- «Plenum di mandata a tre uscite» (PL-03) non ha corredo di posa nelle regole della distinta: chi lo fornisce e che cosa porta con se'? Si scrive nelle regole della distinta (corredo).
- «Plenum di mandata a sei uscite» (PL-01) non ha corredo di posa nelle regole della distinta: chi lo fornisce e che cosa porta con se'? Si scrive nelle regole della distinta (corredo).

## Da confermare per questa offerta

- Fornitura: apparecchiature fornite da Nove C; bocchette e griglie del Committente; opere edili del Committente; messa in servizio con Nove C — come da regole predefinite di Nove C; confermare per questa offerta.

## Le tratte

| tratto | rete | da - a | sezione | L stimata | L da quotare | conto |
|---|---|---|---|---|---|---|
| T01 | Mandata aria 3 | PL-01 - TA-01 | Ø160 | 3 | 5 | (3 + 1) × 1,15 = 4,6 → 5 m |
| T02 | Mandata aria 3 | PL-01 - TA-02 | Ø160 | 4 | 6 | (4 + 1) × 1,15 = 5,75 → 6 m |
| T03 | Mandata aria 3 | PL-01 - TA-03 | Ø160 | 5 | 7 | (5 + 1) × 1,15 = 6,9 → 7 m |
| T04 | Mandata aria 3 | PL-01 - TA-04 | Ø160 | 6 | 8,5 | (6 + 1) × 1,15 = 8,05 → 8,5 m |
| T05 | Mandata aria 3 | PL-01 - TA-05 | Ø160 | 7 | 9,5 | (7 + 1) × 1,15 = 9,2 → 9,5 m |
| T06 | Mandata aria 3 | PL-01 - TA-06 | Ø160 | 8 | 10,5 | (8 + 1) × 1,15 = 10,35 → 10,5 m |
| T07 | Mandata aria 1 | PL-02 - TA-07 | Ø160 | 3 | 5 | (3 + 1) × 1,15 = 4,6 → 5 m |
| T08 | Mandata aria 1 | PL-02 - TA-08 | Ø160 | 4 | 6 | (4 + 1) × 1,15 = 5,75 → 6 m |
| T09 | Mandata aria 2 | PL-03 - TA-09 | Ø160 | 3 | 5 | (3 + 1) × 1,15 = 4,6 → 5 m |
| T10 | Mandata aria 2 | PL-03 - TA-10 | Ø160 | 4 | 6 | (4 + 1) × 1,15 = 5,75 → 6 m |
| T11 | Mandata aria 2 | PL-03 - TA-11 | Ø160 | 5 | 7 | (5 + 1) × 1,15 = 6,9 → 7 m |
| T12 | Scarico condensa 3 | TE-01 - SIF-01 - AL-01 | Ø32 | 3 | 10 | (3 + 1) × 1,15 = 4,6 → 5 m; minimo condensa 10 m → 10 m |
| T13 | Scarico condensa 1 | TE-02 - SIF-02 - AL-02 | Ø32 | 3 | 10 | (3 + 1) × 1,15 = 4,6 → 5 m; minimo condensa 10 m → 10 m |
| T14 | Scarico condensa 2 | TE-03 - SIF-03 - AL-03 | Ø32 | 3 | 10 | (3 + 1) × 1,15 = 4,6 → 5 m; minimo condensa 10 m → 10 m |
| T15 | Alimentazione pompa di calore | QE-01 - GT-01 | 3G2,5 | 12 | 15 | (12 + 1) × 1,15 = 14,95 → 15 m |
| T16 | Alimentazione ventilconvettore 3 | QE-01 - TE-01 | 3G1,5 | 11 | 14 | (11 + 1) × 1,15 = 13,8 → 14 m |
| T17 | Alimentazione ventilconvettore 1 | QE-01 - TE-02 | 3G1,5 | 9 | 11,5 | (9 + 1) × 1,15 = 11,5 → 11,5 m |
| T18 | Alimentazione ventilconvettore 2 | QE-01 - TE-03 | 3G1,5 | 10 | 13 | (10 + 1) × 1,15 = 12,65 → 13 m |
| T19 | Consenso del termostato 1 | TZ-01 - TE-02 | 2×0,75 | 6 | 8,5 | (6 + 1) × 1,15 = 8,05 → 8,5 m |
| T20 | Consenso del termostato 2 | TZ-02 - TE-03 | 2×0,75 | 6 | 8,5 | (6 + 1) × 1,15 = 8,05 → 8,5 m |
| T21 | Consenso del termostato 3 | TZ-03 - TE-01 | 2×0,75 | 6 | 8,5 | (6 + 1) × 1,15 = 8,05 → 8,5 m |

## La verifica (segnala, non corregge)

| dove | controllo | valore | soglia | esito |
|---|---|---|---|---|
| T01 | velocità | manca la portata (`portata_m3h`) | ≤ 3 m/s | non verificabile |
| T02 | velocità | manca la portata (`portata_m3h`) | ≤ 3 m/s | non verificabile |
| T03 | velocità | manca la portata (`portata_m3h`) | ≤ 3 m/s | non verificabile |
| T04 | velocità | manca la portata (`portata_m3h`) | ≤ 3 m/s | non verificabile |
| T05 | velocità | manca la portata (`portata_m3h`) | ≤ 3 m/s | non verificabile |
| T06 | velocità | manca la portata (`portata_m3h`) | ≤ 3 m/s | non verificabile |
| T07 | velocità | manca la portata (`portata_m3h`) | ≤ 3 m/s | non verificabile |
| T08 | velocità | manca la portata (`portata_m3h`) | ≤ 3 m/s | non verificabile |
| T09 | velocità | manca la portata (`portata_m3h`) | ≤ 3 m/s | non verificabile |
| T10 | velocità | manca la portata (`portata_m3h`) | ≤ 3 m/s | non verificabile |
| T11 | velocità | manca la portata (`portata_m3h`) | ≤ 3 m/s | non verificabile |

## Le voci, con la regola e il conto

| rif | voce | q.tà | um | conto | regola |
|---|---|---|---|---|---|
| A.1 | Pompa di calore aria-acqua: marca e modello DA DEFINIRE | 1 | n | 1 nello schema (GT-01) | `corredo/heat-pump-air-water/apparecchiatura` |
| A.2 | Termostato di zona: marca e modello DA DEFINIRE | 3 | n | 3 nello schema (TZ-01, TZ-02, TZ-03) | `corredo/room-thermostat/apparecchiatura` |
| S.1 | Basamento a terra per l'unità esterna con supporti antivibranti | 1 | n | GT-01: 1 | `corredo/heat-pump-air-water/basamento-pdc` |
| S.2 | Sospensione del plenum di ripresa: 2 barre filettate M8 con ancoranti e dadi | 3 | kit | 3 pezzi × 1 = 3 (RA-01, RA-02, RA-03) | `corredo/return-air-terminal/sospensione-plenum-di-ripresa` |
| B.1 | Condotto flessibile coibentato Ø160 (isolamento 25 mm, barriera vapore), confezione da 10 m | 11 | conf. | 11 pezzi interi, 75,5 m: in confezioni da 10 m (utili 9,5) ne servono 11 [9,5] [9,5] [8,5 + 1] [7] [7] [6] [6] [6] [5] [5] [5]; riserva 25%: 75,5 × 1,25 = 94,38 m → 10; si prende il maggiore: 11; 1 giunte: un tratto e' piu' lungo di una confezione | `fluidi/supply_air/flessibile-in-confezioni` |
| B.2 | Manicotto di giunzione Ø160 per i tratti piu' lunghi di una confezione | 1 | n | 1 giunte | `fluidi/supply_air/flessibile-in-confezioni` |
| B.3 | Manicotto di giunzione Ø160 | 2 | n | 2 per sezione | `fluidi/supply_air/manicotto-di-riserva` |
| B.4 | Fascetta di serraggio Ø160 (anima e mantello) | 44 | n | 11 tratti × 4 = 44 | `fluidi/supply_air/fascette` |
| B.5 | Nastro alluminio rinforzato 50 mm | 4 | rotolo | 75,5 m / 20 m per eccesso, almeno 1 = 4 | `fluidi/supply_air/nastro-alluminio` |
| B.6 | Sostegno per flessibile (fascia o collare con pendino), passo ≤ 1,2 m | 78 | n | T01 6 + T02 6 + T03 7 + T04 9 + T05 9 + T06 10 + T07 6 + T08 6 + T09 6 + T10 6 + T11 7 = 78 (L / 1,2 m per eccesso +1 per tratto) | `fluidi/supply_air/sostegni` |
| B.7 | Plenum porta-bocchetta coibentato per bocchetta 300×150, attacco Ø160 laterale | 11 | n | 11 pezzi × 1 = 11 (TA-07, TA-08, TA-09, TA-10, TA-11, TA-01, TA-02, TA-03, TA-04, TA-05, TA-06) | `corredo/air-supply-terminal/plenum-porta-bocchetta` |
| B.8 | Plenum di ripresa in lamiera zincata, non coibentato, con filtro ispezionabile, bocca DA DEFINIRE (sezione), sulla bocca di aspirazione dell'unità interna; filtro unico: l'eventuale filtro di serie dell'unità interna si toglie | 3 | n | 3 pezzi × 1 = 3 (RA-01, RA-02, RA-03) | `corredo/return-air-terminal/plenum-di-ripresa` |
| D.1 | Tubo PVC rigido Ø32 | 30 | m | T12 10 + T13 10 + T14 10 = 30 m | `fluidi/condensate/tubo-pvc` |
| D.2 | Curva 87°-90° Ø32 | 18 | n | T12 6 + T13 6 + T14 6 = 18 (L / 2 m per eccesso +1 per tratto) | `fluidi/condensate/curve-condensa` |
| D.3 | Manicotto Ø32 | 9 | n | T12 3 + T13 3 + T14 3 = 9 (L / 3 m per eccesso -1 per tratto) | `fluidi/condensate/manicotti-condensa` |
| D.4 | Collare per tubo condensa | 30 | n | T12 10 + T13 10 + T14 10 = 30 (L / 1 m per eccesso per tratto) | `fluidi/condensate/collari-condensa` |
| D.5 | Isolamento anticondensa 9 mm per il tubo della condensa | 30 | m | T12 10 + T13 10 + T14 10 = 30 m | `fluidi/condensate/isolamento-anticondensa` |
| D.6 | Collante e pulitore PVC | 1 | n | 1 per fluido | `fluidi/condensate/collante-pvc` |
| D.7 | Innesto sullo scarico esistente con braga 45° Ø40, a valle del sifone dell'apparecchio | 3 | n | 3 pezzi × 1 = 3 (AL-02, AL-03, AL-01) | `corredo/condensate-outlet/innesto-sullo-scarico` |
| D.8 | Sifone ispezionabile per condensa | 3 | n | 3 pezzi × 1 = 3 (SIF-02, SIF-03, SIF-01) | `corredo/condensate-trap/sifone` |
| I.1 | Tubo della rete «Circuito dei ventilconvettori»: diametro, metri e isolamento DA DEFINIRE | DA DEFINIRE | m | mancano i metri della rete | `fluidi/heating_water/tubo` |
| I.2 | Tee a pressare tubo multistrato MS 26×3 | 3 | n | 3 pezzi × 1 = 3 (RC-04, RC-03, RC-02) | `corredo/tee-junction/tee + corredo/tee-split/tee` |
| I.3 | Defangatore magnetico 1" | 1 | n | DEF-01: 1 | `corredo/dirt-separator/pezzo` |
| I.4 | Vaso di espansione chiuso a membrana per riscaldamento DA DEFINIRE (volume_l) l, con attacco e staffa | 1 | n | VE-01: 1 | `corredo/expansion-connection/pezzo` |
| I.5 | Giunto antivibrante 1" | 2 | n | 2 pezzi × 1 = 2 (GA-02, GA-01) | `corredo/flexible-joint/pezzo` |
| I.6 | Pulitore per impianti nuovi o recenti, 1 l | 1 | n | GT-01: 1 | `corredo/heat-pump-air-water/pulitore` |
| I.7 | Filmante e inibitore per impianti, 1 l | 1 | n | GT-01: 1 | `corredo/heat-pump-air-water/filmante` |
| I.8 | Manometro 0-6 bar attacco ½" | 1 | n | MN-01: 1 | `corredo/pressure-gauge/pezzo` |
| I.9 | Tee a pressare tubo multistrato MS 32×3 | 4 | n | 4 pezzi × 1 = 4 (RC-01, DER-03, DER-02, DER-01) | `corredo/tee-split/tee + corredo/tee-branch/tee` |
| I.10 | Filtro a Y 1" FF, maglia 500 µm | 1 | n | FIL-01: 1 | `corredo/strainer/pezzo` |
| I.11 | Rubinetto portamanometro a tre vie ½" | 1 | n | RM-01: 1 | `corredo/valve-gauge-cock-3way/pezzo` |
| I.12 | Valvola a sfera a passaggio totale 1" FF, con leva | 3 | n | 3 pezzi × 1 = 3 (VI-04, VI-05, VI-01) | `corredo/valve-isolation/pezzo` |
| I.13 | Valvola a sfera a passaggio totale ½" FF, con leva | 6 | n | 6 pezzi × 1 = 6 (VI-07, VI-06, VI-09, VI-08, VI-02, VI-03) | `corredo/valve-isolation/pezzo` |
| I.14 | Valvola a sfera a passaggio totale DA DEFINIRE (pollice) FF, con leva | 1 | n | VIB-01: 1 | `corredo/valve-isolation-locked-open/pezzo` |
| I.15 | Valvola di sicurezza ½" MF 3 bar, con scarico convogliato | 1 | n | VS-01: 1 | `corredo/valve-safety/pezzo` |
| I.16 | Raccordo diritto a pressare M 1" × tubo multistrato MS 32×3 | 10 | n | 10 giunzioni: GA-01 (GA-01 – DER-01); VI-01 (DER-01 – VI-01); VI-01 (VI-01 – RC-01); VI-04 (RC-04 – VI-04); VI-05 (VI-05 – DER-02); FIL-01 (DER-03 – FIL-01); FIL-01 (FIL-01 – GA-02); GA-02 (FIL-01 – GA-02); VIB-01 (DER-03 – VIB-01); RM-01 (DER-02 – RM-01) | `corredo/giunzioni/raccordo` |
| I.17 | Raccordo diritto a pressare M ½" × tubo multistrato MS 20×2 | 12 | n | 12 giunzioni: VI-07 (RC-01 – VI-07); VI-07 (VI-07 – TE-02); VI-09 (RC-02 – VI-09); VI-09 (VI-09 – TE-03); VI-02 (RC-02 – VI-02); VI-02 (VI-02 – TE-01); VI-06 (TE-02 – VI-06); VI-06 (VI-06 – RC-04); VI-08 (TE-03 – VI-08); VI-08 (VI-08 – RC-03); VI-03 (TE-01 – VI-03); VI-03 (VI-03 – RC-03) | `corredo/giunzioni/raccordo` |
| I.18 | Raccordo diritto a pressare M × tubo multistrato MS 20×2, all'attacco | 6 | n | 6 giunzioni: TE-02 (VI-07 – TE-02); TE-03 (VI-09 – TE-03); TE-01 (VI-02 – TE-01); TE-02 (TE-02 – VI-06); TE-03 (TE-03 – VI-08); TE-01 (TE-01 – VI-03) | `corredo/giunzioni/raccordo-all-attacco` |
| I.19 | Nipplo 1" M × M | 2 | n | 2 giunzioni: VI-04 – DEF-01; DEF-01 – VI-05 | `corredo/giunzioni/nipplo` |
| E.1 | Cavo FG16OR16 3G2,5, Alimentazione pompa di calore | 15 | m | T15 15 m | `fluidi/power_supply/cavo-di-alimentazione` |
| E.2 | Cavo FG16OR16 3G1,5, Alimentazione ventilconvettore 3, Alimentazione ventilconvettore 1, Alimentazione ventilconvettore 2 | 38,5 | m | T16 14 + T17 11,5 + T18 13 = 38,5 m | `fluidi/power_supply/cavo-di-alimentazione` |
| E.3 | DA DEFINIRE (protezione), linea dedicata: Alimentazione pompa di calore | 1 | n | una per tratto: T15 | `fluidi/power_supply/protezione-della-linea` |
| E.4 | DA DEFINIRE (protezione), linea dedicata: Alimentazione ventilconvettore 3, Alimentazione ventilconvettore 1, Alimentazione ventilconvettore 2 | 3 | n | una per tratto: T16, T17, T18 | `fluidi/power_supply/protezione-della-linea` |
| E.5 | Scatola di derivazione IP55 | 4 | n | 4 tratti × 1 = 4 | `fluidi/power_supply/scatola-di-derivazione` |
| E.6 | Tubo corrugato Ø25 per le linee di alimentazione | 60 | m | T15 15 + T16 14 + T17 11,5 + T18 13 = 53,5 m × 1, per eccesso a 10 m = 60 m | `fluidi/power_supply/corrugato-di-potenza` |
| E.7 | Cavo 2×0,75, Consenso del termostato 1, Consenso del termostato 2, Consenso del termostato 3 | 25,5 | m | T19 8,5 + T20 8,5 + T21 8,5 = 25,5 m | `fluidi/control_bus/cavo-di-bus` |
| E.8 | Tubo corrugato Ø20 per bus e linee di comando | 30 | m | T19 8,5 + T20 8,5 + T21 8,5 = 25,5 m × 1, per eccesso a 10 m = 30 m | `fluidi/control_bus/corrugato-di-bus` |
| E.9 | Aggiornamento dello schema del quadro elettrico | 1 | a corpo | QE-01: 1 | `corredo/electrical-panel/aggiornamento-schema-quadro` |
| E.10 | Scatola 503 per termostati e comandi a parete | 3 | n | 3 pezzi × 1 = 3 (TZ-01, TZ-02, TZ-03) | `corredo/room-thermostat/scatola-503` |
| F.1 | Foratura di tramezza Ø300 (o vano 470×270) per flessibili coibentati e plenum di bocchetta | 11 | n | T01 1 + T02 1 + T03 1 + T04 1 + T05 1 + T06 1 + T07 1 + T08 1 + T09 1 + T10 1 + T11 1 = 11 | `fluidi/supply_air/foratura-per-flessibile` |
| F.2 | Foratura per lo scarico della condensa (tramezze e parete del bagno) | 3 | n | T12 1 + T13 1 + T14 1 = 3 | `fluidi/condensate/foratura-condensa` |
| F.3 | Tracce per le linee dal quadro al controsoffitto | 10 | m | QE-01: 10 | `corredo/electrical-panel/tracce-dal-quadro` |
| F.4 | Traccia per la condensa fino allo scarico | 9 | m | 3 pezzi × 3 = 9 (AL-02, AL-03, AL-01) | `corredo/condensate-outlet/traccia-condensa` |
| F.5 | Traccia per termostati e comandi a parete, dal controsoffitto alla scatola | 4,2 | m | 3 pezzi × 1,4 = 4,2 (TZ-01, TZ-02, TZ-03) | `corredo/room-thermostat/traccia-per-apparecchio-a-parete` |
| X.1 | Ventilconvettore canalizzato: fornitura e corredo di posa DA DEFINIRE | 3 | n | 3 nello schema (TE-02, TE-03, TE-01) | `corredo/fan-coil-ducted-air (manca)` |
| X.2 | Plenum di mandata a due uscite: fornitura e corredo di posa DA DEFINIRE | 1 | n | 1 nello schema (PL-02) | `corredo/supply-plenum-2 (manca)` |
| X.3 | Plenum di mandata a tre uscite: fornitura e corredo di posa DA DEFINIRE | 1 | n | 1 nello schema (PL-03) | `corredo/supply-plenum-3 (manca)` |
| X.4 | Plenum di mandata a sei uscite: fornitura e corredo di posa DA DEFINIRE | 1 | n | 1 nello schema (PL-01) | `corredo/supply-plenum-6 (manca)` |
| Z.1 | Velette o controsoffitti per le bocchette, altezza utile ≥ 30 cm | 1 | a corpo | 1 per fluido | `fluidi/supply_air/velette-per-le-bocchette` |
| Z.2 | Bocchetta di mandata 300×150 a doppio filare con serranda | 11 | n | 11 pezzi × 1 = 11 (TA-07, TA-08, TA-09, TA-10, TA-11, TA-01, TA-02, TA-03, TA-04, TA-05, TA-06) | `corredo/air-supply-terminal/bocchetta-di-mandata` |
| Z.3 | Griglia di transito o luce sotto porta per il ritorno dell'aria dal locale servito | 11 | n | 11: 11 locali serviti (Camera 1, Camera 2, Studio, Bagno, Disimpegno, Soggiorno 1, Soggiorno 2, Cucina, Pranzo, Ingresso, Corridoio); il locale e' letto dall'etichetta della bocchetta | `corredo/air-supply-terminal/griglia-di-transito` |
| Z.4 | Griglia di ripresa DA DEFINIRE (sezione) senza filtro, apribile per accedere al filtro | 3 | n | 3 pezzi × 1 = 3 (RA-01, RA-02, RA-03) | `corredo/return-air-terminal/griglia-di-ripresa` |
| Z.5 | Chiusura e ripristino di fori, tracce e passaggi | 1 | a corpo | sempre | `attivita/chiusure-e-ripristini` |
| G.1 | Distribuzione aria: 11 rami flessibili interi dal plenum alle bocchette, senza curve rigide: curve del flessibile ampie (raggio in asse non inferiore a un diametro), senza schiacciamenti né anse; UI e plenum arretrati verso il portico quanto serve a curvare ampi all'uscita delle serrande; plenum porta-bocchetta, sostegni e sigillature; bocche protette fino alla posa delle bocchette. | 1 | a corpo | nell'impianto: aria di mandata | `attivita/distribuzione-aria` |
| G.2 | Scarico condensa con sifone e allaccio allo scarico; prova di scarico e della pompa prima della chiusura del controsoffitto. | 1 | a corpo | nell'impianto: condensa | `attivita/scarico-condensa-e-prova` |
| G.3 | Linee elettriche dedicate dal quadro, collegamento fra le unità, linee di comando e bus; posa di termostati e comandi a parete. | 1 | a corpo | nell'impianto: alimentazione elettrica, bus di comando | `attivita/linee-elettriche-e-comandi` |
| G.4 | Dichiarazione di conformità D.M. 37/2008, art. 1 lettera a) (impianti elettrici), con lo schema del quadro aggiornato e gli allegati. | 1 | a corpo | nell'impianto: alimentazione elettrica | `attivita/dico-elettrico` |
| G.5 | Dichiarazione di conformità D.M. 37/2008, art. 1 lettera c) (impianti di climatizzazione), con allegati; documenti per libretto di impianto, catasto regionale e F-Gas. | 1 | a corpo | nell'impianto: aria di mandata | `attivita/dico-climatizzazione` |
| G.6 | Cantiere: POS e oneri della sicurezza (presenza dell'impresa del Committente), trabattello e mezzi di sollevamento. | 1 | a corpo | sempre | `attivita/cantiere` |
| G.7 | Pulizia finale e smaltimento di imballi e residui di lavorazione. | 1 | a corpo | sempre | `attivita/pulizia-e-smaltimenti` |
| V.1 | Flessibile posato oltre la quantità di computo, con fascette e sostegni |  | m | nell'impianto: aria di mandata; solo prezzo unitario | `attivita/variante-flessibile` |
| V.2 | Cavo di alimentazione in corrugato oltre la quantità di computo, stessa sezione |  | m | nell'impianto: alimentazione elettrica; solo prezzo unitario | `attivita/variante-cavo` |
| V.3 | Accesso aggiuntivo in cantiere (oltre i due previsti) |  | n | sempre; solo prezzo unitario | `attivita/variante-accesso` |
| V.4 | Centralino aggiuntivo 8 moduli, se il quadro non ha i moduli liberi per le protezioni nuove |  | n | nell'impianto: Quadro elettrico; solo prezzo unitario | `attivita/variante-centralino` |
| V.5 | Staffe a muro per la pompa di calore al posto del basamento a terra, se il progettista le chiede |  | n | nell'impianto: Pompa di calore aria-acqua; solo prezzo unitario | `attivita/variante-staffe-pdc` |
| V.6 | Cavo scaldante autoregolante sul tratto esterno dello scarico dell'unità esterna, con collegamento elettrico |  | m | sempre; solo prezzo unitario | `attivita/variante-cavo-scaldante` |

## Avvisi

- T12 (Scarico condensa 3: TE-01 - SIF-01 - AL-01): la tubazione SIF-01 - AL-01 senza lunghezza; si considera compresa nei 3 m dati sul tratto.
- T13 (Scarico condensa 1: TE-02 - SIF-02 - AL-02): la tubazione SIF-02 - AL-02 senza lunghezza; si considera compresa nei 3 m dati sul tratto.
- T14 (Scarico condensa 2: TE-03 - SIF-03 - AL-03): la tubazione SIF-03 - AL-03 senza lunghezza; si considera compresa nei 3 m dati sul tratto.
- T01, T02, T03, T04, T05, T06, T07, T08, T09, T10, T11: un tratto e' piu' lungo di una confezione, 1 giunte.
- T01, T02, T03, T04, T05, T06, T07, T08, T09, T10, T11 (aria di mandata): attraversamenti di parete non dati, assunti 1 per tratto (regola Nove C: una parete per ramo, se il progettista non dice quante).
- T12, T13, T14 (condensa): attraversamenti di parete non dati, assunti 1 per tratto (regola Nove C: una parete, se il progettista non dice quante).

## Note

1. «L da quotare» = (L stimata + 1 m) × 1,15, per eccesso a 0,5 m; minimi: fluido frigorigeno in fase liquida, fluido frigorigeno in fase gassosa 12 m; condensa 10 m; bus di comando 5 m; aria di mandata, aria di ripresa 2 m. La L stimata è un dato del progettista, scritta su ogni tratto.
2. Quantità indicative per un prezzo a corpo, fisso e invariabile: l'installatore le verifica nel sopralluogo obbligatorio prima dell'offerta; le varianti hanno solo il prezzo unitario.
3. Fornitura da confermare: apparecchiature fornite da Nove C; bocchette e griglie, opere edili del Committente; messa in servizio con Nove C.
4. La distinta non progetta: lunghezze, sezioni, portate, protezioni, marca e modello sono dati del progettista; la distinta li maggiora e ne conta il corredo con regole scritte, ciascuna con la sua fonte.
