"""Chi isola si disegna sull'attacco di cio' che isola (D-120, I-018).

La regola del PM, data «da senior al disegnatore»: «le valvole di
intercettazione che vengono montate per manutenere le macchine devono essere
disegnate molto piu' vicine agli attacchi, una regola di vicinanza fissa e
piuttosto piccola, esempio 2 mm».

Chi isola e cosa si manutiene **lo dice il catalogo**, mai il nome del pezzo: la
funzione `isolation` (o quella bloccabile aperta) da una parte, la proprieta'
`maintainable` dall'altra — la stessa che la regola dell'intercettazione legge
per chiedere quella valvola.

Il minimo raggiungibile e' **un passo oltre la cella riservata davanti
all'attacco** (D-113): quella corsia e' l'unica uscita di quell'attacco e non e'
gioco. Ne discende il fianco della valvola a cinque millimetri dal punto
d'attacco, contro i dodici e mezzo dello stacco ordinario.
"""

from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.catalog.schema import ComponentTrait
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import compose_on_ordinary_frame, inline_component_ids
from disegnatore_mep.layout.geometry import DrawingGeometry, PlacedSymbol, box_of
from disegnatore_mep.layout.grid import GridSpace
from disegnatore_mep.layout.inline import (
    END_CLEARANCE_MM,
    ISOLATING_FUNCTIONS,
    SNUG_CLEARANCE_MM,
    settle_sheet,
)
from disegnatore_mep.layout.partition import partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.route import port_aprons
from disegnatore_mep.layout.trunks import build_trunks
from disegnatore_mep.model.project import PortRef, ProjectModel
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.proposal import RuleGap, RuleProposal
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"
PROVA_2 = ROOT / "examples" / "prova" / "prova-2-pdc-deviatrice-acs.json"
RULES = ROOT / "rules" / "hydronic"
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"

TOLERANCE_MM = 1e-6


def _catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def _completato(path: Path) -> tuple[ProjectModel, list[RuleProposal], list[RuleGap]]:
    """Il modello completato dalle regole: e' quello che porta gli organi."""
    registry = RuleRegistry.from_directory(RULES)
    registry.cross_check(_catalog())
    return saturate(load_project(path), _catalog(), registry)


def test_lo_stacco_stretto_e_un_passo_e_non_zero() -> None:
    """Un passo oltre la soglia dell'attacco, che resta libera (D-113)."""
    assert NOVE_C_A3.standard.grid_mm == SNUG_CLEARANCE_MM
    assert SNUG_CLEARANCE_MM < END_CLEARANCE_MM


def test_chi_isola_lo_dice_il_catalogo() -> None:
    """Le due funzioni dell'intercettazione, e nessun nome di componente."""
    registry = _catalog()
    isolators = {
        item.id
        for item in registry.all()
        if ISOLATING_FUNCTIONS & set(item.functions)
    }
    assert isolators
    # Chi isola lo si riconosce dal mestiere dichiarato, e chi si manutiene da
    # una proprieta': due elenchi che il catalogo tiene, e nessuno scritto qui.
    serviced = {
        item.id
        for item in registry.all()
        if item.has_trait(ComponentTrait.MAINTAINABLE)
    }
    assert serviced
    assert not (isolators & serviced), (
        "chi isola non si isola a sua volta, o le valvole vorrebbero valvole"
    )


def test_la_valvola_si_siede_sull_attacco_della_macchina_che_isola() -> None:
    """La misura di D-120: il fianco della valvola contro il punto d'attacco.

    Si guarda **la prima valvola di ogni tratta che parte da un pezzo
    manutenibile**, che e' il primo dei tre casi della regola. Prima della
    regola quel fianco stava a 12,5 mm — due passi di stacco ordinario piu' il
    passo che separa due accessori — e nessuna disposizione lo avvicinava,
    perche' la costante non distingueva chi isola da un accessorio qualunque.
    """
    project = load_project(PROJECT)
    registry = _catalog()
    inline = inline_component_ids(project, registry)
    trunks = build_trunks(project, inline)
    partition = partition_project(project, trunks)[0]
    grid = GridSpace(origin=NOVE_C_A3.drawing_rect_mm, standard=NOVE_C_A3.standard)
    placed = place_sheet(project, partition, registry, NOVE_C_A3, inline)
    settled = settle_sheet(
        project, list(partition.trunks), placed, registry, grid, tolerant=True
    )

    by_id: dict[str, PlacedSymbol] = {
        item.component_id: item for item in settled.symbols
    }
    definitions = {item.id: item.definition_id for item in project.components}

    def maintainable(component_id: str) -> bool:
        return registry.resolve(
            definitions[component_id]
        ).definition.has_trait(ComponentTrait.MAINTAINABLE)

    def isolates(component_id: str) -> bool:
        return bool(
            ISOLATING_FUNCTIONS
            & set(registry.resolve(definitions[component_id]).definition.functions)
        )

    measured: list[float] = []
    for trunk in partition.trunks:
        members = list(trunk.inline_component_ids)
        if not members:
            continue
        first = members[0]
        host = by_id.get(trunk.start.component_id)
        if host is None or first not in by_id:
            continue
        if not (isolates(first) and maintainable(trunk.start.component_id)):
            continue
        manifest = registry.resolve(
            definitions[trunk.start.component_id]
        ).symbol.manifest.rotated(host.rotation_deg)
        port = manifest.port(trunk.start.port_id)
        x_mm = host.origin.x_mm + port.x_mm
        y_mm = host.origin.y_mm + port.y_mm
        left, top, right, bottom = box_of(by_id[first])
        gap_x = max(left - x_mm, x_mm - right, 0.0)
        gap_y = max(top - y_mm, y_mm - bottom, 0.0)
        measured.append((gap_x**2 + gap_y**2) ** 0.5)

    assert measured, "il caso non contiene una valvola che isola un pezzo manutenibile"
    # Un passo oltre la cella riservata, e non oltre lo stacco ordinario che la
    # regola sostituisce.
    assert max(measured) <= END_CLEARANCE_MM + TOLERANCE_MM
    assert min(measured) >= SNUG_CLEARANCE_MM - TOLERANCE_MM


def test_nessun_accessorio_si_siede_sulla_soglia_di_un_attacco() -> None:
    """La vicinanza non compra la soglia (D-113), che resta l'uscita dell'attacco.

    E' il vincolo che tiene la regola dentro il proprio limite: avvicinare fino
    a coprire la cella davanti all'attacco murerebbe quell'attacco, ed e' un
    fallimento che nessun formato di carta risolve.
    """
    project = load_project(PROJECT)
    registry = _catalog()
    inline = inline_component_ids(project, registry)
    trunks = build_trunks(project, inline)
    partition = partition_project(project, trunks)[0]
    grid = GridSpace(origin=NOVE_C_A3.drawing_rect_mm, standard=NOVE_C_A3.standard)
    placed = place_sheet(project, partition, registry, NOVE_C_A3, inline)
    settled = settle_sheet(
        project, list(partition.trunks), placed, registry, grid, tolerant=True
    )
    reserved = set(
        port_aprons(project, list(partition.trunks), placed, registry, grid).values()
    )
    for accessory in settled.accessories:
        low = grid.to_cell(accessory.origin.x_mm, accessory.origin.y_mm)
        high = grid.to_cell(accessory.right_mm, accessory.bottom_mm)
        occupied = {
            (col, row)
            for col in range(low[0], high[0] + 1)
            for row in range(low[1], high[1] + 1)
        }
        assert not occupied & reserved


# ---------------------------------------------------------------------------
# DRAW-006-R1, blocco E — la coppia in fila, e la tavola 2 al completo
# ---------------------------------------------------------------------------


def _misure_d120(
    project: ProjectModel, drawn: DrawingGeometry, registry: ComponentRegistry
) -> dict[str, float]:
    """Per ogni organo di servizio, la distanza dal pezzo che serve.

    I tre casi della regola, come il posatore li applica: contro il capo di
    partenza della propria tratta, contro quello di arrivo, e la **coppia** in
    fila con un apparecchio manutenibile che sta anch'esso sulla tubazione. Si
    riporta il caso piu' vicino, che e' quello a cui il posatore lo ha stretto;
    chi non serve nessuno non compare.
    """
    inline = inline_component_ids(project, registry)
    partition = partition_project(project, build_trunks(project, inline))[0]
    by_id = {item.component_id: item for item in drawn.sheets[0].symbols}
    definitions = {item.id: item.definition_id for item in project.components}

    def isolates(component_id: str) -> bool:
        return bool(
            ISOLATING_FUNCTIONS
            & set(registry.resolve(definitions[component_id]).definition.functions)
        )

    def serviced(component_id: str) -> bool:
        return registry.resolve(definitions[component_id]).definition.has_trait(
            ComponentTrait.MAINTAINABLE
        )

    def gap(first: tuple[float, float, float, float], second: tuple[float, float, float, float]) -> float:
        dx = max(first[0] - second[2], second[0] - first[2], 0.0)
        dy = max(first[1] - second[3], second[1] - first[3], 0.0)
        return (dx**2 + dy**2) ** 0.5

    def port_box(ref: PortRef) -> tuple[float, float, float, float] | None:
        host = by_id.get(ref.component_id)
        if host is None:
            return None
        port = (
            registry.resolve(definitions[ref.component_id])
            .symbol.manifest.rotated(host.rotation_deg)
            .port(ref.port_id)
        )
        x_mm = host.origin.x_mm + port.x_mm
        y_mm = host.origin.y_mm + port.y_mm
        return (x_mm, y_mm, x_mm, y_mm)

    measured: dict[str, float] = {}
    for trunk in partition.trunks:
        members = list(trunk.inline_component_ids)
        for position, component_id in enumerate(members):
            if not isolates(component_id) or component_id not in by_id:
                continue
            mine = box_of(by_id[component_id])
            candidates: list[float] = []
            for at, ref in ((0, trunk.start), (len(members) - 1, trunk.end)):
                if position != at or not serviced(ref.component_id):
                    continue
                box = port_box(ref)
                if box is not None:
                    candidates.append(gap(mine, box))
            for neighbour in (position - 1, position + 1):
                if not 0 <= neighbour < len(members):
                    continue
                other = members[neighbour]
                if serviced(other) and other in by_id:
                    candidates.append(gap(mine, box_of(by_id[other])))
            if candidates:
                measured[component_id] = min(candidates)
    return measured


def _fuori_regola(measured: dict[str, float]) -> dict[str, float]:
    return {
        name: value
        for name, value in measured.items()
        if not SNUG_CLEARANCE_MM - TOLERANCE_MM <= value <= END_CLEARANCE_MM + TOLERANCE_MM
    }


def test_l_organo_in_coppia_con_un_accessorio_gli_sta_stretto() -> None:
    """Il terzo caso di D-120: due pezzi in fila, non ai capi della tratta.

    E' il caso che il PM ha trovato fuori regola sulla tavola 2: un organo e il
    proprio accessorio, tutti e due in mezzo alla tubazione, con una curva fra
    loro. La proprieta' non e' una soglia della fixture — e' la relazione
    funzionale «questo organo isola quel pezzo», e vale ovunque quella
    relazione esista.
    """
    registry = _catalog()
    project, _, _ = _completato(PROVA_2)
    frame, drawn = compose_on_ordinary_frame(project, registry)
    assert frame is not None
    measured = _misure_d120(project, drawn, registry)
    coppie = {
        name: value
        for name, value in measured.items()
        if name.count("-") and value > END_CLEARANCE_MM + TOLERANCE_MM
    }
    assert coppie == {}, (
        f"organi di servizio lontani dal pezzo che servono: {coppie}"
    )


def test_ogni_organo_della_tavola_2_sta_sul_pezzo_che_serve() -> None:
    """Criterio 7 di DRAW-006-R1: nessun organo fuori dai 2,5÷5 mm.

    Si contano **tutti** quelli che la regola governa, nei suoi tre casi: la
    prova non fissa quanti siano, perche' quel numero e' della fixture e non
    della regola — pretende che nessuno resti fuori.
    """
    registry = _catalog()
    project, _, _ = _completato(PROVA_2)
    _, drawn = compose_on_ordinary_frame(project, registry)
    measured = _misure_d120(project, drawn, registry)
    assert measured, "la tavola 2 non porta nessun organo governato da D-120"
    assert _fuori_regola(measured) == {}
