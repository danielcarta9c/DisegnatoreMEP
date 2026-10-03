"""I simboli nuovi del primo caso reale, disegnati (REL-009, I-194).

La tavola di prova `docs/collaudi/REL-009/simboli-nuovi/` mette in un impianto piccolo
il contatore di calore, l'attacco predisposto con la sua scritta, il volano a sei
attacchi, il collettore con mandata e ritorno e i confini con l'impianto esistente. Si
disegna dal suo grafo e dal suo piano, col comando della skill, e deve uscire: zero
tratte cedute, zero bloccanti, e le scritte del progettista scritte.
"""

# categoria: difende il prodotto — I-194, le voci nuove si disegnano e le scritte libere non si perdono

from pathlib import Path

import pytest

from disegnatore_mep.skill import cartelle_del_repository, main

ROOT = Path(__file__).resolve().parents[2]
PROVA = ROOT / "docs" / "collaudi" / "REL-009" / "simboli-nuovi"


@pytest.fixture(scope="module")
def tavola(tmp_path_factory: pytest.TempPathFactory) -> Path:
    cartelle = cartelle_del_repository(ROOT)
    uscita = tmp_path_factory.mktemp("simboli")
    assert main(["completa", str(PROVA / "grafo.json"), "--out", str(uscita / "completo.json")], cartelle) == 0
    codice = main(
        ["disegna", str(uscita / "completo.json"), "--piano", str(PROVA / "piano.json"), "--out", str(uscita / "t")],
        cartelle,
    )
    assert codice == 0, "la tavola dei simboli nuovi si consegna"
    return uscita / "t"


def test_la_tavola_dei_simboli_nuovi_esce_senza_bloccanti(tavola: Path) -> None:
    rilievi = next(tavola.glob("*-rilievi.md")).read_text(encoding="utf-8")
    assert "tratte cedute **0**" in rilievi and "rilievi bloccanti **0**" in rilievi


def test_i_simboli_nuovi_ci_sono_e_le_scritte_sono_scritte(tavola: Path) -> None:
    svg = next(tavola.glob("*.svg")).read_text(encoding="utf-8")
    for simbolo in ("heat-meter", "capped-connection", "buffer-six-port", "zone-manifold-pair"):
        assert simbolo in svg, simbolo
    for scritta in ("al solare termico", "verso impianto esistente", "da impianto esistente"):
        assert scritta in svg, scritta
