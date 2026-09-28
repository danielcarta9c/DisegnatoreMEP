"""La geometria delle sei tavole approvate com'e' su `main`, prima della tabella.

Si lancia **con il codice di `main`**, da un albero di lavoro separato, e scrive la
geometria di ciascuna tavola (`--geometry` della CLI) in una cartella: il collaudo di
REL-006 la confronta con quella di oggi, per dire se il disegno si e' spostato.

    git worktree add --detach <albero> origin/main
    PYTHONPATH=<albero>/src python3 docs/collaudi/REL-006/geometria_di_main.py <albero> <cartella>
"""

import sys
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.piano.esecutore import esegui_piano
from disegnatore_mep.piano.formato import carica_piano


def main() -> None:
    albero, uscita = Path(sys.argv[1]), Path(sys.argv[2])
    uscita.mkdir(parents=True, exist_ok=True)
    approvati = albero / "docs" / "collaudi" / "DRAW-018" / "prova-camera-pulita-2026-09-24"
    impianto_6 = albero / "docs" / "collaudi" / "REL-003" / "impianto-6"
    elenco = [
        (f"tavola-{n}", approvati / f"grafo-completo-{n}.json", approvati / f"piano-completo-{n}.json")
        for n in ("1", "2", "3", "4", "5")
    ]
    elenco.append(("tavola-6", impianto_6 / "grafo-completo-6.json", impianto_6 / "piano-6-a.json"))
    simboli = SymbolRegistry.from_directory(albero / "assets" / "symbols")
    catalogo = ComponentRegistry.from_directory(albero / "examples" / "layout" / "catalog", symbols=simboli)
    for nome, grafo, piano in elenco:
        esito = esegui_piano(load_project(grafo), carica_piano(piano), catalogo, simboli, albero / "naming")
        if esito.disegno is None:
            raise SystemExit(f"{nome}: {esito.errore}")
        (uscita / f"{nome}.json").write_text(esito.disegno.model_dump_json(indent=1), encoding="utf-8")
        print(nome, "scritta")


if __name__ == "__main__":
    main()
