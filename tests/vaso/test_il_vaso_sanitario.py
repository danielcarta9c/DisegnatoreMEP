"""Il vaso sanitario del bollitore (REL-026 A-5, I-300).

Il metodo e' del focus tecnico Caleffi «Il dimensionamento degli impianti idrosanitari —
Vasi d'espansione e accumuli» (0851415), p. 4, e si prova sul suo esempio di p. 5. Il
metodo e' una **proposta al PO**: queste prove dicono che fa quello che il modulo dichiara,
non che i margini siano quelli giusti.
"""

from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.skill import cartelle_del_repository, main
from disegnatore_mep.vaso import (
    SERIE_DEI_VASI_SANITARI_L,
    DatiDelVasoSanitario,
    coefficiente_di_espansione,
    dimensiona_il_vaso_sanitario,
    pressione_finale_sanitaria,
)
from disegnatore_mep.vaso.comando import applica_sanitario

ROOT = Path(__file__).resolve().parents[2]
T1 = ROOT / "docs" / "collaudi" / "REL-023" / "T1" / "grafo-completo.json"
VASO = "expansion-connection-dhw-bollitore-cold-in"
SICUREZZA = "dhw-safety-group-bollitore-cold-in"


@pytest.fixture(scope="module")
def catalogo() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        ROOT / "examples" / "layout" / "catalog", symbols=SymbolRegistry.from_directory(ROOT / "assets" / "symbols")
    )


# --- il calcolatore -------------------------------------------------------------------


def test_l_esempio_di_caleffi() -> None:
    """Caleffi, p. 5: 1000 l, acqua fredda a 10 °C, accumulo a 80 °C, rete 3 bar, valvola a
    7 bar → 63,49 l. Il coefficiente dalla densita' (0,02871) e' quello della tabella di
    Caleffi (0,0290 − 0,0003 = 0,0287) al decimillesimo."""
    vaso = dimensiona_il_vaso_sanitario(DatiDelVasoSanitario(1000, 80, 3, 7))
    assert vaso.coefficiente == pytest.approx(0.0287, abs=1e-4)
    assert vaso.pressione_finale_bar == pytest.approx(6.3)
    assert vaso.precarica_bar == pytest.approx(3.0)
    assert vaso.volume_nominale_l == pytest.approx(63.49, rel=1e-3)
    # La prima taglia della serie non sotto il nominale, come per il riscaldamento.
    assert vaso.taglia_l == 80


@pytest.mark.parametrize(("temperatura", "caleffi"), [(60, 0.0167), (70, 0.0224), (80, 0.0287)])
def test_il_coefficiente_dalla_densita_e_quello_della_tabella_di_caleffi(temperatura: int, caleffi: float) -> None:
    """La tabella di Caleffi (p. 4) e' riferita a 4 °C: fra 10 °C e la massima e' la
    differenza delle due righe (10 °C: 0,0003)."""
    assert coefficiente_di_espansione(temperatura, 10.0) == pytest.approx(caleffi, abs=1.5e-4)


@pytest.mark.parametrize(("taratura", "finale"), [(3.0, 2.5), (5.0, 4.5), (6.0, 5.4), (7.0, 6.3), (8.0, 7.2)])
def test_la_pressione_finale_dalla_taratura(taratura: float, finale: float) -> None:
    """Sopra i 5 bar il 10 % sotto la taratura (Caleffi, p. 4); fino a 5 bar lo scarto di
    0,5 bar del riscaldamento. A 5 bar le due regole danno lo stesso numero."""
    assert pressione_finale_sanitaria(taratura) == pytest.approx(finale)


def test_un_bollitore_da_200_litri() -> None:
    """L'esempio del rapporto: 200 l, 60 °C, rete 3 bar, valvola a 6 bar."""
    vaso = dimensiona_il_vaso_sanitario(DatiDelVasoSanitario(200, 60, 3, 6))
    assert vaso.volume_di_espansione_l == pytest.approx(200 * coefficiente_di_espansione(60, 10))
    assert vaso.volume_nominale_l == pytest.approx(vaso.volume_di_espansione_l * 6.4 / 2.4)
    assert vaso.taglia_l == 12
    assert vaso.avvisi == ()


def test_la_precarica_e_la_pressione_di_rete() -> None:
    vaso = dimensiona_il_vaso_sanitario(DatiDelVasoSanitario(300, 65, 4, 6))
    assert vaso.precarica_bar == pytest.approx(4.0)
    assert vaso.caratteristiche(esecutivo=False) == f"{vaso.taglia_l} l"
    assert vaso.caratteristiche(esecutivo=True) == f"{vaso.taglia_l} l · precarica 4,0 bar"


def test_la_taglia_della_commessa_sta_nella_serie() -> None:
    """Il solo riscontro della commessa (I-300): un vaso sanitario da 18 l. Non si sa con
    quali dati: il metodo non e' tarato su quel numero, si guarda solo che la taglia esista."""
    assert 18 in SERIE_DEI_VASI_SANITARI_L


def test_una_rete_sopra_la_pressione_finale_vuole_un_riduttore() -> None:
    with pytest.raises(ValueError, match="riduttore"):
        dimensiona_il_vaso_sanitario(DatiDelVasoSanitario(200, 60, 5.5, 6))


def test_poco_salto_fra_rete_e_finale_si_avvisa() -> None:
    vaso = dimensiona_il_vaso_sanitario(DatiDelVasoSanitario(200, 60, 5.2, 6))
    assert any("meno di 0,3 bar" in avviso for avviso in vaso.avvisi)


def test_oltre_la_serie_non_sceglie_e_lo_dice() -> None:
    vaso = dimensiona_il_vaso_sanitario(DatiDelVasoSanitario(10000, 80, 4, 6))
    assert vaso.taglia_l is None
    assert any("catalogo del fornitore" in avviso for avviso in vaso.avvisi)


@pytest.mark.parametrize(
    "dati",
    [
        DatiDelVasoSanitario(0, 60, 3, 6),
        DatiDelVasoSanitario(200, 10, 3, 6),
        DatiDelVasoSanitario(200, 60, 0, 6),
        DatiDelVasoSanitario(200, 60, 3, 0.5),
    ],
)
def test_dati_che_non_bastano_si_fermano(dati: DatiDelVasoSanitario) -> None:
    with pytest.raises(ValueError):
        dimensiona_il_vaso_sanitario(dati)


# --- il comando -----------------------------------------------------------------------


def _con_livello(livello: str | None) -> ProjectModel:
    modello = load_project(T1)
    return modello.model_copy(update={"metadata": modello.metadata.model_copy(update={"livello": livello})})


def test_nel_definitivo_solo_la_taglia_e_il_bollitore_dal_grafo(catalogo: ComponentRegistry) -> None:
    completo, vaso, scritto = applica_sanitario(_con_livello(None), catalogo, 60, 3, 6)
    pezzi = {c.id: c for c in completo.components}
    assert pezzi[VASO].properties["volume_l"] == vaso.taglia_l == 12
    assert "precarica_bar" not in pezzi[VASO].properties
    assert "etichetta" not in pezzi[SICUREZZA].properties
    # Il volume del bollitore e' quello del grafo (200 l), e il comando lo dice.
    assert vaso.volume_di_espansione_l == pytest.approx(200 * coefficiente_di_espansione(60, 10))
    assert any("dal grafo" in riga and "200" in riga for riga in scritto)
    # Il vaso dell'impianto non si tocca.
    assert pezzi["expansion-connection-pdc-water-return"].properties == {}


def test_nell_esecutivo_anche_la_precarica_e_la_taratura_della_sicurezza(catalogo: ComponentRegistry) -> None:
    completo, vaso, _ = applica_sanitario(_con_livello("esecutivo"), catalogo, 60, 3.5, 6, volume_bollitore_l=300)
    pezzi = {c.id: c for c in completo.components}
    assert pezzi[VASO].properties["precarica_bar"] == pytest.approx(3.5)
    assert pezzi[SICUREZZA].properties["etichetta"] == "6 bar"
    assert vaso.volume_di_espansione_l == pytest.approx(300 * coefficiente_di_espansione(60, 10))


def test_senza_vaso_sanitario_si_ferma(catalogo: ComponentRegistry) -> None:
    modello = load_project(ROOT / "examples" / "rules" / "centrale-pdc-completa.json")
    with pytest.raises(ValueError, match="acqua fredda del bollitore"):
        applica_sanitario(modello, catalogo, 60, 3, 6, volume_bollitore_l=200)


def test_la_riga_di_comando(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    uscita = tmp_path / "grafo.json"
    argv = ["vaso", str(T1), "--sanitario", "--tmax", "60", "--rete", "3", "--taratura", "6", "--out", str(uscita)]
    assert main(argv, cartelle_del_repository(ROOT)) == 0
    detto = capsys.readouterr().out
    assert "Vaso sanitario" in detto and "12 l" in detto
    vaso = next(c for c in load_project(uscita).components if c.id == VASO)
    assert vaso.properties["volume_l"] == 12
    # Senza la taratura il sanitario non parte: la valvola del riscaldamento (3 bar) non vale.
    assert main(["vaso", str(T1), "--sanitario", "--tmax", "60", "--rete", "3", "--out", str(uscita)],
                cartelle_del_repository(ROOT)) == 1
    # E il vaso d'impianto vuole ancora i suoi dati.
    assert main(["vaso", str(T1), "--tmax", "55", "--out", str(uscita)], cartelle_del_repository(ROOT)) == 1
