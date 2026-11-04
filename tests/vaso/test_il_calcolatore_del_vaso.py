"""Il calcolatore del vaso d'espansione (REL-011, D-220): stessi dati, stesso vaso."""

import pytest

from disegnatore_mep.vaso import (
    DatiDelVaso,
    coefficiente_di_espansione,
    densita_dell_acqua,
    dimensiona_il_vaso,
)

SHENLING = {"taratura_sicurezza_bar": 3.0, "pressione_minima_bar": 1.5, "pressione_di_riempimento_bar": 2.0}
"""ThermaX R290: valvola di sicurezza a 3 bar, almeno 1,5 bar per la portata, si riempie a
circa 2 bar (manuale, ricerca guasti e § 6.6)."""


def test_la_densita_dell_acqua_e_quella_delle_tabelle() -> None:
    assert densita_dell_acqua(10) == pytest.approx(999.70, abs=0.01)
    assert densita_dell_acqua(70) == pytest.approx(977.77, abs=0.01)
    assert coefficiente_di_espansione(55) == pytest.approx(0.0142, abs=0.0001)
    assert coefficiente_di_espansione(70) == pytest.approx(0.0224, abs=0.0001)


def test_una_casa_con_la_shenling() -> None:
    """200 l d'acqua, 55 °C, il punto piu' alto 6 m sopra il vaso: 20,4 l nominali, il
    vaso da 24 l, precarica 1,5 bar (la minima della macchina), carica 2,0 bar."""
    vaso = dimensiona_il_vaso(DatiDelVaso(contenuto_l=200, temperatura_massima_c=55, dislivello_m=6, **SHENLING))
    assert vaso.volume_nominale_l == pytest.approx(20.4, abs=0.1)
    assert (vaso.taglia_l, vaso.precarica_bar, vaso.caricamento_bar) == (24, 1.5, 2.0)
    assert vaso.caratteristiche(esecutivo=True) == "24 l · precarica 1,5 bar"
    assert vaso.caratteristiche(esecutivo=False) == "24 l"
    assert vaso.scritta_di_caricamento == "carica 2,0 bar"
    assert not vaso.avvisi


def test_la_statica_alza_la_precarica() -> None:
    """15 m sopra il vaso: 1,47 bar di colonna, piu' 0,3 = 1,8 bar."""
    vaso = dimensiona_il_vaso(DatiDelVaso(contenuto_l=1000, temperatura_massima_c=55, dislivello_m=15, **SHENLING))
    assert (vaso.precarica_bar, vaso.taglia_l) == (1.8, 100)


def test_il_contenuto_stimato_si_dice() -> None:
    vaso = dimensiona_il_vaso(DatiDelVaso(contenuto_l=200, temperatura_massima_c=55, dislivello_m=6, **SHENLING))
    assert vaso.caratteristiche(esecutivo=False, contenuto_stimato=True) == "24 l · contenuto stimato"


def test_il_glicole_porta_il_suo_coefficiente() -> None:
    acqua = dimensiona_il_vaso(DatiDelVaso(contenuto_l=300, temperatura_massima_c=55, dislivello_m=3, **SHENLING))
    glicole = dimensiona_il_vaso(
        DatiDelVaso(contenuto_l=300, temperatura_massima_c=55, dislivello_m=3, coefficiente_di_espansione=0.025, **SHENLING)
    )
    assert glicole.volume_nominale_l > acqua.volume_nominale_l


def test_un_edificio_troppo_alto_per_la_valvola_non_ha_vaso() -> None:
    with pytest.raises(ValueError, match="nessun vaso basta"):
        dimensiona_il_vaso(DatiDelVaso(contenuto_l=400, temperatura_massima_c=70, dislivello_m=25, **SHENLING))


def test_non_inventa() -> None:
    with pytest.raises(ValueError):
        dimensiona_il_vaso(DatiDelVaso(contenuto_l=0, temperatura_massima_c=55, dislivello_m=3))
