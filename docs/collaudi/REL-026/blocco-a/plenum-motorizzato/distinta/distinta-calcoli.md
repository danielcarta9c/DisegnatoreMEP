# Distinta materiali — foglio dei calcoli (PROVA-B, tavola M.02 rev. 00)

Committente: Committente (dati omessi) · Progetto: Ventilconvettore canalizzato idronico con plenum motorizzato di zona · Data: 13.11.2026

> proposta (D-213, REL-013): il PO non ha ancora deciso se la skill fa la distinta; finché non decide, la distinta si fa solo col comando esplicito `mep.py distinta`. Regole `13d6f4ef01e2a96a` (distinta 1.3.0, lunghezze 1.1.0, fluidi 1.3.0, corredo 1.7.0, attivita 1.2.0, verifica 1.1.0).

## DA DEFINIRE — le domande al progettista

- GT-01 (Pompa di calore aria-acqua): marca e modello li dà il progettista.
- TZ-01, TZ-02, TZ-03, TZ-04 (Termostato di zona): marca e modello li dà il progettista.
- RA-01 (Griglia di ripresa con plenum e filtro): su che tubo sta? Il tubo del suo tratto non c'e': i diametri non sono chiesti su quella rete, o il calcolo non ne ha la portata. Serve la `sezione` del tratto (es. «MS 32×3»).
- Rete «Circuito del ventilconvettore»: quanti metri di tubo, di che diametro e come isolato (preisolato, o nudo con guaina e il suo spessore)? Si scrivono nel blocco «distinta» del grafo.
- VE-01 (Vaso di espansione): manca il dato «volume_l» per «Vaso di espansione chiuso a membrana per riscaldamento DA DEFINIRE (volume_l) l, con attacco e staffa».
- VIB-01 (Valvola di intercettazione bloccabile aperta): su che tubo sta? Il tubo del suo tratto non c'e': i diametri non sono chiesti su quella rete, o il calcolo non ne ha la portata. Serve la `sezione` del tratto (es. «MS 32×3»).
- T06 (Alimentazione centrale di zona): manca `protezione` sul tratto.
- T08 (Alimentazione ventilconvettore): manca `protezione` sul tratto.
- T07 (Alimentazione pompa di calore): manca `protezione` sul tratto.
- «Ventilconvettore canalizzato» (TE-01) non ha corredo di posa nelle regole della distinta: chi lo fornisce e che cosa porta con se'? Si scrive nelle regole della distinta (corredo).

## Da confermare per questa offerta

- Fornitura: apparecchiature fornite da Nove C; bocchette e griglie del Committente; opere edili del Committente; messa in servizio con Nove C — come da regole predefinite di Nove C; confermare per questa offerta.

## Le tratte

| tratto | rete | da - a | sezione | L stimata | L da quotare | conto |
|---|---|---|---|---|---|---|
| T01 | Mandata aria 1 | PLZ-01 - TA-01 | Ø160 | 3 | 5 | (3 + 1) × 1,15 = 4,6 → 5 m |
| T02 | Mandata aria 1 | PLZ-01 - TA-02 | Ø160 | 4 | 6 | (4 + 1) × 1,15 = 5,75 → 6 m |
| T03 | Mandata aria 1 | PLZ-01 - TA-03 | Ø160 | 5 | 7 | (5 + 1) × 1,15 = 6,9 → 7 m |
| T04 | Mandata aria 1 | PLZ-01 - TA-04 | Ø160 | 6 | 8,5 | (6 + 1) × 1,15 = 8,05 → 8,5 m |
| T05 | Scarico condensa 1 | TE-01 - SIF-01 - AL-01 | Ø32 | 3 | 10 | (3 + 1) × 1,15 = 4,6 → 5 m; minimo condensa 10 m → 10 m |
| T06 | Alimentazione centrale di zona | QE-01 - CZ-01 | 3G1,5 | 9 | 11,5 | (9 + 1) × 1,15 = 11,5 → 11,5 m |
| T07 | Alimentazione pompa di calore | QE-01 - GT-01 | 3G2,5 | 12 | 15 | (12 + 1) × 1,15 = 14,95 → 15 m |
| T08 | Alimentazione ventilconvettore | QE-01 - TE-01 | 3G1,5 | 9 | 11,5 | (9 + 1) × 1,15 = 11,5 → 11,5 m |
| T09 | Collegamento centrale-ventilconvettore | CZ-01 - TE-01 | bus | 2 | 5 | (2 + 1) × 1,15 = 3,45 → 3,5 m; minimo bus 5 m → 5 m |
| T10 | Bus della centrale ai termostati | CZ-01 - TZ-01 | bus | 6 | 8,5 | (6 + 1) × 1,15 = 8,05 → 8,5 m |
| T11 | Bus della centrale ai termostati | CZ-01 - TZ-02 | bus | 6 | 8,5 | (6 + 1) × 1,15 = 8,05 → 8,5 m |
| T12 | Bus della centrale ai termostati | CZ-01 - TZ-03 | bus | 6 | 8,5 | (6 + 1) × 1,15 = 8,05 → 8,5 m |
| T13 | Bus della centrale ai termostati | CZ-01 - TZ-04 | bus | 6 | 8,5 | (6 + 1) × 1,15 = 8,05 → 8,5 m |

## La verifica (segnala, non corregge)

| dove | controllo | valore | soglia | esito |
|---|---|---|---|---|
| T01 | velocità | manca la portata (`portata_m3h`) | ≤ 3 m/s | non verificabile |
| T02 | velocità | manca la portata (`portata_m3h`) | ≤ 3 m/s | non verificabile |
| T03 | velocità | manca la portata (`portata_m3h`) | ≤ 3 m/s | non verificabile |
| T04 | velocità | manca la portata (`portata_m3h`) | ≤ 3 m/s | non verificabile |

## Le voci, con la regola e il conto

| rif | voce | q.tà | um | conto | regola |
|---|---|---|---|---|---|
| A.1 | Pompa di calore aria-acqua: marca e modello DA DEFINIRE | 1 | n | 1 nello schema (GT-01) | `corredo/heat-pump-air-water/apparecchiatura` |
| A.2 | Plenum motorizzato di zona a quattro serrande: Marca di prova plenum motorizzato a 4 serrande | 1 | n | 1 nello schema (PLZ-01) | `corredo/zoning-plenum-4/apparecchiatura` |
| A.3 | Termostato di zona: marca e modello DA DEFINIRE | 4 | n | 4 nello schema (TZ-01, TZ-02, TZ-03, TZ-04) | `corredo/room-thermostat/apparecchiatura` |
| S.1 | Basamento a terra per l'unità esterna con supporti antivibranti | 1 | n | GT-01: 1 | `corredo/heat-pump-air-water/basamento-pdc` |
| S.2 | Sospensione del plenum motorizzato (flangiato sulla mandata dell'unità interna): 4 barre filettate M10 con ancoranti, dadi e antivibranti | 1 | kit | PLZ-01: 1 | `corredo/zoning-plenum-4/sospensione-plenum-di-zona` |
| S.3 | Sospensione del plenum di ripresa: 2 barre filettate M8 con ancoranti e dadi | 1 | kit | RA-01: 1 | `corredo/return-air-terminal/sospensione-plenum-di-ripresa` |
| B.1 | Condotto flessibile coibentato Ø160 (isolamento 25 mm, barriera vapore), confezione da 10 m | 4 | conf. | 4 pezzi interi, 26,5 m: in confezioni da 10 m (utili 9,5) ne servono 4 [8,5] [7] [6] [5]; riserva 25%: 26,5 × 1,25 = 33,12 m → 4; si prende il maggiore: 4 | `fluidi/supply_air/flessibile-in-confezioni` |
| B.2 | Manicotto di giunzione Ø160 | 2 | n | 2 per sezione | `fluidi/supply_air/manicotto-di-riserva` |
| B.3 | Fascetta di serraggio Ø160 (anima e mantello) | 16 | n | 4 tratti × 4 = 16 | `fluidi/supply_air/fascette` |
| B.4 | Nastro alluminio rinforzato 50 mm | 2 | rotolo | 26,5 m / 20 m per eccesso, almeno 1 = 2 | `fluidi/supply_air/nastro-alluminio` |
| B.5 | Sostegno per flessibile (fascia o collare con pendino), passo ≤ 1,2 m | 28 | n | T01 6 + T02 6 + T03 7 + T04 9 = 28 (L / 1,2 m per eccesso +1 per tratto) | `fluidi/supply_air/sostegni` |
| B.6 | Plenum porta-bocchetta coibentato per bocchetta 300×150, attacco Ø160 laterale | 4 | n | 4 pezzi × 1 = 4 (TA-01, TA-02, TA-03, TA-04) | `corredo/air-supply-terminal/plenum-porta-bocchetta` |
| B.7 | Isolamento elastomerico adesivo 13 mm per manicotti, raccordi, derivazione e plenum | 2 | rotolo | PLZ-01: 2 | `corredo/zoning-plenum-4/isolamento-raccordi-plenum` |
| B.8 | Plenum di ripresa in lamiera zincata, non coibentato, con filtro ispezionabile, bocca DA DEFINIRE (sezione), sulla bocca di aspirazione dell'unità interna; filtro unico: l'eventuale filtro di serie dell'unità interna si toglie | 1 | n | RA-01: 1 | `corredo/return-air-terminal/plenum-di-ripresa` |
| D.1 | Tubo PVC rigido Ø32 | 10 | m | T05 10 m | `fluidi/condensate/tubo-pvc` |
| D.2 | Curva 87°-90° Ø32 | 6 | n | T05 6 (L / 2 m per eccesso +1 per tratto) | `fluidi/condensate/curve-condensa` |
| D.3 | Manicotto Ø32 | 3 | n | T05 3 (L / 3 m per eccesso -1 per tratto) | `fluidi/condensate/manicotti-condensa` |
| D.4 | Collare per tubo condensa | 10 | n | T05 10 (L / 1 m per eccesso per tratto) | `fluidi/condensate/collari-condensa` |
| D.5 | Isolamento anticondensa 9 mm per il tubo della condensa | 10 | m | T05 10 m | `fluidi/condensate/isolamento-anticondensa` |
| D.6 | Collante e pulitore PVC | 1 | n | 1 per fluido | `fluidi/condensate/collante-pvc` |
| D.7 | Innesto sullo scarico esistente con braga 45° Ø40, a valle del sifone dell'apparecchio | 1 | n | AL-01: 1 | `corredo/condensate-outlet/innesto-sullo-scarico` |
| D.8 | Sifone ispezionabile per condensa | 1 | n | SIF-01: 1 | `corredo/condensate-trap/sifone` |
| I.1 | Tubo della rete «Circuito del ventilconvettore»: diametro, metri e isolamento DA DEFINIRE | DA DEFINIRE | m | mancano i metri della rete | `fluidi/heating_water/tubo` |
| I.2 | Defangatore magnetico ¾" | 1 | n | DEF-01: 1 | `corredo/dirt-separator/pezzo` |
| I.3 | Vaso di espansione chiuso a membrana per riscaldamento DA DEFINIRE (volume_l) l, con attacco e staffa | 1 | n | VE-01: 1 | `corredo/expansion-connection/pezzo` |
| I.4 | Giunto antivibrante ¾" | 2 | n | 2 pezzi × 1 = 2 (GA-02, GA-01) | `corredo/flexible-joint/pezzo` |
| I.5 | Pulitore per impianti nuovi o recenti, 1 l | 1 | n | GT-01: 1 | `corredo/heat-pump-air-water/pulitore` |
| I.6 | Filmante e inibitore per impianti, 1 l | 1 | n | GT-01: 1 | `corredo/heat-pump-air-water/filmante` |
| I.7 | Manometro 0-6 bar attacco ½" | 1 | n | MN-01: 1 | `corredo/pressure-gauge/pezzo` |
| I.8 | Filtro a Y ¾" FF, maglia 500 µm | 1 | n | FIL-01: 1 | `corredo/strainer/pezzo` |
| I.9 | Tee a pressare tubo multistrato MS 26×3 | 3 | n | 3 pezzi × 1 = 3 (DER-03, DER-02, DER-01) | `corredo/tee-branch/tee` |
| I.10 | Rubinetto portamanometro a tre vie ½" | 1 | n | RM-01: 1 | `corredo/valve-gauge-cock-3way/pezzo` |
| I.11 | Valvola a sfera a passaggio totale ¾" FF, con leva | 3 | n | 3 pezzi × 1 = 3 (VI-02, VI-03, VI-01) | `corredo/valve-isolation/pezzo` |
| I.12 | Valvola a sfera a passaggio totale DA DEFINIRE (pollice) FF, con leva | 1 | n | VIB-01: 1 | `corredo/valve-isolation-locked-open/pezzo` |
| I.13 | Valvola di sicurezza ½" MF 3 bar, con scarico convogliato | 1 | n | VS-01: 1 | `corredo/valve-safety/pezzo` |
| I.14 | Raccordo diritto a pressare M ¾" × tubo multistrato MS 26×3 | 10 | n | 10 giunzioni: GA-01 (GA-01 – DER-01); VI-01 (DER-01 – VI-01); VI-01 (VI-01 – TE-01); VI-02 (TE-01 – VI-02); VI-03 (VI-03 – DER-02); FIL-01 (DER-03 – FIL-01); FIL-01 (FIL-01 – GA-02); GA-02 (FIL-01 – GA-02); VIB-01 (DER-03 – VIB-01); RM-01 (DER-02 – RM-01) | `corredo/giunzioni/raccordo` |
| I.15 | Raccordo diritto a pressare M × tubo multistrato MS 26×3, all'attacco | 2 | n | 2 giunzioni: TE-01 (VI-01 – TE-01); TE-01 (TE-01 – VI-02) | `corredo/giunzioni/raccordo-all-attacco` |
| I.16 | Nipplo ¾" M × M | 2 | n | 2 giunzioni: VI-02 – DEF-01; DEF-01 – VI-03 | `corredo/giunzioni/nipplo` |
| E.1 | Cavo FG16OR16 3G1,5, Alimentazione centrale di zona, Alimentazione ventilconvettore | 23 | m | T06 11,5 + T08 11,5 = 23 m | `fluidi/power_supply/cavo-di-alimentazione` |
| E.2 | Cavo FG16OR16 3G2,5, Alimentazione pompa di calore | 15 | m | T07 15 m | `fluidi/power_supply/cavo-di-alimentazione` |
| E.3 | DA DEFINIRE (protezione), linea dedicata: Alimentazione centrale di zona, Alimentazione ventilconvettore | 2 | n | una per tratto: T06, T08 | `fluidi/power_supply/protezione-della-linea` |
| E.4 | DA DEFINIRE (protezione), linea dedicata: Alimentazione pompa di calore | 1 | n | una per tratto: T07 | `fluidi/power_supply/protezione-della-linea` |
| E.5 | Scatola di derivazione IP55 | 3 | n | 3 tratti × 1 = 3 | `fluidi/power_supply/scatola-di-derivazione` |
| E.6 | Tubo corrugato Ø25 per le linee di alimentazione | 40 | m | T06 11,5 + T07 15 + T08 11,5 = 38 m × 1, per eccesso a 10 m = 40 m | `fluidi/power_supply/corrugato-di-potenza` |
| E.7 | Cavo bus, Collegamento centrale-ventilconvettore, Bus della centrale ai termostati | 39 | m | T09 5 + T10 8,5 + T11 8,5 + T12 8,5 + T13 8,5 = 39 m | `fluidi/control_bus/cavo-di-bus` |
| E.8 | Tubo corrugato Ø20 per bus e linee di comando | 40 | m | T09 5 + T10 8,5 + T11 8,5 + T12 8,5 + T13 8,5 = 39 m × 1, per eccesso a 10 m = 40 m | `fluidi/control_bus/corrugato-di-bus` |
| E.9 | Aggiornamento dello schema del quadro elettrico | 1 | a corpo | QE-01: 1 | `corredo/electrical-panel/aggiornamento-schema-quadro` |
| E.10 | Scatola 503 per termostati e comandi a parete | 4 | n | 4 pezzi × 1 = 4 (TZ-01, TZ-02, TZ-03, TZ-04) | `corredo/room-thermostat/scatola-503` |
| F.1 | Foratura di tramezza Ø300 (o vano 470×270) per flessibili coibentati e plenum di bocchetta | 4 | n | T01 1 + T02 1 + T03 1 + T04 1 = 4 | `fluidi/supply_air/foratura-per-flessibile` |
| F.2 | Foratura per lo scarico della condensa (tramezze e parete del bagno) | 1 | n | T05 1 | `fluidi/condensate/foratura-condensa` |
| F.3 | Tracce per le linee dal quadro al controsoffitto | 7,5 | m | QE-01: 7,5 | `corredo/electrical-panel/tracce-dal-quadro` |
| F.4 | Traccia per la condensa fino allo scarico | 3 | m | AL-01: 3 | `corredo/condensate-outlet/traccia-condensa` |
| F.5 | Traccia per termostati e comandi a parete, dal controsoffitto alla scatola | 5,6 | m | 4 pezzi × 1,4 = 5,6 (TZ-01, TZ-02, TZ-03, TZ-04) | `corredo/room-thermostat/traccia-per-apparecchio-a-parete` |
| X.1 | Ventilconvettore canalizzato: fornitura e corredo di posa DA DEFINIRE | 1 | n | 1 nello schema (TE-01) | `corredo/fan-coil-ducted-air (manca)` |
| Z.1 | Velette o controsoffitti per le bocchette, altezza utile ≥ 30 cm | 1 | a corpo | 1 per fluido | `fluidi/supply_air/velette-per-le-bocchette` |
| Z.2 | Bocchetta di mandata 300×150 a doppio filare con serranda | 4 | n | 4 pezzi × 1 = 4 (TA-01, TA-02, TA-03, TA-04) | `corredo/air-supply-terminal/bocchetta-di-mandata` |
| Z.3 | Griglia di transito o luce sotto porta per il ritorno dell'aria dal locale servito | 4 | n | 4: 4 locali serviti (Camera 1, Camera 2, Soggiorno, Studio); il locale e' letto dall'etichetta della bocchetta | `corredo/air-supply-terminal/griglia-di-transito` |
| Z.4 | Botola di ispezione ≥ 600×600 sotto la macchina (filtro, pompa, scheda) | 1 | n | PLZ-01: 1 | `corredo/zoning-plenum-4/botola-di-ispezione` |
| Z.5 | Copertura Wi-Fi in zona plenum e centrale di zona, per la configurazione e l'app | 1 | a corpo | PLZ-01: 1 | `corredo/zoning-plenum-4/copertura-wifi` |
| Z.6 | Griglia di ripresa DA DEFINIRE (sezione) senza filtro, apribile per accedere al filtro | 1 | n | RA-01: 1 | `corredo/return-air-terminal/griglia-di-ripresa` |
| Z.7 | Chiusura e ripristino di fori, tracce e passaggi | 1 | a corpo | sempre | `attivita/chiusure-e-ripristini` |
| G.1 | Distribuzione aria: 4 rami flessibili interi dal plenum alle bocchette, senza curve rigide: curve del flessibile ampie (raggio in asse non inferiore a un diametro), senza schiacciamenti né anse; UI e plenum arretrati verso il portico quanto serve a curvare ampi all'uscita delle serrande; plenum porta-bocchetta, sostegni e sigillature; bocche protette fino alla posa delle bocchette. | 1 | a corpo | nell'impianto: aria di mandata | `attivita/distribuzione-aria` |
| G.2 | Scarico condensa con sifone e allaccio allo scarico; prova di scarico e della pompa prima della chiusura del controsoffitto. | 1 | a corpo | nell'impianto: condensa | `attivita/scarico-condensa-e-prova` |
| G.3 | Linee elettriche dedicate dal quadro, collegamento fra le unità, linee di comando e bus; posa di termostati e comandi a parete. | 1 | a corpo | nell'impianto: alimentazione elettrica, bus di comando | `attivita/linee-elettriche-e-comandi` |
| G.4 | Dichiarazione di conformità D.M. 37/2008, art. 1 lettera a) (impianti elettrici), con lo schema del quadro aggiornato e gli allegati. | 1 | a corpo | nell'impianto: alimentazione elettrica | `attivita/dico-elettrico` |
| G.5 | Dichiarazione di conformità D.M. 37/2008, art. 1 lettera c) (impianti di climatizzazione), con allegati; documenti per libretto di impianto, catasto regionale e F-Gas. | 1 | a corpo | nell'impianto: aria di mandata | `attivita/dico-climatizzazione` |
| G.6 | Cantiere: POS e oneri della sicurezza (presenza dell'impresa del Committente), trabattello e mezzi di sollevamento. | 1 | a corpo | sempre | `attivita/cantiere` |
| G.7 | Trasporto, ricevimento e custodia delle apparecchiature fornite da Nove C fino al collaudo; protezioni delle macchine e delle bocche durante le opere edili. | 1 | a corpo | nell'impianto: Plenum motorizzato di zona a quattro serrande | `attivita/custodia-e-protezioni` |
| G.8 | Pulizia finale e smaltimento di imballi e residui di lavorazione. | 1 | a corpo | sempre | `attivita/pulizia-e-smaltimenti` |
| V.1 | Flessibile posato oltre la quantità di computo, con fascette e sostegni |  | m | nell'impianto: aria di mandata; solo prezzo unitario | `attivita/variante-flessibile` |
| V.2 | Cavo di alimentazione in corrugato oltre la quantità di computo, stessa sezione |  | m | nell'impianto: alimentazione elettrica; solo prezzo unitario | `attivita/variante-cavo` |
| V.3 | Accesso aggiuntivo in cantiere (oltre i due previsti) |  | n | sempre; solo prezzo unitario | `attivita/variante-accesso` |
| V.4 | Centralino aggiuntivo 8 moduli, se il quadro non ha i moduli liberi per le protezioni nuove |  | n | nell'impianto: Quadro elettrico; solo prezzo unitario | `attivita/variante-centralino` |
| V.5 | Staffe a muro per la pompa di calore al posto del basamento a terra, se il progettista le chiede |  | n | nell'impianto: Pompa di calore aria-acqua; solo prezzo unitario | `attivita/variante-staffe-pdc` |
| V.6 | Cavo scaldante autoregolante sul tratto esterno dello scarico dell'unità esterna, con collegamento elettrico |  | m | sempre; solo prezzo unitario | `attivita/variante-cavo-scaldante` |

## Avvisi

- T05 (Scarico condensa 1: TE-01 - SIF-01 - AL-01): la tubazione SIF-01 - AL-01 senza lunghezza; si considera compresa nei 3 m dati sul tratto.
- T01, T02, T03, T04 (aria di mandata): attraversamenti di parete non dati, assunti 1 per tratto (regola Nove C: una parete per ramo, se il progettista non dice quante).
- T05 (condensa): attraversamenti di parete non dati, assunti 1 per tratto (regola Nove C: una parete, se il progettista non dice quante).

## Note

1. «L da quotare» = (L stimata + 1 m) × 1,15, per eccesso a 0,5 m; minimi: fluido frigorigeno in fase liquida, fluido frigorigeno in fase gassosa 12 m; condensa 10 m; bus di comando 5 m; aria di mandata, aria di ripresa 2 m. La L stimata è un dato del progettista, scritta su ogni tratto.
2. Quantità indicative per un prezzo a corpo, fisso e invariabile: l'installatore le verifica nel sopralluogo obbligatorio prima dell'offerta; le varianti hanno solo il prezzo unitario.
3. Fornitura da confermare: apparecchiature fornite da Nove C; bocchette e griglie, opere edili del Committente; messa in servizio con Nove C.
4. La distinta non progetta: lunghezze, sezioni, portate, protezioni, marca e modello sono dati del progettista; la distinta li maggiora e ne conta il corredo con regole scritte, ciascuna con la sua fonte.
