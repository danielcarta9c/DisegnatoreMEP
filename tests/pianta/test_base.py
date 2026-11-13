"""La base standard della tavola MEP (REL-026, C-3): una sola, qualunque fosse l'ingresso.

Muri grigio chiaro con gli angoli raccordati e un contorno solo, finestre celesti, porte a
tratto fine, balconi, nomi dei locali con i mq; lo sfondo d'origine fuori dalla tavola
quando la base e' ridisegnata."""

from __future__ import annotations

import json
import zlib
from pathlib import Path
from typing import Any

import pytest

from disegnatore_mep.graphics.pdf import svg_in_pdf
from disegnatore_mep.pianta import base
from disegnatore_mep.pianta.base import (
    CELESTE_DELLE_FINESTRE,
    GRIGIO_DEI_MURI,
    allungamenti,
    aperture_della_base,
    area_con_segno,
    dentro,
    locali_con_nome,
    muri_della_base,
    sagome_dei_muri,
    unione_rettilinea,
)
from disegnatore_mep.pianta.comando import Esito, disegna_la_pianta
from disegnatore_mep.pianta.modello import Pianta
from disegnatore_mep.pianta.tavola import (
    LAYER_APERTURE,
    LAYER_BALCONI,
    LAYER_FINESTRE,
    LAYER_MURI,
    Arco,
    Area,
    Immagine,
    Linea,
    componi,
    scrivi_svg,
)

from .conftest import CASI


def _pianta(**campi: Any) -> Pianta:
    return Pianta.model_validate({"versione": "1.0.0", **campi})


def _muro(id_: str, da: tuple[float, float], a: tuple[float, float], spessore: float = 0.3,
          tipo: str = "perimetrale") -> dict[str, Any]:
    return {"id": id_, "da": list(da), "a": list(a), "spessore": spessore, "tipo": tipo}


def _identita(x: float, y: float) -> tuple[float, float]:
    return (x, y)


def _pieno(primitive: list[Any], punto: tuple[float, float]) -> bool:
    aree = [p for p in primitive if isinstance(p, Area) and p.layer == LAYER_MURI]
    return any(sum(dentro(punto, anello) for anello in (a.punti, *a.buchi)) % 2 == 1 for a in aree)


# --- i raccordi -------------------------------------------------------------------------------


def test_l_angolo_si_chiude_senza_sporgere() -> None:
    """Due perimetrali da 30 cm con gli assi che si incontrano: un contorno solo, a L, con
    lo spigolo di fuori a mezzo spessore dall'asse."""
    pianta = _pianta(muri=[_muro("nord", (0, 0), (4, 0)), _muro("ovest", (0, 0), (0, 3))])
    assert allungamenti(pianta) == {"nord": (0.15, 0.0), "ovest": (0.15, 0.0)}
    gruppi, storti = sagome_dei_muri(pianta)
    assert storti == [] and len(gruppi) == 1
    anello, buchi = gruppi[0]
    assert buchi == [] and len(anello) == 6
    assert min(x for x, _ in anello) == pytest.approx(-0.15) and min(y for _, y in anello) == pytest.approx(-0.15)
    assert max(x for x, _ in anello) == pytest.approx(4.0) and max(y for _, y in anello) == pytest.approx(3.0)


def test_l_angolo_con_spessori_diversi() -> None:
    """Un 30 e un 45: ognuno arriva alla faccia lontana dell'altro, e l'angolo e' pieno."""
    pianta = _pianta(muri=[_muro("nord", (0, 0), (4, 0), 0.3), _muro("ovest", (0, 0), (0, 3), 0.45, "portante")])
    assert allungamenti(pianta)["nord"] == (pytest.approx(0.225), 0.0)
    assert allungamenti(pianta)["ovest"] == (pytest.approx(0.15), 0.0)
    ((anello, _),), _ = sagome_dei_muri(pianta)
    assert len(anello) == 6
    assert (pytest.approx(-0.225), pytest.approx(-0.15)) in [(x, y) for x, y in anello]


def test_la_t_della_tramezza_arriva_alla_faccia_lontana_e_non_oltre() -> None:
    pianta = _pianta(muri=[_muro("nord", (0, 0), (6, 0)), _muro("t", (3, 0), (3, 3), 0.1, "tramezza")])
    assert allungamenti(pianta)["t"] == (pytest.approx(0.15), 0.0)
    ((anello, buchi),), _ = sagome_dei_muri(pianta)
    assert buchi == [] and len(anello) == 8
    assert min(y for _, y in anello) == pytest.approx(-0.15)


def test_un_capo_libero_finisce_dov_e() -> None:
    """Una spalletta: il capo che non arriva su un altro muro non si allunga."""
    pianta = _pianta(muri=[_muro("nord", (0, 0), (6, 0)), _muro("s", (3, 0), (3, 1.2), 0.1, "tramezza")])
    assert allungamenti(pianta)["s"][1] == 0.0
    ((anello, _),), _ = sagome_dei_muri(pianta)
    assert max(y for _, y in anello) == pytest.approx(1.2)


def test_un_capo_a_pochi_centimetri_si_raccorda_lo_stesso() -> None:
    """Chi trascrive a mano non mette i capi al millimetro: entro 5 cm il raccordo c'e'."""
    pianta = _pianta(muri=[_muro("nord", (0, 0), (6, 0)), _muro("t", (3, 0.18), (3, 3), 0.1, "tramezza")])
    assert allungamenti(pianta)["t"][0] == pytest.approx(0.33)
    ((anello, _),), _ = sagome_dei_muri(pianta)
    assert len(anello) == 8


def test_quattro_muri_chiusi_sono_un_anello_con_un_buco() -> None:
    pianta = _pianta(muri=[
        _muro("n", (0, 0), (5, 0)), _muro("s", (0, 4), (5, 4)),
        _muro("o", (0, 0), (0, 4)), _muro("e", (5, 0), (5, 4)),
    ])
    ((anello, buchi),), _ = sagome_dei_muri(pianta)
    assert len(anello) == 4 and len(buchi) == 1 and len(buchi[0]) == 4
    assert area_con_segno(anello) == pytest.approx(5.3 * 4.3)
    assert area_con_segno(buchi[0]) == pytest.approx(-4.7 * 3.7)
    primitive = muri_della_base(pianta, _identita)
    aree = [p for p in primitive if isinstance(p, Area)]
    contorni = [p for p in primitive if isinstance(p, Linea)]
    assert len(aree) == 1 and len(aree[0].buchi) == 1 and aree[0].colore == GRIGIO_DEI_MURI
    assert len(contorni) == 2  # il contorno di fuori e quello di dentro: nessuna linea dei rettangoli
    assert _pieno(primitive, (0.0, 2.0)) and not _pieno(primitive, (2.5, 2.0))


def test_le_aperture_tagliano_il_muro_e_la_finestra_e_celeste() -> None:
    pianta = _pianta(
        muri=[_muro("n", (0, 0), (5, 0))],
        aperture=[{"id": "f1", "muro": "n", "centro": [2.5, 0.0], "larghezza": 1.2, "tipo": "finestra"}],
    )
    gruppi, _ = sagome_dei_muri(pianta)
    assert len(gruppi) == 2
    primitive = muri_della_base(pianta, _identita)
    assert not _pieno(primitive, (2.5, 0.0)) and _pieno(primitive, (1.0, 0.0))
    disegno, tratti = aperture_della_base(pianta, _identita, 1.0)
    vano = [p for p in disegno if isinstance(p, Area)]
    assert len(vano) == 1 and vano[0].layer == LAYER_FINESTRE and vano[0].colore == CELESTE_DELLE_FINESTRE
    assert {p.layer for p in disegno} == {LAYER_FINESTRE}
    assert len(tratti) == 3


def test_le_sagome_storte_si_disegnano_una_per_una() -> None:
    pianta = _pianta(sagome_muri=[[[0, 0], [2, 0], [2, 0.3], [0, 0.3]], [[2, 0], [3, 1], [2.8, 1.2], [1.8, 0.2]]])
    gruppi, storti = sagome_dei_muri(pianta)
    assert len(gruppi) == 1 and len(storti) == 1


def test_l_unione_di_due_rettangoli_che_si_toccano_d_angolo() -> None:
    """Due celle che si toccano solo nello spigolo: due anelli, che non si attraversano."""
    anelli = unione_rettilinea([[(0, 0), (1, 0), (1, 1), (0, 1)], [(1, 1), (2, 1), (2, 2), (1, 2)]])
    assert len(anelli) == 2 and all(len(a) == 4 for a in anelli)
    assert all(area_con_segno(a) > 0 for a in anelli)


# --- le porte -----------------------------------------------------------------------------------


def _porta(**campi: Any) -> Pianta:
    return _pianta(
        muri=[_muro("t", (0, 0), (4, 0), 0.1, "tramezza")],
        aperture=[{"id": "p1", "muro": "t", "centro": [2.0, 0.0], "larghezza": 0.8, "tipo": "porta", **campi}],
    )


def test_la_cerniera_sta_dove_la_pianta_dice() -> None:
    for cerniera, x in (("sinistra", 1.6), ("destra", 2.4)):
        disegno, _ = aperture_della_base(_porta(apre_verso="sotto", cerniera=cerniera), _identita, 1.0)
        (arco,) = [p for p in disegno if isinstance(p, Arco)]
        assert arco.centro[0] == pytest.approx(x), cerniera
        assert arco.centro[1] == pytest.approx(0.05)  # dalla parte in cui apre
        assert {p.layer for p in disegno} == {LAYER_APERTURE}


def test_la_porta_a_due_ante_e_la_scorrevole() -> None:
    disegno, _ = aperture_della_base(_porta(anta="doppia", apre_verso="sotto"), _identita, 1.0)
    assert len([p for p in disegno if isinstance(p, Arco)]) == 2
    disegno, _ = aperture_della_base(_porta(anta="scorrevole"), _identita, 1.0)
    assert not [p for p in disegno if isinstance(p, Arco)] and len(disegno) == 1


def test_la_porta_senza_verso_si_disegna_chiusa() -> None:
    """Uno schizzo o un catastale non disegnano il verso (camera pulita di REL-026): l'anta sta
    chiusa nel vano, un tratto solo. Un arco da una parte a caso sembrerebbe un dato letto."""
    for campi in ({}, {"anta": "doppia"}, {"cerniera": "destra"}):
        disegno, tratti = aperture_della_base(_porta(**campi), _identita, 1.0)
        assert not [p for p in disegno if isinstance(p, Arco)], campi
        (anta,) = disegno
        assert isinstance(anta, Linea) and anta.layer == LAYER_APERTURE
        assert [tuple(q) for q in anta.punti] == [pytest.approx((1.6, 0.0)), pytest.approx((2.4, 0.0))]
        assert tratti


def test_la_cerniera_deve_stare_lungo_il_muro() -> None:
    with pytest.raises(ValueError, match="cerniera"):
        _porta(cerniera="sopra")
    with pytest.raises(ValueError, match="solo delle porte"):
        _pianta(
            muri=[_muro("t", (0, 0), (4, 0))],
            aperture=[{"id": "f", "muro": "t", "centro": [2.0, 0.0], "larghezza": 1, "tipo": "finestra",
                       "anta": "doppia"}],
        )


# --- balconi e locali --------------------------------------------------------------------------


def test_il_balcone_ha_il_contorno_il_nome_e_i_mq() -> None:
    pianta = _pianta(
        muri=[_muro("n", (0, 0), (5, 0))],
        stanze=[{"id": "camera", "nome": "Camera", "poligono": [[0, 0.15], [3, 0.15], [3, 3.15], [0, 3.15]]}],
        balconi=[{"id": "b", "nome": "Terrazzo", "poligono": [[0, -1.65], [4, -1.65], [4, -0.15], [0, -0.15]]}],
    )
    disegno, _ = aperture_della_base(pianta, _identita, 1.0)
    (contorno,) = [p for p in disegno if p.layer == LAYER_BALCONI]
    assert isinstance(contorno, Linea) and len(contorno.punti) == 5
    assert [(chi, parti) for chi, parti, _ in locali_con_nome(pianta)] == [
        ("stanza camera", ("Camera", "9 m²")), ("balcone b", ("Terrazzo", "6 m²")),
    ]


def test_il_balcone_non_e_l_interno() -> None:
    """Un balcone non e' una stanza: per l'instradatore resta esterno, e fuori si passa solo
    nelle zone esterne che il progettista dichiara."""
    from disegnatore_mep.pianta.griglia import costruisci_la_griglia

    pianta = _pianta(
        muri=[_muro("n", (0, 0), (5, 0)), _muro("s", (0, 3), (5, 3)), _muro("o", (0, 0), (0, 3)),
              _muro("e", (5, 0), (5, 3))],
        stanze=[{"id": "c", "nome": "Camera", "poligono": [[0.15, 0.15], [4.85, 0.15], [4.85, 2.85], [0.15, 2.85]]}],
        balconi=[{"id": "b", "poligono": [[0, -1.65], [4, -1.65], [4, -0.15], [0, -0.15]]}],
    )
    griglia = costruisci_la_griglia(pianta)
    k = griglia.nodo(round(2.0 / griglia.passo) - griglia.i0, round(-1.0 / griglia.passo) - griglia.j0)
    assert griglia.esterno[k] and not griglia.stanza[k]


# --- la tavola ----------------------------------------------------------------------------------


def test_lo_sfondo_resta_fuori_dalla_tavola_quando_la_base_e_ridisegnata(tmp_path: Path) -> None:
    """La planimetria d'origine serve al controllo a vista: sulla tavola consegnata c'e' la
    base standard. Il progettista la puo' chiedere (`sulla_tavola`: il caso del corridoio)."""
    dati = json.loads(CASI["corridoio"].read_text(encoding="utf-8"))
    dati["sfondo"].pop("sulla_tavola")
    variante = tmp_path / "corridoio.json"
    variante.write_text(json.dumps(dati), encoding="utf-8")
    (tmp_path / "sfondo-corridoio.jpg").write_bytes((CASI["corridoio"].parent / "sfondo-corridoio.jpg").read_bytes())
    esito = disegna_la_pianta(variante, tmp_path / "out", None, dxf=False, png=False)
    assert not any(isinstance(p, Immagine) for p in esito.tavola.primitive)
    assert not any(p.name.endswith(".jpg") for p in esito.file)
    assert Pianta.model_validate({**dati, "muri": [], "aperture": []}).sfondo_sulla_tavola


def test_lo_sfondo_chiesto_sulla_tavola_c_e(esiti: dict[str, Esito]) -> None:
    esito = esiti["corridoio"]
    assert esito.pianta.sfondo is not None and esito.pianta.sfondo.sulla_tavola
    assert any(isinstance(p, Immagine) for p in esito.tavola.primitive)


def test_lo_sfondo_puo_essere_un_pdf_con_la_sua_taratura() -> None:
    pianta = _pianta(sfondo={"file": "planimetria.pdf", "pagina": 2, "dpi": 200, "px_per_m": 157.48,
                             "origine_px": [100, 50], "rotazione": 90.0 - 88.5})
    assert pianta.sfondo is not None
    x, y = pianta.sfondo.in_pixel(1.0, 0.0)
    assert x > 100 + 157 and y > 50  # girata in senso orario: l'asse x scende un poco
    assert not pianta.sfondo_sulla_tavola or not pianta.base_ridisegnata


def test_la_base_standard_sulla_tavola(esiti: dict[str, Esito]) -> None:
    """Sull'appartamento d'esempio: i muri grigio chiaro sono pochi gruppi (non un rettangolo
    per tratto), le finestre celesti sul loro layer, i nomi dei locali in mezzatinta."""
    tavola = esiti["appartamento"].tavola
    muri = [p for p in tavola.primitive if isinstance(p, Area) and p.layer == LAYER_MURI]
    assert muri and {p.colore for p in muri} == {GRIGIO_DEI_MURI}
    assert len(muri) < len(esiti["appartamento"].pianta.muri)
    finestre = [p for p in tavola.primitive if isinstance(p, Area) and p.layer == LAYER_FINESTRE]
    assert len(finestre) == len([a for a in esiti["appartamento"].pianta.aperture if a.tipo == "finestra"])
    nomi: dict[str, list[str]] = {}
    for chi, s in tavola.scritte:
        if chi.startswith("stanza"):
            nomi.setdefault(chi, []).append(s.testo)
    # Ogni locale ha i suoi mq: su una riga, o su due dove una linea gli toglie il posto.
    assert nomi and all("m²" in " ".join(righe) for righe in nomi.values())
    assert any(len(righe) == 2 for righe in nomi.values())


def test_la_base_e_deterministica(esiti: dict[str, Esito]) -> None:
    esito = esiti["sagome"]
    rifatta = componi(esito.pianta, esito.percorsi, esito.lunghezze, [], [], None)
    assert scrivi_svg(rifatta) == scrivi_svg(componi(esito.pianta, esito.percorsi, esito.lunghezze, [], [], None))


def test_nel_dxf_i_layer_della_base_sono_distinti(esiti: dict[str, Esito]) -> None:
    ezdxf = pytest.importorskip("ezdxf")
    esito = esiti["appartamento"]
    documento = ezdxf.readfile(next(p for p in esito.file if p.suffix == ".dxf"))
    per_layer: dict[str, set[str]] = {}
    for entita in documento.modelspace():
        per_layer.setdefault(entita.dxf.layer, set()).add(entita.dxftype())
    assert "HATCH" in per_layer["A-WALL"] and "LWPOLYLINE" in per_layer["A-WALL"]
    assert "HATCH" in per_layer["A-GLAZ"]
    assert {"ARC", "LWPOLYLINE"} <= per_layer["A-DOOR"]
    assert any(t in per_layer["A-AREA-IDEN"] for t in ("TEXT", "MTEXT"))


def test_il_pdf_incorpora_un_png(tmp_path: Path) -> None:
    """Il PDF del motore incorpora anche un PNG pieno, coi suoi IDAT come sono (il
    predittore PNG del FlateDecode): l'immagine della pagina d'origine nel controllo a vista."""
    from disegnatore_mep.skill import _png

    righe = [bytes([(x * 7 + y * 3) % 256 for x in range(12) for _ in range(3)]) for y in range(9)]
    (tmp_path / "prova.png").write_bytes(_png(12, 9, righe))
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="40mm" height="30mm" viewBox="0 0 40 30">'
           '<image href="prova.png" x="0" y="0" width="40" height="30" preserveAspectRatio="none"/></svg>')
    dati = svg_in_pdf(svg, tmp_path).dati
    assert b"/Predictor 15 /Colors 3" in dati and b"/Width 12 /Height 9" in dati
    inizio = dati.index(b"stream\n", dati.index(b"/Predictor 15")) + 7
    flusso = zlib.decompress(dati[inizio : dati.index(b"\nendstream", inizio)])
    assert len(flusso) == 9 * (1 + 12 * 3)


def test_il_modulo_della_base_ha_i_colori_in_un_punto_solo() -> None:
    """Le costanti dei colori sono in `base.py`; la tavola usa lo stesso grigio per i nomi."""
    from disegnatore_mep.pianta import tavola

    assert tavola.COLORE_STANZE == base.GRIGIO_DEI_LOCALI
    sorgente = Path(tavola.__file__).read_text(encoding="utf-8")
    for colore in (base.GRIGIO_DEI_MURI, base.CELESTE_DELLE_FINESTRE, base.LINEA_DELLE_PORTE):
        assert colore not in sorgente
