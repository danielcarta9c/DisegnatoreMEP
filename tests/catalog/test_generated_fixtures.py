"""I generatori delle fixture riproducono cio' che e' committato.

Il difetto che questa prova rende impossibile e' successo due volte. La prima:
rigenerare il catalogo cambiava in silenzio il fluido di una porta del
bollitore. La seconda, il 6 agosto 2026: la correzione dello scarico ha
aggiunto a mano `stored_medium` ai due serbatoi **senza toccare il generatore
che li genera**, e da quel momento rieseguire il generatore cancellava il
campo, spegnendo l'intera catena — regole, grafo, documento e quasi tutte le
prove — con un errore di caricamento.

Nessuna prova presidiava il giro completo, e il difetto e' rimasto invisibile
finche' non l'ha trovato un collaudo indipendente. Ora si vede subito: chi
modifica a mano un file generato fa fallire questa prova, che gli dice quale
file e perche'.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

GENERATORS: list[tuple[str, str]] = [
    ("examples/layout/build_layout_fixtures.py", "examples/layout/catalog"),
    ("examples/foundation/build_fixtures.py", "examples/foundation/catalog"),
    # La libreria dei simboli: tre segni erano stati corretti a mano — i due
    # raccordi (D-119) e il ritegno (D-122) — e il generatore li avrebbe
    # riportati indietro alla prima rigenerazione. DRAW-005 li ha portati nel
    # generatore, e da qui la libreria pubblicata e' la sua rigenerazione.
    ("examples/graphics/build_symbols.py", "assets/symbols"),
]


def snapshot(directory: Path) -> dict[str, object]:
    """Il contenuto della cartella, letto come dati e non come testo.

    Confrontare i dati e non i byte tiene la prova sul punto che conta — cosa
    dichiara il catalogo — invece di farla fallire per un a capo. I corpi SVG
    dei simboli si confrontano come testo, senza gli a capo ai bordi.
    """
    found: dict[str, object] = {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(directory.glob("*.json"))
    }
    found.update(
        {path.name: path.read_text(encoding="utf-8").strip() for path in sorted(directory.glob("*.svg"))}
    )
    return found


@pytest.mark.parametrize(("script", "catalog"), GENERATORS)
def test_the_generator_reproduces_what_is_committed(script: str, catalog: str) -> None:
    generator, directory = ROOT / script, ROOT / catalog
    if not generator.exists() or not directory.exists():
        pytest.skip(f"{script} non c'e' piu'")
    before = snapshot(directory)
    assert before, f"{catalog} e' vuoto: la prova non direbbe nulla"

    subprocess.run(  # noqa: S603
        [sys.executable, str(generator)], cwd=ROOT, check=True, capture_output=True
    )
    after = snapshot(directory)

    missing = sorted(set(before) - set(after))
    added = sorted(set(after) - set(before))
    changed = sorted(name for name in before.keys() & after.keys() if before[name] != after[name])
    assert not (missing or added or changed), (
        f"rieseguire {script} cambia il catalogo committato — "
        f"spariti: {missing}; comparsi: {added}; diversi: {changed}. "
        "Un file generato non si modifica a mano: si modifica il generatore."
    )
