"""Un piano agli atti con lo spazio per il corredo nuovo delle pompe di calore (REL-011).

    python3 docs/collaudi/REL-011/piani/fai_spazio.py <grafo-completo> <piano> <uscita> [<mm>]

Dal 4 novembre 2026 ogni pompa di calore porta sui suoi attacchi il giunto antivibrante
(D-222) e, nelle case, la valvola antigelo (D-230); le macchine in parallelo il ritegno
(D-217). Sono pezzi in linea in piu' fra la macchina e il primo raccordo, e un piano
scritto per il corredo di prima non lascia il tratto dritto per posarli.

Non e' il pezzo 3 che ricompone: e' la mano della sessione che fa posto. Ogni pezzo del
piano che sta **dalla parte degli attacchi** di una pompa di calore — a destra delle
macchine, per i piani in cui le macchine stanno a sinistra — si sposta di <mm> (25 di
default) nel verso degli attacchi; le macchine restano dove sono. Il resto della
composizione non cambia.
"""

import json
import sys
from pathlib import Path

grafo = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
piano = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
passo = float(sys.argv[4]) if len(sys.argv) > 4 else 25.0
pompe = {c["id"] for c in grafo["components"] if c["definition_id"].startswith("heat-pump-air-water")}
pezzi = piano["pezzi"]
xs = [float(pezzi[p]["x"]) for p in pompe if p in pezzi]
if not xs:
    raise SystemExit("nessuna pompa di calore posata nel piano")
soglia = max(xs)
spostati = 0
for nome, pezzo in pezzi.items():
    if nome in pompe:
        continue
    if float(pezzo["x"]) > soglia:
        pezzo["x"] = float(pezzo["x"]) + passo
        spostati += 1
piano.setdefault("note", [])
piano["note"] = [
    f"REL-011: {spostati} pezzi a destra delle pompe di calore spostati di {passo:g} mm per il giunto, "
    "la valvola antigelo e il ritegno sui loro attacchi (docs/collaudi/REL-011/piani/fai_spazio.py).",
    *piano["note"],
]
Path(sys.argv[3]).write_text(json.dumps(piano, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"{spostati} pezzi spostati di {passo:g} mm")
