"""Scrive grafo.json (prima stesura) dai numeri di dim.json."""
import json
from pathlib import Path

L = Path(__file__).parent
dim = json.loads((L / "dim.json").read_text(encoding="utf-8"))
T = {t["id"]: t for t in dim["tratte"]}


def m(x):
    return f"{x:g}".replace(".", ",")


def scritta(tid, testo=None):
    t = T[tid]
    return testo or f"{t['dn']} · L {m(t['l_quot_m'])} m"


reti = [
    ("frigo-liquido", "Linea del liquido", "refrigerant", "refrigerant_liquid"),
    ("frigo-gas", "Linea del gas", "refrigerant", "refrigerant_gas"),
    ("aria-mandata", "Mandata aria alle zone", "aeraulic", "supply_air"),
    ("aria-ripresa", "Ripresa aria", "aeraulic", "return_air"),
    ("condensa", "Scarico condensa", "condensate", "condensate"),
    ("alimentazione-ue", "Alimentazione unita' esterna", "control", "power_supply"),
    ("alimentazione-airzone", "Alimentazione centrale Airzone", "control", "power_supply"),
    ("collegamento", "Collegamento UI-UE", "control", "interconnection"),
    ("p1p2", "Linea P1-P2 dell'unita' interna", "control", "control_bus"),
    ("serrande", "Comando motori serrande", "control", "control_bus"),
    ("bus-airzone", "Bus Airzone ai termostati", "control", "control_bus"),
]

comp = [
    ("ue", "split-outdoor-unit", {"marca": "Daikin", "modello": "RXM60A · 49 kg", "power_kw": 5.7}, "UE-01"),
    ("ui", "ducted-indoor-unit", {"marca": "Daikin", "modello": "FBA60A9 · 1000×800×245 mm · 35 kg", "power_kw": 5.7, "flow_rate_m3h": 1080},
     "UI-01"),
    ("plenum", "zoning-plenum-5", {"marca": "Airzone", "modello": "Easyzone 5 × Ø200, es. AZEZ8DAIBS07M5 · 1425×250×454 mm"},
     "PLZ-01"),
    ("centrale", "zone-controller", {"marca": "Airzone", "modello": "centrale Easyzone e gateway Daikin AZX6GTCDA1 (nel kit)"}, "CZ-01"),
    ("ripresa", "return-air-terminal", {"etichetta": "ripresa 1000×250 · 1080 m³/h (griglia esclusa)"}),
]
for b in dim["bocchette"]:
    comp.append((f"bocchetta-{b['id'].lower()}", "air-supply-terminal",
                 {"etichetta": f"{b['id']} · {b['ambiente'].replace(' 24 m²', '')}"}))
comp += [
    ("sifone", "condensate-trap", {}),
    ("scarico", "condensate-outlet", {"etichetta": "scarico bagno Ø40"}),
    ("quadro", "electrical-panel", {"etichetta": "quadro elettrico (posizione da sopralluogo)"}, "QE-01"),
    ("sezionatore", "isolator-switch", {}, "SZ-01"),
]
zone_t = {"Z1": "Camera 13 m²", "Z2": "Camera 15 m²", "Z3": "Camera 16 m²", "Z4": "Soggiorno-cucina"}
for i, (z, nome) in enumerate(zone_t.items(), start=1):
    comp.append((f"termostato-{i}", "room-thermostat", {"marca": "Airzone", "modello": "Blueface", "etichetta": f"{z} {nome}"},
                 f"TZ-0{i}"))
comp.append(("madoka", "wired-remote", {"marca": "Daikin", "modello": "Madoka BRC1H52W"}, "CF-01"))

conn = []


def c(cid, rete, a, b, testo=None):
    ca, pa = a.split(".")
    cb, pb = b.split(".")
    props = {"scritta": testo} if testo else {}
    conn.append({"id": cid, "network_id": rete, "endpoint_a": {"component_id": ca, "port_id": pa},
                 "endpoint_b": {"component_id": cb, "port_id": pb}, "properties": props})


c("r-liq", "frigo-liquido", "ue.liquid", "ui.liquid", scritta("R-L"))
c("r-gas", "frigo-gas", "ue.gas", "ui.gas", scritta("R-G"))
c("a-ui", "aria-mandata", "ui.supply", "plenum.in")
for i, b in enumerate(dim["bocchette"], start=1):
    t = T[f"A-{b['id']}"]
    c(f"a-{b['id'].lower()}", "aria-mandata", f"plenum.out_{i}", f"bocchetta-{b['id'].lower()}.a",
      f"Ø200 · {t['portata_m3h']} m³/h · L {m(t['l_quot_m'])} m")
c("e-6", "serrande", "plenum.motori", "centrale.serrande", "di fabbrica")
c("a-rip", "aria-ripresa", "ripresa.a", "ui.return")
c("c-1", "condensa", "ui.drain", "sifone.a", scritta("C-1", f"PVC Ø32 · L {m(T['C-1']['l_quot_m'])} m"))
c("c-2", "condensa", "sifone.b", "scarico.a")
c("e-1a", "alimentazione-ue", "ue.power", "sezionatore.b")
c("e-1b", "alimentazione-ue", "sezionatore.a", "quadro.out_1", f"3G2,5 · L {m(T['E-1']['l_quot_m'])} m")
c("e-2", "collegamento", "ue.link", "ui.link", f"4G1,5 · L {m(T['E-2']['l_quot_m'])} m")
c("e-3", "alimentazione-airzone", "quadro.out_2", "centrale.power", f"3G1,5 · L {m(T['E-3']['l_quot_m'])} m")
c("e-4", "p1p2", "ui.p1p2_a", "centrale.p1p2", f"P1-P2 · L {m(T['E-4']['l_quot_m'])} m")
c("e-5", "p1p2", "ui.p1p2_b", "madoka.a", f"P1-P2 · L {m(T['E-5']['l_quot_m'])} m")
for i in range(1, 5):
    c(f"e-tz{i}", "bus-airzone", f"centrale.bus_{i}", f"termostato-{i}.a",
      f"bus · L {m(T[f'E-TZ-0{i}']['l_quot_m'])} m")

grafo = {
    "schema_version": "1.1.0",
    "metadata": {
        "project_id": "caso-prova-aria-aria",
        "client": "Committente (dati omessi)",
        "project_name": "Climatizzazione canalizzata Daikin con zonizzazione Airzone",
        "commission_code": "AA-01",
        "revision": "00",
        "issue_date": "2026-10-29",
        "address": "Indirizzo omesso",
        "sheet_title": "Schema funzionale — impianto di climatizzazione canalizzato",
        "sheet_number": "M.02",
        "drawn_by": "Nove C",
        "checked_by": "Ing. Daniel Carta",
        "header_note": "Caso di prova aria-aria",
    },
    "plant_regime": "up_to_35_kw",
    "networks": [{"id": i, "name": n, "domain": d, "medium": md} for i, n, d, md in reti],
    "components": [{"id": x[0], "definition_id": x[1], "tag": x[3] if len(x) > 3 else None, "properties": x[2]}
                   for x in comp],
    "connections": conn,
    "assumptions": [],
    "rule_applications": [],
    "subsystems": [],
    "sheets": [],
}
(L / "grafo.json").write_text(json.dumps(grafo, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(comp), "pezzi,", len(conn), "tubazioni")
