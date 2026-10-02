"""Il solutore e' fuori dalla catena, e si vede (**D-151**, `DRAW-015` §4).

# categoria: difende una regola del piano — D-151, il disegno lo compone un agente

Non e' una prova di comportamento: e' la prova che **un file morto resta morto**.
Fino al 20 settembre 2026 la posa la decidevano `layout/improve.py` (il ciclo di
miglioramento) e la fase del tronco di `layout/spine.py`; `layout/dilate.py`
inseguiva il riempimento. D-151 e D-149 li hanno tolti dalla decisione; il
2 ottobre 2026, col via libera del PO (I-180), il codice e' stato tolto, e resta
nella storia di git.

Il rischio che questa prova chiude e' preciso, e ha un precedente: un file che
nessuno chiama e non lo dichiara e' una trappola — e' cosi' che la ricerca del
4 agosto e' rimasta inattuata per sei settimane. Qui si sorveglia il contrario:
che nessuno **ricominci** a chiamarli senza accorgersene.
"""

import subprocess
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]

MORTI = ("disegnatore_mep.layout.improve", "disegnatore_mep.layout.dilate")
"""I due moduli del solutore, tolti il 2 ottobre 2026 (I-180): nessun percorso deve
importarli, nemmeno se qualcuno li riportasse."""


def _moduli_dopo(codice: str) -> set[str]:
    """Quali moduli di `disegnatore_mep` risultano importati dopo questo codice.

    Si misura in un **processo nuovo**: dentro la suite `sys.modules` porta gia'
    mezzo progetto, importato da altre prove, e la misura non direbbe niente.
    """
    esito = subprocess.run(
        [sys.executable, "-c", codice + "\nimport sys, json\n"
         "print(json.dumps(sorted(n for n in sys.modules if n.startswith('disegnatore_mep'))))"],
        capture_output=True,
        text=True,
        cwd=RADICE,
        check=True,
    )
    import json

    return set(json.loads(esito.stdout.strip().splitlines()[-1]))


def test_la_via_ordinaria_non_importa_piu_il_solutore() -> None:
    """`compose_on_ordinary_frame` — il comando `draw` — non lo tira dentro."""
    visti = _moduli_dopo("from disegnatore_mep.layout.compose import compose_on_ordinary_frame")
    assert not (visti & set(MORTI)), sorted(visti & set(MORTI))


def test_la_via_del_piano_non_importa_il_solutore() -> None:
    """`esegui_piano` e `revisiona` — i comandi `piano` e `revisiona`."""
    visti = _moduli_dopo(
        "from disegnatore_mep.piano.esecutore import esegui_piano\n"
        "from disegnatore_mep.piano.revisore import revisiona"
    )
    assert not (visti & set(MORTI)), sorted(visti & set(MORTI))


def test_la_cli_intera_non_importa_il_solutore() -> None:
    """La CLI e' la somma dei suoi comandi: se uno lo tira dentro, si vede qui."""
    visti = _moduli_dopo("import disegnatore_mep.cli")
    assert not (visti & set(MORTI)), sorted(visti & set(MORTI))


def test_la_composizione_non_chiama_piu_la_fase_del_tronco() -> None:
    """`spine.py` vive per `carry_the_rest`, non per `lay_the_spine`.

    Il modulo non si puo' misurare con gli import — `compose.py` non lo importa
    piu' affatto, e la semina la usa il piano — quindi si misura sul testo, che
    e' il documento agli atti.
    """
    sorgente = (RADICE / "src/disegnatore_mep/layout/compose.py").read_text(encoding="utf-8")
    assert "lay_the_spine" not in sorgente
    assert "improve_sheet" not in sorgente


def test_i_moduli_del_solutore_non_ci_sono_piu() -> None:
    """Il 2 ottobre 2026, col via libera del PO (I-180), il solutore e' stato tolto:
    `improve.py` e `dilate.py` non esistono piu', e di `spine.py` resta la semina.

    Fino ad allora questa prova sorvegliava che i tre moduli **dichiarassero** di
    essere morti, perche' un file morto che non lo dice e' una trappola. Tolti, la
    trappola non c'e' piu'; resta da sorvegliare che non tornino, e che `spine.py`
    dica che cosa ospitava e dove e' finito: la storia di git.
    """
    layout = RADICE / "src/disegnatore_mep/layout"
    assert not (layout / "improve.py").exists()
    assert not (layout / "dilate.py").exists()
    spine = (layout / "spine.py").read_text(encoding="utf-8")
    assert "def lay_the_spine" not in spine
    testa = " ".join(spine[:1600].split())
    assert "D-151" in testa and "I-180" in testa and "storia di git" in testa
