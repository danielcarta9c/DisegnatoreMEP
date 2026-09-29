"""Il calcolatore dei diametri (REL-007, D-193), su casi calcolati a mano.

Il DN e' il diametro interno netto (I-150): la sezione di un DN e' pi·DN²/4, col DN in
metri. La velocita' massima e' quella della tab. 9 del Quaderno Caleffi n. 5 per gli
edifici residenziali e terziari (I-154). La portata piu' grande che un DN porta e'
dunque, a mano:

    DN 10  1,1 m/s · pi·0,010²/4 = 8,6394e-5 m³/s =   0,3110 m³/h
    DN 15  1,1 m/s · pi·0,015²/4 = 1,9439e-4 m³/s =   0,6998 m³/h
    DN 20  1,1 m/s · pi·0,020²/4 = 3,4558e-4 m³/s =   1,2441 m³/h
    DN 25  1,3 m/s · pi·0,025²/4 = 6,3814e-4 m³/s =   2,2973 m³/h
    DN 32  1,6 m/s · pi·0,032²/4 = 1,2868e-3 m³/s =   4,6325 m³/h
    DN 40  1,8 m/s · pi·0,040²/4 = 2,2619e-3 m³/s =   8,1430 m³/h
    DN 50  2,0 m/s · pi·0,050²/4 = 3,9270e-3 m³/s =  14,1372 m³/h
    DN 65  2,2 m/s · pi·0,065²/4 = 7,3003e-3 m³/s =  26,2810 m³/h
    DN 80  2,5 m/s · pi·0,080²/4 = 1,2566e-2 m³/s =  45,2389 m³/h
    DN 300 2,5 m/s · pi·0,300²/4 = 0,17671  m³/s = 636,1725 m³/h

Un millesimo di m³/h sotto il bordo il DN resta quello; un millesimo sopra passa al
successivo. E la portata dalla potenza, a mano: 15 kW con 5 K sono 15 / (4,18 · 5) =
0,71770 kg/s, cioe' 2,5837 m³/h con 1000 kg/m³.
"""

import pytest

from disegnatore_mep.diametri.calcolatore import (
    SERIE_DEI_DN,
    VELOCITA_MASSIMA_M_S,
    diametro_per,
    portata_da_potenza,
    portata_massima_m3h,
    potenza_da_portata,
    velocita_m_s,
)

BORDI_A_MANO: list[tuple[int, float, int | None]] = [
    (10, 0.3110, 15),
    (15, 0.6997, 20),
    (20, 1.2440, 25),
    (25, 2.2972, 32),
    (32, 4.6324, 40),
    (40, 8.1430, 50),
    (50, 14.137, 65),
    (65, 26.280, 80),
    (80, 45.238, 100),
    (300, 636.17, None),
]
"""Per ogni DN: una portata appena sotto il suo bordo, e il DN che viene subito dopo."""


@pytest.mark.parametrize(("dn", "sotto", "dopo"), BORDI_A_MANO)
def test_ai_bordi_fra_un_dn_e_il_successivo(dn: int, sotto: float, dopo: int | None) -> None:
    """Appena sotto il bordo il DN e' quello; appena sopra, il successivo."""
    scelto = diametro_per(sotto)
    assert scelto is not None and scelto.dn == dn
    assert scelto.velocita_m_s <= VELOCITA_MASSIMA_M_S[dn]
    oltre = diametro_per(sotto + 0.01 if dn == 300 else sotto + 0.001)
    if dopo is None:
        assert oltre is None, "oltre DN 300 il calcolatore non estrapola"
    else:
        assert oltre is not None and oltre.dn == dopo


@pytest.mark.parametrize("dn", SERIE_DEI_DN)
def test_proprio_sul_bordo_il_dn_resta_quello(dn: int) -> None:
    """«La velocita' non supera la massima» (D-193): uguale e' ancora dentro, anche
    quando il conto in virgola mobile da' un ultimo decimale in piu'."""
    scelto = diametro_per(portata_massima_m3h(dn))
    assert scelto is not None and scelto.dn == dn


def test_le_portate_massime_sono_quelle_calcolate_a_mano() -> None:
    a_mano = {10: 0.3110, 15: 0.6998, 20: 1.2441, 25: 2.2973, 32: 4.6325, 40: 8.1430,
              50: 14.1372, 65: 26.2810, 80: 45.2389, 300: 636.1725}
    for dn, attesa in a_mano.items():
        assert portata_massima_m3h(dn) == pytest.approx(attesa, abs=1e-4), dn


def test_la_serie_e_la_velocita_sono_quelle_di_d_193() -> None:
    assert SERIE_DEI_DN == (10, 15, 20, 25, 32, 40, 50, 65, 80, 100, 125, 150, 200, 250, 300)
    assert [VELOCITA_MASSIMA_M_S[dn] for dn in (20, 25, 32, 40, 50, 65, 80)] == [
        1.1, 1.3, 1.6, 1.8, 2.0, 2.2, 2.5
    ]
    assert all(VELOCITA_MASSIMA_M_S[dn] == 1.1 for dn in (10, 15))
    assert all(VELOCITA_MASSIMA_M_S[dn] == 2.5 for dn in SERIE_DEI_DN if dn >= 80)


def test_la_portata_dalla_potenza_calcolata_a_mano() -> None:
    assert portata_da_potenza(15, 5) == pytest.approx(2.583732, abs=1e-6)
    assert portata_da_potenza(40, 5) == pytest.approx(6.889952, abs=1e-6)
    assert portata_da_potenza(25, 10) == pytest.approx(2.153110, abs=1e-6)
    assert potenza_da_portata(portata_da_potenza(120, 5), 5) == pytest.approx(120)


def test_una_pompa_di_calore_da_15_kw_con_5_k_esce_oi_32() -> None:
    """Il caso portato al PO nella domanda (I-154): DN 25 porterebbe 1,46 m/s, oltre
    i suoi 1,3; DN 32 la porta a 2,5837 / 3600 / 8,0425e-4 = 0,892 m/s."""
    scelto = diametro_per(portata_da_potenza(15, 5))
    assert scelto is not None
    assert scelto.dn == 32
    assert scelto.scritta == "Øi 32"
    assert scelto.velocita_m_s == pytest.approx(0.8924, abs=1e-4)
    assert velocita_m_s(portata_da_potenza(15, 5), 25) == pytest.approx(1.462, abs=1e-3)


@pytest.mark.parametrize("dati", [(0, 5), (15, 0), (-1, 5), (15, -5)])
def test_niente_potenze_o_salti_nulli(dati: tuple[float, float]) -> None:
    with pytest.raises(ValueError):
        portata_da_potenza(*dati)


@pytest.mark.parametrize("portata", [0.0, -1.0])
def test_niente_portate_nulle(portata: float) -> None:
    with pytest.raises(ValueError):
        diametro_per(portata)
