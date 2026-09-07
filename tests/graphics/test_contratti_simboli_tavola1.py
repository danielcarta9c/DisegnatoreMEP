"""I contratti grafici di DRAW-005, parte B, scritti prima del codice.

La matrice PM fissa, per i simboli critici della tavola 1:

1. il filtro a Y e' una Y riconoscibile — ramo inclinato e gambo inferiore — con
   due porte in linea, e il gambo non sale sopra l'asse in nessuna rotazione ammessa;
2. un confine di rete uscente e uno entrante condividono il tipo grafico ma puntano
   entrambi nel verso locale dell'acqua: l'orientamento viene dal verso della porta,
   mai dall'identificativo o dal bordo del foglio;
3. `P`, `T`, `F` e qualunque glifo interno dichiarato leggibile restano dritti
   rispetto al foglio a 0/90/180/270 gradi, senza alterare corpo e porte;
4. il simbolo della pompa di calore lascia fra mandata e ritorno lo spazio
   funzionale agli accessori, senza sovrapposizioni;
5. l'accumulo combinato mostra un serpentino continuo da `cold_in` a `dhw_out`, e
   gli attacchi tecnici entrano nel volume del mantello; puffer e bollitore hanno
   corpi coerenti con i propri fluidi.

Le prove leggono la libreria pubblicata e il catalogo di prova: nessun identificativo
o coordinata della tavola 1.
"""

import math
import re
from functools import cache
from pathlib import Path
from xml.etree import ElementTree

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentDefinition, ComponentTrait
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import Symbol, SymbolRegistry
from disegnatore_mep.graphics.sheet import render_sheet
from disegnatore_mep.graphics.standard import A3_LANDSCAPE
from disegnatore_mep.graphics.symbol import (
    PortFace,
    SymbolManifest,
    functional_room_mm,
    rotate_point_mm,
)
from disegnatore_mep.layout.geometry import PlacedSymbol, Point, SheetGeometry
from disegnatore_mep.model.types import PortFlow

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"

HEATING = "heating_water"
COLD = "cold_water"
DHW = "domestic_hot_water"
TOLERANCE_MM = 1e-6
Pt = tuple[float, float]
Segment = tuple[Pt, Pt]


@cache
def library() -> SymbolRegistry:
    return SymbolRegistry.from_directory(SYMBOLS)


@cache
def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(CATALOG, symbols=library())


def _local(tag: str) -> str:
    return tag.rpartition("}")[2]


def _numbers(text: str) -> list[float]:
    return [float(item) for item in re.findall(r"-?\d+(?:\.\d+)?", text)]


def path_vertices(d: str) -> list[Pt]:
    """I vertici di un tracciato assoluto: M e L, e il punto d'arrivo di Q."""
    vertices: list[Pt] = []
    for command, arguments in re.findall(r"([MLQZ])([^MLQZ]*)", d):
        numbers = _numbers(arguments)
        if command in ("M", "L"):
            vertices.extend(zip(numbers[0::2], numbers[1::2], strict=False))
        elif command == "Q":
            vertices.append((numbers[2], numbers[3]))
    return vertices


def segments_of(element: ElementTree.Element) -> list[Segment]:
    """Tutti i tratti rettilinei del corpo: le linee e i lati dei tracciati."""
    found: list[Segment] = []
    for item in element.iter():
        tag, get = _local(item.tag), item.get
        if tag == "line":
            found.append(
                (
                    (float(get("x1", "0")), float(get("y1", "0"))),
                    (float(get("x2", "0")), float(get("y2", "0"))),
                )
            )
        elif tag == "path":
            vertices = path_vertices(get("d", ""))
            found.extend(zip(vertices, vertices[1:], strict=False))
    return found


def rects_of(element: ElementTree.Element) -> list[tuple[float, float, float, float]]:
    return [
        tuple(float(item.get(key, "0")) for key in ("x", "y", "width", "height"))  # type: ignore[misc]
        for item in element.iter()
        if _local(item.tag) == "rect"
    ]


def parsed(body: str) -> ElementTree.Element:
    return ElementTree.fromstring(f"<g>{body}</g>")


def close(first: Pt, second: Pt, tolerance: float = 1e-3) -> bool:
    return abs(first[0] - second[0]) <= tolerance and abs(first[1] - second[1]) <= tolerance


def definitions_with(function: str) -> list[ComponentDefinition]:
    return [item for item in catalog().all() if function in item.functions]


# ---------------------------------------------------------------------------
# B1 — il filtro a Y
# ---------------------------------------------------------------------------


def _strainer_symbols() -> list[Symbol]:
    ids = sorted({item.symbol_id for item in definitions_with("filtration")})
    assert ids, "nessun filtro in catalogo: la prova non direbbe nulla"
    return [library().get(symbol_id) for symbol_id in ids]


def _the_y(symbol: Symbol) -> tuple[Pt, Segment, Segment]:
    """L'asse delle porte, il ramo inclinato e il gambo che lo chiude."""
    manifest = symbol.manifest
    assert len(manifest.ports) == 2
    first, second = manifest.ports
    assert first.face is second.face.opposite
    assert abs(first.y_mm - second.y_mm) <= TOLERANCE_MM, "le due porte non sono in linea"
    axis_y = first.y_mm
    segments = segments_of(parsed(symbol.body))
    inclined = [
        item
        for item in segments
        if abs(item[1][0] - item[0][0]) > TOLERANCE_MM
        and abs(item[1][1] - item[0][1]) > TOLERANCE_MM
        and (
            (abs(item[0][1] - axis_y) <= TOLERANCE_MM and item[1][1] > axis_y + TOLERANCE_MM)
            or (abs(item[1][1] - axis_y) <= TOLERANCE_MM and item[0][1] > axis_y + TOLERANCE_MM)
        )
    ]
    assert len(inclined) == 1, f"{manifest.id}: il ramo inclinato dall'asse verso il basso non c'e', o ce n'e' piu' d'uno"
    branch = inclined[0]
    root, tip = (branch if abs(branch[0][1] - axis_y) <= TOLERANCE_MM else (branch[1], branch[0]))
    stems = [
        item
        for item in segments
        if item != branch
        and (close(item[0], tip) or close(item[1], tip))
        and min(item[0][1], item[1][1]) > axis_y + TOLERANCE_MM
    ]
    assert stems, f"{manifest.id}: al ramo inclinato manca il gambo inferiore"
    return root, (root, tip), stems[0]


@pytest.mark.parametrize("symbol", _strainer_symbols(), ids=lambda item: item.manifest.id)
def test_il_filtro_e_una_y_con_ramo_inclinato_e_gambo_sotto_l_asse(symbol: Symbol) -> None:
    root, (_, tip), stem = _the_y(symbol)
    # Il ramo parte dal centro dell'asse fra le due porte, non da un capo.
    assert abs(root[0] - symbol.manifest.width_mm / 2) <= TOLERANCE_MM
    # Ramo e gambo stanno dentro il riquadro, sotto l'asse.
    for point in (tip, *stem):
        assert 0 - TOLERANCE_MM <= point[0] <= symbol.manifest.width_mm + TOLERANCE_MM
        assert root[1] < point[1] <= symbol.manifest.height_mm + TOLERANCE_MM
    # Il segno resta in linea: la linea passante raggiunge tutte e due le porte.
    segments = segments_of(parsed(symbol.body))
    for port in symbol.manifest.ports:
        assert any(
            close(end, (port.x_mm, port.y_mm)) for item in segments for end in item
        ), port.id


@pytest.mark.parametrize("symbol", _strainer_symbols(), ids=lambda item: item.manifest.id)
def test_il_gambo_del_filtro_non_sale_mai_sopra_l_asse_in_nessuna_rotazione_ammessa(
    symbol: Symbol,
) -> None:
    """«Gambo inferiore in ogni rotazione ammessa»: la libreria ammette solo le
    rotazioni in cui il gambo non punta in su, e ne ammette una verticale,
    perche' il filtro deve potersi posare su una tubazione verticale."""
    manifest = symbol.manifest
    root, (_, tip), _ = _the_y(symbol)
    for degrees in manifest.allowed_rotations_deg:
        turned_root = rotate_point_mm(root[0], root[1], manifest.width_mm, manifest.height_mm, degrees)
        turned_tip = rotate_point_mm(tip[0], tip[1], manifest.width_mm, manifest.height_mm, degrees)
        assert turned_tip[1] >= turned_root[1] - TOLERANCE_MM, (
            f"{manifest.id}: a {degrees} gradi il gambo punta in su"
        )
    assert any(degrees in manifest.allowed_rotations_deg for degrees in (90, 270)), (
        "il filtro deve potersi posare su una tubazione verticale"
    )
    assert 0 in manifest.allowed_rotations_deg


# ---------------------------------------------------------------------------
# B2 — il confine di rete guarda nel verso dell'acqua
# ---------------------------------------------------------------------------


def _boundaries() -> tuple[ComponentDefinition, ComponentDefinition]:
    """Un confine uscente e uno entrante che condividono il simbolo."""
    found = definitions_with("boundary")
    by_symbol: dict[str, list[ComponentDefinition]] = {}
    for item in found:
        by_symbol.setdefault(item.symbol_id, []).append(item)
    for members in by_symbol.values():
        outgoing = [item for item in members if item.ports[0].flow is PortFlow.OUT]
        incoming = [item for item in members if item.ports[0].flow is PortFlow.IN]
        if outgoing and incoming:
            return outgoing[0], incoming[0]
    raise AssertionError("nessuna coppia di confini uscente/entrante sullo stesso simbolo")


def _glyph_paths(root: ElementTree.Element, component_id: str) -> list[ElementTree.Element]:
    group = next(
        item
        for item in root.iter()
        if _local(item.tag) == "g" and item.get("data-component-id") == component_id
    )
    return [item for item in group.iter() if item.get("class") == "flow-glyph"]


def _tip_and_base(path: ElementTree.Element) -> tuple[Pt, Pt]:
    vertices = path_vertices(path.get("d", ""))
    assert len(vertices) >= 3, path.get("d")
    tip = vertices[0]
    base = ((vertices[1][0] + vertices[2][0]) / 2, (vertices[1][1] + vertices[2][1]) / 2)
    return tip, base


def test_confine_uscente_ed_entrante_condividono_il_simbolo_che_dichiara_il_glifo_di_verso() -> None:
    outgoing, incoming = _boundaries()
    assert outgoing.symbol_id == incoming.symbol_id
    manifest = library().get(outgoing.symbol_id).manifest
    assert [glyph.port for glyph in manifest.flow_glyphs] == [outgoing.ports[0].id]


@pytest.mark.parametrize("degrees", (0, 90, 180, 270))
def test_la_freccia_del_confine_punta_nel_verso_locale_dell_acqua(degrees: int) -> None:
    """Uscente: l'acqua lascia il confine ed entra nel tubo, la punta guarda la
    porta. Entrante: l'acqua arriva dal tubo, la punta guarda dentro il
    simbolo. In ogni rotazione, e la freccia non sposta la porta."""
    outgoing, incoming = _boundaries()
    symbol = library().get(outgoing.symbol_id)
    turned = symbol.manifest.rotated(degrees)
    placed = [
        PlacedSymbol(
            component_id=name,
            symbol_id=symbol.manifest.id,
            rotation_deg=degrees,
            origin=Point(x_mm=x_mm, y_mm=100.0),
            width_mm=turned.width_mm,
            height_mm=turned.height_mm,
            port_flows={outgoing.ports[0].id: flow.value},
        )
        for name, x_mm, flow in (("uscente", 100.0, PortFlow.OUT), ("entrante", 140.0, PortFlow.IN))
    ]
    sheet = SheetGeometry(sheet_id="t1", title="prova", symbols=placed)
    root = ElementTree.fromstring(render_sheet(sheet, NOVE_C_A3, library()))
    port = turned.port(outgoing.ports[0].id)
    for item in placed:
        at = (item.origin.x_mm + port.x_mm, item.origin.y_mm + port.y_mm)
        paths = _glyph_paths(root, item.component_id)
        assert len(paths) == 1, item.component_id
        tip, base = _tip_and_base(paths[0])
        nearer = math.dist(tip, at) < math.dist(base, at)
        assert nearer == (item.component_id == "uscente"), (degrees, item.component_id)
        # La punta sta sull'asse della porta, dentro il riquadro.
        outward = port.face.outward_angle_deg
        along = (math.cos(math.radians(outward)), math.sin(math.radians(outward)))
        across = abs((tip[0] - at[0]) * along[1] - (tip[1] - at[1]) * along[0])
        assert across <= 1e-6, (degrees, tip, at)


def test_senza_un_verso_dichiarato_il_confine_si_disegna_uscente_e_non_muto() -> None:
    """Il foglio di riscontro e la legenda non conoscono il catalogo: la
    freccia esce comunque, nel verso in cui la libreria la pubblica."""
    outgoing, _ = _boundaries()
    symbol = library().get(outgoing.symbol_id)
    placed = PlacedSymbol(
        component_id="muto",
        symbol_id=symbol.manifest.id,
        rotation_deg=0,
        origin=Point(x_mm=100.0, y_mm=100.0),
        width_mm=symbol.manifest.width_mm,
        height_mm=symbol.manifest.height_mm,
    )
    root = ElementTree.fromstring(
        render_sheet(SheetGeometry(sheet_id="t1", title="prova", symbols=[placed]), NOVE_C_A3, library())
    )
    paths = _glyph_paths(root, "muto")
    assert len(paths) == 1
    port = symbol.manifest.port(outgoing.ports[0].id)
    tip, base = _tip_and_base(paths[0])
    at = (100.0 + port.x_mm, 100.0 + port.y_mm)
    assert math.dist(tip, at) < math.dist(base, at)


def test_la_posa_scrive_il_verso_di_ogni_porta_con_glifo_leggendolo_dal_catalogo() -> None:
    """Il verso viene dal `PortFlow` della definizione, mai dal nome del pezzo
    ne' da dove il pezzo finisce sul foglio."""
    from datetime import date

    from disegnatore_mep.layout.compose import compose_drawing
    from disegnatore_mep.model.project import (
        ComponentInstance,
        ConnectionModel,
        NetworkModel,
        PortRef,
        ProjectMetadata,
        ProjectModel,
    )

    outgoing, incoming = _boundaries()
    tank = next(
        item
        for item in catalog().all()
        if item.has_trait(ComponentTrait.HOLDS_ITS_OWN_VOLUME)
        and item.stored_medium == HEATING
        and {"cold_in", "dhw_out"} <= item.port_ids
    )
    project = ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-confini",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 7),
        ),
        networks=[
            NetworkModel(id="primo", name="primo", domain="hydronic", medium=HEATING),
            NetworkModel(id="secondo", name="secondo", domain="hydronic", medium=HEATING),
            NetworkModel(id="fredda", name="fredda", domain="hydronic", medium=COLD),
            NetworkModel(id="calda", name="calda", domain="hydronic", medium=DHW),
        ],
        components=[
            ComponentInstance(id="generatore", definition_id="heat-pump-air-water"),
            ComponentInstance(id="serbatoio", definition_id=tank.id),
            ComponentInstance(id="corpo", definition_id="radiator"),
            # I nomi sono scambiati apposta: chi si chiama «uscita» e' il confine
            # che riceve, e viceversa. Il verso lo dice il catalogo.
            ComponentInstance(id="uscita", definition_id=incoming.id),
            ComponentInstance(id="ingresso", definition_id=outgoing.id),
        ],
        connections=[
            ConnectionModel(id="p1", network_id="primo", endpoint_a=PortRef(component_id="generatore", port_id="water_supply"), endpoint_b=PortRef(component_id="serbatoio", port_id="primary_in")),
            ConnectionModel(id="p2", network_id="primo", endpoint_a=PortRef(component_id="serbatoio", port_id="primary_out"), endpoint_b=PortRef(component_id="generatore", port_id="water_return")),
            ConnectionModel(id="s1", network_id="secondo", endpoint_a=PortRef(component_id="serbatoio", port_id="secondary_out"), endpoint_b=PortRef(component_id="corpo", port_id="in")),
            ConnectionModel(id="s2", network_id="secondo", endpoint_a=PortRef(component_id="corpo", port_id="out"), endpoint_b=PortRef(component_id="serbatoio", port_id="secondary_in")),
            ConnectionModel(id="w1", network_id="fredda", endpoint_a=PortRef(component_id="ingresso", port_id="a"), endpoint_b=PortRef(component_id="serbatoio", port_id="cold_in")),
            ConnectionModel(id="w2", network_id="calda", endpoint_a=PortRef(component_id="serbatoio", port_id="dhw_out"), endpoint_b=PortRef(component_id="uscita", port_id="a")),
        ],
    )
    drawing = compose_drawing(project, catalog(), NOVE_C_A3)
    placed = {item.component_id: item for item in drawing.sheets[0].symbols}
    assert placed["ingresso"].port_flows == {"a": PortFlow.OUT.value}
    assert placed["uscita"].port_flows == {"a": PortFlow.IN.value}
    root = ElementTree.fromstring(render_sheet(drawing.sheets[0], NOVE_C_A3, library()))
    for name, expected_nearer in (("ingresso", True), ("uscita", False)):
        item = placed[name]
        turned = library().get(item.symbol_id).manifest.rotated(item.rotation_deg)
        port = turned.port("a")
        at = (item.origin.x_mm + port.x_mm, item.origin.y_mm + port.y_mm)
        tip, base = _tip_and_base(_glyph_paths(root, name)[0])
        assert (math.dist(tip, at) < math.dist(base, at)) == expected_nearer, name


# ---------------------------------------------------------------------------
# B3 — i glifi interni restano dritti rispetto al foglio
# ---------------------------------------------------------------------------


def _apply(transform: str, point: Pt) -> Pt:
    """Applica una lista di trasformazioni SVG (`translate`, `rotate`) come
    farebbe un renderer: da destra a sinistra sul punto."""
    operations = re.findall(r"(translate|rotate)\(([^)]*)\)", transform)
    x, y = point
    for name, arguments in reversed(operations):
        numbers = _numbers(arguments)
        if name == "translate":
            x, y = x + numbers[0], y + (numbers[1] if len(numbers) > 1 else 0.0)
        else:
            angle = math.radians(numbers[0])
            cx, cy = (numbers[1], numbers[2]) if len(numbers) == 3 else (0.0, 0.0)
            dx, dy = x - cx, y - cy
            cos, sin = round(math.cos(angle), 12), round(math.sin(angle), 12)
            x, y = dx * cos - dy * sin + cx, dx * sin + dy * cos + cy
    return (x, y)


def _points_of(element: ElementTree.Element) -> list[Pt]:
    points: list[Pt] = []
    for tag_points in segments_of(element):
        points.extend(tag_points)
    for item in element.iter():
        if _local(item.tag) == "circle":
            points.append((float(item.get("cx", "0")), float(item.get("cy", "0"))))
    return points


def _glyph_groups(root: ElementTree.Element) -> list[ElementTree.Element]:
    return [item for item in root.iter() if _local(item.tag) == "g" and item.get("data-glyph")]


def _with_upright_glyphs() -> list[Symbol]:
    found = [item for item in library().all() if item.manifest.upright_glyphs]
    assert found, "nessun simbolo dichiara un glifo leggibile: la prova non direbbe nulla"
    return found


def test_manometro_e_termometro_dichiarano_la_lettera_come_glifo_leggibile() -> None:
    for function in ("pressure_measurement", "temperature_measurement"):
        for definition in definitions_with(function):
            manifest = library().get(definition.symbol_id).manifest
            assert manifest.upright_glyphs, definition.symbol_id


@pytest.mark.parametrize("symbol", _with_upright_glyphs(), ids=lambda item: item.manifest.id)
def test_ogni_glifo_dichiarato_ha_il_proprio_gruppo_nel_corpo_e_viceversa(symbol: Symbol) -> None:
    declared = {glyph.id for glyph in symbol.manifest.upright_glyphs}
    drawn = {item.get("data-glyph") for item in _glyph_groups(parsed(symbol.body))}
    assert declared == drawn, symbol.manifest.id
    for glyph in symbol.manifest.upright_glyphs:
        assert 0 <= glyph.x_mm <= symbol.manifest.width_mm
        assert 0 <= glyph.y_mm <= symbol.manifest.height_mm


@pytest.mark.parametrize("symbol", _with_upright_glyphs(), ids=lambda item: item.manifest.id)
@pytest.mark.parametrize("degrees", (0, 90, 180, 270))
def test_il_glifo_resta_dritto_e_il_corpo_gira_con_le_porte(symbol: Symbol, degrees: int) -> None:
    """Il corpo ruota con le porte; il glifo si limita a seguire il proprio
    centro, senza girare: ogni suo punto finisce dove finirebbe traslando il
    punto originale di quanto si e' spostato il centro."""
    manifest = symbol.manifest
    if degrees not in manifest.allowed_rotations_deg:
        pytest.skip("rotazione non ammessa dal simbolo")
    turned = symbol.rotated(degrees)
    root = ElementTree.fromstring(f"<g>{turned.body}</g>")
    outer = turned.body_transform
    upright = parsed(symbol.body)
    before = {item.get("data-glyph"): _points_of(item) for item in _glyph_groups(upright)}
    for group in _glyph_groups(root):
        glyph = next(item for item in manifest.upright_glyphs if item.id == group.get("data-glyph"))
        centre_after = rotate_point_mm(glyph.x_mm, glyph.y_mm, manifest.width_mm, manifest.height_mm, degrees)
        shift = (centre_after[0] - glyph.x_mm, centre_after[1] - glyph.y_mm)
        inner = group.get("transform", "")
        for point, original in zip(_points_of(group), before[group.get("data-glyph")], strict=True):
            landed = _apply(outer, _apply(inner, point))
            expected = (original[0] + shift[0], original[1] + shift[1])
            assert close(landed, expected), (manifest.id, degrees, landed, expected)
    # Tutto cio' che non e' glifo gira come sempre: le porte lo provano.
    for port in manifest.ports:
        moved = turned.manifest.port(port.id)
        expected = rotate_point_mm(port.x_mm, port.y_mm, manifest.width_mm, manifest.height_mm, degrees)
        assert close((moved.x_mm, moved.y_mm), expected)


@pytest.mark.parametrize("degrees", (0, 90, 180, 270))
def test_un_glifo_futuro_dichiarato_leggibile_resta_dritto_come_gli_altri(degrees: int) -> None:
    """La regola e' generale: un flussostato con la sua F, dichiarato domani,
    si comporta come manometro e termometro oggi."""
    manifest = SymbolManifest.model_validate(
        {
            "id": "flussostato-di-prova",
            "version": "1.0.0",
            "name": "Flussostato di prova",
            "width_mm": 5.0,
            "height_mm": 10.0,
            "allowed_rotations_deg": [0, 90, 180, 270],
            "ports": [{"id": "a", "face": "bottom", "x_mm": 2.5, "y_mm": 10.0}],
            "keep_out": {"bottom_mm": 2.0},
            "upright_glyphs": [{"id": "lettera", "x_mm": 2.5, "y_mm": 3.0}],
            "source": "CONV-GRAFICA-001",
        }
    )
    body = (
        '<line x1="2.5" y1="10" x2="2.5" y2="5"/><circle cx="2.5" cy="3" r="2"/>'
        '<g data-glyph="lettera"><line x1="1.7" y1="1.8" x2="1.7" y2="4.2"/>'
        '<line x1="1.7" y1="1.8" x2="3.3" y2="1.8"/><line x1="1.7" y1="3" x2="3" y2="3"/></g>'
    )
    symbol = Symbol(manifest=manifest, body=body)
    turned = symbol.rotated(degrees)
    root = ElementTree.fromstring(f"<g>{turned.body}</g>")
    group = _glyph_groups(root)[0]
    centre_after = rotate_point_mm(2.5, 3.0, 5.0, 10.0, degrees)
    shift = (centre_after[0] - 2.5, centre_after[1] - 3.0)
    originals = _points_of(_glyph_groups(parsed(body))[0])
    for point, original in zip(_points_of(group), originals, strict=True):
        landed = _apply(turned.body_transform, _apply(group.get("transform", ""), point))
        assert close(landed, (original[0] + shift[0], original[1] + shift[1])), (degrees, landed)


def test_un_corpo_che_disegna_un_glifo_non_dichiarato_o_ne_tace_uno_e_rifiutato(tmp_path: Path) -> None:
    from disegnatore_mep.graphics.errors import SymbolError

    payload = {
        "id": "strumento",
        "version": "1.0.0",
        "name": "Strumento",
        "width_mm": 5.0,
        "height_mm": 10.0,
        "allowed_rotations_deg": [0, 90, 180, 270],
        "ports": [{"id": "a", "face": "bottom", "x_mm": 2.5, "y_mm": 10.0}],
        "keep_out": {"bottom_mm": 2.0},
        "upright_glyphs": [{"id": "lettera", "x_mm": 2.5, "y_mm": 3.0}],
        "source": "CONV-GRAFICA-001",
    }
    import json

    (tmp_path / "strumento.json").write_text(json.dumps(payload), encoding="utf-8")
    (tmp_path / "strumento.svg").write_text('<line x1="2.5" y1="10" x2="2.5" y2="5"/>', encoding="utf-8")
    with pytest.raises(SymbolError, match="glyph"):
        SymbolRegistry.from_directory(tmp_path)
    payload["upright_glyphs"] = []
    (tmp_path / "strumento.json").write_text(json.dumps(payload), encoding="utf-8")
    (tmp_path / "strumento.svg").write_text(
        '<line x1="2.5" y1="10" x2="2.5" y2="5"/><g data-glyph="lettera"><line x1="2" y1="2" x2="3" y2="3"/></g>',
        encoding="utf-8",
    )
    with pytest.raises(SymbolError, match="glyph"):
        SymbolRegistry.from_directory(tmp_path)


# ---------------------------------------------------------------------------
# B4 — la pompa di calore lascia spazio funzionale fra mandata e ritorno
# ---------------------------------------------------------------------------


def _machines_of_the_first_plant() -> list[ComponentDefinition]:
    """Le pompe di calore aria-acqua: le macchine di generazione con la
    filtrazione richiesta e nessun combustibile — quelle della tavola 1."""
    return [
        item
        for item in definitions_with("heat_generation")
        if item.has_trait(ComponentTrait.NEEDS_DEBRIS_PROTECTION)
        and "circulation" in item.carries_on_board
    ]


def test_lo_spazio_funzionale_si_misura_dal_catalogo_e_dalla_griglia() -> None:
    """La misura e' derivata: l'accessorio in linea piu' alto che puo' stare
    sul fluido di quelle porte, piu' la distanza minima di rispetto. Non e'
    una costante per tutti i simboli."""
    room = functional_room_mm(catalog(), HEATING, A3_LANDSCAPE)
    tallest = max(
        (
            catalog().resolve(item.id).symbol.manifest.height_mm
            for item in catalog().all()
            if catalog().resolve(item.id).is_inline
            and all(port.medium == HEATING for port in item.ports)
        ),
        default=0.0,
    )
    assert room == pytest.approx(tallest + A3_LANDSCAPE.min_clearance_mm)
    assert room > 5.0, "cinque millimetri erano l'altezza della valvola, e non bastavano"


@pytest.mark.parametrize("definition", _machines_of_the_first_plant(), ids=lambda item: item.id)
def test_mandata_e_ritorno_della_pompa_di_calore_lasciano_spazio_agli_accessori(
    definition: ComponentDefinition,
) -> None:
    manifest = library().get(definition.symbol_id).manifest
    media = {port.id: port.medium for port in definition.ports if not port.off_the_run}
    by_face: dict[PortFace, list[float]] = {}
    for port in manifest.ports:
        if port.id not in media:
            continue
        by_face.setdefault(port.face, []).append(
            port.x_mm if port.face in (PortFace.TOP, PortFace.BOTTOM) else port.y_mm
        )
    assert any(len(items) >= 2 for items in by_face.values()), "mandata e ritorno stanno sulla stessa faccia"
    for face, items in by_face.items():
        items.sort()
        for before, after in zip(items, items[1:], strict=False):
            room = functional_room_mm(catalog(), media[next(iter(media))], A3_LANDSCAPE)
            assert after - before >= room - TOLERANCE_MM, (definition.id, face.value, after - before, room)
    supply = manifest.port(next(port.id for port in definition.ports if port.flow is PortFlow.OUT))
    back = manifest.port(next(port.id for port in definition.ports if port.flow is PortFlow.IN))
    assert abs(back.y_mm - supply.y_mm) == pytest.approx(15.0), "la matrice PM chiede 15 mm per la PDC della tavola 1"


def test_cinque_millimetri_fra_due_porte_non_passano_la_misura() -> None:
    """La misura riconosce il difetto di DRAW-004: due attacchi a cinque
    millimetri portano due valvole che si toccano."""
    room = functional_room_mm(catalog(), HEATING, A3_LANDSCAPE)
    assert 5.0 < room


# ---------------------------------------------------------------------------
# B5 — il serpentino dell'accumulo combinato, e i tre accumuli distinti
# ---------------------------------------------------------------------------


def _reserves() -> list[ComponentDefinition]:
    return [
        item for item in catalog().all() if item.has_trait(ComponentTrait.HOLDS_ITS_OWN_VOLUME)
    ]


def _shell(body: ElementTree.Element) -> tuple[float, float, float, float]:
    rects = rects_of(body)
    assert rects, "la riserva non ha un mantello"
    x, y, w, h = max(rects, key=lambda item: item[2] * item[3])
    return (x, y, x + w, y + h)


def _inside(point: Pt, shell: tuple[float, float, float, float], slack: float = 1e-6) -> bool:
    return shell[0] - slack <= point[0] <= shell[2] + slack and shell[1] - slack <= point[1] <= shell[3] + slack


def _through_and_volume_ports(
    definition: ComponentDefinition,
) -> tuple[list[str], list[str]]:
    """Chi attraversa la riserva in un serpentino, e chi entra nel volume.

    Attraversa chi porta un fluido diverso da quello tenuto in serbo e non e'
    l'attacco da cui la riserva si riempie; entra nel volume tutto il resto."""
    through: list[str] = []
    volume: list[str] = []
    for port in definition.ports:
        if port.off_the_run:
            continue
        if port.medium != definition.stored_medium and port.id != definition.fills_from:
            through.append(port.id)
        else:
            volume.append(port.id)
    return through, volume


@pytest.mark.parametrize("definition", _reserves(), ids=lambda item: item.id)
def test_gli_attacchi_del_volume_entrano_nel_mantello(definition: ComponentDefinition) -> None:
    symbol = library().get(definition.symbol_id)
    body = parsed(symbol.body)
    shell = _shell(body)
    _, volume = _through_and_volume_ports(definition)
    assert volume, definition.id
    segments = segments_of(body)
    for port_id in volume:
        port = symbol.manifest.port(port_id)
        at = (port.x_mm, port.y_mm)
        stubs = [item for item in segments if close(item[0], at) or close(item[1], at)]
        assert stubs, (definition.id, port_id)
        inner = [item[1] if close(item[0], at) else item[0] for item in stubs]
        assert any(_inside(point, shell) for point in inner), (definition.id, port_id, inner)


@pytest.mark.parametrize("definition", _reserves(), ids=lambda item: item.id)
def test_chi_attraversa_la_riserva_lo_fa_in_un_serpentino_continuo(definition: ComponentDefinition) -> None:
    """Dal proprio ingresso alla propria uscita, un tracciato solo, che passa
    dentro il mantello e gira abbastanza da leggersi come un serpentino."""
    symbol = library().get(definition.symbol_id)
    body = parsed(symbol.body)
    shell = _shell(body)
    through, _ = _through_and_volume_ports(definition)
    coils = [item for item in body.iter() if item.get("class") == "coil"]
    if not through:
        assert not coils, f"{definition.id} non ha nulla che attraversi la riserva, ma disegna un serpentino"
        return
    assert coils, f"{definition.id}: {through} attraversano la riserva e il corpo non disegna il serpentino"
    served: set[str] = set()
    for coil in coils:
        start, end = coil.get("data-from"), coil.get("data-to")
        assert start in through and end in through, (definition.id, start, end)
        first = symbol.manifest.port(str(start))
        last = symbol.manifest.port(str(end))
        vertices = path_vertices(coil.get("d", ""))
        assert close(vertices[0], (first.x_mm, first.y_mm)), (definition.id, vertices[0])
        assert close(vertices[-1], (last.x_mm, last.y_mm)), (definition.id, vertices[-1])
        interior = vertices[1:-1]
        assert all(_inside(point, shell) for point in interior), (definition.id, interior)
        turns = sum(
            1
            for before, here, after in zip(vertices, vertices[1:], vertices[2:], strict=False)
            if (here[0] - before[0], here[1] - before[1]) != (after[0] - here[0], after[1] - here[1])
        )
        assert turns >= 6, (definition.id, turns)
        served.update({str(start), str(end)})
    assert served == set(through), (definition.id, served, through)


def test_l_accumulo_combinato_e_il_bollitore_hanno_serpentini_diversi_e_il_puffer_nessuno() -> None:
    combined = [
        item for item in _reserves() if item.stored_medium == HEATING and {COLD, DHW} <= {p.medium for p in item.ports}
    ]
    cylinders = [
        item for item in _reserves() if item.stored_medium == DHW and HEATING in {p.medium for p in item.ports if not p.off_the_run}
    ]
    puffers = [
        item for item in _reserves() if item.stored_medium == HEATING and {p.medium for p in item.ports if not p.off_the_run} == {HEATING}
    ]
    assert combined and cylinders and puffers
    for item in combined:
        through, _ = _through_and_volume_ports(item)
        assert set(through) == {"cold_in", "dhw_out"}
    for item in cylinders:
        through, volume = _through_and_volume_ports(item)
        assert {p for p in through} == {p.id for p in item.ports if p.medium == HEATING and not p.off_the_run}
        assert "cold_in" in volume and "dhw_out" in volume
    for item in puffers:
        through, _ = _through_and_volume_ports(item)
        assert not through
