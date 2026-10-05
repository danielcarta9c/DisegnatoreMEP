"""Le sette tavole di prova approvate, con i simboli nuovi (I-176, I-177), e i piani adattati agli appesi:
lo sfiato non e' piu' alto 10 come quando i piani furono scritti — 5 dal 2 ottobre 2026, 7,5 col suo
rubinetto dal 5 ottobre (I-211) — e si sposta della differenza, cosi' l'attacco resta dov'era; lo scarico
del volano a due attacchi sta sotto il volano coricato (y del volano + 10). Strumento di sessione:

    python docs/collaudi/REL-005/prova-po-1/tavole_di_prova.py <cartella-di-uscita>
"""
import importlib.util, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location("c", ROOT / "docs/collaudi/REL-007/collaudo.py")
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.cartiglio import Cartiglio
from disegnatore_mep.graphics.registry import SymbolRegistry
simboli = SymbolRegistry.from_directory(ROOT / "assets/symbols")
catalogo = ComponentRegistry.from_directory(ROOT / "examples/layout/catalog", symbols=simboli)
cartiglio = Cartiglio.da_file(ROOT / "assets/cartigli/Cartiglio_NoveC_A3.json")
SFIATO = catalogo.resolve("air-vent").symbol.manifest.height_mm
"""L'altezza dello sfiato di oggi: i piani lo posavano alto 10."""
for nome, impianto, grafo, piano, dati in c.tavole():
    g = json.loads(grafo.read_text("utf-8")); p = json.loads(piano.read_text("utf-8"))
    defin = {x["id"]: x["definition_id"] for x in g["components"]}
    spostati = []
    for pid, pos in p["pezzi"].items():
        if defin.get(pid, "").startswith("air-vent"):
            pos["y"] += 10 - SFIATO; spostati.append(pid)
    for k in g["connections"]:
        for a, b in ((k["endpoint_a"], k["endpoint_b"]), (k["endpoint_b"], k["endpoint_a"])):
            if defin.get(a["component_id"]) == "buffer-two-port" and a["port_id"] == "drain" and b["component_id"] in p["pezzi"]:
                p["pezzi"][b["component_id"]]["y"] = p["pezzi"][a["component_id"]]["y"] + 10; spostati.append(b["component_id"])
            # Lo sfiato del volano coricato torna addosso al volano: sopra la mandata ci era
            # andato solo perche' il volano ritto gliela portava sul cielo («A4 cede a B1»).
            if defin.get(a["component_id"]) == "buffer-two-port" and a["port_id"] == "vent" and b["component_id"] in p["pezzi"]:
                v = p["pezzi"][a["component_id"]]
                p["pezzi"][b["component_id"]].update({"x": v["x"] + 10, "y": v["y"] - SFIATO}); spostati.append(b["component_id"] + " addosso")
    adattato = OUT / f"piano-{nome}.json"; adattato.write_text(json.dumps(p, indent=1), "utf-8")
    modello = c.con_i_dati(grafo, impianto, dati)
    esito, foglio, svg, dxf = c.esegui(nome, modello, adattato, simboli, catalogo, cartiglio, OUT)
    print(nome, "spostati:", spostati)
