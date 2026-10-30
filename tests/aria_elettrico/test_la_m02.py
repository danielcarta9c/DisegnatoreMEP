"""L'accettazione della fase 2 di REL-012: la M.02 del kit aria-aria rifatta dalla skill.

La strada e' quella di un agente: il grafo dell'esempio AA-01
(`docs/collaudi/REL-012/fase-2/grafo.json`) -> `valida` -> `completa` -> `disegna` col piano
del kit (`piano.json`); la distinta e' un documento a parte. La tavola esce **senza rilievi
bloccanti e senza tratte cedute**, con le scritte Ø·L di ogni tratto, la tabella delle
apparecchiature e la legenda.

**In A3** (REL-015, I-233): «Manteniamo in tavola solo la tabella con le sigle delle
macchine/accessori e la legenda» — tratte, note, attivita' e computo stanno nel PDF della
distinta. Prima la M.02 usciva in A1, per il computo sul foglio.
"""

import contextlib
import io
import json
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
    uscita = io.StringIO()
    with contextlib.redirect_stdout(uscita):
        codice = main(
            ["disegna", str(completo), "--piano", str(FASE_2 / "piano.json"), "--out", str(lavoro / "tavola"), "--senza-dxf"],
            cartelle,
        )
    assert codice == 0, uscita.getvalue()
    svg = (lavoro / "tavola" / "caso-prova-aria-aria-t1.svg").read_text(encoding="utf-8")
    rilievi = (lavoro / "tavola" / "caso-prova-aria-aria-t1-rilievi.md").read_text(encoding="utf-8")
    return uscita.getvalue(), svg, rilievi


def test_la_m02_esce_pulita_in_a3(la_m02: tuple[str, str, str]) -> None:
    uscita, _, rilievi = la_m02
    assert "Formato A3 · tratte 20 · tratte cedute 0 · rilievi bloccanti 0" in uscita
    assert "Formato **A3** · tratte **20** · tratte cedute **0** · rilievi bloccanti **0**" in rilievi
    assert "## Le regole del piano\n\n- nessuna violazione" in rilievi


def test_il_piano_non_riserva_zone_per_le_tabelle() -> None:
    piano = json.loads((FASE_2 / "piano.json").read_text(encoding="utf-8"))
    assert piano["formato"] == "A3" and "zone_tabelle" not in piano
    rifai = (FASE_2 / "rifai.sh").read_text(encoding="utf-8")
    assert "--tabelle" not in rifai


def test_ogni_tratto_porta_la_sua_scritta(la_m02: tuple[str, str, str]) -> None:
    _, svg, _ = la_m02
    grafo = json.loads((FASE_2 / "grafo.json").read_text(encoding="utf-8"))
    scritte = [t["scritta"] for t in grafo["connections"] if t.get("scritta")]
    assert len(scritte) == 18
    for scritta in scritte:
        assert scritta.replace('"', "&quot;") in svg or scritta in svg, scritta


def test_sulla_tavola_solo_apparecchiature_e_legenda(la_m02: tuple[str, str, str]) -> None:
    _, svg, _ = la_m02
    assert 'class="tabella-nelle-zone"' not in svg
    for titolo in ("TABELLA DELLE TRATTE", "COMPUTO DELLE QUANTIT", "G. ATTIVIT", "NOTE DELLA DISTINTA", "NOTE DI PROGETTO"):
        assert titolo not in svg, titolo
    for intestazione in ("CODICE", "DESCRIZIONE", "MARCA", "MODELLO"):
        assert f">{intestazione}<" in svg, intestazione
    for sigla in ("UE-01", "UI-01", "PLZ-01", "CZ-01", "CF-01", "TZ-01"):
        assert f">{sigla}<" in svg, sigla
    assert ">Refrigerante liquido<" in svg and ">Aria di mandata<" in svg, "la legenda"


def test_lo_schema_del_collaudo_t3_esce_in_a3(tmp_path: Path) -> None:
    """Lo schema del collaudo T3 di REL-012, rifatto (`collaudo-t3/rifatto/`): in A3, senza
    tabelle della distinta. Con la posa del collaudo la scritta di TA-03 non trovava posto
    contro la legenda; il piano rifatto la sposta e lo dice nelle note."""
    t3 = ROOT / "docs" / "collaudi" / "REL-012" / "collaudo-t3"
    piano = json.loads((t3 / "rifatto" / "piano.json").read_text(encoding="utf-8"))
    assert piano["formato"] == "A3" and "zone_tabelle" not in piano
    uscita = io.StringIO()
    with contextlib.redirect_stdout(uscita):
        codice = main(
            ["disegna", str(t3 / "grafo-completo.json"), "--piano", str(t3 / "rifatto" / "piano.json"),
             "--out", str(tmp_path), "--senza-dxf"],
            cartelle_del_repository(ROOT),
        )
    assert codice == 0, uscita.getvalue()
    assert "Formato A3 · tratte 18 · tratte cedute 0 · rilievi bloccanti 0 · pieghe 4" in uscita.getvalue()
    svg = (tmp_path / "canalizzato-appartamento-secondo-piano-t1.svg").read_text(encoding="utf-8")
    assert "Soggiorno (sopra il varco)" in svg and 'class="tabella-nelle-zone"' not in svg
    assert "--tabelle" not in (t3 / "rifatto" / "rifai.sh").read_text(encoding="utf-8")
