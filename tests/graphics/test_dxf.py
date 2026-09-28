"""La tavola in DXF (REL-004): la stessa tavola dell'SVG, che AutoCAD apre.

Il PO la giudica aprendola in AutoCAD (I-138); queste prove tengono su quello
che si misura senza AutoCAD: che i simboli cadano dove li mette la tavola —
ruotati e specchiati —, che le tratte siano quelle, sui layer delle loro reti e
con i loro colori, che i testi siano tarati, che il file sia valido per ezdxf e
che esca uguale byte per byte.
"""

import json
import math
from dataclasses import dataclass
from pathlib import Path

import ezdxf
import pytest
from ezdxf.math import Matrix44

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.cartiglio import (
    Cartiglio,
    CartiglioDellaTavola,
    valori_del_cartiglio,
)
from disegnatore_mep.graphics.dxf import (
    ALTEZZA_MAIUSCOLE_EM,
    DXF_VERSION,
    Polilinea,
    aci_vicino,
    corpo_del_simbolo,
    inserimento_del_simbolo,
    layer_della_rete,
    lineweight,
    nome_del_blocco,
    write_dxf,
)
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.graphics.sheet import _interrupted, sheet_marks
from disegnatore_mep.layout.geometry import Point, SheetGeometry
from disegnatore_mep.layout.legend import style_for
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.piano.esecutore import EsitoDelPiano, esegui_piano
from disegnatore_mep.piano.formato import carica_piano

ROOT = Path(__file__).resolve().parents[2]
SYMBOLS = ROOT / "assets" / "symbols"
CATALOG = ROOT / "examples" / "layout" / "catalog"
IMPIANTO_6 = ROOT / "docs" / "collaudi" / "REL-003" / "impianto-6"
APPROVATI = ROOT / "docs" / "collaudi" / "DRAW-018" / "prova-camera-pulita-2026-09-24"
DATI_DI_PROVA = ROOT / "docs" / "collaudi" / "REL-002" / "dati-di-prova.json"
MODELLO_CARTIGLIO = ROOT / "assets" / "cartigli" / "Cartiglio_NoveC_A3.json"
TOLLERANZA_MM = 1e-6


@pytest.fixture(scope="module")
def simboli() -> SymbolRegistry:
    return SymbolRegistry.from_directory(SYMBOLS)


def _esegui(grafo: Path, piano: Path, simboli: SymbolRegistry, con_i_dati: bool) -> tuple[ProjectModel, EsitoDelPiano]:
    documento = json.loads(grafo.read_text(encoding="utf-8"))
    if con_i_dati:
        dati = json.loads(DATI_DI_PROVA.read_text(encoding="utf-8"))
        documento["metadata"].update({**dati["tutti"], "sheet_number": "T6"})
    modello = ProjectModel.model_validate(documento)
    catalogo = ComponentRegistry.from_directory(CATALOG, symbols=simboli)
    esito = esegui_piano(modello, carica_piano(piano), catalogo, simboli, ROOT / "naming")
    assert esito.disegno is not None
    return modello, esito


@pytest.fixture(scope="module")
def impianto_6(simboli: SymbolRegistry) -> tuple[ProjectModel, EsitoDelPiano]:
    """La tavola di prova di REL-003, approvata (I-136): i cinque simboli nuovi."""
    return _esegui(
        IMPIANTO_6 / "grafo-completo-6.json", IMPIANTO_6 / "piano-6-a.json", simboli, True
    )


@dataclass(frozen=True)
class Scritto:
    target: Path
    foglio: SheetGeometry
    altezza: float
    """L'altezza del foglio: il DXF ha y in alto, la tavola in basso."""


@pytest.fixture(scope="module")
def dxf_6(
    impianto_6: tuple[ProjectModel, EsitoDelPiano],
    simboli: SymbolRegistry,
    tmp_path_factory: pytest.TempPathFactory,
) -> Scritto:
    modello, esito = impianto_6
    assert esito.disegno is not None
    foglio = esito.disegno.sheets[0]
    tavola = CartiglioDellaTavola(
        cartiglio=Cartiglio.da_file(MODELLO_CARTIGLIO),
        valori=valori_del_cartiglio(modello, foglio.sheet_id),
    )
    target = tmp_path_factory.mktemp("dxf") / "tavola.dxf"
    write_dxf(foglio, esito.frame, simboli, target, tavola)
    return Scritto(target, foglio, esito.frame.standard.sheet_height_mm)


def _nel_dxf(point: Point, altezza_foglio: float) -> tuple[float, float]:
    return point.x_mm, altezza_foglio - point.y_mm


# --- i simboli ----------------------------------------------------------------------


def test_ogni_giacitura_porta_le_porte_dove_le_porta_la_tavola(simboli: SymbolRegistry) -> None:
    """Il cuore dello scrittore: l'inserimento del blocco — punto, rotazione,
    specchio — riproduce la trasformazione di `Symbol.rotated`, su tutta la
    libreria e nelle otto giaciture (D-169). Se le porte cadono giuste, il
    corpo le segue: che corpo e porte girino insieme lo tiene `test_rotation.py`.
    """
    altezza_foglio = 297.0
    origine = Point(x_mm=137.5, y_mm=82.5)
    for simbolo in simboli.all():
        manifest = simbolo.manifest
        for gradi in manifest.allowed_rotations_deg:
            for specchiato in (False, True):
                girato = manifest.rotated(gradi, specchiato)
                dove = inserimento_del_simbolo(
                    origine, gradi, specchiato, manifest.width_mm, manifest.height_mm,
                    altezza_foglio,
                )
                matrice = Matrix44.chain(
                    Matrix44.scale(-1.0 if dove.specchiato else 1.0, 1.0, 1.0),
                    Matrix44.z_rotate(math.radians(dove.rotazione)),
                    Matrix44.translate(dove.x, dove.y, 0),
                )
                for porta in manifest.ports:
                    atteso = girato.port(porta.id)
                    x, y, _ = matrice.transform((porta.x_mm, -porta.y_mm, 0))
                    ex, ey = _nel_dxf(
                        Point(x_mm=origine.x_mm + atteso.x_mm, y_mm=origine.y_mm + atteso.y_mm),
                        altezza_foglio,
                    )
                    assert (round(x - ex, 9), round(y - ey, 9)) == (0, 0), (
                        manifest.id, gradi, specchiato, porta.id,
                    )


def test_ogni_simbolo_della_tavola_e_un_inserimento_del_suo_blocco(
    dxf_6: Scritto, simboli: SymbolRegistry
) -> None:
    doc = ezdxf.readfile(dxf_6.target)
    nomi = {nome_del_blocco(p.symbol_id) for p in dxf_6.foglio.symbols}
    inseriti = {
        (round(i.dxf.insert.x, 6), round(i.dxf.insert.y, 6), i.dxf.name): i
        for i in doc.modelspace().query("INSERT")
        if i.dxf.layer == "M-DIAG-EQPM" and i.dxf.name in nomi
    }
    assert len(inseriti) == len(dxf_6.foglio.symbols)
    for placed in dxf_6.foglio.symbols:
        manifest = simboli.get(placed.symbol_id).manifest
        dove = inserimento_del_simbolo(
            placed.origin, placed.rotation_deg, placed.specchiato,
            manifest.width_mm, manifest.height_mm, dxf_6.altezza,
        )
        chiave = (round(dove.x, 6), round(dove.y, 6), nome_del_blocco(placed.symbol_id))
        assert chiave in inseriti, placed.component_id
        inserito = inseriti[chiave]
        assert inserito.dxf.rotation == pytest.approx(dove.rotazione)
        assert (inserito.dxf.xscale < 0) == dove.specchiato, placed.component_id


def test_i_blocchi_hanno_nomi_che_autocad_accetta_e_la_descrizione_italiana(
    simboli: SymbolRegistry,
) -> None:
    for simbolo in simboli.all():
        nome = nome_del_blocco(simbolo.manifest.id)
        nomi = [nome] + [f"{nome}_{g.id.capitalize()}" for g in simbolo.manifest.upright_glyphs]
        for item in nomi:
            assert len(item) <= 31, item
            assert item.replace("_", "").isalnum() and item.isascii(), item


def test_nel_blocco_la_geometria_segue_l_inserimento(dxf_6: Scritto) -> None:
    """Layer 0, colore e spessore DaBlocco: l'aspetto lo decide l'inserimento
    (Autodesk, *Block Object Properties Reference*)."""
    doc = ezdxf.readfile(dxf_6.target)
    for blocco in doc.blocks:
        if not blocco.name.startswith("NoveC_"):
            continue
        assert blocco.block.dxf.description, blocco.name
        for entita in blocco:
            assert entita.dxf.layer == "0", (blocco.name, entita.dxftype())
            assert entita.dxf.color == 0, (blocco.name, entita.dxftype())  # DaBlocco


# --- le reti ------------------------------------------------------------------------


def test_le_tratte_sono_quelle_della_tavola_sul_layer_della_loro_rete(dxf_6: Scritto) -> None:
    doc = ezdxf.readfile(dxf_6.target)
    foglio, altezza = dxf_6.foglio, dxf_6.altezza
    scritte: dict[str, list[list[tuple[float, float]]]] = {}
    for polilinea in doc.modelspace().query("LWPOLYLINE"):
        scritte.setdefault(polilinea.dxf.layer, []).append(
            [(round(x, 6), round(y, 6)) for x, y in polilinea.get_points("xy")]
        )
    marks = sheet_marks(foglio)
    attese: dict[str, list[list[tuple[float, float]]]] = {}
    for indice, route in enumerate(foglio.routes):
        hops = [m.at for m in marks.hops if m.route_index == indice]
        for segment in route.segments:
            for piece in _interrupted(segment, hops):
                attese.setdefault(layer_della_rete(route.medium, route.supply), []).append(
                    [(round(p.x_mm, 6), round(altezza - p.y_mm, 6)) for p in piece]
                )
    for layer, pezzi in attese.items():
        assert sorted(scritte.get(layer, [])) == sorted(pezzi), layer


def test_i_layer_delle_reti_portano_colore_e_tratteggio_della_tavola(dxf_6: Scritto) -> None:
    """I-139: i colori sono gli RGB esatti della tavola; il tratteggio e' il
    suo, in millimetri."""
    doc = ezdxf.readfile(dxf_6.target)
    for route in dxf_6.foglio.routes:
        colore, tratto = style_for(route.medium, route.supply)
        layer = doc.layers.get(layer_della_rete(route.medium, route.supply))
        atteso = tuple(int(colore[i : i + 2], 16) for i in (1, 3, 5))
        assert tuple(layer.rgb) == atteso, layer.dxf.name
        assert layer.dxf.color == aci_vicino(atteso), "l'ACI di ripiego, non il 7"
        assert layer.dxf.lineweight == lineweight(0.35)
        if tratto == "none":
            assert layer.dxf.linetype == "Continuous"
        else:
            motivo = doc.linetypes.get(layer.dxf.linetype).simplified_line_pattern()
            assert tuple(motivo) == tuple(float(v) for v in tratto.split()), layer.dxf.name
        assert layer.description, layer.dxf.name


def test_le_frecce_sono_blocchi_sul_layer_della_rete(dxf_6: Scritto) -> None:
    """I-138: «con le frecce già incorporate»."""
    doc = ezdxf.readfile(dxf_6.target)
    reti = {layer_della_rete(r.medium, r.supply) for r in dxf_6.foglio.routes}
    frecce = [i for i in doc.modelspace().query("INSERT") if i.dxf.name == "NoveC_FlowArrow"]
    assert frecce
    assert {f.dxf.layer for f in frecce} <= reti | {"M-DIAG-EQPM", "M-ANNO-LEGN"}
    assert any(f.dxf.layer in reti for f in frecce)


# --- testi, cartiglio, presentazione -------------------------------------------------------


def test_i_testi_sono_tarati_sulle_maiuscole(dxf_6: Scritto) -> None:
    """AutoCAD misura l'altezza sulle maiuscole, l'SVG sul corpo: un testo della
    legenda da 1,8 mm di corpo e' alto 1,8 × 0,688 nel DXF."""
    doc = ezdxf.readfile(dxf_6.target)
    foglio = dxf_6.foglio
    legenda = [t for t in doc.modelspace().query("TEXT") if t.dxf.layer == "M-ANNO-LEGN"]
    assert legenda
    for testo in legenda:
        assert testo.dxf.height == pytest.approx(round(1.8 * ALTEZZA_MAIUSCOLE_EM, 4))
        assert testo.dxf.style == "NOVEC_ARIAL"
    nomi = {t.dxf.text for t in legenda}
    assert {entry.name for entry in foglio.legend} <= nomi


def test_il_cartiglio_sta_in_spazio_carta_con_i_suoi_testi_e_il_logo_accanto(
    dxf_6: Scritto,
) -> None:
    """Nello spazio modello resta lo schema: si copia in un altro disegno senza
    portarsi dietro squadratura e cartiglio."""
    doc = ezdxf.readfile(dxf_6.target)
    target = dxf_6.target
    carta = doc.paperspace("A2")
    assert not [e for e in doc.modelspace() if e.dxf.layer == "G-ANNO-TTLB"]
    testi = {t.dxf.text: t for t in carta.query("TEXT") if t.dxf.layer == "G-ANNO-TTLB"}
    assert "Condominio di prova" in testi
    assert testi["Condominio di prova"].dxf.style == "NOVEC_ARIAL_GRASSETTO"
    assert "T6" in testi
    assert not doc.modelspace().query("IMAGE")
    immagini = carta.query("IMAGE")
    assert len(immagini) == 1
    nome = immagini[0].image_def.dxf.filename
    assert "/" not in nome and "\\" not in nome, "il logo si cerca accanto al DXF"
    logo = target.parent / nome
    assert logo.read_bytes() == Cartiglio.da_file(MODELLO_CARTIGLIO).logo_jpeg


def test_il_file_e_valido_in_millimetri_con_la_presentazione_1_a_1(dxf_6: Scritto) -> None:
    doc = ezdxf.readfile(dxf_6.target)
    assert doc.dxfversion == "AC1027" and DXF_VERSION == "R2013"
    assert doc.header["$INSUNITS"] == 4 and doc.header["$MEASUREMENT"] == 1
    auditor = doc.audit()
    assert not auditor.has_errors, [str(e) for e in auditor.errors]
    assert doc.layouts.names() == ["Model", "A2"]
    finestre = [v for v in doc.paperspace("A2").query("VIEWPORT") if v.dxf.id != 1]
    assert len(finestre) == 1
    finestra = finestre[0]
    assert finestra.dxf.view_height == pytest.approx(finestra.dxf.height)  # 1:1
    assert finestra.dxf.flags & 16384, "la finestra ha lo zoom bloccato"
    assert doc.layers.get(finestra.dxf.layer).dxf.plot == 0
    assert doc.header["$TILEMODE"] == 0, "il file si apre sulla presentazione"
    assert doc.layouts.active_layout().name == "A2"


def test_ogni_entita_sta_su_un_layer_definito(dxf_6: Scritto) -> None:
    """ezdxf mette la finestra principale su un layer `VIEWPORTS` che non
    definisce; l'audit non lo vede, il giro con l'ODA File Converter si'."""
    doc = ezdxf.readfile(dxf_6.target)
    definiti = {layer.dxf.name for layer in doc.layers}
    usati = {
        e.dxf.layer
        for spazio in (doc.modelspace(), doc.paperspace("A2"), *doc.blocks)
        for e in spazio
        if e.dxf.hasattr("layer")
    }
    assert usati <= definiti, usati - definiti


def test_ogni_colore_esatto_ha_il_suo_ripiego(dxf_6: Scritto) -> None:
    """Chi non legge il colore esatto (420) legge l'indice (62): accanto a ogni
    RGB c'e' il colore d'indice piu' vicino, mai il 7 ne' «DaLayer»."""
    doc = ezdxf.readfile(dxf_6.target)
    colorati = [
        e for spazio in (doc.modelspace(), doc.paperspace("A2")) for e in spazio if e.rgb is not None
    ] + [layer for layer in doc.layers if layer.rgb is not None]
    assert colorati
    for oggetto in colorati:
        assert oggetto.dxf.color == aci_vicino(tuple(oggetto.rgb)), oggetto


def test_l_aci_di_ripiego_e_il_piu_vicino_e_non_e_il_7() -> None:
    assert aci_vicino((255, 0, 0)) == 1
    assert aci_vicino((0, 0, 255)) == 5
    assert aci_vicino((255, 255, 255)) == 255, "il 7 e' nero su fondo bianco"
    assert aci_vicino((192, 57, 43)) == 22, "come l'ODA File Converter"


def test_il_dxf_esce_uguale_byte_per_byte(
    impianto_6: tuple[ProjectModel, EsitoDelPiano], simboli: SymbolRegistry, tmp_path: Path
) -> None:
    _, esito = impianto_6
    assert esito.disegno is not None
    foglio = esito.disegno.sheets[0]
    primo = write_dxf(foglio, esito.frame, simboli, tmp_path / "a" / "t.dxf")[0]
    secondo = write_dxf(foglio, esito.frame, simboli, tmp_path / "b" / "t.dxf")[0]
    assert primo.read_bytes() == secondo.read_bytes()


def test_le_classi_del_file_sono_in_ordine_di_nome(dxf_6: Scritto) -> None:
    """ezdxf registra le classi scorrendo un insieme: senza riordinarle, la
    sezione CLASSES cambiava da un processo all'altro (`PYTHONHASHSEED`) e lo
    stesso piano dava due file diversi. La prova byte per byte qui sopra, che
    scrive due volte nello stesso processo, non lo vede."""
    testo = dxf_6.target.read_text(encoding="utf-8")
    sezione = testo.split("CLASSES", 1)[1].split("ENDSEC", 1)[0]
    righe = [riga.strip() for riga in sezione.splitlines()]
    classi = [
        (righe[i + 2], righe[i + 4])
        for i in range(len(righe) - 4)
        if righe[i] == "CLASS" and righe[i + 1] == "1"
    ]
    assert len(classi) > 5
    assert classi == sorted(classi)


def test_senza_cartiglio_la_riserva_e_la_bozza_come_nell_svg(
    simboli: SymbolRegistry, tmp_path: Path
) -> None:
    _, esito = _esegui(
        APPROVATI / "grafo-completo-1.json", APPROVATI / "piano-completo-1.json", simboli, False
    )
    assert esito.disegno is not None
    scritti = write_dxf(esito.disegno.sheets[0], esito.frame, simboli, tmp_path / "t1.dxf")
    assert [p.name for p in scritti] == ["t1.dxf"], "senza cartiglio non c'e' logo"
    doc = ezdxf.readfile(scritti[0])
    testi = {t.dxf.text for t in doc.paperspace("A3").query("TEXT")}
    assert "BOZZA — cartiglio non compilato" in testi
    assert not [e for e in doc.modelspace() if e.dxf.layer == "G-ANNO-TTLB"]
    assert not doc.audit().has_errors


# --- i corpi SVG ---------------------------------------------------------------------


def test_un_rettangolo_arrotondato_ha_gli_angoli_ad_arco() -> None:
    corpo = corpo_del_simbolo('<rect x="0" y="0" width="10" height="20" rx="2"/>')
    (polilinea,) = [p for p in corpo.primitive if isinstance(p, Polilinea)]
    assert polilinea.chiusa
    curve = [b for _, _, b in polilinea.vertici if b]
    assert len(curve) == 4
    # Un quarto di giro in senso orario a vederlo: nel DXF, y in alto, e' orario.
    assert all(b == pytest.approx(-math.tan(math.pi / 8)) for b in curve)


def test_lo_scavallo_si_gonfia_a_destra() -> None:
    """L'arco SVG da sopra a sotto con bandiera 1 passa per destra: nel DXF la
    curvatura e' oraria, cioe' negativa."""
    corpo = corpo_del_simbolo('<path d="M5 0 A2.5 2.5 0 0 1 5 5"/>')
    (polilinea,) = corpo.primitive
    assert isinstance(polilinea, Polilinea)
    (x0, y0, b0), (x1, y1, _) = polilinea.vertici
    assert (x0, y0, x1, y1) == (5, 0, 5, -5)
    assert b0 == pytest.approx(-1.0)


def test_un_elemento_che_il_dxf_non_sa_scrivere_si_ferma() -> None:
    with pytest.raises(ValueError, match="non sa scrivere"):
        corpo_del_simbolo('<text x="0" y="0">P</text>')


def test_ogni_corpo_della_libreria_si_legge(simboli: SymbolRegistry) -> None:
    for simbolo in simboli.all():
        corpo = corpo_del_simbolo(simbolo.body)
        assert corpo.primitive, simbolo.manifest.id
        assert set(corpo.glifi) == {g.id for g in simbolo.manifest.upright_glyphs}
