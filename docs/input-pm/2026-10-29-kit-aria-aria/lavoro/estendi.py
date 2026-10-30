"""Estensione aria-aria della copia di lavoro della skill disegnatore-mep (AA-01).

Da lanciare su una copia pulita:  rm -rf skill && cp -r skill-orig skill && python3 estendi.py
Aggiunge: simboli, voci di catalogo, fluidi, famiglie, stili di linea, layer DXF,
la scritta manuale per tratta (connections[].properties.scritta) e i telai con
banda tabella larga (A3T, A2T, A1T).
"""
import json
import re
from pathlib import Path

SK = Path(__file__).parent / "skill"
DATI = SK / "dati"
PKG = SK / "scripts" / "disegnatore_mep"
FONTE = "proposta della sessione del 29/10/2026 (caso di prova AA-01, canalizzato aria-aria): forma da approvare dal PO sulla tavola"


def carica(p):
    return json.loads(p.read_text(encoding="utf-8"))


def salva(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- simboli
def porta(pid, face, x, y):
    return {"id": pid, "face": face, "x_mm": x, "y_mm": y}


SIMBOLI = {}

# Unita' esterna split: mantello, ventilatore a sinistra, compressore a destra.
SIMBOLI["split-outdoor-unit"] = (
    {"id": "split-outdoor-unit", "version": "1.0.0", "name": "Unità esterna ad espansione diretta",
     "width_mm": 40.0, "height_mm": 30.0, "allowed_rotations_deg": [0],
     "ports": [porta("liquid", "right", 40.0, 7.5), porta("gas", "right", 40.0, 17.5),
               porta("power", "bottom", 10.0, 30.0), porta("link", "bottom", 27.5, 30.0)],
     "keep_out": {"left_mm": 0.0, "right_mm": 2.0, "top_mm": 0.0, "bottom_mm": 2.0},
     "stroke_weight": "medium", "source": FONTE},
    '<rect x="2.5" y="2.5" width="35" height="25"/>'
    '<circle cx="13" cy="15" r="7.5"/>'
    '<line x1="13" y1="15" x2="13" y2="9.4"/><line x1="13" y1="15" x2="8.15" y2="17.8"/>'
    '<line x1="13" y1="15" x2="17.85" y2="17.8"/>'
    '<circle cx="29" cy="15" r="5"/><path d="M26.2 18.3 L29 10.8 L31.8 18.3 Z"/>'
    '<line x1="37.5" y1="7.5" x2="40" y2="7.5"/><line x1="37.5" y1="17.5" x2="40" y2="17.5"/>'
    '<line x1="10" y1="27.5" x2="10" y2="30"/><line x1="27.5" y1="27.5" x2="27.5" y2="30"/>'
)

# Unita' interna canalizzata: batteria a sinistra, ventilatore, collare di mandata a destra,
# bocca di ripresa in alto, vaschetta con pompa condensa in basso.
SIMBOLI["ducted-indoor-unit"] = (
    {"id": "ducted-indoor-unit", "version": "1.0.0", "name": "Unità interna canalizzata",
     "width_mm": 40.0, "height_mm": 30.0, "allowed_rotations_deg": [0],
     "ports": [porta("liquid", "left", 0.0, 7.5), porta("gas", "left", 0.0, 17.5),
               porta("supply", "right", 40.0, 12.5), porta("p1p2_a", "right", 40.0, 25.0),
               porta("return", "top", 20.0, 0.0),
               porta("link", "bottom", 7.5, 30.0), porta("drain", "bottom", 22.5, 30.0),
               porta("p1p2_b", "bottom", 32.5, 30.0)],
     "keep_out": {"left_mm": 2.0, "right_mm": 2.0, "top_mm": 2.0, "bottom_mm": 2.0},
     "stroke_weight": "medium", "source": FONTE},
    '<rect x="2.5" y="2.5" width="35" height="25"/>'
    '<path d="M7 5 L10 7 L7 9 L10 11 L7 13 L10 15 L7 17 L10 19 L7 21"/>'
    '<path d="M12 5 L15 7 L12 9 L15 11 L12 13 L15 15 L12 17 L15 19 L12 21"/>'
    '<circle cx="27" cy="12.5" r="5.5"/>'
    '<line x1="27" y1="12.5" x2="27" y2="8.4"/><line x1="27" y1="12.5" x2="23.45" y2="14.55"/>'
    '<line x1="27" y1="12.5" x2="30.55" y2="14.55"/>'
    '<path d="M4.5 23.5 L4.5 25.5 L35.5 25.5 L35.5 23.5"/>'
    '<circle cx="22.5" cy="22" r="1.5"/>'
    '<line x1="0" y1="7.5" x2="2.5" y2="7.5"/><line x1="0" y1="17.5" x2="2.5" y2="17.5"/>'
    '<path d="M37.5 9.5 L40 9.5 M37.5 15.5 L40 15.5"/><line x1="37.5" y1="12.5" x2="40" y2="12.5"/>'
    '<line x1="37.5" y1="25" x2="40" y2="25"/>'
    '<path d="M15 2.5 L15 0.5 L25 0.5 L25 2.5"/><line x1="20" y1="0" x2="20" y2="2.5"/>'
    '<line x1="7.5" y1="27.5" x2="7.5" y2="30"/><line x1="22.5" y1="23.5" x2="22.5" y2="30"/>'
    '<line x1="32.5" y1="27.5" x2="32.5" y2="30"/>'
)

# Plenum motorizzato a cinque serrande; i motori vanno alla centrale di zona.
_outs = [5.0, 17.5, 30.0, 42.5, 55.0]
_corpo = ['<rect x="2.5" y="0" width="35" height="57.5"/>',
          '<line x1="0" y1="12.5" x2="2.5" y2="12.5"/>',
          '<path d="M0 9.5 L2.5 9.5 M0 15.5 L2.5 15.5"/>',
          '<line x1="2.5" y1="12.5" x2="20" y2="12.5"/><line x1="20" y1="5" x2="20" y2="55"/>']
for y in _outs:
    _corpo.append(f'<rect x="27.5" y="{y - 2:g}" width="5" height="4"/>')
    _corpo.append(f'<line x1="28" y1="{y + 1.5:g}" x2="32" y2="{y - 1.5:g}"/>')
    _corpo.append(f'<line x1="32.5" y1="{y:g}" x2="40" y2="{y:g}"/>')
    _corpo.append(f'<line x1="20" y1="{y:g}" x2="27.5" y2="{y:g}"/>')
SIMBOLI["zoning-plenum-5"] = (
    {"id": "zoning-plenum-5", "version": "1.0.0", "name": "Plenum motorizzato di zona a cinque serrande",
     "width_mm": 40.0, "height_mm": 57.5, "allowed_rotations_deg": [0],
     "ports": [porta("in", "left", 0.0, 12.5), porta("motori", "bottom", 20.0, 57.5)]
     + [porta(f"out_{i + 1}", "right", 40.0, y) for i, y in enumerate(_outs)],
     "keep_out": {"left_mm": 2.0, "right_mm": 2.0, "top_mm": 0.0, "bottom_mm": 2.0},
     "stroke_weight": "medium", "source": FONTE},
    "".join(_corpo),
)

# Centrale di zona: comanda i motori delle serrande, dialoga con la UI (P1-P2) e coi termostati.
_bus = [7.5, 22.5, 37.5, 52.5]
_c = ['<rect x="2.5" y="2.5" width="25" height="55"/>', '<line x1="15" y1="0" x2="15" y2="2.5"/>',
      '<line x1="0" y1="10" x2="2.5" y2="10"/><line x1="0" y1="20" x2="2.5" y2="20"/>',
      '<rect x="6" y="6" width="12" height="7"/><line x1="8" y1="9.5" x2="16" y2="9.5"/>']
for y in _bus:
    _c.append(f'<line x1="27.5" y1="{y:g}" x2="30" y2="{y:g}"/><circle cx="25" cy="{y:g}" r="0.9"/>')
SIMBOLI["zone-controller"] = (
    {"id": "zone-controller", "version": "1.0.0", "name": "Centrale di zona",
     "width_mm": 30.0, "height_mm": 60.0, "allowed_rotations_deg": [0],
     "ports": [porta("serrande", "top", 15.0, 0.0), porta("p1p2", "left", 0.0, 10.0), porta("power", "left", 0.0, 20.0)]
     + [porta(f"bus_{i + 1}", "right", 30.0, y) for i, y in enumerate(_bus)],
     "keep_out": {"left_mm": 2.0, "right_mm": 2.0, "top_mm": 2.0, "bottom_mm": 0.0},
     "stroke_weight": "medium", "source": FONTE},
    "".join(_c),
)

# Ripresa: griglia con plenum e filtro.
SIMBOLI["return-grille"] = (
    {"id": "return-grille", "version": "1.0.0", "name": "Griglia di ripresa con plenum e filtro",
     "width_mm": 10.0, "height_mm": 10.0, "allowed_rotations_deg": [0, 90, 180, 270],
     "ports": [porta("a", "right", 10.0, 5.0)],
     "keep_out": {"left_mm": 0.0, "right_mm": 2.0, "top_mm": 0.0, "bottom_mm": 0.0},
     "stroke_weight": "medium", "source": FONTE},
    '<rect x="0.8" y="1.2" width="7.2" height="7.6"/>'
    '<line x1="0.8" y1="3.1" x2="8" y2="3.1"/><line x1="0.8" y1="5" x2="8" y2="5"/>'
    '<line x1="0.8" y1="6.9" x2="8" y2="6.9"/>'
    '<line x1="8" y1="5" x2="10" y2="5"/>'
)

# Sifone sulla condensa (organo in linea).
SIMBOLI["condensate-trap"] = (
    {"id": "condensate-trap", "version": "1.0.0", "name": "Sifone ispezionabile",
     "width_mm": 10.0, "height_mm": 5.0, "allowed_rotations_deg": [0, 90, 180, 270], "inline_gap_mm": 10.0,
     "ports": [porta("a", "left", 0.0, 2.5), porta("b", "right", 10.0, 2.5)],
     "keep_out": {"left_mm": 2.0, "right_mm": 2.0, "top_mm": 0.0, "bottom_mm": 0.0},
     "stroke_weight": "medium", "source": FONTE},
    '<path d="M0 2.5 L3 2.5 L3 4.6 L7 4.6 L7 2.5 L10 2.5"/><line x1="3" y1="0.6" x2="3" y2="2.5"/>'
)

# Scarico della condensa nella rete di scarico (confine).
SIMBOLI["condensate-outlet"] = (
    {"id": "condensate-outlet", "version": "1.0.0", "name": "Allaccio allo scarico",
     "width_mm": 5.0, "height_mm": 10.0, "allowed_rotations_deg": [0, 90, 180, 270],
     "ports": [porta("a", "top", 2.5, 0.0)],
     "keep_out": {"left_mm": 0.0, "right_mm": 0.0, "top_mm": 2.0, "bottom_mm": 0.0},
     "stroke_weight": "medium", "source": FONTE},
    '<line x1="2.5" y1="0" x2="2.5" y2="3"/><path d="M0.5 3 L4.5 3 L2.5 6.2 Z"/>'
    '<line x1="2.5" y1="6.2" x2="2.5" y2="9"/><line x1="0.5" y1="9" x2="4.5" y2="9"/>'
)

# Quadro elettrico (confine dell'alimentazione).
SIMBOLI["electrical-panel"] = (
    {"id": "electrical-panel", "version": "1.0.0", "name": "Quadro elettrico",
     "width_mm": 25.0, "height_mm": 15.0, "allowed_rotations_deg": [0],
     "ports": [porta("out_1", "top", 7.5, 0.0), porta("out_2", "top", 17.5, 0.0)],
     "keep_out": {"left_mm": 0.0, "right_mm": 0.0, "top_mm": 2.0, "bottom_mm": 0.0},
     "stroke_weight": "medium", "source": FONTE},
    '<rect x="0.5" y="2.5" width="24" height="12"/><path d="M0.5 14.5 L24.5 2.5 L24.5 14.5 Z" fill="currentColor"/>'
    '<line x1="7.5" y1="0" x2="7.5" y2="2.5"/><line x1="17.5" y1="0" x2="17.5" y2="2.5"/>'
)

# Sezionatore onnipolare (organo in linea).
SIMBOLI["isolator-switch"] = (
    {"id": "isolator-switch", "version": "1.0.0", "name": "Sezionatore onnipolare",
     "width_mm": 5.0, "height_mm": 5.0, "allowed_rotations_deg": [0, 90, 180, 270], "inline_gap_mm": 5.0,
     "ports": [porta("a", "left", 0.0, 2.5), porta("b", "right", 5.0, 2.5)],
     "keep_out": {"left_mm": 2.0, "right_mm": 2.0, "top_mm": 0.0, "bottom_mm": 0.0},
     "stroke_weight": "medium", "source": FONTE},
    '<line x1="0" y1="2.5" x2="1" y2="2.5"/><line x1="1" y1="2.5" x2="3.9" y2="0.7"/>'
    '<line x1="4" y1="2.5" x2="5" y2="2.5"/><line x1="4" y1="1.6" x2="4" y2="3.4"/>'
)

# Termostato di zona.
SIMBOLI["room-thermostat"] = (
    {"id": "room-thermostat", "version": "1.0.0", "name": "Termostato di zona",
     "width_mm": 10.0, "height_mm": 10.0, "allowed_rotations_deg": [0, 90, 180, 270],
     "ports": [porta("a", "left", 0.0, 5.0)],
     "keep_out": {"left_mm": 2.0, "right_mm": 0.0, "top_mm": 0.0, "bottom_mm": 0.0},
     "upright_glyphs": [{"id": "sigla", "x_mm": 5.5, "y_mm": 5.0}],
     "stroke_weight": "medium", "source": FONTE},
    '<line x1="0" y1="5" x2="2" y2="5"/><rect x="2" y="1" width="7" height="8"/>'
    '<g data-glyph="sigla"><path d="M3.7 3 L7.3 3 M5.5 3 L5.5 7.2"/></g>'
)

# Comando a filo dell'unità.
SIMBOLI["wired-remote"] = (
    {"id": "wired-remote", "version": "1.0.0", "name": "Comando a filo",
     "width_mm": 10.0, "height_mm": 10.0, "allowed_rotations_deg": [0, 90, 180, 270],
     "ports": [porta("a", "left", 0.0, 5.0)],
     "keep_out": {"left_mm": 2.0, "right_mm": 0.0, "top_mm": 0.0, "bottom_mm": 0.0},
     "stroke_weight": "medium", "source": FONTE},
    '<line x1="0" y1="5" x2="2" y2="5"/><rect x="2" y="1" width="7" height="8"/>'
    '<rect x="3.5" y="2.4" width="4" height="3"/><circle cx="5.5" cy="7.1" r="0.7"/>'
)


# --------------------------------------------------------------------------- catalogo
def p(pid, domain, medium, flow, required=True):
    return {"id": pid, "domain": domain, "medium": medium, "flow": flow, "required": required}


TRATTI = ["shutoff_ordinary", "attachment_inline"]
CATALOGO = {
    "split-outdoor-unit": {"name": "Unità esterna split a pompa di calore", "functions": ["refrigerant_generation"],
                           "symbol_id": "split-outdoor-unit",
                           "ports": [p("liquid", "refrigerant", "refrigerant_liquid", "bidirectional"),
                                     p("gas", "refrigerant", "refrigerant_gas", "bidirectional"),
                                     p("power", "control", "power_supply", "in"),
                                     p("link", "control", "interconnection", "bidirectional")]},
    "ducted-indoor-unit": {"name": "Unità interna canalizzata ad espansione diretta",
                           "functions": ["direct_expansion_terminal"], "symbol_id": "ducted-indoor-unit",
                           "ports": [p("liquid", "refrigerant", "refrigerant_liquid", "bidirectional"),
                                     p("gas", "refrigerant", "refrigerant_gas", "bidirectional"),
                                     p("supply", "aeraulic", "supply_air", "out"),
                                     p("return", "aeraulic", "return_air", "in"),
                                     p("drain", "condensate", "condensate", "out"),
                                     p("link", "control", "interconnection", "bidirectional"),
                                     p("p1p2_a", "control", "control_bus", "bidirectional"),
                                     p("p1p2_b", "control", "control_bus", "bidirectional", False)]},
    "zoning-plenum-5": {"name": "Plenum motorizzato di zona a cinque serrande",
                        "functions": ["air_zoning"], "symbol_id": "zoning-plenum-5",
                        "ports": [p("in", "aeraulic", "supply_air", "in"),
                                  p("motori", "control", "control_bus", "bidirectional")]
                        + [p(f"out_{i}", "aeraulic", "supply_air", "out") for i in range(1, 6)]},
    "zone-controller": {"name": "Centrale di zona", "functions": ["zone_control"], "symbol_id": "zone-controller",
                        "ports": [p("serrande", "control", "control_bus", "bidirectional"),
                                  p("p1p2", "control", "control_bus", "bidirectional"),
                                  p("power", "control", "power_supply", "in")]
                        + [p(f"bus_{i}", "control", "control_bus", "bidirectional", False) for i in range(1, 5)]},
    "air-supply-terminal": {"name": "Bocchetta di mandata con plenum di raccordo", "functions": ["air_terminal"],
                            "symbol_id": "air-diffuser",
                            "ports": [p("a", "aeraulic", "supply_air", "in")]},
    "return-air-terminal": {"name": "Griglia di ripresa con plenum e filtro", "functions": ["air_return"],
                            "symbol_id": "return-grille",
                            "ports": [p("a", "aeraulic", "return_air", "out")]},
    "condensate-trap": {"name": "Sifone ispezionabile sulla condensa", "functions": ["condensate_trap"],
                        "symbol_id": "condensate-trap",
                        "ports": [p("a", "condensate", "condensate", "in"), p("b", "condensate", "condensate", "out")]},
    "condensate-outlet": {"name": "Allaccio della condensa allo scarico", "functions": ["boundary"],
                          "symbol_id": "condensate-outlet",
                          "ports": [p("a", "condensate", "condensate", "in")]},
    "electrical-panel": {"name": "Quadro elettrico", "functions": ["power_source"], "symbol_id": "electrical-panel",
                         "ports": [p("out_1", "control", "power_supply", "out"),
                                   p("out_2", "control", "power_supply", "out", False)]},
    "isolator-switch": {"name": "Sezionatore onnipolare", "functions": ["power_isolation"],
                        "symbol_id": "isolator-switch",
                        "ports": [p("a", "control", "power_supply", "in"), p("b", "control", "power_supply", "out")]},
    "room-thermostat": {"name": "Termostato di zona", "functions": ["room_control"], "symbol_id": "room-thermostat",
                        "ports": [p("a", "control", "control_bus", "bidirectional")]},
    "wired-remote": {"name": "Comando a filo dell'unità", "functions": ["unit_control"], "symbol_id": "wired-remote",
                     "ports": [p("a", "control", "control_bus", "bidirectional")]},
}

FLUIDI = [("return_air", "aria di ripresa"), ("condensate", "condensa"),
          ("power_supply", "alimentazione elettrica"), ("interconnection", "collegamento elettrico fra le unita'"),
          ("control_bus", "bus di comando")]

FAMIGLIE = [
    ("air_zoning", "PLZ", "Plenum motorizzato di zona", "direct_expansion_terminal"),
    ("zone_control", "CZ", "Centrale di zona", "air_zoning"),
    ("air_return", "RA", "Ripresa aria", "air_terminal"),
    ("condensate_trap", "SIF", "Sifone", "drain"),
    ("power_source", "QE", "Quadro elettrico", None),
    ("power_isolation", "SZ", "Sezionatore", None),
    ("room_control", "TZ", "Termostato di zona", None),
    ("unit_control", "CF", "Comando a filo", None),
]


def estendi_dati():
    s = carica(DATI / "simboli.json")
    s["file"]["air-diffuser.json"]["name"] = "Bocchetta di mandata con plenum di raccordo"
    for sid, (man, svg) in SIMBOLI.items():
        s["file"][f"{sid}.json"] = man
        s["file"][f"{sid}.svg"] = svg
    salva(DATI / "simboli.json", s)

    c = carica(DATI / "catalogo.json")
    for cid, v in CATALOGO.items():
        c["file"][f"{cid}.json"] = {"id": cid, "version": "1.0.0", "name": v["name"], "functions": v["functions"],
                                    "traits": TRATTI, "symbol_id": v["symbol_id"], "composite": False,
                                    "ports": v["ports"], "sources": [FONTE]}
    salva(DATI / "catalogo.json", c)

    m = carica(DATI / "naming" / "media.json")
    presenti = {x["medium"] for x in m["media"]}
    for med, nome in FLUIDI:
        if med not in presenti:
            m["media"].append({"medium": med, "name": nome})
    salva(DATI / "naming" / "media.json", m)

    f = carica(DATI / "naming" / "families.json")
    funz = [x["function"] for x in f["families"]]
    for fn, pre, nome, dopo in FAMIGLIE:
        if fn in funz:
            continue
        voce = {"function": fn, "prefix": pre, "name": nome}
        i = funz.index(dopo) + 1 if dopo in funz else len(funz)
        f["families"].insert(i, voce)
        funz.insert(i, fn)
    salva(DATI / "naming" / "families.json", f)


# --------------------------------------------------------------------------- codice
def sostituisci(rel, vecchio, nuovo, conta=1):
    path = PKG / rel
    testo = path.read_text(encoding="utf-8")
    n = testo.count(vecchio)
    if n != conta:
        raise SystemExit(f"{rel}: atteso {conta} volte, trovato {n}: {vecchio[:70]!r}")
    path.write_text(testo.replace(vecchio, nuovo), encoding="utf-8")


def estendi_codice():
    # Stili di linea e nomi in legenda dei fluidi nuovi.
    sostituisci("layout/legend.py",
                '    "solar_fluid": ("#c71585", "none"),\n}',
                '    "solar_fluid": ("#c71585", "none"),\n'
                '    "power_supply": ("#b03a2e", "4 1 1 1"),\n'
                '    "interconnection": ("#a04000", "4 1 1 1 1 1"),\n'
                '    "control_bus": ("#1f618d", "1.5 1.5"),\n}')
    sostituisci("layout/legend.py", '    "refrigerant_gas": ("#6c3483", "6 2"),', '    "refrigerant_gas": ("#6c3483", "3 1.5"),')
    sostituisci("layout/legend.py",
                '    "solar_fluid": "Fluido solare",\n}',
                '    "solar_fluid": "Fluido solare",\n'
                '    "power_supply": "Alimentazione elettrica 230 V",\n'
                '    "interconnection": "Collegamento UI-UE (alimentazione e segnale)",\n'
                '    "control_bus": "Bus di comando e regolazione",\n}')
    # Il ritorno dell'aria e' l'aria di ripresa: colore proprio, non lo spostamento della mandata.
    sostituisci("layout/legend.py",
                '    "#c71585": "#c71585",\n}',
                '    "#c71585": "#c71585",\n'
                '    "#b03a2e": "#b03a2e",\n    "#a04000": "#a04000",\n    "#1f618d": "#1f618d",\n'
                '    "#616a6b": "#616a6b",\n}')
    # Layer DXF: refrigerante, aria e condensa ci sono gia'; si aggiungono i circuiti elettrici.
    sostituisci("graphics/dxf.py",
                '_RETI: dict[tuple[str, bool], str] = {\n',
                '_RETI: dict[tuple[str, bool], str] = {\n'
                '    ("power_supply", True): "E-POWR-CIRC",\n    ("power_supply", False): "E-POWR-CIRC",\n'
                '    ("interconnection", True): "E-POWR-LINK",\n    ("interconnection", False): "E-POWR-LINK",\n'
                '    ("control_bus", True): "E-CTRL-BUS",\n    ("control_bus", False): "E-CTRL-BUS",\n')
    # Fluidi senza verso: aria, refrigerante, condensa e circuiti elettrici hanno una riga sola
    # in legenda, col loro nome, e lo stesso tratto in qualunque verso li si legga.
    sostituisci("layout/legend.py",
                'def style_for(medium: str, supply: bool = True) -> tuple[str, str]:\n',
                'NON_DIREZIONALI = frozenset({"supply_air", "return_air", "refrigerant_liquid", "refrigerant_gas",\n'
                '                             "condensate", "power_supply", "interconnection", "control_bus"})\n'
                '"""Fluidi che in legenda non hanno andata e ritorno (estensione aria-aria, AA-01)."""\n\n\n'
                'def style_for(medium: str, supply: bool = True) -> tuple[str, str]:\n'
                '    if medium in NON_DIREZIONALI:\n'
                '        return MEDIUM_STYLES.get(medium, DEFAULT_STYLE)\n')
    sostituisci("layout/legend.py",
                "        for medium, name in sorted(by_medium.items())\n        for supply in (True, False)\n    ]\n",
                "        for medium, name in sorted(by_medium.items())\n        for supply in (True, False)\n"
                "        if medium not in NON_DIREZIONALI\n    ] + [\n"
                "        (medium, name, True) for medium, name in sorted(by_medium.items()) if medium in NON_DIREZIONALI\n    ]\n")
    sostituisci("layout/legend.py",
                "        disegnate = {(route.medium, route.supply) for route in routes}\n"
                "        keys = [key for key in keys if (key[0], key[2]) in disegnate]\n",
                "        disegnate = {(route.medium, route.supply) for route in routes}\n"
                "        disegnate |= {(route.medium, True) for route in routes if route.medium in NON_DIREZIONALI}\n"
                "        keys = [key for key in keys if (key[0], key[2]) in disegnate]\n")
    # Scritta manuale per tratta: connections[].properties.scritta ("Ø200 · L 5,0 m").
    # Il tratto e' la tratta del motore che contiene quella tubazione; la scritta si posa
    # col posatore dei diametri, e un DN calcolato sullo stesso tratto cede il posto.
    sostituisci("diametri/tratti.py",
                "    if project.diametri is None:\n        return ()\n    return tuple(\n"
                "        item for item in tratti_del_diametro(project, catalog, trunks) if item.porta_il_dn\n    )\n",
                "    manuali = _tratti_con_scritta(project, catalog, trunks)\n"
                "    if project.diametri is None:\n        return manuali\n"
                "    coperti = {c for item in manuali for c in item.connection_ids}\n"
                "    return manuali + tuple(\n"
                "        item for item in tratti_del_diametro(project, catalog, trunks)\n"
                "        if item.porta_il_dn and not (item.connection_ids & coperti)\n    )\n\n\n"
                "@dataclass(frozen=True)\nclass _ScrittaManuale:\n    scritta: str\n\n\n"
                "def _tratti_con_scritta(project, catalog, trunks=None):\n"
                "    scritte = {c.id: c.properties.get('scritta') for c in project.connections\n"
                "               if isinstance(c.properties.get('scritta'), str) and c.properties.get('scritta').strip()}\n"
                "    if not scritte:\n        return ()\n"
                "    tutte = list(trunks) if trunks is not None else tratte_del_progetto(project, catalog)\n"
                "    tratti = []\n"
                "    for tratta in tutte:\n"
                "        testi = [scritte[c] for c in tratta.connection_ids if c in scritte]\n"
                "        if not testi:\n            continue\n"
                "        tratti.append(TrattoDelDiametro(chiavi=(tratta.connection_ids,), reti=(tratta.network_id,),\n"
                "                                        capi=(tratta.start, tratta.end), portata_m3h=None, fonti=(),\n"
                "                                        diametro=_ScrittaManuale(testi[0]), richiesto=True,\n"
                "                                        strada_principale=True))\n"
                "    return tuple(tratti)\n")
    sostituisci("layout/diametri.py",
                'TESTO_DELLA_LEGENDA = "diametro interno netto minimo in mm, materiale a scelta"',
                'TESTO_DELLA_LEGENDA = "diametro o sezione e lunghezza da quotare (riserva compresa) di ogni tratto: tabella delle tratte"')
    sostituisci("layout/diametri.py", 'CAMPIONE_DELLA_LEGENDA = "Øi"', 'CAMPIONE_DELLA_LEGENDA = "Ø · L"')

    # Tabella delle apparecchiature: anche UI, plenum, termostati e comando.
    sostituisci("graphics/tabella.py",
                '    "circulation",\n    "expansion",\n)',
                '    "circulation",\n    "expansion",\n    "direct_expansion_terminal",\n    "air_zoning",\n'
                '    "zone_control",\n    "unit_control",\n)')
    sostituisci("graphics/tabella.py",
                '    "circulation": ("flow_rate_m3h", "head_kpa", "head_m"),\n}',
                '    "circulation": ("flow_rate_m3h", "head_kpa", "head_m"),\n'
                '    "direct_expansion_terminal": ("power_kw", "flow_rate_m3h"),\n}')

    # Telai con le tabelle: l'area del disegno si restringe a destra e in basso, e la
    # zona che resta libera accoglie la tabella delle tratte, le note e il computo
    # (scritti dopo, da tabelle.py, nello stesso SVG e nel DXF).
    sostituisci("graphics/frame.py",
                'NOVE_C_A3 = SheetFrame(standard=A3_LANDSCAPE)\n',
                'class SheetFrameConTabelle(SheetFrame):\n'
                '    """Un telaio ordinario con una riserva per le tabelle (estensione AA-01)."""\n\n'
                '    riserva_destra_mm: FiniteFloat = 0.0\n    riserva_sotto_mm: FiniteFloat = 0.0\n\n'
                '    @property\n    def drawing_rect_mm(self) -> Rect:\n'
                '        body = self.body_rect_mm\n'
                '        return Rect(x_mm=body.x_mm, y_mm=body.y_mm,\n'
                '                    width_mm=body.width_mm - self.legend_width_mm - self.riserva_destra_mm,\n'
                '                    height_mm=body.height_mm - self.riserva_sotto_mm)\n\n\n'
                'NOVE_C_A3 = SheetFrame(standard=A3_LANDSCAPE)\n')
    sostituisci("graphics/frame.py",
                'NOVE_C_A1 = SheetFrame(standard=A1_LANDSCAPE)\n',
                'NOVE_C_A1 = SheetFrame(standard=A1_LANDSCAPE)\n\n'
                'NOVE_C_A2T = SheetFrameConTabelle(standard=A2_LANDSCAPE, riserva_destra_mm=175.0, riserva_sotto_mm=135.0)\n'
                '"""A2 con le tabelle: disegno in alto a sinistra, tratte e note a destra, computo in basso."""\n')
    sostituisci("piano/formato.py", 'FormatoOrdinario = Literal["A3", "A2", "A1"]',
                'FormatoOrdinario = Literal["A3", "A2", "A1", "A2T"]')
    sostituisci("piano/esecutore.py",
                '    voluta = _LARGHEZZE_MM[nome]\n',
                '    if nome == "A2T":\n'
                '        from disegnatore_mep.graphics.frame import NOVE_C_A2T\n\n'
                '        return NOVE_C_A2T\n'
                '    voluta = _LARGHEZZE_MM[nome]\n')


if __name__ == "__main__":
    estendi_dati()
    estendi_codice()
    print("estensione applicata")
