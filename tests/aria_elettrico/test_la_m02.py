"""L'accettazione della fase 2 di REL-012: la M.02 del kit aria-aria rifatta dalla skill.

La strada e' quella di un agente: il grafo dell'esempio AA-01
(`docs/collaudi/REL-012/fase-2/grafo.json`) -> `valida` -> `completa` -> `distinta` ->
`disegna --tabelle` col piano del kit (`piano.json`), le tabelle della distinta e le note
di progetto. La tavola esce **senza rilievi bloccanti e senza tratte cedute**, con quello
che la M.02 del kit porta: le scritte Ø·L di ogni tratto, la tabella delle apparecchiature,
la tabella delle tratte, le note, le attivita' e il computo.
"""

import contextlib
import io
import json
import re
from pathlib import Path

import pytest

from disegnatore_mep.skill import Cartelle, cartelle_del_repository, main

ROOT = Path(__file__).resolve().parents[2]
FASE_2 = ROOT / "docs" / "collaudi" / "REL-012" / "fase-2"


@pytest.fixture(scope="module")
def la_m02(tmp_path_factory: pytest.TempPathFactory) -> tuple[str, str, str]:
    cartelle: Cartelle = cartelle_del_repository(ROOT)
    lavoro = tmp_path_factory.mktemp("m02")
    completo = lavoro / "grafo-completo.json"
    assert main(["valida", str(FASE_2 / "grafo.json")], cartelle) == 0
    assert main(["completa", str(FASE_2 / "grafo.json"), "--out", str(completo)], cartelle) == 0
    assert main(["distinta", str(completo), "--out", str(lavoro / "distinta")], cartelle) == 0
    uscita = io.StringIO()
    with contextlib.redirect_stdout(uscita):
        codice = main(
            [
                "disegna", str(completo), "--piano", str(FASE_2 / "piano.json"), "--out", str(lavoro / "tavola"),
                "--tabelle", str(lavoro / "distinta" / "tabelle-del-foglio.json"),
                "--tabelle", str(FASE_2 / "note-di-progetto.json"), "--senza-dxf",
            ],
            cartelle,
        )
    assert codice == 0, uscita.getvalue()
    svg = (lavoro / "tavola" / "caso-prova-aria-aria-t1.svg").read_text(encoding="utf-8")
    rilievi = (lavoro / "tavola" / "caso-prova-aria-aria-t1-rilievi.md").read_text(encoding="utf-8")
    return uscita.getvalue(), svg, rilievi


def test_la_m02_esce_pulita(la_m02: tuple[str, str, str]) -> None:
    uscita, _, rilievi = la_m02
    assert "tratte cedute 0 · rilievi bloccanti 0" in uscita
    assert "Formato **A1** · tratte **20** · tratte cedute **0** · rilievi bloccanti **0**" in rilievi
    assert "## Le regole del piano\n\n- nessuna violazione" in rilievi


def test_ogni_tratto_porta_la_sua_scritta(la_m02: tuple[str, str, str]) -> None:
    _, svg, _ = la_m02
    grafo = json.loads((FASE_2 / "grafo.json").read_text(encoding="utf-8"))
    scritte = [t["scritta"] for t in grafo["connections"] if t.get("scritta")]
    assert len(scritte) == 18
    for scritta in scritte:
        assert scritta.replace('"', "&quot;") in svg or scritta in svg, scritta


def test_le_tabelle_del_kit_ci_sono_tutte(la_m02: tuple[str, str, str]) -> None:
    uscita, svg, _ = la_m02
    for titolo in (
        "TABELLA DELLE TRATTE",
        "COMPUTO DELLE QUANTIT",
        "G. ATTIVIT",
        "NOTE DELLA DISTINTA",
        "NOTE DI PROGETTO",
    ):
        assert titolo in svg, titolo
    assert svg.count('class="tabella-nelle-zone"') >= 5
    for tratto in range(1, 19):
        assert f">T{tratto:02d}<" in svg
    for voce in ("A.1", "B.11", "C.11", "D.9", "E.13", "F.7", "Z.7", "G.12"):
        assert f">{voce}<" in svg, voce
    assert re.search(r"«tratte» a destra.*\n.*«attivita» a destra.*\n.*«note» a destra", uscita)
    assert "«computo» in basso" in uscita and "«note-di-progetto» in basso" in uscita
    for sigla in ("UE-01", "UI-01", "PLZ-01", "CZ-01", "CF-01"):
        assert f">{sigla}<" in svg
