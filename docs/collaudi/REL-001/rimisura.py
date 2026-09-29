"""Il comando della skill sui dati del repository, per rimisurare quello che un agente consegna (REL-001).

Quello che un agente in camera pulita riferisce non è una misura finché la sessione non l'ha
rieseguito (D-152, regola 3). Questo strumento lancia lo stesso comando della skill —
`disegnatore_mep.skill.main` — con il motore, i simboli, il catalogo, le regole e il naming del
repository invece di quelli copiati nella cartella della skill: dal grafo completo e dal piano
dell'agente deve uscire la stessa tavola, byte per byte. E' uno strumento di sessione. Uso:

    python docs/collaudi/REL-001/rimisura.py disegna <grafo-completo.json> --piano <piano.json> --out <cartella>
"""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from disegnatore_mep.skill import cartelle_del_repository, main  # noqa: E402

if __name__ == "__main__":
    spec = importlib.util.spec_from_file_location("grafo_leggibile", ROOT / "examples/graph/build_plant_graph.py")
    assert spec is not None and spec.loader is not None
    grafo_leggibile = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(grafo_leggibile)
    raise SystemExit(main(sys.argv[1:], cartelle_del_repository(ROOT), grafo_leggibile.build))
