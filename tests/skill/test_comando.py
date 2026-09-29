"""Il comando della skill (REL-001): il lavoro deterministico, in un comando solo.

Le prove girano con i dati del repository; quelle sulla cartella costruita stanno in
`test_costruzione_della_skill.py`. Tengono su quello che la skill promette al
progettista, e che I-166 vuole della skill e non della sessione:

- `valida` dice se il grafo di Capire regge, e quali domande porta;
- `completa` scrive il grafo completo e il grafo da leggere, e dice una volta sola
  il perche' di ogni regola;
- `disegna` esegue il piano e **misura**: SVG, PDF, DXF e i rilievi della tavola,
  scritti accanto per il progettista, e un codice d'uscita che ferma la consegna
  quando la tavola non si consegna;
- `catalogo`, `anteprima`, `consegna` fanno quello che dicono.
"""

import importlib.util
import json
import re
import zlib
from collections.abc import Callable
from pathlib import Path

import pytest

from disegnatore_mep.graphics.pdf import PUNTI_PER_MM
from disegnatore_mep.skill import Cartelle, _png, cartelle_del_repository, main

ROOT = Path(__file__).resolve().parents[2]
IMPIANTO_6 = ROOT / "docs" / "collaudi" / "REL-003" / "impianto-6"
BOZZA_6 = ROOT / "docs" / "collaudi" / "REL-003" / "capire-giro-2" / "grafo.json"
PROVA_1 = ROOT / "examples" / "prova" / "prova-1-due-pdc-accumulo-combinato.json"


@pytest.fixture(scope="module")
def cartelle() -> Cartelle:
    return cartelle_del_repository(ROOT)


@pytest.fixture(scope="module")
def documento() -> Callable[..., str]:
    spec = importlib.util.spec_from_file_location(
        "grafo_leggibile", ROOT / "examples" / "graph" / "build_plant_graph.py"
    )
    assert spec is not None and spec.loader is not None
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo.build  # type: ignore[no-any-return]


def test_valida_dice_se_il_grafo_regge_e_quali_domande_porta(
    cartelle: Cartelle, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["valida", str(BOZZA_6)], cartelle) == 0
    uscita = capsys.readouterr().out
    assert "Il grafo si legge: 25 pezzi, 30 tubazioni, 5 reti" in uscita
    assert "a-ritorno-serpentino:" in uscita, "le assunzioni proposte sono le domande del passo 2"


def test_valida_ferma_un_grafo_che_nomina_una_voce_che_non_c_e(
    cartelle: Cartelle, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    grafo = json.loads(BOZZA_6.read_text(encoding="utf-8"))
    grafo["components"][0]["definition_id"] = "pompa-inventata"
    (tmp_path / "grafo.json").write_text(json.dumps(grafo), encoding="utf-8")
    assert main(["valida", str(tmp_path / "grafo.json")], cartelle) == 2
    assert "UNKNOWN_COMPONENT_DEFINITION" in capsys.readouterr().out


def test_completa_scrive_il_grafo_completo_e_il_grafo_da_leggere(
    cartelle: Cartelle,
    documento: Callable[..., str],
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    completo = tmp_path / "grafo-completo.json"
    assert main(["completa", str(PROVA_1), "--out", str(completo)], cartelle, documento) == 0
    uscita = capsys.readouterr().out
    assert json.loads(completo.read_text(encoding="utf-8"))["components"]
    da_leggere = tmp_path / "grafo-completo-da-leggere.md"
    assert da_leggere.read_text(encoding="utf-8").startswith("# Il grafo dell'impianto")
    # Una regola che mette piu' pezzi ha una ragione sola, detta una volta.
    regole = re.findall(r"· regola: (\S+)", uscita)
    assert len(regole) == len(set(regole)), "il perche' di una regola si stampa una volta sola"
    assert re.search(r"Valvola di intercettazione — \d+ pezzi", uscita)


def test_completa_dice_quando_il_grafo_da_leggere_non_si_scrive(
    cartelle: Cartelle,
    documento: Callable[..., str],
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Il circuito solare non ha ancora una famiglia di linea (`naming/lines.json`): il grafo
    completo esce lo stesso, e il documento che manca si dice invece di fermare tutto."""
    completo = tmp_path / "grafo-completo.json"
    assert main(["completa", str(BOZZA_6), "--out", str(completo)], cartelle, documento) == 0
    assert json.loads(completo.read_text(encoding="utf-8")) == json.loads(
        (IMPIANTO_6 / "grafo-completo-6.json").read_text(encoding="utf-8")
    ), "il grafo completo e' quello che la catena di REL-003 ha scritto"
    assert "Il grafo da leggere non si e' potuto scrivere" in capsys.readouterr().out


def test_disegna_scrive_la_tavola_in_pdf_dxf_e_svg_con_i_rilievi_accanto(
    cartelle: Cartelle, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    codice = main(
        [
            "disegna", str(IMPIANTO_6 / "grafo-completo-6.json"),
            "--piano", str(IMPIANTO_6 / "piano-6-a.json"),
            "--out", str(tmp_path),
        ],
        cartelle,
    )
    assert codice == 0
    uscita = capsys.readouterr().out
    assert "tratte cedute 0 · rilievi bloccanti 0" in uscita
    nome = "prova-6-centrale-ibrida-solare-t1"
    for estensione in (".svg", ".pdf", ".dxf"):
        assert (tmp_path / f"{nome}{estensione}").exists(), estensione
    pdf = (tmp_path / f"{nome}.pdf").read_bytes()
    lato = re.search(rb"/MediaBox \[0 0 ([0-9.]+) ([0-9.]+)\]", pdf)
    assert lato is not None
    assert float(lato.group(1)) == pytest.approx(594 * PUNTI_PER_MM, abs=1e-3), "il piano chiede l'A2"
    rilievi = (tmp_path / f"{nome}-rilievi.md").read_text(encoding="utf-8")
    assert "Formato **A2** · tratte **48** · tratte cedute **0** · rilievi bloccanti **0**" in rilievi
    assert "HIGHWAY_IS_NOT_STRAIGHT" in rilievi, "le regole del piano stanno nei rilievi"
    assert "## Il cartiglio" in rilievi


def test_un_piano_che_non_si_instrada_ferma_la_consegna_e_dice_dove(
    cartelle: Cartelle, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    piano = json.loads((IMPIANTO_6 / "piano-6-a.json").read_text(encoding="utf-8"))
    for pezzo in piano["pezzi"].values():
        pezzo["x"], pezzo["y"] = 0, 0
    (tmp_path / "piano.json").write_text(json.dumps(piano), encoding="utf-8")
    codice = main(
        [
            "disegna", str(IMPIANTO_6 / "grafo-completo-6.json"),
            "--piano", str(tmp_path / "piano.json"), "--out", str(tmp_path / "tavola"),
        ],
        cartelle,
    )
    assert codice == 2
    uscita = capsys.readouterr().out
    assert "Il piano non si instrada" in uscita
    assert "nel piano" in uscita, "il messaggio dice dove il piano ha messo i due capi"
    assert not (tmp_path / "tavola").exists(), "niente tavola, niente cartella"


def test_un_file_che_non_c_e_esce_con_uno(cartelle: Cartelle, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["valida", str(tmp_path / "manca.json")], cartelle) == 1
    assert "Errore:" in capsys.readouterr().err


def test_il_catalogo_e_una_riga_per_voce(cartelle: Cartelle, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["catalogo"], cartelle) == 0
    voci = [r for r in capsys.readouterr().out.splitlines() if r and not r.startswith(" ")]
    assert len(voci) == len(list(cartelle.catalogo.glob("*.json")))
    assert main(["catalogo", "--mestiere", "heat_generation"], cartelle) == 0
    generatori = [r for r in capsys.readouterr().out.splitlines() if r and not r.startswith(" ")]
    assert generatori and all("heat_generation" in r for r in generatori)


def test_il_catalogo_dice_quando_un_pezzo_non_c_e(cartelle: Cartelle, capsys: pytest.CaptureFixture[str]) -> None:
    """Un cogeneratore non e' una caldaia: la voce che manca si dice, e non se ne sceglie una
    che somiglia (Capire, tipo B; la valutazione 4 di REL-001)."""
    assert main(["catalogo", "--cerca", "cogeneratore"], cartelle) == 0
    assert "Nessuna voce del catalogo per «cogeneratore»" in capsys.readouterr().out
    assert main(["catalogo", "--cerca", "caldaia"], cartelle) == 0
    trovate = [r for r in capsys.readouterr().out.splitlines() if r and not r.startswith(" ")]
    assert {r.split(" — ")[0] for r in trovate} == {"gas-boiler", "gas-boiler-modular"}
    assert any("a bordo: circulation" in r for r in trovate), "la caldaia modulare porta il circolatore"


def test_il_png_dell_anteprima_e_un_png_che_si_legge() -> None:
    dati = _png(2, 1, [bytes([255, 0, 0, 0, 0, 255])])
    assert dati.startswith(b"\x89PNG\r\n\x1a\n")
    intestazione = dati[16:29]
    assert int.from_bytes(intestazione[0:4], "big") == 2 and int.from_bytes(intestazione[4:8], "big") == 1
    idat = dati.index(b"IDAT")
    lunghezza = int.from_bytes(dati[idat - 4 : idat], "big")
    assert zlib.decompress(dati[idat + 4 : idat + 4 + lunghezza]) == bytes([0, 255, 0, 0, 0, 0, 255])


def test_consegna_copia_i_file_per_il_progettista(cartelle: Cartelle, tmp_path: Path) -> None:
    tavola = tmp_path / "tavola"
    tavola.mkdir()
    for nome in ("t1.pdf", "t1.dxf", "t1.svg", "t1-rilievi.md", "logo.jpg", "geometria.json"):
        (tavola / nome).write_text("x", encoding="utf-8")
    assert main(["consegna", str(tavola), str(tmp_path / "fuori")], cartelle) == 0
    assert sorted(p.name for p in (tmp_path / "fuori").iterdir()) == [
        "logo.jpg", "t1-rilievi.md", "t1.dxf", "t1.pdf", "t1.svg",
    ]
