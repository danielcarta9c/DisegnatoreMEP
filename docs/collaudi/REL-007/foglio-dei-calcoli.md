# Il foglio dei calcoli delle tavole di REL-007

Scritto da `collaudo.py` con `diametri.foglio`: una riga per tratto d'acqua. **I dati sono di prova, e inventati** (`dati-di-prova.json`, e la tabella di `REL-006`). Le basi del calcolo sono **D-193**: DN come diametro interno netto, velocità massima per diametro (tab. 9 del Quaderno Caleffi n. 5), acqua a 4,18 kJ/(kg·K) e 1000 kg/m³.

## tavola-1 — Due pompe di calore in parallelo con accumulo combinato

| rete | da | a | dati del progettista | potenza kW | ΔT K | portata m³/h | DN | velocità m/s | massima m/s | note |
|---|---|---|---|---:|---:|---:|---|---:|---:|---|
| Acqua fredda sanitaria | AF-03 | VM-01 | ACS-01 1,50 m³/h | – | – | 1,500 | **Øi 25** | 0,85 | 1,3 |  |
| Circuito primario | PDC-01 | RC-01 | PDC-01 15 kW, ΔT 5 K | 15,0 | 5,0 | 2,584 | **Øi 32** | 0,89 | 1,6 |  |
| Circuito primario | PDC-02 | RC-01 | PDC-02 15 kW, ΔT 5 K | 15,0 | 5,0 | 2,584 | **Øi 32** | 0,89 | 1,6 |  |
| Circuito primario | RC-01 | ACC-01 | PDC-01 15 kW, ΔT 5 K + PDC-02 15 kW, ΔT 5 K | 30,0 | 5,0 | 5,167 | **Øi 40** | 1,14 | 1,8 |  |
| Circuito primario | ACC-01 | RC-02 | PDC-01 15 kW, ΔT 5 K + PDC-02 15 kW, ΔT 5 K | 30,0 | 5,0 | 5,167 | **Øi 40** | 1,14 | 1,8 |  |
| Circuito primario | RC-02 | PDC-01 | PDC-01 15 kW, ΔT 5 K | 15,0 | 5,0 | 2,584 | **Øi 32** | 0,89 | 1,6 |  |
| Circuito primario | RC-02 | PDC-02 | PDC-02 15 kW, ΔT 5 K | 15,0 | 5,0 | 2,584 | **Øi 32** | 0,89 | 1,6 |  |
| Circuito secondario | ACC-01 | RAD-01 | CIR-01 2,50 m³/h | – | – | 2,500 | **Øi 32** | 0,86 | 1,6 |  |
| Circuito secondario | RAD-01 | ACC-01 | CIR-01 2,50 m³/h | – | – | 2,500 | **Øi 32** | 0,86 | 1,6 |  |
| Acqua fredda sanitaria | AF-01 | ACC-01 | AF-01 1,50 m³/h | – | – | 1,500 | **Øi 25** | 0,85 | 1,3 |  |
| Acqua calda sanitaria | ACC-01 | ACS-01 | ACS-01 1,50 m³/h | – | – | 1,500 | **Øi 25** | 0,85 | 1,3 |  |

## tavola-2 — Pompa di calore con deviazione fra climatizzazione e ACS

| rete | da | a | dati del progettista | potenza kW | ΔT K | portata m³/h | DN | velocità m/s | massima m/s | note |
|---|---|---|---|---:|---:|---:|---|---:|---:|---|
| Acqua fredda sanitaria | AF-03 | VM-01 | – | – | – | – | – | – | – | la portata non viene dai dati del progettista |
| Circuito primario | PDC-01 | VOL-01 | PDC-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | **Øi 25** | 1,17 | 1,3 |  |
| Circuito primario | VOL-01 | RC-01 | PDC-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | **Øi 25** | 1,17 | 1,3 |  |
| Circuito primario | VD-01 | BOL-01 | PDC-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | **Øi 25** | 1,17 | 1,3 |  |
| Circuito primario | BOL-01 | RC-01 | PDC-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | **Øi 25** | 1,17 | 1,3 |  |
| Circuito primario | RC-01 | PDC-01 | PDC-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | **Øi 25** | 1,17 | 1,3 |  |
| Circuito secondario | VOL-01 | VC-01 | CIR-01 2,00 m³/h | – | – | 2,000 | **Øi 25** | 1,13 | 1,3 |  |
| Circuito secondario | VC-01 | VOL-01 | CIR-01 2,00 m³/h | – | – | 2,000 | **Øi 25** | 1,13 | 1,3 |  |
| Acqua fredda sanitaria | AF-01 | BOL-01 | – | – | – | – | – | – | – | la portata non viene dai dati del progettista |
| Acqua calda sanitaria | BOL-01 | ACS-01 | – | – | – | – | – | – | – | la portata non viene dai dati del progettista |

## tavola-3 — Pompa di calore diretta su pavimento radiante, ACS separata

| rete | da | a | dati del progettista | potenza kW | ΔT K | portata m³/h | DN | velocità m/s | massima m/s | note |
|---|---|---|---|---:|---:|---:|---|---:|---:|---|
| Acqua fredda sanitaria | AF-03 | VM-01 | – | – | – | – | – | – | – | la portata non viene dai dati del progettista |
| Circuito di riscaldamento | PDC-01 | COL-01 | PDC-01 9 kW, ΔT 5 K | 9,0 | 5,0 | 1,550 | **Øi 25** | 0,88 | 1,3 |  |
| Circuito di riscaldamento | COL-01 | PAV-01 | PAV-01 5 kW, ΔT 5 K | 5,0 | 5,0 | 0,861 | **Øi 20** | 0,76 | 1,1 |  |
| Circuito di riscaldamento | COL-01 | PAV-02 | PAV-02 4 kW, ΔT 5 K | 4,0 | 5,0 | 0,689 | **Øi 15** | 1,08 | 1,1 |  |
| Circuito di riscaldamento | PAV-01 | RC-01 | PAV-01 5 kW, ΔT 5 K | 5,0 | 5,0 | 0,861 | **Øi 20** | 0,76 | 1,1 |  |
| Circuito di riscaldamento | PAV-02 | RC-01 | PAV-02 4 kW, ΔT 5 K | 4,0 | 5,0 | 0,689 | **Øi 15** | 1,08 | 1,1 |  |
| Circuito di riscaldamento | RC-01 | VOL-01 | PAV-01 5 kW, ΔT 5 K + PAV-02 4 kW, ΔT 5 K | 9,0 | 5,0 | 1,550 | **Øi 25** | 0,88 | 1,3 |  |
| Circuito di riscaldamento | VOL-01 | PDC-01 | PDC-01 9 kW, ΔT 5 K | 9,0 | 5,0 | 1,550 | **Øi 25** | 0,88 | 1,3 |  |
| Acqua fredda sanitaria | AF-01 | BPC-01 | – | – | – | – | – | – | – | la portata non viene dai dati del progettista |
| Acqua calda sanitaria | BPC-01 | ACS-01 | – | – | – | – | – | – | – | la portata non viene dai dati del progettista |

## tavola-4 — Sistema ibrido con pompa di calore e caldaia a condensazione

| rete | da | a | dati del progettista | potenza kW | ΔT K | portata m³/h | DN | velocità m/s | massima m/s | note |
|---|---|---|---|---:|---:|---:|---|---:|---:|---|
| Circuito primario | PDC-01 | RC-01 | PDC-01 16 kW, ΔT 5 K | 16,0 | 5,0 | 2,756 | **Øi 32** | 0,95 | 1,6 |  |
| Circuito primario | VD-01 | SCA-01 | CAL-01 25 kW, ΔT 10 K | 25,0 | 10,0 | 2,153 | **Øi 25** | 1,22 | 1,3 |  |
| Circuito primario | SCA-01 | VCR-01 | CAL-01 25 kW, ΔT 10 K | 25,0 | 10,0 | 2,153 | **Øi 25** | 1,22 | 1,3 |  |
| Circuito primario | CAL-01 | RC-02 | CAL-01 25 kW, ΔT 10 K | 25,0 | 10,0 | 2,153 | **Øi 25** | 1,22 | 1,3 |  |
| Circuito primario | CAL-01 | RC-01 | CAL-01 25 kW, ΔT 10 K | 25,0 | 10,0 | 2,153 | **Øi 25** | 1,22 | 1,3 |  |
| Circuito primario | RC-01 | VOL-01 | CAL-01 25 kW, ΔT 10 K + PDC-01 16 kW, ΔT 5 K | – | – | 4,909 | **Øi 40** | 1,09 | 1,8 |  |
| Circuito primario | VOL-01 | RC-02 | CAL-01 25 kW, ΔT 10 K + PDC-01 16 kW, ΔT 5 K | – | – | 4,909 | **Øi 40** | 1,09 | 1,8 |  |
| Circuito primario | RC-02 | PDC-01 | PDC-01 16 kW, ΔT 5 K | 16,0 | 5,0 | 2,756 | **Øi 32** | 0,95 | 1,6 |  |
| Circuito secondario | VOL-01 | RAD-01 | CIR-01 3,00 m³/h | – | – | 3,000 | **Øi 32** | 1,04 | 1,6 |  |
| Circuito secondario | RAD-01 | VOL-01 | CIR-01 3,00 m³/h | – | – | 3,000 | **Øi 32** | 1,04 | 1,6 |  |
| Acqua fredda sanitaria | AF-01 | SCA-01 | AF-01 0,70 m³/h | – | – | 0,700 | **Øi 20** | 0,62 | 1,1 |  |
| Acqua calda sanitaria | SCA-01 | ACS-01 | ACS-01 0,70 m³/h | – | – | 0,700 | **Øi 20** | 0,62 | 1,1 |  |

## tavola-5 — Tre pompe di calore in cascata con tre circuiti secondari e ACS

| rete | da | a | dati del progettista | potenza kW | ΔT K | portata m³/h | DN | velocità m/s | massima m/s | note |
|---|---|---|---|---:|---:|---:|---|---:|---:|---|
| Acqua fredda sanitaria | AF-03 | VM-02 | ACS-01 2,00 m³/h | – | – | 2,000 | **Øi 25** | 1,13 | 1,3 |  |
| Circuito primario | PDC-01 | RC-01 | PDC-01 40 kW, ΔT 5 K | 40,0 | 5,0 | 6,890 | **Øi 40** | 1,52 | 1,8 |  |
| Circuito primario | RC-02 | RC-03 | PDC-01 40 kW, ΔT 5 K + PDC-02 40 kW, ΔT 5 K + PDC-03 40 kW, ΔT 5 K | 120,0 | 5,0 | 20,670 | **Øi 65** | 1,73 | 2,2 |  |
| Circuito primario | RC-03 | PDC-01 | PDC-01 40 kW, ΔT 5 K | 40,0 | 5,0 | 6,890 | **Øi 40** | 1,52 | 1,8 |  |
| Circuito primario | RC-03 | RC-04 | PDC-02 40 kW, ΔT 5 K + PDC-03 40 kW, ΔT 5 K | 80,0 | 5,0 | 13,780 | **Øi 50** | 1,95 | 2,0 |  |
| Circuito primario | RC-04 | PDC-02 | PDC-02 40 kW, ΔT 5 K | 40,0 | 5,0 | 6,890 | **Øi 40** | 1,52 | 1,8 |  |
| Circuito primario | RC-04 | PDC-03 | PDC-03 40 kW, ΔT 5 K | 40,0 | 5,0 | 6,890 | **Øi 40** | 1,52 | 1,8 |  |
| Circuito primario | PDC-02 | RC-05 | PDC-02 40 kW, ΔT 5 K | 40,0 | 5,0 | 6,890 | **Øi 40** | 1,52 | 1,8 |  |
| Circuito primario | RC-05 | RC-01 | PDC-02 40 kW, ΔT 5 K + PDC-03 40 kW, ΔT 5 K | 80,0 | 5,0 | 13,780 | **Øi 50** | 1,95 | 2,0 |  |
| Circuito primario | PDC-03 | RC-05 | PDC-03 40 kW, ΔT 5 K | 40,0 | 5,0 | 6,890 | **Øi 40** | 1,52 | 1,8 |  |
| Circuito primario | RC-01 | VOL-01 | PDC-01 40 kW, ΔT 5 K + PDC-02 40 kW, ΔT 5 K + PDC-03 40 kW, ΔT 5 K | 120,0 | 5,0 | 20,670 | **Øi 65** | 1,73 | 2,2 |  |
| Circuito primario | VD-01 | BOL-01 | PDC-01 40 kW, ΔT 5 K + PDC-02 40 kW, ΔT 5 K + PDC-03 40 kW, ΔT 5 K | 120,0 | 5,0 | 20,670 | **Øi 65** | 1,73 | 2,2 |  |
| Circuito primario | VOL-01 | RC-02 | PDC-01 40 kW, ΔT 5 K + PDC-02 40 kW, ΔT 5 K + PDC-03 40 kW, ΔT 5 K | 120,0 | 5,0 | 20,670 | **Øi 65** | 1,73 | 2,2 |  |
| Circuito primario | BOL-01 | RC-02 | PDC-01 40 kW, ΔT 5 K + PDC-02 40 kW, ΔT 5 K + PDC-03 40 kW, ΔT 5 K | 120,0 | 5,0 | 20,670 | **Øi 65** | 1,73 | 2,2 |  |
| Circuito secondario | VOL-01 | RC-06 | CIR-02 3,20 m³/h + CIR-03 5,00 m³/h + CIR-01 4,50 m³/h | – | – | 12,700 | **Øi 50** | 1,80 | 2,0 |  |
| Circuito secondario | RC-10 | PAV-01 | CIR-03 5,00 m³/h | – | – | 5,000 | **Øi 40** | 1,11 | 1,8 |  |
| Circuito secondario | PAV-01 | RC-09 | CIR-03 5,00 m³/h | – | – | 5,000 | **Øi 40** | 1,11 | 1,8 |  |
| Circuito secondario | RC-09 | VM-01 | CIR-03 5,00 m³/h | – | – | 5,000 | **Øi 40** | 1,11 | 1,8 |  |
| Circuito secondario | RC-09 | RC-08 | CIR-03 5,00 m³/h | – | – | 5,000 | **Øi 40** | 1,11 | 1,8 |  |
| Circuito secondario | RC-07 | VOL-01 | CIR-02 3,20 m³/h + CIR-03 5,00 m³/h + CIR-01 4,50 m³/h | – | – | 12,700 | **Øi 50** | 1,80 | 2,0 |  |
| Circuito secondario | RC-06 | BAT-01 | CIR-01 4,50 m³/h | – | – | 4,500 | **Øi 32** | 1,55 | 1,6 |  |
| Circuito secondario | BAT-01 | RC-07 | CIR-01 4,50 m³/h | – | – | 4,500 | **Øi 32** | 1,55 | 1,6 |  |
| Circuito secondario | RC-06 | RC-10 | CIR-02 3,20 m³/h + CIR-03 5,00 m³/h | – | – | 8,200 | **Øi 50** | 1,16 | 2,0 |  |
| Circuito secondario | RC-10 | VC-01 | CIR-02 3,20 m³/h | – | – | 3,200 | **Øi 32** | 1,11 | 1,6 |  |
| Circuito secondario | VC-01 | RC-08 | CIR-02 3,20 m³/h | – | – | 3,200 | **Øi 32** | 1,11 | 1,6 |  |
| Circuito secondario | RC-08 | RC-07 | CIR-02 3,20 m³/h + CIR-03 5,00 m³/h | – | – | 8,200 | **Øi 50** | 1,16 | 2,0 |  |
| Acqua fredda sanitaria | AF-01 | BOL-01 | AF-01 2,00 m³/h | – | – | 2,000 | **Øi 25** | 1,13 | 1,3 |  |
| Acqua calda sanitaria | BOL-01 | ACS-01 | ACS-01 2,00 m³/h | – | – | 2,000 | **Øi 25** | 1,13 | 1,3 |  |
| Acqua calda sanitaria | BOL-01 | ACS-R | CIR-04 0,80 m³/h | – | – | 0,800 | **Øi 20** | 0,71 | 1,1 |  |

## tavola-6 — Centrale ibrida condominiale con pompa di calore di alta potenza, caldaia modulare e solare termico

| rete | da | a | dati del progettista | potenza kW | ΔT K | portata m³/h | DN | velocità m/s | massima m/s | note |
|---|---|---|---|---:|---:|---:|---|---:|---:|---|
| Acqua calda sanitaria alle utenze | BOL-01 | AL-04 | AL-04 2,50 m³/h | – | – | 2,500 | **Øi 32** | 0,86 | 1,6 |  |
| Acqua fredda sanitaria al bollitore | AL-01 | BOL-01 | AL-01 2,50 m³/h | – | – | 2,500 | **Øi 32** | 0,86 | 1,6 |  |
| Acqua fredda sanitaria al bollitore | AL-03 | VM-01 | AL-04 2,50 m³/h | – | – | 2,500 | **Øi 32** | 0,86 | 1,6 |  |
| Circuito primario dei generatori (volume tecnico e serpentino superiore del bollitore) | GT-02 | RC-01 | GT-02 120 kW, ΔT 5 K | 120,0 | 5,0 | 20,670 | **Øi 65** | 1,73 | 2,2 |  |
| Circuito primario dei generatori (volume tecnico e serpentino superiore del bollitore) | RC-03 | GT-01 | GT-01 150 kW, ΔT 10 K | 150,0 | 10,0 | 12,919 | **Øi 50** | 1,83 | 2,0 |  |
| Circuito primario dei generatori (volume tecnico e serpentino superiore del bollitore) | GT-01 | RC-01 | GT-01 150 kW, ΔT 10 K | 150,0 | 10,0 | 12,919 | **Øi 50** | 1,83 | 2,0 |  |
| Circuito primario dei generatori (volume tecnico e serpentino superiore del bollitore) | RC-01 | VOL-01 | GT-01 150 kW, ΔT 10 K + GT-02 120 kW, ΔT 5 K | – | – | 33,589 | **Øi 80** | 1,86 | 2,5 |  |
| Circuito primario dei generatori (volume tecnico e serpentino superiore del bollitore) | VD-01 | BOL-01 | GT-01 150 kW, ΔT 10 K + GT-02 120 kW, ΔT 5 K | – | – | 33,589 | **Øi 80** | 1,86 | 2,5 |  |
| Circuito primario dei generatori (volume tecnico e serpentino superiore del bollitore) | VOL-01 | RC-02 | GT-01 150 kW, ΔT 10 K + GT-02 120 kW, ΔT 5 K | – | – | 33,589 | **Øi 80** | 1,86 | 2,5 |  |
| Circuito primario dei generatori (volume tecnico e serpentino superiore del bollitore) | BOL-01 | RC-02 | GT-01 150 kW, ΔT 10 K + GT-02 120 kW, ΔT 5 K | – | – | 33,589 | **Øi 80** | 1,86 | 2,5 |  |
| Circuito primario dei generatori (volume tecnico e serpentino superiore del bollitore) | RC-02 | RC-03 | GT-01 150 kW, ΔT 10 K + GT-02 120 kW, ΔT 5 K | – | – | 33,589 | **Øi 80** | 1,86 | 2,5 |  |
| Circuito primario dei generatori (volume tecnico e serpentino superiore del bollitore) | RC-03 | GT-02 | GT-02 120 kW, ΔT 5 K | 120,0 | 5,0 | 20,670 | **Øi 65** | 1,73 | 2,2 |  |
| Circuito secondario dal volume tecnico (radiatori e fan-coil canalizzati) | VOL-01 | RC-04 | CIR-01 4,00 m³/h + CIR-02 6,00 m³/h | – | – | 10,000 | **Øi 50** | 1,41 | 2,0 |  |
| Circuito secondario dal volume tecnico (radiatori e fan-coil canalizzati) | RC-04 | TE-02 | CIR-02 6,00 m³/h | – | – | 6,000 | **Øi 40** | 1,33 | 1,8 |  |
| Circuito secondario dal volume tecnico (radiatori e fan-coil canalizzati) | TE-02 | RC-05 | CIR-02 6,00 m³/h | – | – | 6,000 | **Øi 40** | 1,33 | 1,8 |  |
| Circuito secondario dal volume tecnico (radiatori e fan-coil canalizzati) | RC-04 | TE-01 | CIR-01 4,00 m³/h | – | – | 4,000 | **Øi 32** | 1,38 | 1,6 |  |
| Circuito secondario dal volume tecnico (radiatori e fan-coil canalizzati) | TE-01 | RC-05 | CIR-01 4,00 m³/h | – | – | 4,000 | **Øi 32** | 1,38 | 1,6 |  |
| Circuito secondario dal volume tecnico (radiatori e fan-coil canalizzati) | RC-05 | VOL-01 | CIR-01 4,00 m³/h + CIR-02 6,00 m³/h | – | – | 10,000 | **Øi 50** | 1,41 | 2,0 |  |
| Circuito solare (collettori e serpentino inferiore del bollitore) | GT-03 | BOL-01 | CIR-03 1,20 m³/h | – | – | 1,200 | **Øi 20** | 1,06 | 1,1 |  |
| Circuito solare (collettori e serpentino inferiore del bollitore) | BOL-01 | GT-03 | CIR-03 1,20 m³/h | – | – | 1,200 | **Øi 20** | 1,06 | 1,1 |  |

## tavola-1-retrofit — Due pompe di calore in parallelo con accumulo combinato

| rete | da | a | dati del progettista | potenza kW | ΔT K | portata m³/h | DN | velocità m/s | massima m/s | note |
|---|---|---|---|---:|---:|---:|---|---:|---:|---|
| Acqua fredda sanitaria | AF-03 | VM-01 | – | – | – | – | – | – | – | diametri non chiesti su questa rete |
| Circuito primario | PDC-01 | RC-01 | PDC-01 15 kW, ΔT 5 K | 15,0 | 5,0 | 2,584 | **Øi 32** | 0,89 | 1,6 |  |
| Circuito primario | PDC-02 | RC-01 | PDC-02 15 kW, ΔT 5 K | 15,0 | 5,0 | 2,584 | **Øi 32** | 0,89 | 1,6 |  |
| Circuito primario | RC-01 | ACC-01 | PDC-01 15 kW, ΔT 5 K + PDC-02 15 kW, ΔT 5 K | 30,0 | 5,0 | 5,167 | **Øi 40** | 1,14 | 1,8 |  |
| Circuito primario | ACC-01 | RC-02 | PDC-01 15 kW, ΔT 5 K + PDC-02 15 kW, ΔT 5 K | 30,0 | 5,0 | 5,167 | **Øi 40** | 1,14 | 1,8 |  |
| Circuito primario | RC-02 | PDC-01 | PDC-01 15 kW, ΔT 5 K | 15,0 | 5,0 | 2,584 | **Øi 32** | 0,89 | 1,6 |  |
| Circuito primario | RC-02 | PDC-02 | PDC-02 15 kW, ΔT 5 K | 15,0 | 5,0 | 2,584 | **Øi 32** | 0,89 | 1,6 |  |
| Circuito secondario | ACC-01 | RAD-01 | CIR-01 2,50 m³/h | – | – | 2,500 | – | – | – | rete esistente |
| Circuito secondario | RAD-01 | ACC-01 | CIR-01 2,50 m³/h | – | – | 2,500 | – | – | – | rete esistente |
| Acqua fredda sanitaria | AF-01 | ACC-01 | – | – | – | – | – | – | – | diametri non chiesti su questa rete |
| Acqua calda sanitaria | ACC-01 | ACS-01 | – | – | – | – | – | – | – | rete esistente |
