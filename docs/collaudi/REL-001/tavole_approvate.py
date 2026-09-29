"""Le sette tavole approvate di `REL-008`, rigenerate in SVG con il codice corrente (REL-001).

Sono le tavole su cui si misura il PDF senza browser (criterio 1): gli stessi grafi, piani e
dati di prova del collaudo di `REL-007`, che `REL-008` ha rieseguito con le scritte a 9 punti.
E' uno strumento di sessione. Uso:

    python docs/collaudi/REL-001/tavole_approvate.py <cartella-di-uscita>

e poi `confronto_pdf.py <cartella-di-uscita> <cartella-del-confronto>`.
"""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from disegnatore_mep.catalog.registry import ComponentRegistry  # noqa: E402
from disegnatore_mep.graphics.cartiglio import Cartiglio  # noqa: E402
from disegnatore_mep.graphics.registry import SymbolRegistry  # noqa: E402


def main() -> None:
    spec = importlib.util.spec_from_file_location("collaudo_rel_007", ROOT / "docs/collaudi/REL-007/collaudo.py")
    assert spec is not None and spec.loader is not None
    collaudo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(collaudo)
    simboli = SymbolRegistry.from_directory(ROOT / "assets/symbols")
    catalogo = ComponentRegistry.from_directory(ROOT / "examples/layout/catalog", symbols=simboli)
    cartiglio = Cartiglio.da_file(ROOT / "assets/cartigli/Cartiglio_NoveC_A3.json")
    uscita = Path(sys.argv[1])
    for nome, impianto, grafo, piano, dati in collaudo.tavole():
        modello = collaudo.con_i_dati(grafo, impianto, dati)
        _, _, svg, _ = collaudo.esegui(nome, modello, piano, simboli, catalogo, cartiglio, uscita)
        print(nome, svg)


if __name__ == "__main__":
    main()
