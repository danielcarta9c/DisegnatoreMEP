"""La posa governata dal costo delle tubazioni (DRAW-002, I-021, D-078, D-080).

> **Dal 2 ottobre 2026 (I-180) il solutore non c'e' piu'**, e con lui le prove che lo
> difendevano. Restano qui le due prove che la via senza piano e' deterministica e non legge gli identificativi. Il resto di questa intestazione e' la storia del
> file, e si legge come tale.


Il PO: «bisogna spostare le macchine perche' spostare le macchine costa zero;
invece incroci, curve e lunghezze costano». Il PM ne ha fatto una specifica:
un solo confronto lessicografico della tavola intera, nessuna distensione che
compri riempimento pagando in tubo, candidati ricavati dalla topologia.

Queste prove sono **generali**: gli impianti sono costruiti qui dentro, con il
catalogo di prova, e nessuna coordinata o identificativo dell'impianto 1 entra
nel motore ne' nelle attese. Sono scritte prima del codice applicativo, come il
pacchetto chiede.
"""
# categoria: difende il motore — la via senza piano e' deterministica e non legge gli identificativi

from functools import cache
from pathlib import Path

from disegnatore_mep.catalog.registry import ComponentRegistry
from disegnatore_mep.graphics.frame import NOVE_C_A3
from disegnatore_mep.graphics.registry import SymbolRegistry
from disegnatore_mep.io.project_json import load_project
from disegnatore_mep.layout.compose import compose_drawing
from disegnatore_mep.layout.geometry import (
    DrawingGeometry,
    drawing_fingerprint,
)
from disegnatore_mep.model.project import (
    ComponentInstance,
    ConnectionModel,
    NetworkModel,
    PortRef,
    ProjectMetadata,
    ProjectModel,
    SubsystemModel,
)

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "examples" / "layout" / "catalog"
SYMBOLS = ROOT / "assets" / "symbols"
FIXTURE = ROOT / "examples" / "layout" / "heat-pump-dhw-buffer-two-zones.json"



@cache
def catalog() -> ComponentRegistry:
    return ComponentRegistry.from_directory(
        CATALOG, symbols=SymbolRegistry.from_directory(SYMBOLS)
    )


def _plant(
    components: list[tuple[str, str]],
    connections: list[tuple[str, str, str, str, str]],
    subsystems: list[tuple[str, list[str]]],
) -> ProjectModel:
    """Un impianto minimo: (id, definizione), (id, da, porta, a, porta), gruppi."""
    return ProjectModel(
        metadata=ProjectMetadata(
            project_id="prova-costo-peso",
            client="prova",
            project_name="prova",
            commission_code="PROVA",
            revision="00",
            issue_date="2026-09-03",
        ),
        subsystems=[
            SubsystemModel(id=name, name=name, component_ids=members, network_ids=["rete"])
            for name, members in subsystems
        ],
        networks=[
            NetworkModel(id="rete", name="Rete", domain="hydronic", medium="heating_water")
        ],
        components=[
            ComponentInstance(id=item, definition_id=definition)
            for item, definition in components
        ],
        connections=[
            ConnectionModel(
                id=item,
                network_id="rete",
                endpoint_a=PortRef(component_id=source, port_id=source_port),
                endpoint_b=PortRef(component_id=target, port_id=target_port),
            )
            for item, source, source_port, target, target_port in connections
        ],
    )








# ---------------------------------------------------------------------------
# Gli impianti di prova, costruiti qui: nessun identificativo dell'impianto 1
# ---------------------------------------------------------------------------


def generatore_accumulo_terminale() -> ProjectModel:
    """Una macchina, un accumulo e un terminale in fila, con una valvola."""
    return _plant(
        components=[
            ("macchina", "heat-pump-air-water"),
            ("valvola", "valve-isolation"),
            ("serbatoio", "buffer-two-port"),
            ("terminale", "radiator"),
        ],
        connections=[
            ("c1", "macchina", "water_supply", "valvola", "a"),
            ("c2", "valvola", "b", "serbatoio", "a"),
            ("c3", "serbatoio", "b", "terminale", "in"),
            ("c4", "terminale", "out", "macchina", "water_return"),
        ],
        subsystems=[
            ("generazione", ["macchina", "valvola"]),
            ("accumulo", ["serbatoio"]),
            ("utenza", ["terminale"]),
        ],
    )








# ---------------------------------------------------------------------------
# 1. Un solo confronto esplicito, lessicografico
# ---------------------------------------------------------------------------










# ---------------------------------------------------------------------------
# 2. Una posa compatta batte una posa equidistante
# ---------------------------------------------------------------------------






# ---------------------------------------------------------------------------
# 3. I candidati vengono dalla topologia
# ---------------------------------------------------------------------------








# ---------------------------------------------------------------------------
# 4. Determinismo, e indipendenza dagli identificativi
# ---------------------------------------------------------------------------


def _renamed(project: ProjectModel) -> ProjectModel:
    """Lo stesso impianto con ogni identificativo cambiato, e l'ordine alfabetico
    rovesciato: se il motore decidesse qualcosa in base al nome, si vedrebbe."""
    names = (
        [item.id for item in project.components]
        + [item.id for item in project.connections]
        + [item.id for item in project.subsystems]
        + [item.id for item in project.networks]
    )
    ordered = sorted(names)
    mapping = {name: f"z{len(ordered) - index:03d}-{name}" for index, name in enumerate(ordered)}

    def rename(document: object) -> object:
        if isinstance(document, dict):
            out: dict[str, object] = {}
            for key, value in document.items():
                if key in _ID_KEYS and isinstance(value, str):
                    out[key] = mapping.get(value, value)
                elif key in _ID_LIST_KEYS and isinstance(value, list):
                    out[key] = [mapping.get(item, item) for item in value]
                else:
                    out[key] = rename(value)
            return out
        if isinstance(document, list):
            return [rename(item) for item in document]
        return document

    return ProjectModel.model_validate(rename(project.model_dump(mode="json")))


_ID_KEYS = frozenset({"id", "component_id", "network_id", "subsystem_id"})
_ID_LIST_KEYS = frozenset({"component_ids", "network_ids", "subsystem_ids"})


def _shape(drawing: DrawingGeometry) -> tuple[object, ...]:
    """La geometria senza i nomi: cosa c'e' e dove, non come si chiama."""
    sheet = drawing.sheets[0]
    symbols = sorted(
        (item.symbol_id, item.rotation_deg, item.origin.x_mm, item.origin.y_mm)
        for item in sheet.symbols
    )
    routes = sorted(
        (
            route.medium,
            tuple(tuple((point.x_mm, point.y_mm) for point in segment) for segment in route.segments),
        )
        for route in sheet.routes
    )
    return (tuple(symbols), tuple(routes))


def test_due_ingressi_equivalenti_con_identificativi_diversi_danno_la_stessa_geometria() -> None:
    """Il nome di un pezzo non decide dove sta (D-093)."""
    project = load_project(FIXTURE)
    twin = _renamed(project)
    assert {item.id for item in twin.components}.isdisjoint(
        {item.id for item in project.components}
    )
    assert _shape(compose_drawing(project, catalog(), NOVE_C_A3)) == _shape(
        compose_drawing(twin, catalog(), NOVE_C_A3)
    )


def test_due_generazioni_consecutive_danno_lo_stesso_fingerprint() -> None:
    project = generatore_accumulo_terminale()
    once = drawing_fingerprint(compose_drawing(project, catalog(), NOVE_C_A3))
    twice = drawing_fingerprint(compose_drawing(project, catalog(), NOVE_C_A3))
    assert once == twice


