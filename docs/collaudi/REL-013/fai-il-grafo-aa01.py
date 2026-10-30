"""Scrive examples/distinta/AA-01/grafo-completo.json dal grafo e da dim.json del kit (REL-013).

    cp docs/input-pm/2026-10-29-kit-aria-aria/lavoro/{dimensionamento,grafo}.py <copia>/
    python3 <copia>/dimensionamento.py && python3 <copia>/grafo.py      # scrivono dim.json e grafo.json
    python3 docs/collaudi/REL-013/fai-il-grafo-aa01.py <copia> examples/distinta/AA-01/grafo-completo.json

Gli script del kit scrivono accanto a se': si lanciano su una copia, non nel kit.
Al grafo del kit aggiunge, come dati del progettista: la lunghezza stimata di ogni
tratto (la «L stim.» della tabella delle tratte), le sezioni, le portate dei rami
d'aria, le pareti passate, le protezioni, il minimo della linea dell'unita' esterna,
i dati di carica dell'unita' esterna, l'attacco condensa, la misura delle bocchette,
la centrale nel kit del plenum; e le sigle di bocchette, ripresa e sifone.
"""
import json
import sys
from pathlib import Path

kit = Path(sys.argv[1])
out = Path(sys.argv[2])
g = json.loads((kit / "grafo.json").read_text())
dim = json.loads((kit / "dim.json").read_text())
T = {t["id"]: t for t in dim["tratte"]}
comp = {c["id"]: c for c in g["components"]}


def P(cid):
    return comp[cid]["properties"]


P("ue").update({"refrigerante": "R32", "precarica_fino_a_m": 10, "carica_aggiuntiva_g_m": 20,
                "lunghezza_max_m": 30, "dislivello_max_m": 20})
P("ui").update({"attacco_condensa": "VP20 (Øe 26)", "nota": "pompa condensa a bordo"})
P("plenum").update({"nota": "codice da confermare col distributore"})
P("centrale").update({"compreso_in": "plenum"})
for i in range(1, 6):
    c = comp[f"bocchetta-b{i}"]
    c["tag"] = f"B{i}"
    c["properties"]["dimensione"] = "400×200"
comp["ripresa"]["tag"] = "RA-01"
comp["sifone"]["tag"] = "SIF-01"
lung = {"r-liq": "R-L", "r-gas": "R-G", "c-1": "C-1", "e-1b": "E-1", "e-2": "E-2", "e-3": "E-3",
        "e-4": "E-4", "e-5": "E-5"}
for i in range(1, 6):
    lung[f"a-b{i}"] = f"A-B{i}"
for i in range(1, 5):
    lung[f"e-tz{i}"] = f"E-TZ-0{i}"
sez = {"r-liq": "Ø6,35 (1/4\")", "r-gas": "Ø12,7 (1/2\")", "c-1": "Ø32", "e-1b": "3G2,5", "e-2": "4G1,5",
       "e-3": "3G1,5", "e-4": "2×0,75 (P1-P2)", "e-5": "2×0,75 (P1-P2)", "a-rip": "1000×250"}
for i in range(1, 6):
    sez[f"a-b{i}"] = "Ø200"
for i in range(1, 5):
    sez[f"e-tz{i}"] = "bus Airzone, schermato"
for c in g["connections"]:
    # Il kit scriveva la linea dell'unita' esterna dall'ingresso verso l'uscita, per
    # aggirare il lato del sezionatore (RAPPORTO del kit, §6.3): la validazione della
    # fase 1 di REL-012 la ferma, e il lato lo decide ora il mestiere del sezionatore.
    if c["id"] in ("e-1a", "e-1b"):
        c["endpoint_a"], c["endpoint_b"] = c["endpoint_b"], c["endpoint_a"]
for c in g["connections"]:
    p = c["properties"]
    cid = c["id"]
    if cid in sez:
        p["sezione"] = sez[cid]
    if cid in lung:
        p["lunghezza_m"] = T[lung[cid]]["l_stima_m"]
    if cid in ("a-ui", "a-rip", "e-6"):
        p["lunghezza_m"] = 0
    if cid.startswith("a-b"):
        p["portata_m3h"] = T[lung[cid]]["portata_m3h"]
    if cid == "a-rip":
        p["portata_m3h"] = 1080
    if cid in ("a-b1", "a-b3", "r-gas"):
        p["attraversamenti"] = 2
    if cid == "e-1b":
        p["lunghezza_minima_m"] = 20
        p["protezione"] = "Magnetotermico-differenziale 1P+N C16, Idn 30 mA, tipo A o F, 6 kA"
    if cid == "e-3":
        p["protezione"] = "Magnetotermico 1P+N C6"
    primi = ("sezione", "lunghezza_m", "scritta")
    c["properties"] = {k: p[k] for k in primi if k in p} | {k: v for k, v in p.items() if k not in primi}
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(g, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("scritto", out)
