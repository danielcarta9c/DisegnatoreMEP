# Distinta materiali — foglio dei calcoli (AA-01, tavola M.02 rev. 00)

Committente: Committente (dati omessi) · Progetto: Climatizzazione canalizzata Daikin con zonizzazione Airzone · Data: 29.10.2026

> proposta (D-213, REL-013): il PO non ha ancora deciso se la skill fa la distinta; finché non decide, la distinta si fa solo col comando esplicito `mep.py distinta`. Regole `f8b849f909489495` (distinta 1.1.0, lunghezze 1.1.0, fluidi 1.1.0, corredo 1.1.0, attivita 1.1.0, verifica 1.1.0).

## Da confermare per questa offerta

- Fornitura: apparecchiature fornite da Nove C; bocchette e griglie del Committente; opere edili del Committente; messa in servizio con Nove C — come da regole predefinite di Nove C; confermare per questa offerta.

## Le tratte

| tratto | rete | da - a | sezione | L stimata | L da quotare | conto |
|---|---|---|---|---|---|---|
| T01 | Mandata aria alle zone | PLZ-01 - B1 | Ø200 | 4,1 | 6 | (4,1 + 1) × 1,15 = 5,86 → 6 m |
| T02 | Mandata aria alle zone | PLZ-01 - B2 | Ø200 | 2 | 3,5 | (2 + 1) × 1,15 = 3,45 → 3,5 m |
| T03 | Mandata aria alle zone | PLZ-01 - B3 | Ø200 | 4,2 | 6 | (4,2 + 1) × 1,15 = 5,98 → 6 m |
| T04 | Mandata aria alle zone | PLZ-01 - B4 | Ø200 | 2 | 3,5 | (2 + 1) × 1,15 = 3,45 → 3,5 m |
| T05 | Mandata aria alle zone | PLZ-01 - B5 | Ø200 | 4,8 | 7 | (4,8 + 1) × 1,15 = 6,67 → 7 m |
| T06 | Ripresa aria | RA-01 - UI-01 | 1000×250 |  |  | raccordo diretto |
| T07 | Linea del liquido | UE-01 - UI-01 | Ø6,35 (1/4") | 8 | 12 | (8 + 1) × 1,15 = 10,35 → 10,5 m; minimo frigo 12 m → 12 m |
| T08 | Linea del gas | UE-01 - UI-01 | Ø12,7 (1/2") | 8 | 12 | (8 + 1) × 1,15 = 10,35 → 10,5 m; minimo frigo 12 m → 12 m |
| T09 | Scarico condensa | UI-01 - SIF-01 - AL-01 | Ø32 | 7,6 | 10 | (7,6 + 1) × 1,15 = 9,89 → 10 m |
| T10 | Alimentazione centrale Airzone | QE-01 - CZ-01 | 3G1,5 | 12 | 15 | (12 + 1) × 1,15 = 14,95 → 15 m |
| T11 | Alimentazione unita' esterna | QE-01 - SZ-01 - UE-01 | 3G2,5 | 15 | 20 | (15 + 1) × 1,15 = 18,4 → 18,5 m; minimo scritto sul tratto 20 m → 20 m |
| T12 | Collegamento UI-UE | UE-01 - UI-01 | 4G1,5 | 9 | 13 | (9 + 1) × 1,15 = 11,5 → 11,5 m; segue T07 + 1 m: 13 m → 13 m |
| T13 | Bus Airzone ai termostati | CZ-01 - TZ-01 | bus Airzone, schermato | 6,5 | 9 | (6,5 + 1) × 1,15 = 8,62 → 9 m |
| T14 | Bus Airzone ai termostati | CZ-01 - TZ-02 | bus Airzone, schermato | 4,9 | 7 | (4,9 + 1) × 1,15 = 6,79 → 7 m |
| T15 | Bus Airzone ai termostati | CZ-01 - TZ-03 | bus Airzone, schermato | 5,2 | 7,5 | (5,2 + 1) × 1,15 = 7,13 → 7,5 m |
| T16 | Bus Airzone ai termostati | CZ-01 - TZ-04 | bus Airzone, schermato | 3,7 | 5,5 | (3,7 + 1) × 1,15 = 5,4 → 5,5 m |
| T17 | Linea P1-P2 dell'unita' interna | UI-01 - CF-01 | 2×0,75 (P1-P2) | 3,7 | 5,5 | (3,7 + 1) × 1,15 = 5,4 → 5,5 m |
| T18 | Linea P1-P2 dell'unita' interna | UI-01 - CZ-01 | 2×0,75 (P1-P2) | 1,5 | 5 | (1,5 + 1) × 1,15 = 2,88 → 3 m; minimo bus 5 m → 5 m |

## La verifica (segnala, non corregge)

| dove | controllo | valore | soglia | esito |
|---|---|---|---|---|
| T01 | velocità | 270 m³/h su Ø200: 2,39 m/s | ≤ 3 m/s | entro |
| T02 | velocità | 280 m³/h su Ø200: 2,48 m/s | ≤ 3 m/s | entro |
| T03 | velocità | 210 m³/h su Ø200: 1,86 m/s | ≤ 3 m/s | entro |
| T04 | velocità | 275 m³/h su Ø200: 2,43 m/s | ≤ 3 m/s | entro |
| T05 | velocità | 275 m³/h su Ø200: 2,43 m/s | ≤ 3 m/s | entro |
| T06 | velocità | 1080 m³/h su 1000×250: 1,2 m/s | ≤ 2 m/s | entro |
| Camera 13 m² | griglia di transito | 270 m³/h a 1,5 m/s | Aeff ≥ 0,05 m² | da rispettare |
| Camera 15 m² | griglia di transito | 280 m³/h a 1,5 m/s | Aeff ≥ 0,052 m² | da rispettare |
| Camera 16 m² | griglia di transito | 210 m³/h a 1,5 m/s | Aeff ≥ 0,039 m² | da rispettare |
| Soggiorno-cucina | griglia di transito | 550 m³/h a 1,5 m/s | Aeff ≥ 0,102 m² | da rispettare |
| T07 | lunghezza della linea frigorifera | 12 m da quotare | ≤ 30 m (UE-01) | entro |
| T08 | lunghezza della linea frigorifera | 12 m da quotare | ≤ 30 m (UE-01) | entro |
| T01 | scritta sulla tavola | «Ø200 · 270 m³/h · L 6 m» | L 6 m da quotare | entro |
| T02 | scritta sulla tavola | «Ø200 · 280 m³/h · L 3,5 m» | L 3,5 m da quotare | entro |
| T03 | scritta sulla tavola | «Ø200 · 210 m³/h · L 6 m» | L 6 m da quotare | entro |
| T04 | scritta sulla tavola | «Ø200 · 275 m³/h · L 3,5 m» | L 3,5 m da quotare | entro |
| T05 | scritta sulla tavola | «Ø200 · 275 m³/h · L 7 m» | L 7 m da quotare | entro |
| T07 | scritta sulla tavola | «Ø6,35 (1/4") · L 12 m» | L 12 m da quotare | entro |
| T08 | scritta sulla tavola | «Ø12,7 (1/2") · L 12 m» | L 12 m da quotare | entro |
| T09 | scritta sulla tavola | «PVC Ø32 · L 10 m» | L 10 m da quotare | entro |
| T10 | scritta sulla tavola | «3G1,5 · L 15 m» | L 15 m da quotare | entro |
| T11 | scritta sulla tavola | «3G2,5 · L 20 m» | L 20 m da quotare | entro |
| T12 | scritta sulla tavola | «4G1,5 · L 13 m» | L 13 m da quotare | entro |
| T13 | scritta sulla tavola | «bus · L 9 m» | L 9 m da quotare | entro |
| T14 | scritta sulla tavola | «bus · L 7 m» | L 7 m da quotare | entro |
| T15 | scritta sulla tavola | «bus · L 7,5 m» | L 7,5 m da quotare | entro |
| T16 | scritta sulla tavola | «bus · L 5,5 m» | L 5,5 m da quotare | entro |
| T17 | scritta sulla tavola | «P1-P2 · L 5,5 m» | L 5,5 m da quotare | entro |
| T18 | scritta sulla tavola | «P1-P2 · L 3 m» | L 5 m da quotare | oltre |

## Le voci, con la regola e il conto

| rif | voce | q.tà | um | conto | regola |
|---|---|---|---|---|---|
| A.1 | Comando a filo dell'unità: Daikin Madoka BRC1H52W | 1 | n | 1 nello schema (CF-01) | `corredo/wired-remote/apparecchiatura` |
| A.2 | Plenum motorizzato di zona a cinque serrande: Airzone Easyzone 5 × Ø200, es. AZEZ8DAIBS07M5 · 1425×250×454 mm | 1 | n | 1 nello schema (PLZ-01) | `corredo/zoning-plenum-5/apparecchiatura` |
| A.3 | Termostato di zona: Airzone Blueface | 4 | n | 4 nello schema (TZ-01, TZ-02, TZ-03, TZ-04) | `corredo/room-thermostat/apparecchiatura` |
| A.4 | Unità esterna split a pompa di calore: Daikin RXM60A · 49 kg | 1 | n | 1 nello schema (UE-01) | `corredo/split-outdoor-unit/apparecchiatura` |
| A.5 | Unità interna canalizzata ad espansione diretta: Daikin FBA60A9 · 1000×800×245 mm · 35 kg | 1 | n | 1 nello schema (UI-01) | `corredo/ducted-indoor-unit/apparecchiatura` |
| B.1 | Condotto flessibile coibentato Ø200 (isolamento 25 mm, barriera vapore), confezione da 10 m | 4 | conf. | 5 pezzi interi, 26 m: in confezioni da 10 m (utili 9,5) ne servono 3 [7] [6 + 3,5] [6 + 3,5]; riserva 25%: 26 × 1,25 = 32,5 m → 4; si prende il maggiore: 4 | `fluidi/supply_air/flessibile-in-confezioni` |
| B.2 | Curva 90° Ø200 in lamiera zincata, all'uscita del plenum | 5 | n | 5 tratti × 1 = 5 | `fluidi/supply_air/curva-in-lamiera` |
| B.3 | Manicotto di giunzione Ø200 | 2 | n | 2 per sezione | `fluidi/supply_air/manicotto-di-riserva` |
| B.4 | Fascetta di serraggio Ø200 (anima e mantello) | 40 | n | 5 tratti × 8 = 40 | `fluidi/supply_air/fascette` |
| B.5 | Nastro alluminio rinforzato 50 mm | 2 | rotolo | 26 m / 20 m per eccesso, almeno 1 = 2 | `fluidi/supply_air/nastro-alluminio` |
| B.6 | Sostegno per flessibile (fascia o collare con pendino), passo ≤ 1,2 m | 27 | n | T01 6 + T02 4 + T03 6 + T04 4 + T05 7 = 27 (L / 1,2 m per eccesso +1 per tratto) | `fluidi/supply_air/sostegni` |
| B.7 | Plenum porta-bocchetta coibentato per bocchetta 400×200, attacco Ø200 laterale o dall'alto | 5 | n | 5 pezzi × 1 = 5 (B1, B2, B3, B4, B5) | `corredo/air-supply-terminal/plenum-porta-bocchetta` |
| B.8 | Kit sospensione: barra filettata M10, tassello per solaio in laterocemento, antivibrante | 10 | n | PLZ-01 4 + RA-01 2 + UI-01 4 = 10 | `corredo/zoning-plenum-5/kit-sospensione + corredo/return-air-terminal/kit-sospensione + corredo/ducted-indoor-unit/kit-sospensione` |
| B.9 | Isolamento elastomerico adesivo per raccordi e plenum | 1 | rotolo | PLZ-01: 1 | `corredo/zoning-plenum-5/isolamento-raccordi-plenum` |
| B.10 | Plenum di ripresa coibentato con filtro ispezionabile, bocca 1000×250, sulla bocca di aspirazione dell'unità interna | 1 | n | RA-01: 1 | `corredo/return-air-terminal/plenum-di-ripresa` |
| B.11 | Giunto antivibrante in tela fra unità interna e plenum di ripresa | 1 | n | UI-01: 1 | `corredo/ducted-indoor-unit/giunto-antivibrante-ripresa` |
| C.1 | Tubo rame ricotto pre-isolato Ø6,35 (1/4"), isolamento ≥ 10 mm, resistente a 120 °C | 12 | m | T07 12 m | `fluidi/refrigerant_liquid/tubo-rame-liquido` |
| C.2 | Manicotto a brasare Ø6,35 (1/4") (riserva, posa in tratta unica) | 2 | n | 2 per sezione | `fluidi/refrigerant_liquid/manicotti-a-brasare-liquido` |
| C.3 | Tubo rame ricotto pre-isolato Ø12,7 (1/2"), isolamento ≥ 13 mm, resistente a 120 °C | 12 | m | T08 12 m | `fluidi/refrigerant_gas/tubo-rame-gas` |
| C.4 | Manicotto a brasare Ø12,7 (1/2") (riserva, posa in tratta unica) | 2 | n | 2 per sezione | `fluidi/refrigerant_gas/manicotti-a-brasare-gas` |
| C.5 | Nastro di finitura e manicotti isolanti per le giunzioni a cartella | 1 | kit | 1 tratto × 1 = 1 | `fluidi/refrigerant_gas/nastro-e-manicotti-isolanti` |
| C.6 | Collare di sostegno linee frigorifere in controsoffitto | 10 | n | T08 10 (L / 1,2 m per eccesso per tratto) | `fluidi/refrigerant_gas/collari-linee-frigo` |
| C.7 | Refrigerante R32, riserva per carica aggiuntiva | 0,2 | kg | T08: (12 - 10 m) × 20 g/m = 0,04 kg, almeno 0,2 kg → 0,2 kg | `fluidi/refrigerant_gas/carica-aggiuntiva` |
| C.8 | Canalina coprilinee esterna 80×60 | 4 | m | UE-01: 4 | `corredo/split-outdoor-unit/canalina-esterna` |
| C.9 | Accessori canalina: curva 2, terminale a muro 1, giunto 2 | 1 | kit | UE-01: 1 | `corredo/split-outdoor-unit/accessori-canalina` |
| C.10 | Staffe a parete per unità esterna, portata almeno doppia del peso della macchina, con antivibranti | 1 | kit | UE-01: 1 | `corredo/split-outdoor-unit/staffe-unita-esterna` |
| C.11 | Scarico condensa dell'unità esterna (funziona anche in caldo): raccordo e tubo Ø16 fino a pluviale o pozzetto | 4 | m | UE-01: 4 | `corredo/split-outdoor-unit/scarico-condensa-unita-esterna` |
| D.1 | Tubo PVC rigido Ø32 | 10 | m | T09 10 m | `fluidi/condensate/tubo-pvc` |
| D.2 | Curva 87°-90° Ø32 | 6 | n | T09 6 (L / 2 m per eccesso +1 per tratto) | `fluidi/condensate/curve-condensa` |
| D.3 | Manicotto Ø32 | 3 | n | T09 3 (L / 3 m per eccesso -1 per tratto) | `fluidi/condensate/manicotti-condensa` |
| D.4 | Collare per tubo condensa | 10 | n | T09 10 (L / 1 m per eccesso per tratto) | `fluidi/condensate/collari-condensa` |
| D.5 | Isolamento anticondensa 9 mm per il tubo della condensa | 10 | m | T09 10 m | `fluidi/condensate/isolamento-anticondensa` |
| D.6 | Collante e pulitore PVC | 1 | n | 1 per fluido | `fluidi/condensate/collante-pvc` |
| D.7 | Innesto sullo scarico esistente (braga 45° o presa sul sifone di un apparecchio) | 1 | n | AL-01: 1 | `corredo/condensate-outlet/innesto-sullo-scarico` |
| D.8 | Sifone ispezionabile per condensa | 1 | n | SIF-01: 1 | `corredo/condensate-trap/sifone` |
| D.9 | Raccordo di adattamento dall'attacco condensa dell'unità interna (VP20 (Øe 26)) al tubo di scarico, con fascetta | 1 | n | UI-01: 1 | `corredo/ducted-indoor-unit/raccordo-condensa-unita-interna` |
| E.1 | Cavo FG16OR16 3G1,5, Alimentazione centrale Airzone | 15 | m | T10 15 m | `fluidi/power_supply/cavo-di-alimentazione` |
| E.2 | Cavo FG16OR16 3G2,5, Alimentazione unita' esterna | 20 | m | T11 20 m | `fluidi/power_supply/cavo-di-alimentazione` |
| E.3 | Magnetotermico 1P+N C6, linea dedicata: Alimentazione centrale Airzone | 1 | n | una per tratto: T10 | `fluidi/power_supply/protezione-della-linea` |
| E.4 | Magnetotermico-differenziale 1P+N C16, Idn 30 mA, tipo A o F, 6 kA, linea dedicata: Alimentazione unita' esterna | 1 | n | una per tratto: T11 | `fluidi/power_supply/protezione-della-linea` |
| E.5 | Scatola di derivazione IP55 | 2 | n | 2 tratti × 1 = 2 | `fluidi/power_supply/scatola-di-derivazione` |
| E.6 | Tubo corrugato Ø25 per le linee di alimentazione | 40 | m | T10 15 + T11 20 = 35 m × 1, per eccesso a 10 m = 40 m | `fluidi/power_supply/corrugato-di-potenza` |
| E.7 | Cavo di collegamento 4G1,5 a doppio isolamento, Collegamento UI-UE | 13 | m | T12 13 m | `fluidi/interconnection/cavo-di-collegamento` |
| E.8 | Cavo bus Airzone, schermato, Bus Airzone ai termostati | 29 | m | T13 9 + T14 7 + T15 7,5 + T16 5,5 = 29 m | `fluidi/control_bus/cavo-di-bus` |
| E.9 | Cavo 2×0,75 (P1-P2), Linea P1-P2 dell'unita' interna | 10,5 | m | T17 5,5 + T18 5 = 10,5 m | `fluidi/control_bus/cavo-di-bus` |
| E.10 | Tubo corrugato Ø20 per bus e linee di comando | 40 | m | T13 9 + T14 7 + T15 7,5 + T16 5,5 + T17 5,5 + T18 5 = 39,5 m × 1, per eccesso a 10 m = 40 m | `fluidi/control_bus/corrugato-di-bus` |
| E.11 | Scatola 503 per termostati e comandi a parete | 5 | n | 5 pezzi × 1 = 5 (CF-01, TZ-01, TZ-02, TZ-03, TZ-04) | `corredo/wired-remote/scatola-503 + corredo/room-thermostat/scatola-503` |
| E.12 | Aggiornamento dello schema del quadro elettrico | 1 | a corpo | QE-01: 1 | `corredo/electrical-panel/aggiornamento-schema-quadro` |
| E.13 | Sezionatore onnipolare di prossimità IP55, apertura contatti ≥ 3 mm | 1 | n | SZ-01: 1 | `corredo/isolator-switch/sezionatore` |
| F.1 | Foratura di tramezza Ø250 (o vano 450×250) per flessibili e plenum di bocchetta | 7 | n | T01 2 + T02 1 + T03 2 + T04 1 + T05 1 = 7 | `fluidi/supply_air/foratura-per-flessibile` |
| F.2 | Foratura di parete interna Ø80 per linee frigorifere e cavi | 2 | n | T08 2 | `fluidi/refrigerant_gas/foratura-linee-frigo` |
| F.3 | Foratura per lo scarico della condensa | 1 | n | T09 1 | `fluidi/condensate/foratura-condensa` |
| F.4 | Traccia per termostati e comandi a parete | 5 | n | 5 pezzi × 1 = 5 (CF-01, TZ-01, TZ-02, TZ-03, TZ-04) | `corredo/wired-remote/traccia-per-apparecchio-a-parete + corredo/room-thermostat/traccia-per-apparecchio-a-parete` |
| F.5 | Tracce per le linee dal quadro al controsoffitto | 5 | m | QE-01: 5 | `corredo/electrical-panel/tracce-dal-quadro` |
| F.6 | Traccia per la condensa fino allo scarico | 3 | m | AL-01: 3 | `corredo/condensate-outlet/traccia-condensa` |
| F.7 | Carotaggio parete esterna Ø80 con guaina passante e sigillatura | 1 | n | UE-01: 1 | `corredo/split-outdoor-unit/carotaggio-parete-esterna` |
| Z.1 | Velette o controsoffitti per le bocchette, altezza utile ≥ 30 cm | 1 | a corpo | 1 per fluido | `fluidi/supply_air/velette-per-le-bocchette` |
| Z.2 | Bocchetta di mandata 400×200 a doppio filare con serranda | 5 | n | 5 pezzi × 1 = 5 (B1, B2, B3, B4, B5) | `corredo/air-supply-terminal/bocchetta-di-mandata` |
| Z.3 | Griglia di transito o luce sotto porta per il ritorno dell'aria dal locale servito | 4 | n | 4: 4 locali serviti (Camera 13 m², Camera 15 m², Camera 16 m², Soggiorno-cucina); il locale e' letto dall'etichetta della bocchetta | `corredo/air-supply-terminal/griglia-di-transito` |
| Z.4 | Botola di ispezione ≥ 600×600 sotto la macchina (filtro, pompa, scheda) | 2 | n | 2 pezzi × 1 = 2 (PLZ-01, UI-01) | `corredo/zoning-plenum-5/botola-di-ispezione + corredo/ducted-indoor-unit/botola-di-ispezione` |
| Z.5 | Griglia di ripresa 1000×250 senza filtro, apribile per accedere al filtro | 1 | n | RA-01: 1 | `corredo/return-air-terminal/griglia-di-ripresa` |
| Z.6 | Controsoffitto in zona unità interna e plenum: altezza libera ≥ 35 cm sotto il solaio | 1 | a corpo | UI-01: 1 | `corredo/ducted-indoor-unit/controsoffitto-zona-macchina` |
| Z.7 | Chiusura e ripristino di fori, tracce e passaggi | 1 | a corpo | sempre | `attivita/chiusure-e-ripristini` |
| G.1 | Posa dell'unità interna in controsoffitto su sospensioni antivibranti, con plenum di zona e plenum di ripresa. | 1 | a corpo | nell'impianto: Unità interna canalizzata ad espansione diretta | `attivita/posa-unita-interna` |
| G.2 | Posa dell'unità esterna su staffe con antivibranti; canalina esterna e scarico condensa dell'unità esterna. | 1 | a corpo | nell'impianto: Unità esterna split a pompa di calore | `attivita/posa-unita-esterna` |
| G.3 | Linee frigorifere: posa e cartelle; prova di tenuta in azoto prima della chiusura del controsoffitto, circuito lasciato in pressione con manometro fino al secondo accesso, con verbale; vuoto, apertura rubinetti, eventuale carica, registrazione F-Gas. | 1 | a corpo | nell'impianto: fluido frigorigeno in fase liquida, fluido frigorigeno in fase gassosa | `attivita/linee-frigorifere-e-prove` |
| G.4 | Distribuzione aria: 5 rami flessibili con plenum porta-bocchetta, sostegni e sigillature; bocche protette fino alla posa delle bocchette. | 1 | a corpo | nell'impianto: aria di mandata | `attivita/distribuzione-aria` |
| G.5 | Scarico condensa con sifone e allaccio allo scarico; prova di scarico e della pompa prima della chiusura del controsoffitto. | 1 | a corpo | nell'impianto: condensa | `attivita/scarico-condensa-e-prova` |
| G.6 | Linee elettriche dedicate dal quadro, collegamento fra le unità, linee di comando e bus; posa di termostati e comandi a parete. | 1 | a corpo | nell'impianto: alimentazione elettrica, collegamento elettrico fra le unita', bus di comando | `attivita/linee-elettriche-e-comandi` |
| G.7 | Messa in servizio con Nove C, al secondo accesso: regolazione della prevalenza dell'unità interna e misura delle portate per zona, configurazione della zonizzazione e dei comandi, app; collaudo con verbale. | 1 | a corpo | nell'impianto: Unità interna canalizzata ad espansione diretta, Unità esterna split a pompa di calore | `attivita/messa-in-servizio` |
| G.8 | Dichiarazione di conformità D.M. 37/2008, art. 1 lettera a) (impianti elettrici), con lo schema del quadro aggiornato e gli allegati. | 1 | a corpo | nell'impianto: alimentazione elettrica | `attivita/dico-elettrico` |
| G.9 | Dichiarazione di conformità D.M. 37/2008, art. 1 lettera c) (impianti di climatizzazione), con allegati; documenti per libretto di impianto, catasto regionale e F-Gas. | 1 | a corpo | nell'impianto: fluido frigorigeno in fase liquida, fluido frigorigeno in fase gassosa, aria di mandata | `attivita/dico-climatizzazione` |
| G.10 | Cantiere: POS e oneri della sicurezza (presenza dell'impresa del Committente), trabattello e mezzi di sollevamento. | 1 | a corpo | sempre | `attivita/cantiere` |
| G.11 | Trasporto, ricevimento e custodia delle apparecchiature fornite da Nove C fino al collaudo; protezioni delle macchine e delle bocche durante le opere edili. | 1 | a corpo | nell'impianto: Unità esterna split a pompa di calore, Unità interna canalizzata ad espansione diretta, Plenum motorizzato di zona a cinque serrande | `attivita/custodia-e-protezioni` |
| G.12 | Pulizia finale e smaltimento di imballi e residui di lavorazione. | 1 | a corpo | sempre | `attivita/pulizia-e-smaltimenti` |
| V.1 | Linea frigorifera completa oltre la quantità di computo (coppia pre-isolata, cavo di collegamento, canalina, refrigerante) |  | m | nell'impianto: fluido frigorigeno in fase liquida, fluido frigorigeno in fase gassosa; solo prezzo unitario | `attivita/variante-linea-frigorifera` |
| V.2 | Flessibile posato oltre la quantità di computo, con fascette e sostegni |  | m | nell'impianto: aria di mandata; solo prezzo unitario | `attivita/variante-flessibile` |
| V.3 | Cavo di alimentazione in corrugato oltre la quantità di computo, stessa sezione |  | m | nell'impianto: alimentazione elettrica; solo prezzo unitario | `attivita/variante-cavo` |
| V.4 | Accesso aggiuntivo in cantiere (oltre i due previsti) |  | n | sempre; solo prezzo unitario | `attivita/variante-accesso` |
| V.5 | Centralino aggiuntivo 8 moduli, se il quadro non ha i moduli liberi per le protezioni nuove |  | n | nell'impianto: Quadro elettrico; solo prezzo unitario | `attivita/variante-centralino` |

## Avvisi

- T09 (Scarico condensa: UI-01 - SIF-01 - AL-01): la tubazione SIF-01 - AL-01 senza lunghezza; si considera compresa nei 7,6 m dati sul tratto.
- T11 (Alimentazione unita' esterna: QE-01 - SZ-01 - UE-01): la tubazione SZ-01 - UE-01 senza lunghezza; si considera compresa nei 15 m dati sul tratto.
- T02, T04, T05 (aria di mandata): attraversamenti di parete non dati, assunti 1 per tratto (regola Nove C: una parete per ramo, se il progettista non dice quante).
- T09 (condensa): attraversamenti di parete non dati, assunti 1 per tratto (regola Nove C: una parete, se il progettista non dice quante).
- T18, scritta sulla tavola: «P1-P2 · L 3 m», contro L 5 m da quotare.

## Note

1. «L da quotare» = (L stimata + 1 m) × 1,15, per eccesso a 0,5 m; minimi: fluido frigorigeno in fase liquida, fluido frigorigeno in fase gassosa 12 m; condensa 10 m; bus di comando 5 m; aria di mandata, aria di ripresa 2 m. La L stimata è un dato del progettista, scritta su ogni tratto.
2. Quantità indicative per un prezzo a corpo, fisso e invariabile: l'installatore le verifica nel sopralluogo obbligatorio prima dell'offerta; le varianti hanno solo il prezzo unitario.
3. Velocità nei tratti di aria di mandata da 1,9 a 2,5 m/s, sulla sezione lorda, dalle portate e dalle sezioni del progettista (verifica: segnala, non corregge).
4. Velocità nei tratti di aria di ripresa 1,2 m/s, sulla sezione lorda, dalle portate e dalle sezioni del progettista (verifica: segnala, non corregge).
5. Fornitura da confermare: apparecchiature fornite da Nove C; bocchette e griglie, opere edili del Committente; messa in servizio con Nove C.
6. La distinta non progetta: lunghezze, sezioni, portate, protezioni, marca e modello sono dati del progettista; la distinta li maggiora e ne conta il corredo con regole scritte, ciascuna con la sua fonte (regole f8b849f909489495).
