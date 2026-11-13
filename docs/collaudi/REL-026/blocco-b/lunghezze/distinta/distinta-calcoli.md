# Distinta materiali — foglio dei calcoli (DA DEFINIRE, tavola DA DEFINIRE rev. 00)

Committente: DA DEFINIRE · Progetto: Canalizzato aria-aria in pompa di calore - appartamento al secondo piano · Data: 29.10.2026

> proposta (D-213, REL-013): il PO non ha ancora deciso se la skill fa la distinta; finché non decide, la distinta si fa solo col comando esplicito `mep.py distinta`. Regole `4ed0b8034a230fed` (distinta 1.3.0, lunghezze 1.1.0, fluidi 1.3.0, corredo 1.7.0, attivita 1.2.0, verifica 1.1.0).

## DA DEFINIRE — le domande al progettista

- TA-01 (Bocchetta di mandata con plenum di raccordo): manca il dato «dimensione» per «Plenum porta-bocchetta coibentato per bocchetta DA DEFINIRE (dimensione), attacco Ø200 laterale».
- TA-02 (Bocchetta di mandata con plenum di raccordo): manca il dato «dimensione» per «Plenum porta-bocchetta coibentato per bocchetta DA DEFINIRE (dimensione), attacco Ø200 laterale».
- TA-04 (Bocchetta di mandata con plenum di raccordo): manca il dato «dimensione» per «Plenum porta-bocchetta coibentato per bocchetta DA DEFINIRE (dimensione), attacco Ø200 laterale».
- TA-03 (Bocchetta di mandata con plenum di raccordo): manca il dato «dimensione» per «Plenum porta-bocchetta coibentato per bocchetta DA DEFINIRE (dimensione), attacco Ø200 laterale».
- T07: su UE-01 servono `precarica_fino_a_m` e `carica_aggiuntiva_g_m` (dati di macchina del progettista) per la riserva di refrigerante.
- UI-01 (Unità interna canalizzata ad espansione diretta): manca il dato «attacco_condensa» per «Raccordo di adattamento dall'attacco condensa dell'unità interna (DA DEFINIRE (attacco_condensa)) al tubo di scarico, con fascetta».
- T09 (Alimentazione della centrale di zona): manca `protezione` sul tratto.
- T10 (Alimentazione dell'unità esterna): manca `protezione` sul tratto.
- T12, T13, T14 (bus di comando): che sezione hanno? Serve `sezione` sul tratto (es. «Ø200», «3G2,5»).
- TA-01 (Bocchetta di mandata con plenum di raccordo): manca il dato «dimensione» per «Bocchetta di mandata DA DEFINIRE (dimensione) a doppio filare con serranda».
- TA-02 (Bocchetta di mandata con plenum di raccordo): manca il dato «dimensione» per «Bocchetta di mandata DA DEFINIRE (dimensione) a doppio filare con serranda».
- TA-04 (Bocchetta di mandata con plenum di raccordo): manca il dato «dimensione» per «Bocchetta di mandata DA DEFINIRE (dimensione) a doppio filare con serranda».
- TA-03 (Bocchetta di mandata con plenum di raccordo): manca il dato «dimensione» per «Bocchetta di mandata DA DEFINIRE (dimensione) a doppio filare con serranda».

## Da confermare per questa offerta

- Fornitura: apparecchiature fornite da Nove C; bocchette e griglie del Committente; opere edili del Committente; messa in servizio con Nove C — come da regole predefinite di Nove C; confermare per questa offerta.

## Le tratte

| tratto | rete | da - a | sezione | L stimata | L da quotare | conto |
|---|---|---|---|---|---|---|
| T01 | Mandata dell'aria | PLZ-01 - TA-01 | Ø200 | 3,8 | 6 | (3,8 + 1) × 1,15 = 5,52 → 6 m |
| T02 | Mandata dell'aria | PLZ-01 - TA-02 | Ø200 | 3,4 | 5,5 | (3,4 + 1) × 1,15 = 5,06 → 5,5 m |
| T03 | Mandata dell'aria | PLZ-01 - TA-03 | Ø200 | 1,55 | 3 | (1,55 + 1) × 1,15 = 2,93 → 3 m |
| T04 | Mandata dell'aria | PLZ-01 - TA-04 | Ø200 | 4,55 | 6,5 | (4,55 + 1) × 1,15 = 6,38 → 6,5 m |
| T05 | Ripresa dell'aria | RA-01 - UI-01 | 800×300 |  |  | raccordo diretto |
| T06 | Linea frigorifera del liquido | UE-01 - UI-01 | 1/4" | 9 | 12 | (9 + 1) × 1,15 = 11,5 → 11,5 m; minimo frigo 12 m → 12 m |
| T07 | Linea frigorifera del gas | UE-01 - UI-01 | 5/8" | 9 | 12 | (9 + 1) × 1,15 = 11,5 → 11,5 m; minimo frigo 12 m → 12 m |
| T08 | Scarico della condensa | UI-01 - SIF-01 - AL-01 | PVC Ø32 | 8 | 10,5 | (8 + 1) × 1,15 = 10,35 → 10,5 m |
| T09 | Alimentazione della centrale di zona | QE-01 - CZ-01 | 3G1,5 | 8 | 10,5 | (8 + 1) × 1,15 = 10,35 → 10,5 m |
| T10 | Alimentazione dell'unità esterna | QE-01 - SZ-01 - UE-01 | 3G4 | 10,63 | 13,5 | (10,63 + 1) × 1,15 = 13,37 → 13,5 m |
| T11 | Collegamento fra unità interna ed esterna | UE-01 - UI-01 | 4G1,5 | 10 | 13 | (10 + 1) × 1,15 = 12,65 → 13 m |
| T12 | Bus dei termostati di zona | CZ-01 - TZ-01 | — | 3,46 | 5,5 | (3,46 + 1) × 1,15 = 5,13 → 5,5 m |
| T13 | Bus dei termostati di zona | CZ-01 - TZ-02 | — | 5,11 | 7,5 | (5,11 + 1) × 1,15 = 7,02 → 7,5 m |
| T14 | Bus dei termostati di zona | CZ-01 - TZ-03 | — | 2,37 | 5 | (2,37 + 1) × 1,15 = 3,87 → 4 m; minimo bus 5 m → 5 m |
| T15 | Interfaccia centrale di zona - unità interna | CZ-01 - UI-01 | 2×0,75 | 2 | 5 | (2 + 1) × 1,15 = 3,45 → 3,5 m; minimo bus 5 m → 5 m |
| T16 | Linea del comando a filo | UI-01 - CF-01 | 2×0,75 | 3,79 | 6 | (3,79 + 1) × 1,15 = 5,51 → 6 m |

## La verifica (segnala, non corregge)

| dove | controllo | valore | soglia | esito |
|---|---|---|---|---|
| T01 | velocità | 300 m³/h su Ø200: 2,65 m/s | ≤ 3 m/s | entro |
| T02 | velocità | 220 m³/h su Ø200: 1,95 m/s | ≤ 3 m/s | entro |
| T03 | velocità | 300 m³/h su Ø200: 2,65 m/s | ≤ 3 m/s | entro |
| T04 | velocità | 300 m³/h su Ø200: 2,65 m/s | ≤ 3 m/s | entro |
| T05 | velocità | manca la portata (`portata_m3h`) | ≤ 2 m/s | non verificabile |
| Camera matrimoniale | griglia di transito | 300 m³/h a 1,5 m/s | Aeff ≥ 0,056 m² | da rispettare |
| Camera singola | griglia di transito | 220 m³/h a 1,5 m/s | Aeff ≥ 0,041 m² | da rispettare |
| Soggiorno | varco verso la ripresa | 600 m³/h a 1,5 m/s | Aeff ≥ 0,112 m² | da rispettare |

## Le voci, con la regola e il conto

| rif | voce | q.tà | um | conto | regola |
|---|---|---|---|---|---|
| A.1 | Comando a filo dell'unità: Mitsubishi Electric PAR-41MAA | 1 | n | 1 nello schema (CF-01) | `corredo/wired-remote/apparecchiatura` |
| A.2 | Plenum motorizzato di zona a quattro serrande: Airzone | 1 | n | 1 nello schema (PLZ-01) | `corredo/zoning-plenum-4/apparecchiatura` |
| A.3 | Termostato di zona: Airzone Think a filo | 3 | n | 3 nello schema (TZ-01, TZ-02, TZ-03) | `corredo/room-thermostat/apparecchiatura` |
| A.4 | Unità esterna split a pompa di calore: Mitsubishi Electric SUZ-M71VA | 1 | n | 1 nello schema (UE-01) | `corredo/split-outdoor-unit/apparecchiatura` |
| A.5 | Unità interna canalizzata ad espansione diretta: Mitsubishi Electric PEAD-M71JA | 1 | n | 1 nello schema (UI-01) | `corredo/ducted-indoor-unit/apparecchiatura` |
| S.1 | Sospensione del plenum motorizzato (flangiato sulla mandata dell'unità interna): 4 barre filettate M10 con ancoranti, dadi e antivibranti | 1 | kit | PLZ-01: 1 | `corredo/zoning-plenum-4/sospensione-plenum-di-zona` |
| S.2 | Sospensione del plenum di ripresa: 2 barre filettate M8 con ancoranti e dadi | 1 | kit | RA-01: 1 | `corredo/return-air-terminal/sospensione-plenum-di-ripresa` |
| S.3 | Staffe a parete per unità esterna, portata almeno doppia del peso della macchina, con tasselli chimici e antivibranti; scostamento dalla parete min. 150 mm | 1 | kit | UE-01: 1 | `corredo/split-outdoor-unit/staffe-unita-esterna` |
| S.4 | Sospensione dell'unità interna: 4 barre filettate M10, ancoranti per carichi sospesi su laterocemento, dadi, rondelle e antivibranti | 1 | kit | UI-01: 1 | `corredo/ducted-indoor-unit/sospensione-unita-interna` |
| B.1 | Condotto flessibile coibentato Ø200 (isolamento 25 mm, barriera vapore), confezione da 10 m | 3 | conf. | 4 pezzi interi, 21 m: in confezioni da 10 m (utili 9,5) ne servono 3 [6,5 + 3] [6] [5,5]; riserva 25%: 21 × 1,25 = 26,25 m → 3; si prende il maggiore: 3 | `fluidi/supply_air/flessibile-in-confezioni` |
| B.2 | Manicotto di giunzione Ø200 | 2 | n | 2 per sezione | `fluidi/supply_air/manicotto-di-riserva` |
| B.3 | Fascetta di serraggio Ø200 (anima e mantello) | 16 | n | 4 tratti × 4 = 16 | `fluidi/supply_air/fascette` |
| B.4 | Nastro alluminio rinforzato 50 mm | 2 | rotolo | 21 m / 20 m per eccesso, almeno 1 = 2 | `fluidi/supply_air/nastro-alluminio` |
| B.5 | Sostegno per flessibile (fascia o collare con pendino), passo ≤ 1,2 m | 23 | n | T01 6 + T02 6 + T03 4 + T04 7 = 23 (L / 1,2 m per eccesso +1 per tratto) | `fluidi/supply_air/sostegni` |
| B.6 | Plenum porta-bocchetta coibentato per bocchetta DA DEFINIRE (dimensione), attacco Ø200 laterale | 4 | n | 4 pezzi × 1 = 4 (TA-01, TA-02, TA-04, TA-03) | `corredo/air-supply-terminal/plenum-porta-bocchetta` |
| B.7 | Isolamento elastomerico adesivo 13 mm per manicotti, raccordi, derivazione e plenum | 2 | rotolo | PLZ-01: 2 | `corredo/zoning-plenum-4/isolamento-raccordi-plenum` |
| B.8 | Plenum di ripresa in lamiera zincata, non coibentato, con filtro ispezionabile, bocca 800×300, sulla bocca di aspirazione dell'unità interna; filtro unico: l'eventuale filtro di serie dell'unità interna si toglie | 1 | n | RA-01: 1 | `corredo/return-air-terminal/plenum-di-ripresa` |
| B.9 | Giunto antivibrante in tela fra unità interna e plenum di ripresa | 1 | n | UI-01: 1 | `corredo/ducted-indoor-unit/giunto-antivibrante-ripresa` |
| C.1 | Tubo rame ricotto pre-isolato 1/4", isolamento ≥ 10 mm, resistente a 120 °C | 12 | m | T06 12 m | `fluidi/refrigerant_liquid/tubo-rame-liquido` |
| C.2 | Manicotto a brasare 1/4" (riserva, posa in tratta unica) | 2 | n | 2 per sezione | `fluidi/refrigerant_liquid/manicotti-a-brasare-liquido` |
| C.3 | Tubo rame ricotto pre-isolato 5/8", isolamento ≥ 13 mm, resistente a 120 °C | 12 | m | T07 12 m | `fluidi/refrigerant_gas/tubo-rame-gas` |
| C.4 | Manicotto a brasare 5/8" (riserva, posa in tratta unica) | 2 | n | 2 per sezione | `fluidi/refrigerant_gas/manicotti-a-brasare-gas` |
| C.5 | Nastro di finitura e manicotti isolanti per le giunzioni a cartella | 1 | kit | 1 tratto × 1 = 1 | `fluidi/refrigerant_gas/nastro-e-manicotti-isolanti` |
| C.6 | Collare di sostegno linee frigorifere in controsoffitto | 10 | n | T07 10 (L / 1,2 m per eccesso per tratto) | `fluidi/refrigerant_gas/collari-linee-frigo` |
| C.7 | Refrigerante R32, riserva per carica aggiuntiva | DA DEFINIRE | kg | mancano i dati di macchina | `fluidi/refrigerant_gas/carica-aggiuntiva` |
| C.8 | Canalina coprilinee esterna 110×75 (linee frigo isolate, cavo di collegamento, alimentazione dell'unità esterna) | 4 | m | UE-01: 4 | `corredo/split-outdoor-unit/canalina-esterna` |
| C.9 | Accessori canalina: curva 2, terminale a muro 1, giunto 2 | 1 | kit | UE-01: 1 | `corredo/split-outdoor-unit/accessori-canalina` |
| D.1 | Tubo PVC rigido PVC Ø32 | 10,5 | m | T08 10,5 m | `fluidi/condensate/tubo-pvc` |
| D.2 | Curva 87°-90° PVC Ø32 | 7 | n | T08 7 (L / 2 m per eccesso +1 per tratto) | `fluidi/condensate/curve-condensa` |
| D.3 | Manicotto PVC Ø32 | 3 | n | T08 3 (L / 3 m per eccesso -1 per tratto) | `fluidi/condensate/manicotti-condensa` |
| D.4 | Collare per tubo condensa | 11 | n | T08 11 (L / 1 m per eccesso per tratto) | `fluidi/condensate/collari-condensa` |
| D.5 | Isolamento anticondensa 9 mm per il tubo della condensa | 10,5 | m | T08 10,5 m | `fluidi/condensate/isolamento-anticondensa` |
| D.6 | Collante e pulitore PVC | 1 | n | 1 per fluido | `fluidi/condensate/collante-pvc` |
| D.7 | Innesto sullo scarico esistente con braga 45° Ø40, a valle del sifone dell'apparecchio | 1 | n | AL-01: 1 | `corredo/condensate-outlet/innesto-sullo-scarico` |
| D.8 | Sifone ispezionabile per condensa | 1 | n | SIF-01: 1 | `corredo/condensate-trap/sifone` |
| D.9 | Scarico dell'unità esterna (sbrinamento): raccordo sul foro di scarico, tappi sui fori non usati, tubo in pendenza fino a pluviale o pozzetto | 4 | m | UE-01: 4 | `corredo/split-outdoor-unit/scarico-condensa-unita-esterna` |
| D.10 | Raccordo di adattamento dall'attacco condensa dell'unità interna (DA DEFINIRE (attacco_condensa)) al tubo di scarico, con fascetta | 1 | n | UI-01: 1 | `corredo/ducted-indoor-unit/raccordo-condensa-unita-interna` |
| E.1 | Cavo FG16OR16 3G1,5, Alimentazione della centrale di zona | 10,5 | m | T09 10,5 m | `fluidi/power_supply/cavo-di-alimentazione` |
| E.2 | Cavo FG16OR16 3G4, Alimentazione dell'unità esterna | 13,5 | m | T10 13,5 m | `fluidi/power_supply/cavo-di-alimentazione` |
| E.3 | DA DEFINIRE (protezione), linea dedicata: Alimentazione della centrale di zona | 1 | n | una per tratto: T09 | `fluidi/power_supply/protezione-della-linea` |
| E.4 | DA DEFINIRE (protezione), linea dedicata: Alimentazione dell'unità esterna | 1 | n | una per tratto: T10 | `fluidi/power_supply/protezione-della-linea` |
| E.5 | Scatola di derivazione IP55 | 2 | n | 2 tratti × 1 = 2 | `fluidi/power_supply/scatola-di-derivazione` |
| E.6 | Tubo corrugato Ø25 per le linee di alimentazione | 30 | m | T09 10,5 + T10 13,5 = 24 m × 1, per eccesso a 10 m = 30 m | `fluidi/power_supply/corrugato-di-potenza` |
| E.7 | Cavo di collegamento 4G1,5 a doppio isolamento, Collegamento fra unità interna ed esterna | 13 | m | T11 13 m | `fluidi/interconnection/cavo-di-collegamento` |
| E.8 | Cavo DA DEFINIRE (sezione), Bus dei termostati di zona | 18 | m | T12 5,5 + T13 7,5 + T14 5 = 18 m | `fluidi/control_bus/cavo-di-bus` |
| E.9 | Cavo 2×0,75, Interfaccia centrale di zona - unità interna, Linea del comando a filo | 11 | m | T15 5 + T16 6 = 11 m | `fluidi/control_bus/cavo-di-bus` |
| E.10 | Tubo corrugato Ø20 per bus e linee di comando | 30 | m | T12 5,5 + T13 7,5 + T14 5 + T15 5 + T16 6 = 29 m × 1, per eccesso a 10 m = 30 m | `fluidi/control_bus/corrugato-di-bus` |
| E.11 | Scatola 503 per termostati e comandi a parete | 4 | n | 4 pezzi × 1 = 4 (CF-01, TZ-01, TZ-02, TZ-03) | `corredo/wired-remote/scatola-503 + corredo/room-thermostat/scatola-503` |
| E.12 | Aggiornamento dello schema del quadro elettrico | 1 | a corpo | QE-01: 1 | `corredo/electrical-panel/aggiornamento-schema-quadro` |
| E.13 | Sezionatore onnipolare di prossimità IP55, 25 A, apertura contatti ≥ 3 mm | 1 | n | SZ-01: 1 | `corredo/isolator-switch/sezionatore` |
| F.1 | Foratura di tramezza Ø300 (o vano 470×270) per flessibili coibentati e plenum di bocchetta | 4 | n | T01 1 + T02 1 + T03 1 + T04 1 = 4 | `fluidi/supply_air/foratura-per-flessibile` |
| F.2 | Foratura di parete interna Ø125 per linee frigorifere e cavi | 1 | n | T07 1 | `fluidi/refrigerant_gas/foratura-linee-frigo` |
| F.3 | Foratura per lo scarico della condensa (tramezze e parete del bagno) | 1 | n | T08 1 | `fluidi/condensate/foratura-condensa` |
| F.4 | Traccia per termostati e comandi a parete, dal controsoffitto alla scatola | 5,6 | m | 4 pezzi × 1,4 = 5,6 (CF-01, TZ-01, TZ-02, TZ-03) | `corredo/wired-remote/traccia-per-apparecchio-a-parete + corredo/room-thermostat/traccia-per-apparecchio-a-parete` |
| F.5 | Tracce per le linee dal quadro al controsoffitto | 5 | m | QE-01: 5 | `corredo/electrical-panel/tracce-dal-quadro` |
| F.6 | Traccia per la condensa fino allo scarico | 3 | m | AL-01: 3 | `corredo/condensate-outlet/traccia-condensa` |
| F.7 | Carotaggio parete esterna Ø125 con guaina passante e sigillatura (linee frigo, cavo di collegamento, alimentazione dell'unità esterna) | 1 | n | UE-01: 1 | `corredo/split-outdoor-unit/carotaggio-parete-esterna` |
| Z.1 | Velette o controsoffitti per le bocchette, altezza utile ≥ 30 cm | 1 | a corpo | 1 per fluido | `fluidi/supply_air/velette-per-le-bocchette` |
| Z.2 | Bocchetta di mandata DA DEFINIRE (dimensione) a doppio filare con serranda | 4 | n | 4 pezzi × 1 = 4 (TA-01, TA-02, TA-04, TA-03) | `corredo/air-supply-terminal/bocchetta-di-mandata` |
| Z.3 | Griglia di transito o luce sotto porta per il ritorno dell'aria dal locale servito | 2 | n | 2: 2 locali serviti (Camera matrimoniale, Camera singola); nessuna dove il locale ha un varco: Soggiorno | `corredo/air-supply-terminal/griglia-di-transito` |
| Z.4 | Botola di ispezione ≥ 600×600 sotto la macchina (filtro, pompa, scheda) | 2 | n | 2 pezzi × 1 = 2 (PLZ-01, UI-01) | `corredo/zoning-plenum-4/botola-di-ispezione + corredo/ducted-indoor-unit/botola-di-ispezione` |
| Z.5 | Copertura Wi-Fi in zona plenum e centrale di zona, per la configurazione e l'app | 1 | a corpo | PLZ-01: 1 | `corredo/zoning-plenum-4/copertura-wifi` |
| Z.6 | Griglia di ripresa 800×300 senza filtro, apribile per accedere al filtro | 1 | n | RA-01: 1 | `corredo/return-air-terminal/griglia-di-ripresa` |
| Z.7 | Potenza contrattuale adeguata all'unità esterna (corrente MCA di targa) e alle altre utenze, prima della messa in servizio | 1 | a corpo | UE-01: 1 | `corredo/split-outdoor-unit/potenza-contrattuale` |
| Z.8 | Controsoffitto in zona unità interna e plenum: altezza libera ≥ 35 cm sotto il solaio | 1 | a corpo | UI-01: 1 | `corredo/ducted-indoor-unit/controsoffitto-zona-macchina` |
| Z.9 | Chiusura e ripristino di fori, tracce e passaggi | 1 | a corpo | sempre | `attivita/chiusure-e-ripristini` |
| G.1 | Posa dell'unità interna in controsoffitto su sospensioni antivibranti, con il plenum di zona flangiato sulla mandata e il plenum di ripresa. | 1 | a corpo | nell'impianto: Unità interna canalizzata ad espansione diretta | `attivita/posa-unita-interna` |
| G.2 | Posa dell'unità esterna su staffe antivibranti, con gli spazi minimi del manuale; canalina esterna e scarico dell'unità esterna. | 1 | a corpo | nell'impianto: Unità esterna split a pompa di calore | `attivita/posa-unita-esterna` |
| G.3 | Linee frigorifere: posa e cartelle; prova in azoto alla pressione del manuale del costruttore per 24 h, con verbale, prima della chiusura del controsoffitto, poi circuito a pressione ridotta con manometro fino al secondo accesso; vuoto max. 500 micron con prova di tenuta del vuoto, apertura rubinetti, registrazione F-Gas. Carica aggiuntiva solo oltre la lunghezza precaricata dall'unità esterna. | 1 | a corpo | nell'impianto: fluido frigorigeno in fase liquida, fluido frigorigeno in fase gassosa | `attivita/linee-frigorifere-e-prove` |
| G.4 | Distribuzione aria: 4 rami flessibili interi dal plenum alle bocchette, senza curve rigide: curve del flessibile ampie (raggio in asse non inferiore a un diametro), senza schiacciamenti né anse; UI e plenum arretrati verso il portico quanto serve a curvare ampi all'uscita delle serrande; plenum porta-bocchetta, sostegni e sigillature; bocche protette fino alla posa delle bocchette. | 1 | a corpo | nell'impianto: aria di mandata | `attivita/distribuzione-aria` |
| G.5 | Scarico condensa con sifone e allaccio allo scarico; prova di scarico e della pompa prima della chiusura del controsoffitto. | 1 | a corpo | nell'impianto: condensa | `attivita/scarico-condensa-e-prova` |
| G.6 | Linee elettriche dedicate dal quadro, collegamento fra le unità, linee di comando e bus; posa di termostati e comandi a parete. | 1 | a corpo | nell'impianto: alimentazione elettrica, collegamento elettrico fra le unita', bus di comando | `attivita/linee-elettriche-e-comandi` |
| G.7 | Messa in servizio con Nove C, al secondo accesso: taratura automatica della prevalenza dell'unità interna con tutte le serrande aperte e il filtro pulito e misura delle portate per zona, configurazione della zonizzazione e dei comandi, app; collaudo con verbale. | 1 | a corpo | nell'impianto: Unità interna canalizzata ad espansione diretta, Unità esterna split a pompa di calore | `attivita/messa-in-servizio` |
| G.8 | Dichiarazione di conformità D.M. 37/2008, art. 1 lettera a) (impianti elettrici), con lo schema del quadro aggiornato e gli allegati. | 1 | a corpo | nell'impianto: alimentazione elettrica | `attivita/dico-elettrico` |
| G.9 | Dichiarazione di conformità D.M. 37/2008, art. 1 lettera c) (impianti di climatizzazione), con allegati; documenti per libretto di impianto, catasto regionale e F-Gas. | 1 | a corpo | nell'impianto: fluido frigorigeno in fase liquida, fluido frigorigeno in fase gassosa, aria di mandata | `attivita/dico-climatizzazione` |
| G.10 | Cantiere: POS e oneri della sicurezza (presenza dell'impresa del Committente), trabattello e mezzi di sollevamento. | 1 | a corpo | sempre | `attivita/cantiere` |
| G.11 | Trasporto, ricevimento e custodia delle apparecchiature fornite da Nove C fino al collaudo; protezioni delle macchine e delle bocche durante le opere edili. | 1 | a corpo | nell'impianto: Unità esterna split a pompa di calore, Unità interna canalizzata ad espansione diretta, Plenum motorizzato di zona a quattro serrande | `attivita/custodia-e-protezioni` |
| G.12 | Pulizia finale e smaltimento di imballi e residui di lavorazione. | 1 | a corpo | sempre | `attivita/pulizia-e-smaltimenti` |
| V.1 | Linea frigorifera completa oltre la quantità di computo (coppia pre-isolata, cavo di collegamento, canalina, refrigerante) |  | m | nell'impianto: fluido frigorigeno in fase liquida, fluido frigorigeno in fase gassosa; solo prezzo unitario | `attivita/variante-linea-frigorifera` |
| V.2 | Flessibile posato oltre la quantità di computo, con fascette e sostegni |  | m | nell'impianto: aria di mandata; solo prezzo unitario | `attivita/variante-flessibile` |
| V.3 | Cavo di alimentazione in corrugato oltre la quantità di computo, stessa sezione |  | m | nell'impianto: alimentazione elettrica; solo prezzo unitario | `attivita/variante-cavo` |
| V.4 | Accesso aggiuntivo in cantiere (oltre i due previsti) |  | n | sempre; solo prezzo unitario | `attivita/variante-accesso` |
| V.5 | Centralino aggiuntivo 8 moduli, se il quadro non ha i moduli liberi per le protezioni nuove |  | n | nell'impianto: Quadro elettrico; solo prezzo unitario | `attivita/variante-centralino` |
| V.6 | Basamento a terra con piedini antivibranti al posto delle staffe dell'unità esterna, se la posizione lo richiede |  | n | nell'impianto: Unità esterna split a pompa di calore; solo prezzo unitario | `attivita/variante-basamento` |
| V.7 | Cavo scaldante autoregolante sul tratto esterno dello scarico dell'unità esterna, con collegamento elettrico |  | m | sempre; solo prezzo unitario | `attivita/variante-cavo-scaldante` |

## Avvisi

- T08 (Scarico della condensa: UI-01 - SIF-01 - AL-01): la tubazione SIF-01 - AL-01 senza lunghezza; si considera compresa nei 8 m dati sul tratto.
- T10 (Alimentazione dell'unità esterna: QE-01 - SZ-01 - UE-01): la tubazione SZ-01 - UE-01 senza lunghezza; si considera compresa nei 10,63 m dati sul tratto.
- T01, T02, T03, T04 (aria di mandata): attraversamenti di parete non dati, assunti 1 per tratto (regola Nove C: una parete per ramo, se il progettista non dice quante).
- T07 (fluido frigorigeno in fase gassosa): attraversamenti di parete non dati, assunti 1 per tratto (regola Nove C: una parete per linea, se il progettista non dice quante).
- T08 (condensa): attraversamenti di parete non dati, assunti 1 per tratto (regola Nove C: una parete, se il progettista non dice quante).

## Note

1. «L da quotare» = (L stimata + 1 m) × 1,15, per eccesso a 0,5 m; minimi: fluido frigorigeno in fase liquida, fluido frigorigeno in fase gassosa 12 m; condensa 10 m; bus di comando 5 m; aria di mandata, aria di ripresa 2 m. La L stimata è un dato del progettista, scritta su ogni tratto.
2. Quantità indicative per un prezzo a corpo, fisso e invariabile: l'installatore le verifica nel sopralluogo obbligatorio prima dell'offerta; le varianti hanno solo il prezzo unitario.
3. Velocità nei tratti di aria di mandata da 1,9 a 2,7 m/s, sulla sezione lorda, dalle portate e dalle sezioni del progettista (verifica: segnala, non corregge).
4. Fornitura da confermare: apparecchiature fornite da Nove C; bocchette e griglie, opere edili del Committente; messa in servizio con Nove C.
5. La distinta non progetta: lunghezze, sezioni, portate, protezioni, marca e modello sono dati del progettista; la distinta li maggiora e ne conta il corredo con regole scritte, ciascuna con la sua fonte.
