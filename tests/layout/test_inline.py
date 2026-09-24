# categoria: difende il motore
from datetime import date
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.errors import LayoutError
from disegnatore_mep.layout.geometry import (
    PlacedSymbol,
    Point,
    RoutedTrunk,
    box_of,
    intrudes_into,
    moves_of,
    run_intrudes_on,
)
from disegnatore_mep.layout.grid import GridSpace
from disegnatore_mep.layout.inline import place_inline_accessories
from disegnatore_mep.layout.partition import partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.route import route_sheet
from disegnatore_mep.layout.trunks import Trunk, build_trunks
from disegnatore_mep.model.project import (
    ComponentInstance,
    ConnectionModel,
    NetworkModel,
    PortRef,
    ProjectMetadata,
    ProjectModel,
    SubsystemModel,
)
from disegnatore_mep.model.types import PlantRegime

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"


def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def grid() -> GridSpace:
    return GridSpace(origin=NOVE_C_A3.drawing_rect_mm, standard=NOVE_C_A3.standard)


def routed_case() -> tuple[ProjectModel, list[Trunk], list[RoutedTrunk], list[PlacedSymbol]]:
    project = load_project(PROJECT)
    registry = catalog()
    inline = frozenset(
        item.id
        for item in project.components
        if registry.resolve(item.definition_id).is_inline
    )
    trunks = build_trunks(project, inline)
    part = partition_project(project, trunks)[0]
    placed = place_sheet(project, part, registry, NOVE_C_A3, inline)
    routes = route_sheet(project, list(part.trunks), placed, registry, grid())
    return project, list(part.trunks), routes, placed


def with_accessories() -> list[tuple[Trunk, list[list[Point]], list[PlacedSymbol]]]:
    project, trunks, routes, _ = routed_case()
    registry, space = catalog(), grid()
    out = []
    for trunk, routed in zip(trunks, routes, strict=True):
        if not trunk.inline_component_ids:
            continue
        accessories, broken = place_inline_accessories(
            project, trunk, routed, registry, space
        )
        out.append((trunk, broken.segments, accessories))
    return out


def test_every_inline_accessory_of_the_case_is_placed() -> None:
    placed = {
        item.component_id for _, _, items in with_accessories() for item in items
    }
    assert placed == {"strainer", "shutoff", "pump-secondary"}


def test_an_accessory_sits_on_its_own_run() -> None:
    for trunk, broken, accessories in with_accessories():
        for accessory in accessories:
            centre = Point(
                x_mm=accessory.origin.x_mm + accessory.width_mm / 2,
                y_mm=accessory.origin.y_mm + accessory.height_mm / 2,
            )
            ends = [point for segment in broken for point in (segment[0], segment[-1])]
            assert any(
                abs(point.x_mm - centre.x_mm) + abs(point.y_mm - centre.y_mm)
                <= accessory.width_mm / 2 + accessory.height_mm / 2 + 1e-9
                for point in ends
            ), trunk.connection_ids


def test_the_line_is_broken_not_covered() -> None:
    """D-027: nessuna linea continua passa sotto un componente in linea."""
    for _, broken, accessories in with_accessories():
        assert len(broken) == len(accessories) + 1
        for accessory in accessories:
            for segment in broken:
                for before, after in zip(segment, segment[1:], strict=False):
                    crosses_x = (
                        accessory.origin.x_mm < min(before.x_mm, after.x_mm)
                        and max(before.x_mm, after.x_mm) < accessory.right_mm
                    )
                    crosses_y = (
                        accessory.origin.y_mm < min(before.y_mm, after.y_mm)
                        and max(before.y_mm, after.y_mm) < accessory.bottom_mm
                    )
                    assert not (crosses_x and crosses_y)


def test_the_break_is_as_long_as_the_declared_gap() -> None:
    registry = catalog()
    project, trunks, routes, _ = routed_case()
    definitions = {item.id: item.definition_id for item in project.components}
    for trunk, routed in zip(trunks, routes, strict=True):
        if len(trunk.inline_component_ids) != 1:
            continue
        gap = registry.resolve(
            definitions[trunk.inline_component_ids[0]]
        ).symbol.manifest.inline_gap_mm
        assert gap is not None
        _, broken = place_inline_accessories(project, trunk, routed, registry, grid())
        head, tail = broken.segments[0][-1], broken.segments[1][0]
        measured = abs(tail.x_mm - head.x_mm) + abs(tail.y_mm - head.y_mm)
        assert measured == pytest.approx(gap)


def test_the_rotation_follows_the_run_and_is_allowed() -> None:
    """La giacitura la da' il tratto, e la rotazione e' una che il simbolo
    ammette. Non una coppia fissa di angoli: un filtro a Y non si specchia —
    ammette 0 e 270 — e su un tratto verticale la sola giacitura possibile e'
    270. Cio' che conta e' che il simbolo stia **lungo il proprio tubo**."""
    registry = catalog()
    project, _, _, _ = routed_case()
    definitions = {item.id: item.definition_id for item in project.components}
    for _, broken, accessories in with_accessories():
        for index, accessory in enumerate(accessories):
            manifest = registry.resolve(
                definitions[accessory.component_id]
            ).symbol.manifest
            assert accessory.rotation_deg in manifest.allowed_rotations_deg
            head, tail = broken[index][-1], broken[index + 1][0]
            horizontal = abs(tail.y_mm - head.y_mm) <= 1e-9
            assert accessory.rotation_deg in ((0, 180) if horizontal else (90, 270)), (
                accessory.component_id,
                accessory.rotation_deg,
                horizontal,
            )


def test_an_accessory_centre_lands_on_a_grid_node() -> None:
    space = grid()
    for _, _, accessories in with_accessories():
        for accessory in accessories:
            space.to_cell(
                accessory.origin.x_mm + accessory.width_mm / 2,
                accessory.origin.y_mm + accessory.height_mm / 2,
            )


def test_a_run_too_short_for_its_accessories_fails_with_a_diagnostic() -> None:
    project, trunks, routes, _ = routed_case()
    trunk = next(item for item in trunks if item.inline_component_ids)
    routed = RoutedTrunk(
        network_id=trunk.network_id,
        connection_ids=list(trunk.connection_ids),
        segments=[[Point(x_mm=10.0, y_mm=20.0), Point(x_mm=12.0, y_mm=20.0)]],
    )
    with pytest.raises(LayoutError, match="never shrunk|need"):
        place_inline_accessories(project, trunk, routed, catalog(), grid())


def test_a_run_without_accessories_is_returned_untouched() -> None:
    project, trunks, routes, _ = routed_case()
    for trunk, routed in zip(trunks, routes, strict=True):
        if trunk.inline_component_ids:
            continue
        accessories, unchanged = place_inline_accessories(
            project, trunk, routed, catalog(), grid()
        )
        assert accessories == []
        assert unchanged is routed


def hugging_run(accessory: PlacedSymbol) -> RoutedTrunk:
    """Una tratta altrui che taglia in verticale il riquadro dell'accessorio."""
    centre_x = accessory.origin.x_mm + accessory.width_mm / 2
    return RoutedTrunk(
        network_id="other",
        connection_ids=["altrui"],
        segments=[
            [
                Point(x_mm=centre_x, y_mm=accessory.origin.y_mm - 20.0),
                Point(x_mm=centre_x, y_mm=accessory.bottom_mm + 20.0),
            ]
        ],
    )


def test_an_accessory_steps_aside_from_a_run_that_is_not_its_own() -> None:
    """B5 — un accessorio e' un simbolo, e una tratta altrui gli sta lontano.

    Senza questo vincolo l'accessorio si posava dove la tratta gia' disegnata di
    un'altra rete gli passava addosso — 0 mm — e sulla tavola completa erano tre
    rilievi bloccanti: chi posava non vedeva le tratte, e chi instradava dopo
    non vedeva l'accessorio.
    """
    project, trunks, routes, _ = routed_case()
    registry, space = catalog(), grid()
    trunk, routed = next(
        (item, line)
        for item, line in zip(trunks, routes, strict=True)
        if len(item.inline_component_ids) == 1
    )
    alone, _ = place_inline_accessories(project, trunk, routed, registry, space)
    intruder = hugging_run(alone[0])
    minimum = NOVE_C_A3.standard.min_clearance_mm
    assert run_intrudes_on(box_of(alone[0]), [intruder], minimum)

    aside, _ = place_inline_accessories(
        project, trunk, routed, registry, space, None, [intruder]
    )
    assert aside[0].origin != alone[0].origin
    assert not run_intrudes_on(box_of(aside[0]), [intruder], minimum)


def test_a_run_with_nowhere_clear_to_sit_its_accessory_says_so(
) -> None:
    """Se nessuna stazione rispetta lo stacco si solleva, non si posa male."""
    project, trunks, routes, _ = routed_case()
    registry, space = catalog(), grid()
    trunk, routed = next(
        (item, line)
        for item, line in zip(trunks, routes, strict=True)
        if len(item.inline_component_ids) == 1
    )
    # Una tratta altrui appoggiata per il lungo su tutta la spezzata: nessuna
    # stazione puo' starne lontana.
    along = RoutedTrunk(
        network_id="other",
        connection_ids=["altrui"],
        segments=[list(routed.segments[0])],
    )
    with pytest.raises(LayoutError, match="clear of the other symbols and runs"):
        place_inline_accessories(
            project, trunk, routed, registry, space, None, [along]
        )


def test_the_accessory_keeps_its_tag() -> None:
    tags = {
        item.component_id: item.tag
        for _, _, items in with_accessories()
        for item in items
    }
    assert tags["strainer"] == "FIL-01"
    assert tags["pump-secondary"] == "CIR-02"


def test_an_accessory_moves_on_when_its_own_run_bends_back_into_it() -> None:
    """D-027 sulla propria tratta: il posto dove la linea gli rientra nel
    riquadro si scarta subito, e l'accessorio avanza di un passo.

    E' la geometria vera della mandata sanitaria dell'impianto 1 composto dalla
    via ordinaria: la linea sale dall'uscita ACS, corre a sinistra per 62,5 mm,
    scende e rientra. Il miscelatore termostatico e' alto dieci millimetri, e
    posato a due passi dalla curva si ritrovava la discesa lungo il fianco. Fino
    al 23 settembre 2026 il posto si scopriva sbagliato solo a tratta finita —
    «still passes under mixing-valve-thermostatic after breaking for it» — e la
    tavola cadeva; diciannove prove rosse della suite si fermavano li'.

    **Da D-175 il miscelatore non sta piu' su quella tratta**: ha il terzo
    attacco dell'acqua fredda, non e' piu' un organo in linea e la mandata
    sanitaria finisce su di lui. La geometria della prova resta la stessa, e la
    porta adesso il **defangatore** del ritorno comune, l'altro organo in linea
    alto dieci millimetri dell'impianto 1: la proprieta' sorvegliata e' la
    stessa — nessun accessorio posato su una tratta piegata le sta addosso.
    """
    from disegnatore_mep.io.canonical import canonical_json
    from disegnatore_mep.rules.apply import saturate
    from disegnatore_mep.rules.registry import RuleRegistry

    registry = catalog()
    regole = RuleRegistry.from_directory(ROOT / "rules" / "hydronic")
    regole.cross_check(registry)
    completo, _, _ = saturate(
        load_project(ROOT / "examples" / "prova" / "prova-1-due-pdc-accumulo-combinato.json"),
        registry,
        regole,
    )
    project = ProjectModel.model_validate_json(canonical_json(completo))
    inline = frozenset(
        item.id
        for item in project.components
        if registry.resolve(item.definition_id).is_inline
    )
    trunk = next(
        item for item in build_trunks(project, inline) if "p4-a-4" in item.connection_ids
    )
    assert "dirt-separator-collettore-ritorno-a" in trunk.inline_component_ids
    alto = registry.resolve("dirt-separator").symbol.manifest
    assert max(alto.width_mm, alto.height_mm) == 10.0
    routed = RoutedTrunk(
        network_id=trunk.network_id,
        connection_ids=list(trunk.connection_ids),
        segments=[
            [
                Point(x_mm=260.0, y_mm=151.0),
                Point(x_mm=260.0, y_mm=138.5),
                Point(x_mm=197.5, y_mm=138.5),
                Point(x_mm=197.5, y_mm=163.5),
                Point(x_mm=192.5, y_mm=163.5),
            ]
        ],
    )
    accessories, broken = place_inline_accessories(
        project, trunk, routed, registry, grid()
    )
    assert len(accessories) == len(trunk.inline_component_ids)
    for accessory in accessories:
        for part in broken.segments:
            assert not any(
                intrudes_into(box_of(accessory), before, after)
                for before, after in moves_of(part)
            ), accessory.component_id


def _una_macchina_e_il_suo_organo(organo: str) -> tuple[ProjectModel, Trunk]:
    """Una pompa di calore, un volano, e un organo in linea sulla mandata fra i
    due: la tratta parte dalla macchina e l'organo le e' collegato con `a`."""
    pezzi = [("nord", "heat-pump-air-water"), ("volano", "buffer-four-port"), ("organo", organo)]
    project = ProjectModel(
        metadata=ProjectMetadata(
            project_id="verso",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date=date(2026, 9, 23),
        ),
        plant_regime=PlantRegime.UP_TO_35_KW,
        networks=[NetworkModel(id="rete", name="rete", domain="hydronic", medium="heating_water")],
        components=[ComponentInstance(id=item, definition_id=definition) for item, definition in pezzi],
        connections=[
            ConnectionModel(
                id="m1",
                network_id="rete",
                endpoint_a=PortRef(component_id="nord", port_id="water_supply"),
                endpoint_b=PortRef(component_id="organo", port_id="a"),
            ),
            ConnectionModel(
                id="m2",
                network_id="rete",
                endpoint_a=PortRef(component_id="organo", port_id="b"),
                endpoint_b=PortRef(component_id="volano", port_id="primary_in"),
            ),
        ],
        subsystems=[
            SubsystemModel(
                id="tutto",
                name="tutto",
                component_ids=[item for item, _ in pezzi],
                network_ids=["rete"],
            )
        ],
    )
    (trunk,) = build_trunks(project, frozenset({"organo"}))
    assert trunk.start.component_id == "nord" and trunk.inline_component_ids == ("organo",)
    return project, trunk


def _porta(accessory: PlacedSymbol, port_id: str) -> Point:
    manifesto = (
        SymbolRegistry.from_directory(SYMBOLS)
        .get(accessory.symbol_id)
        .manifest.rotated(accessory.rotation_deg, accessory.specchiato)
    )
    porta = manifesto.port(port_id)
    return Point(
        x_mm=accessory.origin.x_mm + porta.x_mm, y_mm=accessory.origin.y_mm + porta.y_mm
    )


@pytest.mark.parametrize(
    ("verso", "dal_capo", "al_capo"),
    [
        ("su", (200.0, 151.0), (200.0, 101.0)),
        ("giu", (200.0, 101.0), (200.0, 151.0)),
        ("destra", (150.0, 101.0), (200.0, 101.0)),
        ("sinistra", (200.0, 101.0), (150.0, 101.0)),
    ],
)
def test_una_valvola_di_ritegno_si_disegna_nel_verso_del_flusso(
    verso: str, dal_capo: tuple[float, float], al_capo: tuple[float, float]
) -> None:
    """**La freccia della valvola di ritegno segue il fluido**, in tutti e
    quattro i versi. Il suo simbolo ha la freccia disegnata dall'ingresso
    all'uscita; fino al 23 settembre 2026 il motore sceglieva la rotazione dalla
    sola giacitura del tratto, e su una colonna in salita la freccia puntava in
    giu' — l'ha visto un agente in camera pulita, e stava gia' sulla tavola a
    mano dell'impianto 4. L'ingresso sta dalla parte da cui la tratta arriva."""
    project, trunk = _una_macchina_e_il_suo_organo("valve-check")
    routed = RoutedTrunk(
        network_id="rete",
        medium="heating_water",
        connection_ids=list(trunk.connection_ids),
        segments=[[Point(x_mm=dal_capo[0], y_mm=dal_capo[1]), Point(x_mm=al_capo[0], y_mm=al_capo[1])]],
    )
    (valvola,), _ = place_inline_accessories(project, trunk, routed, catalog(), grid())
    ingresso, uscita = _porta(valvola, "a"), _porta(valvola, "b")
    partenza = Point(x_mm=dal_capo[0], y_mm=dal_capo[1])

    def lontano(punto: Point) -> float:
        return abs(punto.x_mm - partenza.x_mm) + abs(punto.y_mm - partenza.y_mm)

    assert lontano(ingresso) < lontano(uscita), (verso, valvola)


def test_una_valvola_simmetrica_non_si_specchia() -> None:
    """E chi non ha un verso resta com'era: una valvola d'intercettazione sulla
    stessa tratta verso sinistra non si specchia e non si gira. Le sue porte
    sono tutt'e due `bidirectional`, e la tavola non cambia di un tratto."""
    project, trunk = _una_macchina_e_il_suo_organo("valve-isolation")
    routed = RoutedTrunk(
        network_id="rete",
        medium="heating_water",
        connection_ids=list(trunk.connection_ids),
        segments=[[Point(x_mm=200.0, y_mm=101.0), Point(x_mm=150.0, y_mm=101.0)]],
    )
    (valvola,), _ = place_inline_accessories(project, trunk, routed, catalog(), grid())
    assert (valvola.rotation_deg, valvola.specchiato) == (0, False)
