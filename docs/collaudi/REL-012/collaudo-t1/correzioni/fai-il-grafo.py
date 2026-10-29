"""Il grafo del collaudo T1 di REL-012 (canalizzato a quattro uscite), rifatto dopo le
correzioni: e' lo script del collaudo (`lavoro/gen_grafo.py`) con il plenum a quattro
serrande al posto del ripiego «uscita 5 tappata». Nient'altro e' cambiato.

    python3 docs/collaudi/REL-012/collaudo-t1/correzioni/fai-il-grafo.py [uscita.json]
"""
import json, sys
from pathlib import Path
out = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).with_name("grafo.json"))
def comp(id, d, props=None, tag=None, **kw):
    c = {"id": id, "definition_id": d, "tag": tag, "properties": props or {}}
    c.update(kw); return c
def con(id, net, a, pa, b, pb, sezione=None, L=None, props=None, scritta=None):
    c = {"id": id, "network_id": net, "endpoint_a": {"component_id": a, "port_id": pa},
         "endpoint_b": {"component_id": b, "port_id": pb}, "properties": props or {}}
    if sezione is not None: c["sezione"] = sezione
    if L is not None: c["lunghezza_m"] = L
    if scritta is not None: c["scritta"] = scritta
    return c
g = {
 "schema_version": "1.1.0",
 "metadata": {"project_id": "canalizzato-appartamento-secondo-piano", "client": "ND",
   "project_name": "Canalizzato aria-aria in pompa di calore - appartamento al secondo piano",
   "commission_code": "ND", "revision": "00", "issue_date": "2026-10-29"},
 "plant_regime": "up_to_35_kw",
 "networks": [
  {"id": "frigo-liquido", "name": "Linea frigorifera del liquido", "domain": "refrigerant", "medium": "refrigerant_liquid"},
  {"id": "frigo-gas", "name": "Linea frigorifera del gas", "domain": "refrigerant", "medium": "refrigerant_gas"},
  {"id": "mandata-aria", "name": "Mandata dell'aria", "domain": "aeraulic", "medium": "supply_air"},
  {"id": "ripresa-aria", "name": "Ripresa dell'aria", "domain": "aeraulic", "medium": "return_air"},
  {"id": "condensa", "name": "Scarico della condensa", "domain": "condensate", "medium": "condensate"},
  {"id": "alim-ue", "name": "Alimentazione dell'unita' esterna", "domain": "control", "medium": "power_supply"},
  {"id": "alim-airzone", "name": "Alimentazione della centrale di zona", "domain": "control", "medium": "power_supply"},
  {"id": "collegamento-ui-ue", "name": "Collegamento fra unita' interna ed esterna", "domain": "control", "medium": "interconnection"},
  {"id": "bus-termostati", "name": "Bus ai termostati di zona", "domain": "control", "medium": "control_bus"},
  {"id": "motori-serrande", "name": "Comando dei motori delle serrande", "domain": "control", "medium": "control_bus"},
  {"id": "interfaccia-airzone", "name": "Collegamento centrale di zona - unita' interna", "domain": "control", "medium": "control_bus"},
  {"id": "comando-filo", "name": "Comando a filo dell'unita' interna", "domain": "control", "medium": "control_bus"}
 ],
 "components": [
  comp("ue", "split-outdoor-unit", {"power_kw": 7.1, "potenza": "7,1 kW", "marca": "Mitsubishi Electric", "modello": "SUZ-M71VA", "refrigerante": "R32", "etichetta": "Terrazzo"}),
  comp("ui", "ducted-indoor-unit", {"marca": "Mitsubishi Electric", "modello": "PEAD-M71JA", "pompa_condensa": "a bordo", "posizione": "controsoffitto del disimpegno"}),
  comp("plenum", "zoning-plenum-4", {"marca": "Airzone", "tipo": "plenum motorizzato a 4 uscite Ø200"}),
  comp("centrale-zona", "zone-controller", {"marca": "Airzone"}),
  comp("bocchetta-matrimoniale", "air-supply-terminal", {"etichetta": "Z1 Camera matrimoniale"}),
  comp("bocchetta-singola", "air-supply-terminal", {"etichetta": "Z2 Camera singola"}),
  comp("bocchetta-soggiorno-1", "air-supply-terminal", {"etichetta": "Z3 Soggiorno (sopra il varco)"}),
  comp("bocchetta-soggiorno-2", "air-supply-terminal", {"etichetta": "Z3 Soggiorno (veletta)"}),
  comp("ripresa", "return-air-terminal", {"dimensione": "800×300", "etichetta": "Disimpegno"}),
  comp("sifone", "condensate-trap", {}),
  comp("scarico-cucina", "condensate-outlet", {"etichetta": "Scarico della cucina"}),
  comp("quadro", "electrical-panel", {"etichetta": "Ingresso"}),
  comp("sezionatore", "isolator-switch", {"etichetta": "vicino all'unita' esterna"}),
  comp("termostato-matrimoniale", "room-thermostat", {"marca": "Airzone", "modello": "Think a filo", "etichetta": "Z1 Camera matrimoniale"}),
  comp("termostato-singola", "room-thermostat", {"marca": "Airzone", "modello": "Think a filo", "etichetta": "Z2 Camera singola"}),
  comp("termostato-soggiorno", "room-thermostat", {"marca": "Airzone", "modello": "Think a filo", "etichetta": "Z3 Soggiorno"}),
  comp("comando-filo", "wired-remote", {"marca": "Mitsubishi Electric", "modello": "PAR-41MAA", "etichetta": "Ingresso"})
 ],
 "connections": [
  con("c-liquido", "frigo-liquido", "ue", "liquid", "ui", "liquid", '1/4"', 9),
  con("c-gas", "frigo-gas", "ue", "gas", "ui", "gas", '5/8"', 9),
  con("c-link", "collegamento-ui-ue", "ue", "link", "ui", "link", "4G1,5", 10),
  con("c-mandata-plenum", "mandata-aria", "ui", "supply", "plenum", "in", None, 0),
  con("c-ramo-matrimoniale", "mandata-aria", "plenum", "out_1", "bocchetta-matrimoniale", "a", "Ø200", 5, {"portata_m3h": 300}),
  con("c-ramo-singola", "mandata-aria", "plenum", "out_2", "bocchetta-singola", "a", "Ø200", 3, {"portata_m3h": 220}),
  con("c-ramo-soggiorno-1", "mandata-aria", "plenum", "out_3", "bocchetta-soggiorno-1", "a", "Ø200", 4, {"portata_m3h": 300}),
  con("c-ramo-soggiorno-2", "mandata-aria", "plenum", "out_4", "bocchetta-soggiorno-2", "a", "Ø200", 6, {"portata_m3h": 300}),
  con("c-ripresa", "ripresa-aria", "ripresa", "a", "ui", "return", "800×300", 0),
  con("c-condensa-1", "condensa", "ui", "drain", "sifone", "a", "PVC Ø32", 8),
  con("c-condensa-2", "condensa", "sifone", "b", "scarico-cucina", "a", "PVC Ø32", 0),
  con("c-alim-ue-1", "alim-ue", "quadro", "out_1", "sezionatore", "a", "3G4", 18),
  con("c-alim-ue-2", "alim-ue", "sezionatore", "b", "ue", "power", "3G4"),
  con("c-alim-airzone", "alim-airzone", "quadro", "out_2", "centrale-zona", "power", "3G1,5", 8),
  con("c-bus-matrimoniale", "bus-termostati", "centrale-zona", "bus_1", "termostato-matrimoniale", "a", None, 7),
  con("c-bus-singola", "bus-termostati", "centrale-zona", "bus_2", "termostato-singola", "a", None, 5),
  con("c-bus-soggiorno", "bus-termostati", "centrale-zona", "bus_3", "termostato-soggiorno", "a", None, 9),
  con("c-motori", "motori-serrande", "centrale-zona", "serrande", "plenum", "motori", None, 0),
  con("c-interfaccia", "interfaccia-airzone", "centrale-zona", "p1p2", "ui", "p1p2_b"),
  con("c-comando-filo", "comando-filo", "ui", "p1p2_a", "comando-filo", "a", "2×0,75", 6)
 ],
 "assumptions": [
  {"id": "a-plenum", "status": "approved", "text": "Il plenum motorizzato Airzone a 4 uscite: la voce del catalogo a quattro serrande."},
  {"id": "a-zone", "status": "approved", "text": "Zone: 4 uscite e 3 zone. Le due bocchette del soggiorno (sopra il varco e sulla veletta a x=1) sono due serrande asservite allo stesso termostato Z3. Il grafo non ha un modo di dire l'asservimento: lo dicono le etichette Z3 sulle due bocchette."},
  {"id": "a-bus-ordine", "status": "approved", "text": "Bus ai termostati 7, 5 e 9 m: letti nell'ordine in cui il testo elenca le zone (camera matrimoniale 7 m, camera singola 5 m, soggiorno 9 m)."},
  {"id": "a-sezioni-mancanti", "status": "proposed", "text": "Sezioni e lunghezze che il testo non da': la sezione del cavo bus Airzone ai termostati; la sezione e la lunghezza del collegamento fra la centrale Airzone e l'unita' interna; la lunghezza del tratto fra sezionatore e unita' esterna (i 18 m sono stati messi fra quadro e sezionatore). Senza, quei tratti restano senza scritta o con DA DEFINIRE."},
  {"id": "a-diretti", "status": "approved", "text": "Raccordi diretti, lunghezza zero: il plenum attaccato alla bocca di mandata della UI; la ripresa 800x300 sotto la UI, nel disimpegno; il cablaggio fra centrale Airzone e motori delle serrande, di fabbrica."},
  {"id": "a-condensa", "status": "approved", "text": "Condensa: 8 m di PVC Ø32 dalla UI al sifone, e il sifone sull'allaccio allo scarico della cucina. La pompa di condensa e' a bordo della UI (non disegnata come pezzo)."},
  {"id": "a-potenza", "status": "approved", "text": "La potenza 7,1 kW dell'unita' esterna e' quella del testo, nominale; non si dice se in raffrescamento o in riscaldamento. Regime della centrale: fino a 35 kW."},
  {"id": "a-tabella", "status": "proposed", "text": "Per la tabella delle apparecchiature e per la distinta mancano: il modello del plenum Airzone e della centrale di zona; le dimensioni delle bocchette; i dati di scheda dell'unita' esterna (precarica fino a m, carica aggiuntiva g/m, lunghezza massima); l'attacco della condensa della UI; la protezione nel quadro delle due linee. Se non li dai, quelle celle restano vuote o DA DEFINIRE."},
  {"id": "a-cartiglio", "status": "proposed", "text": "Cartiglio: mancano committente, codice di commessa, indirizzo, titolo e numero della tavola. Senza, la tavola esce in bozza con DA DEFINIRE."},
  {"id": "a-diametri", "status": "approved", "text": "Diametri calcolati: non si applica. Sezioni e lunghezze sono date dal progettista, tratto per tratto."}
 ],
 "rule_applications": [], "subsystems": [], "sheets": []
}
json.dump(g, open(out, "w"), ensure_ascii=False, indent=1)
