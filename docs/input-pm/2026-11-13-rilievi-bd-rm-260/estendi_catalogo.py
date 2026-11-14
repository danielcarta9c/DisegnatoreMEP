"""Estensione del catalogo e dei simboli della copia di lavoro della skill Disegnatore MEP
per BD.RM.260: ventilconvettore canalizzato idronico con lato aria e plenum di mandata NON motorizzato.
Autorizzata da Daniel Carta (PO) il 12/11/2026. Non tocca la skill installata."""
import json, sys
from pathlib import Path
skill = Path(sys.argv[1])
FONTE = "estensione di lavoro BD.RM.260 del 12/11/2026, autorizzata dal PO in chat: forma da approvare dal PO sulla tavola"

cat_p = skill/"dati/catalogo.json"; cat = json.loads(cat_p.read_text(encoding="utf-8"))
sim_p = skill/"dati/simboli.json"; sim = json.loads(sim_p.read_text(encoding="utf-8"))
fam_p = skill/"dati/naming/families.json"; fam = json.loads(fam_p.read_text(encoding="utf-8"))

def porta(i, dom, med, flow, req): return {"id": i, "domain": dom, "medium": med, "flow": flow, "required": req}

# 1. Ventilconvettore canalizzato idronico con lato aria, condensa, comando
cat["file"]["fan-coil-ducted-air.json"] = {
    "id": "fan-coil-ducted-air", "version": "1.0.0", "name": "Ventilconvettore canalizzato",
    "functions": ["emission"],
    "traits": ["maintainable", "fouls_circuit", "shutoff_ordinary", "attachment_inline"],
    "symbol_id": "fan-coil-ducted-air", "composite": False,
    "ports": [
        porta("in", "hydronic", "heating_water", "in", True),
        porta("out", "hydronic", "heating_water", "out", True),
        porta("supply", "aeraulic", "supply_air", "out", False),
        porta("return", "aeraulic", "return_air", "in", False),
        porta("drain", "condensate", "condensate", "out", False),
        porta("power", "control", "power_supply", "in", False),
        porta("bus", "control", "control_bus", "bidirectional", False),
        porta("consenso_in", "control", "control_bus", "in", False),
        porta("consenso", "control", "control_bus", "out", False),
    ],
    "sources": [FONTE, "attacchi aria e condensa come ducted-indoor-unit; attacchi acqua e comando come fan-coil-ducted"],
}
sim["file"]["fan-coil-ducted-air.json"] = {
    "id": "fan-coil-ducted-air", "version": "1.0.0", "name": "Ventilconvettore canalizzato",
    "width_mm": 40.0, "height_mm": 30.0, "allowed_rotations_deg": [0],
    "ports": [
        {"id": "in", "face": "left", "x_mm": 0.0, "y_mm": 7.5},
        {"id": "out", "face": "left", "x_mm": 0.0, "y_mm": 17.5},
        {"id": "supply", "face": "right", "x_mm": 40.0, "y_mm": 12.5},
        {"id": "return", "face": "top", "x_mm": 20.0, "y_mm": 0.0},
        {"id": "drain", "face": "bottom", "x_mm": 22.5, "y_mm": 30.0},
    ],
    "control_ports": [
        {"id": "consenso_in", "face": "left", "x_mm": 0.0, "y_mm": 25.0},
        {"id": "consenso", "face": "right", "x_mm": 40.0, "y_mm": 25.0},
        {"id": "power", "face": "bottom", "x_mm": 7.5, "y_mm": 30.0},
        {"id": "bus", "face": "bottom", "x_mm": 32.5, "y_mm": 30.0},
    ],
    "keep_out": {"left_mm": 2.0, "right_mm": 2.0, "top_mm": 2.0, "bottom_mm": 2.0},
    "stroke_weight": "medium", "source": FONTE + "; corpo dell'unita' interna canalizzata (ducted-indoor-unit) con gli attacchi d'acqua",
}
sim["file"]["fan-coil-ducted-air.svg"] = (
    '<rect x="2.5" y="2.5" width="35" height="25"/>'
    '<path d="M7 5 L10 7 L7 9 L10 11 L7 13 L10 15 L7 17 L10 19 L7 21"/>'
    '<path d="M12 5 L15 7 L12 9 L15 11 L12 13 L15 15 L12 17 L15 19 L12 21"/>'
    '<circle cx="27" cy="12.5" r="5.5"/><line x1="27" y1="12.5" x2="27" y2="8.4"/>'
    '<line x1="27" y1="12.5" x2="23.45" y2="14.55"/><line x1="27" y1="12.5" x2="30.55" y2="14.55"/>'
    '<path d="M4.5 23.5 L4.5 25.5 L35.5 25.5 L35.5 23.5"/><circle cx="22.5" cy="22" r="1.5"/>'
    '<g data-moncone="in"><line x1="0" y1="7.5" x2="2.5" y2="7.5"/></g>'
    '<g data-moncone="out"><line x1="0" y1="17.5" x2="2.5" y2="17.5"/></g>'
    '<g data-port="supply"><path d="M37.5 9.5 L39.5 9.5 L39.5 15.5 L37.5 15.5"/><line x1="37.5" y1="12.5" x2="40" y2="12.5"/></g>'
    '<g data-port="return"><path d="M15 2.5 L15 0.5 L25 0.5 L25 2.5"/><line x1="20" y1="0" x2="20" y2="2.5"/></g>'
    '<g data-port="drain"><line x1="22.5" y1="23.5" x2="22.5" y2="30"/></g>'
    '<g data-comando="consenso_in"><line x1="0" y1="25" x2="2.5" y2="25"/></g>'
    '<g data-comando="consenso"><line x1="40" y1="25" x2="37.5" y2="25"/></g>'
    '<g data-comando="power"><line x1="7.5" y1="30" x2="7.5" y2="27.5"/></g>'
    '<g data-comando="bus"><line x1="32.5" y1="30" x2="32.5" y2="27.5"/></g>\n'
)

# 2. Plenum di mandata NON motorizzato a 2 e 3 attacchi
if not any(f["function"] == "air_distribution" for f in fam["families"]):
    i = next(k for k, f in enumerate(fam["families"]) if f["function"] == "air_zoning")
    fam["families"].insert(i + 1, {"function": "air_distribution", "prefix": "PL", "name": "Plenum di mandata"})
NOMI = {2: "due", 3: "tre"}
for n in (2, 3):
    ys = [5.0, 17.5, 30.0][:n]; h = 20.0 if n == 2 else 32.5
    # a due uscite il pezzo ha tre attacchi: l'ingresso sta in asse con la prima uscita (regola B4)
    yin = 5.0 if n == 2 else 12.5
    cat["file"][f"supply-plenum-{n}.json"] = {
        "id": f"supply-plenum-{n}", "version": "1.0.0", "name": f"Plenum di mandata a {NOMI[n]} attacchi",
        "functions": ["air_distribution"], "traits": ["shutoff_ordinary", "attachment_inline"],
        "symbol_id": f"supply-plenum-{n}", "composite": False,
        "ports": [porta("in", "aeraulic", "supply_air", "in", True)]
                 + [porta(f"out_{k+1}", "aeraulic", "supply_air", "out", True) for k in range(n)],
        "sources": [FONTE, "plenum di zona (zoning-plenum) senza serrande ne' motori"],
    }
    sim["file"][f"supply-plenum-{n}.json"] = {
        "id": f"supply-plenum-{n}", "version": "1.0.0", "name": f"Plenum di mandata a {NOMI[n]} attacchi",
        "width_mm": 40.0, "height_mm": h, "allowed_rotations_deg": [0],
        "ports": [{"id": "in", "face": "left", "x_mm": 0.0, "y_mm": yin}]
                 + [{"id": f"out_{k+1}", "face": "right", "x_mm": 40.0, "y_mm": y} for k, y in enumerate(ys)],
        "keep_out": {"left_mm": 2.0, "right_mm": 2.0, "top_mm": 0.0, "bottom_mm": 0.0},
        "stroke_weight": "medium", "source": FONTE + "; il disegno del plenum di zona senza le serrande",
    }
    body = (f'<rect x="2.5" y="0" width="35" height="{h:g}"/>'
            f'<g data-port="in"><line x1="0" y1="{yin:g}" x2="2.5" y2="{yin:g}"/><path d="M2.5 {yin-3:g} L0.5 {yin-3:g} L0.5 {yin+3:g} L2.5 {yin+3:g}"/></g>'
            f'<line x1="2.5" y1="{yin:g}" x2="20" y2="{yin:g}"/>'
            f'<line x1="20" y1="5" x2="20" y2="{ys[-1]:g}"/>')
    for k, y in enumerate(ys):
        body += (f'<line x1="20" y1="{y:g}" x2="37.5" y2="{y:g}"/>'
                 f'<g data-port="out_{k+1}"><line x1="37.5" y1="{y:g}" x2="40" y2="{y:g}"/><path d="M37.5 {y-2:g} L39.5 {y-2:g} L39.5 {y+2:g} L37.5 {y+2:g}"/></g>')
    sim["file"][f"supply-plenum-{n}.svg"] = body + "\n"

for p, d in ((cat_p, cat), (sim_p, sim), (fam_p, fam)):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print("estensione scritta")
