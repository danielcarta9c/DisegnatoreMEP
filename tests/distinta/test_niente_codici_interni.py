"""Il documento della distinta non porta codici interni (collaudo indipendente della 1.7.0).

La distinta va all'installatore. Il collaudo dello ZIP 1.7.0 ha trovato nel PDF «(D-190)»
sei volte, nelle domande su marca e modello, e l'impronta delle regole («regole
05a61bb20ef686d8») nelle avvertenze: sono codici del repository, che chi legge non conosce.
L'impronta resta nei file per chi la controlla (`distinta.json`, `distinta-calcoli.md`).
"""
# categoria: difende il prodotto

import contextlib
import io
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
T3 = ROOT / "docs" / "collaudi" / "REL-012" / "collaudo-t3"


def test_il_documento_non_porta_decisioni_input_ne_impronte(tmp_path: Path) -> None:
    from disegnatore_mep.skill import cartelle_del_repository, main

    with contextlib.redirect_stdout(io.StringIO()):
        main(
            ["distinta", str(T3 / "grafo-completo.json"), "--out", str(tmp_path), "--regole", str(ROOT / "rules" / "distinta")],
            cartelle_del_repository(ROOT),
        )
    documento = next(item for item in tmp_path.glob("Distinta_materiali_*.md"))
    testo = documento.read_text(encoding="utf-8")
    assert "marca e modello" in testo
    assert not re.findall(r"\b[DI]-\d{3}\b", testo)
    assert not re.findall(r"\b[0-9a-f]{16}\b", testo)
    assert "da' il" not in testo
