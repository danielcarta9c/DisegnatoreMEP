"""L'ordine degli stacchi lungo il tronco: le prove di DRAW-009 §C.

Il PO, il 13 settembre 2026, chiudendo la domanda §7.1 del rapporto DRAW-008:

    «Preferirei che il bollitore non ruotasse, ne' lui stesso ne' i suoi
    ingressi. Gli ingressi si possono spostare, quello si', per far si' che le
    linee siano dritte. Pero' non serve operare sugli ingressi del bollitore: e'
    sufficiente mettere gli stacchi di mandata e ritorno dal tronco principale
    nel giusto ordine. Se avessi messo lo stacco della mandata rossa a destra
    rispetto allo stacco del ritorno blu avrei pagato molti piu'
    attraversamenti.»

Due cose, quindi, e sono tutt'e due qui:

- **l'ordine**: quando due tratte lasciano il tronco per raggiungere lo stesso
  pezzo, corrono **annidate** e non si incrociano mai. La prova positiva lo
  misura sulla geometria consegnata; la negativa costruisce l'ordine invertito e
  mostra che l'incrocio c'e' per forza, e che a valle non si toglie;
- **il bollitore non ruota**, e non ruotano i suoi attacchi: nessuna posa che il
  motore sappia generare — ne' la fase del tronco ne' il ciclo — ne cambia
  `rotation_deg` o `port_map`.
"""
# categoria: difende il motore — due tratte verso lo stesso pezzo corrono annidate (DRAW-009 §C); due prove difendevano il solutore, Improver e fase del tronco: elencate nel rapporto

from functools import cache
from pathlib import Path

import pytest

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import compose_drawing, inline_component_ids
from disegnatore_mep.layout.geometry import RoutedTrunk, SheetGeometry
from disegnatore_mep.layout.improve import Improver
from disegnatore_mep.layout.partition import partition_project
from disegnatore_mep.layout.place import place_sheet
from disegnatore_mep.layout.spine import carry_the_rest, lay_the_spine
from disegnatore_mep.layout.trunks import Trunk, build_trunks
from disegnatore_mep.model.project import ProjectModel
from disegnatore_mep.rules.apply import saturate
from disegnatore_mep.rules.registry import RuleRegistry

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
RULES = ROOT / "rules" / "hydronic"
PROVE = ROOT / "examples" / "prova"

TAVOLE = {
    "tavola-1": PROVE / "prova-1-due-pdc-accumulo-combinato.json",
    "tavola-2": PROVE / "prova-2-pdc-deviatrice-acs.json",
}
STEP_MM = 2.5


@cache
def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


@cache
def rules() -> RuleRegistry:
    registry = RuleRegistry.from_directory(RULES)
    registry.cross_check(catalog())
    return registry


@cache
def _completo(name: str) -> ProjectModel:
    done, _, _ = saturate(load_project(TAVOLE[name]), catalog(), rules())
    return done


@cache
def _tavola(name: str) -> SheetGeometry:
    return compose_drawing(_completo(name), catalog(), NOVE_C_A3).sheets[0]


def _nodi(route: RoutedTrunk) -> set[tuple[float, float]]:
    """I nodi di griglia percorsi, non i soli vertici."""
    touched: set[tuple[float, float]] = set()
    for segment in route.segments:
        for before, after in zip(segment, segment[1:], strict=False):
            steps = int(
                round(
                    (abs(after.x_mm - before.x_mm) + abs(after.y_mm - before.y_mm))
                    / STEP_MM
                )
            )
            for index in range(steps + 1):
                ratio = 0.0 if steps == 0 else index / steps
                touched.add(
                    (
                        round(before.x_mm + (after.x_mm - before.x_mm) * ratio, 3),
                        round(before.y_mm + (after.y_mm - before.y_mm) * ratio, 3),
                    )
                )
    return touched


def _coppie_verso_lo_stesso_pezzo(
    project: ProjectModel, sheet: SheetGeometry
) -> list[tuple[str, RoutedTrunk, RoutedTrunk]]:
    """Le coppie di tratte che lasciano il tronco per raggiungere lo stesso pezzo.

    Si leggono sulle tratte del foglio, non su un elenco: due tratte che toccano
    lo stesso pezzo da due pezzi diversi sono la coppia che il PO ha in mente —
    la mandata che ci arriva e il ritorno che ne riparte.
    """
    inline = inline_component_ids(project, catalog())
    trunks = {
        tuple(trunk.connection_ids): trunk
        for trunk in build_trunks(project, inline)
    }
    routes = {tuple(item.connection_ids): item for item in sheet.routes}
    per_pezzo: dict[str, list[tuple[Trunk, RoutedTrunk]]] = {}
    for key, trunk in trunks.items():
        route = routes.get(key)
        if route is None:
            continue
        for mine, other in (
            (trunk.start, trunk.end),
            (trunk.end, trunk.start),
        ):
            per_pezzo.setdefault(mine.component_id, []).append((trunk, route))
            del other
    found: list[tuple[str, RoutedTrunk, RoutedTrunk]] = []
    for component_id, items in sorted(per_pezzo.items()):
        if len(items) != 2:
            continue
        (one_trunk, one), (two_trunk, two) = items
        estremi = {
            ref.component_id
            for trunk in (one_trunk, two_trunk)
            for ref in (trunk.start, trunk.end)
        } - {component_id}
        if len(estremi) != 2:
            continue
        found.append((component_id, one, two))
    return found


@pytest.mark.parametrize("name", sorted(TAVOLE))
def test_due_tratte_verso_lo_stesso_pezzo_corrono_annidate(name: str) -> None:
    """La prova positiva: le due tratte **non si incrociano**.

    E' la forma misurabile di «corrono annidate». L'ordine degli stacchi lungo
    il tronco e' giusto quando le due tratte non condividono nessun nodo di
    griglia; invertito, l'incrocio c'e' per forza — lo mostra la prova negativa
    qui sotto.
    """
    project, sheet = _completo(name), _tavola(name)
    coppie = _coppie_verso_lo_stesso_pezzo(project, sheet)
    assert coppie, "nessuna coppia di tratte verso lo stesso pezzo su questa tavola"
    for component_id, one, two in coppie:
        condivisi = _nodi(one) & _nodi(two)
        # I nodi delle due porte del pezzo non contano: li' le tratte arrivano,
        # non si incrociano. Un incrocio e' un nodo lontano da tutt'e due.
        estremi = {
            (point.x_mm, point.y_mm)
            for route in (one, two)
            for segment in route.segments
            for point in (segment[0], segment[-1])
        }
        assert not (condivisi - estremi), (
            component_id,
            sorted(condivisi - estremi),
            one.connection_ids,
            two.connection_ids,
        )


def test_l_ordine_invertito_produce_un_incrocio_che_non_si_toglie() -> None:
    """La prova negativa, e non su una tavola: su due percorsi qualunque.

    Due tratte lasciano un tronco orizzontale e scendono verso lo stesso pezzo,
    che sta piu' in basso e a destra. Nell'ordine **giusto** lo stacco piu'
    lontano dal pezzo va all'attacco piu' basso e quello piu' vicino all'attacco
    piu' alto: le due corrono annidate e non si toccano. Invertito l'ordine si
    incrociano, e si incrociano **per costruzione** — e' il teorema di Jordan su
    una striscia, non un difetto dell'instradatore: ecco perche' l'incrocio non
    si puo' togliere a valle, e va evitato dove lo stacco si decide.
    """

    def passi(here: float, there: float) -> list[float]:
        step = 1.0 if there >= here else -1.0
        return [here + step * index for index in range(int(abs(there - here)) + 1)]

    def gomito(
        start: tuple[float, float], goal: tuple[float, float]
    ) -> set[tuple[float, float]]:
        """Le celle del percorso che scende dal tronco e poi va verso il pezzo."""
        cells = {(start[0], y) for y in passi(start[1], goal[1])}
        cells |= {(x, goal[1]) for x in passi(start[0], goal[0])}
        return cells

    lontano, vicino = (0.0, 0.0), (20.0, 0.0)
    alto, basso = (40.0, 20.0), (40.0, 30.0)

    giusto = gomito(lontano, basso) & gomito(vicino, alto)
    assert not giusto, sorted(giusto)

    invertito = gomito(lontano, alto) & gomito(vicino, basso)
    assert invertito, "l'ordine invertito deve incrociare, e per costruzione"


@pytest.mark.parametrize("name", sorted(TAVOLE))
def test_il_bollitore_non_ruota_e_non_ruotano_i_suoi_attacchi(name: str) -> None:
    """§C: nessuna posa candidata cambia la giacitura di un accumulo sanitario.

    Non si prova guardando la tavola consegnata — li' potrebbe essere un caso —
    ma **tutte** le candidate che il ciclo sa generare per quel pezzo: se
    nessuna lo gira, nessuna tavola puo' uscirne girata. Il pezzo si riconosce
    dal mestiere dichiarato dal catalogo, non dal nome.
    """
    project = _completo(name)
    inline = inline_component_ids(project, catalog())
    partition = partition_project(project, build_trunks(project, inline))[0]
    first = place_sheet(project, partition, catalog(), NOVE_C_A3, inline)
    spine = lay_the_spine(project, partition, catalog(), NOVE_C_A3, first)
    seeded = carry_the_rest(project, partition, catalog(), first, spine, NOVE_C_A3)
    improver = Improver(project, partition, catalog(), NOVE_C_A3, seeded, inline, spine)

    accumuli = [
        item.id
        for item in project.components
        if "dhw_storage" in catalog().get(item.definition_id).functions
    ]
    if not accumuli:
        pytest.skip("questa tavola non ha un accumulo sanitario a se'")
    for component_id in accumuli:
        if component_id not in improver.best:
            continue
        posa = improver.best[component_id]
        for refining in (False, True):
            improver.refining = refining
            for _, move in improver.candidates_by_kind(component_id):
                if component_id not in move:
                    continue
                assert move[component_id].rotation_deg == posa.rotation_deg, (
                    component_id,
                    move[component_id].rotation_deg,
                )
                assert move[component_id].port_map == posa.port_map, (
                    component_id,
                    move[component_id].port_map,
                )
        improver.refining = False


@pytest.mark.parametrize("name", sorted(TAVOLE))
def test_la_fase_del_tronco_non_gira_l_accumulo_sanitario(name: str) -> None:
    """La stessa cosa per la fase del tronco, che sceglie le pose per prima."""
    project = _completo(name)
    inline = inline_component_ids(project, catalog())
    partition = partition_project(project, build_trunks(project, inline))[0]
    first = place_sheet(project, partition, catalog(), NOVE_C_A3, inline)
    spine = lay_the_spine(project, partition, catalog(), NOVE_C_A3, first)
    prima = {item.component_id: item for item in first}
    accumuli = {
        item.id
        for item in project.components
        if "dhw_storage" in catalog().get(item.definition_id).functions
    }
    if not accumuli:
        pytest.skip("questa tavola non ha un accumulo sanitario a se'")
    for item in spine.symbols:
        if item.component_id not in accumuli:
            continue
        assert item.rotation_deg == prima[item.component_id].rotation_deg
        assert item.port_map == prima[item.component_id].port_map
