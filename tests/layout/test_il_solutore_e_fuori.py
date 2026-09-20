"""Il solutore e' fuori dalla catena, e si vede (**D-151**, `DRAW-015` §4).

# categoria: difende una regola del piano — D-151, il disegno lo compone un agente

Non e' una prova di comportamento: e' la prova che **un file morto resta morto**.
Fino al 20 settembre 2026 la posa la decidevano `layout/improve.py` (il ciclo di
miglioramento) e la fase del tronco di `layout/spine.py`; `layout/dilate.py`
inseguiva il riempimento. D-151 e D-149 li hanno tolti dalla decisione, e i tre
moduli **restano agli atti**.

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
"""I due moduli che il percorso vigente non deve piu' nemmeno importare."""


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


def test_i_tre_moduli_dichiarano_di_essere_morti() -> None:
    """La dichiarazione in testa **e'** il contratto: senza, sono una trappola."""
    for nome in ("improve", "spine", "dilate"):
        # Gli a capo si tolgono: la dichiarazione e' prosa, e una frase che va
        # a capo in mezzo e' la stessa frase.
        testa = " ".join(
            (RADICE / f"src/disegnatore_mep/layout/{nome}.py")
            .read_text(encoding="utf-8")[:1400]
            .split()
        )
        # Le tre cose che il pacchetto chiede a una riga di morte: **quando**,
        # **perche'** (la decisione), e **dove e' finito il suo lavoro**. Senza
        # la terza, la dichiarazione dice che il file e' morto e non dice a chi
        # rivolgersi: e' meta' trappola.
        assert "2026" in testa, nome
        assert "D-15" in testa or "D-149" in testa, nome
        assert "Dove e' finito il suo lavoro" in testa, nome
