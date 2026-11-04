# Il foglio dei calcoli delle varianti della villetta (I-279)

## villetta-calcolo

| rete | da | a | dati del progettista | potenza kW | ΔT K | portata m³/h | Øi minimo mm | tubo | Øi reale mm | velocità m/s | massima m/s | note |
|---|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| Circuito della pompa di calore | GT-01 | VOL-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **MS 32×3** | 26,0 | 1,08 | 1,3 |  |
| Circuito della pompa di calore | VD-01 | BOL-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **MS 32×3** | 26,0 | 1,08 | 1,3 |  |
| Circuito della pompa di calore | VOL-01 | RC-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **MS 32×3** | 26,0 | 1,08 | 1,3 |  |
| Circuito della pompa di calore | BOL-01 | RC-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **MS 32×3** | 26,0 | 1,08 | 1,3 |  |
| Circuito della pompa di calore | RC-01 | GT-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **MS 32×3** | 26,0 | 1,08 | 1,3 |  |

## villetta-con-lunghezze

| rete | da | a | dati del progettista | potenza kW | ΔT K | portata m³/h | Øi minimo mm | tubo | Øi reale mm | velocità m/s | massima m/s | note |
|---|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| Circuito della pompa di calore | GT-01 | VOL-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **MS 32×3** | 26,0 | 1,08 | 1,3 |  |
| Circuito della pompa di calore | VD-01 | BOL-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **MS 32×3** | 26,0 | 1,08 | 1,3 |  |
| Circuito della pompa di calore | VOL-01 | RC-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **MS 32×3** | 26,0 | 1,08 | 1,3 |  |
| Circuito della pompa di calore | BOL-01 | RC-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **MS 32×3** | 26,0 | 1,08 | 1,3 |  |
| Circuito della pompa di calore | RC-01 | GT-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **MS 32×3** | 26,0 | 1,08 | 1,3 |  |

### Verifica della prevalenza della pompa a bordo

Darcy-Weisbach con Swamee-Jain, acqua a 40 °C (ν 0,658·10⁻⁶ m²/s), sul diametro interno reale del tubo e con la scabrezza del suo materiale (multistrato 0,007 mm, acciaio 0,045 mm, rame 0,0015 mm); concentrate il 30% delle distribuite. Non entrano le perdite proprie di serpentini, scambiatori e volano.

**GT-01** — il giro piu' costoso di 2:

| da | a | tubo | portata m³/h | velocità m/s | L m | Pa/m | kPa |
|---|---|---|---:|---:|---:|---:|---:|
| GT-01 | VD-01 | MS 32×3 (Øi 26,0) | 2,067 | 1,08 | 12,0 | 506 | 6,07 |
| VD-01 | BOL-01 | MS 32×3 (Øi 26,0) | 2,067 | 1,08 | 4,0 | 506 | 2,02 |
| BOL-01 | RC-01 | MS 32×3 (Øi 26,0) | 2,067 | 1,08 | 4,0 | 506 | 2,02 |
| RC-01 | GT-01 | MS 32×3 (Øi 26,0) | 2,067 | 1,08 | 12,0 | 506 | 6,07 |

Distribuite 16,18 kPa + concentrate 4,85 kPa = **21,04 kPa**; prevalenza utile 10,0 kPa: **NON BASTA**.

## villetta-sezione-ms32-su-tutto

| rete | da | a | dati del progettista | potenza kW | ΔT K | portata m³/h | Øi minimo mm | tubo | Øi reale mm | velocità m/s | massima m/s | note |
|---|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| Circuito della pompa di calore | GT-01 | VOL-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **MS 32×3** | 26,0 | 1,08 | 1,3 | del progettista |
| Circuito della pompa di calore | VD-01 | BOL-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **MS 32×3** | 26,0 | 1,08 | 1,3 | del progettista |
| Circuito della pompa di calore | VOL-01 | RC-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **MS 32×3** | 26,0 | 1,08 | 1,3 | del progettista |
| Circuito della pompa di calore | BOL-01 | RC-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **MS 32×3** | 26,0 | 1,08 | 1,3 | del progettista |
| Circuito della pompa di calore | RC-01 | GT-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **MS 32×3** | 26,0 | 1,08 | 1,3 | del progettista |

## villetta-15kw-ms32-del-progettista

| rete | da | a | dati del progettista | potenza kW | ΔT K | portata m³/h | Øi minimo mm | tubo | Øi reale mm | velocità m/s | massima m/s | note |
|---|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| Circuito della pompa di calore | GT-01 | VOL-01 | GT-01 15 kW, ΔT 5 K | 15,0 | 5,0 | 2,584 | 26,5 | **MS 32×3** | 26,0 | 1,35 | 1,3 | del progettista: oltre la massima, il calcolo sceglierebbe MS 40×3,5 |
| Circuito della pompa di calore | VD-01 | BOL-01 | GT-01 15 kW, ΔT 5 K | 15,0 | 5,0 | 2,584 | 26,5 | **MS 32×3** | 26,0 | 1,35 | 1,3 | del progettista: oltre la massima, il calcolo sceglierebbe MS 40×3,5 |
| Circuito della pompa di calore | VOL-01 | RC-01 | GT-01 15 kW, ΔT 5 K | 15,0 | 5,0 | 2,584 | 26,5 | **MS 32×3** | 26,0 | 1,35 | 1,3 | del progettista: oltre la massima, il calcolo sceglierebbe MS 40×3,5 |
| Circuito della pompa di calore | BOL-01 | RC-01 | GT-01 15 kW, ΔT 5 K | 15,0 | 5,0 | 2,584 | 26,5 | **MS 32×3** | 26,0 | 1,35 | 1,3 | del progettista: oltre la massima, il calcolo sceglierebbe MS 40×3,5 |
| Circuito della pompa di calore | RC-01 | GT-01 | GT-01 15 kW, ΔT 5 K | 15,0 | 5,0 | 2,584 | 26,5 | **MS 32×3** | 26,0 | 1,35 | 1,3 | del progettista: oltre la massima, il calcolo sceglierebbe MS 40×3,5 |

## villetta-15kw-calcolo

| rete | da | a | dati del progettista | potenza kW | ΔT K | portata m³/h | Øi minimo mm | tubo | Øi reale mm | velocità m/s | massima m/s | note |
|---|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| Circuito della pompa di calore | GT-01 | VOL-01 | GT-01 15 kW, ΔT 5 K | 15,0 | 5,0 | 2,584 | 23,9 | **MS 40×3,5** | 33,0 | 0,84 | 1,6 |  |
| Circuito della pompa di calore | VD-01 | BOL-01 | GT-01 15 kW, ΔT 5 K | 15,0 | 5,0 | 2,584 | 23,9 | **MS 40×3,5** | 33,0 | 0,84 | 1,6 |  |
| Circuito della pompa di calore | VOL-01 | RC-01 | GT-01 15 kW, ΔT 5 K | 15,0 | 5,0 | 2,584 | 23,9 | **MS 40×3,5** | 33,0 | 0,84 | 1,6 |  |
| Circuito della pompa di calore | BOL-01 | RC-01 | GT-01 15 kW, ΔT 5 K | 15,0 | 5,0 | 2,584 | 23,9 | **MS 40×3,5** | 33,0 | 0,84 | 1,6 |  |
| Circuito della pompa di calore | RC-01 | GT-01 | GT-01 15 kW, ΔT 5 K | 15,0 | 5,0 | 2,584 | 23,9 | **MS 40×3,5** | 33,0 | 0,84 | 1,6 |  |

## villetta-acciaio

| rete | da | a | dati del progettista | potenza kW | ΔT K | portata m³/h | Øi minimo mm | tubo | Øi reale mm | velocità m/s | massima m/s | note |
|---|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| Circuito della pompa di calore | GT-01 | VOL-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **DN 25 (1")** | 27,3 | 0,98 | 1,3 |  |
| Circuito della pompa di calore | VD-01 | BOL-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **DN 25 (1")** | 27,3 | 0,98 | 1,3 |  |
| Circuito della pompa di calore | VOL-01 | RC-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **DN 25 (1")** | 27,3 | 0,98 | 1,3 |  |
| Circuito della pompa di calore | BOL-01 | RC-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **DN 25 (1")** | 27,3 | 0,98 | 1,3 |  |
| Circuito della pompa di calore | RC-01 | GT-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **DN 25 (1")** | 27,3 | 0,98 | 1,3 |  |

## villetta-rame-esecutivo

| rete | da | a | dati del progettista | potenza kW | ΔT K | portata m³/h | Øi minimo mm | tubo | Øi reale mm | velocità m/s | massima m/s | note |
|---|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| Circuito della pompa di calore | GT-01 | VOL-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **Cu 28×1** | 26,0 | 1,08 | 1,3 |  |
| Circuito della pompa di calore | VD-01 | BOL-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **Cu 28×1** | 26,0 | 1,08 | 1,3 |  |
| Circuito della pompa di calore | VOL-01 | RC-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **Cu 28×1** | 26,0 | 1,08 | 1,3 |  |
| Circuito della pompa di calore | BOL-01 | RC-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **Cu 28×1** | 26,0 | 1,08 | 1,3 |  |
| Circuito della pompa di calore | RC-01 | GT-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **Cu 28×1** | 26,0 | 1,08 | 1,3 |  |

## villetta-esecutivo

| rete | da | a | dati del progettista | potenza kW | ΔT K | portata m³/h | Øi minimo mm | tubo | Øi reale mm | velocità m/s | massima m/s | note |
|---|---|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| Circuito della pompa di calore | GT-01 | VOL-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **MS 32×3** | 26,0 | 1,08 | 1,3 |  |
| Circuito della pompa di calore | VD-01 | BOL-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **MS 32×3** | 26,0 | 1,08 | 1,3 |  |
| Circuito della pompa di calore | VOL-01 | RC-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **MS 32×3** | 26,0 | 1,08 | 1,3 |  |
| Circuito della pompa di calore | BOL-01 | RC-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **MS 32×3** | 26,0 | 1,08 | 1,3 |  |
| Circuito della pompa di calore | RC-01 | GT-01 | GT-01 12 kW, ΔT 5 K | 12,0 | 5,0 | 2,067 | 23,7 | **MS 32×3** | 26,0 | 1,08 | 1,3 |  |
