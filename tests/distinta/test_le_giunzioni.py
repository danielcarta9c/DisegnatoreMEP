"""REL-023: le giunzioni dell'acqua (I-291, D-239) e il circolatore fra le apparecchiature
(I-292). Il PO: «I nippli vanno tra due accessori minori i raccordi a pressare tra tubo e
accessorio e tra tubo e tubo … le tee invece le conta dal grafo»."""

from typing import Any

import pytest

from disegnatore_mep.distinta import RegoleDellaDistinta, componi_la_distinta

from .test_il_corredo_idronico_e_il_costo import _tubo

RACCORDO_1 = "Raccordo diritto a pressare M 1\" × tubo multistrato MS 32×3"
NIPPLO_1 = "Nipplo 1\" M × M"
ALL_ATTACCO = "Raccordo diritto a pressare M × tubo multistrato MS 32×3, all'attacco"


def _grafo(pezzi: list[tuple[str, str, str]], tubi: list[dict[str, Any]], **pezzo_dati: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "1",
        "metadata": {"project_name": "Prova delle giunzioni"},
        "distinta": {"tubi": [{"rete": "primario", "tubo": "MS 32×3", "metri": 10, "isolamento": "preisolato"},
                              {"rete": "secondario", "tubo": "MS 32×3", "metri": 6, "isolamento": "preisolato"}]},
        "networks": [
            {"id": "primario", "name": "Primario", "domain": "hydronic", "medium": "heating_water"},
            {"id": "secondario", "name": "Secondario", "domain": "hydronic", "medium": "heating_water"},
        ],
        "components": [
            {"id": ident, "definition_id": voce, "tag": tag, "properties": pezzo_dati.get(ident, {})}
            for ident, voce, tag in pezzi
        ],
        "connections": tubi,
    }


def _sezione(distinta: Any, lettera: str) -> dict[str, Any]:
    return {v.testo: v for v in distinta.voci_della_sezione(lettera)}


def _gruppo_del_circolatore(**dati: Any) -> dict[str, Any]:
    """Volano – sfera – circolatore – sfera – collettore del pavimento, e ritorno al volano
    con una sfera: i pezzi della centrale si toccano."""
    pezzi = [
        ("vol", "buffer-four-port", "VOL-01"), ("v1", "valve-isolation", "VI-01"),
        ("cir", "pump-circulator", "CIR-01"), ("v2", "valve-isolation", "VI-02"),
        ("pav", "underfloor-panel", "TE-01"), ("v3", "valve-isolation", "VI-03"),
    ]
    tubi = [
        _tubo("s1", "secondario", ("vol", "secondary_out"), ("v1", "a"), sezione="MS 32×3"),
        _tubo("s2", "secondario", ("v1", "b"), ("cir", "a"), sezione="MS 32×3"),
        _tubo("s3", "secondario", ("cir", "b"), ("v2", "a"), sezione="MS 32×3"),
        _tubo("s4", "secondario", ("v2", "b"), ("pav", "in"), sezione="MS 32×3"),
        _tubo("s5", "secondario", ("pav", "out"), ("v3", "a"), sezione="MS 32×3"),
        _tubo("s6", "secondario", ("v3", "b"), ("vol", "secondary_in"), sezione="MS 32×3", **dati),
    ]
    return _grafo(pezzi, tubi, vol={"marca": "X", "modello": "Y"})


def test_fra_due_accessori_un_nipplo_fra_accessorio_e_tubo_un_raccordo(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    sezione_i = _sezione(componi_la_distinta(_gruppo_del_circolatore(), regole, *nomi), "I")
    # Nippli: VOL-01–VI-01, VI-01–CIR-01, CIR-01–VI-02 e VI-03–VOL-01.
    assert sezione_i[NIPPLO_1].quantita == 4
    # Raccordi: VI-02 e VI-03 verso il tubo del pavimento, che e' un confine.
    assert sezione_i[RACCORDO_1].quantita == 2
    assert sezione_i[ALL_ATTACCO].quantita == 2
    assert all("× 2" not in v.calcolo for v in sezione_i.values())


def test_il_circolatore_e_un_apparecchiatura_che_nove_c_compra_a_parte(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    distinta = componi_la_distinta(_gruppo_del_circolatore(), regole, *nomi)
    assert any(v.testo.startswith("Pompa di circolazione") for v in distinta.voci_della_sezione("A"))
    assert not [v for v in distinta.voci_della_sezione("I") if "ircolatore" in v.testo]


def test_tubo_vero_dove_il_contesto_lo_dice(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    """`"tubo": true`: VI-03 sta lontana dal volano; il nipplo diventa due raccordi."""
    sezione_i = _sezione(componi_la_distinta(_gruppo_del_circolatore(tubo=True), regole, *nomi), "I")
    assert sezione_i[NIPPLO_1].quantita == 3
    assert sezione_i[RACCORDO_1].quantita == 3
    assert sezione_i[ALL_ATTACCO].quantita == 3


def test_ogni_tratto_fra_due_pezzi_che_non_sono_tee_ha_almeno_un_tubo(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    """La deviatrice e la sfera sull'attacco del volano non si toccano: fra loro c'e' il tubo."""
    pezzi = [("dev", "diverting-valve-3way", "VD-01"), ("v1", "valve-isolation", "VI-01"),
             ("vol", "buffer-four-port", "VOL-01")]
    tubi = [
        _tubo("p1", "primario", ("dev", "out_a"), ("v1", "a"), sezione="MS 32×3"),
        _tubo("p2", "primario", ("v1", "b"), ("vol", "primary_in"), sezione="MS 32×3"),
    ]
    sezione_i = _sezione(componi_la_distinta(_grafo(pezzi, tubi), regole, *nomi), "I")
    assert sezione_i[NIPPLO_1].quantita == 1, "la sfera sull'attacco del volano"
    assert sezione_i[RACCORDO_1].quantita == 2, "il tubo fra deviatrice e sfera"


def test_il_tratto_esterno_comincia_dopo_giunto_e_riduzione(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    """Dalla pompa di calore: il giunto sull'attacco, la riduzione sul giunto senza nipplo,
    poi il tubo fino alla centrale anche se dopo c'e' un filtro filettato."""
    pezzi = [("pdc", "heat-pump-air-water", "GT-01"), ("ga", "flexible-joint", "GA-01"),
             ("rid", "pipe-reducer", "RID-01"), ("fil", "strainer", "FIL-01"), ("v1", "valve-isolation", "VI-01"),
             ("vol", "buffer-four-port", "VOL-01")]
    tubi = [
        _tubo("r1", "primario", ("pdc", "water_return"), ("ga", "a"), sezione="MS 32×3"),
        _tubo("r2", "primario", ("ga", "b"), ("rid", "a"), sezione="MS 32×3"),
        _tubo("r3", "primario", ("rid", "b"), ("fil", "a"), sezione="MS 32×3"),
        _tubo("r4", "primario", ("fil", "b"), ("v1", "a"), sezione="MS 32×3"),
        _tubo("r5", "primario", ("v1", "b"), ("vol", "primary_out"), sezione="MS 32×3"),
    ]
    grafo = _grafo(pezzi, tubi, pdc={"marca": "Shenling", "modello": "ThermaX R290"}, rid={"attacco": "1¼\"", "tubo": "1\""})
    distinta = componi_la_distinta(grafo, regole, *nomi)
    sezione_i = _sezione(distinta, "I")
    assert sezione_i[RACCORDO_1].quantita == 2, "la riduzione e il filtro sui due capi del tratto esterno"
    assert sezione_i[NIPPLO_1].quantita == 2, "filtro–sfera e sfera sul volano"
    assert ALL_ATTACCO not in sezione_i


def test_fra_due_pollici_diversi_il_nipplo_e_ridotto(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]]
) -> None:
    """Un accumulo con gli attacchi da 1¼" (`attacco`) e la sfera da 1": nipplo ridotto."""
    grafo = _gruppo_del_circolatore()
    grafo["components"][0]["properties"]["attacco"] = "1¼\""
    sezione_i = _sezione(componi_la_distinta(grafo, regole, *nomi), "I")
    ridotto = sezione_i["Nipplo ridotto 1¼\" × 1\" M × M"]
    assert ridotto.quantita == 2
    assert ridotto.prezzo is not None and ridotto.prezzo.codici == (("I78a", 1.0),)


@pytest.mark.parametrize("voce", ["air-vent", "pressure-gauge", "valve-safety"])
def test_gli_stacchi_non_portano_giunzioni(
    regole: RegoleDellaDistinta, nomi: tuple[dict[str, str], dict[str, str]], voce: str
) -> None:
    pezzi = [("vol", "buffer-four-port", "VOL-01"), ("tee", "tee-branch", "DER-01"), ("st", voce, "ST-01"),
             ("v1", "valve-isolation", "VI-01")]
    tubi = [
        _tubo("p1", "primario", ("vol", "primary_out"), ("tee", "a"), sezione="MS 32×3"),
        _tubo("p2", "primario", ("tee", "branch"), ("st", "a"), sezione="MS 32×3"),
        _tubo("p3", "primario", ("tee", "b"), ("v1", "a"), sezione="MS 32×3"),
    ]
    sezione_i = _sezione(componi_la_distinta(_grafo(pezzi, tubi), regole, *nomi), "I")
    assert sezione_i[ALL_ATTACCO].quantita == 1
    assert sezione_i[RACCORDO_1].quantita == 1
    assert not [t for t in sezione_i if t.startswith("Nipplo")]
