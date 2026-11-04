"""La lista della spesa per l'installatore (I-262, I-264): stessi calcoli della distinta,
un documento piu' semplice — solo i materiali da comprare, niente offerta a corpo."""

import json
from pathlib import Path

import pytest

from disegnatore_mep.distinta import Distinta, RegoleDellaDistinta, componi_la_distinta
from disegnatore_mep.distinta.documento import Tabella, documento_della_lista, tutti_i_testi
from disegnatore_mep.skill import cartelle_del_repository, main

from .conftest import AA01, ROOT, sigle


@pytest.fixture(scope="module")
def aa01(regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]) -> Distinta:
    grafo = json.loads(AA01.read_text(encoding="utf-8"))
    return componi_la_distinta(grafo, regole, *nomi, sigle(grafo))


def test_tre_capitoli_e_solo_quello_che_si_compra(aa01: Distinta) -> None:
    documento = documento_della_lista(aa01)
    assert [c.titolo for c in documento.capitoli] == [
        "L'impianto",
        "Le tratte: sezioni e lunghezze",
        "La lista dei materiali",
    ]
    tabelle = [b for b in documento.capitoli[2].blocchi if isinstance(b, Tabella)]
    lettere = [t.titolo[0] for t in tabelle]
    assert "F" not in lettere and "Z" not in lettere
    assert lettere[0] == "A"
    righe = [r for t in tabelle[1:] for r in t.righe]
    assert righe and all(r[2].strip().lower() != "a corpo" for r in righe)


def test_stessi_numeri_della_distinta(aa01: Distinta) -> None:
    """La lista non ricalcola: ogni riga e' una voce della distinta, con la stessa quantita'."""
    documento = documento_della_lista(aa01)
    per_rif = {v.rif: v for v in aa01.voci}
    for tabella in (b for b in documento.capitoli[2].blocchi if isinstance(b, Tabella)):
        for riga in tabella.righe:
            assert riga[1] == per_rif[riga[0]].testo.replace("`", "")


def test_niente_linguaggio_dell_offerta(aa01: Distinta) -> None:
    testi = " ".join(tutti_i_testi(documento_della_lista(aa01))).lower()
    assert "a corpo" not in testi and "fisso e invariabile" not in testi and "offerta" not in testi


def test_il_comando(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["distinta", str(AA01), "--out", str(tmp_path), "--lista"], cartelle_del_repository(ROOT)) == 0
    capsys.readouterr()
    nomi = sorted(p.name for p in tmp_path.iterdir())
    assert "AA-01_Lista_materiali_Climatizzazione_canalizzata_Daikin.md" in nomi
    testo = (tmp_path / "AA-01_Lista_materiali_Climatizzazione_canalizzata_Daikin.md").read_text(encoding="utf-8")
    assert "Lista materiali per l'installatore" in testo
