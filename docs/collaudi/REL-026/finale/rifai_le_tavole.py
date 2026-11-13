"""La tavola del blocco B che il blocco C ha cambiato ancora, rifatta col codice finale.

    .venv/bin/python docs/collaudi/REL-026/finale/rifai_le_tavole.py

Le cartelle `blocco-b/` sono la fotografia del blocco B quando e' stato consegnato (i dettagli
si aprivano ancora da soli); le cartelle `blocco-c-*/` sono gia' rifatte col codice unito. Qui
sta il solo caso di B-5 — il T3 con 49 discordanze, disegnato con distinta e grafo — com'e'
alla fine del pacchetto: da mettere accanto a `blocco-b/discordanze/prima/`.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

QUI = Path(__file__).resolve().parent
RADICE = QUI.parents[3]
sys.path.insert(0, str(RADICE / "src"))

spec = importlib.util.spec_from_file_location("blocco_b", QUI.parent / "blocco-b" / "rifai_le_tavole.py")
assert spec is not None and spec.loader is not None
blocco_b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(blocco_b)


def principale() -> int:
    with tempfile.TemporaryDirectory() as temporanea:
        sorgente = blocco_b._variante(blocco_b.CASI / "collaudo-t3.json",
                                      Path(temporanea) / "discordanze.json", blocco_b.discordante)
        distinta = blocco_b.CASI / "collaudo-t3.distinta.json"
        grafo = blocco_b.CASI / "collaudo-t3.grafo-completo.json"
        misura = blocco_b.dopo(sorgente, QUI / "discordanze", distinta=distinta, grafo=grafo)
    riga = f"discordanze, codice finale, distinta e grafo (formato, scala, avvisi in tavola, avvisi del confronto): {misura}"
    (QUI / "misure.txt").write_text(riga + "\n", encoding="utf-8")
    print(riga)
    return 0


if __name__ == "__main__":
    sys.exit(principale())
