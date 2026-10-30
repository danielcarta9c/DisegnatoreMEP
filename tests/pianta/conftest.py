"""I casi di prova della pianta, disegnati una volta per modulo: ogni giro scrive
PDF, DXF e PNG, e tre secondi a prova sarebbero troppi."""

from pathlib import Path

import pytest

from disegnatore_mep.graphics.cartiglio import Cartiglio
from disegnatore_mep.pianta.comando import Esito, disegna_la_pianta

RADICE = Path(__file__).resolve().parents[2]
ESEMPI = RADICE / "examples" / "pianta"
APPARTAMENTO = ESEMPI / "appartamento-aria-aria.json"
CASI = {
    "appartamento": APPARTAMENTO,
    "corridoio": ESEMPI / "casi" / "corridoio.json",
    "incrocio": ESEMPI / "casi" / "incrocio.json",
    "muro": ESEMPI / "casi" / "muro-senza-aperture.json",
    "collaudo": ESEMPI / "casi" / "collaudo-t1.json",
    "collaudo-t3": ESEMPI / "casi" / "collaudo-t3.json",
}
"""`collaudo` e' la pianta del collaudo indipendente REL-012 (t1): una planimetria
inventata, data a parole, con le lunghezze del progettista sui tracciati.
`collaudo-t3` e' quella del terzo collaudo (sulla 1.6.0), con le posizioni vere del
testo: la centrale sopra il plenum, la ripresa sotto la UI, il terrazzo solo davanti
al soggiorno; si disegna con la distinta e il grafo del collaudo accanto."""

CONFRONTI = {
    "collaudo-t3": (
        ESEMPI / "casi" / "collaudo-t3.distinta.json",
        ESEMPI / "casi" / "collaudo-t3.grafo-completo.json",
    ),
}
"""I casi che si disegnano con `--distinta` e `--grafo`."""
CATALOGO = RADICE / "examples" / "layout" / "catalog"
NOMI = RADICE / "naming"
CARTIGLIO = RADICE / "assets" / "cartigli" / "Cartiglio_NoveC_A3.json"


@pytest.fixture(scope="session")
def esiti(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Esito]:
    cartiglio = Cartiglio.da_file(CARTIGLIO)
    out: dict[str, Esito] = {}
    for nome, percorso in CASI.items():
        cartella = tmp_path_factory.mktemp(f"pianta-{nome}")
        distinta, grafo = CONFRONTI.get(nome, (None, None))
        out[nome] = disegna_la_pianta(
            percorso, cartella, cartiglio, png=(nome in ("appartamento", "collaudo")),
            distinta=distinta, grafo=grafo, catalogo=CATALOGO, nomi=NOMI,
        )
    return out
