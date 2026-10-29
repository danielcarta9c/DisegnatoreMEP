"""Le regole come dato, la regola delle lunghezze, le confezioni senza giunte, i sostegni."""

import json
from pathlib import Path

import pytest

from disegnatore_mep.distinta import ErroreDelleRegole, RegoleDellaDistinta, carica_regole
from disegnatore_mep.distinta.confezioni import in_confezioni
from disegnatore_mep.distinta.lunghezze import Minimo, da_quotare, per_eccesso, quante_volte
from disegnatore_mep.distinta.regole import FILE_DELLE_REGOLE
from disegnatore_mep.skill import fascio_della_cartella

from .conftest import REGOLE

# --- le regole -------------------------------------------------------------------


def test_ogni_voce_delle_regole_ha_fonte_e_perche(regole: RegoleDellaDistinta) -> None:
    """Le regole si caricano solo se ogni voce dice da dove viene e perche'."""
    voci = [v for f in regole.fluidi.values() for v in f["voci"]]
    voci += [v for c in regole.corredo.values() for v in c["voci"]]
    voci += list(regole.attivita)
    assert len(voci) > 50
    for voce in voci:
        assert voce["fonte"].strip() and voce["perche"].strip(), voce["id"]


def test_una_regola_senza_fonte_non_si_carica(tmp_path: Path) -> None:
    for nome in FILE_DELLE_REGOLE:
        (tmp_path / f"{nome}.json").write_text((REGOLE / f"{nome}.json").read_text(encoding="utf-8"), encoding="utf-8")
    fluidi = json.loads((tmp_path / "fluidi.json").read_text(encoding="utf-8"))
    del fluidi["fluidi"][0]["voci"][0]["fonte"]
    (tmp_path / "fluidi.json").write_text(json.dumps(fluidi, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ErroreDelleRegole, match="supply_air/flessibile-in-confezioni: manca «fonte»"):
        carica_regole(tmp_path)


def test_un_calcolo_sconosciuto_non_si_carica(tmp_path: Path) -> None:
    for nome in FILE_DELLE_REGOLE:
        (tmp_path / f"{nome}.json").write_text((REGOLE / f"{nome}.json").read_text(encoding="utf-8"), encoding="utf-8")
    corredo = json.loads((tmp_path / "corredo.json").read_text(encoding="utf-8"))
    corredo["voci"]["ducted-indoor-unit"]["voci"][0]["calcolo"]["tipo"] = "a_occhio"
    (tmp_path / "corredo.json").write_text(json.dumps(corredo, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ErroreDelleRegole, match="calcolo 'a_occhio' sconosciuto"):
        carica_regole(tmp_path)


def test_le_regole_si_leggono_anche_da_un_fascio(tmp_path: Path, regole: RegoleDellaDistinta) -> None:
    """Nella skill i dati stanno in un file per cartella (I-188): lo stesso fascio
    dei simboli e del catalogo porta le stesse regole, con la stessa impronta."""
    fascio = tmp_path / "distinta.json"
    fascio.write_text(fascio_della_cartella(REGOLE, "distinta"), encoding="utf-8")
    assert carica_regole(fascio).impronta == regole.impronta


# --- la regola delle lunghezze -----------------------------------------------------

REGOLA_DEL_KIT = {"aggiunta_m": 1.0, "fattore": 1.15, "passo_m": 0.5}


@pytest.mark.parametrize(
    ("stimata", "attesa"),
    [(4.1, 6.0), (2.0, 3.5), (4.2, 6.0), (4.8, 7.0), (7.6, 10.0), (12.0, 15.0), (1.5, 3.0), (3.7, 5.5)],
)
def test_la_regola_delle_lunghezze_del_kit(stimata: float, attesa: float) -> None:
    """(L + 1 m) × 1,15 per eccesso al mezzo metro: i numeri della tabella delle
    tratte della M.02 del kit."""
    assert da_quotare(stimata, REGOLA_DEL_KIT).da_quotare == attesa


def test_il_minimo_vince_e_il_conto_lo_dice() -> None:
    esito = da_quotare(8.0, REGOLA_DEL_KIT, [Minimo(12.0, "minimo frigo")])
    assert esito.da_quotare == 12.0
    assert esito.calcolo == "(8 + 1) × 1,15 = 10,35 → 10,5 m; minimo frigo 12 m → 12 m"
    assert da_quotare(20.0, REGOLA_DEL_KIT, [Minimo(12.0, "minimo frigo")]).da_quotare == 24.5


def test_le_regole_della_cartella_sono_quelle_del_kit(regole: RegoleDellaDistinta) -> None:
    regola = regole.lunghezze["regola"]
    assert (regola["aggiunta_m"], regola["fattore"], regola["passo_m"]) == (1.0, 1.15, 0.5)
    minimi = {c["classe"]: c["minimo_m"] for c in regole.lunghezze["classi"]}
    assert minimi == {"frigo": 12.0, "condensa": 10.0, "bus": 5.0, "ramo_aria": 2.0, "potenza": 0.0}


def test_l_eccesso_non_conta_il_rumore_della_virgola_mobile() -> None:
    """12 / 1,2 in virgola mobile fa 10,000000000000002: dieci passi, non undici."""
    assert quante_volte(12.0, 1.2) == 10
    assert per_eccesso(3.0, 0.5) == 3.0
    assert per_eccesso(3.01, 0.5) == 3.5


# --- le confezioni senza giunte ----------------------------------------------------


def test_i_rami_del_kit_stanno_interi_in_tre_confezioni_e_se_ne_comprano_quattro() -> None:
    esito = in_confezioni([6.0, 3.5, 6.0, 3.5, 7.0], 10.0, 0.5, 0.25)
    assert esito.riempimento == ((7.0,), (6.0, 3.5), (6.0, 3.5))
    assert esito.giunte == 0
    assert esito.per_la_riserva == 4
    assert esito.numero == 4


def test_nessun_pezzo_si_spezza_e_ogni_confezione_lascia_lo_sfrido() -> None:
    pezzi = [2.0, 9.5, 4.5, 4.5, 3.0, 8.0, 1.5]
    esito = in_confezioni(pezzi, 10.0, 0.5, 0.0)
    assert sorted(p for c in esito.riempimento for p in c) == sorted(pezzi)
    assert all(sum(c) <= 9.5 for c in esito.riempimento)
    assert esito.giunte == 0


def test_un_tratto_piu_lungo_di_una_confezione_si_giunta_e_lo_si_dice() -> None:
    esito = in_confezioni([12.0], 10.0, 0.5, 0.25)
    assert esito.giunte == 1
    assert sorted(p for c in esito.riempimento for p in c) == [2.5, 9.5]
    assert "1 giunte" in esito.calcolo


# --- i sostegni ----------------------------------------------------------------------


def test_i_sostegni_uno_ogni_passo_piu_uno_per_tratto(regole: RegoleDellaDistinta) -> None:
    sostegni = next(v for v in regole.fluidi["supply_air"]["voci"] if v["id"] == "sostegni")
    passo, in_piu = sostegni["calcolo"]["passo_m"], sostegni["calcolo"]["in_piu"]
    assert (passo, in_piu) == (1.2, 1)
    assert [quante_volte(q, passo) + in_piu for q in (6.0, 3.5, 6.0, 3.5, 7.0)] == [6, 4, 6, 4, 7]
    assert quante_volte(1.2, passo) + in_piu == 2
