"""Un piano agli atti con lo spazio per il ritegno: tutto cio' che sta dal collettore in la' si
sposta a destra di 15 mm, il resto resta dov'e'.

    python3 docs/collaudi/REL-011/proposta-1/fai_spazio.py <piano-agli-atti> <x-del-collettore> <uscita>

Non e' il pezzo 3 che ricompone: e' la mano della sessione che fa posto a un pezzo in piu', per
avere la tavola «dopo» da mettere accanto a quella di prima. Il resto della composizione non
cambia, e i numeri del disegno lo dicono.
"""

import json
import sys
from pathlib import Path

PASSO = 15.0

piano = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
soglia = float(sys.argv[2])
for pezzo in piano["pezzi"].values():
    if float(pezzo["x"]) >= soglia:
        pezzo["x"] = float(pezzo["x"]) + PASSO
piano["note"] = [
    f"REL-011 proposta 1: il piano {Path(sys.argv[1]).name} con cio' che sta da x={soglia:g} in la' "
    f"spostato di {PASSO:g} mm a destra, per il ritegno sulla mandata di ogni generatore. "
    "Nient'altro cambia.",
    *piano.get("note", []),
]
Path(sys.argv[3]).write_text(json.dumps(piano, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
