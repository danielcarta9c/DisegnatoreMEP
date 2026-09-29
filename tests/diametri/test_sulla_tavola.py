"""Il DN sulla tavola: un'etichetta per tratto, in linea con la tubazione (REL-007).

Sulle sei tavole approvate, eseguite dai loro piani con i dati di prova:

- **un'etichetta per tratto** (I-143): ogni tratto che porta il DN ne ha una, e una
  sola, e nessuna nomina un tratto che non lo porta — il preflight non ha niente da
  dire;
- **in linea e addosso** (I-152): ogni etichetta sta, allo stacco dichiarato, lungo
  un rettilineo del proprio tratto; sulla tavola 1 la mandata ha il tag sopra e il
  ritorno sotto (I-156);
- **non tocca niente**: simboli, sigle, altre etichette, tabella, altre linee;
- **il disegno non si muove**: simboli, tratte e sigle sono quelli della stessa
  tavola senza la richiesta dei diametri, che non porta ne' etichette ne' la riga
  della legenda;
- **il DXF** le porta uguali all'SVG, sul loro layer, e le verticali girate;
- **deterministico**.
"""

from collections.abc import Callable
from dataclasses import dataclass

import ezdxf
import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.diametri.tratti import TrattoDelDiametro, tratti_da_etichettare
from disegnatore_mep.graphics.dxf import LAYER_DIAMETRI, write_dxf
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import render_sheet
from disegnatore_mep.layout.diametri import STACCO_DALLA_LINEA_MM, riquadro_del_diametro
from disegnatore_mep.layout.geometry import SheetGeometry, zona_della_tabella
from disegnatore_mep.layout.labels import text_width_mm
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.piano.esecutore import EsitoDelPiano, esegui_piano
from disegnatore_mep.piano.formato import carica_piano

from .conftest import IMPIANTI, NAMING, grafo_e_piano

Box = tuple[float, float, float, float]


@dataclass(frozen=True)
class Tavola:
    modello: ProjectModel
    esito: EsitoDelPiano
    foglio: SheetGeometry
    senza: SheetGeometry
    tratti: tuple[TrattoDelDiametro, ...]


_TAVOLE: dict[str, Tavola] = {}


@pytest.fixture
def tavola(
    modello: Callable[..., ProjectModel], catalogo: ComponentRegistry, simboli: SymbolRegistry
) -> Callable[[str], Tavola]:
    def esegui(impianto: str) -> Tavola:
        if impianto not in _TAVOLE:
            _, piano = grafo_e_piano(impianto)
            con = modello(impianto)
            esito = esegui_piano(con, carica_piano(piano), catalogo, simboli, NAMING)
            senza = esegui_piano(
                modello(impianto, con_la_richiesta=False), carica_piano(piano), catalogo, simboli, NAMING
            )
            assert esito.disegno is not None and senza.disegno is not None
            _TAVOLE[impianto] = Tavola(
                modello=con,
                esito=esito,
                foglio=esito.disegno.sheets[0],
                senza=senza.disegno.sheets[0],
                tratti=tratti_da_etichettare(con, catalogo),
            )
        return _TAVOLE[impianto]

    return esegui


def _sovrapposti(a: Box, b: Box) -> bool:
    return a[0] < b[2] - 1e-6 and b[0] < a[2] - 1e-6 and a[1] < b[3] - 1e-6 and b[1] < a[3] - 1e-6


def _segmenti(foglio: SheetGeometry, connessioni: frozenset[str] | None = None) -> list[Box]:
    """I tratti dritti delle linee: di un tratto, o di tutti gli altri."""
    trovati: list[Box] = []
    for route in foglio.routes:
        proprio = bool(route.connection_ids) and set(route.connection_ids) <= (connessioni or set())
        if connessioni is not None and not proprio:
            continue
        for polilinea in route.segments:
            for a, b in zip(polilinea, polilinea[1:], strict=False):
                trovati.append(
                    (min(a.x_mm, b.x_mm), min(a.y_mm, b.y_mm), max(a.x_mm, b.x_mm), max(a.y_mm, b.y_mm))
                )
    return trovati


@pytest.mark.parametrize("impianto", IMPIANTI)
def test_un_etichetta_per_tratto(impianto: str, tavola: Callable[[str], Tavola]) -> None:
    t = tavola(impianto)
    assert t.tratti, "i dati di prova danno il DN a qualche tratto"
    per_tratto = {item.connection_ids: 0 for item in t.tratti}
    for etichetta in t.foglio.diametri:
        chiave = frozenset(etichetta.connection_ids)
        assert chiave in per_tratto, etichetta
        per_tratto[chiave] += 1
    # REL-008 (I-161, I-162): un tratto di strada principale ha la sua etichetta,
    # accanto alla linea o — ultima spiaggia — staccata con freccia; quello di una
    # strada secondaria ne ha al piu' una, e dove non c'e' posto si sacrifica.
    for item in t.tratti:
        quante = per_tratto[item.connection_ids]
        assert quante == 1 if item.strada_principale else quante <= 1, (item.capi, quante)
    staccate = [e for e in t.foglio.diametri if e.richiamo_da is not None]
    principali = {item.connection_ids for item in t.tratti if item.strada_principale}
    assert all(frozenset(e.connection_ids) in principali for e in staccate)
    scritte = {item.connection_ids: item.scritta for item in t.tratti}
    assert all(e.testo == scritte[frozenset(e.connection_ids)] for e in t.foglio.diametri)
    assert not [r.code for r in t.esito.rilievi if r.code.startswith("DIAMETER_")]


@pytest.mark.parametrize("impianto", IMPIANTI)
def test_in_linea_con_la_tubazione_e_addosso(impianto: str, tavola: Callable[[str], Tavola]) -> None:
    """Ogni etichetta ha un rettilineo del suo tratto parallelo e allo stacco
    dichiarato, e ci sta tutta dentro in lunghezza."""
    t = tavola(impianto)
    corpo = t.esito.frame.standard.text_small_mm
    for etichetta in t.foglio.diametri:
        if etichetta.richiamo_da is not None:
            continue  # staccata con freccia (I-162): la misura e' in tests/scritte
        box = riquadro_del_diametro(etichetta, corpo)
        propri = _segmenti(t.foglio, frozenset(etichetta.connection_ids))
        trovato = False
        for linea in propri:
            orizzontale = linea[1] == linea[3]
            if orizzontale == etichetta.verticale:
                continue
            if orizzontale:
                distanza = min(abs(box[1] - linea[1]), abs(box[3] - linea[1]))
                dentro = linea[0] <= box[0] and box[2] <= linea[2]
            else:
                distanza = min(abs(box[0] - linea[0]), abs(box[2] - linea[0]))
                dentro = linea[1] <= box[1] and box[3] <= linea[3]
            if dentro and distanza == pytest.approx(STACCO_DALLA_LINEA_MM):
                trovato = True
        assert trovato, etichetta


def test_sulla_tavola_1_la_mandata_sopra_e_il_ritorno_sotto(tavola: Callable[[str], Tavola]) -> None:
    """I-156, sulla tavola 1: ogni etichetta orizzontale di una mandata sta sopra la
    sua linea, ogni etichetta di un ritorno sotto."""
    t = tavola("1")
    versi = {frozenset(route.connection_ids): route.supply for route in t.foglio.routes}
    corpo = t.esito.frame.standard.text_small_mm
    for etichetta in t.foglio.diametri:
        if etichetta.verticale or etichetta.richiamo_da is not None:
            continue
        box = riquadro_del_diametro(etichetta, corpo)
        mandata = next(
            verso for chiave, verso in versi.items() if chiave and chiave <= frozenset(etichetta.connection_ids)
        )
        linee = [
            linea[1]
            for linea in _segmenti(t.foglio, frozenset(etichetta.connection_ids))
            if linea[1] == linea[3] and linea[0] <= box[0] and box[2] <= linea[2]
        ]
        assert linee, etichetta
        if mandata:
            assert any(box[3] < y for y in linee), f"{etichetta.testo} non sta sopra la mandata"
        else:
            assert any(box[1] > y for y in linee), f"{etichetta.testo} non sta sotto il ritorno"


@pytest.mark.parametrize("impianto", IMPIANTI)
def test_non_tocca_niente(impianto: str, tavola: Callable[[str], Tavola]) -> None:
    t = tavola(impianto)
    corpo = t.esito.frame.standard.text_small_mm
    simboli = [(s.origin.x_mm, s.origin.y_mm, s.right_mm, s.bottom_mm) for s in t.foglio.symbols]
    sigle = [
        (x.anchor.x_mm, x.anchor.y_mm - corpo, x.anchor.x_mm + text_width_mm(x.text, corpo), x.anchor.y_mm)
        for x in t.foglio.labels
    ]
    tabella = [zona_della_tabella(t.foglio.tabella.riquadro, 0.0)] if t.foglio.tabella else []
    riquadri = [riquadro_del_diametro(e, corpo) for e in t.foglio.diametri]
    for indice, (box, etichetta) in enumerate(zip(riquadri, t.foglio.diametri, strict=True)):
        for altro in (*simboli, *sigle, *tabella):
            assert not _sovrapposti(box, altro), (etichetta.testo, altro)
        for altro in riquadri[indice + 1 :]:
            assert not _sovrapposti(box, altro), etichetta.testo
        propri = set(_segmenti(t.foglio, frozenset(etichetta.connection_ids)))
        for linea in _segmenti(t.foglio):
            if linea not in propri:
                assert not _sovrapposti(box, linea), (etichetta.testo, linea)


@pytest.mark.parametrize("impianto", IMPIANTI)
def test_il_disegno_non_si_muove_e_senza_richiesta_non_c_e_niente(
    impianto: str, tavola: Callable[[str], Tavola], simboli: SymbolRegistry
) -> None:
    t = tavola(impianto)
    assert t.foglio.symbols == t.senza.symbols
    assert t.foglio.routes == t.senza.routes
    assert t.foglio.labels == t.senza.labels
    assert t.foglio.legend == t.senza.legend and t.foglio.network_keys == t.senza.network_keys
    assert t.senza.diametri == [] and t.senza.note_della_legenda == []
    assert "diametri" not in t.senza.model_dump(mode="json")
    assert "note_della_legenda" not in t.senza.model_dump(mode="json")
    assert 'class="diameter"' not in render_sheet(t.senza, t.esito.frame, simboli)
    assert t.foglio.note_della_legenda, "con il DN la legenda lo spiega (I-155)"
    assert t.foglio.note_della_legenda[0].campione == "Øi"


@pytest.mark.parametrize("impianto", ("1", "5"))
def test_il_dxf_porta_le_stesse_etichette(
    impianto: str, tavola: Callable[[str], Tavola], simboli: SymbolRegistry, tmp_path
) -> None:  # type: ignore[no-untyped-def]
    t = tavola(impianto)
    altezza = t.esito.frame.standard.sheet_height_mm
    dxf = tmp_path / "tavola.dxf"
    write_dxf(t.foglio, t.esito.frame, simboli, dxf)
    sul_layer = [e for e in ezdxf.readfile(dxf).modelspace() if e.dxf.layer == LAYER_DIAMETRI]
    letti = sorted(
        (e.dxf.text, round(e.dxf.insert.x, 6), round(e.dxf.insert.y, 6), round(e.dxf.rotation, 6))
        for e in sul_layer
        if e.dxftype() == "TEXT"
    )
    # Un'etichetta staccata (I-162) porta anche il suo richiamo: una linea e una
    # freccia piena.
    staccate = sum(1 for e in t.foglio.diametri if e.richiamo_da is not None)
    assert sum(1 for e in sul_layer if e.dxftype() == "LINE") == staccate
    assert sum(1 for e in sul_layer if e.dxftype() == "SOLID") == staccate
    attesi = sorted(
        (e.testo, round(e.ancora.x_mm, 6), round(altezza - e.ancora.y_mm, 6), 90.0 if e.verticale else 0.0)
        for e in t.foglio.diametri
    )
    assert letti == attesi
    if impianto == "5":
        assert any(rotazione == 90.0 for *_, rotazione in letti), "la 5 ha etichette verticali"


@pytest.mark.parametrize("impianto", ("1", "6"))
def test_deterministico(
    impianto: str,
    modello: Callable[..., ProjectModel],
    catalogo: ComponentRegistry,
    simboli: SymbolRegistry,
) -> None:
    _, piano = grafo_e_piano(impianto)
    uscite = []
    for _ in range(2):
        esito = esegui_piano(modello(impianto), carica_piano(piano), catalogo, simboli, NAMING)
        assert esito.disegno is not None
        uscite.append(render_sheet(esito.disegno.sheets[0], esito.frame, simboli))
    assert uscite[0] == uscite[1]


@pytest.mark.parametrize("impianto", ("1", "5"))
def test_il_velo_della_verifica_non_copre_il_dn(
    impianto: str,
    modello: Callable[..., ProjectModel],
    catalogo: ComponentRegistry,
    simboli: SymbolRegistry,
) -> None:
    """Gli indirizzi della modalita' verifica (D-110) si posano dopo tutto il resto,
    e il DN fa parte del resto: non ci vanno sopra."""
    _, piano = grafo_e_piano(impianto)
    esito = esegui_piano(modello(impianto), carica_piano(piano), catalogo, simboli, NAMING, verifica=True)
    assert esito.disegno is not None
    foglio = esito.disegno.sheets[0]
    corpo = esito.frame.standard.text_small_mm
    assert foglio.diametri
    indirizzi = [
        (x.anchor.x_mm, x.anchor.y_mm - corpo, x.anchor.x_mm + text_width_mm(x.text, corpo), x.anchor.y_mm)
        for x in foglio.labels
        if x.role == "address"
    ]
    assert indirizzi
    for etichetta in foglio.diametri:
        box = riquadro_del_diametro(etichetta, corpo)
        assert not any(_sovrapposti(box, altro) for altro in indirizzi), etichetta.testo
