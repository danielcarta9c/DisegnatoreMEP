"""La tavola della pianta: le scritte, il determinismo, le lunghezze, le uscite."""

import json
from pathlib import Path

import pytest

from disegnatore_mep.cli import main as cli
from disegnatore_mep.graphics.cartiglio import Cartiglio
from disegnatore_mep.layout.legend import MEDIUM_STYLES
from disegnatore_mep.pianta.comando import Esito, disegna_la_pianta
from disegnatore_mep.pianta.lunghezze import da_quotare, metri
from disegnatore_mep.pianta.modello import (
    ErroreDellaPianta,
    Fluido,
    Maggiorazione,
    carica_pianta,
    schema_della_pianta,
)
from disegnatore_mep.pianta.tavola import stile
from disegnatore_mep.skill import cartelle_del_repository
from disegnatore_mep.skill import main as skill

from .conftest import APPARTAMENTO, CARTIGLIO, CASI, RADICE


@pytest.mark.parametrize("nome", sorted(CASI))
def test_le_scritte_non_toccano_linee_ne_altre_scritte(esiti: dict[str, Esito], nome: str) -> None:
    rilievi = esiti[nome].rilievi
    assert rilievi.scritte_su_linee == []
    assert rilievi.scritte_su_scritte == []
    assert all(posata.libera for _, posata in esiti[nome].tavola.scritte)


@pytest.mark.parametrize("nome", sorted(CASI))
def test_nessun_rilievo_bloccante(esiti: dict[str, Esito], nome: str) -> None:
    assert esiti[nome].rilievi.bloccanti == []


def test_ogni_tratta_ha_la_sua_scritta(esiti: dict[str, Esito]) -> None:
    """«T03 · Ø200 · L 7,5 m»; un fascio fra le stesse macchine ne ha una sola."""
    esito = esiti["appartamento"]
    testi = [s.testo for chi, s in esito.tavola.scritte if chi.startswith(("tratta", "fascio"))]
    assert "T07–T09 · L 12 m" in testi
    lunghe = {lu.tratta: lu for lu in esito.lunghezze}
    assert f"T03 · Ø200 · L {metri(lunghe['T03'].da_quotare_m)} m" in testi
    prime = {testo.split(" ")[0] for testo in testi}
    attese = {t.tratta for t in esito.pianta.tracciati if t.fascio is None} | {"T07–T09"}
    assert prime == attese


def test_la_tavola_esce_su_a3_a_1_50_con_tutti_i_file(esiti: dict[str, Esito]) -> None:
    esito = esiti["appartamento"]
    assert (esito.tavola.formato, esito.tavola.scala) == ("A3", 50)
    assert esito.tavola.avvisi == []
    suffissi = {p.suffix for p in esito.file}
    assert {".svg", ".pdf", ".dxf", ".png", ".json", ".jpg"} <= suffissi
    svg = next(p for p in esito.file if p.suffix == ".svg").read_text(encoding="utf-8")
    assert "Percorsi indicativi, da verificare in sopralluogo." in svg
    assert "Scala 1:50" in svg
    assert "M.03" in svg


def test_colori_e_tratti_sono_quelli_dello_schema() -> None:
    for fluido, valore in MEDIUM_STYLES.items():
        assert stile(fluido) == valore


def test_stesso_ingresso_stessa_tavola(tmp_path: Path, esiti: dict[str, Esito]) -> None:
    cartiglio = Cartiglio.da_file(CARTIGLIO)
    di_nuovo = disegna_la_pianta(APPARTAMENTO, tmp_path, cartiglio, png=False)
    for suffisso in (".svg", ".dxf"):
        prima = next(p for p in esiti["appartamento"].file if p.suffix == suffisso)
        dopo = next(p for p in di_nuovo.file if p.suffix == suffisso)
        assert prima.read_bytes() == dopo.read_bytes(), suffisso
    prima = next(p for p in esiti["appartamento"].file if p.name.endswith(".tracciati.json"))
    dopo = next(p for p in di_nuovo.file if p.name.endswith(".tracciati.json"))
    assert prima.read_text(encoding="utf-8") == dopo.read_text(encoding="utf-8")


def test_la_regola_delle_lunghezze_e_un_parametro() -> None:
    kit = Maggiorazione()
    assert da_quotare(2.0, kit, "supply_air") == (3.5, None)  # (2 + 1) × 1,15 = 3,45
    assert da_quotare(4.0, kit, "supply_air") == (6.0, None)  # 5,75 per eccesso
    con_minimo = Maggiorazione(minimi_m={"refrigerant_liquid": 12})
    assert da_quotare(4.0, con_minimo, "refrigerant_liquid") == (12.0, 12.0)
    altra = Maggiorazione(aggiunta_m=0, fattore=1.0, arrotondamento_m=0.1)
    assert da_quotare(4.03, altra, "supply_air") == (4.1, None)


def test_le_lunghezze_sono_quelle_del_percorso_disegnato(esiti: dict[str, Esito]) -> None:
    esito = esiti["appartamento"]
    dati = json.loads(next(p for p in esito.file if p.name.endswith(".tracciati.json")).read_text())
    for tratta, percorso in zip(dati["tratte"], esito.percorsi, strict=True):
        punti = percorso.punti
        misurata = sum(abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in zip(punti, punti[1:], strict=False))
        assert tratta["lunghezza_misurata_m"] == pytest.approx(misurata, abs=1e-3)
        attesa, _ = da_quotare(tratta["lunghezza_misurata_m"], esito.pianta.maggiorazione, tratta["fluido"])
        assert tratta["lunghezza_da_quotare_m"] == attesa
    assert dati["rilievi"]["diagonali"] == 0
    assert dati["forature"] and dati["fori_dei_pezzi"]


def test_lo_sfondo_raster_sta_sotto_il_disegno(esiti: dict[str, Esito]) -> None:
    esito = esiti["corridoio"]
    assert any(p.name == "sfondo-corridoio.jpg" for p in esito.file)
    svg = next(p for p in esito.file if p.suffix == ".svg").read_text(encoding="utf-8")
    assert '<image href="sfondo-corridoio.jpg"' in svg
    assert svg.index("<image") < svg.index("<polyline")


def test_lo_schema_dichiarato_e_quello_del_modello() -> None:
    dichiarato = json.loads((RADICE / "schemas" / "pianta.schema.json").read_text(encoding="utf-8"))
    assert dichiarato == schema_della_pianta()


def test_i_fluidi_sono_quelli_di_naming() -> None:
    nomi = {m["medium"] for m in json.loads((RADICE / "naming" / "media.json").read_text())["media"]}
    assert set(Fluido.__args__) <= nomi  # type: ignore[attr-defined]


def test_una_pianta_che_non_regge_dice_dove(tmp_path: Path) -> None:
    dati = json.loads(APPARTAMENTO.read_text(encoding="utf-8"))
    dati["aperture"][0]["muro"] = "non-c-e"
    rotta = tmp_path / "rotta.json"
    rotta.write_text(json.dumps(dati), encoding="utf-8")
    with pytest.raises(ErroreDellaPianta, match="non-c-e"):
        carica_pianta(rotta)


def test_il_comando_del_repository(tmp_path: Path) -> None:
    uscita = cli(["pianta", str(CASI["muro"]), "--out", str(tmp_path), "--cartiglio", str(CARTIGLIO)])
    assert uscita == 0
    for suffisso in (".svg", ".pdf", ".dxf", ".tracciati.json"):
        assert (tmp_path / f"muro-senza-aperture{suffisso}").exists()


def test_il_comando_della_skill(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    uscita = skill(
        ["pianta", str(CASI["muro"]), "--out", str(tmp_path), "--senza-dxf"],
        cartelle_del_repository(RADICE),
    )
    assert uscita == 0
    assert "Forature fuori dalle aperture: 1" in capsys.readouterr().out
    assert not (tmp_path / "muro-senza-aperture.dxf").exists()
