"""Due giri del banco a confronto, tavola per tavola.

    python3 docs/collaudi/REL-011/confronta.py <esiti-prima.json> <esiti-dopo.json>

Per ogni tavola: «identica» se l'SVG ha lo stesso hash, altrimenti le due sintesi (o
l'errore). In fondo il conto.
"""

import json
import sys
from pathlib import Path

prima = {item["tavola"]: item for item in json.loads(Path(sys.argv[1]).read_text("utf-8"))}
dopo = {item["tavola"]: item for item in json.loads(Path(sys.argv[2]).read_text("utf-8"))}
uguali = 0
for nome in prima:
    a, b = prima[nome], dopo.get(nome, {})
    if a.get("svg") and a.get("svg") == b.get("svg"):
        uguali += 1
        print(f"{nome:24} identica")
        continue
    print(f"{nome:24} CAMBIA")
    print(f"{'':26}prima: {a.get('sintesi') or a.get('errore')}")
    print(f"{'':26}dopo:  {b.get('sintesi') or b.get('errore')}")
print(f"\n{uguali} identiche su {len(prima)}")
