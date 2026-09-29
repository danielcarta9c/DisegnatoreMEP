#!/usr/bin/env python3
"""Il comando della skill Disegnatore MEP.

    python3 scripts/mep.py <comando> [...]

Comandi: ambiente, catalogo, valida, completa, disegna, anteprima, consegna.
`python3 scripts/mep.py <comando> --help` dice che cosa vuole ciascuno.

Il motore sta qui accanto, in `disegnatore_mep/`, ed e' la copia di quello del
repository che ha costruito questa cartella. Ha bisogno di una libreria sola che la
libreria standard non ha, pydantic: se l'ambiente non ce l'ha, il comando prova a
installarla, e se non ci riesce lo dice.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
RADICE = QUI.parent

PYDANTIC = "pydantic==2.13.4"
"""La versione con cui il motore e' provato: quella del `pyproject.toml` del repository."""

FACOLTATIVE: dict[str, dict[str, str]] = {
    "ambiente": {"ezdxf": "ezdxf==1.4.4", "pypdfium2": "pypdfium2==5.13.0"},
    "disegna": {"ezdxf": "ezdxf==1.4.4"},
    "anteprima": {"pypdfium2": "pypdfium2==5.13.0"},
}
"""Le librerie senza le quali un comando fa meno, non niente: il DXF vuole ezdxf, la
versione del `pyproject.toml`; l'anteprima un lettore di PDF, e pypdfium2 5.13.0 e'
quello provato con la skill il 29 settembre 2026. Se mancano si prova a installarle;
se non si riesce, il comando lavora senza e lo dice."""

ATTESA_PIP_S = 180
"""Quanto si aspetta l'installazione: pydantic e le sue tre dipendenze sono pochi
megabyte, e tre minuti bastano anche su una rete lenta."""


def _installa(modulo: str, pacchetto: str, perche: str) -> bool:
    print(f"Manca la libreria {modulo}, {perche}: provo a installare {pacchetto}.", file=sys.stderr)
    riuscita = _pip(pacchetto)
    if riuscita:
        print(f"Installata: {pacchetto}.", file=sys.stderr)
    return riuscita and importlib.util.find_spec(modulo) is not None


def _pip(pacchetto: str) -> bool:
    try:
        esito = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", pacchetto],
            capture_output=True,
            text=True,
            timeout=ATTESA_PIP_S,
        )
    except (OSError, subprocess.TimeoutExpired) as errore:
        print(f"L'installazione non e' riuscita: {errore}", file=sys.stderr)
        return False
    if esito.returncode != 0:
        ultima = (esito.stderr or esito.stdout).strip().splitlines()[-1:] or ["?"]
        print(f"L'installazione non e' riuscita: {ultima[0]}", file=sys.stderr)
        return False
    importlib.invalidate_caches()
    return True


def main() -> int:
    # La cartella della skill puo' essere di sola lettura: niente file compilati accanto.
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(QUI))
    if importlib.util.find_spec("pydantic") is None and not _installa(
        "pydantic", PYDANTIC, "che il motore usa"
    ):
        print(
            "Senza pydantic il comando non parte. Serve un ambiente con Python 3.11 o piu' "
            f"e la libreria {PYDANTIC}, oppure la rete per installarla.",
            file=sys.stderr,
        )
        return 1
    import pydantic

    if int(pydantic.VERSION.split(".")[0]) < 2:
        print(
            f"C'e' pydantic {pydantic.VERSION}, e il motore vuole la versione 2: "
            f"python3 -m pip install {PYDANTIC}",
            file=sys.stderr,
        )
        return 1

    comando_chiesto = next((a for a in sys.argv[1:] if not a.startswith("-")), "")
    chiede_aiuto = any(a in ("-h", "--help") for a in sys.argv[1:])
    for modulo, pacchetto in ({} if chiede_aiuto else FACOLTATIVE.get(comando_chiesto, {})).items():
        if importlib.util.find_spec(modulo) is None:
            _installa(modulo, pacchetto, "senza la quale il comando fa meno")

    import grafo_leggibile
    from disegnatore_mep.skill import cartelle_della_skill
    from disegnatore_mep.skill import main as comando

    return comando(sys.argv[1:], cartelle_della_skill(RADICE), grafo_leggibile.build)


if __name__ == "__main__":
    raise SystemExit(main())
